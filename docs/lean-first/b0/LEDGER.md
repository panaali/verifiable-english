# Lean-first batch 0: deletion ledger

Plan: `docs/LEAN-FIRST-PLAN.md` (draft 3), section 5.1 item 3 and section 5.2 row 0. Base `62a5c589` (tag
`lean-first/oracle-python`). Every deleted Python decision site is mapped to the Lean check or answer that now
owns it.

## Deleted decision sites

| # | Deleted (base) | Decided | Owner now |
|---|---|---|---|
| D1 | `ve/backends/diagnostics.py` `_UNPREFIXED` and the stripping branch of `checker_error` | removed `UnknownSymbol: `, `TypeMismatch: `, `UnboundVariable: `, `UnsupportedProfile: ` from Lean's texts so they read as Python's | nobody rewords: `relay.decide` raises Lean's text verbatim; Python's own texts for these codes are Lean's (`ve/errors.py` `_CodeWorded`, DRI answer 3) |
| D2 | `ve/backends/diagnostics.py` `_UNPREFIXED_LIMITS` | removed `ResourceLimit: ` from `_Checker`'s three budget texts | the same; `ve/ast.py`'s three raise sites write Lean's text |
| D3 | `checker_error`'s classification of service rows (`partition(":")` against `_CODES`, the `InvalidModel(...)` regex, `DependencyCycle` → `InvalidInput`) | the code and generator of every Lean service rejection | `lean/VE/Service/Protocol.lean` `rejectionCode` and `codeMembers` (`coded`, theorems `coded_error`, `coded_of_status`, `rejectionCode_mem`); the client reads `code` and `generator` off the row |
| D4 | `checker_error`'s dead `Definition ` branch | none (a head starting `Definition ` is never a code) | — |
| D5 | `ve/backends/lean_service.py` `_run_chunk`: `startswith("ResourceLimit")` → `ResourceLimit`, else `VEError` | the class of a whole-request rejection | Lean's `requestError` carries `code` (`rejectionCode`); `relay.rejection` maps it |
| D6 | `ve/backends/lean_runner.py` `run` (and its pool, `_close`, `require_ok` on service rows) | which rows are errors and how they are raised | `ve/backends/relay.py` `decide`, the one Python entry; every caller switched (`admission`, `argument`, `ast` ×2, `background` ×2, `bundle`, `definitions`, `entailment`, `evaluate`, `norm_admission`, `norms` ×4, `parser`, `readings`, `search`, `backends/validation` ×2) |

No consumer of a deleted symbol remains: `git grep` over `ve/`, `tests/`, `tools/` and `conformance/` at the
head finds no use of `lean_runner.run`, `_pool` or `_close`, and no reference to `_UNPREFIXED`,
`_UNPREFIXED_LIMITS` or `_CODES`. `tools/semantic_inventory.py` cannot show it: it records top-level imports
only, and every caller imported `lean_runner.run` inside a function (the base's inventory lists no consumer of
it either).

## Retained, named

| Site | Why it stays | Removed by |
|---|---|---|
| `checker_error`'s prefix classification of rows that carry no code | the Rust JSONL checker's string errors and the one-shot `ve_quantity` row (`admission._lean_quantity_admission`) have no `code`; it is the one Python copy of `rejectionCode`'s rule, now applied only to them | batch 1 (the one-shot routes become service modes and get `code`) and batch 15b (Rust texts never reach a user) |
| `tests/test_environment_field_types.py` `_same_diagnostic` | a test-side comparison of Python's `DuplicateDeclaration` and block texts with Lean's, outside the four codes this batch changed | batches 7 and 12, with those decoders |

## Lines

Python (`ve/`, base to head, `git diff --shortstat 62a5c589 HEAD -- ve`): 141 lines deleted, 204 added. The
decision code deleted is `diagnostics.py` (39 lines out, 16 in), `lean_runner.py` (29 out, 1 in) and
`lean_service.py`'s request-error branch (+20/−14 with `run_bound`); the additions are `relay.py` (75 lines, the
entry the later batches route through), the response schemas' `code` (JSON) and 15 lines of `errors.py`. Lean
(`lean/`, +207/−18 in all): `VE/Service/Protocol.lean` +79/−5 (`rejectionCodes`, `rejectionCode`, `codeMembers`,
`coding`, five `#guard`s, the new theorems, two restated), `ResponseDecode.lean` +35/−10, `Audit.lean` +4,
`axioms.txt` +86 (generated), `checkers.lock` and `frozen-sources.sha256` repinned.
