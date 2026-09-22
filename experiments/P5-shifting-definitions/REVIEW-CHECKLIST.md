# Blinded review gate

Two independent reviewers examine **all 84** packets before scoring. At least
one is a human or project lead. Work separately before comparing annotations.
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

Open questions: Are the compact registry rules natural and clear enough? Does
“cleared” actually shift between the cited uses? Is the omitted bridge genuinely
absent? Are any redundant paths licensing a purported flawed root? Do shorthand
rule groups or the vocabulary workload create a shortcut? Is the draft prose a
faithful argument rather than a label hint? Offline drafts are NOT the registered
Qwen paraphrases and cannot pass the independent-paraphrase gate.

Explanation scoring is a separate post-inference task: two raters receive the
packet and answer without arm/model fields, assess source-groundedness, record
protocol recognition, and resolve disagreements before analysis. Missing ratings
remain failures; no paid automated grader is assumed.
