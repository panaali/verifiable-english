# Related work and capability boundaries

Controlled English with formal interpretation is established prior work.
[ACE](https://doi.org/10.1007/978-3-540-85658-0_3), with its RACE reasoner,
already connects controlled language to first-order reasoning.
[PENG](https://researchers.mq.edu.au/en/publications/representing-knowledge-in-controlled-natural-language-a-case-stud/)
provides restricted-language knowledge representation and guided authoring.
[Logical English](https://www.doc.ic.ac.uk/~rak/papers/Logical_English_Demonstration_for_ICLP.pdf)
targets logic programming; its execution and negation conventions differ from
classical consequence. [FRET](https://github.com/NASA-SW-VnV/fret) links restricted
requirements to formal and visual representations, including simulation.
These are substantive interface precedents, not baselines we have outperformed.

The closest trust-oriented predecessor is
[Gordon and Matskevich](https://arxiv.org/html/2310.03885v1#S5): natural-language
specifications in Lean, interpretation certificates, and explicit scrutiny of
lexical definitions. [FormalJudge](https://arxiv.org/html/2602.11136) combines
model-generated specifications with Dafny/Z3 checking, while retaining errors
from intent decomposition and fact extraction. VE adds a particular artifact
and paired rendering evaluation; it does not newly discover these boundaries.

| System | Semantics and reasoning | Verified components / guarantee scope | Adversarial evidence and empirical comparison here |
|---|---|---|---|
| ACE + RACE | Discourse representation mapped to FOL; consistency and entailment | Translation conventions and reasoner; no kernel-checked end-to-end guarantee established by the repository review | No matched sign-off comparison in this paper |
| PENG | Restricted grammar and lexicon; logical knowledge representation and reasoning services | Guided authoring is not a proof of intended meaning; verification scope not established here | No matched adversarial or sign-off comparison here |
| Logical English | Executable logic-programming rules | Execution under its operational semantics; no intent guarantee | No empirical comparison here; not assumed to share VE's negation semantics |
| FRET | Restricted requirements with temporal/formal representations; simulation | Formalized requirements and analysis interfaces; no source-intent guarantee established here | No matched sign-off comparison here |
| Gordon--Matskevich | English specifications interpreted inside Lean | Interpretation certificates checked in Lean; lexical definitions still require review | Lexical trust/attack analysis; no empirical comparison here |
| FormalJudge | Model specifications checked using Dafny/Z3 | Deductive checks of the generated specification; intent and extracted facts remain obligations | Agentic-oversight evaluation in the cited work; no matched comparison here |
| VE | Function-free relational FOL plus opt-in closure; finite evaluation and certificate replay | Lean reference soundness, strict surface properties, base graph soundness; production refinement absent | E1 non-equivalence attacks and E4 critic pilot only; other systems not evaluated |

The table reports capabilities supported by the repository's existing literature
notes; "not established here" is not a claim that another system lacks a
feature. No fresh literature search was made for this revision. Verified
first-order provers and checkers exist in the literature
[citation needed: verified FOL provers]. The local documentation contains no
usable citation for that comparison; we therefore make no formal-novelty claim
for standard tableau soundness or finite-path reasoning.

Studies of [debate](https://arxiv.org/abs/2402.06782v4) and
[weak judges](https://arxiv.org/abs/2407.04622v2) motivate measuring a capability
gap under controlled information access. They do not supply guarantees for VE.
Human [controlled-English comprehension](https://attempto.ifi.uzh.ch/site/pubs/papers/kuhn2013swj.pdf)
is also distinct from adversarial sign-off. We have no human study and no
matched comparisons with debate, critique, voting, trusted back-translation,
or Lean/Dafny statements accompanied by an LLM explanation. The e2 development
observation makes trusted back-translation a particularly important missing
baseline.
