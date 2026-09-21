# VE v2 plan: a trusted oversight component that is not a language model

Approved by the project lead on 2026-09-21 ("Good ideas. go ahead."). Supersedes the experiment part of `PLAN.md`;
`FUTURE.md` stays the backlog. Designs this plan draws on: `design/ve-protocol-design.md`, `design/evidence-layer-design.md`,
`design/positioning-vs-debate-theory.md`, `design/open-problems-survey.md`, and the two reviews summarised in
`~/code/manage-agents/reviews/SYNTHESIS.md`.

## Thesis

LLM overseers have measured failures: they miss attacks deep in long contexts, change correct verdicts under
persuasion, lose accuracy as the reviewed work grows, and can be prompt-injected. A verified checker has none of these.
VE's model-only value is therefore verifiability plus protocol, shown where frontier models fail. The English surface is
for human sign-off and is not claimed to help models. Combining proofs with debate is not our idea (prover-estimator
debate, section 8), and checked deductions do not relax its stability assumption; our contribution is an implemented,
verified substrate and the measurements that paper asks for.

## Work packages, in order

| # | Package | Deliverable | Who | Budget |
|---|---|---|---|---|
| 1 | **Obfuscated-arguments benchmark (F0)** | Generator for certified claim graphs of 50 to 5,000 steps with one planted flaw in a deduction, a leaf premise or the formalisation, plus no-flaw controls; a world-model oracle with query accounting; transcript format with a hash chain; debate runner with typed moves and budgets; judge harness with an inspection budget; arms: prose debate, debate with cross-examination, chunked review, VE + checker, VE + FORGED checker line; a real-artefact arm. Preregistration, dev pilot to find the size at which frontier judges start failing, then the scored run | Codex builds; Claude (cheaper model) reviews the science; orchestrator runs the API jobs | pilot about $20, scored about $60-85 (Vertex Gemini first, OpenRouter for other families) |
| 2 | **Context-invariance study** | The same oversight decision at 100K to 800K tokens: LLM monitor vs checker; baselines chunking, pinned constraints, verbatim JSON. Requirement retention is re-scoped to measuring semantic drift when the agent re-authors | same | about $100-200; long contexts are the expensive part: start with a $20 probe |
| 3 | **Evidence layer** | Evidence-record schema, leaf assessments with intervals, Frechet lower-bound propagation through checked graphs, coherence checker (oracle-triggered constraints + LP), provisional assessments with an update ledger, challenge moves; experiments E-A (planted worlds with exact posteriors) and E-B (post-cutoff resolved questions, scored per stage) | same | about $130-180 |
| 4 | Round-2 controls for the existing paper | E4 ablation (verdict only, countermodel without verdict, forged checker), fluent-effect control with independently paraphrased requirements, multi-family judges | same | about $30-50 |
| 5 | Language | finish `order@0` (Python stage), the regular-English surface (review and merge, then a Lean round-trip proof), obligation and priority profile | Codex, one core-touching profile at a time | subscription quota only |
| 6 | Training study (Phase T) | unchanged design; gate first | later | Colab units |

Every experiment: preregistered; one primary contrast; a control that could show harm; every arm gets the same
information and is charged its full cost including VE authoring; results that are true by construction are labelled so;
negative results are published.

## Operating rules (quota)

Weekly limits on 2026-09-21: Claude Fable 80% used, Claude all models 46% used, Codex 60% used; both reset on
25-26 September. Therefore: the orchestrator (Fable) acts only on completions and user messages and keeps replies short;
Claude subagents run on cheaper models and only for reviews and browser work; Codex builds, one or two tasks at a
time, effort `high` (xhigh only for Lean proofs and science reviews); judge and debater calls for experiments go to paid
APIs (Vertex trial credit $273, OpenRouter $20), never to the subscriptions. If a limit is reached, work continues on
whatever resource remains and the state is in `~/code/manage-agents/ve-run-log.md`.
