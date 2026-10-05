import VE.NormDefaults.Wire

/-! Witness, status and gap replays under `norm-defaults@0` (docs/spec/norm-defaults.md
2.5, 3.1, 3.2 and 8): the evidence Python proposes, checked from raw JSON.

* A CONFLICT witness is a finite model of `E‴_base` (the base vocabulary plus the
  `unsaid__` tables, which are the filling) that passes `Background_base` and `Fill_T`
  and makes a regenerated target of `fill U` true at a typed tuple
  (`normDefaults_wire_witness_sound`).
* A status is read on a finite model of `E_base`: `table3`, exhaustive
  enumeration, or two supplied fillings with opposite outcomes
  (`normDefaults_wire_status_sound`): SETTLED is `SettledAs`, UNDECIDED is
  `UndecidedAt`; anything else is UNKNOWN.
* `gaps: none` for `p` is an accepted certificate for `∀x̄. ¬reached_p` over
  `Background_base(E‴) ++ Fill_T` (`normDefaults_wire_gaps_sound`); `gaps: reachable`
  (for a deny/allow `p`: `default reached`) is a filled finite model of `E‴_base`
  at which `reached_p` is true (`normDefaults_wire_reached_sound`). -/
namespace VE.NormDefaults.Wire
open Lean
open VE.Norms
open VE.Bridge (fields strings)
universe u

theorem lookup_append {α : Type} (l₁ l₂ : List (String × α)) (k : String) :
    VE.Bridge.lookup (l₁ ++ l₂) k = match VE.Bridge.lookup l₁ k with
      | some x => some x
      | none => VE.Bridge.lookup l₂ k := by
  simp only [VE.Bridge.lookup, List.find?_append]
  cases l₁.find? (fun x => x.1 == k) <;> rfl

/-! ## Models of `E‴_base` -/

/-- The unsaid predicates as model vocabulary entries. -/
def unsaidEntries (U : UDoc) : List (String × List String) :=
  U.unspec.map fun p => (unsaidName p, sortsOf U.D p)

/-- `E‴_base` as model vocabulary: the base vocabulary and the unsaid tables. -/
def baseModelVocabularyU (s : SourceU) : VE.Bridge.Vocabulary :=
  let v := VE.Norms.Replay.baseModelVocabulary s.src.ne s.src.D
  { v with predicates := v.predicates ++ unsaidEntries s.U }

theorem baseModelU_valid (s : SourceU) (hs : s.profiled = true) (M : VE.FiniteModel VE.Bridge.Entity)
    (h : M.Valid (baseModelVocabularyU s).environment) : M.Valid (envAt (fill s.U) 0) := by
  have hw := s.wfU hs
  have hu := uvalid hw
  have hD := s.doc
  refine ⟨fun c t hc => h.1 c t (by
    change s.U.D.E.constants c = some t at hc
    rw [hD, s.src.env] at hc
    exact hc), fun p vs hp => ?_⟩
  obtain ⟨ss, hss, ht⟩ := h.2 p vs hp
  refine ⟨ss, ?_, ht⟩
  change VE.Bridge.lookup ((VE.Norms.Replay.baseModelVocabulary s.src.ne s.src.D).predicates ++ unsaidEntries s.U) p =
    some ss at hss
  rw [lookup_append] at hss
  cases hl1 : VE.Bridge.lookup (VE.Norms.Replay.baseModelVocabulary s.src.ne s.src.D).predicates p with
  | some x =>
    rw [hl1] at hss
    have hx : x = ss := Option.some.inj hss
    subst hx
    change VE.Bridge.lookup (s.src.ne.rv.vocabulary.predicates.filter _) p = some x at hl1
    rw [VE.Norms.Replay.lookup_filter_not] at hl1
    split at hl1
    · cases hl1
    · rename_i hl
      have hl' : p ∉ layerNames s.U.D.T := by rw [hD]; simpa using hl
      have hE : s.U.D.E.predicates p = some x := by rw [hD, s.src.env]; exact hl1
      simp only [envAt, hide, List.drop_zero, layerNames_fill hu, hl', if_false, fill_E]
      rw [fillEnv_declared hu hE, hE]
  | none =>
    rw [hl1] at hss
    obtain ⟨q, hq, he⟩ : ∃ q ∈ s.U.unspec, unsaidName q = p ∧ sortsOf s.U.D q = ss := by
      simp only [unsaidEntries, VE.Bridge.lookup] at hss
      rw [List.find?_map] at hss
      cases hf : s.U.unspec.find? ((fun x => x.1 == p) ∘ fun q => (unsaidName q, sortsOf s.U.D q)) with
      | none => rw [hf] at hss; cases hss
      | some q =>
        rw [hf] at hss
        simp only [Option.map_some, Option.some.injEq] at hss
        exact ⟨q, List.mem_of_find?_eq_some hf, by simpa using List.find?_some hf, hss⟩
    obtain ⟨rfl, rfl⟩ := he
    exact envAt_fill_unsaid hu 0 hq

/-! ## CONFLICT witnesses -/

structure WitnessDataU (s : SourceU) where
  M : VE.FiniteModel VE.Bridge.Entity
  valid : M.Valid (envAt (fill s.U) 0)
  background : backgroundValid (fill s.U) M = true
  filled : (fillPremises s.U).all (fun φ => φ.eval M []) = true
  target : String × List String × VE.Formula
  mem : target ∈ targets (fill s.U)
  tuple : List VE.Bridge.Entity
  typed : VE.TupleTyped M.asStructure target.2.1 tuple

def WitnessDataU.conflict {s : SourceU} (w : WitnessDataU s) : Bool := w.target.2.2.eval w.M (tupleVal w.tuple)

/-- Decode a filled witness: the model of `E‴_base` must pass `Background_base` and
`Fill_T` (else `InvalidModel`, never a verdict), then the target and typed tuple. -/
def witnessFromU (s : SourceU) (w : Json) : Except String (WitnessDataU s) := do
  if hs : s.profiled = true then
    let v := baseModelVocabularyU s
    let data ← VE.Bridge.decodeModelData v (← w.getObjVal? "model")
    let M := data.toModel
    let name ← VE.Bridge.stringField w "target"
    let ids ← VE.Bridge.strings (← w.getObjVal? "tuple")
    if hv : data.valid v = true then
      if hb : backgroundValid (fill s.U) M = true then
        if hf : (fillPremises s.U).all (fun φ => φ.eval M []) = true then
          match hfind : (targets (fill s.U)).find? (·.1 == name) with
          | none => throw s!"InvalidInput: unknown conflict target {name}"
          | some t =>
            let tuple := t.2.1.zip ids
            if ht : ids.length == t.2.1.length && VE.Bridge.tupleCheck M t.2.1 tuple then
              pure ⟨M, baseModelU_valid s hs M (VE.Bridge.modelData_valid data v hv), hb, hf, t,
                List.mem_of_find?_eq_some hfind, tuple,
                (VE.Bridge.tupleCheck_iff M _ _).mp (by simp only [Bool.and_eq_true] at ht; exact ht.2)⟩
            else throw "InvalidInput: witness tuple has the wrong length or sort"
        else throw (VE.Route.Wire.invalidModel "unsaid")
      else throw (VE.Route.Wire.invalidModel "literals")
    else throw "model is not semantically admissible"
  else throw "UnsupportedProfile: filled witnesses require norm-defaults@0"

def replayWitnessU (j : Json) : Except String ((s : SourceU) × WitnessDataU s) := do
  let environment ← j.getObjVal? "environment"
  let s ← decodeSourceU environment (j.getObjValD "norms")
  let wd ← witnessFromU s (← j.getObjVal? "witness")
  pure ⟨s, wd⟩

/-- A filled finite witness of any target of `fill U` refutes `ConflictFreeU`. -/
theorem targetU_refutes (U : UDoc) (h : WellFormed (fill U) = true) (t : String × List String × VE.Formula)
    (ht : t ∈ targets (fill U)) (B : VE.Structure.{u}) (hB : BaseAdmissibleU U B) (vs : List B.Carrier)
    (hvs : VE.TupleTyped B t.2.1 vs) (hw : t.2.2.denote B (tupleVal vs)) : ¬ ConflictFreeU.{u} U := by
  have hv := valid_of_wellFormed _ h
  intro hc
  have hcf := hc B hB
  rcases List.mem_append.mp ht with ht | ht
  · obtain ⟨q, hq, he⟩ := List.mem_filterMap.mp ht
    cases q with
    | defn _ => cases he
    | reg r =>
      simp only [Option.some.injEq] at he
      subst he
      exact hcf.1 r (mem_syms_reg hq) vs hvs hw
  · obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ht
    exact hcf.2 pr hpr vs hvs hw

/-- `normDefaults_wire_witness_sound` (CONFLICT half): a successful raw witness
replay whose regenerated target formula is true at the typed tuple of the checked
filled model refutes, for the document decoded from that very input,
CONFLICT-FREE under every admissible filling (a settled or latent conflict). -/
theorem normDefaults_wire_witness_sound (j : Json) (s : SourceU) (w : WitnessDataU s)
    (h : replayWitnessU j = .ok ⟨s, w⟩) (hw : w.conflict = true) :
    decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") = .ok s ∧ ¬ ConflictFreeU.{0} s.U := by
  unfold replayWitnessU at h
  obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨s', hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨wd, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  refine ⟨by rw [he]; exact hd, targetU_refutes s.U s.wfFill w.target w.mem w.M.asStructure
    ⟨baseAdmissible_of_valid (fill s.U) w.M w.valid w.background, fun φ hφ =>
      (VE.eval_iff_denote w.M [] φ).mp (List.all_eq_true.mp w.filled φ hφ)⟩
    w.tuple w.typed ((VE.eval_iff_denote w.M _ _).mp hw)⟩

/-! ## Statuses -/

/-- The status a replay reports. -/
inductive Status | settled (b : Bool) | undecided | unknown
  deriving DecidableEq, Repr

def Status.label : Status → String
  | .settled true => "SETTLED yes"
  | .settled false => "SETTLED no"
  | .undecided => "UNDECIDED"
  | .unknown => "UNKNOWN"

/-- A finite filling from JSON. Validate the entire table before converting ids to
typed entities: `zip` alone would silently discard extra ids, and `withFill`
filters ill-typed tuples rather than rejecting untrusted evidence. -/
def decodeFilling (U : UDoc) (M : VE.FiniteModel VE.Bridge.Entity) (j : Json) :
    Except String (FiniteFill U VE.Bridge.Entity) := do
  let supplied ← VE.Bridge.fields j
  let allowed := U.unspec.map unsaidName
  for (name, _) in supplied do
    unless allowed.contains name do throw s!"InvalidInput: unknown filling table {name}"
  let tables ← U.unspec.mapM fun p => do
    let rows ← match j.getObjVal? (unsaidName p) with
      | .ok r => (← r.getArr?).toList.mapM strings
      | .error _ => pure []
    unless rows.eraseDups.length == rows.length do throw "duplicate relation tuple"
    let sorts := sortsOf U.D p
    let tuples ← rows.mapM fun row => do
      unless row.length == sorts.length do throw "wrong relation arity"
      let tuple := sorts.zip row
      unless VE.Bridge.tupleCheck M sorts tuple do throw "dangling or wrong-sort tuple"
      pure tuple
    pure (unsaidName p, tuples)
  pure fun n => (VE.Bridge.lookup tables n).getD []

structure StatusData (j : Json) where
  s : SourceU
  decoded : decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") = .ok s
  profiled : s.profiled = true
  M : VE.FiniteModel VE.Bridge.Entity
  valid : M.Valid (envAt s.U.D 0)
  background : backgroundValid s.U.D M = true
  r : Regulated
  mem : r ∈ s.U.D.T.regulated
  tuple : List VE.Bridge.Entity
  typed : VE.TupleTyped M.asStructure r.sorts tuple
  status : Status
  sound₁ : ∀ b, status = .settled b → SettledAs.{0} s.U M.asStructure r tuple b
  sound₂ : status = .undecided → UndecidedAt.{0} s.U M.asStructure r tuple

/-- The status of `p` at a tuple of a base model, by the named method. -/
def replayStatus (j : Json) : Except String (StatusData j) :=
  match hs0 : decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") with
  | .error e => throw e
  | .ok s => do
  if hs : s.profiled = true then
    let hw := s.wfU hs
    let v := VE.Norms.Replay.baseModelVocabulary s.src.ne s.src.D
    let data ← VE.Bridge.decodeModelData v (← j.getObjVal? "model")
    let M := data.toModel
    let name ← VE.Bridge.stringField j "predicate"
    let ids ← VE.Bridge.strings (← j.getObjVal? "tuple")
    let method ← VE.Bridge.stringField j "method"
    if hv : data.valid v = true then
      if hb : backgroundValid s.U.D M = true then
        match hfind : s.U.D.T.regulated.find? (·.name == name) with
        | none => throw s!"InvalidInput: unknown regulated predicate {name}"
        | some r =>
          let tuple := r.sorts.zip ids
          if ht : ids.length == r.sorts.length && VE.Bridge.tupleCheck M r.sorts tuple then
            have hvalid : M.Valid (envAt s.U.D 0) := by
              rw [s.doc]
              exact VE.Norms.Replay.baseModel_valid s.src.ne s.src.D s.src.env M (VE.Bridge.modelData_valid data v hv)
            have hmem : r ∈ s.U.D.T.regulated := List.mem_of_find?_eq_some hfind
            have htyped : VE.TupleTyped M.asStructure r.sorts tuple :=
              (VE.Bridge.tupleCheck_iff M _ _).mp (by simp only [Bool.and_eq_true] at ht; exact ht.2)
            let unknown : StatusData j := ⟨s, hs0, hs, M, hvalid, hb, r, hmem, tuple, htyped, .unknown,
              (fun _ hb'' => by cases hb''), (fun hu => by cases hu)⟩
            if method == "table3" then
              match h3 : table3 s.U M r.name tuple with
              | some b => pure ⟨s, hs0, hs, M, hvalid, hb, r, hmem, tuple, htyped, .settled b,
                  (fun b' hb'' => by
                    cases hb''
                    exact settled_of_table3 s.U hw M hvalid hb r hmem tuple htyped b h3),
                  (fun hu => by cases hu)⟩
              | none => pure unknown
            else if method == "enumerate" then
              match he : enumerateSettled s.U M r.name tuple with
              | some b => pure ⟨s, hs0, hs, M, hvalid, hb, r, hmem, tuple, htyped, .settled b,
                  (fun b' hb'' => by
                    cases hb''
                    exact settled_of_enumeration s.U hw M hvalid hb r hmem tuple htyped b he),
                  (fun hu => by cases hu)⟩
              | none => pure unknown
            else if method == "undecided" then
              let F₁ ← decodeFilling s.U M (j.getObjValD "yes")
              let F₂ ← decodeFilling s.U M (j.getObjValD "no")
              if hc : fillValid s.U M F₁ = true ∧ fillValid s.U M F₂ = true ∧
                  (outcomeBase (fill s.U) r.name).eval (M.withFill F₁) (tupleVal tuple) = true ∧
                  (outcomeBase (fill s.U) r.name).eval (M.withFill F₂) (tupleVal tuple) = false then
                pure ⟨s, hs0, hs, M, hvalid, hb, r, hmem, tuple, htyped, .undecided,
                  (fun _ hb'' => by cases hb''),
                  (fun _ => undecided_witness_sound s.U hw M hvalid hb F₁ F₂ hc.1 hc.2.1 r hmem tuple htyped
                    hc.2.2.1 hc.2.2.2)⟩
              else pure unknown
            else throw s!"InvalidInput: unknown status method {method}"
          else throw "InvalidInput: status tuple has the wrong length or sort"
      else throw (VE.Route.Wire.invalidModel "literals")
    else throw "model is not semantically admissible"
  else throw "UnsupportedProfile: statuses require norm-defaults@0"

/-- `normDefaults_wire_status_sound`: a replayed SETTLED status is `SettledAs` and a
replayed UNDECIDED status is `UndecidedAt`, for the document and model decoded from
that very input; UNKNOWN claims nothing. -/
theorem normDefaults_wire_status_sound (j : Json) (d : StatusData j) (_h : replayStatus j = .ok d) :
    decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") = .ok d.s ∧
    (∀ b, d.status = .settled b → SettledAs.{0} d.s.U d.M.asStructure d.r d.tuple b) ∧
    (d.status = .undecided → UndecidedAt.{0} d.s.U d.M.asStructure d.r d.tuple) :=
  ⟨d.decoded, d.sound₁, d.sound₂⟩

/-! ## `gaps: none` -/

/-- The package key and target of `p`'s `default reached`/gap formula. -/
def reachedTarget (U : UDoc) (r : Regulated) : String × List String × VE.Formula :=
  ("reached:" ++ r.name, r.sorts, reachedF U r.name)

/-- An accepted certificate for `∀x̄. ¬reached_p` over `Background_base(E‴) ++ Fill_T`
means no admissible filling reaches `p`: `gaps: none` (and, for a deny/allow `p`,
the completion is never used). -/
theorem normDefaults_wire_gaps_sound (U : UDoc) (r : Regulated) (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (fill U) 0) (baseBackgroundU U)
      (targetConclusion (reachedTarget U r)) c = true) :
    ∀ B : VE.Structure.{u}, BaseAdmissibleU U B → ∀ vs, VE.TupleTyped B r.sorts vs →
      ¬ (reachedF U r.name).denote B (tupleVal vs) := by
  intro B hB vs hvs
  have he := VE.Tableau.checkCertificate_sound.{u} _ _ _ c ok B hB.1.1 (fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact hB.1.2 a ha
    · exact hB.2 a ha)
  exact (bindAll_denote_nil B _ _).mp he vs hvs

structure GapsReplay where
  s : SourceU
  r : Regulated
  cert : Option VE.Tableau.Certificate

def GapsReplay.none_ (g : GapsReplay) : Bool := match g.cert with
  | some c => VE.Tableau.checkCertificate (envAt (fill g.s.U) 0) (baseBackgroundU g.s.U)
      (targetConclusion (reachedTarget g.s.U g.r)) c
  | none => false

def replayGaps (j : Json) : Except String GapsReplay := do
  let environment ← j.getObjVal? "environment"
  let norms := j.getObjValD "norms"
  let s ← decodeSourceU environment norms
  let name ← VE.Bridge.stringField j "predicate"
  match s.U.D.T.regulated.find? (·.name == name) with
  | none => throw s!"InvalidInput: unknown regulated predicate {name}"
  | some r =>
    pure ⟨s, r, decodePackageU s.U environment norms (j.getObjValD "packages") (reachedTarget s.U r)⟩

/-! ## `gaps: reachable` and `default reached` -/

structure ReachedData (s : SourceU) where
  M : VE.FiniteModel VE.Bridge.Entity
  valid : M.Valid (envAt (fill s.U) 0)
  background : backgroundValid (fill s.U) M = true
  filled : (fillPremises s.U).all (fun φ => φ.eval M []) = true
  r : Regulated
  mem : r ∈ s.U.D.T.regulated
  tuple : List VE.Bridge.Entity
  typed : VE.TupleTyped M.asStructure r.sorts tuple

def ReachedData.reached {s : SourceU} (d : ReachedData s) : Bool :=
  (reachedF s.U d.r.name).eval d.M (tupleVal d.tuple)

/-- Decode a filled model of `E‴_base` (the `model` field of `w`, checked against
`Background_base` and `Fill_T`), the predicate (`name`, read after the model) and the
typed tuple (the `tuple` field of `w`). -/
def reachedFromU (s : SourceU) (name : Except String String) (w : Json) : Except String (ReachedData s) := do
  if hs : s.profiled = true then
    let v := baseModelVocabularyU s
    let data ← VE.Bridge.decodeModelData v (← w.getObjVal? "model")
    let M := data.toModel
    let name ← name
    let ids ← VE.Bridge.strings (← w.getObjVal? "tuple")
    if hv : data.valid v = true then
      if hb : backgroundValid (fill s.U) M = true then
        if hf : (fillPremises s.U).all (fun φ => φ.eval M []) = true then
          match hfind : s.U.D.T.regulated.find? (·.name == name) with
          | none => throw s!"InvalidInput: unknown regulated predicate {name}"
          | some r =>
            let tuple := r.sorts.zip ids
            if ht : ids.length == r.sorts.length && VE.Bridge.tupleCheck M r.sorts tuple then
              pure ⟨M, baseModelU_valid s hs M (VE.Bridge.modelData_valid data v hv), hb, hf, r,
                List.mem_of_find?_eq_some hfind, tuple,
                (VE.Bridge.tupleCheck_iff M _ _).mp (by simp only [Bool.and_eq_true] at ht; exact ht.2)⟩
            else throw "InvalidInput: tuple has the wrong length or sort"
        else throw (VE.Route.Wire.invalidModel "unsaid")
      else throw (VE.Route.Wire.invalidModel "literals")
    else throw "model is not semantically admissible"
  else throw "UnsupportedProfile: filled models require norm-defaults@0"

/-- Decode a filled model of `E‴_base` (checked against `Background_base` and `Fill_T`),
the predicate and the typed tuple. -/
def replayReached (j : Json) : Except String ((s : SourceU) × ReachedData s) := do
  let environment ← j.getObjVal? "environment"
  let s ← decodeSourceU environment (j.getObjValD "norms")
  pure ⟨s, ← reachedFromU s (VE.Bridge.stringField j "predicate") j⟩

/-- `normDefaults_wire_reached_sound`: a replayed filled model at which `reached_p`
evaluates true is an admissible filling at which no author rule decides `p` at the
typed tuple: `gaps: reachable` (for an unspecified `p`) or `default reached` (for a
deny/allow `p`, the evidence behind `UngroundedDefault`). -/
theorem normDefaults_wire_reached_sound (j : Json) (s : SourceU) (d : ReachedData s)
    (_h : replayReached j = .ok ⟨s, d⟩) (hr : d.reached = true) :
    BaseAdmissibleU s.U d.M.asStructure ∧ VE.TupleTyped d.M.asStructure d.r.sorts d.tuple ∧
      (reachedF s.U d.r.name).denote d.M.asStructure (tupleVal d.tuple) :=
  ⟨⟨baseAdmissible_of_valid (fill s.U) d.M d.valid d.background, fun φ hφ =>
      (VE.eval_iff_denote d.M [] φ).mp (List.all_eq_true.mp d.filled φ hφ)⟩,
    d.typed, (VE.eval_iff_denote d.M _ _).mp hr⟩

end VE.NormDefaults.Wire
