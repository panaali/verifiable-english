import VE.EnglishGrammar.SourceWords

/-! The candidates a source word opens in translation, read from the catalogue's rows (`SourceWords`; et-5b): one owner
per context for "always" (DRI 2026-11-03 item 3) and the anchor's state for "always" and "eventually" (spec 1.3, 2.4).
The rows are the data; this file only chooses among them. -/

namespace VE.EnglishGrammar
open Lean

/-- The deontic verbs that make a sentence a rule (docs/spec/soft-norms.md 2.1: `must`, `may`, `need not` strict;
`should` default). -/
def ruleVerbs : List String := ["must", "may", "need", "should"]

/-- Where a source word stands: inside a rule (a deontic verb, or a rule lead-in such as "Claude should by default:"),
outside one, or not known. `leadIn` is the translator's: `some true` under a rule lead-in, `some false` under none. -/
inductive RuleContext | rule | outside | unknown
  deriving DecidableEq, Repr

def ruleContext (sentence : List String) (leadIn : Option Bool) : RuleContext :=
  if leadIn == some true || sentence.any fun w => ruleVerbs.contains (fold w) then .rule
  else if leadIn == some false then .outside else .unknown

/-- The document's anchor (spec 1.3): an ISO anchor, the open term `date_of_this_document`, or neither. -/
inductive AnchorState | iso | openTerm | none
  deriving DecidableEq, Repr

def rowOf (word profile frame : String) : Option SourceWordKind :=
  (sourceWords.find? fun r => r.word == word && r.profile == profile && r.frame == frame).map (·.kind)

/-- The candidate wordings of `word`, or the reason it stays UNFORMALISED. Inside a rule a word soft-norms owns gets
soft-norms' row only; where the context is not known it is `<word>-owner` (`always-owner`), never both. Outside a rule
the events row applies: both candidates with an ISO anchor, else the no-anchor row's one reading. -/
def sourceReadings (word : String) (ctx : RuleContext) (anchor : AnchorState) : Except String (List String) :=
  let wordings : Option SourceWordKind → Except String (List String)
    | some (.readings cs) => .ok (cs.map (·.wording))
    | some (.refuse _ _ rewrite) => .ok [rewrite]
    | _ => .error s!"no reading row: {word}"
  match rowOf word "soft-norms@0" "rule", ctx with
  | some k, .rule => wordings (some k)
  | some _, .unknown => .error s!"{word}-owner"
  | _, _ => wordings (rowOf word "events@0" (if anchor == .iso then "source" else "source no anchor"))

/-- The candidates a document with the open anchor term may not hold (`AnchorOpen: <candidate>`, spec 2.9 item 8): the
refused candidate of each no-anchor row. -/
def anchorCandidates : List String := sourceWords.filterMap fun r => match r.kind with
  | .refuse code _ _ => if r.frame == "source no anchor" then some code else none
  | _ => none

end VE.EnglishGrammar
