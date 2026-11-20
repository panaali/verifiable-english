import os, subprocess, sys, json
M = "/home/seyran/code/manage-agents"; S = ".new-usagew2"; T = M + "/tools-local"
base = {"PICK_SCRIPT": f"{M}/pick-claude-account.sh{S}", "RESET_FRESH_SCRIPT": f"{T}/reset_fresh.py{S}", "EG_SCRIPT": f"{T}/endgame.py{S}",
        "BURNDOWN_SCRIPT": f"{T}/burndown.py{S}", "REVIEW_AB_RULE_SCRIPT": f"{T}/review-ab-rule.py{S}"}
seeds = [
 ("S8", "EG_SCRIPT", "for y in (at.year - 1, at.year, at.year + 1):", "for y in (at.year,):", "endgame year: at.year only", ["test_usage_reset_fresh.py"]),
 ("S9", "PICK_SCRIPT", "    hours = max(168.0 if hw is None else hw, 1)",
  '    try: reset = datetime.datetime.strptime(f"{now.year} {r2}", "%Y %a_%b%d_%H:%M").replace(tzinfo=tz)\n    except ValueError: reset = now + datetime.timedelta(days=7)\n    hours = max((reset - now).total_seconds() / 3600, 1)',
  "picker hours to the weekly reset: own year-less parse again", ["test_usage_reset_fresh.py"]),
 ("S10", "RESET_FRESH_SCRIPT", "    h = endgame.hours_to(r, at)\n    return None",
  '    try: h = (datetime.datetime.strptime(f"{at.year} {r}", "%Y %a_%b%d_%H:%M").replace(tzinfo=endgame.TZ) - at).total_seconds() / 3600\n    except ValueError: h = None\n    return None',
  "reset_fresh: own year-less parse", ["test_usage_reset_fresh.py"]),
 ("S11", "BURNDOWN_SCRIPT", "hr_ = _endgame().hours_to(rs, NOW)", "hr_ = _endgame().hours_to(rs, NOW.replace(year=2026))", "burndown: year 2026", ["test_burndown.py"]),
 ("S12", "REVIEW_AB_RULE_SCRIPT", "h = endgame.hours_to(f[6], now) if", "h = endgame.hours_to(f[6], now.replace(tzinfo=endgame.TZ)) if", "review-ab-rule: field read as UTC", ["test_review_ab_rule.py"]),
]
out = []
for sid, var, a, b, what, tests in seeds:
    src = open(base[var]).read(); assert src.count(a) == 1, (sid, src.count(a))
    ext = ".sh" if base[var].endswith(".sh" + S) else ".py"
    mp = f"/tmp/uw2/mut/{sid}{ext}"; open(mp, "w").write(src.replace(a, b))
    env = dict(os.environ, **base); env[var] = mp
    fails = []
    for t in tests:
        r = subprocess.run([sys.executable, "-I", f"{T}/{t}"], env=env, capture_output=True, text=True, cwd=T)
        fails += [l.split(" (")[0][6:] for l in r.stderr.splitlines() if l.startswith(("FAIL: ", "ERROR:"))]
    out.append({"id": sid, "file": base[var].replace("/home/seyran/code/", ""), "change": what, "failing": fails})
    os.remove(mp)
for o in out: print(json.dumps(o))
