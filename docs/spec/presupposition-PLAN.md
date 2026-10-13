# Presupposition and definite descriptions (`presupposition@0`): buildable plan

> Status: plan draft 1, 2026-10-13, branch `design/presupposition` from `main` at `f98183bf`. Design only: no product
> code, no tests, no generated file touched, no model calls. Research: [docs/research/presupposition.md](../research/presupposition.md)
> (cited below as R, with its section numbers). It follows the cross-plan synthesis of the seven wave-1 designs
> (`manage-agents/debates/plan-synthesis/SYNTHESIS.md`, `DRI-DECISIONS-PHASE2.md`): shared owners, queues and landing
> rules are theirs and are cited, not restated. Every number is measured (the method is in R 2.1) or marked
> **estimate**. Lean blocks are statements for the statement review (PS-S), not proved results; the review fixes exact
> bodies, as it did for the wave-1 plans.

## 0. Summary

**What gets built.**
- **Trigger rows.** A presupposition trigger ("the operator’s instructions", "Claude’s core values", "stop",
  "recognise that") is a row of a closed table. The row says what the trigger takes for granted (`pre`), and what the
  clause means with it asserted (`strong`) or with the clause silent where it fails (`weak`).
- **Obligations.** Each trigger occurrence in a unit is an obligation. Lean regenerates its position (a one-hole
  *frame* in the unit's content or the rule frame) and its **projected goal**: Karttunen's filtering, read off VE's
  connectives, quantifiers and W1 guards.
- **Carriers.** Each obligation has exactly one carrier:
  - **proved**: a checked certificate for the goal. A theorem shows the readings then coincide, so there is no choice.
  - **assumed**: an explicit asserted unit whose content is the goal.
  - **conditioned**: the content is the weak reading; a rule's guard gains `pre`, and the rule is silent where it fails.
  - **asserted**: the content is the strong reading.
  - **unresolved**: a reading set whose readings are exactly the row's measured candidates at that position, or a
    question in authoring.
- **Coupling.** Obligations with the same goal share one choice.
- **What readers see.** "Assumed: …", "This applies only where …", or nothing at all when the text already says it.

**What it reuses.**
- discourse@1's description formulas and carrier words;
- P0 certificates; W1's `applies`; W5's flags;
- reading sets and lf-14d's joint choices;
- norm-defaults' `unspecified` silence.

**What it adds to the trusted core.** Two structural functions, three theorems and per-row definedness lemmas.

**First batch that moves a number.** PS-0p is pilot-only. It claims the heading presuppositions that a word triggers
and nothing else blocks: **+89 B** (3 units), +145 B (5) if VE English can write "exactly one", stretch +294 B (9).
All are **estimates**, gated by the audit. It also removes 11 recorded heading "presuppositions" that no word
triggers (349 B), and stops the pilot assuming what the text withholds (u0254, u0268).

| Batch | Kind | Hours | Depends on | Constitution bytes (estimate) | UDHR bytes (estimate) |
|---|---|---|---|---|---|
| PS-0p | pilot, no product code | 2–3 | none | **+89**; +145; stretch +294 | 0 |
| PS-S | spec and statement review | 4–5 | none | 0 | 0 |
| PS-1 | Lean core, new files | 5–6 | PS-S | 0 | 0 |
| PS-E1 | experiment (readers' carriers) | 3 | DRI authorises model calls | 0 | 0 |
| PS-E2 | experiment (rendering) | 2 | PS-E1 | 0 | 0 |
| PS-2a | Lean: obligation check, `presuppositions` mode | 5–6 | PS-1, PS-E1, protocol queue | 0 | 0 |
| PS-2b | Python relay, CLI, fixtures, fuzz | 3–4 | PS-2a | 0 | 0 |
| PS-3 | Lean: coupling identical goals | 3–4 | PS-2a, lf-14d | 0 | 0 |
| PS-4 | on the composition stack, status rule | 4–5 | PS-2a, AR-10 table, lf-16g | 0 | 0 |
| PS-5p | pilot fidelity | 3 | PS-2b; per unit: SC-3b, AP-2/AP-3, PS-7 | 0–72 B READINGS; fidelity 430 B | fidelity 441 B |
| PS-6 | English authoring rows | 5–6 | PS-E1, PS-E2, PS-2a, English queue | 0 (authoring) | 0 |
| PS-7 | change-of-state and iteration rows | 4–5 | PS-1, events ET-3/ET-4 (and ET-D2 for acts) | 0 claimed; enables 36 units, 6,887 B | 0 claimed |
| PS-8 | optional: one carrier vocabulary | 2–3 | PS-2a, qa-q2 merged, cross-plan review | 0 | 0 |

## 1. The design

### 1.1 Position in the stack

The composition stack's order is RESOLVE (discourse), then scope@0's step 1b, then STRUCTURE, SUPERPOSE, CHAIN and
CHECK (composition-PLAN; scope-PLAN 1.1). `presupposition@0` is a checking wrapper at step **1c**: after discourse and
scope, so that names are resolved and governors' conditions are in the rules' guards, and before the chain.

It **does not rewrite content**. Translators and authors write the carrier's elaboration; Lean regenerates it from
the row, the recorded arguments and the path, and compares. This matches discourse's rule that the recorded targets
are the comparison point, never a filter.

Until PS-4 lands on the stack, the same check runs as a separate service mode, `presuppositions` (PS-2a), which
changes no existing admission.

### 1.2 Trigger rows

A row has a name, a builder from recorded arguments to a `Reading` (`pre`, `strong`, `weak`), and a definedness
lemma `strong ↔ pre ∧ weak`. The rows of this plan:

| Row | Example | `pre` | `strong` | `weak` | Owner of the parts |
|---|---|---|---|---|---|
| `definite` | "the mission of Anthropic", "the operator" | `U(D) = ∃x (D x ∧ ∀y (D y → y = x))` | discourse's `assertive` | discourse's `presupposed` `∀x (D x → P x)` | discourse (formulas, unchanged); this plan (row) |
| `plural` (plural or mass possessive, plural definite) | "Claude’s core values", "the operator’s instructions", "his family" | `∃x D x` | `∃x D x ∧ ∀x (D x → P x)` | `∀x (D x → P x)` | this plan |
| `generic` | a factive's complement; a change of state's earlier state; an iteration's earlier event; a possessive act argument | supplied by the owner | `pre ∧ body` | `pre → body` | attitudes or attribution (factive verbs), events (state wordings), act phrases (arguments) |

The restriction `D` may mention the hole's other variables ("the operator of that situation"). The open versions of
the definite formulas weaken `D` past the second binder with W1's existing instantiation (4.3); they agree with
discourse's on closed restrictions (`uniqueOpen_closed`).

### 1.3 Projection: the projected goal

The trigger's position is a one-hole frame `f` over VE's formula constructors. Its projected goal `f.goal pre` is
built as follows:
- **Passes through:** negation, the left side of every connective, and the antecedent of "if".
- **Hypotheses added** for the right side of "and" and of "if" (the left side), and of "or" (the negation of the left
  side).
- **Universal closure** over every binder crossed, "some" included: the presupposition must hold for every witness
  that reaches the hole.

For a trigger in a rule's act, the goal is `∀x̄ (applies N → pre)` (`ruleGoal`, 4.4): the guard and the absence of
carve-outs are the local context.

**Not crossed:**
- reported content ("X says that …") is a plug (attribution owns it);
- the right conjunct does not satisfy the left one ("Her manager is ready, and Alice has exactly one manager" is
  unresolved; PS-E1 measures whether readers agree).

### 1.4 Obligations and carriers

| Carrier | What the document records | What Lean checks | Unit status (W2, through the document mode after PS-4) |
|---|---|---|---|
| proved | a unit-less asserted deduction node with a certificate (discourse's frozen `proved` form) | `checkCertificate E premises goal cert = true` | as the unit's own content |
| assumed | an asserted unit whose content is the goal (discourse's frozen `assumed` form, generalised) | the unit exists, has kind `asserted`, and its content is the regenerated goal | the assumed unit: CHECKED as an assumption, listed in the residual |
| conditioned | the unit's content is `f.plug weak`, or the rule with guard `g ∧ pre` | regenerated content equals the recorded content | as the unit's own content |
| asserted | the unit's content is `f.plug strong` | regenerated content equals the recorded content | as the unit's own content |
| unresolved | the unit carries an open reading set | its readings are exactly the row's candidates at the position (PS-E1's table), pairwise separated by Lean-admitted situations | READINGS, or UNFORMALISED; never CHECKED or OPEN on one reading |

A certificate may come from any untrusted prover (Rust search, an external prover). Lean only checks it. No
certificate means no proved carrier; the obligation then stays unresolved unless another carrier is recorded.

### 1.5 When a presupposition fails

R 4.2 has the full table. In short:
- **assumed:** a situation where `pre` fails is not a model of the premises. If the premises refute the goal, the
  existing inconsistency report shows it, with a `PresuppositionRefuted` line naming the trigger.
- **conditioned:** the sentence says nothing there, and a rule is silent. Norm-defaults' `unspecified` gives
  UNDECIDED, never "not required".
- **asserted:** the sentence is false there.
- **unresolved:** readings@1 verdicts.
- **Questions:** keep speech acts' PRESUPPOSITION-FAILED.

### 1.6 Ambiguity and coupling

- **Candidates come from the words only:** the row and the position class (top, negated, antecedent, consequent,
  rule act, rule guard, under a modal, under an attitude, reported). The table is the one PS-E1 measures. A position
  class with no measured candidates admits no reading set: in translation the unit stays UNFORMALISED; in authoring
  the sentence is refused with advice.
- **One choice per distinct goal.** Obligations whose projected goals are equal as formulas share one choice
  (PS-3). Their reading sets are linked by generated `requires` constraints through lf-14d's joint choices. The 68
  constitution units with "the user" or "the operator" make one choice per distinct goal, not a product over units.
- **Weights never select a carrier**, and a translator's narrowing is attributed and labelled (discourse 2.4,
  unchanged).

### 1.7 What the reader sees

- **Proved.** No extra line by default. "Why" shows: "‘the user’s request’ takes for granted that the user made a
  request; the rule's condition says so."
- **Assumed.** In the document's assumptions list: "Assumed (from ‘Claude’s core values’): Claude has at least one
  core value."
- **Conditioned.** The rule rewritten in full with its condition: "Where there is a system prompt, Claude must not
  actively deceive the user about its content." For a plain claim: "Where Alice has a manager, every manager of
  Alice is ready."
- **Asserted.** "There is exactly one owner, and that owner is ready."
- **Unresolved.** "Two readings: (1) Assumed: every situation this rule covers has operator instructions. (2) This
  rule applies only where the operator has given instructions." Each reading is followed by a situation where they
  differ, in document terms.
- **Authoring (PS-6).** One question: "‘the operator’s instructions’ takes for granted that the operator gave
  instructions. Is that always so, or does this rule apply only when it is so?" Each answer is shown as a rewritten
  sentence.
- No symbols, ids or arrows appear by default; obligation ids are in the provenance view.

## 2. English

### 2.1 Translation (what the pilots write)

- **Ledger fields.** Each unit gets `presupposition_triggers`, one entry per trigger: `words`, `class` (definite,
  possessive, plural, factive, change-of-state, iterative, wh-title), `pre` (in English) and `carrier` (proved,
  assumed, conditioned, asserted, unresolved, or `none` for a title). When a carrier is unresolved, `other_blockers`
  gains `presupposition`.
- **Heading units.** A heading with a trigger carries its presupposition. A heading without one is a title (scope's
  SC-3a) and has no `presupposed_claim` (PS-0p).
- **The block.** Once PS-2a lands, the translation document also carries the `presuppositions` block (3), which Lean
  checks. Before that, the ledger fields are the record and the audit checks them.

### 2.2 Authoring (PS-6)

- **Admitted with one reading.** A trigger construction in VE English is admitted with one reading when its
  obligation is proved, by an earlier sentence, a condition, a rule guard or W5 flags. In the same document, "If a
  user makes a request, Claude must answer the user’s request." is one sentence with one reading.
- **Otherwise refused.** The sentence is refused with `PresuppositionUnresolved: ‘<words>’ takes for granted that
  <pre>.` and offers exactly the rewrites for the row's candidates at that position:
  - **assumed:** add the sentence "<pre>." to the document;
  - **conditioned:** "Where <pre>, <sentence>.", or "If <pre>, then <sentence>." for a rule;
  - **asserted:** "<pre>, and <sentence>."
- **Rewrite discipline.** Each rewrite has exactly one reading (attitudes' `refused_have_rewrites` pattern).

## 3. Wire form (the `presuppositions` block)

```json
"presuppositions": {
  "version": "presupposition@0",
  "obligations": [
    {"id": "p1", "unit": "u0156.s03", "span": [95180, 95191], "row": "plural",
     "position": {"rule_act": "no-system-prompt-deception"},
     "arguments": {"sort": "entity", "restriction": ["binary", "content_of", ["var", 0], ["var", 1]],
                   "body": ["unary", "deceived_about", ["var", 0]]},
     "carrier": {"conditioned": {}}},
    {"id": "p2", "unit": "u0013.presupposition", "span": [6120, 6144], "row": "plural",
     "position": {"path": []},
     "arguments": {"sort": "entity", "restriction": ["binary", "core_value_of", ["var", 0], ["const", "claude"]],
                   "body": ["top"]},
     "carrier": {"assumed": {"unit": "u0013.presupposition"}}}
  ]
}
```

- **Position.** `path` is a list of child indices into the unit's content formula; `rule_act` names a W1 rule of the
  unit.
- **Formulas.** Formulas are P0 wire formulas over the hole's context with the described entity at index 0.
- **Ids and nulls.** Ids are tokens of the existing grammar. Optional fields are absent, never `null`.
- **Identity.** The block is inside the front matter, so it is identity-bound through `document_id` like discourse's
  block.
- **Python.** Python never reads the block's meaning; it sends it to Lean.

## 4. Lean: files and exact statements (PS-1 unless marked)

### 4.1 `lean/VE/Presupposition/Frame.lean`

```lean
import VE.Semantics

namespace VE.Presupposition
universe u

/-- A formula with one hole: where a trigger stands. -/
inductive Frame where
  | hole
  | notF (f : Frame)
  | andL (f : Frame) (r : VE.Formula)
  | andR (l : VE.Formula) (f : Frame)
  | orL (f : Frame) (r : VE.Formula)
  | orR (l : VE.Formula) (f : Frame)
  | impL (f : Frame) (r : VE.Formula)
  | impR (l : VE.Formula) (f : Frame)
  | allF (s : String) (f : Frame)
  | exF (s : String) (f : Frame)
  deriving DecidableEq, Repr

def Frame.plug : Frame → VE.Formula → VE.Formula
  | .hole, a => a
  | .notF f, a => .not (f.plug a)
  | .andL f r, a => .and (f.plug a) r
  | .andR l f, a => .and l (f.plug a)
  | .orL f r, a => .or (f.plug a) r
  | .orR l f, a => .or l (f.plug a)
  | .impL f r, a => .implies (f.plug a) r
  | .impR l f, a => .implies l (f.plug a)
  | .allF s f, a => .all s (f.plug a)
  | .exF s f, a => .ex s (f.plug a)

/-- Binder sorts between the root and the hole, innermost first: the hole's context is `f.binders ++ Γ`. -/
def Frame.binders : Frame → List String
  | .hole => []
  | .allF s f | .exF s f => f.binders ++ [s]
  | .notF f | .andL f _ | .andR _ f | .orL f _ | .orR _ f | .impL f _ | .impR _ f => f.binders

/-- The projected goal (Karttunen 1974, Heim 1983): what must hold at the root for `p` to hold wherever the hole
    is reached. Negation and left sides pass it through; the right side of `and`/`implies` gains the left side as a
    hypothesis, the right side of `or` its negation; every binder closes it universally. -/
def Frame.goal : Frame → VE.Formula → VE.Formula
  | .hole, p => p
  | .notF f, p | .andL f _, p | .orL f _, p | .impL f _, p => f.goal p
  | .andR l f, p | .impR l f, p => .implies l (f.goal p)
  | .orR l f, p => .implies (.not l) (f.goal p)
  | .allF s f, p | .exF s f, p => .all s (f.goal p)

/-- The valuations at which the hole is evaluated from `ρ`, under what the text to the hole's left guarantees
    there (the incremental local context, Schlenker 2009). -/
def Frame.Reach (S : VE.Structure.{u}) : Frame → VE.Valuation S → VE.Valuation S → Prop
  | .hole, ρ, τ => τ = ρ
  | .notF f, ρ, τ | .andL f _, ρ, τ | .orL f _, ρ, τ | .impL f _, ρ, τ => f.Reach S ρ τ
  | .andR l f, ρ, τ | .impR l f, ρ, τ => l.denote S ρ ∧ f.Reach S ρ τ
  | .orR l f, ρ, τ => ¬ l.denote S ρ ∧ f.Reach S ρ τ
  | .allF s f, ρ, τ | .exF s f, ρ, τ => ∃ v, S.domain s v ∧ f.Reach S (v :: ρ) τ

theorem goal_denote (f : Frame) (p : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (f.goal p).denote S ρ ↔ ∀ τ, f.Reach S ρ τ → p.denote S τ

/-- Local replacement: contents that agree wherever the hole is reached may be exchanged. -/
theorem plug_congr (f : Frame) (a b : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : ∀ τ, f.Reach S ρ τ → (a.denote S τ ↔ b.denote S τ)) :
    (f.plug a).denote S ρ ↔ (f.plug b).denote S ρ

theorem reach_typed (f : Frame) (S : VE.Structure.{u}) (Γ : List String) (ρ τ : VE.Valuation S)
    (hρ : VE.Valuation.Typed S Γ ρ) (h : f.Reach S ρ τ) : VE.Valuation.Typed S (f.binders ++ Γ) τ

theorem plug_wellFormed (E : VE.Environment) (f : Frame) (a : VE.Formula) (Γ : List String)
    (h : (f.plug a).WellFormed E Γ) : a.WellFormed E (f.binders ++ Γ)

theorem goal_wellFormed (E : VE.Environment) (f : Frame) (a p : VE.Formula) (Γ : List String)
    (hf : (f.plug a).WellFormed E Γ) (hp : p.WellFormed E (f.binders ++ Γ)) : (f.goal p).WellFormed E Γ

/-- The hole at a recorded path (child indices from the root): the regeneration step of PS-2a. -/
def Frame.locate : VE.Formula → List Nat → Option (Frame × VE.Formula)

theorem locate_plug (a : VE.Formula) (path : List Nat) (f : Frame) (b : VE.Formula)
    (h : Frame.locate a path = some (f, b)) : f.plug b = a

end VE.Presupposition
```

### 4.2 `lean/VE/Presupposition/Reading.lean`

```lean
import VE.Presupposition.Frame
import VE.Norms.Prefix      -- VE.Norms.Sat; the module discourse's Descriptions.lean uses for VE.Tableau

namespace VE.Presupposition
universe u

/-- What a trigger row gives at its hole, all three over the hole's context. -/
structure Reading where
  pre    : VE.Formula   -- what the trigger takes for granted
  strong : VE.Formula   -- the clause with `pre` asserted: false where `pre` fails ("asserted")
  weak   : VE.Formula   -- the clause where `pre` holds, true where it fails ("conditioned")
  deriving DecidableEq, Repr

/-- A row's definedness lemma at one valuation. -/
def Reading.DefinedAt (r : Reading) (S : VE.Structure.{u}) (τ : VE.Valuation S) : Prop :=
  r.strong.denote S τ ↔ r.pre.denote S τ ∧ r.weak.denote S τ

/-- Where the projected goal holds, the strong and weak readings of the whole sentence agree. -/
theorem collapse (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hdef : ∀ τ, f.Reach S ρ τ → r.DefinedAt S τ) (hgoal : (f.goal r.pre).denote S ρ) :
    (f.plug r.strong).denote S ρ ↔ (f.plug r.weak).denote S ρ

/-- The proved carrier: a checked certificate for the goal from the premises removes the choice. -/
theorem collapse_certified (E : VE.Environment) (prem : List VE.Formula) (f : Frame) (r : Reading)
    (c : VE.Tableau.Certificate) (acc : VE.Tableau.checkCertificate E prem (f.goal r.pre) c = true)
    (hdef : ∀ S : VE.Structure.{u}, S.Admissible E → ∀ τ, f.Reach S [] τ → r.DefinedAt S τ)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S prem) :
    (f.plug r.strong).denote S [] ↔ (f.plug r.weak).denote S []

/-- The assumed carrier: with the goal an explicit premise, the readings agree as well. -/
theorem collapse_assumed (E : VE.Environment) (prem : List VE.Formula) (f : Frame) (r : Reading)
    (hdef : ∀ S : VE.Structure.{u}, S.Admissible E → ∀ τ, f.Reach S [] τ → r.DefinedAt S τ)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S (prem ++ [f.goal r.pre])) :
    (f.plug r.strong).denote S [] ↔ (f.plug r.weak).denote S []

end VE.Presupposition
```

### 4.3 `lean/VE/Presupposition/Rows.lean`

```lean
import VE.Presupposition.Reading
import VE.Discourse.Descriptions
import VE.Norms.Basic

namespace VE.Presupposition
universe u

/-- Weakening an open restriction past one new binder at index 1, by W1's instantiation (no new substitution
    code): `D` over `σ :: Δ` with `n = Δ.length`. -/
def raise1 (n : Nat) (D : VE.Formula) : VE.Formula :=
  VE.Norms.inst (.var 0 :: (List.range n).map (fun i => .var (i + 2))) D

def uniqueOpen (n : Nat) (σ : String) (D : VE.Formula) : VE.Formula :=
  .ex σ (.and D (.all σ (.implies (raise1 n D) (.eq (.var 0) (.var 1)))))

def assertiveOpen (n : Nat) (σ : String) (D P : VE.Formula) : VE.Formula :=
  .ex σ (.and D (.and (.all σ (.implies (raise1 n D) (.eq (.var 0) (.var 1)))) P))

/-- A singular definite. On closed restrictions these are discourse@1's formulas exactly. -/
def definite (n : Nat) (σ : String) (D P : VE.Formula) : Reading :=
  { pre := uniqueOpen n σ D, strong := assertiveOpen n σ D P, weak := VE.Discourse.presupposed σ D P }

theorem uniqueOpen_closed (E : VE.Environment) (σ : String) (D : VE.Formula) (hD : D.WellFormed E [σ]) :
    uniqueOpen 0 σ D = VE.Discourse.uniqueD σ D
theorem assertiveOpen_closed (E : VE.Environment) (σ : String) (D P : VE.Formula) (hD : D.WellFormed E [σ]) :
    assertiveOpen 0 σ D P = VE.Discourse.assertive σ D P

/-- Generalises `VE.Discourse.description_definedness` (which is the case `Δ = []`, `τ = []`). -/
theorem definite_defined (E : VE.Environment) (Δ : List String) (σ : String) (hσ : σ ∈ E.sorts)
    (D P : VE.Formula) (hD : D.WellFormed E (σ :: Δ)) (hP : P.WellFormed E (σ :: Δ))
    (S : VE.Structure.{u}) (hS : S.Admissible E) (τ : VE.Valuation S) (hτ : VE.Valuation.Typed S Δ τ) :
    (definite Δ.length σ D P).DefinedAt S τ

/-- A plural or mass description or possessive: existence without uniqueness, distributive predication. -/
def plural (σ : String) (D P : VE.Formula) : Reading :=
  { pre := .ex σ D, strong := .and (.ex σ D) (.all σ (.implies D P)), weak := .all σ (.implies D P) }

theorem plural_defined (σ : String) (D P : VE.Formula) (S : VE.Structure.{u}) (τ : VE.Valuation S) :
    (plural σ D P).DefinedAt S τ

/-- Any trigger whose owner supplies what it takes for granted and the clause. -/
def generic (pre body : VE.Formula) : Reading :=
  { pre := pre, strong := .and pre body, weak := .implies pre body }

theorem generic_defined (pre body : VE.Formula) (S : VE.Structure.{u}) (τ : VE.Valuation S) :
    (generic pre body).DefinedAt S τ

end VE.Presupposition
```

If `VE.Norms.inst`'s list form cannot express the weakening for every `n`, the statement review adds one
`liftFrom` for `VE.Formula` beside `VE.Norms.inst`, in `Norms/Basic.lean`'s owner's file, as the single owner of
substitution. This plan defines none of its own.

### 4.4 `lean/VE/Presupposition/Rules.lean`

```lean
import VE.Presupposition.Reading
import VE.Norms.Elaborate

namespace VE.Presupposition
universe u

/-- A trigger in a rule's act: its local context is the rule's applicability (guard, no carve-out). -/
def ruleGoal (N : VE.Norms.Node) (pre : VE.Formula) : VE.Formula :=
  VE.Norms.bindAll N.over (.implies (VE.Norms.applies N) pre)

/-- The conditioned carrier for a rule: it applies only where `pre` holds. -/
def conditionNode (N : VE.Norms.Node) (pre : VE.Formula) : VE.Norms.Node :=
  { N with guard := .and N.guard pre }

theorem condition_applies (N : VE.Norms.Node) (pre : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) :
    (VE.Norms.applies (conditionNode N pre)).denote S ρ ↔
      (VE.Norms.applies N).denote S ρ ∧ pre.denote S ρ

/-- Where the rule-level goal holds, conditioning changes nothing at any instance of the rule's variables
    (valuations in the order `VE.Norms.bindAll` binds them; the review pins `bindAll_denote`'s form). -/
theorem rule_collapse (E : VE.Environment) (N : VE.Norms.Node) (pre : VE.Formula)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hgoal : (ruleGoal N pre).denote S [])
    (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S N.over.reverse ρ) (hlen : ρ.length = N.over.length) :
    (VE.Norms.applies (conditionNode N pre)).denote S ρ ↔ (VE.Norms.applies N).denote S ρ

/-- The rule's decision is unchanged: conditioning a rule whose goal is proved leaves `decides` equivalent on
    every admissible structure satisfying the premises (instantiated through W1's `selects`/`decides`). -/
theorem rule_collapse_decides (E : VE.Environment) (T : VE.Norms.Tree) (N : VE.Norms.Node) (hN : N ∈ T.nodes)
    (pre : VE.Formula) (prem : List VE.Formula) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate E prem (ruleGoal N pre) c = true)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S prem) (p : String) (sign : Bool) :
    (VE.Norms.decides (replaceNode T N (conditionNode N pre)) p sign).denote S [] ↔
      (VE.Norms.decides T p sign).denote S []

end VE.Presupposition
```

(`replaceNode` is the tree with one node replaced in place; its name is pinned at PS-S.)

### 4.5 `lean/VE/Presupposition/Agree.lean`: the existing pieces are instances

```lean
import VE.Presupposition.Rows
import VE.Data.Background
import VE.SpeechActs.Answer

namespace VE.Presupposition
universe u

/-- discourse@1's definite is this plan's `definite` row on closed restrictions (no copy). -/
theorem discourse_definite_is_row (E : VE.Environment) (σ : String) (D P : VE.Formula)
    (hD : D.WellFormed E [σ]) :
    (definite 0 σ D P).pre = VE.Discourse.uniqueD σ D ∧
    (definite 0 σ D P).strong = VE.Discourse.assertive σ D P ∧
    (definite 0 σ D P).weak = VE.Discourse.presupposed σ D P

/-- W5 `data@0`: total and functional flags prove the goal of "the r of c"; the English `data@0` already admits
    is the proved case, needing no reading choice. -/
theorem data_attribute_proved (E : VE.Environment) (f : VE.Data.Flag) (c : String) (S : VE.Structure.{u})
    (hS : S.Admissible E) (hc : E.constants c = some f.source)
    (hfun : (VE.Data.functionalPremise f).denote S []) (htot : (VE.Data.totalPremise f).denote S []) :
    (Frame.hole.goal (VE.Discourse.uniqueD f.target (.binary f.name (.const c) (.var 0)))).denote S []

/-- Speech acts: a question's presupposition is an obligation at an empty frame. `SupportedGiven` is the assumed
    carrier and `Supported` the proved one; their answer texts are unchanged. -/
theorem speech_question_top (D : VE.SpeechActs.SpeechDoc) (q : VE.SpeechActs.Question) :
    Frame.hole.goal (VE.SpeechActs.presupposition D q) = VE.SpeechActs.presupposition D q

end VE.Presupposition
```

### 4.6 `lean/VE/Presupposition/{Wire,Admit,Run}.lean` (PS-2a)

```lean
namespace VE.Presupposition

/-- How one obligation is carried. The words are discourse@1's (proved, assumed, unresolved) plus two. -/
inductive Carrier where
  | proved (node : String)
  | assumed (unit : String)
  | conditioned
  | asserted
  | unresolved
  deriving DecidableEq, Repr

inductive PositionClass where
  | top | negated | antecedent | consequent | ruleAct | ruleGuard | modal | attitude | reported
  deriving DecidableEq, Repr

inductive Candidate where
  | assumed | conditioned | asserted
  deriving DecidableEq, Repr

/-- A trigger row: the reading it builds from recorded arguments, and the candidates readers take at each
    position class (PS-E1's table; an unmeasured class lists none). -/
structure Row where
  name       : String
  build      : Args → Except String Reading
  candidates : PositionClass → List Candidate

structure Obligation where
  id       : String
  unit     : String
  span     : Nat × Nat            -- prose bytes of the trigger words (display and audit only)
  row      : String
  position : Position             -- a path into the unit's content, or a W1 rule of the unit
  args     : Args
  carrier  : Carrier

/-- An obligation as Lean regenerates it: never read from the wire unchecked. -/
structure Checked where
  ob      : Obligation
  frame   : Frame                 -- `Frame.locate` on the content, or the rule frame
  reading : Reading
  goal    : VE.Formula            -- `frame.goal reading.pre`, or `ruleGoal`
  pos     : PositionClass

def regenerate (D : PDoc) (o : Obligation) : Except String Checked
def admit (D : PDoc) : Except String Report

theorem admit_regenerates (D : PDoc) (R : Report) (h : admit D = .ok R) :
    R.checked.map (·.ob) = D.block.obligations ∧ ∀ c ∈ R.checked, regenerate D c.ob = .ok c

theorem admit_proved_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (n : String) (hp : c.ob.carrier = .proved n) :
    ∃ cert, nodeCertificate D n = some cert ∧
      VE.Tableau.checkCertificate (env D) (premises D) c.goal cert = true

theorem admit_assumed_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (u : String) (hp : c.ob.carrier = .assumed u) :
    unitKind D u = some .asserted ∧ unitContent D u = some c.goal

theorem admit_content_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked) :
    (c.ob.carrier = .conditioned → recordedContent D c.ob = some (conditionedContent c)) ∧
    (c.ob.carrier = .asserted → recordedContent D c.ob = some (assertedContent c))

/-- Readings come from the row: an unresolved obligation's unit has an open set whose readings are exactly the
    row's candidates at its position class, in the row's order, or the unit is UNFORMALISED. -/
theorem admit_unresolved_readings (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hu : c.ob.carrier = .unresolved) :
    unitReadings D c.ob.unit = ((rowOf D c.ob.row).candidates c.pos).map (candidateContent c) ∨
      unitUnformalised D c.ob.unit

/-- No silent accommodation: a unit with one content never carries an unresolved obligation. -/
theorem no_silent_accommodation (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hu : c.ob.carrier = .unresolved) :
    unitContent D c.ob.unit = none

/-- A document without the block is admitted exactly as before. -/
theorem no_block_unchanged (D : PDoc) (h : D.block = none) : admitWrapped D = admitBase D

end VE.Presupposition
```

`PDoc`, `Args`, `Position`, `Report`, `env`, `premises`, `unitContent`, `unitKind`, `unitReadings`,
`recordedContent`, `conditionedContent`, `assertedContent` and `candidateContent` are fixed by PS-S over the decoded
W2 document. They take `ve-document@2`'s units when discourse is present, and the Lean document mode's decoded units
after lf-16g.

**Diagnostics** (Lean's text; Python prints it):
- `PresuppositionUnknownRow: <obligation>: <row>`
- `PresuppositionPosition: <obligation>`
- `PresuppositionMismatch: <obligation>: <field>`
- `PresuppositionCertificate: <obligation>`
- `PresuppositionAssumedUnit: <obligation>: <unit>`
- `PresuppositionUnresolved: <obligation>`: a unit with one content
- `PresuppositionCandidates: <obligation>`: readings not exactly the row's candidates
- `ResourceLimit: presuppositions`: UNKNOWN, never a rejection

### 4.7 `lean/VE/Presupposition/Couple.lean` (PS-3)

```lean
namespace VE.Presupposition

/-- One generated `requires` constraint pair per two obligations with equal goals, through lf-14d's API. -/
def couplings (R : Report) : List VE.Readings.Constraint      -- lf-14d's constraint type, pinned at PS-S

theorem coupled_uniform (D : PDoc) (R : Report) (h : admit D = .ok R) (c₁ c₂ : Checked)
    (h₁ : c₁ ∈ R.checked) (h₂ : c₂ ∈ R.checked) (hg : c₁.goal = c₂.goal)
    (ch : Choice) (hch : ch ∈ jointChoices D (couplings R)) :
    candidateChosen ch c₁ = candidateChosen ch c₂

/-- The joint set grows with distinct goals, not with occurrences. -/
theorem coupling_bound (D : PDoc) (R : Report) (h : admit D = .ok R) :
    (jointChoices D (couplings R)).length ≤ jointBoundByDistinctGoals D R

end VE.Presupposition
```

## 5. Fixtures

### 5.1 Synthetic (Lean `example`s on finite structures where `decide` applies, otherwise `#guard`s of the executable functions; the same documents through the service in PS-2b)

| Id | Fixture | Expected |
|---|---|---|
| S1 | "The owner is ready." (top level, `definite`) | unresolved. The regenerated assumed, conditioned and asserted contents are discourse's. Discourse's ξ models separate them (no owner; two owners) |
| S2 | "If Alice has exactly one manager, then her manager is ready." | goal `U → U`; proved by a one-step certificate; `collapse_certified` applies; one reading |
| S3 | "Alice’s manager is not ready." | the goal passes the negation: same goal as S1 |
| S4 | "Alice has no manager, or her manager is ready." (`plural`) | goal `¬¬∃m … → ∃m …`; proved |
| S5 | "Every person who has a manager trusts their manager." vs "Every person trusts their manager." | first: goal proved by the restrictor; second: goal `∀x (person x → ∃m …)` unresolved |
| S6 | W1 rule over `situation`, guard "a user makes a request in that situation", act "answer the user’s request" with `pre` = the guard's atom | `ruleGoal` proved by a syntactic certificate; `rule_collapse_decides`: the conditioned and the original rule decide alike |
| S7 | W1 rule over `situation`, guard ⊤, act "follow the operator’s instructions" | unresolved. Assumed candidate "In every situation, the operator has given at least one instruction."; conditioned candidate: guard gains the atom. In a situation without instructions, assumed has no model and conditioned gives UNDECIDED (norm-defaults `unspecified`) |
| S8 | `resides_in` declared total and functional; "the State wherein that person resides" | `data_attribute_proved`; one reading. Without the flags: unresolved |
| S9 | "Her manager is ready, and Alice has exactly one manager." | unresolved: the right conjunct does not filter (incremental local context); pins the choice PS-E1 tests |
| S10 | "Alice has exactly one manager. Her manager is ready." (two units) | proved from the earlier unit (a premise), one reading |
| S11 | a discourse@1 document with ξ and η (regression) | byte-identical answers |
| M1 | mutant: `goal` for `orR` without `.not` | S4 no longer proved; `plug_congr`'s proof fails (the seeded Lean bug of PS-1) |
| M2 | mutant: `admit` accepts `proved` without checking the certificate | P-cert fixture (a wrong certificate) is accepted; its test fails (the seeded Lean bug of PS-2a) |

### 5.2 From the pilots (run `20261012T1800Z`; bytes are ledger spans)

| Id | Unit (bytes, status) | Fixture | Expected |
|---|---|---|---|
| P1 | u0013.presupposition (24, U) | "Claude’s core values": `plural`, restriction `core_value_of(x, claude)`, body ⊤, carrier assumed (its own span) | CHECKED as an assumption; "Assumed (from ‘Claude’s core values’): Claude has at least one core value." |
| P2 | u0095.presupposition (36, U) | "Following Anthropic’s guidelines": `plural`, `guideline_of(x, anthropic)` | as P1. Its premise later proves "Anthropic’s guidelines" in u0073.s05 (P7) |
| P3 | u0286.presupposition (29, U) | "Acknowledging open problems": `generic` (factive with a noun object), `pre` = `∃x open_problem(x)` | as P1 |
| P4 | u0002 (37), u0235 (19) | singular `definite`: "Anthropic has exactly one mission"; "Claude has exactly one nature" | as P1 if VE English writes the uniqueness; otherwise stays UNFORMALISED with the note "uniqueness not writable (PS-6)" |
| P5 | u0268 (22), u0254 (50) with u0269.s02 | possessive the text withholds | never assumed alone. Optional reading set {assumed: "Claude has wellbeing."; no claim}; claimed only if the audit accepts (PS-5p) |
| P6 | u0156.s03 (100, READINGS) | "its content" as `plural` in the rule's act, after act phrases split the object | candidates {assumed, conditioned}, separated by a situation without a system prompt. With the conditioned carrier, "… and, where there is one, about its content" |
| P7 | u0073.s05 (234, OPEN) | "the system prompt’s instructions", with scope SC-3b's label condition in the guard and the bridging premise "An operator prompt that addresses a case gives at least one instruction for it." | proved: one reading. Without the bridging premise: unresolved {assumed, conditioned} |
| P8 | u0076.s01 (250, U) | "the operator’s system prompt" under "not", inside "if" | goal at rule level; candidates per PS-E1 (expected: conditioned, asserted, assumed). Assumed contradicts the u0073.s01 case "There’s no operator prompt" once that case is formalised (`PresuppositionRefuted` line). Projection fixture only; no unlock |
| P9 | u0220.s06 (251, U) | "continuing with an ongoing action" (PS-7) | proved within the phrase: one reading |
| P10 | u0168.s01 (96, OPEN) | "remain firm" (PS-7) | unresolved {assumed: "Claude is firm before such arguments", conditioned} unless the hard-constraint context proves it |
| P11 | UDHR u055 (108, READINGS) | "deprived of his nationality", "change his nationality" (`plural` in a prohibition, after act phrases) | candidates {assumed: "Everyone has a nationality.", conditioned}, separated by a stateless person |
| P12 | UDHR u049 (98, READINGS) | "his own", "return to his country", within the existing set (nationality or residence) | the existence carrier is coupled with the existing set (PS-3), not multiplied out |
| P13 | 14th Amendment (use case L) | as S8 on the use case's own vocabulary | one reading with the flags |

## 6. Batches

### PS-0p. Heading presuppositions in the pilot (pilot, no product code; 2–3 h)

- **Goal.**
  - Claim the heading presuppositions that a word triggers and that nothing else blocks.
  - Stop recording claims no word triggers.
  - Stop assuming what the text withholds.
  - Tag triggers as co-blockers.
- **Depends on.** Nothing. It is delivered as additions to the DRI-merged pilot prompts
  (`manage-agents/prompts/pilot-additions.txt` and `pilot-audit-additions.txt`; `DRI-DECISIONS-PHASE2.md`, SC2). The
  UDHR has no heading presuppositions, so it gets no addition. It touches no repository file.
  - **No new sort** (`DRI-DECISIONS-PHASE2.md`, ET1, until premise-scale lands): the new predicates are over the
    existing sort `entity`, and
    there is one new constant `anthropic` of sort `entity`. Existential premises can be witnessed by existing
    elements, so no model needs a larger domain.
  - **Queue 4.4** (the hard constraints u0164, u0165, u0173) is untouched.
- **Steps.**
  1. **Ledger.** Add `presupposition_triggers` to every unit (2.1). This is the measurement of R 2.3 made exact over
     whole units; the excerpts gave only lower bounds.
  2. **Class E** (11 headings, 349 B, R 2.2). Remove `presupposed_claim` and note "no trigger word: a title (scope
     SC-3a)". The status stays UNFORMALISED; scope claims the titles.
  3. **Class A.** Each `.presupposition` span becomes `kind: asserted`, `support: assumption`, `meaning: specified`,
     with fenced VE English content, English round trip, and the ledger fields `carrier: assumed`, `trigger`,
     `trigger_words`.
     - **u0013:** `core_value_of(entity, entity)`, "{0} is a core value of {1}"; "Some entity is a core value of
       Claude."
     - **u0095:** `guideline_of`; "Some entity is a guideline of Anthropic."
     - **u0286:** `open_problem(entity)`; "Some entity is an open problem."
     - **u0002 and u0235:** uniqueness, written as "Some entity is a mission of Anthropic, and every entity that is a
       mission of Anthropic is that entity." if the parser admits it. Otherwise these two stay UNFORMALISED with the
       note "uniqueness not writable (PS-6)".
  4. **Class D** (u0254, u0268). Replace `presupposed_claim` with the note "the text withholds this (u0269.s02): not
     assumed". The status is unchanged.
  5. **Class B** (u0069, u0083, u0245, u0032; 149 B). Offer each to the audit as a separate item, in step 3's form
     (u0032 is OPEN, with `genuine_helpfulness`). Each is claimed only if the audit accepts it.
  6. **Check.** `ve document check` on the translation: it loads, the reading-set choices stay conflict-free (8 of 8
     today), and the carried probes are byte-identical.
- **Audit additions.**
  - For each heading presupposition claimed: the trigger word is in the title.
  - The content is exactly the existence (for a singular description, existence and uniqueness) of what the trigger
    names, and nothing more: no "is desired", "is relevant" or "must".
  - The source does not withhold it elsewhere: search for "whether" or "uncertain" with the noun.
- **Bar.** The next audit samples every claimed heading unit and accepts each. A rejected unit reverts to
  UNFORMALISED and nothing is claimed for it.
- **Bytes.** **+89 B** (u0013, u0095, u0286), +145 B with u0002 and u0235, stretch +294 B with class B. All are
  estimates until audited. UDHR: 0.
- **Deleted.** 11 invented `presupposed_claim` fields.
- **Seeded bug.** None: no product code.

### PS-S. Specification and statement review (planner; 4–5 h)

- **Deliverable.** `docs/spec/presupposition.md`:
  - the bodies of section 4's definitions;
  - the types left open (`PDoc`, `Args`, `Position`, `Report`, `replaceNode`, lf-14d's constraint type);
  - the wire block (3) and the diagnostics (4.6);
  - the candidate-table format (filled by PS-E1) and the English templates (filled after PS-E2).
- **Stubs.** The statements of 4.1–4.5 elaborate in a scratch Lean project outside `lean/`, never committed. `lean/`
  admits no unproved theorem, and its audit bans the words for one, even in comments.
- **Review.** Sol (standing in for Astra on credits) and Fable converge before PS-1. They check in particular:
  - `goal`'s `exF` case (universal closure over a witness);
  - the incremental versus symmetric choice (S9);
  - `raise1` through `VE.Norms.inst`;
  - `rule_collapse_decides`'s use of W1's tree.
- **Bytes.** 0.

### PS-1. Lean core (5–6 h)

- **New files.** `lean/VE/Presupposition/Frame.lean`, `Reading.lean`, `Rows.lean`, `Rules.lean`, `Agree.lean` and
  `Examples.lean` (S1–S11 and P1–P4, P13 as `example`s or `#guard`s).
- **Statements.** 4.1–4.5, all proved, with the standard axiom allowlist unchanged (`python3 lean/audit.py`).
- **Shared files touched.**
  - `lean/VE.lean`: one import.
  - `lean/VE/Audit.lean`: the new theorem names, or AR-1's generated manifest if it has merged (append by hand
    before AR-1 lands, regenerate after, never both).
  - `tools/layer_policy.py`: the new directory's layer.
  - `tools/trust-classes.json`: the new files' trust class.
  - Generated inventories (`lean/statements.txt`, `lean/declarations.txt`, `lean/checkers.lock` and any other that
    `tools/regen_generated.py --list` names) are regenerated with `--write`, never edited.
- **Reads, never edits.** `VE/Discourse/Descriptions.lean`, `VE/Norms/{Basic,Elaborate,Prefix}.lean`,
  `VE/Data/Background.lean`, `VE/SpeechActs/Answer.lean`.
- **Seeded bug.** M1 (5.1): S4's example and `plug_congr` fail. Restore.
- **Bytes.** 0.

### PS-E1. Experiment: which carriers do readers take? (3 h; no product code; model calls authorised by the DRI)

- **Pre-registered here.**
- **Items.** 7 trigger classes × 6 position classes × 2 items = 84 items.
  - Trigger classes: singular definite; possessive or plural; role definite in a rule; factive; change of state;
    iteration; heading noun phrase.
  - Position classes: top level; under negation; consequent with an unrelated antecedent; antecedent; rule act;
    rule guard.
  - **Controls:** 12 items where the text supplies the presupposition (the filters of R 4.1).
  - **Suspension:** 6 items with "whether" ("We are uncertain whether X has a manager; X’s manager is …").
  - **Proviso pairs:** 6 items ("If Alice is a diver, she will bring her wetsuit").
  - Total: 108 items.
- **Each item.** A sentence, a situation (where `pre` fails, or holds for controls), and the question "What does the
  sentence say about this situation?", with four options:
  - (a) it is false here, or the rule is broken: **asserted**;
  - (b) it says nothing about this situation: **conditioned**;
  - (c) it takes for granted that `pre`, so this situation goes against the text: **assumed**;
  - (d) cannot tell.
- **Protocol.** Sonnet 5.5 as human proxy, 40 fresh trials per item (4,320 calls), as attitudes' E1/E2.
- **Bars, fixed before the run.**
  - A carrier is a **candidate** in a cell iff it gets at least 6/40 on each of the cell's two items.
  - A cell is **one-reading** iff one carrier gets at least 36/40 on both items. The row then admits only that
    carrier there, and authoring asks no question.
  - A cell where (d) exceeds 10/40 on either item admits **no** carrier: refused in authoring, UNFORMALISED in
    translation.
  - **Controls:** at least 36/40 choose the answer the proved carrier predicts, on at least 11 of 12 items. If not,
    `collapse`'s English counterpart is in doubt, and PS-6 stops for review (PS-2a's mechanical check still stands).
  - **Suspension:** (c) at most 6/40 on each item. If not, "whether" does not suspend for readers, and class D's
    handling (R 2.2) is reopened.
  - **Proviso:** reported as the share of unconditional-assumption answers. If at least 6/40 on both items, the
    unconditional goal becomes an extra candidate in the consequent cells.
- **Output.** `docs/research/presupposition-E1.md`, and the candidate table that PS-2a and PS-6 read.
- **Bytes.** 0.

### PS-E2. Experiment: the plain-English lines (2 h)

- **Items.** 20 rendered sentences: 5 each for proved (the "why" line), assumed ("Assumed (from …): …"),
  conditioned ("This applies only where …") and unresolved (two readings with a situation). Each has one question on
  what the document commits to in a named situation.
- **Protocol.** 40 trials each.
- **Bar.** At least 36/40 correct on at least 18/20 items. Otherwise the wording is revised and rerun once; a second
  failure keeps the lines in the provenance view only.
- **Bytes.** 0.

### PS-2a. Lean: obligations, check, report, `presuppositions` mode (5–6 h)

- **Depends on.** PS-1; PS-E1 (the candidate table); the protocol queue. `Protocol.lean` and `service_schema.py` are
  edited after their in-flight editors (`lf-16e`, `qa-q2`, `lean-first/b14d`), in landing order with AR-10's
  registry, ME-2, QT-A3, SC-1c, AP-4, ME-12 and ME-4 (SYNTHESIS 4.2).
- **The CLAUDE.md recipe, steps 1–4.**
  - Runner `VE.Presupposition.Run.runCaseReported`.
  - Dispatch in `VE.Service.runMode`, with `VE.Service.runMode_presuppositions` listed in `lean/VE/Audit.lean`.
  - Shape `lean/ResponseShape/Schemas/Presuppositions.lean`.
  - Encoder theorem `ResponseShape.Encoders.Presuppositions.runCaseReported_fits`, listed in
    `lean/ResponseShape/Audit.lean`.
  - Generated `ve/backends/lean_service_schema/presuppositions.json` (`tools/response_schemas.py --write`).
  - `MODES` in `ve/backends/service_schema.py`.
- **Answer rows.** One per obligation, in the block's order:
  - `id`, `unit`, `carrier`;
  - `goal` (the P0 wire formula and its English line, rendered by Lean);
  - `outcome` (checked, or the diagnostic);
  - for unresolved obligations, the candidates' contents.
  - Plus `PresuppositionRefuted` lines from the existing inconsistency report.
- **Statements.** 4.6.
- **New files.** `lean/VE/Presupposition/{Wire,Admit,Run}.lean` and the two ResponseShape files.
- **Shared files touched.** `lean/VE/Service/Protocol.lean` (one dispatch line), `lean/VE/Audit.lean`,
  `lean/ResponseShape/Audit.lean`, `ve/backends/service_schema.py` (one `MODES` entry). Generated: the schema and
  `lean/checkers.lock`.
- **Seeded bug.** M2. Restore.
- **Bytes.** 0.
- **Alternative for the cross-plan review** (SYNTHESIS C9). Instead of a mode, the report becomes a field of the Lean
  document mode's answer after lf-16g. PS-4 can absorb it; this plan does not need both.

### PS-2b. Python relay, CLI, fixtures, fuzz (3–4 h)

- **Relay.** `ve/presuppositions.py` sends the document with `rows` from `ve/backends/relay.py` and binds the answer:
  every obligation id, unit, span and choice it names exists in the request, and no row is empty or extra. Anything
  else is `CheckerUnavailable`. It checks schema and binding only (DRI ruling R8).
- **CLI.** `ve document presuppositions <file>` prints Lean's lines (display only).
- **Tests.**
  - `tests/test_presuppositions_lean.py`: S1–S11, P1–P13 as documents.
  - `tests/test_presuppositions_answer.py`: one-fault and two-fault mutants of genuine answers (each member dropped,
    emptied, retyped, duplicated or reordered; an index pushed out of range); each mutant is `CheckerUnavailable` or
    changes nothing shown.
  - Genuine cases recorded by `tests/route_case_recorder.py` into `tests/data/route-cases.jsonl`.
  - Waits use `HANG_TIMEOUT`; tests write only under `tmp_path`.
- **Shared files touched.** `ve/__main__.py` (one subcommand) and `tools/layer_policy.py`.
- **Seeded bug (Python).** The relay accepts an obligation id that is not in the request. A fuzz test fails. Restore.
- **Bytes.** 0.

### PS-3. Coupling identical goals (3–4 h; after `lean-first/b14d` merges)

- **Goal.** Obligations with equal goals become one choice: generated `requires` constraints through lf-14d's
  joint-choice API, which this batch calls and never edits.
- **New file.** `lean/VE/Presupposition/Couple.lean` (4.7). It touches no shared file beyond `lean/VE.lean` and the
  audit list.
- **Fixtures.**
  - P12 (u049): the existence carrier and the existing nationality/residence set.
  - A synthetic document with "the user" in 5 rules: one choice, not 2⁵.
  - Joint enumeration over 64 is `ResourceLimit: joint choices`, so UNKNOWN (discourse 4.8, unchanged).
- **Bytes.** 0.

### PS-4. On the composition stack (4–5 h; after AR-10's table and lf-16g)

- **Goal.** `presupposition@0` becomes one row in AR-10's profile table, at step 1c. The Lean document mode applies
  the status rule: a unit with an unresolved obligation is READINGS or UNFORMALISED, never CHECKED or OPEN on one
  reading.
- **Statements.**
  - The row's composition theorem for every combination it newly admits (with `norms@0`, `norm-defaults@0`,
    `readings@1`, `soft-norms@0`, `scope@0` where landed), as AR-10's rule requires.
  - `no_block_unchanged` for every legacy combination.
  - `status_unresolved_never_single` over the document mode's status function.
- **Shared files touched.**
  - `lean/VE/Compose/Dispatch.lean`: one row of AR-10's table.
  - The Lean document mode file: the status hook, in the document-mode queue after AT-3b, SC-1b, QT-A4, ET-5, WG-4
    and ME-10 (SYNTHESIS 4.2). If `ve/document.py` still exists, its display only.
  - Python's profile data is generated from AR-10's table.
- **Bytes.** 0.

### PS-5p. Pilot fidelity (pilot; 3 h; per unit, after the named dependency)

| Unit | Fidelity change | Needs |
|---|---|---|
| u0156.s03 | the fused predicate "existence-or-content" goes; the carrier is recorded | act phrases AP-2/AP-3 |
| u0073.s05 | proved through the label condition | scope SC-3b |
| u0168.s01 | "remain" carried | PS-7 |
| UDHR u045a, u049, u055, u064, u077 | existence carriers explicit; packed descriptions such as "the person's country of nationality" go | AP-2/AP-3, and PS-3 for u049 |
| u0254, u0268 | the optional reading set {assumed, no claim}, offered to the audit | PS-2b |

- **Bytes.** Constitution: 0–72 B new READINGS (u0254, u0268), audit-gated; fidelity 430 B. UDHR: fidelity 441 B.
  Statuses are otherwise unchanged.
- **Deleted (pilot data).** The fused and packed predicates above.

### PS-6. English authoring rows (5–6 h; in the English queue)

- **Depends on.** PS-E1, PS-E2, PS-2a. The queue on `lean/VE/EnglishGrammar/*`: AP-1's hunk, then AT-5 → QT-A6 →
  ME-11 → QT-B3 → SC-7 (SYNTHESIS 4.1, 4.2); PS-6 comes after SC-7 unless the DRI assigns another slot.
- **Rows.**
  - **Admitted:** definite "the N of t", possessive "t’s N" and "its/their N", plural definite, and factive "knows
    that" (attitudes' row; only the presupposition column is added).
  - **Each row carries:** its `pre` template, the candidate list per position class from PS-E1, and the rewrite
    templates of 2.2.
  - **Refusal:** `PresuppositionUnresolved` with rewrites.
  - **Statement:** an instance of attitudes' `refused_have_rewrites`. Each rewrite has exactly one reading, and the
    rewrites' readings are exactly the row's candidates, in the row's order.
- **Shared files touched.** The catalogue files in the queue. The generated fixed tables are regenerated, never
  edited.
- **Seeded bug.** A rewrite list missing one candidate; the `refused_have_rewrites` instance fails.
- **Bytes.** 0 on the pilots; it serves authoring (VE's own documentation and web copy, unmeasured).

### PS-7. Change of state, continuation and iteration (4–5 h; after events ET-3/ET-4, and ET-D2 for acts)

- **Rows** (as `generic` instances over events' state sorts and `begins`/`ends`/"is in progress on"):

  | Trigger | `pre` |
  |---|---|
  | "stops" | in progress before the day |
  | "continues" / "remains" | in progress before and on |
  | "ceases" | as "stops" |
  | "resumes" | an earlier state that ended |
  | "again" | an earlier event of the same sort |
  | "returns to" | an earlier state at the place |
  | "no longer" | in progress before, not on |

- **Ownership.** "Still" is admitted only in the sense senses assigns; "stop … from" is the prevent sense, which
  this row never reads.
- **New file.** `lean/VE/Presupposition/Events.lean`, importing events' module. It edits no events file.
- **English rows.** In the English queue after PS-6.
- **Fixtures.** P9, P10, and UDHR u055's and u067's "change".
- **Bytes.** 0 claimed. It makes the 36 constitution units (6,887 B, lower bound) faithfully expressible when their
  primary feature lands (**estimate**).

### PS-8. One carrier vocabulary (optional; 2–3 h; only if the cross-plan review adopts it)

- **Goal.** Discourse's `PresuppositionCarrier` and `presuppositionLine`, and speech acts' presupposition answer
  kinds, map into `Carrier`.
- **Statements.** Agreement theorems in `lean/VE/Presupposition/Agree.lean` (new code only).
- **Frozen texts.** They stay byte-identical. Discourse's and speech acts' files are not edited until their owners
  agree.
- **After.** qa-q2 has merged.
- **Bytes.** 0.

## 7. Dependencies and merge-conflict map

| In-flight or planned item | Branch / worktree | Needed by | How conflicts are avoided |
|---|---|---|---|
| Lean document mode | lf-16e, lf-16f, lf-16g (`ve-lf-16e`, …) | PS-4 | PS-4 after lf-16g, in the document-mode queue after ME-10; until then only new files and the PS-2a mode |
| Coupled reading sets in Lean | lf-14d (`lean-first/b14d`, `ve-lf-14d`) | PS-3 | called, never edited; PS-3 after it merges |
| Protocol and schema registry | in-flight editors lf-16e, qa-q2 (`ve-qa-q2`), lf-14d; then the protocol queue | PS-2a | one dispatch line and one `MODES` entry, in landing order |
| Profile-gate table | AR-10 | PS-4 | one row with its composition proof; the table lands first |
| Generated audit manifests | AR-1 (`arch-20261010-1`) | PS-1 onwards | append by hand before AR-1, regenerate after |
| English catalogue queue | AP-1 hunk, AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7 | PS-6, PS-7 | PS-6 and PS-7 last, one batch at a time |
| Attitudes: "knows", `NegatedFactive` rows | AT-1, AT-5 (`design/attitudes`) | PS-6 factive row | PS-6 adds only the presupposition column to attitudes' rows; the cross-plan review decides whether `NegatedFactive`'s candidates are generated by PS's projection (9) |
| Events: state sorts, act-performance bridge | ET-3, ET-4, ET-D2 (`design/events-time-causation`) | PS-7 | new file importing events; no events file edited |
| Act phrases: argument structure | AP-2, AP-3 (`design/act-phrases`) | PS-5p (u0156.s03, UDHR possessives) | pilot use only |
| Scope: titles, label conditions | SC-3a, SC-3b (`design/scope`) | PS-0p (titles are scope's), PS-5p (u0073.s05) | pilot use only; no shared file |
| Quantities | QT-0p (u0042.presupposition), the superlative in u0027 | PS-0p | both excluded from PS-0p |
| Hard-constraint queue 4.4 | AT-0p → SC-1b → SC-2 → AT-6a/b → WG-5 | none | PS-0p touches no unit of u0164, u0165 or u0173 |
| Premise scale | infra/oom-rootcause, then premise-scale (`ve-premise-scale`) | PS-0p | PS-0p adds no sort (DRI ET1) |
| Discourse | merged; scope SC-3a moves anchor bodies out of `Access.lean`/`WellFormed.lean` | PS-1 reads `Descriptions.lean` | no discourse file edited |
| Premise packs | PK-1 after `rd-9-int` (`ve-rd-9-int`) | none | assumed carriers are document units, not packs; `Layered.lean` untouched |
| Question answering | qa-q2 (`ve-qa-q2`) | PS-8 | PS-8 after it merges; no speech-acts file edited |
| Composition S4, "discourse on the chain" | not in flight, not scheduled | none | the block carries each obligation's own restriction, so documents with norms need no discourse manifest; discourse mentions are read where present |
| Wave 2 siblings | judgment-terms, defeasible (`design/*`) | none | `pre` may contain open terms (judgment-terms' records); "normally"/"by default" are defeasible's |

**Every shared file a batch touches:**
- `lean/VE.lean` and `lean/VE/Audit.lean`: PS-1, PS-2a, PS-3, PS-7.
- `tools/layer_policy.py`: PS-1, PS-2b. `tools/trust-classes.json`: PS-1.
- `lean/VE/Service/Protocol.lean`, `lean/ResponseShape/Audit.lean`, `ve/backends/service_schema.py`: PS-2a.
- `ve/__main__.py`: PS-2b.
- `lean/VE/Compose/Dispatch.lean` and the Lean document mode file: PS-4.
- `lean/VE/EnglishGrammar/*` catalogue files: PS-6, PS-7.

**Generated, never hand-edited or hand-merged:** the service schemas, `lean/checkers.lock`, `lean/statements.txt`,
`lean/declarations.txt`, Python's profile data from AR-10's table, and the route cases (through the recorder).
`tools/regen_generated.py --write` regenerates them; `--resolve` finishes merges whose only conflicts are generated.

**The full gate** runs once, on each batch's committed final HEAD.

## 8. One owner per piece of logic

| Logic | Owner | This plan's use |
|---|---|---|
| Description formulas, `description_definedness`, the proved/assumed frozen forms | discourse@1 | the `definite` row reuses them; `definite_defined` generalises the lemma without copying the formulas |
| Certificates | P0's tableau checker | the proved carrier |
| Rule applicability, binding | W1 `applies`, `bindAll`, `decides` | the rule frame |
| Substitution on `VE.Formula` | W1 `VE.Norms.inst` | `raise1`; any missing lift is added there (4.3) |
| Attribute flags | W5 `data@0` | proved by declaration |
| Silence of a rule | norm-defaults `unspecified` | conditioned failure |
| Reading sets, separating situations | readings@1 | unresolved |
| Joint choices | lf-14d | coupling |
| Question presuppositions | speech acts | an empty frame (`speech_question_top`) |
| Knowing, thinking, their refusal rows | attitudes | the factive row's attitude part |
| Report verbs, plugs | attribution | reported positions are blocked |
| State sorts, "in progress" | events | PS-7's `pre` |
| Act arguments | act phrases | possessive arguments become visible |
| Titles, label and heading conditions | scope | untriggered headings; label conditions as local context |
| Source-word rows and refusals | english-lean's catalogue | trigger rows are catalogue rows |
| Profile registration, mode registry | AR-10 | one row, one mode line |
| Statuses | the Lean document mode | the status rule |
| **Frames, projected goals, `plug_congr`, `collapse`, trigger-row readings, carriers, obligation checks, the coupling rule, the presupposition lines** | **this plan** (new) | — |

**What is deleted or not duplicated:**
- **Product code.** No general presupposition logic exists, so nothing is deleted. Discourse's three formulas are
  imported, not copied. PS-8 (if adopted) turns discourse's carrier type and line into thin agreements with the
  shared ones, keeping the frozen texts.
- **Pilot data.**
  - 11 untriggered `presupposed_claim` fields (PS-0p);
  - u0156.s03's "existence-or-content" (PS-5p);
  - packed existence assumptions in UDHR predicate descriptions (PS-5p).
- **Not duplicated.** Attitudes keeps its `NegatedFactive` rows, events its "missing fact" report, speech acts their
  answer kinds. Each is an instance of the shared pieces below, proved to agree, never re-implemented.

## 9. Risks and questions for the review

1. **The translation boundary.** Lean cannot see a trigger in free English. In translation, the presence of a
   trigger and its row are the translator's claim, checked by the audit (PS-0p's audit lines), as scope accepts for
   reaches. Lean checks everything after that: position, goal, carrier, candidates, coupling.
2. **Incremental local contexts.** S9 ("Her manager is ready, and Alice has exactly one manager") stays unresolved.
   If PS-E1 shows readers accept the right-to-left satisfaction, the symmetric local context becomes an extra
   *candidate*, never a silent filter.
3. **CHECKED as an assumption.** PS-0p's units are CHECKED under W2's rule for assumptions, and listed in the
   residual. NORTH-STAR already says "CHECKED includes admitted assumptions, not proof of their truth". The audit
   decides each unit.
4. **Factive verbs other than "know".** Does "recognise"/"acknowledge"/"be aware" belong to attitudes (a new
   attitude word) or attribution (a report verb with a factive flag)? This plan needs only the complement as `pre`.
5. **A mode or a field.** PS-2a's mode against a field of the Lean document mode (SYNTHESIS C9). Either works; the
   review picks one.
6. **NORTH-STAR row 12.** Its "0–999 B" should be corrected per R 2.2: 145 B direct (294 B stretch), 72 B as reading
   sets, 284 B co-blocked, 349 B not presuppositions at all. The DRI applies it at the next NORTH-STAR update.
7. **Cost of coupling.** If distinct goals exceed the joint budget, verdicts are UNKNOWN, which is honest. PS-5p
   measures how many distinct goals the constitution actually has.

## 10. Shared pieces

Abstractions several topics could share. The cross-plan review may move them.

| Shared piece | Who would use it | Proposal |
|---|---|---|
| **Local contexts and projected goals** (`Frame`, `goal`, `Reach`, `plug_congr`) | presupposition; attitudes (`NegatedFactive`'s two candidates are a factive's projection under negation); scope (a governor's condition inserted into a guard is a filter, and can prove a presupposition: u0073.s05); events (the "missing fact where a wording needed it" is an obligation with an events `pre`); math-evidence ("the limit of", "the unique x such that": definedness obligations whose certificates may come from untrusted provers); quantities ("exactly three", superlatives take existence for granted); speech acts (`H(q)` at the empty frame) | one module, `VE.Presupposition.Frame`, owned here |
| **One carrier vocabulary**: proved, assumed, conditioned, asserted, unresolved; refuted as a report line | discourse 4.5, speech acts 4.5, W5, events' missing facts, attitudes' refusals, math-evidence's proof obligations | `VE.Presupposition.Carrier`, with discourse's words; agreement lemmas, frozen texts unchanged (PS-8) |
| **Trigger rows with per-position candidates and rewrites** | attitudes (AT-5), events (ET-5's wordings), act phrases, quantities (QT-A6) | a row kind `presupposition` in english-lean's catalogue: trigger, `pre` template, candidates per position class, rewrite templates; one rewrite generator (attitudes' `refused_have_rewrites` pattern) |
| **Collapse by proof**: readings that a certificate shows to agree are one reading, reported once | scope (deictic reaches that coincide), act phrases (attachments that coincide), quantities (roundings that coincide on the data), readings@1 generally | a generic lemma beside `collapse`: readings equal under certified premises are merged before a reading set is formed |
| **Coupling by identical content** | presupposition (same goal), scope (one set per governor), discourse (same target), rights (limitation scope) | lf-14d's joint choices with generated `requires` constraints, never a product over occurrences |
| **Existence facts are validated, never assumed** | events, presupposition, quantities (domain sizes), premise-scale | one obligation record and one "missing fact" line |
| **Plain-English assumption and condition lines** ("Assumed (from …): …", "This applies only where …") | presupposition, scope's provenance sentences, discourse's reviewed presentation, weighing's decision records | one wording table in Lean (the catalogue), one display format in Python |
| **Headings: title or presupposition** | scope (titles), presupposition (triggered claims), both pilots | one rule: a heading with a trigger carries its presupposition; without one it is a title; the pilot prompt states it once (PS-0p) |
