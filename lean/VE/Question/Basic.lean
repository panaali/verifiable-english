import VE.EnglishGrammar.Read
import VE.EnglishGrammar.Diagnose

namespace VE.Question
open Lean VE.EnglishGrammar
open VE.Grammar (Derives)


def auxiliaries : List String := ["is", "must", "may"]
def caseFrame : String := "Is it the case that "
def whWords : List String := ["Who", "What", "Which", "Whom", "Whose", "Where", "When", "Why", "How"]
def maxQuestionBytes : Nat := 4096
def maxTokens : Nat := 300
def maxCandidates : Nat := 64

inductive Form
  | caseThat
  | fronted (aux : String) (gap : Nat)
  deriving DecidableEq, Repr

structure Candidate where
  form : Form
  sentence : String
  deriving DecidableEq, Repr

inductive Shape
  | caseThat (body : String)
  | fronted (aux rest : String)
  | other (first : String)
  | notQuestion
  deriving DecidableEq, Repr

def questionMarks (q : String) : Nat := (q.toList.filter (· == '?')).length

/-- F1 takes precedence: a question whose text before the `?` begins with `caseFrame` is F1. -/
def shape (auxs : List String) (q : String) : Shape :=
  if !q.endsWith "?" || questionMarks q != 1 then .notQuestion
  else
    let s := q.dropRight 1
    if caseFrame.isPrefixOf s then .caseThat (s.drop caseFrame.length)
    else match auxs.find? (fun a => (capitalise a ++ " ").isPrefixOf s) with
      | some a => .fronted a (s.drop (a.length + 1))
      | none => .other ((s.splitOn " ").headD "")

def Shape.body : Shape → Option String
  | .caseThat t => some t
  | .fronted _ r => some r
  | _ => none

/-- Where the body starts in the question, in bytes. -/
def Shape.offset : Shape → Nat
  | .caseThat _ => caseFrame.utf8ByteSize
  | .fronted a _ => a.utf8ByteSize + 1
  | _ => 0

def isPunct : Tok → Bool
  | .punct .. => true
  | _ => false

/-- The body's one sentence `t ++ "."` as tokens with spans; `none` unless it lexes to exactly one sentence. `lexSpans`
    refuses a final sentence without `.` (`Lexer.lean:265`), hence the added `.`. -/
def bodySentence (t : String) : Option (Array Spanned) :=
  match lexSpans (t ++ ".") with
  | .ok ss => if ss.size == 1 then ss[0]? else none
  | .error _ => none

/-- F2's gaps: the byte offsets in `rest` of every token after the first that is not punctuation. The added `.` is not
    a token, so no gap is at the end. An offset past `rest` is dropped: the lexer gives none, but no statement says
    so, and `mapSpan_valid` needs the bound (spec 2.2; a body change made to prove a reviewed statement). -/
def gaps (rest : String) : List Nat :=
  match bodySentence rest with
  | some toks => (toks.toList.drop 1).filterMap fun (t, a, _) =>
      if isPunct t || decide (rest.utf8ByteSize < a) then none else some a
  | none => []

def insertAt (rest a : String) (g : Nat) : String :=
  rest.extract ⟨0⟩ ⟨g⟩ ++ a ++ " " ++ rest.extract ⟨g⟩ rest.endPos ++ "."

def candidates (auxs : List String) (q : String) : List Candidate :=
  match shape auxs q with
  | .caseThat t => if (bodySentence t).isSome then [⟨.caseThat, t ++ "."⟩] else []
  | .fronted a r => (gaps r).map fun g => ⟨.fronted a g, insertAt r a g⟩
  | _ => []

inductive Got
  | none                         -- no derivation
  | one (φ : EFormula)           -- one derivation, a meaning, no conclusion mark
  | many                         -- two derivations
  | refused (o : ReadOutcome)    -- a derivation without a meaning, or a conclusion mark
  | budget
  | notOne                       -- the candidate does not lex as exactly one sentence

/-- The sentence count is checked before `read`'s outcome, so `.stopped _ o` is sentence 0's. -/
def got (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (c : Candidate) : Got :=
  match lex c.sentence with
  | .error _ => .notOne
  | .ok ws =>
    if ws.size != 1 then .notOne
    else match read E O L b c.sentence with
      | .ok [(φ, false)] => .one φ
      | .stopped _ .noDerivation => .none
      | .stopped _ (.ambiguous _ _) => .many
      | .stopped _ .budget => .budget
      | o => .refused o

def Got.isNotOne : Got → Bool | .notOne => true | _ => false
def Got.isBudget : Got → Bool | .budget => true | _ => false
def Got.isMany : Got → Bool | .many => true | _ => false
def Got.isRefused : Got → Bool | .refused _ => true | _ => false
def Got.meaning? : Got → Option EFormula | .one φ => some φ | _ => Option.none

/-- Add a candidate only when its meaning is new. -/
def addMeaning (acc : List (Candidate × EFormula)) (x : Candidate × Got) :
    List (Candidate × EFormula) :=
  match x.2.meaning? with
  | some φ => if acc.any (·.2 == φ) then acc else acc ++ [(x.1, φ)]
  | none => acc

/-- The first candidate of each distinct meaning, in candidate order. -/
def firstMeanings (gs : List (Candidate × Got)) : List (Candidate × EFormula) :=
  gs.foldl addMeaning []

/-- F1's question for a candidate: `Is it the case that <sentence without its ".">?`. -/
def caseThatQuestion (c : Candidate) : String := caseFrame ++ c.sentence.dropRight 1 ++ "?"

end VE.Question
