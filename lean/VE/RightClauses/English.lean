import VE.RightClauses.Tree
import VE.Question.Frames
import VE.EnglishGrammar.Norm.Rules
import VE.Presupposition.Run

/-! The English of `right-clauses@0` (docs/spec/right-clauses.md 2): RC1 to RC4 as frames of stage S3, shown only
through W7's all-derivations gate (composition.md 2), in the form of `VE.Question.Frames`: each frame fixed text and
slots, a line shown as frame `f` only when, over every frame registered here, it has exactly one derivation and that
derivation is `f`'s (`gated`). RC2 is the relation instance inside RC1 and RC3; each instance passes the gate as RC2
before it is placed. `english` returns the shown lines of a document in document order (the reader's checklist,
spec 2): RC1 for every structured line, RC3 for every total relation, RC4 for every line; a line that does not pass
the gate, or that holds a G6 or G9 substring, refuses the whole answer (`english_gated`). RC5 is cmp-s3-candrel's.

The words are the request's lexicon (the rights line's soft environment, as `ve.surface.rights` words it): sort nouns
and predicate wordings. The consequence is the norm grammar's (`VE.EnglishGrammar.Norm.wording`, a default line's
modal as `_soft_consequence` words it); conditions are the core renderer's (`VE.English.renderTree`) in the line's
scope, the line's slots named as `Norm.bindings` names them. -/
namespace VE.RightClauses.English
open VE.Question (Piece pieceReadings)
open VE.RightClauses

/-- RC1 to RC4 of spec 2, each `<...>` part (with any optional part after it) one `slot`; RC1 once per line kind. -/
def rcFrames : List (String × List Piece) :=
  [("RC1", [.lit "Claim of right ", .num, .lit ". ", .slot, .lit "."]),
   ("RC1", [.lit "Liberty of right ", .num, .lit ". ", .slot, .lit "."]),
   ("RC1", [.lit "Immunity of right ", .num, .lit ". ", .slot, .lit "."]),
   ("RC2", [.lit "that ", .slot]),
   ("RC2", [.lit "the first ", .slot]),
   ("RC2", [.lit "the second ", .slot]),
   ("RC3", [.lit "For every ", .slot, .lit " there is at least one ", .slot, .lit " such that ", .slot, .lit "."]),
   ("RC4", [.lit "This line leaves out: ", .slot, .lit "."]),
   ("RC4", [.lit "This line leaves out nothing."])]

/-- Every derivation of a line from every frame of `rcFrames`. -/
def readings (line : String) : List (String × List String) :=
  rcFrames.flatMap fun (name, ps) => (pieceReadings ps line.toList).map (name, ·)

/-- W7's all-derivations gate: the line has exactly one derivation, and it is frame `f`'s; its slots. -/
def gated (f line : String) : Option (List String) :=
  match readings line with
  | [(g, slots)] => if g == f then some slots else none
  | _ => none

/-- G6's generated-name substrings and G9's `may not` (composition.md 10.4; 13.20: no exception for source text). -/
def banned : List String := ["ve__", "rd-", "soft__", "rights__", "may not"]

def holds (pat s : String) : Bool := (VE.EnglishGrammar.findSub pat.toList s.toList 0).isSome

/-- A shown line of the answer: its frame, the rule name of its line, its text. -/
structure Row where
  frame : String
  rule : String
  text : String
  deriving DecidableEq, Repr

/-- Shown only when it passes the gate as its frame and holds no G6 or G9 substring. -/
def shown (r : Row) : Bool := (gated r.frame r.text).isSome && !banned.any (holds · r.text)

/-- The core renderer's lexicon of the request's: nouns and wordings as words, `{i}` placeholder `i`. -/
def slotOf (w : String) : VE.English.Slot :=
  match (if w.startsWith "{" && w.endsWith "}" then ((w.drop 1).dropRight 1).toNat? else none) with
  | some i => .hole i
  | none => .word w

def coreLexicon (L : VE.EnglishGrammar.Lexicon) : VE.English.Lexicon where
  sorts := L.nouns.map (·.1)
  noun s := ((L.nouns.lookup s).getD "").splitOn " "
  letter s := (L.letters.lookup s).getD ""
  predicates := L.wordings.map (·.1)
  template p := (L.wordings.lookup p).map fun w => (w.splitOn " ").map slotOf
  constants := L.spellings.map (·.1)
  spelling c := ((L.spellings.lookup c).getD "").splitOn " "

/-- Every symbol of `φ` has its words: a predicate a template with exactly its places, a constant a spelling, a sort
    a noun; else the line is not worded (a missing word would drop part of the condition). -/
def worded (L : VE.English.Lexicon) : VE.Formula → Bool
  | .top | .bottom => true
  | .unary p t => (L.template p).any (fun T => T.arity == 1 && T.contains (.hole 0)) && term t
  | .binary p t u => (L.template p).any (fun T => T.arity == 2 && T.contains (.hole 0) && T.contains (.hole 1)) &&
      term t && term u
  | .eq t u => term t && term u
  | .not a => worded L a
  | .and a b | .or a b | .implies a b => worded L a && worded L b
  | .all s a | .ex s a => L.sorts.contains s && worded L a
where term : VE.Term → Bool
  | .var _ => true
  | .const c => L.constants.contains c

/-- A condition in the scope `Γ` (innermost first), on one line. -/
def condition (L : VE.English.Lexicon) (Γ : List VE.English.Ref) (φ : VE.Formula) : Option String :=
  if worded L φ && Γ.all (L.sorts.contains ·.sort) then
    some (VE.Presupposition.lineOf
      ((VE.English.renderTree L (fun s => Γ.countP (·.sort == s) + VE.English.sdepth s φ) Γ φ).yield L 0))
  else none

/-- The names of a line's slots, in slot order (`Norm.bindings`): `that <noun>`, or `the first` / `the second` for
    a sort that occurs twice. -/
def refs (ss : List String) : Option (List VE.English.Ref) :=
  (List.range ss.length).zip ss |>.mapM fun (i, s) =>
    match ss.count s, (ss.take i).count s with
    | 1, _ => some (.plain s)
    | 2, 0 => some (.first s)
    | 2, _ => some (.second s)
    | _, _ => none

/-- RC2: the relation atom `pred(x_a, x_b)` in the scope `Γ` (innermost first, slot `j` at `k-1-j`), through the
    gate as RC2. -/
def relInstance (L : VE.English.Lexicon) (Γ : List VE.English.Ref) (r : Relation) : Option String := do
  let t := condition L Γ (.binary r.pred (.var (Γ.length - 1 - r.slots.1)) (.var (Γ.length - 1 - r.slots.2)))
  let s ← t
  (gated "RC2" s).map fun _ => s

/-- RC1: the rights line sentence up to its act and holder (`<Kind> of right <n>. ` and the consequence), then the
    relation instance, the guard (left out when `⊤`) and the clauses in wire order, then the line's carve-outs as
    rights 2.1 words them. -/
def rc1 (D : ClauseDoc) (L : VE.EnglishGrammar.Lexicon) (R : String) (c : CLine) : Option String := do
  let kind ← match c.line.kind with
    | .claim => some "Claim" | .liberty => some "Liberty" | .immunity => some "Immunity" | .power => none
  let N ← c.line.norm
  let r ← D.doc.soft.T.regulated.find? (·.name == N.pred)
  let (σ, ds) ← VE.EnglishGrammar.Norm.bindings L r.sorts
  let strict ← VE.EnglishGrammar.Norm.wording L r σ ds N.sign
  let consequence ← match N.mode, r.role with
    | .strict, _ => some strict
    | .default, .obligation => some (VE.EnglishGrammar.replaceFirst strict (if N.sign then " must " else " need not ")
        (if N.sign then " should " else " generally need not "))
    | .default, .permission => some (VE.EnglishGrammar.replaceFirst strict (if N.sign then " may " else " must not ")
        (if N.sign then " generally may " else " should not "))
    | .default, .plain => none
  let cL := coreLexicon L
  let Γ := (← refs r.sorts).reverse
  let rel ← match c.relation with
    | some x => (relInstance cL Γ x).map (", where " ++ ·)
    | none => some ""
  let parts ← ((if N.guard == .top then [] else [N.guard]) ++ c.clauses.map (·.formula)).mapM (condition cL Γ)
  let conds := if parts.isEmpty then "" else ", if " ++ " and ".intercalate parts
  let carve ← N.carveOuts.mapM (condition cL Γ)
  let tail := match carve with
    | [u] => ", unless " ++ u ++ "."
    | us => "." ++ String.join (us.map (" Except when " ++ · ++ "."))
  some (s!"{kind} of right {(D.doc.rs.map (·.name)).idxOf R + 1}. " ++ consequence ++ rel ++ conds ++ tail)

/-- RC3 for a total relation (total on the holder slot `j`, `o` the other): the holder introduced first, as `the
    first <sort>` and slot `o` as `the second <sort>` when both are of one sort; the right's holder guard `H` after
    `that` when it is not `⊤`; the instance in the predicate's argument order. -/
def rc3 (D : ClauseDoc) (L : VE.EnglishGrammar.Lexicon) (R : String) (c : CLine) (r : Relation) (j : Nat) :
    Option String := do
  let ss := lineSorts D.doc.soft c.line
  let o := if r.slots.1 == j then r.slots.2 else r.slots.1
  let (sj, so) := (← ss[j]?, ← ss[o]?)
  let h : VE.English.Ref := if sj == so then .first sj else .plain sj
  let w : VE.English.Ref := if sj == so then .second so else .plain so
  let cL := coreLexicon L
  let H := ((D.doc.rs.find? (·.name == R)).map (·.guard)).getD .top
  let that ← if H == .top then some "" else (condition cL [h] H).map (" that " ++ ·)
  let arg (i : Nat) : VE.Term := .var (if i == j then 1 else 0)
  let inst ← condition cL [w, h] (.binary r.pred (arg r.slots.1) (arg r.slots.2))
  let _ ← gated "RC2" inst
  let decl (x : VE.English.Ref) := VE.Presupposition.lineOf (x.declYield cL)
  some ("For every " ++ decl h ++ that ++ " there is at least one " ++ decl w ++ " such that " ++ inst ++ ".")

/-- RC4: each elided span quoted with its source bytes, in the line's order; a span whose text holds `may not`, a
    double quote or a G6 substring, or is no UTF-8 text, as `bytes [<a>, <b>)`. A span outside the source refuses. -/
def rc4 (src : ByteArray) (n : String) (es : List (Nat × Nat)) : Except String String := do
  let one (sp : Nat × Nat) : Except String String :=
    if sp.2 ≤ src.size then
      match String.fromUTF8? (src.extract sp.1 sp.2) with
      | some t => if ("\"" :: banned).any (holds · t) then pure s!"bytes [{sp.1}, {sp.2})" else pure ("\"" ++ t ++ "\"")
      | none => pure s!"bytes [{sp.1}, {sp.2})"
    else throw s!"InvalidInput: {n}: elided span [{sp.1}, {sp.2}) is outside the source"
  if es.isEmpty then pure "This line leaves out nothing."
  else pure ("This line leaves out: " ++ "; ".intercalate (← es.mapM one) ++ ".")

/-- The rows of one line: RC1 when it is structured, RC3 when its relation is total, then RC4. -/
def lineRows (D : ClauseDoc) (L : VE.EnglishGrammar.Lexicon) (src : ByteArray) (x : String × String × CLine) :
    Except String (List Row) := do
  let (R, n, c) := x
  let word (f : String) : Option String → Except String (List Row)
    | some t => pure [⟨f, n, t⟩]
    | none => throw s!"CheckerUnavailable: VE could not word the {f} line of {n}"
  let one ← if c.clauses.isEmpty && c.relation.isNone then pure [] else word "RC1" (rc1 D L R c)
  let three ← match c.relation with
    | some r => match r.total with
      | some j => word "RC3" (rc3 D L R c r j)
      | none => pure []
    | none => pure []
  pure (one ++ three ++ [⟨"RC4", n, ← rc4 src n c.elided⟩])

/-- The frame and rule of the first row that is not shown (named in the refusal; its text is never shown). -/
def firstUnshown (rows : List Row) : String :=
  ((rows.find? (!shown ·)).map fun r => s!"{r.frame} line of {r.rule}").getD ""

/-- The shown lines of `D` in document order, each line read once; returned only when every one is `shown`. -/
def english (D : ClauseDoc) (L : VE.EnglishGrammar.Lexicon) (source : String) : Except String (List Row) :=
  match D.lines.mapM (lineRows D L source.toUTF8) with
  | .error e => .error e
  | .ok xs =>
    if xs.flatten.all shown then .ok xs.flatten
    else .error s!"CheckerUnavailable: the {firstUnshown xs.flatten} does not pass the all-derivations gate"

/-- Every line `english` returns passes W7's all-derivations gate: over every frame of `rcFrames`, its text has
    exactly one derivation, and it is its own frame's. -/
theorem english_gated : ∀ (D : ClauseDoc) (L : VE.EnglishGrammar.Lexicon) (source : String) (rows : List Row),
    english D L source = .ok rows → ∀ r ∈ rows, ∃ slots, readings r.text = [(r.frame, slots)] := by
  intro D L source rows h r hr
  unfold english at h
  split at h
  · cases h
  · split at h
    · rename_i hs
      cases h
      simp only [List.all_eq_true] at hs
      have hg : (gated r.frame r.text).isSome = true := by
        have := hs r hr
        unfold shown at this
        simp only [Bool.and_eq_true] at this
        exact this.1
      unfold gated at hg
      split at hg
      · rename_i g slots hrd
        split at hg
        · rename_i he
          have : g = r.frame := by simpa using he
          subst this
          exact ⟨slots, hrd⟩
        · cases hg
      · cases hg
    · cases h

end VE.RightClauses.English
