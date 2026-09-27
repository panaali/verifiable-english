# Semantics migration plan: compiled Lean as the single semantic authority

**Status:** revision 2 for the lead's decision, 2026-09-27. Revision 1 received a REVISE verdict from the Astra
review (`~/code/manage-agents/migration-plan-review-astra.final.md`); every A and B finding is resolved below and
the changes are indexed in section 8. Disagreements are in section 9. No code or proofs change with this document.
Inputs: `~/code/ve-bench/bench/ANALYSIS.md` and `results-full/REPORT.md` (commit `5c20b6b`),
[implementation.md](../implementation.md), [verification-contract.md](verification-contract.md),
[conformance/README.md](../../conformance/README.md), [INTEGRATION-GAPS.md](../INTEGRATION-GAPS.md),
[lean/README.md](../../lean/README.md), [PLAN-EXPAND2.md](../../PLAN-EXPAND2.md).

## 0. Decision and scope

The benchmark gives no performance reason to keep three implementations of the same semantics. Every ordinary
compiled-Lean check meets the 200 ms target even one-shot (47–152 ms medians, startup included), batches run
2–30x faster than Python, and Rust is the only runtime that matters for countermodel search (22,145 searches/s,
18.2x Python) and hot evaluation (2.0x Lean). Python's checkers are 1–12 ms warm, so a naive switch would slow
interactive checks; the persistent service in stage 1 removes that objection first.

Target architecture: **Lean decides** every *leaf verdict* (parsing acceptance and canonical text, typing,
environment and model validity, evaluation verdicts, countermodel validity, certificate replay, Background and
definition elaboration, norm elaboration and conflict verdicts, admission, labels, bundles) **and every
*combined verdict* that asserts a consequence** (the claim-graph report with its exact assumption list; the
reading-set classification). **Rust searches and evaluates fast** (countermodel and distinguishing-model search,
budgeted evaluation, traces); every Rust witness is validated by Lean before it is reported. **Python keeps the
surface** (English, five views, documents, IDE and `ve assist`, web app, CLI, harnesses, adapters), **proof
generation** (tableau, order, closure-induction and norm searches) and **orchestration that asserts nothing**
(relabelling a single Lean verdict, diagnostic statuses, display). All Python producers are untrusted; their
output is checked by Lean or labelled as trusted display in the record itself.

What this plan does not claim. Compiled execution does not upgrade assurance. Grammar P1–P3, P7 and P8 and the
graph-wire refinement remain unproved ([lean/README.md § Remaining obligations](../../lean/README.md)); JSON and
wire decoding, SHA-256 identity, IO, compiler and display stay trusted. Section 3, stage 4, therefore narrows the
`assurance` label to operations whose theorems are complete and lists the trusted remainder in every record.

Nothing in this plan changes a proved checker module, a frozen wire identity or an artefact identity; only
`checker_build` and the record ids derived from it change, by design. New Lean code is glue and one new checker
(readings), in new files, each pinned to the proved function it wraps.

## 1. Inventory of `ve/` (19,051 lines, 70 modules)

### 1.1 Semantic duplicates: authority moves to Lean (search and hot paths to Rust), code deleted in stage 5

The "kept" column is now dependency-level (finding B2): it names the symbols that retained modules import, from
the import graph read on 2026-09-27. Stage 0 regenerates this table mechanically; the estimates below are
provisional until then.

| Python | Lines deleted (est.) | Lean authority today | Rust role | Kept after stage 5 (and why) |
|---|---:|---|---|---|
| `ast.py` `_Checker`, `check_formula/document` verdicts | ~150 of 468 | `Formula.check` via `Bridge.decodeFormula` (`check_iff_wellFormed`) | typed `Document::check` | constructors, wire encode/decode, `formula_from_data`; a structural pre-check stays as an untrusted filter for surface code that builds ASTs (rule: Lean types what is reported) |
| `environment.py` semantic validation | ~200 of 366 | `Bridge.decodeEnvironment`, `Route/Gate`, `Route/Wire.decodeVocabulary` | decodes | `Environment` container, structural decode, `environment_id`, `RESERVED`, `valid_identifier`, `validate_identifier` (used by `surface/*`, `assist/*`, `argument.py`, `equivalence.py`, `propose.py`, `fol.py`) |
| `model.py` validation | ~150 of 189 | `Bridge.decodeModel` (proved admissible), Background validity | decodes, validates | `FiniteModel` container, structural `from_dict`, `model_id` (consumers: `readings.py`, `argument.py`, `adapters/cedar.py`, `assist/*`) |
| `evaluate.py` | ~180 of 232 | `Document.eval` (P6) | budgeted evaluation, traces (new) | `_Evaluator` **only if** stage 0 confirms a consumer that cannot switch to the adapter (`adapters/cedar.py:20`, `norms.py:319,356`, `search.py:11`); otherwise nothing |
| `search.py` `check_countermodel` | ~110 | `countermodelCheck` (P11) | | `_used_predicates` (imported by `norms.py:17`) moves to a kept module |
| `search.py` `find_countermodel`, `find_distinguishing_model`, non-vacuity filters | ~460 | none (search is not a checker) | search, extended in stage 2 | nothing, once Rust covers every option in the support matrix |
| `entailment.py` replay verdict path: `_Replayer`, `check_entailment_certificate` internals, `_binding` verification | ~150–200 of 711 | `Tableau.checkCertificate` (v0, closure, core) | | `prove_entailment`, `_Searcher`, and the rule helpers it shares with replay: `_Signed`, `_Branch`, `_InvalidTrace`, `_term_token`, `_derive`, `_apply`, `_closed` (also imported by `closure.py:36,56,180,227`) |
| `closure.py` | ~0–40 of 244 | `Closure/*`, `TableauClosure` | | `derive_extra`, `extra_candidates`, `derive_induction`, `induction_candidates`, `InductionInvariant`: the search (`closure.py:225`) calls the same rule application the replayer used; it stays as untrusted generation code |
| `order.py` replay verdict path: `decode_trace`, `_Replayer`, `replay_trace` | ~130 of 741 | `Order/Tableau.checkCertificate` | evaluates order models | `search`, `_Search` and the shared helpers `closed`, `next_branches`, `neq_split`, `farkas_closes`, `constraint`, `linearize`, `_fourier_motzkin`, `_cut_wire` (`order.py:622–653` uses them) |
| `background.py` generators, `validate_background`, `dependency_order` | ~150 of 201 | route `background`, `dependency-order`, model validity | regenerates Background | `Premise` type, `HOOKS`, and adapter-backed `background()`, `dependency_order()` with the same signatures (consumers: `admission.py`, `bundle.py`, `argument.py`, `entailment.py:549`, `assist/ambiguity_patterns.py`, `definitions.py`, `norms.py`) |
| `definitions.py` | ~100 of 165 | `Definitions/*` via route `background` | defined tables | `Definition`, `_atom`, `premise` types and an adapter-backed `compile_definitions` (imported by `surface/definitions.py:27`) |
| `norms.py` generated premises, conflict targets, `check_conflict`, `check_witness`, certificate replay | ~300 of 409 | `ve_norms_route` `norms-elaborate`, `norms-conflict`, `norms-certificate` | evaluates generated formulas | `Norm`, `NormDocument`, `_atom` surface objects (imported by `norm_strict.py`, `norm_english.py`, `adapters/cedar.py`, `norm_admission.py`), `prove_norm_entailment` |
| `norm_admission.py`, `admission.py` | ~450 of 599 | norms `admission`; route `admission`, `label` | label grammar, DAG order | `token`, `_check_kind`, `parse_label`, `validate_label`, `_decode_reading_set` as structural helpers (imported by `readings.py`, `document.py`, `bundle.py`, `argument.py:65`, `openterms.py`); `_disjunction` moves into the Lean readings checker |
| `bundle.py` Python replay | ~100 of 191 | route `bundle` (`bundle_sound`) | | Lean call only |
| `profiles.py` `checker_family` | ~40 of 66 | `Route/Gate` (`route_gate`) | envelope gate | `LANGUAGE`, `SPEC_REVISION`, `require_checker` as a static routing table |
| `parser.py` acceptance and canonical verdicts | ~250 of 396 | `Surface.parse` (P4/P5), `Surface.normalize` | `parse` with spans and diagnostic classes | `_Parser` as an untrusted surface reader for norm units (`norm_strict.py:9`) and `parse`/`canonicalize`/`is_canonical`/`parse_with_metadata` as adapter entry points (public API, `authoring.py`, `argument.py`, `assist/session.py`, `attacks.py`, `check.py`, `__main__.py`, `printer.py:689`) |
| `printer.py` canonical `print_document/formula` as authority | ~0 of 861 | `Surface.print` (`canonical` field) | byte-identical printer | all of it: view renderers and `_Traversal` (`norm_strict.py:10`); `print_*` become display whose bytes must equal Lean's `canonical` in shadow |
| `argument.py` per-edge replay, countermodel checks, reachability, leaf and composition computation | ~300 of 725 | per edge via `check-certificate`/route; graph via `VE.Graph.checkTableau` (exposed in stage 2, section 2.1) | | package decoding, per-edge orchestration, diagnostic statuses, displays (`outstanding_obligations`) |

Roughly 3,800–4,300 lines, a fifth of the package, are duplicate semantics; revision 1 said 5,000 because it
counted shared search helpers as replay code.

### 1.2 Orchestration: two classes, only one of which is semantics-free (finding A1)

Revision 1 listed `check.py`, `vacuity.py`, `equivalence.py`, `readings.py`, `document.py`, `argument.py`
graph code, `identity.py`, `wire.py`, `errors.py`, `limits.py` and the `ve` API as orchestration "with no
semantics of its own". That was wrong for every place where Python combines several checked results into a new
verdict. The classes below are binding; stage 0 assigns every function to one of them.

**Class L, relabelling.** A single Lean verdict is renamed, wrapped or displayed; no rule combines verdicts.
Covered by Lean's assurance for that operation once it is a covered operation. Examples: `check()` in `check.py`
(`language: accepted` is Lean's parse acceptance, `canonical` is byte equality with Lean's canonical text,
`evaluation` is Lean's evaluation record); `premise_status` in `vacuity.py` (`INCONSISTENT` is one Lean-valid
certificate of ⊥, `model` is one Lean-valid model of the premises, otherwise `UNKNOWN`); the `vacuous` flag that
copies that status onto edges; `document.py`'s premise report; `identity.py` and `wire.py` (spec-pinned RFC 8785
subset and SHA-256, recomputed by Lean for every binding it accepts, section 2.2).

**Class C, combination.** Python derives a verdict from two or more checked results by a rule of its own. These
are semantics. Each one below has a decision: **Lean interface** (the combined verdict is produced by a checked
Lean function and Python only displays it) or **trusted, narrowed** (the record carries `assurance: experimental`
for the combined verdict, names the Lean-checked constituents, and lists the Python rule in `trusted`).

| Combination point | Rule today | Decision |
|---|---|---|
| Claim-graph composition, `argument.py:545–596`: reachable set, leaf (assumption) list, `unresolved_obligations`, `composed`, the `composition` record (`root_claim_id`, `assumption_claim_ids`, `supporting_edge_ids`, Background assumptions) | Python walks the DAG from the root, takes leaves as assumptions, composes when every reachable edge has a Lean-valid `follows` certificate | **Lean interface.** New service mode `graph` (section 2.1) wraps `VE.Graph.checkTableau`, proved by `VE.Graph.check_sound`, `check_entails`, `check_unfolds` and `tableau_certificateSound` (`lean/VE/ClaimGraph.lean:317–335`). Lean returns the `Report` (root claim, exact ordered assumption list). `composed` is true only when Lean returns a report whose root is the package root; `assumption_claim_ids` and `assumptions` are Lean's list, not Python's walk. Python's reachability code is deleted in stage 5; until then shadow compares its leaf list to Lean's and any difference is a zero-tolerance divergence. `lean_checked`/`lean_detail` keep their keys and read "graph report checked by Lean"; `proof` reads "Lean graph report checked" instead of "Python replay checked" (documented wording change). The graph-wire decoding has no refinement theorem and is listed as trusted. |
| Reading-set classification, `readings.py:198–238`: `ALL` from one certificate over per-set disjunctions, `NONE` from one shared model of every reading, `SOME` from one proving choice and one refuted choice | Python builds the right-nested disjunctions and the shared-model premise list, then relabels leaf verdicts into `ALL`/`SOME`/`NONE` | **Lean interface.** New checker `lean/VE/Route/Readings.lean` and service mode `readings` (section 2.1). Input: environment, fixed premises, reading sets (ids, versions, reading ASTs), conclusion, the candidate verdict and its evidence. Lean rebuilds the disjunctions itself (the right-nested constructor already exists in `lean/VE/Route/Admission.lean` for `readings:…:all` leaves), checks the certificate or the model against premises it assembled, and emits the verdict and labels. Theorems: `readings_all_sound` (valid `ALL` evidence ⇒ every choice entails the conclusion), `readings_none_sound` (valid `NONE` evidence ⇒ no choice entails it; the shared admissible model is a countermodel for every choice, via `countermodel_sound`), `readings_some_sound`. `plan_choices` (route selection, 64-choice budget) stays Python: it can only yield `UNKNOWN`. If the checker has not merged by gate 4, `check_readings` is excluded from `covered_operations`, its record stays `experimental` and names the Lean-checked constituent certificate or model; stage 4 is not blocked, and the checker remains a gate-5 requirement. |
| `equivalence.compare`, `equivalence.py:186–189` and the inhabited-sort refinement | `EQUIVALENT` iff both directions have Lean-valid certificates; `DIFFERENT` iff either direction has a Lean-valid countermodel | **Trusted, narrowed.** The rule is a two-clause conjunction with no theorem to attach; the record carries both certificates or the model, `assurance: experimental`, and `trusted: ["python:equivalence.compare"]`. |
| `check_argument` diagnostic statuses: `CheckerConflict`, `ContradictoryPremises`, `Incomplete`, `ResourceLimit`, `InvalidInput` | Python combines per-edge findings into a status that asserts no consequence | **Trusted, narrowed.** These are diagnostics on non-composed records (`proof: not_checked`). They are listed under `trusted` as display. Only `Checked` asserts anything, and it comes from Lean's report (row 1). |
| `check_readings` `vacuous`, edge `vacuous` flags | copy of `premise_status` | Class L once `premise_status` is adapter-backed. |

### 1.3 Surface, authoring, IDE, CLI, harness: unchanged by this plan

`english.py`, `fluent.py`, `natural.py`, `english_vocabulary.py`, `english_phrases.py`, `surface/*` (registry,
Earley all-derivations check, definitions and norms English, data and n-ary sugar), `norm_english.py`,
`norm_strict.py`, `grammar.py`, `lexicon/`, `propose.py`, `authoring.py`, `fol.py`, `openterms.py`,
`adapters/*` (Cedar, Gatekeeper, records, attributes), `printer.py` views, legend and lint, `assist/*`
(`ground.py` is a search whose witnesses are already re-checked; an optional Rust port), `attacks.py`,
`stream_audit.py`, `argument_fixtures.py`, `__main__.py`, `ve_experiments/`, `experiments/`, `conformance/*.py`
generators, `tools/`, and `ve_webapp` in `~/code/ve-webapp`. Surface desugaring (English, data sugar, norm
blocks to norm objects) stays outside Lean's authority exactly as today; the W7 round-trip proof is the
separate remedy. These modules import from semantic modules (section 1.4); the imports are preserved by the
"kept" column, not by leaving the semantic code in place.

### 1.4 Dependency inventory: a stage-0 deliverable, not a gate-5 check (finding B2)

Revision 1 discovered consumers of deleted symbols only at gate 5. The import graph shows the problem is
structural: the untrusted searchers share rule-application helpers with the replayers (`entailment.py`,
`order.py`, `closure.py`), and surface modules import private helpers (`norm_strict.py` imports `_Parser` and
`_Traversal`; `surface/definitions.py` imports `Definition`, `_atom`, `compile_definitions`, `premise`;
`norms.py` imports `_used_predicates`; `adapters/cedar.py` imports `_Evaluator`).

Stage 0 produces `docs/spec/semantics-inventory.md` from a script `tools/semantic_inventory.py` (AST-level import
graph over `ve/`, `tests/`, `conformance/`, `ve_experiments/`, `~/code/ve-webapp`, `~/code/ve-bench`). Every
symbol in a section-1.1 module gets one class:

- **A, authority:** its verdict moves behind an adapter with the same signature; the Python body is deleted in stage 5.
- **U, untrusted helper:** shared by a retained searcher or surface module; kept, moved out of the deleted body
  if necessary, with a module docstring stating that its output is never reported as a verdict. The
  replay-side helpers listed in 1.1 are the first entries.
- **S, surface:** unchanged.
- **D, delete:** no consumer after stage 5.

Rules: no retained module may import a class-A body after stage 4 (a lint in `audit.py`'s Python companion
enforces it); a class-U helper whose only consumer switches to an adapter (candidate: `_Evaluator` for
`adapters/cedar.py`) becomes D; every A row names its adapter and its Lean or Rust interface from section 2.1.
The inventory is reviewed by the lead before adapter design starts (gate 0), and it is the list stage 5 deletes.

## 2. What Lean and Rust lack today

### 2.1 Interfaces the service must expose (finding B1)

The six runner wrappers of revision 1 do not cover the promised operations. `VE.Bridge.runCase`
(`lean/VE/Bridge.lean:255`) requires a model and a candidate AST; route `evaluate` (`lean/VE/Route/Wire.lean:469`)
returns values without a source binding; there is no standalone parse, typing, environment, model or
normalization request, and no graph request outside admission. The table lists every service mode, what it
wraps, and its theorem coverage. Modes marked *new glue* are new files under `lean/VE/Service/` that call existing
proved functions; each is pinned by an unfolding theorem to the function it wraps and covered by `audit.py`.
Nothing under the existing `lean/VE/` modules changes; the P0 hash test is extended to all of them.

| Mode | Request | Response | Wraps | Theorem coverage | Status |
|---|---|---|---|---|---|
| `evaluate` (legacy) | `environment`, `model`, `ast`, `source`? | `values`, `value`, `canonical`, `status` | `VE.Bridge.runCaseReported` | P6 `eval_iff_denote`, `document_eval_iff_denote`; source/AST equality checked when `source` present | existing |
| `route` | any route case (`evaluate`, `countermodel`, `certificate`, `background`, `dependency-order`, `label`, `bundle`, `admission`) | existing route result | `VE.Route.Run.runCaseReported` | per kind: P6, P11, `checkCertificate_sound`, `bundle_sound`, `route_gate` | existing |
| `route/evaluate` gains `source`? | as today plus optional `source` | plus `canonical` | `Surface.parse` and `Surface.print` on the family's surface, then `runFol/runClosure/runOrder` | source/AST equality decided by Lean, as in the legacy runner; parsing itself is P1–P3-unproved | new glue |
| `check-certificate`, `order`, `norms`, `english` | as today | as today | existing runners | as today | existing |
| `parse` | `environment`, `source` (bytes), `family` | `ast`, `canonical`, `source_id`, `meaning_id`, or `status: error` | `Surface.parse`/`print` (`lean/VE/Surface.lean:181,44`), `Closure.Surface`, `Core.Surface`, `Order.Surface.parse` | acceptance is Lean's decision; only the propositional fragment has `parse_print_propositional`; Rust supplies diagnostics for rejections | new glue |
| `normalize` | `environment`, `source` | `canonical` or `none` | `Surface.normalize` (`normalize_idempotent_propositional`) | as `parse` | new glue |
| `check` | `environment`, `ast` (document or formula) | `well_typed`, `meaning_id`, or the typing error | `Bridge.decodeFormula` + `Formula.check` | `check_iff_wellFormed` | new glue |
| `environment` | `environment` | `environment_id`, `profiles`, `family`, or the gate diagnostic | `Bridge.decodeEnvironment`, `Route.Gate.decodeEnvelope`, `Route.Wire.decodeVocabulary` | `route_gate`, decoder proofs where they exist; JSON correspondence trusted | new glue |
| `model` | `environment`, `model` | `model_id`, `valid`, or `InvalidModel(<generator>)` | `Bridge.decodeModel`, `decodeDataModel`, Background validity | `decodeModel` admissibility (proved) | new glue |
| `graph` | `environment`, `nodes: [{name, ast, label?, premises?, certificate?}]`, `root` | `report: {root, assumptions}` or the rejection | `VE.Route.Admission.decodeNode` + `VE.Graph.checkTableau` for `ve.core@0.2`; a legacy-environment node decoder over `Bridge.decodeEnvironment`/`decodeFormula` + `CertificateWire.decodeCertificate` for `ve-argument-tableau@1` packages | `Graph.check_sound`, `check_entails`, `check_unfolds`, `tableau_certificateSound`; certificate bindings via `Route.Wire.bindingOk` (as `Norms/Admission.checkBindings` does today) | new glue (2–3 days) |
| `readings` | `environment`, `fixed`, `sets`, `conclusion`, `verdict`, `evidence` | `verdict`, `labels`, or the rejection | new checker `lean/VE/Route/Readings.lean` | `readings_all_sound`, `readings_none_sound`, `readings_some_sound` (new) | new checker (1–1.5 weeks) |
| `identity` | `kind ∈ {source, meaning, model, claim, edge}`, payload | the id | new `lean/VE/Service/Identity.lean` over `VE.CertificateWire.digest` and the canonical encoder | SHA-256 has vector tests, no proof; trusted as today | new glue (3–4 days) |

Rust supplies, over the same JSON-lines protocol: `parse` diagnostics with codes and spans (pinned by
`parser.json`, 742 cases), `evaluate --trace` with Python's schema (`kind`, `value`, `bindings`, `detail`,
`children`) **and Python's budget rule** (with tracing on, the work budget is `min(max_evaluations,
max_trace_nodes)`, as `evaluate.py:193` does, so outcome classes match), the search options `min_domain_size`,
`nonempty_domains`, `nonvacuous_for`, `semantic_nonvacuity` and distinguishing models, and the deterministic work
budgets and counts. Every Rust witness goes to Lean's `route/countermodel` or `model` before it is reported.

### 2.2 Identity bindings: what Lean recomputes and what remains Python's (finding B1)

Revision 1 said Lean recomputes every identity. Today Lean recomputes `environment_id` and `meaning_id`
(`Route/Wire.bindingOk`, admission `checkBindings`), `report_id` (`Route/Run.runAdmit`, `Norms/Run`),
`document_hash` (`Norms/Replay`) and certificate digests. It does not compute `source_id`, `model_id`, `claim_id`,
`edge_id`, `graph_id` or any `record_id`.

| Identity | Python definition | After stage 2 |
|---|---|---|
| `environment_id`, `meaning_id` | `wire.digest` over the canonical environment / `{environment_id, ast}` | Lean recomputes on every binding it accepts (today) |
| `source_id` | `sha256("ve-source-<identity_version>\n" + bytes)` (`identity.py:9`) | Lean computes in `parse` and `identity`; Python's value must match or the record is rejected |
| `model_id` | `digest("ve-model-<v>\n", {environment_id, model: normalized})` (`model.py:166`) | Lean computes in `model` from its decoded model re-encoded canonically; shadow's identity class catches any normalisation mismatch |
| `claim_id` | `digest("ve-claim-v1\n", {environment_id, source_id, meaning_id, label?})` (`argument.py:106`) | Lean computes in `graph` and `identity`; `graph` rejects a node whose submitted `claim_id` differs |
| `edge_id` | `digest("ve-deduction-v1\n", {version, environment_id, name, premises: [{name, claim_id}], conclusion: {name, claim_id}})` (`argument.py:243`) | Lean computes in `graph`; `supporting_edge_ids` in the composition record are Lean's |
| `report_id`, `document_hash` | route/norms | Lean (today) |
| `graph_id`, argument `record_id`, composition `record_id`, `checker_build` | digests over Python-assembled package and diagnostic records | **remain Python, trusted.** They identify records, not semantic bindings; listed in `trusted` as `python:record-identity`. `checker_build` becomes the Lean binary hash plus toolchain, the Rust binary hash and the Python surface digests from a committed `checkers.lock`. |

### 2.3 Operation × profile support matrix: the compatibility contract (finding A2)

Revision 1's gate 2 allowed existing behaviour to become `UnsupportedProfile` if the pilots did not use it, while
gate 3 demanded zero verdict divergence. Those cannot both hold, and pilot usage says nothing about other users.
The matrix replaces pilot impact as the acceptance criterion.

`docs/spec/semantics-support-matrix.md` is generated in stage 0 by a probe suite (`tests/probe_matrix.py`) that
runs every public semantic operation against every profile family and input class under Python, and later under
Lean/Rust, recording the outcome class and diagnostic code:

- **Operations:** parse/accept, canonicalize, typing, environment validation, model validation, evaluate,
  evaluate with trace, countermodel check, countermodel search (each option), distinguishing model, certificate
  replay (v0, extended, closure, order, core), Background, definitions elaboration, dependency order, admission,
  label, bundle, norms elaborate/conflict/certificate/admission, readings, argument check (graph), compare,
  premise status.
- **Profile families:** `relational-fol@0` alone and with `definitions@0`, `data@0`, `norms@0`; `closure@0`;
  `closure@0+nary@0` (core); `order@0`; each allowed combination in `profiles.py`; the English surface.
- **Input classes:** positive; rejection with a code (malformed, ill-typed, stale identity, invalid model,
  forged certificate); budget boundary (exactly at and one over each `limits.py` cap and each work budget,
  including trace exhaustion at 10,000 nodes).

Cell values: **S** supported (a verdict), **R** rejected with a named code, **U** `UnsupportedProfile`.
**Rule:** no S cell may become R or U, and no R cell may change its code, at any stage. A cell may leave the
matrix only by a separate, recorded product decision by the lead, implemented in Python first with a release
note, so that the shadow comparison stays exact. Gate 2 requires an empty regression diff between the Python
column and the Lean/Rust column over S and R cells.

Known Lean gaps, from the code read for this revision, with their disposition:

| Gap | Python today | Lean today | Disposition |
|---|---|---|---|
| Norms with definitions or data flags | supported (`norm_admission.py` has no such gate) | `UnsupportedProfile` (`lean/VE/Norms/Wire.lean:201,203`) | **close in Lean before gate 4** (stage 2c; the largest schedule uncertainty) |
| Lemma bundles on the closure family | to confirm at stage 0 (`bundle.py` has no closure gate) | deferred (`lean/VE/Route/Run.lean:96`) | close in Lean if S in Python; otherwise not a loss |
| Admission on closure and order families; admission with definitions; citations without a bundle binding | `UnsupportedProfile` (`admission.py:429,431,471`) | `UnsupportedProfile` (`Run.lean:89,95,106,49`) | U in both: not a compatibility loss; remains a PLAN-EXPAND2 item |
| Search options and distinguishing models | supported | none; Rust absent | Rust extension, Lean validates witnesses |
| Traces | supported | none | Rust `--trace` with Python's schema and budget rule |
| Standalone parse, typing, environment, model, normalize; `evaluate` with source binding | supported | absent (section 2.1) | new glue modes |
| Graph report for `ve-argument-tableau@1` packages | Python composition | `Graph.checkTableau` without a package decoder | `graph` mode |
| `ve-argument-tableau@1` package decoder as a proved refinement | n/a | none | stays a PLAN-EXPAND2 §7 item; decoding is trusted and listed |
| English surface | Python | v0 unary/binary core skeleton, pretokenised | stays Python by decision |
| Long-running process; deterministic work budgets and counts | n/a; Python budgets | one-shot; unbudgeted reference evaluator | stage 1 service; Rust owns budgets (section 3) |

## 3. Stages and gates

### Stage 0: inventory, matrix, baseline (3–4 days, before any adapter design)

Deliverables: the dependency inventory (1.4); the support matrix (2.3) with its Python column filled; a frozen
**behaviour baseline** `conformance/baseline-2026-09/` holding Python's complete output for every matrix cell,
including rejection records and budget-boundary outcomes, generated by the current code and committed with the
generator's commit hash. This baseline is the reference for shadow (stage 3) and the independent oracle for
regenerated goldens (stage 5).

**Gate 0.** Inventory and matrix reviewed by the lead; every inventory row has a class and every A row names its
interface; every matrix S cell that Lean or Rust lacks has an owner and a stage-2 task; the baseline is committed
and replays byte-identically on a second machine.

### Stage 1: persistent Lean service (1.5–2 weeks)

Build one new executable `ve_service` from a new `lean/Serve.lean` that imports the existing runners
(`VE.Order.runEvaluationCaseReported`, `VE.CertificateWire.runCaseReported`, `VE.Order.Surface.runCaseReported`,
`VE.Route.Run.runCaseReported`, `VE.Norms.Run.runCaseReported`, `VE.English.Run.run`) and, as they land, the
section-2.1 glue modes. No existing file under `lean/VE/` changes.

Protocol (resolves the section-C clarifications):

- **Framing.** One JSON object per line. A request is `{"id", "mode", "cases": [...]}`; the response is
  `{"id", "results": [...]}` with results in request order, each `result` byte-for-byte the existing runner output
  for that case. A batch is the unit of timeout and cancellation; the adapter caps a batch at 256 cases or 4 MiB.
  The hard cap is 16 MiB per line as in Rust and the one-shot runners; an over-long or malformed line yields one
  error record for that line and processing continues. No state is kept between lines.
- **Handshake.** First line `{"service": "ve-lean@1", "lean": "4.24.0", "build": <sha256>, "modes": [...]}`;
  the adapter refuses a build not in `checkers.lock` unless explicitly overridden.
- **JSON.** The envelope and every case are decoded by the same restricted decoder the one-shot runners use
  (`VE.Json.parse`, depth 256, via `VE.JsonInput`); no second parser is introduced, so the rejections are the
  documented ones.
- **Dispatch.** Pinned by one theorem per mode, `dispatch m j = <runner> j`, so the statement review reduces to
  reading those lines; `audit.py` covers them.
- **Cancellation.** Out of band only: the Python supervisor (`ve/backends/lean_service.py`) kills the process on
  timeout, and the caller of the in-flight batch receives `CheckerUnavailable`. There is no in-band cancel. One
  retry on a fresh process for a killed batch (all requests are stateless); a second failure is
  `CheckerUnavailable`.
- **Timeout classification.** A wall-clock timeout, an address-space or RSS kill, a crash, EOF or a protocol
  error is `CheckerUnavailable`, an operational code that is never a verdict and never `ResourceLimit`.
  `ResourceLimit` is reserved for deterministic budgets: Rust's work budget, Python's structural caps in
  `limits.py` (which the adapter enforces before calling, exactly as today), and Lean's deterministic caps (node
  counts, identifier bytes, 16 MiB, depth). Revision 1's "second, non-deterministic `ResourceLimit` source" is
  withdrawn. The cost is that an in-cap input Lean cannot finish in time is unavailable rather than limited; the
  completion-rate gate in stage 3 measures that.
- **Supervision.** Address-space limit (default 4 GiB), per-batch timeout (5 s interactive, 60 s batch), restart
  on timeout, crash, EOF or protocol error, recycle after N requests or an RSS threshold, small pool, nonce ids
  that must match. A service failure never falls back to Python.

**Gate 1.** Byte-identical results against the one-shot executables on every conformance fixture, report
generator and the stage-0 baseline; a 20,000-request mixed-mode soak with RSS growth under 10% and no restarts;
fault injection (kill, hang, garbage output, truncated line, over-long line) fails closed; `audit.py` and the
hash test clean; the per-request latency gate of section 4 met on a quiet machine.

### Stage 2: adapters, new Lean modes, coverage closure, Rust extensions (4–6 weeks, overlaps stage 1)

**2a. Python adapters.** New package `ve/backends/` with `lean_service.py`, `rust_jsonl.py`, `dispatch.py`
(flag `VE_AUTHORITY=python|shadow|lean|rust-experimental`, default `python`, plus per-operation overrides
`VE_AUTHORITY_OVERRIDES=op=python,...`), `diagnostics.py`. Every class-A function gains an adapter with the same
signature and result type. Preservation obligations:

- **Schemas.** Every `to_dict` keeps its keys: `EvaluationResult` (`evaluations` carries Rust's work count,
  `explanation` Rust's trace), `CountermodelCheck`, `EntailmentCertificateCheck` (`steps` becomes the trace node
  count, documented), the `check()` record, admission reports, bundle rows, `ArgumentResult`. Snapshot tests pin
  them. Records gain `authority`, `assurance`, `covered_operations` and `trusted` (stage 4).
- **Identities.** As section 2.2: Python computes, Lean recomputes and rejects mismatches; only `checker_build`
  and the record ids derived from it change.
- **Diagnostics.** Lift the convention in `tests/test_p0_three_way.py` into `diagnostics.py`:
  `InvalidModel(<generator>)`, `UnsupportedProfile:`, `AdmissionError:`, `ResourceLimit:`, `DependencyCycle`,
  `DuplicateDeclaration`, `Definition …` map to the existing `VEError` codes; parse rejections carry Rust's code
  and span; anything else is `InvalidInput` with Lean's message. Codes are a zero-tolerance shadow class; message
  wording is recorded and changes land in one reviewed commit.
- **Traces and limits.** Rust `evaluate --trace` and search options as in 2.1. Exit codes 0/1/2/3/4 unchanged.
- **Failure modes.** Missing or mismatched binaries, crashes and timeouts surface as `CheckerUnavailable` with
  detail; there is no silent degradation and no inference of a Lean result from a Python one.
- **Rust-only operation is explicit.** `VE_AUTHORITY=rust-experimental` is chosen by the deployment (Colab,
  harness sandboxes); records carry `authority: rust` and `assurance: experimental`. It is never selected
  automatically: `VE_AUTHORITY=lean` with no Lean binary is `CheckerUnavailable`.
- **Batching.** `premise_status`, `check_readings`, `check_argument` and `check_step` send one batched request
  per operation instead of one per call, since a sentence check performs four to six authority calls.
- **Composition through Lean.** `check_argument` submits the package's nodes and root to `graph` and takes
  `composed`, the assumption list and `supporting_edge_ids` from the report; `check_readings` submits its verdict
  and evidence to `readings`. In `shadow`, Python's own composition runs too and any difference is a divergence.

**2b. New Lean glue modes** (`parse`, `normalize`, `check`, `environment`, `model`, `graph`, `identity`,
`route/evaluate` with `source`): new files, unfolding theorems, `audit.py`, statement review. 1–1.5 weeks.

**2c. Lean coverage closure.** Every matrix S cell Lean lacks: norms with definitions or data flags; closure
bundles if Python supports them. Lean agents, 1–2 weeks, uncertain; this item, not the adapters, sets the
critical path to gate 4.

**2d. Readings checker** `lean/VE/Route/Readings.lean` with its three soundness theorems. 1–1.5 weeks.

**2e. Rust extensions.** `--trace` with Python's budget rule, search options, distinguishing models. 1–2 weeks.

**Gate 2.** The full suite (1,059 tests, in the usual four chunks) passes under `VE_AUTHORITY=lean` for every
class-A operation, with fixture changes limited to `checker_build`, `record_id` and documented message wording;
the matrix's Lean/Rust column shows no S→R, S→U or code change against the Python column (an empty regression
diff; remaining Lean gaps are cells Python also lacks); adapter fault-injection tests; the inventory lint passes
(no retained module imports a class-A body); the `graph` mode is merged; the readings checker is merged or its
exclusion from `covered_operations` is recorded.

### Stage 3: shadow mode (1 week to build, then 14 consecutive clean days)

`VE_AUTHORITY=shadow` runs Python and Lean/Rust on every semantic call, returns Python's result, and appends a
divergence record `{op, input_digest, python, lean, rust, class}` to a JSONL log.

Classes with **zero tolerance:** `verdict`; `identity`; `diagnostic-code`; `schema`; `explanation` (trace
structure: `kind`, `value`, `detail`, children shape, compared once Rust `--trace` exists); `budget-outcome`
(the outcome class Satisfied/Violated/Found/NotFound/Valid/Invalid/ResourceLimit under the same nominal budget,
including trace exhaustion); `composition` (Python's leaf list versus Lean's report; Python's readings verdict
versus Lean's). Classes **recorded with bounds reported:** `diagnostic-message`; `count-value` (`evaluations`,
`steps`, `models_checked` differ by construction; the ratio distribution is reported); `latency`.

Corpora: the full suite; the stage-0 baseline (every matrix cell, including rejections and budget boundaries);
every conformance fixture and generator (evaluation 701, countermodels 708, parser 742, identity 706,
certificates 732 plus 150 forged, the closure, order, induction, admission, elaborated-document and norms
families, the 1,000-set definitions and 1,000-case data differentials, 85,000 English pairs); fuzz (5,000 core,
3,000 closure, plus a fresh 5,000-case seed nightly); the `usecases/` pilots through `ve document check`;
assist ledgers (tests, `experiments/authoring-gates/`, T1c); E1, P1 and iceberg validators; the web app API
tests. CI runs shadow on every merge. Triage rule: a Python deviant is a Python bug, fixed with a new
conformance case; a Lean glue or decoder deviant is fixed with statement review; a spec ambiguity gets a spec
note and a fixture. Any adapter or glue fix restarts the 14-day clock. Shadow also produces the performance data
for gate 4.

**Gate 3.** Zero divergences in the zero-tolerance classes on all corpora for 14 consecutive days; the
completion rate of section 4 is 100% over the accepted workload; count-value and latency reports attached.

### Stage 4: switch authority (3–5 days, packaging 1 week in parallel with stage 3)

Default becomes `VE_AUTHORITY=lean`; Python semantic functions become thin wrappers.

**Assurance is narrowed, per operation.** Every record carries `authority` (`lean`, `rust`, `python`),
`assurance`, `covered_operations` and `trusted`. `assurance: reference-theorems-checked` is granted only to
operations in a committed `docs/spec/theorem-coverage.md` that maps each operation to its theorems and to
`axioms.txt`. Initial list, to be confirmed by the Lean agents against the theorem table in `lean/README.md`:
evaluation (`eval_iff_denote`, `document_eval_iff_denote`); countermodel validity (`countermodelCheck_iff`,
`countermodel_sound`, admissibility from `decodeModel`); typing (`check_iff_wellFormed`); certificate replay for
v0, extended, closure, order and core (`checkCertificate_sound*`); the graph report (`Graph.check_sound`,
`check_entails`, `check_unfolds`, `tableau_certificateSound`); readings once `Readings.lean` is merged.
Explicitly **not** covered and labelled `experimental`: parse acceptance and canonical text (P1–P3 unproved
outside the propositional fragment), Background regeneration and definitions elaboration unless a theorem is
listed, `compare`, argument diagnostic statuses, the English surface, everything under `rust-experimental`.
Every record's `trusted` list names the JSON and wire decoding, SHA-256 identity, IO, compiler, display and the
Python class-C rules that produced any field on it, as the contract's evidence table requires.

**Rollback is per operation.** `VE_AUTHORITY=python` restores every operation that has a Python implementation.
Operations introduced Lean-only after the stage-2 rule (section 6) have no Python target: under `python`
authority they return `CheckerUnavailable`, never a verdict, and each such construct's release note says so.
Every release from stage 2 to stage 5 pins the Lean binary manifest and keeps the Python semantics, so any
release in that window is a compatible runtime for both authorities.

Packaging: one stripped `ve_service` (today's two binaries are 175 MiB each) built for linux-x86_64 and macOS
arm64 as release artefacts with a committed SHA-256 manifest, `lake-manifest.json`, toolchain and `axioms.txt`;
the adapter verifies the hash before use. Documentation: `implementation.md` trust section, `lean/README.md`,
`docs/rust.md`, `conformance/README.md`, ROADMAP status.

**Gate 4.** Gate 3 passed; performance gates in section 4 met from shadow data; packaging installed on a clean
machine and the suite passes there; `theorem-coverage.md` reviewed; **rollback rehearsed against new
artefacts:** create records under the new `checker_build`, including documents using any Lean-only construct
merged since stage 2, flip to `python`, and confirm that pre-existing operations return identical results,
Lean-only records return `CheckerUnavailable`, artefact identities are unchanged, and the old build reads the new
artefacts; the revert-one-merge path rehearsed as well.

### Stage 5: delete Python semantics, two-way conformance (1–2 weeks)

Delete every class-A body and class-D symbol from the inventory; keep the searchers, class-U helpers and surface
objects. Regenerate fixture goldens with Lean (`conformance/generate.py` and the report generators call the
service); Rust is checked against Lean-produced goldens, so the three-way families (`test_p0_three_way`,
`test_norms_three_way`, `test_data_three_way`, `test_nary_differential`, `test_definitions_differential`, Rust and
Lean conformance) lose their Python column.

**Independent expected results are preserved.** Today's README says golden truth values are produced by Python,
so Lean agreement is a differential check. After the switch, Lean would be checking Lean's own goldens. Therefore:
(i) the stage-0 baseline and the pre-deletion Python goldens are frozen under the tag `pre-semantics-deletion`,
following the `conformance/replay_baseline.py` pattern that extracts a pinned commit and never imports the
current checker; (ii) every regenerated Lean golden must be byte-identical to the frozen Python golden;
(iii) a new fixture after stage 5 needs the agreement of two independent implementations (Lean and Rust; for
parse diagnostics, Rust and the pinned `parser.json`), and a disagreement blocks the fixture; (iv) the frozen v0
replay regression stays as it is. The README sentence flips to "golden values are frozen from the pre-migration
Python at `<commit>` and extended only by two-implementation agreement". Malformed-package tests and
Rust-versus-Lean decoder fuzz stay, because both decoders remain unproved. One merge, one revert.

**Gate 5.** Suite green; a repository-wide import inventory (this repo, `ve-webapp`, `ve-bench`, `experiments/`,
sibling worktrees) shows no consumer of a deleted symbol, regenerated from the stage-0 script; regenerated
fixtures byte-identical to the frozen ones; the readings checker merged; `audit.py` clean; line-count and
binary-size report in the merge message.

## 4. Performance and compatibility gates (finding B3)

Measurement method, replacing "five repetitions": latency is a per-request distribution over a full replay of
the assist ledgers and the suite under `VE_AUTHORITY=lean` (at least 20,000 requests), in three independent
sessions on a quiet machine; p50, p95 and p99 are reported with 95% bootstrap confidence intervals and the gate
applies to the upper bound. The first 100 requests after a service start are reported separately as the
cold-start figure. End-to-end times are taken at the Python public-function boundary (for example `check_step`
entry to return), so IPC, JSON encoding and supervision are included. Document throughput is measured on each
distinct `usecases/` pilot document, 20 end-to-end runs in fresh sessions, never by repeating one fixture.
Batch figures use 30 repetitions with medians and intervals.

| Gate | Target | Baseline |
|---|---|---|
| IDE: `check_step` end-to-end p95 on the assist replay corpus, checker portion | ≤ 200 ms; no regression over Python for the same step, on the interval's upper bound | Python 1–12 ms per check; Lean one-shot 47–152 ms |
| Per authority call through the service | median ≤ 5 ms, p95 ≤ 20 ms; large certificate (2,047 nodes) p95 ≤ 200 ms | one-shot 85–116 ms medians, startup 87–96 ms |
| Pilot throughput: `ve document check` per `usecases/` document | median ≤ Python's; p95 ≤ 1.25 × Python's p95 for the same document | recorded in shadow |
| Batches | 2,048 definitions ≤ 1.0 s; 256 bundles ≤ 0.25 s; 256 conflicts ≤ 0.5 s; 8 large certificates ≤ 0.3 s | 0.995 s, 0.203 s, 0.468 s, 0.239 s one-shot |
| Search (Rust) | ≥ 10,000 searches/s on `search.json` batches | 22,145/s |
| Service footprint | cold start ≤ 150 ms once per session; ≤ 4 GiB per process; ≤ 2 processes for the IDE | startup 87–96 ms |
| **Completion rate** | 100% of cases that complete under Python within nominal budgets complete under Lean/Rust with the same outcome class, over the suite, the baseline, the corpora, the pilots and the assist ledgers; every `CheckerUnavailable` in shadow is triaged | n/a |
| **Budget boundaries** | the stage-0 boundary fixtures (each `limits.py` cap, `max_evaluations`, trace exhaustion at 10,000 nodes, tableau `max_steps`, 16 MiB) reproduce Python's outcome class and code | Python today |

## 5. Risks and rollback

| Risk | Mitigation |
|---|---|
| A Python-supported cell is lost (norms with definitions or data flags; closure bundles) | matrix rule: no S cell regresses; stage 2c closes the gaps in Lean before gate 4; pilot impact is information, not a criterion |
| Python still asserts a combined verdict | class-C table (1.2): graph and readings behind Lean interfaces; `compare` and diagnostic statuses trusted and labelled `experimental` with the rule named in `trusted` |
| Assurance overstated | per-operation `assurance` from `theorem-coverage.md`; parse acceptance stays `experimental` while P1–P3 are unproved; decoding, identity, IO, compiler, display listed as trusted on every record |
| Traces disappear | Rust trace mode with the identical schema and Python's budget rule; fallback keeps the Python tree as untrusted display whose root must equal Lean's verdict |
| Availability loss hidden by "resource divergence allowed" | outcome class is zero tolerance; only count values may differ; completion-rate gate; timeouts are `CheckerUnavailable` and triaged |
| Diagnostics lose spans or change wording | Rust spans for rejections; the mapping table; codes zero tolerance; wording changes in one reviewed commit |
| Interactive latency regresses | stage 1 before anything else; batching; per-request distribution gates with intervals; gate 4 blocks the switch |
| Service crashes, hangs, desynchronises, grows | nonce framing, batch timeouts, restart and recycling, address-space limit, fail-closed `CheckerUnavailable` |
| Unproved JSON boundary is mistaken for a verified one | `covered_operations` and `trusted` on every record; decoder fuzz and malformed-package tests retained |
| Lean-only constructs have no Python rollback | rollback is per operation; Lean-only records degrade to `CheckerUnavailable`, never a verdict; release notes say so; rehearsed at gate 4 with new artefacts |
| 175 MiB binaries, two platforms, Lean-less environments | release artefacts with hash pinning; `rust-experimental` is an explicit deployment choice, labelled |
| Hidden consumers of Python internals | stage-0 inventory with classes; class-U helpers kept; import lint from stage 4; import inventory at gate 5; one release of deprecation shims |
| Goldens lose independence when Lean generates them | frozen pre-deletion goldens; byte-identity required; two-implementation agreement for new fixtures |
| `checker_build` and `record_id` churn | expected and excluded from the shadow diff; artefact identities asserted byte-equal |
| Readings checker slips | gate 4 proceeds with `check_readings` excluded from `covered_operations`; gate 5 requires it |
| Expansion streams keep adding Python checkers | rule change at stage 2 (section 6) |

Rollback: through stage 4 the Python code is present and `VE_AUTHORITY=python` restores every operation that
ever had a Python implementation; per-operation overrides allow a partial rollback; stage 5 is one tagged merge,
reverted as a unit. Rust extensions and the Lean service are additive and need no rollback.

## 6. Effort and parallelism

| Stage | Effort | Calendar | Runs in parallel with |
|---|---|---|---|
| 0 inventory, matrix, baseline | 3–4 d | week 1 | nothing else starts before gate 0 except stage 1 |
| 1 service | Lean glue and protocol 4–6 d, supervisor 2–3 d, soak 1–2 d | weeks 1–3 | everything: new files only |
| 2a adapters | 2 wk | weeks 2–6 | everything: new package, flag off |
| 2b new Lean modes and identities | 1–1.5 wk | weeks 2–4 | 2a |
| 2c Lean coverage closure | 1–2 wk (uncertain) | weeks 2–5 | 2a, 2b; sets the critical path |
| 2d readings checker | 1–1.5 wk | weeks 3–5 | 2a–2c |
| 2e Rust extensions | 1–2 wk | weeks 2–5 | 2a |
| 3 shadow | 1 wk build, 14 clean days, ~1 d/wk triage | weeks 6–9 | everything: additive, and each expansion merge runs under it |
| 4 switch | 3–5 d plus 1 wk packaging | weeks 9–10 | needs a 2-day freeze on semantic modules |
| 5 delete | 1–2 wk | weeks 10–12 | after numbers round 2 and the W1 mixed-parity branches merge |

Total roughly 12–14 engineer-weeks over 12–13 calendar weeks (revision 1: 8–9 over 10–11). The increase is the
inventory and matrix, the section-2.1 modes and identities, the coverage closure and the readings checker. Team
fit follows PLAN-EXPAND2: Lean glue and the readings checker by the Lean agents with statement review, Python
and Rust by the Codex agents, shadow triage by the orchestrator.

Rule change from the start of stage 2, to be recorded in PLAN-EXPAND2 §2 and ROADMAP: no new Python semantic
code. New constructs (soft norms first, then rights, then causation) land as Lean checkers and elaborators
behind an adapter; Python contributes surface, IDE offering and proof search only. Consequence, stated
explicitly: such constructs have no Python rollback target; under `VE_AUTHORITY=python` they are
`CheckerUnavailable`, and their release notes say so. This removes one of three implementations from every
expansion immediately, before any deletion, and makes the three-way parity rule a two-way rule for new work.

## 7. Summary

Compiled Lean meets the 200 ms target for every ordinary check and beats Python by 2–30x in batches; only its
process startup and missing service mode keep Python's duplicate checkers alive. The plan first fixes the
compatibility contract (dependency inventory, operation × profile matrix, frozen behaviour baseline), then adds a
JSON-lines `ve_service` (no proved module touched, glue pinned by unfolding theorems, timeouts never verdicts),
then the standalone parse, typing, environment, model, identity, graph and readings interfaces Lean lacks, so
that every leaf verdict and every combined verdict that asserts a consequence is Lean's, then Python adapters
that preserve schemas, identities, codes, traces and budget outcomes, then a 14-day shadow soak with zero
divergence in verdicts, identities, codes, schemas, explanations, budget outcomes and compositions across the
suite, the baseline, all corpora, pilots and assist replays, then the switch with hash-pinned binaries,
per-operation assurance and per-operation rollback, and finally deletion of about 4,000 lines of Python
semantics with conformance frozen from pre-migration Python and extended by two-implementation agreement. Rust
takes search and budgeted evaluation; Python keeps the English surface, IDE, web app, CLI, harnesses, proof
search and semantics-free orchestration. Stages 1–3 run alongside expansion work; from stage 2 no new Python
semantics is written.

## 8. Response table (finding → change)

| Finding | Change | Where |
|---|---|---|
| A: Python remains a semantic authority (graph composition, readings ALL/NONE); checking edges does not validate the graph or retained assumptions | Class L / class C split; graph composition moved behind a `graph` mode over `VE.Graph.checkTableau` (assumption list is Lean's report); readings behind a new `Readings.lean` checker with soundness theorems; `compare` and diagnostic statuses retained as trusted with `assurance: experimental` and named in `trusted` | 0, 1.2, 2.1, stage 2a, stage 4 |
| A: P1–P3 and graph-wire refinement unproved; compiled execution cannot upgrade combined acceptance | `assurance` granted per operation from `theorem-coverage.md`; parse acceptance and decoding stay `experimental`/trusted and are listed on every record | 0, stage 4 |
| A: Gate 2 `UnsupportedProfile` allowance conflicts with gate 3 zero divergence; pilot impact is not compatibility | Operation × profile × input-class matrix with the no-regression rule; gate 2 requires an empty regression diff; Lean gaps enumerated with dispositions; norms with definitions or data flags closed in Lean before gate 4 (stage 2c); pilot impact demoted to information | 2.3, stage 0, stage 2c, gate 2 |
| A: Lean-only expansion defeats universal flag rollback; rehearse rollback on new artefacts; retain a compatible runtime | Rollback defined per operation with explicit `CheckerUnavailable` degradation for Lean-only constructs; every release pins both runtimes until stage 5; gate 4 rehearsal creates and rolls back new artefacts | stage 4, 5, 6, 9 |
| B: Runner wrappers do not expose promised operations; legacy evaluation needs a model; route evaluation lacks source binding | Mode table with `parse`, `normalize`, `check`, `environment`, `model`, `graph`, `readings`, `identity` and `route/evaluate` with `source`; each wraps a named proved function with its theorem coverage | 2.1, stage 2b |
| B: Lean lacks recomputation of `source_id`, `model_id`, `claim_id`, `edge_id` | Identity table: Lean adds those four via the `identity`, `parse`, `model` and `graph` modes; `graph_id` and record ids stay Python and are declared trusted | 2.2 |
| B: Deletion classifications ignore shared helpers (`order.py:622`, `closure.py:225`, `norm_strict.py:9`); inventory belongs before adapter design | Dependency-level "kept" column; class A/U/S/D inventory generated by `tools/semantic_inventory.py` as a stage-0 deliverable and gate-0 criterion; import lint; deletion estimate revised from 5,000 to about 4,000 lines | 1.1, 1.4, stage 0, gate 2, gate 5 |
| B: Stable keys do not preserve counts, explanations, codes or budget outcomes; resource divergence can hide availability loss (`evaluate.py:194`) | Shadow classes `explanation`, `budget-outcome`, `composition` added at zero tolerance; codes zero tolerance; counts recorded with ratio reports; Rust `--trace` adopts Python's `min(max_evaluations, max_trace_nodes)` rule; boundary fixtures; completion-rate gate; timeouts triaged | 2.1, stage 0, stage 3, section 4 |
| B: Latency sampling, warmup and end-to-end timing undefined; five repetitions weak; repeated-fixture throughput is not document performance | Per-request distributions over ≥ 20,000 requests in three sessions with bootstrap intervals; cold start reported separately; timing at the Python API boundary; per-document pilot runs in fresh sessions | 4 |
| B: Preserve independent expected results when changing golden generators | Frozen pre-deletion goldens and baseline under a tag; byte-identity of regenerated goldens; two-implementation agreement for new fixtures; README wording | stage 5 |
| C: Batch framing, restricted JSON, cancellation, timeout classification, Rust-only operation | Protocol section: `cases`/`results` framing and caps, same restricted decoder, out-of-band cancellation with one retry, timeouts and kills are `CheckerUnavailable` only, `rust-experimental` is an explicit deployment choice | stage 1, stage 2a |

## 9. Disagreements

1. **The "no new Python semantics" rule stays, and universal flag rollback is not a goal for new constructs.**
   The review treats Lean-only expansion as defeating rollback. For a construct that never had a Python
   implementation there is nothing to roll back to; a flag flip can only make it unavailable, which is what it
   was before the construct shipped. The plan therefore defines rollback per operation, makes the degradation
   explicit (`CheckerUnavailable`, never a verdict) and rehearses it, rather than requiring a Python twin of
   every new construct, which would recreate the duplication this plan removes.
2. **Cells that Python itself reports as `UnsupportedProfile` are not compatibility losses.** Admission on the
   closure and order families, admission with definitions and citations without a bundle binding raise
   `UnsupportedProfile` in Python today (`admission.py:429,431,471`) exactly as in Lean. They leave the
   loss list and stay PLAN-EXPAND2 items. Norms with definitions or data flags, where Python has no such gate,
   are a real loss and are closed in Lean before gate 4.
3. **Work counts are not preserved; outcome classes and completion rates are.** `evaluations`, `steps` and
   `models_checked` differ between Rust's accounting and Python's by construction. Pinning their values would
   require re-implementing Python's evaluator step for step in Rust. The plan pins the outcome class under the
   same nominal budget, the boundary fixtures and a 100% completion rate, and reports the count ratios.
4. **Argument diagnostic statuses remain Python.** `CheckerConflict`, `ContradictoryPremises`, `Incomplete`,
   `ResourceLimit` and `InvalidInput` combine Lean-checked findings but assert no consequence; the record they
   appear on is `proof: not_checked`. A Lean interface for them would be a decoder for Python's diagnostic record
   with no theorem to attach. They are declared trusted display in `trusted`. The composed verdict and the
   assumption list, which do assert consequences, come from Lean.
5. **Wall-clock limits are operational, not `ResourceLimit`.** The review asked for a consistent choice; the
   plan chooses `CheckerUnavailable` for every non-deterministic failure and withdraws revision 1's
   non-deterministic `ResourceLimit` source. This costs the ability to report "limited" for an in-cap input Lean
   cannot finish in time; the completion-rate gate measures how often that happens before the switch.
