import VE.Presupposition.Frame
import VE.Norms.Prefix

/-! # Readings and root carriers (docs/spec/presupposition.md 4.3)

A `Reading` is what a trigger row gives at its hole: what it takes for granted (`pre`), the
assertive clause (`strong`) and the presuppositional clause (`weak`). Where the projected goal
holds, every root carrier says what the weak plug says (`collapse`, `carriers_on_goal`). A unit
with several obligations carries them by `carried`: the asserted goals as left conjuncts, then
the conditioned goals as antecedents, then the base content. -/
namespace VE.Presupposition
universe u

/-- What a trigger row gives at its hole, all three over the hole's context. -/
structure Reading where
  pre    : VE.Formula
  strong : VE.Formula
  weak   : VE.Formula
  deriving DecidableEq, Repr

def Reading.DefinedAt (r : Reading) (S : VE.Structure.{u}) (τ : VE.Valuation S) : Prop :=
  r.strong.denote S τ ↔ r.pre.denote S τ ∧ r.weak.denote S τ

theorem collapse (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hdef : ∀ τ, f.Reach S ρ τ → r.DefinedAt S τ) (hgoal : (f.goal r.pre).denote S ρ) :
    (f.plug r.strong).denote S ρ ↔ (f.plug r.weak).denote S ρ :=
  plug_congr f _ _ S ρ fun τ hr =>
    (hdef τ hr).trans (and_iff_right ((goal_denote f r.pre S ρ).mp hgoal τ hr))

theorem collapse_certified (E : VE.Environment) (prem : List VE.Formula) (f : Frame) (r : Reading)
    (c : VE.Tableau.Certificate) (acc : VE.Tableau.checkCertificate E prem (f.goal r.pre) c = true)
    (hdef : ∀ S : VE.Structure.{u}, S.Admissible E → ∀ τ, f.Reach S [] τ → r.DefinedAt S τ)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S prem) :
    (f.plug r.strong).denote S [] ↔ (f.plug r.weak).denote S [] :=
  collapse f r S [] (hdef S hS) (VE.Tableau.checkCertificate_sound.{u} E prem _ c acc S hS hprem)

theorem collapse_assumed (E : VE.Environment) (prem : List VE.Formula) (f : Frame) (r : Reading)
    (hdef : ∀ S : VE.Structure.{u}, S.Admissible E → ∀ τ, f.Reach S [] τ → r.DefinedAt S τ)
    (S : VE.Structure.{u}) (hS : S.Admissible E) (hprem : VE.Norms.Sat S (prem ++ [f.goal r.pre])) :
    (f.plug r.strong).denote S [] ↔ (f.plug r.weak).denote S [] :=
  collapse f r S [] (hdef S hS) (hprem _ (List.mem_append_right _ (List.mem_singleton_self _)))

/-- Root carriers: asserted is `goal ∧ clause`, conditioned is `goal → clause`, in place is the clause alone. -/
def assertedAt (f : Frame) (r : Reading) : VE.Formula := .and (f.goal r.pre) (f.plug r.strong)
def conditionedAt (f : Frame) (r : Reading) : VE.Formula := .implies (f.goal r.pre) (f.plug r.strong)
def inPlaceAt (f : Frame) (r : Reading) : VE.Formula := f.plug r.strong

theorem asserted_false_off_goal (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : ¬ (f.goal r.pre).denote S ρ) : ¬ (assertedAt f r).denote S ρ :=
  fun ha => h ha.1

theorem conditioned_vacuous_off_goal (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : ¬ (f.goal r.pre).denote S ρ) : (conditionedAt f r).denote S ρ :=
  fun hg => absurd hg h

theorem carriers_on_goal (f : Frame) (r : Reading) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hdef : ∀ τ, f.Reach S ρ τ → r.DefinedAt S τ) (hgoal : (f.goal r.pre).denote S ρ) :
    ((assertedAt f r).denote S ρ ↔ (f.plug r.weak).denote S ρ) ∧
    ((conditionedAt f r).denote S ρ ↔ (f.plug r.weak).denote S ρ) ∧
    ((inPlaceAt f r).denote S ρ ↔ (f.plug r.weak).denote S ρ) :=
  have hc := collapse f r S ρ hdef hgoal
  ⟨(and_iff_right hgoal).trans hc, (imp_iff_right hgoal).trans hc, hc⟩

/-- What one obligation adds at the root of its unit. -/
inductive Root where
  | bare | asserted | conditioned
  deriving DecidableEq, Repr

/-- The whole unit: the asserted goals as left conjuncts, then the conditioned goals as antecedents, then the base
    content, each group in block order. -/
def carried (ms : List (Root × VE.Formula)) (B : VE.Formula) : VE.Formula :=
  (ms.filter (fun m => m.1 == Root.asserted)).foldr (fun m a => .and m.2 a)
    ((ms.filter (fun m => m.1 == Root.conditioned)).foldr (fun m a => .implies m.2 a) B)

/-- The inverse shape: remove `k` left conjuncts, then `m` antecedents. -/
def peel : Nat → Nat → VE.Formula → Option VE.Formula
  | 0, 0, a => some a
  | 0, m + 1, .implies _ b => peel 0 m b
  | k + 1, m, .and _ b => peel k m b
  | _, _, _ => none

theorem foldr_and_denote (l : List (Root × VE.Formula)) (X : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) :
    (l.foldr (fun m a => .and m.2 a) X).denote S ρ ↔ (∀ m ∈ l, m.2.denote S ρ) ∧ X.denote S ρ := by
  induction l with
  | nil => simp
  | cons x l ih => simp only [List.foldr_cons, VE.Formula.denote, ih, List.forall_mem_cons, and_assoc]

theorem foldr_implies_denote (l : List (Root × VE.Formula)) (X : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) :
    (l.foldr (fun m a => .implies m.2 a) X).denote S ρ ↔ ((∀ m ∈ l, m.2.denote S ρ) → X.denote S ρ) := by
  induction l with
  | nil => simp
  | cons x l ih => simp only [List.foldr_cons, VE.Formula.denote, ih, List.forall_mem_cons, and_imp]

theorem carried_denote (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) :
    (carried ms B).denote S ρ ↔
      (∀ m ∈ ms, m.1 = Root.asserted → m.2.denote S ρ) ∧
      ((∀ m ∈ ms, m.1 = Root.conditioned → m.2.denote S ρ) → B.denote S ρ) := by
  simp only [carried, foldr_and_denote, foldr_implies_denote, List.mem_filter, beq_iff_eq, and_imp]

theorem carried_asserted (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (m : Root × VE.Formula) (hm : m ∈ ms) (ha : m.1 = Root.asserted)
    (h : (carried ms B).denote S ρ) : m.2.denote S ρ :=
  ((carried_denote ms B S ρ).mp h).1 m hm ha

theorem carried_conditioned_off (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (m : Root × VE.Formula) (hm : m ∈ ms) (hc : m.1 = Root.conditioned)
    (hoff : ¬ m.2.denote S ρ) :
    (carried ms B).denote S ρ ↔ ∀ m' ∈ ms, m'.1 = Root.asserted → m'.2.denote S ρ := by
  rw [carried_denote]
  exact ⟨fun h => h.1, fun h => ⟨h, fun hall => absurd (hall m hm hc) hoff⟩⟩

theorem carried_on_goals (ms : List (Root × VE.Formula)) (B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (h : ∀ m ∈ ms, m.1 ≠ Root.bare → m.2.denote S ρ) :
    (carried ms B).denote S ρ ↔ B.denote S ρ := by
  rw [carried_denote]
  exact ⟨fun h' => h'.2 fun m hm hc => h m hm (by rw [hc]; decide),
    fun hB => ⟨fun m hm ha => h m hm (by rw [ha]; decide), fun _ => hB⟩⟩

theorem peel_ands (l : List (Root × VE.Formula)) (m : Nat) (X : VE.Formula) :
    peel l.length m (l.foldr (fun m a => .and m.2 a) X) = peel 0 m X := by
  induction l with
  | nil => rfl
  | cons x l ih => simp only [List.length_cons, List.foldr_cons, peel, ih]

theorem peel_implies (l : List (Root × VE.Formula)) (B : VE.Formula) :
    peel 0 l.length (l.foldr (fun m a => .implies m.2 a) B) = some B := by
  induction l with
  | nil => simp only [List.length_nil, List.foldr_nil, peel]
  | cons x l ih => simp only [List.length_cons, List.foldr_cons, peel, ih]

theorem peel_carried (ms : List (Root × VE.Formula)) (B : VE.Formula) :
    peel (ms.filter (fun m => m.1 == Root.asserted)).length
      (ms.filter (fun m => m.1 == Root.conditioned)).length (carried ms B) = some B := by
  rw [carried, peel_ands, peel_implies]

/-- Congruence through `carried`: a conditioned goal whose failure already gives `B` changes nothing at the root. -/
theorem carried_idle (ms₁ ms₂ : List (Root × VE.Formula)) (g B : VE.Formula) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (h : ¬ g.denote S ρ → B.denote S ρ) :
    (carried (ms₁ ++ (Root.conditioned, g) :: ms₂) B).denote S ρ ↔
      (carried (ms₁ ++ (Root.bare, g) :: ms₂) B).denote S ρ := by
  simp only [carried_denote, List.mem_append, List.mem_cons, or_imp, forall_and, forall_eq, reduceCtorEq,
    false_implies, true_and, forall_const]
  refine and_congr_right fun _ => ⟨fun h1 ⟨h₁, h₂⟩ => ?_, fun h2 ⟨h₁, _, h₂⟩ => h2 ⟨h₁, h₂⟩⟩
  exact (Classical.em (g.denote S ρ)).elim (fun hg => h1 ⟨h₁, hg, h₂⟩) h

/-- R-D2: at a shallow frame, the whole unit with this obligation in place has the models of the whole unit with it
    conditioned, whatever the other obligations' root modes `ms₁`, `ms₂`. -/
theorem inPlace_iff_conditioned_shallow (f : Frame) (hf : f.shallow) (r : Reading)
    (ms₁ ms₂ : List (Root × VE.Formula)) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hpre : ∀ τ, f.Reach S ρ τ → r.strong.denote S τ → r.pre.denote S τ) :
    (carried (ms₁ ++ (Root.bare, f.goal r.pre) :: ms₂) (f.plug r.strong)).denote S ρ ↔
      (carried (ms₁ ++ (Root.conditioned, f.goal r.pre) :: ms₂) (f.plug r.strong)).denote S ρ := by
  refine (carried_idle ms₁ ms₂ _ _ S ρ ?_).symm
  rcases hf with rfl | ⟨q, rfl⟩
  · exact fun hg hs => hg (hpre ρ rfl hs)
  · exact fun hg hs => absurd (hpre ρ rfl hs) hg

end VE.Presupposition
