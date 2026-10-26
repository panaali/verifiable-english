# Q1.4 report: speech acts' F1 polar questions and `Must`/`Can` refusal read by Lean

**No DRI signature is reserved in this item.** It is cut: `Is <Name> …?` (F2) stays Python's, because moving it
changes 19 verdicts (below). That move is the next item, Q1.4b, and it needs the DRI's decision on those rows first;
Q1.3 is independent. Merge base `c45d799f3`. Statement gate: no theorem statement is added or changed (`#guard`s only).

## Plan rows (docs/spec/question-answering-PLAN.md Q1.4, 3.5, 5, 6.4)

| Row | Status | Where |
|---|---|---|
| Lean: `VE.Question` with `auxs := ["is"]` for the speech-acts caller | delivered | `Caller.auxs`, `speechAuxiliaries`; request field `caller` (`decodeCaller`, `caseFields`); `Examples.lean:81-104` |
| `ModalQuestion` becomes a Lean text in `VE.Question.Texts`, speech caller only | delivered | `modalWords`, `modalQuestionText`, `Run.modalFields`, status `modal`; `Examples.lean:106-111` |
| Python: polar branches call `read_question` | F1 delivered; F2 → Q1.4b | `speech_english._polar`, prefixes from the contract's `callers` (`speechPrefixes`) |
| Delete the Python F1 branch and the `Must`/`Can` refusal | delivered | d20414bb1 |
| Delete the polar use of `_copular` | Q1.4b | `speech_english.py:188` stays until the DRI decides F2's rows |
| 6.4: speech fixtures keep their content; `Must …` keeps the refusal with Lean's text | delivered | `tests/test_speech_acts*.py`, conformance pass unchanged; `test_a_modal_wording_gets_leans_refusal` |
| A/B over the speech-acts corpus | delivered | [DELTA.md](DELTA.md): 0 verdict, 60 rows under R1/R2 |
| Relay lint on the speech polar path | delivered | `RELAYED_FUNCTIONS["ve/speech_english.py"] = ("_polar",)` |

## Deletion ledger

- Deleted: `speech_english.py`'s F1 branch (`_formula` over `Is it the case that …?`) and its `Must`/`Can` refusal.
- `_copular` stays, with these callers: `_sentence` (`Does it follow from these premises that …?`, `Prove that …`;
  Q3), `_body` (which-questions; Q3) and the F2 branch `Is <Name> …?` (Q1.4b).
- `read_question` gains `caller`; `question_problem` gains two binding checks: `ModalQuestion` only for the
  speech-acts caller, and no lone surrogate anywhere. The second also closes the gap for `ve ask --reading`.
- New layer-ledger edge `ve.speech_english -> ve.backends.english_lean` (`tools/layer-exceptions.json`).

## Why F2 is cut (Q1.4b)

With `Is ` routed to Lean too (`speech_ab.py write-f2`, [evidence/delta-f2.json](evidence/delta-f2.json)), 19
verdicts change. No standing ruling covers them:
- Python reads a declared one-place gloss as one opaque predicate: `Is atlas reviewed by staff?` and 7 others under
  `glossed`, and `Is tom a cat?` under both `f0-*`. Lean's lexicon has no such wording, so it refuses them (10 rows).
- Python folds a name's case (`Is ATLAS reviewed?`), and Lean refuses it (3 rows).
- Python refuses `Is every service reviewed?` and `Is some service reviewed?` (`UnknownAlternative`). Lean reads them,
  which widens what is accepted (6 rows).

The plan expects the gloss difference (Q1.4: "`_copular`'s match on a declared verbalisation against Lean's lexicon
wording"). Once the DRI signs or redirects these rows, Q1.4b is Python only: add `"Is "` to `speechPrefixes`, delete
line 188 and the `Is <Name>` test case.

## Evidence

- Seeded bugs: [mutants.json](mutants.json), each planted alone, shown failing, then restored. Lean (10):
  `speechAuxiliaries := []` fails G24 (`Examples.lean:81`); the text dropped fails the `Must` fixture
  (`Examples.lean:106`, `test_a_modal_wording_gets_leans_refusal`); one per other new definition. Python (7): one per
  binding check (`ModalQuestion`'s caller, the lone surrogate, a caller outside the contract) and per routing step.
- Trust mutants: [trust-mutants.json](trust-mutants.json), 39 KILLED, 0 survivors or UNKNOWN (exit 0).
- Trust: V +30, K +0, S +0 (Run.lean +28 under R6, Basic.lean +2 under R16), as two allowances in
  `docs/trust-baseline.json`. `trust_map.py --check` passes.
- Tests: `tests/test_speech_polar_lean.py` (55) and a curated run of 39 files on the final code (speech, question, ask,
  relay lint, manifest, regen, trust, layers, schemas, conformance, gate collection): 2,207 passed, 0 failed. `select_tests --run`
  selects 374 of 462 units (Lean changed); the chain's gate runs them. Not this item: `tests/test_p1_amendment{9,12,15}.py`
  fail on the Mac runner (`httpx.ConnectError`, no DNS) and pass on the VM.
- Pilot bytes expected to move: 0. Size: 645 hand-written lines (`git diff --numstat` over the merge base
  without generated files and saved evidence JSON): over the ~600 rule by the 155-line A/B script; F2 is already cut.

## Self-review against BUILDER-CHECKLIST

1. PASS: `test_every_mutation_of_a_genuine_speech_answer_is_refused`, `test_a_surrogate_or_deep_field_is_refused`, `test_lean_refuses_a_malformed_caller`.
2. PASS: the plan rows above; F2 is cut for its verdict rows (a ruling's precondition), named as Q1.4b; no in-flight branch shares a hand-written file (173 scanned).
3. PASS: [mutants.json](mutants.json), [trust-mutants.json](trust-mutants.json) (39 KILLED).
4. PASS: the A/B, `speech_ab.py compare` and `check` ([DELTA.md](DELTA.md)); `test_an_f1_question_is_leans_reading`.
5. PASS: `test_a_modal_answer_is_bound_to_the_speech_caller`, `test_the_relay_refuses_a_caller_outside_the_contract`, `test_the_caller_is_sent_only_when_given`.
6. PASS: the evidence is recorded from the merge base and from this head; the chain runs the full gate on the final HEAD.
7. PASS: every DELTA row cites R1, R2, R3, R6 or R16; nothing is unsigned.
8. PASS: [DELTA.md](DELTA.md) covers every changed record of `delta.json` (60).
9. PASS: `select_tests` selects `tests/test_speech_polar_lean.py` and `tests/test_speech_acts.py`; Lean files changed, so most units are selected.
10. N.A.: no new or changed theorem.
11. N.A.: no new budget or limit; the speech caller reads under E2's `workBudget`, the same as `ve ask`.
12. N.A.: one Lean call per F1 question, replacing `parse_english`'s; the A/B (2,048 records) ran in 10 s.
13. PASS: no test removed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
