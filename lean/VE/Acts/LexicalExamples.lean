import VE.Norms.Wire

/-! Acceptance fixtures of AP-1 (docs/spec/act-phrases.md 11.1: A1-A6, A13, A15-A19, A21-A30, A32, A33), with the
boundaries of each limit and each diagnostic of `VE.Acts.Lexical` (10: D-1 to D-14, D-19). In act phrases the
fixed phrase is the list `fx` beside it. -/

namespace VE.Acts.LexicalExamples
open VE.Acts.Lexical
open VE.Norms.Wire (canonicalAct canonicalActIn decodeRegulatedIn decodeRegulated)
open VE.Norms (actChecks)

def okS (e : Except String String) : Option String := e.toOption
def errS (e : Except String String) : Option String := match e with
  | .error m => some m
  | .ok _ => none
def errFixed (fx : List String) : Option String := match decodeFixed fx with
  | .error m => some m
  | .ok _ => none
def toks (fx : List String) (s : String) : Option (List Tok) := (lex fx s).toOption
def errReg (e : Except String VE.Norms.Regulated) : Option String := match e with
  | .error m => some m
  | .ok _ => none
def actOf (e : Except String VE.Norms.Regulated) : Option (Option String) := e.toOption.map (·.act)
def chk (fx : List String) (k : Nat) (s : String) : Except String String := check fx "p" k (.str s)

/-! ### 11.1 -/

-- A1 (u039): 97 B, over today's 80; 8 tokens; the wording 109 B
def a1 := "{0} in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"
def fx1 := ["a fair and public hearing by an independent and impartial tribunal"]
#guard a1.utf8ByteSize == 97 && (fx1.getD 0 "").utf8ByteSize == 66
#guard okS (chk fx1 2 a1) == some a1
#guard errS (canonicalAct "p" 2 (.str a1)) == some "InvalidInput: invalid act phrase for p"
#guard toks fx1 a1 == some [.slot 0, .word "in", .word "full", .word "equality", .word "to", .fixed 0, .word "in",
  .slot 1]
#guard wording .entitled a1 ==
  "{0} is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"
#guard (wording .entitled a1).utf8ByteSize == 109

-- A2 (u085), A3 (u106)
def a2 := "{0} to equal pay for equal work without any discrimination"
#guard a2.utf8ByteSize == 58 && okS (chk ["equal pay for equal work"] 1 a2) == some a2
#guard ((toks ["equal pay for equal work"] a2).map List.length) == some 6
#guard wording .right a2 == "{0} has the right to equal pay for equal work without any discrimination"
#guard (wording .right a2).utf8ByteSize == 72
def a3 := "{0} to the protection of the moral and material interests resulting from {1}"
#guard a3.utf8ByteSize == 76 && okS (chk ["the moral and material interests"] 2 a3) == some a3
#guard ((toks ["the moral and material interests"] a3).map List.length) == some 9

-- A4 (u051 today): both checks accept it with the same string
def a4 := "{0} to seek as well as enjoy in other countries asylum from persecution"
#guard a4.utf8ByteSize == 71 && okS (canonicalAct "p" 1 (.str a4)) == some a4
#guard okS (chk fx1 1 a4) == some a4 && okS (chk [] 1 a4) == some a4

-- A5 (u051 source), A6 (u027): a join word outside a fixed phrase (D-4)
#guard errS (chk [] 1 "{0} to seek and to enjoy in other countries asylum from persecution") ==
  some "InvalidInput: act phrase for p joins acts with 'and' outside a fixed phrase"
def a6 := "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment"
def fx6 := ["cruel, inhuman or degrading treatment or punishment"]
#guard a6.utf8ByteSize == 85 && (fx6.getD 0 "").utf8ByteSize == 51
#guard errS (chk fx6 1 a6) == some "InvalidInput: act phrase for p joins acts with 'or' outside a fixed phrase"
-- the fixed phrase's own comma and join words are inside its token
#guard toks fx6 "{0} be subjected to cruel, inhuman or degrading treatment or punishment" ==
  some [.slot 0, .word "be", .word "subjected", .word "to", .fixed 0]

-- A13 (u0156.s03)
def a13 := "{0} actively deceive {1} about the existence of a system prompt or its content"
#guard a13.utf8ByteSize == 78 && okS (chk ["the existence of a system prompt or its content"] 2 a13) == some a13

-- A15 (u024, u037): two permissions on `{0} take place` with different sorts; act identity includes the sorts
def perm (sorts : List String) : Except String VE.Norms.Regulated :=
  decodeRegulatedIn ["acts@0"] [] "p" sorts
    (.mkObj [("role", .str "permission"), ("default", .str "deny"), ("act", .str "{0} take place")])
#guard actOf (perm ["meeting"]) == some (some "{0} take place")
#guard (do actChecks [← perm ["meeting"], ← perm ["assembly"]]).isOk
#guard !(do actChecks [← perm ["meeting"], ← perm ["meeting"]]).isOk

-- A16 (u041): 152 B; fixed phrase 84 B
def a16 := "{0} to be presumed innocent until proved guilty according to law in a public trial at which they have had all the guarantees necessary for their defence"
def fx16 := ["a public trial at which they have had all the guarantees necessary for their defence"]
#guard a16.utf8ByteSize == 152 && (fx16.getD 0 "").utf8ByteSize == 84 && okS (chk fx16 1 a16) == some a16

-- A17, A18: clause words (D-3, D-12)
#guard errS (chk [] 2 "{0} take part if {1} is open") ==
  some "InvalidInput: act phrase for p uses the clause word 'if'; write the condition in the rule's guard"
#guard errFixed ["the court that is competent"] ==
  some "InvalidInput: fixed phrase 'the court that is competent' uses the clause word 'is'"

-- A19 (u0263.s04.p2): the curly apostrophe is folded, in the act and in the fixed phrase
def a19 := "{0} comply with the operator’s instructions in {1}"
#guard a19.utf8ByteSize == 52
#guard okS (chk ["the operator’s instructions"] 2 a19) == some "{0} comply with the operator's instructions in {1}"
#guard "{0} comply with the operator's instructions in {1}".utf8ByteSize == 50
#guard toks ["the operator's instructions"] a19 == some [.slot 0, .word "comply", .word "with", .fixed 0, .word "in",
  .slot 1]

-- A20, A21, A22: a clause word; exactly 400 B accepted, 401 B refused (D-2)
#guard errS (chk [] 1 "{0} must seek asylum") ==
  some "InvalidInput: act phrase for p uses the clause word 'must'; write the condition in the rule's guard"
def a21 := "{0}" ++ String.join (List.replicate 131 " ab") ++ " a a"
def a22 := "{0}" ++ String.join (List.replicate 131 " ab") ++ " a ab"
#guard a21.utf8ByteSize == 400 && okS (chk [] 1 a21) == some a21
#guard a22.utf8ByteSize == 401 && errS (chk [] 1 a22) == some "ResourceLimit: act phrase for p is over 400 bytes"
-- A21 as a plain act: its wording is 414 B
#guard (wording .right a21).utf8ByteSize == 414 && (wording .entitled a21).utf8ByteSize == 412

-- A23: slots and arity (D-1)
#guard errS (chk [] 1 "{0} meet {1}") == some "InvalidInput: invalid act phrase for p"

-- A24: today's check accepts "nor"; this one refuses it (the one exception of `check_extends`)
def a24 := "{0} neither seek nor enjoy asylum"
#guard okS (canonicalAct "p" 1 (.str a24)) == some a24
#guard errS (chk [] 1 a24) == some "InvalidInput: act phrase for p joins acts with 'nor' outside a fixed phrase"

-- A25, A26, A27: overlapping fixed phrases (D-14), a join word at an edge (D-13). A25 uses the stub's phrases: the
-- spec's `equal pay for` ends with a join word, so D-13 comes first.
#guard errFixed ["equal pay rates", "pay rates for women"] ==
  some "InvalidInput: fixed phrases 'equal pay rates' and 'pay rates for women' overlap, or one holds the other"
#guard errFixed ["equal pay for", "for equal work"] ==
  some "InvalidInput: fixed phrase 'equal pay for' must begin and end with a word other than and, or, nor and for"
#guard errFixed ["equal pay", "equal pay for equal work"] ==
  some "InvalidInput: fixed phrases 'equal pay' and 'equal pay for equal work' overlap, or one holds the other"
#guard errFixed ["or its content"] ==
  some "InvalidInput: fixed phrase 'or its content' must begin and end with a word other than and, or, nor and for"

-- A28, A29: a comma not after a word (D-1), a final comma (D-6)
#guard errS (chk [] 1 "{0} seek asylum ,freely") == some "InvalidInput: invalid act phrase for p"
#guard errS (chk [] 1 "{0} seek asylum,") == some "InvalidInput: act phrase for p ends with a comma"

-- A30: a plain act needs its form and a form its act; the form is one of two (D-19)
def plainReg (fields : List (String × Lean.Json)) : Except String VE.Norms.Regulated :=
  decodeRegulatedIn ["acts@0", "norms@0"] [] "p" ["person"]
    (.mkObj ([("role", .str "plain"), ("default", .str "deny")] ++ fields))
#guard errReg (plainReg [("act", .str "{0} to seek asylum")]) ==
  some "InvalidInput: a plain act for p needs its form, and a form needs its act"
#guard errReg (plainReg [("form", .str "has the right")]) ==
  some "InvalidInput: a plain act for p needs its form, and a form needs its act"
#guard errReg (plainReg [("act", .str "{0} to seek asylum"), ("form", .str "may")]) ==
  some "InvalidInput: invalid form for p"
#guard errReg (plainReg [("act", .str "{0} to seek asylum"), ("form", .num 1)]) == some "InvalidInput: invalid form for p"
#guard actOf (plainReg [("act", .str "{0} to seek asylum"), ("form", .str "has the right")]) ==
  some (some "{0} to seek asylum")
#guard actOf (plainReg [("act", .str "{0} to seek asylum"), ("form", .str "is entitled")]) ==
  some (some "{0} to seek asylum")
#guard actOf (plainReg []) == some none
-- the plain act is checked like any act
#guard errReg (plainReg [("act", .str "{0} to seek and enjoy asylum"), ("form", .str "has the right")]) ==
  some "InvalidInput: act phrase for p joins acts with 'and' outside a fixed phrase"

-- A32 (u0123.s03): `false` is a clause word, in a fixed phrase too (F10, SR13)
#guard errFixed ["its core identity or principles", "to be human", "genuinely deceptive tactics that could harm users",
    "false information that could deceive the user", "health or safety", "Anthropic’s guidelines"] ==
  some "InvalidInput: fixed phrase 'false information that could deceive the user' uses the clause word 'false'"

-- A33 (u092 source): its first comma comes before its "or" (D-5)
def a33 := "{0} to security in the event of unemployment, sickness, disability, widowhood, old age or other lack of livelihood in circumstances beyond their control"
#guard a33.utf8ByteSize == 152
#guard errS (chk ["other lack of livelihood"] 1 a33) ==
  some "InvalidInput: act phrase for p has a comma outside a fixed phrase"

/-! ### Without `acts@0`: today's decoder, whatever the fixed phrases (`decodeRegulated_without_acts`) -/

#guard errS (canonicalActIn ["norms@0"] fx1 "p" 2 (.str a1)) == some "InvalidInput: invalid act phrase for p"
#guard okS (canonicalActIn ["acts@0"] fx1 "p" 2 (.str a1)) == some a1
#guard errReg (decodeRegulatedIn ["norms@0"] [] "p" ["person"]
    (.mkObj [("role", .str "plain"), ("default", .str "deny"), ("act", .str "{0} to seek asylum"),
      ("form", .str "has the right")])) == some "InvalidInput: invalid regulated fields for p"
#guard errReg (decodeRegulated "p" ["person"]
    (.mkObj [("role", .str "plain"), ("default", .str "deny"), ("form", .str "has the right")])) ==
  some "InvalidInput: invalid regulated fields for p"

/-! ### Limits and the diagnostics of `phraseToks` and `decodeFixed` -/

#guard maxActBytes == 400 && maxPhraseBytes == 300 && maxPhrases == 128
def letters : List Char := "abcdefghijklmnop".toList
/-- The `i`-th of 256 two-word phrases, no two of which overlap. -/
def phrase (i : Nat) : String :=
  let c := String.mk [letters.getD (i / 16) 'a', letters.getD (i % 16) 'a']
  "x" ++ c ++ " y" ++ c
#guard (decodeFixed ((List.range 128).map phrase)).isOk
#guard errFixed ((List.range 129).map phrase) == some "ResourceLimit: more than 128 fixed phrases"
def long (n : Nat) : String := "ab" ++ String.join (List.replicate n " ab")
#guard (long 99).utf8ByteSize == 299 && (decodeFixed [long 99 ++ "c"]).isOk
#guard errFixed [long 99 ++ "cd"] ==
  some s!"ResourceLimit: fixed phrase '{long 99 ++ "cd"}' is over 300 bytes"
-- the limit is on the canonical phrase: runs of spaces count once
#guard (decodeFixed ["ab   " ++ long 99 |>.drop 3 |>.push 'c']).isOk
#guard errFixed ["the court, ,of law"] ==
  some "InvalidInput: fixed phrase 'the court, ,of law' has a comma that does not follow a word"
#guard errFixed ["the court,"] == some "InvalidInput: fixed phrase 'the court,' has a comma that does not follow a word"
#guard errFixed ["the {1} court"] == some "InvalidInput: fixed phrase 'the {1} court' holds a slot"
#guard errFixed ["the c0urt"] == some "InvalidInput: fixed phrase 'the c0urt' has 'c0urt', which is not a word of letters"
#guard errFixed ["the court Is"] == some "InvalidInput: fixed phrase 'the court Is' uses the clause word 'Is'"
#guard errFixed ["court"] == some "InvalidInput: fixed phrase 'court' must hold two words or more"
#guard errFixed ["court ,"] == some "InvalidInput: fixed phrase 'court ,' has a comma that does not follow a word"
#guard errFixed ["the court For"] ==
  some "InvalidInput: fixed phrase 'the court For' must begin and end with a word other than and, or, nor and for"
#guard (decodeFixed ["court, tribunal"]).isOk
#guard errFixed ["the court", "the  court"] == some "InvalidInput: fixed phrase 'the  court' is declared twice"
-- a phrase that overlaps itself: its suffix `a b` begins it
#guard errFixed ["a b a b"] == some "InvalidInput: fixed phrases 'a b a b' and 'a b a b' overlap, or one holds the other"
#guard errFixed ["one two three", "two three"] ==
  some "InvalidInput: fixed phrases 'one two three' and 'two three' overlap, or one holds the other"
#guard errFixed ["two three", "one two"] ==
  some "InvalidInput: fixed phrases 'one two' and 'two three' overlap, or one holds the other"
#guard (decodeFixed ["one two", "three four", "two one"]).isOk == false
#guard (decodeFixed ["one two", "three four"]).isOk

/-! ### Each step of `check` and `lex` -/

-- words, slots and commas; whitespace normalised as `canonicalAct` does, U+2019 folded
#guard normal " {0}  seek\tasylum\n " == "{0} seek asylum" && fold "a’b’" == "a'b'" && fold "a‘b" == "a‘b"
#guard dropComma "asylum," == "asylum" && dropComma "asylum" == "asylum" && dropComma "," == ""
#guard slotOf? "{12}" == some 12 && slotOf? "{}" == none && slotOf? "{1a}" == none && slotOf? "x{1}" == none &&
  slotOf? "{1}x" == none
#guard toks [] "{0} seek {12}, asylum" == some [.slot 0, .word "seek", .slot 12, .comma, .word "asylum"]
#guard (lex [] "{0} seek ,asylum").toOption == none && (lex [] "{0} seek a,b").toOption == none
#guard (lex [] "{0} seek asylum,").toOption == none && (lex ["a b,"] "{0} seek asylum").toOption == none
-- every occurrence is grouped, at any position, and a word that only begins a phrase stays a word
#guard toks ["their country", "their own"] "{0} leave their country and their own country their" ==
  some [.slot 0, .word "leave", .fixed 0, .word "and", .fixed 1, .word "country", .word "their"]
-- the shape test of `canonicalAct`, with a word's final comma dropped
#guard errS (chk [] 1 "{1} seek asylum") == some "InvalidInput: invalid act phrase for p"
#guard errS (chk [] 1 "{0}seek asylum") == some "InvalidInput: invalid act phrase for p"
#guard errS (chk [] 1 "{0}") == some "InvalidInput: invalid act phrase for p"
#guard okS (chk [] 1 "{0} go") == some "{0} go"
#guard errS (chk [] 2 "{0} meet {1} {1}") == some "InvalidInput: invalid act phrase for p"
#guard errS (chk [] 1 "{0} seek asylum2") == some "InvalidInput: invalid act phrase for p"
#guard errS (check [] "p" 1 (.num 3)) == some "InvalidInput: invalid act phrase for p"
#guard okS (chk [] 2 "{0} meet a{1}") == some "{0} meet a{1}"
-- a clause word after a comma, in any case; the literal word `slot` is not one
#guard errS (chk [] 1 "{0} seek asylum, Then rest") ==
  some "InvalidInput: act phrase for p uses the clause word 'Then'; write the condition in the rule's guard"
#guard errS (chk ["seek asylum"] 1 "{0} seek asylum, rest") ==
  some "InvalidInput: act phrase for p has a comma outside a fixed phrase"
#guard okS (chk [] 1 "{0} book a slot") == some "{0} book a slot"
-- a join word in any case, after a fixed phrase that holds one; `for` is a join word in AP-1
#guard errS (chk ["equal pay for equal work"] 1 "{0} get equal pay for equal work FOR women") ==
  some "InvalidInput: act phrase for p joins acts with 'FOR' outside a fixed phrase"
-- the fixed phrases' diagnostics come through `check`
#guard errS (chk ["court"] 1 "{0} go") == some "InvalidInput: fixed phrase 'court' must hold two words or more"
-- the size limit is on the canonical act
#guard okS (chk [] 1 ("  " ++ a21 ++ "  ")) == some a21

/-! ### Wordings -/

#guard Form.ofText? "has the right" == some .right && Form.ofText? "is entitled" == some .entitled &&
  Form.ofText? "Has the right" == none && Form.ofText? "has the right " == none
#guard Form.text .right == "has the right" && Form.text .entitled == "is entitled"
#guard wording .right "{0} to seek asylum" == "{0} has the right to seek asylum"

end VE.Acts.LexicalExamples
