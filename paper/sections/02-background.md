# Background and related work

## Oversight, debate, and weaker judges

Debate attempts to make an agent's answer assessable through adversarial
criticism. Its usefulness depends on the task, information access, and judge.
[Bowman et al.](https://arxiv.org/abs/2211.03540) describe a sandwiching design
in which expert performance establishes a target above an unaided supervisor.
[Khan et al.](https://arxiv.org/abs/2402.06782v4) study debate with information
asymmetry and report improvements for weaker model and human judges.
[Kenton et al.](https://arxiv.org/abs/2407.04622v2) broaden the task distribution:
debate beats assigned consultancy, while comparisons with direct answering are
mixed without information asymmetry. These studies motivate measuring a
capability gap instead of assuming one from model names.
<!-- src: docs/research-review.md; design/phase-t-literature.md. -->

[Buhl et al.](https://arxiv.org/html/2505.03989v3#S4.SS4.SSS2) identify
inconsistent definitions across branches as a possible failure of judging only
leaves, and describe cross-examination as a defense. That observation is not a
measurement of attack prevalence. [Prover-estimator debate](https://arxiv.org/html/2506.13609v2#S8)
suggests combining formal proofs with debate over uncertain claims. VE does not
inherit that protocol's guarantees. It offers exact claim references and checked
local implications; evidence disputes, collusion, and hard-to-locate false
premises remain outside its logical checks.
<!-- src: docs/architecture-and-design.md; docs/research-review.md, source-review record. -->

## Controlled natural languages

Controlled English with formal interpretation is established prior work.
[Attempto Controlled English (ACE)](https://doi.org/10.1007/978-3-540-85658-0_3)
uses explicit interpretation conventions and discourse representations that can
be translated to logic. [PENG](https://researchers.mq.edu.au/en/publications/representing-knowledge-in-controlled-natural-language-a-case-stud/)
combines a restricted grammar and lexicon with guided authoring and reasoning
services. [Logical English](https://www.doc.ic.ac.uk/~rak/papers/Logical_English_Demonstration_for_ICLP.pdf)
is an English syntax for logic programming. Its execution and negation semantics
are not automatically VE's classical consequence relation. VE does not claim to
introduce English-to-logic translation.
<!-- src: design/related-systems.md; docs/research-review.md. ACE chapter DOI
could not be freshly fetched; mark remains in references. -->

[Kuhn's controlled-English study](https://attempto.ifi.uzh.ch/site/pubs/papers/kuhn2013swj.pdf)
found better comprehension and lower learning time for ACE than a simplified
Manchester-style notation; test completion time was similar. That finding does
not establish better adversarial specification review. [Fuchs](https://attempto.ifi.uzh.ch/site/pubs/papers/cnl2018main_fuchs.pdf)
shows how ACE interpretation conventions can conflict with ordinary English
intuitions. [Little Tricky Logic](https://arxiv.org/abs/2211.01677) documents
misconceptions about temporal formulas and their English descriptions among
formal-methods researchers. Familiar wording alone is insufficient evidence of
correct understanding. VE therefore plans model-satisfaction questions alongside
approval judgments.
<!-- src: docs/research-review.md; design/related-systems.md. -->

[Canonical English](https://canonical-english.org/) emphasizes recorded parses,
lexical senses, and stable referents for agent communication. The inspected
website is a design description, not an audited entailment system. The repository
review could not inspect its linked implementation; an unsuccessful fetch does
not establish that code is absent. Sense identifiers are a useful interface idea,
but an attached sense identifier does not prove that evidence uses that sense.
<!-- src: design/related-systems.md; docs/architecture-and-design.md. -->

## Trustworthy specifications and evaluator deception

[Gordon and Matskevich](https://arxiv.org/html/2310.03885v1#S5) provide a close
predecessor: formal natural-language specifications in Lean with interpretation
certificates and an explicit trust analysis of the lexicon. VE's proposed
contribution is a bounded review workflow and adversarial evaluation, not a new
recognition that lexical definitions need inspection. [FormalJudge](https://arxiv.org/html/2602.11136)
combines model-generated specifications and formal checking; intent decomposition
and fact extraction remain distinct error sources. VE likewise separates
entailment from grounding.
<!-- src: docs/research-review.md; docs/architecture-and-design.md. -->

[Gao et al.](https://arxiv.org/abs/2210.10760) study optimization against an
imperfect reward proxy. [Wen et al.](https://arxiv.org/abs/2409.12822) find that
training can raise approval by time-limited humans without improving task
correctness. [Re:Form](https://arxiv.org/abs/2507.16331) analyzes weak and trivial
Dafny specifications that can pass verification. [Kenton et al.'s training
study](https://arxiv.org/abs/2608.17776) compares debate training with a weaker
judge against ordinary AI-feedback training. These results motivate an outcome
evaluator outside VE's proposed training reward. They do not establish that a
deterministic English view improves a trained policy.
<!-- src: design/phase-t-literature.md. -->

Model evaluation also has its own validity problems. [Zheng et al.](https://arxiv.org/abs/2306.05685)
report position, verbosity, and self-enhancement biases. [Panickssery et al.](https://arxiv.org/abs/2404.13076)
connect self-recognition with self-preference. Our model judges are experimental
subjects, not authorities on semantic truth. Checker evidence or explicit record
construction supplies labels. Results must remain specific to each judge,
serving stack, and input presentation.
<!-- src: design/phase-t-literature.md; design/critique-codex.md. -->
