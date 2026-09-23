# T1b: size and weak-monitor follow-up

New preregistration: [PREREG-T1b.md](PREREG-T1b.md). T1 remains unchanged.

Run from repository root with `UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4`:

```sh
uv run python -m ve_experiments.t1b.run prepare
uv run python -m ve_experiments.t1b.run stamp
# Commit the freeze and bound timestamps before ANY endpoint call.
uv run python -m ve_experiments.t1b.run all
uv run python -m ve_experiments.t1b.run report
uv run python -m ve_experiments.t1b.run report --split full
```

`all` completes all three gates, then automatically runs all five arms in
passing cells. Global STOP.json prohibits further calls. Run on the macOS host
so sandbox-exec can initialize for b-exec/d. At UTC midnight the runner waits
before launching a request that could cross the date boundary; date-specific
ledgers preserve the injected context. Completed logical requests are reused,
never failed or interrupted ones. T1's original failed gate is never consulted
as authorization for this separate experiment.

Offline validation before timestamp: 13 tests passed, including host sandbox
confinement, 5,000-record graph invariants, fresh split disjointness, cell-specific
thresholds, duplicate/missing gate slots, and lossless VE transport. Command:

```sh
T1_SANDBOX_TEST=1 UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run pytest -q tests/test_t1b.py
```

All original T1 HASHES entries were verified unchanged. The largest raw
5,000-record judge packet is 179,442 UTF-8 bytes; adding 6,000 output and 4,096
wrapper tokens gives a conservative 189,538 bound, below Haiku's 200,000.
Full c packet fit requires a native count when its byte upper bound is too large.
These checks never truncate source data or infer subscription charges.

## Explicit A1 continuation

The initial launch stopped on supplementary Haiku canonical metadata before
scoring. [PREREG-T1b-A1.md](PREREG-T1b-A1.md) independently freezes and timestamps
the exact shorthand equivalence; the original stop and response are preserved.
The original served ID matches the pinned dated model. A1 reuses that response
without resampling. Its active commands are:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python -m ve_experiments.t1b.amendment_run all
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/T1b/audit.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/T1b/write_report.py
```

A new `STOP-A1.json` is an immutable active global stop. Never delete either
stop file or change frozen code to force continuation. The standalone audit and
report scripts make no model calls. A 5,000-record honest VE closure/coverage
check also passed offline before continuation.
