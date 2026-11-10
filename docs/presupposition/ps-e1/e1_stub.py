"""PS-E1 per-item frame and denotation table: computed by Lean from PS-1's stub and written into the prereg file."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e1_items  # noqa: E402

PREREG = e1_items.ROOT / "docs/research/presupposition-E1-prereg.md"
LEAN = e1_items.ROOT / "lean"
BEGIN, END = "<!-- stub-table:begin -->\n```json\n", "```\n<!-- stub-table:end -->"
PRELUDE = """import VE.Presupposition.Examples
namespace PsE1
open VE.Presupposition VE.Presupposition.Examples

def wa (p : String) : VE.Formula := .unary p (.const "w")
def dr (p c : String) : VE.Formula := .binary p (.var 0) (.const c)
def va (p : String) : VE.Formula := .unary p (.var 0)

def shape : Frame → String
  | .hole => "·"
  | .notF f => s!"not ({shape f})"
  | .andL f _ => s!"({shape f}) and …"
  | .andR _ f => s!"… and ({shape f})"
  | .orL f _ => s!"({shape f}) or …"
  | .orR _ f => s!"… or ({shape f})"
  | .impL f _ => s!"if ({shape f}) then …"
  | .impR _ f => s!"if … then ({shape f})"
  | .allF s f => s!"every {s}: {shape f}"
  | .exF s f => s!"some {s}: {shape f}"

def clsName : PositionClass → String
  | .top => "top" | .negated => "negated" | .antecedent => "antecedent" | .consequent => "consequent"
  | .disjunct => "disjunct" | .ruleAct => "rule_act" | .ruleGuard => "rule_guard"

def row (id : String) (f : Frame) (r : Reading) (M : VE.FiniteModel String) : String :=
  let b (x : Bool) := if x then "true" else "false"
  let same := f.shallowB && ev M (inPlaceAt f r) == ev M (conditionedAt f r)
  "{\\"id\\":\\"" ++ id ++ "\\",\\"frame\\":\\"" ++ shape f ++ "\\",\\"cls\\":\\"" ++ clsName f.cls ++ "\\",\\"shallow\\":" ++
    b f.shallowB ++ ",\\"goal\\":" ++ b (ev M (f.goal r.pre)) ++ ",\\"close\\":" ++ b (ev M (f.close r.pre)) ++
    ",\\"asserted\\":" ++ b (ev M (assertedAt f r)) ++ ",\\"conditioned\\":" ++ b (ev M (conditionedAt f r)) ++
    ",\\"in_place\\":" ++ b (ev M (inPlaceAt f r)) ++ ",\\"base\\":" ++ b (ev M (f.plug r.strong)) ++
    ",\\"be_one_class\\":" ++ b same ++ "}"
"""
LEAN_CELL = {"top": ".top", "negated": ".negated", "antecedent": ".antecedent", "consequent": ".consequent"}


def guards(i):
    """The stub's #guards of one item; a failing guard stops the generator (spec 6 item 5, R-D4)."""
    out = []
    if i["cell"] in LEAN_CELL and i["family"] != "control":
        out.append(f"#guard f.cls == {LEAN_CELL[i['cell']]}")
    if i["cell"] in e1_items.E_CELLS:
        out += ["#guard f.shallowB", "#guard ev M (inPlaceAt f r) == ev M (conditionedAt f r)"]
    if i["family"] in ("target", "suspension"):
        out.append("#guard !ev M (f.goal r.pre)")
    elif i["family"] == "control":
        out.append("#guard ev M (f.goal r.pre)")
    else:
        out += ["#guard ev M (f.goal r.pre)", "#guard !ev M (f.close r.pre)"]
    return out


def lean_source(items):
    parts = [PRELUDE]
    for n, i in enumerate(items):
        lean = i["lean"]
        parts.append(f'namespace I{n}\ndef r : Reading := {lean["reading"]}\ndef f : Frame := {lean["frame"]}\n'
                     f'def M : VE.FiniteModel String := {lean["model"]}\n' + "\n".join(guards(i)) +
                     f'\n#eval IO.println (row "{i["id"]}" f r M)\nend I{n}\n')
    return "\n".join(parts) + "\nend PsE1\n"


def run_lean(source, name="PsE1Stub.lean"):
    """Elaborate one generated file against the built library; the file stays outside lean/."""
    lake = shutil.which("lake") or os.path.expanduser("~/.elan/bin/lake")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        path.write_text(source)
        done = subprocess.run([lake, "env", "lean", str(path)], cwd=LEAN, capture_output=True, text=True, timeout=1800)
    if done.returncode:
        raise RuntimeError(f"lean refused the generated file: {done.stdout[-2000:]}{done.stderr[-500:]}")
    return done.stdout


def compute(items):
    rows = [json.loads(line) for line in run_lean(lean_source(items)).splitlines() if line.startswith("{")]
    cells = {i["id"]: i["cell"] for i in items}
    for r in rows:
        r["cell"] = cells[r["id"]]
        if r["cell"] == "rule_act":  # a rule's act has no asserted carrier and no in-place one (1.8)
            r["asserted"] = r["in_place"] = None
    return rows


def render(rows):
    return BEGIN + "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n]\n" + END


def saved_table(text=None):
    text = PREREG.read_text() if text is None else text
    return json.loads(text.split(BEGIN)[1].split(END)[0])


def write():
    text = PREREG.read_text()
    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: render(compute(e1_items.load())), text, flags=re.S)
    PREREG.write_text(new)


if __name__ == "__main__":
    if sys.argv[1:] == ["--write"]:
        write()
    elif sys.argv[1:] == ["--check"]:
        raise SystemExit(0 if compute(e1_items.load()) == saved_table() else "stub table is stale")
    else:
        raise SystemExit("usage: e1_stub.py --write|--check")
