# Q1.4: DELTA

Base: `parse_speech` at the merge base `c45d799f3` ([evidence/base.json](evidence/base.json)); head: the same corpus
with F1 and the `Must`/`Can` refusal read by Lean ([evidence/head.json](evidence/head.json)). 2,048 records (4
environments × 512 wordings, [evidence/speech_ab.py](evidence/speech_ab.py)); the differences are in
[evidence/delta.json](evidence/delta.json): 0 `verdict`, 0 `lint`, 37 `wording`, 23 `class`.
`speech_ab.py check evidence/delta.json` exits 0 (`{"rows": 60, "O1": 4, "failing": 0}`): every row other than
O1's keeps every name the base quoted, and a span wherever the base had one. `Must …` and `Can …` refusals are
byte-identical (no row), now with Lean's text.

| Row | Class, count | Base (Python) | Head (Lean) | Ruling |
|---|---|---|---|---|
| W1 | wording, 36 | an F1 refusal from `parse_english` over the embedded sentence: `Sentence 1 has no reading with the current vocabulary. <diagnosis>` (33), `Sentence 1 is marked as a conclusion, …` (3), the span of the embedded sentence | `english.question`'s text: `The question has no reading with the current vocabulary. Closest sentence tried: "…". <the same diagnosis>`, or `A question cannot contain "therefore", "so", "hence" or …`, with the span in code points of the question | R1 (DRI-RULINGS.md): (a) every quoted name kept, (b) a span on every row, (c) the head names the closest sentence or the marker word; `speech_ab.py check` |
| W2 | class, 20 | a wording that begins `Is it the case that ` but is not one question (no `?`, or a control character after it): `InvalidInput: no single speech-act reading`, no span | `SyntaxError` `Write one question that ends with a question mark.` (`NotOneQuestion`) with the question's span | R1 (DRI-RULINGS.md): the class is Lean's `codeClasses` (the English E2 precedent, its row W2); no name quoted by the base; the added span is R3 (DRI-RULINGS.md), checked inside the question by `question_problem` |
| O1 | order, 4 | `Is it the case that atlas is reviewed. Beacon is reviewed?`: `InvalidInput: Speech wording requires one sentence` (3), or sentence 1's unknown phrase under `f0-checked` (1) | `NotOneQuestion` (`Write one question that ends with a question mark.`) | R2 (DRI-RULINGS.md). O1: a wording of more than one sentence is refused as not one question before any of its sentences is read (`VE.Question.classify`: the body's sentences counted by `lexSpans` before any candidate is read by `got`); deterministic, `speech_ab.py`'s `order_o1` |
| T1 | trust, V +30 | K 997, S 11390, V 41982 at `c45d799f3` | VE/Question/Run.lean +28 (`Caller`, `Caller.auxs`, `decodeCaller`, `caseFields`, `speechPrefixes`, `questionCase`'s caller dispatch), VE/Question/Basic.lean +2 (`speechAuxiliaries`); K +0, S +0 | R6 (DRI-RULINGS.md) for Run.lean +28: they replace speech_english's deleted F1 branch and `Must`/`Can` refusal; R16 (DRI-RULINGS.md) for Basic.lean +2, new behaviour (the speech caller reads F2 with `["is"]`), exercised by `Examples.lean:81,90`; trust-mutants.json 39 KILLED; FOLLOW-UPS.md row `## q1-4` |
