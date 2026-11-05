# ap-rust-replay-decode: the agent-policy replays refuse undecodable or too-deep output

Summary (review F1 of ap-rust-replay, regraded A, repair-first):
- `usecases/agent-policy/check.py` now reads the Rust and Lean replays' stdout as bytes; `parsed` (:745) decodes it as strict UTF-8 and parses it.
- Output that is not UTF-8, not JSON, or too deeply nested to parse (RecursionError) raises `CheckerUnavailable` instead of a traceback.
- `cli` (:1028) reports a `CheckerUnavailable` as one stderr line with exit code 1, the same exit code an uncaught refusal had before.
- Python relay only (R8): no verdict logic moved, `results.json` is unchanged, trust +0, no DELTA file. Report directory: `docs/usecases/agent-policy/ap-rust-replay-decode/`, beside `ap-rust-replay/`.

## 1. Deliverables

| Task deliverable | Where | Test |
|---|---|---|
| (1) Rust stdout read as bytes and decoded as strict UTF-8; non-UTF-8 refused | `replay_rust` :787 (no `text=True`, input sent as `json.dumps(...).encode()`), `rust_values` :763 → `parsed` :745 | `test_rust_values_refuses_bad_output[not UTF-8]`, `test_rust_replay_refuses_bad_output_of_the_binary[not UTF-8]` |
| (1) The Lean route call had the same fault; fixed the same way | `replay_lean` :735, :737 | `test_lean_replay_refuses_bad_output_of_the_route[not UTF-8]` |
| (2) RecursionError caught where the output is parsed (Rust and Lean) | `parsed` :756 | `test_rust_values_refuses_bad_output[too deep]`, `test_rust_replay_refuses_bad_output_of_the_binary[too deep]`, `test_lean_replay_refuses_bad_output_of_the_route[too deep]` |
| (3) The harness reports the refusal and its exit code, not a traceback | `cli` :1028 | `test_the_harness_reports_the_refusal_and_exits_1_without_a_traceback[not UTF-8]`, `[too deep]` |

The tests are in a new file, `tests/test_agent_policy_replay_decode.py` (4 tests, 2 cases each: 8). The fake binaries are executables in
`tmp_path` that read the request and write the bad bytes: `[{"id": "0", "status": "Satisfied\xff"}]` (a real 0xff
byte, not the valid string `"\xff"` that `tests/test_agent_policy.py` already used) and a 500,000-deep array.
The harness test runs `check.cli(["replay"])` in a child process, with `RUST` set to the fake binary, `LEAN_ROUTE`
set to a missing path (so the Lean replay is skipped) and `EVIDENCE` set to a file in `tmp_path`. It asserts exit code 1, a stderr
that starts with `CheckerUnavailable: Rust replay: ...`, and no `Traceback`.

The refusal path itself is unchanged: `CheckerUnavailable`, as for a bad row. Before this item, `check.py` had no
handler, so every refusal ended as a traceback with exit code 1. `cli` keeps exit code 1 and prints only the message.
`tests/test_agent_policy.py::_replay_with` (:329) now hands the stub's text to the replay as UTF-8 bytes, as the
binary does (3 lines).

Lean route, as found: `replay_lean` called the route with `text=True` and `json.loads(done.stdout)` with no handler at
all, so a 0xff byte, any non-JSON output or a 500k-deep array escaped as a traceback. All three now give `CheckerUnavailable`.
The rows the Lean route returns are still not typed or bound (`row.get` on a non-dict, `zip` over a short answer), and
neither replay reads the return code (review F2). Neither is in this task: FOLLOW-UP below and `ap-rust-replay-out`.

`usecases/asimov-extended/asimov_extended_check.py` starts no subprocess and parses no replay output (grep for
`subprocess` and `text=True`: no match), so no FOLLOW-UP `ap-rust-replay-decode-ax` is needed. The review names one
more site of the same kind outside this task's files: `usecases/claude-constitution-excerpt/verify_definitions.py:33`
(`text=True`, `json.loads` with no handler). It is not edited here (FOLLOW-UP below).

## 2. Size, trust, results

- `git diff --numstat $(git merge-base HEAD main)`: `usecases/agent-policy/check.py` +28 −8,
  `tests/test_agent_policy.py` +3 −2, `tests/test_agent_policy_replay_decode.py` +81, plus this report and `mutants.json`.
  The product change is within the 20–60 lines the task gives; the tests and the report add the rest.
- Trust +0: no Lean or Rust file changed, and no new trusted definition. No DELTA file: the only user-visible change is a
  refusal message in place of a traceback, with the same exit code; the task leaves DELTA out.
- `results.json` is unchanged (not in the diff). The real replays still pass with the bytes path: the selected run
  included `tests/test_agent_policy_rerun.py` (exit 0) with both `lean/.lake/build/bin/ve_conformance` and
  `rust/target/release/ve` present, so `test_lean_replays_every_certificate_of_the_rerun` and
  `test_rust_replay_of_the_rerun_equals_the_committed_m9` ran on real output.
- Pilot bytes expected to move: 0 (a harness refusal path; no verdict or document text changes).

## 3. Seeded bugs (Python; the only language changed)

Each was planted in `usecases/agent-policy/check.py`, run with the one test named, then restored with `git checkout`.
Recorded in `mutants.json`.

| # | Mutant | Failing test |
|---|---|---|
| S1 | drop the decode check: `stdout.decode("utf-8", "replace")` | `tests/test_agent_policy_replay_decode.py::test_rust_values_refuses_bad_output[not UTF-8]` |
| S2 | drop the `except RecursionError` clause | `tests/test_agent_policy_replay_decode.py::test_rust_values_refuses_bad_output[too deep]` |
| S3 | Lean replay parses with `json.loads(done.stdout)` again | `tests/test_agent_policy_replay_decode.py::test_lean_replay_refuses_bad_output_of_the_route[not UTF-8]` |
| S4 | `cli` re-raises instead of `sys.exit(...)` | `tests/test_agent_policy_replay_decode.py::test_the_harness_reports_the_refusal_and_exits_1_without_a_traceback[not UTF-8]` |

## 4. Checks run on the final code

- `uv run pytest -q tests/test_agent_policy_replay_decode.py`: 8 passed; `tests/test_agent_policy.py -k rust`: 55 passed.
- `uv run python tools/regen_generated.py --check`: exit 0 (no generated file is stale).
- `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`: exit 0, 36 units, 0 failed (ran on the VM:
  the coverage maps could not be sent to ve-mac-1).
- No Lean change, so no lake build, `lean/audit.py` or trust_mutants run. Full gate: run by the chain on the final HEAD.

## 5. Next item

None in this use case. Follow-ups:

FOLLOW-UP: ap-rust-replay-decode-lean agent-policy `replay_lean`: type and bind each Lean route row (non-list answer, non-dict row, short answer)
FOLLOW-UP: ap-rust-replay-decode-cc claude-constitution-excerpt `verify_definitions.py:33`: strict UTF-8 decode and RecursionError refusal for the Lean and Rust replays

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: PASS for decoding and nesting depth: `test_lean_replay_refuses_bad_output_of_the_route[not UTF-8]`, `[too deep]`. Typing each Lean row is left to FOLLOW-UP ap-rust-replay-decode-lean.
2. Every deliverable built: PASS, table in section 1; no deliverable cut.
3. Tests can fail: PASS, S1–S4 in section 3 and `mutants.json`.
4. Python, Lean, Rust agree, valid inputs still pass: PASS, `test_rust_replay_of_the_rerun_equals_the_committed_m9`, `test_lean_replays_every_certificate_of_the_rerun`, `test_a_genuine_rust_row_is_counted`.
5. R8 binding: PASS, unchanged row checks: `test_rust_output_not_bound_to_the_request_is_refused`, `test_rust_rows_in_the_wrong_order_are_refused`.
6. Gate evidence matches the final HEAD: N.A., the chain runs the gate on the final HEAD.
7. No unsigned item: N.A., no DELTA row and no trust growth.
8. Every user-visible change in DELTA: N.A., the task leaves DELTA out (a refusal message in place of a traceback, same exit code 1: `test_the_harness_reports_the_refusal_and_exits_1_without_a_traceback`).
9. Test selection: PASS, the selected run listed `tests/test_agent_policy_replay_decode.py`, `tests/test_agent_policy.py` and `tests/test_agent_policy_rerun.py`.
10. Lean statements: N.A., no Lean change.
11. Budgets, limits and deadlines fail closed: PASS, the 500k-deep fixture ends in `CheckerUnavailable`: `test_rust_replay_refuses_bad_output_of_the_binary[too deep]`. The size of stdout is not limited here (no limit is stated for this harness).
12. No CPU or memory regression: N.A., the decode adds one pass over stdout to the same `json.loads`.
13. `Test-removed` trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS, the genuine row is still counted (`test_a_genuine_rust_row_is_counted`) and the bad outputs are refused (section 1 tests).
15. Overclaim, silent cut, new checks can fail, limits charged: PASS. Each "no"/"all" claim in this report names its test or grep. No deliverable was cut. Each new check has a mutant (S1–S4). Limits: N.A., no new evaluator or limit.
