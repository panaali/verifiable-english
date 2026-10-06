import VE.EnglishGrammar.Token
import VE.EnglishGrammar.Lexicon

namespace VE.EnglishGrammar

inductive AdvWord where
  | w (s : String)
  | any
  | anyBut (s : String)
  deriving DecidableEq, Repr

structure AdviceRow where
  id : String
  profile : String
  patterns : List (List AdvWord)
  text : String

def aw (s : String) : List AdvWord := (splitWs s).map AdvWord.w

def riskConditionText : String :=
  "A condition wording ('cannot lead to … unless …', 'leads to … exactly when …', 'If …, … leads to …') is a " ++
  "record statement. In a rule, 'unless' is the rule's carve-out: write ', unless …', or move the condition into " ++
  "the decision record."
def pluralText : String := "Plural or possessive reference needs an explicit-name or scoped-referent confirmation."
def negExistText : String :=
  "A sentence that begins with \"no\" cannot use \"that\" or \"who\" after the noun. Write \"it is not the case that there is ... such that ...\" instead."

def adviceRows : List AdviceRow :=
  [⟨"risk-may", "risk@0", [aw "may lead to"], "Use 'might lead to': 'may' is permission."⟩,
   ⟨"risk-does-not", "risk@0", [aw "does not lead to"], "Choose 'cannot lead to' or 'might not lead to'."⟩,
   ⟨"risk-degree", "risk@0", [aw "could lead to", aw "risks", aw "is likely to lead to", aw "increases the risk of"],
     "Use 'might lead to' for possibility under the declared record."⟩,
   ⟨"risk-certainly", "risk@0", [aw "certainly leads to"], "Use 'leads to' for certainty under the declared record."⟩,
   ⟨"risk-prevents", "risk@0", [aw "prevents"], "Use 'might prevent' in a risk environment."⟩,
   ⟨"risk-safer", "risk@0", [aw "is safer than"], "Use 'has a less severe worst case than'."⟩,
   ⟨"risk-condition", "risk@0", [aw "unless", aw "exactly when"], riskConditionText⟩,
   ⟨"alternatives-causes", "alternatives@0", [aw "causes"],
     "The proximate cause wording needs a declared proximate role; declare it or write 'leads to'."⟩,
   ⟨"alternatives-results", "alternatives@0", [aw "results in", aw "brings about"],
     "Use the declared Boolean wording 'leads to' for this outcome."⟩,
   ⟨"alternatives-degree", "alternatives@0", [aw "could lead to", aw "risks", aw "increases the risk of",
     aw "contributes to", aw "provides uplift to"],
     "This outcome wording is not Boolean. State a supported leads-to cell or label the degree of risk as open."⟩,
   ⟨"alternatives-inaction", "alternatives@0", [aw "through inaction allows"],
     "Through inaction allows has two readings. State whether inaction leads to the harm, or whether an avoidable harm is allowed."⟩,
   ⟨"alternatives-human-harm", "alternatives@0", [aw "allows a harm to a human being to happen"],
     "Write the long form: there is a harm such that both that harm is a harm to a human being and that action allows that harm to happen."⟩,
   ⟨"alternatives-person", "alternatives@0", [[.w "allows", .any, .w "to", .anyBut "happen"]],
     "Permission for a person uses the W1 'may' wording, not causal 'allows'."⟩]

def advWords (toks : List Tok) : List (Option String) :=
  toks.map fun t => match t with
    | .word x _ => some (fold x)
    | _ => none
def advPrefix (ws : List (Option String)) : List AdvWord → Bool
  | [] => true
  | p :: ps => match ws with
    | [] => false
    | w :: rest => (match p, w with
        | .w s, some x => x == s
        | .any, some _ => true
        | .anyBut s, some x => x != s
        | _, none => false) && advPrefix rest ps
def advice (profiles : List String) (toks : List Tok) : Option (String × String) :=
  let ws := advWords toks
  if ws.head? == some (some "no") && (ws.contains (some "that") || ws.contains (some "who")) then
    some ("negated-existential", negExistText)
  else if (["they", "them", "their", "her", "him", "his"].map some).contains (ws.headD none) then
    some ("plural-pronoun", pluralText)
  else (List.range ws.length).findSome? fun i =>
    (adviceRows.find? fun r => profiles.contains r.profile && r.patterns.any (advPrefix (ws.drop i))).map
      fun r => (r.id, r.text)

end VE.EnglishGrammar
