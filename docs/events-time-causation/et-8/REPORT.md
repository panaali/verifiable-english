# et-8 build report: Asimov and the ET-1 component on the completion (events-time-causation ET-8)

No DRI signature is reserved; DELTA.md has no rows (no product code changed). Branch `feature/et-8`, from main
`630d2e136`. Plan: `research/events-time-causation-p1` at `a12fea083`, section 5 "ET-8", 2.10, fixture R2 (4.3).
Statement gate: ET-8 states no Lean statement; the plan's draft 3 applies the converged statement review, and ET-7
and ET-7b, which it needs, have merged.

## Results

**Asimov's v2 rules** (`usecases/asimov-extended/asimov_unspecified.py`, results in
`usecases/asimov-extended/unspecified/results.json`), with `permitted` completed `unspecified` under
`norm-defaults@0`, on Lean's alternatives route:

| | allow (before) | deny | `unspecified` (ET-8) |
|---|---|---|---|
| 13 rules | CHECKED | | CHECKED (one reading each; same text, blocks and text digest) |
| conflict verdict | CONFLICT-FREE | | CONFLICT-FREE, 8 targets replayed |
| 9 distinct spec models with a clear action | 6 | | **2** (`d-full`, `e`) |
| 43 of the 51 records (no `might` cell) with a clear action | 30 (= `results.json` on the risk route, record by record) | 11 | **11** |
| DILEMMA witnesses `b-A0`, `b-A1`, `j` | NONE-PERMITTED ×2, OVER-REQUIRED | | the same |

Each `unspecified` clear set equals the deny clear set and lies inside the allow clear set. Every remaining clear
action is permitted by rule 1, 2 or 9. 19 records have an UNDECIDED action (`UNSETTLED(...)`, evidence: two
validated fillings). The earlier figures (49/51 extended, 37/51 v2, 13/51 deny, all on the risk route) stay in the
READMEs as history.

**The ET-1 component** (`experiments/events-time-causation/et8_component.py`; evidence `evidence/component.json`
and `evidence/component-results.json`): phase 1's component with `permitted` ("may be given") completed `unspecified`
and the legend removed from its description. Its rules, premises and scenario are unchanged.

- CONFLICT-FREE (3 targets replayed); unmapped obligations: none.
- FOLLOWABLE: **no certificate found**, so the answer is `UNKNOWN: no accepted followability certificate`.
- DILEMMA, with the filling that permits nothing unsaid: where refusal is the only response, `UNSETTLED(refuse)`.
  On phase 1's scenario, `UNSETTLED(refuse, answer)`; the scenario check gives `undermine` not clear, `refuse` and
  `answer` undecided.
- So the outcome is **DILEMMA `UNSETTLED(refuse)`**, not FOLLOWABLE: no rule of the component permits refusal.
  As a comparison only, the component with u0172.s02 read as a permission ("every response that is inaction may be
  given, unless a hard constraint forbids it") is FOLLOWABLE, conditional on both u0172.s02 premises. Whether
  u0172.s02 states that permission is the targeted audit's question (DEFERRED, below).
- R14: no conflict or dilemma is presented as a finding about the constitution. `UNSETTLED(refuse)` is a result
  about this translation. It is a CANDIDATE until an independent source check by a different model, which this
  item may not run (no model calls): EXTERNAL, owner the DRI, together with the targeted audit.

## Plan rows

| Plan row (ET-8; R2) | Delivered | Where |
|---|---|---|
| asimov-laws with `permitted` switched to `unspecified`; clear actions only where a rule permits; UNSETTLED only from two validated fillings | yes, as a measured re-run; the committed environment keeps allow (the extended case's `risk@0` needs it) | `test_rerun_spec_models_and_records_equal_the_committed_results`, `test_the_committed_counts_derive_from_the_committed_rows` |
| bar: 13 rules still CHECKED and conflict-free | yes | `test_v2_rules_stay_checked_and_conflict_free_under_unspecified` |
| bar: count of models with a clear action reported | v2: yes (2/9 models, 11/43 records). Extended rules: **no** (`risk@0` does not take the completion, plan 2.10: its own batch) | READMEs; `test_permission_default_stays_allow_until_norm_defaults_combines_with_risk_and_alternatives` still holds |
| README and coverage numbers updated, old figures kept | yes | both READMEs |
| ET-1 component on `unspecified`, legend removed; record FOLLOWABLE or DILEMMA `UNSETTLED(refuse)` | yes: DILEMMA `UNSETTLED(refuse)` | `test_the_switched_component_differs_from_phase_1_only_in_the_completion_and_the_legend`, `test_the_et1_component_on_the_completion_equals_the_committed_results` |
| the targeted audit's view of u0172.s02; R14 source check | **no**: needs a model call (DEFERRED 0.3, EXTERNAL) | |

## Deviations

- 8 of the 51 records (O5, P1, P2, P3, P4, P7, P9, P10) have a `might` cell, which needs `risk@0`; they are listed
  and not run. The other 43 are rebuilt as v2 alternatives scenarios. Under allow, each gives its committed
  risk-route clear set, which checks the rebuilding.
- Conflict certificates are searched over `Fill_T` alone first, then with the slot premises: with the slot premises
  the prover hits its step limit on `permitted` (20,000 steps, also 200,000). Lean replays the certificate over fewer
  premises.
- The u0171.s03 entailment is not re-run: `alt-certificate` with `norm-defaults@0` is refused by name (et-7c).
- Check time: under `unspecified`, `R:dominated-action-when-threats-conflict` takes about 145 s of Lean CPU per
  scenario check, against the route's 180 s deadline. One run exceeded the deadline, so the harness sets a 900 s
  wall-clock limit. The tests do not rerun that record. A full harness run takes about 12 minutes.
- The results file is `unspecified/results.json`, which `tools/difffuzz_corpus.py` already files as recorded results.

## Seeded bugs ([mutants.json](mutants.json))

All Python (no product code changed). Each was applied, its test run, and the file restored; all 9 were killed.

| Id | File, definition | Bug | Killed by |
|---|---|---|---|
| S1 | `asimov_unspecified.py`, `environment` | `unspecified` left at allow | `test_v2_rules_stay_checked_and_conflict_free_under_unspecified` |
| S2 | same, `clear` | UNDECIDED counted as clear | `test_rerun_spec_models_and_records_equal_the_committed_results` |
| S3 | same, `records_section` | a two-action `might` record run without risk | the same |
| S4 | same, `conflict` | no search without the slot premises | `test_v2_rules_stay_checked_and_conflict_free_under_unspecified` |
| S5 | same, `witnesses` | a filling that permits `pull` | the same |
| C1 | `et8_component.py`, `component` | legend kept | `test_the_switched_component_differs_from_phase_1_only_in_the_completion_and_the_legend` |
| C2 | same, `component` | `permitted` left at allow | `test_the_et1_component_on_the_completion_equals_the_committed_results` |
| C3 | same, `answers` | a filling that permits refusal | the same |
| C4 | same, `permission_reading` | the permission without its exception | the same |

## Trust, size, pilot bytes

- Trust: K +0, S +0, V +0; `tools/trust_map.py --check` PASS. No R16 row is needed.
- Size: 487 hand-written lines added or changed (harnesses 287, tests 113, READMEs 64 added and 60 removed,
  DELTA, mutants and this report about 130). The generated evidence (`component.json`, the two result files) is
  not counted.
- Pilot bytes: 0 new bytes (plan estimate 0). Fidelity of ET-1's bytes: phase 1's FOLLOWABLE for u0172.s01 and
  u0172.s02 (332 B) rested on the allow completion and its legend. On the completion it holds only if the audit
  reads u0172.s02 as a permission. Nothing is claimed before that audit.

## Next items

- **et-8b**: re-run the extended rules (1–29) and the 8 `might` records with `unspecified` once `risk@0` takes the
  completion (a product batch, plan 2.10); then switch the committed environments.
- The targeted audit of u0171.s03, u0172.s01, u0172.s02 (0.3), told the u0172.s02 permission question, with R14's
  source check of `UNSETTLED(refuse)`.
- u0171.s03 on the completion after et-7c; the 145 s scenario check (FOLLOW-UP for the scenario search's cost).

## Tests run

- `tests/test_et8_completion.py` (5 passed); the touched Asimov tests (3 passed); the 9 mutants.
- Selected tests (`mac-pytest.sh --select`, ve-mac-1, HEAD `7e9e033f`): 1 failed, `test_difffuzz.py::
  test_every_fixture_is_read_or_excluded_with_a_reason` (the results file's first path), fixed in `a86285987`; the
  rerun passes. Final selected run: see below. No test of main-known-red.txt was hit.
- `tools/regen_generated.py --check` (31 entries), `tools/repo_map.py --check`, `tools/gate_collection.py --check
  --prebuilt` (5 added, 0 refused, stale or malformed), `tools/trust_map.py --check`, `lake build` (no Lean change).
  The full gate is the chain's, on the final HEAD.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained: N.A., no relay or schema changed.
2. Every deliverable: PASS, plan-row table above; no Python copy of a Lean decision (every status is Lean's row).
3. Tests can fail: PASS, 9 seeded bugs, [mutants.json](mutants.json).
4. Py/Lean/Rust agree: PASS for the rebuilt records, whose allow answers equal the risk route's
   (`test_rerun_spec_models_and_records_equal_the_committed_results`); no Rust leg (Rust decodes no `alternatives@0`).
5. R8 binding: N.A., no relayed field is read in new product code.
6. Gate evidence matches HEAD: PASS, branched from current main `630d2e136`; the gate is the chain's.
7. No unsigned item: PASS, DELTA has no rows; nothing is reserved for the DRI.
8. Every user-visible change in DELTA: PASS, no product output changes (`git diff main...HEAD --stat` touches no
   product path).
9. Test selection: PASS, `select_tests.py` selects `test_et8_completion.py`, `test_asimov_extended.py`,
   `test_asimov_laws.py` and `test_difffuzz.py`, the test that caught the first results path.
10. Lean statements: N.A., no Lean change.
11. Budgets fail closed: N.A. for product code. The harness's explicit timeout is a wall-clock limit, and a cut
    scenario would raise `CheckerUnavailable`, never a status.
12. CPU or memory: N.A. for product code; the 145 s scenario check is reported above as a finding.
13. Test-removed trailers: PASS, `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed (no test removed).
