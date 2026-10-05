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

/-- An object holding the field `f` with a value fitting `s`, any other field allowed. -/
theorem one_field {m : Std.TreeMap.Raw String Json compare} {f : String} {s : Skel} {w : Json}
    (hf : m.get? f = some w) (hs : Fits req s w) : Fits req (.obj [(f, s)] (some .any) [f] []) (.obj m) := by
  refine Fits.obj (fun k v h => ?_) (fun k hk => ?_) (fun _ h => by cases h)
  · by_cases hk : k = f
    · subst hk
      have : v = w := Option.some.inj (h.symm.trans hf)
      subst this
      simpa [Skel.field, List.lookup] using hs
    · have h1 : (k == f) = false := by simpa using hk
      simp only [Skel.field, List.lookup, h1, Option.getD]
      exact Fits.any _
  · simp only [List.mem_cons, List.not_mem_nil, or_false] at hk
    subst hk
    exact Option.isSome_iff_exists.mpr ⟨_, hf⟩

/-- An object lacking the field `f`, any other field allowed. -/
theorem lacks {m : Std.TreeMap.Raw String Json compare} {f : String} (hf : m.get? f = none) :
    Fits req (.obj [] (some .any) [] [f]) (.obj m) := by
  refine Fits.obj (fun k v _ => ?_) (fun _ h => by cases h) (fun k hk => ?_)
  · exact Fits.any _
  · simp only [List.mem_cons, List.not_mem_nil, or_false] at hk
    subst hk
    exact hf

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
  · -- Not a rejection: the result is not an object, lacks status or error, or has another status
    -- or an error that is not a string (one `else` branch each).
    rename_i hne
    simp only [List.append_nil]
    cases result with
    | obj m =>
      have hD : ∀ k, (Json.obj m).getObjValD k = (m.get? k).getD .null := fun k => by
        simp only [Json.getObjValD, Json.getObjVal?]
        cases m.get? k <;> rfl
      cases hs : m.get? "status" with
      | none =>
        refine Fits.ofAlt (List.mem_of_getElem? (i := 2) rfl) ?_
        fits using lacks hs
      | some sv =>
        by_cases hsv : sv = .str "error"
        · subst hsv
          cases he : m.get? "error" with
          | none =>
            refine Fits.ofAlt (List.mem_of_getElem? (i := 3) rfl) ?_
            fits using lacks he
          | some ev =>
            cases ev with
            | str message => exact (hne message (by rw [hD, hs]; rfl) (by rw [hD, he]; rfl)).elim
            | _ =>
              refine Fits.ofAlt (List.mem_of_getElem? (i := 5) rfl) ?_
              fits using one_field he (Fits.kindNot (by simp only [kind]; first | decide | (split <;> decide)))
        · refine Fits.ofAlt (List.mem_of_getElem? (i := 4) rfl) ?_
          fits using one_field hs (Fits.strNotIn (fun t ht => by subst ht; simpa using hsv))
    | _ =>
      refine Fits.ofAlt (List.mem_of_getElem? (i := 1) rfl) ?_
      fits using Fits.kindNot (by simp only [kind]; first | decide | (split <;> decide))

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
