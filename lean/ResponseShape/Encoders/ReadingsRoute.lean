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
    OkFits req (skel% "readings-route.json#/$defs/candidate") (Run.candidateJson a R i) := by
  unfold Run.candidateJson
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
    OkP (fun l => Fits req (skel% "readings-route.json#/$defs/validate") (VE.Route.Wire.ok id l)) (validateResult a) := by
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

/-! The S2a kinds (`runS2`). -/

theorem elaborate_fits (id : String) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/elaborate") (runElaborate id j) := by
  unfold runElaborate
  okfits
  simp only [okWith, VE.Route.Wire.ok, elaborateFields]
  split <;> (try simp only [choicesJson]) <;> (try split) <;>
    simp only [List.cons_append, List.nil_append, List.append_nil, vocabularyJson, slotJson, sizesJson]
  all_goals fits

theorem conflict_fits (id : String) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/conflict") (runConflict id j) := by
  unfold runConflict
  okfits
  all_goals (try simp only [okWith, VE.Route.Wire.ok])
  all_goals fits

theorem certificate_fits (id : String) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/certificate") (runCertificate id j) := by
  unfold runCertificate
  okfits
  simp only [okWith, VE.Route.Wire.ok]
  fits

theorem model_fits (id : String) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/model") (runModel id j) := by
  unfold runModel
  okfits
  all_goals (try simp only [okWith, VE.Route.Wire.ok])
  all_goals fits

theorem dead_fits (id : String) (j : Json) : OkFits req (skel% "readings-route.json#/$defs/dead") (runDead id j) := by
  unfold runDead
  okfits
  all_goals (try simp only [okWith, VE.Route.Wire.ok])
  all_goals fits

theorem choice_fits (lower : List String → Json → Json) (id : String) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/choice_answer") (runChoice lower id j) := by
  unfold runChoice
  okfits
  all_goals (try simp only [okWith, VE.Route.Wire.ok])
  all_goals fits

theorem runS2_fits (lower : List String → Json → Json) (id kind : String) (j : Json)
    (hK : KindRead "evaluate" req kind) : OkFits req Skeletons.readingsRoute (runS2 lower id kind j) := by
  unfold runS2
  rcases hK with hK | ⟨hK, hd⟩
  all_goals (try subst hd)
  all_goals okfits
  all_goals kind_norm
  all_goals first
    | (intro v hv; fits_from elaborate_fits _ _ v hv)
    | (intro v hv; fits_from conflict_fits _ _ v hv)
    | (intro v hv; fits_from certificate_fits _ _ v hv)
    | (intro v hv; fits_from model_fits _ _ v hv)
    | (intro v hv; fits_from dead_fits _ _ v hv)
    | (intro v hv; fits_from choice_fits _ _ _ v hv)

theorem runCase_fits (j : Json) : OkFits j Skeletons.readingsRoute (runCase j) := by
  unfold runCase
  okfits
  all_goals read_kind
  all_goals first
    | fits_from validate_fits _ _ _ ‹_›
    | exact runS2_fits _ _ _ _ (KindRead.of_str ‹_›)
    | exact runS2_fits _ _ _ _ (Or.inr ⟨‹_›, rfl⟩)
    | (simp only [VE.Route.Wire.ok]; fits using pair_fits)

/-! ## The lower routes

A case of another kind is answered by the lower route `Compose.dispatch` names, on the case with
`readings@1` dropped from its environment's profiles (`runLower`). Its row fits for the rewritten
case, and so for the case: every condition on the case in the lower routes' skeletons is on its
kind, on a field other than `environment`, or the lower routes' own tests of the case, which read
no profile but their own (`*_lower`). -/

section Lower

theorem toList_of_mapM {xs : List Json} {l : List String} (h : xs.mapM Json.getStr? = .ok l) : xs = l.map Json.str := by
  induction xs generalizing l with
  | nil => cases h; rfl
  | cons x xs ih =>
    simp only [List.mapM_cons] at h
    cases hx : x.getStr? with
    | error e => rw [hx] at h; cases h
    | ok s =>
      cases hr : xs.mapM Json.getStr? with
      | error e => rw [hx, hr] at h; cases h
      | ok r =>
        rw [hx, hr] at h
        cases h
        rw [ResponseShape.Encoders.Common.str_of_getStr hx, ih hr]
        rfl

theorem strings_arr {P : Json} {l : List String} (h : VE.Bridge.strings P = .ok l) : P = .arr (l.map Json.str).toArray := by
  unfold VE.Bridge.strings at h
  cases P with
  | arr a =>
    simp only [Json.getArr?] at h
    have := toList_of_mapM h
    rw [← this]
  | _ => simp [Json.getArr?] at h <;> cases h

theorem any_filter_map {l : List String} {r : String} (q : Json → Bool) (hq : q (.str r) = false) :
    ((l.filter (· != r)).map Json.str).any q = (l.map Json.str).any q := by
  induction l with
  | nil => rfl
  | cons x xs ih =>
    by_cases hx : x = r
    · subst hx; simp [hq, ih]
    · simp [hx, ih]

theorem toJson_strings (l : List String) : toJson l = Json.arr (l.map Json.str).toArray := by
  show Json.arr (l.toArray.map toJson) = _
  simp [toJson]

/-- Setting a field of a well-formed object map. -/
theorem getObjValD_set_ne {m : Std.TreeMap.Raw String Json compare} (wf : m.WF) {k k' : String} (hk : k ≠ k') (v : Json) :
    (Json.obj m |>.setObjVal! k v).getObjValD k' = (Json.obj m).getObjValD k' := by
  simp only [CaseCond.getObjValD_eq]
  rw [getObjVal_setObjVal (j := .obj m) (fun _ h => by cases h; exact wf) rfl hk]

theorem getObjValD_set_eq {m : Std.TreeMap.Raw String Json compare} (wf : m.WF) (k : String) (v : Json) :
    (Json.obj m |>.setObjVal! k v).getObjValD k = v := by
  simp only [Json.setObjVal!, CaseCond.getObjValD_eq, Json.getObjVal?]
  rw [Std.TreeMap.Raw.get?_eq_getElem?, Std.TreeMap.Raw.getElem?_insert_self wf]
  rfl

theorem getObjVal_set_ne {m : Std.TreeMap.Raw String Json compare} (wf : m.WF) {k k' : String} (hk : k ≠ k') (v : Json) :
    (Json.obj m |>.setObjVal! k v).getObjVal? k' = (Json.obj m).getObjVal? k' :=
  getObjVal_setObjVal (j := .obj m) (fun _ h => by cases h; exact wf) rfl hk v


theorem getObjVal_set_eq {m : Std.TreeMap.Raw String Json compare} (wf : m.WF) (k : String) (v : Json) :
    (Json.obj m |>.setObjVal! k v).getObjVal? k = .ok v := by
  simp only [Json.setObjVal!, Json.getObjVal?]
  rw [Std.TreeMap.Raw.get?_eq_getElem?, Std.TreeMap.Raw.getElem?_insert_self wf]
  rfl

theorem mapM_str (l : List String) : (l.map Json.str).mapM Json.getStr? = .ok l := by
  induction l with
  | nil => rfl
  | cons x xs ih => simp only [List.map_cons, List.mapM_cons, Json.getStr?, ih]; rfl

theorem strings_toJson (l : List String) : VE.Bridge.strings (toJson l) = .ok l := by
  rw [toJson_strings]
  unfold VE.Bridge.strings
  simp only [Json.getArr?, List.toList_toArray]
  exact mapM_str l

theorem contains_filter_ne {l : List String} {r p : String} (h : p ≠ r) :
    (l.filter (· != r)).contains p = l.contains p := by
  induction l with
  | nil => rfl
  | cons x xs ih =>
    simp only [List.filter_cons]
    by_cases hx : x = r
    · subst hx
      have : (p == x) = false := beq_eq_false_iff_ne.mpr h
      simp only [bne_self_eq_false, Bool.false_eq_true, ↓reduceIte, ih, List.contains_cons, this, Bool.false_or]
    · have : (x != r) = true := bne_iff_ne.mpr hx
      simp only [this, ↓reduceIte, List.contains_cons, ih]

theorem ok_bind {ε α β : Type} (x : α) (f : α → Except ε β) : (Except.ok x >>= f) = f x := rfl

theorem strip_spec {env env' : Json} (h : VE.Readings.Wire.stripReadings env = .ok env') :
    ∃ P l, env.getObjVal? "profiles" = .ok P ∧ VE.Bridge.strings P = .ok l ∧
      env' = env.setObjVal! "profiles" (toJson (l.filter (· != VE.Readings.Wire.readingsProfile))) := by
  unfold VE.Readings.Wire.stripReadings at h
  obtain ⟨P, hP, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨l, hl, h⟩ := VE.Order.ProfileGate.bind_ok h
  exact ⟨P, l, hP, hl, (Except.ok.inj h).symm⟩

theorem getObjValD_of_ok {j v : Json} {k : String} (h : j.getObjVal? k = .ok v) : j.getObjValD k = v := by
  rw [CaseCond.getObjValD_eq, h]; rfl

theorem soft_lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') :
    VE.SoftNorms.Run.usesSoftPath ((Json.obj m).setObjVal! "environment" env') =
      VE.SoftNorms.Run.usesSoftPath (.obj m) := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  have hPa := strings_arr hl
  unfold VE.SoftNorms.Run.usesSoftPath
  simp only [getObjValD_set_eq wf, getObjValD_set_ne wf (show "environment" ≠ "kind" by decide),
    getObjValD_set_ne wf (show "environment" ≠ "norms" by decide),
    getObjValD_set_ne wf (show "environment" ≠ "document" by decide), he,
    getObjValD_set_ne wfe (show "profiles" ≠ "vocabulary" by decide), getObjValD_set_eq wfe,
    getObjValD_of_ok hP, hPa, toJson_strings]
  rw [any_filter_map _ (by decide)]


theorem rights_lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') :
    VE.Rights.Run.usesRightsPath ((Json.obj m).setObjVal! "environment" env') =
      VE.Rights.Run.usesRightsPath (.obj m) := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  have hPa := strings_arr hl
  unfold VE.Rights.Run.usesRightsPath
  simp only [getObjValD_set_eq wf, getObjValD_set_ne wf (show "environment" ≠ "kind" by decide),
    getObjValD_set_ne wf (show "environment" ≠ "document" by decide), he,
    getObjValD_set_ne wfe (show "profiles" ≠ "vocabulary" by decide), getObjValD_set_eq wfe,
    getObjValD_of_ok hP, hPa, toJson_strings]
  rw [any_filter_map _ (by decide)]

theorem layered_lower {e : Std.TreeMap.Raw String Json compare} {env' : Json} (wfe : e.WF)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') :
    VE.Norms.Plain.layered env' = VE.Norms.Plain.layered (.obj e) := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  have hPa := strings_arr hl
  unfold VE.Norms.Plain.layered
  simp only [getObjValD_set_eq wfe, getObjValD_of_ok hP, hPa, toJson_strings, Array.any_toList.symm,
    List.toList_toArray]
  rw [any_filter_map _ (by decide)]

theorem norms_lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') :
    VE.Norms.Run.usesNormsPath ((Json.obj m).setObjVal! "environment" env') =
      VE.Norms.Run.usesNormsPath (.obj m) := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  unfold VE.Norms.Run.usesNormsPath
  simp only [getObjValD_set_eq wf, getObjValD_set_ne wf (show "environment" ≠ "kind" by decide),
    getObjValD_set_ne wf (show "environment" ≠ "document" by decide), he,
    getObjVal_set_ne wf (show "environment" ≠ "norms" by decide),
    getObjValD_set_ne wfe (show "profiles" ≠ "vocabulary" by decide)]

theorem nd_lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') :
    VE.NormDefaults.Run.usesNormDefaultsPath ((Json.obj m).setObjVal! "environment" env') =
      VE.NormDefaults.Run.usesNormDefaultsPath (.obj m) := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  unfold VE.NormDefaults.Run.usesNormDefaultsPath VE.NormDefaults.Wire.hasProfile VE.NormDefaults.Wire.profilesOf
    VE.NormDefaults.Wire.unspecifiedNames
  simp only [getObjValD_set_eq wf, getObjValD_set_ne wf (show "environment" ≠ "kind" by decide), he,
    getObjVal_set_ne wfe (show "profiles" ≠ "vocabulary" by decide), getObjVal_set_eq wfe, hP,
    hl]
  rw [ok_bind, ok_bind, strings_toJson, hl]
  simp only [Except.toOption, Option.getD,
    contains_filter_ne (r := VE.Readings.Wire.readingsProfile) (p := VE.NormDefaults.Wire.profile) (by decide)]


/-- The conditions the lower routes' skeletons put on the case, each read the same of the case and
of its rewrite: a condition other than a conjunction (`atomInv`), or a conjunction of those. -/
def atomInv : CaseCond → Bool
  | .kind _ => true
  | .lacks k => k != "environment"
  | .path [k] => k != "environment"
  | .decided d => d == .rightsPath || d == .softPath || d == .normDefaultsPath || d == .normsPath
  | _ => false

def lowerInv : CaseCond → Bool
  | .all cs => cs.all atomInv
  | c => atomInv c

theorem atomInv_holds {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') (cond : CaseCond) (h : atomInv cond = true) :
    cond.holds (.obj m) = cond.holds ((Json.obj m).setObjVal! "environment" env') := by
  match cond, h with
  | .kind k, _ =>
    simp only [CaseCond.holds, getObjValD_set_ne wf (show "environment" ≠ "kind" by decide)]
  | .lacks k, h =>
    have hk : "environment" ≠ k := by simp [atomInv] at h; exact fun e => h e.symm
    simp only [CaseCond.holds, Json.setObjVal!]
    rw [← Json.setObjVal!, getObjVal_set_ne wf hk]
  | .path [k], h =>
    have hk : "environment" ≠ k := by simp [atomInv] at h; exact fun e => h e.symm
    simp only [CaseCond.holds, Json.setObjVal!]
    rw [← Json.setObjVal!, getObjVal_set_ne wf hk]
  | .decided d, h =>
    simp only [CaseCond.holds_decided]
    cases d
    · exact (soft_lower wf wfe he hs).symm
    · exact (rights_lower wf wfe he hs).symm
    · exact (nd_lower wf wfe he hs).symm
    · simp only [CaseDecider.fn, getObjValD_set_eq wf, he]
      rw [norms_lower wf wfe he hs, layered_lower wfe hs]
    all_goals exact absurd h (by decide)
  | .path [], h => simp [atomInv] at h
  | .path (_ :: _ :: _), h => simp [atomInv] at h
  | .has _, h => simp [atomInv] at h
  | .all _, h => simp [atomInv] at h

theorem lowerInv_holds {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') (cond : CaseCond) (h : lowerInv cond = true) :
    cond.holds (.obj m) = cond.holds ((Json.obj m).setObjVal! "environment" env') := by
  cases cond with
  | all cs =>
    simp only [lowerInv, List.all_eq_true] at h
    induction cs with
    | nil => rfl
    | cons c cs ih =>
      simp only [CaseCond.holds_all_cons]
      rw [atomInv_holds wf wfe he hs c (h c List.mem_cons_self),
        ih (fun x hx => h x (List.mem_cons_of_mem _ hx))]
  | _ => exact atomInv_holds wf wfe he hs _ h

/-- The rewritten case is one the service could decode. -/
theorem caseWF_lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') : CaseWF ((Json.obj m).setObjVal! "environment" env') := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  refine ⟨fun m' h => ?_, fun m' h => ?_⟩
  · simp only [Json.setObjVal!] at h
    cases h
    exact Std.TreeMap.Raw.WF.insert wf
  · rw [getObjValD_set_eq wf] at h
    simp only [Json.setObjVal!] at h
    cases h
    exact Std.TreeMap.Raw.WF.insert wfe

end Lower

/-- A row of the lower route for the rewritten case, of a skeleton whose conditions on the case
`lowerInv` admits, is a row for the case. -/
theorem lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') {k : Skel} {v : Json}
    (h : Fits ((Json.obj m).setObjVal! "environment" env') k v) (hc : Skel.condsOk lowerInv 1000 k = true) :
    Fits (.obj m) k v :=
  Fits.congr (p := lowerInv) (fun cond hp => (lowerInv_holds wf wfe he hs cond hp).symm) h 1000 hc

/-- The case is of none of the readings kinds: the selection reaches the lower routes' rows. -/
theorem of_lower_row {v : Json} {s : Skel} (hs : s ∈ [Skeletons.rights, Skeletons.softNorms, Skeletons.normDefaults,
      Skeletons.norms])
    (hn : ∀ k ∈ ["readings-validate", "readings-separate", "readings-elaborate", "readings-conflict",
      "readings-certificate", "readings-model", "readings-dead", "readings-choice"], (CaseCond.kind k).holds req = false)
    (h : Fits req s v) : Fits req Skeletons.readingsRoute v := by
  skel_norm
  repeat (refine Fits.onCaseE (hn _ (by simp)) ?_)
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hs
  rcases hs with rfl | rfl | rfl | rfl
  all_goals fits_from h

/-- The lower route's row, for a case of none of the readings kinds. -/
theorem runLower_fits (j : Json) (hj : CaseWF j)
    (hn : ∀ k ∈ ["readings-validate", "readings-separate", "readings-elaborate", "readings-conflict",
      "readings-certificate", "readings-model", "readings-dead", "readings-choice"], (CaseCond.kind k).holds j = false) :
    Fits j Skeletons.readingsRoute (runLower j) := by
  unfold runLower
  split
  · exact of_lower_row (by simp) hn (Rights.runCaseReported_fits j hj)
  · rename_i ps hps
    -- The environment is an object (its profiles were read) and so is the case.
    obtain ⟨P, hP, _⟩ := VE.Order.ProfileGate.bind_ok hps
    cases hen : j.getObjValD "environment" with
    | obj e =>
      cases j with
      | obj m =>
        have wf := hj.1 m rfl
        have wfe := hj.2 e hen
        split
        · rename_i env' hs
          have hj' := caseWF_lower wf wfe hs
          simp only []
          repeat' split
          all_goals first
            | exact of_lower_row (by simp) hn (lower wf wfe hen hs (Rights.runCaseReported_fits _ hj') (by decide))
            | exact of_lower_row (by simp) hn (lower wf wfe hen hs (SoftNorms.runCaseReported_fits _ hj') (by decide))
            | exact of_lower_row (by simp) hn
                (lower wf wfe hen hs (NormDefaults.runCaseReported_fits _ hj') (by decide))
            | exact of_lower_row (by simp) hn (lower wf wfe hen hs (Norms.runCaseReported_fits _ hj') (by decide))
        · simp only []
          repeat' split
          all_goals first
            | exact of_lower_row (by simp) hn (Rights.runCaseReported_fits _ hj)
            | exact of_lower_row (by simp) hn (SoftNorms.runCaseReported_fits _ hj)
            | exact of_lower_row (by simp) hn (NormDefaults.runCaseReported_fits _ hj)
            | exact of_lower_row (by simp) hn (Norms.runCaseReported_fits _ hj)
      | _ => cases hen
    | _ =>
      rw [hen] at hP
      simp [Json.getObjVal?] at hP

/-- A case whose `kind` is `x` is read as `x`. -/
theorem caseKind_of_holds {j : Json} {x : String} (h : (CaseCond.kind x).holds j = true) :
    VE.Route.Run.caseKind j = .ok x := by
  simp only [CaseCond.holds, CaseCond.getObjValD_eq] at h
  unfold VE.Route.Run.caseKind
  cases hv : j.getObjVal? "kind" with
  | error e => rw [hv] at h; simp [Option.getD, Except.toOption, Json.getStr?] at h
  | ok v =>
    rw [hv] at h
    cases v with
    | str s =>
      have h' : (some s == some x) = true := h
      have : s = x := by simpa using h'
      subst this
      rfl
    | _ => simp [Json.getStr?, Except.toOption, Option.getD] at h

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.readingsRoute (runCaseReported j) := by
  unfold runCaseReported
  split
  · rename_i k hk
    split
    · rename_i hr
      split
      · exact runCase_fits j _ ‹_›
      · -- The runner's error row, for a case of a readings kind.
        have hK : j.getObjValD "kind" = .str k := by
          unfold VE.Route.Run.caseKind at hk
          split at hk
          · exact CaseCond.getObjValD_of_str ‹_› hk
          · cases hk; simp [s2Kinds] at hr
        simp only [s2Kinds, Bool.or_eq_true, beq_iff_eq, List.contains_cons, List.contains_nil,
          Bool.or_false] at hr
        simp only [or_assoc] at hr
        rcases hr with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> fits
    · rename_i hr
      refine runLower_fits j hj fun x hx => ?_
      cases hb : (CaseCond.kind x).holds j
      · rfl
      · have := caseKind_of_holds hb
        rw [hk] at this
        cases this
        simp [s2Kinds] at hr hx
        rcases hx with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> simp_all
  · rename_i hk
    refine runLower_fits j hj fun x hx => ?_
    cases hb : (CaseCond.kind x).holds j
    · rfl
    · exact absurd (caseKind_of_holds hb) (hk x)

end ResponseShape.Encoders.ReadingsRoute
