# Infrastructure recovery amendment — 2026-09-22

The user's explicit instruction authorizes resuming the interrupted replacement
judge stage on **danielsaeedi37 only**, retaining its 128 completed judgments and
completing the remaining 352. This supersedes the transport-error portion of the
previous permanent-stop rule. It does not authorize changed prompts, models,
accounts, argument artifacts, scoring, or sample selection.

A connection error (including ECONNRESET), a `<synthetic>` placeholder without a
served model, or an empty stream is an **INFRASTRUCTURE failure, never a sample**.
Retry the identical request up to five times within a run, after 30, 60, 120, 240,
and 480 seconds. Every physical attempt and retry delay is appended to the same
ledger under the same request key. After exhaustion, write `PAUSE.json`, exit 75,
and leave that request resumable. An explicit resume starts a fresh retry allowance;
its first attempt following a recorded infrastructure failure waits 30 seconds.
A real alternate-model identity still takes priority and permanently halts. Other
endpoint-integrity rules, the global 790-start ceiling, and pinned UTC date remain.

`results-judge-rerun/STOP.json` and the original failed stream remain byte-for-byte
historical evidence. Only that exact stop hash is exempted by `resume-manifest.json`;
a new permanent halt is stored as `ENDPOINT_STOP.json`. No old score is deleted,
regenerated, or selected again. A legacy error is classified from its preserved
raw stream; its next ledger entry documents infrastructure recovery. Raw rows are
never rewritten. The new manifest freezes updated backend/runner code, this
amendment, retry tests, all 128 scores, and every pre-resume ledger byte prefix,
and incorporates unchanged hashes from the previous manifest. The original
manifest stays immutable. The backend revision and request controls stay unchanged
because the new code changes transport handling only, preserving cache identity.

Analysis uses the existing frozen scoring and whole-item paired bootstrap method.
Report all ten complete cells, attack answer rejection and translation catch,
false approval, honest completion, both-correct items, and reported thinking usage.
Infrastructure attempts and retries are accounted separately from samples.
