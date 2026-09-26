import VE.Route.Examples

/-! The definitions layer of PLAN-EXPAND2 W3, for every unary and binary
definition `p(x̄) := φ(x̄)` whose body is a v0 formula over the symbols strictly
below `p`. It generalises `VE.Route.Examples.copyLayer` (a body that is one
atom) to arbitrary bodies and to a dependency-ordered list of definitions, and
it instantiates the frozen `VE.Route.Layer` without changing it.

Conventions, shared with Python `ve/definitions.py`:

* a definition's body is typed in the context `args.reverse`, so de Bruijn
  index 0 is the last argument;
* `Def.premise` is the closed biconditional with binders in declared argument
  order, `∀x:s. ∀y:t. (p(x,y) → φ) ∧ (φ → p(x,y))`;
* `expand` lists the premises in dependency order, and that list is the
  `definitions` slice of Background.

Environments are presented as one full environment `E` (every declared
predicate, defined or not) together with `hide E ns`, the environment below the
definitions named `ns`. The layer for an ordered list `ds` goes from
`hide E (names ds)` (the base vocabulary) to `hide E []` (which is `E`). -/
namespace VE.Definitions
universe u
open VE.Route

/-- A definition `name(args) := body`. -/
structure Def where
  name : String
  args : List String
  body : VE.Formula
  deriving DecidableEq, Repr

/-- The defined atom applied to the bound arguments. -/
def Def.head (d : Def) : VE.Formula :=
  match d.args with
  | [_] => .unary d.name (.var 0)
  | [_, _] => .binary d.name (.var 1) (.var 0)
  | _ => .bottom

/-- `a ↔ b` in the v0 connectives, as Python writes it. -/
def iff (a b : VE.Formula) : VE.Formula := .and (.implies a b) (.implies b a)

/-- The closed biconditional generated for one definition. -/
def Def.premise (d : Def) : VE.Formula :=
  d.args.foldr (fun s a => .all s a) (iff d.head d.body)

/-- `Definitions.expand`: the executable elaboration, one premise per
definition, in the given (dependency) order. -/
def expand (ds : List Def) : List VE.Formula := ds.map Def.premise

def names (ds : List Def) : List String := ds.map Def.name

/-- A definition has one or two arguments (the v0 atoms). -/
def Def.Arity (d : Def) : Prop := d.args.length = 1 ∨ d.args.length = 2

/-- The reviewed meaning of one definition: on every well-typed argument
tuple, the defined predicate holds exactly when its body does. -/
def Agrees (S : VE.Structure.{u}) (d : Def) : Prop :=
  ∀ vs, VE.TupleTyped S d.args vs → (S.relation d.name vs ↔ d.body.denote S vs.reverse)

theorem iff_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) (a b : VE.Formula) :
    (iff a b).denote S ρ ↔ (a.denote S ρ ↔ b.denote S ρ) := by
  simp only [iff, VE.Formula.denote]
  exact ⟨fun h => ⟨h.1, h.2⟩, fun h => ⟨h.1, h.2⟩⟩

/-- The generated biconditional says exactly `Agrees`. -/
theorem premise_iff (d : Def) (hd : d.Arity) (S : VE.Structure.{u}) :
    d.premise.denote S [] ↔ Agrees S d := by
  obtain ⟨p, args, body⟩ := d
  simp only [Def.Arity] at hd
  match args, hd with
  | [s], _ =>
    simp only [Def.premise, Def.head, List.foldr, VE.Formula.denote, iff_denote, VE.Term.denote,
      Agrees]
    constructor
    · intro h vs hvs
      match vs, hvs with
      | [v], ⟨hv, _⟩ => simpa using h v hv
    · intro h v hv
      simpa using h [v] ⟨hv, trivial⟩
  | [s, t], _ =>
    simp only [Def.premise, Def.head, List.foldr, VE.Formula.denote, iff_denote, VE.Term.denote,
      Agrees]
    constructor
    · intro h vs hvs
      match vs, hvs with
      | [v, w], ⟨hv, hw, _⟩ => simpa using h v hv w hw
    · intro h v hv w hw
      simpa using h [v, w] ⟨hv, hw, trivial⟩

/-- `faithful`: the generated premises hold exactly when every defined
predicate agrees with its body. -/
theorem faithful (ds : List Def) (hd : ∀ d ∈ ds, d.Arity) (S : VE.Structure.{u}) :
    (∀ a ∈ expand ds, a.denote S []) ↔ ∀ d ∈ ds, Agrees S d := by
  simp only [expand, List.mem_map, forall_exists_index, and_imp, forall_apply_eq_imp_iff₂]
  exact ⟨fun h d hm => (premise_iff d (hd d hm) S).mp (h d hm),
    fun h d hm => (premise_iff d (hd d hm) S).mpr (h d hm)⟩

/-! ## Environments and structures -/

/-- The environment below the definitions named `ns`: they are undeclared. -/
def hide (E : VE.Environment) (ns : List String) : VE.Environment :=
  { E with predicates := fun r => if r ∈ ns then none else E.predicates r }

theorem hide_nil (E : VE.Environment) : hide E [] = E := by
  cases E
  simp [hide]

/-- Forget the relations of the symbols `ns`. -/
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

/-- Interpret one defined predicate by its body; every other relation is kept. -/
def interpret (d : Def) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun r vs =>
      if r = d.name then VE.TupleTyped S d.args vs ∧ d.body.denote S vs.reverse
      else S.relation r vs }

theorem sortOf_congr {E E' : VE.Environment} (hc : E'.constants = E.constants) (Γ : List String)
    (t : VE.Term) : t.sortOf E' Γ = t.sortOf E Γ := by
  cases t <;> simp [VE.Term.sortOf, hc]

/-- Typing is monotone in the declared predicates. -/
theorem wf_mono {E E' : VE.Environment} (hs : E'.sorts = E.sorts) (hc : E'.constants = E.constants)
    (hp : ∀ r ss, E.predicates r = some ss → E'.predicates r = some ss)
    (a : VE.Formula) (Γ : List String) (hw : a.WellFormed E Γ) : a.WellFormed E' Γ := by
  induction a generalizing Γ with
  | unary r t =>
    obtain ⟨s, hr, ht⟩ := hw
    exact ⟨s, hp r _ hr, by rw [sortOf_congr hc]; exact ht⟩
  | binary r t w =>
    obtain ⟨s₁, s₂, hr, ht, hw'⟩ := hw
    exact ⟨s₁, s₂, hp r _ hr, by rw [sortOf_congr hc]; exact ht, by rw [sortOf_congr hc]; exact hw'⟩
  | eq t w =>
    obtain ⟨s, ht, hw'⟩ := hw
    exact ⟨s, by rw [sortOf_congr hc]; exact ht, by rw [sortOf_congr hc]; exact hw'⟩
  | top | bottom => trivial
  | not a ih => exact ih Γ hw
  | and a b ia ib | or a b ia ib | implies a b ia ib => exact ⟨ia Γ hw.1, ib Γ hw.2⟩
  | all t a ih | ex t a ih => exact ⟨by rw [hs]; exact hw.1, ih (t :: Γ) hw.2⟩

/-- Truth of a formula typed over `E` only reads the relations `E` declares. -/
theorem denote_congr (E : VE.Environment) (S : VE.Structure.{u})
    (R : String → List S.Carrier → Prop)
    (hR : ∀ r ss vs, E.predicates r = some ss → (R r vs ↔ S.relation r vs))
    (a : VE.Formula) (Γ : List String) (ρ : VE.Valuation S) (hw : a.WellFormed E Γ) :
    a.denote { S with relation := R } ρ ↔ a.denote S ρ := by
  induction a generalizing Γ ρ with
  | unary r t =>
    obtain ⟨_, hr, _⟩ := hw
    simp only [VE.Formula.denote, VE.Term.denote]
    constructor
    · rintro ⟨v, hv, h⟩; exact ⟨v, by cases t <;> exact hv, (hR r _ _ hr).mp h⟩
    · rintro ⟨v, hv, h⟩; exact ⟨v, by cases t <;> exact hv, (hR r _ _ hr).mpr h⟩
  | binary r t w =>
    obtain ⟨_, _, hr, _⟩ := hw
    simp only [VE.Formula.denote, VE.Term.denote]
    constructor
    · rintro ⟨v, v', hv, hv', h⟩
      exact ⟨v, v', by cases t <;> exact hv, by cases w <;> exact hv', (hR r _ _ hr).mp h⟩
    · rintro ⟨v, v', hv, hv', h⟩
      exact ⟨v, v', by cases t <;> exact hv, by cases w <;> exact hv', (hR r _ _ hr).mpr h⟩
  | eq t w => cases t <;> cases w <;> simp [VE.Formula.denote, VE.Term.denote]
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

/-! ## One definition as a `Layer` -/

/-- The obligations of one elaboration step from `E_in` to `E_out`: `E_out`
declares exactly one more predicate, `d.name : d.args`, and the body is typed
over `E_in` (so it mentions only symbols strictly below `d.name`, and never
`d.name` itself). -/
structure Step (E_in E_out : VE.Environment) (d : Def) : Prop where
  sorts : E_out.sorts = E_in.sorts
  constants : E_out.constants = E_in.constants
  fresh : E_in.predicates d.name = none
  declared : E_out.predicates d.name = some d.args
  others : ∀ r, r ≠ d.name → E_out.predicates r = E_in.predicates r
  arity : d.Arity
  args : ∀ s ∈ d.args, s ∈ E_in.sorts
  body : d.body.WellFormed E_in d.args.reverse

/-- Side conditions of the admissibility below the layer that only read
constants and domains (for example distinct `$string` literals) are unaffected
by changing relations. -/
def RelationFree (X : VE.Structure.{u} → Prop) : Prop :=
  ∀ (S : VE.Structure.{u}) (R : String → List S.Carrier → Prop), X { S with relation := R } ↔ X S

section Step
variable {E_in E_out : VE.Environment} {d : Def} (h : Step E_in E_out d)
include h

theorem Step.extends (a : VE.Formula) (Γ : List String) (hw : a.WellFormed E_in Γ) :
    a.WellFormed E_out Γ :=
  wf_mono h.sorts h.constants (fun r ss hr => by
    have hne : r ≠ d.name := fun he => by rw [he, h.fresh] at hr; cases hr
    rw [h.others r hne]; exact hr) a Γ hw

theorem Step.head_wellFormed : d.head.WellFormed E_out d.args.reverse := by
  obtain ⟨p, args, body⟩ := d
  have hd := h.arity
  have hdecl := h.declared
  have hargs := h.args
  simp only [Def.Arity] at hd
  match args, hd with
  | [s], _ => exact ⟨s, hdecl, rfl⟩
  | [s, t], _ => exact ⟨s, t, hdecl, rfl, rfl⟩

theorem Step.premise_wellFormed : d.premise.WellFormed E_out [] := by
  have hhead := h.head_wellFormed
  have hbody := h.extends d.body d.args.reverse h.body
  have hargs : ∀ s ∈ d.args, s ∈ E_out.sorts := fun s hs => by rw [h.sorts]; exact h.args s hs
  obtain ⟨p, args, body⟩ := d
  have hd := h.arity
  simp only [Def.Arity] at hd
  match args, hd with
  | [s], _ =>
    exact ⟨hargs s (by simp), ⟨hhead, hbody⟩, ⟨hbody, hhead⟩⟩
  | [s, t], _ =>
    exact ⟨hargs s (by simp), hargs t (by simp), ⟨hhead, hbody⟩, ⟨hbody, hhead⟩⟩

theorem Step.forget_admissible (S : VE.Structure.{u}) (hS : S.Admissible E_out) :
    (forget [d.name] S).Admissible E_in := by
  refine ⟨fun c s hc => hS.1 c s (by rw [h.constants]; exact hc), fun r vs hr => ?_⟩
  obtain ⟨hne, hr⟩ := hr
  have hne : r ≠ d.name := by simpa using hne
  obtain ⟨ss, hss, ht⟩ := hS.2 r vs hr
  exact ⟨ss, by rw [← h.others r hne]; exact hss,
    (VE.Route.Examples.tupleTyped_relation S _ ss vs).mpr ht⟩

theorem Step.restrict_holds (S : VE.Structure.{u}) (a : VE.Formula) (Γ : List String)
    (ρ : VE.Valuation S) (hw : a.WellFormed E_in Γ) :
    a.denote (forget [d.name] S) ρ ↔ a.denote S ρ :=
  denote_congr E_in S _ (fun r ss vs hr => by
    have hne : r ≠ d.name := fun he => by rw [he, h.fresh] at hr; cases hr
    simp [hne]) a Γ ρ hw

/-- The body reads the same in the interpretation as below it. -/
theorem Step.body_interpret (S₀ : VE.Structure.{u}) (ρ : VE.Valuation S₀) :
    d.body.denote (interpret d S₀) ρ ↔ d.body.denote S₀ ρ :=
  denote_congr E_in S₀ _ (fun r ss vs hr => by
    have hne : r ≠ d.name := fun he => by rw [he, h.fresh] at hr; cases hr
    simp [hne]) d.body d.args.reverse ρ h.body

theorem Step.interpret_admissible (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible E_in) :
    (interpret d S₀).Admissible E_out := by
  refine ⟨fun c s hc => h₀.1 c s (by rw [← h.constants]; exact hc), fun r vs hr => ?_⟩
  by_cases hrp : r = d.name
  · subst hrp
    simp only [interpret, if_true] at hr
    exact ⟨d.args, h.declared, (VE.Route.Examples.tupleTyped_relation S₀ _ _ vs).mpr hr.1⟩
  · simp only [interpret, hrp, if_false] at hr
    obtain ⟨ss, hss, ht⟩ := h₀.2 r vs hr
    exact ⟨ss, by rw [h.others r hrp]; exact hss,
      (VE.Route.Examples.tupleTyped_relation S₀ _ ss vs).mpr ht⟩

theorem Step.forget_interpret (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible E_in) :
    forget [d.name] (interpret d S₀) = S₀ := by
  cases S₀ with
  | mk C dom c rel =>
    simp only [forget, interpret, VE.Structure.mk.injEq, heq_eq_eq, true_and]
    funext r vs
    apply propext
    by_cases hr : r = d.name
    · subst hr
      simp only [List.mem_singleton, not_true_eq_false, false_and, false_iff]
      intro hrel
      obtain ⟨ss, hss, _⟩ := h₀.2 _ vs hrel
      rw [h.fresh] at hss
      cases hss
    · simp [hr]

theorem Step.interpret_agrees (S₀ : VE.Structure.{u}) : Agrees (interpret d S₀) d := by
  intro vs hvs
  have hb := h.body_interpret S₀ vs.reverse
  have ht := (VE.Route.Examples.tupleTyped_relation S₀ _ d.args vs).mp hvs
  change (if d.name = d.name then VE.TupleTyped S₀ d.args vs ∧ d.body.denote S₀ vs.reverse
    else S₀.relation d.name vs) ↔ d.body.denote (interpret d S₀) vs.reverse
  rw [if_pos rfl, hb]
  exact ⟨fun hx => hx.2, fun hx => ⟨ht, hx⟩⟩

theorem Step.expands (X : VE.Structure.{u} → Prop) (hX : RelationFree X)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible E_in ∧ X S₀) :
    Unique fun S => forget [d.name] S = S₀ ∧ (S.Admissible E_out ∧ X S) ∧
      ∀ a ∈ [d.premise], a.denote S [] := by
  refine ⟨interpret d S₀, ⟨h.forget_interpret S₀ h₀.1, ⟨h.interpret_admissible S₀ h₀.1,
    (hX S₀ _).mpr h₀.2⟩, ?_⟩, ?_⟩
  · simp only [List.mem_singleton, forall_eq]
    exact (premise_iff d h.arity _).mpr (h.interpret_agrees S₀)
  · rintro S ⟨rfl, ⟨hS, _⟩, hb⟩
    have ha : Agrees S d := (premise_iff d h.arity S).mp (hb _ (List.mem_singleton_self _))
    cases S with
    | mk C dom c rel =>
      simp only [interpret, forget, VE.Structure.mk.injEq, heq_eq_eq, true_and]
      funext r vs
      apply propext
      by_cases hr : r = d.name
      · subst hr
        simp only [if_true]
        have hb' := h.restrict_holds ⟨C, dom, c, rel⟩ d.body d.args.reverse vs.reverse h.body
        simp only [forget] at hb'
        rw [hb']
        constructor
        · intro hrel
          obtain ⟨ss, hss, ht⟩ := hS.2 _ vs hrel
          rw [h.declared] at hss
          cases hss
          exact ⟨(VE.Route.Examples.tupleTyped_relation ⟨C, dom, c, rel⟩ _ _ vs).mpr ht,
            (ha vs ht).mp hrel⟩
        · rintro ⟨ht, hbody⟩
          exact (ha vs ((VE.Route.Examples.tupleTyped_relation ⟨C, dom, c, rel⟩ _ _ vs).mp ht)).mpr
            hbody
      · simp [hr]

end Step

/-- One definition as an instance of the frozen `Layer`: premises are the
definition's biconditional, restriction forgets the defined predicate, the
reviewed meaning is `Agrees`, and `expands` is unique expansion. `X` is the
relation-free part of the admissibility below (for example distinct literals). -/
def stepLayer {Doc : Type} (E_in E_out : VE.Environment) (d : Def) (h : Step E_in E_out d)
    (X : VE.Structure.{u} → Prop) (hX : RelationFree X) : Layer fol.{u} Doc where
  E_in := E_in
  E_out := E_out
  extends_env a ha := h.extends a [] ha
  premises _ := [d.premise]
  premises_wellFormed _ a ha := by
    rw [List.mem_singleton.mp ha]
    exact h.premise_wellFormed
  Admissible_in S := S.Admissible E_in ∧ X S
  Admissible_out S := S.Admissible E_out ∧ X S
  admissible_out _ hS := hS.1
  restrict := forget [d.name]
  restrict_admissible S hS := ⟨h.forget_admissible S hS.1, (hX S _).mpr hS.2⟩
  restrict_holds S a _ ha := h.restrict_holds S a [] [] ha
  Intended _ S := Agrees S d
  faithful _ S _ := by
    simp only [List.mem_singleton, forall_eq]
    exact premise_iff d h.arity S
  expands _ S₀ h₀ := h.expands X hX S₀ h₀

/-! ## A dependency-ordered list of definitions -/

/-- The whole list is admissible over the full environment `E` when each
definition is one elaboration step from the environment hiding it and every
later definition to the environment hiding only the later ones. -/
def Chain (E : VE.Environment) : List Def → Prop
  | [] => True
  | d :: ds => Step (hide E (d.name :: names ds)) (hide E (names ds)) d ∧ Chain E ds

/-- A composed definitions layer with the facts its composition needs. -/
structure ChainLayer (Doc : Type) (E : VE.Environment) (ds : List Def)
    (X : VE.Structure.{u} → Prop) where
  layer : Layer fol.{u} Doc
  E_in : layer.E_in = hide E (names ds)
  E_out : layer.E_out = hide E []
  Admissible_in : ∀ S, layer.Admissible_in S ↔ S.Admissible (hide E (names ds)) ∧ X S
  Admissible_out : ∀ S, layer.Admissible_out S ↔ S.Admissible (hide E []) ∧ X S
  premises : ∀ doc, layer.premises doc = expand ds
  restrict : ∀ S, layer.restrict S = forget (names ds) S

/-- Compose the step layers innermost (lowest) first. -/
def chainLayer {Doc : Type} (E : VE.Environment) (X : VE.Structure.{u} → Prop) (hX : RelationFree X) :
    (ds : List Def) → Chain E ds → ChainLayer Doc E ds X
  | [], _ =>
    { layer := Layer.id (L := fol.{u}) (hide E []) (fun S => S.Admissible (hide E []) ∧ X S)
        (fun _ hS => hS.1)
      E_in := rfl
      E_out := rfl
      Admissible_in := fun _ => Iff.rfl
      Admissible_out := fun _ => Iff.rfl
      premises := fun _ => rfl
      restrict := fun S => (forget_nil S).symm }
  | d :: ds, h =>
    let r := chainLayer E X hX ds h.2
    let l₁ : Layer fol.{u} Doc := stepLayer _ _ d h.1 X hX
    { layer := Layer.comp l₁ r.layer r.E_in (fun S => r.Admissible_in S)
      E_in := rfl
      E_out := r.E_out
      Admissible_in := fun _ => Iff.rfl
      Admissible_out := r.Admissible_out
      premises := fun doc => congrArg (List.cons d.premise) (r.premises doc)
      restrict := fun S => by
        show forget [d.name] (r.layer.restrict S) = forget (names (d :: ds)) S
        rw [r.restrict, forget_forget]; rfl }

/-- The definitions layer of a checked list over the full environment `E`,
with relation-free side condition `X` on admissible structures. -/
def layer {Doc : Type} (E : VE.Environment) (ds : List Def) (h : Chain E ds)
    (X : VE.Structure.{u} → Prop) (hX : RelationFree X) : Layer fol.{u} Doc :=
  (chainLayer E X hX ds h).layer

theorem chain_arity (E : VE.Environment) : (ds : List Def) → Chain E ds → ∀ d ∈ ds, d.Arity
  | [], _, _, hd => nomatch hd
  | _ :: ds, h, _, hd => by
    rcases List.mem_cons.mp hd with rfl | hd
    · exact h.1.arity
    · exact chain_arity E ds h.2 _ hd

/-- `conservative`: every admissible structure of the base vocabulary has
exactly one admissible expansion to the full vocabulary satisfying the
definitions. Restriction forgets the defined predicates. -/
theorem conservative (E : VE.Environment) (ds : List Def) (h : Chain E ds)
    (X : VE.Structure.{u} → Prop) (hX : RelationFree X)
    (S₀ : VE.Structure.{u}) (h₀ : S₀.Admissible (hide E (names ds))) (hx : X S₀) :
    Unique fun S => forget (names ds) S = S₀ ∧ (S.Admissible E ∧ X S) ∧
      ∀ a ∈ expand ds, a.denote S [] := by
  let c := chainLayer (Doc := Unit) E X hX ds h
  obtain ⟨S, ⟨hr, ha, hp⟩, hu⟩ := c.layer.expands () S₀ ((c.Admissible_in S₀).mpr ⟨h₀, hx⟩)
  have ha' := (c.Admissible_out S).mp ha
  rw [hide_nil] at ha'
  refine ⟨S, ⟨by rw [← c.restrict]; exact hr, ha', by rw [← c.premises ()]; exact hp⟩, ?_⟩
  rintro S' ⟨hr', ha'', hp'⟩
  apply hu
  refine ⟨by rw [c.restrict]; exact hr', (c.Admissible_out S').mpr (by rw [hide_nil]; exact ha''),
    by rw [c.premises ()]; exact hp'⟩

/-- Conservativity in its consequence form: for premises and a conclusion over
the base vocabulary, consequence with the definitions over the full vocabulary
is exactly consequence without them over the base vocabulary. -/
theorem conservative_entails (E : VE.Environment) (ds : List Def) (h : Chain E ds)
    (X : VE.Structure.{u} → Prop) (hX : RelationFree X)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (hide E (names ds)) []) (hφ : φ.WellFormed (hide E (names ds)) []) :
    (∀ S : VE.Structure.{u}, S.Admissible E → X S → (∀ a ∈ expand ds ++ Γ, a.denote S []) →
        φ.denote S []) ↔
      (∀ S₀ : VE.Structure.{u}, S₀.Admissible (hide E (names ds)) → X S₀ →
        (∀ a ∈ Γ, a.denote S₀ []) → φ.denote S₀ []) := by
  let c := chainLayer (Doc := Unit) E X hX ds h
  have hwΓ : ∀ a ∈ Γ, fol.WellFormed c.layer.E_in a := fun a ha => by rw [c.E_in]; exact hΓ a ha
  have hwφ : fol.WellFormed c.layer.E_in φ := by rw [c.E_in]; exact hφ
  have hout : ∀ S, c.layer.Admissible_out S ↔ S.Admissible E ∧ X S := fun S => by
    rw [c.Admissible_out, hide_nil]
  constructor
  · intro hall S₀ h₀ hx hs
    obtain ⟨S, ⟨hr, ha, hp⟩, _⟩ := c.layer.expands () S₀ ((c.Admissible_in S₀).mpr ⟨h₀, hx⟩)
    subst hr
    apply (c.layer.restrict_holds S φ ha hwφ).mpr
    have ha' := (hout S).mp ha
    refine hall S ha'.1 ha'.2 (fun a hm => ?_)
    rcases List.mem_append.mp hm with hm | hm
    · exact hp a (by rw [c.premises ()]; exact hm)
    · exact (c.layer.restrict_holds S a ha (hwΓ a hm)).mp (hs a hm)
  · intro hbase S hS hx hs
    have ho : c.layer.Admissible_out S := (hout S).mpr ⟨hS, hx⟩
    have hi := (c.Admissible_in _).mp (c.layer.restrict_admissible S ho)
    apply (c.layer.restrict_holds S φ ho hwφ).mp
    exact hbase _ hi.1 hi.2 (fun a hm =>
      (c.layer.restrict_holds S a ho (hwΓ a hm)).mpr (hs a (List.mem_append_right _ hm)))

end VE.Definitions
