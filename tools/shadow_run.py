"""One run of one Stage 3 corpus in shadow (docs/spec/mig3.md 2.8, 4.3).

Usage: ``tools/shadow_run.py --corpus ID --out DIRECTORY [--trigger nightly|merge|manual]
[--webapp-commit SHA] [--calibration]``

The tool registers the run (``run.json`` without ``finished``, ``exit``,
``cases`` and ``stderr_faults``) before it starts the corpus command, runs it
with ``VE_AUTHORITY=shadow``, ``VE_SHADOW_DIR`` the run's directory and
``VE_SHADOW_RUN`` the run's name, copies its standard error to ``stderr.txt``,
rewrites ``run.json`` when it exits, prints ``run <run> is not complete:
<condition>`` for each condition of 2.8 that fails, and exits with the
command's own status.  ``--calibration`` checks every condition but the floors
(a calibration run, 2.9).

``run_problems`` is the completeness check that ``tools/shadow_gate.py`` also uses.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "conformance/shadow/corpora.json"
KINDS = ("divergence", "unavailable", "lean-only", "recorder-fault")
RECORD_MEMBERS = {"kind", "op", "input_digest", "python", "lean", "rust", "class", "python_ms",
                  "backend_ms", "run", "test", "input"}
TALLY_MEMBERS = {"run", "pid", "nonce", "started", "final", "calls", "ops"}
OP_COUNTS = ("compared", "agree", "recorded_only", "zero_tolerance", "completion_failures",
             "unavailable_other", "lean_only", "recorder_faults")
STDERR_FAULT = "ve shadow:"
# The corpus that takes the seed of its day (2.9).
SEEDED = ("fuzz-nightly",)
BINARIES = {"ve_service": ("VE_LEAN_SERVICE", "lean/.lake/build/bin/ve_service"),
            "rust_jsonl": ("VE_RUST_JSONL", "rust/target/release/ve")}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(*args: str, root: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout


def clean(root: Path = ROOT) -> bool:
    return git("status", "--porcelain", root=root).strip() == ""


def sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def builds(root: Path = ROOT) -> dict:
    """The SHA-256 of the two checker binaries a run loads, found as the backends find them."""
    return {name: sha256(Path(os.environ.get(variable) or root / default))
            for name, (variable, default) in BINARIES.items()}


def load_registry(path: Path = REGISTRY) -> list[dict]:
    return json.loads(path.read_text())


def corpus(registry: list[dict], name: str) -> dict:
    for entry in registry:
        if entry.get("id") == name:
            return entry
    raise SystemExit(f"shadow run: no corpus {name!r} in the registry")


def day_seed(started: str) -> int:
    return int(started[:10].replace("-", ""))


# --- the completeness check (2.8) ------------------------------------------------------

def is_record(row) -> bool:
    if type(row) is not dict or row.get("kind") not in KINDS:
        return False
    expected = set(RECORD_MEMBERS)
    if row["kind"] == "unavailable":
        expected.add("sides")
    if row["kind"] == "recorder-fault":
        expected.add("error")
    return set(row) == expected and type(row["class"]) is list and type(row["op"]) is str


def is_tally(data) -> bool:
    return (type(data) is dict and set(data) == TALLY_MEMBERS and type(data["final"]) is bool
            and type(data["calls"]) is int and type(data["ops"]) is dict
            and all(type(counts) is dict and all(type(counts.get(name)) is int for name in OP_COUNTS)
                    for counts in data["ops"].values()))


def read_run(directory: Path) -> dict:
    """The files of a run directory: `run.json`, the tallies and the records by
    worker (`pid-nonce`), the malformed files, and `stderr.txt`'s fault lines."""
    directory = Path(directory)
    try:
        meta = json.loads((directory / "run.json").read_text())
    except (OSError, ValueError):
        meta = None
    tallies, records, malformed = {}, {}, []
    for path in sorted(directory.glob("tally-*.json")):
        worker = path.name[len("tally-"):-len(".json")]
        try:
            data = json.loads(path.read_text())
        except ValueError:
            data = None
        if is_tally(data):
            tallies[worker] = data
        else:
            malformed.append(path.name)
    for path in sorted(directory.glob("records-*.jsonl")):
        worker = path.name[len("records-"):-len(".jsonl")]
        text = path.read_text(encoding="utf-8", errors="replace")
        rows = []
        bad = not text.endswith("\n") and text != ""
        for line in text.splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                row = None
            if not is_record(row):
                bad = True
            else:
                rows.append(row)
        if bad:
            malformed.append(path.name)
        records[worker] = rows
    try:
        stderr = (directory / "stderr.txt").read_text(errors="replace").splitlines()
    except OSError:
        stderr = []
    return {"meta": meta, "tallies": tallies, "records": records, "malformed": malformed,
            "stderr_faults": sum(1 for line in stderr if line.startswith(STDERR_FAULT))}


def summed(tallies: dict) -> dict:
    """The tallies of a run summed over its workers, by operation."""
    ops: dict[str, dict] = {}
    for tally in tallies.values():
        for op, counts in tally["ops"].items():
            mine = ops.setdefault(op, {name: 0 for name in OP_COUNTS} | {"uncompared": {}})
            for name in OP_COUNTS:
                mine[name] += counts[name]
            for reason, number in counts.get("uncompared", {}).items():
                mine["uncompared"][reason] = mine["uncompared"].get(reason, 0) + number
            for key in ("count_members", "latency"):
                if key in counts:
                    mine.setdefault(key, {})
                    _merge(mine[key], counts[key])
    return ops


def _merge(target: dict, source: dict) -> None:
    for key, value in source.items():
        if isinstance(value, dict):
            _merge(target.setdefault(key, {}), value)
        elif isinstance(value, list):
            current = target.setdefault(key, [0] * len(value))
            target[key] = [a + b for a, b in zip(current, value)]
        elif key == "min":
            target[key] = value if target.get(key) is None else (
                target[key] if value is None else min(target[key], value))
        elif key == "max":
            target[key] = value if target.get(key) is None else (
                target[key] if value is None else max(target[key], value))
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            target[key] = target.get(key, 0) + value
        else:
            target.setdefault(key, value)


def reconciles(tally: dict, rows: list[dict] | None) -> bool:
    kinds = {kind: 0 for kind in KINDS}
    for row in rows or ():
        kinds[row["kind"]] += 1
    ops = tally["ops"].values()
    total = {name: sum(counts[name] for counts in ops) for name in OP_COUNTS}
    if rows is None:
        return not (total["zero_tolerance"] or total["recorded_only"] or total["completion_failures"]
                    or total["unavailable_other"] or total["lean_only"])
    return (kinds["divergence"] == total["zero_tolerance"] + total["recorded_only"]
            and kinds["unavailable"] == total["completion_failures"] + total["unavailable_other"]
            and kinds["lean-only"] == total["lean_only"]
            and kinds["recorder-fault"] <= total["recorder_faults"])


def run_problems(directory: Path, entry: dict | None, lock: dict | None, *,
                 calibration: bool = False) -> list[str]:
    """The conditions of 2.8 that a run fails, in the wording of 3.1 (empty: complete).

    `entry` is the corpus's registry entry; `lock` is `lean/checkers.lock` at
    the run's commit."""
    run = read_run(directory)
    meta = run["meta"]
    if type(meta) is not dict:
        return ["run.json is missing or malformed"]
    problems = []
    if entry is None:
        problems.append(f"the corpus {meta.get('corpus')} is not in the registry")
        entry = {}
    if meta.get("exit") != entry.get("expected_exit"):
        problems.append(f"the exit status is {meta.get('exit')}, not {entry.get('expected_exit')}")
    if meta.get("clean") != {"started": True, "finished": True}:
        problems.append(f"the checkout was not clean at {meta.get('commit')}")
    for name in BINARIES:
        if (meta.get("builds") or {}).get(name) not in (lock or {}).get(name, ()):
            problems.append(f"the {name} binary is not pinned in lean/checkers.lock")
    for name in run["malformed"]:
        problems.append(f"the file {name} is malformed")
    tallies, records = run["tallies"], run["records"]
    for worker, tally in sorted(tallies.items()):
        if not tally["final"]:
            problems.append(f"the worker {worker} did not finalize its tally")
    for worker in sorted(set(tallies) | set(records)):
        if worker not in tallies or not reconciles(tallies[worker], records.get(worker)):
            problems.append(f"the tally of {worker} does not match its records")
    faults = sum(counts["recorder_faults"] for tally in tallies.values() for counts in tally["ops"].values())
    stderr_faults = meta.get("stderr_faults")
    if faults or stderr_faults != 0:
        problems.append(f"{faults + (stderr_faults or 0)} recorder faults ({stderr_faults} on standard error)")
    if not calibration:
        compared = sum(counts["compared"] for counts in summed(tallies).values())
        if entry.get("min_cases") is None or entry.get("min_compared") is None:
            problems.append(f"the corpus {entry.get('id')} has no floors: it is not calibrated")
        else:
            if type(meta.get("cases")) is not int or meta["cases"] < entry["min_cases"]:
                problems.append(f"{meta.get('cases')} cases, below the floor of {entry['min_cases']}")
            if compared < entry["min_compared"]:
                problems.append(f"{compared} compared calls, below the floor of {entry['min_compared']}")
    if meta.get("corpus") in SEEDED and meta.get("seed") != day_seed(meta.get("started") or "0000-00-00"):
        problems.append(f"the seed is {meta.get('seed')}, not the seed of {str(meta.get('started'))[:10]}")
    if not meta.get("finished"):
        problems.append("the run has not finished")
    return problems


# --- running ---------------------------------------------------------------------------

def _copy(stream, *targets) -> None:
    for line in iter(stream.readline, b""):
        for target in targets:
            target.write(line)
            target.flush()


def write_json(path: Path, data: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    os.replace(temporary, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--trigger", choices=("nightly", "merge", "manual"), default="manual")
    parser.add_argument("--webapp-commit")
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--calibration", action="store_true",
                        help="a calibration run: every condition but the floors")
    args = parser.parse_args(argv)
    entry = corpus(load_registry(args.registry), args.corpus)
    if not entry.get("command"):
        raise SystemExit(f"shadow run: the corpus {args.corpus} has no command yet")
    directory = args.out
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise SystemExit(f"shadow run: {directory} is not empty")
    commit = git("rev-parse", "HEAD").strip()
    started = now()
    name = f"{args.corpus}-{commit[:12]}-{started.replace('-', '').replace(':', '')}"
    seed = day_seed(started) if args.corpus in SEEDED else None
    meta = {"run": name, "corpus": args.corpus, "commit": commit, "trigger": args.trigger,
            "started": started, "builds": builds(), "seed": seed,
            "webapp_commit": args.webapp_commit if args.corpus == "webapp" else None,
            "clean": {"started": clean(), "finished": None}}
    write_json(directory / "run.json", meta)
    environment = {key: value for key, value in os.environ.items()
                   if key not in ("VE_AUTHORITY_OVERRIDES", "VE_SHADOW_LOG")}
    cases_file = directory.resolve().parent / f".{directory.name}.cases.json"
    environment.update({"VE_AUTHORITY": "shadow", "VE_SHADOW_DIR": str(directory.resolve()),
                        "VE_SHADOW_RUN": name, "VE_SHADOW_STARTED": started,
                        "VE_SHADOW_CASES": str(cases_file)})
    command = [part.replace("{python}", sys.executable).replace("{seed}", str(seed)) for part in entry["command"]]
    with open(directory / "stderr.txt", "wb") as copy:
        process = subprocess.Popen(command, cwd=ROOT, env=environment, stderr=subprocess.PIPE)
        pump = threading.Thread(target=_copy, args=(process.stderr, copy, sys.stderr.buffer), daemon=True)
        pump.start()
        status = process.wait()
        pump.join()
    try:
        cases = json.loads(cases_file.read_text())["cases"]
        cases_file.unlink()
    except (OSError, ValueError, KeyError):
        cases = None
    meta.update({"finished": now(), "exit": status, "cases": cases,
                 "stderr_faults": read_run(directory)["stderr_faults"]})
    meta["clean"]["finished"] = clean()
    write_json(directory / "run.json", meta)
    lock = json.loads(git("show", f"{commit}:lean/checkers.lock"))
    for problem in run_problems(directory, entry, lock, calibration=args.calibration):
        print(f"run {name} is not complete: {problem}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
