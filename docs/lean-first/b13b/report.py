"""The numbers of lean-first batch 13b's REPORT.md, regenerated from saved evidence only.

    python docs/lean-first/b13b/report.py --capture-scope   # once, at the batch's last source commit
    python docs/lean-first/b13b/report.py --write           # rewrite REPORT.md's generated block
    python docs/lean-first/b13b/report.py                   # exit 1 if the block or the evidence is off

`--capture-scope` is the only step that reads git: it saves the branch's own commits (`main..HEAD --no-merges`)
and their line counts to `evidence/scope.json`. Everything else reads the files of `evidence/`, so the report and
its test (`tests/test_lean_first_b13b.py`) give the same answer after a sync with main and after the merge.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVIDENCE = HERE / "evidence"
REPORT = HERE / "REPORT.md"
BEGIN, END = "<!-- BEGIN GENERATED: python docs/lean-first/b13b/report.py --write -->", "<!-- END GENERATED -->"
GROUPS = {"production Python": ("ve/",), "Lean": ("lean/VE/", "lean/ResponseShape/")}


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text())


def capture_scope() -> None:
    def git(*args):
        return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout
    commits = [line.split(" ", 1) for line in git("log", "--format=%H %s", "main..HEAD", "--no-merges").splitlines()]
    files: dict[str, list[int]] = {}
    for sha, _ in commits:
        for line in git("show", "--numstat", "--format=", sha).splitlines():
            added, deleted, path = line.split("\t")
            if added != "-":
                files.setdefault(path, [0, 0])
                files[path][0] += int(added)
                files[path][1] += int(deleted)
    scope = {"head": git("rev-parse", "HEAD").strip(), "merge_base": git("merge-base", "main", "HEAD").strip(),
             "commits": [{"sha": sha, "subject": subject} for sha, subject in commits], "files": files}
    (EVIDENCE / "scope.json").write_text(json.dumps(scope, indent=1, sort_keys=True) + "\n")


def lines(scope: dict, prefixes: tuple[str, ...], suffix: str) -> tuple[int, int]:
    rows = [counts for path, counts in scope["files"].items() if path.startswith(prefixes) and path.endswith(suffix)]
    return sum(r[0] for r in rows), sum(r[1] for r in rows)


def generated() -> str:
    scope, ab, fuzz = load("scope.json"), load("corpus-ab.json"), load("difffuzz-ab.json")
    mutants, latency, gate = load("mutants.json"), load("latency.json"), load("gate.json")
    totals = ab["totals"]
    corpora: dict[str, dict] = {}
    for key, count in ab["records"].items():
        corpus = key.split("/")[0]
        corpora.setdefault(corpus, {"records": 0, "wording": 0, "order": 0, "verdict": 0, "availability": 0})
        corpora[corpus]["records"] += count
    for row in ab["differences"]:
        corpora[row["corpus"]][row["class"]] += 1
    out = ["| Corpus | Records per side | Same | Wording | Order | Verdict | Availability |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    for corpus, row in sorted(corpora.items()):
        changed = sum(row[k] for k in ("wording", "order", "verdict", "availability"))
        out.append(f"| {corpus} | {row['records']:,} | {row['records'] - changed:,} | {row['wording']} | "
                   f"{row['order']} | {row['verdict']} | {row['availability']} |")
    records = sum(totals.values())
    out.append(f"| **All** | **{records:,}** | **{totals.get('same', 0):,}** | **{totals.get('wording', 0)}** | "
               f"**{totals.get('order', 0)}** | **{totals.get('verdict', 0)}** | **{totals.get('availability', 0)}** |")
    out.append("")
    out.append(f"Unlisted differences: {ab['unlisted']}. Branch commits (`main..HEAD --no-merges`, saved): "
               f"{len(scope['commits'])}, merge base `{scope['merge_base'][:8]}`, last source commit "
               f"`{scope['head'][:8]}`.")
    for name, prefixes in GROUPS.items():
        added, deleted = lines(scope, prefixes, ".py" if name.endswith("Python") else ".lean")
        out.append(f"Code lines, {name}: +{added}/−{deleted} (net {added - deleted:+d}).")
    runs = fuzz["runs"]
    sizes = [(r["baseline"][0]["entries"], r["baseline"][1]["entries"]) for r in runs]
    out.append(f"Differential fuzz: {len(runs)} paired runs (CI and {len(runs) - 1} date seeds); reviewed baseline "
               f"{sizes[0][0]} → {sizes[0][1]}; head-only new signatures "
               f"{sum(len(r['head_only_new']) for r in runs)}; head entries not reproduced "
               f"{sum(len(r['head_not_reproduced']) for r in runs)}; all runs ok: {fuzz['ok']}.")
    caught = sum(row["caught"] for row in mutants["mutants"])
    out.append(f"Seeded faults: {caught} of {len(mutants['mutants'])} caught and restored; service build restored: "
               f"{mutants['service_build_restored']}.")
    for op in ("udhr", "eligibility", "agent-policy"):
        row = latency[op]
        out.append(f"Latency, {op}: base {row['median']['base']['wall_s']:.1f} s → head "
                   f"{row['median']['head']['wall_s']:.1f} s wall ({row['wall_ratio']:.3f}×), child CPU "
                   f"{row['child_cpu_ratio']:.3f}×; same output: {row['same_output']}; within budget: "
                   f"{row['within_budget']}.")
    counts = gate["counts"]
    out.append(f"Full gate at `{gate['commit_sha'][:8]}` (clean worktree: {not gate['dirty']}): {gate['status']}; "
               f"{counts['passed']:,} passed, {counts['skipped']} skipped, {counts['failed']} failed, "
               f"{len(gate['failures'])} failure records.")
    return "\n".join(out)


def problems() -> list[str]:
    text = REPORT.read_text()
    found = []
    if BEGIN not in text or END not in text:
        return ["REPORT.md has no generated block"]
    block = text.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    if block != generated():
        found.append("REPORT.md's generated block differs from the evidence; run report.py --write")
    ab = load("corpus-ab.json")
    if ab["unlisted"] or ab["totals"].get("verdict") or ab["totals"].get("availability"):
        found.append("the A/B has unlisted, verdict or availability differences")
    fuzz = load("difffuzz-ab.json")
    if not fuzz["ok"] or any(r["baseline"][1]["entries"] > r["baseline"][0]["entries"] for r in fuzz["runs"]):
        found.append("the differential fuzzer's baseline grew or a run failed")
    mutants = load("mutants.json")
    if len(mutants["mutants"]) < 3 or not all(r["caught"] for r in mutants["mutants"]):
        found.append("a seeded fault was not caught")
    gate = load("gate.json")
    if gate["status"] != "passed" or gate["dirty"] or gate["failures"]:
        found.append("the saved full gate did not pass on a clean worktree")
    return found


def main(argv: list[str]) -> int:
    if "--capture-scope" in argv:
        capture_scope()
        return 0
    if "--write" in argv:
        text = REPORT.read_text()
        head, rest = text.split(BEGIN, 1)
        REPORT.write_text(f"{head}{BEGIN}\n{generated()}\n{END}{rest.split(END, 1)[1]}")
    found = problems()
    print("\n".join(found) or "ok")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
