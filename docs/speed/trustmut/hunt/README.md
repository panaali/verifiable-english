# speed-trustmut: the probes of reviews F1, F6-F16 (F14c, F15c and F16c: their classes) and of the adversarial hunts (REPORT section 1e)

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
`../evidence/probes.json` with the sha256 of the tool, the test file, the report (its quote of this line left out),
`../claims.py` and `F15c.md` (`SOURCES`); its summary line:

> Probes on 8820e8cd6 (this checkout's sources): 84 of 85 exit 0; non-zero: N4 (1, boundary 1); not run: F14c (it checks this file's sentences against this file: run after run.py), T5w (a mutant's build runs until --build-timeout), T7 (a mutant's build runs until --build-timeout).

F14c runs `../claims.py`, which checks against the saved evidence the sentences of the report and of this README
that `CLAIM` reads as stating a result, the report's step-1 table and the sentences its `named()` lists, and no other
number (review F14 as a class). F15c runs it on `F15c.md`, one wrong count of each form `CLAIM` reads, and requires
each UNBOUND, as its own sentence (review F15 as a class). F16 changes one number of the table or of a named sentence
per copy of the report, and F16c each cell and each named number alone, each named sentence removed alone; both
require UNBOUND on every copy (review F16 and its class).

| Names | Source |
|---|---|
| F1, F6-F16, F14c, F15c, F16c | the reviews' PROBE lines (F12: F11's with `bS`; F14, F15 and F16 read REPORT.md and the saved evidence, no Lean; F14c, F15c and F16c are F14's, F15's and F16's classes) |
| H1-H7, G1-G5 | hunt 1 (G: forms tried that were fine) |
| N1-N10 | hunt 2 |
| P1-P9 | hunt 3 |
| Q1-Q12 | hunt 4 |
| R1-R8 | hunt 5 |
| S1-S9 | hunt 6 |
| T1-T7 | hunt 7 (T5w and T7 were not reported by the hunter: its builds did not end) |
