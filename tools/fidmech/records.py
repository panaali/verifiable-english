"""The result record of one mutant and the inputs_sha256 that binds it to everything it was computed from (plan 2e).

A record is `{"id", "verdict": {"K", "L1", "L2", "L3", "L4", "D", "CR"}, "kernel": {"changed", "inconclusive",
"toward_key", "away_from_key"}, "seconds", "cpu_seconds", "worker", "sentinel_ok", "inputs_sha256"}`, each verdict in
its vocabulary. `kernel_verdict` applies the K kill rule: an item's decided answer that differs from the batch
baseline kills; a move to or from UNDECIDED, UNKNOWN, NOT RUN or a resource limit (`UNDECIDED`) is inconclusive,
never a kill. Movement toward or away from the key is
read from the document's own comparison (its `agree` field), never recomputed here.

`inputs_sha256` is the sha256 of a canonical JSON of the listed inputs. The B5 runner refuses a resume or a merge on
any difference; the files later batches create (equivalents.json, actors.json, the generator version, mutant ids)
enter as absent or empty values the function already accepts.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

VOCABULARY = {
    "K": ("killed", "survived", "inconclusive", "error", "not-run"),
    "L1": ("killed", "survived"), "L2": ("killed", "survived"), "L3": ("killed", "survived"),
    "L4": ("killed", "survived"), "D": ("killed", "survived"),
    "CR": ("found", "missed", "not-read"),
}
RECORD_KEYS = ("id", "verdict", "kernel", "seconds", "cpu_seconds", "worker", "sentinel_ok", "inputs_sha256")
# Every spelling of the third value (plan 2e: UNDECIDED or a resource limit; build-checklist 6: UNKNOWN is never a
# decided answer) a document writes into an answer field: RSP and PF `UNDECIDED` (`UNDECIDED-faithful`), FSF `UNKNOWN`
# (N1, premises, S1, S4, D1, D3) and `NOT RUN`, the resource-limit reasons of RSP and PF. A string is undecided when it
# is one of them or one of them followed by a separator; tests/test_fidmech_records.py reads every such spelling in
# the documents' sources (ast) and fails on one this table does not recognise.
UNDECIDED = ("UNDECIDED", "UNKNOWN", "NOT RUN", "resource limit", "resource-limit")
UNDECIDED_SEPARATORS = ("-", ":", " ", "(")
# usecases/<doc>/fidmech/ files named by plan 2e; any other file of that directory (actors.json, B4) enters too.
CASE_FILES = ("boundaries.json", "ruled_out.json", "equivalents.json", "bindings.json")
INPUT_KEYS = ("commit", "uncommitted", "sources", "case_files", "tools_fidmech", "generator_version", "mutants")


def _undecided(answer):
    """Whether an answer tuple carries an undecided value anywhere."""
    if isinstance(answer, str):
        return any(answer == token or answer.startswith(tuple(token + s for s in UNDECIDED_SEPARATORS))
                   for token in UNDECIDED)
    if isinstance(answer, (tuple, list)):
        return any(_undecided(a) for a in answer)
    return False


def kernel_verdict(baseline, mutant, agree_baseline=None, agree_mutant=None):
    """(K verdict, kernel dict) of a mutant's answers against the batch baseline's ({item id: answer tuple}).
    An item set that differs is an error (the key fixes the items). `agree_*` ({item id: bool}) give the
    movement toward and away from the key."""
    if set(baseline) != set(mutant):
        return "error", {"changed": [], "inconclusive": [], "toward_key": 0, "away_from_key": 0,
                         "items_differ": sorted(set(baseline) ^ set(mutant))}
    changed, inconclusive = [], []
    for item in baseline:
        if baseline[item] == mutant[item]:
            continue
        (inconclusive if _undecided(baseline[item]) or _undecided(mutant[item]) else changed).append(item)
    toward = away = 0
    if agree_baseline is not None and agree_mutant is not None:
        for item in changed + inconclusive:
            toward += not agree_baseline[item] and agree_mutant[item]
            away += agree_baseline[item] and not agree_mutant[item]
    verdict = "killed" if changed else "inconclusive" if inconclusive else "survived"
    return verdict, {"changed": sorted(changed), "inconclusive": sorted(inconclusive), "toward_key": toward,
                     "away_from_key": away}


def result_record(id_, verdict, kernel, seconds, cpu_seconds, worker, sentinel_ok, inputs_sha256):
    """A result line; a verdict outside its vocabulary, a missing verdict or a malformed field is refused."""
    if set(verdict) != set(VOCABULARY):
        raise ValueError(f"{id_}: verdicts {sorted(verdict)} are not {sorted(VOCABULARY)}")
    for check, value in verdict.items():
        if value not in VOCABULARY[check]:
            raise ValueError(f"{id_}: verdict {check}={value!r} is not one of {VOCABULARY[check]}")
    if not {"changed", "inconclusive", "toward_key", "away_from_key"} <= set(kernel):
        raise ValueError(f"{id_}: kernel lacks {sorted({'changed', 'inconclusive', 'toward_key', 'away_from_key'} - set(kernel))}")
    if type(sentinel_ok) is not bool or type(inputs_sha256) is not str or len(inputs_sha256) != 64:
        raise ValueError(f"{id_}: sentinel_ok is a bool and inputs_sha256 a sha256")
    return dict(zip(RECORD_KEYS, (id_, dict(verdict), dict(kernel), seconds, cpu_seconds, worker, sentinel_ok,
                                  inputs_sha256)))


def sha256_file(path):
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def canonical(value):
    """The canonical JSON bytes the hash reads: sorted keys, no spaces, UTF-8."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def inputs_sha256(inputs):
    """sha256 of the canonical JSON of exactly the INPUT_KEYS; a missing or an extra key is refused."""
    if set(inputs) != set(INPUT_KEYS):
        raise ValueError(f"inputs keys {sorted(inputs)} are not {sorted(INPUT_KEYS)}")
    return hashlib.sha256(canonical(inputs)).hexdigest()


def _git(worktree, *args):
    return subprocess.run(["git", "-C", str(worktree), *args], check=True, capture_output=True).stdout


def collect_inputs(worktree, document, *, generator_version=None, mutants=()):
    """The inputs of one document's batch in a worktree: the commit, every uncommitted change (the diff against HEAD
    and each untracked file's sha256), the pinned source hashes, the sha256 of each case file (None when absent) and
    of every file under tools/fidmech/, the generator version and the sorted (mutant id, sha256 of its edits)."""
    worktree = Path(worktree)
    commit = _git(worktree, "rev-parse", "HEAD").decode().strip()
    diff = _git(worktree, "diff", "--binary", "HEAD")
    untracked = _git(worktree, "ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")
    pinned = json.loads((worktree / "usecases" / "pinned_sources.json").read_text(encoding="utf-8"))["sources"]
    entry = pinned.get(document, {})
    case_dir = worktree / "usecases" / document / "fidmech"
    names = set(CASE_FILES) | ({p.name for p in case_dir.iterdir() if p.is_file()} if case_dir.is_dir() else set())
    fidmech = worktree / "tools" / "fidmech"
    tools = {p.relative_to(worktree).as_posix(): sha256_file(p) for p in sorted(fidmech.rglob("*"))
             if p.is_file() and "__pycache__" not in p.parts}
    return {
        "commit": commit,
        "uncommitted": {"diff_sha256": hashlib.sha256(diff).hexdigest(),
                        "untracked": {u: sha256_file(worktree / u) for u in sorted(filter(None, untracked))}},
        "sources": {k: entry.get(k) for k in ("text_sha256", "pdf_sha256")},
        "case_files": {name: sha256_file(case_dir / name) for name in sorted(names)},
        "tools_fidmech": tools,
        "generator_version": generator_version,
        "mutants": sorted([m.id, hashlib.sha256(canonical(m.edits)).hexdigest()] for m in mutants),
    }
