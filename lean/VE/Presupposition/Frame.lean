import VE.Semantics

/-! # One-hole frames (docs/spec/presupposition.md 4.2)

A `Frame` is a formula with one hole. `goal` projects a presupposition from the hole to the
root: negation and left sides pass it through, the right side of "and" and "if" gains the left
side as a hypothesis, the right side of "or" its negation, and every binder closes it
universally (Karttunen 1974, Heim 1983). `Reach` is the incremental local context of the hole
(Schlenker 2009), `goal_denote` its meaning. -/
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

/-- R-D1: "not" at the root, or the antecedent of a root "if": where in place has the models of conditioned. -/
def Frame.shallow (f : Frame) : Prop := f = .notF .hole ∨ ∃ r, f = .impL .hole r

def Frame.shallowB : Frame → Bool
  | .notF .hole => true
  | .impL .hole _ => true
  | _ => false

theorem Frame.shallowB_iff (f : Frame) : f.shallowB = true ↔ f.shallow := by
  unfold Frame.shallowB Frame.shallow
  split <;> simp_all

instance (f : Frame) : Decidable f.shallow := decidable_of_iff _ f.shallowB_iff

theorem goal_denote (f : Frame) (p : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    (f.goal p).denote S ρ ↔ ∀ τ, f.Reach S ρ τ → p.denote S τ := by
  induction f generalizing ρ with
  | hole => simp [Frame.goal, Frame.Reach]
  | notF f ih | andL f _ ih | orL f _ ih | impL f _ ih => exact ih ρ
  | andR l f ih | impR l f ih =>
    simp only [Frame.goal, Frame.Reach, VE.Formula.denote, ih]
    exact ⟨fun h τ ⟨hl, hr⟩ => h hl τ hr, fun h hl τ hr => h τ ⟨hl, hr⟩⟩
  | orR l f ih =>
    simp only [Frame.goal, Frame.Reach, VE.Formula.denote, ih]
    exact ⟨fun h τ ⟨hl, hr⟩ => h hl τ hr, fun h hl τ hr => h τ ⟨hl, hr⟩⟩
  | allF s f ih | exF s f ih =>
    simp only [Frame.goal, Frame.Reach, VE.Formula.denote, ih]
    exact ⟨fun h τ ⟨v, hv, hr⟩ => h v hv τ hr, fun h v hv τ hr => h τ ⟨v, hv, hr⟩⟩

theorem plug_congr (f : Frame) (a b : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : ∀ τ, f.Reach S ρ τ → (a.denote S τ ↔ b.denote S τ)) :
    (f.plug a).denote S ρ ↔ (f.plug b).denote S ρ := by
  induction f generalizing ρ with
  | hole => exact h ρ rfl
  | notF f ih => exact not_congr (ih ρ h)
  | andL f r ih => exact and_congr_left' (ih ρ h)
  | orL f r ih => exact or_congr_left (ih ρ h)
  | impL f r ih => exact imp_congr_left (ih ρ h)
  | andR l f ih => exact and_congr_right fun hl => ih ρ fun τ hr => h τ ⟨hl, hr⟩
  | impR l f ih => exact imp_congr_right fun hl => ih ρ fun τ hr => h τ ⟨hl, hr⟩
  | orR l f ih =>
    show l.denote S ρ ∨ _ ↔ l.denote S ρ ∨ _
    by_cases hl : l.denote S ρ
    · simp only [hl, true_or]
    · simp only [hl, false_or]
      exact ih ρ fun τ hr => h τ ⟨hl, hr⟩
  | allF s f ih =>
    exact forall_congr' fun v => imp_congr_right fun hv => ih (v :: ρ) fun τ hr => h τ ⟨v, hv, hr⟩
  | exF s f ih =>
    exact exists_congr fun v => and_congr_right fun hv => ih (v :: ρ) fun τ hr => h τ ⟨v, hv, hr⟩

theorem reach_typed (f : Frame) (S : VE.Structure.{u}) (Γ : List String) (ρ τ : VE.Valuation S)
    (hρ : VE.Valuation.Typed S Γ ρ) (h : f.Reach S ρ τ) : VE.Valuation.Typed S (f.binders ++ Γ) τ := by
  induction f generalizing Γ ρ with
  | hole => subst h; exact hρ
  | notF f ih | andL f _ ih | orL f _ ih | impL f _ ih => exact ih Γ ρ hρ h
  | andR l f ih | impR l f ih | orR l f ih => exact ih Γ ρ hρ h.2
  | allF s f ih | exF s f ih =>
    obtain ⟨v, hv, hr⟩ := h
    simpa [Frame.binders] using ih (s :: Γ) (v :: ρ) (VE.typed_cons hρ hv) hr

theorem plug_wellFormed (E : VE.Environment) (f : Frame) (a : VE.Formula) (Γ : List String)
    (h : (f.plug a).WellFormed E Γ) : a.WellFormed E (f.binders ++ Γ) := by
  induction f generalizing Γ with
  | hole => exact h
  | notF f ih => exact ih Γ h
  | andL f _ ih | orL f _ ih | impL f _ ih => exact ih Γ h.1
  | andR _ f ih | orR _ f ih | impR _ f ih => exact ih Γ h.2
  | allF s f ih | exF s f ih => simpa [Frame.binders] using ih (s :: Γ) h.2

theorem goal_wellFormed (E : VE.Environment) (f : Frame) (a p : VE.Formula) (Γ : List String)
    (hf : (f.plug a).WellFormed E Γ) (hp : p.WellFormed E (f.binders ++ Γ)) : (f.goal p).WellFormed E Γ := by
  induction f generalizing Γ with
  | hole => exact hp
  | notF f ih => exact ih Γ hf hp
  | andL f _ ih | orL f _ ih | impL f _ ih => exact ih Γ hf.1 hp
  | andR _ f ih | impR _ f ih => exact ⟨hf.1, ih Γ hf.2 hp⟩
  | orR _ f ih => exact ⟨hf.1, ih Γ hf.2 hp⟩
  | allF s f ih | exF s f ih => exact ⟨hf.1, ih (s :: Γ) hf.2 (by simpa [Frame.binders] using hp)⟩

theorem close_wellFormed (E : VE.Environment) (f : Frame) (a p : VE.Formula) (Γ : List String)
    (hf : (f.plug a).WellFormed E Γ) (hp : p.WellFormed E (f.binders ++ Γ)) : (f.close p).WellFormed E Γ := by
  induction f generalizing Γ with
  | hole => exact hp
  | notF f ih => exact ih Γ hf hp
  | andL f _ ih | orL f _ ih | impL f _ ih => exact ih Γ hf.1 hp
  | andR _ f ih | orR _ f ih | impR _ f ih => exact ih Γ hf.2 hp
  | allF s f ih | exF s f ih => exact ⟨hf.1, ih (s :: Γ) hf.2 (by simpa [Frame.binders] using hp)⟩

theorem locate_plug (a : VE.Formula) (path : List Nat) (f : Frame) (b : VE.Formula)
    (h : Frame.locate a path = some (f, b)) : f.plug b = a := by
  induction path generalizing a f with
  | nil =>
    cases a <;> simp only [Frame.locate, Option.some.injEq, Prod.mk.injEq] at h <;>
      obtain ⟨rfl, rfl⟩ := h <;> rfl
  | cons i p ih =>
    cases a <;> (try rcases i with _ | _ | i) <;> simp only [Frame.locate, reduceCtorEq] at h <;>
      (obtain ⟨⟨g, c⟩, hl, he⟩ := Option.map_eq_some_iff.mp h
       simp only [Prod.mk.injEq] at he
       obtain ⟨rfl, rfl⟩ := he
       simp only [Frame.plug, ih _ _ hl])

end VE.Presupposition
