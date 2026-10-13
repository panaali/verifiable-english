# fix/main-relay: the relay gate's length-check fixture after ts-B1

## Problem

`main` at 49de179e (Merge infra/ts-B1): `tests/test_relay_mutation_gate.py::test_a_client_without_its_length_check_fails_the_gate`
errored at setup with `AttributeError: module ve.backends.service_schema has no attribute RESPONSE`.
ts-B1 compiles every service validator lazily through the module's one compiler, `service_schema._compiler`:
`ROWS` is a `_Rows` mapping that calls `_compiler.ref(<mode>.json, "#/row")`, and `check_response` and
`check_handshake` call `_compiler.ref("envelope.json", ...)`. The module-level `RESPONSE` and `HANDSHAKE` are gone.

**Main moved while this ran.** AR-5a's merge (0ae408bb, "test: repair merged trust baseline and relay mutation
probe", on `main` by da0c04bd) made the same fixture fix. This branch merges `main` (ce68e6b6) and resolves the
fixture to the one-line form below; the code is equivalent. What this branch adds is the explanation in the
fixture's docstring, the cause of the ts-B1 miss, and the seeded-bug evidence.

## Fix (test only)

The fixture `without_length_check` patches `Compiler._x_length` to a no-op and replaces `service_schema._compiler`
with a fresh `Compiler()`. That one swap removes `x-length` from both the row validators and the response envelope,
and `monkeypatch` puts the module's own compiler back afterwards. `RESPONSE` is not reintroduced: `_compiler`
already owns the envelope validator. No other file in `tests/`, `tools/`, `ve/`, `conformance/` or `usecases/`
uses `RESPONSE`, `HANDSHAKE` or the old eager `ROWS` dict. No product code changed.

## Why the ts-B1 merge verify missed it

Test selection was not the cause. `branch-ts-B1-verify` ran the **full suite**: the selector printed
`368/368 test units ... FULL: missing coverage map`, and the run reported 14678 passed. It ran in
`~/code/ve-ts-B1`, where this same fixture fix had been made at 08:58 on 2026-10-12 but never committed
(`git -C ~/code/ve-ts-B1 status` still shows ` M tests/test_relay_mutation_gate.py`). The verify passed on the
dirty tree. The merge then used the committed tree dbea4a58 (the integration verify was "reused" because the
committed trees matched), so the old fixture reached `main`.

I checked whether selection catches this test: a scratch commit on 615e89d7 that changes only
`ve/backends/service_schema.py` (to its ts-B1 version) selects `tests/test_relay_mutation_gate.py` in the static
graph ("imports ve/backends/service_schema.py; names ve/backends/service_schema.py"). With a coverage map,
deleting `RESPONSE` taints `check_response`, and this test runs that in-process. So I did not change the map or
the static name rule, and I added no selection regression test.

Suggestion for the orchestrator (outside this repository): `verify.sh` / `merge-train.sh` should refuse to
verify a worktree with uncommitted changes, or commit them first as the verify-fix step already does.

## Seeded bugs

Python only, in the one changed file. Run with `uv run python tools/mutants.py docs/fix-main-relay/mutants.json`;
results are in `mutants-evidence.json`.

| id | file | change | killed by |
|----|------|--------|-----------|
| M1 | tests/test_relay_mutation_gate.py | no `_x_length` patch (check intact) | `test_a_client_without_its_length_check_fails_the_gate` |
| M2 | tests/test_relay_mutation_gate.py | length check removed from `envelope.json` only | same |
| M3 | tests/test_relay_mutation_gate.py | length check removed everywhere except `rights.json` | same |
| M4 | tests/test_relay_mutation_gate.py | rows compiled first, then only the class patched, with no fresh compiler (the old stale-cache shape) | same |

**Expected survivor S1** (`envelope-untouched.json`, results in `envelope-untouched-evidence.json`): the envelope
validator is left untouched and only the rows lose `x-length`. The test still **passes**, and should. The
envelope's only `x-length` is on `results` (`"/cases"`), and the same array's `x-rows` already requires
`len(results) == len(cases) == len(digests)`. So the envelope's length check is redundant, and no gate outcome
depends on it. M2 shows the other direction: removing only the envelope check leaves the gate passing these
routes, and the test fails. The probe runs (gate failures per variant) gave exactly the asserted
`accepted service:evaluate ... values` and `accepted service:rights ... unit_open` lines for rows-only removal,
and none for envelope-only removal.

## Deltas

No user-visible delta (the change is test-only), so no DRI-RULINGS row applies.

## Tests run

- `tests/test_relay_mutation_gate.py` and `tests/test_service_schema*.py`: 27 passed.
- Selected tests for the branch (`tools/select_tests.py --base $(git merge-base HEAD main) --run`): 0 failed.
- First full gate, on d9bd4082 (before merging main): failed, 14685 passed, 3 failed
  (`gate-result-d9bd4082-failed.json`). All three failures were
  `tests/test_gate_integrity.py::test_interrupted_gate_cannot_record_pass[*]`. They pass outside the gate (3 passed).
  This is the known main failure described in AR-1's report: inside the gate, `tools/lake_outputs.py` looked for
  `lean` under the gate's replacement HOME. AR-1's fix (320391aa) reached `main` at 11676c2c, after this branch's
  base 49de179e, so I merged `main` instead of rerunning the failed tests.
  This branch changes neither file.
- After the merge: `tests/test_relay_mutation_gate.py`, `tests/test_service_schema*.py` and
  `tests/test_gate_integrity.py`: 64 passed. M1–M4 are still killed and S1 still survives. `regen_generated.py --check`
  passes (24 entries).
- Full gate on the final HEAD: `docs/fix-main-relay/gate-result.json`.
- Operational note: my first attempt at the gate used `--workers auto`. At load 64 on 32 cores it picked 1 xdist
  worker, so I stopped it at about 47% and started `--workers 8` on the same commit. That stop only reached the
  `setsid` wrapper, so the 1-worker gate kept running alongside the second one until I killed its process group.
  The saved d9bd4082 record is the `--workers 8` run; the 1-worker run never wrote a final record.
