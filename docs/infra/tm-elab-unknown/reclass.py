"""Reclassify the UNKNOWN ids of the df-5 and et-4b records under tools/trust_mutants.py's `invalid` (this tree).

For each id: write the record's mutant (before -> after on its line, the line found in this tree's file by the
occurrence of `before` nearest the record's line), elaborate it with `lake env lean`, keep the errors inside the
mutated declaration (the record's lines, shifted the same), and ask `invalid` for the verdict.
Usage (from the repo, elan on PATH):
    uv run python -I docs/infra/tm-elab-unknown/reclass.py . <record.json> [<record.json> ...]
"""
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo / "tools"))
import trust_mutants  # noqa: E402

LOC = re.compile(r"^(\S+?\.lean):(\d+):(\d+): error(?:\([^)]*\))?: ", re.M)
work = Path(tempfile.mkdtemp(prefix="tm-elab-unknown-"))


def one(record: str, m: dict) -> str:
    text = (repo / "lean" / m["file"]).read_text()
    lines = text.split("\n")
    near = sorted((abs(i + 1 - m["line"]), i) for i, ln in enumerate(lines) if m["before"] in ln)
    assert near, m["id"]
    i = near[0][1]
    shift = i + 1 - m["line"]
    assert lines[i].count(m["before"]) == 1, m["id"]
    column = lines[i].index(m["before"])
    starts = [0, *(k + 1 for k, ch in enumerate(text) if ch == "\n")]
    at = starts[i] + column
    mutated = text[:at] + m["after"] + text[at + len(m["before"]):]
    path = work / f"{Path(record).stem}-{m['id']}.lean"
    path.write_text(mutated)
    out = subprocess.run(["lake", "env", "lean", str(path)], cwd=repo / "lean", capture_output=True, text=True,
                         timeout=3000).stdout
    marks = list(LOC.finditer(out))
    errors = []
    first, last = m["lines"][0] + shift, m["lines"][1] + shift
    for k, x in enumerate(marks):
        end = marks[k + 1].start() if k + 1 < len(marks) else len(out)
        n, c, message = int(x[2]), int(x[3]), out[x.end():end].rstrip("\n")
        if first <= n <= last:
            errors.append((m["file"], n, message, c))
    verdict = trust_mutants.invalid(errors, mutated, (first, last), (at, at + len(m["after"]))) if errors else (
        "no error in the mutated declaration", "")
    where = ", ".join(f"{n}:{c}" for _, n, _, c in errors)
    return (f"{Path(record).name} {m['id']} {m['file']}:{i + 1} (record line {m['line']}) edit cols "
            f"{column}-{column + len(m['after'])}; errors at {where}: {m['raw_status']} -> {verdict[0]} "
            f"({verdict[1][:90]})")


jobs = []
for record in sys.argv[2:]:
    for m in json.loads(Path(record).read_text())["mutants"]:
        if m["status"] == "UNKNOWN":
            jobs.append((record, m))
with ThreadPoolExecutor(4) as pool:
    for line in pool.map(lambda j: one(*j), jobs):
        print(line, flush=True)
