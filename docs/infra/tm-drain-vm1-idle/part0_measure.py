"""Part 0 of tm-drain-vm1-idle: timeouts vs verdicts of the trust-mutant nightly, per host and per hour, from its records.

usage: python3 -I part0_measure.py <test-skip dir> <cloud-jobs dir> <sar dir> [--since STAMP] [--end ISO]
Reads (never writes) the nightly's part records (nightly/parts-<stamp>/parts.tsv and part-<k>.json), its run logs
(nightly-run-<stamp>.log: setup seconds, clones, disk-low evictions), the Actions job records (cloud-jobs/*/job.json: which
part an Actions job wrote) and saved `sar -q` 5-min loads (<sar dir>/<host>.txt: "ISO load5" per line). A verdict is
KILLED, SURVIVOR, INVALID or ALLOWED; a build timeout is an UNKNOWN whose detail says "did not finish in N s
(--build-timeout)" (tm-nightly.py build_timeout). Prints markdown tables to stdout.
"""
import bisect
import calendar
import collections
import glob
import json
import os
import re
import statistics
import sys
import time

VERDICT = ("KILLED", "SURVIVOR", "INVALID", "ALLOWED")
BT = re.compile(r"did not finish in ([0-9.]+) s \(--build-timeout\)")
SETUP = re.compile(r"\[cloud2@(\S+) (\d\d:\d\d:\d\d)Z\] trust_mutants on (\S+) \([^)]*\), slot \d+, commit \w+, setup (\d+)s: "
                   r".*?--only (M\d+)")


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime(t))


def epoch(s):
    return calendar.timegm(time.strptime(s[:16], "%Y-%m-%dT%H:%M"))


def loads(sar_dir):
    out = {}
    for p in glob.glob(os.path.join(sar_dir, "*.txt")):
        rows = sorted((epoch(a), float(b)) for a, b in (ln.split() for ln in open(p) if len(ln.split()) == 2))
        out[os.path.basename(p)[:-4]] = ([t for t, _ in rows], [v for _, v in rows])
    return out


def load_at(series, host, t):
    s = series.get("vm1" if host in ("vm1", "VM1") else host)
    if not s:
        return None
    i = bisect.bisect_right(s[0], t) - 1
    return s[1][i] if i >= 0 and t - s[0][i] <= 1200 else None


def load_during(series, host, t0, t1):
    """The mean of the host's 5-min load samples taken while the part ran (its own jobs included), else None."""
    s = series.get("vm1" if host in ("vm1", "VM1") else host)
    if not s:
        return None
    v = s[1][bisect.bisect_left(s[0], t0):bisect.bisect_right(s[0], t1)]
    return sum(v) / len(v) if v else None


def actions_dests(cj):
    out = {}
    for p in glob.glob(os.path.join(cj, "*", "job.json")):
        try:
            d = json.load(open(p))
        except (OSError, ValueError):
            continue
        if d.get("pool") == "actions" and d.get("dest"):
            out[os.path.realpath(d["dest"])] = d.get("job")
    return out


def parts(ts_dir, cj, since):
    acts = actions_dests(cj)
    for pdir in sorted(glob.glob(os.path.join(ts_dir, "nightly", "parts-*"))):
        stamp = os.path.basename(pdir)[6:]
        if stamp < since:
            continue
        log = os.path.join(ts_dir, f"nightly-run-{stamp}.log")
        text = open(log, errors="replace").read() if os.path.exists(log) else ""
        setups = {m[5]: (m[1], int(m[4])) for m in SETUP.finditer(text)}  # first id -> (host, setup s): the last one
        for ln in open(os.path.join(pdir, "parts.tsv")):
            f = ln.rstrip("\n").split("\t")
            if len(f) < 8:
                continue
            k, n, rc, t0, t1, path, first = f[0], int(f[1]), int(f[2]), int(f[3]), int(f[4]), f[5], f[6]
            try:
                d = json.load(open(path))
            except (OSError, ValueError):
                d = None
            host = (d or {}).get("where") or ("actions" if os.path.realpath(path) in acts else
                                              setups.get(first, ("none",))[0] if d is None else "vm1")
            c = collections.Counter()
            tries = []  # (id, "timeout" | "verdict" | "unknown"): the same id at the same head is the same mutant
            tval = set()
            files = collections.Counter()
            for m in (d or {}).get("mutants") or []:
                st = m.get("status")
                b = BT.search(str(m.get("raw_detail") or m.get("detail") or "")) if st == "UNKNOWN" else None
                if b or st in VERDICT or st == "UNKNOWN":
                    tries.append((m.get("id"), "timeout" if b else "verdict" if st in VERDICT else "unknown"))
                if b:
                    c["timeout"] += 1
                    tval.add(float(b[1]))
                    files[m.get("file")] += 1
                elif st in VERDICT:
                    c["verdict"] += 1
                elif st == "UNKNOWN":
                    c["unknown"] += 1
                else:
                    c["notrun"] += 1
            yield dict(stamp=stamp, k=k, n=n, rc=rc, t0=t0, t1=t1, host=host, rec=d is not None, c=c, tval=tval,
                       files=files, tries=tries, head=(d or {}).get("head"), setup=setups.get(first, (None, None))[1] if host != "actions" else None,
                       jobs=(d or {}).get("jobs"))


def share(c):
    j = c["verdict"] + c["timeout"]
    return f"{100 * c['timeout'] / j:.0f}%" if j else "-"


def main(argv):
    ts_dir, cj, sar_dir = argv[:3]
    since = argv[argv.index("--since") + 1] if "--since" in argv else "20261112T0600Z"
    end = epoch(argv[argv.index("--end") + 1]) if "--end" in argv else None
    series = loads(sar_dir)
    ps = list(parts(ts_dir, cj, since))
    for p in ps:
        p["load"] = load_at(series, p["host"], p["t0"])
        p["during"] = load_during(series, p["host"], p["t0"], p["t1"])
    print("## A. Per host and UTC hour of the part's start (parts with a record)\n")
    print("| hour (UTC) | host | parts | verdicts | build timeouts | timeout share | other UNKNOWN | NOT RUN | 5-min load at start"
          " (mean) | load during the part (mean) | setup s (each) | timeout value s |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    by = collections.defaultdict(list)
    for p in ps:
        if p["rec"]:
            by[(iso(p["t0"])[:13], p["host"])].append(p)
    for (h, host), g in sorted(by.items()):
        c = sum((p["c"] for p in g), collections.Counter())
        ls = [p["load"] for p in g if p["load"] is not None]
        du = [p["during"] for p in g if p["during"] is not None]
        dus = f"{statistics.mean(du):.0f}" if du else "-"
        st = [str(p["setup"]) for p in g if p["setup"] is not None]
        tv = sorted(set().union(*(p["tval"] for p in g)))
        print(f"| {h}Z | {host} | {len(g)} | {c['verdict']} | {c['timeout']} | {share(c)} | {c['unknown']} | {c['notrun']} | "
              f"{statistics.mean(ls):.0f} | {dus} | {', '.join(st) or '-'} | {', '.join(f'{v:g}' for v in tv) or '-'} |"
              if ls else
              f"| {h}Z | {host} | {len(g)} | {c['verdict']} | {c['timeout']} | {share(c)} | {c['unknown']} | {c['notrun']} | - | {dus} | "
              f"{', '.join(st) or '-'} | {', '.join(f'{v:g}' for v in tv) or '-'} |")
    print("\n## B. Per day of the part's end and host\n")
    print("| day (UTC) | host | parts (no record) | verdicts | build timeouts | timeout share | verdicts per part-hour |")
    print("|---|---|---|---|---|---|---|")
    day = collections.defaultdict(list)
    for p in ps:
        day[(iso(p["t1"])[:10], p["host"])].append(p)
    for (dd, host), g in sorted(day.items()):
        c = sum((p["c"] for p in g if p["rec"]), collections.Counter())
        hrs = sum(p["t1"] - p["t0"] for p in g) / 3600
        print(f"| {dd} | {host} | {len(g)} ({sum(not p['rec'] for p in g)}) | {c['verdict']} | {c['timeout']} | {share(c)} | "
              f"{c['verdict'] / hrs:.1f} |" if hrs else f"| {dd} | {host} | {len(g)} | - | - | - | - |")
    print("\n## C. Build-timeout share by the host's mean 5-min load while the part ran (32 cores each; its own jobs included)\n")
    print("| host | load bucket | parts | verdicts | build timeouts | timeout share |")
    print("|---|---|---|---|---|---|")
    bk = collections.defaultdict(list)
    for p in ps:
        if p["rec"] and p["during"] is not None:
            b = "< 16" if p["during"] < 16 else "16-32" if p["during"] < 32 else "32-64" if p["during"] < 64 else ">= 64"
            bk[(p["host"], b)].append(p)
    order = {"< 16": 0, "16-32": 1, "32-64": 2, ">= 64": 3}
    for (host, b), g in sorted(bk.items(), key=lambda x: (x[0][0], order[x[0][1]])):
        c = sum((p["c"] for p in g), collections.Counter())
        print(f"| {host} | {b} | {len(g)} | {c['verdict']} | {c['timeout']} | {share(c)} |")
    print("\n## D. Build-timeout share by setup (cold: a re-clone and Lean rebuild, setup >= 300 s; warm: < 300 s)\n")
    print("| host | setup | parts | verdicts | build timeouts | timeout share | setup s (median) |")
    print("|---|---|---|---|---|---|---|")
    sk = collections.defaultdict(list)
    for p in ps:
        if p["rec"] and p["setup"] is not None:
            sk[(p["host"], "cold" if p["setup"] >= 300 else "warm")].append(p)
    for (host, w), g in sorted(sk.items()):
        c = sum((p["c"] for p in g), collections.Counter())
        print(f"| {host} | {w} | {len(g)} | {c['verdict']} | {c['timeout']} | {share(c)} | "
              f"{statistics.median(p['setup'] for p in g):.0f} |")
    print("\n## E. Files of the build-timeout mutants (all hosts)\n")
    fc = sum((p["files"] for p in ps), collections.Counter())
    print(", ".join(f"{f} {n}" for f, n in fc.most_common(8)) + f"; total {sum(fc.values())}")
    print("\n## G. The same mutant tried more than once (same head and id), at least once a build timeout: each try by the"
          " host's mean load while its part ran\n")
    print("| host | load bucket | tries | build timeout | verdict | other UNKNOWN |")
    print("|---|---|---|---|---|---|")
    seen = collections.defaultdict(list)
    for p in ps:
        for i, o in p["tries"]:
            seen[(p["head"], i)].append((p, o))
    gk = collections.defaultdict(collections.Counter)
    for key, ts in seen.items():
        if len(ts) > 1 and any(o == "timeout" for _, o in ts):
            for p, o in ts:
                ld = p["during"]
                b = "-" if ld is None else "< 32" if ld < 32 else "32-64" if ld < 64 else ">= 64"
                gk[(p["host"], b)][o] += 1
    for (host, b), c in sorted(gk.items()):
        print(f"| {host} | {b} | {sum(c.values())} | {c['timeout']} | {c['verdict']} | {c['unknown']} |")
    n = sum(1 for ts in seen.values() if len(ts) > 1 and any(o == "timeout" for _, o in ts))
    later = sum(1 for ts in seen.values() if len(ts) > 1 and ts[0][1] == "timeout" and any(o == "verdict" for _, o in ts[1:]))
    always = sum(1 for ts in seen.values() if len(ts) > 1 and all(o == "timeout" for _, o in ts))
    print(f"\n{n} mutants tried more than once with a build timeout: {later} timed out first and got a verdict later, "
          f"{always} timed out on every try.")
    if end:
        w = [p for p in ps if end - 86400 < p["t1"] <= end and p["rec"]]
        c = sum((p["c"] for p in w), collections.Counter())
        hosts = sorted({p["host"] for p in w})
        print(f"\n## F. The 24 h ending {iso(end)} (parts that ended in it)\n")
        print(f"{len(w)} parts with a record on {', '.join(hosts) or 'no host'}: {c['verdict']} verdicts, {c['timeout']} build "
              f"timeouts ({share(c)}), {c['unknown']} other UNKNOWN, {c['notrun']} NOT RUN.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
