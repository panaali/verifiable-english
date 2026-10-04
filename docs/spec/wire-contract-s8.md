# Wire contracts, stage S8 item 1: `rights@0`, `reports@0` and `ve-units@1` become public (statement specification)

> Status: statement specification, draft 1 (2026-10-04). This is the item-1 statement spec of
> [wire-contract-S8-PLAN.md](wire-contract-S8-PLAN.md) draft 2 (the **plan**). It covers item 1 only: the three
> contracts `rights@0` (base plan 5.3 row 10), `reports@0` (row 11) and `ve-units@1` (row 12), each authored, run
> in shadow, measured and switched to `public`, which is every step of 5.1 of
> [wire-contract-PLAN.md](wire-contract-PLAN.md) (the **base plan**), on the generalised tooling of S5 (the **S5
> spec**, [wire-contract-s5.md](wire-contract-s5.md), 7.1). It builds on [wire-contract.md](wire-contract.md)
> (the **base spec**), [wire-contract-s4.md](wire-contract-s4.md) (the **S4 spec**) and the S5 spec and changes
> no definition of them. The Astra + Fable statement review comes before any build step. No debate was held on
> stage S8 (plan, status paragraph), so that review is the first reading of everything here that the base
> plan's debate did not decide; section 12 lists those choices. Fixtures are implementation obligations, not
> claims of completed tests. Nothing was built or run for this draft: the three tables of section 2 were
> authored by reading the three Python validators and the three Lean routes, the expected records of section 8
> and the expected delta of section 6 were derived by hand, and every `file:line` reference was read on `main`
> at `bb05a08d` and on `wire-s5/integrate` at `c981fe68` and must be re-read at each step. The writer's sandbox
> had no Lean toolchain: the statements of section 5 were written to a scratch file (5.6) with the `#eval`s
> that confirm every number of section 8, but that file was not run; running it is the first step of the build
> (plan, S8-stubs), before this review. Nothing here changes a verdict, an identity, a code, a frozen contract,
> an existing theorem statement or a checker function.

## 0. Scope, one paragraph

After S5 three contracts exist (one public, two in shadow). Item 1 adds three. `rights@0` is the table of what
the Lean rights route checks on a rights source (an environment with a `rights` block and the array of right,
right_lines, limitation, bar and norm unit contents); `reports@0` is the table of what the Lean reports route
checks on a reports document (an environment with a `reports` block and a W2 document with contexts,
assessments, bridges and scoped checks); `ve-units@1` is the table of what Python's quantity admission checks on
a W6a document (an environment with `unit_schema` and `units`, and the P0-shaped document whose statements are
annotated quantities). The first two are authored in the Lean routes' order, the authorities of those units,
and the third in Python's; each is run in shadow against the other language's engine and legacy validator on a
generated and replayed corpus, measured, signed by the DRI and made **public** in the one place where Python
validates a submitted source of the unit and rejects it: the error then carries the contract's record. When a
check of the table fails, the record names the first one that fails and the message is that check's text;
otherwise the message is the validator's. The legacy validators still decide, alone, whether a source is
accepted. Lean's route rows are frozen and do not change; `ve_diagnose` gains the three units. Rust has code for
two of the units but no engine, so it is not run and no Rust text changes. `rights@0` is the first contract with
a view: it includes the pilot's six phases on the environment stripped of its rights constructs, and every
included record carries `path` `/environment` with the inner pointer in `args`.

In this specification: the decisions (1), the definitions, including the three tables (2), the English, one
reading each (3), the diagnostics (4), the Lean statements relied on, the Lean modules and the scratch file
(5), the expected delta of each profile (6), the files and gates of S8.0 and of each unit's measurement and
switch commits (7), the acceptance fixtures (8), the switch gate (9), limits (10), the statement review
checklist (11), and the choices this specification resolves (12).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | Each unit's root is `{"environment", "document"}`: for `rights@0` the document is the array of unit contents the Lean route reads; for `reports@0` the W2 document object the Lean route reads; for `ve-units@1` the P0-shaped admission input of `ve_quantity`'s `document` kind. Each adapter builds it from a route case as the route does | 2.2 |
| D2 | The tables of `rights@0` and `reports@0` are in the Lean routes' order, the authorities'; their texts are Lean's wherever Python's differ, except where Lean's is a JSON-library text, which gets a fixed contract text. The table of `ve-units@1` is in Python's order with Python's texts, except the field-list texts and the quoting of names and literals, which get fixed texts and the `json` renderer. For every unit the Lean route's own text on a one-fault input is compared with the record's and reported (`lean_route_changes`); the listed differences of section 6 are allowed and any other fails the gate | 2.3, 2.4, 2.5, 2.14, 6, 9 |
| D3 | The contract's classes are the authority's: for `rights@0` and `reports@0` the class `checker_error` gives the Lean route's text, for `ve-units@1` the class Python raises. `code` is never written by a switch, so on the first two units the public error's `code` and its record's `class` may differ; that is listed, counted and not enforced | 2.13, 10 |
| D4 | `rights@0` includes `soft-norms@0`'s six phases at `/environment` under the view `soft_source_of_rights`, without `as`: the view gives the stripped environment with no norms, as `decodeRightsEnvironment` does | 2.3 |
| D5 | The envelope, the profile gate, the P0 vocabulary decoder, the formula decoders and the W2 kind decoder are inherited checks until S4 items 3 to 6; so are the shape members of the rights unit decoder and the quoted-package members of the reports content decoder, whose texts are each language's JSON-library texts | 2.3, 2.4, 2.5, 2.6 |
| D6 | One function per unit, `public_rejection`, in a new contract module per unit (`ve/rights_contract.py`, `ve/reports_contract.py`, `ve/units_contract.py`), turns a legacy rejection into the public error; it returns the same error object and never raises | 2.8 |
| D7 | One production call site per unit, inside the handler of the rejection: the two rights statements of `_load_document` (`_environment`, `RightsDocument`), its `ReportsDocument` statement, and `admit_quantity_document` in `_admit_document_python` | 2.9 |
| D8 | The legacy validators are not edited; the gate calls them after the switch through `legacy_validation` of each contract module | 2.2, 7.2 |
| D9 | A public change is a changed message; the complete list on the unit's corpus is measured, stored and signed check by check; at `public`, the gate fails on a change without a signature and on a signature without a change | 2.12, 9 |
| D10 | Each switch raises the unit's revision; `rights@0`'s generated table inlines the pilot's entries, so a revision of `soft-norms@0` regenerates `Tables/Rights.lean` too | 2.11 |
| D11 | The unit registry of `ve_diagnose` gains three entries by an append-only edit of `Diagnose.lean`, the C4 exception S5 recorded, unless the list has moved to `DiagnoseMain.lean` | 5.3 |
| D12 | Rust is not run on any of the three units: it has no engine. Its texts and tolerances stay | 2.2 |
| D13 | The statement set S of `ve-units@1` is defined once and emitted by five classifier entries, at every position a statement occurs; the lint checks the five copies against the definition | 2.5, 8.7 |
| D14 | A unit's domain excludes the inputs on which its two legacy validators would not be validating the same thing; the adapters refuse such cases and the catalogue never builds them | 2.2 |

## 2. Definitions

### 2.1 Terms carried over

| Term | Meaning |
|---|---|
| record, outcome, overlay, residual record, deferred record | base spec 2.7, 2.8 |
| instance, scope, position, order key | base spec 2.6; a scope is a resolved include, and a record under one carries the include id before the check id (`soft/2.7a`) |
| a record under a view | base spec 2.7: its `path` is the include's site and `args.inner_path` is the pointer inside the view |
| inherited check | base spec 2.5, rule 5: a hook or member whose text is the inherited decoder's own, in each language; its `text` and `args` are not compared between engines |
| legacy validator | for each unit, the Python function and the Lean route of 2.2 |
| the gate, the corpus | `conformance/wire_contract_gate.py --unit <unit>` (S5 spec 7.1) and the cases of its `gate_cases` for that unit: tiers 0, A, B, the replayed sources (tier R) and the legacy-difference inputs (tier L) |
| a corpus case that Lean reads | S4 spec 2.1; for these units every corpus case, except a recorded test input that carries a `null` |
| handler-reaching case | S5 spec 2.11: a rejected case on which the call reaches the switched statement, so that the error it raises is that statement's |
| the class rule | the rule of 2.13 for the unit's authority |

A **source** of a unit is a pair of an environment and a document in the unit's root form. The **legacy error**
of a source is the `VEError` that the unit's Python legacy validator raises on it; its **legacy code** is the
error's `code` (a class name: none of the three units has fine codes today) and its **legacy text** is `str` of
the error. The **Lean legacy text** is the `error` string of the Lean route's row, and its **Lean class** is the
one `ve.backends.diagnostics.checker_error` gives it (`ve/backends/diagnostics.py:31–52`): the leading word
before a colon when it names a `VEError` class, else `InvalidInput`.

### 2.2 The three units: roots, adapters, domains, legacy validators

**Roots.** All three contracts have `"input": ["environment", "document"]`.

| Unit | `environment` | `document` |
|---|---|---|
| `rights@0` | a `ve.core@0.2` environment as submitted, with its `rights` block | the array the Lean route reads (rights.md 3.2): `{"source_units": [ids]}` first, then the `content` of every unit of kind `right`, `right_lines`, `limitation`, `bar` or `norm` in document order, as `VE.Rights.Admission.splitDocument` and `ve.document._rights_units` build it |
| `reports@0` | a `ve.core@0.2` environment as submitted, with its `reports` block | the W2 document the Lean route reads (attribution.md 3.2, 3.3): `units` (each with `id`, `span`, `kind`, optional `meaning`, `support`, `content`), `contexts`, `assessments`, `bridges`, `scoped`, `open_terms`, and optionally `graph`; a member the case lacks is absent, not `null` |
| `ve-units@1` | a `ve.core@0.2` environment with `unit_schema` and `units` | the P0-shaped admission input (`ve.document.quantity_admission_input`): `units` (each with `id`, `span`, `kind`, optional `content` a `ve-quantity@1` payload), `graph` (`root`, `nodes`), optional `lemmas`, `open_terms`, `reading_sets`, `narrowings` |

**Adapters.** `rights_source`, `reports_source` and `quantity_source`, in Python and in Lean. Any other kind is
refused as the pilot's adapter refuses one: `{"id", "status": "error", "error": "UnsupportedProfile: case kind
<kind> has no wire contract input"}`.

| Adapter | Case kinds | Root |
|---|---|---|
| `rights_source` | `rights-elaborate`, `rights-projections`, `rights-scope`, `rights-conflict`, `rights-bar`, `rights-certificate` | the case's `environment` and `document` |
| | `admission` | the case's `environment` and the second component of `splitDocument` of the case's `document` (the ids, then the active contents); when the document is not an object with a `units` array of objects, `document` is `null` |
| `reports_source` | `reports-elaborate`, `reports-scoped`, `reports-certificate`, `reports-countermodel`, `reports-status`, `admission` | the case's `environment` and `document` |
| `quantity_source` | `document`; `admission` with a member `document` | the case's `environment` and `document` |
| | `admission` with a member `quantity`, `countermodel`, `certificate`, `count`, `day`, `civil`, `lower`, `render` | refused: `UnsupportedProfile: the case is outside the unit's domain` (single statements and conversions are not documents) |

**Domains.** A unit's domain is the set of sources on which its two legacy validators are compared. The adapter
refuses, with the error `UnsupportedProfile: the case is outside the unit's domain`, a source on which the two
would not be validating the same thing (D14; S5 spec R3):

- `rights@0`: the environment is not an object, or `document` is `null` (an `admission` case whose document has
  no `units` array). Everything else is in the domain, including a document that is not an array (both
  validators refuse it, 4.1) and an environment whose `vocabulary` is not an object (both refuse it; Python by
  a crash, 2.13).
- `reports@0`: the environment is not an object; `document` is not an object; `document` has a member outside
  `units`, `contexts`, `assessments`, `bridges`, `scoped`, `open_terms`, `graph` (the loader refuses `lemmas` and
  `reading_sets` under `reports@0` before `ReportsDocument`, `ve/document.py:463–464`, and reads `narrowings`
  elsewhere); `units` is not an array of objects; a unit's `kind` does not decode under W2's kind decoder with
  the act `wants` admitted (`ve.admission._check_kind(kind, reports=True)`; Lean `decodeKind 16`), or a unit
  lacks `id`, `span` or `kind`; `open_terms` is present and not an array of tokens. These are the loader's W2
  checks (`ve-document@1`, base plan 5.3 row 13), which Python makes before `ReportsDocument` and Lean makes
  inside `decodeDocumentRaw`; both reject such an input, but Python's text is the loader's and not
  `ReportsDocument`'s.
- `ve-units@1`: the environment is not an object with both `unit_schema` and `units` (without them the dispatch
  takes the W2 admission, row 13; with one of the two Python's `Environment` refuses before the W6 checks and
  the Lean route's `exactFields` refuses with a library text); `profiles` lists `risk@0` (the risk route carries
  the extension, `ve/units.py:36–38`); `document` is not an object.

A source inside the domain need not reach a call site. For `rights@0` and `reports@0` an environment that the
loader's own `_environment` or `Environment` statement refuses is in the domain and both validators refuse it;
the record is then witnessed at the function and at `ve_diagnose`, and the call raises today's error without a
record where the refusing statement is not a switched one (2.9, 2.12).

**Legacy validators.** Python, each defined once as `legacy_validation(environment, document)` in the unit's
contract module, for the gate and the recorder:

| Unit | `legacy_validation` | The route's statements it is |
|---|---|---|
| `rights@0` | `ve.rights.correlate(environment, document)`: `RightsEnvironment(environment)`, then `RightsDocument(env, document)` | `_environment(environment_data)` and `RightsDocument(env, _rights_units(units, attached))` of `_load_document` (`ve/document.py:365, 379`); `conformance/rights_differential.py:252` |
| `reports@0` | `env = Environment(environment)`; `ReportsDocument(env, document.get("contexts", []), document.get("assessments", []), document["units"], bridges=document.get("bridges", []), scoped=document.get("scoped", []), open_terms=document.get("open_terms", []))` | `_environment` and `ReportsDocument(...)` of `_load_document` (`ve/document.py:365, 467–469`), the units in the wire form `_wire_unit` gives them |
| `ve-units@1` | `env = Environment(environment)`; `admit_quantity_document(env, document)` | `Environment(environment)` and `admit_quantity_document(env, document)` of `_admit_document_python` (`ve/admission.py:503–507`) |

Lean: `ve_rights_route` with the case kind `rights-elaborate`; `ve_reports_route` with `reports-elaborate`;
`ve_quantity` with `document`. Each is the route to which the unit's sources go. A Lean row with `status`
`error` is a rejection, its `error` string the Lean legacy text, its Lean class as 2.1 defines it. No Lean route
reports a `code`.

**No Rust column.** Rust decodes `ve-units@1` environments and statements (`rust/ve-core/src/units.rs`) and
gates `reports@0` environments (`environment.rs:200–220`), and has no engine (S4 item 2, not started). Under
edit d an implementation that does not complete diagnosis is not compared; Rust is not run on any of the three
units, no Rust text changes, and no Rust tolerance is removed.

### 2.3 The contract `rights@0`, revision 1

**Limits and classes used.** `limits.json` gains `MAX_RIGHTS_UNITS` 1024, `MAX_RIGHTS` 128 and
`MAX_LIMITATIONS` 16 (literals in both validators: `ve/rights.py:187, 270, 272`; `lean/VE/Rights/Wire.lean:286`,
`Correlate.lean:358–359`). `names.json` gains nothing: Lean checks no format of a right, limitation or bar name
beyond the `rights-` prefix (2.13). `"uses": ["limits", "names", "soft-norms@0"]`; adapter `rights_source`;
residual code `RIGHTS_INVALID_INPUT`.

**Codes.** Twenty-two, with Lean's classes (D3): the class `checker_error` gives the Lean route's text.

| Class | Codes |
|---|---|
| `UnsupportedProfile` | `RIGHTS_UNSUPPORTED_PROFILE` |
| `InvalidInput` | `RIGHTS_INVALID_BLOCK`, `RIGHTS_INVALID_DOCUMENT`, `RIGHTS_INVALID_UNIT`, `RIGHTS_UNKNOWN_RIGHT`, `RIGHTS_RESERVED_NAME`, `RIGHTS_INCIDENT_SHAPE`, `RIGHTS_FAN_OUT`, `RIGHTS_HOLDER_SLOT`, `RIGHTS_WITHOUT_INCIDENT`, `RIGHTS_INVALID_LIMITATION`, `RIGHTS_MISSING_DECIDER`, `RIGHTS_INVALID_BAR`, `RIGHTS_SOFT_DEPENDENCY_CYCLE`, `RIGHTS_SOFT_OVER_HARD`, `RIGHTS_NOT_STRATIFIED`, `RIGHTS_INVALID_INPUT` (the `residual` code) |
| `UnknownSymbol` | `RIGHTS_UNKNOWN_SYMBOL` |
| `DuplicateDeclaration` | `RIGHTS_DUPLICATE_DECLARATION` |
| `TypeMismatch` | `RIGHTS_TYPE_MISMATCH` |
| `UnboundVariable` | `RIGHTS_UNBOUND_VARIABLE` |
| `ResourceLimit` | `RIGHTS_RESOURCE_LIMIT` |

The included soft checks keep the pilot's codes and classes (no `as`).

**The table.** `E` abbreviates `/environment`, `B` abbreviates `/environment/vocabulary/rights` and `D`
abbreviates `/document`. A row "group" opens a group; its sub-entries follow, indented by `·`, until the next
row that is not indented. The order is `decodeRightsSource`'s (`lean/VE/Rights/Wire.lean:277–293`): the
profiles, the block's shape, the soft table on the stripped environment, the document array unit by unit, then
`validateRights` (`Correlate.lean:436–445`): `checkBlock`, the limits, names, rights and lines, limitations,
bars, citations, the correlated soft document, decision names, stratification. Texts are Lean's; where Lean's
is a JSON-library text (`fields do not match: …`, `String expected`, `array expected`), the row says so and
gives the fixed text used instead, or marks the member inherited.

Phase 1, `profiles`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 1.1a | `type` `E`: object | `RIGHTS_UNSUPPORTED_PROFILE` | `UnsupportedProfile: profiles must be a sorted unique array` |
| 1.1b | `requires` `E` member `profiles` | as 1.1a | as 1.1a |
| 1.1c | `type` `E/profiles`: array of strings | as 1.1a | as 1.1a |
| 1.2 | `requires` `E/profiles` item `"rights@0"` | as 1.1a | `UnsupportedProfile: rights@0 is required` |
| 1.3 | `requires` `E/profiles` item `"soft-norms@0"` | as 1.1a | `UnsupportedProfile: rights@0 requires soft-norms@0` |
| 1.4 | `requires` `E/profiles` item `"norms@0"` | as 1.1a | `UnsupportedProfile: rights@0 requires norms@0` |

Phase 2, `block` (the shape; `decodeRightsBlock`, `Wire.lean:68–96`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 2.1a | `type` `E/vocabulary`: object | `RIGHTS_INVALID_BLOCK` | `InvalidInput: invalid rights block` |
| 2.1b | `requires` `E/vocabulary` member `rights` | as 2.1a | as 2.1a |
| 2.2 | `keys` `B`: required `holders`, `bearers`; optional `protected`, `alters` | as 2.1a | as 2.1a |
| 2.3 | `type` `B/holders`: array of strings | as 2.1a | as 2.1a |
| 2.4 | `type` `B/bearers`: array of strings | as 2.1a | as 2.1a |
| 2.5 | `type` `B/protected`: array of strings | as 2.1a | as 2.1a |
| 2.6 | `type` `B/alters`: object | as 2.1a | as 2.1a |
| | group `alters` over `B/alters/*` | | |
| · 2.7a | `keys` `@`: required `holder_slot`, `status`; optional `recognition` | as 2.1a | `InvalidInput: alters {key}` |
| · 2.7b | `type` `@/holder_slot`: integer | as 2.1a | as 2.7a |
| · 2.7c | `type` `@/status`: string | as 2.1a | as 2.7a |
| · 2.7d | `type` `@/recognition`: string | as 2.1a | as 2.7a |

Phase 3, `soft`: one include.

| Id | Entry | Says |
|---|---|---|
| soft | include `soft-norms@0`, phases `envelope`, `declarations`, `profiles`, `references`, `semantic`, at `E`, view `soft_source_of_rights`, no `as` | The view gives the object with two members: `environment`, which is `/environment` with `rights@0` removed from `profiles` and the member `rights` removed from `vocabulary`, and `norms`, which is the empty array; every included check reads that object and nothing else of the input. |

Lean runs `Phases.checkSource stripped (.arr #[])` at this point (`Wire.lean:115–118`) and throws the fault's
message; Python runs `SoftEnvironment(raw)` with the block popped (`ve/rights.py:52–68`). With no norms the
pilot's phase `rule-fields` has no instance, so it is not included; of the included phases, the checks 1.1 to
3.5b, 5.1, 5.2a, 5.2b and 6.1 to 6.3 can fail, 3.3b and 3.3c are always masked by 1.3 and 1.4, and 5.3 to 5.9,
6.4a and 6.5a to 6.15 have no reaching input (gaps G2 and G3 of 8.9). A record of this scope has `check`
`soft/<id>`, `phase` `soft`, `path` `/environment` and `args.inner_path` the pointer inside the view
(`/environment/vocabulary/soft/parties/1`); the include's wording is the view's `says` (3.1, 3.2).

Phase 4, `document` (the array and each unit's decoding; `addUnit`, `Wire.lean:235–263`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 4.1 | `type` `D`: array | `RIGHTS_INVALID_DOCUMENT` | `InvalidInput: document must be an array` |
| 4.2 | `max_items` `D`: `MAX_RIGHTS_UNITS` | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: units` |
| | group `units` over `D/*` | | |
| · 4.3 | classifier `rights_unit` at `@`, emits: | | |
| · · 4.3a | a second `source_units` unit | `RIGHTS_INVALID_UNIT` | `InvalidInput: duplicate source_units` |
| · · 4.3b | `source_units` not an array of strings | as 4.3a | `InvalidInput: source_units must list unit ids` |
| · · 4.3c | the unit's decoder refuses its shape: a `displayFields`, `stringField`, `getArr?`, `getNat?`, formula-decoder or `ruleFields` failure of `decodeRight`, `decodeLine`, `decodeLines`, `decodeLimitation`, `decodeCondition`, `decodeBar` or `decodeLineNorm`, in the decoder's order; inherited | as 4.3a | `{message}` |
| · · 4.3d | a line's `kind` outside the four | as 4.3a | `InvalidInput: invalid line kind` |
| · · 4.3e | a `fan_out` value that is not a string | as 4.3a | `InvalidInput: invalid fan_out` |
| · · 4.3f | `cites` not an object | as 4.3a | `InvalidInput: cites must be an object` |
| · · 4.3g | a `cites` entry that is not a non-empty array of strings; returns `key` | as 4.3a | `InvalidInput: cites {key} must list unit ids` |
| · · 4.3h | a `right_lines` unit naming a right not yet declared; returns `value` | `RIGHTS_UNKNOWN_RIGHT` | `UnknownRight: {value}` |
| · · 4.3i | a limitation's `kinds` neither `"all"` nor an array; returns `name` | as 4.3a | `InvalidInput: invalid kinds of limitation {name}` |
| · · 4.3j | a limitation's `decided_by` present and not a string | as 4.3a | `InvalidInput: invalid decider for limitation {name}` |
| · · 4.3k | a condition's `role` neither `"necessary"` nor `"sufficient"` | as 4.3a | `InvalidInput: invalid condition {name}` |
| · · 4.3l | a condition's `decided_by` present and not a string | as 4.3a | `InvalidInput: invalid decider for condition {name}` |
| · · 4.3m | a bar's `reading` neither `"rule"` nor `"query"` | as 4.3a | `InvalidInput: invalid bar reading for {name}` |
| · · 4.3n | a bar's `decided_by` present and not a string | as 4.3a | `InvalidInput: invalid decider for bar {name}` |
| · · 4.3o | a unit whose key set is none of the five forms | as 4.3a | `InvalidInput: invalid rights document unit` |

Phase 5, `block-semantics` (`checkBlock`, `Correlate.lean:240–270`, which Lean runs after every unit is decoded):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 5.1 | classifier `rights_block` at `B`, emits: | | |
| · 5.1a | `holders` or `bearers` empty | `RIGHTS_INVALID_BLOCK` | `InvalidInput: invalid rights block` |
| · 5.1b | a holder or bearer sort not declared; returns `value` | `RIGHTS_UNKNOWN_SYMBOL` | `UnknownSymbol: sort {value}` |
| · 5.1c | a holder repeated | `RIGHTS_DUPLICATE_DECLARATION` | `DuplicateDeclaration: holder {value}` |
| · 5.1d | a bearer repeated | as 5.1c | `DuplicateDeclaration: bearer {value}` |
| · 5.1e | a protected name undeclared, regulated, defined or without a holder-sort argument | as 5.1a | `InvalidInput: protected {value}` |
| · 5.1f | an `alters` act repeated; unreached (object keys are distinct) | as 5.1c | `DuplicateDeclaration: alters {value}` |
| · 5.1g | an `alters` entry whose act is not a permission, whose slot is out of range or not a holder sort, whose status is not a base predicate with that sort, or whose recognition is not an obligation with a bearer subject and that holder sort | as 5.1a | `InvalidInput: alters {value}` |

Phase 6, `rights` (`checkRights` after the block, `Correlate.lean:358–414`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 6.1 | `max_count` of `D/*/right`: `MAX_RIGHTS`, at `D` | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: rights` |
| 6.2 | `max_count` of `D/*/limitation`: `MAX_LIMITATIONS`, at `D` | as 6.1 | `ResourceLimit: limitations` |
| 6.3 | classifier `rights_names` at `D`, emits: | | |
| · 6.3a | a right, limitation, bar or rule name beginning `rights-` | `RIGHTS_RESERVED_NAME` | `InvalidInput: name {value} begins with rights-` |
| · 6.3b | a name repeated, the first being a right | `RIGHTS_DUPLICATE_DECLARATION` | `DuplicateDeclaration: right {value}` |
| · 6.3c | repeated, a limitation | as 6.3b | `DuplicateDeclaration: limitation {value}` |
| · 6.3d | repeated, a bar | as 6.3b | `DuplicateDeclaration: bar` |
| · 6.3e | repeated, a rule | as 6.3b | `DuplicateDeclaration: rule {value}` |
| · 6.3f | a regulated or defined predicate beginning `rights__`, or a generated name already declared | as 6.3a | `InvalidInput: author predicate {value} begins with rights__` |
| · 6.3g | an `over` entry beginning `rights-` | `RIGHTS_UNKNOWN_SYMBOL` | `UnknownSymbol: rule {value}` |
| 6.4 | classifier `rights_lines` at `D`, emits: | | |
| · 6.4a | a right's holder not a holder sort | `RIGHTS_UNKNOWN_SYMBOL` | `UnknownSymbol: sort {value}` |
| · 6.4b | the right's guard ill typed over `[holder]`: a type mismatch; inherited | `RIGHTS_TYPE_MISMATCH` | `{message}` |
| · 6.4c | the same: an unknown predicate, constant or binder sort; inherited | `RIGHTS_UNKNOWN_SYMBOL` | `{message}` |
| · 6.4d | the same: a variable index outside its scope; inherited | `RIGHTS_UNBOUND_VARIABLE` | `{message}` |
| · 6.4e | the guard fails `check` after `typeDiagnostic` passed; unreached | `RIGHTS_INVALID_UNIT` | `InvalidInput: ill-typed right {name}` |
| · 6.4f | a source line or a line instance off the shape table of rights.md 1.2 (`checkSourceLine`, `checkShape`); returns `detail`, the text after `IncidentShape: ` | `RIGHTS_INCIDENT_SHAPE` | `IncidentShape: {detail}` |
| · 6.4g | a fan-out map missing a bearer, repeating one, naming a non-bearer, or mapping to a predicate of another act, role, subject or sorts; returns `detail` | `RIGHTS_FAN_OUT` | `FanOutUndeclared: {detail}` |
| · 6.4h | two object slots of the holder sort and no `holder_slot` | `RIGHTS_HOLDER_SLOT` | `HolderSlotAmbiguous: {name}` |
| · 6.4i | a line instance with more than six carve-outs | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: carve-outs of rule {name}` |
| · 6.4j | a right with no line | `RIGHTS_WITHOUT_INCIDENT` | `RightWithoutIncident: {name}` |
| 6.5 | classifier `rights_limitations` at `D`, emits: | | |
| · 6.5a | an empty `scope` list | `RIGHTS_INVALID_LIMITATION` | `InvalidInput: invalid scope of limitation {name}` |
| · 6.5b | a scope naming an undeclared right | `RIGHTS_UNKNOWN_RIGHT` | `UnknownRight: {value}` |
| · 6.5c | an empty `kinds` list | as 6.5a | `InvalidInput: invalid kinds of limitation {name}` |
| · 6.5d | more than eight conditions | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: conditions` |
| · 6.5e | a condition name that is not an identifier | as 6.5a | `InvalidInput: invalid condition {name}` |
| · 6.5f | a condition `decided_by` that is a string outside the decider class | as 6.5a | `InvalidInput: invalid decider for condition {name}` |
| · 6.5g | a condition name repeated in its limitation | `RIGHTS_DUPLICATE_DECLARATION` | `DuplicateDeclaration: condition {value}` |
| · 6.5h | a limitation `decided_by` that is a string outside the decider class | as 6.5a | `InvalidInput: invalid decider for limitation {name}` |
| · 6.5i | no limitation `decided_by` | `RIGHTS_MISSING_DECIDER` | `MissingExceptionDecider: limitation {name}` |
| 6.6 | classifier `rights_bar` at `D`, emits: | | |
| · 6.6a | a second bar | `RIGHTS_DUPLICATE_DECLARATION` | `DuplicateDeclaration: bar` |
| · 6.6b | a bar `decided_by` outside the decider class | `RIGHTS_INVALID_BAR` | `InvalidInput: invalid decider for bar {name}` |
| 6.7 | hook `citations_declared` at `D`; returns `value` | `RIGHTS_UNKNOWN_SYMBOL` | `UnknownSymbol: unit {value}` |

Phase 7, `correlated` (`validateSoft (correlate D)`, the decision names, `rightsSemanticCheck`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 7.1 | classifier `correlated_soft` at `D`, emits the pilot's semantic set over `T″` (its members 6.5a to 6.15 in the pilot's order and with the pilot's texts, ids 7.1a to 7.1m): | | |
| · 7.1a | 6.5a | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: AST exceeds 10,000 nodes` |
| · 7.1b | 6.5b; returns `detail` | `RIGHTS_SOFT_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |
| · 7.1c | 6.6 | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: precedence depth` |
| · 7.1d | 6.7; returns `detail` | `RIGHTS_SOFT_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |
| · 7.1e | 6.8; returns `detail` | `RIGHTS_SOFT_OVER_HARD` | `SoftOverHard: {detail}` |
| · 7.1f | 6.9; returns `detail` | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: derived carve-out{detail}` |
| · 7.1g | 6.10a; returns `detail` | `RIGHTS_SOFT_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |
| · 7.1h | 6.10b; inherited | `RIGHTS_RESOURCE_LIMIT` | `{message}` |
| · 7.1i | 6.11 | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: generated soft premise` |
| · 7.1j | 6.12; returns `detail` | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: generated norm layer {detail}` |
| · 7.1k | 6.13; returns `detail` | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: generated conflict target {detail}` |
| · 7.1l | 6.14 | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: generated background` |
| · 7.1m | 6.15 | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: generated norm layers` |
| 7.2 | hook `decision_names_fit` at `D`; returns `name` | `RIGHTS_RESOURCE_LIMIT` | `ResourceLimit: identifier {name} exceeds 64 bytes` |
| 7.3 | hook `rights_stratified` at `D` | `RIGHTS_NOT_STRATIFIED` | `InvalidInput: rights document is not stratified` |

**What is not in the table, and why.** Python's own texts for the block (`InvalidInput: holder must be a nonempty
list`, `UnknownSymbol: sort s` at the environment, `InvalidInput: alters act` with Python's conditions) and
for the units (`InvalidInput: right`, `InvalidInput: right_lines`, `InvalidInput: limitation`,
`InvalidInput: bar`, `InvalidInput: rights unit`, `InvalidInput: incident line`, `InvalidInput: incident line
fields`, `InvalidInput: invalid fan-out`, `InvalidInput: incident norm`, `InvalidInput: line … has predicate and
fan_out`, `InvalidInput: authored precedence cites a generated rule`, `ResourceLimit: units` for a non-list):
each is a Python check whose Lean counterpart is one of the rows above with Lean's text, and the delta report
lists the message change (section 6). Four Python checks have no Lean counterpart and are S8-pre candidates of
2.13, residuals until fixed: `_name` (`InvalidInput: invalid rights name …`), the required `guard` of a right,
the required `decided_by` of a condition, and the `rights__` prefix on a base predicate. The Lean route's `UnknownRight`
inside `linesOf` and the fall-through texts of `decodeRightsSource` after `checkSource` (`UnsupportedProfile:
rights route with definitions is not implemented`, `… with data flags …`) are unreachable: the soft phases'
3.5a and 3.5b refuse those environments first. The order inside each classifier set is the Lean function's and
is test-enforced; the Python classifiers of 2.6 are walks in that order.

**Planned tiers.** 32 numbered checks: T1 1.1 to 1.4, 2.1 to 2.7, 4.1, 4.2, 6.1, 6.2 (11, counting a lettered
row set as one); T2 not inherited 6.7, 7.2, 7.3 (3); T3 4.3, 5.1, 6.3, 6.4, 6.5, 6.6, 7.1 (7); the include
`soft` counts as the pilot's 67, under a view (coarse). `n1 + n2` is 14 of 21 own checks; the gate reports the
counts and requires none (S5 spec R9).

### 2.4 The contract `reports@0`, revision 1

**Limits and classes used.** `limits.json` gains `MAX_UNITS` 10000, `MAX_CONTEXTS` 256 and `MAX_ASSESSMENTS` 256
(`ve/reports.py:121–122`; `lean/VE/Attribution/Wire.lean:385, 389, 391`). `names.json` gains `token`: `first`
and `rest` `A-Za-z0-9_.-`, `min_bytes` 1, `max_bytes` 64 (`ve/admission.py:26, 42–44`;
`VE.Route.Admission.token`) and `not_reports_reserved`: `forbid_prefix` `["reports__"]`. `"uses": ["limits",
"names"]`; adapter `reports_source`; residual code `REPORTS_INVALID_INPUT`.

**Codes.** Thirty-one, with Lean's classes.

| Class | Codes |
|---|---|
| `UnsupportedProfile` | `REPORTS_UNSUPPORTED_PROFILE`, `REPORTS_NEEDS_BLOCK` |
| `InvalidInput` | `REPORTS_INVALID_ENVELOPE`, `REPORTS_INVALID_VOCABULARY`, `REPORTS_INVALID_BLOCK`, `REPORTS_RESERVED_PREDICATE`, `REPORTS_INVALID_VERBALISATION`, `REPORTS_RESERVED_VERBALISATION`, `REPORTS_INVALID_DOCUMENT`, `REPORTS_INVALID_UNIT`, `REPORTS_UNSUPPORTED_ACT`, `REPORTS_INVALID_ASSESSMENT`, `REPORTS_INVALID_LITERAL`, `REPORTS_INVALID_CONTENT`, `REPORTS_KIND_MISMATCH`, `REPORTS_INVALID_META`, `REPORTS_INVALID_CONTEXT`, `REPORTS_CONTEXT_TENSE`, `REPORTS_INVALID_BRIDGE`, `REPORTS_INVALID_SCOPED`, `REPORTS_OPEN_COMPLEMENT`, `REPORTS_UNKNOWN_HOLDER`, `REPORTS_HOLDER_SORT`, `REPORTS_UNKNOWN_CONTEXT`, `REPORTS_UNKNOWN_ASSESSMENT`, `REPORTS_HASH_COLLISION`, `REPORTS_SCOPED_TARGET`, `REPORTS_SCOPED_ENVIRONMENT`, `REPORTS_BRIDGE_TARGET`, `REPORTS_BRIDGE_KIND`, `REPORTS_INVALID_INPUT` (the `residual` code) |
| `UnknownSymbol` | `REPORTS_UNKNOWN_SYMBOL` |
| `DuplicateDeclaration` | `REPORTS_DUPLICATE_DECLARATION` |
| `ResourceLimit` | `REPORTS_RESOURCE_LIMIT` |

`UnsupportedAct`, `KindMismatch`, `ContextTense`, `OpenComplement`, `UnknownHolder`, `HolderSort`,
`UnknownContext`, `UnknownAssessment`, `HashCollision`, `ScopedTarget`, `ScopedEnvironment`, `BridgeTarget` and
`BridgeKindMismatch` are leading words that name no `VEError` class, so their class is `InvalidInput` in both
languages (Python raises them as `VEError`).

**The table.** `E` abbreviates `/environment`, `V` abbreviates `/environment/vocabulary`, `R` abbreviates
`/environment/vocabulary/reports` and `D` abbreviates `/document`. The order is `decodeEnvironment`'s
(`Wire.lean:43–87`), then `decodeDocumentRaw`'s (`:377–408`), then `firstFailure`'s (`:417–474`), which is the
text the route gives after a successful raw decode (5.5).

Phase 1, `environment`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 1.1 | `exact_keys` `E`: `language`, `profiles`, `spec_revision`, `vocabulary` | `REPORTS_INVALID_ENVELOPE` | `InvalidInput: invalid environment envelope` (Lean: a library text) |
| 1.2 | `const` `E/language`: `"ve.core@0.2"` | `REPORTS_UNSUPPORTED_PROFILE` | `UnsupportedProfile: Unsupported language` |
| 1.3 | `type` `E/profiles`: array of strings | as 1.2 | `UnsupportedProfile: profiles must be a sorted unique array` |
| 1.4 | `sorted_unique` `E/profiles` | as 1.2 | `UnsupportedProfile: profiles must be sorted and unique` |
| 1.5 | `requires` `E/profiles` item `"reports@0"` | as 1.2 | `UnsupportedProfile: reports@0 is required` |
| 1.6 | hook `fol_family` at `E/profiles`, inherited: the frozen classifier on the list without `reports@0` answers `.fol` | as 1.2 | `{message}` |
| 1.7 | `excludes` `E/profiles` item `"data@0"` | as 1.2 | `UnsupportedProfile: reports@0 with data@0 layers` |
| 1.8 | `excludes` `E/profiles` item `"definitions@0"` | as 1.2 | `UnsupportedProfile: reports@0 with definitions@0 layers` |
| 1.9 | `excludes` `E/profiles` item `"norms@0"` | as 1.2 | `UnsupportedProfile: reports@0 with norms@0 layers` |
| 1.10 | `const` `E/spec_revision`: `"ve-v0.2-expand2-2026-09-25"` | as 1.2 | `UnsupportedProfile: Unsupported specification revision {value}` |
| 1.11a | `type` `V`: object | `REPORTS_NEEDS_BLOCK` | `UnsupportedProfile: reports@0 needs a reports block` |
| 1.11b | `requires` `V` member `reports` | as 1.11a | as 1.11a |
| 1.12 | `exact_keys` `V`: `sorts`, `predicates`, `constants`, `reports` | `REPORTS_INVALID_VOCABULARY` | `InvalidInput: invalid vocabulary` (Lean: a library text) |
| 1.13 | `exact_keys` `R`: `holders`, `evidence` | `REPORTS_INVALID_BLOCK` | `InvalidInput: invalid reports block` (Lean: a library text) |
| 1.14 | `type` `R/holders`: array of strings | as 1.13 | as 1.13 |
| 1.15 | `type` `R/evidence`: string | as 1.13 | as 1.13 |
| 1.16 | `type` `V/predicates`: object | as 1.12 | as 1.12 |
| | group `author-predicates` over `V/predicates/*` | | |
| · 1.17 | `name` on key `@`: class `not_reports_reserved` | `REPORTS_RESERVED_PREDICATE` | `InvalidInput: author predicate {key} begins with reports__` |
| 1.18 | `type` `V/constants`: object | as 1.12 | as 1.12 |
| | group `constant-verbalisations` over `V/constants/*` | | |
| · 1.19 | hook `constant_verbalisation` at `@/verbalisation`, when `@/verbalisation` is present; inherited | `REPORTS_INVALID_VERBALISATION` | `{message}` |
| 1.20 | hook `p0_vocabulary` at `V`, inherited: the P0 vocabulary decoder on `sorts`, `predicates` and `constants` with every `verbalisation` removed, under the profiles without `reports@0` | as 1.12 | `{message}` |
| 1.21 | hook `holders_well_formed` at `R/holders` | as 1.13 | `InvalidInput: holders must be 1 to 8 distinct sorts` |
| | group `holders` over `R/holders/*` | | |
| · 1.22 | hook `holder_sort_declared` at `@` | `REPORTS_UNKNOWN_SYMBOL` | `UnknownSymbol: holder sort {value}` |
| 1.23 | hook `evidence_sort_declared` at `R/evidence` | as 1.22 | `UnknownSymbol: evidence sort` |
| 1.24 | hook `holder_verbalisation_free` at `V/constants` | `REPORTS_RESERVED_VERBALISATION` | `InvalidInput: holder verbalisation reserved` |

Phase 2, `document` (`decodeDocumentRaw`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 2.1 | `keys` `D`: required `units`; optional `graph`, `lemmas`, `open_terms`, `reading_sets`, `narrowings`, `contexts`, `assessments`, `bridges`, `scoped` | `REPORTS_INVALID_DOCUMENT` | `InvalidInput: invalid document fields` (Lean: a library text) |
| 2.2 | `type` `D/units`: array | as 2.1 | `InvalidInput: units must be a list` (Lean: a library text) |
| | group `units` over `D/units/*` | | |
| · 2.3 | `type` `@/id`: string | `REPORTS_INVALID_UNIT` | `invalid unit id {value:json}` (Lean: a library text) |
| · 2.4 | `name` `@/id`: `token` | as 2.3 | `invalid unit id {value}` |
| · 2.5 | `type` `@/span`: an array of exactly 2 elements: an integer, an integer | as 2.3 | `invalid span` |
| · 2.6 | hook `span_ordered` at `@/span` | as 2.3 | `invalid span` |
| · 2.7 | classifier `report_content` at `@`, emits (`decodeUnit` and `decodeContent`, `Wire.lean:169–198, 329–354`): | | |
| · · 2.7a | a report unit without exactly `id`, `span`, `kind`, `content`, `meaning`, `support`, or a W2 unit with a key outside `id`, `span`, `kind`, `content`, `meaning`, `support` | as 2.3 | `InvalidInput: unit {id} fields` (Lean: a library text) |
| · · 2.7b | a content that is not an object with one of the tags, a top-level content that is not a report, assessment or negated node, a W2 content that is not `{"ast": …}`, a content on a quoted kind, or `fence` content | as 2.3 | `InvalidInput: invalid content for {id}` |
| · · 2.7c | a report's act outside the four; returns `act` | `REPORTS_UNSUPPORTED_ACT` | `UnsupportedAct: {act} (reports@0 admits says, believes, wants, intends)` |
| · · 2.7d | an assessment's judgment outside the two; returns `judgment` | `REPORTS_INVALID_ASSESSMENT` | `InvalidInput: unknown judgment {judgment}` |
| · · 2.7e | a `literal` that is not a non-empty string | `REPORTS_INVALID_LITERAL` | `InvalidInput: literal` |
| · · 2.7f | a `literal` over 4,096 bytes | `REPORTS_RESOURCE_LIMIT` | `ResourceLimit: literal bytes` |
| · · 2.7g | a `negated` operand that is not a report or assessment node | as 2.3 | `InvalidInput: negated operand in {id}` |
| · · 2.7h | a formula, quoted norm package or quoted definition package refused by its frozen decoder; inherited | `REPORTS_INVALID_CONTENT` | `{message}` |
| · · 2.7i | the W2 kind does not match the tree | `REPORTS_KIND_MISMATCH` | `KindMismatch: {id}` |
| · · 2.7j | the content decoder's fuel (40) exhausted; unreached (a matching kind of that depth is outside the domain) | `REPORTS_RESOURCE_LIMIT` | `ResourceLimit: content depth` |
| · 2.8 | hook `meaning_shape` at `@/meaning`, when `@/meaning` is present | `REPORTS_INVALID_META` | `invalid meaning status` |
| · 2.9 | `type` `@/support`: string, when `@/support` is present | as 2.8 | `InvalidInput: support of {id}` (Lean: a library text) |
| 2.10 | `max_items` `D/units`: `MAX_UNITS` | `REPORTS_RESOURCE_LIMIT` | `ResourceLimit: unit count` |
| | group `unit-ids` over `D/units/*/id` | | |
| · 2.11 | `unique_so_far` `@` | `REPORTS_INVALID_UNIT` | `duplicate unit id` |
| 2.12 | hook `spans_sorted` at `D/units` | as 2.11 | `unit spans must be sorted and non-overlapping` |
| 2.13 | `type` `D/contexts`: array | `REPORTS_INVALID_CONTEXT` | `InvalidInput: contexts must be a list` (Lean: a library text) |
| | group `contexts` over `D/contexts/*` | | |
| · 2.14 | classifier `context_record` at `@`, emits (`decodeContext`, `:208–224`): | | |
| · · 2.14a | not an object with `id`, `tense`, `description` and optionally `reference_time`, or one of them not a string | as 2.13 | `InvalidInput: context {id}` (Lean: a library text) |
| · · 2.14b | an `id` that is not a token | as 2.13 | `InvalidInput: invalid context id {id}` |
| · · 2.14c | a `tense` outside the three | `REPORTS_CONTEXT_TENSE` | `ContextTense: {id}` |
| · · 2.14d | a `reference_time` that is not a token | as 2.13 | `InvalidInput: invalid reference time for {id}` |
| · · 2.14e | an empty `description` | as 2.13 | `InvalidInput: context {id} description` |
| · · 2.14f | a `description` over 200 bytes | `REPORTS_RESOURCE_LIMIT` | `ResourceLimit: context description` |
| 2.15 | `max_items` `D/contexts`: `MAX_CONTEXTS` | `REPORTS_RESOURCE_LIMIT` | `ResourceLimit: contexts` |
| 2.16 | `type` `D/assessments`: array | `REPORTS_INVALID_ASSESSMENT` | `InvalidInput: assessments must be a list` (Lean: a library text) |
| | group `assessments` over `D/assessments/*` | | |
| · 2.17 | classifier `assessment_record` at `@`, emits (`decodeAssessment`, `:226–244`): | | |
| · · 2.17a | no `decided_by` | as 2.16 | `InvalidInput: assessment {id} needs decided_by` |
| · · 2.17b | not exactly the nine keys, a field of the wrong type, a `jurisdiction` that is not a token, a `version` below 1, or an empty factor or precedent | as 2.16 | `InvalidInput: assessment {id}` |
| · · 2.17c | an `id` that is not a token | as 2.16 | `InvalidInput: invalid assessment id {id}` |
| · · 2.17d | a criterion refused by the P0 formula decoder; inherited | `REPORTS_INVALID_CONTENT` | `{message}` |
| 2.18 | `max_items` `D/assessments`: `MAX_ASSESSMENTS` | `REPORTS_RESOURCE_LIMIT` | `ResourceLimit: assessments` |
| | group `bridges` over `D/bridges/*` | | |
| · 2.19 | classifier `bridge_record` at `@`, emits (`decodeBridge`, `:258–269`): | | |
| · · 2.19a | not an object with `id`, `unit`, `accepted_by`, `reason` and optionally `path`, or a field of the wrong type | `REPORTS_INVALID_BRIDGE` | `InvalidInput: bridge` |
| · · 2.19b | a `path` not of the form `1(.1)*`; returns `path` | as 2.19a | `InvalidInput: bridge path {path}` |
| | group `scoped` over `D/scoped/*` | | |
| · 2.20 | classifier `scoped_record` at `@`, emits (`decodeScoped`, `decodePath`, `:247–283`): | | |
| · · 2.20a | not an object with `id`, `payloads`, `conclusion` and optionally `certificate`, `envelope`, a field of the wrong type, or a `conclusion` that is not `{"ast": …}` | `REPORTS_INVALID_SCOPED` | `InvalidInput: scoped` |
| · · 2.20b | a payload path neither a string nor `{"unit", "path"}` with `path` of the form `1(.1)*`; returns `path` | as 2.20a | `InvalidInput: bridge path {path}` |
| · · 2.20c | the conclusion refused by the formula decoder; inherited | `REPORTS_INVALID_CONTENT` | `{message}` |
| · · 2.20d | an `envelope` without a `certificate` | as 2.20a | `InvalidInput: envelope without a certificate on scoped check {id}` |

Phase 3, `wellformed` (`WellFormedReports`, in `firstFailure`'s order):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 3.1 | classifier `reports_wellformed` at `D`, emits: | | |
| · 3.1a | a context id repeated | `REPORTS_DUPLICATE_DECLARATION` | `DuplicateDeclaration: context {id}` |
| · 3.1b | an assessment id repeated | as 3.1a | `DuplicateDeclaration: assessment {id}` |
| · 3.1c | a bridge id repeated | as 3.1a | `DuplicateDeclaration: bridge {id}` |
| · 3.1d | a scoped check id repeated | as 3.1a | `DuplicateDeclaration: scoped {id}` |
| · 3.1e | an assessment's context not a constant of the evidence sort; returns `context` | `REPORTS_UNKNOWN_SYMBOL` | `UnknownSymbol: evidence context {context}` |
| · 3.1f | an assessment's `decided_by` not a token | `REPORTS_INVALID_ASSESSMENT` | `InvalidInput: assessment {id} needs decided_by` |
| · 3.1g | an assessment criterion not closed and typed over `E` | `REPORTS_OPEN_COMPLEMENT` | `OpenComplement: assessment {id} criteria` |
| · 3.1h | a unit's content deeper than 16; unreached (its kind is deeper than 16, outside the domain) | `REPORTS_RESOURCE_LIMIT` | `ResourceLimit: content depth in {id}` |
| · 3.1i | a report holder not a constant; returns `holder` | `REPORTS_UNKNOWN_HOLDER` | `UnknownHolder: {holder}` |
| · 3.1j | a report holder not of a holder sort | `REPORTS_HOLDER_SORT` | `HolderSort: {holder} is not of a holder sort` |
| · 3.1k | a report context not declared; returns `context` | `REPORTS_UNKNOWN_CONTEXT` | `UnknownContext: {context}` |
| · 3.1l | an assessment record not declared; returns `record` | `REPORTS_UNKNOWN_ASSESSMENT` | `UnknownAssessment: {record}` |
| · 3.1m | a negated operand that is not a statement; unreached (2.7g) | `REPORTS_INVALID_UNIT` | `InvalidInput: negated operand in {id}` |
| · 3.1n | a formula node, or a definition package's statement, not closed and typed over its environment | `REPORTS_OPEN_COMPLEMENT` | `OpenComplement: {id}` |
| · 3.1o | two distinct digested objects with one digest; unreached | `REPORTS_HASH_COLLISION` | `HashCollision: two distinct canonical objects with one digest` |
| · 3.1p | a scoped check with more than 64 payloads | `REPORTS_RESOURCE_LIMIT` | `ResourceLimit: scoped payloads` |
| · 3.1q | a payload path that does not resolve to a formula node | `REPORTS_SCOPED_TARGET` | `ScopedTarget: {id}` |
| · 3.1r | payloads over two environments, or a conclusion not closed over theirs | `REPORTS_SCOPED_ENVIRONMENT` | `ScopedEnvironment: {id}` |
| · 3.1s | a bridge target that does not resolve; returns `unit` | `REPORTS_BRIDGE_TARGET` | `BridgeTarget: {unit}` |
| · 3.1t | a bridge target that is a norm or definition node or lies under a pinned environment; returns `unit`, `depth` | `REPORTS_BRIDGE_KIND` | `BridgeKindMismatch: {unit}, {depth}` |
| · 3.1u | a `support` outside W2's eight | `REPORTS_INVALID_META` | `InvalidInput: support of {id}` |
| · 3.1v | a root `unformalised` kind whose reason differs from the meaning's | as 3.1u | `InvalidInput: unformalised kind reason does not match meaning of {id}` |
| · 3.1w | a meaning that is not W2's, an `open` list naming an undeclared and ungenerated term, a `specified` report unit with an assessment node, or an `open` one missing a generated name | as 3.1u | `InvalidInput: meaning of {id}` |
| · 3.1x | a generated name declared, over 64 bytes or repeated, or the predicates over `MAX_PREDICATES` | `REPORTS_RESOURCE_LIMIT` | `ResourceLimit: MAX_PREDICATES` |
| · 3.1y | `WellFormedReports` false for no listed reason; unreached | `REPORTS_INVALID_INPUT` | `InvalidInput: the document is not well-formed` |

**What is not in the table, and why.** A unit's `kind`, `lemmas`, `reading_sets`, `narrowings` and the tokens
of `open_terms` are the loader's W2 checks (domain, 2.2). Python's `ResourceLimit: bridges or scoped` (more
than 1,000 bridges or 256 scoped checks) has no Lean counterpart (`decodeDocumentRaw` bounds neither): it is an
S8-pre candidate (2.13) and, until fixed, a residual. Python's `UnsupportedProfile: reports reading choices
await the Lean route` needs `choices`, which no wire document carries. The Lean route's
`UnsupportedProfile: reports@0 with definitions@0 layers` after the vocabulary decoder is unreachable (1.8
refuses the profile first). Python's `ReportsConformance` texts belong to the three-way comparison, after
validation.

**Planned tiers.** 42 numbered checks: T1 1.1 to 1.5, 1.7 to 1.18, 2.1 to 2.5, 2.9 to 2.11, 2.13, 2.15, 2.16,
2.18 (27); T2 not inherited 1.21 to 1.24, 2.6, 2.8, 2.12 (7); inherited hooks 1.6, 1.19, 1.20 (3); T3 2.7, 2.14,
2.17, 2.19, 2.20, 3.1 (6). `n1 + n2` is 34 of 42.

### 2.5 The contract `ve-units@1`, revision 1

**Limits and classes used.** `limits.json` gains `MAX_UNIT_TAGS` 64, `MAX_GRAPH_NODES` 1000 and
`MAX_LEMMA_LEAVES` 1000 (`ve/units.py:94`; `ve/quantity_admission.py:150, 292`; `lean/VE/Time/Wire.lean:261`,
`Document.lean:531, 564`) and uses `MAX_UNITS` (2.4). `names.json` gains `currency`: `first` and `rest` `A-Z`,
`min_bytes` 3, `max_bytes` 3 (`ve/units.py:110`; `Wire.lean:150`), and uses `token` (2.4). `"uses": ["limits",
"names"]`; adapter `quantity_source`; residual code `UNITS_INVALID_INPUT`.

**Codes.** Thirty, with Python's classes (D3).

| Class | Codes |
|---|---|
| `InvalidInput` | `UNITS_INVALID_ENVELOPE`, `UNITS_INVALID_DECLARATION`, `UNITS_DISPLAY_COLLISION`, `UNITS_INVALID_VOCABULARY`, `UNITS_INVALID_SLOT`, `UNITS_UNKNOWN_UNIT`, `UNITS_TAG_COLLISION`, `UNITS_INVALID_VERBALISATION`, `UNITS_VERBALISATION_COLLISION`, `UNITS_INVALID_DOCUMENT`, `UNITS_INVALID_UNIT`, `UNITS_INVALID_KIND`, `UNITS_INVALID_STATEMENT`, `UNITS_UNIT_PRECISION`, `UNITS_INVALID_DATE`, `UNITS_DATE_RANGE`, `UNITS_INVALID_DECIMAL`, `UNITS_UNKNOWN_SYMBOL`, `UNITS_UNBOUND_VARIABLE`, `UNITS_INVALID_LEMMA`, `UNITS_INVALID_READING_SET`, `UNITS_INVALID_NODE`, `UNITS_INVALID_CERTIFICATE`, `UNITS_GRAPH_REJECTED`, `UNITS_ADMISSION_ERROR`, `UNITS_INVALID_INPUT` (the `residual` code) |
| `UnsupportedProfile` | `UNITS_UNSUPPORTED_PROFILE` |
| `ResourceLimit` | `UNITS_RESOURCE_LIMIT` |
| `SyntaxError` | `UNITS_INVALID_INTEGER` |
| `TypeMismatch` | `UNITS_TYPE_MISMATCH` |

`UnknownUnit`, `UnitPrecision`, `InvalidDate`, `DateRange`, `UnitScale`, `DisplayCollision` and
`VerbalisationCollision` are leading words that name no class: Python raises them as `VEError`
(`InvalidInput`), and so does `checker_error` for Lean's texts. `UNITS_ADMISSION_ERROR` is declared
`InvalidInput`, because `AdmissionError` is not one of the ten classes a contract may name (base spec 2.2); its
checks are exempt from the class rule (2.13), and whether the format should gain that class is put to the
review (12, open point 4). `UNITS_UNBOUND_VARIABLE` is `InvalidInput` because `ve/units.py:373` raises
`VEError`, not `UnboundVariable`.

**The table.** `E` abbreviates `/environment`, `U` abbreviates `/environment/units`, `V` abbreviates
`/environment/vocabulary` and `D` abbreviates `/document`. The order is `Environment._decode`'s
(`ve/environment.py:315–612`) for the environment, with one deviation stated at 3.1, and
`admit_quantity_document`'s (`ve/quantity_admission.py:264–318`) for the document. Texts are Python's; the
field-list texts (`Incorrect fields (missing=[…], unknown=[…])`, `fields do not match: …`) become fixed texts,
since a template cannot render the key lists, and a name or literal that Python spells with `repr` is spelled
as compact JSON (`{value:json}`).

Phase 1, `envelope`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 1.1 | `exact_keys` `E`: `language`, `profiles`, `spec_revision`, `vocabulary`, `unit_schema`, `units` | `UNITS_INVALID_ENVELOPE` | `InvalidInput: invalid environment envelope` |
| 1.2 | hook `p0_envelope_gate` at `E`, inherited: the language and the frozen profile classifier (`checker_family`; Lean `Gate.classify`) | `UNITS_UNSUPPORTED_PROFILE` | `{message}` |
| 1.3 | `const` `E/spec_revision`: `"ve-v0.2-expand2-2026-09-25"` | as 1.2 | `UnsupportedProfile: Unsupported specification revision {value}` |
| 1.4 | hook `w6_profiles` at `E/profiles`: the list is `["order@0", "relational-fol@0", "time@0"]` or that list with `"documents@1"` first | as 1.2 | `UnsupportedProfile: ve-units@1 requires exactly order@0, relational-fol@0 and time@0, optionally with documents@1` |

Phase 2, `units` (`validate_units`, `ve/units.py:88–130`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 2.1 | `const` `E/unit_schema`: `"ve-units@1"` | `UNITS_UNSUPPORTED_PROFILE` | `UnsupportedProfile: Unsupported unit schema` |
| 2.2 | `type` `U`: object | `UNITS_INVALID_DECLARATION` | `units must be an object` |
| 2.3 | `max_items` `U`: `MAX_UNIT_TAGS` | `UNITS_RESOURCE_LIMIT` | `ResourceLimit: At most 64 unit tags` |
| | group `tags` over `U/*` | | |
| · 2.4 | hook `unit_tag_valid` at `@`: the key is an identifier (`[a-z][a-z0-9_]*`, at most 64 bytes) and not `dimensionless` | as 2.2 | `Invalid unit tag {key:json}` |
| · 2.5 | `exact_keys` `@`: `scale`, `display` | as 2.2 | `InvalidInput: invalid unit record` |
| · 2.6 | `type` `@/scale`: string | as 2.2 | `String expected` |
| · 2.7 | classifier `unit_scale` at `@/scale`, emits (`_scale`; Lean `decodeScale`): | | |
| · · 2.7a | more than 40 characters | `UNITS_RESOURCE_LIMIT` | `ResourceLimit: numeral length` |
| · · 2.7b | not `-?[0-9]+` | as 2.2 | `invalid integer` |
| · · 2.7c | not canonical | as 2.2 | `non-canonical integer` |
| · · 2.7d | not `1` followed by zeros | as 2.2 | `UnitScale({key}): expected a positive power of ten` |
| · 2.8 | `type` `@/display`: object | as 2.2 | `Invalid display for {key}` |
| · 2.9 | `requires` `@/display` member `kind` | as 2.2 | `Invalid display for {key}` |
| · 2.10 | `type` `@/display/kind`: string | as 2.2 | `String expected` |
| · 2.11 | `enum` `@/display/kind`: `"percent"`, `"money"`, `"decimal"`, `"iso_date"` | as 2.2 | `Unknown display kind {value}` |
| · 2.12 | `exact_keys` `@/display`: `kind`, when `@/display/kind` is `"percent"` | as 2.2 | `InvalidInput: invalid display fields for {key}` |
| · 2.13 | `keys` `@/display`: required `kind`, `currency`; optional `input_symbol`, when `@/display/kind` is `"money"` | as 2.2 | as 2.12 |
| · 2.14 | `type` `@/display/currency`: string, when `@/display/kind` is `"money"` | as 2.2 | `String expected` |
| · 2.15 | `name` `@/display/currency`: `currency`, when `@/display/kind` is `"money"` | as 2.2 | `Invalid currency for {key}` |
| · 2.16 | `type` `@/display/input_symbol`: string, when `@/display/kind` is `"money"` | as 2.2 | `String expected` |
| · 2.17 | classifier `display_string_trailing` at `@/display/input_symbol`, when `@/display/kind` is `"money"` and `@/display/input_symbol` is present, emits: | | |
| · · 2.17a | empty | as 2.2 | `Display string must be nonempty` |
| · · 2.17b | over 256 characters | `UNITS_RESOURCE_LIMIT` | `ResourceLimit: Display string exceeds 256 characters` |
| · · 2.17c | a word empty or holding a space character, one trailing space allowed | as 2.2 | `Display string {value:json} must be whitespace-normalized` |
| · 2.18 | `keys` `@/display`: required `kind`, `label`; optional `placement`, when `@/display/kind` is `"decimal"` | as 2.2 | as 2.12 |
| · 2.19 | `type` `@/display/label`: string, when `@/display/kind` is `"decimal"` | as 2.2 | `String expected` |
| · 2.20 | classifier `display_string` at `@/display/label`, when `@/display/kind` is `"decimal"`, emits 2.20a to 2.20c as 2.17a to 2.17c, with no trailing space allowed | | |
| · 2.21 | `type` `@/display/placement`: string, when `@/display/kind` is `"decimal"` | as 2.2 | `String expected` |
| · 2.22 | `enum` `@/display/placement`: `"prefix"`, `"suffix"`, when `@/display/kind` is `"decimal"` | as 2.2 | `Invalid placement for {key}` |
| · 2.23 | `exact_keys` `@/display`: `kind`, when `@/display/kind` is `"iso_date"` | as 2.2 | as 2.12 |
| · 2.24 | hook `iso_date_is_day` at `@`, when `@/display/kind` is `"iso_date"`: the key is `day` and the scale `"1"` | as 2.2 | `iso_date requires day at scale 1` |
| · 2.25 | hook `reserved_day` at `@`: a record under the key `day` is exactly `{"scale": "1", "display": {"kind": "iso_date"}}` | as 2.2 | `Reserved unit day has a fixed declaration` |
| · 2.26 | hook `reserved_elapsed_day` at `@`: a record under the key `elapsed_day` is exactly `{"scale": "1", "display": {"kind": "decimal", "label": "days"}}` | as 2.2 | `Reserved unit elapsed_day has a fixed declaration` |
| 2.27 | classifier `displays_injective` at `U`, emits (`check_display_injective`; Lean `displayInjective`): | | |
| · 2.27a | an affix whose edge is a digit, a sign or a point; returns `text` | `UNITS_DISPLAY_COLLISION` | `DisplayCollision({text:json} touches the amount)` |
| · 2.27b | two affixes on one side, one a prefix (or suffix) of the other; returns `a`, `b` | as 2.27a | `DisplayCollision({a:json}, {b:json})` |

Phase 3, `vocabulary`. **Deviation from Python's order:** Python validates `argument_units` inside its predicate
loop and `unit` inside its constant loop, between the base checks of those entries (`ve/environment.py:419–423,
499–505`); the base decoder is one inherited hook here, so every base fault of the vocabulary comes before any
slot or constant unit fault. On a vocabulary with a bad slot in one predicate and an undeclared sort in a later
one, Python today reports the slot and the table reports the sort (fixture Q23; section 6).

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 3.1 | hook `p0_vocabulary` at `V`, inherited: `Environment` on the erased environment (`ve.units.erased_data`; Lean `eraseEnvironment` and the frozen order decoder) | `UNITS_INVALID_VOCABULARY` | `{message}` |
| | group `predicates` over `V/predicates/*` | | |
| · 3.2 | `type` `@/argument_units`: object | `UNITS_INVALID_SLOT` | `argument_units must be an object` |
| · | group `slots` over `@/argument_units/*` | | |
| · · 3.3 | hook `slot_index_valid` at `@`: the key is `0` or digits without a leading zero, below the arity | as 3.2 | `Invalid argument unit slot {key}` |
| · · 3.4 | hook `slot_is_integer` at `@`: the argument at that index is `$int` | as 3.2 | `Unit on non-integer slot {key}` |
| · · 3.5 | `type` `@`: string | as 3.2 | `String expected` |
| · · 3.6 | hook `unit_tag_declared` at `@`: `dimensionless` or a key of `U` | `UNITS_UNKNOWN_UNIT` | `UnknownUnit({value})` |
| | group `constants` over `V/constants/*` | | |
| · 3.7 | hook `unit_on_integer_constant` at `@`, when `@/unit` is present: the sort is `$int` | as 3.2 | `Unit on non-integer constant {key}` |
| · 3.8 | `type` `@/unit`: string | as 3.2 | `String expected` |
| · 3.9 | hook `unit_tag_declared` at `@/unit` | `UNITS_UNKNOWN_UNIT` | `UnknownUnit({value})` |

Phase 4, `extension` (`validate_extension`, `ve/units.py:237–246`):

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 4.1 | hook `tags_not_sorts` at `U`: neither `dimensionless` nor any tag is a declared sort; returns `name` | `UNITS_TAG_COLLISION` | `Unit tag {name} collides with a declared sort` |
| 4.2 | hook `no_string_literals` at `V/constants` | `UNITS_UNSUPPORTED_PROFILE` | `UnsupportedProfile: $string literals are not admitted with ve-units@1` |
| 4.3 | classifier `verbalisations` at `V/constants`, emits (`check_verbalisations`, in sorted name order): | | |
| · 4.3a | an empty verbalisation | `UNITS_INVALID_VERBALISATION` | `Verbalisation must be nonempty` |
| · 4.3b | over 256 characters | `UNITS_RESOURCE_LIMIT` | `ResourceLimit: Verbalisation exceeds 256 characters` |
| · 4.3c | not whitespace-normalized; returns `value` | as 4.3a | `Verbalisation {value:json} must be whitespace-normalized` |
| · 4.3d | two constants with one sentence-initial spelling; returns `other`, `name` | `UNITS_VERBALISATION_COLLISION` | `VerbalisationCollision({other}, {name})` |

Phase 5, `document` (`admit_quantity_document`). **The statement set S** is emitted by five classifier entries,
at `@/content` of a unit (5.10), at `@/conclusion` of a lemma (5.16), at `@/quantity` of a lemma leaf (5.19), at
a reading (5.27) and at `@/quantity` of a node (5.36). Its members, in `elaborate_quantity`'s order
(`ve/units.py:508–529`; the elaboration members by the first node Python's `_Elaborator` refuses, in pre-order
with a node's terms before its sub-formulas, and at a node in the order of `ve/units.py:364–491`):

| Member | Fails when | Code | Text |
|---|---|---|---|
| a | not an object with `format`, `formula` and optionally `traces`, `Q` | `UNITS_INVALID_STATEMENT` | `InvalidInput: invalid quantity fields` |
| b | `format` is not `"ve-quantity@1"` | as a | `Unsupported quantity format` |
| c | `traces` is not an array | as a | `traces must be an array` |
| d | `traces` is not empty | `UNITS_UNSUPPORTED_PROFILE` | `UnsupportedProfile: trace declarations require the missing numbers2 route` |
| e | the formula has more than 10,000 array nodes, or a node is past the 10,000th or deeper than 64 | `UNITS_RESOURCE_LIMIT` | `ResourceLimit: Quantity AST exceeds node or depth limit` |
| f | a tag neither `dimensionless` nor declared; returns `tag` | `UNITS_UNKNOWN_UNIT` | `UnknownUnit({tag})` |
| g | a decimal off the tag's grid; returns `tag`, `scale` | `UNITS_UNIT_PRECISION` | `UnitPrecision({tag}, scale={scale})` |
| h | a `date` text not a valid calendar date; returns `value` | `UNITS_INVALID_DATE` | `InvalidDate({value})` |
| i | a `date` before 1970; returns `value` | `UNITS_DATE_RANGE` | `DateRange({value})` |
| j | a decimal text not `-?(0\|[1-9][0-9]*)(\.[0-9]+)?` | `UNITS_INVALID_DECIMAL` | `Invalid decimal literal {value:json}` |
| k1 | an integer literal over 40 characters; inherited | `UNITS_RESOURCE_LIMIT` | `{message}` |
| k2 | an integer literal not canonical or not a string; inherited | `UNITS_INVALID_INTEGER` | `{message}` |
| l1 | a decimal with more than 40 digits | `UNITS_RESOURCE_LIMIT` | `ResourceLimit: Decimal literal exceeds 40 digits` |
| l2 | a lowered coordinate over 40 characters | as l1 | `ResourceLimit: Lowered integer exceeds 40 characters` |
| m | two types that must agree and do not, a unit on an object constant, a scaled or added calendar date, an order over non-quantities; returns `message`, the text without a class prefix | `UNITS_TYPE_MISMATCH` | `{message}` |
| n | an `$int` binder, `var` with a tag, `atom`, or a W6b form; returns `message` | `UNITS_UNSUPPORTED_PROFILE` | `{message}` |
| o1 | a constant not declared; returns `name` | `UNITS_UNKNOWN_SYMBOL` | `Unknown constant {name:json}` |
| o2 | a predicate not declared or of another arity; returns `name` | as o1 | `Unknown predicate or arity {name}` |
| o3 | a variable index outside its scope; inherited | `UNITS_UNBOUND_VARIABLE` | `{message}` |
| p | a node of the wrong shape: not a tagged array, an unknown tag, a wrong number of members, an invalid binder, a negative day offset; inherited | as a | `{message}` |
| q | a supplied `Q` that differs from the regenerated one | as a | `Quantity Q differs from regenerated formula` |
| r | the regenerated core refused by the frozen decoder; inherited; unreached | `UNITS_INVALID_VOCABULARY` | `{message}` |

A classifier entry `statement` emits S with ids `<entry>a` to `<entry>r` (`5.10a`, …, `5.10r`); the five copies
are the same list, which the lint checks (T6). The texts of m and n are compared between engines (`returns`
`["message"]` without `inherited`): the Lean hook strips the leading `TypeMismatch: ` or `UnsupportedProfile: `,
after which Python's and Lean's texts are equal from reading (`UnitMismatch(bp,day)`, `TypeMismatch(unit
bp,sort person)`, `Unit on object constant k`, `Calendar dates cannot be added`, `Order needs quantity terms`,
the `numbers2` and `n-ary` texts). k1, k2, o3 and p are inherited because the texts differ: `Integer literal
exceeds 40 characters` against `ResourceLimit: numeral length`; `Non-canonical integer literal '07'`
(`SyntaxError`) against `non-canonical integer`; `Unbound variable 'x'` against `Unbound variable`;
`Invalid unary arity` against `Unknown quantity formula unary`.

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 5.1 | `requires` `E/profiles` item `"documents@1"` | `UNITS_UNSUPPORTED_PROFILE` | `UnsupportedProfile: quantity documents require documents@1` |
| 5.2 | `keys` `D`: required `units`, `graph`; optional `lemmas`, `open_terms`, `reading_sets`, `narrowings` | `UNITS_INVALID_DOCUMENT` | `InvalidInput: invalid document fields` |
| 5.3 | `type` `D/units`: array | as 5.2 | `expected an array` |
| | group `units` over `D/units/*` | | |
| · 5.4 | `keys` `@`: required `id`, `span`, `kind`; optional `content` | `UNITS_INVALID_UNIT` | `InvalidInput: invalid unit fields` |
| · 5.5 | `type` `@/id`: string | as 5.4 | `expected a string` |
| · 5.6 | `name` `@/id`: `token` | as 5.4 | `invalid unit id {value}` |
| · 5.7 | `type` `@/span`: array | as 5.4 | `expected an array` |
| · 5.8 | classifier `unit_span` at `@/span`, emits: | | |
| · · 5.8a | not two members, or start after stop | as 5.4 | `invalid span` |
| · · 5.8b | a member that is not a natural number; inherited | as 5.4 | `{message}` |
| · 5.9 | hook `w2_kind` at `@/kind`, inherited: W2's kind decoder | `UNITS_INVALID_KIND` | `{message}` |
| · 5.10 | classifier `statement` at `@/content`, when `@/content` is present: S | | |
| 5.11 | `max_items` `D/units`: `MAX_UNITS` | `UNITS_RESOURCE_LIMIT` | `ResourceLimit: unit count` |
| | group `unit-ids` over `D/units/*/id` | | |
| · 5.12 | `unique_so_far` `@` | `UNITS_INVALID_UNIT` | `duplicate unit id` |
| 5.13 | hook `spans_sorted` at `D/units` | as 5.12 | `unit spans must be sorted and non-overlapping` |
| 5.14a | `type` `D/lemmas`: array | `UNITS_INVALID_DOCUMENT` | `expected an array` |
| 5.14b | `type` `D/open_terms`: array | as 5.14a | as 5.14a |
| 5.14c | `type` `D/reading_sets`: array | as 5.14a | as 5.14a |
| 5.14d | `type` `D/narrowings`: array | as 5.14a | as 5.14a |
| | group `lemmas` over `D/lemmas/*` | | |
| · 5.15 | classifier `lemma_record` at `@`, emits: | | |
| · · 5.15a | not an object with exactly `name`, `conclusion`, `leaves`, `certificate` | `UNITS_INVALID_LEMMA` | `InvalidInput: invalid lemma fields` |
| · · 5.15b | a `name` that is not a string | as 5.15a | `expected a string` |
| · · 5.15c | a `name` that does not parse as `cite:<name>`; returns `name` | as 5.15a | `invalid lemma name {name}` |
| · 5.16 | classifier `statement` at `@/conclusion`: S | | |
| · 5.17 | `type` `@/leaves`: array | as 5.15a | `expected an array` |
| · | group `leaves` over `@/leaves/*` | | |
| · · 5.18 | classifier `lemma_leaf` at `@`, emits: | | |
| · · · 5.18a | not an object with exactly `quantity`, `label` | as 5.15a | `InvalidInput: invalid leaf fields` |
| · · · 5.18b | a `label` that is not a string | as 5.15a | `expected a string` |
| · · · 5.18c | a `label` that does not parse; returns `label` | `UNITS_ADMISSION_ERROR` | `AdmissionError: invalid label {label}` |
| · · · 5.18d | a `cite` label | as 5.18c | `AdmissionError: lemma leaves must be transitive (no cite labels)` |
| · · 5.19 | classifier `statement` at `@/quantity`: S | | |
| · 5.20 | `max_items` `@/leaves`: `MAX_LEMMA_LEAVES` | `UNITS_RESOURCE_LIMIT` | `ResourceLimit: lemma leaves` |
| · 5.21 | hook `certificate_shape` at `@/certificate`: an object with exactly `format`, `environment_id`, `premise_meaning_ids`, `conclusion_meaning_id`, `core`, with `format` `"ve-quantity-certificate@1"` | `UNITS_INVALID_CERTIFICATE` | `Invalid quantity certificate` |
| · 5.22 | hook `lemma_established` at `@`; returns `name` | `UNITS_ADMISSION_ERROR` | `AdmissionError: lemma {name} is not established by its certificate` |
| | group `lemma-names` over `D/lemmas/*/name` | | |
| · 5.23 | `unique_so_far` `@` | `UNITS_INVALID_LEMMA` | `duplicate lemma` |
| 5.24 | classifier `open_terms` at `D/open_terms`, emits: | | |
| · 5.24a | a member that is not a string | `UNITS_INVALID_DOCUMENT` | `expected strings` |
| · 5.24b | a member that is not a token | as 5.24a | `invalid name` |
| | group `reading-sets` over `D/reading_sets/*` | | |
| · 5.25 | classifier `reading_set_record` at `@`, emits: | | |
| · · 5.25a | not an object with exactly `id`, `version`, `readings` | `UNITS_INVALID_READING_SET` | `InvalidInput: invalid reading set fields` |
| · · 5.25b | an `id` that is not a string | as 5.25a | `expected a string` |
| · · 5.25c | an `id` that is not a token; returns `id` | as 5.25a | `invalid reading set id {id}` |
| · · 5.25d | a `version` that is not a natural number; inherited | as 5.25a | `{message}` |
| · · 5.25e | `readings` not an array | as 5.25a | `expected an array` |
| · | group `readings` over `@/readings/*` | | |
| · · 5.26 | classifier `statement` at `@`: S | | |
| · 5.27 | hook `readings_count` at `@/readings`: 1 to 64 members | as 5.25a | `reading sets hold 1 to 64 readings` |
| 5.28 | hook `reading_set_versions_distinct` at `D/reading_sets` | as 5.25a | `duplicate reading set version` |
| 5.29 | classifier `narrowings` at `D/narrowings`, emits 5.29a and 5.29b as 5.24a and 5.24b | | |
| 5.30a | `type` `D/graph`: object | `UNITS_INVALID_DOCUMENT` | `Expected a JSON object` |
| 5.30b | `exact_keys` `D/graph`: `root`, `nodes` | as 5.30a | `InvalidInput: invalid graph fields` |
| 5.31 | `type` `D/graph/root`: string | as 5.30a | `expected a string` |
| 5.32 | `type` `D/graph/nodes`: array | as 5.30a | `expected an array` |
| 5.33 | `max_items` `D/graph/nodes`: `MAX_GRAPH_NODES` | `UNITS_RESOURCE_LIMIT` | `ResourceLimit: graph node count` |
| | group `nodes` over `D/graph/nodes/*` | | |
| · 5.34 | classifier `graph_node` at `@`, emits: | | |
| · · 5.34a | not an object with `name`, `quantity` and optionally `label`, `unit`, `premises`, `certificate` | `UNITS_INVALID_NODE` | `InvalidInput: invalid node fields` |
| · · 5.34b | a `name` or `label` that is not a string | as 5.34a | `expected a string` |
| · · 5.34c | the label `"asserted"` written out | as 5.34a | `non-canonical label: the default label asserted is omitted` |
| · 5.35 | classifier `statement` at `@/quantity`: S | | |
| · 5.36 | classifier `graph_node_rest` at `@`, emits: | | |
| · · 5.36a | a `unit` that is not a string | as 5.34a | `expected a string` |
| · · 5.36b | one of `premises` and `certificate` without the other | as 5.34a | `premises and certificate come together` |
| · · 5.36c | `premises` not an array | as 5.34a | `expected an array` |
| · · 5.36d | a premise that is not a string | as 5.34a | `expected strings` |
| · · 5.36e | a `certificate` not of the shape of 5.21 | `UNITS_INVALID_CERTIFICATE` | `Invalid quantity certificate` |
| 5.37 | classifier `admission` at `D/graph/nodes`, emits (the first node not admitted, in order; `_diagnostic`, Lean `nodeDiagnostic`): | | |
| · 5.37a | the node names a quoted unit and is not a bridge leaf naming it; returns `unit` | `UNITS_ADMISSION_ERROR` | `AdmissionError: quoted content of unit {unit} is used without a bridge leaf` |
| · 5.37b | the node is not admitted under its label; returns `name`, `label` | as 5.37a | `AdmissionError: node {name} is not admitted under label {label}` |
| · 5.37c | the label does not parse; returns `label` | as 5.37a | `AdmissionError: invalid label {label}` |
| 5.38 | hook `graph_checks` at `D/graph`: distinct names, premises earlier, each certificate valid for its premises, the root a node | `UNITS_GRAPH_REJECTED` | `graph rejected: cycle, duplicate name, dangling premise, ill-typed claim or invalid certificate` |
| 5.39 | hook `citations_closed` at `D/graph` | `UNITS_ADMISSION_ERROR` | `AdmissionError: a cited lemma's leaves are missing from the report` |
| 5.40 | hook `choices_compatible` at `D/graph` | as 5.39 | `AdmissionError: incompatible reading choices` |

**What is not in the table, and why.** Python's round-trip check (`W6 environment does not round-trip to its
canonical declaration`, `ve/environment.py:611–612`) has no Lean counterpart and is an S8-pre candidate (2.13);
until fixed, a residual. The envelope's `unit_schema` and `units` together (`:322–323`) is a domain condition
(2.2). The risk route's extension conditions (`:510–517`) are outside the domain. Rust's texts and classes are
not in the table (no Rust column).

**Planned tiers.** 66 numbered checks, counting a lettered row set as one: T1 1.1, 1.3, 2.1 to 2.3, 2.5, 2.6,
2.8 to 2.16, 2.18, 2.19, 2.21 to 2.23, 3.2, 3.5, 3.8, 5.2 to 5.7, 5.11, 5.12, 5.14, 5.17, 5.20, 5.23, 5.30 to
5.33 (40); T2 not inherited 1.4, 2.4, 2.24 to 2.26, 3.3, 3.4, 3.6, 3.7, 3.9, 4.1, 4.2, 5.13, 5.21, 5.22, 5.27,
5.28, 5.38 to 5.40 (20); inherited hooks 1.2, 3.1, 5.9 (3); T3 2.7, 2.17, 2.20, 2.27, 4.3, 5.8, 5.10, 5.15,
5.16, 5.18, 5.19, 5.24, 5.25, 5.26, 5.29, 5.34 to 5.37 (counted once each). `n1 + n2` is 60 of 66 among the
checks that are not classifier sets.

### 2.6 The hooks, classifiers and views, in both languages

Rules of base spec 2.5 apply: a hook reads its two arguments only, may assume every earlier instance holds, and
is required to agree across languages only on such inputs. Lean's hooks call frozen functions read-only; none
calls a route's whole decoder. For `rights@0` and `reports@0` the Lean classifiers call the frozen functions
whose order the table is (`addUnit`, `checkBlock`, `checkRights`, `validateSoft`, `decodeUnit`, `decodeContent`,
`decodeContext`, `decodeAssessment`, `decodeBridge`, `decodeScoped`, `firstFailure`) and name the member by the
text's leading words, as the pilot's `semanticMember` does; the Python classifiers are **walks** in those
functions' order, written in the contract module, diagnostic only and under no theorem (5.2), as S5's Lean
walks were in Python's order. For `ve-units@1` it is the other way round: the Python classifiers call the
frozen Python functions and the Lean classifiers call the frozen Lean functions, both of which already check in
the table's order (2.5, S), except the inherited members, where the texts differ.

**`rights@0`** (`ve/rights_contract.py`; `lean/VE/WireContract/Hooks/Rights.lean`):

| Name | Python | Lean |
|---|---|---|
| `soft_source_of_rights` (view) | `{"environment": e′, "norms": []}` with `e′` a deep copy of the value with `"rights@0"` removed from `profiles` (when `profiles` is a list) and `rights` popped from `vocabulary` (when `vocabulary` is a dict); any other value is returned under `environment` unchanged | the same, by `VE.Rights.Wire.stripRights` where it succeeds and the value itself where it does not; total, as every view is |
| `rights_unit` (4.3) | a walk in `addUnit`'s order over the unit: its key set decides the branch; inside each branch the fields are checked in the Lean decoder's order with `ve.units._fields`' texts for the shapes; the line norms by `ve.softnorms.decode_rule` texts, as the soft route's `_rule_fields` gives them | `VE.Rights.Wire.addUnit` on the unit with the accumulator of the earlier units (`decodeRightsEnvironment` for the `SoftEnvironment`); the member by the text (`InvalidInput: duplicate source_units` → a; `… must list unit ids` → b; `InvalidInput: invalid line kind` → d; … ; `UnknownRight: ` → h, returning the rest; `InvalidInput: invalid kinds of limitation ` → i; … ; `InvalidInput: invalid rights document unit` → o); any other text is c |
| `rights_block` (5.1) | a walk in `checkBlock`'s order over the decoded block and the stripped environment's sorts and predicates | `VE.Rights.checkBlock` on the `RightsDoc` built as `decodeRightsSource` builds it before `validateRights` (`Wire.lean:288–290`); the member by the leading words |
| `rights_names`, `rights_lines`, `rights_limitations`, `rights_bar` (6.3 to 6.6) | one walk in `checkRights`' order (`Correlate.lean:358–414`) over the decoded units, split at the four points where the set changes; each classifier runs the walk and reports only a member of its own set, holding when the walk fails in another set (which an earlier instance then reports) | `VE.Rights.checkRights` on the same `RightsDoc`, with the member by the text's leading words and the set by the member; a text of another set is `ok` |
| `citations_declared` (6.7) | every `cites` target of every line and outside norm is in `source_units` | the last loop of `checkRights` (`:411–414`), run alone over the decoded units |
| `correlated_soft` (7.1) | `RightsDocument(env, document)` run to completion; a `VEError` from `_correlate`'s `SoftNormDocument` is mapped as the pilot's `soft_semantic` maps it (a to m); `ResourceLimit: decision predicate …` and `ResourceLimit: extended vocabulary` name no member (7.2 and 2.13) | `VE.SoftNorms.validateSoft (correlate D)` with the pilot's `semanticMember` relabelled 7.1a to 7.1m |
| `decision_names_fit` (7.2) | the decision names of the correlated document (the pilot's `decision_names_fit` over `rights.soft_document`), the first over 64 bytes | `VE.SoftNorms.decisionNames (correlate D)`, the first over 64 bytes (`Correlate.lean:443`) |
| `rights_stratified` (7.3) | `RightsDocument` completes (its `_correlate` builds the layers) | `VE.Rights.rightsSemanticCheck D` |

**`reports@0`** (`ve/reports_contract.py`; `Hooks/Reports.lean`):

| Name | Python | Lean |
|---|---|---|
| `fol_family` (1.6, inherited) | `ve.profiles.checker_family(profiles)` must give `"fol"`; its `UnsupportedProfile` text is the message | `VE.Route.Gate.classify (ps.erase "reports@0")` must be `.ok .fol`; its text, or `UnsupportedProfile: reports@0 requires the FOL family` |
| `constant_verbalisation` (1.19, inherited) | `ve.environment._verbalisation(value)` | `VE.Bridge.displayString` on the value |
| `p0_vocabulary` (1.20, inherited) | `Environment` on the environment with `reports@0` removed from `profiles`, `reports` removed from `vocabulary` and `verbalisation` removed from every constant | `VE.Route.Wire.decodeVocabulary (ps.erase "reports@0") vocab'` with `vocab'` as `decodeEnvironment` builds it (`Wire.lean:66–75`) |
| `holders_well_formed` (1.21) | 1 to 8 distinct strings | `!holders.isEmpty && holders.length ≤ 8 && holders.eraseDups.length == holders.length` |
| `holder_sort_declared` (1.22), `evidence_sort_declared` (1.23) | the item is a key of `V/sorts` | the same |
| `holder_verbalisation_free` (1.24) | no constant of a holder sort whose `verbalisation` lower-cased (ASCII) is `the stated assessment` | `Wire.lean:82–86` |
| `span_ordered` (2.6), `spans_sorted` (2.12) | `start ≤ stop`; each unit's start at or after the previous stop | the same (`sortedSpans`) |
| `report_content` (2.7) | a walk in `decodeUnit`'s and `decodeContent`'s order over the unit: the key set by the content's tags, then the tree in pre-order with the report fields in `holder`, `act`, `context`, `literal`, `content` order; quoted packages by `NormDocument` and `Environment` (member h); the kind by `_kind_matches` (i) | `VE.Reports.Wire.decodeUnit E j` with `E` the decoded environment (1.20); the member by the text's leading words; a library text is a (fields) or h (a quoted package or formula) by the branch it came from |
| `meaning_shape` (2.8) | `ReportsDocument._meaning` | `decodeMeaning` |
| `context_record` (2.14), `assessment_record` (2.17), `bridge_record` (2.19), `scoped_record` (2.20) | walks in `decodeContext`'s, `decodeAssessment`'s, `decodeBridge`'s, `decodeScoped`'s order over the record | the frozen decoders; the member by the leading words, a library text to the record's shape member |
| `reports_wellformed` (3.1) | a walk in `firstFailure`'s order over `ReportsDocument`'s decoded parts: the four duplicate scans, the assessments (`evidence context`, `decided_by` token, criteria closed), the content depth, the nodes (holder, holder sort, context, assessment record, operand, closed formula), the digests, the scoped checks, the bridges, the metadata, the predicate count | `Wire.decodeDocumentRaw` and, when `WellFormedReports dec.D` is false, `firstFailure dec.D`; the member by the text (5.5) |

**`ve-units@1`** (`ve/units_contract.py`; `Hooks/Units.lean`):

| Name | Python | Lean |
|---|---|---|
| `p0_envelope_gate` (1.2, inherited) | `language` is `ve.core@0.2` (`UnsupportedProfile: Unsupported language`) and `checker_family(profiles)` passes | `UnsupportedProfile: quantity route requires ve-units@1 on ve.core@0.2` on the language; `Gate.classify` on the profiles |
| `w6_profiles` (1.4) | `tuple(profiles) in W6_PROFILES` | `w6Profiles.contains profiles` |
| `unit_tag_valid` (2.4) | `valid_identifier(key) and key != "dimensionless"` | `identifier tag && tag != dimensionless` |
| `unit_scale` (2.7) | `ve.units._scale`; the member by the text | `decodeScale`; the member by the text |
| `display_string_trailing` (2.17), `display_string` (2.20) | `ve.units.display_string(value, trailing_space=…)` | `displayString s trailing` |
| `iso_date_is_day` (2.24), `reserved_day` (2.25), `reserved_elapsed_day` (2.26) | `ve/units.py:121–128` | `Wire.lean:169–175` (`canonicalText` equality) |
| `displays_injective` (2.27) | `check_display_injective(units)`; the member and `text`, or `a` and `b`, from the message | `displayInjective` on the decoded units, in `fields` order |
| `p0_vocabulary` (3.1, inherited) | `Environment(ve.units.erased_data(environment))` | `VE.Route.Wire.decodeOrderVocabulary` on `eraseEnvironment`'s vocabulary |
| `slot_index_valid` (3.3), `slot_is_integer` (3.4), `unit_tag_declared` (3.6, 3.9), `unit_on_integer_constant` (3.7) | `validate_slot_units`, `validate_tag`, `ve/environment.py:499–505` | `decodeSlot`, `validTag`, `Wire.lean:282–291` |
| `tags_not_sorts` (4.1), `no_string_literals` (4.2), `verbalisations` (4.3) | `validate_extension`; the member by the text | `Wire.lean:269–274, 292` (`checkVerbalisations`) |
| `unit_span` (5.8), `w2_kind` (5.9), `spans_sorted` (5.13) | `_array`, `_nat`, `_check_kind` | `Document.lean:459–474`, `decodeKind 16` |
| `statement` (S) | `elaborate_quantity(env, payload)`; the member by the exception's class and text; `message` for m and n is the text without its class name | `decodeQuantity w p`; the member by the text's leading words, with `TypeMismatch: ` and `UnsupportedProfile: ` stripped for m and n |
| `lemma_record`, `lemma_leaf`, `certificate_shape`, `lemma_established` (5.15 to 5.22) | `_decode_lemma`, `_decode_leaf`, `_certificate`, `check_quantity_certificate` | `decodeLemma`, `decodeLeaf`, `decodeW6Certificate`, `checkW6Certificate` |
| `open_terms`, `narrowings` (5.24, 5.29) | `_tokens` | `tokenList` |
| `reading_set_record`, `readings_count`, `reading_set_versions_distinct` (5.25 to 5.28) | `_decode_reading_set` and the pair set | `decodeReadingSet` and `eraseDups` |
| `graph_node`, `graph_node_rest`, `admission`, `graph_checks`, `citations_closed`, `choices_compatible` (5.34 to 5.40) | `_decode_node`, `_node_admitted` with `_diagnostic`, `_check_graph` and the root lookup, the citation loop, `_compatible` | `decodeNode`, `admitNodes` with `nodeDiagnostic`, `checkGraph` and `find?`, `CitationsClosed`, `ChoicesCompatible` |

Each unit's registry is the hooks, classifiers, views and adapter above; `rights@0`'s registry also holds the
pilot's hooks and classifiers under their names, so that the included checks run with the pilot's functions, as
`norm-defaults@0`'s does for `norms@0` (S5 spec 2.5); in Lean, `Hooks/Rights.lean` imports `Hooks/SoftNorms.lean`
and dispatches the pilot's names to it.

### 2.7 Shadow and public

As S4 spec 2.2, for each unit. While `status` is `shadow`, no output of any program depends on the contract.
When it is `public`, exactly one output depends on it: the error that the unit's call site raises (2.9).
Nothing in Lean reads `status`. Changing `status` is a contract edit and raises the revision; today's output is
restored by reverting the switch commit or by a later revision that sets `status` to `shadow`.

### 2.8 The boundary functions

```
ve.rights_contract.public_rejection(environment, document, error, *, contract=None, registry=None)
ve.reports_contract.public_rejection(environment, document, error, *, contract=None, registry=None)
ve.units_contract.public_rejection(environment, document, error, *, contract=None, registry=None)
```

Each is the S4 spec's 2.3 for its unit, step for step: return at once if `error.diagnostic` is set or the
locked contract's `status` is not `public`; the root is `{"environment": e, "document": d}` with deep copies of
the arguments; `outcome` is `engine.run(contract, root, registry=…)` with the unit's `REGISTRY`; `record` is
`engine.overlay(contract, error, outcome)` with no Lean argument; set `error.diagnostic`, `error.message` and
`error.args` so that `message` and `str(error)` are the record's `text`; return `error`. The **failure rule**
holds: if loading the contract or any step raises an `Exception`, the function returns `error` as it received
it. It never writes `error.code`, `error.path` or `error.span`, never creates an error, never calls the legacy
validator on the source itself (the hooks of 2.6 call parts of it; `correlated_soft` and `rights_stratified`
call `RightsDocument`, and `lemma_established` calls the certificate checker, as the pilot's `soft_semantic`
called `load_soft_document`), and starts no Lean process.

By the overlay, the reported record is the fault record, the residual record (whose `text` is the legacy text),
or the deferred record `{"contract", "revision", "deferred": id, "text"}` with the legacy text. The three Python
registries are complete, so the gate's deferred count in Python is 0 for every unit and must stay 0.

### 2.9 The call sites

**`rights@0`.** In `ve/document.py`, `_load_document(raw, path, lean)` builds the environment by one statement,
`env = _environment(environment_data)` (`:365`), which is `RightsEnvironment(environment_data)` when
`rights_enabled`, and the rights document by one statement, `rights_document = RightsDocument(env,
_rights_units(units, attached))` (`:379`). The switch wraps each in one handler, entered only when
`rights_enabled`: a `VEError` the statement raises is passed to `public_rejection(environment_data, source,
error)`, and the returned error is raised. `source` is `_rights_units(units, attached)` at the second statement
(the list the statement received), and at the first statement the value of a total helper
`ve.rights_contract.rights_source_of(meta, attached)`, which returns `_rights_units(meta.get("units"),
attached)` when that call succeeds and `null` otherwise (the first statement has not read `units` yet; an
environment fault is reported by the environment phases, which do not read the document). The import of
`public_rejection` is a statement inside each handler. Nothing else in the function changes. An error of any
other statement of `_load_document` keeps today's text and has no record.

**`reports@0`.** In the same function, the reports document is built by one statement, `reports =
ReportsDocument(env, meta.get("contexts", []), meta.get("assessments", []), [_wire_unit(u) for u in compiled],
bridges=meta.get("bridges", []), scoped=meta.get("scoped", []), open_terms=sorted(open_names))` (`:467–469`),
entered only when `reports@0` is in the profiles. The switch wraps it in one handler of the same shape, with
`ve.reports_contract.public_rejection(environment_data, document, error)`, where `document` is the object with
members `units` (the list of `_wire_unit(u)`), `contexts`, `assessments`, `bridges`, `scoped` (each as the
statement received it) and `open_terms` (`sorted(open_names)`). The environment statement (`:365`) is wrapped
for `reports@0` too, with the same `document` built from `meta` by a total helper
`ve.reports_contract.reports_source_of(meta)` that gives `null` members where `meta` has none.

**`ve-units@1`.** In `ve/admission.py`, `_admit_document_python(environment, document)` builds the environment
by one statement, `env = environment if type(environment) is Environment else Environment(environment)`
(`:503`), and admits the quantity document by one statement, `return admit_quantity_document(env, document)`
(`:507`). The switch wraps each in one handler: the first entered only when `environment` is a dict with a
member `unit_schema` or `units` (the unit's domain), with `ve.units_contract.public_rejection(environment,
document, error)`; the second with `public_rejection(env.to_dict(), document, error)`. The round-trip check
(`ve/environment.py:611–612`) makes `env.to_dict()` canonically equal to the submitted dictionary on every
environment the first statement accepts.

Four properties follow from this shape and are tested (8.4), not proved:

- **(V1) The verdict is the legacy validator's.** Each call site raises exactly when its statement raises, and
  raises the same object: same type, same `code`. The handler ends in a `raise` on every path.
- **(V2) An accepted source does not reach the engine.** On an input the statements accept, no contract module
  and not `ve.wire_contract` is imported by the call.
- **(V3) The engine and the legacy validator read the same source.** The root's `document` is the list or
  object the statement received, and its `environment` is the dictionary the statement decoded or, for units,
  its round-tripped form; the statements modify neither (fixture Z5).
- **(V4) An environment fault has one record whichever statement raises it.** For rights and reports the
  environment phases read only `/environment`, so the record of an environment fault is the same whether the
  first or the second statement raised; for units the environment phases 1 to 4 read only `/environment` too.

**The import rule** of base spec 7.3 and S5 spec 2.8 becomes a table with three more rows. Inside `ve/`, outside
`ve/wire_contract/` and the contract modules: `ve.rights_contract` and `ve.reports_contract` are imported only by
`ve/document.py`, `ve.units_contract` only by `ve/admission.py`; each importer imports the one name
`public_rejection` in one import statement per handler, each inside one `except VEError` handler of the named
function, the call being the operand of a `raise`; `ve/document.py` has two handlers for rights and two for
reports, `ve/admission.py` two for units; no module imports `ve.wire_contract`; `ve/rights_contract.py` may
import `ve.softnorms_contract`. `tests/test_softnorms_contract.py::test_diagnostic_modules_stay_off_verdict_import_paths`
is rewritten over that table, with the S4 spec's resolution of relative imports. The Lean import rule is
unchanged.

### 2.10 Entry points: switched, and not switched

| Entry point | After the switch |
|---|---|
| `ve.document.load_document(path)` on a `ve-document@1` text whose environment lists `rights@0` (the loader's `_load_document`); the adapter's case kind `admission` with a rights document | **public** for `rights@0`: an error of the two statements of 2.9 carries the reported record |
| the same on a text whose environment lists `reports@0` | **public** for `reports@0`: an error of the environment statement or the `ReportsDocument` statement carries the reported record |
| `ve.admission.admit_document(environment, document)` under the Python authority, for an environment with `unit_schema` and `units` (`ve/admission.py:443–444, 503–507`); reached from `ve document check` on a W6 document (`ve/document.py:996`) | **public** for `ve-units@1`: an error of the two statements of 2.9 carries the reported record |

Not switched; each keeps today's message and has no record:

| Entry point | Why not in item 1 |
|---|---|
| the loader's other statements: W2 unit schema, spans, kinds, meanings, support, open terms, reading sets, fences (`ve/document.py:366–459, 482–489`) | the unit `ve-document@1` (base plan 5.3, row 13) |
| `RightsEnvironment`, `RightsDocument`, `correlate`, `ReportsDocument`, `Environment`, `admit_quantity_document`, `elaborate_quantity` alone, and the recorder's calls of them | base spec section 10, item 7; and the validators must stay what the gate calls |
| the readings route (`ve/readings.py:94, 196`, `ve/readings_s1.py:476`), `UnspecifiedRightsDocument` (`ve/norm_defaults.py:711–723`), the lower-route constructions of `ve/document.py:685–705, 1349–1351` | they build a rights document over their own sources; their own rows or stages |
| `report_rights`, `admit_rights_document`, `checked_elaboration`, `run_case` (`ve/rights_route.py`, `ve/reports_route.py`) and `_lean_quantity_admission` | Lean rows read by `checker_error` or compared after validation; the routes are frozen |
| the loader's own elaboration of each unit's quantity statement (`ve/document.py:122–143`) and `_check_quantity_document`'s payload checks | a second call site for the same unit with its own delta; the statement set S would report the same record there |
| the single-statement cases of `ve_quantity` (`admission` with `quantity`, `countermodel`, `certificate`, `count`, the conversions) and Rust's `quantity` cases | outside the domain (2.2); no Rust column |
| the English front ends (`ve/surface/rights.py`, `ve/report_english.py`, `ve/surface/time.py`) | they build the source from English; there is no submitted JSON |
| every Lean row; every Rust output | base plan 2.5; Rust has no engine |

Until their own rows, the same fault can therefore read differently through two entry points (plan section 8,
question 7).

The existing tolerances keep their assertions: `conformance/rights_differential.py:265–271` keeps its suffix
count as a reported number; the units tests' substring matches compare Lean route texts, which do not change
(2.14). The gate compares every text of each unit at zero tolerance instead (section 9).

### 2.11 The contract edits

Revision 1 of each contract is the shadow one of 2.3 to 2.5. The shadow may edit any of them; the switch of a
unit is one further revision, written `R` in sections 4 and 8, whose only differences from the revision before
it are `"revision": R` and `"status": "public"`. What follows mechanically, by `tools/wire_contract.py --write`:

- `contracts.lock`: the entry of the contract;
- `lean/VE/WireContract/Tables/Rights.lean`, `Tables/Reports.lean` or `Tables/Units.lean`: the header comment
  and the numeral of the table's `revision`, and nothing else, and the module's line in
  `VE/Route/frozen-sources.sha256`;
- because the Lean generator inlines an included contract's entries, a revision of `soft-norms@0` also changes
  the header of `Tables/Rights.lean`, which names the pilot's hash: that module and its inventory line are
  regenerated too, and `rights@0`'s own revision does not change (S5 spec 2.10; T5);
- `docs/spec/rights-wire-table.md`, `reports-wire-table.md`, `ve-units-wire-table.md`: no change is expected
  (they state no revision); `--check` decides.

Every record of either engine then has the new `revision`, so the stored reports that hold records are
regenerated (gate, golden, catalogue, delta).

### 2.12 A public change, and the delta

As S5 spec 2.11, per unit. For a corpus case on which Python's legacy validator raises a legacy error with code
`c` and text `m`, let `r` be the reported record: `engine.overlay(contract, error, engine.run(contract, root,
registry=REGISTRY))`. The case has a **text change** when `r`'s `text` is not `m`; a **class difference** when
`r` has a `class` and it is not `c`; it is **attributed** to `r`'s `check` (an id, an include path such as
`soft/2.7a`, or `residual`), or to `deferred`. Every check counts, inherited ones too. A case the legacy
validator accepts has no public change.

A rejected case is **handler-reaching** when the call of 2.9 reaches a switched statement, so that the error it
raises is that statement's. For `rights@0` and `reports@0` that is every rejected case of the domain on which
the loader's statements before `:365` pass (the front matter splits, the environment is a dict, the profile
combination is not refused at `:354–358`) and, for the second statement, on which the loader's W2 checks of
`:366–459` pass. For `ve-units@1` it is every rejected case of the domain (the dispatch of `admit_document`
takes the W6 branch on every environment with the extension). On any other rejected case the call raises
today's error from an earlier statement, with no record; the record `r` of such a case is a result of the
engine and of the boundary function, and is never public.

The **delta report** `conformance/wire-contract/<unit>-delta.json` has the members `public_diagnostic_changes`
and `lean_route_changes` of the S5 spec. For `rights@0` and `reports@0` the second is enforced within a list:
section 6 names the checks whose record text may differ from the Lean route's own text (the fixed texts that
replace library texts, the members whose Lean text has no class prefix, and the included checks whose `path` the
route does not print); a Lean route difference on any other check fails the gate (D2). For `ve-units@1` it is
reported, as in S5.

The **signing file** `conformance/wire-contract/<unit>-switch.json` is written by hand, as the pilot's: `signed`
gives each check whose text may change one sentence saying what changes; `release_note` is the text of 3.4 with
the list filled in. A class difference cannot be signed (2.13).

### 2.13 The class rule, S8-pre and the Lean legacy differences

**The class rule.** On every corpus case where the reported record is a fault:

- for `ve-units@1`, the record's `class` is the legacy code, except on the exempt checks: the inherited hooks
  1.2, 3.1 and 5.9 and the inherited members k1, k2, o3, p and r of S and 5.8b, 5.25d, whose one code stands
  for a decoder that raises several classes; and the checks with code `UNITS_ADMISSION_ERROR` (5.18c, 5.18d,
  5.22, 5.37, 5.39, 5.40), whose legacy code is `AdmissionError`, a class the format cannot name (2.5). Each
  exemption is listed in section 10 and the gate counts the cases it covers;
- for `rights@0` and `reports@0`, the record's `class` is the Lean class of the Lean route's text on the same
  source (2.1), on every corpus case that Lean reads and on which the record is not inherited. That is a
  property of the table (the codes' classes are Lean's) and of the Lean hooks (the member named by the leading
  words), tested in tiers 0 and A. The Python legacy code may differ from the record's class; the gate reports
  those cases as `legacy_class_differences` and does not enforce them. From reading they are: a non-list rights
  document (Python `ResourceLimit`, the record `InvalidInput`); Python's `VEError` texts for `UnknownSymbol:
  sort` and `UnknownSymbol: unit` (Python `InvalidInput`, the record `UnknownSymbol`); Python's
  `DuplicateDeclaration` for the pilot's 2.7b inside the view (the same class, no difference); and no other
  from reading. Aligning Python's classes to Lean's is a product decision in `ve/rights.py` and
  `ve/reports.py`, outside this work (plan section 8, question 5).

**S8-pre** blocks each unit's switch. The shadow gate lists, per unit, every corpus case on which the Python
legacy validator and the Lean route of 2.2 disagree on the verdict (`legacy_verdict_differences`) and every
case on which Python raises something other than a `VEError` (`legacy_crashes`). Each is treated as a class and
run to ground, as S3-pre to S5-pre were, outside this work, and recorded in
`conformance/wire-contract/s8-pre.md`; closed means the gate reports both lists empty, and the gate fails
otherwise. From reading, the candidates are:

| Unit | Candidate | Python | Lean |
|---|---|---|---|
| `rights@0` | a right, limitation or bar whose `name` is not `[a-z][a-z0-9-]*` or is over 64 bytes (`R9`, a 65-byte name) | `InvalidInput: invalid rights name 'R9'` (`ve/rights.py:23–28`) | accepts (`stringField` only; `Wire.lean:185, 203, 217`) |
| `rights@0` | a right without `guard` | `InvalidInput: right` (`ve/rights.py:212–214`: exactly `name`, `holder`, `guard`, `lines`) | accepts (`guard` optional, `Wire.lean:184–189`) |
| `rights@0` | a condition without `decided_by` | `InvalidInput: limitation condition` (`:437`: `decided_by` required, `null` allowed) | accepts (`optString`, `Wire.lean:199`) |
| `rights@0` | a base predicate whose name begins `rights__` | `InvalidInput: author predicate rights__x begins with rights__` (`:64–66`: every predicate) | accepts (`checkRights` tests regulated and defined predicates and the generated names only, `Correlate.lean:369–372`) |
| `rights@0` | a rights environment whose `vocabulary` is not an object | `AttributeError` (`ve/rights.py:53`) | `InvalidInput: invalid rights block` |
| `rights@0` | a correlated vocabulary `E″′` with more than 256 predicates | `ResourceLimit: extended vocabulary` (the soft 6.4b check inside `SoftNormDocument`) | no check known from reading on the rights route (`validateRights` calls `validateSoft` and the decision-name length only) |
| `reports@0` | more than 1,000 bridges, or more than 256 scoped checks | `ResourceLimit: bridges or scoped` (`ve/reports.py:133–134`) | no check (`Wire.lean:392–393`) |
| `reports@0` | a `scoped` check whose `conclusion` has a key beside `ast` | `InvalidInput: scoped` (`:429`) | `exactFields c ["ast"]`, a rejection too; not a verdict difference, a text difference (2.20a) |
| `ve-units@1` | a W6 environment whose `to_dict()` differs canonically from the submitted dictionary | `W6 environment does not round-trip to its canonical declaration` (`ve/environment.py:611–612`) | no check; no input is known from reading that reaches it |

A verdict difference is fixed outside this plan: in Python first where Python's verdict changes, and by a
reviewed Lean change with its own statement review where Lean's would (the rights name format is the one case
from reading where Lean accepts what the spec, rights.md 3.2, says to reject). Class differences between the two
legacy validators are not S8-pre's: they are recorded in the delta (`lean_route_changes`,
`legacy_class_differences`) and the contract keeps the authority's classes (D3).

### 2.14 What is constructed and what is tested

By construction:

- **(A) The public record is the measured one.** Each call site reports `overlay(run(…))` through its
  `public_rejection`, and the gate measures the delta with the same two functions on the same registry.
- **(B) In Lean only the generated tables' revisions change at a switch.** The engine reads a table's phases
  only, and revision `R` has the phases of the revision before it (T3, L4).
- **(C) The base spec's claims (A) and (B)** hold for the three contracts: the expansion, and the record
  conditional on equal predicate results. The viewed include of `rights@0` is a scope of base spec 2.6 whose
  view is the same function in both languages where `stripRights` succeeds and the identity where it does not
  (2.6); `run_congr_reached` asks for views equal on every value, and that equality is tested (R9).
- **(D) The class rule, on the authority's side**: for `ve-units@1` on the Python side for every check that is
  not exempt (the code's class is the class Python raises); for `rights@0` and `reports@0` on the Lean side
  (the code's class is `checker_error`'s class of the Lean text the member stands for).

Tested, not constructed:

- that each engine reports a fault exactly when its legacy validator rejects, on the corpus, at zero tolerance,
  and that the classifier members agree between the two engines;
- that the Python walks of 2.6 refuse the same member as the frozen Lean functions, on every catalogue fault
  and pair (tiers 0 and A);
- that the signed list is complete: on the corpus only;
- that Python's public text equals the text of Lean's `ve_diagnose` record: on every corpus case that Lean
  reads, for checks that are not inherited;
- for `rights@0` and `reports@0`, that the Lean route's own text is the record's text on every corpus case
  that Lean reads, except on the checks section 6 lists (D2);
- V1 to V4 of 2.9.

Not claimed: that a Lean route's own text on a multi-fault `ve-units@1` input is the record's (the table's
order is Python's). Not claimed either: that an input outside the domain gets a record, or that Rust's texts
relate to the record's.

## 3. English: one reading each

### 3.1 The hand-written sentences

The generated wordings of base spec 3.1 cover every T1 row of the three tables; `tools/wire_contract.py` writes
them to `docs/spec/rights-wire-table.md`, `reports-wire-table.md` and `ve-units-wire-table.md`. The hooks,
members and the view carry these `says` sentences. "The item" is the innermost group's item, which the
generated lead names (`For the `tags` item: `); "the enclosing item" is the group one level out. Each string is
exactly as shown, backticks included.

`rights@0`:

```json
{"soft":  "The view gives the object with two members: `environment`, which is `/environment` with `rights@0` removed from `profiles` and the member `rights` removed from `vocabulary`, and `norms`, which is the empty array; every included check reads that object and nothing else of the input.",
 "4.3a": "The item is not a second `source_units` unit.",
 "4.3b": "The item's `source_units`, when present, is an array of strings.",
 "4.3c": "The item decodes under the rights decoder for its form: a right with `name`, `holder`, `lines` and optionally `guard`; a `right_lines` with `right` and `lines`; a limitation with `name`, `scope`, `kinds`, `conditions`, `factors` and optionally `decided_by`; a bar with `name`, `reading` and optionally `decided_by`; a norm unit with `norm` and optionally `cites`; each line with `kind` and the fields of its kind, its norm objects as soft norm objects.",
 "4.3d": "Every line's `kind` is one of `claim`, `liberty`, `immunity`, `power`.",
 "4.3e": "Every `fan_out` value is a string.",
 "4.3f": "Every `cites` is an object.",
 "4.3g": "Every `cites` entry is a non-empty array of strings.",
 "4.3h": "A `right_lines` unit names a right declared by an earlier unit.",
 "4.3i": "A limitation's `kinds` is `all` or an array.",
 "4.3j": "A limitation's `decided_by`, when present, is a string.",
 "4.3k": "Every condition's `role` is `necessary` or `sufficient`.",
 "4.3l": "A condition's `decided_by`, when present, is a string.",
 "4.3m": "A bar's `reading` is `rule` or `query`.",
 "4.3n": "A bar's `decided_by`, when present, is a string.",
 "4.3o": "The item's keys are exactly `source_units`, `right`, `right_lines`, `limitation` or `bar`, or include `norm`.",
 "5.1a": "`holders` and `bearers` are non-empty.",
 "5.1b": "Every holder and bearer is a declared sort.",
 "5.1c": "No holder is repeated.",
 "5.1d": "No bearer is repeated.",
 "5.1e": "Every protected name is a declared base predicate with a holder-sort argument.",
 "5.1f": "No `alters` act is repeated.",
 "5.1g": "Every `alters` entry names a permission whose `holder_slot` argument is a holder sort, a `status` that is a base predicate with that sort, and, when present, a `recognition` that is an obligation with a bearer subject and that holder sort among its arguments.",
 "6.3a": "No right, limitation, bar or rule name begins with `rights-`.",
 "6.3b": "No right name is repeated among the names of rights, limitations, bars and rules.",
 "6.3c": "No limitation name is repeated among them.",
 "6.3d": "No bar name is repeated among them.",
 "6.3e": "No rule name is repeated among them.",
 "6.3f": "No regulated or defined predicate begins with `rights__`, and no generated name is already declared.",
 "6.3g": "No `over` entry begins with `rights-`.",
 "6.4a": "Every right's `holder` is a holder sort.",
 "6.4b": "Every right's `guard` is well typed over its holder; the fault is a type mismatch.",
 "6.4c": "Every right's `guard` is well typed over its holder; the fault is a predicate, constant or binder sort that is not a declared name.",
 "6.4d": "Every right's `guard` is well typed over its holder; the fault is a variable index outside its scope.",
 "6.4e": "Every right's `guard` passes the checker after passing the diagnostic.",
 "6.4f": "Every line and every line instance has the shape of its kind: a claim on a bearer-subject obligation with sign true or permission with sign false, a liberty on a holder-subject permission with sign true, an immunity on a bearer-subject permission with sign false whose act alters that holder slot, a power with a liberty whose act alters slot 0 with a recognition and that recognition.",
 "6.4g": "Every fan-out map names each bearer once, and maps it to a regulated predicate with that bearer as subject and the first mapped predicate's act, role and other sorts.",
 "6.4h": "A line whose predicate has two object slots of the holder sort names its `holder_slot`.",
 "6.4i": "No line instance has more than six carve-outs.",
 "6.4j": "Every right has at least one line.",
 "6.5a": "A limitation's `scope` is `all` or a non-empty list.",
 "6.5b": "Every right a `scope` names is declared.",
 "6.5c": "A limitation's `kinds` is `all` or a non-empty list.",
 "6.5d": "No limitation has more than eight conditions.",
 "6.5e": "Every condition's `name` is an identifier.",
 "6.5f": "A condition's `decided_by`, when a string, is 1 to 64 bytes.",
 "6.5g": "No condition name is repeated within its limitation.",
 "6.5h": "A limitation's `decided_by`, when a string, is 1 to 64 bytes.",
 "6.5i": "Every limitation has a `decided_by`.",
 "6.6a": "There is at most one bar.",
 "6.6b": "The bar's `decided_by`, when a string, is 1 to 64 bytes.",
 "6.7":  "Every `cites` target is one of the `source_units` ids.",
 "7.1a": "The correlated soft document stays within the W1 node budget.",
 "7.1b": "The correlated soft document's author precedence is acyclic.",
 "7.1c": "The correlated soft document's precedence depth is at most sixteen.",
 "7.1d": "The correlated soft document's base rules are stratified.",
 "7.1e": "In the correlated soft document no default rule takes precedence over a strict rule.",
 "7.1f": "The correlated soft document's derived carve-outs stay within resource limits.",
 "7.1g": "The correlated soft document's softened rules are stratified.",
 "7.1h": "The correlated soft document's softened rules satisfy W1 resource limits.",
 "7.1i": "Each generated soft premise of the correlated soft document stays within resource limits.",
 "7.1j": "Each generated norm layer of the correlated soft document stays within resource limits.",
 "7.1k": "Each generated conflict target of the correlated soft document stays within resource limits.",
 "7.1l": "The correlated soft document's generated background stays within one budget.",
 "7.1m": "The correlated soft document's generated norm layers and the one-node conclusion of the smallest query together fit one checker's budget of 10,000 nodes.",
 "7.2":  "Every generated decision predicate name of the correlated soft document is at most 64 bytes long in UTF-8.",
 "7.3":  "The correlated rights document is stratified: no bar node is named in any rule's `over`, no right permission has a dual, and every own guard, selector, condition, limitation pack, aimed formula and limitation premise is well typed."}
```

`reports@0`:

```json
{"1.6":  "The frozen profile classifier accepts `/environment/profiles` without `reports@0` as the FOL family.",
 "1.19": "The item's `verbalisation` is a non-empty string of at most 256 characters.",
 "1.20": "The P0 vocabulary decoder accepts `/environment/vocabulary` without `reports` and without any constant's `verbalisation`, under `/environment/profiles` without `reports@0`.",
 "1.21": "`/environment/vocabulary/reports/holders` has 1 to 8 members, no two equal.",
 "1.22": "The item is a key of `/environment/vocabulary/sorts`.",
 "1.23": "`/environment/vocabulary/reports/evidence` is a key of `/environment/vocabulary/sorts`.",
 "1.24": "No constant of a holder sort has a `verbalisation` that reads `the stated assessment` after ASCII lower-casing.",
 "2.6":  "The item's `span` has its first member at most its second.",
 "2.7a": "The item has exactly the keys `id`, `span`, `kind`, `content`, `meaning`, `support` when its content is a report, assessment or negated node, and otherwise the keys `id`, `span`, `kind` and optionally `content`, `meaning`, `support`.",
 "2.7b": "The item's `content`, when present, is an object with one tag; a report, assessment or negated node when it holds one of those tags; `{\"ast\": …}` otherwise, on a kind that is not quoted.",
 "2.7c": "Every report node's `act` is one of `says`, `believes`, `wants`, `intends`.",
 "2.7d": "Every assessment node's `judgment` is `may` or `probably`.",
 "2.7e": "Every report node's `literal`, when present, is a non-empty string.",
 "2.7f": "Every report node's `literal` is at most 4,096 bytes long in UTF-8.",
 "2.7g": "Every negated node wraps a report or assessment node.",
 "2.7h": "Every formula node decodes as a closed formula, and every quoted norm or definition package decodes under its pinned environment.",
 "2.7i": "The item's `kind` matches its content tree: `attributed` with the holder and act for a report node, `hedged` with `could` or `likely` for a `may` or `probably` assessment, a negated node transparent.",
 "2.7j": "The item's content tree is at most 40 levels deep.",
 "2.8":  "The item's `meaning`, when present, is `specified`, or an object with one member `open` (an array of strings), `contextual` (a string) or `unformalised` (a string).",
 "2.12": "Every unit's span starts at or after the previous unit's span ends.",
 "2.14a": "The item is an object with `id`, `tense`, `description` and optionally `reference_time`, each a string.",
 "2.14b": "The item's `id` is a token.",
 "2.14c": "The item's `tense` is `present`, `past` or `perfect`.",
 "2.14d": "The item's `reference_time`, when present, is a token.",
 "2.14e": "The item's `description` is not empty.",
 "2.14f": "The item's `description` is at most 200 bytes long in UTF-8.",
 "2.17a": "The item has a `decided_by`.",
 "2.17b": "The item has exactly the keys `id`, `context`, `decided_by`, `necessary`, `sufficient`, `factors`, `precedents`, `jurisdiction`, `version`, with strings, arrays and a natural number where each is due, a token `jurisdiction`, a `version` of at least 1 and no empty factor or precedent.",
 "2.17c": "The item's `id` is a token.",
 "2.17d": "Every criterion of the item decodes as a formula.",
 "2.19a": "The item is an object with `id`, `unit`, `accepted_by`, `reason` and optionally `path`, with strings where each is due and `reason` an array of strings.",
 "2.19b": "The item's `path`, when present, is `1`, `1.1`, `1.1.1`, and so on.",
 "2.20a": "The item is an object with `id`, `payloads`, `conclusion` and optionally `certificate`, `envelope`, with `id` a string, `payloads` an array and `conclusion` an object with exactly the key `ast`.",
 "2.20b": "Every payload path is a unit id or an object with `unit` and a `path` of the form `1`, `1.1`, `1.1.1`, and so on.",
 "2.20c": "The item's conclusion decodes as a formula.",
 "2.20d": "The item has no `envelope` without a `certificate`.",
 "3.1a": "No context id is repeated.",
 "3.1b": "No assessment id is repeated.",
 "3.1c": "No bridge id is repeated.",
 "3.1d": "No scoped check id is repeated.",
 "3.1e": "Every assessment's `context` is a constant of the evidence sort.",
 "3.1f": "Every assessment's `decided_by` is a token.",
 "3.1g": "Every assessment criterion is closed and typed over the environment.",
 "3.1h": "Every unit's content tree is at most 16 levels deep.",
 "3.1i": "Every report node's `holder` is a declared constant.",
 "3.1j": "Every report node's `holder` has a holder sort.",
 "3.1k": "Every report node's `context` is a declared context.",
 "3.1l": "Every assessment node's `record` is a declared assessment.",
 "3.1m": "Every negated node wraps a report or assessment node.",
 "3.1n": "Every formula node, and every definition package's statement, is closed and typed over its environment.",
 "3.1o": "No two distinct digested objects share a digest.",
 "3.1p": "No scoped check has more than 64 payloads.",
 "3.1q": "Every scoped payload path resolves to a formula node.",
 "3.1r": "All payloads of a scoped check lie over one environment, over which its conclusion is closed.",
 "3.1s": "Every bridge's target path resolves.",
 "3.1t": "Every bridge's target is a formula or report node over the author's environment.",
 "3.1u": "Every unit's `support`, when present, is one of W2's eight.",
 "3.1v": "A unit whose root kind is `unformalised` has the meaning `{\"unformalised\": <the same reason>}`.",
 "3.1w": "Every unit's `meaning` is W2's; an `open` list names declared or generated terms; a report unit that is `specified` has no assessment node, and a report unit with assessment nodes is `open` and lists every generated assessment name of its tree.",
 "3.1x": "Every generated name is undeclared, at most 64 bytes and distinct, and the author's and generated predicates together are at most 256.",
 "3.1y": "The document is well-formed."}
```

`ve-units@1` (the S members once; a `statement` entry's members carry them, with `the statement` naming the
entry's target):

```json
{"1.2":  "`/environment/language` is `ve.core@0.2` and the frozen profile classifier accepts `/environment/profiles`.",
 "1.4":  "`/environment/profiles` is exactly `order@0`, `relational-fol@0`, `time@0`, with `documents@1` first or not at all.",
 "2.4":  "The key of the item is an identifier (`[a-z][a-z0-9_]*`, at most 64 bytes) other than `dimensionless`.",
 "2.7a": "The item's `scale` is at most 40 characters.",
 "2.7b": "The item's `scale` is an optional minus and digits.",
 "2.7c": "The item's `scale` is canonical: no leading zero, no `-0`.",
 "2.7d": "The item's `scale` is `1` followed by zeros.",
 "2.17a": "The item's `input_symbol` is not empty.",
 "2.17b": "The item's `input_symbol` is at most 256 characters.",
 "2.17c": "The item's `input_symbol` is words of non-space characters joined by single spaces, with at most one trailing space.",
 "2.20a": "The item's `label` is not empty.",
 "2.20b": "The item's `label` is at most 256 characters.",
 "2.20c": "The item's `label` is words of non-space characters joined by single spaces.",
 "2.24": "When the item's display kind is `iso_date`: the key of the item is `day` and its `scale` is `1`.",
 "2.25": "When the key of the item is `day`: the item is exactly `{\"scale\": \"1\", \"display\": {\"kind\": \"iso_date\"}}`.",
 "2.26": "When the key of the item is `elapsed_day`: the item is exactly `{\"scale\": \"1\", \"display\": {\"kind\": \"decimal\", \"label\": \"days\"}}`.",
 "2.27a": "No enabled affix of `/environment/units` begins (a prefix) or ends (a suffix) with a digit, a minus or a point.",
 "2.27b": "No two enabled affixes on one side of `/environment/units`, taken in sorted tag order, have one a prefix of the other.",
 "3.1":  "The P0 order vocabulary decoder accepts `/environment` with `unit_schema`, `units`, every `argument_units`, every constant's `unit` and `verbalisation` removed.",
 "3.3":  "The key of the item is `0` or digits without a leading zero, below the predicate's arity.",
 "3.4":  "The predicate's argument at the item's index is `$int`.",
 "3.6":  "The item is `dimensionless` or a key of `/environment/units`.",
 "3.7":  "When the item's `unit` is present: the item's `sort` is `$int`.",
 "3.9":  "The item's `unit` is `dimensionless` or a key of `/environment/units`.",
 "4.1":  "Neither `dimensionless` nor any key of `/environment/units` is a key of `/environment/vocabulary/sorts`.",
 "4.2":  "No constant has the sort `$string`.",
 "4.3a": "Every constant's `verbalisation`, in sorted name order, is not empty.",
 "4.3b": "Every constant's `verbalisation` is at most 256 characters.",
 "4.3c": "Every constant's `verbalisation` is words of non-space characters joined by single spaces.",
 "4.3d": "No two constants' verbalisations are equal after their first letter is ASCII-uppercased.",
 "5.8a": "The item's `span` has exactly two members, the first at most the second.",
 "5.8b": "Each member of the item's `span` is a natural number.",
 "5.9":  "The item's `kind` decodes under W2's kind decoder.",
 "5.13": "Every unit's span starts at or after the previous unit's span ends.",
 "5.15a": "The item is an object with exactly `name`, `conclusion`, `leaves`, `certificate`.",
 "5.15b": "The item's `name` is a string.",
 "5.15c": "`cite:` followed by the item's `name` parses as a citation label.",
 "5.18a": "The item is an object with exactly `quantity`, `label`.",
 "5.18b": "The item's `label` is a string.",
 "5.18c": "The item's `label` parses as a label.",
 "5.18d": "The item's `label` is not a citation.",
 "5.21": "The item's `certificate` is an object with exactly `format`, `environment_id`, `premise_meaning_ids`, `conclusion_meaning_id`, `core`, and `format` is `ve-quantity-certificate@1`.",
 "5.22": "The item's certificate establishes its conclusion from exactly its leaves, in order, bound to their annotated meaning ids.",
 "5.24a": "Every member of `/document/open_terms` is a string.",
 "5.24b": "Every member of `/document/open_terms` is a token.",
 "5.25a": "The item is an object with exactly `id`, `version`, `readings`.",
 "5.25b": "The item's `id` is a string.",
 "5.25c": "The item's `id` is a token.",
 "5.25d": "The item's `version` is a natural number.",
 "5.25e": "The item's `readings` is an array.",
 "5.27": "The item's `readings` has 1 to 64 members.",
 "5.28": "No two reading sets of `/document/reading_sets` share an `id` and a `version`.",
 "5.29a": "Every member of `/document/narrowings` is a string.",
 "5.29b": "Every member of `/document/narrowings` is a token.",
 "5.34a": "The item is an object with `name`, `quantity` and optionally `label`, `unit`, `premises`, `certificate`.",
 "5.34b": "The item's `name`, and its `label` when present, are strings.",
 "5.34c": "The item's `label`, when present, is not `asserted`.",
 "5.36a": "The item's `unit`, when present, is a string.",
 "5.36b": "The item has `premises` and `certificate` both or neither.",
 "5.36c": "The item's `premises`, when present, is an array.",
 "5.36d": "Every member of the item's `premises` is a string.",
 "5.36e": "The item's `certificate`, when present, has the shape of 5.21.",
 "5.37a": "No node names a quoted unit unless it is a bridge leaf naming that unit.",
 "5.37b": "Every node is admitted under its label: a deduction is `asserted` and names an asserted unit with its statement if it names one; a leaf meets its label's provenance rule.",
 "5.37c": "Every node's label parses.",
 "5.38": "The graph's node names are distinct, every premise names an earlier node, every deduction's certificate is valid for exactly its premises and conclusion, and the root is a node.",
 "5.39": "Every cited lemma's leaves are in the report with their labels.",
 "5.40": "The report's reading choices are compatible.",
 "S.a":  "The statement is an object with `format`, `formula` and optionally `traces`, `Q`.",
 "S.b":  "The statement's `format` is `ve-quantity@1`.",
 "S.c":  "The statement's `traces`, when present, is an array.",
 "S.d":  "The statement's `traces` is empty.",
 "S.e":  "The statement's `formula` has at most 10,000 array nodes, none past the 10,000th or deeper than 64 levels.",
 "S.f":  "Every unit tag in the statement is `dimensionless` or declared.",
 "S.g":  "Every decimal literal in the statement lies on its tag's grid.",
 "S.h":  "Every `date` literal in the statement is a valid calendar date.",
 "S.i":  "Every `date` literal in the statement is on or after 1970-01-01.",
 "S.j":  "Every decimal literal in the statement is an optional minus, digits without a leading zero and optionally a point and digits.",
 "S.k1": "Every integer literal in the statement is at most 40 characters.",
 "S.k2": "Every integer literal in the statement is a canonical decimal string.",
 "S.l1": "Every decimal literal in the statement has at most 40 digits.",
 "S.l2": "Every lowered coordinate in the statement is at most 40 characters.",
 "S.m":  "Every pair of terms the statement compares, adds or passes to a slot have one type, no object constant carries a unit, no calendar date is scaled or added, and every order comparison is between quantities.",
 "S.n":  "The statement has no `$int` binder, no tagged variable, no n-ary atom and no W6b form.",
 "S.o1": "Every constant the statement names is declared.",
 "S.o2": "Every predicate the statement names is declared with the arity used.",
 "S.o3": "Every variable index in the statement is within its scope.",
 "S.p":  "Every node of the statement is a tagged array of a known tag with its number of members, every binder names a sort, and every day offset is non-negative.",
 "S.q":  "The statement's `Q`, when present, equals the regenerated annotated formula.",
 "S.r":  "The regenerated core decodes in the erased environment."}
```

### 3.2 How a public rejection reads

The S4 spec's four sentences (its 3.1) apply to every record of every unit, with the check id as the record
gives it. Two forms are new here:

| The record is | Sentence |
|---|---|
| under the view (`rights@0`, `soft/<id>`) | `This input is rejected. The first check that fails is soft/<id>, inside the view soft_source_of_rights of /environment, at <inner_path> inside it: <wording>` where `<wording>` is the pilot's row for `<id>` in `docs/spec/soft-norms-wire-table.md` |
| a classifier member whose text is inherited | `This input is rejected. The first check that fails is <id>: <wording> The message shown is this program's own.` |

Example, for the source of fixture R9 (parties `["p", "Q!"]` in a rights environment): `This input is rejected.
The first check that fails is soft/2.7a, inside the view soft_source_of_rights of /environment, at
/environment/vocabulary/soft/parties/1 inside it: The `parties` item, when present, is a string in the class
`soft_name`.` "First" always means the order of base spec 2.6, which the table file shows from top to bottom;
under an include it is the including contract's order, and the view's sentence (3.1, `soft`) says what the
included checks read.

### 3.3 Wordings this replaces, and why

| Wording | Its two readings | Written instead |
|---|---|---|
| "`rights@0`, `reports@0` and `ve-units@1` are switched from shadow." (the pointer) | the three contracts exist and are in shadow; or they are to be written, shadowed and then switched | "Each contract is authored, run in shadow, measured, signed and then switched; none exists before item 1." |
| "The order is the authority's." | Lean's, for all three; or the manifest's authority per unit | "The tables of `rights@0` and `reports@0` are in the Lean routes' order and the table of `ve-units@1` in Python's; a difference from the other validator's order is reported, and for the first two the Lean route's text is also enforced to equal the record's except on the listed checks." |
| "The diagnostics become uniform." | the three languages print one message; or Python's message is the contract's text, which equals the Lean engine's record | "On every corpus case that Lean reads, Python's message is the text of the record that `ve_diagnose` gives for the same source, except on inherited checks. Rust is not run." |
| "Rights reuses the soft phases." | it calls the soft validator as one coarse check; or it includes the pilot's phases, check by check, on a transformed value | "`rights@0` includes the pilot's six phases at `/environment` under the view `soft_source_of_rights`, so each soft check is its own instance with its own id and code, its `path` is `/environment` and its pointer inside the view is `args.inner_path`." |
| "The record's class is the error's class." | always; or where the contract declares it so | "On `ve-units@1` the record's class is the class Python raises, except on the listed exempt checks. On `rights@0` and `reports@0` it is the class of the Lean route's text; Python's `code` may differ and the gate counts those cases." |
| "`path` points into the input." | into the submitted root; or into the value a view gives | "Under the view, `path` is `/environment` and `args.inner_path` is the pointer inside the value the view gives." |
| "The statement set is one classifier." | one entry in the table; or one member list emitted at five entries | "S is one member list, emitted by the five `statement` entries with the entry's id as prefix; the lint checks the five copies are equal." |
| "`code` is unchanged." | the error's `code`; or the record's | "The error's `code` is the legacy validator's class, as today. The record's `code` is the contract's; its `class` is the authority's." |
| "The delta report is complete." | no other message can change; or none on the corpus | "Every message change on the unit's corpus is in the report." |
| "Rust is deferred." | Rust runs the table and defers on a hook; or Rust is not run | "Rust has no engine and is not run on any of the three units; its texts and tolerances stay." |
| "A deep content tree is rejected." | at the content decoder's bound of 40; or at `WellFormedReports`' 16 | "A unit whose kind is deeper than 16 is outside the domain (the loader's W2 check); a content deeper than its kind is `KindMismatch` (2.7i); the two depth members are unreached and declared so." |

### 3.4 The release notes

The `release_note` of each signing file is this text, with the unit's name and the list filled from `signed`.
For `rights@0`:

> When `ve document check` in `ve` rejects a document whose environment lists `rights@0` while it validates
> the rights environment or correlates the rights source, the error now has one more member, `diagnostic`:
> the error carries the contract's record. When a check of the table fails, the record names the first one
> that fails and the message is that check's text; otherwise the message is the validator's. The table is
> `docs/spec/rights-wire-table.md`; "first" is its order from top to bottom, which is the Lean rights route's
> order. With the check, the record gives the place in the input and a code; for a check of the included soft
> table the place is `/environment` and the pointer inside the stripped environment is in `args.inner_path`.
> For many rejections the message is the same as before. It is a different message for these checks. ⟨for
> each signed check, in table order: its id, a colon, a space, and its sentence from `signed`, the entries
> separated by a space⟩ Whether a document is accepted or rejected has not changed. The public switch does not
> change the error's `code`; where the Lean route classifies the same fault under another class, the record's
> `class` says so. An error raised before that validation, while the document's front matter is split, or
> after it, while the units are checked or the document is admitted by the Lean route, has no record, and its
> message is as before. Other ways of submitting a rights source (the readings route, the completions audit,
> English input) report as before.

For `reports@0`, the same with "while it validates the reports environment or the reports document",
`docs/spec/reports-wire-table.md`, "the Lean reports route's order", without the sentence on the included
table, and with the last sentence listing "the reports routes' own cases, English input". For `ve-units@1`:

> When document admission in `ve` rejects a quantity document, one whose environment carries `unit_schema` and
> `units`, while it validates the environment or admits the document, the error now has one more member,
> `diagnostic`: the error carries the contract's record. When a check of the table fails, the record names the
> first one that fails and the message is that check's text; otherwise the message is the validator's. The
> table is `docs/spec/ve-units-wire-table.md`; "first" is its order from top to bottom. With the check, the
> record gives the place in the input and a code: a malformed date, a date before 1970, a decimal off its
> unit's grid and an undeclared unit tag each have a code of their own. For most rejections the message is the
> same as before. It is a different message for these checks. ⟨the signed list⟩ Whether a document is accepted
> or rejected has not changed. The public switch does not change the error's `code`. The Lean quantity route
> and the Rust decoder print as before. An error raised while `ve document check` elaborates a unit's
> statement, before admission, has no record, and its message is as before.

### 3.5 The paragraphs added to the three specs

To rights.md, section 8, after its order paragraph:

> **The public record.** When `ve document check` rejects a document under `rights@0` while it validates the
> rights environment or correlates the rights source, the error carries the contract's record, in its member
> `diagnostic`. The contract is the wire contract `rights@0` ([rights-wire-table.md](rights-wire-table.md);
> [wire-contract.md](wire-contract.md) 2.7). When a check of the table fails, the record names the first one
> that fails and the message is that check's text; otherwise the message is the validator's. The checks, their
> order and their texts are those of the Lean rights route (`decodeRightsSource`, `validateRights`), each with
> one code; the soft checks on the stripped environment are the soft table's, included under a view, so their
> place is `/environment` with the inner pointer beside it. The contract chooses the message only: the
> validator decides, as before, whether the document is rejected.

To attribution.md, section 8, after its order paragraph: the same with "under `reports@0` while it validates
the reports environment or the reports document", `reports-wire-table.md`, "the Lean reports route
(`decodeDocument`, `firstFailure`)", and without the sentence on the soft checks.

To units-schema.md, section 3.2, after step 5:

> **The public record.** When document admission rejects a quantity document while it validates the
> environment or admits the document, the error carries the contract's record, in its member `diagnostic`. The
> contract is the wire contract `ve-units@1` ([ve-units-wire-table.md](ve-units-wire-table.md);
> [wire-contract.md](wire-contract.md) 2.7). When a check of the table fails, the record names the first one
> that fails and the message is that check's text; otherwise the message is the validator's. The checks and
> their order are Python's (`Environment`, `admit_quantity_document`, `elaborate_quantity`), each with one code;
> `UnitPrecision`, `InvalidDate`, `DateRange`, `UnknownUnit` and the type mismatches are codes, and a malformed
> decimal literal has one class, `InvalidInput`. The contract chooses the message only: the validator decides,
> as before, whether the document is admitted.

## 4. Diagnostics

### 4.1 The public errors

For the source of fixture R8 (base B_R with a second right named `r9`), `to_dict()` of the raised error is:

```json
{"code": "DuplicateDeclaration", "message": "DuplicateDeclaration: right r9",
 "diagnostic": {"contract": "rights@0", "revision": R, "check": "6.3b", "phase": "rights",
                "code": "RIGHTS_DUPLICATE_DECLARATION", "class": "DuplicateDeclaration", "path": "/document",
                "text": "DuplicateDeclaration: right r9", "args": {"value": "r9"}}}
```

Today it is `{"code": "DuplicateDeclaration", "message": "right r9"}`. For the source of fixture R9 (the soft
block's parties `["p", "Q!"]`), the record is under the view:

```json
{"code": "InvalidInput", "message": "InvalidInput: invalid soft name Q!",
 "diagnostic": {"contract": "rights@0", "revision": R, "check": "soft/2.7a", "phase": "soft",
                "code": "SOFT_INVALID_NAME", "class": "InvalidInput", "path": "/environment",
                "text": "InvalidInput: invalid soft name Q!",
                "args": {"value": "Q!", "inner_path": "/environment/vocabulary/soft/parties/1"}}}
```

For the source of fixture P9 (a report whose holder is `claude`, a constant of sort `model`, not a holder sort):

```json
{"code": "InvalidInput", "message": "HolderSort: claude is not of a holder sort",
 "diagnostic": {"contract": "reports@0", "revision": R, "check": "3.1j", "phase": "wellformed",
                "code": "REPORTS_HOLDER_SORT", "class": "InvalidInput", "path": "/document",
                "text": "HolderSort: claude is not of a holder sort", "args": {"holder": "claude"}}}
```

For the source of fixture Q13 (unit 0's statement compares `["decimal", "bp", "3.755"]`):

```json
{"code": "InvalidInput", "message": "UnitPrecision(bp, scale=100)",
 "diagnostic": {"contract": "ve-units@1", "revision": R, "check": "5.10g", "phase": "document",
                "code": "UNITS_UNIT_PRECISION", "class": "InvalidInput", "path": "/document/units/0/content",
                "text": "UnitPrecision(bp, scale=100)", "args": {"tag": "bp", "scale": "100"}}}
```

With a residual record or a deferred record, `message` is the legacy text and `diagnostic` is the record of base
spec 4.1. With no record, `to_dict()` is today's.

### 4.2 Field by field

As S4 spec 4.2: the object and its type are the legacy validation's; `code` is unchanged and never written;
`message`, `str(error)` and `to_dict()["message"]` are the reported record's `text`; `diagnostic` is the
reported record, before the switch `None` and no member; `path` and `span` are unchanged, and the record's
`path` is not copied into `error.path`; every other member of `to_dict()` is unchanged, `VEError.to_dict` not
being edited. The legacy errors of these units set a `path` in one place: `require_fields` inside
`Environment` (`ve/wire.py:102–108`) and the loader's W2 checks; such a `path` stays a member and is relative
to the environment, while the record's is relative to the root (S4 spec 4.2). On `rights@0` and `reports@0` the
record's `class` is Lean's and may differ from `code` (2.13). A consumer that validates Python's error object
against a closed shape must admit `diagnostic`; the switch commits list every such schema and stored
expectation they had to change.

### 4.3 Lean

- Every row of `ve_rights_route`, `ve_reports_route` and `ve_quantity` is byte-identical to its row before each
  switch, on every corpus case that Lean reads.
- `ve_diagnose rights@0`, `ve_diagnose reports@0` and `ve_diagnose ve-units@1` print the records of 2.3 to 2.5;
  after a switch, the same rows with the new `revision`.
- Where a Lean route's text differs from the record's on a one-fault input (section 6, the allowed set), the
  route keeps its text. That is not a public change: no Lean output switches.

### 4.4 Tool diagnostics

`tools/wire_contract.py` gains one lint clause and no other code: `WC12`, a `statement` entry of `ve-units@1`
whose members differ from S's (ids beyond the prefix, codes, texts, `returns`, `inherited`, `says`); the set S is
read from the first `statement` entry in table order (5.10). After S5.0 its findings name the contract.
Raising `status` without the revision is `WC10`; `rights@0` without `soft-norms@0` in `uses` is `WC09`; a hook
or member without a fault in its catalogue and not declared unreached is `WC08`.

The gate prints the S4 and S5 lines with the unit named, and these in addition:

| Line | Printed when |
|---|---|
| `gate fails: <unit>: legacy crashes <list>` | Python raised something other than a `VEError` on a corpus case (S8-pre) |
| `gate fails: <unit>: lean route differs on <check> in <n> cases` | `rights@0` or `reports@0`: the Lean route's text differs from the record's on a check section 6 does not list (D2) |
| `gate reports: <unit>: legacy class differences <n>` | `rights@0` or `reports@0`: Python's legacy code differs from the record's class; informative (2.13) |
| `gate fails: <unit>: public delta: <n> class differences` | `ve-units@1`: the class rule fails on `<n>` cases outside the exemptions |
| `gate reports: <unit>: viewed records <n>` | `rights@0`: records with `path` `/environment` and an `inner_path`; informative (plan section 8, question 10) |

## 5. Lean: the statements relied on, the Lean modules and the scratch file

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

These four, and their four helpers, are in `VE/Audit.lean`. Item 1 changes none of them and does not touch
`VE/Audit.lean`, `lean/axioms.txt` or `tools/check_lean_imports.py`. `run_congr_reached` covers the viewed
include of `rights@0`: its hypothesis `hv` asks the two hook sets' views to agree on every name and value, which
is why the view is defined as a total function on every value (2.6) and tested as such (R9). No theorem relates a
contract to a decoder (base plan 3.2); none is added by the build.

### 5.2 The hooks modules

`lean/VE/WireContract/Hooks/Rights.lean`, `Hooks/Reports.lean` and `Hooks/Units.lean`, hand-written, in the shape
of `Hooks/Norms.lean`: `predicate`, `classifier`, `view`, `hooks`, `adapter` and `registered`, and a `#guard`
that every hook, classifier and view name occurring in the unit's generated table is one it registers.
`Hooks/Rights.lean` imports `Hooks/SoftNorms.lean` and dispatches the pilot's names to its `predicate` and
`classifier`; its `view` is `soft_source_of_rights` and the identity on every other name. Each imports the
frozen modules it calls read-only (`VE.Rights.Wire`, `VE.Rights.Correlate`, `VE.SoftNorms.Phases`;
`VE.Attribution.Wire`, `VE.Attribution.Content`, `VE.Route.Gate`, `VE.Route.Wire`; `VE.Time.Wire`,
`VE.Time.Document`, `VE.Route.Admission`); none of those is edited.

The Lean classifiers of `rights@0` and `reports@0` call the frozen functions and read the member off the text's
leading words, as the pilot's `semanticMember` does; they hold no walk. The Python contract modules hold the
walks in those functions' order (2.6), diagnostic only and under no theorem; tiers 0 and A compare each walk with
the frozen function on every catalogue fault and pair, and a disagreement is an engine mismatch, never a silent
record.

### 5.3 The unit registry: a C4 exception

`ve_diagnose` finds a unit in `units`, a hard-coded list in `lean/VE/WireContract/Diagnose.lean`, a hand-written
module in the frozen inventory. S5 added two entries by an append-only edit and recorded it as the second C4
exception (S5 spec 5.3). Item 1 adds three `import` lines and three entries the same way, no existing line
changing, unless the DRI has taken S5's question 4 and moved the list to `lean/DiagnoseMain.lean`, which is not
hash-listed; then the three entries are lines there and no exception is needed. Either way the diff is reviewed
and the rehash of the module's inventory line goes with it.

### 5.4 Manifest, inventory, layers, imports

- **Inventory.** `Hooks/Rights.lean`, `Hooks/Reports.lean`, `Hooks/Units.lean`, `Tables/Rights.lean`,
  `Tables/Reports.lean` and `Tables/Units.lean` are added. `Limits.lean` and `Names.lean` are regenerated (new
  entries), and so are the pilot's and S5's tables, whose headers name the hashes of `limits.json` and
  `names.json`; those are generated rehashes. `Diagnose.lean` is the exception of 5.3.
- **Assurance manifest.** The `wire.diagnose` binding gains three modes: `rights@0` with the `rights-` kinds and
  `admission`, `reports@0` with the `reports-` kinds and `admission`, `ve-units@1` with `document` and
  `admission`, each dispatching to `Diagnose.lean` and its hooks module; the three hooks modules are classified
  under `other_json` as "diagnostic only: no verdict depends on it". Nothing else of the manifest changes: the
  call sites start no Lean process, and the pinned decoder total does not grow.
- **Layers.** `ve.rights_contract`, `ve.reports_contract` and `ve.units_contract` are in the layer of the module
  each reads (`ve.rights`, `ve.reports`, `ve.quantity_admission`), by `tools/layer_policy.py`'s rule for the
  S5 contract modules.
- **Imports.** The Lean rule of base spec 7.3 is unchanged: `VE.WireContract.*` is imported by
  `VE.WireContract.*`, `DiagnoseMain` and (the engine only) `VE.Audit`. The Python rule is the table of 2.9.

### 5.5 Optional statements about frozen code

Three statements, each the fact a hook of 2.6 rests on, stated exactly. They are optional in the sense of edit
c: the build may add them with an append-only `VE/Audit.lean` diff, or record them as open; the S4 review struck
optional statements of this kind as unnecessary, and the statement review decides again here. None is used by
the build.

```lean
/-- The rights decoder runs the soft table on the stripped environment with no norms: the value
    the view `soft_source_of_rights` gives (2.3, phase 3). -/
theorem rights_decode_checks_stripped (e d : Json) (src : VE.Rights.Wire.RightsSource)
    (h : VE.Rights.Wire.decodeRightsSource e d = .ok src) :
    ∃ s c, VE.Rights.Wire.stripRights e = .ok s ∧
      VE.SoftNorms.Phases.checkSource s (Json.arr #[]) = .ok c

/-- After a successful raw decode, the reports route's text is `firstFailure`'s: the members of
    classifier 3.1 of `reports@0` (2.4) are its branches in its order. -/
theorem reports_decode_text (e d : Json) (dec : VE.Reports.Wire.Decoded)
    (h : VE.Reports.Wire.decodeDocumentRaw e d = .ok dec)
    (hw : VE.Reports.WellFormedReports dec.D = false) :
    VE.Reports.Wire.decodeDocument e d = .error (VE.Reports.Wire.firstFailure dec.D)

/-- An admitted quantity statement has at most 10,000 array nodes in its submitted formula:
    member e of the statement set S (2.5) is checked before any elaboration. -/
theorem quantity_nodes_bounded (w : VE.Time.Wire.W6Env) (p : Json) (a : VE.Time.Wire.Admission w)
    (h : VE.Time.Wire.decodeQuantity w p = .ok a) :
    VE.Time.Wire.jsonNodes 257 (p.getObjValD "formula") ≤ 10000
```

What they do and do not say: the first says the view is the decoder's own transformation, not that the soft
table's verdict on it is the rights route's; the second says the table of 3.1 is the route's text in the route's
order, not that Python's walk is; the third bounds the count the Lean route checks and says nothing of Python's
`_source_nodes`. Each follows from unfolding one frozen definition.

### 5.6 The scratch file

`/tmp/wire-s8-stubs/Stubs.lean`, outside the repository, holds the statements of 5.1 and 5.5 as stubs (`sorry`,
allowed there and nowhere else) and the `#eval`s behind every number section 8 states: byte lengths of names,
the 80-byte cut of the `json` renderer, the dates and decimals of Q10 to Q14, the scales of Q5, the display
collision of Q6 and the node count of Q8. It is run from `lean/` with a built tree:

```
lake env lean /tmp/wire-s8-stubs/Stubs.lean
```

This draft's writer could not run it: the sandbox had neither a Lean toolchain nor a build. Every statement of
section 5 is therefore unchecked as of this draft, and every number of section 8 is a hand derivation with its
confirming `#eval` written beside it in the file. The build's first step (plan, S8-stubs) runs the file; a
statement that does not type-check or a number that differs is corrected in this specification before the
statement review reads it, and the correction is recorded in section 12.

## 6. The expected delta of each profile

"Only diagnostics may become uniform, listed per profile": these are the lists, from reading the validators and
the routes. None was run for this draft; the measured lists of 2.12 replace them, and the signatures are given
on the measured lists.

**`rights@0`.** Python's message at the call sites of 2.9:

| Check | Today | After the switch | Read from |
|---|---|---|---|
| 1.1 | `rights@0 is required` (an environment that is not a dict) | `UnsupportedProfile: profiles must be a sorted unique array` | `ve/rights.py:48`; `Wire.lean:109` |
| 1.4 | the soft table's 3.3c text, through `SoftEnvironment` | `UnsupportedProfile: rights@0 requires norms@0` | `ve/rights.py:68`; `Wire.lean:112` |
| 4.1 | `units` (`ResourceLimit`) | `InvalidInput: document must be an array`; a class difference, counted | `ve/rights.py:187`; `Wire.lean:285` |
| 4.2 | `units` | `ResourceLimit: units` | `:187`; `:286` |
| 4.3c | `InvalidInput: right`, `InvalidInput: right_lines`, `InvalidInput: limitation`, `InvalidInput: bar`, `InvalidInput: incident line`, `InvalidInput: incident line fields`, `InvalidInput: incident norm`, `InvalidInput: limitation factors`, and the soft texts of `decode_rule` | the Python walk's text for the shape (`fields do not match: expected [name, holder, lines], got […]`, `String expected`, …), as `ve.units._fields` spells Lean's | `ve/rights.py:214, 228, 235, 245, 255, 331, 336, 345, 433`; `Wire.lean:159–223` |
| 4.3d to 4.3n | `InvalidInput: incident line` (the kind), `InvalidInput: invalid fan-out`, `InvalidInput: line citations`, `InvalidInput: cites k must list unit ids`, `UnknownRight: r`, `InvalidInput: limitation kinds`, `MissingExceptionDecider: limitation l`, `InvalidInput: limitation condition`, `InvalidInput: bar reading`, `InvalidInput: bar decider` | the Lean texts of 2.3 | `ve/rights.py:331–342, 404–407, 237, 429–431, 442, 261–263` |
| 4.3o | `InvalidInput: rights unit <kind>` | `InvalidInput: invalid rights document unit` | `:268`; `Wire.lean:263` |
| 5.1a | `InvalidInput: holder must be a nonempty list` | `InvalidInput: invalid rights block` | `ve/rights.py:33`; `Correlate.lean:243` |
| 5.1g | `InvalidInput: alters <act>` | the same | — |
| 6.1, 6.2 | `rights`, `limitations` | `ResourceLimit: rights`, `ResourceLimit: limitations` | `:270–273` |
| 6.3b to 6.3e, 6.5g, 6.6a | `right r9`, `limitation l`, `bar`, `rule n`, `condition c` | with the class prefix: `DuplicateDeclaration: right r9`, … | `:217, 248, 253, 356, 370, 444` |
| 6.3a | `InvalidInput: name n begins with rights-` | the same | — |
| 6.4i | `ResourceLimit: carve-outs of rule n` | the same | — |
| 6.5a, 6.5c, 6.5e | `InvalidInput: limitation scope`, `InvalidInput: limitation kinds`, `InvalidInput: limitation condition` | `InvalidInput: invalid scope of limitation l`, `… invalid kinds of limitation l`, `… invalid condition c` | `:423, 429, 442` |
| 6.5d | `conditions` | `ResourceLimit: conditions` | `:418` |
| 6.5f, 6.5h, 6.6b | `MissingExceptionDecider: condition c` / `… limitation l` for an empty or non-string decider | `InvalidInput: invalid decider for condition c`, `… for limitation l`, `… for bar b` | `:430–431, 446–450, 262–263` |
| 7.1a to 7.1m | the pilot's Python texts for 6.5a to 6.15 on `T″` | the pilot's contract texts (S4 spec section 6) | the pilot's delta |
| 7.2 | `ResourceLimit: decision predicate n` | `ResourceLimit: identifier n exceeds 64 bytes` | `ve/softnorms_contract.py:228–236`; `Correlate.lean:444` |
| 7.3 | Python's own stratification text, if any | `InvalidInput: rights document is not stratified` | `Correlate.lean:445` |
| multi-fault inputs | Python's first fault: the block's semantics before any unit, a unit's lines after the limits and limitations | the table's first fault: Lean's order | 2.3 |
| every other check, and 6.4a to 6.4h, 6.4j, 6.5b, 6.5i, 6.7 | the contract's text | the same | the texts agree |

The included soft checks change as the pilot's switch changed them (S4 spec section 6), on the stripped
environment. Lean's rows do not change (4.3). Rust: no column. **Allowed Lean route differences** (D2): none from
reading, the record's texts being the route's own, except 4.3c's inherited texts, which are not compared.

**`reports@0`.** Python's message at the call sites:

| Check | Today | After the switch | Read from |
|---|---|---|---|
| 1.1, 1.12, 1.13 | `Incorrect fields (missing=[…], unknown=[…])` | `InvalidInput: invalid environment envelope`, `InvalidInput: invalid vocabulary`, `InvalidInput: invalid reports block` | `ve/wire.py:108`; `ve/environment.py:327, 362, 532` |
| 1.7 to 1.9 | `reports@0 with norms@0 layers` (Python checks `norms@0` first) | the same text with the class prefix, Lean's order (`data@0` first) | `ve/profiles.py:85–88`; `Content.lean:607` |
| 1.17 | `InvalidInput: author predicate begins with reports__` | `InvalidInput: author predicate <p> begins with reports__` | `ve/environment.py:546`; `Wire.lean:65` |
| 1.21, 1.22 | `holder sort` (`UnknownSymbol`) | `InvalidInput: holders must be 1 to 8 distinct sorts` (a class difference, counted), `UnknownSymbol: holder sort <s>` | `:534–536`; `Wire.lean:77–80` |
| 1.23 | `evidence sort` | `UnknownSymbol: evidence sort` | `:537–538`; `:81` |
| 2.3 to 2.6, 2.11 | `InvalidInput: report unit`; `unit spans must be sorted and non-overlapping` | `invalid unit id <id>`, `invalid span`, `duplicate unit id` | `ve/reports.py:177–183`; `Wire.lean:330–335, 386` |
| 2.7d | `UnknownAssessment: <record>` (Python tests the judgment and the record together) | `InvalidInput: unknown judgment <j>` | `ve/reports.py:541–542`; `Wire.lean:130` |
| 2.14b, 2.17c | `InvalidInput: contexts record`, `InvalidInput: assessments record` | `InvalidInput: invalid context id <c>`, `InvalidInput: invalid assessment id <a>` | `ve/reports.py:107–108`; `Wire.lean:211, 231` |
| 2.14d, 2.14e | `InvalidInput: context <c>` | `InvalidInput: invalid reference time for <c>`, `InvalidInput: context <c> description` | `:139–144`; `:218, 222` |
| 2.19b, 2.20b | `InvalidInput: bridge path` | `InvalidInput: bridge path <p>` | `:401`; `:256, 267` |
| 3.1g, 3.1n | the P0 checker's own texts (`TypeMismatch: …`, `UnboundVariable: …`) | `OpenComplement: assessment <a> criteria`, `OpenComplement: <unit>` | `:163, 483`; `Wire.lean:433, 448` |
| 3.1h | `ResourceLimit: content depth` | not reachable in the domain (unreached) | 2.4 |
| multi-fault inputs | Python's first fault: contexts and assessments before units, a report's holder, act and context while decoding | the table's first fault: units first, then the front matter, then `firstFailure`'s order | 2.4 |
| every other check | the contract's text | the same | the texts agree, including `KindMismatch`, `UnsupportedAct`, `UnknownHolder`, `HolderSort`, `UnknownContext`, `ScopedTarget`, `ScopedEnvironment`, `BridgeTarget`, `BridgeKindMismatch`, `DuplicateDeclaration: context <c>` and the metadata texts |

**Allowed Lean route differences** (D2): 1.1, 1.12, 1.13, 2.1, 2.2, 2.3, 2.9, 2.13, 2.16, and the shape members
2.7a, 2.14a, 2.17b, 2.19a, 2.20a, on the inputs where the route prints a JSON-library text (`fields do not match:
…`, `String expected`, `array expected`, `Natural number expected`); 2.7b on `fence` content (`UnsupportedProfile:
fence content is not decoded by the Lean reports route`). On every other check and input the route's text is
the record's. Rust's gate texts do not change (no Rust engine).

**`ve-units@1`.** Python's message at the call sites:

| Check | Today | After the switch | Read from |
|---|---|---|---|
| 1.1, 5.2, 5.4, 5.15a, 5.18a, 5.25a, 5.30b, 5.34a, S.a | `Incorrect fields (missing=[…], unknown=[…])` | `InvalidInput: invalid environment envelope`, `… invalid document fields`, `… invalid unit fields`, `… invalid lemma fields`, `… invalid leaf fields`, `… invalid reading set fields`, `… invalid graph fields`, `… invalid node fields`, `… invalid quantity fields` | `ve/wire.py:108`; `ve/quantity_admission.py:52, 70, 84, 125, 141, 268, 288`; `ve/units.py:510` |
| 2.5, 2.12, 2.13, 2.18, 2.23 | `fields do not match: expected [scale, display], got […]`, `fields do not match: required [kind, currency], optional [input_symbol], got […]` | `InvalidInput: invalid unit record`, `InvalidInput: invalid display fields for <tag>` | `ve/units.py:63–71, 99, 106, 108, 115, 120` |
| 2.4 | `Invalid unit tag "<tag>"` (Lean's `String.quote`) | `Invalid unit tag "<tag>"` as compact JSON; the two differ on a tag with a control character or a quote, which the class refuses anyway | `ve/units.py:44–48, 98` |
| 2.17c, 2.20c, 4.3c | `Display string "<s>" must be whitespace-normalized` (`String.quote`) | the same with compact JSON quoting; differs on control characters (`\x1c` against `\u001c`) | `:146, 165` |
| 2.27a, 2.27b | `DisplayCollision("EUR " touches the amount)`, `DisplayCollision("EUR ", "EUR ")` | the same with compact JSON quoting; equal for ASCII affixes | `:207, 215` |
| S.j | `Invalid decimal literal '3,75'` (`repr`) | `Invalid decimal literal "3,75"` | `:262` |
| S.o1 | `Unknown constant 'k'` (`repr`) | `Unknown constant "k"` | `:381` |
| 3.2 to 3.9 on a vocabulary with an earlier base fault | the slot or constant unit text | the base decoder's text (the deviation of 2.5, phase 3) | `ve/environment.py:419–423, 499–505` |
| every other check | the contract's text | the same | the texts agree |

**Lean route differences, reported** (D2, not enforced for this unit): the field-list rows above (Lean: `fields
do not match: …`, `unknown or missing …`); 1.3 (`UnsupportedProfile: Unsupported specification revision` without
the value); 1.2 (`UnsupportedProfile: quantity route requires ve-units@1 on ve.core@0.2` for a wrong language);
2.6, 2.10, 2.14, 2.16, 2.19, 2.21, 3.5, 3.8, 5.5, 5.15b, 5.18b, 5.25b, 5.31, 5.34b, 5.36a (`String expected` and
`expected a string` are the same words in another order? no: Lean prints `String expected`, Python `expected a
string` at the document checks and `String expected` at the unit checks; the table keeps each Python text); 5.3,
5.7, 5.14, 5.17, 5.25e, 5.32, 5.36c (`expected an array` against Lean's `array expected`); 5.21, 5.36e (Lean
appends the reason: `Invalid quantity certificate: …`); S.k1, S.k2, S.o3, S.p (inherited); S.m on a Lean text
whose prefix the hook strips (equal after stripping); S.j and S.o1 (Lean's `String.quote` against compact JSON on
the same characters). Rust prints as before (no column).

Classes: none changes at any switch. For `ve-units@1` the exempt cases of 2.13 are counted; for `rights@0` and
`reports@0` `legacy_class_differences` is reported (2.13).

## 7. S8.0, the shadow, measurement and switch commits: files and gates

### 7.1 S8.0: the registration

One commit, before any contract. It changes tooling and tests only; nothing in `ve/` except the three new
contract modules' skeletons (registries without hooks) that `UNITS` names. After it, the pilot's and S5's
generated files, stored reports, gate numbers and English tables are byte-identical.

| Today (after S5.0) | After S8.0 |
|---|---|
| `tools/wire_contract.py` `UNITS` names three units | six: `rights@0` (`ve.rights_contract`, legacy `ve.rights_contract.legacy_validation`), `reports@0` (`ve.reports_contract`, its `legacy_validation`), `ve-units@1` (`ve.units_contract`, its `legacy_validation`); `unit_label` gives `Rights`, `Reports`, `VeUnits`; `unit_paths` gives `examples/rights@0/`, `docs/spec/rights-wire-table.md`, `Tables/Rights.lean`, `conformance/wire-contract/rights@0-catalogue.json`, and likewise `reports-wire-table.md`, `ve-units-wire-table.md`, `Tables/Reports.lean`, `Tables/Units.lean` (the label `VeUnits` would read oddly; the table module is `Tables/Units.lean` by one entry of a name table, R13) |
| `conformance/wire_contract_faults.py` `unit_module` dispatches to `wire_contract_faults_<name>` | `wire_contract_faults_rights.py`, `_reports.py`, `_ve_units.py`, each with the S5 shape (`Fault`, `LEAN_ROUTE`, `CASE_KIND`, `FEASIBILITY_OF`, `RECORDED_TESTS`, `GAP_APPLIES`, `UNREACHED`, `WHOLE_SOURCE_PARTNER`, `handler_reaching`, `class_exempt`, `own_text`, `call_outcome`, `call_problems`, the sources) |
| the gate's `CASE_KINDS` names three Lean binaries | six: `ve_rights_route`: `rights-elaborate`; `ve_reports_route`: `reports-elaborate`; `ve_quantity`: `document`; the allowed-gap table of a new unit is read from this file's 8.9 (`("**Allowed coverage gaps**", "## 9.")`) |
| the recorder wraps the S5 units' functions | also each new unit's `legacy_validation` and `public_rejection`, `ve.document._load_document` (recording the rights and reports sources it builds, when the environment lists the unit's profile), `ve.admission._admit_document_python` (recording a W6 source), `RightsEnvironment`, `RightsDocument`, `ReportsDocument` and `admit_quantity_document` built over an environment, and the three Lean binaries and `ve_diagnose` with a new unit; the corpus test's three tests are parametrised over six units, with the globs `tests/test_rights*`, `tests/test_report*`, `tests/test_units*`, `tests/test_w6a*`, `tests/test_w6b*` added |
| the pre-commit hook names the S5 paths | the paths of every unit, from the same table |
| `Diagnose.lean` lists five units | the three entries of 5.3 (in S8.1a to S8.3a, not in S8.0) |

### 7.2 Diff scope, per unit

Item 1 is, per unit, a shadow commit (S8.1a, S8.2a, S8.3a), a measurement commit (S8.1b, …) and a switch commit
(S8.1d, …), after S8.0 and after the commit of S8-pre where one is needed.

**The shadow commit** of a unit: `ve/wire_contract/<unit>.json`, `examples/<unit>/` (two examples: the base of
section 8 and an accepted second source), `limits.json` and `names.json` with their lock entries; the unit's
contract module (hooks, classifiers, view, adapter, `legacy_validation`, `REGISTRY`; no `public_rejection`
yet); `lean/VE/WireContract/Hooks/<Unit>.lean`, the generated `Tables/<Unit>.lean`, `Limits.lean`, `Names.lean`
and the regenerated earlier tables, with their inventory lines; `Diagnose.lean` (5.3); `docs/spec/<unit>-wire-
table.md`; `conformance/wire_contract_faults_<name>.py` and the stored reports of the unit (gate, golden,
catalogue, call snapshot); the manifest's `wire.diagnose` mode; `tools/layer_policy.py`; tests.

**The measurement commit** of a unit: the stored gate and delta reports regenerated over the whole corpus with
`public_diagnostic_changes`, `lean_route_changes` and `legacy_class_differences`; the gate enforces S8-pre, the
class rule (units) or the Lean route list (rights, reports) from here; tests (the fixtures G3, G6 and G8 of the
unit). No file of `ve/` or `lean/` changes.

**The switch commit** of a unit: the contract and the lock (2.11); its generated table and inventory line (and,
for a switch of the pilot, `Tables/Rights.lean` with its line); the contract module gains `public_rejection`;
the call sites (2.9); the gate's tier P and the rows of section 9 enforced at `public`; the stored reports at
revision `R`, the new `<unit>-switch.json`, and `<unit>-test-inputs.json` for the sources of 8.8; tests;
`tests/contract_input_recorder.py` if a wrapper is still missing; the import-scan test; the paragraph of 3.5 in
the unit's spec; this file's response section.

Not changed by any commit of item 1, and checked by the diff-scope test of C1: `ve/rights.py`,
`ve/rights_route.py`, `ve/reports.py`, `ve/reports_route.py`, `ve/units.py`, `ve/quantity_admission.py`,
`ve/environment.py`, `ve/softnorms.py`, `ve/errors.py`, `ve/wire.py`, `ve/ast.py`, `ve/wire_contract/engine.py`,
`contract.schema.json`, the pilot's and S5's contracts and examples, every Lean module other than the generated
tables, the three hooks modules and `Diagnose.lean`, `VE/Audit.lean`, `lean/axioms.txt`,
`tools/check_lean_imports.py`, `Main.lean`, every Rust file, `conformance/identity.json`, the frozen baseline.
`ve/document.py` and `ve/admission.py` change only by the handlers of 2.9. The commit of S8-pre is a different
commit, before the switch, with its own scope.

### 7.3 The gates

The four conservativity gates of base plan 5.2, as the debate amended them, for every commit of item 1:

- **C1.** The diff is within 7.2. `VEError.to_dict()` is not edited; `diagnostic` is set at three more call
  sites (six statements).
- **C2.** Legacy verdicts equal their snapshot. Each engine reports `clean` on every accepted corpus case of its
  unit and a fault on every rejected one, in Python and in Lean; Rust is not run. Python's deferred count is 0.
- **C3.** Public diagnostics change only as the signed delta of the unit lists; the gate fails otherwise. S8.0
  and the shadow and measurement commits change no public diagnostic.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass. The inventory diff is the
  additions and generated rehashes of 5.4 and the append-only `Diagnose.lean` diff of 5.3, and nothing else; no
  commit touches `VE/Audit.lean` unless the optional statements of 5.5 are added, and then by added lines only.

The corpus-completeness test is kept, with its three tests per unit (8.8). The pointer's `difffuzz` gate has no
object (plan section 1).

## 8. Acceptance fixtures for item 1

Deterministic, with expectations written by hand from section 2 and base spec sections 2 and 8, and every
number confirmed by an `#eval` of the scratch file (5.6) once it is run. Each reviewer derives the expectation
of every fixture before reading the column "Expected". A fixture of 8.1 to 8.3 is green when the Python engine
and `ve_diagnose` both return the expected outcome, as records compared by base spec 2.7, except that an
inherited record's `text` and `args` are each language's own. Every "exactly when" of section 2 and 3.1 has a
fixture in each direction, named below.

**The base B_R** (`rights@0`): the environment `env(ARREST)` of `tests/test_rights_lean.py:59–68` (sorts
`state`, `person`; the permission `arrest_permitted` with act `{0} arrest {1}` over `(state, person)`, the
base predicates `arbitrary_arrest` over `(state, person)` and `journalist` over `(person)`; profiles
`["norms@0", "relational-fol@0", "rights@0", "soft-norms@0"]`; the block `{"holders": ["person"], "bearers":
["state", "person"]}`), and the document:

```json
[{"source_units": ["u1", "u2"]},
 {"right": {"name": "r9", "holder": "person", "guard": ["top"],
            "lines": [{"kind": "claim", "norm": {"name": "no-arbitrary-arrest", "predicate": "arrest_permitted",
                       "sign": false, "guard": ["binary", "arbitrary_arrest", ["var", 1], ["var", 0]],
                       "unless": [], "over": []}}]}},
 {"limitation": {"name": "l29", "scope": "all", "kinds": "all", "decided_by": "unstated",
                 "conditions": [{"name": "determined_by_law", "role": "necessary", "decided_by": "unstated",
                                 "verbalisation": "the limitation is determined by law"}],
                 "factors": []}}]
```

"Unit *i*" is `/document/i`. The second example is the environment with the document `[]`.

**The base B_P** (`reports@0`): the environment `E0()` of `tests/test_reports_lean.py:57–73` (sorts
`organisation`, `text`, `system`, `model`, `evidence`; predicates `safe` over `system`, `helpful`,
`was_helpful`, `human` over `model`, `reviewed` over `system`, `publishes` over `(organisation, system)`;
constants `anthropic : organisation`, `the_article : text`, `the_team : organisation`, `service : system`,
`claude : model`, `e1 : evidence`; the block `{"holders": ["organisation", "text"], "evidence": "evidence"}`;
profiles `["relational-fol@0", "reports@0"]`), and the document:

```json
{"units": [{"id": "u1", "span": [0, 1], "kind": ["attributed", "the_article", "says", "asserted"],
            "meaning": "specified", "support": "testimony",
            "content": {"report": {"holder": "the_article", "act": "says", "context": "c2",
                                   "content": {"ast": ["unary", "safe", ["const", "service"]]}}}}],
 "contexts": [{"id": "c1", "tense": "present", "description": "the constitution"},
              {"id": "c2", "tense": "past", "reference_time": "sept16", "description": "the article of 16 September"},
              {"id": "c3", "tense": "present", "description": "the article"}],
 "assessments": [{"id": "a1", "context": "e1", "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
                  "factors": ["review status"], "precedents": [], "jurisdiction": "news_desk", "version": 1}]}
```

The second example is the environment with `{"units": [], "contexts": [], "assessments": []}`.

**The base B_Q** (`ve-units@1`): the environment `raw_environment()` of `tests/test_w6a_review_regressions.py:20–26`
with `profiles` `["documents@1", "order@0", "relational-fol@0", "time@0"]` (empty vocabulary; `units` `{"bp":
{"scale": "100", "display": {"kind": "percent"}}}`), and the document:

```json
{"units": [{"id": "u1", "span": [0, 15], "kind": "asserted", "content": Q}],
 "graph": {"root": "n1", "nodes": [{"name": "n1", "quantity": Q, "unit": "u1"}]}}
```

where **Q** is `{"format": "ve-quantity@1", "formula": ["lt", ["decimal", "bp", "3.75"], ["decimal", "bp",
"4.00"]]}`. "Statement *i*" is `/document/units/i/content`. The second example adds a unit `u2` with span `[15,
30]`, kind `exposition` and no content. The **balanced conjunction** of `n` formulas is as the S5 spec defines
it (over `n` `top`s it has `2n − 1` nodes); a **`not` chain** of `k` around `top` has depth `k + 1`.

### 8.1 The engine on `rights@0`

| Case | Change to B_R | Expected `check`, `path`, `text` |
|---|---|---|
| R1 | none; and the second example | clean; both legacy validators accept |
| R2 | `rights@0` removed from `profiles` | 1.2, `/environment/profiles`, `UnsupportedProfile: rights@0 is required` |
| R3 | `soft-norms@0` removed from `profiles` | 1.3, `/environment/profiles`, `UnsupportedProfile: rights@0 requires soft-norms@0` |
| R4 | `norms@0` removed from `profiles` | 1.4, `/environment/profiles`, `UnsupportedProfile: rights@0 requires norms@0` |
| R5 | the block lacks `bearers` | 2.2, `/environment/vocabulary/rights`, `InvalidInput: invalid rights block` |
| R6 | `holders` is `"person"` | 2.3, `/environment/vocabulary/rights/holders`, the same text |
| R7 | the block gains `"alters": {"arrest_permitted": {"holder_slot": 1}}` | 2.7a, `/environment/vocabulary/rights/alters/arrest_permitted`, `InvalidInput: alters arrest_permitted` |
| R8 | a copy of unit 1 appended (a second right `r9`) | 6.3b, `/document`, `DuplicateDeclaration: right r9`; `args` `value` `r9` |
| R9 | the vocabulary gains `"soft": {"parties": ["p", "Q!"], "outranking": {"mode": "strict"}}` | `soft/2.7a`, `/environment`, `InvalidInput: invalid soft name Q!`; `args` `value` `Q!`, `inner_path` `/environment/vocabulary/soft/parties/1`; phase `soft` |
| R10 | the document is `{"right": {}}` | 4.1, `/document`, `InvalidInput: document must be an array`; Python's legacy class is `ResourceLimit` (a class difference, counted) |
| R11 | 1,022 copies of unit 1 appended (1,025 units) | 4.2, `/document`, `ResourceLimit: units`; `args` `count` `1025`, `limit` `1024` |
| R12 | unit 1's right lacks `holder` | 4.3c, `/document/1`, class `InvalidInput`; text each language's own |
| R13 | unit 1's line has `kind` `"duty"` | 4.3d, `/document/1`, `InvalidInput: invalid line kind` |
| R14 | unit 1's line gains `"cites": {"guard": []}` | 4.3g, `/document/1`, `InvalidInput: cites guard must list unit ids`; `args` `key` `guard` |
| R15 | a unit `{"right_lines": {"right": "r18", "lines": []}}` appended | 4.3h, `/document/3`, `UnknownRight: r18` |
| R16 | unit 2's `kinds` is `"some"` | 4.3i, `/document/2`, `InvalidInput: invalid kinds of limitation l29` |
| R17 | a unit `{"bar": {"name": "b30", "reading": "maybe", "decided_by": "unstated"}}` appended | 4.3m, `/document/3`, `InvalidInput: invalid bar reading for b30` |
| R18 | a unit `{"limit": {}}` appended | 4.3o, `/document/3`, `InvalidInput: invalid rights document unit` |
| R19 | `holders` is `[]` | 5.1a, `/environment/vocabulary/rights`, `InvalidInput: invalid rights block` |
| R20 | `holders` is `["person", "robot"]` | 5.1b, `/environment/vocabulary/rights`, `UnknownSymbol: sort robot` |
| R21 | `bearers` is `["state", "state"]` | 5.1d, `/environment/vocabulary/rights`, `DuplicateDeclaration: bearer state` |
| R22 | the block gains `"protected": ["arrest_permitted"]` | 5.1e, `/environment/vocabulary/rights`, `InvalidInput: protected arrest_permitted` |
| R23 | 128 more rights `r1` to `r128`, each unit 1's body renamed | 6.1, `/document`, `ResourceLimit: rights`; `args` `count` `129`, `limit` `128` |
| R24 | unit 1's right renamed `rights-r9` | 6.3a, `/document`, `InvalidInput: name rights-r9 begins with rights-` |
| R25 | the vocabulary gains a permission `rights__permitted` (act `{0} permit {1}`, over `(state, person)`) | 6.3f, `/document`, `InvalidInput: author predicate rights__permitted begins with rights__` |
| R26 | unit 1's line norm gains `"over": ["rights-fan-1"]` | 6.3g, `/document`, `UnknownSymbol: rule rights-fan-1` |
| R27 | unit 1's `holder` is `"state"` | 6.4a, `/document`, `UnknownSymbol: sort state` |
| R28 | unit 1's `guard` is `["unary", "journalist", ["var", 1]]` | 6.4d, `/document`, class `UnboundVariable`; text each language's own |
| R29 | unit 1's line norm has `"sign": true` | 6.4f, `/document`, `IncidentShape: no-arbitrary-arrest on right r9`; `args` `detail` |
| R30 | unit 1's `lines` is `[]` | 6.4j, `/document`, `RightWithoutIncident: r9` |
| R31 | unit 2's `scope` is `["r18"]` | 6.5b, `/document`, `UnknownRight: r18` |
| R32 | unit 2 has nine conditions `c1` to `c9` | 6.5d, `/document`, `ResourceLimit: conditions` |
| R33 | unit 2's `decided_by` is `""` | 6.5h, `/document`, `InvalidInput: invalid decider for limitation l29` |
| R34 | two bar units `b30` and `b31` appended | 6.6a, `/document`, `DuplicateDeclaration: bar` |
| R35 | unit 1's line gains `"cites": {"guard": ["u9"]}` | 6.7, `/document`, `UnknownSymbol: unit u9` |
| R36 | unit 1's line norm gains `"mode": "default"` with the exception `{"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}`, and a second line (claim, norm `strict-one` on `arrest_permitted`, sign false, guard `["top"]`) is added before it; the default norm's `over` is `["strict-one"]` | 7.1e, `/document`, `SoftOverHard: rule no-arbitrary-arrest over strict-one`; `args` `detail` |
| R37 | R10 with R3 | 1.3, `/environment/profiles` (phase 1 before phase 4) |
| R38 | R19 with R13 | 4.3d, `/document/1` (phase 4 before phase 5: Lean decodes every unit before `checkBlock`; Python today reports the block) |
| R39 | R20 with R24 | 5.1b, `/environment/vocabulary/rights` (phase 5 before phase 6) |
| R40 | R9 with R12 | `soft/2.7a`, `/environment` (phase 3 before phase 4) |
| R41 | unit 1's right renamed `R9` | clean in both engines; Python's legacy validator rejects (`InvalidInput: invalid rights name 'R9'`) and the Lean route accepts: a listed legacy verdict difference (2.13), the only case where "a fault exactly when the validator rejects" is expected to fail until S8-pre |
| R42 | unit 1's right lacks `guard` | clean in both engines; Python rejects (`InvalidInput: right`), Lean accepts (`guard` optional): a legacy verdict difference (2.13) |

R30 and R1 are the two directions of 6.4j ("every right has at least one line"); R19 and R1 of 5.1a; R35 and
B_R's own `cites`-free line of 6.7. For every case from R2 to R40, the record's `class` equals the Lean class
of the Lean route's text (2.13), and both legacy validators reject.

### 8.2 The engine on `reports@0`

| Case | Change to B_P | Expected `check`, `path`, `text` |
|---|---|---|
| P1 | none; and the second example | clean; both legacy validators accept |
| P2 | `profiles` `["relational-fol@0"]` and the block removed | 1.5, `/environment/profiles`, `UnsupportedProfile: reports@0 is required` |
| P3 | `profiles` `["norms@0", "relational-fol@0", "reports@0"]` | 1.9, `/environment/profiles`, `UnsupportedProfile: reports@0 with norms@0 layers` |
| P4 | the vocabulary lacks `reports` | 1.11b, `/environment/vocabulary`, `UnsupportedProfile: reports@0 needs a reports block` |
| P5 | `holders` has nine members (`organisation`, `text` and seven more names) | 1.21, `/environment/vocabulary/reports/holders`, `InvalidInput: holders must be 1 to 8 distinct sorts`; Python's legacy class is `UnknownSymbol` (counted) |
| P6 | `holders` is `["organisation", "robot"]` | 1.22, `/environment/vocabulary/reports/holders/1`, `UnknownSymbol: holder sort robot` |
| P7 | `evidence` is `"proof"` | 1.23, `/environment/vocabulary/reports/evidence`, `UnknownSymbol: evidence sort` |
| P8 | `anthropic` gains `"verbalisation": "The Stated Assessment"` | 1.24, `/environment/vocabulary/constants`, `InvalidInput: holder verbalisation reserved` |
| P9 | `u1`'s report holder is `claude` and its kind names `claude` | 3.1j, `/document`, `HolderSort: claude is not of a holder sort`; `args` `holder` `claude` |
| P10 | `u1`'s report holder is `nobody` and its kind names `nobody` | 3.1i, `/document`, `UnknownHolder: nobody` |
| P11 | `u1`'s report context is `c9` | 3.1k, `/document`, `UnknownContext: c9` |
| P12 | `u1`'s report act is `promised` and its kind names `promised` | 2.7c, `/document/units/0`, `UnsupportedAct: promised (reports@0 admits says, believes, wants, intends)` |
| P13 | `u1`'s id is `"u 1"` | 2.4, `/document/units/0/id`, `invalid unit id u 1` |
| P14 | `u1`'s span is `[5, 2]` | 2.6, `/document/units/0/span`, `invalid span` |
| P15 | 254 more contexts `c4` to `c257`, each as `c1` renamed | 2.15, `/document/contexts`, `ResourceLimit: contexts`; `args` `count` `257`, `limit` `256` |
| P16 | `c1`'s tense is `"future"` | 2.14c, `/document/contexts/0`, `ContextTense: c1` |
| P17 | `c1`'s description is 201 `a`s | 2.14f, `/document/contexts/0`, `ResourceLimit: context description` |
| P18 | `a1` lacks `decided_by` | 2.17a, `/document/assessments/0`, `InvalidInput: assessment a1 needs decided_by` |
| P19 | `a1`'s context is `anthropic` | 3.1e, `/document`, `UnknownSymbol: evidence context anthropic` |
| P20 | `u1`'s content is `{"assessment": {"judgment": "may", "record": "a9", "content": {"ast": …}}}`, kind `["hedged", "could", "asserted"]`, meaning `{"open": ["reports__may__1"]}` | 3.1l, `/document`, `UnknownAssessment: a9` |
| P21 | `u1`'s content is `{"negated": {"ast": ["unary", "safe", ["const", "service"]]}}`, kind `asserted` | 2.7g, `/document/units/0`, `InvalidInput: negated operand in u1` |
| P22 | `u1`'s kind is `["attributed", "anthropic", "says", "asserted"]` | 2.7i, `/document/units/0`, `KindMismatch: u1` |
| P23 | `u1`'s support is `"rumour"` | 3.1u, `/document`, `InvalidInput: support of u1` |
| P24 | `u1`'s meaning is `{"open": ["zz"]}` | 3.1w, `/document`, `InvalidInput: meaning of u1` |
| P25 | `bridges` is `[{"id": "b1", "unit": "u1", "path": "2", "accepted_by": "ann", "reason": []}]` | 2.19b, `/document/bridges/0`, `InvalidInput: bridge path 2` |
| P26 | `bridges` is `[{"id": "b1", "unit": "u7", "accepted_by": "ann", "reason": ["u1"]}]` | 3.1s, `/document`, `BridgeTarget: u7` |
| P27 | `scoped` is `[{"id": "s1", "payloads": ["u1"], "conclusion": {"ast": ["unary", "safe", ["const", "service"]]}}]` | 3.1q, `/document`, `ScopedTarget: s1` (`u1`'s root complement is a report node) |
| P28 | P27's check with `"envelope": {}` and no `certificate` | 2.20d, `/document/scoped/0`, `InvalidInput: envelope without a certificate on scoped check s1` |
| P29 | a second context `c1` | 3.1a, `/document`, `DuplicateDeclaration: context c1` |
| P30 | P16 with P10 | 2.14c, `/document/contexts/0` (phase 2 before phase 3) |
| P31 | P29 with P13 | 2.4, `/document/units/0/id` (units before the front matter; Python today reports the duplicate context) |
| P32 | P9 with P19 | 3.1e, `/document` (the assessments before the nodes inside `firstFailure`) |
| P33 | P12 with P11 | 2.7c, `/document/units/0` (the decoder before `WellFormedReports`) |
| P34 | `u1`'s kind is `"bogus"` | outside the domain: both adapters refuse the case (`UnsupportedProfile: the case is outside the unit's domain`); `legacy_validation` is not compared |
| P35 | `u1`'s content is `{"assessment": {"judgment": "may", "record": "a1", "content": {"ast": …}}}`, kind `["hedged", "could", "asserted"]`, meaning `"specified"` | 3.1w, `/document`, `InvalidInput: meaning of u1` |
| P36 | P35 with meaning `{"open": ["reports__may__1"]}` | clean; both accept |
| P37 | `u1` as in B_P with meaning `{"open": ["t"]}` and `"open_terms": ["t"]` | clean; both accept (an `open` meaning on a unit without assessment nodes is allowed) |

P35, P36 and P37 are the directions of 3.1w: a `specified` report unit has no assessment node (P35 fails, P1
holds); a unit with assessment nodes is `open` listing their names (P36); `open` is allowed without them (P37).
For every case from P2 to P33 and P35, the record's `class` equals the Lean class of the route's text.

### 8.3 The engine on `ve-units@1`

| Case | Change to B_Q | Expected `check`, `path`, `text` |
|---|---|---|
| Q1 | none; and the second example | clean; both legacy validators accept |
| Q2 | `profiles` `["documents@1", "relational-fol@0", "time@0"]` | 1.4, `/environment/profiles`, `UnsupportedProfile: ve-units@1 requires exactly order@0, relational-fol@0 and time@0, optionally with documents@1` |
| Q3 | `unit_schema` `"ve-units@2"` | 2.1, `/environment/unit_schema`, `UnsupportedProfile: Unsupported unit schema` |
| Q4 | 65 tags `t1` to `t65`, each `{"scale": "1", "display": {"kind": "decimal", "label": "t<i>"}}` | 2.3, `/environment/units`, `ResourceLimit: At most 64 unit tags`; `args` `count` `65`, `limit` `64` |
| Q4′ | `bp` renamed to 100 `a`s | 2.4, `/environment/units/aaa…a` (100 `a`s), `Invalid unit tag "aaa…a...`: a quote, 79 `a`s and `...` (the `json` renderer's 80-byte cut; 5.6) |
| Q5 | `bp`'s scale `"7"` | 2.7d, `/environment/units/bp/scale`, `UnitScale(bp): expected a positive power of ten` |
| Q5′ | scale `"0100"` | 2.7c, the same path, `non-canonical integer` |
| Q5″ | scale of 41 `1`s | 2.7a, the same path, `ResourceLimit: numeral length` |
| Q6 | `units` `{"eur": money EUR, "usd": money USD with input_symbol "EUR "}` | 2.27b, `/environment/units`, `DisplayCollision("EUR ", "EUR ")`; `args` `a`, `b` both `EUR ` |
| Q6′ | `units` `{"bp": percent, "pct": {"scale": "1", "display": {"kind": "decimal", "label": "%"}}}` | 2.27b, `/environment/units`, `DisplayCollision("%", " %")` |
| Q7 | the vocabulary gains a predicate `p` over `["$int"]` with `"argument_units": {"1": "bp"}` | 3.3, `/environment/vocabulary/predicates/p/argument_units/1`, `Invalid argument unit slot 1` |
| Q7′ | a sort `item` and a predicate `q` over `["item"]` with `"argument_units": {"0": "bp"}` | 3.4, `/environment/vocabulary/predicates/q/argument_units/0`, `Unit on non-integer slot 0` |
| Q7″ | `p` with `"argument_units": {"0": "zz"}` | 3.6, `/environment/vocabulary/predicates/p/argument_units/0`, `UnknownUnit(zz)` |
| Q8 | statement 0's formula is the balanced conjunction of 5,001 `top`s (10,001 array nodes) | 5.10e, `/document/units/0/content`, `ResourceLimit: Quantity AST exceeds node or depth limit` |
| Q8′ | statement 0's formula is a `not` chain of 65 | 5.10e, the same |
| Q9 | statement 0's formula is `["eq", ["num", "bp", "375"], ["num", "0"]]` | 5.10m, `/document/units/0/content`, `UnitMismatch(bp,dimensionless)`; `args` `message` |
| Q10 | `units` gain `"day": {"scale": "1", "display": {"kind": "iso_date"}}`; statement 0 is `["eq", ["date", "2100-02-29"], ["num", "day", "0"]]` | 5.10h, `/document/units/0/content`, `InvalidDate(2100-02-29)` |
| Q11 | as Q10 with `"1969-12-31"` | 5.10i, the same path, `DateRange(1969-12-31)` |
| Q12 | as Q10 with `"09/10/2026"` | 5.10h, the same path, `InvalidDate(09/10/2026)` |
| Q13 | statement 0 is `["eq", ["decimal", "bp", "3.755"], ["num", "bp", "375"]]` | 5.10g, the same path, `UnitPrecision(bp, scale=100)`; `args` `tag` `bp`, `scale` `100` |
| Q14 | `["eq", ["decimal", "bp", "3,75"], ["num", "bp", "375"]]` | 5.10j, the same path, `Invalid decimal literal "3,75"` |
| Q15 | `["eq", ["num", "zz", "1"], ["num", "zz", "2"]]` | 5.10f, the same path, `UnknownUnit(zz)` |
| Q16 | `["eq", ["const", "k"], ["num", "375"]]` | 5.10o1, the same path, `Unknown constant "k"` |
| Q17 | `["forall", "$int", ["top"]]` | 5.10n, the same path, `$int quantification requires the missing numbers2 route` |
| Q18 | `["unary", "p", ["num", "1"], ["num", "2"]]` with `p` over `["$int"]` | 5.10p, the same path, class `InvalidInput`; text each language's own |
| Q19 | Q with `"Q": ["top", false]` and formula `["top"]` | 5.10q, the same path, `Quantity Q differs from regenerated formula` |
| Q20 | Q with `"format": "ve-quantity@2"` | 5.10b, the same path, `Unsupported quantity format` |
| Q21 | the graph's `nodes` is `[]` | 5.38, `/document/graph`, `graph rejected: cycle, duplicate name, dangling premise, ill-typed claim or invalid certificate` |
| Q22 | the node has `"label": "open:t"` and no `unit` | 5.37b, `/document/graph/nodes`, `AdmissionError: node n1 is not admitted under label open:t`; `args` `name`, `label` |
| Q23 | the vocabulary gains `p` over `["$int"]` with `"argument_units": {"1": "bp"}` and `q` over `["ghost"]` | 3.1, `/environment/vocabulary`, class `InvalidInput`; text each language's own (the deviation of 2.5: Python today reports `Invalid argument unit slot 1`) |
| Q24 | Q4 with Q13 | 2.3, `/environment/units` (phase 2 before phase 5) |
| Q25 | Q15 with Q21 | 5.10f, `/document/units/0/content` (the units before the graph) |
| Q26 | statement 0 is `["lt", ["decimal", "bp", "3,75"], ["num", "zz", "1"]]` | 5.10j (the left term before the right) |
| Q27 | a unit `u2` with span `[10, 20]` and no content appended | 5.13, `/document/units`, `unit spans must be sorted and non-overlapping` |
| Q28 | `lemmas` `[{"name": "b/l", "conclusion": Q, "leaves": [{"quantity": Q, "label": "cite:b/m"}], "certificate": C}]` with `C` any object of the shape of 5.21 | 5.18d, `/document/lemmas/0/leaves/0`, `AdmissionError: lemma leaves must be transitive (no cite labels)` |
| Q29 | the case carries `quantity` instead of `document` | outside the domain: both adapters refuse the case |
| Q30 | statement 0 is `["eq", ["decimal", "bp", "-0.25"], ["num", "bp", "-25"]]` | clean; both accept |
| Q31 | `units` `{"bp": percent, "usd": money USD}` | clean; both accept |

Q13 and Q30 (with Q1) are the two directions of S.g ("a decimal lies on its tag's grid"); Q6 and Q31 of 2.27;
Q21 and Q1 of 5.38. For every case from Q2 to Q28, the record's `class` equals the code the legacy validator
reports in Python, except on the exempt cases Q18, Q22 and Q23 (2.13), and both legacy validators reject.

### 8.4 The boundary and the call sites

**T_R(D)** is the `ve-document@1` text whose front matter is `{"format": "ve-document@1", "environment": E,
"units": […]}` with one unit per content of `D` after its `source_units` element, ids `u1`, `u2`, …, kind the
content's tag, meaning `specified`, support `none`, spans partitioning the source `Unit 1.\nUnit 2.\n…`, as
`conformance/rights_differential.py:211–229` builds it; its `source_units` is then `["u1", "u2", …]`. **T_P(D)**
is the same for a reports document, with each unit's `kind`, `meaning` and `support` as in `D` and the
document's `contexts`, `assessments`, `bridges`, `scoped`, `open_terms` as front-matter members. "The call" is
`ve.document.load_document` on the text for rights and reports, and `ve.admission.admit_document(environment,
document)` under the Python authority for units. All records have the unit's `contract` and `"revision": R`.

| Case | Input | Expected |
|---|---|---|
| S1 | the call on T_R(R8's document) | raises a `DuplicateDeclaration` whose `to_dict()` is the first object of 4.1 |
| S2 | the call on T_R(B_R) with R9's soft block | raises a `VEError` whose `to_dict()` is the second object of 4.1; the raising statement is `_environment` (`:365`) |
| S3 | the call on T_R(B_R) with R3's profiles | `code` `UnsupportedProfile`; record 1.3; the raising statement is `_environment` |
| S4 | for each of S1 to S3: the legacy error `e` from `legacy_validation` on the same source | the raised error has `e`'s type and `e`'s `code`; `str` of it, its `message` and its record's `text` are equal |
| S5 | the call on T_R(B_R) (accepted), in a subprocess started without the recorder plugin, with the Lean routes available | the document loads as today; afterwards none of the three contract modules and not `ve.wire_contract` is in `sys.modules` |
| S6 | `ve.rights_contract.public_rejection` on B_R (accepted) with a hand-made `VEError("legacy says no")` | returns the same object; `message` is `legacy says no`; `diagnostic` is the residual record: `check` and `phase` `residual`, code `RIGHTS_INVALID_INPUT`, class `InvalidInput`, path `""`, text `legacy says no`, args `{}` |
| S7 | `public_rejection` on R35's source and legacy error, with a registry lacking `citations_declared` | `diagnostic` is `{"contract": "rights@0", "revision": R, "deferred": "6.7", "text": "UnknownSymbol: unit u9"}`; the message is unchanged |
| S8 | as S7, with a registry whose `rights_names` raises `KeyError` | returns `e` unchanged: `diagnostic` is `None` |
| S9 | `public_rejection` on S1's source and error, with the contract of the shadow revision | returns the error unchanged |
| S10 | `public_rejection` twice on S1's source and error | the second call changes nothing |
| S11 | `public_rejection` on S1's source and error | the two arguments are equal, after the call, to deep copies taken before it |
| S12 | the syntax-tree scan of 2.9 on the tree; and on each of four changed trees: (a) `ve/readings.py` gains `from .rights_contract import legacy_validation`; (b) `_load_document` gains a third call of `ve.rights_contract.public_rejection`; (c) a call is bound to a name and the name raised; (d) `ve/admission.py` imports `ve.reports_contract` | passes; fails on each of (a) to (d) |
| S13 | the call on T_P(P9's document) | raises a `VEError` whose `to_dict()` is the third object of 4.1 |
| S14 | the call on T_P(B_P) with P5's holders | raises an `UnknownSymbol` (Python's class) whose `diagnostic` is the record of 1.21 with class `InvalidInput`: `code` and `class` differ (2.13) |
| S15 | the call on T_P(B_P) with `u1`'s kind `"bogus"` | raises the loader's own error (`unknown kind bogus`) before `ReportsDocument`: `diagnostic` is `None` and the message is today's |
| S16 | the call on B_Q's environment and Q13's document | raises a `VEError` whose `to_dict()` is the fourth object of 4.1 |
| S17 | the call on Q4's environment and B_Q's document | raises a `ResourceLimit` from the `Environment` statement (`:503`) with the record of 2.3 |
| S18 | the call on B_Q's environment without `unit_schema` and `units`, and its document | raises from the W2 admission path, as today: `diagnostic` is `None` |
| S19 | `ve document check` on a text whose unit statement is Q14's | raises from the loader's own elaboration (`ve/document.py:142`), as today: `diagnostic` is `None` |
| S20 | `ve.units_contract.public_rejection` on Q2's source and its legacy error, with a registry lacking `w6_profiles` | `diagnostic` is `{"contract": "ve-units@1", "revision": R, "deferred": "1.4", "text": …}` with the legacy text |
| S21 | `ve.reports_contract.public_rejection` on B_P (accepted) with a hand-made `VEError("x")`; `ve.units_contract.public_rejection` on B_Q with the same | the residual records of `reports@0` and `ve-units@1` |
| S22 | `RightsDocument(RightsEnvironment(B_R.environment), R8's document)`; `ReportsDocument` on P9's; `admit_quantity_document` on Q13's | each raises an error whose `diagnostic` is `None` and whose message is the legacy text |

### 8.5 The delta and the gate

Tier **P** runs, per unit, only when the contract's `status` is `public`: for every corpus case that Python's
legacy validator rejects with an error `e`, `public_rejection(environment, document, e′)` on a fresh error `e′`
of the same source, and the call of 8.4. The function is checked on every rejected case. The call carries the
record only on the handler-reaching cases (2.12); on the others it must raise today's error.

| Case | Input | Expected |
|---|---|---|
| G1 | tier P, every case, the function | the returned error's `diagnostic` equals the reported record of 2.12, computed apart; its `message` is that record's `text`; its type and `code` are `e`'s |
| G2 | tier P, every handler-reaching case, the call | raises; `to_dict()` equals `e`'s `to_dict()` with `message` replaced by the record's `text` and `diagnostic` added |
| G3 | the gate of a unit at its measurement commit, in shadow | the sum of text changes over checks that are not inherited is `text_delta_count`; `public_diagnostic_changes` lists each check of section 6 that has a case, and any check beyond section 6 is reported, not dropped; `lean_route_changes` and `legacy_class_differences` are present; the gate exits 0 unless S8-pre, the class rule (units) or the Lean route list (rights, reports) fails |
| G4 | at `public`, the signing file without the entry of 6.3b (`rights@0`), 1.21 (`reports@0`) or S.j (`ve-units@1`) | the gate fails with the first line of S4 spec 4.4 |
| G5 | at `public`, the signing file with an entry `6.7`, `3.1k` or `5.13` | the gate fails with the second line |
| G6 | the gate's measurement of `ve-units@1` with Python's legacy class on Q15's class of inputs replaced, in the test only, by `UnknownSymbol` | fails with `public delta: <n> class differences` |
| G7 | the gate with the Lean verdict of the candidates of 2.13 replaced, in the test only, by `ok` where Python rejects | fails with `legacy verdict differences` naming them |
| G8 | the delta report after a contract text is edited, without regeneration | `conformance/wire_contract_delta.py --unit <unit> --check` fails |
| G9 | the gate after S8-pre and the switch, per unit | exits 0: every row of section 9 holds |
| G10 | the gate of `rights@0` | the included checks of gaps G2 and G3 of 8.9 have no first-fault witness and the gate passes; any other included check without one fails |
| G11 | the pilot's and S5's gates after S8.0 | the stored reports, deltas, golden and catalogue files and English tables are byte-identical to the S5 branch's |
| G12 | tier P, every rejected case that is not handler-reaching, the call | raises an error with no record: `diagnostic` is `None`, and its type, `code` and message are those of the snapshot before the switch commit (Z8) |
| G13 | the gate of `rights@0` or `reports@0` with the Lean route's text on R29's or P9's class of inputs replaced, in the test only, by another text | fails with `lean route differs on 6.4f …` or `… 3.1j …` |
| G14 | the gate with Python's legacy validator replaced, in the test only, by one that raises `TypeError` on R10's input | fails with `legacy crashes` naming it |
| G15 | the gate of `rights@0` | `viewed records` reports the number of records with `path` `/environment` and an `inner_path`, at least R9's |

### 8.6 Conservativity

- **Z1.** The full existing suite, the conformance reports, `conformance/identity.json`, the frozen baseline and
  every frozen hash are unchanged by each commit of item 1, except the files of 7.2. Every stored expectation of
  a Python error's text that a switch commit changes is listed in it.
- **Z2.** `VEError("x").to_dict()` is `{"code": "InvalidInput", "message": "x"}`, as today.
- **Z3.** Every row of `ve_rights_route`, `ve_reports_route` and `ve_quantity`, on every corpus case that Lean
  reads, is byte-identical to the snapshot before each commit.
- **Z4.** On every corpus case, Python's legacy validator gives the verdict, code and text of the snapshot before
  the commit. (A commit of S8-pre has its own snapshot rule, 2.13.)
- **Z5.** On every corpus case, the environment and the document are equal, after `legacy_validation` returned or
  raised, to deep copies taken before it (V3 of 2.9).
- **Z6.** `frozen.py` passes; the inventory diff is as C4 says.
- **Z7.** After S8.0, the pilot's and S5's outputs are byte-identical (G11).
- **Z8.** On every rejected corpus case that is not handler-reaching (2.12), the call raises the error of the
  snapshot before the commit: same type, `code` and message, and no `diagnostic`.
- **Z9.** Every Rust output of the conformance suites is byte-identical before and after every commit of item 1.

### 8.7 Lean and tooling

| Case | Input | Expected |
|---|---|---|
| L1 | `ve_diagnose rights@0` on S1's source as a `rights-elaborate` case | `{"id": …, "status": "ok", "outcome": "fault", "diagnostic": r}` with `r` the record of 4.1's first object |
| L2 | `ve_diagnose reports@0` on P9's source as a `reports-elaborate` case | the record of 4.1's third object |
| L3 | `ve_diagnose ve-units@1` on Q13's source as a `document` case | the record of 4.1's fourth object |
| L4 | `ve_diagnose rights@0` on an `admission` case whose document is T_R(R8's document)'s front matter | the same record as L1 (the adapter runs `splitDocument`) |
| L5 | `ve_diagnose <unit>` on every corpus case that Lean reads, before and after the unit's switch commit | the rows are equal once the old `revision` is read as `R` |
| L6 | `ve_diagnose reports@0` on P34's case; `ve_diagnose ve-units@1` on Q29's; `ve_diagnose rights@0` on a `rights-elaborate` case whose environment is `7` | `{"id": …, "status": "error", "error": "UnsupportedProfile: the case is outside the unit's domain"}`; exit 1 |
| L7 | `ve_diagnose soft-norms@0`, `norms@0` and `norm-defaults@0` on their corpora after S8.0 and after each shadow commit | byte-identical rows |
| L8 | `lake build` with `Tables/Rights.lean` naming a hook `Hooks/Rights.lean` does not register | fails at the `#guard` |
| L9 | the Lean view `soft_source_of_rights` on every corpus environment, and on `7`, `[]` and `{}` | equals `{"environment": s, "norms": []}` with `s` `stripRights`'s result where it succeeds, and `{"environment": v, "norms": []}` where it fails; the Python view gives the same object on the same inputs (R9 of 12) |
| L10 | the Lean classifiers `rights_names` to `rights_bar` and `reports_wellformed` against the Python walks, on every catalogue fault and tier-A pair | the same member, or both `ok` |
| T1 | `tools/wire_contract.py --check` on the committed tree | exits 0 and prints nothing |
| T2 | a contract with `status` `public` and the shadow revision | `WC10` |
| T3 | `Tables/Rights.lean` at the switch commit of `rights@0`, against its parent | the diff is the header comment and the numeral of `revision`, and nothing else; the same for `Tables/Reports.lean` and `Tables/Units.lean` at their switches |
| T4 | `rights@0.json` with `uses` `["limits", "names"]` | `WC09` |
| T5 | `soft-norms@0.json` with its revision raised and nothing else changed, then `--check` | `WC11` on `Tables/SoftNorms.lean` and on `Tables/Rights.lean` (the include is inlined); `--write` regenerates both and their inventory lines, and `rights@0`'s revision and lock entry do not change |
| T6 | `ve-units@1.json` with member `5.16g`'s text changed | `WC12` |
| T7 | `--write` after each shadow commit | exactly the generated files of 7.2, the lock and the generated modules' inventory lines change |
| T8 | `names.json`'s `currency` as generated into `Names.lean` | the Lean class admits `USD` and refuses `usd`, `US` and `USDX`, as the Python engine does |
| T9 | `names.json`'s `token` as generated | admits `u7.1` and `news_desk`, refuses `u 1`, the empty string and a 65-byte token |
| T10 | `lake env lean /tmp/wire-s8-stubs/Stubs.lean` from `lean/` (plan, S8-stubs) | exits 0; every `#eval` prints the value its comment states; the only warnings are the `sorry`s |

### 8.8 The corpus-completeness test

`tests/test_wire_gate_corpus.py` keeps its three tests for the pilot and S5's units and runs the same three for
each new unit: every input of the unit's contract tests and of the tests that build its sources is in the unit's
corpus; every source of its conformance scripts (`conformance/rights_differential.py`, `rights_three_way.py`,
`rights.py`; the reports fixtures of `tests/test_reports_lean.py` and `test_reports_agreement.py`; the W6 fixtures
of `usecases/news-article/w6a-quantity-fixtures.json` and `tests/test_w6a_documents.py`) is in it; every fixture
of rights.md 10, attribution.md 10 and units-schema.md 7 that a test builds is in it. The recorder sees the new
paths through the wrappers of 7.1; each wrapper is shown to work by one source submitted through that path and
no other, stored in `<unit>-test-inputs.json`.

| Case | Input | Expected |
|---|---|---|
| S23 | the call on T_R(B_R) with unit 1's right renamed `rights-r8` | raises as R24 with `rights-r8`; the source is in `rights@0-test-inputs.json` |
| S24 | `ve.reports_contract.public_rejection` on B_P with `u1`'s report context `c8` and a hand-made `VEError("x")` | the record of 3.1k with `c8`; `code` `InvalidInput`, the hand-made error's own; the source is in `reports@0-test-inputs.json` |
| S25 | `ve.admission.admit_document` on B_Q's environment with statement 0 `["eq", ["num", "zy", "1"], ["num", "zy", "1"]]` | raises as Q15 with `zy`; the source is in `ve-units@1-test-inputs.json` |

### 8.9 Allowed coverage gaps

**Allowed coverage gaps** (base spec 8.3, for these units; the gate reads this table):

| Gap | Language | Applies to | Reason |
|---|---|---|---|
| G1 | Lean | a check every catalogue fault of which only the in-process API can carry (`readers` `python`) | Reached only by an explicit null, which the wire readers refuse before diagnosis: Lean has no witness; Python has its first-fault and masking witnesses. |
| G2 | both | an included check whose every reaching input fails an earlier check of the including unit on every input of the unit's domain (`soft/3.3b`, `soft/3.3c`, `soft/6.4b` of `rights@0`) | The including unit's own checks 1.3 and 1.4 require the profiles this check requires, and the W1 decoder of `soft/2.3` bounds the predicates this check counts, so the check is never the first fault under this unit; it is witnessed in the pilot's own gate. |
| G3 | both | an included check whose group runs over the view's `norms`, or whose classifier reads the view's norms, which the view makes empty (`soft/5.3` to `soft/5.9b`, `soft/6.4a`, `soft/6.5a` to `soft/6.15` of `rights@0`) | No input of the unit's domain reaches the check: the view gives no norms. It is in the table because the Lean decoder runs the included phases over the stripped environment, and it is witnessed in the pilot's own gate. |

A member declared in a unit's `UNREACHED` (rights 5.1f, 6.4e; reports 2.7j, 3.1h, 3.1m, 3.1o, 3.1y; units S.r)
is not a gap: the `WC08` clause accepts the declaration and the gate reports the member as uncovered, as S5 fixed.

## 9. The switch gate

The DRI reviews, per unit, one gate report at revision `R`, the delta report and the signing file. Astra and
Fable read the measured delta and the signing file before the switch commit. The switch commit is made only when
every row holds, and the gate exits non-zero on any unmet row that is enforced, judging each from the data and
not from a stated summary (base spec section 17).

| Row | Definition | Required |
|---|---|---|
| the continuation rows | base spec section 9: tiers 0 and A, residual, deferred, coverage; feasibility reported with `n1`, `n2`, `coarse`, `t3` partitioning the unit's numbered checks and no threshold | as there |
| S8-pre | `legacy_verdict_differences` and `legacy_crashes`, over every tier | both empty |
| the class rule (`ve-units@1`) | cases with a class difference outside the exemptions of 2.13 | 0; the exempt cases counted and reported |
| the Lean route list (`rights@0`, `reports@0`) | `lean_route_changes` on checks outside section 6's allowed set | 0; the allowed set's counts reported |
| the legacy class differences (`rights@0`, `reports@0`) | `legacy_class_differences` | reported |
| the signed delta | the checks with a measured text change, against the keys of `signed` | the two sets are equal |
| the boundary | tier P: G1 on every rejected case; G2 on every handler-reaching case; G12 on every other rejected case | no difference |
| errors without a record | tier P cases on which the failure rule applied | 0 |
| the source is not modified | Z5 | 0 cases |
| the legacy validators | Z3 and Z4; Z9 | byte-identical |
| the viewed records (`rights@0`) | records with `path` `/environment` and an `inner_path` | reported |
| the corpus | `tests/test_wire_gate_corpus.py` for the unit | passes |
| the scratch file | T10 | passes, before the statement review |

When each row is enforced: S8-pre, the class rule and the Lean route list from the measurement commit on, whatever
the `status`; the signed delta, the boundary and errors without a record only at `public`; every other row
whatever the `status`. A row that fails after a switch commit is handled by a revert of the commit, or by a
revision that sets `status` to `shadow`.

## 10. Limits, and what is not claimed

1. **No verdict and no identity.** The engine runs inside the handler of a rejection and returns the error it
   was given, at six statements of three functions. That is a tested property of each (V1), not a theorem.
2. **One entry point per unit.** Only the document loader (rights, reports) and `_admit_document_python` (units)
   are public; the entry points of 2.10 keep today's messages.
3. **The delta is complete on the corpus.** An input outside the unit's corpus can show a message change that no
   list contains, a class that differs from its record's, a residual record, or an error without a record.
4. **The tables' order is the authority's.** For `rights@0` and `reports@0` Python today reports another fault
   first on many multi-fault inputs (the block before the units, the front matter before the units, a holder
   while decoding); after the switch the public message is Lean's first fault. For `ve-units@1` the Lean route's
   first fault can differ on multi-fault inputs and is reported, and the vocabulary decoder runs before the slot
   checks (2.5, phase 3).
5. **Inherited texts differ between languages** until S4 items 3 to 6: the envelope and gate hooks (reports 1.6,
   units 1.2), the vocabulary decoders (reports 1.20, units 3.1), the formula and package decoders (rights 4.3c,
   6.4b to 6.4d; reports 2.7h, 2.17d, 2.20c), the W2 kind (units 5.9), the literal and shape members of S (k1,
   k2, o3, p) and the unit decoder's shape member (rights 4.3c, whose Python text is the walk's own and new).
6. **Classes under Lean authority.** On `rights@0` and `reports@0` the public error's `code` is Python's class
   and its record's `class` is Lean's; they differ on the cases of 2.13, which the gate counts and does not
   enforce. On `ve-units@1` the class rule has the exemptions of 2.13, among them every `AdmissionError` check,
   because the format names no such class.
7. **The view's `path`.** Every included soft record points at `/environment`; the pointer inside the stripped
   environment is `args.inner_path` (edit g). Whether an IDE can use it is measured here for the first time
   (`viewed records`) and not decided.
8. **Rust is not run.** `ve-units@1` has a Rust decoder and `reports@0` a Rust gate, both with their own texts
   and classes (`SyntaxError` for a malformed integer or decimal); nothing here compares them or changes them.
   The three-way claims of rows 11 and 12 wait for S4 item 2.
9. **The failure rule hides an engine defect from the caller.** The caller gets today's error; the defect is
   visible only where the gate or a test runs the same input.
10. **Cost.** A rejection at a call site costs one engine run; `correlated_soft` and `rights_stratified` run
    `RightsDocument` again, `lemma_established` replays a certificate, and the Python walks of `rights@0` and
    `reports@0` re-read the units. An accepted document costs nothing.
11. **The domain cuts around the loader.** For `reports@0` a unit whose kind does not decode, and `lemmas`,
    `reading_sets` and `narrowings`, are outside the domain and get no record through this unit (row 13's).
    For `ve-units@1` the single-statement route cases get no record.
12. **Unverified reading.** The Lean stubs were not type-checked and the numbers of section 8 were not run by
    this draft's writer (5.6); the S8-pre candidates of 2.13 were seen by reading only.
13. **The surface prints none of the sentences of 3.2.** They are fixed, not shown.

## 11. Statement review checklist (Astra + Fable, before any build step)

1. **Scope (plan section 8, questions 2, 3, 7, 8).** Is S8 before S4 items 3 to 6 right? Is one shadow per unit
   right? Is the document loader the right call site for rights and reports, and `_admit_document_python` for
   units? Is leaving Rust out right, or should the units switch wait for the Rust engine?
2. **Authority and order (D2, D3; plan question 5, 6).** Is Lean's order right for `rights@0` and `reports@0`,
   given the delta it produces, and Python's for `ve-units@1`? Is "the record's class is Lean's, `code` is
   Python's" acceptable, or must Python's classes be aligned first?
3. **The `rights@0` table (2.3).** For each row, do the kind, guard and text reproduce `decodeRightsSource` and
   `validateRights`? Is the viewed include at `/environment` with the pilot's five phases right, and are gaps G2
   and G3 the only unreached included checks? Derive R37 to R40 independently. Rows worth attacking: 4.3c (one
   inherited member for every shape), the split of `checkRights` into 6.3 to 6.6, 7.1 (the pilot's set over
   `T″`).
4. **The `reports@0` table (2.4).** Does the domain (2.2) cut exactly where the loader's W2 checks are? Do 2.7's
   members and 3.1's reproduce `decodeContent` and `firstFailure`? Derive P30 to P33 and P35 to P37. Is 3.1w's
   sentence one reading?
5. **The `ve-units@1` table (2.5).** Is S right, member by member, against `elaborate_quantity` and
   `decodeQuantity`, and is one list at five positions (D13) better than five tables? Is the deviation of phase 3
   acceptable? Is `UNITS_ADMISSION_ERROR` as `InvalidInput` acceptable, or must the format gain the class?
6. **The hooks (2.6).** Can a Python walk disagree with the frozen Lean function it mirrors on an input tier A
   does not reach? Can any Lean hook fail for a reason that belongs to a later check? Is the view total and equal
   in both languages (L9)?
7. **S8-pre (2.13).** Attack the candidates: the rights name format, the right without `guard`, the condition
   without `decided_by`, the base predicate named `rights__…`, the correlated predicate count, the bridges and
   scoped counts, the round trip. Are there others?
8. **The delta (2.12, 6).** Derive the expected lists independently; attack the allowed Lean route set of
   `reports@0` and the field-list texts of `ve-units@1`.
9. **Wordings (3).** Does each `says` sentence have one reading? Does the viewed record's sentence (3.2) say
   where the fault is? Is any rejected wording of 3.3 still in this file or in the plan?
10. **Conservativity (5.3, 7, 8.6).** Can anything in item 1 change a verdict, an identity, a code, a Lean byte
    other than the generated tables and the registry's added lines, or a Rust byte?
11. **The scratch file (5.6, T10).** Did it type-check, and do the `#eval`s give section 8's numbers? Which
    corrections did S8-stubs make (section 12)?
12. **The corpus (8.8).** Does the recorder see every path through which a test submits a source of any unit?

## 12. Choices this specification resolves, and open points

The plan fixes that there are three switch commits, that each sets `VEError.diagnostic` and the message, and that
each adds its call sites. Everything below is this specification's own choice, put to the statement review.

| # | Choice | Relative to the base documents |
|---|---|---|
| R1 | Item 1 is the three units through every step of 5.1, after S8.0 | the pointer says the three units; no contract exists |
| R2 | The tables of `rights@0` and `reports@0` are in the Lean routes' order with Lean's texts; `ve-units@1` in Python's with Python's | base plan 5.1 step 1 and rows 10 to 12; S5's tables were Python's because Python was the authority |
| R3 | The domains: `rights@0` excludes only non-object environments and documentless admissions; `reports@0` excludes the loader's W2 checks; `ve-units@1` excludes environments without the extension, `risk@0`, and single statements | S5 spec R3: the adapters refuse what the two validators would not both validate |
| R4 | The contract's classes are the authority's: Lean's for two units, so the public `code` may differ from the record's `class` | base plan 2.4 ("`class` is the legacy `VEError` class") read as the authority's; the S4 and S5 rule kept for units |
| R5 | `rights@0` includes the pilot's `envelope`, `declarations`, `profiles`, `references`, `semantic` at `/environment` under a view; `rule-fields` is not included | base spec 2.6 and edit g; the first view in production |
| R6 | The view is total: `stripRights`'s result where it succeeds, the value itself where it does not, with `norms` `[]` | base spec 2.5 rule 4; `run_congr_reached`'s hypothesis |
| R7 | The Python classifiers of `rights@0` and `reports@0` are walks in the Lean functions' order; the Lean classifiers call the frozen functions | S5 spec 2.5 did the mirror image for Python's authority |
| R8 | JSON-library texts of Lean (`fields do not match: …`, `String expected`, `array expected`) get fixed contract texts or inherited members; the Lean route differences they cause are an allowed, listed set | base spec 3.4 keeps today's text where the implementations agree; here they do not |
| R9 | `lean_route_changes` is enforced within section 6's list for `rights@0` and `reports@0`, reported for `ve-units@1` | S5 spec R14 reported it only |
| R10 | The statement set S is one list emitted by five classifier entries with the entry's prefix; `WC12` checks the copies | base spec 2.5 has no shared member list |
| R11 | `UNITS_ADMISSION_ERROR` is declared `InvalidInput` and its checks are exempt from the class rule | base spec 2.2 names ten classes; `AdmissionError` is not one |
| R12 | Two statements per unit are wrapped (the environment's and the document's), so an environment fault of the unit's own phases is public | the S4 and S5 switches wrapped one statement each; the environment belonged to row 4 there, here its W6 part and the reports and rights blocks are the unit's |
| R13 | `unit_label` for `ve-units@1` is `Units` (one entry of a name table), so the module is `Tables/Units.lean` | S5 spec 7.1's rule would give `VeUnits` |
| R14 | `limits.json` gains six names and `names.json` two classes (`token`, `currency`, `not_reports_reserved`); the other limits the hooks read are the modules' constants | base spec 2.2 |
| R15 | `legacy_validation` per unit composes the environment decoder with the document validator, as the route does | S5 spec R11 |
| R16 | Members no input reaches are declared `UNREACHED` with a reason rather than dropped, where the frozen function has the branch | S5 kept the pilot's rule 13 (a text with no member is a residual); here the branches are known |

Open, for the review or the build to settle:

1. **The S8-pre candidates of 2.13**, and any the shadow finds. Each is a verdict difference between two
   frozen-by-policy validators, or a Python crash; the fix is a product decision outside this work. The rights
   name format and the right without `guard` are the two where rights.md 3.2 sides with Python.
2. **Aligning Python's classes to Lean's** on `rights@0` and `reports@0` (plan question 5), or accepting that the
   public `code` and the record's `class` differ on the counted cases.
3. **The registry** (plan question 4): append-only edits of `Diagnose.lean`, or one move to `DiagnoseMain.lean`.
4. **`AdmissionError` as a contract class.** Adding it to base spec 2.2's list is a format change with its own
   statement review; R11 avoids it at the cost of an exemption.
5. **The scratch file.** Every statement of section 5 and every number of section 8 awaits S8-stubs; a
   correction is recorded here when made.
6. **The deviation of `ve-units@1` phase 3** (the vocabulary decoder before the slot checks): accepted here as the
   only expressible form; the alternative is a per-predicate inherited hook that validates the whole vocabulary
   at each predicate, which would report the same text many times over.
7. **The width of 4.3c and 2.7h.** One inherited member for every shape failure of a unit's decoder keeps the
   table short and the Python walk honest about library texts; the review may prefer one member per field.
8. **Whether `reports@0`'s domain should instead carry the loader's W2 checks as inherited hooks**, so that a
   document with a bad kind gets a record through this unit rather than through row 13's.

