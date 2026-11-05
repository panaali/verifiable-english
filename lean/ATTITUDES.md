# `attitudes@0` in Lean (attitudes plan item AT-1)

Statement spec: [docs/spec/attitudes.md](../docs/spec/attitudes.md), draft 8 (at-0-finish); plan:
[docs/spec/attitudes-PLAN.md](../docs/spec/attitudes-PLAN.md), "AT-1. Lean core". The spec's Lean governs where it
and the plan's block differ (spec section 11). Sources are in `lean/VE/Attitudes/`, namespace `VE.Attitudes`, with
`open VE.Reports (Act)`, so every definition and theorem has the spec's name. The statement stub
`docs/spec/attitudes/SpecStubs_attitudes.lean` is read, never imported.

AT-1 is built in three merge-sized parts, in this order, on module seams.

| File | Spec | Part | Contents |
|---|---|---|---|
| `Scale.lean` | 2.1, 6.1 `table_reviewed` | at-1a | `Word`, `Item`, `Scale`, `Scale.toOrder`, `Scale.atLeast` (QS-1's `Order.atLeast`), `Table`, `Table.words`, `Table.scale`, `Table.hasPair`, `Table.reviewed`, `e1Words`, the frozen `table`, `scaleCaps`; `table_reviewed` by `decide` |
| `Syntax.lean` | 2.2, 2.3, 2.4 | at-1a | `Mode`, `Mode.slug`, `Mode.words`, `Cond`, `AFormula`, `ARule`, `Lex`, `AttDoc` (with `lex` and `parts`), `AttDoc.scale`; `Key`, `Key.sorts`, `Cond.key`, `AFormula.conds`, `ruleContext`, `condsOf`, `partsOf`, `keys`, `name`, `keyOf`; `baseEnv`, `envAtt`, `baseEnvAtt` |
| `Examples.lean` | 7.1, 7.5 | at-1a, then each part | the fixtures F-AT0 to F-AT3, C-a's two conditions and C-e (`c_e_part`, `c_e_guard`), with a `#guard` on each value 2.1 to 2.4 compute; from at-1b the other fixtures of 7.1, one `#guard` per row of 5.2, 7.4's passes and 7.5's five |
| `Syntax.lean` (appended) | 2.5, 2.6 | at-1b | `atom`, `AFormula.toFormula`, `ARule.toNode`, `toNorms`, `partClaim`; `throwIf`, `mentionsSlot`, `lexPred`, `lexTerm`, `lexCovers`, `renderCheck` (D14a-d), `renderable`, `lexAgrees` (D6b), `checkCond`, `checkConds`, `checkParts`, `checkNames`, `checkAtt`, `WellFormedAtt`, `AWellFormed` |
| `Theorems.lean` | 6.1 `names_fresh`, `names_injective`, `keyOf_name`, `envAtt_extends`, `toNorms_wellFormed` | at-1b, then at-1 | the five statements that take `WellFormedAtt`, proved from `checkNames` and the `Nodup` check; at-1 adds the rest of 6.1 |
| `Frame.lean`, `Semantics.lean` (and `Theorems.lean`, extended) | 2.7, 2.8, 2.9; the rest of 6.1 | at-1 | the frame, the semantics independent of the elaboration, the route views and the `attitudes` pack |

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
  AT-2's `keyOrigin`, `labelOrigin`; AT-3a's `decodeAttDoc`, `encodeElaboration`; AT-5's `renderCond`,
  `renderAssertedNotKnows`, `readCond`, `readGuard`, `readGuardAll`, `readRule`, `readRuleAll`, `refusalOf`.

No theorem uses an axiom beyond those `python3 lean/audit.py` allows.
