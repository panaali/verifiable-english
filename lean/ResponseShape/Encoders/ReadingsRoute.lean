import ResponseShape.Encoders.Rights
import ResponseShape.Encoders.NormDefaults

/-! The `readings-route` mode (`Readings.Run.runCaseReported`) against `readings-route.json#/row`. A
case of another kind is the lower route's (rights, soft-norms, norm-defaults or norms). -/

namespace ResponseShape.Encoders.ReadingsRoute
open Lean ResponseShape ResponseShape.Skeletons
open VE.Readings VE.Readings.Run

variable {req : Json}

theorem keyJson_fits (k : GenKey) : Fits req (skel% "readings-route.json#/$defs/key") (Wire.keyJson k) := by
  cases k with
  | excepted r b => cases b <;> simp only [Wire.keyJson, Option.toList, List.map_cons, List.map_nil] <;> fits
  | off r b π => cases b <;> simp only [Wire.keyJson, Option.toList, List.map_cons, List.map_nil] <;> fits
  | _ => unfold Wire.keyJson; fits

theorem candidate_fits (a : Wire.Admitted) (R : ReadingSet) (i : Nat) :
    OkFits req (skel% "readings-route.json#/$defs/candidate") (candidateJson a R i) := by
  unfold candidateJson
  okfits
  all_goals (try simp only [keyEntry])
  all_goals fits using keyJson_fits

theorem pair_fits (f : PairFacts) (sid : String) :
    Fits req (skel% "readings-route.json#/$defs/pair") (pairJson f sid) := by
  unfold pairJson optBool
  fits

/-- An element of `setPairs`: a pair of readings and their separating situation's facts. -/
def PairEntry (x : Json) : Prop :=
  ∃ r o f sid, x = Json.mkObj [("reading", .str r), ("other", .str o), ("pair", pairJson f sid)]

theorem setPairs_entries (a : Wire.Admitted) (R : ReadingSet) (RJ : Wire.SetJ) :
    OkP (fun out => ∀ x ∈ out, PairEntry x) (setPairs a R RJ) := by
  unfold setPairs
  simp only [bind_pure]
  refine OkP.forIn (P := fun (out : List Json) => ∀ x ∈ out, PairEntry x) ?_ ?_
  · intro _ h
    cases h
  intro x _ r hr
  apply OkP.bind
  intro r' hr'
  apply OkP.pure
  refine OkP.forIn (P := fun (out : List Json) => ∀ x ∈ out, PairEntry x) hr (fun y _ s hs => ?_) r' hr'
  okfits
  all_goals simp only [ForInStep.value, List.mem_append, List.mem_singleton]
  all_goals first
    | exact hs
    | (intro z hz; rcases hz with hz | rfl
       · exact hs z hz
       · exact ⟨_, _, _, _, rfl⟩)

/-- A row of `validateResult`: one content-bearing set with its candidates and pairs. -/
def SetEntry (req : Json) (x : Json) : Prop :=
  ∃ (s : String) (v : Json) (cands pairs : List Json) (fs : Json), x = Json.mkObj [("set", .str s), ("version", v), ("candidates", Json.arr cands.toArray),
      ("pairs", Json.arr pairs.toArray), ("findings", fs)] ∧
    (∀ c ∈ cands, Fits req (skel% "readings-route.json#/$defs/candidate") c) ∧ (∀ p ∈ pairs, PairEntry p)

theorem validate_fits (id : String) (a : Wire.Admitted) :
    OkP (fun l => Fits req Skeletons.readingsRoute (VE.Route.Wire.ok id l)) (validateResult a) := by
  unfold validateResult
  simp only []
  okfits
  · simp only [VE.Route.Wire.ok]
    fits
  rename_i rows hrows
  have hrows := OkP.forIn (P := fun (out : List Json) => ∀ x ∈ out, SetEntry req x) (fun _ h => by cases h) (fun R _ r hr => by
      okfits
      all_goals simp only [ForInStep.value, List.mem_append, List.mem_singleton]
      all_goals first
        | exact hr
        | (intro z hz
           rcases hz with hz | rfl
           · exact hr z hz
           · exact ⟨_, _, _, _, _, rfl, OkP.mapM (fun i _ => candidate_fits a R i) _ ‹_›,
               setPairs_entries a R _ _ ‹_›⟩)) rows hrows
  simp only [VE.Route.Wire.ok]
  fits
  obtain ⟨s, v, cands, pairs, fs, rfl, hc, hp⟩ := hrows _ ‹_›
  fits
  · exact hc _ ‹_›
  · obtain ⟨r, o, f, sid, rfl⟩ := hp _ ‹_›
    fits using pair_fits

theorem runCase_fits (j : Json) : OkFits req Skeletons.readingsRoute (runCase j) := by
  unfold runCase
  okfits
  · exact validate_fits _ _ _ ‹_›
  · simp only [VE.Route.Wire.ok]
    fits using pair_fits

theorem of_rights {v : Json} (h : Fits req Skeletons.rights v) : Fits req Skeletons.readingsRoute v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem of_softNorms {v : Json} (h : Fits req Skeletons.softNorms v) : Fits req Skeletons.readingsRoute v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem of_normDefaults {v : Json} (h : Fits req Skeletons.normDefaults v) : Fits req Skeletons.readingsRoute v := by
  refine Fits.altSub ?_ h
  alt_sub

theorem of_norms {v : Json} (h : Fits req Skeletons.norms v) : Fits req Skeletons.readingsRoute v := by
  refine Fits.altSub ?_ h
  alt_sub

/-- A row for the case with its environment rewritten is a row for the case: every condition on
the case in the lower modes' skeletons is on its `kind`, which the rewrite keeps. -/
theorem lower {j j' : Json} (hk : j'.getObjValD "kind" = j.getObjValD "kind") {k : Skel} {v : Json}
    (h : Fits j' k v) (hc : Skel.condsOk CaseCond.isKind 1000 k = true) : Fits j k v :=
  Fits.congr (p := CaseCond.isKind) (fun cond hp => by
    cases cond with
    | kind k => simp [CaseCond.holds, hk]
    | path ks => cases hp) h 1000 hc

theorem lower_rights {j j' : Json} (hk : j'.getObjValD "kind" = j.getObjValD "kind") :
    Fits j Skeletons.readingsRoute (VE.Rights.Run.runCaseReported j') :=
  of_rights (lower hk (Rights.runCaseReported_fits j') (by decide))

theorem lower_softNorms {j j' : Json} (hk : j'.getObjValD "kind" = j.getObjValD "kind") :
    Fits j Skeletons.readingsRoute (VE.SoftNorms.Run.runCaseReported j') :=
  of_softNorms (lower hk (SoftNorms.runCaseReported_fits j') (by decide))

theorem lower_normDefaults {j j' : Json} (hk : j'.getObjValD "kind" = j.getObjValD "kind") :
    Fits j Skeletons.readingsRoute (VE.NormDefaults.Run.runCaseReported j') :=
  of_normDefaults (lower hk (NormDefaults.runCaseReported_fits j') (by decide))

theorem lower_norms {j j' : Json} (hk : j'.getObjValD "kind" = j.getObjValD "kind") :
    Fits j Skeletons.readingsRoute (VE.Norms.Run.runCaseReported j') :=
  of_norms (lower hk (Norms.runCaseReported_fits j') (by decide))

theorem runLower_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.readingsRoute (runLower j) := by
  unfold runLower
  repeat' (first | split | simp only [])
  all_goals
    first
      | with_reducible apply lower_rights
      | with_reducible apply lower_softNorms
      | with_reducible apply lower_normDefaults
      | with_reducible apply lower_norms
    first
      | rfl
      | exact kind_setObjVal hj (by decide) _

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.readingsRoute (runCaseReported j) := by
  unfold runCaseReported
  split
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · split
    · exact runCase_fits j _ ‹_›
    · fits
  · exact runLower_fits j hj

end ResponseShape.Encoders.ReadingsRoute
