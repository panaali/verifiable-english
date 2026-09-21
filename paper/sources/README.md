# Frozen paper inputs

`manifest.json` records the implementation base and the revision, source path,
and SHA-256 of every copied input. Branch files are byte-for-byte snapshots of
committed objects. The Colab ladder and statement-review records were supplied
outside this repository; this paper commits copies for auditability. They have
not been independently rerun. The process excerpts are selected complete log
entries, not a complete audit trail. Source files retain their historical claims;
the manuscript qualifies or supersedes those claims where later evidence requires it.

All ladder rows are **DEV-PILOT**, not held-out presentation effects. E1 and E5
preregistrations are **drafts**, not evidence that a scored run was authorized
or completed. Copying a draft here does not freeze it for scoring.

Generation reads these snapshots and the committed implementation fixtures. It
never reads a moving branch, downloads a dataset, or makes a model call.
