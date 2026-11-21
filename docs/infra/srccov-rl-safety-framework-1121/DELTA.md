# srccov-rl-safety-framework-1121 DELTA

There is no user-visible change of VE. This file has no row and reserves no signature.

This item changes no file under `ve/`, `lean/`, `rust/` or `tools/` (`git diff --numstat main...HEAD`; REPORT.md
section 5 lists the files). VE's diagnostics, fault order, fields, verdicts, availability and CPU stay as they are on
main. The change is to one use case's translation: two new rule blocks in `usecases/safety-framework/rules.d1.ve`,
two new obligation predicates with legends quoted from the source in `vocabulary.py`, and the recorded outputs those
regenerate.

In `results.json`, no keyed item moves: `comparison` is equal to main's, and every item keeps its verdict. Item N3
("every rule has a witness") keeps NONE. It now counts 47 rules, and the two new rules have the witness case
A-L0-DEV. Two `document_conflicts` rows are added, one for each new predicate, and both are CONFLICT-FREE. This is
the same kind of change as the precedents srccov-safety-framework-1119 and fsf-repair-f8-disclosure-1119.
