import VE.Question.Help

namespace VE.Question
open Lean VE.EnglishGrammar

inductive Outcome
  | one (c : Candidate) (φ : EFormula)
  | meanings (firsts : List (Candidate × EFormula)) (rephrasings : List String)
  | ambiguous (c : Candidate)
  | indefinite (article : String) (rephrasings : List String)
  | none (closest : Option Candidate)
  | refused (c : Candidate) (o : ReadOutcome)
  | form (wh : Bool)
  | text (o : ReadOutcome)        -- the vocabulary refused, or the body's lexing
  | notQuestion
  | limit
  | budget (c : Candidate)

/-- 6's limits on a question: its bytes, the tokens of its body, its candidates. -/
def withinLimits (auxs : List String) (q : String) : Bool :=
  decide (q.utf8ByteSize ≤ maxQuestionBytes) &&
  (match (shape auxs q).body with
   | some t => match bodySentence t with
     | some toks => decide (toks.size ≤ maxTokens)
     | none => true
   | none => true) &&
  decide ((candidates auxs q).length ≤ maxCandidates)

def classify (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) : Outcome :=
  match grammarFault E O L with
  | some g => .text (.invalidGrammar g)
  | none =>
    match shape auxs q with
    | .notQuestion => .notQuestion
    | .other w => .form (whWords.contains w)
    | sh =>
      if q.utf8ByteSize > maxQuestionBytes then .limit else
      match lexSpans ((sh.body.getD "") ++ ".") with
      | .error r => .text (.lexical r)
      | .ok ss =>
        if ss.size != 1 then .notQuestion
        else if ss.any (·.size > maxTokens) then .limit
        else
          let cs := candidates auxs q
          if cs.length > maxCandidates then .limit
          else
            let gs := cs.map fun c => (c, got E O L b c)
            if gs.any (·.2.isNotOne) then .notQuestion
            else match gs.find? (·.2.isBudget) with
            | some (c, _) => .budget c
            | none => match gs.find? (·.2.isMany) with
              | some (c, _) => .ambiguous c
              | none =>
                match firstMeanings gs with
                | [(c, φ)] => .one c φ
                | [] => match gs.find? (·.2.isRefused) with
                  | some (c, .refused o) => .refused c o
                  | _ => .none (closest E L cs)
                | fs => .meanings fs (fs.map fun x => caseThatQuestion x.1)

/-- The every and the some questions, when the body begins with the token `a` or `an`. -/
def swap (frame t : String) : Option (String × String × String) :=
  if "a ".isPrefixOf t then some ("a", frame ++ "every " ++ t.drop 2 ++ "?", frame ++ "some " ++ t.drop 2 ++ "?")
  else if "an ".isPrefixOf t then some ("an", frame ++ "every " ++ t.drop 3 ++ "?", frame ++ "some " ++ t.drop 3 ++ "?")
  else none

def indefiniteSwaps (auxs : List String) (q : String) : Option (String × String × String) :=
  match shape auxs q with
  | .caseThat t => swap caseFrame t
  | .fronted a r => swap (capitalise a ++ " ") r
  | _ => none

/-- The questions of `qs` that read with one meaning, each meaning once, in order. -/
def offered (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (qs : List String) : List String :=
  (qs.foldl (fun (acc : List (String × EFormula)) r => match classify auxs E O L b r with
    | .one _ φ => if acc.any (·.2 == φ) then acc else acc ++ [(r, φ)]
    | _ => acc) []).map (·.1)

def readQuestion (auxs : List String) (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (q : String) : Outcome :=
  match classify auxs E O L b q with
  | .none cl =>
    match indefiniteSwaps auxs q with
    | some (art, qe, qs) =>
      let rs := offered auxs E O L b [qe, qs]
      if rs.isEmpty then .none cl else .indefinite art rs
    | none => .none cl
  | o => o
end VE.Question
