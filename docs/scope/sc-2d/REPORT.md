# sc-2d: spec 5.4's five effect theorems with `(hw : JsonWF o)` — build report

Status: **done**. All five are proved, with no `sorry`. No DRI signature is reserved: the premise is SIGNED (reviews/dri-decisions-20261031-sc-2c.md item 1), and the size override is SIGNED (reviews/dri-decisions-20261101-sc-2d.md item 1).
Changed: `reguard_applies`, `restrict_applies`, `carveOut_applies`, `applyEffect_typed` and `commute_applies` (`lean/VE/Scope/Theorems.lean:2152-2306`), now equal to spec 5.4's text; condition (ii) `baseObj_jsonWF` (:2382).
Open: none. Pilot: 0 bytes (proofs only); nothing claimed. Next: sc-3b, once its addendum is approved (edits-scope.md item 2).

## Plan rows (task deliverables 1-6 and the DRI's conditions)

| Row | Result |
|---|---|
| (1) The five theorems, with `hw` | `Theorems.lean` section `Effects`. On a well-formed rule object, lookup and traversal see the same single member, so the decoder reads the member `applyEffect` rewrote. `decodeNorm_view` (:1998): W1's view of the rule has the rule's own W1 members. `decodeNorm_same` (:2060): two rules that differ only in `guard` and `unless` differ only in guard and carve-outs. `decodeNorm_effect` (:2048): the guard and each carve-out are their members' `decodeBudgeted` values. The decoder lemmas are in `EffectLemmas.lean`: `normFields_spec` (:262), `w1_spec` (:291), `ruleFields_spec` (:319), `forIn_carve` (:240), `budgetFormula_mono` (:156; a shared node count only lowers a carve-out's budget), and `narrowing_some` (:425). |
| (2) Condition (ii) | `baseObj_jsonWF` (Theorems.lean:2382), proved: a rule object of a `JsonWF` document, framed by `JsonWF` payloads, is `JsonWF`. The `example` at `lean/VE/Service/ScopeExamples.lean:180` discharges `hw` in `reguard_applies` for a rule of any decoded document, through `decodeBlock_jsonWF` and `decodeBlock_payloads` (sc-1af's `jsonWF?_sound`). It is in the Service layer, not in Examples.lean, because it needs `ScopeAdmission`, and `tools/check_lean_imports.py` refuses a Scope module importing a Service one. |
| (3) Condition (iii) | `tests/test_scope_5_4_statements.py`: the five equal spec 5.4's text, whitespace aside, so a statement changed in the Lean source alone fails. Their binders are pinned (corrected by sc-2d-f1; this row first claimed more than its regex over explicit `(..)` binders checked): spec 5.4's bracketed binders of every kind (`(..)`, `{..}`, `⦃..⦄`, `[..]`), in order, must be the pinned explicit names, and the statement Lean elaborated, read from the generated `lean/statements.txt`, must have the same telescope binder for binder (a named binder keeps its name, a hypothesis is an anonymous premise, the premise at `hw` is `VE.Scope.JsonWF o`). So a binder added or dropped in both the spec and the Lean source fails, whatever its bracket. Not checked: a premise's or the conclusion's type changed in both texts with the binders kept (only `hw`'s type is read); the spec text is the reviewed statement. |
| (4) Condition (i) and fixtures | F-raw-effect (`Examples.lean:1180`) is unchanged. Section `SC2d` (`Examples.lean:1191`) checks each theorem on both chains. Accepting, on the well-formed `pRule`: every premise holds, and both conjuncts hold at each valuation of `ownModel` (:1213, :1237, :1255). Refusing (:1229, :1243, :1255): a rule with no guard, a condition with `own` at a term position, a condition with `own` that is no narrowing, and `p(x₁)` as the new guard or carve-out (the norms chain leaves the rule untyped; the soft chain refuses it). For commute, the non-commuting pair (`¬own`, then a narrowing) writes rules that apply differently at `a`. |
| (5) Inventories | `lean/statements.txt` lists the five. `lean/axioms.txt` gains 40 lines, all within `propext`, `Classical.choice` and `Quot.sound` (`git diff main -- lean/axioms.txt`). |
| (6) Condition (iv), seeded bugs | See below. |

Reused, not copied: `substOwn_id`, `substOwn_id_le`, `hasOwn_mono`, `commutes_symm` (via `Commutes`), `lookups_spec` (via `mergeParts_keys`), `mergeParts_mk`, `governorsOf_iff`, `applyEffect_src`, `top_set`, `setObjVal_ne`, `jsonWF_getD`, `budgetFormula_val`, `decodeBudgeted_ok` and `VE.Kit.Except.bind_ok`. sc-1ae's `normFields_name` and `ruleFields_name` are now corollaries of `normFields_spec` and `ruleFields_spec` (the 77 deleted lines of `Theorems.lean`), so the walk has one owner. `ite_bind_ok` moved to `EffectLemmas.lean`. `own_congr` and `order_refused` are unchanged.

edits-scope.md: no edit is implemented here. Edit 1 is sc-2b's; the others are other items' plan text.

## Seeded bugs ([mutants.json](mutants.json); each planted alone, then restored)

| Bug | File | Fails |
|---|---|---|
| reguard keeps the old guard | Govern.lean | `applyEffect_reguard` under `reguard_applies`. With that proof stubbed: `#guard` Examples.lean:1213, :1255 and F-raw-effect :1180 |
| carve-out prepends | Govern.lean | `applyEffect_carveOut` under `carveOut_applies`. Stubbed: `#guard` :1213 and :1180 |
| `Commutes` true for any reguard before a narrowing | Effects.lean | `commute_applies` (Theorems.lean:2325) and `commutes_symm`. Stubbed: `#guard` :1255 |
| `restrict_applies` loses `hw` | Theorems.lean | `test_the_proved_statements_are_spec_5_4s_text[restrict_applies]`, `test_an_effect_statement_takes_exactly_the_signed_premises[restrict_applies]` and `test_the_check_tells_a_changed_statement` (3 failed) |
| `Typed` forgets the carve-outs | Theorems.lean | `applyEffect_typed`. Stubbed: the typing `#guard`s |

Lean is the only product language changed. The test file is Python test code.

## Trust

Measured with `uv run python tools/trust_map.py --check` on the merged tree: K +0 and S +3, which is `VE.Scope.Typed` (`Theorems.lean:2211`), spec 5.4's own definition. It is recorded with `--allow` under standing ruling R16, and its FOLLOW-UPS row "## sc-2d" asks for the ties pass. The new fixtures are `T` in `tools/trust-classes.json`. Trust mutants: [trust-mutants.json](trust-mutants.json) has 9 mutants, all ALLOWED, exit 0. The allow file is [trust-mutants-allow.json](trust-mutants-allow.json). `Typed` is a Prop, and no check can evaluate it, because a `Decidable` instance reads through the mutant. So each mutant is exercised by proofs: it breaks `applyEffect_typed` (:2214) and the typing `#guard`s (:1237, :1243), and the tool lists both.

## Validation

- **Lean.** `lake build` on the merged tree: 1211 jobs. `python3 lean/audit.py`: PASS, 707 files, 7903 declarations.
- **Generated files.** `regen_generated.py --write`: 35 entries, written again after the merge of main and after the example moved.
- **Statement test.** `uv run pytest -q tests/test_scope_5_4_statements.py`: 14 passed.
- **Selected tests.** `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`.
  - Run 1, at `6622b29b`: shard 1 stopped at `tools/check_lean_imports.py`. The cause was the boundary example's import of `ScopeAdmission` in `VE/Scope/WireExamples.lean`; `tests/test_precommit_hook.py::test_large_staged_change_passes` failed for the same reason.
  - Fixed in `12982ecda` (the example moved to `VE/Service/ScopeExamples.lean`).
  - Run 2, at `12982ecda`: 411 of 411 units passed, exit 0. It ran on the VM fallback (ve-mac-1 unreachable, 18,937 s); the log line is "recorded 411 units ... 0 failed".
- **Trust mutants.** Rescored on `12982ecda`: 9 ALLOWED, exit 0.
- **Trust ledger.** The merge of main dropped sc-10a's allowance from `docs/trust-baseline.json`. It was rebuilt as main's file plus sc-2d's one allowance (`git diff --numstat main`: +7). `trust_map --check`: PASS. `tests/test_trust_budget.py`: 7 passed.
- **Not run here.** The full gate; the chain runs it on the final HEAD.
- **Overlap.** No in-flight `lean-first/`, `feature/`, `infra/` or `foundation/` branch touches these files.

**Size.** The DRI's override (dri-decisions-20261101-sc-2d.md item 1) allows about 1,100 lines. `git diff --numstat $(git merge-base HEAD main)`, generated files excluded: 1,013 added and 101 deleted before this report.
- `Theorems.lean`: +446 −77
- `EffectLemmas.lean`: +320
- `Examples.lean`: +75
- `Service/ScopeExamples.lean`: +14
- test: +39 −18
- spec: +6 −5
- DELTA, mutants and allow file: +99
- trust classes: +14

**Spec re-read.** Each statement was checked against `docs/spec/scope.md`:
- `reguard_applies` against :1246
- `restrict_applies` against :1255
- `carveOut_applies` against :1264
- `Typed` against :1272
- `applyEffect_typed` against :1276
- `commute_applies` against :1292
- `own_congr` (:1284) and `order_refused` (:1301), unchanged
- the boundary against `lean/VE/Scope/Wire.lean:103-110`

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer or request decoder changed.
2. PASS: the plan-row table above. The size override is dri-decisions-20261101-sc-2d.md. `git diff main...HEAD -- lean/VE/Scope/Govern.lean lean/VE/Scope/Effects.lean lean/VE/Scope/Wire.lean` is empty.
3. PASS: mutants.json (5 seeds, each failing a named proof, `#guard` or test). trust-mutants.json exits 0.
4. N.A.: no answer changes; no Python or Rust product code.
5. N.A.: no relayed field.
6. PASS: synced with main (merge `34e20ab25`), regenerated, built and audited on the merged tree. The chain runs the final-HEAD gate.
7. PASS: DELTA's one row is SIGNED by the DRI with its decision file. Trust S +3 is under R16, with `trust_map --check` PASS and the FOLLOW-UPS row.
8. PASS: DELTA.md. No definition changed (item 2's diff).
9. PASS: the selected run below includes `tests/test_scope_5_4_statements.py`; seed `restrict_applies_drops_hw` fails it.
10. PASS: each seed breaks a proof (mutants.json). The added premise has its counterexample, F-raw-effect, and its ruling.
11. N.A.: no budget, limit or deadline code. `budgetFormula_mono` is a proof about the existing budget.
12. N.A.: no production computation changed.
13. PASS: the five `Test-removed` trailers are in commit `4707a74ac`. `gate_collection.py --check --prebuilt`: 10 added, 5 removed by a trailer, 0 refused, 0 stale, 0 malformed.
14. PASS: both sides in every fixture (section SC2d); the spec re-read is above; every claim cites a command or a line.
