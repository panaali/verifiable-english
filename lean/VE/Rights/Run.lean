import VE.Rights.Admission
import VE.SoftNorms.Run

/-! The `ve_rights_route` executable (docs/spec/rights.md 9.4), invoked as
`lean/.lake/build/bin/ve_rights_route <cases.json|->`. Each case is
`{"id", "environment", "kind", "document", ...}`; a `rights@0` environment must also enable
`soft-norms@0` and `norms@0`; `document` is the array of unit contents of 3.2.

* `rights-elaborate`: → `environment_prime` (`E″′`), `generated` (each rights-generated
  predicate with its source keys), `lines` (per instance: right, source and instance kind,
  rule name, predicate, holder slot, bearer, node), `limitations` (the labelled `Lim_D`),
  `bars`, `derived`, `order`, `background` (with the `soft` and `rights` slots), `premises`,
  `colliding_pairs`, `conflict_targets`, `narrowings` (per line: each mechanism and its
  licence without certificates), `distinction` (per right-derived predicate), `fragment`,
  `warnings`; or the shared diagnostic.
* `rights-projections`: `model` (a finite base model over `E″′_base` passing
  `Background_base″`) and optionally `holder` / `bearer` → `rights_of`, `duties_of`: the
  selecting line instances with their tuples.
* `rights-scope`: `certificates` (scope target `<rule>:<mechanism>` ↦ package) → `findings`
  and, per mechanism, its licence and the certification target `∀x̄. cond_n° → limpack_N`
  (`conclusion`) a package must prove (`Wire.rights_wire_scope_sound`).
* `rights-conflict`: `packages` (target ↦ package over `Background_base″`) → `CONFLICT-FREE`
  with `conditional_on`, or `UNKNOWN` (`Wire.rights_wire_conflict_sound`); or `witness` →
  `CONFLICT`, classified (`Wire.rights_wire_conflict_witness_sound`).
* `rights-bar`: rule reading → per right-derived permission predicate: the barred right
  lines, the blocked default rules (on `m` or `require` on its dual) and the strict rules
  that are composition candidates (4.7); without an overlap witness no conflict is asserted.
  Query reading → per predicate the
  target `∀x̄. aimed_m(x̄) → ¬m(x̄)` and, when a certificate is supplied, whether it is entailed.
* `rights-certificate`: `premises`, `conclusion`, `certificate` bound to
  `background″ ++ layer premises ++ premises` over `E″′` → `valid`, `conditional_on`
  (`Wire.rights_wire_acceptance`).
* `admission`: a W2 document with active rights units and exact regenerated leaves.
* A case without a rights construct is delegated unchanged to soft's `Run.runCase`. -/
namespace VE.Rights.Run
open Lean
open VE.Norms
open VE.SoftNorms (SoftNode soften)
open VE.Rights.Wire
open VE.SoftNorms.Wire (enc)

/-- A rights construct: the `rights@0` profile, the vocabulary's `rights` block, a `rights-*`
case kind, or a rights unit in the document. -/
def usesRightsPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let profile := match env.getObjValD "profiles" with
    | .arr ps => ps.toList.contains (.str rightsProfile)
    | _ => false
  let block := ((env.getObjValD "vocabulary").getObjVal? "rights").toBool
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "rights-"
    | _ => false
  let rightsUnit (u : Json) := ["right", "right_lines", "limitation", "bar"].any (fun k => (u.getObjVal? k).toBool)
  let units := match j.getObjValD "document" with
    | .arr us => us.toList.any rightsUnit
    | d => match d.getObjValD "units" with
      | .arr us => us.toList.any (fun u => rightsUnit (u.getObjValD "content"))
      | _ => false
  profile || block || kind || units

/-! ## Regenerated outputs -/

def kindText : Kind → String
  | .claim => "claim" | .liberty => "liberty" | .immunity => "immunity" | .power => "power"

def ikindText : IKind → String
  | .claim => "claim" | .liberty => "liberty" | .immunity => "immunity"
  | .powerLiberty => "powerLiberty" | .powerRecognition => "powerRecognition"

/-- The source keys rendered beside each generated predicate name (1.6). -/
def generatedKeys (D : RightsDoc) : List Json :=
  (limKeys D).map (fun k => Json.mkObj [("name", .str (limName ((limKeys D).idxOf k + 1))),
      ("kind", .str "lim"), ("limitation", .str k.1), ("act", .str k.2)]) ++
  (condKeys D).map (fun k => Json.mkObj [("name", .str (condName ((condKeys D).idxOf k + 1))),
      ("kind", .str "cond"), ("limitation", .str k.1), ("act", .str k.2.1), ("condition", .str k.2.2)]) ++
  (if D.bars = [] then [] else (barPreds D).map (fun m => Json.mkObj [("name", .str (aimedName (barIndex D m))),
      ("kind", .str "aimed"), ("predicate", .str m)]))

def nodeJson (X : SoftNode) : Json :=
  Json.mkObj [("name", .str X.name), ("predicate", .str X.pred), ("sign", .bool X.sign),
    ("mode", .str (if X.mode == .strict then "strict" else "default")), ("guard", enc X.guard),
    ("unless", Json.arr (X.carveOuts.map enc).toArray), ("over", toJson X.over), ("hard", .bool X.hard)]

def lineJson (D : RightsDoc) (RN : String × Line) : Json :=
  Json.mkObj ([("right", .str RN.1), ("kind", .str (kindText RN.2.kind)), ("instance", .str (ikindText RN.2.ikind)),
    ("rule", .str RN.2.node.name), ("predicate", .str RN.2.node.pred), ("holder_slot", toJson (holderSlot D RN.2)),
    ("node", nodeJson (nodeOf D RN.2))] ++
    (match RN.2.bearer, RN.2.source.norm with
     | some b, some n => [("bearer", .str b), ("source_line", .str n.name)]
     | _, _ => []))

/-- The licence of a mechanism without certificates, or `none`. -/
def licence (D : RightsDoc) (N : Line) (n : Narrowing) : Option String :=
  match n with
  | .limPack => some "limitation"
  | .bar => some "bar"
  | .blockedBy M =>
    if cited D N n then some "cited" else if rightCollision D N n then some "collision"
    else if sameEffectStrict D N M then some s!"effect delivered by strict rule {M}" else none
  | _ => if cited D N n then some "cited" else if rightCollision D N n then some "collision" else none

def narrowingsJson (D : RightsDoc) (certs : List (Option VE.Tableau.Certificate)) : Json :=
  Json.arr ((linesOf D).map (fun RN => Json.mkObj [("right", .str RN.1), ("rule", .str RN.2.node.name),
    ("in_scope", .bool (D.limits.any (fun L => inScope D L RN.1 RN.2))),
    ("mechanisms", Json.arr ((narrowings D RN.2).map (fun n => Json.mkObj ([("mechanism", .str (mechText n)),
      ("target", .str (scopeTargetName RN.2 n)), ("conclusion", enc (certTarget D RN.2 n))] ++
      match licence D RN.2 n with
      | some l => [("licence", .str l)]
      | none => if certified D certs RN.2 n then [("licence", .str "certified")] else [("licence", .null)]))).toArray)])).toArray

def distinctionJson (D : RightsDoc) : Json :=
  Json.arr ((VE.SoftNorms.dedup ((linesOf D).map (·.2.node.pred))).map (fun p => Json.mkObj
    [("predicate", .str p), ("independent", .bool (independentReported D p)),
     ("hits", Json.arr ((distinctionHits D p).map (fun (N, q, c) => Json.mkObj [("rule", .str N.node.name),
        ("right", .str N.right), ("protected", .str q), ("cited", .bool c)])).toArray)])).toArray

def regenerated (D : RightsDoc) (environment : Json) : List (String × Json) :=
  let soft := VE.SoftNorms.Wire.regenerated (correlate D) environment
  [("environment_prime", (primeJsonR D environment).toOption.getD .null),
   ("generated", Json.arr (generatedKeys D).toArray),
   ("lines", Json.arr ((linesOf D).map (lineJson D)).toArray),
   ("limitations", Json.arr ((limPremisesLabelled D).map (fun (l, a) =>
      Json.mkObj [("label", .str l), ("ast", enc a)])).toArray),
   ("bars", Json.arr ((barNodes D).map nodeJson).toArray),
   ("rights_background", Json.arr ((limPremisesLabelled D).map (fun (l, a) =>
      VE.SoftNorms.Wire.bgEntry "rights" l a)).toArray),
   ("narrowings", narrowingsJson D []),
   ("distinction", distinctionJson D),
   ("findings", Json.arr ((noDistinction D).map (fun f => Json.str f.text)).toArray)] ++
  soft.filter (fun kv => kv.1 != "environment_prime")

/-! ## Projections on a finite base model -/

/-- Every typed tuple of the sorts over the model's domains. -/
def tuples (M : VE.FiniteModel VE.Bridge.Entity) : List String → List (List VE.Bridge.Entity)
  | [] => [[]]
  | s :: ss => (M.domains s).flatMap (fun x => (tuples M ss).map (x :: ·))

def projections (D : RightsDoc) (M : VE.FiniteModel VE.Bridge.Entity) : List (String × Line × List VE.Bridge.Entity) :=
  (linesOf D).flatMap (fun RN => (tuples M (sortsOf D RN.2)).filterMap (fun vs =>
    if (outcomeSubst D (selectsR D RN.2)).eval M (tupleVal vs) then some (RN.1, RN.2, vs) else none))

def entryJson (t : String × Line × List VE.Bridge.Entity) : Json :=
  Json.mkObj [("right", .str t.1), ("rule", .str t.2.1.node.name), ("instance", .str (ikindText t.2.1.ikind)),
    ("tuple", toJson (t.2.2.map (·.2)))]

def projectionsResult (src : RightsSource) (j : Json) : Except String (List (String × Json)) := do
  let ⟨M, _⟩ ← decodeModelR src (Json.mkObj [("model", j.getObjValD "model")])
  unless backgroundValidR src.D M do throw (VE.Route.Wire.invalidModel "rights background")
  let sel := projections src.D M
  let holder := (j.getObjValD "holder").getStr?.toOption
  let bearer := (j.getObjValD "bearer").getStr?.toOption
  let rightsOf := sel.filter (fun t => match holder with
    | some h => (t.2.2[holderSlot src.D t.2.1]?).map (·.2) == some h
    | none => true)
  let dutiesOf := sel.filter (fun t => dutyKind t.2.1 && match bearer with
    | some b => (t.2.2.head?).map (·.2) == some b
    | none => true)
  pure [("rights_of", Json.arr (rightsOf.map entryJson).toArray), ("duties_of", Json.arr (dutiesOf.map entryJson).toArray)]

/-! ## Premises used by a certificate -/

def rightsLabelled (D : RightsDoc) : List (String × VE.Formula) :=
  VE.SoftNorms.Wire.softLabelled (correlate D) ++ limPremisesLabelled D

/-- `Background_base″` with the labelled premise replaced by `⊤` at its position. -/
def baseWithout (D : RightsDoc) (label : String) : List VE.Formula :=
  VE.Norms.backgroundBase (soften (correlate D)) ++ (rightsLabelled D).map (fun (l, f) => if l == label then .top else f)

def conflictUses (r : RightsConflictReplay) (label : String) : Bool :=
  ((targets (soften (correlate r.src.D))).zip r.certs).any (fun (t, c) => match c with
    | some c => !VE.Tableau.checkCertificate (envAt (soften (correlate r.src.D)) 0) (baseWithout r.src.D label)
        (targetConclusion t) c
    | none => false)

def entailmentUses (r : RightsEntailmentReplay) (label : String) : Bool :=
  !VE.Tableau.checkCertificate (envAt (soften (correlate r.src.D)) (size (soften (correlate r.src.D))))
    (VE.Norms.background (soften (correlate r.src.D)) ++
      (rightsLabelled r.src.D).map (fun (l, f) => if l == label then .top else f) ++
      elaborate (soften (correlate r.src.D)).T ++ r.premises) r.conclusion r.cert

/-- The premises a result is conditional on: the open coherence labels and every limitation label. -/
def openLabels (D : RightsDoc) : List String :=
  VE.SoftNorms.Wire.openCoherence (correlate D) ++ (limPremisesLabelled D).map (·.1)

/-! ## The bar -/

def barResult (src : RightsSource) (environment document certs : Json) : List (String × Json) :=
  let D := src.D
  let C := correlate D
  let rows := (if D.bars.isEmpty then [] else barPreds D).map (fun m =>
    if ruleReading D then
      let barred := ((lineNodes D).filter (fun X => X.pred == m && X.sign)).map (·.name)
      let blocked := (C.T.nodes.filter (fun X => X.mode == .default &&
        (X.pred == m || (X.sign && VE.SoftNorms.dualPerm C X.pred == some m)))).map (·.name)
      let composition := (D.soft.T.nodes.filter (fun X => X.mode == .strict &&
        ((X.pred == m && X.sign) || (X.sign && VE.SoftNorms.dualPerm C X.pred == some m)))).map (·.name) ++
        ((lineNodes D).filter (fun X => X.mode == .strict && X.sign && VE.SoftNorms.dualPerm C X.pred == some m)).map (·.name)
      Json.mkObj [("predicate", .str m), ("aimed", .str (aimedName (barIndex D m))), ("reading", .str "rule"),
        ("barred", toJson barred), ("blocked_defaults", toJson blocked),
        ("composition_candidates", toJson composition), ("composition_conflicts", toJson ([] : List String))]
    else
      let target := bindAll (VE.SoftNorms.sortsOf D.soft m) (.implies (aimedF D m) (.not (atom m (VE.SoftNorms.sortsOf D.soft m))))
      let entailed : Option Bool := match certs.getObjVal? m with
        | .error _ => none
        | .ok cj => match VE.CertificateWire.decodeCertificate cj, primeJsonR D environment with
          | .ok c, .ok prime =>
            match VE.Route.Wire.bindingOk src.re.profiles prime
                ((backgroundR D ++ elaborate (soften C).T).map enc) (enc target)
                c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
            | .ok () => some (VE.Tableau.checkCertificate (envAt (soften C) (size (soften C)))
                (backgroundR D ++ elaborate (soften C).T) target c)
            | .error _ => some false
          | _, _ => some false
      Json.mkObj ([("predicate", .str m), ("aimed", .str (aimedName (barIndex D m))), ("reading", .str "query"),
        ("target", enc target)] ++ match entailed with
          | some b => [("entailed", .bool b)]
          | none => []))
  let _ := document
  [("bars", Json.arr rows.toArray)]

/-! ## Dispatch -/

def encodeAdmitted (id reportId : String) (res : Admission.Admitted) : Json :=
  let labels := VE.SoftNorms.Wire.openCoherence (correlate res.src.D) ++
    (limPremisesLabelled res.src.D).map (·.1)
  let conditional := labels.filter (fun l => res.report.assumptions.any (fun c => c.label == l))
  VE.Route.Wire.ok id [("admitted", .bool true), ("report", Norms.Run.reportJson res.report),
    ("report_id", .str reportId), ("kinds", Json.arr res.kinds.toArray),
    ("conditional_on", toJson conditional)]

def runAdmission (id : String) (environment document : Json) : Except String Json := do
  let res ← Admission.admitDocument environment document
  let canonical ← Norms.Wire.canonicalEnvironmentJson environment
  let envId ← VE.Route.Wire.environmentId res.src.re.profiles canonical
  let reportId ← VE.CertificateWire.digest (Norms.Run.reportDomain res.src.re.profiles)
    (Norms.Run.reportPayload envId document res.report)
  return encodeAdmitted id reportId res

def RightsAdmissionAnswer (id : String) (environment document answer : Json) : Prop :=
  ∃ res : Admission.Admitted, ∃ reportId : String,
    Admission.admitDocument environment document = .ok res ∧
    WellFormedRights res.src.D = true ∧
    answer = encodeAdmitted id reportId res ∧
    VE.Rights.Wire.primeJsonR res.src.D environment = .ok res.prime ∧
    VE.Norms.Admission.checkBindings res.src.re.profiles res.prime res.decoded = .ok () ∧
    VE.Graph.SoundReport.{0} (VE.SoftNorms.envPrime (correlate res.src.D)) res.graph res.report ∧
    (∀ w ∈ res.wires, Admission.NodeAdmitted res.src res.doc res.couplingIds w) ∧
    VE.Route.Admission.CitationsClosed res.doc res.report ∧
    VE.Route.Admission.ChoicesCompatible res.report ∧
    Admission.CouplingChoicesCompatible document res.report = true ∧
    (∀ S : VE.Structure.{0}, S.Admissible (VE.SoftNorms.envPrime (correlate res.src.D)) →
      Sat S (backgroundR res.src.D ++ elaborate (soften (correlate res.src.D)).T) →
      Sat S ((Admission.otherAssumptions res).map (·.formula)) →
      res.report.root.formula.denote S []) ∧
    ∃ canonical envId, Norms.Wire.canonicalEnvironmentJson environment = .ok canonical ∧
      VE.Route.Wire.environmentId res.src.re.profiles canonical = .ok envId ∧
      VE.CertificateWire.digest (Norms.Run.reportDomain res.src.re.profiles)
        (Norms.Run.reportPayload envId document res.report) = .ok reportId

open VE.Order.ProfileGate (bind_ok) in
theorem runAdmission_sound (id : String) (environment document answer : Json)
    (h : runAdmission id environment document = .ok answer) :
    RightsAdmissionAnswer id environment document answer := by
  unfold runAdmission at h
  obtain ⟨res, hr, h⟩ := bind_ok h
  obtain ⟨canonical, hc, h⟩ := bind_ok h
  obtain ⟨envId, he, h⟩ := bind_ok h
  obtain ⟨reportId, hd, h⟩ := bind_ok h
  cases h
  obtain ⟨hwf, hp, hb, hs, hn, hcit, hch, hcoupling⟩ :=
    Admission.admitDocument_spec environment document res hr
  exact ⟨res, reportId, hr, hwf, rfl, hp, hb, hs, hn, hcit, hch, hcoupling,
    (fun S hS hg ho => Admission.rights_wire_report_consequence environment document res hr S hS hg ho),
    canonical, envId, hc, he, hd⟩

def witnessKind (t : String × List String × VE.Formula) : String :=
  if (t.1.splitOn "->").length > 1 then s!"pair conflict on {t.1}" else s!"strict collision on {t.1}"

def runRightsKind (id kind : String) (j : Json) : Except String Json := do
  if kind == "admission" then
    return ← runAdmission id (← j.getObjVal? "environment") (← j.getObjVal? "document")
  if kind == "rights-elaborate" then
    let environment ← j.getObjVal? "environment"
    let src ← decodeRightsSource environment (j.getObjValD "document")
    return VE.Route.Wire.ok id (regenerated src.D environment)
  if kind == "rights-projections" then
    let src ← decodeRightsSource (← j.getObjVal? "environment") (j.getObjValD "document")
    return VE.Route.Wire.ok id (← projectionsResult src j)
  if kind == "rights-scope" then
    let r ← replayRightsScope j
    return VE.Route.Wire.ok id [("findings", Json.arr (r.findings.map (fun f => Json.str f.text)).toArray),
      ("licensed", .bool r.findings.isEmpty), ("narrowings", narrowingsJson r.src.D r.certs)]
  if kind == "rights-certificate" then
    let r ← replayRightsEntailment j
    let conditional := if r.valid then (openLabels r.src.D).filter (entailmentUses r) else []
    return VE.Route.Wire.ok id [("valid", .bool r.valid),
      ("background", toJson (backgroundR r.src.D).length),
      ("layers", toJson (elaborate (soften (correlate r.src.D)).T).length),
      ("conditional_on", toJson conditional)]
  if kind == "rights-bar" then
    let environment ← j.getObjVal? "environment"
    let document := j.getObjValD "document"
    let src ← decodeRightsSource environment document
    return VE.Route.Wire.ok id (barResult src environment document (j.getObjValD "certificates"))
  if kind == "rights-conflict" && (j.getObjVal? "witness").toBool then
    let ⟨src, w⟩ ← replayRightsWitness j
    let names ← VE.Bridge.strings ((j.getObjValD "witness").getObjValD "tuple")
    let situation := String.intercalate ", " names
    return VE.Route.Wire.ok id ([("verdict", .str (if w.conflict then "CONFLICT" else "UNKNOWN")),
      ("target", .str w.target.1), ("targets", toJson ((targets (soften (correlate src.D))).map (·.1))),
      ("status_text", .str (if w.conflict then s!"CONFLICT: {witnessKind w.target} at {situation}"
                            else s!"UNKNOWN: {w.target.1}, budget 10000"))] ++
      (if w.conflict then [("witness_kind", .str (witnessKind w.target))] else []))
  if kind == "rights-conflict" then
    let res ← replayRightsConflict j
    let verdict := if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN"
    let conditional := if res.conflictFree then (openLabels res.src.D).filter (conflictUses res) else []
    let coherence := conditional.filter (fun l => l.startsWith "soft:")
    let limitation := conditional.filter (fun l => l.startsWith "rights:")
    let statusText := if res.conflictFree then
      s!"CONFLICT-FREE among rules on the same act, conditional on {coherence.length} coherence premises and {limitation.length} limitation premises"
      else s!"UNKNOWN: {(firstFailure res).getD "target unspecified"}, budget 10000"
    return VE.Route.Wire.ok id ([("verdict", .str verdict), ("status_text", .str statusText),
      ("targets", toJson ((targets (soften (correlate res.src.D))).map (·.1))),
      ("conditional_on", toJson conditional)] ++
      match firstFailure res with
      | some d => if res.conflictFree then [] else [("detail", .str d)]
      | none => [])
  throw s!"UnsupportedProfile: case kind {kind} is not available on the rights route"

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if !usesRightsPath j then return ← VE.SoftNorms.Run.runCase j
  runRightsKind id kind j

open VE.Order.ProfileGate (bind_ok) in
theorem rights_wire_acceptance (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : usesRightsPath j = true) :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      RightsAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "admission" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  simp [hn] at h
  unfold runRightsKind at h
  simp at h
  obtain ⟨environment, he, h⟩ := bind_ok h
  obtain ⟨document, hd, h⟩ := bind_ok h
  have he' : j.getObjValD "environment" = environment := by
    simp only [Json.getObjValD, he]; rfl
  have hd' : j.getObjValD "document" = document := by
    simp only [Json.getObjValD, hd]; rfl
  rw [he', hd']
  exact ⟨id, hid, runAdmission_sound id environment document answer (by simpa using h)⟩

def runCaseReported (j : Json) : Json :=
  if usesRightsPath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str message)]
  else VE.SoftNorms.Run.runCaseReported j

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_rights_route [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j
      | .error message => Json.mkObj [("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.Rights.Run
