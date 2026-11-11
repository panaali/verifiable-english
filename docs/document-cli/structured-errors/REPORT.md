# document-cli-structured-errors: report

Feature item document-cli-structured-errors (queue rank 120; follow-up filed by the DRI decider,
reviews/dri-decisions-20261110-df-5b.md item 2, found at df-5b ff7c9e31bb). Branch
feature/document-cli-structured-errors, base main 8eda0371fd. Statement gate: none (Python error presentation only).
Trust: none (no Lean changed; no trusted definition added).

SIZE: 28 product, 279 tests lines added (`git diff --numstat $(git merge-base HEAD main)`, after review fix 1:
ve/__main__.py +15 −6, ve/errors.py +9, ve/acts.py +4 −5; tests/test_document_cli_errors.py +264,
tests/test_judgments_document.py +15 −13), plus this directory's DELTA.md, REPORT.md and mutants.json; docs/codemap/
is generated and not counted.

## Deliverables

| Task line | Delivered | Commit and test |
| --- | --- | --- |
| (1) The document subcommand's `VEError`s go through the same handler as the other subcommands: `{status, error}` on stdout, exit 2, exit 4 for `ResourceLimit`; no second copy of the status mapping | yes. `ve.errors.diagnostic_answer` is the one owner of the mapping (after review F1; it keys on the class, `isinstance(exc, ResourceLimit)`); `_emit_error` (ve/__main__.py) prints it, and `ve acts` (ve/acts.py) calls it in place of its own copy; the two existing copies (`senses check`'s handler and `_main`'s final handler) call it, and `_main`'s `document` route catches `VEError` and calls it | 135c677421; `test_document_errors_are_structured[*]` |
| (1) `CheckerUnavailable` keeps today's output and exit code | yes: it is a `RuntimeError`, not a `VEError`, so it still reaches `main`'s own handler (exit 5) | 135c677421; `test_checker_unavailable_is_unchanged[check, readings]` |
| (2) One case per error class on `ve document check` and `ve document readings`, asserting status, code, message, exit code and no traceback | yes: InvalidInput (`--under` without `--conclusion`, `readings`; the check is a `readings` argument), UnsupportedProfile (`weighing@0` at load, `check` and `readings`), ResourceLimit (front matter nested 200,000 deep, `check` and `readings`), CheckerUnavailable (`check` and `readings`). Each compares the whole record with the `to_dict()` of the exception `ve.document.cli.main` raises for the same argv. One process case (`test_under_without_conclusion_prints_no_traceback`) checks exit 2 and stderr as a caller sees them | tests/test_document_cli_errors.py |
| (2) df-5b's weighing CLI test stays green unchanged | yes: it calls `ve.document.cli.main`, which still raises; it is not edited | `uv run pytest -q tests/test_defaults_zone_cli.py -k weighing_documents_are_refused`: `1 passed, 6 deselected` |
| Existing callers of the old behaviour | tests/test_judgments_document.py's `ve_check` caught the `VEError` that escaped `ve document check` and called it exit 1. It now reads the command's structured answer; its six refusal asserts check exit 2 and status `InvalidInput` (helper `refusal`) and keep their texts (Lean's) unchanged. No other caller of `main(["document", ...])` or `python -m ve document` depended on the traceback (`grep -rnE 'main\(\[\s*"document"'` over tests/, docs/, tools/, usecases/, conformance/: test_rights_open_act_is_open.py and test_discourse_composed_route.py, both success or exit-5 paths) | 8df900270f; `tests/test_judgments_document.py`: `74 passed` |
| ve/document/cli.py's command logic untouched | yes: no file under ve/document/ changed | `git diff --name-only main...HEAD` |

Not delivered: none.

## Base and head

The `--under` case, with a one-unit `ve-document@1` written by `tests.test_document.write_doc` (the base route only
called `ve.document.cli.main`, which `python -m ve.document` runs):

- base path (`python -m ve.document readings sample.ve.md --under s:0`): `exit=1`, 0 bytes on stdout, last stderr line
  `ve.errors.VEError: --under requires --conclusion`.
- head (`python -m ve document readings sample.ve.md --under s:0`): `exit=2`, stdout
  `{"status": "InvalidInput", "error": {"code": "InvalidInput", "message": "--under requires --conclusion"}}` (indented).

On base the `weighing@0` fixture (docs/defeasible/df-5b/fixtures/weighing.ve.md) on `check` and on `readings` printed a
traceback ending `ve.errors.UnsupportedProfile: UnsupportedProfile: Unsupported profile weighing@0` (probed in this
worktree before the fix).

## Seeded bugs (docs/document-cli/structured-errors/mutants.json)

All are in Python, the only product language changed (ve/__main__.py; after review fix 1 also ve/errors.py and
ve/acts.py). Each was planted on the committed fix, the
test file run (`uv run pytest -q tests/test_document_cli_errors.py`), and the file restored with `git checkout`.

| Id | Bug | Failing tests |
| --- | --- | --- |
| M1 | `_emit_error` returns 2 for `ResourceLimit` | `[limit-check]`, `[limit-readings]` (2 failed, 6 passed) |
| M2 | the `document` route calls `document_main` with no handler (the base) | `[under]`, `[weighing-check]`, `[weighing-readings]`, `[limit-check]`, `[limit-readings]`, `test_under_without_conclusion_prints_no_traceback` (6 failed, 2 passed) |
| M3 | the `document` route catches `(VEError, CheckerUnavailable)` and sends both to `_emit_error` | `test_checker_unavailable_is_unchanged[check]`, `[readings]` (2 failed, 6 passed) |
| M1 (rerun, review fix 1) | `diagnostic_answer` returns 2 for `ResourceLimit` (the mapping's new home, ve/errors.py) | `[limit-check]`, `[limit-readings]`, the three `[relayed-limit-*]`, every `ResourceLimit` row of `test_every_relayed_code_gets_the_answer_of_its_class` and of `test_every_command_line_answers_a_relayed_limit_by_its_class` |
| M4 | `diagnostic_answer` keys on `exc.code == "ResourceLimit"` (review F1's bug) | 19 failed, 85 passed: `[relayed-limit-check, -readings, -coverage]`, the five wire-coded limit rows of `test_every_relayed_code_gets_the_answer_of_its_class`, the ten wire-coded limit rows of `test_every_command_line_answers_a_relayed_limit_by_its_class`, `test_no_product_code_asks_an_exceptions_class_by_its_code` |
| M5 | ve/acts.py keeps its own code-keyed copy (F1's same class at ve/acts.py:149) | 3 failed: `[acts-SOFT_RESOURCE_LIMIT]`, `[acts-ACTS_RESOURCE_LIMIT]`, the lint |
| M6 | `_senses_subcommand` keeps main's code-keyed copy (F1's same class at ve/__main__.py:154) | 3 failed: `[senses-SOFT_RESOURCE_LIMIT]`, `[senses-ACTS_RESOURCE_LIMIT]`, the lint |

## Tests run

- `uv run pytest -q tests/test_document_cli_errors.py`: `8 passed`.
- `uv run pytest -q tests/test_defaults_zone_cli.py -k weighing_documents_are_refused`: `1 passed`.
- `uv run python tools/regen_generated.py --write` once (the new test file is an input of docs/codemap/): exit 0,
  `wrote 40 entries`; committed as 6fb097ea67. It also brought codemap pages that were already behind on main up to date
  (docs/codemap/docs__act-phrases.md and others); no hand edit.
- Selected run on bcd1899887 (committed, clean): `MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base $(git
  merge-base HEAD main) --run`, 309/593 units, ran on the VM: exit 1, one failed file, tests/test_judgments_document.py
  (3 failed, 71 passed: the three refusal tests above, `assert (2 == 1)`); every other unit passed (log lines
  `chunked ...: 0 failed`). Fixed in the next commit; the three failed ids rerun through `mac-pytest.sh -- <ids>`:
  `3 passed`, exit 0. None of the failures is in main-known-red.txt.
- No trust_mutants sweep: no Lean changed and no trusted definition was added (Trust: none). The light-lane check
  (`light-lane.py check`) printed `NOT 184 changed lines outside generated files > 150`; the excess is this item's
  docs, and the task asks for no trust_mutants record.

Review fix 1 (F1), on 2657372bec:
- PROBE F1 before the fix (4e8abe7538 code): `AssertionError: (2, 'InvalidInput')`. After: `ve document check`,
  `readings` and `coverage` on the probe's 300-rule document each give exit 4, status `ResourceLimit`, `error`
  `{"code": "SOFT_RESOURCE_LIMIT", "message": "ResourceLimit: rules", "diagnostic": {... "class": "ResourceLimit" ...}}`.
- `uv run pytest -q tests/test_document_cli_errors.py`: `104 passed`.
- Selected run (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, ran on GitHub Actions, 6
  shards): exit 0, 115 units, 115 passed (tests/test_document_cli_errors.py, tests/test_acts_readings_lean.py,
  tests/test_judgments_document.py and the senses CLI tests among them).
- `lake build`: `Build completed successfully (1406 jobs)`; `python3 lean/audit.py`: `PASS: 854 source files`.

Pilot bytes expected to move: none (pilots run `ve document` on documents that load; only a run that fails changes
from a traceback to a structured answer). Estimate only; nothing is claimed before a pilot audit.

## Notes for the DRI

- The handler takes `VEError` only, as the task says. Other exceptions under `ve document` still print a traceback:
  a missing file (`FileNotFoundError`), a `--conclusion` file that is not JSON (`json.JSONDecodeError`, read by
  `json.loads` in ve/document/cli.py). The other subcommands' final handler maps `(OSError, ValueError)` to
  `InvalidInput`, exit 2. Widening the document route the same way would be a further delta; not done here.
- A document over `MAX_DOCUMENT_BYTES` is refused with `VEError("document byte budget exceeded")`, code `InvalidInput`
  (exit 2), not `ResourceLimit` (exit 4); the task's "ResourceLimit from an over-size input" case therefore uses the
  reader's depth limit (`ResourceLimit: JSON front matter nesting exceeds the parser's depth`), the `ResourceLimit` the
  document reader raises. The byte-budget code is ve/document/source.py's and is not changed here.

- Review fix 1 (F1) removes the class "a limit asked by its code": `diagnostic_answer` is the one mapping for
  `ve document`, `ve senses resolve`/`propose-readings`, the final handler and `ve acts`, and an AST lint over ve/
  (`test_no_product_code_asks_an_exceptions_class_by_its_code`) refuses any comparison of an exception's `.code` with
  a diagnostic class's code. It found exactly the two sites the review named (ve/__main__.py's helper, ve/acts.py:149).
  The review filed ve/acts.py as a FOLLOW-UP (acts-cli-coded-resource-limit); it is fixed here, by the same helper, so
  that row can close. `ve acts readings`' own relay codes its rejections by class, so the case is tested by a relayed
  `ACTS_RESOURCE_LIMIT` exception injected at `ve.acts.readings`, not end to end.
- Not changed (FOLLOW-UP candidates, all on main): `ve bundle check` and `ve definitions` answer every `VEError`,
  a `ResourceLimit` too (for example `_read`'s over-size input), as `InvalidInput`, exit 2: not a code comparison but
  a fixed status; changing their exit code is a delta no ruling here signs. ve/argument.py:680 compares a recorded
  error row's `code` with `"ResourceLimit"`; its rows come from certificate replay and countermodel check, whose relays
  code rejections by class (no wire contract), so it is not reachable with a wire code today.

Next item: none in this stream.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed answer, schema or route changed; `_emit_error` prints the
   exception's own `to_dict()`).
2. Deliverables built, no rule broken: PASS (Deliverables table; one owner of the status mapping,
   `ve.errors.diagnostic_answer`: `_emit_error` and ve/acts.py call it, the former copies are gone; no report test).
3. Tests can fail: PASS (M1-M6 in mutants.json, each with its failing tests; the lint has
   `test_the_lint_sees_each_spelling`).
4. Python, Lean and Rust agree: N.A. (Python presentation only; `test_document_errors_are_structured` compares the CLI
   record with the exception the command raises).
5. R8 binding: N.A. (no field read from a Lean answer).
6. Gate evidence matches final HEAD: PASS for what this item runs (the chain runs the gate on the final HEAD; no batch
   evidence lists are saved by this item).
7. No unsigned item: PASS (DELTA D1 and D2 cite R1; no trust growth).
8. Every user-visible change in DELTA: PASS (D1; D2 for review F1's change to senses, the final handler and acts; the codemap regeneration is generated, no user-visible delta;
   `_emit_error` in `senses check` and `_main` prints what the two copies printed: same expression, moved).
9. Test selection finds the tests: PASS (`select_tests.py` lists tests/test_document_cli_errors.py; the selected run
   found the three tests/test_judgments_document.py cases the change broke).
10. Lean statements: N.A. (no Lean).
11. Budgets fail closed: PASS (`test_document_errors_are_structured[limit-check, limit-readings]`: the reader's
    `ResourceLimit` gives status `ResourceLimit`, exit 4; after review F1 also Lean's relayed limit,
    `[relayed-limit-check, -readings, -coverage]`, and every wire-coded limit on every command line).
12. No CPU or memory regression: N.A. (one `try` around the route; no new work).
13. Test-removed trailers: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS (refused direction: the five error cases; the other
    direction: `test_checker_unavailable_is_unchanged` and test_judgments_document's success cases, `code == 0`;
    claims cite commands above; task text and R1 re-read).
15. No overclaim / no silent cut / every check can fail / limits charged: PASS (Notes name what the handler does not
    cover; nothing cut; M1-M3; the limit is the reader's own, unchanged).
