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
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ElementTree

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
    if not junit.exists():
        return []
    found = []
    for case in ElementTree.parse(junit).getroot().iter("testcase"):
        if case.find("failure") is not None or case.find("error") is not None:
            path = case.get("file") or case.get("classname", "").replace(".", "/") + ".py"
            found.append(f"{path}::{case.get('name')}")
    return found


def candidates(seed: dict, worktree: Path, selected: list[str], index: dict, modes: set[str],
               seconds: dict[str, float]) -> list[str]:
    """The narrowed selection's files that name the seed's text; else its users of the seed's modes."""
    words = re.findall(r"[A-Za-z][A-Za-z ,:-]{6,}", seed["old"])
    named = [unit for unit in selected if unit.startswith("tests/") and any(
        word.strip() in (worktree / unit).read_text(errors="replace") for word in words if len(word.strip()) > 8)]
    if named:
        return sorted(named, key=lambda unit: seconds.get(unit, 0))
    keys = index["keys"]
    users = {unit for unit, entry in index["units"].items()
             if any(index["modes"][i] in modes for i in entry["keys"])}
    return sorted((unit for unit in selected if unit in users and unit.startswith("tests/")),
                  key=lambda unit: seconds.get(unit, 0))[:12] if keys else []


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
        tried = candidates(seed, worktree, modes_plan["selected"], index, modes, seconds)
        junit = work / f"{seed['id']}-junit.xml"
        if tried:
            run(nested_pytest.command(["-q", "-p", "no:cacheprovider", "-x", f"--junitxml={junit}", *tried],
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


def check(rows: list[dict]) -> None:
    seeds = json.loads(SEEDS.read_text())
    assert [row["id"] for row in rows] == [seed["id"] for seed in seeds]
    for row, seed in zip(rows, seeds, strict=True):
        assert (row["file"], row["old"], row["new"]) == (seed["file"], seed["old"], seed["new"])
        if row["status"] != "caught":
            continue
        assert row["caught_by"] and all(row["caught_in"].values()), row["id"]
        for name, key in (("today", "today"), ("modes", "modes_selected"), ("answers", "answers_selected")):
            assert row["caught_in"][name] == all(test.split("::")[0] in row[key] for test in row["caught_by"])
        assert set(row["modes_selected"]) <= set(row["today"]), row["id"]
    caught = [row for row in rows if row["status"] == "caught"]
    assert len(caught) >= REQUIRED, f"{len(caught)} seeds caught, {REQUIRED} required"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    go = sub.add_parser("run")
    go.add_argument("--worktree", type=Path, required=True)
    go.add_argument("--recording", type=Path, required=True)
    go.add_argument("--base-answers", type=Path, required=True, help="the recording replayed on W's unseeded build")
    go.add_argument("--only", nargs="*")
    sub.add_parser("check")
    args = parser.parse_args()
    if args.command == "check":
        check(json.loads(EVIDENCE.read_text())["seeds"])
        print("every caught seed is caught by a test today's, the modes and the answers selections keep")
        return 0
    work = Path(tempfile.mkdtemp(prefix="cutoff-seeds-"))
    rows = json.loads(EVIDENCE.read_text())["seeds"] if EVIDENCE.exists() else []
    done = {row["id"]: row for row in rows}
    for seed in json.loads(SEEDS.read_text()):
        if args.only and seed["id"] not in args.only:
            continue
        done[seed["id"]] = one(seed, args.worktree.resolve(), args.recording.resolve(), args.base_answers, work)
        print(json.dumps({key: done[seed["id"]].get(key) for key in ("id", "status", "caught_by", "caught_in",
                                                                    "changed_cases", "seconds")}), flush=True)
        order = [seed["id"] for seed in json.loads(SEEDS.read_text())]
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_text(json.dumps({"worktree_commit": subprocess.run(
            ["git", "-C", str(args.worktree), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
            "seeds": [done[i] for i in order if i in done]}, indent=1) + "\n")
    print(f"logs in {work}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
