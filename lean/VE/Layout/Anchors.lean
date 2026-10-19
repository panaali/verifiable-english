import VE.Discourse.Manifest
import VE.Layout.List

/-! Anchors (scope@0, docs/spec/scope.md 1.2 and 4.1): which units an anchor holds, and the anchor checks. These are
    discourse's containment bodies and anchor checks, moved here so that one body serves discourse and scope:
    discourse's `within`, `narrower`, `innermostAnchor` and `anchorsOk` call them. -/

/-! ## The generic checks the anchor checks call (moved from `VE/Discourse/WellFormed.lean`, names unchanged) -/

namespace VE.Discourse

def req (b : Bool) (e : String) : Except String Unit := if b then .ok () else .error e

/-- Run the stages in order; the first failure is the diagnostic. -/
def runAll : List (Unit → Except String Unit) → Except String Unit
  | [] => .ok ()
  | f :: fs => match f () with
    | .ok _ => runAll fs
    | .error e => .error e

theorem runAll_ok : ∀ (fs : List (Unit → Except String Unit)), runAll fs = .ok () → ∀ f ∈ fs, f () = .ok ()
  | [], _, _, hf => nomatch hf
  | g :: gs, h, f, hf => by
    unfold runAll at h
    split at h
    · rename_i hg
      rcases List.mem_cons.mp hf with rfl | hf
      · exact hg
      · exact runAll_ok gs h f hf
    · cases h

def allOk {α : Type} (xs : List α) (f : α → Except String Unit) : Except String Unit :=
  runAll (xs.map fun x _ => f x)

theorem allOk_ok {α : Type} (xs : List α) (f : α → Except String Unit) (h : allOk xs f = .ok ()) :
    ∀ x ∈ xs, f x = .ok () := by
  intro x hx
  exact runAll_ok _ h _ (List.mem_map.mpr ⟨x, hx, rfl⟩)

theorem runAll_nil : runAll [] = .ok () := rfl

theorem runAll_cons (f : Unit → Except String Unit) (fs : List (Unit → Except String Unit)) :
    runAll (f :: fs) = .ok () ↔ f () = .ok () ∧ runAll fs = .ok () := by
  show (match f () with | .ok _ => runAll fs | .error e => .error e) = .ok () ↔ _
  cases h : f () with
  | ok v => simp
  | error e => simp

theorem req_ok (b : Bool) (e : String) : req b e = .ok () ↔ b = true := by
  unfold req; cases b <;> simp

theorem allOk_iff {α : Type} (xs : List α) (f : α → Except String Unit) :
    allOk xs f = .ok () ↔ ∀ x ∈ xs, f x = .ok () := by
  unfold allOk
  induction xs with
  | nil => simp [runAll]
  | cons x xs ih => simp [runAll_cons, ih]

def spanIn (inner outer : Nat × Nat) : Bool := outer.1 ≤ inner.1 && inner.2 ≤ outer.2
def spansDisjoint (a b : Nat × Nat) : Bool := a.2 ≤ b.1 || b.2 ≤ a.1

def dupOf : List String → Option String
  | [] => none
  | x :: xs => if xs.contains x then some x else dupOf xs

theorem dupOf_none : ∀ xs : List String, dupOf xs = none → xs.Nodup
  | [], _ => List.nodup_nil
  | x :: xs, h => by
    unfold dupOf at h
    split at h
    · cases h
    · rename_i hc
      exact List.nodup_cons.mpr ⟨by simpa using hc, dupOf_none xs h⟩

end VE.Discourse

namespace VE.Layout

/-! ## Containment: discourse's bodies, over `(unit spans, anchors)` -/

def spansOf (L : List Unit) : List (String × Nat × Nat) := L.map fun x => (x.id, x.span.1, x.span.2)

/-- The unit lies inside the anchor's span. -/
def within (spans : List (String × Nat × Nat)) (anchors : List VE.Discourse.Anchor) (unit anchor : String) : Bool :=
  match (spans.find? (·.1 == unit)).map (fun k => (k.2.1, k.2.2)), anchors.find? (·.id == anchor) with
  | some (b, e), some a => a.span.1 ≤ b && e ≤ a.span.2
  | _, _ => false

def narrower (best : Option VE.Discourse.Anchor) (a : VE.Discourse.Anchor) : Option VE.Discourse.Anchor :=
  match best with
  | none => some a
  | some b => if a.span.2 - a.span.1 < b.span.2 - b.span.1 then some a else some b

/-- The smallest anchor containing the unit (the first of equal size). -/
def innermostAnchor (spans : List (String × Nat × Nat)) (anchors : List VE.Discourse.Anchor) (unit : String) :
    Option VE.Discourse.Anchor :=
  (anchors.filter fun a => within spans anchors unit a.id).foldl narrower none

/-- An anchor's units: the layout units within it, in source order. The first is its heading. -/
def anchorUnits (L : List Unit) (anchors : List VE.Discourse.Anchor) (a : String) : List String :=
  (L.filter fun x => within (spansOf L) anchors x.id a).map (·.id)

def headingOf (L : List Unit) (anchors : List VE.Discourse.Anchor) (a : String) : Option String :=
  (anchorUnits L anchors a).head?

/-- The anchor reach: the anchor's units after its heading. -/
def anchorReach (L : List Unit) (anchors : List VE.Discourse.Anchor) (a : String) : Except String (List String) :=
  match anchorUnits L anchors a with
  | [] => .error s!"ScopeUnknownAnchor: {a}"
  | _ :: us => .ok us

/-! ## Discourse's anchor checks (its spec 4.1(2)), over `(anchors, definition spans, unary test)` -/

open VE.Discourse (req runAll allOk dupOf spanIn spansDisjoint)

/-- The anchor reaches the root through parents within the fuel. -/
def reachesRoot (anchors : List VE.Discourse.Anchor) : Nat → VE.Discourse.Anchor → Bool
  | 0, _ => false
  | n + 1, a => match a.parent with
    | none => true
    | some p => match anchors.find? (·.id == p) with
      | some b => spanIn a.span b.span && reachesRoot anchors n b
      | none => false

/-- One tree, nested and non-overlapping spans, unique labels per parent, exports. -/
def anchorsOk (anchors : List VE.Discourse.Anchor) (defSpans : List (Nat × Nat)) (unary : String → Bool) :
    Except String _root_.Unit := runAll [
  fun _ => req (anchors.length ≤ 1024) "ResourceLimit: anchors",
  fun _ => match dupOf (anchors.map VE.Discourse.Anchor.id) with
    | some a => .error ("DuplicateDeclaration: anchor " ++ a)
    | none => .ok (),
  fun _ => req ((anchors.filter (·.parent.isNone)).length == 1 || anchors.isEmpty)
    "InvalidInput: anchors must form one tree",
  fun _ => allOk anchors fun a => req (reachesRoot anchors (anchors.length + 1) a)
    ("DanglingAnchor: " ++ ((a.parent).getD a.id)),
  fun _ => allOk anchors fun a => allOk anchors fun b =>
    if a.id != b.id && a.parent == b.parent && a.parent.isSome then
      if a.label.toLower == b.label.toLower then .error ("DuplicateAnchor: " ++ a.label)
      else req (spansDisjoint a.span b.span) ("InvalidInput: anchors " ++ a.id ++ ", " ++ b.id ++ " overlap")
    else .ok (),
  fun _ => allOk anchors fun a => req (a.exports.all fun p => unary p && defSpans.any (spanIn · a.span))
    ("ManifestMismatch: anchors." ++ a.id ++ ".exports")]

/-! ## Theorems (spec 5.5) -/

theorem narrower_mem : ∀ (l : List VE.Discourse.Anchor) (best : Option VE.Discourse.Anchor) (a : VE.Discourse.Anchor),
    l.foldl narrower best = some a → best = some a ∨ a ∈ l
  | [], best, a, h => Or.inl h
  | x :: xs, best, a, h => by
    rcases narrower_mem xs (narrower best x) a h with h' | h'
    · unfold narrower at h'
      split at h'
      · cases h'; exact Or.inr List.mem_cons_self
      · split at h'
        · cases h'; exact Or.inr List.mem_cons_self
        · exact Or.inl h'
    · exact Or.inr (List.mem_cons_of_mem _ h')

theorem innermost_within {spans : List (String × Nat × Nat)} {anchors : List VE.Discourse.Anchor} {u : String}
    {a : VE.Discourse.Anchor} (h : innermostAnchor spans anchors u = some a) : within spans anchors u a.id = true := by
  unfold innermostAnchor at h
  rcases narrower_mem _ none a h with h | h
  · cases h
  · exact (List.mem_filter.mp h).2

theorem mem_anchorUnits (L : List Unit) (anchors : List VE.Discourse.Anchor) (a u : String) :
    u ∈ anchorUnits L anchors a ↔ u ∈ L.map (·.id) ∧ within (spansOf L) anchors u a = true := by
  simp only [anchorUnits, List.mem_map, List.mem_filter]
  constructor
  · rintro ⟨x, ⟨hx, hw⟩, rfl⟩; exact ⟨⟨x, hx, rfl⟩, hw⟩
  · rintro ⟨⟨x, hx, rfl⟩, hw⟩; exact ⟨x, ⟨hx, hw⟩, rfl⟩

theorem anchorReach_iff (L : List Unit) (hd : (L.map (·.id)).Nodup) (anchors : List VE.Discourse.Anchor)
    (a : String) (us : List String) (h : anchorReach L anchors a = .ok us) (u : String) :
    u ∈ us ↔ u ∈ L.map (·.id) ∧ within (spansOf L) anchors u a = true ∧ some u ≠ headingOf L anchors a := by
  have hn : (anchorUnits L anchors a).Nodup := (List.filter_sublist.map _).nodup (by simpa [List.map_map] using hd)
  unfold headingOf
  rw [← and_assoc, ← mem_anchorUnits]
  unfold anchorReach at h
  cases hu : anchorUnits L anchors a with
  | nil => simp [hu] at h
  | cons x xs =>
    simp only [hu, Except.ok.injEq] at h
    subst h
    rw [hu] at hn
    have hx : x ∉ xs := (List.nodup_cons.mp hn).1
    simp only [List.head?_cons, List.mem_cons, ne_eq, Option.some.injEq]
    constructor
    · intro hm; exact ⟨Or.inr hm, fun he => hx (he ▸ hm)⟩
    · rintro ⟨he | hm, hne⟩
      · exact absurd he hne
      · exact hm

end VE.Layout
