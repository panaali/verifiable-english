import VE.Question.Read

/-! Question-specific response wording. The English reader's existing rejection table
remains the source for shared codes; these are the new question codes and the three
wording adjustments required by the question surface. -/

namespace VE.Question
open VE.EnglishGrammar

/-- First version of the question contract. -/
def question_version : Nat := 1

def newCodeClasses : List (String × String) :=
  [("NotOneQuestion", "SyntaxError"), ("QuestionForm", "SyntaxError"),
   ("QuestionTooLong", "ResourceLimit"), ("AmbiguousQuestion", "AmbiguousDerivation"),
   ("QuestionWithMarker", "SyntaxError"), ("IndefiniteQuestion", "SyntaxError"),
   ("QuestionWordMoved", "SyntaxError")]

def notOneQuestionText : String := "Write one question that ends with a question mark."
def whQuestionText : String :=
  "VE answers yes-or-no questions. It does not answer who, what or which questions yet."
def auxiliariesText (auxs : List String) : String :=
  match (auxs.map fun a => "\"" ++ capitalise a ++ "\"").reverse with
  | [] => ""
  | [a] => a
  | a :: rest => ", ".intercalate rest.reverse ++ " or " ++ a

def formText (auxs : List String) : String :=
  "VE answers questions that begin with " ++ auxiliariesText auxs ++
  ", or with \"Is it the case that\" followed by a sentence."
def questionTooLongText : String := "The question is longer than VE reads. Ask a shorter question."
def workBudgetText : String := "VE stopped reading this question at its work limit."
def ambiguousQuestionText : String :=
  "This question can be read in more than one way. Ask one of these instead:"
def indefiniteText (art : String) : String :=
  "VE cannot tell whether \"" ++ art ++ "\" here means every or some. Ask one of these instead:"
def noDerivationText : String := "The question has no reading with the current vocabulary."
def closestText (c : Candidate) (d : Diagnosis) : String :=
  " Closest sentence tried: \"" ++ c.sentence ++ "\". " ++ d.text
def badQuestionSpacingText (position : Nat) : String :=
  s!"The spacing at position {position} is not allowed: write no space before the question mark."
def markerText : String :=
  "A question cannot contain \"therefore\", \"so\", \"hence\" or \"it follows that\"."
/-- A0 (3.3): the sentence the answer is about, without its final period. -/
def askedText (c : Candidate) : String := "You asked whether " ++ c.sentence.dropRight 1 ++ "."
def illTypedQuestionText : String :=
  "The question was read, and its formula does not pass the type check."
/-- The moved-out refusal (`VE.Question.Moved`): the word, and whether questions are offered in its place. -/
def movedText (aux : String) (offers : Nat) : String :=
  "VE could read this question only by putting \"" ++ aux ++ "\" back inside a smaller part of the sentence, such " ++
  "as a part that begins with \"who\", \"that\", \"which\", \"if\", \"both\" or \"either\", or one of the " ++
  "phrases joined by \"and\" or \"or\". English moves a word to the front only from the main sentence." ++
  (if offers == 0 then "" else if offers == 1 then " Ask this instead:" else " Ask one of these instead:")
/-- What `ve ask` says while VE answers no question (plan Q2, not built). -/
def unansweredText : String :=
  "VE does not answer questions yet. It shows only the sentence it reads the question as."

end VE.Question
