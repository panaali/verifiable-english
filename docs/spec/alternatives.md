# Alternatives (`alternatives@0`): preventable harm over explicit alternatives, on `norms@0`

> Status: item-1 specification, draft 3 (2026-09-28), written from [causation-PLAN.md](causation-PLAN.md) draft 4,
> the transcription of the converged Astra + Fable debate (`manage-agents/debates/design-causation/{astra,fable}.md`,
> REVISE, CONVERGED after round 3), with the ten edits of the Astra + Fable statement review of draft 1
> (`manage-agents/debates/causation-spec/{astra,fable}.md`, FIX, CONVERGED after round 3) applied and attributed in
> section 12, and the four corrections of Astra's verification of draft 2
> (`manage-agents/causation-verify1b-astra.final.md`, FAIL) applied and attributed in section 13. It is the
> statement under the repeated item-1 gate, which covers the changed entries (10.13)
> and precedes items 2 and 3 (PLAN-EXPAND2 rule 10). Sections 4 to 7 are the statements under review; section 8 gives the fixtures with their
> definitions (8.1) separated from their expected results (8.2), so that each reviewer derives the expectations from
> the stated rule sets, premises and models before reading them; section 11 lists every point where this draft chose
> between readings of the plan. Theorem statements and fixtures are implementation obligations, not claims of
> completed proofs or tests. Inputs: [norms.md](norms.md) (W1, cited as `norms.md n`), [soft-norms.md](soft-norms.md),
> [document.md](document.md) (W2), [VISION.md](../../VISION.md), [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md)
> section 6, `lean/VE/Norms/*` and [lean/NORMS.md](../../lean/NORMS.md) (the W1 Lean names this spec reuses), the
> Asimov use case (`usecases/asimov-laws/{rules.ve,environment.json,README.md}` once item 0 merges; today
> `~/code/ve-asimov/usecases/asimov-laws/`), the pinned constitution (cited `C:n`). Nothing here changes a frozen
> contract, a `norms@0` hash, a W1 theorem statement or a checker function.

## 0. Scope, one paragraph

"Allow through inaction" is a claim about what else the agent could have done. The checker never certifies a causal
fact (VISION.md converged rule 8); it certifies structure over a **declared** causal model: for each *chooser* (one
agent at one decision point) a finite list of alternatives, each action belonging to exactly one chooser, and an
outcome table `leads_to(action, harm)` whose negative cells are either stated with their support or covered by a
named decider's completion assumption. Three words get fixed definitions, *avoidable*, *allows*, *prevents*, and are
inlined into ordinary W1 guards, so the document that reaches the route is plain `norms@0` over base predicates plus
four universal slot premises. One new check, **followability**, asks whether at every choice some available action
is permitted, forgoes no required alternative and discharges every *mapped* obligation; it is computed only on a
CONFLICT-FREE document and reports FOLLOWABLE (a certificate over `BaseAdmissibleAlt`, a class broader than accepted
scenarios, with the cost named), DILEMMA (a certified witness with a rendered diagnosis) or UNKNOWN. Scenario results
are bound to their model and are never called FOLLOWABLE. The semantics are Lean-only (SEMANTICS-MIGRATION-PLAN 6):
Python checks the block's shape, dispatches, registers the surface and searches for proofs; Rust evaluates untrusted.

In this specification: the block, roles and fulfilments (1), the English (2), the wire form (3), well-formedness,
premises, definitions, outcomes, followability, scenarios, stratification and conservativity (4), the report (5),
diagnostics (6), the Lean definitions and every item-2 theorem as a statement (7), the fixtures (8), limits (9), the
review checklist (10) and the resolved choices (11).

Out of scope, by the plan: time, traces and multi-step strategies (stage 2); nondeterministic environments (games);
joint causation and joint action; degrees (probability, risk, uplift, severity); proximate causation beyond an open
predicate; combination with `soft-norms@0` (gated on the soft-norms composition proof); the W8 hooks (item 6) beyond
the wordings fixed in section 2; the coverage protocol (plan item 5).

## 1. What an alternatives document is

An alternatives document is a W1 norm document (norms.md 1) over an environment that carries the `alternatives`
block, whose guards, carve-outs and assertion units may use the four profile words, and whose obligations may
declare fulfilments. Everything W1 requires still holds on the inlined document (4.1); the alternatives checks come
on top.

### 1.1 The block: roles

| Field | Mandatory | Names | Argument sorts, fixed | Canonical verbalisation, fixed |
|---|---|---|---|---|
| `chooser`, `action`, `harm` | yes | three distinct declared sorts | | |
| `available` | yes | a base predicate | `(action, chooser)` | `{0} is available to {1}` |
| `leads_to` | yes | a base predicate | `(action, harm)` | `{0} leads to {1}` |
| `outcomes` | yes | `"signed"` or `{"complete_by": "<decider>"}` | | (1.4) |
| `decided_by` | no | a string of at most 64 bytes or `unstated` | | who stands behind the counterfactual cells and, unless a W2 open-term declaration names another, behind `causes` |
| `performed` | no | `{"permission": m, "obligation": q}`, a declared W1 pair | both `(action)` | W1's act wordings |
| `inaction` | no | a base predicate | `(action)` | `{0} is inaction` |
| `taken` | no | a base predicate | `(action)` | `{0} is taken` |
| `proximate` | no | a base predicate | `(action, harm)` | `{0} causes {1}` |
| `fulfilments` | no | list of `{"obligation": o, "body": <formula> | "avoids"}` (1.3) | | |

Sort and predicate *names* are the author's; the block assigns roles. Argument orders and verbalisations of role
predicates are fixed so that each wording of section 2 has one reading and no verbalisation can read `risks` or
`could lead to` (`AlternativesSort`, `AlternativesVerbalisation`). Role predicates are base predicates: not
regulated, not W3-defined, no W5 flag (`AlternativesRegulated`). The block is part of the canonical environment
bytes (3.5).

### 1.2 Choosers and ownership

A chooser is one agent at one decision point; a second decision by the same agent is a second chooser, unlinked.
`available(a, r)` says `a` is one of `r`'s alternatives. **Every action is available to at most one chooser** (slot
premise `own`, 4.2) and, in every accepted scenario, to at least one (existence fact E1). With this, a unary
`taken`, `permitted` or `required` on an action speaks about exactly one choice, and "the robot that can take it"
is a definite description.

### 1.3 Fulfilments and mapped obligations

An obligation-role regulated predicate `o` whose first argument sort is the chooser sort may declare one
fulfilment `F_o`, a formula over the context `(action, remaining arguments of o)` that mentions base predicates of
`E` only (`FulfilmentNotBase: <o>` if it mentions a regulated, defined or profile symbol). The profile supplies one
named body, `avoids`, for obligations on `(chooser, harm)`: `avoids(a, h) := ¬leads_to(a, h)`. An obligation with a
fulfilment is **mapped**: taking an alternative `a` discharges `o(r, x̄)` when `F_o(a, x̄)`. The `performed`
obligation `q` is the action constraint itself and may not carry a fulfilment (`FulfilmentOnPerformed`). Any other
obligation without a fulfilment is **unmapped**: it does not constrain the choice, and every followability report
names it (5.2). A fulfilment body is never an atom of a rule or a unit: it enters `clear` (4.6), the scenario words
(4.3) and the legend (2.3) only, so the tree mentions the four profile words and no fulfilment name, and the
declared vocabulary is extended by the profile words alone (4.1(2)).

### 1.4 The outcome table and its negative cells

`avoidable` depends on `¬leads_to`, so an unstated cell is a claim that an action avoids a harm; it must never
become evidenced silently (debate: Astra 4). The mandatory `outcomes` field chooses:

- **`signed`.** Every cell is stated. In a W2 document, each cell is a unit, positive `<action> leads to <harm>` or
  negative `It is not the case that <action> leads to <harm>.`, with its own `support`; nothing is generated. On a
  supplied scenario the table is a list of signed rows (3.3); a missing row for an available action and a harm of
  the model is `InvalidModel("alternatives", "outcome of <a> for <h> unstated")`.
- **`complete_by: <decider>`.** An action leads to a harm only where the document says so. The route regenerates
  one labelled premise `alternatives:table_complete` from the document's positive cells over constants (4.4) and
  lists it in the residual as an assumption of the decider; on a scenario, missing rows are read as negative and
  listed under `assumed_harm_free` with the decider. Document completion and row completion are distinct: the
  premise is generated from the document's cells alone and is evaluated on a scenario like every other `Γ_base`
  unit, so a scenario's positive rows must lie within the document's positive cells
  (`InvalidModel("alternatives", "premise alternatives:table_complete fails")` otherwise), and rows change neither
  the premise nor the document hash (3.3, 3.5). Every result whose certificate uses the premise says
  `conditional_on: alternatives:table_complete`.

## 2. The English (one reading each; rejected as today when `alternatives@0` is off)

### 2.1 Wordings

| Wording | The one reading (the IDE's paraphrase) | Formal effect |
|---|---|---|
| `<action> is available to <chooser>` | The action is one of the chooser's alternatives at its decision point. | `available(a, r)` |
| `<action> leads to <harm>` | In the declared model, if the action is taken the harm occurs. Not "tends to". | `leads_to(a, h)` |
| `It is not the case that <action> leads to <harm>.` | The negative cell, stated with its support. | `¬leads_to(a, h)` |
| `<action> is inaction` | The chooser's do-nothing alternative. | `inaction(a)` |
| `<action> is taken` | What happened. | `taken(a)` |
| `<action> causes <harm>` | Only with `proximate` declared: <decider> judges the action the proximate cause of the harm; it then also leads to it. | `causes(a, h)` |
| `<harm> is avoidable by <chooser>` | Some action available to the chooser does not lead to the harm. | `avoidable(h, r)` |
| `<harm> is unavoidable by <chooser>` | The chooser has at least one available action, and every one of them leads to the harm. | `unavoidable(h, r)` |
| `<action> allows <harm> to happen` | The action leads to the harm, and another action available to the same chooser does not. | `allows(a, h)` |
| `<action> prevents <harm>` | The action does not lead to the harm, and another action available to the same chooser does. | `prevents(a, h)` |
| `every action available to <chooser> <verb phrase>` (guards) | All of the chooser's alternatives satisfy the verb phrase. | `∀a'. available(a', r) → VP(a')` |
| `every other action available to <chooser> <verb phrase>` (guards of a rule on an action; reference form `that other action`) | All of the chooser's alternatives other than the action the rule is about satisfy the verb phrase. | `∀a'. available(a', r) ∧ a' ≠ a → VP(a')` |
| `another action available to <chooser> <verb phrase>` (guards of a rule on an action) | Some alternative of the chooser other than that action satisfies the verb phrase. | `∃a'. available(a', r) ∧ a' ≠ a ∧ VP(a')` |
| `there is a <chooser> such that that action is available to that <chooser> and <formula>` | Binds the chooser of the action a rule is about; by ownership it is "the robot that can take it". | `∃r. available(a, r) ∧ …` |
| `Every <chooser> must <act> each <harm> …, if …` on a mapped obligation | W1 obligation on (chooser, harm), fulfilled by taking an action satisfying the fulfilment; for `avoids`: by taking an action that does not lead to the harm. | act with fulfilment |

Quantified guards are W1's (norms.md 9.2); the existing `there is a <noun> such that`, `both … and`, `either … or`,
`it is not the case that`, `first`/`second` and label reference forms apply unchanged (docs/english-surface.md).
The four profile words and the three `available to` constructs are registered by `ve/surface/alternatives.py` with
`profiles=("alternatives@0",)`; an author template that collides with them is rejected by the registry's duplicate
refusal as today.

### 2.2 Synonyms, rejected wordings, the short object form

Input synonyms rendered canonically: `preventable by` → `avoidable by`; `lets <harm> happen` → `allows <harm> to
happen`; `<action> does not lead to <harm>` → `It is not the case that <action> leads to <harm>.`. Nothing else.

Rejected with rewrites: undeclared `causes` (declare `proximate`, or write `leads to`); `results in`, `brings about`
(→ `leads to`); `could lead to`, `risks`, `increases the risk of`, `contributes to`, `provides uplift to` (a hedged
unit or an open degree term; the table is Boolean and the IDE says so); `allows <person> to <act>` (deontic: W1
`may`); `through inaction allows` (readings A and B, 2.6, with the distinguishing model o); `that <chooser>` inside a
rule on an action with no binder (→ `there is a <chooser> such that that action is available to that <chooser> and
…`).

The short object form `allows a harm to a human being to happen` (an indefinite inside the object of `allows`) is
**accepted only if fixture q shows it has exactly one derivation**; until then the canonical guard is the long form
`there is a harm such that both that harm is a harm to a human being and that action allows that harm to happen`,
and every rule text in this specification is given in a form the existing surface admits or marks the short form.

### 2.3 The legend (generated from the block, shown with the environment)

```text
Each <chooser> faces one choice among the actions available to it and takes at most one of them.
Each action is available to at most one <chooser>.
Doing nothing counts as one of a <chooser>'s actions; every checked situation lists exactly one inaction per <chooser> with any alternative.   (inaction declared)
"<action> leads to <harm>" records the declared model; for an action not taken it is a counterfactual judgment by <decider>.
Every cell of the outcome table is stated.                                                                      (signed)
An action leads to a harm only where this document says so; <decider> stands behind every unstated cell.       (complete_by)
"<action> causes <harm>" records a proximate-cause judgment by <decider>; an action that causes a harm leads to it.  (proximate declared)
A <chooser> <act> by taking an action that <fulfilment body verbalised>.                                          (one per mapped obligation; for avoids: "prevents a harm by taking an action that does not lead to it")
The following duties do not bear on the choice: <unmapped obligations' act phrases>.                            (when any)
```

The third sentence states a validity fact of accepted scenarios, not a premise (4.2), and is qualified by E2: a
chooser with no alternative has no inaction and is reported `no alternatives` (4.7); the status text of 5.2 says
so where it matters.

### 2.4 The reader's checklist (norms.md 2.5, extended)

For every rule using `allows`, `prevents` or `avoidable`, the IDE shows a two-action situation in which the rule
decides and a situation in which the harm is unavoidable and the rule does not decide. For every mapped obligation,
a situation in which some permitted alternative discharges it and one in which none does. For a followability
status, the dilemma situation rendered in document terms with each alternative's reason ("`nothing` is forbidden by
rule 7: it allows h1 to happen; `pull` is required by nothing and discharges preventing h1 but not preventing h2").
For a `GuardOnOwnOutcome` offer, the sentence of 4.8 saying that the rewrite changes meaning.

### 2.5 Binding

Inside a rule whose regulated predicate is on the action sort, `that <chooser>` has no antecedent; the only binder
is `there is a <chooser> such that that action is available to that <chooser> and …` (by `own`, unique). A rule on
`(chooser, harm)` binds `that <chooser>` and `that harm` as W1 situation variables. Each new wording of 2.1 has
binding, unique-derivation and paraphrase fixtures before surface acceptance (fixture q; items 3 and 4).

### 2.6 Rules from the sources (canonical texts used by the fixtures)

Asimov (`usecases/asimov-laws`): Rules 1–6 are `rules.ve` verbatim, by stable name (`law-3-permission`,
`law-2-permission`, `law-1-direct` = rule 3, `law-0-direct`, `law-2-obey` = rule 5, `law-3-preserve` = rule 6). **In a
rule subset, `over` entries naming absent rules are dropped**: `law-1-direct` is "exception to rule 2" verbatim, so
in {3, 7} rule 3 carries no precedence edge (W1's `UnknownRule`, norms.md 4.1(2), would reject the subset
otherwise); a subset's precedence graph is exactly the listed rules' edges among themselves. New rules, each an
attributed translator's reading or narrowing where marked (VISION.md 3); "short object form" marks an indefinite
inside the object of `allows` or `leads to`, accepted subject to fixture q (2.2):

```text
Rule 7.   Every action must not be performed, if that action is inaction and there is a harm such that both that
          harm is a harm to a human being and that action allows that harm to happen.
          guard  inaction(a) ∧ ∃h. harms_human(h) ∧ allows(a, h)                    reading A of the inaction clause
Rule 7′.  Every action must not be performed, if there is a harm such that both that harm is a harm to a human
          being and that action allows that harm to happen.
          guard  ∃h. harms_human(h) ∧ allows(a, h)                                   the `allows` reading of "injure" (set {causes, allows})
Rule 8.   Every robot must prevent each harm that is a harm to a human being, if that harm is avoidable by that robot.
          on prevent_required(r, h); guard harms_human(h) ∧ avoidable(h, r); fulfilment avoids     reading B
Rule 8c.  Rule 8 with  Except when every action available to that robot leads to a harm that is a harm to a human being.
          carve-out ∀a. available(a, r) → ∃h. harms_human(h) ∧ leads_to(a, h)       (short object form, subject to q)
Rule 8⁻.  Every robot must prevent each harm that is a harm to a human being.        (rule 8 without its guard; fixture c)
Rule 9 (exception to rules 3 and 7).  Every action may be performed, if there is a robot such that that action is
          available to that robot and every other action available to that robot either injures a human being or
          allows a harm to a human being to happen.                                     (short object form, subject to q)
          guard  ∃r. available(a, r) ∧ ∀a'. (available(a', r) ∧ a' ≠ a → injures_human(a') ∨ ∃h. harms_human(h) ∧ allows(a', h))
          a narrowing attributed to the translator: Asimov's text has no such clause
Rule 9⁻.  Rule 9 as an exception to rule 7 only.                    (with rule 3 unrelated by precedence: fixture b′, A⁻)
Rule 9_B (exception to rule 3).  Every action may be performed, if there is a robot such that that action is
          available to that robot and every other action available to that robot injures a human being.
Rule 10.  Every action must not be performed, if that action is inaction and there is a harm such that both that
          harm is a harm to humanity and that action allows that harm to happen.                (Law 0, reading A)
Rule 6′.  Every robot must prevent each harm that is a harm to that robot, if that harm is avoidable by that robot.
          on prevent_required(r, h); guard harm_to(h, r) ∧ avoidable(h, r)                       (Law 3 as a prevention duty)
Γ_link.   Every action that injures a human being leads to a harm that is a harm to a human being.   (short object form, subject to q)
          ∀a. injures_human(a) → ∃h. harms_human(h) ∧ leads_to(a, h)     an author premise (W2 assertion, support assumption)
```

Constitution: `C:187` (fixture f): sort `assistant` as chooser; `Rule F1. Every assistant must respond to the risk to
life, if a life is at risk for that assistant.` on `respond_required(assistant)` with fulfilment
`refers(a) ∨ gives_safety_information(a)`; author premise `Γ_ref`: `For every assistant there is an action such that
both that action is available to that assistant and that action refers the user to emergency services.` `C:335`
(fixture g): `Rule G1. Every action must not be performed, if there is a harm such that both that harm is serious and
that action allows that harm to happen.` (`serious` open). `C:338`, `C:531` (fixture h): `Rule H1. Every action must
not be performed, if there is a harm such that both that harm is a harm to a human being and that action causes that
harm.` with `proximate` declared.

## 3. Declarations, wire form and strict form

### 3.1 The environment block (identity-bound like `regulated`)

```json
"alternatives": {
  "chooser": "robot", "action": "action", "harm": "harm",
  "available": "available", "leads_to": "leads_to",
  "outcomes": "signed",
  "decided_by": "Asimov case annotator",
  "performed": {"permission": "permitted", "obligation": "required"},
  "inaction": "inaction", "taken": "taken",
  "proximate": "causes",
  "fulfilments": [{"obligation": "prevent_required", "body": "avoids"},
                  {"obligation": "respond_required", "body": ["or", ["unary", "refers", ["var", 0]],
                                                                    ["unary", "gives_safety_information", ["var", 0]]]}]
}
```

`outcomes` is `"signed"` or `{"complete_by": "<decider>"}` (`MissingOutcomeDecider` if the object lacks the
decider; `InvalidInput: alternatives.outcomes` otherwise). A fulfilment `body` is `"avoids"` (allowed only for an
obligation on `(chooser, harm)`) or a formula in the P0 wire form over the context `(action :: remaining sorts).reverse`
(W1's convention, norms.md 6.1: de Bruijn index 0 is the last remaining argument, and the action when there is
none, as in the `respond_required` example), mentioning base predicates of `E` only. Unknown fields are rejected. `alternatives@0` requires `norms@0`
(`UnsupportedProfile: alternatives@0 requires norms@0`); with `soft-norms@0` also enabled the route answers
`UnsupportedProfile: alternatives@0 with soft-norms@0` until the composition proof (plan item 7).

### 3.2 Norm units and assertion units

Norm units are W1's (norms.md 3.2) with guards and carve-outs that may mention the profile words as atoms:
`["binary", "allows", ["var", 1], ["var", 0]]` and so on, with the fixed argument orders of 1.1. Assertion units
over the profile words (`h1 is avoidable by R`) are ordinary W2 units and are inlined like guards (4.3). Cells are
assertion units on `leads_to` with `support`; a negative cell is the negation. No unit may have a profile word as
a regulated or defined predicate.

W2 graph nodes may use those four words as typed atoms. The checker admits a regenerated
`alternatives:profile:<word>` leaf for each word: the closed equivalence between that atom and its inlined base
body, universally quantified over its two argument sorts. These definition leaves are assumptions in the graph
report and its semantic consequence; they add no model table and do not alter source identities.

### 3.3 Scenarios (finite models on this route)

A finite model supplies base tables as in W1 (norms.md 11.3) except that the `leads_to` table is supplied as signed
rows:

```json
"outcomes": [{"action": "nothing", "harm": "h1", "leads_to": true,  "support": "testimony"},
             {"action": "pull",    "harm": "h1", "leads_to": false, "support": "assumption"}]
```

The `leads_to` relation is the set of positive rows; `signed` requires a row for every (available action, harm)
pair; `complete_by` reads missing rows as negative and lists them (5.3). Rows are validated with the model
(`RowsConsistent`, 7.1): each names a constant of the action sort and one of the harm sort, no two rows name the
same pair, and the positive rows are exactly the `leads_to` table. Under `complete_by` the document's regenerated
`alternatives:table_complete` is evaluated on the model with the rest of `Γ_base` (4.2), so every positive row must
be a positive cell of the document (`InvalidModel("alternatives", "premise alternatives:table_complete fails")`
otherwise); rows are model data and never enter the premise or the document hash (1.4, 3.5). Regulated tables are
computed, never supplied (W1's `InvalidModel("norms", …)`); the profile words are computed from the base tables.

### 3.4 Strict text

The profile words and constructs have the strict forms `(a allows h)`, `(a prevents h)`, `(h avoidable_by r)`,
`(h unavoidable_by r)`; the `available to` constructs are ordinary strict quantifiers over `available` with the
explicit inequality (`not (x1 equals x0)`). Fulfilments are environment JSON, as `regulated` is. `print(parse(s)) =
s` on canonical text; English and strict forms round-trip through the same AST with W1's preserved name metadata
(norms.md 10.6, 11.2).

### 3.5 Identity and binding

`environment_id` binds the whole block (roles, fixed orders, `outcomes`, `decided_by`, `performed`, `inaction`,
`taken`, `proximate`, fulfilments) beside `regulated`; it is unchanged for every existing environment (none has the
block). A norm unit's `meaning_id` is W1's over the un-inlined AST (profile words as atoms), so inlining changes no
identity. The alternatives document hash is the canonical array of the active norm objects and the active base
assertion units (including cells) in document order under `environment_id`. Packages: a conflict package has W1's
outer binding `(environment_id, document_hash, conflict_target)` and an inner certificate bound to the regenerated
`E_base` and `Background_base ++ altPremises`; a **followability package** has outer binding `(environment_id,
document_hash, "followable")` and an inner certificate bound to `E_base`, `Background_base ++ altPremises ++ Γ_base`
and the closed formula `∀r. followable°(r)`; a **dilemma package** binds the same source plus the witness model id
and the chooser; a **scenario report** binds `(environment_id, document_hash, model_id)`. Every binding is
recomputed from the raw source (norms.md 11.4 step 4); a replay against a changed rule, cell, block field or model
is stale (fixture v).

## 4. Semantics

### 4.1 Well-formedness (`WellFormedAlt`)

An alternatives document `A = (E, lits, alt, T, Γ)` is well-formed when, in this order:

1. `E` enables `alternatives@0` and `norms@0` and not `soft-norms@0`; the block decodes with no unknown field.
2. The three sorts exist and are distinct; every role predicate exists, is base, and has exactly the argument sorts
   and the canonical verbalisation of 1.1 (`UnknownSymbol: alternatives.<role> <name>`, `AlternativesRegulated`,
   `AlternativesSort`, `AlternativesVerbalisation`). The role predicates are therefore pairwise distinct: a declared
   predicate has one argument-sort list and one verbalisation; `available` and `leads_to` differ in sort (chooser
   versus harm), `leads_to` and `proximate`, and `inaction` and `taken`, differ in verbalisation. A block naming one
   predicate for two roles fails this clause (fixture l6), and `alternative_monotone` (7.2) relies on the
   distinctness. No declared sort, predicate or constant of `E` is named `avoidable`, `unavoidable`, `allows` or
   `prevents` (`AlternativesReserved: <name>`), so `extEnv` (7.1) extends `E` by the four profile words without
   collision.
3. `performed`, when present, names a declared W1 pair `(m, q)` both on `(action)` (`AlternativesPerformed: <m>,
   <q>`).
4. Each fulfilment names an obligation-role predicate whose first sort is the chooser sort, once
   (`DuplicateDeclaration: fulfilment <o>`, `FulfilmentSort: <o>`), not the `performed` obligation
   (`FulfilmentOnPerformed`); its body is typed over its context and mentions base predicates only
   (`FulfilmentNotBase: <o>`); `avoids` only on `(chooser, harm)`.
5. `T` type-checks over `E` extended by the four profile words with their fixed sorts, profile words occurring in
   guards, carve-outs and assertion units only.
6. The inlined document `inlineTree A` (4.3) is within `MAX_NODES` per formula (`ResourceLimit: alternatives
   inlining of rule <n>`) and W1 well-formed (norms.md 4.1), including both DAGs computed on the inlined tree; a
   guard mentioning the rule's own predicate through a deontic atom on another action is W1's `DependencyCycle: <p>`
   with the English-layer hint `GuardOnOwnOutcome` (4.8).
7. `Γ` (the active base assertion units, inlined) is well-formed over `E_base`; under `complete_by` the generated
   `alternatives:table_complete` (4.4) is appended to `Γ`.

### 4.2 Slot premises, `BaseAdmissibleAlt`, existence facts and the broader class

The Background slot `alternatives` (generator after `profile` in the P0 hook table) contributes closed universal
formulas over base predicates, in this order and only those whose role is declared:

```text
own           ∀a r r'.  available(a, r) ∧ available(a, r') → r = r'
one_taken     ∀r a a'.  available(a, r) ∧ available(a', r) ∧ taken(a) ∧ taken(a') → a = a'
one_inaction  ∀r a a'.  available(a, r) ∧ available(a', r) ∧ inaction(a) ∧ inaction(a') → a = a'
proximate     ∀a h.     causes(a, h) → leads_to(a, h)
```

```text
altPremises A            := the list above (labels alternatives:own, alternatives:one_taken, alternatives:one_inaction, alternatives:proximate)
Background_baseAlt A     := Background_base(inlineTree A) ++ altPremises A          (flags, literals, then the slot)
backgroundAlt A          := background(inlineTree A) ++ altPremises A               (definitions, literals, profile, slot)
BaseAdmissibleAlt A B    := BaseAdmissible (inlineTree A) B ∧ Sat B (altPremises A)
Γ_base                   := A.Γ, the document's active base premises (assertion units over E_base, inlined; incl. table_complete)
```

`BaseAdmissibleAlt` is the admissibility contract of every statement in section 7: W1's `BaseAdmissible` is `E_base`
plus `Background_base`, and the route strips the block before W1's decoder sees the document, so the slot premises
are named explicitly in the conflict hypothesis `hc`, in both followability theorems and in the wire statements
(debate: Astra 5, Fable round 2). The conflict check on this route runs over `Background_baseAlt`.

**Existence facts** are validated on supplied finite models and never assumed:

```text
E1  every action of the action domain is available to some chooser
E2  when `inaction` is declared: every chooser with at least one alternative has an inaction among them (exactly one, with one_inaction)
E3  under `signed`: every (a, h) with a available to some chooser and h in the harm domain has a signed row
```

`validateAlternatives` (7.1) checks the four premises by evaluation, the supplied rows (`RowsConsistent`, 3.3),
E1–E3, and `Γ_base` by evaluation (under `complete_by` including `alternatives:table_complete`), and reports
`InvalidModel("alternatives", <text>)` (6). **Certificates therefore quantify over a class broader than accepted
scenarios.** A FOLLOWABLE certificate holds in every `BaseAdmissibleAlt` structure satisfying `Γ_base`, hence in
every accepted scenario; but a document followable in every accepted scenario may have no certificate. The cost,
named: an obligation whose fulfilment is `inaction(a)` is met in every valid scenario (E2), yet a structure in which
a chooser with alternatives has no inaction refutes `∀r. followable(r)`; no certificate exists, and no valid witness
exists either, so the status is UNKNOWN and the report says which existence fact is validated but not assumed
(fixture u). The premises stay universal because of W1's Background shape, immediate soundness over the
superclass, and because an existence premise can be added later as a new profile version without changing any
accepted scenario. norms.md 7.1(3) is not the reason: it is a fragment-membership condition, and every document
using `allows` is outside the fragment anyway.

### 4.3 The profile words and inlining

```text
avoidable(h, r)    := ∃a. available(a, r) ∧ ¬leads_to(a, h)
unavoidable(h, r)  := (∃a. available(a, r)) ∧ ¬avoidable(h, r)
allows(a, h)       := leads_to(a, h) ∧ ∃r. available(a, r) ∧ avoidable(h, r)
prevents(a, h)     := ¬leads_to(a, h) ∧ ∃r. available(a, r) ∧ ∃a'. available(a', r) ∧ leads_to(a', h)
```

By `own` the `∃r` in `allows` and `prevents` is single-valued (theorem `owner_unique`), so the paraphrase "another
action available to the same robot" is exact. `allows` covers enabling by an act and failing to prevent by inaction;
`inaction` tells them apart; *causing* is the separate open `causes`, never derived. `inline A φ` replaces every
profile-word atom in `φ` by its body, capture-avoiding, in one pass (bodies mention no profile word); fulfilment
names are never atoms (1.3), so nothing else is replaced. `inlineTree A` applies `inline` to every guard, carve-out and unit of `T` and returns the
W1 `Doc ⟨E, lits, T_inlined⟩`; the route runs W1 on it. Theorem `inline_faithful` (7.2): on every structure
admissible for `E` (`S.Admissible A.E`), the inlined formula denotes exactly what the original denotes when the
profile words are interpreted by their bodies. Admissibility is part of the claim, not a convenience: on a structure
in which a constant of `E` is undefined, a profile-word atom is false while its inlined body may be true (7.2).
No W1×W3 composition is needed (INTEGRATION-GAPS); when it closes, the bodies may become definition layers with no
change of meaning. The scenario-only words:

```text
discharged_o(r, x̄) := ∃a. available(a, r) ∧ taken(a) ∧ F_o(a, x̄)                  o mapped
violation_o(r, x̄)  := O_o(r, x̄) ∧ (∃a. available(a, r) ∧ taken(a)) ∧ ¬discharged_o(r, x̄)
violation(a)       := O_q(a) ∧ ¬taken(a)        breach(a) := ¬O_m(a) ∧ taken(a)        (the performed pair; W1's violation with taken as done)
```

### 4.4 Outcomes: the `table_complete` premise

Under `complete_by`, with `C⁺ = {(c_a, c_h)}` the positive cells of the document (assertion units `leads_to(c_a,
c_h)` over constants), the route regenerates

```text
alternatives:table_complete   ∀a h. leads_to(a, h) → ⋁_{(c_a, c_h) ∈ C⁺} (a = c_a ∧ h = c_h)         (⊥ when C⁺ is empty)
```

appended to `Γ_base` with support `assumption` and the block's decider, never taken from the wire. Under `signed`
nothing is generated: a conclusion that needs a negative cell is provable only from a stated negative unit, and the
countermodel otherwise shows the cell true. On scenarios (3.3) the two modes act on rows (1.4). The residual line
`counterfactual_leaves` lists every stated cell with its support and the block's decider; `assumed_harm_free` lists
the cells the completion covers.

### 4.5 Conflict status on this route

W1's conflict check (norms.md 5) runs on `inlineTree A` with `Background_baseAlt A` in place of `Background_base`:
per-target tableau certificates for CONFLICT-FREE (`AltConflictFree A := ∀ B, BaseAdmissibleAlt A B → ConflictFree
(inlineTree A) B`), a valid finite base witness passing `backgroundValidAlt` for CONFLICT, UNKNOWN otherwise.
Statuses, witnesses, `Overlap` and the vacuity report are W1's unchanged. A W1 certificate over `Background_base`
alone also proves the target (fewer premises), and the route accepts it.

### 4.6 The followability check

Computed **only when the conflict status is CONFLICT-FREE**; on CONFLICT and on UNKNOWN the status is `not
computed: conflict status <CONFLICT | UNKNOWN>` (fixture s). With `O_p°` the base-substituted outcomes of norms.md
4.5 on the inlined document, `(m, q)` the `performed` pair and `F_o` the mapped fulfilments:

```text
clear(r, a)   := available(a, r)
               ∧ [m declared] O_m°(a)                                               taking a is permitted
               ∧ [q declared] ∀a'. (available(a', r) ∧ O_q°(a') → a' = a)          a forgoes no required alternative
               ∧ ⋀_{o mapped} ∀x̄. (O_o°(r, x̄) → F_o(a, x̄))                         a discharges every mapped obligation on r
followable(r) := (∃a. available(a, r)) → ∃a. clear(r, a)
```

The argument order of `clear` is (chooser, action), as `ClearIn A S r a` (7.1). Absent parts of the block drop their
conjunct. A chooser with no alternative is followable vacuously and is reported `no alternatives` (4.7, 5.2). The
checked claim is about **the mapped obligations and the declared action constraints**, never "every rule"; the
report names each unmapped obligation (5.2). Verdict scope:

| Result | Evidence | Scope and binding |
|---|---|---|
| **FOLLOWABLE** | a tableau certificate for `Background_baseAlt ++ Γ_base ⊢ ∀r. followable°(r)` over `E_base` | document-wide over every `BaseAdmissibleAlt` structure satisfying `Γ_base`; `conditional_on` lists the `Γ_base` labels the certificate uses; bound as a followability package (3.5). Unqualified FOLLOWABLE is reserved for this |
| **DILEMMA** | a finite base model `M` with its signed rows, valid for `E_base`, passing `validateAlternatives` (premises, rows, E1–E3, `Γ_base`), and a typed chooser `r` at which `¬followable°` evaluates true. Lean certifies exactly this (`dilemma_witness_sound`) | refutes the document-wide claim for this rule set and `Γ_base`; bound as a dilemma package with the model id and chooser |
| **UNKNOWN** | neither within budget; the budget named | document |

The **diagnosis** rendered with a DILEMMA is computed by the untrusted evaluator at the witness chooser, on the
base-substituted outcomes in `M`:

```text
Perm := {a available to r : O_m°(a)}          (all alternatives when m is absent)
Req  := {a available to r : O_q°(a)}          (∅ when q is absent)
if Perm = ∅                                   NONE-PERMITTED
else if |Req| ≥ 2                             OVER-REQUIRED(Req)
else P := {a ∈ Perm : Req ⊆ {a}}              permitted and forgoing no required alternative; nonempty on a CONFLICT-FREE document,
                                              because Req = {a₀} with a₀ ∉ Perm is a pair conflict point
     Duties := {(o, x̄) : o mapped, O_o°(r, x̄)}
     if some (o, x̄) ∈ Duties has no a ∈ P with F_o(a, x̄)      UNDISCHARGEABLE(o, x̄)   (the first in declaration and tuple order;
                                                              the rendering names any forbidden or forgoing alternative that would discharge it)
     else                                                     JOINTLY-UNDISCHARGEABLE(D) for a minimal D ⊆ Duties with no common discharger in P
```

Because `¬followable°(r)` is certified, exactly one branch applies. Minimality of `D` and the per-alternative
reasons are report properties, not theorems; the certified object is `¬followable°` at `r`. A DILEMMA is not a
verdict that the rules are wrong: it is a situation in which no available action complies with the mapped
obligations and the declared action constraints, which is what "ought implies can" asks an author to face.

Two consequences, stated so that expectations can be derived. A document keeping Asimov's rule 5 (`law-2-obey`) or
rule 6 (`law-3-preserve`) is never document-wide FOLLOWABLE: two ordered (or two protective) permitted alternatives
are both required (fixture j). A prohibition whose guard is an unconstrained base predicate (rule 3 on
`injures_human`) is refuted by the structure in which every alternative of one chooser satisfies it; a certificate
needs an escape covering that case (rule 9 as an exception to rule 3, fixture b′) or an author premise in `Γ_base`
shown under `conditional_on`.

### 4.7 Scenario evaluation

On a supplied scenario passing `validateAlternatives`, the route first evaluates every regenerated conflict formula
of 4.5 on the model. If one is true at a typed tuple, the answer is that CONFLICT witness, classified as
`alt-conflict` would classify it (norms.md 5.2), and no per-chooser evaluation is rendered: at a conflict point
`O_m°` is a completion value with no meaning (norms.md 11.3), so nothing below is defined there. Otherwise the report
lists per chooser: its alternatives (with the inaction and the taken alternative when declared), which are
permitted and required (`O_m°`, `O_q°`), which harms are avoidable and unavoidable by it, which alternative allows or
prevents which harm, which alternatives are `clear` and for the others why not, and, when `taken` is supplied,
violations and breaches (4.3). The text is `<chooser> has a clear action: <list>`, `no clear action at <chooser>:
<diagnosis>` or, for a chooser with no alternative (E2 admits one), `no alternatives at <chooser>`, plus `unmapped
obligations: <list>`; it is bound to `(environment_id, document_hash, model_id)` and never says FOLLOWABLE. A
scenario at which `¬followable°` holds is also a dilemma witness for the document **only when the document's
conflict status is CONFLICT-FREE** (4.6); the report then says so, and otherwise says `not computed: conflict status
<CONFLICT | UNKNOWN>` for the document beside the scenario result.

### 4.8 Stratification and `GuardOnOwnOutcome`

A guard of a rule on `permitted` that mentions `permitted` on another action ("if it is not the case that another
action available to that robot may be performed") is a self-edge in the shared DAG, W1's `DependencyCycle:
permitted` (norms.md 4.1(4)). The English layer attaches the hint `GuardOnOwnOutcome` and offers rule 9's factual
guard ("… every other action available to that robot either injures a human being or allows a harm to a human being
to happen") as **an author-selected change of meaning, not an equivalence**: the factual guard names which facts
forbid the other alternatives today, and a rule added later that forbids alternatives for another reason is not
tracked by it. The offer says so in one sentence. Priority across different obligations for different actions is
therefore never a checker primitive: it is a W1 exception over facts, a soft-norm rank on the colliding rules
(which resolves per action only, soft-norms 4.5), or an open decider in the residual; the followability check
certifies what was written or shows the situation in which it fails.

### 4.9 Conservativity

Environments without the block are untouched by construction: the profile is a new route (`ve_alternatives_route`),
frozen files are unchanged, and `environment_id` of every existing environment is unchanged. For a document over an
environment with the block whose premises and conclusion mention none of the block's role predicates, the slot
premises add no consequence: `alternatives_conservative` (7.2), proved by reinterpreting `available`, `inaction`,
`taken` and `causes` as empty relations in any base-admissible structure, which satisfies the four premises and
leaves the old formulas' denotations unchanged. The theorem is about base formulas over `oldEnv` (7.2); agreement
of the two routes on a conclusion over regulated predicates (fixture r4, `permitted` and `required`) is differential
evidence, not a theorem, and r5 exercises the theorem's content. The trust-cost line for `ROADMAP.md` (converged rule 4), to land
with item 2: "Alternatives (`alternatives@0`): new trusted decoder, inliner, slot generator, followability formula
and `ve_alternatives_route` executable, proved from raw JSON under the unchanged allowlist; untrusted: the Python
block-shape check, the rendered diagnosis, Rust evaluation."

### 4.10 Outside this profile

Stage 2 (traces, horizon `H`, deterministic `successor`, "avoidable within H" as a bounded existential chain,
backward-prevention validity once W6's time sort merges) starts only on a committed document that needs it
(converged rule 3). Nondeterministic environments (games), joint causation (two robots who could each prevent a harm
both "allow" it; a harm preventable only jointly is avoidable by neither, a stated limit), degrees, consent,
responsibility and causal assertions between propositions (W2 kind `causal`, labelled) stay outside.

## 5. The report

### 5.1 The questions

| Question | Method | Result |
|---|---|---|
| Is the declared model well-formed, and is this situation valid for it? | `WellFormedAlt`; `validateAlternatives` | diagnostics (6) / `InvalidModel("alternatives", …)` |
| Can the rules contradict each other? | W1's conflict check on the inlined document over `Background_baseAlt` | CONFLICT-FREE / CONFLICT (witness) / UNKNOWN, as norms.md 5.2 |
| Can the mapped obligations and the declared action constraints be met at every choice? | certificate; witness with `¬followable°`; budget; only on CONFLICT-FREE | FOLLOWABLE (`conditional_on`) / DILEMMA (diagnosis, situation) / UNKNOWN / `not computed` |
| In this situation, what does each chooser's choice look like? | the regenerated conflict formulas on the model first, then finite evaluation (4.7) | a CONFLICT witness at a conflict point; otherwise per chooser: alternatives, permitted, required, avoidability, allows/prevents, clear, violations, or `no alternatives`; bound to the model |
| What is assumed about the causal model? | the residual (5.3) | declared alternatives, cells with support, assumed cells, deciders, unmapped obligations, narrowings |

### 5.2 Status text

```text
FOLLOWABLE: at every choice some available action is permitted, forgoes no required alternative and discharges the
  mapped obligations (<act phrases>); unmapped obligations: <act phrases | none>; conditional on <Γ_base labels | nothing>;
  certificate <id>. Certified over every structure satisfying the slot premises; existence facts (<E1–E3 as applicable>)
  are validated on situations and not assumed.
DILEMMA at <chooser> in <situation>: no available action complies with the mapped obligations and the declared action
  constraints here; <diagnosis>; <per-alternative reasons>. This is a situation the rules do not cover, not a verdict
  that they are wrong.
UNKNOWN: <budget>[; note: an existence fact that is validated and not assumed may be what a certificate would need]
not computed: conflict status <CONFLICT | UNKNOWN>
scenario (model <id>): <chooser> has a clear action: <list> | no clear action at <chooser>: <diagnosis> | no alternatives at <chooser>;
  unmapped obligations: <list | none>[; also a dilemma witness for the document (conflict status CONFLICT-FREE) |
  document followability not computed: conflict status <CONFLICT | UNKNOWN>]
scenario (model <id>): CONFLICT at <tuple>: <W1 classification>; no per-chooser evaluation
```

Diagnosis renderings: `NONE-PERMITTED` ("every available action is forbidden: <a>: rule <n>; …"), `OVER-REQUIRED`
("<a> and <a'> are both required: rules <n>, <n'>"), `UNDISCHARGEABLE(<act> <args>)` ("<duty> is required here and
no permitted available action discharges it[; <a> would, but is forbidden by rule <n> | forgoes <a'>, which is
required]"), `JOINTLY-UNDISCHARGEABLE(<duties>)` ("each of <duties> is discharged by some permitted available action,
but no single action discharges all of them").

### 5.3 Residual lines (W2 coverage, plan item 3)

Beside open terms, assumptions, bridge leaves and unresolved reading sets: `alternatives_declared` (per chooser, its
alternatives with their declarer: the list is "alternatives considered so far", extensible by a challenger like a
reading set), `counterfactual_leaves` (every stated cell with support and decider), `assumed_harm_free` (cells covered
by `complete_by`, with the decider), `table_complete` (the premise, when generated, as an assumption of the decider),
`proximate_judgments` (every `causes` unit, with the decider), `unmapped_obligations`, `dilemmas` (diagnoses with
situations), `narrowings` (with citations: rule 7′ as the `allows` reading of "injure", rule 9 as the translator's
resolution, annotator facts such as `injures_human(pull)`). A norm unit using a profile word over declared
vocabulary is CHECKED; one whose guard carries an open predicate (`serious`, `causes`) is OPEN, as today. No new
status.

### 5.4 Binding

Every package and report binds the source as in 3.5; scenario reports additionally bind the model id. A followability
package replayed against a document with a changed rule, cell, block field or `Γ_base` unit is stale; a scenario
report replayed against a different model is stale (fixture v).

## 6. Diagnostics (shared text in Python and Lean unless marked)

| Text | When | Kind |
|---|---|---|
| `UnsupportedProfile: alternatives@0 requires norms@0` / `alternatives@0 with soft-norms@0` | profile gate; the composition proof pending | error |
| `InvalidInput: alternatives.<field>` | a mandatory field missing or malformed; an unknown field | error |
| `UnknownSymbol: alternatives.<role> <name>` | a role names an undeclared sort or predicate | error |
| `AlternativesRegulated: <role> <p>` | a role predicate is regulated, defined or flagged | error |
| `AlternativesSort: <role> expects (<sorts>)` / `AlternativesSort: sorts must be distinct` | argument sorts differ from 1.1; chooser, action, harm not distinct | error |
| `AlternativesVerbalisation: <role> must read "<canonical>"` | a role predicate's verbalisation is not the canonical one | error |
| `AlternativesReserved: <name>` | a declared sort, predicate or constant is named as a profile word (4.1(2)) | error |
| `AlternativesPerformed: <m>, <q>` | `performed` is not a declared pair on `(action)` | error |
| `FulfilmentSort: <o>` / `FulfilmentNotBase: <o>` / `FulfilmentOnPerformed: <q>` / `DuplicateDeclaration: fulfilment <o>` | fulfilment declarations (1.3) | error |
| `MissingOutcomeDecider: alternatives.outcomes` | `complete_by` without a decider | error |
| `ResourceLimit: alternatives inlining of rule <n>` / `ResourceLimit: fulfilments` | `MAX_NODES` after inlining; more than 16 fulfilments | error |
| `DependencyCycle: <p>` + hint `GuardOnOwnOutcome` (English layer only) | a guard mentions the rule's own predicate on another action (4.8) | error |
| `InvalidModel("alternatives", "action <a> is available to two choosers: <r>, <r'>")` | `own` fails | model |
| `InvalidModel("alternatives", "<r> has two taken actions: <a>, <a'>")` / `"<r> has two inactions: <a>, <a'>"` | `one_taken` / `one_inaction` fail | model |
| `InvalidModel("alternatives", "<a> causes <h> but does not lead to it")` | `proximate` fails | model |
| `InvalidModel("alternatives", "action <a> belongs to no chooser")` / `"<r> has no inaction"` | E1 / E2 | model |
| `InvalidModel("alternatives", "outcome of <a> for <h> unstated")` | E3 under `signed` | model |
| `InvalidModel("alternatives", "row <a>/<h> <untyped | repeated>")` / `"row <a>/<h> disagrees with leads_to"` | `RowsConsistent` fails (3.3) | model |
| `InvalidModel("alternatives", "premise <label> fails")` | a `Γ_base` unit false in the supplied model; under `complete_by` the label `alternatives:table_complete` when a positive row is not a document cell | model |
| unbound `that <chooser>` in a rule on an action (English layer) | 2.5; rewrite offered | error |

Order: environment declarations (W1's, then the block), then W1's rule checks on the inlined tree, then fulfilments,
then `Γ_base`. English diagnostics carry the span and the plain-language expectation as today. Existing P0 and W1
diagnostics are unchanged. Model diagnostics come from the Lean route; Python only dispatches (debate: Fable 5).

## 7. Lean (item 2): definitions and the exact statements to prove

Files: `lean/VE/Alternatives/Decl.lean` (`AltEnv`, `AltDoc`, `WellFormedAlt`, canonical checks), `Inline.lean`
(profile bodies, `inline`, `inlineTree`, faithfulness), `Background.lean` (`altPremises`, `BaseAdmissibleAlt`,
`tableComplete`, conservativity, the conflict check over the extended background), `Followable.lean` (`clearF`,
`followableF`, `ClearIn`, `FollowableIn`, both soundness theorems), `Validate.lean` (`validateAlternatives`, existence
facts, `backgroundValidAlt`, scenario evaluation, `diagnose`), `Wire.lean`, `Admission.lean`, `Run.lean` (the
`ve_alternatives_route` executable, root `AlternativesMain.lean`), and `lean/ALTERNATIVES.md` listing each theorem in
plain words. Frozen `Norms/*`, `Route/*` and all P0 sources untouched; `VE.lean`, `VE/Audit.lean` and `lakefile.toml`
gain imports, audit entries and the new target only; the audit allowlist unchanged. Names have prefix
`VE.Alternatives.`; W1 names are `VE.Norms.*` as in `lean/NORMS.md`; theorem names contain no prime. The blocks are
statement schemata: helper names are defined here, not already implemented Lean.

Two conventions hold in every statement below. **Argument orders, fixed once**: `avoidable` and `unavoidable` take
`(harm, chooser)`; `allows` and `prevents` take `(action, harm)`; `clear` takes `(chooser, action)`, as `ClearIn A S
r a`; `followable` takes `(chooser)`; a fulfilment body takes `(action, remaining arguments of the obligation)`. A
generated formula's context is its argument list `.reverse` (norms.md 6.1: index 0 is the last argument) and it is
evaluated at `tupleVal` of its arguments in argument order (`tupleVal vs = vs.reverse`, `tupleVal_typed`). **Carrier
transport**: no statement shares an element between independently quantified structures. Where a base structure and
an expansion appear together with a common element, the expansion `S` is quantified and the base structure is
`restrictAll (inlineTree A).T S` (the same carrier, as `subst_sound`); where a structure is extended, the extension is
built from `S` on the same carrier (`extendAvailable`); a finite witness `M` appears only through `M.asStructure` with
its own elements, and the passage from `M` to an expansion is the explicit hypothesis `restrictAll (inlineTree A).T S
= M.asStructure` of the corollary `dilemma_expansion`, never an element of `M` used in `S` (`DocumentExpansion`
equates structures propositionally only).

### 7.1 Definitions

```lean
namespace VE.Alternatives
open VE.Norms (Doc Tree Regulated Node Pair pairs Sat tupleVal bindAll atom anyF allF envAt size before subst
  restrictAll outcomeBase conflict pairConflict ConflictFree DocumentExpansion BaseAdmissible backgroundBase
  background elaborate WellFormed backgroundValid PrefixAdmissible PrefixPremises ConflictFreeAt)

inductive Outcomes | signed | completeBy (decider : String)

structure Fulfilment where
  obligation : String              -- obligation-role predicate, first sort = chooser
  body       : VE.Formula          -- context (action :: remaining sorts of the obligation).reverse; base predicates only
                                   -- `avoids` is  .not (atom leadsTo [action, harm])

structure AltEnv where
  chooser   : String
  action    : String
  harm      : String
  available : String               -- (action, chooser)
  leadsTo   : String               -- (action, harm)
  outcomes  : Outcomes
  decidedBy : Option String        -- none = "unstated"
  performed : Option (String × String)   -- (m, q)
  inaction  : Option String
  taken     : Option String
  proximate : Option String
  fulfilments : List Fulfilment

structure AltDoc where
  E    : VE.Environment            -- the complete original environment; the role predicates are base predicates of E
  lits : List String
  alt  : AltEnv
  T    : Tree                      -- guards, carve-outs may mention the four profile words; no fulfilment atoms (1.3)
  Γ    : List VE.Formula           -- active base assertion units, inlined; tableComplete appended under completeBy

structure Row where                -- 3.3: one signed row of a supplied scenario
  action  : String                 -- a constant of the action sort
  harm    : String                 -- a constant of the harm sort
  leadsTo : Bool
  support : String

def profileWords : List String := ["avoidable", "unavoidable", "allows", "prevents"]
def extEnv (A : AltDoc) : VE.Environment                -- E plus the four profile words with their fixed sorts (4.1(2): no collision)
def avoidableF (A : AltEnv) : VE.Formula                -- 4.3, avoidable(h, r): context [harm, chooser].reverse
def unavoidableF (A : AltEnv) : VE.Formula              -- unavoidable(h, r): context [harm, chooser].reverse
def allowsF (A : AltEnv) : VE.Formula                   -- allows(a, h): context [action, harm].reverse
def preventsF (A : AltEnv) : VE.Formula                 -- prevents(a, h): context [action, harm].reverse
def inline (A : AltDoc) : VE.Formula → VE.Formula       -- capture-avoiding replacement of the profile-word atoms only
def inlineTree (A : AltDoc) : Doc                       -- ⟨A.E, A.lits, T with every guard/carve-out inlined⟩
def withDefinitions (A : AltDoc) (S : VE.Structure) : VE.Structure
                                                        -- S plus the four profile words interpreted by their bodies (same carrier)
def WellFormedAlt (A : AltDoc) : Bool                    -- 4.1

def ownPremise (A) : VE.Formula                          -- 4.2
def oneTakenPremise (A) : Option VE.Formula
def oneInactionPremise (A) : Option VE.Formula
def proximatePremise (A) : Option VE.Formula
def altPremises (A : AltDoc) : List VE.Formula           -- own :: the declared optional premises, in 4.2 order
def tableComplete (A : AltDoc) (cells : List (String × String)) : VE.Formula   -- 4.4
def backgroundBaseAlt (A : AltDoc) : List VE.Formula := backgroundBase (inlineTree A) ++ altPremises A
def backgroundAlt (A : AltDoc) : List VE.Formula := background (inlineTree A) ++ altPremises A
def BaseAdmissibleAlt (A : AltDoc) (B : VE.Structure) : Prop :=
  BaseAdmissible (inlineTree A) B ∧ Sat B (altPremises A)
def PrefixAdmissibleAlt (A : AltDoc) (k : Nat) (S : VE.Structure) : Prop :=
  PrefixAdmissible (inlineTree A) k S ∧ Sat (restrictAll (inlineTree A).T S) (altPremises A)
def AltConflictFree (A : AltDoc) : Prop := ∀ B, BaseAdmissibleAlt A B → ConflictFree (inlineTree A) B
def altConflictFreeCheck (A : AltDoc) (certs : List (Option VE.Tableau.Certificate)) : Bool
  -- every W1 target of (inlineTree A) has an accepted certificate for backgroundBaseAlt A ⊢ ∀x̄. ¬conflict over envAt (inlineTree A) 0

/-- 4.6, as formulas over E_base (° = subst (inlineTree A).T (size (inlineTree A))). -/
def clearF (A : AltDoc) : VE.Formula                     -- clear°(r, a), context [chooser, action].reverse, evaluated at tupleVal [r, a]
def followableF (A : AltDoc) : VE.Formula                -- followable°(r), context [chooser], evaluated at tupleVal [r]
def notFollowableF (A : AltDoc) : VE.Formula := .not (followableF A)
def allFollowable (A : AltDoc) : VE.Formula := bindAll [A.alt.chooser] (followableF A)

/-- 4.6, as propositions over a document expansion S (regulated predicates interpreted by S). -/
def TypedChooser (A) (S : VE.Structure) (r : S.Carrier) : Prop := S.inSort A.alt.chooser r
def Avail (A) (S : VE.Structure) (a r : S.Carrier) : Prop := S.relation A.alt.available [a, r]
def ClearIn (A : AltDoc) (S : VE.Structure) (r a : S.Carrier) : Prop :=
  Avail A S a r ∧
  (∀ m q, A.alt.performed = some (m, q) →
     S.relation m [a] ∧ ∀ a', Avail A S a' r → S.relation q [a'] → a' = a) ∧
  (∀ f ∈ A.alt.fulfilments, ∀ xs, VE.TupleTyped S (restSorts A f) xs →
     S.relation f.obligation (r :: xs) → f.body.denote S (tupleVal (a :: xs)))
def FollowableIn (A : AltDoc) (S : VE.Structure) : Prop :=
  ∀ r, TypedChooser A S r → (∃ a, Avail A S a r) → ∃ a, ClearIn A S r a

/-- Same carrier, domains, constants and every other relation; `available` extended by `more` (7.2, alternative_monotone). -/
def extendAvailable (A : AltEnv) (S : VE.Structure) (more : S.Carrier → S.Carrier → Prop) : VE.Structure :=
  { S with relation := fun p vs =>
      if p = A.available then S.relation p vs ∨ (match vs with | [a, r] => more a r | _ => False) else S.relation p vs }

/-- 4.2 finite validation and 4.7 evaluation. -/
def backgroundValidAlt {α} [DecidableEq α] (A : AltDoc) (M : VE.FiniteModel α) : Bool :=
  backgroundValid (inlineTree A) M && (altPremises A).all (fun p => p.eval M [])
def RowsConsistent {α} (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Prop
  -- 3.3: every row's action and harm constants denote in M, in the action and harm domains; no two rows name one
  -- (action, harm) pair; [a, h] ∈ M.relations A.alt.leadsTo ↔ some row with leadsTo = true denotes (a, h)
def ExistenceFacts {α} (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Prop
  -- RowsConsistent A M rows ∧ E1 ∧ E2 ∧ (A.alt.outcomes = .signed → E3 over rows)
def validateAlternatives {α} [DecidableEq α] (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Except String Unit
  -- M.Valid, backgroundValidAlt, RowsConsistent, E1–E3 by enumeration, every Γ formula by evaluation (under
  -- completeBy this includes tableComplete: positive rows within the document's positive cells); the 6 texts on failure
def scenarioConflict {α} [DecidableEq α] (A : AltDoc) (M : VE.FiniteModel α) : Option (Target × List α)
  -- 4.7: the first regenerated conflict formula of (inlineTree A) true at a typed tuple of M, if any;
  -- Target is the element type of VE.Norms.targets (inlineTree A), as in alt_conflict_witness_sound
def diagnose {α} [DecidableEq α] (A : AltDoc) (M : VE.FiniteModel α) (r : α) : Diagnosis   -- untrusted, 4.6 procedure
```

`restSorts A f` is the obligation's argument sorts after the chooser; the tuple convention is W1's (relation tuples in
argument order, `tupleVal` for valuations, `[]` for closed formulas). `Row` is the signed-row record of 3.3; `rows`
are validated with `M` and never enter `A` (no premise, no hash).

### 7.2 Theorems

```lean
/-- 4.1 ⇒ W1 well-formedness of the inlined document. -/
theorem alternatives_wellFormed (A : AltDoc) (h : WellFormedAlt A = true) :
  WellFormed (inlineTree A) = true

/-- What inlining changes and what it keeps. -/
theorem inlineTree_shape (A : AltDoc) (h : WellFormedAlt A = true) :
  (inlineTree A).E = A.E ∧ (inlineTree A).lits = A.lits ∧ (inlineTree A).T.regulated = A.T.regulated ∧
  (inlineTree A).T.nodes = A.T.nodes.map (fun N => { N with guard := inline A N.guard, carveOuts := N.carveOuts.map (inline A) })

/-- Inlined formulas mention no profile word (the tree has no fulfilment atoms, 1.3). -/
theorem inline_base (A) (h) (φ : VE.Formula) (Γ) (hφ : φ.WellFormed (extEnv A) Γ) :
  (inline A φ).WellFormed A.E Γ ∧ ∀ w ∈ profileWords, w ∉ VE.Norms.preds (inline A φ)

/-- 4.3: inlining is faithful to the definitional reading. `S.Admissible A.E` is needed: on a structure in which a
    harm constant is undefined, `Term.denote` is `none`, the profile-word atom is false, and its inlined body (an
    existential over a negated `leads_to`) can be true. -/
theorem inline_faithful (A : AltDoc) (h : WellFormedAlt A = true) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (extEnv A) Γ) (S : VE.Structure) (hS : S.Admissible A.E)
    (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S Γ ρ) :
  (inline A φ).denote S ρ ↔ φ.denote (withDefinitions A S) ρ

/-- 1.2: under the slot premises an action's chooser is unique (`WellFormedAlt` gives the sorts of `available`). -/
theorem owner_unique (A : AltDoc) (h : WellFormedAlt A = true) (B : VE.Structure) (hB : BaseAdmissibleAlt A B)
    (a r r' : B.Carrier) :
  B.relation A.alt.available [a, r] → B.relation A.alt.available [a, r'] → r = r'

/-- Adding available alternatives to `S` on the same carrier (`extendAvailable`, 7.1) never removes avoidability,
    an `allows` or a `prevents`. `WellFormedAlt` is needed: it makes the role predicates pairwise distinct (4.1(2)),
    in particular `A.alt.available ≠ A.alt.leadsTo`, so `extendAvailable` leaves `leads_to` unchanged. With one
    predicate `p` in both roles, adding `p(a, h)` to a structure holding `p(a, r)` (action `a`, chooser `r`, harm
    `h`) keeps ownership and makes `h` unavoidable by `r`. Nothing is claimed for `clear`. Arguments in argument
    order (4.3). -/
theorem alternative_monotone (A : AltDoc) (hw : WellFormedAlt A = true) (S : VE.Structure)
    (more : S.Carrier → S.Carrier → Prop)
    (hS' : Sat (extendAvailable A.alt S more) (altPremises A)) (r h a : S.Carrier) :
  ((avoidableF A.alt).denote S (tupleVal [h, r]) → (avoidableF A.alt).denote (extendAvailable A.alt S more) (tupleVal [h, r])) ∧
  ((allowsF A.alt).denote S (tupleVal [a, h]) → (allowsF A.alt).denote (extendAvailable A.alt S more) (tupleVal [a, h])) ∧
  ((preventsF A.alt).denote S (tupleVal [a, h]) → (preventsF A.alt).denote (extendAvailable A.alt S more) (tupleVal [a, h]))

/-- 4.5: W1's conflict machinery over the extended background. -/
theorem alt_conflict_free (A : AltDoc) (h : WellFormedAlt A = true) (certs) (hc : altConflictFreeCheck A certs = true) :
  AltConflictFree A
theorem alt_conflict_witness_sound {α} [DecidableEq α] (A) (h) (t) (ht : t ∈ VE.Norms.targets (inlineTree A))
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (inlineTree A) 0)) (hb : backgroundValidAlt A M = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure t.2.1 vs) (hw : t.2.2.eval M (tupleVal vs) = true) :
  ¬ ConflictFree (inlineTree A) M.asStructure ∧ ¬ VE.Route.Unique (DocumentExpansion (inlineTree A) M.asStructure) ∧
  ¬ AltConflictFree A

/-- 4.6: the base formulas denote the expansion-level propositions (via subst_sound and inline_faithful). Stated over
    the expansion `S` and its base restriction on the same carrier (carrier transport, 7). -/
theorem clear_denote (A : AltDoc) (h : WellFormedAlt A = true) (S : VE.Structure)
    (hS : DocumentExpansion (inlineTree A) (restrictAll (inlineTree A).T S) S)
    (hB : BaseAdmissibleAlt A (restrictAll (inlineTree A).T S))
    (r a : S.Carrier) (typed : VE.TupleTyped S [A.alt.chooser, A.alt.action] [r, a]) :
  (clearF A).denote (restrictAll (inlineTree A).T S) (tupleVal [r, a]) ↔ ClearIn A S r a
theorem followable_denote (A) (h) (S : VE.Structure)
    (hS : DocumentExpansion (inlineTree A) (restrictAll (inlineTree A).T S) S)
    (hB : BaseAdmissibleAlt A (restrictAll (inlineTree A).T S)) :
  (allFollowable A).denote (restrictAll (inlineTree A).T S) [] ↔ FollowableIn A S

/-- FOLLOWABLE: the certified claim, over the broader class (4.2). -/
theorem followable_sound (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree A)
    (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (inlineTree A) 0) (backgroundBaseAlt A ++ A.Γ) (allFollowable A) c = true) :
  ∀ B : VE.Structure, BaseAdmissibleAlt A B → Sat B A.Γ →
    ∀ S, DocumentExpansion (inlineTree A) B S → FollowableIn A S

/-- DILEMMA: a typed chooser of a valid finite witness at which ¬followable° evaluates true refutes the document-wide
    claim. The witness appears only as `M.asStructure` instantiating `B`; no element of `M` is used in another
    structure. -/
theorem dilemma_witness_sound {α} [DecidableEq α] (A : AltDoc) (h : WellFormedAlt A = true)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (inlineTree A) 0)) (hb : backgroundValidAlt A M = true)
    (hΓ : A.Γ.all (fun p => p.eval M []) = true) (r : α) (typed : M.inDomain A.alt.chooser r)
    (hd : (notFollowableF A).eval M (tupleVal [r]) = true) :
  ¬ (∀ B : VE.Structure, BaseAdmissibleAlt A B → Sat B A.Γ → (allFollowable A).denote B [])

/-- The expansion-level corollary (carrier transport, 7): on any document expansion `S` whose base restriction
    satisfies the slot premises, a typed chooser `r` of `S` at which ¬followable° denotes true in the restriction has
    no clear alternative in `S`. Applied to a witness `M` through `followable_eval_iff_denote` and the explicit
    hypothesis `restrictAll (inlineTree A).T S = M.asStructure`, under which `r` is an element of `S`; existence of
    such an `S` is conflict-freedom of `M.asStructure` (`conflictFree_expands_document`). -/
theorem dilemma_expansion (A : AltDoc) (h : WellFormedAlt A = true) (S : VE.Structure)
    (hS : DocumentExpansion (inlineTree A) (restrictAll (inlineTree A).T S) S)
    (hB : BaseAdmissibleAlt A (restrictAll (inlineTree A).T S))
    (r : S.Carrier) (typed : TypedChooser A S r)
    (hd : (notFollowableF A).denote (restrictAll (inlineTree A).T S) (tupleVal [r])) :
  ¬ ∃ a, ClearIn A S r a

/-- The finite evaluation of the followability formulas agrees with their denotation (W1's typed eval_iff_denote). -/
theorem followable_eval_iff_denote {α} [DecidableEq α] (A) (M : VE.FiniteModel α) (r : α) :
  (notFollowableF A).eval M (tupleVal [r]) = true ↔ (notFollowableF A).denote M.asStructure (tupleVal [r])

/-- 4.2: successful validation gives every hypothesis `dilemma_witness_sound` needs, plus the rows and existence
    facts (`ExistenceFacts A M rows` includes `RowsConsistent A M rows`). -/
theorem validate_sound {α} [DecidableEq α] [EntityName α] (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row)
    (valid : M.Valid (envAt (inlineTree A) 0))
    (hv : validateAlternatives A M rows = .ok ()) :
  M.Valid (envAt (inlineTree A) 0) ∧ backgroundValidAlt A M = true ∧ A.Γ.all (fun p => p.eval M []) = true ∧
  BaseAdmissibleAlt A M.asStructure ∧ ExistenceFacts A M rows

For a decoded scenario, `validate_sound_decoded` has the same conclusion without a caller-supplied `valid`:
`decodeScenario` establishes `M.Valid` before validation. The generic Boolean validator cannot establish structural
validity for an arbitrary `FiniteModel`: its relation table is a function over every predicate name, and an
otherwise accepted model may give an undeclared, unused predicate an ill-typed tuple. `EntityName` supplies names
for diagnostics and does not affect successful validation. This correction preserves the executable input and
output contracts and the full wire-level conclusion.

/-- 4.7: a scenario answer is rendered only where no regenerated conflict formula holds on the model. -/
theorem scenarioConflict_sound {α} [DecidableEq α] (A : AltDoc) (h : WellFormedAlt A = true) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (inlineTree A) 0)) (hb : backgroundValidAlt A M = true) (t) (vs)
    (hc : scenarioConflict A M = some (t, vs)) :
  ¬ ConflictFree (inlineTree A) M.asStructure ∧ ¬ AltConflictFree A

/-- 4.9: for formulas that mention none of the block's role predicates, the slot premises add no consequence. -/
def oldEnv (A : AltDoc) : VE.Environment            -- E_base minus available, leads_to, inaction, taken, causes
theorem alternatives_conservative (A : AltDoc) (h : WellFormedAlt A = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (oldEnv A) []) (hφ : φ.WellFormed (oldEnv A) []) :
  (∀ B, BaseAdmissibleAlt A B → Sat B Γ → φ.denote B []) ↔
  (∀ B, BaseAdmissible (inlineTree A) B → Sat B Γ → φ.denote B [])

/-- The route, restated with BaseAdmissibleAlt and backgroundAlt (soft-norms 9.3 shape; W1's per-structure lemmas reused). -/
theorem alt_prefix_satisfaction (A) (h) (i) (hi : i ≤ size (inlineTree A)) (S) :
  PrefixAdmissibleAlt A i S ↔ S.Admissible (envAt (inlineTree A) i) ∧ BaseAdmissibleAlt A (restrictAll (inlineTree A).T S) ∧
    Sat S (PrefixPremises (inlineTree A) i)
theorem alt_conflictFree_prefix (A) (h) (r) (hr) (hc : AltConflictFree A) (S₀) (h₀ : PrefixAdmissibleAlt A (before (inlineTree A) r.name) S₀) :
  ConflictFreeAt (inlineTree A) r.name S₀
def altRoute (A) (h) (hc : AltConflictFree A) :
  { R : VE.Route.Layer VE.Route.fol Unit // R.E_in = envAt (inlineTree A) 0 ∧ (∀ B, R.Admissible_in B ↔ BaseAdmissibleAlt A B) ∧
    R.E_out = envAt (inlineTree A) (size (inlineTree A)) ∧ R.premises () = elaborate (inlineTree A).T }
theorem alt_route_backgroundSound (A) (h) (hc) : VE.Route.BackgroundSound (altRoute A h hc).1 (backgroundAlt A)
theorem alt_route_backgroundComplete (A) (h) (hc) : VE.Route.BackgroundComplete (altRoute A h hc).1 (backgroundAlt A)
theorem alt_route_acceptance (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree A)
    (Γ : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (accepted : VE.Tableau.checkCertificate (envAt (inlineTree A) (size (inlineTree A)))
                  (backgroundAlt A ++ elaborate (inlineTree A).T ++ Γ) φ c = true) :
  (∀ S : VE.Structure, S.Admissible (envAt (inlineTree A) (size (inlineTree A))) → VE.Norms.holdsCatala (inlineTree A).T S →
     VE.Norms.definitionsHold (inlineTree A) S → VE.Norms.profileHold (inlineTree A) S →
     Sat S (backgroundBase (inlineTree A)) → Sat S (altPremises A) → Sat S Γ → φ.denote S []) ∧
  ((∀ a ∈ Γ, a.WellFormed (envAt (inlineTree A) 0) []) → φ.WellFormed (envAt (inlineTree A) 0) [] →
     ∀ B : VE.Structure, BaseAdmissibleAlt A B → Sat B Γ → φ.denote B [])
theorem alt_route_countermodel (A : AltDoc) (h) (hc : AltConflictFree A) (Γ) (φ)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (inlineTree A) 0) []) (hφ : φ.WellFormed (envAt (inlineTree A) 0) [])
    (B : VE.Structure) (hB : BaseAdmissibleAlt A B) (hs : Sat B Γ) (hn : ¬ φ.denote B []) :
  ∃ S, DocumentExpansion (inlineTree A) B S ∧ Sat S (altPremises A) ∧ Sat S Γ ∧ ¬ φ.denote S []

/-- The wire (norms.md 11.4 shape). `decodeAltSource` decodes the environment with its block, the norm objects with
    profile-word guards, and the active base units; `res.src.A` is the decoded AltDoc. -/
theorem alternatives_wire_conflict_sound (j : Json) (res : AltConflictReplay) (h : replayAltConflict j = .ok res)
    (hv : res.conflictFree = true) :
  Wire.decodeAltSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
    WellFormedAlt res.src.A = true ∧ AltConflictFree res.src.A
theorem alternatives_wire_followable_sound (j : Json) (res : FollowableReplay) (h : replayFollowable j = .ok res)
    (hv : res.followable = true) :
  Wire.decodeAltSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
    WellFormedAlt res.src.A = true ∧ AltConflictFree res.src.A ∧
    ∀ B, BaseAdmissibleAlt res.src.A B → Sat B res.src.A.Γ →
      ∀ S, DocumentExpansion (inlineTree res.src.A) B S → FollowableIn res.src.A S
theorem alternatives_wire_dilemma_sound (j : Json) (src : Wire.AltSource) (w : DilemmaData src)
    (h : replayDilemma j = .ok ⟨src, w⟩) (hw : w.dilemma = true) :
  Wire.decodeAltSource (j.getObjValD "environment") (j.getObjValD "document") = .ok src ∧
    WellFormedAlt src.A = true ∧ AltConflictFree src.A ∧
    validateAlternatives src.A w.M w.rows = .ok () ∧ w.M.inDomain src.A.alt.chooser w.r ∧
    (notFollowableF src.A).eval w.M (tupleVal [w.r]) = true ∧
    ¬ (∀ B, BaseAdmissibleAlt src.A B → Sat B src.A.Γ → (allFollowable src.A).denote B [])
theorem alternatives_wire_acceptance (j : Json) (r : AltEntailmentReplay) (h : replayAltEntailment j = .ok r)
    (hv : r.valid = true) :
  Wire.decodeAltSource (j.getObjValD "environment") (j.getObjValD "document") = .ok r.src ∧
  (∀ S : VE.Structure, S.Admissible (envAt (inlineTree r.src.A) (size (inlineTree r.src.A))) →
     VE.Norms.holdsCatala (inlineTree r.src.A).T S → VE.Norms.definitionsHold (inlineTree r.src.A) S →
     VE.Norms.profileHold (inlineTree r.src.A) S → Sat S (backgroundBase (inlineTree r.src.A)) →
     Sat S (altPremises r.src.A) → Sat S r.premises → r.conclusion.denote S []) ∧
  (AltConflictFree r.src.A →
     (∀ a ∈ r.premises, a.WellFormed (envAt (inlineTree r.src.A) 0) []) → r.conclusion.WellFormed (envAt (inlineTree r.src.A) 0) [] →
     ∀ B : VE.Structure, BaseAdmissibleAlt r.src.A B → Sat B r.premises → r.conclusion.denote B [])
theorem Run.alternatives_wire_acceptance (j answer : Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : Run.usesAltPath j = true) :
  ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
    Run.AltAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer
```

The dilemma wire theorem carries `AltConflictFree src.A` because the executable computes followability only after a
CONFLICT-FREE result for the same source (4.6), and carries the successful validation of the witness with its rows
(`DilemmaData src` holds `M`, `rows` and `r`), so that `validate_sound` and `dilemma_expansion` apply to the replayed
data: for every expansion `S` with `restrictAll (inlineTree src.A).T S = w.M.asStructure`, the chooser has no clear
alternative in `S`. `AltAdmissionAnswer` is W1's `AdmissionAnswer` with the alternatives decoder, `alternatives:*`
leaves admitted only when equal to the regenerated premises, and the report consequence stated over `backgroundAlt
++ elaborate (inlineTree A).T ++ Γ_base ++` the four regenerated profile definitions. The graph checker types
profile-word claims over `extEnv A`.

Proof plan: `inline_faithful` by the capture-avoiding atom-substitution lemma under `S.Admissible A.E` (W3's
`faithful` is the model, not a dependency, so the W1×W3 gap is not on the path); `clear_denote` and
`followable_denote` from W1's `subst_sound` and `prefix_satisfaction` on `S` and `restrictAll (inlineTree A).T S` with
`inline_faithful`; `followable_sound` from those and `conflictFree_expands_document`; `dilemma_witness_sound` from
`eval_iff_denote`, `baseAdmissible_of_valid` extended by the slot premises, and the document iff; `dilemma_expansion`
from `followable_denote`; `scenarioConflict_sound` from W1's `conflict_witness_sound` and `conflict_pair_witness_sound`;
`alternative_monotone` by unfolding the three bodies on `extendAvailable`, with `A.alt.available ≠ A.alt.leadsTo`
from `WellFormedAlt` so that the `leads_to` atoms are untouched; `alternatives_conservative` by the
empty-relation expansion; the route theorems as W1's `Layer.lean` with `PrefixAdmissibleAlt`; the wire theorems by
W1's chain (decoder soundness → exact regeneration → binding equality → leaf admission → checker soundness). Every
proof audited under the unchanged allowlist.

### 7.3 The executable `ve_alternatives_route`

`lean/.lake/build/bin/ve_alternatives_route <cases.json>`, root `AlternativesMain.lean`, a new Lake target; `Run.main`
is the executable root and no frozen file changes. On raw input it runs the frozen envelope and profile gate, requires
`alternatives@0` and `norms@0` and rejects `soft-norms@0`, decodes the environment with its block through the W1
norms decoder plus a strict alternatives decoder (unknown fields rejected; the original complete environment hashed),
decodes the norm objects and active base units, runs `WellFormedAlt`, regenerates the inlined document, the slot
premises, `table_complete`, `Background_baseAlt`, `backgroundAlt`, the layer premises, every conflict target and the
followability formulas, validates bindings, and delegates every checker call to the unchanged W1 functions on the
regenerated data. Case kinds:

| Kind | Extra input | Output |
|---|---|---|
| `alt-elaborate` | none | `inlined` (the W1 document, canonical), `premises` (`alternatives:*`, `background`, `layer:norms:<p>`), `followable` (the closed formula and per-chooser `clear°`), `conflict_targets`, `unmapped_obligations`, `fragment`, `legend` |
| `alt-validate` | finite model with signed `outcomes` rows | `valid` or `InvalidModel("alternatives", …)`; on success, first the regenerated conflict formulas on the model: a true one is answered as that CONFLICT witness (classified as W1) with no per-chooser evaluation; otherwise the scenario evaluation of 4.7 with `model_id`, `assumed_harm_free`, `clear` or `no alternatives` per chooser, the diagnosis where `¬followable°` holds, and "also a dilemma witness" only with a CONFLICT-FREE result for the same source in the batch or by bound package (else `document followability not computed`) |
| `alt-conflict` | `packages` per target over `Background_baseAlt`, or `witness` | CONFLICT-FREE / CONFLICT (classified as W1) / UNKNOWN |
| `alt-followable` | `certificate` for `∀r. followable°(r)` over `Background_baseAlt ++ Γ_base`, or `witness` (model, signed rows, chooser); requires a CONFLICT-FREE result for the same source in the batch or by bound package | FOLLOWABLE (`conditional_on`) / DILEMMA (certified `¬followable°` on the validated witness, rendered diagnosis) / UNKNOWN / `not computed` |
| `alt-certificate` | `premises`, `conclusion`, `certificate` over `backgroundAlt ++ layer premises ++ premises` | `valid`, `background`, `layers`, `conditional_on` |
| `admission` | W2 document with norm units and cells, graph | `admitted`, `report`, `report_id`, `kinds`, `conditional_on` |

P0 and W1 cases without the block delegate unchanged to `Norms.Run.runCase`; malformed alternatives inputs never fall
back after a failed decode. Python's proof search consumes `alt-elaborate` output and returns certificates to
`alt-followable` and `alt-conflict`; Python holds no elaborator of its own.

### 7.4 What is not claimed

No theorem about the diagnosis: Lean certifies `¬followable°` at the witness chooser; NONE-PERMITTED, OVER-REQUIRED,
UNDISCHARGEABLE and JOINTLY-UNDISCHARGEABLE and the minimality of the listed set are properties of the untrusted
rendering. No completeness: UNKNOWN is honest, and the broader-class cost of 4.2 is documented, not repaired. No
theorem about the existence facts beyond `validate_sound`. No route-level conservativity for conclusions over
regulated predicates: `alternatives_conservative` covers formulas over `oldEnv`, and fixture r4's agreement between
the two routes is differential evidence. No theorem about the English surface (item 3). No claim
that the declared table is true, that the alternative list is complete, or that `clear` matches an author's intent:
that is this statement review and W8's fidelity gate. No claim about combination with `soft-norms@0`.

## 8. Acceptance fixtures for item 1

Deterministic, hand-written expected results; required from the Lean route and, for surface and dispatch, from
Python (`tests/test_alternatives*.py`, the `alternatives` conformance family). Section 8.1 states each fixture's rule
set, premises, model and verdict scope without its expected result; section 8.2 gives the expected results. The
statement review protocol (plan item 1): each reviewer derives the expectation of every fixture from 8.1 and sections
4 to 6 before reading 8.2.

### 8.1 Definitions

**Environment `asimov-v2`** (fixtures a–e, j, l–v unless stated): sorts `robot` (chooser), `action`, `harm`. Base:
`available(action, robot)`, `leads_to(action, harm)`, `inaction(action)`, `taken(action)`; `harms_human(harm)` "{0}
is a harm to a human being"; `harms_humanity(harm)`; `harm_to(harm, robot)` "{0} is a harm to {1}"; the annotator's
`ordered`, `protects_robot` ("{0} is protective"), `injures_human`, `injures_humanity` as in `environment.json`.
Regulated: `permitted(action)` permission allow-by-default, act `{0} be performed`; `required(action)` obligation
deny-by-default, dual `permitted`; `prevent_required(robot, harm)` obligation deny-by-default, act `{0} prevent
{1}`, fulfilment `avoids`. Block: chooser `robot`, action `action`, harm `harm`, `available`, `leads_to`,
`outcomes: signed`, `decided_by: "Asimov case annotator"`, `performed {permitted, required}`, `inaction`, `taken`.
One robot `R` with the listed alternatives; `nothing` is the inaction; every listed alternative is available to `R`
and to no one else; `taken` empty; `Γ_base` empty; no annotator classification unless stated; cells signed for every
(alternative, harm) pair, positive exactly where listed. Rule texts are 2.6; in every rule subset, `over` entries
naming absent rules are dropped (2.6), so {3, 7} has no precedence edge and only {1–6} keeps Asimov's chain.

| # | Rule set | Model (alternatives; harms; positive cells; facts) | Scope |
|---|---|---|---|
| a | {3, 7} | `nothing`, `pull`; h1 `harms_human`; `nothing`→h1 | scenario |
| b | A₀ {3, 7}; A₁ {3, 7} + fact `injures_human(pull)`; A₂ {3, 7′}; B {3, 8} | `nothing`, `pull`; h1, h2 `harms_human`; `nothing`→h1, `pull`→h2 | scenario each; document for A₁, A₂, B |
| b′ | (A) {3, 7, 9}; (A⁻) {3, 7, 9⁻}; (A5) {3, 5, 7, 9}; (A⁻5) {3, 5, 7, 9⁻}; (B) {3, 8c, 9_B} with and without `Γ_link` | for (A): scenario b with A₁'s fact; for (B) without `Γ_link`: `R` with `a₀` (`injures_human`, no positive cell), `a₁` (not injuring, `a₁`→h), `nothing` (inaction, `nothing`→h); h `harms_human`; for (B) also scenario b without classification | document; scenario |
| c | {3, 7}; {3, 8}; {3, 8⁻} | `nothing`, `pull`; h `harms_human`; `nothing`→h, `pull`→h | scenario; document for {3, 8⁻} |
| d | {1–6}; {3, 6′} | `shield`, `retreat`, `nothing`; hs with `harm_to(hs, R)`; `nothing`→hs; `protects_robot = {shield, retreat}` | document for {1–6}; scenario for {3, 6′} |
| e | {3, 7, 10} | `nothing`, `act`; hH `harms_humanity`, hp `harms_human`; `nothing`→hH, `act`→hp; fact `injures_human(act)` | document |
| j | {1–6} | `a₁`, `a₂`, `nothing`; no harms; `ordered = {a₁, a₂}`; nothing injures or protects | document |
| l | {3, 7} | l1: `nothing`, `wait` both inaction; l2: `taken = {nothing, pull}`; l3: `idle` inaction available to no chooser; l4: `R` with `pull` only, `inaction` declared and empty; l5: model c then `pull₂` added with no positive cell; l6: the `asimov-v2` block with `leads_to: "available"` (one predicate in two roles), no model | model; environment for l6 |
| m | {3, 7} | `a` available to `R1` and `R2`, inactions `n₁` (`R1`) and `n₂` (`R2`); then `a₁` to `R1` and `a₂` to `R2` in place of `a` | model |
| n | {3, 7, N} with `Rule N (exception to rule 7). Every action may be performed, if there is a robot such that that action is available to that robot and it is not the case that another action available to that robot may be performed.` | none | document |
| o | {3, 7}; {3, 8} | `nothing`, `act`, `rescue`; h `harms_human`; `nothing`→h, `act`→h | scenario |
| p | {3, 7} | p1: model a with the row (`pull`, h1) omitted, `signed`; p2: the same with `complete_by: "Asimov case annotator"` and the document stating its one positive cell as the unit `nothing leads to h1` (support `testimony`); p3: a W2 document with units `nothing is available to R`, `pull is available to R`, `nothing is inaction`, `h1 is a harm to a human being`, `nothing leads to h1` and the conclusion `nothing allows h1 to happen`, first without and then with `It is not the case that pull leads to h1.` (support `testimony`); p4: p3 without the negative unit under `complete_by`, plus the distinctness unit `It is not the case that pull is inaction.` (support `testimony`; with `nothing is inaction` it forces `pull ≠ nothing`); p5: p4 without the distinctness unit; p6: p2 with the row (`pull`, h1, `true`) supplied | model; document; model for p6 |
| q | any | q1: rule 9 with `if every other action available to that robot …` and no binder; q2: every wording of 2.1 and each construct of 2.6, including the short object form; q3: paraphrases of rules 7, 8, 9 and of the a and c situations | surface |
| r | any | r1: every existing fixture, identity, certificate and wire hash; r2: `asimov-v2` with and without the block; r3: a `norms@0`-only environment with a rule using `allows`; r4: `asimov-v2` with rules {1–6} only and the conclusion `every ordered action that may be performed must be performed`; r5: `asimov-v2` with rules {1–6} only, the premise `a₁ is ordered` and the conclusion `there is an action such that that action is ordered` (premise and conclusion over `oldEnv`) | identity; differential for r4 |
| s | s1: {3, 7}; s2: {3, 7, X} with `Rule X. Every action may be performed, if that action is inaction.`; s3: {3, 7} | s1: tableau and search budgets at zero; s2, s3: default budgets; no model | document |
| t | {3, 7, T} with `report_required(robot)` obligation deny, act `{0} file a report`, no fulfilment, `Rule T. Every robot must file a report.` | model a | scenario |
| u | {U} with `stand_down_required(robot)` obligation deny, act `{0} stand down`, fulfilment body `inaction(a)`; `recalled(robot)`; `Rule U. Every robot must stand down, if that robot is recalled.` | any valid scenario with `recalled(R)`; and the document | scenario; document |
| v | {3, 7} | the scenario report of a, replayed against model a without `pull`; against {3, 7′}; against a changed cell | binding |

**Environment `constitution`** (fixtures f, g, h): chooser sort `assistant`, `action`, `harm`; block as above with
`performed {permitted, required}` and `inaction`. f: `life_at_risk(assistant)`, `refers(action)`,
`gives_safety_information(action)`; `respond_required(assistant)` obligation deny, act `{0} respond to the risk to
life`, fulfilment `refers(a) ∨ gives_safety_information(a)`. g: `serious(harm)` (open). h: `proximate: causes`,
`harms_human`.

| # | Rule set | Model | Scope |
|---|---|---|---|
| f | {F1} | f1: `A` with `refuse`, `refer`, `answer`, `nothing`; `life_at_risk(A)`; `refers = {refer}`, `gives_safety_information = {answer}`; no harms. f2: `A` with `refuse`, `nothing` only. f3: the document with `Γ_ref` | scenario; document for f2 and f3 |
| g | {G1} | `answer`, `refuse`, `nothing`; h `serious`; g1: `answer`→h, `refuse`→h, `nothing`→h; g2: `answer`→h only | scenario |
| h | {H1, 7′}; {H1, 7} | `S`: `operate`, `wait`, `nothing`; hc, hd `harms_human`; `operate`→hc, `wait`→hd, `nothing`→hd; `causes = {(operate, hc)}`; h3: the same model with `causes = {(operate, hd)}` | document; model for h3 |
| i | none | a W2 unit asserting a counterfactual about a past choice, no block | coverage |
| k | none | U:5 "is the foundation of", U:7 "have resulted in" | coverage |

### 8.2 Expected results

Every rule set in a–k except b′(A⁻), b′(A⁻5) and s2 is CONFLICT-FREE by certificate (no positive and negative rule
select together; no pair conflict, `required` having no rule or rule 5 only where noted), so followability is
computed; for b′(A⁻), b′(A⁻5) and s2 it is `not computed`.

- **(a)** `avoidable(h1, R)` (via `pull`); `allows(nothing, h1)`; rule 7 selects at `nothing`: not permitted; `pull`
  permitted by default, nothing required. Scenario: `R has a clear action: pull`; `nothing` is not clear (rule 7).
- **(b)** A₀: `pull` permitted and clear: `R has a clear action: pull`, no dilemma. A₁: rule 3 forbids `pull`, rule
  7 forbids `nothing`: NONE-PERMITTED; the model passes validation, so document DILEMMA for {3, 7}, witness the A₁
  model, its fact listed under `narrowings` (annotator). A₂: rule 7′ forbids both (`allows(nothing, h1)`,
  `allows(pull, h2)`): NONE-PERMITTED, document DILEMMA for {3, 7′}. B: `prevent_required(R, h1)` and
  `prevent_required(R, h2)` both hold (each avoidable); both alternatives permitted, none required;
  `avoids(pull, h1)` but not `(pull, h2)`, `avoids(nothing, h2)` but not `(nothing, h1)`: no clear action;
  diagnosis JOINTLY-UNDISCHARGEABLE(`prevent_required(R, h1)`, `prevent_required(R, h2)`); document DILEMMA for
  {3, 8}. The model distinguishes A₀ from B and not A₁ or A₂ from B; the IDE says so and names o.
- **(b′)** (A) {3, 7, 9}: FOLLOWABLE by certificate: for a chooser with an alternative that neither injures nor is
  an inaction allowing a human harm, that alternative is permitted by default; otherwise every alternative injures
  or is such an inaction, so for each alternative every other one satisfies rule 9's disjunct and rule 9 permits it.
  On scenario b with A₁'s fact both alternatives are permitted (rule 9 yields at each) and clear; the report says
  the source does not settle the tie and lists rule 9 under `narrowings`. (A⁻) {3, 7, 9⁻}: CONFLICT, witness a
  chooser whose every alternative injures a human being: at each alternative rule 3 selects negatively and rule 9⁻
  positively (every other alternative injures), with no precedence edge between them (rule 3's `over` names the
  absent rule 2 and is dropped; rule 9⁻ is over rule 7 only), the shape of norms.md fixture i(b); followability `not
  computed: conflict status CONFLICT`. (A5) {3, 5, 7, 9}: document
  DILEMMA, witness j (OVER-REQUIRED). (A⁻5) {3, 5, 7, 9⁻}: CONFLICT at the witness of A⁻, which rule 5 leaves in
  place (it selects on `required` only and carries no `over` entry, so rules 3 and 9⁻ still select together on
  `permitted` with no edge between them); followability `not computed: conflict status CONFLICT`, and the
  OVER-REQUIRED dilemma of A5 is never reached. (B) {3, 8c, 9_B} with `Γ_link`: FOLLOWABLE, `conditional_on: Γ_link` (an
  alternative leading to no human harm discharges every prevention duty and is permitted unless it injures, in
  which case by `Γ_link` it leads to a harm, contradiction; if every alternative leads to a human harm the carve-out
  silences rule 8c and rule 9_B or the default permits one); without `Γ_link`: document DILEMMA at the stated
  witness, diagnosis UNDISCHARGEABLE(`prevent_required(R, h)`) with the rendering "`a₀` would discharge it but is
  forbidden by rule 3". On scenario b (no classification) under {3, 8c}: the carve-out holds for both harms, no duty,
  both clear.
- **(c)** `avoidable(h, R)` false, `unavoidable(h, R)` true, neither alternative allows or prevents h. {3, 7} and
  {3, 8}: both permitted and clear, `R has a clear action: nothing, pull`. {3, 8⁻}: `prevent_required(R, h)` holds
  and no alternative avoids h: UNDISCHARGEABLE(`prevent_required(R, h)`), document DILEMMA; the IDE proposes the
  `avoidable` guard.
- **(d)** {1–6}: `shield` and `retreat` permitted (rule 1) and required (rule 6): OVER-REQUIRED, document DILEMMA
  (the README's stated approximation, now visible). {3, 6′}: `prevent_required(R, hs)` holds; `shield` and `retreat`
  avoid hs, `nothing` does not: `R has a clear action: shield, retreat`.
- **(e)** rule 10 forbids `nothing` (`allows(nothing, hH)` via `act`); rule 3 forbids `act`: NONE-PERMITTED,
  document DILEMMA for {3, 7, 10}; rule 7 does not fire (`nothing` leads to no human harm). No exception is in the
  source; any positive exception is a narrowing.
- **(f)** f1: `respond_required(A)` holds; `refer` and `answer` discharge it, `refuse` and `nothing` do not; all
  permitted; `A has a clear action: refer, answer`. f2: UNDISCHARGEABLE(`respond_required(A)`), document DILEMMA
  for {F1}. f3: FOLLOWABLE, `conditional_on: Γ_ref`.
- **(g)** g1: h unavoidable by A; both permitted and clear. g2: `allows(answer, h)`: `answer` forbidden; `refuse`
  and `nothing` clear. The degree of counterfactual impact is open (the table is Boolean).
- **(h)** {H1, 7′}: `operate` forbidden by H1 (`causes(operate, hc)`) and by 7′ (`allows(operate, hc)`, since `wait`
  avoids hc); `wait` and `nothing` forbidden by 7′ (`allows(·, hd)`, since `operate` avoids hd): NONE-PERMITTED,
  document DILEMMA. {H1, 7}: `operate` forbidden, `nothing` forbidden (rule 7), `wait` clear: a "let die"
  resolution the source rejects (C:531); "more harm" needs a severity comparison, open. h3:
  `InvalidModel("alternatives", "operate causes hd but does not lead to it")`.
- **(i)** OPEN with reason `alternatives unstated`; never CHECKED.
- **(j)** `a₁`, `a₂` permitted (rule 2) and required (rule 5): OVER-REQUIRED, document DILEMMA for the unchanged
  Asimov document under the block.
- **(k)** W2 `causal` kind, LABELLED.
- **(l)** l1 `InvalidModel("alternatives", "R has two inactions: nothing, wait")`; l2 `"R has two taken actions:
  nothing, pull"`; l3 `"action idle belongs to no chooser"`; l4 `"R has no inaction"`; l5: h becomes avoidable,
  `allows(nothing, h)` and `allows(pull, h)` become true, the report's `alternatives_declared` lists `pull₂` among
  R's alternatives (one model cannot say which alternative was added; `alternative_monotone`, under `WellFormedAlt`,
  is the general claim). l6: `AlternativesSort: leads_to expects (action, harm)`, since `available` is declared
  `(action, robot)`: one predicate cannot serve two roles, which is the case `alternative_monotone`'s hypothesis
  excludes. l1–l5 from the Lean route; l6 from the block-shape check and the Lean route alike (6).
- **(m)** `InvalidModel("alternatives", "action a is available to two choosers: R1, R2")`; the split model accepted.
- **(n)** `DependencyCycle: permitted` from Python and Lean; Python's English diagnostic carries `GuardOnOwnOutcome`
  with rule 9's guard and the sentence that the rewrite changes meaning.
- **(o)** {3, 7}: `nothing` forbidden; `act`, `rescue` clear. {3, 8}: `prevent_required(R, h)` holds; `rescue`
  alone avoids h; `act` permitted but not clear; `rescue` clear. Both `R has a clear action`; recorded as the
  distinguishing model of the reading set {A, B}.
- **(p)** p1: `InvalidModel("alternatives", "outcome of pull for h1 unstated")`. p2: accepted (the regenerated
  premise `∀a h. leads_to(a, h) → a = nothing ∧ h = h1` holds on the rows); `avoidable(h1, R)`; `assumed_harm_free:
  pull/h1 (Asimov case annotator)`; the scenario report and any certificate using the cell say `conditional_on:
  alternatives:table_complete`; the document hash covers the unit `nothing leads to h1` and no row. p3 without the
  negative unit: the conclusion is refuted by the countermodel in which `pull` leads to h1; with it: proved,
  `counterfactual_leaves` lists `nothing leads to h1` and `It is not the case that pull leads to h1.` with their
  supports (the two cells exclude `pull = nothing`). p4: proved, `conditional_on: alternatives:table_complete`, the
  premise listed as an assumption of the annotator, the distinctness unit under `counterfactual_leaves` beside the
  cell. p5: refuted by the countermodel in which `pull` and `nothing` denote one element (constants may alias,
  implementation.md): the single alternative leads to h1, `table_complete` and every unit hold, `avoidable(h1, R)`
  is false, so `nothing allows h1 to happen` is false. p6: `InvalidModel("alternatives", "premise
  alternatives:table_complete fails")`: the positive row `pull`/h1 is not a document cell; the premise and the
  document hash are unchanged by the row.
- **(q)** q1 rejected ("that robot" has no antecedent) with the `there is a robot such that` rewrite. q2: exactly one
  derivation per wording and construct; the short object form is accepted only if it has one, else rejected with
  the long-form rewrite. q3: the paraphrases of 2.1 with the a situation (rule 7 decides) and the c situation
  (h unavoidable, rule 7 silent); rule 9's paraphrase says "the robot that can take it".
- **(r)** r1 unchanged byte for byte. r2: `environment_id` differs only with the block. r3: rejected as today
  (`UnknownSymbol: allows`). r4: CONFLICT-FREE and the entailment's status identical to `ve_norms_route`'s, as
  differential evidence only: the conclusion mentions `permitted` and `required`, outside `oldEnv`, so
  `alternatives_conservative` does not cover it (4.9, 7.4). r5: proved on both routes, each by a certificate bound to
  that route's own environment and regenerated premise list (the block changes `environment_id`, r2, and this route
  adds the slot premises), the two certificates proving the same conclusion and never compared;
  `alternatives_conservative` is the theorem behind the agreement of the two verdicts, the premise and conclusion
  being over `oldEnv`, and says nothing about certificate identity.
- **(s)** s1: conflict status UNKNOWN, followability `not computed: conflict status UNKNOWN`. s2: CONFLICT (rule X
  permits and rule 7 forbids an inaction that allows a human harm), `not computed: conflict status CONFLICT`. s3:
  computed.
- **(t)** `R has a clear action: pull; unmapped obligations: report_required (file a report)`; the FOLLOWABLE and
  DILEMMA texts for this rule set list the same.
- **(u)** every valid scenario with `recalled(R)` and at least one alternative of R: `R has a clear action:
  nothing` (E2 gives the inaction, which is permitted by default and discharges the duty); with no alternative of
  R: `no alternatives at R` (E2 admits such a chooser; `followable(R)` is vacuous). Document: no certificate (a
  structure with `recalled(r)`, an alternative and no inaction refutes the claim) and no valid witness (E2):
  UNKNOWN with the note naming E2.
- **(v)** all three replays rejected as stale; no scenario report contains unqualified FOLLOWABLE.

### 8.3 Regression suites

norms.md 10.1 repeated on documents carrying the block (identical statuses, witnesses, premise lists plus the four
slot premises); 10.6 to 10.10 repeated with the new wordings and fields (surface round trip with metadata; every
existing identity unchanged; certificate binding against a changed rule, cell, block field, fulfilment, `Γ_base`
unit or model; DAG diagnostics on the inlined tree); the Lean `alt-elaborate` output round-trips through Python's
dispatch and its certificates replay in Lean on 1,000 generated alternatives documents; every `InvalidModel` text of
section 6 produced by the Lean route on a hand-written model.

## 9. Limits, regeneration, Rust

Rules ≤ 256, regulated predicates ≤ 64, fulfilments ≤ 16, precedence depth ≤ 16, carve-outs ≤ 8 per rule (none
derived), each inlined formula within `MAX_NODES` (10,000 nodes, `ve/limits.py`); the followability witness search
uses the existing bounds and `MAX_EVALUATIONS` per chooser; every overflow is `ResourceLimit` with the limit named,
never a truth value. The inlined document, the slot premises, `table_complete`, the followability formulas and every
package are regenerated from the decoded units and declarations at every trusted site (norms.md 11.3); a finite
model supplies base tables and signed rows, and a supplied regulated or profile-word table is rejected as in W1.
Python holds no elaborator: its proof search runs on `alt-elaborate` output. Rust never elaborates: on the
`elaborated-document` family an alternatives case carries the Lean-generated inlined premises marked `untrusted:
true`, and its verdict must agree with Lean's (regression evidence; the trust path is Lean). Under
`VE_AUTHORITY=python` every operation of this route is `CheckerUnavailable`, never a verdict
(SEMANTICS-MIGRATION-PLAN 6).

## 10. Statement review checklist (Astra + Fable, before items 2 and 3)

1. The block (1.1), fixed argument orders and verbalisations, ownership (1.2), fulfilments and the mapped/unmapped
   distinction (1.3), the two outcome modes (1.4) and the `table_complete` premise (4.4).
2. The slot premises and `BaseAdmissibleAlt` used in every statement of 7.2; existence facts E1–E3 as validation
   only; the broader-class sentence and its named cost (4.2, fixture u): acceptable?
3. The four definitions and inlining (4.3); `inline_faithful` without a W3 dependency; `owner_unique`;
   `alternative_monotone` and the non-claim for `clear`.
4. `clear` and `followable` (4.6): is `clear` the intended reading of "complies with the mapped obligations and the
   declared action constraints"? Is `unavoidable`'s existence conjunct wanted? The gate on CONFLICT-FREE.
5. The verdict-scope table and the diagnosis procedure (4.6): Lean certifies `¬followable°`; the classification,
   minimality and per-alternative reasons are report properties (Fable round 3's precision point, resolved choice
   11.5).
6. Scenario evaluation bound to the model and never FOLLOWABLE (4.7, fixture v).
7. `GuardOnOwnOutcome` as an author-selected change with its sentence (4.8); the `there is a robot such that`
   binder (2.5).
8. Conservativity (4.9) and the ROADMAP trust-cost line.
9. The English table (2.1): one reading per wording; the three synonyms; the rejected wordings; the short object
   form's status; the `available to` constructs.
10. The diagnostics (6) and the fixtures: each reviewer derives 8.2 from 8.1 first, then compares; disagreements are
    recorded before any expectation is edited.
11. The Lean statements (7.2) and the executable's case kinds (7.3), including the dilemma wire theorem's
    CONFLICT-FREE hypothesis.
12. The resolved choices of section 11.
13. **The repeated gate on draft 2** (statement review, round 3): the changed entries and their direct dependencies
    only, each reviewer checking the rewritten signatures themselves: the rule-subset rule (2.6, 8.1); b′(A⁻), the
    8.2 header and 11.16; p2, p4, p5, p6 and the row rule of 1.4/3.3; r4 as differential evidence and r5; u and the
    `no alternatives` branch (4.7, 5.2); the scenario conflict gate (4.7, 7.3); the argument orders, the carrier
    rule, `inline_faithful`, `owner_unique`, `alternative_monotone`, `clear_denote`, `followable_denote`,
    `dilemma_witness_sound`, `dilemma_expansion`, `validate_sound`, `ExistenceFacts … rows` and the dilemma wire
    theorem (7.1, 7.2); the reserved names and the absence of fulfilment atoms (4.1(2), 4.3). Unchanged fixtures
    need no fresh derivation unless an edit changes an assumption they use. Draft 3 adds to the gate the four
    verification corrections (13): `alternative_monotone`'s `WellFormedAlt` hypothesis with the distinctness
    sentence of 4.1(2) and l6; r5's per-route certificates; b′(A⁻5) and the 8.2 header; the admissibility
    qualification of 4.3.

## 11. Resolved choices in this draft

Each is a point where the plan left a reading open; the review may overturn any of them.

1. **Fixed argument orders and canonical verbalisations for role predicates** (1.1), so that one reading per wording
   holds without a per-environment check and `risks`/`could lead to` cannot enter as a verbalisation. The plan
   assigned roles to the author's predicates without fixing either.
2. **`available(action, chooser)`**, matching `{0} is available to {1}`; the plan's draft 1 wrote `available(robot,
   action)`. Formal notation throughout follows the fixed order.
3. **A block-level `decided_by`** stands behind the counterfactual cells and, by default, `causes`; `unstated` is a
   checker-level value as in soft-norms; a W2 open-term declaration for `causes` overrides.
4. **`outcomes` is mandatory** (no silent default, as W1's `default`); scenarios supply signed rows; the
   `table_complete` premise is generated from the document's positive cells over constants and enters `Γ_base` as an
   attributed assumption. The alternative (documents always signed, completion only on scenarios) is weaker and was
   not chosen.
5. **Diagnosis versus verdict** (Fable round 3): Lean certifies `¬followable°` at the witness chooser; the
   classification is rendered by the untrusted evaluator with the procedure of 4.6; minimality is a report property;
   fixture c keeps UNDISCHARGEABLE as the single-duty case.
6. **`Γ_base` enters the followability certificate** under `conditional_on`, so an author premise (`Γ_link`, `Γ_ref`)
   can make a document certifiable; W1's conflict check stays over `Background_baseAlt` alone. Without this, b′(B)
   and f3 have no certificate.
7. **The `available to` constructs** (`every action`, `every other action`, `another action available to <chooser>`)
   and the `there is a <chooser> such that` binder are `alternatives@0` wordings with the formal effects of 2.1; the
   plan used them in rule texts without registering them.
8. **Profile words are also inlined in assertion units** (`h1 is avoidable by R`), so `Γ_base` is over `E_base`.
9. **Fulfilment bodies are base-only and inlined**, never W3 definitions, so the W1×W3 gap is not on the path; the
   `performed` obligation carries no fulfilment.
10. **`P ≠ ∅` in the diagnosis** relies on CONFLICT-FREE (a required, unpermitted alternative is a pair conflict
    point), which is one more reason for the gate of 4.6.
11. **Existence facts** are exactly E1–E3; nothing about `taken` beyond the premise and E1.
12. **The soft-norms combination** answers `UnsupportedProfile` on this route until the composition proof; the plan
    said "gated" without naming the answer.
13. **Scenario reports bind the P0 `model_id`**; dilemma packages bind the model id and the chooser.
14. **`GuardOnOwnOutcome` is an English-layer hint** on W1's shared `DependencyCycle` text (as `DualGuardCycle`),
    keeping Python and Lean diagnostic strings identical.
15. **Slot order**: `alternatives` follows `profile` in `ve/background.py` `HOOKS`, so `backgroundAlt` is
    definitions, literals, profile, alternatives; the certificate premise order is `backgroundAlt ++ layer premises
    ++ Γ`.
16. **Rule 9 is an exception to rules 3 and 7**, not to 7 alone: as an exception to 7 only, rule 9 and rule 3 both
    select at every alternative of a chooser whose alternatives all injure, with no precedence edge between them,
    so the document is CONFLICT and followability is not computed (fixture b′, A⁻); the plan's draft 1 attached it
    to rule 7 only.
17. **Rule subsets drop `over` entries naming absent rules** (2.6, 8.1), so that Asimov's rules can be cited
    verbatim in subsets without W1's `UnknownRule`; a subset's precedence graph is the listed rules' edges among
    themselves (statement review, Astra 1 and Fable 2).
18. **`clear` takes (chooser, action)**, the order of `ClearIn`, and every generated formula's context and
    evaluation tuple follow the argument-order convention stated once in 7 (statement review, Fable 3 and Astra 4);
    draft 1 wrote `clear(a, r)` and mixed the contexts.
19. **Carrier transport is explicit** (7): expansion-level statements are over `S` and `restrictAll (inlineTree A).T
    S`; `alternative_monotone` extends `S` on its own carrier; the expansion-level half of the dilemma claim is the
    corollary `dilemma_expansion` with the passage from the witness as a hypothesis (statement review, Astra 4 and
    Fable round 2).
20. **Constants may alias** (implementation.md), so fixture p4 states `pull ≠ nothing` through `It is not the case
    that pull is inaction.` beside `nothing is inaction`, and p5 keeps the aliased structure as the countermodel
    (statement review, Astra 2).
21. **The reserved-name diagnostic is `AlternativesReserved: <name>`** (4.1(2), 6), the environment-level
    counterpart of the surface registry's duplicate refusal (2.1), and the tree carries no fulfilment atoms
    (statement review, Astra 6 and Fable round 2).
22. **r4 is differential evidence**, not a consequence of `alternatives_conservative`, whose statement is over
    `oldEnv`; r5 exercises the theorem, each route with a certificate bound to its own environment and premise list
    (verification, Astra V2: the theorem relates verdicts, not certificates). A route-level conservativity statement
    for regulated conclusions was not added (statement review, Fable 5: either edit was acceptable; the smaller one
    was taken).
23. **`alternative_monotone` assumes `WellFormedAlt`** (verification, Astra V1): the theorem is about a well-formed
    block, whose role predicates are pairwise distinct (4.1(2)). The alternative, an explicit
    `A.alt.available ≠ A.alt.leadsTo` hypothesis, was not taken: well-formedness is what every other statement of
    7.2 assumes, the route establishes it before any theorem applies, and the distinctness of the other role pairs
    comes with it.

## 12. Statement review response (draft 1 → draft 2)

Sources: `manage-agents/debates/causation-spec/{astra,fable}.md` (rounds 1–3, FIX, CONVERGED after round 3; the
joint position is Fable's round-3 list of ten edits, the union of Astra 1–7 and Fable 1–6). No expected result
changed except b′(A⁻), p2 (document cell), p4 (distinctness unit) and u (qualification); the new fixtures are p5, p6
and r5.

| Item | Change in this draft | Where |
|---|---|---|
| Astra 1 = Fable 2 — rule subsets | `over` entries naming absent rules dropped; 8.1 says so | 2.6, 8.1, 11.17 |
| Astra 1 (round 2) — b′(A⁻) is CONFLICT | expectation CONFLICT, followability `not computed`; header lists A⁻ beside s2 | 8.2, 11.16 |
| Astra 2 — p4 aliasing | distinctness unit in p4; aliased countermodel p5 | 8.1, 8.2, 11.20 |
| Astra 3 — p2 and document completion | p2's document states `nothing leads to h1`; positive rows within document cells else `premise alternatives:table_complete fails` (p6); rows never change premise or hash | 1.4, 3.3, 8.1, 8.2 |
| Fable 3 = Astra 4 — argument orders | fixed once; contexts `.reverse`; `tupleVal` in argument order; `clear(r, a)` | 4.6, 7, 7.1, 7.2, 11.18 |
| Astra 4 / Fable round 2 — Lean statements | `S.Admissible A.E` on `inline_faithful`; `WellFormedAlt` on `owner_unique`; carrier transport; `alternative_monotone` on `extendAvailable`; `dilemma_expansion` | 7, 7.1, 7.2, 11.19 |
| Astra 5 — validation evidence | `ExistenceFacts A M rows` with `RowsConsistent`; `validate_sound` over rows; the dilemma wire carries `validateAlternatives … = .ok ()` | 3.3, 7.1, 7.2, 6 |
| Astra 6 / Fable round 2 — namespaces | `AlternativesReserved`; no fulfilment atoms; `inline`, `inline_base`, `withDefinitions` over profile words only | 1.3, 4.1, 4.3, 6, 7.1, 7.2, 11.21 |
| Astra 7 = Fable 4 — scenario gating | conflict formulas evaluated on the model first; document DILEMMA from a scenario only on CONFLICT-FREE | 4.7, 5.1, 5.2, 7.1, 7.2, 7.3 |
| Astra 7 / Fable round 3 — empty choices | `no alternatives` branch; legend line 3 qualified; fixture u qualified | 2.3, 4.6, 4.7, 5.2, 8.2 |
| Fable 5 — r4 | differential evidence; r5 added | 4.9, 7.4, 8.1, 8.2, 11.22 |
| Fable 6 — wording | short object form marked on rule 9 and Γ_link; b(A₁) "witness the A₁ model"; l5 without "added" | 2.6, 8.2 |
| Process | the repeated gate covers the changed entries (10.13); the plan is synchronized in the same commit | 10, causation-PLAN.md |

## 13. Verification response (draft 2 → draft 3)

Source: Astra's read-only verification of draft 2 and plan draft 3 (`manage-agents/causation-verify1b-astra.final.md`,
FAIL: all ten statement-review fixes represented, four corrections, no objection to the plan's design questions). Each
correction is applied here and in plan draft 4 (its 9.2). No design changed and no expected result of an existing
fixture changed; the new fixtures are b′(A⁻5) and l6.

| Item | Correction in this draft | Where |
|---|---|---|
| Astra V1 — `alternative_monotone` | `hw : WellFormedAlt A = true` added: it makes the role predicates pairwise distinct, in particular `available ≠ leads_to`, so `extendAvailable` leaves `leads_to` unchanged; without it both roles may name one `p`, and adding `p(a, h)` to `p(a, r)` keeps ownership but removes avoidability. 4.1(2) states the distinctness; l6 is the rejected block; the plan's schema carries the hypothesis | 4.1(2), 7.2, 8.1, 8.2, 10.13, 11.23; plan 3, 5, 6 |
| Astra V2 — r5 | "the same certificate" withdrawn: the routes bind different environments (the block changes `environment_id`) and different regenerated premise lists, so r5 requires a separately bound certificate per route proving the same conclusion; `alternatives_conservative` accounts for the agreement of the verdicts and does not establish certificate identity | 8.2, 11.22; plan 5 (r) |
| Astra V3 — plan b′ | "Any of these plus rule 5: DILEMMA" narrowed to (A) and (B) plus rule 5: A⁻ plus rule 5 keeps the permission conflict between rules 3 and 9⁻, so followability stays `not computed`; fixture b′ gains (A⁻5) and the 8.2 header lists it | 8.1, 8.2; plan 5 (b′) |
| Astra V4 — inlining prose | "on any structure" qualified by admissibility (`S.Admissible A.E`), matching the signature of `inline_faithful` | 4.3; plan 3 |

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-28 | Draft 1 | Item-1 specification from plan draft 2: block with roles, fixed orders and verbalisations, ownership, fulfilments and mapped obligations, two outcome modes; the English table with the `available to` constructs, the binder and the negative-cell wording; wire form, signed rows, identity and package bindings; `WellFormedAlt`; slot premises, `BaseAdmissibleAlt`, existence facts and the broader-class sentence with its cost; definitions and inlining; `table_complete`; conflict over the extended background; `clear`, `followable`, the verdict-scope table, the gate on CONFLICT-FREE and the diagnosis procedure with JOINTLY-UNDISCHARGEABLE; scenario evaluation bound to the model; `GuardOnOwnOutcome` as an author-selected change; conservativity and the ROADMAP line; report, status text, residual lines; diagnostics; every item-2 theorem as a statement in W1's Lean conventions; fixtures a–v with definitions (8.1) separated from expectations (8.2); resolved choices. Spec only: no code, Lean or frozen contract changed. |
| 2026-09-28 | Draft 2 | The ten edits of the converged statement review (`manage-agents/debates/causation-spec/`, FIX), section 12: rule subsets drop `over` entries naming absent rules; b′(A⁻) is CONFLICT with followability not computed (8.2 header, 11.16); p4 gains a distinctness unit and p5 keeps the aliased countermodel; p2's document states its positive cell, a scenario's positive rows must lie within the document's cells (p6), rows change neither premise nor hash; argument orders fixed once with `clear(r, a)`; `S.Admissible A.E` on `inline_faithful`, `WellFormedAlt` on `owner_unique`, explicit carrier transport (`clear_denote`, `followable_denote`, `dilemma_expansion`, `extendAvailable`), `ExistenceFacts A M rows` with `RowsConsistent`, validation carried by the dilemma wire theorem; `AlternativesReserved` and no fulfilment atoms; `alt-validate` evaluates the conflict formulas first and a scenario failure is a document DILEMMA only on CONFLICT-FREE; the `no alternatives` branch, legend line 3 and fixture u qualified; r4 differential with r5 added; wording (short object form marked, b(A₁), l5). Checklist item 10.13 names the repeated gate. Spec only. |
| 2026-09-28 | Draft 3 | The four corrections of Astra's verification of draft 2 (`manage-agents/causation-verify1b-astra.final.md`, FAIL), section 13: `alternative_monotone` takes `WellFormedAlt A = true`, 4.1(2) states that the role predicates are pairwise distinct and fixture l6 rejects a block naming one predicate for two roles; r5 requires a separately bound certificate per route proving the same conclusion, not "the same certificate"; fixture b′ gains (A⁻5), CONFLICT with followability not computed, and the 8.2 header lists it; the inlining prose of 4.3 is qualified by admissibility. Resolved choices 11.22 and 11.23; the repeated gate (10.13) covers the four. Spec only. |
| 2026-09-28 | Implementation correction | Section 7.2 states the structural validity premise required for arbitrary `FiniteModel` and the premise-free decoded-scenario theorem; a build-time counterexample demonstrates why the original generic statement cannot hold. Section 3.2 and the W2 admission statement specify profile-word graph typing and regenerated definition leaves. Existing wire identities and frozen W1 contracts are unchanged. |
