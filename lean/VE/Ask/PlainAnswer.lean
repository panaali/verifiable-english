import VE.Ask.PlainWire

/-! The plain adapter's answer (docs/spec/question-answering.md 5.2; plan 4.7, R13, Q2.3): one row, choice `[]`, rendered
by `VE.Ask.Lines` from its view. A yes or no row cites exactly the sources of the positions its replayed certificate
uses (`plainCites_spec`); a countermodel's situation is the checked model's (`VE.Words.situation`); every shown line
passes W7's gate (`answerForPlain_gated`). -/

namespace VE.Ask
open Lean VE.Readings VE.Readings.Wire VE.Route.Wire

/-- The row of a plain verdict, as the lines read rows: choice `[]`, conflict-free (no rules), no split. -/
def PlainRow.toRow (r : PlainRow) : Row := ⟨[], .free, r.premise, r.query, r.negation, false⟩

theorem PlainRow.toRow_lead (r : PlainRow) : r.toRow.lead = r.lead := rfl

/-- Each premise of `Γ` with its source: the Background's are the word list's, each assertion its unit's. -/
def PlainParts.sourced (p : PlainParts) : List (Source × VE.Formula) :=
  p.background.map (Source.background, ·) ++ p.units.map fun u => (Source.unit u.1, u.2.2)

theorem PlainParts.sourced_sources (p : PlainParts) : p.sourced.map (·.1) = p.sources := by
  simp [PlainParts.sourced, PlainParts.sources, Function.comp_def]

theorem PlainParts.sourced_premises (p : PlainParts) : p.sourced.map (·.2) = p.Γ := by
  simp [PlainParts.sourced, PlainParts.Γ, Function.comp_def]

/-- The certificate a yes or no plain row rests on, with what it proves. -/
def plainCertPiece (p : PlainParts) (case : Json) (r : PlainRow) : Option (VE.Formula × VE.Tableau.Certificate) :=
  match r.lead with
  | .yes => (plainCert p p.conclusion (p.piece case "certificate")).map (p.ψ, ·)
  | .no => (plainCert p (encodeFormula (.not p.ψ)) (p.piece case "negation")).map (.not p.ψ, ·)
  | _ => none

def plainUsed (p : PlainParts) (ψ : VE.Formula) (k : VE.Tableau.Certificate) : List Nat := usedPositions p.V p.Γ ψ k

/-- The sources a yes or no plain row cites: exactly the sources of the positions its certificate uses. -/
def plainCites (p : PlainParts) (case : Json) (r : PlainRow) : List Source :=
  match plainCertPiece p case r with
  | some (ψ, k) => cited p.sources (plainUsed p ψ k)
  | none => []

theorem plainCites_spec (p : PlainParts) (case : Json) (r : PlainRow) (ψ : VE.Formula) (k : VE.Tableau.Certificate)
    (h : plainCertPiece p case r = some (ψ, k)) :
    (∀ s, s ∈ plainCites p case r ↔ ∃ i ∈ plainUsed p ψ k, (p.sourced[i]?).map (·.1) = some s) ∧
    (∀ (i : Nat) (s : Source) (f : VE.Formula), p.sourced[i]? = some (s, f) → p.Γ[i]? = some f) ∧
    (replayOk p.V p.Γ ψ k = true → VE.Entails.{0} p.V ((plainUsed p ψ k).filterMap (p.Γ[·]?)) ψ) := by
  refine ⟨fun s => ?_, fun i s f hi => ?_, fun hr => usedPositions_sufficient _ _ ψ k hr⟩
  · simp only [plainCites, h, mem_cited, ← p.sourced_sources, List.getElem?_map]
  · rw [← p.sourced_premises, List.getElem?_map, hi]
    rfl

/-- The view of a plain answer. -/
def plainView (s : PlainAsked) (p : PlainParts) (unused : List String) : View :=
  let words := (englishOf s.text (s.request.getObjValD "lexicon")).toOption
  { asked := s.c, ids := [], rows := [s.x.row.toRow], cites := fun _ => plainCites p s.case s.x.row, names := [],
    unused := unused, words := words, setUnit := fun _ => none,
    situation := fun frame _ => if frame == "S1" then
        match words, plainModel p (p.piece s.case "countermodel") with
        | some (E, L), some M => some (VE.Words.situation E L M)
        | _, _ => none
      else none,
    points := fun _ _ => [], ruleUnits := fun _ _ => [] }

/-- A decided plain row's certificate replays on `Γ`. -/
def plainCertReplays (p : PlainParts) (case : Json) (r : PlainRow) : Bool :=
  if r.lead == .yes || r.lead == .no then
    match plainCertPiece p case r with
    | some (ψ, k) => replayOk p.V p.Γ ψ k
    | none => false
  else true

/-- The answer of a replayed plain request: its context, the parts of its case and its view; refused when an unused
    unit has no display number, the decided row's certificate does not replay, or a line does not pass the gate. -/
def answerForPlain (s : PlainAsked) : Except String (Context × PlainParts × View) :=
  match contextOf s.text, plainParts s.case with
  | .ok ctx, .ok ⟨p, _⟩ =>
    let v := plainView s p (documentUnused s.text)
    if (v.unused.mapM ctx.displayOf).isSome then
      if plainCertReplays p s.case s.x.row then
        if linesGated (renderV ctx v) then .ok (ctx, p, v)
        else .error "CheckerUnavailable: a line of the answer does not pass the all-derivations gate"
      else .error "CheckerUnavailable: the decided answer's certificate does not replay"
    else .error "CheckerUnavailable: an unused sentence has no display number"
  | .error e, _ => .error e
  | _, .error e => .error e

theorem answerForPlain_ok {s : PlainAsked} {ctx : Context} {p : PlainParts} {v : View}
    (h : answerForPlain s = .ok (ctx, p, v)) :
    contextOf s.text = .ok ctx ∧ v = plainView s p (documentUnused s.text) ∧
    (v.unused.mapM ctx.displayOf).isSome = true ∧ plainCertReplays p s.case s.x.row = true ∧
    linesGated (renderV ctx v) = true := by
  unfold answerForPlain at h
  split at h
  · rename_i ctx' p' _ hc _
    dsimp only at h
    split at h
    · rename_i hu
      split at h
      · rename_i hr
        split at h
        · rename_i hg
          cases h
          exact ⟨hc, rfl, hu, hr, hg⟩
        · cases h
      · cases h
    · cases h
  · cases h
  · cases h

/-- Every line of an accepted plain answer passes W7's all-derivations gate as its frame. -/
theorem answerForPlain_gated (s : PlainAsked) (ctx : Context) (p : PlainParts) (v : View)
    (h : answerForPlain s = .ok (ctx, p, v)) :
    ∀ l ∈ renderV ctx v, ∃ slots, VE.Question.frameReadings l.text = [(gateName l.frame, slots)] := by
  intro l hl
  obtain ⟨_, _, _, _, hg⟩ := answerForPlain_ok h
  simp only [linesGated, List.all_eq_true] at hg
  exact gated_some (hg l hl)

end VE.Ask
