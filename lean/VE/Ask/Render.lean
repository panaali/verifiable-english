import VE.Ask.Wire
import VE.Words.Situation
import VE.Question.Frames

/-! The answer's text, rendered by Lean from Lean's answer (docs/spec/question-answering.md 3.3, 5.2; plan 4.3, 4.4,
4.6, D6, D9, D11, D14, R7, R8, Q2.3).

Each line is built as metadata (its frame, the source it cites, the quote, the readings it names, the row whose
checked evidence it shows, the unchecked mark), and its text is `lineText` of that metadata, the one owner of every
line's words (`render_text_matches_metadata`). The answer: A0; then one block per group (R7), whose first line is the
lead (A1 to A5, or an R1 line naming the group's readings when there are two or more groups); then the group's
reasons: one citation line per cited source for yes and no (C1 to C4), the countermodel (S1, then S3 per gap) for
not necessarily, the split (S2, then S2p per differing point) for not settled, the reasons (X1 to X6) for unknown;
R2 after the only block of a decided answer over open sets; one U1 after every block when the document has unused
sentences. The citations are exactly the sources of the positions the accepted certificate uses
(`checkedCites_spec`), and every line is shown only when W7's all-derivations gate reads it as its frame, once
(`answerFor_gated`). -/

namespace VE.Ask
open Lean VE.Readings VE.Readings.Wire VE.NormDefaults

/-! ## The sources of a choice's assertions -/

/-- The choice's assertions with the unit each comes from, by the fold `choiceDoc` makes (`build`). -/
def sourcedAssertions (D : Doc) (c : Choice) : List (Source × VE.Formula) :=
  D.items.foldl (fun acc it => match it with
    | .fixed u c' _ => acc ++ (asserted c').map (fun f => (Source.unit u, f))
    | .bar _ _ => acc
    | .set R => match ((c.index R.id).bind (R.candidates[·]?)).bind (fun a => a.content.map (fun c => (c, a.cites))) with
      | some (c', _) => acc ++ (asserted c').map (fun f => (Source.unit R.unit, f))
      | none => acc) []

theorem sourcedAssertions_formulas (D : Doc) (c : Choice) :
    (sourcedAssertions D c).map (·.2) = (choiceDoc D c).2 := by
  unfold sourcedAssertions choiceDoc build
  suffices h : ∀ (items : List Item) (acc : List (Source × VE.Formula)) (acc' : VE.Rights.RightsDoc × List VE.Formula),
      acc.map (·.2) = acc'.2 →
      (items.foldl (fun acc it => match it with
        | .fixed u c' _ => acc ++ (asserted c').map (fun f => (Source.unit u, f))
        | .bar _ _ => acc
        | .set R => match ((c.index R.id).bind (R.candidates[·]?)).bind
            (fun a => a.content.map (fun c => (c, a.cites))) with
          | some (c', _) => acc ++ (asserted c').map (fun f => (Source.unit R.unit, f))
          | none => acc) acc).map (·.2) =
      (items.foldl (fun acc it => match it with
        | .fixed u c cs => if (fun _ => true) u then (place acc.1 c cs, acc.2 ++ asserted c) else acc
        | .bar u b => if (fun _ => true) u then ({ acc.1 with bars := acc.1.bars ++ [b] }, acc.2) else acc
        | .set R => match ((fun R => (c.index R.id).bind (R.candidates[·]?)) R).bind
            (fun a => a.content.map (fun c => (c, a.cites))) with
          | some (c, cs) => (place acc.1 c cs, acc.2 ++ asserted c)
          | none => acc) acc').2 from h D.items [] (D.frame, []) rfl
  intro items
  induction items with
  | nil => intro acc acc' h; exact h
  | cons it rest ih =>
    intro acc acc' h
    simp only [List.foldl_cons]
    apply ih
    cases it with
    | fixed u c' cs => simp [h, List.map_map, Function.comp_def]
    | bar u b => simpa using h
    | set R =>
      dsimp only
      split
      · rename_i c' cs' hp
        rw [hp]
        simp [h, List.map_map, Function.comp_def]
      · rename_i hp
        rw [hp]
        exact h

/-! ## Citations: the certificate's used positions, by source -/

/-- The accepted certificate a yes or no row rests on, with what it proves: the query's certificate bound as RD-3
    binds it (`ndBoundCert`, the case's own premises and conclusion), or the negation certificate (`negCert`). -/
def certPiece (x : NDVerdicts) (case : Json) (r : Row) : Option (VE.Formula × VE.Tableau.Certificate) :=
  let entry := VE.Readings.Run.entryFor (VE.Readings.Run.evidenceList case) r.choice
  match r.lead with
  | .yes => (pieceOf entry "certificate").bind fun p =>
      ((ndBoundCert x.r r.choice [] (case.getObjValD "conclusion") (p.getObjValD "certificate")).toOption).map (x.φ, ·)
  | .no => (negCert x.r r.choice x.φ entry).map (.not x.φ, ·)
  | _ => none

/-- A row's premises (`premisesU` of its choice's filled document and assertions) and their sources. -/
def rowSourced (x : NDVerdicts) (r : Row) : List (Source × VE.Formula) :=
  sourced (choiceU x.r.N r.choice) (sourcedAssertions x.r.N.D r.choice)

def rowPremises (x : NDVerdicts) (r : Row) : List VE.Formula :=
  VE.NormDefaults.Wire.premisesU (choiceU x.r.N r.choice) (choiceDoc x.r.N.D r.choice).2

theorem rowSourced_premises (x : NDVerdicts) (r : Row) : (rowSourced x r).map (·.2) = rowPremises x r := by
  rw [rowSourced, sourced_premises, sourcedAssertions_formulas]
  rfl

/-- The positions the row's certificate uses. -/
def rowUsed (x : NDVerdicts) (r : Row) (ψ : VE.Formula) (k : VE.Tableau.Certificate) : List Nat :=
  usedPositions (fullEnv x.r.N r.choice) (rowPremises x r) ψ k

/-- The sources a yes or no row cites: exactly the sources of the positions its certificate uses; none otherwise. -/
def checkedCites (j : Json) (x : NDVerdicts) (r : Row) : List Source :=
  match certPiece x (j.getObjValD "case") r with
  | some (ψ, k) => cited ((rowSourced x r).map (·.1)) (rowUsed x r ψ k)
  | none => []

/-- Citation exactness. For a yes or no row with certificate `k` for `ψ` (the asked formula or its negation): a
    source is cited exactly when it is the source of a position `k` uses; the premise at that position is the
    premise the source names (positions pair each premise with its source, in `premisesU`'s order); and when `k`
    replays, the used premises alone entail `ψ`. -/
theorem checkedCites_spec (j : Json) (x : NDVerdicts) (r : Row) (ψ : VE.Formula) (k : VE.Tableau.Certificate)
    (h : certPiece x (j.getObjValD "case") r = some (ψ, k)) :
    (∀ s, s ∈ checkedCites j x r ↔ ∃ i ∈ rowUsed x r ψ k, ((rowSourced x r)[i]?).map (·.1) = some s) ∧
    (∀ (i : Nat) (s : Source) (f : VE.Formula), (rowSourced x r)[i]? = some (s, f) → (rowPremises x r)[i]? = some f) ∧
    (replayOk (fullEnv x.r.N r.choice) (rowPremises x r) ψ k = true →
      VE.Entails.{0} (fullEnv x.r.N r.choice) ((rowUsed x r ψ k).filterMap ((rowPremises x r)[·]?)) ψ) := by
  refine ⟨fun s => ?_, fun i s f hi => ?_, fun hr => usedPositions_sufficient _ _ ψ k hr⟩
  · simp only [checkedCites, h, mem_cited, List.getElem?_map]
  · rw [← rowSourced_premises, List.getElem?_map, hi]
    rfl

/-! ## The document's own text -/

structure Context where
  text : String
  units : List (String × Nat × Nat)
  textOf : String → Option String
  displayOf : String → Option Nat

/-- The bytes `[a, b)` of the source, when they are whole characters. -/
def bytesOf (source : String) (a b : Nat) : Option String :=
  String.fromUTF8? (source.toUTF8.extract a b)

/-- Each front-matter unit's id and span; its text, the document's own bytes in its span (a fenced unit's: its
    fence's sentence), without leading or trailing white space; its display number, its position from 1. -/
def contextOf (text : String) : Except String Context := do
  let sp ← VE.Service.Document.split text
  let us ← match sp.front.getObjValD "units" with
    | .arr us => pure us.toList
    | _ => throw "InvalidInput: the document has no units"
  let units ← us.mapM fun u => do
    let id ← VE.Bridge.stringField u "id"
    let (a, b) ← VE.Discourse.Loader.spanOf (u.getObjValD "span")
    pure (id, a, b)
  let texts := units.filterMap fun (id, a, b) =>
    (match sp.fences.lookup id with
     | some f => some f
     | none => bytesOf sp.source a b).map fun (t : String) => (id, t.trim)
  let ids := units.map (·.1)
  pure { text, units, textOf := fun u => texts.lookup u, displayOf := fun u => (ids.idxOf? u).map (· + 1) }

/-- A unit set aside for having no formal content: meaning `unformalised`, a reading set none of whose readings has
    content, or no content outside a reading set and not a heading (`meta`), which W2 stores as LABELLED. -/
def unusedUnit (front u : Json) : Bool :=
  let id := u.getObjValD "id"
  let content := u.getObjValD "content"
  let sets := match front.getObjValD "reading_sets" with
    | .arr rs => rs.toList.filter fun (R : Json) => strOf? (R.getObjValD "unit") == strOf? id
    | _ => []
  if (u.getObjValD "meaning").getObjVal? "unformalised" |>.toOption |>.isSome then true
  else if !sets.isEmpty then sets.all fun R => match R.getObjValD "readings" with
    | .arr cs => cs.all fun c => match c.getObjValD "content" with | .null => true | _ => false
    | _ => true
  else match content with
    | .null => strOf? (u.getObjValD "kind") != some "meta"
    | _ => false

/-- The ids of the unused units, in document order. -/
def documentUnused (text : String) : List String :=
  match VE.Service.Document.split text with
  | .ok sp => match sp.front.getObjValD "units" with
    | .arr us => us.toList.filterMap fun u => if unusedUnit sp.front u then strOf? (u.getObjValD "id") else none
    | _ => []
  | .error _ => []

/-- `sentence 3`, `sentences 3 and 5`, `sentences 3, 5 and 6`. -/
def citationText : List Nat → String
  | [] => "no sentence"
  | [n] => s!"sentence {n}"
  | ns => "sentences " ++ ", ".intercalate ((ns.dropLast).map toString) ++ " and " ++ toString (ns.getLastD 0)

/-! ## Lines and the answer -/

structure Line where
  frame : String
  text : String
  source : Option Source := none
  quote : Option (String × String) := none
  readings : List (String × Nat) := []
  witness : Option Choice := none   -- S1, S2 and X1: the checked row choice, not printed as an id
  unchecked : Bool := false       -- the line carries "(VE has not checked this wording)"
  deriving Repr, Inhabited

structure Answer where
  request : Json
  text : String
  case : Json
  x : VE.Readings.Wire.NDVerdicts
  asked : VE.Question.Candidate
  ids : List String
  rows : List Row
  cites : Row → List Source
  names : List Name
  unused : List String

def Answer.key (a : Answer) (r : Row) : Lead × List Source :=
  (r.lead, if r.lead == .yes || r.lead == .no then a.cites r else [])
def Answer.groups (a : Answer) : List Group := VE.Ask.groups a.ids a.rows a.key

def named (on : List (String × Option Nat)) : List (String × Nat) := on.filterMap fun (s, i) => i.map (s, ·)

def leadKey : Lead → String
  | .yes => "yes" | .no => "no" | .notSettled => "notSettled" | .notNecessarily => "notNecessarily"
  | .unknown => "unknown"

def leadFrame : Lead → String
  | .yes => "A1" | .no => "A2" | .notSettled => "A3" | .notNecessarily => "A4" | .unknown => "A5"

def leadText : Lead → String
  | .yes => "Yes."
  | .no => "No. The document rules this out."
  | .notSettled => "The text does not settle this."
  | .notNecessarily => "Not necessarily."
  | .unknown => "VE could not decide this."

def leadPhrase : Lead → String
  | .yes => "yes"
  | .no => "no: the document rules this out"
  | .notSettled => "the text does not settle this"
  | .notNecessarily => "not necessarily"
  | .unknown => "VE could not decide this"

def leads : List Lead := [.yes, .no, .notSettled, .notNecessarily, .unknown]

/-- The lead a block's first line states: by its frame. -/
def leadOfLine : Option Line → Option Lead
  | some l => leads.find? fun d => l.frame == leadFrame d || l.frame == "R1:" ++ leadKey d
  | none => none

def reasonFrame : Reason → String
  | .conflict => "X1" | .conflictUnchecked => "X2" | .inconsistent => "X3" | .noResult => "X4" | .tooMany => "X5"
  | .unchecked => "X6"

def reasonText : Reason → String
  | .conflictUnchecked => "VE could not check that the rules never contradict each other."
  | .inconsistent => "The sentences of this document cannot all be true together, so VE does not answer questions about it."
  | .noResult => "VE found neither a proof nor a situation where it fails, within its limits."
  | .tooMany => "There are more than 64 ways to read this document's open sentences. VE did not check them all."
  | .unchecked => "VE found a proof but could not check that the document's sentences can all be true together, so it does not answer."
  | .conflict => ""

def askedLine (s : String) : Line := { frame := "A0", text := "You asked whether " ++ s.dropRight 1 ++ "." }

/-- The frame a line is gated as: its frame name before any `:`. -/
def gateName (f : String) : String := (f.splitOn ":").headD f

/-! ### What a line's text reads -/

/-- The English environment and lexicon of the answer's request. -/
def wordsOf (a : Answer) : Option (VE.EnglishGrammar.Env × VE.EnglishGrammar.Lexicon) :=
  (englishOf a.text (a.request.getObjValD "lexicon")).toOption

/-- The unit of an open set. -/
def setUnit (a : Answer) (s : String) : Option String := (a.x.r.N.D.sets.find? (·.id == s)).map (·.unit)

/-- `sentence <n> means "<reading>"`, with the mark of an unchecked wording. -/
def readingClause (ctx : Context) (a : Answer) (p : String × Nat) : Option String := do
  let n ← ctx.displayOf (← setUnit a p.1)
  let nm ← a.names.find? fun n => n.set == p.1 && n.index == p.2
  pure (s!"sentence {n} means \"{nm.text}\"" ++ if nm.checked then "" else " (VE has not checked this wording)")

/-- `reading sentence <n> as "<reading>" and sentence <m> as "<reading>"`. -/
def readingSuffix (ctx : Context) (a : Answer) (ps : List (String × Nat)) : Option String := do
  if ps.isEmpty then return ""
  let parts ← ps.mapM fun p => do
    let n ← ctx.displayOf (← setUnit a p.1)
    let nm ← a.names.find? fun n => n.set == p.1 && n.index == p.2
    pure (s!"sentence {n} as \"{nm.text}\"" ++ if nm.checked then "" else " (VE has not checked this wording)")
  pure (", reading " ++ " and ".intercalate parts)

/-- The checked evidence of a row's choice: its evidence entry in the case. -/
def entryOf (a : Answer) (c : Choice) : Json :=
  VE.Readings.Run.entryFor (VE.Readings.Run.evidenceList a.case) c

/-- The row of a choice. -/
def rowAt (a : Answer) (c : Choice) : Option Row := a.rows.find? (·.choice == c)

/-- The checked countermodel of a choice (`countermodel`), decoded on its layered source. -/
def counterOf (a : Answer) (c : Choice) : Option (FilledModel (choiceU a.x.r.N c)) := do
  let e ← (a.x.evs.find? (·.1 == c))
  if h : e.1 = c then
    let hw : WellFormedU (choiceU a.x.r.N c) = true := h ▸ e.2.wfc
    let L ← (choiceLayered a.x.r c hw).toOption
    let p ← pieceOf (entryOf a c) "countermodel"
    (ndFilled a.x.r c L p).toOption
  else none

/-- The checked split of a choice. -/
def splitOf (a : Answer) (c : Choice) : Option (FilledModel (choiceU a.x.r.N c) × FilledModel (choiceU a.x.r.N c)) := do
  let e ← (a.x.evs.find? (·.1 == c))
  if h : e.1 = c then
    let hw : WellFormedU (choiceU a.x.r.N c) = true := h ▸ e.2.wfc
    let p ← pieceOf (entryOf a c) "split"
    splitModels a.x.r c hw p
  else none

/-- The checked conflict witness of a choice: its filled model. -/
def witnessOf (a : Answer) (c : Choice) : Option (VE.FiniteModel VE.Bridge.Entity) := do
  let e ← (a.x.evs.find? (·.1 == c))
  if h : e.1 = c then
    let hw : WellFormedU (choiceU a.x.r.N c) = true := h ▸ e.2.wfc
    let L ← (choiceLayered a.x.r c hw).toOption
    let w ← pieceOf (entryOf a c) "witness"
    match VE.NormDefaults.Wire.witnessConflictX L.1 (w.getObjValD "witness") with
    | .ok (_, _, (Mf, _, _)) => some Mf
    | .error _ => none
  else none

/-- The points where a split's two fillings differ: each unspecified predicate's tuples in one filling and not the
    other, in predicate order, rows sorted. -/
def differs (U : UDoc) (m₁ m₂ : FilledModel U) : List (String × List VE.Bridge.Entity) :=
  U.unspec.flatMap fun p =>
    let n := unsaidName p
    let rows := (m₁.F n).filter (fun v => !(m₂.F n).contains v) ++ (m₂.F n).filter (fun v => !(m₁.F n).contains v)
    rows.map (p, ·)

/-- The filled gaps a countermodel's failure depends on (RD-3's `gapsOf`). -/
def gapsOfCounter (a : Answer) (c : Choice) (m : FilledModel (choiceU a.x.r.N c)) : List (String × List String × Bool) :=
  gapsOf (choiceU a.x.r.N c) (m.M.withFill m.F) [] (VE.Norms.subst (fill (choiceU a.x.r.N c)).T
    (VE.Norms.size (fill (choiceU a.x.r.N c))) a.x.φ)

/-- The tuple of a gap, as entities of the predicate's sorts. -/
def gapTuple (U : UDoc) (p : String) (ids : List String) : List VE.Bridge.Entity := (sortsOf U.D p).zip ids

/-- The text of the `i`-th point line of a split (S2p) or gap line of a countermodel (S3) of choice `c`. -/
def pointText (a : Answer) (c : Choice) (kind : String) (i : Nat) : Option String := do
  let (_, L) ← wordsOf a
  if kind == "S2p" then
    let (m₁, m₂) ← splitOf a c
    let (p, vs) ← (differs _ m₁ m₂)[i]?
    let clause ← VE.Words.pointClause L m₁.M p vs
    pure ("The text does not say whether " ++ clause ++ ".")
  else
    let m ← counterOf a c
    let (p, ids, _) ← (gapsOfCounter a c m)[i]?
    let clause ← VE.Words.pointClause L m.M p (gapTuple (choiceU a.x.r.N c) p ids)
    pure (VE.Words.fillingSentence clause)

/-- The units whose rules (fixed, or of the chosen reading) are on `p`, in source order. -/
def ruleUnits (D : Doc) (c : Choice) (p : String) : List String :=
  D.items.filterMap fun it => match it with
    | .fixed u (.norm N) _ => if N.pred == p then some u else none
    | .set R => match (c.index R.id).bind (R.candidates[·]?) with
      | some ⟨_, some (.norm N), _, _⟩ => if N.pred == p then some R.unit else none
      | _ => none
    | _ => none

/-- A citation line's text: C1 quotes a unit; C2 names the rules on an act; C3 the word list; C4 the pair rule. -/
def citeText (ctx : Context) (a : Answer) (l : Line) : String :=
  match l.frame, l.quote, l.source with
  | "C1", some (u, t), _ => match ctx.displayOf u with
    | some n => s!"Sentence {n} says: \"{t}\""
    | none => ""
  | "C2", _, some (.rules p) =>
    match l.witness, wordsOf a with
    | some c, some (E, L) =>
      match (ruleUnits a.x.r.N.D c p).mapM ctx.displayOf, VE.Words.genericClause E L p with
      | some ns, some g => "Sentences " ++ (citationText ns).drop 10 ++ " say when " ++ g ++ "."
      | _, _ => ""
    | _, _ => ""
  | "C3", _, _ => "VE also used what the document's word list declares."
  | "C4", _, some (.pair r m) | "C4", _, some (.fill r m) => match wordsOf a with
    | some (E, L) => match VE.Words.pairSentence E L r m with
      | some t => "VE also used its rule that whatever must be done may be done: " ++ t
      | none => ""
    | none => ""
  | _, _, _ => ""

/-- The text of a line, from its metadata and the answer: the one owner of every line's words. -/
def lineText (ctx : Context) (a : Answer) (l : Line) : String :=
  match (l.frame.splitOn ":") with
  | ["A0"] => "You asked whether " ++ a.asked.sentence.dropRight 1 ++ "."
  | ["A1"] => leadText .yes
  | ["A2"] => leadText .no
  | ["A3"] => leadText .notSettled
  | ["A4"] => leadText .notNecessarily
  | ["A5"] => leadText .unknown
  | ["R1", k] => match leads.find? (leadKey · == k), l.readings.mapM (readingClause ctx a) with
    | some d, some cs => "If " ++ " and ".intercalate cs ++ ", " ++ leadPhrase d ++ "."
    | _, _ => ""
  | ["R2"] => "Every way of reading the document gives this answer."
  | ["S1"] => match l.witness, wordsOf a with
    | some c, some (E, L) => match counterOf a c, readingSuffix ctx a l.readings with
      | some m, some sfx => "Here is a situation the document allows where it fails: " ++
          VE.Words.situation E L m.M ++ sfx ++ "."
      | _, _ => ""
    | _, _ => ""
  | ["S2"] => match l.witness, wordsOf a with
    | some c, some (E, L) => match splitOf a c, readingSuffix ctx a l.readings with
      | some (m, _), some sfx => "Here is a situation where the answer depends on what the text leaves unsaid: " ++
          VE.Words.situation E L m.M ++ sfx ++ "."
      | _, _ => ""
    | _, _ => ""
  | [kind, i] => match l.witness, i.toNat? with
    | some c, some n => if kind == "S2p" || kind == "S3" then (pointText a c kind n).getD "" else ""
    | _, _ => ""
  | ["X1"] => match l.witness, wordsOf a with
    | some c, some (E, L) => match witnessOf a c, readingSuffix ctx a l.readings with
      | some M, some sfx => "The document's rules or defaults conflict in this situation, so VE cannot answer: " ++
          VE.Words.situation E L M ++ sfx ++ "."
      | _, _ => ""
    | _, _ => ""
  | ["X2"] => reasonText .conflictUnchecked
  | ["X3"] => reasonText .inconsistent
  | ["X4"] => reasonText .noResult
  | ["X5"] => reasonText .tooMany
  | ["X6"] => reasonText .unchecked
  | ["U1"] => match a.unused.mapM ctx.displayOf with
    | some ds => s!"VE did not use {a.unused.length} sentences of this document that it could not read formally: " ++
        citationText ds ++ "."
    | none => ""
  | _ => citeText ctx a l

/-- A line made from its metadata: its text is `lineText` of it. -/
def mk (ctx : Context) (a : Answer) (l : Line) : Line := { l with text := lineText ctx a l }

theorem lineText_text (ctx : Context) (a : Answer) (l : Line) (t : String) :
    lineText ctx a { l with text := t } = lineText ctx a l := rfl

theorem mk_text (ctx : Context) (a : Answer) (l : Line) : (mk ctx a l).text = lineText ctx a (mk ctx a l) := rfl

/-- Whether a reading's wording is unchecked. -/
def uncheckedIn (a : Answer) (ps : List (String × Nat)) : Bool :=
  ps.any fun p => a.names.any fun n => !n.checked && (n.set, n.index) == p

/-- The line citing one source, under the choice `c` (the group's first row). -/
def citeLine (ctx : Context) (a : Answer) (c : Choice) (s : Source) : Line :=
  mk ctx a <| match s with
  | .unit u => { frame := "C1", text := "", source := some s,
                 quote := (ctx.textOf u).map (u, ·) }
  | .rules p => match ruleUnits a.x.r.N.D c p with
    | [] => { frame := "C3", text := "", source := some s }
    | [u] => { frame := "C1", text := "", source := some s, quote := (ctx.textOf u).map (u, ·) }
    | _ => { frame := "C2", text := "", source := some s, witness := some c }
  | .definition _ | .background => { frame := "C3", text := "", source := some s }
  | .pair _ _ | .fill _ _ => { frame := "C4", text := "", source := some s }

/-- A situation line (S1, S2, X1) of a row: its choice and every open set's reading. -/
def situationLine (ctx : Context) (a : Answer) (frame : String) (r : Row) : Line :=
  let rs := named (assignment a.ids r)
  mk ctx a { frame := frame, text := "", readings := rs, witness := some r.choice, unchecked := uncheckedIn a rs }

/-- The point lines (S2p or S3) after a situation line of a row. -/
def pointLines (ctx : Context) (a : Answer) (kind : String) (r : Row) (count : Nat) : List Line :=
  (List.range count).map fun i => mk ctx a { frame := kind ++ ":" ++ toString i, text := "", witness := some r.choice }

/-- The reason lines of an unknown group: each distinct reason of its rows, in order; X1 with the first conflict
    row's witness. -/
def reasonLines (ctx : Context) (a : Answer) (g : Group) : List Line :=
  let reasons := (g.rows.filterMap (·.reason)).eraseDups
  reasons.flatMap fun x => match x with
    | .conflict => match g.rows.find? (·.conflict == .conflict) with
      | some r => [situationLine ctx a "X1" r]
      | none => []
    | x => [mk ctx a { frame := reasonFrame x, text := "" }]

/-- The lines after a group's lead: its citations, its situation, or its reasons. -/
def groupReasons (ctx : Context) (a : Answer) (g : Group) : List Line :=
  match g.lead with
  | .yes | .no => g.cited.map (citeLine ctx a ((g.rows.head?.map (·.choice)).getD []))
  | .notNecessarily => match g.rows.find? (·.query == .refuted) with
    | some r => situationLine ctx a "S1" r :: pointLines ctx a "S3" r
        (((counterOf a r.choice).map (fun m => (gapsOfCounter a r.choice m).length)).getD 0)
    | none => []
  | .notSettled => match g.rows.find? (·.split == true) with
    | some r => situationLine ctx a "S2" r :: pointLines ctx a "S2p" r
        (((splitOf a r.choice).map (fun (m₁, m₂) => (differs _ m₁ m₂).length)).getD 0)
    | none => []
  | .unknown => reasonLines ctx a g

/-- One group's block: its lead (A1 to A5 when it is the only group, else an R1 line naming its readings of the
    relevant sets), its reasons, and R2 after the only block of a decided answer over open sets. -/
def renderGroup (ctx : Context) (a : Answer) (g : Group) : List Line :=
  if a.groups.length < 2 then
    mk ctx a { frame := leadFrame g.lead, text := "" } :: groupReasons ctx a g ++
      (if !a.ids.isEmpty && g.lead != .unknown then [mk ctx a { frame := "R2", text := "" }] else [])
  else
    let rs := named g.on
    mk ctx a { frame := "R1:" ++ leadKey g.lead, text := "", readings := rs, unchecked := uncheckedIn a rs } ::
      groupReasons ctx a g

/-- U1, after every block, when the document has unused sentences whose display numbers are known. -/
def unusedLines (ctx : Context) (a : Answer) : List Line :=
  if a.unused.isEmpty then [] else match a.unused.mapM ctx.displayOf with
    | some _ => [mk ctx a { frame := "U1", text := "" }]
    | none => []

def render (ctx : Context) (a : Answer) : List Line :=
  askedLine a.asked.sentence :: (a.groups.flatMap (renderGroup ctx a) ++ unusedLines ctx a)

/-! ## The render theorems -/

/-- What the shown witness of an S1, S2 or X1 line is: the row's accepted countermodel, split or conflict witness
    (each a row result Lean computed from this request's evidence). -/
def checkedWitness (_j : Json) (_x : VE.Readings.Wire.NDVerdicts) (r : Row) (frame : String) : Prop :=
  (frame = "S1" ∧ r.query = .refuted) ∨ (frame = "S2" ∧ r.split = true) ∨ (frame = "X1" ∧ r.conflict = .conflict)

/-- Only replayed evidence and the document's own split may supply render inputs. `contextOf` extracts each
    `textOf` value from `split.source` at the front-matter unit span (or from its named fence), trimmed as the
    document loader trims it; `displayOf` is that unit's display position. Every unused unit must have one. -/
def RenderInputBound (ctx : Context) (a : Answer) : Prop :=
  contextOf a.text = .ok ctx ∧
  a.request.getObjValD "case" = a.case ∧
  VE.Readings.Run.replayVerdictsND a.case = .ok a.x ∧
  a.rows.map (·.choice) = a.x.evs.map (·.1) ∧
  (∀ r ∈ a.rows, a.cites r = checkedCites a.request a.x r) ∧
  a.unused = documentUnused a.text ∧
  ∃ displays, a.unused.mapM ctx.displayOf = some displays

theorem mem_render {ctx : Context} {a : Answer} {l : Line} (h : l ∈ render ctx a) :
    l = askedLine a.asked.sentence ∨ (∃ g ∈ a.groups, l ∈ renderGroup ctx a g) ∨ l ∈ unusedLines ctx a := by
  simp only [render, List.mem_cons, List.mem_append, List.mem_flatMap] at h
  rcases h with h | h | h
  · exact Or.inl h
  · exact Or.inr (Or.inl h)
  · exact Or.inr (Or.inr h)

theorem citeLine_quote (ctx : Context) (a : Answer) (c : Choice) (s : Source) :
    ∀ u t, (citeLine ctx a c s).quote = some (u, t) → ctx.textOf u = some t := by
  intro u t h
  unfold citeLine mk at h
  cases s with
  | unit v =>
    simp only [Option.map_eq_some_iff, Prod.mk.injEq] at h
    obtain ⟨t', ht, rfl, rfl⟩ := h
    exact ht
  | rules p =>
    dsimp only at h
    split at h
    · simp at h
    · simp only [Option.map_eq_some_iff, Prod.mk.injEq] at h
      obtain ⟨t', ht, rfl, rfl⟩ := h
      exact ht
    · simp at h
  | definition _ => simp at h
  | background => simp at h
  | pair _ _ => simp at h
  | fill _ _ => simp at h

/-! ## The answer of a replayed request -/

/-- A decided row's certificate replays on the row's premises (`replayOk`). -/
def certReplays (a : Answer) (r : Row) : Bool :=
  if r.lead == .yes || r.lead == .no then
    match certPiece a.x a.case r with
    | some (ψ, k) => replayOk (fullEnv a.x.r.N r.choice) (rowPremises a.x r) ψ k
    | none => false
  else true

/-- Every line passes W7's all-derivations gate as its frame (`VE.Question.gated`). -/
def linesGated (ls : List Line) : Bool := ls.all fun l => (VE.Question.gated (gateName l.frame) l.text).isSome

/-- The answer of a replayed request: its context from the document, the rows' citations from their accepted
    certificates; refused when an unused unit has no display number, a decided row's certificate does not replay,
    or a line does not pass the gate. -/
def answerFor (s : Asked) : Except String (Context × Answer) :=
  match hc : contextOf s.text with
  | .error e => .error e
  | .ok ctx =>
    let a : Answer := ⟨s.request, s.text, s.case, s.x, s.c, s.x.r.N.D.sets.map (·.id), s.rows,
      checkedCites s.request s.x, s.names, documentUnused s.text⟩
    if (a.unused.mapM ctx.displayOf).isSome then
      if a.rows.all (certReplays a) then
        if linesGated (render ctx a) then .ok (ctx, a)
        else .error "CheckerUnavailable: a line of the answer does not pass the all-derivations gate"
      else .error "CheckerUnavailable: a decided reading's certificate does not replay"
    else .error "CheckerUnavailable: an unused sentence has no display number"

end VE.Ask
