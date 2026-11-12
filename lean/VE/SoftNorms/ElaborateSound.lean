import VE.SoftNorms.Run

/-! The wire theorem of the soft route's `soft-elaborate` kind (kernel boundary).

A harness asks `soft-elaborate` for a soft-norms document's premises and then has the route
replay a certificate over them. The soft route's acceptance theorems are about the lists
`background' D` and `elaborate (soften D).T`. This file ties the two: the `background` and
`premises` fields of a `soft-elaborate` answer hold, entry for entry and in order, the encodings
(`enc`) of exactly those two lists for the document the case's own decoder reads. -/
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

/-- What a `soft-elaborate` answer is for the document `D`: status `ok` under the case's id, and
its first six fields in order, of which `background` and `premises` are the two fields above. -/
def ElaborationAnswer (id : String) (D : SoftDoc) (answer : Json) : Prop :=
  ∃ (prime decisions derived order background premises : Json) (rest : List (String × Json)),
    answer = VE.Route.Wire.ok id ([("environment_prime", prime), ("decisions", decisions),
      ("derived", derived), ("order", order), ("background", background), ("premises", premises)] ++ rest) ∧
    BackgroundField D background ∧ PremisesField D premises

theorem regeneratedCore_fields (D : SoftDoc) (environment : Json) :
    ∃ (prime decisions derived order background premises : Json) (rest : List (String × Json)),
      regeneratedCore D environment = [("environment_prime", prime), ("decisions", decisions),
        ("derived", derived), ("order", order), ("background", background), ("premises", premises)] ++ rest ∧
      BackgroundField D background ∧ PremisesField D premises := by
  refine ⟨_, _, _, _, _, _, _, rfl, ?_, ?_⟩
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
document, and the answer's `background` and `premises` fields are the encodings of
`background' D` and `elaborate (soften D).T`. -/
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
  obtain ⟨prime, decisions, derived, order, background, premises, rest, hcore, hb, hp⟩ :=
    regeneratedCore_fields src.D identityEnvironment
  refine ⟨id, environment, src, hid, henv, hsrc, prime, decisions, derived, order, background, premises,
    rest ++ ?t, ?h, hb, hp⟩
  case h =>
    dsimp only [regenerated]
    rw [hcore, List.append_assoc, List.append_assoc, List.append_assoc, List.append_assoc]

end VE.SoftNorms.Run
