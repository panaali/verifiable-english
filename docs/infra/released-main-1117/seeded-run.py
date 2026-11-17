import os, subprocess, sys, shutil
M = "/home/seyran/code/manage-agents"
PK, PC = f"{M}/pick-claude-account.sh.new-rel", f"{M}/tools-local/pick_critical.py.new-released-main"
T = f"{M}/tools-local/test_pick_released_main.py"
seeds = [  # (id, file, old, new, test)
 ("S1-pace-bound", PK, 'if w > pl - 4: return (False, f"week {w} > PICK_MAIN_PACE line {pl:.1f} - 4")', 'if w > pl - 3: return (False, f"week {w} > PICK_MAIN_PACE line {pl:.1f} - 4")', "ReleasedMain.test_2_pace_minus_3_avoided"),
 ("S2-rise-bound", PK, 'if wr[0] >= 5: return (False, f"week +{wr[0]} pt in 5 h >= 5")\n    return relhold()', 'if wr[0] >= 6: return (False, f"week +{wr[0]} pt in 5 h >= 5")\n    return relhold()', "ReleasedMain.test_3_rise_5_avoided"),
 ("S3-giveback-drops-all", PK, "                if hs[me] <= 0: del hs[me]\n                hwrite(relmark, hi, hs)", "                hs = {}\n                hwrite(relmark, hi, hs)", "ReleasedMain.test_6_same_row_second_session_joins"),
 ("S4-dead-pid-kept", PK, "        if n > 0 and pid_alive(p): hs[p] = hs.get(p, 0) + n", "        if n > 0: hs[p] = hs.get(p, 0) + n", "ReleasedMain.test_7_dead_pid_marker_cleared"),
 ("S5-other-row-joins", PK, "            if hs and hi != row:", "            if hs and hi == \"?\":", "ReleasedMain.test_5_second_released_row_avoided"),
 ("S6-shell-keeps-row-main", PK, "[ -n \"$relmain\" ] && rv=(${rv:#main});", "", "ReleasedMain.test_1_granted"),
 ("S7-rank-order-reversed", PC, "        if k < mk and (best is None or k < best):", "        if k > mk and (best is None or k < best):", "ReleasedMain.test_rank_order"),
]
for sid, f, old, new, test in seeds:
    src = open(f).read(); assert src.count(old) == 1, sid
    d = f"/tmp/relm-seed/{sid}"; os.makedirs(d, exist_ok=True)
    mp, mc = f"{d}/pick.sh", f"{d}/pick_critical.py"
    shutil.copy(PK, mp); shutil.copy(PC, mc)
    open(mp if f == PK else mc, "w").write(src.replace(old, new))
    r = subprocess.run([sys.executable, "-I", T, test], env=dict(os.environ, PICK_SCRIPT=mp, PCF_SCRIPT=mc), capture_output=True, text=True, timeout=300)
    fails = [l for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
    print(f"{sid} file={os.path.relpath(f, M)} test={test} rc={r.returncode} {'CAUGHT' if r.returncode else 'MISSED'} {fails[:1]}")
