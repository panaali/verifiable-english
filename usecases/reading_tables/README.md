# Reading tables of feature C (answers under each named reading)

One table per law (`<law>.tsv`, the format of `usecases/reading_runs.py`), its run (`runs/<law>.json`), the two match
graders' outputs (`match/`), the sealed per-reading answers with every value hashed (`SEALED.tsv`), the frozen reading
names (`READINGS.tsv`) and the checks run on each final table (`CHECKS.tsv`). `usecases/reading_compare.py` is the gate
over this folder and `tests/test_reading_compare.py::test_the_reading_tables_pass_the_sealed_gate` runs it: a change to
any file here fails until the table is run again, both graders and the source check ran on it, and every per-reading
answer equals the sealed answer of its matched reading. Per-reading answers are counted apart, never in a headline.
The laws' use cases are on their own branches (not here); the run files record what each run used.
