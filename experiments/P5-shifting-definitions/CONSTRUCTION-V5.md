# Round-4 construction repair (2026-09-22)

Revision 5 repairs the two blockers and two validity issues from the fourth
blinded review. All work uses local computation and free token counting; paid
calls and spend remain zero. This is a construction audit, not an efficacy claim.

## Artifact blinding

`execution-inventory.json` now retains only opaque ID, family, split and vocabulary
size per packet. The original design inventory retains aggregate budgets and
counts but no slot manifest. Current planted kinds and slot IDs are serialized
only in `labels.jsonl.gz`. Formal graphs no longer duplicate the slot object or
negative label. The checklist explicitly bars every hidden formal, label and
historical review artifact. A gate decompresses and greps tracked non-barred P5
artifacts for label fields, gold fields and label-bearing slot strings; a
regression test also checks the blacklist is individually documented.

The ID namespace changes from v4 to v5 using the same private nonce. This is
necessary because the previous IDs' labels were published in Git history.
The key is unchanged, never committed or selected using gate results.

## Uniform localisation

Every packet has exactly two gold sets: the singleton consumer and the
producer/consumer pair. These are neutral inspection anchors on benign packets.
Both defect kinds receive identical grading: a correct rejection, correct kind,
source-grounded explanation and either exact set earn detection credit; the
producer alone does not. A benign completion requires approval, issue `none`,
and an empty response location list. Gold anchor shape is identical across all
three kinds and is never included in judge or rater requests. Fresh review
annotations record the same singleton/pair shape, including benign anchors.

## Read senses from records

All 16 inference paragraphs state premises by content using four frames:
Because, Since, Given that, and It follows that ... because. No inference,
including alternative conclusions, contains a parenthesised sense definition.
The glossary and authoritative conditional records retain the sense meanings;
readers recover the relevant sense from the record that licenses each inference.
Only actual premises of the source inference are rendered, avoiding redundant
context that could license another same-term conclusion. VE retains the formal
parent block separately. This is still a deterministic offline draft; independent
Qwen prose and fresh isolated reviews remain required before scoring.

## Matched reference profiles

Four blocks each establish two senses of a term on a comparison lot, then a
result on another unit, followed by its immediately-referencing consumer.
Decoy producers independently choose lot or sample via a fixed family stream;
they do not all share the critical required unit. One block is critical; the other three are sound decoys. Its position is selected
by a fixed family stream without reading the variant. Every reference has
exactly three prior conclusions with the same term, two distinct senses and
two distinct units. This is checked per packet, not merely in aggregate. The
maximum-referent-count heuristic therefore ties four ways on every packet and
has zero unique correct localisations. This does not eliminate all possible
localisation shortcuts or establish scientific difficulty.

Four ambiguous terms (one critical and three decoys) replace the previous three.
Both senses are actually used in each packet. There are still 28 families, 84
slots, six declared leaves, 16 steps, a fork and join, and fixed source records
within siblings. The soundness gate independently parses public records and
prose, recovers senses, checks each claimed inference and computes whole-source
closure. Formal countermodels and proof certificates are additionally replayed
in Python and Lean. The 2,048 common-packet cap is unchanged.

Seeds, namespace, frame schedule, classifier hyperparameters and permutation
criterion are fixed before the final leakage run. No seed/nonce acceptance
search is permitted. The previous node-feature sense-ID probes now observe
missing sense tags; record-reading belongs to the semantic audit. All candidate
probes are refitted under 199 within-family permutations with the same max-test
criterion, p >= 0.05.

Export:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run python experiments/P5-shifting-definitions/run_p5.py review --export /private/tmp/p5-review-v5.json
```

This produces three path-only assignments, with one sibling per family in each.
Give a reviewer one assignment only; use a fresh model context for each file.

The initial v5 matched-profile construction was rejected: giving every decoy
producer the critical required unit leaked smuggle through sample-count
comparisons (best 56/84, adjusted p=0.005). Its report remains in the leakage
attempt ledger. Decoy unit choices now use a separate label-independent family
stream; no nonce, seed or probe hyperparameter was searched. This is an explicit
construction change following a failed gate, not an unreported acceptance run.
