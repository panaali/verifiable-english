# RSP run loop recheck 2 fix

Status: F5 fixed; F3's remaining N1 gap closes with it; no DRI signature requested.
HEAD: implementation `c93f3b85c`; this report is a follow-up commit on `infra/usecase-rsp-run`.
Changed: source-linked N1 date counterfactual and regenerated unscored results; the frozen key and scored 111/126 answers are unchanged.
Open: the independent R14 source check and `uc-audit` remain with their owners; the three tests in `main-known-red.txt` are pre-existing and were not edited.
Checks: F5 probe before and after, two failing Python seeds restored, focused regressions, 47 selected units, `lake build`, and `lean/audit.py`.

## Finding and class

F5 -> date questions now carry their source rule in one `DATE_QUESTIONS` table; `date_answer` reads that rule's existing RS0 classification before answering an obligation under the N1 prediction variant -> `test_rsp_date_obligations_follow_their_source_rules`, `test_rsp_each_narrowing_has_an_unscored_counterfactual` -> `c93f3b85c`.

The original `PROBE F5` failed before the fix (`D4=ALL`, `D5=ALL`) and passed after it (`D4=NONE`, `D5=NONE`). The same dependency also applies to the F8 coverage-date questions: D3b changes from ALL to NONE without N1; D3a was already NONE. The saved N1 comparison contains 49 changed cells, including D3b, D4 and D5; N2 and N3 remain separate. This completes the unscored comparison gap noted as F3. The date arithmetic remains a replayed VE quantity certificate in the baseline; the counterfactual changes whether its source creates an obligation.

## Seeded failures

| Changed Python product file | Temporary bug | Failing regression |
|---|---|---|
| `run.py` | tested `independent` instead of `RS0` in the N1 guard | `test_rsp_date_obligations_follow_their_source_rules`: D3b, D4 and D5 remained ALL |
| `stage0.py` | linked D4 to the independent `f5-strict` rule | `test_rsp_date_obligations_follow_their_source_rules`: source-rule classification assertion failed |

Both seeds were restored before the passing run. Lean and Rust product code did not change, so there is no seed in those languages.

## Verification and rulings

- The two focused regressions passed after restoration. The selected Mac plan ran 47 units on the uncommitted implementation snapshot (later committed as `c93f3b85c`); all passed, with zero failed or error IDs. The selection included `tests/test_safetyfw_usecases.py` and `tests/test_safety_framework.py`.
- `PATH=~/.elan/bin:$PATH lake build` passed, 1,161 jobs. `python3 lean/audit.py` passed: 668 source files and 7,428 named theorem declarations under the standard axiom allowlist.
- No full suite, release gate, model call or push was run, as requested.

There is no DELTA row: this corrects the use case's unscored section 9 counterfactual evidence. It does not change a VE product answer, approved theorem, frozen key, scored baseline, trust budget or source translation. R14 still requires the independent source check before any translated conflict is called a conflict in the policy; those conflicts remain candidates.
