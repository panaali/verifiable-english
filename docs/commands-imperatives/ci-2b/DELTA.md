# ci-2b delta: command English has one owner (Lean)

Base `63b2b596f` (`git merge-base HEAD main`). Python's command branch of `parse_speech`, `_command_candidates`,
`PROOF_TASK_ACT` and the scope sentences of `legend` are deleted; every command wording is read by Lean's
`VE.Commands.readInstruction` through `read_command` (the `english.command` mode), and the speech-source wrapper reads
every resolved command fence again. The A/B over the pinned command corpus (`evidence/ab.py`, `evidence/ab.json`,
24,204 rows) is the comparison: 24,164 rows are byte-identical (outcome, command object or `code: text`), and the 40
others are rows 2 to 5. The legend `ve speech-acts` prints is byte-identical (Lean's lines, then norms' W1 sentences:
`tests/test_speech_source_switch.py::test_public_speech_projection_matches_frozen`, every template).

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | **The authority move.** Command English (the proof task included) moves from Python to Lean; Python's command branch and `PROOF_TASK_ACT` are deleted in the same change (the deletion ledger below). | The ledger: each deleted check with its Lean check and test. The A/B: `uv run python docs/commands-imperatives/ci-2b/evidence/ab.py check` exits 0 ("A/B: no forbidden row"): every sentence the base refused is still refused (its code and quoted names kept) or read as `many`; `tests/test_ci2b_ab.py`. Trusted growth: row 6. | SIGNED by the DRI 2026-10-28 (reviews/dri-decisions-20261028-commands-imperatives.md item 2(a)) |
| 2 | **Read to refused (9 A/B rows, class b2).** 7 rows "Prove that tom is a cat using these premises." (F5: english-lean selects `{0} is classified as "cat"` for the gloss `{0} is a cat`): `NoDerivation: The sentence to prove has no reading …`; "Click check, if ." (ci-1 review F3): `EmptySentence: The condition is empty.`; a 401-byte proof wording: `limit` (O10). The live test of F5 moved to a wording english-lean reads (`tests/test_speech_acts_conformance.py::test_proof_task_wording_uses_an_act_both_linters_accept`, as P1′). | `evidence/ab.json` rows of class `b2`; P5, W18-like and O10 fixtures in `lean/VE/Commands/RunExamples.lean`. | SIGNED by the DRI 2026-10-28 (reviews/dri-decisions-20261028-commands-imperatives.md item 2(b)) |
| 3 | **Refused to `many` (1 A/B row).** "Review the meaning." was `AmbiguousDerivation: multiple declared acts match` (an `InvalidInput`-coded `VEError`); Lean reads it `many` (W10), which `read_command` raises as `AmbiguousDerivation` (code `SyntaxError`) whose text is Lean's paraphrase of each reading, one per line. | `evidence/ab.json` row of class `many`; `tests/test_command_relay.py::test_many_is_raised_with_leans_paraphrases`. | SIGNED by the DRI 2026-10-28 (reviews/dri-decisions-20261028-commands-imperatives.md item 2(a)) |
| 4 | **Reworded diagnostics (26 A/B rows).** A condition english-lean does not read: P0's "Sentence 1 has no reading with the current vocabulary. …" is english-lean's `NoDerivation: The condition has no reading with the current vocabulary. …` (22 rows), and P0's "The character at position 4 cannot appear outside a quoted name." gains its code, `BadCharacter: …` (4 rows). Each keeps the base's class (`SyntaxError`) and every quoted name. | `evidence/ab.json` rows of class `R1`; `tests/test_ci2b_ab.py` (each R1 row keeps the base's code, or class when the base has none, and quoted names; the check fails on a lost one). | R1 |
| 5 | **A proof task with no matching record (4 A/B rows).** `InvalidInput: query required` (the deleted Python selection found no record) is `QueryMismatch: <unit>` (spec P2, O1). | `evidence/ab.json` (`RULED` in `ab.py`); P2, P3, P3′ in `lean/VE/Commands/RunExamples.lean`. | R1 |
| 6 | **The wrapper's new refusals (A2).** A speech-source payload with a command fence and no `reading_context` is `InvalidInput: command reading context` (after every other check), and a resolved command that is not Lean's one reading of its wording is `InvalidInput: resolved speech fences`. `ve speech-acts` always sends the context with the resolved fences, so no document it reads changes. | `tests/test_command_relay.py::test_a_command_fence_needs_the_reading_context`, `::test_a_resolved_command_lean_does_not_read_is_refused`, `::test_a_question_fence_needs_no_reading_context` (the opposite direction); `commandFence_needs_context`. | SIGNED by the DRI 2026-10-28 (reviews/dri-decisions-20261028-commands-imperatives.md item 2(b)) |
| 7 | **Trusted Lean growth** (`lean/VE/SpeechActs/Source/Run.lean`: the A2 re-read and the split of `decodeSpeechSource`; figures in REPORT.md, "Trust"). | `uv run python tools/trust_map.py --check` with the allowance in `docs/trust-baseline.json`; `trust-mutants.json`; `mutants.json` S2, S3; the FOLLOW-UPS.md row under "## ci-2b". | R16 |

## The deletion ledger (DRI item 2(a))

| Deleted (`ve/speech_english.py`, `ve/speech_document.py`, `ve/speech_acts.py`) | Lean check | Test |
|---|---|---|
| `You may ` → `PermissionNotCommand` | `prefixRefusal`, diagnostic 3 | W15 (`Examples.lean`); A/B rows "You may open the desk." and 4 others (`mutants.json` S5) |
| `Please ` → please needs author approval | `prefixRefusal`, diagnostic 4 | W24; `RunExamples.lean` "Please prove …" guard; A/B |
| ` and ` coordination flag | `coordinated`, diagnostic 13 | W25, W26; A/B (48 `CoordinatedActs` rows of the Q1.4 corpus, same) |
| proof task, `PROOF_TASK_ACT` | `proofTask`, `Texts.proofAct` | P1′ to P8 (`RunExamples.lean`) |
| the proof task's query selection (`speech_document.py`: `_sentence`, then the one query whose target matches) | `proofTask`'s record match (`matchedRecord`) | P2, P3, P3′, P3″; A/B row 5 |
| `text.endswith(".")`, `rsplit(", if ")`, `Do not ` | `parts`, `splitLastIf` | W8, W9, W29 |
| `_command_candidates` (every act with a verb, constants and definites) | `slotFills`, `tuples`, `phraseMatches` | W5 to W7, W10 |
| `ascii_fold(plain) == ascii_fold(phrase)` | `fold`, `filled` | W27, W28 |
| one match, `AmbiguousDerivation`, wrong role | `readCommand`, `refusal`, diagnostics 8, 10, 11 | W10, W22, W23; A/B row 3 |
| the condition through `_formula` | `guardOf` | W8, W18, W19; A/B row 4 |
| the scope sentences of `legend` | `VE.SpeechActs.Run.legend`, relayed in the source report's `legend` | `test_public_speech_projection_matches_frozen` (against the frozen pre-switch legend) |
| `act_verb` (its one caller was `_command_candidates`) | `VE.SpeechActs.Wire.actVerb` (`readCommand`'s verb) | W1 to W7 |

Kept, as the plan's ledger says: `_sentence` (assertions and `follows`), `_copular` (which-questions and `follows`,
question-answering's Q3), the `Does it follow from these premises that …?` selection in `speech_document.py`, q1-4b's
`_polar` and `_copular`'s polar use, and norms' `default_sentence` for the W1 lines of `legend`.
`tests/frozen_speech/speech_english.py` keeps the deleted parser verbatim as test data: the frozen pre-switch checkers
and the A/B's base read commands with it.
