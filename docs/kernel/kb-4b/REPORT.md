# kb-4b: the `metered` runner split (frozen envelope, acts, current)

**Summary.** Built; no DRI signature needed (DELTA rows cite R16 and R12). The `metered` mode's entry answers a frozen
`ve.core@0`/`@0.1` envelope with `runCaseReportedLegacy`, an environment whose deciding view reads `acts@0` with
`runCaseReportedActs` (candidate paths `meteredLegacy` and `meteredActs`), and every other case with the current runner
(`runCaseCurrent`, the `metered` kernel path), each answering exactly as `runCase` does (theorems below). The current
runner's validation and model view reference no typing reduction, no frozen decoder and no acts view. Kernel 9,991 to
9,738 lines (-253); `metered` path 3,238 to 2,883. No answer byte changes (equality theorems; the five keys' 24,385
metered answers compared before and after). Open: none blocking; deviations from the task's letter are D1-D9 under
"Notes for the DRI"; the full gate is the chain's.

SIZE: 650 product, 152 tests, 726 other hand-written lines (`git diff --numstat` against the merge base, generated
files excluded; product: the Lean of lean/VE/Service/Standalone.lean, lean/VE/Route/MeteredRun.lean,
lean/VE/Route/MeteredSplit.lean (the proofs, 294), lean/VE/Route/MeteredWire.lean, lean/VE/Norms/Plain.lean,
lean/VE/Service/Protocol.lean, lean/ResponseShape/Encoders/Metered.lean, lean/VE.lean; tests:
lean/VE/Route/MeteredSplitExamples.lean (103) and tests/test_kernel_closure.py (49); other: these three docs, CALLS.md,
seeded-bugs.json, the allow file, the registry, the trust table and allowance and the records; besides, 435 lines of
evidence JSON written by scripts and tools: calls.json, keys-answers.json, timing.json, trust-mutants.json).

## Step 1: CALLS.md

[CALLS.md](CALLS.md) (committed `dd05d8f46`, before any Lean change). Its table:

| Key | `metered` calls | (a) legacy `language` | (b) `judgments@0` | (c) `acts@0` | (d) `norms@0` + `regulated` | (e) layered core |
|---|---:|---:|---:|---:|---:|---:|
| eligibility | 0 | | | | | |
| Anthropic RSP | 2,311 | 0 | 0 | 0 | 0 | 0 |
| OpenAI Preparedness | 36 | 0 | 0 | 0 | 0 | 0 |
| DeepMind FSF | 10,209 | 0 | 0 | 0 | 0 | 0 |
| agent policy | 11,829 | 0 | 0 | 0 | 480 | 0 |
| **keys** | **24,385** | **0** | **0** | **0** | **480** | **0** |
| the 87 test files that reach `evaluate` (`evaluate-budgeted` cases) | 137,397 | 66,707 | 0 | 0 | 8,368 | 11 |

No frozen key sends (a), (b) or (c): the stop condition does not hold, and every keyed call is the current runner's.

## The split and its theorems (verbatim)

lean/VE/Route/MeteredSplit.lean (namespace `VE.Service.Standalone`, then `VE.Route.MeteredRun`):

```lean
theorem validated_today (environment : Json) (typing : Bool) :
    validated environment typing = Today.validated environment typing

theorem validated_plain (environment : Json) : validated environment false = validatedPlain environment

theorem evaluableActs_today (environment : Json) :
    evaluableActs environment = (do validated (← VE.Compose.decidingEnvironment environment))

theorem validatedCurrent_eq (view : Json)
    (h : (VE.Norms.Wire.actsProfiles true view).isEmpty = true) :
    validatedCurrent view = validatedPlain view

theorem regulatedOfWith_plain (environment : Json)
    (h : (VE.Norms.Wire.actsProfiles true environment).isEmpty = true) :
    regulatedOfWith VE.Norms.Wire.ActsHook.plain environment = regulatedOf environment

theorem profileTreeWith_plain (environment : Json)
    (h : (VE.Norms.Wire.actsProfiles true environment).isEmpty = true) :
    profileTreeWith VE.Norms.Wire.ActsHook.plain environment = profileTree environment

theorem modelEnvironment_current (environment view : Json) (e : VE.Route.Gate.Envelope)
    (hD : VE.Compose.decidingEnvironment environment = .ok view)
    (hdrop : modelViewDropped environment view = false)
    (he : VE.Route.Gate.decodeEnvelope view = .ok e) :
    modelEnvironment environment = modelEnvironmentCurrent environment

theorem prepare_legacy (environment : Json) (h : isLegacy environment = true) :
    prepare environment = prepareLegacy environment

theorem prepare_acts (environment : Json) (h : isLegacy environment = false) :
    prepare environment = prepareActs environment

theorem runWith_prepare_current (environment j : Json) (hl : isLegacy environment = false)
    (ha : readsApart environment = false) :
    runWith (.ok (prepare environment)) j = runWith (.ok (prepareCurrent environment)) j

theorem runWith_split (j : Json) :
    runWith (prepare <$> j.getObjVal? "environment") j =
      if legacyCase j then runWith (prepareLegacy <$> j.getObjVal? "environment") j
      else if actsCase j then runWith (prepareActs <$> j.getObjVal? "environment") j
      else runWith (prepareCurrent <$> j.getObjVal? "environment") j

theorem runCase_split (j : Json) :
    runCase j = if legacyCase j then runCaseLegacy j else if actsCase j then runCaseActs j
      else runCaseCurrent j

theorem runCaseReported_today (j : Json) :
    runCaseReported j = reportedWith (prepare <$> j.getObjVal? "environment") j

theorem reportedWith_prepare (j environment : Json) (h : j.getObjVal? "environment" = .ok environment) :
    reportedWith (.ok (prepare environment)) j = runCaseReported j
```

Also `regulatedOf_today`, `regulatedOf_lexical`, `checkRegulated_today` and `profileTree_today` (rfl; the reshaped
readers are their bodies before). The restated wire theorems, lean/VE/Route/MeteredWire.lean, all proved from today's
proof through one lemma `wire_sound_of (prep : Json → Prepared)` (today's `metered_wire_sound` is `wire_sound_of
prepare`):

```lean
theorem metered_wire_sound_current (j answer : Json) (h : runCaseCurrent j = .ok answer)
    (hk : VE.Bridge.stringField j "kind" = .ok "evaluate-budgeted") :
    ∃ (id : String) (environment : Json) (checked : VE.Service.Standalone.Validated) (model : Json)
      (q : Query),
      VE.Bridge.stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok environment ∧
      VE.Service.Standalone.evaluableCurrent environment = .ok checked ∧
      CaseModel j checked (prepareCurrent environment) model ∧
      query j id false = .ok q ∧ q.id = id ∧
      EvaluationAnswer q checked (prepareCurrent environment) model answer
```

`metered_wire_sound_legacy` and `metered_wire_sound_acts` are the same with `runCaseLegacy`/`evaluableLegacy`/
`prepareLegacy` and `runCaseActs`/`evaluableActs`/`prepareActs`. `runWith_sound` is stated for every `Prepared`, so it
holds for each runner as written and is listed on all three paths (D5).

How the deliverables map:

| Task | Where |
|---|---|
| (1) `validatedPlain`, no reference to `typingReduced`, `riskReduced`, `Typed.typingEnvironment`; `validated env false = validatedPlain env`; `evaluable` calls it | `Standalone.validatedPlain` = `validatedOver (checkRegulated env) none (← actsRead env)`; `validated_plain`; `evaluable` = `if isLegacy then evaluableLegacy else evaluableActs` and `evaluableActs` calls `validatedPlain` (`evaluableActs_today`) (D2) |
| (2) the legacy arm its own runner and path; the split theorem; the current runner references no legacy decoder | `runCaseLegacy`, `runCase_split`; `--why` below; path `meteredLegacy` |
| (2) `metered_wire_sound`, `runWith_sound` per runner, from today's proof | `metered_wire_sound_{current,legacy,acts}` via `wire_sound_of`; `runWith_sound` (D5) |
| (2) handle table statements unchanged, proofs adapted | `Entry.prepared_eq`, `caseResultWith_entry`, `caseResult_cached` (lean/VE/Service/Protocol.lean): no statement or proof text changed; `reportedWith_prepare` (which `caseResultWith_entry` reads) keeps its statement and is now proved from `runCaseReported_today`; the encoder theorem `ResponseShape.Encoders.Metered.runCaseReported_fits` keeps its statement, proof adapted |
| (3) `acts@0` through kb-4a's hook in a runner of its own; the current runner references nothing under `VE.Acts.*` beyond `LexicalBase` | `runCaseActs` reads the regulated extension with `ActsHook.lexical`'s operations (`regulatedOf_lexical`; D3); the current runner with `ActsHook.plain` (`regulatedOfWith`); what remains of `VE.Acts.*`: D4 |
| (4) `judgments@0` arm stays; its counted lines | below |
| Registry | `metered` (kernel: entry `runCaseReported`, theorems `runWith_sound`, `metered_wire_sound_current`, delegates the two reported runners); `meteredLegacy`, `meteredActs` (candidate, note "runner theorems complete; outside the kernel tier by the architect seat (D14): …"); `tests/test_kernel_closure.py::test_the_metered_mode_lists_every_runner_arm` |

## Kernel and per-path figures

`VE_NATIVE_PREBUILT=1 python3 tools/kernel_closure.py` before (merge base `b8abce49e`, `/tmp/kb4b/table-before.log`)
and after (`968f450b2`, `docs/kernel/closure-baseline.json`, written by `tools/regen_generated.py --write --only
kernel-closure`):

| Path | Tier | Spec | Wrap | Lines before | Lines after |
|---|---|---:|---:|---:|---:|
| metered | kernel | 2,843 | 40 | 3,238 | 2,883 |
| meteredLegacy | candidate | 2,457 | 6 | | 2,463 |
| meteredActs | candidate | 3,133 | 6 | | 3,139 |
| readingsRoute | candidate | 9,349 | 14,974 | 24,257 | 24,263 |
| discourse | candidate | 36,266 | 11 | 36,232 | 36,272 |
| document | candidate | 35,349 | 900 | 36,197 | 36,242 |
| **kernel** | | | | **9,991** | **9,738** |
| keyed lines (validators in full) | | | | 16,269 | 16,341 |

Every other path is unchanged. The kernel falls by 253 lines, below the assumed 300-600 (D6). The keyed figure rises
by 72 (D7). The verdict writers outside the kernel stay at 56 (`PASS: verdict writers outside the kernel 56 <= 56`).

`--why` on the final tree (`/tmp/kb4b/why-after.log`, and `tests/test_kernel_closure.py::
test_no_kernel_path_counts_the_typing_reductions_or_the_frozen_decoders`):

```
VE.Service.Standalone.typingReduced: counted by no kernel path
VE.Service.Standalone.riskReduced: counted by no kernel path
VE.Service.Standalone.decodeLegacy: counted by no kernel path
VE.Route.Typed.typingEnvironment: counted by no kernel path
VE.Service.Standalone.actsRead: counted by no kernel path
VE.Service.Standalone.modelEnvironment: counted by no kernel path
VE.Bridge.decodeEnvironment: counted by no kernel path
VE.Acts.Lexical
  metered spec: 5 lines in 3 definitions; chain: VE.Route.MeteredRun.metered_wire_sound_current -> VE.Route.MeteredRun.prepareCurrent -> VE.Service.Standalone.profileTreeWith -> VE.Service.Standalone.regulatedOfWith -> VE.Norms.Wire.decodeRegulatedWith -> VE.Acts.Lexical.Form
```

Before, `typingReduced` was counted twice over: through `evaluable -> validated` (spec) and through `prepare ->
modelEnvironment` (wrap, the norms profile's model view); the task named the first. The second is why the current
runner has its own model view `modelEnvironmentCurrent`, equal to `modelEnvironment` wherever it is read
(`modelEnvironment_current`; D1).

### The `judgments@0` arm's counted lines

Measured by replacing the deciding view with the identity in the current runner's three readers (`evaluableCurrent`,
`modelEnvironmentCurrent`, `readsApart`) in a scratch copy of lean/ (not committed) and re-running the tool
(`/tmp/kb4b/table-nojudg.log`): the `metered` path is 2,715 lines without the arm and 2,883 with it, so **the arm
counts 168 of `metered`'s lines** (`decidingEnvironment` and what it reads: `layersApart`, `gateOf profileTable` and the
table's rows, `withoutDocumentLayers`, `listedProfiles`). The kernel total would fall by only 2 (9,738 to 9,736): the
`norms` path counts the same table through `VE.Norms.Run.decidesActs` (`--why VE.Compose.decidingEnvironment`: `norms
wrap: … runCaseRouted -> decidesActs -> decidingEnvironment`).

## Checks

| Check | Result |
|---|---|
| `cd lean && PATH=~/.elan/bin:$PATH lake build` | `Build completed successfully (1478 jobs).` (`/tmp/kb4b/wt-build.log`) |
| `python3 lean/audit.py` | `PASS: 898 source files; 10153 named theorem declarations audited …; only the declared standard axiom allowlist.` (`/tmp/kb4b/audit.log`) |
| kernel check on the regenerated baseline, ALLOWANCES "fall" line | `docs/kernel/ALLOWANCES.md` row 2026-11-16 kb-4b (-253, "not needed (a fall, section 6.2)"), signed total 9,738; `tools/kernel_closure.py --out` printed `signed total 9991 >= kernel 9738` and `PASS: verdict writers outside the kernel 56 <= 56`; `tests/test_kernel_closure.py::test_the_records_quote_the_saved_measurement` passes (the spec table, its totals, the frozen keys' figures and the signed total) |
| `uv run python tools/trust_map.py --check` | `K +0, S +0 … trusted +47`, `PASS` after the R16 allowance (DELTA row 1) |
| `uv run python tools/regen_generated.py --check` | on the final tree (`bc93a6a02`): `regen_generated: checked 41 entries`, exit 0 (`/tmp/kb4b/regen-check2.log`); before the R16 allowance only `trust-tables` failed; the `binding_census` lines are notes about ve/readings_route.py, which this branch does not touch |
| the five keys byte-identical | [keys-answers.json](keys-answers.json): every `metered` case and its answer row digested (SHA-256 of the sorted-key JSON) by the recorder of CALLS.md, before (`b8abce49e` build) and after (`968f450b2` build): the multiset of (case, answer) digests is the same for each key (agent policy 11,829, RSP 2,311, Preparedness 36, FSF 10,209; eligibility sends none); every harness exited 0 both times and the eight `usecases/*/results.json` kept their SHA-256 (`sha rc=0`) |
| `evaluate`'s median time | [timing.json](timing.json): one captured agent-policy case and one RSP case, each 200 times per run through the one-shot `ve_metered`, 15 interleaved runs per build: agent policy 0.740 s before, 0.743 s after (1.004×); RSP 1.063 s before, 1.034 s after (0.972×); the outputs were byte-identical |
| the service corpus and the tests that reach `evaluate` | the selected run below |

## Tests

| Run | Result |
|---|---|
| `VE_NATIVE_PREBUILT=1 uv run pytest -q tests/test_kernel_closure.py -k "metered_mode_lists or typing_reductions or records_quote or registry or every_path or act_grammar or why_names"` | `9 passed, 36 deselected` (`/tmp/kb4b/t-kc.log`) |
| `lake build VE.Route.MeteredSplitExamples` (the dispatch #guards) | builds |
| `MAC_PYTEST_NO_DEFER=1 zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on the committed `33aa14181` (clean tree; ran on the VM, the Mac unreachable) | 535 units: 534 passed, 1 failed: `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` (the two new Lean files were not classified in ve/assurance-manifest.json). Fixed in `bc93a6a02` (their `other_json` reasons); `uv run pytest -q tests/test_assurance_manifest.py`: `167 passed` (`/tmp/kb4b/t-am.log`). Every test file that reaches `evaluate` (CALLS.md's 87) and the service corpus's replays (`tests/test_lean_service_schema.py`, `tests/test_lean_handles.py`, `tests/test_metered_handles.py`) ran in it and passed |
| `uv run python tools/gate_collection.py --check --prebuilt` | exit 0: `35624 collected, 35622 at b8abce49e…; 2 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers` (`/tmp/kb4b/gc.log`; no test removed or renamed) |
| the full release gate | not run here (the chain runs it on the final HEAD) |

## Trust mutants

`zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --build-timeout 3600 --test
lean/VE/Route/MeteredSplitExamples.lean --test lean/VE/Route/MeteredProfileExamples.lean --allow
docs/kernel/kb-4b/trust-mutants-allow.json --json docs/kernel/kb-4b/trust-mutants.json` on `bf187fb1d` (ran on the VM,
8 jobs, 1,528 s): **18 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 4 ALLOWED, 0 NOT RUN, exit 0** (6 definitions, 22
mutants; no Lean changed after it). The first run, on `968f450b2` (before the guards), had 9 KILLED, 12 SURVIVOR and
1 UNKNOWN: `validatedOver`'s typing condition (`&&` to `||`, `==` to `!=`), six list mutants of `modelViewProfiles`, and
the four now ALLOWED. The guards added in `bf187fb1d` (lean/VE/Route/MeteredSplitExamples.lean) kill the first eight:
`validated e t` equals its frozen copy `Today.validated e t` on eight environments for both values of `t`; the current
runner's validation and norms profile equal today's where it runs, and it refuses an `acts@0` view with
`actsHookRefusal`; a layered core environment keeps its layers apart without typing and not with it; and the
model-view profiles are the four `modelEnvironment` reads apart. ALLOWED (`trust-mutants-allow.json`, one reason each):
the default `typing := false` of `validated` (a default is elaborated into the refuting check's own term; the guards
refute both values), `regulatedBy`'s `ps.take 1` and `ps.dropLast` (equivalent: `fixed` reads only emptiness, and a
nonempty `ps` has `acts@0` and the base profile), and `profileTreeBy`'s `predicates -> []`, which does not elaborate.

## Seeded bugs

[seeded-bugs.json](seeded-bugs.json); all Lean (no Python or Rust product code changed), planted in a scratch copy of
lean/ at the final sources and restored:

| Seed | File | Mutation | Fails |
|---|---|---|---|
| (a) | lean/VE/Route/MeteredRun.lean | `legacyCase` answers false on every case: a frozen envelope goes to the current runner | the split theorem fails to build: `lake build VE.Route.MeteredSplit` stops at `legacyCase_ok` (MeteredSplit.lean:250, unsolved goals), the lemma `runWith_split`/`runCase_split` rest on |
| (b) | lean/VE/Service/Standalone.lean | `validatedPlain` passes `fun _ => pure ()` as the regulated check | `validated_plain` (MeteredSplit.lean:89) and `validatedCurrent_eq` (:126) fail to build |
| (b') | lean/VE/Service/Standalone.lean | the shared body `validatedOver` skips the regulated check and strip | `validated_today` (MeteredSplit.lean:72) fails to build against the frozen copy |
| (c) | lean/VE/Route/MeteredWire.lean | `metered_wire_sound_current` stated about `runCase`, `evaluable`, `prepare` | `--why VE.Service.Standalone.decodeLegacy`: `metered spec: 20 lines; chain: VE.Route.MeteredRun.metered_wire_sound_current -> VE.Service.Standalone.evaluable -> VE.Service.Standalone.evaluableLegacy -> VE.Service.Standalone.decodeLegacy`; `--check` exits 1 (`FAIL: the kernel grew from 9738 to 10081 lines`) |

The experiment that measured the `judgments@0` arm also showed the examples catch a change of the deciding view: the
`#guard` that the entry answers each example as today failed (MeteredSplitExamples.lean:62).

## Notes for the DRI

- D1. The model view. `prepare`'s norms profile reads `modelEnvironment`, which ends in `typingReduced`. On every
  environment the current runner reads, that view is the deciding view (`modelEnvironment_current`: the route gate
  admits only known profiles, so no statement profile is listed and no `unit_schema` field is left). For a
  `judgments@0` environment the proof needs the profiles of `withoutDocumentLayers environment`, which go through
  `setObjVal!`; the toolchain proves that lookup only for well-formed objects (`Std.TreeMap.Raw.getElem?_insert_self`
  needs `WF`). So the dispatch predicate `readsApart` also names `modelViewDropped` (an environment that lists a
  model-view profile its deciding view does not): never true of a parsed JSON object, and such a case goes to the acts
  runner, today's code. CALLS.md's column (f): no key and no test sends a candidate for it.
- D2. `validatedPlain` and `validated` share one body, `validatedOver` (the typing step passed in): one owner rather
  than a second copy. `validated_plain` is then `rfl`, so seeded bug (b) is planted in `validatedPlain` itself, and
  `validated_today` pins `validated` (every mode's) to its body before kb-4b with a frozen copy (P), which catches a
  mutation of the shared body (b').
- D3. The acts runner reads the regulated extension with the operations of `ActsHook.lexical` (kb-4a's `ActsHook.acts`
  without the joined-act check, which this reader never runs; `regulatedOf_lexical`), and `regulatedOf` passes them
  one by one instead of the hook constant: through the constant, the validators that read `regulatedOf` would count the
  hook's acts vocabulary decoders too.
- D4. The current runner still reads 5 lines of `VE.Acts.Lexical` (`Form`, through the plain regulated decoder
  `Norms.Wire.decodeRegulatedWith`) and the `ActsHook` structure (the `VE.Acts.Act` type of its `joined` field), as
  the plain norms path does (kb-4a D5). Separating them changes the norms decoder, outside this item.
- D5. `runWith_sound` is stated for every prepared environment, so it is one statement for the three runners; the
  per-runner restatements are `metered_wire_sound_{current,legacy,acts}`.
- D6. The kernel falls by 253 lines, not the assumed 300-600: the `judgments@0` arm stays (168 lines of `metered`), the
  dispatch is 34 new wrap lines, and the current runner has its own validation and model view.
- D7. The keyed lines rise by 72 (16,269 to 16,341): the current runner's declarations are new lines under the keys,
  while the validators (counted in full) still read the definitions it no longer does.
- D8. The test-suite measurement ran the 87 test files the coverage map records under `evaluate` and `_metered`; a
  first run of all 188 `_metered` files was stopped on a VM at load 120 (its partial rows were discarded).
- D9. The service's handle table keeps today's `prepare` in its entries; a held case answers as the unhandled case
  does through `reportedWith_prepare`, now proved from `runCaseReported_today`.

## Spec re-read

- "`runCase` of the metered mode answers every input exactly as today": `runCase` is unchanged and `runCase_split`
  states the three runners against it, against the task text, STEP 2.
- "`runCaseCurrent` references no legacy decoder (`decodeLegacy`, `VE.Bridge`'s and `VE.Core.Bridge`'s legacy
  functions: check with `--why`)": `decodeLegacy`, `VE.Bridge.decodeEnvironment` and `VE.Closure.Bridge.decodeEnvironment`
  are counted by no kernel path; `VE.Core.Bridge.decodeEnvironment` is the core family's current vocabulary decoder
  (`prepareOf`'s `core` thunk), which the current runner reads as today, against the task text, STEP 2 (2).
- The registry note "runner theorems complete; outside the kernel tier by the architect seat (D14)" begins both new
  paths' notes, against the task text, Registry.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relayed answer, schema or Python reader changes; the metered answers are byte-identical: keys-answers.json, `runCaseReported_today`).
2. Every deliverable built, no rule broken: PASS (the deliverables table above maps each task line to its commit and check; one owner kept: `validated` and `validatedPlain` share `validatedOver`, D2; no Python copy of a Lean decision; no permanent report test).
3. Tests and gates can fail: PASS (seeded-bugs.json (a), (b), (b'), (c); trust-mutants.json 18 KILLED, 0 SURVIVOR, exit 0, with trust-mutants-allow.json).
4. Python, Lean and Rust agree, valid inputs pass: PASS (keys-answers.json, same multiset of case and answer digests for 24,385 keyed cases; timing.json outputs byte-identical; the #guard comparing the entry with `reportedWith (prepare …)` on eight cases).
5. R8 binding: N.A. (no field Python reads changes).
6. Gate evidence matches the final HEAD: PASS (main has not moved since b8abce49e, `git log HEAD..main` empty; the selected run is on the committed `33aa14181`; after it, `bc93a6a02` (ve/assurance-manifest.json, the failed test rerun and passing) and docs/kernel/kb-4b/*.md; the full gate is the chain's on the final HEAD).
7. No unsigned item: PASS (DELTA rows 1 and 2 cite R16 and R12; the R16 conditions: per-file itemisation re-measured with `tools/trust_map.py --check`, trust-mutants.json, FOLLOW-UPS.md ties-pass row).
8. Every user-visible change in DELTA: PASS (no answer changes: `runCaseReported_today`, `validated_today`, keys-answers.json; the non-answer deltas are DELTA rows 1-2).
9. Test selection finds the tests: PASS (`tools/select_tests.py --base b8abce49e` selects 516 files, among them tests/test_kernel_closure.py, test_metered_profile.py, test_metered_answer.py, test_metered_lean.py, test_metered_handles.py, test_lean_service_schema.py, test_lean_handles.py; `/tmp/kb4b/select-plan.log`).
10. Lean statements say what is claimed: PASS (seeded bugs (a)-(c) break the build or the kernel check; `metered_wire_sound_current` is about `runCaseCurrent`, the value the entry returns for its arm: `runCaseReported_today`).
11. Budgets fail closed: N.A. (no budget, limit or deadline changes; the runners share `runWith`'s `Metered.limit` and `max_evaluations`).
12. No CPU or memory regression: PASS (timing.json: median 1.004× agent policy, 0.972× RSP over 200 cases × 15 runs).
13. Test-removed trailers: N.A. (no test removed or renamed; `tools/gate_collection.py --check --prebuilt`: 0 stale, 0 malformed).
14. Both directions, cited evidence, spec re-read: PASS (the dispatch #guards name each arm; the current runner's validation equals today's on the environments it takes and refuses an `acts@0` view; the layered guard checks both typing modes; claims cite their commands; "Spec re-read" above).
15. No overclaim, no silent cut, checks can fail, limits before work: PASS (universal words in this report cite `--why`, the theorems or keys-answers.json; no deliverable cut (D1-D9 are deviations of form, each named); every new #guard is killed-tested by trust-mutants.json; limits N.A. as 11).
