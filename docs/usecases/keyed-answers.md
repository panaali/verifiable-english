# Who computes the keyed answers of a norm document with soft rules

VE's rule is that Lean decides meaning and acceptance (docs/ARCHITECTURE.md section 1). Norm documents with soft
rules do not follow that rule yet, and every safety-framework use case is one: `anthropic-rsp`,
`openai-preparedness` and `safety-framework`, the three harnesses scored against a frozen answer key. Lean
elaborates the soft rules and replays every certificate. Python's `ve/norms.py` and `ve/softnorms.py` build the
rule formulas and **evaluate them on each case model**: Python decides which rules a case selects, a completed
outcome and every conflict found on a model. `_lean_route` is false for any document that is not exactly a
`NormDocument`, so a `SoftenedNormDocument` never reaches Lean's norms routes. Work item `kb-10` moves these
answers onto Lean's soft-norms route.

So a keyed answer is only as checked as the row it comes from: a selection, an outcome or a CONFLICT is Python's
evaluation of Python's formulas. A CONFLICT-FREE answer or an entailment is a proof that Lean replayed, over goals
that Python built.

## The answers and their owners

The *Recorded as* column names the paths that `usecases/keyed_paths.py` counts. `tests/test_keyed_answers_authority.py`
checks this table against those paths on a small soft document, and against the saved counts of the three
harnesses in [keyed-answers.json](keyed-answers.json) (measured 2026-11-11; regenerate with
`uv run python usecases/measure_keyed_paths.py --write`).

| Answer | Owner | Recorded as |
|---|---|---|
| The soft elaboration: rule layers, exceptions and decision atoms | Lean | `soft-elaborate` |
| The rule formulas: which rules are selected, a predicate's outcome, the conflict targets | Python | not recorded (`NormDocument.selection`, `outcome`, `conflict_targets`) |
| Which rules a case selects | Python | `selected_rules` |
| A completed outcome on a case, evaluated by the harness | Python | `completed`, `holds_at` |
| A conflict and its witness (CONFLICT) | Python | `_check_conflict_python`, `_find_conflict` |
| Whether a case model satisfies the background axioms | Python | `_evaluate_validated` |
| The prover's check of its own proof before Lean replays it (an untrusted step, never an answer) | Python | `prover-self-replay` |
| A certificate: conflict-freedom (CONFLICT-FREE) or an entailment | Lean | `_check_certificate_lean` |
| A formula evaluated through the public `evaluate()` | Lean | `_evaluate_lean` |

The Lean parts carry Lean's proofs. The Python parts are VE's retained Python path, and no proof covers them.
