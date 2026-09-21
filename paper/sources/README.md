# Frozen paper inputs

`manifest.json` records the implementation base and the revision, source path,
and SHA-256 of every copied input. Branch files are byte-for-byte snapshots of
committed objects. The Colab ladder and statement-review records were supplied
outside this repository; this paper commits copies for auditability. They have
not been independently rerun. The process excerpts are selected complete log
entries, not a complete audit trail. Source files retain their historical claims;
the manuscript qualifies or supersedes those claims where later evidence requires it.

All ladder rows are **DEV-PILOT**, not held-out presentation effects. E1 v5 and
E4 revision 2 froze before scored judging. `e1-results.md` is the scored E1/E1b
report at cb2b7ff; `e4-score-summary.json` and `e4-score-table.md` are supplied
external scored records, committed here before manuscript authoring. Selected
outcome log entries are in `process-log-results.md`; planned replication and
baseline comparisons are in `planned-replication.md`. The qualitative debate
and amendment snapshots pin usecases/main and are not cross-reviewed. Their
historical claims about bounded search are qualified in the manuscript.
E5 remains materials and pilots only; E2 was not run.
The fourth Lean review supersedes the historical closure-certificate restriction.

Generation reads these snapshots and the committed implementation fixtures. It
never reads a moving branch, downloads a dataset, or makes a model call.
