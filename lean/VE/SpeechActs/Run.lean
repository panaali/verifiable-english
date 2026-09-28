import VE.SpeechActs.Wire
import VE.Norms.Run

/-! The `ve_speech_acts_route` executable (docs/spec/speech-acts.md 8.6), invoked
as `lean/.lake/build/bin/ve_speech_acts_route <cases.json|->`. Each case is
`{"id", "kind", "environment", "document", ...}`; `document` holds the units of
3.2 and the derived `queries` records. Every formula is regenerated from the
decoded document (`Wire.decodeDocument`); nothing on the wire supplies
`policy(D)`, `premises(D)`, `H(q)`, `F(q, a)` or `Π_q`.

* `speech-elaborate` → the scope, the legend sentences, the W1 regeneration of
  `policy(D)`, each active command's rule and paraphrase, the dormant commands,
  each question's mode, presupposition and tokens or domain, each query's
  premises and target.
* `speech-answer` with `question`, `evidence` (`{"certificate"}` with `answer`,
  `{"conditional"}` with `answer`, `{"presupposition_failed"}` or `{"model"}`)
  and optionally `premise_status` (`{"model"}` or `{"inconsistent"}`) → the
  answer line of 5.3. Certificates bind the canonical environment, the
  regenerated premise list and the exact conclusion.
* `speech-consequence` with `query` and `certificate` and/or `model` →
  `follows`, `gap` or `unresolved` (`CheckerConflict` when both succeed).
* `speech-conflict` with `witness` (W1's witness shape on the regenerated
  policy) → `CONFLICT` or `UNKNOWN`.
* Cases without a speech-act construct delegate unchanged to
  `Norms.Run.runCase`; a speech-act input never falls back after a failed
  decode. W2 `admission` of speech-act documents is not implemented yet and is
  rejected with a diagnostic.

On the model path the regulated tables are computed from the rules in layer
order (norms.md 11.3), never supplied: the model gives base tables only. -/
namespace VE.SpeechActs.Run
open Lean
open VE.Bridge (stringField strings fields)
open VE.Norms (Regulated Node Sym syms elaborate background envAt size outcome layerNames tupleVal Sat)
universe u

def enc (a : VE.Formula) : Json := VE.Route.Wire.encodeFormula a

/-! ## Regenerated output (`speech-elaborate`) -/

def encodeNode (N : Node) : Json :=
  Json.mkObj [("name", .str N.name), ("predicate", .str N.pred), ("sign", .bool N.sign),
    ("guard", enc N.guard), ("unless", Json.arr (N.carveOuts.map enc).toArray), ("over", toJson N.over)]

/-- How a constant is written in the text: its bound definite phrase, else its name. -/
def nameOf (D : SpeechDoc) (a : String) : String :=
  match D.scope.definites.find? (·.2 == a) with
  | some (p, _) => p
  | none => a

/-- The act phrase after slot 0, later slots filled (2.1). -/
def actRest (D : SpeechDoc) (c : Command) : String :=
  let act := ((regOf D c.act).bind Regulated.act).getD c.act
  let rest := if act.startsWith "{0} " then act.drop 4 else act
  (c.args.zipIdx 1).foldl (fun s (a, i) => s.replace ("{" ++ toString i ++ "}") (nameOf D a)) rest

/-- The deterministic paraphrase of a command (2.1), without logic. -/
def paraphrase (D : SpeechDoc) (c : Command) : String :=
  "In this task, you are " ++ (if c.force = .require then "required to " else "not permitted to ") ++
    actRest D c ++ (if c.guard == .top then "" else ", where the stated condition holds") ++ "."

/-- The legend sentences of the scope (2.1). -/
def legend (sc : Scope) : List String :=
  [s!"This document is task {sc.task}."] ++
    (match sc.addressee with
     | some (_, c) => [s!"In this task, you are {c}."]
     | none => []) ++
    sc.definites.map (fun (p, c) => s!"In this task, {p} is {c}.")

def questionJson (D : SpeechDoc) (q : Question) : Json :=
  Json.mkObj ([("unit", .str q.unit), ("mode", .str (Wire.modeName q.mode)),
      ("presupposition", enc (presupposition D q))] ++
    match q.mode with
    | .polar => [("tokens", toJson ["yes", "no"]), ("body", enc q.body)]
    | .whichOne => [("tokens", toJson q.domain), ("body", enc q.body)]
    | .whichAll => [("domain", toJson q.domain), ("body", enc q.body)]
    | .follows => [("query", toJson q.query)]
    | .reading => [("set", toJson (q.readingSet.map Prod.fst)), ("version", toJson (q.readingSet.map Prod.snd))])

/-! ## Meaning identities (3.5) -/

/-- The `ve-meaning` digest of an AST under the document's canonical environment id. -/
def meaningOf (dec : Wire.Decoded) (ast : Json) : String :=
  match VE.Route.Wire.environmentId dec.se.profiles dec.se.canonical with
  | .ok envId => (VE.Route.Wire.meaningId dec.se.profiles envId ast).toOption.getD ""
  | .error _ => ""

/-- A query as bound into a meaning: its id, its regenerated premise meaning ids and its target meaning id. -/
def queryIdentity (dec : Wire.Decoded) (i : String) : Json :=
  match dec.D.queries.find? (·.id == i) with
  | some qr => Json.mkObj [("id", .str i), ("premises", toJson (qr.premises.map (fun a => meaningOf dec (enc a)))),
      ("target", .str (meaningOf dec (enc qr.target)))]
  | none => Json.mkObj [("id", .str i)]

/-- The command object of 3.5; a proof task (a slot of sort `query`) carries its query's identity. -/
def commandAst (dec : Wire.Decoded) (c : Command) : Json :=
  let query := match dec.D.E.predicates c.act with
    | some (_ :: ss) => ((ss.zip c.args).find? (·.1 == "query")).map Prod.snd
    | _ => none
  Json.mkObj [("command", Json.mkObj ([("force", Wire.encodeForce c.force), ("act", .str c.act),
    ("args", toJson c.args), ("guard", enc c.guard)] ++
    match query with
    | some i => [("query", queryIdentity dec i)]
    | none => []))]

/-- The question object of 3.5: derived mode, sort, domain, body, the query's identity, the reading set. -/
def questionAst (dec : Wire.Decoded) (q : Question) : Json :=
  Json.mkObj [("question", Json.mkObj ([("mode", .str (Wire.modeName q.mode))] ++
    (match q.mode with
     | .polar => [("body", enc q.body)]
     | .whichAll | .whichOne => [("sort", toJson q.sort), ("domain", toJson q.domain), ("body", enc q.body)]
     | .follows => [("query", queryIdentity dec (q.query.getD ""))]
     | .reading => [("set", toJson (q.readingSet.map Prod.fst)), ("version", toJson (q.readingSet.map Prod.snd))])))]

def elaborated (dec : Wire.Decoded) : List (String × Json) :=
  let D := dec.D
  [("environment_id", .str ((VE.Route.Wire.environmentId dec.se.profiles dec.se.canonical).toOption.getD "")),
   ("scope", Wire.encodeScope D.scope),
   ("legend", toJson (legend D.scope)),
   ("premises", Json.arr ((premises D).map enc).toArray),
   ("policy", Json.mkObj (VE.Norms.Wire.regenerated (policy D))),
   ("commands", Json.arr (D.commands.map (fun c => Json.mkObj [("unit", .str c.unit),
      ("force", Wire.encodeForce c.force), ("demand", encodeNode (demand D c)),
      ("paraphrase", .str (paraphrase D c)), ("meaning_id", .str (meaningOf dec (commandAst dec c)))])).toArray),
   ("dormant", toJson (dec.units.filterMap (fun u => match u.role, Wire.activeCommand u with
      | .command _, none => some u.id
      | _, _ => none))),
   ("questions", Json.arr (D.questions.map (fun q =>
      (questionJson D q).setObjVal! "meaning_id" (.str (meaningOf dec (questionAst dec q))))).toArray),
   ("queries", Json.arr (D.queries.map (fun qr => Json.mkObj ([("id", .str qr.id),
      ("premises", Json.arr (qr.premises.map enc).toArray), ("target", enc qr.target)] ++
      (if trivialQuery D qr then [("warning", .str s!"TrivialQuery: {qr.id}")] else [])))).toArray)]

/-! ## Models (model path): base tables supplied, regulated tables computed -/

/-- Compute each regulated table from its completed outcome in layer order (norms.md 11.3). -/
def computeRegulated (T : VE.Norms.Tree) (d : VE.Bridge.ModelData) : VE.Bridge.ModelData :=
  (syms T).foldl (fun d q => match q with
    | .reg r =>
      let rows := (VE.Route.Wire.tuples d.toModel r.sorts).filter
        (fun row => (outcome T r).eval d.toModel (tupleVal row))
      { d with relations := d.relations ++ [(r.name, rows)] }
    | .defn _ => d) d

/-- A validated finite model of the complete environment: its structural validity over the full vocabulary,
`Background_base` and every formula of the checked list true. -/
structure CheckedModel (D : SpeechDoc) (checked : List VE.Formula) where
  M : VE.FiniteModel VE.Bridge.Entity
  valid : M.Valid (En D)
  background : VE.Norms.backgroundValid (policy D) M = true
  sat : checked.all (fun φ => φ.eval M []) = true

theorem valid_transfer {M : VE.FiniteModel VE.Bridge.Entity} {E E' : VE.Environment}
    (hc : E'.constants = E.constants) (hp : ∀ p, E'.predicates p = E.predicates p) (h : M.Valid E) :
    M.Valid E' :=
  ⟨fun c s hcs => h.1 c s (hc ▸ hcs), fun p vs hr => by
    obtain ⟨ss, hss, ht⟩ := h.2 p vs hr
    exact ⟨ss, (hp p).trans hss, ht⟩⟩

theorem En_predicates (D : SpeechDoc) (p : String) : (En D).predicates p = D.E.predicates p :=
  VE.Norms.envAt_size_predicates (policy D) p

def decodeCheckedModel (dec : Wire.Decoded) (checked : List VE.Formula) (j : Json) :
    Except String (CheckedModel dec.D checked) := do
  let D := dec.D
  let baseV := VE.Norms.Replay.baseModelVocabulary dec.se.ne (policy D)
  let data₀ ← VE.Bridge.decodeModelData baseV j
  let data := computeRegulated (policy D).T data₀
  let fullV := dec.se.ne.rv.modelVocabulary
  if hv : data.valid fullV = true then
    have hc : (En D).constants = fullV.environment.constants := by
      show D.E.constants = _; rw [dec.env]; rfl
    have hp : ∀ p, (En D).predicates p = fullV.environment.predicates p := fun p => by
      rw [En_predicates, dec.env]; rfl
    if hb : VE.Norms.backgroundValid (policy D) data.toModel = true then
      if hs : checked.all (fun φ => φ.eval data.toModel []) = true then
        pure ⟨data.toModel, valid_transfer hc hp (VE.Bridge.modelData_valid data fullV hv), hb, hs⟩
      else throw "InvalidModel(premises): the model does not satisfy the checked premises"
    else throw (VE.Route.Wire.invalidModel "literals")
  else throw "model is not semantically admissible"

/-! ## Certificates -/

/-- Decode a certificate bound to the canonical environment, the regenerated checked list and the conclusion. -/
def boundCertificate (dec : Wire.Decoded) (checked : List VE.Formula) (conclusion : VE.Formula) (j : Json) :
    Except String VE.Tableau.Certificate := do
  let c ← VE.CertificateWire.decodeCertificate j
  VE.Route.Wire.bindingOk dec.se.profiles dec.se.canonical (checked.map enc) (enc conclusion)
    c.environment_id c.premise_meaning_ids c.conclusion_meaning_id
  pure c

/-! ## Premise status (5.3) -/

/-- P0's three-way status of a checked premise list: a validated model, an accepted inconsistency certificate,
or UNKNOWN (no evidence supplied); `vacuous` is its fixed function. -/
inductive PremiseStatus (D : SpeechDoc) (checked : List VE.Formula)
  | model (id : String) (m : CheckedModel D checked)
  | inconsistent (c : VE.Tableau.Certificate)
      (accepted : VE.Tableau.checkCertificate (En D) checked .bottom c = true)
  | unknown

def PremiseStatus.text {D : SpeechDoc} {checked : List VE.Formula} : PremiseStatus D checked → String
  | .model id _ => s!"model {id}; vacuous: no"
  | .inconsistent .. => "INCONSISTENT (certificate); vacuous: yes"
  | .unknown => "UNKNOWN (no premise-status evidence); vacuous: unknown"

def decodePremiseStatus (dec : Wire.Decoded) (checked : List VE.Formula) (modelId : String) (j : Json) :
    Except String (PremiseStatus dec.D checked) := do
  match j.getObjVal? "premise_status" with
  | .error _ => pure .unknown
  | .ok s =>
    match s.getObjVal? "model", s.getObjVal? "inconsistent" with
    | .ok m, .error _ => pure (.model modelId (← decodeCheckedModel dec checked m))
    | .error _, .ok cj =>
      let c ← boundCertificate dec checked .bottom cj
      if h : VE.Tableau.checkCertificate (En dec.D) checked .bottom c = true then pure (.inconsistent c h)
      else pure .unknown
    | _, _ => throw "InvalidInput: premise_status"

/-- A model status witnesses a satisfiable list (not vacuous); an inconsistency certificate refutes every
admissible structure satisfying it (vacuous). -/
theorem premiseStatus_sound {D : SpeechDoc} {checked : List VE.Formula} (s : PremiseStatus D checked) :
    (∀ id m, s = .model id m → m.M.asStructure.Admissible (En D) ∧ Sat m.M.asStructure checked) ∧
    (∀ c h, s = .inconsistent c h → ∀ S : VE.Structure.{u}, S.Admissible (En D) → ¬ Sat S checked) := by
  refine ⟨fun id m _ => ⟨m.valid, fun a ha => (VE.eval_iff_denote m.M [] a).mp (List.all_eq_true.mp m.sat a ha)⟩,
    fun c h _ S hS hs => ?_⟩
  exact VE.Tableau.checkCertificate_sound _ _ _ c h S hS hs

/-! ## Answers (`speech-answer`) -/

def findQuestion (D : SpeechDoc) (u : String) : Except String { q : Question // q ∈ D.questions } :=
  match h : D.questions.find? (·.unit == u) with
  | some q => .ok ⟨q, List.mem_of_find?_eq_some h⟩
  | none => .error s!"InvalidInput: unknown question {u}"

def findQuery (D : SpeechDoc) (i : String) : Except String { qr : Query // qr ∈ D.queries } :=
  match h : D.queries.find? (·.id == i) with
  | some qr => .ok ⟨qr, List.mem_of_find?_eq_some h⟩
  | none => .error s!"InvalidInput: unknown query {i}"

def tokenFormula (D : SpeechDoc) (q : Question) (a : Answer) :
    Except String { φ : VE.Formula // correct D q a = some φ } :=
  match h : correct D q a with
  | some φ => .ok ⟨φ, rfl⟩
  | none => .error s!"AnswerOutsideDomain: {q.unit}, {(Wire.encodeAnswer a).compress}"

/-- The answer a validated model gives, if any (the finite evaluator). -/
def modelAnswer (D : SpeechDoc) (q : Question) (M : VE.FiniteModel VE.Bridge.Entity) : Option Answer :=
  let P := fun a => (instAt q a).eval M []
  let cands : List Answer := match q.mode with
    | .polar => [.yes, .no]
    | .whichOne => q.domain.map .one
    | .whichAll => [.all (q.domain.filter P)]
    | _ => []
  cands.find? (answerEval D q M)

def answerText : Answer → String
  | .yes => "yes"
  | .no => "no"
  | .one a => a
  | .all [] => "none"
  | .all S => " and ".intercalate S

/-- A replayed answer case. -/
inductive AnswerReplay (D : SpeechDoc) (q : Question)
  | certificate (a : Answer) (φ : VE.Formula) (hφ : correct D q a = some φ) (c : VE.Tableau.Certificate)
      (status : PremiseStatus D (premises D))
  | conditional (a : Answer) (φ : VE.Formula) (hφ : correct D q a = some φ) (c : VE.Tableau.Certificate)
      (status : PremiseStatus D (premises D ++ [presupposition D q]))
  | presuppositionFailed (c : VE.Tableau.Certificate)
  | model (id : String) (m : CheckedModel D (premises D))

/-- Whether the unchanged tableau checker accepts the case's certificate for its exact regenerated query. -/
def AnswerReplay.accepted {D : SpeechDoc} {q : Question} : AnswerReplay D q → Bool
  | .certificate _ φ _ c _ => VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) φ) c
  | .conditional _ φ _ c _ => VE.Tableau.checkCertificate (En D) (premises D ++ [presupposition D q]) φ c
  | .presuppositionFailed c => VE.Tableau.checkCertificate (En D) (premises D) (.not (presupposition D q)) c
  | .model .. => true

def AnswerReplay.line {D : SpeechDoc} {q : Question} (r : AnswerReplay D q) : String :=
  match r, r.accepted with
  | .certificate a _ _ _ s, true => s!"supported {answerText a} (certificate; premises: {s.text})"
  | .conditional a _ _ _ s, true => s!"supported {answerText a} given the presupposition (certificate; " ++
      s!"assumption speech:presupposition:{q.unit}; premises with H: {s.text})"
  | .presuppositionFailed _, true => "PRESUPPOSITION-FAILED (certificate for ¬H)"
  | .model id m, _ =>
    if (presupposition D q).eval m.M [] then
      match modelAnswer D q m.M with
      | some a => s!"evaluated {answerText a} in model {id} (this situation only)"
      | none => "UNKNOWN (no answer in the supplied model)"
    else s!"PRESUPPOSITION-FAILED (model {id})"
  | _, _ => "UNKNOWN (certificate not accepted)"

structure AnswerCase where
  dec : Wire.Decoded
  q : Question
  mem : q ∈ dec.D.questions
  replay : AnswerReplay dec.D q

def replayAnswer (j : Json) : Except String AnswerCase := do
  let dec ← Wire.decodeDocument (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let D := dec.D
  let ⟨q, hq⟩ ← findQuestion D (← stringField j "question")
  let modelId := (stringField j "model_id").toOption.getD "m"
  let ev ← j.getObjVal? "evidence"
  let replay ← match ev.getObjVal? "certificate", ev.getObjVal? "conditional",
      ev.getObjVal? "presupposition_failed", ev.getObjVal? "model" with
    | .ok cj, .error _, .error _, .error _ => do
      let a ← Wire.decodeAnswer (← j.getObjVal? "answer")
      let ⟨φ, hφ⟩ ← tokenFormula D q a
      let concl := VE.Formula.and (presupposition D q) φ
      let c ← boundCertificate dec (premises D) concl cj
      let status ← decodePremiseStatus dec (premises D) modelId j
      pure (AnswerReplay.certificate a φ hφ c status)
    | .error _, .ok cj, .error _, .error _ => do
      let a ← Wire.decodeAnswer (← j.getObjVal? "answer")
      let ⟨φ, hφ⟩ ← tokenFormula D q a
      let checked := premises D ++ [presupposition D q]
      let c ← boundCertificate dec checked φ cj
      let status ← decodePremiseStatus dec checked modelId j
      pure (AnswerReplay.conditional a φ hφ c status)
    | .error _, .error _, .ok cj, .error _ => do
      let concl := VE.Formula.not (presupposition D q)
      let c ← boundCertificate dec (premises D) concl cj
      pure (AnswerReplay.presuppositionFailed c)
    | .error _, .error _, .error _, .ok mj => do
      pure (AnswerReplay.model modelId (← decodeCheckedModel dec (premises D) mj))
    | _, _, _, _ => throw "InvalidInput: evidence"
  pure ⟨dec, q, hq, replay⟩

/-! ## Consequence questions (`speech-consequence`) -/

structure ConsequenceCase where
  dec : Wire.Decoded
  qr : Query
  mem : qr ∈ dec.D.queries
  cert : Option VE.Tableau.Certificate
  model : Option (CheckedModel dec.D (queryPremises dec.D qr))

def ConsequenceCase.follows (r : ConsequenceCase) : Bool :=
  match r.cert with
  | some c => VE.Tableau.checkCertificate (En r.dec.D) (queryPremises r.dec.D r.qr) r.qr.target c
  | none => false

def ConsequenceCase.gap (r : ConsequenceCase) : Bool :=
  match r.model with
  | some m => !(r.qr.target.eval m.M [])
  | none => false

def replayConsequence (j : Json) : Except String ConsequenceCase := do
  let dec ← Wire.decodeDocument (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let ⟨qr, hq⟩ ← findQuery dec.D (← stringField j "query")
  let cert ← match j.getObjVal? "certificate" with
    | .ok cj => some <$> boundCertificate dec (queryPremises dec.D qr) qr.target cj
    | .error _ => pure none
  let model ← match j.getObjVal? "model" with
    | .ok mj => some <$> decodeCheckedModel dec (queryPremises dec.D qr) mj
    | .error _ => pure none
  pure ⟨dec, qr, hq, cert, model⟩

/-! ## Conflict witnesses (`speech-conflict`) -/

/-- The regenerated policy as a W1 decoded source (its well-formedness from `WellFormedSpeech`). -/
def normsSource (dec : Wire.Decoded) : VE.Norms.Wire.Source :=
  ⟨dec.se.ne, policy dec.D, (validSpeech_of_wellFormed _ dec.wf).policy, dec.env, dec.lits⟩

def replayWitness (j : Json) :
    Except String ((dec : Wire.Decoded) × VE.Norms.Replay.WitnessData (normsSource dec)) := do
  let dec ← Wire.decodeDocument (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let w ← VE.Norms.Replay.witnessFrom (normsSource dec) (← j.getObjVal? "witness")
  pure ⟨dec, w⟩

/-! ## Conflict packages (`speech-conflict`, CONFLICT-FREE) -/

/-- The regenerated base environment: the scope block and the `speech-acts@0` profile removed, then W1's base
environment (regulated predicates and `norms@0` removed). -/
def baseEnvironmentJson (environment : Json) : Except String Json := do
  VE.Norms.Replay.baseEnvironmentJson (← Wire.stripSpeech environment)

/-- The speech-act document hash: the complete source document under the canonical environment id. -/
def documentHash (dec : Wire.Decoded) (document : Json) : Except String String := do
  let envId ← VE.Route.Wire.environmentId dec.se.profiles dec.se.canonical
  VE.CertificateWire.digest s!"ve-speech-acts-{VE.Route.Wire.identityVersion dec.se.profiles}\n"
    (Json.mkObj [("environment_id", .str envId), ("document", document)])

/-- One target's package: `none` unless the outer binding (canonical environment id, document hash, target)
matches the source and the inner certificate binds the regenerated base environment, `Background_base` and
`∀x̄. ¬conflict`. -/
def decodePackage (dec : Wire.Decoded) (environment document packages : Json)
    (t : String × List String × VE.Formula) : Option VE.Tableau.Certificate := Id.run do
  let D := policy dec.D
  let some baseEnv := (baseEnvironmentJson environment).toOption | none
  let some baseProfiles := (strings (baseEnv.getObjValD "profiles")).toOption | none
  let some envId := (VE.Route.Wire.environmentId dec.se.profiles dec.se.canonical).toOption | none
  let some docHash := (documentHash dec document).toOption | none
  let package := packages.getObjValD t.1
  unless package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash &&
      package.getObjValD "target" == .str t.1 do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  match VE.Route.Wire.bindingOk baseProfiles baseEnv ((VE.Norms.backgroundBase D).map enc)
      (enc (VE.Norms.targetConclusion t)) c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
  | .ok () => some c
  | .error _ => none

structure ConflictCase where
  dec : Wire.Decoded
  certs : List (Option VE.Tableau.Certificate)

def ConflictCase.conflictFree (r : ConflictCase) : Bool := VE.Norms.conflictFreeCheck (policy r.dec.D) r.certs

def replayConflict (j : Json) : Except String ConflictCase := do
  let environment ← j.getObjVal? "environment"
  let document ← j.getObjVal? "document"
  let dec ← Wire.decodeDocument environment document
  let packages := j.getObjValD "packages"
  pure ⟨dec, (VE.Norms.targets (policy dec.D)).map (decodePackage dec environment document packages)⟩

/-- The first target without an accepted certificate. -/
def firstFailure (r : ConflictCase) : Option String :=
  let D := policy r.dec.D
  (((VE.Norms.targets D).zip r.certs).find? (fun (t, c) => match c with
    | some c => !VE.Tableau.checkCertificate (envAt D 0) (VE.Norms.backgroundBase D) (VE.Norms.targetConclusion t) c
    | none => true)).map (fun (t, _) => s!"no accepted certificate for {t.1}")

/-- A CONFLICT-FREE verdict: every base-admissible structure is conflict-free for the regenerated policy
(W1's `conflictFreeCheck_sound`), so W1's route theorems apply to it (`speech_route_acceptance`). -/
theorem speech_wire_conflict_free_sound (j : Json) (r : ConflictCase) (h : replayConflict j = .ok r)
    (hv : r.conflictFree = true) :
    WellFormedSpeech r.dec.D = true ∧
      ∀ B : VE.Structure.{u}, VE.Norms.BaseAdmissible (policy r.dec.D) B → VE.Norms.ConflictFree (policy r.dec.D) B :=
  ⟨r.dec.wf, fun B hB => VE.Norms.conflictFreeCheck_sound (policy r.dec.D) (policy_wellFormed r.dec.D r.dec.wf)
    r.certs hv B hB⟩

/-! ## The public entry point -/

/-- A speech-act construct: the `speech-acts@0` profile, the scope block, a `speech-*` kind, or a unit of kind
`binding` or with command or question content. The `norms@0` profile alone is not one. -/
def usesSpeechPath (j : Json) : Bool :=
  let env := j.getObjValD "environment"
  let profile := match env.getObjValD "profiles" with
    | .arr ps => ps.toList.contains (.str Wire.speechProfile)
    | _ => false
  let kind := match j.getObjValD "kind" with
    | .str k => k.startsWith "speech-"
    | _ => false
  let unit := match (j.getObjValD "document").getObjValD "units" with
    | .arr units => units.toList.any (fun u => u.getObjValD "kind" == .str "binding" ||
        ((u.getObjValD "content").getObjVal? "command").toBool ||
        ((u.getObjValD "content").getObjVal? "question").toBool)
    | _ => false
  profile || (env.getObjVal? "speech_acts").toBool || kind || unit

def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if kind == "speech-elaborate" then
    let dec ← Wire.decodeDocument (← j.getObjVal? "environment") (← j.getObjVal? "document")
    return VE.Route.Wire.ok id (elaborated dec)
  if kind == "speech-answer" then
    let r ← replayAnswer j
    return VE.Route.Wire.ok id [("question", .str r.q.unit), ("answer", .str r.replay.line)]
  if kind == "speech-consequence" then
    let r ← replayConsequence j
    if r.follows && r.gap then throw "CheckerConflict"
    let judgment :=
      if r.follows then "follows (certificate)"
      else if r.gap then "gap (model " ++ (stringField j "model_id").toOption.getD "m" ++ ")"
      else "unresolved (no accepted evidence)"
    return VE.Route.Wire.ok id [("query", .str r.qr.id), ("judgment", .str judgment)]
  if kind == "speech-conflict" && !(j.getObjVal? "witness").toBool then
    let r ← replayConflict j
    return VE.Route.Wire.ok id ([("verdict", .str (if r.conflictFree then "CONFLICT-FREE" else "UNKNOWN")),
      ("targets", toJson ((VE.Norms.targets (policy r.dec.D)).map (·.1)))] ++
      match firstFailure r with
      | some d => if r.conflictFree then [] else [("detail", .str d)]
      | none => [])
  if kind == "speech-conflict" then
    let ⟨dec, w⟩ ← replayWitness j
    return VE.Route.Wire.ok id [("verdict", .str (if w.conflict then "CONFLICT" else "UNKNOWN")),
      ("target", .str w.target.1),
      ("targets", toJson ((VE.Norms.targets (policy dec.D)).map (·.1)))]
  if usesSpeechPath j then
    throw s!"UnsupportedProfile: case kind {kind} is not available on the speech-acts route"
  VE.Norms.Run.runCase j

def runCaseReported (j : Json) : Json :=
  if usesSpeechPath j then
    match runCase j with
    | .ok result => result
    | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"),
        ("error", .str message)]
  else VE.Norms.Run.runCaseReported j

def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_speech_acts_route [cases.json|-]"
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

/-! ## Soundness of the replays -/

/-- A supported answer line: in every admissible structure satisfying the regenerated premises, the answer is
correct (`support_sound`); a conditional one, wherever the presupposition also holds
(`support_conditional_sound`); a presupposition-failure certificate leaves no correct token
(`answers_presupposition`); on the model path the finite evaluator's answers are exactly `AnswersAt` in that
model (`model_answers`). Every premise status is sound (`premiseStatus_sound`). -/
theorem speech_wire_answer_sound (j : Json) (r : AnswerCase) (h : replayAnswer j = .ok r) :
    WellFormedSpeech r.dec.D = true ∧ r.q ∈ r.dec.D.questions ∧
    (∀ a φ hφ c s, r.replay = .certificate a φ hφ c s → r.replay.accepted = true →
      ∀ S : VE.Structure.{u}, S.Admissible (En r.dec.D) → Sat S (premises r.dec.D) → AnswersAt r.dec.D r.q S a) ∧
    (∀ a φ hφ c s, r.replay = .conditional a φ hφ c s → r.replay.accepted = true →
      ∀ S : VE.Structure.{u}, S.Admissible (En r.dec.D) → Sat S (premises r.dec.D) →
        (presupposition r.dec.D r.q).denote S [] → AnswersAt r.dec.D r.q S a) ∧
    (∀ c, r.replay = .presuppositionFailed c → r.replay.accepted = true →
      ∀ S : VE.Structure.{u}, S.Admissible (En r.dec.D) → Sat S (premises r.dec.D) →
        ∀ a, ¬ AnswersAt r.dec.D r.q S a) ∧
    (∀ id m, r.replay = .model id m →
      ∀ a, answerEval r.dec.D r.q m.M a = true ↔ AnswersAt r.dec.D r.q m.M.asStructure a) := by
  have hwf := r.dec.wf
  have hq := r.mem
  refine ⟨hwf, hq, fun a φ hφ c s he ha => ?_, fun a φ hφ c s he ha => ?_, fun c he ha => ?_,
    fun id m _ a => model_answers r.dec.D hwf r.q hq m.M m.valid m.background m.sat a⟩
  · rw [he] at ha
    exact support_sound r.dec.D hwf r.q hq a φ hφ c ha
  · rw [he] at ha
    exact support_conditional_sound r.dec.D hwf r.q hq a φ hφ c ha
  · rw [he] at ha
    intro S hS hp a' ha'
    exact (VE.Tableau.checkCertificate_sound _ _ _ c ha S hS hp) ha'.2.1

/-- `follows` is `Entails` over the regenerated `Π_q`; `gap` is its refutation (at every universe);
the two never both hold (`CheckerConflict`). -/
theorem speech_wire_consequence_sound (j : Json) (r : ConsequenceCase) (h : replayConsequence j = .ok r) :
    WellFormedSpeech r.dec.D = true ∧ r.qr ∈ r.dec.D.queries ∧
    (r.follows = true → VE.Entails.{u} (En r.dec.D) (queryPremises r.dec.D r.qr) r.qr.target) ∧
    (r.gap = true → ¬ VE.Entails.{u} (En r.dec.D) (queryPremises r.dec.D r.qr) r.qr.target) ∧
    ¬ (r.follows = true ∧ r.gap = true) := by
  have hwf := r.dec.wf
  have hq := r.mem
  have hf : r.follows = true → VE.Entails.{u} (En r.dec.D) (queryPremises r.dec.D r.qr) r.qr.target := by
    intro hf
    unfold ConsequenceCase.follows at hf
    split at hf
    · rename_i c _
      exact follows_sound r.dec.D hwf r.qr hq c hf
    · cases hf
  have hg : r.gap = true → ¬ VE.Entails.{u} (En r.dec.D) (queryPremises r.dec.D r.qr) r.qr.target := by
    intro hg
    unfold ConsequenceCase.gap at hg
    split at hg
    · rename_i m _
      exact gap_sound r.dec.D hwf r.qr hq m.M m.valid m.background m.sat (by simpa using hg)
    · cases hg
  exact ⟨hwf, hq, hf, hg, fun ⟨a, b⟩ => hg b (hf a)⟩

/-- A CONFLICT verdict from a witness on the regenerated policy refutes its conflict-freedom, its unique
expansion and the document property (W1's `target_refutes`). -/
theorem speech_wire_conflict_witness_sound (j : Json) (dec : Wire.Decoded)
    (w : VE.Norms.Replay.WitnessData (normsSource dec))
    (h : replayWitness j = .ok ⟨dec, w⟩) (hw : w.conflict = true) :
    ¬ VE.Norms.ConflictFree (policy dec.D) w.M.asStructure ∧
      ¬ (∀ B : VE.Structure.{0}, VE.Norms.BaseAdmissible (policy dec.D) B → VE.Norms.ConflictFree (policy dec.D) B) :=
  let hr := VE.Norms.Replay.target_refutes (policy dec.D) (policy_wellFormed dec.D dec.wf) w.target w.mem
    w.M.asStructure ⟨w.valid, fun a ha => (VE.eval_iff_denote w.M [] a).mp (List.all_eq_true.mp w.background a ha)⟩
    w.tuple w.typed ((VE.eval_iff_denote w.M _ _).mp hw)
  ⟨hr.1, hr.2.2⟩

end VE.SpeechActs.Run
