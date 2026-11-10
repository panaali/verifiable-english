# `attitudes@0` in Lean (attitudes plan item AT-1)

Statement spec: [docs/spec/attitudes.md](../docs/spec/attitudes.md), draft 8 (at-0-finish); plan:
[docs/spec/attitudes-PLAN.md](../docs/spec/attitudes-PLAN.md), "AT-1. Lean core". The spec's Lean governs where it
and the plan's block differ (spec section 11). Sources are in `lean/VE/Attitudes/`, namespace `VE.Attitudes`, with
`open VE.Reports (Act)`, so every definition and theorem has the spec's name. The statement stub
`docs/spec/attitudes/SpecStubs_attitudes.lean` is read, never imported.

AT-1 is built in five merge-sized parts, in this order, on module seams: at-1a, at-1b, at-1c, at-1d, at-1.

| File | Spec | Part | Contents |
|---|---|---|---|
| `Scale.lean` | 2.1, 6.1 `table_reviewed` | at-1a | `Word`, `Item`, `Scale`, `Scale.toOrder`, `Scale.atLeast` (QS-1's `Order.atLeast`), `Table`, `Table.words`, `Table.scale`, `Table.hasPair`, `Table.reviewed`, `e1Words`, the frozen `table`, `scaleCaps`; `table_reviewed` by `decide` |
| `Syntax.lean` | 2.2, 2.3, 2.4 | at-1a | `Mode`, `Mode.slug`, `Mode.words`, `Cond`, `AFormula`, `ARule`, `Lex`, `AttDoc` (with `lex` and `parts`), `AttDoc.scale`; `Key`, `Key.sorts`, `Cond.key`, `AFormula.conds`, `ruleContext`, `condsOf`, `partsOf`, `keys`, `name`, `keyOf`; `baseEnv`, `envAtt`, `baseEnvAtt` |
| `Examples.lean` | 7.1, 7.4, 7.5 | at-1a, then each part | the fixtures F-AT0 to F-AT3, C-a's two conditions and C-e (`c_e_part`, `c_e_guard`), with a `#guard` on each value 2.1 to 2.4 compute; from at-1b the other fixtures of 7.1, one `#guard` per row of 5.2, 7.4's passes and 7.5's five |
| `Syntax.lean` (appended) | 2.5, 2.6 | at-1b | `atom`, `AFormula.toFormula`, `ARule.toNode`, `toNorms`, `partClaim`; `throwIf`, `mentionsSlot`, `lexPred`, `lexTerm`, `lexCovers`, `renderCheck` (D14a-d), `renderable`, `lexAgrees` (D6b), `checkCond`, `checkConds`, `checkParts`, `checkNames`, `checkAtt`, `WellFormedAtt`, `AWellFormed` |
| `Theorems.lean` | 6.1 `names_fresh`, `names_injective`, `keyOf_name`, `envAtt_extends`, `toNorms_wellFormed` | at-1b, then at-1 | the five statements that take `WellFormedAtt`, proved from `checkNames` and the `Nodup` check; at-1c, at-1d and at-1 add the rest of 6.1 |
| `Frame.lean` | 2.7 | at-1c | `entailsMode`, `sameSubject`, `framePairs`, `closeOver`, `atomAt`, `knowsKeys`, `factive`, `entails`, `framePremises`, `frameLabels` |
| `Semantics.lean` | 2.8 | at-1c | `AttModel`, `contentAt`, `Intended`, `AFormula.denote`, `interp`, `restrict`, `seedClosure` |
| `Route.lean` | 2.9 (its first block) | at-1c | `toU`, `SettledAsX`, `UnsaidFree`, `attitudesPack`, `attitudesRow` (defined, registered by AT-3a), and AT-2's stand-in `labelOrigin`; the module spec 6.2 names for AT-2's statements, which import `VE.NormDefaults.Layered`; 2.9's `pointCheck` goes to `Packs.lean` (AT-2) |
| `Theorems.lean` (appended) | 6.1 `frame_wellFormed`, `frame_universalQF`, `frameLabels_nodup`, `framePairs_modes`, `framePairs_transitive`, `empty_relations_frame` | at-1c | proved from `checkAtt`'s condition and name checks; `table_reviewed` stays at-1a's, in `Scale.lean` |
| `Theorems.lean` (appended) | 6.1 `frame_iff_intended`, `knows_factive`, `seed_intended`, `seed_least`, `forced_iff_reachable`, `mistaken_belief_admissible`, `guard_collapse` | at-1d | the statements about `Intended`, `framePremises` and `seedClosure`; helper lemmas `closeOver_denote`, `atomAt_interp`, `contentAt_interp`, `denote_interp_base` (a formula over `baseEnv` means the same on `interp`) for at-1 to reuse; `Examples.lean` gains 7.4's and 7.5's points for each |
| `Theorems.lean` (appended) | 6.1 `old_formula_invariant`, `att_elaboration_faithful`, `interp_admissible`, `restrict_admissible`, `restrict_intended`, `interp_restrict`, `att_old_language_conservative`, `att_conservative_doc` | at-1 | elaboration, the model correspondence and conservativity; helper lemmas `denote_interp_of` (at-1d's `denote_interp_base` over any environment that declares no generated name), `keyOf_old`, `interp_name`, `envAtt_name`, `term_interp`, `denote_withRelation`, `tupleTyped_withRelation`. With these, every statement of 6.1 is proved. `AFormula.toFormula` is D[V] tied to `att_elaboration_faithful` (row at-1b-tie) |

## The statements of spec 6.1, in plain words

All 27 are proved (in `Theorems.lean`, `table_reviewed` in `Scale.lean`). "A well-formed document" is one `checkAtt` passes.

- `names_fresh`: in a well-formed document every key's generated name is undeclared by the document's environment, at most
  64 bytes long, and not the name of a regulated predicate or a definition.
- `names_injective`: two keys of a well-formed document with the same generated name are the same key.
- `keyOf_name`: reading a key's generated name back gives that key.
- `envAtt_extends`: a formula typed over the document's environment stays typed once the generated names are declared.
- `toNorms_wellFormed`: a well-formed document elaborates to a W1 document that W1's own check accepts.
- `frame_wellFormed`: every frame premise is typed over the base vocabulary with the generated names.
- `frame_universalQF`: every frame premise is universal and quantifier-free inside.
- `frameLabels_nodup`: there is one label per frame premise, and the labels are distinct.
- `framePairs_modes`: no frame pair starts at says, believes, wants or intends, and none ends at knows.
- `framePairs_transitive`: two frame pairs that chain give a third from the first key to the last.
- `att_elaboration_faithful`: an elaborated guard, read with the attitude relations as the generated predicates, means
  what the attitude guard means.
- `frame_iff_intended`: for typed relations over the document's keys, the frame premises hold exactly when the
  relations are intended (knowing is factive and every frame pair is respected).
- `interp_admissible`: an intended attitude model over an admissible structure gives an admissible structure over
  the extended environment.
- `restrict_admissible`: restricting an admissible structure over the extended environment (hiding the generated
  names) gives an admissible structure over the document's environment.
- `restrict_intended`: if such a structure also satisfies the frame, its restriction is an intended attitude model.
- `interp_restrict`: restricting and then reading back changes no relation.
- `old_formula_invariant`: a formula of the document's own vocabulary means the same whether or not the attitude
  relations are added.
- `empty_relations_frame`: with no attitude held, every frame premise holds, on any structure.
- `att_old_language_conservative`: from premises in the old vocabulary, adding the frame and the generated names proves
  no new conclusion in the old vocabulary, and loses none.
- `att_conservative_doc`: a document with no attitude condition and no reading-set part has no key, no frame, and the
  same environment.
- `knows_factive`: in every intended model, what is known is true.
- `seed_intended`: closing a typed seed (whose known contents are true) under the frame pairs gives an intended model.
- `seed_least`: every intended model holding the seed holds that whole closure.
- `forced_iff_reachable`: a seed forces an attitude exactly when frame pairs reach it from a seed member at the same
  tuple; nothing else is forced.
- `mistaken_belief_admissible`: any attitude other than knowing may be held of a false content.
- `guard_collapse`: when a frame pair links two conditions with the same holder and slot, `(ck ∧ a) ∨ ct` means `ct`.
- `table_reviewed`: the frozen table passes its closure review.

## Interfaces used, and stand-ins still in force

- QS-1's `VE.Closure.Order`, `Caps`, `Order.admit`, `Order.atLeast` (`lean/VE/Closure/Order.lean`): `Scale.atLeast`
  is `Order.atLeast`, no second closure (edit 1); `scaleCaps` is checked by `Order.admit`.
- `reports@0`'s `VE.Reports.Act`, `Act.name` (the four acts, `Mode.act`) and `VE.Reports.dedup` (one key per
  attitude, content identity by syntax-tree equality) from `lean/VE/Attribution/Content.lean`.
- The English grammar's `VE.EnglishGrammar.Env`, `Overlay`, `Lexicon` (`lean/VE/EnglishGrammar/Lexicon.lean`),
  carried as `AttDoc.lex`; read from at-1b on (D6a, D6b, D14d).
- `VE.Reports.wantsPhrase?` (`lean/VE/Attribution/Words.lean`, at-1w): merged, no stand-in; D14c (at-1b) calls it
  on the finite verb phrase, `w.stripPrefix "{0} "`, in both lines of `renderCheck`: the one difference from the spec's
  text (reviews/dri-decisions-20261105-at-1b.md item 1, in manage-agents), which the spec's next docs commit adopts.
- Stand-ins of the spec's section 0 still in force (their bodies are later batches' work, none read by at-1a):
  AT-2's `keyOrigin`, `labelOrigin` (from at-1c a definition in `Route.lean` answering the root path, since
  `attitudesPack` reads it and `lean/audit.py` refuses the stub's bodiless declaration; AT-2 writes the body); AT-3a's `decodeAttDoc`, `encodeElaboration`; AT-5's `renderCond`,
  `renderAssertedNotKnows`, `readCond`, `readGuard`, `readGuardAll`, `readRule`, `readRuleAll`, `refusalOf`.

No theorem uses an axiom beyond those `python3 lean/audit.py` allows.
