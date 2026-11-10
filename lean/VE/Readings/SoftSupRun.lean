import VE.Readings.SoftSupWire

/-! sc-11c: the soft runners on a superposed soft document (docs/spec/rd-9-soft-chain.md 14.3, 14.11): `readings-conflict`,
`-certificate`, `-model` and the scopes of a `readings-verdicts` case, reached only from `SoftSupRunExamples.lean`
(sc-11b switches `runSDKind`; sc-11cb builds the soft row on `SDCase`).

`sdCaseOf` admits a case once (`admitSDOf`) and routes it once, and stores what its pieces read (`SDCase`): `sup N.D`,
`supU N`, `fill (supU N)`, the slot, `softXL`, `supX`, `Fill_T`, the targets, the backgrounds, the checked choices and
the environments, each computed there; no piece admits or routes again (the norms chain's per-piece `x.run` is not
copied). The approved bodies `fillPremises` and `supVocabulary` read `fill U` and `sup D` themselves, once per case.
Each check an answer reports is the approved definition its `readings_wire_sd_*_sound` theorem reads, on the case's
values (`SDCase.*_eq`). `SDCount` counts what W-13 and W-14 measure; admissions are counted by `sdCaseOf`. -/
namespace VE.Readings.Run
open Lean VE.Readings VE.Readings.Wire
open VE.Norms (envAt size targets)
open VE.NormDefaults (fill UDoc)
open VE.Bridge (Entity)

/-- What a case has read (W-13, W-14). -/
structure SDCount where
  admissions : Nat := 0
  routes : Nat := 0
  images : Nat := 0
  replays : Nat := 0
  checks : Nat := 0
  deriving BEq, Repr

abbrev SDM := ExceptT String (StateM SDCount)

def attempt {α : Type} (x : SDM α) : SDM (Except String α) := tryCatch (Except.ok <$> x) (fun e => pure (.error e))

/-- A superposed soft case: its replay and the values its pieces read, each computed once (14.11). -/
structure SDCase where
  x : SupReplaySD
  S : VE.Rights.RightsDoc × List VE.Formula
  U : UDoc
  F : VE.Norms.Doc
  slot : VE.Compose.Labelled
  XL : List (String × VE.Formula)
  X : List VE.Formula
  fp : List VE.Formula
  FL : List (String × VE.Formula)
  ts : List (String × List String × VE.Formula)
  bgb : List VE.Formula
  bg : List VE.Formula
  el : List VE.Formula
  checked : List Choice
  envQ : VE.Environment
  v : VE.Bridge.Vocabulary
  canon : Except String Json
  hS : S = sup x.r.N.D
  hU : U = supU x.r.N
  hF : F = fill U
  hslot : slot = slotLabelled x.r.N.D
  hXL : XL = softXL x.r.N S.1
  hX : X = XL.map (·.2)
  hfp : fp = VE.NormDefaults.fillPremises U
  hFL : FL = (VE.NormDefaults.Admission.fillLabels U).zip fp
  hts : ts = targets F
  hbgb : bgb = VE.Norms.backgroundBase F
  hbg : bg = VE.Norms.background F
  hel : el = VE.Norms.elaborate F.T
  hc : checked = checkedChoices x.r.N.D
  hQ : envQ = sharedEnvSD x.r.N
  hv : v = supVocabulary x.r.b.a.re x.r.b.D
  hcanon : canon = VE.NormDefaults.Wire.canonicalEnvironmentJsonU x.r.b.a.re.lowerJson

theorem choices_isEmpty (D : Doc) : (choices D).isEmpty = (checkedChoices D).isEmpty := by
  simp only [checkedChoices, choices, search_eq, maxChoices, maxChoiceChecks]
  cases allFrom D D.sets [] <;> rfl

/-- The route of an admitted case, read once (`routeSD_superposed_iff`) in 14.11's order: `routeOf`, `superposable`
    and `WellFormedU (supU N)` (`sdSuperposable`, not charged: sc-11w), the count, then the work, then past 64
    choices each choice's text (at most 64: admission's, `sdCheck_of_admitted`). Off the superposed row: `refusal`. -/
def sdCaseOf (refusal : NDoc → String) (b : Admitted2) : SDM SDCase := do
  modify fun k => { k with admissions := k.admissions + 1 }
  match hadm : admitSDOf b with
  | .error e => throw e
  | .ok r =>
    modify fun k => { k with routes := k.routes + 1 }
    let N := r.N
    let S := sup N.D
    let U := asU N S.1
    let checked := checkedChoices N.D
    if h : routeOf true N.D = .enumerated ∧ superposable N.D = true ∧ VE.NormDefaults.WellFormedU U = true ∧
        checked.length ≤ maxChoiceChecks then
      let XL := softXL N S.1
      if hw : checked.length * (XL.length + (S.1.soft.T.nodes.map
            (fun M => (M.guard :: M.carveOuts).map VE.Bridge.formulaNodes)).flatten.sum) ≤ maxSdCheckWork ∧
          (checked.length ≤ maxChoices ∨ checked.all (fun c => (sdChoiceText r.b.a.re N c).isNone) = true) then
        if hs : checked.isEmpty = false then
          have hck : sdChecked r.b.a.re N = true := by
            rcases hw.2 with hle | hall
            · exact sdCheck_of_admitted b r hadm (superposable_supReady h.2.1) hle hw.1
            · simp only [sdChecked, Bool.and_eq_true, decide_eq_true_eq]
              exact ⟨⟨h.2.2.2, hw.1⟩, hall⟩
          have hr : routeSD r.b.a.re N = .superposed :=
            (routeSD_superposed_iff _ _).mpr ⟨h.1, by simp [sdSuperposable, h.2.1, h.2.2.1, supU, U, S], hck⟩
          let F := fill U
          let fp := VE.NormDefaults.fillPremises U
          pure ⟨⟨r, hr, by rw [choices_isEmpty]; exact hs⟩, S, U, F,
            VE.Rights.limPremisesLabelled S.1 ++ choiceLabelled N.D ++ gatedRel N.D, XL, XL.map (·.2), fp,
            (VE.NormDefaults.Admission.fillLabels U).zip fp, targets F, VE.Norms.backgroundBase F,
            VE.Norms.background F, VE.Norms.elaborate F.T, checked, sharedEnvSD N, supVocabulary r.b.a.re r.b.D,
            VE.NormDefaults.Wire.canonicalEnvironmentJsonU r.b.a.re.lowerJson,
            rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
        else throw (unsatText N.D)
      else throw (refusal N)
    else throw (refusal N)

namespace SDCase
variable (c : SDCase)

def N : NDoc := c.x.r.N
def slotX (A : Choice) : List VE.Formula := c.slot.formulas ++ atoms c.N.D A ++ c.X
def taken (A : Choice) : Bool := c.checked.any (fun ch => A.all (ch.contains ·))
def labels : List String := c.slot.map (·.1) ++ c.FL.map (·.1)

/-- `conflictFreeCheckX (supU N) (slotUnder N.D A ++ supX N)` on the case's values. -/
def free (A : Choice) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  c.ts.length == certs.length && (c.ts.zip certs).all (fun (t, k) => match k with
    | some k => VE.Tableau.checkCertificate (envAt c.F 0) (c.bgb ++ c.slotX A ++ c.fp)
        (VE.Norms.targetConclusion t) k
    | none => false)

/-- `premisesX (supU N) (slotUnder N.D A ++ supX N) ((sup N.D).2 ++ Γ)`, D14's premises, on the case's values. -/
def premises (A : Choice) (Γ : List VE.Formula) : List VE.Formula :=
  c.bg ++ c.slotX A ++ c.fp ++ c.el ++ (c.S.2 ++ Γ)

def model (A : Choice) (M : VE.FiniteModel Entity) (G : VE.NormDefaults.FiniteFill c.U Entity)
    (Γ : List VE.Formula) (φ : VE.Formula) : Bool × Bool :=
  ((VE.Norms.backgroundValid c.U.D M && c.fp.all (fun a => a.eval (M.withFill G) []) &&
    Γ.all (fun a => (VE.Norms.subst c.F.T (size c.F) a).eval (M.withFill G) [])) &&
      (c.slotX A).all (fun a => a.eval (M.withFill G) []),
    (VE.Norms.subst c.F.T (size c.F) φ).eval (M.withFill G) [])

def localFree (M : VE.FiniteModel Entity) (G : VE.NormDefaults.FiniteFill c.U Entity) : Bool :=
  c.ts.all (fun t => (VE.NormDefaults.allTuples M t.2.1).all (fun vs => !t.2.2.eval (M.withFill G) (VE.Norms.tupleVal vs)))

theorem slotX_eq (A : Choice) : c.slotX A = slotUnder c.N.D A ++ supX c.N := by
  cases c; subst_vars; simp [slotX, N, slotUnder, slotP, supX, softX, List.append_assoc]

theorem free_eq (A : Choice) (certs : List (Option VE.Tableau.Certificate)) :
    c.free A certs = VE.NormDefaults.Wire.conflictFreeCheckX (supU c.N) (slotUnder c.N.D A ++ supX c.N) certs := by
  rw [← slotX_eq]; cases c; subst_vars; rfl

theorem premises_eq (A : Choice) (Γ : List VE.Formula) :
    c.premises A Γ = VE.NormDefaults.Wire.premisesX (supU c.N) (slotUnder c.N.D A ++ supX c.N) ((sup c.N.D).2 ++ Γ) := by
  rw [← slotX_eq]; cases c; subst_vars; rfl

theorem model_eq (A : Choice) (M : VE.FiniteModel Entity) (G : VE.NormDefaults.FiniteFill c.U Entity)
    (Γ : List VE.Formula) (φ : VE.Formula) :
    c.model A M G Γ φ = VE.NormDefaults.modelCheckX c.U (slotUnder c.N.D A ++ supX c.N) M G Γ φ := by
  rw [← slotX_eq]; cases c; subst_vars; rfl

theorem local_eq (M : VE.FiniteModel Entity) (G : VE.NormDefaults.FiniteFill c.U Entity) :
    c.localFree M G = VE.Readings.Wire.localFree c.U M G := by
  cases c; subst_vars; rfl

theorem taken_eq (A : Choice) : c.taken A = takenBy c.N.D A := by
  cases c; subst_vars; rfl

theorem labels_eq : c.labels = (slotLabelled c.N.D).map (·.1) ++
    (VE.NormDefaults.Admission.fillLabelled (supU c.N)).map (·.1) := by
  cases c; subst_vars; rfl

/-- `bindCertX` on the case's values: the certificate bound to the source environment and to `premisesX (supU N)
    (slotUnder N.D A ++ supX N) (sup N.D).2` followed by the request's own premises (D14, `bind_eq`). -/
def bind (A : Choice) (own : List Json) (conclusion j : Json) : Except String VE.Tableau.Certificate := do
  let cert ← VE.CertificateWire.decodeCertificate j
  VE.Route.Wire.bindingOk (VE.NormDefaults.Wire.profilesOf c.x.r.b.a.re.lowerJson) (← c.canon)
    ((c.premises A []).map VE.NormDefaults.Wire.enc ++ own) conclusion cert.environment_id cert.premise_meaning_ids
    cert.conclusion_meaning_id
  pure cert

theorem bind_eq (A : Choice) (own : List Json) (conclusion j : Json) :
    c.bind A own conclusion j = VE.NormDefaults.Wire.bindCertX c.x.r.b.a.re.lowerJson (supU c.N)
      (slotUnder c.N.D A ++ supX c.N) (sup c.N.D).2 own conclusion j := by
  have h := c.premises_eq A []
  simp only [List.append_nil] at h
  unfold bind VE.NormDefaults.Wire.bindCertX
  rw [h]; cases c; subst_vars; rfl

/-- An accepted conflict answer is `readings_wire_sd_conflict_sound`'s hypothesis on the case's replay. -/
theorem free_sound (A : Choice) (hA : ∀ z ∈ A, (candidate c.N.D z.1 z.2).isSome)
    (certs : List (Option VE.Tableau.Certificate)) (h : c.free A certs = true) :
    ∀ ch, Compatible c.N.D ch → (∀ z ∈ A, z ∈ ch) →
      VE.NormDefaults.Wire.ConflictFreeX.{0} (choiceU c.N ch) (choiceX c.N ch) :=
  readings_wire_sd_conflict_sound c.x A hA certs (c.free_eq A certs ▸ h)

/-- A certificate accepted on `premises` is `supCertificateCheckSD`'s, the hypothesis of `readings_wire_sd_all_sound`. -/
theorem premises_check (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (h : VE.Tableau.checkCertificate (envAt c.F (size c.F)) (c.premises A Γ) φ cert = true) :
    supCertificateCheckSD c.N A Γ φ cert = true := by
  rw [premises_eq] at h; cases c; subst_vars; exact h

end SDCase

def sdTick (f : SDCount → SDCount) : SDM Unit := modify f

/-- The queries' premises and conclusion over `sharedEnvSD N` (DRI item 1), typed by the decoders (`choiceFormulas`). -/
def sdShared (E : VE.Environment) (j : Json) : Except String (List VE.Formula × VE.Formula) :=
  choiceFormulas E (if j.getObjValD "premises" == .null then j.setObjVal! "premises" (.arr #[]) else j)

/-- The assumed readings: candidates, and taken by a checked choice. -/
def sdAssumed (c : SDCase) (j : Json) : Except String Choice := do
  let ⟨A, _⟩ ← decodeAssumed c.N.D (j.getObjValD "assumed")
  unless c.taken A do throw (untakenText c.N.D A)
  pure A

/-- A base model of the superposed vocabulary (`decodeSupModel`, on the case's vocabulary) and its `filling`. -/
def sdModel (c : SDCase) (j : Json) :
    Except String (VE.FiniteModel Entity × VE.NormDefaults.FiniteFill c.U Entity) := do
  let data ← VE.Bridge.decodeModelData c.v (j.getObjValD "model")
  unless data.valid c.v do throw "model is not semantically admissible"
  pure (data.toModel, ← VE.NormDefaults.Wire.decodeFilling c.U data.toModel (j.getObjValD "filling"))

/-- The superposed proofs a piece's answer replays: one per conflict certificate, then the query's. The labelled
    middle each replays is the slot, `supX` and `Fill_T` (`A`'s atoms after the slot), so `Fill_T` is no tail. -/
def sdProofs (c : SDCase) (certs : List (Option VE.Tableau.Certificate))
    (query : Option (List VE.Formula × VE.Formula × VE.Tableau.Certificate)) : List SupProof :=
  (c.ts.zip certs).filterMap (fun (t, k) => k.map (fun cert => ⟨envAt c.F 0, c.bgb, [], VE.Norms.targetConclusion t, cert⟩)) ++
  query.toList.map (fun (Γ, φ, cert) => ⟨envAt c.F (size c.F), c.bg, c.el ++ (c.S.2 ++ Γ), φ, cert⟩)

/-- The conflict certificates of a request and their one check under `A` (a scope reads it once for all its pieces). -/
def sdFree (c : SDCase) (A : Choice) (j : Json) : SDM (List (Option VE.Tableau.Certificate) × Bool) := do
  let certs := decodeConflictCertsFor c.ts (j.getObjValD "conflict_certificates")
  sdTick fun k => { k with checks := k.checks + 1 }
  pure (certs, c.free A certs)

abbrev Free := Option (List (Option VE.Tableau.Certificate) × Bool)

/-! ## `readings-conflict` -/

def sdWitness (id : String) (c : SDCase) (A : Choice) (w : Json) : SDM Json := do
  let (M, G) ← sdModel c w
  unless VE.Norms.backgroundValid c.U.D M && c.fp.all (fun a => a.eval (M.withFill G) []) &&
      (c.slotX A).all (fun a => a.eval (M.withFill G) []) do
    throw (VE.Route.Wire.invalidModel "readings background")
  let name ← VE.Bridge.stringField w "target"
  let ids ← VE.Bridge.strings (w.getObjValD "tuple")
  let some t := c.ts.find? (·.1 == name) | throw s!"InvalidInput: unknown conflict target {name}"
  let tuple := t.2.1.zip ids
  unless ids.length == t.2.1.length && VE.Bridge.tupleCheck M t.2.1 tuple do
    throw "InvalidInput: witness tuple has the wrong length or sort"
  sdTick fun k => { k with checks := k.checks + 1 }
  let conflict := t.2.2.eval (M.withFill G) (VE.Norms.tupleVal tuple)
  pure (okWith id [("verdict", .str (if conflict then "CONFLICT" else "UNKNOWN")), ("target", .str t.1),
    ("assumed", choiceJson A), ("choice", choiceJson (encodedChoice c.N.D M))])

/-- The conflict answer and the proofs it rests on: one check of the targets' certificates over the case's values. -/
def sdConflictCore (id : String) (c : SDCase) (j : Json) (pre : Free := none) : SDM (Json × List SupProof) := do
  let A ← sdAssumed c j
  if (j.getObjVal? "witness").toBool then return (← sdWitness id c A (j.getObjValD "witness"), [])
  let (certs, free) ← match pre with | some p => pure p | none => sdFree c A j
  pure (okWith id [("verdict", .str (if free then "CONFLICT-FREE" else "UNKNOWN")), ("assumed", choiceJson A),
    ("targets", toJson (c.ts.map (·.1))), ("reading_premises", toJson c.labels)], sdProofs c certs none)

/-! ## `readings-certificate` and `readings-model` -/

/-- `accepted` is the conflict status under `assumed` and the certificate, bound to `premisesX (supU N)
    (slotUnder N.D A ++ supX N) (sup N.D).2` and the request's own premises (`SDCase.bind_eq`: `bindCertX`) and
    checked on the same list with the request's premises after it (`SDCase.premises_check`: D14). -/
def sdCertificateCore (id : String) (c : SDCase) (j : Json) (pre : Free := none) : SDM (Json × List SupProof) := do
  let A ← sdAssumed c j
  let (Γ, φ) ← sdShared c.envQ j
  let own := match j.getObjValD "premises" with | .arr xs => xs.toList | _ => []
  let cert ← c.bind A own (j.getObjValD "conclusion") (← j.getObjVal? "certificate")
  let (certs, free) ← match pre with | some p => pure p | none => sdFree c A j
  let valid := VE.Tableau.checkCertificate (envAt c.F (size c.F)) (c.premises A Γ) φ cert
  pure (okWith id [("accepted", .bool (free && valid)), ("conflict_free", .bool free), ("valid", .bool valid),
    ("assumed", choiceJson A), ("reading_premises", toJson c.labels)], sdProofs c certs (some (Γ, φ, cert)))

/-- `valid` is the model check with `localFree` (14.3: a reported model has no conflict at any tuple); the first
    failing premise is named by its label, a soft premise by the choice label it is the image of under the choice
    the model encodes (`labelImage`; `null` for none), never by its superposed label. -/
def sdModelRun (id : String) (c : SDCase) (j : Json) : SDM Json := do
  let A ← sdAssumed c j
  let (Γ, φ) ← sdShared c.envQ j
  let (M, G) ← sdModel c j
  let res := c.model A M G (c.S.2 ++ Γ) φ
  let ch := encodedChoice c.N.D M
  let failing := (c.slot ++ A.map (fun x => (s!"readings:{x.1}:{x.2}", choiceAtom c.N.D x.1 x.2)) ++ c.XL ++ c.FL).find?
    (fun x => !x.2.eval (M.withFill G) [])
  let shown := failing.bind fun l =>
    if c.XL.any (·.1 == l.1) then ((labelImage c.N ch).find? (·.2 == l.1)).map (·.1) else some l.1
  pure (okWith id [("valid", .bool (res.1 && c.localFree M G)), ("conclusion_value", .bool res.2),
    ("first_failing", match shown with | some l => .str l | none => .null),
    ("assumed", choiceJson A), ("choice", choiceJson ch)])

/-- The three kinds on one routed case; any other kind is refused as `runSDKind` refuses it. -/
def runSDSup (id kind : String) (c : SDCase) (j : Json) : SDM Json :=
  if kind == "readings-conflict" then (·.1) <$> sdConflictCore id c j
  else if kind == "readings-certificate" then (·.1) <$> sdCertificateCore id c j
  else if kind == "readings-model" then sdModelRun id c j
  else throw s!"UnsupportedProfile: case kind {kind} is not available on the readings route"

/-! ## The verdict scopes (14.11 rows four and five) -/

/-- `sdShown`, read through label images computed once for the scope. -/
def shownWith (images : List (List (String × String))) (used : List String) : List String :=
  VE.SoftNorms.dedup (images.flatMap (fun im => im.filterMap (fun p => if used.contains p.2 then some p.1 else none)))

theorem shownWith_eq (N : NDoc) (A : Choice) (used : List String) :
    shownWith (((checkedChoices N.D).filter (fun c => A.all (c.contains ·))).map (labelImage N)) used =
      sdShown N A used := by
  simp [shownWith, sdShown, List.flatMap_map]

namespace SDCase
variable (c : SDCase)

/-- The label images of the checked choices taking `A`, read once by a scope (`images_shown`: `sdShown`). -/
def images (A : Choice) : List (List (String × String)) :=
  (c.checked.filter (fun ch => A.all (ch.contains ·))).map (labelImage c.N)

theorem images_shown (A : Choice) (used : List String) : shownWith (c.images A) used = sdShown c.N A used := by
  cases c; subst_vars; exact shownWith_eq _ _ _

/-- The labelled premises a piece's labels are read over (14.11): the slot, `supX` and `Fill_T`. -/
def middle : VE.Compose.Labelled := c.slot ++ c.XL ++ c.FL

/-- A replay of `ps` with `m` for the labelled premises, `A`'s atoms after the slot. -/
def replay (A : Choice) (ps : List SupProof) (m : List VE.Formula) : Bool :=
  ps.all (fun q => q.check (m.take c.slot.length ++ atoms c.N.D A ++ m.drop c.slot.length))

theorem fill_formulas : c.FL.map (·.2) = c.fp := by
  cases c; subst_vars
  exact List.map_snd_zip (by simp [VE.NormDefaults.Admission.fillLabels, VE.NormDefaults.fillPremises])

theorem middle_full (A : Choice) : ((c.middle.map (·.2)).take c.slot.length ++ atoms c.N.D A ++
    (c.middle.map (·.2)).drop c.slot.length) = c.slotX A ++ c.fp := by
  have hf := c.fill_formulas
  have hx := c.hX
  simp only [middle, slotX, List.map_append, VE.Compose.Labelled.formulas, List.append_assoc]
  rw [List.take_append_of_le_length (by simp), List.drop_append_of_le_length (by simp)]
  simp [hf, hx, List.take_of_length_le, List.drop_of_length_le]

/-- With nothing blanked, a query piece's replay is its own check (`premises`, 14.11's last row but one). -/
theorem replay_query (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate) :
    c.replay A (sdProofs c [] (some (Γ, φ, cert))) (c.middle.map (·.2)) =
      VE.Tableau.checkCertificate (envAt c.F (size c.F)) (c.premises A Γ) φ cert := by
  simp only [replay, c.middle_full A]
  simp [sdProofs, SupProof.check, premises, List.append_assoc]

/-- With nothing blanked, a conflict piece's replay is its accepted certificates' checks (`free`). -/
theorem replay_conflict (A : Choice) (certs : List (Option VE.Tableau.Certificate)) :
    c.replay A (sdProofs c certs none) (c.middle.map (·.2)) = (c.ts.zip certs).all (fun x => match x.2 with
      | some k => VE.Tableau.checkCertificate (envAt c.F 0) (c.bgb ++ c.slotX A ++ c.fp) (VE.Norms.targetConclusion x.1) k
      | none => true) := by
  simp only [replay, c.middle_full A]
  simp [sdProofs, SupProof.check, List.append_assoc]
  congr; funext x; rcases x with ⟨t, _ | k⟩ <;> simp

/-- A piece's labels (14.11, `usedLabels`): those its proofs still replay without, dropped greedily. -/
def usedOf (A : Choice) (ps : List SupProof) : List String :=
  if ps.isEmpty then [] else usedLabels (c.replay A ps) [] c.middle []

/-- The labels a piece shows still replay its proofs (`greedy_replay_sound`), when its own check passed. -/
theorem usedOf_replays (A : Choice) (ps : List SupProof) (h : c.replay A ps (c.middle.map (·.2)) = true) :
    c.replay A ps (blank c.middle (c.usedOf A ps)) = true := by
  unfold usedOf
  split
  · rename_i he; simp [replay, List.isEmpty_iff.mp he]
  · exact greedy_replay_sound _ _ h

/-- A piece's labels as shown: the slot's as they are, the soft premises' by their choice labels through the scope's
    images, then `Fill_T`'s (`relabel_shown`: `sdShown`). -/
def relabel (images : List (List (String × String))) (ls : List String) : List String :=
  ls.filter (fun l => !(c.XL.map (·.1)).contains l && !(c.FL.map (·.1)).contains l) ++
    shownWith images (ls.filter (c.XL.map (·.1)).contains) ++ ls.filter (c.FL.map (·.1)).contains

theorem relabel_shown (A : Choice) (ls : List String) : c.relabel (c.images A) ls =
    ls.filter (fun l => !(c.XL.map (·.1)).contains l && !(c.FL.map (·.1)).contains l) ++
      sdShown c.N A (ls.filter (c.XL.map (·.1)).contains) ++ ls.filter (c.FL.map (·.1)).contains := by
  simp only [relabel, images_shown]

end SDCase

/-- One scope under `A`: each piece of `e` on the case's values, the conflict certificates decoded and checked once
    for all of them (`sdFree`); `labelImage` once for the scope, at its first accepted piece (none if no piece is);
    each accepted piece's labels (`usedOf`) shown by choice labels (`relabel_shown`: `sdShown`). A refused piece is
    noted, never a negative verdict. -/
def sdScope (c : SDCase) (A : Choice) (Γ φ e : Json) : SDM SupScope := do
  let packages := (pieceOf e "conflict").getD (Json.mkObj [])
  let mut notes : List PieceNote := []
  let mut used : List (String × List String) := []
  let mut images : Option (List (List (String × String))) := none
  let mut encoded : List (String × Choice) := []
  let mut st : List (String × Bool) := []
  let mut cf : Free := none
  for name in ["conflict", "witness", "certificate", "countermodel", "unsat", "model"] do
    if let some p := pieceOf e name then
      let query := name == "certificate" || name == "unsat"
      let body := if query then p.setObjVal! "conflict_certificates" (packages.getObjValD "conflict_certificates")
        else p
      let plain := name == "model" || name == "unsat"
      let body := supPieceCase A (if plain then .arr #[] else Γ) (if plain then .null else φ) body
      if cf.isNone && (name == "conflict" || query) then cf := some (← sdFree c A packages)
      let res ← attempt (if name == "conflict" || name == "witness" then sdConflictCore "readings-verdicts" c body cf
        else if query then sdCertificateCore "readings-verdicts" c body cf
        else (·, []) <$> sdModelRun "readings-verdicts" c body)
      match res with
      | .error err => notes := notes ++ [{ name := name, accepted := false, error := some err }]
      | .ok (answer, proofs) =>
        let ok := if name == "conflict" then answer.getObjValD "verdict" == .str "CONFLICT-FREE"
          else if name == "witness" then answer.getObjValD "verdict" == .str "CONFLICT"
          else if query then answer.getObjValD "accepted" == .bool true
          else answer.getObjValD "valid" == .bool true && answer.getObjValD "conclusion_value" == .bool false
        st := st ++ [(name, ok)]
        if ok && images.isNone then
          sdTick fun k => { k with images := k.images + 1 }
          images := some (c.images A)
        if ok && (name == "conflict" || query) then sdTick fun k => { k with replays := k.replays + 1 }
        let labels := if ok then c.relabel (images.getD []) (c.usedOf A proofs) else []
        used := used ++ [(name, labels)]
        let shown := if ok && (name == "witness" || name == "countermodel" || name == "model") then
          some (if name == "witness" then (p.getObjValD "witness").getObjValD "model" else p.getObjValD "model")
          else none
        notes := notes ++ [{ name := name, accepted := ok, shown := shown, conditionalOn := labels }]
        if shown.isSome then encoded := encoded ++ [(name, jchoice (answer.getObjValD "choice"))]
  let on (n : String) : Bool := st.any (fun (x : String × Bool) => x.1 == n && x.2)
  let cs : ChoiceResult := if on "conflict" then .free else if on "witness" then .conflict else .unknown
  let qs : ChoiceResult := if on "certificate" then .proved else if on "countermodel" then .refuted else .unknown
  let ps : ChoiceResult := if on "unsat" then .inconsistent else if on "model" then .model else .unknown
  return { info := ⟨A, cs, qs, ps, notes⟩, encoded := encoded, used := used }

end VE.Readings.Run
