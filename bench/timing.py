"""Small offline timing helpers for the English benchmark."""
import math
import os
import statistics
import time


def measure(fn, *, repeats=5, warmups=1):
    """Keep cold start out of warm-process latency samples."""
    if repeats < 1 or warmups < 0:
        raise ValueError('repeats must be positive and warmups nonnegative')
    for _ in range(warmups):
        fn()
    vals, loads = [], []
    for _ in range(repeats):
        loads.append([round(v, 3) for v in os.getloadavg()])
        start = time.perf_counter()
        fn()
        vals.append(round((time.perf_counter() - start) * 1000, 3))
    return vals, loads


def stats(vals):
    ordered = sorted(vals)
    rank = (len(ordered) - 1) * .95
    low = math.floor(rank)
    high = math.ceil(rank)
    p95 = ordered[low] + (ordered[high] - ordered[low]) * (rank - low)
    return {'p50_ms': round(statistics.median(vals), 3),
            'p95_ms': round(p95, 3), 'max_ms': ordered[-1]}
