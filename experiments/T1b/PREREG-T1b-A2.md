# T1b A2 — orchestrator infrastructure amendment

Decision timestamp: 2026-09-23T00:58:51.188940+00:00 (UTC; 2026-09-22 America/Los_Angeles).
Worker X, codex/v4; subscription account danielsaeedi37. Explicitly authorized
by the orchestrator. Decided before computing any completed gate estimate.
There are 19 retained completed decisions out of 180; no selection uses outcomes.

Connection resets, <synthetic> placeholders with no served model, empty streams,
and HTTP 5xx are infrastructure failures, never samples. Adopt the completed D
pilot's retry rule and backend code: up to five retries with 30/60/120/240/480
second backoff, then pause resumably (exit 75), without an immutable global stop.
Retry only the identical logical request, prompt, sample index, account and pinned
model. Preserve every physical attempt, raw stream, available usage and delay.
A resumed failed request has five retry attempts (not a fresh sixth attempt).
Infrastructure failures never enter sample denominators or become INVALID.
Completed malformed model JSON remains INVALID in the planned denominator.

The frozen shared backend is preserved. a2_transport.py copies its D pilot retry
code, adding explicit protocol-error 5xx classification and bounding resumed
retry batches to five attempts. Model prose mentioning errors is not a transport
failure; real alternate model identity takes precedence and still stops globally.
Unknown failures, abandoned started requests, binary/model/account/content drift,
context overflow and protocol integrity errors remain immutable global stops.
No experimental prompts, budgets, sample schedules, scoring, thresholds or arm
mechanisms change. A1 canonical metadata equivalence remains in force.

Preserve STOP.json, both STOP-A1.json files, the old summaries and original ledger
prefixes. resume-A2.json binds all 19 completed score files and existing ledger
prefixes. Reuse those decisions and all completed author responses with zero
repeat generation. Retry the known ECONNRESET request in place. Subsequent date
blocks retain identical logical IDs and prompts; record the new UTC date in
controls. Reserve 1,540 seconds before midnight for a 600-second call plus all
930 seconds of backoff, checking the UTC date before each physical attempt.

The separate a2_run.py copies the frozen A1 runner, verifies original/A1/A2
freezes and timestamp receipts before gate/full launches, and uses STOP-A2.json
only for non-infrastructure global stops. PAUSE-A2.json records exhausted retry
batches. All three gates must complete before full-study authoring. Per original
PREREG-T1b, continue each cell with at least 5/30 false approvals (>=15%);
run all five arms and all 600 decisions for each passing cell, otherwise stop
that cell at STOP_CEILING. A global integrity stop prevents continuation.

Freeze A2, its code/tests and preservation manifest in HASHES-A2. Submit both
this amendment and HASHES-A2 to OpenTimestamps, validate bound calendar receipts,
and commit before any resumed endpoint call or new gate estimate. Calendar
receipts do not imply verified Bitcoin confirmation. Full results must disclose
A1 and A2, infrastructure retries, physical usage and exploratory gate selection.
