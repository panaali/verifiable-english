import VE.Rights.Route
import VE.SoftNorms.Run

/-! The rights decoder and replays (docs/spec/rights.md 3, 9.3 and 9.4).

The soft decoder does not know `rights@0` or the vocabulary's `rights` block.
`decodeRightsEnvironment` checks the profile triple, strips exactly the block and the
profile, decodes the rest with soft's unchanged `decodeSoftEnvironment`, decodes the block
strictly (unknown fields rejected) and keeps the original complete environment for
identity. The document is the array of unit contents of 3.2: `{"right": …}`,
`{"right_lines": …}` (appended to its right's lines), `{"limitation": …}`, `{"bar": …}`
and the norm units outside rights (`{"norm": …}`, with an optional `cites` beside
`norm`), plus at most one `{"source_units": [ids]}`, the source unit ids every `cites`
entry must name (`UnknownSymbol: unit <u>` otherwise; none declared means no citation is
valid). The frozen restricted JSON parser rejects `null`, so the optional fields
`holder_slot`, `recognition`, `decided_by` and a fan-out line's `predicate` are sent
absent instead.

Nothing on the wire supplies an elaboration: `E″`, `T″`, `Lim_D`, `Exc_T`, `Coh_T`,
`Background_base″`, `background″`, the layer premises, conflict targets and scope
targets are regenerated from the decoded `RightsDoc`, and certificates are replayed by
the unchanged tableau checker. Bindings (all recomputed here):

* identity: `environment_id` over the original canonical environment with its profiles;
  the rights document hash (`ve-rights-<identity version>`) over the canonical unit
  array, soft fields at their default values omitted (3.5);
* conflict and scope packages: outer `(environment_id, document_hash, target)`, inner
  certificate bound to the regenerated `E″′_base` JSON (`basePrimeJsonR`),
  `Background_base″` and the target's conclusion;
* entailment certificates: the regenerated full `E″′` JSON (`primeJsonR`),
  `background″ ++ layer premises ++ Γ` and the conclusion. -/
namespace VE.Rights.Wire
open Lean
open VE.Norms
open VE.Bridge (exactFields fields stringField strings)
open VE.SoftNorms (SoftNode SoftDoc soften decisions)
open VE.SoftNorms.Wire (SoftEnvironment stripSoft withDecisions enc softProfile)
open VE.Order.ProfileGate (bind_ok)

def rightsProfile : String := "rights@0"

/-! ## The environment -/

/-- The environment without its rights constructs. -/
def stripRights (environment : Json) : Except String Json := do
  let profiles ← strings (← environment.getObjVal? "profiles")
  let vocab ← environment.getObjVal? "vocabulary"
  let vocab' := Json.mkObj ((← fields vocab).filter (·.1 != "rights"))
  pure ((environment.setObjVal! "profiles" (toJson (profiles.filter (· != rightsProfile)))).setObjVal!
    "vocabulary" vocab')

def invalidBlock : String := "InvalidInput: invalid rights block"

def optStrings (j : Json) (k : String) : Except String (List String) :=
  match j.getObjVal? k with
  | .error _ => pure []
  | .ok v => match strings v with
    | .ok xs => pure xs
    | .error _ => throw invalidBlock

def optString (j : Json) (k : String) (bad : String) : Except String (Option String) :=
  match j.getObjVal? k with
  | .error _ => pure none
  | .ok (.str s) => pure (some s)
  | .ok _ => throw bad

/-- The environment `rights` block (3.1). -/
def decodeRightsBlock (vocab : Json) : Except String RightsEnv := do
  let b ← match vocab.getObjVal? "rights" with
    | .ok b => pure b
    | .error _ => throw invalidBlock
  match VE.Bridge.displayFields b ["holders", "bearers"] ["protected", "alters"] with
  | .ok () => pure ()
  | .error _ => throw invalidBlock
  let holders ← optStrings b "holders"
  let bearers ← optStrings b "bearers"
  let prot ← optStrings b "protected"
  let alters ← match b.getObjVal? "alters" with
    | .error _ => pure []
    | .ok a => do
      let entries ← match fields a with
        | .ok es => pure es
        | .error _ => throw invalidBlock
      entries.mapM fun (act, e) => do
        match VE.Bridge.displayFields e ["holder_slot", "status"] ["recognition"] with
        | .ok () => pure ()
        | .error _ => throw s!"InvalidInput: alters {act}"
        let slot ← match (e.getObjValD "holder_slot").getNat? with
          | .ok n => pure n
          | .error _ => throw s!"InvalidInput: alters {act}"
        let status ← match e.getObjValD "status" with
          | .str s => pure s
          | _ => throw s!"InvalidInput: alters {act}"
        let recognition ← optString e "recognition" s!"InvalidInput: alters {act}"
        pure (⟨act, slot, status, recognition⟩ : AltersEntry)
  pure ⟨holders, bearers, prot, alters⟩

/-- A decoded rights environment: soft's decoding of the stripped environment, the rights
block and the original JSON with its original profiles. -/
structure RightsEnvironment where
  se : SoftEnvironment
  block : RightsEnv
  profiles : List String
  json : Json

def decodeRightsEnvironment (environment : Json) : Except String RightsEnvironment := do
  let profiles ← match environment.getObjVal? "profiles" >>= strings with
    | .ok ps => pure ps
    | .error _ => throw (VE.Route.Gate.unsupported "profiles must be a sorted unique array")
  unless profiles.contains rightsProfile do throw "UnsupportedProfile: rights@0 is required"
  unless profiles.contains softProfile do throw "UnsupportedProfile: rights@0 requires soft-norms@0"
  unless profiles.contains "norms@0" do throw "UnsupportedProfile: rights@0 requires norms@0"
  let vocab ← environment.getObjVal? "vocabulary"
  let block ← decodeRightsBlock vocab
  let stripped ← stripRights environment
  let checked ← match VE.SoftNorms.Phases.checkSource stripped (.arr #[]) with
    | .ok checked => pure checked
    | .error fault => throw fault.message
  let se : SoftEnvironment := ⟨checked.ne, checked.soft, checked.profiles, stripped⟩
  pure ⟨se, block, profiles, environment⟩

/-! ## Units (3.2) -/

def decodeCites (j : Json) : Except String (List (String × List String)) := do
  let kvs ← match fields j with
    | .ok kvs => pure kvs
    | .error _ => throw "InvalidInput: cites must be an object"
  kvs.mapM fun (k, v) => do
    let us ← match strings v with
      | .ok us => pure us
      | .error _ => throw s!"InvalidInput: cites {k} must list unit ids"
    if us.isEmpty then throw s!"InvalidInput: cites {k} must list unit ids"
    pure (k, us)

def optCites (j : Json) : Except String (List (String × List String)) :=
  match j.getObjVal? "cites" with
  | .error _ => pure []
  | .ok c => decodeCites c

/-- A soft norm object inside a line; a fan-out line's absent predicate is read as its first
mapped predicate (every instance replaces it). -/
def decodeLineNorm (se : SoftEnvironment) (raw : Json) (fanPred : Option String) : Except String SoftNode :=
  let raw' := match fanPred, raw.getObjVal? "predicate" with
    | some p, .error _ => raw.setObjVal! "predicate" (.str p)
    | _, _ => raw
  match VE.SoftNorms.Phases.ruleFields se.soft.exceptionDecider
      (Json.mkObj [("norm", raw')]) with
  | .ok N => .ok N
  | .error fault => .error fault.message

def decodeKind (j : Json) : Except String Kind :=
  match j with
  | .str "claim" => pure .claim
  | .str "liberty" => pure .liberty
  | .str "immunity" => pure .immunity
  | .str "power" => pure .power
  | _ => throw "InvalidInput: invalid line kind"

def decodeLine (se : SoftEnvironment) (j : Json) : Except String SourceLine := do
  VE.Bridge.displayFields j ["kind"] ["norm", "liberty", "recognition", "fan_out", "holder_slot", "cites"]
  let kind ← decodeKind (j.getObjValD "kind")
  let fanOut ← match j.getObjVal? "fan_out" with
    | .error _ => pure []
    | .ok v => do
      (← fields v).mapM fun (b, p) => do
        match p with
        | .str s => pure (b, s)
        | _ => throw "InvalidInput: invalid fan_out"
  let holderSlot ← match j.getObjVal? "holder_slot" with
    | .error _ => pure none
    | .ok v => some <$> v.getNat?
  let cites ← optCites j
  let fanPred := fanOut.head?.map (·.2)
  let opt (k : String) : Except String (Option SoftNode) :=
    match j.getObjVal? k with
    | .error _ => pure none
    | .ok raw => some <$> decodeLineNorm se raw fanPred
  pure ⟨kind, ← opt "norm", ← opt "liberty", ← opt "recognition", fanOut, holderSlot, cites⟩

def decodeLines (se : SoftEnvironment) (j : Json) : Except String (List SourceLine) := do
  (← (← j.getObjVal? "lines").getArr?).toList.mapM (decodeLine se)

def decodeRight (se : SoftEnvironment) (j : Json) : Except String Right := do
  VE.Bridge.displayFields j ["name", "holder", "lines"] ["guard"]
  let name ← stringField j "name"
  let holder ← stringField j "holder"
  let guard ← match j.getObjVal? "guard" with
    | .error _ => pure .top
    | .ok g => VE.Bridge.decodeFormula 64 g
  pure ⟨name, holder, guard, ← decodeLines se j⟩

def decodeCondition (j : Json) : Except String Condition := do
  VE.Bridge.displayFields j ["name", "role", "verbalisation"] ["decided_by", "purposes"]
  let name ← stringField j "name"
  let necessary ← match j.getObjValD "role" with
    | .str "necessary" => pure true
    | .str "sufficient" => pure false
    | _ => throw s!"InvalidInput: invalid condition {name}"
  let decidedBy ← optString j "decided_by" s!"InvalidInput: invalid decider for condition {name}"
  pure ⟨name, necessary, ← stringField j "verbalisation", decidedBy⟩

def decodeLimitation (j : Json) : Except String Limitation := do
  VE.Bridge.displayFields j ["name", "scope", "kinds", "conditions", "factors"] ["decided_by"]
  let name ← stringField j "name"
  let scope ← match j.getObjValD "scope" with
    | .str "all" => pure none
    | v => some <$> strings v
  let kinds ← match j.getObjValD "kinds" with
    | .str "all" => pure none
    | .arr ks => some <$> ks.toList.mapM decodeKind
    | _ => throw s!"InvalidInput: invalid kinds of limitation {name}"
  let decidedBy ← optString j "decided_by" s!"InvalidInput: invalid decider for limitation {name}"
  let conditions ← (← (j.getObjValD "conditions").getArr?).toList.mapM decodeCondition
  pure ⟨name, scope, kinds, decidedBy, conditions, ← strings (j.getObjValD "factors")⟩

def decodeBar (j : Json) : Except String Bar := do
  VE.Bridge.displayFields j ["name", "reading"] ["decided_by"]
  let name ← stringField j "name"
  let reading ← match j.getObjValD "reading" with
    | .str "rule" => pure Reading.rule
    | .str "query" => pure Reading.query
    | _ => throw s!"InvalidInput: invalid bar reading for {name}"
  pure ⟨name, reading, ← optString j "decided_by" s!"InvalidInput: invalid decider for bar {name}"⟩

/-- The units decoded so far, in document order. -/
structure Units where
  rs : List Right := []
  limits : List Limitation := []
  bars : List Bar := []
  outside : List SoftNode := []
  cites : List (String × List (String × List String)) := []
  order : List (String × SourceLine) := []
  sourceUnits : Option (List String) := none

def addUnit (se : SoftEnvironment) (acc : Units) (u : Json) : Except String Units := do
  let keys := (← fields u).map (·.1)
  if keys == ["source_units"] then
    if acc.sourceUnits.isSome then throw "InvalidInput: duplicate source_units"
    let ids ← match strings (u.getObjValD "source_units") with
      | .ok ids => pure ids
      | .error _ => throw "InvalidInput: source_units must list unit ids"
    pure { acc with sourceUnits := some ids }
  else if keys == ["right"] then
    let R ← decodeRight se (u.getObjValD "right")
    pure { acc with rs := acc.rs ++ [R], order := acc.order ++ R.lines.map (R.name, ·) }
  else if keys == ["right_lines"] then
    let j := u.getObjValD "right_lines"
    VE.Bridge.displayFields j ["right", "lines"] []
    let r ← stringField j "right"
    unless acc.rs.any (·.name == r) do throw s!"UnknownRight: {r}"
    let ls ← decodeLines se j
    let rs := acc.rs.map (fun R => if R.name == r then { R with lines := R.lines ++ ls } else R)
    pure { acc with rs := rs, order := acc.order ++ ls.map (r, ·) }
  else if keys == ["limitation"] then
    pure { acc with limits := acc.limits ++ [← decodeLimitation (u.getObjValD "limitation")] }
  else if keys == ["bar"] then
    pure { acc with bars := acc.bars ++ [← decodeBar (u.getObjValD "bar")] }
  else if keys.contains "norm" then
    VE.Bridge.displayFields u ["norm"] ["cites"]
    let N ← decodeLineNorm se (u.getObjValD "norm") none
    let cs ← optCites u
    pure { acc with outside := acc.outside ++ [N], cites := acc.cites ++ (if cs.isEmpty then [] else [(N.name, cs)]) }
  else throw "InvalidInput: invalid rights document unit"

/-! ## The decoded source -/

structure RightsSource where
  re : RightsEnvironment
  D : RightsDoc
  wf : WellFormedRights D = true
  env : D.soft.E = re.se.ne.rv.environment
  lits : D.soft.lits = re.se.ne.rv.literals
  defs : D.soft.T.definitions = []

/-- Decode the environment with its rights block and the document units (no W3 definitions or
W5 flags on this path) and run `WellFormedRights`; the diagnostics are those of `validateRights`. -/
def decodeRightsSource (environment document : Json) : Except String RightsSource := do
  let re ← decodeRightsEnvironment environment
  unless re.se.ne.rv.definitions.isEmpty do
    throw "UnsupportedProfile: rights route with definitions is not implemented"
  unless re.se.ne.rv.flags.isEmpty do
    throw "UnsupportedProfile: rights route with data flags is not implemented"
  let units ← match document with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: document must be an array"
  if units.length > 1024 then throw "ResourceLimit: units"
  let us ← units.foldlM (addUnit re.se) {}
  let D : RightsDoc :=
    ⟨⟨re.se.ne.rv.environment, re.se.ne.rv.literals, re.se.soft, ⟨re.se.ne.regulated, [], us.outside⟩⟩,
     re.block, us.rs, us.limits, us.bars, us.cites, some us.order, us.sourceUnits.getD []⟩
  match hv : validateRights D with
  | .error e => throw e
  | .ok () => pure ⟨re, D, by unfold WellFormedRights; rw [hv], rfl, rfl, rfl⟩

/-! ## Identity (3.5) -/

/-- A soft norm object with its soft fields at their default values omitted. -/
def canonicalRaw (raw : Json) : Json :=
  let keep := fun (kv : String × Json) => match kv with
    | ("mode", .str "strict") | ("alterable", .arr #[]) | ("hard", .bool false) => false
    | _ => true
  match raw with
  | .obj kvs => Json.mkObj (kvs.toList.filter keep)
  | _ => raw

def canonicalLine (l : Json) : Json :=
  ["norm", "liberty", "recognition"].foldl (fun acc k => match acc.getObjVal? k with
    | .ok raw => acc.setObjVal! k (canonicalRaw raw)
    | .error _ => acc) l

def canonicalLines (j : Json) : Json :=
  match j.getObjVal? "lines" with
  | .ok (.arr ls) => j.setObjVal! "lines" (.arr (ls.map canonicalLine))
  | _ => j

def canonicalUnit (u : Json) : Json :=
  match u.getObjVal? "norm", u.getObjVal? "right", u.getObjVal? "right_lines" with
  | .ok raw, _, _ => u.setObjVal! "norm" (canonicalRaw raw)
  | _, .ok r, _ => u.setObjVal! "right" (canonicalLines r)
  | _, _, .ok r => u.setObjVal! "right_lines" (canonicalLines r)
  | _, _, _ => u

def rightsDocumentHash (profiles : List String) (environment document : Json) : Except String String := do
  let envId ← VE.Route.Wire.environmentId profiles (← Norms.Wire.canonicalEnvironmentJson environment)
  let canon := match document with
    | .arr xs => Json.arr (xs.map canonicalUnit)
    | j => j
  VE.CertificateWire.digest s!"ve-rights-{VE.Route.Wire.identityVersion profiles}\n"
    (Json.mkObj [("environment_id", .str envId), ("document", canon)])

/-- The declared act phrase of a regulated predicate. -/
def actPhrase (D : RightsDoc) (p : String) : String := ((regOfName D p).bind (·.act)).getD ""

/-- A limitation's display number: its position in document order (2.1). -/
def limDisplay (D : RightsDoc) (L : String) : Nat := (D.limits.map (·.name)).idxOf L + 1

def condVerbalisation (D : RightsDoc) (L c : String) : String :=
  (((D.limits.find? (·.name == L)).bind (fun l => l.conditions.find? (·.name == c))).map (·.verbalisation)).getD ""

def generatedEntry (sorts : List String) (description verbalisation : String) : Json :=
  Json.mkObj [("arguments", toJson sorts), ("description", .str description), ("verbalisation", .str verbalisation)]

/-- Every rights-generated declaration of `E″` (the names and sorts of `genDecls`), with the
source keys in its description and its one generated wording (2.1): `lim` as `limitation <m>
holds where <act>`, `cond` as `<condition phrase> where <act>`, `aimed` as `<act> aimed at the
destruction of a right`. The Python profile generates the same bytes, so `E″′` and every
certificate binding over it agree. -/
def genEntries (D : RightsDoc) : List (String × Json) :=
  (limKeys D).map (fun k => (limName ((limKeys D).idxOf k + 1),
      generatedEntry (VE.SoftNorms.sortsOf D.soft k.2) s!"limitation {k.1} of {k.2}"
        s!"limitation {limDisplay D k.1} holds where {actPhrase D k.2}")) ++
  (condKeys D).map (fun k => (condName ((condKeys D).idxOf k + 1),
      generatedEntry (VE.SoftNorms.sortsOf D.soft k.2.1) s!"condition {k.2.2} of limitation {k.1} on {k.2.1}"
        s!"{condVerbalisation D k.1 k.2.2} where {actPhrase D k.2.1}")) ++
  (if D.bars = [] then [] else (barPreds D).map (fun m => (aimedName (barIndex D m),
      generatedEntry (VE.SoftNorms.sortsOf D.soft m) "act aimed at destruction of a right"
        s!"{actPhrase D m} aimed at the destruction of a right")))

def withGenerated (D : RightsDoc) (environment : Json) : Except String Json := do
  let vocab ← environment.getObjVal? "vocabulary"
  let preds ← fields (← vocab.getObjVal? "predicates")
  pure (environment.setObjVal! "vocabulary" (vocab.setObjVal! "predicates" (Json.mkObj (preds ++ genEntries D))))

/-- The regenerated `E″′_base`: no regulated predicate, no soft or rights construct, the
rights-generated and decision predicates as base predicates; profiles without `norms@0`,
`soft-norms@0` and `rights@0`. -/
def basePrimeJsonR (D : RightsDoc) (environment : Json) : Except String Json := do
  withDecisions (correlate D) (← withGenerated D (← Norms.Replay.baseEnvironmentJson (← stripSoft (← stripRights environment))))

/-- The regenerated full `E″′`: the canonical source environment plus the rights-generated and
decision predicates. -/
def primeJsonR (D : RightsDoc) (environment : Json) : Except String Json := do
  withDecisions (correlate D) (← withGenerated D (← Norms.Wire.canonicalEnvironmentJson environment))

/-! ## Packages (conflict and scope targets over `Background_base″`) -/

/-- A package's certificate, `none` unless the outer binding matches the source and the inner
binding matches `E″′_base`, `Background_base″` and the conclusion. -/
def decodeRightsPackage (src : RightsSource) (environment document package : Json) (target : String)
    (conclusion : VE.Formula) : Option VE.Tableau.Certificate := Id.run do
  let some baseEnv := (basePrimeJsonR src.D environment).toOption | none
  let some baseProfiles := (strings (baseEnv.getObjValD "profiles")).toOption | none
  let some canonical := (Norms.Wire.canonicalEnvironmentJson environment).toOption | none
  let some envId := (VE.Route.Wire.environmentId src.re.profiles canonical).toOption | none
  let some docHash := (rightsDocumentHash src.re.profiles environment document).toOption | none
  unless package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash &&
      package.getObjValD "target" == .str target do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  match VE.Route.Wire.bindingOk baseProfiles baseEnv ((backgroundBaseR src.D).map enc) (enc conclusion)
      c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
  | .ok () => some c
  | .error _ => none

structure RightsConflictReplay where
  src : RightsSource
  certs : List (Option VE.Tableau.Certificate)

def RightsConflictReplay.conflictFree (r : RightsConflictReplay) : Bool := rightsConflictFreeCheck r.src.D r.certs

def replayRightsConflict (j : Json) : Except String RightsConflictReplay := do
  let environment ← j.getObjVal? "environment"
  let document := j.getObjValD "document"
  let src ← decodeRightsSource environment document
  let packages := j.getObjValD "packages"
  pure ⟨src, (targets (soften (correlate src.D))).map (fun t =>
    decodeRightsPackage src environment document (packages.getObjValD t.1) t.1 (targetConclusion t))⟩

/-- A successful raw replay whose every target certificate is accepted: the input decodes to
exactly the replayed well-formed rights document, which is conflict-free over every
rights-admissible base. -/
theorem rights_wire_conflict_sound (j : Json) (res : RightsConflictReplay) (h : replayRightsConflict j = .ok res)
    (hv : res.conflictFree = true) :
    decodeRightsSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
      WellFormedRights res.src.D = true ∧ RightsConflictFree.{0} res.src.D := by
  unfold replayRightsConflict at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨src, hd, h⟩ := bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  exact ⟨by rw [he]; exact hd, src.wf, rights_conflict_free src.D src.wf _ hv⟩

def firstFailure (r : RightsConflictReplay) : Option String :=
  (((targets (soften (correlate r.src.D))).zip r.certs).find? (fun (t, c) => match c with
    | some c => !VE.Tableau.checkCertificate (envAt (soften (correlate r.src.D)) 0) (backgroundBaseR r.src.D)
        (targetConclusion t) c
    | none => true)).map (fun (t, c) => match c with
      | some _ => s!"invalid certificate for {t.1}"
      | none => s!"missing certificate for {t.1}")

/-! ## The scope audit with certificates -/

/-- The scope target name of a mechanism of a line. -/
def scopeTargetName (N : Line) (n : Narrowing) : String := s!"{N.node.name}:{mechText n}"

structure RightsScopeReplay where
  src : RightsSource
  certs : List (Option VE.Tableau.Certificate)

def RightsScopeReplay.findings (r : RightsScopeReplay) : List Finding := limitationScope r.src.D r.certs

/-- Decode the source and the `certificates` object (scope target name ↦ package); each
package binds its certificate to its own target `∀x̄. cond_n° → limpack_N`. -/
def replayRightsScope (j : Json) : Except String RightsScopeReplay := do
  let environment ← j.getObjVal? "environment"
  let document := j.getObjValD "document"
  let src ← decodeRightsSource environment document
  let packages := j.getObjValD "certificates"
  let certs := (linesOf src.D).flatMap (fun RN => (narrowings src.D RN.2).filterMap (fun n =>
    let name := scopeTargetName RN.2 n
    if (packages.getObjVal? name).toBool then
      some (decodeRightsPackage src environment document (packages.getObjValD name) name (certTarget src.D RN.2 n))
    else none))
  pure ⟨src, certs⟩

/-- A successful raw scope replay with no finding: the input decodes to that document and its
audit, with the replayed certificates, is empty, so `limitation_scope_sound` applies. -/
theorem rights_wire_scope_sound (j : Json) (res : RightsScopeReplay) (h : replayRightsScope j = .ok res)
    (hv : res.findings = []) :
    decodeRightsSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
      limitationScope res.src.D res.certs = [] := by
  unfold replayRightsScope at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨src, hd, h⟩ := bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  exact ⟨by rw [he]; exact hd, hv⟩

/-! ## Entailment certificates on the rights route -/

structure RightsEntailmentReplay where
  src : RightsSource
  premises : List VE.Formula
  conclusion : VE.Formula
  cert : VE.Tableau.Certificate

def RightsEntailmentReplay.valid (r : RightsEntailmentReplay) : Bool :=
  VE.Tableau.checkCertificate (envAt (soften (correlate r.src.D)) (size (soften (correlate r.src.D))))
    (backgroundR r.src.D ++ elaborate (soften (correlate r.src.D)).T ++ r.premises) r.conclusion r.cert

/-- Decode the source, the premises and conclusion (typed over `E″′`, so limitation,
condition, `aimed` and decision predicates may be named) and the certificate, bound to the
regenerated `E″′`, `background″ ++ layer premises` followed by the premises, and the
conclusion. -/
def replayRightsEntailment (j : Json) : Except String RightsEntailmentReplay := do
  let environment ← j.getObjVal? "environment"
  let src ← decodeRightsSource environment (j.getObjValD "document")
  let E := envAt (soften (correlate src.D)) (size (soften (correlate src.D)))
  let premisesJson ← j.getObjVal? "premises"
  let ps ← VE.Route.Wire.decodeFormulas E premisesJson
  let conclusionJson ← j.getObjVal? "conclusion"
  let c ← VE.Route.Wire.decodeClosed E conclusionJson
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  VE.Route.Wire.bindingOk src.re.profiles (← primeJsonR src.D environment)
    ((backgroundR src.D ++ elaborate (soften (correlate src.D)).T).map enc ++ (← premisesJson.getArr?).toList)
    conclusionJson cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  pure ⟨src, ps, c, cert⟩

theorem replayRightsEntailment_decodes (j : Json) (r : RightsEntailmentReplay)
    (h : replayRightsEntailment j = .ok r) :
    decodeRightsSource (j.getObjValD "environment") (j.getObjValD "document") = .ok r.src := by
  unfold replayRightsEntailment at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨src, hd, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  rw [he]; exact hd

/-- The certificate half of the wire (norms.md 11.4 shape): from a successful raw replay with an
accepted certificate, the conclusion holds under the direct soft semantics of `T″` with the
soft and limitation premises, and, given conflict-freedom and base formulas, over every
rights-admissible base. -/
theorem rights_wire_acceptance (j : Json) (r : RightsEntailmentReplay) (h : replayRightsEntailment j = .ok r)
    (hv : r.valid = true) :
    decodeRightsSource (j.getObjValD "environment") (j.getObjValD "document") = .ok r.src ∧
    (∀ S : VE.Structure.{0}, S.Admissible (VE.Norms.envAt (soften (correlate r.src.D)) (size (soften (correlate r.src.D)))) →
       VE.SoftNorms.holdsSoft (correlate r.src.D) S → VE.Norms.definitionsHold (soften (correlate r.src.D)) S →
       VE.Norms.profileHold (soften (correlate r.src.D)) S → Sat S (VE.Norms.backgroundBase (soften (correlate r.src.D))) →
       Sat S (VE.SoftNorms.softPremises (correlate r.src.D)) → Sat S (limPremises r.src.D) → Sat S r.premises →
       r.conclusion.denote S []) ∧
    (RightsConflictFree.{0} r.src.D →
       (∀ a ∈ r.premises, a.WellFormed (VE.Norms.envAt (soften (correlate r.src.D)) 0) []) →
       r.conclusion.WellFormed (VE.Norms.envAt (soften (correlate r.src.D)) 0) [] →
       ∀ B : VE.Structure.{0}, BaseAdmissibleR r.src.D B → Sat B r.premises → r.conclusion.denote B []) := by
  refine ⟨replayRightsEntailment_decodes j r h, fun S hS hs hd hp hb hsp hl hΓ => ?_, fun hc hΓ hφ => ?_⟩
  · exact rights_route_intended r.src.D r.src.wf r.premises r.conclusion r.cert hv S hS hs hd hp hb hsp hl hΓ
  · exact (rights_route_acceptance r.src.D r.src.wf hc r.premises r.conclusion r.cert hv).2 hΓ hφ

/-! ## Witnesses (CONFLICT) over `E″′_base` -/

/-- The base model vocabulary over `E″′_base`: the rights-generated predicates, the decision
predicates, then the source predicates without layer symbols. -/
def primeModelVocabularyR (re : RightsEnvironment) (D : RightsDoc) : VE.Bridge.Vocabulary :=
  { re.se.ne.rv.modelVocabulary with
    predicates := genDecls D ++ decisions (correlate D) ++
      re.se.ne.rv.vocabulary.predicates.filter (fun p => !(layerNames (soften (correlate D)).T).contains p.1) }

/-- No rights-generated name is a layer symbol of `T″′` (checked when a witness is decoded). -/
def genFresh (D : RightsDoc) : Bool := (genDecls D).all (fun d => !(layerNames (soften (correlate D)).T).contains d.1)

theorem primeModelR_valid (src : RightsSource) (M : VE.FiniteModel VE.Bridge.Entity)
    (hg : genFresh src.D = true)
    (h : M.Valid (primeModelVocabularyR src.re src.D).environment) :
    M.Valid (envAt (soften (correlate src.D)) 0) := by
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ (correlate_wellFormed src.D src.wf)
  simp only [genFresh, List.all_eq_true, Bool.not_eq_true', List.contains_eq_any_beq, List.any_eq_false,
    beq_iff_eq] at hg
  refine ⟨fun c s hc => h.1 c s (by
    change src.D.soft.E.constants c = some s at hc; rw [src.env] at hc; exact hc), fun p vs hp => ?_⟩
  obtain ⟨ss, hss, ht⟩ := h.2 p vs hp
  refine ⟨ss, ?_, ht⟩
  change VE.Bridge.lookup (genDecls src.D ++ decisions (correlate src.D) ++
    src.re.se.ne.rv.vocabulary.predicates.filter _) p = some ss at hss
  rw [VE.SoftNorms.Wire.lookup_append, VE.SoftNorms.Wire.lookup_append, Norms.Replay.lookup_filter_not] at hss
  rw [VE.SoftNorms.Wire.envAt_soften_zero]
  -- a decision name is not a generated name (decisions are fresh in `E″`)
  have hdecgen : ∀ d ∈ decisions (correlate src.D), (genDecls src.D).find? (·.1 == d.1) = none := by
    intro d hd
    have hfresh := hsv.decFresh d.1 (List.mem_map.mpr ⟨d, hd, rfl⟩)
    change (envR src.D).predicates d.1 = none at hfresh
    cases hf : (genDecls src.D).find? (·.1 == d.1) with
    | none => rfl
    | some g => simp only [envR, hf] at hfresh; cases hfresh
  by_cases hl : p ∈ layerNames (soften (correlate src.D)).T
  · exfalso
    have hgen : (genDecls src.D).find? (·.1 == p) = none := by
      apply List.find?_eq_none.mpr
      intro x hx he
      simp only [beq_iff_eq] at he
      exact hg x hx p hl (he ▸ rfl)
    have hdec : (decisions (correlate src.D)).find? (·.1 == p) = none := by
      apply List.find?_eq_none.mpr
      intro x hx he
      simp only [beq_iff_eq] at he
      obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp hl
      obtain ⟨q, hq, rfl⟩ : ∃ q, (syms (soften (correlate src.D)).T)[i]? = some q ∧ q.name = p := by
        simp only [layerNames, List.getElem?_map, Option.map_eq_some_iff] at hi
        exact hi
      have hqm := List.mem_of_getElem? hq
      cases q with
      | reg r =>
        have hr := mem_syms_reg hqm
        have := hsv.decFresh _ (List.mem_map.mpr ⟨x, hx, he⟩)
        have hd := hsv.regDecl r hr
        simp only [Sym.name] at this
        rw [this] at hd
        cases hd
      | defn d =>
        have := mem_syms_defn hqm
        rw [show (soften (correlate src.D)).T.definitions = [] from src.defs] at this
        cases this
    simp only [VE.Bridge.lookup, hgen, hdec, Option.map_none, Option.none_or, hl, if_true] at hss
    cases hss
  · simp only [hl, if_false]
    cases hd : (decisions (correlate src.D)).find? (·.1 == p) with
    | some d =>
      have hdm := List.mem_of_find?_eq_some hd
      have hdp : d.1 = p := by simpa using List.find?_some hd
      have hgen := hdecgen d hdm
      rw [hdp] at hgen
      simp only [VE.Bridge.lookup, hgen, hd, Option.map_none, Option.map_some, Option.none_or,
        Option.some_or] at hss
      simp only [hss]
    | none =>
      show (envR src.D).predicates p = some ss
      cases hgp : (genDecls src.D).find? (·.1 == p) with
      | some g =>
        simp only [VE.Bridge.lookup, hgp, Option.map_some, Option.some_or] at hss
        simp only [envR, hgp, hss]
      | none =>
        simp only [VE.Bridge.lookup, hgp, hd, Option.map_none, Option.none_or, hl, if_false] at hss
        simp only [envR, hgp, src.env]
        exact hss

/-- A decoded witness over a decoded rights source: a base model over `E″′_base` (limitation,
condition, `aimed` and decision tables included) passing `Background_base″`, a target and a
typed entity tuple. -/
structure RightsWitnessData (src : RightsSource) where
  M : VE.FiniteModel VE.Bridge.Entity
  valid : M.Valid (envAt (soften (correlate src.D)) 0)
  background : backgroundValidR src.D M = true
  target : String × List String × VE.Formula
  mem : target ∈ targets (soften (correlate src.D))
  tuple : List VE.Bridge.Entity
  typed : VE.TupleTyped M.asStructure target.2.1 tuple

def RightsWitnessData.conflict {src : RightsSource} (w : RightsWitnessData src) : Bool :=
  w.target.2.2.eval w.M (tupleVal w.tuple)

def decodeModelR (src : RightsSource) (w : Json) :
    Except String { M : VE.FiniteModel VE.Bridge.Entity // M.Valid (envAt (soften (correlate src.D)) 0) } := do
  let v := primeModelVocabularyR src.re src.D
  let data ← VE.Bridge.decodeModelData v (← w.getObjVal? "model")
  if hg : genFresh src.D = true then
    if hv : data.valid v = true then
      pure ⟨data.toModel, primeModelR_valid src _ hg (VE.Bridge.modelData_valid data v hv)⟩
    else throw "model is not semantically admissible"
  else throw "InvalidInput: a generated predicate names a layer symbol"

def rightsWitnessFrom (src : RightsSource) (w : Json) : Except String (RightsWitnessData src) := do
  let ⟨M, valid⟩ ← decodeModelR src w
  let name ← stringField w "target"
  let ids ← strings (← w.getObjVal? "tuple")
  if hb : backgroundValidR src.D M = true then
    match hf : (targets (soften (correlate src.D))).find? (·.1 == name) with
    | none => throw s!"InvalidInput: unknown conflict target {name}"
    | some t =>
      let tuple := t.2.1.zip ids
      if ht : ids.length == t.2.1.length && VE.Bridge.tupleCheck M t.2.1 tuple then
        pure ⟨M, valid, hb, t, List.mem_of_find?_eq_some hf, tuple,
          (VE.Bridge.tupleCheck_iff M _ _).mp (by simp only [Bool.and_eq_true] at ht; exact ht.2)⟩
      else throw "InvalidInput: witness tuple has the wrong length or sort"
  else throw (VE.Route.Wire.invalidModel "rights background")

def replayRightsWitness (j : Json) : Except String ((src : RightsSource) × RightsWitnessData src) := do
  let environment ← j.getObjVal? "environment"
  let src ← decodeRightsSource environment (j.getObjValD "document")
  let wd ← rightsWitnessFrom src (← j.getObjVal? "witness")
  pure ⟨src, wd⟩

/-- A successful raw witness replay whose regenerated target formula is true at the typed tuple:
the input decodes to that document, and the model refutes conflict-freedom and the conditional
claim; the witness is a strict collision or a pair conflict with a strict rule or a completion. -/
theorem rights_wire_conflict_witness_sound (j : Json) (src : RightsSource) (w : RightsWitnessData src)
    (h : replayRightsWitness j = .ok ⟨src, w⟩) (hw : w.conflict = true) :
    decodeRightsSource (j.getObjValD "environment") (j.getObjValD "document") = .ok src ∧
    ¬ VE.Norms.ConflictFree (soften (correlate src.D)) w.M.asStructure ∧ ¬ RightsConflictFree.{0} src.D ∧
    (¬ VE.SoftNorms.NoStrictCollision (correlate src.D) w.M.asStructure ∨
      ¬ VE.SoftNorms.NoHardPairConflict (correlate src.D) w.M.asStructure) := by
  unfold replayRightsWitness at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨src', hd, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨wd, _, h⟩ := bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  obtain ⟨hn, hs, hcl⟩ := rights_conflict_witness_sound src.D src.wf w.target w.mem w.M w.valid w.background
    w.tuple w.typed hw
  exact ⟨by rw [he]; exact hd, hn, hs, hcl⟩

end VE.Rights.Wire
