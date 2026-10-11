"""AR-4 evidence and report numbers.

    uv run python docs/arch/AR-4/report.py --collect   # at a clean HEAD: evidence/budget.json, evidence/scope.json
    uv run python docs/arch/AR-4/report.py --write     # REPORT.md's generated block, from the saved evidence only
    uv run python docs/arch/AR-4/report.py --check     # exit 1 if the block or the evidence disagree (gate, merge train)

`--collect` measures the head and the merge base with `tools/trust_map.py` (its `measure` and `measure_rev`, the one
owner of the counts), reads the committed budget file, and lists the batch's commits (`base..HEAD --no-merges`) and
changed files. The checks are D4's: the evidence is checked here, at the batch gate and by the merge train, not by a
permanent test.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "docs/arch/AR-4"
EVIDENCE = HERE / "evidence"
REPORT = HERE / "REPORT.md"
BEGIN, END = "<!-- BEGIN GENERATED AR-4 METRICS -->", "<!-- END GENERATED AR-4 METRICS -->"
sys.path.insert(0, str(ROOT / "tools"))
import trust_map  # noqa: E402


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


def collect() -> None:
    if _git("status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("commit first: the evidence is collected at a clean HEAD")
    head = _git("rev-parse", "HEAD").strip()
    base = _git("merge-base", "HEAD", "main").strip()
    files, problems = trust_map.measure()
    base_files, base_problems, base_data = trust_map.measure_rev(base)
    if problems or base_problems:
        raise SystemExit("\n".join(problems + base_problems))
    data, bad = trust_map.parse_baseline(json.loads(trust_map.BASELINE.read_text()))
    if bad:
        raise SystemExit("\n".join(bad))
    allowances = data["allowances"]
    budget = {"head": head, "base": base, "measured_head": trust_map.budget(trust_map.totals(files)),
              "measured_base": trust_map.budget(trust_map.totals(base_files)),
              "recorded_base": trust_map.budget(base_data["totals"]), "recorded_head": data["budget"],
              "allowances": len(allowances),
              "unsigned_allowances": sum(a["signature"] == trust_map.UNSIGNED for a in allowances),
              "introduced": trust_map.introduced(allowances, trust_map.from_history(base_data)),
              "removed": trust_map.introduced(trust_map.from_history(base_data), allowances),
              "file_lines": {"base": len(_git("show", f"{base}:{trust_map.BASELINE.relative_to(ROOT)}").splitlines()),
                             "head": len(trust_map.BASELINE.read_text().splitlines())},
              "check_exit": trust_map.main(["--check"])}
    commits = [dict(zip(("hash", "subject"), line.split(" ", 1)))
               for line in _git("log", "--no-merges", "--format=%H %s", f"{base}..HEAD").splitlines()]
    changed = sorted(_git("diff", "--name-only", f"{base}..HEAD").split())
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "budget.json").write_text(json.dumps(budget, indent=1) + "\n")
    (EVIDENCE / "scope.json").write_text(json.dumps({"base": base, "head": head, "commits": commits,
                                                     "files": changed}, indent=1) + "\n")


def problems() -> list[str]:
    """What the saved evidence contradicts: the plan's claims for AR-4, each from a number the tools generated."""
    budget = json.loads((EVIDENCE / "budget.json").read_text())
    scope = json.loads((EVIDENCE / "scope.json").read_text())
    migration = json.loads((EVIDENCE / "migration.json").read_text())
    mutants = json.loads((EVIDENCE / "mutants.json").read_text())["mutants"]
    out = []
    if budget["check_exit"] != 0:
        out.append("trust_map.py --check failed at the evidence commit")
    if budget["measured_head"] != budget["measured_base"] or budget["introduced"] or budget["removed"]:
        out.append("AR-4 changes no Lean line and no allowance: head and base must measure the same")
    if not budget["measured_base"] == migration["measured_budget"] == budget["recorded_head"]:
        out.append("the starting budget is not the value measured at the base (D3)")
    if migration["base"] != budget["base"]:
        out.append("the migration ran at another base")
    if budget["file_lines"]["head"] >= 300:
        out.append("the budget file is not under 300 lines (plan outcome)")
    if any(path.startswith(("ve/", "lean/", "rust/")) for path in scope["files"]):
        out.append("a file under ve/, lean/ or rust/ changed: gate items 2 and 3 apply")
    if scope["head"] != budget["head"] or not scope["commits"]:
        out.append("the scope and the budget evidence are of different commits")
    killed = [m for m in mutants if m.get("killed") is True]
    if not killed or len(killed) != len(mutants) or {m.get("file") for m in mutants} != {"tools/trust_map.py"}:
        out.append("a seeded bug survived, or none names tools/trust_map.py")
    source = hashlib.sha256(_git("show", f"{budget['head']}:tools/trust_map.py").encode()).hexdigest()
    if {m.get("source_sha256") for m in mutants} != {source}:
        out.append("the seeded bugs ran on another tools/trust_map.py than the evidence commit's")
    return out


def block() -> str:
    budget = json.loads((EVIDENCE / "budget.json").read_text())
    scope = json.loads((EVIDENCE / "scope.json").read_text())
    migration = json.loads((EVIDENCE / "migration.json").read_text())
    mutants = json.loads((EVIDENCE / "mutants.json").read_text())["mutants"]
    head, base = budget["measured_head"], budget["measured_base"]
    lines = [
        f"Measured with `tools/trust_map.py` at `{budget['head'][:8]}` against the merge base `{budget['base'][:8]}`:",
        "",
        "| Class | Recorded at the base | Measured at the base | Measured at the head | Starting budget |",
        "|---|---:|---:|---:|---:|",
        *(f"| {c} | {budget['recorded_base'][c]:,} | {base[c]:,} | {head[c]:,} | {budget['recorded_head'][c]:,} |"
          for c in trust_map.BUDGET),
        "",
        f"`docs/trust-baseline.json`: {budget['file_lines']['base']:,} lines at the base, "
        f"{budget['file_lines']['head']:,} at the head (keys before: {', '.join(migration['old_keys'])}; "
        f"{migration['per_file_modules']} per-file rows and {migration['section11_rows']} `section11` rows left the tree).",
        f"History: {migration['history_entries']} entries, {migration['distinct_entries']} distinct, became "
        f"{budget['allowances']} allowances (one per class that grew); {budget['allowances'] - budget['unsigned_allowances']} "
        f"carry a DRI signature, {budget['unsigned_allowances']} were rebaselines with a reason before AR-4.",
        f"`trust_map.py --check` at the head: exit {budget['check_exit']}; allowances introduced: "
        f"{len(budget['introduced'])}, removed: {len(budget['removed'])}.",
        f"Commits (`{budget['base'][:8]}..{budget['head'][:8]} --no-merges`): {len(scope['commits'])}; files changed: "
        f"{len(scope['files'])}, none under `ve/`, `lean/` or `rust/`: "
        f"{'yes' if not any(p.startswith(('ve/', 'lean/', 'rust/')) for p in scope['files']) else 'no'}.",
        f"Seeded bugs: {len(mutants)}, each killed by its named test: "
        f"{'yes' if all(m.get('killed') is True for m in mutants) else 'no'}.",
    ]
    return "\n".join(lines)


def rendered(text: str) -> str:
    head, rest = text.split(BEGIN, 1)
    return head + BEGIN + "\n" + block() + "\n" + END + rest.split(END, 1)[1]


def main(argv: list[str]) -> int:
    if argv == ["--collect"]:
        collect()
        return 0
    text = REPORT.read_text()
    if argv == ["--write"]:
        REPORT.write_text(rendered(text))
        return 0
    if argv == ["--check"]:
        found = problems() + (["REPORT.md's generated block is stale; run --write"] if rendered(text) != text else [])
        for problem in found:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1 if found else 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
