# RSP run loop recheck 3 fix

Status: F6 fixed; no DRI signature or DELTA row is needed.
HEAD: implementation commit `282544e0d`; this report follows it.
Changed: one RS0 classification in each fact header, one shared fact selector, regenerated unscored N1 evidence and README count.
Open: independent R14 source check and `uc-audit` remain with their owners; three `main-known-red.txt` tests are pre-existing and untouched.
Checks: F6 probe failed before and passed after; seven focused regressions and all 47 selected units passed; `lake build` and `lean/audit.py` passed.

## Finding and class

F6 -> T4's “will/would consider” definition premises now carry the source's RS0 classification, and proof, countermodel and premise validation all use `selected_facts` when N1 is removed -> `test_rsp_n1_filters_all_rs0_definition_premises`, `test_rsp_n1_counterfactual_removes_t_family_definition`, `test_rsp_n1_saved_comparison_includes_t_family` -> `282544e0d`.

The exact `PROBE F6` printed `ALL` and failed before the fix, then printed `NONE` and passed after it. Five T-family cells now change under the N1 counterfactual: T1, T2b, T3, T4b and T7 all become NONE, with validated countermodels. The N1 comparison changes 54 cells in all. The frozen key and scored baseline remain 111/126, with 15 faithful undecided rows. F3's previously identified T-family omission is closed by this same fix. F7's stale README count was corrected to 54 as a related documentation edit.

The fix uses the fact headers as the sole classification source. Threshold identity and the independent “highly capable” definition remain available under N1 removal; all six T4 and scenario (2) definition blocks are RS0. The same filter applies to entailment premises, countermodel validation and case-premise validation, so those paths cannot disagree about which facts the counterfactual includes.

## Seeded bug and checks

I temporarily changed the Python fact selector to filter `independent` instead of `RS0`. All six new behavior cases failed, including the original T3 probe; I restored the selector before the passing run. Lean and Rust product code did not change, so no seed in those languages applies.

- Seven focused F6 regression cases passed.
- `PATH=~/.elan/bin:$PATH lake build` passed, 1,161 jobs.
- `python3 lean/audit.py` passed: 668 source files and 7,428 named theorem declarations under the standard axiom allowlist.
- Selected run through `mac-pytest.sh --select`: 47 units passed in three shards (11, 19 and 17 units); exit 0 on implementation commit `282544e0d`.
- Full suite, release gate, model calls and branch push were not run, as requested. The wrapper's configured remote test dispatch was used for selected tests.

This only corrects the use case's unscored section 9 counterfactual evidence. There is no VE product verdict, approved theorem, frozen-key, scored baseline or trust-budget delta, so there is no DELTA ruling cell. Standing ruling R14 still requires an independent source check before describing any translated conflict as a conflict in the policy.
