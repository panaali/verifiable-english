# document-cli-structured-errors: report

Feature item document-cli-structured-errors (queue rank 120; follow-up filed by the DRI decider,
reviews/dri-decisions-20261110-df-5b.md item 2, found at df-5b ff7c9e31bb). Branch
feature/document-cli-structured-errors, base main 8eda0371fd. Statement gate: none (Python error presentation only).
Trust: none (no Lean changed; no trusted definition added).

SIZE: 9 product, 80 tests, 3 other hand-written lines (`git diff --numstat $(git merge-base HEAD main)`:
ve/__main__.py +14 −5, tests/test_document_cli_errors.py +80; the docs under this directory are evidence, and
docs/codemap/ is generated).

## Deliverables

| Task line | Delivered | Commit and test |
| --- | --- | --- |
| (1) The document subcommand's `VEError`s go through the same handler as the other subcommands: `{status, error}` on stdout, exit 2, exit 4 for `ResourceLimit`; no second copy of the status mapping | yes. `_emit_error` (ve/__main__.py) is now the one owner of the mapping; the two existing copies (`senses check`'s handler and `_main`'s final handler) call it, and `_main`'s `document` route catches `VEError` and calls it | 135c677421; `test_document_errors_are_structured[*]` |
| (1) `CheckerUnavailable` keeps today's output and exit code | yes: it is a `RuntimeError`, not a `VEError`, so it still reaches `main`'s own handler (exit 5) | 135c677421; `test_checker_unavailable_is_unchanged[check, readings]` |
| (2) One case per error class on `ve document check` and `ve document readings`, asserting status, code, message, exit code and no traceback | yes: InvalidInput (`--under` without `--conclusion`, `readings`; the check is a `readings` argument), UnsupportedProfile (`weighing@0` at load, `check` and `readings`), ResourceLimit (front matter nested 200,000 deep, `check` and `readings`), CheckerUnavailable (`check` and `readings`). Each compares the whole record with the `to_dict()` of the exception `ve.document.cli.main` raises for the same argv. One process case (`test_under_without_conclusion_prints_no_traceback`) checks exit 2 and stderr as a caller sees them | tests/test_document_cli_errors.py |
| (2) df-5b's weighing CLI test stays green unchanged | yes: it calls `ve.document.cli.main`, which still raises; it is not edited | `uv run pytest -q tests/test_defaults_zone_cli.py -k weighing_documents_are_refused`: `1 passed, 6 deselected` |
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

All three are in Python, in ve/__main__.py (the only product file changed). Each was planted on the committed fix, the
test file run (`uv run pytest -q tests/test_document_cli_errors.py`), and the file restored with `git checkout`.

| Id | Bug | Failing tests |
| --- | --- | --- |
| M1 | `_emit_error` returns 2 for `ResourceLimit` | `[limit-check]`, `[limit-readings]` (2 failed, 6 passed) |
| M2 | the `document` route calls `document_main` with no handler (the base) | `[under]`, `[weighing-check]`, `[weighing-readings]`, `[limit-check]`, `[limit-readings]`, `test_under_without_conclusion_prints_no_traceback` (6 failed, 2 passed) |
| M3 | the `document` route catches `(VEError, CheckerUnavailable)` and sends both to `_emit_error` | `test_checker_unavailable_is_unchanged[check]`, `[readings]` (2 failed, 6 passed) |

## Tests run

- `uv run pytest -q tests/test_document_cli_errors.py`: `8 passed`.
- `uv run pytest -q tests/test_defaults_zone_cli.py -k weighing_documents_are_refused`: `1 passed`.
- `uv run python tools/regen_generated.py --write` once (the new test file is an input of docs/codemap/): exit 0,
  `wrote 40 entries`; committed as 6fb097ea67. It also brought codemap pages that were already behind on main up to date
  (docs/codemap/docs__act-phrases.md and others); no hand edit.
- Final selected run: see "Final selected run" below.

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

Next item: none in this stream.
