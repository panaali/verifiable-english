import VE.Discourse.Access

/-! # The discourse grammar (docs/spec/discourse.md 4.3, 9.2)

`Derives D u s d`: `d` is a derivation of the token list `s` of unit `u` in the discourse
grammar, a small explicit sentence grammar with a slot production for each
formula-producing form of 1.4. A derivation is a tree plus its slots in source order (an
enclosing slot before the slots nested in it); a slot is (unit, span, form), a surface
position and never a target. The grammar is a relation defined by a checking function on a
given tree (`treeEnd`), independent of the enumerator `derivs`, which is proved to list
exactly the derivations (`mem_derivs`): the all-derivations gate.

Sentences (tokens are lowercased words, the sentence ends with `.`):

```
sentence := core | "by" CITE LABEL "," core                    -- citation slot on "CITE LABEL"
core     := NP ("is" | "are") ADJ
          | NAME "and" NAME "are" ADJ                           -- the coordination of a pair
          | NP VERB NP
          | ("every" | "a" | "an") MOD SORT "is" ADJ
          | "every" W SORT "is" ADJ "," "where" W "has" "the" "meaning" "defined" "in" "section" L
                                                                -- definition_ref slot on W
MOD      := ε | ADJ | "such"                                    -- such slot
NP       := NAME                                                -- a registered display or alias
          | PRONOUN | "they" | ("this" | "that") SORT | "the" ("former" | "latter") | DOCUMENT
          | "the" NOUN                                          -- definite slot, restriction NOUN(x)
          | POSSESSIVE RELNOUN                                  -- definite slot with a nested
                                                                   possessive slot, RELNOUN_of(x, ·)
```
-/
namespace VE.Discourse
open VE.English (Tok)

/-- The restriction of a definite: a unary noun, or a relational noun with the nested
possessive slot supplying its other argument. -/
inductive Restr where
  | noun (p : String)
  | rel (p : String) (poss : Slot)
  deriving DecidableEq, Repr

inductive NP where
  | name (c : String) (k : Nat)          -- spelling `k` of the registered constant `c`
  | slot (m : Slot)                      -- pronoun, plural, demonstrative, ordinal pair, document name
  | definite (m : Slot) (r : Restr)
  deriving DecidableEq, Repr

inductive Mod where
  | none
  | adj (p : String)
  | slot (m : Slot)                      -- `such`
  deriving DecidableEq, Repr

inductive Core where
  | pred (subj : NP) (are : Bool) (p : String)
  | coord (a : String) (ka : Nat) (b : String) (kb : Nat) (p : String)
  | rel (subj : NP) (p : String) (obj : NP)
  | every (m : Mod) (s p : String)
  | some (an : Bool) (m : Mod) (s p : String)
  | everyDef (m : Slot) (s p sec : String)
  deriving DecidableEq, Repr

inductive STree where
  | core (c : Core)
  | cite (m : Slot) (c : Core)
  deriving DecidableEq, Repr

/-- 4.3: a derivation with its slots. -/
structure DTree where
  tree : STree
  slots : List Slot
  deriving DecidableEq, Repr

def pronounWords : List String := ["it", "she", "he", "her", "him"]
def possessiveWords : List String := ["her", "his", "its", "their"]
def demonstrativeWords : List String := ["this", "that"]
def ordinalWords : List String := ["former", "latter"]
def citeWords : List String := ["clause", "section", "article", "lemma"]

def isW (s : List Tok) (i : Nat) (w : String) : Bool := wordAt s i == some w

def verbWord (are : Bool) : String := if are then "are" else "is"
def articleWord (an : Bool) : String := if an then "an" else "a"

def wordIn (s : List Tok) (i : Nat) (ws : List String) : Bool := (wordAt s i).any ws.contains

/-- Words that always refer back: pronouns, possessives, plural pronouns, the ordinals of a
pair and `such`. -/
def referenceWords : List String :=
  ["it", "she", "he", "her", "him", "his", "its", "their", "they", "them", "former", "latter", "such"]

/-! ### Slot discovery (docs/spec/discourse.md 4.1(6))

Every reference surface of a unit's own text is a slot to account for, whether or not the grammar
places it. Discovery reads the unit's bytes alone (a unit boundary always ends a segment) as its
segments, the maximal runs of characters with a fold (`foldChar`: ASCII letters and digits, `İ`,
`ı`, `ſ`, the Kelvin sign), folded, with their byte ranges, so a reference word joined to anything
else (`It's`, `It-is`, `It_`, `Itʼs`, `İt`) is still found. At each segment the surfaces starting
there are: a reference word; `this|that` before the segments of a sort's name or of its declared
singular noun (`DDoc.nouns`); `the` before `former|latter`
or before segments whose `_`-join is a unary predicate; a document display's segments; and, after
`by`, a citation word through the end of the label the lexer reads after it. Scanning left to
right, the longest surface starting at a segment is taken and the scan resumes after it, so a
longer surface (a document display `It is safe`) is one surface, never its shorter parts. A unit
with meaning must record each surface as a formula-producing mention with exactly its byte range
(`coverageOk`). Python's `reference_surfaces` is the same function. -/

def segGo : List Char → Nat → List Char → Nat → List (String × Nat × Nat)
  | [], pos, cur, start => if cur.isEmpty then [] else [(String.mk cur.reverse, start, pos)]
  | c :: rest, pos, cur, start => match foldChar c with
    | some f => segGo rest (pos + c.utf8Size) (f :: cur) (if cur.isEmpty then pos else start)
    | none => (if cur.isEmpty then [] else [(String.mk cur.reverse, start, pos)]) ++
        segGo rest (pos + c.utf8Size) [] 0

/-- The segments of a text, folded, with their byte ranges `[a, b)`. -/
def segments (t : String) : List (String × Nat × Nat) := segGo t.toList 0 [] 0

/-- The folded segments of a string. -/
def segmentsOf (w : String) : List String := (segments w).map (·.1)

/-- A symbol name split into segments is spelled by its `_`-joined segments (identifiers are
`[a-z][a-z0-9_]*`, at most 64 bytes, so at most 32 segments). -/
def joinLimit : Nat := 32

/-- The end byte of a citation label: the first token the lexer reads in the text after byte `e`,
when it is a word (none: no label follows). -/
def labelEnd (t : String) (e : Nat) : Option Nat :=
  match lex (sliceText t e t.utf8ByteSize) with
  | (w, _, b) :: _ => if w.toList.head?.any wordChar then some (e + b) else none
  | [] => none

/-- The lengths, in segments, of the surfaces starting at segment `j` that end on a segment. -/
def segmentLengths (D : DDoc) (ws : List String) (j : Nat) : List Nat :=
  let after := ws.drop (j + 1)
  (if (ws[j]?).any referenceWords.contains then [1] else []) ++
  (if (ws[j]?).any demonstrativeWords.contains then
    (D.E.sorts ++ D.nouns).filterMap fun srt =>
      let p := segmentsOf srt
      if !p.isEmpty && p.isPrefixOf after then some (p.length + 1) else none
   else []) ++
  (if ws[j]? == some "the" then
    (if (after.head?).any ordinalWords.contains then [2] else []) ++
    (List.range (min after.length joinLimit)).filterMap fun k =>
      if unaryPred D.E ("_".intercalate (after.take (k + 1))) then some (k + 2) else none
   else []) ++
  D.K.documents.flatMap fun d => d.display.filterMap fun x =>
    let p := segmentsOf x
    if !p.isEmpty && p.isPrefixOf (ws.drop j) then some p.length else none

/-- The end bytes of the surfaces starting at segment `j` of a text with segments `sg`. -/
def surfaceEnds (D : DDoc) (t : String) (sg : List (String × Nat × Nat)) (j : Nat) : List Nat :=
  let ws := sg.map (·.1)
  (segmentLengths D ws j).filterMap (fun n => (sg[j + n - 1]?).map (·.2.2)) ++
  (if (ws[j]?).any citeWords.contains && j != 0 && ws[j - 1]? == some "by" then
    match sg[j]? with
    | some (_, _, e) => [(labelEnd t e).getD e]
    | none => []
   else [])

/-- The first segment at or after `j` that starts at or after byte `e`. -/
def resumeAt (sg : List (String × Nat × Nat)) (e j : Nat) : Nat :=
  j + ((sg.drop j).takeWhile (·.2.1 < e)).length

/-- The longest-first scan from segment `j` (the fuel bounds the segments left). -/
def scanFrom (D : DDoc) (t : String) (sg : List (String × Nat × Nat)) : Nat → Nat → List (Nat × Nat)
  | 0, _ => []
  | fuel + 1, j => match sg[j]? with
    | none => []
    | some (_, a, _) => match (surfaceEnds D t sg j).max? with
      | some e => (a, e) :: scanFrom D t sg fuel (resumeAt sg e (j + 1))
      | none => scanFrom D t sg fuel (j + 1)

/-- The reference surfaces of a text, as byte ranges of it, in order. -/
def textSurfaces (D : DDoc) (t : String) : List (Nat × Nat) :=
  let sg := segments t
  scanFrom D t sg sg.length 0

/-- The reference surfaces of unit `u`, as prose byte ranges: discovered in the unit's own text. -/
def discovered (D : DDoc) (u : String) : List (Nat × Nat) :=
  match unitOf D.base u with
  | some x => (textSurfaces D (sliceText D.prose x.start x.stop)).map fun r => (x.start + r.1, x.start + r.2)
  | none => []

/-- The slot forms an `NP.slot` may carry. -/
def simpleForm (f : Form) : Bool :=
  f == .pronoun || f == .plural || f == .demonstrative || f == .ordinalPair || f == .documentName

/-- The surface of a simple slot fits its form. -/
def surfaceOk (D : DDoc) (s : List Tok) (m : Slot) : Bool :=
  let i := m.span.1
  let j := m.span.2
  decide (j ≤ s.length) && match m.form with
  | .pronoun => j == i + 1 && wordIn s i pronounWords
  | .plural => j == i + 1 && isW s i "they"
  | .demonstrative => j == i + 2 && wordIn s i demonstrativeWords && (wordAt s (i + 1)).any (sortWord D.E)
  | .ordinalPair => j == i + 2 && isW s i "the" && wordIn s (i + 1) ordinalWords
  | .documentName => decide (i < j) && D.K.documents.any fun d => d.display.any fun x =>
      (s.drop i).take (j - i) == lexWords x
  | _ => false

def relWord (D : DDoc) (s : List Tok) (i : Nat) (p : String) : Bool :=
  match wordAt s i with
  | some w => p == w ++ "_of" && binaryPred D.E p
  | none => false

def npEnd (D : DDoc) (u : String) (s : List Tok) (i : Nat) : NP → Option Nat
  | .name c k => match registered D c with
    | some n => match (spellings n)[k]? with
      | some sp => if !sp.isEmpty && sp.isPrefixOf (s.drop i) then some (i + sp.length) else none
      | none => none
    | none => none
  | .slot m => if m.unit == u && m.span.1 == i && simpleForm m.form && surfaceOk D s m then some m.span.2 else none
  | .definite m (.noun p) =>
    if m == ⟨u, (i, i + 2), .definite⟩ && isW s i "the" && isW s (i + 1) p && unaryPred D.E p then some (i + 2)
    else none
  | .definite m (.rel p q) =>
    if m == ⟨u, (i, i + 2), .definite⟩ && q == ⟨u, (i, i + 1), .possessive⟩ && wordIn s i possessiveWords &&
      relWord D s (i + 1) p then some (i + 2) else none

def modEnd (D : DDoc) (u : String) (s : List Tok) (i : Nat) : Mod → Option Nat
  | .none => some i
  | .adj p => if isW s i p && unaryPred D.E p then some (i + 1) else none
  | .slot m => if m == ⟨u, (i, i + 1), .such⟩ && isW s i "such" then some (i + 1) else none

/-- The tokens of the `definition_ref` production after `every`. -/
def defTail (w s p sec : String) : List Tok :=
  [w, s, "is", p, ",", "where", w, "has", "the", "meaning", "defined", "in", "section", sec].map Tok.word

def coreEnd (D : DDoc) (u : String) (s : List Tok) (i : Nat) : Core → Option Nat
  | .pred subj are p => match npEnd D u s i subj with
    | some j => if isW s j (verbWord are) && isW s (j + 1) p && unaryPred D.E p then some (j + 2) else none
    | none => none
  | .coord a ka b kb p => match npEnd D u s i (.name a ka) with
    | some j => if isW s j "and" then match npEnd D u s (j + 1) (.name b kb) with
      | some k => if isW s k "are" && isW s (k + 1) p && unaryPred D.E p then some (k + 2) else none
      | none => none
      else none
    | none => none
  | .rel subj p obj => match npEnd D u s i subj with
    | some j => if isW s j p && binaryPred D.E p then npEnd D u s (j + 1) obj else none
    | none => none
  | .every m srt p => if isW s i "every" then match modEnd D u s (i + 1) m with
      | some j => if isW s j srt && sortWord D.E srt && isW s (j + 1) "is" && isW s (j + 2) p && unaryPred D.E p
          then some (j + 3) else none
      | none => none
    else none
  | .some an m srt p => if isW s i (articleWord an) then match modEnd D u s (i + 1) m with
      | some j => if isW s j srt && sortWord D.E srt && isW s (j + 1) "is" && isW s (j + 2) p && unaryPred D.E p
          then some (j + 3) else none
      | none => none
    else none
  | .everyDef m srt p sec => if isW s i "every" && m == ⟨u, (i + 1, i + 2), .definitionRef⟩ then
      match wordAt s (i + 1) with
      | some w => if (s.drop (i + 1)).take 14 == defTail w srt p sec && unaryPred D.E w && sortWord D.E srt &&
          unaryPred D.E p then some (i + 15) else none
      | none => none
    else none

def treeEnd (D : DDoc) (u : String) (s : List Tok) : STree → Option Nat
  | .core c => coreEnd D u s 0 c
  | .cite m c => if isW s 0 "by" && m == ⟨u, (1, 3), .citation⟩ && wordIn s 1 citeWords && (wordAt s 2).isSome &&
      isW s 3 "," then coreEnd D u s 4 c else none

def npSlots : NP → List Slot
  | .name _ _ => []
  | .slot m => [m]
  | .definite m (.noun _) => [m]
  | .definite m (.rel _ q) => [m, q]

def modSlots : Mod → List Slot
  | .slot m => [m]
  | _ => []

def coreSlots : Core → List Slot
  | .pred subj _ _ => npSlots subj
  | .coord .. => []
  | .rel subj _ obj => npSlots subj ++ npSlots obj
  | .every m _ _ | .some _ m _ _ => modSlots m
  | .everyDef m _ _ _ => [m]

def slotsOf : STree → List Slot
  | .core c => coreSlots c
  | .cite m c => m :: coreSlots c

/-- The sentence ends with `.` right after the tree. -/
def endsAt (s : List Tok) (j : Nat) : Bool := s.length == j + 1 && s[j]? == some (.word ".")

/-- 4.3: `d` derives the sentence `s` of unit `u`. -/
def Derives (D : DDoc) (u : String) (s : List Tok) (d : DTree) : Prop :=
  d.slots = slotsOf d.tree ∧ ∃ j, treeEnd D u s d.tree = some j ∧ endsAt s j = true

/-! ## The enumerator and its completeness -/

def wordsOf (s : List Tok) : List String := s.filterMap fun | .word w => some w | _ => none

def allForms : List Form :=
  [.pronoun, .demonstrative, .definite, .ordinalPair, .such, .possessive, .plural, .sectionRef,
   .definitionRef, .documentName, .citation, .navigation]

def nameCands (D : DDoc) : List (String × Nat) :=
  D.K.names.flatMap fun n => (List.range (spellings n).length).map (n.constant, ·)

def npCands (D : DDoc) (u : String) (s : List Tok) (i : Nat) : List NP :=
  (nameCands D).map (fun x => .name x.1 x.2) ++
  ((List.range (s.length + 1)).flatMap fun j => allForms.map fun f => .slot ⟨u, (i, j), f⟩) ++
  (wordsOf s).map (fun w => .definite ⟨u, (i, i + 2), .definite⟩ (.noun w)) ++
  (wordsOf s).map (fun w => .definite ⟨u, (i, i + 2), .definite⟩ (.rel (w ++ "_of") ⟨u, (i, i + 1), .possessive⟩))

def modCands (u : String) (s : List Tok) (i : Nat) : List Mod :=
  .none :: ((wordAt s i).toList.map .adj ++ [.slot ⟨u, (i, i + 1), .such⟩])

def coreCands (D : DDoc) (u : String) (s : List Tok) (i : Nat) : List Core :=
  ((npCands D u s i).flatMap fun np => match npEnd D u s i np with
    | some j => ([true, false].flatMap fun are => (wordAt s (j + 1)).toList.map (.pred np are ·)) ++
        ((wordAt s j).toList.flatMap fun p => (npCands D u s (j + 1)).map (.rel np p ·))
    | none => []) ++
  ((nameCands D).flatMap fun a => match npEnd D u s i (.name a.1 a.2) with
    | some j => (nameCands D).flatMap fun b => match npEnd D u s (j + 1) (.name b.1 b.2) with
      | some k => (wordAt s (k + 1)).toList.map (.coord a.1 a.2 b.1 b.2 ·)
      | none => []
    | none => []) ++
  ((modCands u s (i + 1)).flatMap fun m => match modEnd D u s (i + 1) m with
    | some j => (wordAt s j).toList.flatMap fun srt => (wordAt s (j + 2)).toList.flatMap fun p =>
        [.every m srt p, .some true m srt p, .some false m srt p]
    | none => []) ++
  ((wordAt s (i + 2)).toList.flatMap fun srt => (wordAt s (i + 4)).toList.flatMap fun p =>
    (wordAt s (i + 14)).toList.map fun sec => .everyDef ⟨u, (i + 1, i + 2), .definitionRef⟩ srt p sec)

def treeCands (D : DDoc) (u : String) (s : List Tok) : List STree :=
  (coreCands D u s 0).map .core ++ (coreCands D u s 4).map (.cite ⟨u, (1, 3), .citation⟩)

def derivesB (D : DDoc) (u : String) (s : List Tok) (t : STree) : Bool :=
  match treeEnd D u s t with
  | some j => endsAt s j
  | none => false

/-- Every derivation of the sentence, from the finite candidate trees. -/
def derivs (D : DDoc) (u : String) (s : List Tok) : List DTree :=
  ((treeCands D u s).filter (derivesB D u s)).map fun t => ⟨t, slotsOf t⟩

theorem wordAt_mem {s : List Tok} {i : Nat} {w : String} (h : wordAt s i = some w) : w ∈ wordsOf s := by
  unfold wordAt at h
  cases hx : s[i]? with
  | none => rw [hx] at h; cases h
  | some t =>
    rw [hx] at h
    cases t with
    | word w' =>
      cases h
      simp only [wordsOf, List.mem_filterMap]
      exact ⟨.word w, List.mem_of_getElem? hx, rfl⟩
    | label _ _ => cases h

theorem isW_wordAt {s : List Tok} {i : Nat} {w : String} (h : isW s i w = true) : wordAt s i = some w := by
  simpa [isW] using h

theorem isW_lt {s : List Tok} {i : Nat} {w : String} (h : isW s i w = true) : i < s.length := by
  have := isW_wordAt h
  unfold wordAt at this
  split at this
  · rename_i _ hw; exact (List.getElem?_eq_some_iff.mp hw).1
  · cases this

theorem wordAt_lt {s : List Tok} {i : Nat} {w : String} (h : wordAt s i = some w) : i < s.length := by
  unfold wordAt at h
  split at h
  · rename_i _ hw; exact (List.getElem?_eq_some_iff.mp hw).1
  · cases h

theorem mem_allForms (f : Form) : f ∈ allForms := by cases f <;> simp [allForms]

theorem registered_constant {D : DDoc} {c : String} {n : Name} (h : registered D c = some n) :
    n ∈ D.K.names ∧ n.constant = c := by
  unfold registered at h
  split at h
  · exact ⟨List.mem_of_find?_eq_some h, by simpa using List.find?_some h⟩
  · cases h

theorem name_mem_nameCands {D : DDoc} {u : String} {s : List Tok} {i : Nat} {c : String} {k j : Nat}
    (h : npEnd D u s i (.name c k) = some j) : (c, k) ∈ nameCands D := by
  simp only [npEnd] at h
  split at h
  · rename_i n hn
    split at h
    · rename_i sp hsp
      obtain ⟨hm, hc⟩ := registered_constant hn
      simp only [nameCands, List.mem_flatMap, List.mem_map, List.mem_range]
      exact ⟨n, hm, k, (List.getElem?_eq_some_iff.mp hsp).1, by rw [hc]⟩
    · cases h
  · cases h

theorem npEnd_cands (D : DDoc) (u : String) (s : List Tok) (i : Nat) (np : NP) (j : Nat)
    (h : npEnd D u s i np = some j) : np ∈ npCands D u s i := by
  unfold npCands
  simp only [List.mem_append, List.mem_map, List.mem_flatMap, List.mem_range]
  cases np with
  | name c k => exact Or.inl (Or.inl (Or.inl ⟨(c, k), name_mem_nameCands h, rfl⟩))
  | slot m =>
    simp only [npEnd] at h
    split at h
    · rename_i hc
      simp only [Bool.and_eq_true, beq_iff_eq] at hc
      obtain ⟨⟨⟨hu, hi⟩, _⟩, hs⟩ := hc
      have hle : m.span.2 ≤ s.length := by
        simp only [surfaceOk, Bool.and_eq_true, decide_eq_true_eq] at hs
        exact hs.1
      refine Or.inl (Or.inl (Or.inr ⟨m.span.2, by omega, m.form, mem_allForms _, ?_⟩))
      rcases m with ⟨mu, ⟨a, b⟩, f⟩
      simp only at hu hi
      subst hu hi
      rfl
    · cases h
  | definite m r =>
    cases r with
    | noun p =>
      simp only [npEnd] at h
      split at h
      · rename_i hc
        simp only [Bool.and_eq_true, beq_iff_eq] at hc
        obtain ⟨⟨⟨hm, _⟩, hp⟩, _⟩ := hc
        exact Or.inl (Or.inr ⟨p, wordAt_mem (isW_wordAt hp), by rw [hm]⟩)
      · cases h
    | rel p q =>
      simp only [npEnd] at h
      split at h
      · rename_i hc
        simp only [Bool.and_eq_true, beq_iff_eq] at hc
        obtain ⟨⟨⟨hm, hq⟩, _⟩, hr⟩ := hc
        unfold relWord at hr
        split at hr
        · rename_i w hw
          simp only [Bool.and_eq_true, beq_iff_eq] at hr
          exact Or.inr ⟨w, wordAt_mem hw, by rw [hm, hq, hr.1]⟩
        · cases hr
      · cases h

theorem modEnd_cands (D : DDoc) (u : String) (s : List Tok) (i : Nat) (m : Mod) (j : Nat)
    (h : modEnd D u s i m = some j) : m ∈ modCands u s i := by
  cases m with
  | none => exact List.mem_cons_self
  | adj p =>
    simp only [modEnd] at h
    split at h
    · rename_i hc
      simp only [Bool.and_eq_true] at hc
      simp [modCands, isW_wordAt hc.1]
    · cases h
  | slot m =>
    simp only [modEnd] at h
    split at h
    · rename_i hc
      simp only [Bool.and_eq_true, beq_iff_eq] at hc
      simp [modCands, hc.1]
    · cases h

theorem coreEnd_cands (D : DDoc) (u : String) (s : List Tok) (i : Nat) (c : Core) (e : Nat)
    (h : coreEnd D u s i c = some e) : c ∈ coreCands D u s i := by
  unfold coreCands
  simp only [List.mem_append, List.mem_flatMap]
  cases c with
  | pred np are p =>
    simp only [coreEnd] at h
    split at h
    · rename_i j hj
      split at h
      · rename_i hc
        simp only [Bool.and_eq_true] at hc
        refine Or.inl (Or.inl (Or.inl ⟨np, npEnd_cands D u s i np j hj, ?_⟩))
        rw [hj]
        refine List.mem_append_left _ (List.mem_flatMap.mpr ⟨are, by cases are <;> simp, ?_⟩)
        simp [isW_wordAt hc.1.2]
      · cases h
    · cases h
  | coord a ka b kb p =>
    simp only [coreEnd] at h
    split at h
    · rename_i j hj
      split at h
      · split at h
        · rename_i k hk
          split at h
          · rename_i hc
            simp only [Bool.and_eq_true] at hc
            refine Or.inl (Or.inl (Or.inr ⟨(a, ka), name_mem_nameCands hj, ?_⟩))
            simp only [hj]
            refine List.mem_flatMap.mpr ⟨(b, kb), name_mem_nameCands hk, ?_⟩
            simp [hk, isW_wordAt hc.1.2]
          · cases h
        · cases h
      · cases h
    · cases h
  | rel np p obj =>
    simp only [coreEnd] at h
    split at h
    · rename_i j hj
      split at h
      · rename_i hc
        simp only [Bool.and_eq_true] at hc
        refine Or.inl (Or.inl (Or.inl ⟨np, npEnd_cands D u s i np j hj, ?_⟩))
        rw [hj]
        refine List.mem_append_right _ ?_
        simp only [isW_wordAt hc.1, Option.toList_some, List.flatMap_cons, List.flatMap_nil, List.append_nil]
        exact List.mem_map.mpr ⟨obj, npEnd_cands D u s (j + 1) obj e h, rfl⟩
      · cases h
    · cases h
  | every m srt p =>
    simp only [coreEnd] at h
    split at h
    · split at h
      · rename_i j hj
        split at h
        · rename_i hc
          simp only [Bool.and_eq_true] at hc
          refine Or.inl (Or.inr ⟨m, modEnd_cands D u s (i + 1) m j hj, ?_⟩)
          simp [hj, isW_wordAt hc.1.1.1.1, isW_wordAt hc.1.2]
        · cases h
      · cases h
    · cases h
  | some an m srt p =>
    simp only [coreEnd] at h
    split at h
    · split at h
      · rename_i j hj
        split at h
        · rename_i hc
          simp only [Bool.and_eq_true] at hc
          refine Or.inl (Or.inr ⟨m, modEnd_cands D u s (i + 1) m j hj, ?_⟩)
          cases an <;> simp [hj, isW_wordAt hc.1.1.1.1, isW_wordAt hc.1.2]
        · cases h
      · cases h
    · cases h
  | everyDef m srt p sec =>
    simp only [coreEnd] at h
    split at h
    · rename_i hc
      simp only [Bool.and_eq_true, beq_iff_eq] at hc
      split at h
      · rename_i w hw
        split at h
        · rename_i ht
          simp only [Bool.and_eq_true, beq_iff_eq] at ht
          have htail := ht.1.1.1
          have hlen : ((s.drop (i + 1)).take 14).length = 14 := by rw [htail]; rfl
          have hget : ∀ k (hk : k < 14), ((s.drop (i + 1)).take 14)[k]? = (defTail w srt p sec)[k]? := by
            intro k _; rw [htail]
          have h1 : wordAt s (i + 2) = some srt := by
            have := hget 1 (by decide)
            simp only [List.getElem?_take, List.getElem?_drop, defTail] at this
            simp [wordAt, show i + 1 + 1 = i + 2 from rfl] at this ⊢
            simp [this]
          have h3 : wordAt s (i + 4) = some p := by
            have := hget 3 (by decide)
            simp only [List.getElem?_take, List.getElem?_drop, defTail] at this
            simp [wordAt, show i + 1 + 3 = i + 4 by omega] at this ⊢
            simp [this]
          have h13 : wordAt s (i + 14) = some sec := by
            have := hget 13 (by decide)
            simp only [List.getElem?_take, List.getElem?_drop, defTail] at this
            simp [wordAt, show i + 1 + 13 = i + 14 by omega] at this ⊢
            simp [this]
          refine Or.inr ?_
          simp [h1, h3, h13, hc.2]
        · cases h
      · cases h
    · cases h

theorem treeEnd_cands (D : DDoc) (u : String) (s : List Tok) (t : STree) (e : Nat)
    (h : treeEnd D u s t = some e) : t ∈ treeCands D u s := by
  unfold treeCands
  cases t with
  | core c => exact List.mem_append_left _ (List.mem_map.mpr ⟨c, coreEnd_cands D u s 0 c e h, rfl⟩)
  | cite m c =>
    simp only [treeEnd] at h
    split at h
    · rename_i hc
      simp only [Bool.and_eq_true, beq_iff_eq] at hc
      refine List.mem_append_right _ (List.mem_map.mpr ⟨c, coreEnd_cands D u s 4 c e h, ?_⟩)
      rw [hc.1.1.1.2]
    · cases h

/-- The enumerator lists exactly the derivations: the all-derivations gate. -/
theorem mem_derivs (D : DDoc) (u : String) (s : List Tok) (d : DTree) : d ∈ derivs D u s ↔ Derives D u s d := by
  unfold derivs Derives
  simp only [List.mem_map, List.mem_filter]
  constructor
  · rintro ⟨t, ⟨_, hd⟩, rfl⟩
    refine ⟨rfl, ?_⟩
    unfold derivesB at hd
    split at hd
    · rename_i j hj; exact ⟨j, hj, hd⟩
    · cases hd
  · rintro ⟨hs, j, hj, he⟩
    refine ⟨d.tree, ⟨treeEnd_cands D u s d.tree j hj, by simp [derivesB, hj, he]⟩, ?_⟩
    rcases d with ⟨t, sl⟩
    simp only at hs
    rw [hs]

end VE.Discourse
