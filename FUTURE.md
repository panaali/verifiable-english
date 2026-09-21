# Future phases and idea backlog

The orchestrator appends here as results and ideas arrive. When the current plan in `PLAN.md` is finished, or the
user has not returned, the next phase is chosen from this file: pick the item with the highest expected information
per hour, write it into `PLAN.md` as a new phase, and continue. The project does not stop on its own.

Standing limits: no model training (no GPU yet), no pushing or publishing without the user, no human-participant claims.

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
