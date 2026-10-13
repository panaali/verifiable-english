# Batch 16e report: rights@0 and readings@1 documents (review fix round 1)

Batch 16e is implemented: Lean's `document` mode decides rights documents, with and without the `readings@1` head,
and `readings@1` documents without `norm-defaults@0`, by calling the existing rights and soft routes. The route,
schema, binding, measurements, A/B, deltas and seeded faults are in [DELTA.md](DELTA.md) and `evidence/`.

## Review findings (lf-16e-review.final.md)

- **F1 (A)**, batch not implemented. The mode now composes the rights route (`Service.Document.rightsDoc`,
  `rightsContentOf`), owns `readings@1` without `norm-defaults@0`, and types and binds every new answer field. The
  class is a document Lean cannot decide; it is closed for every shape but the listed unowned parts
  (`RightsDoc.unowned`), which keep the retained path. PROBE F1 failed before the fix (stopped on `s0`) and passes
  after it: `measure.py` decides all 1,250 ledger cases (955 accepted with the prior path's report, 242 rejected
  with its error, 53 retained carve-out limits). The nine-corpus A/B has 0 unlisted differences; 15 of 15 seeded
  faults were caught.
- **F2 (B)**, measurement counted Lean's outcome without the prior path's. `measure.py` now compares every outcome
  with the prior path's public outcome. PROBE F2 failed before the fix and passes after it.
- **F3 (B)**, the saved gate was of `9801fe70`, not the reviewed HEAD. This round's instructions forbid running the
  release gate; the final-HEAD gate is the merge train's branch verify. The earlier records are renamed
  `evidence/gate-9801fe70.json` and `gate-full-9801fe70.json` and no longer stand as this HEAD's gate. PROBE F3
  (`git notes --ref=refs/notes/ve-gate show HEAD`) cannot pass before a gate runs on HEAD, so it is not a regression
  test here.

Regression tests: `tests/test_b16e_rights_document.py` (the two probes, the corpus sample and the mutation sweep on
both paths, the three retained-path crashes, the unowned parts, `ownedBeneath`, and the typed and bound fuzz of every
new field).

## Earlier rounds

The release gate of the earlier round ran on `9801fe70`, before any code of this batch: 14,390 passed, 92 skipped and
one test (`tests/test_gate_integrity.py::test_fsmonitor_hook_cannot_hide_edited_source`) failed, then passed on the
same-commit rerun of its file (37 passed), SIGNED by standing ruling R13 (DRI-RULINGS.md) for that commit only.
