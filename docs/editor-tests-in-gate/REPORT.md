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
`webapp/requirements.txt` exists, it snapshots the synced environment (`uv pip freeze --python <checkout>/.venv`, stage
"Python packages from the lock"; an empty snapshot fails the gate), runs `uv pip install --require-hashes --no-build
--python <checkout>/.venv -r webapp/requirements.txt` (stage "editor web server"; same fresh uv cache and isolated
environment as the sync; `--no-build` so no source distribution is built during the gate), snapshots again (stage
"Python packages with the web server") and fails the gate if any package the locked sync installed is missing or at
another version afterwards (names compared canonically; an editable install by its whole line). Only then does it
record the file's sha256 as `toolchains.web_requirements_sha256` in the gate record. Each of the three commands raises on
failure through `command`, and `main` turns that into a failed gate. Without the file (main until the editor merges)
nothing changes. `uv.lock`, `pyproject.toml` and the recorded `toolchains.uv_lock_sha256` are untouched: the install
writes only `.venv`. The added packages that are not in `uv.lock` (fastapi, starlette, uvicorn, annotated-doc,
opentelemetry-api) are imported only by the editor and its tests (`ve_webapp/`, `tests/test_webapp*.py`,
`tests/webapp_support.py`). The editor's file re-pins nine locked packages (pydantic, pydantic-core, anyio, idna, h11,
click, typing-extensions, annotated-types, typing-inspection) at their locked versions; the version check above is what
enforces that, so every later stage and the Lean-first oracle still run on exactly the lock's versions.

`tools/gate-optional.json` (a file only `tools/gate.py` reads: select_tests and pytest never apply it) still lists the
editor's tests as allowed skips ("the editor's web server is not in uv.lock") and a `fastapi` backend entry. Those rows
are on the editor branch (plain-vocab-editor-1126), not on this one, so this branch leaves them alone. Once both
branches are merged the gate always installs the web server when the file exists, so those rows can only hide a
regression (for example a renamed `webapp/requirements.txt`, whose `is_file()` early return is silent, or a fail-open
install). They are dropped by backlog row `editor-tests-skip-rows-drop` (filed by the acting DRI, 2026-11-27), which runs
after both plain-vocab-editor-1126 and this item merge: it removes the "the editor's web server is not in uv.lock" rows
and the `fastapi` backend entry and keeps the node rows.

2026-11-27, after both merged: branch editor-followups-1127 (row editor-tests-skip-rows-drop) dropped those 32 rows and
the `fastapi` backend entry; tests/test_gate_integrity.py now fails if a web-server skip is admitted again.

VE's outputs (verdicts, diagnostics, schemas) do not change. The gate record gains one field; the gate log gains the
stage line.

## Evidence

- Unit tests (`tests/test_gate_integrity.py`, `command` faked; the requirements file is written at the literal path
  `webapp/requirements.txt`, so on a gate without the step they fail on behaviour, not on a missing attribute):
  - `test_gate_installs_the_editor_web_server_on_the_synced_environment`: stage order and exact commands (sync,
    snapshot, install with `--require-hashes --no-build`, snapshot), recorded hash;
  - `test_gate_without_web_requirements_runs_only_the_locked_sync`;
  - `test_web_server_install_never_names_the_oracle_lock`: the checkout's `uv.lock` hash is the oracle pin
    312825c8c53903f3dcacc5aa9fea5514183a99aa155f4df9ee056d163011b75b and the install never locks, adds or names the lock
    or `pyproject.toml` (the copied-lock assert that could not fail is gone);
  - `test_web_server_install_must_not_change_a_locked_package[version|version-respelled|removed|editable-source]` (B1):
    the fake reports a changed version, a changed version under another spelling, a removed package, a moved editable
    install; each fails the gate naming the package. On the previous branch head (266f45b63c) all four fail;
  - `test_web_server_install_may_add_packages_and_respell_names`, `test_web_server_install_refuses_an_empty_lock_snapshot`;
  - `test_web_server_install_fails_closed[...]` (B2), one per stage (both snapshots, the install): the stage raises,
    `check_python_project` re-raises it unchanged and `web_requirements_sha256` is not recorded.
- Seeded mutants: `mutants.json`, 14 of 14 killed, each an exact from/to edit of `tools/gate.py` replayed against its
  test: no install, no `--require-hashes`, wrong environment, inverted file check, lock hashed instead, `uv lock` instead
  of `uv pip install`, install before the sync (P7, now exact text), fail-open install (P8, `try`/`except RuntimeError:
  return`), version check off (P9), removals ignored (P10), names not canonicalised (P11), empty snapshot accepted
  (P12), no `--no-build` (P13), one snapshot reused for both sides (P14).
- End to end (the operator's harness, outside this repository; VM route only, run before the fix round, so it covers the
  install but not the snapshots or `--no-build`, which only the unit tests above exercise): in a scratch checkout of the
  editor branch at f388b9c121, the gate's own `gate_environment` + `check_toolchains` + `check_python_project`, then pytest on
  `tests/test_webapp.py tests/test_webapp_copy.py tests/test_webapp_asimov.py`:
  - main's venv step: 19 passed, 32 skipped ("the editor's web server is not in uv.lock"), 1 xfailed;
  - this venv step: 51 passed, 1 xfailed (the known open copy measurement), 0 skipped;
  - `uv.lock` sha256 before and after both runs, and `toolchains.uv_lock_sha256` as the gate recorded it: the oracle pin
    above; `git status` of `uv.lock` and `pyproject.toml`: clean.
- Selected tests for this branch (`tools/select_tests.py --base main --run`): first round, coverage map e1ae0677a4, 238
  of 238 units passed; fix round, at a466fd0b71 (tree c69fc6c6c3), 266 units recorded, 0 failed. `lake build` and
  `lean/audit.py` pass (no Lean change).
