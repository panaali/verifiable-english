# speed-trustmut: the probes of reviews F1, F6-F12 and of the adversarial hunts (REPORT section 1e)

Each `<name>.sh` is one command, run from the root of a checkout of this branch:

    PATH=$HOME/.elan/bin:$PATH bash docs/speed/trustmut/hunt/<name>.sh

It builds a tiny Lean package under a temporary directory (F1 reads this checkout's own tree instead), runs
`tools/trust_mutants.py` on it, prints the mutants of the definition at issue as (operator, status, detail) and
asserts that none has the verdict the form wrongly gave (KILLED, or INVALID). Every probe exits 0 on the final tool
except N4 and T6, which the hunt's boundaries (1) and (3) put out of the class (REPORT section 1e), and T5w and T7,
where a mutant makes Lean's build run forever: the tool now gives it UNKNOWN after `--build-timeout` (1,800 s by
default), which is past the probe's own wait. Each fixed form is also a row of `tests/test_trust_mutants.py`
(`HUNT`, `STUCK`, `test_a_build_past_its_time_limit_is_unknown`), which is what the suite runs.

| Names | Source |
|---|---|
| F1, F6-F12 | the reviews' PROBE lines (F12: F11's with `bS`) |
| H1-H7, G1-G5 | hunt 1 (G: forms tried that were fine) |
| N1-N10 | hunt 2 |
| P1-P9 | hunt 3 |
| Q1-Q12 | hunt 4 |
| R1-R8 | hunt 5 |
| S1-S9 | hunt 6 |
| T1-T7 | hunt 7 (T5w and T7 were not reported by the hunter: its builds did not end) |
