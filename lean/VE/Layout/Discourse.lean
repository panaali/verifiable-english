import VE.Discourse.WellFormed

/-! Discourse reads anchors through the layout's bodies (scope@0, docs/spec/scope.md 1.2 and 5.5). Its containment
    definitions and its anchor checks are the moved bodies of `VE/Layout/Anchors.lean`, on discourse's own unit
    spans, anchors, definition spans and environment (`discourse_*_unchanged`). -/

namespace VE.Layout

theorem discourse_within_unchanged (D : VE.Discourse.DDoc) (u a : String) :
    VE.Discourse.within D u a =
      within ((VE.Discourse.unitKeys D).map (fun k => (k.1, k.2.1, k.2.2.1))) D.K.anchors u a := by
  simp only [VE.Discourse.within, VE.Discourse.unitKeys, VE.Discourse.unitKey, List.map_map, Function.comp_def]

theorem discourse_innermost_unchanged (D : VE.Discourse.DDoc) (u : String) :
    VE.Discourse.innermostAnchor D u =
      innermostAnchor ((VE.Discourse.unitKeys D).map (fun k => (k.1, k.2.1, k.2.2.1))) D.K.anchors u := by
  simp only [VE.Discourse.innermostAnchor, VE.Discourse.unitKeys, VE.Discourse.unitKey, List.map_map,
    Function.comp_def]

/-- Discourse's anchor checks are the moved body, on discourse's own anchors, definition spans and environment. -/
theorem discourse_anchorsOk_unchanged (D : VE.Discourse.DDoc) :
    VE.Discourse.anchorsOk D = anchorsOk D.K.anchors
      ((D.base.units.filter (fun x => decide (x.kind = .definition))).map (fun x => (x.start, x.stop)))
      (VE.Discourse.unaryPred D.E) := rfl

end VE.Layout
