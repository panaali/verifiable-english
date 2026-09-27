# Causation as preventable harm over explicit alternatives: plan (`alternatives@0`)

> Status: planning draft 1 (2026-09-27), planner Fable 5.1, no model calls; input to the Astra + Fable converge
> debate for North Star rank 4 (`~/code/ve-northstar/NORTH-STAR.md`: "Causation / preventable harm", 0–13,000 B
> upper bound, semantics absent). Inputs: the Asimov use case (`~/code/ve-asimov/usecases/asimov-laws/`, Astra
> review `manage-agents/asimov-review-astra.final.md`); [norms.md](norms.md) (W1); [soft-norms-PLAN.md](soft-norms-PLAN.md);
> [document.md](document.md) (W2); the pinned pilots (`manage-agents/pilots/{claude-constitution,udhr}/`, cited by
> source line as `C:n` and `U:n`); [VISION.md](../../VISION.md); `design/vex-mandatory-evidence.md`. Nothing here
> changes a frozen contract, a `norms@0` identity or a checker function. Theorem statements are obligations, not
> proofs; no coverage number is predicted.

## 0. Problem and stance

The Asimov README leaves the inaction clauses UNFORMALISED: "through inaction, allow ... to come to harm" needs "a
causal account of what the robot could have prevented. W1 has no such account." The same gap blocks C:187 (refer to
emergency services when life is at risk), C:221 (actions that could cause severe harm), the harm-weighing factors
C:334–341 and U:73 ("protection of the law against such interference"). Causation is the primary blocker on 81 C
units and 2 U units, almost all co-blocked by quantities, modality or attribution.

Stance. "Allow through inaction" is a claim about **what else the agent could have done**. The checker cannot
certify causal facts (converged rule 8), but it can certify structure over a **declared** causal model: a finite
list of alternatives per chooser and a table saying which alternative leads to which harm. The construct is
therefore small: explicit alternatives, the outcome table, three defined words (*avoidable*, *allows*, *prevents*)
and one new check (can the rules be followed at every choice?). Every verdict reads "in the declared model"; the
table's correctness, counterfactual truth, degrees, proximate causation and the completeness of the alternative
list stay open and are listed in the residual. No new logic: everything elaborates into `norms@0` over base
predicates, definitions are inlined into guards, and the checks reuse W1's substitution, tableau and witnesses.

## 1. Semantics

### 1.1 Declarations (environment block, identity-bound like `regulated`)

```json
"alternatives": {
  "chooser": "robot", "action": "action", "harm": "harm",
  "available": "available",              // available(robot, action): a is one of r's alternatives
  "leads_to":  "leads_to",               // leads_to(action, harm): the declared outcome table
  "performed": {"permission": "permitted", "obligation": "required"},   // optional: the W1 pair meaning "take a"
  "inaction":  "inaction",               // optional: inaction(action)
  "taken":     "taken",                  // optional: taken(action), the construct's `done`
  "proximate": "causes"                  // optional: causes(action, harm), an open predicate with a decider
}
```

A *chooser* is one agent at one decision point; a second decision by the same agent is a second chooser, unlinked
(1.5). Sorts, names and verbalisations are the author's; the block assigns roles. Regulated predicates and rules
are W1's, unchanged: Asimov keeps `permitted(action)` and `required(action)`. An obligation predicate whose first
argument is the chooser sort may declare `"fulfilment": "<definition>"`, a base definition over `(action,
remaining arguments)` naming which alternative discharges it; the profile supplies `avoids(a, h) := ¬leads_to(a,
h)` for duties of prevention (`FulfilmentNotBase` if a fulfilment mentions a regulated symbol).

Background slot `alternatives` (a generator in the P0 hook table, as W1 added `profile`), universal premises over
base predicates in `Background_base`: at most one taken alternative per chooser (`available(r,a) ∧ available(r,a')
∧ taken(a) ∧ taken(a') → a = a'`); at most one inaction per chooser; `causes(a,h) → leads_to(a,h)` when
`proximate` is declared. Existence facts (a chooser has an inaction; an action belongs to a chooser) are validated
on supplied finite models (`InvalidModel("alternatives", ...)`) and never assumed by a certificate, so the
premises stay universal (norms.md 7.1(3)).

### 1.2 Definitions (bodies fixed by the profile, inlined into guards)

```text
avoidable(r, h)    := ∃a. available(r, a) ∧ ¬leads_to(a, h)                       some alternative of r avoids h
unavoidable(r, h)  := (∃a. available(r, a)) ∧ ¬avoidable(r, h)                    r has alternatives and all lead to h
allows(a, h)       := leads_to(a, h) ∧ ∃r. available(r, a) ∧ avoidable(r, h)      a leads to h; another alternative would not
prevents(a, h)     := ¬leads_to(a, h) ∧ ∃r. available(r, a) ∧ ∃a'. available(r, a') ∧ leads_to(a', h)
discharged_o(r, x̄) := ∃a. available(r, a) ∧ taken(a) ∧ F_o(a, x̄)                  o an obligation on (chooser, x̄) with fulfilment F_o
violation_o(r, x̄)  := O_o(r, x̄) ∧ (∃a. available(r, a) ∧ taken(a)) ∧ ¬discharged_o(r, x̄)
```

`allows` covers both enabling by an act and failing to prevent by inaction; the `inaction` marker tells them
apart, and *causing* (proximate) is the separate open predicate `causes`, never derived. The elaborator inlines
the bodies into guards, which W1 admits (quantified guards, norms.md 9.2), so the document that reaches the route
is plain `norms@0` over `E_base` plus the slot's premises; no W1×W3×W5 composition is needed (INTEGRATION-GAPS).
Theorem `inline_faithful` (section 6) says inlining equals W3 layering, so when that gap closes the bodies may
become definition layers with no change of meaning. `discharged` and `violation` are evaluated on scenarios, like
W1's `violation := required ∧ ¬done`, and are not route premises.

Two W1 encodings of a duty of prevention, differing only in dilemmas:

```text
(A) per action   Rule 7. Every action must not be performed, if that action is inaction and that action allows a
                 harm to a human being to happen.                       (guard: ∃h. to_human(h) ∧ allows(a, h))
(B) per harm     regulated prevent_required(robot, harm), obligation, deny-by-default, act "{0} prevent {1}",
                 fulfilment avoids.  Rule 8. Every robot must prevent each harm to a human being, if that harm is
                 avoidable by that robot.
```

In translation the inaction clause is a reading set `{A, B}`; "injure" versus "come to harm" is a second set
`{causes, allows}`, and the existing direct-injury rules (`injures_human`, annotator-decided) are `causes`
restricted to humans.

### 1.3 The followability check (the one new check)

For a CONFLICT-FREE document, with `O_p°` the base-substituted outcomes of norms.md 4.5 and `(m, q)` the declared
`performed` pair:

```text
clear(r, a)   := available(r, a) ∧ O_m°(a)                                       taking a is permitted
               ∧ ∀a'. (available(r, a') ∧ O_q°(a') → a' = a)                     and forgoes nothing that is required
               ∧ ⋀_{o with F_o} ∀x̄. (O_o°(r, x̄) → F_o(a, x̄))                    and discharges every obligation on r
followable(r) := (∃a. available(r, a)) → ∃a. clear(r, a)
```

Absent parts of the block drop their conjunct; an obligation with no declared fulfilment does not constrain the
choice, and the report says so. Document status, three-valued and bound to `environment_id` and the document hash
exactly as conflict packages are (norms.md 5.2, 11.4): **FOLLOWABLE**, a tableau certificate for `Background_base
⊢ ∀r. followable(r)`; **DILEMMA**, a valid finite base model and a typed chooser at which `¬followable°` evaluates
true, classified NONE-PERMITTED, OVER-REQUIRED or UNDISCHARGEABLE(o, x̄) and rendered as a situation (fixture b);
**UNKNOWN** with the budget named. Enumeration never yields FOLLOWABLE. A DILEMMA is not a verdict that the rules
are wrong; it is a situation in which no available action complies with all of them, which is what "ought implies
can" asks an author to face. On a CONFLICT document the status is not computed. On a scenario (finite model) the
checker also lists, per chooser, permissions, requirements, avoidability, who allows or prevents what, `clear`, and
violations when `taken` is supplied; Rust evaluates the substituted formula untrusted (norms.md 11.6).

### 1.4 Stratification: priority across obligations is written over facts

An exception guarded by "if no other action available to that robot is permitted" mentions `permitted` on its own
predicate and is `DependencyCycle: permitted` (norms.md 4.1(4)). The author states the facts that forbid the
other alternatives instead ("if every other action available to that robot allows a harm to a human being to
happen"); the IDE offers this rewrite under the hint `GuardOnOwnOutcome`. So priority across different
obligations for different actions is never a checker primitive: it is a W1 exception over facts, a soft-norm rank
on the colliding rules (which resolves per action only, soft-norms-PLAN 1.6), or an open decider in the residual;
the followability check certifies whatever was written, or shows the situation it fails.

### 1.5 Time and traces (stage 2, stated so that stage 1 is its one-step case)

Stage 1 has no time predicate: `leads_to` means "occurs afterwards" and each chooser decides once. Stage 2: a
trace is choice points `c_0 … c_H` with a declared horizon `H`, a deterministic `successor(action, choice)`, and
"h is avoidable within H" as a bounded H-fold existential chain finding a harm-free path, elaborated the way W6's
`eventually` is bounded quantification over `[0, H]`; size under `MAX_NODES`, `ResourceLimit` never a verdict. A
nondeterministic environment (several successors of one alternative) turns avoidability into a game and stays
outside. Once W6's time sort merges, supplied models are also checked for backward prevention. Stage 2 starts only
on a committed document that needs it (converged rule 3); the Asimov, C and U clauses below do not.

## 2. English (one reading each; rejected as today when `alternatives@0` is off)

| Wording | The one reading (the IDE's paraphrase) | Formal |
|---|---|---|
| legend (generated from the block): `Each robot faces one choice among the actions available to it and takes at most one of them.` `Doing nothing is one of them.` `"<action> leads to <harm>" records the declared model; for an action not taken it is a counterfactual judgment by <decider>.` | exclusivity; the inaction, when declared; the counterfactual decider | slot premise, validity, support |
| `<action> leads to <harm>` | In the declared model, if the action is taken, the harm occurs. Not "tends to". | `leads_to` |
| `<action> is available to <robot>` / `<action> is inaction` / `<action> is taken` | membership / the do-nothing alternative / what happened | base |
| `<harm> is avoidable by <robot>` | Some action available to the robot does not lead to the harm. | `avoidable` |
| `<harm> is unavoidable by <robot>` | The robot has at least one available action and every one of them leads to the harm. | `unavoidable` |
| `<action> allows <harm> to happen` | The action leads to the harm, and another action available to the same robot does not. | `allows` |
| `<action> prevents <harm>` | The action does not lead to the harm, and another action available to the same robot does. | `prevents` |
| `Every robot must prevent each harm ..., if ...` | W1 obligation, fulfilled by taking an action that does not lead to the harm. | act with fulfilment `avoids` |
| `<action> causes <harm>` | Only with a declared `proximate` predicate: the annotator judges the action the proximate cause; it then also leads to the harm. | open `causes` |

Input synonyms, rendered canonically: `preventable by` → `avoidable by`; `lets <harm> happen` → `allows <harm> to
happen`. Nothing else. Rejected with rewrites: undeclared `causes` (declare an open proximate-cause predicate, or
write `leads to`); `results in`, `brings about` (→ `leads to`); `could lead to`, `risks`, `increases the risk of`,
`contributes to`, `provides uplift to` (a hedged unit or an open degree term; the table is Boolean and the IDE says
so); `allows <person> to <act>` (deontic: W1 `may`); `through inaction allows` (readings A and B, fixture b). The
reader's checklist (norms.md 2.5) adds, for every rule using `allows` or `avoidable`, a two-action situation in
which the rule decides and one in which the harm is unavoidable and it does not. Whether the object-relative "a
harm ... that that action allows to happen" parses in one derivation is a spec item for the surface (W7 harness).

## 3. What the checker certifies and what stays open

**Certified** (certificate, witness or theorem; always relative to the declared alternatives and table):

1. W1 statuses on the extended document, unchanged machinery.
2. FOLLOWABLE / DILEMMA / UNKNOWN with classified, rendered witnesses (1.3).
3. Scenario evaluation: avoidability, allows/prevents, per-alternative outcomes, violations.
4. Model validity of the block's existence and uniqueness facts.
5. `alternative_monotone`: adding an available alternative never makes an avoidable harm unavoidable and never
   removes an `allows`; omitting one can only hide. The report prints `alternatives_declared` per chooser; the list
   is "alternatives considered so far", extensible by a challenger like a reading set (VISION.md 3).
6. The definitions' fixed meaning and the inlining (`inline_faithful`).

**Open, never certified:** the outcome table (causal model correctness); the truth of counterfactual rows
(support `observation` for the taken alternative, `testimony`, `calculation` or `assumption` otherwise; residual
line `counterfactual_leaves` with deciders); completeness of the alternative list; proximate versus distal
causation (`causes`); probability, risk, uplift, severity, breadth, reversibility (degrees: quantities, VEX);
consent, responsibility, vulnerability (open terms, C:339–341); joint causation (two robots who could each prevent
a harm both "allow" it; a harm preventable only jointly is avoidable by neither, a stated limit); multi-step
strategies (1.5); causal assertions between propositions (W2 kind `causal(because | in order to | prevents, kind,
kind)`, labelled, never checked).

## 4. Relation to the rest of VE

- **W1.** Profile `alternatives@0` requires `norms@0`. Rules, precedence, completions, duals, the conflict check,
  wire forms and every existing identity are unchanged; guards gain vocabulary; Background gains one slot;
  `environment_id` changes only for environments carrying the block.
- **Soft norms.** `mode`, `rank`, `alterable` attach to these rules as to any (C:187 is strict with a possible user
  switch; the direct-harm hard constraints stay hard). Followability on a soft document is conditional on `Coh_T`
  like every soft result. The dilemma check is the minimal form of the cross-act incompatibility that soft-norms
  1.6 defers: exclusivity is *declared* (the alternatives of one chooser), not inferred. Of the eight harm-weighing
  factors (C:334–341), two get a structural reading: counterfactual impact (C:335 → `avoidable`: freely available
  information makes the harm unavoidable by refusing) and proximate cause (C:338 → `causes` versus `allows`); the
  other six stay `factors` of the open weighing term.
- **Action alternatives and cross-obligation priority** (the North Star row without an estimate): 1.3–1.4 and
  fixtures d, e.
- **Rights (rank 2).** A protection right's positive duty (U:73, U:135 "protection against") is a prevention
  obligation of shape (B) on the duty-bearer; the shape is handed to the rights design and no U bytes are claimed.
- **VEX.** Every `leads_to` row is a W2 unit with `support`; VEX may later attach evidence records and lower bounds
  to counterfactual leaves and propagate them through `allows`; no probability enters the checker now.

## 5. Tests against the sources (deterministic fixtures, hand-written expectations)

| # | Source | Encoding | Expected |
|---|---|---|---|
| a | Asimov Law 1 corollary | robot R; `nothing` (inaction), `pull`; h1 to a human under `nothing` only | `nothing` allows h1, rule 7 forbids it; `pull` permitted; FOLLOWABLE on the scenario; (B) discharged by `pull` |
| b | the same, two harms | h1 under `nothing` only, h2 under `pull` only | both allow a harm, both forbidden; DILEMMA NONE-PERMITTED with the situation of 1.3; (A) and (B) both unfollowable here, so this is not a distinguishing model and the IDE says so |
| b′ | b plus `Rule 9 (exception to rule 7). Every action may be performed, if every other action available to that robot allows a harm to a human being to happen.` | an explicit resolution, an attributed narrowing in translation | FOLLOWABLE by certificate; both alternatives permitted in (b); the source does not settle the tie and the report says so |
| c | unavoidable harm | h under both alternatives | h unavoidable by R; neither allows; both permitted; rule 8 without its `avoidable` guard gives DILEMMA UNDISCHARGEABLE(prevent, h) and the IDE proposes the guard |
| d | Law 3 (Astra P2) | `shield`, `retreat`, `nothing`; h_self under `nothing` only | current Rule 6: both protective actions required, exclusive, DILEMMA OVER-REQUIRED (the README's approximation made visible); `Every robot must prevent each harm to that robot, if that harm is avoidable by that robot`: discharged by either, FOLLOWABLE |
| e | Zeroth-law tradeoff | `nothing` leads to h_humanity; `act` causes h_human | Law 0 inaction rule forbids `nothing`, Law 1 forbids `act`: DILEMMA; nothing in the source resolves it; any exception is a narrowing |
| f | C:187 risk to life | chooser: the assistant in a situation; `refuse`, `refer`, `answer`; obligation `respond_to_risk(assistant)` with fulfilment `refers(a) ∨ gives_safety_information(a)` | disjunctive discharge; `refuse` not clear; FOLLOWABLE when `refer` is available |
| g | C:335 counterfactual impact | `answer`, `refuse`; h under both (freely available information) versus under `answer` only | first: h unavoidable, `answer` permitted under a rule against allowing serious harm; second: forbidden; the *degree* of impact stays open |
| h | C:338 proximate cause; C:531 surgeon | `causes` declared open; three alternatives each with its harms | a strict rule on `causes` and a default rule on `allows` coexist; "more harm" is a quantity comparison, open |
| i | C:297 "could have done something differently" | assertive counterfactual about a past choice, no alternatives declared | OPEN with reason `alternatives unstated`; never CHECKED |
| k | U:5, U:7 preamble | "is the foundation of", "have resulted in" | W2 `causal` kind, LABELLED; outside this construct |
| l | validity; monotonicity | two inactions for one chooser; two taken; inaction not available; then add `pull` where h was unavoidable | `InvalidModel("alternatives", ...)` from Python and Lean; h becomes avoidable and `nothing` allows it, the report naming the added alternative |
| n | stratification | exception guarded by "no other available action is permitted" | `DependencyCycle: permitted` with hint `GuardOnOwnOutcome` and the rewrite of (b′) |

Plus: norms.md 10.1 regressions unchanged on documents carrying the block; identity fixtures (the block changes
`environment_id`, existing environments unchanged); the 10.8 binding fixtures repeated for followability packages.

## 6. Lean obligations (statement schemata; files `lean/VE/Alternatives/*`, `lean/ALTERNATIVES.md`)

Frozen `Norms/*`, `Route/*` and P0 files untouched; a new Lake target `ve_alternatives_route` wraps the norms
decoder as norms.md 11.4 prescribes (separate and validate the block, hash the original complete environment,
reject unknown fields, regenerate every formula). `D` is the decoded source; `E_base`, `Background_base`, `subst`,
`outcome`, `ConflictFree`, `DocumentExpansion` are W1's.

```lean
theorem alternatives_wellFormed (D) : WellFormedAlt D = true → Norms.WellFormed D.E (inlineTree D) = true
theorem inline_faithful (D) (φ) (hφ : φ.WellFormed (E_base ++ defs D) Γ) (S) (ρ) :
  (inline D φ).denote S ρ ↔ φ.denote (withDefinitions D S) ρ                 -- via W3 Definitions faithfulness
theorem alternative_monotone (S S') (h : S ≤_available S') :
  (avoidable S r h → avoidable S' r h) ∧ (allows S a h → allows S' a h)
theorem followable_sound (D) (hw) (hc : ∀ B, BaseAdmissible D.E B → ConflictFree D.E D.T B) (c : Certificate)
    (ok : checkCertificate E_base (Background_base D) (allR (followableFormula D)) c = true) :
  ∀ B, BaseAdmissible D.E B → ∀ S, DocumentExpansion D.E D.T B S →
    ∀ r, Typed r → (∃ a, available B r a) → ∃ a, ClearIn D S r a           -- ClearIn over S's actual relations
theorem dilemma_witness_sound (D) (hw) (M) (valid : M.Valid E_base) (hb : backgroundValid M = true) (r) (typed)
    (hd : (notFollowable D).eval M (tupleVal [r]) = true) :
  ¬ (∀ B, BaseAdmissible D.E B → Followable D B) ∧
  (ConflictFree D.E D.T M.asStructure → ∀ S, DocumentExpansion D.E D.T M.asStructure S → ¬ ∃ a, ClearIn D S r a)
theorem alternatives_wire_acceptance / alternatives_wire_followable_sound    -- raw JSON, as norms_wire_* (11.4)
```

Also executable guards: `validateAlternatives` agrees with the slot premises plus existence facts, and the finite
evaluation of `followable` agrees with its denotation (typed `eval_iff_denote`). Proof plan: `inline_faithful`
from W3; the two soundness theorems from `subst_sound`, `prefix_satisfaction` and `conflictFree_expands_document`;
the wire theorems by W1's chain. Audit allowlist unchanged. Statement review questions (rule 10): is `clear` the
intended reading of "complies with every rule here"; is the per-action clause (`a' = a`) right when an action is
available to two choosers; is existence-by-validity acceptable; is `unavoidable`'s existence conjunct wanted.

## 7. Work items

| # | Item | Owner, effort | Notes |
|---|---|---|---|
| 0 | Prerequisite: the Asimov use case merges via the train (`usecases/asimov-laws`) | in progress | fixtures a–e build on it |
| 1 | `docs/spec/alternatives.md`: block, slot premises, definitions, followability, diagnostics (`FulfilmentNotBase`, `GuardOnOwnOutcome`, `InvalidModel("alternatives")`), wordings, fixtures a–n; Astra + Fable statement review | spec, 2 days | review questions in section 6 |
| 2 | Lean `lean/VE/Alternatives/{Decl,Inline,Background,Followable,Wire,Run}.lean`, section 6, executable `ve_alternatives_route`, `lean/ALTERNATIVES.md` | Lean, 5–7 days (Opus 5.5) | semantics owner under the migration rule (SEMANTICS-MIGRATION-PLAN 6): no new Python semantics |
| 3 | Python surface and adapter: `ve/surface/alternatives.py`, block validation in `ve/environment.py`, dispatch to the Lean executable, coverage lines `alternatives_declared` and `counterfactual_leaves`; Rust untrusted evaluation | Python, 3 days (Sol) | a Python mirror of `followable` only if the parity rule still binds at start (one day, decided then) |
| 4 | Asimov v2: harm sort, `leads_to`, inaction rules as reading set {A, B}, Law 3 as a prevention duty, dilemma witnesses (b, e), README boundary rewritten, tests extended | 1–2 days (Sol) | the README's three UNFORMALISED items become checked in the declared model, DILEMMA, or open |
| 5 | Pilot probes: C:187, C:221, C:297, C:335, C:338, C:531; U:5, U:7, U:73; reading sets with cited narrowings under the soft-norms counting protocol (end-to-end admission, split-only baseline, blind review) | pilot, 2 days | prediction: no change in the causation-primary count (the tagged C units u0010, u0011, u0019–u0021 are explanatory prose, co-blocked); any gain is measured, including zero |
| 6 | W8: `declare_alternatives`, `add_outcome_row`, paraphrases with a two-action example and the dilemma explanation; fidelity gate first | later | not before item 4 passes |
| 7 | Stage 2 (traces, horizon, backward-prevention validity) and VEX bounds on counterfactual leaves | not scheduled | trigger: a committed document that needs them (converged rule 3) |

Sequencing: 1 → statement review → 2 ∥ 3 → 4 → 5; 6 after 4. Nothing waits on W6 or on the W1×W3 composition gap.

## 8. Risks

1. **Fake precision by table.** A Boolean `leads_to` stands in for graded causal belief. Mitigation: a support
   label on every row, the counterfactual decider in the legend, "in the declared model" in every verdict, and the
   refusal of `risks`, `could lead to`, `uplift` as wordings.
2. **Gaming the alternative list.** Omitting an alternative hides an `allows`; adding a fanciful one manufactures
   blame. Mitigation: `alternative_monotone` in the report, the list printed with its declarer, challenger extension.
3. **DILEMMA read as a moral verdict.** Mitigation: fixed wording "no available action complies with every rule in
   this situation", with the (b′) rewrite offered beside it.
4. **English collisions.** "allows" is everyday permission language; "leads to" suggests tendency. Mitigation: the
   `to happen` tail, fixed paraphrases, rejected synonyms, W7 unambiguity fixtures, W8 fidelity gate first.
5. **Fragment loss.** Quantified guards put every document using `allows` outside the small-model fragment, so
   FOLLOWABLE needs a tableau certificate and UNKNOWN will be common. Mitigation: honest UNKNOWN with budget,
   witness search bounded per chooser, search hints as for conflict packages.
6. **Scope creep and modelling misfit.** General causation, temporal logic, games; joint action, repeated and
   continuous choice. Mitigation: 1.5 and section 3 name each boundary and trigger; separate choosers for separate
   decisions.
7. **No measurable gain on C.** The causation-tagged units are mostly explanatory prose; the norm clauses this
   construct serves are `norms`-primary. The plan is still worth its spec (the Asimov gap and the constitution's
   harm-avoidance section need it), and item 5 reports what it measures.

## Summary

Causation enters VE as *preventable harm over explicit alternatives*: a profile `alternatives@0` that declares,
per chooser, a finite list of alternatives (optionally including inaction) and a declared outcome table
`leads_to(action, harm)`, and fixes three defined words, avoidable, allows and prevents, inlined into ordinary W1
guards. "Through inaction allow harm" becomes a per-action prohibition or a per-harm duty of prevention (a
reading set in translation), both checked by unchanged `norms@0` machinery. One new check, followability, reports
FOLLOWABLE, DILEMMA (a rendered situation in which no available action complies with every rule) or UNKNOWN, and
makes priority across obligations something an author writes over facts rather than something the checker
invents. Certified: structure over the declared model. Open, listed as residual: the table, counterfactual truth,
completeness of alternatives, proximate causation, degrees, consent and responsibility. Time and multi-step
strategies are a stated stage 2; Lean owns the semantics; no coverage gain is predicted.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-27 | Draft 1 | Initial plan. Plan only: no code, Lean or frozen contract changed. |
