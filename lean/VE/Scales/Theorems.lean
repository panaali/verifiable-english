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
end VE.Scales
