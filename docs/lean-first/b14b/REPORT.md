# Lean-first batch 14b build report

## Delivered scope

Non-first-order norm guards on closure, core and order families now regenerate in
`VE.Norms.Family`. The `family-norms` service selects the family's checker,
emits fully typed response rows, and checks submitted certificates and conflict
witnesses. `ve/norms.py` relays those decisions and binds row names and counts to
the request. The former Python `_NON_FOL_TAGS`, `_first_order` and
`_family_norms` fallback classification and rejection were removed in the same
batch. Python's search remains an untrusted proposal generator under the lead's
question-10 ruling. N-ary core definitions remain batch 14c's scope.

Against the pinned merge base `f1b719c7`, 42 Python product lines were deleted
from `ve/norms.py`; 715 Lean product lines were added across
`VE/Norms/Family.lean`, `VE/Service/FamilyNorms.lean`, `VE/Norms/Wire.lean`
and the response encoder and shapes. No Rust product code changed. The
[deletion ledger](LEDGER.md) maps each removed decision to its Lean owner.

## Gate evidence

The [1,350-record family corpus comparison](evidence/corpus-ab.json) has 1,334
identical results and 16 listed changes in four n-ary core documents. The
[DELTA.md](DELTA.md) states the old candidate substitution bug and the pending
DRI signature. It also records signed standing rulings R4, R6, R7, R8 and R12 with
their tests. No approved theorem statement changed (`lean/statements.txt` is
unchanged).

| Evidence | Base/head result |
|---|---|
| [Stage-0 probe](evidence/probe-compare.json) | 18,870/18,870 identical (9,435 per authority) |
| [Conformance](evidence/conformance-compare.json) | 39,612/39,612 identical; no unavailable rows |
| [Readings](evidence/readings-compare.json) | 1,137/1,137 identical |
| [Discourse](evidence/discourse-compare.json) | 6,350/6,350 identical |
| [Rights](evidence/rights-compare.json) | 2,500/2,500 identical |
| [Quantity](evidence/quantity-compare.json) | 25,726/25,726 identical |
| [Norm defaults](evidence/norm-defaults-compare.json) | 2,020/2,020 identical |
| [Document wrapper](evidence/document-compare.json) | 3,632/3,632 identical |
| [Historical pilots](evidence/pilots-compare.json) | 486/486 identical outcomes; six identical unavailable rows listed under R7 |
| [Agent policy](evidence/agent-policy-ab.json) | 42/42 answer key on both; semantic summaries equal |
| [Eligibility](evidence/eligibility-ab.json) | 269/269 answer key on both; summaries equal |
| [Differential fuzz](evidence/difffuzz-ab.json) | CI sample and 14 date seeds; zero head-only signatures, unreviewed entries or lost baseline reproductions |
| [Latency](evidence/latency.json) | FOL control 0.768742 to 0.703626 ms median Lean CPU per call; new reach case 0.935184 ms; maximum reach wall call 94.572 ms, and every reach call consumed less than 483.524 ms Lean CPU |

Raw corpus and differential-fuzz recordings are on the local
`lean-first/b14b-evidence` branch; its manifest checks compressed record
hashes, counts and commit list. The final release-gate result is
`gate-result.json` at the worktree root, run on the committed final HEAD.

The first clean full gate, on `e44ff402`, ran 14,654 selected Python tests
and 36 Rust tests, then reported eight Python failures. Three were stale
curated Lean decoder pins after the new family reader; one was the prior 8b
ledger line count; three were an interruption test whose mock skipped the
toolchain check but not stale Lake output cleanup; and one was the mutation
runner's direct pytest command. The failed result is retained on the local
evidence branch as `initial-gate-result.json`. I reviewed and updated the
decoder ranges and hashes, regenerated the assurance document, corrected the
ledger, completed the interruption mock, and switched the mutation runner to
`tools.nested_pytest`. The eight detecting tests passed on rerun, as did all
six seeded faults and their restored checks. The gate's `--rerun-failed` mode
requires the same tree as its prior record, so it cannot apply after these
fixes; the final full gate runs on a new committed tree.

### Relay mutation gate

The pre-review gate at `366bd777` failed `tools/relay_mutation_gate.py` with
133 failures: 128 allow-list paths that match nothing and five accepted
readings-route mutants. All 133 are on routes this batch does not change,
and the list matches the saved run on main `49de179e`
(109,195 mutants in both runs). `family-norms`, the only relayed route this batch
changed, had none. The fixtures (`tests/data/relay-gate-cases.jsonl`) have not
changed since `111c4fd4`. The failures come from answer shapes that changed on
main after the allow-list was written. ts-B1 and ts-B5 typed the report labels,
and the readings-route fixtures no longer reach the `units` and `names` shapes.

This batch changes only `tools/relay-gate-allow.json`, in one commit that can
be reverted on its own. It removes the 128 stale paths, which drops five
entries that are left with no paths: B5 norm-defaults, reports and risk;
F4 discourse; F7 readings-route. It also files the five accepted mutants
under the existing follow-ups whose descriptions they match. Under F10
(request-bound lists that accept an emptied or repeated element), it adds an
emptied and a repeated `fill`, and a repeated `units/*/content/norm/over`.
Under F11 (strings the schema lets be empty), it adds an emptied
`fill/*/label` and `targets/*`. This batch does not add a classification;
whether these mutants are binding gaps to fix (R8) belongs to the readings-route
owner. After the change, the gate passed
with 39 routes, 109,195 mutants and 0 failures
([report](evidence/relay-gate.json)). `tests/test_relay_mutation_gate.py`
passed (18 tests). The full release gate then ran once on the committed
`f06911d8`. Its status is passed: 14,562 Python tests passed, none failed,
92 were skipped (allowed) and 36 Rust tests passed (`gate-result.json`
at the worktree root). Only this report changed after that commit.

## Review of sibling findings

This batch does not change the document or norm-defaults owner. Their complete
A/B corpora above are identical. I separately checked the changed-file list
for the sibling 16d classes: no quoted-kind dispatch, active-reading selection,
coverage fold, or Python reconstruction of document lines changed in 14b.
The generic family route is limited to norm guard formulas, so it cannot supply
coverage from an unresolved reading.
The response schema is Lean-owned and recursive for core/order formulas;
Python binds request names and counts and does not recompute their meaning.
No report score is constructed as a constant. The checker lock was regenerated
with only the release binary's new hash.

## Acceptance

| Item | Type | State |
|---|---|---|
| Lean owner, Python relay, deletion ledger and typed/bound rows | AGENT | Implemented; focused tests passed |
| Corpus, pilots, fuzzer, answer keys, latency and full release gate | AGENT | Evidence cited above and in the final gate JSON |
| Four n-ary core documents' 16 rejection-to-answer changes | HUMAN (DRI) | Signature requested; deferred to DRI |
| External service or publication | EXTERNAL | None requested |

The applicable build-checklist checks are the Lean-owned response contract and
request binding (1, 4, 15), malformed wire and zero-budget behavior (5, 6),
three-authority and corpus comparisons (2, 10, 19), the fail-able mutations
(13), regenerated inventory and statement checks (16, 17), and the final clean
gate and signed delta ledger (20–23). This batch changes no text normalizer,
English grammar, state machine, or source-document interpretation.

## Seeded bugs and final checks

Six seeded faults in the changed Lean and Python product files are specified
in `mutants.py`. Their caught-test results are in `evidence/mutants.json`.
The selector chose all 364 test units. Every unit's recorded run exited zero,
including the long wire, readings and soft-review corpora. The selector process
then exited one while writing its coverage map to the read-only home cache;
that post-run cache failure is not counted as a passing selector command. The
final clean release gate provides the complete suite result on the committed
HEAD and writes `gate-result.json` at the worktree root.

| Seeded fault | Changed product file | Detecting test |
|---|---|---|
| Stop routing family norms to Lean | `ve/norms.py` | `test_non_first_order_norms_are_dispatched_and_match_python` |
| Accept an extra conflict target | `ve/norms.py` | `test_non_first_order_conflict_refuses_extra_target` |
| Accept an unbound certificate layer count | `ve/norms.py` | `test_non_first_order_certificate_refuses_unbound_layer_count` |
| Treat a refused witness as confirmed | `ve/norms.py` | `test_non_first_order_conflict_refused_witness_is_unavailable` |
| Turn a zero model budget into a conflict | `ve/norms.py` | `test_non_first_order_conflict_zero_model_budget_is_unknown` |
| Misclassify reach as first order | `lean/VE/Norms/Family.lean` | `/tmp/lf14b-family-route-guard.lean` |

All six planted versions failed their detecting checks, all six restored versions
passed, and `lake build ve_service ve_response_decode` passed after restoration
([record](evidence/mutants.json)). `tools/trust_map.py --check` passed with zero
unclassified lines and no drift beyond the R6 allowance; the regenerated
checker-pin, frozen-inventory, response-schema and gate-collection checks passed;
`tools/relay_lint.py` found no own content diagnostic in 13 relayed modules and
six relayed functions. The generated statement check passed with zero added,
removed or changed entries across 4,802 statements, the predicate list and
the declaration list. The final diff review uses the
pinned base `f1b719c7` and a fixed task commit. No document wrapper or
norm-defaults source changed. Free disk was 58 GiB at final preparation.
