import VE.Readings.Unspecified
import VE.NormDefaults.LayeredEntail

/-! Documents and extra base premises for readings on the soft completion. -/
namespace VE.Readings
open VE.Norms (envAt)
open VE.SoftNorms (SoftNode SoftDoc soften)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)
universe u

def contentSoft : Content → Bool
  | .assertion _ => true
  | .norm _ => true
  | _ => false

def softShaped (D : Doc) : Bool :=
  D.chain == .soft && D.frame.soft.T.nodes.isEmpty && noRights D.frame &&
  D.items.all (fun it => match it with
    | .fixed _ c _ => contentSoft c
    | .bar _ _ => false
    | .set R => R.candidates.all (fun a => (a.content.map contentSoft).getD true))

def softXL (N : NDoc) (X : RightsDoc) : List (String × VE.Formula) :=
  VE.NormDefaults.Wire.softLabelledU (asU N X) (correlate X)
def softX (N : NDoc) (X : RightsDoc) : List VE.Formula := (softXL N X).map (·.2)
def freeX (N : NDoc) : List VE.Formula := softX N (free N.D).1
def oneX (N : NDoc) (s : String) (i : Nat) : List VE.Formula := softX N (one N.D s i).1
def choiceX (N : NDoc) (c : Choice) : List VE.Formula := softX N (choiceDoc N.D c).1

theorem softX_strict (N : NDoc) (X : RightsDoc) (hr : noRights X = true) (hs : allStrict X = true) :
    softX N X = [] := by
  have hh : StrictNodes X.soft := by
    intro M hM
    simp only [allStrict, List.all_eq_true, Bool.and_eq_true, beq_iff_eq, List.isEmpty_iff] at hs
    exact hs M hM
  have hc := correlate_noRights X hr
  have hp := softPremises_strict X.soft hh
  change VE.SoftNorms.excPremises X.soft ++ VE.SoftNorms.cohPremises X.soft = [] at hp
  obtain ⟨he, hcoh⟩ := List.append_eq_nil_iff.mp hp
  have hcp : VE.SoftNorms.collidingPairs X.soft = [] := by
    simpa only [VE.SoftNorms.cohPremises, List.map_eq_nil_iff] using hcoh
  simp only [softX, softXL, VE.NormDefaults.Wire.softLabelledU, hc.1, hcp, List.map_nil,
    List.append_nil, List.map_eq_nil_iff]
  simp [he]

theorem choiceX_normsShaped (N : NDoc) (hn : normsShaped N.D = true) (c : Choice) :
    choiceX N c = [] := by
  have hs : StrictDoc (choiceDoc N.D c).1 :=
    build_strict N.D (shaped hn) _ _ (fun R a h => by
      cases hi : c.index R.id with
      | none => rw [hi] at h; cases h
      | some i => rw [hi] at h; exact List.mem_of_getElem? h)
  exact softX_strict N _ hs.1 (by
    simp only [allStrict, List.all_eq_true, Bool.and_eq_true, beq_iff_eq, List.isEmpty_iff]
    intro M hM
    exact hs.2 M hM)

def filledAuthorEnv (N : NDoc) : VE.Environment :=
  envAt { N.D.frame.soft with E := fillFrameEnv N }.base 0

theorem filledAuthorEnv_eq (N : NDoc) : filledAuthorEnv N = authorEnv (fillDoc N) := by
  rfl

def WellFormedSD (N : NDoc) : Bool :=
  WellFormedDoc N.D && softShaped N.D && fillNamesFree N && VE.NormDefaults.WellFormedU (freeU N) &&
  N.D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || VE.NormDefaults.WellFormedU (oneU N R.id i)))
end VE.Readings
