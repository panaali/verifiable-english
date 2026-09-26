# Definitions statement review

The current Lean implementation covers a fresh unary predicate whose body is
an existing unary predicate of the same sort. It is a foundation for the full
definition layer, not an enabled `definitions@0` route.

| Theorem | Statement in plain words |
|---|---|
| `faithful` | The generated biconditional holds exactly when the new and existing predicates agree on every object of their sort. |
| `conservative` | Every admissible input structure has exactly one admissible expansion satisfying that biconditional. |
| `alias_acceptance` | A checked certificate using the definition proves an old-vocabulary conclusion from old-vocabulary premises in every original admissible structure. |

The proposed citation rule permits a lemma conclusion only after checking its
certificate under the same environment and confirming all its hypotheses and
transitive labelled leaves are available to the citing deduction. Shared
reading choices must agree. This rule is not yet implemented by W3.

The English forms “call a point prime if …”, “by Theorem 3”, “every point that
is prime …”, and “no point is prime” are not yet offered by `ve assist` or the
surface parser. Their authoring gate remains closed.
