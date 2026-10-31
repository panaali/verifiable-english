# sc-2c: spec 5.4's remaining SC-2 theorems — build report

Status: **partial, cut by the DRI's decision**. No DRI signature is reserved here. Source HEAD `b7de96453`.
Changed: `own_congr` and `order_refused` are proved exactly as spec 5.4 states them, with fixtures on both sides. F-raw-effect is a built counterfixture to the other five as written.
Open: `reguard_applies`, `restrict_applies`, `carveOut_applies`, `applyEffect_typed` and `commute_applies` are false on a raw rule tree. They go to **sc-2d**, which proves them with `(hw : JsonWF o)`, SIGNED in reviews/dri-decisions-20261031-sc-2c.md item 1.
Pilot: 0 bytes (proofs only); nothing claimed.

## Statement gate and the counterexample

The statement review closed PASS (`scope-p3ver2.final.md`). `tests/test_scope_5_4_statements.py` extends sc-2's check to
the seven theorems:
- the proved `own_congr`, `order_refused` and `listName_run` must equal spec 5.4's text after whitespace normalisation;
- each of the five unproved names must be absent from `Theorems.lean`;
- a changed premise or conclusion must be told apart.

9 passed (evidence/checks.txt).

The effect statements fail on the soft chain. Take a `Std.TreeMap.Raw` rule object that no parser builds, with `guard`
(or `unless`) twice: once where lookup finds it, and once later in traversal. `applyEffect` rewrites the member lookup
finds. `Phases.ruleFields` reads members by traversal, and `Json.mkObj` keeps the last. So every premise holds, yet
`N'.guard = N.guard` (and `N'.carveOuts = N.carveOuts`).

F-raw-effect (`Examples.lean:1180`) checks this. It also shows the norms chain refusing the tree (`exactFields`), and
all three effects as stated on the well-formed rule. I asked the DRI with this counterexample (msg.sh, 06:30Z and
07:13Z). The DRI signed `(hw : JsonWF o)` for the five, as fix (a) for 5.1, and moved them to sc-2d. The spec 5.4 text
update and its DELTA row also go to sc-2d. sc-2c changes no statement.

edits-scope.md: none of its edits is implemented here. Edit 1 (`substOwn` through AT-3a) is sc-2b's; the others edit
other items' plan text.

## Plan rows

| Row | Result |
|---|---|
| `own_congr` | `Theorems.lean:1955`, by `own_congr_le` (:1879): an induction on `substOwn`'s fuel. A guard that decodes is an array that is not a term (`budgetFormula_arr`, `budgetFormula_not_term`), so a scalar or term position is never substituted (`substOwn_scalar`, `substOwn_term`). Under a binder, `ownSafe` gives `substOwn_id_le`. The decoded value does not depend on node count or fuel (`budgetFormula_val`). The lemmas are in `EffectLemmas.lean`. |
| `order_refused` | `Theorems.lean:2021`. `orderCheck_error` (:1970): every throw of the nested loops is `ScopeOrder` (`forIn_error`, `scopeOrder_prefix`). `orderCheck_ok` (:1993): an admitted check leaves no non-commuting pair (`forIn_unit_ok`). |
| `reguard_applies`, `restrict_applies`, `carveOut_applies`, `applyEffect_typed`, `commute_applies` | **sc-2d**, under the DRI's decision; the reason is F-raw-effect. |
| Fixtures, `order_refused` | `Examples.lean:1111-1141`. Refused: the theorem applied to `short [gt, oA, oB]`, whose two reguards meet only on `b`, the last unit. Answers: `ScopeOrder: b: oA, oB`, `ScopeOrder: b: oB, oA` and `ScopeOrder: b: oN, oA`. Admitted: narrowing and own-free carve-out in either order, with the same rule. The `Commutes` table is checked on both sides. |
| Fixtures, `own_congr` | `Examples.lean:1147`. The guards `p(x₀)` and `top` agree at `a` and not at `b`; the own-safe `own ∨ ⊥` agrees exactly where they do. Under `∃` (not own-safe) the guards agree and the conditions do not. At a term position the condition does not decode. |
| Statements dumped | `lean/statements.txt` regenerated. `lean/axioms.txt` gains one line per new declaration, all within `propext`, `Classical.choice`, `Quot.sound`; no new axiom (`lean/audit.py` PASS). |

Reused rather than copied: `substOwn_id_le`, `governorsOf_iff`, `forIn_unit_ok` and `startsWith_append_ascii`.
`commutes_symm`, `lookups_spec`, `mergeParts_keys` and `substOwn_no_own` serve the effect theorems (sc-2d).

## Seeded bugs (docs/scope/sc-2c/mutants.json; each planted alone, then restored)

Some runs stubbed with `sorry` a proof that fails first, so that the build reaches the fixtures; mutants.json lists
which.

| Bug | File | Fails |
|---|---|---|
| reguard keeps the old guard | Govern.lean | F-raw-effect `Examples.lean:1180`, F3/F4 |
| carve-out prepends | Govern.lean | F-raw-effect `:1180` |
| `Commutes` true for reguard with a narrowing | Effects.lean | order `#guard` `:1129`, `Commutes` `:1138`, F7 |
| `orderCheck` skips the last unit | Govern.lean | `orderCheck_ok` (`Theorems.lean:2002`, under `order_refused`); fixture `:1129` (no earlier fixture catches it) |
| `ownSafe` forgets `exists` | Effects.lean | `own_congr_le` (`:1945`); fixture `:1147` |
| `own_congr` gains `(hx : True)` | Theorems.lean | `test_the_proved_statements_are_spec_5_4s_text[own_congr]` |
| `own_congr` loses `hs` | Theorems.lean | `lake build VE.Scope.Theorems` (`:1965`) |

Lean is the only product language changed.

## Validation (evidence/checks.txt)

- **Lean build and audit.** `lake build`: 1182 jobs. `lean/audit.py`: PASS, 684 files, 7650 declarations.
- **Generated files.** `regen_generated.py --write`: 34 entries. `--check`: exit 0, and again after the last edits for
  the entries those edits touch.
- **Trust.** `trust_map.py --check`: K +0, S +0, trusted +0. The new fixtures are `T` in `tools/trust-classes.json`. No
  new trusted definition, so the R16 trust mutants and the FOLLOW-UPS row do not apply.
- **Selected tests.**
  - Run 1 stopped at the audit: `declarations.txt` was stale.
  - Run 2: 405/508 units, 2 failures. Both were the new file missing from `tools/trust-classes.json` and
    `ve/assurance-manifest.json`.
  - Fixed in `1cd8ca688`. The 2 ids then passed on the VM fallback.
- **Other checks.** `gate_collection --check --prebuilt`: 9 added, 0 removed. `repo_map --check`: PASS.
- **Not run here.** The full gate; the chain runs it on the final HEAD.
- **Overlap.** No in-flight `lean-first/`, `feature/`, `infra/` or `foundation/` branch touches these files.

**Size.** 537 hand-written lines before this report and the evidence:
- `EffectLemmas.lean`: 156
- `Theorems.lean`: 170
- `Examples.lean`: 83
- test: 54
- `mutants.json`: 61
- tables: 13

The report and evidence add about 110.

**Spec re-read.**
- `own_congr` against `docs/spec/scope.md:1283`.
- `order_refused` against `:1300`.
- The no-attitude lead paragraph against `:1239-1242`.
- The effect statements against `:1246-1289`, for the counterexample.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer or request decoder changed.
2. PASS: plan-row table above. The cut is the DRI's (dri-decisions-20261031-sc-2c.md item 1); `git diff main...HEAD -- lean/VE/Scope/Govern.lean lean/VE/Scope/Effects.lean` is empty.
3. PASS: mutants.json, 7 seeds, each failing a named check.
4. N.A.: no answer changes; no Python or Rust product code.
5. N.A.: no relayed field.
6. N.A.: the chain runs the final-HEAD gate; the selected runs are in evidence/checks.txt.
7. PASS: DELTA.md is none; trust +0; no reserved signature.
8. PASS: DELTA.md; no definition changed (item 2's diff).
9. PASS: `select_tests.py --paths`: `Theorems.lean` and `scope.md` select `tests/test_scope_5_4_statements.py`; `Govern.lean` selects `lake build`.
10. PASS: `test_the_check_tells_a_changed_statement`; seeds `own_congr_added_premise` and `own_congr_dropped_premise`. The DRI's added hypothesis has its mechanised counterexample, F-raw-effect.
11. N.A.: no budget, limit or deadline code.
12. N.A.: no production computation changed.
13. PASS: `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. PASS: both sides in every fixture (`Examples.lean:1108-1189`); spec re-read above; every claim cites evidence/checks.txt or a line.

Next item: **sc-2d**, the five effect theorems with `JsonWF o`, after this item. Then sc-3b, which the DRI now also puts
after sc-2d.
