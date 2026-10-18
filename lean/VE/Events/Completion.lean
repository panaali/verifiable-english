import VE.Events.Calendar

/-! The calendar completion's fragment (docs/spec/events-time-causation.md 1.7, 6.1, 6.2). A day
extension adds days with no facts except those of the predicates in `ng` (`before` and the unsaid
tables); `hits ng k a` says `a` is false whenever variable `k` is an added day, `vacuous ng k a` that
it is true then. `up` formulas stay true in every day extension and `down` formulas stay false
(`dayExtension_transfer`): a universal day quantifier needs a guarded body for `up`, an existential
one a body that hits its variable for `down`. Order atoms are never guards. -/
namespace VE.Events
universe u v

def isConst : VE.Term → Bool
  | .const _ => true
  | .var _ => false

/-- The term is variable `k` (the spec's `t == .var k`). -/
def isVar (k : Nat) : VE.Term → Bool
  | .var i => i == k
  | .const _ => false

mutual
def hits (ng : List String) (k : Nat) : VE.Formula → Bool
  | .bottom => true
  | .unary p t => !ng.contains p && isVar k t
  | .binary p t w => !ng.contains p && (isVar k t || isVar k w)
  | .eq t w => (isVar k t && isConst w) || (isVar k w && isConst t)
  | .not a => vacuous ng k a
  | .and a b => hits ng k a || hits ng k b
  | .or a b => hits ng k a && hits ng k b
  | .ex _ a => hits ng (k + 1) a
  | _ => false
def vacuous (ng : List String) (k : Nat) : VE.Formula → Bool
  | .top => true
  | .not a => hits ng k a
  | .and a b => vacuous ng k a && vacuous ng k b
  | .or a b => vacuous ng k a || vacuous ng k b
  | .implies a b => hits ng k a || vacuous ng k b
  | .all _ a => vacuous ng (k + 1) a
  | _ => false
end

end VE.Events
namespace VE.Events

mutual
def up (day : String) (ng : List String) : VE.Formula → Bool
  | .not a => down day ng a
  | .and a b => up day ng a && up day ng b
  | .or a b => up day ng a && up day ng b
  | .implies a b => down day ng a && up day ng b
  | .ex _ a => up day ng a
  | .all s a => up day ng a && (s != day || vacuous ng 0 a)
  | _ => true
def down (day : String) (ng : List String) : VE.Formula → Bool
  | .not a => up day ng a
  | .and a b => down day ng a && down day ng b
  | .or a b => down day ng a && down day ng b
  | .implies a b => up day ng a && down day ng b
  | .ex s a => down day ng a && (s != day || hits ng 0 a)
  | .all _ a => down day ng a
  | _ => true
end

end VE.Events
namespace VE.Events

/-- `S` extends `M` along `ι` by days only: `ι` is one-to-one and keeps domains, constants and
    relations; an element outside its image is a day; a true tuple with such an element is of a
    predicate in `ng`. -/
def DayExtension (day : String) (ng : List String) (M : VE.Structure.{u}) (S : VE.Structure.{v})
    (ι : M.Carrier → S.Carrier) : Prop :=
  (∀ x y, ι x = ι y → x = y) ∧
  (∀ s x, S.domain s (ι x) ↔ M.domain s x) ∧
  (∀ s y, S.domain s y → (∀ x, ι x ≠ y) → s = day) ∧
  (∀ c, S.constant c = (M.constant c).map ι) ∧
  (∀ p xs, S.relation p (xs.map ι) ↔ M.relation p xs) ∧
  (∀ p ys, S.relation p ys → (∃ y ∈ ys, ∀ x, ι x ≠ y) → p ∈ ng)

/-! ## Proofs -/

theorem isVar_eq {k : Nat} {t : VE.Term} (h : isVar k t = true) : t = .var k := by
  cases t <;> simp_all [isVar]

/-- `isVar k t` is the spec's `t == .var k`, so `hits` is the spec's function. -/
theorem isVar_beq (k : Nat) (t : VE.Term) : isVar k t = (t == .var k) := by
  cases t <;> rfl

theorem isConst_eq {t : VE.Term} (h : isConst t = true) : ∃ c, t = .const c := by
  cases t <;> simp_all [isConst]

/-- `hits` and `vacuous` are sound at an added day, at every valuation of the extension. -/
theorem hits_vacuous {day : String} {ng : List String} {M : VE.Structure.{u}} {S : VE.Structure.{v}}
    {ι : M.Carrier → S.Carrier} (hx : DayExtension day ng M S ι) (a : VE.Formula) :
    ∀ (k : Nat) (σ : List S.Carrier) (y : S.Carrier), σ[k]? = some y → (∀ x, ι x ≠ y) →
      (hits ng k a = true → ¬ a.denote S σ) ∧ (vacuous ng k a = true → a.denote S σ) := by
  obtain ⟨-, -, -, hc, -, hng⟩ := hx
  have outside : ∀ p ys y', S.relation p ys → y' ∈ ys → (∀ x, ι x ≠ y') → ng.contains p = false → False :=
    fun p ys _ hr hm hy hp => by simp [hng p ys hr ⟨_, hm, hy⟩] at hp
  induction a with
  | top => intro k σ y _ _; simp [hits, vacuous, VE.Formula.denote]
  | bottom => intro k σ y _ _; simp [hits, vacuous, VE.Formula.denote]
  | unary p t =>
    intro k σ y hk hy
    refine ⟨fun h ⟨v, hv, hr⟩ => ?_, fun h => by simp [vacuous] at h⟩
    simp only [hits, Bool.and_eq_true, Bool.not_eq_true'] at h
    rw [isVar_eq h.2] at hv; simp [VE.Term.denote, hk] at hv; subst hv
    exact outside p _ _ hr (by simp) hy h.1
  | binary p t w =>
    intro k σ y hk hy
    refine ⟨fun h ⟨v, v', hv, hv', hr⟩ => ?_, fun h => by simp [vacuous] at h⟩
    simp only [hits, Bool.and_eq_true, Bool.not_eq_true', Bool.or_eq_true] at h
    rcases h.2 with ht | ht
    · rw [isVar_eq ht] at hv; simp [VE.Term.denote, hk] at hv; subst hv
      exact outside p _ _ hr (by simp) hy h.1
    · rw [isVar_eq ht] at hv'; simp [VE.Term.denote, hk] at hv'; subst hv'
      exact outside p _ _ hr (by simp) hy h.1
  | eq t w =>
    intro k σ y hk hy
    refine ⟨fun h ⟨v, hv, hv'⟩ => ?_, fun h => by simp [vacuous] at h⟩
    simp only [hits, Bool.and_eq_true, Bool.or_eq_true] at h
    rcases h with ⟨ht, hw⟩ | ⟨hw, ht⟩
    · obtain ⟨c, rfl⟩ := isConst_eq hw
      rw [isVar_eq ht] at hv; simp [VE.Term.denote, hk] at hv; subst hv
      simp [VE.Term.denote, hc] at hv'; obtain ⟨x, -, hxy⟩ := hv'; exact hy x hxy
    · obtain ⟨c, rfl⟩ := isConst_eq ht
      rw [isVar_eq hw] at hv'; simp [VE.Term.denote, hk] at hv'; subst hv'
      simp [VE.Term.denote, hc] at hv; obtain ⟨x, -, hxy⟩ := hv; exact hy x hxy
  | not a ih =>
    intro k σ y hk hy
    simp only [hits, vacuous, VE.Formula.denote]
    exact ⟨fun h hn => hn ((ih k σ y hk hy).2 h), fun h => (ih k σ y hk hy).1 h⟩
  | and a b ia ib =>
    intro k σ y hk hy
    simp only [hits, vacuous, VE.Formula.denote, Bool.or_eq_true, Bool.and_eq_true]
    exact ⟨fun h ⟨ha, hb⟩ => h.elim (fun h => (ia k σ y hk hy).1 h ha) (fun h => (ib k σ y hk hy).1 h hb),
      fun h => ⟨(ia k σ y hk hy).2 h.1, (ib k σ y hk hy).2 h.2⟩⟩
  | or a b ia ib =>
    intro k σ y hk hy
    simp only [hits, vacuous, VE.Formula.denote, Bool.or_eq_true, Bool.and_eq_true]
    exact ⟨fun h hab => hab.elim ((ia k σ y hk hy).1 h.1) ((ib k σ y hk hy).1 h.2),
      fun h => h.elim (fun h => .inl ((ia k σ y hk hy).2 h)) (fun h => .inr ((ib k σ y hk hy).2 h))⟩
  | implies a b ia ib =>
    intro k σ y hk hy
    simp only [hits, vacuous, VE.Formula.denote, Bool.or_eq_true]
    refine ⟨fun h => by simp at h, fun h ha => ?_⟩
    exact h.elim (fun h => absurd ha ((ia k σ y hk hy).1 h)) (fun h => (ib k σ y hk hy).2 h)
  | all s a ih =>
    intro k σ y hk hy
    simp only [hits, vacuous, VE.Formula.denote]
    exact ⟨fun h => by simp at h, fun h v _ => (ih (k + 1) (v :: σ) y (by simpa using hk) hy).2 h⟩
  | ex s a ih =>
    intro k σ y hk hy
    simp only [hits, vacuous, VE.Formula.denote]
    exact ⟨fun h ⟨v, _, hv⟩ => (ih (k + 1) (v :: σ) y (by simpa using hk) hy).1 h hv, fun h => by simp at h⟩

theorem term_map {M : VE.Structure.{u}} {S : VE.Structure.{v}} {ι : M.Carrier → S.Carrier}
    (hc : ∀ c, S.constant c = (M.constant c).map ι) (t : VE.Term) (ρ : List M.Carrier) :
    t.denote S (ρ.map ι) = (t.denote M ρ).map ι := by
  cases t <;> simp [VE.Term.denote, hc]

/-- The transfer theorem: in a day extension, `up` formulas stay true and `down` formulas stay false,
    at every valuation of old elements. -/
theorem dayExtension_transfer (day : String) (ng : List String) (M : VE.Structure.{u}) (S : VE.Structure.{v})
    (ι : M.Carrier → S.Carrier) (hx : DayExtension day ng M S ι) (a : VE.Formula) (ρ : List M.Carrier) :
    (up day ng a = true → a.denote M ρ → a.denote S (ρ.map ι)) ∧
    (down day ng a = true → a.denote S (ρ.map ι) → a.denote M ρ) := by
  have hv := hits_vacuous hx
  obtain ⟨inj, dom, newDay, hc, hrel, -⟩ := hx
  have tm := term_map hc
  induction a generalizing ρ with
  | top => simp [VE.Formula.denote]
  | bottom => simp [VE.Formula.denote]
  | unary p t =>
    have e : (VE.Formula.unary p t).denote S (ρ.map ι) ↔ (VE.Formula.unary p t).denote M ρ := by
      simp only [VE.Formula.denote, tm]
      constructor
      · rintro ⟨_, h, hr⟩
        obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.1 h
        exact ⟨x, hx, (hrel p [x]).1 hr⟩
      · rintro ⟨x, hx, hr⟩
        exact ⟨ι x, by simp [hx], (hrel p [x]).2 hr⟩
    exact ⟨fun _ h => e.2 h, fun _ h => e.1 h⟩
  | binary p t w =>
    have e : (VE.Formula.binary p t w).denote S (ρ.map ι) ↔ (VE.Formula.binary p t w).denote M ρ := by
      simp only [VE.Formula.denote, tm]
      constructor
      · rintro ⟨_, _, h, h', hr⟩
        obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.1 h
        obtain ⟨x', hx', rfl⟩ := Option.map_eq_some_iff.1 h'
        exact ⟨x, x', hx, hx', (hrel p [x, x']).1 hr⟩
      · rintro ⟨x, x', hx, hx', hr⟩
        exact ⟨ι x, ι x', by simp [hx], by simp [hx'], (hrel p [x, x']).2 hr⟩
    exact ⟨fun _ h => e.2 h, fun _ h => e.1 h⟩
  | eq t w =>
    have e : (VE.Formula.eq t w).denote S (ρ.map ι) ↔ (VE.Formula.eq t w).denote M ρ := by
      simp only [VE.Formula.denote, tm]
      constructor
      · rintro ⟨_, h, h'⟩
        obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.1 h
        obtain ⟨x', hx', he⟩ := Option.map_eq_some_iff.1 h'
        exact ⟨x, hx, by rw [hx', inj _ _ he]⟩
      · rintro ⟨x, hx, hx'⟩
        exact ⟨ι x, by simp [hx], by simp [hx']⟩
    exact ⟨fun _ h => e.2 h, fun _ h => e.1 h⟩
  | not a ih =>
    simp only [up, down, VE.Formula.denote]
    exact ⟨fun h hm hs => hm ((ih ρ).2 h hs), fun h hs hm => hs ((ih ρ).1 h hm)⟩
  | and a b ia ib =>
    simp only [up, down, VE.Formula.denote, Bool.and_eq_true]
    exact ⟨fun h hm => ⟨(ia ρ).1 h.1 hm.1, (ib ρ).1 h.2 hm.2⟩,
      fun h hs => ⟨(ia ρ).2 h.1 hs.1, (ib ρ).2 h.2 hs.2⟩⟩
  | or a b ia ib =>
    simp only [up, down, VE.Formula.denote, Bool.and_eq_true]
    exact ⟨fun h hm => hm.imp ((ia ρ).1 h.1) ((ib ρ).1 h.2),
      fun h hs => hs.imp ((ia ρ).2 h.1) ((ib ρ).2 h.2)⟩
  | implies a b ia ib =>
    simp only [up, down, VE.Formula.denote, Bool.and_eq_true]
    exact ⟨fun h hm hs => (ib ρ).1 h.2 (hm ((ia ρ).2 h.1 hs)),
      fun h hs hm => (ib ρ).2 h.2 (hs ((ia ρ).1 h.1 hm))⟩
  | all s a ih =>
    simp only [up, down, VE.Formula.denote, Bool.and_eq_true, Bool.or_eq_true]
    refine ⟨fun h hm y hy => ?_, fun h hs x hx => (ih (x :: ρ)).2 h (hs (ι x) ((dom s x).2 hx))⟩
    by_cases himg : ∃ x, ι x = y
    · obtain ⟨x, rfl⟩ := himg
      exact (ih (x :: ρ)).1 h.1 (hm x ((dom s x).1 hy))
    · have hs : s = day := newDay s y hy (fun x hxy => himg ⟨x, hxy⟩)
      have hvac : vacuous ng 0 a = true := by simpa [hs] using h.2
      exact (hv a 0 (y :: ρ.map ι) y rfl (fun x hxy => himg ⟨x, hxy⟩)).2 hvac
  | ex s a ih =>
    simp only [up, down, VE.Formula.denote, Bool.and_eq_true, Bool.or_eq_true]
    refine ⟨fun h ⟨x, hx, hm⟩ => ⟨ι x, (dom s x).2 hx, (ih (x :: ρ)).1 h hm⟩, fun h ⟨y, hy, hs⟩ => ?_⟩
    by_cases himg : ∃ x, ι x = y
    · obtain ⟨x, rfl⟩ := himg
      exact ⟨x, (dom s x).1 hy, (ih (x :: ρ)).2 h.1 hs⟩
    · have hd : s = day := newDay s y hy (fun x hxy => himg ⟨x, hxy⟩)
      have hhit : hits ng 0 a = true := by simpa [hd] using h.2
      exact absurd hs ((hv a 0 (y :: ρ.map ι) y rfl (fun x hxy => himg ⟨x, hxy⟩)).1 hhit)

end VE.Events
