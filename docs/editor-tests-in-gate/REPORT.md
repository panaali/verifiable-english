# editor-tests-in-gate: the full gate installs the editor's web server

Row editor-tests-in-gate (infra). Decision: the decider's ruling of 2026-11-27 on the plain-vocab-editor escalation 1
(ACCEPTED: the gate installs the pinned `webapp/requirements.txt`; the oracle's `uv.lock` pin does not change).

## Problem

The full gate's venv step, `tools/gate.py` `check_python_project`, runs `uv sync --locked --group dev`. That sync is
exact: it removes any package not in `uv.lock`. `uv.lock` is frozen by the Lean-first oracle
(`tools/lean_first_oracle.py`, `docs/lean-first/oracle.json`) and has no fastapi, so every gate (VM, Mac, Actions
shards, cloud: all run `tools/gate.py`, which re-syncs whatever the host prepared) skipped the editor's tests
(`tests/test_webapp*.py`, mark `NEEDS_SERVER`, listed as optional in `tools/gate-optional.json`).

## Change

`check_python_project` now calls `install_web_server` after the locked sync and the environment check. When
`webapp/requirements.txt` exists, it runs `uv pip install --require-hashes --python <checkout>/.venv -r
webapp/requirements.txt` (stage "editor web server"; same fresh uv cache and isolated environment as the sync) and records
the file's sha256 as `toolchains.web_requirements_sha256` in the gate record. Without the file (main until the editor
merges) nothing changes. `uv.lock`, `pyproject.toml` and the recorded `toolchains.uv_lock_sha256` are untouched: the
install writes only `.venv`. The added packages that are not in `uv.lock` (fastapi, starlette, uvicorn, annotated-doc,
opentelemetry-api) are imported only by the editor and its tests (`ve_webapp/`, `tests/test_webapp*.py`,
`tests/webapp_support.py`); the shared packages are pinned to their locked versions, so other tests see the same versions.
`tools/gate-optional.json` keeps the fastapi entries: environments without the web server (a builder's plain checkout)
may still skip them.

VE's outputs (verdicts, diagnostics, schemas) do not change. The gate record gains one field; the gate log gains the
stage line.

## Evidence

- Unit tests (`tests/test_gate_integrity.py`): `test_gate_installs_the_editor_web_server_on_the_synced_environment`
  (order and exact command, recorded hash), `test_gate_without_web_requirements_runs_only_the_locked_sync`,
  `test_web_server_install_leaves_the_oracle_lock_alone` (checkout's `uv.lock` hash = the oracle pin
  312825c8c53903f3dcacc5aa9fea5514183a99aa155f4df9ee056d163011b75b; the install never locks, adds or names the lock). On
  main's `tools/gate.py`: 2 failed, 2 passed (the no-file case passes on both). With the change: 4 passed.
- Seeded mutants: `mutants.json`, 7 of 7 killed (no install, no `--require-hashes`, wrong environment, inverted file
  check, lock hashed instead, `uv lock` instead of `uv pip install`, install before the sync).
- End to end (the operator's harness, outside this repository): in a scratch checkout of the editor branch at
  f388b9c121, the gate's own `gate_environment` + `check_toolchains` + `check_python_project`, then pytest on
  `tests/test_webapp.py tests/test_webapp_copy.py tests/test_webapp_asimov.py`:
  - main's venv step: 19 passed, 32 skipped ("the editor's web server is not in uv.lock"), 1 xfailed;
  - this venv step: 51 passed, 1 xfailed (the known open copy measurement), 0 skipped;
  - `uv.lock` sha256 before and after both runs, and `toolchains.uv_lock_sha256` as the gate recorded it: the oracle pin
    above; `git status` of `uv.lock` and `pyproject.toml`: clean.
- Selected tests for this branch (`tools/select_tests.py --base main --run`, coverage map e1ae0677a4): 238 of 238 units
  passed, 0 failed.
