# Round-3 construction repair (2026-09-22)

This revision implements the operator's three requested repairs and permutation
null criterion, with $0 paid calls. It preserves the accepted four-way source
records, 16-step argument design, 28 families and 84 assigned slots. V3 results
remain historical evidence; none approves these replacement packet hashes.

## IDs and isolation

All 84 IDs are 128-bit HMAC-SHA256 outputs keyed by one private 256-bit random
nonce stored outside the repository with permissions 0600. The key is never
serialized into manifests, material archives, prompts or commits. Regeneration
reuses it; neither IDs nor the nonce are selected using leakage results. The
regression suite checks the disclosed v3 enumeration against every new ID.

The four source cells remain fixed within a family. Thus the family-transductive
unfired-cell attack remains a reason for strict isolation. Calls and offline
editors accept exactly one dossier per context; few-shot examples are rejected,
and every transcript entry must bind the current item. Review and explanation
exports contain a path-only manifest with three family-disjoint assignments.
Each file holds one packet, without a node/parent block. Each reviewer receives
one assignment only; model contexts reset for every file. Imports reject
reviewer/rater/adjudicator identities exposed to siblings, including prior
submissions. Two reviews per packet require disjoint reviewer pools, including
a human/project lead for each packet. Never concatenate assignments or supply
the entire directory tree to a reviewer.

## Prose

The shared argument has 16 topologically ordered prose paragraphs. Each step
states premises by content; its own bracketed step label supports localization.
Only VE requests add the node/parent block. Unqualified references name the
immediately preceding result, so their referents are unique without parent IDs.
The critical sense/unit inference remains unqualified and is not repaired.
Exactly three noncritical steps use the same reference device. A separate
family-seeded random stream selects these steps without reading the label.
Eligible steps must actually depend on the immediately preceding step; the
second fork branch is excluded. The critical reference does not have a fixed
ordinal rank among the four references.

These are deterministic offline prose drafts, not independent Qwen paraphrases.
Fresh blinded source-fidelity review remains required. The previous gate and
provisional v4 report are retained in the leakage-attempt ledger; the provisional
v4 placement was changed because its critical reference was always last, not
because its label-classifier result failed. The private nonce was unchanged.

## Leakage criterion

The gate fixes three logistic probes, two depth-3 trees, the previous reviewer's
unit/rank rule, and 555 single-feature majority lookups (561 candidates total).
It repeats the entire best-of-k selection on 199 label permutations within
families, preserving one of each label per family. All fitted classifiers and
lookup mappings are refitted. Label-dependent stratification is regenerated;
vectorizers and scalers use training folds only. A nonconvergent fit blocks.

The one-sided max-statistic p-value is
`(1 + count(null maximum >= observed maximum)) / 200`.
The gate passes at **p >= 0.05**, replacing the flat one-third cutoff. Seeds,
hyperparameters and the nonce are fixed; no acceptance search is performed.
This shortcut screen is not evidence of scientific efficacy.

## Export for the next independent review

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run python experiments/P5-shifting-definitions/run_p5.py review --export /private/tmp/p5-review-v4.json
```

The JSON is an assignment index, not an 84-packet batch. Assign exactly one of
its three lists to each reviewer and start a fresh model context for each file.
