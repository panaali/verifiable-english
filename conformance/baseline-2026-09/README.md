# Stage 0 Python behaviour baseline

`python.json` contains the full Python return value or rejection record for
each matrix cell, the named claim-graph packages and records, work and envelope
boundary outcomes, and targeted feature probes. Its `source_commit` is the
commit that last changed `tests/probe_matrix.py`; the generator builds inputs
deterministically from that source. The generated index is
`docs/spec/semantics-support-matrix.md`.

Replay in a checkout with the same Python and locked dependencies:

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run python tests/probe_matrix.py
python3 tools/semantic_inventory.py
```

Both commands fail if their committed output differs. The baseline was made
with Python 3.14.7. Reproduction on a second machine remains the Gate 0 lead
check; a replay in this worktree checks only local determinism.

The matrix uses S for a returned verdict, R for a rejection and U for
`UnsupportedProfile`. Some rejected evidence is returned as a diagnostic
verdict, so its cell remains S and its exact `status` is retained. The pinned
Python executable is a second oracle only for inputs it actually supports.
