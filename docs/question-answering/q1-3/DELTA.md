# Q1.3: DELTA

No user-visible delta. The item adds a measuring script (`conformance/question_reverse.py`), its tests, its saved
evidence and two reports. No file under `ve/`, `lean/` or `rust/` changes (`git diff --name-only main...HEAD`), so no
verdict, text, code or limit changes, and the table has no rows.

`conformance/english_lean_e2_evidence.py` gains `PER_CONFIG`, `PER_USECASE`, `use_case_claims` and `streams(claims=)`.
`claims` is off by default, so E2's streams are unchanged.
