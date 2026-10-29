# Audit job cap

Status: complete on branch `infra/audit-jobs`.
Changed: Lean audit parts now use a bounded worker pool; gate and selector budgets reach it.
Open items: none. DRI signature: none required. No DELTA rows: this is tooling only, with unchanged audit output.
The first selected-test chain run found one branch-caused failure in `test_the_audit_replays_lean_output_and_checks_it_as_fresh`: its `axiom_outputs` stub still accepted only two arguments after the audit gained an optional jobs budget. The fixture now accepts the third argument; its focused test passes (1 passed, 59 deselected). The requested selected-test rerun is reported in the final handoff. The full release gate remains assigned to the merge train.

## Delivery

| Directive | Commit | Evidence |
|---|---|---|
| `VE_AUDIT_JOBS` takes precedence, then a caller job budget, then `max(1, cpu_count // 4)`; the pool never exceeds the number of parts. | `79695041c` | `test_audit_parts_obey_job_budget_and_keep_order` (four cases) |
| `--jobs` passes a caller budget to the audit; `pool.map` keeps output order. | `79695041c` | `test_audit_parts_obey_job_budget_and_keep_order`, real audit comparison below |
| `select_tests --jobs` reaches the audit. | `79695041c` | `test_audit_inherits_selector_job_budget` |
| A numeric gate `--workers` reaches the audit, and an explicit `VE_AUDIT_JOBS` overrides it despite the gate's clean environment. | `79695041c`, `b5db8860b` | `test_numeric_gate_workers_cap_audit`, `test_audit_env_budget_overrides_gate_workers` |
| At most two stub Lean processes run simultaneously with `VE_AUDIT_JOBS=2`. | `79695041c` | `test_audit_parts_obey_job_budget_and_keep_order[2-5-32-2]` (peak exactly 2) |

With `VE_AUDIT_JOBS=2`, `python3 lean/audit.py` passed over 654 sources and 7,286 theorem declarations. Removing its final PASS line and comparing the remaining bytes with the committed `lean/axioms.txt` succeeded (`cmp`, SHA-256 `bccacb19c1855d51d72b64ca679fad76d12d6ff8a5cb9cdd1b6d8af569bb9cbb`). That record was produced by the prior uncapped audit; its contents were not changed. The focused original build run passed 9 tests; the added part-count case passed separately, and the two gate-budget cases passed after the last gate edit. The read-only selector planned 125 of 486 units. No Lean source, generated input, Rust code, or trusted-base file changed, so no Lean build, regeneration, or trust-mutants run was required. The full gate was not run here, per this item's instructions.

## Seeded bugs

Each temporary change was restored. Each named test failed on its assertion, rather than on a build or hash check.

| File | Planted bug | Failing test |
|---|---|---|
| `lean/audit.py` | Ignore `VE_AUDIT_JOBS`, using caller jobs 5. | `test_audit_parts_obey_job_budget_and_keep_order[2-5-32-2]` |
| `lean/audit.py` | Ignore caller jobs 3, using CPU default 8. | `test_audit_parts_obey_job_budget_and_keep_order[None-3-32-3]` |
| `lean/audit.py` | Use `cpu_count // 2` instead of `// 4`. | `test_audit_parts_obey_job_budget_and_keep_order[None-None-8-2]` |
| `tools/select_tests.py` | Forward `jobs + 1`. | `test_audit_inherits_selector_job_budget` |
| `tools/gate.py` | Forward numeric workers plus one. | `test_numeric_gate_workers_cap_audit` |
| `tools/gate.py` | Ignore `VE_AUDIT_JOBS`. | `test_audit_env_budget_overrides_gate_workers` |

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean service response or request decoder changed.
2. PASS — delivery table and `git diff --check main...HEAD`; no authority or generated inventory changed.
3. PASS — six seeded bugs and their named failing tests above.
4. N.A. — no semantic input, parser, or language backend changed.
5. N.A. — no relay binding changed.
6. N.A. — the task assigns the final-HEAD gate to the chain and merge train.
7. PASS — no DELTA rows or trust growth; real audit `cmp` above.
8. PASS — real audit `cmp` against the prior uncapped record; no user-visible delta.
9. PASS — read-only `tools/select_tests.py --base $(git merge-base HEAD main)` selected 125/486 units, including `tests/test_lean_audit_record.py`.
10. N.A. — no Lean theorem or proof changed.
11. PASS — `test_audit_parts_obey_job_budget_and_keep_order` checks worker limits; no deadline changed.
12. PASS — the same test observes a peak of two stub Lean processes under a two-job cap.
13. N.A. — no test was removed or renamed.
