import VE.Ask.Wire
import VE.Words.Situation
import VE.Question.Frames

/-! The answer's lines, for every route (docs/spec/question-answering.md 3.3, 5.2; plan 4.4, 4.6, D6, D9, D11, D14,
R7, R8, Q2.3).

A route gives a `View` of its answer: the asked candidate, the open sets, one `Row` per compatible choice, each row's
citations, the reading names, the unused units, the English environment and lexicon, and what its checked evidence
shows (a situation of an S1, S2 or X1 line, the point lines of a split or a countermodel, the units of the rules on
an act). Each line is built as metadata (its frame, the source it cites, the quote, the readings it names, the row
whose checked evidence it shows, the unchecked mark), and its text is `lineTextV` of that metadata, the one owner of
every line's words. The answer: A0; then one block per group (R7), whose first line is the lead (A1 to A5, or an R1
line naming the group's readings when there are two or more groups); then the group's reasons: one citation line per
cited source for yes and no (C1 to C4), the countermodel (S1, then S3 per gap) for not necessarily, the split (S2,
then S2p per differing point) for not settled, the reasons (X1 to X6) for unknown; R2 after the only block of a
decided answer over open sets; one U1 after every block when the document has unused sentences. `VE.Ask.Render`
proves the approved render statements for the readings route from the lemmas here. -/

namespace VE.Ask
open Lean VE.Readings

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

structure View where
  asked : VE.Question.Candidate
  ids : List String
  rows : List Row
  cites : Row → List Source
  names : List Name
  unused : List String
  words : Option (VE.EnglishGrammar.Env × VE.EnglishGrammar.Lexicon)
  setUnit : String → Option String
  /-- The situation an S1, S2 or X1 line shows of a choice's checked evidence. -/
  situation : String → Choice → Option String
  /-- The point lines (S2p, S3) after a choice's split or countermodel. -/
  points : String → Choice → List String
  /-- The units whose rules on an act a choice's document holds, in source order. -/
  ruleUnits : Choice → String → List String
  /-- The filled gaps a choice's checked countermodel's failure depends on (RD-3's `gapsOf`): predicate, tuple,
      the filling's value. -/
  gaps : Choice → List (String × List String × Bool) := fun _ => []

def View.key (v : View) (r : Row) : Lead × List Source :=
  (r.lead, if r.lead == .yes || r.lead == .no then v.cites r else [])
def View.groups (v : View) : List Group := VE.Ask.groups v.ids v.rows v.key

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

/-- `sentence <n> means "<reading>"`, with the mark of an unchecked wording. -/
def readingClause (ctx : Context) (v : View) (p : String × Nat) : Option String := do
  let n ← ctx.displayOf (← v.setUnit p.1)
  let nm ← v.names.find? fun n => n.set == p.1 && n.index == p.2
  pure (s!"sentence {n} means \"{nm.text}\"" ++ if nm.checked then "" else " (VE has not checked this wording)")

/-- `reading sentence <n> as "<reading>" and sentence <m> as "<reading>"`. -/
def readingSuffix (ctx : Context) (v : View) (ps : List (String × Nat)) : Option String := do
  if ps.isEmpty then return ""
  let parts ← ps.mapM fun p => do
    let n ← ctx.displayOf (← v.setUnit p.1)
    let nm ← v.names.find? fun n => n.set == p.1 && n.index == p.2
    pure (s!"sentence {n} as \"{nm.text}\"" ++ if nm.checked then "" else " (VE has not checked this wording)")
  pure (", reading " ++ " and ".intercalate parts)

/-- A citation line's text: C1 quotes a unit; C2 names the rules on an act; C3 the word list; C4 the pair rule. -/
def citeText (ctx : Context) (v : View) (l : Line) : String :=
  match l.frame, l.quote, l.source with
  | "C1", some (u, t), _ => match ctx.displayOf u with
    | some n => s!"Sentence {n} says: \"{t}\""
    | none => ""
  | "C2", _, some (.rules p) =>
    match l.witness, v.words with
    | some c, some (E, L) =>
      match (v.ruleUnits c p).mapM ctx.displayOf, VE.Words.genericClause E L p with
      | some ns, some g => "Sentences " ++ (citationText ns).drop 10 ++ " say when " ++ g ++ "."
      | _, _ => ""
    | _, _ => ""
  | "C3", _, _ => "VE also used what the document's word list declares."
  | "C4", _, some (.pair r m) | "C4", _, some (.fill r m) => match v.words with
    | some (E, L) => match VE.Words.pairSentence E L r with
      | some t => "VE also used its rule that whatever must be done may be done: " ++ t
      | none => ""
    | none => ""
  | _, _, _ => ""

/-- The text of a parameterised frame: `R1:<lead>` names its readings and its lead phrase; `S2p:<i>` and `S3:<i>`
    are the `i`-th point line of the witness row's split or countermodel. -/
def paramText (ctx : Context) (v : View) (l : Line) : String :=
  match l.frame.toList with
  | 'R' :: '1' :: ':' :: k => match leads.find? (leadKey · == String.mk k), l.readings.mapM (readingClause ctx v) with
    | some d, some cs => "If " ++ " and ".intercalate cs ++ ", " ++ leadPhrase d ++ "."
    | _, _ => ""
  | 'S' :: '2' :: 'p' :: ':' :: i => match l.witness, (String.mk i).toNat? with
    | some c, some n => (v.points "S2p" c)[n]?.getD ""
    | _, _ => ""
  | 'S' :: '3' :: ':' :: i => match l.witness, (String.mk i).toNat? with
    | some c, some n => (v.points "S3" c)[n]?.getD ""
    | _, _ => ""
  | _ => ""

/-- An S1, S2 or X1 line's text: its lead-in, the choice's situation and the readings it names. -/
def situationText (ctx : Context) (v : View) (l : Line) (leadIn : String) : String :=
  match l.witness with
  | some c => match v.situation (l.frame) c, readingSuffix ctx v l.readings with
    | some sit, some sfx => leadIn ++ sit ++ sfx ++ "."
    | _, _ => ""
  | none => ""

/-- The text of a line, from its metadata and the view: the one owner of every line's words. -/
def lineTextV (ctx : Context) (v : View) (l : Line) : String :=
  match l.frame with
  | "A0" => "You asked whether " ++ v.asked.sentence.dropRight 1 ++ "."
  | "A1" => leadText .yes
  | "A2" => leadText .no
  | "A3" => leadText .notSettled
  | "A4" => leadText .notNecessarily
  | "A5" => leadText .unknown
  | "R2" => "Every way of reading the document gives this answer."
  | "S1" => situationText ctx v l "Here is a situation the document allows where it fails: "
  | "S2" => situationText ctx v l "Here is a situation where the answer depends on what the text leaves unsaid: "
  | "X1" => situationText ctx v l "The document's rules or defaults conflict in this situation, so VE cannot answer: "
  | "X2" => reasonText .conflictUnchecked
  | "X3" => reasonText .inconsistent
  | "X4" => reasonText .noResult
  | "X5" => reasonText .tooMany
  | "X6" => reasonText .unchecked
  | "U1" => match v.unused.mapM ctx.displayOf with
    | some ds => s!"VE did not use {v.unused.length} sentences of this document that it could not read formally: " ++
        citationText ds ++ "."
    | none => ""
  | "C1" | "C2" | "C3" | "C4" => citeText ctx v l
  | _ => paramText ctx v l

/-- A line made from its metadata: its text is `lineText` of it. -/
def mk (ctx : Context) (v : View) (l : Line) : Line := { l with text := lineTextV ctx v l }

theorem lineText_text (ctx : Context) (v : View) (l : Line) (t : String) :
    lineTextV ctx v { l with text := t } = lineTextV ctx v l := rfl

theorem mk_text (ctx : Context) (v : View) (l : Line) : (mk ctx v l).text = lineTextV ctx v (mk ctx v l) := rfl

/-- Whether a reading's wording is unchecked. -/
def uncheckedIn (v : View) (ps : List (String × Nat)) : Bool :=
  ps.any fun p => v.names.any fun n => !n.checked && (n.set, n.index) == p

/-- The line citing one source, under the choice `c` (the group's first row). -/
def citeLine (ctx : Context) (v : View) (c : Choice) (s : Source) : Line :=
  mk ctx v <| match s with
  | .unit u => { frame := "C1", text := "", source := some s,
                 quote := (ctx.textOf u).map (u, ·) }
  | .rules p => match v.ruleUnits c p with
    | [] => { frame := "C3", text := "", source := some s }
    | [u] => { frame := "C1", text := "", source := some s, quote := (ctx.textOf u).map (u, ·) }
    | _ => { frame := "C2", text := "", source := some s, witness := some c }
  | .definition _ | .background => { frame := "C3", text := "", source := some s }
  | .pair _ _ | .fill _ _ => { frame := "C4", text := "", source := some s }

/-- A situation line (S1, S2, X1) of a row: its choice and every open set's reading. -/
def situationLine (ctx : Context) (v : View) (frame : String) (r : Row) : Line :=
  let rs := named (assignment v.ids r)
  mk ctx v { frame := frame, text := "", readings := rs, witness := some r.choice, unchecked := uncheckedIn v rs }

/-- The point lines (S2p or S3) after a situation line of a row. -/
def pointLines (ctx : Context) (v : View) (kind : String) (r : Row) (count : Nat) : List Line :=
  (List.range count).map fun i => mk ctx v { frame := kind ++ ":" ++ toString i, text := "", witness := some r.choice }

/-- The reason lines of an unknown group: each distinct reason of its rows, in order; X1 with the first conflict
    row's witness. -/
def reasonLines (ctx : Context) (v : View) (g : Group) : List Line :=
  let reasons := (g.rows.filterMap (·.reason)).eraseDups
  reasons.flatMap fun x =>
    if x == .conflict then match g.rows.find? (·.conflict == .conflict) with
      | some r => [situationLine ctx v "X1" r]
      | none => []
    else [mk ctx v { frame := reasonFrame x, text := "" }]

/-- The lines after a group's lead: its citations, its situation, or its reasons. -/
def groupReasons (ctx : Context) (v : View) (g : Group) : List Line :=
  match g.lead with
  | .yes | .no => g.cited.map (citeLine ctx v ((g.rows.head?.map (·.choice)).getD []))
  | .notNecessarily => match g.rows.find? (·.query == .refuted) with
    | some r => situationLine ctx v "S1" r :: pointLines ctx v "S3" r
        (v.points "S3" r.choice).length
    | none => []
  | .notSettled => match g.rows.find? (·.split == true) with
    | some r => situationLine ctx v "S2" r :: pointLines ctx v "S2p" r
        (v.points "S2p" r.choice).length
    | none => []
  | .unknown => reasonLines ctx v g

/-- One group's block: its lead (A1 to A5 when it is the only group, else an R1 line naming its readings of the
    relevant sets), its reasons, and R2 after the only block of a decided answer over open sets. -/
def renderGroupV (ctx : Context) (v : View) (g : Group) : List Line :=
  if v.groups.length < 2 then
    mk ctx v { frame := leadFrame g.lead, text := "" } :: groupReasons ctx v g ++
      (if !v.ids.isEmpty && g.lead != .unknown then [mk ctx v { frame := "R2", text := "" }] else [])
  else
    let rs := named g.on
    mk ctx v { frame := "R1:" ++ leadKey g.lead, text := "", readings := rs, unchecked := uncheckedIn v rs } ::
      groupReasons ctx v g

/-- U1, after every block, when the document has unused sentences whose display numbers are known. -/
def unusedLines (ctx : Context) (v : View) : List Line :=
  if v.unused.isEmpty then [] else match v.unused.mapM ctx.displayOf with
    | some _ => [mk ctx v { frame := "U1", text := "" }]
    | none => []

def renderV (ctx : Context) (v : View) : List Line :=
  askedLine v.asked.sentence :: (v.groups.flatMap (renderGroupV ctx v) ++ unusedLines ctx v)


/-! ## What the lines are -/

/-- What the shown witness of an S1, S2 or X1 line is: the row's accepted countermodel, split or conflict witness
    (each a row result Lean computed from the request's evidence). -/
def checkedWitnessRow (r : Row) (frame : String) : Prop :=
  (frame = "S1" ∧ r.query = .refuted) ∨ (frame = "S2" ∧ r.split = true) ∨ (frame = "X1" ∧ r.conflict = .conflict)

theorem citeLine_quote (ctx : Context) (v : View) (c : Choice) (s : Source) :
    ∀ u t, (citeLine ctx v c s).quote = some (u, t) → ctx.textOf u = some t := by
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

/-! ### What each kind of line is -/

/-- The frames that show a checked row's situation. -/
def witnessFrames : List String := ["S1", "S2", "X1"]

/-- What a line of a block is: a citation line of a decided group, or a line made from metadata with no source and no
    quote, whose frame is not U1, whose situation (S1, S2, X1) is a checked row's of the group naming every open set's
    reading of it, and whose unchecked mark covers its readings. -/
def BlockLine (ctx : Context) (v : View) (g : Group) (l : Line) : Prop :=
  ((g.lead = .yes ∨ g.lead = .no) ∧ ∃ s ∈ g.cited, l = citeLine ctx v ((g.rows.head?.map (·.choice)).getD []) s) ∨
  (∃ l0 : Line, l = mk ctx v l0 ∧ l0.source = none ∧ l0.quote = none ∧ l0.frame ≠ "U1" ∧
    (l0.frame ∈ witnessFrames → ∃ r ∈ g.rows, checkedWitnessRow r l0.frame ∧
      l0.witness = some r.choice ∧ l0.readings = named (assignment v.ids r)) ∧
    (l0.readings = [] ∨ l0.unchecked = uncheckedIn v l0.readings))

theorem citeLine_source (ctx : Context) (v : View) (c : Choice) (s : Source) :
    (citeLine ctx v c s).source = some s := by
  unfold citeLine mk
  cases s with
  | rules p =>
    dsimp only
    split <;> rfl
  | _ => rfl

theorem citeLine_fields (ctx : Context) (v : View) (c : Choice) (s : Source) :
    (citeLine ctx v c s).readings = [] ∧ (citeLine ctx v c s).frame ∈ ["C1", "C2", "C3", "C4"] := by
  unfold citeLine mk
  cases s with
  | rules p =>
    dsimp only
    split <;> simp
  | _ => simp

theorem frame_param_length (kind : String) (i : Nat) (hk : 2 ≤ kind.length) :
    (kind ++ ":" ++ toString i).length ≥ 3 := by
  simp only [String.length_append]
  have : ":".length = 1 := rfl
  omega

theorem param_not_short {f : String} (h : f.length ≥ 3) : f ∉ witnessFrames ∧ f ≠ "U1" := by
  refine ⟨fun hm => ?_, fun he => ?_⟩
  · simp only [witnessFrames, List.mem_cons, List.not_mem_nil, or_false] at hm
    rcases hm with rfl | rfl | rfl <;> exact absurd h (by decide)
  · subst he
    exact absurd h (by decide)

theorem situationLine_block (ctx : Context) (v : View) (g : Group) (frame : String) (r : Row)
    (hr : r ∈ g.rows) (hw : checkedWitnessRow r frame) (hf : frame ≠ "U1") :
    BlockLine ctx v g (situationLine ctx v frame r) := by
  right
  refine ⟨_, rfl, rfl, rfl, hf, fun _ => ⟨r, hr, hw, rfl, rfl⟩, Or.inr rfl⟩

theorem pointLines_block (ctx : Context) (v : View) (g : Group) (kind : String) (r : Row) (n : Nat)
    (hk : 2 ≤ kind.length) : ∀ l ∈ pointLines ctx v kind r n, BlockLine ctx v g l := by
  intro l hl
  simp only [pointLines, List.mem_map, List.mem_range] at hl
  obtain ⟨i, _, rfl⟩ := hl
  have hp := param_not_short (frame_param_length kind i hk)
  right
  exact ⟨_, rfl, rfl, rfl, hp.2, fun hm => absurd hm hp.1, Or.inl rfl⟩

theorem plain_block (ctx : Context) (v : View) (g : Group) (f : String) (hw : f ∉ witnessFrames) (hu : f ≠ "U1") :
    BlockLine ctx v g (mk ctx v { frame := f, text := "" }) := by
  right
  exact ⟨_, rfl, rfl, rfl, hu, fun hm => absurd hm hw, Or.inl rfl⟩

theorem find_mem {p : Row → Bool} {rows : List Row} {r : Row} (h : rows.find? p = some r) : r ∈ rows ∧ p r = true :=
  ⟨List.mem_of_find?_eq_some h, List.find?_some h⟩

theorem reasonLines_block (ctx : Context) (v : View) (g : Group) :
    ∀ l ∈ reasonLines ctx v g, BlockLine ctx v g l := by
  intro l hl
  simp only [reasonLines, List.mem_flatMap] at hl
  obtain ⟨x, _, hl⟩ := hl
  split at hl
  · rename_i hx
    split at hl
    · rename_i r hr
      simp only [List.mem_singleton] at hl
      subst hl
      obtain ⟨hm, hp⟩ := find_mem hr
      exact situationLine_block ctx v g "X1" r hm (Or.inr (Or.inr ⟨rfl, by simpa using hp⟩)) (by decide)
    · cases hl
  · rename_i hx
    simp only [List.mem_singleton] at hl
    subst hl
    apply plain_block
    · cases x <;> simp_all [reasonFrame, witnessFrames]
    · cases x <;> simp [reasonFrame]

theorem groupReasons_block (ctx : Context) (v : View) (g : Group) :
    ∀ l ∈ groupReasons ctx v g, BlockLine ctx v g l := by
  intro l hl
  unfold groupReasons at hl
  split at hl
  · rename_i hlead
    simp only [List.mem_map] at hl
    obtain ⟨s, hs, rfl⟩ := hl
    exact Or.inl ⟨Or.inl hlead, s, hs, rfl⟩
  · rename_i hlead
    simp only [List.mem_map] at hl
    obtain ⟨s, hs, rfl⟩ := hl
    exact Or.inl ⟨Or.inr hlead, s, hs, rfl⟩
  · split at hl
    · rename_i r hr
      obtain ⟨hm, hp⟩ := find_mem hr
      simp only [List.mem_cons] at hl
      rcases hl with rfl | hl
      · exact situationLine_block ctx v g "S1" r hm (Or.inl ⟨rfl, by simpa using hp⟩) (by decide)
      · exact pointLines_block ctx v g "S3" r _ (by decide) l hl
    · cases hl
  · split at hl
    · rename_i r hr
      obtain ⟨hm, hp⟩ := find_mem hr
      simp only [List.mem_cons] at hl
      rcases hl with rfl | hl
      · exact situationLine_block ctx v g "S2" r hm (Or.inr (Or.inl ⟨rfl, by simpa using hp⟩)) (by decide)
      · exact pointLines_block ctx v g "S2p" r _ (by decide) l hl
    · cases hl
  · exact reasonLines_block ctx v g l hl

theorem leadFrame_ok (d : Lead) : leadFrame d ∉ witnessFrames ∧ leadFrame d ≠ "U1" := by
  cases d <;> decide

theorem r1Frame_ok (d : Lead) : ("R1:" ++ leadKey d) ∉ witnessFrames ∧ ("R1:" ++ leadKey d) ≠ "U1" := by
  cases d <;> decide

theorem renderGroup_block (ctx : Context) (v : View) (g : Group) :
    ∀ l ∈ renderGroupV ctx v g, BlockLine ctx v g l := by
  intro l hl
  unfold renderGroupV at hl
  split at hl
  · simp only [List.mem_cons, List.mem_append] at hl
    rcases hl with (rfl | hl) | hl
    · exact plain_block ctx v g _ (leadFrame_ok g.lead).1 (leadFrame_ok g.lead).2
    · exact groupReasons_block ctx v g l hl
    · split at hl
      · simp only [List.mem_singleton] at hl
        subst hl
        exact plain_block ctx v g "R2" (by decide) (by decide)
      · cases hl
  · simp only [List.mem_cons] at hl
    rcases hl with rfl | hl
    · right
      exact ⟨_, rfl, rfl, rfl, (r1Frame_ok g.lead).2, fun hm => absurd hm (r1Frame_ok g.lead).1, Or.inr rfl⟩
    · exact groupReasons_block ctx v g l hl

theorem unusedLines_eq (ctx : Context) (v : View) :
    ∀ l ∈ unusedLines ctx v, l = mk ctx v { frame := "U1", text := "" } := by
  intro l hl
  unfold unusedLines at hl
  split at hl
  · cases hl
  · split at hl
    · simpa using hl
    · cases hl

theorem render_mem {ctx : Context} {v : View} {l : Line} (h : l ∈ renderV ctx v) :
    l = askedLine v.asked.sentence ∨ (∃ g ∈ v.groups, BlockLine ctx v g l) ∨
      l = mk ctx v { frame := "U1", text := "" } := by
  simp only [renderV, List.mem_cons, List.mem_append, List.mem_flatMap] at h
  rcases h with h | ⟨g, hg, hl⟩ | h
  · exact Or.inl h
  · exact Or.inr (Or.inl ⟨g, hg, renderGroup_block ctx v g l hl⟩)
  · exact Or.inr (Or.inr (unusedLines_eq ctx v l h))

/-! ### The render theorems (spec 5.2) -/

theorem render_quotes_bytesV : ∀ (ctx : Context) (v : View),     ∀ l ∈ renderV ctx v, ∀ u t, l.quote = some (u, t) → ctx.textOf u = some t := by
  intro ctx v l hl u t hq
  rcases render_mem hl with rfl | ⟨g, _, hb⟩ | rfl
  · cases hq
  · rcases hb with ⟨_, s, _, rfl⟩ | ⟨l0, rfl, _, h0, _⟩
    · exact citeLine_quote ctx v _ s u t hq
    · simp [mk, h0] at hq
  · cases hq

theorem render_text_matches_metadataV : ∀ (ctx : Context) (v : View),     ∀ l ∈ renderV ctx v, l.text = lineTextV ctx v l := by
  intro ctx v l hl
  rcases render_mem hl with rfl | ⟨g, _, hb⟩ | rfl
  · rfl
  · rcases hb with ⟨_, s, _, rfl⟩ | ⟨l0, rfl, _⟩
    · unfold citeLine
      exact mk_text _ _ _
    · exact mk_text _ _ _
  · exact mk_text _ _ _

theorem render_askedV : ∀ (ctx : Context) (v : View), (renderV ctx v).head? = some (askedLine v.asked.sentence) := by
  intro ctx v
  rfl

theorem render_cites_exactV : ∀ (ctx : Context) (v : View) (g : Group), g ∈ v.groups →
    (g.lead = .yes ∨ g.lead = .no) → (renderGroupV ctx v g).filterMap (·.source) = g.cited := by
  intro ctx v g _ hlead
  have hc : (groupReasons ctx v g).filterMap (·.source) = g.cited := by
    unfold groupReasons
    rcases hlead with h | h <;> simp [h, List.filterMap_map, Function.comp_def, citeLine_source]
  unfold renderGroupV
  split
  · rw [List.filterMap_append, List.filterMap_cons]
    show (groupReasons ctx v g).filterMap (·.source) ++ _ = _
    rw [hc]
    split <;> simp [mk]
  · rw [List.filterMap_cons]
    exact hc

theorem render_leadV : ∀ (ctx : Context) (v : View) (g : Group), g ∈ v.groups →
    leadOfLine (renderGroupV ctx v g).head? = some g.lead := by
  intro ctx v g _
  unfold renderGroupV
  split
  · cases g.lead <;> rfl
  · cases g.lead <;> rfl

/-- R7, with `groups_cover`: each row's one block names exactly its readings of the relevant sets. -/
theorem render_covers_rowsV : ∀ (ctx : Context) (v : View) (g : Group), g ∈ v.groups → 2 ≤ v.groups.length →
    ((renderGroupV ctx v g).head?.map (·.readings)) = some (named g.on) := by
  intro ctx v g _ h2
  unfold renderGroupV
  rw [if_neg (by omega)]
  rfl

/-- R8: an unchecked wording is marked in the line that shows it. -/
theorem render_marks_uncheckedV : ∀ (ctx : Context) (v : View), ∀ l ∈ renderV ctx v,
    (∃ n ∈ v.names, n.checked = false ∧ (n.set, n.index) ∈ l.readings) → l.unchecked = true := by
  intro ctx v l hl ⟨n, hn, hc, hr⟩
  have hu : uncheckedIn v l.readings = true := by
    simp only [uncheckedIn, List.any_eq_true, Bool.and_eq_true, Bool.not_eq_true', beq_iff_eq]
    exact ⟨_, hr, n, hn, hc, rfl⟩
  rcases render_mem hl with rfl | ⟨g, _, hb⟩ | rfl
  · simp [askedLine] at hr
  · rcases hb with ⟨_, s, _, rfl⟩ | ⟨l0, rfl, _, _, _, _, h0⟩
    · rw [(citeLine_fields ctx v ((g.rows.head?.map (·.choice)).getD []) s).1] at hr
      cases hr
    · rcases h0 with h0 | h0
      · simp [mk, h0] at hr
      · simp only [mk] at hu ⊢
        rw [h0]
        exact hu
  · simp [mk] at hr

theorem render_model_names_choiceV : ∀ (ctx : Context) (v : View),     ∀ l ∈ renderV ctx v, l.frame ∈ ["S1", "S2", "X1"] →
      ∃ r ∈ v.rows, l.witness = some r.choice ∧ checkedWitnessRow r l.frame ∧
        l.readings = named (assignment v.ids r) := by
  intro ctx v l hl hf
  rcases render_mem hl with rfl | ⟨g, hg, hb⟩ | rfl
  · simp [askedLine] at hf
  · rcases hb with ⟨_, s, _, rfl⟩ | ⟨l0, rfl, _, _, _, hw, _⟩
    · have := (citeLine_fields ctx v ((g.rows.head?.map (·.choice)).getD []) s).2
      simp only [List.mem_cons, List.not_mem_nil, or_false] at this hf
      rcases this with h | h | h | h <;> rw [h] at hf <;> simp at hf
    · obtain ⟨r, hr, hc, hw', hrd⟩ := hw hf
      have hmem := (group_rows v.ids v.rows v.key g hg r hr).1
      exact ⟨r, hmem, hw', hc, hrd⟩
  · simp [mk] at hf

/-- D14, R8: one U1 after all answer blocks, with the document-derived count and citation; none for an empty list. -/
theorem render_unused_onceV : ∀ (ctx : Context) (v : View) (displays : List Nat),
    v.unused.mapM ctx.displayOf = some displays →
    (v.unused = [] → ∀ l ∈ renderV ctx v, l.frame ≠ "U1") ∧
    (v.unused ≠ [] → ∃ pre u, renderV ctx v = pre ++ [u] ∧
      (∀ l ∈ pre, l.frame ≠ "U1") ∧ u.frame = "U1" ∧
      u.text = lineTextV ctx v u ∧ u.quote = none ∧ u.source = none ∧
      u.readings = [] ∧ u.witness = none ∧
      u.text = s!"VE did not use {v.unused.length} sentences of this document that it could not read formally: " ++
        citationText displays ++ ".") := by
  intro ctx v displays hd
  have hpre : ∀ l ∈ askedLine v.asked.sentence :: v.groups.flatMap (renderGroupV ctx v), l.frame ≠ "U1" := by
    intro l hl
    simp only [List.mem_cons, List.mem_flatMap] at hl
    rcases hl with rfl | ⟨g, _, hl⟩
    · simp [askedLine]
    · rcases renderGroup_block ctx v g l hl with ⟨_, s, _, rfl⟩ | ⟨l0, rfl, _, _, hu, _⟩
      · have := (citeLine_fields ctx v ((g.rows.head?.map (·.choice)).getD []) s).2
        simp only [List.mem_cons, List.not_mem_nil, or_false] at this
        rcases this with h | h | h | h <;> rw [h] <;> decide
      · exact hu
  constructor
  · intro he l hl
    have hr : renderV ctx v = askedLine v.asked.sentence :: v.groups.flatMap (renderGroupV ctx v) := by
      simp [renderV, unusedLines, he]
    rw [hr] at hl
    exact hpre l hl
  · intro hne
    have hu : unusedLines ctx v = [mk ctx v { frame := "U1", text := "" }] := by
      have : v.unused.isEmpty = false := by simpa using hne
      simp only [unusedLines, this, hd, Bool.false_eq_true, ↓reduceIte]
    refine ⟨askedLine v.asked.sentence :: v.groups.flatMap (renderGroupV ctx v), mk ctx v { frame := "U1", text := "" },
      ?_, hpre, rfl, rfl, rfl, rfl, rfl, rfl, ?_⟩
    · simp [renderV, hu]
    · show lineTextV ctx v { frame := "U1", text := "" } = _
      simp only [lineTextV, hd]
      rfl


end VE.Ask
