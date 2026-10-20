# sc-1ab: the effects on a rule's JSON object (scope@0, Lean core). Build report

No DRI signature is reserved in this item. The one DELTA row (trust budget, +72 lines, K +0) is signed by standing
ruling R16.

- Branch `feature/sc-1ab`, worktree `/home/seyran/code/ve-sc-1ab`, merge base `585794c92`.
- Plan: [scope-PLAN.md](../../spec/scope-PLAN.md), section "SC-1a. Lists and lead-ins: Lean core". Spec:
  [scope.md](../../spec/scope.md), 1.2–1.4, 1.5.2–1.5.3, 4.2, 5.1, 7.1 and 7.4's F7-t. Both are on main, identical to
  `e010fb6aa`. SYNTHESIS 4.1 and 4.2 and DRI-DECISIONS-PHASE2 SC1–SC3 change nothing here.
- Started from `wip/sc-1ab-own` (`b8a4e5255`) and `b2dd5747f`'s order table, as sc-1a's report says. Main had moved
  on (sc-3a merged), so the files were ported onto main, not merged. sc-3a's files (`lean/VE/Layout/`,
  `lean/VE/Discourse/`) are not touched.

## Statement gate

**PASS.** The scope statement review closed with PASS (`scope-p3ver1.final.md`, then `scope-p3ver2.final.md`), which
opened SC-1a. sc-1ab is part of SC-1a.

[statement-diff.txt](statement-diff.txt) (from [evidence/spec_diff.py](evidence/spec_diff.py)) compares each built
declaration with spec 4.2 and 5.1, ignoring whitespace and comments, and theorems up to `:=`:
- **exact (14 of 15)**: the five theorems `substOwn_no_own`, `substOwn_id`, `commutes_symm`, `mergeParts_keys`,
  `mergeParts_conflict`; the definitions `depthLimit`, `Effect`, `members`, `hasOwn`, `depthOk`, `ownSafe`,
  `substOwn`, `narrowing` and `Commutes`.
- **differs (1)**: `mergeParts` reads `lookups lead` and `lookups item`, not `VE.Bridge.fields` (deviation 1).

## Plan rows

| Row (task and plan SC-1a, the effects part) | Status | Where |
|---|---|---|
| `lookups`, `mergeParts` with `mergeParts_keys`, `mergeParts_conflict`, counterfixture `unordered_join` | delivered | `lean/VE/Scope/{Effects,Theorems,Examples}.lean`, `cdf733630` |
| `depthLimit`, `members`, `hasOwn`, `depthOk`, `ownSafe`, `substOwn` with `substOwn_no_own`, `substOwn_id` | delivered | same |
| `Effect`, `narrowing`, `Commutes` with `commutes_symm` and F7-t | delivered | same |
| Fixtures F1-m, F1′, F-own (7.1) and F7-t (7.4) | delivered as `#guard`s and kernel theorems | `lean/VE/Scope/Examples.lean`, section "sc-1ab" |
| Seeded bugs for each | delivered | 16 Lean mutants, below |
| The R16 row | delivered | [DELTA.md](DELTA.md): +72 (the estimate was about +74) |
| `lean/audit.py` and `tools/regen_generated.py --check` pass | delivered | Tests |
| `lean/VE.lean` imports, `lean/SCOPE.md` | delivered | two imports (`[union]` file); a section on the effects |

## Deviations

1. **`mergeParts` reads through `lookups` (sc-1a's deviation 3).** Spec 4.2's text reads `VE.Bridge.fields`, and the
   approved `mergeParts_keys` is false of it: on a raw `Std.TreeMap.Raw` whose keys are out of order, `fields` lists
   a key that `getObjVal?` cannot find, and the joined object then holds it (`unordered_join`, by `decide +kernel`).
   The built definition reads `lookups` (each listed key once, with the value lookup finds), and both theorems are
   proved for every JSON value with their statements unchanged.
   - **No reviewed statement changes**: all five theorems are exact.
   - **What is accepted does not change.** `mergeParts_text` (`Examples.lean`, proved through `lookups_fields`)
     shows `mergeParts` is equal to the spec's text whenever each side is a well-formed object or not an object.
     Lean's JSON parser builds objects only by `insert` (`Lean/Data/Json/Parser.lean`, `objectCore`), and
     `Json.mkObj` builds them by `ofList`, so every object a document can carry is well-formed. sc-1a's builder
     checked this with a `#guard`; it is a theorem now.
   - So the task's "otherwise record it in your REPORT" applies: this is the record, and the FOLLOW-UPS row under
     "## sc-1ab" asks the spec's next revision to take the built text.
2. **Fixtures beyond spec 7.1**, added so that every mutant fails a fixture as well as a proof: `own` as an object
   value and as a key, the depth limit's boundary (`nest 63` passes, `nest 64` does not), `effects_six`,
   `ownSafe` beyond its fuel (in `depth_bound`), and four more `Commutes` cases (a narrowing with an own carve-out, a
   carve-out with a reguard that is not a narrowing, each in both orders).

## Size

The rule is about 600 changed hand-written lines. This item is **about 800**, above it
(`git diff --numstat $(git merge-base HEAD main)`, generated files excluded):
- Lean 486: `Theorems.lean` 286 (sc-1a's builder's proofs, plus 35 for `firstKeys_self` and `lookups_fields`),
  `Effects.lean` 85, `Examples.lean` 113, `VE.lean` 2.
- Tests 28 (`tests/test_scope_lean.py`). Ledgers 50 (`tools/trust-classes.json` 35, `docs/trust-baseline.json` 14,
  `ve/assurance-manifest.json` 3).
- Docs and evidence about 270: `lean/SCOPE.md` 39, `DELTA.md` 19, `mutants.json` 18, `statement-diff.txt` 21,
  `evidence/spec_diff.py` 34, this report.

I did not cut it. The task names this deliverable list, and the proofs (about 60% of the code) were already built.
The only cut that stands alone is the order table (`Effect`, `narrowing`, `Commutes`, F7-t), which would save about
60 lines and still leave the item over 600. If the merge train wants it smaller, that is the cut to make.

## Overlap check

Hand-written files: `lean/VE/Scope/{Effects,Theorems,Examples}.lean`, `lean/VE.lean`, `lean/SCOPE.md`,
`tests/test_scope_lean.py`, `tools/trust-classes.json`, `docs/trust-baseline.json`, `ve/assurance-manifest.json`,
`docs/scope/sc-1ab/*`. Against `git diff --name-only main...<b>` for every `lean-first/*`, `feature/*`, `infra/*` and
`foundation/*` branch:
- `feature/ap-1a` and `foundation/me-1` also edit `lean/VE.lean` (a `[union]` import list).
- `feature/ap-1a`, `feature/ar-10a` and `foundation/me-1` also edit `tools/trust-classes.json` and
  `docs/trust-baseline.json`. These are JSON ledgers, merged by the `ve-generated` driver.
- No other branch touches `lean/VE/Scope/`, `lean/SCOPE.md` or `tests/test_scope_lean.py`.

## Seeded bugs (Lean; [mutants.json](mutants.json))

Each mutant was applied to the committed source and built with `lake build VE.Scope.Examples`, then the source was
restored. Each was also compiled a second way, in a scratch file (never committed) that holds the mutated
`Effects.lean` and the effects fixtures but not `Theorems.lean`, so the fixtures run even when a proof breaks. An
unmutated control raised no error either way. Every new trusted definition has at least one mutant.

| # | Definition | Mutant (claimed behaviour) | Fails (build) | Fails (proofs bypassed) |
|---|---|---|---|---|
| 1 | `Effect` | a seventh constructor (exactly spec 1.3's six effects) | `effects_six` | `effects_six` |
| 2 | `depthLimit` | 65 (the limit is 64) | the `nest` depth `#guard` | same |
| 3 | `members` | always `[]` (an object's values are read) | `members_obj` | `own`-as-value `#guard` |
| 4 | `lookups` | returns `fields` (only what lookup finds) | `lookups_spec` | `unordered_join` |
| 5 | `hasOwn` | `"own"` is not found | `substOwn_id_le` | F-own `#guard`, `own_binder`, `narrowings`, F7-t |
| 6 | `depthOk` | fuel 0 passes (too deep is refused) | depth `#guard`, `depth_bound` | same |
| 7 | `ownSafe` | `exists` is not a binder (ScopeOwnBound) | `own_binder` | `own_binder` |
| 8 | `ownSafe` | fuel 0 refuses (total, refuses nothing beyond its fuel) | `depth_bound` | `depth_bound` |
| 9 | `substOwn` | objects are skipped (`own` inside an attitude node) | `substOwn_no_own_le`, `substOwn_id_le` | F-own `#guard`s |
| 10 | `narrowing` | `C` may mention `own` | `narrowings` | `narrowings` |
| 11 | `Commutes` | two carve-outs always commute (F7-t) | F7-t `#guard` | F7-t `#guard` |
| 12 | `Commutes` | the carve-out/reguard row dropped (symmetry) | `commutes_symm` | F7-t `#guard` |
| 13 | `Commutes` | a narrowing commutes with an own carve-out | `commutes_symm` | mixed-rows `#guard` |
| 14 | `Commutes` | a carve-out commutes with any reguard | `commutes_symm` | mixed-rows `#guard` |
| 15 | `mergeParts` | a conflict overrides (ScopeConflict, F1′) | `mergeParts_conflict`, `mergeParts_keys` | F1′ `#guard` |
| 16 | `mergeParts` | the item's part is dropped (union, F1-m) | `mergeParts_keys` | F1-m `#guard` |

Mutants 8, 13 and 14 survived the fixtures on the first sweep (only a proof, or nothing, caught them), so fixtures
were added for them in `74613eef5` (deviation 2). No Python or Rust product code changed: the Python change is a test
file and the JSON ledgers.

## Trust

Measured on this HEAD with `uv run python tools/trust_map.py --check` against `585794c92`: **PASS**. K +0, S +64,
G[V] +8 untied, trusted **+72**, all in `lean/VE/Scope/Effects.lean`. `Theorems.lean` is P, and the new fixtures are
T. The growth is recorded with `--allow` as `SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-1ab, 2026-10-18`.
Every new trusted definition is used by a theorem
(`tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem`; the check can fail:
`::test_an_effects_definition_no_theorem_uses_is_reported`) and has a mutant that fails (above). The ties-pass row
is in manage-agents FOLLOW-UPS.md under "## sc-1ab (2026-10-19)".

## Tests

- **Lean**: `lake build` (1,040 jobs) has no error, and every `#guard` and kernel fixture holds. `python3 lean/audit.py`:
  PASS, 587 files, 6,667 theorems, only the standard axioms.
- **Generated files**: `uv run python tools/regen_generated.py --check` on `74613eef5`: 31 entries, exit 0.
- **Gate collection**: `tools/gate_collection.py --check --prebuilt`: 3 added, 0 removed, 0 refused, 0 stale, 0
  malformed. No test was removed or renamed: the original `test_a_definition_no_theorem_uses_is_reported` is kept,
  and the effects cases are a new test.
- **Other checks**: `tools/repo_map.py --check` PASS (no mode added); `tools/check_lean_imports.py` kept;
  `tools/relay_mutation_gate.py` 42 routes, 137,740 mutants, 0 failures (review-ready runs it because
  `ve/assurance-manifest.json` changed).
- **Selected tests** (`mac-pytest.sh --select`; locally `select_tests.py` picks 99 of 452 units):
  - The first run, on `93755a6b`, had 1 failure: `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`.
    The three scope files build JSON and had no recorded reason. `bff817534` adds the reasons, and the file then
    passes (137 tests).
  - The final run, on `74613eef5` (clean), on ve-mac-1: 77 of 452 units (the Mac's own test map), exit 0, 0
    failed. It ran the previously failing `tests/test_assurance_manifest.py` first. No test from `main-known-red.txt`
    failed.
- **Full gate**: not run by me, as the task says. The chain runs it on the final HEAD.

## Pilot bytes (estimate)

0 B in both pilots: no route calls the effects yet. The first scope number moves at SC-1b (an estimate of +22 B on
the constitution), after sc-1ac, ar-10a and lf-16g. Nothing is claimed before a pilot audit.

## Next items

- **sc-1ac**: `Reach`, `Governor`, `SDoc`, `applyEffect`, `itemRule`, the reaches (`coveredLayout`, `covered`,
  `frameOn`, `governorsOf`), `admitBlock`, `govern`, the run path `governFast`, spec 5.1's other theorems
  (`itemRule_decoder`, `govern_*`, `governorsOf_iff`, `decodeNorm_name`, `frontier_graph_refused`, `readings_refused`,
  `nonrule_refused`, `governFast_eq`) and 7.1's `govern` fixtures. `applyEffect` uses `substOwn` and `depthLimit` as
  built here. It probably needs its own cut to fit R16 and the size rule.
- **SC-1b** follows after sc-1ac, ar-10a and lf-16g.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** N.A.: no relayed Lean answer, route or response field is added.
2. **Every required deliverable built.** PASS: see Plan rows. There is no Python copy of a Lean decision and no new
   report test. The shared files are a `[union]` import list and the JSON ledgers (Overlap check). Probe:
   `git diff --name-only main...HEAD`.
3. **Tests and gates can fail.** PASS: 16 seeded Lean mutants, each failing a named theorem and a fixture, with an
   unmutated control (`mutants.json`). The R16 check's can-fail test is
   `tests/test_scope_lean.py::test_an_effects_definition_no_theorem_uses_is_reported`.
4. **Python, Lean and Rust agree; valid inputs still pass.** N.A. for agreement: only a Lean implementation exists.
   Valid inputs pass: the pilot's F1-m part and u0173.s01's condition (`#guard`s).
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS as far as I can take it. The tree is committed and clean, and the
   chain runs the full gate on the final HEAD. The evidence commit list is below (`git log --no-merges main..HEAD`).
7. **No unsigned item.** PASS: the one DELTA row cites R16 and meets its conditions (72 <= 150, K +0, itemised,
   exercised, FOLLOW-UPS row).
8. **Every user-visible change in DELTA.** PASS: DELTA.md lists the trust row and says why nothing else is a delta
   (no caller; `mergeParts_text`).
9. **Test selection finds the tests.** PASS: `tools/select_tests.py --base $(git merge-base HEAD main)` selects 99
   of 452 units, including `tests/test_scope_lean.py` and `tests/test_assurance_manifest.py`, plus the Lean build,
   which runs every mutant's failing check.
10. **Lean statements say what is claimed.** PASS: `statement-diff.txt` has 5 of 5 theorems exact and adds no
    hypothesis. Mutants 3, 4, 5, 9, 12, 15 and 16 break the proofs of the claims.
11. **Budgets fail closed.** PASS for the one limit added: `depthLimit` is the fuel of `depthOk`, which refuses a
    condition deeper than its fuel (`depth_bound`, the `nest 64` `#guard`; mutants 2 and 6). The
    `ResourceLimit` text is `admitBlock`'s (sc-1ac).
12. **No CPU or memory regression.** N.A. for the pilots: no route calls the new code. The build cost of
    `VE.Scope.Examples` is about 10 s.
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and 0
    malformed. No test was removed.

## Evidence commit list (`git log --no-merges main..HEAD`, before this report's commit)

```
74613eef5 sc-1ab: fixtures for three survivors of the mutant sweep (Commutes' mixed rows, ownSafe beyond its fuel); 16 mutants
bff817534 sc-1ab: assurance manifest reasons for the three scope files that build JSON
93755a6b2 sc-1ab: lean/SCOPE.md for the effects; DELTA (R16 row)
e178af4fc sc-1ab: boundary fixtures (own as an object value, depth limit, the six effects), saved statement diff and 13 seeded Lean mutants
b734dc972 sc-1ab: trust classes, R16 allowance (S +64, V +8, K +0) and R16 exercised checks for the effects
cdf733630 sc-1ab: VE.Scope.Effects (mergeParts via lookups, own, Commutes) with Theorems and fixtures; regenerate
```
