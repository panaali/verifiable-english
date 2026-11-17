"""Seeded bugs for pick-main-slot-mark: each mutates a /tmp copy of pick-claude-account.sh.new-pickw and runs one test of
tools-local/test_pick_main_rank.py.new-pickw against it (must FAIL); the unmutated copy must PASS the same test.
usage: python3 -I seed_run.py <manage-agents dir> <out json>"""
import json, os, subprocess, sys, tempfile
MA, OUT = sys.argv[1], sys.argv[2]
SRC = os.path.join(MA, "pick-claude-account.sh.new-pickw")
TEST = os.path.join(MA, "tools-local/test_pick_main_rank.py.new-pickw")
GATE = "if critmain and r1on and 0 < mcap == int(running.get(d, 0)) < 3: r1x = r1_ if r1_[0] else r1ok(w)"
SEEDS = [  # (name, language, old, new, test)
    ("cffall cap refusal does not mark", "shell", '  [[ "$b" == *"main: main worker cap"* ]] && mmark mark  #', '  true  #',
     "test_crit_fallback_cap_refusal_marks"),
    ("cffall marks on any refusal", "shell", '  [[ "$b" == *"main: main worker cap"* ]] && mmark mark  #', '  mmark mark  #',
     "test_crit_fallback_other_refusal_or_rank4_no_mark"),
    ("no rank-1 extra slot", "embedded python", GATE, "if False: r1x = r1_",
     "test_rank1_crit_fallback_third_slot"),
    ("extra slot not limited to mcap + 1", "embedded python", GATE,
     "if critmain and r1on and 0 < mcap <= int(running.get(d, 0)) < 3: r1x = r1_ if r1_[0] else r1ok(w)",
     "test_rank1_slot_only_one_over_the_cap"),
    # review F1: the slot is the 3rd main slot at most; without the bound a cap of 3 (5-h < 40) gives a 4th main session
    ("extra slot past the 3rd main session (bound dropped)", "embedded python", GATE,
     "if critmain and r1on and 0 < mcap == int(running.get(d, 0)): r1x = r1_ if r1_[0] else r1ok(w)",
     "test_rank1_slot_never_a_fourth_main_session"),
    ("extra slot past the 3rd main session (bound off by one)", "embedded python", GATE,
     "if critmain and r1on and 0 < mcap == int(running.get(d, 0)) < 4: r1x = r1_ if r1_[0] else r1ok(w)",
     "test_rank1_slot_sweep_never_past_the_third_main_session"),
    ("extra slot skips the rank-1 rule (pace - 4)", "embedded python", GATE,
     "if critmain and r1on and 0 < mcap == int(running.get(d, 0)) < 3: r1x = (True, \"\")",
     "test_rank1_slot_refused_over_pace_minus_4"),
    # review F2: the one-row marker alone (r1hold), not the whole rule as in the seed above
    ("extra slot skips the one-row marker only", "embedded python", "    ok, why_ = r1hold()\n", "    ok, why_ = True, \"\"\n",
     "test_rank1_slot_one_row_at_a_time"),
    ("extra slot not only for the critical fallback", "embedded python", GATE,
     "if r1on and 0 < mcap == int(running.get(d, 0)) < 3: r1x = r1_ if r1_[0] else r1ok(w)",
     "test_slot_only_for_rank1_critical_fallback"),
    ("granted slot not recorded (r1d): holder marker given back", "embedded python", "            r1_ = r1x; r1d = d\n",
     "            r1_ = r1x\n", "test_rank1_crit_fallback_third_slot"),
]


def run(script, test):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PICK_", "PCF_", "RCX_"))}
    env.update(PICK_SCRIPT=script)
    return subprocess.run([sys.executable, "-I", TEST, "CritFallbackSlot." + test], env=env, capture_output=True, text=True,
                          cwd=os.path.join(MA, "tools-local"))


src = open(SRC).read(); rows = []
for name, lang, old, new, test in SEEDS:
    assert src.count(old) == 1, name
    clean = run(SRC, test)
    fd, p = tempfile.mkstemp(prefix="seed-pickw-", suffix=".sh"); os.write(fd, src.replace(old, new).encode()); os.close(fd)
    os.chmod(p, 0o755)
    r = run(p, test)
    os.unlink(p)
    rows.append(dict(file="pick-claude-account.sh.new-pickw", language=lang, seed=name, test="CritFallbackSlot." + test,
                     clean_rc=clean.returncode, rc=r.returncode, caught=r.returncode != 0 and clean.returncode == 0,
                     tail=r.stderr.strip().splitlines()[-1:]))
json.dump(rows, open(OUT, "w"), indent=1); print(json.dumps([(x["seed"], x["test"], x["caught"]) for x in rows], indent=0))
