# kb-1: label files the nightly mutation sweep reads

kb-1's own record, allow file, report and DELTA are in `docs/kb-1/` (signed; unchanged). The nightly sweep
(manage-agents tm-nightly.py) reads an item's allowances only from `docs/<family>/<label>/`, so it does not see
`docs/kb-1/`. This directory holds the pair the 2026-11-23 nightly needed (`VE.Kernel.Path.Ran` body-true) and kb-1's three other
Prop pairs a later nightly would reach (`Path.Ran` body-false and eq-ne, `Path` eq-ne), with kb-1's reasons, re-judged at
main df25d3c3b3 by `tools/trust_mutants.py` (`trust-mutants.json`: 4 ALLOWED; M400's raw verdict is UNKNOWN, the toy
path's proof CarryChecks.lean:16, as kb-1's reason says). kb-1's other allowed pairs are refusals (no program) and stay
only in `docs/kb-1/`. Row
tm-esc-sweep-1123; report `docs/kernel/tm-esc-sweep-1123/REPORT.md`.
