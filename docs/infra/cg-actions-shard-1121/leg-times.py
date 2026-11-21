"""Wall minutes of the train's blocking arm shard legs (gha-arm/gha-arm-shard.jsonl rows mode blocking, wall_s set),
rows with 2026-11-14T00:00Z <= t < 2026-11-21T11:00Z."""
import json, statistics as st, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
b = [r for r in rows if r.get("mode") == "blocking" and "2026-11-14" <= r.get("t", "") < "2026-11-21T11:00Z" and r.get("wall_s")]
w = sorted(r["wall_s"] / 60 for r in b)
q = lambda p: w[min(len(w) - 1, int(p * len(w)))]
print(f"legs {len(b)}; labels cand-* {sum(1 for r in b if str(r.get('label','')).startswith('cand-'))}; merged",
      {m: sum(1 for r in b if r.get('merged') == m) for m in sorted(set(str(r.get('merged')) for r in b))})
print("wall min: median %.1f p75 %.1f p90 %.1f p95 %.1f max %.1f" % (st.median(w), q(.75), q(.9), q(.95), w[-1]))
print("legs over 75 min: %d (%.1f%%); over 90 min: %d" % (sum(x > 75 for x in w), 100 * sum(x > 75 for x in w) / len(w), sum(x > 90 for x in w)))
print("last 8 legs: median %.1f" % st.median(r["wall_s"] / 60 for r in b[-8:]))
