# Design handoff: P1 deference and P5 shifting definitions

2026-09-21. **Design and preregistration only; no API calls, no scored runs,
no external publication.** The companion inventories are offline assignment and
maximum-token accounting artifacts. P1 selects existing material IDs; P5 records
construction slots, explicitly `UNBUILT`. Neither inventory is a frozen prompt
bundle or evidence that a model, tokenizer, new runner, or material gate passed.
`P5` is this study's requested directory name: it implements **F2 / the duel
component of PLAN-V3 package 4**, not PLAN-V3 package 5 (drift/evidence).

## 1. Scientific basis and precedence

Read [PLAN-V3](../PLAN-V3.md), “What the reviewers changed,” packages 1 and 4,
and “Claims we stop making”; [positioning](../design/positioning-vs-debate-theory.md)
§§4, 6, 9; [protocol](../design/ve-protocol-design.md) §§2.2–2.5, §4/F2 and
both **2026-09-21 correction banners** in §§3(a), 4/F0. The corrections override
the old lead-case, zero-total-cost and obfuscated-arguments framing. A valid
conditional proof says nothing about the truth of its premises. Identity binds
symbols, not their intended senses. A distinguishing model between formulas
alone does not refute an inference from its actual premise set.

Design review inputs: [Astra review](../../manage-agents/reviews/plan-review-astra.md)
§§2–3, 6–7 (existing controls, matched total cost, independent translations,
small cluster counts); [Fable review](../../manage-agents/reviews/plan-review-fable.md)
§§2–4, 7 (missing F2, worst flaw, deference harm, 10-point margin, oracle/random
harness checks). The follow-up [Astra prereg review](../../manage-agents/reviews/prereg-review-astra.md)
and [Fable prereg review](../../manage-agents/reviews/prereg-review-fable.md)
are incorporated in the revised study-specific contrasts, controls, pilot
framing and budgets. Study-specific schedules and intervals below supersede
earlier matched-dollar, output-cap and t-interval assumptions.
These files are external to this repository; the paths resolve
from this checkout and must be archived with the later freeze.
[Paper audit](../paper/AUDIT.md), findings 1, 3, 6, 7, 9, 13 and “Critical-review
synthesis revision,” requires accurate assurance scope, disclosure of failed
gates/floors, untruncated cluster intervals, limited leakage claims, and an
external timestamp. Prior E4 outcomes are already public within the project:
reuse here is a new intervention on known materials, not a pristine task holdout.

Literature claims here follow the locally read positioning note by section:
SC §4.4.2/D5.5 and §5.2 already credit cross-examination with avoiding inconsistent
branch definitions; PE §8 already proposes proofs plus debate. No novelty claim
is attached to either idea. These documents do not verify the survey's flagged
percentage claims or estimate their population frequencies.

## 2. Shared execution contract to implement before scoring

Reuse the existing item/condition/trial contract in
`experiments/E2E4/materials.py` and `experiments/trial_analysis.py`, not the
old E4 condition names or estimand unchanged. The current
`experiments/E2E4/analyze_e4.py:analyze` specifically compares
`checked_countermodel - prose_critique`; **it cannot analyze P1 or P5 as-is**.
Implement a thin adapter and the prescribed analyses in a later execution change.
Do not turn the inventory checker into a paid runner.

Every assignment must have an append-only record of item/template/split, arm,
model/provider revision, role and turn, visible message bytes and role boundaries,
prompt hash, response bytes, parse status, tools requested and returned, checker
build/query/artifact digests, elapsed time, billed input/output/reasoning tokens,
fee-inclusive dollars, and remaining budget. Labels, generator fields and hidden
countermodels live in a separate local scorer file. Provider messages are built
from an allowlist; never send `payload._audit`, ground-truth labels or the full
inventory to a model. Freeze the exact renderer, prompts, parser, model IDs,
sampling settings and condition order. Shuffle complete item-arm blocks with
seed 20260921; separate conversations prevent cross-arm contamination.

Temperature 0, one sample per item/arm/judge, seed 20260921 where supported
(record unsupported seeds). No paid retries, replacement samples, optional
stopping on results, or silent substitutions. A 120-second wall timeout per API
call and the per-call billed-output cap apply, including hidden thinking tokens.
Set SDK, transport and provider retries to zero (one attempt), disable automatic
paid tool continuations and dispatch serially. Reserve worst-case billing before
dispatch and keep timed-out calls reserved until reconciled; cancellation is not
proof that billing stopped. Unknown billing stops further dispatch. P1 includes
a separate ten-call/$1 output probe and deterministic reduced schedules; P5
uses its scheduled dev calls to validate total-output feasibility.
An endpoint that cannot enforce these caps fails preflight. Input limits include
system messages, tools, schema and the whole visible history; exact provider
counting/tokenization must pass before calls. Never truncate source evidence or
silently shorten a transcript. Full cached and uncached billing is logged; budget
planning assumes no cache, batch, credit, subscription or promotional discount.
Unspent capacity is not permission to add items or hypotheses after outcomes.

Before inference reserve each complete block's worst remaining cost against the
study's ledger. If insufficient, stop before the block and report the incomplete
study, with all assigned missing trials retained as failures. No cross-study
borrowing beyond the separate $30/$40 caps. Pricing changes, unavailable model
revisions, inadequate contexts, unresolved ground truth, unimplemented role
boundaries or a failed known-answer test require a dated amendment **before
scoring**, not an improvised run. Dev calls count against these same caps and
use only the scheduled dev inventory; no dev outcome is asserted here.

## 3. Prices and cost boundary

| Ledger key | Planned endpoint | Input / output per million | Fee |
|---|---|---:|---:|
| pro | Vertex global standard `gemini-3.1-pro-preview` (pin served revision) | $2 / $12 | 0 |
| replication | OpenRouter `qwen/qwen-2.5-72b-instruct`, DeepInfra fp8, fallback disabled | $0.36 / $0.40 | 5.5% |
| weak | OpenRouter `meta-llama/llama-3.1-8b-instruct`, DeepInfra fp8 Turbo, fallback disabled | $0.02 / $0.04 | 5.5% |

OpenRouter assumptions are exactly the price-table rows and credit fee in
[`~/code/manage-agents/api-pricing.md`](../../manage-agents/api-pricing.md),
as of 2026-09-21. That file **does not quote Vertex rates**. The missing rate was
checked separately against Google's [Vertex pricing, Gemini 3.1 Pro Preview,
standard global requests at <=200K input tokens](https://cloud.google.com/vertex-ai/generative-ai/pricing)
on 2026-09-21: $2 input and $12 output, including reasoning. Priority and
long-context rates are not used. Availability/rates must be checked and recorded
again in the pre-scoring freeze; these are accounting assumptions, not purchased
capacity. Qwen72 is an open-weight family replication, **not claimed to match
Gemini's frontier capability**. Weakness of Llama8 is a size-based design choice,
not an observed calibration result.

For each row, cost = calls × (input_cap × input_rate + billed_output_cap ×
output_rate) / 1e6 × fee_multiplier. Inventory rows include every model role,
optional replay continuation, dev/probe call, isolated answer, follow-up, repair
and maximum pushback call. There is no P5 cost-matching top-up.
Checker tokens = 0 model tokens; checker bytes returned to models count in input.
Local CPU, engineering and manual validation time are reported separately.
P5 additionally charges a notional $0.024/core-hour, at most 60 core-seconds
per item-arm ($0.0004), against attributed cost under the matched ceiling; this
is an explicit accounting assumption, not a cloud invoice. Exceeding it is a cost failure, not free work.
P1 local bookkeeping/replay has a $0.25 allowance from its reserve. Neither
experiment measures engineering cost amortization in deployment.

## 4. Current files and exact offline commands

```text
experiments/PREREG-DESIGN.md                 shared design / execution boundary
experiments/prereg_inventory.py             stdlib-only counts and cost audit
experiments/P1-deference/PREREG.md           P1 statistical and intervention plan
experiments/P1-deference/inventory.json      existing IDs, subsets, cost rows
experiments/P5-shifting-definitions/PREREG.md P5 material and statistical plan
experiments/P5-shifting-definitions/inventory.json  84 unbuilt slots, cost rows
```

Run from repository root; none of these commands performs inference:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
python3 experiments/prereg_inventory.py --check
# Only if intentionally rebuilding the design inventory before freeze:
python3 experiments/prereg_inventory.py --write
python3 experiments/prereg_inventory.py --check
shasum -a 256 experiments/P1-deference/PREREG.md experiments/P5-shifting-definitions/PREREG.md
shasum -a 256 experiments/PREREG-DESIGN.md experiments/prereg_inventory.py experiments/P1-deference/inventory.json experiments/P5-shifting-definitions/inventory.json
```

The future execution change must create, under each study directory,
`prompts.json`, `materials/{dev,scored}.jsonl.gz`, `labels.jsonl.gz`,
`freeze.json`, `checks/{known-answer,tokenizer,lean-replay}.json`, and
`runs/<run-id>/{trials.jsonl,costs.jsonl,analysis.json}`. P1 materials may reference
existing archives by digest instead of duplicating them. P5 also needs
`materials/{graphs,paraphrases,review-ledger}.jsonl.gz`. The future runner's
exact export/preflight/run/analyze commands must be added to `freeze.json` and
committed; **there is no working paid-run command in this design delivery**.
Known commands for the later Lean evidence gate, from `lean/`, are
`lake build`, `lake exe ve_conformance check-certificate PATH/query.json` and
`lake exe ve_conformance PATH/countermodel-cases.json` (the last file uses the
case schema illustrated in `conformance/countermodels.json`).
Every scored certificate and negative witness must appear in the replay ledger.
Python/Lean disagreements stop the freeze; a Lean theorem never silently upgrades
the Python graph, serialization, channel authentication or prose fidelity.

## 5. External timestamp, not performed here

Before scoring, an operator publishes the **SHA-256 of each exact `PREREG.md`**
in a dated public GitHub gist/release or submits it to OpenTimestamps and retains
the receipt and subsequent verification. Also publish an aggregate manifest hash
covering these inventories, this design, executable/prompt/material hashes,
prices and model revisions. Store the public URL/date or `.ots` proof in the
freeze record. A local commit date alone is insufficient. Publish amendments and
a new hash before affected scoring; retain the prior version and explain every
change. Do not label these documents externally timestamped until that happens.
