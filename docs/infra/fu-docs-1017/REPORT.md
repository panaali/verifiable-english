# fu-docs-1017: wording follow-ups (FAST lane)

No DRI signature needed. No DELTA rows: only comments, docstrings and DELTA prose change, so no user-visible behaviour
changes. `python3 tools/trust_map.py --check` against the merge base `b5248038e` reports K +0, S +0, D +0, G +0,
tied +0, trusted +0.

## Items

| Item | Source | Change |
| --- | --- | --- |
| 1 | fu-lf14c-f4 review F1 | `lean/VE/Core/Layers.lean`: the module docstring's `evaluate`/`countermodel` bullet now says what happens. The FOL projection (no defined predicates) is decoded with its flags checked (`InvalidModel(flags\|literals)`). Then `completeModel` computes every defined table in the one dependency order under one shared budget and checks each biconditional (`InvalidModel(definitions)`). `definitionNodes` says its `fol` argument is always empty. `elaborateNary` says it checks `entries` for one to six arguments (`stepOkFrom 1`). `Layered` says `nary` holds every definition, of any arity. `naryCheck` and `background_fol` say "every definition", not "n-ary". `lean/VE/Norms/Family.lean`: `firstOrderFormula` is also used for definition bodies. `ve/norms.py` `_lean_route`: the n-ary exclusion is gone, since `family_in_scope` takes definitions of any arity. |
| 2 | ties-qs-1 review F1 | `docs/quantities/qs1/DELTA.md`, `VE.Closure.Order` row: no theorem is proposed. `Order` is a plain data type and stays S, as meaning a reader reviews. The restated theorems would add nothing, so the tie would be vacuous. The `Caps` and `admit` rows (`admit_ok_iff`) are unchanged. |
| 3 | ties-jt-crossplan round 1 F4 | `docs/jt-crossplan-fixes/DELTA.md`, conjunct (a): "`d` claims its head" is spelled out as `c.lintHeads.any (·.2 == d.name)`, with the false head-word reading named. The guard reads the same fact through `f.claimed`. Conjunct (c), which had the same ambiguity, now says `!c.lintHeads.any (·.2 == d.name)`, matching `fixedPointTieOf`. |
| 4 | FOLLOW-UPS F2 above "## fu-rd9-checks" | `tools/trust_map.py` module docstring: with a merge uncommitted, the base is the merge base of `main` and the merge being committed. On main that is HEAD itself (the merge train). On a branch syncing main, it is the base the branch will have once the sync is committed. This matches `resolve_base`. |

Generated and pinned files: `lean/declarations.txt` and `docs/spec/assurance-manifest.md` were regenerated with
`tools/regen_generated.py --write`. `ve/assurance-manifest.json` pins `lean/VE/Norms/Family.lean` whole (range
1–505), and `regen_generated.py` says those pins are reviewed by hand. The diff is the one docstring line (469), and the
line count is unchanged, so only the hash was re-pinned. The docstrings keep their line counts because doc-comment
lines count as trusted lines: a first draft measured V +3.

## Checks

- `cd lean && lake build`: passes. `python3 lean/audit.py`: PASS. `uv run python tools/regen_generated.py --check`:
  28 entries checked.
- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, on d3c89ff94): exit 0, 347 units,
  0 failed. They ran on the VM because no Mac slot was free.
- The full gate was not run (FAST lane). The chain and the merge train run it.

## Seeded bugs

No behaviour is claimed, so the task rates seeded bugs as not applicable. To meet the pre-review [mutants] check
anyway, one seed was planted in each changed product language, in a changed file. They are recorded in
`evidence/mutants.json`.

- S1 `ve/norms.py` (`_lean_route` returns False for the family route) fails
  `tests/test_stage2_norms.py::test_lean_family_route_answers_as_the_retained_python_route`.
- S2 `tools/trust_map.py` (`resolve_base` ignores `MERGE_HEAD`) fails
  `tests/test_trust_ratchet.py::test_an_uncommitted_sync_of_main_into_a_branch_is_checked_as_committed`.
- S3 `lean/VE/Norms/Family.lean` (`firstOrderDefinition` ignores the body) fails
  `tests/test_stage2_norms.py::test_a_definition_over_a_ternary_predicate_has_its_premises`, plus the two `-body` cases.
  For this run only, the service was rebuilt and its pin relocked, so the failure is behavioural, not a pin mismatch.
  The lock was restored and the service rebuilt afterwards.

## Left as follow-ups (outside the four items; no edit made)

- `ve/norms.py` `_instantiate` docstring: "until batch 14c moves n-ary scope with a DRI-signed delta" may be
  stale now that the family route takes definitions of any arity. Whether the base expansion should change is a
  behaviour question, not wording.
- `ve/assurance-manifest.json` reason for `lean/VE/Core/Layers.lean` ("decodes definitions and data flags with the
  pinned FOL route decoders over the FOL projection") is stale in the same way as item 1: definitions are decoded by
  the core formula decoder.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer, schema or relay code changed (docstring only in `ve/norms.py`).
2. PASS: every item above maps to commit 545b1a7ae or d3c89ff94. `git diff main...HEAD` touches none of the files
   reserved for ties-fu-1017, tarch-histdep, rd-7 or lf-16f/g.
3. PASS: seeds S1–S3 (`evidence/mutants.json`), each failing a named test.
4. N.A.: no behaviour change. The selected run (347 units) passes.
5. N.A.: no binding code changed.
6. PASS for the FAST lane: the selected tests passed on d3c89ff94. Only this report and `evidence/` come after it.
   The full gate is the chain's and the merge train's.
7. PASS: no DELTA rows and no trust growth (`trust_map.py --check`: K/S/V +0).
8. PASS: no user-visible change. Comments only, and the selected suite passes unchanged.
9. PASS: the selected run on d3c89ff94 (347 units) included `tests/test_stage2_norms.py` (seeds S1, S3). Re-planned
   afterwards, `select_tests.py --base $(git merge-base HEAD main)` selects 82/429 units, including
   `tests/test_trust_ratchet.py` (seed S2) but not `tests/test_stage2_norms.py`. The changes to `ve/norms.py` and
   `Family.lean` are comment-only.
10. N.A.: no theorem or statement changed. `lean/declarations.txt` was regenerated and `lean/audit.py` passes.
11. N.A.: no budget or limit code changed.
12. N.A.: no code changed.
13. N.A.: no test removed or renamed.
