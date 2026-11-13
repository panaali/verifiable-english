"""`soft-selected` through the Python relay (kb-10e, deliverable 4): the call `ve.soft_route.selected_at` makes.

usage: python docs/kernel/kb-10e/bench_relay.py <case.json> [<case.json> ...] [--reps 5]

For the first case: the median wall time of the first call (a fresh pool, the document registered with
the request) and of a repeat call, through `ve.backends.relay.decide("soft-norms", [case])`, with
soft-document handles and, for comparison, with the cases written out (`handles=False`). Then, for all
the cases given (documents), alternating, on a pool of two processes: the registrations each process
made, called one after another and from two threads at once (the pool hands a call to any idle
process, and each process registers the documents of the calls it answers).
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ve.backends import relay  # noqa: E402
from ve.backends.lean_service import LeanServicePool  # noqa: E402


def ms(xs):
    return round(statistics.median(xs) * 1000, 1)


def timed(pool, case):
    start = time.perf_counter()
    [entry] = pool.run_bound("soft-norms", relay.wire_checked([case]))
    assert entry["result"]["status"] == "ok", entry
    return time.perf_counter() - start


def first_and_repeat(case, reps, handles):
    firsts, repeats = [], []
    for _ in range(reps):
        with LeanServicePool(size=1, handles=handles) as pool:
            pool.start()
            firsts.append(timed(pool, case))
            repeats.extend(timed(pool, dict(case, id=f"r{i}")) for i in range(reps))
    return ms(firsts), ms(repeats)


def registrations(cases, threads):
    with LeanServicePool(size=2) as pool:
        pool.start()
        calls = [dict(cases[i % len(cases)], id=f"c{i}") for i in range(20)]
        if threads == 1:
            for c in calls:
                timed(pool, c)
        else:
            def work(part):
                for c in part:
                    timed(pool, c)
            ts = [threading.Thread(target=work, args=(calls[k::threads],)) for k in range(threads)]
            for t in ts:
                t.start()
            for t in ts:
                t.join()
        return [s.stats["registered"] for s in pool.services]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases", nargs="+")
    ap.add_argument("--reps", type=int, default=5)
    args = ap.parse_args()
    cases = [json.loads(Path(p).read_text()) for p in args.cases]
    print(f"| relay, {Path(args.cases[0]).name}, median of {args.reps} | first call ms | repeat call ms |")
    print("|---|---:|---:|")
    print("| soft-document handle | %s | %s |" % first_and_repeat(cases[0], args.reps, True))
    print("| written out (handles=False) | %s | %s |" % first_and_repeat(cases[0], args.reps, False))
    print()
    print(f"20 calls over {len(cases)} documents, alternating, pool of 2: registrations per process")
    print("- one after another:", registrations(cases, 1))
    print("- two threads:", registrations(cases, 2))


if __name__ == "__main__":
    main()
