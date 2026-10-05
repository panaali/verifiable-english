import ResponseShape.Encoders.Common

/-! The service's own lines against `envelope.json`: each result bound to its position and case
digest (`Service.Protocol.bound`), the response (`response`) and a request error
(`requestError`). The rows inside are the modes' (`ResponseShape.Encoders.runMode_fits`). -/

namespace ResponseShape.Encoders.Envelope
open Lean ResponseShape ResponseShape.Skeletons
open VE.Service

variable {req : Json}

/-- A value whose field `k` is the string `s` is an object holding it. -/
theorem getObjValD_str {j : Json} {k s : String} (h : j.getObjValD k = .str s) :
    ∃ m : Std.TreeMap.Raw String Json, j = .obj m ∧ m.get? k = some (.str s) := by
  cases j with
  | obj m =>
    refine ⟨m, rfl, ?_⟩
    simp only [Json.getObjValD, Json.getObjVal?] at h
    split at h
    · rename_i v hv
      simp only [Except.toOption, Option.getD] at h
      exact hv.trans (congrArg some h)
    · cases h
  | _ => simp [Json.getObjValD, Json.getObjVal?, Except.toOption] at h

theorem bound_fits (index : Nat) (digest : String) (result : Json) :
    Fits req (skel% "envelope.json#/$defs/bound") (bound index digest result) := by
  unfold bound coding codeMembers
  split
  · rename_i m hs he
    obtain ⟨o, rfl, hso⟩ := getObjValD_str hs
    obtain ⟨o', ho, heo⟩ := getObjValD_str he
    cases ho
    have hr : Fits req (.obj [("status", .strIn ["error"]), ("error", .any)] (some .any) ["status", "error"] [])
        (Json.obj o) := by
      refine Fits.obj (fun k v h => ?_) (fun k hk => ?_) (fun _ h => by cases h)
      · by_cases hk : k = "status"
        · subst hk
          have : v = .str "error" := Option.some.inj (h.symm.trans hso)
          subst this
          exact Fits.strIn (by simp)
        · have h1 : (k == "status") = false := by simpa using hk
          have hf : Skel.field [("status", .strIn ["error"]), ("error", .any)] (some .any) k = .any := by
            simp only [Skel.field, List.lookup, h1]
            cases k == "error" <;> rfl
          rw [hf]
          exact Fits.any _
      · simp only [List.mem_cons, List.not_mem_nil, or_false] at hk
        rcases hk with rfl | rfl
        · exact Option.isSome_iff_exists.mpr ⟨_, hso⟩
        · exact Option.isSome_iff_exists.mpr ⟨_, heo⟩
    split <;> fits using hr
  · fits

theorem response_fits (r : Request) (cases : Array (Except String Json)) (digests : Array String) :
    Fits req (skel% "envelope.json#/$defs/ok") (response r cases digests) := by
  unfold response bindResults
  simp only []
  fits
  refine Fits.arrOf fun x hx => ?_
  obtain ⟨i, hi, rfl⟩ := Array.mem_mapIdx.mp hx
  exact bound_fits _ _ _

theorem requestError_fits (r : Request) (message : String) :
    Fits req (skel% "envelope.json#/$defs/error") (requestError r message) := by
  unfold requestError
  fits

end ResponseShape.Encoders.Envelope
