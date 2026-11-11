# soft-cf-text-1: the soft route's CONFLICT-FREE line names no search, and `<j>` counts WP(T)

**Status:** built; no DRI signature needed (DELTA rows 1-3 cite R1, R3, R16). Base main b81b82ef9.
**What changed:** with no `coherent_model` the soft-conflict CONFLICT-FREE line ends `coherent situation exhibited:
none supplied (not searched; budget N unused)`, not `UNKNOWN (budget N)`. The words have one owner,
`VE.SoftNorms.Wire.notSearchedText`, which the rights line also calls. `<j>` already counted the open WP(T) on main
(rights-cfr-2-budget-1), so it is now pinned, not changed. No printed count moves (step 1). Specs 7.3 updated.
**Open:** the full gate, which the chain runs on the final HEAD.

SIZE: 17 product (Lean +13/-4), 124 tests, 539 other hand-written lines (specs 12, DELTA 22, this REPORT 146, step-1
probe and plugin 148 and its output 20, delta.json 103, mutants.json 66, trust and assurance records 20, ties row 2).

## Step 1: measured before any edit

Commands (on the unedited tree, main b81b82ef9; output and command lines saved in `evidence/step1-output.txt`):
a pytest run of 26 soft, rights, readings, relay-binding, handles and route-schema test files with a plugin
(`evidence/soft_cf_probe_plugin.py`) that logs every soft CONFLICT-FREE status line in any Lean answer, nested ones
included (1361 passed), then `uv run python docs/soft-norms/soft-cf-text-1/evidence/step1_probe.py <log dir>`, which
also runs every soft-conflict case of tests/data/relay-gate-cases.jsonl and tests/data/route-cases.jsonl and one
constructed case, and for each answer asks `soft-pairs` with the same environment, norms and pair evidence for the
open WP(T) list.

Definitions (main b81b82ef9, lean/VE/SoftNorms/Run.lean):
- `<k>` = `conditional.length`, `conditional := sufficientCoherence openLabels (conflictValidWithout res)` (:359, :149):
  the open coherence premises the certificates still need.
- printed `<j>` = `openLabels.length` (:125), `openLabels := openAfterClassification ...` (:357, :117):
  `Wire.openCoherence` (lean/VE/SoftNorms/Wire.lean:174) less the pairs the request's evidence discharges as DISJOINT.
  The rights-cfr-2-budget-1 merge already changed this from `conditional.length`.
- open WP(T) list: `weighing_points` of a `soft-pairs` answer (`pairsResult`, :103-113): pairs neither RANK-RESOLVED
  nor DISJOINT. The soft-conflict answer itself has no `weighing_points` field (see Notes).

| Source | Status line printed on main (tail) | `<k>` | printed `<j>` | open WP(T) |
|---|---|---|---|---|
| relay-gate-cases.jsonl:485 (c) | `1 coherence premises; 1 weighing points open; coherent situation exhibited: UNKNOWN (budget 10000)` | 1 | 1 | 1 |
| relay-gate-cases.jsonl:486 (c) | `0 coherence premises; 0 weighing points open; ... UNKNOWN (budget 10000)` | 0 | 0 | 0 |
| route-cases.jsonl:222 (c) | `1 ...; 1 ...; ... UNKNOWN (budget 10000)` | 1 | 1 | 1 |
| route-cases.jsonl:223 (c) | `0 ...; 0 ...; ... UNKNOWN (budget 10000)` | 0 | 0 | 0 |
| route-cases.jsonl:224 (shown) | `1 ...; 1 ...; ... yes` | 1 | 1 | 1 |
| test_relay_binding_inventory `[document-soft-defaults]` (two lines) | `0/0 ... UNKNOWN (budget 7)`, `1/1 ... UNKNOWN (budget 7)` | 0, 1 | 0, 1 | 0, 1 |
| test_soft_norms_lean `test_delta_conflict_free_conditional_on_coherence` | `1/1 ... UNKNOWN (budget 10000)`, `1/1 ... yes` | 1 | 1 | 1 |
| test_soft_norms_lean `test_alpha_rank_resolved_conflict_free_unconditionally` | `0/0 ... UNKNOWN (budget 10000)` | 0 | 0 | 0 |
| test_rights_report_parts `test_rights_and_soft_routes_count_the_same_weighing_points` | `1/1 ... UNKNOWN (budget 10000)` | 1 | 1 | 1 |
| test_lean_handles `[soft-norms]` (route corpus, three lines) | `1/1 ... UNKNOWN`, `0/0 ... UNKNOWN`, `1/1 ... yes` | 1, 0, 1 | 1, 0, 1 | 1, 0, 1 |
| constructed: default `a` guarded by ⊥, certificates without Coh | `0 coherence premises; 1 weighing points open; ... UNKNOWN (budget 10000)` | 0 | 1 | 1 |

Reading: on every existing fixture and test `<k>` = printed `<j>` = open WP(T). On the constructed case `<k>` (0)
and WP(T) (1) differ, and main already prints `<j>` = 1. So `<j>` counts what it names. The old
`conditional.length` would print 0 there, but it prints the same number on every existing fixture. Deliverable (2)
is therefore "take `<j>` from the open WP(T) list (one owner), delete the duplicate", and rights-cfr-2-budget-1 had
already done it. This item pins it and changes no count, so the task's stop condition does not apply.

## Deliverables

| Task line | Delivered by | Test |
|---|---|---|
| (1) no model: the line must not say a search hit its budget; rights-cfr-2-budget-1's words; budget value kept; `yes` with a model; JSON fields byte for byte; R1 DELTA row | `VE.SoftNorms.Wire.notSearchedText` (new, one owner; `Rights.Run.exhibitedText` now calls it, output unchanged), `SoftNorms.Run.conflictFreeText` calls it. Shared, not mirrored: Rights already imports `VE.SoftNorms.Wire`, so this adds no dependency (Soft cannot import Rights.Run, which imports Soft). | `test_soft_conflict_free_without_a_coherent_model_names_no_search`, `test_soft_no_search_delta_keeps_every_quoted_value` (fields equal the saved ones, no field added), `#guard`s SoftNorms/Run.lean :129-:130; DELTA row 1 |
| (2) `<j>` counts what it names | Already WP(T) on main (`openAfterClassification` on `Wire.openCoherence`, the definition the rights line counts with no pair evidence); duplicate `conditional.length` already gone. No product change; pinned. | `test_soft_weighing_point_count_is_the_open_wp_list` (constructed `<k>` 0, `<j>` 1 = `len(soft-pairs weighing_points)`), `#guard` :130 (`<k>` 0, `<j>` 1) and :129 (`<k>` 1, `<j>` 2) |
| (3) specs: soft-norms.md 7.3 and rights.md 7.3 state the no-search form and what `<j>` counts | soft-norms.md 7.3 template line 2 plus a paragraph on `<k>`, `<j>`, `none supplied` and `UNKNOWN (<budget>)`; rights.md 7.3 already had both and gains one sentence naming the shared definition. | `soft_spec_line` reads the soft template; the three tests above compare Lean's line with it; tests/test_rights_report_parts.py (reads the rights template) 71 passed |
| (4) tests, seeded bugs, mutants.json | see above; S1-S5 below | `mutants.json` |
| Step 1 measurement | `evidence/step1-output.txt`, table above | |
| DELTA | `DELTA.md` rows 1-3 (R1, R3, R16) | review-ready's Ruling-cell check run on the file: all three pass |

Condition tests (must stay selected): `tests/test_soft_norms_lean.py::test_soft_conflict_free_without_a_coherent_model_names_no_search`
and `::test_soft_weighing_point_count_is_the_open_wp_list`. `tools/select_tests.py --base b81b82ef9` selects 512/590
units including tests/test_soft_norms_lean.py.

## Seeded bugs (mutants.json)

| Id | Language, file | Mutation | Failing check |
|---|---|---|---|
| S1 | Lean, lean/VE/SoftNorms/Run.lean | old exhibited text `UNKNOWN (budget {budget})` restored | `#guard` :129 (`lake build VE.SoftNorms.Run` failed); with the guards dropped and the service pinned temporarily: `test_soft_conflict_free_without_a_coherent_model_names_no_search`, `test_soft_weighing_point_count_is_the_open_wp_list` and `test_soft_no_search_delta_keeps_every_quoted_value` FAILED |
| S2 | Lean, lean/VE/SoftNorms/Run.lean | `<j>` back to `conditional.length` | `#guard`s :129, :130; with the guards dropped: `test_soft_weighing_point_count_is_the_open_wp_list` FAILED (line printed `0 weighing points open`), and the delta test FAILED |
| S3 | Lean, lean/VE/SoftNorms/Wire.lean | `notSearchedText` drops the budget value | `#guard` :129 |
| S4 | Lean, lean/VE/SoftNorms/Run.lean | the `yes` branch lost (always `notSearchedText`) | `#guard` :130 |
| S5 | Lean, lean/VE/Rights/Run.lean | `exhibitedText` quotes budget 7 | RightsChecks.lean :56, :58, :61 |

Each mutant was restored and the tree rebuilt (`lake build`, 1395 jobs, success). Python product code is unchanged.

## Trust (R16)

`tools/trust_map.py --check` against b81b82ef91ad: K +0, S +0, D +8 (V +8): VE/SoftNorms/Wire.lean +6, VE/SoftNorms/Run.lean
+2. Recorded with `trust_map.py --allow` in docs/trust-baseline.json. `notSearchedText` is classed D[V] in
tools/trust-classes.json, beside `openCoherence`. Wire.lean is pinned whole in ve/assurance-manifest.json: re-pinned
(538 lines, new sha256, decoder total 45074) after review (the 6 new lines are one string function, no decoding);
tests/test_assurance_manifest.py 152 passed. trust_mutants (`mac-pytest.sh --trustmut -- --test
lean/VE/SoftNorms/Run.lean --test lean/ResponseShape/Schemas/RightsChecks.lean --json .../trust-mutants.json`, at
783a72c905, run on the VM, exit 0) planned 0 definitions, 0 mutants. Every changed trusted line is string text or a
call, and its operators mask strings and have nothing else to mutate there. The hand-planted S1-S5 cover those lines.
The ties-pass row is in `evidence/follow-ups-row.md` and appended to FOLLOW-UPS.md. `python3 lean/audit.py`: PASS
(849 files, 9508 theorems).

## Spec re-read

- "coherent situation exhibited: yes | UNKNOWN (<budget>) | none supplied (not searched; <budget> unused)" against
  docs/spec/soft-norms.md 7.3 and rights.md 7.3 (:767); the words are rights.md's, with `<budget>` rendered
  `budget N` as rights-cfr-2-budget-1's tests do.
- "`<j>` counts WP(T) under the request's pair evidence" against soft-norms.md:577 (WP(T) := WEIGHING POINT and
  UNKNOWN pairs) and :632, and Run.lean `openAfterClassification`.
- "`yes` when the request sends a coherent_model that satisfies Background′" against Run.lean :361-366
  (`backgroundValid'`, InvalidModel otherwise).

## Test results

While iterating: `uv run pytest tests/test_soft_norms_lean.py -k "no_search or weighing_point_count or
delta_conflict_free or alpha_rank"` 5 passed; tests/test_rights_report_parts.py 71 passed;
tests/test_assurance_manifest.py 152 passed. `regen_generated.py --write` once (only code-map files changed, committed).
Final selected run: see below.

## Notes for the DRI

- The soft template in soft-norms.md 7.3 shows `(<labels>)` after `<k>`, but the shipped line has never printed the
  labels; they are the answer's `conditional_on` field. This item leaves that as it is, because changing either is a
  wording delta outside its task. The test helper `soft_spec_line` drops `(<labels>)` and says why.
- The soft-conflict answer has no `weighing_points` field, unlike rights-conflict. The open WP(T) list comes from a
  `soft-pairs` request. Adding the field would change the answer's schema, and the task keeps every JSON field byte
  for byte, so this item does not add it.
- `regen_generated.py --write` also rewrote code-map files for areas this item does not touch (acts, presupposition).
  `main`'s code map was stale; it is advisory and is regenerated on merge.

## Self-review against BUILDER-CHECKLIST

1. PASS (no new field). The relayed `status_text` stays a typed string, and its relay checks are unchanged
   (`tests/test_relay_binding_inventory.py`, in the selected run).
2. PASS. Each task line is mapped to a commit and test in "Deliverables". `git diff main...HEAD -- ve/` adds no Python
   copy of a Lean decision (only the assurance pins changed), and no permanent report test was added.
3. PASS. S1-S5 each fail a named check. trust_mutants (0 mutants, explained) and its JSON are committed.
4. PASS. Rights output is byte-identical (RightsChecks `#guard`s, test_rights_report_parts 71 passed). The soft line on
   every recorded fixture is compared base vs head in `delta.json`. Rust has no soft-conflict status text
   (`grep -rn "coherent situation" rust/`: none).
5. N.A. No field Python reads changed or was added.
6. PASS. Merge base b81b82ef9 is main's tip at start. The chain runs the gate on the final HEAD.
7. PASS. DELTA rows 1-3 cite R1, R3 and R16 with their tests; review-ready's `ruling_verdict` passes all three.
8. PASS. Every changed output is in DELTA row 1 (`delta.json`, 4 records). The step-1 probe covers every soft
   CONFLICT-FREE answer in the 26 files and both fixture files.
9. PASS. `select_tests.py --base b81b82ef9`: 512/590 units, including tests/test_soft_norms_lean.py and
   tests/test_rights_report_parts.py. S1/S2 fail tests in tests/test_soft_norms_lean.py.
10. N.A. No new theorem. The new `#guard`s are covered by S1-S4.
11. N.A. No budget logic changed. The `budget` value is only quoted (the delta test checks budget 7 and 10000).
12. N.A. One string function; no new Lean call or enumeration.
13. PASS. No test removed or renamed.
14. PASS. Both directions: no model gives `none supplied` and a model gives `yes`
    (`test_soft_conflict_free_without_a_coherent_model_names_no_search`, `#guard`s :129/:130); `<k>` = `<j>` and
    `<k>` ≠ `<j>` (:129, constructed test). Claims cite their commands above. Spec re-read is listed.
15. PASS. Overclaim: "every JSON field byte for byte" → `test_soft_no_search_delta_keeps_every_quoted_value` (field
    equality and key set); "no printed count changes" → evidence/step1-output.txt; "rights unchanged" →
    RightsChecks.lean and test_rights_report_parts. No deliverable was cut. Every new check can fail (S1-S5). Limits: N.A.
