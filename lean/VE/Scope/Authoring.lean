import Lean.Data.Json
import VE.Discourse.Access

/-! Scope's authoring wordings (docs/spec/scope.md 2.2, 5.8 and 8.1; SC-7): a writer types one of 2.2's wordings, and
    `Pinned.parseGovernor` gives the part of the scope@0 block (spec 3) the wording fixes; `Pinned.renderGovernor`
    writes the wording back, and `Pinned.paraphrase` gives 2.2's one reading for the IDE to show.

    A parsed block holds what the wording says and nothing the layout decides: the reach in spec 3's form where the
    wording names it (`{"list_name": n}`, `"frontier"`), otherwise what the wording says of it (`"list"`: the list this
    line leads; `{"anchor": {"heading": h, "level": k}}`: the section this heading opens; `{"anchor": {"section": s}}`:
    the section the wording numbers), and each condition or rule the English reader has still to read as
    `{"english": text}` at its place. Unit and anchor ids and the readings of those texts are the IDE's (sc-7b).

    Only 2.2's wordings are accepted, with no spacing or spelling variant (english-lean ruling 1): a wording is read
    by every row, and accepted only when exactly one row's block renders back to the same bytes; two readings are
    refused, never chosen. The list name, the condition, the rule, the section and the heading are the slots; every
    other word is fixed, and no slot but a title's heading ends a sentence (`clause`). -/

namespace VE.Scope
open Lean

namespace Pinned

/-- A character of a word: no space (`VE.Discourse.spaceChar`, Python's `str.isspace`), no control character (C0, DEL
    and C1: below U+0020, and U+007F to U+009F) and no filler drawn as a space (U+115F, U+1160, U+2800, U+3164, U+FFA0). -/
def wordChar (c : Char) : Bool := !VE.Discourse.spaceChar c && 0x20 ≤ c.toNat && !(0x7F ≤ c.toNat && c.toNat ≤ 0x9F) && ![0x115F, 0x1160, 0x2800, 0x3164, 0xFFA0].contains c.toNat

/-- Words with one space between them, no other space or control character, and at least one word. -/
def spaced (s : String) : Bool := (s.splitOn " ").all fun w => !w.isEmpty && w.all wordChar

/-- What may close a word after a sentence's end (`clause`): each character of Unicode 16.0's categories Pe (closing
    brackets), Pf and Pi (final and initial quotes: German and Danish close with “ and «), the quotes `"`, `'`, `＂` and
    `＇`, `>`, and Markdown's `*`, `_`, `` ` `` and `~`. -/
def closers : String := "\"')*>]_`}~«»༻༽᚜‘’‛“”‟‹›⁆⁾₎⌉⌋〉❩❫❭❯❱❳❵⟆⟧⟩⟫⟭⟯⦄⦆⦈⦊⦌⦎⦐⦒⦔⦖⦘⧙⧛⧽⸂⸃⸄⸅⸉⸊⸌⸍⸜⸝⸠⸡⸣⸥⸧⸩⹖⹘⹚⹜〉》」』】〕〗〙〛〞〟﴾︘︶︸︺︼︾﹀﹂﹄﹈﹚﹜﹞＂＇）］｝｠｣"

/-- Every slot's text (a condition, a rule, a list name, a section): spaced, and no word ends a sentence or a lead-in. Once
    its trailing `closers` and characters of Unicode 16.0's Cf, Mn, Me, Default_Ignorable_Code_Point and U+2800 are dropped
    (mixed in any order), a word's last character is no Unicode 16.0 Sentence_Terminal, no ":" and none whose NFKC form ends
    in one of them ("…", "：", "︖", "⒈", "㏂"); `wordChar` refuses U+115F, U+1160, U+2800, U+3164, U+FFA0 anywhere. -/
def clause (s : String) : Bool := spaced s && (s.splitOn " ").all fun w => !"!.:?։؝؞؟۔܀܁܂߹࠷࠹࠽࠾।॥၊။።፧፨᙮᜵᜶។៕᠃᠉᥄᥅᪨᪩᪪᪫᭎᭏᭚᭛᭞᭟᭽᭾᭿᰻᰼᱾᱿․‥…‼‽⁇⁈⁉⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑⒒⒓⒔⒕⒖⒗⒘⒙⒚⒛⸮⸼⹓⹔。㏂㏇㏘꓿꘎꘏꛳꛷꡶꡷꣎꣏꤯꧈꧉꩝꩞꩟꫰꫱꯫︒︓︕︖︙︰﹒﹕﹖﹗！．：？｡𐩖𐩗𐽕𐽖𐽗𐽘𐽙𐾆𐾇𐾈𐾉𑁇𑁈𑂾𑂿𑃀𑃁𑅁𑅂𑅃𑇅𑇆𑇍𑇞𑇟𑈸𑈹𑈻𑈼𑊩𑏔𑏕𑑋𑑌𑗂𑗃𑗉𑗊𑗋𑗌𑗍𑗎𑗏𑗐𑗑𑗒𑗓𑗔𑗕𑗖𑗗𑙁𑙂𑜼𑜽𑜾𑥄𑥆𑩂𑩃𑪛𑪜𑱁𑱂𑻷𑻸𑽃𑽄𖩮𖩯𖫵𖬷𖬸𖭄𖵮𖵯𖺘𛲟𝪈🄀".contains (w.dropRightWhile fun c =>
  closers.contains c || #[(0xAD,0xAD), (0x300,0x36F), (0x483,0x489), (0x591,0x5BD), (0x5BF,0x5BF), (0x5C1,0x5C2), (0x5C4,0x5C5), (0x5C7,0x5C7), (0x600,0x605), (0x610,0x61A), (0x61C,0x61C), (0x64B,0x65F), (0x670,0x670), (0x6D6,0x6DD), (0x6DF,0x6E4), (0x6E7,0x6E8), (0x6EA,0x6ED), (0x70F,0x70F), (0x711,0x711), (0x730,0x74A), (0x7A6,0x7B0), (0x7EB,0x7F3), (0x7FD,0x7FD), (0x816,0x819), (0x81B,0x823), (0x825,0x827), (0x829,0x82D), (0x859,0x85B), (0x890,0x891), (0x897,0x89F), (0x8CA,0x902), (0x93A,0x93A), (0x93C,0x93C), (0x941,0x948), (0x94D,0x94D), (0x951,0x957), (0x962,0x963), (0x981,0x981), (0x9BC,0x9BC), (0x9C1,0x9C4), (0x9CD,0x9CD), (0x9E2,0x9E3), (0x9FE,0x9FE), (0xA01,0xA02), (0xA3C,0xA3C), (0xA41,0xA42), (0xA47,0xA48), (0xA4B,0xA4D), (0xA51,0xA51), (0xA70,0xA71), (0xA75,0xA75), (0xA81,0xA82), (0xABC,0xABC), (0xAC1,0xAC5), (0xAC7,0xAC8), (0xACD,0xACD), (0xAE2,0xAE3), (0xAFA,0xAFF), (0xB01,0xB01), (0xB3C,0xB3C), (0xB3F,0xB3F), (0xB41,0xB44), (0xB4D,0xB4D), (0xB55,0xB56), (0xB62,0xB63), (0xB82,0xB82), (0xBC0,0xBC0), (0xBCD,0xBCD), (0xC00,0xC00), (0xC04,0xC04), (0xC3C,0xC3C), (0xC3E,0xC40), (0xC46,0xC48), (0xC4A,0xC4D), (0xC55,0xC56), (0xC62,0xC63), (0xC81,0xC81), (0xCBC,0xCBC), (0xCBF,0xCBF), (0xCC6,0xCC6), (0xCCC,0xCCD), (0xCE2,0xCE3), (0xD00,0xD01), (0xD3B,0xD3C), (0xD41,0xD44), (0xD4D,0xD4D), (0xD62,0xD63), (0xD81,0xD81), (0xDCA,0xDCA), (0xDD2,0xDD4), (0xDD6,0xDD6), (0xE31,0xE31), (0xE34,0xE3A), (0xE47,0xE4E), (0xEB1,0xEB1), (0xEB4,0xEBC), (0xEC8,0xECE), (0xF18,0xF19), (0xF35,0xF35), (0xF37,0xF37), (0xF39,0xF39), (0xF71,0xF7E), (0xF80,0xF84), (0xF86,0xF87), (0xF8D,0xF97), (0xF99,0xFBC), (0xFC6,0xFC6), (0x102D,0x1030), (0x1032,0x1037), (0x1039,0x103A), (0x103D,0x103E), (0x1058,0x1059), (0x105E,0x1060), (0x1071,0x1074), (0x1082,0x1082), (0x1085,0x1086), (0x108D,0x108D), (0x109D,0x109D), (0x115F,0x1160), (0x135D,0x135F), (0x1712,0x1714), (0x1732,0x1733), (0x1752,0x1753), (0x1772,0x1773), (0x17B4,0x17B5), (0x17B7,0x17BD), (0x17C6,0x17C6), (0x17C9,0x17D3), (0x17DD,0x17DD), (0x180B,0x180F), (0x1885,0x1886), (0x18A9,0x18A9), (0x1920,0x1922), (0x1927,0x1928), (0x1932,0x1932), (0x1939,0x193B), (0x1A17,0x1A18), (0x1A1B,0x1A1B), (0x1A56,0x1A56), (0x1A58,0x1A5E), (0x1A60,0x1A60), (0x1A62,0x1A62), (0x1A65,0x1A6C), (0x1A73,0x1A7C), (0x1A7F,0x1A7F), (0x1AB0,0x1ACE), (0x1B00,0x1B03), (0x1B34,0x1B34), (0x1B36,0x1B3A), (0x1B3C,0x1B3C), (0x1B42,0x1B42), (0x1B6B,0x1B73), (0x1B80,0x1B81), (0x1BA2,0x1BA5), (0x1BA8,0x1BA9), (0x1BAB,0x1BAD), (0x1BE6,0x1BE6), (0x1BE8,0x1BE9), (0x1BED,0x1BED), (0x1BEF,0x1BF1), (0x1C2C,0x1C33), (0x1C36,0x1C37), (0x1CD0,0x1CD2), (0x1CD4,0x1CE0), (0x1CE2,0x1CE8), (0x1CED,0x1CED), (0x1CF4,0x1CF4), (0x1CF8,0x1CF9), (0x1DC0,0x1DFF), (0x200B,0x200F), (0x202A,0x202E), (0x2060,0x206F), (0x20D0,0x20F0), (0x2800,0x2800), (0x2CEF,0x2CF1), (0x2D7F,0x2D7F), (0x2DE0,0x2DFF), (0x302A,0x302D), (0x3099,0x309A), (0x3164,0x3164), (0xA66F,0xA672), (0xA674,0xA67D), (0xA69E,0xA69F), (0xA6F0,0xA6F1), (0xA802,0xA802), (0xA806,0xA806), (0xA80B,0xA80B), (0xA825,0xA826), (0xA82C,0xA82C), (0xA8C4,0xA8C5), (0xA8E0,0xA8F1), (0xA8FF,0xA8FF), (0xA926,0xA92D), (0xA947,0xA951), (0xA980,0xA982), (0xA9B3,0xA9B3), (0xA9B6,0xA9B9), (0xA9BC,0xA9BD), (0xA9E5,0xA9E5), (0xAA29,0xAA2E), (0xAA31,0xAA32), (0xAA35,0xAA36), (0xAA43,0xAA43), (0xAA4C,0xAA4C), (0xAA7C,0xAA7C), (0xAAB0,0xAAB0), (0xAAB2,0xAAB4), (0xAAB7,0xAAB8), (0xAABE,0xAABF), (0xAAC1,0xAAC1), (0xAAEC,0xAAED), (0xAAF6,0xAAF6), (0xABE5,0xABE5), (0xABE8,0xABE8), (0xABED,0xABED), (0xFB1E,0xFB1E), (0xFE00,0xFE0F), (0xFE20,0xFE2F), (0xFEFF,0xFEFF), (0xFFA0,0xFFA0), (0xFFF0,0xFFFB), (0x101FD,0x101FD), (0x102E0,0x102E0), (0x10376,0x1037A), (0x10A01,0x10A03), (0x10A05,0x10A06), (0x10A0C,0x10A0F), (0x10A38,0x10A3A), (0x10A3F,0x10A3F), (0x10AE5,0x10AE6), (0x10D24,0x10D27), (0x10D69,0x10D6D), (0x10EAB,0x10EAC), (0x10EFC,0x10EFF), (0x10F46,0x10F50), (0x10F82,0x10F85), (0x11001,0x11001), (0x11038,0x11046), (0x11070,0x11070), (0x11073,0x11074), (0x1107F,0x11081), (0x110B3,0x110B6), (0x110B9,0x110BA), (0x110BD,0x110BD), (0x110C2,0x110C2), (0x110CD,0x110CD), (0x11100,0x11102), (0x11127,0x1112B), (0x1112D,0x11134), (0x11173,0x11173), (0x11180,0x11181), (0x111B6,0x111BE), (0x111C9,0x111CC), (0x111CF,0x111CF), (0x1122F,0x11231), (0x11234,0x11234), (0x11236,0x11237), (0x1123E,0x1123E), (0x11241,0x11241), (0x112DF,0x112DF), (0x112E3,0x112EA), (0x11300,0x11301), (0x1133B,0x1133C), (0x11340,0x11340), (0x11366,0x1136C), (0x11370,0x11374), (0x113BB,0x113C0), (0x113CE,0x113CE), (0x113D0,0x113D0), (0x113D2,0x113D2), (0x113E1,0x113E2), (0x11438,0x1143F), (0x11442,0x11444), (0x11446,0x11446), (0x1145E,0x1145E), (0x114B3,0x114B8), (0x114BA,0x114BA), (0x114BF,0x114C0), (0x114C2,0x114C3), (0x115B2,0x115B5), (0x115BC,0x115BD), (0x115BF,0x115C0), (0x115DC,0x115DD), (0x11633,0x1163A), (0x1163D,0x1163D), (0x1163F,0x11640), (0x116AB,0x116AB), (0x116AD,0x116AD), (0x116B0,0x116B5), (0x116B7,0x116B7), (0x1171D,0x1171D), (0x1171F,0x1171F), (0x11722,0x11725), (0x11727,0x1172B), (0x1182F,0x11837), (0x11839,0x1183A), (0x1193B,0x1193C), (0x1193E,0x1193E), (0x11943,0x11943), (0x119D4,0x119D7), (0x119DA,0x119DB), (0x119E0,0x119E0), (0x11A01,0x11A0A), (0x11A33,0x11A38), (0x11A3B,0x11A3E), (0x11A47,0x11A47), (0x11A51,0x11A56), (0x11A59,0x11A5B), (0x11A8A,0x11A96), (0x11A98,0x11A99), (0x11C30,0x11C36), (0x11C38,0x11C3D), (0x11C3F,0x11C3F), (0x11C92,0x11CA7), (0x11CAA,0x11CB0), (0x11CB2,0x11CB3), (0x11CB5,0x11CB6), (0x11D31,0x11D36), (0x11D3A,0x11D3A), (0x11D3C,0x11D3D), (0x11D3F,0x11D45), (0x11D47,0x11D47), (0x11D90,0x11D91), (0x11D95,0x11D95), (0x11D97,0x11D97), (0x11EF3,0x11EF4), (0x11F00,0x11F01), (0x11F36,0x11F3A), (0x11F40,0x11F40), (0x11F42,0x11F42), (0x11F5A,0x11F5A), (0x13430,0x13440), (0x13447,0x13455), (0x1611E,0x16129), (0x1612D,0x1612F), (0x16AF0,0x16AF4), (0x16B30,0x16B36), (0x16F4F,0x16F4F), (0x16F8F,0x16F92), (0x16FE4,0x16FE4), (0x1BC9D,0x1BC9E), (0x1BCA0,0x1BCA3), (0x1CF00,0x1CF2D), (0x1CF30,0x1CF46), (0x1D167,0x1D169), (0x1D173,0x1D182), (0x1D185,0x1D18B), (0x1D1AA,0x1D1AD), (0x1D242,0x1D244), (0x1DA00,0x1DA36), (0x1DA3B,0x1DA6C), (0x1DA75,0x1DA75), (0x1DA84,0x1DA84), (0x1DA9B,0x1DA9F), (0x1DAA1,0x1DAAF), (0x1E000,0x1E006), (0x1E008,0x1E018), (0x1E01B,0x1E021), (0x1E023,0x1E024), (0x1E026,0x1E02A), (0x1E08F,0x1E08F), (0x1E130,0x1E136), (0x1E2AE,0x1E2AE), (0x1E2EC,0x1E2EF), (0x1E4EC,0x1E4EF), (0x1E5EE,0x1E5EF), (0x1E8D0,0x1E8D6), (0x1E944,0x1E94A), (0xE0000,0xE0FFF)].binSearchContains (c.toNat, c.toNat) fun x y => x.2 < y.1).back

/-- A list name: "the" and at least one more word ("the hard constraints"), a slot (`clause`). -/
def listName (n : String) : Bool := n.startsWith "the " && clause n

/-- The list name at the start of a sentence, and back. -/
def cap (n : String) : String := "The" ++ n.drop 3
def uncap (h : String) : Option String := if h.startsWith "The " then some ("the" ++ h.drop 3) else none

def frameWording : String := "Every instance of Claude must not:"
/-- The condition of the "In place of" row (F3's): the attitude words of spec 3's `g2`. -/
def kindWording : String := "Claude knows that the act is of its kind, or thinks it quite likely that it is"

def english (s : String) : Json := Json.mkObj [("english", .str s)]
def narrowing (c : String) : Json := Json.mkObj [("reguard", Json.arr #[.str "and", .str "own", english c])]
def attitude (mode : String) (degree : Option String) : Json :=
  let holder := Json.arr #[.str "var", toJson (0 : Nat)]
  Json.mkObj [("attitude", match degree with
    | none => Json.mkObj [("holder", holder), ("mode", .str mode), ("content", .str "own")]
    | some d => Json.mkObj [("holder", holder), ("mode", .str mode), ("degree", .str d), ("content", .str "own")])]
/-- F3's condition, as spec 3's `g2` writes it. -/
def kindCondition : Json :=
  Json.arr #[.str "or", Json.arr #[.str "and", .str "own", attitude "knows" none], attitude "thinks" (some "quite likely")]
def frameBlock : Json := Json.mkObj [("reach", .str "list"), ("effect", Json.mkObj [("frame",
  Json.mkObj [("sign", .bool false), ("unless", Json.arr #[]), ("over", Json.arr #[])])])]
def onName (n : String) (effect : Json) : Json := Json.mkObj [("reach", Json.mkObj [("list_name", .str n)]), ("effect", effect)]
def heading (k : Nat) (h : String) (effect : Json) : Json :=
  Json.mkObj [("reach", Json.mkObj [("anchor", Json.mkObj [("heading", .str h), ("level", toJson k)])]), ("effect", effect)]

/-- 2.2's rows, each with its slots. -/
inductive Row where
  | frame | named (n : String) | narrowed (n c : String) | inPlace (n : String) | carved (n c : String)
  | precedes (s r : String) | whenHeading (k : Nat) (h c : String) | title (k : Nat) (h : String) | frontier (c : String)
  deriving Repr, DecidableEq

def textOf (j : Json) : String := j.getStr?.toOption.getD ""
def englishOf (j : Json) : String := textOf (j.getObjValD "english")
def narrowed? (e : Json) : Option String :=
  match e.getObjValD "reguard" with
  | .arr #[.str "and", .str "own", c] => some (englishOf c)
  | _ => none

/-- The row a block is written by. -/
def classify (b : Json) : Row :=
  let r := b.getObjValD "reach"
  let e := b.getObjValD "effect"
  let n := textOf (r.getObjValD "list_name")
  let a := r.getObjValD "anchor"
  let k := (a.getObjValD "level").getNat?.toOption.getD 0
  match b.getObjValD "list_name", r, a.getObjValD "section", a.getObjValD "heading" with
  | .str m, _, _, _ => .named m
  | _, .str "list", _, _ => .frame
  | _, .str "frontier", _, _ => .frontier ((narrowed? e).getD "")
  | _, _, .str s, _ => .precedes s (englishOf (b.getObjValD "rule"))
  | _, _, _, .str h => match narrowed? e with
    | some c => .whenHeading k h c
    | none => .title k h
  | _, _, _, _ =>
    if e.getObjValD "reguard" == kindCondition then .inPlace n
    else match narrowed? e with
    | some c => .narrowed n c
    | none => .carved n (englishOf (e.getObjValD "carve_out"))

/-- 2.2's wording of a row. -/
def Row.wording : Row → String
  | .frame => frameWording
  | .named n => s!"The rules below are called {n}."
  | .narrowed n c => s!"{cap n} apply only where {c}."
  | .inPlace n => s!"In place of their own condition, {n} apply only where {kindWording}."
  | .carved n c => s!"{cap n} do not apply when {c}."
  | .precedes s r => s!"Notwithstanding the rules of section {s}, {r}."
  | .whenHeading k h _ | .title k h => "".pushn '#' k ++ " " ++ h
  | .frontier c => s!"This applies only where {c}."

def renderGovernor (b : Json) : String := (classify b).wording

/-- What the paraphrase reads from the document, not the wording: the number of rules a list name covers, the default
    sentence of each rule's predicate (W1 2.5), the governor's own rule's name, and for a frontier reach the one
    candidate established to fit ("the rule above", "the list above"; SC-5), none for a question. -/
structure Context where
  count : Nat := 0
  defaults : String := ""
  rule : String := ""
  fits : Option String := none

/-- 2.2's right column: the one reading the IDE shows. -/
def Row.paraphrase (x : Context) : Row → String
  | .frame => s!"Each item below is its own rule: ‘{frameWording.dropRight 1} <item>.’"
  | .named n => s!"‘{cap n}’ names the rules of the list that follows."
  | .narrowed n c => s!"Each of the {x.count} rules called ‘{n}’ applies only where {c}."
  | .inPlace _ => s!"Each of the {x.count} rules now applies where {kindWording}, instead of where its own act occurs; " ++
      "its existing carve-outs still apply. ‘Its kind’ is each rule's own act."
  | .carved _ c => s!"None of the {x.count} rules applies when {c}; other rules may decide; if none does, {x.defaults}."
  | .precedes s _ => s!"Wherever {x.rule}, or a rule that takes precedence over it directly or through other rules, " ++
      s!"applies, no rule of section {s} decides on that act."
  | .whenHeading _ h c =>
    s!"Every rule in this section applies only {if h.startsWith "If " then "if" else "when"} {c}."
  | .title _ _ => "A title: it changes no rule."
  | .frontier _ => match x.fits with
    | some f => s!"This qualifies {f}."
    | none => "Which rule or list above does this qualify?"

def paraphrase (x : Context) (b : Json) : String := (classify b).paraphrase x

def between (w pre suf : String) : Option String :=
  (w.dropPrefix? pre).bind fun s => (s.toString.dropSuffix? suf).map (·.toString)
def splitOnce (w sep : String) : Option (String × String) :=
  match w.splitOn sep with
  | [a, b] => some (a, b)
  | _ => none

/-- A list-name row "<The name> <verb> <condition>.": the name and the condition. -/
def onList (w verb : String) : Option (String × String) := do
  let (h, rest) ← splitOnce w s!" {verb} "
  let n ← uncap h
  let c ← (rest.dropSuffix? ".").map (·.toString)
  if listName n && clause c then some (n, c) else none

/-- A heading of level 1 to 6: a full "When"/"If" clause narrows its section; any other heading is a title. A heading
    whose first word is "When" or "If" and whose rest is no `clause` ("When should I?", "If so, ask!") is refused. -/
def readHeading (w : String) : Option Json := do
  let k := (w.takeWhile (· == '#')).length
  let h ← ((w.drop k).dropPrefix? " ").map (·.toString)
  if !(1 ≤ k && k ≤ 6 && spaced h) then none
  match h.splitOn " " with
  | first :: rest =>
    if first == "When" || first == "If" then
      let c := " ".intercalate rest
      if clause c then some (heading k h (narrowing c)) else none
    else some (heading k h (.str "title"))
  | [] => none

/-- Every row's block for `w`, before the rendering test. -/
def readings (w : String) : List Json :=
  [if w == frameWording then some frameBlock else none,
   (between w "The rules below are called " ".").bind fun n =>
     if listName n then some (Json.mkObj [("list_name", .str n)]) else none,
   (onList w "apply only where").bind fun (n, c) =>
     if (c.splitOn "its kind").length == 1 then some (onName n (narrowing c)) else none,
   (between w "In place of their own condition, " s!" apply only where {kindWording}.").bind fun n =>
     if listName n then some (onName n (Json.mkObj [("reguard", kindCondition)])) else none,
   (onList w "do not apply when").map fun (n, c) => onName n (Json.mkObj [("carve_out", english c)]),
   (between w "Notwithstanding the rules of section " ".").bind fun rest =>
     match rest.splitOn ", " with
     | s :: more => let r := ", ".intercalate more
       if clause s && s.all (fun ch => ch != ' ' && ch != ',') && clause r then
         some (Json.mkObj [("reach", Json.mkObj [("anchor", Json.mkObj [("section", .str s)])]),
           ("effect", .str "precedes"), ("rule", english r)])
       else none
     | [] => none,
   readHeading w,
   (between w "This applies only where " ".").bind fun c =>
     if clause c then some (Json.mkObj [("reach", .str "frontier"), ("effect", narrowing c)]) else none].filterMap id

/-- The block of an authoring wording: the one row's block that renders back to `w`, or none (not a wording of 2.2, or
    two readings). -/
def parseGovernor (w : String) : Option Json :=
  match (readings w).filter (renderGovernor · == w) with
  | [b] => some b
  | _ => none

end Pinned

theorem scope_parseRender (w : String) (b : Json) (h : Pinned.parseGovernor w = some b) :
    Pinned.renderGovernor b = w := by
  unfold Pinned.parseGovernor at h
  split at h
  · rename_i hf
    cases h
    have hm : b ∈(Pinned.readings w).filter (Pinned.renderGovernor · == w) := by rw [hf]; simp
    simpa using (List.mem_filter.mp hm).2
  · cases h

theorem scope_renderParse (w : String) (b : Json) (h : Pinned.parseGovernor w = some b) :
    Pinned.parseGovernor (Pinned.renderGovernor b) = some b := by
  rw [scope_parseRender w b h]
  exact h

end VE.Scope
