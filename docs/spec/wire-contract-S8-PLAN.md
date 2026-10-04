# Wire contract stage S8: `rights@0`, `reports@0` and `ve-units@1` (PLAN)

**Status:** plan only, draft 2, 2026-10-04, branch `design/wire-s8` from `main` at `bb05a08d`. No code or proofs
change with this document. Draft 1 (`70721d76`) was a pointer of one paragraph: "Item 1 of THIS plan is stage S8
of docs/spec/wire-contract-PLAN.md: rights@0, reports@0 and ve-units@1. S0-S4 are merged on main; S5 (norms@0,
norm-defaults@0, including the S5.0 generalisation of the generator) is merging in parallel and is a
PREREQUISITE: write the spec against S5's generalised generator as specified in the S5 plan/spec on branch
design/wire-s5 (docs/spec/wire-contract-S5-PLAN.md, wire-contract-s5.md). Apply the base plan's S8 section
exactly: only diagnostics may become uniform (listed per profile); accept/reject and identities unchanged;
corpus completeness test kept; the difffuzz baseline (infra/difffuzz, if merged) must not grow. Honest open
questions." Draft 2 applied the converged position of `manage-agents/debates/design-wire-s8/{fable,astra}.md`
and wrote the plan out. The item-1 statement spec is [wire-contract-s8.md](wire-contract-s8.md) (the
**statement spec**); its statement review comes before any build step. [wire-contract.md](wire-contract.md),
the statement spec of S0 to S3 with its build responses, is the **base spec**;
[wire-contract-PLAN.md](wire-contract-PLAN.md) is the **base plan**; [wire-contract-s5.md](wire-contract-s5.md)
and [wire-contract-S5-PLAN.md](wire-contract-S5-PLAN.md), on `design/wire-s5` and `wire-s5/integrate`, are the
**S5 spec** and the **S5 plan**, whose shape this plan follows and whose generalisation (S5.0) this plan
builds on.

**What the debate files are.** As for S4 and S5, `debates/design-wire-s8/` holds the three files of
`debates/design-wire/`, word for word: the debate on the base plan (CONVERGED after round 3; Sol at xhigh stood
in for Astra, as `astra.md` records), and `TOPIC.md` still asks about the base plan. No reviewer has read this
plan. The converged edits a to h are already in the base plan (its section 11) and were restated for S4 and S5
(S4 plan section 3, S5 plan section 3). "Applying them exactly" therefore means here: each edit is restated as
it binds stage S8 (section 3), and no design choice of the debate is reopened or added to. Everything in this
plan that the debate did not decide is marked as a choice of this draft and listed in section 8 for the
statement review.

The plan was written from reading the sources at `bb05a08d` and the S5 branch head `c981fe68`
(`wire-s5/integrate`); nothing was built or run, and every `file:line` reference must be re-read at each step.
The writer's sandbox had no Lean toolchain and no build, so the Lean stubs the statement spec names (its 5.6)
were written but not type-checked, and its fixture numbers were derived by hand with the `#eval`s that confirm
them written beside them; both are the first action of the build (section 6, S8-stubs).

## 0. Decision in brief

1. **Stage S8 is one item with three units, in order.** Item 1 is the base plan's rows 10, 11 and 12 of 5.3:
   the contract `rights@0` (the holder-side rights documents of rights.md), then `reports@0` (the reported
   content and assessments of attribution.md), then `ve-units@1` (the W6a unit declarations and quantity
   documents of units-schema.md), each taken through every step of base plan 5.1: author, hooks, generate,
   shadow, delta report, DRI review, switch. None of the three contracts exists today.
2. **The S5 generalisation is the machinery; S8 adds no tooling.** After S5.0 every path of a unit is named
   from the unit (`tools/wire_contract.py` `UNITS` and `unit_paths`, a fault-catalogue module per unit, the
   gate's `--unit`, the recorder, the corpus test, the pre-commit hook). S8 registers three units in those
   tables (S8.0), adds three entries to the `ve_diagnose` registry by the append-only edit S5 recorded (edit c,
   section 3), and changes nothing else in the tooling.
3. **The authority's order, which is Lean's for two of the three.** The tables of `rights@0` and `reports@0`
   follow the Lean routes (`ve_rights_route`, `ve_reports_route`), the authorities of those units
   (`ve/assurance-manifest.json`: `soft.elaborate` and the reports and rights operations are Lean's; base plan
   5.1 step 1 names rights among the Lean-authority units, and rows 10 and 11 say "Order taken from: Lean").
   Their texts are Lean's wherever Python's differ, so Python's public message changes on every such check:
   that is rows 10 and 11's "Python texts that are only suffix-equal today" and "texts". The table of
   `ve-units@1` follows Python (`admission` is Python's; row 12), as S5's tables did. Where a unit's Python
   validator checks the same facts in another order, the record is the table's and the Python public message
   changes on multi-fault inputs; where the Lean route's own first fault differs from the table's (units only),
   that is reported, not enforced, as in S5.
4. **The first view.** `rights@0` includes the pilot's six phases on a transformed value: the Lean decoder runs
   the soft table on the environment with the `rights` block and the `rights@0` profile removed and with no
   norms (`VE/Rights/Wire.lean:115–118`). The include sits at `/environment` under the view
   `soft_source_of_rights`, so edit g applies for the first time in production: an included check's `path` is
   the include site `/environment` and the pointer inside the view goes in `args` as `inner_path`.
5. **Each switch changes one thing in public.** At one call site per unit, when Python rejects a submitted
   source, the error carries the contract's record. When a check of the table fails, the record names the
   first one that fails and the message is that check's text; otherwise the message is the validator's. No
   verdict, no identity, no code and no Lean row changes. The complete list of changed messages is measured
   on each unit's corpus and signed by the DRI before its switch commit.
6. **The contract still decides no verdict.** The engine runs only after the legacy validator has rejected,
   inside the handler of that rejection, and hands back the same error (edit f, section 3).
7. **Rust has no column.** Rust decodes `ve-units@1` environments and statements and gates `reports@0`
   environments, but the Rust engine is S4 item 2, which is not started, so Rust completes no diagnosis and is
   not run (edit d). Row 11's "Rust `reports@0` gate text" and row 12's three-way uniformity wait for that
   item; every Rust text stays as it is, and so does every Rust tolerance. The two deltas this plan can
   deliver are Python's and Lean's.
8. **Base plan rows 2 to 5 are still not contracted** (S4 items 3 to 6 are not started), so the envelope, the
   profile gate and the vocabulary stay inherited checks with language-specific text in all three contracts,
   as in the pilot and in S5; the cost is recorded (section 8, question 2).

## 1. Where the work stands (read at `bb05a08d` and `c981fe68`, not run)

| Fact | Source |
|---|---|
| Three contracts exist after S5: `soft-norms@0` (public, revision 4), `norms@0` and `norm-defaults@0` (shadow, revision 1, their switches blocked by S5-pre). The S5 branch is not merged; this plan's build starts from its merge | `ve/wire_contract/*.json` on `wire-s5/integrate`; `conformance/wire-contract/s5-pre.md` (open) |
| S5.0 is done on that branch: `tools/wire_contract.py` has the `UNITS` table and `unit_paths`; a unit's catalogue is `conformance/wire_contract_faults_<name>.py` with `Fault`, `LEAN_ROUTE`, `CASE_KIND`, `FEASIBILITY_OF`, `RECORDED_TESTS`, `GAP_APPLIES`, `UNREACHED`, `handler_reaching`, `class_exempt`, `own_text`, `call_outcome`, `call_problems`, `replay_sources`, `legacy_difference_sources`, `test_and_fixture_sources`; the gate takes `--unit` and reads the unit's allowed-gap table from the unit's spec; the recorder wraps each unit's `legacy_validation` and `public_rejection`; `Diagnose.lean` lists the units | `tools/wire_contract.py:53–74`, `conformance/wire_contract_gate.py:83–118`, `conformance/wire_contract_faults_norms.py`, `tests/contract_input_recorder.py`, `lean/VE/WireContract/Diagnose.lean:32–38` on `wire-s5/integrate` |
| The Python engine supports `include` with `at`, `view`, `as` and `says`; a viewed include's record has `path` = the include site and `inner_path` in `args`; the Lean engine's `Frame` does the same; the engine corpus exercises a view (`forms@0`, `n1`) | `ve/wire_contract/engine.py:395–491`; `lean/VE/WireContract/Engine.lean:38–55`; `conformance/wire-contract/contracts/forms@0.json`; `engine-golden.json` (`inner_path`) |
| **Rights.** Python's legacy validator is `ve.rights.correlate(environment, units)`: `RightsEnvironment` (profiles, the block's shape, `rights__` predicates, then `SoftEnvironment` on the stripped environment, then holders, bearers, protected, alters) and `RightsDocument` (units in document order with Python's own shape checks, the limits, limitations, citations, line instances, then the correlated soft document). It runs at one production site, the document loader (`_environment` and `RightsDocument` in `_load_document`); `ve.admission` never runs it, and admission of a rights document is Lean's (`admit_rights_document`) | `ve/rights.py:42–112, 180–286, 570–573`; `ve/document.py:294–303, 365, 375–385, 1174–1178`; `ve/rights_route.py:124–134` |
| Lean's rights validator is `decodeRightsSource`: profiles (strings; `rights@0`, `soft-norms@0`, `norms@0`), the block's shape, `stripRights`, `Phases.checkSource stripped (.arr #[])`, no definitions or flags, the document array (at most 1,024 units) decoded unit by unit (`addUnit`), then `validateRights`: `checkRights` (`checkBlock`, the limits, names, predicates, rights and lines, limitations, bars, citations), `validateSoft (correlate D)`, decision-name length, `rightsSemanticCheck`. Every `rights-*` kind and `admission` (through `splitDocument`) runs it | `lean/VE/Rights/Wire.lean:106–120, 235–293`; `lean/VE/Rights/Correlate.lean:240–445`; `lean/VE/Rights/Run.lean:280–336`; `lean/VE/Rights/Admission.lean:39–45, 315–344` |
| Where the two rights validators differ from reading: Lean requires `norms@0` at the environment, Python only through the soft phases; Lean checks no format of a right, limitation or bar `name` beyond the `rights-` prefix (`stringField`), Python requires `[a-z][a-z0-9-]*` of at most 64 bytes (`_name`); Lean checks the block's semantics after every unit is decoded, Python before any unit; Python decodes a unit's lines in `_instances`, after the limits and limitations; a non-list document is `ResourceLimit: units` in Python and `InvalidInput: document must be an array` in Lean; a vocabulary that is not an object is a Python `AttributeError` | `lean/VE/Rights/Wire.lean:112, 185, 283–285`; `ve/rights.py:23–28, 53, 187, 201, 326` |
| The rights differential compares the two validators' rejection texts by suffix (`error.endswith(row["error"]) or row["error"].endswith(error)`) and reports the count; the three-way script and `tests/test_rights_lean.py` compare Lean rows with fixed texts | `conformance/rights_differential.py:265–271`; `conformance/rights_three_way.py`; `tests/test_rights_lean.py:164, 169, 215` |
| **Reports.** Python's legacy validator is `Environment(environment)` (the reports block: present, `holders` 1 to 8 distinct declared sorts, `evidence` a sort, no reserved holder verbalisation, no `reports__` author predicate) and `ReportsDocument(env, contexts, assessments, units, bridges, scoped, open_terms)`. It runs at one production site, the document loader, after the loader's own W2 unit checks; `ve.admission` has no reports branch, and admission of a reports document is Lean's | `ve/environment.py:360–364, 529–547`; `ve/reports.py:115–249, 349–375, 403–557`; `ve/document.py:366, 460–480, 1046–1062` |
| Lean's reports validator is `Wire.decodeDocument`: `decodeEnvironment` (envelope, language, profiles, the reports gate, revision, the block, `reports__` predicates, verbalisations, the P0 vocabulary decoder, holders, evidence, the reserved verbalisation), then `decodeDocumentRaw` (the document's keys, every unit with its content tree, metadata, the limits, contexts, assessments, bridges, scoped checks, lemmas, open terms, reading sets, narrowings), then `WellFormedReports`, whose failure text is `firstFailure`'s, in a fixed order | `lean/VE/Attribution/Wire.lean:43–87, 377–408, 417–484`; `lean/VE/Attribution/Content.lean:602–611, 634–716` |
| Where the two reports validators differ from reading: Python checks contexts and assessments before units and the block's semantics inside the environment decoder; Lean decodes units first and checks the block last; Python checks a report node's holder, act and context while decoding, Lean after decoding (`nodeOk`); Python validates no `kind` of a unit without report content (`json.dumps`), Lean decodes every kind; Python rejects `lemmas` and `reading_sets` under `reports@0` before `ReportsDocument` | `ve/reports.py:138–200, 512–526`; `ve/document.py:463–464`; `lean/VE/Attribution/Wire.lean:329–354, 383–400` |
| Rust gates `reports@0` environments (`needs a reports block`, `with {other} layers`, holders 1 to 8, duplicates, evidence a string) and has no `reports-*` case | `rust/ve-core/src/environment.rs:151–220`; `rust/ve/src/main.rs:97–200` |
| **Units.** Python's legacy validator is `Environment(environment)` (the W6 extension: `unit_schema` and `units` together, the W6 profile tuple, `validate_units` before the vocabulary, slot and constant units inside it, `validate_extension` after it, the round-trip check) and `admit_quantity_document(env, document)` (units, lemmas, open terms, reading sets, narrowings, the graph, admission); every statement runs `elaborate_quantity`. The production site is `_admit_document_python`, reached by `admit_document` under the Python authority when `env.unit_schema` is set; the document loader elaborates each unit's statement itself and calls `admit_document` on the P0-shaped input | `ve/environment.py:321–340, 352–357, 419–423, 499–505, 604–612`; `ve/units.py:88–247, 508–529`; `ve/quantity_admission.py:264–318`; `ve/admission.py:443–444, 493–507`; `ve/document.py:122–143, 962–996` |
| Lean's units validator is `ve_quantity` with kind `document`: `decodeEnvironment` (envelope, language, the profile tuple, revision, schema, the units with `decodeUnit` and `displayInjective`, the vocabulary's keys, tag and sort collisions, `$string` literals, slot units, constant units, verbalisations, then the frozen order decoder on the erased target), then `Document.admitDocument` (`decodeDocument`, `admitDecoded`); every statement runs `decodeQuantity` | `lean/VE/Time/Wire.lean:247–297, 548–574`; `lean/VE/Time/Document.lean:458–570, 598–611` |
| Where the Python and Lean units validators differ from reading: Python runs the vocabulary decoder between the unit declarations and the slot units, Lean runs it last; Python checks the tag and sort collision and `$string` literals after the vocabulary, Lean before; Python has a round-trip check Lean has not; Python quotes names with `repr`, Lean with `String.quote`; a `unary` with the wrong arity is `Invalid unary arity` in Python and `Unknown quantity formula unary` in Lean; a non-canonical integer literal is `SyntaxError` in Python, a bare `non-canonical integer` in Lean | `ve/environment.py:352–357, 419–423, 604–612`; `ve/units.py:262, 381, 432`; `lean/VE/Time/Wire.lean:264–297, 320, 464–466`; `lean/VE/Order/Wire.lean:24–28` |
| Rust decodes the same declarations and statements with its own texts and classes (`SyntaxError` for a malformed integer or decimal, `InvalidInput` for a date), regenerates meaning ids for a document and admits nothing | `rust/ve-core/src/units.rs:89–103, 129–163, 563–702, 842–902` |
| The units tests compare Lean's texts with fixed substrings (`message in got["error"]`) and Python's with `pytest.raises(match=…)`; `tests/test_w6a2_looprecheck1.py:47–52` accepts any class other than `ResourceLimit` on definition premises of the order route, which is not this unit | `tests/test_units_lean_w6a.py:121–129, 163–167, 219–222`; `tests/test_w6a2_looprecheck1.py:47–52` |
| rights.md 8, attribution.md 8 and units-schema.md 3.2 state their diagnostics and an order in words; none has a known-limitation paragraph on diagnostics | `docs/spec/rights.md:777–800`; `docs/spec/attribution.md:1002–1026`; `docs/spec/units-schema.md:275–334` |
| `infra/difffuzz` has no commit beyond `main` and the tree has no `difffuzz` file; the pointer's "baseline must not grow" has nothing to measure | `git log main..infra/difffuzz` (empty); `grep -r difffuzz` (this plan only) |

## 2. Item 1: the three units become public

The statement spec fixes every detail; this section is the plan-level summary.

- **S8.0, the registration.** `tools/wire_contract.py`'s `UNITS` gains the three units with their registry
  modules (`ve/rights_contract.py`, `ve/reports_contract.py`, `ve/units_contract.py`) and legacy validations;
  `conformance/wire_contract_faults_rights.py`, `_reports.py` and `_units.py` are the catalogues; the recorder,
  the corpus test and the pre-commit hook read the same tables; `Diagnose.lean` gains three imports and three
  entries, append-only. No tooling function changes. The S5 units' outputs are byte-identical after it.
- **The roots.** `rights@0`: `{"environment", "document"}`, the document being the array of unit contents the
  Lean route reads (`{"source_units": ids}` first, then every right, right_lines, limitation, bar and norm
  content), as `splitDocument` and `_rights_units` build it. `reports@0`: `{"environment", "document"}`, the
  document being the W2 document the Lean route reads (`units`, `contexts`, `assessments`, `bridges`, `scoped`,
  `open_terms`, optional `graph`). `ve-units@1`: `{"environment", "document"}`, the document being the P0-shaped
  admission input of `ve_quantity`'s `document` kind.
- **The domains.** Each unit is measured on the sources both of its legacy validators validate as the same
  thing (statement spec 2.2): for `reports@0` that excludes a unit whose `kind` does not decode, `lemmas`,
  `reading_sets` and `narrowings`, which Python's loader checks or refuses before `ReportsDocument`; for
  `ve-units@1` it excludes an environment without the W6 extension, one listing `risk@0`, and the single-
  statement cases of `ve_quantity`; for `rights@0` nothing beyond the adapter's case kinds.
- **Before each switch, S8-pre (blocks the switch).** The shadow gate of each unit lists every corpus case on
  which the Python legacy validator and the Lean route disagree on the verdict (`legacy_verdict_differences`),
  and every case on which Python crashes (`legacy_crashes`). A verdict difference is outside this plan's licence
  and is fixed separately, as S3-pre to S5-pre were, with its record `conformance/wire-contract/s8-pre.md`.
  Candidates from reading (statement spec 2.13): a right, limitation or bar whose `name` is not
  `[a-z][a-z0-9-]*` or is longer than 64 bytes (Python rejects, Lean accepts); a rights environment whose
  `vocabulary` is not an object (Python crashes); a W6 environment that Python's round-trip check rejects;
  under `reports@0` a context whose `description` is not a string (both reject, texts differ: not a candidate)
  and a document key outside the Lean route's list (outside the domain). Class differences are recorded and
  not fixed: for `rights@0` and `reports@0` the contract's classes are Lean's; for `ve-units@1` Python's
  (section 8, question 5).
- **The measured delta, per unit.** As S5: the gate computes, for every corpus case that Python's legacy
  validator rejects, the record the overlay would report, and lists every case whose message or class would
  change, grouped by check; the public delta is the part on the handler-reaching cases. The DRI signs the list
  check by check (`conformance/wire-contract/<unit>-switch.json`), with the release note. The measurement is
  a commit of its own, before the switch and in shadow.
- **The switch commit, per unit** (step 6): the contract's `status` becomes `public` and its revision rises;
  one function, `public_rejection`, in the unit's contract module and one call site are added; generated
  files, the lock and the reports are regenerated. The legacy validators are not edited. For `rights@0` and
  `reports@0` the call site is the document loader (`ve/document.py`, `_load_document`), the only production
  path on which Python validates a submitted source of those units; for `ve-units@1` it is
  `_admit_document_python` (`ve/admission.py`).
- **What may change, for `rights@0`** (base plan 5.3, row 10): Python's message on the checks of the signed
  list. From reading, those are every check whose Lean text differs from Python's: the profile texts, the
  block's shape texts (one Lean text for seven Python ones), `document must be an array`, the texts of the
  included soft checks where the pilot already changed Python's, and every multi-fault input on which Python's
  order differs from Lean's. Lean's rows do not change; Rust has no column.
- **What may change, for `reports@0`** (row 11): the envelope and block shape texts, `units must be a list`
  and the W2 metadata texts where Lean's differ, `ResourceLimit: content depth in <unit>` for Python's
  `ResourceLimit: content depth`, and the order of contexts and assessments against units. Rust's gate text
  does not change (no Rust engine).
- **What may change, for `ve-units@1`** (row 12): the field-list texts become fixed texts
  (`InvalidInput: invalid unit record`, `InvalidInput: invalid document fields`, …); names and literals are
  quoted as compact JSON where Python used `repr`; `InvalidDate`, `DateRange`, `UnitPrecision`, `UnknownUnit`
  and `UnitMismatch` become codes; the vocabulary decoder runs before the slot-unit checks, so a predicate with
  a bad slot after one with an undeclared sort reports the sort. The malformed-literal class is Python's
  (`InvalidInput` for a decimal, `SyntaxError` for an integer) and Lean's class on those checks is recorded as
  a Lean legacy difference; Rust's `SyntaxError` for both waits for the Rust engine.
- **What rows 10 to 12 ask to delete.** Step 6 deletes "the unit's test tolerance" and "the spec's
  known-limitation paragraph". Row 10 names `rights_differential.py:270`: the suffix count stays in the
  script's report, and the gate replaces the tolerance by comparing every text of the unit at zero tolerance.
  Row 11 names none. Row 12 names `test_w6a2_looprecheck1.py:47–52` and "substring matches in the units
  tests": the first is about definition premises on the order route, outside this unit, and is not touched;
  the substring matches of `tests/test_units_lean_w6a.py` compare Lean route texts with fixed words and stay,
  since no Lean row changes. None of the three specs has a known-limitation paragraph; each gains the paragraph
  of the statement spec's 3.5. The deletions are empty for these units; that is recorded here rather than
  invented.

## 3. The converged edits, as they bind stage S8

Each row restates one edit of the joint position (Fable's round 3, which Astra's round 3 restates) for S8. The
base plan's text for each edit is unchanged.

| Edit | What it requires of S8 |
|---|---|
| a. "By construction" is limited to table expansion, and to position, code, path and text conditional on equal predicate results; T3 order is test-enforced; raw JSON scanner order is open | "Uniform" after a switch has this meaning only. For each unit: Python's public text is the contract's template text; that it equals the Lean engine's record is constructed only where every predicate reached returns the same result in both, and is tested on every corpus case that Lean reads. The order inside each classifier set (the rights unit decoder, `checkBlock`, `checkRights`, the correlated soft checks; the reports content decoder and `firstFailure`; the units statement set and the admission set) is the authority's and is test-enforced: for `rights@0` and `reports@0` the Python classifiers are walks in the Lean functions' order, as S5's Lean hooks were walks in Python's. The scanner order belongs to S4 item 3 and stays open there |
| b. C1 covers identity serialisation; `VEError.to_dict()` may gain `diagnostic` | The member exists since S1a and is set at the pilot's call site since S4 (and at S5's two, once merged). Item 1 sets it at three more; nothing in `to_dict()` changes, and `code` is never written by any switch. On `rights@0` and `reports@0` the record's class is Lean's, so the public error's `code` and its record's `class` can differ where Python's class differs from Lean's (statement spec 2.13); that is a listed limit, not a change to `code` |
| c. C4 allows additions, generated rehashes, and a reviewed append-only `VE/Audit.lean` diff with its rehash in S1b; the lemmas stay optional | `VE/Audit.lean` is not touched. The inventory diff of a commit is additions (three hooks modules, three tables) and generated rehashes (`Limits.lean`, `Names.lean`, the tables whose headers name their hashes), plus the append-only edit of `VE/WireContract/Diagnose.lean` that S5 recorded as a C4 exception (three imports and three entries here, no existing line changing), unless the DRI took S5's question 4 and moved the list to `DiagnoseMain.lean`, in which case no exception is needed. The three optional statements of statement spec 5.5 are optional in the sense of this edit: if added, `VE/Audit.lean` gains lines only |
| d. C2 and the tolerance removals apply where an implementation supports the unit and completes diagnosis; a deferred outcome carries the contract, revision, deferred check id and legacy text, has no `check`, `code` or `path`, and is never a residual | Python's registries for the three units are complete, so Python is compared at zero tolerance and its deferred count is 0. The call sites consult no Lean process; if an engine ever defers there, the deferred record is reported with the legacy text. Rust supports `ve-units@1` and the `reports@0` environment gate but has no engine (S4 item 2), so it completes no diagnosis and is not run on any of the three; there is no Rust column and no Rust tolerance to remove |
| e. Run the inherited `norm-defaults@0` difference to ground before S3; fix a reachable verdict difference outside the plan | Closed (`s3-pre.md`, `s4-pre.md`; `s5-pre.md` is open on the S5 branch). S8-pre of this plan handles the three units' legacy verdict differences and crashes the same way: run to ground in shadow, fixed outside the plan, before the switch |
| f. Strike `Engine.run` as a route's validation; "contract first" covers diagnostics only | Each switch puts a call of the engine inside the handler of a rejection that the legacy validator already raised: the two rights statements and the `ReportsDocument` statement of `_load_document`, and the `admit_quantity_document` statement of `_admit_document_python`; it hands back the same error object, and on an accepted input the diagnostic modules are not imported. `RightsEnvironment`, `RightsDocument`, `ReportsDocument`, `Environment` and `admit_quantity_document` keep deciding the verdict and are not edited |
| g. Under a `view`, `path` is the include site; the generator imports `FORBIDDEN`; one switch commit per unit | `rights@0` includes `soft-norms@0` at `/environment` under the view `soft_source_of_rights`: every included record has `path` `/environment` and the inner pointer in `args.inner_path`, as edit g fixed and as the Python and Lean engines already do. `reports@0` and `ve-units@1` have no include. The generator is unchanged. Item 1 is three of the per-unit switch commits: one commit, one revert, its own delta report and release note, each |
| h. After S3 the DRI reviews the gate; if it fails, stop; S4 onward needs a separate decision | The gate is met (S4 spec section 1). The separate decision for S8 is the pointer (`70721d76`, 2026-10-04) and covers stage S8 only; S9 onward needs another. S6 and S7 are not prerequisites of S8 (no unit of S8 includes a unit of theirs); S5 is, for its generalisation |
| Scope: S1c moved to S4 | The Rust engine is S4 item 2 and is not started. S8's three units are the first where Rust has code to compare (`units.rs`, the `reports@0` gate); the comparison waits for that item and is listed as such |

## 4. What S8 does not include

| Not included | Why |
|---|---|
| S4 items 2 to 6 (the Rust engine, `json@0`, `envelope@0.2`, `vocabulary@0.2`, `formula@0.2` and `model@0.2`) | separate statement specs; the pointer covers S8 only. Until item 5 exists, the envelope and the vocabulary are inherited hooks in all three contracts, and the formula decoders of rights guards and reports criteria are inherited members; their texts stay language-specific |
| S6 and S7 (`speech-acts@0`, `alternatives@0`, `risk@0`) | their own stages; `risk@0` environments are outside `ve-units@1`'s domain (the risk route carries the unit extension itself, `ve/units.py:36–38`) |
| the other entry points that build a `RightsDocument`, a `ReportsDocument` or elaborate a quantity (the readings route, `UnspecifiedRightsDocument`, `report_rights`, the document loader's own quantity elaboration, the single-statement `ve_quantity` cases, the English front ends) | each keeps today's message; listed in the statement spec 2.10 |
| admission of rights and reports documents, which is Lean's (`admit_rights_document`, `ve_reports_route admission`), and the Lean-authority path of `admission` for quantity documents (`_lean_quantity_admission`) | their rejections are Lean rows read by `checker_error`; no Python validator runs; not switched |
| any change of a Python class or text in a legacy validator, and any change of a Lean row or a Rust text | the contract chooses Python's public message only; a changed class or a verdict is a product decision this plan does not make (section 8, questions 5 and 6) |
| a `difffuzz` baseline | there is none to keep from growing (section 1) |

## 5. Gates for every commit of S8

The four conservativity gates of base plan 5.2, as the debate amended them:

- **C1.** No diff in a decoder, canonical serialiser, identity serialisation or digest function. The diff-scope
  list of each commit is in the statement spec (7.2); `ve/rights.py`, `ve/reports.py`, `ve/units.py`,
  `ve/quantity_admission.py`, `ve/environment.py`, `ve/errors.py`, `ve/wire_contract/engine.py` and every Lean
  module except the generated tables and the unit registry are outside it.
- **C2.** Legacy verdicts equal their snapshot; each engine reports a fault exactly when its legacy validator
  rejects, at zero tolerance, where the language completes diagnosis (Python and Lean; no Rust).
- **C3.** Public diagnostics change only as the signed delta of the unit lists; the gate fails on a change
  outside it.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass; the inventory diff is additions
  and generated rehashes, plus the one append-only registry diff of edit c.

And two that the pointer names:

- **The corpus-completeness test is kept.** `tests/test_wire_gate_corpus.py` keeps its three tests for the
  pilot and S5's units, unweakened, and gains the same three for each new unit; an input that item 1's new tests
  submit must be in the unit's corpus like any other.
- **`tools/wire_contract.py --check`** passes in the gate and the hook, for every contract.

The pointer's third gate, "the difffuzz baseline must not grow", has no object (section 1) and is recorded as
met by vacuity until a baseline exists.

## 6. Steps and effort

| Step | Content | Effort |
|---|---|---|
| S8-stubs | **first:** type-check `/tmp/wire-s8-stubs/Stubs.lean` (statement spec 5.6) and compare its `#eval` results with section 8 of the statement spec; a differing number is corrected in the spec before the statement review reads it | 0.5 d |
| S8.0 | the registration: `UNITS`, the three catalogue modules' skeletons, the recorder's and the corpus test's tables, the hook's paths; the S5 units' outputs byte-identical | 0.5 d |
| S8.1a | `rights@0`: contract (with the view), examples, Python hooks, classifiers, view and adapter (`ve/rights_contract.py`), Lean hooks (`Hooks/Rights.lean`), generated table and English table, catalogue, shadow gate | 4 d |
| S8.1b | the measurement commit for `rights@0`, in shadow: the stored reports over the whole corpus; the gate enforces S8-pre and the class rule from here | 0.5 d |
| S8.1c | DRI review of the delta: the signing file and the release note | review |
| S8.1d | the switch commit for `rights@0`: status, revision, `public_rejection`, the two call sites, tests, the paragraph in rights.md | 0.5 d |
| S8.2a to d | `reports@0`: contract, examples, hooks in both languages, generated files, catalogue, shadow gate; measurement; review; switch, the paragraph in attribution.md | 3.5 d + review + 0.5 d |
| S8.3a to d | `ve-units@1`: the same; switch, the paragraph in units-schema.md | 4 d + review + 0.5 d |
| S8-pre | the legacy verdict differences and crashes of each unit run to ground; a fix outside the wire work; `s8-pre.md` | 1–2 d |

About 15 to 17 engineer-days, against the base plan's 8 for the S8 row, which did not count the measurements,
the switches, S8-pre or the three Python walks in Lean's order. Order: S8-stubs, then S8.0, then the three
units in the order of 5.3 (rights, reports, units); S8-pre runs during each shadow and blocks that unit's
switch. The statement review reads the statement spec and this plan before S8.0.

## 7. Risks

| Risk | Mitigation |
|---|---|
| The diagnostic layer changes a verdict | the call is inside the rejection's handler and returns the same error object; a test scans each call site's shape; the gate asserts the raised object's type and code against the legacy validator on every rejected case |
| The engine raises on some input and turns a rejection into a crash | `public_rejection` returns the error unchanged on any exception; the gate requires zero such cases |
| A message changes that nobody signed | C3: the gate fails on a measured change whose check has no signature, and on a signature with no measured change |
| The two legacy validators disagree on a verdict, or Python crashes | found by the shadow gate (C2 in both languages on every case, `legacy_crashes`), fixed outside the plan (S8-pre), before the switch; the rights name format is the known candidate |
| A Python classifier that walks in Lean's order drifts from the frozen Lean function it mirrors | the Lean classifier calls the frozen function itself (`checkRights`, `firstFailure`); tiers 0 and A compare the two on every catalogue fault and pair; a drift is a mismatch, never a silent record |
| The view makes every included soft record point at `/environment` | that is edit g; `inner_path` carries the pointer, and the English sentence of 3.2 of the statement spec says where the fault is. Whether an IDE can use it was left open by the base spec (its 12, open point 5) and is measured here for the first time |
| The reports unit's domain, cut around the document loader's W2 checks, leaves a class of inputs with no record | the domain is stated (2.2), the excluded checks belong to `ve-document@1` (row 13) and are listed there; the gate counts out-of-domain cases the adapter refuses |
| The units contract's statement set is repeated at five positions | the set is defined once (statement spec 2.5, S) and the lint checks each copy's members against it (T6); the catalogue has one fault per member at each position |
| The corpus misses an input class, so the signed list is incomplete in the field | the corpus-completeness test is kept per unit; the claim is "complete on the corpus", stated as such |
| The Lean stubs were not type-checked by the writer | step S8-stubs runs them first; a statement that does not type-check is corrected in the spec before the review |

## 8. Open questions

1. **No debate was held on S8.** The debate files are the base plan's. The statement review is the first review
   of anything specific to S8; it reads this plan with the statement spec.
2. **S8 before S4 items 3 to 6.** The base plan put rows 2 to 5 first because the later profiles inherit them.
   This draft follows the pointer: the envelope, the profile gate and the vocabulary are inherited hooks with
   language-specific text in all three contracts, and turning them into includes after items 4 and 5 is a
   second delta for each unit.
3. **What "stage S8" covers.** The pointer says the three units; no contract exists. This draft reads it as the
   whole of base plan 5.1 for each, with its own shadow and measurement, as S5 did.
4. **The unit registry.** S5 recorded the append-only `Diagnose.lean` exception and offered moving the list to
   `DiagnoseMain.lean`. S8 adds three more entries; if S5's question is still open, S8 is the moment to move
   the list, after which no unit needs the exception. The DRI's call.
5. **Classes under Lean authority.** For `rights@0` and `reports@0` the record's class is the class of the Lean
   route's text under `checker_error`, and the public error's `code` stays Python's. Where they differ (from
   reading: a non-list rights document, `ResourceLimit` against `InvalidInput`; Python's `VEError` texts that
   name another class, as `UnknownRight`, `IncidentShape`, `KindMismatch`, which both map to `InvalidInput`;
   `UnknownSymbol: sort` where Python raises `VEError`), the public object carries both. Aligning Python's
   classes to Lean's is a product decision in Python's legacy validators, outside this plan; the gate reports
   the count (`legacy_class_differences`) and does not enforce it. The S4 and S5 rule (record class = Python's
   code) is kept for `ve-units@1`, whose authority is Python.
6. **Lean's texts become Python's public texts on multi-fault inputs.** Under Lean authority the table's order
   is Lean's, so where Python today reports a different fault first, the public message names Lean's. That is
   the base plan's rule (5.1 step 1) and the point of rows 10 and 11, but the delta will be large for
   `rights@0` (Python checks the block before the units, Lean after). The signed list makes it visible.
7. **One entry point per unit.** For rights and reports the only Python validation of a submitted source is the
   document loader, so the switch is there and not in `ve.admission`; the loader's rejection is what
   `ve document check` prints. The admission of those units is Lean's and is not switched. For units the switch
   is in `_admit_document_python`; the loader's own elaboration of each unit's statement keeps today's text.
8. **Rust.** `ve-units@1` is the first unit with a Rust decoder and no Rust engine. Nothing in this plan changes
   a Rust text; the three-way claim of row 12 is deferred to S4 item 2, which this plan does not schedule.
9. **The rights name format.** If Lean accepts names that Python refuses (section 2), the fix is either a Lean
   check (a frozen-file edit, outside this plan, with its own review) or Python's check removed (a product
   decision). Until then the switch of `rights@0` is blocked by S8-pre.
10. **The viewed include's usefulness** (base spec 12, open point 5): the first measured answer comes from the
    rights delta report, which counts the records whose `path` is `/environment` with an `inner_path`.
11. **Effort figures** are this draft's; the base plan's 8 days covered authoring only.
12. **The Lean type-check and the `#eval`s were not run** by this draft's writer (no toolchain in its sandbox).
    The stub file is written; S8-stubs runs it before the review.

## 9. Debate response table (draft 2)

Source: `manage-agents/debates/design-wire-s8/{fable,astra}.md`, a copy of the base plan's debate. Verdict there:
**BUILD (exact edits): S0 to S3 only, S1c moved to S4**; S4 onward by a separate decision.

| Debate edit | Change in this draft |
|---|---|
| a | section 0, item 3; section 3, row a; statement spec 2.14 |
| b | section 3, row b; section 5, C1; section 8, question 5; statement spec 2.8, 2.13 and 4.2 |
| c | section 3, row c; section 5, C4; section 8, question 4; statement spec 5.3 and 7.3 (C4) |
| d | section 0, item 7; section 3, row d; section 5, C2; statement spec 2.2 (no Rust column) and 2.8 (the deferred record at the call sites) |
| e | section 2 and section 6, step S8-pre; section 3, row e; statement spec 2.13 |
| f | section 0, item 6; section 3, row f; statement spec 2.9 |
| g | section 0, item 4; section 3, row g; statement spec 2.3 (the view), 3.2 (how a viewed record reads) and 4.1 |
| h | section 3, row h; section 1 (the gate's state) |
| Scope: S1c moved to S4 | section 0, item 7; section 3, last row; section 4 |
