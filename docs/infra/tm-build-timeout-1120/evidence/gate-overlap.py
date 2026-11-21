"""Timeout share of the 11-16..19 ve-cloud-2 parts grouped by gate overlap and by the limit in force (reads corr.out)."""
import re, collections
b = collections.defaultdict(lambda: [0, 0, 0, []])
for l in open('/home/seyran/code/manage-agents/reviews/tm-build-timeout-1120/evidence/corr.out'):
    m = re.match(r'(2026111[6-9]\S+) p\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+) \S+ g(\S+) tm(\S+) sel(\S+)', l)
    if not m:
        continue
    g = float(m[6]); k = ('gate>=0.5' if g >= 0.5 else 'gate<0.2' if g < 0.2 else 'gate 0.2-0.5') + (' @3600' if '1620Z' in m[1] else ' @1800')
    b[k][0] += int(m[4]); b[k][1] += int(m[5]); b[k][2] += 1; b[k][3].append(g)
for k, v in sorted(b.items()):
    print(k, f"parts {v[2]} judged {v[0]} TO {v[1]} tries {v[0] + v[1]} TO share {v[1] / (v[0] + v[1]):.2f} overlap {min(v[3]):.2f}-{max(v[3]):.2f}")
