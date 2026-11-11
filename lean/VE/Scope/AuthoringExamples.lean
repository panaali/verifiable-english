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

/-! ## sc-7 review F7: a sentence end before any closer (`closers`) is a sentence end -/

-- the review's PROBE F7, and the DRI note's `x.› y` and `x.） y`
#guard ["## If the user says 'stop.'", "The rules below are called the x.' The rules below are called the y.",
  "The hard constraints apply only where x.} y.", "The hard constraints apply only where x。」 y.",
  "The hard constraints apply only where x.› y.", "The hard constraints apply only where x.） y."].all (parseGovernor · == none)
-- the DRI note's closers and the ASCII and Markdown ones are closers (tests/test_scope_authoring.py checks all of Pe, Pf, Pi)
#guard "'}›’」』）］｝〉》】〕”\")]»＂＇>*_`~«“‘‹".all closers.contains
-- the class: every closer, alone or after another, after every sentence end, in every slot
def slotsEnding (e : String) : List String :=
  [s!"## If the user says stop{e}", s!"## When asked{e} refuse", s!"The hard constraints apply only where x{e} y.",
   s!"The hard constraints do not apply when x{e} y.", s!"Notwithstanding the rules of section 3, x{e} y.",
   s!"Notwithstanding the rules of section 3{e}, x.", s!"This applies only where x{e} y.",
   s!"The rules below are called the x{e} The rules below are called the y.",
   s!"In place of their own condition, the x{e} the y apply only where {kindWording}."]
#guard ".?!:…‽。？！：．".toList.all fun t => closers.toList.all fun q =>
  (slotsEnding (t.toString ++ q.toString) ++ slotsEnding (t.toString ++ q.toString ++ ")”")).all (parseGovernor · == none)
-- the other direction: a closer after no sentence end stays in its slot
#guard trip "The rules below are called the users' rules." "{\"list_name\": \"the users' rules\"}"
#guard trip "The hard constraints apply only where the act (as above) is “final”." "{\"reach\": {\"list_name\": \"the hard constraints\"}, \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"the act (as above) is “final”\"}]}}"

/-! ## sc-7 review F8: a sentence end of any script ends a slot (no one of them is in `clause`'s allow-list) -/

-- the recheck's PROBE F8, verbatim
#guard ["The rules below are called the x‼ The rules below are called the y.", "The hard constraints apply only where x⁉ y.", "The hard constraints apply only where x؟ y.", "The hard constraints apply only where x｡ y.", "The hard constraints apply only where x﹖ y.", "The hard constraints apply only where x। y."].all (VE.Scope.Pinned.parseGovernor · == none)
-- the sentence ends recheck F8 named besides F7's eleven (the DRI note's ‼ ⁉ ⁈ ⁇ ؟ ۔ ｡ ﹖ ﹗ ﹒ ։ ። । among them): in every
-- slot, alone, before a closer, two closers and an invisible character (tests/test_scope_authoring.py sweeps every character)
#guard "։؝؞؟۔܀܁܂߹࠷࠹࠽࠾।॥၊။።፧፨᙮᜵᜶។៕᠃᠉᥄᥅᪨᪩᪪᪫᭎᭏᭚᭛᭞᭟᭽᭾᭿᰻᰼᱾᱿․‥‼⁇⁈⁉⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑⒒⒓⒔⒕⒖⒗⒘⒙⒚⒛⸮⸼⹓⹔㏂㏇㏘꓿꘎꘏꛳꛷꡶꡷꣎꣏꤯꧈꧉꩝꩞꩟꫰꫱꯫︒︓︕︖︙︰﹒﹕﹖﹗｡𐩖𐩗𐽕𐽖𐽗𐽘𐽙𐾆𐾇𐾈𐾉𑁇𑁈𑂾𑂿𑃀𑃁𑅁𑅂𑅃𑇅𑇆𑇍𑇞𑇟𑈸𑈹𑈻𑈼𑊩𑏔𑏕𑑋𑑌𑗂𑗃𑗉𑗊𑗋𑗌𑗍𑗎𑗏𑗐𑗑𑗒𑗓𑗔𑗕𑗖𑗗𑙁𑙂𑜼𑜽𑜾𑥄𑥆𑩂𑩃𑪛𑪜𑱁𑱂𑻷𑻸𑽃𑽄𖩮𖩯𖫵𖬷𖬸𖭄𖵮𖵯𖺘𛲟𝪈🄀".toList.all fun t =>
  [t.toString, t.toString ++ "’", t.toString ++ ")”", t.toString ++ "\u200B"].all fun e => (slotsEnding e).all (parseGovernor · == none)

/-! ## sc-7 review F9: an invisible character or a mark after a sentence end hides nothing (`clause`, `wordChar`) -/

-- the recheck's PROBE F9, verbatim
#guard ["The rules below are called the x.\u200B The rules below are called the y.", "The hard constraints apply only where x.\u2060 y.", "The hard constraints apply only where x.\u0301 y."].all (VE.Scope.Pinned.parseGovernor · == none)
-- the DRI note's U+00AD, U+FE0F and "x.)\u0301 y", and invisible characters mixed with closers in either order
#guard ["The hard constraints apply only where x.\u00AD y.", "The hard constraints apply only where x.\uFE0F y.",
  "The hard constraints apply only where x.)\u0301 y.", "The hard constraints apply only where x.\u200B) y.",
  "The rules below are called the x‼\u200B”\u0301 The rules below are called the y."].all (parseGovernor · == none)
-- the class: a sample of Cf, Mn, Me and Default_Ignorable_Code_Point characters (range ends among them), alone, after a
-- closer and before one, after each of F7's sentence ends, in every slot (tests/test_scope_authoring.py sweeps every
-- character)
#guard [0xAD, 0x300, 0x36F, 0x488, 0x489, 0x600, 0x61C, 0x200B, 0x200F, 0x202A, 0x202E, 0x2060, 0x2064, 0x2065, 0x206F, 0x20DD,
  0x20F0, 0xFE00, 0xFE0F, 0xFE20, 0xFEFF, 0xFFF0, 0xFFFB, 0x110BD, 0x13430, 0x1BCA3, 0x1D173, 0x1E944, 0xE0000, 0xE0001,
  0xE007F, 0xE0100, 0xE01EF, 0xE0FFF].all fun n => ".?!:…‽。？！：．".toList.all fun t =>
  [s!"{t}{Char.ofNat n}", s!"{t}’{Char.ofNat n}", s!"{t}{Char.ofNat n}”"].all fun e => (slotsEnding e).all (parseGovernor · == none)
-- the DRI note's amendment: a Hangul filler or the braille blank after a sentence end (`wordChar` refuses each anywhere,
-- and none is in `clause`'s allow-list)
#guard !clause "x.\u3164"
#guard !clause "x.\u115F"
#guard !clause "x.\u1160"
#guard !clause "x.\uFFA0"
#guard !clause "x.\u2800"
-- a C1 control after a sentence end, and a filler drawn as a space in place of a space, are no word characters
#guard ["The hard constraints apply only where x.\u0080 y.", "The hard constraints apply only where x.\u009F y.",
  "The rules below are called the x.\u3164The rules below are called the y.", "The hard constraints apply only where x.\u2800y.",
  "The hard constraints apply only where x.\u115Fy.", "The hard constraints apply only where x.\u1160y.",
  "The hard constraints apply only where x.\uFFA0y."].all (parseGovernor · == none)
-- a word that ends in a mark or an invisible character is refused even after no sentence end (sc-7 note 2026-11-09 (c):
-- no mark or format character is in `clause`'s allow-list); a precomposed letter takes its place ("café", below)
#guard ["The rules below are called the cafe\u0301 rules.", "The hard constraints apply only where the act is final\u200B."].all
  (parseGovernor · == none)

/-! ## sc-7 recheck F10 and the DRI note 2026-11-09 (c): `clause` is an allow-list -/

-- the recheck's PROBE F10, verbatim: the Coptic Old Nubian full stop and question marks
#guard ["The hard constraints apply only where x\u2CF9 y.", "The hard constraints apply only where x\u2CFA y.", "The rules below are called the x\u2CFB The rules below are called the y."].all (VE.Scope.Pinned.parseGovernor · == none)
-- the recheck's blank-looking characters after a ".": U+1D159 (musical null notehead), U+E000 (private use), U+FFFC
-- (object replacement), as a condition and as a list name, and in every slot
#guard ["The hard constraints apply only where x.\uFFFC y.", "The rules below are called the x.\uFFFC The rules below are called the y.",
  "The hard constraints apply only where x.\uE000 y.", "The rules below are called the x.\uE000 The rules below are called the y."].all
  (parseGovernor · == none)
#guard [0x1D159, 0xE000, 0xFFFC].all fun n => [s!".{Char.ofNat n}", s!"{Char.ofNat n}", s!".{Char.ofNat n}”"].all fun e =>
  (slotsEnding e).all (parseGovernor · == none)

/-! ## sc-7-f11: a sentence end inside a word, with a blank-looking character in place of the space (`clause`) -/

/-- Each slot with `e` inside a word, joined to the next word with no space. -/
def slotsJoined (e : String) : List String :=
  [s!"## If the user says x{e}The rest", s!"## When asked{e}The refuse", s!"The hard constraints apply only where x{e}The y.",
   s!"The hard constraints do not apply when x{e}The y.", s!"Notwithstanding the rules of section 3, x{e}The y.",
   s!"Notwithstanding the rules of section 3{e}The, x.", s!"This applies only where x{e}The y.",
   s!"The rules below are called the x{e}The rules below are called the y.",
   s!"In place of their own condition, the x{e}The y apply only where {kindWording}."]
-- the recheck's FOLLOW-UP F11: U+1D159, U+FFFC and U+E000 joined, as a list name and as a condition, and in every slot,
-- alone, after a closer and before one
#guard [0x1D159, 0xFFFC, 0xE000].all fun n => let c := Char.ofNat n
  [s!"The rules below are called the x.{c}The rules below are called the y.",
   s!"The hard constraints apply only where the x.{c}The rules below are called the y."].all (parseGovernor · == none) &&
  [s!".{c}", s!".”{c}", s!".{c}”"].all fun e => (slotsJoined e).all (parseGovernor · == none)
-- the class: each of F7's sentence ends, joined by a blank-looking, invisible or mark character, in every slot
#guard ".?!:…‽。？！：．".toList.all fun t => [0x1D159, 0xFFFC, 0xE000, 0x200B, 0x2060, 0x3164, 0x2800, 0x0301].all fun n =>
  (slotsJoined s!"{t}{Char.ofNat n}").all (parseGovernor · == none)
-- the other direction: a "." inside a word before a `follower` stays in its slot
#guard [".", ".)", "”", ".(", ".—"].all fun e => (slotsJoined e).all fun w => (parseGovernor w).isSome
#guard trip "The hard constraints apply only where the dose is over 3.5 mg, e.g in a trial." "{\"reach\": {\"list_name\": \"the hard constraints\"}, \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"the dose is over 3.5 mg, e.g in a trial\"}]}}"
#guard ["e.g", "3.5", "x.y", "x.)y", "x.”’y", "Claude’s", "(x)", "“x”", "x—y", "x\u200By", "cafe\u0301s", "x..y", "x——y",
  "wait...,", "((a))", "“(a)”)", "(b)—is", "user’(s)", "(a)–(b)", "x.!y", "x.~y", "x.\u2010y", "x.\u2027y", "x.\u2024y"].all clause
#guard ["The hard constraints apply only where the act (see “(a)”) is final.", "The hard constraints apply only where the act ((a)) is final.",
  "The hard constraints apply only where the act—(a) or (b)—is final.", "The hard constraints apply only where the user’(s) act is final.",
  "The hard constraints apply only where the user says wait..., then x."].all fun w => (parseGovernor w).isSome
-- `follower`'s edges: the ends of its two ranges and a Latin letter are in, the characters just beside them are not
#guard [0x21, 0x7E, 0x2010, 0x2027, 0xC0, 0x24F].all (follower ∘ Char.ofNat) &&
  ![0x20, 0x7F, 0x80, 0x200F, 0x2028, 0xBF, 0x250, 0xD7].any (follower ∘ Char.ofNat)
#guard ["x.Ày", "x.ɏy", "x”éy"].all clause
-- what this rule refuses that was accepted: a character outside the allow-list, then one that is no `follower`, inside a
-- word (the edges of `follower`'s two ranges among them)
#guard ["x.\u0301y", "x\u200B\u200By", "xαβy", "x”\u0301y", "Привет,", "日本語-text", "x.\u200Fy", "x.\u2030y", "x.¡y", "x.\u2060y"].all
  (!clause ·)
-- a Markdown character reference in a word draws a space or a sentence end where the source has none (`charRef`; the
-- DRI decision 2026-11-10 sc-7-f11 item 1): refused in every slot, at a word's end and inside it
#guard ["The hard constraints apply only where x&#46; y.", "The rules below are called the x.&nbsp;The rules below are called the y."].all
  (parseGovernor · == none)
#guard ["&nbsp;", "&#32;", "&#x20;", "&period;", "&#46;", "&#46;&#32;The", ".&nbsp;The", "&amp;", "&#5;"].all fun e =>
  (slotsEnding e ++ slotsJoined e).all (parseGovernor · == none)
#guard ["x&nbsp;y", "x&#32;", "x&#x20;y", "x&period;", "&#46;", "x.&nbsp;y"].all (!clause ·)
-- a reference after another "&", or before one, and a pair at a word's start (trust mutants: the first or last "&" only,
-- the first pair skipped)
#guard ["x&y&nbsp;z", "x&nbsp;&y", ".\u200By", "\u0301\u0301y", "x .\uFFFCThe"].all (!clause ·)
-- a run of one is a reference too (the ruling's "non-empty run"; sc-7-f11 review F2), in every slot
#guard ["&a;", "&#;", "&1;", "AT&T;", "x&#;", "x&a;y", "R&D;"].all (!clause ·)
#guard ["&a;", "&#;", "AT&T;", "x&#;"].all fun e => (slotsEnding e ++ slotsJoined e).all (parseGovernor · == none)
-- "&" with no run before ";", or with no ";", is no reference
#guard ["AT&T", "AT&T,", "x&;", "x&;y", "R&D-heavy", "x&y", "x&nbsp", "x&-;"].all clause
#guard trip "The rules below are called the AT&T rules." "{\"list_name\": \"the AT&T rules\"}"
-- a word that is empty once its closers are dropped is refused
#guard [")", "x )", "x ”’", "\"", "x *_"].all (!clause ·)
#guard ["The hard constraints apply only where x ) y.", "The rules below are called the x ” The rules below are called the y."].all
  (parseGovernor · == none)
-- a C1 control inside a word, where the allow-list does not see it: `wordChar` refuses DEL and U+0080 to U+009F anywhere
#guard ["x\x7Fy", "x\u0080y", "x\u0090y", "x\u009Ey", "x\u009Fy"].all (!clause ·) && clause "x\u00A1y"
#guard ["The hard constraints apply only where the act\u0080is irreversible.", "The rules below are called the x\u009Fy."].all
  (parseGovernor · == none)
-- every closer is dropped after a word's allowed character, alone or twice, and hides no "." before it
#guard closers.toList.all fun q => clause s!"x{q}" && clause s!"x{q}{q}" && !clause s!"x.{q}"
#guard trip "The hard constraints apply only where the act is \"final\"." "{\"reach\": {\"list_name\": \"the hard constraints\"}, \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"the act is \\\"final\\\"\"}]}}"
-- one accepted word ending in each class of the allow-list: an ASCII letter, a digit, a Latin letter (the range's ends
-- and "café"), and each allowed ASCII punctuation character; and the characters just beside them are refused
#guard ["xa", "xz", "xA", "xZ", "x0", "x9", "xÀ", "xÖ", "xØ", "xö", "xø", "xÿ", "xő", "xɏ", "café", "x,", "x;", "x-", "x%", "x/",
  "x&", "x+", "x=", "x#", "x$", "x@", "x@)”"].all clause
#guard ["x×", "x÷", "x¿", "xɐ", "x.", "x!", "x?", "x:", "x\u0301", "x\u200B", "xα", "x٣", "x'.", "x<", "x^", "x|", "x\\"].all (!clause ·)
-- U+01C3 "ǃ" (Latin letter retroflex click) is drawn as "!", so it is left out of the Latin range; its neighbours stay in
#guard ["The rules below are called the xǃ The rules below are called the y.", "The hard constraints apply only where xǃ y."].all
  (parseGovernor · == none)
#guard !clause "xǃ" && ["xǀ", "xǁ", "xǂ", "xǄ"].all clause
#guard trip "The rules below are called the café rules." "{\"list_name\": \"the café rules\"}"
#guard trip "The hard constraints apply only where the act is in Claude’s café." "{\"reach\": {\"list_name\": \"the hard constraints\"}, \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"the act is in Claude’s café\"}]}}"
#guard trip "The hard constraints apply only where a, b; c- 5% d/ e& f+ g= h# i$ j@ k." "{\"reach\": {\"list_name\": \"the hard constraints\"}, \"effect\": {\"reguard\": [\"and\", \"own\", {\"english\": \"a, b; c- 5% d/ e& f+ g= h# i$ j@ k\"}]}}"

end VE.Scope.AuthoringExamples
