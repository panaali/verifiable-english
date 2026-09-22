# Package 3b: a checked direct answer to ICEBERG

**Result:** `Iceberg.iceberg_root` proves that W's height is unchanged, A's height
is within a specified tolerance of its initial height and never higher, M's height
strictly decreases, and none of the three ideal tubs spills. The proof covers
arbitrary finite quasistatic histories. It imports only `Std`, uses exact `Rat`,
and does not translate the misleading oil/debate branches.

- [SPEC.md](SPEC.md): intended source question, model, laws and approximation contract.
- [ASSUMPTIONS.md](ASSUMPTIONS.md): every physical premise and its failure mode.
- [Lean source](../../../lean/Iceberg.lean): definitions, 13 audited theorems,
  including a combined concrete witness for all three cases.
- [COST.md](COST.md), [cost.json](cost.json): measured phase costs and telemetry scope.
- [verification.json](verification.json): full serial build and final axiom audit.
- [attempts.jsonl](attempts.jsonl): all six standalone development invocations,
  including four failed invocations (failed logs naturally mention `sorryAx`).
- [VE.md](VE.md): the checked qualitative skeleton and its arithmetic boundary.

## Direct argument

Initial force equilibrium cancels positive gravity to yield
`rho * initialDisplaced = iceMass + inclusionMass`.
At each equilibrium stage, nonnegative upward support implies that the remaining
contents displace at most their mass divided by water density. Mass conservation
then bounds the occupied volume by the initial brim capacity. Induction over the
rim-discharge rule proves that cumulative spill stays zero, however many modelled
stages occur. This does **not** assume away the competing claim that W spills.

Melting, final volume addition and prismatic-tub geometry then give

```text
rho * area * (finalHeight - rim) = rho * finalInclusionVolume - inclusionMass.
```

Substitution yields the root result. The air-mass bound is
`inclusionMass <= rho * area * epsilon`. There is a `1/1000` metre corollary, but
only when that bound holds in SI units. With positive air mass the ideal level
strictly drops: exact air equality would be the wrong theorem. There is no
unconditional millimetre guarantee in the dimensionless original question.

Atmospheric buoyancy, expansion, waves and other omitted physics remain outside
this ideal model. `residual_height_bound` propagates a *supplied* residual bound;
it is not an empirical validation of these omissions. In particular, the exact
no-spill conclusion must not be exported to a model retaining atmospheric
buoyancy without redoing the accounting.

## Reproduction

From the repository root, using the pinned Lean 4.24.0 installation:

```sh
python3 experiments/obfuscated-arguments/iceberg/verify.py
python3 experiments/obfuscated-arguments/iceberg/qualitative.py
```

`verify.py` builds local modules in dependency order, one `lake build +Module:o`
at a time, including native objects, before the final `lake build`. The default
Lake targets include `Iceberg`, so future ordinary builds cover this proof.
The final fresh Lean invocation checks all printed axiom dependencies against
`propext`, `Classical.choice`, and `Quot.sound`. No Mathlib, custom global axioms,
`sorry`, `admit`, or native decision oracle occurs in the source.

The rational witness uses rho = area = gravity = 1, ice mass 9 and rim height 100.
W has inclusion mass/volume 1 and final height 100; A has mass 1/10000 and final
height 100 - 1/10000; M has mass 2, volume 1/4, density 8 and final height 100 - 7/4.
These are consistent ideal states, not measured tubs or a continuous-dynamics proof.

## Lesson for mandatory proofs versus debate

For this example, a short direct certificate can establish the root without
locating every flaw in the adversarial tree. Kernel checking is cheap relative
to specification and authoring. It removes the need to trust an uninspected
algebraic deduction, but leaves physical-model choice, tolerance and source-to-model
correspondence for review. This one self-reviewed pilot supplies no controlled
cost comparison with debate, no human readability evidence, no proof that VE is
better than an equivalent structured interface, and no solution to the general
obfuscated-arguments problem. Credit the arithmetic result to Lean; VE's demonstrated
contribution here is only a readable/checkable relational skeleton.
