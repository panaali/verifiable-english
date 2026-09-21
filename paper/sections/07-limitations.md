# Limitations and interpretation

The fluent signal has a serious identification problem. Its rendering is
nearly string-identical to the template requirement, and its word/symbol token
proxy is about 30% shorter than symbolic FOL (27.8 versus 39.6); these are not
model-token counts. A model may align corresponding phrases without learning
a better logical representation. Fluent rendering is also the one view with
no proved property; the strict round-trip theorem does not cover it. Thus the
helpful surface and the assured surface are different. Independently paraphrased
requirements are needed before attributing the 14B effect to controlled English
rather than lexical alignment and length.

All scored judges come from one Qwen family and selected serving configurations.
A one-candidate boundary determined 32B's primary role, and its scored baseline
fell outside the development gate. The legend change and explanation recipes
show substantial prompt sensitivity. One greedy response per trial does not
measure seed, prompt-paraphrase, or serving variability. The capability-by-surface
pattern is conditional on this inventory, not a universal threshold at 32B.
Hosted development performance suggests that harder tasks are needed to test
stronger judges; it is not a held-out frontier result.

The 12 E1 templates are fixed author-written structures, not independent draws
from a target distribution. Renaming vocabulary does not add semantic clusters.
Cluster-t intervals, sign-flip tests, and the cluster-robust logistic alternative
all require assumptions that this design cannot validate. The 0.05 useful-effect
threshold and HA margins lack a task-specific cost model. Post hoc analyses
are explicitly labeled and do not replace the frozen decisions. The revised
E4 presentation changes the parser after seeing results, so it is descriptive.
Differential protocol failures, failed calibration gates, label-bearing checker
feedback, and the absence of a forged-checker control preclude claims of a
measured comprehension mechanism.

The project was developed and reviewed by AI agents. The human set objectives
and supplied resources, but **no human has read the Lean theorem statements,
the templates, or the preregistrations**. Repository freezes for E1 v5 and E4
revision 2 have no external timestamps. Cross-family reviews caught concrete
defects, including a harness that had allowed judges to read labels from disk;
fixes preceded the scored runs. Those catches provide no estimate of residual
errors and do not substitute for human statement review. Process records and
compute accounting are in the appendices.

Finally, no theorem proves that the running Python or Rust code refines Lean,
that the display corresponds to the reviewed AST, or that a source translation
captures intent. E4 replay used Python. Neither E1 nor E4 studies humans,
production deployments, long-context compaction, large specifications, or
long-horizon specification drift. Training, E2 scaling, and E5 grounding/badge
experiments were not completed. The artifact is useful for exposing these
boundaries; its existence does not establish a scalable-oversight benefit.
