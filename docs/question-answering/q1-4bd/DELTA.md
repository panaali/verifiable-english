# Q1.4bd: DELTA

Base: `ve.english.parse_english` with main's `ve/backends/english_lean.py` at the merge base `e68b0dd88`
([evidence/base.json](evidence/base.json)); head: the same corpus at this item's relay
([evidence/head.json](evidence/head.json)). Lean is the same at base and head (this item changes no file under
`lean/`), so the base was recorded in this tree with main's `english_lean.py` checked out, then restored. The corpus
is 205 documents: the 163 S3 fixtures (`conformance/english_lean_s3_python._fixtures`) and 42 ill-typed documents (a
reach sentence at six places, in each of the seven S3 environments). `english_read_delta.py delta` writes
[evidence/delta.json](evidence/delta.json): the 24 records whose outcome moved. The other 181 did not move.

`tests/test_english_e2_responses.py::test_the_saved_delta_moved_only_the_dropped_code` checks the saved files
(`english_read_delta.problems`): every moved record is a `TypeMismatch` whose head is its base with the
`TypeMismatch: ` prefix dropped, and nothing else changed, including the class, the span and every quoted name.
Delta.json is the exact difference of base and head, and no head message still starts with the code.
`::test_a_delta_record_is_refused_live_with_leans_text` reads each moved record again.

| Row | Class | Env | Wording | Base (Python) | Head (Lean) | Ruling |
|---|---|---|---|---|---|---|
| W1 | wording, 24 | `F`, `FO`, `FD`, `FM` (6 each; `FA`, `FR`, `FR_UNITS` declare no `legacy` and give the same `SyntaxError` at base and head) | a document with a sentence Lean reads and refuses as `IllTyped`, e.g. `Legacy is deployed. Starting from legacy, legacy is reachable by zero or more steps, …` | `TypeMismatch` `TypeMismatch: Sentence 2 was read, and its formula does not pass the type check.` with the sentence's span | `TypeMismatch` `Sentence 2 was read, and its formula does not pass the type check.`, the same span: Lean's text verbatim (`LeanReading.rejection` no longer lets `errors._CodeWorded` prefix the code) | R1 (DRI-RULINGS.md): (a) the base quotes no name, and the sentence number is kept; (b) the same span; (c) the same text without the repeated code, which the JSON's `code` field still carries. Evidence: the saved delta and `test_the_saved_delta_moved_only_the_dropped_code` |
