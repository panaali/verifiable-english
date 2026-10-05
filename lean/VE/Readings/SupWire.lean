import VE.Readings.Route

/-! The wire of S2a (docs/spec/composition-s2.md 3, 4.1, 7, 8.5): the couplings and narrowings decoded with W2's and
rights 3.3's texts, the admission of a superposed document, and the replays of a certificate and of a model on
`sup D`.

A document carries, beside S1's `units` and `reading_sets`, optional `couplings` and `narrowings` in W2's shape
(`{"id", "axis", "sets": [{"set", "version"}], "by", "reason_spans"}` and
`{"id", "set", "version", "keeps", "by", "reason_spans"}`); the decoder runs today's checks in today's order, with
today's texts, after S1's admission. A choice is written `[[set, index], ...]`. A model is the finite-model wire
form over the base vocabulary of `sup D`'s soft route (`supVocabulary`): the frame's sorts and `ve__reading`, its
constants and `ve__here`, the decision predicates of `sup D`, the bits and the frame's base predicates. -/
namespace VE.Readings.Wire
open Lean
open VE.Bridge (fields strings stringField Entity)
open VE.Norms (envAt size)
open VE.SoftNorms (soften decisions)
open VE.Rights (RightsDoc correlate)
open VE.Route.Admission (token)

/-! ## Couplings and narrowings -/

def sortedKeys (j : Json) : Option (List String) :=
  match fields j with
  | .ok kvs => some (VE.Route.sortStrings (kvs.map (·.1)))
  | .error _ => none

def stringList (j : Json) : Option (List String) := (strings j).toOption

/-- The labels of a set's readings on an axis, when every reading carries one. -/
def axisLabels (R : SetJ) (axis : String) : Option (List String) :=
  R.readings.mapM (fun r => r.labels.lookup axis)

/-- W2's `validate_couplings`, in its order and with its texts; the satisfiability check is the last. -/
def decodeCouplings (doc : Json) (sets : List SetJ) (unitIds : List String) : Except String (List Coupling) := do
  let items ← match doc.getObjValD "couplings" with
    | .null => pure []
    | .arr xs => pure xs.toList
    | _ => throw "invalid couplings"
  if items.length > 8 then throw "ResourceLimit: couplings"
  let act := active sets
  let mut ids : List String := []
  let mut out : List Coupling := []
  for item in items do
    let bad := "invalid coupling"
    unless sortedKeys item == some ["axis", "by", "id", "reason_spans", "sets"] do throw bad
    let id ← match item.getObjValD "id" with | .str s => pure s | _ => throw bad
    let axis ← match item.getObjValD "axis" with | .str s => pure s | _ => throw bad
    let by_ ← match item.getObjValD "by" with | .str s => pure s | _ => throw bad
    let spans ← match stringList (item.getObjValD "reason_spans") with | some l => pure l | none => throw bad
    let refs ← match item.getObjValD "sets" with | .arr xs => pure xs.toList | _ => throw bad
    unless token id && !ids.contains id && token axis && token by_ && !spans.isEmpty &&
        spans.all unitIds.contains && refs.length ≥ 2 do throw bad
    ids := ids ++ [id]
    let mut seen : List String := []
    let mut members : List (String × Nat) := []
    for ref in refs do
      let badSet := "invalid coupling set"
      unless sortedKeys ref == some ["set", "version"] do throw badSet
      let s ← match ref.getObjValD "set" with | .str s => pure s | _ => throw badSet
      let v ← match (ref.getObjValD "version").getNat? with | .ok n => pure n | .error _ => throw badSet
      let some R := act.find? (fun R => R.id == s && R.version == v) | throw badSet
      if seen.contains s then throw badSet
      seen := seen ++ [s]
      members := members ++ [(s, v)]
      if (axisLabels R axis).isNone then throw s!"CouplingLabelMissing: {id}, {s}"
    let values := members.filterMap (fun (s, v) =>
      (act.find? (fun R => R.id == s && R.version == v)).bind (axisLabels · axis))
    let shared := match values with
      | [] => []
      | l :: rest => l.filter (fun x => rest.all (·.contains x))
    if shared.isEmpty then throw s!"CouplingLabelMissing: {id}, {(members.head?.map (·.1)).getD ""}"
    out := out ++ [⟨id, axis, members⟩]
  pure out

/-- W2's `validate_narrowings`, in its order and with its texts. A narrowing may cite any recorded version; only
    one on the active version is in force (1.2). -/
def decodeNarrowings (doc : Json) (sets : List SetJ) (unitIds : List String) : Except String (List Narrowing) := do
  let items ← match doc.getObjValD "narrowings" with
    | .null => pure []
    | .arr xs => pure xs.toList
    | _ => throw "narrowings must be a list"
  let mut ids : List String := []
  let mut out : List Narrowing := []
  for item in items do
    unless sortedKeys item == some ["by", "id", "keeps", "reason_spans", "set", "version"] do
      throw "invalid narrowing"
    let id := match item.getObjValD "id" with | .str s => s | _ => ""
    let by_ := match item.getObjValD "by" with | .str s => s | _ => ""
    unless token id && !ids.contains id && token by_ do throw "invalid narrowing id or author"
    ids := ids ++ [id]
    let s ← match item.getObjValD "set" with | .str s => pure s | _ => throw "invalid narrowing"
    let v ← match item.getObjValD "version" with
      | .num n => match (Json.num n).getNat? with | .ok k => pure k | .error _ => throw "invalid narrowing"
      | _ => throw "invalid narrowing"
    unless token s && v ≥ 1 do throw "invalid narrowing"
    let some R := sets.find? (fun R => R.id == s && R.version == v)
      | throw "narrowing cites unknown reading set version"
    let keeps ← match stringList (item.getObjValD "keeps") with
      | some l => pure l
      | none => throw "narrowing must keep named readings"
    unless !keeps.isEmpty && keeps.all (fun k => R.readings.any (·.id == k)) do
      throw "narrowing must keep named readings"
    let spans ← match stringList (item.getObjValD "reason_spans") with
      | some l => pure l
      | none => throw "narrowing needs cited source units"
    unless !spans.isEmpty && spans.all unitIds.contains do throw "narrowing needs cited source units"
    out := out ++ [⟨id, s, v, keeps⟩]
  pure out

/-! ## The S2a admission -/

/-- A document admitted by S1 with its couplings and narrowings decoded. -/
structure Admitted2 where
  a : Admitted
  D : Doc
  wf : WellFormedDoc D = true
  frame : D.frame = frameOf a.re a.doc.units

def unitIdsOf (document : Json) : List String :=
  match document.getObjValD "units" with
  | .arr us => us.toList.filterMap (fun u => match u.getObjValD "id" with | .str s => some s | _ => none)
  | _ => []

/-- `WellFormedDoc` reads the chain, the frame and the items alone: a document's couplings and narrowings leave it
    unchanged (`wellFormedDoc_links`), so the S2a admission keeps S1's check instead of building every candidate's
    document again (lean-first plan F5b: once per request). -/
theorem attachedIter_links (D : Doc) (cs : List Coupling) (ns : List Narrowing) :
    ∀ (n : Nat) (tbl : List (String × List String)),
      attachedIter ⟨D.chain, D.frame, D.items, cs, ns⟩ n tbl = attachedIter D n tbl
  | 0, _ => rfl
  | n + 1, tbl => by
    simp only [attachedIter, attachedIter_links D cs ns n]
    rfl

theorem attached_links (D : Doc) (cs : List Coupling) (ns : List Narrowing) (u : String) :
    attached ⟨D.chain, D.frame, D.items, cs, ns⟩ u = attached D u := by
  unfold attached
  rw [attachedIter_links]
  rfl

theorem wellFormedDoc_links (D : Doc) (cs : List Coupling) (ns : List Narrowing) :
    WellFormedDoc ⟨D.chain, D.frame, D.items, cs, ns⟩ = WellFormedDoc D := by
  simp only [WellFormedDoc, singlyAttached, sideWF, free, one, attached_links]
  rfl

def admitS2 (environment document : Json) : Except String Admitted2 := do
  let ids := unitIdsOf document
  unless decide ids.Nodup do throw "duplicate or invalid unit id"
  let a ← admitReadings environment document
  let sets ← match document.getObjValD "reading_sets" with
    | .arr ss => ss.toList.mapM decodeSet
    | .null => pure []
    | _ => throw "reading_sets must be a list"
  let cs ← decodeCouplings document sets a.doc.units
  -- Today's satisfiability check of the couplings alone (`CouplingUnsatisfiable`), before the narrowings.
  let Dc : Doc := { a.D with couplings := cs }
  if !cs.isEmpty && (search Dc Dc.sets [] 1).isEmpty then
    throw ("CouplingUnsatisfiable: " ++ ", ".intercalate (VE.Route.sortStrings (cs.map (·.id))))
  let ns ← decodeNarrowings document sets a.doc.units
  -- `WellFormedDoc` reads no coupling or narrowing: S1's check holds of the document that carries them.
  pure ⟨a, ⟨a.D.chain, a.D.frame, a.D.items, cs, ns⟩, (wellFormedDoc_links a.D cs ns).trans a.wf, rfl⟩

/-! ## A superposed document -/

/-- The decoded document of a superposed case: S1's admission with couplings and narrowings decoded (4.1 step 1),
    a compatible choice found (4.1 step 3: never a verdict over no reading) and the soft check of every compatible
    choice's document passed (DRI ruling 5). -/
structure SupReplay where
  D : Doc
  wf : WellFormedDoc D = true
  soft : D.chain ≠ .rights
  sp : superposable D = true
  sat : (choices D).isEmpty = false
  checked : choicesSoftChecked D = true

/-- The superposed route's admission of a case: `ReadingsUnsatisfiable` when no choice is compatible, the chain's
    diagnostic under the first choice whose document fails the soft check, `ResourceLimit` past `maxChoiceChecks`
    choices; a document that is not superposable is the enumerated route's. -/
def supReplayOf (b : Admitted2) : Except String SupReplay :=
  if h : b.D.chain ≠ .rights ∧ superposable b.D = true then
    if hs : (choices b.D).isEmpty = false then
      if hc : choicesSoftChecked b.D = true then pure ⟨b.D, b.wf, h.1, h.2, hs, hc⟩
      else throw ((superposedCheckText b.D).getD checkBudgetText)
    else throw (unsatText b.D)
  else match notSuperposable b.D with
    | some (sets, cause) => throw s!"{notSuperposableText sets} ({cause}); use readings-choice"
    | none => throw "UnsupportedProfile: superposition of a rights document is S2b; use readings-choice"

def replaySup (j : Json) : Except String SupReplay := do
  supReplayOf (← admitS2 (← j.getObjVal? "environment") (← j.getObjVal? "document"))

def decodeChoice (j : Json) : Except String Choice := do
  let xs ← match j with
    | .arr xs => pure xs.toList
    | .null => pure []
    | _ => throw "InvalidInput: invalid choice"
  xs.mapM fun x => match x with
    | .arr #[.str s, n] => match n.getNat? with
      | .ok i => pure (s, i)
      | .error _ => throw "InvalidInput: invalid choice"
    | _ => throw "InvalidInput: invalid choice"

/-! ## The base vocabulary of `sup D` and its models -/

/-- The model vocabulary over `E′_base` of `sup D`: the decision predicates, the bits, then the frame's base
    predicates without layer symbols; the frame's sorts and constants with the choice sort and constant. -/
def supVocabulary (re : ReadingsEnvironment) (D : Doc) : VE.Bridge.Vocabulary :=
  { sorts := re.se.ne.rv.modelVocabulary.sorts ++ ["ve__reading"],
    constants := ("ve__here", "ve__reading") :: re.se.ne.rv.vocabulary.constants,
    predicates := decisions (sup D).1.soft ++ bitDecls D ++
      re.se.ne.rv.vocabulary.predicates.filter (fun p => !(VE.Norms.layerNames (soften (sup D).1.soft).T).contains p.1) }

theorem lookup_append_right {α : Type} (a b : List (String × α)) (k : String) :
    VE.Bridge.lookup (a ++ b) k = (VE.Bridge.lookup a k).or (VE.Bridge.lookup b k) := by
  simp only [VE.Bridge.lookup, List.find?_append]
  cases a.find? (fun x => x.1 == k) <;> rfl

theorem supModel_valid (re : ReadingsEnvironment) (D : Doc) (hh : Hyps D)
    (hf : D.frame.soft.E = re.se.ne.rv.environment) (M : VE.FiniteModel Entity)
    (h : M.Valid (supVocabulary re D).environment) : M.Valid (envAt (soften (correlate (sup D).1)) 0) := by
  rw [sup_correlate hh]
  have hw := sup_wfSoft hh
  have hfr : choiceFresh D = true := by
    have hr := hh.ready
    simp only [supReady, Bool.and_eq_true] at hr; exact hr.1.2
  simp only [choiceFresh, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hfr
  refine ⟨fun c s hc => h.1 c s ?_, fun p vs hp => ?_⟩
  · rw [envAt_consts0, soften_E, envPrime_constants, sup_E] at hc
    show VE.Bridge.lookup (("ve__here", "ve__reading") :: re.se.ne.rv.vocabulary.constants) c = some s
    unfold choiceEnv at hc
    split at hc
    · by_cases he : c = "ve__here"
      · subst he
        rw [hf] at hc hfr
        rw [hfr.1] at hc; cases hc
      · rw [hf] at hc
        have hc' : VE.Bridge.lookup re.se.ne.rv.vocabulary.constants c = some s := hc
        simpa [VE.Bridge.lookup, List.find?_cons, show ("ve__here" == c) = false from by simp [Ne.symm he]]
          using hc'
    · simp only at hc
      by_cases he : c = "ve__here"
      · subst he; simp at hc; subst hc; simp [VE.Bridge.lookup]
      · simp only [show (c == "ve__here") = false by simpa using he, Bool.false_eq_true, if_false] at hc
        rw [hf] at hc
        have hc' : VE.Bridge.lookup re.se.ne.rv.vocabulary.constants c = some s := hc
        simpa [VE.Bridge.lookup, List.find?_cons, show ("ve__here" == c) = false from by simp [Ne.symm he]]
          using hc'
  · obtain ⟨ss, hss, ht⟩ := h.2 p vs hp
    refine ⟨ss, ?_, ht⟩
    change VE.Bridge.lookup (decisions (sup D).1.soft ++ bitDecls D ++ _) p = some ss at hss
    rw [lookup_append_right, lookup_append_right] at hss
    cases hd : VE.Bridge.lookup (decisions (sup D).1.soft) p with
    | some ss' =>
      rw [hd] at hss
      simp only [Option.some_or, Option.some.injEq] at hss
      subst hss
      simp only [VE.Bridge.lookup, Option.map_eq_some_iff] at hd
      obtain ⟨x, hx, rfl⟩ := hd
      have hxp : x.1 = p := by simpa using List.find?_some hx
      rw [← hxp]
      exact envAt_decision hw 0 (List.mem_of_find?_eq_some hx)
    | none =>
      rw [hd] at hss
      simp only [Option.none_or] at hss
      have hnd : p ∉ VE.SoftNorms.decisionNames (sup D).1.soft := by
        intro hm
        obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hm
        simp only [VE.Bridge.lookup, Option.map_eq_none_iff] at hd
        exact absurd (List.find?_eq_none.mp hd x hx) (by simp)
      cases hb : VE.Bridge.lookup (bitDecls D) p with
      | some ss' =>
        rw [hb] at hss
        simp only [Option.some_or, Option.some.injEq] at hss
        subst hss
        simp only [VE.Bridge.lookup, Option.map_eq_some_iff] at hb
        obtain ⟨x, hx, rfl⟩ := hb
        have hxp : x.1 = p := by simpa using List.find?_some hx
        have hxm := List.mem_of_find?_eq_some hx
        simp only [bitDecls, List.mem_flatMap, List.mem_range, List.mem_map] at hxm
        obtain ⟨m, hm, j, hj, rfl⟩ := hxm
        rw [← hxp]
        exact sup_bit hh hm hj 0
      | none =>
        rw [hb] at hss
        simp only [Option.none_or] at hss
        rw [VE.Norms.Replay.lookup_filter_not] at hss
        split at hss
        · cases hss
        · rename_i hl
          rw [envAt_other 0 hl hnd, sup_E]
          unfold choiceEnv
          split
          · rw [hf]; exact hss
          · simp only
            rw [List.find?_eq_none.mpr (fun x hx he => by
              simp only [VE.Bridge.lookup, Option.map_eq_none_iff] at hb
              exact absurd (List.find?_eq_none.mp hb x hx) (by simpa using he))]
            rw [hf]; exact hss

def decodeSupModel (re : ReadingsEnvironment) (D : Doc) (hh : Hyps D) (hf : D.frame.soft.E = re.se.ne.rv.environment)
    (j : Json) : Except String { M : VE.FiniteModel Entity // M.Valid (envAt (soften (correlate (sup D).1)) 0) } := do
  let v := supVocabulary re D
  let data ← VE.Bridge.decodeModelData v j
  if hv : data.valid v = true then
    pure ⟨data.toModel, supModel_valid re D hh hf _ (VE.Bridge.modelData_valid data v hv)⟩
  else throw "model is not semantically admissible"

/-! ## Certificates and models on `sup D` -/

structure CertificateReplay extends SupReplay where
  assumed : Choice
  hA : ∀ x ∈ assumed, (candidate D x.1 x.2).isSome
  Γ : List VE.Formula
  φ : VE.Formula
  hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) []
  hφ : φ.WellFormed (sharedEnv D) []
  conflictCerts : List (Option VE.Tableau.Certificate)
  cert : VE.Tableau.Certificate
  taken : takenBy D assumed = true

def decodeAssumed (D : Doc) (j : Json) : Except String { A : Choice // ∀ x ∈ A, (candidate D x.1 x.2).isSome } := do
  let A ← decodeChoice j
  if h : A.all (fun x => (candidate D x.1 x.2).isSome) = true then
    pure ⟨A, fun x hx => List.all_eq_true.mp h x hx⟩
  else throw "InvalidInput: assumed reading is no candidate"

def decodeShared (D : Doc) (premises conclusion : Json) :
    Except String { p : List VE.Formula × VE.Formula //
      (∀ a ∈ p.1, a.WellFormed (sharedEnv D) []) ∧ p.2.WellFormed (sharedEnv D) [] } := do
  let Γ ← match premises with
    | .null => pure []
    | j => VE.Route.Wire.decodeFormulas (sharedEnv D) j
  let φ ← match conclusion with
    | .null => pure .bottom
    | j => VE.Route.Wire.decodeClosed (sharedEnv D) j
  if h : Γ.all (fun a => a.check (sharedEnv D) []) = true ∧ φ.check (sharedEnv D) [] = true then
    pure ⟨(Γ, φ), fun a ha => (VE.check_iff_wellFormed _ _ _).mp (List.all_eq_true.mp h.1 a ha),
      (VE.check_iff_wellFormed _ _ _).mp h.2⟩
  else throw "ill-typed or unbound formula"

/-- The conflict certificates, one per conflict target of `sup D`'s soft route, read from an object keyed by the
    target's name. -/
def decodeConflictCerts (D : Doc) (j : Json) : List (Option VE.Tableau.Certificate) :=
  (VE.Norms.targets (soften (correlate (sup D).1))).map (fun t =>
    (VE.CertificateWire.decodeCertificate (j.getObjValD t.1)).toOption)

def replayCertificate (j : Lean.Json) : Except String CertificateReplay := do
  let r ← replaySup j
  let ⟨A, hA⟩ ← decodeAssumed r.D (j.getObjValD "assumed")
  let ⟨(Γ, φ), hΓ, hφ⟩ ← decodeShared r.D (j.getObjValD "premises") (j.getObjValD "conclusion")
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  -- A named reading no compatible choice takes would make every certificate under it vacuous (review A1's class).
  if ht : takenBy r.D A = true then
    pure ⟨r, A, hA, Γ, φ, hΓ, hφ, decodeConflictCerts r.D (j.getObjValD "conflict_certificates"), cert, ht⟩
  else throw (untakenText r.D A)

structure ModelReplay extends SupReplay where
  assumed : Choice
  Γ : List VE.Formula
  φ : VE.Formula
  hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) []
  hφ : φ.WellFormed (sharedEnv D) []
  M : VE.FiniteModel VE.Bridge.Entity
  valid : M.Valid (envAt (soften (correlate (sup D).1)) 0)

def replayModel (j : Lean.Json) : Except String ModelReplay := do
  let b ← admitS2 (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let _ ← supReplayOf b
  if hs : b.D.chain ≠ .rights ∧ superposable b.D = true ∧ (choices b.D).isEmpty = false ∧
      choicesSoftChecked b.D = true then
    let A ← decodeChoice (j.getObjValD "assumed")
    let ⟨(Γ, φ), hΓ, hφ⟩ ← decodeShared b.D (j.getObjValD "premises") (j.getObjValD "conclusion")
    let ⟨M, valid⟩ ← decodeSupModel b.a.re b.D ⟨b.wf, hs.1, hs.2.1⟩ (by rw [b.frame]; rfl) (← j.getObjVal? "model")
    pure ⟨⟨b.D, b.wf, hs.1, hs.2.1, hs.2.2.1, hs.2.2.2⟩, A, Γ, φ, hΓ, hφ, M, valid⟩
  else throw "InvalidInput: readings document is not superposable"

end VE.Readings.Wire
