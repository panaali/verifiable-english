# relb-f3-phrases: user-visible delta

Spare-capacity stream 1 (plain phrases, F3; reviews/SPARE-CAPACITY-TRACK-20261123.md in manage-agents), row
relb-f3-phrases. Sizing: reviews/relb-f1-sizing-20261121.md section F3.

**No existing output changes.** The item adds 48 rows to the finite idiom table (`IDIOMS` in
`ve/english_vocabulary.py` and its Lean copy `idioms1`/`idioms2` in `lean/VE/EnglishGrammar/Lexicon.lean`; 37
one-place, 11 two-place), one per yes/no predicate of the eligibility use case, and the data file
`usecases/eligibility/plain_wordings.json` (49 wordings: the 48 rows and "{0} is excluded", which has the
mechanical shape). An idiom row changes the lint only of a predicate whose declared wording is exactly that row.
No environment in the repository declares any of the 48 today: translation.py does not read the file yet (its
run.py, results.json, RESULTS.md and docs/kernel/ownership.json are held while relb-f1f2-eligibility waits to
merge), so no rendered line, diagnostic, verdict or limit of an existing input changes. The new behaviour: an
environment that declares one of these wordings gets it in place of 'is classified as "<name>"' / 'has the recorded
relation "<name>" to', and sentences in it read. Generated files regenerated: English grammar actions_version 49,
checker pin, declarations, kernel closure baseline (candidate paths readingsRoute, discourse, document +48 lines
each; kernel 9,738 before and after) and its table in docs/spec/kernel-boundary.md.

| # | Delta | Ruling | Evidence |
| --- | --- | --- | --- |
| 1 | Trust budget: **V +48** (K +0, S +0), measured with `uv run python tools/trust_map.py --check` on the final tree against its merge base with main: `VE/EnglishGrammar/Lexicon.lean` +48, rows of the existing definitions `idioms1` (+37) and `idioms2` (+11). No new trusted definition. | R16 (DRI-RULINGS.md): new Lean-owned behaviour (Lean's lexicon check V6 admits the 48 wordings), 48 lines, none in K; the changed definitions are exercised by tests that fail on a seeded change of a row (`docs/relb/f3-phrases/mutants.json`: PY1, PY2, LEAN1; 4 of 4 killed, `evidence/mutants-run.json`); the ties pass is asked for in `manage-agents/FOLLOW-UPS.md` ("## relb-f3-phrases", text in `evidence/follow-ups-row.md`). Recorded with `tools/trust_map.py --allow` (V 48 in `docs/trust-baseline.json`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), relb-f3-phrases, 2026-11-23") | `uv run python tools/trust_map.py --check` exit 0 |
