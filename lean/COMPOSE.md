# Feature composition in Lean (`lean/VE/Compose/*`, stage S0)

Specification: [docs/spec/composition.md](../docs/spec/composition.md) section 9 (the exact theorem statements)
and section 10 (the fixtures), from [docs/spec/composition-PLAN.md](../docs/spec/composition-PLAN.md) stage S0.
This file lists every definition the statement review reads and every theorem in plain words. All statements
quantify universally over their displayed parameters. `lean/audit.py` audits every theorem: no `sorry`, only
`propext`, `Classical.choice` and `Quot.sound`. No `lean/VE/Norms/*`, `lean/VE/SoftNorms/*`, `lean/VE/Rights/*`,
`lean/VE/Route/*`, `lean/VE/Discourse/*` or P0 source changed: `python3 VE/Route/frozen.py` passes, with the four
new modules added to its inventory (`VE/Route/frozen-sources.sha256`) and `VE/Audit.lean` rehashed there.
`VE.lean` and `VE/Audit.lean` gained imports and audit entries only; `lakefile.toml` is unchanged (no new
target). S0 changes no behaviour: no executable calls anything here.

## Files

| File | Contents |
|---|---|
| `Slot.lean` | The base-premise slot: `SlotWellFormed`, `slotCheck`, `BaseAdmissibleP`, `backgroundBaseP`, `backgroundP`, `ConflictFreeP`; `gate`; `Labelled`; `slotConflictFreeCheck`, `backgroundValidP`; `PrefixAdmissibleP`, the layer chain (`slotSymLayer`, `SlotChain`, `slotChain`, `slotRouteChain`) and `slotRoute`; the route theorems relative to a slot; the rights route as the instance `P := Lim_D` |
| `Dispatch.lean` | `unsupported`, `registered`, `speechAllow`, `wrapperProfiles`, `Route`; today's gate `todayGate`, `todayHead`, `today` and the declarative `TodayList`; the stack: `base`, `sitsOn`, `wrapperHead`, `outside`, `refusal`, `dispatch`, `ChainList`, `stackHead` |
| `Content.lean` | `Content` (five constructors), `Content.kind`, `Content.needs`, `lineRuleNames`, `Content.declared` |
| `Examples.lean` | Build-time `#guard` checks of fixtures D1 to D52 (with the removals of D28 to D31, D50 and D51; the rows are spec 10.1's one table, which `tests/test_compose_dispatch.py` reads and requires these guards to repeat), D-all, D-unsorted's seeded lists, L1 to L8 and C1 to C6, and the two `rfl` equations of L9 |

## How the proofs are organised

* The slot theorems are the rights route's proofs (`lean/VE/Rights/Route.lean`) with `Lim_D` replaced by an
  arbitrary list `P`. `Lim_D` was used there only as satisfied formulas and, where a premise moves between a
  structure and its base restriction, through `RightsValid.limTyped`; here that is `SlotWellFormed X P`. So
  `slot_conflict_free`, `slotRoute` and `slot_route_intended` take no typing hypothesis, and the background
  soundness and completeness, the second half of acceptance, the countermodel and exactness take `hP`.
* Every rights instance holds by unfolding: `BaseAdmissibleR D B` is by definition
  `BaseAdmissible′ (correlate D) B ∧ Sat B (limPremises D)` and `backgroundR D` is
  `background′ (correlate D) ++ limPremises D`. `rights_acceptance_from_slot` and `rights_countermodel_from_slot`
  carry the statements of `rights_route_acceptance` and `rights_route_countermodel` and are proved from the slot
  theorems alone; fixture L9 checks with `rfl` that their types agree definitionally with the originals'.
* `todayGate` is a transcription of `ve/profiles.py` `checker_family` as merged with `norm-defaults@0` (sixteen
  names, eighteen checks; `normDefaults` is the ninth route, spec draft 3). It is checked against the declarative
  `TodayList` in both directions (`todayGate_sound`, `todayGate_complete`), against the frozen classifier on the
  frozen registry (`today_classify`), and against Python on all 65,536 sorted lists of registered profiles,
  texts included (fixture D-all in `Examples.lean`, whose literals `tests/test_compose_dispatch.py` recomputes
  from Python).
* The `dispatch` theorems go through one characterisation, `dispatch_ok_iff`: `dispatch` succeeds exactly on a
  sorted list whose base has a route that every present wrapper sits on, and then it answers `stackHead`.

## Theorems

### `Slot.lean` (spec 9.2)

| Theorem | In plain words |
|---|---|
| `slotCheck_sound` | A slot the executable check accepts is closed and well-formed over the base vocabulary. |
| `sat_nil`, `sat_append` | Every structure satisfies the empty list; a structure satisfies `P ++ Q` exactly when it satisfies both. |
| `slot_empty` | Relative to the empty slot, base admissibility is the soft route's. |
| `slot_empty_conflictFree` | Conflict-freedom relative to the empty slot is soft's conflict-freedom. |
| `slot_empty_background` | The empty slot adds nothing to the background or the base background. |
| `baseAdmissibleP_append` | Admissible relative to `P ++ Q` is admissible relative to `P` and satisfying `Q`. |
| `slotWellFormed_append` | `P ++ Q` is a slot exactly when `P` and `Q` are. |
| `conflictFreeP_append` | A longer slot admits fewer bases, so conflict-freedom relative to `P` holds relative to `P ++ Q`. The converse is not claimed. |
| `gate_wellFormed` | Gating a slot by a closed base formula gives a slot. |
| `sat_gate_on` | Where the gate holds, satisfying the gated slot is satisfying the slot. |
| `sat_gate_off` | Where the gate fails, the gated slot is satisfied whatever the slot says. |
| `slot_coherent_expands_all` | Over the bases admissible relative to `P`, every base has exactly one expansion to the complete vocabulary exactly when the document is conflict-free relative to `P`. |
| `slot_empty_check` | The certified conflict check relative to the empty slot is soft's check. |
| `slotConflictFreeCheck_target` | An accepted check has an accepted certificate for every conflict target. |
| `sat_backgroundBaseP` | A base admissible relative to `P` satisfies the base background extended by `P`. |
| `slot_conflict_free` | One accepted certificate per W1 conflict target, from the base background extended by `P`, proves conflict-freedom relative to `P`. |
| `baseAdmissibleP_of_valid` | A valid finite base model that passes `backgroundValidP` is admissible relative to `P`. |
| `slot_conflict_witness_sound` | Such a model satisfying a conflict target refutes conflict-freedom, relative to `P` too, and the conflict is classified as soft classifies it. |
| `slot_restrict_admissible`, `slot_layer_expands` | One layer of the route relative to `P`: forgetting the layer symbol keeps admissibility, and conflict-freedom at the layer gives a unique expansion. |
| `prefixAdmissibleP_zero` | The admissibility of the empty prefix is base admissibility relative to `P`. |
| `slotChain_hc` | Conflict-freedom relative to `P` gives every layer's hypothesis. |
| `slotRouteChain_premises`, `slotRouteChain_restrict` | The composed route's premises are the layer premises of `soften X`, and its restriction is the restriction to the base vocabulary. |
| `sat_slot_restrict` | A slot holds in a structure exactly when it holds in its base restriction. |
| `slot_route_backgroundSound`, `slot_route_backgroundComplete` | The route relative to `P` is sound and complete for the background extended by `P`. |
| `slot_route_intended` | A certificate accepted from the background extended by `P`, the layer premises and `Γ` proves its conclusion in every structure with the intended soft meaning that satisfies the background, the soft premises, `P` and `Γ`; no conflict-freedom needed. |
| `slot_route_acceptance` | That, and when the document is conflict-free relative to `P` and `Γ`, `φ` are base formulas, the conclusion holds in every base admissible relative to `P` that satisfies `Γ`. |
| `slot_route_countermodel` | Under the same hypotheses a base admissible relative to `P` that satisfies `Γ` and refutes `φ` expands to a full structure satisfying the soft premises, `P` and `Γ` and refuting `φ`. |
| `slot_route_entails_iff` | Entailment from the checked premises is truth in every base admissible relative to `P`. |
| `rights_is_slot`, `rights_conflictFree_is_slot`, `rights_background_is_slot`, `rights_check_is_slot`, `rights_valid_is_slot` | The rights route's admissibility, conflict-freedom, backgrounds, certified check and finite-model check are the slot's at `P := Lim_D` over `correlate D`, by definition. |
| `rights_slot_wellFormed` | `Lim_D` of a well-formed rights document is a slot. |
| `rights_acceptance_from_slot`, `rights_countermodel_from_slot` | The rights route's acceptance and countermodel theorems, statements unchanged, proved from the slot theorems alone. |

### `Dispatch.lean` (spec 9.3)

| Theorem | In plain words |
|---|---|
| `contains_eq` | List containment of a string is its membership, decided. |
| `ite_error_ok`, `ite_ok_of` | An `if` whose true branch is an error answers `ok` exactly through its false branch. |
| `todayGate_sound`, `todayGate_complete` | Today's gate accepts exactly the lists of `TodayList`. |
| `today_ok`, `today_error` | `today` answers `ok` with `todayHead` exactly when the gate accepts, and passes the gate's error through. |
| `today_sound` | A list `today` routes is a `TodayList`, and its route is `todayHead`. |
| `today_complete` | Every `TodayList` is routed to `todayHead`. |
| `todayHead_cases` | `todayHead` is the first of risk, alternatives, speech acts, reports, rights, soft, norm defaults, norms present, else frozen. |
| `todayHead_not_wrapper` | `todayHead` never answers a wrapper's head. |
| `known_registered` | Every profile of the frozen gate's registry is registered. |
| `todayGate_classify` | On the frozen gate's registry, today's gate is the frozen classifier with its family forgotten. |
| `today_classify` | There, both accept the same lists and reject the others with the same text. |
| `today_frozen`, `today_norms`, `today_normDefaults`, `today_soft`, `today_rights`, `today_alternatives`, `today_risk`, `today_reports` | What each of today's heads may rely on: the memberships its own Lean gate requires. |
| `forIn_yield_ok` | A loop whose every step yields succeeds. |
| `today_speech` | A list routed to speech acts passes the speech-act route's own profile gate. |
| `mem_base`, `base_mem`, `mem_wrappers`, `base_of_no_wrapper` | Membership in the base list and in the present wrappers; a list without wrappers is its own base. |
| `dispatch_ok_iff` | `dispatch` succeeds exactly on a sorted list whose base has a route every present wrapper sits on, and answers the stack's head. |
| `dispatch_today` | On a list without wrapper profiles `dispatch` is `today`: today's lists keep today's route, today's rejections keep today's diagnostic. |
| `dispatch_chain` | On a chain list `dispatch` answers the stack's head. |
| `dispatch_descends` | When `dispatch` answers a wrapper's head on a list, then after that wrapper strips its own profile, `dispatch` accepts the rest with its stack head. |
| `dispatch_unsorted` | Every list that is not strictly increasing gets the order error, whatever it contains. |
| `dispatch_discourse_frozen` | On today's discourse lists the wrapper is the head and what it sits on is today's frozen route. |
| `dispatch_error` | Every error of `dispatch` is the order error, today's error on the base list, or a wrapper's named refusal. |
| `refusal_names` | A refusal names two profiles of the list (`with`), or one of the list and one it lacks (`requires`). |

### `Content.lean` (spec 9.4)

| Theorem | In plain words |
|---|---|
| `needs_chain` | A content needs `norms@0`, `rights@0` or nothing. |
| `assertion_declares_nothing` | A formula declares no name. |

## Not built here

The lifting lemma of spec 9.5 (`adjoinOne` and its five statements) is stated in the specification for S2a and
is not built in S0 (resolved choice 11 recommends building it with S0; that recommendation was not applied).
Nothing about `sup`, any reading set, separation, `plain` or resolution (spec 9.6).
