# Presupposition and definite descriptions (`presupposition@0`): item-1 statement specification

> Status: draft 1, 2026-10-14, branch `design/presupposition`. Written from [presupposition-PLAN.md](presupposition-PLAN.md)
> draft 2, which applies the converged Fable + Astra review of plan draft 1
> (`manage-agents/debates/design-presupposition/{fable,astra}.md`, round 3; edits D2-1 to D2-9). This is PS-S's
> deliverable. Its statement review is the bounded re-check of draft 2, and nothing beyond PS-0p starts until that
> review passes. Theorem statements and fixtures are implementation obligations, not claims of completed proofs or
> tests.
>
> **Not yet elaborated.** Every definition and statement below is transcribed in the scratch file
> `lean/SpecStubs_presupposition.lean`: definitions with their bodies, each theorem as a `Prop`-valued definition
> `stmt_<name>`, and every fixture value as a `#guard` on a finite model. The session that wrote this draft could not
> run `lake` (its permission mode refused the command), so the stubs have not elaborated and the `#guard`s have not
> run. The fixture values in section 7 were derived by hand and count as computed only once the stub run passes. The
> run is: `cd lean && PATH=~/.elan/bin:$PATH lake env lean SpecStubs_presupposition.lean`. The scratch file contains
> no word the Lean audit bans, and it is not committed.
>
> Section 10 lists every place where this draft chose between readings of the plan.

## 0. Scope, one paragraph

A presupposition trigger ("the owner", "Claude’s core values", "the operator’s instructions") is a row of a closed
table. The row builds three formulas at the trigger's position: what it takes for granted (`pre`), the clause with
`pre` built in (`strong`), and the clause read where `pre` holds (`weak`). Lean regenerates the trigger's position (a
one-hole frame in the unit's carrier-free base content, or a W1 rule's act) and its projected goal (Karttunen's
filtering). Each occurrence is an obligation with exactly one carrier: proved by a checked certificate from strictly
earlier units and declared background; assumed as an explicit asserted unit; asserted as `goal ∧ clause`;
conditioned as `goal → clause` (for a rule, its guard gains `pre`, and only an `unspecified` predicate may be
conditioned); or unresolved, as a reading set whose readings are exactly the row's measured candidates. Several
carriers in one unit compose by one operator that puts asserted goals above every condition. Coupling of equal goals
is an optional compression that Lean admits only after checking that no admissible joint reading is lost. Nothing
here changes a frozen report text, a P0, W1 or W3 theorem statement, or a checker function. One hash-frozen source
changes: discourse's `Descriptions.lean` gains the generalised description builders, its hash in
`lean/VE/Route/frozen-sources.sha256` is renewed, and today's `uniqueD` and `assertive` stay equal to their current
bodies by `rfl`.

## 1. Definitions

### 1.1 Rows and readings

- A **row** is one of `definite`, `plural` and `generic` (section 4.4). Other names are refused
  (`PresuppositionUnknownRow`).
- A **reading** is a triple of formulas over the hole's context: `pre`, `strong`, `weak`. A row's **definedness** at a
  valuation `τ` is `strong ↔ pre ∧ weak` there (`Reading.DefinedAt`).
- **Arguments** come from the wire: `sort` and `restriction` (definite and plural), `body` (the clause at the hole,
  for content positions), and `pre` (generic only). A rule's act has no `body`.

| Row | `pre` | `strong` | `weak` |
|---|---|---|---|
| `definite σ D P` (context of length `n`) | `uniqueOpen n σ D` = `∃x:σ (D ∧ ∀y:σ (D' → y = x))` | `assertiveOpen n σ D P` = `∃x:σ (D ∧ (∀y:σ (D' → y = x)) ∧ P)` | `presupposed σ D P` = `∀x:σ (D → P)` |
| `plural σ D P` | `∃x:σ D` | `(∃x:σ D) ∧ ∀x:σ (D → P)` | `∀x:σ (D → P)` |
| `generic pre body` | `pre` | `pre ∧ body` | `pre → body` |

`D'` is `raise1 n D`: the restriction weakened past the inner binder, so its variable 1 and above skip the outer
binder's index. All three definite formulas are built in discourse's file (4.1); on closed restrictions (`n = 0`)
they are discourse@1's `uniqueD`, `assertive` and `presupposed` exactly.

### 1.2 Frames, goals and position classes

- A **frame** `f` is a formula with one hole, built from VE's eleven formula constructors (section 4.2). `f.plug a`
  puts `a` in the hole. `f.binders` lists the sorts of the binders crossed, innermost first; the hole's context is
  `f.binders ++ Γ`.
- The **projected goal** `f.goal p`:
  - passes through negation, the left side of every connective and the antecedent of "if";
  - gains the left side as a hypothesis on the right of "and" and of "if", and its negation on the right of "or";
  - closes universally over every binder crossed, "some" included.
- **Reach.** `f.Reach S ρ τ` holds when the hole is evaluated at `τ` from `ρ`, under what the text to its left
  guarantees there (Schlenker's incremental local context). `goal_denote` says the goal holds exactly when `p` holds
  at every reached valuation.
- **Position class** (`Frame.cls`): the first operator from the root that is not "and" or a quantifier decides it:
  none (`top`), "not" (`negated`), the antecedent of "if" (`antecedent`), the consequent of "if" (`consequent`), a
  disjunct (`disjunct`). A rule's act is `ruleAct`. `ruleGuard` exists for authoring only (10, C2).
- `f.close p` is the universal closure over the binders alone, without hypotheses: the proviso's unconditional goal.

### 1.3 Base content

A unit's **base content** `B` is its content with each trigger's clause (`strong`) in place and no carrier added. For
a rule, the **base rule** is the rule with the conditions that carriers added removed from its guard. Every frame and
every goal is computed on the base content or the base rule (D2-8). So a `pre` that one carrier adds never filters
another obligation, and never proves its own goal. Paths in the wire are paths into `B`.

### 1.4 Carriers

Write `G = f.goal pre` for an obligation at frame `f` in `B`.

| Carrier | The unit's recorded content | What else must exist | Where `G` fails |
|---|---|---|---|
| proved | `B` | a deduction node whose certificate checks `G` from `premisesBefore` (1.7) | cannot fail in a model of the premises |
| assumed | `B` | an asserted unit whose content is `G` | not a model of the document |
| asserted | `G ∧ B` (`assertedAt`) | — | false, at every frame (`asserted_false_off_goal`) |
| conditioned | `G → B` (`conditionedAt`) | — | says nothing, at every frame (`conditioned_vacuous_off_goal`) |
| in place (local accommodation) | `B` (`inPlaceAt`) | — | the clause as written; under "not" it is true there |
| unconditional | `B` | an asserted unit whose content is `f.close pre` | not a model of the document |
| unresolved | an open reading set (1.8) | — | readings@1 verdicts |

- Where `G` holds and the row is defined at every reached valuation, asserted, conditioned and in place all equal
  the weak reading of the whole sentence (`carriers_on_goal`, from `collapse`).
- In place and unconditional exist only in cells where PS-E1 measures them: in place in the `negated` and
  `antecedent` cells (option (e)), unconditional in the `consequent` cells (the proviso bar).
- A recorded carrier other than proved and unresolved must be one of the row's candidates at the obligation's position
  class: the translator's narrowing, attributed and labelled (discourse 2.4). Otherwise `PresuppositionCandidates`.

### 1.5 Several obligations in one unit

The unit's recorded content is `carried ms B`, where `ms` lists each obligation's root mode and goal in block order:
asserted contributes its goal as a left conjunct; conditioned contributes its goal as an antecedent; every other
carrier contributes nothing at the root.

`carried ms B = A₁ ∧ (A₂ ∧ … ∧ (C₁ → (C₂ → … → B)))`, the `Aᵢ` the asserted goals and the `Cⱼ` the conditioned goals,
each group in block order.

- An asserted goal never sits under another obligation's condition, so where it fails the unit is false
  (`carried_asserted`).
- Where a conditioned goal fails, the unit says exactly its asserted goals (`carried_conditioned_off`).
- Where every goal holds, the unit is `B` (`carried_on_goals`).
- `peel k m` removes `k` left conjuncts and then `m` antecedents; `peel` of `carried` returns `B` (`peel_carried`).
  This is how Lean recovers `B` from the recorded content before it locates the paths.

### 1.6 Rules

- The **rule goal** of a trigger in the act of rule `N` on regulated predicate `r` is
  `ruleGoal r N pre = ∀x̄:r.sorts (applies N → pre)`. The binders are `r.sorts` in declared order (D2-1), never
  `N.over`, which holds precedence names. `pre` is over the context `r.sorts.reverse`.
- **Conditioning.** `conditionNode N c` is `N` with guard `g ∧ c`. `conditionRule T n c` conditions the rule named
  `n` in place; every rule keeps its name, predicate, sign, carve-outs and precedence (`conditionRule_shape`). This is
  the plan's `replaceNode`.
- Several conditioned obligations on one rule add their `pre`s in block order: guard `((g ∧ pre₁) ∧ pre₂) …`.
- **Where `pre` fails** the conditioned rule selects nothing: it contributes no decision
  (`conditioned_contributes_nothing`). The predicate is UNDECIDED there only where no other rule of either sign
  decides, and only because it is `unspecified`: norm-defaults' `value3 P N .unspecified` is `unsaid` exactly when
  neither side decides (`unsaid_iff`).
- **Default predicates.** For a predicate with an allow or deny default, the default would decide where the text says
  nothing. A conditioned carrier on its rules is refused: `PresuppositionDefault: <obligation>: <predicate>`.
- **Candidates.** A rule act has no asserted carrier; its candidates are at most assumed and conditioned
  (`candidates_ruleAct`, over the table's shape check).
- **Validity.** The recorded tree and the base tree both pass W1's `validate` (a computed check, not a proof).
- **Source identity.** When several rules take one closed `pre` for granted, assuming `pre` once entails every one of
  their rule goals (`source_identity_entails`). Lean offers it as one extra, labelled choice; it is never imposed.

### 1.7 Premises of a proved carrier

`premisesBefore D u` is the declared background (W5 flags, literal distinctness, W3 definitions, in the P0 generator
order) followed by the contents of the asserted claim units strictly before `u`, in document order (D2-3). Rule
elaborations, the unit `u` itself and every later unit are excluded. A certificate that needs any of them fails:
`PresuppositionCertificate`.

### 1.8 Candidates, the table and reading sets

- `Candidate` is one of assumed, conditioned, asserted, in place, unconditional.
- The **candidate table** gives, per row and position class, the candidates in the row's order. PS-E1 fills it. Until
  then every cell is empty, so no obligation is admitted as unresolved, and authoring refuses every unproved trigger.
- **Shape check** (`cellOk`, `tableOk`): no duplicates; never both assumed and asserted in one cell (they have the same
  models, so readings@1 could not separate them; 10, C3); no asserted in a `ruleAct` cell; in place only in `negated`
  and `antecedent`; unconditional only in `consequent`.
- An **unresolved** obligation's unit carries an open reading set whose readings are, in the cell's order, one per
  candidate (`expectedReadings`):
  - a claim's reading is `carried ms B` with this obligation's root mode set by the candidate, plus a premise for
    assumed (`G`) and unconditional (`f.close pre`);
  - a rule's reading is the base rule with the other obligations' recorded conditions, plus this one's for
    conditioned, and the premise `G` for assumed.
- readings@1's own check requires the readings to be pairwise separated by admitted situations; PS-2a calls it.
- At most one unresolved obligation per unit (10, C6).

### 1.9 Coupling (PS-3)

- A **pick** chooses one candidate per unresolved obligation.
- A **group** is two or more unresolved obligations with equal goals and equal cells, all of whose candidates are root
  carriers (assumed, conditioned, asserted). Every obligation is in at most one group. In presupposition@0 a unit's
  only open set is its obligation's own, so every obligation sits in the root reading alternative (10, C9).
- The **representative** of a pick on a group sets every member to assumed if any member chose assumed; else to
  asserted if any chose asserted; else to conditioned.
- **Couplable.** Over the existing constrained joint set `J` (lf-14d's enumeration, within its budget), every pick's
  representative is in `J`. Only couplable groups are coupled, by generated `requires` constraints.
- `coupling_complete`: for a couplable group, every admissible pick's representative is admissible and uniform, and
  has the same models, the same `decides` at typed tuples and the same assumptions. A group that is not couplable stays
  uncoupled: equal goals never impose one choice by themselves.
- In place and unconditional candidates are never in a group; they couple only through an explicit shared
  source-choice identity with its own preservation proof (not in presupposition@0).

## 2. English

### 2.1 What each row takes for granted

| Row | Trigger | `pre` in English |
|---|---|---|
| definite | "the N", "the N of t", "t’s N" (singular) | "there is exactly one N" / "t has exactly one N" |
| plural | "t’s Ns", "the Ns of t", "its/their N" (mass or plural) | "there is at least one N" / "t has at least one N" |
| generic | factive complement, earlier state, earlier event (owner's row) | the owner's sentence, e.g. "the action was in progress before that day" |

### 2.2 One-reading paraphrases

Each line below is the English for exactly one formula. The formula column is what the paraphrase must elaborate
to; PS-6 proves each authoring rewrite has exactly one reading (`refused_have_rewrites`). "The owner is ready." uses
the `definite` row with `D = owner`, `P = ready`.

| Position | Carrier | Paraphrase | Formula |
|---|---|---|---|
| top | asserted | "There is exactly one owner, and that owner is ready." | `U ∧ assertive` |
| top | conditioned | "Where there is exactly one owner, that owner is ready." | `U → assertive` |
| top | assumed | "Assumed (from ‘the owner’): There is exactly one owner." and "The owner is ready." | unit `U`; content `assertive` |
| negated | asserted | "There is exactly one owner, and that owner is not ready." | `U ∧ ¬assertive` |
| negated | conditioned | "Where there is exactly one owner, that owner is not ready." | `U → ¬assertive` |
| negated | in place | "It is not so that there is exactly one owner and that owner is ready." | `¬assertive` |
| consequent | asserted | "If the shop is open, then there is exactly one owner, and that owner is ready." | `(open → U) ∧ (open → assertive)` |
| consequent | conditioned | "If the shop is open and there is exactly one owner, then that owner is ready." | `(open → U) → (open → assertive)` |
| consequent | unconditional | "Assumed (from ‘the owner’): There is exactly one owner." and the sentence | unit `U`; content `open → assertive` |
| rule act | assumed | "Assumed (from ‘the operator’s instructions’): In every situation this rule covers, the operator has given at least one instruction." and the rule | unit `ruleGoal`; the base rule |
| rule act | conditioned | "If the operator has given at least one instruction, then Claude must follow the operator’s instructions." | the rule with guard `g ∧ pre` |

The consequent rows rely on two propositional equivalences, checked when the stub's fixtures run on S21:
`(o → U) ∧ (o → A)` is `o → (U ∧ A)`, and `(o → U) → (o → A)` is `(o ∧ U) → A`.

### 2.3 Lines the reader sees

- **Proved.** No line by default. "Why": "‘<words>’ takes for granted that <pre>; <the earlier sentence, condition or
  declaration> says so."
- **Assumed.** In the assumptions list: "Assumed (from ‘<words>’): <goal>."
- **Asserted.** The asserted paraphrase of 2.2.
- **Conditioned.** "This applies only where <goal>." For a rule: "Where <pre>, <rule>. Where not, this rule contributes
  no decision."
- **In place.** The in-place paraphrase of 2.2.
- **Unresolved.** "Two readings: (1) … (2) …", each followed by a situation where they differ, in document terms.
- **Refuted.** `PresuppositionRefuted: <obligation>: <assumed unit>` when the existing inconsistency report shows that
  the premises refute an assumed goal.
- No symbols, ids or arrows by default; obligation ids are in the provenance view. PS-E2 tests these lines.

### 2.4 Authoring: refusal and rewrites (PS-6)

A trigger construction in VE English is admitted with one reading only when its obligation is proved. Otherwise:

`PresuppositionUnresolved: ‘<words>’ takes for granted that <pre>.`

followed by exactly the rewrites of the cell's candidates, in the row's order:
- assumed: add "<goal>." to the document, before the sentence;
- conditioned: "Where <goal>, <sentence>."; for a rule, "If <pre>, then <rule sentence>.", offered only for an
  `unspecified` predicate;
- asserted: "<goal>, and <sentence with an anaphor>.";
- in place: the in-place paraphrase;
- unconditional: add "<closure of pre>." to the document.

A one-reading cell offers exactly one rewrite, and the original wording is still refused (D2-6). An empty cell gives
the refusal with the advice "rephrase so that the sentence states or conditions on <pre>".

### 2.5 PS-E1's options (exact item wording)

The question is "What does the sentence say about this situation?" in a situation where the projected goal fails.
- (a) "The sentence is false in this situation." Dropped for rule-act items.
- (b) "The sentence says nothing about this situation." For rule-act items: "This rule decides nothing in this
  situation."
- (c) "The sentence takes for granted that <pre>, so this situation goes against the text."
- (d) "I cannot tell."
- (e) In the negated and antecedent cells only: "The sentence is true in this situation."

Results are labelled "proxy, an upper bound for careful readers". They decide candidates and wording only.

## 3. Wire form

```json
"presuppositions": {
  "version": "presupposition@0",
  "obligations": [
    {"id": "p1", "unit": "u0156.s03", "span": [95180, 95191], "row": "plural",
     "position": {"rule_act": "no-system-prompt-deception"},
     "arguments": {"sort": "entity", "restriction": ["binary", "content_of", ["var", 0], ["var", 1]]},
     "carrier": {"conditioned": {}}},
    {"id": "p2", "unit": "u0013.presupposition", "span": [6120, 6144], "row": "plural",
     "position": {"path": []},
     "arguments": {"sort": "entity", "restriction": ["binary", "core_value_of", ["var", 0], ["const", "claude"]],
                   "body": ["top"]},
     "carrier": {"assumed": {"unit": "u0013.presupposition"}}}
  ]
}
```

| Field | Type | Rule |
|---|---|---|
| `version` | `"presupposition@0"` | exact |
| `id` | token of the existing id grammar | unique in the block |
| `unit` | unit id | a unit of the document |
| `span` | `[start, end]` byte offsets | display and audit only; Lean never reads meaning from it |
| `row` | `"definite"`, `"plural"`, `"generic"` | else `PresuppositionUnknownRow` |
| `position` | `{"path": [i, …]}` or `{"rule_act": name}` | path: child indices into the base content (`not`: 0; `and`, `or`, `implies`: 0 left, 1 right; `all`, `ex`: 0) |
| `arguments` | object with optional `sort`, `restriction`, `body`, `pre` | P0 wire formulas over the hole's context, the described entity at index 0; absent, never `null` |
| `carrier` | one of `{"proved": {"node": id}}`, `{"assumed": {"unit": id}}`, `{"conditioned": {}}`, `{"asserted": {}}`, `{"in_place": {}}`, `{"unconditional": {"unit": id}}`, `{"unresolved": {}}` | exactly one key |

- At `rule_act`, `body` is absent; present, it is `PresuppositionMismatch: <obligation>: body`.
- The block sits in the front matter, so it is identity-bound through `document_id` like discourse's block.
- Python never reads the block's meaning: it sends it to Lean and binds the answer (plan PS-2b).
- p1's conditioned carrier is admitted only if the rule's predicate is `unspecified` in the norm-defaults block.

## 4. Lean: definitions and exact statements

The stub transcribes each `theorem` below as `def stmt_<name> : Prop := ∀ …` with the same binders and conclusion.

### 4.1 `lean/VE/Discourse/Descriptions.lean` (edited in PS-1; frozen hash rehashed)

```lean
namespace VE.Discourse

def uniqueAt (σ : String) (Dr Dr' : VE.Formula) : VE.Formula :=
  .ex σ (.and Dr (.all σ (.implies Dr' (.eq (.var 0) (.var 1)))))
def assertiveAt (σ : String) (Dr Dr' P : VE.Formula) : VE.Formula :=
  .ex σ (.and Dr (.and (.all σ (.implies Dr' (.eq (.var 0) (.var 1)))) P))

/-- A restriction over `σ :: Δ` (`n = Δ.length`) weakened past one new binder at index 1, by W1's `inst`. -/
def raise1 (n : Nat) (Dr : VE.Formula) : VE.Formula :=
  VE.Norms.inst (.var 0 :: (List.range n).map (fun i => .var (i + 2))) Dr
def uniqueOpen (n : Nat) (σ : String) (Dr : VE.Formula) : VE.Formula := uniqueAt σ Dr (raise1 n Dr)
def assertiveOpen (n : Nat) (σ : String) (Dr P : VE.Formula) : VE.Formula := assertiveAt σ Dr (raise1 n Dr) P

-- today's definitions become wrappers; each is `rfl`-equal to its current body (S11)
def uniqueD (σ : String) (Dr : VE.Formula) : VE.Formula := uniqueAt σ Dr Dr
def assertive (σ : String) (Dr P : VE.Formula) : VE.Formula := assertiveAt σ Dr Dr P

theorem raise1_zero (Dr : VE.Formula) : raise1 0 Dr = Dr
theorem uniqueOpen_zero (σ : String) (Dr : VE.Formula) : uniqueOpen 0 σ Dr = uniqueD σ Dr
theorem assertiveOpen_zero (σ : String) (Dr P : VE.Formula) : assertiveOpen 0 σ Dr P = assertive σ Dr P
```

Every existing proof that unfolds `uniqueD` or `assertive` adds `uniqueAt` or `assertiveAt` to its `simp only` list;
no statement changes. `tools/trust-classes.json` gets the five new definitions.

### 4.2 `lean/VE/Presupposition/Frame.lean`

```lean
import VE.Semantics

namespace VE.Presupposition
universe u

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

def Frame.binders : Frame → List String
  | .hole => []
  | .allF s f | .exF s f => f.binders ++ [s]
  | .notF f | .andL f _ | .andR _ f | .orL f _ | .orR _ f | .impL f _ | .impR _ f => f.binders

def Frame.goal : Frame → VE.Formula → VE.Formula
  | .hole, p => p
  | .notF f, p | .andL f _, p | .orL f _, p | .impL f _, p => f.goal p
  | .andR l f, p | .impR l f, p => .implies l (f.goal p)
  | .orR l f, p => .implies (.not l) (f.goal p)
  | .allF s f, p | .exF s f, p => .all s (f.goal p)

def Frame.close : Frame → VE.Formula → VE.Formula
  | .hole, p => p
  | .notF f, p | .andL f _, p | .andR _ f, p | .orL f _, p | .orR _ f, p | .impL f _, p | .impR _ f, p => f.close p
  | .allF s f, p | .exF s f, p => .all s (f.close p)

def Frame.Reach (S : VE.Structure.{u}) : Frame → VE.Valuation S → VE.Valuation S → Prop
  | .hole, ρ, τ => τ = ρ
  | .notF f, ρ, τ | .andL f _, ρ, τ | .orL f _, ρ, τ | .impL f _, ρ, τ => f.Reach S ρ τ
  | .andR l f, ρ, τ | .impR l f, ρ, τ => l.denote S ρ ∧ f.Reach S ρ τ
  | .orR l f, ρ, τ => ¬ l.denote S ρ ∧ f.Reach S ρ τ
  | .allF s f, ρ, τ | .exF s f, ρ, τ => ∃ v, S.domain s v ∧ f.Reach S (v :: ρ) τ

def Frame.locate : VE.Formula → List Nat → Option (Frame × VE.Formula)
  | a, [] => some (.hole, a)
  | .not a, 0 :: p => (Frame.locate a p).map (fun x => (Frame.notF x.1, x.2))
  | .and a r, 0 :: p => (Frame.locate a p).map (fun x => (Frame.andL x.1 r, x.2))
  | .and l a, 1 :: p => (Frame.locate a p).map (fun x => (Frame.andR l x.1, x.2))
  | .or a r, 0 :: p => (Frame.locate a p).map (fun x => (Frame.orL x.1 r, x.2))
  | .or l a, 1 :: p => (Frame.locate a p).map (fun x => (Frame.orR l x.1, x.2))
  | .implies a r, 0 :: p => (Frame.locate a p).map (fun x => (Frame.impL x.1 r, x.2))
  | .implies l a, 1 :: p => (Frame.locate a p).map (fun x => (Frame.impR l x.1, x.2))
  | .all s a, 0 :: p => (Frame.locate a p).map (fun x => (Frame.allF s x.1, x.2))
  | .ex s a, 0 :: p => (Frame.locate a p).map (fun x => (Frame.exF s x.1, x.2))
  | _, _ :: _ => none

inductive PositionClass where
  | top | negated | antecedent | consequent | disjunct | ruleAct | ruleGuard
  deriving DecidableEq, Repr

def Frame.cls : Frame → PositionClass
  | .hole => .top
  | .andL f _ | .andR _ f | .allF _ f | .exF _ f => f.cls
  | .notF _ => .negated
  | .impL _ _ => .antecedent
  | .impR _ _ => .consequent
  | .orL _ _ | .orR _ _ => .disjunct

theorem goal_denote (f : Frame) (p : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (f.goal p).denote S ρ ↔ ∀ τ, f.Reach S ρ τ → p.denote S τ

theorem plug_congr (f : Frame) (a b : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : ∀ τ, f.Reach S ρ τ → (a.denote S τ ↔ b.denote S τ)) :
    (f.plug a).denote S ρ ↔ (f.plug b).denote S ρ

theorem reach_typed (f : Frame) (S : VE.Structure.{u}) (Γ : List String) (ρ τ : VE.Valuation S)
    (hρ : VE.Valuation.Typed S Γ ρ) (h : f.Reach S ρ τ) : VE.Valuation.Typed S (f.binders ++ Γ) τ

theorem plug_wellFormed (E : VE.Environment) (f : Frame) (a : VE.Formula) (Γ : List String)
    (h : (f.plug a).WellFormed E Γ) : a.WellFormed E (f.binders ++ Γ)

theorem goal_wellFormed (E : VE.Environment) (f : Frame) (a p : VE.Formula) (Γ : List String)
    (hf : (f.plug a).WellFormed E Γ) (hp : p.WellFormed E (f.binders ++ Γ)) : (f.goal p).WellFormed E Γ

theorem close_wellFormed (E : VE.Environment) (f : Frame) (a p : VE.Formula) (Γ : List String)
    (hf : (f.plug a).WellFormed E Γ) (hp : p.WellFormed E (f.binders ++ Γ)) : (f.close p).WellFormed E Γ

theorem locate_plug (a : VE.Formula) (path : List Nat) (f : Frame) (b : VE.Formula)
    (h : Frame.locate a path = some (f, b)) : f.plug b = a
```

### 4.3 `lean/VE/Presupposition/Reading.lean`

```lean
import VE.Presupposition.Frame
import VE.Norms.Prefix

structure Reading where
  pre    : VE.Formula
  strong : VE.Formula
  weak   : VE.Formula
  deriving DecidableEq, Repr

def Reading.DefinedAt (r : Reading) (S : VE.Structure.{u}) (τ : VE.Valuation S) : Prop :=
  r.strong.denote S τ ↔ r.pre.denote S τ ∧ r.weak.denote S τ

theorem collapse (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hdef : ∀ τ, f.Reach S ρ τ → r.DefinedAt S τ) (hgoal : (f.goal r.pre).denote S ρ) :
    (f.plug r.strong).denote S ρ ↔ (f.plug r.weak).denote S ρ

theorem collapse_certified (E : VE.Environment) (prem : List VE.Formula) (f : Frame) (r : Reading)
    (c : VE.Tableau.Certificate) (acc : VE.Tableau.checkCertificate E prem (f.goal r.pre) c = true)
    (hdef : ∀ S : VE.Structure.{u}, S.Admissible E → ∀ τ, f.Reach S [] τ → r.DefinedAt S τ)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S prem) :
    (f.plug r.strong).denote S [] ↔ (f.plug r.weak).denote S []

theorem collapse_assumed (E : VE.Environment) (prem : List VE.Formula) (f : Frame) (r : Reading)
    (hdef : ∀ S : VE.Structure.{u}, S.Admissible E → ∀ τ, f.Reach S [] τ → r.DefinedAt S τ)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S (prem ++ [f.goal r.pre])) :
    (f.plug r.strong).denote S [] ↔ (f.plug r.weak).denote S []

def assertedAt (f : Frame) (r : Reading) : VE.Formula := .and (f.goal r.pre) (f.plug r.strong)
def conditionedAt (f : Frame) (r : Reading) : VE.Formula := .implies (f.goal r.pre) (f.plug r.strong)
def inPlaceAt (f : Frame) (r : Reading) : VE.Formula := f.plug r.strong

theorem asserted_false_off_goal (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : ¬ (f.goal r.pre).denote S ρ) : ¬ (assertedAt f r).denote S ρ

theorem conditioned_vacuous_off_goal (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : ¬ (f.goal r.pre).denote S ρ) : (conditionedAt f r).denote S ρ

theorem carriers_on_goal (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hdef : ∀ τ, f.Reach S ρ τ → r.DefinedAt S τ) (hgoal : (f.goal r.pre).denote S ρ) :
    ((assertedAt f r).denote S ρ ↔ (f.plug r.weak).denote S ρ) ∧
    ((conditionedAt f r).denote S ρ ↔ (f.plug r.weak).denote S ρ) ∧
    ((inPlaceAt f r).denote S ρ ↔ (f.plug r.weak).denote S ρ)

inductive Root where
  | bare | asserted | conditioned
  deriving DecidableEq, Repr

def carried (ms : List (Root × VE.Formula)) (B : VE.Formula) : VE.Formula :=
  (ms.filter (fun m => m.1 == Root.asserted)).foldr (fun m a => .and m.2 a)
    ((ms.filter (fun m => m.1 == Root.conditioned)).foldr (fun m a => .implies m.2 a) B)

def peel : Nat → Nat → VE.Formula → Option VE.Formula
  | 0, 0, a => some a
  | 0, m + 1, .implies _ b => peel 0 m b
  | k + 1, m, .and _ b => peel k m b
  | _, _, _ => none

theorem carried_denote (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) :
    (carried ms B).denote S ρ ↔
      (∀ m ∈ ms, m.1 = Root.asserted → m.2.denote S ρ) ∧
      ((∀ m ∈ ms, m.1 = Root.conditioned → m.2.denote S ρ) → B.denote S ρ)

theorem carried_asserted (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (m : Root × VE.Formula) (hm : m ∈ ms) (ha : m.1 = Root.asserted)
    (h : (carried ms B).denote S ρ) : m.2.denote S ρ

theorem carried_conditioned_off (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (m : Root × VE.Formula) (hm : m ∈ ms) (hc : m.1 = Root.conditioned)
    (hoff : ¬ m.2.denote S ρ) :
    (carried ms B).denote S ρ ↔ ∀ m' ∈ ms, m'.1 = Root.asserted → m'.2.denote S ρ

theorem carried_on_goals (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (h : ∀ m ∈ ms, m.1 ≠ Root.bare → m.2.denote S ρ) :
    (carried ms B).denote S ρ ↔ B.denote S ρ

theorem peel_carried (ms : List (Root × VE.Formula)) (B : VE.Formula) :
    peel (ms.filter (fun m => m.1 == Root.asserted)).length
      (ms.filter (fun m => m.1 == Root.conditioned)).length (carried ms B) = some B
```

### 4.4 `lean/VE/Presupposition/Rows.lean`

```lean
import VE.Presupposition.Reading
import VE.Discourse.Descriptions

def definite (n : Nat) (σ : String) (D P : VE.Formula) : Reading :=
  { pre := VE.Discourse.uniqueOpen n σ D, strong := VE.Discourse.assertiveOpen n σ D P,
    weak := VE.Discourse.presupposed σ D P }

def plural (σ : String) (D P : VE.Formula) : Reading :=
  { pre := .ex σ D, strong := .and (.ex σ D) (.all σ (.implies D P)), weak := .all σ (.implies D P) }

def generic (pre body : VE.Formula) : Reading :=
  { pre := pre, strong := .and pre body, weak := .implies pre body }

/-- Generalises `VE.Discourse.description_definedness` (the case `Δ = []`, `τ = []`). -/
theorem definite_defined (E : VE.Environment) (Δ : List String) (σ : String) (hσ : σ ∈ E.sorts)
    (D P : VE.Formula) (hD : D.WellFormed E (σ :: Δ)) (hP : P.WellFormed E (σ :: Δ))
    (S : VE.Structure.{u}) (hS : S.Admissible E) (τ : VE.Valuation S) (hτ : VE.Valuation.Typed S Δ τ) :
    (definite Δ.length σ D P).DefinedAt S τ

theorem plural_defined (σ : String) (D P : VE.Formula) (S : VE.Structure.{u}) (τ : VE.Valuation S) :
    (plural σ D P).DefinedAt S τ

theorem generic_defined (pre body : VE.Formula) (S : VE.Structure.{u}) (τ : VE.Valuation S) :
    (generic pre body).DefinedAt S τ

/-- The arguments as one tuple: `(sort, restriction, body, pre)`. Errors name the field. -/
def buildReading (row : String) (n : Nat) (a : Option String × Option VE.Formula × Option VE.Formula ×
    Option VE.Formula) : Except String Reading :=
  match row, a with
  | "definite", (some σ, some D, some P, none) => .ok (definite n σ D P)
  | "plural", (some σ, some D, some P, none) => .ok (plural σ D P)
  | "generic", (none, none, some b, some p) => .ok (generic p b)
  | "definite", _ | "plural", _ | "generic", _ => .error "arguments"
  | _, _ => .error "row"

def buildPre (row : String) (n : Nat) (a : Option String × Option VE.Formula × Option VE.Formula ×
    Option VE.Formula) : Except String VE.Formula :=
  match row, a with
  | "definite", (some σ, some D, none, none) => .ok (VE.Discourse.uniqueOpen n σ D)
  | "plural", (some σ, some D, none, none) => .ok (.ex σ D)
  | "generic", (none, none, none, some p) => .ok p
  | "definite", (_, _, some _, _) | "plural", (_, _, some _, _) | "generic", (_, _, some _, _) => .error "body"
  | "definite", _ | "plural", _ | "generic", _ => .error "arguments"
  | _, _ => .error "row"
```

`buildReading row (f.binders.length) args` at a content position (the unit's content is closed, so the hole's
context is `f.binders`); `buildPre row r.sorts.length args` at a rule act. For a definite at a content position,
`buildPre` and `(buildReading …).pre` agree, and so do the plural forms.

### 4.5 `lean/VE/Presupposition/Rules.lean`

```lean
import VE.Presupposition.Reading
import VE.Norms.Elaborate
import VE.NormDefaults.Semantics

def ruleGoal (r : VE.Norms.Regulated) (N : VE.Norms.Node) (pre : VE.Formula) : VE.Formula :=
  VE.Norms.bindAll r.sorts (.implies (VE.Norms.applies N) pre)

def conditionNode (N : VE.Norms.Node) (c : VE.Formula) : VE.Norms.Node := { N with guard := .and N.guard c }

def conditionRule (T : VE.Norms.Tree) (n : String) (c : VE.Formula) : VE.Norms.Tree :=
  { T with nodes := T.nodes.map (fun M => if M.name == n then conditionNode M c else M) }

theorem condition_applies (N : VE.Norms.Node) (c : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (VE.Norms.applies (conditionNode N c)).denote S ρ ↔ (VE.Norms.applies N).denote S ρ ∧ c.denote S ρ

theorem conditionRule_shape (T : VE.Norms.Tree) (n : String) (c : VE.Formula) :
    (conditionRule T n c).regulated = T.regulated ∧ (conditionRule T n c).definitions = T.definitions ∧
    (conditionRule T n c).nodes.map (fun M => (M.name, M.pred, M.sign, M.carveOuts, M.over)) =
      T.nodes.map (fun M => (M.name, M.pred, M.sign, M.carveOuts, M.over))

theorem rule_collapse_decides (T : VE.Norms.Tree) (n : String) (c : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (h : ∀ M ∈ T.nodes, M.name = n → (VE.Norms.applies M).denote S ρ → c.denote S ρ)
    (p : String) (sign : Bool) :
    (VE.Norms.decides (conditionRule T n c) p sign).denote S ρ ↔ (VE.Norms.decides T p sign).denote S ρ

theorem rule_collapse_typed (T : VE.Norms.Tree) (r : VE.Norms.Regulated) (N : VE.Norms.Node) (pre : VE.Formula)
    (S : VE.Structure.{u}) (hname : ∀ M ∈ T.nodes, M.name = N.name → M = N)
    (hgoal : (ruleGoal r N pre).denote S []) (vs : List S.Carrier) (hvs : VE.TupleTyped S r.sorts vs)
    (p : String) (sign : Bool) :
    (VE.Norms.decides (conditionRule T N.name pre) p sign).denote S (VE.Norms.tupleVal vs) ↔
      (VE.Norms.decides T p sign).denote S (VE.Norms.tupleVal vs)

theorem rule_collapse_certified (E : VE.Environment) (prem : List VE.Formula) (T : VE.Norms.Tree)
    (r : VE.Norms.Regulated) (N : VE.Norms.Node) (pre : VE.Formula) (cert : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate E prem (ruleGoal r N pre) cert = true)
    (hname : ∀ M ∈ T.nodes, M.name = N.name → M = N)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S prem)
    (vs : List S.Carrier) (hvs : VE.TupleTyped S r.sorts vs) (p : String) (sign : Bool) :
    (VE.Norms.decides (conditionRule T N.name pre) p sign).denote S (VE.Norms.tupleVal vs) ↔
      (VE.Norms.decides T p sign).denote S (VE.Norms.tupleVal vs)

theorem conditioned_contributes_nothing (T : VE.Norms.Tree) (f : Nat) (N : VE.Norms.Node) (c : VE.Formula)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S) (h : ¬ c.denote S ρ) :
    ¬ (VE.Norms.selects T f (conditionNode N c)).denote S ρ

theorem unsaid_iff (P N : Prop) : VE.NormDefaults.value3 P N .unspecified = .unsaid ↔ ¬ P ∧ ¬ N

theorem source_identity_entails (E : VE.Environment) (pre : VE.Formula) (hpre : pre.WellFormed E [])
    (S : VE.Structure.{u}) (h : pre.denote S []) (r : VE.Norms.Regulated) (N : VE.Norms.Node) :
    (ruleGoal r N pre).denote S []
```

`rule_collapse_decides` needs no validity: it holds at any valuation where every rule named `n` gives the condition
when it applies. `rule_collapse_typed` instantiates it at typed tuples of the predicate's sorts, from the rule goal,
through `VE.Norms.bindAll_denote_nil`. The hypothesis `hname` (rule names unique) holds in every W1-valid tree.

### 4.6 `lean/VE/Presupposition/Agree.lean`

```lean
import VE.Presupposition.Rows
import VE.Data.Background
import VE.SpeechActs.Answer

theorem discourse_definite_is_row (σ : String) (D P : VE.Formula) :
    (definite 0 σ D P).pre = VE.Discourse.uniqueD σ D ∧
    (definite 0 σ D P).strong = VE.Discourse.assertive σ D P ∧
    (definite 0 σ D P).weak = VE.Discourse.presupposed σ D P

theorem data_attribute_proved (E : VE.Environment) (f : VE.Data.Background.Flag) (c : String)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hc : E.constants c = some f.source)
    (hfun : (VE.Data.Background.functionalPremise f).denote S [])
    (htot : (VE.Data.Background.totalPremise f).denote S []) :
    (Frame.hole.goal (VE.Discourse.uniqueD f.target (.binary f.name (.const c) (.var 0)))).denote S []

theorem speech_question_top (D : VE.SpeechActs.SpeechDoc) (q : VE.SpeechActs.Question) :
    Frame.hole.goal (VE.SpeechActs.presupposition D q) = VE.SpeechActs.presupposition D q
```

(Plan draft 1 wrote `VE.Data.Flag`; the flag type is `VE.Data.Background.Flag`.)

### 4.7 `lean/VE/Presupposition/{Wire,Admit,Run}.lean` (PS-2a)

**Types.**

```lean
inductive Carrier where
  | proved (node : String) | assumed (unit : String) | conditioned | asserted | inPlace
  | unconditional (unit : String) | unresolved
  deriving DecidableEq, Repr

inductive Candidate where
  | assumed | conditioned | asserted | inPlace | unconditional
  deriving DecidableEq, Repr

def Carrier.root : Carrier → Root            -- asserted ↦ asserted, conditioned ↦ conditioned, else bare
def Carrier.cand : Carrier → Option Candidate -- the candidate a recorded carrier stands for; none for proved, unresolved
def Candidate.root : Candidate → Root
def Candidate.core : Candidate → Bool        -- assumed, conditioned, asserted

inductive Position where
  | path (p : List Nat)
  | ruleAct (rule : String)
  deriving DecidableEq, Repr

structure Args where
  sort        : Option String := none
  restriction : Option VE.Formula := none
  body        : Option VE.Formula := none
  pre         : Option VE.Formula := none
  deriving DecidableEq, Repr

structure Obligation where
  id : String
  unit : String
  span : Nat × Nat
  row : String
  position : Position
  args : Args
  carrier : Carrier
  deriving DecidableEq, Repr

abbrev CandidateTable := String → PositionClass → List Candidate
def candidateTable : CandidateTable := fun _ _ => []     -- filled from PS-E1's output
def cellOk (pc : PositionClass) (cs : List Candidate) : Bool
def tableOk (rows : List String) (t : CandidateTable) : Bool

inductive RContent where
  | claim (a : VE.Formula)
  | rule (N : VE.Norms.Node)
  deriving DecidableEq, Repr

structure RReading where
  cand : Candidate
  content : RContent
  premise : Option VE.Formula
  deriving DecidableEq, Repr

inductive UContent where
  | claim (a : VE.Formula) | rule (name : String) | readings (rs : List RReading) | unformalised
  deriving DecidableEq, Repr

structure DocUnit where
  id : String
  asserted : Bool
  content : UContent
  deriving DecidableEq, Repr

/-- PS-2a's view of the decoded W2 document. -/
structure PDoc where
  E : VE.Environment
  lits : List String
  norms : VE.Norms.Tree                     -- the fixed W1 rules
  unspec : List String                      -- norm-defaults' `unspecified` predicates ([] without its block)
  background : List VE.Formula              -- declared background, P0 generator order
  units : List DocUnit                        -- document order
  proofs : List (String × VE.Tableau.Certificate)   -- deduction nodes: id, certificate
  block : Option (List Obligation)

structure Checked where
  ob : Obligation
  frame : Frame                 -- in the base content; `.hole` at a rule act
  pre : VE.Formula
  reading : Option Reading      -- none at a rule act
  goal : VE.Formula
  pos : PositionClass
  deriving DecidableEq, Repr

structure Report where
  checked : List Checked                    -- one per obligation, block order
  bases : List (String × VE.Formula)        -- each claim unit with obligations: its base content
  baseTree : VE.Norms.Tree                  -- every rule with the carriers' conditions removed (open rules included)
```

The bodies of `cellOk`, `tableOk`, `premisesBefore`, `unitContent`, `unitAsserted`, `unitReadings`,
`unitUnformalised`, `nodeCertificate`, `unitModes`, `claimReading`, `ruleReading`, `expectedReadings` and
`ruleConditions` are in the stub, as written in sections 1.4 to 1.8.

**The check, in order.** The first failing step gives the answer.
1. Budget: at most 256 obligations, and every regenerated formula within W1's 10,000-node AST budget; else
   `ResourceLimit: presuppositions` (UNKNOWN).
2. Per obligation, block order: a unique id (`PresuppositionMismatch: <o>: id`), an existing unit (`…: unit`) and a
   known row (`PresuppositionUnknownRow`).
3. Per unit with obligations, document order: the base content `B = peel kₐ k꜀ (recorded content)` for a claim unit
   (for an open set, from each reading, all equal), and the base rule for a rule; a shape that does not peel is
   `PresuppositionMismatch: <first obligation of the unit>: content` or `…: rule`.
4. Per obligation, block order:
   - position: the path locates in `B`, or the rule is the unit's (fixed or open); else `PresuppositionPosition`;
   - arguments: `buildReading` or `buildPre`; errors are `PresuppositionMismatch: <o>: arguments` or `…: body`;
     the located subformula is `strong`, else `…: clause`;
   - carrier: proved checks against `premisesBefore` (`PresuppositionCertificate`); assumed and unconditional need an
     asserted unit with the regenerated content (`PresuppositionAssumedUnit`); a conditioned rule needs an
     `unspecified` predicate (`PresuppositionDefault`); a recorded carrier must be in the cell
     (`PresuppositionCandidates`); unresolved needs an open set on its unit (`PresuppositionUnresolved`), with exactly
     `expectedReadings` (`PresuppositionCandidates`), and no second unresolved obligation in the unit
     (`PresuppositionCandidates` on the second).
5. Per unit: `carried (unitModes R u) B` equals the recorded content (`…: content`); each recorded rule equals its base
   rule with `ruleConditions` (`…: rule`); the recorded tree and the base tree pass `VE.Norms.validate` (`…: rule`);
   readings@1's separation check accepts each open set (its diagnostic).

**Statements.** `admit` is PS-2a's function `PDoc → Except String Report`.

```lean
theorem admit_regenerates (D : PDoc) (R : Report) (h : admit D = .ok R) :
    D.block = some (R.checked.map (·.ob))

theorem admit_goals_from_base (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (p : List Nat) (hp : c.ob.position = .path p) :
    ∃ B r, (c.ob.unit, B) ∈ R.bases ∧ c.reading = some r ∧ Frame.locate B p = some (c.frame, r.strong) ∧
      buildReading c.ob.row c.frame.binders.length c.ob.args.tuple = .ok r ∧
      c.pre = r.pre ∧ c.goal = c.frame.goal r.pre ∧ c.pos = c.frame.cls

theorem admit_rule_goal (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (n : String) (hp : c.ob.position = .ruleAct n) :
    ∃ N ∈ R.baseTree.nodes, N.name = n ∧ ∃ r ∈ D.norms.regulated, r.name = N.pred ∧
      buildPre c.ob.row r.sorts.length c.ob.args.tuple = .ok c.pre ∧ c.goal = ruleGoal r N c.pre ∧
      c.pos = .ruleAct ∧ c.ob.args.body = none

theorem admit_claim_content (D : PDoc) (R : Report) (h : admit D = .ok R) (x : String × VE.Formula)
    (hx : x ∈ R.bases) (hres : ∀ c ∈ R.checked, c.ob.unit = x.1 → c.ob.carrier ≠ .unresolved) :
    unitContent D x.1 = some (carried (unitModes R x.1) x.2)

theorem admit_rule_content (D : PDoc) (R : Report) (h : admit D = .ok R) :
    VE.Norms.WellFormed ⟨D.E, D.lits, D.norms⟩ = true ∧ VE.Norms.WellFormed ⟨D.E, D.lits, R.baseTree⟩ = true ∧
    ∀ N ∈ R.baseTree.nodes, ∀ M ∈ D.norms.nodes, M.name = N.name →
      M = (ruleConditions R N.name).foldl conditionNode N

theorem admit_proved_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (n : String) (hp : c.ob.carrier = .proved n) :
    ∃ cert, nodeCertificate D n = some cert ∧
      VE.Tableau.checkCertificate (env D) (premisesBefore D c.ob.unit) c.goal cert = true

theorem admit_assumed_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (u : String) (hp : c.ob.carrier = .assumed u) :
    unitAsserted D u = true ∧ unitContent D u = some c.goal

theorem admit_unconditional_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (u : String) (hp : c.ob.carrier = .unconditional u) :
    unitAsserted D u = true ∧ unitContent D u = some (c.frame.close c.pre)

theorem admit_conditioned_rule_unspecified (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (n : String) (hpos : c.ob.position = .ruleAct n) (hcar : c.ob.carrier = .conditioned) :
    ∃ N ∈ R.baseTree.nodes, N.name = n ∧ N.pred ∈ D.unspec

theorem admit_carrier_candidate (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (k : Candidate) (hk : c.ob.carrier.cand = some k) :
    k ∈ candidateTable c.ob.row c.pos

theorem admit_unresolved_readings (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hu : c.ob.carrier = .unresolved) :
    (unitReadings D c.ob.unit = expectedReadings candidateTable R c ∧ (unitReadings D c.ob.unit).isSome) ∨
      unitUnformalised D c.ob.unit

theorem no_silent_accommodation (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hu : c.ob.carrier = .unresolved) : unitContent D c.ob.unit = none

theorem one_open_per_unit (D : PDoc) (R : Report) (h : admit D = .ok R) (c d : Checked)
    (hc : c ∈ R.checked) (hd : d ∈ R.checked) (hu : c.ob.unit = d.ob.unit)
    (hcu : c.ob.carrier = .unresolved) (hdu : d.ob.carrier = .unresolved) : c.ob.id = d.ob.id

theorem candidates_ruleAct (t : CandidateTable) (ht : tableOk rowNames t = true) (row : String)
    (hrow : row ∈ rowNames) (c : Candidate) (hc : c ∈ t row .ruleAct) : c = .assumed ∨ c = .conditioned

/-- PS-2a's wrapper (and PS-4's document mode) on a document without the block. -/
theorem no_block_unchanged (D : PDoc) (h : D.block = none) : admitWrapped D = admitBase D
```

`candidateTable` is a constant; `#guard tableOk rowNames candidateTable` runs in `Examples.lean` once PS-E1 fills it.

### 4.8 `lean/VE/Presupposition/Couple.lean` (PS-3)

```lean
abbrev Pick := List (String × Candidate)
def pickOf (ch : Pick) (o : String) : Option Candidate := (ch.find? (fun x => x.1 == o)).map (·.2)

structure Group where
  members : List String
  goal : VE.Formula
  cands : List Candidate
  deriving DecidableEq, Repr

def groups (t : CandidateTable) (R : Report) : List Group         -- 1.9; body in the stub
def repCandidate (g : Group) (ch : Pick) : Candidate
def rep (g : Group) (ch : Pick) : Pick :=
  ch.map (fun x => if g.members.contains x.1 then (x.1, repCandidate g ch) else x)
def Uniform (g : Group) (ch : Pick) : Prop := ∀ o ∈ g.members, ∀ o' ∈ g.members, pickOf ch o = pickOf ch o'
def couplable (J : List Pick) (g : Group) : Bool :=
  g.cands.all Candidate.core && J.all (fun ch => J.contains (rep g ch))
def coupledSet (J : List Pick) (gs : List Group) : List Pick := J.filter (fun ch => gs.all (fun g => uniformB g ch))

def formulasUnder (D : PDoc) (R : Report) (ch : Pick) : List VE.Formula      -- background, claims, picked readings
def treeUnder (D : PDoc) (R : Report) (ch : Pick) : VE.Norms.Tree            -- fixed rules and picked open rules
def assumptionsUnder (D : PDoc) (R : Report) (ch : Pick) : List VE.Formula   -- the picked readings' premises
def PickFits (t : CandidateTable) (R : Report) (ch : Pick) : Prop

def SameModels (D : PDoc) (R : Report) (ch ch' : Pick) : Prop :=
  ∀ S : VE.Structure.{u}, S.Admissible D.E →
    (VE.Norms.Sat S (formulasUnder D R ch ++ VE.Norms.elaborate (treeUnder D R ch)) ↔
      VE.Norms.Sat S (formulasUnder D R ch' ++ VE.Norms.elaborate (treeUnder D R ch')))

def SameDecides (D : PDoc) (R : Report) (ch ch' : Pick) : Prop :=
  ∀ S : VE.Structure.{u}, S.Admissible D.E → VE.Norms.Sat S (formulasUnder D R ch) →
    ∀ r ∈ D.norms.regulated, ∀ vs, VE.TupleTyped S r.sorts vs → ∀ sign : Bool,
      ((VE.Norms.decides (treeUnder D R ch) r.name sign).denote S (VE.Norms.tupleVal vs) ↔
        (VE.Norms.decides (treeUnder D R ch') r.name sign).denote S (VE.Norms.tupleVal vs))

theorem coupling_complete (D : PDoc) (R : Report) (h : admit D = .ok R) (J : List Pick) (g : Group)
    (hg : g ∈ groups candidateTable R) (hc : couplable J g = true) (ch : Pick) (hch : ch ∈ J)
    (hfit : PickFits candidateTable R ch) :
    rep g ch ∈ J ∧ Uniform g (rep g ch) ∧ SameModels.{u} D R ch (rep g ch) ∧ SameDecides.{u} D R ch (rep g ch) ∧
      ∀ φ, φ ∈ assumptionsUnder D R ch ↔ φ ∈ assumptionsUnder D R (rep g ch)

theorem coupled_uniform (J : List Pick) (gs : List Group) (g : Group) (hg : g ∈ gs) (ch : Pick)
    (hch : ch ∈ coupledSet J gs) : Uniform g ch

theorem coupled_subset (J : List Pick) (gs : List Group) (ch : Pick) (hch : ch ∈ coupledSet J gs) : ch ∈ J
```

- `J` is lf-14d's enumeration of the existing constrained joint set. PS-3 proves, against lf-14d's API once it lands,
  that its generated `requires` constraints cut `J` down to exactly `coupledSet J (couplable groups)`
  (`couplings_spec`); the constraint type is lf-14d's and is pinned then.
- Why `coupling_complete` holds: a mixed pick that contains assumed or asserted entails the shared goal `G`; under `G`
  each conditioned member equals its base (`carried_on_goals`, `rule_collapse_typed`), so the representative has the
  same models and decisions. A pick that is all conditioned is its own representative. The assumptions agree because
  the representative is assumed exactly when some member was.
- A group whose representatives leave `J` (S18) is not couplable and stays uncoupled.

## 5. Diagnostics

Lean writes the text; Python prints it. `<o>` is an obligation id.

| Diagnostic | When |
|---|---|
| `PresuppositionUnknownRow: <o>: <row>` | the row is not `definite`, `plural` or `generic` |
| `PresuppositionPosition: <o>` | the path does not locate in the base content, or the rule is not the unit's |
| `PresuppositionMismatch: <o>: <field>` | `<field>` is `id` (duplicate), `unit` (missing), `arguments`, `body` (at a rule act), `clause` (the located subformula is not `strong`), `content` (the recorded content is not the regenerated one), `rule` (a recorded rule, or a tree that fails W1's check) |
| `PresuppositionCertificate: <o>` | no certificate, or it fails against `premisesBefore` (a certificate citing the unit itself or a later one fails here) |
| `PresuppositionAssumedUnit: <o>: <unit>` | the assumed or unconditional unit is missing, not asserted, or has another content |
| `PresuppositionDefault: <o>: <predicate>` | a conditioned rule whose predicate has an allow or deny default |
| `PresuppositionUnresolved: <o>` | an unresolved obligation on a unit with one content |
| `PresuppositionCandidates: <o>` | readings not exactly the cell's candidates; a recorded carrier not in the cell; a second unresolved obligation in one unit |
| `ResourceLimit: presuppositions` | over budget: UNKNOWN, never a rejection |

`PresuppositionRefuted: <o>: <unit>` is a report line, not a diagnostic.

## 6. Table and template formats

**Candidate table** (PS-E1's output, read by PS-2a and PS-6): one JSON object per row,

```json
{"row": "plural", "cells": {"top": ["assumed", "conditioned"], "negated": [], "antecedent": [],
                            "consequent": [], "disjunct": [], "rule_act": ["assumed", "conditioned"],
                            "rule_guard": []}}
```

with candidate names `assumed`, `conditioned`, `asserted`, `in_place`, `unconditional`, in the measured order (the
share of answers, highest first; ties in this list's order). A generator writes the Lean `candidateTable` from it;
`tableOk` must hold, and a table that fails it is a PS-E1 analysis error. The values above are placeholders, not
measurements.

**English templates** (filled after PS-E2): per row, a `pre` template with the slots `{t}` (possessor) and `{N}` (the
noun), and per candidate the reader line and the rewrite of 2.3 and 2.4, with `{goal}`, `{pre}` and `{sentence}`.

## 7. Acceptance fixtures

### 7.1 Formula-level fixtures (PS-1 `Examples.lean`; computed by the stub's `#guard`s)

Values were derived by hand for this draft; the stub's `#guard`s compute them. Models are finite: `entity` holds the
listed elements, and only the listed tuples are true. "The owner" is `definite 0 entity owner ready`; `U` its `pre`.

| Id | Fixture | Models | Expected (in model order) |
|---|---|---|---|
| S1, S13 | "The owner is ready." | none: no owner; one: `a` owner, ready; one-unready; two-one-unready: `a`, `b` owners, `a` ready; two-ready | asserted `U ∧ strong`: F T F F F. Conditioned `U → strong`: T T F T T. Weak in two-one-unready: F (draft 1's conditioned) |
| S1 (definedness) | `strong ↔ U ∧ weak` | one / none / one-unready | true with both sides true / false through `U` / false through weak |
| S12 | "The owner is not ready." | none, one, one-unready, two-one-unready | asserted F F T F; conditioned T F T T; in place T F T T. Draft 1 at none: asserted (`¬strong`) T, conditioned (`¬weak`) F. Collapse: one, both F; one-unready, both T |
| S21 | "If the shop is open, then the owner is ready." | open, no owner; closed; open, one ready owner | goal `open → U`: F T T. Asserted F T T. Conditioned T T T |
| S16 | "The owner is ready, or the manager is busy." (owner asserted, manager conditioned) | neither; one ready owner; one unready owner, no manager; an unready owner and an idle manager | `carried`: F T T F. The opposite nesting `G_manager → (U_owner ∧ B)`: T in "neither". In the third model the manager's goal fails and the unit is exactly the owner's goal (T) |
| S15 | two units, one goal: assumed and conditioned | none, one (ready, idle), one (ready, busy), two-ready | mixed `[B₁, U, U → B₂]` and uniform `[B₁, U, B₂, U]`: both F F T F |
| S14 | rule on `answer_required(agent, situation)`; `pre` = "a request in that situation addressed to that agent" | agents `ag1`, `ag2`; situation `s1`; request `q` in `s1` addressed to `ag1` | S14a (guard = `pre`): goal T; `decides` original = conditioned at (ag1, s1): T = T, at (ag2, s1): F = F. S14b (guard without the addressee): goal F; at (ag2, s1) original T, conditioned F. M3 (binders from `over`): goal T, wrongly |
| S8 | `resides_in` total and functional; "the State wherein Alice resides" | Alice in one state; Alice in two | flags T and `U` T; functional F and `U` F |
| S20 | a rule act with `body` | — | `buildPre` gives `body`; without `body`, `.ex entity D` |
| S17 | `premisesBefore` of the second of three units | background `⊤` | `[⊤, <first unit's claim>]`: the unit itself and the third are excluded |
| S19 | "the user" in 5 rules: identical goals; different goals | candidates {assumed, conditioned}, no constraints | identical: 32 picks, 1 group, couplable, 2 coupled picks. Different: 0 groups, 32 picks |
| S18 | 2 obligations, one goal, a constraint that excludes both uniform pairs | `J` = the two mixed picks | not couplable; the representative of the first is the all-assumed pick, outside `J` |
| table | `tableOk` | the fixture table; the empty table; `[asserted]` everywhere; `[assumed, asserted]` everywhere | T, T, F, F |
| 4.1 | builders | — | `definite 0`'s `pre` and `strong` are discourse's `uniqueD` and `assertive`; `raise1 1` maps var 1 to var 2; `raise1 0` is the identity on the sample |
| 4.2 | `locate`, `cls` | — | `[0]` under `not`, `[1]` under `or`; `[2]` into `ex` is none; classes negated, consequent (through a quantifier and a conjunct), disjunct |

### 7.2 Every "exactly when" claim, both directions

| Claim | Holds (true side) | Fails (false side) |
|---|---|---|
| `goal_denote` | S21 closed (nothing reached), open with a ready owner (every reached valuation has `U`) | S21 open, no owner (a reached valuation fails `U`) |
| `plug_congr`, `collapse` | S12 one-unready: both plugs true | S12 one: both plugs false |
| `DefinedAt` (definite) | one: strong, `U`, weak all true | none: strong and `U` false; one-unready: strong and weak false |
| `carriers_on_goal` | S1 one: asserted = conditioned = weak = T | S12 one: asserted = conditioned = in place = weak-plug = F |
| `condition_applies` | S14b at (ag1, s1): applies and `pre` both true, conditioned applies | S14b at (ag2, s1): `pre` false, conditioned does not apply |
| `rule_collapse_decides` | S14a at (ag1, s1): both decide | S14a at (ag2, s1): neither decides. S14b at (ag2, s1) shows the hypothesis is needed |
| `carried_denote` | S16 one ready owner: T | S16 neither (an asserted goal fails); S16 unready owner, idle manager (goals hold, `B` fails) |
| `carried_conditioned_off` | S16 unready owner, no manager: unit T = owner's goal T | S16 neither: unit F = owner's goal F |
| `carried_on_goals` | S16 one ready owner: unit T = `B` T | S16 unready owner, idle manager: unit F = `B` F |
| `unsaid_iff` | S7 (document): no rule decides, UNDECIDED | S7b (document): another rule decides, decided (`value3` is noncomputable, so these are PS-2b documents) |
| `tableOk` | the fixture table, the empty table | `[asserted]` at a rule act; `[assumed, asserted]` |
| `couplable` | S19 identical goals | S18 |
| readings exactly the candidates (`admit_unresolved_readings`) | A1 | A2 |
| `no_block_unchanged` | S11: every discourse@1 answer byte-identical | — (an equality; A14 shows a block changes the answer) |

### 7.3 Admission fixtures (PS-2a in Lean, PS-2b as documents)

One fixture per accept rule and per diagnostic. The fixture table of the stub stands in for PS-E1's.

| Id | Document | Expected |
|---|---|---|
| A1 | S1 with an open set {assumed, conditioned} in the cell's order | admitted; two readings, separated by the no-owner situation |
| A2 | A1 with the conditioned reading missing | `PresuppositionCandidates: p1` |
| A3 | S1 unresolved on a unit with one content | `PresuppositionUnresolved: p1` |
| A4 | S7 conditioned, predicate `unspecified` | admitted; at a situation without instructions, UNDECIDED when no other rule decides |
| A5 | S7d: S7 with an allow-by-default predicate | `PresuppositionDefault: p1: <predicate>` |
| A6 | S20: a rule act with `body` | `PresuppositionMismatch: p1: body` |
| A7 | S17: proved, the certificate cites its own unit or the later "There is exactly one owner." | `PresuppositionCertificate: p1` |
| A8 | S10: the same unit after "Alice has exactly one manager." | admitted, proved |
| A9 | assumed carrier whose unit states `pre` without the projected hypothesis (S21: "There is exactly one owner." where the goal is "If the shop is open, there is exactly one owner") | `PresuppositionAssumedUnit: p1: <unit>` |
| A10 | conditioned recorded as `B → G` instead of `G → B` | `PresuppositionMismatch: p1: content` |
| A11 | S16 with the two root goals recorded in the opposite nesting | `PresuppositionMismatch: p1: content` |
| A12 | row `"title"` | `PresuppositionUnknownRow: p1: title` |
| A13 | path `[2]` into an `ex` | `PresuppositionPosition: p1` |
| A14 | a recorded asserted carrier in a cell without asserted | `PresuppositionCandidates: p1` |
| A15 | 257 obligations | `ResourceLimit: presuppositions` (UNKNOWN) |
| A16 | S14 conditioned, the recorded guard `g ∧ pre` with `pre` written over the wrong variable order | `PresuppositionMismatch: p1: rule` |
| A17 | S11: no block | byte-identical to today's answers |

### 7.4 Pilot fixtures

P1 to P13 are the plan's (5.2), with draft 2's corrections: P2 no longer proves u0073.s05 (strictly earlier units);
P6 and P11's conditioned carriers need `unspecified` predicates; P7's bridging premise must be an earlier unit or the
background; P8 is a goal fixture only (its trigger sits in a guard, 10, C2); P12 is coupled only if `couplable` holds.

### 7.5 Seeded bugs

- **Lean (PS-1).** M1: `goal` for `orR` without `.not`; S4 and `plug_congr` fail. M3: `ruleGoal` binds `N.over`; S14's
  goal `#guard` flips. M4: `carried` puts the conditioned goals outside the asserted ones; S16's first `#guard` fails.
- **Lean (PS-2a).** M2: proved accepted without the certificate check; A7 is admitted and its test fails.
- **Python (PS-2b).** The relay accepts an obligation id that is not in the request; a fuzz test fails.

## 8. Limits

- **The translation boundary.** Lean cannot see a trigger in free English. A trigger's presence, its row and, for a
  rule act, the link between the restriction and the act are the translator's claim, checked by the audit.
- **Positions.** presupposition@0 addresses content paths and rule acts. A trigger in a rule's guard, under a modal or
  an attitude, or inside reported content has no position: the unit stays UNFORMALISED in translation, and authoring
  refuses with advice. Reported content is a plug owned by attribution.
- **One open obligation per unit.** A unit with two unresolved triggers stays UNFORMALISED until a later version.
- **Units in another profile's open set** (a scope or act-phrase reading set) have no single base content, so their
  obligations are not addressable in presupposition@0.
- **Proxy readers.** PS-E1 and PS-E2 use Sonnet as a proxy; the results bound careful readers from above and say
  nothing certain about untrained human readers.
- **The table starts empty.** Until PS-E1 runs, every unproved trigger is refused in authoring and UNFORMALISED in
  translation.
- **Validity of trees** is a computed check (W1's `validate` on both trees), not a theorem about conditioning.
- **Budgets.** Over 256 obligations, or over W1's AST budget, or over lf-14d's joint budget, the answer is UNKNOWN.
- **Untrusted certificates.** A certificate may come from any prover; Lean only checks it.

## 9. Review checklist (PS-S)

1. `goal`'s `exF` case closes universally (S5's restrictor proof, `goal_denote`).
2. Incremental, not symmetric, local contexts (S9).
3. The generalised builders: `uniqueD` and `assertive` stay `rfl`-equal; `raise1` through `VE.Norms.inst`.
4. Root carriers and `carried` against S12, S13 and S16.
5. `rule_collapse_typed`'s binders and `conditionRule` against S14 and M3.
6. `premisesBefore` against S17 and A7.
7. `coupling_complete`'s conditions against S18 and S19.
8. The choices of section 10.
9. The stub run: every statement elaborates and every `#guard` passes.

## 10. Choices this draft made, and questions for the review

- **C1. Position classes.** The plan lists top, negated, antecedent, consequent, rule act, rule guard, modal,
  attitude and reported. VE's formulas have no modal, attitude or reported constructor, so presupposition@0 has no
  frame for them; this draft drops them and adds `disjunct` (a hole under "or" first), which PS-E1 does not measure,
  so its cell is empty. `cls` takes the first operator from the root that is not "and" or a quantifier.
- **C2. Rule guards.** The plan's wire has no address for a trigger inside a guard, so `ruleGuard` is for authoring
  only, and P8 is a goal fixture, not an admission one. A later version can add `{"rule_guard": name, "path": …}`.
- **C3. Assumed and asserted never share a cell.** They have the same models (`G` as a premise with `B`, against
  `G ∧ B`), so readings@1 could not separate them. If PS-E1 puts both above the bar, this draft proposes that the cell
  lists `assumed` (the presupposition stays visible as "Assumed: …"), and that PS-E2 tests the asserted wording as its
  paraphrase. **Question Q1:** assumed, asserted, or a merged reading with two wordings?
- **C4. A recorded carrier must be a candidate.** A translator's single carrier other than proved is a narrowing of
  the cell's readings, so it must be one of them (`PresuppositionCandidates` otherwise).
- **C5. `premisesBefore`.** The background is W5 flags, literal distinctness and W3 definitions; rule elaborations are
  excluded even when earlier, since a rule's meaning is not evidence that something exists. **Question Q2:** should
  earlier rules' elaborations count?
- **C6. One open obligation per unit** (8).
- **C7. Recovering the base.** `B` is peeled from the recorded content by the canonical wrapper shape of `carried`;
  rule conditions are appended as left-nested conjunctions in block order. An author who writes an equivalent but
  differently shaped content gets `…: content`.
- **C8. `replaceNode` is `conditionRule`,** by name; tree validity is a computed check of both trees (8).
- **C9. The reading alternative.** In presupposition@0 a unit's only open set is its obligation's, so every
  obligation is in the root alternative, and "same alternative" in 1.9 always holds. It becomes a real condition when
  units inside other profiles' sets are addressable.
- **C10. Budgets.** 256 obligations and W1's 10,000-node AST budget are this draft's proposal.
- **C11. The representative's order** (assumed, then asserted, then conditioned) keeps every assumption: the
  representative is assumed exactly when some member was.
- **C12. Names.** `uniqueAt`, `assertiveAt`, `raise1`, `uniqueOpen` and `assertiveOpen` live in discourse's file;
  `conditionRule` replaces the plan's `replaceNode`; the plan's `assertedContent`, `conditionedContent` and
  `candidateContent` are `assertedAt`, `conditionedAt`, `claimReading` and `ruleReading`.
