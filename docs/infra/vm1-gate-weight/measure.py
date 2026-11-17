"""vm1-gate-weight MEASURE (read only): VM chain gates over the 72 h before the run, from stage-events.jsonl.
MEASURED: VM gate holds (gate + R13 rerun of one item within 5 min = one hold) and their pairwise overlaps.
ESTIMATE: the wait a one-per-host FIFO (by start time, durations unchanged) would have added; then a count of every
chain gate kind (all of which run on VM1 from 2026-11-18 07:22Z). usage: python3 -I measure.py [stage-events.jsonl]"""
import datetime as dt, json, sys
E = sys.argv[1] if len(sys.argv) > 1 else "/home/seyran/code/manage-agents/stage-events.jsonl"
now = dt.datetime.now(dt.timezone.utc); lo = now - dt.timedelta(hours=72)
P = lambda s: dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
evs = []
for l in open(E):
    try: e = json.loads(l)
    except Exception: continue
    if e.get("stage") in ("gate-start", "gate-end", "gate-cancelled") : evs.append(e)
open_ = {}; iv = []
for e in evs:
    t = P(e["t"]); it = e["item"]; n = e.get("note", "")
    if e["stage"] == "gate-start" and (n.startswith("vm ") or n.startswith("vm-rerun ")):
        open_[it] = (t, n.split()[0])
    elif e["stage"] == "gate-end" and (n.startswith("vm rc") or n.startswith("vm-rerun rc")) and it in open_:
        s, k = open_.pop(it); iv.append((s, t, it, k))
    elif e["stage"] == "gate-cancelled" and it in open_:
        s, k = open_.pop(it); iv.append((s, t, it, k + "(cx)"))
for it, (s, k) in open_.items():
    if s >= lo - dt.timedelta(hours=12): print("OPEN", it, k, s)
iv = [x for x in iv if x[1] >= lo]
# merge each item's gate+rerun into one hold
iv.sort()
print("vm gate runs in 72h:", len(iv), "items:", len({x[2] for x in iv}))
for s, t, it, k in iv: print(f"  {s:%m-%d %H:%M}-{t:%H:%M} {(t-s).total_seconds()/60:6.1f}m {k:10s} {it}")
holds = {}
for s, t, it, k in iv:
    if it in holds and (s - holds[it][-1][1]).total_seconds() < 300: holds[it][-1] = (holds[it][-1][0], t)
    else: holds.setdefault(it, []).append((s, t))
H = sorted((s, t, it) for it, v in holds.items() for s, t in v)
ov = []
for i in range(len(H)):
    for j in range(i+1, len(H)):
        a, b = H[i], H[j]
        o = (min(a[1], b[1]) - max(a[0], b[0])).total_seconds()
        if o > 0: ov.append((o, a, b))
print("overlapping pairs:", len(ov), "total overlap min:", round(sum(o for o, *_ in ov)/60, 1))
for o, a, b in ov: print(f"  {o/60:6.1f}m  {a[2]} {a[0]:%m-%d %H:%M}-{a[1]:%H:%M} | {b[2]} {b[0]:%m-%d %H:%M}-{b[1]:%H:%M}")
# concurrency profile
pts = sorted([(s, 1) for s, t, _ in H] + [(t, -1) for s, t, _ in H])
c = 0; mx = 0; at = {}; prev = None
for t, d in pts:
    if prev is not None: at[c] = at.get(c, 0) + (t - prev).total_seconds()
    c += d; mx = max(mx, c); prev = t
print("max concurrent:", mx, "time at concurrency (min):", {k: round(v/60, 1) for k, v in sorted(at.items())})
# simulate one-per-host FIFO by start time (durations unchanged: ESTIMATE)
free = None; waits = []
for s, t, it in H:
    d = t - s; st = s if free is None or s >= free else free
    waits.append(((st - s).total_seconds(), it)); free = st + d
w = [x for x, _ in waits if x > 0]
print("ESTIMATE one-per-host: gates that wait:", len(w), "of", len(H), "total wait min:", round(sum(w)/60, 1), "max min:", round(max(w or [0])/60, 1), "mean over waiters min:", round(sum(w)/60/max(len(w),1), 1))
for x, it in waits:
    if x > 0: print(f"   wait {x/60:6.1f}m {it}")
# every chain gate kind in the window (gate-start note's first word -> its gate-end)
import collections
c = collections.Counter(); op = {}; dur = collections.defaultdict(list)
for l in open(E):
    try: e = json.loads(l)
    except Exception: continue
    if e.get("stage") not in ("gate-start", "gate-end"): continue
    t = P(e["t"]); k = e.get("note", "").split()[0] if e.get("note") else "?"
    if e["stage"] == "gate-start": op[(e["item"], k)] = t
    elif t >= lo:
        k2 = k.rstrip(":"); s = op.pop((e["item"], k2), None)
        if s: c[k2] += 1; dur[k2].append((t - s).total_seconds() / 60)
print("all chain gate kinds in the window:")
for k, n in c.most_common():
    d = sorted(dur[k]); print(f"  {k:16s} n={n:3d} median={d[len(d)//2]:6.1f}m total={sum(d)/60:6.1f}h")
