# Lean-first batch 0: DELTA

Base `62a5c589` (tag `lean-first/oracle-python`), head `lean-first/b0`. Gate item 2 of
`docs/LEAN-FIRST-PLAN.md` 5.1: every public result of the corpora below, base against head, by
`tools/lean_first_diff.py` (record each commit from its own checkout and builds, then `compare --delta
docs/lean-first/b0/delta.json`).

## Result

| Corpus | Records per side | Same | Wording | Order | Verdict | Availability |
|---|---:|---:|---:|---:|---:|---:|
__TABLE__

Every difference is a wording change of list W1, and every W1 pair is used. No `order`, `verdict` or
`availability` change: no answer changes, only texts.

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

## Not in the corpora above

- **Use-case harnesses.** Not rerun by the A/B tool; their answer keys are pinned by the suite
  (`test_agent_policy_rerun`, the eligibility and other use-case tests), which passes at the head (gate item 1).
- **Theorem statements.** `VE.Service.bound` now sets the coding beside a rejection: `boundResults_eq` keeps its
  text but its `bound` changed meaning, and `bound_eq`, `coding_of_status`, `coding_error` and
  `rejectionCode_mem` are new. They need statement review (build checklist 17).
- **Diagnostics of rows with no code** (Rust, one-shot `ve_quantity`): their text is no longer stripped either.
  No corpus record reached one with a changed text.
