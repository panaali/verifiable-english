import VE.Commands.Read

/-! The step reader (docs/spec/commands-imperatives.md section 7, CI-3; item ci-3a): the shapes of a wording
(`If <c>, <x>.`, `Then <x>.`, `<x₁>, then <x₂>.`, the merged wording), each read through `readCommand`, and the
combination of competing shapes' complete alternatives. No route calls it yet; ci-3 wires it into
`readInstruction`. The definitions are section 7's text; `Form` is section 10's (CI-6), defined here because
section 7's `Alt` names it. -/

namespace VE.Commands

open VE.SpeechActs (Scope)
open VE.SpeechActs.Wire (SpeechEnvironment)
open VE.EnglishGrammar (Env Lexicon)

inductive Shape
  | core (s : String)                      -- a merged wording
  | preposed (c x : String)                -- `If <c>, <x>.`
  | after (x : String)                     -- `Then <x>.`: a step after its named source antecedent (finding (c))
  | seq (xs : List String)                 -- `<x₁>, then <x₂>[, then …].`, 2 to 8 steps, none conditioned
  deriving DecidableEq, Repr

def capitalise (x : String) : String :=
  match x.toList with
  | c :: cs => String.mk (c.toUpper :: cs)
  | [] => x

def hasThen (s : String) : Bool := ((trimmed s).splitOn ", then ").length > 1

/-- Every split of `If <c>, <x>.` at a `, `, left to right; `Then <x>.`; the sequence; else the merged wording. -/
def shapes (s : String) : List Shape :=
  let t := trimmed s
  if !(t.endsWith ".") then [.core s] else
  let body := t.dropRight 1
  let pre : List Shape :=
    if body.startsWith "If " then
      let ws := (body.drop 3).splitOn ", "
      (List.range (ws.length - 1)).map fun i =>
        .preposed (", ".intercalate (ws.take (i + 1))) (", ".intercalate (ws.drop (i + 1)))
    else []
  let aft : List Shape := if body.startsWith "Then " then [.after (body.drop 5)] else []
  let xs := body.splitOn ", then "
  let sq : List Shape := if 2 ≤ xs.length && xs.length ≤ 8 && !body.startsWith "If " then [.seq xs] else []
  match pre ++ aft ++ sq with
  | [] => [.core s]
  | l => l

/-- Section 10's forms of a wording (CI-6), named here by section 7's `Alt.form`. -/
inductive Form
  | command | supposition | permission | conditionalClaim | remark | heading
  deriving DecidableEq, Repr

/-- One competing reading of a unit, as `many` lists it. CI-3 adds `shape`; CI-6 `form`; CI-7 `purpose`. -/
inductive Alt
  | shape (sh : Shape) (rs : List Reading)
  | form (f : Form)                          -- CI-6
  | purpose (r : Reading) (p : String)       -- CI-7b
  deriving DecidableEq, Repr

inductive StepOutcome
  | one (r : Reading) (afterPrevious : Bool)
  | steps (rs : List Reading)
  | many (alts : List Alt)
  | refused (code text : String)
  | limit
  | mixed (r : Reading) (p : String)         -- CI-7b
  deriving DecidableEq, Repr

/-- A merged outcome as a step outcome; `after` marks a `Then <x>.` step. -/
def lift (sh : Shape) (after : Bool) : Outcome → StepOutcome
  | .one r => .one r after
  | .many rs => .many (rs.map fun r => .shape sh [r])
  | .refused code text => .refused code text
  | .limit => .limit

def conditionScope : StepOutcome :=
  .refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the condition on each step or on the first only"

/-- The individual shape's complete outcomes. Core, preposed and after use `lift`; `seq` combines every step,
including all readings of a `many` step. The precedence and cap are specified immediately below. -/
def readingTuples : List (List Reading) → List (List Reading)
  | [] => [[]]
  | xs :: rest => xs.flatMap fun x => (readingTuples rest).map (x :: ·)

def shapeOutcome (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) : Shape → StepOutcome
  | .core s => lift (.core s) false (readCommand se sc E L b s)
  | .preposed c x =>
    if hasThen (x ++ ".") then conditionScope
    else lift (.preposed c x) false (readCommand se sc E L b (capitalise x ++ ", if " ++ c ++ "."))
  | .after x => lift (.after x) true (readCommand se sc E L b (capitalise x ++ "."))
  | .seq xs =>
    let os := xs.map fun x => readCommand se sc E L b (capitalise x ++ ".")
    let firstFault := os.findSome? fun o => match o with
      | .refused code text => some (.refused code text)
      | .one r => if r.guard == .top then none else some conditionScope
      | .many rs => if rs.any (·.guard != .top) then some conditionScope else none
      | .limit => none
    match firstFault with
    | some fault => fault
    | none =>
      if os.any (fun o => match o with | .limit => true | _ => false) then .limit
      else
        let choices := os.map fun o => match o with
          | .one r => [r]
          | .many rs => rs
          | _ => []
        let all := readingTuples choices
        if all.length > maxCandidates then .limit
        else match all with
          | [rs] => .steps rs
          | [] => .refused "InvalidInput" "no single speech-act reading"
          | alts => if alts.length ≤ VE.SpeechActs.Wire.readingsBound
              then .many (alts.map fun rs => .shape (.seq xs) rs) else .limit

/-- Each alternative is a complete interpretation of its shape: a sequence alternative has exactly one reading
for every step. `one` and `steps` contribute one alternative; `many` contributes each of its alternatives. -/
def shapeAlts (sh : Shape) (o : StepOutcome) : List Alt :=
  match o with
  | .one r _ => [.shape sh [r]]
  | .steps rs => [.shape sh rs]
  | .many alts => alts
  | _ => []

/-- Combine the outcomes of competing shapes as specified below. -/
def combineShapes (os : List (Shape × StepOutcome)) : StepOutcome :=
  let alts := os.flatMap fun (sh, o) => shapeAlts sh o
  if alts.length > VE.SpeechActs.Wire.readingsBound then .limit
  else if 2 ≤ alts.length then .many alts
  else if os.any (fun (_, o) => match o with | .limit => true | _ => false) then .limit
  else match os.findSome? (fun (_, o) => match o with
      | .one _ _ => some o
      | .steps _ => some o
      | .many _ => some o
      | _ => none) with
    | some o => o
    | none =>
      if os.any (fun (_, o) => match o with
          | .refused code _ => code == "ConditionScope"
          | _ => false) then conditionScope
      else .refused "InvalidInput" "no single speech-act reading"

/-- A single shape passes through; multiple shapes combine their complete alternatives and limit flags. -/
def readStep (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String) : StepOutcome :=
  let os := (shapes s).map fun sh => (sh, shapeOutcome se sc E L b sh)
  match os with
  | [(_, o)] => o
  | _ => combineShapes os

/-- A shape has a completed reading, including an alternative of `many`. -/
def reads (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (sh : Shape) : Bool :=
  !(shapeAlts sh (shapeOutcome se sc E L b sh)).isEmpty

end VE.Commands
