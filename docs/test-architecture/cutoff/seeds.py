"""Behavioural Lean seeds: is each one caught by a test that the narrowed selections keep?

  python3 docs/test-architecture/cutoff/seeds.py run --worktree W --recording DIR [--only S01 ...]
  python3 docs/test-architecture/cutoff/seeds.py check

`run` works in W, a scratch worktree at this batch's commit with a Lean build: for each seed of
seeds.json it plants the edit, rebuilds `ve_service` alone (the one-shot executables keep the
unseeded code, so a catch is through the service), pins that build in W's lean/checkers.lock for
the run, replays the recording against it (tools/answer_replay.py), computes today's selection and
the `modes` and `answers` selections for the one changed file with the recording's map, and runs the
candidate tests (the files that name the seed's text, else the narrowed users of its modes) until
one fails. Then it restores W. The rows go to evidence/seeds.json; `check` reads them only.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
SEEDS = HERE / "seeds.json"
EVIDENCE = HERE / "evidence/seeds.json"
SERVICE = "lean/.lake/build/bin/ve_service"
LOCK = "lean/checkers.lock"
REQUIRED = 26  # Astra's re-check point 6 and docs/test-speed-b2/REPORT.md: 26 behavioural Lean seeds


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def env_for(worktree: Path) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith(("PYTEST_", "VE_TESTMAP"))}
    env.update(PATH=str(Path.home() / ".elan/bin") + os.pathsep + env.get("PATH", ""), VE_LEAN_PREBUILT="1",
               VE_NATIVE_PREBUILT="1")
    return env


def run(command: list[str], cwd: Path, log: Path, env: dict[str, str]) -> int:
    with log.open("a") as handle:
        handle.write(f"\n+ {' '.join(command)}\n")
        handle.flush()
        return subprocess.run(command, cwd=cwd, env=env, stdout=handle, stderr=subprocess.STDOUT).returncode


def failures(junit: Path) -> list[str]:
    """The failed node IDs of a JUnit report written with `run_order.junit_options` (tools/run_order.py)."""
    import run_order
    found = run_order.read_junit(junit)
    return sorted(found[1]) if found else []


def candidates(seed: dict, worktree: Path, selected: list[str], index: dict, modes: set[str],
               seconds: dict[str, float], changed: set[str] = frozenset()) -> list[str]:
    """Where in the narrowed selection a test may see the seed: the units that sent a case whose answer
    changed, the files that name the seed's text, and else the users of the seed's modes (at most 12 of
    each, the shortest first)."""
    def shortest(units) -> list[str]:
        return sorted((unit for unit in set(units) if unit in selected and unit.startswith("tests/")),
                      key=lambda unit: (seconds.get(unit, 0), unit))[:12]

    keys = index["keys"]
    senders = shortest(unit for unit, entry in index["units"].items() if any(keys[i] in changed for i in entry["keys"]))
    words = [word.strip() for word in re.findall(r"[A-Za-z][A-Za-z ,:-]{6,}", seed["old"]) if len(word.strip()) > 8]
    named = shortest(unit for unit in selected if unit.startswith("tests/") and any(
        word in (worktree / unit).read_text(errors="replace") for word in words))
    users = [] if senders or named else shortest(
        unit for unit, entry in index["units"].items() if any(index["modes"][i] in modes for i in entry["keys"]))
    return sorted(set(senders) | set(named) | set(users))


def one(seed: dict, worktree: Path, recording: Path, base_answers: Path, work: Path) -> dict:
    sys.path.insert(0, str(worktree / "tools"))
    import answer_cutoff
    import answer_replay
    import lean_mode_deps
    import nested_pytest
    import select_tests
    import source_graph
    import test_map

    env = env_for(worktree)
    log = work / f"{seed['id']}.log"
    path = worktree / seed["file"]
    original = path.read_text()
    lock = (worktree / LOCK).read_text()
    row = {"id": seed["id"], "file": seed["file"], "old": seed["old"], "new": seed["new"]}
    started = time.monotonic()
    try:
        path.write_text(original.replace(seed["old"], seed["new"]))
        if run(["lake", "build", "ve_service"], worktree / "lean", log, env):
            return {**row, "status": "build failed"}
        build = sha256(worktree / SERVICE)
        pins = json.loads(lock)
        pins["ve_service"] = sorted({*pins["ve_service"], build})
        (worktree / LOCK).write_text(json.dumps(pins, indent=2) + "\n")
        graph = source_graph.load(worktree)
        module = ".".join(Path(seed["file"]).with_suffix("").parts[1:])
        roots = lean_mode_deps.load() or {}
        modes = {mode for mode, entry in roots.items() if any(module in graph.lean_closure(r) for r in entry)}
        # Only the cases of the modes whose runMode roots import the module: the others keep the base's
        # answers here. Replaying them too could only add changed answers, so a test this selection keeps
        # is kept by the full replay's selection as well; the selection sizes below are lower bounds.
        base = answer_replay.read_json(base_answers)
        partial = answer_replay.replay(recording, worktree / SERVICE, jobs=8, progress=lambda _: None, modes=modes)
        head = {**base, "service": partial["service"], "answers": {**base["answers"], **partial["answers"]}}
        diff = answer_replay.diff(base, head)
        diff["recording_dir"] = str(recording)
        diff_path = work / f"{seed['id']}-diff.json"
        answer_replay.write_json(diff, diff_path)
        data = test_map.load(recording / "map.json.gz")
        today = select_tests.select([seed["file"]], base="HEAD", coverage=select_tests.Coverage(data))
        modes_plan = answer_cutoff.select("modes", [seed["file"]], base="HEAD", coverage=select_tests.Coverage(data))
        answers_plan = answer_cutoff.select_answers(diff_path, [seed["file"]], base="HEAD", after=None, build=build)
        index = answer_replay.read_json(recording / "requests.json.gz")
        seconds = {unit: status["seconds"] for unit, status in data["status"].items()}
        tried = candidates(seed, worktree, modes_plan["selected"], index, modes, seconds, set(diff["changed"]))
        junit = work / f"{seed['id']}-junit.xml"
        if tried:
            import run_order
            run(nested_pytest.command(["-q", "-p", "no:cacheprovider", "-x", *run_order.junit_options(junit), *tried],
                                      workers=8), worktree, log, nested_pytest.environment(env))
        caught = failures(junit)
        return {**row, "status": "caught" if caught else "not caught", "build": build, "modes": sorted(modes),
                "changed_cases": len(diff["changed"]), "cases": diff["cases"],
                "replayed_cases": len(partial["answers"]),
                "changed_modes": sorted({index["modes"][index["keys"].index(k)] for k in diff["changed"]}),
                "today": today["selected"], "modes_selected": modes_plan["selected"],
                "answers_selected": answers_plan["selected"], "unknown": sorted(answers_plan["cutoff"]["unknown"]),
                "tried": tried, "caught_by": caught,
                "caught_in": {name: all(test.split("::")[0] in plan for test in caught)
                              for name, plan in (("today", today["selected"]), ("modes", modes_plan["selected"]),
                                                 ("answers", answers_plan["selected"]))},
                "seconds": round(time.monotonic() - started)}
    finally:
        path.write_text(original)
        (worktree / LOCK).write_text(lock)
        sys.path.pop(0)


def verify(row: dict, worktree: Path, unseeded: Path, work: Path, tests: list[str]) -> dict:
    """Whether the catch is the service's: with the source restored and the same pins, the catching tests
    fail with the seeded ve_service and pass with the unseeded one. A test that fails only because it reads
    the Lean source (a trust count, a source hash) is no catch through the service."""
    sys.path.insert(0, str(worktree / "tools"))
    import nested_pytest
    env = env_for(worktree)
    log = work / f"{row['id']}-verify.log"
    path, binary, lock_path = worktree / row["file"], worktree / SERVICE, worktree / LOCK
    original, lock = path.read_text(), lock_path.read_text()
    outcome = {}
    try:
        path.write_text(original.replace(row["old"], row["new"]))
        if run(["lake", "build", "ve_service"], worktree / "lean", log, env):
            return {"status": "build failed"}
        seeded = sha256(binary)
        path.write_text(original)
        pins = json.loads(lock)
        pins["ve_service"] = sorted({*pins["ve_service"], seeded})
        lock_path.write_text(json.dumps(pins, indent=2) + "\n")
        # Every candidate file with the seeded build, then only what failed with the unseeded one.
        for name, source, tests in (("seeded", None, tests), ("unseeded", unseeded, None)):
            if source is not None:
                binary.write_bytes(source.read_bytes())
            tests = tests if tests is not None else outcome["seeded"]
            if not tests:
                outcome[name] = []
                continue
            junit = work / f"{row['id']}-verify-{name}.xml"
            import run_order
            run(nested_pytest.command(["-q", "-p", "no:cacheprovider", *run_order.junit_options(junit), *tests],
                                      workers=8 if source is None else 1), worktree, log, nested_pytest.environment(env))
            outcome[name] = failures(junit)
    finally:
        path.write_text(original)
        lock_path.write_text(lock)
        binary.write_bytes(unseeded.read_bytes())
        sys.path.pop(0)
    through = sorted(set(outcome["seeded"]) - set(outcome["unseeded"]))
    return {"build": seeded, "seeded_failures": outcome["seeded"], "unseeded_failures": outcome["unseeded"],
            "through_service": through}


CAUGHT, SOURCE_ONLY, MISSED, UNSEEN, UNBUILT, UNVERIFIED = (
    "caught", "caught only by a reader of the Lean source", "not caught", "seen by no service test", "build failed",
    "not verified")


def outcome(row: dict) -> str:
    """What a seed's row shows. A catch counts when a test fails on the seeded build with the source restored
    and passes on the unseeded one (`verify`); a seed that changed no recorded answer no service test sees."""
    if row["status"] == "build failed":
        return UNBUILT
    if "verified" in row:
        if row["verified"].get("through_service"):
            return CAUGHT
        return SOURCE_ONLY if row["status"] == "caught" else MISSED
    if row["status"] == "not caught" and not row["changed_cases"]:
        return UNSEEN
    return UNVERIFIED


def kept_by(row: dict) -> dict[str, bool]:
    """Whether today's, the modes and the answers selections hold every test that catches the seed."""
    units = {test.split("::")[0] for test in row["verified"]["through_service"]}
    return {name: units <= set(row[key]) for name, key in (("today", "today"), ("modes", "modes_selected"),
                                                          ("answers", "answers_selected"))}


def check(rows: list[dict]) -> int:
    """The saved rows are the seeds of seeds.json and agree with themselves; the number caught."""
    seeds = json.loads(SEEDS.read_text())
    assert [row["id"] for row in rows] == [seed["id"] for seed in seeds]
    for row, seed in zip(rows, seeds, strict=True):
        assert (row["file"], row["old"], row["new"]) == (seed["file"], seed["old"], seed["new"])
        found = outcome(row)
        assert found != UNVERIFIED, f"{row['id']} was not verified"
        if found == UNBUILT:
            continue
        assert set(row["modes_selected"]) <= set(row["today"]) and set(row["answers_selected"]) <= set(row["today"])
        if found == CAUGHT:
            verified = row["verified"]
            assert set(verified["through_service"]) <= set(verified["seeded_failures"])
            assert not set(verified["through_service"]) & set(verified["unseeded_failures"])
        if found == UNSEEN:
            assert not row["caught_by"] and not row["changed_cases"], row["id"]
    return sum(outcome(row) == CAUGHT for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    go = sub.add_parser("run")
    go.add_argument("--worktree", type=Path, required=True)
    go.add_argument("--recording", type=Path, required=True)
    go.add_argument("--base-answers", type=Path, required=True, help="the recording replayed on W's unseeded build")
    go.add_argument("--only", nargs="*")
    go.add_argument("--output", type=Path, default=EVIDENCE, help="where the rows go (merge them into the evidence)")
    again = sub.add_parser("verify", help="re-run each caught seed's catching tests with the source restored")
    again.add_argument("--worktree", type=Path, required=True)
    again.add_argument("--evidence", type=Path, default=EVIDENCE)
    again.add_argument("--recording", type=Path, required=True)
    again.add_argument("--diffs", type=Path, nargs="+", required=True, help="directories of the seeds' diffs")
    again.add_argument("--only", nargs="*")
    again.add_argument("--reverse", action="store_true", help="last seed first (a second worker meets the first)")
    again2 = sub.add_parser("stale", help="add to each answers selection the units that read a stale case")
    again2.add_argument("--evidence", type=Path, default=EVIDENCE)
    again2.add_argument("--recording", type=Path, required=True)
    again2.add_argument("--base-answers", type=Path, required=True, help="the seeds' base replay")
    again2.add_argument("--recording-answers", type=Path, required=True,
                        help="the recording replayed on its own build, in the seeds' answer format")
    sub.add_parser("check")
    args = parser.parse_args()
    if args.command == "stale":
        # The seeds' base build is this machine's; the recording's is the runner's. A case whose answer
        # differs between the two makes its readers unknown (answer_cutoff.unknown_units); they are
        # service users, so today's selection holds them, and the answers selection gains them.
        with gzip.open(args.base_answers, "rt") as handle:
            base = json.load(handle)
        with gzip.open(args.recording_answers, "rt") as handle:
            own = json.load(handle)
        assert base["version"] == own["version"] and base["recording"] == own["recording"]
        stale = {key for key, answer in own["answers"].items() if base["answers"].get(key) != answer}
        with gzip.open(args.recording / "requests.json.gz", "rt") as handle:
            index = json.load(handle)
        readers = {unit for unit, entry in index["units"].items() if any(index["keys"][i] in stale for i in entry["keys"])}
        data = json.loads(args.evidence.read_text())
        data["stale"] = {"cases": len(stale), "units": sorted(readers), "base_build": base["service"],
                         "recording_build": own["service"], "answer_format": base["version"]}
        for row in data["seeds"]:
            if row["status"] in ("caught", "not caught"):
                row["answers_selected"] = sorted(set(row["answers_selected"]) | (readers & set(row["today"])))
                row["unknown"] = sorted(set(row["unknown"]) | (readers & set(row["today"])))
                if row["status"] == "caught":
                    row["caught_in"]["answers"] = all(test.split("::")[0] in row["answers_selected"]
                                                      for test in row["caught_by"])
        args.evidence.write_text(json.dumps(data, indent=1) + "\n")
        print(f"{len(stale)} stale cases, read by {sorted(readers)}")
        return 0
    if args.command == "verify":
        worktree = args.worktree.resolve()
        work = Path(tempfile.mkdtemp(prefix="cutoff-verify-"))
        env = env_for(worktree)
        if run(["lake", "build", "ve_service"], worktree / "lean", work / "unseeded.log", env):
            raise SystemExit("the unseeded build failed")
        unseeded = work / "ve_service.unseeded"
        unseeded.write_bytes((worktree / SERVICE).read_bytes())
        data = json.loads(args.evidence.read_text())
        sys.path.insert(0, str(worktree / "tools"))
        import answer_replay
        index = answer_replay.read_json(args.recording / "requests.json.gz")
        with gzip.open(args.recording / "map.json.gz", "rt") as handle:
            seconds = {unit: status["seconds"] for unit, status in json.load(handle)["status"].items()}
        for row in (reversed(data["seeds"]) if args.reverse else data["seeds"]):
            # A seed that changed no recorded answer cannot be seen through the service: nothing to verify.
            if (row["status"] == "caught" or row["status"] == "not caught" and row["changed_cases"]) \
                    and "verified" not in row and (not args.only or row["id"] in args.only):
                diff = next(json.loads(path.read_text()) for directory in args.diffs
                            if (path := directory / f"{row['id']}-diff.json").exists())
                tests = sorted(set(row.get("tried", ())) | set(candidates(
                    row, worktree, row["modes_selected"], index, set(row["modes"]), seconds, set(diff["changed"]))))
                row["verified"] = {"tests": tests, **verify(row, worktree, unseeded, work, tests)}
                print(row["id"], row["verified"].get("through_service"), flush=True)
                args.evidence.write_text(json.dumps(data, indent=1) + "\n")
        return 0
    if args.command == "check":
        rows = json.loads(EVIDENCE.read_text())["seeds"]
        caught = check(rows)
        kept = {name: sum(kept_by(row)[name] for row in rows if outcome(row) == CAUGHT)
                for name in ("today", "modes", "answers")}
        print(f"{caught} seeds caught through the service (activation needs {REQUIRED}); kept by today {kept['today']}, "
              f"modes {kept['modes']}, answers {kept['answers']}")
        return 0
    work = Path(tempfile.mkdtemp(prefix="cutoff-seeds-"))
    rows = json.loads(args.output.read_text())["seeds"] if args.output.exists() else []
    done = {row["id"]: row for row in rows}
    for seed in json.loads(SEEDS.read_text()):
        if args.only and seed["id"] not in args.only:
            continue
        done[seed["id"]] = one(seed, args.worktree.resolve(), args.recording.resolve(), args.base_answers, work)
        print(json.dumps({key: done[seed["id"]].get(key) for key in ("id", "status", "caught_by", "caught_in",
                                                                    "changed_cases", "seconds")}), flush=True)
        order = [seed["id"] for seed in json.loads(SEEDS.read_text())]
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"worktree_commit": subprocess.run(
            ["git", "-C", str(args.worktree), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
            "seeds": [done[i] for i in order if i in done]}, indent=1) + "\n")
    print(f"logs in {work}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
