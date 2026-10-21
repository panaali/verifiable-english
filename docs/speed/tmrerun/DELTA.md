# speed-tmrerun: DELTA

No user-visible delta, so this file has no rows. The item stopped after step 1 (REPORT.md section 1: the carry rule
carries under half of the rerun mutants). It adds only the step-1 measurement under `docs/speed/tmrerun/`: the rule
measured (`rule.py`), its replay (`replay.py`, `replay.json`), its seeded bugs (`mutants.json`,
`mutants-evidence.json`) and ap-1b's saved second-run evidence (`evidence/`). It changes no file under `ve/`, `lean/`,
`rust/`, `tools/` or `conformance/`: `tools/trust_mutants.py` is main's, no VE output, diagnostic, verdict, limit or
fault order can change, and no gate, merge train (R2) or nightly (R3) reads anything this item adds. Trust budget:
+0 (no Lean change).
