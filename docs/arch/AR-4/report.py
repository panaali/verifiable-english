"""AR-4 evidence and report numbers.

    uv run python docs/arch/AR-4/report.py --collect   # at a clean HEAD: evidence/budget.json, evidence/scope.json
    uv run python docs/arch/AR-4/report.py --render    # REPORT.md's generated block, from the saved evidence only
    uv run python docs/arch/AR-4/report.py --check     # exit 1 if the block or the evidence disagree (gate, merge train)
    uv run python docs/arch/AR-4/report.py --check --gate GATE.json [RERUN.json]
                                                       # also the full gate of the final HEAD (`tools/gate.py --output`)
                                                       # and, under R13, its serial rerun (`--rerun-failed`)

`--collect` measures the head and the merge base with `tools/trust_map.py` (its `measure` and `measure_rev`, the one
owner of the counts), reads the committed budget file, and lists the batch's commits (`base..HEAD --no-merges`) and
changed files. The checks are D4's: the evidence is checked here, at the batch gate and by the merge train, not by a
permanent test. Every saved file is checked against its writer's schema before it is used, so malformed evidence or a
malformed gate record is refused with a message, never a crash (recheck F7). No gate record is kept in the tree: the
chain runs the full gate on the final HEAD and passes its record with `--gate`.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "docs/arch/AR-4"
EVIDENCE = HERE / "evidence"
REPORT = HERE / "REPORT.md"
DELTA = HERE / "DELTA.md"
# Changed product files under tools/ with no behaviour to seed a bug in, each with the reason.
NO_MUTANT: dict[str, str] = {}
BEGIN, END = "<!-- BEGIN GENERATED AR-4 METRICS -->", "<!-- END GENERATED AR-4 METRICS -->"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
from tools import batch_evidence, batch_scope  # noqa: E402
from tools.evidence import EvidenceError, load  # noqa: E402
import trust_map  # noqa: E402

SHA = re.compile(r"[0-9a-f]{40}")
# What `collect` writes to evidence/budget.json and `migrate_baseline.py` to evidence/migration.json.
BUDGET_FIELDS = ("head", "base", "measured_head", "measured_base", "recorded_base", "recorded_head", "allowances",
                 "unsigned_allowances", "introduced", "removed", "file_lines", "check_exit")
MIGRATION_FIELDS = ("base", "recorded_budget", "measured_budget", "old_lines", "new_lines", "old_keys",
                    "history_entries", "distinct_entries", "allowances", "signed_allowances", "per_file_modules",
                    "section11_rows")
# Standing ruling R15 signs the starting budget; DELTA row 1's Ruling cell is this text and the value measured.
R15 = "SIGNED by standing ruling R15 (DRI-RULINGS.md)"


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


def starting_budget_problems(budget: dict) -> list[str]:
    """D3 and standing ruling R15: the starting budget is the value measured at AR-4's merge base with `main`.
    DELTA row 1 states it, and its Ruling cell is R15's signature quoting exactly that value, so a sync that
    changes the value needs the cell changed with it."""
    value = ", ".join(f"{c} {budget['recorded_head'][c]:,}" for c in trust_map.BUDGET)
    rows = [line for line in DELTA.read_text().splitlines() if line.startswith("| 1 |")]
    cells = [cell.strip() for cell in rows[0].strip().strip("|").split("|")] if len(rows) == 1 else []
    if len(cells) != 4 or f"The starting budget is {value}:" not in cells[1]:
        return [f"DELTA.md row 1 does not state the starting budget {value} of the evidence"]
    signed = f"{R15}: {value}"
    if cells[2] != signed:
        return [f"DELTA.md row 1's Ruling cell is not R15's signature of the measured starting budget: `{signed}`"]
    return []


def budget_shape(budget: object) -> list[str]:
    """Why `budget` is not what `collect` writes (evidence/budget.json): exactly its fields, with their types."""
    if not isinstance(budget, dict) or set(budget) != set(BUDGET_FIELDS):
        return [f"evidence/budget.json holds exactly {', '.join(BUDGET_FIELDS)}"]
    budgets = set(trust_map.BUDGET)
    bad = [k for k in ("head", "base") if not isinstance(budget[k], str) or not SHA.fullmatch(budget[k])]
    bad += [k for k in ("measured_head", "measured_base", "recorded_base", "recorded_head")
            if not trust_map.nonnegative_int_record(budget[k], budgets)]
    bad += [k for k in ("allowances", "unsigned_allowances", "check_exit") if type(budget[k]) is not int]
    bad += [k for k in ("introduced", "removed") if not isinstance(budget[k], list)
            or any(trust_map.allowance_problems(entry) for entry in budget[k])]
    bad += [] if trust_map.nonnegative_int_record(budget["file_lines"], {"base", "head"}) else ["file_lines"]
    return [f"evidence/budget.json: `{k}` is not what --collect writes" for k in bad]


def migration_shape(migration: object) -> list[str]:
    """Why `migration` is not what `migrate_baseline.py` writes (evidence/migration.json)."""
    if not isinstance(migration, dict) or set(migration) != set(MIGRATION_FIELDS):
        return [f"evidence/migration.json holds exactly {', '.join(MIGRATION_FIELDS)}"]
    bad = [] if isinstance(migration["base"], str) and SHA.fullmatch(migration["base"]) else ["base"]
    bad += [k for k in ("recorded_budget", "measured_budget")
            if not trust_map.nonnegative_int_record(migration[k], set(trust_map.BUDGET))]
    bad += [] if isinstance(migration["old_keys"], list) and all(isinstance(k, str) for k in migration["old_keys"]) \
        else ["old_keys"]
    bad += [k for k in MIGRATION_FIELDS[3:] if k != "old_keys" and (type(migration[k]) is not int or migration[k] < 0)]
    return [f"evidence/migration.json: `{k}` is not what migrate_baseline.py writes" for k in bad]


def saved() -> tuple[dict, list[str]]:
    """The saved evidence, each file read as JSON and checked against its writer's schema before any use."""
    found, out = {}, []
    for name in ("budget", "scope", "migration", "mutants"):
        try:
            found[name] = load(EVIDENCE / f"{name}.json")
        except (OSError, EvidenceError, RecursionError) as exc:
            out.append(f"evidence/{name}.json cannot be read: {exc}")
    if out:
        return found, out
    # The scope is untrusted evidence: its writer's git-backed checker runs before its paths are used.
    out += budget_shape(found["budget"]) + migration_shape(found["migration"])
    out += batch_scope.scope_problems(found["scope"], ROOT)
    out += batch_evidence.mutant_problems(found["mutants"], 1)
    return found, out


def gate_problems(paths: list[Path], budget: dict) -> tuple[list[str], list[str]]:
    """The gated commits and the problems of the full gate's record (`tools/gate.py --output`) on the final
    HEAD, and under R13 its serial rerun: a passed gate (`batch_evidence.gate_record_problems`) or a gate whose
    only failures passed on the rerun of the same commit (`rerun_pair_problems`), every record with the per-file
    trust counts of the evidence head (`gate_trust_problems`). Any value is a problem or a pass, never a crash."""
    records = []
    for path in paths:
        try:
            records.append(load(path))
        except (OSError, EvidenceError, RecursionError) as exc:
            return [], [f"the full gate record {path} cannot be read: {exc}"]
    commits = [r.get("commit_sha") if isinstance(r, dict) else None for r in records]
    if not all(isinstance(c, str) and SHA.fullmatch(c) for c in commits):
        return [], ["a full gate record names no gated commit"]
    if len(records) == 1:
        out = batch_evidence.gate_record_problems(commits[0], records[0])
    else:
        out = batch_evidence.rerun_pair_problems(*records)
    for record in records:
        out += batch_evidence.gate_trust_problems(record, budget["measured_head"])
    return commits, out


def _problems(gates: list[Path]) -> list[str]:
    found, out = saved()
    if out:
        return out
    budget, scope, migration = found["budget"], found["scope"], found["migration"]
    mutants = batch_evidence.mutant_rows(found["mutants"])
    commits, out = gate_problems(gates, budget) if gates else ([], [])
    if budget["check_exit"] != 0:
        out.append("trust_map.py --check failed at the evidence commit")
    if budget["measured_head"] != budget["measured_base"] or budget["introduced"] or budget["removed"]:
        out.append("AR-4 changes no Lean line and no allowance: head and base must measure the same")
    if not budget["measured_base"] == migration["measured_budget"] == budget["recorded_head"]:
        out.append("the starting budget is not the value measured at the base (D3)")
    out += starting_budget_problems(budget)
    if migration["base"] != budget["base"]:
        out.append("the migration ran at another base")
    if budget["file_lines"]["head"] != 7 * budget["allowances"] + 10:
        out.append("the budget file holds more than the comment, the budget and the allowances")
    if any(path.startswith(("ve/", "lean/", "rust/")) for path in scope["files"]):
        out.append("a file under ve/, lean/ or rust/ changed: gate items 2 and 3 apply")
    if scope["head"] != budget["head"] or scope["base"] != budget["base"]:
        out.append("the scope and the budget evidence are of different commits")
    # The gate and the measurements cover HEAD: from each gated commit and from the evidence head (either may
    # come first) to HEAD, only this directory changes.
    for start in dict.fromkeys((*commits, budget["head"])):
        try:
            out += batch_evidence.outside_report(batch_evidence.changed_since(start, "HEAD", ROOT), "docs/arch/AR-4")
        except (ValueError, subprocess.CalledProcessError) as exc:
            out.append(f"the evidence is not bound to HEAD: {exc}")
    product = {path for path in scope["files"] if path.startswith("tools/") and path.endswith(".py")}
    if any(m.get("killed") is not True for m in mutants) or not (product - set(NO_MUTANT)) <= {m["file"] for m in mutants}:
        out.append(f"a seeded bug survived, or the seeded bugs do not cover {', '.join(sorted(product - set(NO_MUTANT)))}")
    out += batch_evidence.mutant_source_problems(mutants, budget["head"], ROOT)
    return list(dict.fromkeys(out))


def problems(gates: list[Path] = ()) -> list[str]:
    """What the saved evidence (and, given, the full gate's records) contradicts: the plan's claims for AR-4,
    each from a number the tools generated. Malformed or missing evidence is a problem, never an exception:
    each file is checked against its writer's schema first, and anything they miss still fails closed here."""
    try:
        return _problems(list(gates))
    except (LookupError, TypeError, ValueError, AttributeError, OSError, RecursionError) as exc:
        return [f"the saved evidence is malformed: {exc!r}"]


def block(found: dict) -> str:
    """REPORT.md's generated block, from the saved evidence `saved()` read and checked."""
    budget, scope, migration = found["budget"], found["scope"], found["migration"]
    mutants = batch_evidence.mutant_rows(found["mutants"])
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


def rendered(text: str, found: dict) -> str:
    head, rest = text.split(BEGIN, 1)
    return head + BEGIN + "\n" + block(found) + "\n" + END + rest.split(END, 1)[1]


def main(argv: list[str]) -> int:
    if argv == ["--collect"]:
        collect()
        return 0
    text = REPORT.read_text()
    if argv == ["--render"]:
        found, bad = saved()
        for problem in bad:
            print(f"FAIL: {problem}", file=sys.stderr)
        if not bad:
            REPORT.write_text(rendered(text, found))
        return 1 if bad else 0
    if argv[:1] == ["--check"] and (len(argv) == 1 or argv[1] == "--gate" and len(argv) in (3, 4)):
        gates = [Path(path) for path in argv[2:]]
        found = problems(gates)
        if not found and rendered(text, saved()[0]) != text:
            found.append("REPORT.md's generated block is stale; run --render")
        for problem in found:
            print(f"FAIL: {problem}", file=sys.stderr)
        if not gates:
            print("note: no full gate record checked; after `tools/gate.py` on the final HEAD, run `--check --gate "
                  "GATE.json` (and under R13 its serial rerun's record after it)", file=sys.stderr)
        return 1 if found else 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
