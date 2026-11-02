# Q1.3b: DELTA

No user-visible delta. The item extends a measuring script (`conformance/question_reverse.py`, its `--part b`), its
tests, its saved evidence, two reports and the batch's own `seed.py`, `samples.py` and `claims.py`. No file under `ve/`, `lean/` or `rust/` changes
(`git diff --name-only main...HEAD`), so no verdict, text, code or limit changes, and the table has no rows.
`read_sentences` now also keeps `english.read`'s `code` and `span`, which only this script reads.
