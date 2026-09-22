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
outcome. Do not open labels.jsonl.gz or graphs.jsonl.gz while annotating.

For each packet, recover and record:

- The intended meaning of every relevant use, anchored in specific source records.
- The original root, required assumptions, and which assumptions are declared.
- Whether the justification shifts a definition, needs an undeclared bridge, or
  is benign; acceptable one/two-node localization sets and supporting passages.
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
cannot approve these replacement packets. Revision 4 keeps records fixed across
siblings and renders inferences as topologically ordered prose paragraphs.
Step labels support localization; parent IDs are absent from prose. The four
unqualified references per packet have unique immediately-preceding referents;
three are harmless. Inspect the critical inference without silently qualifying
or repairing it. Only VE-arm requests include the additional node block. Alternative checks in a
sentence are conditional comparisons, not additional declared facts. In
particular, naming a unit as a sample of a lot supplies no rule transporting its
properties to the lot, or from the lot back to the sample.

Open questions: Is each unqualified reuse actually read in the sense required by
the downstream record? Is the cross-unit bridge plausible but genuinely
unstated? Are both decoy senses used consistently? Are the conditional
alternatives natural, or too cumbersome? Can the full prose meet the original
context caps? The exact packet must pass the token/structural and node-relational leakage gates;
that does not establish semantic readiness. These drafts are NOT the registered
Qwen paraphrases and cannot pass the independent-paraphrase gate.

Explanation scoring is a separate post-inference task: two raters receive the
packet and answer without arm/model fields, assess source-groundedness, record
protocol recognition, and resolve disagreements before analysis. Missing ratings
remain failures; no paid automated grader is assumed.
