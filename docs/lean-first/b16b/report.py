"""The 16b report numbers: saved once from git, then regenerated from the saved evidence only.

    python docs/lean-first/b16b/report.py --capture   # write evidence/scope.json from `main..HEAD --no-merges`
    python docs/lean-first/b16b/report.py             # rewrite DELTA.md's generated block from evidence/
    python docs/lean-first/b16b/report.py --check     # exit 1 when that block differs from the evidence

`scope.json` holds the commit list of `main..HEAD --no-merges` and each commit's numstat, captured at a head; the
line counts sum those rows (source files: `ve/`, `lean/VE/`, `lean/ResponseShape/`, `conformance/`, `tools/`,
`tests/`, generated inventories and the batch's own report directory excluded). Nothing here reads git after the
capture, so the numbers survive later syncs and the merge.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
DELTA = HERE / "DELTA.md"
SOURCES = ("ve/", "lean/VE/", "lean/ResponseShape/", "conformance/", "tools/", "tests/")
GENERATED = ("lean/VE/Route/frozen-sources.sha256", "ve/assurance-manifest.json", "tools/gate-collection.json",
             "ve/backends/lean_service_schema/", "tools/lean_first_schema/")
BEGIN, END = "<!-- BEGIN GENERATED B16B METRICS -->", "<!-- END GENERATED B16B METRICS -->"


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def capture() -> None:
    head = git("rev-parse", "HEAD").strip()
    base = git("merge-base", "main", "HEAD").strip()
    commits = git("rev-list", "--no-merges", "main..HEAD").split()
    rows = []
    for commit in commits:
        for line in git("show", "--numstat", "--format=", commit).splitlines():
            added, deleted, path = line.split("\t")
            # A binary file (the gzipped corpus) has no line counts.
            rows.append({"commit": commit, "path": path, "added": 0 if added == "-" else int(added),
                         "deleted": 0 if deleted == "-" else int(deleted)})
    (EVIDENCE / "scope.json").write_text(json.dumps(
        {"range": "main..HEAD --no-merges", "captured_head": head, "base": base, "commits": commits,
         "numstat": rows}, indent=1) + "\n")


def source(path: str) -> bool:
    return path.startswith(SOURCES) and not path.startswith(GENERATED)


def metrics() -> dict:
    scope = json.loads((EVIDENCE / "scope.json").read_text())
    rows = [row for row in scope["numstat"] if source(row["path"])]

    def total(prefix, key, suffix=""):
        return sum(row[key] for row in rows if row["path"].startswith(prefix) and row["path"].endswith(suffix))
    ab = json.loads((EVIDENCE / "ab.json").read_text())
    fuzz = json.loads((EVIDENCE / "difffuzz.json").read_text())
    share = json.loads((EVIDENCE / "share.json").read_text())
    mutants = json.loads((EVIDENCE / "mutants.json").read_text())
    latency = json.loads((EVIDENCE / "latency.json").read_text())["head_run"]["documents"]
    return {
        "commits": len(scope["commits"]), "captured_head": scope["captured_head"],
        "python_added": total("ve/", "added"), "python_deleted": total("ve/", "deleted"),
        "lean_added": total("lean/", "added", ".lean"), "lean_deleted": total("lean/", "deleted", ".lean"),
        "test_added": total("tests/", "added"),
        "records": sum(ab["records"].values()), "same": ab["totals"]["same"], "unlisted": ab["unlisted"],
        "listed": ab["listed"], "pilots": ab["records"]["pilots/default"],
        "by_owner": ab["listed_records_by_owner"],
        "ci_new": fuzz["ci"]["new"], "seeds": len(fuzz["seeds"]),
        "head_only": sum(row["head_only"] for row in fuzz["seeds"]),
        "share": {name: [row["lean"], row["documents"]] for name, row in sorted(share.items())},
        "mutants": [len(mutants["mutants"]), sum(row["caught"] for row in mutants["mutants"])],
        "lean_cpu_max_ms": round(1000 * max(row["child_cpu_per_call"] for row in latency.values()), 1),
        "wall_max_ms": round(1000 * max(row["wall_max"] for row in latency.values()), 1),
    }


def block() -> str:
    m = metrics()
    share = ", ".join(f"{name} {lean:,} of {total:,}" for name, (lean, total) in m["share"].items())
    owners = ", ".join(f"{owner} {count}" for owner, count in sorted(m["by_owner"].items()))
    return "\n".join([
        BEGIN, "",
        f"- Scope: {m['commits']} commits of `main..HEAD --no-merges`, captured at `{m['captured_head'][:10]}` "
        f"(`evidence/scope.json`).",
        f"- Python under `ve/`: **{m['python_deleted']} lines deleted**, {m['python_added']} added. "
        f"Lean: **{m['lean_added']} lines added**, {m['lean_deleted']} deleted. Tests: {m['test_added']} added.",
        f"- Corpus A/B: {m['records']:,} records per side, {m['same']:,} identical, **{m['unlisted']} unlisted**; "
        f"listed: {m['listed']['order']} order, {m['listed']['verdict']} verdict (same code, text and `path` "
        f"only), {m['listed']['wording']} wording pairs, {m['listed']['unavailable']} unavailable on both sides, "
        f"{m['listed']['availability']} availability. Listed document records by the decoder whose text "
        f"changed: {owners}. Pilots: {m['pilots']} documents.",
        f"- Differential fuzzer: CI run {m['ci_new']} new signatures; {m['seeds']} date seeds, "
        f"{m['head_only']} head-only signatures.",
        f"- Documents Lean decides at the head: {share}.",
        f"- Seeded faults: {m['mutants'][1]} of {m['mutants'][0]} caught.",
        f"- Latency (owned seeds, load about 50): at most {m['lean_cpu_max_ms']} ms Lean CPU and "
        f"{m['wall_max_ms']} ms wall per `check_document`.",
        "", END])


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if args == ["--capture"]:
        capture()
        return 0
    text = DELTA.read_text()
    start, end = text.index(BEGIN), text.index(END) + len(END)
    if args == ["--check"]:
        return 0 if text[start:end] == block() else 1
    DELTA.write_text(text[:start] + block() + text[end:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
