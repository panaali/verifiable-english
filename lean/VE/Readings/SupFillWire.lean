import VE.Readings.SupExtra
import VE.Readings.SupWireSound
import VE.Readings.UnspecifiedWire

/-! The superposed kinds under the unspecified completion (docs/spec/readings-defaults-PLAN.md RD-6b; spec 6.7).

A document under the completion takes the superposed row when `sup (fillDoc N)` is superposable and `supU N` is
`WellFormedU` (`routeND`, `UnspecifiedWire.lean`). Its superposed kinds run S2a's on the filled document with
`Fill_T` of `supU N` appended to the slot (`ndQ`, labels `unsaid:pair:<r>,<m>`): the conflict certificates over
`Background_base′ ++ slotUnder ++ Fill_T`, the certificate by `supCertificateCheckExtra`, the model by
`supModelCheckExtra`, every model over the filled base vocabulary (`unsaid__p` included). DRI ruling 5 runs on every
compatible choice up to `maxChoiceChecks`, the soft check on its filled document and `WellFormedU` on `choiceU N c`
(`ndChecked`). The wire theorems read each accepted answer in norm-defaults' terms through `nd_superpose_conflict_free`,
`nd_superpose_all` and `superpose_countermodel_extra` at `fill_transfers`. Nothing is decided from JSON a caller
supplies: the filled documents and `Fill_T` are regenerated from the decoded document. -/
namespace VE.Readings.Wire
open Lean
open VE.Readings
open VE.Bridge (Entity)
open VE.Norms (envAt size Sat targets)
open VE.SoftNorms (soften circ canon)
open VE.Rights (correlate)
open VE.Compose (slotConflictFreeCheck backgroundValidP)
open VE.NormDefaults (fill EntailsU)
universe u

/-! ## The replays -/

/-- A superposed case under the completion: the admitted document (its filled document admitted by S1), the filled
    document superposable with `WellFormedU (supU N)`, a compatible choice, and DRI ruling 5's check passed. -/
structure SupReplayND where
  f : AdmittedNDFull
  sp : superposable (fillDoc f.r.N) = true
  wfu : VE.NormDefaults.WellFormedU (supU f.r.N) = true
  sat : (choices f.r.N.D).isEmpty = false
  checked : ndChecked f.r.b.a.re f.r.N = true

/-- `readings-conflict`, `-certificate` and `-model` refuse a document under the completion that is not superposable
    with its cause, as `supReplayOf` refuses one that is not. -/
def ndRefusal (re : ReadingsEnvironment) (N : NDoc) : String :=
  s!"{notSuperposableText (completionFinding N.D).1} ({ndNotSuperposable re N}); use readings-choice"

def supReplayND (f : AdmittedNDFull) : Except String SupReplayND :=
  if h : superposable (fillDoc f.r.N) = true ∧ VE.NormDefaults.WellFormedU (supU f.r.N) = true then
    if hs : (choices f.r.N.D).isEmpty = false then
      if hc : ndChecked f.r.b.a.re f.r.N = true then pure ⟨f, h.1, h.2, hs, hc⟩
      else throw ((ndSuperposedCheckText f.r.b.a.re f.r.N).getD checkBudgetText)
    else throw (unsatText f.r.N.D)
  else throw (ndRefusal f.r.b.a.re f.r.N)

theorem SupReplayND.hyps (r : SupReplayND) : Hyps (fillDoc r.f.r.N) := hyps_fill r.f.r.wfU r.f.r.wfF r.sp

/-- The filled document's frame reads the filled admission's environment. -/
theorem filled_frame_E (f : AdmittedNDFull) : (fillDoc f.r.N).frame.soft.E = f.fa.a.re.se.ne.rv.environment := by
  rw [← f.fa.frame]; rfl

/-- The assumed readings, each a candidate of the filled document. -/
def decodeAssumedND (N : NDoc) (j : Json) :
    Except String { A : Choice // ∀ x ∈ A, (candidate (fillDoc N) x.1 x.2).isSome } :=
  decodeAssumed (fillDoc N) j

theorem candidate_of_fill {N : NDoc} {A : Choice} (hA : ∀ x ∈ A, (candidate (fillDoc N) x.1 x.2).isSome) :
    ∀ x ∈ A, (candidate N.D x.1 x.2).isSome := fun x hx => by
  have := hA x hx
  rw [candidate_fillDoc] at this
  simpa using this

structure CertificateReplayND extends SupReplayND where
  assumed : Choice
  hA : ∀ x ∈ assumed, (candidate (fillDoc f.r.N) x.1 x.2).isSome
  Γ : List VE.Formula
  φ : VE.Formula
  hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc f.r.N)) []
  hφ : φ.WellFormed (sharedEnv (fillDoc f.r.N)) []
  conflictCerts : List (Option VE.Tableau.Certificate)
  cert : VE.Tableau.Certificate
  taken : takenBy (fillDoc f.r.N) assumed = true

def replayCertificateND (f : AdmittedNDFull) (j : Json) : Except String CertificateReplayND := do
  let r ← supReplayND f
  let D := fillDoc r.f.r.N
  let ⟨A, hA⟩ ← decodeAssumedND r.f.r.N (j.getObjValD "assumed")
  let ⟨(Γ, φ), hΓ, hφ⟩ ← decodeShared D (j.getObjValD "premises") (j.getObjValD "conclusion")
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  if ht : takenBy D A = true then
    pure ⟨r, A, hA, Γ, φ, hΓ, hφ, decodeConflictCerts D (j.getObjValD "conflict_certificates"), cert, ht⟩
  else throw (untakenText D A)

def replayCertificateNDJ (j : Json) : Except String CertificateReplayND := do
  replayCertificateND (← admitNDFullJ (← j.getObjVal? "environment") (← j.getObjVal? "document")) j

structure ModelReplayND extends SupReplayND where
  assumed : Choice
  Γ : List VE.Formula
  φ : VE.Formula
  hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc f.r.N)) []
  hφ : φ.WellFormed (sharedEnv (fillDoc f.r.N)) []
  M : VE.FiniteModel Entity
  valid : M.Valid (envAt (soften (correlate (sup (fillDoc f.r.N)).1)) 0)

def replayModelND (f : AdmittedNDFull) (j : Json) : Except String ModelReplayND := do
  let r ← supReplayND f
  let D := fillDoc r.f.r.N
  let A ← decodeChoice (j.getObjValD "assumed")
  let ⟨(Γ, φ), hΓ, hφ⟩ ← decodeShared D (j.getObjValD "premises") (j.getObjValD "conclusion")
  let ⟨M, valid⟩ ← decodeSupModel r.f.fa.a.re D r.hyps (filled_frame_E r.f) (← j.getObjVal? "model")
  pure ⟨r, A, Γ, φ, hΓ, hφ, M, valid⟩

def replayModelNDJ (j : Json) : Except String ModelReplayND := do
  replayModelND (← admitNDFullJ (← j.getObjVal? "environment") (← j.getObjVal? "document")) j

/-! ## The wire theorems -/

/-- A replayed document under the completion on the superposed route has a compatible reading, and every compatible
    reading's filled document is well formed for the chain and its `choiceU N c` is `WellFormedU` (DRI ruling 5, run
    on every compatible choice). -/
theorem readings_wire_nd_choices (r : SupReplayND) :
    (∃ c, Compatible r.f.r.N.D c) ∧ ∀ c, Compatible r.f.r.N.D c →
      sideWF (fillDoc r.f.r.N) (choiceDoc (fillDoc r.f.r.N) c) = true ∧
        VE.NormDefaults.WellFormedU (choiceU r.f.r.N c) = true := by
  have hh := r.hyps
  refine ⟨exists_compatible_of_choices r.f.r.N.D r.sat, fun c hc => ?_⟩
  have hc' := (compatible_fillDoc r.f.r.N c).mpr hc
  exact ⟨choice_wellFormed _ hh.wf hh.chain hh.sp (choicesSoftChecked_of_nd r.checked) c hc',
    (ndChecked_spec hh.ready r.checked c hc').2⟩

/-- CONFLICT-FREE under the completion: the conflict certificates of a replayed certificate case, checked on the
    slot with `Fill_T`, make every compatible reading taking the assumed ones CONFLICT-FREE in norm-defaults' sense,
    and an accepted certificate proves the conclusion from its assertions and the premises there. -/
theorem readings_wire_nd_all_sound (j : Json) (r : CertificateReplayND) (_h : replayCertificateNDJ j = .ok r)
    (hc : slotConflictFreeCheck (correlate (sup (fillDoc r.f.r.N)).1)
      (slotUnder (fillDoc r.f.r.N) r.assumed ++ ndQ r.f.r.N) r.conflictCerts = true)
    (ha : supCertificateCheckExtra (fillDoc r.f.r.N) r.assumed (ndQ r.f.r.N) r.Γ r.φ r.cert = true) :
    ∀ c, Compatible r.f.r.N.D c → (∀ x ∈ r.assumed, x ∈ c) →
      VE.NormDefaults.ConflictFreeU.{u} (choiceU r.f.r.N c) ∧
        EntailsU.{u} (choiceU r.f.r.N c) ((choiceDoc r.f.r.N.D c).2 ++ r.Γ) r.φ := by
  intro c hcc hAc
  have hh := r.hyps
  have hcf := VE.Compose.slot_conflict_free.{u} _ (sup_wellFormed _ hh.sp).2 _ _ hc
  have hA := candidate_of_fill r.hA
  exact ⟨(nd_superpose_conflict_free r.f.r.N r.f.r.wfU r.f.r.wfF r.sp r.wfu r.assumed hA).mp hcf c hcc hAc,
    nd_superpose_all r.f.r.N r.f.r.wfU r.f.r.wfF r.sp r.wfu r.assumed hA hcf r.Γ r.φ r.hΓ r.hφ r.cert ha c hcc hAc⟩

/-- The conflict certificates alone, under the completion. -/
theorem readings_wire_nd_conflict_sound (r : SupReplayND) (A : Choice)
    (hA : ∀ x ∈ A, (candidate (fillDoc r.f.r.N) x.1 x.2).isSome) (certs : List (Option VE.Tableau.Certificate))
    (hc : slotConflictFreeCheck (correlate (sup (fillDoc r.f.r.N)).1)
      (slotUnder (fillDoc r.f.r.N) A ++ ndQ r.f.r.N) certs = true) :
    ∀ c, Compatible r.f.r.N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU r.f.r.N c) :=
  (nd_superpose_conflict_free r.f.r.N r.f.r.wfU r.f.r.wfF r.sp r.wfu A (candidate_of_fill hA)).mp
    (VE.Compose.slot_conflict_free.{u} _ (sup_wellFormed _ r.hyps.sp).2 _ _ hc)

/-- A checked model under the completion is an admissible filled situation of the reading its atoms encode
    (norm-defaults' `BaseAdmissibleU`, `Fill_T` included); with the conclusion false it is a countermodel there. -/
theorem readings_wire_nd_model_sound (j : Json) (r : ModelReplayND) (_h : replayModelNDJ j = .ok r)
    (hm : supModelCheckExtra (fillDoc r.f.r.N) r.assumed (ndQ r.f.r.N) r.Γ r.M = true)
    (hn : (circ (correlate (sup (fillDoc r.f.r.N)).1) r.φ).eval r.M [] = false) :
    ∃ c, Compatible r.f.r.N.D c ∧ (∀ x ∈ r.assumed, x ∈ c) ∧ Encodes (fillDoc r.f.r.N) c r.M.asStructure ∧
      VE.NormDefaults.BaseAdmissibleU (choiceU r.f.r.N c) (pull (fillDoc r.f.r.N) c r.M.asStructure) ∧
      Sat (canon (fill (choiceU r.f.r.N c)) (pull (fillDoc r.f.r.N) c r.M.asStructure))
        ((choiceDoc r.f.r.N.D c).2 ++ r.Γ) ∧
      ¬ r.φ.denote (canon (fill (choiceU r.f.r.N c)) (pull (fillDoc r.f.r.N) c r.M.asStructure)) [] := by
  have hh := r.hyps
  have hp := wellFormedND_parts r.f.r.wfU
  obtain ⟨c, hc, hA, he, hB, hs, hφ⟩ := superpose_countermodel_extra (fillDoc r.f.r.N) hh.wf hh.chain hh.sp
    r.assumed _ _ (fill_transfers r.f.r.N r.f.r.wfU r.f.r.wfF r.sp r.wfu) r.Γ r.φ r.hΓ r.hφ r.M r.valid hm hn
  have hfc := fillDoc_choice r.f.r.N hp.2.1 hp.2.2.1 c
  unfold expand at hs hφ
  rw [hfc.1, hfc.2] at hs
  rw [hfc.1] at hφ
  exact ⟨c, (compatible_fillDoc r.f.r.N c).mp hc, hA, he, (baseAdmissibleP_choiceU r.f.r.wfU c _).mp hB, hs, hφ⟩

theorem backgroundValidP_append {α : Type u} [DecidableEq α] (X : VE.SoftNorms.SoftDoc) (P Q : List VE.Formula)
    (M : VE.FiniteModel α) (h : backgroundValidP X (P ++ Q) M = true) :
    backgroundValidP X P M = true ∧ Q.all (fun a => a.eval M []) = true := by
  simp only [backgroundValidP, Bool.and_eq_true, List.all_eq_true, List.mem_append] at h ⊢
  exact ⟨⟨h.1, fun a ha => h.2 a (Or.inl ha)⟩, fun a ha => h.2 a (Or.inr ha)⟩

/-- A conflict witness under the completion: a model of the slot with `Fill_T` whose target holds at a typed tuple
    is an admissible filled situation of the reading its atoms encode, where that reading is not conflict-free. -/
theorem readings_wire_nd_witness_sound (r : SupReplayND) (A : Choice)
    (t : String × List String × VE.Formula) (ht : t ∈ targets (soften (correlate (sup (fillDoc r.f.r.N)).1)))
    (M : VE.FiniteModel Entity) (valid : M.Valid (envAt (soften (correlate (sup (fillDoc r.f.r.N)).1)) 0))
    (hb : backgroundValidP (correlate (sup (fillDoc r.f.r.N)).1) (slotUnder (fillDoc r.f.r.N) A ++ ndQ r.f.r.N) M = true)
    (vs : List Entity) (typed : VE.TupleTyped M.asStructure t.2.1 vs) (hw : t.2.2.eval M (VE.Norms.tupleVal vs) = true) :
    ∃ c, Compatible r.f.r.N.D c ∧ (∀ x ∈ A, x ∈ c) ∧
      VE.NormDefaults.BaseAdmissibleU (choiceU r.f.r.N c) (pull (fillDoc r.f.r.N) c M.asStructure) ∧
      ¬ VE.Norms.ConflictFree (fill (choiceU r.f.r.N c)) (pull (fillDoc r.f.r.N) c M.asStructure) := by
  have hh := r.hyps
  have hp := wellFormedND_parts r.f.r.wfU
  obtain ⟨hb1, hQ⟩ := backgroundValidP_append _ _ _ M hb
  obtain ⟨c, hc, hA, he, hB, hn⟩ := superpose_conflict_witness (fillDoc r.f.r.N) hh.wf hh.chain hh.sp A t ht M valid
    hb1 vs typed hw
  have hBs := VE.Compose.baseAdmissibleP_of_valid _ _ M valid hb1
  have hBslot : VE.Compose.BaseAdmissibleP (correlate (sup (fillDoc r.f.r.N)).1) (slotP (fillDoc r.f.r.N))
      M.asStructure := ⟨hBs.1, fun a ha => hBs.2 a (List.mem_append_left _ ha)⟩
  have hQs : Sat M.asStructure (ndQ r.f.r.N) := fun a ha => by
    simp only [List.all_eq_true] at hQ
    exact (VE.eval_iff_denote M [] a).mp (hQ a ha)
  have hQc := ((fill_transfers r.f.r.N r.f.r.wfU r.f.r.wfF r.sp r.wfu).2 c hc _ hBslot he).mp hQs
  have hYn := correlate_noRights _ (choiceDoc_noRights _ c hh.noRights)
  have hfc := fillDoc_choice r.f.r.N hp.2.1 hp.2.2.1 c
  refine ⟨c, (compatible_fillDoc r.f.r.N c).mp hc, hA,
    (baseAdmissibleP_choiceU r.f.r.wfU c _).mp ⟨hB.1, (VE.Compose.sat_append _ _ _).mpr ⟨hB.2, hQc⟩⟩, ?_⟩
  rw [← hfc.1]; exact hn

end VE.Readings.Wire

/-! ## The runners -/

namespace VE.Readings.Run
open Lean
open VE.Readings
open VE.Readings.Wire
open VE.Norms (targets)
open VE.SoftNorms (soften)
open VE.Rights (correlate)

/-- The first slot premise (the slot with `Fill_T`), or assumed atom, a model falsifies. -/
def firstFailingND {α : Type} [DecidableEq α] (N : NDoc) (A : Choice) (M : VE.FiniteModel α) : Option String :=
  ((ndSlotLabelled N ++ A.map (fun x => (s!"readings:{x.1}:{x.2}", choiceAtom (fillDoc N) x.1 x.2))).find?
    (fun x => !x.2.eval M [])).map (·.1)

def ndSlotLabels (N : NDoc) : List String := (ndSlotLabelled N).map (·.1)

/-- `readings-conflict` under the completion: `runConflict` on the filled document with `Fill_T` in the slot. -/
def runConflictND (id : String) (f : AdmittedNDFull) (j : Json) : Except String Json := do
  let r ← supReplayND f
  let N := r.f.r.N
  let D := fillDoc N
  let ⟨A, _⟩ ← decodeAssumedND N (j.getObjValD "assumed")
  unless takenBy D A do throw (untakenText D A)
  let X := correlate (sup D).1
  let w := j.getObjValD "witness"
  if (j.getObjVal? "witness").toBool then
    let ⟨M, _⟩ ← decodeSupModel r.f.fa.a.re D r.hyps (filled_frame_E r.f) (w.getObjValD "model")
    unless VE.Compose.backgroundValidP X (slotUnder D A ++ ndQ N) M do
      throw (VE.Route.Wire.invalidModel "readings background")
    let name ← VE.Bridge.stringField w "target"
    let ids ← VE.Bridge.strings (w.getObjValD "tuple")
    let some t := (targets (soften X)).find? (·.1 == name) | throw s!"InvalidInput: unknown conflict target {name}"
    let tuple := t.2.1.zip ids
    unless ids.length == t.2.1.length && VE.Bridge.tupleCheck M t.2.1 tuple do
      throw "InvalidInput: witness tuple has the wrong length or sort"
    let conflict := t.2.2.eval M (VE.Norms.tupleVal tuple)
    return okWith id [("verdict", .str (if conflict then "CONFLICT" else "UNKNOWN")), ("target", .str t.1),
      ("assumed", choiceJson A), ("choice", choiceJson (encodedChoice D M))]
  let certs := decodeConflictCerts D (j.getObjValD "conflict_certificates")
  let free := VE.Compose.slotConflictFreeCheck X (slotUnder D A ++ ndQ N) certs
  pure (okWith id [("verdict", .str (if free then "CONFLICT-FREE" else "UNKNOWN")), ("assumed", choiceJson A),
    ("targets", toJson ((targets (soften X)).map (·.1))), ("reading_premises", toJson (ndSlotLabels N))])

/-- `readings-certificate` under the completion (`readings_wire_nd_all_sound`). -/
def runCertificateND (id : String) (f : AdmittedNDFull) (j : Json) : Except String Json := do
  let r ← replayCertificateND f j
  let N := r.f.r.N
  let D := fillDoc N
  let X := correlate (sup D).1
  let free := VE.Compose.slotConflictFreeCheck X (slotUnder D r.assumed ++ ndQ N) r.conflictCerts
  let valid := supCertificateCheckExtra D r.assumed (ndQ N) r.Γ r.φ r.cert
  pure (okWith id [("accepted", .bool (free && valid)), ("conflict_free", .bool free), ("valid", .bool valid),
    ("assumed", choiceJson r.assumed), ("reading_premises", toJson (ndSlotLabels N))])

/-- `readings-model` under the completion (`readings_wire_nd_model_sound`). -/
def runModelND (id : String) (f : AdmittedNDFull) (j : Json) : Except String Json := do
  let r ← replayModelND f j
  let N := r.f.r.N
  let D := fillDoc N
  unless r.assumed.all (fun x => (candidate D x.1 x.2).isSome) && takenBy D r.assumed do
    throw (if r.assumed.all (fun x => (candidate D x.1 x.2).isSome) then untakenText D r.assumed
           else "InvalidInput: assumed reading is no candidate")
  let X := correlate (sup D).1
  let valid := supModelCheckExtra D r.assumed (ndQ N) r.Γ r.M
  let value := (VE.SoftNorms.circ X r.φ).eval r.M []
  pure (okWith id [("valid", .bool valid), ("conclusion_value", .bool value),
    ("first_failing", match firstFailingND N r.assumed r.M with | some l => .str l | none => .null),
    ("assumed", choiceJson r.assumed), ("choice", choiceJson (encodedChoice D r.M))])

/-- The S2a kinds of a document under the completion, admitted once (`admitNDFull`): elaborate, choice and dead as
    RD-2a answers them, the superposed kinds on the filled document (RD-6b), refused with the route's cause when the
    document is not superposable (`supReplayND`). -/
def runNDKind (id kind : String) (f : AdmittedNDFull) (j : Json) : Except String Json := do
  if kind == "readings-elaborate" then return ← runElaborateNDFilled id f
  if kind == "readings-choice" then return ← runChoiceND id f.r j
  if kind == "readings-dead" then return ← deadAnswer id f.r.N.D j
  if kind == "readings-conflict" then return ← runConflictND id f j
  if kind == "readings-certificate" then return ← runCertificateND id f j
  if kind == "readings-model" then return ← runModelND id f j
  throw s!"UnsupportedProfile: case kind {kind} is not available on the readings route"

end VE.Readings.Run
