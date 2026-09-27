import VE.Route.Examples

/-! Formula and structure helpers for W1 norms (docs/spec/norms.md section 6).

* `anyF`/`allF` are the left folds Python `ve/norms.py` writes (`_any` starts at
  `bottom`, `_all` at `top`), so generated premises are byte-identical.
* `bindAll` wraps binders in declared argument order (outermost first), and
  `tupleVal` turns a relation tuple (declared argument order) into the de
  Bruijn valuation of the body (`vs.reverse`, index 0 is the last argument).
* `hide`/`forget` present "the environment below" and "forget these symbols",
  as W3's `VE.Definitions` does; `inst` is capture-avoiding instantiation of the
  situation variables of an open formula by terms. -/
namespace VE.Norms
universe u

/-! ## Connectives in Python's shapes -/

def anyF (l : List VE.Formula) : VE.Formula := l.foldl .or .bottom
def allF (l : List VE.Formula) : VE.Formula := l.foldl .and .top
/-- `a ↔ b` as Python and W3 write it. -/
def iffF (a b : VE.Formula) : VE.Formula := .and (.implies a b) (.implies b a)
/-- Universal binders in declared argument order: `∀x₁:s₁. … ∀xₖ:sₖ. body`. -/
def bindAll (sorts : List String) (body : VE.Formula) : VE.Formula :=
  sorts.foldr (fun s a => .all s a) body

/-- The atom of a unary or binary symbol applied to its situation variables. -/
def atom (p : String) (sorts : List String) : VE.Formula :=
  match sorts with
  | [_] => .unary p (.var 0)
  | [_, _] => .binary p (.var 1) (.var 0)
  | _ => .bottom

/-- Relation tuples stay in declared argument order; formulas use de Bruijn
valuation order. -/
def tupleVal {α : Type u} (vs : List α) : List α := vs.reverse

theorem anyF_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) (l : List VE.Formula) :
    (anyF l).denote S ρ ↔ ∃ a ∈ l, a.denote S ρ := by
  suffices h : ∀ acc : VE.Formula, (l.foldl .or acc).denote S ρ ↔ acc.denote S ρ ∨ ∃ a ∈ l, a.denote S ρ by
    simp [anyF, h, VE.Formula.denote]
  induction l with
  | nil => intro acc; simp
  | cons b l ih =>
    intro acc
    simp only [List.foldl_cons, ih, VE.Formula.denote, List.mem_cons, exists_eq_or_imp]
    constructor
    · rintro ((h | h) | h)
      · exact Or.inl h
      · exact Or.inr (Or.inl h)
      · exact Or.inr (Or.inr h)
    · rintro (h | h | h)
      · exact Or.inl (Or.inl h)
      · exact Or.inl (Or.inr h)
      · exact Or.inr h

theorem allF_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) (l : List VE.Formula) :
    (allF l).denote S ρ ↔ ∀ a ∈ l, a.denote S ρ := by
  suffices h : ∀ acc : VE.Formula, (l.foldl .and acc).denote S ρ ↔ acc.denote S ρ ∧ ∀ a ∈ l, a.denote S ρ by
    simp [allF, h, VE.Formula.denote]
  induction l with
  | nil => intro acc; simp
  | cons b l ih =>
    intro acc
    simp only [List.foldl_cons, ih, VE.Formula.denote, List.mem_cons, forall_eq_or_imp]
    exact ⟨fun ⟨⟨h₁, h₂⟩, h₃⟩ => ⟨h₁, h₂, h₃⟩, fun ⟨h₁, h₂, h₃⟩ => ⟨⟨h₁, h₂⟩, h₃⟩⟩

theorem iffF_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) (a b : VE.Formula) :
    (iffF a b).denote S ρ ↔ (a.denote S ρ ↔ b.denote S ρ) := by
  simp only [iffF, VE.Formula.denote]
  exact ⟨fun h => ⟨h.1, h.2⟩, fun h => ⟨h.1, h.2⟩⟩

theorem bindAll_denote (S : VE.Structure.{u}) (sorts : List String) (body : VE.Formula)
    (ρ : VE.Valuation S) :
    (bindAll sorts body).denote S ρ ↔
      ∀ vs, VE.TupleTyped S sorts vs → body.denote S (vs.reverse ++ ρ) := by
  induction sorts generalizing ρ with
  | nil =>
    simp only [bindAll, List.foldr]
    constructor
    · intro h vs hvs
      match vs, hvs with
      | [], _ => simpa using h
    · intro h
      simpa using h [] trivial
  | cons s ss ih =>
    simp only [bindAll, List.foldr, VE.Formula.denote] at ih ⊢
    constructor
    · intro h vs hvs
      match vs, hvs with
      | v :: vs, ⟨hv, hvs⟩ => simpa using (ih (v :: ρ)).mp (h v hv) vs hvs
    · intro h v hv
      exact (ih (v :: ρ)).mpr fun vs hvs => by simpa using h (v :: vs) ⟨hv, hvs⟩

/-- The closed binder form at the empty valuation reads the body at `tupleVal`. -/
theorem bindAll_denote_nil (S : VE.Structure.{u}) (sorts : List String) (body : VE.Formula) :
    (bindAll sorts body).denote S [] ↔
      ∀ vs, VE.TupleTyped S sorts vs → body.denote S (tupleVal vs) := by
  simpa [tupleVal] using bindAll_denote S sorts body []

theorem tupleTyped_length {S : VE.Structure.{u}} :
    ∀ {ss : List String} {vs : List S.Carrier}, VE.TupleTyped S ss vs → vs.length = ss.length
  | [], [], _ => rfl
  | _ :: _, _ :: _, h => by simp [tupleTyped_length h.2]
  | [], _ :: _, h => h.elim
  | _ :: _, [], h => h.elim

/-- An arity is one of the two v0 atom shapes. -/
def Arity (sorts : List String) : Prop := sorts.length = 1 ∨ sorts.length = 2

theorem atom_denote (S : VE.Structure.{u}) (p : String) (sorts : List String) (ha : Arity sorts)
    (vs : List S.Carrier) (hv : VE.TupleTyped S sorts vs) :
    (atom p sorts).denote S (tupleVal vs) ↔ S.relation p vs := by
  unfold Arity at ha
  have hl := tupleTyped_length hv
  match sorts, vs, ha, hl with
  | [_], [v], _, _ => simp [atom, tupleVal, VE.Formula.denote, VE.Term.denote]
  | [_, _], [v, w], _, _ => simp [atom, tupleVal, VE.Formula.denote, VE.Term.denote]

/-- `tupleVal_typed`: a typed relation tuple gives a typed valuation of the
reversed context. -/
theorem tupleVal_typed (S : VE.Structure.{u}) (ss : List String) (vs : List S.Carrier)
    (h : VE.TupleTyped S ss vs) : VE.Valuation.Typed S ss.reverse (tupleVal vs) := by
  induction ss generalizing vs with
  | nil => match vs, h with | [], _ => exact VE.typed_empty S
  | cons s ss ih =>
    match vs, h with
    | v :: vs, ⟨hv, hvs⟩ =>
      intro i r hi
      simp only [tupleVal, List.reverse_cons] at hi ⊢
      have hl : vs.reverse.length = ss.reverse.length := by
        simp [tupleTyped_length hvs]
      by_cases hlt : i < ss.reverse.length
      · rw [List.getElem?_append_left hlt] at hi
        rw [List.getElem?_append_left (hl ▸ hlt)]
        exact ih vs hvs i r hi
      · have hge : ss.reverse.length ≤ i := Nat.le_of_not_lt hlt
        rw [List.getElem?_append_right hge] at hi
        rw [List.getElem?_append_right (hl ▸ hge), hl]
        cases hk : i - ss.reverse.length with
        | zero => rw [hk] at hi; simp at hi; subst hi; exact ⟨v, by simp, hv⟩
        | succ k => rw [hk] at hi; simp at hi

/-- The converse of `tupleVal_typed` for tuples of the right length. -/
theorem tupleTyped_of_tupleVal (S : VE.Structure.{u}) (ss : List String) (vs : List S.Carrier)
    (hl : vs.length = ss.length) (h : VE.Valuation.Typed S ss.reverse (tupleVal vs)) :
    VE.TupleTyped S ss vs := by
  induction ss generalizing vs with
  | nil => match vs, hl with | [], _ => trivial
  | cons s ss ih =>
    match vs, hl with
    | v :: vs, hl =>
      simp only [List.length_cons, Nat.add_right_cancel_iff] at hl
      have hl' : vs.reverse.length = ss.reverse.length := by simp [hl]
      refine ⟨?_, ih vs hl fun i r hi => ?_⟩
      · obtain ⟨w, hw, hd⟩ := h ss.reverse.length s (by simp)
        simp only [tupleVal, List.reverse_cons] at hw
        rw [List.getElem?_append_right (by simp [hl']), hl'] at hw
        simp at hw; subst hw; exact hd
      · have hlt : i < ss.reverse.length := by
          have := List.getElem?_eq_some_iff.mp hi; exact this.1
        obtain ⟨w, hw, hd⟩ := h i r (by simp only [List.reverse_cons]; rw [List.getElem?_append_left hlt]; exact hi)
        simp only [tupleVal, List.reverse_cons] at hw
        rw [List.getElem?_append_left (hl' ▸ hlt)] at hw
        exact ⟨w, hw, hd⟩

/-! ## Environments below and forgetting symbols -/

/-- The environment below the symbols `ns`: they are undeclared. -/
def hide (E : VE.Environment) (ns : List String) : VE.Environment :=
  { E with predicates := fun r => if r ∈ ns then none else E.predicates r }

/-- Forget the relations of the symbols `ns`; carrier, domains and constants stay. -/
def forget (ns : List String) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun r vs => r ∉ ns ∧ S.relation r vs }

theorem forget_forget (ns ms : List String) (S : VE.Structure.{u}) :
    forget ns (forget ms S) = forget (ns ++ ms) S := by
  cases S
  simp only [forget, VE.Structure.mk.injEq, heq_eq_eq, true_and]
  funext r vs
  simp [and_assoc]

theorem forget_nil (S : VE.Structure.{u}) : forget [] S = S := by
  cases S
  simp [forget]

theorem forget_congr {ns ms : List String} (h : ∀ r, r ∈ ns ↔ r ∈ ms) (S : VE.Structure.{u}) :
    forget ns S = forget ms S := by
  cases S
  simp only [forget, VE.Structure.mk.injEq, heq_eq_eq, true_and]
  funext r vs
  simp [h]

/-- Forgetting symbols that no true tuple uses does nothing. -/
theorem forget_eq_self {ns : List String} (S : VE.Structure.{u})
    (h : ∀ r vs, S.relation r vs → r ∉ ns) : forget ns S = S := by
  cases S with
  | mk C d c rel =>
    simp only [forget, VE.Structure.mk.injEq, heq_eq_eq, true_and]
    funext r vs
    apply propext
    exact ⟨fun h' => h'.2, fun h' => ⟨h r vs h', h'⟩⟩

theorem tupleTyped_relation (S : VE.Structure.{u}) (R : String → List S.Carrier → Prop)
    (ss : List String) (vs : List S.Carrier) :
    VE.TupleTyped { S with relation := R } ss vs ↔ VE.TupleTyped S ss vs :=
  VE.Route.Examples.tupleTyped_relation S R ss vs

theorem tupleTyped_forget (ns : List String) (S : VE.Structure.{u}) (ss : List String)
    (vs : List S.Carrier) : VE.TupleTyped (forget ns S) ss vs ↔ VE.TupleTyped S ss vs :=
  tupleTyped_relation S _ ss vs

theorem typed_forget (ns : List String) (S : VE.Structure.{u}) (Γ : List String)
    (ρ : VE.Valuation S) : VE.Valuation.Typed (forget ns S) Γ ρ ↔ VE.Valuation.Typed S Γ ρ :=
  Iff.rfl

theorem sortOf_hide (E : VE.Environment) (ns : List String) (Γ : List String) (t : VE.Term) :
    t.sortOf (hide E ns) Γ = t.sortOf E Γ := by
  cases t <;> rfl

theorem sortOf_congr {E E' : VE.Environment} (hc : E'.constants = E.constants) (Γ : List String)
    (t : VE.Term) : t.sortOf E' Γ = t.sortOf E Γ := by
  cases t <;> simp [VE.Term.sortOf, hc]

/-- Well-formedness is monotone in the declared predicates. -/
theorem wf_mono {E E' : VE.Environment} (hs : E'.sorts = E.sorts) (hc : E'.constants = E.constants)
    (hp : ∀ r ss, E.predicates r = some ss → E'.predicates r = some ss) :
    ∀ (a : VE.Formula) (Γ : List String), a.WellFormed E Γ → a.WellFormed E' Γ := by
  intro a
  induction a with
  | top | bottom => intro _ h; exact h
  | unary r t =>
    intro Γ ⟨s, hr, ht⟩
    exact ⟨s, hp _ _ hr, by rw [sortOf_congr hc]; exact ht⟩
  | binary r t w =>
    intro Γ ⟨s, s', hr, ht, hw⟩
    exact ⟨s, s', hp _ _ hr, by rw [sortOf_congr hc]; exact ht, by rw [sortOf_congr hc]; exact hw⟩
  | eq t w =>
    intro Γ ⟨s, ht, hw⟩
    exact ⟨s, by rw [sortOf_congr hc]; exact ht, by rw [sortOf_congr hc]; exact hw⟩
  | not a ih => intro Γ h; exact ih Γ h
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro Γ h; exact ⟨ia Γ h.1, ib Γ h.2⟩
  | all s a ih | ex s a ih =>
    intro Γ h; exact ⟨hs ▸ h.1, ih _ h.2⟩

theorem wf_hide_mono (E : VE.Environment) {ns ms : List String} (hsub : ∀ r, r ∈ ms → r ∈ ns)
    (a : VE.Formula) (Γ : List String) (h : a.WellFormed (hide E ns) Γ) :
    a.WellFormed (hide E ms) Γ := by
  refine wf_mono (E := hide E ns) (E' := hide E ms) rfl rfl ?_ a Γ h
  intro r ss hr
  simp only [hide] at hr ⊢
  by_cases hn : r ∈ ns
  · simp [hn] at hr
  · have : r ∉ ms := fun hm => hn (hsub r hm)
    simp only [this, if_false]
    simpa [hn] using hr

/-- Truth of a formula over `E` ignores the relations of undeclared symbols. -/
theorem denote_forget {E : VE.Environment} {ns : List String}
    (hn : ∀ r ∈ ns, E.predicates r = none) (S : VE.Structure.{u})
    (a : VE.Formula) (Γ : List String) (ρ : VE.Valuation S) (hw : a.WellFormed E Γ) :
    a.denote (forget ns S) ρ ↔ a.denote S ρ := by
  induction a generalizing Γ ρ with
  | unary r t =>
    obtain ⟨_, hr, _⟩ := hw
    have : r ∉ ns := fun h => by rw [hn r h] at hr; cases hr
    simp [VE.Formula.denote, forget, this, VE.Term.denote]
  | binary r t w =>
    obtain ⟨_, _, hr, _⟩ := hw
    have : r ∉ ns := fun h => by rw [hn r h] at hr; cases hr
    simp [VE.Formula.denote, forget, this, VE.Term.denote]
  | eq t w => simp [VE.Formula.denote, forget, VE.Term.denote]
  | top | bottom => simp [VE.Formula.denote]
  | not a ih => simp only [VE.Formula.denote]; rw [ih Γ ρ hw]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    simp only [VE.Formula.denote]; rw [ia Γ ρ hw.1, ib Γ ρ hw.2]
  | all t a ih | ex t a ih =>
    simp only [VE.Formula.denote]
    constructor
    · intro h
      first
      | exact fun v hv => (ih (t :: Γ) (v :: ρ) hw.2).mp (h v hv)
      | exact let ⟨v, hv, ha⟩ := h; ⟨v, hv, (ih (t :: Γ) (v :: ρ) hw.2).mp ha⟩
    · intro h
      first
      | exact fun v hv => (ih (t :: Γ) (v :: ρ) hw.2).mpr (h v hv)
      | exact let ⟨v, hv, ha⟩ := h; ⟨v, hv, (ih (t :: Γ) (v :: ρ) hw.2).mpr ha⟩

theorem denote_forget_hide {E : VE.Environment} {ns ms : List String} (hsub : ∀ r ∈ ms, r ∈ ns)
    (S : VE.Structure.{u}) (a : VE.Formula) (Γ : List String) (ρ : VE.Valuation S)
    (hw : a.WellFormed (hide E ns) Γ) :
    a.denote (forget ms S) ρ ↔ a.denote S ρ :=
  denote_forget (fun r hr => by simp [hide, hsub r hr]) S a Γ ρ hw

/-- Relations outside `ns` are unchanged by forgetting `ns`. -/
theorem forget_relation {ns : List String} (S : VE.Structure.{u}) {r : String} (hr : r ∉ ns)
    (vs : List S.Carrier) : (forget ns S).relation r vs ↔ S.relation r vs := by
  simp [forget, hr]

/-- A structure admissible for `E` is, after forgetting `ns`, admissible for `hide E ns`. -/
theorem forget_admissible (E : VE.Environment) (ns : List String) (S : VE.Structure.{u})
    (h : S.Admissible E) : (forget ns S).Admissible (hide E ns) := by
  refine ⟨fun c s hc => h.1 c s hc, fun r vs hr => ?_⟩
  obtain ⟨hne, hr⟩ := hr
  obtain ⟨ss, hss, ht⟩ := h.2 r vs hr
  exact ⟨ss, by simp [hide, hne, hss], (tupleTyped_forget ns S ss vs).mpr ht⟩

/-! ## Instantiating situation variables by terms -/

def Term.shift : VE.Term → VE.Term
  | .var i => .var (i + 1)
  | .const c => .const c

def Term.inst (σ : List VE.Term) : VE.Term → VE.Term
  | .var i => σ[i]?.getD (.var i)
  | .const c => .const c

/-- Replace variable `i` by `σ[i]`, lifting under binders (Python `_instantiate`). -/
def inst : List VE.Term → VE.Formula → VE.Formula
  | _, .top => .top
  | _, .bottom => .bottom
  | σ, .unary p t => .unary p (Term.inst σ t)
  | σ, .binary p t u => .binary p (Term.inst σ t) (Term.inst σ u)
  | σ, .eq t u => .eq (Term.inst σ t) (Term.inst σ u)
  | σ, .not a => .not (inst σ a)
  | σ, .and a b => .and (inst σ a) (inst σ b)
  | σ, .or a b => .or (inst σ a) (inst σ b)
  | σ, .implies a b => .implies (inst σ a) (inst σ b)
  | σ, .all s a => .all s (inst (.var 0 :: σ.map Term.shift) a)
  | σ, .ex s a => .ex s (inst (.var 0 :: σ.map Term.shift) a)

theorem shift_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) (v : S.Carrier) (t : VE.Term) :
    (Term.shift t).denote S (v :: ρ) = t.denote S ρ := by
  cases t <;> rfl

/-- Pointwise: `σ[i]` denotes `vs[i]` under `ρ`. -/
def Denotes (S : VE.Structure.{u}) (ρ : VE.Valuation S) (σ : List VE.Term) (vs : List S.Carrier) :
    Prop :=
  σ.length = vs.length ∧ ∀ i (h₁ : i < σ.length) (h₂ : i < vs.length),
    σ[i].denote S ρ = some vs[i]

theorem denotes_cons {S : VE.Structure.{u}} {ρ : VE.Valuation S} {σ : List VE.Term}
    {vs : List S.Carrier} (h : Denotes S ρ σ vs) (v : S.Carrier) :
    Denotes S (v :: ρ) (.var 0 :: σ.map Term.shift) (v :: vs) := by
  refine ⟨by simp [h.1], fun i h₁ h₂ => ?_⟩
  cases i with
  | zero => rfl
  | succ i =>
    simp only [List.getElem_cons_succ, List.getElem_map]
    rw [shift_denote]
    exact h.2 i (by simpa using h₁) (by simpa using h₂)

theorem term_inst_denote {S : VE.Structure.{u}} {ρ : VE.Valuation S} {σ : List VE.Term}
    {vs : List S.Carrier} (h : Denotes S ρ σ vs) (E : VE.Environment) (Γ : List String)
    (hl : Γ.length = vs.length) (t : VE.Term) (s : String) (ht : t.sortOf E Γ = some s) :
    (Term.inst σ t).denote S ρ = t.denote S vs := by
  cases t with
  | const c => rfl
  | var i =>
    have hi : i < Γ.length := (List.getElem?_eq_some_iff.mp ht).1
    have hv : i < vs.length := hl ▸ hi
    have hs : i < σ.length := h.1 ▸ hv
    simp only [Term.inst, VE.Term.denote, List.getElem?_eq_getElem hs, Option.getD_some,
      List.getElem?_eq_getElem hv]
    exact h.2 i hs hv

/-- Instantiation meets its specification on formulas typed in a context of the
tuple's length. -/
theorem inst_denote (S : VE.Structure.{u}) (E : VE.Environment) (a : VE.Formula) :
    ∀ (Γ : List String) (σ : List VE.Term) (ρ : VE.Valuation S) (vs : List S.Carrier),
      a.WellFormed E Γ → Γ.length = vs.length → Denotes S ρ σ vs →
      ((inst σ a).denote S ρ ↔ a.denote S vs) := by
  induction a with
  | top | bottom => intros; simp [inst, VE.Formula.denote]
  | unary p t =>
    intro Γ σ ρ vs ⟨s, _, ht⟩ hl h
    simp only [inst, VE.Formula.denote, term_inst_denote h E Γ hl t s ht]
  | binary p t w =>
    intro Γ σ ρ vs ⟨s, s', _, ht, hw⟩ hl h
    simp only [inst, VE.Formula.denote, term_inst_denote h E Γ hl t s ht,
      term_inst_denote h E Γ hl w s' hw]
  | eq t w =>
    intro Γ σ ρ vs ⟨s, ht, hw⟩ hl h
    simp only [inst, VE.Formula.denote, term_inst_denote h E Γ hl t s ht,
      term_inst_denote h E Γ hl w s hw]
  | not a ih =>
    intro Γ σ ρ vs hw hl h
    simp only [inst, VE.Formula.denote]; rw [ih Γ σ ρ vs hw hl h]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro Γ σ ρ vs hw hl h
    simp only [inst, VE.Formula.denote]; rw [ia Γ σ ρ vs hw.1 hl h, ib Γ σ ρ vs hw.2 hl h]
  | all s a ih | ex s a ih =>
    intro Γ σ ρ vs hw hl h
    simp only [inst, VE.Formula.denote]
    have key : ∀ v, (inst (.var 0 :: σ.map Term.shift) a).denote S (v :: ρ) ↔
        a.denote S (v :: vs) := fun v =>
      ih (s :: Γ) _ (v :: ρ) (v :: vs) hw.2 (by simp [hl]) (denotes_cons h v)
    first
    | exact forall_congr' fun v => imp_congr_right fun _ => key v
    | exact exists_congr fun v => and_congr_right fun _ => key v

theorem term_inst_sortOf (E : VE.Environment) (Γ Γ' : List String) (σ : List VE.Term)
    (hl : σ.length = Γ'.length)
    (hσ : ∀ i (h₁ : i < σ.length) (h₂ : i < Γ'.length), σ[i].sortOf E Γ = some Γ'[i])
    (E' : VE.Environment) (hc : E'.constants = E.constants) (t : VE.Term) (s : String)
    (ht : t.sortOf E' Γ' = some s) : (Term.inst σ t).sortOf E Γ = some s := by
  cases t with
  | const c => simpa [Term.inst, VE.Term.sortOf, hc] using ht
  | var i =>
    obtain ⟨hi, hs⟩ := List.getElem?_eq_some_iff.mp ht
    have h₁ : i < σ.length := hl ▸ hi
    simp only [Term.inst, List.getElem?_eq_getElem h₁, Option.getD_some]
    rw [hσ i h₁ hi, hs]

/-- Typing of an instantiation: a formula typed over `E'` in `Γ'` becomes one
typed over `E` in `Γ` when every `σ[i]` has sort `Γ'[i]` and `E'` declares no
more than `E`. -/
theorem inst_wellFormed (E E' : VE.Environment) (hs : E'.sorts = E.sorts)
    (hc : E'.constants = E.constants)
    (hp : ∀ r ss, E'.predicates r = some ss → E.predicates r = some ss) (a : VE.Formula) :
    ∀ (Γ Γ' : List String) (σ : List VE.Term), σ.length = Γ'.length →
      (∀ i (h₁ : i < σ.length) (h₂ : i < Γ'.length), σ[i].sortOf E Γ = some Γ'[i]) →
      a.WellFormed E' Γ' → (inst σ a).WellFormed E Γ := by
  induction a with
  | top | bottom => intros; trivial
  | unary r t =>
    intro Γ Γ' σ hl hσ ⟨s, hr, ht⟩
    exact ⟨s, hp _ _ hr, term_inst_sortOf E Γ Γ' σ hl hσ E' hc t s ht⟩
  | binary r t w =>
    intro Γ Γ' σ hl hσ ⟨s, s', hr, ht, hw⟩
    exact ⟨s, s', hp _ _ hr, term_inst_sortOf E Γ Γ' σ hl hσ E' hc t s ht,
      term_inst_sortOf E Γ Γ' σ hl hσ E' hc w s' hw⟩
  | eq t w =>
    intro Γ Γ' σ hl hσ ⟨s, ht, hw⟩
    exact ⟨s, term_inst_sortOf E Γ Γ' σ hl hσ E' hc t s ht,
      term_inst_sortOf E Γ Γ' σ hl hσ E' hc w s hw⟩
  | not a ih => intro Γ Γ' σ hl hσ h; exact ih Γ Γ' σ hl hσ h
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro Γ Γ' σ hl hσ h; exact ⟨ia Γ Γ' σ hl hσ h.1, ib Γ Γ' σ hl hσ h.2⟩
  | all s a ih | ex s a ih =>
    intro Γ Γ' σ hl hσ h
    refine ⟨hs ▸ h.1, ih (s :: Γ) (s :: Γ') _ (by simp [hl]) ?_ h.2⟩
    intro i h₁ h₂
    cases i with
    | zero => rfl
    | succ i =>
      have h1' : i < σ.length := by simpa using h₁
      have h2' : i < Γ'.length := by simpa using h₂
      simp only [List.getElem_cons_succ, List.getElem_map]
      have := hσ i h1' h2'
      generalize σ[i] = t at this ⊢
      cases t <;> simpa [Term.shift, VE.Term.sortOf] using this

end VE.Norms
