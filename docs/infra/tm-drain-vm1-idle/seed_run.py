"""Seeded bugs for tm-drain-vm1-idle: each seed is one exact find/replace in a /tmp copy of the staged
manage-agents/tm-nightly.sh.new-tmidle, run with TMN_SH=<copy> python3 -I tools-local/test_tm_drain_vm1_idle.py.
The staged file is never edited. usage: python3 -I seed_run.py <staged tm-nightly.sh> <test file> <out json>"""
import json
import os
import re
import subprocess
import sys
import tempfile

SEEDS = [
    ("S1", "the reserve is ignored (the gate lends every core under nproc - load)",
     "igate(){ local n=${TM_IDLE_NPROC:-$(nproc)} r=${TM_IDLE_RESERVE:-8} l ma",
     "igate(){ local n=${TM_IDLE_NPROC:-$(nproc)} r=0 l ma"),
    ("S2", "the memory gate is dropped",
     "[[ $ma == <-> ]] && (( ma >= ${TM_IDLE_MEM:-24} + ${TM_IDLE_MEM_SPARE:-8} )) ||",
     "true ||"),
    ("S3", "the local part drops the first trust_mutants argument after `--` (not a remote host's command)",
     'ta=("${(@)cmd[$(( ${cmd[(ie)--]} + 1 )),-1]}" "$@"',
     'ta=("${(@)cmd[$(( ${cmd[(ie)--]} + 2 )),-1]}" "$@"'),
    ("S4", "no nice/ionice on the local trust_mutants run",
     "$sc --unit=$u nice -n 19 ionice -c 2 -n 7 ${=TM_IDLE_TM",
     "$sc --unit=$u ${=TM_IDLE_TM"),
    ("S5", "no CPU weight or quota on the local scope",
     "-p CPUWeight=${TM_IDLE_WEIGHT:-10} -p CPUQuota=$(( co * 100 ))%",
     "-p CPUWeight=100"),
    ("S6", "the gate is read once: after one open gate every later part goes local whatever the load",
     "        if igate; then j=$i; return 0; fi;",
     "        if [ -n \"$ionce\" ] || igate; then ionce=1; j=$i; return 0; fi;"),
    ("S7", "a failed local setup still runs trust_mutants",
     "  if (( rc == 0 )); then left=$(( left - ss ))",
     "  if true; then left=$(( left - ss ))"),
    ("S8", "the local record does not say where it ran",
     "d[\"where\"]=\"vm1-idle\"",
     "d[\"where\"]=None"),
]


def main(staged, test, out):
    text = open(staged).read()
    res = []
    for sid, bug, find, repl in SEEDS:
        assert text.count(find) == 1, (sid, text.count(find))
        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as f:
            f.write(text.replace(find, repl))
        p = subprocess.run([sys.executable, "-I", test], env={**os.environ, "TMN_SH": f.name},
                           capture_output=True, text=True, timeout=1800)
        os.unlink(f.name)
        failing = sorted(set(re.findall(r"^(?:FAIL|ERROR): (test_\w+)", p.stderr, re.M)))
        res.append({"id": sid, "bug": bug, "file": "manage-agents/tm-nightly.sh.new-tmidle", "find": find, "replace": repl,
                    "rc": p.returncode, "failing_tests": failing,
                    "test": "tools-local/test_tm_drain_vm1_idle.py " + ", ".join(f"DrainIdle.{t}" for t in failing),
                    "caught": p.returncode != 0 and bool(failing)})
        print(sid, p.returncode, failing, flush=True)
    json.dump({"item": "tm-drain-vm1-idle",
               "note": "Shell only, in manage-agents (no Lean, Python or Rust of this VE repo changed). " + __doc__.split("\n")[1],
               "mutants": res}, open(out, "w"), indent=1)
    return 0 if all(r["caught"] for r in res) else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
