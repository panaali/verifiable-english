# Assumption checklist and trust boundary

All entries are explicit in SPEC.md; algebra is derived in `lean/Iceberg.lean`.
This is an agent's model review, not independent validation of the physical model.

| Premise / definition | Physical justification | What breaks if false |
|---|---|---|
| `Tub.rho_pos`, `g_pos`, `area_pos` | Water, gravity and an open tub have positive density, gravitational acceleration and section area. | Cancellation, volume-to-height conversion and sign inference fail at zero/negative values. |
| `Tub.ice_nonneg`, `inclusion_nonneg`, `base_nonneg`, `displaced_nonneg` | Masses and occupied volumes are nonnegative. | Negative masses could reverse the air sign; other negative data lack the stated physical interpretation. Some domain checks are not needed for the algebra. |
| `Tub.initial_float` | Archimedes' displaced-water force equals total weight for a freely floating body. | Initial displaced volume need not equal total mass divided by density. |
| `Stage.force_balance`, `support_nonneg` | At quasistatic equilibrium, buoyancy plus upward bottom support equals remaining weight; freely floating stages have zero support. | An external pull, downward forcing, acceleration or a buoyant inclusion rising freely may invalidate the capacity bound. |
| `Stage.mass_conservation`, `escaped_nonneg` | Released water plus retained contents plus escaped gas preserve the initial object mass. | Added/removed material, evaporation, dissolved gas, or unaccounted loss changes level accounting. |
| `Stage.liquid_nonneg`, `remaining_nonneg`, `immersed_nonneg` | Released water, remaining mass and immersion are physically nonnegative. | The numerical witness need not describe any body. These are admissibility checks, not all logically necessary for the root. |
| `Tub.initially_brimful` | A prismatic tub's capacity is area times rim height, equal to bath water plus initial displacement. | Nonuniform section needs a different monotone volume-height relation; a non-brimful tub needs a different discharge capacity. |
| `excess`, `spilled` | An ideal open rim drains positive excess, retaining the rest; there is no splashing, leakage or siphon. | Additional losses could lower W even if there is no volume-induced overflow. **Zero spill is proved**, never supplied as a premise. |
| `Process.melting`, `melt_nonneg` | Ice mass becomes liquid water with the bath's fixed density. | Thermal expansion, evaporation, salinity or density changes add a correction. |
| `Process.final_contents`, `inclusion_volume_nonneg` | Volumes of the melted water and final inclusion contribution add; contents are disjoint. | Dissolution, reaction, partial emergence or trapped residual gas changes occupied volume. |
| `Process.final_geometry`, `height_nonneg` | At the final equilibrium, bath water plus occupied addition minus cumulative spill fills the tub to its measured height. | Capillarity, changing geometry, omitted spill history or an unequilibrated surface invalidates the translation to level. |
| W material premise `rho * V = inclusionMass` | The inclusion is water at the same density as the bath. | A different fluid/density can raise or lower the free occupied volume. |
| A material premise `V = 0` | All bubble gas escapes into the atmosphere. | Retained/submerged gas displaces water at the end. |
| A `small_mass`, `epsilon_nonneg` | The chosen tolerance is meaningful only if air mass per rho-area is small enough. | A may fall by more than the tolerance; the source does not give enough data to check this bound. |
| M `metalDensity * V = inclusionMass`, `dense`, `volume_pos` | A positive-volume, rigid, insoluble metal rod is denser than water and rests fully submerged. | Equal density yields zero change; lower density or partial emergence needs another model. |
| Neglected air buoyancy | Standard reduced hydrostatic model, accurate only when omitted atmospheric forces are suitably small. | Even W may discharge a little water; exact real-world no-spill is not claimed. |
| Finite equilibrium history | Represents quasistatic melting/release without transient overshoot; there is no bound on list length. | The proof does not cover continuous dynamics, waves or a rod impacting the tub. |
| Rational quantities | Exact arithmetic for idealised rational data. | No theorem here transfers to arbitrary real-valued trajectories or measurement uncertainty. |
| `residual_height_bound` balance and residual interval | An explicitly supplied error budget can propagate to a height budget. | Without independently justified bounds it says nothing quantitative about omitted physics. These are **additional conditional inputs**, not established physical laws or part of `iceberg_root`. |

The gas-escape and dense-submerged-rod endpoint assumptions match the question's
usual ideal reading. Their physical realisability is not proved from fluid dynamics.
The non-vacuity witnesses check compatible rational states, not continuous trajectories.
No part of the competing root answer, or of the oil detour, is imported as a law.

`#print axioms` audits every named theorem. Allowed logical foundations are
`propext`, `Classical.choice`, and `Quot.sound`; `sorryAx` is forbidden. The physical
laws are visible theorem arguments through structures, so **absence of custom
axioms in this printout does not mean assumption-free physics**. Lean's kernel and
standard rational implementation are trusted; no `native_decide` is used.
