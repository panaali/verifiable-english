# What VE does, and what remains outside it

The physics proof is in Lean over rationals. The current relational VE profile
can express case classifications, conjunction, universal implication and the
qualitative relations between an outcome and an initial state. It cannot express
mass conservation, products, density, positive rational quantities, exact volume
accounting, or a numerical approximation bound. Even an order-only profile would
not supply the arithmetic used here.

| Content | Representation |
|---|---|
| A case is a water / air / metal case | Unary relation in VE, with externally specified interpretation. |
| A case satisfies the physical model | Opaque `admissible` predicate; NOT a VE encoding of the model equations. |
| A's air mass meets the tolerance budget | Opaque `bounded` predicate; the inequality remains in Lean. |
| Water/air is stable within epsilon; metal is lower; no spill | Qualitative predicates, with numeric meanings supplied in the dictionary. |
| Material case plus admissibility implies its outcome | VE universal implications; imported results of Lean arithmetic, not physical axioms. |
| Three cases therefore satisfy the qualitative root | Actual VE deduction, checked in Python and replayed by the Lean VE certificate checker. |

`imports.ve` contains the four **derived theorem imports**, corresponding to
`water_unchanged` (with nonnegative tolerance), `air_approximately_unchanged`,
`metal_lowers`, and `no_spill`. `facts.ve` classifies W, A and M and supplies their
admissibility/bound leaves. `conclusion.ve` combines their outcomes. `dry` means
zero cumulative spill, not absence of water; `stable` means `Within`, not exact
identity. Every carrier case has a fixed nonnegative tolerance by interpretation.
The stronger exact W equality and one-sided A bound remain in Lean.

This correspondence is documented and agent-reviewed, **not a proved translation
from Lean statements to VE**. VE treats the imports as premises. Its certificate
checks only their relational consequence; it does not independently verify the
physics by giving arithmetic an opaque predicate name. This distinction avoids
crediting VE with Lean's arithmetic proof.

Reproduce the canonical VE renderer/parser roundtrip and both certificate checks:

```sh
python3 experiments/obfuscated-arguments/iceberg/qualitative.py
```

Run `verify.py` first to build `ve_conformance`. `environment.json` records the
predicate dictionary, `qualitative-query.json` the exact assumptions, conclusion
and certificate, and `qualitative-verification.json` the replay result.
