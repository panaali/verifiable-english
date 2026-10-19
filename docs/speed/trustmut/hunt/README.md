# speed-trustmut: the probes of reviews F1, F6-F12 and of the adversarial hunts (REPORT section 1e)

Each `<name>.sh` is one command, run from the root of a checkout of this branch:

    PATH=$HOME/.elan/bin:$PATH bash docs/speed/trustmut/hunt/<name>.sh

It builds a tiny Lean package under a temporary directory (F1 reads this checkout's own tree instead), runs
`tools/trust_mutants.py` on it, prints the mutants of the definition at issue as (operator, status, detail) and
asserts that none has the verdict the form wrongly gave (KILLED, or INVALID). Every probe exits 0 on the final tool
except N4, which the hunt's boundary (1) puts out of the class: an `@[implemented_by]` makes the mutated definition
the code that runs, so `#guard`'s changed value is a genuine refutation. Each form is also a row of
`tests/test_trust_mutants.py` (`HUNT`, `STUCK`), which is what the suite runs.

| Names | Source |
|---|---|
| F1, F6-F12 | the reviews' PROBE lines (F12: F11's with `bS`) |
| H1-H7, G1-G5 | hunt 1 (G: forms tried that were fine) |
| N1-N10 | hunt 2 |
| P1-P9 | hunt 3 |
| Q1-Q12 | hunt 4 |
| R1-R8 | hunt 5 |
| S1-S9 | hunt 6 |
