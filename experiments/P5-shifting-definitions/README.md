# P5 materials and staged duel runner

All 12 distinct Gemini study configs now have one billed Vertex ADC calibration
smoke, costing **$0.053782 total** under the separate $0.50 authorization.
The exact-config correction is zero for 11 configs and 139 tokens for the
verdict-schema config. The retained provider smoke separately verifies at
`17 native + 47 config overhead = 64 billed`. See the latest entry in
[AMENDMENTS.md](AMENDMENTS.md). To recheck both cached
smokes with no provider calls, run `probe --offline`; `preflight-openrouter
--offline` checks Qwen only.

The altered-reference paraphrase is repaired by a recorded source-only rule.
The independent REVIEW gate remains open: see
[PARAPHRASE-REVIEW.md](PARAPHRASE-REVIEW.md) for the exact checks and export.
No dev or scored inference ran in this repair session.
Original design aggregate budgets are retained; revision 5 redacts slot labels. Read [AMENDMENTS.md](AMENDMENTS.md) for the
explicit 1,024-billed-token author/repair change and optional Qwen judge-only
replication. Neither is silently represented as the original preregistration.

84 slots: four dev families × shift/smuggle/benign = 12; 24 disjoint scored
families × three variants = 72. Eight scored families each declare 20, 40 or 60
predicates; dev uses 20/40/60/20. Each has six declared leaves, 16 deductions,
two branches and a join. Predicate environments and claims have identity
bindings; hidden whole-premise countermodels falsify flawed original roots.
Bridge-augmented reference proofs are hidden and never online trusted premises.
The shared dossier, including node IDs, records, complete premises and possible
senses, is identical across arms. Siblings share the same sense descriptions; sense IDs and glossary positions
are independently permuted per packet.

The reference generator is **not** the online VE author. Every X/S/VE author
starts from the same final prose, and all authoring/search/repair work is charged.
The English renderer produces every subclaim and the complete argument.
The 84 retained independent Qwen responses replace the original offline drafts.
They undergo exact glossary-parenthetical sanitation and recorded source-only
reference restoration. All final hashes still need independent semantic review;
this delivery does not claim ready-to-score prose or scientific efficacy.

| Scenario | Maximum API + CPU + provider/calibration smokes | Remaining inside $40 |
|---|---:|---:|
| `primary` | $33.9097270016 | $6.0902729984 |
| `dual_judge` | $35.2512920096 | $4.7487079904 |

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
uv run python experiments/P5-shifting-definitions/run_p5.py review --export /private/tmp/p5-review-v5.json
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
by a successful unit test. The original `inventory.json` retains UNBUILT aggregate budgets;
its slot labels are removed under revision 5; `execution-inventory.json` contains build/count status.

To rebuild all paraphrases from retained responses without dispatch or billing
events, use `paraphrase --offline`. It applies the same exact glossary-sense
parenthetical sanitiser to every slot and retains other validation failures as
exclusions. Refreeze after rebuilding. The leakage gate includes three probes
of the exact paraphrased argument as well as the original packet/VE node probes;
independent review and source-soundness gates still apply to the resulting prose.

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

Construction revision 5 addresses the fourth blinded review. Inventories no
longer publish label/slot mappings; the HMAC namespace changes to invalidate
previously disclosed IDs. Gold location sets have the same singleton/pair shape
for every kind. Four natural inference frames omit sense tags; meanings must be
recovered from records. Four immediate references each have three same-term
referents spanning two senses and two units, balanced within every packet.
See [CONSTRUCTION-V5.md](CONSTRUCTION-V5.md) for grading and audit details.

Every call/editor context contains exactly one dossier; few-shot pools are
forbidden. Review and explanation exports are path-only manifests with three
family-disjoint assignments. Each file holds one packet. A reviewer may receive
one assignment only, and each model review uses a fresh context per file.
Imports reject sibling exposure under the same reviewer/rater identity,
including across earlier submissions. Never concatenate the assignments.

The leakage gate refits every probe under 199 within-family label permutations
and compares the observed best-of-k accuracy to the permuted best-of-k null.
It passes at **p >= 0.05**, correcting for feature/probe selection. Three logistic
probes, two depth-3 trees, the prior reviewer's rule, and all single-feature
majority lookups are fixed before the run; seeds, nonce and hyperparameters are
not searched. This screen does not establish semantic readiness.

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
