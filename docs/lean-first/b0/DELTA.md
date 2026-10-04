# Lean-first batch 0: DELTA

Base `62a5c589` (tag `lean-first/oracle-python`), head `lean-first/b0`. Gate item 2 of
`docs/LEAN-FIRST-PLAN.md` 5.1: every public result of the corpora below, base against head, by
`tools/lean_first_diff.py` (record each commit from its own checkout and builds, then `compare --delta
docs/lean-first/b0/delta.json`).

## Result

| Corpus | Records per side | Same | Wording | Order | Verdict | Availability |
|---|---:|---:|---:|---:|---:|---:|
| probe, `python` | 9,435 | 6,258 | 3,177 | 0 | 0 | 0 |
| probe, `lean` | 9,435 | 6,258 | 3,177 | 0 | 0 | 0 |
| conformance, `python` | 19,806 | 19,773 | 33 | 0 | 0 | 0 |
| conformance, `lean` | 19,806 | 19,773 | 33 | 0 | 0 | 0 |
| pilots (`ve document check`, default authority) | 214 | 214 | 0 | 0 | 0 | 0 |
| **All** | 58,696 | 52,276 | 6,420 | 0 | 0 | 0 |

`compare` exits 0 with `"unlisted": 0` (head recorded at `bd59c8f4`, whose `ve/` and `lean/` are those of
`385311aa`; head recording 8 min 51 s wall). Every difference is a wording change of list W1, and every W1 pair
is used (the record counts below are the head run's). The corpora show no `order`, `verdict` or
`availability` change. The one availability change of the batch, A1 below, is on the readings route, which none
of these corpora reaches.

## W1: Python's texts for Lean-prefixed codes are Lean's (`wording`, signed as one block)

Python's own checkers now write the four codes Lean writes as `Code: text` the same way
(`UnknownSymbol`, `TypeMismatch`, `UnboundVariable`, `UnsupportedProfile`: `ve/errors.py` `_CodeWorded`),
and `_Checker`'s three budget messages start `ResourceLimit: ` (`ve/ast.py`). Under `VE_AUTHORITY=lean` the
relay shows Lean's text verbatim, which is now the same text. Before this batch the client stripped Lean's
prefix so that Lean read as Python (`backends/diagnostics.py` `_UNPREFIXED`, deleted). The texts outside these
codes are unchanged. The pairs below are every distinct base-to-head text the corpora produced
([`delta.json`](delta.json)); the rule is the same for every message of these codes, including ones no
corpus reached.

| Id | Base | Head | Records |
|---|---|---|---:|
| W1.1 | `AST exceeds 10,000 nodes` | `ResourceLimit: AST exceeds 10,000 nodes` | 2 |
| W1.2 | `Equality requires one sort, received 'person' and 'service'` | `TypeMismatch: Equality requires one sort, received 'person' and 'service'` | 4 |
| W1.3 | `Equality requires one sort, received 'service' and 'person'` | `TypeMismatch: Equality requires one sort, received 'service' and 'person'` | 2 |
| W1.4 | `Formula exceeds 64 nesting levels` | `ResourceLimit: Formula exceeds 64 nesting levels` | 2 |
| W1.5 | `Invalid variable index` | `UnboundVariable: Invalid variable index` | 2 |
| W1.6 | `Predicate 'deployed' expects ('service',), received ('person',)` | `TypeMismatch: Predicate 'deployed' expects ('service',), received ('person',)` | 6 |
| W1.7 | `Predicate 'owns' expects ('person', 'service'), received ('service', 'service')` | `TypeMismatch: Predicate 'owns' expects ('person', 'service'), received ('service', 'service')` | 4 |
| W1.8 | `Predicate 'owns' has arity 2, not 1` | `TypeMismatch: Predicate 'owns' has arity 2, not 1` | 2 |
| W1.9 | `Undeclared predicate argument sort: 'absent'` | `UnknownSymbol: Undeclared predicate argument sort: 'absent'` | 230 |
| W1.10 | `Undeclared predicate argument sort: 'unknown'` | `UnknownSymbol: Undeclared predicate argument sort: 'unknown'` | 2 |
| W1.11 | `Unknown binder sort 'missing'` | `UnknownSymbol: Unknown binder sort 'missing'` | 2 |
| W1.12 | `Unknown binder sort 5` | `UnknownSymbol: Unknown binder sort 5` | 2 |
| W1.13 | `Unknown predicate 'missing'` | `UnknownSymbol: Unknown predicate 'missing'` | 1612 |
| W1.14 | `Unknown predicate 5` | `UnknownSymbol: Unknown predicate 5` | 2 |
| W1.15 | `Unsupported language, semantic profile, or specification revision` | `UnsupportedProfile: Unsupported language, semantic profile, or specification revision` | 2 |
| W1.16 | `Variable index 0 is outside its scope` | `UnboundVariable: Variable index 0 is outside its scope` | 2 |
| W1.17 | `admission of documents with definitions is deferred` | `UnsupportedProfile: admission of documents with definitions is deferred` | 32 |
| W1.18 | `admission on the closure family is deferred` | `UnsupportedProfile: admission on the closure family is deferred` | 128 |
| W1.19 | `admission on the order family is deferred` | `UnsupportedProfile: admission on the order family is deferred` | 32 |
| W1.20 | `definitions on the order family require an order definition layer` | `UnsupportedProfile: definitions on the order family require an order definition layer` | 2208 |
| W1.21 | `definitions@0 required` | `UnsupportedProfile: definitions@0 required` | 268 |
| W1.22 | `norm document admission is FOL-only` | `UnsupportedProfile: norm document admission is FOL-only` | 320 |
| W1.23 | `norms@0 required` | `UnsupportedProfile: norms@0 required` | 1062 |
| W1.24 | `unbound variable 'broken'` | `UnboundVariable: unbound variable 'broken'` | 460 |
| W1.25 | `unbound variable 's'` | `UnboundVariable: unbound variable 's'` | 8 |
| W1.26 | `unbound variable 'trueish'` | `UnboundVariable: unbound variable 'trueish'` | 4 |
| W1.27 | `unknown binary predicate 'deployed'` | `UnknownSymbol: unknown binary predicate 'deployed'` | 4 |
| W1.28 | `unknown constant 'missing'` | `UnknownSymbol: unknown constant 'missing'` | 4 |
| W1.29 | `unknown sort 'absent'` | `UnknownSymbol: unknown sort 'absent'` | 4 |
| W1.30 | `unknown unary predicate 'absent'` | `UnknownSymbol: unknown unary predicate 'absent'` | 4 |
| W1.31 | `unknown unary predicate 'owns'` | `UnknownSymbol: unknown unary predicate 'owns'` | 4 |

**Signature:** DRI, wording block W1 — pending.

## A1: the readings route answers where Python's text differed from Lean's only by the code (`availability`)

`ve/readings_route.validate` compares Python's regeneration with Lean's row and raises `CheckerUnavailable`
when they differ. Where the only difference was the `Code: ` prefix W1 now gives Python's text, the two agree,
and the route raises Lean's diagnostic instead of `CheckerUnavailable`. The suite has one such input: the
rights document of `tests/test_readings_s1_lean.py` over an environment without (or with a null)
`vocabulary.predicates.arbitrary_arrest`.

| Id | Input | Base | Head |
|---|---|---|---|
| A1 | readings-validate, rights document, `arbitrary_arrest` absent or null | `CheckerUnavailable` (`ReadingsConformance: Python and Lean differ on readings-validate`) | `VEError` `UnknownSymbol: Unknown predicate 'arbitrary_arrest' under rs9@1:0` (Lean's row, now Python's too) |

Tested by `test_a_text_that_differed_only_by_the_code_prefix_gets_leans_diagnostic`. The base's
`test_explicit_null_is_absent_in_the_environment` pinned the old answer (`_known_text_difference`) and passed at
the base. The other known text differences of that test (decoder texts, Lean's content decoder answering first)
are unchanged. The rule extends to any readings-validate input whose two texts differed only by one of W1's
prefixes. No other public path compares Python's text with Lean's: the soft route's restatement
(`softnorms._DROPPED_PROFILE_TEXTS`) matches a text that already carried its prefix, and the dispatch shadow
only records.

**Signature:** DRI, availability A1 — pending.

## Rest of the gate (5.1)

- **Suite (item 1).** The full suite ran at `e6356cd6` (16 chunks and the English merge smoke,
  `VE_NATIVE_PREBUILT=1`). It had three failures, all fixed in `bd59c8f4`: A1's pinned base answer, W1.1's
  pinned base text (`test_norm_defaults.py`), and the reviewed broad handler's new name (`run_bound.worker`, in
  `ve/assurance-manifest.json`). The re-run of those files passed (315 tests), and so did `test_gate_collection.py`
  after `tools/gate_collection.py --write` (9 IDs added, none removed). Every other test passed. Gate stages
  outside pytest, on the head: `tools/wire_contract.py --check`, `lake build` and `lean/audit.py` (287 files,
  3,045 theorems, standard axioms only) pass.
- **Differential fuzzer (item 2).** `infra/difffuzz` (`ca522bac`) merged onto the base (`dc62ee95`) and onto
  the head (`7d1872bf`, the head's `ve/` and `lean/`). CI sample: 23 new signatures on each side, the same ones,
  329 baseline entries seen and 80 not reproduced on each side. The 13 date seeds 20260921 to 20261003
  (`--deep 1` each) give the same counts on both sides, seed by seed, with no head-only signature and no baseline
  entry that reproduces on one side only. With the CI sample that is 14 seeds. The baseline does not grow.
- **Deletion ledger (item 3).** [`LEDGER.md`](LEDGER.md); `tools/relay_lint.py` passes on the head.
- **Latency (item 4).** `docs/lean-first/b0/latency.py 2000` (one warm service, single-case `check`, half
  rejections), base and head run side by side at load 34: wall p50 0.75 ms (base) against 0.71 ms (head), p95
  3.4 ms against 0.96 ms, service CPU 0.345 ms against 0.335 ms per call. The `code` beside a rejection costs no
  measurable time; both are inside section 4's budgets.

## Not in the corpora above

- **Use-case harnesses.** Not rerun by the A/B tool; their answer keys are pinned by the suite
  (`test_agent_policy_rerun`, the eligibility and other use-case tests), which passes at the head (gate item 1).
- **Theorem statements.** `VE.Service.bound` now sets the coding beside a rejection: `boundResults_eq` keeps its
  text but its `bound` changed meaning, and `bound_eq`, `coding_of_status`, `coding_error` and
  `rejectionCode_mem` are new. They need statement review (build checklist 17).
- **Diagnostics of rows with no code** (Rust, one-shot `ve_quantity`): their text is no longer stripped either.
  No corpus record reached one with a changed text.
