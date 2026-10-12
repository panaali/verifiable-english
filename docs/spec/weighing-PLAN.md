# Weighing competing considerations (`weighing@0`): buildable plan

> Status: plan draft 1 (2026-10-12), branch `design/weighing` from `main` at `49de179e`. Research wave of
> 2026-10-12 (DRI). It is the plan for the design recommended in [docs/research/weighing.md](../research/weighing.md)
> (cited here as `research n`), which must be read first: it holds the evidence, the measured need, the prior art
> and the comparison of candidate designs. Planning only: no code, proof, test or generated file changed, and no
> model was called. Lean blocks below are the statements the batches prove. They were written against `main` at
> `49de179e` and against RD-9's branch `rd-9/integrate` (read 2026-10-12), but were **not elaborated**; WG-1 elaborates
> them in an untracked stub before any Lean batch starts, as RD-9's SC-0 did. Numbers are measured (the method is
> named beside each) or labelled *estimate*.
>
> Inputs: [soft-norms.md](soft-norms.md) (cited `soft n`), [soft-norms-PLAN.md](soft-norms-PLAN.md),
> [norm-defaults.md](norm-defaults.md), [lean/SOFT-NORMS.md](../../lean/SOFT-NORMS.md),
> [lean/NORMDEFAULTS.md](../../lean/NORMDEFAULTS.md), RD-9's plan `docs/spec/rd-9-soft-chain-PLAN.md` on
> `design/rd-9` and its build on `rd-9/integrate` (`LayeredEntail.lean`, `LayeredAdmission.lean`), [VISION.md](../../VISION.md)
> (the converged rule "elaborate by default", items 1, 2, 5 and 8), `lean/VE/SoftNorms/{Tree,Soften,Semantics}.lean`,
> `lean/VE/NormDefaults/{Premises,Layered,Evidence,Routes}.lean`, and the pinned constitution and UDHR pilots of
> run `20261012T1800Z`.

## 0. Summary

The constitution asks Claude to weigh: four values in an order that is "holistic rather than strict", costs against
benefits, operators' wishes against users' interests, and almost every "should" is a default that judgment can set
aside. VE already has the right stance for this (`soft-norms@0`, merged and proved): weighing is a set of **named open
decisions** (is this rule's exception met here? does the lower-ranked consideration outweigh the higher one here? has
this party switched the rule off?), and the checker certifies the *structure* around them, never the weighing itself.

This plan extends that stance in two directions, both inside VE's rules (one reading per sentence, plain English, Lean
owns meaning, conservative extension only, honest UNKNOWN):

1. **Constrain the open decisions** (`weighing@0`, batches WG-2 to WG-5). Four kinds of sentence the constitution uses
   and soft norms cannot say become one-reading English, each elaborated into a labelled base premise on an open
   decision, appended to the extra premises `X` that RD-9 makes generic on the layered route. No new semantics:
   `ValueSoft`, `soften` and `fill` are unchanged, and every existing check, certificate and theorem applies.
   - **Strength of a rank edge**: "Safety always outranks ethics." (never outweighed) beside "Ethics generally
     outranks guidelines." (the holistic override, decided by the named decider).
   - **Conditions on an override**: "Helpfulness outweighs ethics on complying with an operator instruction only
     when …" (necessary) or "… when …" (sufficient), with factor lists.
   - **Conditions on a switch, and delegated switches**: "Users may turn off rule 7 only where the operator allows
     it." The checker also checks that a party never grants more than its own switches (:138, "operators cannot grant
     users more than operator-level trust").
2. **Say what the weighing decides, without doing it** (zone answers, batches WG-6 to WG-8). At a situation, for an
   act, Lean answers one of: **settled** whatever the open decisions are; **left to** a named decider, naming the
   questions the answer turns on; **not said** by the text (norm-defaults' gap); or **unknown** with the budget named.
   The same machinery checks a **decision record** (a decider's findings in one situation): admissible, with the
   outcome it produces, or ruled out by a named sentence of the document.

Two further pieces are **experiments** with pre-registered bars (WG-E1, WG-E2): whether collisions between
*different* acts ("help" against "refuse") need a new construct beyond act identification, and whether worked
examples can bind a decider as precedents (Horty's a fortiori constraint, compiled into the same decision
conditions). A holistic choice among explicit alternatives, numeric weights and a defeasible-logic engine inside the
checker are not planned (research 4, 5).

**The first batch that moves a pilot number** is WG-0: no product code, it writes the constitution's value order and
the hard constraints' immunity with what `soft-norms@0` already offers, once RD-9 lets a soft document sit beside
`norm-defaults@0` (RD-9 SC-8). Estimated unlock: 1.3 to 2.6 KB of the constitution (research 5.2, *estimate*).

## 1. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | Weighing stays a set of named open decisions with deciders. The checker certifies structure, bounds and coherence, and answers where the weighing matters; it never computes an "all things considered" verdict | VISION converged rule item 8 ("unconstrained weighing" is outside certification); soft 0; the source itself delegates the judgment ("we do want Claude to weigh these different priorities", :34) | an inside-the-checker weighing (numeric or argumentation-based), research 4.4 and 4.5 |
| D2 | A new profile `weighing@0` requires `soft-norms@0` and `norms@0`, with a new environment block `weighing` beside the vocabulary's `soft` block. `soft-norms@0`'s bytes, decoders, identities, statements and answers do not change; a document without the block is a soft document (WG-2 `weigh_conservative`) | VISION converged rule item 2 (meaning freeze; extensions are new profiles); soft 3.1's strict decoder rejects unknown fields, so the block cannot live inside `soft` | new fields in the `soft` block; a `soft-norms@1` |
| D3 | Every `weighing@0` construct is a **condition on an open decision**, elaborated into labelled base premises `Weigh_T`, appended after soft's own premises in the layered route's extra premises `X` (RD-9's `premisesX`, `EntailsX`, `acceptanceX`, `conflictFreeCheckX_sound`, `modelCheckX_sound`) | soft's exception conditions (`Exc_T`) are already this shape; RD-9 proves the checkers sound for any typed `X`; so the only new proof obligations are typing, the meaning of the premises and conservativity | changing `ValueSoft` or `soften`; a second premise pipeline |
| D4 | **Strength.** A declared edge "a outranks b" may carry `always` or `generally`. A rank pair `(H, L)` with `H` above `L` is **strict** when some chain of declared edges from `H` down to `L` contains an `always` edge, and **holistic** otherwise. A strict pair contributes `∀x̄. ¬outweighs_{a,L,H}(x̄)` for every act `a` on which the pair's rules collide | one rule a reader can apply ("a lower rank can outweigh a higher one only if every step between them says *generally*"); it is monotone both ways (`strictPair_down`, `strictPair_up`), so "safety always outranks ethics" also protects safety from guidelines and helpfulness | strictness per declared edge only (it would let guidelines outweigh safety while ethics cannot, research 4.1); strictness only on the first edge |
| D5 | `generally` needs the document's holistic flag (soft 1.2); under the strict flag it is rejected (`GenerallyUnderStrictOutranking`). `always` under the strict flag is accepted and inert, with a warning (`StrengthInert`). A plain "a outranks b" keeps the flag's meaning | under the strict flag no `outweighs` decision exists (soft 1.3), and creating one would change `E′`, so `soft-norms@0`'s vocabulary would change | creating `outweighs` atoms under the strict flag |
| D6 | **Override and switch conditions** have soft's exception-condition form: quantifier-free base formulas over the target's argument sorts, naming base predicates of `E` only; factor lists are strings with no premise | soft 3.2 and 6.1's fragment gate carry over unchanged, so `Weigh_T` stays in the universal function-free fragment | conditions over regulated or decision predicates (circular and outside the fragment) |
| D7 | **Delegated switches.** "<Party> may turn off rule n only where <grant>" is a necessary condition on `off_{n,party}`; a grant names its grantor, and the grantor must itself hold a switch on rule n (`DelegationExceedsGrantor`) and the grant's predicate must be attributed to the grantor (`GrantNotAttributed`) | :138; the bound is a structural check, decidable and stated as a theorem (`delegation_bounded`) | a general authority logic (research 4.6) |
| D8 | **Zone answers** reuse norm-defaults' three-valued machinery (Kleene evaluation, cones, bounded enumeration, `kleene_sound`, `settled_of_enumeration`) with the set of *open* atoms widened from the unsaid atoms to the unsaid atoms and the decision atoms. The widening is made once, in its owner file `NormDefaults/Evidence.lean`, with today's functions as the instance "open = unsaid" (`rfl`) | one owner of three-valued evaluation; norm-defaults' answers stay byte-identical | a second Kleene evaluator in `Weighing/`; Python enumeration |
| D9 | A zone answer separates **left to <decider>** (two admissible decision assignments, same filling, opposite outcomes) from **not said** (norm-defaults' UNDECIDED: same decisions, two fillings) and reports both when both hold. "Settled" is claimed only from a complete enumeration of the cone or a replayed certificate; anything else is UNKNOWN with its budget | the constitution sends "unclear or uncertain" hard-constraint cases to "holistic and nuanced prioritization" (:457): today those come out UNDECIDED, which reads as "the text does not say", the wrong message | one UNDECIDED for both |
| D10 | **Decision records** (a decider's findings in a situation) are checked with the zone machinery with the recorded atoms fixed: ADMISSIBLE with the outcome (and what is still open), RULED OUT with the first violated premise's label rendered as its sentence, or UNKNOWN | this is the one place a checker can audit a judgment it does not make: consistency with the document's bounds, not correctness | judging whether the finding is right |
| D11 | A new `ve_service` mode `weighing` decodes the block, regenerates `X = softLabelledU ++ weighLabelled`, and answers every layered kind (`-elaborate`, `-conflict`, `-status`, `-report`, `-certificate`, `admission`) by RD-9's layered dispatch with that `X`, plus two new kinds (`weighing-zone`, `weighing-record`). A `weighing@0` document is checked on the layered branch whether or not `norm-defaults@0` is on: with no unspecified predicate `fill U = U.D` and `Fill_T = []` (`fill_conservative`, merged) | one route for every `weighing@0` answer; no copy of the soft route | extending `ve_soft_norms_route` (meaning freeze) |
| D12 | English: each new wording has one reading and a deterministic paraphrase; decision predicates, labels and formulas never appear in what a reader sees (zero-training English). Wordings are registered where `soft-norms@0`'s are registered today (`ve/surface/registry.py` records, selected by `ve/norm_english.py` when the profile is on). If English-in-Lean moves norm wordings into the Lean catalogue first, they go there instead, never both | one owner per wording | symbols, rank numbers or weights in the text |
| D13 | No numeric weights, no "weigh" relation computed by the checker, no default inference inside the checker | research 4.4, 4.5; VISION converged rule item 5 | — |
| D14 | Cross-act collisions and precedents are **experiments first** (WG-E1, WG-E2), each with a pre-registered bar; a build follows only if the bar is met, through a new design batch | the need is unmeasured (research 2.4, 5.3) | building exclusive-act semantics now |

## 2. Design

### 2.1 What a `weighing@0` document is

A `weighing@0` document is a soft document (soft 1) whose environment carries a `weighing` block. Everything soft
requires still holds (soft 4.1), and the layered branch's well-formedness (`WellFormedU (soften D, unspec)`) holds; the
weighing checks come on top (2.5).

### 2.2 The English (one reading each; rejected as today when `weighing@0` is off)

| Wording | The one reading (the paraphrase the IDE shows) | Formal effect |
|---|---|---|
| `<Rank a> always outranks <rank b>.` | Where a rule serving <a> and a rule serving <b> collide on one act, the <b> rule never outweighs the <a> rule; the same holds for every rank below <b>. | declared edge `(a, b)`, strength `always`; `Str_T` premises (D4) |
| `<Rank a> generally outranks <rank b>.` | Where they collide, the <a> rule gives way to the <b> rule only where <decider> finds that the <b> consideration outweighs it there. | declared edge `(a, b)`, strength `generally` (holistic flag required, D5) |
| `<Rank l> outweighs <rank h> on <act phrase> only when <condition>.` | <decider> may find that the <l> consideration outweighs the <h> consideration on <act phrase> only in situations where <condition>. | necessary condition on `outweighs_{act,l,h}` |
| `<Rank l> outweighs <rank h> on <act phrase> when <condition>.` | Wherever <condition>, the <l> consideration outweighs the <h> consideration on <act phrase>. | sufficient condition on `outweighs_{act,l,h}` |
| `Whether <rank l> outweighs <rank h> on <act phrase> takes account of <consideration>[, <consideration>]*.` | These considerations bear on that finding; none is by itself decisive. | factors (no premise) |
| `<Party> may turn off rule n only when <condition>.` | Rule n's switch for <party> works only in situations where <condition>. | necessary condition on `off_{n,party}` |
| `<Party> may turn off rule n only where <grantor> allows it.` | <party>'s switch on rule n works only where <grantor> has allowed it; <grantor> must itself be able to turn rule n off. | grant: necessary condition on `off_{n,party}` over the grantor's attributed predicate (D7) |

The legend line for a grant's predicate is soft's `instruction_of` line ("<verbalisation> records an instruction of
<grantor>"). Wordings not in this table are not `weighing@0` wordings: "normally", "typically", "usually", "in most
cases" stay soft 2.2's reading sets (a default rule or a frequency claim), and "all things considered" has no
wording (it is the decider's judgment, D1).

**Paraphrase of a strict pair** (2.3 checklist, extended): "A <l> rule never outweighs a <h> rule: <h> always
outranks <m>, and <m> outranks <l>." The chain shown is the shortest one containing an `always` edge, in rank-name
order on ties (WG-2 `strictWitness`). **Paraphrase of a holistic pair**: "A <l> rule outweighs a <h> rule only where
<decider> finds so; every step between them says *generally*."

### 2.3 Wire form (environment vocabulary, identity-bound like `soft`)

```json
"weighing": {
  "strengths":  [{"edge": ["safety", "ethics"], "strength": "always"},
                 {"edge": ["ethics", "guidelines"], "strength": "generally"}],
  "conditions": [{"target": {"outweighs": {"act": "comply_permitted", "lower": "helpfulness", "higher": "ethics"}},
                  "kind": "necessary", "condition": ["unary", "emergency", ["var", 0]]}],
  "factors":    [{"target": {"outweighs": {"act": "comply_permitted", "lower": "helpfulness", "higher": "ethics"}},
                  "factors": ["how much the user would lose", "how severe the ethical cost is"]}],
  "grants":     [{"rule": "r7", "party": "user", "grantor": "operator", "predicate": "operator_allows_user_switch"}]
}
```

`edge` names a declared `soft.outranks` pair. `act` is soft's act key (soft 1.3). Every list is optional and defaults
to empty; the block is absent when empty. The canonical environment bytes include the block, so `environment_id`
changes when any entry changes and is unchanged for every environment without it (WG-3 `weigh_identity`). The
layered decoder receives the environment with the block and `weighing@0` removed (`stripWeighing`, a pure function),
and every certificate binds the **full** environment (2.6).

### 2.4 Elaboration: `Weigh_T`

```text
Str_T    for each (a, L, H) ∈ outweighsTriples(D) with strictPair(H, L):   ∀x̄. ¬outweighs_{a,L,H}(x̄)
                                                          label weigh:strength:<H>:<L>:<a>
Dec_T    for each condition c, in block order:
           necessary:  ∀x̄. target_c(x̄) → C(x̄)          label weigh:condition:<i>:necessary
           sufficient: ∀x̄. C(x̄) → target_c(x̄)          label weigh:condition:<i>:sufficient
Grant_T  for each grant g:  ∀x̄. off_{g.rule,g.party}(x̄) → g.predicate(x̄)   label weigh:grant:<rule>:<party>
Weigh_T  := Str_T ++ Dec_T ++ Grant_T
X        := softLabelledU(U, D) ++ Weigh_T              (soft's Exc_T and Coh_T first, as RD-9 orders them)
```

`outweighsTriples` is soft's (`Tree.lean:276`), so a strength premise exists only for an `outweighs` decision that
exists. A condition whose target names no existing decision is rejected (`NoSuchDecision`), never turned into a
fresh predicate.

### 2.5 Well-formedness (`WellFormedWeigh`), in order

1. The profiles contain `weighing@0`, `soft-norms@0` and `norms@0` (`UnsupportedProfile: weighing@0 requires
   soft-norms@0`); the block decodes (shape, field types, lists, sizes: at most 64 strengths, 128 conditions, 64
   factor entries of at most 16 strings of at most 200 bytes, 32 grants).
2. The stripped document passes `WellFormedSoft` and, under `norm-defaults@0`, `WellFormedU (soften D, unspec)`.
3. Each strength names a declared edge (`StrengthOnUndeclaredEdge: <a>, <b>`), at most once (`DuplicateDeclaration:
   strength <a>, <b>`); `generally` needs the holistic flag (`GenerallyUnderStrictOutranking: <a>, <b>`).
4. Each condition and factor target names an existing decision (`NoSuchDecision: <rendered target>`); a condition is
   typed over the target's argument sorts and mentions base predicates of `E` only (`InvalidInput: condition <i>
   mentions <q>`); it is quantifier-free after definition expansion (soft 6.1's gate).
5. Each grant: the rule exists and `party ∈ alterable(rule)` (`NoSuchDecision`); `grantor ∈ alterable(rule)`
   (`DelegationExceedsGrantor: rule <n>, <party>, <grantor>`); the predicate is a base predicate with
   `instruction_of = grantor` (`GrantNotAttributed: <predicate>, <grantor>`) and the rule's argument sorts.
6. Every generated premise, and `X` with the background as one checker types it, is within `MAX_DEPTH` and
   `MAX_NODES` (`ResourceLimit: generated weighing premise <label>`), computed before it is built (soft 8, "Accepted
   means elaborable").

Warnings: `StrengthInert: <a>, <b>` (D5). Diagnostic codes follow AR-13's scheme when it lands (DRI D6); until then
the texts above are the contract, identical in Lean and Python's display.

### 2.6 Zone answers and decision records

At a finite situation `M` (a base model over `E′_base` whose decision tables are ignored), for a regulated predicate
`r` and a typed tuple `v̄`, the **open atoms** are the decision atoms (every decision predicate of `E′` at every typed
tuple of `M`) and, under `norm-defaults@0`, the unsaid atoms. An **admissible completion** sets every open atom and
satisfies `X` and `Fill_T` on `M` (2.4). Lean answers:

| Answer | Meaning | Evidence |
|---|---|---|
| `settled <value>` | every admissible completion gives `<value>` | complete enumeration of the cone's open atoms under the budget (all assignments, admissible or not, agree), or a replayed certificate for `X ++ Fill_T ++ diagram(M) ⊢ outcome` |
| `left to <deciders>` | two admissible completions with the **same** filling and opposite values | the two completions, each checked by `modelCheckX`; the decision atoms on which they differ, rendered in document terms |
| `not said` | two admissible completions with the **same** decisions and opposite values | norm-defaults' witness, as today |
| `unknown <budget>` | none of the above within the budget (`MAX_OPEN_ATOMS`, 16 by default) | the budget named |

A **decision record** fixes some decision atoms (the decider's findings). The answer is the zone answer over
completions that agree with the record, or `ruled out by <label>` when a premise is refuted by Kleene evaluation with
the record fixed, rendered as that premise's sentence. "Assuming no exception applies" is the record that fixes every
`excepted` atom in the cone to false; the answer says so ("assuming no rule's exception applies here").

English (display only; Lean selects the rows): "Settled: whatever the assistant decides here, the text requires the
assistant to <act>." / "Left to the assistant: this depends on whether rule 12's exception applies here, and on
whether helpfulness outweighs ethics on complying with this instruction here." / "Not said: the text does not say
whether …" / "Unknown: more than 16 open questions bear on this point." / "Ruled out: this record finds that
guidelines outweigh safety here; the document says safety always outranks ethics, and ethics outranks guidelines."

### 2.7 What stays open (the residual, never certified)

The findings themselves (`excepted`, `outweighs`, `off`); whether a decider considered the listed factors; whether a
finding is wise; "the spirit of the document" (:44); which category a consideration falls under (:44, "it may be
unclear which category a given consideration falls under"), which stays a translator's reading set over a rule's rank;
collisions between different acts (until WG-E1); "best" responses among alternatives (research 4.7).

## 3. Lean statements

Names have prefix `VE.Weighing.`; soft names are `VE.SoftNorms.*`, norm-defaults names `VE.NormDefaults.*`, RD-9 names
as on `rd-9/integrate`. New files (D13 of RD-9's placement rule: a general definition goes in the file that owns its
special case; new `Weighing/*` files hold only what is specific to this profile):

| File | Contents | Batch |
|---|---|---|
| `lean/VE/Weighing/Tree.lean` | `Strength`, `CondKind`, `Target`, `CondDecl`, `FactorDecl`, `GrantDecl`, `WeighEnv`, `WeighDoc`, `strictPair`, `strictWitness`, `targetF`, `targetSorts` | WG-2 |
| `lean/VE/Weighing/Conditions.lean` | `strengthPremises`, `condPremise`, `grantPremise`, `weighLabelled`, `weighPremises`, `checkWeigh`, `WellFormedWeigh`, the theorems of 3.2 | WG-2 |
| `lean/VE/Weighing/Examples.lean` | `#guard` fixtures W-α to W-θ | WG-2 |
| `lean/VE/Weighing/Wire.lean`, `Run.lean` | block decoder, `stripWeighing`, `weighX`, the mode's dispatch, identity | WG-3 |
| `lean/VE/NormDefaults/Evidence.lean` (owner, extended) | `atomVO`, `coneAtomO`, `coneEvalO`, `coneValuesO`, `enumerateSettledO`, `table3O` with today's functions as the `opens = unsaidNames U` instances | WG-6 |
| `lean/VE/Weighing/Zone.lean`, `ZoneExamples.lean` | `decisionAtoms`, `AdmissibleCompletion`, `SettledZ`, `LeftToZ`, `zoneOf`, `recordCheck`, the theorems of 3.4 | WG-6 |
| `lean/ResponseShape/Schemas/Weighing.lean`, `Encoders/Weighing.lean` | the mode's row shapes and `runCaseReported_fits` | WG-3, WG-7 |
| `lean/WEIGHING.md` | every definition and theorem in plain words | WG-2, WG-3, WG-6 |

### 3.1 Definitions (WG-2)

```lean
namespace VE.Weighing
open VE.Norms VE.SoftNorms VE.NormDefaults
universe u

inductive Strength | always | generally
  deriving DecidableEq, Repr

inductive CondKind | necessary | sufficient
  deriving DecidableEq, Repr

/-- The open decision a condition constrains (soft 1.3). -/
inductive Target
  | outweighs (act lower higher : String)
  | off (rule party : String)
  deriving DecidableEq, Repr

structure CondDecl where
  target : Target
  kind : CondKind
  condition : VE.Formula            -- context (targetSorts target).reverse, base predicates of E only
  deriving DecidableEq, Repr

structure FactorDecl where
  target : Target
  factors : List String
  deriving DecidableEq, Repr

structure GrantDecl where
  rule : String
  party : String
  grantor : String
  predicate : String               -- a base predicate with instruction_of = grantor, over the rule's sorts
  deriving DecidableEq, Repr

structure WeighEnv where
  strengths : List ((String × String) × Strength)
  conditions : List CondDecl
  factors : List FactorDecl
  grants : List GrantDecl
  deriving DecidableEq, Repr

def WeighEnv.empty : WeighEnv := ⟨[], [], [], []⟩

structure WeighDoc where
  D : SoftDoc
  W : WeighEnv

/-- The declared edges below `a` reached through at least one `always` edge, with fuel `ranks.length`:
    `(H, L)` is strict when some chain of declared edges from `H` to `L` contains an `always` edge. -/
def strictBelow (Wd : WeighDoc) : Nat → String → List String
def strictPair (Wd : WeighDoc) (H L : String) : Bool :=
  (strictBelow Wd Wd.D.soft.ranks.length H).contains L

/-- The shortest chain containing an `always` edge, names ordered on ties; `none` when the pair is holistic. -/
def strictWitness (Wd : WeighDoc) (H L : String) : Option (List String)

def targetSorts (Wd : WeighDoc) : Target → List String
  | .outweighs a _ _ => actSortsOf Wd.D a
  | .off n _ => match Wd.D.T.nodes.find? (·.name == n) with
      | some N => sortsOf Wd.D N.pred
      | none => []

def targetF (Wd : WeighDoc) : Target → VE.Formula
  | .outweighs a L H => outweighsF Wd.D a L H
  | .off n π => match Wd.D.T.nodes.find? (·.name == n) with
      | some N => atom (offName N π) (sortsOf Wd.D N.pred)
      | none => .bottom

/-- `Str_T` (2.4). -/
def strengthPremises (Wd : WeighDoc) : List VE.Formula :=
  (outweighsTriples Wd.D).filterMap (fun (a, L, H) =>
    if strictPair Wd H L then some (bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H))) else none)

/-- `Dec_T` for one condition, as soft's `excPremisesOf`. -/
def condPremise (Wd : WeighDoc) (c : CondDecl) : VE.Formula :=
  match c.kind with
  | .sufficient => bindAll (targetSorts Wd c.target) (.implies c.condition (targetF Wd c.target))
  | .necessary  => bindAll (targetSorts Wd c.target) (.implies (targetF Wd c.target) c.condition)

def grantPremise (Wd : WeighDoc) (g : GrantDecl) : VE.Formula :=
  bindAll (targetSorts Wd (.off g.rule g.party))
    (.implies (targetF Wd (.off g.rule g.party)) (atom g.predicate (targetSorts Wd (.off g.rule g.party))))

/-- `Weigh_T` with its labels (2.4), in the order Str_T, Dec_T, Grant_T. -/
def weighLabelled (Wd : WeighDoc) : List (String × VE.Formula)
def weighPremises (Wd : WeighDoc) : List VE.Formula := (weighLabelled Wd).map (·.2)

/-- 2.5, steps 3 to 6, after `WellFormedSoft`; the diagnostics in that order. -/
def checkWeigh (Wd : WeighDoc) : Except String Unit
def WellFormedWeigh (Wd : WeighDoc) : Bool :=
  WellFormedSoft Wd.D && (checkWeigh Wd).isOk
```

### 3.2 Theorems (WG-2)

```lean
/-- D4: a strict pair is ordered. -/
theorem strictPair_outranks (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H L : String)
    (hs : strictPair Wd H L = true) : outranksPlus Wd.D.soft H L = true

/-- D4: an `always` edge is a strict pair. -/
theorem strictPair_of_always (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (a b : String)
    (hab : ((a, b), Strength.always) ∈ Wd.W.strengths) : strictPair Wd a b = true

/-- D4: strictness is inherited downward and upward along the order. -/
theorem strictPair_down (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H M L : String)
    (h₁ : strictPair Wd H M = true) (h₂ : outranksPlus Wd.D.soft M L = true) : strictPair Wd H L = true
theorem strictPair_up (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H M L : String)
    (h₁ : outranksPlus Wd.D.soft H M = true) (h₂ : strictPair Wd M L = true) : strictPair Wd H L = true

/-- D4: a holistic pair has an all-`generally` chain: every chain from `H` to `L` avoids `always` edges. -/
theorem holistic_iff_no_always_chain (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H L : String)
    (ho : outranksPlus Wd.D.soft H L = true) :
    strictPair Wd H L = false ↔
      ∀ chain, RankChain Wd.D.soft H L chain → ∀ e ∈ chainEdges chain, (e, Strength.always) ∉ Wd.W.strengths

/-- The meaning of `always`: in every structure satisfying `Str_T`, a higher effective default rule dominates a
    colliding lower default rule of a strict pair (no holistic override). Fixture W-α. -/
theorem always_dominates (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (strengthPremises Wd)) (M N : SoftNode) (hM : M ∈ Wd.D.T.nodes) (hN : N ∈ Wd.D.T.nodes)
    (hMd : M.mode = .default) (hNd : N.mode = .default) (hi : Incompatible Wd.D M N = true)
    (hh : higher Wd.D M N = true) (hs : strictPair Wd (rk M) (rk N) = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSorts Wd.D N) vs)
    (heff : EffD Wd.D S (tupleVal vs) (rankFuel Wd.D) M) :
    DominatedD Wd.D S (tupleVal vs) (rankFuel Wd.D) N

/-- ... and the lower rule never dominates the higher one by override. -/
theorem always_no_override (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (strengthPremises Wd)) (M N : SoftNode) (hM : M ∈ Wd.D.T.nodes) (hN : N ∈ Wd.D.T.nodes)
    (hMd : M.mode = .default) (hNd : N.mode = .default) (hi : Incompatible Wd.D M N = true)
    (hh : higher Wd.D M N = true) (hs : strictPair Wd (rk M) (rk N) = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSorts Wd.D N) vs) :
    ¬ OutweighsD Wd.D S (tupleVal vs) (act Wd.D N) (rk N) (rk M)

/-- Where every comparable colliding pair is strict, the holistic document decides exactly as the same document under
    the strict flag, on every structure satisfying `Str_T`. -/
theorem all_always_is_strict (Wd : WeighDoc) (h : WellFormedWeigh Wd = true)
    (hall : ∀ M N, (M, N) ∈ collidingPairs Wd.D → Comparable Wd.D M N = true →
      strictPair Wd (rk M) (rk N) = true ∨ strictPair Wd (rk N) (rk M) = true)
    (S : VE.Structure.{u}) (hS : Sat S (strengthPremises Wd)) (ρ : VE.Valuation S) (p : String) (sign : Bool) :
    DecidesSoftD Wd.D S ρ p sign ↔
      DecidesSoftD { Wd.D with soft := { Wd.D.soft with outranking := .strict } } S ρ p sign
  -- typed valuations only, as in soft's denotation lemmas; the stub fixes the typing hypothesis

/-- D7: a delegated switch works only where its grant holds. Fixture W-ζ. -/
theorem grant_needed (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (g : GrantDecl) (hg : g ∈ Wd.W.grants)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd (.off g.rule g.party)) vs)
    (hng : ¬ (atom g.predicate (targetSorts Wd (.off g.rule g.party))).denote S (tupleVal vs)) :
    ¬ (targetF Wd (.off g.rule g.party)).denote S (tupleVal vs)

/-- D7: no party is granted a switch its grantor lacks. -/
theorem delegation_bounded (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (g : GrantDecl) (hg : g ∈ Wd.W.grants) :
    ∃ N ∈ Wd.D.T.nodes, N.name = g.rule ∧ g.party ∈ N.alterable ∧ g.grantor ∈ N.alterable ∧
      (g.predicate, g.grantor) ∈ Wd.D.soft.instructionOf

/-- Typing: `Weigh_T` is a list of closed base formulas of the filled environment, so RD-9's `acceptanceX`,
    `conflictFreeCheckX_sound` and `modelCheckX_sound` apply to `X = softLabelledU ++ Weigh_T`. -/
theorem weighPremises_wellFormed (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : WellFormedU ⟨soften Wd.D, unspec⟩ = true) :
    ∀ a ∈ weighPremises Wd, a.WellFormed (envAt (fill ⟨soften Wd.D, unspec⟩) 0) []

/-- The fragment: every premise survives sort-respecting substructures (soft's gate, D6). -/
theorem weighPremises_substructure (Wd : WeighDoc) (h : WellFormedWeigh Wd = true)
    (B₀ B : VE.Structure.{u}) (hsub : BaseSubstructure Wd.D B₀ B) (hs : Sat B (weighPremises Wd)) :
    Sat B₀ (weighPremises Wd)

/-- D2: an empty block adds nothing. -/
theorem weigh_conservative (D : SoftDoc) : weighPremises ⟨D, WeighEnv.empty⟩ = []
theorem wellFormedWeigh_empty (D : SoftDoc) : WellFormedWeigh ⟨D, WeighEnv.empty⟩ = WellFormedSoft D
```

### 3.3 The route (WG-3)

```lean
namespace VE.Weighing

/-- The layered route's extra premises for a weighing document: soft's, then `Weigh_T`. -/
def weighX (Wd : WeighDoc) (unspec : List String) : List VE.Formula :=
  (VE.NormDefaults.Wire.softLabelledU ⟨soften Wd.D, unspec⟩ Wd.D).map (·.2) ++ weighPremises Wd

theorem weighX_wellFormed (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : WellFormedU ⟨soften Wd.D, unspec⟩ = true) :
    ∀ a ∈ weighX Wd unspec, a.WellFormed (envAt (fill ⟨soften Wd.D, unspec⟩) 0) []
  -- Wire.softLabelledU_wellFormed (rd-9/integrate, LayeredEntail.lean) ++ weighPremises_wellFormed

/-- Certified entailment on a weighing document: RD-9's acceptanceX at `weighX`. -/
theorem weigh_acceptance (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : WellFormedU ⟨soften Wd.D, unspec⟩ = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill ⟨soften Wd.D, unspec⟩) (size (fill ⟨soften Wd.D, unspec⟩)))
            (Wire.premisesX ⟨soften Wd.D, unspec⟩ (weighX Wd unspec) Γ) φ cert = true) :
    EntailsX.{u} ⟨soften Wd.D, unspec⟩ (weighX Wd unspec) Γ φ

/-- Conflict-freedom on a weighing document: RD-9's `conflictFreeCheckX_sound` at `weighX`. -/
theorem weigh_conflict_free (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : WellFormedU ⟨soften Wd.D, unspec⟩ = true) (certs : List (Option VE.Tableau.Certificate))
    (hc : Wire.conflictFreeCheckX ⟨soften Wd.D, unspec⟩ (weighX Wd unspec) certs = true) :
    Wire.ConflictFreeX.{u} ⟨soften Wd.D, unspec⟩ (weighX Wd unspec)

/-- Strength removes holistic weighing points from the conditional claim: a comparable colliding pair of a strict
    pair has its coherence conjunct implied by `Str_T` and the other premises (so it never appears in `conditional_on`
    for a lack of `outweighs` findings). -/
theorem strict_pair_coherent (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (M N : SoftNode)
    (hc : (M, N) ∈ collidingPairs Wd.D) (hcmp : Comparable Wd.D M N = true) (B : VE.Structure.{u})
    (hS : Sat B (strengthPremises Wd)) : (cohPremise Wd.D M N).denote B []
  -- already true without Str_T by `coh_rank_valid`; the statement review keeps it only if it adds a case

namespace Wire
/-- The block removed: the profile list without `weighing@0`, the vocabulary without `weighing`; every other byte
    of the environment is unchanged. -/
def stripWeighing (environment : Json) : Json
theorem stripWeighing_other (environment : Json) (k : String) (hk : k ≠ "weighing") :
    ((stripWeighing environment).getObjValD "vocabulary").getObjValD k =
      (environment.getObjValD "vocabulary").getObjValD k
end Wire

/-- The mode's answer on a case with no `weighing` block is the layered branch's answer, byte for byte. -/
theorem runWeigh_delegates (j : Json) (hb : Run.blockOf j = none) :
    Run.runCase j = VE.NormDefaults.Run.runCase j

/-- Identity: a certificate accepted on a weighing document is bound to the full environment, block included. -/
theorem weigh_identity (j : Json) (r : Run.Replay) (h : Run.replayCertificate j = .ok r) :
    r.environmentId = VE.NormDefaults.Wire.canonicalEnvironmentIdU (j.getObjValD "environment")
end VE.Weighing

-- lean/VE/Service/Protocol.lean (shared): one constructor, one dispatch arm, and
theorem VE.Service.runMode_weighing (j : Json) : runMode .weighing j = VE.Weighing.Run.runCaseReported j := rfl
```

`runWeigh_delegates` is what makes the profile conservative at the wire: the mode is a thin layer that adds premises,
never a second implementation of the layered branch.

### 3.4 Zone answers and records (WG-6)

In `NormDefaults/Evidence.lean` (the owner), beside today's definitions, each with today's function as an instance:

```lean
namespace VE.NormDefaults

/-- `atomV` with an explicit list of open base predicate names. -/
def atomVO (U : UDoc) (M : VE.FiniteModel α) (opens : List String) (tab : String → List α → Option Bool)
    (p : String) (vs : List α) : Option Bool :=
  if p ∈ layerNames (fill U).T then tab p vs
  else if p ∈ opens then none
  else some (decide (vs ∈ M.relations p))
theorem atomV_eq_open (U : UDoc) (M : VE.FiniteModel α) (tab) :
    atomV U M tab = atomVO U M (unsaidNames U) tab := rfl

/-- `coneAtom`, `coneEval`, `coneOf`, `coneAtoms`, `coneAtomV`, `coneValues`, `tabK`, `table3` likewise
    (`coneAtomO` … `table3O`), each with `<name>_eq_open : <name> … = <name>O … (unsaidNames U) …` by `rfl`. -/
def enumerateSettledO (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (fixed : List ((String × List α) × Bool)) (n : String) (vs : List α) : Option Bool
theorem enumerateSettled_eq_open (U : UDoc) (M : VE.FiniteModel α) (n : String) (vs : List α) :
    enumerateSettled U M n vs = enumerateSettledO U [] M (unsaidNames U) [] n vs
```

In `Weighing/Zone.lean`:

```lean
namespace VE.Weighing

/-- The decision atoms of a finite situation: every decision predicate of `D` at every typed tuple. -/
def decisionAtoms (D : SoftDoc) (M : VE.FiniteModel α) : List (String × List α)
def openNames (L : VE.NormDefaults.LayeredU) : List String := decisionNames L.D ++ unsaidNames L.U

/-- A completion of `M`: relations that agree with `M` off the open names and with the record on its atoms, and
    satisfy the layered premises `X` and `Fill_T`. -/
def AdmissibleCompletion (U : UDoc) (X : List VE.Formula) (M : VE.FiniteModel α) (opens : List String)
    (record : List ((String × List α) × Bool)) (R : String → List α → Prop) : Prop :=
  (∀ n vs, n ∉ opens → (R n vs ↔ vs ∈ M.relations n)) ∧
  (∀ a b, (a, b) ∈ record → (R a.1 a.2 ↔ b = true)) ∧
  Wire.BaseAdmissibleX U X { M.asStructure with relation := R }

def OutcomeIn (U : UDoc) (M : VE.FiniteModel α) (R : String → List α → Prop) (r : Regulated) (vs : List α) : Prop :=
  (outcomeBase (fill U) r.name).denote { M.asStructure with relation := R } (tupleVal vs)

def SettledZ (U X M opens record r vs) (b : Bool) : Prop :=
  ∀ R, AdmissibleCompletion U X M opens record R → (OutcomeIn U M R r vs ↔ b = true)

/-- Left to the deciders: two admissible completions that agree on every unsaid atom and differ in outcome. -/
def LeftToZ (U X M opens record r vs) (unsaid : List String) : Prop :=
  ∃ R₁ R₂, AdmissibleCompletion U X M opens record R₁ ∧ AdmissibleCompletion U X M opens record R₂ ∧
    (∀ n ∈ unsaid, ∀ ws, R₁ n ws ↔ R₂ n ws) ∧ OutcomeIn U M R₁ r vs ∧ ¬ OutcomeIn U M R₂ r vs

inductive ZoneAnswer (α : Type u)
  | settled (b : Bool)
  | leftTo (differ : List (String × List α)) (w₁ w₂ : List ((String × List α) × Bool))
  | notSaid (w₁ w₂ : List ((String × List α) × Bool))
  | ruledOut (label : String)
  | unknown (budget : String)

def zoneOf (L : VE.NormDefaults.LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (r : Regulated) (vs : List α)
    (proposed : List (List ((String × List α) × Bool))) : ZoneAnswer α
  -- `proposed`: completions found by the untrusted search; Lean checks each (modelCheckX), never trusts it

theorem zone_settled_sound (L : VE.NormDefaults.LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt L.U.D 0)) (hb : backgroundValid L.U.D M = true)
    (record) (r : Regulated) (hr : r ∈ L.U.D.T.regulated) (vs : List α)
    (typed : VE.TupleTyped M.asStructure r.sorts vs) (proposed) (b : Bool)
    (hz : zoneOf L X M record r vs proposed = .settled b) :
    SettledZ L.U X M (openNames L) record r vs b

theorem zone_leftTo_sound (L X M valid hb record r hr vs typed proposed differ w₁ w₂)
    (hz : zoneOf L X M record r vs proposed = .leftTo differ w₁ w₂) :
    LeftToZ L.U X M (openNames L) record r vs (unsaidNames L.U) ∧
    ∀ a ∈ differ, a.1 ∈ decisionNames L.D

theorem zone_notSaid_sound (L X M valid hb record r hr vs typed proposed w₁ w₂)
    (hz : zoneOf L X M record r vs proposed = .notSaid w₁ w₂) :
    VE.NormDefaults.UndecidedAtX L.U X
      { M.asStructure with relation := completionOf M record w₁ } r vs

/-- A record ruled out: no admissible completion agrees with it; the label is a premise of `X` or `Fill_T`
    that Kleene evaluation refutes with the record fixed. -/
theorem zone_ruledOut_sound (L X M valid hb record r hr vs typed proposed label)
    (hz : zoneOf L X M record r vs proposed = .ruledOut label) :
    ¬ ∃ R, AdmissibleCompletion L.U X M (openNames L) record R

/-- Today's norm-defaults status is the instance with no decision open and no record. -/
theorem zone_extends_status (U : UDoc) (M : VE.FiniteModel α) (n : String) (vs : List α) :
    VE.NormDefaults.enumerateSettledO U [] M (unsaidNames U) [] n vs = VE.NormDefaults.enumerateSettled U M n vs
```

`zone_settled_sound` is proved from the cone lemma (a Kleene-definite value under an assignment of the cone's atoms is
the value in every structure agreeing on them, `kleene_sound`) and the completeness of the enumeration over the
cone's atoms (`enumerate_all`, generalized); it does not need the completions to be admissible, so it is sound
whatever `X` excludes, and it may answer `unknown` where only `X` settles a point (as norm-defaults does today, sound).

## 4. Fixtures

### 4.1 Synthetic (hand-written expected results; `#guard` in Lean, the same through the service in Python)

Unless a fixture says otherwise, soft 10's frame: one sort `assistant`, act X with `x_required` (obligation,
deny-by-default, permission `x_permitted`) and `x_permitted` (permission, allow-by-default), situation `a`, guards `⊤`,
holistic flag, decider `the assistant`.

- **W-α (always).** Soft (α) plus `a always outranks b`. `Str_T = [∀x. ¬soft__outweighs__b__a__x_permitted(x)]`. Every
  admissible base has `H` alone selecting: `ValueSoft = some true`. The finite base with the `outweighs` atom true at
  `a` fails `modelCheckX` with label `weigh:strength:a:b:x_permitted`. Without the strength, soft (α)'s two answers.
- **W-β (closure).** Ranks `s > e > g > h`; `s always outranks e`, `e generally outranks g`, `g generally outranks h`.
  `strictPair`: `(s,e)`, `(s,g)`, `(s,h)` strict; `(e,g)`, `(e,h)`, `(g,h)` holistic. `strictWitness s h = [s, e, g,
  h]`. Colliding rules ranked `s` and `h` on X: no override; ranked `e` and `h`: override possible.
- **W-γ (flags).** The strict flag with `e generally outranks g`: `GenerallyUnderStrictOutranking: e, g`. The strict
  flag with `s always outranks e`: accepted, `StrengthInert: s, e`, `Str_T = []`.
- **W-δ (necessary override condition).** Soft (α), `a generally outranks b`, condition "b outweighs a on doing x
  only when urgent" (`urgent(x)` a base predicate). Zone of `x_required` at `a` with `urgent(a)` false: `settled
  yes`. With `urgent(a)` true: `left to the assistant`, differing on the one `outweighs` atom.
- **W-ε (sufficient override condition).** As W-δ with "b outweighs a on doing x when urgent": with `urgent(a)`
  true, `settled no` (L alone selects).
- **W-ζ (grant).** Strict `must X` on `x_required`, `alterable: [operator, user]`, grant (user, grantor operator,
  `operator_allows(x)` with `instruction_of: operator`). Zone at `a` with `operator_allows(a)` false: `settled yes`
  whatever the user's switch is; true: `left to` the operator and user switches. With `alterable: [user]` only:
  `DelegationExceedsGrantor: rule n, user, operator`. With `instruction_of: user` on the predicate:
  `GrantNotAttributed: operator_allows, operator`.
- **W-η (conservativity).** Every soft fixture α to υ under `weighing@0` with no block: the `weighing` mode's answers
  are byte-identical to the layered branch's (`runWeigh_delegates`); with `weighing@0` off, a `weighing` block is
  `UnsupportedProfile`. Every norm-defaults fixture's `-status` is byte-identical (`zone_extends_status`).
- **W-θ (diagnostics).** `StrengthOnUndeclaredEdge`, `DuplicateDeclaration: strength`, `NoSuchDecision` (an
  `outweighs` target on an act with no colliding pair), `InvalidInput: condition 0 mentions x_required`, a quantified
  condition (fragment gate), each grant diagnostic, `ResourceLimit: generated weighing premise <label>` on a
  condition of `MAX_NODES` nodes.
- **W-ι (identity).** Changing one strength, condition, factor or grant changes `environment_id`; a certificate
  replayed after the change is refused with the stale-binding text.
- **Z-α (left to).** Soft (δ), unranked weighing point: zone of `x_required` at `a` is `left to the assistant`, the
  two completions excepting `A` and `B` respectively; the coherence conjunct rules out the completion with neither
  excepted.
- **Z-β (record).** W-α with the record "b outweighs a on doing x here": `ruled out by weigh:strength:a:b:x_permitted`,
  rendered "the document says a always outranks b".
- **Z-γ (not said beside left to).** A default rule on an `unspecified` predicate whose exception is open
  (norm-defaults' u8 frame): zone where the exception may hold: `left to` on the exception and `not said` on the
  gap, both reported.
- **Z-δ (budget).** Seventeen open atoms in the cone: `unknown: more than 16 open questions`.
- **Z-ε (presumption).** Soft (ρ) with the record "assuming no exception applies": `settled yes` "assuming no
  rule's exception applies here"; without the record, `left to`.

### 4.2 From the constitution (real units, run `20261012T1800Z`)

The unit ids, spans and texts are in research 2.5. Each fixture records the VE sentences, the expected status, and
the zone answer where one applies; WG-5 and WG-8 check them through `ve document` on the pilot branch.

| Fixture | Source | VE sentences (shape) | Expected |
|---|---|---|---|
| C-1 | :34 value order (`u0019` in research 2.5) | soft 2.4's three `outranks` sentences, the holistic flag, decider "the assistant"; unit READINGS {A strict dominance, B open weighing carve-out, C ranks with the holistic flag} | WG-0: rank sentences CHECKED; flag OPEN; unit READINGS |
| C-2 | :40 "even if Claude is confident in its reasoning" | `Safety always outranks ethics.` beside `Safety generally outranks ethics.` (a reading set: :34 says the order is holistic, :40 says the safety step is robust) | WG-5: READINGS, both readings conflict-free |
| C-3 | :42 "Exceptions to this are any hard constraints … and any cases where Anthropic's guidelines overlap with broad safety" | the hard constraints are strict rules (already); guideline rules that overlap with safety carry rank safety (a narrowing per rule, attributed) | WG-5: OPEN (the overlap is an open classification) |
| C-4 | :138 "operators cannot grant users more than operator-level trust" | grants on the instructable-behaviour rules; `DelegationExceedsGrantor` shown as the checked content | WG-5: CHECKED where the rules are declared |
| C-5 | :405-423 instructable behaviours | default rules `(operators may turn off)` / `(users may turn off)` with grants where the source says "absent increased or decreased trust granted by operators" | WG-5: OPEN (each default's exception) |
| C-6 | :443 "cannot be unlocked by any operator or user" | soft's `hard: true` narrowing, cited once on the hard-constraint header | WG-0: CHECKED (`HardConstraintAltered` is the check) |
| C-7 | :457 "For cases that are more unclear or uncertain, we want Claude to be guided by the more holistic … prioritization" | each hard constraint's prohibition in the knowing-or-likely case (today's repair) beside a default "should not" for the unclear case, decided by the assistant | WG-8: zone `settled no` (knowing case), `left to the assistant` (unclear case) where today's probe says UNDECIDED |

## 5. Batches

Every batch is 2 to 6 hours for one builder and passes the lean-first gate (LEAN-FIRST-PLAN 5.1) as RD-9's batches do:
the full gate once on the final commit, selected tests while iterating, seeded bugs in each changed language
recorded with the failing test, `DELTA.md` with the corpus A/B by class, the deletion ledger, the frozen-inventory and
assurance-manifest updates (DRI D2), trust classes with any budget rise signed (DRI D3), `tools/lean_statements.py`
showing additions only, and `lean/audit.py`. New Python respects the layer map (DRI D5); new diagnostics take AR-13's
codes when they land (DRI D6); every identity is Lean's (DRI D7). Generated files are never edited by hand:
`ve/backends/lean_service_schema/weighing.json` by `tools/response_schemas.py --write`, `tools/gate-collection.json`,
`lean/checkers.lock` and the rest through `tools/regen_generated.py --write`.

| # | Batch | Hours | Owner | Needs | Pilot effect (*estimate*, research 5.2) |
|---|---|---:|---|---|---|
| WG-0 | The value order and the hard constraints' immunity with today's `soft-norms@0` | 3–4 | pilot | RD-9 SC-8 on `main`; SC-9's soft form adopted or on the same pilot branch | 1.3–2.6 KB of the constitution from UNFORMALISED to CHECKED/OPEN/READINGS |
| WG-1 | Statement review of section 3, elaborated in a stub; fixture values computed | 3–4 | planner | — | none |
| WG-2 | Lean: block, strength, conditions, grants, premises and their theorems | 5–6 | Lean | WG-1; `main` | none |
| WG-3 | Lean: wire, the `weighing` mode, shapes and encoder theorems | 5–6 | Lean | WG-2; RD-9 SC-1 and SC-6 on `main` | none |
| WG-4 | Python: surface records, relay, document dispatch, fuzz tests | 4–5 | Python | WG-3; RD-9 SC-8 on `main` | none |
| WG-5 | The constitution: strengths, conditions, switches and grants | 4–5 | pilot | WG-4, WG-0 | 3–8 KB (*estimate*) |
| WG-6 | Lean: zone answers and records (open atoms widened in their owner) | 5–6 | Lean | WG-3; RD-9 SC-A on `main` | none |
| WG-7 | Wire and display: `weighing-zone`, `weighing-record`, English, CLI | 5–6 | Lean, Python | WG-6, WG-4 | none |
| WG-8 | The constitution: zone probe on the hard constraints and the "should" sets | 3 | pilot | WG-7 | no coverage claim; answers recorded |
| WG-E1 | Experiment: do collisions between different acts need a new construct? | 4 | planner | WG-0 | decides WG-10 |
| WG-E2 | Experiment: can worked examples bind a decider as precedents? | 5–6 | planner | WG-2 | decides WG-9 |
| WG-9 | (only if E2 passes) Lean: precedents compiled into decision conditions | 5–6 | Lean | WG-E2, WG-3 | per E2's measurement |
| WG-10 | (only if E1 passes) design batch for exclusive acts | 3 | planner | WG-E1 | — |

**Order.** WG-1 and WG-E1's reading can start now; WG-2 needs only `main`. The constitution's path is WG-0 → WG-2 →
WG-3 → WG-4 → WG-5, then WG-6 → WG-7 → WG-8. About 38 to 47 builder-hours on the path (*estimate*, not evidence of
speed).

### WG-0. The value order and the hard constraints' immunity (pilot, 3–4 h)

On a pilot branch (`pilot/cc-<stamp>`), scripts under `usecases/claude-constitution-pilot/run-<stamp>/`, all at one
commit, in the foreground, host load recorded. No product code.

1. Start from RD-9 SC-9's probe translation (soft form of the four "should" sets) if adopted, else from the committed
   translation with `soft-norms@0` added through SC-8's path.
2. Declare the soft block: ranks `safety`, `ethics`, `guidelines`, `helpfulness`; the three `outranks` edges; the
   holistic flag decided by "the assistant" (soft 2.4's :34 reading C). The :34 unit becomes a reading set {A, B, C}
   (soft-norms-PLAN 4); the translator's narrowing to {B, C} is a separate attributed unit citing :34 "holistic rather
   than strict".
3. The :27-32 value list: the four rank names with their definitions as open-term declarations (`meaning: open`), the
   bytes of each definition counted to the term's schema as `factors` (soft-norms-PLAN 4); not CHECKED.
4. "Rule n serves <rank>" on every existing default rule whose rank the source cites (u0073.s05's rule serves
   helpfulness, citing :32), each a narrowing unit.
5. :443's "cannot be unlocked by any operator or user": `hard: true` on the hard-constraint rules, cited once on the
   header (soft-norms-PLAN 4, "split the units").
6. Check, render, measure: before and after at one commit, the measures of RD-9 SC-9's table plus `weighing_points`,
   `holistic_overrides`, the per-pair classification, and the bytes per status. Blind whole-span fidelity review of
   every changed unit before anything is counted (soft-norms-PLAN 4, C1); failures reverted.

Done when: the table is filled with measured values, `SUMMARY.md` and `metrics.json` report before and after, and
every refused sentence, UNKNOWN and failed review is listed rather than worked around. Deleted, not duplicated: none
(no product code). Shared files: none in the product repository.

### WG-1. Statement review (planner, 3–4 h)

Every definition and theorem of section 3 written in an untracked stub (`lean/SpecStubs_weighing.lean`) against the
build of `main` and of `rd-9/integrate`; each theorem as `def T : Prop := …` and the short ones proved; fixture values
of 4.1 computed with `#eval` where a stub can. Reviewed by Astra and Opus until converged (Fable arbitrates only an
unconverged debate). Questions for the review: D4's closure rule against per-edge strength; whether
`strict_pair_coherent` adds anything beyond `coh_rank_valid` (drop it if not); `all_always_is_strict`'s typing
hypothesis; whether `zone_settled_sound`'s enumeration may ignore admissibility (claimed sound, may be incomplete);
the wordings of 2.2 for one reading each. Done when the review has converged and this file carries its edits.

### WG-2. Lean: block, strength, conditions, grants (Lean, 5–6 h)

Files (new): `lean/VE/Weighing/{Tree,Conditions,Examples}.lean`, `lean/WEIGHING.md`. Shared: `lean/VE.lean`
(import), `lean/VE/Audit.lean` (audit entries for every theorem of 3.2), the frozen inventory and assurance manifest
(new files pinned).

Fixtures: W-α to W-θ as `#guard`s on the direct semantics and on the generated premises.

Deleted, not duplicated: no second premise generator (`condPremise` has soft's `excPremisesOf` shape but targets
decisions soft does not constrain; the statement review checks whether `excPremisesOf` can be stated as the
`.excepted` instance of one generator, and if so the generator moves to `SoftNorms/Soften.lean` with soft's statements
unchanged); no second rank closure (`strictBelow` reads soft's `directBelow`/`below`).

Done when: builds with no `sorry` and the allowed axioms only, `lean_statements.py` shows additions only, every
theorem is in `WEIGHING.md` in plain words, and the gate passes. No answer can change: nothing calls the new code.

### WG-3. Lean: wire and the `weighing` mode (Lean, 5–6 h)

Files (new): `lean/VE/Weighing/{Wire,Run}.lean`, `lean/ResponseShape/Schemas/Weighing.lean`,
`lean/ResponseShape/Encoders/Weighing.lean` (`runCaseReported_fits`). Shared: `lean/VE/Service/Protocol.lean` (one
mode constructor, one dispatch arm, `runMode_weighing`), `lean/VE/Audit.lean`, `lean/ResponseShape/Audit.lean`, the
profile registry read by the service (`VE/Service/Document.lean` and `ve/profiles.py`: one entry each, located with
`tools/repo_map.py file`), `ve/backends/service_schema.py` (`MODES` gains `"weighing"`). Generated:
`ve/backends/lean_service_schema/weighing.json` (`tools/response_schemas.py --write`).

The dispatch: decode the block, `stripWeighing`, decode the stripped source with the layered decoder, check
`WellFormedWeigh`, regenerate `weighX`, then answer the case's kind by RD-9's layered dispatch with `X := weighX`
(certificates through `bindCertX` with the full environment). No kind is reimplemented.

Fixtures: W-η through the service (byte-identical to the layered branch), W-ι, and W-α, W-δ, W-ζ's conflict and
certificate answers. Route-case fixtures recorded into `tests/data/route-cases.jsonl` by `tests/route_case_recorder.py`
and checked by `tests/test_route_row_schemas.py` (WG-4 adds the Python tests that record them).

Deleted, not duplicated: none; the mode is a premise layer over the layered branch. `repo_map.py --check` passes (one
mode, one schema).

Done when: the fixtures pass, `runWeigh_delegates` is proved, the corpus A/B is identical (no corpus document has the
profile), and the gate passes.

### WG-4. Python: surface, relay, documents (Python, 4–5 h)

Files (new): `ve/surface/weighing.py` (records for 2.2's wordings, profile-gated as soft's are),
`ve/weighing.py` (the relay: sends the case with `rows` from `ve/backends/relay.py`, checks schema and binding only,
R8), `tests/test_weighing_lean.py` (documents through the service), `tests/test_weighing_answer.py` (fuzz: each member
of a genuine answer dropped, emptied, retyped, duplicated, reordered, an index pushed out of range, one and two faults
at a time; every mutant `CheckerUnavailable` or showing nothing different). Shared: `ve/norm_english.py` (select the
new records when `weighing@0` is on), `ve/document.py` (a `weighing@0` document goes to the `weighing` mode; the
refusal text for unsupported combinations), `tests/test_english_unambiguity.py` (the new wordings), and the
regenerated `tools/gate-collection.json`.

English paraphrases: rendered from Lean's elaboration row (`strictWitness`, labels, targets) by display code only;
`tools/relay_lint.py` gains `weigh__`-free checks (no premise label or decision name in rendered text).

Deleted, not duplicated: Python builds no `Weigh_T`, no `strictPair`, no `X`; it renders Lean's rows.

Done when: the fixtures pass through `ve document load/check/render`, the fuzz tests pass, the unambiguity test covers
every new wording, and the gate passes.

### WG-5. The constitution: strengths, conditions, switches, grants (pilot, 4–5 h)

As WG-0 (pilot branch, one commit, blind review before counting). Translate C-2 to C-5 (4.2): the :38-44 safety
robustness sentences as the reading set {always, generally} on the safety edge with their citations; :42's exceptions;
the operator and user permission layering of :134-139 as switches and grants; the instructable-behaviour lists of
:405-423 as default rules with switches. Measure as WG-0. Required: one zone answer recorded for each new grant
(W-ζ's shape on a real rule), to show the grant bites. Done as WG-0.

### WG-6. Lean: zone answers and records (Lean, 5–6 h)

Files: `lean/VE/NormDefaults/Evidence.lean` (shared owner: the `*O` definitions and `*_eq_open` lemmas of 3.4; today's
functions become the instances, statements unchanged), `lean/VE/Weighing/{Zone,ZoneExamples}.lean` (new). Shared:
`lean/VE/Audit.lean`, frozen inventory and assurance manifest (Evidence.lean re-pinned, decoder code unchanged).

Fixtures: Z-α to Z-ε as `#guard`s; every norm-defaults `-status` fixture byte-identical (`zone_extends_status`).

Deleted, not duplicated: no second Kleene evaluator, cone or enumeration; the bodies of `atomV`, `coneAtom`,
`coneAtomV`, `coneValues`, `enumerateSettled` become one-line instances of their `*O` forms (ledger lines recorded).

Done when: builds, the theorems of 3.4 are proved with the allowed axioms, the norm-defaults A/B is byte-identical,
and the gate passes.

### WG-7. Wire and display for zone answers and records (Lean, Python, 5–6 h)

Lean: kinds `weighing-zone` (situation, act, tuple, optional record, proposed completions) and `weighing-record` in
`Weighing/Run.lean`; their shapes and encoder theorems. Python: `ve/weighing.py` relays them; the untrusted search that
proposes completions reuses `ve/readings_s1.py`'s search over Lean's environment (no second search); the English of
2.6 rendered from Lean's rows; CLI `ve document zone <doc> --situation <file> --act <phrase> [--record <file>]
[--assume-no-exceptions]` in `ve/__main__.py` (shared: one subcommand). Fuzz tests as WG-4 on both kinds.

Done when: Z-α to Z-ε pass through the CLI, the fuzz tests pass, and the gate passes.

### WG-8. Zone probe on the constitution (pilot, 3 h)

On the pilot branch after WG-5: for each hard constraint (u0165.s01 to s07) at the one-element situations of today's
`probes/unspecified-probe.json`, and for each "should" set, record the zone answer verbatim. Expected (C-7): `settled
no` where the knowing-or-likely condition holds; `left to the assistant` where the case holds but the condition does
not, if the default reading of :457 is translated; `not said` only where the act is unspecified and no rule speaks.
No coverage is claimed from the probe; every `unknown` is listed with its budget.

### WG-E1. Experiment: collisions between different acts (planner, 4 h)

Question: how many of the constitution's value conflicts are collisions between *different* positive acts, which
neither soft's same-act collision nor act identification ("refuse" read as "not comply") captures?

Pre-registered protocol: draw 40 units at random (seed `20261012`) from the units whose primary blocker is `norms`
and whose text hits the CROSSACT class of research 2.1; for each, a reader classifies the conflict it expresses as
(i) same act after identification, (ii) two exclusive positive acts, (iii) a choice of the best response among
several, (iv) no conflict between acts. The reader records the act phrases and the citation for each. A second reader
classifies 10 of them blind; agreement is reported.

Bar: build exclusive acts (WG-10) only if (ii) is at least 8 of 40 **and** at least 5 of those 8 would change a
checked answer of the translation (a conflict found or resolved). Otherwise record the result and close.

### WG-E2. Experiment: precedents (planner, 5–6 h)

Question: can the constitution's worked examples constrain one open decision as precedents, without inventing
factors? Protocol: pick the open decision with the most worked examples in the source (expected: the cost-benefit
judgment of :325-347, or the operator-instruction exception of :166); list its factors from the source's own lists
(:332-343); write each example as a precedent (factors present, outcome), citing its span; hold out one third of the
examples (seed `20261012`). Compile the rest into necessary and sufficient conditions by Horty's result model
(research 3.4): a case at least as strong for an outcome as a precedent with that outcome must have it.

Bar: build WG-9 only if (a) every example can be written with source-listed factors only, (b) the precedent set is
consistent, and (c) the compiled conditions force the held-out examples' recorded outcomes in at least half of them
and contradict none. A contradiction or invented factor fails the experiment.

### WG-9. Precedents compiled into decision conditions (Lean, 5–6 h; only if WG-E2 passes)

```lean
namespace VE.Weighing

/-- A recorded decision: the factors present, with their polarity for the decision, and the outcome. -/
structure Precedent where
  target : Target
  pro : List String              -- base predicates favouring the decision (true)
  con : List String              -- base predicates favouring its negation
  present : List String          -- the factors present in the recorded case
  outcome : Bool

/-- The result model: a case at least as strong for the outcome as the precedent must have it. -/
def precedentPremise (Wd : WeighDoc) (P : Precedent) : VE.Formula

def consistentPrecedents (Ps : List Precedent) : Bool :=
  Ps.all (fun P => Ps.all (fun Q =>
    !(P.outcome && !Q.outcome && P.target == Q.target &&
      (P.pro.filter (· ∈ P.present)).all (· ∈ Q.present) &&
      (Q.con.filter (· ∈ Q.present)).all (· ∈ P.present))))

/-- Consistency is exactly satisfiability of the compiled premises at every factor valuation. -/
theorem consistentPrecedents_iff (Wd : WeighDoc) (Ps : List Precedent) (h : WellFormedPrecedents Wd Ps = true) :
    consistentPrecedents Ps = true ↔
      ∀ (S : VE.Structure.{u}) (vs : List S.Carrier), ∃ b : Bool,
        ∀ P ∈ Ps, (precedentPremiseAt Wd P b).denote S (tupleVal vs)

/-- A fortiori: a case dominating a precedent is decided as the precedent was, in every structure satisfying the
    compiled premises. -/
theorem afortiori_sound (Wd : WeighDoc) (P : Precedent) (S : VE.Structure.{u}) (hS : Sat S [precedentPremise Wd P])
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd P.target) vs)
    (hdom : AtLeastAsStrong Wd P S vs) :
    ((targetF Wd P.target).denote S (tupleVal vs) ↔ P.outcome = true)
```

The compiled premises join `Dec_T`; nothing else changes. Deleted, not duplicated: none.

### WG-10. Exclusive acts (design batch, only if WG-E1 passes)

Not specified here. It would extend soft's colliding pairs with declared exclusive acts of the same argument sorts
(research 4.1, extension c); that changes `ValueSoft`'s blocking and dominance steps, so it is a new profile with its
own faithfulness theorem, designed and reviewed before any build.

## 6. In-flight work and merge conflicts

| In-flight item (branch) | What this plan uses | How conflicts are avoided |
|---|---|---|
| RD-9 (`rd-9/lean`, `rd-9/integrate`, `rd-9/py`; plan on `design/rd-9`) | SC-1's `EntailsX`, `acceptanceX`, `conflictFreeCheckX_sound`, `modelCheckX_sound`, `softLabelledU_wellFormed`; SC-6's `LayeredAdmission.lean` and `bindCertX`; SC-8's `ve document` path for soft documents under `norm-defaults@0`; SC-9's pilot migration; SC-A's edits to `NormDefaults/Evidence.lean` | WG-3 starts only after SC-1 and SC-6 are on `main`; WG-4 after SC-8; WG-6 (the only batch editing a file RD-9 edits, `Evidence.lean`) after SC-A; WG-0 after SC-8, on the pilot branch SC-9 uses |
| design wave siblings (`design/attitudes`, and the act-phrases, quantities, events-time-causation, scope and math-evidence designs) | nothing yet; boundaries in research 1.3 | no shared file in WG-0 to WG-8 except `lean/VE.lean`, `lean/VE/Audit.lean`, `Service/Protocol.lean`, `service_schema.py`, `ve/document.py`, `ve/norm_english.py`, `ve/__main__.py` (append-only edits; merge-train regenerates generated files with `regen_generated.py --resolve`) |
| lean-first and arch items (`infra/arch-AR-*`, lf-14 to lf-18) | AR-13's diagnostic codes (DRI D6) | new diagnostics are texts until AR-13 lands, then take its codes in the batch after |

Every shared file a batch touches is listed in its section. New code goes in new files (`lean/VE/Weighing/*`,
`ve/surface/weighing.py`, `ve/weighing.py`, `tests/test_weighing_*.py`). Generated inventories are regenerated by
their tools, never hand-merged.

## 7. The measure

Coverage is measured as soft-norms-PLAN 4 requires: a unit changes status only after end-to-end admission through
`ve document`, against a baseline of the same split at the same commit, and after a blind whole-span fidelity review;
claimed and audit-verified bytes are reported separately; no figure is predicted beyond the estimates in research
5.2, which are upper bounds by keyword and boundary reading, not expected gains. Zone answers are reported as counts
of `settled`, `left to`, `not said` and `unknown` answers on the probe set, never as coverage.

## 8. Not claimed, risks, open questions

- **Not claimed.** That any finding of a decider is right; that a decider considered the listed factors; completeness
  of the zone search (`unknown` is honest); completeness of the classification of colliding pairs beyond soft 9.5;
  anything about collisions between different acts before WG-10; any speed.
- **Risk: false comfort from "settled".** A `settled` answer is about the rules on one act at one situation, under the
  document's premises; it says nothing about other acts or about whether the situation is described correctly. The
  English says "the text requires", never "the assistant should".
- **Risk: residual size.** Strength and conditions add premises, not decisions, so the residual does not grow; grants
  add none either. Zone answers can name many questions; WG-7 shows at most five, then "and <n> more".
- **Risk: reading drift on "always".** "Safety always outranks ethics" is a translator's reading of :40, never the
  only one: C-2 keeps the reading set. WG-0 and WG-5's blind review audits it.
- **Risk: RD-9 slips.** WG-0, WG-3 to WG-8 wait on it. WG-1, WG-2, WG-E1 and WG-E2 do not.
- **Open question (WG-1).** Is D4's "some chain contains `always`" the reading readers take from "always outranks"?
  WG-4's unambiguity test and a Sonnet 5.5 comprehension check (as RD-9's SC-9 does) on three paraphrases are the
  evidence; the DRI decides if they disagree.

## 9. Review checklist (WG-1)

1. D2 and D3: `weighing@0` changes no byte, decoder, statement or answer of `soft-norms@0` or `norm-defaults@0`
   (`weigh_conservative`, `wellFormedWeigh_empty`, `runWeigh_delegates`, `zone_extends_status`).
2. D4's closure: `strictPair_down`, `strictPair_up`, `holistic_iff_no_always_chain`; the paraphrase of 2.2.
3. `always_dominates`, `always_no_override`, `all_always_is_strict` against soft's `DomWithD`.
4. Conditions and grants: their premises, `grant_needed`, `delegation_bounded`, the fragment gate.
5. The route: `weighX`, `weighX_wellFormed`, `weigh_acceptance`, `weigh_conflict_free`, `stripWeighing_other`,
   `weigh_identity`.
6. Zone: the definitions of 3.4, the four soundness theorems, the separation of `left to` from `not said` (D9), and
   that no evaluator is duplicated (D8).
7. The wordings of 2.2: one reading each; no symbol in what a reader sees.
8. The two experiments' bars, fixed before any data is read.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-10-12 | Draft 1 | Plan for the design recommended in docs/research/weighing.md: decisions D1 to D14; `weighing@0` (strength, override and switch conditions, grants) as premises on open decisions over RD-9's generic `X`; zone answers and decision records on norm-defaults' widened three-valued machinery; Lean statements; fixtures W-α to W-ι, Z-α to Z-ε and C-1 to C-7; batches WG-0 to WG-10 with dependencies and shared files; two pre-registered experiments. Planning only. |
