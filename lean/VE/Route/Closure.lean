import VE.Closure.Finite
import VE.Core.Finite
import VE.Bridge

/-! Finite closures as Python and Rust build them, with their charges.

A closure is built once per edge and outer bindings (the closure cache): the
edges are a named relation's rows, or the body's true pairs over its sort;
then Warshall pivots over the edges' vertices materialize each pivot's incoming
and outgoing entities before adding their pairs. `warshallRun` charges that
work (one unit per entity per pivot, one per incoming × outgoing pair) and
builds the same hash set; `warshallH_iff` proves the set is exactly the finite
paths of the edges, so a closure value read from it is the reference value
(`reachValue_closure`, `reachValue_core`). -/
namespace VE.Route.Closure

abbrev Entity := VE.Bridge.Entity
abbrev Edges := Std.HashSet (Entity × Entity)

theorem contains_insert (es : Edges) (p q : Entity × Entity) :
    (es.insert p).contains q = true ↔ p = q ∨ es.contains q = true := by
  rw [Std.HashSet.contains_insert]
  simp

/-- Add (x, y) for every x in `xs` and y in `ys`. -/
def insertAll (xs ys : List Entity) (es : Edges) : Edges :=
  xs.foldl (fun es x => ys.foldl (fun es y => es.insert (x, y)) es) es

theorem contains_insertRow (x : Entity) : ∀ (ys : List Entity) (es : Edges) (a b : Entity),
    (ys.foldl (fun es y => es.insert (x, y)) es).contains (a, b) = true ↔
      es.contains (a, b) = true ∨ (a = x ∧ b ∈ ys)
  | [], es, a, b => by simp
  | y :: ys, es, a, b => by
    rw [List.foldl_cons, contains_insertRow x ys, contains_insert]
    simp only [Prod.mk.injEq, List.mem_cons]
    constructor
    · rintro ((⟨rfl, rfl⟩ | h) | ⟨rfl, h⟩)
      · exact .inr ⟨rfl, .inl rfl⟩
      · exact .inl h
      · exact .inr ⟨rfl, .inr h⟩
    · rintro (h | ⟨rfl, rfl | h⟩)
      · exact .inl (.inr h)
      · exact .inl (.inl ⟨rfl, rfl⟩)
      · exact .inr ⟨rfl, h⟩

theorem contains_insertAll (ys : List Entity) : ∀ (xs : List Entity) (es : Edges) (a b : Entity),
    (insertAll xs ys es).contains (a, b) = true ↔ es.contains (a, b) = true ∨ (a ∈ xs ∧ b ∈ ys)
  | [], es, a, b => by simp [insertAll]
  | x :: xs, es, a, b => by
    show (insertAll xs ys (ys.foldl (fun es y => es.insert (x, y)) es)).contains (a, b) = true ↔ _
    rw [contains_insertAll ys xs, contains_insertRow]
    simp only [List.mem_cons]
    constructor
    · rintro ((h | ⟨rfl, h⟩) | ⟨h, h'⟩)
      · exact .inl h
      · exact .inr ⟨.inl rfl, h⟩
      · exact .inr ⟨.inr h, h'⟩
    · rintro (h | ⟨rfl | h, h'⟩)
      · exact .inl (.inl h)
      · exact .inl (.inr ⟨rfl, h'⟩)
      · exact .inr ⟨h, h'⟩

/-! ## Warshall on a hash set -/

/-- One pivot over the vertices `D`. -/
def pivotH (D : List Entity) (v : Entity) (es : Edges) : Edges :=
  insertAll (D.filter fun x => es.contains (x, v)) (D.filter fun y => es.contains (v, y)) es

theorem contains_pivotH (D : List Entity) (v : Entity) (es : Edges) (a b : Entity) :
    (pivotH D v es).contains (a, b) = true ↔ es.contains (a, b) = true ∨
      (a ∈ D ∧ es.contains (a, v) = true ∧ b ∈ D ∧ es.contains (v, b) = true) := by
  rw [pivotH, contains_insertAll]
  simp only [List.mem_filter]
  constructor
  · rintro (h | ⟨⟨ha, hav⟩, ⟨hb, hvb⟩⟩)
    · exact .inl h
    · exact .inr ⟨ha, hav, hb, hvb⟩
  · rintro (h | ⟨ha, hav, hb, hvb⟩)
    · exact .inl h
    · exact .inr ⟨⟨ha, hav⟩, ⟨hb, hvb⟩⟩

def warshallH (D : List Entity) : List Entity → Edges → Edges
  | [], es => es
  | v :: vs, es => warshallH D vs (pivotH D v es)

/-- Every edge joins two vertices of `D`. -/
def Inside (D : List Entity) (es : Edges) : Prop :=
  ∀ a b, es.contains (a, b) = true → a ∈ D ∧ b ∈ D

def ClosedAt (es : Edges) (v : Entity) : Prop :=
  ∀ a b, es.contains (a, v) = true → es.contains (v, b) = true → es.contains (a, b) = true

theorem pivotH_inside {D : List Entity} {v : Entity} {es : Edges} (h : Inside D es) :
    Inside D (pivotH D v es) := by
  intro a b hab
  rcases (contains_pivotH D v es a b).mp hab with hab | ⟨ha, _, hb, _⟩
  · exact h a b hab
  · exact ⟨ha, hb⟩

theorem pivotH_extends {D : List Entity} {v : Entity} {es : Edges} {a b : Entity}
    (h : es.contains (a, b) = true) : (pivotH D v es).contains (a, b) = true :=
  (contains_pivotH D v es a b).mpr (.inl h)

theorem pivotH_closed {D : List Entity} {v : Entity} {es : Edges} (hin : Inside D es) :
    ClosedAt (pivotH D v es) v := by
  intro a b ha hb
  have ha' : es.contains (a, v) = true := by
    rcases (contains_pivotH D v es a v).mp ha with h | ⟨_, h, _, _⟩ <;> exact h
  have hb' : es.contains (v, b) = true := by
    rcases (contains_pivotH D v es v b).mp hb with h | ⟨_, _, _, h⟩ <;> exact h
  exact (contains_pivotH D v es a b).mpr
    (.inr ⟨(hin a v ha').1, ha', (hin v b hb').2, hb'⟩)

theorem pivotH_preserves {D : List Entity} {v w : Entity} {es : Edges} (hin : Inside D es)
    (h : ClosedAt es w) : ClosedAt (pivotH D v es) w := by
  intro a b ha hb
  rw [contains_pivotH] at ha hb ⊢
  rcases ha with haw | ⟨ha, hav, _, hvw⟩ <;> rcases hb with hwb | ⟨_, hwv, hb, hvb⟩
  · exact .inl (h a b haw hwb)
  · exact .inr ⟨(hin a w haw).1, h a v haw hwv, hb, hvb⟩
  · exact .inr ⟨ha, hav, (hin w b hwb).2, h v b hvw hwb⟩
  · exact .inr ⟨ha, hav, hb, hvb⟩

theorem warshallH_inside {D : List Entity} : ∀ (vs : List Entity) (es : Edges),
    Inside D es → Inside D (warshallH D vs es)
  | [], _, h => h
  | _ :: vs, _, h => warshallH_inside vs _ (pivotH_inside h)

theorem warshallH_extends {D : List Entity} : ∀ (vs : List Entity) (es : Edges) {a b : Entity},
    es.contains (a, b) = true → (warshallH D vs es).contains (a, b) = true
  | [], _, _, _, h => h
  | _ :: vs, _, _, _, h => warshallH_extends vs _ (pivotH_extends h)

theorem warshallH_preserves {D : List Entity} {w : Entity} : ∀ (vs : List Entity) (es : Edges),
    Inside D es → ClosedAt es w → ClosedAt (warshallH D vs es) w
  | [], _, _, h => h
  | _ :: vs, _, hin, h => warshallH_preserves vs _ (pivotH_inside hin) (pivotH_preserves hin h)

theorem warshallH_closed {D : List Entity} {v : Entity} : ∀ (vs : List Entity) (es : Edges),
    v ∈ vs → Inside D es → ClosedAt (warshallH D vs es) v
  | [], _, hv, _ => by cases hv
  | w :: ws, es, hv, hin => by
    rcases List.mem_cons.mp hv with rfl | hv
    · exact warshallH_preserves ws _ (pivotH_inside hin) (pivotH_closed hin)
    · exact warshallH_closed ws _ hv (pivotH_inside hin)

theorem warshallH_sound {D : List Entity} (R : Entity → Entity → Prop) :
    ∀ (vs : List Entity) (es : Edges), (∀ a b, es.contains (a, b) = true → VE.Closure.Path R a b) →
      ∀ a b, (warshallH D vs es).contains (a, b) = true → VE.Closure.Path R a b
  | [], _, h => h
  | v :: vs, es, h => by
    apply warshallH_sound R vs
    intro a b hab
    rcases (contains_pivotH D v es a b).mp hab with hab | ⟨_, hav, _, hvb⟩
    · exact h a b hab
    · exact (h a v hav).trans (h v b hvb)

/-- **Warshall over every vertex gives exactly the finite paths.** -/
theorem warshallH_iff {D : List Entity} (es : Edges) (hin : Inside D es) (vs : List Entity)
    (hvs : ∀ v ∈ D, v ∈ vs) (a b : Entity) :
    (warshallH D vs es).contains (a, b) = true ↔
      VE.Closure.Path (fun x y => es.contains (x, y) = true) a b := by
  constructor
  · exact warshallH_sound _ vs es (fun _ _ h => .edge h) a b
  · intro h
    induction h with
    | edge h => exact warshallH_extends vs es h
    | @cons a b c h _ ih =>
      exact warshallH_closed vs es (hvs b (hin a b h).2) hin a c (warshallH_extends vs es h) ih

/-- Warshall with Python's and Rust's charges: per pivot one unit per vertex,
then one per incoming × outgoing pair; `none` once the budget is exceeded. -/
def warshallRun (limit : Nat) (D : List Entity) : List Entity → Edges → Nat → Option (Edges × Nat)
  | [], es, w => some (es, w)
  | v :: vs, es, w =>
    let w := w + D.length
    if limit < w then none else
    let incoming := D.filter fun x => es.contains (x, v)
    let outgoing := D.filter fun y => es.contains (v, y)
    let w := w + incoming.length * outgoing.length
    if limit < w then none else
    warshallRun limit D vs (insertAll incoming outgoing es) w

theorem warshallRun_eq (limit : Nat) (D : List Entity) : ∀ (vs : List Entity) (es : Edges) (w : Nat)
    (c : Edges) (w' : Nat), warshallRun limit D vs es w = some (c, w') → c = warshallH D vs es
  | [], es, w, c, w', h => by
    simp only [warshallRun, Option.some.injEq, Prod.mk.injEq] at h
    exact h.1.symm
  | v :: vs, es, w, c, w', h => by
    simp only [warshallRun] at h
    split at h
    · cases h
    · split at h
      · cases h
      · exact warshallRun_eq limit D vs _ _ c w' h

/-! ## Edges -/

/-- A named relation's rows as edges. -/
def namedEdgesH (rows : List (List Entity)) : Edges :=
  rows.foldl (fun es row => match row with
    | [a, b] => es.insert (a, b)
    | _ => es) {}

theorem contains_namedEdges_go : ∀ (rows : List (List Entity)) (es : Edges) (a b : Entity),
    (rows.foldl (fun es row => match row with
      | [a, b] => es.insert (a, b)
      | _ => es) es).contains (a, b) = true ↔ es.contains (a, b) = true ∨ [a, b] ∈ rows
  | [], es, a, b => by simp
  | row :: rows, es, a, b => by
    rw [List.foldl_cons, contains_namedEdges_go rows]
    match row with
    | [x, y] =>
      simp only [contains_insert, Prod.mk.injEq, List.mem_cons, List.cons.injEq, and_true]
      constructor
      · rintro ((⟨rfl, rfl⟩ | h) | h)
        · exact .inr (.inl ⟨rfl, rfl⟩)
        · exact .inl h
        · exact .inr (.inr h)
      · rintro (h | ⟨rfl, rfl⟩ | h)
        · exact .inl (.inr h)
        · exact .inl (.inl ⟨rfl, rfl⟩)
        · exact .inr h
    | [] | [_] | _ :: _ :: _ :: _ =>
      simp only [List.mem_cons]
      constructor
      · rintro (h | h)
        · exact .inl h
        · exact .inr (.inr h)
      · rintro (h | h | h)
        · exact .inl h
        · simp at h
        · exact .inr h

theorem contains_namedEdgesH (rows : List (List Entity)) (a b : Entity) :
    (namedEdgesH rows).contains (a, b) = true ↔ [a, b] ∈ rows := by
  rw [namedEdgesH, contains_namedEdges_go]
  simp

/-- The endpoints of a named relation, in Python `sorted` and Rust index order
(one sort, so local-id order). -/
def endpointSet (rows : List (List Entity)) : Std.HashSet Entity :=
  rows.foldl (fun s row => match row with
    | [a, b] => (s.insert a).insert b
    | _ => s) {}

def endpoints (rows : List (List Entity)) : List Entity :=
  (endpointSet rows).toList.mergeSort fun a b => decide (a.2 < b.2) || (a.2 == b.2 && decide (a.1 ≤ b.1))

theorem endpointSet_go : ∀ (rows : List (List Entity)) (s : Std.HashSet Entity) (a b : Entity),
    [a, b] ∈ rows → (rows.foldl (fun s row => match row with
      | [a, b] => (s.insert a).insert b
      | _ => s) s).contains a = true ∧ (rows.foldl (fun s row => match row with
      | [a, b] => (s.insert a).insert b
      | _ => s) s).contains b = true
  | [], _, _, _, h => by cases h
  | row :: rows, s, a, b, h => by
    rw [List.foldl_cons]
    rcases List.mem_cons.mp h with rfl | h
    · have keep : ∀ (rows : List (List Entity)) (s : Std.HashSet Entity) (x : Entity),
          s.contains x = true → (rows.foldl (fun s row => match row with
            | [a, b] => (s.insert a).insert b
            | _ => s) s).contains x = true := by
        intro rows
        induction rows with
        | nil => intro s x h; exact h
        | cons r rs ih =>
          intro s x h
          rw [List.foldl_cons]
          apply ih
          match r with
          | [c, d] => simp [Std.HashSet.contains_insert, h]
          | [] | [_] | _ :: _ :: _ :: _ => exact h
      exact ⟨keep rows _ a (by simp [Std.HashSet.contains_insert]),
        keep rows _ b (by simp [Std.HashSet.contains_insert])⟩
    · exact endpointSet_go rows _ a b h

theorem namedEdgesH_inside (rows : List (List Entity)) :
    Inside (endpoints rows) (namedEdgesH rows) := by
  intro a b h
  have hr := (contains_namedEdgesH rows a b).mp h
  obtain ⟨ha, hb⟩ := endpointSet_go rows {} a b hr
  simp only [endpoints, List.mem_mergeSort, Std.HashSet.mem_toList]
  exact ⟨Std.HashSet.contains_iff_mem.mp ha, Std.HashSet.contains_iff_mem.mp hb⟩

/-- A named closure: one unit per row, then Warshall over its endpoints. -/
def namedClosure (limit : Nat) (rows : List (List Entity)) (w : Nat) : Option (Edges × Nat) :=
  let w := w + rows.length
  if limit < w then none else
  warshallRun limit (endpoints rows) (endpoints rows) (namedEdgesH rows) w

theorem path_congr {R Q : Entity → Entity → Prop} (h : ∀ x y, R x y ↔ Q x y) (a b : Entity) :
    VE.Closure.Path R a b ↔ VE.Closure.Path Q a b := by
  have : R = Q := funext fun x => funext fun y => propext (h x y)
  rw [this]

theorem namedClosure_spec (limit : Nat) (rows : List (List Entity)) (w : Nat) (c : Edges) (w' : Nat)
    (h : namedClosure limit rows w = some (c, w')) (a b : Entity) :
    c.contains (a, b) = true ↔ VE.Closure.Path (fun x y => [x, y] ∈ rows) a b := by
  unfold namedClosure at h
  simp only at h
  split at h
  · cases h
  · rw [warshallRun_eq _ _ _ _ _ _ _ h, warshallH_iff _ (namedEdgesH_inside rows) _ (fun _ h => h)]
    exact path_congr (fun x y => contains_namedEdgesH rows x y) a b

/-- The body at every (x, y) of its domain, x slowest, collecting the true
pairs and threading the evaluator's state. -/
def forPairs {σ : Type} (step : Entity → Entity → σ → Option (Bool × σ)) (domain : List Entity) :
    List Entity → Edges → σ → Option (Edges × σ)
  | [], es, s => some (es, s)
  | x :: xs, es, s => match row x domain es s with
    | none => none
    | some (es, s) => forPairs step domain xs es s
where
  row (x : Entity) : List Entity → Edges → σ → Option (Edges × σ)
    | [], es, s => some (es, s)
    | y :: ys, es, s => match step x y s with
      | none => none
      | some (b, s) => row x ys (if b then es.insert (x, y) else es) s

theorem forPairs_row_spec {σ : Type} (P : σ → Prop) (g : Entity → Entity → Bool)
    (step : Entity → Entity → σ → Option (Bool × σ))
    (hstep : ∀ x y s r, P s → step x y s = some r → r.1 = g x y ∧ P r.2) (domain : List Entity)
    (x : Entity) : ∀ (ys : List Entity) (es es' : Edges) (s s' : σ), P s →
      forPairs.row step x ys es s = some (es', s') →
      P s' ∧ ∀ a b, es'.contains (a, b) = true ↔
        es.contains (a, b) = true ∨ (a = x ∧ b ∈ ys ∧ g a b = true)
  | [], es, es', s, s', hs, h => by
    simp only [forPairs.row, Option.some.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    exact ⟨hs, fun a b => by simp⟩
  | y :: ys, es, es', s, s', hs, h => by
    simp only [forPairs.row] at h
    split at h
    · cases h
    · rename_i b s₁ hst
      obtain ⟨hb, hs₁⟩ := hstep x y s (b, s₁) hs hst
      obtain ⟨hs', hmem⟩ := forPairs_row_spec P g step hstep domain x ys _ es' s₁ s' hs₁ h
      refine ⟨hs', fun a c => ?_⟩
      rw [hmem]
      simp only [List.mem_cons]
      cases hbv : b
      · simp only [Bool.false_eq_true, ↓reduceIte]
        constructor
        · rintro (h | ⟨rfl, hc, hg⟩)
          · exact .inl h
          · exact .inr ⟨rfl, .inr hc, hg⟩
        · rintro (h | ⟨rfl, rfl | hc, hg⟩)
          · exact .inl h
          · rw [hbv] at hb; rw [← hb] at hg; cases hg
          · exact .inr ⟨rfl, hc, hg⟩
      · simp only [↓reduceIte, contains_insert, Prod.mk.injEq]
        constructor
        · rintro ((⟨rfl, rfl⟩ | h) | ⟨rfl, hc, hg⟩)
          · rw [hbv] at hb; exact .inr ⟨rfl, .inl rfl, hb.symm⟩
          · exact .inl h
          · exact .inr ⟨rfl, .inr hc, hg⟩
        · rintro (h | ⟨rfl, rfl | hc, hg⟩)
          · exact .inl (.inr h)
          · exact .inl (.inl ⟨rfl, rfl⟩)
          · exact .inr ⟨rfl, hc, hg⟩

theorem forPairs_spec {σ : Type} (P : σ → Prop) (g : Entity → Entity → Bool)
    (step : Entity → Entity → σ → Option (Bool × σ))
    (hstep : ∀ x y s r, P s → step x y s = some r → r.1 = g x y ∧ P r.2) (domain : List Entity) :
    ∀ (xs : List Entity) (es es' : Edges) (s s' : σ), P s → forPairs step domain xs es s = some (es', s') →
      P s' ∧ ∀ a b, es'.contains (a, b) = true ↔
        es.contains (a, b) = true ∨ (a ∈ xs ∧ b ∈ domain ∧ g a b = true)
  | [], es, es', s, s', hs, h => by
    simp only [forPairs, Option.some.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    exact ⟨hs, fun a b => by simp⟩
  | x :: xs, es, es', s, s', hs, h => by
    simp only [forPairs] at h
    split at h
    · cases h
    · rename_i es₁ s₁ hrow
      obtain ⟨hs₁, hmem₁⟩ := forPairs_row_spec P g step hstep domain x domain es es₁ s s₁ hs hrow
      obtain ⟨hs', hmem⟩ := forPairs_spec P g step hstep domain xs es₁ es' s₁ s' hs₁ h
      refine ⟨hs', fun a b => ?_⟩
      rw [hmem, hmem₁]
      simp only [List.mem_cons]
      constructor
      · rintro ((h | ⟨rfl, hb, hg⟩) | ⟨ha, hb, hg⟩)
        · exact .inl h
        · exact .inr ⟨.inl rfl, hb, hg⟩
        · exact .inr ⟨.inr ha, hb, hg⟩
      · rintro (h | ⟨rfl | ha, hb, hg⟩)
        · exact .inl (.inl h)
        · exact .inl (.inr ⟨rfl, hb, hg⟩)
        · exact .inr ⟨ha, hb, hg⟩

/-- A body closure's value set: Warshall over the whole domain from the pairs
`forPairs` collected. -/
theorem bodyClosure_spec (limit : Nat) (domain : List Entity) (g : Entity → Entity → Bool)
    (es : Edges) (hes : ∀ a b, es.contains (a, b) = true ↔ a ∈ domain ∧ b ∈ domain ∧ g a b = true)
    (w : Nat) (c : Edges) (w' : Nat) (h : warshallRun limit domain domain es w = some (c, w'))
    (a b : Entity) :
    c.contains (a, b) = true ↔
      VE.Closure.Path (fun x y => x ∈ domain ∧ y ∈ domain ∧ g x y = true) a b := by
  have hin : Inside domain es := fun a b h => ⟨((hes a b).mp h).1, ((hes a b).mp h).2.1⟩
  rw [warshallRun_eq _ _ _ _ _ _ _ h, warshallH_iff _ hin _ (fun _ h => h)]
  exact path_congr hes a b

/-! ## Values -/

/-- A reachability value from a closure: `star` also holds from an entity to itself. -/
def reachValue (star : Bool) (c : Edges) (l r : Option Entity) : Bool :=
  match l, r with
  | some v, some w => (star && decide (v = w)) || c.contains (v, w)
  | _, _ => false

theorem reachValue_closure (k : VE.Closure.Kind) (c : Edges) (es : List (Entity × Entity))
    (R : Entity → Entity → Prop) (hes : ∀ x y, (x, y) ∈ es ↔ R x y)
    (hc : ∀ a b, c.contains (a, b) = true ↔ VE.Closure.Path R a b) (v w : Entity) :
    reachValue (decide (k = .star)) c (some v) (some w) = VE.Closure.reachEval k es v w := by
  apply Bool.eq_iff_iff.mpr
  rw [VE.Closure.reachEval_iff, VE.Closure.reachable_congr k _ R hes]
  cases k <;> simp [reachValue, VE.Closure.Reachable, hc]

theorem path_core_iff (R : Entity → Entity → Prop) (a b : Entity) :
    VE.Core.Path R a b ↔ VE.Closure.Path R a b := by
  constructor
  · intro h
    induction h with
    | edge h => exact .edge h
    | cons h _ ih => exact .cons h ih
  · intro h
    induction h with
    | edge h => exact .edge h
    | cons h _ ih => exact .cons h ih

theorem reachValue_core (k : VE.Core.Kind) (c : Edges) (es : List (Entity × Entity))
    (R : Entity → Entity → Prop) (hes : ∀ x y, (x, y) ∈ es ↔ R x y)
    (hc : ∀ a b, c.contains (a, b) = true ↔ VE.Closure.Path R a b) (v w : Entity) :
    reachValue (decide (k = .star)) c (some v) (some w) = VE.Core.reachEval k es v w := by
  apply Bool.eq_iff_iff.mpr
  rw [VE.Core.reachEval_iff, VE.Core.reachable_congr k _ R hes]
  cases k <;> simp [reachValue, VE.Core.Reachable, hc, path_core_iff]

/-! ## The closure cache -/

/-- A closure's cache key without its bindings: Python `f.edge`, Rust `Edge`. -/
inductive EdgeKey (F : Type) where
  | named (relation : String)
  | body (sort : String) (formula : F)
  deriving DecidableEq, Hashable

/-- Work spent and the closures built so far, by edge and outer bindings. -/
structure Meter (F : Type) [DecidableEq F] [Hashable F] where
  work : Nat
  cache : Std.HashMap (EdgeKey F × List Entity) Edges

/-- Every cached closure is the finite paths of its key's edges. -/
def CacheOK {F : Type} [DecidableEq F] [Hashable F]
    (rel : EdgeKey F × List Entity → Entity → Entity → Prop) (s : Meter F) : Prop :=
  ∀ key c, s.cache[key]? = some c → ∀ a b, c.contains (a, b) = true ↔ VE.Closure.Path (rel key) a b

theorem cacheOK_insert {F : Type} [DecidableEq F] [Hashable F]
    {rel : EdgeKey F × List Entity → Entity → Entity → Prop} {s : Meter F} (hs : CacheOK rel s)
    (key : EdgeKey F × List Entity) (c : Edges)
    (hc : ∀ a b, c.contains (a, b) = true ↔ VE.Closure.Path (rel key) a b) (w : Nat) :
    CacheOK rel ⟨w, s.cache.insert key c⟩ := by
  intro key' c' h
  simp only [Std.HashMap.getElem?_insert] at h
  split at h
  · rename_i he
    have := eq_of_beq he
    subst this
    cases h
    exact hc
  · exact hs key' c' h

theorem cacheOK_empty {F : Type} [DecidableEq F] [Hashable F]
    (rel : EdgeKey F × List Entity → Entity → Entity → Prop) (w : Nat) :
    CacheOK rel (⟨w, {}⟩ : Meter F) := by
  intro key c h
  simp at h

end VE.Route.Closure
