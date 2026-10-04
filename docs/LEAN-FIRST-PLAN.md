# Lean first: one owner for every piece of VE logic

**Status:** draft 1, 2026-10-04, branch `design/lean-first` (from `main` at `f4142cb9`). Planning only: no code,
proof or test changes. Measurements in section 3 were taken on this commit; the scripts are in
[`docs/lean-first/`](lean-first/).

**Directive (lead, 2026-10-04).** No logic is duplicated across Python, Lean and Rust. Each piece of logic lives in
exactly one language, and the others call it. Python and Lean today duplicate validation, diagnostics, semantics and
English conditions, and that duplication causes most review findings
(`~/code/manage-agents/FINDING-CLASSES.md`: about 27% of implementation findings and 30% of fix cost sit in
cross-language logic; features with duplicated implementations average 6.6 fix rounds against 3.4).

<!-- SUMMARY -->

## 1. Ownership rules

1. **Lean owns every decision about meaning or acceptance.** That covers decoding and validation (including the
   order in which faults are reported), diagnostic codes and texts, limits, verdicts, elaboration, conflicts,
   statuses and their folds, coverage counts, admission, identities (which fields are hashed), and, once the
   english-lean work lands, the one-reading English parse.
2. **Python relays and displays.** A Python entry point reads files, sends the input to the Lean service, and
   either returns Lean's answer or raises Lean's diagnostic verbatim (code and text, no rewording, no prefix
   stripping). Python raises its own errors only for operational failures (`CheckerUnavailable`), CLI usage and file
   I/O. **Lean validates, Python constructs:** Python builds its containers (`Environment`, `FiniteModel`, documents)
   only from input Lean has accepted; a constructor that fails after Lean accepted is a bug, reported as
   `CheckerUnavailable`. Python keeps the CLI, the views and markdown, the web app API, `ve assist` and other editor
   help (ambiguity hints, lexicon proposals), harnesses and adapters.
3. **Generators are allowed once, untrusted.** Proof search (tableau, order, closure induction, norm conflicts),
   situation search for readings and model search propose evidence. Each kind lives in one language; Lean checks
   every proposal before it is reported; an exhausted or refused proposal is `UNKNOWN` or `CheckerUnavailable`,
   never a verdict.
4. **Rust is a search accelerator only.** It keeps countermodel and distinguishing-model search, whose witnesses
   Lean checks (non-vacuity included, see batch 15). Rust's parser, validators, route, evaluator and the statement
   layer differentials are deleted. Rust decodes only input Lean has already accepted; a Rust rejection of such
   input is `CheckerUnavailable`, and no Rust text reaches a user.
5. **Wire primitives are the one accepted exception.** Each language that speaks the wire keeps its restricted JSON
   reader, canonical JSON writer and SHA-256, because they are the protocol itself. They are specified by
   `docs/spec/v0-language.md` and pinned by shared test vectors. What they are applied to (the identity preimage of
   an environment, model or meaning) is Lean's: Python reads identities from Lean's answers.
6. **No new Python semantics** (already the migration plan's rule from stage 2): a new profile or construct is
   written in Lean, with a Python relay and display. This replaces wire-contract S10 ("contract first").

What these rules do not change: proofs and frozen identities stay as they are; the relay is the stage-1 service's
threat model (`docs/spec/lean-service.md`): the client checks binding and well-formedness of every response and
never re-derives content.

## 2. Inventory: duplicated logic and its single owner

Sources: four read-only sweeps of `ve/`, `lean/`, `rust/` on this commit, cross-checked on the cited lines.
"Decides today" gives the default authority (`VE_AUTHORITY` unset, which is `python`:
`ve/backends/dispatch.py:61`) and then `VE_AUTHORITY=lean`. Line counts are deletable Python estimates; the batch
numbers refer to section 5. Sizes today: `ve/` 39,194 Python lines, `lean/` 87,722 Lean lines, Rust 7,654 lines.

### 2.1 Envelopes, kernel and core operations

| Logic | Python today | Lean | Rust | Decides today (default / lean) | Single owner | Python deleted | Batch |
|---|---|---|---|---|---|---|---|
| Environment envelope, vocabulary, profile gate and family dispatch | `environment.py` `_decode` 346–714; `profiles.py` 48–143 | `Route/Gate`, `Route/Wire.decodeVocabulary`, per-route `profileGate`; `Compose/Dispatch.lean` `todayGate` ("a transcription of `ve/profiles.py`", `lean/COMPOSE.md:34`) | `environment.rs` (third validator) | Python / both must accept, Python's text wins when both reject (`ve/backends/validation.py:108-135`) | Lean | ~490 | 12 |
| Statement-block decoders inside the environment: alternatives, risk, speech scope, units, W1 act phrases | `environment.py:157-302, 370-377, 607-655`; `risk.py:70-215` ("mirrors", `risk.py:3`); `speech_acts.py:26-115`; `units.py:88` | `Alternatives/Wire.lean:78`, `Risk/Wire.lean:189`, `SpeechActs/Wire.lean:71`, `Time/Wire.lean:548`, `Norms/Wire.lean:24-82` | `units.rs`, `risk.rs` (tests only) | Python / Python | Lean | ~700 | 5, 9, 11, 12 |
| Model validation | `model.py` `_decode` 102–216 | `model` mode; `decodeModel_valid` proved | `model.rs` | Python / both | Lean | ~100 | 12 |
| Parse and canonical text | `parser.py` 387–415, `grammar.py`, `printer.py` | `parse` mode over `VE.Surface`, `Closure/Core/Order.Surface`; round trip proved, grammar P1–P3 not | `surface.rs`: a third parser with no runtime caller | Python / both; only Python has spans and specific messages (Lean: one generic "SyntaxError: the source is not accepted by the Lean surface parser", `lean/VE/Service/Standalone.lean:541`) | Lean | ~250 | 13 |
| Typing | `ast.py` `_Checker` 215–325 | `check` mode, `check_iff_wellFormed`; `Service/TypingDiagnostic.lean` copies Python's messages, including Python `repr` | `ast.rs` | Python / Lean | Lean (its wording becomes the spec) | ~110 | 13 |
| Definitions, Background, dependency order, labels | `definitions.py`, `background.py`, `admission.py:99-125` | route `background`, `dependency-order`, `label` | `environment.rs`, `route.rs` (tests only) | Python / Lean, definitions both | Lean | ~290 | 13 |
| Bundles | `bundle.py` | route `bundle`, `FamilyBundle` (`bundle_sound`) | — | Python / both | Lean | ~60 | 13 |
| Norms elaborate, certificate, conflict; norms admission | `norms.py` (constructor 201–262 and `check_witness` 467–488 are not dispatched), `norm_admission.py` | `ve_norms_route`, `family-norms` mode; soundness proved | — | Python / Lean in scope | Lean | ~280 | 13, 14 |
| Route admission | `admission.py` `_admit_document_python` 493–579 | route `admission`, `runAdmission_sound` | — | Python / Lean | Lean | ~500 | 13 |
| Argument graph and statuses | `argument.py` 251–345, 412, 625–727 | `graph` mode, `GenericGraph.check_sound` | — | Python / Lean only when Python says "composed" (`argument.py:588`) | Lean | ~150 | 13 |
| Readings ALL/SOME/NONE, W2 set structure, couplings | `readings.py` 125–270, 288–386, 445–508 | `readings` mode (three soundness theorems); no couplings, narrowings or W2 set decoding (`lean/READINGS.md:146`) | — | Python / Lean confirms; couplings and joint choices stay Python | Lean | ~250 | 14 |
| Evaluation (value, budget, trace) | `evaluate.py` `_Evaluator`, also called directly by `search.py`, `norms.py`, `cedar.py`, `model.py`, `readings.py` | route and legacy `evaluate`; `eval_iff_denote`; no work budget (`Service/Protocol.lean:33-35`) | `eval.rs`, `order.rs` | Python / Rust computes, Lean checks the value only; counts, traces and `ResourceLimit` are Rust's alone | Lean (budgeted evaluator) | ~180 | 15 |
| Countermodel check | `search.py` 149–229 | `countermodelCheck_iff`, `countermodel_sound` | `search.rs` | Python / Rust then Lean | Lean | ~40 | 15 |
| Countermodel and distinguishing search, non-vacuity | `search.py` 259–640, 740–812 | none; no non-vacuity predicate | `search.rs`: the same generator | Python / Rust proposes; non-vacuity checked only by Python (`search.py:471-537`) | Rust (untrusted), Lean checks witnesses and non-vacuity | ~560 | 15 |
| Certificate replay, binding prechecks, step budget | `entailment.py` `_Replayer` 615, `_check_certificate_python` 798, prechecks 709–760; `order.py`; `closure.py` | `checkCertificate_sound*` | — | Python / Lean for validity, Python prechecks and budget | Lean; the provers keep their own internal replay as generator code | ~300 | 13 |
| `premise_status`, `compare`, attacks | `vacuity.py`, `equivalence.py`, `attacks.py` | constituents only | — | Python rule over Lean-checked parts | Lean (small rule) | ~30 | 13 |
| Assist decisions | `assist/session.py` `_decide` 330–367 treats the prover's unreplayed `Found` as yes; `proposer.py:312` `_entails` | none | — | Python | Lean replay (generators stay Python) | 0 (rewire) | 18 |
| Cedar adapter allow/deny | `adapters/cedar.py:264-278` (`_Evaluator` + `NormDocument.outcome`) | none dispatched | — | Python | Lean | 0 (rewire) | 18 |
| Identities | `identity.py`, `wire.py`; every container recomputes its id | every route recomputes ids | `environment.rs`, `model.rs` | Python, compared with Lean where Lean answers | Lean computes; Python reads ids from answers | small | 12, 13 |

### 2.2 Statement layers and documents

| Profile / logic | Python today | Lean | Rust | Decides today | Single owner | Python deleted | Batch |
|---|---|---|---|---|---|---|---|
| Readings S1 (`readings@1`) | `readings_s1.py` (1,470): a full regeneration that must equal Lean's answer byte for byte (`readings_route.py:90-118`) | `Readings/Run.lean:176` | `readings.rs`, compared with Python at runtime | Lean (Python must agree or `CheckerUnavailable`) | Lean | ~1,530 | 3 |
| Discourse (`ve-document@2`) | `discourse.py` `python_discourse` 1016–1266, resolution 258–700, joint checks 166–229 | `Discourse/Run.lean:137`, `Admission.lean:739` | `discourse.rs` (tests) | Lean; Python's text kept when both reject (`discourse.py:1379-1395`) | Lean | ~1,190 | 4 |
| Risk block and route | `risk.py:70-215` | `Risk/Wire.lean`, `Run.lean:557-590` | `risk.rs` evaluator, tests only | Python decodes the environment; semantics already relayed (`risk.py:226-241`) | Lean | ~200 | 5 |
| Alternatives block, `AlternativesReserved`, coverage folds | `environment.py:194-302` (the reserved-wording check at 207–211 exists only in Python); `document.py:789-850` | `Alternatives/Wire.lean`, `Decl.lean:198`, `Run.lean:254` | — | Python decodes; semantics relayed | Lean | ~170 | 5 |
| Soft norms | `softnorms.py` phases 93–535, semantics 718–1065; `softnorms_contract.py` (317); `wire_contract/engine.py` (520); `soft_route.py:34-84` regeneration compare | `SoftNorms/Wire.lean`, `Soften.lean`, `Coherence.lean`, `Run.lean`; `ve_diagnose` | — | **Python's rejection is final; Lean is never asked** (`soft_route.py:126-136`) | Lean | ~1,700 | 6 |
| Rights | `rights.py` (596) correlation and decoding; `rights_route.py:39-102` byte comparison; unit statuses `document.py:509-547` | `Rights/Correlate.lean`, `Run.lean:332`, `Admission.lean:315` | — | Python builds first, so its rejections are final; the five-question report is Lean's | Lean | ~650 | 7 |
| Reports and attribution | `reports.py` 115–614, status folds 49/294/339, `residual_lines` 616 | `Attribution/Run.lean:466`, `Status.lean`, `Admission.lean:232`; no residual lines (`lean/REPORTS.md:233-235`) | — | both computed, compared on 8 fields (`reports_route.py:35-41`) | Lean | ~510 | 8 |
| Quantities, units, time | `units.py` (649), `quantity_admission.py` (318), `surface/count.py` | `Time/Wire.lean`, `Time/Document.lean` (`ve_quantity`), `Time/Count.lean` | `units.rs` (tests) | **Python by default** (`admission.py:443-444, 504-507`) | Lean | ~900 | 9 |
| Norm defaults (`unspecified`) | `norm_defaults.py` (1,087), `norm_defaults_route.py` | `NormDefaults/Run.lean`, `Evidence.lean`, `Tree.lean`; no reached witnesses, `UngroundedDefault` or soft/rights branches | — | **Python only at runtime**; the Lean route is called from tests | Lean | ~1,100 | 10 |
| Speech acts | `speech_acts.py` 498–1057, `speech_document.py` (501), wording checks 97–323 | `SpeechActs/Tree.lean`, `Run.lean:505`; no 8.5 wrapper or admission, no answer, compliance or nomination records (`lean/SPEECH-ACTS.md:145-159`) | — | **Python only at runtime** (`ve speech-acts` never calls Lean) | Lean | ~1,400 | 11 |
| Document wrapper `@1`, unit statuses, coverage and residual counts | `document.py` 343–602, 747–944, `_report` 1043–1243 | none (manifest `document.check` has `lean: null`) | — | Python only | Lean (new `document` mode) | ~900 | 17 |
| Diagnostics plumbing | `backends/diagnostics.py:15-28` (strips Lean's prefixes so texts match Python's), ~1,517 `raise …Error(` sites, `errors.py` | ~1,100 `"Class: …"` literals; only the soft route emits a `code` field | — | mixed | Lean codes and texts, one Python class per code | ~150 | 0 |
| Limits | `limits.py` (13 constants, imported by 24 files) | ~28 named limits by hand (`maxNodes 10000` six times), 69 inline literals, 4 generated values | 6 `MAX_*` | duplicated | Lean (one `VE/Limits.lean`) | small | 19 |
| One-shot transports | `backends/lean.py` (270): six bespoke runners | 14 one-shot executables, 168–173 MiB each | — | — | the service | ~250 | 1 |

### 2.3 English

| Logic | Python today | Lean | Decides today | Single owner | Batch |
|---|---|---|---|---|---|
| Formula-level English parse and one-reading audit | `english.py` `EnglishParser` (886), `surface/unambiguity.py` (Lark Earley, 30 s wall-clock limit) | `VE/English/Parse.lean` (core fragment, `core_one_reading` proved), off the admission path; branch `english-lean/lean` (generic table parser, S1a/S1b proved) | Python (`assurance-manifest.json` `english.admission`: `authority: python`) | Lean (english-lean) | E1–E3 |
| Lexing and normalisation | `english.py:122, 165` | branch: `EnglishGrammar/Lexer.lean` | Python | Lean | E1 |
| Vocabulary lint (18 codes) | `printer.py`, `english.py:230-538`, `english_vocabulary.py` | `English/Check.lean` (narrower, harness only); branch `Lexicon.valid` V1–V5 | Python | Lean for the 10 meaning-relevant codes; the 8 reader-protection codes are DRI question 5 | E2 |
| Statement-layer English (norm rule blocks, norm-default legends, reports, speech, quantities, definitions, risk, soft norms, rights) | `norm_english.py`, `norm_defaults_english.py`, `report_english.py`, `speech_english.py`, `surface/*.py` (~2,500 lines) | none | Python, and it decides acceptance | Lean, one layer at a time after E2 | E3 |
| Display sentences | `rights.py:503-530`, `readings_english.py` | `Rights/Wire.lean:332-357`, risk legend `Risk/Run.lean:421-452` | built in both and compared (`rights_route.py:39-90`) | Lean emits, Python displays | 7, 5 |
| Render, then re-parse | `english.py:809-856` | `English/Render.lean`, `core_parse_render` | Python at runtime | Python renders as an untrusted producer; Lean re-parses each output | E2 |
| Ambiguity hints, OEWN lexicon, fluent and natural views, gloss lint | `assist/ambiguity_patterns.py`, `lexicon/`, `fluent.py`, `natural.py`, `speech_english.py:40-87` | none | Python (editor help, display) | Python | — |

### 2.4 Python-only decisions with no Lean counterpart yet

These are the places where deleting Python would lose a feature, so each needs Lean work before its batch can
delete anything:

- soft-norm report lines `Overlap`, `override_cycles`, `DualGuardCycle` (`lean/SOFT-NORMS.md:201`); soft status and
  weighing points (`document.py:851-868`);
- reports residual lines and status text, `BridgeHolder`, `MissingBridgeRecord`;
- norm-defaults reached witnesses, `UngroundedDefault`, soft and rights branches;
- speech-act 8.5 wrapper, admission, answer, compliance and nomination records;
- readings couplings, narrowings and W2 set structure; the ALL/SOME/NONE verdict for coupled and joint choices;
- the `AlternativesReserved` check; coverage and residual blocks for soft norms, rights and alternatives;
- the `@1` document wrapper, unit statuses and coverage counts;
- stage 2c gaps: `definitions@0` surface sugar, non-first-order norm guards on the closure, core and order
  families, n-ary core definitions, W6 quantity typing;
- certificate binding prechecks and the replay step budget; non-vacuity of search witnesses; evaluation budgets,
  counts and traces;
- Lean parse diagnostics with spans (Lean's parse rejection is one generic message today);
- every statement-layer English parser.

### 2.5 Drift found while taking the inventory

These are concrete instances of the class the directive targets, found by reading both copies (not run):

- **W1 act phrases:** Python's reserved words include `no` (`ve/environment.py:28`); Lean's copy does not
  (`lean/VE/Norms/Wire.lean:25-27`, also `VE/Surface.lean:67`). An act phrase containing "no" is rejected by
  Python and, as far as the code shows, accepted by Lean.
- **Quantity admission:** the docstring says Lean is the authority (`ve/quantity_admission.py:12`); by default
  Python decides (`ve/admission.py:443-444`).
- **Risk admission routing:** `admission.py:508` sends any environment with an alternatives block, risk included,
  to `ve_alternatives_route`, while Lean's dispatch routes risk first.
- **Manifest staleness:** `soft.elaborate` says "No implementation exists in any engine"
  (`ve/assurance-manifest.json:650-665`); both Python and Lean implement it.
- The unmerged differential fuzzer (`infra/difffuzz`, `conformance/DIFFFUZZ.md`) baselines 138 live
  disagreements in 13 groups (DF-1 to DF-13): diagnostic codes, texts and fault order between Python, Lean and Rust
  on environments, models, labels, block routes and Unicode. Every one of them disappears by construction once
  Python relays Lean's diagnostic and Rust's texts are never shown.

## 3. Measurements: how fast is calling Lean?

### 3.1 Method and conditions

- **Commit** `f4142cb9` (this branch's base). Lean built with `lake build` (560 jobs; the build matches
  `lean/checkers.lock`), Rust with `tools/rust_build.py` (hash pinned).
- **Host:** AMD EPYC 7B12, 32 logical CPUs, shared with other workers. The one-minute load average was **57–88**
  throughout (another worker ran the full suite at `-n 16`). Wall times are therefore inflated, roughly 3–5× against
  a quiet machine; every table also gives the checker's **CPU time**, which load inflates much less. The quiet
  reference is the Gate-1 run on `8bf11607` (`experiments/lean-service/latency-8bf1160/LATENCY.md`): service call
  p50 0.75–1.43 ms and p95 1.2–2.4 ms, cold start 41 ms, one-shot 45–54 ms.
- **Tools** (`docs/lean-first/`): `hook/sitecustomize.py` records every Lean one-shot process, service request and
  service start, and every Rust process a VE process makes, with wall and CPU time and the calling `ve` function;
  `measure.py` times start-up, the conformance corpora and document steps and aggregates the records;
  `dump_readings_case.py`, `separate_case.py` and `count_answer.py` isolate the UDHR readings call. Raw records are
  not committed; the commands are in each script's docstring.
- **Authorities.** "Python authority" is today's default. "Lean authority" is `VE_AUTHORITY=lean` (Stage 2's
  adapters: Lean decides the class-A operations, Rust evaluates and searches). Statement-layer routes (soft norms,
  rights, readings, alternatives, quantity and so on) run as one-shot Lean processes under both.

### 3.2 Start-up against per call

| What | Wall p50 / p95 (load ~70) | CPU p50 | Note |
|---|---:|---:|---|
| One-shot route executable, empty batch (14 executables, 20 runs each) | 257–501 ms / 342–2,492 ms | 74–107 ms | each binary is 168–173 MiB; 2.4 GiB in total |
| Service start, spawn to handshake (20 runs) | 233 / 302 ms | — | quiet: 41 / 43 ms; plus the client's SHA-256 of the binary, 144 ms quiet, once per process |
| Service start inside the agent-policy harness (6 workers × pool of 2, 13 starts) | 818 ms / 10.1 s (max 11.6 s) | — | starts contend with each other and with the host |
| Service call, Stage-0 probe matrix (19,558 calls) | 1.0–3.5 ms / 2.8–7.4 ms by mode | 0.5–1.6 ms | table 3.3 |
| Rust call, one process per case (6,161 calls) | 6.0 / 12.5 ms | 3.2 ms | a new process for every evaluation and search |

**Reading:** a one-shot Lean process costs about 0.1 s of CPU before it does any work, 50–150 times a service
call. Every statement-layer route is one-shot today, so every soft-norm, rights, readings, quantity or alternatives
check pays it.

### 3.3 Per operation on the conformance corpus

The Stage-0 probe matrix under Lean authority (`tools/stage2_parity.py --authority lean`; 9,384 cells, 0
regressions, 0 different, as recorded in `docs/spec/stage2-parity.md`). Every request carried a single case.

| Service mode | Calls | Wall p50 / p95 / max ms | Lean CPU p50 / p95 ms |
|---|---:|---:|---:|
| `check` (typing) | 6,708 | 1.33 / 4.37 / 124 | 0.79 / 1.14 |
| `route` (Background, admission, labels, evaluation, countermodels) | 5,624 | 1.21 / 4.20 / 99 | 0.48 / 1.04 |
| `norms` | 4,523 | 1.54 / 4.48 / 53 | 0.66 / 1.24 |
| `model` | 1,305 | 1.58 / 4.86 / 2,314 | 0.98 / 1.48 |
| `parse` | 476 | 0.95 / 4.17 / 1,877 | 0.50 / 0.75 |
| `family-norms` | 240 | 1.45 / 2.77 / 7 | 0.73 / 2.01 |
| `environment` | 235 | 1.02 / 4.18 / 19 | 0.53 / 0.94 |
| `graph` | 122 | 1.68 / 4.82 / 10 | 1.01 / 1.77 |
| `readings` | 118 | 2.36 / 5.03 / 6 | 1.58 / 2.18 |
| `bundle` | 102 | 1.18 / 2.77 / 5 | 0.74 / 1.07 |
| `evaluate` | 61 | 1.24 / 4.59 / 11 | 0.60 / 0.84 |
| `order` | 29 | 3.52 / 7.37 / 8 | 0.62 / 0.91 |
| `check-certificate` | 15 | 1.26 / 3.61 / 8 | 0.81 / 1.51 |
| **all Lean** | 19,558 | total 39.9 s | total 17.7 s |
| Rust (separate processes) | 6,161 | 5.96 / 12.49 / 119 | 3.15 / 4.36 |

The two maxima are the boundary probes: a 1.5 MB model (`MAX_TUPLES`) and a 76 KB source (`MAX_SOURCE_BYTES`).

Whole conformance files through the service (one warm process):

| Corpus | Cases | One `ve_conformance` process | Service, one request per case: sum (p50) | Service, batched |
|---|---:|---:|---:|---:|
| `evaluation.json` (4,912 formulas) | 701 | 3.75 s (1.43 s CPU) | 3.61 s (5.1 ms) | 2.28 s (1.03 s CPU) |
| `countermodels.json` | 708 | 1.69 s (0.71 s CPU) | 1.51 s (1.5 ms) | 1.06 s (0.50 s CPU) |
| `closure.json` (866 formulas) | 46 | 1.07 s (0.42 s CPU) | 0.70 s (12.0 ms) | 0.87 s (0.26 s CPU) |

**Reading:** on the conformance corpus Lean is fast enough everywhere: about 1 ms of Lean CPU per operation and a
few milliseconds of wall time even on a loaded host. Batching saves a further 30–40%.

### 3.4 Use-case documents and pilots

`ve document check` (or the use case's own harness) under each authority. "Lean share" is the time spent in Lean
calls.

<!-- DOCS-TABLE -->

### 3.5 The UDHR pilot: one Lean call

<!-- UDHR -->

## 4. Where calling Lean is fast enough, and the fixes where it is not

<!-- FIXES -->

## 5. Plan: ordered batches

Each batch is 2–6 hours of build work for one worker (review rounds come on top) and does three things: it
switches the callers to the single owner, it **deletes** the duplicate in the same merge, and it keeps behaviour
under the lean-first gate below. Python features are deleted only after Lean has them (port first, then delete), so
no batch removes a capability unless the DRI accepts it by name.

### 5.1 The lean-first gate (every batch)

1. **Suite.** The full suite at the batch head (in chunks, `VE_NATIVE_PREBUILT=1`); test changes limited to the
   batch's listed wording and order changes.
2. **Corpus A/B.** `tools/lean_first_diff.py` (batch 0) runs the base commit and the batch head over the same
   corpora and compares every public result: verdict, diagnostic code and text, fault order, identities, counts.
   Corpora: the Stage-0 probe matrix (9,384 cells); the conformance fixtures (evaluation 701, countermodels 708,
   parser 742, identity 706, validation 43, closure 46, the certificate cohorts); the batch profile's own corpora
   (for example the 1,000-document rights differential, the 1,000 soft-norm trees, the norm-defaults
   differential); the differential fuzzer's CI sample (7,500 mutants) and **14 date seeds at once**; the use-case
   harnesses with their answer keys; and **every historical pilot document** (the `pilot/udhr-*` and `pilot/cc-*`
   branches hold about 30 runs with their companion documents). The result must be identical, or every change is
   listed in the batch's `DELTA.md`, classed `wording`, `order`, `verdict` or `availability`. Wording and order
   lists are signed as one block, as wire-contract S4 did for its 498 text changes; each verdict or availability
   change needs a DRI signature.
3. **Deletion ledger.** The planned Python lines are gone; every deleted Python raise site is mapped to the Lean
   check that now reports it, or to a DRI-accepted drop. `tools/relay_lint.py` (batch 0) fails if a relayed module
   raises a content diagnostic of its own, and the stage-0 inventory script shows no consumer of a deleted symbol.
4. **Latency.** The batch's operations stay inside the section-4 budgets, measured on the same corpus run.

### 5.2 Batches

| # | Batch | Lean work | Python and Rust deleted | Hours |
|---|---|---|---|---:|
| 0 | **Relay foundation.** One Python entry, `ve/backends/relay.py`: `decide(mode, cases)` returns Lean's rows or raises the `VEError` subclass of Lean's code with Lean's text verbatim; `CheckerUnavailable` only for operational failures. `tools/lean_first_diff.py` (built from mig3/py's recorder M3.1 and `tools/shadow_gate.py` M3.4) and `tools/relay_lint.py`. Freeze the pre-deletion Python under a tag for the oracle (section 6.2). | The service adds `code` to every rejection row, derived in one Lean function from the runner's `Class:` prefix, so no frozen runner changes | the prefix-stripping tables in `backends/diagnostics.py` (Python texts that imitated Lean's are replaced by Lean's own) | 4–6 |
| 1 | **Every route in the service.** Service modes for the 12 one-shot executables (soft norms, rights, speech acts, reports, alternatives, risk, risk eval, quantity, norm defaults, discourse, readings, diagnose), each pinned by an `rfl` theorem like `runMode_route`, with binding schemas; Gate-1 byte parity against the one-shot runner on each route's corpus. Per-operation deadlines replace the flat 5 s interactive limit (F4). | glue in `VE/Service/` | the six bespoke transports of `backends/lean.py`; the one-shot executables leave `defaultTargets` (2.4 GiB of binaries become one 170 MiB service) | 4–6 |
| 2 | **Service throughput.** Content-addressed environment handles (F2), one request per document for typing, route and norms calls (F3), and Rust as one persistent JSON-lines process instead of one process per case (F6). | handle table in the service (a miss is a bound request error; the client resends) | per-call environment re-encoding in the adapters | 3–5 |
| 3 | **Readings S1.** `readings_route.validate` relays Lean's row; per-set requests across the pool. | F5: admit the document once (`Admitted.D` is recomputed per pair today), cache per-set answers by digest | `readings_s1.py` (1,470), `rust_check`, `readings.rs` | 4–6 |
| 4 | **Discourse.** `rejection` always returns Lean's diagnostic; joint-choice checks come from Lean's `gateChoices`. | none | `python_discourse`, resolution, joint checks (~1,190), `discourse.rs` | 2–4 |
| 5 | **Risk and alternatives blocks.** Environments with these blocks are validated by their routes; coverage folds come from `alt-elaborate`; admission routes risk first, as Lean's dispatch does. | port `AlternativesReserved`; coverage counts in `alt-elaborate` | `_alternatives_block`, `risk.decode_block`/`check_block` (~370), `risk.rs` | 3–4 |
| 6 | **Soft norms.** Lean is asked first; Rust's soft premises come from Lean's answer. | add soft status, weighing points and the `Overlap`, `override_cycles`, `DualGuardCycle` lines to `soft-elaborate` | `softnorms.py` phases and semantics (~800), `softnorms_contract.py` and `wire_contract/engine.py` (837), the regeneration compare | 4–6 |
| 7 | **Rights.** `rights_route` relays; unit statuses and display sentences come from Lean. | unit statuses in `rights-elaborate` | `RightsDocument` correlation (~550), the byte comparison, `document.py` rights status block | 4–6 |
| 8 | **Reports.** Meaning ids, statuses and residual lines from Lean. | residual lines and status text, `BridgeHolder`, `MissingBridgeRecord` | `ReportsDocument` elaboration and folds (~510) | 4–6 |
| 9 | **Quantities.** `ve_quantity` decides by default; W6 typing goes to Lean. | W6 typing in the `check` mode | `units.py` validation and elaboration (~580), `quantity_admission.py` (318), `units.rs` | 4–6 |
| 10a | **Norm defaults, Lean side.** | reached witnesses, `UngroundedDefault`, soft and rights branches | — | 4–6 |
| 10b | **Norm defaults, switch.** | — | `norm_defaults.py` (~1,000), Python admission (~105) | 3–4 |
| 11a | **Speech acts, Lean side** (replaces wire S6). | 8.5 wrapper and admission; answer, compliance and nomination records | — | 4–6 |
| 11b | **Speech acts, switch.** `ve speech-acts` and `speech_document.py` call the route. | — | `speech_acts.py` and `speech_document.py` semantics (~1,400) | 3–5 |
| 12 | **Environments, models and the profile gate.** Lean validates, Python constructs. Needs batch 2's handles, since environment construction is the hottest call. Ends the env-profiles finding class and DF-1 to DF-13. | none (the decoders exist) | `Environment._decode` and model validation (~590), `profiles.py` gate (~110), `validation.decided` | 4–6 |
| 13a | **Core diagnostics in Lean.** | parse diagnostics with spans (Python `_Parser`'s messages move into Lean); order-family printer; certificate binding prechecks and step budget | — | 4–6 |
| 13b | **Core operations default to Lean.** Typing, parse, definitions, Background, bundles, norms, admission, graph, readings, premise status, compare. | none | the Python bodies (~2,000), the `shadow` path | 4–6 |
| 14a–d | **Stage 2c gaps**, one batch each: `definitions@0` sugar; non-first-order norm guards; n-ary core definitions; coupled reading sets and joint choices. | the four extensions | each Python fallback branch | 4 × 3–5 |
| 15a | **Budgeted evaluation and non-vacuity in Lean** (DRI question 2). | a metered evaluator with Python's charging rule (counts, `ResourceLimit`, traces); a non-vacuity check | — | 4–6 |
| 15b | **Evaluation and search switch.** Rust keeps search only. | — | `_Evaluator` (rewire `norms`, `cedar`, `readings`, `model`), Python search (~560); Rust `surface.rs`, `route.rs`, `eval.rs`, order evaluation, `units.rs`, `risk.rs`, `discourse.rs`, `readings.rs` (about 4,000 of 7,654 Rust lines) | 4–6 |
| 16a | **Document wrapper, Lean side.** A `document` mode: front matter, unit spans and schema, MIXED parts, status inference and fold, coverage and residual counts. | new | — | 4–6 |
| 16b | **Document switch.** `document.py` keeps file I/O and display. | — | ~900 lines of `document.py` | 3–5 |
| 17 | **Assist and adapters.** `_decide` and `_entails` replay through Lean before answering yes; Cedar decisions through Lean evaluation. | none | 0 (rewire) | 2–3 |
| 18 | **Cleanup.** One `VE/Limits.lean` (six copies of `maxNodes` today); Python reads I/O caps from the service handshake; one Python error class per Lean code; the `python` authority and `VE_AUTHORITY_OVERRIDES` removed; the assurance manifest updated. | limits module | `limits.py` duplicates, dispatch shadow, manifest `python` entries | 2–4 |

**English track** (separate workers, in parallel with batches 3–18; the plan is `docs/spec/english-lean-PLAN.md`
on `design/english-lean`):

| # | Batch | Change |
|---|---|---|
| E1 | english-lean S2–S3 (in flight) | the English grammar instance and profiles in Lean |
| E2 | `english.admission` to Lean | S5 directly, on corpus evidence (the 85,000 English pairs, use cases and pilots) instead of S4's 14-day shadow; `EnglishParser` acceptance and the Lark one-reading audit are deleted in the same batch (S5 and S7 merged). The Lark grammar for editor diagnostics is generated from Lean's grammar data and never decides acceptance. |
| E3 | statement-layer English, one profile per batch | after that profile's batch above: norm rule blocks, norm-default legends, reports, speech, quantities, definitions, risk, soft norms, rights |

**Why this order.** Batches 0–2 make relaying cheap and fast. Batches 3 and 4 are deletions where Lean already
decides, so behaviour cannot change by construction (Python had to agree with Lean or fail), and they remove the
most lines per hour. Batches 5–9 flip profiles whose Lean route already exists. Batches 10–11 port missing Lean
features first. Batches 12–13 flip the core, the largest blast radius, after the throughput work. Batches 14–16 add
the remaining Lean, and 17–18 clean up. Total: 26 batches, roughly 100–120 build hours, plus the English track.

**Expected result.** About 14,000 of the 39,194 Python lines deleted by batch 18 (about 3,500–3,900 core, about
9,000–10,000 statement layers, about 1,000 backends and wire-contract engine), and about 5,000 more with the English
track (`english.py`, the Lark audit, about 2,500 lines of statement-layer English). Rust shrinks to search, about
3,000 lines.

## 6. What happens to the other plans

### 6.1 Wire contract (S4–S10)

- **S6–S9 are cancelled** and replaced by relaying Lean's diagnostics: S6 (`speech-acts@0`) by batch 11; S7
  (`alternatives@0`, `risk@0`) by batch 5, which is already the relay pattern S7 itself chose (it defers to
  `ve_diagnose`); S8 (`rights@0`, `reports@0`, `ve-units@1`) by batches 7, 8 and 9; S9 (`ve-document@1`, `@2`,
  discourse) by batches 4 and 16.
- **S4 items 2–6** (Rust engine, `json@0`, `envelope@0.2`, `vocabulary@0.2`, `formula@0.2`, `model@0.2`) are
  cancelled. Their purpose, that Python and Rust report faults in Lean's order with Lean's codes, is met by batch 12
  (Python shows Lean's diagnostic) and rule 4 (Rust's texts are never shown).
- **S5** (`norms@0`, `norm-defaults@0` contracts in shadow on `wire-s5/integrate`) is stopped and not merged. Its
  S5-pre verdict differences (2 for norms, 6 for norm defaults) become inputs to batches 10 and 13b: each is
  resolved by adopting Lean's verdict or porting Python's behaviour into Lean, by DRI ruling.
- **Kept:** the merged Lean engine, the generated `soft-norms@0` table and `ve_diagnose` stay as Lean's own
  diagnostic table for soft norms; the Python engine and hooks go in batch 6. **S10** ("contract first") is
  replaced by rule 6 ("Lean first").

### 6.2 The migration plan's stages 3–5 and the 14-day shadow

- **The 14-day calendar soak is replaced by corpus evidence per batch** (gate item 2) plus a short operational
  soak. Reasoning: under mig3's definition a clean day is one complete nightly run of fixed corpora. The only inputs
  that change from day to day are the date-seeded fuzz seed and new pilot runs, so 14 days add 14 seeds and about
  28 pilot documents. Batch gates run 14 seeds at once and every historical pilot document, so the same evidence
  arrives in hours. What a calendar does add is operational: leaks, RSS growth, timeouts under real load. That is
  covered by the Gate-1 soak (60,000 requests in three sessions) and by **three days of the nightly suite and the
  pilots after batch 13b**, counting timeouts, crashes and `CheckerUnavailable`, not divergences.
- **The comparison changes shape.** Shadow compared Python and Lean inside one process. Batches compare the base
  commit with the batch head over the same corpora (A/B by commit), which measures exactly the batch's behaviour
  change and keeps working after the Python copy is deleted.
- **mig3:** stop the `mig3/py` build where it is and reuse its recorder (M3.1) and `tools/shadow_gate.py` (M3.4) as
  the A/B tool. Open questions: q2 (order of the 2c gaps against the 14 days) becomes batches 14a–d, each with its
  own evidence; q3 (timeouts) is answered by measurement (section 3.4: the flat 5 s limit fails under load) and
  batch 1's per-operation deadlines; q6 (shadow in CI on every merge) is dropped.
- **Stage 4 rollback** by `VE_AUTHORITY=python` disappears operation by operation as batches delete the Python
  copy. Rollback becomes reverting one batch merge, which the one-merge-per-batch rule keeps possible.
- **Stage 5** is spread over the batches. Its independent-oracle rule is kept: before batch 3 the pre-deletion
  Python is frozen under a tag and run in isolation (the `conformance/replay_baseline.py` pattern) to give new
  fixtures an `oracle: lean+pinned-python` label inside the frozen language.

### 6.3 english-lean

Kept, and on the critical path for the one-reading guarantee (the lead's P0 of 2026-10-03). Two changes: S4's
14-day shadow becomes corpus evidence (batch E2), and S5 (authority) and S7 (retire `EnglishParser` and Lark) merge
into one batch, so Python's parser never runs beside Lean's as a second authority. The test-only Python reference
implementations (`conformance/english_lean_{engine,lexer,lexicon}.py`) are deleted once Lean's engine is the only
one; until then they are test oracles, not shipped logic. The vocabulary lint's eight reader-protection codes are
DRI question 5.

### 6.4 Rust

Rust becomes an untrusted search accelerator: countermodel and distinguishing-model search, whose witnesses Lean
checks, with non-vacuity checked in Lean (batch 15a). Deleted: the third parser and printer (`surface.rs`, no
runtime caller today), `route.rs` (tests only), the statement-layer differentials (`units.rs`, `risk.rs`,
`discourse.rs`, `readings.rs`) and, once Lean has a budgeted evaluator, `eval.rs` and the order evaluator. This
follows the lead's earlier "don't pursue Lean search or retire Rust now": Rust stays for the one job where it is
18× faster than Python. Python's own model search (`search.py`, ~560 lines), the duplicate generator, is deleted.
`infra/layers2-b2` (R1–R3, the crate split) is not merged; splitting a 3,000-line search crate is not worth it.

### 6.5 Other in-flight work

- **Layers plan 2:** Python items P11–P19 and P17 move and re-wire Python duplicates of Lean checks; they are
  cancelled. Lean L1–L9 continue. The 25 adapter edges disappear with the adapters.
- **Consolidation (`infra/consolidate-b1`):** continues. It applies "one owner" inside Lean and shrinks the trusted
  base that every relayed answer now depends on.
- **Differential fuzzer (`infra/difffuzz`):** merge it as the record of today's 138 disagreements. Batch by batch
  its Python column goes away and the baseline must shrink to zero for each relayed surface. It stays as the
  relay's type-confusion fuzzer (only `VEError` or `CheckerUnavailable` may escape) and as the Lean-versus-frozen-
  Python oracle.

## 7. Risks and what we lose

1. **The live cross-check.** Two implementations catch each other's bugs, and Python has caught Lean decoder bugs:
   the dependency-order route accepts an empty vocabulary (DF-8), the risk route accepts an NBSP act phrase that
   Python rejects (DF-12), Lean accepts duplicate `protected` rights entries that Python rejects
   (`ARCH-ROADMAP.md`), and the act-phrase `no` drift above. Lean's envelope and vocabulary decoders are not proved
   (`lean/README.md`). After deletion such a bug reaches users with no second opinion. Mitigations: the frozen
   Python oracle for new fixtures; decoder specifications and theorems for the envelope and vocabulary decoders
   first; the fuzzer against Lean alone with spec-derived expectations; review attention moves to Lean decoders.
2. **Worse messages for a while.** Lean's parse rejection is one generic sentence, and some decoder texts expose
   internals (`String expected`). Each surface switches only after its Python messages are ported (batch 13a, E2),
   but every batch changes texts users and tests have seen; each change is listed and signed.
3. **Performance where Lean is slower today** (section 3): the agent-policy harness and the UDHR pilot are slower
   or fail under Lean today. Batches 1–3 are prerequisites for flipping anything with a large environment or many
   readings. The IDE path is fine: a service call costs 1–2 ms at the median.
4. **Lean build and review friction.** A wording change becomes a Lean rebuild (9 minutes from scratch on a quiet
   machine, more than an hour at today's load), a frozen-hash rehash and an audit. More work needs Lean-capable
   workers, and Lean glue needs statement review. The bet is that this costs less than the 6.6-against-3.4 fix
   rounds that duplication costs now.
5. **Deployment.** Every install needs the 170 MiB service binary; the web app and IDE must ship it (macOS arm64
   packaging is not done). There is no Python-only mode by design.
6. **Rollback is coarser.** No runtime switch back to Python after a batch; only reverting its merge.
7. **Silent loss of uncovered behaviour.** The corpus A/B sees only covered inputs. The deletion ledger (every
   deleted raise site mapped to a Lean check) is the guard.
8. **The English move is the largest single risk**: the Lean chart parser's speed on pilot-sized documents is not
   measured yet (english-lean S0 still owes token lengths for use cases and pilots).

## 8. Questions for the DRI

1. Replace the 14-day calendar soak with per-batch corpus evidence plus a three-day operational soak after batch
   13b? Recommended: yes.
2. Rust evaluation: delete it and give Lean a budgeted evaluator (batch 15a), or keep Rust as the untrusted
   producer of budgets, counts and traces? Recommended: delete, if 15a's evaluator stays within the per-call budget.
3. Wording: Lean's texts become canonical everywhere, with Python's better texts ported into Lean where users see
   them (parse errors, the readability evaluation's items)? Recommended: yes.
4. Stop the `mig3/py` build and reuse its recorder as the A/B tool? Recommended: yes.
5. The vocabulary lint's eight reader-protection codes: Lean acceptance checks, or Python editor warnings that
   never reject?
6. Act-phrase `no`: adopt Python's list in Lean as a signed change? Recommended: yes.
7. Keep a frozen pre-deletion Python as a test oracle (one isolated environment to maintain)? Recommended: yes.
8. `soft-norms@0` contract: keep generating Lean's table from the JSON contract, or fold it into Lean source?
   Recommended: keep until batch 18, then decide.
9. Start order: batch 0–2 first, or batch 3 (readings, which also fixes the UDHR pilot's timeout) first?
   Recommended: 0, then 3 and 1 in parallel, then 2.
