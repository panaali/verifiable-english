# Wire contract stage S6: `speech-acts@0` (PLAN)

**Status:** plan only, draft 2, 2026-10-04, branch `design/wire-s6` from `main` at `bb05a08d`. No code or proofs
change with this document. Draft 1 (`e67dabed`) was a pointer of one paragraph: item 1 of this plan is stage S6 of
[wire-contract-PLAN.md](wire-contract-PLAN.md) (the **base plan**), "`speech-acts@0` (numbered table for the spec,
two-sided delta)", with the base plan's S6 section applied exactly: only diagnostics may become uniform (listed per
profile); accept/reject and identities unchanged; the corpus-completeness test kept; the difffuzz baseline, if
merged, must not grow; honest open questions. Draft 2 applies the converged position of
`manage-agents/debates/design-wire-s6/{fable,astra}.md` and writes the plan out. The item-1 statement spec is
[wire-contract-s6.md](wire-contract-s6.md) (the **statement spec**); its statement review comes before any build
step. [wire-contract.md](wire-contract.md), the statement spec of S0 to S3 with its build responses, is the **base
spec**; [wire-contract-S4-PLAN.md](wire-contract-S4-PLAN.md) and [wire-contract-s4.md](wire-contract-s4.md) are the
**S4 plan** and **S4 spec**; [wire-contract-S5-PLAN.md](wire-contract-S5-PLAN.md) and
[wire-contract-s5.md](wire-contract-s5.md), on branch `design/wire-s5`, are the **S5 plan** and **S5 spec**, whose
shape this plan follows.

**Prerequisite.** Stage S5 is merging in parallel (`wire-s5/integrate` at `eccd329b`): its generalisation of the
pilot's tooling (S5.0, `9aaa95c4`: `tools/wire_contract.py`, the gate, the delta, the golden and catalogue files,
the recorder, the corpus test, the pre-commit hook and the Lean unit registry take a unit) is what every step of
this plan runs on, and nothing here regeneralises it. This plan and its statement spec are written against the
generalised tooling as the S5 plan (its 2 and 7.1) and the S5 spec (its 7.1) specify it. S6 starts after S5 has
merged into `main`; if S5 changes the tooling's names or paths before it merges, the statement spec's section 7
follows the merged names and the review notes it.

**What the debate files are.** As for S4 and S5, `debates/design-wire-s6/` holds the three files of
`debates/design-wire/`, word for word: the debate on the base plan (CONVERGED after round 3; Sol at xhigh stood in
for Astra, as `astra.md` records), and `TOPIC.md` still asks about the base plan. No reviewer has read this plan.
The converged edits a to h are already in the base plan (its section 11) and were restated for S4 and S5 (S4 plan
section 3; S5 plan section 3). "Applying them exactly" therefore means here: each edit is restated as it binds
stage S6 (section 3), and no design choice of the debate is reopened or added to. Everything in this plan that
the debate did not decide is marked as a choice of this draft and listed in section 8 for the statement review.

The plan was written from reading the sources at `bb05a08d` (and `wire-s5/integrate` at `eccd329b` for the
generalised tooling); nothing was built or run, and every `file:line` reference must be re-read at each step.

## 0. Decision in brief

1. **Stage S6 is one item with one unit.** Item 1 is the base plan's row 8 of 5.3: the contract `speech-acts@0`,
   taken through every step of base plan 5.1: author, hooks, generate, shadow, delta report, DRI review, switch.
   The contract does not exist today, so the pointer's "numbered table for the spec" is read as: the table is
   authored first (statement spec 2.3), the generated English table `docs/spec/speech-acts-wire-table.md` is
   written by the tooling, and speech-acts.md section 7 points at it.
2. **The table's order is the spec's "Order" paragraph, refined.** Base plan 5.1 step 1 takes the spec's order
   where the spec has one, and base plan row 8 fixes the refinement: "speech-acts.md 7 'Order', refined to a
   numbered table; shape of all units before references". So the table runs the profile gate, the environment
   block, W1's declaration checks, the block's references, the document's shape, every unit's shape in document
   order, the bindings, every unit's references in document order, the reading candidates, the queries and the
   policy, in that order (statement spec 2.3). Neither validator follows that order on a document with two
   faults: Python resolves a command's references while it reads the unit, Lean reads every unit before it
   resolves any. Base plan question 2 says so ("speech acts, where both implementations change and neither order
   is consistent today"), and that is the **two-sided delta**: the measured list has a Python side and a Lean side.
3. **Two sides, one switch.** Python's side is signed by the DRI and switched at one call site: when the
   `ve-document@2` source wrapper rejects a document while `SpeechDocument` validates it, the error carries the
   contract's record. When a check of the table fails, the record names the first one that fails and the message
   is that check's text; otherwise the message is the validator's. Lean's side is measured and reported, not
   applied: the speech-acts decoder is frozen (`lean/VE/SpeechActs/Wire.lean` and `Tree.lean` are hash-listed,
   `VE/Route/frozen-sources.sha256:236–237`, and the manifest pins `Wire.lean` whole, `ve/assurance-manifest.json:87–89`),
   so no row of `ve_speech_acts_route` changes. The uniform answer, for both recorded reproducers and every
   other multi-fault document, is the record: Python's public message and `ve_diagnose speech-acts@0` give it,
   and the Lean route's own text is listed beside it. Base plan row 8's "first diagnostic ... in Python **and**
   Lean" is read this way; changing the frozen route's text is a separate plan (section 8, question 2).
4. **The contract still decides no verdict** (edit f). The engine runs inside the handler of a rejection that
   `SpeechDocument` has already raised, at `ve/speech_document.py:245`, and hands back the same error object.
   `ve/speech_acts.py` is not edited.
5. **The unit is the document core, not the `ve-document@2` wrapper.** The root is `{"environment", "document"}`
   with the document's `units`, `queries` and `reading_sets`; the Python legacy validator is
   `SpeechDocument(Environment(environment), units, queries, reading_sets=…)`, which the three-way tests call
   `core`, and the Lean legacy validator is `ve_speech_acts_route` on a `speech-elaborate` case. Wordings
   (`source`), identities (`meaning_id`), answer and compliance records and the wrapper's envelope fields are
   outside the unit's domain: wordings are English-layer diagnostics, which base plan section 4 leaves out, and
   the rest is `ve-document@2`'s (base plan 5.3, rows 13 and 14).
6. **Rust has no column.** Rust never elaborates speech acts (speech-acts.md 10; no `rust/` file names them), so
   the unit does not need the Rust engine of S4 item 2, which stays undone.
7. **Base plan rows 2 to 6 are not included.** The environment stays one inherited hook with language-specific
   text; the P0 formula shape and typing stay inherited classifier sets; W1's norm decoder and W1's check of the
   policy stay inherited hooks. `norms@0` (S5) is not included, although the policy check is W1's: the policy is
   not a value in the input but the active norms with one demand per active command, and an include can only
   view the value at its site, not the root (section 8, question 4).

## 1. Where the work stands (read at `bb05a08d`, and `eccd329b` for S5; not run)

| Fact | Source |
|---|---|
| Three contracts exist after S5: `soft-norms@0` public at revision 4; `norms@0` and `norm-defaults@0` in shadow. S5-pre is open. The tooling takes a unit; the Lean unit registry in `Diagnose.lean` gained two entries by an append-only edit (the S5 spec's C4 exception) | `wire-s5/integrate`: `ve/wire_contract/`, `conformance/wire-contract/s5-pre.md`, `lean/VE/WireContract/Diagnose.lean:5–6, 39–40`; S5 spec 5.3 |
| Python has no admission dispatch for speech acts: the semantic core says so, and `ve/admission.py` and `ve/backends/dispatch.py` do not name it. Lean's route rejects W2 `admission` of a speech-act document with a diagnostic | `ve/speech_acts.py:1–5`; `lean/VE/SpeechActs/Run.lean:26–29` |
| Python's only production path is `python -m ve speech-acts <path>`, which loads a `ve-document@2` source into `SpeechSource`; that wrapper validates the format, the environment, the unit envelopes and spans, the fences, the open terms, the reading sets and the narrowings, then builds the core by one statement, `SpeechDocument(self.env, self.units, meta.get("queries", []), reading_sets=sets)`, then checks meaning ids, statuses, open terms, answers and compliance | `ve/__main__.py:112–120`; `ve/speech_document.py:138–294, 245` |
| The core validates the profiles, the units in document order (kind, content, fields, references and the guard's typing together per unit), the reading-set shapes before the units, the bindings after them, then the candidates, the question count, the queries, the wordings and the policy | `ve/speech_acts.py:492–640` |
| Lean's route decodes the environment (gate, declarations, block, W1, phrases, templates), the reading-set states, every unit in document order (kind and content shapes, with each formula typed where it is read), then the unit count, duplicate ids, the set units, the spans, the bindings, the reading questions, the dormant units, the queries, the candidates, the regeneration, and `checkSpeech` (the scope's references, every command's references, the question count, every question's references, the policy, the queries) | `lean/VE/SpeechActs/Wire.lean:199–211, 455–503, 869–961`; `lean/VE/SpeechActs/Tree.lean:256–317` |
| The two recorded reproducers: `[c1: act nonesuch, c2: force maybe]` is `UnknownSymbol` in Python and `InvalidInput: force` in Lean; `[b: binding {"you": 7}, c: force maybe]` reverses the first-fault order. The test compares status only; the spec records the limitation and names "the P1 shared wire contract" as what will align the order | `tests/test_speech_acts_conformance.py:1856–1871`; speech-acts.md:884–888 |
| The generated-mutation test compares Python's and Lean's texts only on route fields (the scope, `queries`, `reading_sets`, and `content` under a unit) and leaves the unit envelope to W2: "W2 owns the enclosing span, meaning, support and unknown unit fields" | `tests/test_speech_acts_conformance.py:1912–1971` |
| Lean checks what Python does not: a unit count above 10,000 (`ResourceLimit: unit count`), the unit envelope's exact keys and `span`, the document's exact keys, answer records' `conditional` and `by`. Python checks what Lean does not: a unit's `meaning` and `support` present, the wordings (`_check_wordings`), the restricted JSON subset of the environment (`canonical_json`) | `Wire.lean:456, 872, 876, 879, 951–960`; `ve/speech_acts.py:537, 623, 809–836`; `ve/environment.py:316` |
| Python raises nearly every speech-act rejection as a plain `VEError` whose text names another class (`UnknownSymbol: sort s`, `MissingObligationRole: …`, `QueryMismatch: u`); the four limits are `ResourceLimit`; the profile gate's are `UnsupportedProfile` | `ve/speech_acts.py:26–72, 493–764`; `ve/profiles.py:77–84` |
| The Lean route reports no `code`; its rows carry a bare `error` string, whose leading word Python maps to a class | `Run.lean:538–544`; `ve/backends/diagnostics.py:31–52` |
| Rust has no speech-act route, decoder or case kind; on the `elaborated-document` family it carries Python-generated premises marked untrusted | speech-acts.md 10; `rust/` has no file naming speech acts |
| speech-acts.md 7 calls its diagnostics "shared text in Python and Lean unless marked" and has the known-limitation paragraph of 884–888 | `docs/spec/speech-acts.md:852–888` |
| `infra/difffuzz` is a branch at `bb05a08d` with no commit of its own; there is no difffuzz baseline on `main` | `git show --stat infra/difffuzz` |

## 2. Item 1: `speech-acts@0` becomes public

The statement spec fixes every detail; this section is the plan-level summary.

- **Before the switch, S6-pre (blocks the switch).** The shadow gate lists every corpus case on which the Python
  core and the Lean route disagree on the verdict (`legacy_verdict_differences`). A verdict difference is outside
  this plan's licence and is fixed separately, as S3-pre, S4-pre and S5-pre were, with its record
  `conformance/wire-contract/s6-pre.md`. Candidates from reading: more than 10,000 units (Lean rejects, Python
  does not); an environment outside the restricted JSON subset that only the in-process API can pass (Python
  rejects, the Lean case parser decides). A `functional` or `total` flag without `data@0` is refused by both
  with different texts (`Predicate flags require data@0` against `speech-acts@0 with data flags`): a text change
  of the table's 1.9 and 1.10, not a verdict difference. Class differences between the two are recorded and not
  fixed: the contract's classes are Python's (section 8, question 6).
- **The measured two-sided delta.** The gate computes, for every corpus case that the Python core rejects, the
  record the overlay would report, and lists every case whose message or class would change, grouped by check
  (`public_diagnostic_changes`); and, for every corpus case that Lean reads and rejects, every case on which the
  Lean route's text differs from the record's (`lean_route_changes`), grouped by check, with one example each.
  The first list, restricted to the cases that reach the switched statement (statement spec 2.10), is signed by
  the DRI check by check (`conformance/wire-contract/speech-acts@0-switch.json`), with the release note; the
  second is reported, with the two recorded reproducers named in it, and is not enforced (decision 3). This is
  step 5 of base plan 5.1, done as S4 and S5 did it: the measurement is a commit of its own, before the switch
  and in shadow.
- **The domain.** The unit is measured on `speech-elaborate` cases whose document has `units`, and at most
  `queries` and `reading_sets` besides, whose units carry exactly the envelope `id`, `span`, `kind`, `meaning`,
  `support` and an optional `content`, with well-formed sorted spans, and in which a unit named by a reading set
  is an `asserted` unit without `content` (statement spec 2.2). Everything else is W2's or the English layer's
  and is refused by the adapter, not listed as a verdict difference.
- **The switch commit** (step 6): the contract's `status` becomes `public` and its revision rises; one function,
  `ve.speech_acts_contract.public_rejection`, and one call site in `ve/speech_document.py` are added; generated
  files, the lock and the reports are regenerated. The legacy validators are not edited. At the call site the
  error carries the contract's record. When a check of the table fails, the record names the first one that
  fails and the message is that check's text; otherwise the message is the validator's.
- **What may change, for this profile** (base plan 5.3, row 8): Python's message on the checks of the signed
  list. From reading, those are: the first diagnostic of every document with two or more faults in different
  units or in the shape and the references of one unit (the two reproducers among them); the texts that gain the
  class prefix (`ResourceLimit: definites`, `alternatives`, `questions`, `open-term name`); the profile texts that
  take Lean's words (`speech-acts@0 is required`, `with data flags`, `with <unknown profile>`); and the texts the
  wrapper's envelope checks make unreachable at the call site (statement spec section 6). Lean's route rows do
  not change; Rust has no column.
- **What row 8 asks to delete.** Step 6 deletes "the unit's test tolerance" and "the spec's known-limitation
  paragraph". Row 8 names `tests/test_speech_acts_conformance.py:1856–1871`, which asserts that both validators
  reject the two reproducers and compares nothing else. The gate replaces the tolerance by comparing the record
  of both engines on both reproducers at zero tolerance; the test keeps its two assertions and its comment is
  reworded (statement spec 2.8). Row 8 names speech-acts.md:884–888: the paragraph is replaced by the
  public-record paragraph of the statement spec's 3.5, which states what is then true: the record is one
  answer; Python's message is the record's text; the Lean route's own first fault is unchanged and may differ.

## 3. The converged edits, as they bind stage S6

Each row restates one edit of the joint position (Fable's round 3, which Astra's round 3 restates) for S6. The
base plan's text for each edit is unchanged.

| Edit | What it requires of S6 |
|---|---|
| a. "By construction" is limited to table expansion, and to position, code, path and text conditional on equal predicate results; T3 order is test-enforced; raw JSON scanner order is open | "Uniform" after the switch has this meaning only. Python's public text is the contract's template text; that it equals the Lean engine's record is constructed only where every predicate reached returns the same result in both, and is tested on every corpus case that Lean reads. The order inside the one classifier set that is not inherited, the reading candidates (statement spec 2.3, 9.7), is the unit table's own order, implemented by hand in both languages and test-enforced. The Lean route's own first fault on a multi-fault document is a third thing: the table's order is the spec's, so it can differ, and no claim is made about it (decision 3). The scanner order belongs to S4 item 3 and stays open there |
| b. C1 covers identity serialisation; `VEError.to_dict()` may gain `diagnostic` | The member exists since S1a and is set at the pilot's call site since S4, and at two more after S5. Item 1 sets it at one more; nothing in `to_dict()` changes, and `code` is never written by the switch |
| c. C4 allows additions, generated rehashes, and a reviewed append-only `VE/Audit.lean` diff with its rehash in S1b; the lemmas stay optional | `VE/Audit.lean` is not touched. In S6 the inventory diff of a commit is additions (`Hooks/SpeechActs.lean`, `Tables/SpeechActs.lean`) and generated rehashes (`Limits.lean`, `Names.lean` and the earlier tables, whose headers name the hashes of `limits.json` and `names.json`), plus one reviewed append-only diff of the kind S5 recorded: `Diagnose.lean`'s unit registry gains one import and one entry, no existing line changing (statement spec 5.3), unless S5's open question 4 has moved the list to `DiagnoseMain.lean` by then, in which case no exception is needed |
| d. C2 and the tolerance removals apply where an implementation supports the unit and completes diagnosis; a deferred outcome carries the contract, revision, deferred check id and legacy text, has no `check`, `code` or `path`, and is never a residual | Python's registry is complete, so Python is compared at zero tolerance and its deferred count is 0. The call site consults no Lean process; if the engine ever defers there, the deferred record is reported with the legacy text. Rust does not support the unit and is not run on it; there is no Rust column and no Rust tolerance to remove |
| e. Run the inherited `norm-defaults@0` difference to ground before S3; fix a reachable verdict difference outside the plan | Closed for the pilot (`s3-pre.md`, `s4-pre.md`); S5-pre is open on its branch and is S5's. S6-pre of this plan handles this unit's legacy verdict differences the same way: run to ground in shadow, fixed outside the plan, before the switch |
| f. Strike `Engine.run` as a route's validation; "contract first" covers diagnostics only | The switch puts a call of the engine inside the handler of a rejection that `SpeechDocument` already raised, at `ve/speech_document.py:245`; it hands back the same error object, and on an accepted document the diagnostic modules are not imported. `Environment`, `SpeechDocument` and `SpeechSource`'s other checks keep deciding the verdict and are not edited |
| g. Under a `view`, `path` is the include site; the generator imports `FORBIDDEN`; one switch commit per unit | The contract has no include and no view, so every `path` is the plain pointer into the root and no record has an `inner_path`. The generator is unchanged. Item 1 is one per-unit switch commit: one commit, one revert, its own delta report and release note |
| h. After S3 the DRI reviews the gate; if it fails, stop; S4 onward needs a separate decision | The gate is met (S4 spec section 1). The separate decision for S6 is the pointer (`e67dabed`, 2026-10-04) and covers stage S6 only. S7 onward needs another |
| Scope: S1c moved to S4 | The Rust engine is S4 item 2 and is not started. The unit has no Rust part, so S6 does not need it |

## 4. What S6 does not include

| Not included | Why |
|---|---|
| S4 items 2 to 6 (the Rust engine, `json@0`, `envelope@0.2`, `vocabulary@0.2`, `formula@0.2` and `model@0.2`) and an include of `norms@0` | separate statement specs; the pointer covers S6 only. Until S4 item 5 exists, the environment is one inherited hook; until item 6, the P0 formula shape and typing are inherited classifier members; W1's norm decoder and policy check are inherited hooks because the policy is not a value of the input (section 8, question 4). Their texts stay language-specific (base spec D8) |
| the wrapper's own checks (`SpeechSource`: format, envelope, spans, fences, open terms, W2's reading-set admission structure, narrowings, meaning ids, statuses, answers, compliance) | the unit `ve-document@2` (base plan 5.3, row 14); a rejection there keeps today's text and has no record (statement spec 2.8) |
| wordings: `_check_wordings`, the choice-kind and non-ASCII checks on `source` | English and strict-surface parse diagnostics are outside the base plan (its section 4); units carrying `source` are outside the domain, and at the call site a rejection by a wording is a residual record with the legacy text (section 8, question 3) |
| the other entry points that build a `SpeechDocument` (the direct constructor, `combine`, `effective_scope`, the three-way tests' `core`) | each keeps today's message; listed in the statement spec 2.8 |
| any change of a Python class or text in a legacy validator, and any change of the frozen Lean route | the contract's classes and the residual texts are Python's; a changed class is a product decision this plan does not make; the Lean route is frozen (decision 3) |
| the Lean `admission` of speech-act documents | not implemented in Lean (`Run.lean:28–29`); nothing to compare |

## 5. Gates for every commit of S6

The four conservativity gates of base plan 5.2, as the debate amended them:

- **C1.** No diff in a decoder, canonical serialiser, identity serialisation or digest function. The diff-scope
  list of each commit is in the statement spec (7.2); `ve/speech_acts.py`, `ve/speech_english.py`,
  `ve/environment.py`, `ve/errors.py`, `ve/wire_contract/engine.py` and every Lean module except the generated
  tables and the unit registry are outside it.
- **C2.** Legacy verdicts equal their snapshot; each engine reports a fault exactly when its legacy validator
  rejects, at zero tolerance, where the language completes diagnosis (Python and Lean; no Rust).
- **C3.** Public diagnostics change only as the signed delta lists; the gate fails on a change outside it.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass; the inventory diff is additions
  and generated rehashes, plus the one append-only registry diff of edit c.

And three that the pointer names:

- **The corpus-completeness test is kept.** `tests/test_wire_gate_corpus.py` keeps its three tests for every
  earlier unit, unweakened, and gains the same three for `speech-acts@0`, over the globs `tests/test_speech*` and
  `tests/test_*contract*`; an input that item 1's new tests submit must be in the unit's corpus like any other.
- **`tools/wire_contract.py --check`** passes in the gate and the hook, for every contract.
- **The difffuzz baseline does not grow.** `infra/difffuzz` has no commit of its own at `bb05a08d` and there is
  no baseline on `main`. If it merges before S6's switch, the gate adds one row: the number of stored
  differential findings is not larger after each commit of item 1 than before it; until then the row is vacant
  and the statement spec records it so (its section 9).

## 6. Steps and effort

| Step | Content | Effort |
|---|---|---|
| S6.1a | the shadow commit: `ve/wire_contract/speech-acts@0.json` and its two examples, `limits.json` and `names.json` entries, `ve/speech_acts_contract.py` (hooks, classifiers, adapter, `legacy_validation`, `REGISTRY`), `lean/VE/WireContract/Hooks/SpeechActs.lean`, the generated `Tables/SpeechActs.lean` and `docs/spec/speech-acts-wire-table.md`, `conformance/wire_contract_faults_speech_acts.py`, the registry entry, the manifest mode, the stored reports, the shadow gate | 4.5 d (115 numbered checks and a 55-member classifier; the base plan's 4 d covered authoring only) |
| S6.1b | the measurement commit, in shadow: the stored reports over the whole corpus with both sides of the delta; the gate enforces S6-pre and the class rule from here | 0.5 d |
| S6.1c | DRI review of the two-sided delta: the signing file and the release note; the Lean side read, not signed | review |
| S6.1d | the switch commit: status, revision, `public_rejection`, the call site, tests, the paragraph in speech-acts.md and the pointer to the generated table in its section 7 | 0.5 d |
| S6-pre | the legacy verdict differences run to ground; a fix outside the wire work; `s6-pre.md` | 0.5–1 d |

About 6 to 6.5 engineer-days, against the base plan's 4 for the S6 row. Order: S6.1a after S5 has merged;
S6.1b after the shadow gate is green; S6-pre runs during the shadow and blocks S6.1d. The statement review reads
the statement spec and this plan before S6.1a.

## 7. Risks

| Risk | Mitigation |
|---|---|
| The diagnostic layer changes a verdict | the call is inside the rejection's handler and returns the same error object; a test scans the call site's shape; the gate asserts the raised object's type and code against the legacy validator on every rejected case |
| The engine raises on some input and turns a rejection into a crash | `public_rejection` returns the error unchanged on any exception; the gate requires zero such cases |
| A message changes that nobody signed | C3: the gate fails on a measured change whose check has no signature, and on a signature with no measured change |
| The two legacy validators disagree on a verdict | found by the shadow gate (C2 in both languages on every case), fixed outside the plan (S6-pre), before the switch |
| The table's order differs from both validators on many inputs, so the Python side of the delta is large | expected (decision 2); the delta groups cases by check, the signing is per check, and the release note names the one rule: shape of all units before references |
| The reading-candidate classifier re-implements the unit checks and drifts from them | one function per language, written as "run the unit table's checks on the candidate in table order"; every member has a catalogue fault; tiers 0 and A compare both engines member by member |
| The call site's root carries members outside the domain (`source`, `meaning_id`, `surface`, `status`, `parent_id`), which the corpus never has | no check of the table reads them (statement spec 2.7, V4); the gate's tier P builds wrapper-shaped roots from every corpus case and asserts the same record |
| A Lean hook calls a coarse frozen function and fails for a reason that belongs to a later check | the hooks call `decodeCommand`, `decodeQuestion`, `decodeBinding`, `checkCandidateCommand`, `checkLoneQuestion`, `decodeBudgetFormula`, `typeDiagnostic` and `Norms.validate` on one unit or one formula, never `decodeDocument`; a coarser failure shows as an engine mismatch in tier 0 |
| The corpus misses an input class, so the signed list is incomplete in the field | the corpus-completeness test is kept; the claim is "complete on the corpus", stated as such |

## 8. Open questions

1. **No debate was held on S6.** The debate files are the base plan's. The statement review is the first review
   of anything specific to S6; it reads this plan with the statement spec.
2. **Lean's side of the delta is reported, not applied.** Base plan row 8 says the first diagnostic changes "in
   Python and Lean", but the speech-acts decoder is frozen and this plan edits no frozen file. The record is
   available to a Lean consumer through `ve_diagnose`; the route's own row keeps its text. Changing the route's
   text means editing `Wire.lean`'s order or wrapping the route's rejection with the engine's record, either of
   which is a frozen-decoder change with its own plan, outside this one. The DRI's call whether that plan is
   wanted after S6.
3. **Wordings are outside the unit, but inside the call site.** The wrapper hands the core units with `source`,
   and the core's `_check_wordings` rejects a wording that does not read as its unit's content. The table has no
   check for that, because Lean has no speech English layer and the base plan leaves English diagnostics out; at
   the call site such a rejection is a residual record carrying today's text. The residual count on the corpus
   stays zero because the corpus has no `source`. The alternative is a second contract for the English layer,
   Python-only, which the base spec's engine does not admit (Lean implements every hook).
4. **The policy check is a coarse inherited hook, not an include of `norms@0`.** The policy's norms are the
   active norm units' norms followed by one demand per active command; the demands are not values of the input.
   An include reads the value at its site, optionally through a view of that value, and a view cannot read the
   environment beside the units. Making it an include needs a view that reads the root, which is a change of
   the contract format with its own statement review (base spec 2.3). Recorded; not proposed here.
5. **The domain excludes a reading-set unit that carries content or another kind.** Both cores replace such a
   unit by its authored choice and never validate its own members, so a T1 check on them would fault where the
   validators accept. W2's own rule for such a unit is not stated in speech-acts.md; the statement spec puts it
   outside the domain and lists it as a limit. The alternative is to make every unit-shape check a hook that
   reads the effective unit, losing the T1 share.
6. **Classes.** The contract's classes are Python's (base plan 5.1 keeps the authority's rejected cells), and
   Python raises nearly every speech-act rejection as a plain `VEError`, so most codes are `InvalidInput` under a
   text that names another class (`UnknownSymbol: sort s`). Lean's leading words map to other classes on those
   checks, recorded as Lean legacy differences and not changed. Aligning Python's classes would change its
   rejected cells; not proposed.
7. **One entry point.** Only the wrapper's statement is switched. The direct constructor, `combine`,
   `effective_scope` and the Lean route keep today's messages, so the same fault can read differently through two
   entry points until their own rows.
8. **The question count and the unit count.** Lean refuses more than 10,000 units; Python has no such check.
   It is an S6-pre candidate, not a check of the table. Both refuse more than 256 questions; that is in the table.
9. **Effort figures** are this draft's; the base plan's 4 days covered authoring only and were made before any
   contract existed.

## 9. Debate response table (draft 2)

Source: `manage-agents/debates/design-wire-s6/{fable,astra}.md`, a copy of the base plan's debate. Verdict there:
**BUILD (exact edits): S0 to S3 only, S1c moved to S4**; S4 onward by a separate decision.

| Debate edit | Change in this draft |
|---|---|
| a | section 0, items 2 and 3; section 3, row a; statement spec 2.12 |
| b | section 3, row b; section 5, C1; statement spec 2.6 and 4.2 |
| c | section 3, row c; section 5, C4; statement spec 5.3 and 7.3 (C4) |
| d | section 0, item 6; section 3, row d; section 5, C2; statement spec 2.6 (the deferred record at the call site) and 2.2 (no Rust column) |
| e | section 2 and section 6, step S6-pre; section 3, row e; statement spec 2.11 |
| f | section 0, item 4; section 3, row f; statement spec 2.7 |
| g | section 3, row g; section 2 (one commit, one revert, delta report, release note); statement spec 2.3 (no include, no view) |
| h | section 3, row h; section 1 (the state after S4 and S5) |
| Scope: S1c moved to S4 | section 0, item 6; section 4 |
