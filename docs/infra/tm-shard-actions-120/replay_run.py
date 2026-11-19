#!/usr/bin/env python3
"""Replay the real 0600Z Actions dispatches (p3: 60 mutants at 06:12Z; p4: 30 at 08:20Z) against the real export records
(read-only), through tools-local/test_tm_shard_actions_120.py's dispatch() stubs (room 40, busy 0), for the staged and the
live tm-shard.sh; also prints each file's records reading at those times. Writes nothing outside a private temp dir.
usage: python3 -I docs/infra/tm-shard-actions-120/replay_run.py [STAGED] [LIVE]"""
import calendar, importlib.util, re, shutil, subprocess, sys, tempfile, time

M = "/home/seyran/code/manage-agents"
X = "/home/seyran/code/ve-github-export"
STAGED = sys.argv[1] if len(sys.argv) > 1 else f"{M}/tm-shard.sh.new-tsa"
LIVE = sys.argv[2] if len(sys.argv) > 2 else f"{M}/tm-shard.sh"
spec = importlib.util.spec_from_file_location("tsa", f"{M}/tools-local/test_tm_shard_actions_120.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
d = tempfile.mkdtemp(prefix="tsa-replay-")
try:
    for name, f in (("staged", STAGED), ("live", LIVE)):
        for item, n, at in (("p3", 60, "06:12Z"), ("p4", 30, "08:20Z")):
            now = calendar.timegm(time.strptime(f"2026-11-17T{at}", "%Y-%m-%dT%H:%MZ"))
            rc, dr, lg, _ = T.dispatch(d, f, n, X=X, extra={"CLOUD_NOW": str(now)}, tag=f"{name}-{item}")
            print(f"{name} {item} ({n} mutants, records as of {at}): exit {rc}, {len(dr)} dispatched")
            for line in lg:
                print(f"    {line}")
            print(f"    part args: {dr[0].split(' -- ', 1)[1] if dr and ' -- ' in dr[0] else '-'}")
    for at in ("06:12Z", "08:20Z"):
        now = calendar.timegm(time.strptime(f"2026-11-17T{at}", "%Y-%m-%dT%H:%MZ"))
        m = re.search(r"arecs\(\)\{.*?<<.PY.\n(.*?)\nPY\n", open(STAGED).read(), re.S)
        o = subprocess.run([sys.executable, "-I", "-", X, str(now), "20", "168", "7200", "300", "400"], input=m.group(1),
                           capture_output=True, text=True).stdout.split()
        print(f"staged records reading at {at} (setup worst, runs, per-mutant p90, readings): {o}")
finally:
    shutil.rmtree(d, ignore_errors=True)
