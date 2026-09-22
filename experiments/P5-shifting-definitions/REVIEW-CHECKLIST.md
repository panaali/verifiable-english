# Blinded review gate

Every one of the **84** packets needs two independent reviews before scoring,
including one human or project lead. Use disjoint reviewer pools for the three
assignments: no reviewer sees two siblings. The export index contains paths
only; give each reviewer ONE assignment and open each packet in a fresh model
context. Never concatenate assignments, build few-shot pools, or carry sibling
material into paraphrase, review, rating or adjudication contexts. Imports reject
repeated sibling exposure under the same reviewer/rater identity. Work
separately before comparing annotations.
Review packets contain no planted label, variant, split, formal witness or model
outcome. Review only the individually assigned exported packet files. Never
load the repository, an archive of siblings, or Git history into a reviewer,
judge or rater context. Replicators must keep construction/scoring artifacts
outside inference contexts. The following files are explicitly barred from
reviewers, raters, adjudicators, judge pipelines and replication model contexts
(paths relative to this directory):

- `labels.jsonl.gz`
- `materials/dossiers.jsonl.gz`
- `materials/scored.jsonl.gz`
- `materials/dev.jsonl.gz`
- `materials/paraphrases.jsonl.gz`
- `materials/graphs.jsonl.gz`
- `materials/anchored-labels.jsonl.gz`
- `materials/construction-ledger.jsonl.gz`
- `materials/review-ledger.jsonl.gz`
- `materials/rejected-v1.jsonl.gz`
- `materials/rejected-v2-initial.jsonl.gz`
- `checks/lean-replay-ledger.jsonl.gz`
- `checks/rejected-v2-generator.jsonl.gz`
- `checks/rejected-review-v1.json`
- `checks/round5-review-submission.json`
- `checks/round5-review-verification.txt`

Historical review annotations and formal witnesses can reveal labels even
without a planted kind field. These are offline audit/scoring inputs only.
Bulk packet archives also expose siblings; the scored/dev `group` field enables
family grouping and a transductive attack. Export one isolated packet through
the allowlisted pipeline; never attach these archives to a model context.
The private ID nonce is outside the repository and is never an attachment.

For each packet, recover and record:

- The intended meaning of every relevant use, anchored in specific source records.
- The original root, required assumptions, and which assumptions are declared.
- Whether the justification shifts a definition, needs an undeclared bridge, or
  is benign; localization anchors and supporting passages. Record exactly a singleton
  consumer and its producer/consumer pair for every kind, including benign
  inspection anchors. Both flaw kinds accept either exact set under identical
  grading. Benign answers are scored as approval/none/empty; their neutral gold
  anchors are not response requirements.
- Whether the prose preserves the proposal without repairing it, inserting a
  premise, changing the root or revealing the answer.
- Whether harmless synonyms and consistently used ambiguous terms remain benign.
- Time, identity, reviewer type/model family, corrections and uncertainties.

Every checkbox needs an explicit true/false answer. False or missing fields block
scoring. Disagreement requires a source-grounded, identified adjudication bound
to the exact reviews; alternatively leave the slot unready. Corrections invalidate
old packet hashes and require fresh independent reviews. A planted-label mismatch
requires construction repair and an amendment; it is never silently relabeled.

The previous 84-packet NOT READY review is retained against its old hashes and
cannot approve these replacement packets. Revision 5 retains fixed records across
siblings and uses four natural inference frames without parenthesised sense
tags. Recover each sense by reading the glossary and its licensing record.
Each of four immediate back-references has exactly three prior same-term
conclusions, spanning two senses and two units. Three are harmless; inspect all
four without silently repairing a sense or unit transfer. Only VE-arm requests
include a node/parent block. Conditional alternatives are not declared facts;
a sample relationship supplies no property-transfer rule in either direction.

The packet must pass tracked-artifact blinding, public-text soundness, reference
profile, token, structural and permutation leakage gates. These checks do not
establish semantic readiness. Are the senses recoverable and the prose natural?
Does the proposed inference conceal a plausible unstated bridge? These offline
drafts are NOT the registered independent Qwen paraphrases. Fresh independent
reviews against the exact replacement hashes remain required.

Explanation scoring is a separate post-inference task: two raters receive the
packet and answer without arm/model fields, assess source-groundedness, record
protocol recognition, and resolve disagreements before analysis. Missing ratings
remain failures; no paid automated grader is assumed.

Revision 6 historical review attachments are barred from blind contexts:
`checks/round6-review-submission.json`, `checks/round6-review-verification.txt`.
The latter explicitly discloses unblinded repository/label access. Neither is
attached to Gemini requests or transferred to regenerated packet hashes.

Revision 8 audit evidence, barred from all blind contexts:
`materials/round5-reviewed-packets.jsonl.gz`,
`materials/rejected-v7-paraphrases.jsonl.gz`,
`checks/gemini-rendered-submission.json`,
`checks/gemini-rendered-resume-audit.json`,
`runs/revision-v8/gemini-review-costs.jsonl`.
The dated orchestrator amendment accepts the round-5 Claude report at report
level plus a fresh isolated Gemini review of each current packet. It does not
retroactively manufacture missing historical annotations or call round 6 blind.

`checks/gemini-rendered-adjudication.json` contains the six authorized mechanical
adjudications and complete sense-assignment witnesses. It is private review/scoring
evidence and must never enter judge packets or reviewer attachments.

## Retained-dev diagnosis (2026-09-22)

`DEV-DIAGNOSIS.md` and `checks/dev-diagnosis.json` join raw decisions to hidden
reference labels and exact localization sets. They are scoring audit artifacts,
barred from model contexts and blinded reviewer attachments, like the existing
construction/scoring history listed above.
