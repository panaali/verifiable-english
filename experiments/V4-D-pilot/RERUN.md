# Amended judge-only run

The [orchestrator amendment](AMENDMENT-2026-09-22.md) supersedes the judge stage
of the stopped pilot. `results/` remains immutable, including its permanent STOP
marker and 16 superseded scores. New evidence is in `results-judge-rerun/`.
`rerun-manifest.json` freezes the old evidence, exact argument files, amended
runner, backend and analysis. It was committed as `3a6261b` before new calls.

The shared endpoint accepts `--account-config-dir` or
`VE_CLAUDE_ACCOUNT_CONFIG_DIR`. The Python constructor accepts
`account_config_dir=...`. Explicit account selection ignores an ambient OAuth
token. The account directory supplies only its OAuth access token (credential
file or path-hashed Keychain service); no account settings or memory are imported.
New ledger rows carry `account_label`; ledgers with other or missing labels cannot
be resumed. Historical rows are attributed by immutable file hash and line number
in `legacy-account-attribution.jsonl` without changing the original evidence.

Commands used, serially, from the repository root:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-D-pilot/rerun.py smoke --account-config-dir ~/.claude-danielsaeedi37
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-D-pilot/rerun.py run --account-config-dir ~/.claude-danielsaeedi37
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-D-pilot/analyze_rerun.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-D-pilot/audit_rerun.py
```

The replacement run stopped at 128/480 judgments on a connection reset. To
reproduce the committed partial report with explicit missing counts, use
`UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python experiments/V4-D-pilot/report_stopped_rerun.py`.
Do not remove either stop marker or invoke a new live run as a report step.

The smoke command makes exactly two content-free Haiku calls; they are excluded
from outcomes. Resuming reuses successes only. A replacement STOP marker is
permanent. The original runner still implements the historical capped protocol;
do not use it for this amendment. No argument regeneration is part of the rerun.
