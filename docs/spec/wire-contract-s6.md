# Wire contracts, stage S6 item 1: `speech-acts@0` becomes public (statement specification)

> Status: statement specification, draft 1 (2026-10-04). This is the item-1 statement spec of
> [wire-contract-S6-PLAN.md](wire-contract-S6-PLAN.md) draft 2 (the **plan**). It covers item 1 only: the contract
> `speech-acts@0` (base plan 5.3, row 8), authored, run in shadow, measured on both sides and switched to `public`,
> which is every step of 5.1 of [wire-contract-PLAN.md](wire-contract-PLAN.md) (the **base plan**). It builds on
> [wire-contract.md](wire-contract.md) (the **base spec**), [wire-contract-s4.md](wire-contract-s4.md) (the **S4
> spec**) and, on branch `design/wire-s5`, [wire-contract-s5.md](wire-contract-s5.md) (the **S5 spec**), and
> changes no definition of any of them; the generalised tooling of S5.0 is assumed as the S5 spec's 7.1 states it.
> The Astra + Fable statement review comes before any build step. No debate was held on stage S6 (plan, status
> paragraph), so the review is the first reading of everything here that the base plan's debate did not decide;
> section 12 lists those choices. Fixtures are implementation obligations, not claims of completed tests. Nothing
> was built or run for this draft: the table of section 2 was authored by reading the Python core and the Lean
> route, the expected records of section 8 and the expected delta of section 6 were derived by hand, and every
> `file:line` reference was read on `main` at `bb05a08d` (and `wire-s5/integrate` at `eccd329b`) and must be re-read
> at each step. A scratch Lean file restating the statements of 5.1 and computing the numbers of section 8 by
> `#eval` was written (`/tmp/wire-s6-stubs/Stubs.lean`, outside the repository); the sandbox this draft was written
> in cannot run Lean, so it was not run, and 5.1 and 8.6 state the obligation and the command. Nothing here changes
> a verdict, an identity, a code, a frozen contract, an existing theorem statement or a checker function.

## 0. Scope, one paragraph

After S5 three contracts exist. Item 1 adds one: `speech-acts@0` is the table of what `SpeechDocument` checks on a
speech-act document's units, reading sets and query records over a validated environment, in the order of
speech-acts.md section 7 refined as base plan row 8 fixes it, the shape of every unit before any unit's
references. It is authored, run in shadow against the Lean engine and the Lean route on a generated and replayed
corpus, measured on two sides, signed by the DRI on the Python side and made **public** in the one place where
Python's `ve-document@2` source wrapper rejects a document while the core validates it: the error then carries
the contract's record. When a check of the table fails, the record names the first one that fails and the message
is that check's text; otherwise the message is the validator's. The legacy validators still decide, alone, whether
a document is accepted. Lean's route rows are frozen and do not change; `ve_diagnose` gains the unit, and the Lean
side of the delta lists where the route's own first fault differs from the record. Rust elaborates no speech act
and has no column.

In this specification: the decisions (1), the definitions, including the table (2), the English, one reading each
(3), the diagnostics (4), the Lean statements relied on and the Lean modules (5), the expected delta, both sides
(6), the files and gates of the shadow, measurement and switch commits (7), the acceptance fixtures (8), the
switch gate (9), limits (10), the statement review checklist (11), and the choices this specification resolves
(12).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | The root is `{"environment", "document"}`; `document` is the object the route validates, with `units`, and optionally `queries` and `reading_sets`; the adapter builds it from a `speech-elaborate` case | 2.2 |
| D2 | The table's order is speech-acts.md 7's "Order" paragraph refined as base plan row 8 fixes it: the gate, the block, W1's declarations, the block's references, the document's shape, every unit's shape in document order, the bindings, every unit's references in document order, the candidates, the queries, the policy. Both validators' first fault on a multi-fault document may differ from it; that is measured on two sides and enforced on neither | 2.3, 2.10, 2.12 |
| D3 | The contract's classes are Python's, so that the record's class is the public error's code (the class rule); Python raises most speech-act rejections as a plain `VEError`, so most codes are `InvalidInput` under a text that names another class; where the Lean route's leading word maps to another class, that is a Lean legacy difference, recorded and not changed | 2.3, 2.11 |
| D4 | The environment is one inherited hook (W1's decoder on the environment without the speech block and profile); the P0 formula shape and typing are inherited classifier sets keyed by class; W1's norm decoder, the single-rule check of a dormant norm and W1's check of the policy are inherited hooks. The contract has no include and no view | 2.3, 2.4 |
| D5 | The reading candidates are one classifier set whose members mirror the unit checks: a candidate is checked as the unit would be were it chosen, in the table's order | 2.3 (9.7), 2.4 |
| D6 | Wordings (`source`), identities (`meaning_id`), the wrapper's envelope fields, answer and compliance records, and a reading-set unit that carries content or another kind are outside the domain | 2.2 |
| D7 | One function, `ve.speech_acts_contract.public_rejection`, turns a legacy rejection into the public error; it returns the same error object and never raises | 2.6 |
| D8 | One production call site, inside the handler of the rejection of `SpeechDocument(…)` in `SpeechSource.__init__` (`ve/speech_document.py:245`); the root's environment is `self.env.to_dict()` and its document is the three members the statement receives | 2.7 |
| D9 | The legacy validators are not edited; the gate calls them after the switch through compositions defined in the contract module | 2.2, 7.2 |
| D10 | `code` is never written by the switch. On the corpus the record's class equals it on every check that is not exempt; the exemptions are the inherited hooks whose decoder raises several classes, listed | 2.11, 10 |
| D11 | A public change is a changed message; the complete list on the corpus is measured, stored and signed check by check; at `public`, the gate fails on a change without a signature and on a signature without a change. The Lean side is stored and reported | 2.10, 9 |
| D12 | The switch raises the revision; in Lean only the generated table's revision changes | 2.9 |
| D13 | The unit registry of `ve_diagnose` gains one entry by an append-only edit of `Diagnose.lean`, recorded as a C4 exception, unless S5 has moved the list | 5.3 |

## 2. Definitions

### 2.1 Terms carried over

| Term | Meaning |
|---|---|
| record, outcome, overlay, residual record, deferred record | base spec 2.7, 2.8 |
| instance, position, order key | base spec 2.6; this contract has no scope, so no record carries an include id or an `inner_path` |
| inherited check | base spec 2.5, rule 5: a hook or member whose text is the inherited decoder's own, in each language; its `text` and `args` are not compared between engines |
| legacy validator | the Python core and the Lean route of 2.2 |
| the gate, the corpus | `conformance/wire_contract_gate.py --unit speech-acts@0` and the cases of its `gate_cases`: tiers 0, A, B, the replayed sources (tier R) and the legacy-difference inputs (tier L) |
| a corpus case that Lean reads | S4 spec 2.1; for this unit every corpus case, except a recorded test input that carries a `null`, which only the in-process API can pass |
| the class rule | the rule of 2.11 that the record's `class` is the legacy error's `code` |
| handler-reaching | a rejected corpus case whose call on the wrapper reaches the statement of 2.7 (2.10) |

A **speech source** is a pair of an environment and a document object. The **legacy error** of a speech source is
the `VEError` that the Python core raises on it; its **legacy code** is the error's `code` and its **legacy text**
is `str` of the error.

### 2.2 The unit: root, adapter, domain, legacy validators

**Root.** `"input": ["environment", "document"]`. `environment` is a `ve.core@0.2` environment as submitted (at
the call site, as `to_dict()` returns it, 2.7); `document` is an object whose members are `units` (an array of
unit objects), and optionally `queries` (an array of query records) and `reading_sets` (an array of W2 reading
sets).

**Adapter.** `speech_source`, in Python (`ve/speech_acts_contract.py`) and in Lean (`Hooks/SpeechActs.lean`). For
a case of kind `speech-elaborate` the root's members are the case's `environment` and `document`; a member the
case lacks is `null`. Any other kind is refused, as the earlier adapters refuse one: the row `{"id", "status":
"error", "error": "UnsupportedProfile: case kind <kind> has no wire contract input"}`. The kinds `speech-answer`,
`speech-consequence` and `speech-conflict` decode the same document first, but a rejection of theirs after the
decode is not a rejection of the source, so they are not the unit's cases (12, R1).

**Domain.** The unit's domain is the set of speech sources on which its two legacy validators are compared. The
adapter also refuses, with the error `UnsupportedProfile: the case is outside the unit's domain`, a source that
the wrapper never hands to the core, or on which only one validator reads a member, so that the two would not be
validating the same thing:

- `environment` is not an object (the wrapper requires one, `ve/speech_document.py:142`).
- `document` is not an object with a member `units`, or has a member other than `units`, `queries` and
  `reading_sets`. The wrapper passes exactly those three to the core (`:245`); Lean's `displayFields` refuses
  other members, and Lean alone reads `answers` (`Wire.lean:872, 951–960`).
- `units` is an array and some element is an object that lacks one of `id`, `span`, `kind`, `meaning`,
  `support`, or has a member outside those five and `content`. Lean requires `id`, `span`, `kind` and admits
  `meaning`, `support`, `content`, `source`, `meaning_id` (`Wire.lean:456`); Python requires `id`, `kind`,
  `meaning`, `support` and admits anything (`ve/speech_acts.py:537`); the wrapper supplies the five and adds
  `source`, `parent_id`, and admits `surface`, `status`, `meaning_id` (`ve/speech_document.py:164–193`). In the
  intersection both read the same envelope. `source` is excluded with it: Lean reads it for the ASCII and
  choice-kind checks only, Python also parses it (`_check_wordings`), and the English layer is outside the base
  plan (its section 4). `meaning_id` is W2's identity and the wrapper's check (`:249–264`).
- some unit's `span` is not an array of two integers with the first at most the second, or the spans are not
  sorted and non-overlapping. Lean checks both (`Wire.lean:459–462, 879`); the core reads no span; the wrapper
  checks a partition of the source bytes before the statement (`:169–172, 194`).
- some reading set names as its `unit` a unit whose `kind` is not `asserted` or that has a `content` member.
  Both cores replace such a unit by its latest authored choice and never validate its own kind and content
  (`ve/speech_acts.py:545–550`, `_reading_choice`; `Wire.lean:669–678`, `chosenUnit`), so a check on them would
  fault where the validators accept (plan section 8, question 5).

A source inside the domain need not reach the call site. A source whose environment does not decode, or whose
reading sets the wrapper refuses, is in the domain: both legacy validators refuse it, and both engines and the
boundary function are tested on it; the wrapper refuses it before the statement of 2.7, so those checks are
never a public record (2.10, the handler-reaching cases).

The fault catalogue never builds a case outside the domain, and the Python engine is never handed one by the
adapter. The call site hands the engine the wrapper's units, which carry `source` and `parent_id` and may carry
`surface`, `status` and `meaning_id`; no check of the table reads those members (2.7, V4).

**Legacy validators.** Python: `SpeechDocument(Environment(environment), document["units"],
document.get("queries", []), reading_sets=document.get("reading_sets", []))`, the `core` of the three-way tests
(`tests/test_speech_acts_conformance.py:41–43`), defined once as `legacy_validation(environment, document)` in
`ve/speech_acts_contract.py`, for the gate and the recorder. Lean: `ve_speech_acts_route` with the case kind
`speech-elaborate` (`checkedDocument`: `Wire.decodeDocument` then `checkMeaningIds`, which reads nothing in the
domain). A Lean row with `status` `error` is a rejection; its `error` string is the Lean legacy text, and its Lean
class is the one `ve.backends.diagnostics.checker_error` gives it. The route reports no `code`.

**No Rust column.** Rust has no speech-act route, decoder or case kind (speech-acts.md 10; `rust/` names none).
Under edit d, Rust does not support the unit and is not run on it.

### 2.3 The contract `speech-acts@0`, revision 1

**Limits and classes used.** `limits.json` gains `MAX_DEFINITES` 64, `MAX_ALTERNATIVES` 16, `MAX_QUESTIONS` 256,
`MAX_READINGS` 64 and `MAX_OPEN_TERM_UNIT_BYTES` 47 (literals in both validators: `ve/speech_acts.py:65, 738, 620,
662, 761`; `Tree.lean:261, 282, 291`; `Wire.lean:746, 786, 907`). `names.json` gains `w2_token`: `first`
`A-Za-z0-9_.-`; `rest` `A-Za-z0-9_.-`; `max_bytes` 64 (`ve/speech_acts.py:19`; `Tree.lean:185–187`). The
character-set reader takes a trailing `-` as a literal (S5 spec 2.3); the Lean generator must agree (T7).

**Codes.** Forty-three, with Python's classes (D3). Where the Lean route's leading word maps to another class
through `checker_error`, that is a Lean legacy difference, recorded in the delta and not changed.

| Class | Codes |
|---|---|
| `InvalidInput` | `SPEECH_PROFILE_REQUIRED`, `SPEECH_UNSUPPORTED_DECLARATION`, `SPEECH_INVALID_BLOCK`, `SPEECH_INVALID_ENVIRONMENT`, `SPEECH_ATTACHED_SLOT`, `SPEECH_UNKNOWN_SORT`, `SPEECH_UNKNOWN_CONSTANT`, `SPEECH_INVALID_DOCUMENT`, `SPEECH_INVALID_READING_SET`, `SPEECH_INVALID_SET_VERSION`, `SPEECH_INVALID_UNIT`, `SPEECH_INVALID_UNIT_ID`, `SPEECH_DUPLICATE_UNIT_ID`, `SPEECH_INVALID_KIND`, `SPEECH_INVALID_BINDING`, `SPEECH_MISPLACED_CONTENT`, `SPEECH_INVALID_COMMAND`, `SPEECH_INVALID_FORCE`, `SPEECH_INVALID_FORMULA`, `SPEECH_INVALID_QUESTION`, `SPEECH_INVALID_NORM`, `SPEECH_INVALID_CONTENT`, `SPEECH_DUPLICATE_BINDING`, `SPEECH_BINDING_CONFLICT`, `SPEECH_UNKNOWN_PREDICATE`, `SPEECH_MISSING_ROLE`, `SPEECH_TYPE_MISMATCH_ARGS`, `SPEECH_UNBOUND_SLOT`, `SPEECH_TYPE_MISMATCH_ADDRESSEE`, `SPEECH_UNKNOWN_ALTERNATIVE`, `SPEECH_ALTERNATIVE_SORT`, `SPEECH_DUPLICATE_ALTERNATIVE`, `SPEECH_INVALID_READING`, `SPEECH_INVALID_QUERY`, `SPEECH_DUPLICATE_QUERY`, `SPEECH_QUERY_MISMATCH`, `SPEECH_UNKNOWN_RULE`, `SPEECH_INVALID_POLICY`, `SPEECH_INVALID_INPUT` (the `residual` code) |
| `UnsupportedProfile` | `SPEECH_UNSUPPORTED_PROFILE` |
| `ResourceLimit` | `SPEECH_RESOURCE_LIMIT` |
| `UnknownSymbol` | `SPEECH_UNKNOWN_SYMBOL` |
| `TypeMismatch` | `SPEECH_TYPE_MISMATCH` |
| `UnboundVariable` | `SPEECH_UNBOUND_VARIABLE` |

`SPEECH_PROFILE_REQUIRED` is `InvalidInput` because the core raises the absence of `speech-acts@0` as a `VEError`
(`ve/speech_acts.py:493–494`) and Python's `Environment` refuses the block without the profile as a field error
(`ve/environment.py:327`); `SPEECH_UNSUPPORTED_DECLARATION` because Python's `Environment` refuses a `defined`
member without `definitions@0` as a field error (`ve/environment.py:394–404`). A `functional` or `total` flag
without `data@0` is refused by `Environment` as an `UnsupportedProfile` (`Predicate flags require data@0`,
`:400–402`), so 1.9 and 1.10 carry `SPEECH_UNSUPPORTED_PROFILE`. The three typing codes carry the classes
`ve.ast._Checker` raises. The text is kept; the class is the public code.

**The table.** `E` abbreviates `/environment`, `S` abbreviates `/environment/speech_acts`, `P` abbreviates
`/environment/vocabulary/predicates`, `D` abbreviates `/document`. A row "group" opens a group; its sub-entries
follow, indented by `·`, until the next row that is not indented. `{id}` is the argument `"id": "@/id"` (or
`@1/id` one group further in); `{value}` is the target's value. Guards are written after the kind. Three guards
recur: **C** is `[present @/content/command, absent @/content/binding]`; **Q** is `[present @/content/question,
absent @/content/binding, absent @/content/command]`; **N** is `[present @/content/norm, absent @/content/binding,
absent @/content/command, absent @/content/question]`; **F** is `[present @/content, absent @/content/binding,
absent @/content/command, absent @/content/question, absent @/content/norm]`. The absents reproduce the tag
precedence of both cores (`contentTag`, `Wire.lean:432–441`; `ve/speech_acts.py:559–593`): binding, command,
question, norm, formula. The texts are those of speech-acts.md 7 and of the two validators where they agree;
Lean's where Python's lacks the class prefix (the four limits) or differs in words (1.4, 1.6, 1.9, 1.10); section
6 lists each.

Phase 1, `profiles` (speech-acts.md 1.6, 7; `ve/profiles.py:48–84`; `Wire.lean:112–118, 140–144`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 1.1 | `requires` `E` member `profiles` | `SPEECH_UNSUPPORTED_PROFILE` | `UnsupportedProfile: profiles must be a sorted unique array` |
| 1.2 | `type` `E/profiles`: array of strings | as 1.1 | as 1.1 |
| 1.3 | `sorted_unique` `E/profiles` | as 1.1 | `UnsupportedProfile: profiles must be sorted and unique` |
| 1.4 | `requires` `E/profiles` item `"speech-acts@0"` | `SPEECH_PROFILE_REQUIRED` | `UnsupportedProfile: speech-acts@0 is required` |
| 1.5 | `requires` `E/profiles` item `"norms@0"` | `SPEECH_UNSUPPORTED_PROFILE` | `UnsupportedProfile: speech-acts@0 requires norms@0` |
| | group `profile-items` over `E/profiles/*` | | |
| · 1.6 | `enum`: `"norms@0"`, `"relational-fol@0"`, `"speech-acts@0"` | as 1.1 | `UnsupportedProfile: speech-acts@0 with {value}` |
| 1.7 | `requires` `E/profiles` item `"relational-fol@0"` | as 1.1 | `UnsupportedProfile: Missing profile relational-fol@0` |
| | group `declared-predicates` over `P/*` | | |
| · 1.8 | `excludes` `@` member `defined` | `SPEECH_UNSUPPORTED_DECLARATION` | `UnsupportedProfile: speech-acts@0 with definitions` |
| · 1.9 | `excludes` `@` member `functional` | `SPEECH_UNSUPPORTED_PROFILE` | `UnsupportedProfile: speech-acts@0 with data flags` |
| · 1.10 | `excludes` `@` member `total` | as 1.9 | as 1.9 |

Phase 2, `block` (speech-acts.md 3.1; `ve/speech_acts.py:34–50`; `Wire.lean:56–93, 146–149`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 2.1 | `requires` `E` member `speech_acts` | `SPEECH_INVALID_BLOCK` | `InvalidInput: speech_acts block` |
| 2.2 | `keys` `S`: required `task`; optional `addressee`, `definites` | as 2.1 | as 2.1 |
| 2.3 | `type` `S/task`: string | as 2.1 | as 2.1 |
| 2.4 | `name` `S/task`: `w2_token` | as 2.1 | as 2.1 |
| 2.5 | `exact_keys` `S/addressee`: `constant`, `sort` | as 2.1 | as 2.1 |
| 2.6 | `type` `S/addressee/sort`: string | as 2.1 | as 2.1 |
| 2.7 | `type` `S/addressee/constant`: string | as 2.1 | as 2.1 |
| 2.8 | `type` `S/definites`: object | as 2.1 | as 2.1 |
| | group `definite-constants` over `S/definites/*` | | |
| · 2.9 | `type` `@`: string | as 2.1 | as 2.1 |
| | group `definite-phrases` over `S/definites/*` | | |
| · 2.10 | hook `definite_phrase` at `@` | as 2.1 | as 2.1 |

Phase 3, `declarations`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 3.1 | hook `w1_environment` at `E`, inherited | `SPEECH_INVALID_ENVIRONMENT` | `{message}` |

Phase 4, `scope` (the block's references; `ve/speech_acts.py:51–69, 84–101`; `Wire.lean:152–156, 191–197`;
`Tree.lean:257–264`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 4.1 | hook `template_slots_apart` at `P` | `SPEECH_ATTACHED_SLOT` | `InvalidInput: speech template slot must stand apart` |
| 4.2 | hook `sort_declared` at `S/addressee/sort` | `SPEECH_UNKNOWN_SORT` | `UnknownSymbol: sort {value}` |
| 4.3 | hook `addressee_constant_of_sort` at `S/addressee/constant` | `SPEECH_UNKNOWN_CONSTANT` | `UnknownSymbol: {value}` |
| 4.4 | `max_items` `S/definites`: `MAX_DEFINITES` | `SPEECH_RESOURCE_LIMIT` | `ResourceLimit: definites` |
| | group `definite-references` over `S/definites/*` | | |
| · 4.5 | hook `constant_declared` at `@` | `SPEECH_UNKNOWN_CONSTANT` | `UnknownSymbol: {value}` |

Phase 5, `document` (the document's shape and the reading sets' shape; `ve/speech_acts.py:197–229, 503–513`;
`Wire.lean:545–576`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 5.1 | `type` `D/units`: array | `SPEECH_INVALID_DOCUMENT` | `array expected` |
| 5.2 | `type` `D/reading_sets`: array | `SPEECH_INVALID_READING_SET` | `InvalidInput: reading sets on the speech-acts route need their unit, version and status` |
| 5.3 | `type` `D/queries`: array | `SPEECH_INVALID_DOCUMENT` | `array expected` |
| | group `sets` over `D/reading_sets/*` | | |
| · 5.4 | `type` `@`: object | as 5.2 | as 5.2 |
| · 5.5a | `requires` `@` member `unit` | as 5.2 | as 5.2 |
| · 5.5b | `type` `@/unit`: string | as 5.2 | as 5.2 |
| · 5.6a | `requires` `@` member `version` | as 5.2 | as 5.2 |
| · 5.6b | `type` `@/version`: integer | as 5.2 | as 5.2 |
| · 5.7a | `requires` `@` member `status` | as 5.2 | as 5.2 |
| · 5.7b | `enum` `@/status`: `"authored"`, `"open"` | as 5.2 | as 5.2 |
| · 5.8 | hook `version_positive` at `@/version` | `SPEECH_INVALID_SET_VERSION` | `invalid or duplicate reading set version` |
| · 5.9 | `excludes` `@` member `signature`, when `@/status` is `"open"` | as 5.2 | `open reading set cannot have an author signature` |
| · 5.10 | hook `authored_choice_signed` at `@`, when `@/status` is `"authored"` | as 5.2 | `authored reading needs one signed choice` |
| · 5.11 | hook `set_version_unique` at `@` | `SPEECH_INVALID_SET_VERSION` | `invalid or duplicate reading set version` |

Phase 6, `units` (speech-acts.md 3.2; `ve/speech_acts.py:536–609, 697–764`; `Wire.lean:290–407, 455–503, 878`).
One group `units` over `D/units/*`; every row below it up to 6.33 is a sub-entry, so each unit's shape is checked
completely before the next, as both cores decode unit by unit.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · 6.1 | `type` `@`: object | `SPEECH_INVALID_UNIT` | `InvalidInput: speech unit` |
| · 6.2 | `name` `@/id`: `w2_token` | `SPEECH_INVALID_UNIT_ID` | `InvalidInput: speech unit id` |
| · 6.3 | `unique_so_far` `@/id` | `SPEECH_DUPLICATE_UNIT_ID` | `InvalidInput: speech unit id` |
| · 6.4 | classifier `w2_kind` at `@/kind`, when `@/kind` is absent or is not `"binding"`, emits: | | |
| · · 6.4a | the kind is a W2 kind; inherited | `SPEECH_INVALID_KIND` | `{message}` |
| · · 6.4b | the kind nests at most 16 deep; inherited | `SPEECH_RESOURCE_LIMIT` | `{message}` |
| · 6.5 | `excludes` `@` member `content`, when `@/meaning/unformalised` is present | `SPEECH_INVALID_UNIT` | `unformalised unit cannot assert content` |
| · 6.6 | `requires` `@` member `content`, when `@/kind` is `"binding"` | `SPEECH_INVALID_BINDING` | `InvalidInput: invalid binding fields for {id}` |
| · 6.7 | `type` `@/content`: object, same guard | as 6.6 | as 6.6 |
| · 6.8 | `requires` `@/content` member `binding`, same guard | as 6.6 | as 6.6 |
| · 6.9 | `const` `@/kind`: `"binding"`, when `@/content/binding` is present | `SPEECH_MISPLACED_CONTENT` | `InvalidInput: binding content requires binding kind` |
| · 6.10 | hook `binding_entry_shape` at `@/content/binding`, when present | `SPEECH_INVALID_BINDING` | `InvalidInput: invalid binding fields for {id}` |
| · 6.11 | hook `kind_wraps_instruction` at `@/kind`, when C | `SPEECH_MISPLACED_CONTENT` | `InvalidInput: command content requires instruction kind` |
| · 6.12 | `keys` `@/content/command`: required `act`, `args`, `force`; optional `guard`; when C | `SPEECH_INVALID_COMMAND` | `InvalidInput: invalid command fields for {id}` |
| · 6.13 | `enum` `@/content/command/force`: `"forbid"`, `"require"`; when C | `SPEECH_INVALID_FORCE` | `InvalidInput: force` |
| · 6.14 | `type` `@/content/command/act`: string; when C | as 6.12 | as 6.12 |
| · 6.15 | `type` `@/content/command/args`: array of strings; when C | as 6.12 | as 6.12 |
| · 6.16 | classifier `formula_shape` at `@/content/command/guard`, when C and `@/content/command/guard` is present, emits: | | |
| · · 6.16a | the formula has the P0 wire shape; inherited | `SPEECH_INVALID_FORMULA` | `{message}` |
| · · 6.16b | the formula is within its depth and node budget; inherited | `SPEECH_RESOURCE_LIMIT` | `{message}` |
| · 6.17 | hook `kind_is_or_wraps_question` at `@/kind`, when Q | `SPEECH_MISPLACED_CONTENT` | `InvalidInput: question content requires question kind` |
| · 6.18 | `type` `@/content/question`: object; when Q | `SPEECH_INVALID_QUESTION` | `InvalidInput: invalid question fields for {id}` |
| · 6.19a | `requires` `@/content/question` member `mode`; when Q | as 6.18 | as 6.18 |
| · 6.19b | `enum` `@/content/question/mode`: `"follows"`, `"polar"`, `"reading"`, `"which_all"`, `"which_one"`; when Q | as 6.18 | as 6.18 |
| · 6.20a | `exact_keys` `@/content/question`: `body`, `mode`; when Q and `@/content/question/mode` is `"polar"` | as 6.18 | as 6.18 |
| · 6.20b | `exact_keys` `@/content/question`: `body`, `domain`, `mode`, `sort`; when Q and the mode is `"which_all"` | as 6.18 | as 6.18 |
| · 6.20c | the same, when the mode is `"which_one"` | as 6.18 | as 6.18 |
| · 6.20d | `exact_keys` `@/content/question`: `mode`, `query`; when Q and the mode is `"follows"` | as 6.18 | as 6.18 |
| · 6.20e | `exact_keys` `@/content/question`: `mode`, `set`, `version`; when Q and the mode is `"reading"` | as 6.18 | as 6.18 |
| · 6.21 | classifier `formula_shape` at `@/content/question/body`, when Q and `@/content/question/body` is present, emits 6.21a and 6.21b as 6.16a and 6.16b | | |
| · 6.22 | `type` `@/content/question/sort`: string; when Q and `@/content/question/domain` is present | as 6.18 | as 6.18 |
| · 6.23 | `type` `@/content/question/domain`: array of strings; same guard | as 6.18 | as 6.18 |
| · 6.24 | `type` `@/content/question/query`: string; when Q and it is present | as 6.18 | as 6.18 |
| · 6.25 | `type` `@/content/question/set`: string; when Q and it is present | as 6.18 | as 6.18 |
| · 6.26 | `type` `@/content/question/version`: integer; when Q and it is present | as 6.18 | as 6.18 |
| · 6.27 | hook `kind_wraps_norm` at `@/kind`, when N | `SPEECH_MISPLACED_CONTENT` | `InvalidInput: norm content requires norm kind` |
| · 6.28 | hook `w1_norm_unit` at `@/content`, when N; inherited | `SPEECH_INVALID_NORM` | `{message}` |
| · 6.29a | `type` `@/content`: array or object; when F and `@/kind` is `"asserted"` | `SPEECH_INVALID_CONTENT` | `InvalidInput: asserted content` |
| · 6.29b | the same, when F and `@/kind` is absent or is not `"asserted"` | as 6.29a | `InvalidInput: misplaced speech content` |
| · 6.30a | `exact_keys` `@/content`: `ast`; when F, `@/content` is an object and `@/kind` is `"asserted"` | as 6.29a | `InvalidInput: asserted content` |
| · 6.30b | the same, when `@/kind` is absent or is not `"asserted"` | as 6.29a | `InvalidInput: misplaced speech content` |
| · 6.31 | classifier `formula_shape` at `@/content/ast`, when F and `@/content/ast` is present, emits 6.31a and 6.31b as 6.16a and 6.16b | | |
| · 6.32 | classifier `formula_shape` at `@/content`, when F and `@/content` is an array, emits 6.32a and 6.32b as 6.16a and 6.16b | | |
| · 6.33 | `declared_in` `@/id`: `D/reading_sets/*/unit`; when `@/kind` is `"asserted"` and `@/content` is absent | `SPEECH_INVALID_UNIT` | `asserted unit needs content or a reading set` |
| | group `set-units` over `D/reading_sets/*` | | |
| · 6.34 | `declared_in` `@/unit`: `D/units/*/id` | `SPEECH_INVALID_READING_SET` | `invalid reading set unit or status` |

Phase 7, `bindings` (speech-acts.md 1.1; `ve/speech_acts.py:362–414`; `Wire.lean:699–728, 884–892`). One group
`binding-units` over `D/units/*`, with the guard `[present @/content/binding]`; each binding unit is checked
completely before the next, in document order, as both cores merge.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · 7.1 | hook `binding_task_token` at `@/content/binding/task`, when present | `SPEECH_INVALID_BLOCK` | `InvalidInput: speech_acts block` |
| · 7.2a | hook `constant_declared` at `@/content/binding/you`, when present | `SPEECH_UNKNOWN_CONSTANT` | `UnknownSymbol: {value}` |
| · 7.2b | hook `constant_declared` at `@/content/binding/constant`, when present | as 7.2a | as 7.2a |
| · 7.3 | hook `binding_not_duplicate` at `@`, returns `entry` | `SPEECH_DUPLICATE_BINDING` | `DuplicateDeclaration: binding {entry}` |
| · 7.4 | hook `binding_consistent` at `@`, returns `entry` | `SPEECH_BINDING_CONFLICT` | `BindingConflict: {entry}` |

Phase 8, `references` (speech-acts.md 3.2, 4.1; `ve/speech_acts.py:697–764, 848–854`; `Tree.lean:265–305`;
`Wire.lean:781–806, 900–921`). One group `refs` over `D/units/*`; each unit's references are checked completely
before the next.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| · 8.1 | hook `act_declared` at `@/content/command/act`, when C | `SPEECH_UNKNOWN_PREDICATE` | `UnknownSymbol: regulated predicate {value}` |
| · 8.2a | hook `act_role_obligation` at `@/content/command/act`, when C and `@/content/command/force` is `"require"`; returns `act` | `SPEECH_MISSING_ROLE` | `MissingObligationRole: {act}` |
| · 8.2b | hook `act_role_permission` at the same, when C and the force is `"forbid"`; returns `act` | as 8.2a | `MissingPermissionRole: {act}` |
| · | group `args` over `@/content/command/args/*`, when C | | |
| · · 8.3 | hook `constant_declared` at `@` | `SPEECH_UNKNOWN_CONSTANT` | `UnknownSymbol: {value}` |
| · 8.4 | hook `args_fit_slots` at `@/content/command/args`, when C | `SPEECH_TYPE_MISMATCH_ARGS` | `TypeMismatch: command args for {id}` |
| · 8.5 | classifier `formula_typing` at `@/content/command/guard`, when C and present, emits: | | |
| · · 8.5a | the formula names declared predicates, constants and binder sorts; inherited | `SPEECH_UNKNOWN_SYMBOL` | `{message}` |
| · · 8.5b | the formula is well typed; inherited | `SPEECH_TYPE_MISMATCH` | `{message}` |
| · · 8.5c | every variable index is in scope; inherited | `SPEECH_UNBOUND_VARIABLE` | `{message}` |
| · 8.6 | hook `addressee_bound` at `@` | `SPEECH_UNBOUND_SLOT` | `UnboundSlot: you` |
| · 8.7 | hook `addressee_sort_fits` at `@` | `SPEECH_TYPE_MISMATCH_ADDRESSEE` | `TypeMismatch: addressee` |
| · 8.8 | classifier `formula_typing` at `@/content/question/body`, when Q and `@/content/question/mode` is `"polar"`, emits 8.8a to 8.8c as 8.5a to 8.5c | | |
| · 8.9 | hook `sort_declared` at `@/content/question/sort`, when Q and `@/content/question/domain` is present | `SPEECH_UNKNOWN_SORT` | `UnknownSymbol: sort {value}` |
| · 8.10 | `max_items` `@/content/question/domain`: `MAX_ALTERNATIVES`; same guard | `SPEECH_RESOURCE_LIMIT` | `ResourceLimit: alternatives` |
| · 8.11 | hook `at_least_two_alternatives` at `@/content/question/domain`; same guard | `SPEECH_INVALID_QUESTION` | `InvalidInput: invalid question fields for {id}` |
| · | group `alternatives` over `@/content/question/domain/*`, when Q | | |
| · · 8.12 | hook `constant_declared` at `@`; `{id}` is `@1/id` | `SPEECH_UNKNOWN_ALTERNATIVE` | `UnknownAlternative: {id}, {value}` |
| · · 8.13 | hook `alternative_of_sort` at `@`; `{id}` is `@1/id` | `SPEECH_ALTERNATIVE_SORT` | `AlternativeSort: {id}` |
| · | group `alternatives-distinct` over `@/content/question/domain/*`, when Q | | |
| · · 8.14 | `unique_so_far`; `{id}` is `@1/id` | `SPEECH_DUPLICATE_ALTERNATIVE` | `DuplicateAlternative: {id}, {value}` |
| · 8.15 | classifier `formula_typing_in_sort` at `@/content/question/body`, when Q and `@/content/question/domain` is present, emits 8.15a to 8.15c as 8.5a to 8.5c | | |
| · 8.16 | hook `reading_set_version_exists` at `@/content/question`, when Q and `@/content/question/set` is present | `SPEECH_INVALID_QUESTION` | `InvalidInput: invalid question fields for {id}` |
| · 8.17 | hook `reading_meaning_is_open_term` at `@/meaning`, when Q, `@/content/question/set` is present and `@/kind` is `"question"` | as 8.16 | as 8.16 |
| · 8.18 | `max_bytes` `@/id`: `MAX_OPEN_TERM_UNIT_BYTES`; when Q and `@/content/question/set` is present | `SPEECH_RESOURCE_LIMIT` | `ResourceLimit: open-term name` |
| · 8.19 | hook `w1_quoted_norm` at `@/content`, when N and `@/kind` is absent or is not `"norm"`; inherited | `SPEECH_INVALID_NORM` | `{message}` |
| · 8.20 | classifier `formula_typing` at `@/content/ast`, when F and present, emits 8.20a to 8.20c as 8.5a to 8.5c | | |
| · 8.21 | classifier `formula_typing` at `@/content`, when F and `@/content` is an array, emits 8.21a to 8.21c as 8.5a to 8.5c | | |

Phase 9, `candidates` (speech-acts.md 6; `ve/speech_acts.py:646–695`; `Wire.lean:734–753, 811–845, 930–931`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| | group `sets` over `D/reading_sets/*` | | |
| · 9.1a | `requires` `@` member `readings` | `SPEECH_INVALID_READING` | `reading sets hold 1 to 64 readings` |
| · 9.1b | `type` `@/readings`: array | as 9.1a | as 9.1a |
| · 9.2 | `max_items` `@/readings`: `MAX_READINGS` | as 9.1a | as 9.1a |
| · 9.3 | hook `at_least_one_reading` at `@/readings` | as 9.1a | as 9.1a |
| · | group `readings` over `@/readings/*` | | |
| · · 9.4 | `type` `@`: object | as 9.1a | `invalid reading` |
| · · 9.5a | `requires` `@` member `kind` | as 9.1a | `invalid reading` |
| · · 9.5b | `requires` `@` member `content` | as 9.1a | `invalid reading` |
| · · 9.6 | classifier `w2_kind` at `@/kind`, when `@/kind` is absent or is not `"binding"`, emits 9.6a and 9.6b as 6.4a and 6.4b | | |
| · · 9.7 | classifier `reading_candidate` at `@`, when `@/content` is absent or is not `null`; `{id}` is `@1/unit`; emits the members below | | |

The members of 9.7, in this order, are `c0.1` and one member `c<k>` for each `k` among 6.10, 6.12, 6.13, 6.14,
6.15, 6.16a, 6.16b, 6.18, 6.19a, 6.19b, 6.20a to 6.20e, 6.21a, 6.21b, 6.22 to 6.26, 6.28, 6.31a, 6.31b, 7.1,
7.2a, 7.2b, 8.1, 8.2a, 8.2b, 8.3, 8.4, 8.5a to 8.5c, 8.8a to 8.8c, 8.9 to 8.14, 8.15a to 8.15c, 8.16, 8.18,
8.19, 8.20a to 8.20c (fifty-five members; an array content is read as `{"ast": …}`, so 6.31 stands for 6.32 and
8.20 for 8.21). `c0.1` has the code `SPEECH_INVALID_READING` and the text `invalid speech reading
content`; its `says` is in 3.1. Each `c<k>` has the code, the text and the `says` of check `k`, with `{id}`
the set's `unit` and every other placeholder returned by the classifier, and its `says` is prefixed as 3.1 states.
A member mirroring an inherited member is inherited. The classifier's function (2.4) runs the mirrored checks on
the reading, as the unit would be were the reading chosen, in the table's order; the order key of a fault for
`c<k>` is the position of `k` in the unit table, so the oracle of tiers 0 and A follows the member list.

Phase 10, `queries` (speech-acts.md 1.4, 3.2; `ve/speech_acts.py:445–460, 620, 766–795`; `Wire.lean:686–694,
923–943`; `Tree.lean:282`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 10.1 | hook `questions_fit` at `D/units` | `SPEECH_RESOURCE_LIMIT` | `ResourceLimit: questions` |
| | group `records` over `D/queries/*` | | |
| · 10.2 | `exact_keys` `@`: `id`, `premises`, `target` | `SPEECH_INVALID_QUERY` | `InvalidInput: query` |
| · 10.3 | `type` `@/id`: string | as 10.2 | as 10.2 |
| · 10.4 | `type` `@/premises`: array of strings | as 10.2 | as 10.2 |
| · 10.5 | `exact_keys` `@/target`: `ast` | as 10.2 | as 10.2 |
| · 10.6 | classifier `formula_shape` at `@/target/ast`, emits 10.6a and 10.6b as 6.16a and 6.16b | | |
| · 10.7 | classifier `formula_typing` at `@/target/ast`, emits 10.7a to 10.7c as 8.5a to 8.5c | | |
| | group `record-ids` over `D/queries/*` | | |
| · 10.8 | `unique_so_far` `@/id` | `SPEECH_DUPLICATE_QUERY` | `InvalidInput: duplicate query` |
| | group `asking-units` over `D/units/*` | | |
| · 10.9 | hook `asks_regenerated_query` at `@` | `SPEECH_QUERY_MISMATCH` | `QueryMismatch: {id}` |
| | group `consumed` over `D/queries/*` | | |
| · 10.10 | hook `query_consumed` at `@/id` | `SPEECH_QUERY_MISMATCH` | `QueryMismatch: {value}` |

Phase 11, `policy` (speech-acts.md 4.2, 7; `ve/speech_acts.py:637–640`; `Tree.lean:308–311`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 11.1 | hook `no_command_over` at `D/units`, returns `rule` | `SPEECH_UNKNOWN_RULE` | `UnknownRule: rule {rule}` |
| 11.2 | hook `w1_policy` at `D/units`; inherited | `SPEECH_INVALID_POLICY` | `{message}` |

**What is not in the table, and why.** The wrapper's checks (2.2, the domain); the clash of a definite phrase,
or of a phrase a binding unit binds, with a declared constant's or sort's name or a reserved word
(`ve/speech_acts.py:52–55, 380`; `Wire.lean:152–156, 721–723`): both validators check it and it cannot fail,
because a phrase that passes 2.10 contains a space and no declared name does (`ve/environment.py:29`), so it
would have no first-fault witness; the wordings (`_check_wordings`,
`ve/speech_acts.py:809–836`; the English layer is outside the base plan); Lean's `ResourceLimit: unit count`
(`Wire.lean:876`; Python has no check: S6-pre, 2.11); Lean's `ill-typed asserted unit` and `speech-act document
is not well-formed` (`Tree.lean:307, 323`; unreachable after the checks above, a residual if reached); Lean's
`invalid or duplicate reading set version` for a negative version (the restricted wire readers refuse negative
numbers, base spec 2.1); Python's restricted-subset check of the environment (`ve/environment.py:316`; the JSON
layer, base plan row 2). Where the spec's "Order" paragraph puts the queries after the policy, the table puts
them before it: both validators decode, deduplicate and regenerate the query records before W1's check of the
policy (`ve/speech_acts.py:622, 637`; `Wire.lean:923–943, 947`), and the paragraph is prose, not a numbered table
(base plan 5.1, step 1; 3.3).

**Planned tiers.** 115 numbered checks: T1 64 (1.1 to 1.10; 2.1 to 2.9; 4.4; 5.1 to 5.7, 5.9; 6.1 to 6.3, 6.5 to
6.9, 6.12 to 6.15, 6.18 to 6.20, 6.22 to 6.26, 6.29, 6.30, 6.33, 6.34; 8.10, 8.14, 8.18; 9.1, 9.2, 9.4, 9.5; 10.2
to 10.5, 10.8); T2 not inherited 33 (2.10; 4.1 to 4.3, 4.5; 5.8, 5.10, 5.11; 6.10, 6.11, 6.17, 6.27; 7.1 to 7.4;
8.1 to 8.4, 8.6, 8.7, 8.9, 8.11 to 8.13, 8.16, 8.17; 9.3; 10.1, 10.9, 10.10; 11.1); inherited 17 (3.1; 6.4,
6.16, 6.21, 6.28, 6.31, 6.32; 8.5, 8.8, 8.15, 8.19 to 8.21; 9.6; 10.6, 10.7; 11.2); T3 not inherited 1 (9.7).
`n1 + n2` is 97 of 115. The base spec's threshold was the pilot's; for a new unit the gate reports the counts and
requires none (S5 spec 12, R9).

### 2.4 The hooks and classifiers, in both languages

Rules of base spec 2.5 apply: a hook reads its two arguments only, may assume every earlier instance holds, and
is required to agree across languages only on such inputs. Lean's hooks call frozen functions read-only
(`VE.SpeechActs.Wire`, `VE.SpeechActs.Tree`, `VE.Norms.Wire`, `VE.Norms.Tree`, `VE.Route.Admission`,
`VE.Bridge`), on one environment, one unit, one reading or one formula; none calls `decodeDocument` or
`validateSpeech` on the whole document. Two notions recur:

- **The effective unit.** A unit as its latest reading set leaves it: a unit named by no set, or by one whose
  latest version is `open`, is itself (and in the second case **pending**); a unit named by a set whose latest
  version is `authored` has the choice's `kind` and `content`, and the meaning `specified`, except that a chosen
  reading question means its derived open term (`_reading_choice`, `ve/speech_acts.py:232–251`; `chosenUnit`,
  `Wire.lean:651–657`). In the domain a set's unit is `asserted` without content (2.2), so only the hooks that
  read behaviour (8.6, 8.7, 10.1, 10.9, 11.1, 11.2) read the effective unit; every T1 check reads the wire.
- **An active command** is an effective unit whose `kind` is exactly `instruction`, whose `meaning` is
  `specified` and which is not pending (`ve/speech_acts.py:568–569`; `Wire.lean:508–511`). An **active norm** is
  an effective unit of kind exactly `norm`, not pending. A **fixed assertion** is an effective unit of kind
  `asserted` with content, not pending.
- **The merged scope** is the block with the bindings of the binding units merged in document order
  (`_merge_bindings`; `mergeBindings`); it is read only after phase 7 holds.

| Name | Python (`ve/speech_acts_contract.py`) | Lean (`Hooks/SpeechActs.lean`) |
|---|---|---|
| `definite_phrase` (2.10) | the key of the item matches `ve.speech_acts._PHRASE` and is at most 80 bytes in UTF-8 | `Wire.phraseOk` on the key |
| `w1_environment` (3.1, inherited) | `Environment(e)` on the environment with `speech_acts` removed and `speech-acts@0` removed from `profiles`, as `ve/norms.py:440–443` strips it; a `VEError` is the message | `Norms.Wire.decodeNormsEnvironment` on `Wire.stripSpeech` of the environment; the error is the message |
| `template_slots_apart` (4.1) | `ve.speech_acts.check_templates` over the decoded predicates | `Wire.checkTemplates` over the predicates and the regulated declarations of the W1 environment |
| `sort_declared` (4.2, 8.9) | the value is a key of `E/vocabulary/sorts` | the same |
| `addressee_constant_of_sort` (4.3) | the value is a key of `E/vocabulary/constants` whose `sort` is `S/addressee/sort` | the same |
| `constant_declared` (4.5, 7.2, 8.3, 8.12) | the value is a key of `E/vocabulary/constants` | the same |
| `version_positive` (5.8) | the value is at least 1 | the same |
| `authored_choice_signed` (5.10) | `readings` is an array of exactly one object with the members `kind` and `content`, and `signature` is a `w2_token` | the same (`Wire.readingStates`, the `authored` arm; `Wire.signed`) |
| `set_version_unique` (5.11) | no earlier item has the same `unit` and `version` | the same |
| `w2_kind` (6.4, 9.6) | `ve.admission._check_kind(kind)`; a `ResourceLimit` is member b, any other `VEError` member a | `Route.Admission.decodeKind 16`; a failure whose leading word is `ResourceLimit` is member b, any other is member a |
| `binding_entry_shape` (6.10) | the value is an object that is exactly `{"you": c}`, `{"task": t}` or `{"phrase": p, "constant": c}` with string values, and `p` passes `definite_phrase` (`_binding_entry`'s shape test) | `Wire.decodeBinding` succeeds |
| `kind_wraps_instruction` (6.11), `kind_wraps_norm` (6.27) | `ve.speech_acts._wraps(kind, "instruction")`, `_wraps(kind, "norm")` | `Wire.wraps (decodeKind 16 kind) .instruction`, `.norm` |
| `kind_is_or_wraps_question` (6.17) | the kind is `question` or `_wraps(kind, "question")` | `k == .question \|\| wraps k .question` |
| `formula_shape` (6.16, 6.21, 6.31, 6.32, 10.6) | `ve.speech_acts.formula_shape(v)`; then the node count of `v`, counted as `VE.Bridge.formulaNodes` counts (one per formula node, one per term), is at most 10,000. A `ResourceLimit` is member b, any other `VEError` member a; the message is the exception's text | `Wire.decodeBudgetFormula v`; a failure whose leading word is `ResourceLimit` is member b, any other is member a |
| `w1_norm_unit` (6.28, inherited) | `ve.speech_acts._norm_shapes(content)` then `NormDocument._decode(content)`; a `VEError` is the message | `Wire.decodeBudgetNorm content` |
| `binding_task_token` (7.1) | the value matches `_TOKEN` | `Route.Admission.token` |
| `binding_not_duplicate` (7.3) | no earlier binding unit binds the same entry (`you`, `task`, or the phrase); returns the entry | the same |
| `binding_consistent` (7.4) | the entry's value equals the block's value for it, when the block has one (`task` always, `you` when the block has an addressee, a phrase when the block defines it); returns the entry | `Wire.mergeBindings` over the block and the earlier bindings does not fail with `BindingConflict` |
| `act_declared` (8.1) | the value is a key of `P` | the same |
| `act_role_obligation`, `act_role_permission` (8.2) | the act's declaration has `regulated` with `role` `obligation` (`permission`); returns `act`: the declaration's normalised act phrase, or the predicate name when it has none | the same, over `Regulated.act` |
| `args_fit_slots` (8.4) | the constants named by `args`, in order, have the declared sorts of the act's predicate after the first | `Tree.constsTyped E args r.sorts.tail` with `E.predicates act == some r.sorts` |
| `formula_typing` (8.5, 8.8, 8.20, 8.21, 10.7), `formula_typing_in_sort` (8.15) | `ve.ast.formula_from_data(Environment(e), v)` in context `()`; for 8.15, `_Decoder().decode(v)` then `_Checker(env).formula(body, (sort,))` with `sort` the question's `sort`. The exception's class names the member: `UnknownSymbol` a, `TypeMismatch` b, `UnboundVariable` c; any other class names no member | `Norms.typeDiagnostic E [] φ` (for 8.15, `[sort]`) on the formula `decodeBudgetFormula` returns; the leading word names the member |
| `addressee_bound` (8.6) | when the effective unit is an active command: the merged scope has an addressee | the same |
| `addressee_sort_fits` (8.7) | when the effective unit is an active command: the addressee's sort is the first declared sort of the act's predicate | the same |
| `at_least_two_alternatives` (8.11) | the array has at least 2 members | the same |
| `alternative_of_sort` (8.13) | the constant's declared sort is the question's `sort` | the same |
| `reading_set_version_exists` (8.16) | `version` is at least 1 and some set has `id` equal to `set` and `version` equal to `version` | `Wire.readingSetKeys` contains the pair and `1 ≤ version` |
| `reading_meaning_is_open_term` (8.17) | the value equals `{"open": ["intended-reading.<id>"]}` | the same |
| `w1_quoted_norm` (8.19, inherited) | `ve.norm_admission._check_quoted(Environment(e), content)`; a `VEError` is the message | `Norms.validate` on a one-rule document with the rule's `over` emptied, as `Wire.lean:916–918` |
| `at_least_one_reading` (9.3) | the array is not empty | the same |
| `reading_candidate` (9.7) | the reading's `content`: an array is read as `{"ast": …}`; otherwise it is an object with exactly one member, else `c0.1`; `ve.speech_acts.content_kind_ok(kind, tag)` else `c0.1`; then the checks of 2.3 that apply to a unit of that kind and content, in table order, over the set's `unit` as `{id}`, returning the first mirrored member that fails with its arguments | `Wire.checkCandidate`'s shape and `contentKindOk` tests for `c0.1`; then the same mirrored checks, by the Lean functions of this table, in table order |
| `questions_fit` (10.1) | the effective units of kind exactly `question` with question content are at most 256 | the same |
| `asks_regenerated_query` (10.9) | for each query the effective unit asks about (a `follows` question's `query`, the argument of sort `query` of a command's act, then the same of each reading of a set naming the unit, in set order): some record has that `id` and its `premises` are exactly the ids of the fixed assertions before the unit, in document order (`SpeechDocument._queries`) | the same, as `Wire.lean:932–940` |
| `query_consumed` (10.10) | some effective unit or reading asks about the record's `id` (the same enumeration) | the same, as `Wire.lean:942–943` |
| `no_command_over` (11.1) | no active norm's `over` names `cmd-<id>` for the `id` of an active command; returns `rule`, the name | the same (`Tree.noCommandOver`) |
| `w1_policy` (11.2, inherited) | `NormDocument(Environment(e′), [*norms, *demands])` with `e′` the environment under the merged scope, `norms` the active norms decoded by `NormDocument._decode` and `demands` `SpeechDocument.demand` of each active command, in document order; a `VEError` is the message | `Norms.validate (policy D)` over the `SpeechDoc` built as `decodeDocument` builds it from the units that hold; the error is the message |

### 2.5 Shadow and public

As S4 spec 2.2. While `status` is `shadow`, no output of any program depends on the contract. When it is
`public`, exactly one output depends on it: the error that the call site of 2.7 raises. Nothing in Lean reads
`status`. Changing `status` is a contract edit and raises the revision; today's output is restored by reverting
the switch commit or by a later revision that sets `status` to `shadow`.

### 2.6 The boundary function

```
ve.speech_acts_contract.public_rejection(environment, document, error, *, contract=None, registry=None)
```

It is the S4 spec's 2.3 for this unit, step for step: return at once if `error.diagnostic` is set or the locked
contract's `status` is not `public`; the root is `{"environment": e, "document": d}` with deep copies of the
arguments; `outcome` is `engine.run(contract, root, registry=REGISTRY)`; `record` is `engine.overlay(contract,
error, outcome)` with no Lean argument; set `error.diagnostic`, `error.message` and `error.args` so that
`message` and `str(error)` are the record's `text`; return `error`. The **failure rule** holds: if loading the
contract or any step raises an `Exception`, the function returns `error` as it received it. It never writes
`error.code`, `error.path` or `error.span`, never creates an error, never calls the legacy validator on the
source itself (the hooks of 2.4 call parts of it), and starts no Lean process.

By the overlay, the reported record is the fault record, the residual record (whose `text` is the legacy text),
or the deferred record `{"contract", "revision", "deferred": id, "text"}` with the legacy text. The Python
registry is complete, so the gate's deferred count in Python is 0 and must stay 0.

### 2.7 The call site

In `ve/speech_document.py`, `SpeechSource.__init__(self, meta, source, fences)` decodes the environment (`:144`),
requires the profile (`:145–146`), validates the source bytes, the unit envelopes and spans, the fences, the open
terms, the reading sets and the narrowings (`:147–244`), and then builds the core by one statement,
`self.document = SpeechDocument(self.env, self.units, meta.get("queries", []), reading_sets=sets)` (`:245`). The
switch wraps that one statement in one handler: a `VEError` it raises is passed to
`public_rejection(self.env.to_dict(), {"units": self.units, "queries": meta.get("queries", []), "reading_sets":
sets}, error)`, and the returned error is raised. The import of `public_rejection` is a statement inside the
handler. Nothing else in the file changes. An error from any earlier statement, and from the meaning-id, status,
open-term, answer and compliance checks after it (`:246–294`), keeps today's text and has no record.

**The root at the call site.** `environment` is `self.env.to_dict()`, because the environment reaches the
statement as an `Environment` object; the checks of phases 1 to 4 read `profiles`, `speech_acts` and the
`vocabulary` members, which `to_dict()` reproduces as submitted (`ve/environment.py:640–664`). Phases 1 to 4
cannot fail at the call site: the same decoder accepted the same environment at `:144`, and `:145` required the
profile. `document.units` is `self.units`, the wrapper's units: each carries the five envelope members and
`content`, plus `source` for every `instruction` or `question` unit (`:192`), `parent_id` for a nested unit
(`:193`), and `surface`, `status` or `meaning_id` when the source had them. Those four members are outside the
domain (2.2) and no check of the table names them (V4). The reading sets and the queries are the source's own.

Four properties follow from this shape and are tested (8.3), not proved:

- **(V1) The verdict is the legacy validator's.** The call site raises exactly when the statement raises, and
  raises the same object: same type, same `code`. The handler ends in a `raise` on every path.
- **(V2) An accepted source does not reach the engine.** On an input the statement accepts, neither
  `ve.speech_acts_contract` nor `ve.wire_contract` is imported by this call.
- **(V3) The engine and the legacy validator read the same source.** The root's `units`, `queries` and
  `reading_sets` are the objects the statement received, and its `environment` is the dictionary of the
  `Environment` the statement received; the statement modifies none of them (fixture Z5).
- **(V4) The engine reads no member outside the domain.** On every corpus case, the record is the same whether
  the units carry `source`, `parent_id`, `surface`, `status` and `meaning_id` or not (fixture G13).

**The import rule** of base spec 7.3 and the S5 spec's 2.8 gains one row: inside `ve/`, outside
`ve/wire_contract/` and the contract modules, `ve.speech_acts_contract` is imported only by
`ve/speech_document.py`, which imports the one name `public_rejection` in one import statement and one call, both
inside one `except VEError` handler of `SpeechSource.__init__`, the call being the operand of a `raise`; no
module imports `ve.wire_contract`. The scan of `tests/test_softnorms_contract.py` gains the row, with the S4
spec's resolution of relative imports. The Lean import rule is unchanged.

### 2.8 Entry points: switched, and not switched

| Entry point | After the switch |
|---|---|
| `ve.speech_document.SpeechSource(meta, source, fences)`, reached from `load_speech_document` and `python -m ve speech-acts <path>` (`ve/__main__.py:112–120`) | **public**: an error of the statement of 2.7 carries the reported record |

Not switched; each keeps today's message and has no record:

| Entry point | Why not in item 1 |
|---|---|
| the wrapper's statements before and after 2.7 (`ve/speech_document.py:140–244, 246–294`) | the unit `ve-document@2` (base plan 5.3, row 14) and the W2 envelope |
| `SpeechDocument(…)` built directly, `combine`, `effective_scope` (`ve/speech_acts.py:485, 1022, 1044`) | base spec section 10, item 7; and the core must stay the legacy validator the gate calls |
| the three-way tests' `core`, `elaborate` and `run1` | test harnesses over the two legacy validators |
| every Lean row; every Rust output | base plan 2.5; the route is frozen; Rust has no column |

The tolerance of row 8, `tests/test_speech_acts_conformance.py:1856–1871`, asserts that both validators reject
the two reproducers and compares nothing else; it keeps both assertions, its comment is reworded to say that
the contract fixes the first diagnostic and that the gate compares the record of both engines on these inputs
(fixtures E40, E41), and the gate compares every text of the unit at zero tolerance (section 9).

### 2.9 The contract edits

Revision 1 is the shadow one of 2.3. The shadow may edit it; the switch is one further revision, written `R` in
sections 4 and 8, whose only differences from the revision before it are `"revision": R` and `"status":
"public"`. What follows mechanically, by `tools/wire_contract.py --write`: `contracts.lock`'s entry;
`lean/VE/WireContract/Tables/SpeechActs.lean`'s header comment and the numeral of `revision`, and nothing else,
with the module's line in `VE/Route/frozen-sources.sha256`; `docs/spec/speech-acts-wire-table.md`: no change is
expected (it states no revision); `--check` decides. The contract includes nothing, so no other table changes.
Every record of either engine then has the new `revision`, so the stored reports that hold records are
regenerated (gate, golden, catalogue, delta).

### 2.10 A public change, and the two-sided delta

As S4 spec 2.7. For a corpus case on which the Python core raises a legacy error with code `c` and text `m`, let
`r` be the reported record: `engine.overlay(contract, error, engine.run(contract, root, registry=REGISTRY))`.
The case has a **text change** when `r`'s `text` is not `m`; a **class difference** when `r` has a `class` and
it is not `c`; it is **attributed** to `r`'s `check` (an id, or `residual`), or to `deferred`. Every check
counts, inherited ones too. A case the core accepts has no public change.

A rejected case is **handler-reaching** when the call on the wrapper (section 8) reaches the statement of 2.7,
so that the error it raises is that statement's: the environment decodes and lists `speech-acts@0`, and no
statement of the wrapper before `:245` raises. From reading, those are the rejected cases whose environment
decodes, whose unit envelopes and spans the wrapper accepts, and whose reading sets pass the wrapper's
`_reading_sets` (`:30–122`), which is stricter than the core on shape (it requires W2's reading ids, meaning ids
and admission records) and so makes most faults of phases 5 and 9 unreachable at the call site. On any other
rejected case the call raises today's error from an earlier statement, with no record; the record `r` of such a
case is a result of the engine and of the boundary function, and is never public.

The **delta report** `conformance/wire-contract/speech-acts@0-delta.json` has two sides:

- `public_diagnostic_changes`: for each check with at least one text change or class difference on a
  handler-reaching case, in table order, the number of those cases with a text change, the number with a class
  difference, and one example; computed over the handler-reaching cases of the whole corpus and stored.
- `lean_route_changes`: for each check, the number of corpus cases that Lean reads and rejects on which the Lean
  route's text differs from the record's `text`, with one example, and, named separately, the two reproducers of
  speech-acts.md 884–888 with the route's text, Python's legacy text and the record's text side by side.

`--check` compares the stored file with regeneration. The first side is signed; the second is reported and not
enforced (plan, decision 3).

The **signing file** `conformance/wire-contract/speech-acts@0-switch.json` is written by hand, as the pilot's:
`signed` gives each check whose text may change one sentence saying what changes; `release_note` is the text of
3.4 with the list filled in. A class difference cannot be signed (2.11).

### 2.11 The class rule, and S6-pre

**The class rule.** On every corpus case where the reported record is a fault, the record's `class` is the
legacy code, except on the exempt checks:

- 3.1, 6.28, 8.19, 11.2: one inherited code for a decoder or validator that raises several classes
  (`Environment`, `NormDocument._decode`, `_check_quoted`, `NormDocument`).
- 1.1: Python's `require_fields` raises a plain `VEError` where the code's class is `UnsupportedProfile`.

Each exemption is listed in section 10, and the gate counts the cases it covers. The rule is checked on every
rejected case of the corpus, handler-reaching or not: it is a property of the engine's record.

The rule holds by construction of the Python side for every check that is not inherited (the code's class is the
class Python raises, 2.3), for the `w2_kind` and `formula_shape` members (each is keyed by the class Python
raises) and for the typing members (keyed by class). For the Lean engine it holds by the hand-written members of
`Hooks/SpeechActs.lean`, tested in tiers 0 and A. A Lean text whose leading word names no member makes the Lean
classifier answer `ok`, which shows as an engine mismatch, never as a silent class.

**S6-pre** blocks the switch. The shadow gate lists every corpus case on which the Python core and the Lean route
disagree on the verdict (`legacy_verdict_differences`). Each is treated as a class and run to ground, as S3-pre,
S4-pre and S5-pre were, outside this work, and recorded in `conformance/wire-contract/s6-pre.md`; closed means
the gate reports the list empty, and the gate fails otherwise. From reading, the candidates are:

| Candidate | Python | Lean |
|---|---|---|
| more than 10,000 units | no check | `ResourceLimit: unit count` (`Wire.lean:876`) |
| an environment outside the restricted JSON subset (size, Unicode), passed in process | `canonical_json` rejects (`ve/environment.py:316`) | the case parser `VE.JsonInput.parseCases` decides; not known from reading |
| a `functional` or `total` flag without `data@0` | `Environment` rejects with `Predicate flags require data@0` (`ve/environment.py:400–402`) | rejects with `with data flags` (`Wire.lean:143–144`); both reject, the texts differ: not a verdict difference, measured as a text change of 1.9 and 1.10, never handler-reaching |

A verdict difference is fixed outside this plan, in Python first where Python's verdict changes. Class
differences between the two legacy validators are not S6-pre's: they are recorded in `lean_route_changes` and
the contract keeps Python's classes (D3).

### 2.12 What is constructed and what is tested

By construction:

- **(A) The public record is the measured one.** The call site reports `overlay(run(…))` through
  `public_rejection`, and the gate measures the delta with the same two functions on the same registry.
- **(B) In Lean only the generated table's revision changes at the switch.** The engine reads a table's phases
  only, and revision `R` has the phases of the revision before it (T3, L4).
- **(C) The base spec's claims (A) and (B)** hold: the expansion, and the record conditional on equal predicate
  results. The contract has no scope, so every `path` is the plain pointer of the target.
- **(D) The class rule, on the Python side, for the checks of 2.11.**

Tested, not constructed:

- that each engine reports a fault exactly when its legacy validator rejects, on the corpus, at zero tolerance,
  and that the Lean classifier members agree with Python's, the fifty-five of 9.7 among them;
- that the signed list is complete: on the corpus only;
- that Python's public text equals the text of Lean's `ve_diagnose` record: on every corpus case that Lean reads,
  for checks that are not inherited;
- V1 to V4 of 2.7.

Not claimed: that the Lean route's own text on a multi-fault document is the record's, nor that Python's legacy
text is (D2). The table's order is the spec's; on a document with one fault the two validators and the table
agree on the fact, and the record's text equals the route's where the texts agree (section 6).

## 3. English: one reading each

### 3.1 The hand-written sentences

The generated wordings of base spec 3.1 cover every T1 row of the table; `tools/wire_contract.py` writes them to
`docs/spec/speech-acts-wire-table.md`. The hooks and members carry these `says` sentences. "The item" is the
innermost group's item, which the generated lead names (`For the `units` item: `); "the enclosing item" is the
group one level out. Each string is exactly as shown, backticks included.

```json
{"2.10": "The key of the item is a definite phrase: the word `the`, then one or more words, the words separated by single spaces, each word a letter followed by letters, apostrophes and hyphens, and the whole key at most 80 bytes long in UTF-8.",
 "3.1":  "W1's environment decoder accepts `/environment` with `speech_acts` removed and `speech-acts@0` removed from `/environment/profiles`.",
 "4.1":  "In every regulated act phrase and in every `verbalisation` and `negative_verbalisation` of `/environment/vocabulary/predicates`, each slot `{n}` begins the template or follows ASCII whitespace or an ASCII punctuation character other than `'`, `-`, `_`, `{` and `}`, and ends the template or precedes one.",
 "4.2":  "`/environment/speech_acts/addressee/sort` is the name of a declared sort.",
 "4.3":  "`/environment/speech_acts/addressee/constant` is the name of a declared constant whose sort is `/environment/speech_acts/addressee/sort`.",
 "4.5":  "The item is the name of a declared constant.",
 "5.8":  "The item's `version` is at least 1.",
 "5.10": "When the item's `status` is `authored`: its `readings` is an array of exactly one object with the members `kind` and `content`, and its `signature` is a string in the class `w2_token`.",
 "5.11": "No earlier `sets` item has the same `unit` and the same `version` as the item.",
 "6.4a": "The item's `kind` is a W2 kind: one of the ten atomic kinds, or an `attributed`, `hedged`, `causal` or `unformalised` kind of the W2 form.",
 "6.4b": "The item's `kind` nests quoted kinds at most 16 deep.",
 "6.10": "The item's `content/binding` is an object that is exactly `{\"you\": c}`, `{\"task\": t}` or `{\"phrase\": p, \"constant\": c}` with string values, and a `phrase` is a definite phrase as 2.10 defines one.",
 "6.11": "The item's `kind` is `instruction`, or an `attributed` or `hedged` kind that wraps `instruction` at any depth.",
 "6.16a": "The item's `content/command/guard` is a formula of the P0 wire form: tagged arrays with their numbers of members, first-order tags only, variable indices natural numbers.",
 "6.16b": "The item's `content/command/guard` is at most 64 levels deep and has at most 10,000 nodes.",
 "6.17": "The item's `kind` is `question`, or an `attributed` or `hedged` kind that wraps `question` at any depth.",
 "6.21a": "The item's `content/question/body` is a formula of the P0 wire form, as 6.16a.",
 "6.21b": "The item's `content/question/body` is within the budgets of 6.16b.",
 "6.27": "The item's `kind` is `norm`, or an `attributed` or `hedged` kind that wraps `norm` at any depth.",
 "6.28": "W1's norm decoder accepts the item's `content` as one norm object, each of its conditions a formula of the P0 wire form within the rule's budget.",
 "6.31a": "The item's `content/ast` is a formula of the P0 wire form, as 6.16a.",
 "6.31b": "The item's `content/ast` is within the budgets of 6.16b.",
 "6.32a": "The item's `content` is a formula of the P0 wire form, as 6.16a.",
 "6.32b": "The item's `content` is within the budgets of 6.16b.",
 "7.1":  "The item's `content/binding/task` is a string in the class `w2_token`.",
 "7.2a": "The item's `content/binding/you` is the name of a declared constant.",
 "7.2b": "The item's `content/binding/constant` is the name of a declared constant.",
 "7.3":  "No earlier `binding-units` item binds the same entry as the item: `you`, `task`, or the same phrase.",
 "7.4":  "The value the item binds equals the value `/environment/speech_acts` gives the same entry, when it gives one: `task` always, `addressee/constant` for `you`, and the constant of the same phrase under `definites`.",
 "8.1":  "The item's `content/command/act` is the name of a declared predicate.",
 "8.2a": "When the item's `content/command/force` is `require`: the predicate named by `content/command/act` is declared with `regulated` and its `role` is `obligation`.",
 "8.2b": "When the item's `content/command/force` is `forbid`: the predicate named by `content/command/act` is declared with `regulated` and its `role` is `permission`.",
 "8.3":  "The item is the name of a declared constant.",
 "8.4":  "The sorts of the constants named by the item's `content/command/args`, in order, are the declared argument sorts of the act's predicate after the first.",
 "8.5a": "The item's `content/command/guard` names declared predicates, declared constants and declared binder sorts.",
 "8.5b": "The item's `content/command/guard` is well typed: every predicate has its declared arity and sorts, and both sides of an equality have one sort.",
 "8.5c": "Every variable index of the item's `content/command/guard` is inside the scope of its binders.",
 "8.6":  "When the item, as its latest authored reading set leaves it, is an active command (its `kind` is exactly `instruction`, its `meaning` is `specified`, and no open reading set names it): the scope, with the bindings of the document merged, has an addressee.",
 "8.7":  "When the item is an active command as 8.6 defines one: the addressee's sort is the first declared argument sort of the act's predicate.",
 "8.8a": "The item's `content/question/body` names declared predicates, constants and binder sorts.",
 "8.8b": "The item's `content/question/body` is well typed, as 8.5b.",
 "8.8c": "Every variable index of the item's `content/question/body` is inside the scope of its binders.",
 "8.9":  "The item's `content/question/sort` is the name of a declared sort.",
 "8.11": "The item's `content/question/domain` has at least 2 members.",
 "8.12": "The item is the name of a declared constant.",
 "8.13": "The constant named by the item is declared with the sort `content/question/sort` of the enclosing item.",
 "8.15a": "The item's `content/question/body`, read with one free variable of the sort `content/question/sort`, names declared predicates, constants and binder sorts.",
 "8.15b": "The item's `content/question/body`, read so, is well typed, as 8.5b.",
 "8.15c": "Every variable index of the item's `content/question/body` is inside the scope of its binders or is the one free variable.",
 "8.16": "The item's `content/question/version` is at least 1, and some `/document/reading_sets` item has `id` equal to the item's `content/question/set` and `version` equal to its `content/question/version`.",
 "8.17": "When the item's `kind` is `question`: its `meaning` is `{\"open\": [\"intended-reading.<id>\"]}`, with `<id>` the item's `id`.",
 "8.19": "When the item's `kind` wraps `norm` but is not `norm`: W1's norm validation accepts the item's `content` as a one-rule document with the rule's `over` emptied.",
 "8.20a": "The item's `content/ast` names declared predicates, constants and binder sorts.",
 "8.20b": "The item's `content/ast` is well typed, as 8.5b.",
 "8.20c": "Every variable index of the item's `content/ast` is inside the scope of its binders.",
 "8.21a": "The item's `content` names declared predicates, constants and binder sorts.",
 "8.21b": "The item's `content` is well typed, as 8.5b.",
 "8.21c": "Every variable index of the item's `content` is inside the scope of its binders.",
 "9.3":  "The item's `readings` has at least 1 member.",
 "9.6a": "The item's `kind` is a W2 kind, as 6.4a.",
 "9.6b": "The item's `kind` nests quoted kinds at most 16 deep.",
 "c0.1": "The item's `content` is an array, or an object with exactly one member whose name is `ast`, `command`, `question`, `norm` or `binding`; and that member may stand under the item's `kind`: `binding` under `binding` exactly, and `ast`, `command`, `question` or `norm` under `asserted`, `instruction`, `question` or `norm` or under an `attributed` or `hedged` kind that wraps it.",
 "10.1": "The `/document/units` items whose `kind`, as their latest authored reading sets leave them, is exactly `question` and whose content is a question are at most 256.",
 "10.6a": "The item's `target/ast` is a formula of the P0 wire form, as 6.16a.",
 "10.6b": "The item's `target/ast` is within the budgets of 6.16b.",
 "10.7a": "The item's `target/ast` names declared predicates, constants and binder sorts.",
 "10.7b": "The item's `target/ast` is well typed, as 8.5b.",
 "10.7c": "Every variable index of the item's `target/ast` is inside the scope of its binders.",
 "10.9": "For each query the item asks about, in this order: its `content/question/query` when its `content/question/mode` is `follows`, the argument of sort `query` of its command's act, and the same two of each reading of each `/document/reading_sets` item that names the item, in set order: some `/document/queries` item has that `id`, and that item's `premises` are exactly the ids of the fixed assertions before the item, in document order.",
 "10.10": "Some `/document/units` item, or some reading of a `/document/reading_sets` item, asks about the item as 10.9 enumerates asking.",
 "11.1": "No active norm's `over` names `cmd-<id>` for the `id` of an active command.",
 "11.2": "W1's norm validation accepts the policy: the active norms of `/document/units`, then the demand of each active command, in document order, over the environment with the merged scope."}
```

A member `c<k>` of 9.7 has the sentence of `k` prefixed by `For the reading as the unit named by the enclosing
`sets` item's `unit` would be, were the reading chosen: `. The inherited checks' sentences state the fact the
decoder decides; the text of an inherited record is each language's own, so the English of the expectation is
the sentence above, not the message.

### 3.2 How a public rejection reads

The S4 spec's four sentences (its 3.1) apply to every record of this unit, with the check id as the record gives
it and `<wording>` the row of `docs/spec/speech-acts-wire-table.md`. Example, for the source of fixture E13:
`This input is rejected. The first check that fails is 6.13: The `units` item's `content/command/force`, when
present, is one of `forbid`, `require`.` "First" always means the order of base spec 2.6, which the table file
shows from top to bottom.

### 3.3 Wordings this replaces, and why

| Wording | Its two readings | Written instead |
|---|---|---|
| "`speech-acts@0` (numbered table for the spec, two-sided delta)" (the base plan's row) | the spec already has a numbered table to transcribe; or the paragraph is to be refined into one | "The table of 2.3 is authored from speech-acts.md 7's paragraph, refined as base plan row 8 fixes; the generated `speech-acts-wire-table.md` is the numbered table, and section 7 points at it." |
| "The first diagnostic changes in Python and Lean." | both programs' public rows change; or both differ from the table today and the table's record is the one answer | "Python's public message becomes the record's text. The Lean route's row is frozen and does not change; `ve_diagnose` gives the record, and the Lean side of the delta lists where the route's row differs from it." |
| "Shape of all units before references." | each unit's shape and then its references, unit by unit; or every unit's shape, then every unit's references | "Phase 6 checks the shape of every unit in document order; phase 8 then checks the references of every unit in document order. A reference fault in unit 0 comes after a shape fault in unit 1." |
| "Order: the profile gate; the environment block; W1's declaration checks; …; `policy(D)`…; queries" (speech-acts.md 7) | the queries after the policy; or as the validators do it, before | "The queries' shape, duplicates and regeneration (phase 10) come before W1's check of the policy (phase 11), as both validators do it; the paragraph is prose, and base plan 5.1 step 1 takes the authority's behaviour where the spec has no numbered table." |
| "The diagnostics become uniform." | the three languages print one message; or Python's message is the contract's text, which equals the Lean engine's record | "On every corpus case that Lean reads, Python's message is the text of the record that `ve_diagnose` gives for the same source, except on inherited checks. Rust prints nothing for this unit." |
| "Every reference is resolved and typed at decode time" (speech-acts.md 3.2) | with the unit's shape, before the next unit; or after every unit's shape | "Both validators resolve while they read a unit, or after every unit; the table resolves after every unit's shape (phase 8). Where a document has a shape fault in a later unit and a reference fault in an earlier one, the record names the shape fault." |
| "The contract covers the speech-act document." | the `ve-document@2` source; or the core's document object | "The unit is the document object the core validates: `units`, `queries`, `reading_sets`. The wrapper's envelope, fences, identities, answers and compliance are `ve-document@2`'s." |
| "`code` is unchanged." | the error's `code`; or the record's | "The error's `code` is the legacy validator's class, as today. The record's `code` is the contract's; its `class` is the legacy code on every check that is not exempt." |
| "The delta report is complete." | no other message can change; or none on the corpus | "Every message change on the unit's corpus is in the report." |
| "Rust is deferred." | Rust runs the table and defers on a hook; or Rust is not run | "Rust elaborates no speech act and is not run on the unit; there is no Rust column." |

### 3.4 The release note

The `release_note` of the signing file is this text, with the list filled from `signed`:

> When `ve speech-acts` rejects a `ve-document@2` source while it validates the document's units, reading sets
> and query records over the environment, the error now has one more member, `diagnostic`: the error carries the
> contract's record. When a check of the table fails, the record names the first one that fails and the message is
> that check's text; otherwise the message is the validator's. The table is `docs/spec/speech-acts-wire-table.md`;
> "first" is its order from top to bottom: every unit's shape before any unit's references. With the check, the
> record gives the place in the input and a code. For most rejections the message is the same as before. It is a
> different message for these checks. ⟨for each signed check, in table order: its id, a colon, a space, and its
> sentence from `signed`, the entries separated by a space⟩ Whether a document is accepted or rejected has not
> changed. The public switch does not change the error's `code`. An error raised before that validation, while the
> environment, the unit envelopes, the fences, the open terms or the reading sets are read, or after it, while the
> meaning ids, the statuses, the open terms, the answers or the compliance records are checked, has no record, and
> its message is as before. A rejection of a wording keeps its message and carries a record that names no check.
> The Lean route `ve_speech_acts_route` reports as before; `ve_diagnose speech-acts@0` reports the record.

### 3.5 The paragraph that replaces speech-acts.md:884–888

> **The public record.** When `ve speech-acts` rejects a source while it validates the document's units, reading
> sets and query records over the environment, the error carries the contract's record, in its member
> `diagnostic`. The contract is the wire contract `speech-acts@0`
> ([speech-acts-wire-table.md](speech-acts-wire-table.md); [wire-contract.md](wire-contract.md) 2.7). When a check
> of the table fails, the record names the first one that fails and the message is that check's text; otherwise
> the message is the validator's. The table is the order paragraph above made exact, with one rule the paragraph
> left open: the shape of every unit is checked before the references of any unit. The checks are those of this
> section, with one code each; the environment's W1 checks, the P0 formula shape and typing, W1's norm decoder
> and W1's check of the policy are inherited checks whose text is each checker's own. The contract chooses the
> message only: the validator decides, as before, whether the document is rejected. On a document with two
> independent faults, Python's message is the record's and `ve_diagnose speech-acts@0` gives the same record; the
> Lean route's own row keeps its first fault, which may name the other check (units `[c1: command act nonesuch,
> c2: command force maybe]` give the record `InvalidInput: force` at unit `c2`, which the route also reports; units
> `[b: binding {"you": 7}, c: command force maybe]` give the record `InvalidInput: invalid binding fields for b`,
> which the route also reports; before the contract Python reported the other fault in each case).

Section 7's "Order:" paragraph gains, after its last sentence: "The numbered table is
[speech-acts-wire-table.md](speech-acts-wire-table.md), generated from the contract `speech-acts@0`."

## 4. Diagnostics

### 4.1 The public errors

For the source of fixture E13 (base B with unit 1's `force` `"maybe"`), `to_dict()` of the raised error is:

```json
{"code": "InvalidInput", "message": "InvalidInput: force",
 "diagnostic": {"contract": "speech-acts@0", "revision": R, "check": "6.13", "phase": "units",
                "code": "SPEECH_INVALID_FORCE", "class": "InvalidInput",
                "path": "/document/units/1/content/command/force", "text": "InvalidInput: force", "args": {}}}
```

Today it is `{"code": "InvalidInput", "message": "InvalidInput: force"}`: the message is the one printed today.
For the source of fixture E40 (the first reproducer: unit 0's `act` `"nonesuch"` and unit 1's `force` `"maybe"`)
the message changes; today it is `UnknownSymbol: regulated predicate nonesuch`, and after the switch `to_dict()`
is the object above with `"check": "6.13"` and the same path, text and args. For the source of fixture E29 (a
`which_one` question whose `domain` has seventeen constants):

```json
{"code": "ResourceLimit", "message": "ResourceLimit: alternatives",
 "diagnostic": {"contract": "speech-acts@0", "revision": R, "check": "8.10", "phase": "references",
                "code": "SPEECH_RESOURCE_LIMIT", "class": "ResourceLimit",
                "path": "/document/units/0/content/question/domain", "text": "ResourceLimit: alternatives",
                "args": {"count": "17", "limit": "16"}}}
```

Today its message is `alternatives`. With a residual record or a deferred record, `message` is the legacy text
and `diagnostic` is the record of base spec 4.1. With no record, `to_dict()` is today's.

### 4.2 Field by field

As S4 spec 4.2: the object and its type are the legacy validation's; `code` is unchanged and never written;
`message`, `str(error)` and `to_dict()["message"]` are the reported record's `text`; `diagnostic` is the reported
record, before the switch `None` and no member; `path` and `span` are unchanged, and the record's `path` is not
copied into `error.path`; every other member of `to_dict()` is unchanged, `VEError.to_dict` not being edited
(`ve/errors.py:22–30`). The core's legacy errors set no `path` of their own (every raise in
`ve/speech_acts.py:26–640` is without one), so the public objects of 4.1 have none. A consumer that validates
Python's error object against a closed shape must admit `diagnostic`; the switch commit lists every such schema
and stored expectation it had to change.

### 4.3 Lean

- Every row of `ve_speech_acts_route` is byte-identical to its row before the switch, on every corpus case that
  Lean reads.
- `ve_diagnose speech-acts@0` prints the records of 2.3; after the switch, the same rows with the new `revision`.
- Where the Lean route's text differs from the record's (section 6, the Lean side), the route keeps its text.
  That is not a public change: no Lean output switches.

### 4.4 Tool diagnostics

`tools/wire_contract.py` gains no lint code. Its findings name the contract (`speech-acts@0: WC08: …`). Raising
`status` without the revision is `WC10`; a hook or member without a fault in the catalogue is `WC08`, which binds
every one of the fifty-five members of 9.7 to a mutation; a template that uses `{key}` for a returned argument is
`WC04`, which is why 7.3 and 7.4 return `entry`.

The gate prints the S4 spec's lines (its 4.4) with the unit named, the S5 spec's four lines (its 4.4), and:

| Line | Printed when |
|---|---|
| `gate reports: speech-acts@0: lean route differs on <n> cases; reproducers: <two lines>` | informative; never a failure (D2) |
| `gate fails: speech-acts@0: call-site root differs on <n> cases` | V4 fails (G13) |

## 5. Lean: the statements relied on, and the Lean modules

### 5.1 Relied on, as built

The four theorems of the engine (`lean/VE/WireContract/Engine.lean:453–534`), `run_clean_iff`, `run_fault_first`,
`run_phase_major` and `run_congr_reached`, and their helpers, recorded in `VE/Audit.lean`. Item 1 changes none of
them, adds no theorem, and does not touch `VE/Audit.lean`, `lean/axioms.txt` or `tools/check_lean_imports.py`. No
theorem relates the contract to a decoder (base plan 3.2); none is added. The statements, as this draft relies on
them:

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

The scratch file `/tmp/wire-s6-stubs/Stubs.lean` restates each as an `example` whose proof term is the built
theorem applied to its arguments, so that a name or a shape that drifted from the build fails to elaborate. It
could not be run where this draft was written; the builder runs it before the statement review closes, from any
checkout with a built library:

```
LEAN_PATH=<checkout>/lean/.lake/build/lib/lean lean /tmp/wire-s6-stubs/Stubs.lean
```

and the review records the output. The file holds no `sorry` and is not committed.

### 5.2 The hooks module

`lean/VE/WireContract/Hooks/SpeechActs.lean`, hand-written, in the shape of `Hooks/SoftNorms.lean` and
`Hooks/Norms.lean`: `predicate`, `classifier`, `view` (the identity), `hooks`, `adapter` and `registered`, and a
`#guard` that every hook, classifier and view name occurring in `Tables.SpeechActs.table` is one it registers
(`Hooks/SoftNorms.lean:213–219`). It imports the frozen modules it calls read-only (`VE.SpeechActs.Wire`,
`VE.SpeechActs.Tree`, `VE.Norms.Wire`, `VE.Norms.Tree`, `VE.Route.Admission`, `VE.Bridge`); none of those is
edited. The functions it calls on one unit, one reading or one formula are those 2.4 names; the three that take a
`SpeechEnvironment` or a `SpeechDoc` (`checkCandidateCommand`, `checkLoneQuestion`, `validate (policy D)`) are
given the structures `decodeDocument` would build from the parts of the input that earlier checks have passed,
and the module documents, for each, that it does not call `decodeDocument`.

### 5.3 The unit registry: a C4 exception

`ve_diagnose` finds a unit in `units`, a hard-coded list in `lean/VE/WireContract/Diagnose.lean`, a hand-written
module in the frozen inventory. After S5 the list has eight entries (`wire-s5/integrate`, `Diagnose.lean:32–40`).
Item 1 adds one `import` line and one entry and changes no existing line: the third reviewed append-only diff of
that module, recorded as S5 recorded the second (S5 spec 5.3) and as the S1b one was recorded for `VE/Audit.lean`.
If S5's open question 4 has moved the list to `lean/DiagnoseMain.lean` before S6 starts, item 1 adds its line
there and no exception is needed.

### 5.4 Manifest, inventory, layers, imports

- **Inventory.** `Hooks/SpeechActs.lean` and `Tables/SpeechActs.lean` are added. `Limits.lean` and `Names.lean`
  are regenerated (new entries), and so are the earlier tables, whose headers name the hashes of `limits.json`
  and `names.json` (base spec 7.1); those are generated rehashes. `Diagnose.lean` is the exception of 5.3.
- **Assurance manifest.** The `wire.diagnose` binding gains the mode `speech-acts@0` with the kind
  `speech-elaborate`, dispatching to `Diagnose.lean` and `Hooks/SpeechActs.lean`; the hooks module is classified
  under `other_json` as "diagnostic only: no verdict depends on it". Nothing else of the manifest changes: the
  call site starts no Lean process, and the pinned decoder total does not grow.
- **Layers.** `ve.speech_acts_contract` is in the Python layer of `ve.speech_acts` (`tools/layer_policy.py`).
- **Imports.** The Lean rule of base spec 7.3 is unchanged. The Python rule is the row of 2.7.

## 6. The expected delta of this profile, both sides

"Only diagnostics may become uniform, listed per profile": these are the lists, from reading the two validators.
None was run for this draft; the measured lists of 2.10 replace them, and the signatures are given on the
measured Python side.

**The Python side.** Python's message at the call site of 2.7, on handler-reaching cases:

| Check | Today | After the switch | Read from |
|---|---|---|---|
| any check, on a document with a fault in the shape of unit *j* and an earlier fault in the references of unit *i* < *j*, or with a fault in the shape of a later unit and a reference fault resolved while reading an earlier one | the reference fault's text | the shape fault's text | `ve/speech_acts.py:536–607` resolves a command's references, a question's sort, domain and body typing, and a formula's typing while it reads the unit; the table resolves after every unit's shape (phase 8). E40 is such a case |
| 7.1 to 7.4, 8.6, 8.7, with a fault in the shape or references of a later unit | the later unit's text | the binding's or the addressee's text | bindings are merged after the unit loop (`:610`); the addressee is checked at `demand` (`:849–854`), after the queries and wordings |
| 8.10, 10.1 | `alternatives`, `questions` | `ResourceLimit: alternatives`, `ResourceLimit: questions` | `ResourceLimit(...)` without the prefix (`:739, 621`) |
| 8.18 | `open-term name` | `ResourceLimit: open-term name` | `:762` |
| 10.1, with a candidate fault | the candidate's text | `ResourceLimit: questions` | `:619–620`: candidates before the count in Python; the table counts first |
| 11.1 | `UnknownRule: rule cmd-<u>` | the same | `:638–640` after the policy; the table before it: the same text either way |
| every other check that is not inherited | the contract's text | the same | the texts agree on one-fault documents; the gate compares code on every case and text on the faults of tiers 0 and A |

Phases 1 to 5 and 9 are never handler-reaching (2.10), so their text changes are measured but not public:
`ResourceLimit: definites` for `definites` (4.4); Lean's words for 1.1, 1.2, 1.4, 1.6, 1.9, 1.10 (for the last
two, `Predicate flags require data@0`); `InvalidInput: speech_acts block` for `Incorrect fields
(missing=['speech_acts'], unknown=[])` (2.1).

**The Lean side.** The route's text against the record, on every corpus case that Lean reads:

| Check | The route | The record | Read from |
|---|---|---|---|
| 1.7 | `UnsupportedProfile: Missing profile relational-fol@0` from W1's envelope, after the block's structure | the same text, before the block | `Wire.lean:199–208`: `profileGate` does not require the base profile; `decodeNormsEnvironment` does |
| 2.4, 4.2 to 4.5 | checked in `checkSpeech`, after every unit | the block's references before the units | `Tree.lean:257–264` |
| 3.1, with a block structure fault | the vocabulary's shape (`InvalidInput: environment vocabulary`) before the block | the block before W1 | `Wire.lean:202–208` |
| 6.3, with a content fault in the repeated unit | the content fault | `InvalidInput: speech unit id` | `Wire.lean:877` checks duplicates after every unit |
| 8.1 on an active command whose act is a declared, unregulated predicate | `UnknownSymbol: regulated predicate <act>` | `MissingObligationRole: <act>` or `MissingPermissionRole: <act>` (8.2) | `Tree.lean:266–272` against `Wire.lean:795–798` (the dormant case, which agrees with the record) |
| 8.3, 8.4 on an active command when the scope has no addressee | `UnboundSlot: you` | the argument's fault | `Tree.lean:273–279`: the addressee before the arguments |
| 8.5, 8.8, 8.20, 8.21, with a shape fault in a later unit | the typing fault (typed while the unit is read) | the later shape fault | `Wire.lean:327–329, 348, 501` |
| 10.9 for a `follows` question without a record, with an earlier fault of phase 8 | `QueryMismatch: <u>` | the phase-8 fault | `Wire.lean:932–940` regenerates before `checkSpeech` |
| the inherited checks | Lean's own text | Lean's own text | the same engine; no difference by construction |

The two reproducers are named in `lean_route_changes` and are fixtures E40 and E41; on both, the route's text
equals the record's, and Python's legacy text is the one that changes.

**Classes.** None changes at the switch. Lean legacy differences, recorded: every check whose text names a class
other than the one Python raises (D3): `UnknownSymbol`, `TypeMismatch`, `MissingObligationRole`,
`MissingPermissionRole`, `UnboundSlot`, `BindingConflict`, `DuplicateDeclaration`, `UnknownAlternative`,
`AlternativeSort`, `DuplicateAlternative`, `QueryMismatch`, `UnknownRule` texts, which `checker_error` maps to
those classes while Python's `code` is `InvalidInput`.

## 7. The shadow, measurement and switch commits: files and gates

### 7.1 The tooling after S5.0

The generalised tooling takes the unit (S5 spec 7.1): `ve/wire_contract/speech-acts@0.json` is found by the
glob; its examples are `examples/speech-acts@0/`; its English table `docs/spec/speech-acts-wire-table.md`; its
Lean module `Tables/SpeechActs.lean` (`speech-acts@0` gives `SpeechActs`); its catalogue
`conformance/wire_contract_faults_speech_acts.py` with `catalogue("speech-acts@0")`; its reports
`conformance/wire-contract/speech-acts@0-{gate,golden,catalogue,delta,switch,test-inputs}.json`; the gate's
`--unit speech-acts@0` with the legacy function `legacy_validation`, the Lean route `ve_speech_acts_route` and
the case kind `speech-elaborate`; the recorder's wrappers for `legacy_validation`, `public_rejection`,
`SpeechDocument.__init__`, `SpeechSource.__init__` (recording the three members the statement receives) and
`ve_diagnose` with the unit; the corpus test parametrised over the unit with the globs `tests/test_speech*`
and `tests/test_*contract*`; the pre-commit hook's paths from the same table. If S5 merges with other names, 7.1
follows the merged names and the review notes it (plan, prerequisite paragraph).

### 7.2 Diff scope

Item 1 is a shadow commit (S6.1a), a measurement commit (S6.1b) and a switch commit (S6.1d), after the commit of
S6-pre where one is needed.

**The shadow commit:** `ve/wire_contract/speech-acts@0.json`, `examples/speech-acts@0/` (two examples: base B
and B's environment with `units` `[]`), `limits.json` and `names.json` with their lock entries;
`ve/speech_acts_contract.py` (hooks, classifiers, adapter, `legacy_validation`, `REGISTRY`; no `public_rejection`
yet); `lean/VE/WireContract/Hooks/SpeechActs.lean`, the generated `Tables/SpeechActs.lean`, `Limits.lean`,
`Names.lean` and the regenerated earlier tables, with their inventory lines; `Diagnose.lean` (5.3);
`docs/spec/speech-acts-wire-table.md`; `conformance/wire_contract_faults_speech_acts.py` and the stored reports
of the unit (gate, golden, catalogue); the manifest's `wire.diagnose` mode; `tools/layer_policy.py`; tests.

**The measurement commit:** the stored gate and delta reports regenerated over the whole corpus with
`public_diagnostic_changes` and `lean_route_changes`; the gate enforces S6-pre and the class rule from here;
tests (the fixtures G3, G6 and G8). No file of `ve/` or `lean/` changes.

**The switch commit:** the contract and the lock (2.9); its generated table and inventory line; the contract
module gains `public_rejection`; the one call site (2.7); the gate's tier P and the rows of section 9 enforced
at `public`; the stored reports at revision `R`, the new `speech-acts@0-switch.json`, and
`speech-acts@0-test-inputs.json` for the sources of 8.7; tests; `tests/contract_input_recorder.py` if a wrapper
is still missing; the import-scan test; the paragraph of 3.5 and the pointer of section 7 in speech-acts.md; the
comment of `tests/test_speech_acts_conformance.py:1857–1859`; this file's response section.

Not changed by any commit of item 1, and checked by the diff-scope test of C1: `ve/speech_acts.py`,
`ve/speech_english.py`, `ve/environment.py`, `ve/norms.py`, `ve/norm_admission.py`, `ve/admission.py`,
`ve/errors.py`, `ve/wire.py`, `ve/ast.py`, `ve/wire_contract/engine.py`, `contract.schema.json`, the earlier
contracts and examples, every Lean module other than the generated tables, the hooks module and `Diagnose.lean`,
`VE/Audit.lean`, `lean/axioms.txt`, `tools/check_lean_imports.py`, `Main.lean`, `SpeechActsMain.lean`, every
Rust file, `conformance/identity.json`, the frozen baseline. The commit of S6-pre is a different commit, before
the switch, with its own scope.

### 7.3 The gates

The four conservativity gates of base plan 5.2, as the debate amended them, for every commit of item 1:

- **C1.** The diff is within 7.2. `VEError.to_dict()` is not edited; `diagnostic` is set at one more call site.
- **C2.** Legacy verdicts equal their snapshot. Each engine reports `clean` on every accepted corpus case and a
  fault on every rejected one, in Python and in Lean; Rust is not run. Python's deferred count is 0.
- **C3.** Public diagnostics change only as the signed delta lists; the gate fails otherwise. The shadow and
  measurement commits change no public diagnostic.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass. The inventory diff is the
  additions and generated rehashes of 5.4 and the append-only `Diagnose.lean` diff of 5.3, and nothing else; no
  commit touches `VE/Audit.lean`.

The corpus-completeness test is kept, with its three tests per unit (8.7). The difffuzz row of section 9 is
vacant until `infra/difffuzz` merges.

## 8. Acceptance fixtures for item 1

Deterministic, with expectations written by hand from section 2 and base spec sections 2 and 8. Each reviewer
derives the expectation of every fixture before reading the column "Expected". A fixture of 8.1 is green when
the Python engine and `ve_diagnose` both return the expected outcome, as records compared by base spec 2.7,
except that an inherited record's `text` and `args` are each language's own.

**The base B.** The environment is `F0()` of `tests/test_speech_acts_lean.py:57–87`: task `t1`, addressee
`{"sort": "user", "constant": "alice"}`, definites `{"the token": "token1", "the desk": "desk1", "the writing
desk": "desk1"}`, the profiles `["norms@0", "relational-fol@0", "speech-acts@0"]`, the sorts `user`, `control`,
`token`, `desk`, `service`, `thing`, `query`, the regulated predicates `click_required` (obligation, act `{0}
click {1}`, permission `click_permitted`), `click_permitted`, `share_permitted`, `submit_required`,
`submit_permitted`, `open_required`, `open_permitted`, the base predicates `reviewed` (over `service`), `cat`,
`animal`, `disabled`, `done_click`, `done_open`, `done_submit`, and the constants `alice` (`user`), `check`
(`control`), `token1`, `desk1`, `atlas` and `beacon` (`service`), `tom`, `q1`. The document has two units, in
this order, each `{"id", "span": [i, i + 1], "kind", "meaning": "specified", "support": "none", "content"}`:

| Index | `id` | `kind` | `content` |
|---|---|---|---|
| 0 | `u1` | `instruction` | `{"command": {"force": "require", "act": "click_required", "args": ["check"]}}` |
| 1 | `u5` | `question` | `{"question": {"mode": "polar", "body": ["unary", "reviewed", ["const", "atlas"]]}}` |

Both legacy validators accept B (`tests/test_speech_acts_conformance.py:67–99`). B and its environment with
`units` `[]` are the two examples. "Unit *i*" is `/document/units/i`. `A` is the atom `["unary", "reviewed",
["const", "atlas"]]`. **Q(mode)** is `{"question": {"mode": mode, "sort": "service", "domain": ["atlas",
"beacon"], "body": ["unary", "reviewed", ["var", 0]]}}`. **An open set over `a`** is a unit `a` of kind
`asserted` without content at the next span and the reading set `{"id": "rs", "unit": "a", "version": 1,
"status": "open", "readings": [{"kind": "asserted", "content": A}]}`. **A phrase of *n* bytes** is `the ` followed
by *n* − 4 letters `a`. All records have `"contract": "speech-acts@0"` and `"revision": R`.

### 8.1 The engine

| Case | Change to B | Expected `check`, `path`, `text` |
|---|---|---|
| E1 | none; and the second example | clean; both legacy validators accept |
| E2 | `profiles` `["norms@0", "relational-fol@0"]` and `speech_acts` removed | 1.4, `/environment/profiles`, `UnsupportedProfile: speech-acts@0 is required` |
| E3 | `profiles` `["relational-fol@0", "speech-acts@0"]` | 1.5, `/environment/profiles`, `UnsupportedProfile: speech-acts@0 requires norms@0` |
| E4 | `profiles` gain `"soft-norms@0"` (sorted) | 1.6, `/environment/profiles/2`, `UnsupportedProfile: speech-acts@0 with soft-norms@0` |
| E5 | `profiles` `["norms@0", "speech-acts@0"]` | 1.7, `/environment/profiles`, `UnsupportedProfile: Missing profile relational-fol@0` |
| E6 | predicate `reviewed` gains `"functional": true` | 1.9, `/environment/vocabulary/predicates/reviewed`, `UnsupportedProfile: speech-acts@0 with data flags` |
| E7 | `speech_acts` removed | 2.1, `/environment`, `InvalidInput: speech_acts block` |
| E8 | `task` is `"t 1"` | 2.4, `/environment/speech_acts/task`, `InvalidInput: speech_acts block` |
| E9 | `task` is 64 letters `t` | clean (64 bytes is within the class) |
| E10 | `task` is 65 letters `t` | 2.4, `/environment/speech_acts/task`, `InvalidInput: speech_acts block` |
| E11 | the definite `the token` renamed to a phrase of 80 bytes | clean |
| E12 | the definite `the token` renamed to a phrase of 81 bytes | 2.10, `/environment/speech_acts/definites/the aaa…a` (the 81-byte key), `InvalidInput: speech_acts block` |
| E13 | unit 0's `force` is `"maybe"` | 6.13, `/document/units/1/content/command/force` with unit 0 unchanged; see E13′ | |
| E13′ | (the case of E13 written out) unit 1 replaced by `{"id": "c2", "kind": "instruction", …, "content": {"command": {"force": "maybe", "act": "click_required", "args": ["check"]}}}` | 6.13, `/document/units/1/content/command/force`, `InvalidInput: force` |
| E14 | the definite `the desk` mapped to `"nobody"` | 4.5, `/environment/speech_acts/definites/the desk`, `UnknownSymbol: nobody` |
| E15 | the addressee's sort is `"robot"` | 4.2, `/environment/speech_acts/addressee/sort`, `UnknownSymbol: sort robot` |
| E16 | `click_required`'s act is `"{0} click{1}"` | 4.1, `/environment/vocabulary/predicates`, `InvalidInput: speech template slot must stand apart` |
| E17 | `definites` has 65 entries: the phrases `the ba` to `the bz`, `the ca` to `the cz` and `the da` to `the dm`, each mapped to `check` | 4.4, `/environment/speech_acts/definites`, `ResourceLimit: definites`; `args` `count` `65`, `limit` `64` |
| E18 | the same with 64 entries (`the ba` to `the dl`) | clean |
| E19 | struck while drafting: the definite `the token` renamed `the user` was to witness a phrase-clash check, and no such check exists, because a phrase contains a space and a declared name does not (2.3, "what is not in the table"); both validators accept this source. The number stays vacant | none |
| E20 | `reading_sets` is `{}` | 5.2, `/document/reading_sets`, the reading-sets text |
| E21 | an open set over `a`, with `version` `0` | 5.8, `/document/reading_sets/0/version`, `invalid or duplicate reading set version` |
| E22 | an open set over `a`, with `"signature": "s"` added | 5.9, `/document/reading_sets/0`, `open reading set cannot have an author signature` |
| E23 | two open sets over `a`, both version 1 | 5.11, `/document/reading_sets/1`, `invalid or duplicate reading set version` |
| E24 | unit 1's `id` is `"u1"` | 6.3, `/document/units/1/id`, `InvalidInput: speech unit id` |
| E25 | unit 1's `kind` is `"riddle"` | 6.4a, `/document/units/1/kind`, class `InvalidInput`; text each language's own |
| E26 | a third unit `{"id": "b", …, "kind": "binding", "content": {"binding": {"you": 7}}}` | 6.10, `/document/units/2/content/binding`, `InvalidInput: invalid binding fields for b` |
| E27 | unit 0's `kind` is `"question"` | 6.11, `/document/units/0/kind`, `InvalidInput: command content requires instruction kind` |
| E28 | unit 0's command lacks `args` | 6.12, `/document/units/0/content/command`, `InvalidInput: invalid command fields for u1` |
| E29 | unit 0 replaced by a `which_one` question `Q("which_one")` whose `domain` lists seventeen constants `s00` to `s16`, each declared with sort `service` | 8.10, `/document/units/0/content/question/domain`, `ResourceLimit: alternatives`; `args` `count` `17`, `limit` `16` |
| E30 | the same with sixteen (`s00` to `s15`) | clean |
| E31 | unit 1 is `Q("which_all")` with `domain` `["atlas", "atlas"]` | 8.14, `/document/units/1/content/question/domain/1`, `DuplicateAlternative: u5, atlas` |
| E32 | unit 1 is `Q("which_all")` with `domain` `["atlas", "zz"]` | 8.12, `/document/units/1/content/question/domain/1`, `UnknownAlternative: u5, zz` |
| E33 | unit 1 is `Q("which_all")` with `domain` `["atlas", "tom"]` | 8.13, `/document/units/1/content/question/domain/1`, `AlternativeSort: u5` |
| E34 | an open set over `a`, and a fourth unit `r` of kind `question`, meaning `{"open": ["intended-reading.r"]}`, content `{"question": {"mode": "reading", "set": "rs", "version": 1}}`, with `r` 47 letters `q` | clean |
| E35 | E34 with `r` 48 letters `q` | 8.18, `/document/units/3/id`, `ResourceLimit: open-term name`; `args` `count` `48`, `limit` `47` |
| E36 | E34 with `r` of meaning `"specified"` | 8.17, `/document/units/3/meaning`, `InvalidInput: invalid question fields for r` |
| E37 | E34 with the set's `version` `2` in the question | 8.16, `/document/units/3/content/question`, `InvalidInput: invalid question fields for r` |
| E38 | 258 units: B's two and 256 copies of unit 1 named `q000` to `q255` at the next spans (257 questions) | 10.1, `/document/units`, `ResourceLimit: questions` |
| E39 | 257 such units (B's two and 255 copies, `q000` to `q254`: 256 questions) | clean |
| E40 | unit 0's `act` is `"nonesuch"` and unit 1 is E13′'s unit (the first reproducer) | 6.13, `/document/units/1/content/command/force`, `InvalidInput: force` (phase 6 before phase 8) |
| E41 | the units `[b: binding {"you": 7}, c: force maybe]`: `{"id": "b", "kind": "binding", "content": {"binding": {"you": 7}}}` then E13′'s unit as `c` (the second reproducer) | 6.10, `/document/units/0/content/binding`, `InvalidInput: invalid binding fields for b` (item-major: unit 0 before unit 1) |
| E42 | unit 0's `act` is `"nonesuch"` | 8.1, `/document/units/0/content/command/act`, `UnknownSymbol: regulated predicate nonesuch` |
| E43 | unit 0's `act` is `"reviewed"` and its `args` `["atlas"]` | 8.2a, `/document/units/0/content/command/act`, `MissingObligationRole: reviewed` |
| E44 | unit 0's `force` is `"forbid"` | 8.2b, `/document/units/0/content/command/act`, `MissingPermissionRole: {0} click {1}` |
| E45 | unit 0's `args` `["zz"]` | 8.3, `/document/units/0/content/command/args/0`, `UnknownSymbol: zz` |
| E46 | unit 0's `args` `["atlas"]` | 8.4, `/document/units/0/content/command/args`, `TypeMismatch: command args for u1` |
| E47 | `addressee` removed from the block | 8.6, `/document/units/0`, `UnboundSlot: you` |
| E48 | the addressee is `{"sort": "service", "constant": "atlas"}` | 8.7, `/document/units/0`, `TypeMismatch: addressee` |
| E49 | unit 0 gains `"guard": ["unary", "zz", ["const", "atlas"]]` | 8.5a, `/document/units/0/content/command/guard`, class `UnknownSymbol` |
| E50 | unit 0 gains `"guard": 5` | 6.16a, `/document/units/0/content/command/guard`, class `InvalidInput` |
| E51 | unit 0 gains `"guard"`: a chain of 65 `not` around `["top"]` | 6.16b, `/document/units/0/content/command/guard`, class `ResourceLimit` |
| E52 | a third unit `{"id": "b", "kind": "binding", "content": {"binding": {"you": "atlas"}}}` | 7.4, `/document/units/2`, `BindingConflict: you` |
| E53 | two binding units `{"task": "t1"}` and `{"task": "t1"}` | 7.3, `/document/units/3`, `DuplicateDeclaration: binding task` |
| E54 | `queries` `[{"id": "q1", "premises": [], "target": {"ast": A}}]` | 10.10, `/document/queries/0/id`, `QueryMismatch: q1` |
| E55 | a third unit `f` of kind `question`, content `{"question": {"mode": "follows", "query": "q9"}}`, and no `queries` | 10.9, `/document/units/2`, `QueryMismatch: f` |
| E56 | unit 0 replaced by a norm unit `{"norm": {"name": "r0", "predicate": "click_required", "sign": true, "guard": ["top"], "unless": [], "over": ["cmd-u5"]}}` and unit 1 by B's command as `u5` | 11.1, `/document/units`, `UnknownRule: rule cmd-u5` |
| E57 | 257 norm units `r000` to `r256`, each on `click_required` with guard `["top"]`, replacing B's units | 11.2, `/document/units`, class `ResourceLimit`; text each language's own (W1's `rules`) |
| E58 | an open set over `a` whose `readings` has 65 copies of its reading | 9.2, `/document/reading_sets/0/readings`, `reading sets hold 1 to 64 readings`; `args` `count` `65`, `limit` `64` |
| E59 | an open set over `a` whose `readings` is `[]` | 9.3, `/document/reading_sets/0/readings`, the same text |
| E60 | an open set over `a` whose one reading is `{"kind": "instruction", "content": {"command": {"force": "maybe", "act": "click_required", "args": ["check"]}}}` | 9.7, member `c6.13`, `/document/reading_sets/0/readings/0`, `InvalidInput: force` |
| E61 | an open set over `a` whose one reading is `{"kind": "asserted", "content": {"command": {…B's command…}}}` | 9.7, member `c0.1`, `/document/reading_sets/0/readings/0`, `invalid speech reading content` |
| E62 | E13′ with unit 0's `args` `["zz"]` | 6.13, `/document/units/1/content/command/force` (unit 1's shape before unit 0's references) |
| E63 | E45 with a third unit of kind `"riddle"` | 6.4a, `/document/units/2/kind` (phase 6 before phase 8) |
| E64 | E42 with E46 | 8.1, `/document/units/0/content/command/act` (table order inside the item) |
| E65 | `units` is `{}` | 5.1, `/document/units`, `array expected` |

For every case from E2 to E65 that is neither clean nor struck, the Lean route rejects, and the record's `class`
equals the code the legacy validator reports in Python (`VEError.code`), except on the exempt checks (2.11). The numbers: a
phrase of 80 bytes is `the ` (4 bytes) and 76 letters; 81 is 77 letters; `intended-reading.` is 17 bytes, so a
47-byte id gives W2's 64-byte token limit exactly and a 48-byte id exceeds it; 65 two-letter phrases are the 26
from `ba` to `bz`, the 26 from `ca` to `cz` and 13 from `da` to `dm`. The scratch file computes each by `#eval`
(5.1); until it is run, these are hand arithmetic.

### 8.2 The boundary and the call site

The **wrapper call** on a source is `SpeechSource(meta, source, fences)` with `meta` `{"format": "ve-document@2",
"environment": E, "units": U, "queries": …, "reading_sets": …}`, `source` one line of ASCII per unit, each unit's
`span` the byte range of its line, and `fences` `{}`; the units' spans in B are then those lines' ranges, not `[i,
i + 1]`.

| Case | Input | Expected |
|---|---|---|
| S1 | the wrapper call on E13′ | raises a `VEError` whose `to_dict()` is the first object of 4.1 |
| S2 | the wrapper call on E40 | `to_dict()` is the first object of 4.1 (the message changes from `UnknownSymbol: regulated predicate nonesuch`) |
| S3 | the wrapper call on E29 | `to_dict()` is the second object of 4.1 |
| S4 | the wrapper call on E7 | raises from `Environment` at `ve/speech_document.py:144`: `diagnostic` is `None` and the message is today's |
| S5 | the wrapper call on B with unit 1 lacking `support` | raises the wrapper's `invalid unit schema` before the statement: `diagnostic` is `None` |
| S6 | for each of S1 to S3: the legacy error `e` from `legacy_validation` on the same source | the raised error has `e`'s type and `e`'s `code`; `str` of it, its `message` and its record's `text` are equal |
| S7 | the wrapper call on B (accepted), in a subprocess started without the recorder plugin, with the Lean route available | the wrapper returns as today; afterwards neither `ve.speech_acts_contract` nor `ve.wire_contract` is in `sys.modules` |
| S8 | `public_rejection` on B (accepted) with a hand-made `VEError("legacy says no")` | returns the same object; `message` is `legacy says no`; `diagnostic` is the residual record: `check` and `phase` `residual`, code `SPEECH_INVALID_INPUT`, class `InvalidInput`, path `""`, text `legacy says no`, args `{}` |
| S9 | `public_rejection` on E42's source and its legacy error, with a registry that lacks `act_declared` | `diagnostic` is `{"contract": "speech-acts@0", "revision": R, "deferred": "8.1", "text": "UnknownSymbol: regulated predicate nonesuch"}`; the message is unchanged |
| S10 | as S9, with a registry whose `act_declared` raises `KeyError` | returns `e` unchanged: `diagnostic` is `None` |
| S11 | `public_rejection` on E13′'s source and error, with the contract of the shadow revision | returns the error unchanged |
| S12 | `public_rejection` twice on E13′'s source and error | the second call changes nothing |
| S13 | `public_rejection` on E13′'s source and error | the two arguments are equal, after the call, to deep copies taken before it |
| S14 | the syntax-tree scan of 2.7 on the tree; and on each of three changed trees: (a) `ve/speech_acts.py` gains `from .speech_acts_contract import legacy_validation`; (b) `ve/speech_document.py` gains a second call of `public_rejection`; (c) in `ve/speech_document.py` the call is bound to a name and the name raised | passes; fails on each of (a) to (c) |
| S15 | `SpeechDocument(Environment(B.environment), …)` on E13′'s units; `core` on E40 | each raises an error whose `diagnostic` is `None` and whose message is the legacy text |
| S16 | the wrapper call on B with the source line of unit 0 `"Click the moon."` (a wording the parser does not read as unit 0's command) | raises from `_check_wordings` through the statement: `message` is today's (`InvalidInput: invalid command fields for u1`), `diagnostic` is the residual record with that text |
| S17 | the wrapper call on E40 with the wrapper's units carrying `surface`, `status` and `meaning_id` members removed, in the test only, before the statement | the same record as S2 (V4) |

### 8.3 The delta and the gate

Tier **P** runs only when the contract's `status` is `public`: for every corpus case that the Python core
rejects with an error `e`, `public_rejection(environment, document, e′)` on a fresh error `e′` of the same source,
and the wrapper call on the source laid out as 8.2 lays it out. The function is checked on every rejected case.
The call carries the record only on the handler-reaching cases (2.10); on the others it must raise today's
error.

| Case | Input | Expected |
|---|---|---|
| G1 | tier P, every case, the function | the returned error's `diagnostic` equals the reported record of 2.10, computed apart; its `message` is that record's `text`; its type and `code` are `e`'s |
| G2 | tier P, every handler-reaching case, the call | raises; `to_dict()` equals `e`'s `to_dict()` with `message` replaced by the record's `text` and `diagnostic` added |
| G12 | tier P, every rejected case that is not handler-reaching, the call | raises an error with no record: `diagnostic` is `None`, and its type, `code` and message are those of the snapshot before the switch commit (Z8) |
| G13 | tier P, every handler-reaching case, the call's root against the adapter's root | the engine's record on the wrapper's units (with `source`, `parent_id` and, where the test adds them, `surface`, `status`, `meaning_id`) equals the record on the adapter's root (V4) |
| G3 | the gate at the measurement commit, in shadow | the sum of text changes over checks that are not inherited is `text_delta_count`; `public_diagnostic_changes` lists each check of section 6 that has a case, and any check beyond section 6 is reported, not dropped; `lean_route_changes` is present and names E40 and E41; the gate exits 0 unless S6-pre or the class rule fails |
| G4 | at `public`, the signing file without the entry of 8.10 | the gate fails with the first line of S4 spec 4.4 |
| G5 | at `public`, the signing file with an entry `6.13` | the gate fails with the second line |
| G6 | the gate's measurement with Python's legacy class on E42's class of inputs replaced, in the test only, by `UnknownSymbol` | fails with `public delta: <n> class differences` |
| G7 | the gate with the Lean verdict on a document of 10,001 units replaced, in the test only, by `ok` | fails with `legacy verdict differences` naming it (and passes once S6-pre records the class as fixed) |
| G8 | the delta report after a contract text is edited, without regeneration | `conformance/wire_contract_delta.py --unit speech-acts@0 --check` fails |
| G9 | the gate after S6-pre and the switch | exits 0: every row of section 9 holds |
| G10 | the gate's coverage | every check and every member of 9.7 has a first-fault witness and a masked witness; the allowed gaps are G1 of the S5 spec's 8.4 (an explicit `null`) and none else |
| G11 | the earlier units' gates after the shadow commit | their stored reports, delta, golden and catalogue files and English tables are byte-identical, except the regenerated headers of their Lean tables |

### 8.4 Conservativity

- **Z1.** The full existing suite, the conformance reports, `conformance/identity.json`, the frozen baseline and
  every frozen hash are unchanged by each commit of item 1, except the files of 7.2. Every stored expectation of
  a Python error's text that the switch commit changes is listed in it.
- **Z2.** `VEError("x").to_dict()` is `{"code": "InvalidInput", "message": "x"}`, as today.
- **Z3.** Every row of `ve_speech_acts_route`, on every corpus case that Lean reads, is byte-identical to the
  snapshot before each commit.
- **Z4.** On every corpus case, the Python core gives the verdict, code and text of the snapshot before the
  commit. (A commit of S6-pre has its own snapshot rule, 2.11.)
- **Z5.** On every corpus case, the environment and the document are equal, after `legacy_validation` returned
  or raised, to deep copies taken before it (V3 of 2.7).
- **Z6.** `frozen.py` passes; the inventory diff is as C4 says.
- **Z7.** The earlier units' outputs are byte-identical (G11).
- **Z8.** On every rejected corpus case that is not handler-reaching (2.10), the call raises the error of the
  snapshot before the commit: same type, `code` and message, and no `diagnostic`.

### 8.5 Lean and tooling

| Case | Input | Expected |
|---|---|---|
| L1 | `ve_diagnose speech-acts@0` on E13′ as a `speech-elaborate` case | `{"id": …, "status": "ok", "outcome": "fault", "diagnostic": r}` with `r` the record of 4.1's first object |
| L2 | `ve_diagnose speech-acts@0` on E40 and on E41 | the records of E40 and E41 |
| L3 | `ve_diagnose speech-acts@0` on every corpus case that Lean reads, before and after the switch commit | the rows are equal once the old `revision` is read as `R` |
| L4 | `ve_diagnose speech-acts@0` on a `speech-answer` case; on a `speech-elaborate` case whose document has `answers`; on one whose unit carries `source` | `{"id": …, "status": "error", "error": "UnsupportedProfile: case kind speech-answer has no wire contract input"}`; `… the case is outside the unit's domain` twice; exit 1 |
| L5 | `ve_diagnose soft-norms@0`, `norms@0`, `norm-defaults@0` on their corpora after the shadow commit | byte-identical rows |
| L6 | `lake build` with `Tables/SpeechActs.lean` naming a hook `Hooks/SpeechActs.lean` does not register | fails at the `#guard` |
| L7 | the Lean `reading_candidate` classifier and the Lean unit checks it mirrors, on every reading of the corpus whose set is open | the member the classifier names is the first mirrored check that fails on the reading placed as its unit |
| T1 | `tools/wire_contract.py --check` on the committed tree | exits 0 and prints nothing |
| T2 | the contract with `status` `public` and the shadow revision | `WC10` |
| T3 | `Tables/SpeechActs.lean` at the switch commit, against its parent | the diff is the header comment and the numeral of `revision`, and nothing else |
| T4 | the contract with 7.3's `returns` renamed `key` | `WC04` |
| T5 | the contract with hook 8.1 renamed `predicate_declared`, no catalogue fault for it | `WC08` |
| T6 | `--write` after S6.1a | exactly the generated files of 7.2, the lock and the generated modules' inventory lines change |
| T7 | `names.json`'s `w2_token` as generated into `Names.lean` | the Lean class admits `a.b-c_D9`, refuses `a b`, the empty string and a 65-byte name, as the Python engine does |

### 8.6 The scratch file

`/tmp/wire-s6-stubs/Stubs.lean` holds the four `example`s of 5.1 and these `#eval`s, whose values the fixtures
above state: `("the " ++ String.mk (List.replicate 76 'a')).utf8ByteSize` (80) and with 77 (81);
`("intended-reading." ++ String.mk (List.replicate 47 'q')).utf8ByteSize` (64) and with 48 (65);
`VE.SpeechActs.Wire.phraseOk` on the two phrases (`true`, `false`); `VE.Route.Admission.token` on 64 and 65 `t`
(`true`, `false`); `VE.SpeechActs.Tree.token` on the same; `(List.range 26).length * 2 + 13` (65); and
`VE.WireContract.run` of a stub table holding phases 1 and 2 of 2.3 as `Table` literals, with trivial hooks, on
the JSON of E2 to E12, printed through `VE.WireContract.record`. Each printed record must equal the row of 8.1.
The builder runs it as 5.1 says and attaches the output to the statement review.

### 8.7 The corpus-completeness test

`tests/test_wire_gate_corpus.py` keeps its three tests for every earlier unit and runs the same three for
`speech-acts@0`: every input of the unit's contract tests and of the tests that build its sources is in the
unit's corpus; every source of the three speech test modules (`tests/test_speech_acts.py`,
`test_speech_acts_lean.py`, `test_speech_acts_conformance.py`, through `core`, `elaborate`, `run`, `run1` and
`SpeechSource`) is in it; every fixture of speech-acts.md 9 that a test builds is in it. The recorder sees the
paths through the wrappers of 7.1; each wrapper is shown to work by one source submitted through that path and
no other (S18, S19), stored in `speech-acts@0-test-inputs.json`.

| Case | Input | Expected |
|---|---|---|
| S18 | the wrapper call on B with unit 0's `force` `"never"` | raises as E13′ with `never`; the source is in `speech-acts@0-test-inputs.json` |
| S19 | `public_rejection` on B with unit 0's `force` `"always"` and a hand-made `VEError("x")` | the record of 6.13; `code` `InvalidInput`, the hand-made error's own; the source is in `speech-acts@0-test-inputs.json` |

## 9. The switch gate

The DRI reviews one gate report at revision `R`, the two-sided delta report and the signing file. Astra and Fable
read the measured delta and the signing file before the switch commit. The switch commit is made only when every
row holds, and the gate exits non-zero on any unmet row that is enforced, judging each from the data and not
from a stated summary (base spec section 17).

| Row | Definition | Required |
|---|---|---|
| the continuation rows | base spec section 9: tiers 0 and A, residual, deferred, coverage; feasibility reported with `n1`, `n2`, `coarse`, `t3` partitioning the unit's 115 numbered checks and no threshold | as there |
| S6-pre | `legacy_verdict_differences`, over every tier | empty |
| the class rule | cases with a class difference outside the exemptions of 2.11 | 0; the exempt cases counted and reported |
| the signed delta | the checks with a measured text change on handler-reaching cases, against the keys of `signed` | the two sets are equal |
| the boundary | tier P: G1 on every rejected case; G2 on every handler-reaching case; G12 on every other rejected case; G13 on every handler-reaching case | no difference |
| errors without a record | tier P cases on which the failure rule applied | 0 |
| the source is not modified | Z5 | 0 cases |
| the legacy validators | Z3 and Z4 | byte-identical |
| the Lean route delta | `lean_route_changes`, with the two reproducers | reported |
| the corpus | `tests/test_wire_gate_corpus.py` for the unit | passes |
| the difffuzz baseline | the number of stored differential findings of `infra/difffuzz`, after against before each commit of item 1 | not larger; vacant until that branch merges |

When each row is enforced: S6-pre and the class rule from the measurement commit on, whatever the `status`; the
signed delta, the boundary and errors without a record only at `public`; every other row whatever the `status`.
A row that fails after the switch commit is handled by a revert of the commit, or by a revision that sets
`status` to `shadow`.

## 10. Limits, and what is not claimed

1. **No verdict and no identity.** The engine runs inside the handler of a rejection and returns the error it
   was given, at one call site. That is a tested property (V1), not a theorem.
2. **One entry point.** Only the wrapper's statement is public; the entry points of 2.8 keep today's messages.
3. **The delta is complete on the corpus.** An input outside the unit's corpus can show a message change that no
   list contains, a class that differs from its record's, a residual record, or an error without a record.
4. **The table's order is the spec's, which neither validator follows on multi-fault documents.** The record is
   the table's and both engines give it; Python's public message takes it; the Lean route's row keeps the route's
   own first fault, which is reported beside the record and not changed.
5. **Wordings are outside the unit, but inside the call site.** A rejection by `_check_wordings` at the
   statement of 2.7 carries a residual record with today's text (S16). The residual count on the corpus is zero
   because the corpus has no `source`; in the field it is not.
6. **Inherited texts differ between languages** until S4 items 5 and 6 and a later revision: the environment
   (3.1), the formula shape (6.16, 6.21, 6.31, 6.32, 10.6) and typing (8.5, 8.8, 8.15, 8.20, 8.21, 10.7), W1's
   norm decoder (6.28), the dormant norm's rule check (8.19) and the policy (11.2).
7. **The class rule has five exemptions** (2.11), all inherited hooks over decoders that raise several classes,
   and 1.1. Each is counted by the gate.
8. **Lean's classes differ on most checks** (D3): Python's `code` is `InvalidInput` where the text names another
   class, and a Lean-authority deployment would report the leading word's class. Not changed.
9. **Rust prints nothing for this unit.** There is no Rust column, no Rust engine and no Rust tolerance.
10. **The failure rule hides an engine defect from the caller.** The caller gets today's error; the defect is
    visible only where the gate or a test runs the same input.
11. **Cost.** A rejection at the call site costs one engine run; `w1_policy` rebuilds the policy and
    `reading_candidate` re-checks every reading. An accepted document costs nothing.
12. **`self.env.to_dict()` is the root's environment**, not the submitted bytes; the table reads nothing of it
    that the round trip changes (2.7), and the gate's corpus uses the submitted dictionary.
13. **The domain excludes a reading-set unit with content or another kind** (2.2); such a unit is validated by
    neither core on its own members and by this contract not at all (plan section 8, question 5).
14. **The surface prints none of the sentences of 3.2.** They are fixed, not shown.

## 11. Statement review checklist (Astra + Fable, before any build step)

1. **Scope (plan section 8, questions 2, 3, 5, 7).** Is reporting Lean's side without applying it the right
   reading of base plan row 8? Is the document core, with wordings and the wrapper outside, the right unit? Is
   one entry point right?
2. **The table (2.3).** For each row, do the kind, guard and text reproduce `ve/speech_acts.py:493–640, 697–764`
   and `Wire.lean:455–503, 869–961` with `Tree.lean:256–317` on one-fault inputs? Derive E40, E41, E62 to E64
   independently. Rows worth attacking: the guards C, Q, N, F (the tag precedence); 6.20a to 6.20e (the per-mode
   keys); 6.29 and 6.30 (the two texts); 8.1 and 8.2 (the unregulated declared predicate); 8.6 and 8.7 (the
   effective unit); 10.9 (the enumeration of asks); the split of each formula into shape (phase 6) and typing
   (phase 8).
3. **The domain (2.2).** Are the five exclusions the right way to keep C2 true, or should some be listed verdict
   differences? Is excluding `source` sound given that the two cores agree on the ASCII and choice-kind checks?
4. **The candidates (9.7, 2.4).** Is one classifier whose members mirror the unit checks exact against
   `_check_candidates` and `checkCandidate`? Is the member list complete (fifty-five)? Does the order key follow
   the unit table?
5. **The hooks (2.4).** Can any Lean hook fail for a reason that belongs to a later check? Is `w1_environment`'s
   stripped environment exactly what both W1 decoders read? Is the `formula_shape` node count exactly
   `formulaNodes`? Is `w1_policy`'s `SpeechDoc` exactly `decodeDocument`'s on inputs that reach it?
6. **The class rule and S6-pre (2.11).** Are the five exemptions the only ones? Attack the three S6-pre
   candidates; are there others (the question count under quoted kinds, the 10,000-node budget of `decodeBudgetNorm`
   against `_decode`'s)?
7. **The two-sided delta (2.10, 6).** Derive both lists independently; is anything on the Lean side a verdict
   difference in disguise?
8. **Wordings (3).** Does each `says` sentence have one reading? Is any rejected wording of 3.3 still in this
   file or in the plan? Does 3.5 state only what will be true?
9. **Conservativity (5.3, 7, 8.4).** Can anything in item 1 change a verdict, an identity, a code, or a Lean byte
   other than the generated tables and the registry's added lines?
10. **The corpus (8.7).** Does the recorder see every path through which a test submits a source of the unit,
    the wrapper included?
11. **The scratch file (5.1, 8.6).** Run it; do the four examples elaborate and do the printed records equal the
    rows of 8.1?

## 12. Resolved choices in this draft

| # | Choice | Alternative not taken |
|---|---|---|
| R1 | The unit's Lean cases are `speech-elaborate` only | the four `speech-*` kinds, whose later rejections are not source rejections |
| R2 | The domain excludes `source` and the wrapper's envelope members | listing the wordings' rejections as verdict differences, which Lean could never close |
| R3 | The domain excludes a reading-set unit with content or another kind | hooks reading the effective unit for every shape check |
| R4 | The environment is one inherited hook on the stripped environment; the block's own checks are this contract's | the whole environment as one hook (loses the block's T1 checks and the spec's order) |
| R5 | Formula shape and typing are two classifier sets in two phases, the shape's Python side `formula_shape` plus a node count, the typing's `formula_from_data` | one inherited hook per formula (the class rule would need an exemption per formula) |
| R6 | The policy is one inherited hook | an include of `norms@0` under a view (needs a view reading the root; base spec 2.3) |
| R7 | The reading candidates are one classifier whose members mirror the unit checks | fifty separate rows under the `readings` group (the T1 rows would read the raw reading, not the unit it stands for) |
| R8 | The queries come before the policy, against the spec paragraph's order | following the paragraph (neither validator does) |
| R9 | Lean's side of the delta is reported, not enforced and not applied | editing the frozen route (a separate plan) |
| R10 | Both reproducers are engine fixtures (E40, E41) and the tolerance test keeps its assertions | deleting the test |
| R11 | Classes are Python's; most codes are `InvalidInput` | aligning Python's classes to Lean's leading words (changes rejected cells) |
| R12 | The scratch file is written and its command stated; it was not run here | claiming it ran |
