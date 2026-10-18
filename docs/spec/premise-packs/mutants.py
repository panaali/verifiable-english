"""Seeded bugs of the pk-1s statement stub (build checklist 13): each plants one bug in `SpecStubs_pk1.lean`,
type-checks the stub from `lean/` with `lake env lean`, records the first error, and restores the file. Every mutant
must fail (at least one error); the unmutated stub must have none. Writes `mutants.json` next to this script.

Run from the repository root, with `lake` on PATH or in ~/.elan/bin:
`uv run python docs/spec/premise-packs/mutants.py [ID ...]` (with ids, only those mutants are rerun and the others'
saved results kept).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
STUB = HERE / "SpecStubs_pk1.lean"
REL = STUB.relative_to(ROOT).as_posix()
OUT = HERE / "mutants.json"

# Each mutant: one or more (old, new) replacements; every `old` occurs exactly once in the stub.
MUTANTS = [
    {"id": "M1", "mutation": "packOrder puts rights before soft",
     "edits": [('["soft", "rights", "weighing", "attitudes"', '["rights", "soft", "weighing", "attitudes"')]},
    {"id": "M2", "mutation": "firstRepeat forgets the keys it has seen",
     "edits": [("else firstRepeat (n :: seen) rest", "else firstRepeat seen rest")]},
    {"id": "M3", "mutation": "assembly skips the check against the environment",
     "edits": [("named.find? (fun (_, n) => declaredIn E n)", "named.find? (fun (_, _) => false)")]},
    {"id": "M4", "mutation": "packFault drops the legacy text",
     "edits": [("if legacyIds.contains (qs.map (·.id)) then", "if false then")]},
    {"id": "M5", "mutation": "the vocabulary limit is off by one",
     "edits": [("used + (names qs).length > 256", "used + (names qs).length ≥ 256")]},
    {"id": "M6", "mutation": "a repeated pack id is not refused",
     "edits": [("ps.countP (·.id == i) > 1", "ps.countP (·.id == i) > 2")]},
    {"id": "M7", "mutation": "extendEnv lets the base shadow a generated predicate",
     "edits": [("predicates := fun n => match ds.lookup n with | some ss => some ss | none => E.predicates n",
                "predicates := fun n => match E.predicates n with | some ss => some ss | none => ds.lookup n")]},
    {"id": "M8", "mutation": "xWithout keeps only the dropped labels",
     "edits": [("(fun a => !drop.contains a.1)", "(fun a => drop.contains a.1)")]},
    {"id": "M9", "mutation": "furtherEntries writes the soft pack again as a further entry",
     "edits": [('  (qs.filter (fun p => p.id != "soft" && p.id != "rights")).map packEntry\n',
                '  (qs.filter (fun p => p.id != "rights")).map packEntry\n')]},
    {"id": "M10", "mutation": "packPremises reads the first pack whatever its id",
     "edits": [("((qs.find? (·.id == i)).map (·.labelled)).getD []", "((qs.head?).map (·.labelled)).getD []")]},
    {"id": "M11", "finding": "F1", "mutation": "legacy_labels_nodup assumes WellFormedSoft (correlate R) again",
     "edits": [("(hs : VE.Rights.WellFormedRights R = true) (hw",
                "(hs : VE.SoftNorms.WellFormedSoft (VE.Rights.correlate R) = true) (hw")]},
    {"id": "M12", "finding": "F2a", "mutation": "legacyIds placed in Layered.lean, above packFault's file",
     "edits": [("``X_soft_first, ``legacyIds, ``labelledJson,", "``X_soft_first, ``labelledJson,"),
               ("[``softPack, ``rightsPack, ``legacyKinds,", "[``softPack, ``rightsPack, ``legacyIds, ``legacyKinds,")]},
    {"id": "M13", "finding": "F2a", "mutation": "transfers_X placed in Packs.lean (the draft's import cycle)",
     "edits": [("[``VE.Readings.transfers_append, ``VE.Readings.transfers_X]", "[``VE.Readings.transfers_append]"),
               ("``xWithout_nil, ``xWithout_sub, ``KindRow, ``dispatch]",
                "``xWithout_nil, ``xWithout_sub, ``KindRow, ``dispatch, ``VE.Readings.transfers_X]")]},
    {"id": "M14", "finding": "F2a", "mutation": "softPack placed in Packs.lean, below softLabelledU's file",
     "edits": [("[``softPack, ``rightsPack,", "[``rightsPack,"),
               ("``xWithout_nil, ``xWithout_sub, ``KindRow, ``dispatch]",
                "``xWithout_nil, ``xWithout_sub, ``KindRow, ``dispatch, ``softPack]")]},
    {"id": "M15", "finding": "F2a", "mutation": "Packs.lean imports Layered.lean, which imports it",
     "edits": [("some [`VE.NormDefaults.Explain, `VE.Rights.Wire]", "some [`VE.NormDefaults.Layered]")]},
    {"id": "M16", "finding": "F2a", "mutation": "a stub declaration with no file in planFiles",
     "edits": [("``xWithout, ``coherenceLabels,", "``xWithout,")]},
    {"id": "M17", "finding": "F2b", "mutation": "elaborateArrays writes the further packs' entries in pk-1",
     "edits": [('labelledJson l a none)).toArray)]\n\n/-- 2.7: the keys',
                'labelledJson l a none)).toArray)] ++\n'
                '  (qs.filter (fun p => p.id != "soft" && p.id != "rights")).map packEntry\n\n/-- 2.7: the keys')]},
]

ERROR = re.compile(r"^(?:\.\./)?" + re.escape(REL) + r":(\d+):\d+: error: (.*?)(?=^\S+:\d+:\d+: |\Z)", re.M | re.S)


def lake() -> str:
    found = shutil.which("lake") or str(Path.home() / ".elan/bin/lake")
    if not Path(found).exists():
        sys.exit("lake not found on PATH or in ~/.elan/bin")
    return found


def check(text: str) -> tuple[int, int | None, str | None]:
    """The stub's error count, and the line and message of its first error, with `text` as its source."""
    STUB.write_text(text)
    run = subprocess.run([lake(), "env", "lean", f"../{REL}"], cwd=ROOT / "lean", capture_output=True, text=True,
                         env={**os.environ, "PATH": f"{Path.home() / '.elan/bin'}:{os.environ.get('PATH', '')}"})
    found = [(int(m.group(1)), " ".join(m.group(2).split())) for m in ERROR.finditer(run.stdout + run.stderr)]
    if run.returncode != 0 and not found:
        sys.exit(f"lake env lean failed without a stub error:\n{run.stdout}{run.stderr}")
    return len(found), (found[0][0] if found else None), (found[0][1][:240] if found else None)


def main(ids: list[str]) -> int:
    original = STUB.read_text()
    saved = {r["id"]: r for r in json.loads(OUT.read_text())} if ids and OUT.exists() else {}
    results = []
    try:
        errors, _, _ = check(original)
        if errors:
            sys.exit(f"the unmutated stub has {errors} errors")
        for m in MUTANTS:
            if ids and m["id"] not in ids:
                results.append(saved[m["id"]])
                continue
            text = original
            for old, new in m["edits"]:
                if text.count(old) != 1:
                    sys.exit(f"{m['id']}: the text to mutate occurs {text.count(old)} times: {old!r}")
                text = text.replace(old, new)
            errors, line, message = check(text)
            src = text.splitlines()[line - 1].strip() if line else None
            results.append({"id": m["id"], "language": "Lean", "file": REL, **({"finding": m["finding"]} if "finding" in m else {}),
                            "mutation": m["mutation"], "failed": errors > 0, "errors": errors,
                            "test": f"SpecStubs_pk1.lean:{line}" if line else None, "first_failing": src,
                            "message": message})
    finally:
        STUB.write_text(original)
    OUT.write_text("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in results) + "\n]\n")
    survivors = [r["id"] for r in results if not r["failed"]]
    print(f"{len(results) - len(survivors)} of {len(results)} mutants fail" + (f"; survivors: {survivors}" if survivors else ""))
    return 1 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
