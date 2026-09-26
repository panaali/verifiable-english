# Claude constitution translation pilot

This branch records the first translation of the published official body at `ve-green-w3`.
The full fetched HTML and extracted Markdown are pinned under `source/`.
The document, per-unit ledger, metrics, and natural rendering are under `run-20260926T2321Z/`.
`build_translation.py` verifies the source hash before rebuilding the run.

Run from the repository root:

```sh
UV_CACHE_DIR=/tmp/ve-uv-cache uv run python usecases/claude-constitution-pilot/build_translation.py
UV_CACHE_DIR=/tmp/ve-uv-cache uv run python -m ve document check usecases/claude-constitution-pilot/run-20260926T2321Z/translation.ve.md
UV_CACHE_DIR=/tmp/ve-uv-cache uv run python -m ve document coverage usecases/claude-constitution-pilot/run-20260926T2321Z/translation.ve.md
UV_CACHE_DIR=/tmp/ve-uv-cache uv run python -m ve document render usecases/claude-constitution-pilot/run-20260926T2321Z/translation.ve.md
```

Statuses in `units.json` are a review ledger over the exact byte spans.
`UNFORMALISED` reasons identify a primary blocker using the requested fixed categories; `other:discourse` is encoded as `other.discourse` in the VE wire format because document reason tokens cannot contain a colon.
The other-blocker lists and term mentions are search hints, not formal claims or checked semantic coverage.
`100%` coverage means that every source byte is accounted for, not that every sentence is translated.
No prior translation was present and no intent narrowing was made.
