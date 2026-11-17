#!/usr/bin/env python3
"""Plant one seeded bug per behaviour in a temporary COPY of cloud-tm-job.sh (argv[1], default the installed one) and run the test file against it."""
import os, subprocess, sys, tempfile

M = "/home/seyran/code/manage-agents"
SRC = open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(M, "cloud-tm-job.sh")).read()
TMP = tempfile.mkdtemp(prefix="tad-seed-")
SEEDS = [
    ("S1-latest", "sort -g | head -n 1", "sort -g | tail -n 1"),
    ("S2-all-deadlines", '[ ${#dls[@]} -gt 0 ] && targs+=(--deadline "$(printf',
     'for x in ${dls[@]+"${dls[@]}"}; do targs+=(--deadline "$x"); done; false && targs+=(--deadline "$(printf'),
    ("S3-no-refuse", '|| refuse "$f ${v:0:40} is not a number of seconds"', '|| { targs+=("$f" "$v"); continue; }'),
    ("S4-budget-from-now", "dls+=($(( T0 + 10#$v )))", "dls+=($(( $(date +%s) + 10#$v )))"),
    ("S5-equals-ignored", "--budget=*|--deadline=*) v=", "--budget=XX*|--deadline=XX*) v="),
]
for name, old, new in SEEDS:
    assert SRC.count(old) == 1, name
    p = os.path.join(TMP, f"{name}.sh")
    open(p, "w").write(SRC.replace(old, new))
    syn = subprocess.run(["bash", "-n", p]).returncode
    r = subprocess.run(["python3", "-I", os.path.join(M, "tools-local/test_cloud_tm_deadline.py")],
                       env=dict(os.environ, CTJ=p), capture_output=True, text=True)
    fails = [x[5:] for x in r.stdout.splitlines() if x.startswith("FAIL ")]
    print(f"{name}: bash -n {syn}, test rc {r.returncode}, failing: {' '.join(fails)}")
    os.remove(p)
