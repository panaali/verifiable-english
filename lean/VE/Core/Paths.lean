import VE.Paths

/-! `VE.Paths` under the names the Core proofs and statements use: every declaration of the shared
module keeps its Core name, as an abbreviation or a corollary with the identical statement. -/
namespace VE.Core
universe u

abbrev Path {α : Type u} (R : α → α → Prop) : α → α → Prop := VE.Paths.Path R
abbrev Path.below := @VE.Paths.Path.below.{u}

theorem Path.trans {α : Type u} {R : α → α → Prop} {a b c : α}
    (h : Path R a b) (g : Path R b c) : Path R a c := VE.Paths.Path.trans h g

theorem Path.unfold {α : Type u} {R : α → α → Prop} {a c : α} :
    Path R a c ↔ R a c ∨ ∃ b, R a b ∧ Path R b c := VE.Paths.Path.unfold

theorem Path.least {α : Type u} {R : α → α → Prop} {a c : α} :
    Path R a c ↔ ∀ X : α → α → Prop,
      (∀ x y, R x y → X x y) →
      (∀ x y z, R x y → X y z → X x z) → X a c := VE.Paths.Path.least

def Kind := VE.Paths.Kind
instance instDecidableEqKind : DecidableEq Kind := VE.Paths.instDecidableEqKind
instance instBEqKind : BEq Kind := VE.Paths.instBEqKind
instance instReprKind : Repr Kind := VE.Paths.instReprKind
@[match_pattern] abbrev Kind.plus : Kind := VE.Paths.Kind.plus
@[match_pattern] abbrev Kind.star : Kind := VE.Paths.Kind.star
abbrev Reachable {α : Type u} (k : Kind) (R : α → α → Prop) (a b : α) : Prop := VE.Paths.Reachable k R a b

theorem star_least {α : Type u} {R : α → α → Prop} {a c : α} :
    Reachable .star R a c ↔ ∀ X : α → α → Prop,
      (∀ x, X x x) → (∀ x y z, R x y → X y z → X x z) → X a c := VE.Paths.star_least

abbrev dedup {α : Type u} [DecidableEq α] : List α → List α := VE.Paths.dedup

theorem mem_dedup {α : Type u} [DecidableEq α] (a : α) (xs : List α) :
    a ∈ dedup xs ↔ a ∈ xs := VE.Paths.mem_dedup a xs

abbrev pivot {α : Type u} [DecidableEq α] (v : α) (es : List (α × α)) : List (α × α) := VE.Paths.pivot v es

theorem mem_pivot {α : Type u} [DecidableEq α] (v a b : α) (es : List (α × α)) :
    (a, b) ∈ pivot v es ↔ (a, b) ∈ es ∨ (a, v) ∈ es ∧ (v, b) ∈ es := VE.Paths.mem_pivot v a b es

abbrev ClosedAt {α : Type u} (es : List (α × α)) (v : α) : Prop := VE.Paths.ClosedAt es v

theorem pivot_closed {α : Type u} [DecidableEq α] (es : List (α × α)) (v : α) :
    ClosedAt (pivot v es) v := VE.Paths.pivot_closed es v

theorem pivot_preserves_closed {α : Type u} [DecidableEq α]
    (es : List (α × α)) (v w : α) (h : ClosedAt es w) :
    ClosedAt (pivot v es) w := VE.Paths.pivot_preserves_closed es v w h

abbrev warshall {α : Type u} [DecidableEq α] : List α → List (α × α) → List (α × α) := VE.Paths.warshall

theorem warshall_extends {α : Type u} [DecidableEq α] (vs : List α)
    (es : List (α × α)) {a b : α} (h : (a, b) ∈ es) :
    (a, b) ∈ warshall vs es := VE.Paths.warshall_extends vs es h

theorem warshall_preserves_closed {α : Type u} [DecidableEq α] (vs : List α)
    (es : List (α × α)) (v : α) (h : ClosedAt es v) : ClosedAt (warshall vs es) v :=
  VE.Paths.warshall_preserves_closed vs es v h

theorem warshall_closed {α : Type u} [DecidableEq α] (vs : List α)
    (es : List (α × α)) {v : α} (h : v ∈ vs) : ClosedAt (warshall vs es) v :=
  VE.Paths.warshall_closed vs es h

theorem warshall_sound {α : Type u} [DecidableEq α] (vs : List α)
    (es : List (α × α)) (R : α → α → Prop)
    (h : ∀ a b, (a, b) ∈ es → Path R a b) :
    ∀ a b, (a, b) ∈ warshall vs es → Path R a b := VE.Paths.warshall_sound vs es R h

abbrev vertices {α : Type u} (es : List (α × α)) : List α := VE.Paths.vertices es

theorem warshall_iff_path {α : Type u} [DecidableEq α]
    (es : List (α × α)) (a b : α) :
    (a, b) ∈ warshall (dedup (vertices es)) es ↔ Path (fun x y => (x, y) ∈ es) a b :=
  VE.Paths.warshall_iff_path es a b

abbrev reachEval {α : Type u} [DecidableEq α] (k : Kind) (es : List (α × α)) (a b : α) : Bool :=
  VE.Paths.reachEval k es a b

theorem reachEval_iff {α : Type u} [DecidableEq α] (k : Kind)
    (es : List (α × α)) (a b : α) :
    reachEval k es a b = true ↔ Reachable k (fun x y => (x, y) ∈ es) a b :=
  VE.Paths.reachEval_iff k es a b

end VE.Core
