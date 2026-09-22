import Std

/-!
Small feasibility probes for the three physics trees linked by Barnes (2020).
These are NOT complete formalizations of the physics or of the debate transcripts.
They use rational algebra, not continuous real-valued trajectories. Physical balance
laws and the interpretation of quantities are explicit inputs, not proved facts.
Run: lean +leanprover/lean4:v4.24.0 experiments/obfuscated-arguments/Feasibility.lean
-/

namespace ObfuscationFeasibility

-- ICEBERGS: an initially floating composite object, then melted ice plus an
-- inclusion. before/after are occupied volumes above the same baseline water.
-- The two premises are buoyancy (neglecting air buoyancy) and final accounting.
theorem iceberg_balance
    (rho before after iceMass inclusionMass finalInclusionVolume : Rat)
    (hFloat : rho * before = iceMass + inclusionMass)
    (hFinal : rho * after = iceMass + rho * finalInclusionVolume) :
    rho * (after - before) = rho * finalInclusionVolume - inclusionMass := by
  grind

-- Use volume units whose water mass is numerically the same: rho = 1.
-- A water inclusion has final volume equal to its mass in these units.
theorem water_inclusion_no_change
    (before after iceMass inclusionMass : Rat)
    (hFloat : before = iceMass + inclusionMass)
    (hFinal : after = iceMass + inclusionMass) : after = before := by
  grind

-- An ideal massless bubble escapes without contributing final occupied volume.
theorem ideal_air_no_change
    (before after iceMass : Rat)
    (hFloat : before = iceMass)
    (hFinal : after = iceMass) : after = before := by
  grind

-- A dense inclusion sinks and occupies less volume than the water its mass
-- displaced while floating. The ice contributes the same final meltwater mass.
theorem dense_inclusion_level_drops
    (before after iceMass inclusionMass inclusionVolume : Rat)
    (hFloat : before = iceMass + inclusionMass)
    (hFinal : after = iceMass + inclusionVolume)
    (hDense : inclusionVolume < inclusionMass) : after < before := by
  grind

-- Exact air mass cannot just be silently discarded: under this alternative
-- model with positive bubble mass, ignoring air buoyancy, the level drops.
theorem positive_air_mass_changes_answer
    (before after iceMass airMass : Rat)
    (hFloat : before = iceMass + airMass)
    (hFinal : after = iceMass)
    (hAir : 0 < airMass) : after < before := by
  grind

-- The displayed tree's node 14 uses after - before, while node 12 attaches
-- a decrease to before - after < 0. With one meaning of these variables,
-- that sign test instead implies a rise. This is about the written sign test.
theorem iceberg_sign_check
    (before after : Rat) (h : before - after < 0) : before < after := by
  grind

-- TRAIN: node 1's absence of an opposing force only bounds tangential power
-- below by zero. It does not say power is zero. A forward force is a witness.
theorem nonopposing_force_can_do_work :
    let velocity : Rat := 1
    let tangentialForce : Rat := 1
    0 <= tangentialForce * velocity /\
      tangentialForce * velocity ≠ 0 := by
  dsimp
  grind

-- A point particle at two times, with the same positive mass and kinetic
-- energy, has the same squared speed. hMass uses a nonzero-mass assumption.
theorem point_particle_energy
    (mass speedSqBefore speedSqAfter : Rat)
    (hMass : mass ≠ 0)
    (hEnergy : mass * speedSqBefore = mass * speedSqAfter) :
    speedSqBefore = speedSqAfter := by
  grind

-- Twice total kinetic energy in a reduced rigid-body model is
-- (mass + rotationalInertia / radius^2) * squaredCenterSpeed.
-- Concrete endpoint witness: mass=I=1, radii 2 and 1, squared speeds 1 and 5/8.
-- This checks the energy accounting, NOT the existence of a train/track motion
-- realizing these endpoints and maintaining all ideal constraint conditions.
theorem rigid_body_endpoint_witness :
    (1 + (1 : Rat) / (2 * 2)) * 1 =
      (1 + (1 : Rat) / (1 * 1)) * (5 / 8) /\
    (5 / 8 : Rat) < 1 := by
  grind

-- BALL: for a circular pole, let u=(ux,uy) be radial and t=(tx,ty) tangent.
-- q = R*u + s*t and s = L-R*theta. Formal differentiation would give
-- qdot = omega * (R*t - R*t - s*u). The cancellation below is checked;
-- deriving this derivative from a real trajectory is NOT included here.
theorem wrapping_ball_zero_power
    (radius freeLength omega tension ux uy tx ty : Rat)
    (hPerp : ux * tx + uy * ty = 0) :
    (-tension * tx) *
      (omega * (radius * tx - radius * tx - freeLength * ux)) +
    (-tension * ty) *
      (omega * (radius * ty - radius * ty - freeLength * uy)) = 0 := by
  grind

-- Force tangent to the pole is not central about its center. Even with zero
-- power above, torque need not vanish. This defeats a casual appeal to
-- conservation of the ball's angular momentum about the pole center.
theorem wrapping_ball_torque
    (radius freeLength tension ux uy tx ty : Rat)
    (hOrientation : ux * ty - uy * tx = 1) :
    (radius * ux + freeLength * tx) * (-tension * ty) -
    (radius * uy + freeLength * ty) * (-tension * tx) =
      -radius * tension := by
  grind

#print axioms iceberg_balance
#print axioms water_inclusion_no_change
#print axioms ideal_air_no_change
#print axioms dense_inclusion_level_drops
#print axioms positive_air_mass_changes_answer
#print axioms iceberg_sign_check
#print axioms nonopposing_force_can_do_work
#print axioms point_particle_energy
#print axioms rigid_body_endpoint_witness
#print axioms wrapping_ball_zero_power
#print axioms wrapping_ball_torque

end ObfuscationFeasibility
