import VE.Weighing.Tree
import VE.NormDefaults.Packs
import VE.NormDefaults.Check
import VE.Acts.LexicalProofs
import VE.Discourse.Manifest
import VE.EnglishGrammar.Rules
import VE.Readings.SupEnv
import VE.NormDefaults.FillCheck

/-!
# Weighing's premises and checks (docs/spec/weighing.md 1.4-1.6, 5)

`Weigh_T := Str_T ++ Dec_T ++ Grant_T`, each premise with its label and the request path of its entry; the one
premise generator `condPremise` (a grant premise is its necessary `.off` case); the propositional implication check;
`checkWeigh` (weighing.md 1.6, steps 3 to 7) and `WellFormedWeigh`. The theorems of weighing.md 5 follow;
`strength_iff` carries the DRI's added hypothesis (every regulated name begins with an ASCII letter, the decoder's
identifier rule): without it the statement is false off the decoder (`Examples.lean`). Its reverse direction,
`strength_mem`, holds for every triple.
Each condition is the formula the block decoder (WG-3) gives: today W1's budgeted decoder, since AT-3a's guard
node is not on `main`.
-/

namespace VE.Weighing
open VE.Norms VE.SoftNorms
universe u

abbrev RequestPath := VE.NormDefaults.Packs.RequestPath

def blockPath : RequestPath := ["environment", "vocabulary", "weighing"]

/-- `Str_T`: one premise per `outweighs` decision of a strict pair, in `outweighsTriples` order; its origin is the
    first `always` edge (block order) through which the pair is strict. -/
def strengthEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  (outweighsTriples Wd.D).filterMap (fun (a, L, H) =>
    match Wd.W.always.zipIdx.find? (fun (e, _) => (rankOrder Wd).atLeast H e.1 && (rankOrder Wd).atLeast e.2 L) with
    | some (_, i) => some (s!"weigh:strength:{H}:{L}:{a}",
        bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H)), blockPath ++ ["always", toString i])
    | none => none)

/-- The one premise generator (soft's `excPremisesOf` shape). -/
def condPremise (Wd : WeighDoc) (c : CondDecl) : VE.Formula :=
  match c.kind with
  | .sufficient => bindAll (targetSorts Wd c.target) (.implies c.condition (targetF Wd c.target))
  | .necessary => bindAll (targetSorts Wd c.target) (.implies (targetF Wd c.target) c.condition)

/-- `Dec_T`, in block order. -/
def condEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  Wd.W.conditions.zipIdx.map (fun (c, i) =>
    (s!"weigh:condition:{i}:{c.kind.label}", condPremise Wd c, blockPath ++ ["conditions", toString i]))

def grantEdges (Wd : WeighDoc) (n : String) : List (String × String) :=
  (Wd.W.grants.filter (·.rule == n)).map (fun g => (g.party, g.grantor))

/-- `ρ` is reached from `π` through the grants on rule `n`: `π`'s grantor, that grantor's grantor, … -/
def grantReach (Wd : WeighDoc) (n π ρ : String) : Bool := VE.Closure.reachEval .plus (grantEdges Wd n) π ρ

/-- The parties `π`'s switch on rule `n` is granted through, in declared party order, `π` excluded (on an accepted
    document `π` never reaches itself: grant cycles are refused, 4.5). -/
def grantedThrough (Wd : WeighDoc) (n π : String) : List String :=
  Wd.D.soft.parties.filter (fun ρ => ρ != π && grantReach Wd n π ρ)

/-- `Grant_T` as necessary `.off` conditions on the grantee's switch (debate E3): the grant itself, then for each
    party the switch is granted through, that party's necessary switch conditions and that party's own grant. -/
def grantConds (Wd : WeighDoc) : List (String × CondDecl × RequestPath) :=
  Wd.W.grants.zipIdx.flatMap (fun (g, j) =>
    let tgt := Target.off g.rule g.party
    (s!"weigh:grant:{g.rule}:{g.party}", ⟨tgt, .necessary, atom g.predicate (ruleSorts Wd g.rule)⟩,
        blockPath ++ ["grants", toString j]) ::
    (grantedThrough Wd g.rule g.party).flatMap (fun ρ =>
      (Wd.W.conditions.zipIdx.filterMap (fun (c, i) =>
        if c.target == Target.off g.rule ρ && c.kind == .necessary then
          some (s!"weigh:grant:{g.rule}:{g.party}:condition:{i}", ⟨tgt, .necessary, c.condition⟩,
            blockPath ++ ["conditions", toString i])
        else none)) ++
      (Wd.W.grants.zipIdx.filterMap (fun (g', k) =>
        if g'.rule == g.rule && g'.party == ρ then
          some (s!"weigh:grant:{g.rule}:{g.party}:grant:{ρ}",
            ⟨tgt, .necessary, atom g'.predicate (ruleSorts Wd g.rule)⟩, blockPath ++ ["grants", toString k])
        else none))))

def grantEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  (grantConds Wd).map (fun (l, c, p) => (l, condPremise Wd c, p))

/-- `Weigh_T := Str_T ++ Dec_T ++ Grant_T`, each premise with its label and the request path of its entry. -/
def weighEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  strengthEntries Wd ++ condEntries Wd ++ grantEntries Wd

def strengthPremises (Wd : WeighDoc) : List VE.Formula := (strengthEntries Wd).map (·.2.1)
def weighLabelled (Wd : WeighDoc) : List (String × VE.Formula) := (weighEntries Wd).map (fun (l, φ, _) => (l, φ))
def weighOrigins (Wd : WeighDoc) : List (String × RequestPath) := (weighEntries Wd).map (fun (l, _, p) => (l, p))
def weighPremises (Wd : WeighDoc) : List VE.Formula := (weighLabelled Wd).map (·.2)

/-- The decision a target names, as soft's key (profile-composition 1.9: a reader finds a decision by its key). -/
def Target.key : Target → DecisionKey
  | .outweighs a L H => .outweighs a L H
  | .off n π => .off n π

/-- `Pack.conditions` (PK-1's field, profile-composition 1.9): each stated sufficient condition with its decision,
    in block order. Necessary conditions and grants export nothing. -/
def weighConditions (Wd : WeighDoc) : List (DecisionKey × VE.Formula) :=
  Wd.W.conditions.filterMap (fun c => if c.kind == .sufficient then some (c.target.key, c.condition) else none)

def atomsOf : VE.Formula → List VE.Formula
  | .unary p t => [.unary p t]
  | .binary p t w => [.binary p t w]
  | .eq t w => [.eq t w]
  | .not a => atomsOf a
  | .and a b | .or a b | .implies a b => atomsOf a ++ atomsOf b
  | _ => []

/-- A formula read propositionally: each distinct atom is a variable. -/
def evalProp (v : VE.Formula → Bool) : VE.Formula → Bool
  | .top => true
  | .bottom => false
  | .unary p t => v (.unary p t)
  | .binary p t w => v (.binary p t w)
  | .eq t w => v (.eq t w)
  | .not a => !evalProp v a
  | .and a b => evalProp v a && evalProp v b
  | .or a b => evalProp v a || evalProp v b
  | .implies a b => !evalProp v a || evalProp v b
  | .all _ _ | .ex _ _ => false

def subsetsOf {α : Type} : List α → List (List α)
  | [] => [[]]
  | x :: xs => (subsetsOf xs).map (x :: ·) ++ subsetsOf xs

def maxPropAtoms : Nat := 12

def propAtoms (a b : VE.Formula) : List VE.Formula := (atomsOf a ++ atomsOf b).eraseDups

/-- `a → b` holds under every truth assignment to their atoms. Sound (`propImplies_sound`), not complete: equality
    and definitions are not read (W-θ12). Decided exactly; it never searches. -/
def propImplies (a b : VE.Formula) : Bool :=
  VE.Norms.Formula.qfree a && VE.Norms.Formula.qfree b && decide ((propAtoms a b).length ≤ maxPropAtoms) &&
    (subsetsOf (propAtoms a b)).all (fun t =>
      !evalProp (fun φ => t.contains φ) a || evalProp (fun φ => t.contains φ) b)

def targetCheck (Wd : WeighDoc) (t : Target) : Except String Unit := do
  match t with
  | .outweighs a _ _ => if Wd.split.preds.any (·.2.1 == a) then throw (VE.Acts.splitRefusal "act" a)
  | .off n _ => if Wd.split.rules.any (·.2.1 == n) then throw (VE.Acts.splitRefusal "rule" n)
  unless targetExists Wd t do throw s!"NoSuchDecision: {renderTarget t}"

/-- Section 4, steps 3 to 7, in order. -/
def checkWeigh (Wd : WeighDoc) : Except String Unit := do
  let D := Wd.D
  for e in Wd.W.always do
    unless D.soft.outranks.contains e do throw s!"StrengthOnUndeclaredEdge: {e.1}, {e.2}"
    if Wd.W.always.count e > 1 then throw s!"DuplicateDeclaration: strength {e.1}, {e.2}"
  for (c, i) in Wd.W.conditions.zipIdx do
    targetCheck Wd c.target
    match c.target, c.kind with
    | .off _ _, .sufficient => throw s!"InvalidInput: condition {i} on a switch must be necessary"
    | .outweighs _ L H, _ =>
      if strictPair Wd H L then throw s!"ConditionOnStrictPair: {renderTarget c.target}"
    | _, _ => pure ()
    let Γ := (targetSorts Wd c.target).reverse
    typeDiagnostic D.E Γ c.condition
    unless c.condition.check D.E Γ do throw s!"InvalidInput: ill-typed condition {i}"
    if let some q := (preds c.condition).find? (fun q => definedOrRegulated D q || reservedPredicate q) then
      throw s!"InvalidInput: condition {i} mentions {q}"
    unless VE.Norms.Formula.qfree c.condition do throw s!"InvalidInput: condition {i} is not quantifier-free"
  for (f, i) in Wd.W.factors.zipIdx do
    targetCheck Wd f.target
    unless f.factors.length ≤ 16 && f.factors.all (·.utf8ByteSize ≤ 200) do
      throw s!"InvalidInput: invalid factors {i}"
  for g in Wd.W.grants do
    if (Wd.W.grants.filter (fun g' => g'.rule == g.rule && g'.party == g.party)).length > 1 then
      throw s!"DuplicateDeclaration: grant {g.rule}, {g.party}"
    targetCheck Wd (.off g.rule g.party)
    unless targetExists Wd (.off g.rule g.grantor) do
      throw s!"DelegationExceedsGrantor: rule {g.rule}, {g.party}, {g.grantor}"
    unless D.soft.instructionOf.contains (g.predicate, g.grantor) do
      throw s!"GrantNotAttributed: {g.predicate}, {g.grantor}"
    unless D.E.predicates g.predicate == some (ruleSorts Wd g.rule) do
      throw s!"InvalidInput: grant predicate {g.predicate} does not take the arguments of rule {g.rule}"
  for g in Wd.W.grants do
    if grantReach Wd g.rule g.party g.party then throw s!"DelegationCycle: rule {g.rule}, {g.party}"
  for (s, i) in Wd.W.conditions.zipIdx do
    if s.kind == .sufficient then
      for (n, j) in Wd.W.conditions.zipIdx do
        if n.kind == .necessary && n.target == s.target then
          if (propAtoms s.condition n.condition).length > maxPropAtoms then
            throw s!"ResourceLimit: conditions {i}, {j}"
          unless propImplies s.condition n.condition do
            throw s!"ConditionsDisagree: the checker cannot show that condition {i} implies condition {j}"
  for (l, φ) in weighLabelled Wd do
    unless withinLimits φ do throw s!"ResourceLimit: generated weighing premise {l}"

def weighWarnings (Wd : WeighDoc) : List String :=
  if Wd.D.soft.outranking = .strict then Wd.W.always.map (fun e => s!"StrengthInert: {e.1}, {e.2}") else []

def WellFormedWeigh (Wd : WeighDoc) : Bool :=
  WellFormedSoft Wd.D && (match checkWeigh Wd with
    | .ok () => true
    | .error _ => false)

/-! ## What an accepted block guarantees (weighing.md 1.6, steps 3 and 5) -/

/-- A loop body of `checkWeigh` never stops early (`only`), and what its success says (`all`). -/
local macro "wsimp" : tactic => `(tactic| ((try simp only [throw, throwThe, MonadExceptOf.throw, bind, Except.bind,
  pure, Except.pure]) <;> (repeat' split) <;> simp [Except.isOk, Except.toBool]))
local macro "wsimp_all" : tactic => `(tactic| ((try simp only [throw, throwThe, MonadExceptOf.throw, bind,
  Except.bind, pure, Except.pure]) <;> (repeat' split) <;> simp_all [Except.isOk, Except.toBool]))

theorem targetCheck_exists {Wd : WeighDoc} {t : Target} {u : Unit} (h : targetCheck Wd t = .ok u) :
    targetExists Wd t = true := by
  revert h; unfold targetCheck; wsimp_all

/-- Each `always` edge is declared; each grant's party and grantor hold a switch on its rule, and its predicate is
    the grantor's. -/
structure WeighFacts (Wd : WeighDoc) : Prop where
  always : ∀ e ∈ Wd.W.always, e ∈ Wd.D.soft.outranks
  grants : ∀ g ∈ Wd.W.grants, targetExists Wd (.off g.rule g.party) = true ∧
    targetExists Wd (.off g.rule g.grantor) = true ∧ (g.predicate, g.grantor) ∈ Wd.D.soft.instructionOf

theorem weighFacts (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) : WeighFacts Wd := by
  have hc : checkWeigh Wd = .ok () := by
    unfold WellFormedWeigh at h; revert h; split <;> simp_all
  unfold checkWeigh at hc
  simp only [VE.NormDefaults.ebind_ok] at hc
  obtain ⟨_, h1, _, h2, _, h3, _, h4, h5⟩ := hc
  clear h2 h3 h5
  refine ⟨fun e he => ?_, fun g hg => ?_⟩
  · clear h4
    have := VE.Acts.Lexical.forIn_ok h1 (by intro x; wsimp) e he
    clear h1; revert this; wsimp_all
  · clear h1
    have := VE.Acts.Lexical.forIn_ok h4 (by intro x; unfold targetCheck; wsimp) g hg
    clear h4; revert this
    rcases ht : targetCheck Wd (.off g.rule g.party) with _ | u <;> wsimp_all
    exact targetCheck_exists ht

/-! ## 5.1 Strength -/

theorem rankOrder_above (Wd : WeighDoc) (h : WellFormedSoft Wd.D = true) (a b : String) :
    outranksPlus Wd.D.soft a b = (rankOrder Wd).above a b :=
  VE.Closure.outranksPlus_eq_above _ (softValid_of_wellFormed _ h).ranks a b

theorem above_of_atLeast {o : VE.Closure.Order String} {a b c : String} (h₁ : o.atLeast a b = true)
    (h₂ : o.above b c = true) : o.above a c = true := by
  rw [VE.Closure.above_iff] at h₂ ⊢
  rcases (VE.Closure.atLeast_iff o a b).mp h₁ with rfl | h₁
  · exact h₂
  · exact h₁.trans h₂

theorem atLeast_of_above {o : VE.Closure.Order String} {a b : String} (h : o.above a b = true) :
    o.atLeast a b = true :=
  (VE.Closure.atLeast_iff o a b).mpr (.inr ((VE.Closure.above_iff o a b).mp h))

theorem strictPair_edge {Wd : WeighDoc} {H L : String} :
    strictPair Wd H L = true ↔ ∃ e ∈ Wd.W.always, (rankOrder Wd).atLeast H e.1 ∧ (rankOrder Wd).atLeast e.2 L := by
  simp [strictPair, List.any_eq_true]

/-- A strict pair is ordered. -/
theorem strictPair_outranks (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H L : String)
    (hs : strictPair Wd H L = true) : outranksPlus Wd.D.soft H L = true := by
  have hw : WellFormedSoft Wd.D = true := by simp_all [WellFormedWeigh]
  obtain ⟨e, he, h₁, h₂⟩ := strictPair_edge.mp hs
  have hab : (rankOrder Wd).above e.1 e.2 = true :=
    (VE.Closure.above_iff _ _ _).mpr (.single ((weighFacts Wd h).always e he))
  rw [rankOrder_above Wd hw]
  rcases (VE.Closure.atLeast_iff _ _ _).mp h₂ with h₂ | h₂
  · exact above_of_atLeast h₁ (h₂ ▸ hab)
  · exact above_of_atLeast h₁ ((VE.Closure.above_iff _ _ _).mpr
      (((VE.Closure.above_iff _ _ _).mp hab).trans h₂))

/-- An `always` edge is a strict pair. -/
theorem strictPair_of_always (Wd : WeighDoc) (a b : String) (hab : (a, b) ∈ Wd.W.always) :
    strictPair Wd a b = true :=
  strictPair_edge.mpr ⟨(a, b), hab, VE.Closure.atLeast_refl _ _, VE.Closure.atLeast_refl _ _⟩

/-- Strictness is inherited downward and upward along the order. -/
theorem strictPair_down (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H M L : String)
    (h₁ : strictPair Wd H M = true) (h₂ : outranksPlus Wd.D.soft M L = true) : strictPair Wd H L = true := by
  have hw : WellFormedSoft Wd.D = true := by simp_all [WellFormedWeigh]
  obtain ⟨e, he, ha, hb⟩ := strictPair_edge.mp h₁
  rw [rankOrder_above Wd hw] at h₂
  exact strictPair_edge.mpr ⟨e, he, ha, VE.Closure.atLeast_trans _ hb (atLeast_of_above h₂)⟩

theorem strictPair_up (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H M L : String)
    (h₁ : outranksPlus Wd.D.soft H M = true) (h₂ : strictPair Wd M L = true) : strictPair Wd H L = true := by
  have hw : WellFormedSoft Wd.D = true := by simp_all [WellFormedWeigh]
  obtain ⟨e, he, ha, hb⟩ := strictPair_edge.mp h₂
  rw [rankOrder_above Wd hw] at h₁
  exact strictPair_edge.mpr ⟨e, he, VE.Closure.atLeast_trans _ (atLeast_of_above h₁) ha, hb⟩

/-! ## 5.3 Conditions and grants -/

theorem filter_mem_subsetsOf {α : Type} (p : α → Bool) : ∀ l : List α, l.filter p ∈ subsetsOf l
  | [] => by simp [subsetsOf]
  | x :: xs => by by_cases hx : p x <;> simp [subsetsOf, hx, filter_mem_subsetsOf p xs]

/-- On a quantifier-free formula, the propositional reading agrees with `denote` when each atom does. -/
theorem evalProp_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) (v : VE.Formula → Bool) :
    ∀ a : VE.Formula, Formula.qfree a = true → (∀ φ ∈ atomsOf a, v φ = true ↔ φ.denote S ρ) →
      (evalProp v a = true ↔ a.denote S ρ)
  | .top, _, _ | .bottom, _, _ => by simp [evalProp, VE.Formula.denote]
  | .unary _ _, _, hv | .binary _ _ _, _, hv | .eq _ _, _, hv => hv _ (by simp [atomsOf])
  | .all _ _, hq, _ | .ex _ _, hq, _ => by simp [Formula.qfree] at hq
  | .not a, hq, hv => by
    have ih := evalProp_denote S ρ v a hq hv
    simp only [evalProp, VE.Formula.denote, ← ih]; cases evalProp v a <;> simp
  | .and a b, hq, hv | .or a b, hq, hv | .implies a b, hq, hv => by
    simp only [Formula.qfree, Bool.and_eq_true] at hq
    have ih₁ := evalProp_denote S ρ v a hq.1 (fun φ h => hv φ (by simp [atomsOf, h]))
    have ih₂ := evalProp_denote S ρ v b hq.2 (fun φ h => hv φ (by simp [atomsOf, h]))
    simp only [evalProp, VE.Formula.denote, ← ih₁, ← ih₂]
    cases evalProp v a <;> cases evalProp v b <;> simp

/-- The implication check is sound. -/
theorem propImplies_sound (a b : VE.Formula) (hp : propImplies a b = true) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (ha : a.denote S ρ) : b.denote S ρ := by
  classical
  simp only [propImplies, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hp
  obtain ⟨⟨⟨hqa, hqb⟩, _⟩, hall⟩ := hp
  let t := (propAtoms a b).filter (fun φ => decide (φ.denote S ρ))
  have hv : ∀ φ ∈ atomsOf a ++ atomsOf b, (t.contains φ = true ↔ φ.denote S ρ) := fun φ hφ => by
    simp [t, propAtoms, VE.EnglishGrammar.mem_eraseDups hφ]
  have key := hall t (filter_mem_subsetsOf _ _)
  rw [(evalProp_denote S ρ _ a hqa (fun φ h => hv φ (List.mem_append_left _ h))).mpr ha] at key
  simp only [Bool.not_true, Bool.false_or] at key
  exact (evalProp_denote S ρ _ b hqb (fun φ h => hv φ (List.mem_append_right _ h))).mp key

theorem condPremise_mem (Wd : WeighDoc) (c : CondDecl) (hc : c ∈ Wd.W.conditions) :
    condPremise Wd c ∈ weighPremises Wd := by
  rw [← List.zipIdx_map_fst 0 Wd.W.conditions] at hc
  obtain ⟨⟨c', i⟩, hm, rfl⟩ := List.mem_map.mp hc
  simp only [weighPremises, weighLabelled, weighEntries, condEntries, List.map_append, List.map_map,
    List.mem_append, List.mem_map]
  exact .inl (.inr ⟨(c', i), hm, rfl⟩)

/-- E3 and E6: outside a necessary condition its decision is false. Fixtures W-δ, W-ζ2, W-μ. -/
theorem condition_necessary (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (c : CondDecl) (hc : c ∈ Wd.W.conditions)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd c.target) vs) :
    c.kind = .necessary → ¬ c.condition.denote S (tupleVal vs) → ¬ (targetF Wd c.target).denote S (tupleVal vs) := by
  intro hk hn ht
  have h0 := hS _ (condPremise_mem Wd c hc)
  simp only [condPremise, hk] at h0
  exact hn ((bindAll_denote_nil S _ _).mp h0 vs typed ht)

/-- E4: inside a sufficient condition its decision is true. Fixtures W-ε, θ11. -/
theorem condition_sufficient (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (c : CondDecl) (hc : c ∈ Wd.W.conditions)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd c.target) vs) :
    c.kind = .sufficient → c.condition.denote S (tupleVal vs) → (targetF Wd c.target).denote S (tupleVal vs) := by
  intro hk hn
  have h0 := hS _ (condPremise_mem Wd c hc)
  simp only [condPremise, hk] at h0
  exact (bindAll_denote_nil S _ _).mp h0 vs typed hn

/-- A delegated switch works only where its grant holds. Fixture W-ζ. -/
theorem grant_needed (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (g : GrantDecl) (hg : g ∈ Wd.W.grants)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (ruleSorts Wd g.rule) vs)
    (hng : ¬ (atom g.predicate (ruleSorts Wd g.rule)).denote S (tupleVal vs)) :
    ¬ (targetF Wd (.off g.rule g.party)).denote S (tupleVal vs) := by
  rw [← List.zipIdx_map_fst 0 Wd.W.grants] at hg
  obtain ⟨⟨g', j⟩, hm, rfl⟩ := List.mem_map.mp hg
  have h0 := hS (condPremise Wd ⟨.off g'.rule g'.party, .necessary, atom g'.predicate (ruleSorts Wd g'.rule)⟩) (by
    simp only [weighPremises, weighLabelled, weighEntries, grantEntries, grantConds, List.map_append,
      List.map_map, List.mem_append, List.mem_map, List.mem_flatMap]
    exact .inr ⟨_, ⟨(g', j), hm, .head _⟩, rfl⟩)
  exact fun ht => hng ((bindAll_denote_nil S _ _).mp h0 vs typed ht)

/-- No party is granted a switch its grantor lacks. -/
theorem delegation_bounded (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (g : GrantDecl)
    (hg : g ∈ Wd.W.grants) :
    ∃ N ∈ Wd.D.T.nodes, N.name = g.rule ∧ g.party ∈ N.alterable ∧ g.grantor ∈ N.alterable ∧
      (g.predicate, g.grantor) ∈ Wd.D.soft.instructionOf := by
  obtain ⟨hp, hr, hi⟩ := (weighFacts Wd h).grants g hg
  simp only [targetExists] at hp hr
  cases hN : nodeNamed Wd.D g.rule with
  | none => simp [hN] at hp
  | some N =>
    simp only [hN, List.contains_iff_mem] at hp hr
    exact ⟨N, List.mem_of_find?_eq_some hN, by simpa using List.find?_some hN, hp, hr, hi⟩

/-! ## 5.4 Conservativity -/

theorem weighEntries_empty (D : SoftDoc) (sm : VE.Acts.SplitMap) : weighEntries ⟨D, WeighEnv.empty, sm⟩ = [] := by
  simp [weighEntries, strengthEntries, condEntries, grantEntries, grantConds, WeighEnv.empty]

/-- Plan D2: an empty block adds nothing. -/
theorem weigh_conservative (D : SoftDoc) (sm : VE.Acts.SplitMap) : weighPremises ⟨D, WeighEnv.empty, sm⟩ = [] := by
  simp [weighPremises, weighLabelled, weighEntries_empty]

theorem wellFormedWeigh_empty (D : SoftDoc) (sm : VE.Acts.SplitMap) :
    WellFormedWeigh ⟨D, WeighEnv.empty, sm⟩ = WellFormedSoft D := by
  simp only [WellFormedWeigh, checkWeigh, weighLabelled, weighEntries_empty]
  simp [WeighEnv.empty, pure, Except.pure, bind, Except.bind]

/-! ## 5.1 Chains and the paraphrase's witness -/

section Chains
variable {E : List (String × String)}

theorem atLeast_edge {o : VE.Closure.Order String} {a b : String} (h : (a, b) ∈ o.edges) :
    o.atLeast a b = true :=
  atLeast_of_above ((VE.Closure.above_iff _ _ _).mpr (.single h))

/-- The head of a chain of edges reaches each of its members. -/
theorem chain_head_reach (o : VE.Closure.Order String) :
    ∀ (a : String) (c : List String), (∀ e ∈ chainEdges (a :: c), e ∈ o.edges) →
      ∀ x ∈ a :: c, o.atLeast a x = true
  | a, [], _, x, hx => by simp at hx; subst hx; exact VE.Closure.atLeast_refl _ _
  | a, b :: rest, he, x, hx => by
    have hab : o.atLeast a b = true := atLeast_edge (he _ (by simp [chainEdges]))
    rcases List.mem_cons.mp hx with rfl | hx
    · exact VE.Closure.atLeast_refl _ _
    · exact VE.Closure.atLeast_trans _ hab
        (chain_head_reach o b rest (fun e h => he e (by simp [chainEdges, h])) x hx)

theorem chain_last_reach (o : VE.Closure.Order String) :
    ∀ (c : List String) (L : String), (∀ e ∈ chainEdges c, e ∈ o.edges) → c.getLast? = some L →
      ∀ x ∈ c, o.atLeast x L = true
  | [], _, _, h, _, _ => by simp at h
  | [a], L, _, h, x, hx => by simp at h hx; subst h hx; exact VE.Closure.atLeast_refl _ _
  | a :: b :: rest, L, he, h, x, hx => by
    have ih := chain_last_reach o (b :: rest) L (fun e h => he e (by simp [chainEdges, h]))
      (by simpa using h)
    rcases List.mem_cons.mp hx with rfl | hx
    · exact VE.Closure.atLeast_trans _ (atLeast_edge (he _ (by simp [chainEdges]))) (ih b (by simp))
    · exact ih x hx

theorem mem_chainEdges : ∀ {c : List String} {e : String × String}, e ∈ chainEdges c →
    e.1 ∈ c ∧ e.2 ∈ c
  | a :: b :: rest, e, h => by
    simp only [chainEdges, List.mem_cons] at h
    rcases h with rfl | h
    · simp
    · have := mem_chainEdges h; simp_all

theorem chainEdges_append : ∀ (l₁ l₂ : List String) (x y : String), l₁.getLast? = some x → l₂.head? = some y →
    chainEdges (l₁ ++ l₂) = chainEdges l₁ ++ (x, y) :: chainEdges l₂
  | [], _, _, _, h, _ => by simp at h
  | [a], b :: rest, x, y, h₁, h₂ => by simp at h₁ h₂; subst h₁ h₂; simp [chainEdges]
  | a :: a' :: rest, l₂, x, y, h₁, h₂ => by
    have := chainEdges_append (a' :: rest) l₂ x y (by simpa using h₁) h₂
    simp only [List.cons_append] at this ⊢
    simp [chainEdges, this]

/-- Reachability gives a chain of edges (a single node when the ends are equal). -/
theorem chain_of_atLeast (o : VE.Closure.Order String) {a b : String} (h : o.atLeast a b = true) :
    ∃ c : List String, c.head? = some a ∧ c.getLast? = some b ∧ ∀ e ∈ chainEdges c, e ∈ o.edges := by
  rcases (VE.Closure.atLeast_iff _ _ _).mp h with rfl | ht
  · exact ⟨[a], rfl, rfl, by simp [chainEdges]⟩
  · have hp := (VE.Closure.path_iff_transGen).mpr ht
    clear ht h
    induction hp with
    | edge h => exact ⟨[_, _], rfl, rfl, by simpa [chainEdges] using h⟩
    | @cons x y z h _ ih =>
      obtain ⟨c, hh, hl, he⟩ := ih
      match c, hh with
      | _ :: rest, rfl =>
        exact ⟨x :: y :: rest, rfl, by simpa using hl, by
          intro e he'
          simp only [chainEdges, List.mem_cons] at he'
          rcases he' with rfl | he'
          · exact h
          · exact he e he'⟩

theorem chainsFrom_chain : ∀ (f : Nat) (L a : String) (c : List String), c ∈ chainsFrom E L f a →
    c.head? = some a ∧ c.getLast? = some L ∧ 2 ≤ c.length ∧ ∀ e ∈ chainEdges c, e ∈ E
  | 0, _, _, _, h => by simp [chainsFrom] at h
  | f + 1, L, a, c, h => by
    simp only [chainsFrom, List.mem_flatMap, List.mem_filter, beq_iff_eq] at h
    obtain ⟨e, ⟨he, rfl⟩, hc⟩ := h
    split at hc
    · rename_i hL
      simp only [List.mem_singleton] at hc; subst hc
      have hL' : e.2 = L := by simpa using hL
      have : e = (e.1, L) := by rw [← hL']
      refine ⟨rfl, rfl, by simp, ?_⟩
      simp only [chainEdges, List.mem_singleton]; rintro _ rfl; rw [← this]; exact he
    · obtain ⟨c', hc', rfl⟩ := List.mem_map.mp hc
      obtain ⟨hh, hl, hlen, hE⟩ := chainsFrom_chain f L e.2 c' hc'
      match c', hh with
      | _ :: rest, rfl =>
        refine ⟨rfl, by simpa using hl, by simp, ?_⟩
        intro x hx
        simp only [chainEdges, List.mem_cons] at hx
        rcases hx with rfl | hx
        · exact he
        · exact hE x hx

theorem mem_chainsFrom : ∀ (f : Nat) (L a : String) (rest : List String), (a :: rest).Nodup →
    (a :: rest).getLast? = some L → 2 ≤ (a :: rest).length → (a :: rest).length ≤ f + 1 →
    (∀ e ∈ chainEdges (a :: rest), e ∈ E) → a :: rest ∈ chainsFrom E L f a
  | 0, _, _, rest, _, _, h₁, h₂, _ => by simp only [List.length_cons] at h₁ h₂; omega
  | f + 1, L, a, b :: rest, hn, hl, _, hlen, hE => by
    simp only [chainsFrom, List.mem_flatMap, List.mem_filter, beq_iff_eq]
    refine ⟨(a, b), ⟨hE _ (by simp [chainEdges]), rfl⟩, ?_⟩
    by_cases hb : b = L
    · subst hb
      cases rest with
      | nil => simp
      | cons x rest' =>
        exfalso
        have hlast : (x :: rest').getLast? = some b := by simpa using hl
        have := List.mem_of_getLast? hlast
        simp only [List.nodup_cons, List.mem_cons] at hn
        exact hn.2.1 (by simpa using this)
    · simp only [hb]
      cases rest with
      | nil => simp at hl; exact absurd hl hb
      | cons x rest' =>
        refine List.mem_map.mpr ⟨b :: x :: rest', mem_chainsFrom f L b (x :: rest') (List.nodup_cons.mp hn).2
          (by simpa using hl) (by simp) (by simp at hlen ⊢; omega)
          (fun e he => hE e (by simp [chainEdges] at he ⊢; exact .inr he)), rfl⟩

end Chains

theorem chain_nodup (Wd : WeighDoc) (hw : WellFormedSoft Wd.D = true) :
    ∀ c : List String, (∀ e ∈ chainEdges c, e ∈ Wd.D.soft.outranks) → c.Nodup
  | [], _ => List.nodup_nil
  | [_], _ => by simp
  | a :: b :: rest, he => by
    have hv := (softValid_of_wellFormed _ hw).ranks
    refine List.nodup_cons.mpr ⟨fun ha => ?_, chain_nodup Wd hw (b :: rest)
      (fun e h => he e (by simp [chainEdges, h]))⟩
    have hba : (rankOrder Wd).atLeast b a = true :=
      chain_head_reach (rankOrder Wd) b rest (fun e h => he e (by simp [chainEdges, h])) a ha
    have hab : (rankOrder Wd).above a b = true :=
      (VE.Closure.above_iff _ _ _).mpr (.single (he _ (by simp [chainEdges])))
    have := above_of_atLeast (VE.Closure.atLeast_refl _ a) (VE.Closure.atLeast_trans _ (atLeast_of_above hab) hba
      |> fun h => by
        rcases (VE.Closure.atLeast_iff _ _ _).mp hba with h' | h'
        · exact h' ▸ hab
        · exact (VE.Closure.above_iff _ _ _).mpr (((VE.Closure.above_iff _ _ _).mp hab).trans h'))
    rw [← rankOrder_above Wd hw, outranksPlus_irrefl hv] at this
    cases this

theorem nodup_length_le {α : Type} [DecidableEq α] : ∀ {l m : List α}, l.Nodup → l ⊆ m → l.length ≤ m.length
  | [], _, _, _ => Nat.zero_le _
  | a :: t, m, hn, hs => by
    obtain ⟨ha, ht⟩ := List.nodup_cons.mp hn
    have hm : a ∈ m := hs (List.mem_cons_self ..)
    have : t ⊆ m.erase a := fun x hx =>
      (List.mem_erase_of_ne (fun h : x = a => ha (h ▸ hx))).mpr (hs (List.mem_cons_of_mem _ hx))
    have := nodup_length_le ht this
    rw [List.length_erase_of_mem hm] at this
    have : 0 < m.length := List.length_pos_of_mem hm
    simp; omega

theorem chain_members_ranks (Wd : WeighDoc) (hw : WellFormedSoft Wd.D = true) :
    ∀ c : List String, 2 ≤ c.length → (∀ e ∈ chainEdges c, e ∈ Wd.D.soft.outranks) → ∀ x ∈ c, x ∈ Wd.D.soft.ranks
  | a :: b :: rest, _, he, x, hx => by
    have hd := (softValid_of_wellFormed _ hw).ranks.declared
    rcases List.mem_cons.mp hx with rfl | hx
    · exact (hd (x, b) (he _ (by simp [chainEdges]))).1
    · cases rest with
      | nil =>
        simp at hx; subst hx; exact (hd (a, x) (he _ (by simp [chainEdges]))).2
      | cons y rest' =>
        exact chain_members_ranks Wd hw (b :: y :: rest') (by simp)
          (fun e h => he e (by simp [chainEdges] at h ⊢; exact .inr h)) x hx

/-- A chain with an `always` edge makes its ends a strict pair. -/
theorem strictPair_of_chain {Wd : WeighDoc} {H L : String} {c : List String} (hc : RankChain Wd H L c)
    {e : String × String} (he : e ∈ chainEdges c) (ha : e ∈ Wd.W.always) : strictPair Wd H L = true := by
  obtain ⟨hh, hl, _, hE⟩ := hc
  obtain ⟨h₁, h₂⟩ := mem_chainEdges he
  match c, hh with
  | _ :: rest, rfl =>
    exact strictPair_edge.mpr ⟨e, ha, chain_head_reach (rankOrder Wd) H rest hE e.1 h₁,
      chain_last_reach (rankOrder Wd) _ L hE hl e.2 h₂⟩

/-- A strict pair has a chain through an `always` edge. -/
theorem chain_of_strictPair {Wd : WeighDoc} (h : WellFormedWeigh Wd = true) {H L : String}
    (hs : strictPair Wd H L = true) : ∃ c, RankChain Wd H L c ∧ ∃ e ∈ chainEdges c, e ∈ Wd.W.always := by
  obtain ⟨e, he, h₁, h₂⟩ := strictPair_edge.mp hs
  obtain ⟨c₁, hh₁, hl₁, hE₁⟩ := chain_of_atLeast _ h₁
  obtain ⟨c₂, hh₂, hl₂, hE₂⟩ := chain_of_atLeast _ h₂
  have heq := chainEdges_append c₁ c₂ e.1 e.2 hl₁ hh₂
  have hdecl := (weighFacts Wd h).always e he
  refine ⟨c₁ ++ c₂, ⟨?_, ?_, ?_, ?_⟩, e, by simp [heq], he⟩
  · match c₁, hh₁ with | _ :: _, rfl => rfl
  · rw [List.getLast?_append]; match c₂, hl₂ with | _ :: _, h => simpa using h
  · match c₁, c₂, hh₁, hh₂ with | _ :: _, _ :: _, _, _ => simp; omega
  · rw [heq]; intro x hx
    simp only [List.mem_append, List.mem_cons] at hx
    rcases hx with hx | rfl | hx
    · exact hE₁ x hx
    · exact hdecl
    · exact hE₂ x hx

/-- D4, exactly: a pair is holistic iff no chain of declared edges from `H` to `L` contains an `always` edge. -/
theorem holistic_iff_no_always_chain (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H L : String) :
    strictPair Wd H L = false ↔ ∀ c, RankChain Wd H L c → ∀ e ∈ chainEdges c, e ∉ Wd.W.always := by
  constructor
  · intro hf c hc e he ha
    rw [strictPair_of_chain hc he ha] at hf; cases hf
  · intro hall
    cases hs : strictPair Wd H L
    · rfl
    · obtain ⟨c, hc, e, he, ha⟩ := chain_of_strictPair h hs
      exact absurd ha (hall c hc e he)

theorem foldl_best_mem {l : List (List String)} :
    ∀ {init : Option (List String)} {c : List String},
      l.foldl (fun best c => match best with
        | none => some c
        | some b => if chainLt c b then some c else some b) init = some c → init = some c ∨ c ∈ l := by
  induction l with
  | nil => intro init c h; exact .inl h
  | cons x xs ih =>
    intro init c h
    rcases ih h with h' | h'
    · cases init with
      | none => simp at h'; exact .inr (by simp [h'])
      | some b =>
        simp only at h'
        split at h'
        · cases h'; exact .inr (by simp)
        · exact .inl h'
    · exact .inr (List.mem_cons_of_mem _ h')

theorem foldl_best_isSome (l : List (List String)) :
    ∀ (init : Option (List String)), (init.isSome ∨ l ≠ []) →
      (l.foldl (fun best c => match best with
        | none => some c
        | some b => if chainLt c b then some c else some b) init).isSome := by
  induction l with
  | nil => intro init h; simpa using h
  | cons x xs ih =>
    intro init _
    apply ih
    left
    cases init with
    | none => rfl
    | some b => simp only; split <;> rfl

/-- The chain the paraphrase names is a chain through an `always` edge. -/
theorem strictWitness_chain (Wd : WeighDoc) (H L : String) (c : List String)
    (hc : strictWitness Wd H L = some c) : RankChain Wd H L c ∧ ∃ e ∈ chainEdges c, e ∈ Wd.W.always := by
  rcases foldl_best_mem hc with h | h
  · cases h
  · obtain ⟨hm, ha⟩ := List.mem_filter.mp h
    obtain ⟨e, he, hae⟩ := List.any_eq_true.mp ha
    exact ⟨chainsFrom_chain _ L H c hm, e, he, by simpa using hae⟩

/-- The paraphrase names a chain exactly for strict pairs. -/
theorem strictWitness_isSome (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H L : String) :
    (strictWitness Wd H L).isSome = strictPair Wd H L := by
  have hw : WellFormedSoft Wd.D = true := by simp_all [WellFormedWeigh]
  cases hs : strictPair Wd H L
  · cases hw' : strictWitness Wd H L with
    | none => rfl
    | some c =>
      obtain ⟨hc, e, he, ha⟩ := strictWitness_chain Wd H L c hw'
      rw [strictPair_of_chain hc he ha] at hs; cases hs
  · obtain ⟨c, ⟨hh, hl, hlen, hE⟩, e, he, ha⟩ := chain_of_strictPair h hs
    apply foldl_best_isSome; right
    apply List.ne_nil_of_mem (a := c)
    refine List.mem_filter.mpr ⟨?_, List.any_eq_true.mpr ⟨e, he, by simpa using ha⟩⟩
    have hn := chain_nodup Wd hw c hE
    have hsub := chain_members_ranks Wd hw c hlen hE
    have hle : c.length ≤ Wd.D.soft.ranks.length := nodup_length_le hn hsub
    match c, hh with
    | _ :: rest, rfl => exact mem_chainsFrom _ L H rest hn hl hlen (by omega) hE

/-! ## What an accepted block guarantees: conditions, grants, soft's rule and environment checks -/

theorem except_isOk {ε α : Type} {e : Except ε α} : e.isOk = true ↔ ∃ a, e = .ok a := by
  cases e <;> simp [Except.isOk, Except.toBool]

theorem checkWeigh_ok (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) : checkWeigh Wd = .ok () := by
  unfold WellFormedWeigh at h; revert h; split <;> simp_all

/-- What `checkWeigh` says of each condition: its decision exists, a switch condition is necessary, no strict pair
    has one, and the condition is a typed, quantifier-free formula over base predicates. -/
theorem condFacts (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (c : CondDecl) (hc : c ∈ Wd.W.conditions) :
    targetExists Wd c.target = true ∧ (∀ n π, c.target = .off n π → c.kind = .necessary) ∧
      (∀ a L H, c.target = .outweighs a L H → strictPair Wd H L = false) ∧
      c.condition.check Wd.D.E (targetSorts Wd c.target).reverse = true ∧
      (∀ q ∈ preds c.condition, definedOrRegulated Wd.D q = false ∧ reservedPredicate q = false) ∧
      Formula.qfree c.condition = true := by
  have hk := checkWeigh_ok Wd h
  unfold checkWeigh at hk
  simp only [VE.NormDefaults.ebind_ok] at hk
  obtain ⟨_, -, _, h2, -⟩ := hk
  rw [← List.zipIdx_map_fst 0 Wd.W.conditions] at hc
  obtain ⟨⟨c', i⟩, hm, rfl⟩ := List.mem_map.mp hc
  have := VE.Acts.Lexical.forIn_ok h2 (by intro x; unfold targetCheck; wsimp) (c', i) hm
  clear h2 hc hm
  obtain ⟨tgt, kind, φ⟩ := c'
  obtain ⟨u, hu⟩ := except_isOk.mp this
  clear this
  simp only [VE.NormDefaults.ebind_ok] at hu
  obtain ⟨_, ht, hu⟩ := hu
  have hex := targetCheck_exists ht
  refine ⟨hex, ?_⟩
  cases tgt <;> cases kind <;> revert hu <;> (repeat' split) <;>
    simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind, pure, Except.pure] <;>
    (repeat' split) <;> simp_all
  all_goals
    rename_i hf _ _
    intro _ q hq
    have := List.find?_eq_none.mp (Option.eq_none_iff_forall_ne_some.mpr hf) q hq
    simpa using this

theorem grantFacts (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (g : GrantDecl) (hg : g ∈ Wd.W.grants) :
    Wd.D.E.predicates g.predicate = some (ruleSorts Wd g.rule) ∧ grantReach Wd g.rule g.party g.party = false := by
  have hk := checkWeigh_ok Wd h
  unfold checkWeigh at hk
  simp only [VE.NormDefaults.ebind_ok] at hk
  obtain ⟨_, -, _, -, _, -, _, h4, _, h5, -⟩ := hk
  constructor
  · have := VE.Acts.Lexical.forIn_ok h4 (by intro x; unfold targetCheck; wsimp) g hg
    clear h4 h5; revert this
    rcases ht : targetCheck Wd (.off g.rule g.party) with _ | u <;> wsimp_all
  · have := VE.Acts.Lexical.forIn_ok h5 (by intro x; wsimp) g hg
    clear h4 h5; revert this; wsimp_all

theorem disagreeFacts (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (s n : CondDecl)
    (hs : s ∈ Wd.W.conditions) (hn : n ∈ Wd.W.conditions) (hks : s.kind = .sufficient)
    (hkn : n.kind = .necessary) (ht : n.target = s.target) : propImplies s.condition n.condition = true := by
  have hk := checkWeigh_ok Wd h
  unfold checkWeigh at hk
  simp only [VE.NormDefaults.ebind_ok] at hk
  obtain ⟨_, -, _, -, _, -, _, -, _, -, _, h6, -⟩ := hk
  rw [← List.zipIdx_map_fst 0 Wd.W.conditions] at hs hn
  obtain ⟨⟨s', i⟩, hm, rfl⟩ := List.mem_map.mp hs
  obtain ⟨⟨n', j⟩, hm', rfl⟩ := List.mem_map.mp hn
  have := VE.Acts.Lexical.forIn_ok h6 (by intro x; wsimp) (s', i) hm
  clear h6
  simp only at hks hkn ht
  simp only [hks, beq_self_eq_true, if_true] at this
  obtain ⟨u, hu⟩ := except_isOk.mp this
  simp only [VE.NormDefaults.ebind_ok] at hu
  obtain ⟨_, hu, -⟩ := hu
  have := VE.Acts.Lexical.forIn_ok hu (by intro x; wsimp) (n', j) hm'
  clear hu
  simp only [hkn, ht, beq_self_eq_true, Bool.and_self, if_true] at this
  revert this; wsimp_all

theorem checkSoft_ok (D : SoftDoc) (h : WellFormedSoft D = true) : checkSoft D = .ok () := by
  unfold WellFormedSoft validateSoft at h
  split at h <;> rename_i heq
  · split at heq
    · cases heq
    · rename_i hc; cases hc' : checkSoft D <;> simp_all
  · cases h

/-- Soft's rule check: each party of a rule's `alterable` is declared. -/
theorem alterable_parties (D : SoftDoc) (h : WellFormedSoft D = true) (N : SoftNode) (hN : N ∈ D.T.nodes)
    (π : String) (hπ : π ∈ N.alterable) : π ∈ D.soft.parties := by
  have hk := checkSoft_ok D h
  unfold checkSoft at hk
  simp only [VE.NormDefaults.ebind_ok] at hk
  obtain ⟨_, -, _, -, _, -, _, -, _, h4, -⟩ := hk
  have := VE.Acts.Lexical.forIn_ok h4 (by intro x; wsimp) N hN
  clear h4
  obtain ⟨u, hu⟩ := except_isOk.mp this
  simp only [VE.NormDefaults.ebind_ok] at hu
  obtain ⟨_, hu, -⟩ := hu
  unfold checkSoftRule at hu
  have key : ∀ {β : Type} (f : String → PUnit → Except String (ForInStep PUnit)) (k : PUnit → Except String β)
      (b : β), (forIn N.alterable PUnit.unit f) >>= k = .ok b → (∀ x, f x PUnit.unit ≠ .ok (.done PUnit.unit)) →
      (∀ x, (f x PUnit.unit).isOk = true → D.soft.parties.contains x = true) → π ∈ D.soft.parties := by
    intro β f k b hb hf hc
    clear hu this
    obtain ⟨_, hb, -⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp hb
    simpa using hc π (VE.Acts.Lexical.forIn_ok hb hf π hπ)
  cases hr : N.rank <;> simp only [hr, pure_bind] at hu
  case some a =>
    by_cases ha : D.soft.ranks.contains a = true
    · rw [if_pos ha] at hu
      by_cases hs : sortedDistinct N.alterable = true
      · rw [if_pos hs] at hu; exact key _ _ _ hu (by intro x; wsimp) (by
        intro x; split <;> rename_i hx <;> intro hok
        · exact hx
        · simp [Except.isOk, Except.toBool, throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at hok)
      · rw [if_neg hs] at hu; exact (VE.Readings.throw_bind_ok hu).elim
    · rw [if_neg ha] at hu; exact (VE.Readings.throw_bind_ok hu).elim
  by_cases hs : sortedDistinct N.alterable = true
  · rw [if_pos hs] at hu; exact key _ _ _ hu (by intro x; wsimp) (by
        intro x; split <;> rename_i hx <;> intro hok
        · exact hx
        · simp [Except.isOk, Except.toBool, throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at hok)
  · rw [if_neg hs] at hu; exact (VE.Readings.throw_bind_ok hu).elim

/-! ## 5.3 Factors and inherited grants -/

/-- E5: factor lists add no premise. -/
theorem factors_inert (D : SoftDoc) (W : WeighEnv) (sm : VE.Acts.SplitMap) (fs : List FactorDecl) :
    weighPremises ⟨D, {W with factors := fs}, sm⟩ = weighPremises ⟨D, W, sm⟩ := rfl

theorem grantCond_mem (Wd : WeighDoc) {l : String} {cd : CondDecl} {p : RequestPath}
    (hm : (l, cd, p) ∈ grantConds Wd) : condPremise Wd cd ∈ weighPremises Wd := by
  simp only [weighPremises, weighLabelled, weighEntries, grantEntries, List.map_append, List.map_map,
    List.mem_append, List.mem_map]
  exact .inr ⟨(l, cd, p), hm, rfl⟩

theorem path_ends {α : Type} {R : α → α → Prop} {a b : α} (h : Relation.TransGen R a b) :
    (∃ x, R a x) ∧ ∃ y, R y b := by
  have hp := (VE.Closure.path_iff_transGen).mpr h
  clear h
  induction hp with
  | edge h => exact ⟨⟨_, h⟩, ⟨_, h⟩⟩
  | cons h _ ih => exact ⟨⟨_, h⟩, ih.2⟩

theorem mem_grantEdges {Wd : WeighDoc} {n x y : String} (h : (x, y) ∈ grantEdges Wd n) :
    ∃ g ∈ Wd.W.grants, g.rule = n ∧ g.party = x ∧ g.grantor = y := by
  simp only [grantEdges, List.mem_map, List.mem_filter, beq_iff_eq, Prod.mk.injEq] at h
  obtain ⟨g, ⟨hg, hr⟩, hx, hy⟩ := h
  exact ⟨g, hg, hr, hx, hy⟩

/-- :138 ("operators cannot grant users more than operator-level trust"): a switch carries every necessary
    condition and every grant of each party it is granted through (`ρ`: the grantor, its grantor, …).
    Fixtures W-ζ2, W-ζ3. -/
theorem grant_within_grantor (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (n π ρ : String) (hr : grantReach Wd n π ρ = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (ruleSorts Wd n) vs)
    (hoff : (targetF Wd (.off n π)).denote S (tupleVal vs)) :
    (∀ c ∈ Wd.W.conditions, c.target = .off n ρ → c.condition.denote S (tupleVal vs)) ∧
      (∀ g ∈ Wd.W.grants, g.rule = n → g.party = ρ →
        (atom g.predicate (ruleSorts Wd n)).denote S (tupleVal vs)) := by
  have hw : WellFormedSoft Wd.D = true := by simp_all [WellFormedWeigh]
  have hT : Relation.TransGen (fun x y => (x, y) ∈ grantEdges Wd n) π ρ :=
    (VE.Closure.above_iff (⟨[], grantEdges Wd n⟩ : VE.Closure.Order String) π ρ).mp hr
  obtain ⟨⟨x, hx⟩, ⟨y, hy⟩⟩ := path_ends hT
  obtain ⟨g, hg, hgr, hgp, -⟩ := mem_grantEdges hx
  obtain ⟨g', hg', hg'r, -, hg'g⟩ := mem_grantEdges hy
  -- `ρ` is a declared party other than `π`
  have hρ : ρ ∈ Wd.D.soft.parties := by
    have := ((weighFacts Wd h).grants g' hg').2.1
    simp only [targetExists] at this
    split at this
    · rename_i N hN
      exact alterable_parties Wd.D hw N (List.mem_of_find?_eq_some hN) ρ (by simpa [hg'g] using this)
    · cases this
  have hne : ρ ≠ π := by
    rintro rfl
    have := (grantFacts Wd h g hg).2
    rw [hgr, hgp, hr] at this; cases this
  have hthr : ρ ∈ grantedThrough Wd g.rule g.party := by
    simp [grantedThrough, hρ, hne, hgr, hgp, hr]
  rw [← List.zipIdx_map_fst 0 Wd.W.grants] at hg
  obtain ⟨⟨g₀, j⟩, hgj, rfl⟩ := List.mem_map.mp hg
  simp only at hgr hgp hthr
  have inst : ∀ φ : VE.Formula, condPremise Wd ⟨.off n π, .necessary, φ⟩ ∈ weighPremises Wd → φ.denote S (tupleVal vs) :=
    fun φ hm => by
      have h0 := hS _ hm
      simp only [condPremise, targetSorts] at h0
      exact (bindAll_denote_nil S _ _).mp h0 vs typed hoff
  constructor
  · intro c hc hct
    have hk := (condFacts Wd h c hc).2.1 n ρ hct
    rw [← List.zipIdx_map_fst 0 Wd.W.conditions] at hc
    obtain ⟨⟨c₀, i⟩, hci, rfl⟩ := List.mem_map.mp hc
    apply inst
    apply grantCond_mem Wd (l := s!"weigh:grant:{g₀.rule}:{g₀.party}:condition:{i}")
      (p := blockPath ++ ["conditions", toString i])
    simp only [grantConds, List.mem_flatMap, List.mem_cons, List.mem_append, List.mem_filterMap]
    refine ⟨(g₀, j), hgj, .inr ⟨ρ, hthr, .inl ⟨(c₀, i), hci, ?_⟩⟩⟩
    simp only at hct hk
    simp [hct, hk, hgr, hgp]
  · intro g₁ hg₁ hr₁ hp₁
    rw [← List.zipIdx_map_fst 0 Wd.W.grants] at hg₁
    obtain ⟨⟨g₂, k⟩, hgk, rfl⟩ := List.mem_map.mp hg₁
    apply inst
    apply grantCond_mem Wd (l := s!"weigh:grant:{g₀.rule}:{g₀.party}:grant:{ρ}")
      (p := blockPath ++ ["grants", toString k])
    simp only [grantConds, List.mem_flatMap, List.mem_cons, List.mem_append, List.mem_filterMap]
    refine ⟨(g₀, j), hgj, .inr ⟨ρ, hthr, .inr ⟨(g₂, k), hgk, ?_⟩⟩⟩
    simp only at hr₁ hp₁
    simp [hr₁, hp₁, hgr, hgp]

/-! ## 5.2 What `always` means -/

theorem inj_of_nodup_map {α β : Type} {f : α → β} :
    ∀ {l : List α}, (l.map f).Nodup → ∀ {x y}, x ∈ l → y ∈ l → f x = f y → x = y
  | [], _, _, _, hx, _, _ => absurd hx List.not_mem_nil
  | a :: l, h, x, y, hx, hy, e => by
    simp only [List.map_cons, List.nodup_cons, List.mem_map] at h
    rcases List.mem_cons.mp hx with hx' | hx' <;> rcases List.mem_cons.mp hy with hy' | hy'
    · rw [hx', hy']
    · subst hx'; exact absurd ⟨y, hy', e.symm⟩ h.1
    · subst hy'; exact absurd ⟨x, hx', e⟩ h.1
    · exact inj_of_nodup_map h.2 hx' hy' e

theorem incompatible_irrefl (D : SoftDoc) (M : SoftNode) : Incompatible D M M = false := by
  simp [Incompatible]

/-- `Str_T` has the premise of each `outweighs` decision of a strict pair. -/
theorem strength_mem (Wd : WeighDoc) {a L H : String} (ht : (a, L, H) ∈ outweighsTriples Wd.D)
    (hs : strictPair Wd H L = true) :
    bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H)) ∈ strengthPremises Wd := by
  obtain ⟨e, he, h₁, h₂⟩ := strictPair_edge.mp hs
  simp only [strengthPremises, strengthEntries, List.mem_map, List.mem_filterMap]
  cases hf : Wd.W.always.zipIdx.find? (fun (e, _) => (rankOrder Wd).atLeast H e.1 && (rankOrder Wd).atLeast e.2 L) with
  | none =>
    rw [← List.zipIdx_map_fst 0 Wd.W.always] at he
    obtain ⟨⟨e', i⟩, hm, rfl⟩ := List.mem_map.mp he
    have := List.find?_eq_none.mp hf (e', i) hm
    simp [h₁, h₂] at this
  | some x =>
    exact ⟨_, ⟨(a, L, H), ht, by simp only [hf]; rfl⟩, rfl⟩

/-- A colliding default pair, the first above the second, has `outweighs` triple `(act N, rk N, rk M)`. -/
theorem triple_mem (D : SoftDoc) (hw : WellFormedSoft D = true) (hol : D.soft.outranking = .holistic)
    {M N : SoftNode} (hM : M ∈ D.T.nodes) (hN : N ∈ D.T.nodes)
    (hMd : M.mode = .default) (hNd : N.mode = .default) (hi : Incompatible D M N = true)
    (hh : higher D M N = true) : (act D N, rk N, rk M) ∈ outweighsTriples D := by
  have hv := softValid_of_wellFormed D hw
  have hne : M.name ≠ N.name := by
    intro heq
    have : M = N := by
      have := hv.names
      exact inj_of_nodup_map this hM hN heq
    subst this; rw [incompatible_irrefl] at hi; cases hi
  have hc : Comparable D M N = true := by simp [Comparable, hh]
  have hna := higher_asymm hv.ranks hh
  simp only [outweighsTriples, hol, if_true, List.mem_reverse, mem_dedup, List.mem_filterMap]
  have hlt : M.name < N.name ∨ N.name < M.name := by
    by_cases h1 : M.name < N.name
    · exact .inl h1
    by_cases h2 : N.name < M.name
    · exact .inr h2
    exact absurd (String.le_antisymm (String.not_lt.mp h2) (String.not_lt.mp h1)) hne
  rcases hlt with hlt | hlt
  · exact ⟨(M, N), mem_collidingPairs.mpr ⟨hM, hN, hMd, hNd, hlt, hi⟩, by simp [hc, pairTriple, hh]⟩
  · have hc' : Comparable D N M = true := by simp [Comparable, hh]
    exact ⟨(N, M), mem_collidingPairs.mpr ⟨hN, hM, hNd, hMd, hlt, incompatible_symm D N M ▸ hi⟩,
      by simp [hc', pairTriple, hna]⟩

/-- `Str_T` at a typed tuple: a strict, colliding, higher-over-lower pair's `outweighs` atom is false. -/
theorem not_outweighs (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (strengthPremises Wd)) (hol : Wd.D.soft.outranking = .holistic) {M N : SoftNode}
    (hM : M ∈ Wd.D.T.nodes) (hN : N ∈ Wd.D.T.nodes) (hMd : M.mode = .default) (hNd : N.mode = .default)
    (hi : Incompatible Wd.D M N = true) (hh : higher Wd.D M N = true) (hs : strictPair Wd (rk M) (rk N) = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSortsOf Wd.D (act Wd.D N)) vs) :
    ¬ OutweighsD Wd.D S (tupleVal vs) (act Wd.D N) (rk N) (rk M) := by
  have hw : WellFormedSoft Wd.D = true := by simp_all [WellFormedWeigh]
  have h0 := hS _ (strength_mem Wd (triple_mem Wd.D hw hol hM hN hMd hNd hi hh) hs)
  exact (bindAll_denote_nil S _ _).mp h0 vs typed

/-- In every structure satisfying `Str_T`, an effective higher default rule dominates a colliding lower default
    rule of a strict pair. Fixtures W-α, W-β1. -/
theorem always_dominates (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (strengthPremises Wd)) (M N : SoftNode) (hM : M ∈ Wd.D.T.nodes) (hN : N ∈ Wd.D.T.nodes)
    (hMd : M.mode = .default) (hNd : N.mode = .default) (hi : Incompatible Wd.D M N = true)
    (hh : higher Wd.D M N = true) (hs : strictPair Wd (rk M) (rk N) = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSortsOf Wd.D (act Wd.D N)) vs)
    (heff : EffD Wd.D S (tupleVal vs) (rankFuel Wd.D) M) :
    DominatedD Wd.D S (tupleVal vs) (rankFuel Wd.D) N :=
  ⟨M, hM, hi, hMd, by simp [Comparable, hh], .inl ⟨hh, heff,
    fun hol => not_outweighs Wd h S hS hol hM hN hMd hNd hi hh hs vs typed⟩⟩

/-- ... and the lower rule never dominates the higher one by override: `DomWithD`'s override disjunct for `M` with
    opponent `N` is false (under the strict flag it is false by its first conjunct). Fixtures W-α, W-α′, W-β1. -/
theorem always_no_override (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (strengthPremises Wd)) (M N : SoftNode) (hM : M ∈ Wd.D.T.nodes) (hN : N ∈ Wd.D.T.nodes)
    (hMd : M.mode = .default) (hNd : N.mode = .default) (hi : Incompatible Wd.D M N = true)
    (hh : higher Wd.D M N = true) (hs : strictPair Wd (rk M) (rk N) = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSortsOf Wd.D (act Wd.D M)) vs) :
    ¬ (Wd.D.soft.outranking = .holistic ∧ higher Wd.D M N = true ∧ EligibleD Wd.D S (tupleVal vs) N ∧
        OutweighsD Wd.D S (tupleVal vs) (act Wd.D M) (rk N) (rk M)) := by
  rintro ⟨hol, -, -, ho⟩
  have hw : WellFormedSoft Wd.D = true := by simp_all [WellFormedWeigh]
  rw [act_eq (softValid_of_wellFormed _ hw) hi] at typed ho
  exact not_outweighs Wd h S hS hol hM hN hMd hNd hi hh hs vs typed ho

def strictFlag (D : SoftDoc) : SoftDoc :=
  { D with soft := { D.soft with outranking := .strict, outrankingDecider := none } }

section StrictFlag
variable (D : SoftDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S)

theorem strictFlag_higher : higher (strictFlag D) = higher D := rfl
theorem strictFlag_incompatible : Incompatible (strictFlag D) = Incompatible D := rfl
theorem strictFlag_comparable : Comparable (strictFlag D) = Comparable D := rfl
theorem strictFlag_children : children (strictFlag D) = children D := rfl
theorem strictFlag_rulesOn : rulesOn (strictFlag D) = rulesOn D := rfl
theorem strictFlag_act : act (strictFlag D) = act D := rfl
theorem strictFlag_live : LiveD (strictFlag D) S ρ = LiveD D S ρ := rfl
theorem strictFlag_outweighs : OutweighsD (strictFlag D) S ρ = OutweighsD D S ρ := rfl
theorem strictFlag_fuel : fuel (strictFlag D) = fuel D := rfl
theorem strictFlag_rankFuel : rankFuel (strictFlag D) = rankFuel D := rfl
theorem strictFlag_dualPerm : dualPerm (strictFlag D) = dualPerm D := rfl
theorem strictFlag_dualOblig : dualOblig (strictFlag D) = dualOblig D := rfl

theorem strictFlag_strictYields : ∀ f N, StrictYieldsD (strictFlag D) S ρ f N ↔ StrictYieldsD D S ρ f N
  | 0, N => by simp only [StrictYieldsD, strictFlag_live]
  | f + 1, N => by
    simp only [StrictYieldsD, strictFlag_live, strictFlag_children, strictFlag_strictYields f]

theorem strictFlag_strictDecides (p : String) (sign : Bool) :
    StrictDecidesD (strictFlag D) S ρ p sign ↔ StrictDecidesD D S ρ p sign := by
  simp only [StrictDecidesD, StrictSelectsD, strictFlag_rulesOn, strictFlag_live, strictFlag_children,
    strictFlag_fuel, strictFlag_strictYields]

theorem strictFlag_eligible (N : SoftNode) : EligibleD (strictFlag D) S ρ N ↔ EligibleD D S ρ N := by
  simp only [EligibleD, BlockedD, strictFlag_live, strictFlag_strictDecides, strictFlag_dualPerm,
    strictFlag_dualOblig]

end StrictFlag

theorem higher_outranks {D : SoftDoc} {M N : SoftNode} (h : higher D M N = true) :
    outranksPlus D.soft (rk M) (rk N) = true := by
  unfold higher at h
  split at h
  · rename_i a b hM hN; simpa [rk, hM, hN] using h
  · cases h

theorem cp_either (D : SoftDoc) (hw : WellFormedSoft D = true) {M N : SoftNode} (hM : M ∈ D.T.nodes)
    (hN : N ∈ D.T.nodes) (hMd : M.mode = .default) (hNd : N.mode = .default) (hi : Incompatible D M N = true) :
    (M, N) ∈ collidingPairs D ∨ (N, M) ∈ collidingPairs D := by
  have hv := softValid_of_wellFormed D hw
  have hne : M.name ≠ N.name := by
    intro heq
    have : M = N := inj_of_nodup_map hv.names hM hN heq
    subst this; rw [incompatible_irrefl] at hi; cases hi
  by_cases h1 : M.name < N.name
  · exact .inl (mem_collidingPairs.mpr ⟨hM, hN, hMd, hNd, h1, hi⟩)
  by_cases h2 : N.name < M.name
  · exact .inr (mem_collidingPairs.mpr ⟨hN, hM, hNd, hMd, h2, incompatible_symm D N M ▸ hi⟩)
  exact absurd (String.le_antisymm (String.not_lt.mp h2) (String.not_lt.mp h1)) hne

/-- Where every comparable colliding pair is strict, the document decides as the same document under the strict
    flag, on every structure satisfying `Str_T`, at tuples typed for the act. Fixtures W-β1 (both directions), W-β2
    (the hypothesis is needed). -/
theorem all_always_is_strict (Wd : WeighDoc) (h : WellFormedWeigh Wd = true)
    (hall : ∀ M N, (M, N) ∈ collidingPairs Wd.D → Comparable Wd.D M N = true →
      strictPair Wd (rk M) (rk N) = true ∨ strictPair Wd (rk N) (rk M) = true)
    (S : VE.Structure.{u}) (hS : Sat S (strengthPremises Wd)) (p : String) (sign : Bool)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSortsOf Wd.D (actKey Wd.D p)) vs) :
    DecidesSoftD Wd.D S (tupleVal vs) p sign ↔ DecidesSoftD (strictFlag Wd.D) S (tupleVal vs) p sign := by
  have hw : WellFormedSoft Wd.D = true := by simp_all [WellFormedWeigh]
  have hv := softValid_of_wellFormed _ hw
  -- the strict orientation of a comparable colliding pair, `M` above `N`
  have orient : ∀ M N, M ∈ Wd.D.T.nodes → N ∈ Wd.D.T.nodes → M.mode = .default → N.mode = .default →
      Incompatible Wd.D M N = true → higher Wd.D M N = true → strictPair Wd (rk M) (rk N) = true := by
    intro M N hM hN hMd hNd hi hh
    have hc : Comparable Wd.D M N = true := by simp [Comparable, hh]
    have hc' : Comparable Wd.D N M = true := by simp [Comparable, hh]
    have hwrong : strictPair Wd (rk N) (rk M) = true → False := fun hs => by
      have := outranksPlus_asymm hv.ranks (higher_outranks hh)
      rw [strictPair_outranks Wd h _ _ hs] at this; cases this
    rcases cp_either Wd.D hw hM hN hMd hNd hi with hp | hp
    · exact (hall M N hp hc).resolve_right hwrong
    · exact ((hall N M hp hc').resolve_left hwrong)
  -- one opponent: under `Str_T` the holistic body is the strict one
  have body : ∀ (eff : SoftNode → Prop) (M N : SoftNode), N ∈ Wd.D.T.nodes → N.mode = .default →
      act Wd.D N = actKey Wd.D p → M ∈ Wd.D.T.nodes → Incompatible Wd.D M N = true → M.mode = .default →
      (((higher Wd.D M N = true ∧ eff M ∧
          (Wd.D.soft.outranking = .holistic → ¬ OutweighsD Wd.D S (tupleVal vs) (act Wd.D N) (rk N) (rk M))) ∨
        (Wd.D.soft.outranking = .holistic ∧ higher Wd.D N M = true ∧ EligibleD Wd.D S (tupleVal vs) M ∧
          OutweighsD Wd.D S (tupleVal vs) (act Wd.D N) (rk M) (rk N))) ↔ higher Wd.D M N = true ∧ eff M) := by
    intro eff M N hN hNd ha hM hi hMd
    have tyN : VE.TupleTyped S (actSortsOf Wd.D (act Wd.D N)) vs := ha ▸ typed
    have hae := act_eq hv hi
    constructor
    · rintro (⟨hh, he, -⟩ | ⟨hol, hh, -, ho⟩)
      · exact ⟨hh, he⟩
      · exfalso
        have hi' : Incompatible Wd.D N M = true := incompatible_symm Wd.D N M ▸ hi
        rw [← hae] at ho
        exact not_outweighs Wd h S hS hol hN hM hNd hMd hi' hh (orient N M hN hM hNd hMd hi' hh) vs
          (hae ▸ tyN) ho
    · rintro ⟨hh, he⟩
      exact .inl ⟨hh, he, fun hol => not_outweighs Wd h S hS hol hM hN hMd hNd hi hh
        (orient M N hM hN hMd hNd hi hh) vs tyN⟩
  have eff : ∀ g N, N ∈ Wd.D.T.nodes → act Wd.D N = actKey Wd.D p →
      (EffD (strictFlag Wd.D) S (tupleVal vs) g N ↔ EffD Wd.D S (tupleVal vs) g N) := by
    intro g
    induction g with
    | zero => intro N _ _; exact strictFlag_eligible _ _ _ N
    | succ g ih =>
      intro N hN ha
      simp only [EffD, strictFlag_eligible]
      by_cases hNd : N.mode = .default
      · apply and_congr_right; intro _
        apply not_congr
        simp only [DomWithD, strictFlag_incompatible, strictFlag_comparable, strictFlag_higher]
        apply exists_congr; intro M
        constructor
        · rintro ⟨hM, hi, hMd, hc, hb⟩
          have hae : act Wd.D M = actKey Wd.D p := (act_eq hv hi).trans ha
          refine ⟨hM, hi, hMd, hc, (body _ M N hN hNd ha hM hi hMd).mpr ?_⟩
          rcases hb with ⟨hh, he, -⟩ | ⟨hf, -⟩
          · exact ⟨hh, (ih M hM hae).mp he⟩
          · cases hf
        · rintro ⟨hM, hi, hMd, hc, hb⟩
          have hae : act Wd.D M = actKey Wd.D p := (act_eq hv hi).trans ha
          obtain ⟨hh, he⟩ := (body _ M N hN hNd ha hM hi hMd).mp hb
          exact ⟨hM, hi, hMd, hc, .inl ⟨hh, (ih M hM hae).mpr he, fun hf => by cases hf⟩⟩
      · constructor <;> rintro ⟨⟨hd, _⟩, _⟩ <;> exact absurd hd hNd
  have applies : ∀ N, N ∈ Wd.D.T.nodes → act Wd.D N = actKey Wd.D p →
      (AppliesSoftD (strictFlag Wd.D) S (tupleVal vs) N ↔ AppliesSoftD Wd.D S (tupleVal vs) N) := by
    intro N hN ha
    unfold AppliesSoftD
    cases N.mode
    · exact Iff.rfl
    · exact eff _ N hN ha
  have yields : ∀ f N, N ∈ Wd.D.T.nodes → act Wd.D N = actKey Wd.D p →
      (YieldsSoftD (strictFlag Wd.D) S (tupleVal vs) f N ↔ YieldsSoftD Wd.D S (tupleVal vs) f N) := by
    intro f
    induction f with
    | zero => intro N hN ha; exact applies N hN ha
    | succ f ih =>
      intro N hN ha
      simp only [YieldsSoftD, strictFlag_children]
      apply or_congr (applies N hN ha)
      apply exists_congr; intro C
      apply and_congr_right; intro hC
      obtain ⟨hCn, hCp, -⟩ := mem_childrenIn_iff.mp hC
      exact ih C hCn (by simp only [act] at ha ⊢; rw [hCp]; exact ha)
  simp only [DecidesSoftD, SelectsSoftD, strictFlag_rulesOn, strictFlag_children, strictFlag_fuel]
  apply exists_congr; intro N
  apply and_congr_right; intro hN
  obtain ⟨hNn, hNp⟩ := List.mem_filter.mp hN
  have ha : act Wd.D N = actKey Wd.D p := by simp only [act]; rw [beq_iff_eq.mp hNp]
  apply and_congr_right; intro _
  apply and_congr (applies N hNn ha).symm
  apply not_congr
  apply exists_congr; intro C
  apply and_congr_right; intro hC
  obtain ⟨hCn, hCp, -⟩ := mem_childrenIn_iff.mp hC
  exact (yields _ C hCn (by simp only [act] at ha ⊢; rw [hCp]; exact ha)).symm

/-! ## 5.4 Typing, fragment, base-freedom -/

/-- The three kinds of `Weigh_T` premise. -/
theorem mem_weighPremises (Wd : WeighDoc) {φ : VE.Formula} (hφ : φ ∈ weighPremises Wd) :
    (∃ a L H, (a, L, H) ∈ outweighsTriples Wd.D ∧ strictPair Wd H L = true ∧
        φ = bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H))) ∨
      (∃ c ∈ Wd.W.conditions, φ = condPremise Wd c) ∨
      (∃ g ∈ Wd.W.grants, ∃ ψ, φ = condPremise Wd ⟨.off g.rule g.party, .necessary, ψ⟩ ∧
        ((∃ g' ∈ Wd.W.grants, g'.rule = g.rule ∧ ψ = atom g'.predicate (ruleSorts Wd g.rule)) ∨
          (∃ c ∈ Wd.W.conditions, ∃ ρ, c.target = .off g.rule ρ ∧ ψ = c.condition))) := by
  simp only [weighPremises, weighLabelled, weighEntries, List.map_append, List.map_map, List.mem_append,
    List.mem_map, Function.comp_def] at hφ
  rcases hφ with (⟨x, hx, rfl⟩ | ⟨x, hx, rfl⟩) | ⟨x, hx, rfl⟩
  · left
    simp only [strengthEntries, List.mem_filterMap] at hx
    obtain ⟨⟨a, L, H⟩, ht, hx⟩ := hx
    split at hx
    · rename_i e i hf
      cases hx
      have hp := List.find?_some hf
      have hm := List.mem_of_find?_eq_some hf
      simp only [Bool.and_eq_true] at hp
      have he : e ∈ Wd.W.always := by
        rw [← List.zipIdx_map_fst 0 Wd.W.always]; exact List.mem_map.mpr ⟨(e, i), hm, rfl⟩
      exact ⟨a, L, H, ht, strictPair_edge.mpr ⟨e, he, hp.1, hp.2⟩, rfl⟩
    · cases hx
  · right; left
    simp only [condEntries, List.mem_map] at hx
    obtain ⟨⟨c, i⟩, hm, rfl⟩ := hx
    refine ⟨c, ?_, rfl⟩
    rw [← List.zipIdx_map_fst 0 Wd.W.conditions]; exact List.mem_map.mpr ⟨(c, i), hm, rfl⟩
  · right; right
    simp only [grantEntries, List.mem_map] at hx
    obtain ⟨⟨l, cd, p⟩, hm, rfl⟩ := hx
    simp only [grantConds, List.mem_flatMap, List.mem_cons, List.mem_append, List.mem_filterMap] at hm
    obtain ⟨⟨g, j⟩, hgj, hm⟩ := hm
    have hg : g ∈ Wd.W.grants := by
      rw [← List.zipIdx_map_fst 0 Wd.W.grants]; exact List.mem_map.mpr ⟨(g, j), hgj, rfl⟩
    refine ⟨g, hg, ?_⟩
    rcases hm with hm | ⟨ρ, -, ⟨⟨c, i⟩, hci, hm⟩ | ⟨⟨g', k⟩, hgk, hm⟩⟩
    · cases hm; exact ⟨_, rfl, .inl ⟨g, hg, rfl, rfl⟩⟩
    · split at hm
      · rename_i hc
        cases hm
        simp only [Bool.and_eq_true, beq_iff_eq] at hc
        have hcm : c ∈ Wd.W.conditions := by
          rw [← List.zipIdx_map_fst 0 Wd.W.conditions]; exact List.mem_map.mpr ⟨(c, i), hci, rfl⟩
        exact ⟨_, rfl, .inr ⟨c, hcm, ρ, hc.1, rfl⟩⟩
      · cases hm
    · split at hm
      · rename_i hc
        cases hm
        simp only [Bool.and_eq_true, beq_iff_eq] at hc
        have hgm : g' ∈ Wd.W.grants := by
          rw [← List.zipIdx_map_fst 0 Wd.W.grants]; exact List.mem_map.mpr ⟨(g', k), hgk, rfl⟩
        exact ⟨_, rfl, .inl ⟨g', hgm, hc.1, rfl⟩⟩
      · cases hm

/-- Soft's environment check: an `instruction_of` predicate is a declared base predicate. -/
theorem instructionOf_base (D : SoftDoc) (h : WellFormedSoft D = true) (p π : String)
    (hp : (p, π) ∈ D.soft.instructionOf) : definedOrRegulated D p = false := by
  have hk := checkSoft_ok D h
  unfold checkSoft at hk
  obtain ⟨_, hk, -⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp hk
  unfold checkSoftEnv at hk
  simp only [pure_bind] at hk
  by_cases h1 : D.soft.parties.length > 8
  · rw [if_pos h1] at hk; exact (VE.Readings.throw_bind_ok hk).elim
  rw [if_neg h1] at hk
  by_cases h2 : D.soft.ranks.length > 16
  · rw [if_pos h2] at hk; exact (VE.Readings.throw_bind_ok hk).elim
  rw [if_neg h2] at hk
  rcases h3 : dupOf D.soft.ranks with _ | _
  rotate_left; · simp only [h3] at hk; exact (VE.Readings.throw_bind_ok hk).elim
  simp only [h3] at hk
  rcases h4 : dupOf D.soft.parties with _ | _
  rotate_left; · simp only [h4] at hk; exact (VE.Readings.throw_bind_ok hk).elim
  simp only [h4] at hk
  obtain ⟨_, -, hk⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp hk
  obtain ⟨_, -, hk⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp hk
  clear h1 h2 h3 h4
  split at hk
  · exact (VE.Readings.throw_bind_ok hk).elim
  try simp only [pure_bind] at hk
  split at hk
  · exact (VE.Readings.throw_bind_ok hk).elim
  try simp only [pure_bind] at hk
  obtain ⟨_, -, hk⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp hk
  obtain ⟨_, -, hk⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp hk
  obtain ⟨_, -, hk⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp hk
  obtain ⟨_, hk, -⟩ := (VE.NormDefaults.ebind_ok _ _ _).mp hk
  have := VE.Acts.Lexical.forIn_ok hk (by intro x; wsimp) (p, π) hp
  clear hk; revert this
  cases hc : D.soft.parties.contains π <;> cases hd : definedOrRegulated D p <;>
    simp [hc, hd, throw, throwThe, MonadExceptOf.throw, Except.isOk, Except.toBool, pure, Except.pure, bind,
      Except.bind]

theorem preds_declared {E : VE.Environment} : ∀ (φ : VE.Formula) (Γ : List String), φ.WellFormed E Γ →
    ∀ q ∈ preds φ, (E.predicates q).isSome
  | .top, _, _, q, hq | .bottom, _, _, q, hq | .eq _ _, _, _, q, hq => by simp [preds] at hq
  | .unary p _, _, ⟨_, hp, _⟩, q, hq | .binary p _ _, _, ⟨_, _, hp, _⟩, q, hq => by
    simp [preds] at hq; subst hq; simp [hp]
  | .not a, Γ, hw, q, hq => preds_declared a Γ hw q hq
  | .and a b, Γ, hw, q, hq | .or a b, Γ, hw, q, hq | .implies a b, Γ, hw, q, hq => by
    rcases List.mem_append.mp hq with hq | hq
    · exact preds_declared a Γ hw.1 q hq
    · exact preds_declared b Γ hw.2 q hq
  | .all s a, Γ, hw, q, hq | .ex s a, Γ, hw, q, hq => preds_declared a (s :: Γ) hw.2 q hq

/-- Typing reads only the declarations of the predicates a formula mentions. -/
theorem wf_congr {E E' : VE.Environment} (hs : E'.sorts = E.sorts) (hc : E'.constants = E.constants) :
    ∀ (φ : VE.Formula) (Γ : List String), (∀ q ∈ preds φ, E'.predicates q = E.predicates q) →
      φ.WellFormed E Γ → φ.WellFormed E' Γ
  | .top, _, _, h | .bottom, _, _, h => h
  | .unary p t, Γ, hp, ⟨s, h₁, h₂⟩ => by
    refine ⟨s, by rw [hp p (by simp [preds])]; exact h₁, ?_⟩
    cases t <;> simp_all [VE.Term.sortOf]
  | .binary p t w, Γ, hp, ⟨s, r, h₁, h₂, h₃⟩ => by
    refine ⟨s, r, by rw [hp p (by simp [preds])]; exact h₁, ?_, ?_⟩ <;>
    · first | (cases t <;> simp_all [VE.Term.sortOf]) | (cases w <;> simp_all [VE.Term.sortOf])
  | .eq t w, Γ, _, ⟨s, h₁, h₂⟩ => by
    refine ⟨s, ?_, ?_⟩
    · cases t <;> simp_all [VE.Term.sortOf]
    · cases w <;> simp_all [VE.Term.sortOf]
  | .not a, Γ, hp, h => wf_congr hs hc a Γ hp h
  | .and a b, Γ, hp, h | .or a b, Γ, hp, h | .implies a b, Γ, hp, h =>
    ⟨wf_congr hs hc a Γ (fun q hq => hp q (List.mem_append_left _ hq)) h.1,
     wf_congr hs hc b Γ (fun q hq => hp q (List.mem_append_right _ hq)) h.2⟩
  | .all s a, Γ, hp, h | .ex s a, Γ, hp, h => ⟨hs ▸ h.1, wf_congr hs hc a (s :: Γ) hp h.2⟩

theorem bindAll_wf {E : VE.Environment} (body : VE.Formula) :
    ∀ (ss Γ : List String), (∀ s ∈ ss, s ∈ E.sorts) → body.WellFormed E (ss.reverse ++ Γ) →
      (bindAll ss body).WellFormed E Γ
  | [], _, _, h => h
  | s :: ss, Γ, hs, h => ⟨hs s (List.mem_cons_self ..), bindAll_wf body ss (s :: Γ)
      (fun x hx => hs x (List.mem_cons_of_mem _ hx)) (by simpa using h)⟩

theorem atom_wf {E : VE.Environment} {p : String} {ss : List String} (h : E.predicates p = some ss)
    (Γ : List String) : (atom p ss).WellFormed E (ss.reverse ++ Γ) := by
  match ss, h with
  | [x], h => exact ⟨x, h, rfl⟩
  | [x, y], h => exact ⟨x, y, h, rfl, rfl⟩
  | [], _ => trivial
  | _ :: _ :: _ :: _, _ => trivial

theorem universalQF_bindAll (body : VE.Formula) :
    ∀ ss : List String, universalQF (bindAll ss body) = universalQF body
  | [] => rfl
  | _ :: ss => universalQF_bindAll body ss

theorem qfree_atom (p : String) (ss : List String) : Formula.qfree (atom p ss) = true := by
  unfold atom; split <;> rfl

theorem universalQF_qfree {φ : VE.Formula} (h : Formula.qfree φ = true) : universalQF φ = true := by
  cases φ <;> simp_all [universalQF, Formula.qfree]

theorem qfree_target (Wd : WeighDoc) (t : Target) : Formula.qfree (targetF Wd t) = true := by
  cases t with
  | outweighs => exact qfree_atom _ _
  | off n π => simp only [targetF]; split <;> simp [qfree_atom, Formula.qfree]

section Typing
variable (Wd : WeighDoc) (h : WellFormedWeigh Wd = true)
include h

theorem wfSoft : WellFormedSoft Wd.D = true := by simp_all [WellFormedWeigh]

/-- A base predicate a condition or grant mentions is declared at level 0 as in `E`. -/
theorem envAt_base {q : String} (hq : definedOrRegulated Wd.D q = false) (hd : (Wd.D.E.predicates q).isSome) :
    (envAt (soften Wd.D) 0).predicates q = Wd.D.E.predicates q := by
  have hw := wfSoft Wd h
  have hv := softValid_of_wellFormed _ hw
  refine VE.Readings.envAt_other 0 (fun hl => ?_) (fun hn => ?_)
  · rcases VE.Readings.layer_mem q hl with ⟨r, hr, rfl⟩ | ⟨dd, hdd, rfl⟩ <;>
      simp [definedOrRegulated, List.contains_iff_mem] at hq
    · exact hq.1 r hr rfl
    · exact hq.2 dd hdd rfl
  · rw [hv.decFresh _ hn] at hd; cases hd

theorem envAt_target {t : Target} (ht : targetExists Wd t = true) :
    (targetF Wd t).WellFormed (envAt (soften Wd.D) 0) (targetSorts Wd t).reverse := by
  have hw := wfSoft Wd h
  cases t with
  | outweighs a L H =>
    have hd : (outweighsName a L H, actSortsOf Wd.D a) ∈ decisions Wd.D :=
      VE.Readings.mem_decisions.mpr (.inr (.inr ⟨a, L, H, by simpa [targetExists] using ht, rfl⟩))
    simpa using atom_wf (VE.Readings.envAt_decision hw 0 hd) []
  | off n π =>
    simp only [targetExists] at ht
    simp only [targetF, targetSorts, ruleSorts]
    split
    · rename_i N hN
      rw [hN] at ht
      have hd : (offName N π, sortsOf Wd.D N.pred) ∈ decisions Wd.D :=
        VE.Readings.mem_decisions.mpr (.inr (.inl ⟨N, List.mem_of_find?_eq_some hN, π, by simpa using ht, rfl⟩))
      simpa using atom_wf (VE.Readings.envAt_decision hw 0 hd) []
    · trivial

theorem targetSorts_sorts (t : Target) : ∀ s ∈ targetSorts Wd t, s ∈ (envAt (soften Wd.D) 0).sorts := by
  have hw := wfSoft Wd h
  intro s hs
  cases t with
  | outweighs a L H => exact VE.Readings.sortsOf_sorts hw a s hs
  | off n π =>
    simp only [targetSorts, ruleSorts] at hs
    split at hs
    · exact VE.Readings.sortsOf_sorts hw _ s hs
    · cases hs

/-- A condition, typed in `E` over its target's arguments, is typed at level 0. -/
theorem condition_wf (c : CondDecl) (hc : c ∈ Wd.W.conditions) :
    c.condition.WellFormed (envAt (soften Wd.D) 0) (targetSorts Wd c.target).reverse := by
  obtain ⟨_, _, _, hck, hpr, _⟩ := condFacts Wd h c hc
  have hwf := (VE.check_iff_wellFormed _ _ _).mp hck
  exact wf_congr (E := Wd.D.E) (E' := envAt (soften Wd.D) 0) rfl rfl _ _
    (fun q hq => envAt_base Wd h (hpr q hq).1 (preds_declared _ _ hwf q hq)) hwf

theorem grantAtom_wf (g : GrantDecl) (hg : g ∈ Wd.W.grants) :
    (atom g.predicate (ruleSorts Wd g.rule)).WellFormed (envAt (soften Wd.D) 0) (ruleSorts Wd g.rule).reverse := by
  have hp := (grantFacts Wd h g hg).1
  have hi := ((weighFacts Wd h).grants g hg).2.2
  have hb := instructionOf_base Wd.D (wfSoft Wd h) _ _ hi
  have := atom_wf (E := envAt (soften Wd.D) 0) (by rw [envAt_base Wd h hb (by simp [hp]), hp]) []
  simpa using this

/-- Every premise of `Weigh_T` is a universal quantifier-free formula, closed and typed at level 0. -/
theorem premise_facts (φ : VE.Formula) (hφ : φ ∈ weighPremises Wd) :
    universalQF φ = true ∧ φ.WellFormed (envAt (soften Wd.D) 0) [] := by
  have hw := wfSoft Wd h
  rcases mem_weighPremises Wd hφ with ⟨a, L, H, ht, -, rfl⟩ | ⟨c, hc, rfl⟩ | ⟨g, hg, ψ, rfl, hψ⟩
  · refine ⟨by rw [universalQF_bindAll]; simp [universalQF, Formula.qfree, outweighsF, qfree_atom], ?_⟩
    have hd : (outweighsName a L H, actSortsOf Wd.D a) ∈ decisions Wd.D :=
      VE.Readings.mem_decisions.mpr (.inr (.inr ⟨a, L, H, ht, rfl⟩))
    exact bindAll_wf _ _ [] (VE.Readings.sortsOf_sorts hw a)
      (by simpa using atom_wf (VE.Readings.envAt_decision hw 0 hd) [])
  · obtain ⟨hex, _, _, _, _, hq⟩ := condFacts Wd h c hc
    have ht := envAt_target Wd h hex
    have hcw := condition_wf Wd h c hc
    unfold condPremise
    cases c.kind <;> simp only
    · refine ⟨by rw [universalQF_bindAll]; simp [universalQF, Formula.qfree, hq, qfree_target], ?_⟩
      exact bindAll_wf _ _ [] (targetSorts_sorts Wd h _) (by simpa using (⟨ht, hcw⟩ : _ ∧ _))
    · refine ⟨by rw [universalQF_bindAll]; simp [universalQF, Formula.qfree, hq, qfree_target], ?_⟩
      exact bindAll_wf _ _ [] (targetSorts_sorts Wd h _) (by simpa using (⟨hcw, ht⟩ : _ ∧ _))
  · have hex := ((weighFacts Wd h).grants g hg).1
    have ht := envAt_target Wd h hex
    have hψ' : Formula.qfree ψ = true ∧
        ψ.WellFormed (envAt (soften Wd.D) 0) (targetSorts Wd (.off g.rule g.party)).reverse := by
      rcases hψ with ⟨g', hg', hr, rfl⟩ | ⟨c, hc, ρ, hct, rfl⟩
      · refine ⟨qfree_atom _ _, ?_⟩
        have := grantAtom_wf Wd h g' hg'
        rw [hr] at this; exact this
      · refine ⟨(condFacts Wd h c hc).2.2.2.2.2, ?_⟩
        have := condition_wf Wd h c hc
        rw [hct] at this; exact this
    refine ⟨by simp [condPremise, universalQF_bindAll, universalQF, Formula.qfree, hψ'.1, qfree_target], ?_⟩
    exact bindAll_wf _ _ [] (targetSorts_sorts Wd h _) (by simpa using (⟨ht, hψ'.2⟩ : _ ∧ _))

end Typing

/-- Weighing's typing obligation to PK-1 (provider obligation 2): closed base formulas of the filled environment. -/
theorem weighPremises_wellFormed (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : VE.NormDefaults.WellFormedU ⟨soften Wd.D, unspec⟩ = true) :
    ∀ a ∈ weighPremises Wd, a.WellFormed (envAt (VE.NormDefaults.fill ⟨soften Wd.D, unspec⟩) 0) [] := by
  intro a ha
  exact VE.Definitions.wf_mono (E := envAt (soften Wd.D) 0)
    (E' := envAt (VE.NormDefaults.fill ⟨soften Wd.D, unspec⟩) 0) rfl rfl
    (VE.NormDefaults.envAt_fill_mono (VE.NormDefaults.uvalid hw) 0) a [] (premise_facts Wd h a ha).2

/-- The fragment (soft's gate, plan D6): every premise survives sort-respecting substructures. -/
theorem weighPremises_substructure (Wd : WeighDoc) (h : WellFormedWeigh Wd = true)
    (B₀ B : VE.Structure.{u}) (hsub : BaseSubstructure Wd.D B₀ B) (hs : Sat B (weighPremises Wd)) :
    Sat B₀ (weighPremises Wd) := by
  obtain ⟨e, hinj, hd, hc, hr⟩ := hsub
  intro a ha
  obtain ⟨hu, hwf⟩ := premise_facts Wd h a ha
  exact universal_down e hinj hc hr hd a [] [] hu hwf (hs a ha)

/-! ## Base-freedom -/

theorem regulatedName_arity (D : SoftDoc) (hw : WellFormedSoft D = true) {a : String}
    (ha : a ∈ D.T.regulated.map (·.name)) : Arity (sortsOf D a) := by
  have hv := softValid_of_wellFormed D hw
  have hvn := VE.Norms.valid_of_wellFormed _ hv.wf
  unfold sortsOf sortsIn
  cases hf : D.T.regulated.find? (·.name == a) with
  | none =>
    obtain ⟨r, hr, rfl⟩ := List.mem_map.mp ha
    exact absurd (List.find?_eq_none.mp hf r hr) (by simp)
  | some r => exact VE.Norms.regulated_arity hvn (hvn.regulated r (List.mem_of_find?_eq_some hf))

theorem act_arity (D : SoftDoc) (hw : WellFormedSoft D = true) {N : SoftNode} (hN : N ∈ D.T.nodes) :
    Arity (actSortsOf D (act D N)) := by
  have hv := softValid_of_wellFormed D hw
  have hvn := VE.Norms.valid_of_wellFormed _ hv.wf
  unfold actSortsOf act actKey
  cases hd : dualPerm D N.pred with
  | none => exact regulatedName_arity D hw (hv.predReg N hN)
  | some m =>
    obtain ⟨pr, hpr, -, rfl⟩ := dualPerm_some (D := D) hd
    obtain ⟨-, -, m', hm', hmn, -⟩ := hvn.pairs pr hpr
    exact regulatedName_arity D hw (List.mem_map.mpr ⟨m', VE.Norms.mem_syms_reg hm', hmn⟩)

theorem triple_arity (D : SoftDoc) (hw : WellFormedSoft D = true) {a L H : String}
    (ht : (a, L, H) ∈ outweighsTriples D) : Arity (actSortsOf D a) := by
  unfold outweighsTriples at ht
  split at ht
  · simp only [List.mem_reverse, mem_dedup, List.mem_filterMap] at ht
    obtain ⟨⟨M, N⟩, hp, ht⟩ := ht
    obtain ⟨hM, hN, -⟩ := mem_collidingPairs.mp hp
    split at ht
    · simp only [Option.some.injEq] at ht
      unfold pairTriple at ht
      split at ht <;> simp only [Prod.mk.injEq] at ht <;> rw [← ht.1]
      · exact act_arity D hw hN
      · exact act_arity D hw hM
    · cases ht
  · cases ht

/-! ## `strength_iff` (5.1): `outweighsName` is injective on the names a well-formed document reaches -/

/-- A split at `__` after a dunder-free head and before a tail not starting with `_` is unique. -/
theorem split_dunder_left : ∀ (k k' p p' : List Char),
    (∀ u v, k ≠ u ++ '_' :: '_' :: v) → (∀ u v, k' ≠ u ++ '_' :: '_' :: v) →
    p.head? ≠ some '_' → p'.head? ≠ some '_' →
    k ++ '_' :: '_' :: p = k' ++ '_' :: '_' :: p' → k = k' ∧ p = p'
  | [], [], _, _, _, _, _, _, h => by simpa using h
  | [], c :: k', p, p', _, hk', h0, _, h => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h
    obtain ⟨rfl, h⟩ := h
    cases k' with
    | nil => simp at h; obtain ⟨_, rfl⟩ := h; simp at h0
    | cons d k'' =>
      simp only [List.cons_append, List.cons.injEq] at h
      obtain ⟨rfl, -⟩ := h
      exact absurd rfl (hk' [] k'')
  | c :: k, [], p, p', hk, _, _, h0', h => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h
    obtain ⟨rfl, h⟩ := h
    cases k with
    | nil => simp at h; obtain ⟨_, rfl⟩ := h; simp at h0'
    | cons d k'' =>
      simp only [List.cons_append, List.cons.injEq] at h
      obtain ⟨rfl, -⟩ := h
      exact absurd rfl (hk [] k'')
  | c :: k, c' :: k', p, p', hk, hk', h0, h0', h => by
    simp only [List.cons_append, List.cons.injEq] at h
    obtain ⟨rfl, h⟩ := h
    obtain ⟨h1, h2⟩ := split_dunder_left k k' p p' (fun u v e => hk (c :: u) v (by simp [e]))
      (fun u v e => hk' (c :: u) v (by simp [e])) h0 h0' h
    exact ⟨by rw [h1], h2⟩

/-- `outweighsName` is injective on valid rank names and acts not starting with `_`. -/
theorem outweighsName_inj {a L H a' L' H' : String} (hL : validSoftName L = true) (hL' : validSoftName L' = true)
    (hH : validSoftName H = true) (hH' : validSoftName H' = true) (ha : a.data.head? ≠ some '_')
    (ha' : a'.data.head? ≠ some '_') (h : outweighsName a L H = outweighsName a' L' H') :
    a = a' ∧ L = L' ∧ H = H' := by
  have hd := congrArg String.data h
  simp only [outweighsName, String.data_append, List.append_assoc] at hd
  have hd' := List.append_cancel_left hd
  simp only [List.cons_append, List.nil_append] at hd'
  obtain ⟨-, hpL⟩ := VE.Readings.validSoftName_data hL
  obtain ⟨-, hpL'⟩ := VE.Readings.validSoftName_data hL'
  obtain ⟨⟨c, l, hc, hc1, _⟩, hpH⟩ := VE.Readings.validSoftName_data hH
  obtain ⟨⟨c', l', hc', hc1', _⟩, hpH'⟩ := VE.Readings.validSoftName_data hH'
  have h0 : (H.data ++ '_' :: '_' :: a.data).head? ≠ some '_' := by
    rw [hc]; simp only [List.cons_append, List.head?_cons, ne_eq, Option.some.injEq]
    intro e; subst e; exact absurd hc1 (by decide)
  have h0' : (H'.data ++ '_' :: '_' :: a'.data).head? ≠ some '_' := by
    rw [hc']; simp only [List.cons_append, List.head?_cons, ne_eq, Option.some.injEq]
    intro e; subst e; exact absurd hc1' (by decide)
  obtain ⟨h1, h2⟩ := split_dunder_left _ _ _ _ hpL hpL' h0 h0' hd'
  obtain ⟨h3, h4⟩ := split_dunder_left _ _ _ _ hpH hpH' ha ha' h2
  exact ⟨String.ext h4, String.ext h1, String.ext h3⟩

theorem bindAll_not_inj : ∀ {s s' : List String} {x y : VE.Formula},
    bindAll s (.not x) = bindAll s' (.not y) → s = s' ∧ x = y
  | [], [], _, _, h => by simpa [bindAll] using h
  | [], _ :: _, _, _, h => by simp [bindAll] at h
  | _ :: _, [], _, _, h => by simp [bindAll] at h
  | _ :: s, _ :: s', _, _, h => by
    simp only [bindAll, List.foldr_cons, VE.Formula.all.injEq] at h
    obtain ⟨rfl, h⟩ := h
    obtain ⟨rfl, rfl⟩ := bindAll_not_inj (s := s) (s' := s') h
    exact ⟨rfl, rfl⟩

theorem atom_inj {n n' : String} {s : List String} (hs : Arity s) (h : atom n s = atom n' s) : n = n' := by
  match s, hs with
  | [_], _ => simpa [atom] using h
  | [_, _], _ => simpa [atom] using h

theorem regulated_of_sorts {D : SoftDoc} {a : String} (h : sortsOf D a ≠ []) : ∃ r ∈ D.T.regulated, r.name = a := by
  unfold sortsOf sortsIn at h
  cases hf : D.T.regulated.find? (·.name == a) with
  | none => rw [hf] at h; exact absurd rfl h
  | some r => exact ⟨r, List.mem_of_find?_eq_some hf, by simpa using List.find?_some hf⟩

/-- `Str_T` has a premise exactly for the `outweighs` decisions of strict pairs, queried at declared ranks and a
    declared predicate, when every regulated name begins with an ASCII letter (the decoder's identifier rule). -/
theorem strength_iff (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (a L H : String)
    (hL : L ∈ Wd.D.soft.ranks) (hH : H ∈ Wd.D.soft.ranks)
    (ha : ∃ ss, Wd.D.E.predicates a = some ss)
    (hr : ∀ r ∈ Wd.D.T.regulated, ∃ c cs, r.name.data = c :: cs ∧ c.isAlpha) :
    bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H)) ∈ strengthPremises Wd ↔
      (a, L, H) ∈ outweighsTriples Wd.D ∧ strictPair Wd H L = true := by
  refine ⟨fun hm => ?_, fun ⟨ht, hs⟩ => strength_mem Wd ht hs⟩
  have hw : WellFormedSoft Wd.D = true := ((Bool.and_eq_true _ _).mp h).1
  have hrk := VE.Readings.checkSoftEnv_names _ (VE.Readings.checkSoft_parts _ (VE.Readings.wellFormedSoft_check _ hw)).1
  simp only [strengthPremises, strengthEntries, List.mem_map, List.mem_filterMap] at hm
  obtain ⟨⟨l, φ, p⟩, ⟨⟨a', L', H'⟩, ht, hf⟩, hφ⟩ := hm
  split at hf
  · rename_i e i hfe
    simp only [Option.some.injEq, Prod.mk.injEq] at hf
    obtain ⟨-, rfl, -⟩ := hf
    have hs : strictPair Wd H' L' = true := by
      have hp := List.find?_some hfe
      simp only [Bool.and_eq_true] at hp
      have he := List.mem_map_of_mem (f := Prod.fst) (List.mem_of_find?_eq_some hfe)
      rw [List.zipIdx_map_fst] at he
      exact strictPair_edge.mpr ⟨e, he, hp⟩
    obtain ⟨hss, hat⟩ := bindAll_not_inj hφ
    have har := triple_arity Wd.D hw ht
    have hne : actSortsOf Wd.D a' ≠ [] := by rcases har with h1 | h1 <;> intro e <;> simp [e] at h1
    simp only [outweighsF] at hat
    rw [← hss] at hat
    have hn := atom_inj har hat
    have head : ∀ x, actSortsOf Wd.D x ≠ [] → x.data.head? ≠ some '_' := by
      intro x hx
      obtain ⟨r, hr', rfl⟩ := regulated_of_sorts hx
      obtain ⟨c, cs, hc, hca⟩ := hr r hr'
      rw [hc]; simp only [List.head?_cons, ne_eq, Option.some.injEq]
      intro e; subst e; exact absurd hca (by decide)
    obtain ⟨c, hc, ⟨e', he', -⟩⟩ := chain_of_strictPair h hs
    have hmem := chain_members_ranks Wd hw c hc.2.2.1 hc.2.2.2
    have hH' := hrk H' (List.mem_append_left _ (hmem H' (List.mem_of_mem_head? hc.1)))
    have hL' := hrk L' (List.mem_append_left _ (hmem L' (List.mem_of_getLast? hc.2.1)))
    obtain ⟨rfl, rfl, rfl⟩ := outweighsName_inj hL' (hrk L (List.mem_append_left _ hL)) hH'
      (hrk H (List.mem_append_left _ hH)) (head a' hne) (head a (hss ▸ hne)) hn
    exact ⟨ht, hs⟩
  · cases hf

/-- `B'` agrees with `B` on every predicate that is not a decision of `E′`. -/
def SameBase (Wd : WeighDoc) (B B' : VE.Structure.{u}) : Prop :=
  ∃ R : String → List B.Carrier → Prop, B' = { B with relation := R } ∧
    ∀ p vs, p ∉ decisionNames Wd.D → (R p vs ↔ B.relation p vs)

/-- The witness: each `outweighs` atom is the disjunction of its sufficient conditions, each switch is off,
    every other relation is `B`'s. -/
def freeWitness (Wd : WeighDoc) (B : VE.Structure.{u}) : String → List B.Carrier → Prop := fun p vs =>
  match (outweighsTriples Wd.D).find? (fun t => outweighsName t.1 t.2.1 t.2.2 == p) with
  | some (a, L, H) => ∃ c ∈ Wd.W.conditions, c.target = .outweighs a L H ∧ c.kind = .sufficient ∧
      c.condition.denote B (tupleVal vs)
  | none => if ((offDecisions Wd.D).map (·.1)).contains p then False else B.relation p vs

theorem atom_rel (S : VE.Structure.{u}) (p : String) (ss : List String) (vs : List S.Carrier)
    (hv : VE.TupleTyped S ss vs) (h : (atom p ss).denote S (tupleVal vs)) : S.relation p vs := by
  by_cases ha : Arity ss
  · exact (atom_denote S p ss ha vs hv).mp h
  · unfold Arity at ha
    match ss, h with
    | [], h => exact h.elim
    | [_], _ => simp at ha
    | [_, _], _ => simp at ha
    | _ :: _ :: _ :: _, h => exact h.elim

/-- The narrow base-freedom of synthesis edit 1: `Weigh_T` alone never constrains the base. It says nothing about
    `Weigh_T` together with soft's coherence (W-κ). -/
theorem weigh_alone_base_free (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (B : VE.Structure.{u}) :
    ∃ B' : VE.Structure.{u}, SameBase Wd B B' ∧ Sat B' (weighPremises Wd) := by
  have hw := wfSoft Wd h
  have hv := softValid_of_wellFormed _ hw
  have hnd := hv.decNodup
  simp only [decisionNames, decisions, List.map_append, List.nodup_append] at hnd
  obtain ⟨⟨-, -, -⟩, hnw, hdisj⟩ := hnd
  have hnw' : ((outweighsTriples Wd.D).map (fun t => outweighsName t.1 t.2.1 t.2.2)).Nodup := by
    simpa [outweighsDecisions, Function.comp_def] using hnw
  have hfind : ∀ t ∈ outweighsTriples Wd.D, (outweighsTriples Wd.D).find?
      (fun t' => outweighsName t'.1 t'.2.1 t'.2.2 == outweighsName t.1 t.2.1 t.2.2) = some t :=
    find_key (fun t : String × String × String => outweighsName t.1 t.2.1 t.2.2) _ hnw'
  let B' : VE.Structure.{u} := { B with relation := freeWitness Wd B }
  have same : ∀ p vs, p ∉ decisionNames Wd.D → (freeWitness Wd B p vs ↔ B.relation p vs) := by
    intro p vs hp
    unfold freeWitness
    split
    · rename_i a L H hf
      have := List.find?_some hf
      have hm := List.mem_of_find?_eq_some hf
      exact absurd (List.mem_map.mpr ⟨(outweighsName a L H, actSortsOf Wd.D a),
        VE.Readings.mem_decisions.mpr (.inr (.inr ⟨a, L, H, hm, rfl⟩)), by simpa using this⟩) hp
    · split
      · rename_i hc
        exfalso; apply hp
        obtain ⟨d, hd, rfl⟩ := List.mem_map.mp (List.contains_iff_mem.mp hc)
        exact List.mem_map.mpr ⟨d, List.mem_append_left _ (List.mem_append_right _ hd), rfl⟩
      · exact Iff.rfl
  -- a condition reads only base predicates
  have cond_iff : ∀ c ∈ Wd.W.conditions, ∀ vs : List B.Carrier,
      (c.condition.denote B' (tupleVal vs) ↔ c.condition.denote B (tupleVal vs)) := by
    intro c hc vs
    have hwf := (VE.check_iff_wellFormed _ _ _).mp (condFacts Wd h c hc).2.2.2.1
    exact denote_relation_congr (E := Wd.D.E) (ns := decisionNames Wd.D) (fun r hr => hv.decFresh r hr) B _
      same _ _ _ hwf
  -- every switch is off
  have off_false : ∀ n π, targetExists Wd (.off n π) = true → ∀ vs : List B'.Carrier,
      VE.TupleTyped B' (targetSorts Wd (.off n π)) vs → ¬ (targetF Wd (.off n π)).denote B' (tupleVal vs) := by
    intro n π hex vs typed
    simp only [targetExists] at hex
    simp only [targetF]
    split
    · rename_i N hN
      rw [hN] at hex
      simp only [targetSorts, ruleSorts, hN] at typed
      intro hat
      have hr : freeWitness Wd B (offName N π) vs := atom_rel B' _ _ vs typed hat
      have hoff : (offName N π, sortsOf Wd.D N.pred) ∈ offDecisions Wd.D := by
        simp only [offDecisions, List.mem_flatMap, List.mem_map]
        exact ⟨N, List.mem_of_find?_eq_some hN, π, by simpa using hex, rfl⟩
      unfold freeWitness at hr
      split at hr
      · rename_i a L H hf
        have hm := List.mem_of_find?_eq_some hf
        have he := List.find?_some hf
        simp only [beq_iff_eq] at he
        exact hdisj _ (List.mem_append_right _ (List.mem_map.mpr ⟨_, hoff, rfl⟩)) _
          (List.mem_map.mpr ⟨(outweighsName a L H, actSortsOf Wd.D a),
            List.mem_map.mpr ⟨(a, L, H), hm, rfl⟩, rfl⟩) he.symm
      · rw [if_pos (List.contains_iff_mem.mpr (List.mem_map.mpr ⟨_, hoff, rfl⟩))] at hr
        exact hr
    · exact id
  have at_triple : ∀ a L H, (a, L, H) ∈ outweighsTriples Wd.D → ∀ vs : List B.Carrier,
      freeWitness Wd B (outweighsName a L H) vs ↔ ∃ c ∈ Wd.W.conditions, c.target = .outweighs a L H ∧
        c.kind = .sufficient ∧ c.condition.denote B (tupleVal vs) := by
    intro a L H hm vs
    have hf := hfind (a, L, H) hm
    simp only at hf
    simp only [freeWitness, hf]
  refine ⟨B', ⟨freeWitness Wd B, rfl, same⟩, fun φ hφ => ?_⟩
  rcases mem_weighPremises Wd hφ with ⟨a, L, H, hm, hs, rfl⟩ | ⟨c, hc, rfl⟩ | ⟨g, hg, ψ, rfl, -⟩
  · refine (bindAll_denote_nil B' _ _).mpr fun vs typed hat => ?_
    obtain ⟨c, hc, hct, -, -⟩ := (at_triple a L H hm vs).mp (atom_rel B' _ _ vs typed hat)
    rw [(condFacts Wd h c hc).2.2.1 a L H hct] at hs; cases hs
  · obtain ⟨hex, hko, -, -, -, -⟩ := condFacts Wd h c hc
    cases hct : c.target with
    | off n π =>
      have hk := hko n π hct
      simp only [condPremise, hk, hct]
      refine (bindAll_denote_nil B' _ _).mpr fun vs typed hat => ?_
      exact absurd hat (off_false n π (hct ▸ hex) vs typed)
    | outweighs a L H =>
      have hm : (a, L, H) ∈ outweighsTriples Wd.D := by
        rw [hct] at hex; simpa [targetExists] using hex
      cases hk : c.kind with
      | sufficient =>
        simp only [condPremise, hk, hct]
        refine (bindAll_denote_nil B' _ _).mpr fun vs typed hcd => ?_
        exact (atom_denote B' _ _ (triple_arity Wd.D hw hm) vs typed).mpr
          ((at_triple a L H hm vs).mpr ⟨c, hc, hct, hk, (cond_iff c hc vs).mp hcd⟩)
      | necessary =>
        simp only [condPremise, hk, hct]
        refine (bindAll_denote_nil B' _ _).mpr fun vs typed hat => ?_
        obtain ⟨c', hc', hct', hk', hcd⟩ := (at_triple a L H hm vs).mp (atom_rel B' _ _ vs typed hat)
        exact (cond_iff c hc vs).mpr (propImplies_sound _ _
          (disagreeFacts Wd h c' c hc' hc hk' hk (hct.trans hct'.symm)) B _ hcd)
  · simp only [condPremise]
    refine (bindAll_denote_nil B' _ _).mpr fun vs typed hat => ?_
    exact absurd hat (off_false _ _ ((weighFacts Wd h).grants g hg).1 vs typed)

end VE.Weighing
