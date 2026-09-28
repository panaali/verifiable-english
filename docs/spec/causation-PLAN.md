# Causation as preventable harm over explicit alternatives: plan (`alternatives@0`)

> Status: planning draft 4 (2026-09-28), revision 2 transcribing the converged Astra + Fable debate
> (`~/code/manage-agents/debates/design-causation/{astra,fable}.md`, CONVERGED after round 3, verdict **REVISE**),
> synchronized with draft 3 of `alternatives.md`, which applies the ten edits of the Astra + Fable statement review
> of the spec (`~/code/manage-agents/debates/causation-spec/{astra,fable}.md`, CONVERGED after round 3, verdict
> **FIX**; section 9.1 and `alternatives.md` 12 attribute each edit) and the four corrections of Astra's
> verification of that draft (`~/code/manage-agents/causation-verify1b-astra.final.md`, verdict **FAIL**; section
> 9.2 and `alternatives.md` 13 attribute each correction).
> The edit set applied here is exactly the final joint position: Fable's round-2 proposed joint position, which
> adopts Astra's six round-1 changes and five round-2 requirements, together with Fable's own edits (the rule that
> forbids `pull` under reading A and the carve-out under B; the status computed only on CONFLICT-FREE; Lean-only
> validity and followability with Rust untrusted; a conservativity statement and a ROADMAP trust-cost line), the
> A/B distinguishing model, `BaseAdmissibleAlt`, universal slot premises with finite-only existence validation and
> the documented completeness cost, b′'s exact rule set, JOINTLY-UNDISCHARGEABLE, and the four fixture-format items
> Fable accepted in round 3. Section 9 maps each debate item to its change. Item 1 (`docs/spec/alternatives.md`)
> was written from revision 2 with no further plan round; the Astra + Fable statement review of that spec, each
> reviewer deriving the fixture expectations from the stated rule sets and premises before reading the expected
> results, returned FIX with ten exact edits, applied in the spec's draft 2 and here; Astra's verification of that
> draft returned FAIL with four corrections, applied in the spec's draft 3 and here; the repeated gate on the
> changed entries (`alternatives.md` 10.13) precedes items 2 and 3. Inputs as in draft 1: the Asimov use case (`~/code/ve-asimov/usecases/asimov-laws/`,
> Astra review `manage-agents/asimov-review-astra.final.md`); [norms.md](norms.md) (W1); [soft-norms-PLAN.md](soft-norms-PLAN.md)
> and [soft-norms.md](soft-norms.md); [document.md](document.md) (W2); the pinned pilots
> (`manage-agents/pilots/{claude-constitution,udhr}/`, cited as `C:n` and `U:n`); [VISION.md](../../VISION.md);
> [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md) section 6; `design/vex-mandatory-evidence.md`. Nothing
> here changes a frozen contract, a `norms@0` identity or a checker function. Theorem statements are obligations,
> not proofs; no coverage number is predicted.

## 0. Problem and stance

The Asimov README leaves the inaction clauses UNFORMALISED: "through inaction, allow ... to come to harm" needs "a
causal account of what the robot could have prevented. W1 has no such account." The same gap blocks C:187 (refer to
emergency services when life is at risk), C:221 (actions that could cause severe harm), the harm-weighing factors
C:334–341 and U:73 ("protection of the law against such interference"). Causation is the primary blocker on 81 C
units and 2 U units, almost all co-blocked by quantities, modality or attribution.

Stance. "Allow through inaction" is a claim about **what else the agent could have done**. The checker cannot
certify causal facts (converged rule 8), but it can certify structure over a **declared** causal model: a finite
list of alternatives per chooser, each action belonging to exactly one chooser, and a table saying which
alternative leads to which harm, with every cell either stated with its support or covered by an attributed
completion assumption. The construct is small: explicit alternatives, the outcome table, three defined words
(*avoidable*, *allows*, *prevents*) and one new check (can the mapped obligations and the declared action
constraints be met at every choice?). Every verdict reads "in the declared model". A scenario result is bound to
the scenario; a document-wide result exists only as a tableau certificate over a stated class of structures, and
the class is named with its cost. The table's correctness, counterfactual truth, degrees, proximate causation and
the completeness of the alternative list stay open and are listed in the residual. No new logic: everything
elaborates into `norms@0` over base predicates, definitions are inlined into guards, and the checks reuse W1's
substitution, tableau and witnesses. Under SEMANTICS-MIGRATION-PLAN section 6 the semantics are Lean-only: Python
contributes the block's shape check, dispatch, surface and proof search; Rust evaluates untrusted.

## 1. Semantics

### 1.1 Declarations (environment block, identity-bound like `regulated`)

```json
"alternatives": {
  "chooser": "robot", "action": "action", "harm": "harm",
  "available": "available",          // available(action, robot): the action is one of the robot's alternatives
  "leads_to":  "leads_to",           // leads_to(action, harm): the declared outcome table
  "outcomes":  "signed",             // or {"complete_by": "<decider>"}: how unstated cells are read (1.2)
  "performed": {"permission": "permitted", "obligation": "required"},   // optional: the W1 pair meaning "take a"
  "inaction":  "inaction",           // optional: inaction(action)
  "taken":     "taken",              // optional: taken(action), the construct's `done`
  "proximate": "causes"              // optional: causes(action, harm), an open predicate with a decider
}
```

A *chooser* is one agent at one decision point; a second decision by the same agent is a second chooser, unlinked
(1.5). **Every action belongs to exactly one chooser** (Astra 1): shared actions are rejected, because a unary
`taken`, `permitted` or `required` on a shared action would couple two supposedly independent choices. Sorts and
predicate names are the author's; argument orders and verbalisations of the role predicates are fixed by the
profile (`{0} is available to {1}`, `{0} leads to {1}`, `{0} is inaction`, `{0} is taken`, `{0} causes {1}`), so
each wording has one reading and `risks`, `could lead to` cannot be smuggled in as a verbalisation. Regulated
predicates and rules are W1's, unchanged: Asimov keeps `permitted(action)` and `required(action)`. An obligation
predicate whose first argument is the chooser sort may declare a `fulfilment`: a base formula over `(action,
remaining arguments)` naming which alternative discharges it; the profile supplies `avoids(a, h) := ¬leads_to(a,
h)` for duties of prevention (`FulfilmentNotBase` if a fulfilment mentions a regulated, defined or profile symbol).
A fulfilment body is never an atom of a rule or unit: it enters the followability formula (1.4), the scenario
words and the legend only, so the tree mentions the four profile words and no fulfilment name, and no declared
sort, predicate or constant may be named as a profile word (`AlternativesReserved: <name>`).
An obligation without a fulfilment that is not the `performed` obligation is *unmapped*: it does not constrain the
choice and the report names it (1.3).

**Slot premises** (Background slot `alternatives`, a generator in the P0 hook table after `profile`), all closed
universal formulas over base predicates:

```text
own          ∀a r r'.  available(a, r) ∧ available(a, r') → r = r'                       an action has at most one chooser
one_taken    ∀r a a'.  available(a, r) ∧ available(a', r) ∧ taken(a) ∧ taken(a') → a = a'  (when `taken` is declared)
one_inaction ∀r a a'.  available(a, r) ∧ available(a', r) ∧ inaction(a) ∧ inaction(a') → a = a'  (when `inaction` is declared)
proximate    ∀a h.     causes(a, h) → leads_to(a, h)                                       (when `proximate` is declared)
```

`BaseAdmissibleAlt D B := BaseAdmissible D.E B ∧ Sat B (altPremises D)` is the admissibility contract of every
alternatives theorem (Astra 5): W1's `BaseAdmissible` is `E_base` plus `Background_base`, and the route strips the
block before W1's decoder sees the document, so the slot premises must be named explicitly in `hc` and in both
soundness theorems (section 6). The conflict check on this route runs over `Background_base ++ altPremises`.

**Existence facts are validated, never assumed.** A valid finite scenario also satisfies: every action is
available to some chooser; when `inaction` is declared, every chooser with an alternative has exactly one inaction
among them; under `outcomes: signed` every (available action, harm) cell is stated. These are checked on supplied
finite models (`InvalidModel("alternatives", ...)`) together with the supplied signed rows (typed, one per pair,
positive rows equal to the `leads_to` table) and are not premises. A chooser with no alternative is admitted, is
followable vacuously and is reported `no alternatives` (1.4). **Consequently certificates quantify over
a class broader than accepted scenarios**: a FOLLOWABLE certificate holds in every `BaseAdmissibleAlt` structure,
hence in every accepted scenario, but a document can be followable in every accepted scenario and still have no
certificate. Named cost: an obligation discharged by inaction (fulfilment `inaction(a)`) is met in every valid
scenario, yet a structure in which a chooser with alternatives has no inaction refutes `∀r. followable(r)`; no
certificate exists and no valid witness exists either, so the status is UNKNOWN (fixture u). The reasons for
keeping the premises universal are W1's Background shape, immediate soundness over the superclass, and that an
existence premise can be added later (a new profile version) without changing any accepted scenario. norms.md
7.1(3) is *not* the reason: it is a fragment-membership condition, and every document using `allows` is outside
the fragment anyway (Fable round 2, Astra round 2 item 3).

### 1.2 The outcome table: negative cells are accountable (Astra 4)

`avoidable` depends on `¬leads_to`, so an omitted cell is a claim that an action avoids a harm. It must never
become evidenced silently. The block's mandatory `outcomes` field chooses one of two readings:

- **`signed`**: every cell is stated. In a W2 document each cell is a unit, positive `<action> leads to <harm>` or
  negative `It is not the case that <action> leads to <harm>.`, with its own `support`; a conclusion needing an
  unstated negative cell is not provable (the countermodel makes the cell true). On a supplied scenario the table
  is a list of signed rows, and a missing row for an available action and a harm is
  `InvalidModel("alternatives", "outcome of <a> for <h> unstated")`.
- **`complete_by: <decider>`**: an action leads to a harm only where the document says so. The route adds one
  labelled premise `alternatives:table_complete`, regenerated from the document's positive cells over constants
  (`∀a h. leads_to(a, h) → ⋁ (a = c_a ∧ h = c_h)`), listed in the residual as an assumption of the decider; on a
  scenario the missing rows are read as negative and listed under `assumed_harm_free` with the decider. Document
  completion and row completion are distinct: the premise comes from the document's cells alone and is evaluated
  on a scenario like every other base premise, so a scenario's positive rows must lie within the document's
  positive cells (`InvalidModel("alternatives", "premise alternatives:table_complete fails")` otherwise), and rows
  change neither the premise nor the document hash. Every result that uses the premise says `conditional_on:
  alternatives:table_complete`.

The residual line `counterfactual_leaves` lists every cell with its support (`observation` for the taken
alternative, `testimony`, `calculation` or `assumption` otherwise) and decider.

### 1.3 Definitions (bodies fixed by the profile, inlined into guards)

```text
avoidable(h, r)    := ∃a. available(a, r) ∧ ¬leads_to(a, h)                       some alternative of r avoids h
unavoidable(h, r)  := (∃a. available(a, r)) ∧ ¬avoidable(h, r)                    r has alternatives and all lead to h
allows(a, h)       := leads_to(a, h) ∧ ∃r. available(a, r) ∧ avoidable(h, r)      a leads to h; another alternative of a's chooser would not
prevents(a, h)     := ¬leads_to(a, h) ∧ ∃r. available(a, r) ∧ ∃a'. available(a', r) ∧ leads_to(a', h)
discharged_o(r, x̄) := ∃a. available(a, r) ∧ taken(a) ∧ F_o(a, x̄)                  o a mapped obligation on (chooser, x̄)
violation_o(r, x̄)  := O_o(r, x̄) ∧ (∃a. available(a, r) ∧ taken(a)) ∧ ¬discharged_o(r, x̄)
```

By `own`, the `∃r` in `allows` and `prevents` is single-valued, so "another action available to the same robot"
is exact and the draft-1 review question about `a' = a` across choosers vanishes (Fable 3). `allows` covers both
enabling by an act and failing to prevent by inaction; the `inaction` marker tells them apart, and *causing*
(proximate) is the separate open predicate `causes`, never derived. The elaborator inlines the bodies into guards,
which W1 admits (quantified guards, norms.md 9.2), so the document that reaches the route is plain `norms@0` over
`E_base` plus the slot's premises; no W1×W3×W5 composition is needed (INTEGRATION-GAPS). Theorem `inline_faithful`
(section 6) says inlining equals the definitional reading, so when that gap closes the bodies may become
definition layers with no change of meaning. `discharged` and `violation` are evaluated on scenarios, like W1's
`violation := required ∧ ¬done`, and are not route premises.

Two W1 encodings of a duty of prevention. **They differ outside dilemmas** (Astra 2; the draft-1 sentence
"differing only in dilemmas" is withdrawn):

```text
(A) per action   Rule 7. Every action must not be performed, if that action is inaction and there is a harm such
                 that both that harm is a harm to a human being and that action allows that harm to happen.
(B) per harm     regulated prevent_required(robot, harm), obligation, deny-by-default, act "{0} prevent {1}",
                 fulfilment avoids.  Rule 8. Every robot must prevent each harm that is a harm to a human being,
                 if that harm is avoidable by that robot.
```

Distinguishing model (fixture o): robot R with `nothing` (inaction), `act` and `rescue`; `nothing` and `act`
lead to a harm h to a human, `rescue` does not. Under (A) rule 7 forbids `nothing` only, so `act` and `rescue`
are both clear; under (B) `prevent_required(R, h)` holds and only `rescue` discharges it, so `act` is permitted
but not clear. Both readings are followable at R; they differ in which alternatives comply. In translation the
inaction clause is a reading set `{A, B}` with this model recorded as its distinguishing model; "injure" versus
"come to harm" is a second set `{causes, allows}`: the existing direct-injury rules (`injures_human`, annotator
decided) are the `causes` reading restricted to humans, and rule 7′ (rule 7 without the inaction condition, on
every action) is the `allows` reading. Under (A), forbidding a *non-inaction* alternative that leads to harm needs
one of these two, stated and attributed: the annotator's classification `injures_human(a)` under rule 3
(a fact), or rule 7′ (a reading of "injure"). Neither is in Asimov's text as a rule on all actions; each is a
narrowing where it is used (Fable 1, Astra round 2 item 1).

### 1.4 The followability check (the one new check)

Computed **only when the document's conflict status is CONFLICT-FREE** (Fable 2): `followable_sound` assumes
`ConflictFree` on every `BaseAdmissibleAlt` structure, so on CONFLICT and on UNKNOWN the status is
`not computed: conflict status <CONFLICT | UNKNOWN>`. With `O_p°` the base-substituted outcomes of norms.md 4.5,
`(m, q)` the declared `performed` pair and `F_o` the mapped fulfilments:

```text
clear(r, a)   := available(a, r) ∧ O_m°(a)                                          taking a is permitted
               ∧ ∀a'. (available(a', r) ∧ O_q°(a') → a' = a)                       and forgoes no required alternative
               ∧ ⋀_{o mapped} ∀x̄. (O_o°(r, x̄) → F_o(a, x̄))                         and discharges every mapped obligation on r
followable(r) := (∃a. available(a, r)) → ∃a. clear(r, a)
```

`clear` takes (chooser, action), the order of the Lean `ClearIn`; argument orders are fixed once in
`alternatives.md` 7 (avoidable, unavoidable: (harm, chooser); allows, prevents: (action, harm)), each generated
formula's context is its argument list reversed and it is evaluated at `tupleVal` in argument order. Absent parts
of the block drop their conjunct; a chooser with no alternative is followable vacuously. The checked claim is
therefore about **the mapped obligations and the declared action constraints**, never "every rule" (Astra 6); the
report names each unmapped obligation (Fable round 3). Verdict scope is explicit:

| Result | Evidence | Scope and binding |
|---|---|---|
| **FOLLOWABLE** | a tableau certificate for `Background_base ++ altPremises ++ Γ_base ⊢ ∀r. followable°(r)`, `Γ_base` the document's active base premises (including `alternatives:table_complete`), listed under `conditional_on` | document-wide over `BaseAdmissibleAlt`; bound to `environment_id` and the document hash as conflict packages are (norms.md 5.2, 11.4). Unqualified FOLLOWABLE is reserved for this certificate |
| **DILEMMA** | a valid finite base model with its signed rows, satisfying `altPremises`, the row and existence facts and `Γ_base`, and a typed chooser at which `¬followable°` evaluates true; Lean certifies exactly this. The classification NONE-PERMITTED, OVER-REQUIRED, UNDISCHARGEABLE(o, x̄) or JOINTLY-UNDISCHARGEABLE(o₁(x̄₁), …, oₖ(x̄ₖ)) and the rendered situation are a *diagnosis* computed by the untrusted evaluator; minimality of the listed set is a report property, not a theorem | refutes the document-wide claim; bound to environment, document and the witness model |
| **UNKNOWN** | neither within budget; the budget named | document |
| **scenario** | on a supplied finite model, after the regenerated conflict formulas have been evaluated on it (a true one is answered as that CONFLICT witness and nothing else is rendered): per chooser `clear`, permissions, requirements, avoidability, who allows or prevents what, violations when `taken` is supplied; text `<chooser> has a clear action: <list>`, `no clear action at <chooser>: <diagnosis>` or `no alternatives at <chooser>`; a scenario failure is also a document DILEMMA only when the document is CONFLICT-FREE | bound to `environment_id`, the document hash **and the model id** (Astra 3); never called FOLLOWABLE |

Enumeration never yields FOLLOWABLE. JOINTLY-UNDISCHARGEABLE is the diagnosis when every mapped obligation
instance at the chooser is discharged by some permitted, non-forgoing alternative but no single alternative
discharges all of them (fixture b under B); UNDISCHARGEABLE(o, x̄) is the single-instance case (fixture c). A
DILEMMA is not a verdict that the rules are wrong; it is a situation in which no available action complies with
the mapped obligations and the declared action constraints, which is what "ought implies can" asks an author to
face. Two consequences of the corrected fixtures, stated so that expectations can be derived: a document that
keeps Asimov's Rule 5 (`law-2-obey`: an ordered permitted action is required) or Rule 6 is never document-wide
FOLLOWABLE, because two ordered permitted alternatives are both required (fixture j); and a prohibition whose
guard is an unconstrained base predicate (`injures_human`) is refuted by the structure in which every alternative
of one chooser satisfies it, so a certificate needs an escape covering that case (fixture b′) or an author
premise in `Γ_base`. Rust evaluates the substituted formulas untrusted (norms.md 11.6).

### 1.5 Stratification: priority across obligations is written over facts

An exception guarded by "if it is not the case that another action available to that robot may be performed"
mentions `permitted` on its own predicate and is `DependencyCycle: permitted` (norms.md 4.1(4)). The IDE offers,
under the hint `GuardOnOwnOutcome`, the factual guard of rule 9 (1.4, fixture b′): "if there is a robot such that
that action is available to that robot and every other action available to that robot either injures a human
being or allows a harm to a human being to happen" (short object form, subject to fixture q; the long form is
canonical until then). **This rewrite is an author-selected change of meaning, not an
equivalence** (Astra 6): the factual guard names which facts forbid the other alternatives today; a rule added
later that forbids alternatives for another reason is not tracked by it. The IDE says so beside the offer. The
"that robot" of a rule on an action predicate is bound only by `there is a robot such that that action is
available to that robot and ...`; by `own` that robot is unique, and the paraphrase says "the robot that can take
it" (Fable 4). So priority across different obligations for different actions is never a checker primitive: it is
a W1 exception over facts, a soft-norm rank on the colliding rules (which resolves per action only, soft-norms
1.6), or an open decider in the residual; the followability check certifies whatever was written, or shows the
situation in which it fails.

### 1.6 Time and traces (stage 2, stated so that stage 1 is its one-step case)

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
| legend (generated from the block): `Each robot faces one choice among the actions available to it and takes at most one of them.` `Each action is available to at most one robot.` `Doing nothing counts as one of a robot's actions; every checked situation lists exactly one inaction per robot with any alternative.` `"<action> leads to <harm>" records the declared model; for an action not taken it is a counterfactual judgment by <decider>.` `Every cell of the outcome table is stated.` / `An action leads to a harm only where this document says so; <decider> stands behind every unstated cell.` `A robot prevents a harm by taking an action that does not lead to it.` | exclusivity; ownership; the inaction, when declared, as a validity fact; the counterfactual decider; the outcomes mode; the fulfilment | slot premises, validity, support |
| `<action> is available to <robot>` / `<action> leads to <harm>` / `<action> is inaction` / `<action> is taken` | membership / in the declared model, if the action is taken the harm occurs (not "tends to") / the do-nothing alternative / what happened | base, fixed verbalisations |
| `It is not the case that <action> leads to <harm>.` | the negative cell, stated with its support | `¬leads_to` |
| `<harm> is avoidable by <robot>` | Some action available to the robot does not lead to the harm. | `avoidable` |
| `<harm> is unavoidable by <robot>` | The robot has at least one available action and every one of them leads to the harm. | `unavoidable` |
| `<action> allows <harm> to happen` | The action leads to the harm, and another action available to the same robot does not. | `allows` |
| `<action> prevents <harm>` | The action does not lead to the harm, and another action available to the same robot does. | `prevents` |
| `every action available to <robot> <verb phrase>` / `every other action available to <robot> <verb phrase>` / `another action available to <robot> <verb phrase>` (guards; reference form `that other action`) | all of the robot's alternatives / all of them except the action the rule is about / some alternative other than that action | `∀a'. available(a', r) → …` / `∀a'. available(a', r) ∧ a' ≠ a → …` / `∃a'. available(a', r) ∧ a' ≠ a ∧ …` |
| `there is a robot such that that action is available to that robot and …` | binds the chooser of an action inside a rule on an action; by ownership it is "the robot that can take it" | `∃r. available(a, r) ∧ …` |
| `Every robot must prevent each harm ..., if ...` | W1 obligation, fulfilled by taking an action that does not lead to the harm. | act with fulfilment `avoids` |
| `<action> causes <harm>` | Only with a declared `proximate` predicate: the annotator judges the action the proximate cause; it then also leads to the harm. | open `causes` |

Input synonyms, rendered canonically: `preventable by` → `avoidable by`; `lets <harm> happen` → `allows <harm> to
happen`; `<action> does not lead to <harm>` → the negation form. Nothing else. Rejected with rewrites: undeclared
`causes` (declare an open proximate-cause predicate, or write `leads to`); `results in`, `brings about` (→ `leads
to`); `could lead to`, `risks`, `increases the risk of`, `contributes to`, `provides uplift to` (a hedged unit or
an open degree term; the table is Boolean and the IDE says so); `allows <person> to <act>` (deontic: W1 `may`);
`through inaction allows` (readings A and B with the distinguishing model o); `that robot` in a rule on an action
with no binder (the `there is a robot such that` rewrite). The reader's checklist (norms.md 2.5) adds, for every
rule using `allows` or `avoidable`, a two-action situation in which the rule decides and one in which the harm is
unavoidable and it does not; for every mapped obligation, a situation in which it is discharged and one in which
no permitted alternative discharges it. Before surface acceptance (items 3 and 4) every new wording has binding,
unique-derivation and paraphrase fixtures (fixture q); whether the short object form "allows a harm to a human
being to happen" parses in one derivation is decided there, and until then the long form `there is a harm such
that both that harm is a harm to a human being and that action allows that harm to happen` is canonical.

## 3. What the checker certifies and what stays open

**Certified** (certificate, witness or theorem; always relative to the declared alternatives and table, over
`BaseAdmissibleAlt`):

1. W1 statuses on the inlined document, unchanged machinery, with the slot premises in the conflict background.
2. FOLLOWABLE (certificate, document-wide, `conditional_on` the base premises it uses) / DILEMMA (Lean certifies
   `¬followable°` at a typed chooser of a valid witness; the diagnosis is rendered) / UNKNOWN (1.4).
3. Scenario evaluation bound to the model: avoidability, allows/prevents, per-alternative `clear`, violations.
4. Model validity: the slot premises, the supplied signed rows, the existence facts and, under `signed`, outcome
   coverage; under `complete_by`, the positive rows within the document's cells.
5. `owner_unique`: an action's chooser is unique; `alternative_monotone`: on a well-formed block (whose role
   predicates are pairwise distinct, so extending `available` leaves `leads_to` unchanged) adding an available
   alternative never makes an avoidable harm unavoidable and never removes an `allows` or a `prevents`; omitting
   one can only hide (`clear` is not monotone and is not claimed so). The report prints `alternatives_declared` per chooser; the
   list is "alternatives considered so far", extensible by a challenger like a reading set (VISION.md 3).
6. The definitions' fixed meaning and the inlining (`inline_faithful`, over structures admissible for `E`).
7. Conservativity (Fable 6, converged rule 4): environments without the block are untouched by construction (new
   route, frozen files unchanged), and for base premises and conclusions that do not mention the block's
   predicates the slot premises add no consequence (`alternatives_conservative`, over `oldEnv`); agreement of the
   two routes on conclusions over regulated predicates (fixture r4) is differential evidence, not a theorem.

**Open, never certified:** the outcome table (causal model correctness); the truth of counterfactual rows and of
every negative cell (`counterfactual_leaves` with support and decider; `assumed_harm_free` with the completion's
decider); completeness of the alternative list; proximate versus distal causation (`causes`); probability, risk,
uplift, severity, breadth, reversibility (degrees: quantities, VEX); consent, responsibility, vulnerability (open
terms, C:339–341); joint causation (two robots who could each prevent a harm both "allow" it; a harm preventable
only jointly is avoidable by neither, a stated limit); multi-step strategies (1.6); causal assertions between
propositions (W2 kind `causal(because | in order to | prevents, kind, kind)`, labelled, never checked); the
existence facts as premises (1.1: validated on scenarios; certificates quantify over the broader class, with the
named cost).

## 4. Relation to the rest of VE

- **W1.** Profile `alternatives@0` requires `norms@0`. Rules, precedence, completions, duals, the conflict check,
  wire forms and every existing identity are unchanged; guards gain vocabulary; Background gains one slot;
  `environment_id` changes only for environments carrying the block.
- **Soft norms.** `mode`, `rank`, `alterable` attach to these rules as to any (C:187 is strict with a possible user
  switch; the direct-harm hard constraints stay hard). **Combining the two profiles is gated on the soft-norms
  composition proof** (Astra 5): until the soft route's `BaseAdmissible′` and this route's `BaseAdmissibleAlt`
  are composed in Lean, a document enabling both profiles is `UnsupportedProfile: alternatives@0 with
  soft-norms@0` on this route. The dilemma check is the minimal form of the cross-act incompatibility that
  soft-norms 1.6 defers: exclusivity is *declared* (the alternatives of one chooser), not inferred. Of the eight
  harm-weighing factors (C:334–341), two get a structural reading: counterfactual impact (C:335 → `avoidable`:
  freely available information makes the harm unavoidable by refusing) and proximate cause (C:338 → `causes`
  versus `allows`); the other six stay `factors` of the open weighing term.
- **Action alternatives and cross-obligation priority** (the North Star row without an estimate): 1.4–1.5 and
  fixtures b′, d, e, j.
- **Rights (rank 2).** A protection right's positive duty (U:73, U:135 "protection against") is a prevention
  obligation of shape (B) on the duty-bearer; the shape is handed to the rights design and no U bytes are claimed.
- **VEX.** Every cell is a W2 unit with `support`; VEX may later attach evidence records and lower bounds to
  counterfactual leaves and propagate them through `allows`; no probability enters the checker now.
- **Migration rule and ROADMAP.** Causation is named Lean-only (SEMANTICS-MIGRATION-PLAN section 6): no Python
  semantics, no Python rollback target, `CheckerUnavailable` under `VE_AUTHORITY=python`. `ROADMAP.md` gains the
  trust-cost line of converged rule 4 beside its causation row: a new decoder, elaborator (inlining, slot premises,
  followability formula) and executable in the trusted base, proved from raw JSON; the diagnosis and the Python
  block-shape check untrusted.

## 5. Tests against the sources (deterministic fixtures, hand-written expectations)

Every row states its rule set, its premises and model, and its verdict scope (Astra round 2 item 2; Fable round 3
item 1). Rules 1–6 are `rules.ve` by stable name (`law-3-permission`, `law-2-permission`, `law-1-direct` = rule 3,
`law-0-direct`, `law-2-obey` = rule 5, `law-3-preserve` = rule 6); rules 7, 7′, 8, 8c, 9, 10 are 1.3–1.5 and
`alternatives.md` 2.6. In a rule subset, `over` entries naming absent rules are dropped (`law-1-direct` is
"exception to rule 2" verbatim; W1's `UnknownRule` otherwise), so {3, 7} has no precedence edge. Unless stated: one
robot R, completions as declared in the Asimov environment (permission
allow-by-default, obligations deny-by-default), `outcomes: signed`, `Γ_base` empty, no `injures_human`
classification. "Scenario" means the result is bound to the model and never called FOLLOWABLE; "document" means
a certificate or a certified witness for the rule set named. The exact expected results are in `alternatives.md`
8.2, separated from the fixture definitions in 8.1 so that reviewers derive them first.

| # | Source | Rule set, premises, model | Scope | Expected |
|---|---|---|---|---|
| a | Asimov Law 1 corollary | {3, 7}; `nothing` (inaction), `pull`; h1 to a human under `nothing` only | scenario | `nothing` allows h1 and is forbidden by rule 7; `pull` permitted; R has a clear action: `pull`. Conflict status CONFLICT-FREE first |
| b | the same, two harms | h1 under `nothing` only, h2 under `pull` only; A₀ = {3, 7}; A₁ = {3, 7} + annotator fact `injures_human(pull)`; A₂ = {3, 7′}; B = {3, 8} | scenario; document for A₁, A₂, B | A₀: `pull` clear, no dilemma. A₁: both forbidden, NONE-PERMITTED, a valid witness: document DILEMMA for {3, 7}, witness the A₁ model. A₂: likewise, document DILEMMA for {3, 7′}. B: both duties required and individually dischargeable, no action discharges both: JOINTLY-UNDISCHARGEABLE(prevent(R,h1), prevent(R,h2)), document DILEMMA. The model distinguishes A₀ from B and not A₁/A₂ from B; the reading set's distinguishing model is o |
| b′ | an explicit resolution (a narrowing attributed to the translator) | (A): {3, 7, 9} with rule 9 an exception to **both** 3 and 7, no rule on `required`; (B): {3, 8c, 9_B} with `Γ_link := ∀a. injures_human(a) → ∃h. harms_human(h) ∧ leads_to(a, h)` (short object form in its English, subject to q) | document; scenario b with A₁'s fact | (A): FOLLOWABLE by certificate; on b both alternatives permitted and clear, the tie unsettled by the source. Rule 9 as an exception to 7 only (A⁻): **CONFLICT**, since at a chooser whose every alternative injures rule 3 forbids and rule 9⁻ permits each alternative with no precedence edge between them (norms.md fixture i(b)); followability `not computed: conflict status CONFLICT`. (A) or (B) plus rule 5: DILEMMA (j); not A⁻, whose permission conflict rule 5 leaves in place (it selects on `required` only and carries no `over` entry), so followability stays `not computed` (`alternatives.md` b′(A⁻5)). (B): FOLLOWABLE with `Γ_link` (`conditional_on` it); without it DILEMMA UNDISCHARGEABLE at the mixed witness (an injuring alternative that leads to no harm beside a harmless-classified one that does) |
| c | unavoidable harm | h under both alternatives; {3, 7}; {3, 8}; {3, 8⁻} (rule 8 without its `avoidable` guard) | scenario; document for 8⁻ | h unavoidable by R; neither allows; both permitted and clear under {3, 7} and {3, 8}; under {3, 8⁻} UNDISCHARGEABLE(prevent(R, h)), a valid witness, document DILEMMA; the IDE proposes the guard |
| d | Law 3 (Astra P2) | `shield`, `retreat`, `nothing`; h_self (a harm to R) under `nothing` only; both protective; {1–6} + block; then {3, 6′} (`Every robot must prevent each harm that is a harm to that robot, if that harm is avoidable by that robot.`) | document for {1–6}; scenario for {3, 6′} | {1–6}: both protective actions required by rule 6, OVER-REQUIRED, document DILEMMA (the README's approximation made visible); {3, 6′}: discharged by either, R has a clear action: `shield`, `retreat` |
| e | Zeroth-law tradeoff | {3, 7, 10}; `nothing` leads to h_humanity; annotator fact `injures_human(act)` | document | rule 10 forbids `nothing`, rule 3 forbids `act`: NONE-PERMITTED, document DILEMMA; nothing in the source resolves it; any positive exception is a narrowing |
| f | C:187 risk to life | chooser `assistant`; `refuse`, `refer`, `answer`; obligation `respond_required(assistant)` with fulfilment `refers(a) ∨ gives_safety_information(a)`; rule F1 guarded by `life is at risk` | scenario; document with `Γ_ref := ∀x. ∃a. available(a, x) ∧ refers(a)` | model 1: clear = `refer`, `answer`; `refuse` not clear. Model 2 (only `refuse` available): UNDISCHARGEABLE(respond(A)), document DILEMMA for {F1}; with `Γ_ref` FOLLOWABLE, `conditional_on: Γ_ref` |
| g | C:335 counterfactual impact | rule G1 on `allows` a serious harm; `answer`, `refuse`; h under both (freely available information) versus under `answer` only | scenario | first: h unavoidable, both permitted and clear; second: `answer` forbidden, `refuse` clear; the *degree* of impact stays open |
| h | C:338 proximate cause; C:531 surgeon | `causes` declared; `operate` causes h_cut and avoids h_death, `wait` and `nothing` lead to h_death; {H1 on `causes`, 7′} | document | every alternative forbidden: NONE-PERMITTED, document DILEMMA; with 7 in place of 7′ only `wait` is clear, which the source rejects; "more harm" is a quantity comparison, open; a model with `causes` outside `leads_to` is `InvalidModel` |
| i | C:297 "could have done something differently" | assertive counterfactual about a past choice, no block | coverage | OPEN with reason `alternatives unstated`; never CHECKED |
| j | Rule 5 retained (Astra 3, Fable round 2) | {1–6} + block; two ordered, non-injuring alternatives beside the inaction | document | both permitted (rule 2) and both required (rule 5): OVER-REQUIRED, document DILEMMA. No document keeping rule 5 or 6 is document-wide FOLLOWABLE |
| k | U:5, U:7 preamble | "is the foundation of", "have resulted in" | coverage | W2 `causal` kind, LABELLED; outside this construct |
| l | validity; monotonicity | two inactions for R; two taken; an inaction available to no chooser; R with alternatives and no inaction; then add `pull₂` to model c; then a block naming `available`'s predicate as `leads_to` (l6) | model; environment for l6 | `InvalidModel("alternatives", …)` from the Lean route (Python only dispatches); h becomes avoidable and `nothing` allows it, the report listing `pull₂` under `alternatives_declared` (one model cannot say which alternative was added; `alternative_monotone`, under `WellFormedAlt`, is the general claim); l6 rejected `AlternativesSort: leads_to expects (action, harm)`, the double-role block that the theorem's well-formedness hypothesis excludes |
| m | ownership (Astra 1) | action `a` available to R1 and R2; then split into `a₁`, `a₂` | model | `InvalidModel("alternatives", "action a is available to two choosers: R1, R2")`; the split model accepted; `owner_unique` |
| n | stratification | exception guarded by "it is not the case that another action available to that robot may be performed" | document | `DependencyCycle: permitted` with hint `GuardOnOwnOutcome` offering rule 9's factual guard as an author-selected change, with the explanation of 1.5 |
| o | A/B distinguishing model (Astra 2) | `nothing` (inaction), `act`, `rescue`; h under `nothing` and `act`; {3, 7} versus {3, 8} | scenario | both followable at R; (A) clear = `act`, `rescue`; (B) clear = `rescue` only; recorded as the reading set's distinguishing model |
| p | negative outcomes (Astra 4) | scenario a with the cell (`pull`, h1) missing, `signed` then `complete_by: annotator` with the document stating `nothing leads to h1`; W2 document with and without the unit `It is not the case that pull leads to h1.`; under `complete_by` the same with the distinctness unit `It is not the case that pull is inaction.` (p4), without it (p5), and the scenario with a positive row `pull → h1` outside the document's cells (p6) | model; document | `signed`: `InvalidModel("alternatives", "outcome of pull for h1 unstated")`; `complete_by`: accepted, `assumed_harm_free: pull/h1 (annotator)`, results `conditional_on: alternatives:table_complete`, the hash covering the document's cell and no row; W2 under `signed`: `nothing allows h1 to happen` refuted until the negative unit is added, then proved with both cells in `counterfactual_leaves`; p4 proved `conditional_on` the premise; p5 refuted by the countermodel in which `pull` and `nothing` denote one element (constants may alias, implementation.md); p6 `InvalidModel("alternatives", "premise alternatives:table_complete fails")` |
| q | surface (Astra 6, Fable round 3) | each new wording of section 2; rule 9 with an unbound `that robot`; the short object form | surface | exactly one derivation per wording; the unbound form rejected with the `there is a robot such that` rewrite; paraphrases rendered with the two-action and unavoidable situations; the short form accepted only if it has one derivation |
| r | conservativity, identity (Fable 6) | environments with and without the block; a document over an environment with the block whose rules mention none of its predicates, with a conclusion over `permitted` and `required` (r4) and with a base premise and conclusion over `oldEnv` (r5) | identity; differential for r4 | every existing fixture, identity, certificate and hash unchanged; the block changes `environment_id`; r4's statuses and entailments identical to `ve_norms_route`'s as differential evidence (its conclusion is outside `alternatives_conservative`); r5 proved on both routes, each by a certificate bound to that route's own environment and regenerated premise list (the two are never compared), `alternatives_conservative` behind the agreement of the verdicts; delegated cases agree with `ve_norms_route` |
| s | status gate (Fable 2) | a document with conflict status UNKNOWN (budgets zero); one with CONFLICT | document | `not computed: conflict status UNKNOWN` / `CONFLICT`; computed only on CONFLICT-FREE |
| t | unmapped obligations (Fable round 3) | scenario a plus `report_required(robot)` with no fulfilment and `Every robot must file a report.` | scenario | R has a clear action: `pull`; status text lists `unmapped obligations: report_required (file a report)` |
| u | completeness cost (1.1) | `stand_down_required(robot)` with fulfilment `inaction(a)`; `Every robot must stand down, if that robot is recalled.` | scenario; document | every valid scenario with `recalled(R)` and at least one alternative of R: `R has a clear action: nothing`; with none: `no alternatives at R`; no certificate (a `BaseAdmissibleAlt` structure with a recalled chooser lacking an inaction refutes the claim) and no valid witness: UNKNOWN, the report naming the existence fact that is validated and not assumed |
| v | scenario binding (Astra 3) | the report of a replayed against a model without `pull`, and against a changed rule | binding | both rejected as stale; a scenario report never contains unqualified FOLLOWABLE |

Plus: norms.md 10.1 regressions unchanged on documents carrying the block; identity fixtures (the block changes
`environment_id`, existing environments unchanged); the 10.8 binding fixtures repeated for followability packages
and scenario reports; differential inlining and premise generation between Python's dispatch output and the Lean
route (Lean is the trust path).

## 6. Lean obligations (statement schemata; files `lean/VE/Alternatives/*`, `lean/ALTERNATIVES.md`)

Frozen `Norms/*`, `Route/*` and P0 files untouched; a new Lake target `ve_alternatives_route` wraps the norms
decoder as norms.md 11.4 prescribes (separate and validate the block, hash the original complete environment,
reject unknown fields, regenerate every formula). `A` is the decoded source (environment with the block, tree with
guards over the profile words, active base premises `Γ`); `inlineTree A` is the W1 `Doc` it elaborates to;
`BaseAdmissible`, `ConflictFree`, `DocumentExpansion`, `subst`, `backgroundValid` are W1's. Names avoid primes
(the audit's output regex). Two conventions (statement review): argument orders are fixed once (avoidable,
unavoidable: (harm, chooser); allows, prevents: (action, harm); clear: (chooser, action)), every context is the
argument list reversed and every `tupleVal` is in argument order; and no statement shares an element between
independently quantified structures: expansion-level claims are over `S` and `restrictAll (inlineTree A).T S`,
extensions are built on `S`'s carrier (`extendAvailable`), and the passage from a finite witness to an expansion is
the explicit hypothesis of `dilemma_expansion`. Full statements in `alternatives.md` 7.

```lean
def altPremises (A) : List VE.Formula                         -- own, one_taken, one_inaction, proximate, as declared
def BaseAdmissibleAlt (A) (B) : Prop := BaseAdmissible (inlineTree A) B ∧ Sat B (altPremises A)
def AltConflictFree (A) : Prop := ∀ B, BaseAdmissibleAlt A B → ConflictFree (inlineTree A) B
def ClearIn (A) (S) (r a) : Prop                              -- clear over S's actual relations (1.4), (chooser, action)
def FollowableIn (A) (S) : Prop := ∀ r typed, (∃ a, available a r) → ∃ a, ClearIn A S r a
def extendAvailable (A) (S) (more) : VE.Structure             -- S with `available` extended by `more`, same carrier
def ExistenceFacts (A) (M) (rows) : Prop                      -- rows typed, one per pair, positive rows = leads_to; E1–E3

theorem alternatives_wellFormed (A) : WellFormedAlt A = true → WellFormed (inlineTree A) = true
theorem owner_unique (A) (h : WellFormedAlt A = true) (B) (hB : BaseAdmissibleAlt A B) : available a r → available a r' → r = r'
theorem inline_faithful (A) (h) (φ) (hφ) (S) (hS : S.Admissible A.E) (ρ) (hρ) :
  (inline A φ).denote S ρ ↔ φ.denote (withDefinitions A S) ρ
theorem alternative_monotone (A) (hw : WellFormedAlt A = true) (S) (more)
    (hS' : Sat (extendAvailable A.alt S more) (altPremises A)) (r h a : S.Carrier) :   -- hw: role predicates distinct
  (avoidable S h r → avoidable (extendAvailable A.alt S more) h r) ∧ (allows S a h → allows … a h) ∧ (prevents S a h → prevents … a h)
theorem alt_conflict_free (A) (h) (certs) (hc : altConflictFreeCheck A certs = true) : AltConflictFree A
theorem clear_denote (A) (h) (S) (hS : DocumentExpansion (inlineTree A) (restrictAll (inlineTree A).T S) S)
    (hB : BaseAdmissibleAlt A (restrictAll (inlineTree A).T S)) (r a : S.Carrier) (typed) :
  (clearF A).denote (restrictAll (inlineTree A).T S) (tupleVal [r, a]) ↔ ClearIn A S r a
theorem followable_sound (A) (h) (hc : AltConflictFree A) (c)
    (ok : checkCertificate (envAt (inlineTree A) 0) (backgroundBaseAlt A ++ A.Γ) (allFollowable A) c = true) :
  ∀ B, BaseAdmissibleAlt A B → Sat B A.Γ → ∀ S, DocumentExpansion (inlineTree A) B S → FollowableIn A S
theorem dilemma_witness_sound (A) (h) (M) (valid : M.Valid (envAt (inlineTree A) 0))
    (hb : backgroundValidAlt A M = true) (hΓ : evalAll A.Γ M = true) (r) (typed)
    (hd : (notFollowableF A).eval M (tupleVal [r]) = true) :
  ¬ (∀ B, BaseAdmissibleAlt A B → Sat B A.Γ → (allFollowable A).denote B [])
theorem dilemma_expansion (A) (h) (S) (hS : DocumentExpansion (inlineTree A) (restrictAll (inlineTree A).T S) S)
    (hB : BaseAdmissibleAlt A (restrictAll (inlineTree A).T S)) (r : S.Carrier) (typed)
    (hd : (notFollowableF A).denote (restrictAll (inlineTree A).T S) (tupleVal [r])) : ¬ ∃ a, ClearIn A S r a
theorem validate_sound (A) (M) (rows) (hv : validateAlternatives A M rows = .ok ()) :
  M.Valid (envAt (inlineTree A) 0) ∧ backgroundValidAlt A M = true ∧ evalAll A.Γ M = true ∧
  BaseAdmissibleAlt A M.asStructure ∧ ExistenceFacts A M rows
theorem scenarioConflict_sound (A) (h) (M) (valid) (hb) (t vs) (hc : scenarioConflict A M = some (t, vs)) :
  ¬ ConflictFree (inlineTree A) M.asStructure ∧ ¬ AltConflictFree A
theorem alternatives_conservative (A) (h) (Γ φ) (hΓ : over oldEnv A) (hφ : likewise) :
  (∀ B, BaseAdmissibleAlt A B → Sat B Γ → φ.denote B []) ↔ (∀ B, BaseAdmissible (inlineTree A) B → Sat B Γ → φ.denote B [])
theorem alt_route_acceptance / alt_route_countermodel        -- W1's restated with BaseAdmissibleAlt and backgroundAlt
theorem alternatives_wire_followable_sound / alternatives_wire_dilemma_sound / alternatives_wire_conflict_sound /
        alternatives_wire_acceptance / Run.alternatives_wire_acceptance   -- raw JSON, as norms_wire_* (11.4);
        -- the dilemma wire theorem carries validateAlternatives src.A w.M w.rows = .ok () and the evaluated ¬followable°
```

Also executable guards: `validateAlternatives` agrees with the slot premises plus the rows, the existence facts and
outcome coverage; `alt-validate` evaluates the regenerated conflict formulas on the model before any per-chooser
result (`scenarioConflict_sound`); and the finite evaluation of `followable` agrees with its denotation (typed
`eval_iff_denote`). Nothing
is claimed about the diagnosis: Lean certifies `¬followable°` at the witness chooser; NONE-PERMITTED,
OVER-REQUIRED, UNDISCHARGEABLE and JOINTLY-UNDISCHARGEABLE are computed by the untrusted evaluator, and minimality
of the listed set is a report property. Proof plan: `inline_faithful` by the atom-substitution lemma (W3's
`faithful` is the model, not a dependency, so the W1×W3 gap is not on the path); `clear_denote` and
`followable_denote` from `subst_sound` and `prefix_satisfaction`; the two soundness theorems from those and
`conflictFree_expands_document`; `alternative_monotone` by unfolding the three bodies on `extendAvailable`, with
`available ≠ leads_to` from `WellFormedAlt` keeping the `leads_to` atoms untouched; `alternatives_conservative` by
reinterpreting the block's relations as empty; the wire theorems by W1's chain. Audit allowlist unchanged. Statement review questions (rule 10): is `clear` the
intended reading of "complies with the mapped obligations and the declared action constraints"; is certification
over the broader class, with the completeness cost of 1.1, acceptable; is existence-by-validity acceptable; is
`unavoidable`'s existence conjunct wanted; is the regenerated `alternatives:table_complete` premise the right form
of the completion assumption; is the diagnosis-as-report reading acceptable.

## 7. Work items

| # | Item | Owner, effort | Notes |
|---|---|---|---|
| 0 | Prerequisite: the Asimov use case merges via the train (`usecases/asimov-laws`) | in progress, in parallel | fixtures a–e, j build on it |
| 1 | `docs/spec/alternatives.md`: block, slot premises and `BaseAdmissibleAlt`, outcomes modes, definitions, followability and diagnoses, diagnostics, wordings, Lean statements, fixtures a–v with expectations separated from definitions | draft 1 written from revision 2; draft 2 applies the statement review's ten edits; draft 3 applies the four corrections of Astra's verification (2026-09-28) | **gate:** Astra + Fable statement review; each reviewer derives the expectation of every fixture from its rule set, premises and model before reading 8.2; the review returned FIX (ten edits, 9.1) and Astra's verification of draft 2 returned FAIL (four corrections, 9.2), both applied; the repeated gate covers the changed entries and their direct dependencies (`alternatives.md` 10.13), both reviewers checking the rewritten signatures themselves, before items 2 and 3 begin |
| 2 | Lean `lean/VE/Alternatives/{Decl,Inline,Background,Followable,Validate,Wire,Run}.lean`, section 6, executable `ve_alternatives_route`, `lean/ALTERNATIVES.md`; `alternatives_conservative`; the trust-cost line in `ROADMAP.md` | Lean, 5–7 days (Opus 5.5) | semantics owner under the migration rule (SEMANTICS-MIGRATION-PLAN 6): Lean-only, no Python semantics, `CheckerUnavailable` under `VE_AUTHORITY=python` |
| 3 | Python surface and adapter: `ve/surface/alternatives.py`, block **shape** validation in `ve/environment.py`, dispatch to the Lean executable (`alt-elaborate` output feeds proof search), coverage lines `alternatives_declared`, `counterfactual_leaves`, `assumed_harm_free`, `unmapped_obligations`, `dilemmas`; Rust untrusted evaluation; binding, unique-derivation and paraphrase fixtures (q) | Python, 3 days (Sol) | no Python mirror of validity or followability (Fable 5); validity and followability come from Lean |
| 4 | Asimov v2: harm sort, `leads_to` with signed cells, inaction rules as reading set {A, B} with model o, "injure" set {causes, allows}, Law 3 as a prevention duty, dilemma witnesses (b, e, j), README boundary rewritten, tests extended | 1–2 days (Sol) | the README's three UNFORMALISED items become checked in the declared model, DILEMMA, or open; every added rule and fact is an attributed narrowing |
| 5 | Pilot probes: C:187, C:221, C:297, C:335, C:338, C:531; U:5, U:7, U:73; reading sets with cited narrowings under the soft-norms counting protocol (end-to-end admission, split-only baseline, blind review) | pilot, 2 days | prediction: no change in the causation-primary count (the tagged C units u0010, u0011, u0019–u0021 are explanatory prose, co-blocked); any gain is measured, including zero |
| 6 | W8: `declare_alternatives`, `add_outcome_row` (signed), paraphrases with a two-action example and the dilemma explanation; fidelity gate first | later | not before item 4 passes |
| 7 | Stage 2 (traces, horizon, backward-prevention validity) and VEX bounds on counterfactual leaves; soft-norms × alternatives composition proof | not scheduled | triggers: a committed document that needs them (converged rule 3); the soft-norms composition proof for the profile combination |

Sequencing: 1 (this revision, no further plan round) → Astra + Fable statement review with independently derived
fixture expectations → 2 ∥ 3 → 4 → 5; 6 after 4; 0 in parallel throughout. Nothing waits on W6 or on the W1×W3
composition gap. Soft-norm combinations wait for the soft-norms composition proof; stage 2 and VEX stay unscheduled.

## 8. Risks

1. **Fake precision by table.** A Boolean `leads_to` stands in for graded causal belief. Mitigation: a support
   label on every cell, negative cells stated or covered by a named decider's completion assumption printed in the
   residual, the counterfactual decider in the legend, "in the declared model" in every verdict, and the refusal
   of `risks`, `could lead to`, `uplift` as wordings.
2. **Gaming the alternative list.** Omitting an alternative hides an `allows`; adding a fanciful one manufactures
   blame. Mitigation: `alternative_monotone` in the report, the list printed with its declarer, challenger
   extension; ownership stops one action from serving two choosers.
3. **DILEMMA read as a moral verdict.** Mitigation: fixed wording "no available action complies with the mapped
   obligations and the declared action constraints in this situation", with the author-selected rewrite of 1.5
   offered beside it and named as a change of meaning.
4. **English collisions.** "allows" is everyday permission language; "leads to" suggests tendency; "that robot"
   inside a rule on an action has no binder. Mitigation: the `to happen` tail, fixed paraphrases, rejected
   synonyms, the `there is a robot such that` binder, W7 unambiguity fixtures (q), W8 fidelity gate first.
5. **Fragment loss and rare certificates.** Quantified guards put every document using `allows` outside the
   small-model fragment, so FOLLOWABLE needs a tableau certificate and UNKNOWN will be common; and universal
   FOLLOWABLE is refuted by any unescaped prohibition on a free base predicate (1.4). Mitigation: honest UNKNOWN
   with budget, witness search bounded per chooser, search hints as for conflict packages, the escape pattern of
   b′ and author premises in `Γ_base` shown as `conditional_on`, and scenario reports that say what they are.
6. **Broader class.** Certificates quantify over structures no valid scenario matches (1.1), so documents relying
   on an existence fact (fixture u) are UNKNOWN rather than FOLLOWABLE. Mitigation: the cost is named in the
   report; an existence premise can be added in a later profile version without changing accepted scenarios.
7. **Scope creep and modelling misfit.** General causation, temporal logic, games; joint action, repeated and
   continuous choice. Mitigation: 1.6 and section 3 name each boundary and trigger; separate choosers for separate
   decisions.
8. **No measurable gain on C.** The causation-tagged units are mostly explanatory prose; the norm clauses this
   construct serves are `norms`-primary. The plan is still worth its spec (the Asimov gap and the constitution's
   harm-avoidance section need it), and item 5 reports what it measures.

## 9. Debate response table (item → change)

Sources: `manage-agents/debates/design-causation/astra.md` (rounds 1–3) and `fable.md` (rounds 1–3); CONVERGED
after round 3 on REVISE with the union of both lists.

| Item | Change in this revision | Where |
|---|---|---|
| Astra 1 — action ownership | premise `own`; each action belongs to exactly one chooser; finite validation; `owner_unique`; the `∃r` in `allows`/`prevents` single-valued; shared-action fixture m | 1.1, 1.3, 5, 6 |
| Astra 2 / Fable 1 — A/B differ outside dilemmas; what forbids `pull` | "differing only in dilemmas" withdrawn; distinguishing model o; fixture b split into A₀, A₁ (annotator fact), A₂ (rule 7′) and B, each attributed; the (B) carve-out 8c | 1.3, 5 (b, b′, o) |
| Astra 3 / Fable round 2 — scenario versus document; Rule 5 | verdict-scope table; scenario reports bound to the model and never FOLLOWABLE; b′'s exact rule set {3, 7, 9} with 9 over 3 and 7, no rule on `required`; fixture j (Rule 5 → OVER-REQUIRED); every fixture row states rule set, premises, model, scope | 1.4, 5, 8 |
| Astra 4 — negative outcomes | mandatory `outcomes: signed | complete_by`; signed rows on scenarios, negative-cell units in documents, the regenerated `alternatives:table_complete` premise; `assumed_harm_free` and `counterfactual_leaves` in the residual; fixture p | 1.2, 2, 3, 5 |
| Astra 5 / Fable round 2 — proof contract | `BaseAdmissibleAlt` in `hc`, both soundness theorems, conflict, witness and wire statements; the broader-class sentence with its named completeness cost; 7.1(3) not cited as justification; soft-norm combination gated on the composition proof (`UnsupportedProfile` meanwhile) | 1.1, 4, 6, 7 |
| Astra 6 / Fable 4 — English matches the checked claim | "the mapped obligations and declared action constraints"; unmapped obligations named (fixture t); JOINTLY-UNDISCHARGEABLE; `GuardOnOwnOutcome` as an author-selected change with explanation; `there is a robot such that` binder; binding, unique-derivation and paraphrase fixtures (q) before surface acceptance | 1.4, 1.5, 2, 5 |
| Fable 2 — status only on CONFLICT-FREE | `not computed: conflict status <CONFLICT | UNKNOWN>`; fixture s | 1.4, 5 |
| Fable 3 — ownership premise | see Astra 1 | 1.1 |
| Fable 5 — Lean-only | item 3 has no Python mirror; fixture l's diagnostics from the Lean route; Python: block shape, dispatch, surface, proof search; Rust untrusted | 0, 4, 5, 7 |
| Fable 6 — conservativity and trust cost | `alternatives_conservative` plus "new route, by construction"; ROADMAP trust-cost line in item 2; fixture r | 3, 4, 6, 7 |
| Fable round 3 — fixture format, model binding, unmapped list, surface fixtures | as Astra 3 and 6 above; fixtures q, t, v | 1.4, 5 |
| Fable round 3 precision point (diagnosis versus verdict; fixture c keeps UNDISCHARGEABLE) | recorded as a resolved choice for the statement review, not as part of the converged list: Lean certifies `¬followable°`, the classification is rendered, minimality a report property | 1.4, 6; `alternatives.md` 11 |
| Process — item-1 review as the gate; independent expectations | item 1 written from this revision; expectations separated from fixture definitions (`alternatives.md` 8.1/8.2); item 0 in parallel; stage 2 and VEX unscheduled | 5, 7 |

### 9.1 Statement review of item 1 (`manage-agents/debates/causation-spec/`, FIX, CONVERGED after round 3)

The joint position is Fable's round-3 list of ten edits, the union of Astra 1–7 and Fable 1–6; `alternatives.md` 12
has the full table. The plan entries changed by it:

| Item | Change in this draft | Where |
|---|---|---|
| Astra 1 = Fable 2 — rule subsets | `over` entries naming absent rules dropped | 5 |
| Astra 1 (round 2) — b′(A⁻) | CONFLICT, followability not computed (was DILEMMA) | 5 (b′) |
| Astra 2 — p4 aliasing | distinctness unit; aliased countermodel p5 | 5 (p) |
| Astra 3 — p2, document versus row completion | p2's document states its cell; positive rows within document cells (p6); rows change neither premise nor hash | 1.2, 3, 5 (p) |
| Fable 3 = Astra 4 — argument orders | fixed once; `clear(r, a)` | 1.4, 6 |
| Astra 4 / Fable round 2 — Lean statements | `S.Admissible A.E`, `WellFormedAlt` on `owner_unique`, carrier transport, `extendAvailable`, `dilemma_expansion` | 6 |
| Astra 5 — validation evidence | `ExistenceFacts A M rows`; validation in the dilemma wire conclusion | 3, 6 |
| Astra 6 / Fable round 2 — namespaces | `AlternativesReserved`; no fulfilment atoms | 1.1 |
| Astra 7 = Fable 4 — scenario gating | conflict formulas first; document DILEMMA from a scenario only on CONFLICT-FREE | 1.4, 6 |
| Astra 7 / Fable round 3 — empty choices | `no alternatives`; legend and fixture u qualified | 1.1, 1.4, 2, 5 (u) |
| Fable 5 — r4 | differential evidence; r5 | 3, 5 (r) |
| Fable 6 — wording | short object form marked; b(A₁) witness wording; l5 | 1.5, 5 (b, b′, l) |

### 9.2 Verification of draft 2 (`manage-agents/causation-verify1b-astra.final.md`, FAIL, four corrections)

Astra's read-only verification of `alternatives.md` draft 2 and this plan's draft 3 found all ten statement-review
fixes represented, raised no objection to the design questions of section 6, and required four corrections, applied
in `alternatives.md` draft 3 (its section 13) and here. No design changed; the new fixtures are b′(A⁻5) and l6.

| Item | Change in this draft | Where |
|---|---|---|
| Astra V1 — `alternative_monotone` | `hw : WellFormedAlt A = true` in the schema: the role predicates are pairwise distinct, so extending `available` leaves `leads_to` unchanged (otherwise one `p` in both roles loses avoidability while keeping ownership); the proof plan names the dependency; fixture l gains the rejected double-role block l6 | 3 (5), 5 (l), 6 |
| Astra V2 — r5 | a separately bound certificate per route proving the same conclusion, not "the same certificate": the routes bind different environments and regenerated premise lists, and conservativity relates verdicts, not certificates | 5 (r) |
| Astra V3 — b′ plus rule 5 | DILEMMA for (A) and (B) plus rule 5 only; A⁻ plus rule 5 keeps its permission conflict, so followability stays `not computed`; `alternatives.md` fixture b′ gains (A⁻5) | 5 (b′) |
| Astra V4 — inlining prose | `alternatives.md` 4.3 qualified by admissibility (`S.Admissible A.E`), matching `inline_faithful`; section 3 item 6 says the same | 3 (6); `alternatives.md` 4.3 |

## Summary

Causation enters VE as *preventable harm over explicit alternatives*: a profile `alternatives@0` that declares,
per chooser, a finite list of alternatives each belonging to exactly one chooser (optionally including inaction),
a declared outcome table `leads_to(action, harm)` whose negative cells are stated or covered by a named decider's
completion assumption, and three defined words, avoidable, allows and prevents, inlined into ordinary W1 guards.
"Through inaction allow harm" becomes a per-action prohibition or a per-harm duty of prevention, a reading set
with a recorded distinguishing model, both checked by unchanged `norms@0` machinery over `Background_base` plus
four universal slot premises. One new check, followability, computed only on CONFLICT-FREE documents, reports
FOLLOWABLE (a certificate over `BaseAdmissibleAlt`, a class broader than accepted scenarios, with its cost named),
DILEMMA (a certified witness with a rendered diagnosis: NONE-PERMITTED, OVER-REQUIRED, UNDISCHARGEABLE or
JOINTLY-UNDISCHARGEABLE) or UNKNOWN; scenario results are bound to their model and never called FOLLOWABLE. The
checked claim is about the mapped obligations and the declared action constraints, and priority across
obligations is something an author writes over facts, as a stated change of meaning, rather than something the
checker invents. Certified: structure over the declared model. Open, listed as residual: the table and its
negative cells, counterfactual truth, completeness of alternatives, proximate causation, degrees, consent and
responsibility. Time and multi-step strategies are a stated stage 2; Lean owns the semantics; no coverage gain is
predicted.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-27 | Draft 1 | Initial plan. Plan only: no code, Lean or frozen contract changed. |
| 2026-09-28 | Draft 2 | Applied exactly the converged REVISE list of `manage-agents/debates/design-causation/` (Fable round-2 joint position incorporating Astra's six round-1 changes and five round-2 requirements, plus Fable's round-3 fixture-format items): action ownership premise and validation; A/B distinguishing model, the withdrawn "differing only in dilemmas", the attributed rules and facts that forbid a non-inaction alternative, the (B) carve-out; scenario/document verdict scope with model binding and b′'s exact rule set, Rule 5 fixture; accountable negative outcomes (`outcomes` field, signed cells, `table_complete` premise, residual lines); `BaseAdmissibleAlt` throughout, universal premises with finite-only existence validation and the named completeness cost, soft-norm combination gated; "mapped obligations and declared action constraints", unmapped obligations named, JOINTLY-UNDISCHARGEABLE, `GuardOnOwnOutcome` as an author-selected change, the `there is a robot such that` binder; status computed only on CONFLICT-FREE; Lean-only semantics with Rust untrusted; conservativity theorem and ROADMAP trust-cost line; fixtures a–v each with rule set, premises, model and scope, expectations separated in the spec; section 9 response table. The diagnosis-versus-verdict precision point is recorded for the statement review. Plan only. |
| 2026-09-28 | Draft 3 | Synchronized with `alternatives.md` draft 2 (the converged statement review of `manage-agents/debates/causation-spec/`, FIX, ten edits; 9.1): rule subsets drop `over` entries naming absent rules; b′(A⁻) is CONFLICT with followability not computed; p2's document states its positive cell, positive rows within document cells (p6), p4's distinctness unit and the aliased countermodel p5; `clear(r, a)` and the argument-order convention; the Lean schemata of section 6 with `S.Admissible A.E`, `WellFormedAlt` on `owner_unique`, explicit carrier transport, `extendAvailable`, `dilemma_expansion`, `ExistenceFacts A M rows`, `scenarioConflict_sound` and validation in the dilemma wire conclusion; `AlternativesReserved` and no fulfilment atoms; the scenario conflict gate and the `no alternatives` branch; legend and fixture u qualified; r4 differential with r5; the marked short object form. Item 1's gate is repeated on the changed entries. Plan only. |
| 2026-09-28 | Draft 4 | Synchronized with `alternatives.md` draft 3 (Astra's verification of draft 2, `manage-agents/causation-verify1b-astra.final.md`, FAIL, four corrections; 9.2): `alternative_monotone` takes `WellFormedAlt A = true` (role predicates pairwise distinct) and fixture l gains l6; r5 requires a separately bound certificate per route, not "the same certificate"; b′ plus rule 5 is DILEMMA for (A) and (B) only, A⁻ plus rule 5 stays CONFLICT with followability not computed; section 3 item 6 qualifies inlining by admissibility. Plan only. |
