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
- **F4 (B)**, a copied `purposes` value had a narrower schema than the rights decoder: the decoder ignores that
  optional metadata. The schema now admits any JSON value for it, while the copied-content binding still requires
  the exact authored value. PROBE F4 failed before the fix and passes after it. Regression:
  `test_f4_copied_ignored_condition_metadata_accepts_every_json_type`.
- **F5 (B)**, rendering an accepted document could crash on a null citation or an absent condition or bar decider.
  Rendering now treats null citations as absent and reads optional deciders with the same absent/default convention
  as the decoder. PROBE F5 failed before the fix and passes after it. Regression:
  `test_f5_optional_rights_metadata_renders_after_acceptance`.

## Recheck verification

The 2026-10-14 DRI note signed the availability and rendering deltas and the V +269 allowance, conditional on final per-file measurement and a retained-loader consolidation follow-up; both are recorded in DELTA.md. F6 now rejects forbidden null members on both paths (`test_f6_closed_rights_content_rejects_forbidden_null_members`). The original F6 probe's assertion that these documents should return successfully conflicts with the later DRI ruling requiring their rejection, so it is replaced by that regression. The final-HEAD release gate remains assigned to the merge train under the same note.

Both F4 and F5 probes passed after the fix; their 13 new parametrized regressions passed, as did the complete
`test_b16e_rights_document.py` selected unit. `lake build`, `python lean/audit.py` (5,254 theorems), the generated
schema check, and the trust-budget check passed. The merge-base selector chose 364/364 mapped units. Its stale
collection and declaration failures passed after regenerating `tools/gate-collection.json` and
`lean/declarations.txt` and rerunning only the failed tests. The unrelated RD-8 report test used Git's variable
short-hash length; it now checks the full hash against the saved prefix, and its failed test passed on rerun.
The English evidence unit timed out in the recorded run but passed all 67 tests alone. The Lean conformance
`test_lean_transitive_axiom_allowlist` hit its 30-minute guard both in the recorded run and alone; the same
`lean/audit.py` command passed outside that test. The selector's final coverage-cache write failed because its
default home cache is read-only here; the test-unit results above were recorded in `/tmp/ve-select-run-w38gpwrj`.

Regression tests: `tests/test_b16e_rights_document.py` (the two probes, the corpus sample and the mutation sweep on
both paths, the three retained-path crashes, the unowned parts, `ownedBeneath`, and the typed and bound fuzz of every
new field).

## Earlier rounds

The release gate of the earlier round ran on `9801fe70`, before any code of this batch: 14,390 passed, 92 skipped and
one test (`tests/test_gate_integrity.py::test_fsmonitor_hook_cannot_hide_edited_source`) failed, then passed on the
same-commit rerun of its file (37 passed), SIGNED by standing ruling R13 (DRI-RULINGS.md) for that commit only.
