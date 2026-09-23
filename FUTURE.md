# Future phases and idea backlog

The orchestrator appends here as results and ideas arrive. When the current plan in `PLAN.md` is finished, or the
user has not returned, the next phase is chosen from this file: pick the item with the highest expected information
per hour, write it into `PLAN.md` as a new phase, and continue. The project does not stop on its own.

Standing limits: no model training (no GPU yet), no pushing or publishing without the user, no human-participant claims.

## Phase S: beat external state of the art in pure model/agent settings (user priority, 11:54; cost-limited, not time-limited)

Human studies are deferred. The goal is a model-only demonstration that VE beats existing methods, on shared items, at matched cost.

| ID | Setting | VE arm | External baselines | Metric |
|---|---|---|---|---|
| S1 | **Requirement retention under long context and compaction.** An agent receives requirements early, then works through 50k / 200k / 800k tokens of distractor work, or through N forced compactions, and must then enforce or restate the requirements | requirements stored as VE claims + identity hashes, re-rendered and re-checked (parser, evaluator, equivalence oracle) after every compaction | prose notes; LLM-written summaries (the default compaction); a key-value memory tool; structured JSON requirements without a checker | semantic drift measured by the equivalence oracle against the original (EQUIVALENT / weaker / stronger / incomparable), and downstream enforcement accuracy on distinguishing scenarios |
| S2 | Sign-off and critique on the E1/E4 items | VE rendering + checker + countermodels | prose debate with cross-examination; single critique; self-consistency voting; a FormalJudge-style pipeline (LLM writes a Dafny/Z3 spec, solver checks) | false approval and honest acceptance at matched token and dollar cost |
| S3 | Multi-agent hand-off | claims passed between agents as VE with certificates | prose hand-off; JSON hand-off | meaning preserved across k hops (oracle), assumptions dropped |

S1 is the most promising: models degrade with context length and compaction loses information, while a canonical, hashed, checkable claim does not. Design rules: preregister; same information in every arm; charge every arm its full token cost, including VE authoring and checking; report where VE loses.

## Phase F: frontier-scale experiments (user priority, 13:53)

Real-world use requires a benefit for frontier-scale models. Both critical reviews agree that the English surface stops
mattering above roughly 32B on short items, so frontier-scale value must be shown where frontier models fail.

| ID | Setting | Design | Honest limit to test |
|---|---|---|---|
| **F0 (lead)** | **Obfuscated arguments** (Barnes and Christiano; Irving's debate line): a long decomposition where every step looks plausible and a flaw exists that neither debater can locate efficiently | Arguments of 50 to 5,000 steps with one locally plausible flaw. Frontier judge with a debate-style budget (inspects a few steps). Arms: prose debate where a frontier critic must locate the flaw; VE claim graph + checker (every deduction replayed; invalid step returned with a counterexample) | Half the flaws are in a deduction (VE should win by construction: report as such), half in a leaf premise or in the formalisation (VE only narrows the search to K stated premises and makes dropped assumptions visible). Include a forged-checker-line control |
| F1 | Requirement retention under long context and compaction | see Phase S1 | VE authoring cost charged to the VE arm |
| F2 | Size of reviewed work | folded into F0 | |
| F3 | Equal-strength adversary | folded into F0 (frontier attacker writes the obfuscated argument) | |
Funding: Gemini through Vertex AI ($273 trial credit, verified working), OpenRouter ($20), subscriptions for spot checks.

## Language task: make VE read and write like regular English (13:53, user request)

The strict parenthesised form is the canonical internal form (one text, one AST; Lean round-trip proof). Users should see
and write the fluent form. Tasks: (1) fluent becomes the default display everywhere; (2) a deterministic parser for fluent
INPUT with paraphrase-back, and the Lean round-trip/injectivity proof extended to the fluent surface (this also answers the
reviewers' point that the helpful view has no proved property); (3) replace the parenthesised fallback for deep nesting with
enumerated sub-clauses in the style of legal drafting ("all of the following hold: (a) ...; (b) ..."); (4) a precision pass
on the template linter, which currently rejects many natural templates (seen in all four use cases).

## Working position on mathematics (14:52; endorsed by the project lead)

For serious mathematics Lean is the right logic; that is why the labs use it. VE's role there is a readable, verified
STATEMENT layer over Lean: render a Lean theorem statement in VE-style English, let a person (or a checker with
distinguishing scenarios) confirm what it says, keep the proofs in Lean. The problem worth solving is reading the
statement, not checking the proof. Test case: statements from public AI-produced Lean developments (the FLT
formalisation, `openai/ten-proofs`, the zeta-zeros result), each paired with its informal claim; show where a weakened
statement would pass unnoticed (this is stretch experiment E7). The use case `usecases/math-mini-paper` reports what
VE's own logic can and cannot carry and tests this position against the alternatives.

## Phase 2 candidates (after the first paper draft)

| Idea | Why it matters | Depends on | Added |
|---|---|---|---|
| Rust core, differentially tested against the Python core and the Lean evaluator on the shared conformance corpus | A fast, memory-safe checker for deployment; the user asked for it. Value comes only once there is a corpus to test against | `conformance/` corpus from the Lean track; rustup install | 01:40 |
| E7: statement sign-off on real AI-produced Lean theorems (`openai/ten-proofs`, the FLT formalization) | The strongest real-world motivation: proofs are machine-checked, so reading the statement is the whole human job | E1 pipeline; a Lean-statement-to-English renderer beyond v0 | 01:10 |
| Extend v0 toward the statements that did not fit in E0 (arithmetic comparisons, counting, simple temporal operators) | E0's spread shows where coverage fails (Gatekeeper 47%, Alloy 57%, FRET 27%, Clover 13% in the first sample). Each extension needs semantics, renderer rules and new attacks | E0 final numbers | 01:35 |
| Adaptive attacker: the attacker sees the judge's view and its past verdicts, and optimises against it | Fixed attacks measure presentation; an adaptive attacker measures the end-to-end oversight protocol | E1 scored result | 02:05 |
| Judge capability sweep: same items across a ladder of judge strengths | Tests the scaling claim directly: does VE's benefit grow, shrink or vanish as the judge-attacker gap widens? | E1 pipeline | 02:05 |
| Human study package: the E1 and E5 materials exported as a ready-to-run online study with preregistration | No humans are available now; the claim about human readability stays untested until this runs | E1 and E5 materials | 02:05 |
| RL with VE-checked rewards | The training benefit (item 4 in the architecture doc) is untestable without GPUs; design the reward and the honest/deceptive comparison now | GPU access (user will provide) | 02:05 |
| ACE import and comparison with Canonical English | Positions VE against the closest existing systems on the same items | renderer + E1 items | 02:05 |
| Open-weight weak judges on Colab GPUs (1B-8B instruct models), as the bottom of the judge ladder | If Haiku and Luna read FOL too well, the sandwich has no gap. Small open models give a real capability gap, full control of sampling seeds, and no CLI-context asymmetry | E1 dev pilot result; Colab via the user's browser (~200 compute units) | 02:15 |

## Phase U: use-case corpus with a language-gap feedback loop (user request; start when views, argument layer and grammar are merged)

One subagent per document writes it, or a well-chosen part of it, in VE, and records what VE cannot yet say.

Order (orchestrator's decision): first the documents that feed the experiments, then the ones the user finds interesting.
1. Items from the oversight/debate datasets used in E0-E5 (FOLIO stories, Cedar and Gatekeeper policies, a QuALITY-style
   debate question). These decide experiment coverage, so they come first.
2. A real debate: https://opentodebate.substack.com/p/should-america-end-birthright-citizenship . Formalise each side's
   claims as a VE claim graph; mark which disagreements are about premises, which about definitions (shared predicates
   with different senses), and which steps are certified. This is the closest real test of VE's debate story.
3. Part of the US Constitution (for example the 14th Amendment, section 1, which the debate turns on) and part of
   Claude's constitution: norms, exceptions and priorities.
4. The main theorem and definitions of one mathematics paper, one computer-science paper and one physics paper.
5. A recent Reuters or AP news article: attribution ("X said that"), time and numbers.

Feedback loop. Each subagent works in `usecases/<name>/` and produces `source.md` (the excerpt, with licence),
`claims.ve.md`, a coverage table (sentence -> expressed / expressed only through an opaque predicate / not expressible),
and `GAPS.md`. A gap entry names the missing construct (modality or obligation, time, numbers and counting, functions,
n-ary relations, definitions, attribution and quotation, vagueness, exceptions and priorities), gives the smallest
example, and proposes syntax plus semantics. The subagent sends blocking gaps to the orchestrator while it works; the
orchestrator triages them into language-extension tasks for Worker X (semantics, renderer rules, grammar, Lean), and
the subagent retries after the merge. The aggregated gaps table becomes the evidence-based roadmap for VE v1.

## Phase V: VE v0.1 language extensions, ranked by measured need (E0 second rater, 02:09)

Source: `experiments/E0/SECOND_RATER.md` on branch `codex/e0-rater` (210 items, 114 checked witnesses, blind to item labels).
Counts are items out of 210 whose faithful formalization needs the construct.

| Rank | Construct | Items | Where | What it takes |
|---|---|---:|---|---|
| 1 | Numeric comparison and arithmetic | 45 | FRET 18, Clover 16, Gatekeeper 8 | an ordered numeric sort with `<`, `<=`, `+`; finite evaluation is easy, entailment needs a decision procedure or an SMT oracle with checked certificates |
| 2 | Transitive closure / reachability | 27 | Cedar 17 (entity hierarchy `in`), Alloy 9 | a closure operator on binary relations; trivial in finite models, not first-order, so the prover needs induction-free sound rules and will be incomplete |
| 3 | String operations, regex, parsing | 20 | Gatekeeper 20 | opaque today; an honest treatment is an external, specified adapter whose output is a checked relation |
| 4 | Defaults, frequency, counting, metric time, modality | 5 or fewer each | FOLIO, ProofWriter, Alloy, FRET | later profiles |

Do rank 1 and 2 only with semantics in Lean first (extend `denote` and `eval`, keep `eval_iff_denote`), then Python, Rust,
views, grammar and attacks. Each extension is a new profile, not a change to `relational-fol@0`.

## Evidence from the first four use cases (12:32; branch `usecases/main`, one Sonnet agent each, not cross-reviewed)

| Document | Units | DIRECT | REIFIED | OPAQUE | NO |
|---|---:|---:|---:|---:|---:|
| 14th Amendment, section 1 | 4 clauses | 0 | 1 | 3 | 0 |
| Birthright-citizenship debate | 9 claims | shared deductive core formalised; about 5 of 9 claims outside VE (empirical, moral, authority, precedent) | | | |
| Claude's constitution, "core values" excerpt | 23 rows | 0 | 6 | 5 | 12 |
| Reuters article, Fed rate decision | 26 rows | 1 | 11 | 3 | 11 |

Ranked constructs for the next language versions, combining these with the E0 audit:
1. **Obligation, prohibition and permission, with exceptions and defeasible priorities** ("must never", "unless", "generally",
   "prioritise X over Y when they conflict"): dominant in the constitution texts (about 10 of 21 sentences; all three
   "No State shall" clauses). `must` is already reserved in v0.
2. **Numbers and arithmetic** (`order@0`: Lean stage done; Python pending): 7 of 26 news rows; 45 of 210 E0 items.
3. **Definitions** linking a named property to its defining formula (5 of 21 constitution sentences), and **functions /
   definite descriptions** ("the State wherein they reside"), and **relations of arity above two** (which two properties
   conflict: building the conflict rule with `tc[outranks]` over pairs produced a real unsatisfiability).
4. **Attribution and quotation** ("X said that"): 3 of 26 news rows but central to journalism and debate.
5. **Propositional attitudes** ("we believe", "we want"): 7 of 21 constitution sentences.
Not fixable by syntax: open-textured legal terms, empirical predictions, moral premises, weighing of authorities.
What worked better than expected: news ground facts (mostly REIFIED or DIRECT); `closure@0` derived "safety outranks
everything" from three base edges; the debate's hinge was isolated to one predicate's extension.
Practical defect: the hardened template linter rejects many natural verbalisation templates, so the fluent view fell back
to mechanical phrasing: the linter needs a precision pass on real vocabularies.

## Ideas log

- 02:50 From Canonical English (site read; repo study in progress, results go to `design/related-systems.md`):
  (a) **Sense-bound vocabulary.** CE binds every content word to a WordNet sense URI. VE's worst weakness is a vague
  predicate grounded differently in each branch. Requiring each predicate to carry a sense binding, and flagging a
  predicate whose cited evidence uses different senses, is a cheap defence to test as an extra cell in E5.
  (b) **Linter as gatekeeper.** CE puts its checker in the generation loop (rejection sampling, or grammar-constrained
  decoding on open-weight models). VE's parser can do the same: model proposes VE, parser rejects, model repairs. This
  gives E0 an honest autoformalization cost, and works with constrained decoding on Colab models.
  (c) **Document format.** CE's Markdown + JSON-LD frontmatter is a good carrier for a VE environment plus claims.
  (d) CE has no truth-conditional semantics, entailment or countermodels; that is where VE goes further.

- 02:05 The untrusted-explainer contrast (E1) may generalise: any place where an overseen agent controls the
  presentation of a formal object (proof summaries, diff descriptions, test reports) is a place for a deterministic
  renderer. If E1 is positive, a follow-up could test "deterministic summaries of checked artifacts" outside logic.

## Evidence from the math mini-paper use case (2026-09-21, `usecases/math-mini-paper/`)

15 of 19 entailments certified, by the Python replay checker and by the Lean executable alike; 25 of 25 hypotheses shown
necessary by countermodel; one false conjecture refuted and its correction certified. What blocked the rest, in the
order the use case ranks them: lemma citation with conservative definitions (a four-variable congruence times out
although its two halves prove in 50 ms, and VE cannot cite them); predicate arity above 2; an induction rule for
closure (`tc[r]` is the least such relation: monotonicity stays ResourceLimit); function symbols (unary first);
relation parameters for schematic theorems. Euclid's theorem is writable but meaningless because `prime` is
uninterpreted and `times` is ternary. This supports the working position above: keep VE small, make it the readable,
checked STATEMENT layer over Lean, and do only lemma citation, closure induction and arity 3-4 in VE itself. All frozen
under PLAN-V3 until a pilot or the grant.

## From docs/formal-proof-experiments-handoff.md (cherry-picked 9fe83bc, 2026-09-22)

Adopted into the plan as package 3b, after P5 and before the long-argument study, subscription quota only:
**formalise one original Barnes-Christiano physics argument (the iceberg problem) end to end in Lean from accepted
physical laws, with a separate cost ledger (model review, formalisation, proof repair, checking, compute) and an
assumption checklist.** It measures the "mandatory proof" tax on the canonical example and is the honest companion to
our finding that VE contributes nothing to obfuscation itself: the residue is the model/assumption review. The handoff's
experiment 2 (do humans catch a valid proof of the wrong model with VE vs a structured formal interface) is the best
human study we have on the list and stays deferred with the other human studies; experiment 3 (mandatory proofs vs
adversarial debate) folds into P5 and the long-argument study; experiment 4 (size scaling, PrOntoQA subset) into the
grant-scale plan. Starting evidence: 11 checked rational-algebra lemmas in experiments/obfuscated-arguments/Feasibility.lean.

Package 3b result (2026-09-22): [ICEBERG direct proof and measured ledger](experiments/obfuscated-arguments/iceberg/README.md).
The ideal rational root is checked, including finite-history no-spill and an explicit air-mass tolerance;
independent physical-model review and the matched VE-versus-interface/debate experiments remain open.

## Cryptography-inspired ideas (2026-09-22)

See `design/crypto-inspired-oversight.md`. Top three: separating certificates for "cannot access" claims in T1
(checking cheap, redoing expensive: the asymmetry where a frontier benefit is plausible); signed checker verdicts
(P1 showed judges cannot detect forgeries); meaning_id commitments before cross-examination as a P5 arm. Also the
proof-carrying-actions direction (agents prove a tool call complies before it runs).
