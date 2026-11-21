"""Chain-gate minutes per host from stage-events.jsonl (cg-actions-shard-1121 measurement; target: median of the
actions-* host <= 45 min over the gates after the install).

usage: python3 -I measure.py <stage-events.jsonl> [<since ISO, e.g. 2026-11-21T12:00Z>]
Pairs each item's gate-start with its next gate-end; the host is the first word of the start note (actions-arm,
actions-x86, vm, ve-cloud-2, mac, selected, ...), as tools-local/mac-last-resort.py reads it. A start with no end
(a FIX_EARLY cancel: gate-cancelled, no gate-end) is counted as open, not timed. Prints one line per host:
"<host> n=<timed> open=<n> median=<min> p90=<min> max=<min>"."""
import datetime
import json
import statistics
import sys


def ts(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def main(argv):
    since = argv[1] if len(argv) > 1 else ""
    start, mins, opened = {}, {}, {}
    for line in open(argv[0]):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if not isinstance(e, dict) or e.get("t", "") < since:
            continue
        item, st, note = e.get("item"), e.get("stage"), str(e.get("note", ""))
        if st == "gate-start":
            if item in start:
                opened[start[item][0]] = opened.get(start[item][0], 0) + 1
            start[item] = (note.split(" ")[0], ts(e["t"]))
        elif st in ("gate-end", "gate-cancelled") and item in start:
            host, t0 = start.pop(item)
            if st == "gate-end":
                mins.setdefault(host, []).append((ts(e["t"]) - t0).total_seconds() / 60)
            else:
                opened[host] = opened.get(host, 0) + 1
    for host, _ in start.values():
        opened[host] = opened.get(host, 0) + 1
    for host in sorted(set(mins) | set(opened)):
        w = sorted(mins.get(host, []))
        if w:
            p90 = w[min(len(w) - 1, int(0.9 * len(w)))]
            print(f"{host} n={len(w)} open={opened.get(host, 0)} median={statistics.median(w):.1f} p90={p90:.1f} max={w[-1]:.1f}")
        else:
            print(f"{host} n=0 open={opened.get(host, 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
