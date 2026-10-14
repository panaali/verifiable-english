# Batch 14a build report

Plan row 14a (LEAN-FIRST-PLAN draft 3): the `definitions@0` surface sugar (`no S is P`,
`every S x that is P, (A)`, `(A) iff (B)`, `define p(x, …) as (A)`) is read and decided by Lean's `parse` mode,
and the Python fallback batch 13b retained for it is deleted in the same batch. One owner: Lean decides
acceptance, the diagnostic and the document; Python only constructs the document after Lean accepts, and must
agree with Lean or the parse is `CheckerUnavailable`.

## Size

* **Deleted:** 39 lines of `ve/parser.py` (8 added): the `definitions@0` branch of `_parse_lean`,
  `_parse_python_marked`, the `_Parser.sugar` mark and the `definitions_sugar` exception tag. Mapped site by site in
  [LEDGER.md](LEDGER.md).
* **Lean added:** 416 lines (122 deleted) in 9 product files (`Surface`, `Closure/Surface`, `Core/Surface`,
  `Service/ParseDiagnostic`, `Service/Standalone`, the round-trip and proof files that follow the signatures).
  Trusted lines V 37,154 → 37,451 (R6, `docs/trust-baseline.json`); 25 new declarations classified in
  `tools/trust-classes.json`.
* **Tests:** `tests/test_lean_first_b14a.py` (250 lines, new), `tests/test_stage2_parse.py` (+17/−8). Rust unchanged.

## Gate 5.1 evidence

All in [DELTA.md](DELTA.md) and `evidence/`: corpus A/B 65,772 records, 0 unlisted (base and head recordings
byte-identical); sugar corpus 760 records, 350 wording (W1, R1), 0 unlisted; difffuzz `--ci` + `--deep 1` over 14
seeds, 0 head-only signatures, baseline 250 entries on both sides (does not grow); latency within section 4's
budgets (C1, R4); relay mutation gate: the `parse` route has no failure, the 133 failures are identical at base
and head (`main`'s). Every DELTA row is signed by a standing ruling (R1, R4, R6, R7); none needs a DRI signature.

The full release gate runs once, as the last step, on the commit that adds this report; its result is kept as
`gate-result.json` in the worktree (no later commit, so the gate's commit is HEAD).

**First full gate (1e44780b): failed on 3 tests outside the batch.** 14,566 passed, 92 skipped, 36 Rust passed;
the failures were `tests/test_gate_integrity.py::test_interrupted_gate_cannot_record_pass[KeyboardInterrupt|TypeError|AttributeError]`,
and `--rerun-failed` on the same commit failed them again. Cause: inside the gate `HOME` is the gate's scratch
directory, so the unpatched `lake_outputs.drop_stale` in that test cannot find `lean`
("lean is required to check Lake's executables against their traces") and the gate records a failure instead
of re-raising the interruption. The bug is already in the merge base, since none of `tools/gate.py`, `tools/lake_outputs.py`
and the test change on this branch, and `main` fixed it in 0341684a (AR-5a). That 2-line test-only commit is
cherry-picked here unchanged (`-x`). With it, the three tests pass in a gate-like environment (`env -i`, scratch
`HOME`) and the whole file passes (37). A gate started before that with `-n auto` got a single worker under host
load ≈80 and was stopped unfinished after 5 h, with no result. The gate run on 2fafd411 also left no result:
its `gate-result.json` is the placeholder an interrupted gate writes (`status` failed, empty `commit_sha`, no
stages), so no full gate has passed or failed on the cherry-picked fix yet. The chain's gate on the final HEAD is the
record; the resumed session (2026-10-14) ran only `lake build` and the three affected test files
(`tests/test_lean_first_b14a.py`, `tests/test_stage2_parse.py`, `tests/test_gate_integrity.py`) on it, not the
365-unit selection, which is the whole suite.

## Seeded bugs

`evidence/mutants.json`: M1 (Lean, `lean/VE/Service/Standalone.lean`), M2 (Lean,
`lean/VE/Service/ParseDiagnostic.lean`), M3 (Python, `ve/parser.py`), M4 (Lean, `lean/VE/Core/Surface.lean`); each
made its named test fail and was restored.

## Not run, recorded

* Base-side A/B of the UDHR whole-translation input exceeds 8 GB (U2, R7); not retried.
* The rights, discourse and quantity corpora were not recorded (no `definitions@0` surface text; DELTA.md item 2).
* Environments outside Lean's `parse` scope (statement layers, W6 units) keep the Python sugar reader: 13b's scope
  gap 5, FOLLOW-UP outside 14a.

## Self-review against BUILDER-CHECKLIST

Plan row (draft 3, 14a–d): "**Stage 2c gaps**, one batch each: `definitions@0` sugar; … | the four extensions |
the Python fallback branch 13b retained for it". Lean extension: 6d05bf52 (`Surface`, `Core/Surface`,
`Closure/Surface`, `Standalone`, `ParseDiagnostic`), test `test_sugar_is_read_by_lean_as_python_read_it`.
Deleted fallback: 6d05bf52 (`ve/parser.py`), test `test_the_retained_sugar_reading_is_deleted`. Callers switched:
`parser._parse_lean` asks Lean for every source, test `test_definitions_sugar_is_leans`. Gate 5.1: cb685f21
(DELTA.md, `evidence/`). Inventories regenerated with `tools/regen_generated.py` (10f101e1, R12).

1. Lean answers typed and contained: PASS. The `parse` response schema is unchanged (sugar only widens which
   sources Lean accepts). Relay mutation gate `service:parse`: 326 mutants, 0 failures at head
   (`evidence/relay-gate-head.txt`). Wire row: `test_lean_answers_sugar_on_the_wire`.
2. Deliverables built, no rule broken: PASS. See the rows above. There is no new Python copy of a Lean decision:
   Python only constructs the document after Lean accepts and must equal it (`test_metadata_still_comes_from_the_python_constructor`,
   M3). No new permanent report test (D4/R11): `tests/test_lean_first_b14a.py` tests behaviour only.
3. Tests and gates can fail: PASS. M1–M4 in `evidence/mutants.json`, one per behaviour, in Lean and Python (Rust unchanged).
   Each mutant fails a behaviour test, not a hash or build step.
4. Python, Lean and Rust agree: PASS. Corpus A/B gives 65,772 records with 0 unlisted, and the sugar corpus 760 records
   with 0 unlisted (`evidence/corpus-ab.json`, `evidence/sugar-ab.json`). Reordered keys and generated names:
   `test_reordered_environment_keys_and_generated_names_get_the_same_answer`. 3-argument predicates:
   `test_binary_and_nary_definitions_bind_arguments_in_declared_order`.
5. R8 binding: PASS. `parse` answers carry no ids or names that Python reads back. Python checks Lean's AST and
   canonical text for equality with its own document, or the parse is `CheckerUnavailable` (M4 caught by
   `test_sugar_is_read_by_lean_as_python_read_it[family2]`). For undeclared input names:
   `test_sugar_needs_the_definitions_profile`, and the UnknownSymbol fixtures in `REJECTED` (M2).
6. Gate evidence matches the final HEAD: PASS. The chain runs the full gate on the committed final HEAD
   (`gate-result.json`). The branch is not synced with `main`: the merge base `f1b719c7` is the A/B base, and
   `main` has 206 later commits. None of them touches `ve/parser.py` or the five Lean surface files this batch edits.
   Syncing is the merge train's job. The evidence names `f1b719c7` as its base.
7. No unsigned item: PASS. Every DELTA row is signed (W1 R1, U1/U2 R7, C1 R4, T1 R6). None needs a DRI signature.
8. Every user-visible change is in DELTA: PASS. W1 has 350 records, checked per record by `sugar_ab.py compare`.
   The base and head pilot and corpus recordings are byte-identical.
9. Test selection: PASS. `select_tests.py --base f1b719c7` selects 365/365 because `lean/VE/Surface.lean` is
   imported by `ve_service`, and the static graph has nearly every unit running it. The cause is real, not an
   unlayered directory. The selection contains `tests/test_stage2_parse.py`, which fails under M3.
10. Lean statements: N.A. No new theorem. The existing round-trip statements (`parse_print`,
    `parse_print_propositional`) are unchanged; only their proofs unfold the new `parseWith`.
11. Budgets, limits, deadlines: N.A. No budget, limit or deadline is added. `parse` keeps the service's
    existing request limits.
12. No CPU or memory regression: PASS. `evidence/latency.json`: the service stays under 1 ms CPU per call on both
    sides (C1). No enumeration or per-candidate Lean call is added; each source is one `parse` request, as in 13b.
    The pilot recordings are identical, and UDHR whole-translation exceeds 8 GB at base and head alike (U2).
