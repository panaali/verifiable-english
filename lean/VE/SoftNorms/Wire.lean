import VE.SoftNorms.Phases

/-! The soft-norms decoder and replays (docs/spec/soft-norms.md 3, 9.3 and 9.4).

The frozen P0 envelope gate does not know `soft-norms@0`, and the W1 norms
decoder rejects the vocabulary's `soft` block and a predicate's `instruction_of`.
`Phases.checkSource` therefore runs the validation table of 8: it strips exactly
those three soft constructs, decodes the rest with W1's unchanged
`decodeNormsEnvironment`, decodes the soft block strictly (unknown fields
rejected) and checks the profiles, rules and references in table order;
`decodeSoftSource` keeps the original complete environment for identity.

Nothing on the wire supplies an elaboration: `E′`, `T′`, `Exc_T`, `Coh_T`,
`Background_base′`, `background′`, layer premises and targets are regenerated from
the decoded `SoftDoc`, and certificates are replayed by the unchanged tableau
checker. Bindings (all recomputed here):

* identity: `environment_id` over the original canonical environment with its
  profiles; the soft document hash (`ve-soft-norms-<identity version>`) over the
  canonical norm objects, soft fields at their default values omitted (3.4);
* conflict packages: outer `(environment_id, document_hash, target)`, inner
  certificate bound to the regenerated `E′_base` JSON (`basePrimeJson`),
  `Background_base′` and `∀x̄. ¬conflict`;
* entailment certificates: the regenerated full `E′` JSON (`primeJson`),
  `background′ ++ layer premises ++ Γ` and the conclusion. -/
namespace VE.SoftNorms.Wire
open Lean
open VE.Norms
open VE.Bridge (exactFields fields stringField strings)

def softProfile : String := Phases.softProfile

/-! ## The environment -/

/-- The environment without its soft constructs. -/
def stripSoft (environment : Json) : Except String Json := do
  let profiles ← strings (← environment.getObjVal? "profiles")
  let vocab ← environment.getObjVal? "vocabulary"
  let preds ← fields (← vocab.getObjVal? "predicates")
  let preds' ← preds.mapM fun (p, e) => do
    pure (p, Json.mkObj ((← fields e).filter (·.1 != "instruction_of")))
  let vocab' := (Json.mkObj ((← fields vocab).filter (·.1 != "soft"))).setObjVal! "predicates" (Json.mkObj preds')
  pure ((environment.setObjVal! "profiles" (toJson (profiles.filter (· != softProfile)))).setObjVal!
    "vocabulary" vocab')

/-- A decoded soft environment: W1's decoding of the stripped environment, the soft block and
the original JSON with its original profiles. -/
structure SoftEnvironment where
  ne : Norms.Wire.NormsEnvironment
  soft : SoftEnv
  profiles : List String
  json : Json

/-! ## Norm objects (3.2) -/

def w1Keys : List String := Phases.w1Keys
def softKeys : List String := Phases.softKeys

/-- One norm object on its own (a quoted norm): the rule-field checks and the rule's own
cross references of the validation table (8), 4.1 to 4.14 then 5.4 to 5.8. -/
def decodeSoftNorm (se : SoftEnvironment) (j : Json) : Except String SoftNode :=
  match Phases.ruleFields se.soft.exceptionDecider j >>= fun N =>
      (Phases.ruleReferences se.ne se.soft N).map (fun _ => N) with
  | .ok N => .ok N
  | .error f => .error f.message

/-- The canonical object of 3.4: soft fields at their default value omitted. -/
def canonicalNorm (j : Json) : Json :=
  let raw := j.getObjValD "norm"
  let keep := fun (kv : String × Json) => match kv with
    | ("mode", .str "strict") | ("rank", .null) | ("alterable", .arr #[]) | ("exception", .null)
    | ("hard", .bool false) => false
    | _ => true
  match raw with
  | .obj kvs => Json.mkObj [("norm", Json.mkObj (kvs.toList.filter keep))]
  | _ => j

/-! ## The decoded source -/

structure SoftSource where
  se : SoftEnvironment
  D : SoftDoc
  wf : WellFormedSoft D = true
  env : D.E = se.ne.rv.environment
  lits : D.lits = se.ne.rv.literals
  defs : D.T.definitions = []

/-- Decode the environment and the soft norm objects: the validation table of 8 over the whole
source (`Phases.checkSource`), then `WellFormedSoft`, whose remaining diagnostics are the
semantic checks 6.4 to 6.9. -/
def decodeSoftSource (environment norms : Json) : Except String SoftSource := do
  let c ← match Phases.checkSource environment norms with
    | .ok c => pure c
    | .error f => throw f.message
  let se : SoftEnvironment := ⟨c.ne, c.soft, c.profiles, environment⟩
  let D : SoftDoc := ⟨se.ne.rv.environment, se.ne.rv.literals, se.soft, ⟨se.ne.regulated, [], c.nodes⟩⟩
  match hv : validateSoft D with
  | .error e => throw e
  | .ok () => pure ⟨se, D, by unfold WellFormedSoft; rw [hv], rfl, rfl, rfl⟩

/-! ## Identity (3.4) -/

def softDocumentHash (profiles : List String) (environment norms : Json) : Except String String := do
  let envId ← VE.Route.Wire.environmentId profiles (← Norms.Wire.canonicalEnvironmentJson environment)
  let canon := match norms with
    | .arr xs => Json.arr (xs.map canonicalNorm)
    | j => j
  VE.CertificateWire.digest s!"ve-soft-norms-{VE.Route.Wire.identityVersion profiles}\n"
    (Json.mkObj [("environment_id", .str envId), ("document", canon)])

def decisionEntry (sorts : List String) : Json :=
  Json.mkObj [("arguments", toJson sorts), ("description", .str "soft-norms decision")]

def withDecisions (D : SoftDoc) (environment : Json) : Except String Json := do
  let vocab ← environment.getObjVal? "vocabulary"
  let preds ← fields (← vocab.getObjVal? "predicates")
  pure (environment.setObjVal! "vocabulary" (vocab.setObjVal! "predicates"
    (Json.mkObj (preds ++ (decisions D).map (fun (n, ss) => (n, decisionEntry ss))))))

/-- The regenerated `E′_base`: no regulated predicate, no soft construct, the decision
predicates as base predicates; profiles without `norms@0` and `soft-norms@0`. -/
def basePrimeJson (D : SoftDoc) (environment : Json) : Except String Json := do
  withDecisions D (← Norms.Replay.baseEnvironmentJson (← stripSoft environment))

/-- The regenerated full `E′`: the canonical source environment plus the decision predicates. -/
def primeJson (D : SoftDoc) (environment : Json) : Except String Json := do
  withDecisions D (← Norms.Wire.canonicalEnvironmentJson environment)

/-! ## Regenerated outputs -/

def enc (a : VE.Formula) : Json := VE.Route.Wire.encodeFormula a

def excLabels (D : SoftDoc) : List String :=
  D.T.nodes.flatMap (fun N => match N.mode, N.exception with
    | .default, some e =>
      (List.range e.sufficient.length).map (fun i => s!"soft:exception:{N.name}:sufficient:{i}") ++
      (List.range e.necessary.length).map (fun i => s!"soft:exception:{N.name}:necessary:{i}")
    | _, _ => [])

def cohLabel (M N : SoftNode) : String := s!"soft:coherence:{M.name},{N.name}"

def softLabelled (D : SoftDoc) : List (String × VE.Formula) :=
  (excLabels D).zip (excPremises D) ++ (collidingPairs D).map (fun (M, N) => (cohLabel M N, cohPremise D M N))

/-- The coherence conjuncts not discharged by `rank_resolves`. Elaboration reports
all of them; certified results further filter by the accepted proof's use. -/
def openCoherence (D : SoftDoc) : List String :=
  (collidingPairs D).filterMap (fun (M, N) => if Comparable D M N then none else some (cohLabel M N))

def undeclaredTies (D : SoftDoc) : List (String × String) :=
  let rs := D.soft.ranks
  rs.flatMap (fun a => (rs.filter (fun b => decide (a < b))).filterMap (fun b =>
    if outranksPlus D.soft a b || outranksPlus D.soft b a || D.soft.ties.contains (a, b) ||
      D.soft.ties.contains (b, a) then none else some (a, b)))

def warnings (D : SoftDoc) : List String :=
  D.T.nodes.flatMap (fun N => N.over.filterMap (fun m => match D.T.nodes.find? (·.name == m) with
    | some M => if Incompatible D M N && N.mode == .default && M.mode == .default && higher D M N
        then some s!"RankAgainstPrecedence: rule {N.name} over {M.name}" else none
    | none => none)) ++
  (undeclaredTies D).map (fun (a, b) => s!"undeclared tie: {a}, {b}")

def bgEntry (g l : String) (a : VE.Formula) : Json :=
  Json.mkObj ([("generator", .str g), ("ast", enc a)] ++ (if l.isEmpty then [] else [("label", .str l)]))

def regenerated (D : SoftDoc) (environment : Json) : List (String × Json) :=
  let T' := (soften D).T
  [("environment_prime", (primeJson D environment).toOption.getD .null),
   ("decisions", Json.arr ((decisions D).map (fun (n, ss) =>
      Json.mkObj [("name", .str n), ("arguments", toJson ss)])).toArray),
   ("derived", Json.arr (D.T.nodes.map (fun N => Json.mkObj [("rule", .str N.name),
      ("ast", match derivedList D N with
        | [φ] => enc φ
        | _ => .null)])).toArray),
   ("order", toJson (layerNames T')),
   ("background", Json.arr (((definitionPremises T').map (bgEntry "definitions" "") ++
       (backgroundBase (soften D)).map (bgEntry "literals" "") ++
       (pairPremises T').map (bgEntry "profile" "") ++
       (softLabelled D).map (fun x => bgEntry "soft" x.1 x.2))).toArray),
   ("premises", Json.arr ((syms T').filterMap (fun
       | .reg r => some (Json.mkObj [("label", .str ("layer:norms:" ++ r.name)),
           ("ast", enc (elabPremise T' r))])
       | .defn _ => none)).toArray),
   ("colliding_pairs", Json.arr ((collidingPairs D).map (fun (M, N) => Json.mkObj
     [("pair", toJson [M.name, N.name]), ("act", .str (act D M)), ("comparable", .bool (Comparable D M N)),
      ("label", .str (cohLabel M N)), ("ast", enc (cohPremise D M N))])).toArray),
   ("conflict_targets", Json.arr ((targets (soften D)).map (fun t => Json.mkObj
     [("target", .str t.1), ("sorts", toJson t.2.1), ("ast", enc t.2.2)])).toArray),
   ("conditional_on", toJson (openCoherence D)),
   ("fragment", .bool (InFragment D)),
   ("warnings", toJson (warnings D))]

/-! ## Conflict packages (CONFLICT-FREE) -/

def decodeSoftPackage (src : SoftSource) (environment norms packages : Json)
    (t : String × List String × VE.Formula) : Option VE.Tableau.Certificate := Id.run do
  let some baseEnv := (basePrimeJson src.D environment).toOption | none
  let some baseProfiles := (strings (baseEnv.getObjValD "profiles")).toOption | none
  let some canonical := (Norms.Wire.canonicalEnvironmentJson environment).toOption | none
  let some envId := (VE.Route.Wire.environmentId src.se.profiles canonical).toOption | none
  let some docHash := (softDocumentHash src.se.profiles environment norms).toOption | none
  let package := packages.getObjValD t.1
  unless package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash &&
      package.getObjValD "target" == .str t.1 do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  match VE.Route.Wire.bindingOk baseProfiles baseEnv ((backgroundBase' src.D).map enc) (enc (targetConclusion t))
      c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
  | .ok () => some c
  | .error _ => none

structure SoftConflictReplay where
  src : SoftSource
  certs : List (Option VE.Tableau.Certificate)

def SoftConflictReplay.conflictFree (r : SoftConflictReplay) : Bool := softConflictFreeCheck r.src.D r.certs

def replaySoftConflict (j : Json) : Except String SoftConflictReplay := do
  let environment ← j.getObjVal? "environment"
  let norms := j.getObjValD "norms"
  let src ← decodeSoftSource environment norms
  let packages := j.getObjValD "packages"
  pure ⟨src, (targets (soften src.D)).map (decodeSoftPackage src environment norms packages)⟩

open VE.Order.ProfileGate (bind_ok)

/-- A successful raw replay whose every target certificate is accepted: the input decodes to
exactly the replayed well-formed soft document, and it is conflict-free over every coherent
base. -/
theorem soft_wire_conflict_sound (j : Json) (res : SoftConflictReplay) (h : replaySoftConflict j = .ok res)
    (hv : res.conflictFree = true) :
    decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok res.src ∧
      WellFormedSoft res.src.D = true ∧ SoftConflictFree.{0} res.src.D := by
  unfold replaySoftConflict at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨src, hd, h⟩ := bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  exact ⟨by rw [he]; exact hd, src.wf, soft_conflict_free src.D src.wf _ hv⟩

def firstFailure (r : SoftConflictReplay) : Option String :=
  (((targets (soften r.src.D)).zip r.certs).find? (fun (t, c) => match c with
    | some c => !VE.Tableau.checkCertificate (envAt (soften r.src.D) 0) (backgroundBase' r.src.D)
        (targetConclusion t) c
    | none => true)).map (fun (t, c) => match c with
      | some _ => s!"invalid certificate for {t.1}"
      | none => s!"missing certificate for {t.1}")

/-! ## Witnesses (CONFLICT and WEIGHING POINT) over `E′_base` -/

/-- The base model vocabulary over `E′_base`: the decision predicates, then the source
predicates without layer symbols. -/
def primeModelVocabulary (se : SoftEnvironment) (D : SoftDoc) : VE.Bridge.Vocabulary :=
  { se.ne.rv.modelVocabulary with
    predicates := decisions D ++
      se.ne.rv.vocabulary.predicates.filter (fun p => !(layerNames (soften D).T).contains p.1) }

theorem lookup_append {α : Type} (a b : List (String × α)) (k : String) :
    VE.Bridge.lookup (a ++ b) k = (VE.Bridge.lookup a k).or (VE.Bridge.lookup b k) := by
  simp only [VE.Bridge.lookup, List.find?_append]
  cases a.find? (fun x => x.1 == k) <;> rfl

theorem envAt_soften_zero (D : SoftDoc) (p : String) :
    (envAt (soften D) 0).predicates p =
      if p ∈ layerNames (soften D).T then none else
        match (decisions D).find? (·.1 == p) with
        | some d => some d.2
        | none => D.E.predicates p := by
  simp only [envAt, hide, List.drop_zero]
  rfl

theorem primeModel_valid (src : SoftSource) (M : VE.FiniteModel VE.Bridge.Entity)
    (h : M.Valid (primeModelVocabulary src.se src.D).environment) : M.Valid (envAt (soften src.D) 0) := by
  have hsv := softValid_of_wellFormed src.D src.wf
  have hv' := valid_of_wellFormed _ hsv.wf
  refine ⟨fun c s hc => h.1 c s (by
    change src.D.E.constants c = some s at hc; rw [src.env] at hc; exact hc), fun p vs hp => ?_⟩
  obtain ⟨ss, hss, ht⟩ := h.2 p vs hp
  refine ⟨ss, ?_, ht⟩
  change VE.Bridge.lookup (decisions src.D ++ src.se.ne.rv.vocabulary.predicates.filter _) p = some ss at hss
  rw [lookup_append, Norms.Replay.lookup_filter_not] at hss
  rw [envAt_soften_zero]
  by_cases hl : p ∈ layerNames (soften src.D).T
  · -- a layer symbol is regulated, declared in `E`, hence not a decision predicate
    exfalso
    have hdec : (decisions src.D).find? (·.1 == p) = none := by
      apply List.find?_eq_none.mpr
      intro x hx he
      simp only [beq_iff_eq] at he
      obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp hl
      obtain ⟨q, hq, rfl⟩ : ∃ q, (syms (soften src.D).T)[i]? = some q ∧ q.name = p := by
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
        rw [show (soften src.D).T.definitions = [] from src.defs] at this
        cases this
    simp only [VE.Bridge.lookup, hdec, Option.map_none, Option.none_or, hl, if_true] at hss
    cases hss
  · simp only [hl, if_false]
    cases hd : (decisions src.D).find? (·.1 == p) with
    | some d =>
      simp only [VE.Bridge.lookup, hd, Option.map_some, Option.some_or] at hss
      simp only [hss]
    | none =>
      simp only [VE.Bridge.lookup, hd, Option.map_none, Option.none_or, hl, if_false] at hss
      simp only [src.env]
      exact hss

/-- A decoded witness over a decoded soft source: a base model over `E′_base` (decision
tables included) passing `Background_base′`, a target and a typed entity tuple. -/
structure SoftWitnessData (src : SoftSource) where
  M : VE.FiniteModel VE.Bridge.Entity
  valid : M.Valid (envAt (soften src.D) 0)
  background : backgroundValid' src.D M = true
  target : String × List String × VE.Formula
  mem : target ∈ targets (soften src.D)
  tuple : List VE.Bridge.Entity
  typed : VE.TupleTyped M.asStructure target.2.1 tuple

def SoftWitnessData.conflict {src : SoftSource} (w : SoftWitnessData src) : Bool :=
  w.target.2.2.eval w.M (tupleVal w.tuple)

def decodeModel (src : SoftSource) (w : Json) :
    Except String { M : VE.FiniteModel VE.Bridge.Entity // M.Valid (envAt (soften src.D) 0) } := do
  let v := primeModelVocabulary src.se src.D
  let data ← VE.Bridge.decodeModelData v (← w.getObjVal? "model")
  if hv : data.valid v = true then
    pure ⟨data.toModel, primeModel_valid src _ (VE.Bridge.modelData_valid data v hv)⟩
  else throw "model is not semantically admissible"

def softWitnessFrom (src : SoftSource) (w : Json) : Except String (SoftWitnessData src) := do
  let ⟨M, valid⟩ ← decodeModel src w
  let name ← stringField w "target"
  let ids ← strings (← w.getObjVal? "tuple")
  if hb : backgroundValid' src.D M = true then
    match hf : (targets (soften src.D)).find? (·.1 == name) with
    | none => throw s!"InvalidInput: unknown conflict target {name}"
    | some t =>
      let tuple := t.2.1.zip ids
      if ht : ids.length == t.2.1.length && VE.Bridge.tupleCheck M t.2.1 tuple then
        pure ⟨M, valid, hb, t, List.mem_of_find?_eq_some hf, tuple,
          (VE.Bridge.tupleCheck_iff M _ _).mp (by simp only [Bool.and_eq_true] at ht; exact ht.2)⟩
      else throw "InvalidInput: witness tuple has the wrong length or sort"
  else throw (VE.Route.Wire.invalidModel "soft background")

def replaySoftWitness (j : Json) : Except String ((src : SoftSource) × SoftWitnessData src) := do
  let environment ← j.getObjVal? "environment"
  let src ← decodeSoftSource environment (j.getObjValD "norms")
  let wd ← softWitnessFrom src (← j.getObjVal? "witness")
  pure ⟨src, wd⟩

/-- A successful raw witness replay whose regenerated target formula is true at the typed
tuple: the input decodes to that document, and the coherent model refutes conflict-freedom,
unique expansion and the conditional claim; the witness is a strict collision or a pair
conflict with a strict rule or a completion. -/
theorem soft_wire_conflict_witness_sound (j : Json) (src : SoftSource) (w : SoftWitnessData src)
    (h : replaySoftWitness j = .ok ⟨src, w⟩) (hw : w.conflict = true) :
    decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok src ∧
    ¬ VE.Norms.ConflictFree (soften src.D) w.M.asStructure ∧ ¬ SoftConflictFree.{0} src.D ∧
    (¬ NoStrictCollision src.D w.M.asStructure ∨ ¬ NoHardPairConflict src.D w.M.asStructure) := by
  unfold replaySoftWitness at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨src', hd, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨wd, _, h⟩ := bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  obtain ⟨hn, _, hs, hcl⟩ := soft_conflict_witness_sound src.D src.wf w.target w.mem w.M w.valid w.background
    w.tuple w.typed hw
  exact ⟨by rw [he]; exact hd, hn, hs, hcl⟩

/-! ## Entailment certificates on the soft route -/

structure SoftEntailmentReplay where
  src : SoftSource
  premises : List VE.Formula
  conclusion : VE.Formula
  cert : VE.Tableau.Certificate

def SoftEntailmentReplay.valid (r : SoftEntailmentReplay) : Bool :=
  VE.Tableau.checkCertificate (envAt (soften r.src.D) (size (soften r.src.D)))
    (background' r.src.D ++ elaborate (soften r.src.D).T ++ r.premises) r.conclusion r.cert

/-- Decode the source, the premises and conclusion (typed over `E′`, so decision findings may
be named) and the certificate, bound to the regenerated `E′`, `background′ ++ layer premises`
followed by the premises, and the conclusion. -/
def replaySoftEntailment (j : Json) : Except String SoftEntailmentReplay := do
  let environment ← j.getObjVal? "environment"
  let src ← decodeSoftSource environment (j.getObjValD "norms")
  let E := envAt (soften src.D) (size (soften src.D))
  let premisesJson ← j.getObjVal? "premises"
  let ps ← VE.Route.Wire.decodeFormulas E premisesJson
  let conclusionJson ← j.getObjVal? "conclusion"
  let c ← VE.Route.Wire.decodeClosed E conclusionJson
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  VE.Route.Wire.bindingOk src.se.profiles (← primeJson src.D environment)
    ((background' src.D ++ elaborate (soften src.D).T).map enc ++ (← premisesJson.getArr?).toList)
    conclusionJson cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  pure ⟨src, ps, c, cert⟩

theorem replaySoftEntailment_decodes (j : Json) (r : SoftEntailmentReplay) (h : replaySoftEntailment j = .ok r) :
    decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.src := by
  unfold replaySoftEntailment at h
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

/-- The certificate half of the wire (norms.md 11.4 shape): from a successful raw replay with
an accepted certificate, the conclusion holds under the direct soft semantics with the soft
premises, and, given coherent conflict-freedom and base formulas, over every coherent base. -/
theorem soft_wire_acceptance (j : Json) (r : SoftEntailmentReplay) (h : replaySoftEntailment j = .ok r)
    (hv : r.valid = true) :
    decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.src ∧
    (∀ S : VE.Structure.{0}, S.Admissible (envAt (soften r.src.D) (size (soften r.src.D))) → holdsSoft r.src.D S →
      VE.Norms.definitionsHold (soften r.src.D) S → VE.Norms.profileHold (soften r.src.D) S →
      Sat S (VE.Norms.backgroundBase (soften r.src.D)) → Sat S (softPremises r.src.D) →
      Sat S r.premises → r.conclusion.denote S []) ∧
    (SoftConflictFree.{0} r.src.D →
      (∀ a ∈ r.premises, a.WellFormed (envAt (soften r.src.D) 0) []) →
        r.conclusion.WellFormed (envAt (soften r.src.D) 0) [] →
      ∀ B : VE.Structure.{0}, BaseAdmissible' r.src.D B → Sat B r.premises → r.conclusion.denote B []) := by
  refine ⟨replaySoftEntailment_decodes j r h, fun S hS hs hd hp hb hsp hΓ => ?_, fun hc hΓ hφ => ?_⟩
  · exact soft_route_intended r.src.D r.src.wf r.premises r.conclusion r.cert hv S hS hs hd hp hb hsp hΓ
  · exact (soft_route_acceptance r.src.D r.src.wf hc r.premises r.conclusion r.cert hv).2 hΓ hφ

end VE.SoftNorms.Wire
