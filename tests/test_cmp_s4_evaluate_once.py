"""cmp-s4 review F8: the composed path computes each value once, read from the compiled definitions.

The task asks that every value be evaluated once; the loop recheck found the base environment decoded twice and
`contentOk` run twice. Lean is the oracle, not the source text: the check below elaborates under `tmp_path`, counts
each constant in the elaborated bodies of the composed path's definitions (and their auxiliary definitions, such as
`match_1`), and prints the counts. It runs code while it elaborates (`run_cmd`), which the tree may not do
(`tools/lean_dump_cache.py` `EVALUATES`), so it lives here and runs with `lake env lean`, as the review's PROBE did.
"""
import shutil
import subprocess

import pytest

from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

PATH = ["chainEnvironment", "chainBaseWith", "chainBase", "resolveWith", "resolveDocument", "chainDDoc", "chainChecks",
        "caseManifest", "admitChain", "admitComposed"]

# (label, definition or "path" for the sum over PATH, constant): its expected count
EXPECTED = {
    # cmp-s4c: step 1's chain decoder, read once on the path (`admitChain`) and once by `chainBase` (off it)
    ("path", "VE.Norms.Wire.decodeNormsEnvironment"): 1,
    ("chainEnvironment", "VE.Norms.Wire.decodeNormsEnvironment"): 1,
    ("path", "VE.Discourse.chainEnvironment"): 2,
    ("chainBase", "VE.Discourse.chainEnvironment"): 1,
    ("admitChain", "VE.Discourse.chainEnvironment"): 1,
    ("admitChain", "VE.Discourse.chainBaseWith"): 1,
    ("chainBaseWith", "VE.Norms.Wire.canonicalEnvironmentJson"): 1,
    ("path", "VE.Discourse.contentOk"): 1,
    ("resolveWith", "VE.Discourse.contentOk"): 1,
    ("chainChecks", "VE.Discourse.resolveWith"): 1,
    ("admitChain", "VE.Discourse.resolveWith"): 0,
    ("admitChain", "VE.Discourse.chainBase"): 0,
    ("admitChain", "VE.Discourse.chainChecks"): 1,
    ("admitChain", "VE.Discourse.tablesOf"): 1,
    ("caseManifest", "VE.Discourse.chainBase"): 1,
    ("caseManifest", "VE.Discourse.chainChecks"): 1,
}

CHECK = """import VE.Discourse.Compose
open Lean Elab Command

def constCount (n : Lean.Name) : Expr → Nat
  | .const m _ => if m == n then 1 else 0
  | .app f a => constCount n f + constCount n a
  | .lam _ t b _ | .forallE _ t b _ => constCount n t + constCount n b
  | .letE _ t v b _ => constCount n t + constCount n v + constCount n b
  | .mdata _ e | .proj _ _ e => constCount n e
  | _ => 0

run_cmd do
  let env ← getEnv
  let path : List Lean.Name := [{path}]
  let defs (d : Lean.Name) : List Lean.Name :=
    env.constants.fold (fun acc m _ => if d.isPrefixOf m && d != m then m :: acc else acc) [d]
  let count (ds : List Lean.Name) (n : Lean.Name) : Nat :=
    ds.foldl (fun k d => k + ((env.find? d).bind (·.value?) |>.map (constCount n) |>.getD 0)) 0
  for (label, ds, n) in [{rows}] do
    logInfo m!"count {{label}} {{n}} {{count ds n}}"
"""


def check_source() -> str:
    def name(d: str) -> str:
        return f"`VE.Discourse.{d}"
    path = ", ".join(name(d) for d in PATH)
    rows = ", ".join(
        f'("{label}", {"path.flatMap defs" if label == "path" else f"defs {name(label)}"}, `{constant})'
        for label, constant in EXPECTED)
    return CHECK.format(path=path, rows=rows)


def counts(output: str) -> dict:
    """The `count <label> <constant> <n>` lines Lean's `logInfo` prints (bare, or after `info: `)."""
    found = {}
    for line in output.splitlines():
        line = line.partition("info: ")[2] or line
        if line.startswith("count "):
            _, label, constant, value = line.split()
            assert (label, constant) not in found, line
            found[(label, constant)] = int(value)
    return found


@pytest.fixture(scope="module")
def lake():
    found = shutil.which("lake")
    if found is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    return found


def test_every_definition_the_check_names_is_counted():
    assert {label for label, _ in EXPECTED} - {"path"} <= set(PATH)
    source = check_source()
    assert source.startswith("import VE.Discourse.Compose\n") and "run_cmd do" in source
    assert all(f"`{constant})" in source for _, constant in EXPECTED)


def test_counts_read_only_lean_count_lines():
    assert counts("count path VE.A 2\nx.lean:1:0: info: count chainBase VE.B 0\nnoise count path VE.C 3\n") == {
        ("path", "VE.A"): 2, ("chainBase", "VE.B"): 0}


def test_the_composed_path_computes_each_value_once(lake, tmp_path):
    source = tmp_path / "EvaluateOnce.lean"
    source.write_text(check_source())
    run = subprocess.run([lake, "env", "lean", str(source)], cwd=LEAN, capture_output=True, text=True,
                         timeout=HANG_TIMEOUT)
    assert run.returncode == 0, run.stdout + run.stderr
    assert counts(run.stdout + run.stderr) == EXPECTED
