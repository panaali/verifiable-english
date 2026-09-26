# Identity-bound property content

The four unary definitions encode the excerpt's recorded conditions. `holds_property(model, property)` links `@safety`, `@ethics`, `@guidelines`, and `@helpfulness` to those bodies. The definitions are Background premises, not extra theorem hypotheses.

| Constant | Defined predicate | Value in existing true-model fixture |
|---|---|---|
| `@safety` | `safety_content` | `True` |
| `@ethics` | `ethics_content` | `True` |
| `@guidelines` | `guidelines_content` | `True` |
| `@helpfulness` | `helpfulness_content` | `True` |

The priority sentence still needs the W1 norm profile for its defeasible reading; this definition rerun makes no priority-rule claim. Lean and Rust currently reject these `defined` declarations.
