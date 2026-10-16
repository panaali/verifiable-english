"""Render batch 16e metrics from committed evidence only (architecture decision D4: saved evidence, checked at the
batch gate and by the merge train; no live git and no moving HEAD).

    python docs/lean-first/b16e/report.py           # print the metrics block
    python docs/lean-first/b16e/report.py --scope   # save evidence/scope.json for the commits so far
"""
from __future__ import annotations

from collections import Counter
import gzip
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVIDENCE = HERE / "evidence"


def data(name: str):
    path = EVIDENCE / name
    if name.endswith(".gz"):
        return json.loads(gzip.decompress(path.read_bytes()))
    return json.loads(path.read_text())


def save_scope() -> None:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout
    base = git("merge-base", "HEAD", "main").strip()
    head = git("rev-parse", "HEAD").strip()
    commits = [dict(zip(("hash", "subject"), line.split("\t", 1)))
               for line in git("log", "--no-merges", "--format=%H\t%s", f"{base}..{head}").splitlines()]
    (EVIDENCE / "scope.json").write_text(json.dumps({
        "base": base, "head": head, "command": "git log --no-merges $(git merge-base HEAD main)..HEAD",
        "commits": commits}, indent=2) + "\n")


def metrics() -> str:
    scope = data("scope.json")
    cases = data("cases.json.gz")
    ab = data("ab.json")
    mutants = data("mutants.json")
    count = Counter(r["decision"] for r in cases)
    differing = sum("prior_error" in r for r in cases if r["decision"] == "error")
    causes = Counter(r["prior_error"]["code"] for r in cases if r["decision"] == "retained")
    files = sorted({m["file"] for m in mutants})
    return "\n".join([
        f"- Saved scope: `{scope['base'][:8]}..{scope['head'][:8]} --no-merges`, {len(scope['commits'])} commit(s).",
        f"- rights (16c ledger, {len(cases)} cases): Lean decided {count['ok'] + count['error']}/{len(cases)} "
        f"({count['ok']} accepted with the prior path's report, {count['error']} rejected, {differing} with an "
        f"error differing from the prior path's); {count['retained']} retained invalid inputs "
        f"({', '.join(f'{n} {code}' for code, n in sorted(causes.items()))}).",
        f"- Nine-corpus A/B: {sum(ab['records'].values())} records per side; "
        f"{ab['totals'].get('same', 0)} the same; {ab['unlisted']} unlisted differences "
        f"({', '.join(f'{n} {k}' for k, n in sorted(ab['totals'].items()) if k != 'same')} listed in delta.json).",
        f"- Seeded faults caught: {sum(m['caught'] for m in mutants)}/{len(mutants)}, in {', '.join(files)}.",
    ])


if __name__ == "__main__":
    if sys.argv[1:] == ["--scope"]:
        save_scope()
    else:
        print(metrics())
