# Q1.4b report: `Is <Name> …?` read by Lean's question reader through the speech caller

**Status:** done; no DRI signature is reserved. The 19 verdict rows are signed by the DRI
(reviews/dri-decisions-20261027-featureplan-gates.md item 4); every other DELTA row cites R1 or R2. Branch head: the
commit that adds this report, on merge base `de7cb4022`. Changed: `parse_speech` sends every wording that begins with
`Is ` to Lean's `english.question` with caller `speech-acts`, and the `Is <Name>` branch (Python's `_copular` used for
polar questions) is deleted. Python only; no Lean change, no theorem statement added or changed. Open: FOLLOW-UP q1-4bb (below).

## Plan rows delivered

| Plan / directive line | Delivered by | Test |
|---|---|---|
| Plan Q1.4 (question-answering-PLAN.md 6.4 table): "`speech_english.py`'s polar branches …, the polar use of `_copular` … are **deleted**; Python relays. `_copular` stays for which-questions and `follows`" | `ve/speech_english.py`: `"Is "` joins `_LEAN_PREFIXES`; the `Is <Name>` branch is deleted; `_copular` is left for `_sentence` (follows, prove) and `_body` (which) | `test_an_f2_wording_is_sent`, `test_a_wording_without_a_routed_prefix_is_not_sent` |
| DRI item 4 (a): a gloss question gets Lean's refusal text | the routing above | `test_a_gloss_question_gets_leans_refusal_text` (accepting side: `test_a_gloss_leans_lexicon_reads_is_read`, `test_a_gloss_outside_the_environment_is_refused`) |
| DRI item 4 (b): a case-folded name is refused | the routing above | `test_a_case_folded_name_is_refused` (`ATLAS`, `aTLAS`, `ATlas`, `BEACON`; accepting side: `test_a_name_as_declared_or_capitalised_is_read`, `atlas`, `Atlas`, `Beacon`) |
| DRI item 4 (c): `Is every service reviewed?` gets the same verdict and text through the speech caller as through `ve ask` | the routing above | `test_a_quantified_f2_question_is_read_as_ve_ask_reads_it` (runs `ve ask DOC Q --reading` and `--json` on a document in the speech environment; `every`, `some`, and the refusing side `Is a service reviewed?` with its two rephrasings) |
| DELTA: each changed answer or refusal is a row signed by item 4, with its condition test | [DELTA.md](DELTA.md) V1-V19, one row per changed verdict record | `evidence/speech_ab_f2.py check evidence/delta.json` |
| "Bytes 0" | no pilot document asks an `Is <Name> …?` speech question (`conformance/`, `usecases/`: none) | expected pilot bytes moved: 0 (an estimate) |

All 19 verdict rows change exactly as the decision lists them: 10 gloss (`glossed` 8, `f0-*` `Is tom a cat?` 2), 3
case-folded (`Is ATLAS reviewed?` under `speech`, `glossed`, `f0-reviewed`), and 6 every/some (`Is every/some service
reviewed?` under `speech`, `glossed`, `f0-reviewed`). The saved delta is byte-identical to Q1.4's `write-f2` preview
recorded against this base.

## What changed for users (summary of [DELTA.md](DELTA.md))

- 19 verdicts (above), signed by item 4.
- 140 wording rows (R1, R2's O1): the base's text for an `Is <…>?` with no matching gloss was
  `The character at position 0 cannot appear outside a quoted name.` Python's fallback lexed `@<name> <rest>.`, so
  that position belonged to an `@` the writer never typed. The head gives Lean's text over the question itself (the
  closest sentence tried, the unknown phrase, the true position).
- 79 class rows (R1, R3 for the added spans): `InvalidInput: no single speech-act reading` and
  `UnknownAlternative: wording, <word>` become Lean's `SyntaxError`/`TypeMismatch` with a span, keeping the base's
  word.
- The `OpaqueWording` lint now appears on `Which one of …` and query targets only. A polar question that matched a
  gloss is now refused, so it carries no lint. The gloss directive's test asks its glosses as `Which one of …`.

## Seeded bugs (Python, `ve/speech_english.py`; [mutants.json](mutants.json))

| Mutant | Behaviour | Failing test |
|---|---|---|
| M1: the `Is <Name>` branch left in, before the routing | class (a) | `test_a_gloss_question_gets_leans_refusal_text` (3 failed) |
| M2: case folding kept (the name replaced by `_name`'s folded constant before routing) | class (b) | `test_a_case_folded_name_is_refused` (4 failed) |
| M3: `"Is "` dropped from `_LEAN_PREFIXES` | class (c), routing | `test_a_quantified_f2_question_is_read_as_ve_ask_reads_it` (3 failed) |
| C1: the delta checker given q1-4's delta, a row with head text `x`, and head against head | evidence | `speech_ab_f2.py check` exits 1 on each, 0 on the saved delta |

Each was planted alone, shown failing, and restored; the tree was clean afterwards. No Lean or Rust product code
changed, so there are no seeded bugs in those languages.

## Trust and tests

- Trust: `tools/trust_map.py --check` PASS, K +0, S +0, D +0, G +0, trusted +0. No allowance, no R16 row, no trust
  mutants (no trusted Lean changed).
- Selected tests on the final code, before this report (`mac-pytest.sh --select -- --base de7cb4022 --run`, HEAD
  `acf66cbb`): 158 units, 0 failed. Before that, the 6 speech files (313 tests), then `tests/test_speech_polar_lean.py`
  (145 passed).
- `tools/gate_collection.py --check --prebuilt`: 34 added, 4 removed by a trailer, 0 refused, 0 stale, 0 malformed. The
  `Test-removed:` trailer is on commit `be68ad37`, which renamed the F1-prefix boundary test to the `Is ` boundary test
  and added the sent side.
- Not run: the full gate. The chain runs it on the final HEAD.
- Size: about 220 hand-written lines of code and tests, plus these documents and the 75-line checker. The item is
  under the 800-1,500 target because it is a deletion plus its condition tests; nothing was cut.

## Not delivered (FOLLOW-UP q1-4bb)

The DRI kept Q1.4b Python only, so `"Is "` is a Python literal beside the prefixes Lean exports (`speechPrefixes`,
`lean/VE/Question/Run.lean:194`). That def's doc comment still says F2 joins it in Q1.4b. Also, speech-acts.md 2.1
and its `Is <constant> <rest>?` row still describe the polar question as a gloss match. q1-4bb moves `Is ` into
`speechPrefixes` (one owner for the list; `_LEAN_PREFIXES` then reads it from the contract again) and updates those
spec lines.

Next item: q1-3 (Q1 evidence, a measurement report).

## Self-review against BUILDER-CHECKLIST

1. PASS: no new answer shape; the relayed answer is the Q1.4 relay's, checked by `question_problem`: `test_every_mutation_of_a_genuine_speech_answer_is_refused`, `test_a_surrogate_or_deep_field_is_refused`.
2. PASS: plan rows above, each with its test; grep of the diff: no new Python decision (the branch is deleted), no report test, no in-flight branch touches `ve/speech_english.py` or the two test files (all `feature/*`, `lean-first/*`, `infra/*`, `foundation/*` scanned).
3. PASS: M1-M3 and C1 ([mutants.json](mutants.json)); the checker fails on empty and head-against-head input.
4. PASS: speech caller and `ve ask` agree on verdict and text: `test_a_quantified_f2_question_is_read_as_ve_ask_reads_it`; valid wordings still read: `test_a_name_as_declared_or_capitalised_is_read`, `test_a_gloss_leans_lexicon_reads_is_read`.
5. PASS: a name not declared as written is refused, not folded: `test_a_case_folded_name_is_refused`.
6. PASS: base and head recorded at `de7cb4022` and this head (evidence/base.json, head.json); the chain runs the gate on the final HEAD.
7. PASS: every DELTA Ruling cell is `SIGNED by the DRI 2026-10-27 (reviews/dri-decisions-20261027-featureplan-gates.md item 4)` (19) or cites R1/R2/R3; none reserved.
8. PASS: [DELTA.md](DELTA.md) covers all 238 changed records of evidence/delta.json (`speech_ab_f2.py check`: failing 0).
9. PASS: `select_tests` selects `tests/test_speech_polar_lean.py` and `tests/test_speech_acts.py` (156 of 479 units), the files whose tests M1-M3 fail.
10. N.A.: no theorem added or changed (no Lean change).
11. PASS: the question limits are Lean's, as in Q1.4: `test_the_question_limits_are_leans`; no new budget.
12. PASS: one Lean call per `Is ` question, replacing `parse_english`'s E2 call on the fallback; the A/B (2,436 records) ran in 21 s on both base and head.
13. PASS: `Test-removed: tests/test_speech_polar_lean.py::test_a_wording_without_the_f1_prefix_is_not_sent — …` on `be68ad37`; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.

## FIXMAP
- `ve/speech_english.py`: the speech-acts parser. `_LEAN_PREFIXES` (the contract's prefixes plus `"Is "`) at
  `ve/speech_english.py:154`; `_polar` (the relay to `english.question` with caller `speech-acts`) at `:157`;
  `parse_speech`'s routing `if text.startswith(_LEAN_PREFIXES)` at `:185`. `_copular` (`:76`) remains for
  `_sentence` and `_body` only.
- `tests/test_speech_polar_lean.py`: routing (`test_the_routed_prefixes_are_the_contracts`,
  `test_a_wording_without_a_routed_prefix_is_not_sent`, `test_an_f2_wording_is_sent`); the three DRI classes in the
  section "Q1.4b: F2's three classes" (`GLOSSED`, `refused`, `ve_ask`).
- `tests/test_speech_acts.py::test_a_declared_gloss_is_one_opaque_atom_and_the_word_lint_only_warns`: the gloss
  directive, now through `Which one of …`.
- `docs/question-answering/q1-4b/evidence/`: base.json, head.json, delta.json (recorded by
  `../q1-4/evidence/speech_ab.py write|compare`), `speech_ab_f2.py check` (the three classes, R1, O1, the decided counts).
- Lean (unchanged, the owner): `VE.Question.Run.speechPrefixes` `lean/VE/Question/Run.lean:194`, `Caller.auxs` `:181`,
  `speechAuxiliaries` `lean/VE/Question/Basic.lean:11`.
- Regression tests: `VE_NATIVE_PREBUILT=1 uv run pytest -q tests/test_speech_polar_lean.py tests/test_speech_acts.py`
- Evidence: `VE_NATIVE_PREBUILT=1 uv run python docs/question-answering/q1-4/evidence/speech_ab.py write <out>` (on
  the base and the head), `... compare base.json head.json delta.json`, then
  `uv run python docs/question-answering/q1-4b/evidence/speech_ab_f2.py check docs/question-answering/q1-4b/evidence/delta.json`.
- Generated files: none changed (no regen input touched); if one is, `uv run python tools/regen_generated.py --write`.
- trust_mutants: not run (no trusted Lean changed).
## END FIXMAP
