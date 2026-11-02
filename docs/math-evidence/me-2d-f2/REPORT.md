# me-2d-f2: the words "the" alone, and capital letters in reserved and phrase words (me-2d review F2, F3)

**Status:** built; ready for the chain's gate. **HEAD:** the commit that adds this report (branch `feature/me-2d-f2`).
**What changed:** the words "the" alone get `ValueWordsForm: the words of <name> must not be "the" alone` (F2, DELTA D1,
R1). Reserved and phrase words now match ignoring ASCII case, so "the x And y" and "the Sum of x" are refused (F3, D2,
signed by the DRI). Spec 11.2 and 13.1 say both. **Open:** none (no follow-on item). **DRI signature needed:** none
(D2 is signed in reviews/dri-decisions-20261102-me-2d-f2.md item 1; D3 is under R16, trusted +7).

## Deliverables (task file, in its order)

| # | Deliverable | Where | Evidence |
|---|---|---|---|
| 1 | `checkWords` refuses the words "the" alone with its own text; every other `ValueWordsForm` text is as on main | `lean/VE/Calc/Wire.lean:307` | guard "the-alone" (`lean/VE/Calc/RunExamples.lean:960`); the kept guards "the the" (`:953`, accepted), "theory", "The x", "the sum of" (`:958-959`, `:967`), unchanged |
| 1 | 13.1's row gets the new text beside the template; 11.2 says "begin with the word "the" followed by at least one more word" | `docs/spec/math-evidence.md:2078`, `:2780` | spec re-read below |
| 1 | Wire.lean re-pinned (lines 850, sha256, range, reason), and regenerated | `ve/assurance-manifest.json`; `uv run python tools/regen_generated.py --write` (rc 0, "wrote 35 entries") | `tests/test_assurance_manifest.py` in the selected run |
| 1 | DELTA row under R1 with a test over the saved old and new text | `DELTA.md` D1; `evidence/delta.json` | `tests/test_me_2d_f2_delta.py` (2 tests) |
| 2 | DRI asked first (`msg.sh dri me-2d-f2 ...`, 02:25Z); the DRI signed the refusal (02:27Z) | reviews/dri-decisions-20261102-me-2d-f2.md item 1 | n/a |
| 2 | `leadingPhrase` and `reservedIn` compare ASCII-lowercased words (new `lowerWords`) and quote the words as written; `valueWordsOk` reads both, so it is the same rule | `lean/VE/Calc/Render.lean:15-29` | refused guards "the x And y", "the x MINUS y" (`RunExamples.lean:984-985`), "the Sum of x", "Twice the x" (`:969-970`); accepted "the Andes", "the Summit" (`:953`); `valueWordsOk` guards (`lean/VE/Calc/Examples.lean:496-499`) |
| 2 | 11.2's sentence: reserved and phrase words match whatever their capital letters; the first "the" is lowercase | `docs/spec/math-evidence.md:2081-2082` | spec re-read below |
| 2 | Route and relay-gate cases checked for affected words | `grep` of `"words"` values in `tests/data/route-cases.jsonl` and `tests/data/relay-gate-cases.jsonl` for "the" alone and for a capitalised reserved or phrase word: no match | no case changes |
| 3 | Seeded bugs and one mutant (or more) per changed trusted definition | `mutants.json` (9 of 9 killed); `trust-mutants.json` (tools/trust_mutants.py) | below |

The synthesis round 2 edits (`debates/plan-synthesis-2/edits-math-evidence.md`): none of them names this item, and
this item implements none of them. No theorem statement is added or changed (`lean/statements.txt` unchanged against
the merge base; `python3 lean/audit.py`: "PASS: 721 source files; 7979 named theorem declarations audited").

## Seeded bugs (Lean; each planted alone, `lake build VE.Calc.RunExamples VE.Calc.Examples`, then restored)

`RunExamples.lean:955` is the words guards' `expect` block; under each bug only the rows named here change.

| Id | File | Definition | Bug | Fails |
|---|---|---|---|---|
| M1 | lean/VE/Calc/Wire.lean | `checkWords` | the "the" alone branch removed | `RunExamples.lean:955` (row "the-alone") |
| M2 | lean/VE/Calc/Wire.lean | `checkWords` | the branch fires on every word starting "the" | 38 RunExamples guards incl. `:955` |
| M3, M4 | lean/VE/Calc/Render.lean | `lowerWords` | identity; uppercasing | `Examples.lean:497`, `RunExamples.lean:955` (and 4 more Examples guards for M4) |
| M5 | lean/VE/Calc/Render.lean | `leadingPhrase` | exact matching | `Examples.lean:497`, `RunExamples.lean:955` (row "capital-phrase") |
| M6 | lean/VE/Calc/Render.lean | `leadingPhrase` | quotes the phrase lowercased | `RunExamples.lean:955` (row "capital-phrase") |
| M7 | lean/VE/Calc/Render.lean | `reservedIn` | exact matching (the task's seeded bug) | `Examples.lean:497`, `RunExamples.lean:955` (row "capital-and") |
| M8, M9 | lean/VE/Calc/Render.lean | `reservedIn` | quotes the word lowercased; the slice one character late | `RunExamples.lean:955` |

There is no Python or Rust product change. The new test can fail too: with the value's name dropped from the saved
head, `tests/test_me_2d_f2_delta.py::test_the_head_keeps_the_base_s_code_names_and_quoted_words` fails (restored).

Trust mutants (`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/math-evidence/me-2d-f2/trust-mutants-allow.json --rescore ... --json docs/math-evidence/me-2d-f2/trust-mutants.json`,
exit 0): `lowerWords`, `leadingPhrase`, `reservedIn`: 26 KILLED, 0 SURVIVOR, 0 UNKNOWN, 28 INVALID, 11 ALLOWED. The 11
allowed are `list-empty` mutants that do not elaborate (`[]` for a `String`, `Option String` or `Nat`), each listed in
`trust-mutants-allow.json`.

## Trust

`uv run python tools/trust_map.py --check` on the final Lean: K +0, S +0, D +1, G +7, trusted +7
(`lean/VE/Calc/Render.lean` +7: G[V] `lowerWords` new, in `tools/trust-classes.json`; `leadingPhrase`, `reservedIn`
changed). `Wire.lean` +1 is D[R], not trusted. Allowance recorded with `--allow`, "SIGNED by standing ruling R16
(DRI-RULINGS.md), me-2d-f2, 2026-11-02"; FOLLOW-UPS.md row "## me-2d-f2" asks for the ties pass.

## Tests

- Selected tests, once, on the finished code (`mac-pytest.sh --select -- --base f3a4da815 --run`): exit 0, 6 shards,
  447 units passed, 0 failed (`tests/test_calc_service.py`, `tests/test_assurance_manifest.py`,
  `tests/test_me_2d_f2_delta.py` among them). Nothing from main-known-red.txt failed.
- `lake build` (full): "Build completed successfully (1228 jobs)". The full gate was not run here: the chain runs it.

## Size, overlap, bytes

Hand-written lines (`git diff --numstat` against the merge base, generated files excluded): Lean +26 −9, spec +6 −4,
manifest +5 −5, trust classes +1, test +41, evidence and DELTA/REPORT/mutants docs on top. Overlap: of the branches in
flight, only `foundation/me-1` (last commit 2026-10-15, not merged) touches `Render.lean`, `Examples.lean` and the spec;
it is the branch that created them, and nothing in the SYNTHESIS 4.2 queue puts it ahead. Pilot bytes expected to move:
0 (no pilot sends these words; an estimate).

## Spec re-read

- "begin with the word "the" followed by at least one more word" against `docs/spec/math-evidence.md:2078` and
  `checkWords` (`w.startsWith "the "`; "the" alone refused first).
- The 13.1 row's new text against `Wire.lean:307`: `ValueWordsForm: the words of <name> must not be "the" alone`.
- "Reserved and phrase words match whatever their capital letters ... the refusal quotes the word as written; the
  first word "the" is lowercase" against the DRI decision item 1 and `Render.lean:15-29` (the first-word check stays
  exact, `startsWith "the "`).
- 3.1's value record (`:767`) names 11.2's rules by code only; it needs no change.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no response field or schema changes; the refusal is the existing `error` string (`tests/test_calc_service.py`).
2. PASS: every deliverable is in the table above; no Python copy of a Lean rule; the new test reads saved evidence plus Lean's live answer, no report numbers (`tests/test_me_2d_f2_delta.py`).
3. PASS: 9 seeded bugs killed (`mutants.json`); trust mutants exit 0 (`trust-mutants.json`); the R1 test fails on a dropped name (above).
4. PASS: base and head compared on the changed words (`evidence/delta.json`); every accepted word keeps "the x"'s rows and `meaning_id` (`RunExamples.lean:949-954`).
5. N.A.: no field Python reads is added or changed.
6. PASS: built on main f3a4da815; main has since moved to 3b4e471f8, whose changes to this branch's files are only generated files and ledgers (`docs/trust-baseline.json`, `tools/trust-classes.json`, `lean/declarations.txt`, five `docs/codemap` files), regenerated at the merge train's sync; the chain runs the gate on the final HEAD.
7. PASS: Ruling cells are R1, the DRI's decision file, R16 (`DELTA.md`).
8. PASS: both user-visible changes are DELTA rows D1 and D2; route and relay-gate cases checked, none affected.
9. PASS: the selected run included `tests/test_calc_service.py` and `tests/test_me_2d_f2_delta.py` (`/tmp` log above, 447 units).
10. N.A.: no theorem added or changed (`lean/statements.txt` unchanged; `python3 lean/audit.py` PASS).
11. N.A.: no budget, limit or deadline touched; the new test waits with `HANG_TIMEOUT`.
12. N.A.: `lowerWords` is one pass over at most 256 characters (W6's limit) per value.
13. N.A.: no test removed or renamed.
14. PASS: both directions tested (refused "the x And y", "the Sum of x"; accepted "the Andes", "the Summit"; refused "the", accepted "the the"); spec re-read above.
