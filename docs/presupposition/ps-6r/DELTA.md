# ps-6r: user-visible delta

Feature item ps-6r (PS-6r of `docs/spec/presupposition-PLAN.md` at 30fcd8520, rank 24 of the feature feed, acting
DRI dri-featurefeed; slot by DRI-DECISIONS-PHASE2 "Presupposition phase 2" X1 (b)).

**No existing output changes.** The item adds four rows to the finite idiom table (`IDIOMS[2]` in
`ve/english_vocabulary.py` and its Lean copy `idioms2` in `lean/VE/EnglishGrammar/Lexicon.lean`):
"{0} is a core value of {1}", "{0} is a guideline of {1}", "{0} is a mission of {1}", "{0} is a nature of {1}".
An idiom row changes the lint only of a predicate whose declared wording is exactly that row (`template in IDIOMS[…]`
is the only read, in `ve/english.py` and in Lean's `acceptsDeclaredIn` and `negativeTemplate`; `negative_template`'s
past-verb branch does not apply to an "is" wording). No vocabulary, fixture, use case or corpus in the repository
declares any of the four (`git grep -E "is a (core value|guideline|mission|nature) of \{1\}"` finds only the two
tables). Declaring the four beside "{0} is human" leaves that wording, its negative and its lint unchanged
(`tests/test_presupposition_wordings.py::test_the_four_wordings_leave_human_unchanged`). So no diagnostic, rendered
line, verdict, fault order or limit of an existing input changes; the only new behaviour is the plan's: a document
that declares one of these four wordings gets it, in place of the quoted fallback "has the recorded relation …", and
its sentences parse. The one delta is the trust budget.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **V +4** (K +0, S +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main, 702ff7429: `VE/EnglishGrammar/Lexicon.lean` +4, the four rows of the existing definition `idioms2`. No new trusted definition. | SIGNED by standing ruling R16 (DRI-RULINGS.md): new Lean-owned behaviour (Lean's lexicon check V6 admits the four wordings), 4 lines, none in K; the changed definition `idioms2` is exercised by tests that fail on a seeded change of a row (`docs/presupposition/ps-6r/mutants.json` LEAN1-mission-row: 9 tests fail with V6, among them `tests/test_english_lean_tables.py::test_idiom_tables_equal_python`); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## ps-6r", text saved in `evidence/follow-ups-row.md`). Recorded with `tools/trust_map.py --allow` (V 4 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), ps-6r, 2026-10-18") | `uv run python tools/trust_map.py --check` exit 0 |
