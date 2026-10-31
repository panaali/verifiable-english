# `governSets_every_choice` as written has a counterexample (sc-5rd)

Statement (docs/spec/scope/SpecStubs_sc5r.lean, sc-5r's stub; spec 11.3):

    theorem governSets_every_choice (D : SDoc) (hw : Pinned.JsonWF D.doc) (hs : governedSetUnits D ≠ [])
        (out : Json) (ho : governSets D = .ok out) (cs : List VE.Discourse.Choice) (hcs : setChoices D = .ok cs)
        (ch : VE.Discourse.Choice) (hc : ch ∈ cs) :
        ∃ o, governChoice D ch = .ok o ∧ atChoiceOn (governedSetUnits D) out ch = o

The document (well formed: `jsonWF? D.doc = true`):

    {"units": [{"id": "a"}, 5, {}],
     "reading_sets": [{"id": "S", "version": 1, "readings": [{"id": "r", "content": "x"}]}]}

with the layout of `[("a", "Rules:\n"), ("", "- x\n")]` (`listRun … "a" = .ok [""]`) and one governor
`⟨"g", "a", .reguard ["top"], .list "a", [""]⟩`. Then `governedSetUnits D = [""]`, `setChoices D = .ok [[(S, 1, 0)]]`,
`governSets D` succeeds, and for the only choice:

    atChoiceOn su out ch = {"reading_sets":[],"units":[{"id":"a"},null,{"content":null}]}
    governChoice D ch    = {"reading_sets":[],"units":[{"id":"a"},null,{"content":"x"}]}

Why: the units `5` and `{}` both have the id `""` (`idOf` reads `""` when no string id is present). `assemble` writes
reading `r`'s content as `contentOf o "" `, the content of the *first* unit with that id in `govern`'s answer, which
is the non-object `5` (made `null` by `setObjVal!`), so `null`; under the choice, `govern` gives the object unit `{}`
the reading's content `"x"`. With every unit an object (or with distinct unit ids) the two agree. The route does not
exclude it: `checkDocSets` reaches `governSets` after `decodeScope` (`decodeBlock` checks only `jsonWF?` and the
block's parts).

Mechanised: `lean/VE/Scope/ReadingsExamples.lean`, `-- sc-5rd: governSets_every_choice's counterexample` (`#guard`).
