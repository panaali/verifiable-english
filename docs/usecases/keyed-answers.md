# Who computes the keyed answers of a norm document with soft rules

VE's rule is that Lean decides meaning and acceptance (docs/ARCHITECTURE.md section 1). Norm documents with soft
rules do not follow that rule fully yet, and every safety-framework use case is one: `anthropic-rsp`,
`openai-preparedness` and `safety-framework`, the three harnesses scored against a frozen answer key. Lean
elaborates the soft rules and replays every certificate. Since kb-10b, Lean also decides which rules a case
selects and the completed outcome there: Lean's `soft-selected` kind answers them for a document built from its
soft source (`SoftenedNormDocument.selected_rules` and `outcome_at`). Python still builds the conflict targets
and **evaluates them on each case model**, so every conflict found on a model is Python's (`_lean_route` is false
for any document that is not exactly a `NormDocument`, so a `SoftenedNormDocument` never reaches Lean's norms
routes). Work item `kb-10c` moves the conflicts onto Lean's soft-norms route.

So a keyed answer is only as checked as the row it comes from. A selection or an outcome is Lean's `soft-selected`
answer. A CONFLICT is Python's evaluation of Python's formulas. A CONFLICT-FREE answer or an entailment is a proof
that Lean replayed, over goals that Python built.

## The answers and their owners

The *Recorded as* column names the paths that `usecases/keyed_paths.py` counts. `tests/test_keyed_answers_authority.py`
checks this table against those paths on a small soft document, and against the saved counts of the three
harnesses in [keyed-answers.json](keyed-answers.json) (measured 2026-11-14, after kb-10b; regenerate with
`uv run python usecases/measure_keyed_paths.py --write`).

| Answer | Owner | Recorded as |
|---|---|---|
| The soft elaboration: rule layers, exceptions and decision atoms | Lean | `soft-elaborate` |
| Which rules a case selects, and the completed outcome there | Lean | `soft-selected` |
| The same, for a soft document built by hand without its soft source (no keyed harness builds one) | Python | `selected_rules`, `outcome_at` |
| The conflict search's formulas: the conflict targets | Python | not recorded (`NormDocument.selection`, `outcome`, `conflict_targets`) |
| An exception's sufficient condition, evaluated by the `safety-framework` harness to set a case model's decision atoms | Python | `holds_at` |
| A conflict and its witness (CONFLICT) | Python | `_check_conflict_python`, `_find_conflict` |
| Whether a case model satisfies the background axioms | Python | `_evaluate_validated` |
| The prover's check of its own proof before Lean replays it (an untrusted step, never an answer) | Python | `prover-self-replay` |
| A certificate: conflict-freedom (CONFLICT-FREE) or an entailment | Lean | `_check_certificate_lean` |
| A formula evaluated through the public `evaluate()` | Lean | `_evaluate_lean` |

The Lean parts carry Lean's proofs. The Python parts are VE's retained Python path, and no proof covers them.
