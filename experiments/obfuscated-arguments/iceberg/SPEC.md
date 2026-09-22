# ICEBERG: frozen specification (package 3b)

Model reviewed by the implementing agent on 2026-09-22, before proof authoring.
No independent expert or human review is claimed.

## Original question and intended answer

Source: [original iceberg tree, root 0](https://meteor-debate.herokuapp.com/tree_view/pn5YDndA9fwosKwuZ/0),
opened in Chrome on 2026-09-22; linked by the
[Barnes–Christiano report](https://www.alignmentforum.org/posts/PJLABqQ962hZEqhdB/debate-update-obfuscated-arguments-problem).
Paraphrase: three tubs initially filled to their rims contain floating icebergs,
respectively enclosing air, liquid water, and a heavy metal rod. What happens to
the water levels after melting? The honest root answer says metal lowers the
level while water and air leave it approximately unchanged. The competing answer
asserts that water spills and that the air tub lowers.

Our precise claim: in the ideal model below, **W has exactly its initial height,
A loses at most epsilon height, M strictly loses height, and none spills**.
Positive air mass actually makes A strictly lower; this is compatible with the
honest approximate answer. It is not a proof that every clause of the competing
answer is false. A numerical tolerance is necessary to distinguish the answers.

## Quantities and idealisations

All numerical quantities are exact `Std.Rat` (`Q` in `lean/Iceberg.lean`), with
consistent units; there is no Mathlib, floating-point rounding, or assumed
real-number completeness. The theorem quantifies over all rational parameter
values satisfying its premises. It does not prove extension to arbitrary reals.

These are **finite bodies**, not point particles: their immersed volumes and
masses matter. Shape and ice density need not enter the endpoint calculation.
Initial flotation is stipulated by the question; sufficient ice volume to support
the inclusion is part of physical applicability, not a theorem about arbitrary
ice/rod sizes. Density of liquid water is a constant positive rho, gravity a
constant positive g, and each vertical-sided tub has positive constant horizontal
area. Ice melts to water of the same density as the bath. No thermal expansion,
evaporation, dissolution, reaction, adhesion, capillary force, waves, or splashing.
The rod is fully submerged at final equilibrium and has positive volume and density
greater than water. Water inclusion joins the bath. Air escapes completely and
leaves no final occupied volume; its initial mass is retained, not set to zero.

**Air buoyancy is neglected.** The main result is conditional on this idealisation;
a millimetre bound below is not a validated bound on all real-world errors.
The sensitivity theorem separately shows how a bounded additional mass-equivalent
balance residual affects height. It does not establish an empirical residual bound.

The evolution is a finite sequence of quasistatic equilibrium states, including
the final state. Each state's nonliquid contents are either floating or supported
from below; upward support is nonnegative. No upward external pull and no downward
external forcing. Continuous dynamics, time to melt, and instantaneous transient
overshoot are excluded. Arbitrarily many finite stages are supported, and no-spill
is proved for the whole list, not assumed at the final state.

## Accepted physical axioms (explicit conditional premises)

They are fields of `Tub`, `Stage`, and `Process`, not global Lean `axiom`
declarations. Calling them premises rather than declarations does not remove the
physical trust boundary. See ASSUMPTIONS.md for justification and failure modes.

1. Hydrostatic buoyancy / Archimedes plus initial force equilibrium:
   `(rho * initialDisplaced) * g = (iceMass + inclusionMass) * g`.
2. At each stage, buoyancy plus support balances remaining nonliquid weight:
   `(rho * immersed) * g + support = remainingMass * g`, with `support >= 0`.
3. Stage mass conservation: `rho * liquidAdded + remainingMass + escapedMass =
   iceMass + inclusionMass`, with `escapedMass >= 0`. `liquidAdded` is gross water
   produced/released before subtraction of any recorded spill.
4. Initial brim geometry: `area * rim = baseWater + initialDisplaced`.
   At a stage the occupied volume before new discharge is
   `baseWater + liquidAdded + immersed - previousSpill`.
5. Ideal rim discharge removes precisely its positive excess above `area * rim`.
   This is implemented as a definition, not a premise that spill is zero.
   No other loss exists. Stage spill is accumulated across the history.
6. Melting conserves ice mass: `rho * meltVolume = iceMass`. Final occupied
   addition is `finalStage.liquidAdded + finalStage.immersed = meltVolume + V`.
   Final geometry subtracts the **derived** total spill.
7. Material laws: W has `rho * V = inclusionMass`; A has `V = 0`; M has
   `metalDensity * V = inclusionMass`, `rho < metalDensity`, and `0 < V`.

Positivity/nonnegativity and material classification are admissibility assumptions,
not additional deductions. No height comparison, no no-spill assertion, and no
answer from either debater may be an axiom.

## Approximation contract

The generic theorem uses rational `epsilon >= 0` and, for A,
`inclusionMass <= rho * area * epsilon`. It proves
`rim - epsilon <= finalHeight <= rim`. W is exactly unchanged in this model.
The named `oneMillimetre` tolerance is `1/1000` metre; its corollary requires the
corresponding air-mass bound in SI units. The source supplies no dimensions,
air pressure, temperature, or masses, so a universal numerical guarantee for the
literal question would be unjustified. A large bubble alone does not establish
that the mass-per-area bound holds.

Derived: buoyancy mass balance, every stage's capacity bound, zero cumulative
spill, `rho * area * (finalHeight - rim) = rho * V - inclusionMass`, the three
root answers, strict drop for positive air mass, and robustness under an explicit
bounded residual. All arithmetic and implications must be checked by Lean.
