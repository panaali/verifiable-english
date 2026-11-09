# pe-1b DELTA

No user-visible delta. Nothing calls the new code, so no answer, verdict, code, text, path or byte changes.
`check` gains a refusal (step 6a), but no route decodes a `purposes` block or builds `Units` from a document until
PE-2. Evidence: `grep -rln "VE\.Purposes\|VE/Purposes" lean/VE lean/*.lean ve rust tools` outside
`lean/VE/Purposes/` finds only the generated `lean/VE/Audit.lean` and `lean/VE.lean`. `git diff --stat
$(git merge-base HEAD main) -- lean/VE/Route/ lean/VE/Service/ ve/ rust/` is empty.

The one row below itemises the trusted-base growth under R16. It was measured on the final Lean with
`uv run python tools/trust_map.py --check`, which prints "against 0f9fc890970e: K +0, S +12, D +0, G +21, tied +23,
unclassified +0, trusted +12 … PASS: K, S and untied [V] within 0f9fc890970e and the allowances introduced since".

| # | File | Trusted lines (class, declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Purposes/WellFormed.lean` | S +12. The fields `Part.readings` (+1) and `Units.packSources` (+1), `targetKind` (+7) and `holdsTarget` (+3), each counted from its docstring to the next declaration. `WellFormed` gains the `packsInert` conjunct in place, so its line count does not change. Tied, so not counted (G[V], `tools/trust-classes.json`): `packsInert` (`packsInert_iff`, `packsInert_nil`), `shownUnder` (`shownUnder_iff`) and `unlinkedActive` (`unlinkedActive_iff`). `check` is C, tied by `check_ok_iff`. K +0; 12 ≤ 150. | `trust-mutants.json`, which exits 0: `targetKind` and `holdsTarget` 4 KILLED; `WellFormed`'s 18 mutants are ALLOWED, and each breaks `check_ok_iff` and a `wf` #guard. In `mutants.json`: P3, H5 and H8 (`targetKind`), H4 (`holdsTarget`), H7 (`WellFormed`); for the tied definitions, P1 and P2 (`packsInert`), H3 (`shownUnder`), P4, H1 and H2 (`unlinkedActive`), H6 and H9 (`check`). The allowance is in `docs/trust-baseline.json`. The ties-pass row is under "## pe-1b" in FOLLOW-UPS.md | R16 |
