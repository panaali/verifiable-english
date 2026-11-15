# Who computes the keyed answers of a norm document with soft rules

VE's rule is that Lean decides meaning and acceptance (docs/ARCHITECTURE.md section 1). Norm documents with soft
rules do not follow that rule fully yet, and every safety-framework use case is one: `anthropic-rsp`,
`openai-preparedness` and `safety-framework`, the three harnesses scored against a frozen answer key. Lean
elaborates the soft rules and replays every certificate. Since kb-10b, Lean also decides which rules a case
selects and the completed outcome there: Lean's `soft-selected` kind answers them for a document built from its
soft source (`SoftenedNormDocument.selected_rules` and `outcome_at`). Since kb-10c, the harnesses' conflicts are
decided by Lean's soft-norms route (`ve.soft_route.decide_soft_conflict`): Python's search still **evaluates the
conflict targets on each case model**, but only to propose a witness, which the route's `soft-conflict` kind
replays over the targets Lean regenerates (CONFLICT, `VE.SoftNorms.Run.soft_wire_conflict_witness`), and Python's
prover only proposes certificates, which the same kind replays over `Background_base′` (CONFLICT-FREE,
`soft_wire_conflict_free`). Lean's CONFLICT-FREE holds among rules on the same act, conditional on the open
coherence premises its answer names (`conditional_on`). `ve.norms.check_conflict` itself is unchanged: called on a
soft document it is still Python's retained path (`_lean_route` is false for any document that is not exactly a
`NormDocument`), and no keyed harness calls it.

So a keyed answer is only as checked as the row it comes from. A selection or an outcome is Lean's `soft-selected`
answer. A CONFLICT or a CONFLICT-FREE answer is Lean's `soft-conflict` replay. An entailment is a proof that Lean
replayed, over goals that Python built.

## The answers and their owners

The *Recorded as* column names the paths that `usecases/keyed_paths.py` counts. `tests/test_keyed_answers_authority.py`
checks this table against those paths on a small soft document, and against the saved counts of the three
harnesses in [keyed-answers.json](keyed-answers.json) (measured 2026-11-15, after kb-10c; regenerate with
`uv run python usecases/measure_keyed_paths.py --write`).

| Answer | Owner | Recorded as |
|---|---|---|
| The soft elaboration: rule layers, exceptions and decision atoms | Lean | `soft-elaborate` |
| Which rules a case selects, and the completed outcome there | Lean | `soft-selected` |
| The same, for a soft document built by hand without its soft source (no keyed harness builds one) | Python | `selected_rules`, `outcome_at` |
| The conflict search's formulas, which only propose a witness or a proof goal (Lean replays both over the targets it regenerates) | Python | not recorded (`NormDocument.selection`, `outcome`, `conflict_targets`) |
| An exception's sufficient condition, evaluated by the `safety-framework` harness to set a case model's decision atoms | Python | `holds_at` |
| A conflict (CONFLICT, the witness Python's search proposed) or conflict-freedom (CONFLICT-FREE, the certificates Python's prover proposed), as the keyed harnesses ask (`decide_soft_conflict`) | Lean | `soft-conflict` |
| The witness search on a case model (an untrusted generator; its witness is an answer only once Lean replays it) | Python | `_find_conflict` |
| A conflict through `ve.norms.check_conflict` on a soft document (no keyed harness calls it) | Python | `_check_conflict_python` |
| Whether a case model satisfies the background axioms | Python | `_evaluate_validated` |
| The prover's check of its own proof before Lean replays it (an untrusted step, never an answer) | Python | `prover-self-replay` |
| A certificate: an entailment, or conflict-freedom through `ve.norms.check_conflict` | Lean | `_check_certificate_lean` |
| A formula evaluated through the public `evaluate()` | Lean | `_evaluate_lean` |

The Lean parts carry Lean's proofs. The Python parts are VE's retained Python path, and no proof covers them.
