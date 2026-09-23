# T1b A4 — orchestrator infrastructure amendment: output-cap exhaustion

Decision timestamp: 2026-09-23T02:25:07+00:00 (UTC; 2026-09-22 America/Los_Angeles).
Opus 5.5 worker taking over codex/v4; account saeedi.danial. Explicitly authorized
by the orchestrator. At this decision there are 0/600 full decisions and one
completed held-out attack-monitor response; no outcome is used.

Diagnosis of STOP-A3.json (02:19:25 UTC, "Not a single-turn response"): request
5a47675a06cf/b-monitor/1 served claude-sonnet-5 throughout, with empty tool/MCP
inventory and only thinking/text blocks. Its first assistant turn exhausted the
requested 12,000-token output cap, mostly thinking. CLI 2.1.280 then injected a
synthetic user message ("Output token limit hit. Resume directly ...",
isSynthetic=true) and called the model again, giving num_turns=2, two message IDs
and 20,121 output tokens. The two-turn stream was produced by the CLI's recovery
logic. It was not a tool call, model substitution or session limit.

Rule: a response that exhausts its requested output cap is not a sample. This
covers the CLI's synthetic output-cap continuation and a bare max_tokens stop.
Both are classified with A2 infrastructure failures: never scored, never INVALID,
retried as the identical logical request (same account, pinned model, prompt,
sample index and controls) with A2's 30/60/120/240/480 s backoff, then paused
resumably. The retry path accepts only that exact
pattern. Any other user turn, tool block, nonempty tool/MCP inventory, alternate
served model or session limit keeps its A3 handling: an immutable stop.
Retrying conditions retained responses on finishing within the frozen cap. This
is a disclosed limitation. Every such attempt is counted and reported per role.

No prompts, models, output/thinking/effort controls, budgets, schedules, scoring,
thresholds, intervals or arm mechanisms change. A1-A3 remain in force, including
A3's immediate stop on a saeedi.danial session limit or a served-model change.

STOP-A3.json (both copies), the failed raw stream and all A3 artifacts are
preserved byte-for-byte and bound in resume-A4.json. They remain historical.
The failed monitor request resumes in place with five retries. New stops use
STOP-A4.json and pauses PAUSE-A4.json. a4_transport.py and a4_run.py copy the
A3 code, changing only this classification and the A4 file names/verification.
Freeze this amendment, the manifest, the A4 code and its tests in HASHES-A4.
Submit the amendment and HASHES-A4 to OpenTimestamps and commit before any A4
call. Bitcoin confirmation is not asserted.
