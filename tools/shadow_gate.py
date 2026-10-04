"""Stage 3 shadow days, the count and Gate 3 (docs/spec/mig3.md 2.10 to 2.13, 3.1, 4.3, 9).

Usage::

    tools/shadow_gate.py day DATE  [--runs DIR]   # write the ledger entry of a final day
    tools/shadow_gate.py gate DATE [--runs DIR]   # the count, the gate's sentence and the report
    tools/shadow_gate.py --check                  # the committed files are well formed

``--runs`` is the directory that holds the run directories (kept outside the
repository; default ``$VE_SHADOW_RUNS`` or ``~/ve-shadow-runs``).  ``--root`` names
the repository and ``--main`` its main branch; ``--now`` fixes the clock (tests).

Exit status: 0 the day is clean, the gate is met, ``--check`` found nothing;
1 the day is not clean, the gate is not met; 2 the day is not final, or a file
is malformed or a ledger entry does not follow from its rows.

Additions to the specification's ledger entry, needed to judge it from the
committed files alone: ``day``, ``nightly_commit``, ``reasons`` (3.1), each run
row's ``nightly`` flag and ``problems``, ``nightly_ops`` (the sums over the
nightly, for coverage condition 2), and ``findings`` (every finding key of the
day, 2.11, not only the first 20 records of each group).
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import shadow_run, shadow_surface  # noqa: E402
from ve.backends.dispatch import (DISPATCH_NAMES, ZERO_TOLERANCE, wording_entry_problem)  # noqa: E402

SHADOW = "conformance/shadow"
CORPUS_IDS = ("suite", "baseline", "conformance", "differentials", "english", "fuzz-core", "fuzz-closure",
              "fuzz-nightly", "pilots", "assist", "validators", "webapp")
CORPUS_MEMBERS = {"id", "plan", "command", "expected_exit", "min_cases", "min_compared", "calibration", "merge"}
TRIAGE_MEMBERS = {"id", "first_day", "op", "kind", "class", "input_digest", "cause", "fix", "evidence", "note"}
CAUSES = ("python", "glue", "adapter", "spec", "rust", "harness", "operational")
RESTART_CAUSES = ("adapter", "glue", "rust")
CHANGE_MEMBERS = {"commit", "class", "reason", "files", "signed"}
FINDING_KINDS = ("divergence", "unavailable", "recorder-fault")
DAYS_NEEDED = 14
FIRST_RECORDS = 20


class Malformed(Exception):
    """A committed file is malformed: exit 2 with its line of 4.3."""


# --- the commit history --------------------------------------------------------------

class History:
    """The first-parent history of the main branch, and what each commit changes."""

    def __init__(self, root: Path, main: str = "main"):
        self.root = root
        self.commits = self._git("rev-list", "--first-parent", "--reverse", main).split()
        self.index = {commit: position for position, commit in enumerate(self.commits)}
        self.tip = self.commits[-1] if self.commits else None
        self._changed: dict[str, list[str]] = {}
        self._surfaces: dict[str, tuple] = {}

    def _git(self, *args: str, check: bool = True) -> str:
        return subprocess.run(["git", *args], cwd=self.root, check=check, capture_output=True,
                              text=True).stdout

    def resolve(self, commit: str) -> str:
        return self._git("rev-parse", commit).strip()

    def first_parent(self, commit: str) -> str | None:
        position = self.index.get(commit)
        return self.commits[position - 1] if position else None

    def changed(self, commit: str) -> list[str]:
        if commit not in self._changed:
            parent = self.first_parent(commit)
            if parent is None:
                names = self._git("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit)
            else:
                names = self._git("diff", "--name-only", parent, commit)
            self._changed[commit] = sorted(names.split())
        return self._changed[commit]

    def file(self, commit: str, path: str) -> str | None:
        completed = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=self.root, capture_output=True,
                                   text=True)
        return completed.stdout if completed.returncode == 0 else None

    def surface(self, commit: str) -> tuple:
        """The candidate surface at `commit`'s first parent (2.12)."""
        base = self.first_parent(commit) or commit
        if base not in self._surfaces:
            sources, manifest = shadow_surface.tree_sources(base, self.root)
            self._surfaces[base] = shadow_surface.candidate_surface(sources, manifest)
        return self._surfaces[base]

    def classed_files(self, commit: str) -> list[str]:
        surface = self.surface(commit)
        return [path for path in self.changed(commit) if shadow_surface.classed(path, surface)]

    def needs_classing(self, commit: str) -> bool:
        return bool(self.classed_files(commit))

    def needs_merge_run(self, commit: str) -> bool:
        return any(not (path.startswith("docs/") or path.startswith(SHADOW + "/")) for path in self.changed(commit))

    def on_main(self, commit) -> bool:
        if type(commit) is not str or not commit or self.tip is None:
            return False
        completed = subprocess.run(["git", "merge-base", "--is-ancestor", commit, self.tip], cwd=self.root,
                                   capture_output=True)
        return completed.returncode == 0

    def between(self, after: str | None, upto: str) -> list[str]:
        """The first-parent commits after `after` (all, when None) up to and including `upto`."""
        start = -1 if after is None else self.index[after]
        return self.commits[start + 1:self.index[upto] + 1]

    def json_at(self, commit: str, path: str):
        text = self.file(commit, path)
        return None if text is None else json.loads(text)


# --- runs ----------------------------------------------------------------------------------

def load_runs(runs: Path) -> list[dict]:
    found = []
    for meta_path in sorted(Path(runs).glob("*/run.json")) if Path(runs).is_dir() else ():
        try:
            meta = json.loads(meta_path.read_text())
        except ValueError:
            continue
        if type(meta) is dict and type(meta.get("started")) is str:
            found.append({"dir": meta_path.parent, "meta": meta})
    return sorted(found, key=lambda run: (run["meta"]["started"], run["meta"].get("run", "")))


def registered(run: dict, history: History) -> bool:
    meta = run["meta"]
    return meta.get("trigger") in ("nightly", "merge") and meta.get("commit") in history.index


def day_of(meta: dict) -> str:
    return meta["started"][:10]


def end_of(day: str) -> datetime:
    return datetime.combine(date.fromisoformat(day) + timedelta(days=1), datetime.min.time(), timezone.utc)


def parse_time(text: str) -> datetime:
    return datetime.strptime(text.replace(".000000", ""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _registry(history: History, commit: str) -> list[dict]:
    return history.json_at(commit, f"{SHADOW}/corpora.json") or []


def _entry(registry: list[dict], corpus: str):
    return next((entry for entry in registry if entry.get("id") == corpus), None)


def assess(run: dict, history: History) -> dict:
    """A run's row of the ledger entry: its run.json, completeness, summed tally, file hashes."""
    meta, directory = run["meta"], run["dir"]
    commit = meta.get("commit")
    lock = history.json_at(commit, "lean/checkers.lock") if commit in history.index else None
    problems = shadow_run.run_problems(directory, _entry(_registry(history, commit), meta.get("corpus")), lock)
    files = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(Path(directory).iterdir()) if path.is_file()}
    data = shadow_run.read_run(directory)
    records = [row for rows in data["records"].values() for row in rows]
    return {"run": meta, "complete": not problems, "problems": problems, "tally": shadow_run.summed(data["tallies"]),
            "files": files, "_records": records}


def _total(rows: list[dict], name: str) -> int:
    return sum(counts.get(name, 0) for row in rows for counts in row["tally"].values())


def _sum_ops(rows: list[dict]) -> dict:
    ops: dict[str, dict] = {}
    for row in rows:
        for op, counts in row["tally"].items():
            mine = ops.setdefault(op, {})
            shadow_run._merge(mine, counts)
    return ops


def finding_key(record: dict) -> tuple | None:
    """The finding a record belongs to (2.11), or None for a record that is none."""
    kind = record["kind"]
    if kind == "divergence" and not ZERO_TOLERANCE.intersection(record["class"]):
        return None
    if kind not in FINDING_KINDS:
        return None
    return (record["op"], kind, tuple(record["class"]), record["input_digest"])


def _nightlies(runs: list[dict], history: History) -> dict[str, str]:
    """{day: n(day)} over every day with a registered nightly run."""
    nights: dict[str, str] = {}
    for run in runs:      # sorted by start: the first nightly run of a day fixes n(D)
        meta = run["meta"]
        if registered(run, history) and meta["trigger"] == "nightly":
            nights.setdefault(day_of(meta), meta["commit"])
    return nights


def evaluate_day(day: str, runs: list[dict], history: History, now: datetime) -> tuple[int, list[str], dict | None]:
    """(exit status, sentences, ledger entry or None) for `day dATE` (2.10, 3.1)."""
    mine = [run for run in runs if registered(run, history) and day_of(run["meta"]) == day]
    if now < end_of(day):
        return 2, [f"{day} is not final: the day has not ended."], None
    for run in mine:
        if not run["meta"].get("finished"):
            return 2, [f"{day} is not final: the run {run['meta'].get('run')} has not finished."], None
    nights = _nightlies(runs, history)
    nightly_commit = nights.get(day)
    rows = [assess(run, history) for run in mine]
    for row, run in zip(rows, mine):
        row["nightly"] = run["meta"]["trigger"] == "nightly" and run["meta"]["commit"] == nightly_commit
    nightly = [row for row in rows if row["nightly"]]
    registry = _registry(history, nightly_commit or history.tip)
    corpora = [entry.get("id") for entry in registry]
    reasons = []
    for corpus in corpora:
        if not any(row["complete"] and row["run"].get("corpus") == corpus for row in nightly):
            reasons.append(f"the corpus {corpus} has no complete run in the nightly")
    nightly_ops = _sum_ops(nightly)
    for op in DISPATCH_NAMES:
        if nightly_ops.get(op, {}).get("compared", 0) < 1:
            reasons.append(f"the operation {op} has no compared call in the nightly")
    merges = []
    if nightly_commit is not None:
        earlier = [d for d in nights if d < day]
        if earlier:
            after = nights[max(earlier)]
        else:
            first = next((run for run in runs if registered(run, history)), None)
            after = first["meta"]["commit"] if first else None
        if after is not None and history.index[after] > history.index[nightly_commit]:
            after = nightly_commit
        for commit in history.between(after, nightly_commit):
            if not history.needs_merge_run(commit):
                continue
            complete = next((row for row in (assess(run, history) for run in runs
                                             if registered(run, history) and run["meta"]["trigger"] == "merge"
                                             and run["meta"].get("corpus") == "suite"
                                             and run["meta"]["commit"] == commit)
                             if row["complete"]), None)
            merges.append({"commit": commit, "run": complete["run"]["run"] if complete else None})
            if complete is None:
                reasons.append(f"the commit {commit} needs a merge run and has no complete one")
    covered = not reasons
    for row in rows:
        for problem in row["problems"]:
            reasons.append(f"the run {row['run'].get('run')} is not complete: {problem}")
    zero = _total(rows, "zero_tolerance")
    failures = _total(rows, "completion_failures")
    faults = _total(rows, "recorder_faults") + sum(row["run"].get("stderr_faults") or 0 for row in rows)
    if zero:
        reasons.append(f"{zero} compared calls differ in a zero-tolerance class")
    if failures:
        reasons.append(f"{failures} calls completed in Python and got no answer from the backend")
    if faults:
        reasons.append(f"{faults} recorder faults")
    clean = covered and not reasons
    records = [record for row in rows for record in row.pop("_records")]
    groups: dict[tuple, list] = {}
    for record in records:
        groups.setdefault((record["op"], record["kind"], tuple(record["class"])), []).append(record)
    findings = Counter(key for key in map(finding_key, records) if key is not None)
    sides = {finding_key(r): r.get("sides") for r in records if r["kind"] == "unavailable"}
    entry = {"day": day, "written": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "nightly_commit": nightly_commit,
             "covered": covered, "clean": clean, "reasons": reasons, "corpora": corpora, "runs": rows,
             "ops": _sum_ops(rows), "nightly_ops": nightly_ops, "merge_commits": merges,
             "groups": [{"op": op, "kind": kind, "class": list(classes), "count": len(items),
                         "first": items[:FIRST_RECORDS]} for (op, kind, classes), items in sorted(groups.items())],
             "findings": [{"op": op, "kind": kind, "class": list(classes), "input_digest": digest,
                           "sides": sides.get((op, kind, classes, digest)), "count": count}
                          for (op, kind, classes, digest), count in sorted(findings.items(),
                                                                          key=lambda item: json.dumps(item[0]))]}
    if clean:
        sentences = [f"On {day}, every corpus ran in shadow at commit {nightly_commit}, no compared call differed "
                     "in a zero-tolerance class, and no call that Python answered got no answer from the backend."]
    else:
        sentences = [f"{day} is not a clean day: {reason}." for reason in reasons]
    return (0 if clean else 1), sentences, entry


def entry_problem(entry: dict) -> str | None:
    """The member of a ledger entry that does not follow from its own rows, or None."""
    rows = entry.get("runs")
    if type(rows) is not list or type(entry.get("corpora")) is not list:
        return "runs"
    nightly = [row for row in rows if row.get("nightly")]
    if any(row["run"].get("commit") != entry.get("nightly_commit") for row in nightly):
        return "nightly_commit"
    covered = (all(any(row["complete"] and row["run"].get("corpus") == corpus for row in nightly)
                   for corpus in entry["corpora"])
               and all(_sum_ops(nightly).get(op, {}).get("compared", 0) >= 1 for op in DISPATCH_NAMES)
               and all(merge.get("run") for merge in entry.get("merge_commits", ())))
    if covered != entry.get("covered"):
        return "covered"
    clean = (covered and all(row["complete"] for row in rows) and not _total(rows, "zero_tolerance")
             and not _total(rows, "completion_failures") and not _total(rows, "recorder_faults")
             and not any(row["run"].get("stderr_faults") for row in rows))
    if clean != entry.get("clean"):
        return "clean"
    written = entry.get("written")
    try:
        when = parse_time(written)
    except (TypeError, ValueError):
        return "written"
    if when < end_of(entry["day"]) or any(
            not row["run"].get("finished") or when < parse_time(row["run"]["finished"]) for row in rows):
        return "written"
    return None


# --- findings, restart events, the count -----------------------------------------------------

def load(root: Path, name: str):
    return json.loads((root / SHADOW / name).read_text())


def ledger(root: Path) -> dict[str, dict]:
    entries = {}
    for path in sorted((root / SHADOW / "ledger").glob("*.json")):
        entries[path.stem] = json.loads(path.read_text())
    return entries


def _fix_commit(entry: dict):
    fix = entry.get("fix")
    return fix.get("commit") if type(fix) is dict else fix


def _side_cause(entry: dict):
    """The cause of the side a `spec` finding changed to match its note, if one was."""
    fix = entry.get("fix")
    return fix.get("cause") if type(fix) is dict else None


def closed(entry: dict, history: History) -> bool:
    """Whether a triage entry has what its cause needs and its fix is on main (2.11)."""
    cause = entry.get("cause")
    if cause not in CAUSES:
        return False
    fix, evidence, note = _fix_commit(entry), entry.get("evidence"), entry.get("note")
    needs_fix = cause in ("python", "glue", "adapter", "rust", "harness")
    if needs_fix and not fix:
        return False
    if cause in ("python", "glue", "rust", "harness", "operational") and not evidence:
        return False
    if cause == "spec" and not (note and evidence):
        return False
    if cause == "spec" and fix and _side_cause(entry) not in CAUSES:
        return False
    return not fix or history.on_main(fix)


def restart_events(history: History, triage: list[dict], changes: list[dict]) -> dict[str, str]:
    """{commit: the reason of 3.1} for every restart event on the first-parent history."""
    events: dict[str, str] = {}
    by_commit = {entry.get("commit"): entry for entry in changes}
    for entry in triage:
        cause = entry.get("cause")
        if cause in RESTART_CAUSES or (cause == "spec" and _side_cause(entry) in RESTART_CAUSES):
            commit = _fix_commit(entry)
            if commit in history.index and commit not in events:
                events[commit] = f"it fixes finding {entry.get('id')} ({cause})"
    for commit in history.commits:
        entry = by_commit.get(commit)
        if entry is None or commit in events or not history.needs_classing(commit):
            continue
        restart = next((line for line in entry.get("files", ()) if line.get("class") == "restart"), None)
        if restart is not None:
            events[commit] = f"the DRI classed {restart['path']} as a restart: {restart['reason']}"
    return events


def count_on(day: str, entries: dict[str, dict], history: History, events: dict[str, str],
             changes: list[dict]) -> tuple[int, str | None, list[str], str | None]:
    """The count on `day` (2.12): (k, its first day, the unclassed commits that
    stopped it, the restart event that stopped it)."""
    classed = {entry.get("commit") for entry in changes}
    last = entries.get(day, {}).get("nightly_commit")
    k, first = 0, None
    while last is not None:
        candidate = (date.fromisoformat(day) - timedelta(days=k)).isoformat()
        entry = entries.get(candidate)
        if entry is None or not entry.get("clean") or entry.get("nightly_commit") not in history.index:
            return k, first, [], None
        window = history.between(entry["nightly_commit"], last)
        unclassed = [commit for commit in window if history.needs_classing(commit) and commit not in classed]
        restarts = [commit for commit in window if commit in events]
        if unclassed or restarts:
            return k, first, unclassed, (restarts[-1] if restarts else None)
        k, first = k + 1, candidate
    return k, first, [], None


def all_findings(entries: dict[str, dict]) -> list[dict]:
    found: dict[tuple, dict] = {}
    for day, entry in sorted(entries.items()):
        for finding in entry.get("findings", ()):
            key = (finding["op"], finding["kind"], tuple(finding["class"]), finding["input_digest"])
            found.setdefault(key, {**finding, "first_day": day})
    return list(found.values())


def triage_for(finding: dict, triage: list[dict]) -> dict | None:
    return next((entry for entry in triage
                 if (entry.get("op"), entry.get("kind"), list(entry.get("class") or ()), entry.get("input_digest"))
                 == (finding["op"], finding["kind"], finding["class"], finding["input_digest"])), None)


def evaluate_gate(day: str, root: Path, history: History) -> tuple[int, list[str]]:
    entries, triage, changes = ledger(root), load(root, "triage.json"), load(root, "changes.json")
    events = restart_events(history, triage, changes)
    k, first, unclassed, ended = count_on(day, entries, history, events, changes)
    lines = []
    if k:
        lines.append(f"The count of clean days in a row is {k}, from {first} to {day}.")
    else:
        lines.append(f"The count of clean days in a row is 0, from {day} to {day}.")
    if ended in events:
        lines.append(f"The count went back to zero at commit {ended}: {events[ended]}.")
    reasons = []
    if k < DAYS_NEEDED:
        reasons.append(f"the count is {k}, and {DAYS_NEEDED} are needed")
    findings = all_findings(entries)
    for finding in findings:
        entry = triage_for(finding, triage)
        if entry is None or not closed(entry, history):
            label = entry.get("id") if entry else f"{finding['op']}/{finding['input_digest']}"
            reasons.append(f"finding {label} is open")
    for commit in unclassed:
        reasons.append(f"commit {commit} changes a classed path and is not classed")
    if reasons:
        lines.extend(f"Gate 3 is not met on {day}: {reason}." for reason in reasons)
        status = 1
    else:
        nightly, c_first = entries[day]["nightly_commit"], entries[first]["nightly_commit"]
        lines.append(f"Gate 3 is met on {day} at commit {nightly}: the {DAYS_NEEDED} days from {first} to {day} are "
                     f"clean, no restart event is among the commits after {c_first} up to {nightly}, and every "
                     "finding is closed.")
        status = 0
    lines.extend(report(day, k, first, entries, findings, triage, changes, history, events))
    return status, lines


def report(day, k, first, entries, findings, triage, changes, history, events) -> list[str]:
    """The rows and attachments of section 9, in the sentences of 3.1."""
    days = [(date.fromisoformat(day) - timedelta(days=i)).isoformat() for i in range(max(k, 1))][::-1]
    chosen = [entries[d] for d in days if d in entries]
    rows = [row for entry in chosen for row in entry["runs"]]
    compared = _total(rows, "compared")
    failures = _total(rows, "completion_failures")
    verdicts = sum(1 for entry in chosen for group in entry["groups"]
                   if group["kind"] == "divergence" and {"verdict", "budget-outcome"} & set(group["class"])
                   for _ in range(group["count"]))
    lines = ["", f"Report for {day} ({len(chosen)} ledger entries).",
             f"Of {compared + failures} calls that Python completed, the backend completed {compared - verdicts} "
             "with the same outcome."]
    ops = _sum_ops(rows)
    for op, counts in sorted(ops.items()):
        for reason, number in sorted(counts.get("uncompared", {}).items()):
            lines.append(f"{number} calls of {op} were answered by Python alone, because the adapter does not take "
                         f"the input ({reason}). They were not compared.")
        if counts.get("lean_only"):
            lines.append(f"{counts['lean_only']} calls of {op} have no Python implementation. Lean answered them, "
                         "and nothing was compared.")
    for op, counts in sorted(ops.items()):
        for name, cell in sorted(counts.get("count_members", {}).items()):
            lines.append(f"count parity {op} {name}: equal {cell.get('equal', 0)}, different {cell.get('different', 0)}")
        for side, latency in sorted(counts.get("latency", {}).items()):
            if latency.get("count"):
                lines.append(f"latency {op} {side}: {latency['count']} calls, smallest {latency['min']:.3f} ms, "
                             f"largest {latency['max']:.3f} ms, sum {latency['sum']:.3f} ms, "
                             f"histogram {latency['histogram']}")
    messages = [record for entry in chosen for group in entry["groups"] if group["class"] == ["diagnostic-message"]
                for record in group["first"]]
    total_messages = sum(group["count"] for entry in chosen for group in entry["groups"]
                         if group["class"] == ["diagnostic-message"])
    triples = {(r["op"], json.dumps(r["python"], sort_keys=True), json.dumps(r["lean"], sort_keys=True))
               for r in messages}
    lines.append(f"message differences: {total_messages} records, {len(triples)} distinct triples "
                 "(among the first records kept for each group)")
    for entry in chosen:
        for merge in entry.get("merge_commits", ()):
            lines.append(f"merge run {merge['commit']}: {merge['run']}")
    for finding in findings:
        entry = triage_for(finding, triage)
        label = entry.get("id") if entry else "(no entry)"
        if finding["kind"] == "unavailable":
            side = ", ".join(finding.get("sides") or ["backend"])
            lines.append(f"Finding {label}: on {finding['first_day']}, a call of {finding['op']} got no answer from "
                         f"{side} (CheckerUnavailable). Cause: {entry.get('cause') if entry else 'none'}.")
        else:
            lines.append(f"Finding {label}: on {finding['first_day']}, {finding['op']} gave a different result in "
                         f"Python and on the backend ({', '.join(finding['class'])}). Cause: "
                         f"{entry.get('cause') if entry else 'none'}.")
        fix = _fix_commit(entry) if entry else None
        lines.append(f"Fixed by {fix}." if fix else "Open.")
    if chosen:
        last, start = chosen[-1].get("nightly_commit"), chosen[0].get("nightly_commit")
        if last and start:
            for commit in history.between(start, last)[1:]:
                entry = next((item for item in changes if item.get("commit") == commit), None)
                if entry is None:
                    continue
                surface = history.surface(commit)
                for line in entry.get("files", ()):
                    where = "on the candidate surface" if shadow_surface.on_surface(line["path"], surface) else \
                        "off the candidate surface"
                    lines.append(f"classed change {commit} {line['path']} ({where}): {line['class']}, "
                                 f"{line['reason']}")
    return lines


# --- --check ----------------------------------------------------------------------------------

def check(root: Path, history: History) -> list[str]:
    """The lines of 4.3 for every malformed file (empty: well formed)."""
    problems = []
    shadow = root / SHADOW

    def read(name):
        try:
            return json.loads((shadow / name).read_text())
        except (OSError, ValueError):
            problems.append(f"{SHADOW}/{name} is not valid JSON")
            return None

    corpora = read("corpora.json")
    if corpora is not None:
        if type(corpora) is not list:
            problems.append(f"{SHADOW}/corpora.json is not a list")
        else:
            ids = [entry.get("id") for entry in corpora if type(entry) is dict]
            for missing in (name for name in CORPUS_IDS if name not in ids):
                problems.append(f"corpora entry {missing} is missing: id")
            for entry in corpora:
                if type(entry) is not dict or set(entry) != CORPUS_MEMBERS:
                    problems.append(f"corpora entry {entry.get('id') if type(entry) is dict else entry} "
                                    "does not have the members of 2.9: members")
                    continue
                floors = (entry["min_cases"], entry["min_compared"], entry["calibration"])
                if not (all(item is None for item in floors) or (
                        type(entry["min_cases"]) is int and type(entry["min_compared"]) is int
                        and type(entry["calibration"]) is str and entry["command"])):
                    problems.append(f"corpora entry {entry['id']} has floors without a calibration run: calibration")
                if entry["merge"] is not (entry["id"] == "suite"):
                    problems.append(f"corpora entry {entry['id']} is wrongly a merge corpus: merge")
            if len(ids) != len(set(ids)):
                problems.append(f"{SHADOW}/corpora.json repeats an id: id")
    triage = read("triage.json")
    if triage is not None:
        for entry in triage if type(triage) is list else [None]:
            if type(entry) is not dict or set(entry) != TRIAGE_MEMBERS:
                problems.append(f"triage entry {entry.get('id') if type(entry) is dict else entry} "
                                "does not have the members of 2.11: members")
            elif entry["cause"] is not None and entry["cause"] not in CAUSES:
                problems.append(f"triage entry {entry['id']} has an unknown cause: cause")
    wording = read("wording.json")
    if wording is not None:
        for index, entry in enumerate(wording if type(wording) is list else [None]):
            why = wording_entry_problem(entry)
            if why == "location":
                problems.append(f"wording entry {index} is not at an eligible location: {entry['op']} "
                                f"{json.dumps(entry['path'])}")
            elif why:
                problems.append(f"wording entry {index} does not have the members of 2.4: members")
    changes = read("changes.json")
    if changes is not None:
        for entry in changes if type(changes) is list else [None]:
            problems.extend(_change_problems(entry, history))
    for day, entry in ledger(root).items() if (shadow / "ledger").is_dir() else ():
        why = entry_problem(entry) if type(entry) is dict and entry.get("day") == day else "day"
        if why:
            problems.append(f"ledger entry {day} does not match its runs: {why}")
    return problems


def _change_problems(entry, history: History) -> list[str]:
    if type(entry) is not dict or set(entry) != CHANGE_MEMBERS or type(entry.get("files")) is not list:
        return [f"changes entry {entry.get('commit') if type(entry) is dict else entry} "
                "does not have the members of 2.12: members"]
    commit = entry["commit"]
    if commit not in history.index:
        return [f"changes entry {commit} does not match its diff: commit"]
    problems = []
    for line in entry["files"]:
        if type(line) is not dict or set(line) != {"path", "class", "reason"} or \
                line.get("class") not in ("restart", "no-restart") or not line.get("reason"):
            problems.append(f"changes entry {commit} does not match its diff: class")
    if entry["class"] not in ("restart", "no-restart"):
        problems.append(f"changes entry {commit} does not match its diff: class")
    elif entry["class"] != ("restart" if any(type(line) is dict and line.get("class") == "restart"
                                             for line in entry["files"]) else "no-restart"):
        problems.append(f"changes entry {commit} does not match its diff: class")
    expected = history.classed_files(commit)
    listed = [line.get("path") for line in entry["files"] if type(line) is dict]
    for path in sorted(set(expected) ^ set(listed)) + [p for p, n in Counter(listed).items() if n > 1]:
        problems.append(f"changes entry {commit} does not match its diff: {path}")
        break
    return problems


# --- the command line ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", choices=("day", "gate"))
    parser.add_argument("date", nargs="?")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--main", default="main")
    parser.add_argument("--runs", type=Path,
                        default=Path(os.environ.get("VE_SHADOW_RUNS", Path.home() / "ve-shadow-runs")))
    parser.add_argument("--now", help="the UTC time to judge finality by (tests)")
    args = parser.parse_args(argv)
    history = History(args.root, args.main)
    if args.check or args.command is None:
        problems = check(args.root, history)
        for problem in problems:
            print(problem)
        return 2 if problems else 0
    if args.date is None:
        parser.error("a date is needed")
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    if args.command == "day":
        status, sentences, entry = evaluate_day(args.date, load_runs(args.runs), history, now)
        for sentence in sentences:
            print(sentence)
        if entry is not None:
            path = args.root / SHADOW / "ledger" / f"{args.date}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(entry, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
        return status
    problems = check(args.root, history)
    if problems:
        for problem in problems:
            print(problem)
        return 2
    status, lines = evaluate_gate(args.date, args.root, history)
    for line in lines:
        print(line)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
