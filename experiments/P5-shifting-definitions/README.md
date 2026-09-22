# P5 materials and staged duel runner

This build spends **$0**. No probe, dev, scored or paid paraphrase was run.
Original design bytes are retained. Read [AMENDMENTS.md](AMENDMENTS.md) for the
explicit 1,024-billed-token author/repair change and optional Qwen judge-only
replication. Neither is silently represented as the original preregistration.

84 slots: four dev families × shift/smuggle/benign = 12; 24 disjoint scored
families × three variants = 72. Eight scored families each declare 20, 40 or 60
predicates; dev uses 20/40/60/20. Each has six declared leaves, 24 deductions,
two branches and a join. Predicate environments and claims have identity
bindings; hidden whole-premise countermodels falsify flawed original roots.
Bridge-augmented reference proofs are hidden and never online trusted premises.
The shared dossier, including node IDs, records, complete premises and possible
senses, is identical across arms. All three siblings have the same glossary.

The reference generator is **not** the online VE author. Every X/S/VE author
starts from the same final prose, and all authoring/search/repair work is charged.
The offline editor runs in a separate process receiving only natural-language
dossiers. Its deterministic draft paraphrases are **not the independently
paraphrased Qwen materials promised by the preregistration**. The latter cannot
be purchased under this task’s $0 authorization. That gate remains blocked;
this delivery does not claim ready-to-score prose or scientific efficacy.

| Scenario | Maximum API + CPU + provider smoke | Remaining inside $40 |
|---|---:|---:|
| `primary` | $33.4097270016 | $6.5902729984 |
| `dual_judge` | $34.7512920096 | $5.2487079904 |

The original registered allowance was $37.5254702592 including CPU, before the
new separately itemized smoke overhead. X/S/VE use a $0.16 matched **ceiling**,
not matched actual spend. Full shared-paraphrase cost is attributed to each arm.
Actual fees, billed thinking, failed calls and infrastructure holds stay in the
ledger. Qwen replication reads the same frozen Gemini transcript; it is not a
second independently authored duel, and never replaces the primary Gemini panel.

From the repository root:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex
uv run python experiments/P5-shifting-definitions/run_p5.py generate
uv run python experiments/P5-shifting-definitions/run_p5.py inventory --count-tokens
uv run python experiments/P5-shifting-definitions/run_p5.py known-answer
uv run python experiments/P5-shifting-definitions/run_p5.py review --export /private/tmp/p5-review.json
uv run python experiments/P5-shifting-definitions/run_p5.py review --submit /path/to/completed-review.json
uv run python experiments/P5-shifting-definitions/run_p5.py review --adjudicate /path/to/resolution.json
uv run python experiments/P5-shifting-definitions/run_p5.py freeze --scenario dual_judge
uv run python experiments/P5-shifting-definitions/run_p5.py preflight --offline
uv run pytest -q tests/test_p5.py
```

`inventory --count-tokens` calls only free Vertex count_tokens and local pinned
native Qwen counters. Receipts contain each wire digest, actual base count,
reserved prior-output tokens and limit. Runtime counts the exact complete
transcript again; it never truncates evidence. A failed gate is not overridden
by a successful unit test. The original `inventory.json` remains the immutable
UNBUILT design inventory; `execution-inventory.json` contains build/count status.

Later, only under separate paid authorization, use these commands. The current
task does **not** authorize executing them. Every paid command defaults to a $0
cap and refuses dispatch without an explicit positive cap ≤40. The ledger is
study-wide across all commands and scenarios, not reset for each command.

```sh
uv run python experiments/P5-shifting-definitions/run_p5.py preflight-openrouter --cap-usd 40
uv run python experiments/P5-shifting-definitions/run_p5.py probe --cap-usd 40
uv run python experiments/P5-shifting-definitions/run_p5.py paraphrase --cap-usd 40
# Review both independent raters’ FINAL paraphrases, resolve all 84 slots,
# refresh free counts, freeze, publish aggregate timestamp, pass preflight.
uv run python experiments/P5-shifting-definitions/run_p5.py preflight
uv run python experiments/P5-shifting-definitions/run_p5.py dev --cap-usd 40
uv run python experiments/P5-shifting-definitions/run_p5.py explanations --split dev --export /private/tmp/p5-dev-ratings.json
uv run python experiments/P5-shifting-definitions/run_p5.py explanations --split dev --submit /path/to/dev-ratings.json
uv run python experiments/P5-shifting-definitions/run_p5.py scored --cap-usd 40
uv run python experiments/P5-shifting-definitions/run_p5.py resume --split scored --cap-usd 40
uv run python experiments/P5-shifting-definitions/run_p5.py reconcile
uv run python experiments/P5-shifting-definitions/run_p5.py reconcile --receipt /path/to/audited-adjustments.json
uv run python experiments/P5-shifting-definitions/run_p5.py explanations --split scored --export /private/tmp/p5-scored-ratings.json
uv run python experiments/P5-shifting-definitions/run_p5.py explanations --split scored --submit /path/to/scored-ratings.json
uv run python experiments/P5-shifting-definitions/run_p5.py analyze --split scored
```

`probe` performs only the two budgeted infrastructure smokes. P5 efficacy/output
feasibility uses its scheduled dev calls. Successful smokes are durable and
reused, including after a material refreeze with identical requests. Changed
model revisions/prices, unresolved billing, output overrun or source-label
mismatch stop dispatch. `reconcile` reports holds or accepts documented block
releases/allowance adjustments; it cannot fabricate a refund or erase unknown
billing. A panel halt is retained, missing assigned outcomes score zero, and
completed responses are reused on resume. Local oracle receipts are fsynced
before subsequent paid stages so restart does not silently change history.

Independent review instructions and open questions are in
[REVIEW-CHECKLIST.md](REVIEW-CHECKLIST.md). Explanation ratings are separately
blinded to arm/model; two identified raters and source-grounded adjudication
are required. Dev contract compliance is ≥90% separately for each judge, with
source-fidelity review and coverage reporting. All scoring joins validate
assignment IDs and packet hashes; missing outcomes remain assigned failures.

Analysis uses 20,000 paired **family** bootstrap draws (seed 20260921), recomputes
both worst-flaw minima, and reports the Bonferroni Wilson sensitivity/boundary
hull. It reports benign harm, per-flaw and vocabulary results, practical oracle
coverage failures, unsupported approvals and authoring failures. The lone judge
is a descriptive floor. There is no efficacy claim from construction proofs,
known-answer scores, independent paraphraser identity or a positive point estimate.

To timestamp, write the exact `freeze.json` manifest_sha256 followed by a newline
to `freeze-manifest.sha256`, publish it and retain its `.ots` receipt. The
preflight gate verifies that the receipt binds that exact file. Local commit
dates and self-asserted `passed` flags are not timestamp evidence.
