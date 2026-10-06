# Lean-first batch 7: rights ownership and gate

Base: `9aaf918d`. Branch: `lean-first/b7`. This batch changes the rights source's owner to Lean. `RightsDocument` now builds display and search containers from a checked `rights-elaborate` row. The document loader takes each rights source unit's openness from that row, and the generated English sentences come from Lean. `rights_route` relays the five-question report without regenerating and comparing Python's answer. Repeated identical rights requests use the existing bounded service cache.

The committed code diff deletes 585 Python lines in the three rights decision modules (`rights.py`, `rights_route.py`, `document.py`) while adding 128 relay/container lines there. Across all changed Python files, 663 lines are deleted and 164 added. Lean adds 81 lines and deletes 6 across the rights runner, response schema and response-shape proof; the rights runner itself adds 74 lines.

## Deletion ledger

| Deleted Python decision site | Lean owner and relayed answer |
|---|---|
| `RightsDocument.__init__` source shape, duplicate names, limits, guards, references and citation checks | `Rights.Wire.decodeRightsSource`, `Rights.Correlate.checkRights`, `checkBlock`, `checkSourceLine`, `checkShape`; the route's rejection code and text are raised by `backends.relay`. |
| `_line_environment`, `_instances`, `_slot`, `_line_shape` | `Rights.Wire.primeJsonR`, `Rights.Correlate.linesOf` and `nodeOf`, `Rights.Run.lineJson`; Python checks the row's line count and source order before constructing containers. |
| `_validate_limitations`, `_act`, `_in_scope`, `_correlate` | `Rights.Correlate.scopeLimits`, `limPremisesLabelled`, `correlate`; `Rights.Run.regenerated` supplies generated names, predicates, premises, line nodes and the extended environment. |
| `conjugated` and generated wording construction | `Rights.Run.conjugatedAct` and `generatedWordings`; `wordings` is a required, schema-checked field of `rights-elaborate`. |
| `rights_route.check_rights_regenerated` byte comparison and its expected-output reconstruction | `Rights.Run.regenerated` is the answer; `rights_route.report_rights` projects the Lean scope, bar, conflict and elaboration rows. |
| `document.py` rights status fold (`open_rule`, limitation scope and bar checks) | `Rights.Run.unitStatuses` returns `unit_open` in `rights-elaborate`; the loader binds the array to its source unit IDs. |

The Python `RightsEnvironment` block validator is outside row 7's `RightsDocument` deletion and remains for the environment switch in batch 12. The transport removes the head-only `readings@1` profile before asking the lower rights route, matching the readings route's per-choice lower chain; this is availability change A1 below. No Python implementation of the rights correlation, status fold or generated wording remains.

## Acceptance ownership

| Item | Owner | Evidence or state |
|---|---|---|
| Rights source elaboration, generated wordings and unit statuses | AGENT | Rights tests, corpus A/B, response schema, three seeded bugs below. |
| Frozen contract and statement inventory | AGENT | Lean frozen-source hash, generated response schema, statement audit and full gate. |
| Use-case answer keys and historical pilot documents | AGENT | Full suite and all-pilot A/B record. |
| New theorem statement approval | HUMAN (rights DRI) | No approved theorem statement changed. The review fix adds 16 statements, each `twin = original` or a `@[csimp]` registration of one (`lean/statements.txt`); approval remains with the DRI. |
| Signatures for O1, W1 and A1 | HUMAN (DRI) | Listed in `delta.json`; see "Changes for signature". |
| Quiet-host pilot wall time (120 s) | EXTERNAL (quiet host) | CPU measured side by side below; the wall-time budget cannot be measured on this host. |
| English track's general parser ownership | EXTERNAL (English E3) | This batch moves only rights-generated display wording. |

## Gate 5.1

The affected rights and composition tests passed (70 passed, 1 nightly deselected). The schema tests passed (135); `lake build` passed all 743 targets; the frozen-source and generated response-schema checks passed. `tools/lean_statements.py` found 4,096 unchanged theorem statements and refreshed the declaration inventory for the new definitions.

**Corpus A/B:** `tools/lean_first_diff.py` recorded the base and head on probe, conformance, readings, discourse and all historical pilot documents. Its comparison (`evidence/ab-compare.json`) has 66,247 identical results and zero unlisted differences on those corpora. That run left out the rights profile's own generated corpus, and with it every changed rejection (review B2). The tool now has a `rights` corpus: the rights differential's 1,000 generated sources and 250 of them again under `readings@1`, through `check_document` and `render_document`. Each differential generator in `conformance/` is a corpus or is named with its reason (`test_every_differential_generator_is_a_corpus_or_names_its_reason`). On that corpus, 1,938 of 2,500 records are identical, and every one of the 562 differences is O1, W1 or A1 below; `delta.json` lists them, and the comparison with it has zero unlisted differences (`evidence/ab-rights.json`). The readings corpus, re-recorded on the review-fix head, is 1,137 of 1,137 identical. The first eight-worker pilot pass timed out on two large readings documents (`evidence/ab-initial.json`); sequential retries under the same 600-second cap returned answers byte-for-byte identical to the base in 520.67 s and 498.74 s (`evidence/pilot-retries.json`). The retry results replace only those two timeout cells in the final head record. One of the two documents has no rights profile, and sampling found its long-running work in the existing readings verdict route. The host was at roughly 22–42 load on 32 logical CPUs during these runs. That account was wrong (review B1): host load did not cause the timeouts. The changes proposed for signature are listed below.

**Differential fuzzer:** the paired CI sample plus 14 date seeds (2026-09-23 through 2026-10-06) all have equal finding sets, new signatures, baseline-seen counts, and unreviewed entries (`evidence/difffuzz.json`). The CI sample and October 4 seed have zero new signatures on both revisions; the other seeds reproduce the same existing unreviewed signatures on both. The baseline does not grow.

**Latency:** on a 1,687-byte rights document with a limitation, five alternating fresh-process checks had identical JSON answers. Median wall was 0.5786 s on the base and 0.5735 s on the head (`evidence/rights-benchmark.json`). That small document hid the cost (review B1). The readings route builds a `RightsDocument` for every reading candidate (`ve/readings_s1.py` `Side._elaborate`), and since this batch each build is a Lean `rights-elaborate` call. On the UDHR pilot that is 94 calls. Each cost about 1.8–2.0 s, 211 s in all, and almost none of it was the document: an empty rights document over the same environment cost the same. Lean's validation and output rebuilt the layer order of the document for every formula it typed or expanded. `Norms.semanticCheck` and the soft checks did it through `envAt`; `targets` and `InFragment` did it through `subst`/`expTable`. The cost grew about as the fourth power of the regulated predicates. Cutting the pilot's environment to its first 17, 35, 52 and 70 predicates, an empty-document request took 0.016, 0.125, 0.55 and 1.86 s.

The fix keeps every definition the proofs use. Each of those functions has a hoisted twin, proved equal to it (`semanticCheckOnce_eq`, `checkSoftOnce_eq`, `targetsIn_eq`, `InFragmentIn_eq`, …). Each twin is registered with `@[csimp]` in the module where the original is first consumed (`VE/Norms/Once.lean`, `VE/Norms/LayersOnce.lean`, `VE/Norms/Replay.lean`, `VE/SoftNorms/Once.lean`), so the compiler emits the twin wherever compiled code called the original. Batch 3d's readings-only F5d twins move there too. A request over the pilot's environment now costs 0.06 s of service CPU. `tests/test_lean_layers_once.py` walks the compiled IR from the service's `runMode` over every route mode, and fails if any route reaches an original that a registered `VE` twin replaces. With `targets`' twin first registered after `VE.Norms.Replay`, that walk found 22 callers in the norms, speech-act, alternatives and risk routes; registering it in `Replay` itself removed them. The same walk from `validateSoft`'s own body does find them. The test also bounds one rights request over 64 predicates at 0.5 s of CPU.

The UDHR pilot was checked side by side on the base and the review-fix head, at load 37–46 on 32 logical CPUs, with byte-identical answers (`evidence/pilot-timing.json`, `pilot_timing.py`). Measured as CPU of the process and the Lean service, base and head took 100.5 and 119.4 s in round one and 94.4 and 108.5 s in round two, so the head uses 15–19% more CPU. The review measured 82 and 309 s before the fix. The remaining extra is the 94 small requests' service and response-checking work. The 120-second pilot budget is a quiet-host wall time. This host cannot show it: here the base itself took 144–160 s of wall.

The first hermetic full gate ran on clean `8bcd4e86` and reached all six stages. Lean build and audit passed (743 targets; 408 files and 4,311 named theorems with standard axioms only); Rust built and 50 tests passed. Pytest recorded 11,071 passed, 7 allowed skips and 3 failures (`evidence/full-gate-first.json`). All three failures were batch bookkeeping: two deleted call sites remained in `tools/inventory_lint.py`, the new Python container exception boundary lacked its assurance-manifest entry, and eight new Lean declarations lacked trust classes. Those records were fixed, the stale `rights-three-way-report.json` was regenerated as an embedding report, and the three exact failing tests passed.

The second hermetic full gate passed on clean `cc57f668`: 11,074 Python tests passed, 7 allowed skips, 50 Rust tests passed, zero failures (`evidence/full-gate.json`). It again built 743 Lean targets and audited 4,311 named theorems. After committing this gate record, the full gate is run once more on the resulting clean HEAD; that run's commit and result are reported in the handoff.

## Changes for signature

`delta.json` lists every record below, written by `rights_delta.py` from the comparison, which refuses any other kind of difference. Run with `--delta delta.json`, the rights corpus has zero unlisted differences.

| Id | Class | Change | Records | Signature |
|---|---|---|---|---|
| O1 | `order` (code) | A source citing a unit that does not exist is rejected with Lean's code `UnknownSymbol`; the base raised `InvalidInput` with the same text `UnknownSymbol: unit u9`. Both `ve document check` and `render`. | 148 (74 documents × 2 operations) | DRI: pending |
| W1 | `wording` | A rejection's text gains its code as a prefix, as every relayed Lean rejection has it: `bar` becomes `DuplicateDeclaration: bar`, and `carve-outs of rule …` becomes `ResourceLimit: carve-outs of rule …`. The code is unchanged. 6 distinct text pairs. | 224 (112 × 2) | DRI: pending |
| A1 | availability (`verdict` by the tool: the base raised a code other than `CheckerUnavailable`) | A `readings@1` document over a rights source with no rights reading set is checked. The base's rights report asked the lower route with the head profile and raised `UnsupportedProfile: Unsupported profile readings@1` from `ve document check`; the head reports the lower chain's rights report. That report is the one the same document gets without `readings@1`, except `environment_id`, which names the profile (`test_head_profile_over_a_rights_document_without_reading_sets_reports_the_lower_chain`). Rendering was unaffected. | 190 | DRI: pending |

`test_document_loader_relays_lean_rights_rejections_verbatim` pins O1 and W1. For every generated source Lean rejects, `load_document` raises Lean's class and text.

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

13–16. The seeded bugs below are run against the affected tests. The review fix adds three more checks that can fail. Restoring the base's `readings@1` transport makes the A1 test fail. Walking from code compiled before the twins finds the originals. The generator list test fails on an unregistered differential generator. The full gate uses its hermetic environment and pinned binaries. The rights source and response bindings are checked; the gate collection includes the affected tests.

17–19. Lean source hashes and the statement diff pass; the axiom audit runs in the gate. No theorem or use-case formalisation rule was added here. An additional trust-map budget check fails on both base and head for the same existing S/V budget overrun; it is not a new statement change.

20–22. Gate numbers below come from tool output and artifacts. HUMAN and EXTERNAL items are deferred above with owners. The final full gate runs on a committed, clean HEAD; free disk and git status are checked afterward.
