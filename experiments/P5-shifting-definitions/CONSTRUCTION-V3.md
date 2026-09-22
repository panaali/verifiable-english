# Round-2 construction repair (2026-09-22)

Historical report, superseded by [CONSTRUCTION-V4.md](CONSTRUCTION-V4.md).

The operator requested this revision after a second blinded NOT READY review.
The original design inventory and preregistration remain historical records;
this construction now uses **16 deductions and six declared leaves**, as
explicitly requested. No input/output token caps, dollar caps, model assignments,
scored sample counts or scoring rules were amended. This work used **$0**:
local construction/checking and free provider countTokens only.

## Construction

- Four source branches contain the complete product of two senses and two
  units (lot and sample). The required downstream unit is balanced before label
  assignment: 14 families require the sample and 14 require the lot. For each
  label, 14/28 selected results concern a sample. Benign keeps required unit and
  sense; shift changes only sense; smuggle changes only unit. Neither direction
  of property transfer is stated as a premise.
- Source records remain fixed within each family. The fourth branch is genuine
  unused conditional context. The three selected branches all retain the same
  unigram workload, including the unused checks and outcomes.
- The critical predicates have reserved symbols and cannot recur accidentally
  in the ordinary chain. Both still occur on a separate comparison lot. Both
  senses of each decoy ambiguity are asserted and used in every variant.
- Sense IDs and glossary positions use separate deterministic, per-packet random
  permutations, without sorting by semantic role. Natural-language source records
  do not expose the IDs. Relation descriptions, inference openings and conditional
  alternative wording vary independently of the selected branch.
- Nodes contain the complete proposed prose once. There is no duplicate
  `argument` field, including in paraphrase input/output. The common request omits
  the redundant possible-senses header; ambiguous uses retain inline glosses.
  Opaque packet IDs are fresh for this revision.

## Checks

All 84 slots regenerate; 28 actual formal graph shapes have distinct structural
invariants. All 28 benign roots have certified derivations and all 56 flawed
roots have whole-premise countermodels. Lean replays 3,192 queries successfully,
including every intended benign edge, proposed/bridge-augmented proof and flawed
root witness. The offline regression suite contains 24 passing tests.

The current leakage criterion is the best-of-k permutation-null comparison
(p >= 0.05), specified in P5-4. The table below records the historical v3
measurements; its old flat chance cutoff is superseded.

| Probe | Correct / 84 | Accuracy |
|---|---:|---:|
| Token logistic, leave-family-out | 28 | 33.33% |
| Structure logistic, leave-family-out | 28 | 33.33% |
| Combined logistic, leave-family-out | 28 | 33.33% |
| Node relations, depth 3, stratified 6-fold | 18 | 21.43% |
| Node relations, depth 3, stratified-grouped 6-fold | 24 | 28.57% |
| Adapted reviewer unit/rank rule | 28 | 33.33% |

The node feature table includes every node, its unit type, sense ID/order/rank,
parent/conclusion unit relations, graph degrees, alternatives and marker phrases.
It also includes aggregates and the conditional-alternative node selected by
public text alone. It uses no labels to extract features, no gold location and
no logical chaining. An unparsed node blocks the gate rather than disappearing.
The ungrouped requested split and the separate grouped split are both reported.

As a positive control, the same new probes on the rejected round-2 corpus from
commit `4ef5bfe005ee8b4d38b98aed69062394e0130714` score 75/84 (89.29%),
76/84 (90.48%) and 72/84 (85.71%) respectively. This reproduces the reviewer's
closed-form accuracy and demonstrates that the new gate detects the old leak.

The first provisional four-way construction in this revision failed the node
trees at 32/84 and 37/84 despite the original probes being at chance. It retained
family-shared sense-code/order permutations and let the critical predicate recur
in the ordinary chain. Those mechanisms were changed as described above; the
failed report is retained in `checks/leakage-attempts.jsonl.gz`. No failed attempt
was converted into a passing receipt by changing the threshold or CV seeds.

## Unchanged context caps

All stage fixtures (including schemas, system envelopes and maximum generated
history reserves) pass exact tokenizer checks without truncation. Maximum common
request: **Gemini 1,444 / 2,048; Qwen 1,417 / 2,048**. Maximum Qwen paraphrase
input: **1,362 / 4,096**. The preregistered conservative final-judge allocation
remains 2,048 + 4,096 + 1,024 + 1,024 = 8,192 of 10,000 input tokens.
See `checks/tokenizer.json` and `checks/prose-token-fit.json` for per-request
wire hashes and counts.

Independent Qwen prose, fresh independent human/project-lead review, external
timestamp and paid provider/dev gates remain outstanding. These construction
checks establish no scientific efficacy or ready-to-score status. Reviewers
should inspect the new blinded export without reading this construction note,
labels, graph artifacts or gate prediction receipts first.

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run python experiments/P5-shifting-definitions/run_p5.py review --export /private/tmp/p5-review-v3.json
```
