#!/usr/bin/env python3
"""Select against the branch's last passing tree, not against main (test-speed plan, batch B3).

A fixer, a recheck or a repeat verify of a branch today selects the tests that `merge-base(HEAD, main)..HEAD`
can affect (tools/select_tests.py `--base`). Once a full gate has passed on a commit P of the branch, the
tests that only main..P could affect passed there, so the tests P..HEAD can affect are enough. This module
gives callers that base:

    uv run python tools/since_pass.py base --records <gate-records.jsonl>

prints the commit to pass as `select_tests.py --base`: the branch's last passing commit P when the rule
below allows it and the rule is ACTIVE, and otherwise `git merge-base HEAD <main>`, today's base. So the
selection never shrinks before the rule is trusted.

The rule (`choose`). A pass is a `gate` row of the records file (`pass_row`): a full gate that passed, or a
rerun of its failed tests that passed (standing ruling R13), on a clean worktree at a commit whose tree the
row names. P is the pass closest to HEAD among those whose commit exists with that tree, is an ancestor of
HEAD and descends from the merge base (the branch's own history since it left main). A run falls back to
today's base, "forced", when P..HEAD holds more than MAX_STEPS first-parent commits or P passed more than
MAX_AGE ago (or in the future).

Shadow mode. The rule is active only when the committed shadow evidence (EVIDENCE) passes `check`: rows from
at least ACTIVATION_ITEMS items in which the rule chose P and selected less than everything, each written
beside a full gate whose suite completed, and no row where the full gate failed outside the rule's
selection. `after-gate` writes those rows: the chain runs it after every gate of a worktree,

    uv run python tools/since_pass.py after-gate --records R --shadow S --item LABEL --result gate-result.json

and it (1) compares the gate's failures with the selection the rule would have made (and with today's), as
a row of S, then (2) appends the gate's pass, if it passed, to R. `check` validates an evidence file and
recomputes every row's misses from its saved lists; it never trusts a saved verdict. An item is a branch: the
chain's labels for one item's later loops (`rd-9`, `rd-9-c140740`) count once.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import fcntl
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
# A fixer's run, a recheck or a repeat verify is a step; a step is a first-parent commit since the pass.
MAX_STEPS = 5
MAX_AGE = timedelta(hours=24)
ACTIVATION_ITEMS = 10
EVIDENCE = ROOT / "docs/test-speed-b3/evidence/shadow.jsonl"
SHADOW_FORMAT = "ve-since-pass-shadow@1"
MAIN = "main"
# The (status, mode) pairs of a gate record that are a pass: a full gate, or its failed tests rerun (R13).
PASSES = {("passed", "full"), ("rerun-passed", "rerun-failed")}
# Failures of gate checks a selected run never makes (the collection against the base, the source identity):
# no selection can catch them, so they are listed with a row but are not a miss of the rule.
GATE_ONLY = frozenset({"coverage", "source identity"})
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
TIME = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ")


class RecordError(ValueError):
    """A record or evidence row that is not what it claims to be."""


# --- git ------------------------------------------------------------------------------------------------

def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    run = subprocess.run(["git", "--no-optional-locks", *args], cwd=root, text=True, capture_output=True)
    if check and run.returncode:
        raise RecordError(f"git {' '.join(args)}: exit {run.returncode}: {run.stderr.strip()}")
    return run


def rev(root: Path, name: str) -> str | None:
    found = git(root, "rev-parse", "--verify", "--quiet", "--end-of-options", name, check=False)
    return found.stdout.strip() if found.returncode == 0 else None


def is_ancestor(root: Path, older: str, newer: str) -> bool:
    return git(root, "merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def first_parent_steps(root: Path, older: str, newer: str) -> int:
    return int(git(root, "rev-list", "--count", "--first-parent", f"{older}..{newer}").stdout)


def distance(root: Path, older: str, newer: str) -> int:
    return int(git(root, "rev-list", "--count", f"{older}..{newer}").stdout)


def merge_base(root: Path, head: str, main: str) -> str:
    return git(root, "merge-base", head, main).stdout.strip()


# --- the records ----------------------------------------------------------------------------------------

def parse_time(text) -> datetime:
    if type(text) is not str or not TIME.fullmatch(text):
        raise RecordError(f"time {text!r} is not YYYY-MM-DDTHH:MM:SSZ")
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def format_time(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def string(row: dict, key: str, pattern: re.Pattern | None = None) -> str:
    value = row.get(key)
    if type(value) is not str or not value or (pattern is not None and not pattern.fullmatch(value)):
        raise RecordError(f"{key} is {value!r}")
    return value


@dataclass(frozen=True)
class Pass:
    """A gate that passed, as a `gate` row of the records file."""
    item: str
    branch: str
    commit: str
    tree: str
    status: str
    mode: str
    time: datetime
    result_sha256: str

    def row(self) -> dict:
        return {"gate": self.item, "branch": self.branch, "commit": self.commit, "tree": self.tree,
                "status": self.status, "mode": self.mode, "t": format_time(self.time),
                "result_sha256": self.result_sha256}


PASS_KEYS = frozenset(Pass("", "", "", "", "", "", datetime.now(timezone.utc), "").row())


def pass_row(row) -> Pass:
    """The pass a `gate` row records; RecordError unless every field has its type and the pair is a pass."""
    if not isinstance(row, dict) or set(row) != PASS_KEYS:
        raise RecordError(f"a gate row has exactly the keys {sorted(PASS_KEYS)}")
    found = Pass(string(row, "gate"), string(row, "branch"), string(row, "commit", HEX40),
                 string(row, "tree", HEX40), string(row, "status"), string(row, "mode"), parse_time(row["t"]),
                 string(row, "result_sha256", HEX64))
    if (found.status, found.mode) not in PASSES:
        raise RecordError(f"status {found.status!r} in mode {found.mode!r} is not a pass")
    return found


def read_passes(path: Path) -> tuple[list[Pass], list[str]]:
    """(the passes the `gate` rows of a records file name, a note for each `gate` row that is not one). Rows
    of other kinds (train, loop, nightly) are skipped; a missing file has no pass."""
    passes, malformed = [], []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return [], []
    for number, line in enumerate(lines, 1):
        try:
            row = json.loads(line)
        except ValueError:
            continue  # not ours to judge: another writer's line
        if not isinstance(row, dict) or "gate" not in row:
            continue
        try:
            passes.append(pass_row(row))
        except RecordError as exc:
            malformed.append(f"{path}:{number}: {exc}")
    return passes, malformed


# --- the rule -------------------------------------------------------------------------------------------

def choose(root: Path, passes: list[Pass], *, now: datetime, head: str = "HEAD", main: str = MAIN) -> dict:
    """The rule's base for `head`: {"rule": "since-pass", "base": P, ...} or {"rule": "merge-base", "base":
    today's base, "reason": why}. `forced` names the bound that sent an eligible pass back to today's base."""
    head = rev(root, f"{head}^{{commit}}")
    if head is None:
        raise RecordError("no HEAD commit")
    base = merge_base(root, head, main)
    decision = {"rule": "merge-base", "base": base, "merge_base": base, "head": head, "pass": None,
                "steps": None, "age_hours": None, "forced": None}
    eligible = []
    for found in passes:
        if rev(root, f"{found.commit}^{{commit}}") != found.commit \
                or rev(root, f"{found.commit}^{{tree}}") != found.tree:
            continue  # a commit not here, or a row whose tree is not its commit's
        if is_ancestor(root, found.commit, head) and is_ancestor(root, base, found.commit):
            eligible.append(found)
    if not eligible:
        return {**decision, "reason": "no passing tree in the branch's history since the merge base"}
    chosen = min(eligible, key=lambda found: (distance(root, found.commit, head), -found.time.timestamp()))
    steps = first_parent_steps(root, chosen.commit, head)
    age = now - chosen.time
    decision.update({"pass": {"item": chosen.item, "commit": chosen.commit, "tree": chosen.tree,
                              "status": chosen.status, "t": format_time(chosen.time)},
                     "steps": steps, "age_hours": round(age.total_seconds() / 3600, 3)})
    if steps > MAX_STEPS:
        return {**decision, "forced": "steps",
                "reason": f"{steps} first-parent commits since the pass {chosen.commit[:12]} (at most {MAX_STEPS})"}
    if age > MAX_AGE or age < timedelta(0):
        return {**decision, "forced": "age",
                "reason": f"the pass {chosen.commit[:12]} is {decision['age_hours']} h old (0 to "
                          f"{MAX_AGE.total_seconds() / 3600:g} h)"}
    return {**decision, "rule": "since-pass", "base": chosen.commit,
            "reason": f"the pass {chosen.commit[:12]} of {chosen.item}, {steps} steps back"}


# --- shadow rows ----------------------------------------------------------------------------------------

def covered(failure: dict, plan: dict | None, attributed: bool) -> bool | None:
    """Whether a selected run of `plan` would have run what the gate failure is in: True, False, or None for a
    gate-only check (GATE_ONLY). `attributed`: the gate also names a failed test, so a bare `pytest command`
    failure is that test's exit status."""
    stage, nodeid = failure["stage"], failure.get("nodeid")
    if stage in GATE_ONLY and nodeid is None:
        return None
    if plan is None:
        return False
    if plan["full"]:
        return True
    if nodeid is not None:
        return nodeid.split("::", 1)[0] in plan["selected"]
    return stage == "pytest command" and attributed


def outside(failures: list[dict], plan: dict | None) -> list[dict]:
    """The failures a selected run of `plan` would not have run."""
    attributed = any(failure.get("nodeid") is not None for failure in failures)
    return [failure for failure in failures if covered(failure, plan, attributed) is False]


def gate_only(failures: list[dict]) -> list[dict]:
    attributed = any(failure.get("nodeid") is not None for failure in failures)
    return [failure for failure in failures if covered(failure, None, attributed) is None]


def failure_rows(result: dict) -> list[dict]:
    """The gate's failures as {stage, nodeid?}: what a selection is compared on."""
    rows = []
    for failure in result.get("failures") or []:
        if not isinstance(failure, dict) or type(failure.get("stage")) is not str:
            raise RecordError(f"gate failure {failure!r} has no stage")
        nodeid = failure.get("nodeid")
        if nodeid is not None and type(nodeid) is not str:
            raise RecordError(f"gate failure {failure!r} has a nodeid that is not a string")
        rows.append({"stage": failure["stage"], **({"nodeid": nodeid} if nodeid is not None else {})})
    return rows


def plan_summary(plan: dict) -> dict:
    return {"selected": sorted(plan["selected"]), "full": plan["full"], "full_reasons": list(plan["full_reasons"]),
            "map": plan["map"]["commit"] if plan["map"] else None}


def plan_between(base: str, head: str) -> dict:
    """tools/select_tests.py's plan for base..head (on this checkout, at `head`), as `--base` makes it."""
    sys.path.insert(0, str(ROOT / "tools"))
    import select_tests
    paths = select_tests.git_lines("diff", "--no-renames", "--name-only", f"{base}...{head}")
    return select_tests.select(paths, base=base, after=head, coverage="auto")


def counted(row: dict) -> bool:
    """Whether a row is evidence for the rule: it chose a pass and selected less than everything, beside a full
    gate whose suite completed, on a named branch (the item it counts for)."""
    plan = row["since_pass"]
    return row["decision"]["rule"] == "since-pass" and plan is not None and not plan["full"] \
        and row["branch"] != "HEAD"


def shadow_row(root: Path, result: dict, passes: list[Pass], *, item: str, now: datetime, main: str = MAIN,
               planner=plan_between) -> dict:
    """The shadow row of a completed full gate of HEAD (`result`, tools/gate.py's record)."""
    decision = choose(root, passes, now=now, main=main)
    failures = failure_rows(result)
    since = merge = units = None
    if decision["rule"] == "since-pass":
        plan = planner(decision["base"], decision["head"])
        since, units = plan_summary(plan), plan["full_count"]
        merge = plan_summary(planner(decision["merge_base"], decision["head"]))
    row = {"format": SHADOW_FORMAT, "item": item, "branch": current_branch(root), "commit": decision["head"],
           "tree": rev(root, "HEAD^{tree}"), "t": format_time(now),
           "gate": {"status": result.get("status"), "mode": result.get("mode"), "stages": list(result["stages"]),
                    "result_sha256": result_digest(result), "failures": failures},
           "decision": {key: decision[key] for key in ("rule", "base", "merge_base", "pass", "steps", "age_hours",
                                                        "forced", "reason")},
           "units": units, "since_pass": since, "merge_base_plan": merge}
    row["outside"] = {"since_pass": outside(failures, since) if since else [],
                      "merge_base": outside(failures, merge) if merge else [], "gate_only": gate_only(failures)}
    row["counted"] = counted(row)
    return row


def current_branch(root: Path) -> str:
    return git(root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def result_digest(result: dict) -> str:
    return hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()


def bound_result(root: Path, result) -> str | None:
    """Why `result` is not a clean gate record of this HEAD, or None."""
    if not isinstance(result, dict):
        return "the gate record is not an object"
    if result.get("commit_sha") != rev(root, "HEAD^{commit}") or result.get("tree_sha") != rev(root, "HEAD^{tree}"):
        return "the gate record is not of HEAD's commit and tree"
    if result.get("dirty") is not False:
        return "the gate did not run on a clean worktree"
    if not isinstance(result.get("stages"), list):
        return "the gate record has no stage list"
    return None


def after_gate(root: Path, result, *, records: Path, shadow: Path | None, item: str, now: datetime,
               main: str = MAIN, planner=plan_between) -> list[str]:
    """What the chain runs after a gate of HEAD: the shadow row of a completed full gate (against the passes
    recorded before it), then this gate's pass. Returns what it did, one line each."""
    refusal = bound_result(root, result)
    if refusal is not None:
        raise RecordError(refusal)
    done = []
    passes, malformed = read_passes(records)
    done += [f"ignored malformed record {note}" for note in malformed]
    head = rev(root, "HEAD^{commit}")
    if shadow is not None and result.get("mode") == "full" and "pytest" in result["stages"]:
        if any(row.get("item") == item and row.get("commit") == head for row in read_jsonl(shadow)):
            done.append(f"shadow row of {item} at {head[:12]} already written")
        else:
            row = shadow_row(root, result, passes, item=item, now=now, main=main, planner=planner)
            append(shadow, row)
            done.append(f"shadow row: rule {row['decision']['rule']} ({row['decision']['reason']}); "
                        f"outside the rule's selection: {len(row['outside']['since_pass'])}")
    elif shadow is not None:
        done.append("no shadow row: not a full gate whose suite completed")
    pair = (result.get("status"), result.get("mode"))
    if pair in PASSES:
        if any(found.commit == head and (found.status, found.mode) == pair for found in passes):
            done.append(f"pass of {head[:12]} already recorded")
        else:
            found = Pass(item, current_branch(root), head, rev(root, "HEAD^{tree}"), pair[0], pair[1], now,
                         result_digest(result))
            append(records, pass_row(found.row()).row())
            done.append(f"recorded the pass of {head[:12]} ({pair[0]})")
    else:
        done.append(f"no pass recorded: status {pair[0]!r} in mode {pair[1]!r}")
    return done


def read_jsonl(path: Path) -> list[dict]:
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return []
    rows = []
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def append(path: Path, row: dict) -> None:
    """One line, in one write under an exclusive lock to a file opened for appending: other chains append to the
    same file, and a shadow row is longer than the shell's atomic line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        written = os.write(descriptor, data)
        if written != len(data):
            raise RecordError(f"wrote {written} of {len(data)} bytes to {path}")
    finally:
        os.close(descriptor)


# --- the evidence check ---------------------------------------------------------------------------------

def check_plan(plan, where: str) -> dict | None:
    if plan is None:
        return None
    if not isinstance(plan, dict) or set(plan) != {"selected", "full", "full_reasons", "map"}:
        raise RecordError(f"{where}: a plan has exactly selected, full, full_reasons and map")
    selected = plan["selected"]
    if not isinstance(selected, list) or not all(type(unit) is str and unit for unit in selected) \
            or selected != sorted(set(selected)):
        raise RecordError(f"{where}: selected is not a sorted list of distinct unit names")
    if type(plan["full"]) is not bool or not isinstance(plan["full_reasons"], list) \
            or not all(type(reason) is str for reason in plan["full_reasons"]) \
            or plan["full"] != bool(plan["full_reasons"]):
        raise RecordError(f"{where}: full must be a bool that holds exactly when full_reasons is not empty")
    if plan["map"] is not None and (type(plan["map"]) is not str or not HEX40.fullmatch(plan["map"])):
        raise RecordError(f"{where}: map is {plan['map']!r}")
    return plan


def check_row(root: Path, row, where: str) -> dict:
    """Validate one shadow row against the repository and recompute its verdict; returns the row."""
    keys = {"format", "item", "branch", "commit", "tree", "t", "gate", "decision", "units", "since_pass",
            "merge_base_plan", "outside", "counted"}
    if not isinstance(row, dict) or set(row) != keys or row["format"] != SHADOW_FORMAT:
        raise RecordError(f"{where}: not a {SHADOW_FORMAT} row with exactly the keys {sorted(keys)}")
    string(row, "item"), string(row, "branch")
    commit, tree = string(row, "commit", HEX40), string(row, "tree", HEX40)
    when = parse_time(row["t"])
    if rev(root, f"{commit}^{{commit}}") != commit or rev(root, f"{commit}^{{tree}}") != tree:
        raise RecordError(f"{where}: commit {commit} with tree {tree} is not in this repository")
    gate = row["gate"]
    if not isinstance(gate, dict) or set(gate) != {"status", "mode", "stages", "result_sha256", "failures"}:
        raise RecordError(f"{where}: gate has exactly status, mode, stages, result_sha256 and failures")
    if gate["mode"] != "full" or gate["status"] not in ("passed", "failed") \
            or not isinstance(gate["stages"], list) or "pytest" not in gate["stages"]:
        raise RecordError(f"{where}: not a full gate whose suite completed")
    string(gate, "result_sha256", HEX64)
    failures = failure_rows(gate)
    if failures != gate["failures"]:
        raise RecordError(f"{where}: a failure has other fields than stage and nodeid")
    if (gate["status"] == "passed") != (not failures):
        raise RecordError(f"{where}: status {gate['status']!r} with {len(failures)} failures")
    decision = row["decision"]
    if not isinstance(decision, dict) or set(decision) != {"rule", "base", "merge_base", "pass", "steps",
                                                           "age_hours", "forced", "reason"}:
        raise RecordError(f"{where}: decision has the wrong keys")
    string(decision, "reason")
    base = string(decision, "merge_base", HEX40)
    if not is_ancestor(root, base, commit):
        raise RecordError(f"{where}: merge base {base} is not an ancestor of {commit}")
    since, merge = check_plan(row["since_pass"], where), check_plan(row["merge_base_plan"], where)
    if decision["rule"] == "since-pass":
        found = decision["pass"]
        if not isinstance(found, dict) or set(found) != {"item", "commit", "tree", "status", "t"}:
            raise RecordError(f"{where}: since-pass decision without its pass")
        anchor = string(found, "commit", HEX40)
        string(found, "item")
        if decision["base"] != anchor or rev(root, f"{anchor}^{{tree}}") != string(found, "tree", HEX40):
            raise RecordError(f"{where}: the base is not the pass's commit and tree")
        if found["status"] not in {status for status, _ in PASSES}:
            raise RecordError(f"{where}: the pass's status is {found['status']!r}")
        if not (is_ancestor(root, anchor, commit) and is_ancestor(root, base, anchor)):
            raise RecordError(f"{where}: the pass is not in the branch's history since the merge base")
        steps = first_parent_steps(root, anchor, commit)
        if decision["steps"] != steps or type(decision["steps"]) is not int or steps > MAX_STEPS:
            raise RecordError(f"{where}: steps {decision['steps']!r}, recomputed {steps} (at most {MAX_STEPS})")
        age = when - parse_time(found["t"])
        if not timedelta(0) <= age <= MAX_AGE or decision["forced"] is not None:
            raise RecordError(f"{where}: the pass is {age} old at the row's time, or the rule was forced")
        if since is None or merge is None or type(row["units"]) is not int or row["units"] < 1:
            raise RecordError(f"{where}: a since-pass row needs both plans and the unit count")
    elif decision["rule"] == "merge-base":
        if decision["base"] != base or since is not None or merge is not None:
            raise RecordError(f"{where}: a merge-base row has today's base and no plans")
    else:
        raise RecordError(f"{where}: rule {decision['rule']!r}")
    recomputed = {"since_pass": outside(failures, since) if since else [],
                  "merge_base": outside(failures, merge) if merge else [], "gate_only": gate_only(failures)}
    if row["outside"] != recomputed or row["counted"] is not counted(row):
        raise RecordError(f"{where}: the saved outside lists or counted flag differ from the recomputed ones")
    return row


def check(root: Path, path: Path) -> dict:
    """The evidence verdict: {"rows", "items", "misses", "active"}; RecordError when a row is malformed or
    unbound. `items` are the items with a counted row; a miss is a counted or uncounted since-pass row with a
    failure outside the rule's selection."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        lines = []
    rows, seen = [], set()
    for number, line in enumerate(lines, 1):
        where = f"{path.name}:{number}"
        try:
            row = json.loads(line)
        except ValueError as exc:
            raise RecordError(f"{where}: not JSON: {exc}") from exc
        row = check_row(root, row, where)
        key = (row["item"], row["commit"])
        if key in seen:
            raise RecordError(f"{where}: a second row for {row['item']} at {row['commit']}")
        seen.add(key)
        rows.append(row)
    misses = [{"item": row["item"], "commit": row["commit"], "outside": row["outside"]["since_pass"]}
              for row in rows if row["outside"]["since_pass"]]
    items = sorted({row["branch"] for row in rows if row["counted"]})  # an item is its branch, whatever its labels
    return {"rows": len(rows), "items": items, "misses": misses,
            "active": len(items) >= ACTIVATION_ITEMS and not misses}


def activation(root: Path, path: Path) -> tuple[bool, str]:
    try:
        verdict = check(root, path)
    except RecordError as exc:
        return False, f"the shadow evidence is invalid: {exc}"
    if verdict["misses"]:
        return False, f"the shadow evidence has {len(verdict['misses'])} rows with failures outside the selection"
    return verdict["active"], f"{len(verdict['items'])}/{ACTIVATION_ITEMS} items in the shadow evidence"


# --- the command line -----------------------------------------------------------------------------------

def main(argv: list[str] | None = None, *, root: Path = ROOT, now: datetime | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    base = commands.add_parser("base", help="print the commit to pass as select_tests.py --base")
    base.add_argument("--records", type=Path, required=True, help="the gate records (JSON lines)")
    base.add_argument("--main", default=MAIN, help=f"the branch the merge base is taken with (default {MAIN})")
    base.add_argument("--evidence", type=Path, default=EVIDENCE)
    base.add_argument("--json", action="store_true", help="print the decision and the activation instead")
    after = commands.add_parser("after-gate", help="write the shadow row of a gate of HEAD, then record its pass")
    after.add_argument("--records", type=Path, required=True)
    after.add_argument("--shadow", type=Path, help="the shadow rows (JSON lines); none: only the pass is recorded")
    after.add_argument("--item", required=True)
    after.add_argument("--result", type=Path, required=True, help="the gate's record (gate-result.json)")
    after.add_argument("--main", default=MAIN)
    checked = commands.add_parser("check", help="validate shadow evidence and say whether the rule is active")
    checked.add_argument("--evidence", type=Path, default=EVIDENCE)
    args = parser.parse_args(argv)
    now = now or datetime.now(timezone.utc)
    try:
        if args.command == "base":
            passes, malformed = read_passes(args.records)
            decision = choose(root, passes, now=now, main=args.main)
            active, why = activation(root, args.evidence)
            chosen = decision["base"] if active and decision["rule"] == "since-pass" else decision["merge_base"]
            for note in malformed:
                print(f"since_pass: ignored malformed record {note}", file=sys.stderr)
            if args.json:
                print(json.dumps({"base": chosen, "active": active, "activation": why, "decision": decision},
                                 indent=2))
                return 0
            print(f"since_pass: rule {decision['rule']}: {decision['reason']}; "
                  f"{'active' if active else 'shadow only'} ({why}); base {chosen[:12]}", file=sys.stderr)
            print(chosen)
            return 0
        if args.command == "after-gate":
            try:
                result = json.loads(args.result.read_text())
            except (OSError, ValueError) as exc:
                raise RecordError(f"no gate record at {args.result}: {exc}") from exc
            for line in after_gate(root, result, records=args.records, shadow=args.shadow, item=args.item,
                                   now=now, main=args.main):
                print(f"since_pass: {line}")
            return 0
        verdict = check(root, args.evidence)
        print(json.dumps(verdict, indent=2))
        return 1 if verdict["misses"] else 0
    except RecordError as exc:
        print(f"since_pass: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
