#!/usr/bin/env python3
"""Per-pool trust-mutant throughput from the tm-nightly part records of the last 7 days.

Read only. Usage: python3 -I estimate_calc.py [MANAGE_AGENTS_DIR]
For each sweep dir test-skip/nightly/parts-<stamp> with stamp >= 20261113, each part-<k>.json:
  where, seconds (part wall), jobs, and its rows by status.
judged = KILLED + SURVIVOR + INVALID + ALLOWED (a verdict that needs no new try);
bto = UNKNOWN whose detail says the lake build did not finish (build timeout);
unk = other UNKNOWN; notrun = NOT RUN.
Throughput = judged per part-hour (sum judged / sum part seconds * 3600) per pool, and per pool-hour of
sweep wall (first part start to last part end is not recorded, so the sweep wall comes from steps_wall.mutants).
"""
import collections, glob, json, os, sys

root = sys.argv[1] if len(sys.argv) > 1 else "/home/seyran/code/manage-agents"
nd = os.path.join(root, "test-skip", "nightly")
agg = collections.defaultdict(lambda: collections.Counter())
per_sweep = []
for d in sorted(glob.glob(os.path.join(nd, "parts-*"))):
    stamp = d.rsplit("parts-", 1)[1]
    if stamp < "20261113":
        continue
    sw = collections.defaultdict(collections.Counter)
    for f in sorted(glob.glob(os.path.join(d, "part-*.json"))):
        try:
            p = json.load(open(f))
        except Exception as e:  # unreadable part: report, never guess
            print("unreadable", f, e)
            continue
        where = p.get("where") or "?"
        c = sw[where]
        c["parts"] += 1
        c["seconds"] += int(p.get("seconds") or 0)
        c["jobs:%s" % p.get("jobs")] += 1
        for m in p.get("mutants") or []:
            st = m.get("status")
            det = (m.get("detail") or "")
            if st in ("KILLED", "SURVIVOR", "INVALID", "ALLOWED"):
                c["judged"] += 1
            elif st == "UNKNOWN" and "did not finish" in det:
                c["bto"] += 1
            elif st == "UNKNOWN":
                c["unk"] += 1
            else:
                c["notrun"] += 1
    for w, c in sw.items():
        agg[w].update(c)
        per_sweep.append((stamp, w, dict(c)))

print("== per sweep, per pool")
for stamp, w, c in per_sweep:
    h = c.get("seconds", 0) / 3600
    rate = c.get("judged", 0) / h if h else 0
    print(f"{stamp} {w:12s} parts={c.get('parts',0):3d} part_h={h:7.1f} judged={c.get('judged',0):5d} "
          f"bto={c.get('bto',0):4d} unk={c.get('unk',0):3d} notrun={c.get('notrun',0):4d} judged/part_h={rate:5.1f} "
          f"bto_rate={c.get('bto',0)/max(1,c.get('judged',0)+c.get('bto',0)+c.get('unk',0)):.2f}")
print("== 7-day totals per pool")
for w, c in sorted(agg.items()):
    h = c["seconds"] / 3600
    tried = c["judged"] + c["bto"] + c["unk"]
    print(f"{w:12s} parts={c['parts']:4d} part_h={h:8.1f} judged={c['judged']:6d} bto={c['bto']:5d} unk={c['unk']:4d} "
          f"notrun={c['notrun']:5d} judged/part_h={c['judged']/h if h else 0:5.1f} tried/part_h={tried/h if h else 0:5.1f} "
          f"bto_rate={c['bto']/tried if tried else 0:.2f} jobs={ {k:v for k,v in c.items() if k.startswith('jobs:')} }")

# Sweep wall (MEASURED, nightly.log): "pools remote" start line to "all N part(s) returned" line.
WALL = {"20261113T0600Z": ("06:02", "15:52"), "20261114T0600Z": ("06:05", "15:51"), "20261115T0600Z": ("06:04", "15:54"),
        "20261116T0600Z": ("06:04", "15:54"), "20261117T0600Z": ("06:08", "16:04"), "20261119T0727Z": ("07:30", "17:20")}
def hours(a, b):
    (h1, m1), (h2, m2) = map(int, a.split(":")), map(int, b.split(":"))
    return (h2 * 60 + m2 - h1 * 60 - m1) / 60
print("== judged per sweep wall-hour, all remote pools together")
sweep_rate = {}
for stamp, (a, b) in WALL.items():
    j = sum(c.get("judged", 0) for st, w, c in per_sweep if st == stamp)
    sweep_rate[stamp] = j / hours(a, b)
    print(f"{stamp} wall_h={hours(a,b):5.2f} judged={j:4d} judged/h={sweep_rate[stamp]:5.1f}")

# ESTIMATE: one complete fresh sweep at main, remote pools only.
IDS, HEAVY = 8719, 777          # plan-main-09bea0972d.json; heavy = files in ../tm-build-timeout-1120/evidence/heavy20.json
LIGHT = IDS - HEAVY
light_lo_rate = sweep_rate["20261115T0600Z"]   # ve-cloud-2 only (+0 Actions parts), light-dominated
light_c2_rate = sweep_rate["20261114T0600Z"]   # ve-cloud-2 + 2 Actions parts
light_hi_rate = sweep_rate["20261113T0600Z"]   # ve-cloud-2 + ve-cloud-3
SLOTS = 3                                       # tm-nightly: up to 3 parts at once
HEAVY_PH = (1.5, 5.0)                           # heavy judged per part-hour at --jobs 2: ESTIMATE (tm-build-timeout-1120 sec. 4)
print("== ESTIMATE (hours of sweep running, back to back)")
for name, lr in (("cloud-2+cloud-3 (cloud-3 unreachable today)", light_hi_rate),
                 ("cloud-2 (+Actions) today, best", light_c2_rate), ("cloud-2 today, worst", light_lo_rate)):
    lh = LIGHT / lr
    hh_fast, hh_slow = HEAVY / (HEAVY_PH[1] * SLOTS), HEAVY / (HEAVY_PH[0] * SLOTS)
    print(f"{name:45s} light {lh:6.1f} h + heavy {hh_fast:5.1f}-{hh_slow:5.1f} h = "
          f"{(lh+hh_fast)/24:4.1f}-{(lh+hh_slow)/24:4.1f} days")
print(f"one --once launch (36000 s budget) judges {light_lo_rate*10:.0f}-{light_hi_rate*10:.0f} of {IDS} ids "
      f"({light_lo_rate*10/IDS:.0%}-{light_hi_rate*10/IDS:.0%})")
