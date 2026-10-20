# speed-trustmut: the probes of reviews F1, F6-F14 (F14c: F14's class) and of the adversarial hunts (REPORT section 1e)

Each `<name>.sh` is one command, run from the root of a checkout of this branch:

    PATH=$HOME/.elan/bin:$PATH bash docs/speed/trustmut/hunt/<name>.sh

It builds a tiny Lean package under a temporary directory (F1 reads this checkout's own tree instead), runs
`tools/trust_mutants.py` on it, prints the mutants of the definition at issue as (operator, status, detail) and
asserts that none has the verdict the form wrongly gave (KILLED, or INVALID). N4 exits non-zero by design: the
hunt's boundary (1) puts it out of the class (REPORT section 1e). T6 is boundary (3), but PROBE T6 exits 0 on the final tool: since
hunt 7 the fallback instance its check reads is compared with the control's, so its mutant is UNKNOWN. T5w and T7 are not run: a mutant
makes Lean's build run forever, and the tool gives it UNKNOWN after `--build-timeout` (1,800 s by default), past the
probe's own wait. Each fixed form is also a row of `tests/test_trust_mutants.py` (`HUNT`, `STUCK`,
`test_a_build_past_its_time_limit_is_unknown`), which is what the suite runs.

`run.py` runs them all (or the names given) and saves each exit code, time and last line in
`../evidence/probes.json` with the sha256 of the tool and of the test file they ran; its summary line:

> Probes on be422c2d3 (this checkout's tool): 80 of 81 exit 0; non-zero: N4 (1, boundary 1); not run: F14c (it checks this file's sentences against this file: run after run.py), T5w (a mutant's build runs until --build-timeout), T7 (a mutant's build runs until --build-timeout).

F14c runs `../claims.py`, which binds every sentence of the report and of this README that states a result to
the saved evidence (review F14 as a class).

| Names | Source |
|---|---|
| F1, F6-F14, F14c | the reviews' PROBE lines (F12: F11's with `bS`; F14 reads REPORT.md and the saved evidence, no Lean; F14c is F14's class) |
| H1-H7, G1-G5 | hunt 1 (G: forms tried that were fine) |
| N1-N10 | hunt 2 |
| P1-P9 | hunt 3 |
| Q1-Q12 | hunt 4 |
| R1-R8 | hunt 5 |
| S1-S9 | hunt 6 |
| T1-T7 | hunt 7 (T5w and T7 were not reported by the hunter: its builds did not end) |
