# VE: 12-hour plan to a tested implementation and a paper

**Owner:** orchestrator (Claude session `verifiable-english-ab`). **Started:** 2026-09-21 ~00:30 local. **Deadline:** ~12:30 local.
This file is the single source of truth for scope and status. Only the orchestrator edits it on `ve-integration`.
Workers propose changes to it in their reports.

## Goal

1. A fairly complete, tested implementation of VE v0 (inspired by ACE and Canonical English).
2. Experiments, with baselines, that support or refute each claimed benefit of VE for scalable oversight.
3. A paper that reports what was found, including negative results.

Out of scope: RL or any model training (future work), human-participant studies (none available), pushing to GitHub.

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

## Status log

- 01:10 Read the user's links on recent AI mathematics. Added the Lean track and stretch experiment E7.
- 00:30 Plan v1 written. Worktrees created: `~/code/ve-claude` (`claude/main`), `~/code/ve-codex` (`codex/main`),
  `~/code/ve-integration` (`ve-integration`).
