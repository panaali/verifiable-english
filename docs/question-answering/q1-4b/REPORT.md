# Q1.4b report: `Is <Name> …?` read by Lean's question reader through the speech caller

**Status: every DELTA verdict row is signed.** V1–V19 by the DRI 2026-10-27
(reviews/dri-decisions-20261027-featureplan-gates.md item 4); P1–P225 by the DRI 2026-10-28
(reviews/dri-decisions-20261028-q1-4b.md items 1–5: the F1 rows, recheck 1's F3 and F4, and class (d), which covers
recheck 2's F5 openings P20–P69 and loop recheck 1's F6 openings P70–P225), each with a
test that the speech caller's verdict and text equal `ve ask`'s. Every refusal row cites R1 or R2.
Branch head: the commit that adds this fix report, on merge base `de7cb4022`. `parse_speech` sends wordings beginning with
`Is ` to Lean's `english.question` with caller `speech-acts`, and the `Is <Name>` branch (Python's `_copular` used for
polar questions) is deleted. Python only; no Lean change, no theorem statement added or changed. Open: FOLLOW-UP q1-4bb (below).

## Plan rows delivered

| Plan / directive line | Delivered by | Test |
|---|---|---|
| Plan Q1.4 (question-answering-PLAN.md 6.4 table): "`speech_english.py`'s polar branches …, the polar use of `_copular` … are **deleted**; Python relays. `_copular` stays for which-questions and `follows`" | `ve/speech_english.py`: `"Is "` joins `_LEAN_PREFIXES`; the `Is <Name>` branch is deleted; `_copular` is left for `_sentence` (follows, prove) and `_body` (which) | `test_an_f2_wording_is_sent`, `test_a_wording_without_a_routed_prefix_is_not_sent` |
| DRI item 4 (a): a gloss question gets Lean's refusal text | the routing above | `test_a_gloss_question_gets_leans_refusal_text` (accepting side: `test_a_gloss_leans_lexicon_reads_is_read`, `test_a_gloss_outside_the_environment_is_refused`) |
| DRI item 4 (b): a case-folded name is refused | the routing above | `test_a_case_folded_name_is_refused` (`ATLAS`, `aTLAS`, `ATlas`, `BEACON`; accepting side: `test_a_name_as_declared_or_capitalised_is_read`, `atlas`, `Atlas`, `Beacon`) |
| DRI item 4 (c): `Is every service reviewed?` gets the same verdict and text through the speech caller as through `ve ask` | the routing above | `test_a_quantified_f2_question_is_read_as_ve_ask_reads_it` (runs `ve ask DOC Q --reading` and `--json` on a document in the speech environment; `every`, `some`, and the refusing side `Is a service reviewed?` with its two rephrasings) |
| DRI 2026-10-28 items 1–5: P1–P225 equal `ve ask` | the routing above; the corpus's `opening_cases` (one sentence per grammar rule, asked once per `is` gap: `test_every_opening_verdict_row_is_read_as_ve_ask_reads_it`, 206 rows; coverage: `test_the_corpus_records_a_question_for_every_grammar_opening`, `test_every_opening_sentence_is_spelled_in_both_polarities`, `test_a_declared_not_form_is_asked_in_every_opening_and_recorded`) and `reader_cases` (determiners read from the grammar source x predicate with and without a verbalisation x polarity) | `test_a_declared_negative_verbalisation_has_a_recorded_verdict_change`, `test_a_declared_name_with_digit_or_underscore_has_both_verdict_changes`, `test_a_no_question_is_read_as_ve_ask_reads_it`, `test_an_unverbalised_predicate_is_read_as_ve_ask_reads_it`, `test_every_quantified_unverbalised_verdict_row_is_read_as_ve_ask_reads_it`, `test_the_corpus_records_every_grammar_determiner_and_predicate_form` |
| DELTA: every changed answer or refusal has a recorded row | [DELTA.md](DELTA.md) V1–V19 and P1–P225 signed | `evidence/speech_ab_f2.py audit evidence/delta.json` (= `check`) exits 0: `test_the_extended_delta_audits_every_verdict_as_signed`, `test_the_delta_audit_catches_missing_or_unclassified_verdicts` |
| "Bytes 0" | no pilot document asks an `Is <Name> …?` speech question (`conformance/`, `usecases/`: none) | expected pilot bytes moved: 0 (an estimate) |

The original 19 verdict rows change exactly as the decision lists them: 10 gloss (`glossed` 8, `f0-*` `Is tom a cat?` 2), 3
case-folded (`Is ATLAS reviewed?` under `speech`, `glossed`, `f0-reviewed`), and 6 every/some (`Is every/some service
reviewed?` under `speech`, `glossed`, `f0-reviewed`). The saved delta is byte-identical to Q1.4's `write-f2` preview
recorded against this base. F1 adds ten more verdict rows: two accepted negations when a negative verbalisation is
declared, four bare service names with digits or underscores newly refused, and those four names quoted newly accepted.
Recheck 1 (F3, F4) found the corpus still missed two of the reader's dimensions, so fix round 2 generates them:
`reader_cases` crosses every determiner the grammar source puts before a noun (`every`, `some`, `no`) and a name with a
predicate declared with and without a verbalisation (as declared and capitalised) and both polarities. That adds nine
verdict rows: `Is no service reviewed?` (P11), `Is atlas checked/Checked?` without a verbalisation (P12–P13), and
`Is every/some/no service checked/Checked?` (P14–P19). The DRI signed all of them on 2026-10-28; `ve ask` reads each
the same, which the tests assert. Recheck 2 (F5) found the corpus still asked only determiner openings, so fix round 3
generates the openings from the grammar too: `opening_cases` builds one sentence per rule of the grammar source (the
shortest sentence reaching the rule's left-hand side, the environment's words for the vocabulary categories) and asks
it once for each `is` it has, in `speech` and `unverbalised`. 99 of the 101 rules get a sentence (the two left out
need a binary relation neither environment declares); 214 questions are new. That adds 50 verdict rows, all a refusal
becoming Lean's reading (P20–P69: `Is there a service that is reviewed?`, `Is this impossible?` read as `bottom`,
`Is it not the case that atlas is reviewed?`, `Is every service that is reviewed reviewed?`, the ordinal and named
declarations, `Is atlas the same as atlas?`, ...), each equal to `ve ask`'s answer, and 164 refusal rows (W2, C4, C5).
Loop recheck 1 (F6) found the same gap in `negative`: with the not-form declared, `Is every service not reviewed?`,
`Is there a service that is not reviewed?`, `Is every service that is not reviewed reviewed?`, ... were refused at
base, read by Lean, and not asked. Fix round 4 removes the two limits behind it: `opening_inputs` takes every
environment of the added corpus with each of its one-place predicates over `service` (not two fixed pairs), and
`_lexicon` gives `atom` and `relative` both polarities (`_spellings`: the verbalisation and the declared not-form,
`is not <word>` where none is declared), so each sentence is spelled with every combination of polarities in its
places, the all-positive one first (so the earlier 222 questions are unchanged). 2,051 questions are new: 156
verdict rows, all a refusal becoming Lean's reading (P70–P225: 102 `negative`, 28 `names`, 26 `unverbalised`; none
in `speech`, where the undeclared not-form is refused before and after), each equal to `ve ask`'s answer (the
206-row condition test), and 1,892 refusal rows (C6, W3). `opening` now excludes every case recorded before it
(`named_cases`, `reader_cases`), so `Is atlas not reviewed?` stays in item 1's class.

## What changed for users (summary of [DELTA.md](DELTA.md))

- 244 verdicts: the original 19 signed by item 4, plus P1–P225 signed by the DRI 2026-10-28 (items 1–5).
- 159 wording rows (R1, R2's O1): the base's text for an `Is <…>?` with no matching gloss was
  `The character at position 0 cannot appear outside a quoted name.` Python's fallback lexed `@<name> <rest>.`, so
  that position belonged to an `@` the writer never typed. The head gives Lean's text over the question itself (the
  closest sentence tried, the unknown phrase, the true position).
- 2,127 class rows (R1, R3 for the added spans): `InvalidInput: no single speech-act reading` and
  `UnknownAlternative: wording, <word>` become Lean's `SyntaxError`/`TypeMismatch` with a span. The 88 rows of the
  original corpus keep the base's word; of the 156 opening rows (C4), 56 name the fault Lean found (a list marker, a
  name used before it is introduced or introduced twice) without repeating the base's unquoted first word, which the
  head's span covers. The 1,881 opening rows of fix round 4 (C6) are the same refusals in the added environments
  and polarities.
- The `OpaqueWording` lint now appears on `Which one of …` and query targets only. A polar question that matched a
  gloss is now refused, so it carries no lint. The gloss directive's test asks its glosses as `Which one of …`.

## Seeded bugs (Python, `ve/speech_english.py`; [mutants.json](mutants.json))

| Mutant | Behaviour | Failing test |
|---|---|---|
| M1: the `Is <Name>` branch left in, before the routing | class (a) | `test_a_gloss_question_gets_leans_refusal_text` (3 failed) |
| M2: case folding kept (the name replaced by `_name`'s folded constant before routing) | class (b) | `test_a_case_folded_name_is_refused` (4 failed) |
| M3: `"Is "` dropped from `_LEAN_PREFIXES` | class (c), routing | `test_a_quantified_f2_question_is_read_as_ve_ask_reads_it` (3 failed) |
| C1: the delta checker given q1-4's delta, a row with head text `x`, and head against head | evidence | `speech_ab_f2.py check` exits 1 on each, 0 on the saved delta |
| C2 (fix round 2): `determiners()` returns `("every", "some")` instead of reading the grammar source | corpus coverage (F3's class) | `test_the_corpus_records_every_grammar_determiner_and_predicate_form`, `test_the_extended_delta_audits_every_verdict_as_signed` (2 failed) |
| C3 (fix round 2): a determiner row's head may be any atom, not its determiner's formula | evidence | `test_the_delta_audit_catches_missing_or_unclassified_verdicts[speech-Is no service reviewed?-change_head]` (1 failed) |
| C4 (fix round 3): `opening_sentences` skips every rule that opens with a word other than a determiner (F5's blind spot) | corpus coverage (F5's class) | `test_the_corpus_records_a_question_for_every_grammar_opening`, `test_the_extended_delta_audits_every_verdict_as_signed` (2 failed) |
| C5 (fix round 3): `opening_cases` asks only the first `is` gap of each sentence | corpus coverage (`Is every service that is reviewed reviewed?`) | the same 2 tests (2 failed) |
| C6 (fix round 4): `_spellings` returns only the positive form (no not-form in any place) | corpus coverage (F6's class) | `test_a_declared_not_form_is_asked_in_every_opening_and_recorded` (5), `test_every_opening_sentence_is_spelled_in_both_polarities`, `test_the_extended_delta_audits_every_verdict_as_signed` (7 failed) |
| C7 (fix round 4): `opening_inputs` keeps only `speech` and `unverbalised` | corpus coverage (F6's environments) | `test_the_corpus_records_a_question_for_every_grammar_opening`, `test_a_declared_not_form_is_asked_in_every_opening_and_recorded` (5), `test_the_extended_delta_audits_every_verdict_as_signed` (7 failed) |

Each was planted alone, shown failing, and restored; the tree was clean afterwards. No Lean or Rust product code
changed, so there are no seeded bugs in those languages.

## Trust and tests

- Trust: `tools/trust_map.py --check` PASS, K +0, S +0, D +0, G +0, trusted +0. No allowance, no R16 row, no trust
  mutants (no trusted Lean changed).
- Fix round 4 (loop recheck 1 F6): selected tests (`mac-pytest.sh --select -- --base de7cb4022 --run`, HEAD
  `4e1f58ffb`): 158 units, 0 failed; PROBE F6 exits 0; the 206-row condition test passes.
- Fix round 3: selected tests (`mac-pytest.sh --select -- --base de7cb4022 --run`, HEAD `c4a134909`): 158 units,
  0 failed; the F5 probe exits 0.
- Selected tests on the final code, before this report (`mac-pytest.sh --select -- --base de7cb4022 --run`, HEAD
  `acf66cbb`): 158 units, 0 failed. Before that, the 6 speech files (313 tests), then `tests/test_speech_polar_lean.py`
  (145 passed).
- `tools/gate_collection.py --check --prebuilt`: 34 added, 4 removed by a trailer, 0 refused, 0 stale, 0 malformed. The
  `Test-removed:` trailer is on commit `be68ad37`, which renamed the F1-prefix boundary test to the `Is ` boundary test
  and added the sent side.
- Not run: the full gate. The chain runs it on the final HEAD.
- Size: about 220 hand-written lines of code and tests, plus these documents and the 75-line checker. The item is
  under the 800-1,500 target because it is a deletion plus its condition tests; nothing was cut.

## Sibling lessons (review q1-4)

- F1, the question limits: the base read an F2 question only through a gloss match, because its fallback always
  failed on the `@` it added. A gloss is at most 256 characters (`lean/VE/Bridge.lean:123`, `ResourceLimit:
  verbalisation size`), so no question the base read comes near 300 tokens or 4,096 bytes. No F2 verdict changes at
  the limits (probe: a 60-word gloss is refused by the environment, a 40-word one is far under both limits).
- F2, rephrasings: `Is a service reviewed?` carries both rephrasings through the speech caller, the same lines
  `ve ask` prints (`test_a_quantified_f2_question_is_read_as_ve_ask_reads_it`, refusing case).
- F3, one-sided checks: this item adds no check; every test of a refusing side has its accepting side beside it
  (the routed and unrouted prefixes, the glosses Lean reads and refuses, the names as declared and folded).

## Not delivered (FOLLOW-UP q1-4bb)

The DRI kept Q1.4b Python only, so `"Is "` is a Python literal beside the prefixes Lean exports (`speechPrefixes`,
`lean/VE/Question/Run.lean:194`). That def's doc comment still says F2 joins it in Q1.4b. Also, speech-acts.md 2.1
and its `Is <constant> <rest>?` row still describe the polar question as a gloss match. q1-4bb moves `Is ` into
`speechPrefixes` (one owner for the list; `_LEAN_PREFIXES` then reads it from the contract again) and updates those
spec lines.

Also a Lean FOLLOW-UP (recheck 2): `Is this impossible?` is read as `bottom` (P42, P67), as `ve ask` reads it. Whether
the question spec should refuse it is Lean's to decide; this item records Lean's reading and adds no Python refusal.

Next item: q1-3 (Q1 evidence, a measurement report).

## Self-review against BUILDER-CHECKLIST

1. PASS: no new answer shape; the relayed answer is the Q1.4 relay's, checked by `question_problem`: `test_every_mutation_of_a_genuine_speech_answer_is_refused`, `test_a_surrogate_or_deep_field_is_refused`.
2. PASS: plan rows above, each with its test; grep of the diff: no new Python decision (the branch is deleted), no report test, no in-flight branch touches `ve/speech_english.py` or the two test files (all `feature/*`, `lean-first/*`, `infra/*`, `foundation/*` scanned).
3. PASS: M1-M3 and C1 ([mutants.json](mutants.json)); the checker fails on empty and head-against-head input.
4. PASS: speech caller and `ve ask` agree on verdict and text: `test_a_quantified_f2_question_is_read_as_ve_ask_reads_it`; valid wordings still read: `test_a_name_as_declared_or_capitalised_is_read`, `test_a_gloss_leans_lexicon_reads_is_read`.
5. PASS: a name not declared as written is refused, not folded: `test_a_case_folded_name_is_refused`.
6. PASS: base and head recorded at `de7cb4022` and this head (evidence/base.json, head.json); the chain runs the gate on the final HEAD.
7. PASS: every DELTA verdict cell is signed by the DRI (V1–V19: 2026-10-27 item 4; P1–P225: 2026-10-28 items 1–5) and names its condition test; no signature is reserved.
8. PASS for evidence coverage: [DELTA.md](DELTA.md) covers all 2,530 changed records of evidence/delta.json (`speech_ab_f2.py audit` and `check`: failing 0, each class at its recorded count).
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
- `docs/question-answering/q1-4b/evidence/`: base.json, head.json, delta.json (original corpus by
  `../q1-4/evidence/speech_ab.py write`, 2,295 extra cases by `speech_ab_f2.py augment` (`extra_cases`: `named_cases`
  :205, `reader_cases` :46, `opening_cases` :163 over `opening_inputs` :155 (every added environment x one-place
  `service` predicate) and `opening_sentences` :104 (`_lexicon` :68, `_spellings` :58 both polarities, `_Slot` :86),
  all read from `ve/english_grammar/relational-fol@0.json`), comparison by `../q1-4/evidence/speech_ab.py compare`);
  `speech_ab_f2.py audit|check` (nine signed classes, `opening` :317, `DECIDED` :331, R1, O1).
- Lean (unchanged, the owner): `VE.Question.Run.speechPrefixes` `lean/VE/Question/Run.lean:194`, `Caller.auxs` `:181`,
  `speechAuxiliaries` `lean/VE/Question/Basic.lean:11`.
- Regression tests: `VE_NATIVE_PREBUILT=1 uv run pytest -q tests/test_speech_polar_lean.py tests/test_speech_acts.py`
- Evidence: start with Q1.4's saved base/head corpus, run `speech_ab_f2.py augment <saved> <out>` once against the
  merge-base parser (`VE_AB_ROOT=<base checkout>`, e.g. `git archive de7cb4022 ve tests lean/checkers.lock` into a
  tmp dir, with `VE_LEAN_SERVICE=<this checkout>/lean/.lake/build/bin/ve_service`: Lean is identical at both commits)
  and once against the head parser; `augment` adds only cases not yet recorded. Compare with
  `speech_ab.py compare <base> <head> <delta>`, then `speech_ab_f2.py audit <delta>` (exit 0).
- Generated files: none changed (no regen input touched); if one is, `uv run python tools/regen_generated.py --write`.
- trust_mutants: not run (no trusted Lean changed).
## END FIXMAP
