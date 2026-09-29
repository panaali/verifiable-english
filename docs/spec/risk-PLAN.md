# Risk: possible consequences, likelihood and severity over explicit alternatives: plan (`risk@0`)

> Status: planning draft 1 (2026-09-29). Design plan only: no code, Lean, frozen contract or existing identity is
> changed, and no coverage gain is predicted. Inputs: [norms.md](norms.md) (W1, cited `norms.md n`),
> [soft-norms.md](soft-norms.md), [alternatives.md](alternatives.md) and [causation-PLAN.md](causation-PLAN.md)
> (`alternatives@0`, cited `alt n`), [units-schema.md](units-schema.md) (W6, cited `W6 n`), [document.md](document.md)
> (W2), [VISION.md](../../VISION.md) (converged rule cited `CR n`), the evidence-layer design
> ([design/evidence-layer-design.md](../../design/evidence-layer-design.md), cited `EL n`), the Asimov use case
> ([usecases/asimov-laws/README.md](../../usecases/asimov-laws/README.md), its OPEN list) and the ARCH-ROADMAP P1
> items "unspecified default" and "limits contract" (`manage-agents/ARCH-ROADMAP.md`). Theorem statements are
> obligations, not proofs. Every open question is marked **OPEN** and collected in section 13. The gate before any
> specification work is an Astra + Fable review of this plan (PLAN-EXPAND2 rule 10).

## 0. Problem and stance

VE states rules and checks what happened. Many rules are about what *might* happen: an action may lead to a crash, an
injury or a death, with some likelihood and some severity. An AI agent about to run a program that might exhaust
memory and crash a server has to decide whether to run it, run it with a memory limit, ask the user or not run it.
Asimov's First Law weighs harms against one another, and the use case's README leaves this OPEN ("proportionality
and tradeoffs among different harms", "uncertain outcomes"). `alternatives@0` gives the structure (choosers,
explicit alternatives, `leads_to`, `allows`, `prevents`, followability) but its outcome table is Boolean and
certain, and it rejects `could lead to`, `risks` and degrees as wordings (alt 2.2, 4.10).

Stance. The checker **never estimates**. It checks decisions **relative to declared estimates**, each a labelled
assumption with provenance, and it computes only exact consequences of them. The design has two layers:

1. **The estimate layer** (new, per decision): quantities with interval estimates or exact settings, conditions
   linking quantities to outcomes, stated outcome cells, and later likelihood bands, chances and costs. Lean
   **regenerates** from it a finite Boolean table per decision: which harms each alternative *might* lead to, which it
   *leads to* (in every case the estimates allow), and the threshold facts the rules mention. The arithmetic is ground
   and linear over integers (W6 grids), so it is decidable by evaluation and proved exact once.
2. **The rule layer** (unchanged machinery): policies are W1 rules over `alternatives@0`, whose guards mention the
   regenerated facts as ordinary base predicates (details below). Conflict, followability and scenario evaluation
   are `alternatives@0`'s, with a few universal slot premises added.

The rule layer's guards use:

- one new base predicate, `might_lead_to`, which is regenerated on decisions and never supplied;
- its negation, worded `cannot lead to`;
- two defined words with fixed bodies, inlined as alt 4.3 does: `is <class> or worse` and `has a less severe worst
  case than`.

Probability never enters a formula (PLAN-EXPAND2 lists "probability inside formulas" as research). It enters as
data attached to a cell and leaves as a Boolean fact with a certificate of how it was computed. This follows CR 1
("elaborate by default") and CR 8 (weighing, empirical truth and causal assumptions are outside certification; their
formalised conditional consequences may be checked).

## 1. Invariants (what the design never does)

1. **No estimate is produced by VE.** There are no default chances, bands, severities, costs, priors or intervals.
   VE does not interpolate, does not infer chances from frequencies or quantities, and does not multiply along chains.
   It never merges two estimates of one quantity unless the policy states how (5.3).
2. **Every result is conditional** on named estimate, condition and statement ids (`conditional_on`). Every verdict
   says "given estimates E1, E2 …", as `alternatives@0` verdicts say "in the declared model".
3. **One reading per sentence.** Each new wording has one reading and a paraphrase a zero-training reader can check
   against an example. Wordings that invite a second reading are rejected with rewrites (2.1).
4. **No hindsight.** A decision's verdict depends only on what was recorded before it. Outcomes are reported
   separately and never change the verdict (section 6).
5. **No invented content.** A weighing rule, severity order or cost table that the source does not state is an
   attributed narrowing (VISION.md 3) or an author's policy choice, shown as such.
6. **Honest UNKNOWN and honest gaps.** Unexamined cells, unranked severities, missing chances and default-decided
   alternatives are listed, never silently resolved.
7. **Lean owns the semantics** (SEMANTICS-MIGRATION-PLAN 6, as for `alternatives@0`). Python checks shape, surface
   and dispatch. Rust evaluates untrusted for differential tests.

## 2. Possible consequences (question 1)

### 2.1 Wordings

| Wording | The one reading (the IDE's paraphrase) | Formal |
|---|---|---|
| `<action> might lead to <harm>` | The declared estimates, conditions and statements do not rule the harm out if the action is taken. | `might(a, h)` |
| `<action> cannot lead to <harm>` | They rule it out: it happens in no case they allow. | `¬might(a, h)` |
| `<action> leads to <harm>` | The harm happens in every case they allow (`alternatives@0`'s word; not "tends to"). | `leads_to(a, h)` |
| `<action> might not lead to <harm>` | Some case they allow avoids the harm. | `¬leads_to(a, h)` |
| `<action> leads to <harm> if <condition>` | Sufficient condition, a model assumption of its author. | 2.2 `S` |
| `<action> cannot lead to <harm> unless <condition>` | Necessary condition. | 2.2 `N` |
| `<action> leads to <harm> exactly when <condition>` | Both. | `S = N` |
| `<harm> is <class>` / `<harm> is <class> or worse` | Severity (4.1). | `class_of`, `at_least` |
| `<a′> has a less severe worst case than <a>` | `<a>` might lead to a harm more severe than every harm `<a′>` might lead to. | 4.2 |

Conditions are W6 comparisons (`is greater than`, `is less than`, `is at least`, `is at most`, `equals`) between
same-tag linear expressions over declared quantities and literals, joined by `both … and`, `either … or` and `it is
not the case that` (W6 4, docs/english-surface.md).

Rejected, with rewrites:

- **`may lead to`.** W1 reserves `may` for permission, and "May never means might" (norms.md 2.1). The rewrite is
  `might lead to`.
- **`does not lead to`.** Under `risk@0` it has two readings: "cannot" or "might not". The rewrite offers both,
  and the negative cell of `alternatives@0` (`It is not the case that … leads to …`) is paraphrased as `might not
  lead to`.
- **`could lead to`, `risks`, `is likely to lead to`.** These stay rejected as in alt 2.2 until stage B (3.2)
  gives likelihood words their declared ranges. The rewrite is `might lead to`.
- **`is safer than`.** It invites a probability-weighted reading. The rewrite is `has a less severe worst case than`.
- **`Every action … cannot lead to …`.** This has a scope ambiguity ("not every" versus "every … not"), as with
  object-position `every` under `must not` in norms.md 2.1. The rewrite is one sentence per action, or `It is not
  the case that some action available to <chooser> might lead to <harm>.`

**OPEN (Q-wording):** whether zero-training readers take `cannot lead to` deontically, and whether `leads to`
should render as `certainly leads to` under `risk@0`. This is settled by the W8 fidelity gate, not by this plan.

### 2.2 Semantics: possibility is consistency with what is declared

A **decision record** (section 5) declares quantities. Each is an *estimate*, an inclusive interval `[lo, hi]` on its
unit's grid (a point estimate is `lo = hi`, flagged in 7.3), or a *setting*, an exact value chosen as part of an
alternative (the memory limit). A **case** is one value per quantity within its estimate. The **box** is the set of
cases; it is nonempty because validation requires `lo ≤ hi`.

For each cell `(a, h)` the record gives at most one sufficient condition `S` and at most one necessary condition
`N`, each a condition over quantities. A stated `leads to` is `S = ⊤`, a stated `cannot` is `N = ⊥`, and a stated
`might` adds no constraint but asserts that the cell is not ruled out. An unaddressed cell is completed by 2.4.

```text
leads_to(a, h)  :=  ∀v ∈ box. S(v)          the harm follows in every case
ruled_out(a, h) :=  ∀v ∈ box. ¬N(v)         the harm is excluded in every case
might(a, h)     :=  ¬ruled_out(a, h)  =  ∃v ∈ box. N(v)
```

Validation requires `S → N` in every case (`SufficientOutsideNecessary: <a>/<h>`, with the offending case), so every
case gives the harm a consistent status: forced, excluded or open. Then `leads_to → might` (theorem
`certain_within_possible`). A stated `might` on a ruled-out cell, or a stated `cannot` on a certain cell, is
`RiskInconsistent: <a>/<h>`, with the case and the two sources.

This is VE's existing distinction between entailment and consistency. `leads_to` means the declarations entail the
harm, `cannot` means they entail its absence, and `might` means its occurrence is consistent with them. Every
`might` therefore has a **witness case** (e.g. "peak memory 12 GB, free memory 8 GB") checkable by evaluation, and
every `cannot` has an exactness proof (2.3). Cells are **marginal**: `might` for two harms does not claim that both
can happen in one case. Joint possibility is not claimed (**OPEN (Q-joint)**).

### 2.3 Deriving cells from quantities (the separable fragment)

Put each comparison in normal form `Σ cᵢ·qᵢ + k ⋈ 0`, with coefficients collected per quantity and `⋈ ∈ {<, ≤, =}`
(negation flips the comparison), and push negations to the comparisons. Over an integer box, the maximum of
`Σ cᵢ·qᵢ` is `Σ (cᵢ ≥ 0 ? cᵢ·hiᵢ : cᵢ·loᵢ)` and the minimum is symmetric. So one comparison is decided exactly by
endpoint arithmetic.

A condition is **separable** when no estimated (non-point) quantity occurs in two of its comparisons. Settings and
literals may repeat, because a point has no freedom. On separable conditions, `∃` distributes over `and` and `∀`
distributes over `or`, so possibility and certainty are computed by endpoint arithmetic over the condition tree.
Lean proves `possibleE_iff` and `certainE_iff` (8.3) once. An `equals` comparison on estimated quantities requires
coefficients ±1, because only then are the values contiguous (`RiskEqualityCoefficient` otherwise). The `S → N`
check evaluates `S ∧ ¬N`, which must itself be separable unless `S = N`.

Stage A rejects non-separable conditions (`RiskConditionShared: <quantity>`) with two rewrites: split the condition
into cells, or declare the quantities separately. Deciding them needs a satisfiability witness for `might` and an
`order@0` certificate for `cannot`. That is planned as item 7 (section 12); stage A has no UNKNOWN cells.

Worked derivation. "The peak memory of the job is from 6 GB through 12 GB" (E1) and "the free memory of the server
during the job is from 8 GB through 10 GB" (E2). The necessary condition "Running the job cannot lead to a server
outage unless the peak memory of the job is greater than the free memory of the server" gives `might`, because
`hi(E1) = 12 > lo(E2) = 8`; the witness is the case (12, 8). A point estimate of 12 GB against free memory of exactly
8 GB would make the sufficient condition "running the job leads to memory exhaustion if …" certain. The report then
says the certainty rests on two point estimates (7.3).

**Policy-level conditions** ("every job run without a limit …") would quantify over quantity-valued attributes of
actions. That is the `order@0` × n-ary combination W6 leaves gated (W6 1). Stage A conditions are therefore ground,
written per decision over named quantities (W6 4: a quantity name is a declared constant). **OPEN (Q-templates).**

### 2.4 Unexamined cells

The mandatory `unexamined` field says how cells no condition or statement addresses are read, as alt 1.4 does for
`leads_to`:

- **`possible`** (precautionary): unexamined cells are `might`, listed under `unexamined_possible`.
- **`{"ruled_out_by": "<decider>"}`**: unexamined cells are ruled out on that decider's authority, listed under
  `assumed_ruled_out`.
- **`always_possible: [<classes>]`**: listed severity classes stay precautionary under either mode.

The OOM policy (section 9) makes serious and severe harms always possible, so the agent must address them for every
alternative, and lets the agent rule out minor ones. This stops an agent hiding a serious risk by omission while
keeping a decision record short.

### 2.5 Relation to `alternatives@0`

On a decision, the regeneration yields a complete signed `leads_to` table. Each row's support is `calculation` (from
a condition) or the stated cell's support, so existence fact E3 (alt 4.2) holds by construction under
`outcomes: signed`. `avoidable`, `allows` and `prevents` keep their definitions (alt 4.3) over certain outcomes. The
new base predicate `might_lead_to` gets the slot premise `certain_possible: ∀a h. leads_to(a, h) → might_lead_to(a,
h)`. Supplied scenarios never supply `might_lead_to` or `leads_to` rows under `risk@0`: both are computed, as
regulated tables are (alt 3.3). The policy document carries no estimates; decisions are scenarios bound to their
record id.

## 3. Likelihood, in stages (question 2)

### 3.1 Stage A: possibility only (build first)

`might`, `cannot`, `leads to`, derived by 2.3. This is enough for:

- hard bans on possible severe harms;
- worst-case (precautionary) choice among alternatives;
- severity thresholds with confirmation;
- the OOM case and Asimov case A1.

It asks nothing of estimators beyond ranges they can defend, so it adds no false precision.

### 3.2 Stage B: named likelihood bands (on a trigger)

The policy declares a chance unit and bands, each an inclusive range. For example: "In this policy, a chance is
rare when it is from 0% through 1%. A chance is unlikely when it is from 1% through 10%." Bands are ordered, lie in
`[0%, 100%]`, and neighbours may share an endpoint (`BandRange`, `BandOrder` otherwise); gaps are warned. A band word
means exactly its declared range, and the legend shows the range every time the word appears: VE's "unlikely" is not
English "unlikely".

A chance estimate for a cell states a band or an explicit interval, with provenance: "The chance that running the job
leads to a server outage is unlikely." Guards compare chances with bands or literals under the same rule as quantity
comparisons: an unqualified comparison holds for every value in the estimate, and `might be` holds for some.

- `the chance that <a> leads to <h> is at most rare` means `hi ≤ hi(rare)`.
- `… might be more than 1%` means `hi > 1%`.

Lean regenerates one base predicate per distinct (comparison, threshold) the rules use, named `risk__chance__…` by
the scheme of soft-norms 1.3. It adds the ground monotonicity premises between them (more than 10% implies more
than 1%).

Consistency with 2.2:

- A ruled-out cell's chance interval must contain 0% and is narrowed to 0%.
- A certain cell's interval must contain 100% and is narrowed to 100%.
- Otherwise the cell is `ChanceAgainstPossibility`.
- A `might` cell with no chance estimate has the vacuous chance 0%–100%, listed under `no_chance_estimate`.

Narrowing and cross-cell coherence (for example `P(outage) ≤ P(exhaustion)` when an outage needs exhaustion) reuse
the interval-coherence LP of EL 2.3 and are entered only through its certificates.

**Trigger:** a committed policy that uses graded likelihood words with its own ranges (a risk matrix).

### 3.3 Stage C: numeric chances and expected cost (on a trigger)

Costs are **normative** and chances are **empirical**, and the design keeps them apart.

- **Costs.** The policy declares one exact cost per severity class, in a declared unit (points or a currency), with
  its author. Costs must increase along the severity order (`CostAgainstSeverity`).
- **Chances.** Chances are interval estimates per cell.
- **Expected cost.** `EC(a) = Σ_h cost(class(h)) · chance(a, h)` is linear in the chance variables, because costs
  are exact. Lean computes it exactly on the product grid of the cost and chance scales.
- **Comparison.** "`<a′>` has a lower expected cost than `<a>`" holds when `EC(a′) < EC(a)` for **every**
  combination of values within the chance estimates. Coefficients are collected per estimate, so a chance shared by
  two alternatives cancels exactly (the maximum of a linear form over a box, 2.3).
- **Threshold.** "The expected cost of `<a>` is at most 5 points" is decided the same way.

A policy may confine expected-cost rules to alternatives whose worst case is at most some class. This is a rule
pattern, not a primitive: it forbids trading a severe harm for convenience.

**Trigger:** a committed document that states numeric tradeoffs (an error budget, an expected-loss limit). Asimov
case A2 (10.2) illustrates stage C but is a translator's narrowing, not a trigger.

### 3.4 Recommendation and guards against false precision

- **Build.** Build A now. Build B and C only on their triggers (CR 3: a committed document that needs them).
- **Point estimates are flagged**, not forbidden. A conclusion that depends on one says so (7.3).
- **Unknown is vacuous.** A missing chance is 0%–100%, not a guess.
- **No chains.** VE never multiplies along a chain. A chain needs its conditional chances, both `P(H | E)` and
  `P(H | ¬E)`, declared by an estimator. **OPEN (Q-chains)**
- **Every threshold result carries a margin** (7.4), so a decision that turns on a narrow margin is visible.
- **Chance units.** W6 admits at most one `percent` display tag per environment (W6 2.1), so a policy that needs both
  a chance tag and another percentage cannot declare both. The contract change request is a display kind `chance`.
  **OPEN (Q-chance-tag)**
- **Limits of the probabilities.** A chance is an assessment by a named estimator. VE reports whether it is
  coherent with the other chances (EL 2.3) but never whether it is correct (W6 5: hypothetical ratios are not
  measured probabilities).

## 4. Severity and decision rules (question 3)

### 4.1 Severity classes and their order

The `risk` block declares:

- **A severity sort** whose domain is exactly its declared class constants. The generated domain-closure premise is
  `∀s. s = c₁ ∨ … ∨ s = cₙ`, and at most 16 classes are allowed.
- **Order edges.** "Serious harms are more severe than minor harms." These are closed transitively into a strict
  partial order. A cycle is `DependencyCycle: <classes>` via `VE.Route.dependencyOrder`, as soft-norm ranks are
  checked (soft-norms 1.2).
- **Declared unranked pairs.** "Privacy harms and property damage are not ranked." Undeclared incomparable pairs are
  listed under `unranked_severities`.
- **Harm constants of the harm sort, each with exactly one class**, set by a named decider ("Severity is set by the
  platform team"). Validation rejects a harm with no class, or with two (`HarmUnclassified`, `HarmTwoClasses`).

Harms are **policy constants** and decision records choose among them (`UnknownHarm` otherwise). An agent therefore
cannot grade the severity of its own harms. **OPEN (Q-new-harms):** how a decision reports a harm kind the policy did
not list.

The legend reads, for example:

```text
Severity, from most to least severe: severe, serious, minor.
```

### 4.2 The worst-case word

```text
lessWorst(a′, a) := ∃h. might(a, h) ∧ ∀h′. might(a′, h′) → moreSevere(class(h), class(h′))
```

In English: "`a′` has a less severe worst case than `a`" when `a` might lead to a harm more severe than every harm
`a′` might lead to. An alternative that might lead to no harm has a less severe worst case than any alternative that
might lead to some harm.

The relation is irreflexive and transitive (`lessWorst_strict`), and it depends only on the set of classes each
alternative might reach. With an unranked pair it can hold in neither direction; the report then names the pair as
the reason. It ignores certainty and counts: a certain death and a possible death tie.

Rejected alternatives:

- ranking certain harms above possible harms of the same class (lexicographic);
- set inclusion ("every harm `a′` might lead to, `a` might lead to"), which is already expressible in guards and needs
  no word.

**OPEN (Q-worst-case):** which relation a given source means. In translation this is a reading set.

### 4.3 Rule patterns (ordinary W1 rules; no new rule form)

| Pattern | Canonical VE rule (policy text) | Note |
|---|---|---|
| P1 hard ban | `Every action must not be performed, if there is a harm such that both that harm is severe and that action might lead to that harm.` | No carve-out; the paraphrase says "no confirmation lifts this rule" |
| P2 precaution | `Every action must not be performed, if there is an agent such that both that action is available to that agent and another action available to that agent has a less severe worst case than that action[, unless …].` | Guard over facts, not permissions, so no `GuardOnOwnOutcome` (alt 4.8) |
| P3 tiered precaution | P2 with `… another action available to that agent is acceptable and has a less severe worst case …`, where `acceptable` is a plain regulated predicate decided by lower rules | Stratified, like Asimov's `has_lawful_option` (rules.ve rule 7) |
| P4 confirmation threshold | `…, unless the user has confirmed that action.` on P2, with `confirmed(action)` a base predicate recorded from the user's reply | Serious harms can be confirmed, severe harms cannot (P1 has no carve-out) |
| P5 benefit side | `Every action must not be performed, if that action allows task abandonment to happen.` | `alternatives@0`'s `allows` over certain outcomes |
| P6 likelihood threshold (B) | `…, if the chance that that action leads to a server outage might be more than 1%, unless …` | Regenerated threshold facts |
| P7 expected cost (C) | `… another action available to that agent has a lower expected cost than that action.` | Only on the stage C trigger |

**Theorem `precaution_has_maximal`** (8.3). Under the domain-closure premise, every chooser with an alternative has
one that no other alternative beats. The reason is that `lessWorst` depends only on a subset of finitely many
classes. So P2 alone never creates a dilemma, even over infinite structures, and document-wide FOLLOWABLE
certificates for P2-only policies are expected. With P1, P3 or P5 dilemmas are real, and the followability check of
alt 4.6 reports them (NONE-PERMITTED and so on).

**Confirmation.** Confirmation is not a soft-norm switch: `alternatives@0` with `soft-norms@0` is gated (alt 3.1).
Whose harms a user may confirm (harms borne only by the user versus by third parties) needs a `borne_by(harm,
party)` classification. **OPEN (Q-consent)**

### 4.4 Relation to "preference between actions" (the Asimov OPEN limit)

The README's OPEN items (proportionality between harms; preferring the alternative that meets fewer threats) ask for
a ranking of alternatives. alt 4.8 fixes that priority across actions is never a checker primitive. This plan agrees:

- **Preference is derived.** A preference between actions is derived from declared severity (stage A), bands (B) or
  costs (C) through fixed profile words with fixed bodies. It is then written into W1 guards over facts.
- **Other rankings are explicit choices.** Any other ranking is an attributed author or translator choice:
  - "fewer threats" is an expected-cost rule with equal costs, or a set-inclusion guard;
  - "a certain harm is worse than a possible one" is a W1 precedence choice (10.1).
- **What a preference is not.** Soft-norm ranks remain about rules on one act (soft-norms 4.5), not about actions.
  A named relation `preferred_to(a, b)` stays plain vocabulary with no properties (W6 4, declared ordinal relation).

## 5. Where estimates come from (question 4)

### 5.1 The estimate record

Every estimate is a row of the decision record with these fields. Unknown fields are rejected, and every field is
identity-bound.

| Field | Content |
|---|---|
| `id` | stable token, unique in the log |
| `quantity` / `cell` | a declared quantity name with its unit tag, or an `(action, harm)` cell for a chance |
| `range` | `lo`, `hi` as W6 decimals on the tag's grid (`UnitPrecision` otherwise; chance within 0%–100%) |
| `estimator` | a named party or tool with its version ("memory profiler 2.3", "the build agent", "the on-call engineer") |
| `method` | a short text ("peak over the last 5 runs, plus 20%"). It is shown, never interpreted |
| `basis` | ids of the observations, data snapshots (content hashes) or other estimates it used |
| `support` | W2's kinds: `observation`, `statistical`, `calculation`, `testimony`, `assumption` |
| `recorded` | log sequence number and W6 day |
| `supersedes` | optional id of an earlier estimate of the same quantity or cell |

- **Settings** (`kind: setting`) are exact, belong to one alternative, and are chosen by the chooser.
- **Conditions** and **stated cells** carry an author and a support (a condition is usually `assumption`: it is the
  author's model).
- **Severity, costs and bands** are policy content with their author, identity-bound in the environment like
  `regulated`.

### 5.2 What the checker does with them

It checks each estimate's shape, tags, grid and range. It checks provenance: a missing `estimator`, `support` or
`recorded` is `EstimateProvenance: <id> <field>`. It checks policy provenance requirements, for example "The peak
memory of a job must be estimated by the memory profiler" (`EstimatorNotAllowed`). It then computes 2.3 and 3.2–3.3 and
nothing else.

In a W2 document an estimate can also be an `attributed` unit (the estimator estimates …). Accepting it as true is a
bridge leaf, as for any attribution (W2).

### 5.3 Two estimates of one quantity

If a record cites two unsuperseded estimates of one quantity, the policy's declared combination rule applies:

- `latest` uses the one recorded later;
- `hull` uses the smallest range covering both (precautionary);
- `intersection` treats both as true, and an empty intersection is an inconsistency.

Otherwise the record is `ConflictingEstimates: <quantity>`. VE never picks a combination rule.

## 6. Auditing past decisions (question 5)

### 6.1 The log

The log is append-only and hash-chained. Each entry has a sequence number, a day and one of these kinds:

- `estimate`, `setting`, `condition`, `statement`, `supersession`;
- `instruction`: a user's confirmation, with the party;
- `decision`: the decision record and its risk-report id;
- `taken`: the alternative taken;
- `outcome`: observed harms and measured quantities, with observer and support `observation`.

W6 has days but no clock time (W6 6.2), so order within a day is the sequence number. **OPEN (Q-clock)**

### 6.2 What the log must record for each decision

- **The decision:** its id, sequence, day, chooser and the policy's `(environment_id, document_hash)`.
- **The alternatives:** every declared alternative with its inaction and settings. This is `alternatives_declared`,
  "alternatives considered so far" (alt 5.3).
- **The model:** the harms considered, every estimate, condition and stated cell cited (ids and content hashes), and
  the instructions received before the decision.
- **The result:** the risk report id (bound to all of the above), the checker build, and the `taken` entry.

Every entry the decision cites must have a smaller sequence number than the decision. A later entry is
`HindsightEntry: <id>`, and the record is NOT REPLAYABLE.

### 6.3 The audit questions and verdicts

| Question | Method | Verdicts |
|---|---|---|
| 1. Was the taken alternative permitted given what the agent used? | Replay the risk check on the decision's own snapshot | `PERMITTED AT DECISION TIME` (clear / permitted but not clear, with the reason) · `FORBIDDEN AT DECISION TIME` (a breach, alt 4.3) · `NO CLEAR ACTION AT DECISION TIME` (the recorded dilemma) · `NOT REPLAYABLE` (missing, altered or later entry) |
| 2. Did the agent use what was recorded? | Replay with every unsuperseded estimate of the same quantities and cells recorded before the decision, combined by 5.3 | `SAME VERDICT WITH ALL RECORDED ESTIMATES`, or `DIFFERENT VERDICT WITH ALL RECORDED ESTIMATES: <estimate ids not used>`. A policy may make using them mandatory; a violation of that is then reported under question 1 as NOT REPLAYABLE |
| 3. Did the declared model survive the outcome? | Compare each `outcome` entry with the decision-time cells | per observed harm: `within the declared model` (it was `might`) · `surprise: ruled out by <condition / statement>`, naming the estimate a measured quantity contradicts (observed 5 GB outside E2's 8–10 GB) · `unexamined: ruled out by <decider>` (2.4) |
| 4. How often are an estimator's ranges wrong? | Counts of surprises per estimator across audits | Evidence-layer ledger (EL 2.x); outside certification |

The verdict of question 1 never reads an outcome. A bad outcome after a permitted decision is not a violation, and a
good outcome after a forbidden decision is still a breach. A single outcome neither confirms nor refutes a chance.

### 6.4 The no-hindsight rule, mechanically

The Lean audit function takes a `Snapshot`, which has no outcome field, and admits it only if every cited entry
precedes the decision. Theorem `verdict_ignores_outcomes` states that verdicts computed from logs differing only
after the decision's sequence are equal. It is structural: the snapshot extracted from both logs is identical.

## 7. What the checker reports (question 6)

### 7.1 The decision report (scenario)

The report first checks the regenerated conflict formulas on the decision (alt 4.7). If none holds, it gives, per
alternative:

- **status**: permitted, forbidden, required; UNDECIDED once the P1 `unspecified` default lands (11);
- **the deciding rules** by number;
- **the worst case** with its class;
- **for each `might`**: the witness case and the estimates it came from;
- **for each `cannot` or `leads to`**: the condition and the endpoints that decided it;
- **why the alternative is clear or not** (alt 4.6);
- **margins** (7.4).

Then it gives the clear actions, "the policy does not choose among them" when there are several, the gap lines
(7.2) and `conditional_on`. The report is bound to `(environment_id, document_hash, decision_record_id)` and never
says FOLLOWABLE (alt 4.7).

### 7.2 Document report, conflicts and gaps

The policy's own checks are `alternatives@0`'s: conflict status, then followability only on CONFLICT-FREE. They run
over structures satisfying the risk slot premises (8.1), in which regenerated facts are unconstrained base
predicates, so certificates hold for every decision a valid record could produce (alt 4.2's broader class).

Gap and conflict lines:

| Line | Meaning |
|---|---|
| `inconsistent` | `RiskInconsistent` / `SufficientOutsideNecessary` / `ChanceAgainstPossibility`, with the case and the sources |
| `unexamined_possible`, `assumed_ruled_out` | completed cells (2.4), with the decider |
| `unranked_severities` | a worst-case comparison that could not be made, naming the pair |
| `no_chance_estimate` | `might` cells with the vacuous chance (stage B and later) |
| `point_estimates` | conclusions that hold only because an estimate is a point |
| `default_decided` | alternatives whose status came from the completion default, not a rule (the P1 finding: `default: allow` silently permits) |
| `required_alternative_missing` | a policy-required alternative is absent ("every decision to run a program lists running it with a memory limit"), validated on records like alt existence facts |
| `conflicting_estimates`, `hindsight_entries` | 5.3, 6.2 |
| `dilemmas` | alt 4.6 diagnoses |

### 7.3 Point estimates

For every `leads to` or `cannot` result, the report names each point estimate among the quantities of the deciding
condition. Settings are not named, because they are exact by choice. This is a report property: a single number
standing in for an uncertain quantity is where false certainty enters.

### 7.4 Margins

For each non-point estimate endpoint and each alternative, the margin is the nearest value of that endpoint alone at
which the alternative's **status** changes, with every other estimate fixed. The search stays within valid
estimates (`lo ≤ hi`, and chances within 0%–100%). A change that needs both endpoints of one estimate to move is
reported as "no single change".

- **Why it is computable.** Statuses are piecewise constant in one endpoint, with breakpoints only at the comparison
  thresholds involving it. Those are finitely many and computed by endpoint arithmetic. The margin is found by
  re-evaluating at each breakpoint.
- **What is certified.** Lean re-evaluates at the reported value (a checkable witness that the status differs
  there). Minimality rests on `status_piecewise_constant`.
- **How it is rendered.** "Would change if E2's lower bound were at most 6 GB (now 8 GB)."
- **Guard facts versus status.** Margins are on statuses, not on single guard facts: a guard fact can flip without
  changing the status when another rule still decides it (the OOM case shows one).
- **Stage C.** For linear expected-cost thresholds the report adds the exact joint L∞ radius of that one inequality
  (slack divided by the sum of absolute coefficients).
- **What is not claimed.** Robustness to several estimates moving at once is not claimed for statuses.

## 8. Lean and decidability (question 7)

### 8.1 What stays decidable

| Component | Why decidable | Evidence |
|---|---|---|
| Cells from separable conditions | Ground linear integer arithmetic at interval endpoints | Lean evaluation, `possibleE_iff` / `certainE_iff` |
| Severity order, `lessWorst`, domain closure | Finite relations over declared constants | Regenerated tables; `dependencyOrder` |
| Bands, thresholds, expected cost | Ground rational arithmetic on integer grids (exact scaling) | Lean evaluation |
| Decision report | Finite model evaluation after regeneration | `alternatives@0` scenario evaluation (alt 4.7) |
| Policy conflict and followability | Unchanged W1 / `alternatives@0` tableau, witnesses, UNKNOWN | Certificates over `BaseAdmissibleRisk` |
| Margins | Finitely many breakpoints per endpoint | Witness re-evaluation, `status_piecewise_constant` |
| Chance coherence (B and later) | LP over atoms, rational Farkas certificate or feasible point | EL 2.3, entered by certificate only |

**Slot premises** (Background slot `risk`, after `alternatives`, universal only, as in alt 4.2):

- `certain_possible`;
- severity domain closure, strictness and transitivity (ground);
- at most one class per harm;
- threshold monotonicity (ground).

**Existence facts**, validated on records and never assumed: every harm has a class, and every cell is addressed or
completed.

**Excluded:**

- `$int` quantifiers in norm guards (norms.md 0, W6 3.2);
- products of estimated quantities;
- real numbers, densities and continuous distributions;
- probability inside formulas;
- sequential decisions beyond independent choosers (alt 4.10 stage 2);
- non-separable conditions until item 7.

### 8.2 Trust split

**Trusted (Lean, proved from raw JSON under the unchanged allowlist):**

- the `risk` block decoder;
- W6 decimal lowering, reused;
- the endpoint evaluator and cell regeneration;
- the severity closure;
- the profile-word inlining;
- the slot generator;
- the audit snapshot admission;
- the `ve_risk_route` executable.

**Untrusted:**

- Python's shape check, surface and dispatch;
- rendering of reasons, witnesses and margins;
- Rust's evaluation (differential only).

Integers are unbounded in all three languages; Rust uses big integers as W6 does for 40-digit literals. Trust-cost
line for ROADMAP: "Risk (`risk@0`): new trusted decoder, cell regenerator, severity closure, slot premises and
`ve_risk_route`; untrusted: rendering, margins' minimality search, Rust evaluation."

### 8.3 Files and statement schemata

The files are `lean/VE/Risk/{Decl,Estimate,Derive,Severity,Words,Background,Report,Audit,Wire,Run}.lean` plus
`lean/RISK.md`, and later `Expected.lean` for stage C. The frozen `Norms/*`, `Alternatives/*`, `Route/*` and P0
files are untouched. Names use the prefix `VE.Risk.` and contain no primes.

```lean
namespace VE.Risk
structure Box    -- quantity name ↦ (tag, lo, hi), lo ≤ hi; settings have lo = hi
inductive Cond   -- atom (LinExpr ⋈ 0) | and | or | not | top | bot, W6-tagged
def InBox (b : Box) (v : Valuation) : Prop
def Separable (b : Box) (c : Cond) : Bool          -- no non-point quantity in two atoms (after NNF)
def possibleE (b : Box) (c : Cond) : Bool          -- endpoint evaluation
def certainE  (b : Box) (c : Cond) : Bool

theorem possibleE_iff (b c) (hs : Separable b c = true) : possibleE b c = true ↔ ∃ v, InBox b v ∧ c.holds v
theorem certainE_iff  (b c) (hs : Separable b c = true) : certainE b c = true ↔ ∀ v, InBox b v → c.holds v

def regenerate (R : RiskDoc) (d : Decision) : Tables  -- might_lead_to, leads_to, class tables, threshold facts
theorem regenerate_sound (R d) (hv : validateDecision R d = .ok ()) (a h) :
  ([a, h] ∈ (regenerate R d).might ↔ ∃ v, InBox d.box v ∧ Nec d a h v) ∧
  ([a, h] ∈ (regenerate R d).leads ↔ ∀ v, InBox d.box v → Suff d a h v)
theorem certain_within_possible (R d) (hv) : (regenerate R d).leads ⊆ (regenerate R d).might
theorem severity_strict (R) (h : WellFormedRisk R = true) : StrictPartialOrder (moreSevereClosure R)
theorem lessWorst_strict (R) (h) (B) (hB : BaseAdmissibleRisk R B) : Irreflexive (LessWorst R B) ∧ Transitive (LessWorst R B)
theorem precaution_has_maximal (R) (h) (B) (hB : BaseAdmissibleRisk R B) (r) (hne : ∃ a, Avail B a r) :
  ∃ a, Avail B a r ∧ ¬ ∃ a', Avail B a' r ∧ LessWorst R B a' a
theorem risk_inline_faithful   -- the two defined words (0), as alt's inline_faithful, over S.Admissible
theorem risk_conservative      -- no consequence among formulas not mentioning the risk predicates (as alt 4.9)
theorem risk_scenario_sound    -- the decision report = alt scenario evaluation on the regenerated model
theorem status_piecewise_constant (R d e) : status is constant between consecutive breakpoints of endpoint e
theorem verdict_ignores_outcomes (R) (log₁ log₂) (hd) (hsame : prefix log₁ hd.seq = prefix log₂ hd.seq) :
  auditVerdict R log₁ hd = auditVerdict R log₂ hd
theorem risk_wire_acceptance / risk_wire_scenario_sound / risk_wire_audit_sound   -- raw JSON, as alt's wire theorems
-- stage C (Expected.lean): expected_range_exact (min/max of a linear form over the chance box), dominance_sound
```

`BaseAdmissibleRisk R B := BaseAdmissibleAlt (toAlt R) B ∧ Sat B (riskPremises R)`. The policy's conflict and
followability theorems are alt's `alt_conflict_free` and `followable_sound`, restated over it. That makes explicit
the dependency the review must check: `alternatives@0` item 2's Lean must be merged first.

## 9. Worked example: the out-of-memory decision (agent policy)

### 9.1 The policy (a norm document over an environment with the `alternatives` and `risk` blocks)

The environment and legend:

- **Sorts:** `agent` (chooser), `action`, `harm`, `severity`.
- **The `alternatives` block:** as in the Asimov environment, `performed` = (`permitted`, `required`),
  `outcomes: signed`, `inaction`, `taken`.
- **The `risk` block:**
  - classes `severe`, `serious`, `minor`, with severe > serious > minor, set by the platform team;
  - the harm constants below;
  - `unexamined: {"ruled_out_by": "the deciding agent"}` with `always_possible: ["severe", "serious"]`;
  - estimate combination `hull`;
  - required alternatives for decisions that run a program: a memory-limited run and the inaction;
  - required estimator for the peak memory of a job: the memory profiler.

The legend generated from these blocks:

```text
Each agent faces one choice among the actions available to it and takes at most one of them.
"<action> might lead to <harm>" means the declared estimates, conditions and statements do not rule the harm out.
"<action> cannot lead to <harm>" means they rule it out. "<action> leads to <harm>" means it happens in every case they allow.
An unexamined severe or serious outcome counts as possible; the deciding agent rules out other unexamined outcomes.
Severity, from most to least severe: severe, serious, minor. Severity is set by the platform team.
Data loss is severe. A server outage is serious. A job failure is minor. A task delay is minor. Task abandonment is minor.
<a> has a less severe worst case than <b> when <b> might lead to a harm more severe than every harm <a> might lead to.
By default, an action may be performed.
```

The rules:

```text
Rule 1. Every action must not be performed, if there is a harm such that both that harm is severe and that action
might lead to that harm.
Rule 2. Every action must not be performed, if there is an agent such that both that action is available to that
agent and another action available to that agent has a less severe worst case than that action, unless the user
has confirmed that action.
Rule 3. Every action must not be performed, if that action allows task abandonment to happen.
```

The policy's checks:

- **Conflict:** CONFLICT-FREE is expected (all three rules forbid; no permission rule).
- **Followability:** not FOLLOWABLE document-wide. Rule 1 alone is refuted by a record in which every alternative
  might lead to data loss (NONE-PERMITTED). That witness is what "severe risks have no safe alternative here" looks
  like, and it is correct to show it.
- **Rule 2:** P2 with P4, so by `precaution_has_maximal` it alone never creates a dilemma.

### 9.2 Decision 17 (a scenario record, rendered)

```text
Decision 17 of the build agent, log entry 41, 2026-09-29. Policy agent-ops (document hash …).
Available actions: running the job; running the job with the memory limit; asking the user; not running the job (inaction).
E1. The peak memory of the job is from 6 GB through 12 GB, including both bounds.
    [memory profiler 2.3; peak of the last 5 runs plus 20%; statistical; entry 38]
E2. The free memory of the server during the job is from 8 GB through 10 GB, including both bounds.
    [server monitor; minimum over the last hour; observation; entry 40]
S1. The memory limit equals 7 GB.                      [setting of "running the job with the memory limit"]
C1. Running the job cannot lead to a server outage unless the peak memory of the job is greater than the free memory
    of the server.                                     [the build agent; assumption]
C2. Running the job with the memory limit cannot lead to a server outage unless the memory limit is greater than the
    free memory of the server.                         [the build agent; assumption: the limit is enforced by the kernel]
C3. Running the job with the memory limit leads to a job failure exactly when the peak memory of the job is greater
    than the memory limit.                             [the build agent; assumption]
C4. Running the job cannot lead to a job failure unless the peak memory of the job is greater than the free memory of
    the server.                                        [the build agent; assumption]
T1. Asking the user leads to a task delay.             T2. Not running the job leads to task abandonment.
T3. Asking the user cannot lead to a server outage.    T4. Not running the job cannot lead to a server outage.
T5–T8. Running the job cannot lead to data loss. (and one sentence each for the other three actions)
                                                        [platform team: jobs write only to scratch space; testimony]
```

Unit tag `gb`: scale 1, decimal label "GB". C1–C4 are separable, since each has one comparison. The regenerated
cells:

| Action | Server outage (serious) | Job failure (minor) | Other harms | Worst case |
|---|---|---|---|---|
| running the job | might (C1: 12 > 8; witness 12, 8) | might (C4) | data loss cannot (T5); delay and abandonment ruled out by the agent | serious |
| running the job with the memory limit | cannot (C2: 7 > 8 fails in every case) | might (C3: 12 > 7), not certain (6 ≤ 7) | as above | minor |
| asking the user | cannot (T3) | ruled out by the agent | delay leads (T1) | minor |
| not running the job | cannot (T4) | ruled out by the agent | abandonment leads (T2) | minor |

The expected report:

```text
Decision 17 — conditional on E1, E2, S1, C1–C4, T1–T8 and the build agent's ruled-out cells (8 listed).
running the job: forbidden by rule 2. Worst case: a server outage (serious). A server outage is not ruled out: by C1
  it needs the peak memory of the job (6 GB through 12 GB, E1) to be greater than the free memory of the server
  (8 GB through 10 GB, E2), for example 12 GB and 8 GB. Running the job with the memory limit has a less severe
  worst case (a job failure, minor). The user has not confirmed running the job.
  Would change: if E1's upper bound were at most 8 GB. No single valid change of E2 changes it.
running the job with the memory limit: permitted (by default); clear. Worst case: a job failure (minor): by C3 it
  happens exactly when the peak memory is greater than 7 GB, for example 12 GB; not at 6 GB. A server outage is ruled
  out by C2: 7 GB is not greater than the free memory in any case E2 allows.
  Would change: if E2's lower bound were at most 6 GB (the outage would no longer be ruled out and rule 2 would forbid it).
asking the user: permitted (by default); clear. Worst case: a task delay (minor).
not running the job: forbidden by rule 3: it leads to task abandonment (T2), and running the job with the memory limit
  might not lead to it (ruled out by the build agent).
Clear actions: running the job with the memory limit; asking the user. The policy does not choose between them.
default_decided: running the job with the memory limit, asking the user (permitted because no rule forbids them).
```

The margin for running the job shows why margins are taken on statuses: moving E2's lower bound down to 6 GB changes
the memory-limited run's status, but not the status of running the job, because asking the user still has a less
severe worst case. Raising E2's lower bound to 12 GB would clear running the job, but E2's upper bound is 10 GB, so
that is not a single valid change.

**Decision 18: after asking.** The user replies "run it without a limit" (an `instruction` entry, sequence 44).
Decision 18 is a new chooser with alternatives running the job, running the job with the memory limit and not
running the job, and `the user has confirmed running the job`. Rule 2 is silent on running the job, so it is
permitted by default; Rule 1 does not apply. Expected: **clear = running the job, running the job with the memory
limit**. The report adds "running the job is permitted only because the user confirmed it; its worst case is still
a server outage (serious)". Had the job been able to cause data loss, no confirmation would have helped (Rule 1).

**Variant: shared server (fixture k11).** Rule 2's carve-out becomes "unless the user has confirmed that action and
every harm that that action might lead to is borne only by the user". An outage of a shared server is then not
confirmable. This needs `borne_by` (**OPEN (Q-consent)**).

### 9.3 The audit

The agent took the memory-limited run (entry 42). Entry 57 is an outcome: "A server outage happened. The free memory
of the server fell to 5 GB when a second job started." [server monitor; observation]. The log also holds entry 39,
from the scheduler: "The free memory of the server during the job is from 4 GB through 10 GB, including both bounds."
[a second job is scheduled during the run; calculation]. Decision 17 did not cite entry 39.

```text
Q1  PERMITTED AT DECISION TIME: running the job with the memory limit was clear given E1, E2, S1, C1–C4, T1–T8.
Q2  DIFFERENT VERDICT WITH ALL RECORDED ESTIMATES: entry 39 was recorded before the decision and not used. Under the
    policy's hull rule free memory is 4 GB through 10 GB; C2 no longer rules out a server outage (7 > 4), rule 2 then
    forbids the memory-limited run, and the only clear action is asking the user.
Q3  surprise: a server outage was ruled out by C2 under E2; the observed free memory (5 GB) is outside E2 (8–10 GB).
    Estimate E2 (server monitor) is contradicted; condition C2 is not.
Not concluded: that the decision was wrong because an outage followed.
```

If the policy had required every recorded estimate of a cited quantity to be used, Q1 would be NOT REPLAYABLE
(`estimate not used: 39`), and the finding would be the agent's, not the monitor's. Citing entry 57 in a replay of
decision 17 is `HindsightEntry: 57`.

## 10. Worked examples: Asimov

Both cases use the Asimov environment extended with a `risk` block: classes `fatal` > `injuring`, set by the Asimov
case annotator; `unexamined: possible`. Every rule beyond the source is an **attributed narrowing** and sits in a
reading set beside the source-faithful reading, which keeps the dilemma. Asimov gives no severity order, cost or
chance.

### 10.1 Case A1: weighing harms (injury versus death)

The robot can push a person clear of a falling beam, or do nothing (the inaction). The annotator's statements:

- "Doing nothing leads to the person's death."
- "Doing nothing cannot lead to the person's bruising."
- "Pushing the person might lead to the person's bruising."
- "Pushing the person cannot lead to the person's death."
- "The person's death is fatal." "The person's bruising is injuring."
- Both are harms to a human being.

```text
Rule 1 (Law 1, "injure", possibility reading). Every action must not be performed, if there is a harm such that
both that harm is a harm to a human being and that action might lead to that harm.
Rule 2 (Law 1, "through inaction", rule 7′ of alt 2.6). Every action must not be performed, if there is a harm such
that both that harm is a harm to a human being and that action allows that harm to happen.
Rule 3 (exception to rule 1; the translator's "lesser harm" narrowing, no source text). Every action may be
performed, if there is a robot such that both that action is available to that robot and it is not the case that
another action available to that robot has a less severe worst case than that action.
```

| Rule set | Expected |
|---|---|
| {1, 2} | Pushing is forbidden by Rule 1 (might injure); doing nothing by Rules 1 and 2. NONE-PERMITTED, a document DILEMMA: the README's OPEN, made visible |
| {1, 2, 3}, this scenario | Pushing (worst case injuring) is not beaten, so Rule 3 permits it over Rule 1. Rule 2 does not apply, because pushing does not certainly lead to the bruising. **Clear: pushing** |
| {1, 2, 3}, document | **CONFLICT.** In a structure where both alternatives' worst cases are fatal and doing nothing certainly leads to a death the other might avoid, Rule 3 permits doing nothing and Rule 2 forbids it. Witness rendered: "doing nothing: rule 3 permits (no alternative has a less severe worst case); rule 2 forbids (it allows the death, which pushing might avoid)" |
| {1, 2 (exception to rule 3), 3} | The author's (not Asimov's) choice that "a death another action might avoid is never excused". CONFLICT-FREE is expected. Not FOLLOWABLE: two actions each certain to kill a different person give NONE-PERMITTED. The checker does not resolve trolley problems; it shows them |

### 10.2 Case A2: competing threats, and what each stage adds

P faces death and Q faces injury, and the robot can rescue only one.

- **Rescuing P:** P's death might still occur, because the rescue might fail (stated "might"); Q's injury is certain.
- **Rescuing Q:** P's death is certain; Q's injury is ruled out.
- **Doing nothing:** leads to both.

| Stage and rule set | Expected |
|---|---|
| A, {1, 2 (exception to rule 3), 3} | All three worst cases are fatal, a tie, so Rule 3 permits all. Rule 2 forbids rescuing Q (it allows P's death, which rescuing P might avoid), rescuing P (it allows Q's injury, which rescuing Q avoids) and doing nothing. NONE-PERMITTED, DILEMMA. Stage A cannot weigh a possible death against a certain injury, and it says so |
| A, {1, 3} | All permitted and clear, a tie at fatal. "The policy does not choose" |
| C, {1, 4, 5}: costs fatal 100 points and injuring 10 points (translator's), chance "The chance that rescuing P leads to P's death is from 5% through 20%." (the robot's rescue model, estimator) | Rule 4 (P7): "Every action must not be performed, if there is a robot such that both that action is available to that robot and another action available to that robot has a lower expected cost than that action." Rule 5 (exception to rule 1): the same guard, negated, with "may". EC(rescue P) = 100×[5%, 20%] + 10 = [15, 30]; EC(rescue Q) = 100; EC(nothing) = 110. **Clear: rescuing P.** Margin, on rescuing Q's status: "rescuing Q would no longer be forbidden if the upper bound of the chance that rescuing P leads to P's death reached 90% (now 20%)", since 100p + 10 < 100 iff p < 90%. At 90% the intervals meet, neither alternative dominates, and both rescues are clear |

The README's other OPEN item, ranking threats to the robot, is fixture k22. A severity order over threats works with
P3 in stage A. Preferring fewer threats works with a set-inclusion guard in stage A, or equal costs in stage C.
Neither is in the source.

## 11. Relation to the rest of VE

- **`alternatives@0` and W1.** `risk@0` requires `alternatives@0` (hence `norms@0`) and adds:
  - a `risk` block (identity-bound; `environment_id` changes only for environments carrying it);
  - one Background slot;
  - the base predicate `might_lead_to` and two defined words, inlined as alt 4.3 does;
  - regenerated scenario tables.

  Nothing in W1 or `alternatives@0` changes. Stage 2 of alt 4.10 (traces) remains separate; the ask-then-run
  sequence here is two unlinked choosers.
- **Soft norms.** They are gated with `alternatives@0` (alt 3.1), so "should" risk rules wait for the composition
  proof, and confirmation is a base-predicate carve-out (4.3).
- **W6.** Reuses tags, W6 decimal lowering, same-tag linear arithmetic and the interval wording "from … through …,
  including both bounds". Quantities never reach a norm guard: they are consumed by regeneration. Contract change
  request: the `chance` display kind (3.4).
- **Evidence layer.** Chance coherence and narrowing (EL 2.3) and estimator calibration ledgers (6.3 Q4) are EL's.
  This plan only consumes their certificates.
- **ARCH-ROADMAP P1 "unspecified default".** A risk policy with `By default, an action may be performed.` silently
  permits every alternative no rule addresses. Until the third default lands, the report lists them
  (`default_decided`). Once it lands, `unspecified` makes them UNDECIDED and not clear. That design is norms'
  (after rights merges) and this plan does not pre-empt it.
- **ARCH-ROADMAP P1 limits contract.** Proposed per-decision limits: 16 alternatives, 32 harms, 64 estimates and
  settings, 128 conditions and statements, `MAX_NODES` per condition, 16 classes, 8 bands. All are in the shared
  table and checked before evaluation.

## 12. Staged build plan and fixtures

| # | Item | Gate / trigger | Notes |
|---|---|---|---|
| 0 | Astra + Fable review of this plan | now | Especially 2.2 (possibility as consistency), 2.4, 4.2, 6 |
| 1 | `docs/spec/risk.md`, stage A: block, record format, wordings, 2.2–2.5, severity, words, slot premises, report, audit, diagnostics, Lean statements, fixtures k1–k23 with expectations separated from definitions (as alt 8.1/8.2) | after 0; statement review before 2 | Depends on `alternatives@0` item 2 Lean for the restated theorems |
| 2 | Lean `lean/VE/Risk/*`, `ve_risk_route`, `lean/RISK.md`, ROADMAP trust-cost line | after 1's review | Lean-only semantics |
| 3 | Python surface (`ve/surface/risk.py`), block shape check, dispatch, gap lines; Rust untrusted evaluator; differential (200 random records, including separable-condition generators) | parallel with 2 | Surface fixtures (k19) before acceptance |
| 4 | Use case `usecases/agent-oom/` (policy, decisions 17 and 18, the log, audit) and Asimov A1 and A2 as reading sets beside the merged rules | after 2 and 3 | Every narrowing attributed |
| 5 | Stage B: bands, chance estimates, threshold facts, coherence via EL | **trigger:** a committed policy with graded likelihood words and ranges | |
| 6 | Stage C: costs, expected cost, dominance, joint margins | **trigger:** a committed document with numeric tradeoffs; A2's stage C row is a narrowing, not a trigger | |
| 7 | Non-separable conditions (`order@0` certificates, witnesses), policy-level condition templates, event chains | **trigger:** a committed record whose model needs them | Templates also need the `order@0` × n-ary route |
| 8 | W8: `declare_estimate`, `add_condition`, paraphrases with witness cases, margins in plain English | after 4 | Fidelity gate for Q-wording |

Fixtures for items 1–4 (definitions and expected results; the spec separates them):

| # | Definition | Expected |
|---|---|---|
| k1 | E1 6–12 GB, E2 8–10 GB; the C1 form | `might`, witness (12, 8) |
| k2 | E2 8–10 GB; E1 as 11–12, then 6–8 | certain (sufficient form: 11 > 10) / ruled out (necessary form: 8 ≤ 8) |
| k3 | One estimated quantity in two comparisons of one condition | `RiskConditionShared: <quantity>` |
| k4 | A setting repeated in two comparisons | Accepted (points repeat) |
| k5 | `equals` with coefficient 2 on an estimated quantity | `RiskEqualityCoefficient` |
| k6 | `S` true where `N` is false | `SufficientOutsideNecessary`, with the case |
| k7 | Stated `might` plus a derived ruled-out cell | `RiskInconsistent` |
| k8 | An unaddressed serious cell under `always_possible` / a minor cell under `ruled_out_by` | `might` listed in `unexamined_possible` / `cannot` listed in `assumed_ruled_out` |
| k9 | Severity cycle; an unranked pair in a comparison | `DependencyCycle: <classes>`; `unranked_severities` naming the pair, with `lessWorst` false both ways |
| k10 | Decision 17 | As in 9.2, including margins and `default_decided` |
| k11 | Decision 18; the shared-server variant | clear = run and memory-limited run; the variant is OPEN pending `borne_by` |
| k12 | Point estimate E1 = 12 GB | Memory-limited run `leads to` a job failure; `point_estimates` names E1 |
| k13 | Audit of decision 17 (entries 38–57) | Q1–Q3 as in 9.3 |
| k14 | The taken action is the unconfirmed run | `FORBIDDEN AT DECISION TIME` (breach), whatever the outcome |
| k15 | A decision citing entry 57 | `HindsightEntry: 57`, NOT REPLAYABLE |
| k16 | Two estimates of free memory, no combination rule | `ConflictingEstimates: free memory` |
| k17 | Missing estimator / support / recorded | `EstimateProvenance: <id> <field>` |
| k18 | A decision that runs a program without the memory-limited alternative | `required_alternative_missing` |
| k19 | Surface: each wording of 2.1 once; `may lead to`, `does not lead to`, `is safer than`, `Every action … cannot …` | One derivation each; rejections with the rewrites of 2.1 |
| k20 | Asimov A1, all four rows | As in 10.1 |
| k21 | Asimov A2, stage A rows | As in 10.2 |
| k22 | Law 3 threats. (a) The fire rescue might destroy the robot (severe to it); the water rescue might damage it (minor); a P3 rule among lawful rescues. (b) A third rescue that meets both threats, with a set-inclusion guard | (a) Water rescue clear, fire rescue forbidden; without the narrowing both are clear (the README's current result). (b) The rescue meeting only one threat is preferred by the set-inclusion guard. Both are attributed narrowings |
| k23 | Conservativity and identity | Every existing fixture, identity and hash is unchanged; the block changes `environment_id`; the `precaution_has_maximal` property holds on 300 random P2-only records |

Stage B and C fixtures are written when those stages trigger. Anticipated: band admission; chance against
possibility; vacuous chance; A2's stage C row with its 90% margin; coherence failure reported by EL.

## 13. Open questions

1. **Q-wording.** `cannot lead to` read deontically? `leads to` versus `certainly leads to`? Should `could lead to`
   ever be a synonym? Settled by the W8 fidelity gate.
2. **Q-worst-case.** Maximin over the partial order (4.2) versus lexicographic certainty versus set inclusion. Which
   does the agent-policy source intend? A reading set in translation.
3. **Q-unexamined.** Is `possible` the right recommended default? Under it, large records are dilemma-prone, which
   pushes agents towards `ruled_out_by`.
4. **Q-joint.** Cells are marginal. Harms that happen together (crash *and* data loss) need cases, not cells.
5. **Q-chains.** Event-to-event conditions (exhaustion → outage) and chained chances. Deferred to item 7 and stage C.
6. **Q-templates.** Policy-level conditions over quantity attributes of actions need `order@0` × n-ary, gated in W6.
7. **Q-chance-tag.** W6's single-`percent` rule; the contract change request for a `chance` display kind.
8. **Q-new-harms.** A decision meeting a harm kind the policy did not list: reject, or report as unclassified
   (always possible, class unknown)?
9. **Q-consent.** Whose harms a confirmation covers (`borne_by`). Whether confirmations expire.
10. **Q-clock.** Clock time for logs (W6 has days only); sequence numbers meanwhile.
11. **Q-agent-as-estimator.** The agent authors its own conditions and often its own estimates. Beyond required
    estimators (5.2) and audit Q2/Q3, is independent estimation needed for serious classes?
12. **Q-EV-scope.** Whether expected-cost rules should ever range over severe classes. The design supports tiers but
    does not decide.
13. **Q-soft.** "Should"-strength risk rules wait for the soft-norms × `alternatives@0` composition proof.
14. **Q-unspecified.** The P1 third default. `default_decided` is the interim report line.
15. **Q-dependency.** `alternatives@0` item 2 (Lean) must merge before item 2 here. Its fixture expectations are
    inherited, not re-derived.

## 14. Risks

1. **False precision.** Mitigations:
   - ranges, with point estimates flagged;
   - band words always shown with their ranges;
   - the vacuous chance for unknowns;
   - no chains;
   - margins on every threshold;
   - `conditional_on` on every result.
2. **Gaming by the chooser.** An agent can narrow its ranges, omit alternatives or rule out harms. Mitigations:
   - policy-fixed harms and severities;
   - `always_possible` classes;
   - required alternatives and estimators;
   - audit Q2 (unused estimates) and Q3 (surprises per estimator).

   None of these certifies honesty. They make dishonesty visible.
3. **Readers over-trusting "permitted".** A permitted risky action is permitted *relative to the estimates*. The
   status text always names the worst case and the confirmation that permitted it.
4. **Scope creep towards decision theory.** Stages B and C are trigger-gated. Utilities beyond per-class costs,
   risk attitudes, discounting and sequential decisions are outside and stay so until a committed document needs
   them.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-29 | Draft 1 | Initial plan: two-layer design (estimate layer regenerating Boolean facts; unchanged rule layer); possibility as consistency with declared estimates and conditions; the separable endpoint fragment; stages A/B/C with triggers; severity order and the worst-case word; rule patterns P1–P7 and `precaution_has_maximal`; provenance, audit log and no-hindsight rule; report, gaps and status margins; Lean statement schemata; OOM, Asimov A1 and A2 worked examples; fixtures k1–k23; open questions. Plan only. |
