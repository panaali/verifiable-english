# sa-nd-atomsb: `X`, `budget` and `fixed` for nd-atoms' enumeration

Status: built, ready for the gate. HEAD: the last commit on feature/sa-nd-atomsb (base `e63bae651`).
What changed: `lean/VE/NormDefaults/Evidence.lean` gains `enumerateSettledX U X M opens atoms budget fixed n vs`
(weighing plan 3.4's shape), its soundness theorem, and today's `enumerateSettledO` and `coneValuesAtO` as its
instances; 11 new `#guard`s in `Examples.lean`. No statement changed, trust +0, bytes 0, DELTA none.
Open items: none. No DRI signature is needed or reserved. Next item: wg-6 (it also waits for wg-3).

## Plan rows and directive lines

| Row (task deliverable, plan or DRI condition) | Delivered by | Evidence |
|---|---|---|
| (1) the parameterised enumeration, with `X`, `budget`, `fixed` | `enumerateSettledX` Evidence.lean:1065; `coneValuesAtX` :980 prunes against `X ++ fillPremises U`; `coneAtomVX` :970 reads `fixed` first; `freeAtoms` :1055; `none` when the free atoms exceed `budget` | #guards Examples.lean:211-244 |
| Name choice: the old `enumerateSettledO` keeps its signature (its soundness statement is approved and must stay unchanged), so the new one is `enumerateSettledX` (X for extra premises, as weighing's `BaseAdmissibleX`); `enumerateSettledO` is now `enumerateSettledX U [] M opens atoms MAX_UNSAID_ATOMS []` :1074 | `enumerateSettled_eq_X` :1094 states the plan's line (`… 12 [] n vs`) by `rfl` | `lake build` (below) |
| Legacy definitions unchanged | `coneValuesAtO_eq_legacy` :1005 and `enumerateSettledO_eq_legacy` :1079: the instances equal sa-nd-atoms' bodies by `rfl` | `lake build` |
| (2) general soundness, the old theorems as instances, statements unchanged | `denote_of_coneValuesAtX` :1123 (for any `R` that agrees with `M` off `opens`, with `fixed` on its atoms, and satisfies `X ++ Fill_T`); `enumerateSettledX_sound` :1194. `denote_of_coneValuesAtO` :1174, `enumerateSettledO_sound` :1208 and `enumerateO_all` :1108 are now one-line instances at `X = []`, `fixed = []`, `budget = MAX_UNSAID_ATOMS` | `python3 tools/lean_statements.py --check`: "added: 0 removed: 0 changed: 0 … PASS: 7296 statements" |
| `tabKO_sound`, `table3O_outcome` | unchanged: `tabKO`/`table3O` have no enumeration, and plan 3.4 gives `X`, `budget` and `fixed` to `enumerateSettledO`/`coneValuesO` only. They stay sa-nd-atoms' general statements | statements check above |
| No `sorry`, no new axiom | the 6 new theorems use `propext`, `Classical.choice`, `Quot.sound` only (`lean/axioms.txt`) | `python3 lean/audit.py`: "PASS: 707 source files; 7869 named theorem declarations audited" |
| (3) #guards, each with a fixture on both sides | `X` settles u6's `y_permitted(a)`, UNDECIDED today, yes or no (:209-215); `fixed` settles it (:217) and is read at its own tuple (:223, m2); budget boundary 1 → `some true`, 0 → `none` (:226, :228); 13 atoms with `a1` fixed fit budget 12 (:232-233), all 13 unfixed do not (:197) | `lake build VE.NormDefaults.Examples` |
| (4) the evaluator rule (reviews/dri-decisions-20261027-me-12-n1.md) | `enumerateSettledX` computes the free atoms once (`let C`) and charges their number against `budget` before any of the `2 ^ budget` assignments is built; `coneValuesAtX` computes `X ++ Fill_T` once (`let P`), and each assignment evaluates each premise and the outcome once. Fixture: 100 atoms, 88 fixed, 4 premises that read fixed atoms: 4,096 assignments, `some true`; with 87 fixed, `none` before any assignment (:241-246). Budget 0 gives `none` (:228) | `lake build VE.NormDefaults.Examples` (Examples builds in 12 s, `time` of that build) |
| (5) byte identity, saved | `byte-identity.json`: 62 of 62 `norm-defaults` route cases identical, base `e63bae651` vs branch `828a45789` (the commits after it change only `Examples.lean`, the trust side table and docs). `byte_identity.py` runs sa-nd-atoms' comparator, its one owner | `uv run python docs/norm-defaults/sa-nd-atomsb/byte_identity.py …`: "62 of 62 answers identical" |
| (6) seeded bugs | 8 Lean mutants, below and in `mutants.json` | `lake build VE.NormDefaults.Examples` per mutant |
| Files: no edit to Packs.lean, Layered.lean, PacksExamples.lean, PacksLegacyExamples.lean or a consumer | the diff touches Evidence.lean, Examples.lean, generated files, `tools/trust-classes.json` and this directory only | `git diff --stat $(git merge-base HEAD main)` |
| No in-flight branch edits these files | checked at the start over `lean-first/* feature/* infra/* foundation/*` | `git diff --name-only main...<branch>` over each: none |

Spec re-read: "`coneValuesO` prunes the assignments that Kleene evaluation refutes against `X ++ Fill_T`" and
"Over `budget` atoms not fixed by `fixed`, `none`" against weighing-PLAN.md@bda82d18c:714-718; the shape
`enumerateSettled_eq_open … = enumerateSettledO U [] M (unsaidNames U) (coneAtoms U M n vs) 12 [] n vs` against
:721-722 (here `enumerateSettled_eq_X`); "fixed: a record of atoms with given values" against weighing's
`AdmissibleCompletion` (:744-748), which `hfix` restates; edits-norm-defaults.md edit 1 (`atoms`, `opens`, the
instances by `rfl`, byte-identical); DRI 2026-10-31 items 1 and 2 (statements unchanged, budget under the evaluator rule).

## Seeded bugs (Lean; `lean/VE/NormDefaults/Evidence.lean`; each planted alone, then restored)

Where a soundness proof fails first, the mutant is planted again with the affected proofs replaced by `sorry` for
that run only, so the named `#guard` is shown failing as well.

| Definition | Mutation | Proof that fails | #guard that fails (Examples.lean) |
|---|---|---|---|
| `enumerateSettledX` | fixed atoms counted: `C.length > budget` → `atoms.length > budget` | none (sound) | :233 (13 atoms, `a1` fixed, budget 12), :244 |
| `coneValuesAtX` | `X` ignored: `X ++ fillPremises U` → `fillPremises U` | `denote_of_coneValuesAtX` | :211 (`X = [y(a)]` settles u6) |
| `enumerateSettledX` | off by one: `>` → `≥` | `enumerateSettledO_eq_legacy` | :226 (budget 1), :196, :233 |
| `coneAtomVX` | fixed atom found by name only: `e.1 = (p, vs)` → `e.1.1 = p` | `denote_of_coneValuesAtX` | :223 (m2 per-tuple fixture) |
| `freeAtoms` | fixed atoms not removed | none (sound) | :232, :233, :241 |
| `coneValuesX` | `fixed` dropped (`[]` passed) | `enumerateSettledX_sound` | :217, :223 |
| `enumerateSettledO` | instance budget `MAX_UNSAID_ATOMS + 1` | `enumerateSettledO_eq_legacy` | :197 (13 atoms at today's budget) |
| `coneValuesAtO` | instance with `X = [.bottom]` | `coneValuesAtO_eq_legacy` | :180, :195 |

The `coneAtomVX` mutant survived the guards at first; the m2 fixture (:221-224) was added for it. A first
`freeAtoms` run ran out of memory at a guard that called `coneValuesX` without the budget; that guard now checks
the free-atom count first (:241). No Python or Rust product code changed. The comparator was probed with stubbed
digests: head against head exit 0, a changed digest exit 1, empty input exit 1.

## Size, trust, bytes

Hand-written lines (`git diff --numstat $(git merge-base HEAD main)`, generated files excluded): Evidence.lean
+132/-31, Examples.lean +50, trust-classes.json +13, byte_identity.py +21, mutants.json +70, DELTA.md and this
report about 110: about 430. Trust: `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0,
unclassified +0, trusted +0 … PASS". The five new definitions are class C (checked executables) like the
functions they generalise, and the new fixtures are T, so R6 and R16 record no lines, no `--allow` row is needed
and there is no ties-pass row to file. No new trusted definition exists; the mutants above still cover every new
and replaced definition. Pilot bytes expected to move: 0 (no route reads the new parameters).

## Tests

- `lake build` (all of `lean/`): "Build completed successfully (1211 jobs)".
- Selected tests, once on the finished code (`zsh mac-pytest.sh --select -- --base e63bae651 --run`, tree of
  `d4fa31a79`): "summary: selected tests ran on the Claude cloud (6 shards, run sa-nd-atomsb-d4fa31a7-t504814);
  exit=0"; shards 1-6: 74, 73, 74, 67, 65 and 51 units, all passed (404 units, 0 failed).
- Pre-existing failures on main (main-known-red.txt) are not touched here.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer, schema or route changed.
2. PASS: the plan-row table above, each row with its evidence; no Python copy of a Lean decision, no report test.
3. PASS: 8 Lean mutants, each killing a named #guard (`mutants.json`); comparator probe exit 0/1/1.
4. PASS: base vs head on the 62 norm-defaults route cases, `byte-identity.json` 62 of 62.
5. N.A.: no Lean answer is read by Python in this item.
6. PASS: generated files only through `uv run python tools/regen_generated.py --write`; the gate runs on the final HEAD.
7. PASS: DELTA none, trust +0 (`trust_map.py --check`); no unsigned row.
8. PASS: DELTA.md "None", backed by `byte-identity.json` and the `_eq_legacy` theorems.
9. PASS: `uv run python tools/select_tests.py --base e63bae651` selects the norm-defaults suites (tests/test_norm_defaults*.py), not every unit.
10. PASS: `python3 tools/lean_statements.py --check` 0/0/0; the mutants break `denote_of_coneValuesAtX`, `enumerateSettledX_sound` and the `_eq_legacy` theorems.
11. PASS: budget 0 gives `none` (Examples.lean:228); over budget is `none`, never a value.
12. PASS: the enumeration is bounded by `budget` before it is built; the large-request fixture ends in the Examples build (12 s).
13. N.A.: no test removed or renamed.
14. PASS: both directions in every guard (settles / stays UNDECIDED; within / over budget; fixed counted / not); spec re-read above.
