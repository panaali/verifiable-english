# Lean-first batch 7: rights ownership and gate

Base: `9aaf918d`. Branch: `lean-first/b7`. This batch changes the rights source's owner to Lean. `RightsDocument` now builds display and search containers from a checked `rights-elaborate` row. The document loader takes each rights source unit's openness from that row, and the generated English sentences come from Lean. `rights_route` relays the five-question report without regenerating and comparing Python's answer. Repeated identical rights requests use the existing bounded service cache.

The committed code diff deletes 585 Python lines in the three rights decision modules (`rights.py`, `rights_route.py`, `document.py`) while adding 128 relay/container lines there. Across all changed Python files, 659 lines are deleted and 164 added. Lean adds 81 lines and deletes 6 across the rights runner, response schema and response-shape proof; the rights runner itself adds 74 lines.

## Deletion ledger

| Deleted Python decision site | Lean owner and relayed answer |
|---|---|
| `RightsDocument.__init__` source shape, duplicate names, limits, guards, references and citation checks | `Rights.Wire.decodeRightsSource`, `Rights.Correlate.checkRights`, `checkBlock`, `checkSourceLine`, `checkShape`; the route's rejection code and text are raised by `backends.relay`. |
| `_line_environment`, `_instances`, `_slot`, `_line_shape` | `Rights.Wire.primeJsonR`, `Rights.Correlate.linesOf` and `nodeOf`, `Rights.Run.lineJson`; Python checks the row's line count and source order before constructing containers. |
| `_validate_limitations`, `_act`, `_in_scope`, `_correlate` | `Rights.Correlate.scopeLimits`, `limPremisesLabelled`, `correlate`; `Rights.Run.regenerated` supplies generated names, predicates, premises, line nodes and the extended environment. |
| `conjugated` and generated wording construction | `Rights.Run.conjugatedAct` and `generatedWordings`; `wordings` is a required, schema-checked field of `rights-elaborate`. |
| `rights_route.check_rights_regenerated` byte comparison and its expected-output reconstruction | `Rights.Run.regenerated` is the answer; `rights_route.report_rights` projects the Lean scope, bar, conflict and elaboration rows. |
| `document.py` rights status fold (`open_rule`, limitation scope and bar checks) | `Rights.Run.unitStatuses` returns `unit_open` in `rights-elaborate`; the loader binds the array to its source unit IDs. |

The Python `RightsEnvironment` block validator is outside row 7's `RightsDocument` deletion and remains for the environment switch in batch 12. The transport removes the head-only `readings@1` profile before asking the lower rights route, matching the readings route's per-choice lower chain. No Python implementation of the rights correlation, status fold or generated wording remains.

## Acceptance ownership

| Item | Owner | Evidence or state |
|---|---|---|
| Rights source elaboration, generated wordings and unit statuses | AGENT | Rights tests, corpus A/B, response schema, three seeded bugs below. |
| Frozen contract and statement inventory | AGENT | Lean frozen-source hash, generated response schema, statement audit and full gate. |
| Use-case answer keys and historical pilot documents | AGENT | Full suite and all-pilot A/B record. |
| New theorem statement approval | HUMAN (rights DRI) | No approved theorem statement changed in this batch; review remains with the DRI. |
| English track's general parser ownership | EXTERNAL (English E3) | This batch moves only rights-generated display wording. |

## Gate 5.1

The affected rights and composition tests passed (70 passed, 1 nightly deselected). The schema tests passed (135); `lake build` passed all 743 targets; the frozen-source and generated response-schema checks passed. `tools/lean_statements.py` found 4,096 unchanged theorem statements and refreshed the declaration inventory for the new definitions.

**Corpus A/B:** `tools/lean_first_diff.py` recorded the base and head on probe, conformance, readings, discourse and all historical pilot documents. Its final comparison (`evidence/ab-compare.json`) has **66,247 identical results and zero unlisted differences**. The first eight-worker pilot pass timed out on two large readings documents (`evidence/ab-initial.json`); sequential retries under the same 600-second cap returned answers byte-for-byte identical to the base in 520.67 s and 498.74 s (`evidence/pilot-retries.json`). The retry results replace only those two timeout cells in the final head record. One of the two documents has no rights profile, and sampling found its long-running work in the existing readings verdict route. The host was at roughly 22–42 load on 32 logical CPUs during these runs. No Python-visible verdict, diagnostic, identity, count or status change is proposed.

**Differential fuzzer:** the paired CI sample plus 14 date seeds (2026-09-23 through 2026-10-06) all have equal finding sets, new signatures, baseline-seen counts, and unreviewed entries (`evidence/difffuzz.json`). The CI sample and October 4 seed have zero new signatures on both revisions; the other seeds reproduce the same existing unreviewed signatures on both. The baseline does not grow.

**Latency:** on a 1,687-byte rights document with a limitation, five alternating fresh-process checks had identical JSON answers. Median wall was 0.5786 s on the base and 0.5735 s on the head (`evidence/rights-benchmark.json`). This is a loaded-host observation, not a quiet-host CPU measurement. The two large pilot retries took 520.67 s and 498.74 s at load roughly 22–42; both remained inside their 600-second recorder limit and were answer-identical. The separate 120-second quiet-host pilot budget cannot be measured on this saturated host.

The hermetic full gate runs after this report is committed. Its result JSON and counts are added in a separate evidence commit, then that final HEAD is gated again from a clean worktree.

## Seeded bugs: tests can fail

The mutations were applied one at a time to changed Python code, with the named test run against each, then the original file restored. The raw pytest failure tails are in `evidence/seeded-bugs.json`. All three tests then passed unmutated.

| Seed | Changed behaviour | Failing test |
|---|---|---|
| Wording | Replace Lean's generated wording map with an empty map | `test_generated_declarations_are_used_from_lean` |
| Unit status | Ignore Lean's `unit_open` decision for CHECKED units | `test_open_default_right_and_limitation_render_without_checked_label` |
| Line order | Build correlated rules in reverse Lean line order | `test_rights_row_preserves_source_line_order` |

## Build checklist disposition

1–3. The rights correlation has one Lean owner; existing wire-contract and Unicode fixtures exercise its readers. The three seeded bugs below demonstrate that output tests fail on wrong wording, status or line binding.

4–5. The generated rights response schema checks types, required fields and the `unit_open` length. The Python container checks source-line binding and wording keys and raises `CheckerUnavailable` if a Lean-accepted row cannot be built. Existing response-shape mutation and malformed-input tests run in the full suite.

6–8. This batch does not change verdict folds, budgets or status constructors. The Lean unit fold covers limitation, bar, outside norm and each rights line kind; focused tests cover open guards, default lines and bars.

9–10. Lean supplies rights-generated display sentences. The CLI, document loader and readings calls use the relayed rights row; the full suite and pilot A/B cover the entry paths.

11–12. No language parser, state machine or ledger changed.

13–16. The seeded bugs below are run against the affected tests. The full gate uses its hermetic environment and pinned binaries. The rights source and response bindings are checked; the gate collection includes the affected tests.

17–19. Lean source hashes and the statement diff pass; the axiom audit runs in the gate. No theorem or use-case formalisation rule was added here. An additional trust-map budget check fails on both base and head for the same existing S/V budget overrun; it is not a new statement change.

20–22. Gate numbers below come from tool output and artifacts. HUMAN and EXTERNAL items are deferred above with owners. The final full gate runs on a committed, clean HEAD; free disk and git status are checked afterward.
