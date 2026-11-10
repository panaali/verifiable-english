import VE.Readings.SoftSupWire

/-! sc-11c: the soft runners on a superposed soft document (docs/spec/rd-9-soft-chain.md 14.3, 14.11): `readings-conflict`,
`-certificate`, `-model` and the scope of a `readings-verdicts` case. Nothing dispatches here yet (sc-11b switches
`runSDKind`); `SoftSupRunExamples.lean` runs them.

A case is admitted once (`admitSDOf`) and routed once (`sdCaseOf`). The route check reads the values 14.11's third
row names, each computed there once: `sup N.D`, `supU N`, the checked choices, `softXL N (sup N.D).1`; on a
superposed case `fill (supU N)`, `Fill_T`, the targets and the environments follow, and every piece reads them from
the case (`SDCase`). No piece admits or routes again: the norms chain's `x.run`, which replays per piece, is not copied.
At most 64 choices the per-choice texts are admission's result (`sdCheck_of_admitted`); past 64 they run once, after
the count and the work limit. Each answer's check equals the one its `readings_wire_sd_*_sound` theorem reads
(`SDCase.free_eq`, `SDCase.premises_eq`, `SDCase.model_eq`, `SDCase.local_eq`), so the theorem applies to the case's
`SupReplaySD`. A query certificate is bound to `premisesX` by `bindCertX` (D14). `SDCount` is W-13's and W-14's
measure: admissions, route checks, label images, label replays and conflict checks. -/
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
  checked : List Choice
  envQ : VE.Environment
  v : VE.Bridge.Vocabulary
  hS : S = sup x.r.N.D
  hU : U = supU x.r.N
  hF : F = fill U
  hslot : slot = slotLabelled x.r.N.D
  hXL : XL = softXL x.r.N S.1
  hX : X = XL.map (·.2)
  hfp : fp = VE.NormDefaults.fillPremises U
  hFL : FL = (VE.NormDefaults.Admission.fillLabels U).zip fp
  hts : ts = targets F
  hc : checked = checkedChoices x.r.N.D
  hQ : envQ = sharedEnvSD x.r.N
  hv : v = supVocabulary x.r.b.a.re x.r.b.D

/-- The route of an admitted case, read once (`routeSD_superposed_iff`): the work limit before any choice's text,
    and at most 64 choices no text at all (`sdCheck_of_admitted`). Off the superposed row it is `refusal`. -/
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
    let XL := softXL N S.1
    let work := checked.length * (XL.length +
      (S.1.soft.T.nodes.map (fun M => (M.guard :: M.carveOuts).map VE.Bridge.formulaNodes)).flatten.sum)
    if h : routeOf true N.D = .enumerated ∧ superposable N.D = true ∧ VE.NormDefaults.WellFormedU U = true ∧
        checked.length ≤ maxChoiceChecks ∧ work ≤ maxSdCheckWork ∧
        (checked.length ≤ maxChoices ∨ checked.all (fun c => (sdChoiceText r.b.a.re N c).isNone) = true) then
      if hs : (choices N.D).isEmpty = false then
        have hck : sdChecked r.b.a.re N = true := by
          rcases h.2.2.2.2.2 with hle | hall
          · exact sdCheck_of_admitted b r hadm (superposable_supReady h.2.1) hle h.2.2.2.2.1
          · simp only [sdChecked, Bool.and_eq_true, decide_eq_true_eq]
            exact ⟨⟨h.2.2.2.1, h.2.2.2.2.1⟩, hall⟩
        have hr : routeSD r.b.a.re N = .superposed :=
          (routeSD_superposed_iff _ _).mpr ⟨h.1, by simp [sdSuperposable, h.2.1, h.2.2.1, supU, U, S], hck⟩
        let F := fill U
        let fp := VE.NormDefaults.fillPremises U
        let X := XL.map (·.2)
        pure ⟨⟨r, hr, hs⟩, S, U, F, slotLabelled N.D, XL, X, fp, (VE.NormDefaults.Admission.fillLabels U).zip fp,
          targets F, checked, sharedEnvSD N, supVocabulary r.b.a.re r.b.D,
          rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
      else throw (unsatText N.D)
    else throw (refusal N)

namespace SDCase
variable (c : SDCase)

def N : NDoc := c.x.r.N
def slotX (A : Choice) : List VE.Formula := c.slot.formulas ++ atoms c.N.D A ++ c.X
def taken (A : Choice) : Bool := c.checked.any (fun ch => A.all (ch.contains ·))
def labels : List String := c.slot.map (·.1) ++ c.FL.map (·.1)
def sp : superposable c.x.r.b.D = true := c.x.r.hN ▸ c.x.parts.1

/-- `conflictFreeCheckX (supU N) (slotUnder N.D A ++ supX N)` on the case's values. -/
def free (A : Choice) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  c.ts.length == certs.length && (c.ts.zip certs).all (fun (t, k) => match k with
    | some k => VE.Tableau.checkCertificate (envAt c.F 0) (VE.Norms.backgroundBase c.F ++ c.slotX A ++ c.fp)
        (VE.Norms.targetConclusion t) k
    | none => false)

/-- `premisesX (supU N) (slotUnder N.D A ++ supX N) ((sup N.D).2 ++ Γ)`, D14's premises, on the case's values. -/
def premises (A : Choice) (Γ : List VE.Formula) : List VE.Formula :=
  VE.Norms.background c.F ++ c.slotX A ++ c.fp ++ VE.Norms.elaborate c.F.T ++ (c.S.2 ++ Γ)

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

/-- The queries' premises and conclusion over `sharedEnvSD N` (DRI item 1), as `decodeShared` types them. -/
def sdShared (E : VE.Environment) (j : Json) : Except String (List VE.Formula × VE.Formula) := do
  let (Γ, φ) ← choiceFormulas E (if j.getObjValD "premises" == .null then j.setObjVal! "premises" (.arr #[]) else j)
  unless Γ.all (fun a => a.check E []) && φ.check E [] do throw "ill-typed or unbound formula"
  pure (Γ, φ)

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

/-- The superposed proofs a piece's answer replays: one per conflict certificate, then the query's. -/
def sdProofs (c : SDCase) (certs : List (Option VE.Tableau.Certificate))
    (query : Option (List VE.Formula × VE.Formula × VE.Tableau.Certificate)) : List SupProof :=
  (c.ts.zip certs).filterMap (fun (t, k) => k.map (fun cert =>
    ⟨envAt c.F 0, VE.Norms.backgroundBase c.F, c.fp, VE.Norms.targetConclusion t, cert⟩)) ++
  query.toList.map (fun (Γ, φ, cert) =>
    ⟨envAt c.F (size c.F), VE.Norms.background c.F, c.fp ++ VE.Norms.elaborate c.F.T ++ (c.S.2 ++ Γ), φ, cert⟩)

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
def sdConflictCore (id : String) (c : SDCase) (j : Json) : SDM (Json × List SupProof) := do
  let A ← sdAssumed c j
  if (j.getObjVal? "witness").toBool then return (← sdWitness id c A (j.getObjValD "witness"), [])
  let certs := decodeConflictCertsFor c.ts (j.getObjValD "conflict_certificates")
  sdTick fun k => { k with checks := k.checks + 1 }
  let free := c.free A certs
  pure (okWith id [("verdict", .str (if free then "CONFLICT-FREE" else "UNKNOWN")), ("assumed", choiceJson A),
    ("targets", toJson (c.ts.map (·.1))), ("reading_premises", toJson c.labels)], sdProofs c certs none)

/-! ## `readings-certificate` and `readings-model` -/

/-- `accepted` is the conflict status under `assumed` and the certificate, bound by `bindCertX` to the case's
    regenerated premises `premisesX (supU N) (slotUnder N.D A ++ supX N) (sup N.D).2` and the request's own, checked
    on `c.premises A Γ` (D14, `SDCase.premises_check`). -/
def sdCertificateCore (id : String) (c : SDCase) (j : Json) : SDM (Json × List SupProof) := do
  let A ← sdAssumed c j
  let (Γ, φ) ← sdShared c.envQ j
  let own ← match j.getObjValD "premises" with
    | .null => pure []
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: premises must be an array"
  let cert ← VE.NormDefaults.Wire.bindCertX c.x.r.b.a.re.lowerJson c.U (c.slotX A) c.S.2 own (j.getObjValD "conclusion")
    (← j.getObjVal? "certificate")
  let certs := decodeConflictCertsFor c.ts (j.getObjValD "conflict_certificates")
  sdTick fun k => { k with checks := k.checks + 1 }
  let free := c.free A certs
  let valid := VE.Tableau.checkCertificate (envAt c.F (size c.F)) (c.premises A Γ) φ cert
  pure (okWith id [("accepted", .bool (free && valid)), ("conflict_free", .bool free), ("valid", .bool valid),
    ("assumed", choiceJson A), ("reading_premises", toJson c.labels)], sdProofs c certs (some (Γ, φ, cert)))

def sdModelRun (id : String) (c : SDCase) (j : Json) : SDM Json := do
  let A ← sdAssumed c j
  let (Γ, φ) ← sdShared c.envQ j
  let (M, G) ← sdModel c j
  let res := c.model A M G (c.S.2 ++ Γ) φ
  let failing := (c.slot ++ A.map (fun x => (s!"readings:{x.1}:{x.2}", choiceAtom c.N.D x.1 x.2)) ++ c.XL ++ c.FL).find?
    (fun x => !x.2.eval (M.withFill G) [])
  pure (okWith id [("valid", .bool res.1), ("conclusion_value", .bool res.2),
    ("local_free", .bool (c.localFree M G)), ("first_failing", match failing with | some l => .str l.1 | none => .null),
    ("assumed", choiceJson A), ("choice", choiceJson (encodedChoice c.N.D M))])

/-- The three kinds on one routed case. -/
def runSDSup (id kind : String) (c : SDCase) (j : Json) : SDM Json :=
  if kind == "readings-conflict" then (·.1) <$> sdConflictCore id c j
  else if kind == "readings-certificate" then (·.1) <$> sdCertificateCore id c j
  else sdModelRun id c j

/-! ## The verdict scopes (14.11 rows four and five) -/

/-- `sdShown`, read through label images computed once for the scope. -/
def shownWith (images : List (List (String × String))) (used : List String) : List String :=
  VE.SoftNorms.dedup (images.flatMap (fun im => im.filterMap (fun p => if used.contains p.2 then some p.1 else none)))

theorem shownWith_eq (N : NDoc) (A : Choice) (used : List String) :
    shownWith (((checkedChoices N.D).filter (fun c => A.all (c.contains ·))).map (labelImage N)) used =
      sdShown N A used := by
  simp [shownWith, sdShown, List.flatMap_map]

/-- One scope under `A`: each piece of `e` on the case's values; `usedLabels` per accepted piece, over the slot,
    `supX` and `Fill_T`; then, only when a piece was accepted, `labelImage` once for the scope, so each soft premise
    is shown by its choice labels (`shownWith_eq`). A refused piece is noted, never a negative verdict. -/
def sdScope (c : SDCase) (A : Choice) (Γ φ e : Json) : SDM SupScope := do
  let packages := (pieceOf e "conflict").getD (Json.mkObj [])
  let mut notes : List PieceNote := []
  let mut raw : List (String × List String) := []
  let mut encoded : List (String × Choice) := []
  let mut st : List (String × Bool) := []
  let L := c.slot ++ c.XL ++ c.FL
  for name in ["conflict", "witness", "certificate", "countermodel", "unsat", "model"] do
    if let some p := pieceOf e name then
      let query := name == "certificate" || name == "unsat"
      let body := if query then p.setObjVal! "conflict_certificates" (packages.getObjValD "conflict_certificates")
        else p
      let plain := name == "model" || name == "unsat"
      let body := supPieceCase A (if plain then .arr #[] else Γ) (if plain then .null else φ) body
      let res ← attempt (if name == "conflict" || name == "witness" then sdConflictCore "readings-verdicts" c body
        else if query then sdCertificateCore "readings-verdicts" c body
        else (·, []) <$> sdModelRun "readings-verdicts" c body)
      match res with
      | .error err => notes := notes ++ [{ name := name, accepted := false, error := some err }]
      | .ok (answer, proofs) =>
        let ok := if name == "conflict" then answer.getObjValD "verdict" == .str "CONFLICT-FREE"
          else if name == "witness" then answer.getObjValD "verdict" == .str "CONFLICT"
          else if query then answer.getObjValD "accepted" == .bool true
          else answer.getObjValD "valid" == .bool true && answer.getObjValD "conclusion_value" == .bool false &&
            answer.getObjValD "local_free" == .bool true
        st := st ++ [(name, ok)]
        let mut used := []
        if ok && !proofs.isEmpty then
          sdTick fun k => { k with replays := k.replays + 1 }
          used := usedLabels (fun m => proofs.all (fun q => q.check (m.take c.slot.length ++ atoms c.N.D A ++
            m.drop c.slot.length))) [] L []
        raw := raw ++ [(name, used)]
        let shown := if ok && (name == "witness" || name == "countermodel" || name == "model") then
          some (if name == "witness" then (p.getObjValD "witness").getObjValD "model" else p.getObjValD "model")
          else none
        notes := notes ++ [{ name := name, accepted := ok, shown := shown }]
        if shown.isSome then encoded := encoded ++ [(name, jchoice (answer.getObjValD "choice"))]
  let mut images := []
  if st.any (·.2) then
    sdTick fun k => { k with images := k.images + 1 }
    images := (c.checked.filter (fun ch => A.all (ch.contains ·))).map (labelImage c.N)
  let soft := c.XL.map (·.1)
  let used := raw.map (fun (n, ls) => (n, ls.filter (fun l => !soft.contains l && !(c.FL.map (·.1)).contains l) ++
    shownWith images (ls.filter soft.contains) ++ ls.filter (c.FL.map (·.1)).contains))
  let noted := notes.map (fun n => { n with conditionalOn := ((used.find? (·.1 == n.name)).map (·.2)).getD [] })
  let on (n : String) := (st.find? (·.1 == n)).map (·.2) |>.getD false
  let cs : ChoiceResult := if on "conflict" then .free else if on "witness" then .conflict else .unknown
  let qs : ChoiceResult := if on "certificate" then .proved else if on "countermodel" then .refuted else .unknown
  let ps : ChoiceResult := if on "unsat" then .inconsistent else if on "model" then .model else .unknown
  return { info := ⟨A, cs, qs, ps, noted⟩, encoded := encoded, used := used }

end VE.Readings.Run
