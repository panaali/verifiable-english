# ap-1bc delta: the words route decodes `acts@0` clauses

Base: `git merge-base HEAD main` (`110b3bf3a`). ap-1bc is part (1) of [ap-1bb](../ap-1bb/REPORT.md)'s section 6 for
batch AP-1 of [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) (section 4, "AP-1"); what it does not deliver is
named in [REPORT.md](REPORT.md) section 5.

**Everything else: no change.** `VE.Words.regulatedOf` reads `acts@0` only from a sorted unique list
(`actsProfiles`); for any other environment the profiles it passes are `[]`, `actsFixed [] _` is `[]`, and
`decodeRegulatedIn [] []` is the base's `decodeRegulated` (`decodeRegulated_without_acts`). The words route accepts
the same environments as the base (`Env.decode`, unchanged), so no profile list is newly admitted and `gate_acts`
holds as ap-1b proved it. [delta.py](delta.py) recorded the base's and this item's answers with each one's own pinned
service ([evidence/delta.json](evidence/delta.json)): 18 records, 6 identical (the control environment without
`acts@0`, and every refusing-side item), 12 changed, all row 1 (`--compare` exits 1 on any other difference, head
against head and on empty input). No theorem statement changed (`lean/statements.txt` is unchanged). Trust: K +0,
S +0, trusted +0 (`trust_map.py --check`), so there is no trust row.

## User-visible deltas

| # | Delta | Evidence and tests | Ruling |
|---|---|---|---|
| 1 | The words route (`ve.words`, the readings and norm-defaults English's situation, point, filling and pair lines) words an `acts@0` environment's regulated predicates with the declaration Lean's English decodes (`decodeRegulatedIn` with the environment's profiles and its `acts` block's fixed phrases, as `Env.decode`'s `modalForm`): a point or filling item on a plain act gives its wording (`Lexical.wording`, which the lexicon selects) at either value; one on a permission or obligation whose act is over today's 80 characters (up to 400 bytes), holds a declared fixed phrase or a U+2019 gives its act with `may`/`must`, `must not`/`need not`; a pair item on such an obligation gives its pair sentence. Base: `InvalidInput: words: the predicate heard is not regulated` (ap-1bb review F3), and `InvalidInput: words: must_hear is no obligation with a declared permission and at most two arguments of a sort` for the pair. A base predicate, and a pair on a plain act or a permission, are refused as before | `evidence/delta.json` (12 records `worded`: points and fillings on A1, A2 (plain), A3 (a permission whose `and` is inside a fixed phrase), an 81-character permission, and the pair of an obligation on A1); the guards of `lean/VE/Service/ActsExamples.lean` section "ap-1bc" (accepting: A1-A3, the 80, 81 and 400-byte acts, A19; refusing: without `acts@0`, an unsorted list, the block absent, one phrase missing or a refused phrase, a 401-byte act, a base predicate, a plain act's pair); `tests/test_acts_profile.py::test_the_words_route_words_acts_clauses_by_leans_decoder`, `::test_the_words_route_still_refuses_what_is_not_a_regulated_clause` (4); seeded bugs `regulatedOf-base-decoder`, `regulatedOf-acts-unread`, `regulatedOf-any-list`, `regulatedOf-block-unread` ([mutants.json](mutants.json)) | SIGNED by the DRI: `manage-agents/debates/plan-synthesis/SYNTHESIS.md` 2.2 and its table row "Profile-gate table in AR-10", with 4.2 and `DRI-DECISIONS-PHASE2.md` AP1, which schedule the plan's AP-1 row "the profile-aware decoders where `decodeRegulated` is called (spec finding F1, 4.1)" (as ap-1b's DELTA row 2 cites them: Lean's English reads every `acts@0` environment the environment mode accepts); `Words/Situation.lean` is such a caller, added after the tree F1 was measured on (`49de179e`) |
