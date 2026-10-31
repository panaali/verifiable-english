# sa-nd-atoms: an explicit atom list and open-name list in `NormDefaults/Evidence.lean`

DRI signature needed: none (DELTA has no rows; trust growth is 0 lines). The builder asked the DRI decider through
msg.sh whether DF-5, JT-4, AA-1 and WG-6 may rely on the four new general statements as built. Answer,
`reviews/dri-decisions-20261031-sa-nd-atoms.md` item 1: they may, with no separate statement review, as long as
lean_statements stays at 0 removed and 0 changed, audit passes, the approved instances stay derived from them and the
`atoms`/`opens` #guards stay. Item 2 accepts the `sa-nd-atomsb` split, and WG-6 is blocked by it.

Implements synthesis round 2 edit 1 for norm-defaults (`debates/plan-synthesis-2/edits-norm-defaults.md`, C10;
SYNTHESIS row "Three-valued completion and enumeration"). Edits 2 and 3 are plan-text edits and are not this item.
Base `09fca5013`. Statement gate: the edits are DRI-decided (DECISIONS item 2).

## Delivered

| Plan line | Where | Evidence |
|---|---|---|
| `atoms`: an explicit list of ground atoms to enumerate (DF1) | `enumerateSettledO U M opens atoms n vs`, `Evidence.lean:1029`; the size `atoms.length` is charged against `MAX_UNSAID_ATOMS` | `Examples.lean:172-197` |
| `opens`: an explicit list of open predicate names (JT-R1) | `atomVO:340`, `tabKO:395`, `table3O:407`, `coneEvalO:875`, `openInstancesO:918`, `coneOfO:927`, `coneAtomsO:935`, `coneAtomVO:964`, `coneValuesAtO:972`, `coneValuesO:979` (helpers `pairRuleO`, `stepEntryO`, `closeRuleO`, `coneAtomO` replace their unused legacy names) | `Examples.lean:187-191` |
| Today's functions are the instances (`opens = unsaidNames U`, `atoms` the cone), by `rfl` | `atomV`, `tabK`, `table3`, `coneEval`, `openInstances`, `coneOf`, `coneAtoms`, `coneAtomV`, `coneValuesAt`, `coneValues`, `enumerateSettled` are one-line instances; `*_eq_open` lemmas (`table3_eq_open:423`, `coneAtoms_eq_open:960`, `enumerateSettled_eq_open:1038`, ...) are `rfl` | `lake build`: Build completed successfully (1187 jobs) |
| General soundness, the approved theorems re-proved from it with unchanged statements | `tabKO_sound:503`, `table3O_outcome:687` (any `R` that agrees with `M` off `opens` and is `BaseAdmissibleU`), `denote_of_coneValuesAtO:1060`, `enumerateSettledO_sound:1107` (any `R` off `opens` satisfying `Fill_T`; any atom list). `perm_of_req`, `notreq_of_notperm`, `gap_of_kleene`, `canonO`, `tabK_sound`, `table3_outcome`, `denote_of_coneValuesAt`, `enumerate_all`, `settled_of_enumeration` are now wrappers over them | `python3 tools/lean_statements.py --check`: "removed: 0 / changed: 0 / PASS: 7204 statements"; `python3 lean/audit.py`: PASS, 7773 theorems |
| #guards: a strict subset of the cone, an atom outside it, an `opens` list, each beside today's answer | `Examples.lean:166-197`: `[]` against u12's cone (`none` vs `some true`); `y_permitted(a1)`, never in the cone (alone `none`; with the cone 4 assignments, `some true`); `opens` with base `c` in uBetween (`table3O`/enumeration `none` where `table3` is `some true`; the cone gains `c(a)`) | build above |
| Size charged against the existing limit, a large well-formed request ending within it | 12 of u12/m13's 13 atoms: 4,096 assignments, `some true`; all 13: over the limit, `none` (`Examples.lean:195-197`) | build above |
| Legacy outputs byte-identical, a saved comparison | `byte-identity.json` (by `byte_identity.py`, base and branch `ve_service`): "62 of 62 answers identical"; the cases cover status, report, certificate, conflict and gaps kinds | file |

Not delivered (not in edit 1; weighing-PLAN 3.4 sketches them for WG-6): `X` (extra premises the enumeration
prunes against), a `budget` parameter and a `fixed` record on `enumerateSettledO`. Named `sa-nd-atomsb`, for WG-6's
statement review to fix the types. `Packs.lean`, `Layered.lean` and every consumer are untouched.

Spec re-read: `atoms` / `opens` wording and "instances by `rfl`, byte-identical" against edits-norm-defaults.md:7-16;
names (`enumerateSettledO` with `atoms` after `opens`, `coneAtomsO`, `table3O`, `<name>_eq_open`) against
weighing-PLAN 3.4 (`reviews/fidelity-pilot-20261030c/definitions/plans/weighing-PLAN.md:703-726`). Deviation:
`coneAtomO`, `coneEvalO` and `coneAtomVO` take no `U` (unused once `opens` is a parameter).

## Size, trust, bytes

Hand-written lines (`git diff --numstat 09fca5013`): Evidence.lean +348/-163, Examples.lean +33, trust-classes.json
+20/-4, byte_identity.py +45, mutants.json +56, DELTA.md +8, this report: about 560 added. `byte-identity.json`
(319) is the script's output. Trust (`python3 tools/trust_map.py --check`): "K +0, S +0, D +0, G +0, ... trusted +0;
PASS". The new definitions are class C like the functions they generalise; the proof-local notation `MR` is P. R6
and R16 therefore record no lines. Pilot bytes expected to move: 0.

## Seeded bugs (Lean; `docs/norm-defaults/sa-nd-atoms/mutants.json`, each restored)

| Definition | Bug | Fails |
|---|---|---|
| `atomVO` | `p ∈ opens` read as `p ∈ unsaidNames U` | proof `tabKO_sound`, Evidence.lean:527 |
| `enumerateSettledO` | `atoms` ignored, the cone enumerated | proof `enumerateO_all`, Evidence.lean:1048 |
| `enumerateSettledO` | limit `> MAX_UNSAID_ATOMS + 1` | #guard Examples.lean:197 |
| `coneAtomO` | only the first open name read | #guard Examples.lean:189 |
| `coneValuesAtO` | assignments `Fill_T` refutes kept | #guard Examples.lean:65 |
| `coneAtomVO` | assigned atom negated | proof `denote_of_coneValuesAtO`, Evidence.lean:1077 |
| `table3O` | one layer symbol short | #guard Examples.lean:37 |

The three proof failures are the soundness theorems refusing an unsound definition. No Python or Rust product code
changed. The comparator `byte_identity.py` fails on a changed digest and on empty input and passes head against head
(probe with stubbed digests: exit 0, 1, 1).

## Tests

`zsh mac-pytest.sh --select -- --base 09fca5013 --run` (Actions gave no result; Mac path): "summary: ran on
ve-mac-1 (aarch64) ... HEAD f26e0cfc + uncommitted changes (only this report); 8972s; exit=0; failed/error ids=0";
400 units selected and run, 0 failed. Pre-existing main-known-red tests: none touched.
While iterating: `lake env lean` on Evidence.lean and Examples.lean, then `lake build` once ("Build completed
successfully (1187 jobs)") and regen (`regen_generated.py --write`, run again once after a one-line wrap fix).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer or schema changes (no route, no Python).
2. PASS: the Delivered table above; the cut is named `sa-nd-atomsb`. Rule grep: no Python copy, no report test, in-flight branches share only the side tables (merge driver).
3. PASS: seven seeded bugs, each killed (mutants.json); the comparator fails both ways (probe above). Trust mutants N.A.: trust growth 0.
4. PASS: base and head `ve_service` side by side on the norm-defaults corpus, 62 of 62 identical (byte-identity.json).
5. N.A.: no field read from a Lean answer is added.
6. PASS: no gate run here (the chain runs it on the final HEAD); evidence names base `09fca5013` and is saved.
7. PASS: no DELTA rows, trust +0; the DRI question is listed in the first lines.
8. PASS: DELTA "none", backed by the empty diff of byte-identity.json.
9. PASS: `tools/select_tests.py --base 09fca5013` selects 400 of 511 units, including tests/test_norm_defaults*.py.
10. PASS: lean_statements --check 0 changed; seeded definitions break the general proofs (rows 1, 2, 6).
11. PASS: over-limit atom lists give `none` (UNKNOWN), Examples.lean:197; the limit bug is caught.
12. PASS: the instances pass `unsaidNames U` once instead of rebuilding it per atom; no new enumeration (12-atom guard ends at build time).
13. N.A.: no test removed or renamed.
14. PASS: both directions in each fixture group (today's answer and the changed one); claims cite commands; spec re-read above.

Next item: DF-5 (defeasible, the first consumer), then JT-4 and AA-1; WG-6 consumes it.
