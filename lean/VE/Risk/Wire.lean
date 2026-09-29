import VE.Risk.Audit
import VE.Alternatives.Replay
import VE.Time.Wire

/-! The risk decoder (docs/spec/risk.md 1.1, 3 and 7.3): the profile gate, the
strict `risk` block decoder, the W6 unit extension, the `excludes` fulfilment
body, the norm objects and base units over `E_risk`, the policy identity, and
the entry, supplied-entry and log decoders.

The frozen W1 decoder never sees the `alternatives` or `risk` blocks or the W6
extension: `riskNormsView` removes them and the `alternatives@0` and `risk@0`
profiles. The alternatives block is decoded by alt's unchanged `decodeBlock`
after `excludes` is expanded to `¬risk__might_lead_to(a, h)`. The original
complete environment is hashed for identity (3.4). -/
namespace VE.Risk.Wire
open Lean
open VE.Bridge (exactFields fields stringField strings)
open VE.Norms
open VE.Alternatives (AltEnv AltDoc findReg)

/-! ## The profile gate and the views -/

/-- 1.1: `risk@0` requires `alternatives@0` (whose own gate requires `norms@0` and rejects `soft-norms@0`). -/
def profileGate (environment : Json) : Except String (List String) := do
  let ps ← VE.Route.Gate.profilesOf environment
  unless decide (ps.Pairwise (· < ·)) do throw (VE.Route.Gate.unsupported "profiles must be sorted and unique")
  unless ps.contains "risk@0" do throw "UnsupportedProfile: risk@0 is required"
  unless ps.contains "alternatives@0" do throw "UnsupportedProfile: risk@0 requires alternatives@0"
  unless ps.contains "norms@0" do throw "UnsupportedProfile: alternatives@0 requires norms@0"
  if ps.contains "soft-norms@0" then throw "UnsupportedProfile: alternatives@0 with soft-norms@0"
  pure ps

/-- The environment W1's decoder sees: the blocks and the W6 extension removed, the two profiles dropped. -/
def riskNormsView (environment : Json) (ps : List String) : Except String Json := do
  let kept := (← fields environment).filter fun p =>
    !["alternatives", "risk", "unit_schema", "units"].contains p.1
  pure ((Json.mkObj kept).setObjVal! "profiles"
    (toJson (ps.filter (fun p => p != "alternatives@0" && p != "risk@0"))))

/-! ## The W6 unit extension -/

def decodeUnits (environment : Json) : Except String (List (String × Nat)) := do
  match environment.getObjVal? "units" with
  | .error _ =>
    if (environment.getObjVal? "unit_schema").isOk then throw "InvalidInput: units" else pure []
  | .ok u =>
    unless environment.getObjValD "unit_schema" == .str VE.Time.Wire.schema do
      throw "UnsupportedProfile: Unsupported unit schema"
    let fs ← match fields u with
      | .ok fs => pure fs
      | .error _ => throw "units must be an object"
    if fs.length > 64 then throw "ResourceLimit: At most 64 unit tags"
    let decls ← fs.mapM fun (tag, record) => VE.Time.Wire.decodeUnit tag record
    VE.Time.Wire.displayInjective decls
    pure (decls.map fun u => (u.tag, u.places))

/-! ## The risk block (1.1, 3.1) -/

def blockFields : List String :=
  ["severity", "harm_classes", "unexamined", "always_possible", "combination", "alternative_kinds",
   "required_alternatives", "quantity_kinds", "required_estimators", "use_all_recorded"]

def stageFields : List String := ["chance_tag", "bands", "costs", "additive_loss"]

def err (field : String) : String := s!"InvalidInput: risk.{field}"

def str (field : String) (j : Json) : Except String String :=
  match j with
  | .str s => pure s
  | _ => throw (err field)

def strList (field : String) (j : Json) : Except String (List String) :=
  match strings j with
  | .ok xs => pure xs
  | .error _ => throw (err field)

def pairList (field : String) (j : Json) : Except String (List (String × String)) := do
  let xs ← match j with
    | .arr xs => pure xs.toList
    | _ => throw (err field)
  xs.mapM fun x => do
    match ← strList field x with
    | [a, b] => pure (a, b)
    | _ => throw (err field)

def objStrings (field : String) (j : Json) : Except String (List (String × String)) := do
  let fs ← match fields j with
    | .ok fs => pure fs
    | .error _ => throw (err field)
  fs.mapM fun (k, v) => do pure (k, ← str field v)

def identifierOk (s : String) : Bool :=
  VE.Bridge.identifier s && (s.splitOn "__").length.ble 1

def decodeRiskBlock (raw : Json) : Except String RiskEnv := do
  let keys ← match fields raw with
    | .ok fs => pure (fs.map Prod.fst)
    | .error _ => throw (err "block")
  for k in keys do
    if stageFields.contains k then throw s!"InvalidInput: risk.{k} (stage B or C not enabled)"
    unless blockFields.contains k do throw (err k)
  for k in ["severity", "harm_classes", "unexamined"] do
    unless keys.contains k do throw (err k)
  let sv := raw.getObjValD "severity"
  unless (exactFields sv ["sort", "classes", "more_severe", "unranked", "decided_by"]).isOk do throw (err "severity")
  let sort ← str "severity" (sv.getObjValD "sort")
  let classes ← strList "severity" (sv.getObjValD "classes")
  for n in sort :: classes do
    unless identifierOk n do throw (err "severity")
  let edges ← pairList "severity" (sv.getObjValD "more_severe")
  let unranked ← pairList "severity" (sv.getObjValD "unranked")
  let decidedBy ← str "severity" (sv.getObjValD "decided_by")
  if decidedBy.utf8ByteSize > 64 || decidedBy.isEmpty then throw (err "severity")
  let harmClasses ← pairList "harm_classes" (raw.getObjValD "harm_classes")
  let unexamined ← match raw.getObjValD "unexamined" with
    | .str "possible" => pure Unexamined.possible
    | .obj _ =>
      let o := raw.getObjValD "unexamined"
      unless (exactFields o ["ruled_out_by"]).isOk do throw (err "unexamined")
      match o.getObjValD "ruled_out_by" with
      | .str "chooser" => pure Unexamined.ruledOutByChooser
      | .str d => if d.isEmpty || d.utf8ByteSize > 64 then throw (err "unexamined") else pure (Unexamined.ruledOutBy d)
      | _ => throw (err "unexamined")
    | _ => throw (err "unexamined")
  let alwaysPossible ← match raw.getObjVal? "always_possible" with
    | .ok j => strList "always_possible" j
    | .error _ => pure []
  let combination ← match raw.getObjVal? "combination" with
    | .error _ => pure none
    | .ok (.str "latest") => pure (some Combination.latest)
    | .ok (.str "hull") => pure (some Combination.hull)
    | .ok (.str "intersection") => pure (some Combination.intersection)
    | .ok _ => throw (err "combination")
  let alternativeKinds ← match raw.getObjVal? "alternative_kinds" with
    | .ok j => objStrings "alternative_kinds" j
    | .error _ => pure []
  for (k, v) in alternativeKinds do
    unless identifierOk k do throw (err "alternative_kinds")
    if v.isEmpty || v.utf8ByteSize > 64 then throw (err "alternative_kinds")
  let requiredAlternatives ← match raw.getObjVal? "required_alternatives" with
    | .error _ => pure []
    | .ok (.arr xs) => xs.toList.mapM fun x => do
        unless (exactFields x ["when", "require"]).isOk do throw (err "required_alternatives")
        pure (← str "required_alternatives" (x.getObjValD "when"),
          ← strList "required_alternatives" (x.getObjValD "require"))
    | .ok _ => throw (err "required_alternatives")
  let quantityKinds ← match raw.getObjVal? "quantity_kinds" with
    | .ok j => objStrings "quantity_kinds" j
    | .error _ => pure []
  let requiredEstimators ← match raw.getObjVal? "required_estimators" with
    | .error _ => pure []
    | .ok (.arr xs) => xs.toList.mapM fun x => do
        unless (exactFields x ["quantity_kind", "estimators"]).isOk do throw (err "required_estimators")
        pure (← str "required_estimators" (x.getObjValD "quantity_kind"),
          ← strList "required_estimators" (x.getObjValD "estimators"))
    | .ok _ => throw (err "required_estimators")
  let useAll ← match raw.getObjVal? "use_all_recorded" with
    | .error _ => pure false
    | .ok (.bool b) => pure b
    | .ok _ => throw (err "use_all_recorded")
  pure ⟨⟨sort, classes, edges, unranked, decidedBy⟩, harmClasses, unexamined, alwaysPossible, combination,
    alternativeKinds, requiredAlternatives, quantityKinds, requiredEstimators, useAll⟩

/-! ## `excludes` (2.2) -/

/-- `excludes(a, h) := ¬risk__might_lead_to(a, h)`, context `[harm, action]`. -/
def excludesBody : Json :=
  Json.arr #[.str "not", Json.arr #[.str "binary", .str mightName, Json.arr #[.str "var", toJson (1 : Nat)],
    Json.arr #[.str "var", toJson (0 : Nat)]]]

/-- The alternatives block with each `excludes` body expanded; the obligations that used it. -/
def expandExcludes (block : Json) : Json × List String :=
  match block.getObjVal? "fulfilments" with
  | .ok (.arr xs) =>
    let items := xs.toList.map fun item =>
      if item.getObjValD "body" == .str "excludes" then (item.setObjVal! "body" excludesBody, true) else (item, false)
    let names := items.filterMap fun (item, ex) => if ex then match item.getObjValD "obligation" with
      | .str o => some o
      | _ => none else none
    (block.setObjVal! "fulfilments" (Json.arr (items.map Prod.fst).toArray), names)
  | _ => (block, [])

/-! ## The source -/

/-- A decoded, well-formed risk source. -/
structure RiskSource where
  profiles : List String
  ne : VE.Norms.Wire.NormsEnvironment
  R : RiskDoc
  wf : WellFormedRisk R = true
  avoidsOn : List String
  excludesOn : List String

def decodePremisesRisk (R0 : RiskDoc) (premises : Json) : Except String (List (String × VE.Formula)) := do
  let raw ← VE.Alternatives.Wire.decodePremises premises
  for (label, a) in raw do
    unless a.check (riskExtEnv R0) [] do throw s!"InvalidInput: ill-typed premise {label}"
  pure (raw.map fun (l, a) => (l, VE.Alternatives.inline (toAlt R0) (riskInline R0 a)))

/-- Decode the environment with both blocks and the W6 extension, the norm objects and the active base units of
`document` (`{"norms", "units"?}`), then run `WellFormedRisk` with the diagnostics of 6. -/
def decodeRiskSource (environment document : Json) : Except String RiskSource := do
  let ps ← profileGate environment
  let altRaw ← match environment.getObjVal? "alternatives" with
    | .ok b => pure b
    | .error _ => throw "InvalidInput: alternatives.block"
  let riskRaw ← match environment.getObjVal? "risk" with
    | .ok b => pure b
    | .error _ => throw (err "block")
  let units ← decodeUnits environment
  let ne ← VE.Norms.Wire.decodeNormsEnvironment (← riskNormsView environment ps)
  unless ne.rv.definitions.isEmpty do throw "UnsupportedProfile: risk route with definitions is not implemented"
  unless ne.rv.flags.isEmpty do throw "UnsupportedProfile: risk route with data flags is not implemented"
  unless ne.rv.literals.isEmpty do throw "UnsupportedProfile: risk route with $string literals is not implemented"
  let (altExpanded, excludesOn) := expandExcludes altRaw
  let b ← VE.Alternatives.Wire.decodeBlock altExpanded
  let risk ← decodeRiskBlock riskRaw
  let norms := document.getObjValD "norms"
  let unitsJ := document.getObjValD "units"
  let items ← match norms with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: norms must be an array"
  if items.length > 256 then throw "ResourceLimit: rules"
  let nodes ← items.mapM VE.Norms.Wire.decodeNorm
  let envId ← VE.Alternatives.Replay.environmentId ps environment
  let docHash ← VE.Alternatives.Replay.documentHash ps environment norms unitsJ
  let R0 : RiskDoc := ⟨ne.rv.vocabulary, units, [], b.alt, risk, ⟨ne.regulated, [], nodes⟩, [], (envId, docHash), []⟩
  VE.Alternatives.checkBlock (toAlt R0)
  VE.Alternatives.Wire.checkVerbalisations b.alt (← environment.getObjVal? "vocabulary")
  VE.Alternatives.Wire.checkAvoids (toAlt R0) (b.avoidsOn.filter (fun o => !excludesOn.contains o))
  for o in excludesOn do
    match findReg R0.T o with
    | some r => unless r.sorts == [b.alt.chooser, b.alt.harm] do throw s!"FulfilmentSort: {o}"
    | none => throw s!"FulfilmentSort: {o}"
  let gamma ← decodePremisesRisk R0 unitsJ
  let R : RiskDoc := { R0 with Γ := gamma.map Prod.snd, labels := gamma.map Prod.fst }
  match hv : validateRisk R with
  | .error e => throw e
  | .ok () => pure ⟨ps, ne, R, by unfold WellFormedRisk; rw [hv], b.avoidsOn.filter (fun o => !excludesOn.contains o),
      excludesOn⟩

/-! ## Entries, supplied entries and the log (3.3) -/

def decodeDay (j : Json) : Except String Int := do
  let s ← j.getStr?
  let D ← VE.Time.parseIso s
  pure (D.num : Int)

def decodeKind (j : Json) (what : String) : Except String EntryKind :=
  match j with
  | .str k => match EntryKind.ofString k with
    | some kind => pure kind
    | none => throw s!"InvalidInput: {what}.kind"
  | _ => throw s!"InvalidInput: {what}.kind"

def decodeEntryIn (what : String) (j : Json) : Except String Entry := do
  unless (exactFields j ["seq", "day", "id", "kind", "content", "prev", "hash"]).isOk do throw s!"InvalidInput: {what}"
  let seq ← match (j.getObjValD "seq").getNat? with
    | .ok n => pure n
    | .error _ => throw s!"InvalidInput: {what}.seq"
  let day ← match decodeDay (j.getObjValD "day") with
    | .ok d => pure d
    | .error _ => throw s!"InvalidInput: {what}.day"
  let id ← match j.getObjValD "id" with
    | .str s => pure s
    | _ => throw s!"InvalidInput: {what}.id"
  let kind ← decodeKind (j.getObjValD "kind") what
  let prev ← match j.getObjValD "prev" with
    | .str s => pure s
    | _ => throw s!"InvalidInput: {what}.prev"
  let hash ← match j.getObjValD "hash" with
    | .str s => pure s
    | _ => throw s!"InvalidInput: {what}.hash"
  pure ⟨seq, day, id, kind, j.getObjValD "content", prev, hash⟩

/-- The decision entry of a `risk-decision` case. -/
def decodeEntry (j : Json) : Except String Entry := decodeEntryIn "risk-decision" j

/-- The supplied entries (3.3): an estimate entry without `seq` or `day` is `EstimateProvenance: <id> recorded`,
reported when it is decoded, before any citation is matched (4.4 A1). -/
def decodeSupplied (j : Json) : Except String Log := do
  let xs ← match j with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: risk-decision.entries"
  if xs.length > 4096 then throw "ResourceLimit: risk log entries"
  xs.mapM fun x => do
    if x.getObjValD "kind" == .str "estimate" &&
        ((x.getObjVal? "seq").toOption.isNone || (x.getObjVal? "day").toOption.isNone) then
      let id := match x.getObjValD "id" with
        | .str s => s
        | _ => ""
      throw s!"EstimateProvenance: {id} recorded"
    decodeEntryIn "risk-decision" x

/-- The log of a `risk-audit` case: `{"format": "ve-risk-log@0", "entries": [...]}`. -/
def decodeLog (j : Json) : Except String Log := do
  unless (exactFields j ["format", "entries"]).isOk do throw "InvalidInput: risk-log"
  unless j.getObjValD "format" == .str "ve-risk-log@0" do throw "InvalidInput: risk-log.format"
  let xs ← match j.getObjValD "entries" with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: risk-log.entries"
  if xs.length > 4096 then throw "ResourceLimit: risk log entries"
  xs.mapM (decodeEntryIn "risk-log")

/-! ## Regenerated outputs (`risk-elaborate`) -/

def enc (a : VE.Formula) : Json := VE.Route.Wire.encodeFormula a

def labelled (labels : List String) (fs : List VE.Formula) : Json :=
  Json.arr ((labels.zip fs).map (fun (l, a) => Json.mkObj [("label", .str l), ("ast", enc a)])).toArray

/-- Incomparable pairs of classes that are not declared unranked (a warning, 4.1(3)). -/
def unrankedSeverities (R : RiskDoc) : List (String × String) :=
  (VE.Risk.lowerPairs R.classes).filter fun (a, b) =>
    !(closure R).contains (a, b) && !(closure R).contains (b, a) &&
    !R.risk.severity.unranked.contains (a, b) && !R.risk.severity.unranked.contains (b, a)

def usesWord (R : RiskDoc) (w : String) : Bool :=
  R.T.nodes.any fun N => (N.guard :: N.carveOuts).any fun φ => (VE.Norms.preds φ).contains w

def chainOrder (R : RiskDoc) : Option (List String) :=
  -- the closed order is a chain when every pair is comparable; list the classes by the number above them
  if (VE.Risk.lowerPairs R.classes).all (fun (a, b) => (closure R).contains (a, b) || (closure R).contains (b, a)) then
    some (((R.classes.map (fun c => (((closure R).filter (fun p => p.2 == c)).length, c))).mergeSort
      (fun a b => decide (a.1 ≤ b.1))).map Prod.snd)
  else none

/-- 2.4: the legend lines generated from the blocks (untrusted text). -/
def legend (src : RiskSource) : List String :=
  let R := src.R
  let a := R.alt
  let alt := VE.Alternatives.Wire.legend (toAlt R)
  let core := [alt[0]?, alt[1]?, alt[2]?].filterMap id |>.filter (fun l => !l.startsWith "\"<")
  let decider := match R.risk.unexamined with
    | .ruledOutBy d => d
    | _ => s!"the deciding {a.chooser}"
  core ++
  ["\"<action> might lead to <harm>\" means the declared estimates, conditions and statements do not rule the harm out.",
   "\"<action> cannot lead to <harm>\" means they rule it out.",
   "\"<action> leads to <harm>\" means it happens in every case they allow.",
   "\"<action> might not lead to <harm>\" means some case they allow avoids the harm."] ++
  (match R.risk.unexamined with
   | .possible => ["An unexamined outcome counts as possible."]
   | _ => match R.risk.alwaysPossible with
     | [] => [s!"{decider} rules out unexamined outcomes."]
     | cs => [s!"An unexamined {" or ".intercalate cs} outcome counts as possible; {decider} rules out other unexamined outcomes."]) ++
  (match chainOrder R with
   | some order => [s!"Severity, from most to least severe: {", ".intercalate order}. Severity is set by {R.risk.severity.decidedBy}."]
   | none => (R.risk.severity.edges.map fun (x, y) => s!"{x} harms are more severe than {y} harms.") ++
       (R.risk.severity.unranked.map fun (x, y) => s!"{x} harms and {y} harms are not ranked.") ++
       [s!"Severity is set by {R.risk.severity.decidedBy}."]) ++
  (R.risk.harmClasses.map fun (h, c) => s!"{h} is {c}.") ++
  (if usesWord R orWorseName then ["\"<harm> is <class> or worse\" means the harm is <class> or more severe than <class>."] else []) ++
  (if usesWord R lessWorstName then ["<a> has a less severe worst case than <b> when <b> might lead to a harm more severe than every harm <a> might lead to."] else []) ++
  (if usesWord R "avoidable" then ["\"<harm> is avoidable by <chooser>\" means some action available to the chooser might not lead to the harm."] else []) ++
  (if usesWord R "allows" then ["\"<action> allows <harm> to happen\" means the action leads to the harm, and another action available to the same chooser might not lead to it."] else []) ++
  (if usesWord R "prevents" then ["\"<action> might prevent <harm>\" means the action might not lead to the harm, and another action available to the same chooser leads to it."] else []) ++
  (src.avoidsOn.map fun o => s!"A {a.chooser} {VE.Alternatives.Wire.actWords (((findReg R.T o).bind (·.act)).getD o)} by taking an action that might not lead to the harm.") ++
  (src.excludesOn.map fun o => s!"A {a.chooser} {VE.Alternatives.Wire.actWords (((findReg R.T o).bind (·.act)).getD o)} by taking an action that cannot lead to the harm.") ++
  (R.risk.requiredAlternatives.flatMap fun (w, ks) => ks.map fun k =>
    s!"Every decision that lists {(VE.Bridge.lookup R.risk.alternativeKinds w).getD w} also lists {(VE.Bridge.lookup R.risk.alternativeKinds k).getD k}.") ++
  (R.risk.requiredEstimators.map fun (k, es) => s!"Only estimates of {k} by {" or ".intercalate es} are accepted.")

def regenerated (src : RiskSource) : List (String × Json) :=
  let R := src.R
  let A := toAlt R
  [("environment_id", .str R.policy.1), ("document_hash", .str R.policy.2),
   ("e_risk", Json.mkObj [("sort", .str R.sev), ("classes", toJson R.classes),
      ("predicates", Json.mkObj ((genPredList R).map fun (p, ss) => (p, toJson ss))),
      ("words", Json.mkObj [(orWorseName, toJson [R.alt.harm, R.sev]), (lessWorstName, toJson [R.alt.action, R.alt.action])])]),
   ("legend", toJson (legend src)),
   ("risk_premises", labelled (riskPremiseLabels R) (riskPremises R)),
   ("unranked_severities", toJson ((unrankedSeverities R).map fun (a, b) => [a, b])),
   ("inlined", Json.arr ((VE.Alternatives.inlineTree A).T.nodes.map VE.Alternatives.Wire.encodeNode).toArray),
   ("alternatives", labelled (VE.Alternatives.altPremiseLabels A) (VE.Alternatives.altPremises A)),
   ("base_premises", labelled R.labels A.Γ),
   ("followable", Json.mkObj [("ast", enc (VE.Alternatives.allFollowable A)),
     ("followable", enc (VE.Alternatives.followableF A)), ("clear", enc (VE.Alternatives.clearF A))]),
   ("unmapped_obligations", Json.arr ((VE.Alternatives.Wire.unmappedObligations A).map (fun r =>
     Json.mkObj [("obligation", .str r.name), ("act", .str (r.act.getD ""))])).toArray)] ++
  VE.Norms.Wire.regenerated (VE.Alternatives.inlineTree A)

end VE.Risk.Wire
