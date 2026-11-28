# Word senses, version 1: how its bars were measured

`ve read` (ve/word_senses.py) was measured before it was merged, against bars fixed before any build code was written.

- `SCORING.md` is the scoring rule and the bars, copied unchanged from the set hashed before the build (its sha256 is
  pinned in tests/test_word_senses_bars.py). The file names it mentions are the measurement's own working files; the
  texts, keys and recorded answers they hold are in tests/data/word_senses_v1/.
- `seeded-bugs.json` lists bugs planted in ve/word_senses.py and the tests that failed on each.
- Five per-use branch keys (texts l03, l07, t13, t04 and c02) were made after the results were seen, by two fresh
  keyers who saw only the text, the question and the branch. They are not blind, and with the reader the bars for the
  word-on-two-kinds texts and for tiers B and C are met only with them.
- The scorer first used counted a branch "no answer" as safe, which SCORING.md does not; scored as SCORING.md is
  written, set 2 with the reader has 1 wrong text of 20 (g15), within its bar of 2.
- The rule "no answer from the split text when Lean could not check the text's consistency (X6)" was added after the
  first results; it only refuses more. With the word list alone it moved set 2 from 3 wrong texts of 20 to 0.
- Amended rule (ruling amendment of 2026-11-27T19:47Z, round 1127d): with no reader VE no longer answers both ways from
  the word list. It gives the answer `ve read` gave before word senses and adds one line, "Reading each word with one
  meaning throughout." The no-reader answers were measured again (the reader's answers did not change). With no reader:
  set 1 has 10 wrong texts of 10 and set 2 has 0 of 20. As the amendment reads the bars, these are reported as the
  known risk, not as bars. There are 0 needless questions in the 20 friction texts. The word-on-two-kinds texts are
  10 of 10 read with 0 wrong, and tiers B and C have 0 wrong, with the hashed keys alone.
