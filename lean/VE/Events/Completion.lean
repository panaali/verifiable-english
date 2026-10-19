import VE.Events.Calendar

/-! The calendar completion's fragment (docs/spec/events-time-causation.md 1.7, 6.1, 6.2). A day
extension adds days with no facts except those of the predicates in `ng` (`before` and the unsaid
tables); `hits ng k a` says `a` is false whenever variable `k` is an added day, `vacuous ng k a` that
it is true then. `up` formulas stay true in every day extension and `down` formulas stay false
(`dayExtension_transfer`): a universal day quantifier needs a guarded body for `up`, an existential
one a body that hits its variable for `down`. Order atoms are never guards.

The completion adds one day for each civil day number a numbering leaves unused, with no facts
except their order (`completion_extension`, `completion_reading`, `completion_admissible`). -/
namespace VE.Events
open VE.Time (dateMax)
universe u v

def numOf {α : Type} (num : α → Nat) : α ⊕ Nat → Nat
  | .inl x => num x
  | .inr n => n
def oldTuple {α : Type} : List (α ⊕ Nat) → Option (List α)
  | [] => some []
  | .inl x :: zs => (oldTuple zs).map (x :: ·)
  | .inr _ :: _ => none
def addedDay {α : Type} (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat) (n : Nat) : Prop :=
  n ≤ dateMax ∧ ∀ x ∈ M.domains V.day, num x ≠ n
def isDayC {α : Type} (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat) : α ⊕ Nat → Prop
  | .inl x => x ∈ M.domains V.day
  | .inr n => addedDay V M num n

def completion {α : Type} (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat) : VE.Structure.{0} where
  Carrier := α ⊕ Nat
  domain := fun s z => match z with
    | .inl x => x ∈ M.domains s
    | .inr n => s = V.day ∧ addedDay V M num n
  constant := fun c => (M.constants c).map Sum.inl
  relation := fun p zs => match oldTuple zs with
    | some xs => xs ∈ M.relations p
    | none => p = V.before ∧ ∃ z w, zs = [z, w] ∧ isDayC V M num z ∧ isDayC V M num w ∧ numOf num z < numOf num w

def isConst : VE.Term → Bool
  | .const _ => true
  | .var _ => false

/-- The term is variable `k`: the proofs' form of `t == .var k` (`isVar_beq`). -/
def isVar (k : Nat) : VE.Term → Bool
  | .var i => i == k
  | .const _ => false

mutual
def hits (ng : List String) (k : Nat) : VE.Formula → Bool
  | .bottom => true
  | .unary p t => !ng.contains p && t == .var k
  | .binary p t w => !ng.contains p && (t == .var k || w == .var k)
  | .eq t w => (t == .var k && isConst w) || (w == .var k && isConst t)
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

/-- `isVar k t` is `t == .var k`, the test `hits` makes. -/
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
    simp only [hits, Bool.and_eq_true, Bool.not_eq_true', ← isVar_beq] at h
    rw [isVar_eq h.2] at hv; simp [VE.Term.denote, hk] at hv; subst hv
    exact outside p _ _ hr (by simp) hy h.1
  | binary p t w =>
    intro k σ y hk hy
    refine ⟨fun h ⟨v, v', hv, hv', hr⟩ => ?_, fun h => by simp [vacuous] at h⟩
    simp only [hits, Bool.and_eq_true, Bool.not_eq_true', Bool.or_eq_true, ← isVar_beq] at h
    rcases h.2 with ht | ht
    · rw [isVar_eq ht] at hv; simp [VE.Term.denote, hk] at hv; subst hv
      exact outside p _ _ hr (by simp) hy h.1
    · rw [isVar_eq ht] at hv'; simp [VE.Term.denote, hk] at hv'; subst hv'
      exact outside p _ _ hr (by simp) hy h.1
  | eq t w =>
    intro k σ y hk hy
    refine ⟨fun h ⟨v, hv, hv'⟩ => ?_, fun h => by simp [vacuous] at h⟩
    simp only [hits, Bool.and_eq_true, Bool.or_eq_true, ← isVar_beq] at h
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
namespace VE.Events
open VE.Time (dateMax)

/-! ## The completion -/

theorem oldTuple_map {α : Type} : ∀ xs : List α, oldTuple (xs.map Sum.inl : List (α ⊕ Nat)) = some xs
  | [] => rfl
  | x :: xs => by simp [oldTuple, oldTuple_map xs]

theorem oldTuple_eq {α : Type} : ∀ {zs : List (α ⊕ Nat)} {xs : List α}, oldTuple zs = some xs →
    zs = xs.map Sum.inl
  | [], xs, h => by simp [oldTuple] at h; subst h; rfl
  | .inl x :: zs, xs, h => by
    simp only [oldTuple, Option.map_eq_some_iff] at h
    obtain ⟨ys, hy, rfl⟩ := h
    simp [oldTuple_eq hy]
  | .inr _ :: _, _, h => by simp [oldTuple] at h

/-- The completion's `before` on two days, one of them added: their numbers' order. -/
theorem completion_before_new {α : Type} {V : EventsEnv} {M : VE.FiniteModel α} {num : α → Nat}
    {z w : α ⊕ Nat} (h : oldTuple [z, w] = none) :
    (completion V M num).relation V.before [z, w] ↔ isDayC V M num z ∧ isDayC V M num w ∧ numOf num z < numOf num w := by
  simp only [completion, h, true_and]
  constructor
  · rintro ⟨z', w', he, hz, hw, hl⟩
    simp only [List.cons.injEq, and_true] at he; obtain ⟨rfl, rfl⟩ := he
    exact ⟨hz, hw, hl⟩
  · exact fun ⟨hz, hw, hl⟩ => ⟨z, w, rfl, hz, hw, hl⟩

/-- The completion is a day extension in which only `before` has tuples with added days ... -/
theorem completion_extension {α : Type} [DecidableEq α] (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat)
    (hm : Embeds V M.asStructure num) :
    DayExtension V.day [V.before] M.asStructure (completion V M num) Sum.inl := by
  have _ := hm
  refine ⟨fun x y h => Sum.inl.inj h, fun s x => Iff.rfl, ?_, fun c => rfl, fun p xs => ?_, ?_⟩
  · intro s y hy hn
    cases y with
    | inl x => exact absurd rfl (hn x)
    | inr n => exact hy.1
  · simp only [completion, VE.FiniteModel.asStructure, oldTuple_map]
  · intro p ys hr ⟨y, hy, hn⟩
    cases h : oldTuple ys with
    | some xs =>
      rw [oldTuple_eq h] at hy
      obtain ⟨x, -, rfl⟩ := List.mem_map.1 hy
      exact absurd rfl (hn x)
    | none =>
      simp only [completion, h] at hr
      simp [hr.1]

/-- ... whose days are every civil day ... -/
theorem completion_reading {α : Type} [DecidableEq α] (V : EventsEnv) (M : VE.FiniteModel α) (num : α → Nat)
    (hm : Embeds V M.asStructure num) :
    CalendarReading V (completion V M num) (numOf num) := by
  obtain ⟨inj, le, ord, dates⟩ := hm
  refine ⟨⟨?_, ?_, ?_, ?_⟩, ?_⟩
  · intro z w hz hw he
    cases z with
    | inl x => cases w with
      | inl y => exact congrArg Sum.inl (inj x y hz hw he)
      | inr m => exact absurd he (hw.2.2 x hz)
    | inr n => cases w with
      | inl y => exact absurd he.symm (hz.2.2 y hw)
      | inr m => simp only [numOf] at he; rw [he]
  · intro z hz
    cases z with
    | inl x => exact le x hz
    | inr n => exact hz.2.1
  · intro z w hz hw
    have dz : isDayC V M num z := by cases z with
      | inl x => exact hz
      | inr n => exact hz.2
    have dw : isDayC V M num w := by cases w with
      | inl x => exact hw
      | inr n => exact hw.2
    cases z with
    | inl x => cases w with
      | inl y => exact ord x y hz hw
      | inr m => exact (completion_before_new rfl).trans ⟨fun h => h.2.2, fun h => ⟨dz, dw, h⟩⟩
    | inr n => exact (completion_before_new rfl).trans ⟨fun h => h.2.2, fun h => ⟨dz, dw, h⟩⟩
  · intro D hD
    obtain ⟨x, hx, dx, nx⟩ := dates D hD
    exact ⟨.inl x, by simp [completion, VE.FiniteModel.asStructure] at hx ⊢; exact hx, dx, nx⟩
  · intro n hn
    by_cases h : ∃ x ∈ M.domains V.day, num x = n
    · obtain ⟨x, hx, rfl⟩ := h
      exact ⟨.inl x, hx, rfl⟩
    · exact ⟨.inr n, ⟨rfl, hn, fun x hx he => h ⟨x, hx, he⟩⟩, rfl⟩

theorem completion_typed {α : Type} {V : EventsEnv} {M : VE.FiniteModel α} {num : α → Nat} :
    ∀ (ss : List String) (xs : List α), VE.TupleTyped M.asStructure ss xs →
      VE.TupleTyped (completion V M num) ss (xs.map Sum.inl)
  | [], [], _ => trivial
  | _ :: ss, _ :: xs, ⟨h, ht⟩ => ⟨h, completion_typed ss xs ht⟩
  | [], _ :: _, h => h.elim
  | _ :: _, [], h => h.elim

/-- ... and which is a structure of the situation's environment. -/
theorem completion_admissible {α : Type} [DecidableEq α] (E : VE.Environment) (V : EventsEnv)
    (hT : EventsTyped E V = true) (M : VE.FiniteModel α) (valid : M.Valid E) (num : α → Nat)
    (hm : Embeds V M.asStructure num) :
    (completion V M num).Admissible E := by
  have _ := hm
  have hb : E.predicates V.before = some [V.day, V.day] := by
    simp only [EventsTyped, sig2, Bool.and_eq_true, beq_iff_eq] at hT; exact hT.1.1.1.1.1.2
  refine ⟨fun c s hc => ?_, fun p zs hr => ?_⟩
  · obtain ⟨v, hv, dv⟩ := valid.1 c s hc
    exact ⟨.inl v, by simp [completion, VE.FiniteModel.asStructure] at hv ⊢; exact hv, dv⟩
  · cases h : oldTuple zs with
    | some xs =>
      have hr : xs ∈ M.relations p := by simpa only [completion, h] using hr
      obtain ⟨ss, hp, ht⟩ := valid.2 p xs hr
      exact ⟨ss, hp, oldTuple_eq h ▸ completion_typed ss xs ht⟩
    | none =>
      simp only [completion, h] at hr
      obtain ⟨rfl, z, w, rfl, hz, hw, -⟩ := hr
      have day : ∀ z, isDayC V M num z → (completion V M num).domain V.day z := fun z hz => by
        cases z with
        | inl x => exact hz
        | inr n => exact ⟨rfl, hz⟩
      exact ⟨[V.day, V.day], hb, day z hz, day w hw, trivial⟩


/-- The conventions are in the fragment both ways. -/
theorem conventions_exact (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true) (ng : List String)
    (hng : ∀ p ∈ rolePreds V ++ V.links.map (·.predicate), p ∉ ng) :
    ∀ a ∈ conventionPremises V, up V.day ng a = true ∧ down V.day ng a = true := by
  have _ := h
  have role : ∀ p ∈ rolePreds V, p ∉ ng := fun p hp => hng p (List.mem_append_left _ hp)
  have link : ∀ l ∈ V.links, l.predicate ∉ ng := fun l hl =>
    hng l.predicate (List.mem_append_right _ (List.mem_map_of_mem hl))
  have onR : ∀ e ∈ V.events, e.on ∈ rolePreds V := fun e he => by
    simp only [rolePreds, List.mem_append, List.mem_map]; exact .inl ⟨e, he, rfl⟩
  have beginsR : ∀ x ∈ V.states, x.begins ∈ rolePreds V := fun x hx => by
    simp only [rolePreds, List.mem_append, List.mem_flatMap]; exact .inr ⟨x, hx, by simp⟩
  have endsR : ∀ x ∈ V.states, x.ends ∈ rolePreds V := fun x hx => by
    simp only [rolePreds, List.mem_append, List.mem_flatMap]; exact .inr ⟨x, hx, by simp⟩
  intro a ha
  simp only [conventionPremises, conventionLabelled, List.map_append, List.map_map, List.mem_append,
    List.mem_map, Function.comp, List.map_flatMap, List.mem_flatMap, List.map_cons, List.map_nil,
    List.mem_cons, List.not_mem_nil, or_false] at ha
  rcases ha with ((⟨e, hm, rfl⟩ | ⟨x, hm, hx⟩) | ⟨l, hm, rfl⟩) | ⟨⟨n, c⟩, hm, rfl⟩
  · have := role _ (onR e hm)
    simp [oneRoleF, bin, up, down, hits, vacuous, ← isVar_beq, isVar, this]
  · have hb := role _ (beginsR x hm)
    have he := role _ (endsR x hm)
    rcases hx with rfl | rfl | rfl
    · simp [oneRoleF, bin, up, down, hits, vacuous, ← isVar_beq, isVar, hb]
    · simp [oneRoleF, bin, up, down, hits, vacuous, ← isVar_beq, isVar, he]
    · simp [notBeforeBeginF, bin, up, down, hits, vacuous, ← isVar_beq, isVar, hb, he]
  · have hl := link l hm
    unfold linkForwardF
    split
    · next st bd hst hbd =>
      have h1 : st ∉ ng := by
        rcases startRole_mem hst with ⟨e, he, -, rfl⟩ | ⟨x, hx, -, rfl⟩
        · exact role _ (onR e he)
        · exact role _ (beginsR x hx)
      have h2 : bd ∉ ng := by
        rcases boundRole_mem hbd with ⟨e, he, -, rfl⟩ | ⟨x, hx, -, rfl⟩
        · exact role _ (onR e he)
        · exact role _ (endsR x hx)
      simp [bin, up, down, hits, vacuous, ← isVar_beq, isVar, hl, h1, h2]
    · simp [up, down]
  · simp only [weakerPairs, List.mem_flatMap, List.mem_filter, List.mem_map] at hm
    obtain ⟨n', ⟨hn, -⟩, c', -, he'⟩ := hm
    simp only [Prod.mk.injEq] at he'; obtain ⟨rfl, rfl⟩ := he'
    have hl := link n' hn
    simp [linkWeakerF, bin, up, down, hits, vacuous, ← isVar_beq, isVar, hl]

end VE.Events
