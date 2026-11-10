# AR-23: deltas

None. No verdict, refusal text, step count, wire field or fault order changed. The corpus A/B over the nine corpora
of the lean-first gate (`uv run python -m tools.evidence ab ... --delta docs/arch/AR-23/evidence/ab-delta.json`:
"ab PASS") found 100,529 records the same, 31 unavailable on both sides with identical outputs (R7, below) and
0 unlisted, over 100,560 records. The base and head recordings are byte-identical (SHA-256 `e2dbb554…` for both,
`evidence/ab.json`). Closure's version gate and atom-free gate are the same row for row on both runners
(`evidence/closure-probe.json`: 134 certificate-runner rows and 6 route rows, base and head equal byte for byte).
The Lean output differential (OUT) over 441 invocations of every `lean_exe` found no output change: its one listed
difference is the backtrace frames after two pre-existing PANIC lines, which differ the same way between two runs of
the base binary (`evidence/out.json`).

The only rows the A/B lists are records unavailable on both sides with identical outputs. None is a delta. Each record
is in `evidence/ab-delta.json` with its reason; a scratch script asserted per record that base and head outputs are
byte-identical before writing it.

| # | Records | What both sides return | Ruling | Test |
|---|---|---|---|---|
| 1 | 18 `pilots/default` `document_check` records, one `translation-companions-with_source_word.ve.md` per constitution pilot run | The same pre-existing `CheckerUnavailable` (`ReadingsConstruction: ... KeyError`), byte for byte | R7 | `uv run python -m tools.evidence ab ... --delta docs/arch/AR-23/evidence/ab-delta.json` (PASS, 0 unlisted) |
| 2 | 10 `pilots/default` `document_check` records of whole-UDHR translations (`translation-whole.ve.md`, runs of 2026-10-14 to 2026-11-02) | The same 600 s recorder time-out (L75), byte for byte. They were recorded on both sides at once, at a machine load of about 68 on 32 cores. No closure formula appears in these documents | R7 | `uv run python -m tools.evidence ab ... --delta docs/arch/AR-23/evidence/ab-delta.json` (PASS, 0 unlisted) |
| 3 | 1 `pilots/default` `document_check` record, `udhr-20261102T1800Z` `translation-whole.et0.ve.md` | The same pre-existing `CheckerUnavailable` (`readings-verdicts: more than 64 compatible readings`), byte for byte | R7 | `uv run python -m tools.evidence ab ... --delta docs/arch/AR-23/evidence/ab-delta.json` (PASS, 0 unlisted) |
| 4 | 2 `discourse/default` records of text `2757af3b2b5456b1` (`document_check`, `document_render`) | The same pre-existing `CheckerUnavailable` (the norms route refuses a norm object: fields do not match), byte for byte | R7 | `uv run python -m tools.evidence ab ... --delta docs/arch/AR-23/evidence/ab-delta.json` (PASS, 0 unlisted) |

## Removed theorems and their covers (not deltas)

None removed. `lean/statements.txt`: 8506 → 8507 entries, 1 added (`VE.Closure.entails_iff`), 0 removed, 0 changed.
Every kept entry is byte-identical: its statement text, its `-- uses` line with each `@Module` tag, and its `-- expr`
hash (`evidence/statements.json`: `kept_all_byte_identical: true`). This includes the 14 statements whose `-- uses`
line names `VE.Closure.Formula.denote`. `conservativity` and `closure_route_acceptance` are among them. `predicates.txt`
is byte-identical.

Deliverable 4 asks to delete the closure-only lemmas that the new definitions make redundant, each with a cover. No
theorem qualifies.
- The lemmas the new definitions make trivial are: `VE.Core.embedClosure_denote` and `embedClosure_check` (now `rfl`),
  `VE.Core.entails_closure` (now the identity), `VE.Core.path_iff` and `reachable_iff` (now `Iff.rfl`), and closure's
  `check_iff_wellFormed`, `mem_namedEdges`, `mem_bodyEdges`, `reachable_congr`, `eval_iff_denote` and
  `eval_false_iff_not_denote` (now Core's theorem on the embedding).
- Each of them is an audited name that deliverable 3 keeps, or an old name that deliverable 2 keeps as a corollary.
- The only cover any of them would have is a definitional equation, not a Core theorem. Under the task's rule ("a
  removed theorem with no cover stays"), they stay.
- Their proofs shrank instead: P −104 lines, C −56 (`evidence/trust.json`).

## Added theorem (not a delta)

`VE.Closure.entails_iff`: closure consequence, now defined as Core's consequence of the embedded formulas, read back in
closure's own syntax. Its right-hand side is closure's old definition of `Entails`. The proofs that unfolded the old
definition use it (`Route/Background`, `Data/Background`, `Definitions/Route`, `Route/Checker`, `Service/Family`,
`Service/FamilyBundle`).
