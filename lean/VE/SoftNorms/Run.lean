import VE.SoftNorms.Admission
import VE.Norms.Run

/-! The `ve_service` mode `soft-norms` (docs/spec/soft-norms.md 9.4), formerly the one-shot `ve_soft_norms_route`. Each case is
`{"id", "environment", "kind", ...}`; a `soft-norms@0` environment must also
enable `norms@0`.

* `soft-elaborate`: `norms` → `environment_prime`, `decisions`, `derived`,
  `order`, `background` (with the `soft` slot and its labels), `premises`
  (`layer:norms:<p>` on `T′`), `colliding_pairs`, `conflict_targets`,
  `conditional_on`, `fragment`, `warnings`; or the shared diagnostic.
* `soft-pairs`: `norms` and `pairs` (label → a classification package or a
  `witness`) → per pair RANK-RESOLVED / DISJOINT / WEIGHING POINT / UNKNOWN
  (`Status.lean`), the discharged and open labels.
* `soft-conflict`: `packages` (target → package over `Background_base′`) →
  `CONFLICT-FREE` with `conditional_on`, or `UNKNOWN`
  (`Wire.soft_wire_conflict_sound`); or `witness` → `CONFLICT` classified as a
  strict collision or a pair conflict (`Wire.soft_wire_conflict_witness_sound`).
* `soft-certificate`: `premises`, `conclusion`, `certificate` bound to
  `background′ ++ layer premises ++ premises` over `E′` → `valid`
  (`Wire.soft_wire_acceptance`).
* `admission`: a W2 document with soft norm units (`Run.soft_wire_acceptance`).
* A case without a soft construct is delegated unchanged to W1's
  `Norms.Run.runCase` (which delegates P0 cases to `Route.Run.runCase`); a soft
  input never falls back after a failed soft decode. -/
namespace VE.SoftNorms.Run
open Lean
open VE.Norms
open VE.SoftNorms.Wire

/-- A soft construct: the `soft-norms@0` profile, the vocabulary's `soft` block, an
`instruction_of`, a soft field on a norm object, or a `soft-*` case kind. -/
def usesSoftPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let profile := match env.getObjValD "profiles" with
    | .arr ps => ps.toList.contains (.str softProfile)
    | _ => false
  let vocab := env.getObjValD "vocabulary"
  let block := (vocab.getObjVal? "soft").toBool
  let attributed := match vocab.getObjValD "predicates" with
    | .obj kvs => kvs.toList.any (fun (_, e) => (e.getObjVal? "instruction_of").toBool)
    | _ => false
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "soft-"
    | _ => false
  let softField (n : Json) := softKeys.any (fun k => ((n.getObjValD "norm").getObjVal? k).toBool)
  let normsSoft := match j.getObjValD "norms" with
    | .arr ns => ns.toList.any softField
    | _ => false
  let unitSoft := match (j.getObjValD "document").getObjValD "units" with
    | .arr units => units.toList.any (fun u => softField (u.getObjValD "content"))
    | _ => false
  profile || block || attributed || kind || normsSoft || unitSoft

/-! ## Pair classification -/

def classificationPackage (src : SoftSource) (environment norms : Json) (M N : SoftNode) (package : Json) :
    Option VE.Tableau.Certificate := Id.run do
  let label := cohLabel M N
  let some baseEnv := (basePrimeJson src.D environment).toOption | none
  let some baseProfiles := (VE.Bridge.strings (baseEnv.getObjValD "profiles")).toOption | none
  let some canonical := (Norms.Wire.canonicalEnvironmentJson environment).toOption | none
  let some envId := (VE.Route.Wire.environmentId src.se.profiles canonical).toOption | none
  let some docHash := (softDocumentHash src.se.profiles environment norms).toOption | none
  unless package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash &&
      package.getObjValD "target" == .str label do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  match VE.Route.Wire.bindingOk baseProfiles baseEnv ((classificationBackground src.D).map enc)
      (enc (cohPremise src.D M N)) c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
  | .ok () => some c
  | .error _ => none

/-- A weighing-point witness: a base model over `E′_base` passing `Background_base(E′) ++ Exc_T`
and a typed tuple at which both rules select (`weighing_point_sound`). -/
def weighingWitness (src : SoftSource) (M N : SoftNode) (w : Json) : Except String Bool := do
  let ⟨Mo, _⟩ ← decodeModel src w
  unless classificationBackgroundValid src.D Mo do throw (VE.Route.Wire.invalidModel "soft background")
  let ids ← VE.Bridge.strings (← w.getObjVal? "tuple")
  let sorts := actSorts src.D M
  let tuple := sorts.zip ids
  unless ids.length == sorts.length && VE.Bridge.tupleCheck Mo sorts tuple do
    throw "InvalidInput: witness tuple has the wrong length or sort"
  pure ((VE.Formula.and (circ src.D (selects' src.D M)) (circ src.D (selects' src.D N))).eval Mo (tupleVal tuple))

def classify (src : SoftSource) (environment norms pairs : Json) (M N : SoftNode) :
    Except String (PairStatus × String) := do
  if Comparable src.D M N then return (.rankResolved, "")
  let evidence := pairs.getObjValD (cohLabel M N)
  if (evidence.getObjVal? "witness").toBool then
    if ← weighingWitness src M N (evidence.getObjValD "witness") then return (.weighingPoint, "witness")
    else return (.unknown, "witness does not select both rules")
  if (evidence.getObjVal? "certificate").toBool then
    match classificationPackage src environment norms M N evidence with
    | some c =>
      if VE.Tableau.checkCertificate (envAt (soften src.D) 0) (classificationBackground src.D)
          (cohPremise src.D M N) c then return (.disjoint, "")
      else return (.unknown, "invalid certificate")
    | none => return (.unknown, "unbound certificate")
  return (.unknown, "no evidence")

def pairsResult (src : SoftSource) (environment norms pairs : Json) : Except String (List (String × Json)) := do
  let rows ← (collidingPairs src.D).mapM fun (M, N) => do
    let (st, detail) ← classify src environment norms pairs M N
    pure (cohLabel M N, st, Json.mkObj ([("pair", toJson [M.name, N.name]), ("label", .str (cohLabel M N)),
      ("status", .str st.text)] ++ (if detail.isEmpty then [] else [("detail", .str detail)])))
  let discharged := rows.filterMap (fun (l, st, _) =>
    if st == .rankResolved || st == .disjoint then some l else none)
  let open_ := rows.filterMap (fun (l, st, _) =>
    if st == .rankResolved || st == .disjoint then none else some l)
  pure [("pairs", Json.arr (rows.map (·.2.2)).toArray), ("discharged", toJson discharged),
    ("weighing_points", toJson open_)]

def openAfterClassification (src : SoftSource) (environment norms pairs : Json) : Except String (List String) := do
  let rows ← (collidingPairs src.D).mapM fun (M, N) => do
    let (status, _) ← classify src environment norms pairs M N
    pure (cohLabel M N, status)
  pure (rows.filterMap fun (label, status) =>
    if status == .rankResolved || status == .disjoint then none else some label)

/-- Preserve premise positions while disabling a set of open coherence leaves.
The certificate's binding remains to the original complete premise list. -/
def softWithout (D : SoftDoc) (labels : List String) : List VE.Formula :=
  (softLabelled D).map (fun (l, f) => if labels.contains l then .top else f)

def conflictValidWithout (r : SoftConflictReplay) (labels : List String) : Bool :=
  ((targets (soften r.src.D)).zip r.certs).all (fun (t, c) => match c with
    | some c => VE.Tableau.checkCertificate (envAt (soften r.src.D) 0)
        (VE.Norms.backgroundBase (soften r.src.D) ++ softWithout r.src.D labels)
        (targetConclusion t) c
    | none => false)

def entailmentValidWithout (r : SoftEntailmentReplay) (labels : List String) : Bool :=
  VE.Tableau.checkCertificate (envAt (soften r.src.D) (size (soften r.src.D)))
    (VE.Norms.background (soften r.src.D) ++ softWithout r.src.D labels ++
      elaborate (soften r.src.D).T ++ r.premises) r.conclusion r.cert

/-- Keep a sufficient set of open premises. A leaf is removed only if every certificate
still replays after all earlier removals; independent single-leaf checks are insufficient
when two leaves can substitute for one another. -/
def sufficientCoherence (openLabels : List String) (validWithout : List String → Bool) : List String :=
  let removed := openLabels.foldl (fun removed label =>
    if validWithout (label :: removed) then label :: removed else removed) []
  openLabels.filter (!removed.contains ·)

/-! ## Admission -/

/-- The answer for an admitted document: W1's fields and `conditional_on`. -/
def encodeAdmitted (id reportId : String) (res : Admission.Admitted) : Json :=
  VE.Route.Wire.ok id [("admitted", .bool true), ("report", Norms.Run.reportJson res.report),
    ("report_id", .str reportId), ("kinds", Json.arr res.kinds.toArray),
    ("conditional_on", toJson (Admission.conditionalOn res))]

def runAdmission (id : String) (environment document : Json) : Except String Json := do
  let res ← Admission.admitDocument environment document
  let canonical ← Norms.Wire.canonicalEnvironmentJson environment
  let envId ← VE.Route.Wire.environmentId res.src.se.profiles canonical
  let reportId ← VE.CertificateWire.digest (Norms.Run.reportDomain res.src.se.profiles)
    (Norms.Run.reportPayload envId document res.report)
  return encodeAdmitted id reportId res

/-- Every binding is the recomputed one: certificates name the regenerated `E′` and their source
ASTs, and the report id is the digest of the canonical environment id, the complete source
document and the checked report. -/
def BindingsMatchSourceAndRegeneration (environment document : Json) (res : Admission.Admitted)
    (reportId : String) : Prop :=
  Admission.CertificatesBound environment res ∧
  ∃ canonical envId, Norms.Wire.canonicalEnvironmentJson environment = .ok canonical ∧
    VE.Route.Wire.environmentId res.src.se.profiles canonical = .ok envId ∧
    VE.CertificateWire.digest (Norms.Run.reportDomain res.src.se.profiles)
      (Norms.Run.reportPayload envId document res.report) = .ok reportId

/-- W1's `AdmissionAnswer` with the soft decoder: the answer is exactly the encoding of a
checked admission whose bindings equal the recomputed digests and the regenerated `E′`, `T′`,
layer, `background:profile` and `soft:*` leaves, and whose report follows from
`background′ ++ elaborate T′` and its remaining assumptions. -/
def SoftAdmissionAnswer (id : String) (environment document answer : Json) : Prop :=
  ∃ res : Admission.Admitted, ∃ reportId : String,
    Admission.admitDocument environment document = .ok res ∧
    WellFormedSoft res.src.D = true ∧
    answer = encodeAdmitted id reportId res ∧
    Admission.SourceDecoded environment document res ∧
    BindingsMatchSourceAndRegeneration environment document res reportId ∧
    Admission.ReportAdmitted res ∧
    (∀ S : VE.Structure.{0}, S.Admissible (envPrime res.src.D) →
      Sat S (VE.Data.Background.generate res.doc.flags) →
      Sat S (background' res.src.D ++ elaborate (soften res.src.D).T) →
      Sat S ((Admission.otherAssumptions res).map (·.formula)) →
      res.report.root.formula.denote S [])

open VE.Order.ProfileGate (bind_ok) in
theorem runAdmission_sound (id : String) (environment document answer : Json)
    (h : runAdmission id environment document = .ok answer) :
    SoftAdmissionAnswer id environment document answer := by
  unfold runAdmission at h
  obtain ⟨res, hr, h⟩ := bind_ok h
  obtain ⟨canonical, hc, h⟩ := bind_ok h
  obtain ⟨envId, he, h⟩ := bind_ok h
  obtain ⟨reportId, hd, h⟩ := bind_ok h
  cases h
  obtain ⟨hsrc, hbound, hsound, hnodes, hleaves, hcit, hch⟩ :=
    Admission.admitDocument_spec.{0} environment document res hr
  exact ⟨res, reportId, hr, res.src.wf, rfl, hsrc, ⟨hbound, canonical, envId, hc, he, hd⟩,
    ⟨hsound, hnodes, hleaves, hcit, hch⟩,
    fun S hS hf hg ho => Admission.soft_wire_report_consequence environment document res hr S hS hf hg ho⟩

/-! ## Dispatch -/

def witnessKind (t : String × List String × VE.Formula) : String :=
  if (t.1.splitOn "->").length > 1 then s!"pair conflict on {t.1}" else s!"strict collision on {t.1}"

/-- A situation supplied by a searcher is checked against the regenerated base vocabulary.
Warnings are emitted only for a model with a typed tuple and the exception premises. -/
def warningSituation (src : SoftSource) (sorts : List String) (w : Json) :
    Except String (VE.FiniteModel VE.Bridge.Entity × List VE.Bridge.Entity × List String) := do
  let ⟨model, _⟩ ← decodeModel src w
  unless classificationBackgroundValid src.D model do
    throw (VE.Route.Wire.invalidModel "soft background")
  let ids ← VE.Bridge.strings (← w.getObjVal? "tuple")
  let tuple := sorts.zip ids
  unless ids.length == sorts.length && VE.Bridge.tupleCheck model sorts tuple do
    throw "InvalidInput: witness tuple has the wrong length or sort"
  pure (model, tuple, ids)

def warningRule (D : SoftDoc) (name : String) : Except String SoftNode :=
  match D.T.nodes.find? (·.name == name) with
  | some N => pure N
  | none => throw s!"InvalidInput: unknown soft rule {name}"

def overlapLine (src : SoftSource) (w : Json) : Except String Json := do
  let names ← VE.Bridge.strings (← w.getObjVal? "pair")
  unless names.length == 2 && names[0]! < names[1]! do
    throw "InvalidInput: overlap pair must name two distinct sorted rules"
  let M ← warningRule src.D names[0]!
  let N ← warningRule src.D names[1]!
  unless M.mode == .default && N.mode == .default && M.pred == N.pred && M.sign == N.sign do
    throw "InvalidInput: overlap pair must have the same predicate, sign and default mode"
  let (model, tuple, ids) ← warningSituation src (actSorts src.D M) w
  unless (circ src.D (selects' src.D M)).eval model (tupleVal tuple) &&
      (circ src.D (selects' src.D N)).eval model (tupleVal tuple) do
    throw "InvalidInput: overlap witness does not select both rules"
  pure (Json.mkObj [("pair", toJson names), ("tuple", toJson ids),
    ("model", w.getObjValD "model"), ("line", .str s!"Overlap({M.name}, {N.name})")])

/-- `M` is preferred to `N` at this tuple, using the same act-indexed finding
that the direct soft semantics uses for dominance. -/
def preferredAt (D : SoftDoc) (model : VE.FiniteModel VE.Bridge.Entity)
    (tuple : List VE.Bridge.Entity) (M N : SoftNode) : Bool :=
  let finding := (outweighsF D (act D M) (rk (if higher D M N then N else M))
    (rk (if higher D M N then M else N))).eval model (tupleVal tuple)
  (higher D M N && !finding) || (higher D N M && finding)

def overrideCycleLine (src : SoftSource) (w : Json) : Except String Json := do
  let names ← VE.Bridge.strings (← w.getObjVal? "cycle")
  unless names.length >= 3 && names.eraseDups.length == names.length do
    throw "InvalidInput: override cycle needs at least three distinct rules"
  let rules ← names.mapM (warningRule src.D)
  let some first := rules.head? | throw "InvalidInput: empty override cycle"
  let some last := rules.getLast? | throw "InvalidInput: empty override cycle"
  unless src.D.soft.outranking == .holistic && rules.all (fun N =>
      N.mode == .default && act src.D N == act src.D first &&
      actSorts src.D N == actSorts src.D first) do
    throw "InvalidInput: override cycle needs holistic defaults on one act"
  let (model, tuple, ids) ← warningSituation src (actSorts src.D first) w
  unless rules.all (fun N => (eligibleF src.D N).eval model (tupleVal tuple)) do
    throw "InvalidInput: override cycle witness has an ineligible rule"
  let edges := (rules.zip (rules.drop 1)) ++ [(last, first)]
  unless edges.all (fun (M, N) => Incompatible src.D M N && preferredAt src.D model tuple M N) do
    throw "InvalidInput: override cycle witness has a missing preference edge"
  pure (Json.mkObj [("cycle", toJson names), ("tuple", toJson ids),
    ("model", w.getObjValD "model"),
    ("line", .str ("override_cycles: " ++ String.intercalate " > " (names ++ [names.head!])))])

def warningRows (src : SoftSource) (j : Json) : Except String (Option (List Json) × Option (List Json)) := do
  let overlaps ← match (j.getObjVal? "overlap_witnesses").toOption with
    | none => pure none
    | some raw => do
      let ws ← raw.getArr?
      pure (some (← ws.toList.mapM (overlapLine src)))
  let cycles ← match (j.getObjVal? "override_cycle_witnesses").toOption with
    | none => pure none
    | some raw => do
      let ws ← raw.getArr?
      pure (some (← ws.toList.mapM (overrideCycleLine src)))
  pure (overlaps, cycles)

/-- The non-admission soft case kinds. -/
def documentIdentityEnvironment (source request : Json) : Except String (Json × List String) := do
  match (request.getObjVal? "identity_environment").toOption with
  | none => pure (source, ← VE.Bridge.strings (← source.getObjVal? "profiles"))
  | some original =>
    let profiles ← VE.Bridge.strings (← original.getObjVal? "profiles")
    unless profiles.contains "readings@1" do
      throw "InvalidInput: identity environment has no readings@1 profile"
    let lowered := original.setObjVal! "profiles"
      (toJson (profiles.filter (· != "readings@1")))
    unless lowered == source do
      throw "InvalidInput: identity environment differs from the soft source"
    pure (original, profiles)

def runSoftKind (id kind : String) (j : Json) : Except String Json := do
  if kind == "soft-rule" then
    let environment ← j.getObjVal? "environment"
    let src ← decodeSoftSource environment (toJson ([] : List Json))
    let _ ← decodeSoftNorm src.se (← j.getObjVal? "norm")
    return VE.Route.Wire.ok id [("accepted", .bool true)]
  if kind == "soft-rules" then
    let environment ← j.getObjVal? "environment"
    let src ← decodeSoftSource environment (toJson ([] : List Json))
    let norms ← (← j.getObjVal? "norms").getArr?
    let results := norms.toList.map (fun norm =>
      match decodeSoftNorm src.se norm with
      | .ok _ => Json.mkObj [("status", .str "ok")]
      | .error error => Json.mkObj [("status", .str "error"), ("error", .str error)])
    return VE.Route.Wire.ok id [("results", Json.arr results.toArray)]
  if kind == "soft-elaborate" then
    let environment ← j.getObjVal? "environment"
    let norms := j.getObjValD "norms"
    let src ← decodeSoftSource environment norms
    let (identityEnvironment, identityProfiles) ← documentIdentityEnvironment environment j
    let documentHash ← softDocumentHash identityProfiles identityEnvironment norms
    let extra ← warningRows src j
    return VE.Route.Wire.ok id (regenerated src.D identityEnvironment ++
      [("document_hash", .str documentHash)] ++
      extra.1.toList.map (fun value => ("overlaps", toJson value)) ++
      extra.2.toList.map (fun value => ("override_cycles", toJson value)))
  if kind == "soft-pairs" then
    let environment ← j.getObjVal? "environment"
    let norms := j.getObjValD "norms"
    let src ← decodeSoftSource environment norms
    return VE.Route.Wire.ok id (← pairsResult src environment norms (j.getObjValD "pairs"))
  if kind == "soft-certificate" then
    let r ← replaySoftEntailment j
    let openLabels ← openAfterClassification r.src (j.getObjValD "environment")
      (j.getObjValD "norms") (j.getObjValD "pairs")
    let conditional := if r.valid then sufficientCoherence openLabels (entailmentValidWithout r) else []
    return VE.Route.Wire.ok id [("valid", .bool r.valid),
      ("background", toJson (background' r.src.D).length), ("layers", toJson (elaborate (soften r.src.D).T).length),
      ("conditional_on", toJson conditional)]
  if kind == "soft-conflict" && (j.getObjVal? "witness").toBool then
    let ⟨src, w⟩ ← replaySoftWitness j
    let names ← VE.Bridge.strings ((j.getObjValD "witness").getObjValD "tuple")
    let situation := String.intercalate ", " names
    return VE.Route.Wire.ok id ([("verdict", .str (if w.conflict then "CONFLICT" else "UNKNOWN")),
      ("target", .str w.target.1), ("targets", toJson ((targets (soften src.D)).map (·.1))),
      ("status_text", .str (if w.conflict then s!"CONFLICT: {witnessKind w.target} at {situation}"
                            else s!"UNKNOWN: {w.target.1}, budget 10000"))] ++
      (if w.conflict then [("witness_kind", .str (witnessKind w.target))] else []))
  if kind == "soft-conflict" then
    let res ← replaySoftConflict j
    let verdict := if res.conflictFree then "CONFLICT-FREE" else "UNKNOWN"
    let openLabels ← openAfterClassification res.src (j.getObjValD "environment")
      (j.getObjValD "norms") (j.getObjValD "pairs")
    let conditional := if res.conflictFree then sufficientCoherence openLabels (conflictValidWithout res) else []
    let budget := (j.getObjValD "budget").getNat?.toOption.getD 10000
    let exhibit ← if (j.getObjVal? "coherent_model").toBool then do
      let ⟨model, _⟩ ← decodeModel res.src
        (Json.mkObj [("model", j.getObjValD "coherent_model")])
      unless backgroundValid' res.src.D model do
        throw (VE.Route.Wire.invalidModel "soft background")
      pure true
    else pure false
    let statusText := if res.conflictFree then
      s!"CONFLICT-FREE among rules on the same act, conditional on {conditional.length} coherence premises; {conditional.length} weighing points open; coherent situation exhibited: {if exhibit then "yes" else s!"UNKNOWN (budget {budget})"}"
      else s!"UNKNOWN: {(firstFailure res).getD "target unspecified"}, budget {budget}"
    return VE.Route.Wire.ok id ([("verdict", .str verdict),
      ("status_text", .str statusText),
      ("coherent_exhibit", .bool exhibit),
      ("budget", toJson budget),
      ("targets", toJson ((targets (soften res.src.D)).map (·.1))),
      ("conditional_on", toJson conditional)] ++
      match firstFailure res with
      | some d => if res.conflictFree then [] else [("detail", .str d)]
      | none => [])
  throw s!"UnsupportedProfile: case kind {kind} is not available on the soft-norms route"

def runCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if kind == "admission" && usesSoftPath j then
    let environment ← j.getObjVal? "environment"
    let document ← j.getObjVal? "document"
    return ← runAdmission id environment document
  if !usesSoftPath j then return ← Norms.Run.runCase j
  runSoftKind id kind j

open VE.Order.ProfileGate (bind_ok) in
/-- The public admission branch: from raw JSON, a successful soft `admission` answer satisfies
the full admission obligation for the case's own id, environment and document; no successful
soft input falls through to W1 or P0. -/
theorem soft_wire_acceptance (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : usesSoftPath j = true) :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
      SoftAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "admission" := by rw [hkind] at hk; cases hk; rfl
  subst kind
  simp only [beq_self_eq_true, Bool.true_and, hn, ↓reduceIte] at h
  obtain ⟨environment, he, h⟩ := bind_ok h
  obtain ⟨document, hd, h⟩ := bind_ok h
  have he' : j.getObjValD "environment" = environment := by
    simp only [Json.getObjValD, he]; rfl
  have hd' : j.getObjValD "document" = document := by
    simp only [Json.getObjValD, hd]; rfl
  rw [he', hd']
  exact ⟨id, hid, runAdmission_sound id environment document answer (by simpa using h)⟩

/-- Stable classes from docs/spec/soft-norms.md §8; details stay in `error`. -/
def softDiagnosticCode (message : String) : String := Id.run do
  if message.startsWith "InvalidInput: rule " && message.endsWith " needs an exception" then
    return "SOFT_MISSING_EXCEPTION"
  if message.startsWith "InvalidInput: rule " &&
      message.endsWith " is strict and declares an exception" then
    return "SOFT_STRICT_EXCEPTION"
  let prefixes : List (String × String) := [
    ("InvalidInput: invalid ties pair", "SOFT_INVALID_TIES_PAIR"),
    ("InvalidInput: invalid outranks pair", "SOFT_INVALID_OUTRANKS_PAIR"),
    ("InvalidInput: invalid soft block", "SOFT_INVALID_BLOCK"),
    ("InvalidInput: invalid outranking flag", "SOFT_INVALID_OUTRANKING"),
    ("InvalidInput: invalid decider", "SOFT_INVALID_DECIDER"),
    ("MissingExceptionDecider:", "SOFT_MISSING_DECIDER"),
    ("InvalidInput: strict outranking has no decider", "SOFT_STRICT_OUTRANKING_DECIDER"),
    ("InvalidInput: invalid soft name", "SOFT_INVALID_NAME"),
    ("DuplicateDeclaration:", "SOFT_DUPLICATE_DECLARATION"),
    ("UnknownRank:", "SOFT_UNKNOWN_RANK"),
    ("TieAgainstOrder:", "SOFT_TIE_AGAINST_ORDER"),
    ("DependencyCycle:", "SOFT_DEPENDENCY_CYCLE"),
    ("UnknownSymbol: party", "SOFT_UNKNOWN_PARTY"),
    ("InvalidInput: exception sufficient must be an array", "SOFT_EXCEPTION_ARRAY"),
    ("InvalidInput: exception necessary must be an array", "SOFT_EXCEPTION_ARRAY"),
    ("InvalidInput: invalid factors", "SOFT_INVALID_FACTORS"),
    ("InvalidInput: alterable of rule", "SOFT_INVALID_ALTERABLE"),
    ("HardConstraintAltered:", "SOFT_HARD_CONSTRAINT"),
    ("InvalidInput: exception condition of rule", "SOFT_INVALID_EXCEPTION_CONDITION"),
    ("SoftOverHard:", "SOFT_OVER_HARD"),
    ("ResourceLimit:", "SOFT_RESOURCE_LIMIT"),
    ("UnsupportedProfile:", "SOFT_UNSUPPORTED_PROFILE"),
    ("InvalidInput: invalid soft fields", "SOFT_INVALID_RULE_FIELDS"),
    ("InvalidInput: invalid mode for rule", "SOFT_INVALID_RULE_FIELDS"),
    ("InvalidInput: hard of rule", "SOFT_INVALID_RULE_FIELDS")]
  if let some (_, code) := prefixes.find? (fun (pfx, _) => message.startsWith pfx) then
    return code
  if message.startsWith "InvalidInput: " && message.endsWith " must be an array" then
    return "SOFT_INVALID_ARRAY"
  return "SOFT_INVALID_INPUT"

/-- The code of a reported soft error: the failed check of the validation table (8) when the
error is that table's first diagnostic for the case's source, else the stable prefix above.
The code comes from the check, never from substrings of the message. -/
def reportedCode (j : Json) (message : String) : String :=
  let norms := if j.getObjValD "kind" == .str "admission" then
      match VE.Norms.Admission.splitDocument (j.getObjValD "document") with
      | .ok (_, active, _) => active
      | .error _ => .null
    else j.getObjValD "norms"
  match Phases.checkSource (j.getObjValD "environment") norms with
  | .error f => if f.message == message then f.code else softDiagnosticCode message
  | .ok _ => softDiagnosticCode message

/-- A cycle introduced by the soft derived guard, after the source tree itself
passes W1's dependency check. This is the English rewrite hint's condition. -/
def dualGuardCycle (j : Json) (message : String) : Bool :=
  if !message.startsWith "DependencyCycle:" then false else
    match Phases.checkSource (j.getObjValD "environment") (j.getObjValD "norms") with
    | .error _ => false
    | .ok c =>
      let D : SoftDoc := ⟨c.ne.rv.environment, c.ne.rv.literals, c.soft,
        ⟨c.ne.regulated, [], c.nodes⟩⟩
      (validateW1 D.base).isOk &&
        match validateW1 (soften D) with
        | .error e => e == message
        | .ok _ => false

def runCaseReported (j : Json) : Json :=
  if usesSoftPath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj ([("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str message), ("code", .str (reportedCode j message))] ++
        if dualGuardCycle j message then [("dual_guard_cycle", .bool true)] else [])
  else Norms.Run.runCaseReported j

end VE.SoftNorms.Run
