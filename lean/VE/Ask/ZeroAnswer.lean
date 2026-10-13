import VE.Ask.ZeroWire
import VE.Ask.PlainAnswer

/-! The zero-set adapter's answer (docs/spec/question-answering-q2-progress.md, decision 1): one row, choice `[]`,
rendered by `VE.Ask.Lines` from its view. A yes or no row cites exactly the sources of the positions its replayed
certificate uses, in `premisesU`'s order (`zeroCites_spec`, through `sourced`); the situations are the checked
countermodel's, split's and conflict witness's; every shown line passes W7's gate (`answerForZero_gated`). -/

namespace VE.Ask
open Lean VE.Readings VE.NormDefaults VE.NormDefaults.Wire
open VE.Norms (envAt size)

/-- The asserted units with their sources. -/
def ZeroParts.assertions (p : ZeroParts) : List (Source × VE.Formula) := p.units.map fun u => (Source.unit u.1, u.2.2)

/-- Each premise of `premisesU U Γ` with its source. -/
def ZeroParts.sourced (p : ZeroParts) : List (Source × VE.Formula) := VE.Ask.sourced p.U p.assertions

def ZeroParts.premises (p : ZeroParts) : List VE.Formula := premisesU p.U p.Γ

theorem ZeroParts.sourced_premises (p : ZeroParts) : p.sourced.map (·.2) = p.premises := by
  rw [ZeroParts.sourced, VE.Ask.sourced_premises]
  simp [ZeroParts.assertions, ZeroParts.premises, Function.comp_def]

/-- The certificate a yes or no zero-set row rests on, with what it proves. -/
def zeroCertPiece (p : ZeroParts) (case : Json) (r : Row) : Option (VE.Formula × VE.Tableau.Certificate) :=
  match r.lead with
  | .yes => (zeroCert p p.conclusion (p.piece case "certificate")).map (p.ψ, ·)
  | .no => (zeroCert p (VE.NormDefaults.Wire.enc (.not p.ψ)) (p.piece case "negation")).map (.not p.ψ, ·)
  | _ => none

def zeroUsed (p : ZeroParts) (ψ : VE.Formula) (k : VE.Tableau.Certificate) : List Nat := usedPositions p.E p.premises ψ k

def zeroCites (p : ZeroParts) (case : Json) (r : Row) : List Source :=
  match zeroCertPiece p case r with
  | some (ψ, k) => cited (p.sourced.map (·.1)) (zeroUsed p ψ k)
  | none => []

theorem zeroCites_spec (p : ZeroParts) (case : Json) (r : Row) (ψ : VE.Formula) (k : VE.Tableau.Certificate)
    (h : zeroCertPiece p case r = some (ψ, k)) :
    (∀ s, s ∈ zeroCites p case r ↔ ∃ i ∈ zeroUsed p ψ k, (p.sourced[i]?).map (·.1) = some s) ∧
    (∀ (i : Nat) (s : Source) (f : VE.Formula), p.sourced[i]? = some (s, f) → p.premises[i]? = some f) ∧
    (replayOk p.E p.premises ψ k = true → VE.Entails.{0} p.E ((zeroUsed p ψ k).filterMap (p.premises[·]?)) ψ) := by
  refine ⟨fun s => ?_, fun i s f hi => ?_, fun hr => usedPositions_sufficient _ _ ψ k hr⟩
  · simp only [zeroCites, h, mem_cited, List.getElem?_map]
  · rw [← p.sourced_premises, List.getElem?_map, hi]
    rfl

/-- The units whose rules (the case's norm units) are on `pred`, in unit order. -/
def zeroRuleUnits (case : Json) (pred : String) : List String :=
  match (case.getObjValD "document").getObjValD "units" with
  | .arr us => us.toList.filterMap fun u =>
      if strOf? (((u.getObjValD "content").getObjValD "norm").getObjValD "predicate") == some pred then
        strOf? (u.getObjValD "id") else none
  | _ => []

/-- The point lines of a zero-set answer: S2p, one per point where the split's fillings differ; S3, one per gap the
    countermodel's failure depends on. -/
def zeroPoints (p : ZeroParts) (case : Json) (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon)
    (kind : String) : List String :=
  if kind == "S2p" then match zeroSplitModels p (p.piece case "split") with
    | some (m₁, m₂) => (differs p.U m₁ m₂).filterMap fun (q, vs) =>
        (VE.Words.pointClause E L m₁.M q vs).map fun clause => "The text does not say whether " ++ clause ++ "."
    | none => []
  else if kind == "S3" then match zeroModel p (p.piece case "countermodel") with
    | some m => (VE.Readings.Wire.gapsOf p.U (m.M.withFill m.F) [] (VE.Norms.subst (fill p.U).T (size (fill p.U)) p.ψ)).filterMap
        fun (q, ids, _) => (VE.Words.pointClause E L m.M q (gapTuple p.U q ids)).map (VE.Words.fillingSentence · false)
    | none => []
  else []

/-- The view of a zero-set answer. -/
def zeroView (s : ZeroAsked) (p : ZeroParts) (unused : List String) : View :=
  let words := (englishOf s.text (s.request.getObjValD "lexicon")).toOption
  { asked := s.c, ids := [], rows := [s.x.row], cites := fun _ => zeroCites p s.case s.x.row, names := [],
    unused := unused, words := words, setUnit := fun _ => none,
    situation := fun frame _ => match words with
      | some (E, L) =>
        if frame == "S1" then (zeroModel p (p.piece s.case "countermodel")).map fun m => VE.Words.situation E L m.M
        else if frame == "S2" then (zeroSplitModels p (p.piece s.case "split")).map fun (m, _) =>
          VE.Words.situation E L m.M
        else if frame == "X1" then (zeroWitness p s.case).map fun w => VE.Words.situation E L w.M
        else none
      | none => none,
    points := fun kind _ => match words with
      | some (E, L) => zeroPoints p s.case E L kind
      | none => [],
    ruleUnits := fun _ pred => zeroRuleUnits s.case pred,
    gaps := fun _ => match zeroModel p (p.piece s.case "countermodel") with
      | some m => VE.Readings.Wire.gapsOf p.U (m.M.withFill m.F) [] (VE.Norms.subst (fill p.U).T (size (fill p.U)) p.ψ)
      | none => [] }

/-- A decided zero-set row's certificate replays on `premisesU U Γ`. -/
def zeroCertReplays (p : ZeroParts) (case : Json) (r : Row) : Bool :=
  if r.lead == .yes || r.lead == .no then
    match zeroCertPiece p case r with
    | some (ψ, k) => replayOk p.E p.premises ψ k
    | none => false
  else true

def answerForZero (s : ZeroAsked) : Except String (Context × ZeroParts × View) :=
  match contextOf s.text, zeroParts s.case with
  | .ok ctx, .ok ⟨p, _⟩ =>
    let v := zeroView s p (documentUnused s.text)
    if (v.unused.mapM ctx.displayOf).isSome then
      if zeroCertReplays p s.case s.x.row then
        if linesGated (renderV ctx v) then .ok (ctx, p, v)
        else .error s!"CheckerUnavailable: the answer's {firstUngated (renderV ctx v)} line does not pass the all-derivations gate"
      else .error "CheckerUnavailable: the decided answer's certificate does not replay"
    else .error "CheckerUnavailable: an unused sentence has no display number"
  | .error e, _ => .error e
  | _, .error e => .error e

theorem answerForZero_ok {s : ZeroAsked} {ctx : Context} {p : ZeroParts} {v : View}
    (h : answerForZero s = .ok (ctx, p, v)) :
    contextOf s.text = .ok ctx ∧ v = zeroView s p (documentUnused s.text) ∧
    (v.unused.mapM ctx.displayOf).isSome = true ∧ zeroCertReplays p s.case s.x.row = true ∧
    linesGated (renderV ctx v) = true := by
  unfold answerForZero at h
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

theorem answerForZero_gated (s : ZeroAsked) (ctx : Context) (p : ZeroParts) (v : View)
    (h : answerForZero s = .ok (ctx, p, v)) :
    ∀ l ∈ renderV ctx v, ∃ slots, VE.Question.frameReadings l.text = [(gateName l.frame, slots)] := by
  intro l hl
  obtain ⟨_, _, _, _, hg⟩ := answerForZero_ok h
  simp only [linesGated, List.all_eq_true] at hg
  exact gated_some (hg l hl)

end VE.Ask
