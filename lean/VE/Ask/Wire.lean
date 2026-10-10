import VE.Ask.Binding
import VE.Readings.VerdictsWire
import VE.Question.Moved
import VE.Question.Properties
import VE.EnglishGrammar.Run
import VE.Ask.Sound

/-! The `ask` wire on the readings route (docs/spec/question-answering.md 4.2, 5.2; plan 4.3, 4.8, R5, Q2.2).

`replayAsk` reads the request's question with `VE.Question.ask` (so the request's formula is never trusted), binds
the readings case to the document (`checkCase`), checks that the case asks this question with no premise and no
assumed reading, replays it with RD-3's `replayVerdictsND`, and builds one `Row` per compatible choice: RD-3's
conflict, premise and query rows, the negation row (a certificate for `¬ψ`, bound as RD-3 binds a choice's
certificate and accepted with the conflict packages, `negRow_holds`) and the split flag (one base model with two
checked fillings, `splitRow_sound`). Every evidence entry must name a compatible choice, once; the reading names must
be exactly one per candidate of every open set, an asserted candidate's read back (`NameReadsBackSame`).
`ask_wire_sound` states what an accepted request establishes. -/

namespace VE.Ask
open Lean VE.Readings VE.Readings.Wire VE.NormDefaults

/-! ## Names -/

/-- A reading's own sentence, as the request names it, and whether Lean read it back (D11). -/
structure Name where
  set : String
  index : Nat
  text : String
  checked : Bool
  deriving DecidableEq, Repr

def candidateContent (case : Json) (s : String) (i : Nat) : Option Json :=
  match (case.getObjValD "document").getObjValD "reading_sets" with
  | .arr rs => (rs.toList.find? (fun R => R.getObjValD "id" == .str s)).bind fun R =>
      match R.getObjValD "readings" with
      | .arr cs => cs[i]?.map (·.getObjValD "content")
      | _ => none
  | _ => none

/-- A reading's own sentence that Lean checked (D11): it reads, with one meaning, as the candidate's content. -/
def NameReadsBack (case : Json) (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) (n : Name) : Prop :=
  ∃ φn : VE.EnglishGrammar.EFormula,
    VE.EnglishGrammar.read E {} L VE.EnglishGrammar.workBudget (n.text ++ ".") = .ok [(φn, false)] ∧
    candidateContent case n.set n.index = some φn.encode

/-- `NameReadsBack` as Lean can decide it: the candidate's content compared with the name's formula as canonical
    JSON text (`Same`). Lean's `Json` has no decidable equality, so the `=` of `NameReadsBack` cannot be checked of a
    request; this is the relation the binding (`UnitBound`) uses for the same comparison. -/
def NameReadsBackSame (case : Json) (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) (n : Name) : Prop :=
  ∃ φn : VE.EnglishGrammar.EFormula,
    VE.EnglishGrammar.read E {} L VE.EnglishGrammar.workBudget (n.text ++ ".") = .ok [(φn, false)] ∧
    ∃ j, candidateContent case n.set n.index = some j ∧ Same j φn.encode

/-- The check of `NameReadsBackSame`. -/
def nameReadsBack (case : Json) (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) (n : Name) : Bool :=
  match VE.EnglishGrammar.read E {} L VE.EnglishGrammar.workBudget (n.text ++ "."), candidateContent case n.set n.index with
  | .ok [(φn, false)], some j => decide (Same j φn.encode)
  | _, _ => false

theorem nameReadsBack_sound {case : Json} {E : VE.EnglishGrammar.Env} {L : VE.EnglishGrammar.Lexicon} {n : Name}
    (h : nameReadsBack case E L n = true) : NameReadsBackSame case E L n := by
  unfold nameReadsBack at h
  split at h
  · rename_i φn j hr hc
    exact ⟨φn, hr, j, hc, by simpa using h⟩
  · cases h

/-! ## The negation row and the split flag of one choice -/

/-- The negation row: `.proved` with a certificate for `¬ψ` over the choice's filled premises and the conflict
    packages accepted (as RD-3's query row, S2a 14.8). -/
def negRow {N : NDoc} {c : Choice} (e : NDEvidence N c) (ψ : VE.Formula) (k : Option VE.Tableau.Certificate) :
    ChoiceResult :=
  if (k.map (ndCertOk N c [] (.not ψ))).getD false && ndFree e then .proved else .unknown

theorem negRow_holds {N : NDoc} {c : Choice} (e : NDEvidence N c) (ψ : VE.Formula)
    (k : Option VE.Tableau.Certificate) : Holds.{u} N [] (.not ψ) c (negRow e ψ k) := by
  unfold negRow
  split
  · rename_i hp
    simp only [Bool.and_eq_true] at hp
    obtain ⟨hk, hf⟩ := hp
    cases hc : k with
    | none => rw [hc] at hk; cases hk
    | some k =>
      rw [hc] at hk
      exact ⟨ndFree_sound e hf, ndCertOk_sound e [] (.not ψ) k hk⟩
  · trivial

/-- The negation certificate of a choice's evidence entry (`negation.certificate`), bound as RD-3 binds a choice's
    certificate (`ndBoundCert`), its conclusion `¬ψ`; absent or refused, none. -/
def negCert (r : AdmittedND) (c : Choice) (ψ : VE.Formula) (entry : Json) : Option VE.Tableau.Certificate :=
  (pieceOf entry "negation").bind fun p => (ndBoundCert r c [] (encF (.not ψ)) (p.getObjValD "certificate")).toOption

theorem castFM_M {U U' : UDoc} (h : U = U') (m : FilledModel U) : (castFM h m).M = m.M := by
  subst h
  rfl

/-- The split pieces decoded on the choice's layered source: one base situation (`model`) and two fillings,
    `true` (ψ holds) and `false` (ψ fails). -/
def splitModels (r : AdmittedND) (c : Choice) (hw : WellFormedU (choiceU r.N c) = true) (p : Json) :
    Option (FilledModel (choiceU r.N c) × FilledModel (choiceU r.N c)) :=
  match choiceLayered r c hw with
  | .error _ => none
  | .ok L => match VE.NormDefaults.Wire.situationX L.1 (p.getObjValD "model") with
    | .error _ => none
    | .ok S => match VE.NormDefaults.Wire.decodeFilling L.1.U S.M (p.getObjValD "true"),
        VE.NormDefaults.Wire.decodeFilling L.1.U S.M (p.getObjValD "false") with
      | .ok F₁, .ok F₂ => some (castFM L.2 ⟨S.M, S.valid, F₁⟩, castFM L.2 ⟨S.M, S.valid, F₂⟩)
      | _, _ => none

theorem splitModels_base {r : AdmittedND} {c : Choice} {hw : WellFormedU (choiceU r.N c) = true} {p : Json}
    {m₁ m₂ : FilledModel (choiceU r.N c)} (h : splitModels r c hw p = some (m₁, m₂)) : m₁.M = m₂.M := by
  unfold splitModels at h
  split at h
  · cases h
  · split at h
    · cases h
    · split at h
      · rename_i L S F₁ F₂ _ _
        cases h
        rw [castFM_M, castFM_M]
      · cases h

/-- The split flag: both fillings check, ψ true under the first and false under the second. -/
def splitRow (r : AdmittedND) (c : Choice) (e : NDEvidence r.N c) (ψ : VE.Formula) (entry : Json) : Bool :=
  match (pieceOf entry "split").bind (splitModels r c e.wfc) with
  | some (m₁, m₂) => ndModelOk r.N c [] ψ m₁ true && ndModelOk r.N c [] ψ m₂ false
  | none => false

theorem splitRow_sound {r : AdmittedND} {c : Choice} (e : NDEvidence r.N c) (ψ : VE.Formula) (entry : Json)
    (h : splitRow r c e ψ entry = true) : SplitU (choiceU r.N c) (choiceDoc r.N.D c).2 ψ := by
  unfold splitRow at h
  split at h
  · rename_i m₁ m₂ hs
    simp only [Bool.and_eq_true] at h
    obtain ⟨p, _, hp⟩ := Option.bind_eq_some_iff.mp hs
    exact splitOk_sound r.N c e ψ m₁ m₂ (splitModels_base hp) h.1 h.2
  · cases h

/-! ## The rows of a replayed case -/

/-- One compatible choice's row: RD-3's three rows, the negation row and the split flag, from the case's evidence
    entry for the choice. -/
def rowOf (x : NDVerdicts) (j : Json) (e : (c : Choice) × NDEvidence x.r.N c) : Row :=
  let entry := VE.Readings.Run.entryFor (VE.Readings.Run.evidenceList j) e.1
  { choice := e.1, conflict := ndConflictRow e.2, premise := ndPremiseRow e.2, query := ndQueryRow e.2 x.Γ x.φ,
    negation := negRow e.2 x.φ (negCert x.r e.1 x.φ entry), split := splitRow x.r e.1 e.2 x.φ entry }

theorem rowOf_ok (x : NDVerdicts) (j : Json) (hΓ : x.Γ = []) (e : (c : Choice) × NDEvidence x.r.N c) :
    RowOk.{0} x.r.N x.φ (rowOf x j e) := by
  refine ⟨ndConflictRow_holds e.2, ndPremiseRow_holds e.2, ?_, negRow_holds e.2 x.φ _, splitRow_sound e.2 x.φ _⟩
  have := ndQueryRow_holds.{0} e.2 x.Γ x.φ
  rw [hΓ] at this
  simpa [rowOf, hΓ] using this

def rowsOf (x : NDVerdicts) (j : Json) : List Row := x.evs.map (rowOf x j)

theorem rowsOf_choices (x : NDVerdicts) (j : Json) : (rowsOf x j).map (·.choice) = x.evs.map (·.1) := by
  simp [rowsOf, rowOf, Function.comp_def]

theorem rowsOf_ok (x : NDVerdicts) (j : Json) (hΓ : x.Γ = []) : ∀ r ∈ rowsOf x j, RowOk.{0} x.r.N x.φ r := by
  intro r hr
  obtain ⟨e, _, rfl⟩ := List.mem_map.mp hr
  exact rowOf_ok x j hΓ e

/-! ## The replayed request -/

structure Asked where
  request : Json
  text : String
  q : String
  case : Json
  E : VE.EnglishGrammar.Env
  L : VE.EnglishGrammar.Lexicon
  c : VE.Question.Candidate
  φ : VE.EnglishGrammar.EFormula
  x : VE.Readings.Wire.NDVerdicts
  rows : List Row
  names : List Name
  hbind : CaseBinding text case E L
  hrequest : request.getObjValD "document" = .str text ∧
    request.getObjValD "question" = .str q ∧ request.getObjValD "case" = case
  hreplay : VE.Readings.Run.replayVerdictsND case = .ok x
  hread : VE.Question.QuestionOneReading VE.Question.auxiliaries E {} L q c φ
  hψ : case.getObjValD "question" = .str "query" ∧
    Same (case.getObjValD "conclusion") φ.encode ∧
    VE.Route.Wire.decodeClosed (VE.Readings.Wire.fullEnv x.r.N ((x.evs.map (·.1)).headD []))
      (case.getObjValD "conclusion") = .ok x.φ
  hx : x.Γ = [] ∧ x.A = []
  hrows : rows.map (·.choice) = x.evs.map (·.1)
  hok : ∀ r ∈ rows, RowOk.{0} x.r.N x.φ r
  hnames : ∀ n ∈ names, n.checked = true → NameReadsBackSame case E L n

/-- A string member of the request, with its equation. -/
def strField (j : Json) (k : String) : Except String { s : String // j.getObjValD k = .str s } :=
  match j.getObjValD k with
  | .str s => .ok ⟨s, rfl⟩
  | _ => .error s!"InvalidInput: {k} is a string"

/-- The display number of each front-matter unit: its position, from 1. -/
def displayNumbers (front : Json) : List (String × Nat) :=
  match front.getObjValD "units" with
  | .arr us => (us.toList.zip (List.range us.size)).filterMap fun (u, n) => (strOf? (u.getObjValD "id")).map (·, n + 1)
  | _ => []

/-- The display number of a set's unit, for the name-check refusal. -/
def setNumber (D : Doc) (front : Json) (s : String) : String :=
  match D.sets.find? (·.id == s) with
  | some R => match (displayNumbers front).lookup R.unit with
    | some n => toString n
    | none => R.unit
  | none => s

/-- Every candidate of every open set, in source order. -/
def allCandidates (D : Doc) : List (String × Nat) := D.sets.flatMap fun R => (List.range R.candidates.length).map (R.id, ·)

/-- A candidate whose content is a norm object is not read back until E3 (D11); every other content is. -/
def assertedCandidate (case : Json) (s : String) (i : Nat) : Bool :=
  match candidateContent case s i with
  | some c => (c.getObjVal? "norm").toOption.isNone
  | none => false

/-- The request's names: one `{set, index, text}` per candidate of every open set, in source order (none missing,
    none extra); an asserted candidate's name is read back, and one that fails refuses the answer (R8). -/
def decodeNames (D : Doc) (front case : Json) (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon)
    (j : Json) : Except String { ns : List Name // ∀ n ∈ ns, n.checked = true → NameReadsBackSame case E L n } := do
  let items ← match j with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: names is a list"
  let raw ← items.mapM fun it => do
    VE.Bridge.exactFields it ["set", "index", "text"]
    let s ← VE.Bridge.stringField it "set"
    let i ← (it.getObjValD "index").getNat?
    let t ← VE.Bridge.stringField it "text"
    if t.isEmpty then throw "InvalidInput: a reading's name is empty"
    pure (s, i, t)
  unless raw.map (fun (s, i, _) => (s, i)) == allCandidates D do
    throw "InvalidInput: the names are not one per candidate of every open set, in source order"
  let names := raw.map fun (s, i, t) => { set := s, index := i, text := t, checked := assertedCandidate case s i : Name }
  match names.find? (fun n => n.checked && !nameReadsBack case E L n) with
  | some n => throw s!"CheckerUnavailable: VE could not check the wording of a reading of sentence {setNumber D front n.set}"
  | none =>
    if h : ∀ n ∈ names, n.checked = true → nameReadsBack case E L n = true then
      pure ⟨names, fun n hn hc => nameReadsBack_sound (h n hn hc)⟩
    else throw "CheckerUnavailable: VE could not check the wording of a reading"

/-- Every evidence entry names a compatible choice, once (an extra or repeated entry is refused). -/
def evidenceBound (case : Json) (choices : List Choice) : Bool :=
  let named := (VE.Readings.Run.evidenceList case).map fun e => jchoice (e.getObjValD "choice")
  named.all choices.contains && decide named.Nodup &&
    (VE.Readings.Run.evidenceList case).all fun e => (decodeChoice (e.getObjValD "choice")).toOption.isSome

/-- The English environment and lexicon of a request: the front matter's environment, decoded with no overlay,
    and the request's lexicon bound to it. -/
def englishOf (text : String) (lexicon : Json) : Except String (VE.EnglishGrammar.Env × VE.EnglishGrammar.Lexicon) := do
  let sp ← VE.Service.Document.split text
  let environment := sp.front.getObjValD "environment"
  let E ← VE.EnglishGrammar.Env.decode environment (Json.mkObj [])
  let lexiconEnvId ← VE.EnglishGrammar.Run.environmentId (VE.EnglishGrammar.displayJson environment (Json.mkObj []))
  let L ← VE.EnglishGrammar.Run.decodeLexicon lexiconEnvId lexicon
  pure (E, L)

/-- The question's one reading, as the mode shows it (`ask`: a moved-out reading is refused). -/
def oneReading (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) (q : String) :
    Except String { p : VE.Question.Candidate × VE.EnglishGrammar.EFormula //
      VE.Question.QuestionOneReading VE.Question.auxiliaries E {} L q p.1 p.2 } :=
  match h : VE.Question.ask VE.Question.auxiliaries E {} L VE.EnglishGrammar.workBudget q with
  | .read (.one c φ) =>
    .ok ⟨(c, φ), (VE.Question.readQuestion_one _ _ _ _ _ _ _ _
      (VE.Question.ask_one _ _ _ _ _ _ _ _ h).1).2⟩
  | _ => .error "InvalidInput: the question has no one reading"

/-- The request replayed, with `request := j`. -/
def replayAskCore (j : Json) : Except String { a : Asked // a.request = j } := do
  let ⟨text, hd⟩ ← strField j "document"
  let ⟨q, hq⟩ ← strField j "question"
  let case := j.getObjValD "case"
  let (_, L) ← englishOf text (j.getObjValD "lexicon")
  let ⟨E, hbind⟩ ← checkCase text case L
  let ⟨(c, φ), hread⟩ ← oneReading E L q
  if hqs : strOf? (case.getObjValD "question") = some "query" then
  if hsame : Same (case.getObjValD "conclusion") φ.encode then
    match hr : VE.Readings.Run.replayVerdictsND case with
    | .error e => throw e
    | .ok x =>
      match hdc : VE.Route.Wire.decodeClosed (VE.Readings.Wire.fullEnv x.r.N ((x.evs.map (·.1)).headD []))
          (case.getObjValD "conclusion") with
      | .error e => throw e
      | .ok f =>
        if hf : f = x.φ then
          if hx : x.Γ = [] ∧ x.A = [] then
            unless evidenceBound case (x.evs.map (·.1)) do
              throw "InvalidInput: an evidence entry names no compatible choice, or one twice"
            let sp ← VE.Service.Document.split text
            let ⟨names, hnames⟩ ← decodeNames x.r.N.D sp.front case E L (j.getObjValD "names")
            pure ⟨⟨j, text, q, case, E, L, c, φ, x, rowsOf x case, names, hbind, ⟨hd, hq, rfl⟩, hr, hread,
              ⟨eq_of_strOf? hqs, hsame, by rw [hdc, hf]⟩, hx, rowsOf_choices x case, rowsOf_ok x case hx.1, hnames⟩, rfl⟩
          else throw "InvalidInput: the case does not ask this question (premises or assumed readings)"
        else throw "InvalidInput: the case does not ask this question"
  else throw "InvalidInput: the case does not ask this question"
  else throw "InvalidInput: the case does not ask this question"

def replayAsk (j : Json) : Except String Asked := (replayAskCore j).map Subtype.val

theorem replayAsk_request {j : Json} {a : Asked} (h : replayAsk j = .ok a) : a.request = j := by
  unfold replayAsk at h
  cases hc : replayAskCore j with
  | error e => rw [hc] at h; cases h
  | ok s =>
    rw [hc] at h
    cases h
    exact s.2

theorem ask_wire_sound : ∀ (j : Json) (a : Asked), replayAsk j = .ok a →
    a.request = j ∧ a.text = (j.getObjValD "document").getStr?.toOption.getD "" ∧
    a.q = (j.getObjValD "question").getStr?.toOption.getD "" ∧ a.case = j.getObjValD "case" ∧
    VE.Readings.Run.replayVerdictsND a.case = .ok a.x ∧
    (∀ r ∈ a.rows, LeadHolds.{0} a.x.r.N a.x.φ r) ∧
    (∀ r ∈ a.rows, ∀ x, r.reason = some x → ReasonHolds.{0} a.x.r.N a.x.φ r x) ∧
    (∀ c, Compatible a.x.r.N.D c ↔ c ∈ a.rows.map (·.choice)) ∧
    CaseBinding a.text a.case a.E a.L ∧
    VE.Question.QuestionOneReading VE.Question.auxiliaries a.E {} a.L a.q a.c a.φ := by
  intro j a h
  have hj := replayAsk_request h
  obtain ⟨hd, hq, hc⟩ := a.hrequest
  rw [hj] at hd hq hc
  refine ⟨hj, by rw [hd]; rfl, by rw [hq]; rfl, hc.symm, a.hreplay, fun r hr => lead_sound _ _ r (a.hok r hr),
    fun r hr x hx => reason_sound _ _ r x (a.hok r hr) hx, fun c => ?_, a.hbind, a.hread⟩
  rw [a.hrows, a.x.hevs, mem_chosenOf _ a.x.ready a.x.hle, a.hx.2]
  simp

end VE.Ask
