import VE.Risk.Admission
import VE.Alternatives.Run

/-! The `ve_service` mode `risk` (docs/spec/risk.md 7.3), formerly the one-shot `ve_risk_route`. Each case is
`{"id", "kind", "environment", "document", ...}` with the `alternatives` and
`risk` blocks in the environment, `risk@0`, `alternatives@0` and `norms@0`
among its profiles, and `document` = `{"norms", "units"?}` (the norm objects
and the active base units).

* `risk-elaborate` → `E_risk`, the legend, the risk slot premises, the inlined
  norm objects, alt's slot premises and followability formulas, and W1's
  regenerated order, Background, layer premises and conflict targets.
* `risk-decision` with `decision` (the decision entry) and `entries` (the
  supplied entries) → a diagnostic (with the witness case of `S ∧ ¬N` where it
  applies); or the CONFLICT witness; or the tables, statuses, worst cases,
  certified margins, record-level lines, report lines, `conditional_on` and
  `decision_record_id` (`risk_wire_scenario_sound`).
* `risk-conflict` with `packages` → CONFLICT-FREE (`risk_wire_conflict_sound`)
  or UNKNOWN; with `witness` → CONFLICT or UNKNOWN.
* `risk-followable` with `packages` and `package` → FOLLOWABLE
  (`risk_wire_followable_sound`); with `packages` and `witness` → DILEMMA
  (`risk_dilemma_witness_sound`); UNKNOWN; `not computed`.
* `risk-audit` with `log`, `decision` (`{"id", "seq"}`) and optionally
  `alternative` → Q1, Q2, the procedure lines and Q3 (`risk_wire_audit_sound`).
* `risk-certificate` → `valid`.
* `admission` → the W2 graph report bound to the complete risk source
  (`risk_wire_acceptance`), with `risk:*` and `risk:profile:<word>` leaves.
* Cases without the profile, the block or a `risk-*` kind are delegated to
  `VE.Alternatives.Run`.

Every text is a rendering of certified data (7.4). -/
namespace VE.Risk.Run
open Lean
open VE.Norms
open Wire (RiskSource decodeRiskSource)

def ok (id : String) (fields : List (String × Json)) : Json := VE.Route.Wire.ok id fields

def usesRiskPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let profile := match env.getObjValD "profiles" with
    | .arr ps => ps.toList.contains (.str "risk@0")
    | _ => false
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "risk-"
    | _ => false
  profile || (env.getObjVal? "risk").toBool || kind

/-! ## Replays with their wire theorems -/

structure DecisionReplay where
  src : RiskSource
  entry : Entry
  supplied : Log
  d : Decision
  tables : Tables
  conflict : Option ((String × List String × VE.Formula) × List VE.Bridge.Entity)
  statuses : List (String × Status)
  margin : Endpoint → Dir → String → Option Int
  recordInvalid : Endpoint → Dir → Option (Int × String)
  recordConflict : Endpoint → Dir → Option Int

def replayDecision (j : Json) : Except String DecisionReplay := do
  let src ← decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document")
  let entry ← Wire.decodeEntry (j.getObjValD "decision")
  let supplied ← Wire.decodeSupplied (j.getObjValD "entries")
  let d ← admitDecision src.R entry supplied
  validateDecision src.R d
  marginLimit src.R d
  pure ⟨src, entry, supplied, d, regenerate src.R d,
    VE.Alternatives.scenarioConflict (toAlt src.R) (decisionModel src.R d), statuses src.R d,
    scan src.R d, scanInvalid src.R d, scanConflict src.R d⟩

theorem bind_unit {ε β : Type} {x : Except ε Unit} {f : Unit → Except ε β} {b : β}
    (h : (x >>= f) = .ok b) : x = .ok () ∧ f () = .ok b := by
  obtain ⟨u, hu, hf⟩ := VE.Order.ProfileGate.bind_ok h
  cases u
  exact ⟨hu, hf⟩

/-- A raw decision replay: the input decodes to the source, the entry and the supplied entries; the record is
admitted and valid and within the candidate limit; and every reported table, status and scan is the Lean
definition's on that record. -/
theorem risk_wire_scenario_sound (j : Json) (res : DecisionReplay) (h : replayDecision j = .ok res) :
    Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
    WellFormedRisk res.src.R = true ∧
    Wire.decodeEntry (j.getObjValD "decision") = .ok res.entry ∧
    Wire.decodeSupplied (j.getObjValD "entries") = .ok res.supplied ∧
    admitDecision res.src.R res.entry res.supplied = .ok res.d ∧
    validateDecision res.src.R res.d = .ok () ∧
    marginLimit res.src.R res.d = .ok () ∧
    res.tables = regenerate res.src.R res.d ∧
    res.conflict = VE.Alternatives.scenarioConflict (toAlt res.src.R) (decisionModel res.src.R res.d) ∧
    (res.conflict = none → res.statuses = statuses res.src.R res.d) ∧
    (∀ e ∈ endpoints res.d, ∀ dir a, res.margin e dir a = scan res.src.R res.d e dir a) ∧
    (∀ e ∈ endpoints res.d, ∀ dir, res.recordInvalid e dir = scanInvalid res.src.R res.d e dir ∧
      res.recordConflict e dir = scanConflict res.src.R res.d e dir) := by
  unfold replayDecision at h
  obtain ⟨src, hs, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨entry, he, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨supplied, hsu, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨d, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨hv, h⟩ := bind_unit h
  obtain ⟨hm, h⟩ := bind_unit h
  cases h
  exact ⟨hs, src.wf, he, hsu, hd, hv, hm, rfl, rfl, fun _ => rfl, fun _ _ _ _ => rfl, fun _ _ _ => ⟨rfl, rfl⟩⟩

structure AuditReplay where
  src : RiskSource
  log : Log
  decision : DecisionRef
  alternative : String
  q12 : AuditQ12

def decodeRef (j : Json) : Except String DecisionRef := do
  unless (VE.Bridge.exactFields j ["id", "seq"]).isOk do throw "InvalidInput: risk-audit.decision"
  let id ← match j.getObjValD "id" with
    | .str s => pure s
    | _ => throw "InvalidInput: risk-audit.decision"
  let seq ← match (j.getObjValD "seq").getNat? with
    | .ok n => pure n
    | .error _ => throw "InvalidInput: risk-audit.decision"
  pure ⟨id, seq⟩

/-- The queried alternative: the case's `alternative`, else the `taken` entry naming the decision. -/
def queried (j : Json) (log : Log) (hd : DecisionRef) : Except String String :=
  match j.getObjValD "alternative" with
  | .str a => pure a
  | _ => match log.find? (fun x => x.kind == .taken && x.content.getObjValD "decision" == .str hd.id) with
    | some x => match x.content.getObjValD "alternative" with
      | .str a => pure a
      | _ => throw "InvalidInput: risk-audit.taken"
    | none => throw "InvalidInput: risk-audit.alternative"

def replayAudit (j : Json) : Except String AuditReplay := do
  let src ← decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document")
  let log ← Wire.decodeLog (j.getObjValD "log")
  let hd ← decodeRef (j.getObjValD "decision")
  let a ← queried j log hd
  pure ⟨src, log, hd, a, auditQ12 src.R log hd a⟩

theorem risk_wire_audit_sound (j : Json) (res : AuditReplay) (h : replayAudit j = .ok res) :
    Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
    Wire.decodeLog (j.getObjValD "log") = .ok res.log ∧
    res.q12 = auditQ12 res.src.R res.log res.decision res.alternative := by
  unfold replayAudit at h
  obtain ⟨src, hs, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨log, hl, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨hd, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨a, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  exact ⟨hs, hl, rfl⟩

/-! ### Packages -/

/-- The regenerated base environment the inner certificates bind (3.4): the blocks, the W6 extension, the
regulated predicates and `alternatives@0`, `risk@0`, `norms@0` removed; the generated sort, class constants
and predicates of `E_risk` added. -/
def riskBaseEnvironmentJson (R : RiskDoc) (environment : Json) (ps : List String) : Except String Json := do
  let base ← VE.Norms.Replay.baseEnvironmentJson (← Wire.riskNormsView environment ps)
  let vocab ← base.getObjVal? "vocabulary"
  let sorts ← VE.Bridge.fields (← vocab.getObjVal? "sorts")
  let preds ← VE.Bridge.fields (← vocab.getObjVal? "predicates")
  let consts ← VE.Bridge.fields (← vocab.getObjVal? "constants")
  let desc (s : String) := Json.mkObj [("description", .str s)]
  let sorts' := sorts ++ [(R.sev, desc "severity class (risk@0)")]
  let preds' := preds ++ (genPredList R).map fun (p, ss) =>
    (p, Json.mkObj [("arguments", toJson ss), ("description", .str s!"generated by risk@0: {p}")])
  let consts' := consts ++ R.classes.map fun c =>
    (c, Json.mkObj [("sort", .str R.sev), ("description", .str s!"severity class {c}")])
  pure (base.setObjVal! "vocabulary" (Json.mkObj [("sorts", Json.mkObj sorts'), ("predicates", Json.mkObj preds'),
    ("constants", Json.mkObj consts')]))

/-- A package bound to the source, or `none`: the outer binding `(environment_id, document_hash, target)`, the
certificate, and its inner binding to the regenerated base environment, premises and conclusion. -/
def decodePackage (src : RiskSource) (environment : Json) (package : Json) (target : String)
    (premises : List VE.Formula) (conclusion : VE.Formula) : Option VE.Tableau.Certificate := Id.run do
  let some baseEnv := (riskBaseEnvironmentJson src.R environment src.profiles).toOption | none
  let some baseProfiles := (VE.Bridge.strings (baseEnv.getObjValD "profiles")).toOption | none
  unless package.getObjValD "environment_id" == .str src.R.policy.1 &&
      package.getObjValD "document_hash" == .str src.R.policy.2 &&
      package.getObjValD "target" == .str target do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  match VE.Route.Wire.bindingOk baseProfiles baseEnv (premises.map VE.Route.Wire.encodeFormula)
      (VE.Route.Wire.encodeFormula conclusion) c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
  | .ok () => some c
  | .error _ => none

/-- Every conflict target's package, bound to `Background_baseAlt ++ riskPremises` or to alt's backgrounds. -/
def conflictCerts (src : RiskSource) (environment packages : Json) : List (Option VE.Tableau.Certificate) :=
  let A := toAlt src.R
  (targets (VE.Alternatives.inlineTree A)).map fun t =>
    let p := packages.getObjValD t.1
    decodePackage src environment p t.1 (VE.Alternatives.backgroundBaseAlt A ++ riskPremises src.R) (targetConclusion t) <|>
    decodePackage src environment p t.1 (VE.Alternatives.backgroundBaseAlt A) (targetConclusion t) <|>
    decodePackage src environment p t.1 (backgroundBase (VE.Alternatives.inlineTree A)) (targetConclusion t)

structure RiskConflictReplay where
  src : RiskSource
  certs : List (Option VE.Tableau.Certificate)

def RiskConflictReplay.conflictFree (r : RiskConflictReplay) : Bool := riskConflictFreeCheck r.src.R r.certs

def replayRiskConflict (j : Json) : Except String RiskConflictReplay := do
  let src ← decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document")
  pure ⟨src, conflictCerts src (j.getObjValD "environment") (j.getObjValD "packages")⟩

theorem risk_wire_conflict_sound (j : Json) (res : RiskConflictReplay) (h : replayRiskConflict j = .ok res)
    (hv : res.conflictFree = true) :
    Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
    WellFormedRisk res.src.R = true ∧ RiskConflictFree.{0} res.src.R := by
  unfold replayRiskConflict at h
  obtain ⟨src, hs, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  exact ⟨hs, src.wf, risk_conflict_free src.R src.wf _ hv⟩

structure RiskFollowableReplay where
  src : RiskSource
  certs : List (Option VE.Tableau.Certificate)
  cert : Option VE.Tableau.Certificate

def RiskFollowableReplay.conflictFree (r : RiskFollowableReplay) : Bool := riskConflictFreeCheck r.src.R r.certs

def RiskFollowableReplay.followable (r : RiskFollowableReplay) : Bool :=
  r.conflictFree && match r.cert with
    | some c => VE.Tableau.checkCertificate (envAt (VE.Alternatives.inlineTree (toAlt r.src.R)) 0)
        (VE.Alternatives.backgroundBaseAlt (toAlt r.src.R) ++ riskPremises r.src.R ++ r.src.R.Γ)
        (VE.Alternatives.allFollowable (toAlt r.src.R)) c
    | none => false

def replayRiskFollowable (j : Json) : Except String RiskFollowableReplay := do
  let src ← decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document")
  let environment := j.getObjValD "environment"
  let A := toAlt src.R
  pure ⟨src, conflictCerts src environment (j.getObjValD "packages"),
    decodePackage src environment (j.getObjValD "package") "followable"
      (VE.Alternatives.backgroundBaseAlt A ++ riskPremises src.R ++ src.R.Γ) (VE.Alternatives.allFollowable A)⟩

theorem risk_wire_followable_sound (j : Json) (res : RiskFollowableReplay) (h : replayRiskFollowable j = .ok res)
    (hv : res.followable = true) :
    Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
    WellFormedRisk res.src.R = true ∧ RiskConflictFree.{0} res.src.R ∧
    ∀ B : VE.Structure.{0}, BaseAdmissibleRisk res.src.R B → Sat B res.src.R.Γ →
      ∀ S, DocumentExpansion (VE.Alternatives.inlineTree (toAlt res.src.R)) B S →
        VE.Alternatives.FollowableIn (toAlt res.src.R) S := by
  unfold replayRiskFollowable at h
  obtain ⟨src, hs, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  simp only [RiskFollowableReplay.followable, RiskFollowableReplay.conflictFree, Bool.and_eq_true] at hv
  obtain ⟨hc, hf⟩ := hv
  have hcf := risk_conflict_free.{0} src.R src.wf _ hc
  refine ⟨hs, src.wf, hcf, ?_⟩
  revert hf
  split
  · intro hf
    exact risk_followable_sound src.R src.wf hcf _ hf
  · intro hf; cases hf

/-! ## Rendering (untrusted) -/

def renderValue (R : RiskDoc) (b : Box) (q : String) (v : Int) : String :=
  let tag := ((b.find q).map (·.tag)).getD "dimensionless"
  VE.Time.renderAmount ((scaleOf R tag).getD 0) v

def renderCase (R : RiskDoc) (b : Box) (v : Valuation) : String :=
  "(" ++ ", ".intercalate (b.entries.map fun en => s!"{en.name} {renderValue R b en.name (v en.name)}") ++ ")"

def caseJson (R : RiskDoc) (b : Box) (v : Valuation) : Json :=
  Json.arr (b.entries.map fun en => Json.mkObj [("quantity", .str en.name),
    ("value", .str (renderValue R b en.name (v en.name)))]).toArray

/-- The cell a `SufficientOutsideNecessary` or `RiskInconsistent` diagnostic names. -/
def cellOf (t : String) : Option (String × String) :=
  match t.splitOn ": " with
  | [_, rest] => match rest.splitOn "/" with
    | [a, h] => if h.contains ' ' then none else some (a, h)
    | _ => none
  | _ => none

/-- 4.3: the diagnostic with the witness case of `S ∧ ¬N` where one exists. -/
def withCase (R : RiskDoc) (d : Decision) (t : String) : String :=
  if t.startsWith "SufficientOutsideNecessary: " || t.startsWith "RiskInconsistent: " then
    match cellOf t with
    | some (a, h) => match witnessE (box R d) (.and (Suff R d a h) (.not (Nec R d a h))) with
      | some v => t ++ s!", case {renderCase R (box R d) v}"
      | none => t
    | none => t
  else t

def classOfHarm (R : RiskDoc) (h : String) : String := (classOf R h).getD "unclassified"

/-- The maximal classes of an alternative's profile, with their harms. -/
def worstCase (R : RiskDoc) (t : Tables) (a : String) : List (String × String) :=
  let hs := (t.might.filter (·.1 == a)).map (·.2)
  let cs := (hs.map (classOfHarm R)).eraseDups
  let maximal := cs.filter fun c => !cs.any (fun c' => (closure R).contains (c', c))
  hs.filterMap fun h => if maximal.contains (classOfHarm R h) then some (h, classOfHarm R h) else none

/-- Rules on the `performed` pair that select at `a` (guard true, every carve-out false). -/
def firingRules (R : RiskDoc) (d : Decision) (a : String) : List Nat :=
  match R.alt.performed with
  | none => []
  | some (m, q) =>
    let M := decisionModel R d
    let x : VE.Bridge.Entity := (R.alt.action, a)
    let nodes := (VE.Alternatives.inlineTree (toAlt R)).T.nodes
    (List.range nodes.length).filterMap fun i => match nodes[i]? with
      | some N => if (N.pred == m || N.pred == q) && N.guard.eval M [x] && N.carveOuts.all (fun c => !c.eval M [x])
          then some (i + 1) else none
      | none => none

def isSetting (d : Decision) (q : String) : Bool := (settingOf d q).isSome

/-- 4.9: the point estimates among the quantities of a condition. -/
def pointEstimates (R : RiskDoc) (d : Decision) (c : Cond) : List String :=
  (c.atomNames.eraseDups.filter fun q => (box R d).isPoint q && !isSetting d q).flatMap fun q =>
    (estimatesOf d q).map (·.id)

def endpointJson (e : Endpoint) : List (String × Json) :=
  [("estimate", .str e.estimate), ("side", .str (match e.side with | .lo => "lo" | .hi => "hi"))]

def dirName : Dir → String
  | .down => "down"
  | .up => "up"

def statusText (s : Status) : String :=
  (if s.required then "required" else if s.permitted then "permitted" else "forbidden") ++
    (if s.clear then "; clear" else "; not clear")

/-- Alt's diagnosis (4.6) for the record's chooser on the decision model (untrusted text, 7.4). -/
def diagnosisOf (R : RiskDoc) (d : Decision) : String :=
  let r : VE.Bridge.Entity := (R.alt.chooser, d.chooser)
  VE.Alternatives.Run.diagnosisText r (VE.Alternatives.diagnose (toAlt R) (decisionModel R d) r)

/-- The status of `a` in a Q1 line (5.2): permitted but not clear, required but not clear, or forbidden with
the deciding rules. -/
def auditStatusText (R : RiskDoc) (d : Decision) (a : String) : String :=
  match (statuses R d).lookup a with
  | some s =>
    if s.permitted then (if s.required then "required but not clear" else "permitted but not clear")
    else match decidingRules R d a with
      | [] => "forbidden (by default)"
      | [n] => s!"forbidden by rule {n}"
      | ns => s!"forbidden by rules {", ".intercalate (ns.map toString)}"
  | none => "not an alternative of the decision"

/-- 4.10, 5.2: `NO CLEAR ACTION AT DECISION TIME: <diagnosis>; <alternative> was <status>.` A conflict at the
decision has no per-alternative evaluation (4.8), and the line says so. -/
def noClearActionText (R : RiskDoc) (d : Decision) (a : String) : String :=
  match VE.Alternatives.scenarioConflict (toAlt R) (decisionModel R d) with
  | some (t, vs) =>
    s!"CONFLICT at ({", ".intercalate (vs.map (·.2))}) on {t.1}; {a} was not evaluated, because the rules conflict"
  | none => s!"{diagnosisOf R d}; {a} was {auditStatusText R d a}"

def decisionRecordId (dx : Entry) : String :=
  match VE.CertificateWire.canonical 257 dx.content with
  | .ok text => VE.CertificateWire.sha256 text.toUTF8
  | .error _ => ""

/-! ## Cases -/

def runDecision (id : String) (j : Json) : Except String Json := do
  let src ← decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document")
  let R := src.R
  let entry ← Wire.decodeEntry (j.getObjValD "decision")
  let supplied ← Wire.decodeSupplied (j.getObjValD "entries")
  let d ← admitDecision R entry supplied
  match validateDecision R d with
  | .error e => throw (withCase R d e)
  | .ok () => pure ()
  marginLimit R d
  let res ← replayDecision j
  let rid := decisionRecordId entry
  let base := [("environment_id", Json.str R.policy.1), ("document_hash", .str R.policy.2),
    ("decision_record_id", .str rid)]
  match res.conflict with
  | some (t, vs) =>
    return ok id (base ++ [("verdict", .str "CONFLICT"), ("target", .str t.1),
      ("tuple", toJson (vs.map (·.2))),
      ("text", .str s!"Decision {d.id}: CONFLICT at ({", ".intercalate (vs.map (·.2))}) on {t.1}; no per-alternative evaluation.")])
  | none =>
    let t := res.tables
    let b := box R d
    let tablesJ := Json.mkObj [
      ("might", Json.arr ((t.might.map fun (a, h) => Json.mkObj ([("alternative", .str a), ("harm", .str h)] ++
        match (t.witness.find? (·.1 == (a, h))) with
        | some (_, v) => [("witness", caseJson R b v)]
        | none => []))).toArray),
      ("leads", Json.arr ((t.leads.map fun (a, h) => Json.mkObj [("alternative", .str a), ("harm", .str h)])).toArray)]
    let statusesJ := Json.arr (res.statuses.map fun (a, s) =>
      let rules := firingRules R d a
      Json.mkObj [("alternative", .str a), ("permitted", .bool s.permitted), ("required", .bool s.required),
        ("clear", .bool s.clear), ("rules", toJson rules), ("by_default", .bool rules.isEmpty)]).toArray
    let worstJ := Json.mkObj (d.alternatives.map fun a =>
      (a.name, Json.arr ((worstCase R t a.name).map fun (h, c) => Json.mkObj [("harm", .str h), ("class", .str c)]).toArray))
    let eps := endpoints d
    let marginsJ := Json.arr (eps.flatMap fun e => d.alternatives.flatMap fun a => [Dir.down, Dir.up].map fun dir =>
      Json.mkObj (endpointJson e ++ [("alternative", .str a.name), ("direction", .str (dirName dir))] ++
        match res.margin e dir a.name with
        | some x => [("nearest", .str (renderValue R b ((estimateOf d e.estimate).map (·.quantity) |>.getD "") x))]
        | none => [("no_single_valid_change", .bool true)])).toArray
    let invalidJ := Json.arr (eps.flatMap fun e => [Dir.down, Dir.up].filterMap fun dir =>
      (res.recordInvalid e dir).map fun (x, text) => Json.mkObj (endpointJson e ++ [("direction", .str (dirName dir)),
        ("value", .str (renderValue R b ((estimateOf d e.estimate).map (·.quantity) |>.getD "") x)),
        ("diagnostic", .str text)])).toArray
    let conflictJ := Json.arr (eps.flatMap fun e => [Dir.down, Dir.up].filterMap fun dir =>
      (res.recordConflict e dir).map fun x => Json.mkObj (endpointJson e ++ [("direction", .str (dirName dir)),
        ("value", .str (renderValue R b ((estimateOf d e.estimate).map (·.quantity) |>.getD "") x))])).toArray
    let cells := cellsOf R d
    let unexaminedPossible := cells.filter fun (a, h) => !addressed d a h && completion R h == .top
    let decider := match R.risk.unexamined with
      | .ruledOutBy dd => dd
      | _ => d.chooserLabel
    let ruledOut := cells.filter fun (a, h) => !addressed d a h && completion R h == .bottom
    let points := cells.flatMap fun (a, h) =>
      (if t.leads.contains (a, h) then (pointEstimates R d (Suff R d a h)).map fun q => s!"{a}/{h} leads: {q}" else []) ++
      (if !t.might.contains (a, h) then (pointEstimates R d (Nec R d a h)).map fun q => s!"{a}/{h} cannot: {q}" else [])
    let defaultDecided := (d.alternatives.filter fun a => (firingRules R d a.name).isEmpty).map (·.name)
    let clear := (res.statuses.filter (·.2.clear)).map (·.1)
    let conditional := d.cited.map (·.id)
    let dilemmas := if clear.isEmpty then [diagnosisOf R d] else []
    -- 2.4: the condition lines shown with a record that uses the form; c5's wording is risk-wording-probe-2's (2.1)
    let forms := d.conditions.map (·.form)
    let conditionLegend :=
      (if forms.contains .necessary then ["\"<action> cannot lead to <harm> unless <condition>\" means the harm happens in no case they allow in which the condition does not hold."] else []) ++
      (if forms.contains .exact then ["\"<action> leads to <harm> exactly when <condition>\" means the harm happens in every case they allow in which the condition holds, and in no case they allow in which it does not hold."] else []) ++
      (if forms.contains .sufficient then ["\"If <condition>, <action> leads to <harm>\" means the harm happens in every case they allow in which the condition holds."] else [])
    let lines := Json.mkObj [
      ("unexamined_possible", toJson (unexaminedPossible.map fun (a, h) => s!"{a}/{h}")),
      ("assumed_ruled_out", Json.mkObj [("decider", .str decider),
        ("cells", toJson (ruledOut.map fun (a, h) => s!"{a}/{h}"))]),
      ("point_estimates", toJson points), ("default_decided", toJson defaultDecided),
      ("dilemmas", toJson dilemmas)]
    let statusLines := res.statuses.map fun (a, s) => s!"{a}: {statusText s}"
    -- 5.2: the ruled-out cells and the unexamined cells counted as possible are both part of the condition
    let extras := (if ruledOut.isEmpty then [] else [s!"{decider}'s ruled-out cells ({ruledOut.length} listed)"]) ++
      (if unexaminedPossible.isEmpty then []
       else [s!"{unexaminedPossible.length} unexamined cells counted as possible"])
    let conditionalText := match extras with
      | [] => ", ".intercalate conditional
      | [x] => s!"{", ".intercalate conditional} and {x}"
      | xs => s!"{", ".intercalate (conditional ++ xs.dropLast)} and {xs.getLastD ""}"
    let text := s!"Decision {d.id} — conditional on {conditionalText}. " ++
      "; ".intercalate statusLines ++ ". " ++
      (match clear with
       | [] => s!"No clear action: {diagnosisOf R d}."
       | [a] => s!"Clear actions: {a}."
       | cs => s!"Clear actions: {"; ".intercalate cs}. The policy does not choose among them.")
    return ok id (base ++ [("tables", tablesJ), ("statuses", statusesJ), ("worst_cases", worstJ),
      ("margins", marginsJ), ("record_invalid", invalidJ), ("record_conflict", conflictJ), ("lines", lines),
      ("legend", toJson conditionLegend),
      ("clear", toJson clear), ("conditional_on", toJson conditional), ("text", .str text)])

def q1Text (R : RiskDoc) (d : Option Decision) (a : String) : Q1 → String
  | .permitted true => s!"PERMITTED AT DECISION TIME: {a} was clear given {cites d}."
  | .permitted false => s!"PERMITTED AT DECISION TIME: {a} was permitted but not clear given {cites d}."
  | .forbidden rules => s!"FORBIDDEN AT DECISION TIME: {a} was forbidden by rule {", ".intercalate (rules.map toString)} given {cites d}."
  | .noClearAction => match d with
    | some d => s!"NO CLEAR ACTION AT DECISION TIME: {noClearActionText R d a}."
    | none => s!"NO CLEAR ACTION AT DECISION TIME: {a}."
  | .notReplayable t => s!"NOT REPLAYABLE: {t}"
where cites (d : Option Decision) : String := match d with
  | some d => ", ".intercalate (d.cited.map (·.id))
  | none => ""

def q2Text : Q2 → String
  | .same => "SAME VERDICT WITH ALL RECORDED ESTIMATES."
  | .different ids => s!"DIFFERENT VERDICT WITH ALL RECORDED ESTIMATES: {", ".intercalate ids} recorded before the decision and not used."
  | .notComparable t => s!"NOT COMPARABLE: {t}."

def runAudit (id : String) (j : Json) : Except String Json := do
  let res ← replayAudit j
  let R := res.src.R
  let sn := (snapshotOf R res.log res.decision).toOption
  let q3 := auditQ3 R res.log res.decision res.alternative
  let surprise := q3.any (fun l => (l.splitOn "surprise").length > 1)
  return ok id [("alternative", .str res.alternative),
    ("q1", .str (q1Text R (sn.map (·.decision)) res.alternative res.q12.q1)),
    ("q2", .str (q2Text res.q12.q2)), ("procedure", toJson res.q12.procedure), ("q3", toJson q3),
    ("not_concluded", toJson (if surprise then ["Not concluded: that the decision was wrong because a harm followed."] else []))]

/-- A decoded finite witness over `E_risk`'s base vocabulary, with its structural validity. -/
def decodeWitnessModel (R : RiskDoc) (w : Json) : Except String (VE.FiniteModel VE.Bridge.Entity) := do
  let data ← VE.Bridge.decodeModelData (modelVocabulary R) (← w.getObjVal? "model")
  if data.valid (modelVocabulary R) then pure data.toModel else throw "model is not semantically admissible"

def runConflict (id : String) (j : Json) : Except String Json := do
  if (j.getObjVal? "witness").toBool then
    let src ← decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document")
    let R := src.R
    let w ← j.getObjVal? "witness"
    let M ← decodeWitnessModel R w
    unless backgroundValidRisk R M do throw (VE.Route.Wire.invalidModel "risk")
    let name ← VE.Bridge.stringField w "target"
    let some t := (targets (VE.Alternatives.inlineTree (toAlt R))).find? (·.1 == name)
      | throw s!"InvalidInput: unknown conflict target {name}"
    let tuple ← (← VE.Bridge.strings (← w.getObjVal? "tuple")).zip t.2.1 |>.mapM fun (x, s) =>
      VE.Alternatives.Replay.entity M s x
    unless tuple.length == t.2.1.length do throw "InvalidInput: witness tuple has the wrong length or sort"
    let conflict := t.2.2.eval M (tupleVal tuple)
    return ok id [("verdict", .str (if conflict then "CONFLICT" else "UNKNOWN")), ("target", .str t.1)]
  let res ← replayRiskConflict j
  return ok id [("verdict", .str (if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN")),
    ("targets", toJson ((targets (VE.Alternatives.inlineTree (toAlt res.src.R))).map (·.1)))]

def notComputed : String := "not computed: conflict status UNKNOWN"

def runFollowable (id : String) (j : Json) : Except String Json := do
  if (j.getObjVal? "witness").toBool then
    let src ← decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document")
    let R := src.R
    let A := toAlt R
    unless riskConflictFreeCheck R (conflictCerts src (j.getObjValD "environment") (j.getObjValD "packages")) do
      return ok id [("verdict", .str "not computed"), ("text", .str notComputed)]
    let w ← j.getObjVal? "witness"
    let M ← decodeWitnessModel R w
    unless backgroundValidRisk R M do throw (VE.Route.Wire.invalidModel "risk")
    unless R.Γ.all (fun p => p.eval M []) do throw (VE.Route.Wire.invalidModel "premises")
    let r ← VE.Alternatives.Replay.entity M R.alt.chooser (← VE.Bridge.stringField w "chooser")
    if (VE.Alternatives.notFollowableF A).eval M (tupleVal [r]) then
      let dg := VE.Alternatives.Run.diagnosisText r (VE.Alternatives.diagnose A M r)
      return ok id [("verdict", .str "DILEMMA"), ("chooser", .str r.2), ("diagnosis", .str dg),
        ("text", .str s!"DILEMMA at {r.2}: {dg}")]
    return ok id [("verdict", .str "UNKNOWN"), ("text", .str "UNKNOWN: the witness chooser has a clear action")]
  let res ← replayRiskFollowable j
  unless res.conflictFree do
    return ok id [("verdict", .str "not computed"), ("text", .str notComputed)]
  if res.followable then
    return ok id [("verdict", .str "FOLLOWABLE"), ("conditional_on", toJson res.src.R.labels)]
  return ok id [("verdict", .str "UNKNOWN"), ("text", .str "UNKNOWN: no accepted followability certificate for this source")]

def runCertificate (id : String) (j : Json) : Except String Json := do
  let src ← decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document")
  let R := src.R
  let A := toAlt R
  let D := VE.Alternatives.inlineTree A
  let E := envAt D (size D)
  let premisesJson ← j.getObjVal? "premises"
  let ps ← VE.Route.Wire.decodeFormulas E premisesJson
  let conclusionJson ← j.getObjVal? "conclusion"
  let c ← VE.Route.Wire.decodeClosed E conclusionJson
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  let all := VE.Alternatives.backgroundAlt A ++ riskPremises R ++ elaborate D.T
  let baseEnv ← riskBaseEnvironmentJson R (j.getObjValD "environment") src.profiles
  let baseProfiles ← VE.Bridge.strings (baseEnv.getObjValD "profiles")
  VE.Route.Wire.bindingOk baseProfiles baseEnv (all.map VE.Route.Wire.encodeFormula ++ (← premisesJson.getArr?).toList)
    conclusionJson cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  let valid := VE.Tableau.checkCertificate E (all ++ ps) c cert
  return ok id [("valid", .bool valid),
    ("conditional_on", toJson (VE.Alternatives.altPremiseLabels A ++ riskPremiseLabels R))]

def encodeAdmitted (id reportId : String) (res : Admission.Admitted) : Json :=
  ok id [("admitted", .bool true), ("report", VE.Norms.Run.reportJson res.report),
    ("report_id", .str reportId), ("kinds", Json.arr res.kinds.toArray),
    ("conditional_on", toJson (res.src.R.labels ++ riskPremiseLabels res.src.R))]

def runAdmission (id : String) (environment document : Json) : Except String Json := do
  let res ← Admission.admitDocument environment document
  let envId ← VE.Alternatives.Replay.environmentId res.src.profiles environment
  let reportId ← VE.CertificateWire.digest (VE.Norms.Run.reportDomain res.src.profiles)
    (VE.Norms.Run.reportPayload envId document res.report)
  return encodeAdmitted id reportId res

/-- A W2 answer is the exact graph-checker output, bound to the complete risk source. Its semantic consequence is
over alt's premises plus `riskPremises` and the two regenerated definitions, and the ordinary W2 assumptions
remaining in the report. -/
def RiskAdmissionAnswer (id : String) (environment document answer : Json) : Prop :=
  ∃ res : Admission.Admitted, ∃ envId reportId : String,
    Admission.admitDocument environment document = .ok res ∧
    VE.Alternatives.Replay.environmentId res.src.profiles environment = .ok envId ∧
    VE.CertificateWire.digest (VE.Norms.Run.reportDomain res.src.profiles)
      (VE.Norms.Run.reportPayload envId document res.report) = .ok reportId ∧
    answer = encodeAdmitted id reportId res ∧ WellFormedRisk res.src.R = true ∧
    ∀ S : VE.Structure.{0}, S.Admissible (riskExtEnv res.src.R) →
      Sat S (Admission.generated res) →
      Sat S ((Admission.otherAssumptions res).map (·.formula)) →
      res.report.root.formula.denote S []

theorem runAdmission_sound (id : String) (environment document answer : Json)
    (h : runAdmission id environment document = .ok answer) :
    RiskAdmissionAnswer id environment document answer := by
  unfold runAdmission at h
  obtain ⟨res, hr, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨envId, he, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨reportId, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  exact ⟨res, envId, reportId, hr, he, hd, rfl, res.src.wf,
    fun S hS hg ho => Admission.report_consequence res S hS hg ho⟩

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if kind == "admission" then
    return ← runAdmission id (← j.getObjVal? "environment") (← j.getObjVal? "document")
  if kind == "risk-elaborate" then
    let src ← decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document")
    return ok id (Wire.regenerated src)
  if kind == "risk-decision" then return ← runDecision id j
  if kind == "risk-conflict" then return ← runConflict id j
  if kind == "risk-followable" then return ← runFollowable id j
  if kind == "risk-audit" then return ← runAudit id j
  if kind == "risk-certificate" then return ← runCertificate id j
  throw s!"UnsupportedProfile: case kind {kind} is not available on the risk route"

/-- Public W2 acceptance from raw input, with source and report bindings. -/
theorem risk_wire_acceptance (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : usesRiskPath j = true) :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      RiskAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer := by
  have _ := hn
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨kind, hkind, h⟩ := VE.Order.ProfileGate.bind_ok h
  have heq : kind = "admission" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  simp only [beq_self_eq_true, ↓reduceIte] at h
  obtain ⟨environment, he, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨document, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  have he' : j.getObjValD "environment" = environment := by
    simp only [Json.getObjValD, he]; rfl
  have hd' : j.getObjValD "document" = document := by
    simp only [Json.getObjValD, hd]; rfl
  rw [he', hd']
  exact ⟨id, hid, runAdmission_sound id environment document answer (by simpa using h)⟩

def runCaseReported (j : Json) : Json :=
  if usesRiskPath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]
  else VE.Alternatives.Run.runCaseReported j

end VE.Risk.Run
