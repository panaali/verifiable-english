# Batch RD-2b owner and deletion ledger

| Decision | Owner after RD-2b | Caller in this batch | Duplicate deleted |
|---|---|---|---:|
| The frame of a `readings@1` document under `norm-defaults@0`: each `unspecified` completion read as `deny`, the profile removed, every unspecified predicate's table added (E‴) | Lean `filledJson` (`withUnsaid` over `placeholderJson`), answered by `readings-validate` and, from RD-2b, `readings-elaborate` | `ve/readings_s1.py` `S1Environment(data, filled)`: the frame is Lean's `filled.environment`; without it there is none (`CheckerUnavailable`) | 1 Python copy (`readings_s1._placeholder_frame`, DRI ruling 4's placeholder; its only caller was `S1Environment`) |
| Each reading's filled document (the `over` entries `fill` adds, the `F_p` units) | Lean `fillDoc` (`filledUnitsJson`) | `readings_s1.Document(senv, document, filled)`: contents replaced by Lean's, Lean's generated units appended; `Candidate.authored` keeps what the author wrote for the `<reading>` slot | 0 (Python never built it: D12) |
| A reading's `Fill_T` in the search's witness filter | Lean `fillPremisesJson` | `Decoded.fill_holds` evaluates Lean's formulas on the base (the generator-internal evaluator of rule 3, unchanged) | 0 |
| The route, choices and their count under the completion | Lean `routeOf`, `choicesJson` (`readings-elaborate`) | `readings_route._completion_elaborate` binds the row to the request; `readings_verdicts._Route` takes Lean's choices | 0 (Python's `choices` still serves the other routes until RD-3) |
| Each choice's filled document (`E‴_base`, `Fill_T`, layers, conflict targets) | Lean `layeredElaborate` on `choiceU N c` (`readings-choice`, inner `norm-defaults-elaborate`) | `readings_verdicts._FilledChoiceDocument`: the generic prover and model search over Lean's formulas | 0 (no `UnspecifiedDocument` is built for a readings document) |
| RD-2a's refusal by name of a completion document in `ve document` | — | — | 1 (`readings_route.UNDER_COMPLETION` and its branch: the relay now relays) |

The plan (RD-2b) deletes `_placeholder_frame` "if the corpus A/B shows no other caller": it had one caller,
`S1Environment`, and every corpus of the A/B answers byte for byte as at the base
([DELTA.md](DELTA.md), evidence `ab-*.json`). `ve/document.py` `_s1_attached`, which built an `S1Environment` only to
read names, now reads them from the document alone (`Document(None, …)`).
