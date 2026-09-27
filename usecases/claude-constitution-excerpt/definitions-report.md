# Identity-bound property content

The four unary definitions encode the excerpt's recorded conditions. `holds_property(model, property)` links `@safety`, `@ethics`, `@guidelines`, and `@helpfulness` to those bodies. The definitions are Background premises, not extra theorem hypotheses.

| Constant | Defined predicate | Value in existing true-model fixture |
|---|---|---|
| `@safety` | `safety_content` | `True` |
| `@ethics` | `ethics_content` | `True` |
| `@guidelines` | `guidelines_content` | `True` |
| `@helpfulness` | `helpfulness_content` | `True` |

Python, Lean and Rust decode the declarations, compute every defined table from its body and agree on all eight values above (four contents, four `holds_property` links).

The definitions, as the English surface writes them:

- By definition, for every entity of sort "claude_model", that entity of sort "claude_model" is classified as "ethics_content" exactly when both of the following hold:
  (a) that entity of sort "claude_model" is honest;
  (b) for every action that is classified as "inappropriately_harmful", it is not the case that that entity of sort "claude_model" performs that action.
- By definition, for every entity of sort "claude_model", that entity of sort "claude_model" is classified as "guidelines_content" exactly when for every guideline that is relevant, that entity of sort "claude_model" follows that guideline.
- By definition, for every entity of sort "claude_model", that entity of sort "claude_model" is classified as "helpfulness_content" exactly when for every principal that that entity of sort "claude_model" has the recorded relation "interacts" to, that entity of sort "claude_model" benefits that principal.
- By definition, for every entity of sort "claude_model", that entity of sort "claude_model" is classified as "safety_content" exactly when for every mechanism that is appropriate, it is not the case that that entity of sort "claude_model" undermines that mechanism.
- By definition, for every entity of sort "claude_model", for every property, that entity of sort "claude_model" has the recorded relation "holds_property" to that property exactly when at least one of the following holds:
  (a) at least one of the following holds:
    (i) at least one of the following holds:
      (a) both that property is the same as safety and that entity of sort "claude_model" is classified as "safety_content";
      (b) both that property is the same as ethics and that entity of sort "claude_model" is classified as "ethics_content";
    (ii) both that property is the same as guidelines and that entity of sort "claude_model" is classified as "guidelines_content";
  (b) both that property is the same as helpfulness and that entity of sort "claude_model" is classified as "helpfulness_content".

The priority sentence still needs the W1 norm profile for its defeasible reading; this definition rerun makes no priority-rule claim.
