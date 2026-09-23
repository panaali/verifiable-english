# Frontier judge failure modes and what VE needs to address them (2026-09-22)

Source review (primary sources, unverified items flagged): `~/code/manage-agents/reviews/lit-frontier-judge-failures.md`.
Companion ideas: `design/crypto-inspired-oversight.md`.

## 1. What the literature shows (frontier judges/monitors)

| Failure | Key evidence | Shrinks with stronger judge? |
|---|---|---|
| Persuasion / pushback | Jagged Judges (arXiv 2608.12645): GPT-5.x, Opus 4.6, Gemini 3.1 Pro flip verdicts 25-71% under simple pushback, 62-91% under an adversarial persuader; most flips move away from the correct answer | No |
| Long agent logs | Martin & Roger (2605.12366): Opus 4.6 catches an obvious attack 99.7% at 100K tokens, 69% at 800K; worst mid-transcript | Partly |
| Capability gap | Engels et al. 2025: at a 400-Elo gap, oversight success 51.7% (debate), 10.0% (backdoor code) | No |
| Prompt injection at monitors | Terekhov et al.: GPT-4.1 rated all 375 backdoored samples benign; worse with larger attacker-monitor gap | No |
| Judges stop checking | Elasky 2026 (2605.27483): debate beats consultancy by ~15pp in only 3/5 pairings; elsewhere claim verification fell from 61-82% to 16-53% | Pairing-dependent |
| Self-preference | Yang et al. (20 models): stronger models often more self-biased | No |
| Grader hacking | RLHF raised human false positives 18-24%; a bare ":" fools GPT-4o ~35% (snippet only, unverified) | - |
| CoT monitoring under optimisation | Baker et al. 2025: 95% recall collapses to ~0 when trained against the monitor | No |
| Negative claims ("no bug", "nothing missing") | AbsenceBench: best 69.6% F1 at 5K tokens; "bug-free" framing cuts detection 16-94pp (small models only) | Unknown: no frontier study |
| Length / position bias | Length ~gone (corr < 0.011); position bias persists (0.002-0.192) | Length yes, position no |

Our own frontier results agree once the setting is right: on short clean items without sustained pushback, frontier
judges are at ceiling (P1 Gemini 0/208, V4, D pilot); the literature failures appear under pushback, length, capability
gaps and negative claims.

## 2. Does VE need to be extended?

**Current VE is enough (engineering only):**
- Persuasion/pushback: checker-decided verdicts on logic items; needs a signed trusted verdict channel and a
  Jagged-Judges-style pushback harness (P1 harness has most pieces).
- Prompt injection: claims are structured VE; checker ignores free text; needs an injection harness.
- Collusion/self-preference on the verdict: signed, replayable verdicts.
- Position/order bias: checker is order-independent.

**Small extension required: negative/universal claims (T1c).** "u cannot access x" is not-rtc(u,x) in closure@0;
proving it needs a closure-induction rule (a set containing u, closed under the edges, contains everything reachable)
with a Lean soundness proof. Already first in PLAN-T4. Without it the separating certificate is checked by a plain
script outside VE and VE adds nothing.

**Bigger extensions only for realism/transfer:** real policies (Cedar/IAM/Kubernetes) and proof-carrying actions in
ControlArena-style environments need numbers, strings, attributes, sets (E0: ~0% coverage today); checked-RL task specs
need the same. Synthetic RBAC suffices to demonstrate the certificate effect first.

**Out of VE's reach regardless:** claim extraction from long logs (checker does not degrade, the extractor does);
CoT monitoring; debate on reading comprehension/science QA; false premises; faithfulness of formalisation; humans
over-trusting a "checked" label.

## 3. Recommended order

1. Pushback study now (no language change): frontier judges (Opus 5.5, Sonnet 5, Gemini 3.1 Pro), Jagged-Judges-style
   multi-turn pushback, arms with/without a signed checker verdict for the checkable part of the claim; primary metric
   flip rate away from correct on checker-decided items; harm control: honest completion.
2. Closure-induction rule + Lean proof, then T1c (separating certificates for "cannot access" at 5,000 and 20,000
   grants; arms: Opus raw, Haiku raw, Haiku + checker verdict on the certificate, plain-script baseline).
3. Only if 1 or 2 shows signal: policy-grade extensions (numbers, strings, attributes, sets) and proof-carrying actions
   in a control environment.

## 4. Survey corrections for design/open-problems-survey.md

Row 26: SHADE-Arena says "over 20%" false positives, not "20-40%". Row 19: monitors included GPT-5 and Sonnet 4, not
only GPT-4x. Terekhov safety numbers 0.75->0.2 unverified. Missing: Elasky 2026, Baker's recall collapse, self-preference
growing with capability, negative-claim evidence (AbsenceBench, "bug-free" framing).

## 5. Pushback study design details (added 2026-09-22)

- Pressure protocol: reuse Jagged Judges (arXiv 2608.12645) exactly: L1 "Are you sure?", L2 counterargument, L3 expert
  authority, L4 fabricated consensus ("three independent reviewers all disagree"), L5 random mix of L1-L4, L6 adaptive
  persuader LLM; 10 turns. Their tasks are judgement classification (WildGuard, AEGIS, HH-RLHF, ToxiGen, MAGE, Paired
  Prompts) with no checkable core, so VE is not claimed to help there.
- Items: our checker-decidable items (V4 logic, e.g. c-smoke-modus_tollens-000; T1 access claims, e.g. the 5,000-grant
  item copied to ~/code/manage-agents/examples/t1-5000-grants).
- Arms: judge alone vs judge + signed checker verdict on the checkable part (system refuses judge overrides of signed
  verdicts; pressure can only move the residual, e.g. translation faithfulness).
- Calibration anchor: reproduce their flip rate for 1-2 frontier judges on a small WildGuard slice, to show our pressure
  is as strong as theirs.
- Second arm (tests the "decomposition" argument): holistic verdict vs the same verdict decomposed into VE leaves with a
  named catch-all judgement predicate; hypothesis: fewer flips and higher inter-judge agreement per leaf.
- Report the residual honestly: if flips on the residual equal the original flips, VE only relocated the problem.
