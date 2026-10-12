"""Check that a batch's saved gate, corpus comparison and latency evidence cover HEAD.

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
import json
import re
import subprocess
from pathlib import Path

REQUIRED_STAGES = ("toolchains", "lean_build", "lean_audit", "rust_build", "cargo_test", "pytest")
REQUIRED_CORPORA = {"probe", "conformance", "readings", "pilots", "discourse", "rights", "quantity"}


def problems(head: str, gate: dict, comparison: dict, latency: dict) -> list[str]:
    errors = []
    if gate.get("commit_sha") != head or gate.get("dirty") is not False:
        errors.append("full gate did not run on a clean HEAD")
    if gate.get("status") != "passed" or gate.get("stages") != list(REQUIRED_STAGES):
        errors.append("full gate is incomplete or failed")
    counts = gate.get("counts")
    if not isinstance(counts, dict) or not all(type(counts.get(key)) is int and counts[key] > 0
                                                for key in ("passed", "rust_passed")):
        errors.append("full gate has no passing Python and Rust tests")
    if comparison.get("head_commit") != head:
        errors.append("corpus comparison did not run on HEAD")
    if comparison.get("unlisted") != 0 or comparison.get("unavailable_both") != {}:
        errors.append("corpus comparison has an unlisted or unavailable result")
    records = comparison.get("records")
    if not isinstance(records, dict) or not REQUIRED_CORPORA <= {k.split("/", 1)[0] for k, v in records.items()
                                                                 if type(v) is int and v > 0}:
        errors.append("corpus comparison omitted a required corpus")
    if latency.get("head_commit") != head or latency.get("pass") is not True:
        errors.append("latency budget was not measured and passed on HEAD")
    samples = latency.get("samples")
    if not isinstance(samples, dict) or not samples or not all(
        isinstance(row, dict) and type(row.get("base_cpu_ms")) in (int, float)
        and type(row.get("head_cpu_ms")) in (int, float) and row["base_cpu_ms"] > 0
        and 0 <= row["head_cpu_ms"] <= 1.2 * row["base_cpu_ms"]
        for row in samples.values()
    ):
        errors.append("latency evidence is empty, malformed or above the 20% Lean CPU budget")
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


SCOPE = ("base", "head", "commits", "files")
FULL_ID = re.compile(r"[0-9a-f]{40}")


def _git_out(cwd: Path | None, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "--no-optional-locks", "-c", "core.quotePath=false", *args], cwd=cwd,
                          capture_output=True, text=True)


def git_scope(base: str, head: str, cwd: Path | None = None) -> dict:
    """A batch's scope as git records it: its commits `base..head` without merges (newest first, each
    `{"hash", "subject"}`) and the paths it changes (sorted; renames as delete and add). The one
    writer and the one checker (`scope_problems`) of every saved scope."""
    log = _git_out(cwd, "log", "--no-merges", "-z", "--format=%H %s", f"{base}..{head}")
    if log.returncode:
        raise ValueError(f"git log {base}..{head}: {log.stderr.strip()}")
    commits = [dict(zip(("hash", "subject"), entry.split(" ", 1))) for entry in log.stdout.split("\0") if entry]
    return {"base": base, "head": head, "commits": commits, "files": sorted(changed_since(base, head, cwd))}


def scope_problems(scope: object, cwd: Path | None = None, main: str = "main") -> list[str]:
    """Why a saved scope is not the batch's: exactly the fields `SCOPE`; `base` and `head` full
    commit ids; `base` the merge base of `head` and `main` (once `head` is merged into `main`, only an
    ancestor of it); and `commits` and `files` exactly `git_scope(base, head)`. A dropped, added,
    reordered or edited commit or path is a problem, and so is a malformed scope: never a pass."""
    if not isinstance(scope, dict) or set(scope) != set(SCOPE):
        return [f"the scope holds exactly {', '.join(SCOPE)}"]
    base, head = scope["base"], scope["head"]
    if not all(isinstance(rev, str) and FULL_ID.fullmatch(rev) for rev in (base, head)):
        return ["the scope's base and head are full commit ids"]
    if _git_out(cwd, "merge-base", "--is-ancestor", head, main).returncode == 0:
        if _git_out(cwd, "merge-base", "--is-ancestor", base, head).returncode != 0:
            return [f"the scope's base {base[:12]} is not an ancestor of its head {head[:12]}"]
    else:
        merged = _git_out(cwd, "merge-base", head, main)
        if merged.returncode or merged.stdout.strip() != base:
            return [f"the scope's base {base[:12]} is not the merge base of its head {head[:12]} and {main} "
                    f"({merged.stdout.strip()[:12] or merged.stderr.strip()})"]
    try:
        actual = git_scope(base, head, cwd)
    except (ValueError, subprocess.CalledProcessError) as exc:
        return [f"the scope's commits cannot be listed: {exc}"]
    return [f"the scope's {field} are not git's {base[:12]}..{head[:12]} ({len(actual[field])} there)"
            for field in ("commits", "files") if scope[field] != actual[field]]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("head")
    parser.add_argument("gate", type=Path)
    parser.add_argument("comparison", type=Path)
    parser.add_argument("latency", type=Path)
    parser.add_argument("--report-commit", help="a later commit that may change only --report-dir")
    parser.add_argument("--report-dir", help="the batch's report directory, relative to the repository root")
    args = parser.parse_args()
    if (args.report_commit is None) != (args.report_dir is None):
        parser.error("--report-commit and --report-dir go together")
    try:
        values = [json.loads(p.read_text()) for p in (args.gate, args.comparison, args.latency)]
        errors = problems(args.head, *values)
        if args.report_commit is not None:
            errors += outside_report(changed_since(args.head, args.report_commit), args.report_dir)
    except (OSError, ValueError, TypeError, subprocess.CalledProcessError) as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(errors))
        return 1
    later = f"; report commit {args.report_commit} changes only {args.report_dir}" if args.report_commit else ""
    print(f"batch evidence PASS on {args.head}{later}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
