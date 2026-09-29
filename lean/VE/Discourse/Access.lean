import VE.Discourse.Manifest
import VE.English.Parse

/-! # Accessibility `Acc(D, m, t)` (docs/spec/discourse.md 4.2, 9.2)

An independent relation between a slot and a candidate target, with no nearest-mention,
gender, salience, paragraph-reset or frequency heuristic. Its inputs are exactly: the
registrations, content names, anchors, document table and declarations; the unit table
(ids, spans, kinds) and the lemma names; the slot's unit, span and form; and the text of
the units of the slot's innermost anchor up to the slot (the binders, coordinations and
restrictive properties of the earlier sentences of that anchor and of the slot's own
sentence before it). It never reads another mention, a recorded target or a reading
choice, and sorts play no part (they act only through the type check of 4.3).

Words. The Lean model reads the declared vocabulary by name: a sort's noun is the sort
name, a unary predicate's adjective or noun is its name, a binary predicate `p_of` has
the relational noun `p` and a binary predicate is also a transitive verb under its own
name. The lexer folds every word (`foldChar`), so displays and texts compare case-insensitively. -/
namespace VE.Discourse
open VE.English (Tok)
open VE.Route.Admission (DocUnit Kind)

/-! ## The lexer (a named trust boundary) -/

def punctChar (c : Char) : Bool :=
  c == ',' || c == ';' || c == ':' || c == '!' || c == '?' || c == '(' || c == ')' || c == '"'

/-- The characters that separate words: Python's `str.isspace` (the `\s` of the Python checker's
patterns), so a no-break or other Unicode space separates words as it does for a reader. -/
def spaceChar (c : Char) : Bool :=
  c.isWhitespace || (0x09 ≤ c.val && c.val ≤ 0x0D) || (0x1C ≤ c.val && c.val ≤ 0x1F) || c.val == 0x85 ||
    c.val == 0xA0 || c.val == 0x1680 || (0x2000 ≤ c.val && c.val ≤ 0x200A) || c.val == 0x2028 ||
    c.val == 0x2029 || c.val == 0x202F || c.val == 0x205F || c.val == 0x3000

def wordChar (c : Char) : Bool := !spaceChar c && !punctChar c && c != '.'

/-- The case fold of a character onto a lowercase ASCII letter or digit (`none`: it is neither):
ASCII letters and digits, and the four characters Python's case-insensitive matching equates
with ASCII letters, `İ` and `ı` (i), `ſ` (s) and the Kelvin sign (k). Words and segments are
read through it, in Lean and Python alike (docs/spec/discourse.md 4.1(6)). -/
def foldChar (c : Char) : Option Char :=
  if c.isAlphanum then some c.toLower
  else if c.val == 0x130 || c.val == 0x131 then some 'i'
  else if c.val == 0x17F then some 's'
  else if c.val == 0x212A then some 'k'
  else none

/-- A word with every character that has a fold folded (so `İt` and `ſuch` read `it` and `such`). -/
def foldWord (w : String) : String := w.map fun c => (foldChar c).getD c

def segGo : List Char → Nat → List Char → Nat → List (String × Nat × Nat)
  | [], pos, cur, start => if cur.isEmpty then [] else [(String.mk cur.reverse, start, pos)]
  | c :: rest, pos, cur, start => match foldChar c with
    | some f => segGo rest (pos + c.utf8Size) (f :: cur) (if cur.isEmpty then pos else start)
    | none => (if cur.isEmpty then [] else [(String.mk cur.reverse, start, pos)]) ++
        segGo rest (pos + c.utf8Size) [] 0

/-- The segments of a text (docs/spec/discourse.md 4.1(6)): its maximal runs of characters with a
fold, folded, with their byte ranges `[a, b)`; every other character separates segments. Slot
discovery and the text inputs of `Acc` (binders, restrictive properties, coordinations) read them,
so a word joined to anything else (`service's`, `service’s`, `Bob's`) is still read. -/
def segments (t : String) : List (String × Nat × Nat) := segGo t.toList 0 [] 0

/-- The folded segments of a string. -/
def segmentsOf (w : String) : List String := (segments w).map (·.1)

def charsBytes (cs : List Char) : Nat := cs.foldl (fun n c => n + c.utf8Size) 0

/-- Flush the current word (reversed characters, start byte). -/
def flush (cur : List Char) (start : Nat) : List (String × Nat × Nat) :=
  if cur.isEmpty then [] else [(foldWord (String.mk cur.reverse), start, start + charsBytes cur)]

/-- Tokens with byte ranges `[a, b)` relative to the text: maximal word runs (a `.` between
two alphanumerics stays inside a word, as in `2.1`), single punctuation tokens. -/
def lexGo : List Char → Nat → List Char → Nat → List (String × Nat × Nat)
  | [], _, cur, start => flush cur start
  | c :: rest, pos, cur, start =>
    let next := pos + c.utf8Size
    let inner := c == '.' && (match cur with | p :: _ => p.isAlphanum | [] => false) &&
      (match rest with | n :: _ => n.isAlphanum | [] => false)
    if wordChar c || inner then
      lexGo rest next (c :: cur) (if cur.isEmpty then pos else start)
    else if spaceChar c then flush cur start ++ lexGo rest next [] next
    else flush cur start ++ [(c.toString, pos, next)] ++ lexGo rest next [] next

def lex (s : String) : List (String × Nat × Nat) := lexGo s.toList 0 [] 0

def lexWords (s : String) : List Tok := (lex s).map fun x => .word x.1

/-- The bytes `[a, b)` of a text (unit spans are whole UTF-8 characters, `Loader.cutsCharacter`). -/
def sliceText (t : String) (a b : Nat) : String := (String.fromUTF8? (t.toUTF8.extract a b)).getD ""

/-- The tokens of the text of one unit, `[a, b)` of the prose, with prose byte ranges: every unit
is lexed on its own, so no token joins text across a unit boundary (`Api is reviewed.It is safe.`
as two units is `api is reviewed .` and `it is safe .`). -/
def unitTokens (prose : String) (a b : Nat) : List (String × Nat × Nat) :=
  (lex (sliceText prose a b)).map fun t => (t.1, a + t.2.1, a + t.2.2)

/-! ## Target shapes -/

def entityTarget (c : String) : Target := ⟨.entity, some c, none, [], none, [], none⟩
def binderTarget (i : Nat) : Target := entityTarget ("binder:" ++ toString i)
def listTarget (ms : List String) : Target := ⟨.entity, none, none, ms, none, [], none⟩
def pairTarget (c : String) (p : String × String) : Target := ⟨.entity, some c, none, [], some p, [], none⟩
def predTarget (p : String) : Target := ⟨.predicate, some p, none, [], none, [], none⟩
def unitTarget (us : List String) (cn : Option String) : Target := ⟨.unit, none, none, [], none, us, cn⟩
def namedTarget (k : TargetKind) (n : String) : Target := ⟨k, some n, none, [], none, [], none⟩

/-- A name that is not a local binder name (`binder:<i>`). -/
def notBinder (c : String) : Bool := c.toList.take 7 != "binder:".toList

theorem binder_not_notBinder (i : Nat) : notBinder ("binder:" ++ toString i) = false := by
  simp [notBinder]

theorem binder_inj_zero (i : Nat) (h : "binder:" ++ toString i = "binder:0") : toString i = "0" := by
  have := congrArg String.data h
  simp at this
  exact String.ext this

/-! ## The inputs of `Acc` -/

def unitKey (x : DocUnit) : String × Nat × Nat × Kind := (x.id, x.start, x.stop, x.kind)
def unitKeys (D : DDoc) : List (String × Nat × Nat × Kind) := D.base.units.map unitKey
def unitIds (D : DDoc) : List String := (unitKeys D).map (·.1)
def lemmaNames (D : DDoc) : List String := D.base.lemmas.map (·.name)

def unitSpan (D : DDoc) (u : String) : Option (Nat × Nat) :=
  ((unitKeys D).find? (·.1 == u)).map fun k => (k.2.1, k.2.2.1)

def anchorOf (D : DDoc) (a : String) : Option Anchor := D.K.anchors.find? (·.id == a)

/-- The unit lies inside the anchor's span. -/
def within (D : DDoc) (unit anchor : String) : Bool :=
  match unitSpan D unit, anchorOf D anchor with
  | some (b, e), some a => a.span.1 ≤ b && e ≤ a.span.2
  | _, _ => false

def narrower (best : Option Anchor) (a : Anchor) : Option Anchor :=
  match best with
  | none => some a
  | some b => if a.span.2 - a.span.1 < b.span.2 - b.span.1 then some a else some b

/-- The smallest anchor containing the unit (the first of equal size). -/
def innermostAnchor (D : DDoc) (unit : String) : Option Anchor :=
  (D.K.anchors.filter fun a => within D unit a.id).foldl narrower none

/-- The registration of a constant (binder names are never constants). -/
def registered (D : DDoc) (c : String) : Option Name :=
  if notBinder c then D.K.names.find? (·.constant == c) else none

def sortOf (E : VE.Environment) (c : String) : Option String := E.constants c

/-- The units before `u` in document order. -/
def unitIdsBefore (D : DDoc) (u : String) : List String := (unitIds D).takeWhile (· != u)

/-- The earlier sentences of the slot's innermost anchor. -/
def earlierUnits (D : DDoc) (m : Slot) : List String :=
  match innermostAnchor D m.unit with
  | none => []
  | some a => (unitIdsBefore D m.unit).filter fun v => within D v a.id

/-- The slot's own sentence (read only inside an anchor). -/
def ownText (D : DDoc) (m : Slot) : List Tok :=
  match innermostAnchor D m.unit with
  | none => []
  | some _ => (D.text m.unit).getD []

/-- The text of a unit: its bytes of the prose. -/
def unitString (D : DDoc) (u : String) : Option String :=
  (unitOf D.base u).map fun x => sliceText D.prose x.start x.stop

/-- The slot's own sentence before the slot: its unit's bytes before the slot's first token (read
only inside an anchor). -/
def ownPrefix (D : DDoc) (m : Slot) : String :=
  match innermostAnchor D m.unit, unitString D m.unit with
  | some _, some t => sliceText t 0 ((((lex t)[m.span.1]?).map (·.2.1)).getD t.utf8ByteSize)
  | _, _ => ""

/-- The segment lists `Acc` reads: every earlier sentence of the innermost anchor, then the
slot's own sentence up to the slot. -/
def scopeSegments (D : DDoc) (m : Slot) : List (List String) :=
  (earlierUnits D m).map (fun v => ((unitString D v).map segmentsOf).getD []) ++ [segmentsOf (ownPrefix D m)]

def wordAt (ts : List Tok) (i : Nat) : Option String :=
  match ts[i]? with
  | some (.word w) => some w
  | _ => none

def sortWord (E : VE.Environment) (w : String) : Bool := E.sorts.contains w

/-- A word of a sort, as the lexer reads it: a sort's name or a declared singular noun, folded. -/
def sortNoun (D : DDoc) (w : String) : Bool := sortWord D.E w || D.nouns.any fun n => foldWord n.2 == w

def unaryPred (E : VE.Environment) (p : String) : Bool :=
  match E.predicates p with
  | some [_] => true
  | _ => false

def binaryPred (E : VE.Environment) (p : String) : Bool :=
  match E.predicates p with
  | some [_, _] => true
  | _ => false

def quantifierWords : List String := ["every", "a", "an", "some"]

/-- A symbol name split into segments is spelled by its `_`-joined segments (identifiers are
`[a-z][a-z0-9_]*`, at most 64 bytes, so at most 32 segments). -/
def joinLimit : Nat := 32

/-- `a` occurs contiguously in `b`. -/
def infixS (a b : List String) : Bool := (List.range (b.length + 1)).any fun i => a.isPrefixOf (b.drop i)

/-- The words of sort `s` as segments: its name and its declared singular nouns. -/
def sortPhrases (D : DDoc) (s : String) : List (List String) :=
  ((s :: (D.nouns.filter (·.1 == s)).map (·.2)).map segmentsOf).filter (!·.isEmpty)

/-- A binder of sort `s` in the segments `ws`: a quantifier word followed, later in the same text,
by a word of `s`, whatever lies between (`A big red service`, `A service's owner`). -/
def bindsSort (D : DDoc) (ws : List String) (s : String) : Bool :=
  (List.range ws.length).any fun j => (ws[j]?).any quantifierWords.contains &&
    (sortPhrases D s).any fun p => infixS p (ws.drop (j + 1))

/-- The registered spellings of a name, as the lexer's words (the grammar reads names by them). -/
def spellings (n : Name) : List (List Tok) := (n.display :: n.aliases).map lexWords

/-- The registered spellings of a name, as segments. -/
def spellingSegments (n : Name) : List (List String) :=
  ((n.display :: n.aliases).map segmentsOf).filter (!·.isEmpty)

/-- The coordinations "c₁ and c₂" of those sentences, read as segments: an input of `Acc`. -/
def earlierPairs (D : DDoc) (m : Slot) : List (String × String) :=
  D.K.names.flatMap fun n₁ => D.K.names.flatMap fun n₂ =>
    if (scopeSegments D m).any (fun ws => (spellingSegments n₁).any fun a => (spellingSegments n₂).any fun b =>
        infixS (a ++ ["and"] ++ b) ws)
    then [(n₁.constant, n₂.constant)] else []

/-- The restrictive properties at segment `j`: a quantifier word, the segments of a unary
predicate (`_`-joined) and a word of a sort, as (predicate, sort). -/
def propertiesAt (D : DDoc) (ws : List String) (j : Nat) : List (String × String) :=
  if (ws[j]?).any quantifierWords.contains then
    let after := ws.drop (j + 1)
    (List.range (min after.length joinLimit)).flatMap fun k =>
      let p := "_".intercalate (after.take (k + 1))
      if unaryPred D.E p then D.E.sorts.filter (fun s => (sortPhrases D s).any (·.isPrefixOf (after.drop (k + 1))))
        |>.map (p, ·)
      else []
  else []

/-- (predicate, noun sort) applied restrictively in those sentences: an input of `Acc`. -/
def earlierProperties (D : DDoc) (m : Slot) : List (String × String) :=
  (scopeSegments D m).flatMap fun ws => (List.range ws.length).flatMap (propertiesAt D ws)

/-- A binder of the sort in the earlier sentences of the innermost anchor or earlier in the slot's
own sentence: an input of `Acc`. -/
def competingQuantifier (D : DDoc) (m : Slot) (sort : String) : Bool :=
  (scopeSegments D m).any fun ws => bindsSort D ws sort

/-- Binder `i` of the slot's own sentence scopes over the slot: the one binder a definite
description introduces is its own described entity, `binder:0`. -/
def binderScopes (_D : DDoc) (m : Slot) (i : Nat) : Bool := m.form == .definite && toString i == "0"

/-- `the former` selects member 1, `the latter` member 2. -/
def ordinalIndex (D : DDoc) (m : Slot) : Option Nat :=
  match wordAt (ownText D m) (m.span.1 + 1) with
  | some "former" => some 1
  | some "latter" => some 2
  | _ => none

/-- The anchor a `definition_ref` names: `... defined in section <label>` in the own sentence. -/
def sectionLabel : List Tok → Option String
  | .word "defined" :: .word "in" :: .word "section" :: .word l :: _ => some l
  | _ :: rest => sectionLabel rest
  | [] => none

def namedSection (D : DDoc) (m : Slot) : Option Anchor :=
  (sectionLabel (ownText D m)).bind fun l => D.K.anchors.find? (·.label.toLower == l)

def candidateSort (D : DDoc) (m : Slot) (t : Target) : Option (List String) :=
  match t.kind, t.name, t.members with
  | .entity, some c, _ => if notBinder c then (sortOf D.E c).map ([·]) else none
  | .entity, none, ms => ms.mapM (sortOf D.E)
  | .predicate, some p, _ => match D.E.predicates p with
    | some [s] => some [s]
    | _ => none
  | _, _, _ => none

def formFits : Form → TargetKind → Bool
  | .pronoun, .entity | .pronoun, .unit | .demonstrative, .entity | .demonstrative, .unit
  | .definite, .entity | .ordinalPair, .entity | .such, .predicate | .possessive, .entity
  | .plural, .entity | .sectionRef, .anchor | .sectionRef, .unit | .sectionRef, .rule
  | .definitionRef, .predicate | .documentName, .document | .citation, .claim
  | .navigation, .anchor | .navigation, .unit => true
  | _, _ => false

/-- A registered constant whose scope contains the slot's unit. -/
def constAcc (D : DDoc) (m : Slot) (c : String) : Bool :=
  notBinder c && match registered D c with
    | some n => within D m.unit n.scope
    | none => false

def pronounLike (f : Form) : Bool := f == .pronoun || f == .demonstrative

/-- Every sublist of a list, in order. -/
def subs {α : Type} : List α → List (List α)
  | [] => [[]]
  | x :: xs => subs xs ++ (subs xs).map (x :: ·)

/-- Every list of length `n` over a pool. -/
def tuplesOf {α : Type} (pool : List α) : Nat → List (List α)
  | 0 => [[]]
  | n + 1 => pool.flatMap fun x => (tuplesOf pool n).map (x :: ·)

/-- 4.2 as a Boolean on the target's shape; `Acc` is its truth. -/
def accB (D : DDoc) (m : Slot) (t : Target) : Bool :=
  formFits m.form t.kind && match t with
  | ⟨.entity, some c, none, [], none, [], none⟩ =>
    if notBinder c then
      (pronounLike m.form || m.form == .possessive) && constAcc D m c &&
        (!pronounLike m.form || match sortOf D.E c with
          | some s => !competingQuantifier D m s
          | none => false)
    else c == "binder:0" && m.form == .definite
  | ⟨.entity, none, none, ms, none, [], none⟩ =>
    m.form == .plural && (earlierPairs D m).any (fun p => ms == [p.1, p.2]) && decide ms.Nodup &&
      ms.all (constAcc D m)
  | ⟨.entity, some c, none, [], some p, [], none⟩ =>
    m.form == .ordinalPair && (earlierPairs D m).contains p && constAcc D m p.1 && constAcc D m p.2 &&
      match ordinalIndex D m with
      | some 1 => c == p.1
      | some 2 => c == p.2
      | _ => false
  | ⟨.predicate, some p, none, [], none, [], none⟩ =>
    unaryPred D.E p && (
      (m.form == .such && (earlierProperties D m).any (·.1 == p)) ||
      (m.form == .definitionRef && wordAt (ownText D m) m.span.1 == some p && match namedSection D m with
        | some a => a.exports.contains p
        | none => false))
  | ⟨.unit, none, none, [], none, us, cn⟩ =>
    !us.isEmpty && (subs (unitIds D)).contains us && match cn with
      | none => true
      | some n => D.K.contentNames.any fun c => c.name == n && c.units == us
  | ⟨.anchor, some a, none, [], none, [], none⟩ => (anchorOf D a).isSome
  | ⟨.rule, some r, none, [], none, [], none⟩ => (unitKeys D).any fun k => k.1 == r && decide (k.2.2.2 = .norm)
  | ⟨.claim, some l, none, [], none, [], none⟩ => (lemmaNames D).contains l
  | ⟨.document, some d, none, [], none, [], none⟩ => D.K.documents.any fun x => x.name == d &&
      x.display.any fun s => lexWords s == ((ownText D m).drop m.span.1).take (m.span.2 - m.span.1)
  | _ => false

/-- 4.2: the accessibility relation. -/
def Acc (D : DDoc) (m : Slot) (t : Target) : Prop := accB D m t = true

instance (D : DDoc) (m : Slot) (t : Target) : Decidable (Acc D m t) := inferInstanceAs (Decidable (_ = _))

/-- Every candidate target of every shape `Acc` can accept, part by part. -/
def candidateParts (D : DDoc) (m : Slot) : List (List Target) :=
  let consts := D.K.names.map Name.constant
  [consts.map entityTarget,
   [entityTarget "binder:0"],
   (earlierPairs D m).map (fun p => listTarget [p.1, p.2]),
   (earlierPairs D m).flatMap (fun p => [pairTarget p.1 p, pairTarget p.2 p]),
   (earlierProperties D m).map (fun p => predTarget p.1),
   (match namedSection D m with | some a => a.exports.map predTarget | none => []),
   (subs (unitIds D)).flatMap (fun us => unitTarget us none :: D.K.contentNames.map (fun c => unitTarget us (some c.name))),
   D.K.anchors.map (fun a => namedTarget .anchor a.id),
   (unitKeys D).map (fun k => namedTarget .rule k.1),
   (lemmaNames D).map (namedTarget .claim),
   D.K.documents.map (fun d => namedTarget .document d.name)]

def candidates (D : DDoc) (m : Slot) : List Target := (candidateParts D m).flatten

def accessible (D : DDoc) (m : Slot) : List Target := (candidates D m).filter (accB D m)

/-- The canonical form of a target modulo declared aliases. Targets name constants, never the
spelling a mention used, so a declared alias never changes a target and the canonical form is
the target itself; in particular two plurals with the same members in another order are two
targets (a plural's candidates are the coordinations of the text, in their order, 4.2). -/
def canonTarget (_D : DDoc) (t : Target) : Target := t

/-- Equal modulo declared aliases (4.3), which for constant-naming targets is equality. -/
def AliasEq (D : DDoc) (t t' : Target) : Prop := canonTarget D t = canonTarget D t'

instance (D : DDoc) (t t' : Target) : Decidable (AliasEq D t t') := inferInstanceAs (Decidable (_ = _))

/-! ## Proofs (9.2) -/

theorem mem_subs {α : Type} (l : List α) : ∀ xs : List α, l ∈ subs xs ↔ l.Sublist xs
  | [] => by
    simp only [subs, List.mem_singleton]
    exact ⟨fun h => h ▸ List.Sublist.slnil, fun h => List.sublist_nil.mp h⟩
  | x :: xs => by
    simp only [subs, List.mem_append, List.mem_map]
    constructor
    · rintro (h | ⟨l', h, rfl⟩)
      · exact ((mem_subs l xs).mp h).cons x
      · exact ((mem_subs l' xs).mp h).cons₂ x
    · intro h
      cases h with
      | cons _ h => exact Or.inl ((mem_subs l xs).mpr h)
      | cons₂ _ h => exact Or.inr ⟨_, (mem_subs _ xs).mpr h, rfl⟩

theorem mem_tuplesOf {α : Type} (pool : List α) : ∀ (n : Nat) (l : List α),
    l ∈ tuplesOf pool n ↔ l.length = n ∧ ∀ x ∈ l, x ∈ pool
  | 0, l => by
    simp only [tuplesOf, List.mem_singleton]
    constructor
    · rintro rfl; simp
    · rintro ⟨h, _⟩; exact List.length_eq_zero_iff.mp h
  | n + 1, l => by
    simp only [tuplesOf, List.mem_flatMap, List.mem_map]
    constructor
    · rintro ⟨x, hx, l', hl', rfl⟩
      obtain ⟨h1, h2⟩ := (mem_tuplesOf pool n l').mp hl'
      refine ⟨by simp [h1], fun y hy => ?_⟩
      rcases List.mem_cons.mp hy with rfl | hy
      · exact hx
      · exact h2 y hy
    · rintro ⟨h1, h2⟩
      cases l with
      | nil => simp at h1
      | cons x l' =>
        exact ⟨x, h2 x (by simp), l', (mem_tuplesOf pool n l').mpr ⟨by simpa using h1,
          fun y hy => h2 y (by simp [hy])⟩, rfl⟩

theorem nodup_length_le {α : Type} [DecidableEq α] : ∀ (ms l : List α), ms.Nodup → (∀ x ∈ ms, x ∈ l) →
    ms.length ≤ l.length
  | [], _, _, _ => Nat.zero_le _
  | x :: ms, l, hn, hs => by
    have hx : x ∈ l := hs x (by simp)
    have hn' := List.nodup_cons.mp hn
    have := nodup_length_le ms (l.erase x) hn'.2 (fun y hy => by
      have hne : y ≠ x := fun e => hn'.1 (e ▸ hy)
      exact (List.mem_erase_of_ne hne).mpr (hs y (by simp [hy])))
    rw [List.length_erase_of_mem hx] at this
    have hpos : 0 < l.length := List.length_pos_of_mem hx
    simp only [List.length_cons]
    omega

theorem registered_some {D : DDoc} {c : String} {n : Name} (h : registered D c = some n) :
    n ∈ D.K.names ∧ n.constant = c ∧ notBinder c = true := by
  unfold registered at h
  split at h
  · rename_i hb
    have := List.find?_some h
    exact ⟨List.mem_of_find?_eq_some h, by simpa using this, hb⟩
  · cases h

theorem constAcc_mem {D : DDoc} {m : Slot} {c : String} (h : constAcc D m c = true) :
    c ∈ D.K.names.map Name.constant := by
  unfold constAcc at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨_, h⟩ := h
  split at h
  · rename_i n hn
    obtain ⟨hm, hc, _⟩ := registered_some hn
    exact List.mem_map.mpr ⟨n, hm, hc⟩
  · cases h

theorem mem_candidates {D : DDoc} {m : Slot} {t : Target} (P : List Target) (hP : P ∈ candidateParts D m)
    (h : t ∈ P) : t ∈ candidates D m := List.mem_flatten.mpr ⟨P, hP, h⟩

theorem accB_candidates (D : DDoc) (m : Slot) (t : Target) (h : accB D m t = true) : t ∈ candidates D m := by
  unfold accB at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨hfit, h⟩ := h
  split at h
  · rename_i c
    split at h
    · simp only [Bool.and_eq_true] at h
      exact mem_candidates ((D.K.names.map Name.constant).map entityTarget) (by simp [candidateParts])
        (List.mem_map.mpr ⟨c, constAcc_mem h.1.2, rfl⟩)
    · simp only [Bool.and_eq_true, beq_iff_eq] at h
      rw [h.1]
      exact mem_candidates [entityTarget "binder:0"] (by simp [candidateParts]) (List.mem_singleton_self _)
  · rename_i ms
    simp only [Bool.and_eq_true, List.any_eq_true, beq_iff_eq] at h
    obtain ⟨⟨⟨_, p, hp, rfl⟩, _⟩, _⟩ := h
    exact mem_candidates ((earlierPairs D m).map (fun p => listTarget [p.1, p.2]))
      (by simp [candidateParts]) (List.mem_map.mpr ⟨p, hp, rfl⟩)
  · rename_i c p
    simp only [Bool.and_eq_true, List.contains_iff_mem] at h
    obtain ⟨⟨⟨⟨_, hp⟩, _⟩, _⟩, hk⟩ := h
    refine mem_candidates ((earlierPairs D m).flatMap (fun p => [pairTarget p.1 p, pairTarget p.2 p]))
      (by simp [candidateParts]) (List.mem_flatMap.mpr ⟨p, hp, ?_⟩)
    split at hk
    · simp only [beq_iff_eq] at hk; subst hk; simp [pairTarget]
    · simp only [beq_iff_eq] at hk; subst hk; simp [pairTarget]
    · cases hk
  · rename_i p
    simp only [Bool.and_eq_true, Bool.or_eq_true] at h
    obtain ⟨_, h | h⟩ := h
    · simp only [List.any_eq_true, beq_iff_eq] at h
      obtain ⟨_, x, hx, rfl⟩ := h
      exact mem_candidates ((earlierProperties D m).map (fun p => predTarget p.1)) (by simp [candidateParts])
        (List.mem_map.mpr ⟨x, hx, rfl⟩)
    · obtain ⟨⟨_, _⟩, h⟩ := h
      split at h
      · rename_i a ha
        refine mem_candidates (a.exports.map predTarget) (by simp [candidateParts, ha]) ?_
        exact List.mem_map.mpr ⟨p, List.contains_iff_mem.mp h, rfl⟩
      · cases h
  · rename_i us cn
    simp only [Bool.and_eq_true, List.contains_iff_mem] at h
    obtain ⟨⟨_, hs⟩, hc⟩ := h
    refine mem_candidates ((subs (unitIds D)).flatMap (fun us => unitTarget us none ::
      D.K.contentNames.map (fun c => unitTarget us (some c.name)))) (by simp [candidateParts])
      (List.mem_flatMap.mpr ⟨us, hs, ?_⟩)
    cases cn with
    | none => exact List.mem_cons_self
    | some n =>
      simp only [List.any_eq_true, Bool.and_eq_true, beq_iff_eq] at hc
      obtain ⟨c, hc, rfl, _⟩ := hc
      exact List.mem_cons_of_mem _ (List.mem_map.mpr ⟨c, hc, rfl⟩)
  · rename_i a
    obtain ⟨x, hx⟩ := Option.isSome_iff_exists.mp h
    have hm := List.mem_of_find?_eq_some hx
    have he : x.id = a := by simpa using List.find?_some hx
    exact mem_candidates (D.K.anchors.map (fun a => namedTarget .anchor a.id)) (by simp [candidateParts])
      (List.mem_map.mpr ⟨x, hm, by rw [he]; rfl⟩)
  · rename_i r
    simp only [List.any_eq_true, Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨k, hk, rfl, _⟩ := h
    exact mem_candidates ((unitKeys D).map (fun k => namedTarget .rule k.1)) (by simp [candidateParts])
      (List.mem_map.mpr ⟨k, hk, rfl⟩)
  · rename_i l
    exact mem_candidates ((lemmaNames D).map (namedTarget .claim)) (by simp [candidateParts])
      (List.mem_map.mpr ⟨l, List.contains_iff_mem.mp h, rfl⟩)
  · rename_i d
    simp only [List.any_eq_true, Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨x, hx, rfl, _⟩ := h
    exact mem_candidates (D.K.documents.map (fun d => namedTarget .document d.name)) (by simp [candidateParts])
      (List.mem_map.mpr ⟨x, hx, rfl⟩)
  · cases h

/-- The list and the relation agree. -/
theorem accessible_iff (D : DDoc) (m : Slot) (t : Target) : t ∈ accessible D m ↔ Acc D m t := by
  unfold accessible Acc
  rw [List.mem_filter]
  exact ⟨fun h => h.2, fun h => ⟨accB_candidates D m t h, h⟩⟩

/-- Neither the recorded targets nor the reading choices are inputs of Acc (no pruning). -/
theorem acc_ignores_manifest_choices (D : DDoc) (m : Slot) (t : Target) (ms : List Mention)
    (ρ : List (String × Nat × Nat)) :
    Acc D m t ↔ Acc { D with K := { D.K with mentions := ms, choices := ρ } } m t := Iff.rfl

/-- Witness scope: a binder target is accessible only inside its own sentence and under its scope. -/
theorem no_witness_escape (D : DDoc) (m : Slot) (i : Nat)
    (h : ¬ binderScopes D m i) : ¬ Acc D m ⟨.entity, some ("binder:" ++ toString i), none, [], none, [], none⟩ := by
  intro ha
  unfold Acc accB at ha
  simp only [Bool.and_eq_true, binder_not_notBinder, Bool.false_eq_true, if_false, beq_iff_eq] at ha
  obtain ⟨_, hc, hf⟩ := ha
  apply h
  simp [binderScopes, hf, binder_inj_zero i hc]

/-- Names are scope-based, not distance-based: a registered constant is accessible at every unit of
its scope without a competing quantifier of its sort, and at no unit outside it. -/
theorem name_scope (D : DDoc) (m : Slot) (c s : String) (n : Name) (hn : registered D c = some n)
    (hs : sortOf D.E c = some s) (hf : m.form = .pronoun ∨ m.form = .demonstrative) :
    Acc D m ⟨.entity, some c, none, [], none, [], none⟩ ↔
      within D m.unit n.scope = true ∧ competingQuantifier D m s = false := by
  obtain ⟨_, _, hb⟩ := registered_some hn
  have hp : pronounLike m.form = true := by rcases hf with h | h <;> simp [pronounLike, h]
  have hfit : formFits m.form .entity = true := by rcases hf with h | h <;> simp [formFits, h]
  unfold Acc accB
  simp only [hfit, hb, if_true, hp, Bool.true_or, Bool.true_and, Bool.not_true, Bool.false_or, hs,
    constAcc, hn]
  simp

/-- Kinds never coerce. -/
theorem kind_fit (D : DDoc) (m : Slot) (t : Target) (h : Acc D m t) : formFits m.form t.kind = true := by
  unfold Acc accB at h
  simp only [Bool.and_eq_true] at h
  exact h.1

theorem narrower_mem : ∀ (l : List Anchor) (best : Option Anchor) (a : Anchor),
    l.foldl narrower best = some a → best = some a ∨ a ∈ l
  | [], best, a, h => Or.inl h
  | x :: xs, best, a, h => by
    rcases narrower_mem xs (narrower best x) a h with h' | h'
    · unfold narrower at h'
      split at h'
      · cases h'; exact Or.inr List.mem_cons_self
      · split at h'
        · cases h'; exact Or.inr List.mem_cons_self
        · exact Or.inl h'
    · exact Or.inr (List.mem_cons_of_mem _ h')

theorem innermost_within {D : DDoc} {u : String} {a : Anchor} (h : innermostAnchor D u = some a) :
    within D u a.id = true := by
  unfold innermostAnchor at h
  rcases narrower_mem _ none a h with h | h
  · cases h
  · exact (List.mem_filter.mp h).2

/-- No heuristic: accessibility depends only on registrations, content names, anchors,
declarations (with the sorts' declared nouns), the unit table and lemma names, the slot's unit,
span and form, own-sentence binders, and the binders, coordinations and restrictive properties of
the earlier sentences of the innermost anchor (4.2), read from those sentences' tokens and bytes. -/
theorem acc_no_heuristic (D D₂ : DDoc) (m : Slot) (t : Target)
    (hK : D.K.names = D₂.K.names ∧ D.K.contentNames = D₂.K.contentNames ∧ D.K.anchors = D₂.K.anchors ∧
          D.K.documents = D₂.K.documents ∧ D.K.definitionsVersion = D₂.K.definitionsVersion ∧ D.E = D₂.E)
    (hN : D.nouns = D₂.nouns)
    (ha : innermostAnchor D m.unit = innermostAnchor D₂ m.unit)
    (ht : ∀ a u, innermostAnchor D m.unit = some a → within D u a.id = true → D.text u = D₂.text u)
    (hp : ∀ a u, innermostAnchor D m.unit = some a → within D u a.id = true → unitString D u = unitString D₂ u)
    (hb : unitKeys D = unitKeys D₂ ∧ lemmaNames D = lemmaNames D₂) :
    Acc D m t ↔ Acc D₂ m t := by
  obtain ⟨hn, hc, han, hd, _, hE⟩ := hK
  have hw : ∀ u a, within D u a = within D₂ u a := by
    intro u a
    simp only [within, unitSpan, anchorOf, hb.1, han]
  have hi : ∀ u, innermostAnchor D u = innermostAnchor D₂ u := by
    intro u
    unfold innermostAnchor
    rw [han]
    congr 1
    exact List.filter_congr (fun a _ => hw u a.id)
  have hu : unitIds D = unitIds D₂ := by simp only [unitIds, hb.1]
  have hown : ownText D m = ownText D₂ m := by
    unfold ownText
    rw [← hi]
    cases hx : innermostAnchor D m.unit with
    | none => rfl
    | some a => simp only [ht a m.unit hx (innermost_within hx)]
  have hpre : ownPrefix D m = ownPrefix D₂ m := by
    unfold ownPrefix
    rw [← hi]
    cases hx : innermostAnchor D m.unit with
    | none => rfl
    | some a => simp only [hp a m.unit hx (innermost_within hx)]
  have heu : earlierUnits D m = earlierUnits D₂ m := by
    unfold earlierUnits
    rw [← hi]
    cases innermostAnchor D m.unit with
    | none => rfl
    | some a => simp only [unitIdsBefore, hu, hw]
  have hs : scopeSegments D m = scopeSegments D₂ m := by
    unfold scopeSegments
    rw [← heu, hpre]
    congr 1
    apply List.map_congr_left
    intro v hv
    unfold earlierUnits at hv
    cases hx : innermostAnchor D m.unit with
    | none => rw [hx] at hv; cases hv
    | some a =>
      rw [hx] at hv
      rw [hp a v hx (List.mem_filter.mp hv).2]
  have hsp : sortPhrases D = sortPhrases D₂ := by funext s; simp only [sortPhrases, hN]
  have hbs : bindsSort D = bindsSort D₂ := by funext ws s; simp only [bindsSort, hsp]
  have hpa : propertiesAt D = propertiesAt D₂ := by funext ws j; simp only [propertiesAt, hsp, hE]
  have hpairs : earlierPairs D m = earlierPairs D₂ m := by simp only [earlierPairs, hs, hn]
  have hprops : earlierProperties D m = earlierProperties D₂ m := by simp only [earlierProperties, hs, hpa]
  have hord : ordinalIndex D m = ordinalIndex D₂ m := by simp only [ordinalIndex, hown]
  have hsec : namedSection D m = namedSection D₂ m := by simp only [namedSection, hown, han]
  have hreg : ∀ c, registered D c = registered D₂ c := by intro c; simp only [registered, hn]
  have hconst : ∀ c, constAcc D m c = constAcc D₂ m c := by intro c; simp only [constAcc, hreg, hw]
  have hcq : ∀ s, competingQuantifier D m s = competingQuantifier D₂ m s := by
    intro s; simp only [competingQuantifier, hs, hbs]
  have hanc : ∀ a, anchorOf D a = anchorOf D₂ a := by intro a; simp only [anchorOf, han]
  have hconstf : constAcc D m = constAcc D₂ m := funext hconst
  unfold Acc accB
  simp only [hconstf, hconst, hpairs, hprops, hord, hsec, hcq, hu, hanc, hE, hc, hd, hb.1, hb.2, hown]

end VE.Discourse
