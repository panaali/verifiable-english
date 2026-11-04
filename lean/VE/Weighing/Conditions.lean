import VE.Weighing.Tree
import VE.NormDefaults.Packs
import VE.NormDefaults.Check
import VE.Acts.LexicalProofs
import VE.Discourse.Manifest
import VE.EnglishGrammar.Rules

/-!
# Weighing's premises and checks (docs/spec/weighing.md 1.4-1.6, 5)

`Weigh_T := Str_T ++ Dec_T ++ Grant_T`, each premise with its label and the request path of its entry; the one
premise generator `condPremise` (a grant premise is its necessary `.off` case); the propositional implication check;
`checkWeigh` (weighing.md 1.6, steps 3 to 7) and `WellFormedWeigh`. The theorems of weighing.md 5 follow.
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

end VE.Weighing
