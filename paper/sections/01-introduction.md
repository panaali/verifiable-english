# Introduction

A checked proof can establish a consequence of a specification while leaving
open whether that specification states what its author intended. Controlled
English is an appealing interface for this remaining review task: it may make
scope, quantifier dependencies, and omitted conditions easier to see. This
paper asks a narrower empirical question: does a deterministic English display
help a model judge distinguish faithful from unfaithful translations when the
requirement, vocabulary, and logical candidate are otherwise held fixed?

Our answer is mostly negative for the more capable scored judge. In E1,
Qwen2.5-32B-Instruct-AWQ gained no demonstrated benefit from strict VE over
symbols. A weaker Qwen2.5-14B judge did benefit in some conditions, most clearly
from fluent rendering. This capability-by-surface pattern matters more than a
single pooled result: a display that assists a weak reader on these items need
not assist a capable reviewer. The hosted development judges were near ceiling,
so the current task does not probe where those models need oversight support.

The experimental scope is exact-translation discrimination on short,
author-written, near-formal requirements. The reference AST and the intended
reading are stipulated together. The experiment therefore assumes away the
harder intended-versus-stated problem, and does not vary specification size.
Its false-approval endpoint counts acceptance of any non-equivalent candidate,
including stronger and incomparable formulas. Our post hoc weakening-only
analysis isolates cases that admit behavior forbidden by the reference.

A second experiment, E4, supplies a checker finding alongside a critic's finite
interpretation. This is a useful integration check of whether model decisions
respond to checker feedback. It is also a deliberately limited result: the
finding says whether the inference follows, so the judge is given the answer.
A deterministic rule could read that field directly. We call the outcome
**uptake of checker feedback**, not improved logical comprehension or a benefit
of English. Post hoc lenient parsing separates semantic verdicts from response
protocol failures, which otherwise inflate the 14B contrast.

The accompanying Verifiable English (VE) artifact combines a small relational
language, deterministic displays, finite countermodels, replayable certificates,
and claim graphs that retain assumptions. Its Lean development is assurance
engineering for named reference components. It does not certify the source
interpretation, the production Python/Rust system, or the displayed prose.
The paper's contribution is a negative rendering result with reproducible
methods and an inspectable artifact, rather than a new general oversight
principle. E0 and four qualitative use cases further show how much source
meaning remains outside the implemented fragment.

We distinguish three evidential categories throughout: unchanged preregistered
per-judge decisions, development observations that informed the design, and
POST HOC analyses requested after independent critical reviews. All reanalysis
scripts are committed under `paper/analysis/`, with generated tables, input
hashes, and plots under `paper/generated/`. They use existing trial files only;
this revision made no model calls and used no network. Plans for additional
experiments remain plans.
