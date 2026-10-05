import VE.EnglishGrammar.Token
import VE.EnglishGrammar.Syntax

/-! The English lexer (docs/spec/english-lean.md 2.2; tier B). A definition with no theorem: it is part of
the trusted base.

`lexSpans` reads a source left to right, one character at a time, and returns its sentences as tokens
with their UTF-8 byte spans, or the first rejection; `lex` erases the spans. The choices that S0 fixed
(docs/spec/english-lean-measured.md section 4, on branch `english-lean/py`) are those of the Python
reference `conformance/english_lean_lexer.py`:

- whitespace is the literal list of the 29 code points of Python's `str.isspace` (spec O3);
- offsets in rejections are UTF-8 byte offsets; `emptySentence` carries the sentence index;
- a quoted identifier keeps the characters between its quotes exactly, escapes included;
- a list marker `(a)` `(b)` `(i)` `(ii)` is one token only when written without inner spaces;
- a word is initial when it is the first token of its sentence, or when the tokens before it are
  exactly a conclusion marker (`therefore`, `so`, `hence`, `it follows that`, the first word possibly
  capitalised, as the `kw` terminal accepts it).

The `glued` flags (DRI ruling on O1, 2026-10-04). A punctuation token records whether a character that
is not whitespace comes right before it (`gluedBefore`) and right after it (`gluedAfter`) in the
source, the terminator included. So `deployed, it` and `deployed , it` lex differently, as do
`non-compliant` and `non - compliant`, and the rules decide which spacing they accept.
-/

namespace VE.EnglishGrammar

/-- The limits of the source, as today (`MAX_SOURCE_BYTES`, `MAX_NODES`). -/
def maxSourceBytes : Nat := 65536
def maxTextChars : Nat := 10000

/-- The 29 code points for which Python's `str.isspace` is true (spec O3). -/
def spaceCodes : List Nat :=
  [0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x85, 0xA0, 0x1680,
   0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008, 0x2009, 0x200A,
   0x2028, 0x2029, 0x202F, 0x205F, 0x3000]

def isSpace (c : Char) : Bool := spaceCodes.contains c.val.toNat

/-- A character of a chunk: an ASCII letter or digit, `_`, or a character outside ASCII that is not
whitespace. -/
def chunkChar (c : Char) : Bool :=
  if c.val < 128 then c.isAlphanum || c == '_' else !isSpace c

/-- The punctuation characters that are one token each. `.` is the terminator. -/
def punctChars : List Char := [',', ';', ':', '(', ')', '[', ']', '+', '-', '*']

/-- The list markers, longest first where one is a prefix of another. -/
def markers : List String := ["(ii)", "(a)", "(b)", "(i)"]

/-- The length of the source after every whitespace run outside quotes became one space. The state
is: in quotes, after an escape, after whitespace. -/
def collapsedGo : List Char → Bool → Bool → Bool → Nat → Nat
  | [], _, _, _, n => n
  | c :: cs, quoted, escaped, prevSpace, n =>
    if !quoted && isSpace c then collapsedGo cs quoted escaped true (if prevSpace then n else n + 1)
    else if quoted then
      if escaped then collapsedGo cs true false false (n + 1)
      else if c == '\\' then collapsedGo cs true true false (n + 1)
      else if c == '"' then collapsedGo cs false false false (n + 1)
      else collapsedGo cs true false false (n + 1)
    else collapsedGo cs (c == '"') false false (n + 1)

def collapsedLength (s : String) : Nat := collapsedGo s.toList false false false 0

/-- The digits of a chunk as a number, when every character is an ASCII digit and there is one. -/
def digitsValue (cs : List Char) : Option Nat :=
  if !cs.isEmpty && cs.all Char.isDigit then
    some (cs.foldl (fun n c => 10 * n + (c.toNat - '0'.toNat)) 0)
  else none

/-- The token of a chunk that starts at the byte offset `start`. -/
def chunkToken (cs : List Char) (start : Nat) : Except Reject Tok :=
  match digitsValue cs with
  | some v =>
    if cs.length > 1 && cs.head? == some '0' then .error (.badNumeral start) else .ok (.numeral v)
  | none =>
    let letters := cs.takeWhile fun c => 'A' ≤ c && c ≤ 'Z'
    let rest := cs.drop letters.length
    match digitsValue rest with
    | some v =>
      if !letters.isEmpty && cs.all (fun c => c.val < 128) && rest.head? != some '0' then
        .ok (.label (String.mk letters) v)
      else .ok (.word (String.mk cs) false)
    | none => .ok (.word (String.mk cs) false)

/-- A token with its byte span. -/
abbrev Spanned := Tok × Nat × Nat

/-- What the scanner is in the middle of. -/
inductive Mode where
  | normal
  | quote (start : Nat) (escaped : Bool) (acc : List Char)
  | chunk (start : Nat) (acc : List Char)
  | skip (k : Nat)

/-- The scanner's state: the finished sentences, the current one, the mode. -/
structure Scan where
  sents : Array (Array Spanned)
  cur : Array Spanned
  mode : Mode

/-- Whether `cs` starts with the characters of `m`. -/
def startsWith (cs : List Char) (m : String) : Bool := m.toList.isPrefixOf cs

/-- The marker that the characters `c :: cs` start with, if any. -/
def markerAt (c : Char) (cs : List Char) : Option String :=
  markers.find? fun m => startsWith (c :: cs) m

/-- Whether a character that is not whitespace is the given one. -/
def solid : Option Char → Bool
  | some c => !isSpace c
  | none => false

/-- Reads the character `c` at the byte offset `pos` in normal mode; `prev` is the character before
it and `cs` the characters after it. -/
def normalStep (st : Scan) (prev : Option Char) (c : Char) (cs : List Char) (pos : Nat) :
    Except Reject Scan :=
  if isSpace c then .ok st
  else if c == '"' then .ok { st with mode := .quote pos false [] }
  else if chunkChar c then .ok { st with mode := .chunk pos [c] }
  else if c == '.' then
    if st.cur.isEmpty then .error (.emptySentence st.sents.size)
    else .ok { st with sents := st.sents.push st.cur, cur := #[] }
  else match markerAt c cs with
    | some m =>
      let after := (cs.drop (m.length - 1)).head?
      .ok { st with cur := st.cur.push (.punct m (solid prev) (solid after), pos, pos + m.length),
                    mode := .skip (m.length - 1) }
    | none =>
      if punctChars.contains c then
        .ok { st with cur := st.cur.push (.punct (String.singleton c) (solid prev) (solid cs.head?), pos, pos + 1) }
      else .error (.badCharacter pos)

/-- Ends a chunk at the byte offset `pos`. -/
def endChunk (st : Scan) (start : Nat) (acc : List Char) (pos : Nat) : Except Reject Scan :=
  match chunkToken acc.reverse start with
  | .ok t => .ok { st with cur := st.cur.push (t, start, pos), mode := .normal }
  | .error r => .error r

/-- Reads the characters `c :: cs`, the first at the byte offset `pos`. -/
def scanGo : Scan → Option Char → List Char → Nat → Except Reject Scan
  | st, _, [], _ => .ok st
  | st, prev, c :: cs, pos =>
    let next := pos + c.utf8Size
    match st.mode with
    | .skip k =>
      scanGo { st with mode := if k ≤ 1 then .normal else .skip (k - 1) } (some c) cs next
    | .quote start escaped acc =>
      if escaped then scanGo { st with mode := .quote start false (c :: acc) } (some c) cs next
      else if c == '\\' then scanGo { st with mode := .quote start true (c :: acc) } (some c) cs next
      else if c == '"' then
        scanGo { st with cur := st.cur.push (.quoted (String.mk acc.reverse), start, next), mode := .normal }
          (some c) cs next
      else scanGo { st with mode := .quote start false (c :: acc) } (some c) cs next
    | .chunk start acc =>
      if chunkChar c then scanGo { st with mode := .chunk start (c :: acc) } (some c) cs next
      else
        match endChunk st start acc pos with
        | .error r => .error r
        | .ok st2 =>
          match normalStep st2 prev c cs pos with
          | .error r => .error r
          | .ok st3 => scanGo st3 (some c) cs next
    | .normal =>
      match normalStep st prev c cs pos with
      | .error r => .error r
      | .ok st2 => scanGo st2 (some c) cs next

/-- Whether the words are exactly a conclusion marker, its first word possibly capitalised. -/
def isConclusionMarker (ts : List Tok) : Bool :=
  let first (m : String) (t : String) := t == m || t == capitalise m
  match ts with
  | [.word a _] => first "therefore" a || first "so" a || first "hence" a
  | [.word a _, .word b _, .word c _] => first "it" a && b == "follows" && c == "that"
  | _ => false

/-- Marks the initial words of a sentence (spec 2.2, item 8). -/
def markInitials (s : Array Spanned) : Array Spanned :=
  s.mapIdx fun k (t, a, b) =>
    match t with
    | .word text _ =>
      if k == 0 || isConclusionMarker ((s.extract 0 k).toList.map (·.1)) then (.word text true, a, b)
      else (t, a, b)
    | _ => (t, a, b)

/-- The sentences of a source as tokens with their byte spans, or the first rejection. -/
def lexSpans (s : String) : Except Reject (Array (Array Spanned)) :=
  if s.utf8ByteSize > maxSourceBytes then .error .sourceTooLong
  else if collapsedLength s > maxTextChars then .error .textTooLong
  else
    match scanGo ⟨#[], #[], .normal⟩ none s.toList 0 with
    | .error r => .error r
    | .ok st =>
      let fin : Except Reject Scan :=
        match st.mode with
        | .chunk start acc => endChunk st start acc s.utf8ByteSize
        | .quote start _ _ => .error (.openQuote start)
        | _ => .ok st
      match fin with
      | .error r => .error r
      | .ok st2 =>
        if !st2.cur.isEmpty then .error .unterminated
        else if st2.sents.isEmpty then .error .emptyDocument
        else .ok (st2.sents.map markInitials)

/-- The sentences of a source as tokens (spec 2.2): `lexSpans` with the spans erased. -/
def lex (s : String) : Except Reject (Array (Array Tok)) :=
  (lexSpans s).map fun ss => ss.map fun sent => sent.map (·.1)

end VE.EnglishGrammar
