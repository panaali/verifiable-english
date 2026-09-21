# VE: 12-hour plan to a tested implementation and a paper

**Owner:** orchestrator (Claude session `verifiable-english-ab`). **Started:** 2026-09-21 ~00:30 local. **Deadline:** ~12:30 local.
This file is the single source of truth for scope and status. Only the orchestrator edits it on `ve-integration`.
Workers propose changes to it in their reports.

## Goal

1. A fairly complete, tested implementation of VE v0 (inspired by ACE and Canonical English).
2. Experiments, with baselines, that support or refute each claimed benefit of VE for scalable oversight.
3. A paper that reports what was found, including negative results.

Out of scope: human-participant studies (none available), pushing to GitHub.

**Training is now in scope (user, 03:00).** The user has Google Colab compute (about 200 units; roughly T4 1.2, L4 1.7,
A100-40GB 5.4, A100-80GB 7.5, G4 96GB 8.7, H100 18 units/hour; check the live rate under Runtime > View resources).
Phase T below. Minimise browser use: one setup cell that turns the notebook into a job runner, then files in and out.

## Constraint that shapes the science

There are no human participants. Every judge is a model. So:

- The claims tested are about **weak model supervisors overseeing stronger model agents** (the sandwiching setup
  used by Khan et al. and Kenton et al.). Human readability is not tested and must not be claimed.
- Weak judges: `claude-haiku-4-5-20251001`, `gpt-5.6-luna` (add `gpt-5.5`, `claude-sonnet-5` as mid-tier if budget allows).
  Strong agents and attackers: `claude-fable-5-1`, `gpt-6-astra`. Use both families in every role to control for
  self-preference.
- Model calls go through the CLIs, since no API keys exist: `claude -p --model <id>` and
  `codex exec -m <id> -s read-only --skip-git-repo-check`. Both take about 4–5 s for a trivial call. Cache every call
  on disk keyed by (model, prompt hash, seed). Limit concurrency to about 6. Log tokens.

## Hypotheses and experiments (v1, to be attacked in the design round)

Each experiment names the VE-specific claim, the baseline that could beat it, and the result that would refute it.

| ID | Claim under test | Design sketch | Key baselines |
|---|---|---|---|
| E0 | Coverage: useful oversight claims fit v0 | Try to formalize items from public datasets (candidates: FOLIO, ProofWriter, Cedar/OPA policy examples, a requirements set). Report direct fit, fit only via opaque predicates, and no fit | none; this is a measurement |
| E1 | Sign-off: a weak judge catches adversarially weakened specifications better from a deterministic VE rendering | Intended requirement in prose + candidate formalization, half faithful, half weakened by a strong attacker so that it still looks right. Judge approves or rejects | raw FOL; FOL + **untrusted** explanation written by the attacker; FOL + honest explanation; VE strict; VE natural view. Cross with and without distinguishing scenarios |
| E2 | Scaling: reviewing specification + remaining premises stays flat as the work grows, while direct review degrades | Hold the specification fixed, vary derivation size (for example 4, 16, 64, 256 steps) with one planted invalid step or one false leaf. Judge sees either the work or the checker result + remaining premises | direct review of the full work; prose debate with one critique |
| E3 | Meaning preservation across branches | Arguments where a term shifts meaning between branches. Include the merged-vocabulary variant, where the checker is blind by construction, and the predicate-use panel as an intervention | prose debate with cross-examination and a shared glossary; structured formal claims with the same checker |
| E4 | Countermodels are critiques a judge can verify | Invalid inference + critic objection given as a checked finite countermodel or as prose. Include dishonest critics who object to valid inferences | prose critique; no critique |
| E5 | Harm check: a "proof checked" label raises false approval of grounding errors | Valid deductions with good or bad grounding, with and without the label, and with a fuller "outstanding obligations" display | no label |
| E6 | Debate rounds beyond one critique add value | Same tasks as E3/E4 with 0, 1, and 3 rounds, charging tokens | single critique |
| E7 (stretch) | Statement sign-off on real AI-produced theorems | Theorem statements from public AI-generated Lean developments (for example `openai/ten-proofs`), each paired with its informal claim; half are weakened so that a proof would still plausibly exist. Judge decides whether the formal statement matches the informal claim. These statements are outside v0, so this measures the sign-off problem and the untrusted-explainer risk, not the v0 renderer | raw Lean; Lean + untrusted explanation; Lean + honest explanation |

The most VE-specific angle is in E1: in an oversight setting the explainer is the agent being overseen, so an LLM
explanation can lie, while a deterministic rendering cannot. If VE does not beat "FOL + untrusted explanation", the
English surface has little reason to exist. If it does not beat raw FOL for model judges, say so.

Rules for every experiment:

- Write the metric, the primary contrast, and the refutation condition to `experiments/<id>/PREREG.md` and commit it
  **before** running the scored set. Development items and scored items are disjoint.
- Primary metrics: false approval = approved bad / assigned bad; honest acceptance = approved good / assigned good.
  Keep failures and timeouts in the denominators. Report paired differences with bootstrap confidence intervals.
- Ground truth comes from the checker or from construction, never from a model's opinion.
- Attack items must be validated: a weakened specification must differ semantically from the faithful one
  (a distinguishing finite model exists) and must not be trivially detectable by string comparison.
- Sample sizes are chosen from a pilot's variance, within the call budget. Report inconclusive results as inconclusive.

## Plan v2 decisions (frozen 01:35 after both critiques; supersedes the v1 table where they differ)

Both critiques (`design/critique-claude.md`, `design/critique-codex.md`) agree on the main points. Decisions:

1. **E1 is the primary experiment.** Same underlying item in every cell, attacks generated once and blind to the cell.
   - Views: FOL with symbols; FOL with ASCII keywords (nuisance control: "words, not symbols"); VE strict; VE natural.
     All four are deterministic renderings of the same AST.
   - Crossed factor: no explanation, or an explanation written by the attacker. An honest-explanation cell is
     exploratory only.
   - Primary contrast: false approval, VE strict vs FOL-symbols, in the attacker-explanation cells. Secondary:
     VE vs keyword-FOL (is it English, or just not symbols?), and VE vs FOL with no explanation.
   - **Gate:** E1 is scored only if the dev split shows a capability gap (weak judges' unaided accuracy below the
     strong models') and raw-FOL false approval between 30% and 60%. Otherwise recalibrate attacks first.
   - Attacks: a mechanical family (quantifier swap, dropped conjunct, argument reversal, weakened exception,
     vacuous domain) plus model-written attacks from both families. Each attack is validated by a distinguishing
     finite model and must not be detectable by string comparison with the requirement.
   - **E1b comprehension control:** with no requirement shown, the judge predicts whether the text holds in two small
     finite models; the evaluator scores it. This separates understanding a view from approval bias.
   - Main scored set is synthetic (contamination-free) with fresh vocabulary; FOLIO-derived items are a secondary set.
     Split by semantic template and vocabulary family. Bootstrap over template clusters. Report every judge separately.
2. **E5 is the harm check** and absorbs E3's merged-vocabulary attack. Grounding errors are defined by explicit records
   and scope mismatches, never by a model's verdict. Cells: no label, "proof checked" label, label + outstanding
   obligations display, the latter also with the predicate-use panel.
3. **E0 is a coverage audit with a spread**, not one number: Cedar, Gatekeeper, FOLIO, ProofWriter, and the boundary
   sets (Alloy, FRET, Clover). Freeze the sampling frame and inclusion rules before conversion. Survey labels need a
   second rater from the other model family.
4. **E2 and E4 shrink and must be able to fail.** E2: sizes 4, 32, 256; half the items carry an error the checker
   cannot see (false leaf, wrong specification). Add a structured-FOL arm with the identical checker output, so that
   any VE effect is separated from the checker's effect. E4: include dishonest critics with asserted but unchecked
   countermodels. These are reported as mechanism demonstrations unless the matched baseline differs.
5. **E6 is cut. E3 survives only inside E5. E7 stays a stretch goal.**
6. Every PREREG names one primary contrast, one refutation condition, an honest-acceptance constraint, and a smallest
   useful effect. An interval that spans the smallest useful effect is reported as inconclusive. Unparseable verdicts
   count as the worst case for their cell.
7. Known asymmetry to report: Codex-family judges receive about 13.6k tokens of CLI context per call, Claude-family
   about 500. Judges are therefore never pooled across families in a primary result.

## Implementation scope

- Language core: many-sorted function-free FOL with equality, per `docs/spec/v0-language.md`. Strict parser,
  type and scope checker, canonical printer, round-trip property tests.
- Finite-model evaluation with explanatory bindings. Finite countermodel search.
- Entailment: a sound procedure with checkable evidence. Options to evaluate: Lean certificates (Lean is installed),
  an SMT solver via `pip install z3-solver` with proof/unsat-core evidence, or a small resolution prover that emits a
  checkable trace. The implementer chooses and justifies the trust boundary.
- Argument layer per `docs/spec/debate-protocol.md`: claim graph, certified edges, `follows` / `refuted` / `gap` /
  unresolved, assumption-preserving composition.
- Renderers: strict canonical VE, a more natural read-only view (ACE-style), and FOL → VE import so existing formal
  datasets can be rendered.
- **Lean track (raised in priority at 01:10).** Both model families have produced large Lean-verified results
  autonomously (see `~/code/manage-agents/model-capability-brief.md`, addendum). So a Lean 4 reference semantics with
  proofs of evaluator soundness, printer/parser round trip on the AST, and assumption-preserving composition is in
  scope, led by Worker X. The Python package must agree with it on the conformance cases.
- CLI and a Python API the experiment harness can call. Python is the default for speed; Lean for whatever part
  of the metatheory is cheap to prove. Implementation is expected to take hours, not the whole budget.

## Phases and time boxes

| Phase | Window (hours from start) | Output |
|---|---|---|
| P0 Setup | 0–0.5 | worktrees, this plan, protocol |
| P1 Design round | 0.5–1.5 | each worker's critique of this plan + cross-critique; plan v2 frozen |
| P2 Build | 0.5–4 (overlaps P1) | language core, renderers, checker, harness, datasets |
| P3 Experiments | 3–9 | pilots, preregistrations, scored runs, analysis |
| P4 Paper | 8–11.5 | `paper/` draft, figures, cross-review, revision |
| P5 Close | 11.5–12 | final merge, reproducibility check, summary for the user |

## Phase T: training study on Colab (dispatch when the checker API and the E1 item generator are merged)

Question: does a VE-checked reward make semantic deception less profitable to learn than a judge-only reward?

- Task: given a requirement in prose, the policy writes a formalization (and, in the judge-only arm, an explanation).
  A hidden "tempting" objective makes weakened formalizations easier to satisfy, as in specification gaming.
- Arms, revised after the literature review (`design/phase-t-literature.md`): the first version's B-vs-A contrast was
  close to true by construction, because B contained the ground-truth-linked checker. Prior work already shows that
  weak-judge rewards teach deception (Wen et al. 2024; Mahmoud et al. 2026) and that better-structured rewards reduce
  hacking (Kenton et al. 2026). The narrow new question is the training analogue of E1:
  **A** = frozen weak judge reads the policy's own prose/explanation; **B'** = the same judge reads only the
  deterministic VE rendering, no checker in the reward. **Primary contrast: B' vs A.** Ceilings: **B** = rendering +
  checker, **C** = checker + hidden specification-strength check. Control: **R** = random reward.
- Gate before any RL spend: show deception is inducible (best-of-n probe, n = 1..32, per reward on the base policy;
  audit base-policy false positives). At least 5 seeds per arm on the primary contrast; cut arms before seeds.
- The outcome is never the reward: held-out distinguishing models, renamed vocabulary, reference-AST comparison, a
  cross-family judge panel, and 100 hand-audited rollouts per arm. Preregister an equivalence margin; a null is likely.
- Everything must run inside Colab: small open-weight policy (about 1.5B-3B, LoRA, GRPO or rejection-sampling
  fine-tuning if RL is too slow), frozen small open-weight judge, and the pure-Python `ve` package as the checker.
- Outcome: rate of approved-but-wrong formalizations on held-out items, measured by the checker, per arm, with seeds.
  Refutation: arm B is no better than arm A at equal honest acceptance.
- Budget: decide the GPU from a 10-minute throughput probe; G4 or A100-40GB are the likely choices; stop at 150 units.

## Status log

- 01:48 (real clock) **Capability gate fails with hosted judges.** Two independent dev pilots: on raw FOL, haiku-4.5 false
  approval 1% (accuracy 0.99), luna 5%; on E5 items haiku 0/12 in both badge cells. Today's small hosted models read
  first-order logic almost perfectly, so there is no sandwich gap to measure with them. This is a finding in itself and
  goes in the paper. Response: a ladder of small open-weight judges (0.5B-8B) is being built (`claude/open-judges`);
  the scored E1/E5 runs use the rungs whose raw-FOL false approval lands in 30-60% with honest acceptance >= 70%, plus
  the hosted judges as the top of the ladder. Item difficulty may be raised only by natural, preregistered knobs.
  Merged so far: core, argument layer, grammar, Lean. Under revision after review: views (+fluent), E5/E2/E4 materials,
  harness (fixed by Worker C). Running: Rust core, Lean round-trip, equivalence oracle, E0 second rater.

- 01:35 Both design critiques merged. Plan v2 frozen (section above). Worker C harness done, awaiting cross-review.
- 01:10 Read the user's links on recent AI mathematics. Added the Lean track and stretch experiment E7.
- 00:30 Plan v1 written. Worktrees created: `~/code/ve-claude` (`claude/main`), `~/code/ve-codex` (`codex/main`),
  `~/code/ve-integration` (`ve-integration`).
