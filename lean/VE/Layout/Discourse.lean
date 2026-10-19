import VE.Discourse.WellFormed

/-! Discourse reads anchors through the layout's bodies (scope@0, docs/spec/scope.md 1.2 and 5.5). Its containment
    definitions and its anchor checks are the moved bodies of `VE/Layout/Anchors.lean`, on discourse's own unit
    spans, anchors, definition spans and environment (`discourse_*_unchanged`).

    `Before` restates the bodies discourse had before the move (main at 702ff7429), only so that `before_*` can
    prove the move changed no discourse answer, on every document. Nothing calls them. -/

namespace VE.Layout

theorem discourse_within_unchanged (D : VE.Discourse.DDoc) (u a : String) :
    VE.Discourse.within D u a =
      within ((VE.Discourse.unitKeys D).map (fun k => (k.1, k.2.1, k.2.2.1))) D.K.anchors u a := rfl

theorem discourse_innermost_unchanged (D : VE.Discourse.DDoc) (u : String) :
    VE.Discourse.innermostAnchor D u =
      innermostAnchor ((VE.Discourse.unitKeys D).map (fun k => (k.1, k.2.1, k.2.2.1))) D.K.anchors u := rfl

/-- Discourse's anchor checks are the moved body, on discourse's own anchors, definition spans and environment. -/
theorem discourse_anchorsOk_unchanged (D : VE.Discourse.DDoc) :
    VE.Discourse.anchorsOk D = anchorsOk D.K.anchors
      ((D.base.units.filter (fun x => decide (x.kind = .definition))).map (fun x => (x.start, x.stop)))
      (VE.Discourse.unaryPred D.E) := rfl

namespace Before
open VE.Discourse (DDoc Anchor unitKeys anchorOf unaryPred req runAll allOk dupOf spanIn spansDisjoint)

def unitSpan (D : DDoc) (u : String) : Option (Nat × Nat) :=
  ((unitKeys D).find? (·.1 == u)).map fun k => (k.2.1, k.2.2.1)

def within (D : DDoc) (unit anchor : String) : Bool :=
  match unitSpan D unit, anchorOf D anchor with
  | some (b, e), some a => a.span.1 ≤ b && e ≤ a.span.2
  | _, _ => false

def narrower (best : Option Anchor) (a : Anchor) : Option Anchor :=
  match best with
  | none => some a
  | some b => if a.span.2 - a.span.1 < b.span.2 - b.span.1 then some a else some b

def innermostAnchor (D : DDoc) (unit : String) : Option Anchor :=
  (D.K.anchors.filter fun a => within D unit a.id).foldl narrower none

def reachesRoot (D : DDoc) : Nat → Anchor → Bool
  | 0, _ => false
  | n + 1, a => match a.parent with
    | none => true
    | some p => match anchorOf D p with
      | some b => spanIn a.span b.span && reachesRoot D n b
      | none => false

def definitionIn (D : DDoc) (a : Anchor) : Bool :=
  D.base.units.any fun x => decide (x.kind = .definition) && spanIn (x.start, x.stop) a.span

def anchorsOk (D : DDoc) : Except String _root_.Unit := runAll [
  fun _ => req (D.K.anchors.length ≤ 1024) "ResourceLimit: anchors",
  fun _ => match dupOf (D.K.anchors.map Anchor.id) with
    | some a => .error ("DuplicateDeclaration: anchor " ++ a)
    | none => .ok (),
  fun _ => req ((D.K.anchors.filter (·.parent.isNone)).length == 1 || D.K.anchors.isEmpty)
    "InvalidInput: anchors must form one tree",
  fun _ => allOk D.K.anchors fun a => req (reachesRoot D (D.K.anchors.length + 1) a)
    ("DanglingAnchor: " ++ ((a.parent).getD a.id)),
  fun _ => allOk D.K.anchors fun a => allOk D.K.anchors fun b =>
    if a.id != b.id && a.parent == b.parent && a.parent.isSome then
      if a.label.toLower == b.label.toLower then .error ("DuplicateAnchor: " ++ a.label)
      else req (spansDisjoint a.span b.span) ("InvalidInput: anchors " ++ a.id ++ ", " ++ b.id ++ " overlap")
    else .ok (),
  fun _ => allOk D.K.anchors fun a => req (a.exports.all fun p => unaryPred D.E p && definitionIn D a)
    ("ManifestMismatch: anchors." ++ a.id ++ ".exports")]

end Before

theorem before_within (D : VE.Discourse.DDoc) (u a : String) : Before.within D u a = VE.Discourse.within D u a := by
  simp only [Before.within, Before.unitSpan, VE.Discourse.within, within, VE.Discourse.anchorOf, List.find?_map,
    Option.map_map]
  rfl

theorem before_innermost (D : VE.Discourse.DDoc) (u : String) :
    Before.innermostAnchor D u = VE.Discourse.innermostAnchor D u := by
  simp only [Before.innermostAnchor, before_within]
  rfl

theorem before_reachesRoot (D : VE.Discourse.DDoc) :
    ∀ n a, Before.reachesRoot D n a = reachesRoot D.K.anchors n a
  | 0, _ => rfl
  | n + 1, a => by simp only [Before.reachesRoot, reachesRoot, VE.Discourse.anchorOf, before_reachesRoot D n]; rfl

theorem before_anchorsOk (D : VE.Discourse.DDoc) : Before.anchorsOk D = VE.Discourse.anchorsOk D := by
  simp only [Before.anchorsOk, before_reachesRoot, Before.definitionIn, VE.Discourse.anchorsOk, anchorsOk,
    List.any_map, List.any_filter, Function.comp_def]
  rfl

end VE.Layout
