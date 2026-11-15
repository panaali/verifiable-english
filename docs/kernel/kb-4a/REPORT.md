# kb-4a: the acts hook (plain norms and soft-norms paths independent of the acts code by type)

**Summary.** Built; no DRI signature needed (DELTA rows cite R16, R12). HEAD: this report's commit, synced with main `e51bec7301`.
The norms decoder takes an explicit `ActsHook`: plain runners use `ActsHook.plain`, the soft frame `ActsHook.lexical`, and the norms mode
hands every `acts@0` case to today's runner (`runCaseActsRouted`, new candidate path `normsActs`). Kernel 11,119 to 10,081 lines; the act
grammar, its table and the elaboration are counted by no kernel path. No answer byte changes (equality theorems; five keys checked).
Open: none blocking; deviations from the task's letter are D1-D6 under "Notes for the DRI"; the full gate is the chain's.

**F1 review fix.** `Service.FamilyNorms.folCase` now uses `Wire.decodeFlaggedActs` for every FOL-view source,
including `Flagged.replayWitnessIn`. Before the fix, the review probe and
`tests/test_stage2_norms.py::test_family_norms_fol_witness_uses_the_acts_decoder` failed on `acts@0` witnesses;
after the fix, the exact probe and all four regression cases pass. The regression includes both `CONFLICT`
and `UNKNOWN` witnesses with and without `acts@0`. No Python or Rust product code changed. The base-main
known-red tests remain separate and were not edited. `lake build`, `python3 lean/audit.py`, the kernel closure check,
and the trust check passed. The selected Mac run on `e014b4e776` failed only three test IDs: two assurance manifest
pin checks for the edited file, and one composed-path count still naming the decoder replaced by kb-4a. The whole-file
pin and count name were updated; all three failed IDs passed on rerun. The full gate is the merge train's.

SIZE: 535 product, 316 tests, 805 other hand-written lines (product: 304 of them are the proof modules
`VE.Acts.HookToday` and `VE.Acts.HookTwins`; tests: the #guard modules and tests/test_kernel_closure.py; other: 506
are `MEASURE.md` and the trust-mutants evidence, written by their tools; `git diff --numstat` against the merge base,
generated files excluded).

## Task deliverables

| Deliverable | Where | Tag |
|---|---|---|
| (1) `ActsHook`, one explicit parameter of the decoder and what it calls | `lean/VE/Norms/Wire.lean` (`structure ActsHook`, `ActsHook.plain`, `decodeNormsEnvironmentWith`, `decodeSource`, `decodeFlagged`) | AGENT |
| (1) `ActsHook.plain` refuses with `UnsupportedProfile: acts@0 needs the acts decoder`, references nothing under `VE.Acts.*` but `LexicalBase` (and the `VE.Acts.Act` type, D5) and nothing in `VE.Grammar.Table` | `lean/VE/Norms/Wire.lean`; `--why` below | AGENT |
| (1) `ActsHook.acts` in a module under lean/VE/Acts/, today's code unchanged | `lean/VE/Acts/Hook.lean` (also `ActsHook.lexical`, D2) | AGENT |
| (1) Theorem per decoder: acts = today's on every input; plain = today's where `acts@0` is not read | `lean/VE/Acts/HookToday.lean` (statements below) | AGENT |
| (2) Callers keep their behaviour; each caller and its instance | "Callers" below | AGENT |
| (2) `runCase` / `runAdmission`: does a caller rely on their acceptance of `acts@0`? | "Callers": the soft-norms and speech-acts delegation of a plain norms case does (they get `runCaseActs`); admission does not (its envelope refuses `acts@0` before it decodes: `runAdmission_today`) | AGENT |
| (2) `runCaseRouted` equal to today's, as a theorem | `VE.Acts.HookTwins.runCaseRouted_today` | AGENT |
| (2) service request/answer fixtures byte-identical | the selected run (tests/test_lean_service_schema.py and the relays over `tests/lean_service_corpus.py`), "Tests" below | AGENT |
| (3) statements of the norms and softNorms theorems kept up to the decoder they name | three statements now name `Wire.decodeSource Wire.ActsHook.plain` (`norms_wire_conflict_free`, `norms_wire_conflict_refuted`, `norms_wire_certificate_acceptance`); every other listed statement, and the five `_elaborated` ones, unchanged (lean/statements.txt diff) | AGENT |
| (4) registry: `norms` keeps the plain subjects (kernel); new `normsActs` (candidate, the note, entry the acts runner, subjects `runCaseIn`/`runAdmissionIn`, the five `_elaborated` theorems and `runAdmission_soundIn`); the `norms` mode under both paths | `tools/kernel-paths.json` | AGENT |
| (4) regenerate closure-baseline.json and MEASURE.md | `docs/kernel/closure-baseline.json` (regen); `docs/kernel/kb-4a/MEASURE.md` (D6) | AGENT |
| Acceptance: `--why` of the three modules prints no kernel chain | "Kernel figures and `--why`" | AGENT |
| Acceptance: kernel total falls; what remains of the acts group | 11,119 to 10,081; the acts group 1,185 to 289 lines, table below | AGENT |
| Acceptance: `normsActs`' own spec and wrap | 4,060 spec, 2,702 wrap, 4,083 lines | AGENT |
| Acceptance: `lake build`, `python3 lean/audit.py` (no new axiom), kernel check against the regenerated baseline, ALLOWANCES "fall" line | "Checks" | AGENT |
| Acceptance: every test file that mentions `acts@0` passes unchanged | the selected run selects all 32 of them; none was edited ("Tests") | AGENT |
| Acceptance: the five frozen keys byte-identical; the service corpus byte-identical | "Frozen keys"; "Tests" | AGENT |
| Seeded bugs (a)-(c) | `docs/kernel/kb-4a/seeded-bugs.json`; "Seeded bugs" | AGENT |

## The hook

`structure ActsHook` (lean/VE/Norms/Wire.lean), the operations the acts profile supplies today:

| Field | Type | `ActsHook.acts` (today's) | `ActsHook.plain` |
|---|---|---|---|
| `Vocab` | `Type` | `VE.Acts.Vocab` | `Unit` |
| `profiles` | `Bool → Json → Except String (List String)` | `pure (actsProfiles acts environment)` | `[]` when `actsProfiles` is empty, else `throw actsHookRefusal` |
| `fixed` | `List String → Json → Except String (List String)` | `actsFixed` | `pure []` |
| `vocab` | `List String → Json → Except String Vocab` | `actsVocab` | `pure ()` |
| `check` | `List String → List String → String → Nat → Json → Except String String` | `canonicalActIn` | `canonicalAct` |
| `shape` | same | `canonicalShape` | `canonicalAct` |
| `joined` | `Bool → List String → List String → Vocab → List Regulated → Except String (List (String × VE.Acts.Act))` | `joinedActs` (`actsOf`, the act grammar's reader) | `pure []` |

`ActsHook.lexical` (lean/VE/Acts/Hook.lean) is `ActsHook.acts` with `joined := pure []` (D2). `actsHookRefusal` is
`"UnsupportedProfile: acts@0 needs the acts decoder"`.

## Callers and the instance each gets

The parameterised decoder is `decodeNormsEnvironmentWith (H : ActsHook)` (D1); `decodeSource` takes `H` first.
"Today's" means: the same answer on every input by the theorem named.

| Caller | Instance | Why it answers as today |
|---|---|---|
| `Norms.Wire.decodeFlagged` → `Norms.Run.runCase`, `runAdmission`, `Flagged.replay*` | `plain` | the norms mode reaches `runCase` only when neither the environment nor its deciding view reads `acts@0` (`runCase_plain`, `runCaseRouted_today`); admission refuses `acts@0` at its envelope (`runAdmission_today`) |
| `Norms.Run.runCaseActsRouted` (norms mode, every case that reads `acts@0`, and `acts-elaborate`): `decoderOf` = `Acts.Decode.flaggedSource` or `Wire.decodeFlaggedActs`; `Acts.Run.normsSource` | `acts` | `runCaseActsRouted_today` (rfl), `decodeSource_acts` |
| `Norms.Run.runCaseActs` (= `runCaseIn decodeFlaggedActs`): `SoftNorms.Run.runCase`'s delegation of a non-soft case (SoftNorms/Run.lean:483) and `SpeechActs.Run` (Run.lean:542) | `acts` | they relied on `runCase`'s acceptance of `acts@0`; `runCaseActs_today` (rfl) |
| `Service.Document` admission (Document.lean:2067), `Discourse.Compose` (Compose.lean:58), `Service.ComposedAdmissionExamples` | `runAdmission` (`plain`) | no caller relied on acceptance: `envelopeGate` refuses every environment that reads `acts@0` (`envelopeGate_actsProfiles`, `runAdmission_today`) |
| `SoftNorms.Phases.declarations` (Phases.lean:178, `acts := actsFrame …`, `joined := false`) | `lexical` | `decodeNormsEnvironment_lexical` (rfl at `joined := false`) |
| `Acts.Decode.decodeElaboratedFlagged` → `flaggedSource`; `Acts.Run.normsSource`; `Norms.Replay` (`replayConflict`, `replayWitness`, `replayEntailment`, which no mode calls); `NormDefaults.Wire` (`decodeEnvironmentU` acts := true, `decodeSourceUWith`, `decodeSourceU`); `Service.FamilyNorms.folCase`; `Service.Document` (Document.lean:2186, 2189); `Alternatives.Wire.otherDeclarations`; `Attribution.Wire`; `Readings.SupRun`; `Readings.Wire` (acts := true); `SpeechActs.Wire` (acts := acts); `WireContract.Hooks.Acts.decoded`; `ResponseDecode.sourceTargets`; the examples `Acts.DecodeExamples`, `Service.ActsExamples` (acts := true), `Commands.Examples` (acts := true), `EnglishGrammar.Norm.Examples`; the proofs `Commands.Read.norms_facts`, `Commands.StepsProofs`, `SpeechActs.Wire` | `acts` | `decodeSource_acts`, `decodeNormsEnvironment_acts` (rfl); the proofs read today's body through them |
| `EnglishGrammar.Norm.Rules.regulatedOf` (acts := true) | `acts`, through today's name `decodeNormsEnvironment` (D1) | `decodeNormsEnvironment` is `decodeNormsEnvironmentWith ActsHook.acts` |
| `Alternatives.Wire` (Wire.lean:238), `Risk.Wire` (315), `Discourse.Compose` (71), `WireContract.Hooks.Norms` (80, 97), `WireContract.Hooks.NormDefaults` (27), `Commands.Examples` (474), `Service.ActsExamples` (61), `Discourse.ComposeExamples` (164), all with `acts := false` | `plain` | `actsProfiles false _ = []`, so `decodeNormsEnvironment_plain` holds on every input |
| `Service.Standalone.actsRead` | none | it calls no decoder: it reads `actsProfiles` and `actsView`, which reference no acts code |

`tools/kernel_closure.py --why VE.Acts.Grammar` on main showed the kernel callers (norms spec and wrap through
`decodeSource`, `joinedActs`, `actsOf`, and `runCaseRouted`/`normsSource`; softNorms spec through `declarations`); the
rest were found by `git grep -w decodeNormsEnvironment decodeSource decodeFlagged runCase runAdmission`.

## The equality theorems (verbatim statements)

`lean/VE/Acts/HookToday.lean` (`Today.*`: the definitions on main `4a5d3460d3`, frozen as proof helpers, class P):

```lean
theorem decodeNormsEnvironment_acts (environment : Json) (displayConstants acts joined : Bool) :
    decodeNormsEnvironmentWith ActsHook.acts environment displayConstants acts joined =
      Today.decodeNormsEnvironment environment displayConstants acts joined
theorem decodeSource_acts (environment norms : Json) (flags displayConstants joined : Bool) :
    decodeSource ActsHook.acts environment norms flags displayConstants joined =
      Today.decodeSource environment norms flags displayConstants joined
theorem decodeFlaggedActs_today (environment norms : Json) :
    decodeFlaggedActs environment norms = Today.decodeFlagged environment norms
theorem decodeNormsEnvironment_lexical (environment : Json) (displayConstants acts : Bool) :
    decodeNormsEnvironmentWith ActsHook.lexical environment displayConstants acts false =
      Today.decodeNormsEnvironment environment displayConstants acts false
theorem actsProfiles_eq_nil (acts : Bool) (environment : Json)
    (h : ∀ ps, VE.Route.Gate.profilesOf environment = .ok ps → "acts@0" ∉ ps) :
    actsProfiles acts environment = []
theorem decodeNormsEnvironment_plain (environment : Json) (displayConstants acts joined : Bool)
    (h : actsProfiles acts environment = []) :
    decodeNormsEnvironmentWith ActsHook.plain environment displayConstants acts joined =
      Today.decodeNormsEnvironment environment displayConstants acts joined
theorem decodeNormsEnvironment_plain_refuses (environment : Json) (displayConstants acts joined : Bool)
    (h : actsProfiles acts environment ≠ []) :
    decodeNormsEnvironmentWith ActsHook.plain environment displayConstants acts joined = .error actsHookRefusal
theorem decodeSource_plain (environment norms : Json) (flags displayConstants joined : Bool)
    (h : actsProfiles true environment = []) :
    decodeSource ActsHook.plain environment norms flags displayConstants joined =
      Today.decodeSource environment norms flags displayConstants joined
theorem decodeFlagged_plain (environment norms : Json) (h : actsProfiles true environment = []) :
    decodeFlagged environment norms = Today.decodeFlagged environment norms
```

`lean/VE/Acts/HookTwins.lean` (`Today.*`: main's `decoderOf`, `runCaseRouted`, `runCase`, `runAdmission` over
`HookToday.Today.decodeFlagged`):

```lean
theorem runCaseActsRouted_today (j : Json) : VE.Norms.Run.runCaseActsRouted j = Today.runCaseRouted j
theorem runCaseActs_today (j : Json) : VE.Norms.Run.runCaseActs j = Today.runCase j
theorem runCaseIn_congr {d₁ d₂ : SourceDecoder} {j : Json}
    (hE : ∀ n, d₁ (j.getObjValD "environment") n = d₂ (j.getObjValD "environment") n)
    (hD : ∀ e, VE.Compose.decidingEnvironment (j.getObjValD "environment") = .ok e → ∀ n, d₁ e n = d₂ e n) :
    VE.Norms.Run.runCaseIn d₁ j = VE.Norms.Run.runCaseIn d₂ j
theorem runCase_plain (j : Json) (hE : actsProfiles true (j.getObjValD "environment") = [])
    (hD : ∀ e, VE.Compose.decidingEnvironment (j.getObjValD "environment") = .ok e → actsProfiles true e = []) :
    VE.Norms.Run.runCase j = Today.runCase j
theorem runAdmission_plain (id : String) (environment document : Json) (h : actsProfiles true environment = []) :
    VE.Norms.Run.runAdmission id environment document = Today.runAdmission id environment document
theorem envelopeGate_actsProfiles {environment : Json} (h : Admission.envelopeGate environment = .ok ()) :
    actsProfiles true environment = []
theorem runAdmission_today (id : String) (environment document : Json) :
    VE.Norms.Run.runAdmission id environment document = Today.runAdmission id environment document
theorem runCaseRouted_today (j : Json) : VE.Norms.Run.runCaseRouted j = Today.runCaseRouted j
```

(also `admitDocumentIn_congr`, `runAdmissionIn_congr`, `replayEntailmentIn_congr`, `replayConflictIn_congr`,
`replayWitnessIn_congr`, `actsProfiles_nil_of_underActs`, `bind_congr_ok`, `getObjValD_of_ok`, `ok_bind`,
`error_bind`). All use only `propext`, `Classical.choice`, `Quot.sound` (lean/axioms.txt).

## Kernel figures and `--why`

`python3 tools/kernel_closure.py` (the saved `docs/kernel/closure-baseline.json`):

| Figure | Fork base `4a5d3460d3` | Branch before the merge | main `10e2bfb16b` (kb-8c, kb-10b-switch) | Merged HEAD |
|---|---:|---:|---:|---:|
| kernel, distinct lines | 10,023 | 8,985 | 11,119 | **10,081** |
| norms (theorems, spec, wrap, lines) | 21, 4,371, 2,709, 4,410 | 16, 3,217, 276, 3,461 | 21, 4,371, 2,709, 4,410 | 16, 3,217, 276, 3,461 |
| softNorms | 14, 5,368, 35, 5,376 | 14, 4,682, 35, 4,690 | same as fork base | 14, 4,682, 35, 4,690 |
| normsActs (candidate) | (in norms) | 6, 4,060, 2,702, 4,083 | (in norms) | 6, 4,060, 2,702, 4,083 |
| metered | 2, 3,352, 2,154, 3,358 | unchanged | unchanged | unchanged |
| quantity | candidate, 2,274 | candidate | kernel, 2,274 | kernel, 2,274 |
| keyed lines (under the five keys) | 16,777 | 16,543 | 16,777 | 16,543 |
| verdict writers outside the kernel | 56 | 56 | 56 | 56 |

The acts group (VE.Acts.*, VE.Grammar.Table): 15 modules, 1,185 lines in the kb-8b measure (docs/kernel/kb-4/MEASURE.md,
main `9a3fd7a9f9`); 7 modules, 289 lines now (docs/kernel/kb-4a/MEASURE.md, merged HEAD). What remains, with its chain
(`python3 tools/kernel_closure.py --why …` on the merged HEAD):

```
VE.Acts.Grammar: counted by no kernel path
VE.Grammar.Table: counted by no kernel path
VE.Acts.Elaborate: counted by no kernel path
VE.Acts.Lexical (121)
  norms spec: VE.Norms.FlaggedSpec.norms_wire_conflict_free -> VE.Norms.Wire.decodeSource -> VE.Norms.Wire.decodeNormsEnvironmentWith -> VE.Norms.Wire.decodeRegulatedWith -> VE.Acts.Lexical.Form
  softNorms spec: VE.SoftNorms.Run.soft_wire_acceptance -> VE.SoftNorms.Run.SoftAdmissionAnswer -> VE.SoftNorms.Run.BindingsMatchSourceAndRegeneration -> VE.Norms.Wire.canonicalEnvironmentJson -> VE.Norms.Wire.actsFixed -> VE.Acts.Lexical.Tok
  metered spec and wrap: … -> VE.Service.Standalone.regulatedOf -> VE.Norms.Wire.actsFixed -> VE.Acts.Lexical.Tok
VE.Acts.Syntax (73)
  softNorms spec: … -> VE.SoftNorms.Phases.declarations -> VE.Norms.Wire.ActsHook.lexical -> VE.Acts.Vocab
VE.Acts.LexicalBase (41)
  norms spec: VE.Norms.FlaggedSpec.norms_wire_conflict_free -> VE.Norms.Wire.ActsHook.plain -> VE.Norms.Wire.canonicalAct -> VE.Norms.Wire.words
VE.Acts.Tree (23)
  norms spec: VE.Norms.FlaggedSpec.norms_wire_conflict_free -> VE.Norms.Wire.ActsHook.plain -> VE.Acts.Act
VE.Acts.Wire (16)
  softNorms spec: … -> VE.SoftNorms.Phases.declarations -> VE.Norms.Wire.ActsHook.lexical -> VE.Norms.Wire.actsVocab -> VE.Acts.Wire.decodeVocab
VE.Acts.Hook (11)
  softNorms spec: … -> VE.SoftNorms.Phases.declarations -> VE.Norms.Wire.ActsHook.lexical
VE.Acts.Run (4)
  norms wrap: VE.Norms.Run.runCaseReported -> VE.Norms.Run.runCaseRouted -> VE.Acts.Run.isElaborate
```

`tests/test_kernel_closure.py::test_no_kernel_path_counts_the_act_grammar_or_the_elaboration` keeps the first three
lines (with `ActsHook.acts`, `actsOf`, `decodeNormsEnvironment` and `runCaseActsRouted`) as a test.

## Checks

| Check | Result | Tag |
|---|---|---|
| `cd lean && lake build` | `Build completed successfully (1460 jobs)` on the merged tree (`515bdb4cdc`) | AGENT |
| `python3 lean/audit.py` | `PASS: 888 source files; 10069 named theorem declarations audited …; only the declared standard axiom allowlist` | AGENT |
| `python3 tools/kernel_closure.py --check docs/kernel/closure-baseline.json` | `PASS: kernel 10081 <= 10081`, `PASS: verdict writers outside the kernel 56 <= 56` | AGENT |
| docs/kernel/ALLOWANCES.md | the kb-4a "fall" row (-1,038, total 10,081, "not needed (a fall, section 6.2)"); signed total 10,081 | AGENT |
| `python3 tools/trust_map.py --check` | exit 0: K +0, S +0, trusted +99 (V), signed by R16 (DELTA.md row 1) | AGENT |
| `python3 tools/check_lean_imports.py` | exit 0 (`Lean layer graph kept`) | AGENT |
| `uv run python tools/regen_generated.py --write` | 41 entries on the merged tree | AGENT |

## Frozen keys

On the merged tree's `ve_service` (`bc13008759`, after the merge of `10e2bfb16b`), script `/tmp/kb4a/keys.sh`:

| Key | Command | Result |
|---|---|---|
| Anthropic RSP | `uv run python usecases/anthropic-rsp/run.py --check` | exit 0 |
| OpenAI Preparedness | `uv run python usecases/openai-preparedness/run.py --check --base-only` | exit 0 |
| DeepMind FSF | `uv run python usecases/safety-framework/run.py --check` | exit 0 |
| agent-policy | `uv run python usecases/agent-policy/check.py base --write`, then a JSON comparison with the committed results.json | 6 differences, all timing: `M10.seconds` and the five `M10.policy_seconds` fields; restored with `git checkout` |
| eligibility | `uv run python usecases/eligibility/run.py --no-mutants` here and in a worktree of main `a84c072d76` (kb-8c; its shared Lean build), JSON comparison | 1 difference: `seconds` (204 on main, 273 here) |

## Tests

| Run | Result | Tag |
|---|---|---|
| `MAC_PYTEST_NO_DEFER=1 zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on the committed `515bdb4cdc` (clean tree) | 496 of 623 units selected; every unit passed but two: `tests/test_assurance_manifest.py` (4 tests: the new and changed Lean decoder files were not pinned or classified in ve/assurance-manifest.json) and `tests/test_consolidation_tools.py::test_committed_ledger_names_real_declarations` (docs/CONSOLIDATION-PLAN.md quotes step 8b's upper bound, every untied line of the units' `Wire.lean` files, which this item's +36 lines in Norms/Wire.lean raise from 3,788 to 3,824) | AGENT |
| the fix (`6e42a2f8b9`): the manifest pins and classes, the plan's row | `uv run pytest -q tests/test_consolidation_tools.py::test_committed_ledger_names_real_declarations tests/test_assurance_manifest.py`: 168 passed | AGENT |
| the test files that mention `acts@0` on main (34 by `git grep -l acts@0 main -- 'tests/*.py'`; none is edited here: `git diff --stat main...HEAD` on them is empty) | 27 ran in the selected run and passed; `tests/test_compose_dispatch.py` (not selected): 58 passed; `tests/test_regulated_limit.py` (main's, after the second merge): 18 passed; the other 5 are helper modules (`lean_service_corpus.py`, `profile_gate_oracle.py`, `b15b_model_cases.py`, `frozen_speech/*`) that selected tests import | AGENT |
| the service corpus (`tests/lean_service_corpus.py`, the recorded request/answer fixtures) | unchanged on this branch; the relay and schema tests that replay it ran in the selected run and passed (`tests/test_lean_service_schema.py`, `tests/test_relay_binding_inventory.py` and the mode tests that import it) | AGENT |
| `uv run python tools/gate_collection.py --check --prebuilt` | exit 0: `35263 collected …; 1 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers` | AGENT |
| the full release gate | not run here (the chain runs it on the final HEAD) | EXTERNAL |

## Trust mutants

`zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --build-timeout 3600 --test lean/VE/Acts/HookExamples.lean
--allow docs/kernel/kb-4a/trust-mutants-allow.json --rescore docs/kernel/kb-4a/trust-mutants.json --json
docs/kernel/kb-4a/trust-mutants.json` on `515bdb4cdc` (a full run: its inputs differed from the last one), VM1, 8 jobs:
**29 KILLED, 0 SURVIVOR, 0 UNKNOWN, 1 INVALID, 10 ALLOWED, 0 NOT RUN, exit 0** (17 definitions, 40 mutants; no Lean
changed after it). The ALLOWED ones (`trust-mutants-allow.json`, one reason each): the plain hook's `take 1` and
`reverse.take 1` of the profiles (it tests only emptiness); the decoder's `ps.take 1` and `ps.dropLast` on its act
checks (lines 282-283, where the envelope has admitted `ps` as `"acts@0" :: rest` with at least two more names, read
only through `contains "acts@0"`); and the default arguments of today's name and of `decodeSource`'s `flags`, which
no check can refute because a default is elaborated into the refuting check's own term (each flip is refuted by a
named #guard). Earlier runs found and the guards now kill: the dispatch's two `||` (an environment that reads
`acts@0` while its deciding gate refuses), the one-profile list, and the `flags`, `acts` and `joined` arguments the
hook's call sites carry (lean/VE/Acts/HookExamples.lean, lean/VE/Alternatives/HookExamples.lean,
lean/VE/NormDefaults/HookExamples.lean, lean/VE/Service/HookExamples.lean, and two #guards in
lean/VE/WireContract/Hooks/Acts.lean).

## Seeded bugs

`docs/kernel/kb-4a/seeded-bugs.json`; every seed is Lean (no Python or Rust product code changed).

| Seed | File | Mutation | Caught by |
|---|---|---|---|
| (a) S1 | lean/VE/Norms/Wire.lean | `ActsHook.plain` accepts the `acts@0` profiles (`pure (actsProfiles …)`), its joined check stays `pure []` | `lake build VE.Acts.HookToday`: `decodeNormsEnvironment_plain_refuses` does not build (HookToday.lean:126) |
| (b) S2 | lean/VE/Norms/Run.lean | `runCaseRouted` tests only `isElaborate`, so an `acts@0` environment reaches the plain runner | `lake build VE.Acts.HookTwins`: `runCaseRouted_today` does not build (HookTwins.lean:157) |
| (c) S3 | lean/VE/Norms/Wire.lean | `ActsHook.plain`'s `joined` calls `joinedActs` (a reference to the act grammar, behaviour unchanged) | `python3 tools/kernel_closure.py --check docs/kernel/closure-baseline.json`: `FAIL: the kernel grew from 8985 to 9698 lines`; `--why VE.Acts.Grammar`: `norms spec: 159 lines in 39 definitions; chain: VE.Norms.FlaggedSpec.norms_wire_conflict_free -> VE.Norms.Wire.ActsHook.plain -> VE.Norms.Wire.joinedActs -> VE.Norms.Wire.actsOf -> VE.Acts.RuleS` |

(Measured before the merge with kb-8c, when the signed total was 8,985.)

## Spec re-read

- "`joinedActs` is `if joined && ps.contains "acts@0" then actsOf … else pure []`" against lean/VE/Norms/Wire.lean (main 180-182): the hook's `joined` is `joinedActs` itself in `ActsHook.acts`.
- "`canonicalShape` falls back to `canonicalAct`" against main 46-48: `ActsHook.plain.shape` and `.check` are `canonicalAct`.
- "where the environment lists `acts@0` it refuses with `UnsupportedProfile: acts@0 needs the acts decoder`" against `actsHookRefusal`: the text is the task's; "lists" is read as "from which `acts@0` is read" (`actsProfiles`), the condition under which today's decoder reads the profile; an unsorted list that lists it is not read today and is refused by the envelope as today (HookExamples `unsorted` guards).
- "`runCaseRouted` (Run.lean:227-229) equal to today's": `runCaseRouted_today` states equality on every `j`, with no hypothesis.
- "the norms service mode is listed under both paths' modes": `tools/kernel-paths.json`, `norms.modes` and `normsActs.modes` are `["norms"]`.
- "tier candidate with the note …": `normsActs.note` is the task's text verbatim.

## Notes for the DRI

- D1. The parameterised decoder is named `decodeNormsEnvironmentWith`, not `decodeNormsEnvironment`. Today's name keeps
  today's signature as `decodeNormsEnvironmentWith ActsHook.acts` (lean/VE/Acts/Hook.lean). The one caller that uses it,
  lean/VE/EnglishGrammar/Norm/Rules.lean, is pinned by the English grammar lock (ve/english_grammar/LOCK.json): a
  change there needs a new `actions_version`, which every English answer carries as an identity, so the item would
  change answer bytes. The conservative choice keeps that file byte-identical; every other caller names its hook.
- D2. A third instance, `ActsHook.lexical` (today's acts operations without the joined-act reader), for
  `SoftNorms.Phases.declarations`. The task gives it `ActsHook.acts`, but the soft frame calls with `joined := false`,
  where `joinedActs` reads nothing, and with `ActsHook.acts` the softNorms spec would still count `VE.Acts.Grammar` and
  `VE.Grammar.Table` (the acceptance forbids it). `decodeNormsEnvironment_lexical` proves it is today's at
  `joined := false`.
- D3. The dispatch also tests the environment a `norms-elaborate` case decides over (`decidesActs`), so the plain
  runner meets no environment from which `acts@0` is read and `runCaseRouted_today` holds on every input without a
  hypothesis. I expect the extra test not to change the route for parsed JSON (removing a document layer keeps
  `acts@0`'s reading) but did not prove it: a Lean `Json` value need not be well formed, and the equality is claimed
  for every value. Either way the answer is today's (the theorem).
- D4. Admission keeps the plain runner at every caller: `Admission.envelopeGate` refuses every environment from which
  `acts@0` is read before the decoder runs, so no caller relied on today's acceptance (`runAdmission_today`).
- D5. What stays of the acts group in the kernel (289 lines) is listed above: the `VE.Acts.Act` type of
  `NormsEnvironment.joined` and the hook's `joined` field (Acts.Tree, 23), `canonicalAct`'s words (LexicalBase, 41),
  the plain act's form check in `decodeRegulatedWith` and `canonicalEnvironmentJson`'s act canonicalisation (Lexical,
  121; also counted by `metered`, row kb-4b), the soft frame's `acts` block (Syntax 73, Wire 16, Hook 11) and
  `isElaborate` (Run, 4).
- D6. `docs/kernel/kb-4/MEASURE.md` is kb-8b's measure before this item and is kept; the regenerated measure, by the
  same method (its script embedded), is `docs/kernel/kb-4a/MEASURE.md`.
- `normsActs` is not added to the registry's `keys.paths`: no frozen key reads `acts@0`
  (docs/kernel/kb-validators/part2-measure.json section ii). The keyed figure falls with the kernel (16,777 to 16,543).
- The frozen copies (`VE.Acts.HookToday.Today.*`, `VE.Acts.HookTwins.Today.*`) are proof helpers (class P); they are
  what "today's definition" means in the equality theorems and no product code reads them.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A., no response shape, relay or schema changes; the norms mode's answers are today's on every input (`runCaseRouted_today`), and the response-shape theorems still build (`ResponseShape.Encoders.Norms.runCaseReported_fits`, `ResponseShape.Encoders.Discourse.dispatchAdmission_fits`, `lake build`).
2. Every deliverable built, no rule broken: PASS, "Task deliverables" table; one owner: today's acts code is referenced, not copied, by `ActsHook.acts` (the frozen `Today.*` copies are proof helpers, class P, read only by the equality theorems); no new permanent report test.
3. Tests and gates can fail: PASS, seeded bugs S1-S3 (`docs/kernel/kb-4a/seeded-bugs.json`: `decodeNormsEnvironment_plain_refuses`, `runCaseRouted_today`, `kernel_closure.py --check`), trust mutants 29 KILLED / 0 SURVIVOR / 0 UNKNOWN with the evidence and allow file committed.
4. Python, Lean and Rust agree: N.A. for Python and Rust (no decision moved); Lean against main: the five keys' results ("Frozen keys") and the equality theorems.
5. R8 binding: N.A., no field Python reads from a Lean answer changed.
6. Gate evidence matches the final HEAD: PASS for this item's evidence (synced with main `e51bec7301`; the kernel figures, trust mutants and selected run name their commits; no Lean changed after `515bdb4cdc`); the full gate is the chain's.
7. No unsigned item: PASS, DELTA.md rows cite R16 (trust +99, `python3 tools/trust_map.py --check` exit 0, the trust mutants, FOLLOW-UPS.md ties row) and R12 (generated files).
8. Every user-visible change in DELTA: PASS, no answer changes (`runCaseRouted_today`, `runAdmission_today`, `runCaseActs_today`, `decodeSource_acts`; the five keys); the plain decoder's new refusal is reached by no entry (DELTA.md preamble).
9. Test selection finds the tests: PASS, the selection ran tests/test_kernel_closure.py (the test of S3) and the 27 selected `acts@0` files; the two unselected ones (`test_compose_dispatch.py`, `test_regulated_limit.py`) were run by hand and pass.
10. Lean statements say what is claimed: PASS, S1 and S2 break `decodeNormsEnvironment_plain_refuses` and `runCaseRouted_today`; the equality theorems are about the returned value (`runCaseRouted j = Today.runCaseRouted j`, no hypothesis); no hypothesis was added to a listed statement (three name `ActsHook.plain` in their decoder, lean/statements.txt).
11. Budgets, limits and deadlines fail closed: N.A., no budget, limit or deadline touched (the 64-predicate limit and the envelope order are today's, by the equality theorems).
12. No CPU or memory regression: N.A. by construction for `acts@0` documents (today's runner) and for plain ones (the plain hook does less: no `acts` block read); not timed.
13. Test-removed trailers: PASS, no test removed or renamed; `uv run python tools/gate_collection.py --check --prebuilt` exit 0 (0 refused, 0 stale, 0 malformed).
14. Both directions, cited evidence, spec re-read: PASS, the #guards test each check both ways (plain refuses `envA` and accepts `plainEnv`; the dispatch sends `joinedE` and `judgedA` to today's runner and `plainCase` to the plain one; flags admitted where asked and refused where not); every claim above names its command; "Spec re-read" section.
15. No overclaim, no silent cut, every check can fail, limits before work: PASS, the universal claims ("every input", "no kernel path") are theorem statements or `--why` outputs; D1-D6 record each deviation instead of a cut; each new #guard kills a recorded mutant (trust-mutants.json); N.A. for limits.
