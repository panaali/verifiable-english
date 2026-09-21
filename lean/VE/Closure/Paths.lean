import VE.Finite

namespace VE.Closure
universe u

/-- Positive finite paths are THE definition of transitive closure, also on
infinite structures. A cycle can witness a positive path from a vertex to itself. -/
inductive Path {α : Type u} (R : α → α → Prop) : α → α → Prop where
  | edge {a b} : R a b → Path R a b
  | cons {a b c} : R a b → Path R b c → Path R a c

theorem Path.trans {α : Type u} {R : α → α → Prop} {a b c : α}
    (h : Path R a b) (g : Path R b c) : Path R a c := by
  induction h with
  | edge h => exact .cons h g
  | cons h _ ih => exact .cons h (ih g)

theorem Path.unfold {α : Type u} {R : α → α → Prop} {a c : α} :
    Path R a c ↔ R a c ∨ ∃ b, R a b ∧ Path R b c := by
  constructor
  · intro h; cases h with
    | edge h => exact .inl h
    | cons h p => exact .inr ⟨_, h, p⟩
  · rintro (h | ⟨b, h, p⟩)
    · exact .edge h
    · exact .cons h p

/-- Intersection of all pre-fixed points of X ↦ R ∪ R;X. -/
theorem Path.least {α : Type u} {R : α → α → Prop} {a c : α} :
    Path R a c ↔ ∀ X : α → α → Prop,
      (∀ x y, R x y → X x y) →
      (∀ x y z, R x y → X y z → X x z) → X a c := by
  constructor
  · intro h X he hc
    induction h with
    | edge h => exact he _ _ h
    | cons h _ ih => exact hc _ _ _ h ih
  · intro h
    exact h (Path R) (fun _ _ => Path.edge) (fun _ _ _ => Path.cons)

inductive Kind where
  | plus | star
  deriving DecidableEq, BEq, Repr

def Reachable {α : Type u} (k : Kind) (R : α → α → Prop) (a b : α) : Prop :=
  match k with
  | .plus => Path R a b
  | .star => a = b ∨ Path R a b

theorem star_least {α : Type u} {R : α → α → Prop} {a c : α} :
    Reachable .star R a c ↔ ∀ X : α → α → Prop,
      (∀ x, X x x) → (∀ x y z, R x y → X y z → X x z) → X a c := by
  constructor
  · rintro (rfl | h) X hi hc
    · exact hi _
    · induction h with
      | edge h => exact hc _ _ _ h (hi _)
      | cons h _ ih => exact hc _ _ _ h ih
  · intro h
    apply h (Reachable .star R)
    · intro x; exact .inl rfl
    · rintro x y z h (rfl | p)
      · exact .inr (.edge h)
      · exact .inr (.cons h p)

def dedup {α : Type u} [DecidableEq α] : List α → List α
  | [] => []
  | a :: xs => let rest := dedup xs; if a ∈ rest then rest else a :: rest

theorem mem_dedup {α : Type u} [DecidableEq α] (a : α) (xs : List α) :
    a ∈ dedup xs ↔ a ∈ xs := by
  induction xs generalizing a with
  | nil => simp [dedup]
  | cons b xs ih => simp only [dedup]; split <;> simp_all

/-- One finite Warshall pivot. Materialized edge tables are deduplicated. -/
def pivot {α : Type u} [DecidableEq α] (v : α) (es : List (α × α)) : List (α × α) :=
  dedup (es ++ es.flatMap (fun ab =>
    if ab.2 = v then es.filterMap (fun cd =>
      if cd.1 = v then some (ab.1, cd.2) else none) else []))

theorem mem_pivot {α : Type u} [DecidableEq α] (v a b : α) (es : List (α × α)) :
    (a, b) ∈ pivot v es ↔ (a, b) ∈ es ∨ (a, v) ∈ es ∧ (v, b) ∈ es := by
  simp only [pivot, mem_dedup, List.mem_append, List.mem_flatMap]
  constructor
  · rintro (h | ⟨⟨x, y⟩, hxy, h⟩)
    · exact .inl h
    · split at h
      next hy =>
        obtain ⟨⟨z, w⟩, hzw, he⟩ := List.mem_filterMap.mp h
        split at he
        next hz =>
          simp only [Option.some.injEq, Prod.mk.injEq] at he
          rcases he with ⟨rfl, rfl⟩
          change y = v at hy
          change z = v at hz
          subst y; subst z
          exact .inr ⟨hxy, hzw⟩
        next => simp at he
      next => simp at h
  · rintro (h | ⟨ha, hb⟩)
    · exact .inl h
    · apply Or.inr
      refine ⟨(a, v), ha, ?_⟩
      dsimp
      rw [if_pos rfl]
      apply List.mem_filterMap.mpr
      exact ⟨(v, b), hb, by simp⟩

def ClosedAt {α : Type u} (es : List (α × α)) (v : α) : Prop :=
  ∀ a b, (a, v) ∈ es → (v, b) ∈ es → (a, b) ∈ es

theorem pivot_closed {α : Type u} [DecidableEq α] (es : List (α × α)) (v : α) :
    ClosedAt (pivot v es) v := by
  intro a b ha hb
  rw [mem_pivot] at ha hb ⊢
  rcases ha with ha | ⟨ha, _⟩ <;> rcases hb with hb | ⟨_, hb⟩ <;>
    exact .inr ⟨ha, hb⟩

theorem pivot_preserves_closed {α : Type u} [DecidableEq α]
    (es : List (α × α)) (v w : α) (h : ClosedAt es w) :
    ClosedAt (pivot v es) w := by
  intro a b ha hb
  rw [mem_pivot] at ha hb ⊢
  rcases ha with ha | ⟨hav, hvw⟩ <;> rcases hb with hb | ⟨hwv, hvb⟩
  · exact .inl (h _ _ ha hb)
  · exact .inr ⟨h _ _ ha hwv, hvb⟩
  · exact .inr ⟨hav, h _ _ hvw hb⟩
  · exact .inr ⟨hav, hvb⟩

def warshall {α : Type u} [DecidableEq α] : List α → List (α × α) → List (α × α)
  | [], es => es
  | v :: vs, es => warshall vs (pivot v es)

theorem warshall_extends {α : Type u} [DecidableEq α] (vs : List α)
    (es : List (α × α)) {a b : α} (h : (a, b) ∈ es) :
    (a, b) ∈ warshall vs es := by
  induction vs generalizing es with
  | nil => exact h
  | cons v vs ih => exact ih _ ((mem_pivot v a b es).mpr (.inl h))

theorem warshall_preserves_closed {α : Type u} [DecidableEq α] (vs : List α)
    (es : List (α × α)) (v : α) (h : ClosedAt es v) : ClosedAt (warshall vs es) v := by
  induction vs generalizing es with
  | nil => exact h
  | cons w ws ih => exact ih _ (pivot_preserves_closed es w v h)

theorem warshall_closed {α : Type u} [DecidableEq α] (vs : List α)
    (es : List (α × α)) {v : α} (h : v ∈ vs) : ClosedAt (warshall vs es) v := by
  induction vs generalizing es with
  | nil => simp at h
  | cons w ws ih =>
    rcases List.mem_cons.mp h with rfl | h
    · exact warshall_preserves_closed ws _ _ (pivot_closed es v)
    · exact ih _ h

theorem warshall_sound {α : Type u} [DecidableEq α] (vs : List α)
    (es : List (α × α)) (R : α → α → Prop)
    (h : ∀ a b, (a, b) ∈ es → Path R a b) :
    ∀ a b, (a, b) ∈ warshall vs es → Path R a b := by
  induction vs generalizing es with
  | nil => exact h
  | cons v vs ih =>
    apply ih
    intro a b hab
    rcases (mem_pivot v a b es).mp hab with hab | ⟨ha, hb⟩
    · exact h _ _ hab
    · exact (h _ _ ha).trans (h _ _ hb)

def vertices {α : Type u} (es : List (α × α)) : List α :=
  es.flatMap (fun ab => [ab.1, ab.2])

theorem warshall_iff_path {α : Type u} [DecidableEq α]
    (es : List (α × α)) (a b : α) :
    (a, b) ∈ warshall (vertices es) es ↔ Path (fun x y => (x, y) ∈ es) a b := by
  constructor
  · exact warshall_sound _ _ _ (fun _ _ h => .edge h) _ _
  · intro h
    induction h with
    | edge h => exact warshall_extends _ _ h
    | @cons a b c h _ ih =>
      have hb : b ∈ vertices es := List.mem_flatMap.mpr ⟨(a, b), h, by simp⟩
      exact warshall_closed _ _ hb _ _ (warshall_extends _ _ h) ih

def reachEval {α : Type u} [DecidableEq α] (k : Kind) (es : List (α × α))
    (a b : α) : Bool :=
  (decide (k = .star) && decide (a = b)) || decide ((a, b) ∈ warshall (vertices es) es)

theorem reachEval_iff {α : Type u} [DecidableEq α] (k : Kind)
    (es : List (α × α)) (a b : α) :
    reachEval k es a b = true ↔ Reachable k (fun x y => (x, y) ∈ es) a b := by
  cases k <;> simp [reachEval, Reachable, warshall_iff_path]

end VE.Closure
