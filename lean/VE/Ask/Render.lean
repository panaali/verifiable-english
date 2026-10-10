import VE.Ask.Lines

/-! The answer of the readings route, rendered by Lean from Lean's answer (docs/spec/question-answering.md 5.2; plan
4.3, 4.4, 4.6, Q2.3).

`Answer` is the approved record of a replayed readings case; `Answer.view` gives its `View`: the rows' citations, the
reading names, the unused units, and what each row's checked evidence shows (the countermodel's, the split's and the
conflict witness's situations, the split's differing points and the countermodel's filled gaps, the units of the
rules on an act under the row's choice). `render`, `renderGroup` and `lineText` are `VE.Ask.Lines`' on that view, and
the approved render statements follow from its lemmas. The citations are exactly the sources of the positions the
accepted certificate uses (`checkedCites_spec`, `answerFor_cites`), and every line is shown only when W7's
all-derivations gate reads it as its frame, once (`answerFor_gated`). -/

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

/-- The English environment and lexicon of the answer's request. -/
def wordsOf (a : Answer) : Option (VE.EnglishGrammar.Env × VE.EnglishGrammar.Lexicon) :=
  (englishOf a.text (a.request.getObjValD "lexicon")).toOption

/-- The unit of an open set. -/
def setUnit (a : Answer) (s : String) : Option String := (a.x.r.N.D.sets.find? (·.id == s)).map (·.unit)

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

/-- The point lines of a choice: S2p, one per point where its split's fillings differ; S3, one per filled gap its
    countermodel's failure depends on. -/
def pointsOf (a : Answer) (kind : String) (c : Choice) : List String :=
  match wordsOf a with
  | none => []
  | some (_, L) =>
    if kind == "S2p" then match splitOf a c with
      | some (m₁, m₂) => (differs _ m₁ m₂).filterMap fun (p, vs) =>
          (VE.Words.pointClause L m₁.M p vs).map fun clause => "The text does not say whether " ++ clause ++ "."
      | none => []
    else if kind == "S3" then match counterOf a c with
      | some m => (gapsOfCounter a c m).filterMap fun (p, ids, _) =>
          (VE.Words.pointClause L m.M p (gapTuple (choiceU a.x.r.N c) p ids)).map VE.Words.fillingSentence
      | none => []
    else []

/-- The situation an S1, S2 or X1 line shows of a choice's checked countermodel, split or conflict witness. -/
def situationOf (a : Answer) (frame : String) (c : Choice) : Option String := do
  let (E, L) ← wordsOf a
  if frame == "S1" then (counterOf a c).map fun m => VE.Words.situation E L m.M
  else if frame == "S2" then (splitOf a c).map fun (m, _) => VE.Words.situation E L m.M
  else if frame == "X1" then (witnessOf a c).map fun M => VE.Words.situation E L M
  else none

/-- The units whose rules (fixed, or of the chosen reading) are on `p`, in source order. -/
def ruleUnits (D : Doc) (c : Choice) (p : String) : List String :=
  D.items.filterMap fun it => match it with
    | .fixed u (.norm N) _ => if N.pred == p then some u else none
    | .set R => match (c.index R.id).bind (R.candidates[·]?) with
      | some ⟨_, some (.norm N), _, _⟩ => if N.pred == p then some R.unit else none
      | _ => none
    | _ => none

/-- The view of a readings answer the lines are rendered from. -/
def Answer.view (a : Answer) : View :=
  { asked := a.asked, ids := a.ids, rows := a.rows, cites := a.cites, names := a.names, unused := a.unused,
    words := wordsOf a, setUnit := setUnit a, situation := situationOf a, points := pointsOf a,
    ruleUnits := ruleUnits a.x.r.N.D,
    gaps := fun c => ((counterOf a c).map (gapsOfCounter a c)).getD [] }

theorem Answer.groups_view (a : Answer) : a.groups = a.view.groups := rfl

/-- The text of a line, from its metadata and the answer: the one owner of every line's words. -/
def lineText (ctx : Context) (a : Answer) (l : Line) : String := lineTextV ctx a.view l

def renderGroup (ctx : Context) (a : Answer) (g : Group) : List Line := renderGroupV ctx a.view g

def render (ctx : Context) (a : Answer) : List Line := renderV ctx a.view

/-! ## The render theorems (spec 5.2) -/

/-- What the shown witness of an S1, S2 or X1 line is: the row's accepted countermodel, split or conflict witness
    in this request (each a row result Lean computed from its evidence). -/
def checkedWitness (_j : Json) (_x : VE.Readings.Wire.NDVerdicts) (r : Row) (frame : String) : Prop :=
  checkedWitnessRow r frame

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

theorem render_quotes_bytes : ∀ (ctx : Context) (a : Answer), RenderInputBound ctx a →
    ∀ l ∈ render ctx a, ∀ u t, l.quote = some (u, t) → ctx.textOf u = some t :=
  fun ctx a _ => render_quotes_bytesV ctx a.view

theorem render_text_matches_metadata : ∀ (ctx : Context) (a : Answer), RenderInputBound ctx a →
    ∀ l ∈ render ctx a, l.text = lineText ctx a l :=
  fun ctx a _ => render_text_matches_metadataV ctx a.view

theorem render_asked : ∀ (ctx : Context) (a : Answer), (render ctx a).head? = some (askedLine a.asked.sentence) :=
  fun ctx a => render_askedV ctx a.view

theorem render_cites_exact : ∀ (ctx : Context) (a : Answer) (g : Group), RenderInputBound ctx a → g ∈ a.groups →
    (g.lead = .yes ∨ g.lead = .no) → (renderGroup ctx a g).filterMap (·.source) = g.cited :=
  fun ctx a g _ hg => render_cites_exactV ctx a.view g hg

theorem render_lead : ∀ (ctx : Context) (a : Answer) (g : Group), g ∈ a.groups →
    leadOfLine (renderGroup ctx a g).head? = some g.lead :=
  fun ctx a g hg => render_leadV ctx a.view g hg

/-- R7, with `groups_cover`: each row's one block names exactly its readings of the relevant sets. -/
theorem render_covers_rows : ∀ (ctx : Context) (a : Answer) (g : Group), g ∈ a.groups → 2 ≤ a.groups.length →
    ((renderGroup ctx a g).head?.map (·.readings)) = some (named g.on) :=
  fun ctx a g hg h2 => render_covers_rowsV ctx a.view g hg h2

/-- R8: an unchecked wording is marked in the line that shows it. -/
theorem render_marks_unchecked : ∀ (ctx : Context) (a : Answer), ∀ l ∈ render ctx a,
    (∃ n ∈ a.names, n.checked = false ∧ (n.set, n.index) ∈ l.readings) → l.unchecked = true :=
  fun ctx a => render_marks_uncheckedV ctx a.view

theorem render_model_names_choice : ∀ (ctx : Context) (a : Answer), RenderInputBound ctx a →
    ∀ l ∈ render ctx a, l.frame ∈ ["S1", "S2", "X1"] →
      ∃ r ∈ a.rows, l.witness = some r.choice ∧ checkedWitness a.request a.x r l.frame ∧
        l.readings = named (assignment a.ids r) :=
  fun ctx a _ => render_model_names_choiceV ctx a.view

/-- D14, R8: one U1 after all answer blocks, with the document-derived count and citation; none for an empty list. -/
theorem render_unused_once : ∀ (ctx : Context) (a : Answer), RenderInputBound ctx a →
    (a.unused = [] → ∀ l ∈ render ctx a, l.frame ≠ "U1") ∧
    (a.unused ≠ [] → ∃ pre u displays, render ctx a = pre ++ [u] ∧
      (∀ l ∈ pre, l.frame ≠ "U1") ∧ u.frame = "U1" ∧
      u.text = lineText ctx a u ∧ u.quote = none ∧ u.source = none ∧
      u.readings = [] ∧ u.witness = none ∧
      a.unused.mapM ctx.displayOf = some displays ∧
      u.text = s!"VE did not use {a.unused.length} sentences of this document that it could not read formally: " ++
        citationText displays ++ ".") := by
  intro ctx a hb
  obtain ⟨_, _, _, _, _, _, displays, hd⟩ := hb
  obtain ⟨h1, h2⟩ := render_unused_onceV ctx a.view displays hd
  refine ⟨h1, fun hne => ?_⟩
  obtain ⟨pre, u, h3, h4, h5, h6, h7, h8, h9, h10, h11⟩ := h2 hne
  exact ⟨pre, u, displays, h3, h4, h5, h6, h7, h8, h9, h10, hd, h11⟩

/-! ## The answer of a replayed request -/

/-- A decided row's certificate replays on the row's premises (`replayOk`). -/
def certReplays (a : Answer) (r : Row) : Bool :=
  if r.lead == .yes || r.lead == .no then
    match certPiece a.x a.case r with
    | some (ψ, k) => replayOk (fullEnv a.x.r.N r.choice) (rowPremises a.x r) ψ k
    | none => false
  else true

/-- The first reading a line names whose wording is empty (a reading the relay could not word), by its set. -/
def unworded (a : Answer) (ls : List Line) : Option String :=
  (ls.flatMap (·.readings)).findSome? fun (s, i) =>
    if (a.names.find? fun n => n.set == s && n.index == i).any (!·.text.isEmpty) then none else some s

/-- The frame of the first line that does not pass the gate (named in the refusal; its text is never shown). -/
def firstUngated (ls : List Line) : String :=
  ((ls.find? fun l => !(VE.Question.gated (gateName l.frame) l.text).isSome).map (gateName ·.frame)).getD ""

/-- Every line passes W7's all-derivations gate as its frame (`VE.Question.gated`). -/
def linesGated (ls : List Line) : Bool := ls.all fun l => (VE.Question.gated (gateName l.frame) l.text).isSome

/-- The answer of a replayed request: its context from the document, the rows' citations from their accepted
    certificates; refused when an unused unit has no display number, a decided row's certificate does not replay,
    or a line does not pass the gate. -/
def answerFor (s : Asked) : Except String (Context × Answer) :=
  match contextOf s.text with
  | .error e => .error e
  | .ok ctx =>
    let a : Answer := ⟨s.request, s.text, s.case, s.x, s.c, s.x.r.N.D.sets.map (·.id), s.rows,
      checkedCites s.request s.x, s.names, documentUnused s.text⟩
    if (a.unused.mapM ctx.displayOf).isSome then
      if a.rows.all (certReplays a) then
        match unworded a (render ctx a) with
        | some set => .error s!"CheckerUnavailable: VE could not check the wording of a reading of sentence {
            match (setUnit a set).bind ctx.displayOf with | some n => toString n | none => set}"
        | none =>
          if linesGated (render ctx a) then .ok (ctx, a)
          else .error s!"CheckerUnavailable: the answer's {firstUngated (render ctx a)} line does not pass the all-derivations gate"
      else .error "CheckerUnavailable: a decided reading's certificate does not replay"
    else .error "CheckerUnavailable: an unused sentence has no display number"

end VE.Ask

namespace VE.Ask
open Lean VE.Readings VE.Readings.Wire VE.NormDefaults

theorem answerFor_ok {s : Asked} {ctx : Context} {a : Answer} (h : answerFor s = .ok (ctx, a)) :
    contextOf s.text = .ok ctx ∧
    a = ⟨s.request, s.text, s.case, s.x, s.c, s.x.r.N.D.sets.map (·.id), s.rows, checkedCites s.request s.x, s.names,
      documentUnused s.text⟩ ∧
    (a.unused.mapM ctx.displayOf).isSome = true ∧ a.rows.all (certReplays a) = true ∧
    linesGated (render ctx a) = true := by
  unfold answerFor at h
  split at h
  · cases h
  · rename_i ctx' hc
    dsimp only at h
    split at h
    · rename_i hu
      split at h
      · rename_i hr
        split at h
        · cases h
        · split at h
          · rename_i hg
            cases h
            exact ⟨hc, rfl, hu, hr, hg⟩
          · cases h
      · cases h
    · cases h

theorem answerFor_bound : ∀ (asked : Asked) (ctx : Context) (a : Answer),
    answerFor asked = .ok (ctx, a) → RenderInputBound ctx a ∧
      a.request = asked.request ∧ a.text = asked.text ∧ a.case = asked.case ∧ a.x = asked.x ∧
      a.asked = asked.c ∧ a.rows = asked.rows ∧ a.names = asked.names := by
  intro s ctx a h
  obtain ⟨hc, rfl, hu, _, _⟩ := answerFor_ok h
  exact ⟨⟨hc, s.hrequest.2.2, s.hreplay, s.hrows, fun _ _ => rfl, rfl, Option.isSome_iff_exists.mp hu⟩,
    rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem gated_some {f line : String} (h : (VE.Question.gated f line).isSome = true) :
    ∃ slots, VE.Question.frameReadings line = [(f, slots)] := by
  unfold VE.Question.gated at h
  split at h
  · rename_i g slots hr
    split at h
    · rename_i he
      have : g = f := by simpa using he
      subst this
      exact ⟨slots, hr⟩
    · cases h
  · cases h

/-- Every line of an answer `answerFor` returns passes W7's all-derivations gate: over every registered frame
    (`VE.Question.answerFrames`), its text has exactly one derivation, and it is its own frame's. -/
theorem answerFor_gated : ∀ (asked : Asked) (ctx : Context) (a : Answer), answerFor asked = .ok (ctx, a) →
    ∀ l ∈ render ctx a, ∃ slots, VE.Question.frameReadings l.text = [(gateName l.frame, slots)] := by
  intro s ctx a h l hl
  obtain ⟨_, _, _, _, hg⟩ := answerFor_ok h
  simp only [linesGated, List.all_eq_true] at hg
  exact gated_some (hg l hl)

theorem certPiece_formula {x : NDVerdicts} {case : Json} {r : Row} {ψ : VE.Formula} {k : VE.Tableau.Certificate}
    (h : certPiece x case r = some (ψ, k)) : (r.lead = .yes ∧ ψ = x.φ) ∨ (r.lead = .no ∧ ψ = .not x.φ) := by
  unfold certPiece at h
  split at h
  · rename_i hl
    obtain ⟨p, _, hp⟩ := Option.bind_eq_some_iff.mp h
    obtain ⟨k', _, hk⟩ := Option.map_eq_some_iff.mp hp
    cases hk
    exact Or.inl ⟨hl, rfl⟩
  · rename_i hl
    obtain ⟨k', _, hk⟩ := Option.map_eq_some_iff.mp h
    cases hk
    exact Or.inr ⟨hl, rfl⟩
  · cases h

/-- The reasons of a yes or no row of an accepted answer are its certificate's premises: the row has an accepted
    certificate for the asked formula (yes) or its negation (no) that replays on the row's premises; its citations
    are exactly the sources of the positions the certificate uses (`checkedCites_spec`), and those premises alone
    entail what the lead says. -/
theorem answerFor_cites : ∀ (asked : Asked) (ctx : Context) (a : Answer), answerFor asked = .ok (ctx, a) →
    ∀ r ∈ a.rows, r.lead = .yes ∨ r.lead = .no → ∃ ψ k,
      certPiece a.x a.case r = some (ψ, k) ∧
      ((r.lead = .yes ∧ ψ = a.x.φ) ∨ (r.lead = .no ∧ ψ = .not a.x.φ)) ∧
      (∀ s, s ∈ a.cites r ↔ ∃ i ∈ rowUsed a.x r ψ k, ((rowSourced a.x r)[i]?).map (·.1) = some s) ∧
      VE.Entails.{0} (fullEnv a.x.r.N r.choice) ((rowUsed a.x r ψ k).filterMap ((rowPremises a.x r)[·]?)) ψ := by
  intro s ctx a h r hr hl
  obtain ⟨_, ha, _, hc, _⟩ := answerFor_ok h
  have hrep := List.all_eq_true.mp hc r hr
  have hcase : a.request.getObjValD "case" = a.case := by rw [ha]; exact s.hrequest.2.2
  unfold certReplays at hrep
  have hyn : (r.lead == .yes || r.lead == .no) = true := by rcases hl with h | h <;> simp [h]
  rw [if_pos hyn] at hrep
  split at hrep
  · rename_i ψ k hk
    have hk' : certPiece a.x (a.request.getObjValD "case") r = some (ψ, k) := by rw [hcase]; exact hk
    obtain ⟨hs, _, hent⟩ := checkedCites_spec a.request a.x r ψ k hk'
    refine ⟨ψ, k, hk, certPiece_formula hk, fun t => ?_, hent hrep⟩
    rw [ha] at hs ⊢
    exact hs t
  · cases hrep

end VE.Ask
