# relb-f3-tense-wordings: user-visible delta

Row relb-f3-tense-wordings (wording-only follow-up of relb-f3-eligibility-files, merged at main 0ab01dfe84; found
by the Opus review of that item).

**What changes.** Three plain wordings of the eligibility use case said that something had ended, but their
predicates only say that an end date is recorded, and that date may fall after the qualifying week
(translation.py legends: "The person's care stay has a last day, the care end date"; "... has a last day, the
household's home end date / partnership end date"). Rule R5b read "it is not the case that applicant has left care;
or 2026-09-27 is no later than the applicant's care end date", which contradicts itself when the date is later.

| predicate | before | after |
| --- | --- | --- |
| care_ended | {0} has left care | {0} has a care end date |
| home_ended | {0} stopped sharing a home with {1} | {0} has an end date for sharing a home with {1} |
| partnership_ended | {0} ended a partnership with {1} | {0} has a partnership end date with {1} |

The three new wordings replace the three old rows of the finite idiom table (`IDIOMS` in `ve/english_vocabulary.py`
and its Lean copy `idioms1`/`idioms2` in `lean/VE/EnglishGrammar/Lexicon.lean`). Nothing else in the repository used
the old rows (only the saved evidence of relb-f3-phrases, `docs/relb/f3-phrases/`, which records that item's run and
is left as it was). Rendered output that moves: the eligibility fact and rule sentences that use these three
predicates (results.json `english`: 19 of its 244 fact and rule rows reworded, nothing else in it), the eligibility environment id (0b02fe6f39 -> 1b723c5ec1), the
English lexicon report and corpus seal (they hash that environment), the grammar actions_version 49 -> 50 (and the
S3 fixture comparison that records it), checker pins and lean/declarations.txt. **No answer changes**: 86 profiles,
430 of 430 answers identical before and after (ANSWERS_DIGEST unchanged); mutants 34/34 unchanged. RESULTS.md and
docs/kernel/ownership.json are unchanged (neither holds these sentences or an input this item changes).

Seeded bugs (evidence `mutants-run.json`, 4 of 4 killed): a Lean row differing from the Python one
(tests/test_english_lean_tables.py), a Python row missing (the legend falls back), a past-tense wording declared
again, a past-tense sentence recorded again (tests/test_eligibility_wfp.py).

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **K +0, S +0, V +0** (trusted +0), measured with `uv run python tools/trust_map.py --check` on the final tree: `VE/EnglishGrammar/Lexicon.lean` 3 rows of the existing definitions `idioms1` (1) and `idioms2` (2) replaced (+3 -3 lines); `VE/EnglishGrammar/Fixed/Version.lean` (generated) actions_version 49 -> 50 (+1 -1). No new trusted definition. | R16 (DRI-RULINGS.md): Lean-owned behaviour (Lean's lexicon check V6 admits the three wordings), 3 changed lines, none in K; the changed rows are exercised by tests that fail on a seeded change (`mutants-run.json` LEAN1, PY1); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## relb-f3-tense-wordings"). | `uv run python tools/trust_map.py --check` exit 0 |
