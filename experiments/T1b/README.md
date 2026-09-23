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

## Explicit A2 infrastructure continuation

[PREREG-T1b-A2.md](PREREG-T1b-A2.md), timestamped and committed as `73df459`,
supersedes only infrastructure handling. Original/A1 files and stops remain
historical and immutable. All 19 completed gate decisions and pre-resume ledger
prefixes are bound by `resume-A2.json` and reused without generation.

Active commands (run on the host; account danielsaeedi37 only):

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python -m ve_experiments.t1b.a2_run all
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/T1b/audit_A2.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/T1b/write_report_A2.py
```

The runner verifies every freeze and bound timestamp before gate/full launches.
Connection failures, unserved synthetic placeholders, empty streams and HTTP 5xx
receive up to five retries at 30/60/120/240/480 seconds, then exit 75 with a
resumable `PAUSE-A2.json`. A new `STOP-A2.json` remains an immutable global
integrity stop. Infrastructure failures never count as experimental samples.
The D pilot backend code is preserved in a separate A2 copy, with explicit 5xx
classification and exactly five retries when resuming a previous failure.
`all` finishes every gate before running all five arms in each passing cell.

A2 execution status (2026-09-23 02:09:39 UTC): gate complete, 180/180; only
Haiku/5,000 qualifies. Full study began, then exited 75 after the first Sonnet
monitor request returned six unserved session-limit placeholders (initial plus
five retries). The provider displayed a 06:00 UTC reset. `results-full/PAUSE-A2.json`
is resumable; 0/600 full decisions have been scored. Both completed full author
responses are cached. See [RESULTS.md](RESULTS.md), [execution-A2.json](execution-A2.json)
and [integrity-audit-A2.json](integrity-audit-A2.json). The full study is incomplete;
no five-arm performance claim is available.

## A3 whole full-study account move

[PREREG-T1b-A3.md](PREREG-T1b-A3.md) was frozen, independently timestamped and
committed as `974098c` before resumption. All new full-study calls use
`saeedi.danial` (`~/.claude-saeedi.danial`). At the switch there were 0/600 final
decisions and no completed held-out monitor calls. The two author responses
from the original account are retained unchanged. Gate decisions are frozen.

The active full-study command is:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python -u -m ve_experiments.t1b.a3_run full
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/T1b/audit_A3.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/T1b/write_report_A3.py
```

Run on the host for the trusted macOS sandbox. Session-limit protocol responses
on this account and served-model changes immediately stop all study calls under
`STOP-A3.json`; do not resume or switch accounts. A2's pause remains historical.
New ledgers explicitly include the account label. The qualifying gate had only
6/30 honest approvals, so honest completion is co-primary for interpreting any
arm difference; the original honest noninferiority margin remains −10 points.

A3 stopped at 2026-09-23 02:19:25 UTC with 0/600 final decisions: the second
held-out Sonnet review returned two turns/two message IDs, violating the frozen
single-turn control. The model remained claude-sonnet-5; no new-account session
limit was reported. `STOP-A3.json` is immutable. The failed response reports
195,106 input and 20,121 output tokens; it was not scored. See RESULTS.md and
execution-A3.json. Do not relaunch the command after this integrity stop.
