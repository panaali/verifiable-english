# Measured cost ledger

Model: `gpt-6-astra`. Date: 2026-09-22. One implementing agent; no delegated or independent review.

Cutoff: **2026-09-22T23:11:09.196Z**. Start: 22:55:57 UTC (first clock observation).
Costs after the cutoff (final ledger write/commit/reply) are excluded, not estimated.

| Phase | Wall seconds | Input tokens | Cached input subset | Output tokens | Reasoning subset |
|---|---:|---:|---:|---:|---:|
| model_review | 157.000 | 213,170 | 179,200 | 2,198 | 1,144 |
| formalisation | 144.101 | 102,988 | 94,976 | 5,406 | 1,550 |
| proof_repair | 284.266 | 948,956 | 920,960 | 7,357 | 1,371 |
| checking | 326.829 | 831,574 | 815,360 | 9,594 | 2,349 |
| **Total** | **912.196** | **2,096,688** | **2,010,496** | **24,555** | **6,414** |

These are actual cumulative Codex `token_count` deltas, not a word-count estimate. Input tokens
include the initial instructions, tools and repeated context for each request; cached input is
a subset of input, and reasoning is a subset of output. Do not add either subset again.
This is usage accounting, not distinct transcript length or a dollar bill. Subscription quota
only; no paid model API, GPU, dollar estimate or hidden parallel worker cost is included.

The phase windows are coarse, contiguous wall-clock measurements. Model review includes source
retrieval and idealisation decisions. Formalisation includes writing SPEC and the first proof.
Repair includes compiler diagnosis, checklist writing, and non-vacuity witness authoring/repair.
Checking includes serial build, VE skeleton/certificate preparation, documentation and ledger
work through the cutoff. Token events are charged to the window of their timestamp; requests
can straddle a boundary. This is not CPU time or an independently observed human-work estimate.

## Attempts and compute

- **4 failed invocations out of 6** standalone Lean development runs; multiple cascading diagnostics count as one invocation.
- Attempt 1: grouped structure-field syntax and unassisted order cancellation.
- Attempt 2: nonlinear order/cancellation needed explicit rational lemmas.
- Attempt 3: missing `Rat.mul_sub` name and rational `decide` reduction.
- Attempt 4: the main proof and all original 11 result audits passed.
- Attempt 5: newly added witness tactics failed when `dsimp` made no progress.
- Attempt 6: the complete source and all 13 audits passed.
- Development Lean subprocess wall time: **14.806 s** (all attempts).
- Clean-worktree serial whole-project build plus final audit: **66.243 s** across 44 commands; no initial local `.lake` directory.
- Final fresh standalone proof/audit invocation: **2.646 s**, already included above.
- VE relational search and Python/Lean replay: **1.530 s** (excludes Python startup and rendering).
- All compute durations are subsets of phase wall time; do not add them to that total.
- No failed whole-project builds or VE certificate replays. The unavailable in-app browser was a source-retrieval fallback, not a failed proof.

Reproduction evidence: `attempts.jsonl`, `verification.json`, and
`qualitative-verification.json`. `cost.json` retains only token-counter snapshots,
not conversation content. `cost_ledger.py` regenerates the accounting from this
worker's local rollout; the original private transcript is not part of the commit.

One pilot on a fixed idealisation is not an affordability benchmark across physics,
and does not compare against a measured debate run. Physical validation and a proved
Lean-to-VE translation remain additional costs.
