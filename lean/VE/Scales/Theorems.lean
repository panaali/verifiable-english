import VE.Scales.Premises
import VE.Scales.Intended

/-! The theorems of `scales@0` (docs/spec/quantities.md 6.2): the generated premises hold exactly when
every dimension has its intended meaning, they are well typed, and each label names one premise. -/
namespace VE.Scales
open VE
universe u

/-- A true comparative or equative atom is typed: both arguments lie in the sort. -/
theorem typed2 {E : Environment} {S : Structure.{u}} (hS : S.Admissible E) {p s : String} {x y : S.Carrier}
    (h : E.predicates p = some [s, s]) (hr : S.relation p [x, y]) : S.domain s x ∧ S.domain s y := by
  obtain ⟨ss, hss, ht⟩ := hS.2 p [x, y] hr
  rw [h] at hss; cases hss
  simpa [TupleTyped] using ht

/-- A true graded atom is typed. -/
theorem typed1 {E : Environment} {S : Structure.{u}} (hS : S.Admissible E) {p s : String} {x : S.Carrier}
    (h : E.predicates p = some [s]) (hr : S.relation p [x]) : S.domain s x := by
  obtain ⟨ss, hss, ht⟩ := hS.2 p [x] hr
  rw [h] at hss; cases hss
  simpa [TupleTyped] using ht
/-- `Intended` as one conjunction, field by field. -/
theorem intended_iff_and (S : Structure.{u}) (d : Dimension) : Intended S d ↔
    (∀ x, S.domain d.sort x → ¬ S.relation d.more [x, x]) ∧
    (∀ x y z, S.domain d.sort x → S.domain d.sort y → S.domain d.sort z →
      S.relation d.more [x, y] → S.relation d.more [y, z] → S.relation d.more [x, z]) ∧
    (∀ e, d.same = some e → ∀ x, S.domain d.sort x → S.relation e [x, x]) ∧
    (∀ e, d.same = some e → ∀ x y, S.relation e [x, y] → S.relation e [y, x]) ∧
    (∀ e, d.same = some e → ∀ x y z, S.relation e [x, y] → S.relation e [y, z] → S.relation e [x, z]) ∧
    (∀ e, d.same = some e → ∀ x y, S.relation e [x, y] → ¬ S.relation d.more [x, y]) ∧
    (∀ e, d.same = some e → ∀ x y z,
      S.relation e [x, y] → S.relation d.more [y, z] → S.relation d.more [x, z]) ∧
    (∀ e, d.same = some e → ∀ x y z,
      S.relation d.more [x, y] → S.relation e [y, z] → S.relation d.more [x, z]) ∧
    (d.comparable = true → ∀ e, d.same = some e → ∀ x y, S.domain d.sort x → S.domain d.sort y →
      S.relation d.more [x, y] ∨ S.relation d.more [y, x] ∨ S.relation e [x, y]) ∧
    (∀ g ∈ d.grades, ∀ x y, S.relation g.name [y] →
      (g.direction = .upper → S.relation d.more [x, y] → S.relation g.name [x]) ∧
      (g.direction = .lower → S.relation d.more [y, x] → S.relation g.name [x]) ∧
      (∀ e, d.same = some e → S.relation e [x, y] → S.relation g.name [x])) ∧
    (∀ p ∈ d.above, ∀ x, S.relation p.1 [x] → S.relation p.2 [x]) :=
  ⟨fun ⟨a, b, c, d, e, f, g, h, i, j, k⟩ => ⟨a, b, c, d, e, f, g, h, i, j, k⟩,
   fun ⟨a, b, c, d, e, f, g, h, i, j, k⟩ => ⟨a, b, c, d, e, f, g, h, i, j, k⟩⟩

/-- One dimension: its premises hold exactly when it has its intended meaning, given that its true atoms
are typed. -/
theorem dim_iff (S : Structure.{u}) (d : Dimension)
    (hm : ∀ x y, S.relation d.more [x, y] → S.domain d.sort x ∧ S.domain d.sort y)
    (he : ∀ e, d.same = some e → ∀ x y, S.relation e [x, y] → S.domain d.sort x ∧ S.domain d.sort y)
    (hg : ∀ g ∈ d.grades, ∀ x, S.relation g.name [x] → S.domain d.sort x)
    (ha : ∀ p ∈ d.above, ∀ x, S.relation p.1 [x] → S.domain d.sort x) :
    (∀ a ∈ (premises d).map (·.2), a.denote S []) ↔ Intended S d := by
  have hdir : ∀ g : Grade, g.direction = .upper ∨ g.direction = .lower := by
    intro g; cases g.direction <;> simp
  rw [intended_iff_and]
  rcases hs : d.same with _ | e
  · simp only [premises, hs, List.map_append, List.map_flatMap, List.forall_mem_append,
      List.forall_mem_flatMap, List.map_cons, List.map_nil, List.forall_mem_cons, List.map_map,
      List.forall_mem_map, Function.comp_def]
    simp [rel1, rel2, Formula.denote, Term.denote, forall_and]
    constructor
    · rintro ⟨⟨⟨h1, h2⟩, h3⟩, h4⟩
      refine ⟨h1, fun x y z hx hy hz => h2 x hx y hy z hz, ⟨?_, ?_⟩,
        fun a b hab x hx => h4 a b hab x (ha (a, b) hab x hx) hx⟩
      · intro g hgm x y hy hd hxy
        have := h3 g hgm x (hm _ _ hxy).1 y (hg g hgm y hy) hy
        rw [hd] at this; simp [Formula.denote, Term.denote] at this; exact this hxy
      · intro g hgm x y hy hd hxy
        have := h3 g hgm x (hm _ _ hxy).2 y (hg g hgm y hy) hy
        rw [hd] at this; simp [Formula.denote, Term.denote] at this; exact this hxy
    · rintro ⟨h1, h2, ⟨h3, h4⟩, h5⟩
      refine ⟨⟨⟨h1, fun x hx y hy z hz => h2 x y z hx hy hz⟩, ?_⟩, fun a b hab x _ => h5 a b hab x⟩
      intro g hg x _ y _ hgy hden
      rcases hdir g with hd | hd <;> rw [hd] at hden <;> simp [Formula.denote, Term.denote] at hden
      · exact h3 g hg x y hgy hd hden
      · exact h4 g hg x y hgy hd hden
  · have he' := he e hs
    have closedOf : ∀ (h3 : ∀ g ∈ d.grades, ∀ v, S.domain d.sort v → ∀ v₁, S.domain d.sort v₁ →
        S.relation g.name [v₁] → Formula.denote S [v₁, v] (match g.direction with
          | .upper => .binary d.more (.var 1) (.var 0)
          | .lower => .binary d.more (.var 0) (.var 1)) → S.relation g.name [v])
        (h4 : ∀ g ∈ d.grades, ∀ v, S.domain d.sort v → ∀ v₁, S.domain d.sort v₁ →
          S.relation g.name [v₁] → S.relation e [v, v₁] → S.relation g.name [v]),
        (∀ g ∈ d.grades, ∀ x y, S.relation g.name [y] →
          g.direction = .upper → S.relation d.more [x, y] → S.relation g.name [x]) ∧
        (∀ g ∈ d.grades, ∀ x y, S.relation g.name [y] →
          g.direction = .lower → S.relation d.more [y, x] → S.relation g.name [x]) ∧
        (∀ g ∈ d.grades, ∀ x y, S.relation g.name [y] → S.relation e [x, y] → S.relation g.name [x]) := by
      intro h3 h4
      refine ⟨?_, ?_, fun g hgm x y hy hxy => h4 g hgm x (he' _ _ hxy).1 y (hg g hgm y hy) hy hxy⟩
      · intro g hgm x y hy hd hxy
        have := h3 g hgm x (hm _ _ hxy).1 y (hg g hgm y hy) hy
        rw [hd] at this; simp [Formula.denote, Term.denote] at this; exact this hxy
      · intro g hgm x y hy hd hxy
        have := h3 g hgm x (hm _ _ hxy).2 y (hg g hgm y hy) hy
        rw [hd] at this; simp [Formula.denote, Term.denote] at this; exact this hxy
    have closedTo : ∀ (h3 : ∀ g ∈ d.grades, ∀ x y, S.relation g.name [y] →
          g.direction = .upper → S.relation d.more [x, y] → S.relation g.name [x])
        (h4 : ∀ g ∈ d.grades, ∀ x y, S.relation g.name [y] →
          g.direction = .lower → S.relation d.more [y, x] → S.relation g.name [x]),
        ∀ g ∈ d.grades, ∀ v, S.domain d.sort v → ∀ v₁, S.domain d.sort v₁ →
        S.relation g.name [v₁] → Formula.denote S [v₁, v] (match g.direction with
          | .upper => .binary d.more (.var 1) (.var 0)
          | .lower => .binary d.more (.var 0) (.var 1)) → S.relation g.name [v] := by
      intro h3 h4 g hgm x _ y _ hgy hden
      rcases hdir g with hd | hd <;> rw [hd] at hden <;> simp [Formula.denote, Term.denote] at hden
      · exact h3 g hgm x y hgy hd hden
      · exact h4 g hgm x y hgy hd hden
    cases hc : d.comparable <;>
    simp only [premises, hs, hc, List.map_append, List.map_flatMap, List.forall_mem_append,
      List.forall_mem_flatMap, List.map_cons, List.map_nil, List.forall_mem_cons, List.map_map,
      List.forall_mem_map, Function.comp_def] <;>
    simp [rel1, rel2, Formula.denote, Term.denote, forall_and] <;>
    constructor
    · rintro ⟨⟨⟨⟨h1, h2⟩, h3, h4, h5, h6, h7, h8⟩, h10, h11⟩, h12⟩
      exact ⟨h1, fun x y z hx hy hz => h2 x hx y hy z hz, h3,
        fun x y hxy => h4 x (he' _ _ hxy).1 y (he' _ _ hxy).2 hxy,
        fun x y z hxy hyz => h5 x (he' _ _ hxy).1 y (he' _ _ hxy).2 z (he' _ _ hyz).2 hxy hyz,
        fun x y hxy => h6 x (he' _ _ hxy).1 y (he' _ _ hxy).2 hxy,
        fun x y z hxy hyz => h7 x (he' _ _ hxy).1 y (he' _ _ hxy).2 z (hm _ _ hyz).2 hxy hyz,
        fun x y z hxy hyz => h8 x (hm _ _ hxy).1 y (hm _ _ hxy).2 z (he' _ _ hyz).2 hxy hyz,
        closedOf h10 h11, fun a b hab x hx => h12 a b hab x (ha (a, b) hab x hx) hx⟩
    · rintro ⟨h1, h2, h3, h4, h5, h6, h7, h8, ⟨h10, h11, h12⟩, h13⟩
      exact ⟨⟨⟨⟨h1, fun x hx y hy z hz => h2 x y z hx hy hz⟩, h3, fun x _ y _ => h4 x y,
        fun x _ y _ z _ => h5 x y z, fun x _ y _ => h6 x y, fun x _ y _ z _ => h7 x y z,
        fun x _ y _ z _ => h8 x y z⟩, closedTo h10 h11, fun g hgm x _ y _ => h12 g hgm x y⟩,
        fun a b hab x _ => h13 a b hab x⟩
    · rintro ⟨⟨⟨⟨h1, h2⟩, ⟨h3, h4, h5, h6, h7, h8⟩, h9⟩, h10, h11⟩, h12⟩
      exact ⟨h1, fun x y z hx hy hz => h2 x hx y hy z hz, h3,
        fun x y hxy => h4 x (he' _ _ hxy).1 y (he' _ _ hxy).2 hxy,
        fun x y z hxy hyz => h5 x (he' _ _ hxy).1 y (he' _ _ hxy).2 z (he' _ _ hyz).2 hxy hyz,
        fun x y hxy => h6 x (he' _ _ hxy).1 y (he' _ _ hxy).2 hxy,
        fun x y z hxy hyz => h7 x (he' _ _ hxy).1 y (he' _ _ hxy).2 z (hm _ _ hyz).2 hxy hyz,
        fun x y z hxy hyz => h8 x (hm _ _ hxy).1 y (hm _ _ hxy).2 z (he' _ _ hyz).2 hxy hyz,
        fun x y hx hy => h9 x hx y hy, closedOf h10 h11,
        fun a b hab x hx => h12 a b hab x (ha (a, b) hab x hx) hx⟩
    · rintro ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9, ⟨h10, h11, h12⟩, h13⟩
      exact ⟨⟨⟨⟨h1, fun x hx y hy z hz => h2 x y z hx hy hz⟩, ⟨h3, fun x _ y _ => h4 x y,
        fun x _ y _ z _ => h5 x y z, fun x _ y _ => h6 x y, fun x _ y _ z _ => h7 x y z,
        fun x _ y _ z _ => h8 x y z⟩, fun x hx y hy => h9 x y hx hy⟩,
        closedTo h10 h11, fun g hgm x _ y _ => h12 g hgm x y⟩, fun a b hab x _ => h13 a b hab x⟩

/-- What `WellFormed` gives one dimension: its predicates' signatures and its `above` pairs' grades. -/
theorem dim_ok {E : Environment} {ots : List String} {D : ScaleDoc} (hD : WellFormed E ots D = true)
    {d : Dimension} (hd : d ∈ D.dims) :
    d.sort ∈ E.sorts ∧ E.predicates d.more = some [d.sort, d.sort] ∧
    (∀ e, d.same = some e → E.predicates e = some [d.sort, d.sort]) ∧
    (∀ g ∈ d.grades, E.predicates g.name = some [d.sort]) ∧
    (∀ p ∈ d.above, (∃ g ∈ d.grades, g.name = p.1) ∧ ∃ h ∈ d.grades, h.name = p.2) := by
  simp only [WellFormed, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hD
  obtain ⟨-, hall⟩ := hD
  obtain ⟨⟨⟨⟨⟨⟨hs, hm⟩, he⟩, hg⟩, ha⟩, -⟩, -⟩ := hall d hd
  refine ⟨List.contains_iff_mem.mp hs, by simpa using hm, ?_, fun g hg' => by simpa using (hg g hg').1, ?_⟩
  · intro e he'; rw [he'] at he; simpa using he
  · intro p hp
    have := ha p hp
    split at this
    · next g h hg₁ hh₁ =>
      exact ⟨⟨g, List.mem_of_find?_eq_some hg₁, by simpa using List.find?_some hg₁⟩,
        ⟨h, List.mem_of_find?_eq_some hh₁, by simpa using List.find?_some hh₁⟩⟩
    · simp at this

/-- **Faithful**: the premises hold exactly when every dimension has its intended meaning. -/
theorem premises_iff_intended (E : VE.Environment) (ots : List String) (D : ScaleDoc)
    (hD : WellFormed E ots D = true) (S : VE.Structure.{u}) (hS : S.Admissible E) :
    (∀ a ∈ (scalePremises D).map (·.2), a.denote S []) ↔ ∀ d ∈ D.dims, Intended S d := by
  simp only [scalePremises, List.map_flatMap, List.forall_mem_flatMap]
  refine forall₂_congr fun d hd => ?_
  obtain ⟨-, hm, he, hg, ha⟩ := dim_ok hD hd
  refine dim_iff S d (fun x y h => typed2 hS hm h) (fun e he' x y h => typed2 hS (he e he') h)
    (fun g hg' x h => typed1 hS (hg g hg') h) (fun p hp x h => ?_)
  obtain ⟨⟨g, hg', hn⟩, -⟩ := ha p hp
  exact typed1 hS (hg g hg') (hn ▸ h)

/-- The premises are well typed; at `E := envAt (fill U) 0` this is the `scales` pack's typing obligation. -/
theorem premises_wellTyped (E : VE.Environment) (ots : List String) (D : ScaleDoc)
    (hD : WellFormed E ots D = true) :
    ∀ a ∈ (scalePremises D).map (·.2), a.WellFormed E [] := by
  simp only [scalePremises, List.map_flatMap, List.forall_mem_flatMap]
  intro d hd
  obtain ⟨hs, hm, he, hg, ha⟩ := dim_ok hD hd
  rcases hse : d.same with _ | e <;> cases hc : d.comparable <;>
  simp only [premises, hse, hc, List.map_append, List.map_flatMap, List.forall_mem_append,
    List.forall_mem_flatMap, List.map_cons, List.map_nil, List.forall_mem_cons, List.map_map,
    List.forall_mem_map, Function.comp_def] <;>
  simp [rel1, rel2, Formula.WellFormed, Term.sortOf, hs, hm, he, hse] <;>
  refine ⟨fun g hg' => ?_, fun a b hab => ?_⟩ <;>
  first
  | (simp only [hg g hg', true_and, and_true]; split <;> simp [Formula.WellFormed, Term.sortOf, hm])
  | (obtain ⟨⟨g, hg', rfl⟩, ⟨h, hh, rfl⟩⟩ := ha (a, b) hab; exact ⟨hg g hg', hg h hh⟩)

/-- **One premise per label**: a reported label or instance, and its `origins` entry, names one premise. -/
theorem scalePremises_labels_nodup (E : VE.Environment) (ots : List String) (D : ScaleDoc)
    (hD : WellFormed E ots D = true) : ((scalePremises D).map (·.1)).Nodup := by
  simp only [WellFormed, Bool.and_eq_true, decide_eq_true_eq] at hD
  exact hD.1.2

/-! One role per predicate, and the two model constructions that use it. -/

/-- Two distinct members of a pairwise list are related one way or the other. -/
theorem pairwise_or {α : Type} {R : α → α → Prop} : ∀ {l : List α}, l.Pairwise R →
    ∀ {a b : α}, a ∈ l → b ∈ l → a ≠ b → R a b ∨ R b a
  | _ :: _, .cons h hl, _, _, ha, hb, hne => by
    cases ha with
    | head => cases hb with
      | head => exact absurd rfl hne
      | tail _ hb => exact .inl (h _ hb)
    | tail _ ha => cases hb with
      | head => exact .inr (h _ ha)
      | tail _ hb => exact pairwise_or hl ha hb hne

/-- **One role per predicate**, the consequence of `WellFormed`'s symbol conjunct the constructions below
use: no dimension's comparative is the equative of a dimension of the block, itself or another. -/
theorem more_ne_same {E : Environment} {ots : List String} {D : ScaleDoc} (hD : WellFormed E ots D = true)
    {d d' : Dimension} (hd : d ∈ D.dims) (hd' : d' ∈ D.dims) : d'.same ≠ some d.more := by
  intro hs
  simp only [WellFormed, Bool.and_eq_true, decide_eq_true_eq] at hD
  have hnd := hD.1.1
  simp only [ScaleDoc.symbols, List.Nodup, List.pairwise_flatMap] at hnd
  have hm : d.more ∈ d'.symbols := by simp [Dimension.symbols, hs]
  by_cases hdd : d = d'
  · subst hdd
    have := hnd.1 d hd
    simp only [Dimension.symbols, hs, List.pairwise_cons] at this
    exact this.1 d.more (by simp) rfl
  · rcases pairwise_or hnd.2 hd hd' hdd with h | h
    · exact h d.more (by simp [Dimension.symbols]) d.more hm rfl
    · exact h d.more hm d.more (by simp [Dimension.symbols]) rfl

/-- `S` with the symbols of `D` reread by their roles: an equative holds of any two objects of its
dimension's sort, a graded word (when `grade`) of every object of its dimension's sort, a comparative of
nothing. Every other predicate keeps its meaning in `S`. -/
def reread (D : ScaleDoc) (S : Structure.{u}) (grade : Prop) : Structure.{u} where
  Carrier := S.Carrier
  domain := S.domain
  constant := S.constant
  relation p vs := if p ∈ D.symbols then
      match vs with
      | [x, y] => ∃ d ∈ D.dims, d.same = some p ∧ S.domain d.sort x ∧ S.domain d.sort y
      | [x] => grade ∧ ∃ d ∈ D.dims, ∃ g ∈ d.grades, g.name = p ∧ S.domain d.sort x
      | _ => False
    else S.relation p vs

/-- The one-object structure: every sort holds the object, every constant names it, no relation holds. -/
def point : Structure.{0} := ⟨Unit, fun _ _ => True, fun _ => some (), fun _ _ => False⟩

section reread
variable {E : Environment} {ots : List String} {D : ScaleDoc} {S : Structure.{u}} {grade : Prop}

theorem reread_rel2 {p : String} (hp : p ∈ D.symbols) (x y : (reread D S grade).Carrier) :
    (reread D S grade).relation p [x, y] ↔ ∃ d ∈ D.dims, d.same = some p ∧ S.domain d.sort x ∧ S.domain d.sort y := by
  simp [reread, hp]

theorem reread_rel1 {p : String} (hp : p ∈ D.symbols) (x : (reread D S grade).Carrier) :
    (reread D S grade).relation p [x] ↔ grade ∧ ∃ d ∈ D.dims, ∃ g ∈ d.grades, g.name = p ∧ S.domain d.sort x := by
  simp [reread, hp]

theorem reread_fresh {p : String} (hp : p ∉ D.symbols) (vs : List S.Carrier) :
    (reread D S grade).relation p vs = S.relation p vs := by
  simp [reread, hp]

theorem tupleTyped_reread : ∀ (ss : List String) (vs : List S.Carrier),
    TupleTyped (reread D S grade) ss vs ↔ TupleTyped S ss vs
  | [], [] | [], _ :: _ | _ :: _, [] => Iff.rfl
  | _ :: ss, _ :: vs => and_congr Iff.rfl (tupleTyped_reread ss vs)

theorem mem_symbols {d : Dimension} (hd : d ∈ D.dims) :
    d.more ∈ D.symbols ∧ (∀ e, d.same = some e → e ∈ D.symbols) ∧ ∀ g ∈ d.grades, g.name ∈ D.symbols := by
  simp only [ScaleDoc.symbols, List.mem_flatMap]
  refine ⟨⟨d, hd, by simp [Dimension.symbols]⟩, fun e he => ⟨d, hd, by simp [Dimension.symbols, he]⟩,
    fun g hg => ⟨d, hd, ?_⟩⟩
  simp only [Dimension.symbols, List.mem_cons, List.mem_append, List.mem_map]
  exact .inr (.inr ⟨g, hg, rfl⟩)

theorem reread_admissible (hD : WellFormed E ots D = true) (hS : S.Admissible E) :
    (reread D S grade).Admissible E := by
  refine ⟨hS.1, fun p vs h => ?_⟩
  by_cases hp : p ∈ D.symbols
  · simp only [reread, hp, if_true] at h
    match vs, h with
    | [x, y], ⟨d, hd, hs, hx, hy⟩ =>
      exact ⟨[d.sort, d.sort], (dim_ok hD hd).2.2.1 p hs, hx, hy, trivial⟩
    | [x], ⟨_, d, hd, g, hg, hn, hx⟩ =>
      exact ⟨[d.sort], hn ▸ (dim_ok hD hd).2.2.2.1 g hg, hx, trivial⟩
  · obtain ⟨ss, h₁, h₂⟩ := hS.2 p vs (by rwa [reread_fresh hp] at h)
    exact ⟨ss, h₁, (tupleTyped_reread _ _).mpr h₂⟩

/-- Every dimension of a well-formed block has its intended meaning in the reread structure. -/
theorem reread_intended (hD : WellFormed E ots D = true) {d : Dimension} (hd : d ∈ D.dims) :
    Intended (reread D S grade) d := by
  obtain ⟨hmS, heS, hgS⟩ := mem_symbols hd
  obtain ⟨-, -, hse, hsg, ha⟩ := dim_ok hD hd
  have noMore : ∀ x y, ¬ (reread D S grade).relation d.more [x, y] := fun x y h => by
    obtain ⟨d', hd', hs, -⟩ := (reread_rel2 hmS x y).mp h
    exact more_ne_same hD hd hd' hs
  have sort2 : ∀ e, d.same = some e → ∀ d' ∈ D.dims, d'.same = some e → d'.sort = d.sort := fun e he d' hd' hs => by
    have := (dim_ok hD hd').2.2.1 e hs; rw [hse e he] at this; simp at this; exact this.symm
  have sort1 : ∀ g ∈ d.grades, ∀ d' ∈ D.dims, ∀ g' ∈ d'.grades, g'.name = g.name → d'.sort = d.sort :=
    fun g hg d' hd' g' hg' hn => by
      have := (dim_ok hD hd').2.2.2.1 g' hg'; rw [hn, hsg g hg] at this; simp at this; exact this.symm
  refine ⟨fun x _ h => noMore x x h, fun _ _ _ _ _ _ h => (noMore _ _ h).elim, fun e he x hx => ?_,
    fun e he x y h => ?_, fun e he x y z h₁ h₂ => ?_, fun _ _ x y _ h => noMore x y h,
    fun _ _ _ _ _ _ h => (noMore _ _ h).elim, fun _ _ _ _ _ h _ => (noMore _ _ h).elim,
    fun _ e he x y hx hy => .inr (.inr ((reread_rel2 (heS e he) x y).mpr ⟨d, hd, he, hx, hy⟩)),
    fun g hg x y hy => ⟨fun _ h => (noMore _ _ h).elim, fun _ h => (noMore _ _ h).elim, fun e he h => ?_⟩,
    fun p hp x h => ?_⟩
  · exact (reread_rel2 (heS e he) x x).mpr ⟨d, hd, he, hx, hx⟩
  · obtain ⟨d', hd', hs, hx, hy⟩ := (reread_rel2 (heS e he) x y).mp h
    exact (reread_rel2 (heS e he) y x).mpr ⟨d', hd', hs, hy, hx⟩
  · obtain ⟨d₁, hd₁, hs₁, hx, -⟩ := (reread_rel2 (heS e he) x y).mp h₁
    obtain ⟨d₂, hd₂, hs₂, -, hz⟩ := (reread_rel2 (heS e he) y z).mp h₂
    rw [sort2 e he d₂ hd₂ hs₂, ← sort2 e he d₁ hd₁ hs₁] at hz
    exact (reread_rel2 (heS e he) x z).mpr ⟨d₁, hd₁, hs₁, hx, hz⟩
  · obtain ⟨d', hd', hs, hx, -⟩ := (reread_rel2 (heS e he) x y).mp h
    obtain ⟨hgr, -⟩ := (reread_rel1 (hgS g hg) y).mp hy
    rw [sort2 e he d' hd' hs] at hx
    exact (reread_rel1 (hgS g hg) x).mpr ⟨hgr, d, hd, g, hg, rfl, hx⟩
  · obtain ⟨⟨g, hg, hn₁⟩, ⟨h', hh, hn₂⟩⟩ := ha p hp
    obtain ⟨hgr, d', hd', g', hg', hn, hx⟩ := (reread_rel1 (hn₁ ▸ hgS g hg) x).mp h
    rw [sort1 g hg d' hd' g' hg' (hn.trans hn₁.symm)] at hx
    exact (reread_rel1 (hn₂ ▸ hgS h' hh) x).mpr ⟨hgr, d, hd, h', hh, hn₂, hx⟩

/-- A formula without a symbol of `D` means the same in `S` and in the reread structure. -/
theorem reread_denote (a : Formula) : ∀ ρ : List S.Carrier, Fresh D a →
    (a.denote (reread D S grade) ρ ↔ a.denote S ρ) := by
  have hterm : ∀ (ρ : List S.Carrier) (t : Term), t.denote (reread D S grade) ρ = t.denote S ρ := by
    intro ρ t; cases t <;> rfl
  induction a with
  | top | bottom => intro _ _; exact Iff.rfl
  | eq t t' => intro ρ _; simp only [Formula.denote, hterm]; exact Iff.rfl
  | unary p t =>
    intro ρ h
    have hp : p ∉ D.symbols := h p (by simp [VE.Norms.preds])
    simp only [Formula.denote, hterm, reread_fresh hp]; exact Iff.rfl
  | binary p t t' =>
    intro ρ h
    have hp : p ∉ D.symbols := h p (by simp [VE.Norms.preds])
    simp only [Formula.denote, hterm, reread_fresh hp]; exact Iff.rfl
  | not a ih => intro ρ h; exact not_congr (ih ρ h)
  | and a b iha ihb | or a b iha ihb | implies a b iha ihb =>
    intro ρ h
    have ha := iha ρ fun p hp => h p (by simp [VE.Norms.preds, hp])
    have hb := ihb ρ fun p hp => h p (by simp [VE.Norms.preds, hp])
    simp only [Formula.denote, ha, hb]
  | all s a ih | ex s a ih =>
    intro ρ h
    simp only [Formula.denote]
    first
    | exact forall_congr' fun v => imp_congr_right fun _ => ih (v :: ρ) h
    | exact exists_congr fun v => and_congr_right fun _ => ih (v :: ρ) h

end reread

/-- **Conservative**: formulas without scale symbols have the same consequences with the scale premises. -/
theorem scales_conservative (E : VE.Environment) (ots : List String) (D : ScaleDoc)
    (hD : WellFormed E ots D = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, Fresh D a) (hφ : Fresh D φ) :
    VE.Entails.{u} E (Γ ++ (scalePremises D).map (·.2)) φ ↔ VE.Entails.{u} E Γ φ := by
  refine ⟨fun h S hS hΓS => ?_, fun h S hS hall => h S hS fun a ha => hall a (List.mem_append_left _ ha)⟩
  have hS' := reread_admissible (grade := False) hD hS
  refine (reread_denote φ [] hφ).mp (h _ hS' fun a ha => ?_)
  rcases List.mem_append.mp ha with ha | ha
  · exact (reread_denote a [] (hΓ a ha)).mpr (hΓS a ha)
  · exact (premises_iff_intended E ots D hD _ hS').mpr (fun d hd => reread_intended hD hd) a ha

/-- **No threshold is chosen**: for each graded word, the premises alone have a model where an object has it and one
where it does not. -/
theorem grade_open (E : VE.Environment) (ots : List String) (D : ScaleDoc) (hD : WellFormed E ots D = true)
    (d : Dimension) (hd : d ∈ D.dims) (g : Grade) (hg : g ∈ d.grades) :
    (∃ S : VE.Structure.{0}, S.Admissible E ∧
      (∀ a ∈ (scalePremises D).map (·.2), a.denote S []) ∧ ∃ x, S.domain d.sort x ∧ S.relation g.name [x]) ∧
    (∃ S : VE.Structure.{0}, S.Admissible E ∧
      (∀ a ∈ (scalePremises D).map (·.2), a.denote S []) ∧ ∃ x, S.domain d.sort x ∧ ¬ S.relation g.name [x]) := by
  have hpt : point.Admissible E := ⟨fun _ _ _ => ⟨(), rfl, trivial⟩, fun _ _ h => h.elim⟩
  have hgS := (mem_symbols hd).2.2 g hg
  have models : ∀ grade : Prop, ∀ a ∈ (scalePremises D).map (·.2), a.denote (reread D point grade) [] :=
    fun grade => (premises_iff_intended E ots D hD _ (reread_admissible hD hpt)).mpr
      fun d' hd' => reread_intended hD hd'
  exact ⟨⟨reread D point True, reread_admissible hD hpt, models True, (), trivial,
      (reread_rel1 (S := point) (grade := True) hgS ()).mpr ⟨trivial, d, hd, g, hg, rfl, trivial⟩⟩,
    ⟨reread D point False, reread_admissible hD hpt, models False, (), trivial,
      fun h => ((reread_rel1 (S := point) (grade := False) hgS ()).mp h).1⟩⟩
end VE.Scales
