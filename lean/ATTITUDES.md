# `attitudes@0` in Lean (attitudes plan item AT-1)

Statement spec: [docs/spec/attitudes.md](../docs/spec/attitudes.md), draft 8 (at-0-finish); plan:
[docs/spec/attitudes-PLAN.md](../docs/spec/attitudes-PLAN.md), "AT-1. Lean core". The spec's Lean governs where it
and the plan's block differ (spec section 11). Sources are in `lean/VE/Attitudes/`, namespace `VE.Attitudes`, with
`open VE.Reports (Act)`, so every definition and theorem has the spec's name. The statement stub
`docs/spec/attitudes/SpecStubs_attitudes.lean` is read, never imported.

AT-1 is built in four merge-sized parts, in this order, on module seams: at-1a, at-1b, at-1c, at-1.

| File | Spec | Part | Contents |
|---|---|---|---|
| `Scale.lean` | 2.1, 6.1 `table_reviewed` | at-1a | `Word`, `Item`, `Scale`, `Scale.toOrder`, `Scale.atLeast` (QS-1's `Order.atLeast`), `Table`, `Table.words`, `Table.scale`, `Table.hasPair`, `Table.reviewed`, `e1Words`, the frozen `table`, `scaleCaps`; `table_reviewed` by `decide` |
| `Syntax.lean` | 2.2, 2.3, 2.4 | at-1a | `Mode`, `Mode.slug`, `Mode.words`, `Cond`, `AFormula`, `ARule`, `Lex`, `AttDoc` (with `lex` and `parts`), `AttDoc.scale`; `Key`, `Key.sorts`, `Cond.key`, `AFormula.conds`, `ruleContext`, `condsOf`, `partsOf`, `keys`, `name`, `keyOf`; `baseEnv`, `envAtt`, `baseEnvAtt` |
| `Examples.lean` | 7.1, 7.5 | at-1a, then each part | the fixtures F-AT0 to F-AT3, C-a's two conditions and C-e (`c_e_part`, `c_e_guard`), with a `#guard` on each value 2.1 to 2.4 compute; from at-1b the other fixtures of 7.1, one `#guard` per row of 5.2, 7.4's passes and 7.5's five |
| `Syntax.lean` (appended) | 2.5, 2.6 | at-1b | `atom`, `AFormula.toFormula`, `ARule.toNode`, `toNorms`, `partClaim`; `throwIf`, `mentionsSlot`, `lexPred`, `lexTerm`, `lexCovers`, `renderCheck` (D14a-d), `renderable`, `lexAgrees` (D6b), `checkCond`, `checkConds`, `checkParts`, `checkNames`, `checkAtt`, `WellFormedAtt`, `AWellFormed` |
| `Theorems.lean` | 6.1 `names_fresh`, `names_injective`, `keyOf_name`, `envAtt_extends`, `toNorms_wellFormed` | at-1b, then at-1 | the five statements that take `WellFormedAtt`, proved from `checkNames` and the `Nodup` check; at-1 adds the rest of 6.1 |
| `Frame.lean` | 2.7 | at-1c | `entailsMode`, `sameSubject`, `framePairs`, `closeOver`, `atomAt`, `knowsKeys`, `factive`, `entails`, `framePremises`, `frameLabels` |
| `Semantics.lean` | 2.8 | at-1c | `AttModel`, `contentAt`, `Intended`, `AFormula.denote`, `interp`, `restrict`, `seedClosure` |
| `Route.lean` | 2.9 (its first block) | at-1c | `toU`, `SettledAsX`, `UnsaidFree`, `attitudesPack`, `attitudesRow` (defined, registered by AT-3a), and AT-2's stand-in `labelOrigin`; the module spec 6.2 names for AT-2's statements, which import `VE.NormDefaults.Layered`; 2.9's `pointCheck` goes to `Packs.lean` (AT-2) |
| `Theorems.lean` (appended) | 6.1 `frame_wellFormed`, `frame_universalQF`, `frameLabels_nodup`, `framePairs_modes`, `framePairs_transitive`, `empty_relations_frame` | at-1c | proved from `checkAtt`'s condition and name checks; `table_reviewed` stays at-1a's, in `Scale.lean` |
| `Theorems.lean` (appended) | the other fifteen statements of 6.1 | at-1 | the semantic statements over 2.8 |

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
