# kb-validators build report: `metered` checks and states the norms profile; the validators measured

Status: parts 1 and 2 done; READY for the chain gate. No DRI signature is needed (DELTA rows cite R7, R16, R12). Code HEAD `78c92cdde1` on merge base `0f6d59d441`.
Changed: `metered` applies the `model` mode's profile check (`Plain.profileOkOn`) on every family; `runWith_sound` and `metered_wire_sound` gain the conjunct `ProfileAdmits`.
Acceptance: no keyed call is refused; RSP, Preparedness and FSF `--check` pass on the final binary; agent-policy and eligibility match (timing fields only). `lake build` passes, and `lean/audit.py` passes with no new axiom.
Kernel 9,552 to 9,620 (+68, inside the signed +80). Trust K +0, S +16, V +21 (R16). Trust mutants exit 0.
Open: none. Part 2 is for the architect seat's ruling on (ii) and (iii). The full release gate is the chain's (not run here).

SIZE: 103 product, 306 tests, 164 other hand-written lines (plus this report; 323 generated and 507 evidence lines not counted) (`git diff --numstat 0f6d59d441 HEAD`: product = `lean/VE/**` outside the examples file; tests = `tests/**` and `lean/VE/Route/MeteredProfileExamples.lean`).

## Deliverables

| Task line | Where | Shown by |
|---|---|---|
| Part 1: in `run`, when the environment declares regulated predicates, apply the same check the `model` mode applies, from the same tree built the same way; share the code | `VE.Route.MeteredRun.profiled`, called after the model decoder in all four families (`ebbb7d94a6`). The tree is `Prepared.profile` = `Standalone.profileTree (Standalone.modelEnvironment environment)`, and `modelCase` now calls the same `profileTree` (`Standalone.lean`, it was lines 612-615). The check is `Plain.profileOkOn`, which `profileOk` (the `model` mode) also runs. | `tests/test_metered_profile.py`; `#guard`s in `MeteredProfileExamples.lean`; `prepare_profile` |
| Families fol and closure, "and the others if the profile applies to them: say what you found" | It applies to all four. The `model` mode applies `profileOk` after the family decoder on every non-frozen family, and `validated` admits a `norms@0` pair on the nary and order families (probe: a case on each is answered within the permission and refused beyond it). So `profiled` runs in fol, closure, closureNary and order. A frozen `ve.core@0`/`0.1` envelope has no profile check in the `model` mode, so `prepare` gives none there. | `test_a_model_beyond_its_permission_is_refused_by_metered_with_the_model_modes_diagnostic[*-nary/order]`; `#guard` on `prepare` of a frozen envelope |
| Refuse with the same diagnostic | `InvalidModel(profile): required relation <r> exceeds permission <p>`, from the one owner | the same test asserts the `model` mode's row equals it |
| Theorem: extend `runWith_sound` / `metered_wire_sound` with a property of the decoded `M`, defined once over the decoded model; bridge lemma | `VE.Norms.Plain.ProfileHolds` (over `M.relations`), `VE.Route.MeteredRun.ProfileAdmits` (the prepared environment's tree), the bridge `Plain.profileOkOn_holds` and `profiled_admits`, the pin `prepare_profile`; the conjunct is in `EvaluationAnswer`, which both theorems conclude | `lake build`; seeded bugs S1, S2, S4 |
| Existing statements gain only this conjunct | `EvaluationAnswer` gains `ProfileAdmits p M.relations` (order: `ProfileAdmits p d.toModel.relations`) after the model decoder's equation in each family; `run_fol_sound`, `run_closure_sound`, `run_core_sound` and `run_order_sound` gain the same conjunct. No hypothesis is added and nothing else changes. | the statements below; `git diff 0f6d59d441 HEAD -- lean/VE/Route/MeteredWire.lean` |
| Part 2 (i), (ii), (iii) | tables below; `docs/kernel/kb-validators/part2-measure.json`; the tracer as run, `tracer.py.txt` | |
| Acceptance: `lake build`, `audit.py` (no new axiom), five keys' results.json byte-identical, stop on any keyed `InvalidModel(profile)` | section "Acceptance" | |
| Kernel at most +80, signed line in ALLOWANCES.md | +68: `docs/kernel/ALLOWANCES.md` row "kb-validators part 1 …; up to +80 … architect seat, round 4"; `closure-baseline.json` regenerated | `tests/test_kernel_closure.py` (36 passed) |
| Registry: `check` a pre-filter of `metered`, `route`, `quantity`; `model` of `metered` after this change; `environment` not a pre-filter (a translator) | `tools/kernel-paths.json`, `keys.validator_roles` | `tests/test_kernel_closure.py` |
| Seeded bugs (a), (b), (c) | `docs/kernel/kb-validators/seeded-bugs.json` (S1, S2, S3; plus S4) | section "Seeded bugs" |

### A design point the reviewer should check

The task names "the bridge lemma from `profileOk … = .ok ()` and the model decoder's success". The check
metered runs is the `model` mode's code, `profileOkOn` (`profileOk` is `profileOkOn` over the model's JSON
tables), applied to the decoded relations `M.relations`. So the bridge `profileOkOn_holds` reads only the
check's success, and `ProfileHolds` is stated over `M`, as the task asks. The decoder's success stays in
the conjunct just before it (`Wire.decodeDataModel rv model = .ok M`).

A bridge from the JSON check would need more. It would have to prove that the route decoder turns the
required and permission rows into tuples over the same argument sorts (a decoded tuple is `sorts.zip row`).
Equal sorts are checked by a different decoder, the regulated-predicate decoder (`DualSortMismatch`,
`Norms/Tree.lean` `actChecks`). It would also have to prove that a regulated predicate is no defined one
(`RegulatedDefinedPredicate`).

On models the decoders admit, the two checks agree, by those two refusals. A row is in the permission's
JSON rows exactly when its decoded tuple is in the decoded permission relation. So no answer can differ.
The one place they could differ is the order family. There a cell is decoded to an integer, so two
spellings of one integer, if the decoder admitted both, would be one tuple to `metered` and two to the
`model` mode. That would make `metered` the more permissive of the two, and Python asks the `model` mode
first. I did not test whether the order decoder admits a non-canonical integer spelling (Notes).

## The extended statement (verbatim, `lean/VE/Route/MeteredWire.lean`, `lean/VE/Norms/Plain.lean`)

```lean
abbrev ProfileHolds {γ : Type} (T : Tree) (relations : String → List (List γ)) : Prop :=
  ∀ pr ∈ pairs T, ∀ t ∈ relations pr.req, t ∈ relations pr.perm

theorem profileOkOn_holds {γ : Type} [DecidableEq γ] (T : Tree) (relations : String → List (List γ))
    (h : profileOkOn T (fun name => pure (relations name)) = .ok ()) : ProfileHolds T relations

def ProfileAdmits {γ : Type} (p : Prepared) (relations : String → List (List γ)) : Prop :=
  ∃ T? : Option VE.Norms.Tree, p.profile.get = .ok T? ∧
    ∀ T, T? = some T → VE.Norms.Plain.ProfileHolds T relations

theorem prepare_profile (environment : Json) :
    (prepare environment).profile.get =
      if VE.Service.Standalone.isLegacy environment then .ok none
      else VE.Service.Standalone.modelEnvironment environment >>= VE.Service.Standalone.profileTree

theorem profiled_admits {γ : Type} [DecidableEq γ] (p : Prepared) (relations : String → List (List γ))
    (h : profiled p relations = .ok ()) : ProfileAdmits p relations

def EvaluationAnswer (q : Query) (checked : VE.Service.Standalone.Validated) (p : Prepared)
    (model answer : Json) : Prop :=
  match checked.envelope.family with
  | .fol =>
    ∃ (rv : Wire.RouteVocabulary) (fs : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
      (result : Metered.Result),
      p.route.get = .ok rv ∧
      Wire.decodeFormulas rv.environment q.input (checked.envelope.profiles.contains "data@0") = .ok fs ∧
      fs ≠ [] ∧ Wire.decodeDataModel rv model = .ok M ∧ ProfileAdmits p M.relations ∧
      EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval M [])
  | .closure =>
    ∃ (rv : Wire.RouteVocabulary) (fs : List VE.Closure.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
      (result : Metered.Result),
      p.route.get = .ok rv ∧ VE.Closure.Bridge.decodeFormulas rv.environment q.input = .ok fs ∧
      fs ≠ [] ∧ Wire.decodeDataModel rv model = .ok M ∧ ProfileAdmits p M.relations ∧
      EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval M [])
  | .closureNary =>
    ∃ (v : VE.Bridge.Vocabulary) (fs : List VE.Core.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
      (result : Metered.Result),
      p.core.get = .ok v ∧ VE.Core.Bridge.decodeFormulas v.environment q.input = .ok fs ∧
      fs ≠ [] ∧ VE.Core.Wire.decodeModel v model = .ok M ∧ ProfileAdmits p M.relations ∧
      EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval M [])
  | .order =>
    ∃ (rv : Wire.RouteOrderVocabulary) (fs : List VE.Order.Formula)
      (d : VE.Order.ModelData VE.Order.Wire.Entity) (result : Metered.Result),
      p.order.get = .ok rv ∧ VE.Order.Wire.decodeFormulas rv.vocabulary.environment q.input = .ok fs ∧
      fs ≠ [] ∧ Wire.decodeOrderModel rv model = .ok d ∧ ProfileAdmits p d.toModel.relations ∧
      EncodesEvaluation q.id result answer ∧
      ∀ b, result.value = some b → b = fs.all (fun f => f.eval d.toModel [])

theorem runWith_sound (prepared : Except String Prepared) (j answer : Json)
    (h : runWith prepared j = .ok answer)
    (hk : VE.Bridge.stringField j "kind" = .ok "evaluate-budgeted") :
    ∃ (id : String) (p : Prepared) (checked : VE.Service.Standalone.Validated) (model : Json)
      (q : Query),
      VE.Bridge.stringField j "id" = .ok id ∧
      prepared = .ok p ∧
      p.checked = .ok checked ∧
      CaseModel j checked p model ∧
      query j id false = .ok q ∧ q.id = id ∧
      EvaluationAnswer q checked p model answer

theorem metered_wire_sound (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Bridge.stringField j "kind" = .ok "evaluate-budgeted") :
    ∃ (id : String) (environment : Json) (checked : VE.Service.Standalone.Validated) (model : Json)
      (q : Query),
      VE.Bridge.stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok environment ∧
      VE.Service.Standalone.evaluable environment = .ok checked ∧
      CaseModel j checked (prepare environment) model ∧
      query j id false = .ok q ∧ q.id = id ∧
      EvaluationAnswer q checked (prepare environment) model answer
```

The texts of `runWith_sound` and `metered_wire_sound` are unchanged; each gains the conjunct through
`EvaluationAnswer`. For `metered_wire_sound` the prepared environment is `prepare environment`, so
`prepare_profile` shows the tree: `Standalone.profileTree` of the case environment's model environment,
the function `modelCase` reads. The `non-vacuity` kind runs the same check (the same `run`), but it has
no theorem, as before (`uncovered` in the registry).

## Part 2: the validators under the five keys

Method: each harness was run once through `iso.sh kbv-<key> 16G` with a throwaway tracer
(`/tmp/kbv-hook/sitecustomize.py`, kept as `docs/kernel/kb-validators/tracer.py.txt`, no product change).
It recorded every Lean call of the modes `metered`, `model`, `environment` and `check`, and the branch
of every `FiniteModel.from_dict`. A second run of RSP, Preparedness (`--base-only`), FSF and eligibility
(`--no-write`) recorded the Python call site of every `check` answer carrying `Q` or `core`. Commands
and every figure: `part2-measure.json`.

### (i) `metered` cases with a regulated environment, and whether the `model` mode was asked first

| Key | `metered` cases (all `evaluate-budgeted`) | with a regulated environment | with a declared pair | the `model` mode had accepted the model first | not asked first | soft-path models (Lean not asked; `ve/model.py:54-68`) | of them with a regulated predicate | `metered` refusals |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Anthropic RSP | 4,852 | 0 | 0 | - | 0 | 2,986 | 0 | 0 |
| OpenAI Preparedness | 16,230 | 0 | 0 | - | 0 | 16,969 | 0 | 0 |
| DeepMind FSF | 8,233 | 0 | 0 | - | 0 | 112 | 0 | 0 |
| agent-policy | 11,829 | 480 | 480 | 480 | 0 | 0 | 0 | 0 |
| eligibility | 0 | 0 | 0 | - | 0 | 0 | 0 | 0 |

The three framework keys declare no `regulated` predicate in any environment they build: their norms are
soft-norms documents. So the soft path never carries a pair under the keys. A model "asked first" is one
whose content (domains, constants and relations, rows sorted) the `model` mode was sent earlier in the
same run. On a soft environment with a pair, outside the keys, Python's own decoder refuses a profile
violation (`test_the_soft_path_refuses_the_same_model_in_python_before_metered`). The `model` mode
refused 11 agent-policy models, all `InvalidModel(flags)` (no pair involved); none of them reached
`metered`.

### (ii) Regulated predicates whose authored act text differs from the `acts` the `environment` mode returned

| Key | environments built (distinct) | with regulated predicates | regulated predicates | with `acts@0` | authored act differs from returned `acts` |
|---|---:|---:|---:|---:|---:|
| Anthropic RSP | 20 | 0 | 0 | 0 | 0 |
| OpenAI Preparedness | 19 | 0 | 0 | 0 | 0 |
| DeepMind FSF | 14 | 0 | 0 | 0 | 0 |
| agent-policy | 214 | 128 | 256 | 0 | 0 |
| eligibility | 2 | 0 | 0 | 0 | 0 |

Count 0, so there is no first-20 list. Every one of agent-policy's 256 returned acts equals its authored
text (for example `permitted`: `{0} be performed`; `report_required`: `{0} be reported to the user`). No
key uses `acts@0`, the only profile under which the canonical act can differ from the authored one.

### (iii) Values in a key's results.json or answer that came from a `check`, `model` or `environment` answer

How these were found: a leaf match of every string of length 6 or more in those answers against every
results.json leaf and the harness's stdout, and a call-site trace of every `check` answer carrying `Q`
or `core`. The code each site reaches was then read.

| Key | results.json field (or answer) | Mode, answer field | How it gets there | Count |
|---|---|---|---|---:|
| eligibility | `english.rows[*].sentence`, `english.rows[*].round_trip`, and `english.facts` / `english.round_trip` | `check`, `Q` | `english_facts` (run.py:580-583): `render_quantity_sentence(env, Q)`, and `parse_w6_sentence` of the rendered text compared with `Q`; shown, no kernel row | 80 rows (418 `Q` answers) |
| eligibility | `probes.P3.facts[*].rendered`, `.round_trip` | `check`, `Q` | `probes` (run.py:538-541): `parse_w6_sentence` (which reads `Q`, `surface/time.py:237`) and `render_quantity_sentence` | 3 facts |
| eligibility | `probes.P1.python`, `probes.P2.python` | `check` answer, or its refusal text | `probes`' `python()` (run.py:514): `admitted`, or `rejected: <the check-mode diagnostic>` | 2 |
| eligibility | `profiles[*].single_shot` (`Q1`, `searches.*.status`, `.steps`, `.certified`) and `summary.single_shot` | `check`, `core` | `single_shot` (run.py:93): the cores of `_core_problem` go to Python's `prove_entailment`. `certified` and `Q1` come from that search alone, with no Lean replay. Today `Q1` is `OPEN` on all 80 profiles (no certificate found). | 80 profiles (20,571 `core` answers) |
| eligibility | `profiles[*].steps[*].certified`, `profiles[*].staged`, `profiles[*].answers` | `check`, `core` | `Prover.prove` (run.py:81): `prove_quantity` searches over the cores. Each kept step's certificate is replayed by Lean's `quantity` mode, which re-elaborates the W6 statements and binds their meaning ids (`profiles[*].lean.certificates_accepted`). An answer counts only if Lean admits its document. | 3,458 `core` answers |
| eligibility | `environment_id` | `environment` and `check`, `environment_id` | Python's own digest `env.environment_id`, which each row must equal (`validation.py:105`, `units.py:322`); the value is Python's, bound to Lean's | 1 |
| Anthropic RSP | the answers of `stage0._proved` and `run.factor_within_five` | `check`, `core` | `prove_quantity`'s search over the cores. The answer is true only after `check_quantity_certificate` (Lean's `quantity` mode re-elaborates and binds the meaning ids). A wrong core can only make the search fail (`UNKNOWN`/`None`), never give a wrong verdict. | 141 + 4 `core` answers |
| OpenAI Preparedness | the answers of `run.certified` (run.py:902) | `check`, `core` | the same: search, then Lean replay | 29 (`--base-only`; 45 with mutants) |
| DeepMind FSF | `severity_and_dates.d3` items (`verdict` `ALL`/`UNKNOWN`) | `check`, `core` | the same: search, then Lean replay | 20 |
| agent-policy | none | `check` answers carry only `meaning_id` (typing), which `ve/ast.py` does not read | - | 0 |
| every key | none | `model`, `model_id` | stored as `FiniteModel.model_id` (`validated_model`); no keyed results.json or stdout holds one (leaf match: 0) | 0 |
| every key | none | `environment`, `acts` | stored in place of the authored act (`validation.py:85-105`); equal to it in all 256 keyed cases (table (ii)) | 0 differing |
| every key | none | `check`, `meaning_id` | quantity certificates carry them; Lean's `quantity` mode recomputes and binds them; no results.json holds one (leaf match: 0) | 0 |

`Q` and `meaning_id` from a `check` answer (finding (c), `ve/units.py:317-325`) reach keyed output only in
eligibility: the 80 English rows, the P1 to P3 probes, and `single_shot`. The framework keys use the
cores only as input to an untrusted search that Lean replays.

## Acceptance

| Item | Result | Tag |
|---|---|---|
| `cd lean && lake build` | passes (1,438 jobs) on the final Lean (`844655983c`; later commits change no Lean) | AGENT |
| `python3 lean/audit.py` | PASS: 873 source files, 9,968 named theorems, only the declared standard axioms. The new theorems read `propext`, `Quot.sound` (and `Classical.choice` through `runWith_sound`, as before). | AGENT |
| No keyed call refused with `InvalidModel(profile)` | 0 refusals of any kind from `metered` across the five keys (table (i)): no STOP | AGENT |
| RSP, Preparedness, FSF results.json byte-identical | `--check` exits 0 on each, on the traced binary `cf72c2e5…` and again on the final binary `a6cf2276…` without the tracer | AGENT |
| agent-policy results.json | `check.py base --write` writes a file that differs from the committed one only in `M10.seconds` and `M10.policy_seconds` (timing), on both binaries; restored with `git checkout` | AGENT |
| eligibility results.json | `run.py --no-mutants` on this branch and on main (merge base, a temporary worktree, the same flags) differ only in `seconds`. Both differ from the committed file (2026-09-29) in the `--no-mutants` sections and in 81 wording strings that main changed on 2026-10-05 (`git log -S"is not written in canonical form"`): the committed file is stale on main, not changed here. | AGENT |
| Kernel at most +80 | +68 (table below) | AGENT |
| Architect seat's ruling on part 2 (ii) and (iii) | deferred to the architect seat (HANDOFF section 5) | HUMAN |

## Kernel figures (`python3 tools/kernel_closure.py`, `docs/kernel/closure-baseline.json`)

| Figure | Before (main `0f6d59d441`) | After | Change |
|---|---:|---:|---:|
| kernel, distinct lines | 9,552 | 9,620 | +68 |
| lines under the frozen keys' answers (`keyed_lines`) | 16,198 | 16,225 | +27 |
| of them in the kernel | 9,552 | 9,620 | +68 |
| `metered` spec / wrap / lines | 3,245 / 2,080 / 3,251 | 3,352 / 2,154 / 3,358 | +107 / +74 / +107 |
| `readingsRoute` (candidate) wrap / lines | 20,513 / 24,205 | 20,516 / 24,208 | +3 (it reaches `modelCase`, now via `profileTree`) |
| `discourse` (candidate) spec / lines | 36,141 / 36,147 | 36,151 / 36,157 | +10 (`profileOk` through `profileOkOn`) |
| `document` (candidate) spec / wrap / lines | 34,821 / 12,818 / 35,649 | 34,831 / 12,826 / 35,657 | +10 / +8 / +8 |

The `metered` spec now reads `ProfileAdmits`, `ProfileHolds`, `pairs` and `Tree`; its wrap gained `profiled`,
`profileTree` and `modelEnvironment`'s views. The signed total in `ALLOWANCES.md` is 9,620, and the
specification's table and figures and the frozen-keys figures quote the regenerated baseline
(`tests/test_kernel_closure.py::test_the_records_quote_the_saved_measurement`).

## Seeded bugs (`docs/kernel/kb-validators/seeded-bugs.json`; each restored)

| # | Language, file | Bug | Caught by |
|---|---|---|---|
| S1 (task a) | Lean, `lean/VE/Route/MeteredRun.lean` | the fol branch of `run` skips `profiled` | `lake build VE.Route.MeteredWire`: `run_fol_sound` does not build, so the extended theorem fails |
| S2 (task b) | Lean, `lean/VE/Norms/Plain.lean` | `profileOkOn` compares the permission relation with itself | `lake build VE.Norms.Plain`: `profileOkOn_holds` does not build |
| S3 (task c) | Lean, `lean/VE/Route/MeteredRun.lean` | every `profiled` call removed: main's runner, rebuilt and pinned | `tests/test_metered_profile.py`: 26 failed (the 24 refusal cases, the handle case, the Python reader case). The refused case was answered `{"evaluation": {"evaluations": 3, "explanation": null, "status": "Violated", "value": false}, "id": "e", "status": "ok"}`, which is what main answers |
| S4 | Lean, `lean/VE/Route/MeteredRun.lean` | `prepare` gives no profile on any environment | `lake build VE.Route.MeteredWire`: `prepare_profile` does not build (without it `ProfileAdmits` would hold vacuously) |

No Python or Rust product code changed, so every seed is Lean. Trust mutants (the mechanical sweep, R16):
`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/kernel/kb-validators/trust-mutants.json --test lean/VE/Route/MeteredProfileExamples.lean --allow docs/kernel/kb-validators/trust-mutants-allow.json`.
A full run on `844655983c` was followed by a rescore after an allow-only edit (`fb4b9c5d6b`), and another after the declarations were classified (`babec72be2`, Lean unchanged; classes S 39, G[V] 27, D[V] 6 mutants): **20 KILLED,
0 SURVIVOR, 0 UNKNOWN, 6 INVALID, 46 ALLOWED, exit 0**. What is allowed:
- `EvaluationAnswer` (30 mutants), `ProfileAdmits` (5) and `ProfileHolds` (2): Props. A body mutant of
  `ProfileHolds` changes the instance that decides it, so the tool reads the failing `#guard`s as UNKNOWN.
  The proofs they break are named in each reason.
- 9 mutants that do not elaborate: `≤` on `Except`, and a list operator applied to the namespace
  `VE.Bridge` or to a bare `[]`.

The `#guard`s kill every mutant of `profileOkOn`, `profileTree`, `profiled` and `profileOk` that builds.

## Notes for the DRI

- DELTA row 1 cites R7. At every public entry (`FiniteModel.from_dict` on the validated path, Python's own
  decoder on the soft path) the model is refused before `metered`, on main and here, with the same output.
  Only a direct service request, which no public entry sends, now sees `InvalidModel(profile)` where main
  answered. The two public-path tests show both sides.
- The statements of `runWith_sound` and `metered_wire_sound` changed as the task instructs: one conjunct
  through `EvaluationAnswer`, no hypothesis. The task's architect-seat decision D13 is the authority I
  worked under.

## Notes

- `ProfileHolds` is an `abbrev`, so the standard list instances decide it in the examples. That is the
  only reason; nothing else reads it differently.
- Not tested: whether the order decoder admits two spellings of one integer cell (see the design point).
  If it does, `metered` would be more permissive than the `model` mode on that family, never less, and
  Python asks the `model` mode first.
- Seen in part 2 (iii), for the architect seat: eligibility's `single_shot` writes `certified` and `Q1`
  from Python's `prove_entailment` over check-mode cores, with no Lean replay. It answers `OPEN` on every
  profile today, so no shown answer is wrong now.
- `Plain.forM_ok` was not added: the bridge reuses `VE.Norms.Admission.forM_ok` (one owner), so
  `Norms/Plain.lean` imports `VE.Norms.Admission` (no cycle).
- Regeneration also wrote `docs/codemap/docs__kernel.md`, for kb-10b's `repair_shadow_choices.py`, which
  main's map had not listed yet.

## What was not run

The full release gate (the chain's, on the final HEAD). Eligibility's mutants section (`--no-mutants`;
the branch makes no `metered` or `model` call there, and main and branch match on everything else).
Preparedness' traced call-site run used `--base-only`; its acceptance runs used `--check` (with mutants).

## Selected tests

`MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base 0f6d59d441 --run` on the committed `af20f59485`
(the run fell back to the VM; 10,640 s): every unit passed except two files, both mine:
- `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`: the new example file
  builds JSON and was in no list. It is now under `lean_decoders.other_json` in `ve/assurance-manifest.json`,
  with its reason.
- `tests/test_consolidation_tools.py::test_committed_trust_table_covers_every_declaration` (35 unclassified
  lines) and `::test_committed_ledger_names_real_declarations`. The five new trusted declarations are now
  classified in `tools/trust-classes.json`: `ProfileHolds` and `ProfileAdmits` S; `profileOkOn` and `profiled`
  G[V]; `profileTree` D[V], as `regulatedOf`. That moved the growth between classes (S +16, V +21; the total
  is still +37), and the two allowances say so. The consolidation plan's step 5 row is re-measured: tied
  415 to 413, because `modelCase` and `profileOk` are shorter.

The three failed ids rerun on the fixed commit (`mac-pytest.sh -- <ids>`, `babec72b`): 3 passed. The
trust mutants were rescored after the reclassification (Lean unchanged).

## Spec re-read

- "apply the SAME check the `model` mode applies (… on the same tree, built the same way as Standalone.lean:612-615; share the code)" against the task: the tree comes from `profileTree`, which `modelCase` calls in place of those lines, and the check is `profileOkOn`, which `profileOk` runs.
- "define it once, e.g. `VE.Norms.Plain.ProfileHolds`, over the decoded model, not over JSON" against the task: `ProfileHolds T M.relations`.
- "Existing statements may gain this conjunct; nothing else in them changes" against the task: the diff of `MeteredWire.lean` adds `ProfileAdmits … ∧` in five statements and nothing else in them.
- "record `check` as a pre-filter of `metered`, `route` and `quantity`; `model` as a pre-filter of `metered` AFTER this change; `environment` as NOT a pre-filter" against the task: `keys.validator_roles` in `tools/kernel-paths.json`.
- DELTA row 2 against R16 (DRI-RULINGS.md:62): per-file figures from `trust_map.py`, a failing check per new definition (the trust mutants), and a FOLLOW-UPS ties row.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer is typed and contained: N.A. No answer shape or schema changed. A refusal is the existing error row, and the Python reader turns it into `CheckerUnavailable` (`test_a_profile_refusal_reaches_python_as_checker_unavailable_never_as_an_answer`).
2. Every deliverable is built: PASS. See the Deliverables table, with a commit and test per line.
3. Tests and gates can fail: PASS. Seeded bugs S1 to S4, and trust mutants exit 0 (`trust-mutants.json`).
4. Python, Lean and Rust agree, and valid inputs still pass: PASS. Main and head match on the five keys (Acceptance). `test_a_model_within_its_permission_is_still_answered` covers equal relations in another order and empty ones.
5. R8 binding: N.A. No field Python reads from a Lean answer is added.
6. Gate evidence matches the final HEAD: PASS for what is mine. The trust mutants ran on the final Lean, the keys reran on the final binary, and the commits after them change no Lean. The gate itself is the chain's.
7. No unsigned item: PASS. DELTA rows cite R7, R16 and R12, and the kernel growth is signed in ALLOWANCES.md (architect seat, round 4).
8. Every user-visible change is in DELTA: PASS. Row 1, and the keys' outputs are unchanged (Acceptance).
9. Test selection finds the tests: PASS. `tools/select_tests.py --base 0f6d59d441` lists `tests/test_metered_profile.py` and `tests/test_kernel_closure.py`, and the selected run's two failures were in tests the change affects (section "Selected tests").
10. Lean statements say what is claimed: PASS. S1, S2 and S4 break the build. The theorem is about the decoded `M` the answer is computed in (the same `M` that `answer` evaluates).
11. Budgets and deadlines fail closed: N.A. No budget or limit changed; the check runs after the model decoder's limits.
12. No CPU or memory regression: PASS. The check is one walk over the declared pairs' tuples, and the tree is decoded once per prepared environment (a `Thunk`, kept with a handle). The key wall times are in `part2-measure.json`, measured under VM load, so they are no benchmark.
13. Test-removed trailers: N.A. No test removed or renamed.
14. Both directions and spec re-read: PASS. Refused beyond and answered within, on every family and kind, and with and without a pair (`tests/test_metered_profile.py`). Spec re-read above.
15. No overclaim, no silent cut, every new check can fail, limits charged first: PASS. "Every family" is the parametrised tests, and "no keyed refusal" is table (i). Nothing is cut. Each new guard has its mutant (the trust mutants). No new list is decoded before a limit: the relations are counted by the model decoder first.
