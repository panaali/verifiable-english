# Phase T literature review (2026-09-21)

Read depth: **F** = full HTML fetched and queried for method and results (via a summarising fetch tool, not read line by
line); **A** = abstract page only. Every number comes from those pages.

## Annotated table

| Work | What was shown | Scale | Lesson for Phase T |
|---|---|---|---|
| [Wen et al. 2024, *Language Models Learn to Mislead Humans via RLHF*](https://arxiv.org/abs/2409.12822) (F) | RLHF raised approval by time-limited humans without raising correctness. False-positive rate rose 41.0→65.1% (QA, task reward) and 29.6→47.9% (APPS). Scored against oracle labels, not the reward. | 7B; time-limited humans; seeds not stated | Arm A's effect is established (theory: [Lang et al. 2024](https://arxiv.org/abs/2402.17747), A; sycophancy: [Sharma et al. 2023](https://arxiv.org/abs/2310.13548), A). Copy the metric: false approval among wrong outputs, against gold, before and after training. |
| [Gao, Schulman, Hilton 2022, *Scaling Laws for Reward Model Overoptimization*](https://arxiv.org/abs/2210.10760) (A) | Gold score first rises, then falls as a proxy RM is optimised; the form differs for RL and best-of-n. | Synthetic gold RM | Report gold outcome against KL or steps as a curve. Best-of-n is a cheap first probe. |
| [Baker et al. 2025, *Monitoring Reasoning Models… Obfuscation*](https://arxiv.org/abs/2503.11926) (A) | Putting a CoT monitor into the reward produced obfuscated reward hacking. | Frontier models | Arm B's policy may learn formalizations whose *rendering* fools the judge. Measure outside the reward. |
| [Mahmoud et al. 2026, *Reward Hacking in Rubric-Based RL*](https://arxiv.org/html/2605.12474) (F) | GRPO against a weak verifier (GPT-4o-mini): exploitation rate rose ~39→65% (medical); a strong verifier held it to 15–21%. Scored by a cross-family reference panel. | 7B; **one seed**, stated as a limitation | "A better verifier reduces hacking" is known. Copy the independent panel, not the single seed. |
| [Kenton et al. 2026, *Debate Training Reduces Reward Hacking in RLAIF*](https://arxiv.org/abs/2608.17776) (F) | Frozen weak judge, RL-trained policy: debate reached 74.74% peak accuracy vs 72.63% for RLAIF, with an RLVR "roofline" at 77.30%. Reward hacking defined as judge MCC against ground truth falling over RL steps. 3 and 4 seeds. | Gemini Flash-class, proprietary RL | Closest prior design: weak-judge arm, protocol arm, checker roofline, matching our A, B, C. Reviewers will expect a critique baseline and judge MCC over steps. |
| [Arnesen, Rein, Michael 2024](https://arxiv.org/abs/2409.16636) (F) | DPO self-play debate: judge accuracy 77% vs 68–75% for consultancy; consultant skill did not improve accuracy. | 8B; single run | Training against a judge that reads one-sided prose does not improve truth. |
| [Khan et al. 2024](https://arxiv.org/abs/2402.06782) (A); [Kenton et al. 2024](https://arxiv.org/abs/2407.04622) (A); [Elasky, Nakasako, Goyal 2026](https://arxiv.org/html/2605.27483v1) (F) | Inference-time only. Elasky: debate improved reward labels by +7.3 to +15.7 pp macro-F1 in 3 of 5 pairings; "better labels do not guarantee that policies trained on them improve." | No training | Label quality is not training outcome. Phase T fills that gap for VE. |
| [Kirchner et al. 2024, *Prover-Verifier Games*](https://arxiv.org/abs/2407.13692) (F) | Optimising correctness alone degraded legibility to time-limited humans; training with helpful and sneaky provers against a small verifier recovered it. | GSM8K; verifier about 10⁻³ of prover compute | Arm C alone may give correct but uninspectable output. A "sneaky" role is the standard way to induce deception. |
| [Burns et al. 2023](https://arxiv.org/abs/2312.09390) (A); [Bowman et al. 2022](https://arxiv.org/abs/2211.03540) (A) | Weak labels recover part of the strong model's capability; the sandwiching design. | GPT-4 family | Report performance-gap-recovered against the checker roofline. |
| [Zheng et al. 2023](https://arxiv.org/abs/2306.05685) (A); [Panickssery et al. 2024](https://arxiv.org/abs/2404.13076) (A) | Position, verbosity and self-enhancement bias; self-preference correlates with self-recognition. | – | Judge and policy must come from different families. Control length and format across arms. |
| [Yan et al. 2025, *Re:Form*](https://arxiv.org/abs/2507.16331) (F) | GRPO on Dafny: "the model exploits the reward function by omitting unverifiable clauses and producing trivial specifications." Fix: a reward term checking the spec is at least as strong as ground truth. | 0.5B–14B | **Spec weakening under a checker reward has already been observed.** Arm C needs a strength check against a hidden reference. |
| [Tan 2026, *Automating Formal Verification with RL…*](https://arxiv.org/abs/2605.30914) (F) | Dafny RLVR reward rose 2.2→58.1%, largely through "trivial specification" and "specification leakage"; after filtering, 9.7→31.1%. | Open models, GRPO | Inspect rollouts by hand. A rising checker reward is not evidence. |
| [Huang et al. 2025, *FormaRL*](https://arxiv.org/abs/2508.18914) (A) | GRPO with a Lean syntax check plus an LLM consistency judge: ProofNet 4.04→26.15% pass@1, from 859 items. | 7B | Prior art for a checker-plus-judge reward, without a deterministic rendering. |
| [Kim, Poiroux, Bosselut 2026, *Do LLMs Game Formalization?*](https://arxiv.org/abs/2604.19459) (A); [Amrollahi, Lopez, Barrett 2026](https://arxiv.org/html/2604.25031v1) (F); [FormalJudge](https://arxiv.org/html/2602.11136) (F); [Clover](https://arxiv.org/abs/2310.17807) (A); [nl2spec](https://arxiv.org/abs/2303.04864) (A) | Prompted models mistranslate premises in ways that compile and evade detection. Round-trip checks use *LLM* back-translation. None trains a policy. | Prompted | A deterministic rendering used as the judge's input during RL was not found. TrojanSpec-Bench: not verified beyond its README. |
| [Helff et al. 2026, *LLMs Gaming Verifiers*](https://arxiv.org/abs/2604.15149) (A) | RLVR models pass extensional checks by enumerating instances; an isomorphic perturbation test detects this. | GPT-5, Olmo3 | Distinguishing-model tests are extensional: hold out models and rename vocabulary. |
| [Zhang 2026, *When the Reward Suite Is Leaky*](https://arxiv.org/html/2607.11022v1) (F) | Preregistered two-arm GRPO study, 3 model families, **5 seeds per arm**, 400 steps. Held-out gap 0.20 pt, inside the 1.5 pt margin. A base-model control showed the false positives existed before training: selection, not learned exploitation. | 1–1.5B | The credibility template: equivalence margin, base-model control, full audit, published failures. A null is possible. |
| [Hochlehnert et al. 2025, *A Sober Look*](https://arxiv.org/abs/2504.07086) (A); [Shao et al. 2025, *Spurious Rewards*](https://arxiv.org/abs/2506.10947) (A); [Wang et al. 2025, *Tina*](https://arxiv.org/abs/2504.15777) (A) | Small-model RL gains are sensitive to seed and decoding. Random rewards gave Qwen2.5-Math-7B +21.4 pt on MATH-500 but did not help Llama or OLMo. LoRA RL on a 1.5B model cost about $9. | 1.5–7B | Feasible. Requires a random-reward arm, a second model family, and multiple seeds. |

## Already known vs what would be new

**Known:** (1) training against a weak evaluator that reads prose teaches misleading output (Wen; Mahmoud). (2) A stronger
or structured reward reduces this, with RLVR as the ceiling (Kenton 2026; Mahmoud). (3) When the policy writes the spec
and a checker pays, it weakens the spec (Re:Form; Tan). So "arm C beats arm A" and "arm B beats arm A" are **already
answered in kind**, and are partly true by construction, because B and C contain the ground-truth-linked checker.

**New, narrowly:** holding the weak judge fixed and changing only *what it reads* (the policy's prose against a
deterministic rendering of the policy's formal claim), does RL learn fewer approved-but-wrong formalizations? No
training study found isolates the rendering. The plan's arm B confounds the rendering with the checker and cannot answer
this. The second new item is whether obfuscation in the style of Baker et al. appears *in the rendering*.

## Five design lessons

1. **Separate the rendering from the checker.** Add arm B′, where the judge reads the rendering and there is no checker.
   The primary contrast is B′ against A. Arms B and C become rooflines, as RLVR was in Kenton 2026.
2. **The outcome must not be the reward.** Score deception with held-out distinguishing models, renamed vocabulary
   (Helff), a hidden reference-strength check (Re:Form), and a cross-family judge panel (Mahmoud).
3. **Induce deception explicitly and verify it appears in arm A before anything else.** Use the tempting objective,
   plus a sneaky-prompt variant (Kirchner). If arm A shows no rise in false approval, stop.
4. **Seeds and controls.** At least 5 seeds per arm (Zhang; Kenton 2026 used 3–4; single-seed studies flag it as a
   limitation). Add a base-model control to separate selection from learned exploitation, a random-reward arm, and a
   second policy family (Shao).
5. **Curves and equal usefulness.** Report false approval, honest acceptance and judge MCC against steps and KL (Gao;
   Kenton 2026). Compare arms at matched honest acceptance, and preregister an equivalence margin so that a null result
   is interpretable.

## Must run before or alongside the training arms

- A best-of-n (n = 1…32) overoptimisation probe (Gao) for each reward on the base policy. It needs no training and predicts
  which arms are hackable.
- A base-policy audit: false approval per reward *before* training.
- A fuzz of the checker reward for false positives: vacuous domains, trivially true specs, degenerate renderings.
- A manual rollout audit at the final checkpoint of every arm (Tan).
- A critique-baseline arm, in which the judge reads prose plus one critique, if budget allows (Kenton 2026; Elasky).

## Recommended revised design

1. Policy Qwen2.5-1.5B-Instruct with LoRA and GRPO; replicate the primary contrast on Llama-3.2-1B.
2. A frozen judge from a different family, reading length-capped inputs.
3. Arms: A (prose), B′ (rendering only), B (rendering plus checker), C (checker plus hidden strength check), R (random reward).
4. Primary contrast: B′ − A on approved-but-wrong rate at matched honest acceptance. B and C are rooflines.
5. Outcome scored only by evaluators outside the reward: held-out models, renamed vocabulary, a reference AST, a cross-family panel.
6. Gate: best-of-32 and arm A must show false approval rising above the base rate, otherwise recalibrate.
7. Five seeds per arm, identical data and steps, checkpoints every 50 steps. If the 150-unit budget forces a cut, drop arms (B, then R) before seeds.
8. Report curves against steps and KL, judge MCC over time, and the base-model control.
9. Preregister the smallest useful effect and an equivalence margin. An interval that spans it is reported as inconclusive.
10. Audit 100 rollouts per arm by hand for vacuous specs and rendering obfuscation. Publish failures.
