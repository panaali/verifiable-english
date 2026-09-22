import Std

/-! Package 3b: a direct conditional proof of the original three-tub root.
Physical premises and scope: experiments/obfuscated-arguments/iceberg/SPEC.md.
No Mathlib, no global physical axioms, no assumed height comparison or zero spill.
-/
namespace Iceberg
abbrev Q := Rat

theorem mul_sub (a b c : Q) : a * (b - c) = a * b - a * c := by grind

structure Tub where
  rho : Q
  g : Q
  area : Q
  rim : Q
  baseWater : Q
  initialDisplaced : Q
  iceMass : Q
  inclusionMass : Q
  rho_pos : 0 < rho
  g_pos : 0 < g
  area_pos : 0 < area
  ice_nonneg : 0 ≤ iceMass
  inclusion_nonneg : 0 ≤ inclusionMass
  base_nonneg : 0 ≤ baseWater
  displaced_nonneg : 0 ≤ initialDisplaced
  initial_float : (rho * initialDisplaced) * g = (iceMass + inclusionMass) * g
  initially_brimful : area * rim = baseWater + initialDisplaced

/-- Gross liquid production is measured before subtraction of any prior spill. -/
structure Stage (t : Tub) where
  liquidAdded : Q
  remainingMass : Q
  escapedMass : Q
  immersed : Q
  support : Q
  liquid_nonneg : 0 ≤ liquidAdded
  remaining_nonneg : 0 ≤ remainingMass
  escaped_nonneg : 0 ≤ escapedMass
  immersed_nonneg : 0 ≤ immersed
  support_nonneg : 0 ≤ support
  mass_conservation : t.rho * liquidAdded + remainingMass + escapedMass =
    t.iceMass + t.inclusionMass
  force_balance : (t.rho * immersed) * t.g + support = remainingMass * t.g

def excess (x : Q) : Q := if 0 < x then x else 0

/-- Most recent stage first; the tail is processed before the head. -/
def spilled (t : Tub) : List (Stage t) → Q
  | [] => 0
  | s :: earlier =>
    let previous := spilled t earlier
    previous + excess (t.baseWater + s.liquidAdded + s.immersed -
      previous - t.area * t.rim)

structure Process (t : Tub) where
  history : List (Stage t)
  finalStage : Stage t
  meltVolume : Q
  finalInclusionVolume : Q
  finalHeight : Q
  melt_nonneg : 0 ≤ meltVolume
  inclusion_volume_nonneg : 0 ≤ finalInclusionVolume
  height_nonneg : 0 ≤ finalHeight
  melting : t.rho * meltVolume = t.iceMass
  final_contents : finalStage.liquidAdded + finalStage.immersed =
    meltVolume + finalInclusionVolume
  final_geometry : t.area * finalHeight =
    t.baseWater + finalStage.liquidAdded + finalStage.immersed -
      spilled t (finalStage :: history)

theorem initial_mass_balance (t : Tub) :
    t.rho * t.initialDisplaced = t.iceMass + t.inclusionMass := by
  have h := t.initial_float
  exact Rat.le_antisymm
    (Rat.le_of_mul_le_mul_right (by grind) t.g_pos)
    (Rat.le_of_mul_le_mul_right (by grind) t.g_pos)

/-- Derived from forces and conservation, not an assumed no-overflow bound. -/
theorem stage_within_capacity (t : Tub) (s : Stage t) :
    t.baseWater + s.liquidAdded + s.immersed ≤ t.area * t.rim := by
  have hforce := s.force_balance
  have hsupport := s.support_nonneg
  have hweight : t.rho * s.immersed ≤ s.remainingMass :=
    Rat.le_of_mul_le_mul_right (by grind) t.g_pos
  have hmass := s.mass_conservation
  have hescape := s.escaped_nonneg
  have hinitial := initial_mass_balance t
  have hvol : s.liquidAdded + s.immersed ≤ t.initialDisplaced := by
    apply Rat.le_of_mul_le_mul_left (c := t.rho) _ t.rho_pos
    rw [Rat.mul_add]
    grind
  have := t.initially_brimful
  grind

theorem no_spill (t : Tub) (history : List (Stage t)) : spilled t history = 0 := by
  induction history with
  | nil => rfl
  | cons s earlier ih =>
    have h := stage_within_capacity t s
    simp only [spilled, ih, excess]
    split <;> grind

theorem height_balance (t : Tub) (p : Process t) :
    t.rho * t.area * (p.finalHeight - t.rim) =
      t.rho * p.finalInclusionVolume - t.inclusionMass := by
  have := initial_mass_balance t
  have := t.initially_brimful
  have := p.melting
  have := p.final_contents
  have h := p.final_geometry
  rw [no_spill] at h
  grind

theorem water_unchanged (t : Tub) (p : Process t)
    (water : t.rho * p.finalInclusionVolume = t.inclusionMass) :
    p.finalHeight = t.rim := by
  have h := height_balance t p
  have hp := Rat.mul_pos t.rho_pos t.area_pos
  have heq : (t.rho * t.area) * p.finalHeight = (t.rho * t.area) * t.rim := by
    grind
  exact Rat.le_antisymm
    (Rat.le_of_mul_le_mul_left (by grind) hp)
    (Rat.le_of_mul_le_mul_left (by grind) hp)

def Within (before after epsilon : Q) : Prop :=
  before - epsilon ≤ after ∧ after ≤ before + epsilon

theorem air_approximately_unchanged (t : Tub) (p : Process t) (epsilon : Q)
    (air : p.finalInclusionVolume = 0) (epsilon_nonneg : 0 ≤ epsilon)
    (small_mass : t.inclusionMass ≤ t.rho * t.area * epsilon) :
    Within t.rim p.finalHeight epsilon ∧ p.finalHeight ≤ t.rim := by
  have h := height_balance t p
  rw [air, Rat.mul_zero, mul_sub] at h
  have hp := Rat.mul_pos t.rho_pos t.area_pos
  have hm := t.inclusion_nonneg
  have hlo : t.rim - epsilon ≤ p.finalHeight := by
    apply Rat.le_of_mul_le_mul_left (c := t.rho * t.area) _ hp
    rw [mul_sub]
    grind
  have hhi : p.finalHeight ≤ t.rim :=
    Rat.le_of_mul_le_mul_left (by grind) hp
  unfold Within
  grind

theorem positive_air_strictly_lowers (t : Tub) (p : Process t)
    (air : p.finalInclusionVolume = 0) (positive_mass : 0 < t.inclusionMass) :
    p.finalHeight < t.rim := by
  have h := height_balance t p
  rw [air, Rat.mul_zero, mul_sub] at h
  exact Rat.lt_of_mul_lt_mul_left (by grind)
    (Rat.le_of_lt (Rat.mul_pos t.rho_pos t.area_pos))

theorem metal_lowers (t : Tub) (p : Process t) (metalDensity : Q)
    (dense : t.rho < metalDensity) (volume_pos : 0 < p.finalInclusionVolume)
    (material : metalDensity * p.finalInclusionVolume = t.inclusionMass) :
    p.finalHeight < t.rim := by
  have h := height_balance t p
  rw [mul_sub] at h
  have hd := Rat.mul_lt_mul_of_pos_right dense volume_pos
  exact Rat.lt_of_mul_lt_mul_left (by grind)
    (Rat.le_of_lt (Rat.mul_pos t.rho_pos t.area_pos))

/-- The root answer for three independently parameterised tubs, including spill. -/
theorem iceberg_root (w a m : Tub) (pw : Process w) (pa : Process a) (pm : Process m)
    (epsilon metalDensity : Q)
    (water : w.rho * pw.finalInclusionVolume = w.inclusionMass)
    (air : pa.finalInclusionVolume = 0) (epsilon_nonneg : 0 ≤ epsilon)
    (small_air_mass : a.inclusionMass ≤ a.rho * a.area * epsilon)
    (dense : m.rho < metalDensity) (metal_volume_pos : 0 < pm.finalInclusionVolume)
    (metal : metalDensity * pm.finalInclusionVolume = m.inclusionMass) :
    pw.finalHeight = w.rim ∧
    Within a.rim pa.finalHeight epsilon ∧ pa.finalHeight ≤ a.rim ∧
    pm.finalHeight < m.rim ∧
    spilled w (pw.finalStage :: pw.history) = 0 ∧
    spilled a (pa.finalStage :: pa.history) = 0 ∧
    spilled m (pm.finalStage :: pm.history) = 0 := by
  have ha := air_approximately_unchanged a pa epsilon air epsilon_nonneg small_air_mass
  exact ⟨water_unchanged w pw water, ha.1, ha.2,
    metal_lowers m pm metalDensity dense metal_volume_pos metal,
    no_spill w _, no_spill a _, no_spill m _⟩

def oneMillimetre : Q := 1 / 1000

theorem air_one_millimetre (t : Tub) (p : Process t)
    (air : p.finalInclusionVolume = 0)
    (small_mass : t.inclusionMass ≤ t.rho * t.area * oneMillimetre) :
    Within t.rim p.finalHeight oneMillimetre := by
  exact (air_approximately_unchanged t p oneMillimetre air (by unfold oneMillimetre; grind) small_mass).1

/-- Sensitivity only: the bound on the physical residual is an extra premise.
For example a residual may account for air buoyancy and extra water loss.
It is not asserted to be small merely because its name is `residual`. -/
theorem residual_height_bound (rho area before after volume mass residual epsilon : Q)
    (rho_pos : 0 < rho) (area_pos : 0 < area)
    (balance : rho * area * (after - before) = rho * volume - mass + residual)
    (lower : -(rho * area * epsilon) ≤ rho * volume - mass + residual)
    (upper : rho * volume - mass + residual ≤ rho * area * epsilon) :
    Within before after epsilon := by
  have hp := Rat.mul_pos rho_pos area_pos
  rw [mul_sub] at balance
  constructor
  · apply Rat.le_of_mul_le_mul_left (c := rho * area) _ hp
    rw [mul_sub]
    grind
  · apply Rat.le_of_mul_le_mul_left (c := rho * area) _ hp
    rw [Rat.mul_add]
    grind

/-- Rational non-vacuity witnesses in units with water density, area and g = 1.
Nine units of ice; enough finite ice volume is consistent with flotation. -/
def sampleTub (c : Q) (hc : 0 ≤ c) (hc2 : c ≤ 2) : Tub := by
  refine {
    rho := 1, g := 1, area := 1, rim := 100, baseWater := 91 - c,
    initialDisplaced := 9 + c, iceMass := 9, inclusionMass := c,
    rho_pos := ?_, g_pos := ?_, area_pos := ?_, ice_nonneg := ?_,
    inclusion_nonneg := hc, base_nonneg := ?_, displaced_nonneg := ?_,
    initial_float := ?_, initially_brimful := ?_ }
  all_goals grind

def waterTub : Tub := sampleTub (1) (by grind) (by grind)

def waterProcess : Process waterTub := by
  refine {
    history := [],
    finalStage := {
      liquidAdded := 10, remainingMass := 0, escapedMass := 0,
      immersed := 0, support := 0,
      liquid_nonneg := ?_, remaining_nonneg := ?_, escaped_nonneg := ?_,
      immersed_nonneg := ?_, support_nonneg := ?_,
      mass_conservation := ?_, force_balance := ?_ },
    meltVolume := 9, finalInclusionVolume := 1, finalHeight := 100,
    melt_nonneg := ?_, inclusion_volume_nonneg := ?_, height_nonneg := ?_,
    melting := ?_, final_contents := ?_, final_geometry := ?_ }
  all_goals try dsimp [waterTub, sampleTub, spilled, excess]
  all_goals grind

def airTub : Tub := sampleTub (1 / 10000) (by grind) (by grind)

def airProcess : Process airTub := by
  refine {
    history := [],
    finalStage := {
      liquidAdded := 9, remainingMass := 0, escapedMass := 1 / 10000,
      immersed := 0, support := 0,
      liquid_nonneg := ?_, remaining_nonneg := ?_, escaped_nonneg := ?_,
      immersed_nonneg := ?_, support_nonneg := ?_,
      mass_conservation := ?_, force_balance := ?_ },
    meltVolume := 9, finalInclusionVolume := 0, finalHeight := 100 - 1 / 10000,
    melt_nonneg := ?_, inclusion_volume_nonneg := ?_, height_nonneg := ?_,
    melting := ?_, final_contents := ?_, final_geometry := ?_ }
  all_goals try dsimp [airTub, sampleTub, spilled, excess]
  all_goals grind

def metalTub : Tub := sampleTub (2) (by grind) (by grind)

def metalProcess : Process metalTub := by
  refine {
    history := [],
    finalStage := {
      liquidAdded := 9, remainingMass := 2, escapedMass := 0,
      immersed := 1 / 4, support := 7 / 4,
      liquid_nonneg := ?_, remaining_nonneg := ?_, escaped_nonneg := ?_,
      immersed_nonneg := ?_, support_nonneg := ?_,
      mass_conservation := ?_, force_balance := ?_ },
    meltVolume := 9, finalInclusionVolume := 1 / 4, finalHeight := 100 - 7 / 4,
    melt_nonneg := ?_, inclusion_volume_nonneg := ?_, height_nonneg := ?_,
    melting := ?_, final_contents := ?_, final_geometry := ?_ }
  all_goals try dsimp [metalTub, sampleTub, spilled, excess]
  all_goals grind

/-- The root premises coexist, including strictly positive (not massless) air. -/
theorem root_witness :
    waterProcess.finalHeight = waterTub.rim ∧
    Within airTub.rim airProcess.finalHeight oneMillimetre ∧
    airProcess.finalHeight ≤ airTub.rim ∧
    metalProcess.finalHeight < metalTub.rim ∧
    spilled waterTub (waterProcess.finalStage :: waterProcess.history) = 0 ∧
    spilled airTub (airProcess.finalStage :: airProcess.history) = 0 ∧
    spilled metalTub (metalProcess.finalStage :: metalProcess.history) = 0 := by
  apply iceberg_root waterTub airTub metalTub waterProcess airProcess metalProcess
    oneMillimetre 8
  all_goals try dsimp [waterProcess, airProcess, metalProcess, waterTub, airTub,
    metalTub, sampleTub, oneMillimetre]
  all_goals grind

#print axioms mul_sub
#print axioms root_witness
#print axioms initial_mass_balance
#print axioms stage_within_capacity
#print axioms no_spill
#print axioms height_balance
#print axioms water_unchanged
#print axioms air_approximately_unchanged
#print axioms positive_air_strictly_lowers
#print axioms metal_lowers
#print axioms iceberg_root
#print axioms air_one_millimetre
#print axioms residual_height_bound
end Iceberg
