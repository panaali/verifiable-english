# df-1bb delta: the English of `--assume-no-exception`

Base: `git merge-base HEAD main`. No Lean file changes (trust +0), and no verdict, basis, form, assumption, `forced`
entry, coherence row, diagnostic or fault order changes: every field `ve document readings --assume-no-exception`
printed before prints byte for byte the same (`tests/test_defaults_lean.py` and `tests/test_defaults_answer.py`, whose
exact assertions change only by the new field). Without the flag nothing changes (P-1's answers without it are still
df-03's recorded ones, `tests/test_defaults_lean.py::test_p1_follows_unless_an_exception_applies`). The relay lint and
the recorded route cases change no output.

| # | What changes | Before | After | Evidence | Ruling |
|---|---|---|---|---|---|
| 1 | `ve document readings --assume-no-exception` (`ve.defaults.ask`): the default question's answer gains the field `english`, the plan's sentences (2.8: DE1, DE1′, DE2, DE2·u, DE2′, DE2′·u, DE3, DE4, DE4·u, DE6, DE6′, DE7 with DE7a, DE7a·u, DE7b, DE7b·u, DE11, DE12) rendered from Lean's bound rows; information is added, nothing is removed or renamed, and the strict answer `{"question": "strict", "valid": true}` is unchanged | `{"question": "default", "kind", "answer"[, "coherence"]}` | the same, plus `"english": [<sentence>, ...]` | goldens updated: `tests/test_defaults_lean.py::test_alpha_needs_its_one_exception_and_the_strict_countermodel`, `tests/test_defaults_answer.py::test_strict_answer_only_when_lean_says_valid`; each sentence equal to the plan's wording of Lean's row: `tests/test_defaults_english.py` (one fixture per form, P-1 and P-3); bound to the request: every rule, party, rank, act and entity the sentences name is the request's (`::test_a_label_the_request_cannot_give_is_refused`, `::test_a_forced_rule_the_request_lacks_is_refused`; Lean's rows are bound by `ve.defaults.answer` first) | R3 |
