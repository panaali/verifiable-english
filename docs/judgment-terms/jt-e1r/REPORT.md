# JT-E1r build report

Status: **COMPLETE; JT-3 wording gate FAIL** (bar a FAIL, bar b PASS).
HEAD: pre-call frame and runner commit, followed by this evidence/report commit; no push.
Changed: fresh 40-row frame, actual VE control captures, section 2.4 English generator, 80 saved blinded calls, protocol amendment.
Open items: one JT-3 wording revision and fresh rerun under the plan; human reader audit remains separate. No DRI signature is reserved.
Model budget: 80 calls, 1,191,512 reported CW; no paid-credit fallback.

## Plan and directive rows

| Acceptance | Delivery | Evidence |
|---|---|---|
| AGENT: fresh 20 UDHR / 20 constitution frame, all three answer classes, key, judgment, decider, lint, frozen before calls | `items.tsv`, `PRE-REGISTRATION.md` in the pre-call commit | `test_frozen_frame_and_real_capture_bytes`, `test_original_items_are_not_reused`; `runner.committed()` checked HEAD before dispatch |
| AGENT: main renderer control; no invented answer line | `render.py` saves each `.ve`, environment, command, commit and stdout bytes in `captures/` | `test_frozen_frame_and_real_capture_bytes`; `UV_CACHE_DIR=/tmp/jt-e1r-uv uv run python docs/judgment-terms/jt-e1r/render.py --capture` reported eight fallback rows; `render.audit()` recomputes all 40 control captures |
| AGENT: template-generated English, identical rejected fallback, equivalent information | `render.py` and amended `jt-e1b/PROTOCOL.md`, plan JT-E1b/JT-3 lines | `test_display_information_and_fallback`; the audit reported `U17–U20, C17–C20` as fallback. JT-3's future byte-conformance test is named in the plan amendment. |
| AGENT: separate blinded Sonnet 5.5 calls, 100-call/3M-CW caps, class and decider scoring | `runner.py`, 80 records in `raw/` | `--score` output: identifier 20, English 20, critical `[]`, calls 80, CW 1191512; `test_scoring_requires_class_and_decider_and_flags_critical`, `test_usage_is_fully_reported_and_no_credit_fallback` |
| AGENT: both original bars, fallback and critical results, one gate line | `RESULTS.md` | `--score` output gives bar a `false`, bar b `true`; raw summary below |
| HUMAN: comprehension audit | separate acceptance item | deferred to a human reader; this proxy run makes no human-comprehension claim |

The exact reader command was `UV_CACHE_DIR=/tmp/jt-e1r-uv uv run python docs/judgment-terms/jt-e1r/runner.py --run`. It exited 0 after saving C20-English as call 80 with 1,191,512 CW (`/tmp/jt-e1r-calls.log`, final line). Every saved raw wrapper reported `claude-sonnet-5-5` and `fallback_credit: null`. A raw summary command iterating the 80 records printed `errors 0`, `models {('claude-sonnet-5-5',): 80}`, and `accounts {'claude-danielsaeedi37': 80}`. It also printed 4/8 correct for each fallback arm and 16/32 for each accepted-template arm. `runner.py --score` printed 20/40 in each arm and no critical IDs. The same 20 turns rows were classified CONDITIONAL in both arms. The saved records, not a live git diff, are the result evidence.

The control command uses main's `ve render --view ve_english` route with the judgment predicate as the submitted VE statement. Main's document renderer does not yet provide a usable bound-judgment display route: a probe of `ve document render` on a `judgments@0` document reached `UnsupportedProfile: Unsupported profile judgments@0` while rendering. This experiment therefore captures main's genuine predicate fallback, with the frozen frame binding that predicate to the judgment and with the source, conclusion, atom and decider explicitly shared between arms. No future JT-3 or JT-4 route is presumed. The gate applies to these exact generated declaration lines; it does not validate unseen zone or criterion wording.

## Scope and verification

No `ve/`, `lean/` or `rust/` product file changed; no generated file input changed, so regeneration, a Lean build and a Lean audit were not needed. `UV_CACHE_DIR=/tmp/jt-e1r-uv uv run python tools/trust_map.py --check` printed `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0` against `8868ce2124ec` and `PASS`. No DELTA row exists because there is no user-visible product change. Expected pilot bytes moved by this experiment: **0**; no pilot audit is claimed. The plan's judgment-terms statement review was accepted in its 2026-10-14 change log, so the statement gate was open. Planned hand-written files were the new `jt-e1r/{items.tsv,PRE-REGISTRATION.md,render.py,runner.py,RESULTS.md,REPORT.md}`, `tests/test_jt_e1r.py`, `jt-e1b/PROTOCOL.md`, and the plan. The branch-overlap query on `main...` for all in-flight `lean-first/*`, `feature/*`, `infra/*` and `foundation/*` branches printed no overlapping file (one unrelated branch lacked a merge base). `git diff --cached --numstat` before calls counted 474 added and 2 deleted hand-written lines outside the frozen captures, below the ~600-line limit.

Seeded Python bugs were planted and removed before reader calls:

| Mutation | File | Failing test |
|---|---|---|
| Substitute a wrong predicate in the VE input statement | `render.py` | `test_frozen_frame_and_real_capture_bytes` (exit 1) |
| Invent a distinct English fallback for absent/rejected templates | `render.py` | `test_display_information_and_fallback` (exit 1) |
| Drop the named decider from the English declaration | `render.py` | `test_display_information_and_fallback` (exit 1 after strengthening its generator comparison) |
| Reverse decider equality in scoring | `runner.py` | `test_scoring_requires_class_and_decider_and_flags_critical` (exit 1) |

Spec re-read: section 2.4's declaration wording and rejected-template fallback against `docs/spec/judgment-terms-PLAN.md:238–250`; section 6's two bars and fresh-rerun rule against `:756–775`; JT-E1b step 2 and the 2026-10-29 DRI amendment against `docs/judgment-terms/jt-e1b/PROTOCOL.md` and `reviews/lp-answers-20261029T1620.md` item 2. The English generator fills only the declaration row of section 2.4. The status/zone/criterion rows await their owning routes and are outside the evidence of this failed declaration-line gate.

Next item: JT-3 wording revision and fresh-item rerun under the plan's one-revision rule (follow-up `jt-e1s`); JT-3 stays gated until it passes. The revision should consider showing the zone/conflict rows, since the declaration line alone carries no class information (RESULTS.md). The plan's JT-3 amendment names the acceptance test `tests/test_jt3_english.py::test_declaration_lines_match_jt_e1r_templates`, which JT-3 adds. The human reader audit remains separately owned.

## Self-review against BUILDER-CHECKLIST

1. N.A. — no relayed Lean answer or response schema changed.
2. PASS — `test_frozen_frame_and_real_capture_bytes`, `RESULTS.md`, and the plan-row table above cover the experiment deliverables.
3. PASS — four seeded mutations above failed named tests; no trusted Lean definition changed.
4. N.A. — no Python/Lean/Rust product agreement route changed.
5. N.A. — no new R8 relay field or request binding changed.
6. N.A. — the task directs the chain to run the final-HEAD gate; no local gate was run.
7. PASS — `tools/trust_map.py --check` showed zero growth; there is no DELTA row or reserved signature.
8. N.A. — no user-visible product output changed; `git diff --name-only main...HEAD` contains experiment and docs files only.
9. PASS — the selected-test wrapper chose `tests/test_jt_e1r.py` and it exited 0; selection output is in `/tmp/jt-e1r-selected.log`.
10. N.A. — no Lean statement or proof changed.
11. PASS — `test_usage_is_fully_reported_and_no_credit_fallback` checks call/CW boundaries, malformed usage and credit fallback.
12. N.A. — no product CPU or memory path changed; the 40-row renderer audit is bounded by the frozen frame.
13. N.A. — no test was removed or renamed.
14. PASS — `test_display_information_and_fallback` checks accepted and rejected directions; `test_scoring_requires_class_and_decider_and_flags_critical` checks positive and negative scores; report claims cite commands/raw records and spec text above.
