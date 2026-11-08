import VE.Scope.Authoring

/-! SC-7's fixtures (docs/spec/scope.md 2.2 and 7.8): for each row of 2.2's wording table, the block its wording
    parses to (written as JSON text, not through the parser's constructors), the round trip of `scope_parseRender`
    and `scope_renderParse` on it, and its paraphrase; F5a (u0170.s01's wording is no governor); and the variants and
    two-reading wordings that are refused. -/

namespace VE.Scope.AuthoringExamples
open Lean VE.Scope.Pinned

def j (s : String) : Json := (Json.parse s).toOption.getD .null
/-- `w` parses to `block`, which renders back to `w` and parses again to `block`. -/
def trip (w block : String) : Bool :=
  parseGovernor w == some (j block) && renderGovernor (j block) == w && parseGovernor (renderGovernor (j block)) == some (j block)
def para (w : String) (x : Context := { count := 7, defaults := "Claude may act", rule := "rule 9" }) : String :=
  ((parseGovernor w).map (paraphrase x)).getD "none"

/-! ## One row of 2.2 each -/

def wFrame := "Every instance of Claude must not:"
#guard trip wFrame "{\"reach\": \"list\", \"effect\": {\"frame\": {\"sign\": false, \"unless\": [], \"over\": []}}}"
#guard para wFrame == "Each item below is its own rule: ‘Every instance of Claude must not <item>.’"

def wNamed := "The rules below are called the hard constraints."
#guard trip wNamed "{\"list_name\": \"the hard constraints\"}"
#guard para wNamed == "‘The hard constraints’ names the rules of the list that follows."

def wNarrow := "The hard constraints apply only where the act is irreversible."
#guard trip wNarrow "{\"reach\": {\"list_name\": \"the hard constraints\"}, \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"the act is irreversible\"}]}}"
#guard para wNarrow == "Each of the 7 rules called ‘the hard constraints’ applies only where the act is irreversible."

def wInPlace := "In place of their own condition, the hard constraints apply only where Claude knows that the act is of its kind, or thinks it quite likely that it is."
-- the condition is spec 3's `g2` (F3), byte for byte
#guard trip wInPlace "{\"reach\": {\"list_name\": \"the hard constraints\"}, \"effect\": {\"reguard\": [\"or\", [\"and\", \"own\", {\"attitude\": {\"holder\": [\"var\", 0], \"mode\": \"knows\", \"content\": \"own\"}}], {\"attitude\": {\"holder\": [\"var\", 0], \"mode\": \"thinks\", \"degree\": \"quite likely\", \"content\": \"own\"}}]}}"
#guard para wInPlace == "Each of the 7 rules now applies where Claude knows that the act is of its kind, or thinks it quite likely that it is, instead of where its own act occurs; its existing carve-outs still apply. ‘Its kind’ is each rule's own act."

def wCarve := "The hard constraints do not apply when an operator has authorised the act."
#guard trip wCarve "{\"reach\": {\"list_name\": \"the hard constraints\"}, \"effect\": {\"carve_out\": {\"english\": \"an operator has authorised the act\"}}}"
#guard para wCarve == "None of the 7 rules applies when an operator has authorised the act; other rules may decide; if none does, Claude may act."

def wPrecedes := "Notwithstanding the rules of section 3, every operator may share."
#guard trip wPrecedes "{\"reach\": {\"anchor\": {\"section\": \"3\"}}, \"effect\": \"precedes\", \"rule\": {\"english\": \"every operator may share\"}}"
#guard para wPrecedes == "Wherever rule 9, or a rule that takes precedence over it directly or through other rules, applies, no rule of section 3 decides on that act."

def wWhen := "## When there is no operator prompt"
#guard trip wWhen "{\"reach\": {\"anchor\": {\"heading\": \"When there is no operator prompt\", \"level\": 2}}, \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"there is no operator prompt\"}]}}"
#guard para wWhen == "Every rule in this section applies only when there is no operator prompt."
#guard trip "### If the user is a minor" "{\"reach\": {\"anchor\": {\"heading\": \"If the user is a minor\", \"level\": 3}}, \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"the user is a minor\"}]}}"
#guard para "### If the user is a minor" == "Every rule in this section applies only if the user is a minor."

def wTitle := "## Hard constraints"
#guard trip wTitle "{\"reach\": {\"anchor\": {\"heading\": \"Hard constraints\", \"level\": 2}}, \"effect\": \"title\"}"
#guard trip "# Whenever: a title" "{\"reach\": {\"anchor\": {\"heading\": \"Whenever: a title\", \"level\": 1}}, \"effect\": \"title\"}"
#guard para wTitle == "A title: it changes no rule."

def wFrontier := "This applies only where the user is a minor."
#guard trip wFrontier "{\"reach\": \"frontier\", \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"the user is a minor\"}]}}"
#guard para wFrontier { fits := some "the rule above" } == "This qualifies the rule above."
#guard para wFrontier { fits := none } == "Which rule or list above does this qualify?"

/-! ## F5a: u0170.s01 states something about the list and changes no rule: no governor, and no row reads it -/

def u0170s01 := "The list of hard constraints above is not a list of all the behaviors we think Claude should never exhibit."
#guard parseGovernor u0170s01 == none
#guard readings u0170s01 == []

/-! ## Refused: no spacing, spelling or punctuation variant, and no second reading -/

#guard ["every instance of Claude must not:", "Every instance of Claude must not :", "Every instance of Claude must not: ",
  "Every instance of Claude must not", "The rules below are called hard constraints.",
  "The rules below are called the hard constraints", "The hard constraints apply only where  the act is irreversible.",
  "The hard constraints apply only where the act is irreversible.\n", "The hard constraints apply only where the act is irreversible..",
  "the hard constraints apply only where the act is irreversible.", "The hard constraints do not apply when .",
  "In place of their own condition, the hard constraints apply only where Claude knows that the act is of its kind.",
  "Notwithstanding section 3, every operator may share.", "Notwithstanding the rules of section 3 , every operator may share.",
  "Notwithstanding the rules of section , every operator may share.", "Notwithstanding the rules of section 3, every operator may share:.",
  "##When there is no operator prompt", "##  Hard constraints", "####### Hard constraints", "## ",
  "## When there is no operator prompt:", "## If", "This applies only where ."].all (parseGovernor · == none)
-- a narrowing whose condition mentions "its kind" takes the "In place of" wording (2.2, F4)
#guard parseGovernor "The hard constraints apply only where the act is of its kind." == none
-- two rows read it (a list name, and a narrowing of a list called "the rules below are called the x"): refused
def twoReadings := "The rules below are called the x apply only where y."
#guard (readings twoReadings).length == 2 && parseGovernor twoReadings == none
-- the same, a carve-out over the name "the rules below are called the x"
#guard parseGovernor "The rules below are called the x do not apply when y." == none

end VE.Scope.AuthoringExamples
