"""Seeded bugs for oseq-opus-off-main: each mutates a /tmp copy of pick-claude-account.sh.new-oseqmain and runs one test of
tools-local/test_pick_oseq_opus_main.py against it (must FAIL). usage: python3 -I seed_run.py <manage-agents dir> <out json>"""
import json, os, subprocess, sys, tempfile
MA, OUT = sys.argv[1], sys.argv[2]
SRC = os.path.join(MA, "pick-claude-account.sh.new-oseqmain")
GUARD = 'if os.environ.get("PICK_OSEQ_OPUS") and (a == "main" or os.path.basename(d) == "claude-panaali2"):'
SEEDS = [
    ("check removed", GUARD, 'if False:', "test_1_no_avoid_main_only"),
    ("check only with PICK_AVOID empty", GUARD,
     'if os.environ.get("PICK_OSEQ_OPUS") and not os.environ.get("PICK_AVOID", "").strip() and (a == "main" or os.path.basename(d) == "claude-panaali2"):',
     "test_3_rcx_main_pace_lift"),
    ("config-dir match dropped", GUARD, 'if os.environ.get("PICK_OSEQ_OPUS") and a == "main":', "test_1_config_dir_of_main"),
    ("relwant not cleared", "relwant = False; no(a, f, w, \"held out (PICK_OSEQ_OPUS", "no(a, f, w, \"held out (PICK_OSEQ_OPUS",
     "test_3_released_row"),
]
src = open(SRC).read(); rows = []
for name, old, new, test in SEEDS:
    assert src.count(old) == 1, name
    fd, p = tempfile.mkstemp(prefix="seed-oseqmain-", suffix=".sh"); os.write(fd, src.replace(old, new).encode()); os.close(fd)
    os.chmod(p, 0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PICK_", "RCX_"))}
    env.update(PICK_SCRIPT=p, LIVE_PICK_SCRIPT=SRC)
    r = subprocess.run([sys.executable, "-I", os.path.join(MA, "tools-local/test_pick_oseq_opus_main.py"), "OseqOpusOffMain." + test], env=env, capture_output=True, text=True, cwd=os.path.join(MA, "tools-local"))
    os.unlink(p)
    rows.append(dict(file="pick-claude-account.sh.new-oseqmain", language="shell (embedded python)", seed=name, test=test,
                     rc=r.returncode, caught=r.returncode != 0, tail=r.stderr.strip().splitlines()[-1:]))
json.dump(rows, open(OUT, "w"), indent=1); print(json.dumps([(x["seed"], x["test"], x["caught"]) for x in rows]))
