# T1b A1: canonical metadata equivalence, before outcome inspection

2026-09-22. This explicitly reports and corrects a metadata guard false positive;
it does not alter T1, choose a new gate, change samples, or resample any response.

The timestamped T1b launch made exactly two generation calls: one Opus author
and one Haiku judge. The judge response passed the shared backend's exact model
identity checks: initialization, assistant message and modelUsage key all name
claude-haiku-4-5-20251001. Its supplementary modelUsage.canonicalModel instead
names claude-haiku-4-5. The harness incorrectly required the supplementary field
to repeat the dated request ID verbatim and stopped before writing a score or
cost record for that response. The response is retained as `ok` in the immutable
ledger. No judge decision or rationale has been inspected by the experiment
operator before writing this clarification: only identity, usage, timestamps,
exception and the empty scored summary were read. Thus no observed performance
has informed this correction or the fixed sample design.

Accept ONLY these canonical metadata values for Haiku: the pinned dated ID
claude-haiku-4-5-20251001, or the shorthand claude-haiku-4-5. Continue requiring
EXACT claude-haiku-4-5-20251001 in every served-model protocol location checked
by claude_cli.parse_stream. Do not accept any other version/date/model. Opus
and Sonnet identity guards are unchanged. A shorthand canonical label is not
evidence that the model changed. Any actual identity change still stops globally.

Preserve the original STOP.json, logs, summary and all frozen T1b files. The
separate amendment_run.py verifies the original freeze, this amendment's freeze
and receipts, and the exact original STOP.json hash. It uses STOP-A1.json for
any new global stop. This is an explicit, prospective restart after correcting
the stated false positive, not a silent bypass. Before resuming, submit BOTH
this amendment and HASHES-A1 to OpenTimestamps, retain bound receipts, and commit.
No additional endpoint calls before that commit.

Reuse the already-completed author and judge responses under their original
logical request/sample IDs; reconstruct the missing Haiku cost record from its
original ledger, then score the exact retained response. Never repeat either
call. Keep all remaining samples, order, seeds, thresholds, prompts, budgets,
context checks, date-block rules and conditional full study unchanged. New
failed/started calls remain nonresumable. Preserve all physical costs, including
responses rejected by an integrity guard. The original zero-score summary is
copied to summary-before-A1.json before generating a current summary.

The A1 driver is a copy of the frozen runner with only the exact equivalence,
prior-response cost reconstruction, immutable old-stop validation, new stop path
and amendment freeze verification described here. No experimental outcome
is excluded or changed by this correction. Report this guard error and explicit
amendment in the final study provenance. Original T1 remains STOP_CEILING.
