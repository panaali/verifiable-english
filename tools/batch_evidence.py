"""Check that a batch's saved gate, corpus comparison and latency evidence cover HEAD.

    python tools/batch_evidence.py --check docs/<track>/<batch> [--report-commit SHA]
    python tools/batch_evidence.py HEAD GATE.json COMPARISON.json LATENCY.json [--report-commit SHA --report-dir DIR]

`--check` reads the batch's `evidence.toml` (tools/evidence/config.py) and every evidence file it names: the
saved scope, the gate of the scope's head, the seeded mutants, and where named the corpus A/B, latency, fuzz
A/B, the rendered report block and the claims. It runs at the batch's gate and in the merge train instead of
a permanent report test (DRI decision D4). The positional form checks the three files alone, as before.

Every piece of evidence is tied to the batch (arch-20261010-2 review F1 to F3): the scope starts at the batch's
merge base with `--main` (default `main`; `tools.evidence.merge_base`, which a later merge does not move), each
A/B record compared that base with the scope's head, each seeded mutant ran on its file as committed at the
head, and every file the check opens is inside the repository and, with `--report-commit`, committed there
byte for byte (an ignored or uncommitted file is no evidence the merge train can carry).

The gate result lives in a git note so recording it does not move the commit it
checked. Call this tool with the final commit and the three evidence files before
attaching the note. No missing or partial measurement counts as a pass.

A note is a local ref that a merge or push does not carry, so the batch may also commit
a copy of the evidence. That report commit comes after the gated one; with
`--report-commit SHA --report-dir DIR` the tool also checks that the gated commit is an
ancestor of it and that nothing between them changes a path outside DIR, so the gate
still covers every line of code the report commit holds.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.evidence import EvidenceError, killed, load, merge_base, read_bytes, recording, scope_range  # noqa: E402
from tools.evidence import ab, config as evidence_config, fuzz_ab, latency as evidence_latency, report  # noqa: E402

REQUIRED_STAGES = ("toolchains", "lean_build", "lean_audit", "rust_build", "cargo_test", "pytest")
REQUIRED_CORPORA = set(ab.REQUIRED_CORPORA)
SHA = re.compile(r"[0-9a-f]{40}")


def problems(head: str, gate: dict, comparison: dict, latency: dict) -> list[str]:
    return (gate_problems(head, gate) + ab.problems(comparison, head, REQUIRED_CORPORA)
            + evidence_latency.problems(latency, head))


def gate_problems(head: str, gate: dict) -> list[str]:
    if not isinstance(gate, dict):
        return ["full gate result is not a record"]
    errors = []
    if gate.get("commit_sha") != head or gate.get("dirty") is not False:
        errors.append("full gate did not run on a clean HEAD")
    if gate.get("status") != "passed" or gate.get("stages") != list(REQUIRED_STAGES):
        errors.append("full gate is incomplete or failed")
    counts = gate.get("counts")
    if not isinstance(counts, dict) or not all(type(counts.get(key)) is int and counts[key] > 0
                                                for key in ("passed", "rust_passed")):
        errors.append("full gate has no passing Python and Rust tests")
    return errors


def outside_report(changed: list[str], report_dir: str) -> list[str]:
    """The errors of a commit after the gate: every changed path outside `report_dir`."""
    prefix = report_dir.strip("/") + "/"
    outside = sorted(path for path in changed if not path.startswith(prefix))
    return [f"a commit after the gate changes {path}, outside {prefix}" for path in outside]


def changed_since(gated: str, report: str, cwd: Path | None = None) -> list[str]:
    """The paths that differ between the gated commit and the report commit (renames as delete and add), or an
    error if the gated commit is not an ancestor of the report commit."""
    git = ["git", "--no-optional-locks", "-c", "core.quotePath=false"]
    if subprocess.run(git + ["merge-base", "--is-ancestor", gated, report], cwd=cwd).returncode != 0:
        raise ValueError(f"the gated commit {gated} is not an ancestor of {report}")
    out = subprocess.run(git + ["diff", "--no-renames", "--name-only", "-z", gated, report], cwd=cwd,
                         check=True, capture_output=True).stdout
    return [path for path in out.decode().split("\0") if path]


def scope_problems(scope: dict) -> list[str]:
    """The errors of a saved scope (`python -m tools.evidence scope`): the batch's own commits, newest first."""
    if not isinstance(scope, dict):
        return ["scope is not a record"]
    errors = []
    if not all(isinstance(scope.get(k), str) and SHA.fullmatch(scope[k]) for k in ("base", "head")) \
            or scope["base"] == scope["head"]:
        errors.append("scope has no distinct base and head commits")
    commits = scope.get("commits")
    if not isinstance(commits, list) or not commits or not all(
            isinstance(c, dict) and isinstance(c.get("hash"), str) and SHA.fullmatch(c["hash"]) for c in commits):
        errors.append("scope lists no commits")
    elif commits[0]["hash"] != scope.get("head") or len({c["hash"] for c in commits}) != len(commits):
        errors.append("scope's newest commit is not its head, or it lists a commit twice")
    changes = scope.get("changes")
    if not isinstance(changes, list) or not changes or not all(
            isinstance(c, dict) and isinstance(c.get("path"), str) and c["path"] for c in changes):
        errors.append("scope lists no changed paths")
    return errors


def scope_history_problems(saved: dict, main: str = "main", cwd: Path | None = None) -> list[str]:
    """Compare the saved scope with the batch's range from its merge base with `main`, replayed from Git: a
    base inside the batch would drop its earlier commits (and with them the `ve/` and `lean/` paths that
    require a corpus A/B).

    The merge base does not move when `main` does (`tools.evidence.merge_base`), so a later merge to main
    cannot change a batch's report. The saved base must be that very commit, even when another base's range
    holds the same commits and changes (arch-20261010-2 recheck F1): every A/B record is bound to the saved
    base, and an A/B against a later `main` that adopted the batch's change would show no difference.
    """
    if scope_problems(saved):
        return []  # the shape errors already explain why history cannot be compared
    cwd = cwd or ROOT
    try:
        base = merge_base(saved["head"], main, cwd)
        actual = scope_range(base, saved["head"], cwd)
    except (EvidenceError, subprocess.CalledProcessError) as exc:
        return [f"scope cannot be reproduced from its Git objects: {exc}"]
    errors = []
    if saved["base"] != base:
        errors.append(f"scope base {saved['base'][:8]} is not the batch's merge base {base[:8]} with {main}")
    for field in ("commits", "changes"):
        if saved[field] != actual[field]:
            errors.append(f"scope {field} differ from the batch's {base[:8]}..{saved['head'][:8]} --no-merges "
                          f"(its merge base with {main})")
    return errors


def gate_record_problems(head: str, gate: dict) -> list[str]:
    """`gate_problems`, and the counts and failures of the gate's own record must agree."""
    errors = gate_problems(head, gate)
    counts = gate.get("counts") if isinstance(gate, dict) else None
    keys = ("passed", "skipped", "failed", "selected", "deselected", "collected")
    if not isinstance(counts, dict) or not all(type(counts.get(k)) is int and counts[k] >= 0 for k in keys) \
            or counts["passed"] + counts["skipped"] + counts["failed"] != counts["selected"] \
            or counts["selected"] + counts["deselected"] != counts["collected"] or counts["failed"] != 0:
        errors.append("full gate counts do not add up or show a failure")
    if not isinstance(gate, dict) or gate.get("failures") != []:
        errors.append("full gate lists failures")
    return errors


def mutant_source_problems(mutants, head: str, cwd: Path | None = None) -> list[str]:
    """Each `tools/mutants.py` record ran on its file as committed at `head`: its `source_sha256` is that
    blob's. (The records batches kept before the toolkit hash nothing, `tools.evidence.killed`.)"""
    rows = mutants.get("mutants") if isinstance(mutants, dict) else mutants
    cwd, errors = cwd or ROOT, []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict) or "killed" not in row or not isinstance(row.get("file"), str):
            continue
        name = row.get("id", row["file"])
        try:
            blob = subprocess.run(["git", "cat-file", "blob", f"{head}:{row['file']}"], cwd=cwd, check=True,
                                  capture_output=True).stdout
        except subprocess.CalledProcessError:
            errors.append(f"seeded mutant {name}: {row['file']} is not a file at {head}")
            continue
        if row.get("source_sha256") != hashlib.sha256(blob).hexdigest():
            errors.append(f"seeded mutant {name} ran on another {row['file']} than the one at {head}")
    return errors


def committed_problems(paths: list[Path], commit: str | None, cwd: Path | None = None) -> list[str]:
    """Every file the check opened is inside the repository and, given a `commit`, committed there with the
    same bytes."""
    cwd, errors = cwd or ROOT, []
    for path in dict.fromkeys(paths):
        if not evidence_config.in_repository(path):
            errors.append(f"{path} is outside the repository")
        elif commit is not None:
            relative = path.relative_to(cwd.resolve()).as_posix()
            done = subprocess.run(["git", "cat-file", "blob", f"{commit}:{relative}"], cwd=cwd, capture_output=True)
            if done.returncode != 0 or done.stdout != path.read_bytes():
                errors.append(f"{relative} is not committed as read at {commit}")
    return errors


def mutant_problems(mutants, minimum: int = 3) -> list[str]:
    """The errors of seeded-mutant records: at least `minimum`, each named once, each failing its named test."""
    rows = mutants.get("mutants") if isinstance(mutants, dict) else mutants
    if not isinstance(rows, list) or len(rows) < minimum:
        return [f"fewer than {minimum} seeded mutants are recorded"]
    errors = []
    names = [row.get("id", row.get("bug")) if isinstance(row, dict) else None for row in rows]
    if None in names or len(set(map(str, names))) != len(names):
        errors.append("a seeded mutant has no name, or two share one")
    errors += [f"seeded mutant {name} names no file or no failing test" for name, row in zip(names, rows)
               if not killed(row)]
    return errors


def tally_problems(claim: dict, evidence: report.Evidence) -> list[str]:
    """A per-case ledger agrees with a saved summary table: for each `group` value of `table`, the rows of
    the group counted by `field` equal `table[group][counts]`, and with `rest` they make up `total`."""
    fields = {"kind", "rows", "group", "field", "table", "counts", "unique", "keys", "total", "rest"}
    if set(claim) - fields or not {"rows", "group", "field", "table", "counts"} <= set(claim):
        return [f"tally claim has not the fields {sorted(fields)}: {sorted(claim)}"]
    rows, table = evidence.lookup(claim["rows"]), evidence.lookup(claim["table"])
    if not isinstance(rows, list) or not isinstance(table, dict) or not table:
        return [f"tally {claim['rows']}: no rows or no table"]
    errors = []
    if not all(isinstance(row, dict) for row in rows):
        return [f"tally {claim['rows']}: a row is not a record"]
    if "keys" in claim and any(set(row) != set(claim["keys"]) for row in rows):
        errors.append(f"tally {claim['rows']}: a row's fields are not {claim['keys']}")
    if "unique" in claim and len({tuple(row.get(k) for k in claim["unique"]) for row in rows}) != len(rows):
        errors.append(f"tally {claim['rows']}: two rows share {claim['unique']}")
    if {row.get(claim["group"]) for row in rows} - table.keys():
        errors.append(f"tally {claim['rows']}: a row's {claim['group']} is not in {claim['table']}")
    for group, saved in table.items():
        counted = Counter(row.get(claim["field"]) for row in rows if row.get(claim["group"]) == group)
        if not isinstance(saved, dict) or dict(counted) != saved.get(claim["counts"]):
            errors.append(f"tally {claim['rows']}: {group} counts differ from {claim['table']}")
        elif "total" in claim and sum(counted.values()) + saved.get(claim.get("rest"), 0) != saved.get(claim["total"]):
            errors.append(f"tally {claim['rows']}: {group} rows and {claim.get('rest')} do not make {claim['total']}")
    return errors


CLAIMS = {"tally": tally_problems}


def check(directory: Path, main: str = "main", report_commit: str | None = None) -> tuple[str, list[str]]:
    """(the gated head, the errors) of the batch at `directory`, from its evidence.toml and evidence; the
    scope is the batch's from its merge base with `main`, and with `report_commit` every file read must be
    committed there."""
    with recording() as opened:
        head, errors = _check(directory, main)
    return head, errors + committed_problems(opened, report_commit)


def _check(directory: Path, main: str) -> tuple[str, list[str]]:
    config = evidence_config.read(directory)
    folder = evidence_config.evidence_dir(directory, config)

    def read(section):
        return load(evidence_config.inside(folder, config[section]["file"]))

    saved = read("scope")
    errors = scope_problems(saved)
    errors += scope_history_problems(saved, main)
    head = saved.get("head") if isinstance(saved, dict) else None
    base = saved.get("base") if isinstance(saved, dict) else None  # the merge base, or the check above fails
    errors += gate_record_problems(head, read("gate"))
    mutants = read("mutants")
    errors += mutant_problems(mutants, config["mutants"].get("min", 3))
    errors += mutant_source_problems(mutants, head) if isinstance(head, str) and SHA.fullmatch(head) else []
    product = sorted(c["path"] for c in saved.get("changes") or () if isinstance(c, dict)
                     and str(c.get("path")).startswith(("ve/", "lean/")))
    if "ab" in config:
        errors += ab.problems(read("ab"), head, set(config["ab"].get("corpora", ())) | REQUIRED_CORPORA, base)
    elif product:
        errors.append(f"the batch changes {product[0]} (and {len(product) - 1} more ve/ or lean/ paths) "
                      "but its evidence.toml names no [ab]")
    if "latency" in config:
        errors += evidence_latency.problems(read("latency"), head, config["latency"]["workloads"],
                                            config["latency"].get("allowance", evidence_latency.ALLOWANCE), base)
    if "fuzz_ab" in config:
        evidence = read("fuzz_ab")
        errors += fuzz_ab.problems(evidence, head, base)
        if isinstance(evidence, dict) and evidence.get("rules") != config["fuzz_ab"].get("explained", []):
            errors.append("fuzz A/B ran with other rules than evidence.toml names")
    evidence = report.Evidence(folder)
    if "report" in config:
        target = evidence_config.inside(directory, config["report"]["file"])
        rendered = report.render(folder, config["report"]["lines"])
        if report.block(read_bytes(target).decode(), config["report"]["marker"]) != rendered:
            errors.append(f"the {config['report']['marker']} block of {config['report']['file']} is not the "
                          "rendering of the evidence (python -m tools.evidence report)")
    for index, claim in enumerate(config.get("claims", [])):
        kind = claim.get("kind") if isinstance(claim, dict) else None
        errors += CLAIMS[kind](claim, evidence) if kind in CLAIMS else [f"claim {index} has no known kind"]
    return head, errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", type=Path, metavar="DIR", help="the batch directory holding evidence.toml")
    parser.add_argument("head", nargs="?")
    parser.add_argument("gate", nargs="?", type=Path)
    parser.add_argument("comparison", nargs="?", type=Path)
    parser.add_argument("latency", nargs="?", type=Path)
    parser.add_argument("--report-commit", help="a later commit that may change only --report-dir (with --check: "
                        "every evidence file read is committed there)")
    parser.add_argument("--main", default="main", help="with --check: the branch the batch merges into, whose "
                        "merge base with the scope's head the scope must start from (default main)")
    parser.add_argument("--report-dir", help="the batch's report directory, relative to the repository root "
                        "(with --check: the batch directory)")
    args = parser.parse_args(argv)
    positional = [args.head, args.gate, args.comparison, args.latency]
    if args.check is not None:
        if any(positional) or args.report_dir is not None:
            parser.error("--check takes the batch directory alone (and --report-commit)")
        args.report_dir = (args.check.resolve().relative_to(ROOT).as_posix() if args.report_commit else None)
    elif not all(positional):
        parser.error("give HEAD GATE COMPARISON LATENCY, or --check DIR")
    if (args.report_commit is None) != (args.report_dir is None):
        parser.error("--report-commit and --report-dir go together")
    try:
        if args.check is not None:
            args.head, errors = check(args.check, args.main, args.report_commit)
        else:
            values = [load(p) for p in (args.gate, args.comparison, args.latency)]
            errors = problems(args.head, *values)
        if args.report_commit is not None:
            errors += outside_report(changed_since(args.head, args.report_commit), args.report_dir)
    except (OSError, ValueError, TypeError, KeyError, subprocess.CalledProcessError) as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(errors))
        return 1
    later = f"; report commit {args.report_commit} changes only {args.report_dir}" if args.report_commit else ""
    print(f"batch evidence PASS on {args.head}{later}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
