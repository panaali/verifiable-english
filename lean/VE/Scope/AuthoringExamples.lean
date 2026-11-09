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
-- a slot's words: no tab inside or before a word, one space after every word; a section is one word
#guard ["The hard constraints apply only where the act\tis irreversible.", "The hard constraints apply only where the act \tis irreversible.",
  "The hard constraints apply only where the act  is irreversible.", "Notwithstanding the rules of section 3 x, every operator may share.",
  "Notwithstanding the rules of section  3, every operator may share.", "Notwithstanding the rules of section 3\t, every operator may share.",
  "Notwithstanding the rules of section 3\u00A0, every operator may share.", "Notwithstanding the rules of section 3\x07, every operator may share.",
  "The hard constraints apply only where the act\u00A0is irreversible.", "The hard constraints apply only where the act\u2003is irreversible.",
  "The hard constraints apply only where the act is irreversible\r.", "The hard\u00A0constraints apply only where the act is irreversible.",
  "The hard constraints apply only where the act\x07is irreversible.", "The hard constraints apply only where the act\x7Fis irreversible.",
  "## Hard\u3000constraints"].all (parseGovernor · == none)
-- what a slot may hold: curly quotes, digits and any other letter
#guard trip "The hard constraints apply only where the act is in Claude’s “sandbox” 2." "{\"reach\": {\"list_name\": \"the hard constraints\"}, \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"the act is in Claude’s “sandbox” 2\"}]}}"
-- levels 1 to 6
#guard trip "###### Notes" "{\"reach\": {\"anchor\": {\"heading\": \"Notes\", \"level\": 6}}, \"effect\": \"title\"}"
-- a line with no "#" is no heading, whatever follows
#guard parseGovernor " Hard constraints" == none && parseGovernor "Hard constraints" == none
-- a block no wording gives (a heading with no level, an empty object) renders to a line that is no wording
#guard [j "{\"reach\": {\"anchor\": {\"heading\": \"Hard constraints\"}}, \"effect\": \"title\"}", j "{}", .null].all
  fun b => parseGovernor (renderGovernor b) == none
-- a narrowing whose condition mentions "its kind" takes the "In place of" wording (2.2, F4)
#guard parseGovernor "The hard constraints apply only where the act is of its kind." == none
-- two rows read it (a list name, and a narrowing of a list called "the rules below are called the x"): refused
def twoReadings := "The rules below are called the x apply only where y."
#guard (readings twoReadings).length == 2 && parseGovernor twoReadings == none
-- the row's words twice: the name or the condition could hold them, so it is refused
#guard parseGovernor "The hard constraints apply only where x apply only where y." == none
-- the same, a carve-out over the name "the rules below are called the x"
#guard parseGovernor "The rules below are called the x do not apply when y." == none

/-! ## sc-7 review F1: no slot ends a sentence (`clause`), so a wording is one sentence -/

-- the review's probe: a question or exclamation is no "When"/"If" clause and no condition (refused, never a narrowing)
#guard ["## When should Claude refuse?", "### If in doubt, ask!", "The hard constraints apply only where is the act irreversible?."].all
  fun w => ((parseGovernor w).map (·.getObjValD "effect")).all (· == Json.str "title")
-- every slot, every sentence end, at the slot's end or inside it, before a closing quote, and full-width
#guard ["## When should Claude refuse?", "### If in doubt, ask!", "## When asked. Then refuse", "## If the user says “stop.”",
  "## When asked: refuse", "## If so…", "The hard constraints apply only where is the act irreversible?.",
  "The hard constraints apply only where the act is irreversible!.", "The hard constraints apply only where x. The rules apply only where y.",
  "The hard constraints do not apply when asked?.", "The hard constraints do not apply when asked (see above.).",
  "Notwithstanding the rules of section 3, may every operator share?.", "Notwithstanding the rules of section 3, x. y.",
  "Notwithstanding the rules of section 3?, x.", "Notwithstanding the rules of section 3., x.", "Notwithstanding the rules of section 3:, x.",
  "This applies only where is the user a minor?.", "This applies only where the user is a minor？.", "This applies only where x！ y.",
  "This applies only where the user waits… then acts.", "The rules below are called the x. The rules below are called the y.",
  "The rules below are called the x?.", "The hard constraints. The rules apply only where y.",
  "The hard constraints! do not apply when y.", "In place of their own condition, the x. the y apply only where " ++ kindWording ++ "."
  ].all (parseGovernor · == none)
-- sc-7 review F5: a comma inside the section slot
#guard parseGovernor "Notwithstanding the rules of section 3,4, every operator may share." == none
-- the section slot's first character is checked too: a comma, or a control character before the number
#guard ["Notwithstanding the rules of section ,3, every operator may share.",
  "Notwithstanding the rules of section \x073, every operator may share."].all (parseGovernor · == none)
-- the other direction: a question that is no "When"/"If" heading is a title, and a "." inside a word stays in a slot
#guard trip "## Should Claude refuse?" "{\"reach\": {\"anchor\": {\"heading\": \"Should Claude refuse?\", \"level\": 2}}, \"effect\": \"title\"}"
#guard trip "The hard constraints apply only where the act is in section 3.2." "{\"reach\": {\"list_name\": \"the hard constraints\"}, \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"the act is in section 3.2\"}]}}"
#guard trip "Notwithstanding the rules of section 3.2, every operator may share." "{\"reach\": {\"anchor\": {\"section\": \"3.2\"}}, \"effect\": \"precedes\", \"rule\": {\"english\": \"every operator may share\"}}"
#guard trip "The rules below are called the users’ rules." "{\"list_name\": \"the users’ rules\"}"

end VE.Scope.AuthoringExamples
