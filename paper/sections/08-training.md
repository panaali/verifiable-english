# Training study (Phase T): planned work

Phase T asks whether replacing a policy-controlled explanation with a
deterministic rendering changes the incentive to produce approved but wrong
formalizations. It has not yet run in the evidence frozen for this paper. Its
current design is a plan, not a training result or frozen preregistration.
<!-- src: design/phase-t.md, Status and Estimand; PLAN.md, Phase T. -->

A policy receives a prose requirement and a visible finite state. Some states
satisfy a tempting weakening but violate the hidden reference. Every arm emits
strict VE plus an explanation. Rewards combine output validity, approval, and a
task term based on satisfaction in the visible state. The primary manipulation
changes what the same frozen judge reads.

| Arm | Approval information | Interpretation |
|---|---|---|
| A | Policy-written explanation | Policy controls the explanatory channel. |
| B' | Deterministic VE rendering | Presentation intervention without reference-linked checking in approval. |
| F' | Deterministic keyword FOL | Control for exposing the same formal content without VE wording. |
| R | Matched random approval | Optimization control. |
| B | B' plus scenario tests | Privileged reference-linked baseline. |
| C | Hidden scenarios and two-way reference check | Privileged baseline sharing oracle machinery with evaluation. |

<!-- src: design/phase-t.md, Estimand; supersedes the earlier ceiling terminology
in PLAN.md and design/phase-t-literature.md. -->

The primary comparison is the change from a shared supervised baseline in
approved-and-wrong probability for B' versus A. B' versus F' is needed for a
VE-specific claim. The design also reports wrong-output probability, approval
conditional on wrongness, and approved-and-equivalent probability. Conditional
false approval alone can mislead when training changes which outputs are wrong.
All arms are cross-scored under each presentation, with held-out templates,
renamed vocabulary, distinguishing models, and a separate judge panel.
Reference-linked baselines are not independent gold standards or guaranteed
ceilings.

| Planned training safeguard | Value or decision |
|---|---|
| Selection probe | Best-of-n, n from 1 through 32 |
| Primary replication | 5 paired seeds per arm |
| Paired development RL pilot | 2 seeds, 60 steps |
| Main run length in design | 200 optimizer steps |
| Rollout audit | 100 per arm by strong models; proposed human spot-check is not completed |
| Spend ceiling in plan | 150 Colab compute units |

<!-- src: design/phase-t.md, Gates, Optimization, Inference and Budget;
PLAN.md, Phase T. All figures are plans, not measured costs or completed runs. -->

Before training, the policy must demonstrate faithful-output competence and a
nondegenerate reward signal. A best-of-n probe demonstrates selection pressure,
not learnability. The paired pilot must show inducible false approval before a
main comparison is informative. The final design must freeze power assumptions,
KL budget, checkpoint selection, usefulness constraint, and equivalence margin.
UNKNOWN outcomes retain both extreme assignments.

The original small-judge choices cannot simply be carried forward: the later E1
ladder found largely indiscriminate approval on its tested small open rungs.
Those results do not test every proposed training judge, but they require renewed
calibration on the actual training task and stack. Grammar-constrained generation
can enforce form; it cannot ensure faithfulness. The implemented oracle also
certifies both directions for identical ASTs, superseding the early plan's hash
shortcut wording. No throughput, GPU choice, or training benefit is established
by the budget estimates.
<!-- src: design/phase-t.md; paper/sources/local-ladder.md; docs/oracle.md. -->

**[RESULT-T-GATE: competence, base-policy audit, best-of-n probe, paired pilot,
and end-to-end throughput not yet run.]**

**[RESULT-T-TRAINING: main training, cross-scoring, transfer panel, rollout audits,
and seed-level uncertainty not yet run.]**
