import VE.SoftNorms.Run

/-! The wire theorem of the soft route's `soft-elaborate` kind (kernel boundary).

The soft route's acceptance theorems are about the lists `background' D` and
`elaborate (soften D).T`. This file states that the `background` and `premises` fields of a
`soft-elaborate` answer, read by key as a client reads them, hold entry for entry and in order the
encodings (`enc`) of exactly those two lists for the document the case's own decoder reads.

It says nothing about the other fields (in particular `colliding_pairs`, `derived` and
`soft_status`), nor about what a harness carries from this answer to a later certificate case: the
Python client takes the coherence premises from `colliding_pairs` and only the labels from
`premises`, and the norms route accepts `soft_premises` as the case carries them. -/
namespace VE.SoftNorms.Run
open Lean
open VE.Norms
open VE.SoftNorms.Wire
open VE.Order.ProfileGate (bind_ok)

/-- A rule's exception labels and its exception premises are equally many. -/
theorem excLabels_length (D : SoftDoc) : (excLabels D).length = (excPremises D).length := by
  unfold excLabels excPremises
  induction D.T.nodes with
  | nil => rfl
  | cons N Ns ih =>
    simp only [List.flatMap_cons, List.length_append, ih]
    congr 1
    unfold excPremisesOf
    cases N.mode <;> cases N.exception <;> simp

/-- The labelled soft premises are the soft premises, in order. -/
theorem softLabelled_formulas (D : SoftDoc) : (softLabelled D).map (·.2) = softPremises D := by
  unfold softLabelled softPremises cohPremises
  rw [List.map_append, List.map_map]
  congr 1
  exact List.map_snd_zip (Nat.le_of_eq (excLabels_length D).symm)

/-- The `background` field of an elaboration: one `bgEntry` per formula of `background' D`, in
order, each with its generator and label. -/
def BackgroundField (D : SoftDoc) (field : Json) : Prop :=
  ∃ entries : List (String × String × VE.Formula),
    field = Json.arr (entries.map fun e => bgEntry e.1 e.2.1 e.2.2).toArray ∧
    entries.map (·.2.2) = background' D

/-- The `premises` field of an elaboration: one labelled encoding per layer premise of
`elaborate (soften D).T`, in order. -/
def PremisesField (D : SoftDoc) (field : Json) : Prop :=
  ∃ entries : List (String × VE.Formula),
    field = Json.arr (entries.map fun e => Json.mkObj [("label", .str e.1), ("ast", enc e.2)]).toArray ∧
    entries.map (·.2) = elaborate (soften D).T

/-- `Json.mkObj` keeps the last value of a repeated key, so a key is read from the head of the list
only when the tail does not bind it again. A wire statement that leaves a tail open must say so
(`ElaborationAnswer` reads every field it states by key). -/
theorem mkObj_get_append {pre rest : List (String × Json)} {k : String} {v : Json}
    (hd : (pre.map (·.1)).Nodup) (hm : (k, v) ∈ pre) (hr : k ∉ rest.map (·.1)) :
    (Json.mkObj (pre ++ rest)).getObjVal? k = .ok v := by
  have hp : pre.Pairwise (fun a b => ¬ compare a.1 b.1 = .eq) :=
    (List.pairwise_map.mp hd).imp (fun hne heq => hne (Std.LawfulEqOrd.eq_of_compare heq))
  have hpre := Std.TreeMap.Raw.getElem?_ofList_of_mem (cmp := compare) (k := k) (k' := k)
    Std.ReflCmp.compare_self hp hm
  have hc : (rest.map (·.1)).contains k = false := by simpa using hr
  have hrest := Std.TreeMap.Raw.getElem?_insertMany_list_of_contains_eq_false
    (Std.TreeMap.Raw.WF.ofList (cmp := compare) (l := pre)) hc
  simp only [Json.mkObj, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?,
    Std.TreeMap.Raw.ofList_eq_insertMany_empty, Std.TreeMap.Raw.insertMany_append] at hpre hrest ⊢
  rw [hrest, hpre]
  rfl

/-- What a `soft-elaborate` answer is for the document `D`, read as a client reads it, by key:
status `ok` under the case's id, and `background` and `premises` fields that are the two fields
above. Every other field is open. -/
def ElaborationAnswer (id : String) (D : SoftDoc) (answer : Json) : Prop :=
  answer.getObjVal? "id" = .ok (.str id) ∧ answer.getObjVal? "status" = .ok (.str "ok") ∧
  (∃ background, answer.getObjVal? "background" = .ok background ∧ BackgroundField D background) ∧
  (∃ premises, answer.getObjVal? "premises" = .ok premises ∧ PremisesField D premises)

/-- What a client reads from an elaboration answer, field by field. -/
theorem elaborationAnswer_reads {id : String} {D : SoftDoc} {answer : Json} (h : ElaborationAnswer id D answer) :
    answer.getObjValD "id" = .str id ∧ answer.getObjValD "status" = .str "ok" ∧
    BackgroundField D (answer.getObjValD "background") ∧ PremisesField D (answer.getObjValD "premises") := by
  obtain ⟨hi, hs, ⟨b, hb, hB⟩, ⟨q, hq, hQ⟩⟩ := h
  have get : ∀ {k : String} {v : Json}, answer.getObjVal? k = .ok v → answer.getObjValD k = v := by
    intro k v hv; simp only [Json.getObjValD, hv]; rfl
  exact ⟨get hi, get hs, (get hb).symm ▸ hB, (get hq).symm ▸ hQ⟩

/-- No tail overrides a stated field: an answer whose `background` reads `null` (for example
`Wire.ok id (six ++ [("background", Json.null)])`) is not an elaboration answer. -/
theorem not_elaborationAnswer_of_null_background (id : String) (D : SoftDoc) (answer : Json)
    (h : answer.getObjValD "background" = Json.null) : ¬ ElaborationAnswer id D answer := by
  intro ha
  obtain ⟨_, _, ⟨_, he, _⟩, _⟩ := elaborationAnswer_reads ha
  rw [h] at he
  cases he

/-- A `Wire.ok` answer whose first six fields carry the two fields above, and whose tail binds none
of the four keys `ElaborationAnswer` reads, is an elaboration answer. -/
theorem elaborationAnswer_ok (id : String) (D : SoftDoc)
    (prime decisions derived order background premises : Json) (tail : List (String × Json))
    (ht : ∀ k ∈ ["id", "status", "background", "premises"], k ∉ tail.map (·.1))
    (hb : BackgroundField D background) (hp : PremisesField D premises) :
    ElaborationAnswer id D (VE.Route.Wire.ok id ([("environment_prime", prime), ("decisions", decisions),
      ("derived", derived), ("order", order), ("background", background), ("premises", premises)] ++ tail)) := by
  unfold VE.Route.Wire.ok
  rw [← List.append_assoc]
  have hd : (([("id", Json.str id), ("status", Json.str "ok")] ++ [("environment_prime", prime),
      ("decisions", decisions), ("derived", derived), ("order", order), ("background", background),
      ("premises", premises)]).map (·.1)).Nodup := by simp
  exact ⟨mkObj_get_append hd (by simp) (ht _ (by simp)), mkObj_get_append hd (by simp) (ht _ (by simp)),
    ⟨_, mkObj_get_append hd (by simp) (ht _ (by simp)), hb⟩, ⟨_, mkObj_get_append hd (by simp) (ht _ (by simp)), hp⟩⟩

theorem regeneratedCore_fields (D : SoftDoc) (environment : Json) :
    ∃ (prime decisions derived order background premises : Json) (rest : List (String × Json)),
      regeneratedCore D environment = [("environment_prime", prime), ("decisions", decisions),
        ("derived", derived), ("order", order), ("background", background), ("premises", premises)] ++ rest ∧
      rest.map (·.1) = ["colliding_pairs", "conflict_targets", "conditional_on", "fragment", "warnings"] ∧
      BackgroundField D background ∧ PremisesField D premises := by
  refine ⟨_, _, _, _, _, _, _, rfl, rfl, ?_, ?_⟩
  · refine ⟨(definitionPremises (soften D).T).map (fun a => ("definitions", "", a)) ++
        (backgroundBase (soften D)).map (fun a => ("literals", "", a)) ++
        (pairPremises (soften D).T).map (fun a => ("profile", "", a)) ++
        (softLabelledIn D (soften D) (layersOf (soften D))).map (fun x => ("soft", x.1, x.2)), ?_, ?_⟩
    · simp only [List.map_append, List.map_map]
      rfl
    · simp only [List.map_append, List.map_map]
      rw [show (softLabelledIn D (soften D) (layersOf (soften D))).map
          ((fun e : String × String × VE.Formula => e.2.2) ∘ fun x => ("soft", x.1, x.2)) =
          softPremises D from by rw [softLabelledIn_eq]; exact softLabelled_formulas D]
      simp [background', VE.Norms.background, Function.comp_def]
  · refine ⟨(syms (soften D).T).filterMap (fun
        | .reg r => some ("layer:norms:" ++ r.name, elabPremise (soften D).T r)
        | .defn _ => none), ?_, ?_⟩
    · rw [List.map_filterMap]
      congr 2
      exact congrArg (fun f => List.filterMap f (syms (soften D).T)) (funext fun s => by cases s <;> rfl)
    · rw [List.map_filterMap]
      unfold elaborate
      exact congrArg (fun f => List.filterMap f (syms (soften D).T)) (funext fun s => by cases s <;> rfl)

/-- The soft route's answer to a `soft-elaborate` case: the case's own decoder reads the
document, and the answer, read by key, has status `ok` under the case's id and `background` and
`premises` fields that are the encodings of `background' D` and `elaborate (soften D).T`. No later
field of the answer overrides these (`elaborationAnswer_ok`'s tail condition). -/
theorem soft_wire_elaborate (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "soft-elaborate") (hn : usesSoftPath j = true) :
    ∃ (id : String) (environment : Json) (src : SoftSource),
      VE.Bridge.stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok environment ∧
      decodeSoftSource environment (j.getObjValD "norms") = .ok src ∧
      ElaborationAnswer id src.D answer := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "soft-elaborate" := by rw [hkind] at hk; cases hk; rfl
  subst heq
  simp only [hn, show ("soft-elaborate" == "admission") = false from by decide, Bool.false_and,
    Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
  unfold runSoftKind at h
  simp only [show ("soft-elaborate" == "soft-rule") = false from by decide,
    show ("soft-elaborate" == "soft-rules") = false from by decide,
    show ("soft-elaborate" == "soft-elaborate") = true from by decide,
    Bool.false_eq_true, ↓reduceIte] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨environment, henv, h⟩ := bind_ok h
  obtain ⟨src, hsrc, h⟩ := bind_ok h
  obtain ⟨⟨identityEnvironment, identityProfiles⟩, _, h⟩ := bind_ok h
  obtain ⟨documentHash, _, h⟩ := bind_ok h
  obtain ⟨extra, _, h⟩ := bind_ok h
  cases h
  obtain ⟨prime, decisions, derived, order, background, premises, rest, hcore, hkeys, hb, hp⟩ :=
    regeneratedCore_fields src.D identityEnvironment
  refine ⟨id, environment, src, hid, henv, hsrc, ?_⟩
  dsimp only [regenerated]
  rw [hcore]
  simp only [List.append_assoc]
  refine elaborationAnswer_ok id src.D prime decisions derived order background premises _ ?_ hb hp
  intro k hk
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hk
  rcases hk with rfl | rfl | rfl | rfl <;>
    simp [List.map_append, hkeys, Function.comp_def]

end VE.SoftNorms.Run
