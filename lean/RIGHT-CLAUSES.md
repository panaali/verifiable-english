# `right-clauses@0`: the Lean theorems in plain words

Spec: docs/spec/right-clauses.md (draft 3), section 8. Files: `lean/VE/RightClauses/{Tree,Plain,Relation,PlainWellFormed}.lean`, fixtures
in `Examples.lean`. `Wire.lean` (8.5) is cmp-s3b's. Nothing here imports `VE.Readings`.

A structured line is a rights line with clauses (base formulas with their source spans), at most one relation (a
declared binary base predicate between two of its slots, maybe total on the holder slot) and its elided spans.
`plain D` conjoins each line's clauses and relation atom to its guard and changes nothing else.

## Plain.lean (cmp-s3a)

- `plain_identity`: with no clause and no relation anywhere, `plain D` is the rights document itself.
- `plainContent_identity`: the same for a reading candidate's content.
- `plainContent_declared`: `plain` keeps a candidate's declared names, kind and needs, so the readings checks see
  the same names.
- `plain_shape`: every line instance keeps its right, kinds, rule name, predicate, bearer and holder slot.
- `plain_limPremises`: the limitation premises `Lim_D` are unchanged.
- `plain_guard`: a structured line's plain guard holds exactly where its own guard, every clause and the relation
  atom hold.
- `plain_wellFormed` (8.3): if the structured lines check and the rights document is well formed, `plain D` is well
  formed or its check reports a resource limit (a longer guard can exceed the AST budget). Proved in
  `PlainWellFormed.lean` (cmp-s3a-cfr-1) over the modules in `PlainWellFormed/`: `checkRights` reads the same
  document; the soft check of the correlated document, which passes for `D.doc`, passes or reports a resource limit
  for `plain D`; the identifier check reads the same names; and every formula the rights facts type still types,
  since the added conjuncts are base formulas typed in the line's context.
- `PlainWellFormed/Corollaries.lean`: `plain_wellFormedRights`, and `clauseSlot_labelled_of_doc`,
  `clause_fails_not_selected_of_doc`, `relation_some_bearer_of_doc`: Relation.lean's theorems with
  `WellFormedRights (plain D)` replaced by `WellFormedRights D.doc` and the hypothesis `hr` that
  `validateRights (plain D)` does not fail with a `ResourceLimit: ` error, the outcome 8.3 leaves open.

## Relation.lean (cmp-s3)

- `clauseSlot_eq`: the slot is `Lim_{plain D}` followed by `Rel_D`, one totality premise per total relation.
- `clauseSlot_no_total`: with no total relation the slot is `Lim_{plain D}`: the rights route on `plain D`.
- `clauseSlot_labelled`: if `Lim_D`'s labels are distinct, so are the slot's. Each totality premise has its own
  label `rights:relation:<rule>:total`, and none is a limitation label. The hypothesis is signed by the DRI
  (reviews/dri-decisions-20261104-cmp-s3.md Q3): `Lim_D`'s labels can repeat on a well-formed rights document
  (pk-1c's `cx`, rebuilt as `cxDoc` in Examples.lean).
- `clauseSlot_wellFormed` (8.4): not proved yet (cmp-s3b). It needs every base predicate that the base
  vocabulary shows to stay visible in the correlated document's stage-0 vocabulary. No lemma in the tree gives that.
- `clause_fails_not_selected`: where a clause or the relation fails at a tuple, the line does not select there, so
  no duty or liberty follows from it at that tuple.
- `relation_some_bearer`: under a total relation from the bearer slot to the holder slot, every holder in the
  holder sort who satisfies the right's holder guard has a related bearer. That bearer owes the act wherever the
  line's own guard holds and no narrowing mechanism is active.
