import VE.Ask.Render
import VE.Ask.Plain
import VE.Route.Typed

/-! The plain adapter (docs/spec/question-answering.md 5.2; plan 4.7, R13, Q2.2): `relational-fol@0` documents with no
norms and no reading set, answered by the FOL route's own checkers.

The case is `{"environment", "document": {"units"}, "conclusion", "evidence"}`. Lean decodes the environment as the
route does (`Gate.decodeEnvelope`, `Typed.routeVocabulary`), takes the premises `Γ` to be the route's regenerated
Background followed by the asserted units' formulas in unit order, and checks each piece of evidence: a certificate
for the conclusion, for its negation (`negation`) and for `⊥` (`unsat`), bound to the environment and the premises as
the route binds a certificate and replayed by `checkCertificate`; a countermodel and a premise model decoded as the
route decodes a model (`decodeDataModel`: admissible, literals distinct, flags hold). The row is `PlainRow`, whose
claims `PlainRowOk` states and `plain_lead_sound` reads. `PlainCaseBinding` binds the case to the document as
`CaseBinding` does, and `plain_ask_wire_sound` states what an accepted request establishes. -/

namespace VE.Ask
open Lean VE.Readings VE.Readings.Wire VE.Route.Wire

/-- The plain adapter has the same file-to-case unit conversion and source-byte binding as `CaseBinding`, but
    replays through the lower `relational-fol@0` checker. -/
def PlainCaseBinding (text : String) (case : Json) (E : VE.EnglishGrammar.Env)
    (L : VE.EnglishGrammar.Lexicon) (V : VE.Environment) : Prop :=
  ∃ sp : VE.Discourse.Loader.Split, VE.Service.Document.split text = .ok sp ∧
    Same (case.getObjValD "environment") (sp.front.getObjValD "environment") ∧
    (∀ k ∈ boundKeys, Same ((case.getObjValD "document").getObjValD k) (sp.front.getObjValD k)) ∧
    VE.EnglishGrammar.Env.decode (sp.front.getObjValD "environment") (Json.mkObj []) = .ok E ∧
    L.policyOk E {} = true ∧
    ∃ cus fus : Array Json, (case.getObjValD "document").getObjValD "units" = .arr cus ∧
      sp.front.getObjValD "units" = .arr fus ∧ cus.size = fus.size ∧
      ∀ i (h₁ : i < cus.size) (h₂ : i < fus.size), UnitBound E L V sp.fences cus[i] fus[i]

structure PlainVerdict where
  V : VE.Environment
  Γ : List VE.Formula
  ψ : VE.Formula
  row : PlainRow
  hok : PlainRowOk.{0} V Γ ψ row

/-! ## The decoded case -/

/-- What Lean decodes of a plain case: the route's vocabulary, the asserted units (id, content JSON, formula), the
    conclusion. -/
structure PlainParts where
  profiles : List String
  environment : Json
  rv : RouteVocabulary
  units : List (String × Json × VE.Formula)
  conclusion : Json
  ψ : VE.Formula
  hψ : VE.Route.Wire.decodeClosed rv.environment conclusion = .ok ψ

def PlainParts.V (p : PlainParts) : VE.Environment := p.rv.environment
def PlainParts.background (p : PlainParts) : List VE.Formula := (fullBackground p.rv).map Prod.fst
/-- `Γ`: the regenerated Background, then the assertions in unit order. -/
def PlainParts.Γ (p : PlainParts) : List VE.Formula := p.background ++ p.units.map (·.2.2)
/-- The JSON of `Γ`, as the route binds a certificate's premises. -/
def PlainParts.premisesJson (p : PlainParts) : List Json := p.background.map encodeFormula ++ p.units.map (·.2.1)
/-- Where each premise of `Γ` comes from. -/
def PlainParts.sources (p : PlainParts) : List Source :=
  p.background.map (fun _ => Source.background) ++ p.units.map (fun u => Source.unit u.1)

theorem PlainParts.sources_length (p : PlainParts) : p.sources.length = p.Γ.length := by
  simp [PlainParts.sources, PlainParts.Γ]

/-- One unit of the case: its asserted formula, none for a unit without content; a norm or any other content is not
    a plain document's. -/
def plainUnit (V : VE.Environment) (data : Bool) (u : Json) : Except String (Option (String × Json × VE.Formula)) := do
  let id ← VE.Bridge.stringField u "id"
  match u.getObjValD "content" with
  | .null => pure none
  | c =>
    unless strOf? (u.getObjValD "kind") == some "asserted" do
      throw "UnsupportedProfile: the plain route answers documents whose content is asserted formulas"
    pure (some (id, c, ← VE.Route.Wire.decodeClosed V c data))

def plainParts (case : Json) : Except String { p : PlainParts // p.conclusion = case.getObjValD "conclusion" } := do
  VE.Bridge.exactFields case ["environment", "document", "conclusion", "evidence"]
  let environment ← case.getObjVal? "environment"
  let e ← VE.Route.Gate.decodeEnvelope environment
  unless e.family == .fol && !e.profiles.contains "norms@0" && !e.profiles.contains "readings@1" do
    throw "UnsupportedProfile: the plain route answers relational-fol@0 documents without norms or readings"
  let rv ← VE.Route.Typed.routeVocabulary e
  let data := e.profiles.contains "data@0"
  let us ← match (case.getObjValD "document").getObjValD "units" with
    | .arr us => pure us.toList
    | _ => throw "InvalidInput: the case's units are a list"
  let units ← us.filterMapM (plainUnit rv.environment data)
  let conclusion := case.getObjValD "conclusion"
  match h : VE.Route.Wire.decodeClosed rv.environment conclusion with
  | .ok ψ => pure ⟨⟨e.profiles, environment, rv, units, conclusion, ψ, h⟩, rfl⟩
  | .error err => throw err

/-! ## The evidence and the row -/

/-- A certificate piece's certificate, bound as the route binds one to `Γ` and `conclusion`. -/
def plainCert (p : PlainParts) (conclusion : Json) (piece : Option Json) : Option VE.Tableau.Certificate :=
  piece.bind fun j => match VE.CertificateWire.decodeCertificate (j.getObjValD "certificate") with
    | .ok k => match bindingOk p.profiles p.environment p.premisesJson conclusion k.environment_id
        k.premise_meaning_ids k.conclusion_meaning_id with
      | .ok () => if VE.CertificateWire.folSteps k.trace ≤ VE.CertificateWire.maxSteps then some k else none
      | .error _ => none
    | .error _ => none

/-- A model piece's model, decoded as the route decodes a model. -/
def plainModel (p : PlainParts) (piece : Option Json) : Option (VE.FiniteModel VE.Bridge.Entity) :=
  piece.bind fun j => (decodeDataModel p.rv (j.getObjValD "model")).toOption

theorem plainModel_admissible {p : PlainParts} {piece : Option Json} {M : VE.FiniteModel VE.Bridge.Entity}
    (h : plainModel p piece = some M) : M.asStructure.Admissible p.V := by
  unfold plainModel at h
  cases hp : piece with
  | none => rw [hp] at h; cases h
  | some j =>
    rw [hp] at h
    simp only [Option.bind_some] at h
    cases hd : decodeDataModel p.rv (j.getObjValD "model") with
    | error e => rw [hd] at h; cases h
    | ok M' =>
      rw [hd] at h
      have hM : M' = M := by simpa [Except.toOption] using h
      subst hM
      exact (decodeDataModel_valid p.rv _ M' hd).1.1

def plainProved (p : PlainParts) (φ : VE.Formula) (k : Option VE.Tableau.Certificate) : Bool :=
  (k.map (VE.Tableau.checkCertificate p.V p.Γ φ)).getD false

theorem plainProved_sound {p : PlainParts} {φ : VE.Formula} {k : Option VE.Tableau.Certificate}
    (h : plainProved p φ k = true) : VE.Entails.{u} p.V p.Γ φ := by
  unfold plainProved at h
  cases hk : k with
  | none => rw [hk] at h; cases h
  | some k => rw [hk] at h; exact VE.Tableau.checkCertificate_sound _ _ _ k h

/-- The pieces of the case's evidence. -/
def PlainParts.piece (_p : PlainParts) (case : Json) (k : String) : Option Json :=
  pieceOf (case.getObjValD "evidence") k

/-- A checked countermodel: an admissible model where `Γ` holds and the conclusion fails. -/
def plainRefutes (p : PlainParts) (case : Json) : Bool :=
  match plainModel p (p.piece case "countermodel") with
  | some M => VE.countermodelCheck M p.Γ p.ψ
  | none => false

theorem plainRefutes_sound {p : PlainParts} {case : Json} (h : plainRefutes p case = true) :
    ¬ VE.Entails.{0} p.V p.Γ p.ψ := by
  unfold plainRefutes at h
  split at h
  · rename_i M hM
    obtain ⟨hp, hn⟩ := (VE.countermodelCheck_iff M p.Γ p.ψ).mp h
    exact fun he => hn (he M.asStructure (plainModel_admissible hM) hp)
  · cases h

/-- A checked premise model: an admissible model where `Γ` holds. -/
def plainConsistent (p : PlainParts) (case : Json) : Bool :=
  match plainModel p (p.piece case "model") with
  | some M => p.Γ.all (·.eval M [])
  | none => false

theorem plainConsistent_sound {p : PlainParts} {case : Json} (h : plainConsistent p case = true) :
    Consistent p.V p.Γ := by
  unfold plainConsistent at h
  split at h
  · rename_i M hM
    exact ⟨M.asStructure, plainModel_admissible hM, fun a ha =>
      (VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp h a ha)⟩
  · cases h

def plainProvesUnsat (p : PlainParts) (case : Json) : Bool :=
  plainProved p .bottom (plainCert p (encodeFormula .bottom) (p.piece case "unsat"))
def plainProvesQuery (p : PlainParts) (case : Json) : Bool :=
  plainProved p p.ψ (plainCert p p.conclusion (p.piece case "certificate"))
def plainProvesNegation (p : PlainParts) (case : Json) : Bool :=
  plainProved p (.not p.ψ) (plainCert p (encodeFormula (.not p.ψ)) (p.piece case "negation"))

/-- The row of a plain case. -/
def plainRow (p : PlainParts) (case : Json) : PlainRow :=
  { premise := if plainProvesUnsat p case then .inconsistent
      else if plainConsistent p case then .model else .unknown,
    query := if plainProvesQuery p case then .proved else if plainRefutes p case then .refuted else .unknown,
    negation := if plainProvesNegation p case then .proved else .unknown }

theorem plainRow_ok (p : PlainParts) (case : Json) : PlainRowOk.{0} p.V p.Γ p.ψ (plainRow p case) := by
  refine ⟨fun h => ?_, fun h => ?_, fun h => ?_, fun h => ?_, fun h => ?_⟩
  · by_cases h1 : plainProvesUnsat p case = true <;> by_cases h2 : plainConsistent p case = true <;>
      simp [plainRow, h1, h2] at h
    exact plainConsistent_sound h2
  · by_cases h1 : plainProvesUnsat p case = true <;> by_cases h2 : plainConsistent p case = true <;>
      simp [plainRow, h1, h2] at h
    all_goals exact plainProved_sound h1
  · by_cases h1 : plainProvesQuery p case = true <;> by_cases h2 : plainRefutes p case = true <;>
      simp [plainRow, h1, h2] at h
    all_goals exact plainProved_sound h1
  · by_cases h1 : plainProvesQuery p case = true <;> by_cases h2 : plainRefutes p case = true <;>
      simp [plainRow, h1, h2] at h
    exact plainRefutes_sound h2
  · by_cases h1 : plainProvesNegation p case = true <;> simp [plainRow, h1] at h
    exact plainProved_sound h1

/-- The replay of a plain case: its parts decoded and its row checked. -/
def replayPlainParts (case : Json) : Except String { px : PlainParts × PlainVerdict //
    px.1.conclusion = case.getObjValD "conclusion" ∧ px.2.V = px.1.V ∧ px.2.ψ = px.1.ψ } :=
  match plainParts case with
  | .error e => .error e
  | .ok ⟨p, hc⟩ => .ok ⟨(p, ⟨p.V, p.Γ, p.ψ, plainRow p case, plainRow_ok p case⟩), hc, rfl, rfl⟩

def replayPlain (case : Json) : Except String PlainVerdict := (replayPlainParts case).map (·.1.2)

/-! ## The binding of a plain case -/

/-- The binding's first check, before anything of the case is decoded (spec 4.2: the binding, then the replay): the
    case's environment is the front matter's. -/
def sameEnvironment (text : String) (case : Json) : Except String Unit := do
  let sp ← VE.Service.Document.split text
  unless decide (Same (case.getObjValD "environment") (sp.front.getObjValD "environment")) do
    throw "CheckerUnavailable: the case is not this document's (another environment)"

/-- A one-choice route's request names no reading: a document without an open set has no candidate, so its names
    are the empty list (`decodeNames`'s rule, with no candidate). -/
def noNames (j : Json) : Except String Unit :=
  match j.getObjValD "names" with
  | .arr xs => if xs.isEmpty then pure () else
      throw "InvalidInput: the names are not one per candidate of every open set, in source order"
  | _ => throw "InvalidInput: names is a list"

/-- A one-choice route's case: exactly its environment, document, conclusion and an object of evidence pieces (no
    piece of another type read as no evidence). -/
def oneChoiceCase (case : Json) : Except String Unit := do
  match VE.Bridge.exactFields case ["environment", "document", "conclusion", "evidence"] with
  | .error e => throw s!"InvalidInput: the case's {e}"
  | .ok () => pure ()
  match case.getObjValD "evidence" with
  | .obj _ => pure ()
  | _ => throw "InvalidInput: the case's evidence is an object of pieces"

/-- `PlainCaseBinding`, decided, with `E` decoded from the front matter. -/
def checkPlainCase (text : String) (case : Json) (L : VE.EnglishGrammar.Lexicon) (V : VE.Environment) :
    Except String { E : VE.EnglishGrammar.Env // PlainCaseBinding text case E L V } :=
  match hs : VE.Service.Document.split text with
  | .error e => .error e
  | .ok sp =>
    if he : Same (case.getObjValD "environment") (sp.front.getObjValD "environment") then
      if hk : ∀ k ∈ boundKeys, Same ((case.getObjValD "document").getObjValD k) (sp.front.getObjValD k) then
        match hE : VE.EnglishGrammar.Env.decode (sp.front.getObjValD "environment") (Json.mkObj []) with
        | .error e => .error e
        | .ok E =>
          if hp : L.policyOk E {} = true then
            match hc : (case.getObjValD "document").getObjValD "units", hf : sp.front.getObjValD "units" with
            | .arr cus, .arr fus =>
              if hu : checkUnits E L V sp.fences cus fus = true then
                .ok ⟨E, sp, hs, he, hk, hE, hp, cus, fus, hc, hf, (checkUnits_sound hu).1, (checkUnits_sound hu).2⟩
              else .error "CheckerUnavailable: the case is not this document's (a unit differs)"
            | _, _ => .error "CheckerUnavailable: the case is not this document's (its units are not a list)"
          else .error "CheckerUnavailable: the lexicon does not pass the vocabulary policy for this document"
      else .error "CheckerUnavailable: the case is not this document's (a front-matter input differs)"
    else .error "CheckerUnavailable: the case is not this document's (another environment)"

structure PlainAsked where
  request : Json
  text : String
  q : String
  case : Json
  E : VE.EnglishGrammar.Env
  L : VE.EnglishGrammar.Lexicon
  c : VE.Question.Candidate
  φ : VE.EnglishGrammar.EFormula
  x : PlainVerdict
  hrequest : request.getObjValD "document" = .str text ∧
    request.getObjValD "question" = .str q ∧ request.getObjValD "case" = case
  hbind : PlainCaseBinding text case E L x.V
  hreplay : replayPlain case = .ok x
  hread : VE.Question.QuestionOneReading VE.Question.auxiliaries E {} L q c φ
  hψ : Same (case.getObjValD "conclusion") φ.encode ∧
    VE.Route.Wire.decodeClosed x.V (case.getObjValD "conclusion") = .ok x.ψ

/-- The plain request replayed, with `request := j`. -/
def replayPlainAskCore (j : Json) : Except String { a : PlainAsked // a.request = j } := do
  let ⟨text, hd⟩ ← strField j "document"
  let ⟨q, hq⟩ ← strField j "question"
  let case := j.getObjValD "case"
  let (_, L) ← englishOf text (j.getObjValD "lexicon")
  sameEnvironment text case
  noNames j
  oneChoiceCase case
  match hr : replayPlainParts case with
  | .error e => throw e
  | .ok ⟨(p, x), hconc, hV, hψx⟩ =>
    have hx : replayPlain case = .ok x := by rw [replayPlain, hr]; rfl
    let ⟨E, hbind⟩ ← checkPlainCase text case L x.V
    let ⟨(c, φ), hread⟩ ← oneReading E L q
    if hsame : Same (case.getObjValD "conclusion") φ.encode then
      pure ⟨⟨j, text, q, case, E, L, c, φ, x, ⟨hd, hq, rfl⟩, hbind, hx, hread,
        ⟨hsame, by rw [hV, hψx, ← hconc]; exact p.hψ⟩⟩, rfl⟩
    else throw "InvalidInput: the case does not ask this question"

def replayPlainAsk (j : Json) : Except String PlainAsked := (replayPlainAskCore j).map Subtype.val

theorem replayPlainAsk_request {j : Json} {a : PlainAsked} (h : replayPlainAsk j = .ok a) : a.request = j := by
  unfold replayPlainAsk at h
  cases hc : replayPlainAskCore j with
  | error e => rw [hc] at h; cases h
  | ok s =>
    rw [hc] at h
    cases h
    exact s.2

theorem plain_ask_wire_sound : ∀ (j : Json) (a : PlainAsked), replayPlainAsk j = .ok a →
    a.request = j ∧ a.text = (j.getObjValD "document").getStr?.toOption.getD "" ∧
    a.q = (j.getObjValD "question").getStr?.toOption.getD "" ∧ a.case = j.getObjValD "case" ∧
    replayPlain a.case = .ok a.x ∧ PlainCaseBinding a.text a.case a.E a.L a.x.V ∧
    VE.Question.QuestionOneReading VE.Question.auxiliaries a.E {} a.L a.q a.c a.φ ∧
    LeadHoldsPlain.{0} a.x.V a.x.Γ a.x.ψ a.x.row := by
  intro j a h
  have hj := replayPlainAsk_request h
  obtain ⟨hd, hq, hc⟩ := a.hrequest
  rw [hj] at hd hq hc
  exact ⟨hj, by rw [hd]; rfl, by rw [hq]; rfl, hc.symm, a.hreplay, a.hbind, a.hread,
    plain_lead_sound _ _ _ _ a.x.hok⟩

end VE.Ask
