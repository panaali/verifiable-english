#!/usr/bin/env python3
"""Plant one seeded bug per behaviour in a temporary COPY of tm-shard.sh (argv[1], default the staged .new-tsa) and run
tools-local/test_tm_shard_actions_120.py --skip-5 against it (TSH=<copy>). The file under test is never edited."""
import os, subprocess, sys, tempfile

M = "/home/seyran/code/manage-agents"
SRC = open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(M, "tm-shard.sh.new-tsa")).read()
TMP = tempfile.mkdtemp(prefix="tsa-seed-")
SEEDS = [  # (id, behaviour, old, new)
    ("B1-setup-best", "(1) SETUP = the records' worst setup", "print(math.ceil(max(setups))", "print(math.ceil(min(setups))"),
    ("B2-records-spm-unused", "(1)/(2) the records' p90 per-mutant time sizes the parts",
     "(( rspm > ${TM_SHARD_ACTIONS_SPM:-26} ))", "(( rspm > 999999 ))"),
    ("B3-no-unsharded-budget", "(3) the unsharded Actions part gets --budget", "&& { orig+=($budget);", "&& { :;"),
    ("B4-no-budget-cut", "(3) a budget over LIMIT - PRE is cut", "(( b > lim - pre )) && b=$(( lim - pre ))", ":"),
    ("B6-malformed-budget-dropped", "(3) a malformed TM_PART_BUDGET still gives a budget (fails closed)",
     "[[ $b == <-> ]] || b=$(( lim - pre - ${TM_SHARD_ACTIONS_POST:-600} ))", "[[ $b == <-> ]] || return 1"),
    ("B5-old-lines", "(2) the part line 5,100 s is the default HARD/CANCEL",
     "TM_SHARD_ACTIONS_HARD=${TM_SHARD_ACTIONS_HARD:-$aline} TM_SHARD_ACTIONS_CANCEL=${TM_SHARD_ACTIONS_CANCEL:-$aline}",
     "TM_SHARD_ACTIONS_HARD=${TM_SHARD_ACTIONS_HARD:-5400} TM_SHARD_ACTIONS_CANCEL=${TM_SHARD_ACTIONS_CANCEL:-6600}"),
]
for name, what, old, new in SEEDS:
    assert SRC.count(old) == 1, name
    p = os.path.join(TMP, f"{name}.sh")
    open(p, "w").write(SRC.replace(old, new))
    syn = subprocess.run(["zsh", "-n", p]).returncode
    r = subprocess.run([sys.executable, "-I", os.path.join(M, "tools-local/test_tm_shard_actions_120.py"), "--skip-5"],
                       env=dict(os.environ, TSH=p), capture_output=True, text=True)
    fails = [x.strip()[5:].split("  [")[0] for x in r.stdout.splitlines() if x.startswith("  FAIL ")]
    print(f"{name} ({what}): zsh -n {syn}, test rc {r.returncode}, {len(fails)} failing: " + " | ".join(fails))
    os.remove(p)
