# Wire contracts, stage S7 item 1: `alternatives@0` and `risk@0` become public (statement specification)

> Status: statement specification, draft 1 (2026-10-04). This is the item-1 statement spec of
> [wire-contract-S7-PLAN.md](wire-contract-S7-PLAN.md) draft 2 (the **plan**). It covers item 1: the two
> contracts `alternatives@0` (the alternatives source, base plan 5.3 row 9) and `risk@0` (the risk source and
> the decision record, the same row), each authored, run in shadow, measured and switched to `public`, which is
> every step of 5.1 of [wire-contract-PLAN.md](wire-contract-PLAN.md) (the **base plan**); and item 2, the one
> Rust encoding of `UnitPrecision` (2.14). It builds on [wire-contract.md](wire-contract.md) (the **base
> spec**), [wire-contract-s4.md](wire-contract-s4.md) (the **S4 spec**) and, for the tooling that takes a unit,
> [wire-contract-s5.md](wire-contract-s5.md) (the **S5 spec**, branch `design/wire-s5`), and changes no
> definition of any of them. The Astra + Fable statement review comes before any build step; no debate was
> held on stage S7 (plan, status paragraph), so that review is the first reading of everything here that the
> base plan's debate did not decide, and section 12 lists those choices. Fixtures are implementation
> obligations, not claims of completed tests. Nothing was built or run for this draft: the two tables of
> section 2 were authored by reading the two Lean routes, the expected records of section 8 were derived by
> hand from the Lean definitions, and every `file:line` reference was read on `main` at `bb05a08d` and must be
> re-read at each step. The Lean statements of section 5 and the fixture numbers of section 8 were written
> into the stub `/tmp/wire-s7-stubs/Stubs.lean` (imports the repository modules; holds `sorry` and `#eval`
> lines; never committed), but the session that wrote this draft could run no Lean, so the stub is **not
> compiled**: compiling it, with the build of `VE` on the path (`LEAN_PATH=lean/.lake/build/lib/lean lean
> /tmp/wire-s7-stubs/Stubs.lean`), is the first task of S7.0, and every number marked "derived" in section 8
> is confirmed or corrected by its `#eval` there before any fixture is written. Nothing here changes a
> verdict, an identity, a code, a frozen contract, an existing theorem statement or a checker function.

## 0. Scope, one paragraph

After S4 one contract is public and S5 adds two. Item 1 adds two more, for the two routes whose verdict is
Lean's alone. `alternatives@0` is the table of what `decodeAltSource` checks on an environment with its
`alternatives` block, the norm units and the base assertion units; `risk@0` is the table of what
`decodeRiskSource` checks on the risk source and, when the root carries a `decision`, what `admitDecision`,
`validateDecision` and `marginLimit` check on the record. Each is authored from the Lean route's order, run in
shadow against the Lean engine and the route on a generated and replayed corpus, measured, signed by the DRI
and made **public** in the one place where Python returns the route's rejection: the row that
`ve.alternatives.run_case` or `ve.risk.run_case` returns then carries the contract's record. When a check of
the table fails, the record names the first one that fails and the row's `error` is that check's text;
otherwise the `error` is the route's. The route still decides, alone, whether a case is rejected. Python has
no validator of either unit, so its engine defers at the first check that needs Lean, and the record of such
a case is fetched from `ve_diagnose` through the manifest operation `wire.diagnose`, the first production use
of the consultation that base plan 2.5 designed. Lean's route rows are frozen and do not change; Rust has no
column. Item 2 gives `UnitPrecision` one encoding in Rust's risk evaluator.

In this specification: the decisions (1), the definitions, including the two tables (2), the English, one
reading each (3), the diagnostics (4), the Lean statements and modules (5), the expected delta of each unit
(6), the files and gates of S7.0 and of each unit's measurement and switch commits (7), the acceptance
fixtures (8), the switch gate (9), limits (10), the statement review checklist (11), and the choices this
specification resolves (12).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | `alternatives@0`'s root is `{"environment", "norms", "units"}`, the members of an `alt-elaborate` case; `risk@0`'s is `{"environment", "document", "decision", "entries"}`, the members of a `risk-decision` case, with `decision` and `entries` `null` on every other kind | 2.2 |
| D2 | Each table is in the Lean route's order, the authority's, and takes every text from the route, so that on a one-fault source the record's text is the route's | 2.3, 2.4, 2.13 |
| D3 | The record's class is the class that `ve.backends.diagnostics.checker_error` gives the route's text today, the public class; it is declared per code, and inherited checks are exempt | 2.12 |
| D4 | The checks of the Lean route that are one function with many steps are classifier sets: the block's declarations, the role verbalisations, the typing of a rule, the risk block's declarations, the cited contents, the record's admission and its validation. Each maps a text by its fixed leading text; the order inside a set is the route's and test-enforced | 2.3, 2.4, 2.5 |
| D5 | Inherited checks (W1's environment and unit decoders, W6's unit checks, the typing texts) are Lean-only. Python registers every hook, classifier and view of both units as deferred (`None`), so the public text of an inherited check is always the Lean engine's | 2.5, 2.7 |
| D6 | The unit's legacy validator is the Lean route alone. The Python engine is compared only where it completes diagnosis, which is a fault in the gate phase; its deferred share is reported | 2.2, 2.13 |
| D7 | One function per unit, `public_rejection(case, row)`, in a new contract module per unit, attaches the record to an error row of the route; it returns the same row object, never writes `status` or `id`, consults `ve_diagnose` when the Python engine defers, and never raises | 2.7 |
| D8 | One production call site per unit: the branch of `run_case` that returns an error row, for the kinds `alt-elaborate`, `risk-elaborate` and `risk-decision` | 2.8 |
| D9 | The Lean routes, Python's `Environment`, `ve/risk.py`'s mirror and `VEError` are not edited | 2.2, 7.2 |
| D10 | A public change is a changed `error` text of the row; the complete list on the unit's corpus is measured, stored and signed check by check; at `public`, the gate fails on a change without a signature and on a signature without a change | 2.11, 9 |
| D11 | The decision record is in `risk@0` as phases guarded by a non-null `decision`; the record's validation is one classifier set whose members are the texts of risk.md 6, with the witness case where the route appends one | 2.4 |
| D12 | The unit registry of `ve_diagnose` gains two entries by an append-only edit of `Diagnose.lean`, the C4 exception the S5 spec records (its 5.3); the manifest operation `wire.diagnose` gains two bindings and two call sites | 5.3, 5.4 |
| D13 | `rust/ve-core/src/risk.rs` prints `UnitPrecision` as every other site does: the class `InvalidInput` with the message `UnitPrecision(<tag>, scale=<n>)` | 2.14 |

## 2. Definitions

### 2.1 Terms carried over

| Term | Meaning |
|---|---|
| record, outcome, overlay, residual record, deferred record | base spec 2.7, 2.8 |
| instance, position, order key | base spec 2.6; neither contract has an include, so no record carries a slash in `check` or an `inner_path` |
| inherited check | base spec 2.5, rule 5: a hook or member whose text is the decoder's own; its `text` and `args` are not compared between engines, and here Python has none |
| legacy validator | for each unit, the Lean route of 2.2 |
| the gate, the corpus | `conformance/wire_contract_gate.py` with the unit as its argument (S5 spec 7.1, with the additions of 7.1 here), and the cases of its `gate_cases` for that unit: tiers 0, A, B, the replayed sources (tier R) and the legacy-difference inputs (tier L) |
| a corpus case that Lean reads | S4 spec 2.1; for these units every corpus case, since the Python engine runs on nothing the Lean engine does not |
| the class rule | the rule of 2.12 that the record's `class` is `checker_error`'s class of the route's text |
| the public row | the dictionary `run_case` returns: the route's row, or after a switch the same row with `diagnostic` and possibly another `error` |

A **source** is a root of 2.2. The **legacy row** of a source is the row the Lean route returns on the case
the source builds; its **legacy text** is the row's `error` when its `status` is `error`, and its **legacy
class** is `checker_error(legacy text).code` (`ve/backends/diagnostics.py:31–52`): the leading word before a
colon when it is one of `DuplicateDeclaration`, `InvalidModel`, `ResourceLimit`, `SyntaxError`, `TypeMismatch`,
`UnboundVariable`, `UnknownSymbol`, `UnsupportedProfile`, `CheckerUnavailable`, `AdmissionError` or
`DependencyCycle` (the last gives `InvalidInput`), `InvalidModel` for a text that starts `InvalidModel(`, and
`InvalidInput` otherwise.

### 2.2 The two units: roots, adapters, domains, legacy validators

**Roots.** `alternatives@0` has `"input": ["environment", "norms", "units"]`: a `ve.core@0.2` environment
with its `alternatives` block as submitted, the array of norm objects (`{"norm": {…}}`), and the base
assertion units `[{"label", "ast"}, …]` (base plan: `units`; `lean/VE/Alternatives/Replay.lean:67–69`).
`risk@0` has `"input": ["environment", "document", "decision", "entries"]`: the environment with both blocks
and the W6 extension, the document `{"norms", "units"?}`, the decision entry and the supplied entries of a
`risk-decision` case (`lean/VE/Risk/Run.lean:362–366`). A member the case lacks is `null`.

**Adapters.** `alt_source` and `risk_source`, in Python and in Lean. For a case whose `kind` starts with
`alt-` (respectively `risk-`), the root's members are the case's members of those names, `null` when absent.
Any other kind, `admission` included, is refused with the row `{"id", "status": "error", "error":
"UnsupportedProfile: case kind <kind> has no wire contract input"}`, as the pilot's adapter refuses one. The
alternatives source inside an `admission` document is reached through `splitDocument` and the W2 decoder
(`lean/VE/Alternatives/Admission.lean:69–79`), and the W2 checks after it are row 13's: the kind is outside
both domains (plan section 4).

**Domain.** A unit's domain is the set of roots on which the route is the validator of everything the table
states. For both units that is every root the adapter builds; no root is refused for its content. On a kind
other than `alt-elaborate`, `risk-elaborate` or `risk-decision` the route goes on after the source to a
scenario, a package, a witness or a log, whose rejections have no check in the table; `ve_diagnose` still
diagnoses such a case's source, and `public_rejection` is not called on it (2.8). The gate's corpus consists of
roots; its Lean legacy case is `alt-elaborate` for `alternatives@0`, and for `risk@0` `risk-decision` when the
root's `decision` is not `null` and `risk-elaborate` otherwise (7.1).

**Legacy validators.** `alternatives@0`: `ve_alternatives_route` on the case `{"id", "kind": "alt-elaborate",
"environment", "norms", "units"}`, that is `decodeAltSource environment norms units`
(`lean/VE/Alternatives/Wire.lean:193–223`; `Run.lean:259–261`). `risk@0`: `ve_risk_route` on
`{"id", "kind": "risk-elaborate", "environment", "document"}`, that is `decodeRiskSource environment
document` (`lean/VE/Risk/Wire.lean:298–344`; `Run.lean:595–597`), or on `{"kind": "risk-decision", …,
"decision", "entries"}`, that is `decodeRiskSource`, then `decodeEntry`, `decodeSupplied`, `admitDecision`,
`validateDecision` with `withCase` on its text, and `marginLimit` (`Run.lean:362–371`). Each is defined once
as `legacy_validation(root)` in the unit's contract module (`ve/alternatives_contract.py`,
`ve/risk_contract.py`), which builds the case, runs the route through the transport of `ve/backends/lean.py`
(`run_alternatives_case`, 172–191) and returns `None` on an `ok` row or `(legacy class, legacy text)` on an
error row; `CheckerUnavailable` propagates. A row with `status` `error` is a rejection; no row of either route
carries a `code`.

**Python has no legacy validator** of either unit. `ve/alternatives.py:24` runs Python's `Environment` on the
case's environment before the route; that is a different validator (the environment only, in Python's order),
an earlier statement of the same call (2.8), and the source of S7-pre (2.12). `ve/risk.py` decodes nothing.

**No Rust column.** Rust decodes neither source and no record; it is not run on either unit. Item 2 (2.14) is
a text of the Rust evaluator that `tests/test_risk_differential.py` runs on conditions, not a contract check.

### 2.3 The contract `alternatives@0`, revision 1

**Limits and classes used.** `limits.json` gains `MAX_ALT_FULFILMENTS` 16 (`lean/VE/Alternatives/Wire.lean:108`);
`MAX_RULES` 256 and `MAX_CARVE_OUTS` 8 (S5) exist. `names.json` gains `alternatives_field` (`enum`: `action`,
`available`, `chooser`, `decided_by`, `fulfilments`, `harm`, `inaction`, `leads_to`, `outcomes`, `performed`,
`proximate`, `taken`; `Wire.lean:40–41`); `rule_name` (S5) exists.

**Codes.** The class of each code is the legacy class of its texts (D3); where a text's leading word is not
one `checker_error` knows (`AlternativesSort`, `UnknownRule`, `PrecedenceAcrossPredicates`, …), the class is
`InvalidInput`, as it is in public today.

| Class | Codes |
|---|---|
| `UnsupportedProfile` | `ALT_UNSUPPORTED_PROFILE` |
| `InvalidInput` | `ALT_INVALID_ENVIRONMENT` (inherited, exempt), `ALT_INVALID_BLOCK`, `ALT_MISSING_OUTCOME_DECIDER`, `ALT_INVALID_NORMS`, `ALT_INVALID_NORM` (inherited, exempt), `ALT_INVALID_PREMISES`, `ALT_INVALID_PREMISE` (inherited, exempt), `ALT_ILL_TYPED_PREMISE`, `ALT_SORT`, `ALT_RESERVED`, `ALT_REGULATED`, `ALT_VERBALISATION`, `ALT_PERFORMED`, `ALT_FULFILMENT_SORT`, `ALT_FULFILMENT_NOT_BASE`, `ALT_FULFILMENT_ON_PERFORMED`, `ALT_TYPING` (inherited, exempt), `ALT_INVALID_NAME`, `ALT_INVALID_RULE_FIELDS`, `ALT_UNKNOWN_RULE`, `ALT_PRECEDENCE_ACROSS_PREDICATES`, `ALT_DEPENDENCY_CYCLE`, `ALT_INVALID_INPUT` (the `residual` code) |
| `UnknownSymbol` | `ALT_UNKNOWN_SYMBOL` |
| `DuplicateDeclaration` | `ALT_DUPLICATE_DECLARATION` |
| `ResourceLimit` | `ALT_RESOURCE_LIMIT` |

**The table.** `E` abbreviates `/environment`, `B` abbreviates `/environment/alternatives` and `P`
abbreviates `/environment/vocabulary/predicates`. A row "group" opens a group; its sub-entries follow,
indented by `·`, until the next row that is not indented. Every text is the route's. The order is
`decodeAltSource`'s (`Wire.lean:193–223`): the profile gate, the block present, W1's environment decoder on
the view, no definitions and no data flags, the strict block decoder, the norm units, the base units, then
`checkBlock`, the verbalisations, `avoids`, the base units typed, then `validateAlt` (`Decl.lean:251–263`):
the rules typed over the profile words with the inlining limit, W1's `validate` on the inlined tree
(`lean/VE/Norms/Tree.lean:302–368`), the fulfilments. Three texts of the route are not in the table because
no input reaches them after the checks above (12, R3): `InvalidInput: ill-typed rule <n>`, `InvalidInput:
norm document is not stratified`, `InvalidInput: ill-typed alternatives premise`, and the fallback
`InvalidInput: alternatives block is not well-formed`; a rejection with one of them is a residual, counted.

Phase 1, `gate` (`Wire.lean:25–31, 195–197`; the Python engine runs this phase):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 1.1 | `type` `E`: object | `ALT_UNSUPPORTED_PROFILE` | `UnsupportedProfile: profiles must be a sorted unique array` |
| 1.2 | `requires` `E` member `profiles` | as 1.1 | as 1.1 |
| 1.3 | `type` `E/profiles`: array of strings | as 1.1 | as 1.1 |
| 1.4 | `sorted_unique` `E/profiles` | as 1.1 | `UnsupportedProfile: profiles must be sorted and unique` |
| 1.5 | `requires` `E/profiles` item `"alternatives@0"` | as 1.1 | `UnsupportedProfile: alternatives@0 is required` |
| 1.6 | `requires` `E/profiles` item `"norms@0"` | as 1.1 | `UnsupportedProfile: alternatives@0 requires norms@0` |
| 1.7 | `excludes` `E/profiles` item `"soft-norms@0"` | as 1.1 | `UnsupportedProfile: alternatives@0 with soft-norms@0` |
| 1.8 | `requires` `E` member `alternatives` | `ALT_INVALID_BLOCK` | `InvalidInput: alternatives.block` |

Phase 2, `environment` (`Wire.lean:198–202`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 2.1 | hook `w1_environment` at `E`, inherited | `ALT_INVALID_ENVIRONMENT` | `{message}` |
| 2.2 | hook `no_definitions` at `P` | `ALT_UNSUPPORTED_PROFILE` | `UnsupportedProfile: alternatives route with definitions is not implemented` |
| 2.3 | hook `no_data_flags` at `P` | as 2.2 | `UnsupportedProfile: alternatives route with data flags is not implemented` |

Phase 3, `block` (`decodeBlock`, `Wire.lean:78–128`; `decodeOutcomes`, `:59–69`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 3.1 | `type` `B`: object | `ALT_INVALID_BLOCK` | `InvalidInput: alternatives.block` |
| 3.2a | `requires` `B` member `action` | as 3.1 | `InvalidInput: alternatives.action` |
| 3.2b | `requires` `B` member `available` | as 3.1 | `InvalidInput: alternatives.available` |
| 3.2c | `requires` `B` member `chooser` | as 3.1 | `InvalidInput: alternatives.chooser` |
| 3.2d | `requires` `B` member `harm` | as 3.1 | `InvalidInput: alternatives.harm` |
| 3.2e | `requires` `B` member `leads_to` | as 3.1 | `InvalidInput: alternatives.leads_to` |
| 3.2f | `requires` `B` member `outcomes` | as 3.1 | `InvalidInput: alternatives.outcomes` |
| | group `fields` over `B/*` | | |
| · 3.3 | `name` on key: `alternatives_field` | as 3.1 | `InvalidInput: alternatives.{key}` |
| 3.4a | `type` `B/chooser`: string | as 3.1 | `InvalidInput: alternatives.chooser` |
| 3.4b | `type` `B/action`: string | as 3.1 | `InvalidInput: alternatives.action` |
| 3.4c | `type` `B/harm`: string | as 3.1 | `InvalidInput: alternatives.harm` |
| 3.4d | `type` `B/available`: string | as 3.1 | `InvalidInput: alternatives.available` |
| 3.4e | `type` `B/leads_to`: string | as 3.1 | `InvalidInput: alternatives.leads_to` |
| 3.5a | `type` `B/outcomes`: string or object | as 3.1 | `InvalidInput: alternatives.outcomes` |
| 3.5b | `const` `B/outcomes`: `"signed"`, when `B/outcomes` is a string | as 3.1 | as 3.5a |
| 3.5c | `requires` `B/outcomes` member `complete_by`, when `B/outcomes` is an object | `ALT_MISSING_OUTCOME_DECIDER` | `MissingOutcomeDecider: alternatives.outcomes` |
| 3.5d | `exact_keys` `B/outcomes`: `complete_by`, when `B/outcomes` is an object | `ALT_INVALID_BLOCK` | as 3.5a |
| 3.5e | `type` `B/outcomes/complete_by`: string | `ALT_MISSING_OUTCOME_DECIDER` | as 3.5c |
| 3.5f | hook `decider_nonblank` at `B/outcomes/complete_by` | as 3.5c | as 3.5c |
| 3.6a | `type` `B/decided_by`: string | `ALT_INVALID_BLOCK` | `InvalidInput: alternatives.decided_by` |
| 3.6b | `max_bytes` `B/decided_by`: 64 | as 3.1 | as 3.6a |
| 3.7a | `exact_keys` `B/performed`: `permission`, `obligation` | as 3.1 | `InvalidInput: alternatives.performed` |
| 3.7b | `type` `B/performed/permission`: string | as 3.1 | as 3.7a |
| 3.7c | `type` `B/performed/obligation`: string | as 3.1 | as 3.7a |
| 3.8a | `type` `B/inaction`: string | as 3.1 | `InvalidInput: alternatives.inaction` |
| 3.8b | `type` `B/taken`: string | as 3.1 | `InvalidInput: alternatives.taken` |
| 3.8c | `type` `B/proximate`: string | as 3.1 | `InvalidInput: alternatives.proximate` |
| 3.9a | `type` `B/fulfilments`: array | as 3.1 | `InvalidInput: alternatives.fulfilments` |
| 3.9b | `max_items` `B/fulfilments`: `MAX_ALT_FULFILMENTS` | `ALT_RESOURCE_LIMIT` | `ResourceLimit: fulfilments` |
| | group `fulfilments` over `B/fulfilments/*` | | |
| · 3.9c | `exact_keys` `@`: `obligation`, `body` | `ALT_INVALID_BLOCK` | as 3.9a |
| · 3.9d | `type` `@/obligation`: string | as 3.1 | as 3.9a |
| · 3.9e | `unique_so_far` `@/obligation` | `ALT_DUPLICATE_DECLARATION` | `DuplicateDeclaration: fulfilment {value}` |
| · 3.9f | `type` `@/body`: string or array | `ALT_INVALID_BLOCK` | as 3.9a |
| · 3.9g | `enum` `@/body`: `"avoids"`, when `@/body` is a string | as 3.1 | as 3.9a |
| · 3.9h | hook `fulfilment_body_decodes` at `@/body`, when `@/body` is an array | as 3.1 | as 3.9a |

Phase 4, `norms` (`Wire.lean:204–208`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 4.1 | `type` `/norms`: array | `ALT_INVALID_NORMS` | `InvalidInput: norms must be an array` |
| 4.2 | `max_items` `/norms`: `MAX_RULES` | `ALT_RESOURCE_LIMIT` | `ResourceLimit: rules` |
| | group `units` over `/norms/*` | | |
| · 4.3 | hook `w1_norm`, inherited | `ALT_INVALID_NORM` | `{message}` |

Phase 5, `base-units` (`decodePremises`, `Wire.lean:169–178, 209`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 5.1 | `type` `/units`: null or array | `ALT_INVALID_PREMISES` | `InvalidInput: premises must be an array` |
| | group `premises` over `/units/*` | | |
| · 5.2 | hook `premise_unit`, inherited | `ALT_INVALID_PREMISE` | `{message}` |

Phase 6, `declarations` (`checkBlock`, `Decl.lean:198–216`; `checkVerbalisations`, `Wire.lean:132–152`;
`checkAvoids`, `:155–159`; the base units typed, `:214–215`). The two classifier sets list their members
with a dotted index; the order inside each set is the route's and test-enforced.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 6.1 | classifier `block_declarations` at `B`, emits: | | |
| · 6.1.1 | the chooser sort is a sort of `E`; returns `sort` | `ALT_UNKNOWN_SYMBOL` | `UnknownSymbol: alternatives.chooser {sort}` |
| · 6.1.2 | the action sort, the same | as 6.1.1 | `UnknownSymbol: alternatives.action {sort}` |
| · 6.1.3 | the harm sort, the same | as 6.1.1 | `UnknownSymbol: alternatives.harm {sort}` |
| · 6.1.4 | the three sorts are distinct | `ALT_SORT` | `AlternativesSort: sorts must be distinct` |
| · 6.1.5 | no sort, predicate or constant of `E` is a profile word; returns `word` | `ALT_RESERVED` | `AlternativesReserved: {word}` |
| · 6.1.6 | `available` names a predicate of `E`; returns `predicate` | `ALT_UNKNOWN_SYMBOL` | `UnknownSymbol: alternatives.available {predicate}` |
| · 6.1.7 | that predicate is not regulated or defined; returns `predicate` | `ALT_REGULATED` | `AlternativesRegulated: available {predicate}` |
| · 6.1.8 | its argument sorts are `(action, chooser)`; returns `sorts` | `ALT_SORT` | `AlternativesSort: available expects {sorts}` |
| · 6.1.9–11 | the same three for `leads_to`, expecting `(action, harm)` | as 6.1.6–8 | `… alternatives.leads_to {predicate}`, `AlternativesRegulated: leads_to {predicate}`, `AlternativesSort: leads_to expects {sorts}` |
| · 6.1.12–14 | the same three for `inaction`, when declared, expecting `(action)` | as 6.1.6–8 | with `inaction` |
| · 6.1.15–17 | the same three for `taken`, when declared, expecting `(action)` | as 6.1.6–8 | with `taken` |
| · 6.1.18–20 | the same three for `proximate`, when declared, expecting `(action, harm)` | as 6.1.6–8 | with `proximate` |
| · 6.1.21 | `performed`, when declared, names a permission and its obligation dual, both on `(action)`; returns `pair` | `ALT_PERFORMED` | `AlternativesPerformed: {pair}` |
| 6.2 | classifier `role_verbalisations` at `P`, emits: | | |
| · 6.2.1–5 | the declared role predicate of `available`, `leads_to`, `inaction`, `taken`, `proximate` has the canonical verbalisation | `ALT_VERBALISATION` | `AlternativesVerbalisation: available must read "{{0}} is available to {{1}}"`, `… leads_to must read "{{0}} leads to {{1}}"`, `… inaction must read "{{0}} is inaction"`, `… taken must read "{{0}} is taken"`, `… proximate must read "{{0}} causes {{1}}"` |
| · 6.2.6–10 | no other predicate has that verbalisation, role by role | as 6.2.1 | `AlternativesVerbalisation: available must be declared for "{{0}} is available to {{1}}"`, and so for the other four roles |
| | group `avoids` over `B/fulfilments/*`, when `@/body` is `"avoids"` | | |
| · 6.3 | hook `avoids_obligation`; argument `obligation`: `@/obligation` | `ALT_FULFILMENT_SORT` | `FulfilmentSort: {obligation}` |
| | group `premises-typed` over `/units/*` | | |
| · 6.4 | hook `premise_typed`; argument `label`: `@/label` | `ALT_ILL_TYPED_PREMISE` | `InvalidInput: ill-typed premise {label}` |

Phase 7, `typing` (`checkProfileTyping`, `Decl.lean:222–230`). One group `rules` over `/norms/*`.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · 7.1 | classifier `rule_typing` at `@`; argument `name`: `@/norm/name`; emits: | | |
| · · 7.1a | the guard, then each carve-out, is well typed over `E` extended by the four profile words; inherited | `ALT_TYPING` | `{message}` |
| · · 7.1b | each of the guard and the carve-outs, after inlining, has at most `MAX_NODES` nodes | `ALT_RESOURCE_LIMIT` | `ResourceLimit: alternatives inlining of rule {name}` |

Phase 8, `rules` (W1's `check` on the inlined tree, `Tree.lean:331–346`). One group `rules` over `/norms/*`.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · 8.1 | `name` `@/norm/name`: `rule_name` | `ALT_INVALID_NAME` | `InvalidInput: invalid rule name '{value}'` |
| · 8.2 | `unique_so_far` `@/norm/name` | `ALT_DUPLICATE_DECLARATION` | `DuplicateDeclaration: rule {value}` |
| · 8.3 | hook `regulated_predicate` at `@/norm/predicate` | `ALT_UNKNOWN_SYMBOL` | `UnknownSymbol: regulated predicate {value}` |
| · 8.4 | `max_items` `@/norm/unless`: `MAX_CARVE_OUTS` | `ALT_INVALID_RULE_FIELDS` | `InvalidInput: invalid sign or too many carve-outs` |
| · 8.5 | hook `inlined_nodes_fit` at `@` | `ALT_RESOURCE_LIMIT` | `ResourceLimit: AST exceeds 10,000 nodes` |

Phase 9, `references` (`Tree.lean:347–353`). One group `rule-refs` over `/norms/*`, and inside it one group
`over-refs` over `@/norm/over/*`.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · · 9.1 | `declared_in` `@`: `/norms/*/norm/name` | `ALT_UNKNOWN_RULE` | `UnknownRule: rule {value}` |
| · · 9.2 | hook `over_same_predicate`, returns `rule`, `predicate`, `parent_predicate` | `ALT_PRECEDENCE_ACROSS_PREDICATES` | `PrecedenceAcrossPredicates: rule {rule} on {predicate}, rule {value} on {parent_predicate}` |

Phase 10, `semantic` (`Tree.lean:354–362`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 10.1 | hook `precedence_acyclic` at `/norms`, returns `detail` | `ALT_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |
| 10.2 | hook `precedence_depth_fits` at `/norms` | `ALT_RESOURCE_LIMIT` | `ResourceLimit: precedence depth` |
| 10.3 | hook `layers_acyclic` at `/norms`, returns `detail` | `ALT_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |

Phase 11, `fulfilments` (`checkFulfilments`, `Decl.lean:233–247`). One group `fulfilments-semantic` over
`B/fulfilments/*`; every row has the argument `obligation`: `@/obligation`.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · 11.1 | hook `fulfilment_not_performed` | `ALT_FULFILMENT_ON_PERFORMED` | `FulfilmentOnPerformed: {obligation}` |
| · 11.2 | hook `fulfilment_obligation` | `ALT_FULFILMENT_SORT` | `FulfilmentSort: {obligation}` |
| · 11.3 | hook `fulfilment_body_base` | `ALT_FULFILMENT_NOT_BASE` | `FulfilmentNotBase: {obligation}` |

**What is not in the table, and why.** The four fallback texts above (no reaching input). The limits that
the route checks twice (`ResourceLimit: fulfilments` and `ResourceLimit: rules` in `checkFulfilments` and
`check`, the duplicate fulfilment in `checkFulfilments`, the regulated-predicate count and the act checks in
`check`): each is caught by its earlier row (3.9b, 4.2, 3.9e, 2.1), so the later step cannot be first. The
typing of the inlined formulas over `E` in `check` and the typing of `Γ` in `checkAlt`: `inline_base`
(lean/ALTERNATIVES.md) says an inlined formula is typed over `E` when the original is typed over the extended
environment, which 7.1a and 6.4 have established.

**Planned tiers.** 69 numbered checks (a classifier set counts once). T1: 1.1 to 1.8, 3.1 to 3.9g except
3.5f and 3.9h (33), 4.1, 4.2, 5.1, 8.1, 8.2, 8.4, 9.1 (48). T2 not inherited: 2.2, 2.3, 3.5f, 3.9h, 6.3, 6.4,
8.3, 8.5, 9.2, 10.1 to 10.3, 11.1 to 11.3 (15). Inherited hooks: 2.1, 4.3, 5.2 (3). T3: 6.1, 6.2, 7.1 (3).
`n1 + n2` is 63 of 69. For a new unit the gate reports the counts and requires none (S5 spec, R9). The Python
engine evaluates phase 1 and defers at 2.1 on every root that passes it (2.5), so its fast path is phase 1.

### 2.4 The contract `risk@0`, revision 1

**Limits and classes used.** `limits.json` gains `MAX_UNIT_TAGS` 64 (`lean/VE/Risk/Wire.lean:98`),
`MAX_RISK_LOG_ENTRIES` 4096 (`:389`), `MAX_RISK_ALTERNATIVES` 16 and `MAX_RISK_HARMS` 32
(`lean/VE/Risk/Record.lean:486–489`); `MAX_RULES`, `MAX_CARVE_OUTS` and `MAX_ALT_FULFILMENTS` exist. `names.json`
gains `risk_field` (`enum`: `always_possible`, `alternative_kinds`, `combination`, `harm_classes`,
`quantity_kinds`, `required_alternatives`, `required_estimators`, `severity`, `unexamined`,
`use_all_recorded`; `Wire.lean:153–155`), `risk_identifier` (`first` `a-z`; `rest` `a-z0-9_`; `max_bytes` 64;
`forbid_infix` `__`; `lean/VE/Surface.lean:71–74`, `lean/VE/Bridge.lean:29–30`, `Wire.lean:186–187`),
`risk_decider` (`min_bytes` 1; `max_bytes` 64; `Wire.lean:207, 216, 233`) and `risk_entry_kind` (`enum`:
`condition`, `decision`, `estimate`, `instruction`, `outcome`, `setting`, `statement`, `supersession`,
`taken`; `Record.lean:155–165`); `alternatives_field` and `rule_name` exist.

**Codes.** As 2.3, with the prefix `RISK_`: `RISK_UNSUPPORTED_PROFILE` (`UnsupportedProfile`);
`RISK_RESOURCE_LIMIT` (`ResourceLimit`); `RISK_UNKNOWN_SYMBOL` (`UnknownSymbol`); `RISK_DUPLICATE_DECLARATION`
(`DuplicateDeclaration`); `RISK_INVALID_MODEL` (`InvalidModel`); and these of class `InvalidInput`:
`RISK_INVALID_ENVIRONMENT`, `RISK_INVALID_UNIT`, `RISK_INVALID_NORM`, `RISK_INVALID_PREMISE` and `RISK_TYPING`
(inherited, exempt); `RISK_INVALID_UNITS`, `RISK_INVALID_ALTERNATIVES_BLOCK`, `RISK_MISSING_OUTCOME_DECIDER`,
`RISK_INVALID_BLOCK`, `RISK_STAGE_FIELD`, `RISK_INVALID_NORMS`, `RISK_INVALID_PREMISES`, `RISK_ILL_TYPED_PREMISE`,
`RISK_ALT_SORT`, `RISK_ALT_RESERVED`, `RISK_ALT_REGULATED`, `RISK_ALT_VERBALISATION`, `RISK_ALT_PERFORMED`,
`RISK_FULFILMENT_SORT`, `RISK_FULFILMENT_NOT_BASE`, `RISK_FULFILMENT_ON_PERFORMED`, `RISK_SEVERITY_NOT_FRESH`,
`RISK_RESERVED`, `RISK_UNRANKED_AGAINST_ORDER`, `RISK_HARM_UNCLASSIFIED`, `RISK_HARM_TWO_CLASSES`,
`RISK_OUTCOMES`, `RISK_DEPENDENCY_CYCLE`, `RISK_INVALID_NAME`, `RISK_INVALID_RULE_FIELDS`, `RISK_UNKNOWN_RULE`,
`RISK_PRECEDENCE_ACROSS_PREDICATES`, `RISK_INVALID_DECISION`, `RISK_ESTIMATE_PROVENANCE`, `RISK_ALTERED_ENTRY`,
`RISK_BINDING`, `RISK_HINDSIGHT_ENTRY`, `RISK_MISSING_ENTRY`, `RISK_WITHDRAWN_ENTRY`, `RISK_UNKNOWN_HARM`,
`RISK_CONSTANT`, `RISK_FACT`, `RISK_REQUIRED_ALTERNATIVE_MISSING`, `RISK_UNIT_MISMATCH`, `RISK_UNIT_PRECISION`,
`RISK_INVALID_DECIMAL`, `RISK_RANGE`, `RISK_ESTIMATOR_NOT_ALLOWED`, `RISK_SETTING_TWICE`, `RISK_SETTING_SCOPE`,
`RISK_CONFLICTING_ESTIMATES`, `RISK_INCONSISTENT`, `RISK_UNESTIMATED`, `RISK_TWO_SOURCES`,
`RISK_STATEMENT_FORM`, `RISK_CONDITION_SHARED`, `RISK_EQUALITY_COEFFICIENT`, `RISK_SUFFICIENT_OUTSIDE_NECESSARY`,
`RISK_INVALID_INPUT` (the `residual` code).

**The table.** `E`, `B` and `P` as in 2.3; `K` abbreviates `/environment/risk`, `D` abbreviates `/document`
and `C` abbreviates `/decision/content`. The order is `decodeRiskSource`'s (`Wire.lean:298–344`) and then
`runDecision`'s (`Run.lean:362–371`). Phases 14 and 15 carry the guard "`/decision` is absent or is not
`null`" (`{"is_not": ["/decision", "null"]}`) on every entry, so a root without a decision never reaches them
(5.3). Six texts of the route are not in the table because no input reaches them after the checks above (12,
R3): the four of 2.3 and `InvalidInput: risk block is not well-formed`, `InvalidInput: risk decision model`,
`InvalidInput: a risk premise fails on the decision model`, `InvalidInput: risk decision record is not valid`.

Phase 1, `gate` (`Wire.lean:86–89, 24–31, 299–306`; the Python engine runs this phase):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 1.1a | `requires` `E` member `units`, when `E/unit_schema` is present | `RISK_UNSUPPORTED_PROFILE` | `UnsupportedProfile: unit_schema and units require the ve.core@0.2 quantity route together` |
| 1.1b | `requires` `E` member `unit_schema`, when `E/units` is present | as 1.1a | as 1.1a |
| 1.2a | `type` `E`: object | as 1.1a | `UnsupportedProfile: profiles must be a sorted unique array` |
| 1.2b | `requires` `E` member `profiles` | as 1.1a | as 1.2a |
| 1.2c | `type` `E/profiles`: array of strings | as 1.1a | as 1.2a |
| 1.3 | `sorted_unique` `E/profiles` | as 1.1a | `UnsupportedProfile: profiles must be sorted and unique` |
| 1.4 | `requires` `E/profiles` item `"risk@0"` | as 1.1a | `UnsupportedProfile: risk@0 is required` |
| 1.5 | `requires` `E/profiles` item `"alternatives@0"` | as 1.1a | `UnsupportedProfile: risk@0 requires alternatives@0` |
| 1.6 | `requires` `E/profiles` item `"norms@0"` | as 1.1a | `UnsupportedProfile: alternatives@0 requires norms@0` |
| 1.7 | `excludes` `E/profiles` item `"soft-norms@0"` | as 1.1a | `UnsupportedProfile: alternatives@0 with soft-norms@0` |
| 1.8 | `requires` `E` member `alternatives` | `RISK_INVALID_ALTERNATIVES_BLOCK` | `InvalidInput: alternatives.block` |
| 1.9 | `requires` `E` member `risk` | `RISK_INVALID_BLOCK` | `InvalidInput: risk.block` |

Phase 2, `environment` (`Wire.lean:307–318, 91–101, 117–136, 140–149`; `lean/VE/Route/Gate.lean:150–159`;
`lean/VE/Time/Wire.lean:137–176, 193–205, 230–244, 102–111`). "When extended" is the guard "`E/unit_schema`
is present".

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 2.1 | hook `route_envelope` at `E`, inherited | `RISK_INVALID_ENVIRONMENT` | `{message}` |
| 2.2 | `excludes` `E/profiles` item `"closure@0"` | `RISK_UNSUPPORTED_PROFILE` | `UnsupportedProfile: the risk norms route admits FOL documents only` |
| 2.3 | `excludes` `E/profiles` item `"order@0"` | as 2.2 | as 2.2 |
| 2.4 | `max_items` `E/profiles`: 4, when extended | as 2.2 | `UnsupportedProfile: ve-units@1 requires exactly order@0, relational-fol@0 and time@0, optionally with documents@1` |
| 2.5 | `const` `E/unit_schema`: `"ve-units@1"` | as 2.2 | `UnsupportedProfile: Unsupported unit schema` |
| 2.6 | `type` `E/units`: object | `RISK_INVALID_UNITS` | `units must be an object` |
| 2.7 | `max_items` `E/units`: `MAX_UNIT_TAGS` | `RISK_RESOURCE_LIMIT` | `ResourceLimit: At most 64 unit tags` |
| | group `unit-records` over `E/units/*` | | |
| · 2.8 | hook `w6_unit`, inherited | `RISK_INVALID_UNIT` | `{message}` |
| 2.9 | hook `w6_display_injective` at `E/units`, inherited, when extended | as 2.8 | `{message}` |
| | group `slot-units` over `P/*`, when extended | | |
| · 2.10 | hook `w6_argument_units`, inherited | as 2.8 | `{message}` |
| | group `constant-annotations` over `/environment/vocabulary/constants/*` | | |
| · 2.11 | hook `w6_constant_verbalisation`, inherited | as 2.8 | `{message}` |
| · 2.12 | hook `w6_constant_unit`, inherited, when extended | as 2.8 | `{message}` |
| 2.13 | hook `w1_environment` at `E`, inherited | `RISK_INVALID_ENVIRONMENT` | `{message}` |
| 2.14 | hook `w6_extension` at `/environment/vocabulary`, inherited, when extended | `RISK_INVALID_UNIT` | `{message}` |
| 2.15 | hook `no_definitions` at `P` | `RISK_UNSUPPORTED_PROFILE` | `UnsupportedProfile: risk route with definitions is not implemented` |
| 2.16 | hook `no_data_flags` at `P` | as 2.15 | `UnsupportedProfile: risk route with data flags is not implemented` |
| 2.17 | hook `no_string_literals` at `/environment/vocabulary/constants` | as 2.15 | `UnsupportedProfile: risk route with $string literals is not implemented` |

2.4 is exact after 1.3 to 1.6 and 2.1: the route requires `profiles` to equal `[alternatives@0, norms@0,
relational-fol@0, risk@0]` when extended, and a sorted unique list that contains those four (2.1's gate
requires `relational-fol@0`) equals them exactly when it has four members. 2.2 and 2.3 are exact after 2.1:
`classify` refuses `nary@0` without `closure@0`, so the family is not FOL exactly when `closure@0` or
`order@0` is listed. 2.5 to 2.7 need no guard: without the extension `unit_schema` and `units` are absent
(1.1b) and every one of them holds on an absent target.

Phase 3, `alternatives-block`: the rows 3.1 to 3.9h of 2.3, with the codes `RISK_INVALID_ALTERNATIVES_BLOCK`,
`RISK_MISSING_OUTCOME_DECIDER`, `RISK_RESOURCE_LIMIT` and `RISK_DUPLICATE_DECLARATION` in place of the `ALT_`
ones, and one difference: 3.9g is `enum` `@/body`: `"avoids"`, `"excludes"`, because the route expands an
`excludes` body before it decodes the block (`expandExcludes`, `Wire.lean:268–277, 319–320`).

Phase 4, `risk-block` (`decodeRiskBlock`, `Wire.lean:189–258`). Every text of this phase is
`InvalidInput: risk.<field>` with the code `RISK_INVALID_BLOCK`, except 4.2a.

| Id | Kind, target, guard | Text |
|---|---|---|
| 4.1 | `type` `K`: object | `InvalidInput: risk.block` |
| | group `fields` over `K/*` | |
| · 4.2a | hook `not_stage_field` (code `RISK_STAGE_FIELD`) | `InvalidInput: risk.{key} (stage B or C not enabled)` |
| · 4.2b | `name` on key: `risk_field` | `InvalidInput: risk.{key}` |
| 4.3a | `requires` `K` member `severity` | `InvalidInput: risk.severity` |
| 4.3b | `requires` `K` member `harm_classes` | `InvalidInput: risk.harm_classes` |
| 4.3c | `requires` `K` member `unexamined` | `InvalidInput: risk.unexamined` |
| 4.4a | `exact_keys` `K/severity`: `sort`, `classes`, `more_severe`, `unranked`, `decided_by` | `InvalidInput: risk.severity` |
| 4.4b | `type` `K/severity/sort`: string | as 4.4a |
| 4.4c | `type` `K/severity/classes`: array of strings | as 4.4a |
| 4.4d | `name` `K/severity/sort`: `risk_identifier` | as 4.4a |
| | group `classes` over `K/severity/classes/*` | |
| · 4.4e | `name` `@`: `risk_identifier` | as 4.4a |
| 4.4f | `type` `K/severity/more_severe`: array | as 4.4a |
| | group `edges` over `K/severity/more_severe/*` | |
| · 4.4g | `type` `@`: tuple of two strings | as 4.4a |
| 4.4h | `type` `K/severity/unranked`: array | as 4.4a |
| | group `unranked` over `K/severity/unranked/*` | |
| · 4.4i | `type` `@`: tuple of two strings | as 4.4a |
| 4.4j | `name` `K/severity/decided_by`: `risk_decider` | as 4.4a |
| 4.5a | `type` `K/harm_classes`: array | `InvalidInput: risk.harm_classes` |
| | group `harm-classes` over `K/harm_classes/*` | |
| · 4.5b | `type` `@`: tuple of two strings | as 4.5a |
| 4.6a | `type` `K/unexamined`: string or object | `InvalidInput: risk.unexamined` |
| 4.6b | `const` `K/unexamined`: `"possible"`, when `K/unexamined` is a string | as 4.6a |
| 4.6c | `exact_keys` `K/unexamined`: `ruled_out_by`, when `K/unexamined` is an object | as 4.6a |
| 4.6d | `name` `K/unexamined/ruled_out_by`: `risk_decider` | as 4.6a |
| 4.7 | `type` `K/always_possible`: array of strings | `InvalidInput: risk.always_possible` |
| 4.8 | `enum` `K/combination`: `"latest"`, `"hull"`, `"intersection"` | `InvalidInput: risk.combination` |
| 4.9a | `type` `K/alternative_kinds`: object | `InvalidInput: risk.alternative_kinds` |
| | group `kinds` over `K/alternative_kinds/*` | |
| · 4.9b | `type` `@`: string | as 4.9a |
| | group `kinds-named` over `K/alternative_kinds/*` | |
| · 4.9c | `name` on key: `risk_identifier` | as 4.9a |
| · 4.9d | `name` `@`: `risk_decider` | as 4.9a |
| 4.10a | `type` `K/required_alternatives`: array | `InvalidInput: risk.required_alternatives` |
| | group `requirements` over `K/required_alternatives/*` | |
| · 4.10b | `exact_keys` `@`: `when`, `require` | as 4.10a |
| · 4.10c | `type` `@/when`: string | as 4.10a |
| · 4.10d | `type` `@/require`: array of strings | as 4.10a |
| 4.11a | `type` `K/quantity_kinds`: object | `InvalidInput: risk.quantity_kinds` |
| | group `quantity-kinds` over `K/quantity_kinds/*` | |
| · 4.11b | `type` `@`: string | as 4.11a |
| | group `quantity-kinds-named` over `K/quantity_kinds/*` | |
| · 4.11c | `name` on key: `risk_identifier` | as 4.11a |
| 4.12a | `type` `K/required_estimators`: array | `InvalidInput: risk.required_estimators` |
| | group `estimators` over `K/required_estimators/*` | |
| · 4.12b | `exact_keys` `@`: `quantity_kind`, `estimators` | as 4.12a |
| · 4.12c | `type` `@/quantity_kind`: string | as 4.12a |
| · 4.12d | `type` `@/estimators`: array of strings | as 4.12a |
| 4.13 | `type` `K/use_all_recorded`: boolean | `InvalidInput: risk.use_all_recorded` |

4.4j and 4.6d are exact: the route refuses a value that is not a string, an empty string and one over 64
bytes with one text, and `name` with `risk_decider` fails on exactly those (base spec 2.4); `"chooser"` is
in the class. 4.9b before 4.9c and 4.9d, and 4.11b before 4.11c, are two groups over one pattern because the
route reads every value first and loops again over the names (`Wire.lean:228–233, 241–245`).

Phase 5, `norms` (`Wire.lean:322–328`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 5.1a | `type` `D`: object | `RISK_INVALID_NORMS` | `InvalidInput: norms must be an array` |
| 5.1b | `requires` `D` member `norms` | as 5.1a | as 5.1a |
| 5.1c | `type` `D/norms`: array | as 5.1a | as 5.1a |
| 5.2 | `max_items` `D/norms`: `MAX_RULES` | `RISK_RESOURCE_LIMIT` | `ResourceLimit: rules` |
| | group `units` over `D/norms/*` | | |
| · 5.3 | hook `w1_norm`, inherited | `RISK_INVALID_NORM` | `{message}` |

Phase 6, `declarations` (`Wire.lean:332–340`): 6.1 and 6.2 of 2.3 with the `RISK_` codes, run on `toAlt R`,
whose environment is `E_risk` (`E` plus the severity sort, the class constants and the three generated
predicates, `Decl.lean:90–97`); then:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| | group `avoids` over `B/fulfilments/*`, when `@/body` is `"avoids"` | | |
| · 6.3 | hook `avoids_obligation`; argument `obligation`: `@/obligation` | `RISK_FULFILMENT_SORT` | `FulfilmentSort: {obligation}` |
| | group `excludes` over `B/fulfilments/*`, when `@/body` is `"excludes"` | | |
| · 6.4 | hook `excludes_obligation`; argument `obligation`: `@/obligation` | as 6.3 | as 6.3 |
| 6.5 | `type` `D/units`: null or array | `RISK_INVALID_PREMISES` | `InvalidInput: premises must be an array` |
| | group `premises` over `D/units/*` | | |
| · 6.6 | hook `premise_unit`, inherited | `RISK_INVALID_PREMISE` | `{message}` |
| | group `premises-typed` over `D/units/*` | | |
| · 6.7 | hook `premise_typed`; argument `label`: `@/label` | `RISK_ILL_TYPED_PREMISE` | `InvalidInput: ill-typed premise {label}` |

On this route the base units are decoded after the block's declarations (`Wire.lean:339`), where the
alternatives route decodes them before (2.3, phase 5); that is why 6.5 and 6.6 sit here.

Phase 7, `risk-declarations` (`checkRiskBlock`, `Decl.lean:210–255`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 7.1 | classifier `risk_block_declarations` at `K`, emits: | | |
| · 7.1.1 | the severity sort is not a sort of `E`; returns `sort` | `RISK_SEVERITY_NOT_FRESH` | `RiskSeverityNotFresh: {sort}` |
| · 7.1.2 | no symbol of `E` begins with `risk__` or equals a class; no generated predicate, risk word or class is a symbol of `E`; returns `name` | `RISK_RESERVED` | `RiskReserved: {name}` |
| · 7.1.3 | there are 1 to 16 classes | `RISK_RESOURCE_LIMIT` | `ResourceLimit: risk classes` |
| · 7.1.4 | the classes are distinct; returns `name` | `RISK_DUPLICATE_DECLARATION` | `DuplicateDeclaration: risk class {name}` |
| · 7.1.5 | every edge and unranked pair names classes; returns `name` | `RISK_UNKNOWN_SYMBOL` | `UnknownSymbol: risk.severity {name}` |
| · 7.1.6 | the edges are acyclic; returns `detail` | `RISK_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |
| · 7.1.7 | every unranked pair is incomparable in the closure; returns `pair` | `RISK_UNRANKED_AGAINST_ORDER` | `RiskUnrankedAgainstOrder: {pair}` |
| · 7.1.8 | each `harm_classes` row names a harm constant and a class; returns `name` | `RISK_UNKNOWN_SYMBOL` | `UnknownSymbol: risk.harm_classes {name}` |
| · 7.1.9 | no harm constant is classified twice; returns `harm` | `RISK_HARM_TWO_CLASSES` | `HarmTwoClasses: {harm}` |
| · 7.1.10 | every harm constant is classified; returns `harm` | `RISK_HARM_UNCLASSIFIED` | `HarmUnclassified: {harm}` |
| · 7.1.11 | `always_possible` names classes; returns `name` | `RISK_UNKNOWN_SYMBOL` | `UnknownSymbol: risk.always_possible {name}` |
| · 7.1.12 | `required_alternatives` names kinds, `when` first; returns `name` | as 7.1.11 | `UnknownSymbol: risk.required_alternatives {name}` |
| · 7.1.13 | `quantity_kinds` names `dimensionless` or a declared tag; returns `name` | as 7.1.11 | `UnknownSymbol: risk.quantity_kinds {name}` |
| · 7.1.14 | `required_estimators` names quantity kinds; returns `name` | as 7.1.11 | `UnknownSymbol: risk.required_estimators {name}` |
| · 7.1.15 | `outcomes` is `signed` | `RISK_OUTCOMES` | `RiskOutcomes: risk@0 requires outcomes signed` |

Phase 8, `risk-typing` (`checkRiskTyping`, `Decl.lean:261–268`). One group `rules` over `D/norms/*`.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · 8.1 | classifier `rule_typing_risk` at `@`; argument `name`: `@/norm/name`; emits: | | |
| · · 8.1a | the guard, then each carve-out, is well typed over `E_risk` extended by the four profile words and the two risk words; inherited | `RISK_TYPING` | `{message}` |
| · · 8.1b | each, after the risk words are inlined, has at most `MAX_NODES` nodes | `RISK_RESOURCE_LIMIT` | `ResourceLimit: risk inlining of rule {name}` |

Inside this set the route checks each formula's typing and then its inlining before the next formula
(`Decl.lean:264–268`), where the alternatives route types every formula of a rule before it inlines any
(`Decl.lean:224–230`). The catalogue records the order keys (2.5).

Phase 9, `alternatives-typing` (`checkProfileTyping` on `toAlt R`, `Decl.lean:222–230`). One group `rules`
over `D/norms/*`.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · 9.1 | hook `alt_inlining_fits` at `@`; argument `name`: `@/norm/name` | `RISK_RESOURCE_LIMIT` | `ResourceLimit: alternatives inlining of rule {name}` |

The typing member of this step has no row: a formula typed over the environment of 8.1a is, after the risk
words are inlined, typed over `E_risk` with the profile words (`risk_inline_faithful`, lean/RISK.md), so
`typeDiagnostic` cannot fail here; a failure would be a residual, counted.

Phases 10 to 13, `rules`, `references`, `semantic`, `fulfilments`: the rows 8.1 to 11.3 of 2.3, renumbered
10.1 to 13.3, over `D/norms/*` and `B/fulfilments/*`, with the `RISK_` codes, on the inlined tree of `toAlt R`.

Phase 14, `admission` (`decodeEntry`, `decodeSupplied`, `Wire.lean:360–397`; `admitDecision`,
`Record.lean:492–505`; `decodeRecord`, `:243–274`; `buildDecision`, `:452–462`). Every entry carries the
decision guard. Every text of 14.1 to 14.23 has the code `RISK_INVALID_DECISION`.

| Id | Kind, target, guard | Text |
|---|---|---|
| 14.1 | `exact_keys` `/decision`: `seq`, `day`, `id`, `kind`, `content`, `prev`, `hash` | `InvalidInput: risk-decision` |
| 14.2 | `type` `/decision/seq`: integer | `InvalidInput: risk-decision.seq` |
| 14.3 | hook `w6_day` at `/decision/day` | `InvalidInput: risk-decision.day` |
| 14.4 | `type` `/decision/id`: string | `InvalidInput: risk-decision.id` |
| 14.5 | `name` `/decision/kind`: `risk_entry_kind` | `InvalidInput: risk-decision.kind` |
| 14.6 | `type` `/decision/prev`: string | `InvalidInput: risk-decision.prev` |
| 14.7 | `type` `/decision/hash`: string | `InvalidInput: risk-decision.hash` |
| 14.8 | `type` `/entries`: array | `InvalidInput: risk-decision.entries` |
| 14.9 | `max_items` `/entries`: `MAX_RISK_LOG_ENTRIES` (code `RISK_RESOURCE_LIMIT`) | `ResourceLimit: risk log entries` |
| | group `supplied` over `/entries/*` | |
| · 14.10 | hook `estimate_recorded`, when `@/kind` is `"estimate"`, returns `id` (code `RISK_ESTIMATE_PROVENANCE`) | `EstimateProvenance: {id} recorded` |
| · 14.11a–g | the seven checks of 14.1 to 14.7 on `@` | the seven texts of 14.1 to 14.7 |
| 14.12 | `const` `/decision/kind`: `"decision"` | `InvalidInput: risk-decision.kind` |
| 14.13 | hook `decision_entry_hash` at `/decision`; argument `id`: `/decision/id` (code `RISK_ALTERED_ENTRY`) | `AlteredEntry: {id}` |
| 14.14 | `exact_keys` `C`: `format`, `id`, `chooser`, `chooser_label`, `policy`, `alternatives`, `quantities`, `cites`, `facts` | `InvalidInput: risk-decision.record` |
| 14.15 | `const` `C/format`: `"ve-risk-decision@0"` | `InvalidInput: risk-decision.format` |
| 14.16 | `type` `C/id`: string | `InvalidInput: risk-decision.id` |
| 14.17 | `type` `C/chooser`: string | `InvalidInput: risk-decision.chooser` |
| 14.18 | `type` `C/chooser_label`: string | `InvalidInput: risk-decision.chooser_label` |
| 14.19a | `exact_keys` `C/policy`: `environment_id`, `document_hash` | `InvalidInput: risk-decision.policy` |
| 14.19b | `type` `C/policy/environment_id`: string | as 14.19a |
| 14.19c | `type` `C/policy/document_hash`: string | as 14.19a |
| 14.20a | `type` `C/alternatives`: array | `InvalidInput: risk-decision.alternatives` |
| | group `alternatives` over `C/alternatives/*` | |
| · 14.20b | `keys` `@`: required `name`, `label`; optional `kind`, `inaction` | as 14.20a |
| · 14.20c | `type` `@/inaction`: Boolean | as 14.20a |
| · 14.20d | `type` `@/name`: string | as 14.20a |
| · 14.20e | `type` `@/label`: string | as 14.20a |
| · 14.20f | `type` `@/kind`: string | as 14.20a |
| 14.21a | `type` `C/quantities`: array | `InvalidInput: risk-decision.quantities` |
| | group `quantities` over `C/quantities/*` | |
| · 14.21b | `keys` `@`: required `name`, `label`, `tag`; optional `kind` | as 14.21a |
| · 14.21c | `type` `@/name`: string | as 14.21a |
| · 14.21d | `type` `@/label`: string | as 14.21a |
| · 14.21e | `type` `@/tag`: string | as 14.21a |
| · 14.21f | `type` `@/kind`: string | as 14.21a |
| 14.22a | `type` `C/cites`: array | `InvalidInput: risk-decision.cites` |
| | group `cites` over `C/cites/*` | |
| · 14.22b | `exact_keys` `@`: `id`, `seq`, `hash` | as 14.22a |
| · 14.22c | `type` `@/id`: string | as 14.22a |
| · 14.22d | `type` `@/seq`: integer | as 14.22a |
| · 14.22e | `type` `@/hash`: string | as 14.22a |
| 14.23a | `type` `C/facts`: array | `InvalidInput: risk-decision.facts` |
| | group `facts` over `C/facts/*` | |
| · 14.23b | `exact_keys` `@`: `predicate`, `args`, `entry` | as 14.23a |
| · 14.23c | `type` `@/args`: array of strings | as 14.23a |
| · 14.23d | `type` `@/predicate`: string | as 14.23a |
| · 14.23e | `type` `@/entry`: string | as 14.23a |
| 14.24 | hook `policy_binding` at `C/policy` (code `RISK_BINDING`) | `RiskBinding: policy` |
| 14.25 | `max_items` `C/alternatives`: `MAX_RISK_ALTERNATIVES` (code `RISK_RESOURCE_LIMIT`) | `ResourceLimit: risk alternatives` |
| 14.26 | `max_items` `K/harm_classes`: `MAX_RISK_HARMS` (code `RISK_RESOURCE_LIMIT`) | `ResourceLimit: risk harms` |
| | group `citations` over `C/cites/*`; every row has the argument `id`: `@/id` | |
| · 14.27 | hook `cite_precedes_decision` (code `RISK_HINDSIGHT_ENTRY`) | `HindsightEntry: {id}` |
| · 14.28 | hook `cited_entry_exists` (code `RISK_MISSING_ENTRY`) | `MissingEntry: {id}` |
| · 14.29 | hook `cited_entry_unaltered` (code `RISK_ALTERED_ENTRY`) | `AlteredEntry: {id}` |
| · 14.30 | hook `cited_estimate_not_withdrawn` (code `RISK_WITHDRAWN_ENTRY`) | `WithdrawnEntry: {id}` |
| | group `fact-sources` over `C/facts/*` | |
| · 14.31 | hook `fact_cites_instruction_or_statement` | `InvalidInput: risk-decision.facts` |
| | group `cited-contents` over `C/cites/*` | |
| · 14.32 | classifier `cited_content` at `@`, emits: | |
| · · 14.32.1 | an estimate entry's content has the members of 3.3 | `InvalidInput: risk-decision.estimate` |
| · · 14.32.2 | its `estimator` has the member `name` and at most `version` | `InvalidInput: risk-decision.estimator` |
| · · 14.32.3 | a setting entry's content has the members of 3.3 | `InvalidInput: risk-decision.setting` |
| · · 14.32.4 | a condition entry's content has the members of 3.3 and a condition of 3.2 | `InvalidInput: risk-decision.condition` |
| · · 14.32.5 | a statement entry's content has the members of 3.3 | `InvalidInput: risk-decision.statement` |
| · · 14.32.6 | a condition has at most `MAX_NODES` nodes after normalisation (code `RISK_RESOURCE_LIMIT`) | `ResourceLimit: risk condition nodes` |
| 14.33 | hook `estimates_and_settings_fit` at `C/cites` (code `RISK_RESOURCE_LIMIT`) | `ResourceLimit: risk estimates and settings` |
| 14.34 | hook `conditions_and_statements_fit` at `C/cites` (code `RISK_RESOURCE_LIMIT`) | `ResourceLimit: risk conditions and statements` |

Problems that `decodeItem` records as issues (an unknown quantity, a value off its grid, a tag mismatch, a
statement form) are not faults of 14.32: the route reports them at the validation step that owns them, and so
does 15.1 (`Record.lean:376–441, 817–820`).

Phase 15, `validation` (`validateDecision` with `withCase`, `Record.lean:825–990`, `Run.lean:281–288, 368–371`;
`marginLimit`, `Report.lean:122–124`). The decision guard applies.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 15.1 | classifier `record_validation` at `/decision`, emits, in the order of V1 to V11: | | |
| · 15.1.1 | every quantity a cited content names is a quantity of the record (V1, V7); returns `name` | `RISK_UNKNOWN_SYMBOL` | `UnknownSymbol: quantity {name}` |
| · 15.1.2 | alternative names are distinct; returns `name` | `RISK_DUPLICATE_DECLARATION` | `DuplicateDeclaration: alternative {name}` |
| · 15.1.3 | quantity names are distinct; returns `name` | as 15.1.2 | `DuplicateDeclaration: quantity {name}` |
| · 15.1.4 | the alternatives model's conditions (V1: exactly one inaction; V11: alt's premises, rows, existence facts and `Γ`); returns `detail` | `RISK_INVALID_MODEL` | `InvalidModel(alternatives): {detail}` |
| · 15.1.5 | every harm named is a harm constant; returns `name` | `RISK_UNKNOWN_HARM` | `UnknownHarm: {name}` |
| · 15.1.6 | every alternative named is one of the record's; returns `name` | `RISK_UNKNOWN_SYMBOL` | `UnknownSymbol: alternative {name}` |
| · 15.1.7 | every kind named is declared; returns `name` | as 15.1.6 | `UnknownSymbol: kind {name}` |
| · 15.1.8 | every tag named is `dimensionless` or a declared tag (V1, V7); returns `name` | as 15.1.6 | `UnknownSymbol: unit {name}` |
| · 15.1.9 | a quantity's tag is its kind's; a condition's terms carry one tag (V1, V7); returns `tags` | `RISK_UNIT_MISMATCH` | `UnitMismatch({tags})` |
| · 15.1.10 | no record-local name is a constant of `E_risk` or another record-local name, except an alternative over an action constant; every action constant is an alternative (V1, V10); returns `name` | `RISK_CONSTANT` | `RiskConstant: {name}` |
| · 15.1.11 | facts name base predicates, with typed arguments (V1, V10); returns `predicate` | `RISK_FACT` | `RiskFact: {predicate}` |
| · 15.1.12 | required alternatives are present (V2); returns `detail` | `RISK_REQUIRED_ALTERNATIVE_MISSING` | `RequiredAlternativeMissing: {detail}` |
| · 15.1.13 | an estimate's, a setting's or a condition literal's value lies on its tag's grid (V3, V4, V7); returns `detail` | `RISK_UNIT_PRECISION` | `UnitPrecision({detail})` |
| · 15.1.14 | such a value is a decimal of W6's form (V3, V4, V7); returns `literal` | `RISK_INVALID_DECIMAL` | `Invalid decimal literal {literal}` |
| · 15.1.15 | such a value has at most 40 digits (V3, V4, V7) | `RISK_RESOURCE_LIMIT` | `ResourceLimit: Decimal literal exceeds 40 digits` |
| · 15.1.16 | an estimate has `lo ≤ hi` (V3); returns `id` | `RISK_RANGE` | `RiskRange: {id}` |
| · 15.1.17 | an estimate has an estimator and a support (V3); returns `detail` | `RISK_ESTIMATE_PROVENANCE` | `EstimateProvenance: {detail}` |
| · 15.1.18 | an estimate's estimator is allowed for its quantity's kind (V3); returns `detail` | `RISK_ESTIMATOR_NOT_ALLOWED` | `EstimatorNotAllowed: {detail}` |
| · 15.1.19 | a quantity has at most one setting, and none with an estimate (V4); returns `quantity` | `RISK_SETTING_TWICE` | `RiskSettingTwice: {quantity}` |
| · 15.1.20 | a condition mentioning a setting is on that alternative's cells (V4); returns `detail` | `RISK_SETTING_SCOPE` | `RiskSettingScope: {detail}` |
| · 15.1.21 | two estimates of a quantity need a combination rule (V5); returns `quantity` | `RISK_CONFLICTING_ESTIMATES` | `ConflictingEstimates: {quantity}` |
| · 15.1.22 | estimates intersect under `intersection`; a stated cell agrees with its sources (V5, V8, V9); returns `detail` | `RISK_INCONSISTENT` | `RiskInconsistent: {detail}` |
| · 15.1.23 | every quantity of a condition has an estimate or a setting (V5); returns `quantity` | `RISK_UNESTIMATED` | `RiskUnestimated: {quantity}` |
| · 15.1.24 | one source per side per cell (V6); returns `detail` | `RISK_TWO_SOURCES` | `RiskTwoSources: {detail}` |
| · 15.1.25 | a statement is `leads`, `cannot` or `might` (V6); returns `form` | `RISK_STATEMENT_FORM` | `RiskStatementForm: {form}` |
| · 15.1.26 | a condition, and each cell's `S ∧ ¬N`, is separable (V7, V8); returns `quantity` | `RISK_CONDITION_SHARED` | `RiskConditionShared: {quantity}` |
| · 15.1.27 | an equality has unit coefficients (V7); returns `detail` | `RISK_EQUALITY_COEFFICIENT` | `RiskEqualityCoefficient: {detail}` |
| · 15.1.28 | the sufficient side lies within the necessary side (V8); returns `detail` | `RISK_SUFFICIENT_OUTSIDE_NECESSARY` | `SufficientOutsideNecessary: {detail}` |
| 15.2 | hook `margin_candidates_fit` at `/decision` | `RISK_RESOURCE_LIMIT` | `ResourceLimit: risk margin candidates` |

A member's `detail` (or the named argument) is the route's text after the member's fixed leading text; for
15.1.9 and 15.1.13 the text between the parentheses. Where one leading text is printed by several steps
(`RiskConstant`, `RiskFact`, `RiskInconsistent`, `RiskConditionShared`, `UnknownSymbol: unit`,
`UnknownSymbol: quantity`, `UnitMismatch(`, `UnitPrecision(`, `InvalidModel(alternatives): `), the set has one
member, and the catalogue's order keys tell the steps apart (2.5). The witness case that the route appends to
15.1.22 and 15.1.28 (`withCase`) is part of `detail`.

**What is not in the table, and why.** The six fallback texts above. `UnknownSymbol: unit <t>` at V3 and V4:
the quantity's tag was checked at V1, so an estimate or setting cannot reach it; at V7 a condition literal can
(15.1.8). `DuplicateDeclaration: dependency node <c>` from `dependencyOrder`: duplicate classes are 7.1.4
first. `ResourceLimit: fulfilments` and `ResourceLimit: rules` in `checkFulfilments` and `check`, as in 2.3.

**Planned tiers.** 142 numbered checks (a classifier set counts once; 14.11a to 14.11g count seven; 3.x as in
2.3). T1: phase 1 (11), phase 2 (2.2 to 2.7: 6), phase 3 (33), phase 4 (all but 4.2a: 42), phase 5 (4),
6.5, phases 10 to 13 as 2.3 (6), phase 14 (14.1, 14.2, 14.4 to 14.9, 14.11a, 14.11b, 14.11d to 14.11g,
14.12, 14.14 to 14.23e, 14.25, 14.26: 44) (147 rows; 103 numbered checks). T2 not inherited: 2.15 to 2.17,
3.5f, 3.9h, 4.2a, 6.3, 6.4, 6.7, 9.1, the nine of phases 10 to 13 that 2.3 lists, 14.3, 14.10, 14.11c,
14.13, 14.24, 14.27 to 14.31, 14.33, 14.34, 15.2 (31). Inherited hooks: 2.1, 2.8 to 2.14, 5.3, 6.6 (10).
T3: 6.1, 6.2, 7.1, 8.1, 14.32, 15.1 (6). The counts are the build's to confirm against the contract as
built; the gate reports them and requires none. The Python engine's fast path is phase 1.

### 2.5 The hooks and classifiers

Rules of base spec 2.5 apply: a hook or classifier reads its two arguments only, may assume every earlier
instance holds, and is required to agree across languages only on such inputs. **Lean implements every one**,
in `lean/VE/WireContract/Hooks/Alternatives.lean` and `Hooks/Risk.lean`, calling the frozen functions of the
route read-only on the values the earlier steps decoded, as `Hooks/SoftNorms.lean` does; never
`decodeAltSource`, `decodeRiskSource`, `admitDecision` or `validateDecision` as a whole, except where the
table's step is that whole function (15.1) or a prefix of it (14.13 to 14.34). **Python implements none:**
`ve/alternatives_contract.py` and `ve/risk_contract.py` register every hook, classifier and view name of
their contract with the value `None`, which `engine.run` reads as deferred (`ve/wire_contract/engine.py:453–463`)
and `tools/wire_contract.py` as registered. Python's engine therefore evaluates phase 1 of each table (T1 only)
and defers at 2.1 on every root that passes it; its deferred share on the corpus is the share of roots that
pass phase 1, reported, and its fault, when it has one, is compared with Lean's at zero tolerance (2.13). This
keeps the public text of every inherited check the route's text (D5) and adds no Python code that production
could not reach, because the engine stops at the first deferred instance.

The Lean side, per name. "After step *n*" means the function is applied to the values that the route's
steps up to *n* produced from the root, recomputed by the hook; where the route has no function for one step,
the hook holds the step's lines (`Hooks/*.lean` is hand-written and under no theorem).

| Name | Lean |
|---|---|
| `w1_environment` | alt: `Norms.Wire.decodeNormsEnvironment (normsView environment ps)` (`Wire.lean:198`); risk: the same on `riskNormsView environment ps` (`:314`). The view is applied inside the hook; a failure's text is the decoder's |
| `route_envelope` (risk 2.1) | `Route.Gate.decodeEnvelope (riskNormsView environment ps)` (`:309`); the family check is 2.2 and 2.3 |
| `no_definitions`, `no_data_flags`, `no_string_literals` | `ne.rv.definitions.isEmpty`, `ne.rv.flags.isEmpty`, `ne.rv.literals.isEmpty` on the decoded environment |
| `decider_nonblank` | `d.trim.isEmpty` is false (`Wire.lean:67`) |
| `fulfilment_body_decodes` | `VE.Bridge.decodeFormula 64` succeeds on the item's `body` (`:122`) |
| `w1_norm` | `Norms.Wire.decodeNorm` on the item (`lean/VE/Norms/Wire.lean:231–255`); the text is the decoder's |
| `premise_unit` | `exactFields item ["label", "ast"]`, `stringField item "label"`, `decodeFormula 64 (item.ast)` (`Wire.lean:174–178`); the text is the decoder's |
| `premise_typed` | alt: `a.check (extEnv A0) []` (`:215`); risk: `a.check (riskExtEnv R0) []` (`:293`) |
| `block_declarations` | `checkBlock A0` (alt, `:211`) or `checkBlock (toAlt R0)` (risk, `:332`); the member is the first of 6.1.1 to 6.1.21 whose fixed leading text the message starts with, and the argument is the rest |
| `role_verbalisations` | `checkVerbalisations b.alt vocabulary` (`:212`, `:333`); the member is the one whose text the message equals |
| `avoids_obligation`, `excludes_obligation` | `checkAvoids A0 [o]` for the item's obligation (`:155–159, 213, 334`); for `excludes`, the loop of `:335–338` on the item alone |
| `rule_typing`, `rule_typing_risk` | the loop body of `checkProfileTyping` (`Decl.lean:223–230`) or `checkRiskTyping` (`:262–268`) for the item's rule; a message with the leading text `ResourceLimit: ` names member b, any other message member a; a rule whose predicate is not regulated gives `ok`, as the route skips it |
| `alt_inlining_fits` | the second loop of `checkProfileTyping` on `toAlt R` for the item's rule |
| `regulated_predicate` | `T.regulated.find? (·.name == N.pred)` is some (`Tree.lean:338`) |
| `inlined_nodes_fit` | the sum of `formulaNodes` over the inlined guards and carve-outs of the rules up to and including the item is at most 10,000 (`Tree.lean:345–346`) |
| `over_same_predicate`, `precedence_acyclic`, `precedence_depth_fits`, `layers_acyclic` | the S5 spec's four, on the inlined tree (`Tree.lean:347–362`); the detail is the text after `DependencyCycle: ` |
| `fulfilment_not_performed`, `fulfilment_obligation`, `fulfilment_body_base` | the three branches of `checkFulfilments`' loop body for the item (`Decl.lean:239–247`) |
| `w6_unit` | `Time.Wire.decodeUnit tag record` on the item (`Wire.lean:99`) |
| `w6_display_injective` | `Time.Wire.displayInjective` on the decoded units (`:100`) |
| `w6_argument_units` | the predicate branch of `checkVocabularyUnits` on the item (`:123–126`) |
| `w6_constant_verbalisation`, `w6_constant_unit` | the two parts of the constant branch of `checkVocabularyUnits` on the item (`:127–136`) |
| `w6_extension` | `checkExtension environment units` (`:140–149`) |
| `not_stage_field` | the item's key is not in `stageFields` (`:157, 193–194`) |
| `risk_block_declarations` | `checkRiskBlock R0` (`Decl.lean:210–255`); the member by leading text |
| `w6_day` | `decodeDay` succeeds on the target (`Wire.lean:348–351`) |
| `estimate_recorded` | the item has `seq` and `day` (`:391–396`); `id` is the item's `id` when a string, else the empty string |
| `decision_entry_hash` | `entryHash dx == dx.hash` (`Record.lean:494`) |
| `policy_binding` | `r.policy == R.policy` (`:498`) |
| `cite_precedes_decision`, `cited_entry_exists`, `cited_entry_unaltered`, `cited_estimate_not_withdrawn` | `citeFailure dx es c` on the item (`:467–474`) returns `none`, or a text whose leading word is later than the hook's; that is, the hook with leading word *w* fails exactly when `citeFailure` returns a text starting with *w* |
| `fact_cites_instruction_or_statement` | `factFailure` restricted to the item (`:477–483`) |
| `cited_content` | `decodeItem R qs x` on the entry the item cites (`:384–441`); an `.error` names the member whose text it equals; an `.issue` or a value is `ok` |
| `estimates_and_settings_fit`, `conditions_and_statements_fit` | the two counts of `buildDecision` (`:456–459`) |
| `record_validation` | `validateDecision R d` on the admitted record, its text passed through `withCase R d` (`Run.lean:281–288`); the member by leading text |
| `margin_candidates_fit` | `marginLimit R d` (`Report.lean:122–124`) |

**Order keys inside the sets** (base spec 2.6; recorded by the fault catalogue). `block_declarations`,
`role_verbalisations`, `risk_block_declarations` and `cited_content`: the member's index in `emits`, which is
the route's order. `rule_typing` (alt): (0, *i*) for a typing fault of formula *i* and (1, *i*) for its
inlining, because the route types every formula before it inlines any. `rule_typing_risk`: (*i*, 0) and
(*i*, 1), because the route types and inlines one formula before the next. `record_validation`: (*step*,
*member index*, *item index*) with *step* the validation step 1 to 11 that reports the fault and *item
index* the position of the cited content, condition, cell or quantity the step reads, in the route's order
within that step; the catalogue states the key with every fault of the set.

**Views.** None. `normsView` and `riskNormsView` are applied inside `w1_environment` and `route_envelope`.

**Adapters.** `alt_source` and `risk_source` as 2.2, in both languages.

### 2.6 Shadow and public

As S4 spec 2.2, for each unit. While `status` is `shadow`, no output of any program depends on the contract.
When it is `public`, exactly one output depends on it: the row that the unit's call site returns (2.8).
Nothing in Lean reads `status`. Changing `status` is a contract edit and raises the revision; today's output
is restored by reverting the switch commit or by a later revision that sets `status` to `shadow`.

### 2.7 The boundary functions

```
ve.alternatives_contract.public_rejection(case, row, *, contract=None, registry=None, lean=None)
ve.risk_contract.public_rejection(case, row, *, contract=None, registry=None, lean=None)
```

`case` is the case the route received and `row` the row it returned, with `status` `error`. The keyword
arguments exist for tests; the production call passes none, and the function then uses the locked contract
(`engine.load`), the module's `REGISTRY` (every name deferred, 2.5) and the module's `lean_outcome`.

The function returns `row`, the same object, in every case. It does this, in order:

1. If `row` has a member `diagnostic`, return.
2. If the contract's `status` is not `public`, return.
3. Let the root be the adapter's root of a deep copy of `case` (2.2); `case` and `row` are not modified
   before step 6.
4. Let `outcome` be `engine.run(contract, root, registry=registry)`.
5. Let `error` be `checker_error(row["error"])`, the `VEError` the row stands for, and `record` be
   `engine.overlay(contract, error, outcome, lean=lean)`. With `outcome` deferred, `overlay` calls `lean`,
   which is `lean_outcome(case)`: it submits `[case]` to `ve_diagnose <unit>` through
   `ve.backends.lean.run("wire.diagnose", …, runner="ve_diagnose", mode=<unit>, timeout=180)`, the
   manifest-bound transport (`ve/backends/lean.py:131–169`), and returns `Fault(row["diagnostic"])` when the
   row's `outcome` is `fault` and `CLEAN` when it is `clean`; a `CheckerUnavailable` stays inside `overlay`,
   which then reports the deferred record (`engine.py:505–513`).
6. Set `row["diagnostic"]` to `record`, and when `record` is a fault record set `row["error"]` to its
   `text`. Return.

**Failure rule.** If loading the contract or any of steps 3 to 5 raises an `Exception`, the function returns
`row` as it received it: no `diagnostic`, the route's text. A rejection is never turned into a different
failure by its diagnosis. The gate counts such cases and requires none (9).

What the function never does: it does not write `status` or `id`; it does not create a row; it does not call
the route on the source itself (the hooks of 2.5 call parts of it, in Lean); it starts at most one Lean
process, `ve_diagnose`, and only when the Python engine defers.

By the overlay, the reported record is one of three:

| Engine outcome, after the consultation | `row["diagnostic"]` | `row["error"]` |
|---|---|---|
| `fault(r)` | `r` | `r`'s `text` |
| `clean` (Lean's engine reports clean) | the residual record, whose `text` is the route's text | unchanged |
| deferred, and `wire.diagnose` unavailable | the deferred record `{"contract", "revision", "deferred": id, "text"}`, whose `text` is the route's text | unchanged |

On every root that passes phase 1, the Python engine defers at 2.1, so on such a root the record is Lean's
engine's or the deferred record. A fault of phase 1 is final and consults no Lean process (base spec 2.8).

### 2.8 The call sites

**`alternatives@0`.** In `ve/alternatives.py`, `run_case(case, *, binary=None, timeout=180)` refuses a case
that is not an object of a known kind with an object environment (`:21–22`), decodes the environment with
Python's `Environment` and requires `alternatives@0` (`:23–26`), refuses the Python authority and a missing
binary (`:27–31`), and returns `run_alternatives_case(executable, case, timeout=timeout)` (`:32`). The switch
binds that result to a name and, when its `status` is `error` and `case["kind"]` is `alt-elaborate`, passes
it through `public_rejection(case, row)` and returns the result; the import of `public_rejection` is a
statement inside that branch. Nothing else in the file changes. An error from `Environment` (`:24`), from the
kind check or from the transport keeps today's text and has no record.

**`risk@0`.** In `ve/risk.py`, `run_case` (`:226–241`) refuses a malformed case and the Python authority and
returns `run_alternatives_case(executable, case, timeout=timeout)` (`:241`). The switch is the same shape,
for `case["kind"]` in `risk-elaborate` and `risk-decision`, with `ve.risk_contract.public_rejection`.

The admission path (`ve/admission.py:508–514`) calls `run_case` with kind `admission`; its row is returned
unchanged and `AdmissionError` is raised as today (plan section 4).

Three properties follow from this shape and are tested (8.4), not proved:

- **(V1) The verdict is the route's.** Each call site returns a row whose `status` and `id` are the route's
  row's, and on an `ok` row the route's row itself; the switched branch runs only on an error row.
- **(V2) An accepted case does not reach the engine.** On an `ok` row neither contract module nor
  `ve.wire_contract` is imported by this call.
- **(V3) The engine and the route read the same case.** The root is built from a deep copy of the case the
  transport sent, and `lean_outcome` sends that case (fixture Z5).

**The import rule** of base spec 7.3 and S5 spec 2.8 gains two rows: `ve.alternatives_contract` is imported
only by `ve/alternatives.py`, and `ve.risk_contract` only by `ve/risk.py`; each importer imports the one name
`public_rejection` in one import statement and one call, both inside the branch of `run_case` that handles an
error row, the call being the operand of a `return`; no module imports `ve.wire_contract`; the two contract
modules import `ve.backends.lean` for `lean_outcome` and nothing else of `ve/` outside `ve.wire_contract`,
`ve.wire`, `ve.errors` and `ve.backends.diagnostics`. The scan of
`tests/test_softnorms_contract.py::test_diagnostic_modules_stay_off_verdict_import_paths` is extended over the
two rows. The Lean import rule is unchanged.

**The Lean call site.** `lean_outcome` is a declared call site of `wire.diagnose` in the manifest
(`lean_call_sites`: `ve.alternatives_contract:lean_outcome`, `ve.risk_contract:lean_outcome`), as
`ve/assurance.py:111–124` requires; the binding of each unit lists the kinds of 2.2 and the response
`{"outcome": "string"}` (5.4).

### 2.9 Entry points: switched, and not switched

| Entry point | After the switch |
|---|---|
| `ve.alternatives.run_case` on an `alt-elaborate` case, after Python's `Environment` has accepted the environment | **public** for `alternatives@0`: an error row carries the reported record |
| `ve.risk.run_case` on a `risk-elaborate` or `risk-decision` case | **public** for `risk@0` |

Not switched; each keeps today's text and has no record:

| Entry point | Why not in item 1 |
|---|---|
| `Environment(environment)` at `ve/alternatives.py:24`, and `Environment` wherever else it validates an environment with a block (`ve/admission.py:450, 503`; the English front ends) | a different validator of the environment only, in Python's order; its block checks are `vocabulary@0.2`'s territory with the blocks (base plan 5.3, row 4); S7-pre measures its verdict against the route's (2.12) |
| `run_case` on `alt-validate`, `alt-conflict`, `alt-followable`, `alt-certificate`, `risk-conflict`, `risk-followable`, `risk-audit`, `risk-certificate` | the route goes on after the source to inputs the table does not cover (plan section 4) |
| `run_case` on `admission`, and `ve/admission.py:508–514` | the W2 document (row 13) and the kind's domain (2.2) |
| `ve.document`'s check of a document with a block (`ve/document.py:1074`) | it reaches admission |
| every Lean row and every Rust output | base plan 2.5; Rust has no column |

Until their own rows, the same fault can therefore read differently through two entry points (plan section
8, question 5).

`tests/test_risk_diagnostics.py::test_route_answer_is_leans_through_python_dispatch` asserts that
`run_case`'s row equals the route's row byte for byte. After the switch the two differ in `diagnostic` and in
`error` where the signed list says so; the test keeps the equality on every other member and compares
`error` under the signed list (plan section 8, question 10).

### 2.10 The contract edits

Revision 1 of each contract is the shadow one of 2.3 and 2.4. The shadow may edit either; the switch of a
unit is one further revision, written `R` in sections 4 and 8, whose only differences from the revision
before it are `"revision": R` and `"status": "public"`. What follows mechanically, by
`tools/wire_contract.py --write`: `contracts.lock`; `lean/VE/WireContract/Tables/Alternatives.lean` or
`Tables/Risk.lean` (the header comment and the numeral of the table's `revision`, nothing else) and the
module's line in `VE/Route/frozen-sources.sha256`; `docs/spec/alternatives-wire-table.md` or
`risk-wire-table.md` (no change expected; `--check` decides). Every record of either engine then has the
new `revision`, so the stored reports that hold records are regenerated (gate, golden, catalogue, delta).

### 2.11 A public change, and the delta

As S5 spec 2.11, on rows. For a corpus case on which the route rejects with the legacy text `m` and legacy
class `c`, let `r` be the reported record: `engine.overlay(contract, checker_error(m), engine.run(contract,
root, registry=REGISTRY), lean=lean_outcome(case))`. The case has a **text change** when `r`'s `text` is not
`m`; a **class difference** when `r` has a `class` and it is not `c`; it is **attributed** to `r`'s `check`
(an id or `residual`), or to `deferred`. Every check counts, inherited ones too. A case the route accepts has
no public change.

A rejected case is **handler-reaching** when the call on the case reaches the switched branch of 2.8: for
`alternatives@0`, an `alt-elaborate` case whose environment Python's `Environment` accepts; for `risk@0`, a
`risk-elaborate` or `risk-decision` case. On any other rejected case the call returns today's row with no
record; the record `r` of such a case is a result of the engine and of the boundary function and is never
public.

The **delta report** `conformance/wire-contract/<unit>-delta.json` has `public_diagnostic_changes` as the S5
spec defines it, computed over the handler-reaching cases of the whole corpus and stored, and
`consultations`: the number of corpus cases on which the Python engine deferred and the Lean consultation
answered, with its outcome counts (fault, clean, unavailable). It has no `lean_route_changes`: the table's
order is the route's, so the route's text and the record's differ only inside a classifier set and only on a
multi-fault input, which tier A reports as a mismatch, not as a route difference.

The **signing file** `conformance/wire-contract/<unit>-switch.json` is written by hand, as the pilot's. A class
difference cannot be signed (2.12).

### 2.12 The class rule, and S7-pre

**The class rule.** On every corpus case where the reported record is a fault, the record's `class` is the
legacy class (2.1), except on the inherited checks, whose one code has the class `InvalidInput` while the
decoder they run prints several classes: `alternatives@0` 2.1, 4.3, 5.2, 7.1a; `risk@0` 2.1, 2.8 to 2.14,
5.3, 6.6, 8.1a. Each exemption is listed in section 10, and the gate counts the cases it covers. The rule is
checked on every rejected case of the corpus, handler-reaching or not: it is a property of the engine's
record.

The rule holds by construction for every check that is not inherited: each code's class is
`checker_error`'s class of the texts declared under it (2.3, 2.4), and the Lean classifier members take the
route's text. It can fail only on a residual record, whose class is `InvalidInput` whatever the route printed,
and the residual count must be 0.

**S7-pre** blocks the `alternatives@0` switch. The alternatives route has two validators in sequence: Python's
`Environment` on the environment, then the Lean route (2.8). The shadow gate lists, for every corpus root
whose `norms` and `units` are empty, the cases on which `Environment(environment)` and the route disagree on
the verdict (`legacy_verdict_differences`). Each is treated as a class and run to ground, as S3-pre, S4-pre and
S5-pre were, outside this work, and recorded in `conformance/wire-contract/s7-pre.md`; closed means the gate
reports the list empty, and the gate fails otherwise. From reading, the candidates are:

| Candidate | Python's `Environment` | The Lean route |
|---|---|---|
| a predicate whose verbalisation reads like a profile word (`{0} prevents {1}`, …) | `AlternativesReserved: wording for <p>` (`ve/environment.py:176–180`) | no check: accepted when everything else holds |
| a fulfilment body that is an array the decoder refuses (`["unary"]`) | accepted: Python checks that the body is a list and nothing else (`:270–271`) | `InvalidInput: alternatives.fulfilments` (3.9h). Not a public difference: the route runs after `Environment` and rejects; it is listed because the gate's root-level comparison sees it |

A verdict difference is fixed outside this plan, in Python first where Python's verdict changes (a changed
verdict of a rejected or accepted cell is a product decision). Text and order differences between
`Environment` and the route are not S7-pre's: `Environment` is not switched and keeps its texts (2.9).
`risk@0` has no S7-pre: `ve/risk.py` runs no Python validator; the gate's list for it is expected empty and is
enforced empty all the same.

### 2.13 What is constructed and what is tested

By construction:

- **(A) The public record is the measured one.** Each call site reports `overlay(run(…), lean=…)` through
  its `public_rejection`, and the gate measures the delta with the same functions on the same registry and
  the same consultation.
- **(B) In Lean only the generated tables' revisions change at a switch** (T3, L4).
- **(C) The base spec's claims (A) and (B)** hold for both contracts: the expansion, and the record
  conditional on equal predicate results. For these units "equal predicate results" is trivial outside phase
  1: the Python engine defers, and the record is the Lean engine's.
- **(D) The class rule** for every check that is not inherited (2.12).
- **(E) On a one-fault source the record's text is the route's text**, for every check that is not inside a
  classifier set: the table is the route's checks in the route's order with the route's texts, and the
  catalogue's expected `args` are read from the input where the route reads them. Tier 0 tests it on every
  fault; it is stated here so that the expected delta (section 6) is empty on such sources.

Tested, not constructed:

- that the Lean engine reports a fault exactly when the route rejects, on the corpus, at zero tolerance,
  and that a Python fault (phase 1) is Lean's fault;
- that the signed list is complete: on the corpus only;
- that the Lean classifier members name the route's step: the order inside the six sets of `risk@0` and the
  three of `alternatives@0`, with the order keys of 2.5 (tiers 0 and A);
- V1, V2 and V3 of 2.8.

Not claimed: that Python's `Environment` and the route agree (S7-pre measures it); that the consultation is
available in every deployment (the deferred record covers its absence); that a record is public through any
entry point of 2.9's second table.

### 2.14 Item 2: `UnitPrecision` gets one encoding

Today an off-grid decimal literal is rejected with the message `UnitPrecision(<tag>, scale=<n>)` under the
class `InvalidInput` by Python (`ve/units.py:270`), by Lean's quantity route (`lean/VE/Time/Wire.lean:362`),
by Lean's risk route and evaluator (`lean/VE/Risk/Record.lean:282–283`) and by Rust's unit decoder
(`rust/ve-core/src/units.rs:154–158`), and with the code `UnitPrecision` and the message `<tag>, scale` by
Rust's risk evaluator (`rust/ve-core/src/risk.rs:110–112`). Item 2 changes the one line of `risk.rs` to
`error("InvalidInput", format!("UnitPrecision({tag}, scale={scale})"))`, where `scale` is the tag's scale as
the evaluator holds it (the multiplier `10^k`, `:88–95`), so that the Rust text equals Lean's
`precisionText` on the same tag. `tests/test_risk_differential.py` reads a Rust error as `code: message`
(`:192–196`); it gains the rule that a Rust error of code `InvalidInput` is compared by its message alone
(Lean prints no class before a sub-code), and one shard whose conditions carry an off-grid literal, which
both must reject with one text (8.9). No verdict changes: the literal was rejected before and is rejected
after. No contract names the Rust evaluator; the change is a diagnostic of Rust's own, signed in its commit's
release note.

## 3. English: one reading each

### 3.1 The hand-written sentences

The generated wordings of base spec 3.1 cover every T1 row of the two tables; `tools/wire_contract.py` writes
them to `docs/spec/alternatives-wire-table.md` and `docs/spec/risk-wire-table.md`. The hooks and members
carry these `says` sentences. "The item" is the innermost group's item, which the generated lead names
(`For the `units` item: `). Each string is exactly as shown, backticks included. The first block is
`alternatives@0`; `risk@0` reuses it for the names its table shares (with `/document/norms` for `/norms` and
`/document/units` for `/units`) and adds the second block.

```json
{"2.1":    "W1's environment decoder accepts `/environment` with the member `alternatives` removed and `alternatives@0` dropped from `/environment/profiles`.",
 "2.2":    "No predicate of `/environment/vocabulary/predicates` has a `defined` member.",
 "2.3":    "No predicate of `/environment/vocabulary/predicates` has a `functional` or `total` member equal to `true`.",
 "3.5f":   "`/environment/alternatives/outcomes/complete_by`, when present, contains a character other than a space, a tab, a carriage return or a line feed.",
 "3.9h":   "The item's `body`, when it is an array, is a formula of the P0 wire form within 64 levels.",
 "4.3":    "W1's norm decoder accepts the item: an object with exactly the member `norm`, whose `norm` has exactly the members `name`, `predicate`, `sign`, `guard`, `unless` and `over`, with a string `name`, a string `predicate`, a Boolean `sign`, an array `unless`, an array of strings `over`, and a `guard` and each carve-out that decode within one node and depth budget.",
 "5.2":    "The item is an object with exactly the members `label` and `ast`, whose `label` is a string and whose `ast` is a formula of the P0 wire form within 64 levels.",
 "6.1.1":  "`/environment/alternatives/chooser` names a sort of `/environment/vocabulary/sorts`.",
 "6.1.2":  "`/environment/alternatives/action` names a sort of `/environment/vocabulary/sorts`.",
 "6.1.3":  "`/environment/alternatives/harm` names a sort of `/environment/vocabulary/sorts`.",
 "6.1.4":  "The sorts named by `/environment/alternatives/chooser`, `action` and `harm` are three different sorts.",
 "6.1.5":  "No sort, predicate or constant of `/environment/vocabulary` is named `avoidable`, `unavoidable`, `allows` or `prevents`.",
 "6.1.6":  "`/environment/alternatives/available` names a predicate of `/environment/vocabulary/predicates`.",
 "6.1.7":  "The predicate named by `/environment/alternatives/available` has no `regulated` and no `defined` member.",
 "6.1.8":  "The predicate named by `/environment/alternatives/available` has exactly the argument sorts named by `/environment/alternatives/action` and `/environment/alternatives/chooser`, in that order.",
 "6.1.9":  "`/environment/alternatives/leads_to` names a predicate of `/environment/vocabulary/predicates`.",
 "6.1.10": "The predicate named by `/environment/alternatives/leads_to` has no `regulated` and no `defined` member.",
 "6.1.11": "The predicate named by `/environment/alternatives/leads_to` has exactly the argument sorts named by `/environment/alternatives/action` and `/environment/alternatives/harm`, in that order.",
 "6.1.12": "When `/environment/alternatives/inaction` is present: it names a predicate of `/environment/vocabulary/predicates`.",
 "6.1.13": "When `/environment/alternatives/inaction` is present: the predicate it names has no `regulated` and no `defined` member.",
 "6.1.14": "When `/environment/alternatives/inaction` is present: the predicate it names has exactly one argument sort, the one named by `/environment/alternatives/action`.",
 "6.1.15": "When `/environment/alternatives/taken` is present: it names a predicate of `/environment/vocabulary/predicates`.",
 "6.1.16": "When `/environment/alternatives/taken` is present: the predicate it names has no `regulated` and no `defined` member.",
 "6.1.17": "When `/environment/alternatives/taken` is present: the predicate it names has exactly one argument sort, the one named by `/environment/alternatives/action`.",
 "6.1.18": "When `/environment/alternatives/proximate` is present: it names a predicate of `/environment/vocabulary/predicates`.",
 "6.1.19": "When `/environment/alternatives/proximate` is present: the predicate it names has no `regulated` and no `defined` member.",
 "6.1.20": "When `/environment/alternatives/proximate` is present: the predicate it names has exactly the argument sorts named by `/environment/alternatives/action` and `/environment/alternatives/harm`, in that order.",
 "6.1.21": "When `/environment/alternatives/performed` is present: its `permission` names a regulated predicate of role `permission` whose one argument sort is the action sort, and its `obligation` names a regulated predicate of role `obligation` whose one argument sort is the action sort and whose `permission` is that `permission`.",
 "6.2.1":  "The predicate named by `/environment/alternatives/available` has the verbalisation `{0} is available to {1}`.",
 "6.2.2":  "The predicate named by `/environment/alternatives/leads_to` has the verbalisation `{0} leads to {1}`.",
 "6.2.3":  "When `/environment/alternatives/inaction` is present: the predicate it names has the verbalisation `{0} is inaction`.",
 "6.2.4":  "When `/environment/alternatives/taken` is present: the predicate it names has the verbalisation `{0} is taken`.",
 "6.2.5":  "When `/environment/alternatives/proximate` is present: the predicate it names has the verbalisation `{0} causes {1}`.",
 "6.2.6":  "No predicate of `/environment/vocabulary/predicates` other than the one named by `/environment/alternatives/available` has the verbalisation `{0} is available to {1}`.",
 "6.2.7":  "No predicate other than the one named by `/environment/alternatives/leads_to` has the verbalisation `{0} leads to {1}`.",
 "6.2.8":  "No predicate other than the one named by `/environment/alternatives/inaction` has the verbalisation `{0} is inaction`.",
 "6.2.9":  "No predicate other than the one named by `/environment/alternatives/taken` has the verbalisation `{0} is taken`.",
 "6.2.10": "No predicate other than the one named by `/environment/alternatives/proximate` has the verbalisation `{0} causes {1}`.",
 "6.3":    "The item's `obligation` names a regulated predicate whose argument sorts are exactly the chooser sort and the harm sort, in that order.",
 "6.4":    "The item's `ast` is a closed formula that is well typed over `/environment/vocabulary` extended by the four profile words.",
 "7.1a":   "The item's `norm/guard`, and then each of its `norm/unless`, is well typed over `/environment/vocabulary` extended by the four profile words, in the context of its predicate's argument sorts.",
 "7.1b":   "Each of the item's `norm/guard` and `norm/unless`, with every profile-word atom replaced by its body, has at most 10,000 nodes.",
 "8.3":    "The item's `norm/predicate` names a predicate declared with `regulated`.",
 "8.5":    "The guards and carve-outs of the `rules` items up to and including this one, with every profile-word atom replaced by its body, together have at most 10,000 nodes.",
 "9.2":    "The rule named by the item has the same `predicate` as the enclosing item's rule.",
 "10.1":   "The precedence graph over `/norms`, with an edge from each rule to each rule its `over` names, is acyclic.",
 "10.2":   "Every rule's precedence height, which is 1 for a rule that no rule names in `over` and otherwise 1 more than the greatest height of the rules that name it, is at most 16.",
 "10.3":   "The graph over the regulated predicates, with an edge from a rule's predicate to each regulated predicate its guard or carve-outs mention, is acyclic.",
 "11.1":   "The item's `obligation` is not the `obligation` of `/environment/alternatives/performed`.",
 "11.2":   "The item's `obligation` names a regulated predicate of role `obligation` whose first argument sort is the chooser sort.",
 "11.3":   "The item's `body`, with `avoids` read as `not leads_to(a, h)`, is well typed over `/environment/vocabulary` in the context of the action sort followed by the obligation's argument sorts after the first, and mentions no regulated or defined predicate."}
```

```json
{"2.1":     "The route's envelope decoder accepts `/environment` with the members `alternatives`, `risk`, `unit_schema` and `units` removed, `alternatives@0` and `risk@0` dropped from `/environment/profiles`, and, when `/environment/unit_schema` is present, every constant's `unit` and `verbalisation` and every predicate's `argument_units` removed.",
 "2.8":     "W6's unit decoder accepts the item under its key: the key is an identifier other than `dimensionless`, the record has exactly the members `scale` and `display`, the scale is a positive power of ten and the display is one of W6's forms.",
 "2.9":     "No display affix of the units of `/environment/units` touches an amount, and no two affixes on one side extend each other.",
 "2.10":    "When the item has `argument_units`: it is an object whose keys are decimal slot numbers below the length of the item's `arguments`, each slot has the sort `$int`, and each value is `dimensionless` or a tag of `/environment/units`.",
 "2.11":    "When the item has `verbalisation`: it is a nonempty string of at most 256 characters.",
 "2.12":    "When the item has `unit`: the item's `sort` is `$int` and the unit is `dimensionless` or a tag of `/environment/units`; a constant of a declared sort has no `unit`.",
 "2.13":    "W1's environment decoder accepts `/environment` with the members `alternatives`, `risk`, `unit_schema` and `units` removed, `alternatives@0` and `risk@0` dropped from `/environment/profiles`, and the W6 annotations of 2.1 removed.",
 "2.14":    "No tag of `/environment/units`, and not `dimensionless`, is a sort of `/environment/vocabulary/sorts`; no constant has the sort `$string`; every constant's `verbalisation` is whitespace-normalised, and no two constants have verbalisations that coincide when one starts a sentence.",
 "2.15":    "No predicate of `/environment/vocabulary/predicates` has a `defined` member.",
 "2.16":    "No predicate of `/environment/vocabulary/predicates` has a `functional` or `total` member equal to `true`.",
 "2.17":    "No constant of `/environment/vocabulary/constants` has the sort `$string`.",
 "4.2a":    "The key of the item is not `chance_tag`, `bands`, `costs` or `additive_loss`.",
 "6.4":     "The item's `obligation` names a regulated predicate whose argument sorts are exactly the chooser sort and the harm sort, in that order.",
 "6.7":     "The item's `ast` is a closed formula that is well typed over `/environment/vocabulary` extended by the severity sort, the class constants, the three generated predicates, the four profile words and the two risk words.",
 "7.1.1":   "`/environment/risk/severity/sort` is not a sort of `/environment/vocabulary/sorts`.",
 "7.1.2":   "No sort, predicate or constant of `/environment/vocabulary` begins with `risk__` or equals a class of `/environment/risk/severity/classes`.",
 "7.1.3":   "`/environment/risk/severity/classes` has at least 1 and at most 16 members.",
 "7.1.4":   "The members of `/environment/risk/severity/classes` are distinct.",
 "7.1.5":   "Every name in `/environment/risk/severity/more_severe` and `/environment/risk/severity/unranked` is a member of `/environment/risk/severity/classes`.",
 "7.1.6":   "The graph over the classes, with an edge from each pair's first class to its second, is acyclic.",
 "7.1.7":   "No pair of `/environment/risk/severity/unranked` names one class twice or two classes one of which is more severe than the other in the transitive closure of `more_severe`.",
 "7.1.8":   "Every pair of `/environment/risk/harm_classes` names a constant of the harm sort and a member of `/environment/risk/severity/classes`.",
 "7.1.9":   "No constant is named twice in `/environment/risk/harm_classes`.",
 "7.1.10":  "Every constant of the harm sort is named in `/environment/risk/harm_classes`.",
 "7.1.11":  "Every member of `/environment/risk/always_possible` is a member of `/environment/risk/severity/classes`.",
 "7.1.12":  "In every member of `/environment/risk/required_alternatives`, `when` and then each of `require` is a key of `/environment/risk/alternative_kinds`.",
 "7.1.13":  "Every value of `/environment/risk/quantity_kinds` is `dimensionless` or a tag of `/environment/units`.",
 "7.1.14":  "Every `quantity_kind` of `/environment/risk/required_estimators` is a key of `/environment/risk/quantity_kinds`.",
 "7.1.15":  "`/environment/alternatives/outcomes` is `signed`.",
 "8.1a":    "The item's `norm/guard`, and then each of its `norm/unless`, is well typed over `/environment/vocabulary` extended by the severity sort, the class constants, the three generated predicates, the four profile words and the two risk words, in the context of its predicate's argument sorts.",
 "8.1b":    "Each of the item's `norm/guard` and `norm/unless`, with every risk-word atom replaced by its body, has at most 10,000 nodes.",
 "9.1":     "Each of the item's `norm/guard` and `norm/unless`, with every risk-word atom and then every profile-word atom replaced by its body, has at most 10,000 nodes.",
 "14.3":    "`/decision/day` is a string of the form `YYYY-MM-DD` naming a calendar day from 1970 on.",
 "14.10":   "When the item's `kind` is `estimate`: the item has the members `seq` and `day`.",
 "14.11c":  "The item's `day` is a string of the form `YYYY-MM-DD` naming a calendar day from 1970 on.",
 "14.13":   "The SHA-256 of the canonical JSON of `/decision` without its `hash` equals `/decision/hash`.",
 "14.24":   "`/decision/content/policy` names the `environment_id` and `document_hash` of the policy of `/environment` and `/document`.",
 "14.27":   "The item's `seq` is below `/decision/seq`.",
 "14.28":   "Some member of `/entries` has the item's `id` and `seq`.",
 "14.29":   "That member's SHA-256, recomputed from its fields, equals both its `hash` and the item's `hash`.",
 "14.30":   "No member of `/entries` with a `seq` below `/decision/seq` is a supersession naming the item's `id`, or an estimate whose `supersedes` names it.",
 "14.31":   "The item's `entry` is the `id` of a member of `/decision/content/cites` whose entry is an instruction or a statement.",
 "14.32.1": "The cited estimate's content has the members `quantity`, `lo`, `hi`, `method` and `basis`, and at most `estimator`, `support` and `supersedes`, with string `quantity`, `lo`, `hi` and `supersedes` and a `support` among W2's five kinds.",
 "14.32.2": "The cited estimate's `estimator`, when present, has the member `name`, a string, and at most `version`.",
 "14.32.3": "The cited setting's content has exactly the members `quantity`, `value` and `alternative`, all strings.",
 "14.32.4": "The cited condition's content has the members `action`, `harm`, `form`, `condition`, `author` and `support`, and at most `note`; `form` is `sufficient`, `necessary` or `exact`; `condition` is a tree of 3.2 within 64 levels whose `scale` coefficients are integers; the strings are strings.",
 "14.32.5": "The cited statement's content has the members `action`, `harm`, `stated`, `author` and `support`, and at most `note`, with string `action`, `harm`, `author` and `stated`.",
 "14.32.6": "The cited condition, with coefficients collected per quantity, has at most 10,000 nodes.",
 "14.33":   "The cited estimates and settings are together at most 64.",
 "14.34":   "The cited conditions and statements are together at most 128.",
 "15.1.1":  "Every quantity a cited estimate, setting or condition names is a `name` of `/decision/content/quantities`.",
 "15.1.2":  "The names of `/decision/content/alternatives` are distinct.",
 "15.1.3":  "The names of `/decision/content/quantities` are distinct.",
 "15.1.4":  "When `/environment/alternatives/inaction` is present, exactly one alternative has `inaction` true; and the regenerated model satisfies alt's slot premises, its signed rows, its existence facts and the policy's base units.",
 "15.1.5":  "Every `harm` a cited condition or statement names is a constant of the harm sort.",
 "15.1.6":  "Every `action` a cited condition or statement names, and every setting's `alternative`, is a `name` of `/decision/content/alternatives`.",
 "15.1.7":  "Every `kind` of an alternative is a key of `/environment/risk/alternative_kinds`, and every `kind` of a quantity a key of `/environment/risk/quantity_kinds`.",
 "15.1.8":  "Every quantity's `tag`, and every tag a condition literal names, is `dimensionless` or a tag of `/environment/units`.",
 "15.1.9":  "A quantity with a `kind` has that kind's tag; in a cited condition, both sides of a comparison and both operands of `add` carry one tag.",
 "15.1.10": "Neither `/decision/content/chooser` nor an alternative's `name` equals a class, a constant of `/environment/vocabulary/constants` or another of those names, except an alternative named as an action constant; and every action constant is an alternative's `name`.",
 "15.1.11": "Every fact's `predicate` is a predicate of `/environment/vocabulary/predicates` that is not a role predicate, not generated, not regulated and not defined, and its `args` name entries of the constant table in that predicate's sorts.",
 "15.1.12": "For every member of `/environment/risk/required_alternatives` whose `when` is the `kind` of some alternative, each of its `require` is the `kind` of some alternative.",
 "15.1.13": "Every cited estimate's `lo` and `hi`, every cited setting's `value` and every decimal literal of a cited condition lies on the grid of its quantity's tag.",
 "15.1.14": "Each of those is a decimal of the form `-?(0|[1-9][0-9]*)(.[0-9]+)?`.",
 "15.1.15": "Each of those has at most 40 digits.",
 "15.1.16": "Every cited estimate has `lo` at most `hi`.",
 "15.1.17": "Every cited estimate has an `estimator` and a `support`.",
 "15.1.18": "When a cited estimate's quantity has a `kind` listed in `/environment/risk/required_estimators`, its estimator's `name` is among that kind's estimators.",
 "15.1.19": "No quantity has two cited settings, or a cited setting and a cited estimate.",
 "15.1.20": "Every cited condition that mentions a quantity with a cited setting is on that setting's `alternative`.",
 "15.1.21": "When `/environment/risk/combination` is absent, no quantity has two cited estimates.",
 "15.1.22": "Under `intersection`, the cited estimates of each quantity have a common value; a stated `leads` cell has a sufficient side that is certain on the box; a stated `might` cell has a necessary side that is possible on the box.",
 "15.1.23": "Every quantity a cited condition mentions has a cited estimate or a cited setting.",
 "15.1.24": "For each pair of an alternative and a harm, at most one cited source gives the sufficient side and at most one the necessary side.",
 "15.1.25": "Every cited statement's `stated` is `leads`, `cannot` or `might`.",
 "15.1.26": "In every cited condition, and in each cell's `S` and not `N`, no quantity that is not a point occurs in two atoms after negations are pushed to the atoms.",
 "15.1.27": "In every cited condition, every `=` atom has the coefficient 1 or -1 on each quantity that is not a point.",
 "15.1.28": "For every cell whose sufficient and necessary sides are both conditions and differ, no value in the box satisfies the sufficient side and not the necessary side.",
 "15.2":    "Every endpoint of every cited estimate has at most 256 margin candidates."}
```

The members 15.1.4 and 15.1.22 each gather several steps of the route under one leading text (2.4); their
sentences list the steps with "and", and the order keys of 2.5 keep the steps apart in the oracle.

### 3.2 How a public rejection reads

The S4 spec's four sentences (its 3.1) apply to every record of either unit, with `<wording>` the row of the
unit's table file. Example, for the source of fixture A52: `This input is rejected. The first check that
fails is 8.1: The `rules` item's `norm/name`, when present, is a string in the class `rule_name`.` For a
member of a classifier set the id is the member's, `15.1.16`, and the wording its `says` sentence. "First"
always means the order of base spec 2.6, which the table file shows from top to bottom.

### 3.3 Wordings this replaces, and why

| Wording | Its two readings | Written instead |
|---|---|---|
| "`alternatives@0` and `risk@0`, order taken from Lean (`checkAlt`, `checkRisk`, `checkView`)" (the base plan's row) | the three functions are the whole table; or they are the semantic tail of a route whose decoders come first | "The table is `decodeAltSource`'s and `decodeRiskSource`'s order from the profile gate on, and `checkView`'s for a record; the three named functions are phases 6 to 13 and 15." |
| "The diagnostics become uniform." | the three languages print one message; or the public row's `error` is the contract's text, which is Lean's | "The public row's `error` is the text of the record that `ve_diagnose` gives for the same case. Python prints no text of its own for these units, and Rust prints nothing." |
| "Python defers." | Python runs the table and gives up; or Python runs nothing | "Python's engine runs phase 1 and defers at 2.1; the record is then Lean's, through `ve_diagnose`, or the deferred record when that is unavailable." |
| "The record is validated." | admitted and valid; or one of the two | "The record is admitted (14) and then valid (15); each is a phase, and the first failing instance names which." |
| "`UnitPrecision` gets one encoding." | the class becomes a fine code everywhere; or Rust's risk evaluator adopts the encoding the other sites have | "`risk.rs` prints `InvalidInput` with `UnitPrecision(<tag>, scale=<n>)`, as Python, Lean and `units.rs` do. The fine code is row 12's." |
| "The route's text is the contract's." | always; or on a one-fault source and outside classifier sets | "On a source with one fault outside a classifier set, the record's text is the route's text, by construction of the table; inside a set, and on multi-fault sources, tiers 0 and A test it." |
| "Rejections of alternatives cases carry the record." | every kind and the admission path; or `alt-elaborate` after Python's `Environment` | "An error row of `run_case` on an `alt-elaborate` case whose environment Python's `Environment` accepted carries the record. `Environment`'s own rejection, and every other kind, report as before." |
| "The delta report is complete." | no other message can change; or none on the corpus | "Every message change on the unit's corpus is in the report." |
| "A class names the kind of fault." | the record's class is chosen by the contract; or it is the class the public already sees | "The record's `class` is the class `checker_error` gives the route's text today; the contract declares it per code and the gate checks it on every rejected case." |

### 3.4 The release notes

The `release_note` of each signing file is this text, with the unit's name and the list filled from `signed`.
For `alternatives@0`:

> When the alternatives route in `ve` rejects an `alt-elaborate` case, the row it returns now has one more
> member, `diagnostic`: the row carries the contract's record. When a check of the table fails, the record
> names the first one that fails and the row's `error` is that check's text; otherwise the `error` is the
> route's. The table is `docs/spec/alternatives-wire-table.md`; "first" is its order from top to bottom. With
> the check, the record gives the place in the input and a code. The texts of the table are the route's, so
> for a case with one fault the `error` is the same as before. It is a different `error` for these checks.
> ⟨for each signed check, in table order: its id, a colon, a space, and its sentence from `signed`, the
> entries separated by a space⟩ Whether a case is accepted or rejected has not changed, and the row's
> `status` and `id` are as before. A rejection that Python's environment decoder raises before the route
> runs, a rejection of any other kind of case, and document admission report as before.

For `risk@0`, the same with "the risk route", "a `risk-elaborate` or `risk-decision` case", the table
`docs/spec/risk-wire-table.md`, and the last sentence "A rejection of any other kind of case, and document
admission, report as before."

For item 2: "Rust's risk evaluator now reports an off-grid decimal literal as `InvalidInput` with the
message `UnitPrecision(<tag>, scale=<n>)`, as Python, Lean and Rust's unit decoder do; it reported the code
`UnitPrecision` with the message `<tag>, scale`. The literal is rejected as before."

### 3.5 The paragraphs added to the two specs

To alternatives.md, section 6, after the order sentence:

> **The public record.** When the alternatives route rejects an `alt-elaborate` case, the row carries the
> contract's record, in its member `diagnostic`. The contract is the wire contract `alternatives@0`
> ([alternatives-wire-table.md](alternatives-wire-table.md); [wire-contract.md](wire-contract.md) 2.7). When
> a check of the table fails, the record names the first one that fails and the row's `error` is that
> check's text; otherwise the `error` is the route's. The checks are the route's, in its order, with one code
> each and the texts above; W1's decoders and the typing are inherited checks whose text is the decoder's.
> The contract chooses the message only: the route decides, as before, whether the case is rejected.

To risk.md, section 6, after the order sentence: the same with "the risk route", "a `risk-elaborate` or
`risk-decision` case", `risk@0` and `risk-wire-table.md`, and the sentence "The record's admission and
validation are two sets of checks whose order inside the set is the route's."

## 4. Diagnostics

### 4.1 The public rows

For the source of fixture A52 (base A with unit 0 named `Law`), the row `run_case` returns is:

```json
{"id": "x", "status": "error", "error": "InvalidInput: invalid rule name 'Law'",
 "diagnostic": {"contract": "alternatives@0", "revision": R, "check": "8.1", "phase": "rules",
                "code": "ALT_INVALID_NAME", "class": "InvalidInput", "path": "/norms/0/norm/name",
                "text": "InvalidInput: invalid rule name 'Law'", "args": {"value": "Law"}}}
```

Today it is `{"id": "x", "status": "error", "error": "InvalidInput: invalid rule name 'Law'"}`: the `error`
is the same words. For the source of fixture K7 (a record whose estimate `E` has `lo` `5` and `hi` `3`):

```json
{"id": "x", "status": "error", "error": "RiskRange: E",
 "diagnostic": {"contract": "risk@0", "revision": R, "check": "15.1.16", "phase": "validation",
                "code": "RISK_RANGE", "class": "InvalidInput", "path": "/decision",
                "text": "RiskRange: E", "args": {"id": "E"}}}
```

For a source on which the Python engine fails in phase 1 (fixture A2, profiles without `alternatives@0`) the
record is Python's own, with no Lean process; such a case never reaches the switched branch through
`run_case`, whose `Environment` rejects it first (2.9), so it is public only through `public_rejection`
itself. With a residual record or a deferred record, `error` is the route's text and `diagnostic` is the
record of base spec 4.1. With no record, the row is today's.

### 4.2 Field by field

| Member of the row | After the switch, at the call site of 2.8 |
|---|---|
| `id`, `status` | the route's; never written |
| `error` | the reported record's `text` when it is a fault record; otherwise the route's text |
| `diagnostic` | the reported record; before the switch absent |
| every other member | the route's (an error row has none) |

A consumer that validates the row against a closed shape must admit `diagnostic`; the switch commits list
every such schema and stored expectation they had to change, among them the byte-equality test of 2.9 and
`run_alternatives_case`'s own shape check (`ve/backends/lean.py:185–190`), which reads the row before the
switch and is not changed.

### 4.3 Lean

- Every row of `ve_alternatives_route` and of `ve_risk_route` is byte-identical to its row before each
  switch, on every corpus case.
- `ve_diagnose alternatives@0` and `ve_diagnose risk@0` print the records of 2.3 and 2.4; after a switch, the
  same rows with the new `revision`.
- `ve_diagnose risk@0` on a case without a `decision` prints a record of phases 1 to 13 or `clean`; the
  guard of 5.3 keeps phases 14 and 15 out of its instances.

### 4.4 Tool diagnostics

`tools/wire_contract.py` gains no lint code. A hook, classifier or view the Python registry does not name is
still `WC08`; a name registered as `None` is registered. The gate prints the S5 spec's lines (its 4.4) with
the unit named, and these in addition:

| Line | Printed when |
|---|---|
| `gate reports: <unit>: python deferred on <n> of <m> rejected cases; consultations <n>, unavailable <k>` | informative; Python's deferred share and the consultation counts |
| `gate fails: <unit>: boundary: <n> rows with status or id written` | V1 fails |
| `gate fails: <unit>: lean engine differs from the route on <n> cases` | the Lean engine reports clean on a rejected case or a fault on an accepted one (C2) |

## 5. Lean: the statements, and the Lean modules

**Namespace.** The modules live in `lean/VE/WireContract/` and the namespace is `VE.WireContract`, as built
(base spec section 5, "Namespace as built").

### 5.1 Relied on, as built (`lean/VE/WireContract/Engine.lean:453–534`)

```lean
namespace VE.WireContract
open Lean

theorem run_clean_iff (t : Table) (h : Hooks) (j : Json) :
    run t h j = none ↔ ∀ i ∈ instances t h j, eval h i = none

theorem run_fault_first (t : Table) (h : Hooks) (j : Json) (d : Finding) :
    run t h j = some d ↔
      ∃ pre i post, instances t h j = pre ++ i :: post ∧ eval h i = some d ∧
        ∀ b ∈ pre, eval h b = none

theorem run_phase_major (t : Table) (ps qs : List Phase) (h : Hooks) (j : Json)
    (ht : t.phases = ps ++ qs) :
    run t h j = (run { t with phases := ps } h j).or (run { t with phases := qs } h j)

theorem run_congr_reached (t : Table) (h g : Hooks) (j : Json)
    (hv : ∀ name v, h.view name v = g.view name v)
    (hr : ∀ pre i post, instances t h j = pre ++ i :: post →
            (∀ b ∈ pre, eval h b = none) → eval h i = eval g i) :
    run t h j = run t g j

end VE.WireContract
```

Item 1 changes none of them and does not touch `lean/axioms.txt` or `tools/check_lean_imports.py`. No
theorem relates either contract to a decoder (base plan 3.2); none is added. `run_congr_reached` is what
makes the consultation sound as a diagnostic: the Lean engine's hooks and Python's deferred registry agree on
every instance Python evaluates (phase 1 has no hook), so Python's fault, when it has one, is Lean's.

### 5.2 Two optional statements

Phases 14 and 15 of `risk@0` carry the guard "`/decision` is absent or is not `null`" on every entry. That a
root without a decision reaches no instance of those phases follows from two facts about the engine that are
immediate from the equations of `expand` (`Engine.lean:196–219`) and are stated here so that the audit
lists them if the builder adds them; they are optional, as the engine lemmas were (base plan C4), and if
added their `#print axioms` lines are the append-only `VE/Audit.lean` diff of edit c, recorded.

```lean
namespace VE.WireContract
open Lean

/-- A check whose guard does not hold contributes no instance. -/
theorem expand_check_guard_false (h : Hooks) (phase : String) (root : Json)
    (items earlier : List Pointer) (frame : Frame) (c : Check)
    (hg : guardHolds root items c.guard = false) :
    expand h phase root items earlier frame (.check c) = []

/-- A group whose guard does not hold contributes no instance. -/
theorem expand_each_guard_false (h : Hooks) (phase : String) (root : Json)
    (items earlier : List Pointer) (frame : Frame) (id : String) (over : Pattern)
    (guard : List Lit) (entries : List Entry)
    (hg : guardHolds root items guard = false) :
    expand h phase root items earlier frame (.each id over guard entries) = []

end VE.WireContract
```

Both are stated in the stub (status paragraph) with `sorry`, to be proved by unfolding `expand` and
rewriting with `hg`; no proof is committed with `sorry`. They say nothing about a table: that every entry of
phases 14 and 15 carries the guard is a property of the generated table, checked by a test that reads the
contract (T6).

### 5.3 The hooks modules, the adapters and the registry

`lean/VE/WireContract/Hooks/Alternatives.lean` and `Hooks/Risk.lean`, hand-written, in the shape of
`Hooks/SoftNorms.lean`: `predicate`, `classifier`, `view` (the identity), `hooks`, `adapter` and
`registered`, and a `#guard` that every hook, classifier and view name occurring in the unit's generated
table is one it registers (`Hooks/SoftNorms.lean:213–219`). `Hooks/Risk.lean` imports `Hooks/Alternatives.lean`
and reuses its functions for the names the two tables share. Both import the frozen modules they call
read-only (`VE.Alternatives.Wire`, `VE.Alternatives.Decl`, `VE.Risk.Wire`, `VE.Risk.Decl`, `VE.Risk.Record`,
`VE.Risk.Report`, `VE.Risk.Run` for `withCase`, `VE.Norms.Wire`, `VE.Norms.Tree`, `VE.Route.Gate`,
`VE.Time.Wire`, `VE.Route`); none of those is edited. The adapters build the roots of 2.2; `risk_source` gives
`decision` and `entries` the value `.null` on a case that lacks them, so the guard of phases 14 and 15 is
false on it (`Json.getObjValD` gives `.null`, and `Lit.notType` with `Atom.null` is false on `.null`,
`Engine.lean:143–181`).

**The unit registry: the C4 exception again.** `ve_diagnose` finds a unit in `units`
(`lean/VE/WireContract/Diagnose.lean:32–38`), a hash-listed module. Item 1 adds two `import` lines and two
entries, no existing line changing, as S5 adds its two (S5 spec 5.3); the inventory line's rehash goes with
it, and the diff is reviewed.

### 5.4 Manifest, inventory, layers, imports

- **Inventory.** `Hooks/Alternatives.lean`, `Hooks/Risk.lean`, `Tables/Alternatives.lean` and `Tables/Risk.lean`
  are added. `Limits.lean` and `Names.lean` are regenerated (new entries), and so is every earlier table
  whose header names their hashes (base spec 7.1); those are generated rehashes. `Diagnose.lean` is the
  exception of 5.3. `VE/Audit.lean` only if the statements of 5.2 are added.
- **Assurance manifest.** The `wire.diagnose` operation gains two bindings: `alternatives@0` with the kinds
  `alt-elaborate`, `alt-validate`, `alt-conflict`, `alt-followable`, `alt-certificate`, and `risk@0` with
  `risk-elaborate`, `risk-decision`, `risk-conflict`, `risk-followable`, `risk-audit`, `risk-certificate`,
  each with the response `{"outcome": "string"}` and the dispatch `Diagnose.lean` plus its hooks module; and
  two `lean_call_sites`, `ve.alternatives_contract:lean_outcome` and `ve.risk_contract:lean_outcome`, the
  first call sites the operation has. Its `reason` stays "diagnostic only; no verdict or identity depends on
  it", and the note that a missing executable is a deferred diagnostic. The two hooks modules are classified
  under `other_json` as "diagnostic only: no verdict depends on it". The pinned decoder total does not grow.
- **Layers.** `ve.alternatives_contract` is Python layer 2 beside `ve.alternatives`, and `ve.risk_contract`
  layer 4 beside `ve.risk` (`tools/layer_policy.py:20, 26`).
- **Imports.** The Lean rule of base spec 7.3 is unchanged. The Python rule is the table of 2.8.

## 6. The expected delta of each unit

"Only diagnostics may become uniform, listed per profile": these are the lists, from reading the routes.
None was run for this draft; the measured lists of 2.11 replace them, and the signatures are given on the
measured lists.

**`alternatives@0`.** The public row's `error` at the call site of 2.8:

| Check | Today | After the switch | Read from |
|---|---|---|---|
| every check, on a source with one fault outside a classifier set | the route's text | the same | 2.13 (E): the table takes every text from the route |
| a member of 6.1, 6.2 or 7.1, on a source with two faults inside one set | the route's first | the member of least order key | the catalogue's keys are the route's order (2.5); a mismatch is a tier A failure, not a signed change |
| 2.1, 4.3, 5.2, 7.1a | the decoder's text | the same | inherited |

The expected list is empty. A text change that the measurement finds is a defect of the table or of a hook
and is fixed before the switch, not signed, unless the DRI decides otherwise at step 5.

**`risk@0`.** The same, with 15.1.22 and 15.1.28: today the route's text carries the witness case, and the
classifier takes the route's text through `withCase`, so the case is in `detail` and the text is the same.
Expected list empty.

Classes: none changes at a switch; the record's class is the legacy class by construction (2.12). The
inherited exemptions are counted, not changes.

## 7. S7.0, the measurement commits and the switch commits: files and gates

### 7.1 S7.0: what the tooling must take from the unit

After S5.0 (S5 spec 7.1) every tool takes a unit. S7.0 is one commit, after S5.0 has merged and before any
contract, that adds four generalisations; after it, the pilot's and S5's generated files, stored reports and
gate numbers are byte-identical, and nothing in `ve/` changes except the registry tables of the tooling's own
module.

| S5.0 | After S7.0 |
|---|---|
| the gate's Lean legacy call is the unit's route binary with one case kind | the unit's contract module provides `lean_case(root)`, the case the route validates, and `legacy_validation(root)` (2.2); for `risk@0` the kind depends on the root |
| the gate's Python legacy call raises a `VEError` or returns | `legacy_validation` returns `None` or `(class, text)`; the gate measures the public delta on the row that `public_rejection` returns and compares its `error` and `diagnostic`; it counts the Python engine's deferred outcomes and the consultation's outcomes (2.11) |
| the lint refuses a hook the registry lacks | unchanged: a name registered as `None` is present; the engine defers on it (2.5) |
| the recorder wraps the S5 functions | it also wraps `ve.alternatives.run_case`, `ve.risk.run_case`, both `public_rejection` functions, `ve_alternatives_route`, `ve_risk_route` and `ve_diagnose` with either unit (through `subprocess.run`), recording a root for every `alt-*` and `risk-*` case a test file submits, as 8.8 states |
| the allowed-gap table is read from the unit's statement spec | this file's 8.5 for the two units |

### 7.2 Diff scope, per unit

Item 1 is, per unit, a shadow commit (S7.1a, S7.3a), a measurement commit (S7.1b, S7.3b) and a switch commit
(S7.1d, S7.3d), after S7.0 and, for `alternatives@0`, after the commit of S7-pre where one is needed. Item 2
is one commit (S7.2).

**The shadow commit** of `alternatives@0`: `ve/wire_contract/alternatives@0.json`, `examples/alternatives@0/`
(two examples: base A and A with `norms` `[]`), `limits.json` and `names.json` with their lock entries;
`ve/alternatives_contract.py` (adapter, `legacy_validation`, `lean_case`, `lean_outcome`, `REGISTRY`; no
`public_rejection` yet); `lean/VE/WireContract/Hooks/Alternatives.lean`, the generated `Tables/Alternatives.lean`,
`Limits.lean`, `Names.lean` and every regenerated earlier table, with their inventory lines; `Diagnose.lean`
(5.3); `docs/spec/alternatives-wire-table.md`; `conformance/wire_contract_faults_alternatives.py` and the
stored reports of the unit (gate, golden, catalogue); the manifest's `wire.diagnose` binding for the unit
(without its call site); `tools/layer_policy.py`; tests. The shadow commit of `risk@0` is the same list for
its unit, with the two examples base R and R with `norms` `[]`.

**The measurement commit** of a unit: the stored gate and delta reports regenerated over the whole corpus
with `public_diagnostic_changes` and `consultations`; the gate enforces S7-pre and the class rule from here;
tests (the fixtures G3, G6 and G8 of the unit). No file of `ve/` or `lean/` changes.

**The switch commit** of a unit: the contract and the lock (2.10); its generated table and inventory line;
the contract module gains `public_rejection`; the one call site (2.8); the manifest's call site for the unit;
the gate's tier P and the rows of section 9 enforced at `public`; the stored reports at revision `R`, the
new `<unit>-switch.json`, and `<unit>-test-inputs.json` for the sources of 8.8; tests; the import-scan test;
the paragraph of 3.5 in the unit's spec; this file's response section.

**Item 2's commit:** `rust/ve-core/src/risk.rs` (one line), `tests/test_risk_differential.py`, the release
note.

Not changed by any commit of item 1, and checked by the diff-scope test of C1: `ve/environment.py`,
`ve/risk.py` outside the one branch of `run_case`, `ve/alternatives.py` outside the one branch, `ve/errors.py`,
`ve/wire.py`, `ve/backends/diagnostics.py`, `ve/backends/lean.py`, `ve/admission.py`, `ve/wire_contract/engine.py`,
`contract.schema.json`, every earlier contract and its examples, every Lean module other than the generated
tables, the two hooks modules and `Diagnose.lean` (and `VE/Audit.lean` only for 5.2), `lean/axioms.txt`,
`tools/check_lean_imports.py`, `Main.lean`, every Rust file, `conformance/identity.json`, the frozen baseline.

### 7.3 The gates

The four conservativity gates of base plan 5.2, as the debate amended them, for every commit of item 1:

- **C1.** The diff is within 7.2. `VEError.to_dict()` is not edited; no `VEError` gains a `diagnostic` from
  these units, the row does.
- **C2.** Legacy verdicts equal their snapshot. The Lean engine reports `clean` on every accepted corpus case
  of its unit and a fault on every rejected one; the Python engine reports a fault only on rejected cases,
  and its deferred count is reported; Rust is not run.
- **C3.** Public diagnostics change only as the signed delta of the unit lists; the gate fails otherwise.
  S7.0 and the shadow and measurement commits change no public diagnostic.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass. The inventory diff is the
  additions and generated rehashes of 5.4 and the append-only `Diagnose.lean` diff of 5.3, and nothing else;
  `VE/Audit.lean` only for the statements of 5.2, append-only.

The corpus-completeness test is kept, with its three tests per unit (8.8). The difffuzz condition of the
pointer is vacuous while `infra/difffuzz` is unmerged (plan section 0, item 8).

## 8. Acceptance fixtures for item 1 and item 2

Deterministic, with expectations written by hand from section 2 and base spec sections 2 and 8. Each reviewer
derives the expectation of every fixture before reading the column "Expected". A fixture of 8.1 to 8.3 is
green when `ve_diagnose` returns the expected outcome, as a record compared by base spec 2.7, and the Python
engine returns the same record where the fault is in phase 1 and `Deferred("2.1")` otherwise; an inherited
record's `text` and `args` are Lean's own. Every number marked **derived** was computed from the Lean
definitions by hand (the derivation is given) and has an `#eval` in the stub that confirms it; the build
runs the stub before it writes the fixture, and corrects the fixture to the evaluated value.

**The base A** (`alternatives@0`): the environment of `conformance.alternatives.environment()` (profiles
`["alternatives@0", "norms@0", "relational-fol@0"]`, no constants, the block with `performed` and one
`avoids` fulfilment on `prevent_required`) and the six norm objects `rules()["1"]`, `["2"]`, `["3full"]`,
`["4"]`, `["5"]`, `["6"]`, in this order: `law-3-permission`, `law-2-permission` (over the first),
`law-1-direct` (over the second), `law-0-direct` (over the third), `law-2-obey`, `law-3-preserve`; `units`
absent. It is the rule set `asimov` of `lean/VE/Alternatives/Examples.lean:64` in wire form. "Unit *i*" is
`/norms/i`. The **atom P** is `["exists", "harm", ["binary", "allows", ["var", 1], ["var", 0]]]` in a rule
on `permitted` (4 nodes raw; 19 after inlining, since `allowsF` has 18 nodes: **derived** by `formulaNodes`
on `Decl.lean:85–88`, `#eval` in the stub). A **balanced conjunction** of *n* formulas is as the S5 spec
defines it, with 3*n* − 1 nodes over *n* atoms of 3 nodes, and over *n* copies of P: 5*n* − 1 raw and
20*n* − 1 inlined (**derived**).

**The base R** (`risk@0`): `conformance.risk.agent_ops()` with the document `{"norms":
agent_ops_rules()}` (the policy `ops` of `tests/test_risk_every_diagnostic.py`, three rules), no
`decision`. **The base C** (records): `conformance.risk.cell_env()` with `{"norms": []}`, the records built
by that test's `cell(...)` helper (chooser `the_agent`, alternatives `act` and `nothing`), each cited entry
through its `Log`, which computes every hash. The **atom Q** is `["binary", "risk__less_worst", ["var", 0],
["var", 0]]` in a rule on `permitted` (3 nodes raw; 23 after risk inlining, since `lessWorstF` has 23
nodes: **derived** from `Decl.lean:108–112`, `#eval` in the stub); over *n* copies a balanced conjunction has
4*n* − 1 raw and 24*n* − 1 inlined nodes.

### 8.1 The engine on `alternatives@0`

| Case | Change to A | Expected `check`, `path`, `text` |
|---|---|---|
| A1 | none; and the second example | clean; the route accepts |
| A2 | `profiles` `["norms@0", "relational-fol@0"]` | 1.5, `/environment/profiles`, `UnsupportedProfile: alternatives@0 is required`; the Python engine gives the same record |
| A3 | `profiles` gain `soft-norms@0` (sorted) | 1.7, `/environment/profiles`, `UnsupportedProfile: alternatives@0 with soft-norms@0` |
| A4 | `profiles` `["norms@0", "alternatives@0", "relational-fol@0"]` | 1.4, `/environment/profiles`, `UnsupportedProfile: profiles must be sorted and unique` |
| A5 | the member `alternatives` removed | 1.8, `/environment`, `InvalidInput: alternatives.block` |
| A6 | the environment gains a member `extra` with the value `1` | 2.1, `/environment`, class `InvalidInput`; text Lean's own (`fields do not match: …`) |
| A7 | predicate `ordered` gains `"defined": {"arguments": ["action"], "body": ["top"]}` | 2.2, `/environment/vocabulary/predicates`, `UnsupportedProfile: alternatives route with definitions is not implemented` |
| A8 | `profiles` gain `data@0` (sorted) and predicate `ordered` gains `"functional": true` | 2.3, the same path, `… with data flags is not implemented` |
| A9 | `alternatives` is `[]` | 3.1, `/environment/alternatives`, `InvalidInput: alternatives.block` |
| A10 | the block's `chooser` removed | 3.2c, `/environment/alternatives`, `InvalidInput: alternatives.chooser` |
| A11 | the block's `harm` and `action` removed | 3.2a, `/environment/alternatives`, `InvalidInput: alternatives.action` (the route's order of the mandatory fields) |
| A12 | the block gains `zeta` and `beta`, both `1` | 3.3, `/environment/alternatives/beta`, `InvalidInput: alternatives.beta` (code point order of the keys) |
| A13 | `chooser` is `5` | 3.4a, `/environment/alternatives/chooser`, `InvalidInput: alternatives.chooser` |
| A14 | `outcomes` is `7` | 3.5a, `/environment/alternatives/outcomes`, `InvalidInput: alternatives.outcomes` |
| A15 | `outcomes` is `"open"` | 3.5b, the same path and text |
| A16 | `outcomes` is `{}` | 3.5c, the same path, `MissingOutcomeDecider: alternatives.outcomes` |
| A17 | `outcomes` is `{"complete_by": "x", "extra": 1}` | 3.5d, the same path, `InvalidInput: alternatives.outcomes` |
| A18 | `outcomes` is `{"complete_by": 1}` | 3.5e, `/environment/alternatives/outcomes/complete_by`, `MissingOutcomeDecider: alternatives.outcomes` |
| A19 | `outcomes` is `{"complete_by": " \t"}`; separately `{"complete_by": "x"}` | 3.5f, the same path and text; clean for the second (the two directions of 3.5f) |
| A20 | `decided_by` is `5` | 3.6a, `/environment/alternatives/decided_by`, `InvalidInput: alternatives.decided_by` |
| A21 | `decided_by` is 65 letters `x`; separately 64 letters `x`; separately 33 letters `é` (66 bytes) | 3.6b with `count` `65`, `limit` `64`; clean; 3.6b with `count` `66` (bytes, not characters) |
| A22 | `performed` is `{"permission": "permitted"}` | 3.7a, `/environment/alternatives/performed`, `InvalidInput: alternatives.performed` |
| A23 | `performed` is `{"permission": 1, "obligation": "required"}` | 3.7b, `/environment/alternatives/performed/permission`, the same text |
| A24 | `inaction` is `3` | 3.8a, `/environment/alternatives/inaction`, `InvalidInput: alternatives.inaction` |
| A25 | `fulfilments` is `{}` | 3.9a, `/environment/alternatives/fulfilments`, `InvalidInput: alternatives.fulfilments` |
| A26 | 17 copies of the fulfilment; separately 16 copies | 3.9b, `/environment/alternatives/fulfilments`, `ResourceLimit: fulfilments`, `count` `17`, `limit` `16` (the limit is checked before the items); 3.9e at `…/fulfilments/1/obligation` for 16 (the two directions of 3.9b) |
| A27 | the fulfilment is `{"obligation": "prevent_required"}` | 3.9c, `…/fulfilments/0`, `InvalidInput: alternatives.fulfilments` |
| A28 | the fulfilment's `obligation` is `5` | 3.9d, `…/fulfilments/0/obligation`, the same text |
| A29 | two fulfilments on `prevent_required`, the second with body `["top"]` | 3.9e, `…/fulfilments/1/obligation`, `DuplicateDeclaration: fulfilment prevent_required` |
| A30 | the fulfilment's `body` is `7` | 3.9f, `…/fulfilments/0/body`, `InvalidInput: alternatives.fulfilments` |
| A31 | the fulfilment's `body` is `"excludes"` | 3.9g, the same path and text (on `risk@0` the same body holds, 8.2 R24: the two directions of 3.9g across the units) |
| A32 | the fulfilment's `body` is `["unary"]` | 3.9h, the same path and text |
| A33 | `norms` is `{}` | 4.1, `/norms`, `InvalidInput: norms must be an array` |
| A34 | 257 units: A's six and 251 copies of unit 0 | 4.2, `/norms`, `ResourceLimit: rules`, `count` `257`, `limit` `256` |
| A35 | unit 2's `norm` lacks `over` | 4.3, `/norms/2`, class `InvalidInput`; text Lean's own |
| A36 | unit 0's `guard` is `5` | 4.3, `/norms/0`, class `InvalidInput`; text Lean's own |
| A37 | `units` is `{}` | 5.1, `/units`, `InvalidInput: premises must be an array` |
| A38 | `units` is `[{"label": "u"}]` | 5.2, `/units/0`, class `InvalidInput`; text Lean's own |
| A39 | `units` is `[{"label": "u", "ast": ["forall", "action", ["unary", "zzz", ["var", 0]]]}]` | 6.4, `/units/0`, `InvalidInput: ill-typed premise u` |
| A40 | `chooser` is `"zz"` | 6.1.1, `/environment/alternatives`, `UnknownSymbol: alternatives.chooser zz` |
| A41 | `action` is `"robot"` | 6.1.4, `/environment/alternatives`, `AlternativesSort: sorts must be distinct` |
| A42 | a predicate `allows` with arguments `["action", "harm"]` added | 6.1.5, `/environment/alternatives`, `AlternativesReserved: allows` |
| A43 | `available` is `"nope"` | 6.1.6, `/environment/alternatives`, `UnknownSymbol: alternatives.available nope` |
| A44 | `available` is `"permitted"` | 6.1.7, `/environment/alternatives`, `AlternativesRegulated: available permitted` |
| A45 | `leads_to` is `"available"` | 6.1.11, `/environment/alternatives`, `AlternativesSort: leads_to expects (action, harm)` |
| A46 | `performed` is `{"permission": "required", "obligation": "permitted"}` | 6.1.21, `/environment/alternatives`, `AlternativesPerformed: required, permitted` |
| A47 | `leads_to`'s verbalisation is `{0} risks {1}` | 6.2.2, `/environment/vocabulary/predicates`, `AlternativesVerbalisation: leads_to must read "{0} leads to {1}"` |
| A48 | a predicate `alias` with arguments `["action", "harm"]` and the verbalisation `{0} leads to {1}` added | 6.2.7, the same path, `AlternativesVerbalisation: leads_to must be declared for "{0} leads to {1}"` |
| A49 | the fulfilment's `obligation` is `"required"` | 6.3, `…/fulfilments/0`, `FulfilmentSort: required` |
| A50 | unit 0's `guard` is `["unary", "nope", ["var", 0]]` | 7.1a, `/norms/0`, class `InvalidInput`; text Lean's own (`UnknownSymbol: Unknown predicate 'nope'`) |
| A51 | unit 0's `guard` is a balanced conjunction of 501 atoms P; separately of 500 | 7.1b, `/norms/0`, `ResourceLimit: alternatives inlining of rule law-3-permission` (**derived**: 20 · 501 − 1 = 10,019 > 10,000; raw 2,504 nodes within the unit decoder's budget); clean for 500 (9,999) |
| A52 | unit 0's `name` is `"Law"` | 8.1, `/norms/0/norm/name`, `InvalidInput: invalid rule name 'Law'` |
| A53 | unit 1's `name` is `"law-3-permission"` | 8.2, `/norms/1/norm/name`, `DuplicateDeclaration: rule law-3-permission` |
| A54 | unit 0's `predicate` is `"ordered"` | 8.3, `/norms/0/norm/predicate`, `UnknownSymbol: regulated predicate ordered` (7.1 skips a rule whose predicate is not regulated) |
| A55 | unit 0's `unless` has nine copies of `["top"]` | 8.4, `/norms/0/norm/unless`, `InvalidInput: invalid sign or too many carve-outs`, `count` `9`, `limit` `8` |
| A56 | units 0 and 1 each have as `guard` a balanced conjunction of 300 atoms P; separately unit 0 alone | 8.5, `/norms/1`, `ResourceLimit: AST exceeds 10,000 nodes` (**derived**: each inlined guard has 5,999 nodes, within 7.1b; the two together 11,998); clean for one |
| A57 | unit 1's `over` is `["nope"]` | 9.1, `/norms/1/norm/over/0`, `UnknownRule: rule nope` |
| A58 | unit 4's `over` is `["law-3-permission"]` | 9.2, `/norms/4/norm/over/0`, `PrecedenceAcrossPredicates: rule law-2-obey on required, rule law-3-permission on permitted` |
| A59 | unit 0's `over` is `["law-2-permission"]` | 10.1, `/norms`, `DependencyCycle: law-2-permission, law-3-permission` (the route sorts the names) |
| A60 | seventeen rules `r0` to `r16` on `permitted`, guard `["top"]`, each after the first `over` the one before it, replacing A's rules | 10.2, `/norms`, `ResourceLimit: precedence depth` |
| A61 | unit 0's `guard` is `["unary", "permitted", ["var", 0]]` | 10.3, `/norms`, `DependencyCycle: permitted` |
| A62 | a fulfilment `{"obligation": "required", "body": ["top"]}` replaces A's | 11.1, `…/fulfilments/0`, `FulfilmentOnPerformed: required` |
| A63 | a fulfilment `{"obligation": "ordered", "body": ["top"]}` replaces A's | 11.2, `…/fulfilments/0`, `FulfilmentSort: ordered` |
| A64 | the fulfilment's `body` is `["unary", "harms_human", ["var", 5]]` | 11.3, `…/fulfilments/0`, `FulfilmentNotBase: prevent_required` |
| A65 | A5 with A33 | 1.8, `/environment` (phase 1 before phase 4) |
| A66 | A12 with A13 | 3.3, `/environment/alternatives/beta` (the keys group before 3.4a) |
| A67 | A53 with A57 | 8.2, `/norms/1/norm/name` (phase 8 before phase 9) |
| A68 | A49 with A62 (two fulfilments) | 6.3, `…/fulfilments/0` (phase 6 before phase 11) |
| A69 | A28 at index 0 and A29's duplicate at index 1 (three fulfilments) | 3.9d, `…/fulfilments/0/obligation` (item-major inside `fulfilments`) |
| A70 | A43 with A41 | 6.1.4, `/environment/alternatives` (the order inside the set: the sorts before the role predicates; test-enforced) |

For every case from A2 to A70, the route rejects, and the record's `class` equals the legacy class of the
route's text (2.1), except on the inherited cases A6, A35, A36, A38 and A50 (2.12). The catalogue of
`alternatives@0` holds a fault for each case, with the order keys of 2.5 for A70 and for 7.1.

### 8.2 The engine on `risk@0`, the source

| Case | Change to R | Expected `check`, `path`, `text` |
|---|---|---|
| R1 | none; and the second example | clean; the route accepts |
| R2 | `units` removed | 1.1a, `/environment`, `UnsupportedProfile: unit_schema and units require the ve.core@0.2 quantity route together`; the Python engine gives the same record |
| R3 | `unit_schema` removed | 1.1b, `/environment`, the same text |
| R4 | `profiles` `["alternatives@0", "norms@0", "relational-fol@0"]` | 1.4, `/environment/profiles`, `UnsupportedProfile: risk@0 is required` |
| R5 | `profiles` `["norms@0", "relational-fol@0", "risk@0"]` | 1.5, `/environment/profiles`, `UnsupportedProfile: risk@0 requires alternatives@0` |
| R6 | the member `risk` removed | 1.9, `/environment`, `InvalidInput: risk.block` |
| R7 | the environment gains a member `extra` with the value `1` | 2.1, `/environment`, class `InvalidInput`; text Lean's own |
| R8 | `profiles` gain `closure@0` (sorted) | 2.2, `/environment/profiles`, `UnsupportedProfile: the risk norms route admits FOL documents only` |
| R9 | `profiles` gain `documents@1` (sorted; five members) | 2.4, `/environment/profiles`, `UnsupportedProfile: ve-units@1 requires exactly order@0, relational-fol@0 and time@0, optionally with documents@1`, `count` `5`, `limit` `4` |
| R10 | R9 with `unit_schema` and `units` removed | clean up to 2.4; the route rejects later (`documents@1` on this route) and the record is that later check's: 2.4 is guarded out (the two directions of 2.4's guard) |
| R11 | `unit_schema` is `"ve-units@2"` | 2.5, `/environment/unit_schema`, `UnsupportedProfile: Unsupported unit schema` |
| R12 | `units` is `[]` | 2.6, `/environment/units`, `units must be an object` |
| R13 | 65 unit tags `t00` to `t64`, each `{"scale": "1", "display": {"kind": "decimal", "label": "T"}}`, replacing `gb` | 2.7, `/environment/units`, `ResourceLimit: At most 64 unit tags`, `count` `65`, `limit` `64` |
| R14 | the unit `gb` has `scale` `"3"` | 2.8, `/environment/units/gb`, class `InvalidInput`; text Lean's own (`UnitScale(gb): expected a positive power of ten`) |
| R15 | a second unit `tb` with the display label `GB` | 2.9, `/environment/units`, class `InvalidInput`; text Lean's own (`DisplayCollision(…)`) |
| R16 | predicate `confirmed` gains `"argument_units": {"0": "gb"}` | 2.10, `/environment/vocabulary/predicates/confirmed`, class `InvalidInput`; text Lean's own (`Unit on non-integer slot 0`) |
| R17 | constant `data_loss` gains `"verbalisation": ""` | 2.11, `/environment/vocabulary/constants/data_loss`, class `InvalidInput`; text Lean's own |
| R18 | constant `data_loss` gains `"unit": "gb"` | 2.12, the same path, class `InvalidInput`; text Lean's own (`Unit on non-integer constant data_loss`) |
| R19 | predicate `confirmed`'s `arguments` is `["nope"]` | 2.13, `/environment`, class `InvalidInput`; text Lean's own |
| R20 | a sort `gb` added | 2.14, `/environment/vocabulary`, class `InvalidInput`; text Lean's own (`Unit tag gb collides with a declared sort`) |
| R21 | predicate `confirmed` gains `"defined": {"arguments": ["action"], "body": ["top"]}` | 2.15, `/environment/vocabulary/predicates`, `UnsupportedProfile: risk route with definitions is not implemented` |
| R22 | a constant `s` of sort `$string` added | 2.17, `/environment/vocabulary/constants`, `UnsupportedProfile: risk route with $string literals is not implemented` |
| R23 | the block's `outcomes` is `"open"` | 3.5b, `/environment/alternatives/outcomes`, `InvalidInput: alternatives.outcomes` |
| R24 | the block gains `"fulfilments": [{"obligation": "required", "body": "excludes"}]` | 6.4, `…/fulfilments/0`, `FulfilmentSort: required` (3.9g holds on `excludes`; the two directions with A31) |
| R25 | `risk` is `[]` | 4.1, `/environment/risk`, `InvalidInput: risk.block` |
| R26 | the risk block gains `bands` `[]` | 4.2a, `/environment/risk/bands`, `InvalidInput: risk.bands (stage B or C not enabled)` |
| R27 | the risk block gains `zeta` `1` | 4.2b, `/environment/risk/zeta`, `InvalidInput: risk.zeta` |
| R28 | `unexamined` removed | 4.3c, `/environment/risk`, `InvalidInput: risk.unexamined` |
| R29 | `severity` gains `colour` `"red"` | 4.4a, `/environment/risk/severity`, `InvalidInput: risk.severity` |
| R30 | `severity/sort` is `"Severity"` | 4.4d, `/environment/risk/severity/sort`, the same text |
| R31 | `classes` is `["severe", "serious", "Minor"]` | 4.4e, `/environment/risk/severity/classes/2`, the same text |
| R32 | `more_severe` is `[["severe", "serious", "minor"]]` | 4.4g, `/environment/risk/severity/more_severe/0`, the same text |
| R33 | `decided_by` is `""`; separately 65 letters `x`; separately `"chooser"` | 4.4j, `/environment/risk/severity/decided_by`, the same text; the same; clean up to 4.4j |
| R34 | `harm_classes` is `[["data_loss"]]` | 4.5b, `/environment/risk/harm_classes/0`, `InvalidInput: risk.harm_classes` |
| R35 | `unexamined` is `"impossible"` | 4.6b, `/environment/risk/unexamined`, `InvalidInput: risk.unexamined` |
| R36 | `unexamined` is `{"ruled_out_by": ""}` | 4.6d, `/environment/risk/unexamined/ruled_out_by`, the same text |
| R37 | `combination` is `"max"` | 4.8, `/environment/risk/combination`, `InvalidInput: risk.combination` |
| R38 | `alternative_kinds` gains `"Run": "running"` | 4.9c, `/environment/risk/alternative_kinds/Run`, `InvalidInput: risk.alternative_kinds` |
| R39 | `alternative_kinds/run` is `""` | 4.9d, `/environment/risk/alternative_kinds/run`, the same text |
| R40 | `required_alternatives` is `[{"when": "run"}]` | 4.10b, `/environment/risk/required_alternatives/0`, `InvalidInput: risk.required_alternatives` |
| R41 | `quantity_kinds/peak_memory` is `1` and `alternative_kinds/Run` is `"running"` | 4.9c (4.9 before 4.11) |
| R42 | `use_all_recorded` is `"yes"` | 4.13, `/environment/risk/use_all_recorded`, `InvalidInput: risk.use_all_recorded` |
| R43 | `document` is `{}` | 5.1b, `/document`, `InvalidInput: norms must be an array` |
| R44 | `document` is `{"norms": [], "units": {}}` | 6.5, `/document/units`, `InvalidInput: premises must be an array` |
| R45 | `severity/sort` is `"harm"` | 7.1.1, `/environment/risk`, `RiskSeverityNotFresh: harm` |
| R46 | `classes` is `["severe", "serious", "minor", "prevents"]` | 6.1.5, `/environment/alternatives`, `AlternativesReserved: prevents` (phase 6 before phase 7; the class is a constant of `E_risk`) |
| R47 | a predicate `risk__extra` with arguments `["action"]` added | 7.1.2, `/environment/risk`, `RiskReserved: risk__extra` |
| R48 | `classes` is `[]`; separately 17 classes; separately 16 | 7.1.3, `/environment/risk`, `ResourceLimit: risk classes`; the same; clean up to 7.1.3 for 16 (**derived**: `s.classes.isEmpty || s.classes.length > 16`) |
| R49 | `classes` is `["severe", "serious", "minor", "serious"]` | 7.1.4, `/environment/risk`, `DuplicateDeclaration: risk class serious` |
| R50 | `more_severe` is `[["severe", "serious"], ["serious", "tiny"]]` | 7.1.5, `/environment/risk`, `UnknownSymbol: risk.severity tiny` |
| R51 | `more_severe` is `[["severe", "serious"], ["serious", "minor"], ["minor", "severe"]]` | 7.1.6, `/environment/risk`, `DependencyCycle: minor, serious, severe` (**derived**: the route lists the unresolved names sorted) |
| R52 | `unranked` is `[["minor", "severe"]]`; separately `more_severe` `[["severe", "serious"], ["severe", "minor"]]` with `unranked` `[["serious", "minor"]]` | 7.1.7, `/environment/risk`, `RiskUnrankedAgainstOrder: minor, severe` (**derived**: the closure of R's edges holds `(severe, minor)`); clean up to 7.1.7 for the second (the two directions of 7.1.7) |
| R53 | `harm_classes` gains `["flood", "minor"]` | 7.1.8, `/environment/risk`, `UnknownSymbol: risk.harm_classes flood` |
| R54 | `harm_classes` gains `["data_loss", "minor"]` at index 1 | 7.1.9, `/environment/risk`, `HarmTwoClasses: data_loss` |
| R55 | the row of `server_outage` removed from `harm_classes` | 7.1.10, `/environment/risk`, `HarmUnclassified: server_outage` |
| R56 | `required_alternatives` is `[{"when": "run", "require": ["ask", "fly"]}]` | 7.1.12, `/environment/risk`, `UnknownSymbol: risk.required_alternatives fly` |
| R57 | the block's `outcomes` is `{"complete_by": "the build agent"}` | 7.1.15, `/environment/risk`, `RiskOutcomes: risk@0 requires outcomes signed` |
| R58 | R45 with R57 | 7.1.1 (the order inside the set; test-enforced) |
| R59 | unit 0's `guard` is `["unary", "nope", ["var", 0]]` | 8.1a, `/document/norms/0`, class `InvalidInput`; text Lean's own |
| R60 | unit 0's `guard` is a balanced conjunction of 417 atoms Q; separately of 416 | 8.1b, `/document/norms/0`, `ResourceLimit: risk inlining of rule rule-1` (**derived**: 24 · 417 − 1 = 10,007 > 10,000); clean for 416 (9,983) |
| R61 | unit 0's `guard` is a balanced conjunction of 501 atoms P | 9.1, `/document/norms/0`, `ResourceLimit: alternatives inlining of rule rule-1` (**derived** as A51; the risk inlining leaves P as it is) |
| R62 | unit 0's `name` is `"Rule"` | 10.1, `/document/norms/0/norm/name`, `InvalidInput: invalid rule name 'Rule'` |
| R63 | unit 0's `over` is `["rule-2"]` and unit 1's `over` is `["rule-1"]` | 12.1, `/document/norms`, `DependencyCycle: rule-1, rule-2` |
| R64 | R26 with R45 | 4.2a (phase 4 before phase 7) |
| R65 | R7 with R25 | 2.1 (phase 2 before phase 4) |

For every case from R2 to R65, the route rejects, and the record's `class` equals the legacy class except on
the inherited cases R7, R14 to R20 and R59. R10 is the one case whose expected first fault lies outside the
rows named: it witnesses that 2.4 is guarded out, and the catalogue records the route's actual first fault
for it.

### 8.3 The engine on `risk@0`, the record

Each case is a `risk-decision` root over C (or the named policy) built as `tests/test_risk_every_diagnostic.py`
builds it, so that every hash is computed by the `Log` helper; "the test's case *name*" is that file's case.
`FIVE` is `["decimal", "dimensionless", "5"]` and `q` is `["quantity", …]`.

| Case | Input | Expected `check`, `path`, `text` |
|---|---|---|
| K1 | a `risk-elaborate` root of R | clean; no instance of phases 14 and 15 (the guard) |
| K2 | the test's `InvalidInput-risk-decision-entry-field` (`seq` `"41"`) | 14.2, `/decision/seq`, `InvalidInput: risk-decision.seq` |
| K3 | the decision entry's `day` is `"2026-13-01"` | 14.3, `/decision/day`, `InvalidInput: risk-decision.day` |
| K4 | the decision entry's `kind` is `"outcome"` | 14.12, `/decision/kind`, `InvalidInput: risk-decision.kind` (14.5 holds: `outcome` is a kind) |
| K5 | the test's `InvalidInput-risk-decision-supplied-entries` (`entries` `{}`) | 14.8, `/entries`, `InvalidInput: risk-decision.entries` |
| K6 | the test's `EstimateProvenance-recorded` (`E1` without `seq` and `day`) | 14.10, `/entries/<i>`, `EstimateProvenance: E1 recorded`, with *i* the index of `E1` among the supplied entries |
| K7 | the test's `RiskRange` (`E` with `lo` `5`, `hi` `3`) | 15.1.16, `/decision`, `RiskRange: E` |
| K8 | the test's `AlteredEntry-decision-entry` (`hash` of 64 `f`) | 14.13, `/decision`, `AlteredEntry: D17` |
| K9 | the test's `InvalidInput-risk-decision-record-field` (`format` `ve-risk-decision@1`) | 14.15, `/decision/content/format`, `InvalidInput: risk-decision.format` |
| K10 | the test's `RiskBinding` | 14.24, `/decision/content/policy`, `RiskBinding: policy` |
| K11 | the test's `ResourceLimit-risk-alternatives` (17 alternatives); separately 16 | 14.25, `/decision/content/alternatives`, `ResourceLimit: risk alternatives`, `count` `17`, `limit` `16`; clean up to 14.25 for 16 |
| K12 | the test's `ResourceLimit-risk-harms` (33 harms) | 14.26, `/environment/risk/harm_classes`, `ResourceLimit: risk harms`, `count` `33`, `limit` `32` |
| K13 | the test's `HindsightEntry` (a citation with `seq` 57 of decision 41) | 14.27, `/decision/content/cites/<i>`, `HindsightEntry: 57` |
| K14 | the test's `MissingEntry` (`E1` not supplied) | 14.28, `/decision/content/cites/<i>`, `MissingEntry: E1` |
| K15 | the test's `AlteredEntry-cited-entry` (`E1`'s `lo` changed after hashing) | 14.29, `/decision/content/cites/<i>`, `AlteredEntry: E1` |
| K16 | the test's `WithdrawnEntry` | 14.30, `/decision/content/cites/<i>`, `WithdrawnEntry: E1` |
| K17 | the test's `InvalidInput-risk-decision-facts` | 14.31, `/decision/content/facts/0`, `InvalidInput: risk-decision.facts` |
| K18 | the test's `ResourceLimit-risk-condition-nodes` (a condition of 4,096 atoms); separately 3,333 atoms | 14.32.6, `/decision/content/cites/<i>`, `ResourceLimit: risk condition nodes` (**derived**: an atom `q < 5` normalises to one coefficient, 2 nodes, so *n* atoms give 3*n* − 1 nodes: 12,287 for 4,096; the smallest failing *n* is 3,334 at 10,001); clean up to 14.32 for 3,333 (9,998) |
| K19 | the test's `ResourceLimit-risk-estimates-and-settings` (65 estimates) | 14.33, `/decision/content/cites`, `ResourceLimit: risk estimates and settings` |
| K20 | the test's `ResourceLimit-risk-conditions-and-statements` (129 statements) | 14.34, `/decision/content/cites`, `ResourceLimit: risk conditions and statements` |
| K21 | the test's `UnknownSymbol-quantity` | 15.1.1, `/decision`, `UnknownSymbol: quantity zz` |
| K22 | the test's `InvalidModel-no-inaction` | 15.1.4, `/decision`, `InvalidModel(alternatives): the_agent has no inaction` |
| K23 | the test's `UnknownHarm` | 15.1.5, `/decision`, `UnknownHarm: flood` |
| K24 | the test's `UnitMismatch` | 15.1.9, `/decision`, `UnitMismatch(dimensionless,gb)` |
| K25 | the test's `RiskConstant-class-name` | 15.1.10, `/decision`, `RiskConstant: severe` |
| K26 | the test's `RequiredAlternativeMissing` | 15.1.12, `/decision`, `RequiredAlternativeMissing: run_limited (with run)` |
| K27 | the test's `UnitPrecision` (`6.5` on `gb` at scale 1) | 15.1.13, `/decision`, `UnitPrecision(gb, scale=1)` |
| K28 | `est("E", "q", "1.", "2")` | 15.1.14, `/decision`, `Invalid decimal literal "1."` |
| K29 | the test's `EstimateProvenance-estimator` | 15.1.17, `/decision`, `EstimateProvenance: E estimator` |
| K30 | the test's `RiskSettingTwice-two-settings` | 15.1.19, `/decision`, `RiskSettingTwice: memory_limit` |
| K31 | the test's `ConflictingEstimates` | 15.1.21, `/decision`, `ConflictingEstimates: free_memory` |
| K32 | the test's `RiskInconsistent-estimates-do-not-intersect` | 15.1.22, `/decision`, `RiskInconsistent: q estimates do not intersect` |
| K33 | the test's `RiskUnestimated` | 15.1.23, `/decision`, `RiskUnestimated: q` |
| K34 | the test's `RiskTwoSources-sufficient` | 15.1.24, `/decision`, `RiskTwoSources: act/job_failure sufficient` |
| K35 | the test's `RiskStatementForm` | 15.1.25, `/decision`, `RiskStatementForm: probably` |
| K36 | the test's `RiskConditionShared-condition` | 15.1.26, `/decision`, `RiskConditionShared: q` |
| K37 | the test's `RiskEqualityCoefficient` | 15.1.27, `/decision`, `RiskEqualityCoefficient: C q` |
| K38 | the test's `SufficientOutsideNecessary` | 15.1.28, `/decision`, `SufficientOutsideNecessary: act/job_failure, case (q 8, r 6)` (the witness case is in `detail`) |
| K39 | the test's `RiskInconsistent-stated-cell` | 15.1.22, `/decision`, `RiskInconsistent: act/job_failure, case (q 0)` |
| K40 | the test's `InvalidModel-premise-fails` | 15.1.4, `/decision`, `InvalidModel(alternatives): premise G fails` |
| K41 | the test's `ResourceLimit-risk-margin-candidates` (50 estimates of `q` by hull); separately 42 estimates `[10i, 10i + 5]` | 15.2, `/decision`, `ResourceLimit: risk margin candidates` (**derived**: each endpoint of a cited estimate has, per cited estimate of the quantity, six candidates `w − 1`, `w`, `w + 1` for its two endpoints, all distinct across the estimates since `10i + 6 < 10(i + 1) − 1`, and no atom; 300 for 50; the smallest failing count is 43 at 258); clean for 42 (252) |
| K42 | K7 with K13 | 14.27 (phase 14 before phase 15) |
| K43 | K21 with K7 | 15.1.1 (the order inside the set: V1 before V3; test-enforced) |

For every case from K2 to K43, the route rejects, and the record's `class` equals the legacy class. K22,
K40 and every other `InvalidModel` text have the class `InvalidModel`, as `checker_error` gives it.

### 8.4 The boundary and the call sites

"The call" is `ve.alternatives.run_case` or `ve.risk.run_case` on the case the root builds, with the route
built. All records have the unit's `contract` and `"revision": R`.

| Case | Input | Expected |
|---|---|---|
| S1 | the call on A52's case (`alt-elaborate`) | returns the first row of 4.1 |
| S2 | the call on K7's case (`risk-decision`) | returns the second row of 4.1 |
| S3 | the call on A2's case | raises `UnsupportedProfile` from `Environment` at `ve/alternatives.py:24`: today's error, no row, no record |
| S4 | the call on A5's case | raises from `Environment` (`alternatives block requires alternatives@0` or the block check): today's error, no record |
| S5 | for each of S1 and S2: the route's own row on the same case | the returned row equals it in `id` and `status`; its `error` equals the record's `text`; the route's row has no `diagnostic` |
| S6 | the call on A1's case and on K1's case, in a subprocess started without the recorder plugin, with the route available | the route's row as today; afterwards none of `ve.alternatives_contract`, `ve.risk_contract`, `ve.wire_contract` is in `sys.modules` |
| S7 | `ve.alternatives_contract.public_rejection` on A1's case (accepted) with a hand-made error row `{"id": "x", "status": "error", "error": "legacy says no"}` | returns the same object; `error` is `legacy says no`; `diagnostic` is the residual record: `check` and `phase` `residual`, code `ALT_INVALID_INPUT`, class `InvalidInput`, path `""`, text `legacy says no`, args `{}` (the Lean consultation answered `clean`) |
| S8 | `public_rejection` on S1's case and its row, with `lean` a function that raises `CheckerUnavailable` | `diagnostic` is `{"contract": "alternatives@0", "revision": R, "deferred": "2.1", "text": "InvalidInput: invalid rule name 'Law'"}`; `error` is unchanged |
| S9 | `public_rejection` on A2's case and the route's row for it | `diagnostic` is the record of 1.5, with no Lean process started (the fault is in phase 1); `error` is `UnsupportedProfile: alternatives@0 is required`, the same words |
| S10 | as S8, with `lean` a function that raises `KeyError` | returns the row unchanged: no `diagnostic` |
| S11 | `public_rejection` on S1's case and row, with the contract of the shadow revision | returns the row unchanged |
| S12 | `public_rejection` twice on S1's case and row | the second call changes nothing |
| S13 | `public_rejection` on S1's case and row | the case is equal, after the call, to a deep copy taken before it |
| S14 | the syntax-tree scan of 2.8 on the tree; and on each of four changed trees: (a) `ve/document.py` gains `from .risk_contract import legacy_validation`; (b) `ve/alternatives.py` gains a second call of `public_rejection`; (c) in `ve/risk.py` the call's result is bound to a name and the name returned; (d) `ve/alternatives_contract.py` imports `ve.environment` | passes; fails on each of (a) to (d) |
| S15 | the call on an `alt-validate` case whose source is A52's | the route's row as today: no `diagnostic` |
| S16 | the call on R's `admission` case with a document whose norm unit is A52's unit 0 | `AdmissionError` with today's text, no record |
| S17 | the call on K7's case with the `ve_diagnose` binary absent | the row with the deferred record of S8's shape for `risk@0`, `deferred` `2.1`, and today's `error` |
| S18 | the call on S1's case, with `ve.backends.lean.run` wrapped to count calls | exactly one call of `wire.diagnose`, from `ve.alternatives_contract:lean_outcome`, with the one case |

### 8.5 The delta and the gate

Tier **P** runs, per unit, only when the contract's `status` is `public`: for every corpus case that the
route rejects, `public_rejection(case, row′)` on a fresh copy of the route's row, and the call on the case.
The function is checked on every rejected case. The call carries the record only on the handler-reaching
cases (2.11); on the others it must return today's row or raise today's error.

| Case | Input | Expected |
|---|---|---|
| G1 | tier P, every case, the function | the returned row's `diagnostic` equals the reported record of 2.11, computed apart; its `error` is that record's `text` for a fault record and the legacy text otherwise; `status` and `id` are the route's |
| G2 | tier P, every handler-reaching case, the call | returns a row equal to G1's |
| G12 | tier P, every rejected case that is not handler-reaching, the call | raises today's error or returns today's row, with no `diagnostic` (Z8) |
| G3 | the gate of a unit at its measurement commit, in shadow | the sum of text changes over checks that are not inherited is `text_delta_count`; `public_diagnostic_changes` lists each check of section 6 that has a case (expected none) and any check beyond it; `consultations` is present and its `unavailable` is 0; the gate exits 0 unless S7-pre or the class rule fails |
| G4 | at `public`, the signing file without the entry of a check that the measurement found changed, if any; else the signing file with an entry `8.1` | the gate fails with the first (second) line of S4 spec 4.4 |
| G5 | at `public`, the signing file with an entry `1.5` | the gate fails with the second line |
| G6 | the gate's measurement with the Lean route's text on A52's class of inputs replaced, in the test only, by a text of class `UnknownSymbol` | fails with `public delta: <n> class differences` |
| G7 | the gate with Python's `Environment` verdict on the first S7-pre candidate replaced, in the test only, by acceptance | the list `legacy_verdict_differences` shrinks by that class; with the route's verdict on a block fault replaced by acceptance, the gate fails with `legacy verdict differences` naming it |
| G8 | the delta report after a contract text is edited, without regeneration | `conformance/wire_contract_delta.py --unit <unit> --check` fails |
| G9 | the gate after S7-pre and the switch, per unit | exits 0: every row of section 9 holds |
| G10 | the gate of `risk@0` | every check of phases 14 and 15 has a first-fault witness among the record cases, and every check of phases 1 to 13 among the source cases; a check without one fails the gate unless 8.5's gap table names it |
| G11 | the pilot's and S5's gates after S7.0 | their stored reports, deltas, golden and catalogue files and English tables are byte-identical to the commit before S7.0 |
| G13 | the gate's Python column | the Python engine's deferred count equals the number of corpus cases that pass phase 1; its fault count equals the number that fail it; it reports no clean case; every Python fault equals the Lean engine's record on that case |

**Allowed coverage gaps** (base spec 8.3, for these units; the gate reads this table):

| Gap | Language | Applies to | Reason |
|---|---|---|---|
| G1 | Lean | a check every catalogue fault of which only the in-process API can carry (`readers` `python`) | Reached only by an explicit null, which the wire readers refuse before diagnosis: Lean has no witness; Python has its first-fault and masking witnesses. |
| G4 | Python | every check after phase 1 | The Python engine defers at 2.1 on every root that passes phase 1 (2.5), so it has no witness of any later check; Lean has every witness. |

### 8.6 Conservativity

- **Z1.** The full existing suite, the conformance reports, `conformance/identity.json`, the frozen baseline
  and every frozen hash are unchanged by each commit of item 1, except the files of 7.2. Every stored
  expectation of a row that a switch commit changes is listed in it (2.9).
- **Z2.** `VEError("x").to_dict()` is `{"code": "InvalidInput", "message": "x"}`, as today; no commit of item
  1 sets a `VEError`'s `diagnostic`.
- **Z3.** Every row of `ve_alternatives_route` and `ve_risk_route`, on every corpus case, is byte-identical to
  the snapshot before each commit.
- **Z4.** On every corpus case, the route gives the verdict and text of the snapshot before the commit.
- **Z5.** On every corpus case, the case is equal, after the call returned or raised, to a deep copy taken
  before it (V3 of 2.8).
- **Z6.** `frozen.py` passes; the inventory diff is as C4 says.
- **Z7.** After S7.0, the pilot's and S5's outputs are byte-identical (G11).
- **Z8.** On every rejected corpus case that is not handler-reaching (2.11), the call gives the row or error of
  the snapshot before the commit, with no `diagnostic`.
- **Z9.** On every corpus case, `ve_diagnose` was called at most once by the call, and only on a rejected case
  (S18).

### 8.7 Lean and tooling

| Case | Input | Expected |
|---|---|---|
| L1 | `ve_diagnose alternatives@0` on A52's case | `{"id": …, "status": "ok", "outcome": "fault", "diagnostic": r}` with `r` the record of 4.1's first row |
| L2 | `ve_diagnose risk@0` on K7's case | the record of 4.1's second row |
| L3 | `ve_diagnose risk@0` on R's `risk-elaborate` case; on its `risk-conflict` case with no packages | `outcome` `clean` for both (the source is clean; the record phases are guarded out) |
| L4 | `ve_diagnose <unit>` on every corpus case, before and after the unit's switch commit | the rows are equal once the old `revision` is read as `R` |
| L5 | `ve_diagnose alternatives@0` on an `admission` case; `ve_diagnose risk@0` on a case of kind `norms-elaborate` | `{"id": …, "status": "error", "error": "UnsupportedProfile: case kind <kind> has no wire contract input"}`; exit 1 |
| L6 | `ve_diagnose soft-norms@0`, and S5's two units, on their corpora after S7.0 and after each shadow commit | byte-identical rows |
| L7 | `lake build` with `Tables/Risk.lean` naming a hook `Hooks/Risk.lean` does not register | fails at the `#guard` |
| L8 | the stub of the status paragraph, compiled against the build | every `#check` elaborates, every `example` of 5.1 closes by the named theorem, and every `#eval` prints the number this file states as derived (A51, A56, K18, K41, R48, R51, R52, R60, R61, the node counts of P, Q, `allowsF` and `lessWorstF`); a difference corrects the fixture, not the stub |
| T1 | `tools/wire_contract.py --check` on the committed tree | exits 0 and prints nothing |
| T2 | a contract with `status` `public` and the shadow revision | `WC10` |
| T3 | `Tables/Alternatives.lean` at the switch commit of `alternatives@0`, against its parent | the diff is the header comment and the numeral of `revision`, and nothing else; the same for `Tables/Risk.lean` |
| T4 | `risk@0.json` with hook 14.24 renamed `policy_bound`, no registry entry for it | `WC08` |
| T5 | `--write` after S7.1a | exactly the generated files of 7.2, the lock and the generated modules' inventory lines change |
| T6 | the contract `risk@0.json`, read by a test | every entry of phases 14 and 15, at every depth, carries the literal `{"is_not": ["/decision", "null"]}` in its `when`, and no entry of phases 1 to 13 does |
| T7 | `names.json`'s `risk_identifier` and `risk_decider` as generated into `Names.lean` | `risk_identifier` admits `a_b` and refuses `a__b`, `A`, `a-b` and a 65-byte name; `risk_decider` admits `chooser` and `x` and refuses `""` and a 65-byte string; in both engines |
| T8 | the Python registry of either unit | every hook, classifier and view name of the contract is a key, and every value is `None`; `engine.run` on A1's root returns `Deferred("2.1")` |

### 8.8 The corpus-completeness test

`tests/test_wire_gate_corpus.py` keeps its three tests for every earlier unit and runs the same three for each
new unit: every input of the unit's contract tests and of the tests that build its sources
(`tests/test_alternatives_*`, `tests/test_risk_*`, `tests/test_*contract*`) is in the unit's corpus; every
source of its conformance scripts (`conformance/alternatives.py` `cases()`, `conformance/risk.py`'s policies
and records) is in it; every fixture of alternatives.md 8.1 and risk.md 8.1 that a test builds is in it. The
recorder sees the new paths through the wrappers of 7.1 (a call of `run_case` records the root the adapter
builds; a `subprocess.run` of either route binary or of `ve_diagnose` with either unit records every `alt-*`
and `risk-*` case of its input); each wrapper is shown to work by one source submitted through that path and
no other, stored in `<unit>-test-inputs.json`.

| Case | Input | Expected |
|---|---|---|
| S19 | the call on A with unit 0 named `"Law2"` | returns as S1 with `Law2` for `Law`; the source is in `alternatives@0-test-inputs.json` |
| S20 | `ve.risk_contract.public_rejection` on K7's case with the estimate id `E9` and a hand-made error row | the record of 15.1.16 with `E9`; the source is in `risk@0-test-inputs.json` |

### 8.9 Item 2

| Case | Input | Expected |
|---|---|---|
| U1 | the Rust evaluator (`ve` on a `risk-condition` case) with the condition `["lt", ["quantity", "q"], ["decimal", "gb", "6.5"]]` at scale 1 | an error with `code` `InvalidInput` and `message` `UnitPrecision(gb, scale=1)`; today `code` `UnitPrecision`, `message` `gb, scale` |
| U2 | `ve_risk_eval` on the same case | the error `UnitPrecision(gb, scale=1)` |
| U3 | `tests/test_risk_differential.py` with one shard of off-grid literals | both reject every such condition, and the Rust message equals the Lean text on each |
| U4 | the same condition at scale 10 (`6.5` is on the grid) | both accept; the verdicts of the shard are unchanged by item 2 |
| U5 | `tests/test_risk_rust.py` and the full suite after item 2 | unchanged |

## 9. The switch gate

The DRI reviews, per unit, one gate report at revision `R`, the delta report and the signing file. Astra and
Fable read the measured delta and the signing file before the switch commit. The switch commit is made only
when every row holds, and the gate exits non-zero on any unmet row that is enforced, judging each from the
data and not from a stated summary (base spec section 17).

| Row | Definition | Required |
|---|---|---|
| the continuation rows | base spec section 9: tiers 0 and A, residual, coverage; feasibility reported with `n1`, `n2`, `coarse`, `t3` partitioning the unit's numbered checks (69; 142) and no threshold; the deferred share of Python reported and equal to the share of corpus roots that pass phase 1 (G13) | as there, with G4 of 8.5 |
| S7-pre | `legacy_verdict_differences` (2.12), over every tier | empty |
| the class rule | cases with a class difference outside the exemptions of 2.12 | 0; the exempt cases counted and reported |
| the consultation | `consultations.unavailable` | 0 on the gate's host |
| the signed delta | the checks with a measured text change, against the keys of `signed` | the two sets are equal |
| the boundary | tier P: G1 on every rejected case; G2 on every handler-reaching case; G12 on every other rejected case | no difference |
| rows without a record | tier P cases on which the failure rule applied | 0 |
| the case is not modified | Z5 | 0 cases |
| the route | Z3 and Z4 | byte-identical |
| one consultation at most | Z9 | holds |
| the corpus | `tests/test_wire_gate_corpus.py` for the unit | passes |

When each row is enforced: S7-pre and the class rule from the measurement commit on, whatever the
`status`; the signed delta, the boundary and rows without a record only at `public`; every other row
whatever the `status`. A row that fails after a switch commit is handled by a revert of the commit, or by a
revision that sets `status` to `shadow`.

## 10. Limits, and what is not claimed

1. **No verdict and no identity.** The engine runs on a row the route has rejected and returns that row, at
   two call sites. That is a tested property of each (V1), not a theorem.
2. **One entry point per unit, three kinds in all.** `alt-elaborate`, `risk-elaborate` and `risk-decision`
   through `run_case`; the entry points of 2.9 keep today's rows and errors, among them Python's
   `Environment` on the alternatives route, which rejects before the route runs and whose text is its own.
3. **The delta is complete on the corpus.** An input outside the unit's corpus can show a text change that no
   list contains, a residual record, or a row without a record.
4. **Python diagnoses phase 1 only.** On every other rejection the record is Lean's, through one more Lean
   process, or the deferred record when `ve_diagnose` cannot answer. The Python registries hold no function.
5. **Inherited texts are Lean's own** until S4 items 5 and 6: the environment (2.1, risk 2.1 and 2.13), the
   W6 unit checks (risk 2.8 to 2.14), the unit decoder (4.3, 5.3), the premise units (5.2, 6.6) and the
   typing (7.1a, 8.1a). Making them includes is a later revision of each unit with its own delta.
6. **The class rule has the inherited exemptions** of 2.12, each one code of class `InvalidInput` over a
   decoder that prints several classes. Both are counted by the gate.
7. **The order inside the nine classifier sets is the route's**, test-enforced through the order keys of
   2.5; the record's admission and validation are two such sets, so a record fault has the path `/decision`
   and not a pointer into the record (the decision entry's own seven checks excepted).
8. **Rust prints nothing for these units.** There is no Rust column and no Rust engine; item 2 is one text of
   the Rust evaluator.
9. **The failure rule hides an engine defect from the caller.** The caller gets today's row; the defect is
   visible only where the gate or a test runs the same input.
10. **Cost.** A rejection at a call site costs one Python engine run of phase 1 and, on every root that passes
    it, one `ve_diagnose` process, which re-runs the route's decoders. An accepted case costs nothing.
11. **The stub is uncompiled** (status paragraph). Every number marked derived is confirmed by the build's
    first task, and the fixture, not the stub, is corrected on a difference.
12. **The GENERIC texts of row 9** stay language-specific (plan section 8, question 8).
13. **The surface prints none of the sentences of 3.2.** They are fixed, not shown.

## 11. Statement review checklist (Astra + Fable, before any build step)

1. **Scope (plan section 8, questions 2 to 7).** Is the record inside `risk@0` right, or a unit of its own?
   Is the Lean consultation in production right, or the deferred record? Is leaving Python's `Environment`
   unswitched on the alternatives route right? Is the kind list right?
2. **The `alternatives@0` table (2.3).** For each row, do the kind, guard and text reproduce
   `decodeAltSource`, `checkAlt` and `Tree.check`? Derive A65 to A70 independently. Rows worth attacking:
   3.2 (the mandatory-field order), 3.3 (code point order against the route's sort), 3.5 (the six rows of
   `outcomes`), 6.1 (twenty-one members and their arguments), 7.1 (the order keys), 8.5 (the running total
   on the inlined tree).
3. **The `risk@0` table (2.4).** The same for `decodeRiskSource`, `checkRisk`, `admitDecision` and
   `validateDecision`. Rows worth attacking: 1.1 (the W6 pair as two guarded checks), 2.4 (the four-member
   argument), 2.10 to 2.12 (the annotation loops and the extension guard), 4.9 and 4.11 (two groups over one
   pattern), 6.5 (the premises' position on this route), 14.32 (contents against issues), 15.1 (one member per
   leading text; the shared leads; `withCase`).
4. **The classifier sets (2.5).** Can any Lean classifier name a member the route did not reach, or map a
   message to the wrong member? Is reading `detail` after a fixed lead, and between parentheses for 15.1.9
   and 15.1.13, safe against input that contains the lead? Are the order keys of `record_validation`
   determinate?
5. **The boundary (2.7, 2.8).** Is modifying the route's row in Python acceptable, or must the record go on a
   `VEError`? Is one consultation per rejection acceptable? Is `checker_error(row["error"])` the right error
   object for the overlay?
6. **The class rule and S7-pre (2.12).** Are the exemptions the only ones? Attack the two S7-pre candidates;
   name a third.
7. **The delta (2.11, 6).** Is the expected empty list right? Where does the table's order differ from the
   route's outside a classifier set?
8. **Wordings (3).** Does each `says` sentence have one reading? Is any rejected wording of 3.3 still in this
   file or in the plan?
9. **Conservativity (5, 7, 8.6).** Can anything in item 1 change a verdict, an identity, a code, or a Lean byte
   other than the generated tables, the registry's added lines and the optional statements? Is the
   `Diagnose.lean` exception acceptable a second time?
10. **The derived numbers (8).** Check each derivation against the Lean definitions before the stub runs.
11. **Item 2 (2.14, 8.9).** Is the comparison rule for Rust errors of code `InvalidInput` right, and is the
    message's `scale` the same number in both?
12. **The corpus (8.8).** Does the recorder see every path through which a test submits a source of either
    unit, the direct subprocess calls of `tests/test_risk_every_diagnostic.py` included?

## 12. Choices this specification resolves, and open points

The plan fixes that there are two switch commits, that each attaches the record to the route's row, and that
each adds one production call site. Everything below is this specification's own choice, put to the
statement review.

| # | Choice | Relative to the base documents |
|---|---|---|
| R1 | Item 1 is both units through every step of 5.1, after S7.0 | the pointer names the row; no contract exists |
| R2 | The tables' order is the route's and every text is the route's; the expected delta is empty | base plan 5.1 step 1 and row 9; S5 chose Python's texts where the two differed, because its authority was Python |
| R3 | The adapters refuse `admission`; no root is refused for its content; the public switch covers three kinds | base spec 2.1; S5's adapters refused cases outside the unit's domain by content |
| R4 | The record's class is the legacy class of the route's text, by `checker_error` | base plan 2.4 ("`class` is the legacy `VEError` class"); here the public class is a classification of a Lean text |
| R5 | Nine classifier sets, mapped by fixed leading texts; `record_admission` is T1 rows for the decision entry and the record's shape, hooks for its hashes and citations, and one classifier for the cited contents; `record_validation` is one set with order keys per step | base plan 2.3 (T3 for one function with many steps); base spec R7 |
| R6 | Python registers every name as `None` and diagnoses phase 1 only; the record is Lean's through `ve_diagnose` | base plan 2.5 (the consultation); base spec 2.5 rule 6; S4 and S5 consulted no Lean process |
| R7 | The public object is the route's row, which gains `diagnostic` and may change `error` | S4 and S5 set `VEError.diagnostic`; these routes return rows, not errors |
| R8 | `public_rejection(case, row)` with a `lean` argument; the failure rule covers the consultation | S4 spec 2.3, with one more step |
| R9 | A new unit's gate reports feasibility without a threshold; gap G4 for Python's deferral | S5 spec R9 |
| R10 | `limits.json` gains four names, `names.json` four classes | base spec 2.2 |
| R11 | `legacy_validation` and `lean_case` per unit, in the contract module | S5 spec R11 |
| R12 | The `Diagnose.lean` registry is edited append-only, as a recorded C4 exception | S5 spec R12 |
| R13 | S7.0's four generalisations (7.1) | not in the base documents |
| R14 | No `lean_route_changes`; `consultations` instead | S5 spec R14 reported route differences because its order was Python's |
| R15 | The byte-equality test of 2.9 keeps its assertion on every member but `error` and `diagnostic` | plan section 8, question 10 |
| R16 | The record phases are guarded by `{"is_not": ["/decision", "null"]}` on every entry, and two optional engine lemmas state that a false guard contributes no instance | base spec 2.3 (guards); base plan C4 (optional lemmas) |
| R17 | Item 2 is one line of `risk.rs` and a differential rule for `InvalidInput` sub-codes | base plan 5.3 row 9 |
| R18 | The derived numbers of section 8 are confirmed by the stub's `#eval` before any fixture is written | the base spec computed its numbers by hand; the instruction for this draft asks for evaluation |

Open, for the review or the build to settle:

1. **The two S7-pre candidates of 2.12**, and any the shadow finds. Each is a verdict difference between
   Python's `Environment` and the route on the alternatives route; the fix is a product decision outside
   this work.
2. **The order keys of `record_validation`.** Stated as (step, member, item); the build fixes the item order
   within each step from `Record.lean:825–961` and records every key in the catalogue.
3. **Residuals inside the route's tails.** The six fallback texts of 2.3 and 2.4 are believed unreachable; a
   corpus case that reaches one is a residual and fails the gate, and the DRI decides whether to add a member.
4. **The consultation's timeout** (180 s, as the route's transport) and whether the IDE needs the deferred
   record earlier.
5. **Whether `run_alternatives_case`'s shape check should admit `diagnostic`.** It runs before the switch
   touches the row and is not changed; a future reader of rows that checks the shape must admit the member.
6. **The stub's numbers** (L8): A51, A56, K18, K41, R48, R51, R52, R60, R61 and the four node counts.

