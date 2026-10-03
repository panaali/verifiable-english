# Wire contracts, stage S5 item 1: `norms@0` and `norm-defaults@0` become public (statement specification)

> Status: statement specification, draft 1 (2026-10-03). This is the item-1 statement spec of
> [wire-contract-S5-PLAN.md](wire-contract-S5-PLAN.md) draft 2 (the **plan**). It covers item 1 only: the two
> contracts `norms@0` (W1 norm documents, base plan 5.3 row 6) and `norm-defaults@0` (the `unspecified`
> completion, row 7), each authored, run in shadow, measured and switched to `public`, which is every step of
> 5.1 of [wire-contract-PLAN.md](wire-contract-PLAN.md) (the **base plan**), and the generalisation of the
> pilot's tooling that both need first (S5.0). It builds on [wire-contract.md](wire-contract.md) (the **base
> spec**) and [wire-contract-s4.md](wire-contract-s4.md) (the **S4 spec**) and changes no definition of either.
> The Astra + Fable statement review comes before any build step. No debate was held on stage S5 (plan, status
> paragraph), so that review is the first reading of everything here that the base plan's debate did not decide;
> section 12 lists those choices. Fixtures are implementation obligations, not claims of completed tests. Nothing
> was built or run for this draft: the two tables of section 2 were authored by reading the two Python validators
> and the two Lean routes, the expected records of section 8 and the expected delta of section 6 were derived by
> hand, and every `file:line` reference was read on `main` at `b2ce446e` and must be re-read at each step. Nothing
> here changes a verdict, an identity, a code, a frozen contract, an existing theorem statement or a checker
> function.

## 0. Scope, one paragraph

After S4 one contract is public. Item 1 adds two. `norms@0` is the table of what `NormDocument` checks on a
document's norm units over a validated environment; `norm-defaults@0` is the table of what `UnspecifiedDocument`
checks, which includes the first. Each is authored from Python's order (the authority of `admission`), run in
shadow against the Lean engine and the Lean routes on a generated and replayed corpus, measured, signed by the
DRI and made **public** in the one place where Python's admission of a submitted document rejects its norm
source: the error then carries the contract's record. When a check of the table fails, the record names the
first one that fails and the message is that check's text; otherwise the message is the validator's. The legacy
validators still decide, alone, whether a source is accepted. Lean's route rows are frozen and do not change;
`ve_diagnose` gains the two units. Rust decodes neither unit and has no column. Before any of this, the pilot's
tooling, which names `soft-norms@0` throughout, is made to take a unit (S5.0).

In this specification: the decisions (1), the definitions, including the two tables (2), the English, one reading
each (3), the diagnostics (4), the Lean statements relied on and the Lean modules (5), the expected delta of each
profile (6), the files and gates of S5.0 and of each unit's measurement and switch commits (7), the acceptance
fixtures (8), the switch gate (9), limits (10), the statement review checklist (11), and the choices this
specification resolves (12).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | Each unit's root is `{"environment", "norms"}`, as the pilot's; `norms` is the array of norm objects the route validates, and the adapter builds it from an `admission` case as the route does | 2.2 |
| D2 | Each unit's table is in Python's order, the authority's; the Lean route's first fault may differ on an input with two faults, and that is reported, not enforced | 2.3, 2.4, 2.12, 2.13 |
| D3 | The contract's classes are Python's, so that the record's class is the public error's code (the class rule); where a Lean route's leading word maps to another class, that is recorded as a Lean legacy difference and not changed | 2.3, 2.12 |
| D4 | `norm-defaults@0` includes `norms@0` at the root, without a view, in three includes placed where `UnspecifiedDocument` runs W1's phases; its own checks are six hooks | 2.4 |
| D5 | The environment, the formula decoder and typing are inherited checks until S4 items 5 and 6: one inherited hook for the environment, and classifier sets whose members are keyed by Python's class for the decoder and typing | 2.3, 2.5 |
| D6 | One function per unit, `public_rejection`, in a new contract module per unit, turns a legacy rejection into the public error; it returns the same error object and never raises | 2.7 |
| D7 | One production call site per unit, inside the handler of the rejection: `NormDocument(env, active)` in `_admit_norm_document_python`, and `UnspecifiedDocument(env, [NormDocument._decode(c) …])` in `admit_norm_defaults_document`; the root's environment is `env.to_dict()` | 2.8 |
| D8 | The legacy validators are not edited; the gate calls them after the switch through compositions defined in the contract modules | 2.2, 7.2 |
| D9 | `code` is never written by a switch. On the corpus the record's class equals it on every check that is not exempt; the exemptions are the environment hook and the non-first-order formula case, listed | 2.12, 10 |
| D10 | A public change is a changed message; the complete list on the unit's corpus is measured, stored and signed check by check; at `public`, the gate fails on a change without a signature and on a signature without a change | 2.11, 9 |
| D11 | Each switch raises the unit's revision; a switch of `norms@0` also regenerates `norm-defaults@0`'s Lean table, into which `norms@0`'s entries are inlined | 2.10 |
| D12 | The unit registry of `ve_diagnose` gains two entries by an append-only edit of `Diagnose.lean`, recorded as a C4 exception | 5.3 |

## 2. Definitions

### 2.1 Terms carried over

| Term | Meaning |
|---|---|
| record, outcome, overlay, residual record, deferred record | base spec 2.7, 2.8 |
| instance, scope, position, order key | base spec 2.6; a scope is a resolved include, and a record under one carries the include id before the check id (`w1/4.2`) |
| inherited check | base spec 2.5, rule 5: a hook or member whose text is the inherited decoder's own, in each language; its `text` and `args` are not compared between engines |
| legacy validator | for each unit, the Python function and the Lean route of 2.2 |
| the gate, the corpus | `conformance/wire_contract_gate.py` with the unit as its argument (7.1), and the cases of its `gate_cases` for that unit: tiers 0, A, B, the replayed sources (tier R) and the legacy-difference inputs (tier L) |
| a corpus case that Lean reads | S4 spec 2.1; for these units every corpus case, except a recorded test input that carries a `null` |
| the class rule | the rule of 2.12 that the record's `class` is the legacy error's `code` |

A **norm source** is a pair of an environment and a list of norm objects. The **legacy error** of a norm source
is the `VEError` that the unit's Python legacy validator raises on it; its **legacy code** is the error's `code`
(a class name, since neither unit has fine codes today) and its **legacy text** is `str` of the error.

### 2.2 The two units: roots, adapters, domains, legacy validators

**Roots.** Both contracts have `"input": ["environment", "norms"]`. `environment` is a `ve.core@0.2`
environment as submitted (at the call sites, as `to_dict()` returns it, 2.8); `norms` is an array of the norm
objects (`{"norm": {…}}`) the route validates.

**Adapters.** `norm_source` (for `norms@0`) and `norm_defaults_source` (for `norm-defaults@0`), in Python and in
Lean. For a case of kind `norms-elaborate`, `norms-conflict` or `norms-certificate` (`norms@0`), or of a kind
beginning `norm-defaults-` (`norm-defaults@0`), the root's members are the case's `environment` and `norms`; a
member the case lacks is `null`. For an `admission` case, `norms` is the list of the `content` of the document's
units whose `kind` is `norm` and whose `content` is an object with a member `norm`, in document order, as
`_admit_norm_document_python` and `admit_norm_defaults_document` select `active` (`ve/norm_admission.py:67–84`;
`ve/norm_defaults_route.py:150–166`) and as the Lean routes' `splitDocument` does. Any other kind is refused, as
the pilot's adapter refuses one: the row `{"id", "status": "error", "error": "UnsupportedProfile: case kind
<kind> has no wire contract input"}`.

**Domain.** The adapter also refuses, with the error `UnsupportedProfile: the case is outside the unit's domain`,
a case that the route would never hand to the unit's validator:

- `norms` is not an array, or has an element that is not an object. Every route builds `active` from objects
  only, so `NormDocument`'s "expected norm unit" and `_decode`'s "Expected a JSON object" are unreachable, and
  neither has a check in the table (12, R3).
- the environment's `profiles` has a member outside `data@0`, `definitions@0`, `documents@1`, `norm-defaults@0`,
  `norms@0`, `relational-fol@0`, `time@0`. Checker profiles are refused by both routes before the validator
  runs (`ve/norm_admission.py:58–59`; `ve/norm_defaults_route.py:143–144`); the statement layers are dispatched
  to other routes (`ve/admission.py:499–514`); `NormDocument` alone accepts some of those environments and the
  Lean routes refuse them, which is not a difference of this unit.
- for `norm-defaults@0`: `norm-defaults@0` is not listed. The route checks it before the validator
  (`ve/norm_defaults_route.py:141–142`), and `ve_norm_defaults_route` without the profile is the W1 decoder, so
  the check is unreachable and is not in the table (12, R3).
- the environment has a member `unit_schema` or `units` (the quantity route, `ve/admission.py:504–507`).

The fault catalogue never builds a case outside the domain, and the Python engine is never handed one by a
call site: both call sites sit after the dispatch.

**Legacy validators.** Python: for `norms@0`, `NormDocument(Environment(environment), norms)`; for
`norm-defaults@0`, `UnspecifiedDocument(Environment(environment), [NormDocument._decode(c) for c in norms])`.
Each is the route's own statements in the route's order (`ve/norm_admission.py:52, 96`;
`ve/norm_defaults_route.py:140, 174`), and each is defined once as `legacy_validation(environment, norms)` in
the unit's contract module (`ve/norms_contract.py`, `ve/norm_defaults_contract.py`), for the gate and the
recorder. Lean: for `norms@0`, the route the environment selects, as Python's dispatch selects it:
`ve_norms_route` with the case kind `norms-elaborate`, or `ve_norm_defaults_route` with `norm-defaults-elaborate`
when `norm-defaults@0` is listed; for `norm-defaults@0`, `ve_norm_defaults_route` with
`norm-defaults-elaborate`. A Lean row with `status` `error` is a rejection; its `error` string is the Lean
legacy text, and its Lean class is the one `ve.backends.diagnostics.checker_error` gives it
(`ve/backends/diagnostics.py:31–52`). No Lean route reports a `code` (`lean/VE/Norms/Run.lean:191–192`;
`lean/VE/NormDefaults/Run.lean:194–195`).

**No Rust column.** Rust decodes no norm document, has no `norms-*` or `norm-defaults-*` case kind, and refuses
every environment that lists `norm-defaults@0` (`rust/ve/src/main.rs:97–295`;
`rust/ve-core/src/environment.rs:178–193`; norms.md 11.6; norm-defaults.md 8). Under edit d, Rust does not
support either unit and is not run on it.

### 2.3 The contract `norms@0`, revision 1

**Limits and classes used.** `limits.json` gains `MAX_CARVE_OUTS` 8 (a literal in both validators,
`ve/norms.py:224`; `lean/VE/Norms/Tree.lean:341`); `MAX_RULES` 256 exists. `names.json` gains `rule_name`:
`first` `a-z`; `rest` `a-z0-9-`; `max_bytes` 64 (`ve/norms.py:21, 214`; `lean/VE/Norms/Tree.lean:264–267`).
The character-set reader takes a trailing `-` as a literal (`ve/wire_contract/engine.py:210–220`); the Lean
generator must agree (T8).

**Codes.** Seventeen, with Python's classes (D3). Where the Lean route's leading word maps to another class
through `checker_error`, the second column says so; that is a Lean legacy difference, recorded in the delta and
not changed.

| Class | Codes |
|---|---|
| `InvalidInput` | `NORMS_INVALID_ENVIRONMENT`, `NORMS_PROFILE_REQUIRED` (Lean: `UnsupportedProfile`), `NORMS_INVALID_UNIT`, `NORMS_INVALID_RULE_FIELDS`, `NORMS_INVALID_NAME`, `NORMS_RESERVED_NAME`, `NORMS_UNKNOWN_PREDICATE` (Lean: `UnknownSymbol`), `NORMS_UNKNOWN_RULE`, `NORMS_PRECEDENCE_ACROSS_PREDICATES`, `NORMS_DEPENDENCY_CYCLE`, `NORMS_INVALID_INPUT` (the `residual` code) |
| `SyntaxError` | `NORMS_INVALID_FORMULA` |
| `DuplicateDeclaration` | `NORMS_DUPLICATE_DECLARATION` |
| `TypeMismatch` | `NORMS_TYPE_MISMATCH` |
| `UnknownSymbol` | `NORMS_UNKNOWN_SYMBOL` |
| `UnboundVariable` | `NORMS_UNBOUND_VARIABLE` |
| `ResourceLimit` | `NORMS_RESOURCE_LIMIT` |

`NORMS_PROFILE_REQUIRED` and `NORMS_UNKNOWN_PREDICATE` are `InvalidInput` because Python raises them as `VEError`
with a text that names another class (`ve/norms.py:204, 223`). The text is kept; the class is the public code.

**The table.** `E` abbreviates `/environment`, `P` abbreviates `/environment/vocabulary/predicates` and `N`
abbreviates `/norms`. A row "group" opens a group; its sub-entries follow, indented by `·`, until the next row
that is not indented. The texts are Python's where Python and Lean agree, Lean's where Python's is the class
without the prefix or carries a field list, and the pilot's where neither can be rendered (3.1 to 3.3; section
6 lists each). The order is `NormDocument.__init__`'s (`ve/norms.py:202–262`): the environment is decoded
(`Environment`, before the constructor), the profile and the count are checked, every unit is decoded in order
(`_decode`, `:265–275`), then each rule is checked completely before the next, then the `over` references, then
the three document-wide graphs.

Phase 1, `environment`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 1.1 | hook `w1_environment` at `E`, inherited | `NORMS_INVALID_ENVIRONMENT` | `{message}` |

Phase 2, `profiles`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 2.1 | `requires` `E/profiles` item `"norms@0"` | `NORMS_PROFILE_REQUIRED` | `UnsupportedProfile: norms@0 is required` |
| 2.2 | `max_items` `N`: `MAX_RULES` | `NORMS_RESOURCE_LIMIT` | `ResourceLimit: rules` |

Phase 3, `rule-shape`. One group `units` over `N/*`; every row below is a sub-entry, so each unit is decoded
completely before the next, as `_decode` is applied unit by unit.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · 3.1 | `exact_keys` `@`: `norm` | `NORMS_INVALID_UNIT` | `InvalidInput: expected norm object` |
| · 3.2 | `type` `@/norm`: object | as 3.1 | as 3.1 |
| · 3.3 | `exact_keys` `@/norm`: `name`, `predicate`, `sign`, `guard`, `unless`, `over` | `NORMS_INVALID_RULE_FIELDS` | `InvalidInput: invalid norm fields` |
| · 3.4 | `type` `@/norm/unless`: array | `NORMS_INVALID_RULE_FIELDS` | `InvalidInput: unless and over must be arrays` |
| · 3.5 | `type` `@/norm/over`: array | as 3.4 | as 3.4 |
| · 3.6 | `type` `@/norm/predicate`: string | `NORMS_INVALID_RULE_FIELDS` | `InvalidInput: rule predicate and precedence edges must be strings` |
| · | group `parents` over `@/norm/over/*` | | |
| · · 3.7 | `type`: string | as 3.6 | as 3.6 |
| · 3.8 | classifier `guard_syntax` at `@/norm/guard`, emits: | | |
| · · 3.8a | the guard decodes within the rule's node and depth budget; inherited | `NORMS_RESOURCE_LIMIT` | `{message}` |
| · · 3.8b | the guard is a first-order formula of the P0 wire form; inherited | `NORMS_INVALID_FORMULA` | `{message}` |
| · | group `carve-outs` over `@/norm/unless/*` | | |
| · · 3.9 | classifier `carve_out_syntax` at `@`, emits 3.9a and 3.9b, as 3.8a and 3.8b, over the budget the guard and the earlier carve-outs of the rule have used | as 3.8a, 3.8b | `{message}` |

Phase 4, `rules`. One group `rules` over `N/*`; each rule is checked completely before the next.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · 4.1 | `name` `@/norm/name`: `rule_name` | `NORMS_INVALID_NAME` | `InvalidInput: invalid rule name '{value}'` |
| · 4.2 | `unique_so_far` `@/norm/name` | `NORMS_DUPLICATE_DECLARATION` | `DuplicateDeclaration: rule {value}` |
| · 4.3 | hook `rule_name_not_reserved` at `@/norm/name` | `NORMS_RESERVED_NAME` | `InvalidInput: reserved name {value}` |
| · 4.4 | hook `regulated_predicate` at `@/norm/predicate` | `NORMS_UNKNOWN_PREDICATE` | `UnknownSymbol: regulated predicate {value}` |
| · 4.5 | `type` `@/norm/sign`: Boolean | `NORMS_INVALID_RULE_FIELDS` | `InvalidInput: invalid sign or too many carve-outs` |
| · 4.6 | `max_items` `@/norm/unless`: `MAX_CARVE_OUTS` | as 4.5 | as 4.5 |
| · 4.7 | classifier `rule_typing` at `@`, emits: | | |
| · · 4.7a | the guard, then each carve-out, is well typed over the sorts of the rule's predicate; the fault is a type mismatch; inherited | `NORMS_TYPE_MISMATCH` | `{message}` |
| · · 4.7b | the same; the fault is an unknown predicate, constant or binder sort; inherited | `NORMS_UNKNOWN_SYMBOL` | `{message}` |
| · · 4.7c | the same; the fault is a variable index outside its scope; inherited | `NORMS_UNBOUND_VARIABLE` | `{message}` |
| · · 4.7d | the guards and carve-outs of the rules up to this one together have at most 10,000 nodes; inherited | `NORMS_RESOURCE_LIMIT` | `{message}` |

Phase 5, `references`. One group `rule-refs` over `N/*`, and inside it one group `over-refs` over
`@/norm/over/*`: for each rule, each parent is checked by 5.1 and then 5.2 before the next parent.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · · 5.1 | `declared_in`: `N/*/norm/name` | `NORMS_UNKNOWN_RULE` | `UnknownRule: rule {value}` |
| · · 5.2 | hook `over_same_predicate`, returns `rule`, `predicate`, `parent_predicate` | `NORMS_PRECEDENCE_ACROSS_PREDICATES` | `PrecedenceAcrossPredicates: rule {rule} on {predicate}, rule {value} on {parent_predicate}` |

Phase 6, `semantic`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 6.1 | hook `precedence_acyclic` at `N`, returns `detail` | `NORMS_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |
| 6.2 | hook `precedence_depth_fits` at `N` | `NORMS_RESOURCE_LIMIT` | `ResourceLimit: precedence depth` |
| 6.3 | hook `layers_acyclic` at `N`, returns `detail` | `NORMS_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |

**What is not in the table, and why.** "Expected norm unit" and "Expected a JSON object" (domain, 2.2);
"regulated closure edge in norm guard" (`ve/norms.py:230–232`: a `reach` formula is refused by 3.8b first, 2.5);
the Lean route's `ill-typed rule` and `not stratified` fallbacks (no input is known that reaches them after the
checks above; a rejection there is a residual, counted); the Lean route's envelope, gate and vocabulary texts
(inside 1.1). The order inside each classifier set is the formula order: the guard, then the carve-outs in
array order, one fault per rule; the default order key (the member's index in `emits`) is never consulted,
because a rule's typing raises once.

**Planned tiers.** 24 numbered checks: T1 2.1, 2.2, 3.1 to 3.7, 4.1, 4.2, 4.5, 4.6, 5.1 (14); T2 not inherited
4.3, 4.4, 5.2, 6.1, 6.2, 6.3 (6); inherited hook 1.1 (1); T3 3.8, 3.9, 4.7 (3). `n1 + n2` is 20 of 24. The
base spec's threshold of 45 of 67 was the pilot's; for a new unit the gate reports the counts and requires none
(12, R9).

### 2.4 The contract `norm-defaults@0`, revision 1

`"uses": ["limits", "names", "norms@0"]`; adapter `norm_defaults_source`; residual code
`NORM_DEFAULTS_INVALID_INPUT`. Codes: `NORM_DEFAULTS_RESOURCE_LIMIT` (`ResourceLimit`) and the residual
(`InvalidInput`). The included checks keep `norms@0`'s codes and classes (no `as`).

The order is the route's (`ve/norm_defaults_route.py:140–174`) followed by `UnspecifiedDocument.__init__` and
`_build` (`ve/norm_defaults.py:198–231`): the environment; every unit decoded (`NormDocument._decode`, before
the constructor); W1's remaining checks (`NormDocument`, inside the constructor); the three author limits
(`_check_limits`, `:240–247`); typing over the filled environment with the node budget and the height limit
(`_check_ast`, `:249–265`); the fill premises' budget (`:222–227`). Each include has no `at`, so its site is the
root and every included check keeps its pointer and its code.

| Phase | Id | Entry | Code | Text |
|---|---|---|---|---|
| `environment` | w1-environment | include `norms@0`, phase `environment` | | |
| `rule-shape` | w1-shape | include `norms@0`, phase `rule-shape` | | |
| `norms` | w1 | include `norms@0`, phases `profiles`, `rules`, `references`, `semantic` | | |
| `limits` | 5.1 | hook `filled_vocabulary_fits` | `NORM_DEFAULTS_RESOURCE_LIMIT` | `ResourceLimit: vocabulary size` |
| | 5.2 | hook `filled_rules_fit` | `NORM_DEFAULTS_RESOURCE_LIMIT` | `ResourceLimit: rules` |
| | 5.3 | hook `unspecified_names_fit` | `NORM_DEFAULTS_RESOURCE_LIMIT` | `ResourceLimit: unspecified name length` |
| `fill` | 6.1 | hook `filled_ast_fits` | `NORM_DEFAULTS_RESOURCE_LIMIT` | `ResourceLimit: AST exceeds 10,000 nodes` |
| | 6.2 | hook `filled_precedence_depth_fits` | `NORM_DEFAULTS_RESOURCE_LIMIT` | `ResourceLimit: precedence depth` |
| | 6.3 | hook `fill_premises_fit`, returns `label` | `NORM_DEFAULTS_RESOURCE_LIMIT` | `ResourceLimit: fill premise {label}` |

The ids 5.x and 6.x count from the two phases that follow the three included ones, so that an included record
(`w1/4.2`) and an own record (`5.2`) are told apart by the slash alone. The constructor's checks that the route
makes unreachable (`norm-defaults@0 is required`, `:200`; no `soft-norms@0` or alternatives, `:201–203`) are
outside the domain (2.2) and not in the table. The W1 checks on the filled tree (`FilledNormDocument`,
`:216`) and the decoding of the filled environment (`:214`) are proved never to fail by `fill_wellFormed`
(norm-defaults.md 8); a failure there is a residual, counted.

**Planned tiers.** Six own numbered checks, all T2 and none inherited: `n1 + n2` is 6 of 6. Of the included
checks, `w1/2.1` is always masked by `w1-environment/1.1` under this unit (the environment decoder requires
`norms@0` with `norm-defaults@0`, `ve/profiles.py:105–106`); that is the allowed coverage gap G2 of 8.4.

### 2.5 The hooks and classifiers, in both languages

Rules of base spec 2.5 apply: a hook reads its two arguments only, may assume every earlier instance holds, and
is required to agree across languages only on such inputs. Lean's hooks call frozen functions read-only
(`VE.Norms.Wire`, `VE.Norms.Tree`, `VE.NormDefaults.Wire`, `VE.Route`), never `decodeSource`.

| Name | Python (`ve/norms_contract.py`) | Lean (`Hooks/Norms.lean`) |
|---|---|---|
| `w1_environment` (1.1, inherited) | `Environment(e)`; a `VEError` is the message | when `E/profiles` lists `norms@0`: `Norms.Wire.decodeNormsEnvironment`, applied to `NormDefaults.Wire.placeholderJson` of the environment when it also lists `norm-defaults@0`, followed by the reserved-`unsaid__` author check of `checkAuthor`; otherwise the route's environment decoder (`VE.Route.Wire` with `Gate.decodeEnvelope`), which refuses `regulated` as Python's `Environment` does without the profile |
| `guard_syntax` (3.8) | one `ve.ast._Decoder` decodes the guard; a `ResourceLimit` is 3.8a, a `SyntaxError` is 3.8b; a decoded formula that is not first-order (`ve.norms._first_order`) is 3.8b; any other class names no member | `Norms.Wire`'s budgeted formula decoder on the guard with the rule's fresh budget; a failure whose leading word is `ResourceLimit` is 3.8a, any other failure is 3.8b |
| `carve_out_syntax` (3.9) | one `_Decoder` decodes the guard and the carve-outs up to and including the item; the members as 3.8 | the same decoder with the shared count (`decodeNorm`'s `shared := true`), over the same formulas |
| `rule_name_not_reserved` (4.3) | fails when `E/profiles` contains `norm-defaults@0` and the name starts with `unsaid--` | the same predicate |
| `regulated_predicate` (4.4) | fails unless `P/<predicate>` is an object with a member `regulated` | the same |
| `rule_typing` (4.7) | one `ve.ast._Checker(Environment(e))` types the guard and the carve-outs of every earlier rule, then this rule's guard and carve-outs in order; the first exception's class names the member (`TypeMismatch` a, `UnknownSymbol` b, `UnboundVariable` c, `ResourceLimit` d); any other class names no member | `Norms.Tree.typeDiagnostic` on each formula in the same order, with the running node total that `check` keeps (`Tree.lean:343–346`); the leading word names the member as the class does |
| `over_same_predicate` (5.2) | as the pilot's: the rule named by the item has the same `predicate` as the enclosing rule; returns `rule`, `predicate`, `parent_predicate` | the same |
| `precedence_acyclic` (6.1) | `ve.background.dependency_order` over `{name: set(over)}`; the text after `DependencyCycle: ` is `detail` | `VE.Route.dependencyOrder` over the same graph |
| `precedence_depth_fits` (6.2) | every rule's height (1, or 1 more than the greatest height of the rules naming it) is at most 16, as `NormDocument` computes it | the same |
| `layers_acyclic` (6.3) | `dependency_order` over the regulated predicates with an edge from a rule's predicate to each regulated predicate its guard or carve-outs mention (`_used_predicates`) | `dependencyOrder` over the same graph |

| Name | Python (`ve/norm_defaults_contract.py`) | Lean (`Hooks/NormDefaults.lean`) |
|---|---|---|
| `filled_vocabulary_fits` (5.1) | declared predicates plus unspecified predicates (those whose `regulated/default` is `"unspecified"`) at most `MAX_PREDICATES` | the same count, as `checkAuthor` (`NormDefaults/Wire.lean:78`) |
| `filled_rules_fit` (5.2) | rules plus unspecified predicates at most 256 | as `checkAuthor` (`:79`) |
| `unspecified_names_fit` (5.3) | every unspecified predicate's name at most `ve.norm_defaults.MAX_NAME_BYTES` (56) in UTF-8 | as `checkAuthor` (`:80`) |
| `filled_ast_fits` (6.1) | `_Checker` over the filled environment (`UnspecifiedDocument._filled_environment`) types every author formula and one fill guard per unspecified predicate; a `ResourceLimit` fails | `ruleNodes` and `fillGuardNodes` (`NormDefaults/Tree.lean:91–95`) against 10,000, as `checkAuthor` (`:81–82`) |
| `filled_precedence_depth_fits` (6.2) | every author rule on an unspecified predicate has height at most 15 | as `checkAuthor` (`:83–84`) |
| `fill_premises_fit` (6.3) | `UnspecifiedDocument(env, decoded units)`; a `ResourceLimit` whose text starts `fill premise ` fails with the rest as `label` | the pair premises of `Fill_T` as `Wire.regeneratedU` builds them, each within the node and depth budget. Lean's route has no such check known from reading; whether it rejects such a source is S5-pre's question (2.12) |

The `norm-defaults@0` registry is the `norms@0` registry's hooks and classifiers plus its own six hooks, so the
included checks run with the same Python functions as in `norms@0`; in Lean, `Hooks/NormDefaults.lean` reuses
`Hooks/Norms.lean`'s `predicate` and `classifier` functions by name.

### 2.6 Shadow and public

As S4 spec 2.2, for each unit. While `status` is `shadow`, no output of any program depends on the contract.
When it is `public`, exactly one output depends on it: the error that the unit's call site raises (2.8).
Nothing in Lean reads `status`. Changing `status` is a contract edit and raises the revision; today's output is
restored by reverting the switch commit or by a later revision that sets `status` to `shadow`.

### 2.7 The boundary functions

```
ve.norms_contract.public_rejection(environment, norms, error, *, contract=None, registry=None)
ve.norm_defaults_contract.public_rejection(environment, norms, error, *, contract=None, registry=None)
```

Each is the S4 spec's 2.3 for its unit, step for step: return at once if `error.diagnostic` is set or the
locked contract's `status` is not `public`; the root is `{"environment": e, "norms": n}` with deep copies of the
arguments; `outcome` is `engine.run(contract, root, registry=…)` with the unit's `REGISTRY`; `record` is
`engine.overlay(contract, error, outcome)` with no Lean argument; set `error.diagnostic`, `error.message` and
`error.args` so that `message` and `str(error)` are the record's `text`; return `error`. The **failure rule**
holds: if loading the contract or any step raises an `Exception`, the function returns `error` as it received
it. It never writes `error.code`, `error.path` or `error.span`, never creates an error, never calls the legacy
validator on the source itself (the hooks of 2.5 call parts of it), and starts no Lean process.

By the overlay, the reported record is the fault record, the residual record (whose `text` is the legacy text),
or the deferred record `{"contract", "revision", "deferred": id, "text"}` with the legacy text. Both Python
registries are complete, so the gate's deferred count in Python is 0 for both units and must stay 0.

### 2.8 The call sites

**`norms@0`.** In `ve/norm_admission.py`, `_admit_norm_document_python(environment, document)` decodes the
environment (`env = … Environment(environment)`, `:52`), checks the profile and the family (`:56–59`), validates
the units (`:60–95`) and then builds the norm document by one statement, `norms = NormDocument(env, active)`
(`:96`). The switch wraps that one statement in one handler: a `VEError` it raises is passed to
`public_rejection(env.to_dict(), active, error)`, and the returned error is raised. The import of
`public_rejection` is a statement inside the handler. Nothing else in the file changes. An error from
`Environment` (`:52`), from the unit checks (`:60–95`), from `_check_quoted` (`:97–98`), from `premises()` or
from the admission rows keeps today's text and has no record.

**`norm-defaults@0`.** In `ve/norm_defaults_route.py`, `admit_norm_defaults_document(environment, document)`
decodes the environment (`:140`), checks the profile and the family (`:141–144`), validates the units
(`:145–173`) and builds the source by one statement, `source = nd.UnspecifiedDocument(env, [NormDocument._decode(c)
for c in active])` (`:174`). The switch wraps that one statement in one handler of the same shape, with
`ve.norm_defaults_contract.public_rejection(env.to_dict(), active, error)`. The quoted norms (`:177–180`) and
everything after keep today's text and have no record.

**The root's environment** is `env.to_dict()`, because the environment reaches both functions as an
`Environment` object (`ve/admission.py:503`). The checks of the two contracts read `profiles` and the
`regulated` member of each predicate, which `to_dict()` reproduces as submitted; the only check at a pointer
below `E` is 2.1, at `E/profiles`. Check 1.1 cannot fail at either call site: the same decoder accepted the same
environment one statement earlier.

Three properties follow from this shape and are tested (8.3), not proved:

- **(V1) The verdict is the legacy validator's.** Each call site raises exactly when its statement raises, and
  raises the same object: same type, same `code`. The handler ends in a `raise` on every path.
- **(V2) An accepted source does not reach the engine.** On an input the statement accepts, neither contract
  module nor `ve.wire_contract` is imported by this call.
- **(V3) The engine and the legacy validator read the same source.** The root's `norms` is the list `active`
  the statement received, and its `environment` is the dictionary of the `Environment` the statement received;
  the statement modifies neither (fixture Z5).

**The import rule** of base spec 7.3 and S4 spec 2.4 becomes a table. Inside `ve/`, outside `ve/wire_contract/`
and the three contract modules: `ve.softnorms_contract` is imported only by `ve/soft_route.py`,
`ve.norms_contract` only by `ve/norm_admission.py`, and `ve.norm_defaults_contract` only by
`ve/norm_defaults_route.py`; each importer imports the one name `public_rejection` in one import statement and
one call, both inside one `except VEError` handler of the named function, the call being the operand of a
`raise`; no module imports `ve.wire_contract`; `ve/norm_defaults_contract.py` may import `ve.norms_contract`.
`tests/test_softnorms_contract.py::test_diagnostic_modules_stay_off_verdict_import_paths` is rewritten over that
table, with the S4 spec's resolution of relative imports. The Lean import rule is unchanged.

### 2.9 Entry points: switched, and not switched

| Entry point | After the switch |
|---|---|
| `ve.admission.admit_document(environment, document)` under the Python authority, for an environment that lists `norms@0` and has a norm construct, without `soft-norms@0`, `norm-defaults@0`, `alternatives@0` or a quantity schema (`ve/admission.py:520–526`); the adapter's case kind `admission` | **public** for `norms@0`: an error of the statement of 2.8 carries the reported record |
| the same for an environment that lists `norm-defaults@0` (`ve/admission.py:515–517`) | **public** for `norm-defaults@0` |

Not switched; each keeps today's message and has no record:

| Entry point | Why not in item 1 |
|---|---|
| `Environment(environment)` at either route, and the unit checks before the statement | the environment is `vocabulary@0.2` with its `norms@0` declarations (base plan 5.3, row 4; S4 item 5); the units are `ve-document@1` (row 13) |
| `_check_quoted` and the quoted norms of the defaults route (`ve/norm_admission.py:20–25, 97–98`; `ve/norm_defaults_route.py:177–180`) | a quoted norm is a one-rule document with `over` emptied; a second call site per unit with its own delta |
| `ve.document`'s check and render of a document (`ve/document.py:168–179, 555–573, 1333`) | the unit `ve-document@1` (row 13); its norm units pass `NormDocument._decode` one by one and then `NormDocument` or `UnspecifiedDocument` over the selected units |
| `NormDocument`, `NormDocument._decode`, `UnspecifiedDocument`, `ve.norm_defaults.load_document` alone; `UnspecifiedSoftDocument` and `UnspecifiedRightsDocument`; `audit_completions` and `load_audit_source` (`ve/norm_defaults.py:668–730, 1013–1087`) | base spec section 10, item 7; the soft and rights variants are rows 1 and 10; and the two validators must stay what the gate calls |
| the readings, alternatives, risk, soft and rights routes, which build a `NormDocument` over their own sources | their own rows |
| the English front ends (`ve/norm_english.py`, `ve/norm_strict.py`, `ve/norm_defaults_english.py`) | they build the source from English; there is no submitted JSON |
| `admit_document` under the Lean authority (`ve/admission.py:454–475`), whose rejection is a Lean row read by `checker_error` | a Lean legacy row; the routes are frozen |
| every Lean row; every Rust output | base plan 2.5; Rust has no column |

Until their own rows, the same fault can therefore read differently through two entry points (plan section 8,
question 7).

The three-way tests keep their assertions: `tests/test_norms_three_way.py:168–170` matches `AST exceeds` on a
`NormDocument` built directly, which is not switched; the `invalid act phrase` matches (`:112–118, 202–205`)
are environment texts. The gate compares every text of the unit at zero tolerance instead (section 9).

### 2.10 The contract edits

Revision 1 of each contract is the shadow one of 2.3 and 2.4. The shadow may edit either (the pilot went from 1
to 3 in shadow); the switch of a unit is one further revision, written `R` in sections 4 and 8, whose only
differences from the revision before it are `"revision": R` and `"status": "public"`. What follows
mechanically, by `tools/wire_contract.py --write`:

- `contracts.lock`: the entry of the contract;
- `lean/VE/WireContract/Tables/Norms.lean` or `Tables/NormDefaults.lean`: the header comment and the numeral of
  the table's `revision`, and nothing else, and the module's line in `VE/Route/frozen-sources.sha256`;
- because the Lean generator inlines an included contract's entries (`tools/wire_contract_lean.py:140–147`), a
  revision of `norms@0` also changes the header of `Tables/NormDefaults.lean`, which names the included
  contract's hash: that module and its inventory line are regenerated too (T5), and `norm-defaults@0`'s own
  revision does not change;
- `docs/spec/norms-wire-table.md` and `docs/spec/norm-defaults-wire-table.md`: no change is expected (they
  state no revision); `--check` decides.

Every record of either engine then has the new `revision`, so the stored reports that hold records are
regenerated (gate, golden, catalogue, delta).

### 2.11 A public change, and the delta

As S4 spec 2.7, per unit. For a corpus case on which Python's legacy validator raises a legacy error with code
`c` and text `m`, let `r` be the reported record: `engine.overlay(contract, error, engine.run(contract, root,
registry=REGISTRY))`. The case has a **text change** when `r`'s `text` is not `m`; a **class difference** when
`r` has a `class` and it is not `c`; it is **attributed** to `r`'s `check` (an id, an include path such as
`w1/4.2`, or `residual`), or to `deferred`. Every check counts, inherited ones too. A case the legacy validator
accepts has no public change.

The **delta report** `conformance/wire-contract/<unit>-delta.json` has the member `public_diagnostic_changes`:
for each check with at least one text change or class difference, in table order, the number of cases with a
text change, the number with a class difference, and one example; it is computed over the whole corpus and
stored; `--check` compares it with regeneration. It also has `lean_route_changes`: for each check, the number of
corpus cases that Lean reads on which the Lean route's text differs from the record's `text`, with one example;
this is reported and not enforced (D2).

The **signing file** `conformance/wire-contract/<unit>-switch.json` is written by hand, as the pilot's: `signed`
gives each check whose text may change one sentence saying what changes; `release_note` is the text of 3.4 with
the list filled in. A class difference cannot be signed (2.12).

### 2.12 The class rule, and S5-pre

**The class rule.** On every corpus case where the reported record is a fault, the record's `class` is the
legacy code, except on the exempt checks: 1.1 (one inherited code for an environment decoder that raises several
classes) and 3.8b or 3.9b on a formula that decodes but is not first-order (the record's class is
`SyntaxError`; Python's legacy class, raised at typing, is `UnsupportedProfile`). Each exemption is listed in
section 10, and the gate counts the cases it covers.

The rule holds by construction of the Python side for every check that is not inherited (the code's class is
the class Python raises, 2.3) and for the inherited classifier members (each member is keyed by the class Python
raises, 2.5). For the Lean engine it holds by the hand-written mapping of each Lean text's leading word to a
member, tested in tiers 0 and A: a Lean text whose leading word names no member of the set makes the Lean
classifier answer `ok`, which shows as an engine mismatch, never as a silent class.

**S5-pre** blocks each unit's switch. The shadow gate lists, per unit, every corpus case on which the Python
legacy validator and the Lean route of 2.2 disagree on the verdict (`legacy_verdict_differences`). Each is
treated as a class and run to ground, as S3-pre and S4-pre were, outside this work, and recorded in
`conformance/wire-contract/s5-pre.md`; closed means the gate reports the list empty, and the gate fails
otherwise. From reading, the candidates are:

| Candidate | Python | Lean |
|---|---|---|
| a `data@0` predicate with a `functional` or `total` flag under `norm-defaults@0` | `UnspecifiedDocument` has no check | `decodeSourceU` runs the W1 decoder with `flags = false`, which rejects (`lean/VE/NormDefaults/Wire.lean:89`; `lean/VE/Norms/Wire.lean:279`) |
| a document the decoder accepts and `norms-elaborate` then rejects (a generated layer over a budget) | `NormDocument` builds no layer | not known from reading; the shadow decides |
| a pair premise of `Fill_T` over the node or depth budget | `ResourceLimit: fill premise …` (`ve/norm_defaults.py:222–227`) | no check known from reading |
| a layer cycle through a defined predicate under `definitions@0` | the layer graph has regulated nodes only (`ve/norms.py:253–258`) | the stratum graph has regulated and defined nodes (`lean/VE/Norms/Tree.lean:360–362`) |

A verdict difference is fixed outside this plan, in Python first where Python's verdict changes (a changed
verdict of a rejected or accepted cell is a product decision). Class differences between the two legacy
validators are not S5-pre's: they are recorded in the delta (`lean_route_changes`) and the contract keeps
Python's classes (D3).

### 2.13 What is constructed and what is tested

By construction:

- **(A) The public record is the measured one.** Each call site reports `overlay(run(…))` through its
  `public_rejection`, and the gate measures the delta with the same two functions on the same registry.
- **(B) In Lean only the generated tables' revisions change at a switch.** The engine reads a table's phases
  only, and revision `R` has the phases of the revision before it (T3, L4).
- **(C) The base spec's claims (A) and (B)** hold for both contracts: the expansion, and the record conditional
  on equal predicate results. The include of `norms@0` in `norm-defaults@0` is a scope of base spec 2.6 and
  adds no claim.
- **(D) The class rule, on the Python side, for the checks of 2.12.**

Tested, not constructed:

- that each engine reports a fault exactly when its legacy validator rejects, on the corpus, at zero tolerance,
  and that the Lean classifier members agree with Python's;
- that the signed list is complete: on the corpus only;
- that Python's public text equals the text of Lean's `ve_diagnose` record: on every corpus case that Lean reads,
  for checks that are not inherited;
- V1, V2 and V3 of 2.8.

Not claimed: that a Lean route's own text on a multi-fault input is the record's (D2). The table's order is
Python's; the Lean routes check the rule name's type and the sign's type while decoding each rule, the reserved
rule name after every W1 check, and the data flags under the defaults profile, where Python does not (plan
section 1). On an input with one fault the two agree on the fact, and the record's text equals the route's where
the texts agree (section 6).

## 3. English: one reading each

### 3.1 The hand-written sentences

The generated wordings of base spec 3.1 cover every T1 row of the two tables; `tools/wire_contract.py` writes
them to `docs/spec/norms-wire-table.md` and `docs/spec/norm-defaults-wire-table.md`. The hooks and members carry
these `says` sentences. "The item" is the innermost group's item, which the generated lead names (`For the
`rules` item: `); "the enclosing item" is the group one level out.

Each string is exactly as shown, backticks included, as base spec 8.1 gives the corpus sentences. The first
block is `norms@0`, the second `norm-defaults@0`.

```json
{"1.1":  "W1's environment decoder accepts `/environment`: the route's decoder when `/environment/profiles` lacks `norms@0`, and the norms route's decoder when it lists `norms@0`, applied to the placeholder environment when it also lists `norm-defaults@0`.",
 "3.8a": "The item's `norm/guard` decodes as one formula within the rule's node and depth budget.",
 "3.8b": "The item's `norm/guard` is a first-order formula of the P0 wire form.",
 "3.9a": "The item decodes as one formula within the budget that the enclosing item's `norm/guard` and the earlier carve-outs have used.",
 "3.9b": "The item is a first-order formula of the P0 wire form.",
 "4.3":  "When `/environment/profiles` contains `norm-defaults@0`: the item's `norm/name` does not start with `unsaid--`.",
 "4.4":  "The predicate named by the item's `norm/predicate` is declared with `regulated`.",
 "4.7a": "The item's `norm/guard` and then each of its `norm/unless` are well typed over the sorts of its predicate; the fault is a type mismatch.",
 "4.7b": "The item's `norm/guard` and then each of its `norm/unless` are well typed over the sorts of its predicate; the fault is an unknown predicate, constant or binder sort.",
 "4.7c": "The item's `norm/guard` and then each of its `norm/unless` are well typed over the sorts of its predicate; the fault is a variable index outside its scope.",
 "4.7d": "The guards and carve-outs of the `rules` items up to and including this one together have at most 10,000 nodes.",
 "5.2":  "The rule named by the item has the same `predicate` as the enclosing item's rule.",
 "6.1":  "The precedence graph over `/norms`, with an edge from each rule to each rule its `over` names, is acyclic.",
 "6.2":  "Every rule's precedence height, which is 1 for a rule that no rule names in `over` and otherwise 1 more than the greatest height of the rules that name it, is at most 16.",
 "6.3":  "The graph over the regulated predicates, with an edge from a rule's predicate to each regulated predicate its guard or carve-outs mention, is acyclic."}
```

```json
{"5.1": "The declared predicates and the unspecified predicates are together at most 256.",
 "5.2": "The rules of `/norms` and the unspecified predicates are together at most 256.",
 "5.3": "Every unspecified predicate's name is at most 56 bytes long in UTF-8.",
 "6.1": "The guards and carve-outs of `/norms` and one fill guard per unspecified predicate together have at most 10,000 nodes.",
 "6.2": "Every rule on an unspecified predicate has precedence height at most 15.",
 "6.3": "Every pair premise of `Fill_T` is within the node and depth budget."}
```

The three includes have no `view`, so no `says`; their generated sentence is the include row of base spec 3.1
(`The checks of phase …`). The text of an inherited member is each language's own, so the English of the
expectation is the sentence above, not the message.

### 3.2 How a public rejection reads

The S4 spec's four sentences (its 3.1) apply to every record of either unit, with the check id as the record
gives it: for an included check, the include id and the check id joined by a slash, read as "`w1/4.2`", and
`<wording>` the row of the including unit's table file. Example, for the source of fixture S1: `This input is
rejected. The first check that fails is 4.2: The `rules` item's `norm/name`, when present, differs from the value
at the same place in every earlier `rules` item.` For D4: `… The first check that fails is w1/4.2: …` with the
same wording. "First" always means the order of base spec 2.6, which the table file shows from top to bottom;
under an include it is the including contract's order.

### 3.3 Wordings this replaces, and why

| Wording | Its two readings | Written instead |
|---|---|---|
| "`norms@0` and `norm-defaults@0` are switched from shadow." (the pointer) | the two contracts exist and are in shadow; or they are to be written, shadowed and then switched | "Each contract is authored, run in shadow, measured, signed and then switched; neither exists before item 1." |
| "The order is the authority's." | Lean's, the migration's target; or Python's, the authority of `admission` today | "The table's order is `NormDocument`'s and `UnspecifiedDocument`'s, Python's; the Lean routes' order is not followed where it differs, and a difference is reported." |
| "The diagnostics become uniform." | the three languages print one message; or Python's message is the contract's text, which equals the Lean engine's record | "On every corpus case that Lean reads, Python's message is the text of the record that `ve_diagnose` gives for the same source, except on inherited checks. Rust prints nothing for these units." |
| "`norm-defaults@0` reuses W1's checks." | it calls `NormDocument` as a black box, one coarse check; or it includes `norms@0`'s phases, check by check | "`norm-defaults@0` includes the phases of `norms@0` at the root, so each W1 check is its own instance with its own id, code and path." |
| "The record's class is the error's class." | always; or where the contract declares it so | "On every check except 1.1, 3.8b and 3.9b, the record's class is the class Python raises; those three are listed exemptions." |
| "`code` is unchanged." | the error's `code`; or the record's | "The error's `code` is the legacy validator's class, as today. The record's `code` is the contract's; its `class` is the legacy code on every check that is not exempt." |
| "The delta report is complete." | no other message can change; or none on the corpus | "Every message change on the unit's corpus is in the report." |
| "Rust is deferred." | Rust runs the table and defers on a hook; or Rust is not run | "Rust decodes neither unit and is not run on it; there is no Rust column." |

### 3.4 The release notes

The `release_note` of each signing file is this text, with the unit's name and the list filled from `signed`.
For `norms@0`:

> When document admission in `ve` rejects a submitted document while it validates the document's norm units
> over its environment, the error now has one more member, `diagnostic`: the error carries the contract's
> record. When a check of the table fails, the record names the first one that fails and the message is that
> check's text; otherwise the message is the validator's. The table is `docs/spec/norms-wire-table.md`; "first"
> is its order from top to bottom. With the check, the record gives the place in the input and a code. For most
> rejections the message is the same as before. It is a different message for these checks. ⟨for each signed
> check, in table order: its id, a colon, a space, and its sentence from `signed`, the entries separated by a
> space⟩ Whether a document is accepted or rejected has not changed. The public switch does not change the
> error's `code`. An error raised before that validation, while the environment or the document's units are
> decoded, or after it, while the layers are regenerated or the report is admitted, has no record, and its
> message is as before. Other ways of submitting norms (a document check, a quoted norm, the soft, rights,
> readings, alternatives and risk routes, English input) report as before.

For `norm-defaults@0`, the same with "the document's norm units under `norm-defaults@0`", the table
`docs/spec/norm-defaults-wire-table.md`, and the last sentence listing "a document check, a quoted norm, the
completions audit, the soft and rights variants, English input".

### 3.5 The paragraphs added to the two specs

To norms.md, section 11.1, after its list of diagnostics:

> **The public record.** When document admission rejects a submitted document while it validates its norm
> units over the environment, the error carries the contract's record, in its member `diagnostic`. The contract
> is the wire contract `norms@0` ([norms-wire-table.md](norms-wire-table.md); [wire-contract.md](wire-contract.md)
> 2.7). When a check of the table fails, the record names the first one that fails and the message is that
> check's text; otherwise the message is the validator's. The checks are those of `NormDocument`, in its order,
> with one code each; the environment's own checks are one inherited check whose text is the decoder's. The
> texts above that carry no class prefix in Python (`rules`, `precedence depth`, `rule <name>`) are, in the
> public message, the prefixed forms this section lists. The contract chooses the message only: the validator
> decides, as before, whether the document is rejected.

To norm-defaults.md, section 8, after the diagnostics paragraph:

> **The public record.** When document admission rejects a submitted document under `norm-defaults@0` while it
> validates its norm units, the error carries the contract's record, in its member `diagnostic`. The contract is
> the wire contract `norm-defaults@0` ([norm-defaults-wire-table.md](norm-defaults-wire-table.md)), which
> includes `norms@0`'s checks and adds the author-side limits above, each with one code and the prefixed text
> this section lists. When a check of the table fails, the record names the first one that fails and the
> message is that check's text; otherwise the message is the validator's. The contract chooses the message only:
> the validator decides, as before, whether the document is rejected.

## 4. Diagnostics

### 4.1 The public errors

For the source of fixture S1 (base B with unit 2 renamed `a0`), `to_dict()` of the raised error is:

```json
{"code": "DuplicateDeclaration", "message": "DuplicateDeclaration: rule a0",
 "diagnostic": {"contract": "norms@0", "revision": R, "check": "4.2", "phase": "rules",
                "code": "NORMS_DUPLICATE_DECLARATION", "class": "DuplicateDeclaration",
                "path": "/norms/2/norm/name", "text": "DuplicateDeclaration: rule a0", "args": {"value": "a0"}}}
```

Today it is `{"code": "DuplicateDeclaration", "message": "rule a0"}`. For the source of fixture S2 (unit 1's
`unless` is `{}`) the message is the one printed today:

```json
{"code": "InvalidInput", "message": "InvalidInput: unless and over must be arrays",
 "diagnostic": {"contract": "norms@0", "revision": R, "check": "3.4", "phase": "rule-shape",
                "code": "NORMS_INVALID_RULE_FIELDS", "class": "InvalidInput", "path": "/norms/1/norm/unless",
                "text": "InvalidInput: unless and over must be arrays", "args": {}}}
```

For the source of fixture S16 (base U with unit 2 renamed `a0`), under `norm-defaults@0`:

```json
{"code": "DuplicateDeclaration", "message": "DuplicateDeclaration: rule a0",
 "diagnostic": {"contract": "norm-defaults@0", "revision": R, "check": "w1/4.2", "phase": "norms",
                "code": "NORMS_DUPLICATE_DECLARATION", "class": "DuplicateDeclaration",
                "path": "/norms/2/norm/name", "text": "DuplicateDeclaration: rule a0", "args": {"value": "a0"}}}
```

For the source of fixture S17 (U with a chain of sixteen rules on the unspecified predicate):

```json
{"code": "ResourceLimit", "message": "ResourceLimit: precedence depth",
 "diagnostic": {"contract": "norm-defaults@0", "revision": R, "check": "6.2", "phase": "fill",
                "code": "NORM_DEFAULTS_RESOURCE_LIMIT", "class": "ResourceLimit", "path": "",
                "text": "ResourceLimit: precedence depth", "args": {}}}
```

Today its message is `precedence depth`. With a residual record or a deferred record, `message` is the legacy
text and `diagnostic` is the record of base spec 4.1. With no record, `to_dict()` is today's.

### 4.2 Field by field

As S4 spec 4.2: the object and its type are the legacy validation's; `code` is unchanged and never written;
`message`, `str(error)` and `to_dict()["message"]` are the reported record's `text`; `diagnostic` is the
reported record, before the switch `None` and no member; `path` and `span` are unchanged, and the record's
`path` is not copied into `error.path`; every other member of `to_dict()` is unchanged, `VEError.to_dict` not
being edited (`ve/errors.py:22–30`). The legacy errors of these two units set no `path` of their own (every
raise in `ve/norms.py:202–275` and `ve/norm_defaults.py:198–265` is without one), so the public objects of 4.1
have none; `require_fields` sets `path=""` (`ve/wire.py:102–108`). A consumer that validates Python's error
object against a closed shape must admit `diagnostic`; the switch commits list every such schema and stored
expectation they had to change.

### 4.3 Lean

- Every row of `ve_norms_route` and of `ve_norm_defaults_route` is byte-identical to its row before each switch,
  on every corpus case that Lean reads.
- `ve_diagnose norms@0` and `ve_diagnose norm-defaults@0` print the records of 2.3 and 2.4; after a switch, the
  same rows with the new `revision`.
- Where a Lean route's text differs from the record's on a one-fault input (section 6), the route keeps its
  text. That is not a public change: no Lean output switches.

### 4.4 Tool diagnostics

`tools/wire_contract.py` gains no lint code. After S5.0 its findings name the contract (`<unit>: WC08: …`),
and the catalogue it reads is the unit's (7.1). Raising `status` without the revision is `WC10`; a contract
that includes `norms@0` without listing it in `uses` is `WC09`; a hook or member of either unit without a fault
in its catalogue is `WC08`.

The gate prints the S4 spec's lines (its 4.4) with the unit named, and these in addition:

| Line | Printed when |
|---|---|
| `gate fails: <unit>: legacy verdict differences <list>` | S5-pre is open |
| `gate fails: <unit>: public delta: <n> class differences` | the class rule fails on `<n>` cases outside the exemptions |
| `gate reports: <unit>: lean route differs on <n> cases` | informative; never a failure (D2) |
| `gate fails: <unit>: coverage: <check> has no first-fault witness` | a check outside the allowed gaps of 8.4 lacks one |

## 5. Lean: the statements relied on, and the Lean modules

### 5.1 Relied on, as built

The four theorems of the engine (`lean/VE/WireContract/Engine.lean:453–534`; S4 spec 5.1), `run_clean_iff`,
`run_fault_first`, `run_phase_major` and `run_congr_reached`, and their helpers, recorded in `VE/Audit.lean`.
Item 1 changes none of them, adds no theorem, and does not touch `VE/Audit.lean`, `lean/axioms.txt` or
`tools/check_lean_imports.py`. No theorem relates either contract to a decoder (base plan 3.2); none is added.
`run_congr_reached` covers the include: a scope's instances are instances of the same list, and the hooks of
both units are the same functions by name.

### 5.2 The hooks modules

`lean/VE/WireContract/Hooks/Norms.lean` and `Hooks/NormDefaults.lean`, hand-written, in the shape of
`Hooks/SoftNorms.lean`: `predicate`, `classifier`, `view` (the identity), `hooks`, `adapter` and `registered`,
and a `#guard` that every hook, classifier and view name occurring in the unit's generated table is one it
registers (`Hooks/SoftNorms.lean:214–219`). `Hooks/NormDefaults.lean` imports `Hooks/Norms.lean` and reuses its
`predicate` and `classifier` for the included names. Both import the frozen modules they call read-only
(`VE.Norms.Wire`, `VE.Norms.Tree`, `VE.NormDefaults.Wire`, `VE.NormDefaults.Tree`, `VE.Route.Wire`,
`VE.Route.Gate`, `VE.Route`); none of those is edited.

### 5.3 The unit registry: a C4 exception

`ve_diagnose` finds a unit in `units`, a hard-coded list in `lean/VE/WireContract/Diagnose.lean:32–38`, a
hand-written module in the frozen inventory (`VE/Route/frozen-sources.sha256:260`). Item 1 adds two `import`
lines and two entries to that list and changes no existing line. Under edit c the inventory diff of a commit is
additions and generated rehashes; this one line's rehash is the second exception of that kind, recorded here as
the S1b one was recorded for `VE/Audit.lean`: lines are only added, the diff is reviewed, and the rehash of the
module's inventory line goes with it. The plan's question 4 offers moving the list to `lean/DiagnoseMain.lean`,
which is not hash-listed, so that later units need no exception; this draft does not do it, and the statement
review decides.

### 5.4 Manifest, inventory, layers, imports

- **Inventory.** `Hooks/Norms.lean`, `Hooks/NormDefaults.lean`, `Tables/Norms.lean` and `Tables/NormDefaults.lean`
  are added. `Limits.lean` and `Names.lean` are regenerated (new entries), and so is `Tables/SoftNorms.lean`,
  whose header names the hashes of `limits.json` and `names.json` (base spec 7.1); those three are generated
  rehashes. `Diagnose.lean` is the exception of 5.3.
- **Assurance manifest.** The `wire.diagnose` binding gains two modes, `norms@0` with kinds `norms-elaborate`,
  `norms-conflict`, `norms-certificate` and `admission`, and `norm-defaults@0` with the `norm-defaults-` kinds
  and `admission`, each dispatching to `Diagnose.lean` and its hooks module; the two hooks modules are classified
  under `other_json` as "diagnostic only: no verdict depends on it". Nothing else of the manifest changes: the
  call sites start no Lean process, and the pinned decoder total does not grow.
- **Layers.** `ve.norms_contract` is Python layer 2 beside `ve.norms`; `ve.norm_defaults_contract` is layer 4
  beside `ve.norm_defaults` and `ve.norm_defaults_route` (`tools/layer_policy.py:17–28`).
- **Imports.** The Lean rule of base spec 7.3 is unchanged: `VE.WireContract.*` is imported by
  `VE.WireContract.*`, `DiagnoseMain` and (the engine only) `VE.Audit`. The Python rule is the table of 2.8.

## 6. The expected delta of each profile

"Only diagnostics may become uniform, listed per profile": these are the lists, from reading the validators and
the routes. None was run for this draft; the measured lists of 2.11 replace them, and the signatures are given
on the measured lists.

**`norms@0`.** Python's message at the call site of 2.8:

| Check | Today | After the switch | Read from |
|---|---|---|---|
| 2.2 | `rules` | `ResourceLimit: rules` | `ve/norms.py:206`; Lean `Norms/Wire.lean:283` |
| 3.1, 3.2 | `Incorrect fields (missing=['norm'], unknown=[…])`, or `Expected a JSON object` | `InvalidInput: expected norm object` | `ve/wire.py:104, 108`; the pilot's 4.1a text; Lean says `object expected` or `fields do not match: …` |
| 3.3 | `Incorrect fields (missing=[…], unknown=[…])` | `InvalidInput: invalid norm fields` | `ve/wire.py:108`; the pilot's 4.1c text; Lean `fields do not match: …` |
| 4.1, on a name that is not a string | Python's `repr` of the value (`True`, `[1, 2]`) | compact JSON (`true`, `[1,2]`); the same for an integer | `ve/norms.py:215`; base spec 2.7 |
| 4.2 | `rule <name>` | `DuplicateDeclaration: rule <name>` | `ve/norms.py:217`; Lean `Tree.lean:336` |
| 6.2 | `precedence depth` | `ResourceLimit: precedence depth` | `ve/norms.py:252`; Lean `Tree.lean:357` |
| 2.1, 3.4 to 3.7, 4.1 on a string, 4.3 to 4.6, 5.1, 5.2, 6.1, 6.3 | the contract's text | the same | Python's and Lean's texts agree, except Lean's `String expected` for 3.6 and 3.7 and `InvalidInput: invalid rule name` without the value for 4.1 on a non-string |
| 1.1, 3.8, 3.9, 4.7 | the inherited text | the same | inherited |

Classes: none changes at the switch. Lean legacy differences, recorded: 2.1 and 4.4 (plan section 8, question
5); 3.8b against Lean's unprefixed decoder texts; 1.1 against the environment decoder's texts without a prefix
(`duplicate declaration`, `invalid or reserved declaration: …`).

**`norm-defaults@0`.** Python's message at the call site:

| Check | Today | After the switch | Read from |
|---|---|---|---|
| 5.1 | `vocabulary size` | `ResourceLimit: vocabulary size` | `ve/norm_defaults.py:243`; Lean `NormDefaults/Wire.lean:78` |
| 5.2 | `rules` | `ResourceLimit: rules` | `:245`; `:79` |
| 5.3 | `unspecified name length` | `ResourceLimit: unspecified name length` | `:247`; `:80` |
| 6.1 | `AST exceeds 10,000 nodes` | `ResourceLimit: AST exceeds 10,000 nodes` | `ve/ast.py:212`; `:81–82` |
| 6.2 | `precedence depth` | `ResourceLimit: precedence depth` | `:265`; `:83–84` |
| 6.3 | `fill premise <label>` | `ResourceLimit: fill premise <label>` | `:227`; Lean has no check |
| the included checks | as `norms@0` | as `norms@0` | |

The gate replaces this list by the measured one; its counts are not known before the shadow.

## 7. S5.0, the measurement commits and the switch commits: files and gates

### 7.1 S5.0: the generalisation

One commit, before any contract. It changes tooling and tests only; nothing in `ve/` except a registry table
in `tools/wire_contract.py`'s own code. After it, the pilot's generated files, its stored reports, its gate
numbers (8,796 cases, 498 text changes in seven checks) and its English table are byte-identical.

| Today | After S5.0 |
|---|---|
| `tools/wire_contract.py` imports `ve.softnorms_contract.REGISTRY`, reads `examples/soft-norms@0/`, writes `docs/spec/soft-norms-wire-table.md` and `Tables/SoftNorms.lean`, and reads one catalogue (`:70–73, 501–510, 583–639`) | a table of unit to registry module (`soft-norms@0`, `norms@0`, `norm-defaults@0`); for each contract found by the glob: its examples under `examples/<unit>/`, accepted by its `legacy_validation`; its English table at `docs/spec/<unit without @n>-wire-table.md`; its Lean module `Tables/<Name>.lean` with `<Name>` the unit's words capitalised and joined (`SoftNorms`, `Norms`, `NormDefaults`); its catalogue `conformance/wire-contract/<unit>-catalogue.json` |
| the gate takes no unit (`conformance/wire_contract_gate.py:47–54, 279, 415–427, 484, 494–495, 757`) | `--unit <unit>`; the report, switch, test-inputs and examples paths, the legacy function, the Lean route and its case kind, the feasibility denominator and the allowed-gap table come from the unit; the pilot keeps its threshold, a new unit has none (12, R9); the allowed-gap table is read from the unit's statement spec (`wire-contract.md` 8.3 for the pilot, this file's 8.4 for the two units) |
| the delta, golden and catalogue tools name the pilot (`conformance/wire_contract_delta.py:11–17`; `wire_contract_golden.py:35–38`; `wire_contract_faults.py:23, 428`) | each takes `--unit`; the fault catalogue of a unit is a module `conformance/wire_contract_faults_<name>.py` with the pilot's `Fault` shape, and `catalogue(unit)` dispatches |
| the recorder wraps the soft functions (`tests/contract_input_recorder.py:35–112`) and the corpus test runs for the pilot (`tests/test_wire_gate_corpus.py:43`) | the recorder also wraps `legacy_validation`, `public_rejection`, `admit_norm_document`, `admit_norm_defaults_document`, `NormDocument.__init__` and `UnspecifiedDocument.__init__` (recording a call only when the environment is in the unit's domain and the caller is a test file), and `ve_diagnose` with either unit; the three corpus tests are parametrised over the three units, with the globs `tests/test_norm*` and `tests/test_*contract*` added |
| the pre-commit hook names the soft paths (`tools/hooks/precommit.py:448–462`) | the paths of every unit, from the same table |
| `Diagnose.lean` lists the pilot | the two entries of 5.3 (in S5.1a and S5.2a, not in S5.0) |

### 7.2 Diff scope, per unit

Item 1 is, per unit, a shadow commit (S5.1a, S5.2a), a measurement commit (S5.1b, S5.2b) and a switch commit
(S5.1d, S5.2d), after S5.0 and after the commit of S5-pre where one is needed.

**The shadow commit** of `norms@0`: `ve/wire_contract/norms@0.json`, `examples/norms@0/` (two examples: base B
and the empty source), `limits.json` and `names.json` with their lock entries; `ve/norms_contract.py` (hooks,
classifiers, adapter, `legacy_validation`, `REGISTRY`; no `public_rejection` yet); `lean/VE/WireContract/Hooks/Norms.lean`,
the generated `Tables/Norms.lean`, `Limits.lean`, `Names.lean` and the regenerated `Tables/SoftNorms.lean`, with
their inventory lines; `Diagnose.lean` (5.3); `docs/spec/norms-wire-table.md`; `conformance/wire_contract_faults_norms.py`
and the stored reports of the unit (gate, golden, catalogue); the manifest's `wire.diagnose` mode;
`tools/layer_policy.py`; tests. The shadow commit of `norm-defaults@0` is the same list for its unit, plus the
regenerated `Tables/Norms.lean` if `norms@0`'s revision moved.

**The measurement commit** of a unit: the stored gate and delta reports regenerated over the whole corpus with
`public_diagnostic_changes` and `lean_route_changes`; the gate enforces S5-pre and the class rule from here;
tests (the fixtures G3, G6 and G8 of the unit). No file of `ve/` or `lean/` changes.

**The switch commit** of a unit: the contract and the lock (2.10); its generated table and inventory line (and
`Tables/NormDefaults.lean` with its line, for a switch of `norms@0`); the contract module gains
`public_rejection`; the one call site (2.8); the gate's tier P and the rows of section 9 enforced at `public`;
the stored reports at revision `R`, the new `<unit>-switch.json`, and `<unit>-test-inputs.json` for the sources
of 8.7; tests; `tests/contract_input_recorder.py` if a wrapper is still missing; the import-scan test; the
paragraph of 3.5 in the unit's spec; this file's response section.

Not changed by any commit of item 1, and checked by the diff-scope test of C1: `ve/norms.py`,
`ve/norm_defaults.py`, `ve/environment.py`, `ve/errors.py`, `ve/wire.py`, `ve/ast.py`, `ve/background.py`,
`ve/admission.py`, `ve/wire_contract/engine.py`, `contract.schema.json`, the pilot's contract and examples, every
Lean module other than the generated tables, the two hooks modules and `Diagnose.lean`, `VE/Audit.lean`,
`lean/axioms.txt`, `tools/check_lean_imports.py`, `Main.lean`, every Rust file, `conformance/identity.json`,
the frozen baseline. The commit of S5-pre is a different commit, before the switch, with its own scope.

### 7.3 The gates

The four conservativity gates of base plan 5.2, as the debate amended them, for every commit of item 1:

- **C1.** The diff is within 7.2. `VEError.to_dict()` is not edited; `diagnostic` is set at two more call sites.
- **C2.** Legacy verdicts equal their snapshot. Each engine reports `clean` on every accepted corpus case of its
  unit and a fault on every rejected one, in Python and in Lean; Rust is not run. Python's deferred count is 0.
- **C3.** Public diagnostics change only as the signed delta of the unit lists; the gate fails otherwise. S5.0
  and the shadow and measurement commits change no public diagnostic.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass. The inventory diff is the
  additions and generated rehashes of 5.4 and the append-only `Diagnose.lean` diff of 5.3, and nothing else; no
  commit touches `VE/Audit.lean`.

The corpus-completeness test is kept, with its three tests per unit (8.7).

## 8. Acceptance fixtures for item 1

Deterministic, with expectations written by hand from section 2 and base spec sections 2 and 8. Each reviewer
derives the expectation of every fixture before reading the column "Expected". A fixture of 8.1 or 8.2 is green
when the Python engine and `ve_diagnose` both return the expected outcome, as records compared by base spec
2.7, except that an inherited record's `text` and `args` are each language's own.

**The base B** (`norms@0`): the environment of `ve/wire_contract/examples/soft-norms@0/empty.json` with
`profiles` `["norms@0", "relational-fol@0"]` and one more predicate `c` (`{"arguments": ["assistant"],
"description": "c"}`), and three norm objects, in this order:

| Index | `name` | `predicate` | `sign` | `guard` | `unless` | `over` |
|---|---|---|---|---|---|---|
| 0 | `a0` | `x_required` | `true` | `["unary", "c", ["var", 0]]` | `[]` | `[]` |
| 1 | `b1` | `x_permitted` | `false` | `["top"]` | `[["unary", "c", ["var", 0]]]` | `[]` |
| 2 | `c2` | `x_required` | `false` | `["top"]` | `[]` | `["a0"]` |

**The base U** (`norm-defaults@0`): B's environment with `profiles` `["norm-defaults@0", "norms@0",
"relational-fol@0"]` and `x_permitted`'s `default` `"unspecified"`, with B's norms. B and U are the first
example of each contract; the second is each environment with `norms` `[]`.

"Unit *i*" is `/norms/i`. For a source with norms `N`, the document **D(N)** is `{"units": [{"id": "u<i>",
"span": [i, i + 1], "kind": "norm", "content": n_i}, …], "graph": {"root": "r", "nodes": []}}`: the routes
validate the units and then run the statement of 2.8 before they read the graph. "The call" is
`ve.admission.admit_document(environment, D(N))` under the Python authority. All records have the unit's
`contract` and `"revision": R`.

### 8.1 The engine on `norms@0`

| Case | Change to B | Expected `check`, `path`, `text` |
|---|---|---|
| N1 | none; and the second example | clean; both legacy validators accept |
| N2 | `profiles` `["relational-fol@0"]` and every `regulated` member removed | 2.1, `/environment/profiles`, `UnsupportedProfile: norms@0 is required` |
| N3 | 257 rules: B's three and 254 copies of unit 0 named `r3` to `r256` | 2.2, `/norms`, `ResourceLimit: rules`; `args` `count` `257`, `limit` `256` |
| N4 | unit 1 gains a member `extra` with the value `1` | 3.1, `/norms/1`, `InvalidInput: expected norm object` |
| N5 | unit 0's `norm` is `[]` | 3.2, `/norms/0/norm`, the same text |
| N6 | unit 2's `norm` lacks `over` | 3.3, `/norms/2/norm`, `InvalidInput: invalid norm fields` |
| N7 | unit 1's `unless` is `{}` | 3.4, `/norms/1/norm/unless`, `InvalidInput: unless and over must be arrays` |
| N8 | unit 2's `over` is `["a0", 7]` | 3.7, `/norms/2/norm/over/1`, `InvalidInput: rule predicate and precedence edges must be strings` |
| N9 | unit 0's `guard` is a chain of 65 `not` around `["top"]` | 3.8a, `/norms/0/norm/guard`, class `ResourceLimit`; text each language's own |
| N10 | unit 0's `guard` is `5` | 3.8b, `/norms/0/norm/guard`, class `SyntaxError` |
| N11 | unit 1's `unless` is `[["unary", "c", ["var", 0]], 5]` | 3.9b, `/norms/1/norm/unless/1`, class `SyntaxError` |
| N12 | unit 0's `name` is `"A0"` | 4.1, `/norms/0/norm/name`, `InvalidInput: invalid rule name 'A0'` |
| N13 | unit 2's `name` is `"a0"` | 4.2, `/norms/2/norm/name`, `DuplicateDeclaration: rule a0` |
| N14 | `profiles` gain `norm-defaults@0` (sorted) and unit 1's `name` is `"unsaid--x"` | 4.3, `/norms/1/norm/name`, `InvalidInput: reserved name unsaid--x`; the Lean legacy validator is the defaults route (2.2), which rejects |
| N15 | unit 0's `predicate` is `"c"` | 4.4, `/norms/0/norm/predicate`, `UnknownSymbol: regulated predicate c` |
| N16 | unit 1's `sign` is `"no"` | 4.5, `/norms/1/norm/sign`, `InvalidInput: invalid sign or too many carve-outs` |
| N17 | unit 1's `unless` has nine copies of its carve-out | 4.6, `/norms/1/norm/unless`, the same text; `args` `count` `9`, `limit` `8` |
| N18 | unit 0's `guard` is `["binary", "c", ["var", 0], ["var", 0]]` | 4.7a, `/norms/0`, class `TypeMismatch` |
| N19 | unit 0's `guard` is `["unary", "d", ["var", 0]]` | 4.7b, `/norms/0`, class `UnknownSymbol` |
| N20 | unit 0's `guard` is `["unary", "c", ["var", 1]]` | 4.7c, `/norms/0`, class `UnboundVariable` |
| N21 | unit 0's `guard` is a left-nested conjunction of 3,334 atoms `["unary", "c", ["var", 0]]` | 4.7d, `/norms/0`, class `ResourceLimit` (10,001 nodes under `_Checker`: 3,333 `and` nodes and 2 per atom; the count is to be confirmed by the build, the member is not) |
| N22 | unit 2's `over` is `["zz"]` | 5.1, `/norms/2/norm/over/0`, `UnknownRule: rule zz` |
| N23 | unit 2's `over` is `["b1"]` | 5.2, `/norms/2/norm/over/0`, `PrecedenceAcrossPredicates: rule c2 on x_required, rule b1 on x_permitted` |
| N24 | unit 0's `over` is `["c2"]` | 6.1, `/norms`, `DependencyCycle: a0, c2` |
| N25 | seventeen rules `r0` to `r16` on `x_required`, guard `["top"]`, each after the first `over` the one before it, replacing B's rules | 6.2, `/norms`, `ResourceLimit: precedence depth` (height 17) |
| N26 | unit 0's `guard` is `["unary", "x_permitted", ["var", 0]]` and unit 1's `guard` is `["unary", "x_required", ["var", 0]]` | 6.3, `/norms`, `DependencyCycle: x_permitted, x_required` |
| N27 | N4 with N13 | 3.1, `/norms/1` (phase 3 before phase 4) |
| N28 | N15 with unit 1's `name` `"B1"` | 4.4, `/norms/0/norm/predicate` (item-major: rule 0 completely before rule 1) |
| N29 | N12 with N15 | 4.1, `/norms/0/norm/name` (table order inside the item) |
| N30 | N7 with N16 | 3.4, `/norms/1/norm/unless` (phase 3 before phase 4, on the same item) |
| N31 | unit 1's `unless` is `[["unary", "c", ["var", 0]], ["unary", "d", ["var", 0]]]` | 4.7b, `/norms/1`, class `UnknownSymbol` (the second carve-out; the first is typed) |

For every case N2 to N31, the record's `class` equals the code the legacy validator reports in Python
(`VEError.code`), and the Lean route rejects; for N14 the route is the defaults route.

### 8.2 The engine on `norm-defaults@0`

| Case | Change to U | Expected `check`, `path`, `text` |
|---|---|---|
| D1 | none; and the second example | clean; both legacy validators accept |
| D2 | unit 1's `unless` is `{}` | `w1-shape/3.4`, `/norms/1/norm/unless`, phase `rule-shape`, code `NORMS_INVALID_RULE_FIELDS` |
| D3 | unit 2's `name` is `"a0"` | `w1/4.2`, `/norms/2/norm/name`, phase `norms`, `DuplicateDeclaration: rule a0` |
| D4 | unit 1's `name` is `"unsaid--x"` | `w1/4.3`, `/norms/1/norm/name`, `InvalidInput: reserved name unsaid--x` |
| D5 | unit 0's `over` is `["c2"]` | `w1/6.1`, `/norms`, `DependencyCycle: a0, c2` |
| D6 | 253 predicates `b0` to `b252` added, each `{"arguments": ["assistant"], "description": "b"}` (256 declared) | 5.1, `""`, `ResourceLimit: vocabulary size` |
| D7 | 253 rules `r3` to `r255` on `x_required`, guard `["top"]`, added (256 rules) | 5.2, `""`, `ResourceLimit: rules` |
| D8 | `x_permitted` renamed to a 57-byte name, in its declaration, in `x_required`'s `permission` and in unit 1 | 5.3, `""`, `ResourceLimit: unspecified name length` |
| D9 | unit 0's `guard` is a left-nested conjunction of 3,332 atoms `["unary", "c", ["var", 0]]` | 6.1, `""`, `ResourceLimit: AST exceeds 10,000 nodes` (9,999 author nodes, within W1's budget, plus the fill guard's 2; the counts are to be confirmed by the build, the check is not) |
| D10 | sixteen rules `r0` to `r15` on `x_permitted`, guard `["top"]`, each after the first `over` the one before it, replacing U's rules | 6.2, `""`, `ResourceLimit: precedence depth` (height 16: within W1's 16, over the profile's 15) |
| D11 | a document whose pair premise `unsaid:pair:x_required,x_permitted` exceeds the node budget when built, with every author formula within W1's budget | 6.3, `""`, `ResourceLimit: fill premise unsaid:pair:x_required,x_permitted`; the construction is the build's. If no such input exists within W1's budget, 6.3 is removed before revision 1, as the pilot's 6.10c was (base spec section 15) |
| D12 | D8 with unit 2's `over` `["b1"]` | `w1/5.2`, `/norms/2/norm/over/0` (phase `norms` before phase `limits`) |
| D13 | D10 with D8 | 5.3, `""` (phase `limits` before phase `fill`) |

### 8.3 The boundary and the call sites

| Case | Input | Expected |
|---|---|---|
| S1 | the call on B with unit 2 named `a0` | raises a `DuplicateDeclaration` whose `to_dict()` is the first object of 4.1 |
| S2 | the call on B with unit 1's `unless` `{}` | `to_dict()` is the second object of 4.1 |
| S3 | the call on B with 257 rules (N3) | `code` `ResourceLimit`; `message` `ResourceLimit: rules`; record 2.2 |
| S4 | the call on B with predicate `c` lacking `description` | raises from `Environment` at `ve/norm_admission.py:52`: `diagnostic` is `None` and the message is today's |
| S5 | the call on B with D(N)'s unit 2 lacking `span` | raises the unit error of `ve/norm_admission.py:72` before the statement of 2.8: `diagnostic` is `None` and the message is today's |
| S6 | for each of S1 to S3: the legacy error `e` from `legacy_validation` on the same source | the raised error has `e`'s type and `e`'s `code`; `str` of it, its `message` and its record's `text` are equal |
| S7 | the call on `tests/test_norm_admission.py::source()` (accepted), in a subprocess started without the recorder plugin, with the Lean route available | admission returns as today; afterwards none of `ve.norms_contract`, `ve.norm_defaults_contract`, `ve.wire_contract` is in `sys.modules` |
| S8 | `ve.norms_contract.public_rejection` on B (accepted) with a hand-made `VEError("legacy says no")` | returns the same object; `message` is `legacy says no`; `diagnostic` is the residual record: `check` and `phase` `residual`, code `NORMS_INVALID_INPUT`, class `InvalidInput`, path `""`, text `legacy says no`, args `{}` |
| S9 | `public_rejection` on S1's source and its legacy error, with a registry that lacks `regulated_predicate` | `diagnostic` is `{"contract": "norms@0", "revision": R, "deferred": "4.4", "text": "rule a0"}`; the message is unchanged. (4.2 holds on no rule before unit 2, so the first deferred instance is 4.4 at unit 0) |
| S10 | as S9, with a registry whose `regulated_predicate` raises `KeyError` | returns `e` unchanged: `diagnostic` is `None` |
| S11 | `public_rejection` on S1's source and error, with the contract of the shadow revision | returns the error unchanged |
| S12 | `public_rejection` twice on S1's source and error | the second call changes nothing |
| S13 | `public_rejection` on S1's source and error | the two arguments are equal, after the call, to deep copies taken before it |
| S14 | the syntax-tree scan of 2.8 on the tree; and on each of four changed trees: (a) `ve/document.py` gains `from .norms_contract import legacy_validation`; (b) `ve/norm_admission.py` gains a second call of `public_rejection`; (c) in `ve/norm_admission.py` the call is bound to a name and the name raised; (d) `ve/norm_defaults_route.py` imports `ve.norms_contract` | passes; fails on each of (a) to (d) |
| S15 | `NormDocument(Environment(B.environment), N)` on S1's norms; `NormDocument._decode` on unit 1 of S2 | each raises an error whose `diagnostic` is `None` and whose message is the legacy text |
| S16 | the call on U with unit 2 named `a0` | raises a `DuplicateDeclaration` whose `to_dict()` is the third object of 4.1 |
| S17 | the call on U with the sixteen rules of D10 | `to_dict()` is the fourth object of 4.1 |
| S18 | the call on U with `x_required`'s `default` `"unspecified"` as well and no `norm-defaults@0` in `profiles` | raises from `Environment` at `ve/norm_defaults_route.py:140` (`UnsupportedProfile: unspecified completion requires norm-defaults@0`): `diagnostic` is `None` |
| S19 | the call on U with unit 0's `content` `{"norm": …}` and a quoted unit (kind `quoted`) whose `norm` names predicate `c` | raises from the quoted check (`:177–180`): `diagnostic` is `None` |
| S20 | `ve.norm_defaults_contract.public_rejection` on U (accepted) with a hand-made `VEError("x")` | the residual record of `norm-defaults@0`, code `NORM_DEFAULTS_INVALID_INPUT` |
| S21 | `public_rejection` on S16's source and error with a registry lacking `filled_rules_fit` | `diagnostic` is the fault record of `w1/4.2` (found before any deferred instance) |
| S22 | `public_rejection` on D7's source and its legacy error with a registry lacking `filled_rules_fit` | `diagnostic` is `{"contract": "norm-defaults@0", "revision": R, "deferred": "5.2", "text": "rules"}` |

### 8.4 The delta and the gate

Tier **P** runs, per unit, only when the contract's `status` is `public`: for every corpus case that Python's
legacy validator rejects with an error `e`, `public_rejection(environment, norms, e′)` on a fresh error `e′`
of the same source, and the call on D(N).

| Case | Input | Expected |
|---|---|---|
| G1 | tier P, every case, the function | the returned error's `diagnostic` equals the reported record of 2.11, computed apart; its `message` is that record's `text`; its type and `code` are `e`'s |
| G2 | tier P, every case, the call | raises; `to_dict()` equals `e`'s `to_dict()` with `message` replaced by the record's `text` and `diagnostic` added |
| G3 | the gate of a unit at its measurement commit, in shadow | the sum of text changes over checks that are not inherited is `text_delta_count`; `public_diagnostic_changes` lists each check of section 6 that has a case, and any check beyond section 6 is reported, not dropped; `lean_route_changes` is present; the gate exits 0 unless S5-pre or the class rule fails |
| G4 | at `public`, the signing file without the entry of 4.2 (`norms@0`) or 6.2 (`norm-defaults@0`) | the gate fails with the first line of S4 spec 4.4 |
| G5 | at `public`, the signing file with an entry `3.4` | the gate fails with the second line |
| G6 | the gate's measurement with Python's legacy class on N15's class of inputs replaced, in the test only, by `UnknownSymbol` | fails with `public delta: <n> class differences` |
| G7 | the gate with the Lean verdict of the candidates of 2.12 replaced, in the test only, by `ok` where Python rejects | fails with `legacy verdict differences` naming them |
| G8 | the delta report after a contract text is edited, without regeneration | `conformance/wire_contract_delta.py --unit <unit> --check` fails |
| G9 | the gate after S5-pre and the switch, per unit | exits 0: every row of section 9 holds |
| G10 | the gate of `norm-defaults@0` | `w1/2.1` has no first-fault witness and the gate passes under gap G2; any other included check without one fails |
| G11 | the pilot's gate after S5.0 | 8,796 cases; the stored report, the delta, the golden and catalogue files and the English table are byte-identical to `main` at `b2ce446e` |

**Allowed coverage gaps** (base spec 8.3, for these units; the gate reads this table):

| Gap | Language | Applies to | Reason |
|---|---|---|---|
| G1 | Lean | a check every catalogue fault of which only the in-process API can carry (`readers` `python`) | Reached only by an explicit null, which the wire readers refuse before diagnosis: Lean has no witness; Python has its first-fault and masking witnesses. |
| G2 | both | an included check whose every reaching input fails an earlier check of the including unit on every input of the unit's domain (`w1/2.1` of `norm-defaults@0`) | The including unit's environment decoder requires the profile this check requires, so the check is never the first fault under this unit; it is witnessed in the included unit's own gate. |

### 8.5 Conservativity

- **Z1.** The full existing suite, the conformance reports, `conformance/identity.json`, the frozen baseline and
  every frozen hash are unchanged by each commit of item 1, except the files of 7.2. Every stored expectation of
  a Python error's text that a switch commit changes is listed in it.
- **Z2.** `VEError("x").to_dict()` is `{"code": "InvalidInput", "message": "x"}`, as today.
- **Z3.** Every row of `ve_norms_route` and `ve_norm_defaults_route`, on every corpus case that Lean reads, is
  byte-identical to the snapshot before each commit.
- **Z4.** On every corpus case, Python's legacy validator gives the verdict, code and text of the snapshot before
  the commit. (A commit of S5-pre has its own snapshot rule, 2.12.)
- **Z5.** On every corpus case, the environment and the norms are equal, after `legacy_validation` returned or
  raised, to deep copies taken before it (V3 of 2.8).
- **Z6.** `frozen.py` passes; the inventory diff is as C4 says.
- **Z7.** After S5.0, the pilot's outputs are byte-identical (G11).

### 8.6 Lean and tooling

| Case | Input | Expected |
|---|---|---|
| L1 | `ve_diagnose norms@0` on S1's source as a `norms-elaborate` case | `{"id": …, "status": "ok", "outcome": "fault", "diagnostic": r}` with `r` the record of 4.1's first object |
| L2 | `ve_diagnose norm-defaults@0` on S16's source as a `norm-defaults-elaborate` case | the record of 4.1's third object |
| L3 | `ve_diagnose norms@0` on an `admission` case whose document is D(N) of S1 | the same record as L1 (the adapter selects the active units) |
| L4 | `ve_diagnose <unit>` on every corpus case that Lean reads, before and after the unit's switch commit | the rows are equal once the old `revision` is read as `R` |
| L5 | `ve_diagnose norms@0` on a case of kind `norms-elaborate` whose `norms` is `"x"`, and on one whose environment lists `closure@0` | `{"id": …, "status": "error", "error": "UnsupportedProfile: the case is outside the unit's domain"}`; exit 1 |
| L6 | `ve_diagnose soft-norms@0` on the pilot's corpus after S5.0 and after each shadow commit | byte-identical rows |
| L7 | `lake build` with `Tables/Norms.lean` naming a hook `Hooks/Norms.lean` does not register | fails at the `#guard` |
| T1 | `tools/wire_contract.py --check` on the committed tree | exits 0 and prints nothing |
| T2 | a contract with `status` `public` and the shadow revision | `WC10` |
| T3 | `Tables/Norms.lean` at the switch commit of `norms@0`, against its parent | the diff is the header comment and the numeral of `revision`, and nothing else; the same for `Tables/NormDefaults.lean` at its switch |
| T4 | `norm-defaults@0.json` with `uses` `["limits", "names"]` | `WC09` |
| T5 | `norms@0.json` with its revision raised and nothing else changed, then `--check` | `WC11` on `Tables/Norms.lean` and on `Tables/NormDefaults.lean` (the include is inlined); `--write` regenerates both and their inventory lines, and `norm-defaults@0`'s revision and lock entry do not change |
| T6 | `norms@0.json` with hook 4.3 renamed `rule_name_free`, no catalogue fault for it | `WC08` |
| T7 | `--write` after S5.1a | exactly the generated files of 7.2, the lock and the generated modules' inventory lines change |
| T8 | `names.json`'s `rule_name` as generated into `Names.lean` | the Lean class admits `a-b` and refuses `a_b`, `A`, and a 65-byte name, as the Python engine does |
| T9 | `tools/wire_contract.py` run in a copy where `ve/wire_contract/` holds the pilot alone | the same findings and files as before S5.0 |

### 8.7 The corpus-completeness test

`tests/test_wire_gate_corpus.py` keeps its three tests for the pilot and runs the same three for each new unit:
every input of the unit's contract tests and of the tests that build its sources is in the unit's corpus; every
source of its conformance scripts (`conformance/norm_defaults_three_way.py`, `norm_defaults_differential.py`,
`norm_defaults.py`'s `sources()`; the generated documents of `tests/test_norms_three_way.py:76–101`) is in it;
every fixture of norms.md 10.1 and norm-defaults.md 9 that a test builds is in it. The recorder sees the new
paths through the wrappers of 7.1; each wrapper is shown to work by one source submitted through that path and
no other (S23, S24, as the S4 spec's S17 and S18), stored in `<unit>-test-inputs.json`.

| Case | Input | Expected |
|---|---|---|
| S23 | the call on B with unit 0's `name` `"A1"` | raises as N12 with `A1` for `A0`; the source is in `norms@0-test-inputs.json` |
| S24 | `ve.norm_defaults_contract.public_rejection` on U with unit 0's `name` `"A2"` and a hand-made `VEError("x")` | the record of `w1/4.1` with `A2`; `code` `InvalidInput`, the hand-made error's own; the source is in `norm-defaults@0-test-inputs.json` |

## 9. The switch gate

The DRI reviews, per unit, one gate report at revision `R`, the delta report and the signing file. Astra and
Fable read the measured delta and the signing file before the switch commit. The switch commit is made only when
every row holds, and the gate exits non-zero on any unmet row that is enforced, judging each from the data and
not from a stated summary (base spec section 17).

| Row | Definition | Required |
|---|---|---|
| the continuation rows | base spec section 9: tiers 0 and A, residual, deferred, coverage; feasibility reported with `n1`, `n2`, `coarse`, `t3` partitioning the unit's numbered checks (24; 6) and no threshold | as there |
| S5-pre | `legacy_verdict_differences`, over every tier | empty |
| the class rule | cases with a class difference outside the exemptions of 2.12 | 0; the exempt cases counted and reported |
| the signed delta | the checks with a measured text change, against the keys of `signed` | the two sets are equal |
| the boundary | tier P: G1 on every rejected case, G2 on every case | no difference |
| errors without a record | tier P cases on which the failure rule applied | 0 |
| the source is not modified | Z5 | 0 cases |
| the legacy validators | Z3 and Z4 | byte-identical |
| the Lean route delta | `lean_route_changes` | reported |
| the corpus | `tests/test_wire_gate_corpus.py` for the unit | passes |

When each row is enforced: S5-pre and the class rule from the measurement commit on, whatever the `status`;
the signed delta, the boundary and errors without a record only at `public`; every other row whatever the
`status`. A row that fails after a switch commit is handled by a revert of the commit, or by a revision that
sets `status` to `shadow`.

## 10. Limits, and what is not claimed

1. **No verdict and no identity.** The engine runs inside the handler of a rejection and returns the error it
   was given, at two call sites. That is a tested property of each (V1), not a theorem.
2. **One entry point per unit.** Only admission is public; the entry points of 2.9 keep today's messages.
3. **The delta is complete on the corpus.** An input outside the unit's corpus can show a message change that no
   list contains, a class that differs from its record's, a residual record, or an error without a record.
4. **The table's order is Python's.** The Lean routes' first fault can differ on multi-fault inputs; the record
   is the table's and both engines give it; the route's text is reported beside it.
5. **Inherited texts differ between languages** until S4 items 5 and 6: the environment (1.1), the formula
   decoder (3.8, 3.9) and typing (4.7). Making them includes is a later revision of each unit with its own delta.
6. **The class rule has two exemptions.** On 1.1 the record's class is `InvalidInput` whatever class the
   environment decoder raised; on 3.8b and 3.9b over a formula that decodes but is not first-order the record's
   class is `SyntaxError` while Python's legacy class is `UnsupportedProfile`. Both are counted by the gate.
7. **Lean's classes differ on two checks** (2.1, 4.4) and on the inherited ones; a Lean-authority deployment would
   report those classes. Not changed (D3).
8. **Rust prints nothing for these units.** There is no Rust column, no Rust engine and no Rust tolerance.
9. **The failure rule hides an engine defect from the caller.** The caller gets today's error; the defect is
   visible only where the gate or a test runs the same input.
10. **Cost.** A rejection at a call site costs one engine run; `rule_typing` retypes the earlier rules and
    `fill_premises_fit` rebuilds the source. An accepted document costs nothing.
11. **`env.to_dict()` is the root's environment**, not the submitted bytes; the two contracts read nothing of it
    that the round trip changes (2.8), and the gate's corpus uses the submitted dictionary.
12. **The surface prints none of the sentences of 3.2.** They are fixed, not shown.

## 11. Statement review checklist (Astra + Fable, before any build step)

1. **Scope (plan section 8, questions 2, 3, 7).** Is S5 before S4 items 3 to 6 right? Is one shadow per unit
   right? Is one entry point per unit right?
2. **The `norms@0` table (2.3).** For each row, do the kind, guard and text reproduce `ve/norms.py:202–275`?
   Derive N27 to N31 independently. Rows worth attacking: 3.1 and 3.2 (the chosen text), 3.8 and 3.9 (the shared
   budget), 4.1 (the quotes and the non-string case), 4.7 (the running total and the member keyed by class).
3. **The `norm-defaults@0` table (2.4).** Do the three includes sit where `UnspecifiedDocument` runs W1's
   phases, in particular the decode of every unit before the constructor? Is dropping the profile check (domain)
   right? Derive D12 and D13.
4. **The domain (2.2).** Is refusing non-object units and the dispatched profiles at the adapter the right way to
   keep C2 true, or should those be listed verdict differences? Is `norm-defaults@0` inside `norms@0`'s domain
   with the Lean validator selected by profile sound?
5. **The hooks (2.5).** Can any Lean hook fail for a reason that belongs to a later check? Is `w1_environment`'s
   three-way definition exact against `Environment`? Does `rule_typing`'s member mapping admit a text with no
   member that Python maps to one?
6. **The class rule and S5-pre (2.12).** Are the exemptions the only ones? Is "classes are Python's" right
   against aligning Python to Lean (plan question 5)? Attack the four S5-pre candidates.
7. **The delta (2.11, 6).** Derive the expected list of section 6 independently; attack 3.1 to 3.3 and 4.1.
8. **Wordings (3).** Does each `says` sentence have one reading? Is any rejected wording of 3.3 still in this
   file or in the plan?
9. **Conservativity (5.3, 7, 8.5).** Can anything in item 1 change a verdict, an identity, a code, or a Lean byte
   other than the generated tables and the registry's added lines? Is the `Diagnose.lean` exception acceptable,
   or should the list move (plan question 4)?
10. **S5.0 (7.1).** Does the generalisation leave the pilot byte-identical, and is the per-unit allowed-gap table
    read from the right file?
11. **The corpus (8.7).** Does the recorder see every path through which a test submits a source of either unit?

## 12. Choices this specification resolves, and open points

The plan fixes that there are two switch commits, that each sets `VEError.diagnostic` and the message, and that
each adds one production call site. Everything below is this specification's own choice, put to the statement
review.

| # | Choice | Relative to the base documents |
|---|---|---|
| R1 | Item 1 is both units through every step of 5.1, after S5.0 | the pointer says "switched from shadow"; no contract exists |
| R2 | The tables' order is Python's; the Lean routes' order is reported where it differs | base plan 5.1 step 1 and rows 6 and 7; the pilot's order was Lean's and equalled the route's |
| R3 | The unit's domain excludes non-object units, the dispatched and checker profiles, and (for `norm-defaults@0`) the missing profile; the adapters refuse such cases and the catalogue never builds them; the corresponding checks are not in the tables | base spec 2.1 puts `null` outside the domain in the same way; the pilot had every check of its validator |
| R4 | The contract's classes are Python's; Lean's leading words are not followed on 2.1 and 4.4 | base plan 2.4 ("`class` is the legacy `VEError` class"); base plan 5.1 step 1 keeps the authority's rejected cells |
| R5 | Inherited classifier sets keyed by Python's class for the formula decoder and typing; one inherited hook with one code for the environment, exempt from the class rule | base spec D8 and 2.5 rule 5 give inherited checks one code each |
| R6 | The non-first-order formula is refused by the syntax classifier (`_first_order`), with a listed class exemption | `ve/norms.py:113–122` exists for the family-norms mode; the pilot's `fol_formula` had no such clause |
| R7 | `norm-defaults@0` includes `norms@0` without a view, in three includes; `w1_environment` applies the placeholder rewrite in Lean under the profile | base spec 2.6 (scopes); a view would put every included path at `""` with `inner_path`, which edit g allows but nothing needs |
| R8 | The roots' environment at the call sites is `env.to_dict()` | the S4 spec excluded an environment object's `to_dict()`; here no submitted dictionary reaches the call sites |
| R9 | A new unit's gate reports feasibility without a threshold; the allowed-gap table is read from the unit's statement spec; G2 for an always-masked included check | base spec section 9 fixed 45 of 67 for the pilot and read its table from `wire-contract.md` |
| R10 | `limits.json` gains `MAX_CARVE_OUTS`, `names.json` gains `rule_name`; the other limits the hooks read are the modules' constants | base spec 2.2: `limits.json` holds every value a contract names |
| R11 | `legacy_validation` per unit, in the contract module, is what the gate and the recorder call | the pilot called an existing function, `load_soft_document` |
| R12 | The `Diagnose.lean` registry is edited append-only, as a recorded C4 exception | edit c foresaw only `VE/Audit.lean` |
| R13 | S5.0's naming rules for modules and tables; a fault-catalogue module per unit | not in the base documents |
| R14 | `lean_route_changes` is reported, never enforced | base spec section 9 compared Lean's text with the route's for checks that are not inherited, which held because the pilot's order was the route's |
| R15 | The three-way tests' substring assertions stay; the gate's zero tolerance is the row's "tolerance removed" | base plan 5.3 row 6 |

Open, for the review or the build to settle:

1. **The four S5-pre candidates of 2.12**, and any the shadow finds. Each is a verdict difference between two
   frozen-by-policy validators; the fix is a product decision outside this work.
2. **`fill_premises_fit` (6.3)** may have no reaching input within W1's budget; then it is removed before
   revision 1, and the Python check it mirrors becomes a residual that the gate must show never fires.
3. **`rule_typing`'s member set.** Python's `_Checker` may raise `UnsupportedProfile` (a `$string` quantifier,
   a `reach` node on a FOL environment) or a plain `VEError`; no member is declared for them, so they show as
   residuals; the shadow decides whether a member is added, with Lean's leading word for it.
4. **The reserved-name position.** `rule_name_not_reserved` is `norms@0`'s 4.3 at Python's position; under
   `norm-defaults@0` Lean's route checks it last. The engines agree (both run the table); only the route's text
   differs. Whether the DRI prefers the check in `norm-defaults@0`'s own phases, after `w1`, at Lean's position
   and against Python's, is a delta-review decision (base plan question 3).
5. **The registry (plan question 4).** Append-only edits of `Diagnose.lean`, or one move of the list to
   `DiagnoseMain.lean`.
6. **Node counts in N21 and D9.** The numbers follow `_Checker`'s ticks as read; the build confirms them, and the
   expected check does not depend on them.
7. **Whether `Environment.to_dict()` can differ from the submitted dictionary at a pointer the contracts read.**
   Read as no; the gate's corpus submits dictionaries and tier P compares the call's record with the function's.
