# Stage 0 Python behaviour baseline

`python.json` contains the full Python return value or rejection record for
each matrix cell, the named claim-graph packages and records, work and envelope
boundary outcomes, and targeted feature probes. Its `source_commit` is the
commit that last changed `tests/probe_matrix.py`; `runtime_sha256` binds the
`ve/` Python sources, `pyproject.toml`, and `uv.lock`. The generator builds inputs
deterministically from that source. The generated index is
`docs/spec/semantics-support-matrix.md`.

Replay in a checkout with the same Python and locked dependencies:

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run python tests/probe_matrix.py
python3 tools/semantic_inventory.py
```

Both commands fail if their committed output differs. The baseline was made
with Python 3.14.7. `external-imports.json` pins the native external package
imports and source digests; neither external checkout nor its home path is
needed to replay the inventory. The baseline projection removes only
`checker_build` and the Python `record_id` fields derived from it. They depend
on interpreter build details and are diagnostic identities, while semantic
bindings, statuses, records, certificates and model witnesses remain exact.

On the Stage 2 branch, the probe compares current Python outputs with this
frozen baseline and verifies `runtime_sha256` against the pinned Stage 0 Git
tree. Adapter source changes therefore do not rewrite the frozen runtime hash.

On an independent machine, transfer this committed branch (for example with
`git bundle`), use Python 3.14.7 and the locked dependencies, run the two replay
commands above, and record that machine's hostname, Python version, commit,
`sha256sum` for `python.json`, `external-imports.json` and both generated matrix
files, plus the command exit codes. Do not mark Gate 0 passed until the actual
second-machine run is recorded. A replay in this worktree checks local
determinism only.

The matrix uses S for a returned verdict, R for a rejection and U for
`UnsupportedProfile`. Some rejected evidence is returned as a diagnostic
verdict, so its cell remains S and its exact `status` is retained. The pinned
Python executable is a second oracle only for inputs it actually supports.
