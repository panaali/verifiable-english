# Operation assurance manifest

**Status:** P0-3 of the architecture roadmap, 2026-09-28. This adds the manifest, its executable bindings and the
enforcement hooks. **No operation's authority changes:** every verdict is still produced where it was before, and
Lean and Rust remain cross-checks and test oracles. Inputs: [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md)
(revision 3), [verification-contract.md](verification-contract.md), [lean/README.md](../../lean/README.md).

## 1. What the manifest records

`ve/assurance-manifest.json` (shipped inside the package, loaded by `ve/assurance.py`) has one entry for every
public semantic operation. Each entry records:

| Field | Meaning |
|---|---|
| `id`, `summary`, `class` | the operation; `class` is `leaf`, `combination` (plan section 1.2 classes L and C), `search` or `surface` |
| `authority` | who produces the verdict **now**: `python`, `migrated` (Lean only) or `lean-only` (no Python implementation may exist) |
| `target` | the engine the migration plan assigns: `lean`, `rust` (search, validated by Lean) or `python` (surface and trusted class-C rules) |
| `assurance` | `current` label on records today (always `experimental`) and the label the plan grants `at_switch`, with the reason |
| `python` | every Python function that produces the verdict, as `module:qualname` |
| `outcomes` | the verdict, semantic-unknown, rejection, budget and operational outcome values (section 2) |
| `lean` | `bindings` (executable, mode, case kinds, the typed `response` fields of an `ok` row, their `counts` and the reasons the rest are `uncounted`, dispatch files), `planned_modes`, `theorems` (audited names), `planned_theorems`, `decoders` (trusted decoder files on the path) |
| `rust` | Rust CLI commands on the path and their role |
| `lean_call_sites` | the Python functions that invoke Lean for this operation |
| `tests` | tests that back the operation (conformance, differential and three-way checks) |
| `trusted` | ids from the top-level `trusted` table: what a reader must trust for this operation's verdict |
| `notes` | recorded gaps and conflations |

The top level also holds the `trusted` component table, the pinned Lean decoder ranges (section 4), the
reviewed broad exception handlers (section 5), `plan_operations` and `non_verdict_api`.

**Completeness.** Comparing the decorated functions with the `python` entries cannot find an operation that has
neither. Two further checks can: `plan_operations` maps every operation listed in the migration plan's section 2.3
and every new Lean mode of its section 2.1 to the manifest operations that carry it (the test parses the plan), and
every public name of the `ve` package is either a verdict entry (a function, or a class with an entry method such
as `Environment.__init__`, `FiniteModel.from_dict` or `Claim.claim_id`) or listed in `non_verdict_api` with the
reason it produces no verdict. Environment validation, model validation, identity and reference validation are
operations for this reason.

## 2. Operational failure versus semantic UNKNOWN

Five outcome classes are kept apart in every result:

| Class | Values | Meaning |
|---|---|---|
| verdict | `Valid`, `Satisfied`, `Found`, `ALL`, `CONFLICT`, `Checked`, ... | a checked answer |
| unknown | `UNKNOWN`, `NotFound`, `Incomplete` | the checker ran to completion; bounded search or proof found neither answer |
| rejection | `InvalidInput`, `SyntaxError`, `TypeMismatch`, `InvalidModel`, `AdmissionError`, ... | the input is invalid |
| budget | `ResourceLimit` | a deterministic public work budget or structural cap was reached |
| operational | `CheckerUnavailable` | no verdict was obtained: a backend was missing or mismatched, crashed, timed out or gave malformed output, or a migrated operation reached a non-authoritative engine |

`ve.errors.CheckerUnavailable` carries `code`, `message`, `operation` and `backend`. It is deliberately **not** a
`VEError` or `ValueError`. The semantic modules catch `VEError`, `ResourceLimit` and `ValueError` to produce
`InvalidInput`, `UNKNOWN`, `InvalidCertificate` or a `ResourceLimit` attempt, so a `CheckerUnavailable` passes through
all of them unchanged. The manifest test pins this. `AuthorityViolation` is the `CheckerUnavailable` subclass that
the authority guard raises.

How an operational failure surfaces:

| Where | Before P0-3 | Now |
|---|---|---|
| `ve.backends.lean.run`, the external-checker call currently used by semantic operations | n/a | a missing binary, `OSError`, timeout, signal or unexpected exit status, non-JSON output, a row count, id or case-index mismatch (compared with their JSON types: `false` never names case 0), a row outside the response schema, or an exit status that contradicts the rows all raise `CheckerUnavailable`. The schema: `status` is `ok` or `error`; an `error` row has a string `error`; an `ok` row names its case `id` and carries every field of its binding's `response` with the declared type, element types included, and every declared `counts` holds (a bundle's `lemmas` is an array of strings and `checked` a nat, both counting the submitted lemmas; an argument's `valid` is a Boolean and, on the route, `background` a nat). Only a well-formed `status: error` row, or a well-formed `ok` row whose content differs from the expected acceptance, is Lean's semantic rejection |
| `check_bundle(lean_executable=...)` | `VEError` (`InvalidInput`) for an unavailable Lean; a crash surfaced as `SyntaxError` or `ResourceLimit` | raises `CheckerUnavailable`. A Lean rejection still raises `VEError`. The result carries `lean_outcome`: `accepted`, `not_requested` or `not_applicable` (no lemmas) |
| `check_argument(lean_executable=...)` | `lean_checked: false` for both rejection and unavailability; only `lean_detail` wording differed | `ArgumentResult.lean_outcome` (and `outstanding_obligations`): `accepted`, `rejected`, `unavailable`, `not_requested` or `not_applicable`; `lean_status` reads `Lean-checked: unavailable`. The `ve-argument-tableau@1` record carries `lean_outcome` only when it is `unavailable`: every other outcome is implied by `lean_checked` and `lean_detail`, so those records keep their pre-P0-3 `record_id` (pinned by a test with `checker_build` fixed). The Lean replay is an optional cross-check while authority is Python, so the Python verdict is unaffected |
| `check_argument` when a verdict it needs is unavailable | would have become `InvalidInput` or an edge error had the exception been a `VEError` | `status: CheckerUnavailable`, `composed: false`, `proof: not_checked`, with the error in `errors`. Callers that act on the status (`parse_english_argument`, assist `status`) call `ArgumentResult.require_available()`, which re-raises it, so it never reads as a failed replay or a `SyntaxError` |
| `premise_status`, `compare`, `check_readings`, `check`, `check_document`, norms, admission | no operational path | `CheckerUnavailable` propagates; it never becomes `UNKNOWN` |
| CLI (`python -m ve ...`) | exit 2 with `InvalidInput` | `{"status": "CheckerUnavailable", "error": ...}`, **exit 5**; exit codes 0–4 are unchanged |
| `ve assist` tools and CLI | `BackendError` | the error keeps code `CheckerUnavailable`. The assist CLI exits 5 whether the failure is raised or returned in an action or tool result (`ve.assist.cli.exit_code`), and does not save that action: the ledger must replay, and an operational failure does not recur once the checker is back |

## 3. Authority and the enforcement hook

Every function listed under `python` carries `@semantic_entry("<operation>")` (`ve/assurance.py`). The decorator
registers the function and guards each call. While an operation's `authority` is `python`, the guard is inert (one
check of an empty set). When the manifest records an operation as `migrated`, every Python entry for it raises
`AuthorityViolation` before its body runs. The verdict of a migrated operation can therefore only come from Lean.
A combination that needs the verdict (readings, premise status, compare, the argument checker) reports
`CheckerUnavailable`, never `UNKNOWN`. There is no fallback to Python.

`ve.backends.lean.run` checks every call against the operation's declared Lean `bindings` (executable, mode and case
kinds) and, for callers inside `ve`, its declared `lean_call_sites` before starting a process. An undeclared call is a
programming error (`RuntimeError`), not an outcome. Every `ok` row must carry the binding's declared `response`
fields with their declared types and satisfy its `counts`; any other row is `CheckerUnavailable`, and callers read only
rows that passed. A `response` type is `bool`, `nat` (a non-negative integer, never a Boolean), `string`, `object`,
`json` (any value; the caller compares its content) or `array<T>` (every element of type `T`). A `counts` entry
`FIELD: case.NAME` or `FIELD: row.NAME` requires the length of array `FIELD` (or the value of nat `FIELD`) to equal
the length of the submitted case's array `NAME` or of the row's declared array `NAME`; each is a property of the
runner's output (for bundles `VE.Definitions.Bundle.checkAll_length`, for dependency order
`VE.Route.verifyOrder_sound` with the duplicate-name check, for evaluation `values` counting `case.ast` in every mode
the `VE.EvaluationCounts` decoder theorems). Every size-carrying field (an array or a nat) is either counted or listed
under the binding's `uncounted` with the reason its size is Lean's to determine (for example, the background an
environment generates), so a truncated or padded answer to a case-sized question is never `ok`.

Migrating an operation (SEMANTICS-MIGRATION-PLAN stage 4):

1. Add a Lean-backed implementation with the same signature, marked `@semantic_entry(op, engine="lean")`, whose call
   sites are listed in `lean_call_sites`.
2. Set the operation's `authority` to `migrated`, and update `test_nothing_is_migrated_yet` in the same reviewed
   commit.
3. The existing Python entries stay importable for rollback. `VE_AUTHORITY=python` per-operation rollback is stage 4
   work and is not part of this change.

`ve.assurance.simulate_migration(*ops)` enforces Lean authority for a block of code. The tests use it to check that
every entry is guarded and that combinations propagate unavailability, and a stage-4 rehearsal can run with it.

## 4. The trusted base

Every operation names its trusted components; the definitions are in the manifest's `trusted` table. While
authority is Python, `python:implementation` is trusted for every operation that has one. Tests compare it with Lean
and Rust, but no theorem covers it. The Lean side trusts the kernel and its three axioms (`lean:kernel`, audited by
`lean/audit.py` into `lean/axioms.txt`), the compiler and runtime (`lean:compiler`), the runner dispatch
(`lean:runner-glue`) and the hand-written decoders.

**Hand-written Lean decoders (`lean:decoders`), 1,885 lines.** These are the JSON parser, the wire decoders, the
canonical serializers, the SHA-256 identity code and the norms document split that rewrites a document before it
is decoded. No refinement theorem relates them to the wire specification. Decoded models are proved admissible and
decoded formulas are typed by the proved checker, but the correspondence with the specified wire format is trusted.
The manifest pins each range, and the test checks the following:

- every range starts and ends on a declaration boundary;
- every listed declaration starts inside a range;
- the ranges sum to `total_lines`;
- each file's line count and SHA-256 equal the pinned `lines` and `sha256`.

The last check pins the whole file, not only the ranges: code appended right after a range, or any other edit to a
decoder file, fails the test until a reviewer confirms the ranges still cover the decoders and updates the pins.
Every other Lean file that reads or builds JSON must be classified under `other_json` with the reason it is not a
decoder (runner glue, the order surface parser, theorem statements, executable regressions, the English harness).
The test compares that classification with a scan of `lean/`, so a new JSON-handling file cannot go unlisted.

`lean/VE/Norms/Admission.lean` lines 22–45 (`splitUnit`, `splitDocument`) are pinned because they rewrite the wire
document before `decodeDoc` sees it and `admitDocument_spec` takes their result as given; the remaining JSON reads
in `admitDocument` are specified by `SourceDecoded` in `admitDocument_spec`, and its `envelopeGate` only rejects,
through the pinned `Gate.decodeEnvelope`.

<!-- BEGIN GENERATED DECODERS: python tools/assurance_manifest.py --write -->
| File | File lines | Decoder lines | Ranges | File SHA-256 |
|---|---:|---:|---|---|
| `lean/VE/Alternatives/Admission.lean` | 133 | 133 | 1–133 | `64cacbdf9eb6…` |
| `lean/VE/Alternatives/Replay.lean` | 328 | 328 | 1–328 | `1b69bb125b3d…` |
| `lean/VE/Alternatives/Wire.lean` | 296 | 296 | 1–296 | `26827ec1010c…` |
| `lean/VE/Attribution/Admission.lean` | 343 | 343 | 1–343 | `de9ae29eed4d…` |
| `lean/VE/Attribution/Content.lean` | 726 | 726 | 1–726 | `42d7518d9a79…` |
| `lean/VE/Attribution/Wire.lean` | 514 | 514 | 1–514 | `4eadc30b6ea7…` |
| `lean/VE/Attribution/Preflight.lean` | 550 | 550 | 1–550 | `e54406c9b676…` |
| `lean/VE/Bridge.lean` | 282 | 235 | 14–248 | `2d4e432b9698…` |
| `lean/VE/CertificateWire.lean` | 236 | 164 | 11–163, 177–187 | `3d002c705023…` |
| `lean/VE/Closure/Bridge.lean` | 99 | 58 | 9–66 | `b9c7a15be6bb…` |
| `lean/VE/Core/Bridge.lean` | 159 | 117 | 10–126 | `6cd616c3c663…` |
| `lean/VE/Core/Wire.lean` | 166 | 166 | 1–166 | `280802e8f79a…` |
| `lean/VE/Definitions/Bundle.lean` | 471 | 471 | 1–471 | `fc86d51a7f84…` |
| `lean/VE/EnglishGrammar/Encode.lean` | 782 | 782 | 1–782 | `b1dc5f105ae7…` |
| `lean/VE/EnglishGrammar/Run.lean` | 689 | 689 | 1–689 | `ef68f91ead01…` |
| `lean/VE/Json.lean` | 136 | 136 | 1–136 | `c5891a586979…` |
| `lean/VE/NormDefaults/Admission.lean` | 350 | 350 | 1–350 | `b60054268019…` |
| `lean/VE/NormDefaults/Layered.lean` | 426 | 426 | 1–426 | `dc7777651caf…` |
| `lean/VE/NormDefaults/Replay.lean` | 391 | 391 | 1–391 | `4242c79ff826…` |
| `lean/VE/NormDefaults/Report.lean` | 475 | 475 | 1–475 | `f00d2b66e182…` |
| `lean/VE/NormDefaults/Wire.lean` | 383 | 383 | 1–383 | `c59e1151313d…` |
| `lean/VE/Norms/Admission.lean` | 465 | 24 | 22–45 | `a57c5bf09a15…` |
| `lean/VE/Norms/Flagged.lean` | 389 | 389 | 1–389 | `2921520480a4…` |
| `lean/VE/Norms/Replay.lean` | 404 | 69 | 103–151, 283–302 | `741968e0457a…` |
| `lean/VE/Norms/Wire.lean` | 331 | 306 | 25–330 | `608bb613cc6a…` |
| `lean/VE/Order/Wire.lean` | 292 | 217 | 24–233, 247–253 | `03f085f67a44…` |
| `lean/VE/Readings/SupWire.lean` | 378 | 378 | 1–378 | `f1efaaba3d67…` |
| `lean/VE/Readings/Wire.lean` | 988 | 988 | 1–988 | `311cfeb72316…` |
| `lean/VE/Rights/Admission.lean` | 471 | 471 | 1–471 | `1b43543b7e66…` |
| `lean/VE/Rights/Wire.lean` | 696 | 696 | 1–696 | `858495e911e8…` |
| `lean/VE/Risk/Admission.lean` | 128 | 128 | 1–128 | `f3927135556b…` |
| `lean/VE/Risk/Audit.lean` | 190 | 190 | 1–190 | `62c518fee5d3…` |
| `lean/VE/Risk/Record.lean` | 1266 | 1266 | 1–1266 | `9b9aa82f9a8d…` |
| `lean/VE/Risk/Run.lean` | 632 | 632 | 1–632 | `6d98b5de4c61…` |
| `lean/VE/Risk/Wire.lean` | 487 | 487 | 1–487 | `3c35ffb89361…` |
| `lean/VE/Route/Admission.lean` | 697 | 697 | 1–697 | `230006c26a07…` |
| `lean/VE/Route/Decode.lean` | 282 | 282 | 1–282 | `7cd23701ca95…` |
| `lean/VE/Route/Gate.lean` | 213 | 38 | 126–163 | `afccc5271974…` |
| `lean/VE/Route/Wire.lean` | 666 | 666 | 1–666 | `7a9f5a63f666…` |
| `lean/VE/Senses/Decode.lean` | 93 | 93 | 1–93 | `5f0f5265fe8d…` |
| `lean/VE/Senses/Run.lean` | 147 | 147 | 1–147 | `cc6635b7b2d4…` |
| `lean/VE/Service/Family.lean` | 817 | 817 | 1–817 | `e1e00be43796…` |
| `lean/VE/Service/FamilyBundle.lean` | 500 | 500 | 1–500 | `75698a329690…` |
| `lean/VE/Service/FamilyNorms.lean` | 244 | 244 | 1–244 | `f2e5ffd9ed57…` |
| `lean/VE/Service/Graph.lean` | 255 | 255 | 1–255 | `cd0523e5ad4d…` |
| `lean/VE/Service/Readings.lean` | 215 | 215 | 1–215 | `357a25dda81b…` |
| `lean/VE/SoftNorms/Admission.lean` | 332 | 332 | 1–332 | `65c5511e845d…` |
| `lean/VE/SoftNorms/Phases.lean` | 362 | 362 | 1–362 | `a19fb700f52c…` |
| `lean/VE/SoftNorms/Wire.lean` | 461 | 461 | 1–461 | `0669c3cb6966…` |
| `lean/VE/SpeechActs/Source/Admission/Run.lean` | 630 | 630 | 1–630 | `666d467b95bb…` |
| `lean/VE/SpeechActs/Source/Run.lean` | 889 | 889 | 1–889 | `965cd295dcb4…` |
| `lean/VE/SpeechActs/Wire.lean` | 993 | 993 | 1–993 | `fbe08d985f7f…` |
| `lean/VE/Time/Document.lean` | 613 | 613 | 1–613 | `4407e998d007…` |
| `lean/VE/Time/Wire.lean` | 843 | 843 | 1–843 | `43eff830ca8c…` |
| **total** | | **23,051** | | |
<!-- END GENERATED -->

Outside the decoder count: `lean/VE/Order/Surface.lean` (order text parser, `lean:order-surface-parser`), the runner
dispatch (`lean:runner-glue`), and `lean/VE/English/Run.lean`, a harness no theorem depends on.

## 5. Executable bindings

`tests/test_assurance_manifest.py` checks the manifest against the code:

- **Python entries.** The functions carrying `semantic_entry` are exactly the manifest's `python` entries, found by an
  AST scan of `ve/`. Each entry resolves to a guarded callable, and each is refused once its operation is
  migrated.
- **Lean call sites.** The calls of `ve.backends.lean.run` are exactly the declared `lean_call_sites`, however the
  backend is imported (module or function alias, absolute or relative import); the operation argument must be a
  literal, and any other reference to `run` (stored, passed or rebound) fails the test. At run time `run` also
  refuses a caller inside `ve` that is not a declared call site of the operation, which covers indirections the
  scan cannot see. Only `ve/backends/lean.py`, the additive stage-1
  `ve/backends/lean_service.py` and the stage-2 Rust JSON-lines client `ve/backends/rust_jsonl.py` may import
  `subprocess`.
- **Lean bindings.**
  - Each executable is a `lean_exe` in `lean/lakefile.toml`.
  - Each mode string occurs in its root file.
  - Each case kind occurs in a named dispatch file.
  - Each decoder file is a pinned decoder.
  - The routing itself is executed, not matched as strings: `conformance/binding_probes.py` holds one case of the
    operation for every (operation, executable, mode, kind) binding, and the set of probes must equal the set of
    bindings. Each probe goes through `ve.backends.lean.run` to the built runner in its declared mode and must come
    back `ok` with the binding's declared `response` fields, types and counts, and every other mode of the same executable must reject
    it. Moving a binding to another mode or kind therefore fails without Lean (no probe) and with Lean (the probe is
    not routed there).
- **Theorems.** Every listed theorem is audited in `lean/axioms.txt`. A planned theorem that appears there fails the
  test until it is moved to `theorems`.
- **Other references.** Rust commands occur in `rust/ve/src/main.rs`, and every backing test exists.
- **Broad exception handlers.** Every handler in `ve/` broad enough to catch `CheckerUnavailable` (`Exception`,
  `BaseException`, `RuntimeError`, bare) is listed under `reviewed_broad_handlers` with the reason it cannot turn an
  operational failure into a verdict. A new one fails the test until it is reviewed.
- **Runtime behaviour.**
  - Backend fault injection (missing, crash, signal, usage error, garbage, empty, wrong row count, wrong ids or
    case indices, rows without a status, an error message, a case id or a caller field, ill-typed fields,
    inconsistent exit status, hang) yields `CheckerUnavailable`; for bundles and arguments a malformed row is never
    a rejection.
  - A `status: error` row is returned as a rejection.
  - Bundles and arguments separate rejection from unavailability.
  - The CLI exits 5.
  - With certificate and countermodel checking migrated, `premise_status`, `compare`, `check_readings` and
    `check_argument` report unavailability rather than `UNKNOWN`.
  - Search reports `Found` only after the `countermodel.check` entry accepts the witness: with that operation
    migrated, `find_countermodel` and `find_distinguishing_model` raise `CheckerUnavailable`, and a candidate the
    check refuses is never published. (Proof search already replays its certificate through
    `check_entailment_certificate` before `Found`.)
- **Completeness.** The plan's operations and new Lean modes map to operations (`plan_operations`), and every public
  name of `ve` is an entry or classified in `non_verdict_api`.
- **Invariants.** No operation is migrated yet, and lean-only operations have no Python verdict path: their only
  Python code is a declared relay of Lean's answer through `ve.backends.lean.run` (`senses.read`), never a semantic
  entry.
- **This document.** The table in section 7 is generated from the manifest.

## 6. Recorded conflations, not changed here

Changing a public diagnostic code needs the migration plan's section-2.3 product decision, so these are recorded in
the manifest `notes`, not changed:

- **Earley timeout.** The English Earley wall-clock budget (`ve/surface/unambiguity.py`, `EARLEY_SECONDS`) reports
  `ResourceLimit`. The plan reserves `ResourceLimit` for deterministic budgets and calls wall-clock limits
  operational.
- **Marked English conclusions.** When bounded proof search for a marked English conclusion ends in `NotFound` or
  `ResourceLimit`, the conclusion is rejected as `SyntaxError` (`ve/english.py`, `_check_conclusions`). This is a
  search UNKNOWN surfacing as a rejection, and the search result is not replayed there.

## 7. Operations

<!-- BEGIN GENERATED: python tools/assurance_manifest.py --write -->
| Operation | Class | Authority now → target | Assurance now / at switch | Python entries | Lean bindings | Lean theorems | Rust | Trusted |
|---|---|---|---|---|---|---|---|---|
| `parse` | leaf | python → lean | experimental / experimental | `ve.parser:parse_with_metadata`<br>`ve.parser:parse`<br>`ve.parser:canonicalize`<br>`ve.parser:is_canonical` | `ve_conformance (default)`<br>`ve_conformance order surface` | `VE.Surface.parse_print`<br>`VE.Surface.parse_wellFormed`<br>`VE.Surface.normalize_idempotent`<br>`VE.Surface.print_injective`<br>`VE.Surface.accepted_normalize_eq_iff`<br>`VE.Surface.parse_print_propositional`<br>`VE.Closure.Surface.parse_print_named`<br>`VE.Core.Surface.parse_print_named`<br>`VE.EvaluationCounts.legacy_decodeDocument_length`<br>`VE.EvaluationCounts.closure_decodeFormulas_length` | `parse`<br>`format` | `python:implementation`<br>`python:wire`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue`<br>`lean:order-surface-parser` |
| `typing` | leaf | python → lean | experimental / reference-theorems-checked | `ve.ast:check_formula`<br>`ve.ast:check_document`<br>`ve.ast:formula_from_data`<br>`ve.ast:formula_to_data` | none | `VE.check_iff_wellFormed`<br>`VE.Closure.check_iff_wellFormed`<br>`VE.Order.check_iff_wellFormed`<br>`VE.Core.check_iff_wellFormed` | `conformance` | `python:implementation`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders` |
| `environment` | leaf | python → lean | experimental / experimental | `ve.environment:Environment.__init__` | none | `VE.Route.Gate.decodeEnvelope_sound`<br>`VE.Route.Gate.classify_sound`<br>`VE.Route.Gate.classify_complete`<br>`VE.Route.Run.route_gate`<br>`VE.Route.Run.route_gate_rejects`<br>`VE.Order.profile_gate` | `conformance` | `python:implementation`<br>`python:wire` |
| `model` | leaf | python → lean | experimental / experimental | `ve.model:FiniteModel.from_dict` | none | `VE.Bridge.decodeModel_valid`<br>`VE.Route.Wire.decodeModel_valid`<br>`VE.Route.Wire.decodeModel_background`<br>`VE.Route.Wire.decodeModel_intended` | `conformance` | `python:implementation`<br>`python:wire` |
| `evaluate` | leaf | python → lean | experimental / reference-theorems-checked | `ve.evaluate:evaluate` | `ve_conformance (default)`<br>`ve_conformance route evaluate`<br>`ve_conformance order evaluate` | `VE.eval_iff_denote`<br>`VE.eval_false_iff_not_denote`<br>`VE.document_eval_iff_denote`<br>`VE.Closure.eval_iff_denote`<br>`VE.Order.eval_iff_denote`<br>`VE.Core.eval_iff_denote`<br>`VE.Bridge.decodeModel_valid`<br>`VE.Route.Wire.decodeModel_valid`<br>`VE.EvaluationCounts.legacy_decodeDocument_length`<br>`VE.EvaluationCounts.closure_decodeFormulas_length`<br>`VE.EvaluationCounts.core_decodeFormulas_length`<br>`VE.EvaluationCounts.order_decodeFormulas_length`<br>`VE.EvaluationCounts.route_decodeFormulas_length`<br>`VE.Route.WireSound.runFol_evaluate`<br>`VE.Route.WireSound.runClosure_evaluate`<br>`VE.Route.WireSound.runOrder_evaluate`<br>`VE.Route.RunSound.route_fol_evaluate`<br>`VE.Route.RunSound.route_closure_evaluate`<br>`VE.Route.RunSound.route_order_evaluate` | `evaluate`<br>`conformance` | `python:implementation`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue` |
| `countermodel.check` | leaf | python → lean | experimental / reference-theorems-checked | `ve.search:check_countermodel` | `ve_conformance (default) countermodel`<br>`ve_conformance route countermodel`<br>`ve_conformance order countermodel` | `VE.countermodelCheck_iff`<br>`VE.countermodel_sound`<br>`VE.Closure.countermodelCheck_iff`<br>`VE.Closure.countermodel_sound`<br>`VE.Order.countermodelCheck_iff`<br>`VE.Order.countermodel_sound`<br>`VE.Order.checkCountermodel_sound`<br>`VE.Core.countermodelCheck_iff`<br>`VE.Core.countermodel_sound`<br>`VE.Bridge.decodeModel_valid`<br>`VE.Bridge.decoded_countermodel_sound`<br>`VE.Bridge.CountermodelQuery.refutes_sound`<br>`VE.Route.Wire.decodeModel_valid`<br>`VE.Route.WireSound.runFol_countermodel`<br>`VE.Route.WireSound.runClosure_countermodel`<br>`VE.Route.WireSound.runOrder_countermodel`<br>`VE.Route.RunSound.route_fol_countermodel`<br>`VE.Route.RunSound.route_closure_countermodel`<br>`VE.Route.RunSound.route_order_countermodel` | `check-countermodel`<br>`conformance` | `python:implementation`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue` |
| `countermodel.search` | search | python → rust | experimental / experimental | `ve.search:find_countermodel`<br>`ve.search:find_distinguishing_model` | none | none | `countermodel`<br>`conformance` | `python:implementation` |
| `certificate.check` | leaf | python → lean | experimental / reference-theorems-checked | `ve.entailment:check_entailment_certificate` | `ve_conformance check-certificate`<br>`ve_conformance route certificate`<br>`ve_conformance order certificate` | `VE.Tableau.checkCertificate_sound`<br>`VE.Closure.Tableau.checkCertificate_sound`<br>`VE.Closure.Tableau.checkCertificate_sound_v0`<br>`VE.Core.Tableau.checkCertificate_sound`<br>`VE.Core.Tableau.checkCertificate_sound_v0`<br>`VE.Order.Tableau.checkCertificate_sound`<br>`VE.CertificateWire.Query.accepts_sound`<br>`VE.CertificateWire.ClosureQuery.accepts_sound`<br>`VE.Order.Wire.Query.accepts_sound`<br>`VE.Core.Wire.run_certificate_acceptance`<br>`VE.Route.route_acceptance`<br>`VE.Route.core_route_acceptance`<br>`VE.Route.WireSound.Runner.acceptance`<br>`VE.Route.WireSound.runFol_certificate_acceptance`<br>`VE.Route.WireSound.runClosure_certificate_acceptance`<br>`VE.Route.WireSound.runOrder_certificate_acceptance`<br>`VE.Route.RunSound.route_fol_certificate`<br>`VE.Route.RunSound.route_closure_certificate`<br>`VE.Route.RunSound.route_order_certificate` | none | `python:implementation`<br>`python:wire`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue` |
| `definitions.elaborate` | leaf | python → lean | experimental / experimental | `ve.definitions:compile_definitions`<br>`ve.definitions:expand`<br>`ve.background:background`<br>`ve.background:validate_background`<br>`ve.background:dependency_order` | `ve_conformance route background`<br>`ve_conformance route dependency-order` | `VE.Definitions.stepOk_sound`<br>`VE.Definitions.chainOk_sound`<br>`VE.Definitions.faithful`<br>`VE.Definitions.conservative`<br>`VE.Definitions.conservative_entails`<br>`VE.Definitions.routeLayer_background_sound`<br>`VE.Route.Background.fol_background_sound`<br>`VE.Route.Background.fol_background_complete`<br>`VE.Data.Background.generate_sat_iff` | `conformance` | `python:implementation`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue` |
| `norms.elaborate` | leaf | python → lean | experimental / experimental | `ve.norms:NormDocument.elaborate`<br>`ve.norms:NormDocument.premises` | `ve_service norms norms-elaborate` | `VE.Norms.elaborate_iff`<br>`VE.Norms.elaborate_iff_at`<br>`VE.Norms.norms_route_intended` | `conformance` | `python:implementation`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue` |
| `norms.conflict` | leaf | python → lean | experimental / experimental | `ve.norms:check_witness`<br>`ve.norms:check_conflict` | `ve_service norms norms-conflict` | `VE.Service.FamilyNorms.closure_conflict_target_sound`<br>`VE.Service.FamilyNorms.core_conflict_target_sound`<br>`VE.Service.FamilyNorms.order_conflict_target_sound`<br>`VE.Norms.conflictFreeCheck_sound`<br>`VE.Norms.conflict_witness_sound`<br>`VE.Norms.conflict_smallModel`<br>`VE.Norms.FlaggedSpec.conflictFree_of_base`<br>`VE.Norms.FlaggedSpec.norms_flagged_conflict_free`<br>`VE.Norms.FlaggedSpec.norms_wire_conflict_free`<br>`VE.Norms.Flagged.norms_flagged_conflict_sound`<br>`VE.Norms.Flagged.norms_flagged_witness_sound` | `conformance` | `python:implementation`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue` |
| `norms.certificate` | leaf | python → lean | experimental / experimental | `ve.norms:check_norm_entailment_certificate` | `ve_service norms norms-certificate` | `VE.Service.FamilyNorms.closure_norms_certificate_sound`<br>`VE.Service.FamilyNorms.core_norms_certificate_sound`<br>`VE.Service.FamilyNorms.order_norms_certificate_sound`<br>`VE.Norms.norms_route_acceptance`<br>`VE.Norms.norms_route_entails_iff`<br>`VE.Norms.norms_route_countermodel`<br>`VE.Norms.Flagged.norms_flagged_acceptance`<br>`VE.Norms.RunSound.norms_wire_certificate_acceptance` | none | `python:implementation`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue` |
| `soft.elaborate` | leaf | lean-only → lean | experimental / experimental | none | none | none | none | `lean:kernel`<br>`lean:compiler` |
| `admission` | leaf | python → lean | experimental / experimental | `ve.admission:admit_document`<br>`ve.norm_admission:admit_norm_document`<br>`ve.norm_defaults_route:admit_norm_defaults_document` | `ve_conformance route admission`<br>`ve_service norms admission`<br>`ve_service norm-defaults admission`<br>`ve_service quantity document` | `VE.Route.Admission.admit_report_sound`<br>`VE.Route.Admission.admit_string_sound`<br>`VE.Route.Admission.admit_labels_decoded`<br>`VE.Norms.Admission.admitDocument_spec`<br>`VE.Norms.Admission.norms_wire_admission_sound`<br>`VE.Norms.Admission.norms_wire_report_consequence`<br>`VE.Norms.Run.runAdmission_sound`<br>`VE.Norms.Run.norms_wire_acceptance`<br>`VE.NormDefaults.Admission.admitDocument_spec`<br>`VE.NormDefaults.Admission.wire_report_consequence`<br>`VE.NormDefaults.Run.runAdmission_sound`<br>`VE.NormDefaults.Run.normDefaults_wire_admission` | none | `python:implementation`<br>`python:wire`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue`<br>`python:record-identity` |
| `label` | leaf | python → lean | experimental / experimental | `ve.admission:parse_label`<br>`ve.admission:validate_label` | `ve_conformance route label` | `VE.Route.Admission.parseLabel_render` | `conformance` | `python:implementation`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders` |
| `identity` | leaf | python → lean | experimental / experimental | `ve.identity:source_id`<br>`ve.identity:meaning_id`<br>`ve.argument:Claim.claim_id`<br>`ve.argument:deduction_identity` | none | none | `conformance` | `python:implementation`<br>`python:wire` |
| `readings` | combination | python → lean | experimental / reference-theorems-checked | `ve.readings:check_readings` | none | `VE.Route.readings_all_iff`<br>`VE.Service.Readings.readings_all_sound`<br>`VE.Service.Readings.readings_none_sound`<br>`VE.Service.Readings.readings_some_sound`<br>`VE.Service.Family.closure_readings_all_sound`<br>`VE.Service.Family.closure_readings_none_sound`<br>`VE.Service.Family.closure_readings_some_sound`<br>`VE.Service.Family.core_readings_all_sound`<br>`VE.Service.Family.core_readings_none_sound`<br>`VE.Service.Family.core_readings_some_sound`<br>`VE.Service.Family.order_readings_all_sound`<br>`VE.Service.Family.order_readings_none_sound`<br>`VE.Service.Family.order_readings_some_sound`<br>`VE.Service.Family.fol_readings_all_sound`<br>`VE.Service.Family.fol_readings_none_sound`<br>`VE.Service.Family.fol_readings_some_sound` | none | `python:implementation`<br>`python:readings-rule`<br>`python:wire` |
| `graph.compose` | combination | python → lean | experimental / reference-theorems-checked | `ve.argument:check_argument` | `ve_conformance route certificate`<br>`ve_conformance check-certificate` | `VE.Graph.check_sound`<br>`VE.Graph.check_entails`<br>`VE.Graph.check_unfolds`<br>`VE.Graph.tableau_certificateSound`<br>`VE.composition_sound`<br>`VE.Service.Graph.graph_sound`<br>`VE.Service.Graph.graph_entails`<br>`VE.Service.Graph.graph_unfolds`<br>`VE.Service.Family.closure_graph_sound`<br>`VE.Service.Family.closure_graph_entails`<br>`VE.Service.Family.closure_graph_unfolds`<br>`VE.Service.Family.core_graph_sound`<br>`VE.Service.Family.core_graph_entails`<br>`VE.Service.Family.core_graph_unfolds`<br>`VE.Service.Family.order_graph_sound`<br>`VE.Service.Family.order_graph_entails`<br>`VE.Service.Family.order_graph_unfolds` | none | `python:implementation`<br>`python:composition-rule`<br>`python:argument-diagnostics`<br>`python:record-identity`<br>`python:backend-adapter`<br>`python:wire`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders` |
| `bundle.check` | leaf | python → lean | experimental / experimental | `ve.bundle:check_bundle` | `ve_conformance route bundle` | `VE.Definitions.Bundle.bundle_sound`<br>`VE.Definitions.Bundle.checkAll_sound`<br>`VE.Definitions.Bundle.checkAll_length`<br>`VE.Definitions.Bundle.backgroundLeaves_hold`<br>`VE.Service.FamilyBundle.bundle_sound`<br>`VE.Service.FamilyBundle.fol_bundle_sound`<br>`VE.Service.FamilyBundle.closure_bundle_sound`<br>`VE.Service.FamilyBundle.core_bundle_sound`<br>`VE.Service.FamilyBundle.order_bundle_sound` | none | `python:implementation`<br>`python:record-identity`<br>`python:backend-adapter`<br>`python:wire`<br>`lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue` |
| `english.admission` | surface | migrated → lean | experimental / experimental | `ve.english:parse_english_with_metadata`<br>`ve.english:parse_english`<br>`ve.english:parse_english_argument` | `ve_service english.read`<br>`ve_service english.grammar`<br>`ve_service english.check` | `VE.EnglishGrammar.policy_iff_no_failure`<br>`VE.EnglishGrammar.policy_selection`<br>`VE.EnglishGrammar.admitRequest_ok`<br>`VE.EnglishGrammar.admitRequest_exact`<br>`VE.EnglishGrammar.admitRequest_policy`<br>`VE.EnglishGrammar.translateRequest_policy`<br>`VE.EnglishGrammar.grammarFault_none`<br>`VE.EnglishGrammar.overlayCheck_constants`<br>`VE.EnglishGrammar.checkRequest_some`<br>`VE.EnglishGrammar.sensesRequest_policy`<br>`VE.EnglishGrammar.Run.codeClasses_total`<br>`VE.EnglishGrammar.decode_encode` | none | `lean:kernel`<br>`lean:compiler`<br>`lean:runner-glue`<br>`python:implementation`<br>`python:display`<br>`python:backend-adapter` |
| `english.statement` | surface | python → lean | experimental / experimental | `ve.norm_english:parse_english`<br>`ve.english:parse_statement_english`<br>`ve.surface.unambiguity:require_unique_derivation` | none | none | none | `python:implementation`<br>`python:surface` |
| `senses.read` | surface | lean-only → lean | experimental / experimental | none | `ve_senses_route (default)` | `VE.Senses.senses_resolved_one_reading`<br>`VE.Senses.senses_unit_sound`<br>`VE.Senses.senses_candidate_sound`<br>`VE.Senses.candidates_complete`<br>`VE.Senses.mixed_exact` | none | `lean:kernel`<br>`lean:compiler`<br>`lean:decoders`<br>`lean:runner-glue`<br>`python:wire`<br>`python:backend-adapter` |
| `premise-status` | combination | python → lean | experimental / experimental | `ve.vacuity:premise_status` | none | none | none | `python:implementation` |
| `compare` | combination | python → python | experimental / experimental | `ve.equivalence:compare` | none | none | none | `python:implementation`<br>`python:equivalence.compare` |
| `reference.validate` | combination | python → python | experimental / experimental | `ve.equivalence:validate_reference` | none | none | none | `python:implementation`<br>`python:reference-rule` |
| `document.check` | combination | python → lean | experimental / experimental | `ve.document:check_document` | none | none | none | `python:implementation`<br>`python:surface`<br>`python:record-identity` |
| `wire.diagnose` | leaf | lean-only → lean | experimental / experimental | none | `ve_service diagnose soft-elaborate,admission,norms-elaborate,norms-conflict,norms-certificate,norm-defaults-elaborate,norm-defaults-conflict,norm-defaults-certificate` | none | none | `lean:kernel`<br>`lean:compiler`<br>`lean:runner-glue` |
| `check` | combination | python → lean | experimental / experimental | `ve.check:check` | none | none | none | `python:implementation`<br>`python:display` |
<!-- END GENERATED -->

## 8. Not in this change

- Records do not yet carry the stage-4 `authority`, `assurance`, `covered_operations` and `trusted` fields. The
  manifest is their source when stage 4 adds them.
- `docs/spec/theorem-coverage.md`: the `at_switch` column is the plan's initial list, still to be confirmed.
- The `VE_AUTHORITY` flag, use of the stage-1 Lean service by semantic operations, shadow mode and the planned
  Lean modes (`parse`, `normalize`, `check`, `environment`, `model`, `graph`, `readings`, `identity`); each planned
  mode is carried by an operation's `planned_modes`. The service is available but has no manifest binding or
  semantic call site until the stage-2 adapters are implemented.
