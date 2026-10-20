# Full verification gate

Run these commands from the repository root. For everyday development, start with the [testing guide](TESTING.md).

Run the complete offline verification gate with `python3 tools/gate.py`.
Every stage runs in an environment built from scratch, not inherited: `PATH` holds
only the pinned Lean and Rust toolchain `bin` directories (under the account's
`~/.elan/toolchains` and `~/.rustup/toolchains`), `uv` and `/usr/bin:/bin`; home,
caches and temporary files are fresh directories owned by that run. The allowed
variables are listed in `ALLOWED_ENVIRONMENT` in `tools/gate.py`, and the exact
environment of each stage is recorded in the result.
It checks the pinned Lean and Rust versions, syncs the locked Python environment
(refusing any ancestor `pyproject.toml` that declares a uv workspace, which would
substitute its own lock and `.venv`, and checking that Python runs from the
checkout's `.venv`), builds both native backends once, runs the Lean source audit, `cargo test`, and
the full non-live pytest suite (collected serially, then run on `--workers` xdist
workers, default `auto`; every worker must collect the same selection), then writes `gate-result.json` with the commit SHA, tool versions, counts,
every skip and every failure. It exits nonzero for missing backends, unlisted skips,
missing test IDs, a dirty or changing worktree, or failed stages. The expected test
IDs, deselected live tests included, are the merge base's (`--base REV` names another commit): the
collection a gate attached to that commit as the git note `refs/notes/ve-gate-collection`, or, without
one, the base collected in a scratch worktree (and then attached). New tests are fine; a base ID the head
does not collect fails the gate unless a commit since the base records its removal with a trailer
`Test-removed: <test ID, or its deleted function, class or file> — <reason>`, which reviewers read with the
batch. A trailer naming a test the head still collects fails as stale. `git diff --no-renames base..HEAD`
only labels each removal: its file or test function deleted, or its parametrisation changed
(`tools/gate_collection.py`). Every full
gate attaches its own collection to its commit. `uv run python tools/gate_collection.py --check` (after
`(cd lean && lake build)`) runs the same comparison on the worktree. Optional backend
and fixture skips are listed in `tools/gate-optional.json`. The JSON result is local and ignored by Git;
use `--output PATH` to retain a particular gate record. The package requires
Python 3.12 or later.
