"""Render batch 16f metrics from committed evidence only (architecture decision D4: saved evidence, checked at the
batch gate and by the merge train; no live git and no moving HEAD).

    python docs/lean-first/b16f/report.py           # print the metrics block
    python docs/lean-first/b16f/report.py --write   # replace the block in DELTA.md
    python docs/lean-first/b16f/report.py --scope   # save evidence/scope.json for the commits so far
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
BEGIN, END = "<!-- BEGIN GENERATED B16F METRICS -->\n", "<!-- END GENERATED B16F METRICS -->"


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
    cpu = data("cpu.json")
    gate = data("relay-gate.json")
    fuzz = data("difffuzz-ci.json")
    ours = [r for r in cases if not r.get("outside")]
    outside = [r for r in cases if r.get("outside")]
    count = Counter(r["decision"] for r in ours)
    differing = sum("prior_error" in r for r in ours if r["decision"] == "error")
    by_group = Counter((r["group"], r["decision"]) for r in ours)
    groups = sorted({r["group"] for r in ours})
    files = sorted({m["file"] for m in mutants})
    languages = Counter("Lean" if m["file"].endswith(".lean") else "Python" for m in mutants)
    ratios = [row[f"{op}_ratio"] for row in cpu["rows"] for op in ("check", "render")]
    return "\n".join([
        f"- Saved scope: `{scope['base'][:8]}..{scope['head'][:8]} --no-merges`, {len(scope['commits'])} commit(s).",
        f"- Batch 16f's groups (16c ledger, {len(ours)} cases): Lean decided {count['ok'] + count['error']}/{len(ours)} "
        f"({count['ok']} accepted with the prior path's report, {count['error']} rejected, {differing} with an error "
        f"differing from the prior path's); {count['retained']} retained invalid inputs.",
        "- By group: " + "; ".join(
            f"{g} " + ", ".join(f"{n} {d}" for (gg, d), n in sorted(by_group.items()) if gg == g) for g in groups) + ".",
        f"- Outside the batch's groups: {len(outside)} cases, {sum('outside_problem' in r for r in outside)} of them "
        f"valid documents still on the retained path.",
        f"- Nine-corpus A/B: {sum(ab['records'].values())} records per side; {ab['totals'].get('same', 0)} the same; "
        f"{ab['unlisted']} unlisted differences "
        f"({', '.join(f'{n} {k}' for k, n in sorted(ab['totals'].items()) if k != 'same')} listed in delta.json).",
        f"- Seeded faults caught: {sum(m['caught'] for m in mutants)}/{len(mutants)} "
        f"({languages['Lean']} Lean, {languages['Python']} Python), in {', '.join(files)}.",
        f"- Relay mutation gate (document route): {gate['routes']['service:document']['mutants']} mutants, "
        f"{gate['routes']['service:document']['refused']} refused, {gate['routes']['service:document']['allowed']} "
        f"allowed, {len(gate['failures'])} failures. "
        f"Differential fuzz (CI sample): {len(fuzz['new'])} new differences, passed {fuzz['passed']}.",
        f"- CPU, head over base, on {len(cpu['rows'])} pilots: check and render ratios {min(ratios)} to {max(ratios)}; "
        f"the Lean document request at most "
        f"{max(row['head_lean_document_request_s'] for row in cpu['rows'])} s.",
    ])


def write() -> None:
    path = HERE / "DELTA.md"
    text = path.read_text()
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    path.write_text(head + BEGIN + metrics() + "\n" + END + tail)


if __name__ == "__main__":
    if sys.argv[1:] == ["--scope"]:
        save_scope()
    elif sys.argv[1:] == ["--write"]:
        write()
    else:
        print(metrics())
