# Lean first: one owner for every piece of VE logic

**Status:** draft 2, 2026-10-04, branch `design/lean-first` (from `main` at `f4142cb9`). Planning only: no code,
proof or test changes. Measurements in section 3 were taken on this commit; the scripts are in
[`docs/lean-first/`](lean-first/).

**Directive (lead, 2026-10-04).** No logic is duplicated across Python, Lean and Rust. Each piece of logic lives in
exactly one language, and the others call it. Python and Lean today duplicate validation, diagnostics, semantics and
English conditions, and that duplication causes most review findings
(`~/code/manage-agents/FINDING-CLASSES.md`: about 27% of implementation findings and 30% of fix cost sit in
cross-language logic; features with duplicated implementations average 6.6 fix rounds against 3.4).

**Summary.** (1) A warm Lean service call costs **1–3.5 ms wall, 0.5–1.6 ms Lean CPU** (p50, 19,558 conformance
calls): fast enough for every interactive and corpus use. (2) With a real 5 KB environment a call costs **4 ms of CPU,
90% of it re-decoding the environment** (0.38 ms with an empty one; batching does not help), so the agent-policy
harness takes **883 s under `VE_AUTHORITY=lean` against 162 s today** (identical answers; 61,695 single-case
requests, 22,533 Rust processes). (3) One-shot routes cost **~0.1 s CPU each before any work**. (4) The **UDHR pilot
cannot load under either authority**: its one readings call needs **1,161 s CPU against a 120 s limit**, 62% of it
admission at about 4 s per candidate, and Python's byte-for-byte regeneration adds 938 s, 918 s of it one-shot Lean
rights calls. (5) Lean authority checks the use-case documents in 1.4–9 s (26× faster than Python on bluedot) but
**refuses 3 of 4 constitution-pilot documents** (`norm-defaults@0`, `readings@1`). Fixes F1–F6 (section 4) come
before the switches. Plan: 26 batches, ~100–120 build hours, ~14,000 Python lines deleted (~19,000 with English).

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
- the core profile registry (`lean/VE/Route/Gate.lean:46-55`, 9 profiles against Python's 17): under
  `VE_AUTHORITY=lean`, environments with `norm-defaults@0` or `readings@1` are refused (section 3.4);
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
  for sections 3.2 and 3.3 (another worker ran the full suite at `-n 16`) and **21–74** for sections 3.4 and 3.5
  (2026-10-04, 07:59–09:20 UTC). Wall times are therefore inflated, roughly 3–5× against
  a quiet machine; every table also gives the checker's **CPU time**, which load inflates much less. The quiet
  reference is the Gate-1 run on `8bf11607` (`experiments/lean-service/latency-8bf1160/LATENCY.md`): service call
  p50 0.75–1.43 ms and p95 1.2–2.4 ms, cold start 41 ms, one-shot 45–54 ms.
- **Tools** (`docs/lean-first/`): `hook/sitecustomize.py` records every Lean one-shot process, service request and
  service start, and every Rust process a VE process makes, with wall and CPU time and the calling `ve` function;
  `measure.py` times start-up, the conformance corpora and document steps and aggregates the records (`report
  --by-op` per document); `dump_readings_case.py`, `separate_case.py`, `count_answer.py` and `regenerate_case.py`
  isolate the UDHR readings call and Python's regeneration of it; `env_cost.py` measures the environment's share of
  a service call. Each Lean call of sections 3.4 and 3.5 was bounded at 30 minutes; none reached the bound. Raw
  records are not committed; the commands are in each script's docstring.
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

`ve document check` (`measure.py document check`, one process per authority, so the service is warm after the first
document) or the use case's own harness, under today's default authority and under `VE_AUTHORITY=lean`. "Lean" is
the checker's own CPU in Lean calls with the number of calls (service requests and starts, one-shot processes);
"Rust" likewise. The service's 5 s and Rust's 5 s limits were raised to 300 s for these runs (`VE_LEANFIRST_TIMEOUT`)
so that every run could be timed; the failures they cause at the normal limits are in the notes. The default
columns ran with `VE_AUTHORITY` unset for the harnesses and the alternatives document and with `VE_AUTHORITY=python`
for the other documents, which is the same for documents without alternatives or risk blocks: set explicitly,
`python` refuses those two routes (`ve/alternatives.py:27-28`, `ve/risk.py:235-236`), unset it calls them.

| Workload | Size | Default: wall | Default: Python / Lean (calls) / Rust CPU | Lean: wall | Lean: Python / Lean (calls) / Rust CPU | Note |
|---|---:|---:|---|---:|---|---|
| bluedot `causal.ve.md` | 6.7 KB | 0.13 s | 0.02 / 0.10 s (1 one-shot) / – | 1.77 s | 0.36 / 0.23 s (5) / – | Lean wall includes the service start |
| news `news-w6a.ve.md` | 52 KB | 4.53 s | 3.86 / – / – | 1.47 s | 0.35 / 0.20 s (26) / 0.27 s (5) | |
| bluedot `document.ve.md` | 147 KB | 232 s | 225 / – / – | 9.02 s | 2.02 / 0.63 s (50) / 4.07 s (1) | Python's model search against Rust's; at Rust's 5 s limit the Lean run failed (`CheckerUnavailable`, earlier run, load 57) |
| constitution pilot `translation.ve.md` | 424 KB | 1.48 s | 0.91 / – / – | refused | – | `UnsupportedProfile: Unsupported profile norm-defaults@0` |
| constitution pilot `readings/s1.ve.md` | 415 KB | 8.79 s | 5.00 / 1.08 s (4 one-shot) / 0.14 s (34) | refused | – | `… readings@1` |
| constitution pilot `readings/all-strict.ve.md` | 378 KB | 12.05 s | 10.76 / – / – | refused | – | `… norm-defaults@0` |
| constitution pilot `readings/all-default.ve.md` | 345 KB | 0.79 s | 0.26 / 0.33 s (3 one-shot) / – | 1.43 s | 0.39 / 0.50 s (31) / 0.01 s (3) | |
| UDHR companions, 25 documents | 1.4–7.6 KB | p50 0.012 s, p95 0.093 s | 0.42 / 0.37 s (5 one-shot) / – in total | 5 checked, p50 0.29 s | 0.47 / 0.46 s (107) / – in total | 20 of 25 refused (`norm-defaults@0`) |
| UDHR `translation.ve.md` (load) | 869 KB | fails at 120 s | ≈ 2,550 s with the limit lifted, 98% of its CPU in Lean (section 3.5) | refused in 1.1 s | – | `… readings@1` |
| agent-policy `check.py base` (6 workers) | 26 rules, 42 actions | 162 s | all Python (389 s CPU), 0 Lean calls | 883 s | Lean 387 s (61,695 requests + 8 starts) / Rust 95.5 s (22,533 processes) | identical results (42/42, same policy summary); at the 5 s limit the Lean run failed after 353 s (earlier run) |
| eligibility `run.py --no-write` (6 workers) | 80 profiles | 1,155 s | Lean 214 s (26 one-shot `ve_quantity`, about 9,400 cases, up to 8.4 MB) | 1,417 s | Lean 312 s: the same one-shots 181 s + 22,707 service requests and 13 starts, 131 s | both 269/269 and 32/32 mutants |

**Reading.**

- **Single documents are fast enough under Lean.** Where Lean authority answers, its Lean CPU is 0.2–0.63 s per
  document, and the bluedot document drops from 232 s to 9 s because Rust's search replaces Python's.
- **Lean authority cannot check the pilots.** Lean's core profile registry (`lean/VE/Route/Gate.lean:46-55`) has 9
  profiles, Python's (`ve/profiles.py:19-37`) 17. The statement layers Python strips before calling Lean are not
  affected, but `norm-defaults@0` and `readings@1` reach Lean's `environment` mode and are refused, although Lean's
  composed dispatch (`Compose/Dispatch.lean`) routes both. This is a gap for batch 12, not a speed problem.
- **Many-call harnesses are not fast enough under Lean.** Agent-policy: the same 42/42 answers in 5.5× the time.
  Phase by phase (the harness's own `policy_seconds`): pairs 36.9 → 342.3 s, rules 1.0 → 29.3 s, tool gaps 53.9 → 70.6
  s. Every one of the 61,695 Lean requests carried one case (typing 23,150, evaluation route 13,819, Background
  12,199, norms 8,714, model 1,261, certificate replay 1,256) and the whole environment again: 542 MB of JSON. Lean
  CPU per call was 3.4–6.8 ms (p50; 16.6 ms for certificate replay) against 0.5–1.6 ms on the conformance corpus;
  the client's response checks add 104 s; and every evaluation starts a Rust process (13 ms wall, 4 ms CPU).
  Eligibility pays the same overhead on 22,707 requests (+23% wall), and its own replay costs 19–23 ms of Lean CPU
  per case because each case carries the 10 KB environment.
- **The environment is most of the cost of a call.** `env_cost.py` (300 calls each, load 74): a trivial typing call
  (`check` of `top`) costs **4.05 ms** of Lean CPU with the agent-policy environment and **0.38 ms** with an empty
  one; decoding the environment alone (`environment` mode) costs 4.07 ms; sending 300 such cases in one request
  costs 4.05 ms per case, so batching without environment handles saves nothing.

### 3.5 The UDHR pilot: one Lean call

`document load` of the UDHR translation (pilot run `20261003T0600Z`, 869 KB, 50 reading sets) makes one
`readings-validate` call to the one-shot `ve_readings_route` with a fixed 120 s limit (`ve/backends/lean.py:247`),
then regenerates the answer in Python and compares the two byte for byte (`ve/readings_route.py:90-118`). The case
was captured with `dump_readings_case.py` (500 KB) and run directly, cut to its first 1, 5 and 10 sets, and as one
`readings-separate` query (`separate_case.py`), each bounded at 30 minutes:

| Request | Content-bearing sets | Candidates | Pairs | Input | Lean wall | Lean CPU |
|---|---:|---:|---:|---:|---:|---:|
| `readings-separate`, one pair, first set only | 1 | 4 | 1 | 40 KB | 26.0 s | 21.1 s |
| `readings-validate`, first set | 1 | 4 | 12 | 40 KB | 29.8 s | 24.3 s |
| `readings-validate`, first 5 sets (earlier run) | 5 | 16 | 40 | 61 KB | 283.8 s | 97.2 s |
| `readings-validate`, first 10 sets | 10 | 30 | 72 | 85 KB | 171.3 s | 161.2 s |
| `readings-separate`, one pair, whole document | 39 | 176 | 1 | 500 KB | 836.7 s | **721.0 s** |
| `readings-validate`, whole document | 39 | 176 | 734 | 500 KB | **1,389.0 s** | **1,161.4 s** |
| Python's regeneration (`readings_s1.answer`, `regenerate_case.py`) | 39 | 176 | 734 | | 1,159.5 s | Python 28.5 s, Lean 918.2 s (352 one-shot `ve_rights_route`), Rust 2.4 s (734) |

Lean's answer and Python's regeneration were byte-identical. Peak memory 96 MB.

**Reading.**

- **The call does not finish anywhere near its limit:** 1,161 s of CPU against 120 s, so on a quiet host too
  `document load` is `CheckerUnavailable` under the default limit, whichever authority is set. With the limit lifted
  the load is the Lean call plus Python's regeneration, run one after the other: about **2,550 s** at this load,
  98% of its CPU in Lean.
- **The cost is per candidate, not per pair.** Lean CPU fits about **4.1 s per candidate plus 0.6 s per pair**
  (within 8% on all four validate rows). A query about one pair costs 721 s on the whole document because
  `readings-separate` admits the whole document first (`lean/VE/Readings/Run.lean:182-186`); admission is 62% of
  the full call. The answer then builds each candidate's document `one D s i` again, separately for its row and for
  its chain findings (`Run.lean:63, 73`). Where inside admission the time goes is not profiled yet.
- **The unit of work is a whole-document rights elaboration.** Each candidate's rights document is 28 KB: the whole
  document with that one reading. Python's regeneration asks Lean for it twice per candidate, `rights-scope` (2.2 s
  CPU p50) and `rights-elaborate` (2.9 s CPU p50). For comparison, the constitution pilot's 105 KB soft-norm
  document goes through `ve_soft_norms_route` in 0.14 s CPU, start-up included, so the rights chain is the step to
  profile.
- **Python's regeneration is not a cheaper second opinion.** Its own work is 28.5 s; the other 918 s are the same
  Lean rights chain called again as 352 separate processes.

## 4. Where calling Lean is fast enough, and the fixes where it is not

**Fast enough today, no fix needed:**

- **Interactive and IDE calls.** One service call is 1–3.5 ms wall and 0.5–1.6 ms of Lean CPU at the median on the
  conformance corpus, even at load 70 (section 3.3); 0.75–1.43 ms on a quiet host (Gate 1).
- **Corpus and gate runs.** The conformance files run through the service as fast as through `ve_conformance`, and
  batched 30–40% faster (section 3.3).
- **Single documents.** Where Lean authority answers, a use-case or pilot document costs 0.2–0.63 s of Lean CPU and
  1.4–9 s of wall time, Rust's search included (section 3.4). Small statement-layer documents (the UDHR companions)
  check in 12 ms at the median under the default authority.

**Not fast enough, with the fix.** F1 to F6 are the fixes the batches of section 5 refer to. Gains marked
*measured* follow from section 3's numbers; gains marked *estimate* are to be measured by the batch that builds the
fix.

| # | Problem (measured) | Fix | Expected gain | Batch |
|---|---|---|---|---|
| F1 | Every statement-layer route is a one-shot process: about 0.1 s of CPU and 0.25–0.5 s of wall at this load before any work (section 3.2). A small document's soft-norm check is almost all start-up (0.07 s CPU for a 1 KB document). 14 executables, 2.4 GiB. | Service modes for the 12 one-shot routes, in the one persistent service. | *Measured:* −0.1 s CPU and −0.25–0.5 s wall per route call (about −0.3 s CPU on the constitution pilot's `s1` check, which makes 4); one 170 MiB binary instead of 2.4 GiB. | 1 |
| F2 | The environment is re-sent and re-decoded on every call: a trivial typing call costs 4.05 ms of Lean CPU with the agent-policy environment and 0.38 ms with an empty one, and decoding that environment alone costs 4.07 ms; 542 MB of JSON in one agent-policy run. | Content-addressed environment handles: the first request registers the environment, later requests name its digest; a miss is a bound request error and the client resends. | *Estimate:* Lean CPU per agent-policy call from 3.4–6.8 ms to the conformance corpus's 0.5–1.6 ms, so 387 s to about 40–100 s for the harness and 131 s to about 15–35 s for eligibility; the JSON volume and the client's 104 s of response checks shrink with it. | 2 |
| F3 | Callers send one case per request (61,695 requests in one agent-policy run). | One request per document or per prover step for typing, route and norms calls. Only useful after F2: batching alone saved nothing with a real environment (4.05 ms per case). | *Measured on the conformance corpus:* −30–40% wall; *estimate* for harnesses after F2: per-call wall from 10–13 ms to 1–2 ms. | 2 |
| F4 | Flat wall-clock limits: under load the service's 5 s limit stopped the agent-policy harness after 353 s and Rust's 5 s limit stopped the bluedot document (a 4.1 s CPU search); the readings route's flat 120 s is 10× below what the UDHR call needs on any host. | Per-operation deadlines, set from measured CPU per operation and input size (in CPU time where the platform allows), and reported as `CheckerUnavailable` with the operation named. | Removes failures caused by host load; an input that needs more than its operation's deadline fails saying which operation. | 1 |
| F5 | The UDHR readings call: 1,161 s CPU; 62% is admission, about 4.1 s per candidate, each a whole-document rights elaboration (2.2–2.9 s CPU per 28 KB); Python then repeats the chain in 352 one-shot calls (918 s CPU). | (a) Delete Python's regeneration and its rights calls. (b) Build each candidate's `one D s i` at most once per request and reuse it wherever the answer needs it (today its row and its chain findings build it separately). (c) Elaborate the shared base once and each candidate's own unit as a delta, with a lemma that the result equals `one D s i`. (d) Profile and speed up the rights chain (`limitationScope`, `noDistinction`, key generation). (e) Run independent sets in parallel across the service pool. | (a) *measured:* load from about 2,550 s to about 1,390 s wall, CPU −45%. (b)–(d) *estimate:* admission's 176 whole-document elaborations become one plus 176 deltas; the target is the 120 s budget on a quiet host, about 10× below today. (e) *estimate:* wall ÷ pool size (39 independent sets). | 3 |
| F6 | Every Rust evaluation is a new process: 22,533 in one agent-policy run, 13 ms wall and 4 ms CPU each, 328 s of summed wall. | Rust as one persistent JSON-lines process per worker, like the Lean service. | *Estimate:* about 1 ms per call, so 328 s to about 25–40 s. | 2 |

Two further costs are small but paid by every CLI process: the service start (233 ms at load 70, 41 ms quiet) and
the client's SHA-256 of the 170 MiB service binary (144 ms quiet), once per process. Caching the binary's digest by
path, size and modification time removes the second; a per-user resident service would remove both, but is not
needed for any measured workload.

**Budgets** (the latency item of the batch gate, 5.1 item 4). Measured on the batch's corpus run against the base
commit at the same time, comparing CPU where the host is loaded:

| Operation class | Budget |
|---|---|
| One service call, interactive modes | p50 ≤ 2 ms Lean CPU, p95 ≤ 10 ms wall on a quiet host |
| One document check (≤ 500 KB, readings excluded) | ≤ 1 s Lean CPU, ≤ 2 s wall on a quiet host, Rust search excluded |
| Use-case harnesses (agent-policy, eligibility) | ≤ 1.25× the base commit's wall at the same load; a batch that switches an operation to Lean must not exceed it (agent-policy under Lean is 5.5× today, so batch 2 comes first) |
| Pilot document load (UDHR, constitution) | ≤ 120 s wall on a quiet host (the readings route's present limit); UDHR needs F5 |
| Any batch, any measured workload | no more than 20% more Lean CPU than the base commit, unless the batch's `DELTA.md` lists it and the DRI signs |

**What this means for the order.** Switching the core operations to Lean (batches 12 and 13b) before F2, F3 and F6
would make every many-call workload 5× slower; that is why batches 1 and 2 come first. The readings route is
already Lean's; batch 3 deletes Python's repetition of it (half the load) and starts F5, which is the only fix that
needs Lean proofs.

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
| 3 | **Readings S1.** `readings_route.validate` relays Lean's row (F5a: half the UDHR load); per-set requests across the pool (F5e). | F5b: build each candidate's `one D s i` once per request; F5c (incremental candidate elaboration with its equality lemma) and F5d (rights-chain profile) follow as their own batches if F5b does not reach the 120 s budget | `readings_s1.py` (1,470), `rust_check`, `readings.rs`, the 352 rights calls per UDHR load | 4–6 |
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
| 12 | **Environments, models and the profile gate.** Lean validates, Python constructs. Needs batch 2's handles, since environment construction is the hottest call. Ends the env-profiles finding class and DF-1 to DF-13. | the `environment` mode accepts every profile Python's registry accepts, through Lean's composed dispatch (today 9 of 17: `norm-defaults@0` and `readings@1` are refused, so Lean authority refuses the pilots, section 3.4) | `Environment._decode` and model validation (~590), `profiles.py` gate (~110), `validation.decided` | 4–6 |
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
  own evidence; q3 (timeouts) is answered by measurement (section 3.4: the flat 5 s limits failed the
  agent-policy harness and the bluedot document under load) and batch 1's per-operation deadlines (F4); q6 (shadow
  in CI on every merge) is dropped.
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
3. **Performance where Lean is slower today** (sections 3 and 4): the agent-policy harness takes 5.5× as long under
   Lean authority, and the UDHR pilot's readings call (already Lean's) needs about 10× its limit. Batches 1–3 are
   prerequisites for flipping anything with a large environment or many readings, and F2, F5b and F6 are estimates
   until their batches measure them; if F2 falls short, the core switches (12, 13b) wait. The IDE path is fine: a
   service call costs 1–2 ms at the median.
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
9. Start order: batch 0–2 first, or batch 3 (readings: halves the UDHR load and starts F5) first? Recommended: 0,
   then 3 and 1 in parallel, then 2. Batch 3 alone does not bring the UDHR load under its 120 s limit (1,161 s of
   Lean CPU remain); F5b–F5d do, if anything does.
