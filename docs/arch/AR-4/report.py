"""AR-4 evidence and report numbers.

    uv run python docs/arch/AR-4/report.py --collect   # at a clean HEAD: evidence/budget.json, evidence/scope.json
    uv run python docs/arch/AR-4/report.py --render    # REPORT.md's generated block, from the saved evidence only
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
sys.path.insert(0, str(ROOT))
from tools import batch_evidence, batch_scope  # noqa: E402
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
    scope = batch_scope.git_scope(base, head, ROOT)  # the one writer and checker of a batch's scope
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "budget.json").write_text(json.dumps(budget, indent=1) + "\n")
    (EVIDENCE / "scope.json").write_text(json.dumps(scope, indent=1) + "\n")


def problems() -> list[str]:
    """What the saved evidence contradicts: the plan's claims for AR-4, each from a number the tools generated."""
    budget = json.loads((EVIDENCE / "budget.json").read_text())
    scope = json.loads((EVIDENCE / "scope.json").read_text())
    migration = json.loads((EVIDENCE / "migration.json").read_text())
    mutants = json.loads((EVIDENCE / "mutants.json").read_text())["mutants"]
    full = json.loads((EVIDENCE / "gate-full-failed.json").read_text())
    rerun = json.loads((EVIDENCE / "gate-result.json").read_text())
    out = []
    if budget["check_exit"] != 0:
        out.append("trust_map.py --check failed at the evidence commit")
    if budget["measured_head"] != budget["measured_base"] or budget["introduced"] or budget["removed"]:
        out.append("AR-4 changes no Lean line and no allowance: head and base must measure the same")
    if not budget["measured_base"] == migration["measured_budget"] == budget["recorded_head"]:
        out.append("the starting budget is not the value measured at the base (D3)")
    if migration["base"] != budget["base"]:
        out.append("the migration ran at another base")
    if budget["file_lines"]["head"] != 7 * budget["allowances"] + 10:
        out.append("the budget file holds more than the comment, the budget and the allowances")
    if any(path.startswith(("ve/", "lean/", "rust/")) for path in scope["files"]):
        out.append("a file under ve/, lean/ or rust/ changed: gate items 2 and 3 apply")
    if scope.get("head") != budget["head"] or scope.get("base") != budget["base"] or not scope.get("commits"):
        out.append("the scope and the budget evidence are of different commits")
    out += batch_scope.scope_problems(scope, ROOT)  # recomputed from git: the commits, files and base
    # The gate and the measurements cover HEAD: from the gated commit and from the evidence head (either
    # may come first) to HEAD, only this directory changes.
    for start in dict.fromkeys((full.get("commit_sha"), rerun.get("commit_sha"), budget["head"])):
        try:
            out += batch_evidence.outside_report(batch_evidence.changed_since(start, "HEAD", ROOT), "docs/arch/AR-4")
        except (ValueError, subprocess.CalledProcessError) as exc:
            out.append(f"the evidence is not bound to HEAD: {exc}")
    killed = [m for m in mutants if m.get("killed") is True]
    if not killed or len(killed) != len(mutants) or {m.get("file") for m in mutants} != {"tools/trust_map.py"}:
        out.append("a seeded bug survived, or none names tools/trust_map.py")
    source = hashlib.sha256(_git("show", f"{budget['head']}:tools/trust_map.py").encode()).hexdigest()
    if {m.get("source_sha256") for m in mutants} != {source}:
        out.append("the seeded bugs ran on another tools/trust_map.py than the evidence commit's")
    failed = [f["nodeid"] for f in full["failures"] if f["stage"] == "pytest"]
    if (full["status"] != "failed" or full["dirty"] or
            full["stages"] != ["toolchains", "lean_build", "lean_audit", "rust_build", "cargo_test", "pytest"] or
            {f["stage"] for f in full["failures"]} != {"pytest command", "pytest"} or
            full["counts"]["failed"] != len(failed) or
            full["counts"]["selected"] != sum(full["counts"][k] for k in ("passed", "skipped", "failed"))):
        out.append("the full gate record is not a complete gate with only pytest failures")
    previous = rerun.get("rerun_failed", {}).get("previous", {})
    if (rerun["status"] != "rerun-passed" or rerun["dirty"] or rerun["failures"] or
            rerun["commit_sha"] != full["commit_sha"] or rerun["tree_sha"] != full["tree_sha"] or
            previous.get("commit_sha") != full["commit_sha"] or previous.get("tree_sha") != full["tree_sha"] or
            rerun["rerun_failed"]["tests"] != failed or
            rerun["rerun_failed"]["outcomes"] != {test: "passed" for test in failed} or
            rerun["counts"]["selected"] != rerun["counts"]["passed"]):
        out.append("the serial rerun did not pass every failed test on the full gate's clean commit")
    for name, record in (("full gate", full), ("serial rerun", rerun)):  # AR-4: the tables live in the record
        trust = record.get("trust")
        if trust_map.files_problems(trust) or trust["budget"] != budget["measured_head"]:
            out.append(f"the {name} record has no per-file trust counts of the evidence head "
                       f"({'; '.join(trust_map.files_problems(trust)) or 'another budget'}): rerun the gate")
    return list(dict.fromkeys(out))


def block() -> str:
    budget = json.loads((EVIDENCE / "budget.json").read_text())
    scope = json.loads((EVIDENCE / "scope.json").read_text())
    migration = json.loads((EVIDENCE / "migration.json").read_text())
    mutants = json.loads((EVIDENCE / "mutants.json").read_text())["mutants"]
    full = json.loads((EVIDENCE / "gate-full-failed.json").read_text())
    rerun = json.loads((EVIDENCE / "gate-result.json").read_text())
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
        f"Full gate at `{full['commit_sha'][:8]}`: {full['counts']['passed']:,} Python passed, "
        f"{full['counts']['skipped']:,} skipped or xfailed, {full['counts']['failed']:,} failed; "
        f"{full['counts']['rust_passed']:,} native Rust passed.",
        f"R13 serial rerun at `{rerun['commit_sha'][:8]}`: {rerun['counts']['passed']:,} passed, "
        f"{rerun['counts']['failed']:,} failed; "
        f"{', '.join(rerun['rerun_failed']['tests'])} passed on rerun.",
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
    if argv == ["--render"]:
        REPORT.write_text(rendered(text))
        return 0
    if argv == ["--check"]:
        found = problems() + (["REPORT.md's generated block is stale; run --render"] if rendered(text) != text else [])
        for problem in found:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1 if found else 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
