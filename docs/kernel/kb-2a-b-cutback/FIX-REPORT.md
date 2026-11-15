# kb-2a-b-cutback F1 fix

**Status:** F1 fixed; no DRI signature reserved. Code commit `010c493e53`. The two routing ties now name the
`environmentOf` refusal sites and their exact conditions on lowering profiles. No answer or fault-order change is
intended. The full gate was not run here; the merge train owns it.

F1 -> extract the two existing Lean refusal checks into `judgmentSoftRefusal` and `softReadingsRefusal`, prove their
conditions in `routed_sites`, and tie both `routed` and `routedRefusals` to it ->
`tests/test_trust_budget.py::test_core_routing_ties_name_both_environment_refusal_sites` -> `010c493e53`.

The existing approved `routed_iff` and `routedRefusals_sites` statements were not changed. `routed_sites` includes
`routed_iff`'s exact `environmentOf` outcome and two equivalences: on profiles with lowering rows, the first helper
returns the judgment/soft refusal exactly for an exception-conditioned unit with `soft-norms@0`, and the second
returns the soft/readings refusal exactly for `soft-norms@0` with `readings@1`. `environmentOf` calls those helpers
at its original sites, so earlier faults keep precedence. The regression test checks the compiled statement
inventory, both tie entries, and the calls in `environmentOf`.

**Probe F1:** the review's command exited 1 before the fix, printing `VE.Service.CoreCheck.routed`; it exited 0
after the fix. The regression test passed alone and in the selected run.

**Seeded Lean bug:** in `lean/VE/Service/Document.lean`, replacing the `readings@1` condition in
`softReadingsRefusal` with `false` made `lake build VE.Service.CoreCheckProofs` fail at
`softReadingsRefusal_site` (`unsolved goals`, exit 1). The source was restored and the full `lake build` passed.
Only Lean product code changed; no Python or Rust product mutation was due.

**Checks:** `lake build` passed on the restored tree (1475 jobs); `python3 lean/audit.py` passed (896 files, 10116
theorems, allowed axioms only); `tools/trust_map.py --check` passed with zero unclassified lines and trusted -229
against b6cbafe80a60. The saved `trust-after.json` measures 3133 -> 2904 trusted lines across the eight files.
The generated theorem and assurance entries passed their freshness checks after regeneration. The assurance
manifest's full-file pin for `Document.lean` was reviewed and updated to 3130 lines, with its hash and total.

The selected command (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`) stopped at
`test_assurance_manifest.py` because the source pin still had the old hash and range: two assertions failed.
The other completed selected units, including `test_trust_budget.py`, passed. After updating the pin, the two
failed IDs passed (2 passed), and the dependent `test_trusted_decoder_line_ranges_are_pinned` passed (1 passed).
The selector was not repeated on code it had already passed. No release gate or full suite was run.

The three cases in `main-known-red.txt` are pre-existing main failures and were neither edited nor treated as F1.
`DELTA.md` records no user-visible change; its generated-inventory row cites R12 (DRI-RULINGS.md).
