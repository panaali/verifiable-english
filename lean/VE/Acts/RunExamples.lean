import VE.Acts.ReadingsExamples
import VE.Acts.Run

/-! Fixtures of the `act-readings` mode (docs/spec/act-phrases.md 7, 11.4; plan AP-4 Tests; DRI 2026-11-08 ap-4
item 1): the pilot's phrases through the mode with the counts the audit asks for, AR1's genuine answer for P11, the
token spans and indices, an adverb inside the last joined item (D4, ap-7 FAIL ruling item 2), and each limit on both
sides: the act phrase's 400 bytes, a fixed phrase's 300, 64 readings, the raw cap. -/

namespace VE.Acts.RunExamples
open Lean VE.Acts VE.Acts.Run VE.Acts.Examples VE.Acts.RuleExamples VE.Acts.TableExamples VE.Acts.MeaningExamples
  VE.Acts.ReadingsExamples

def frameJ (f : Frame) : Json := Json.mkObj [("head", .str (" ".intercalate f.head)), ("markers", toJson f.markers),
  ("split", toJson f.split), ("modifiers", toJson f.mods)]
def req (V : Vocab) (fx : List String) (s : String) (role : String := "plain") (sign := true) (form : Json := .null) :
    Json :=
  Json.mkObj [("id", "c"), ("phrase", .str s), ("fixed", toJson fx), ("frames", toJson (V.frames.map frameJ)),
    ("adverbs", toJson V.adverbs), ("role", .str role), ("sign", .bool sign), ("form", form)]
def row (j : Json) : Json := actReadingsReported j
def verdict (j : Json) : Json := (row j).getObjValD "verdict"
def diag (j : Json) : Json := (row j).getObjValD "diagnostic"
/-- The number of readings a `LISTED` row lists. -/
def count (j : Json) : Nat := match (row j).getObjValD "readings" with | .arr xs => xs.size | _ => 0
def acts (j : Json) (k : Nat) : List Json :=
  match (((row j).getObjValD "readings").getArrVal? k).toOption.map (·.getObjValD "acts") with
  | some (Json.arr xs) => xs.toList
  | _ => []
def paraphraseAt (j : Json) (k : Nat) : Option Json :=
  (((row j).getObjValD "readings").getArrVal? k).toOption.map (·.getObjValD "paraphrase")

/-! ### The pilot's phrases: A9, A10, A11 give 2 readings; A5, A8, A12 give 4 (plan AP-4 Tests) -/

#guard [count (req V9 fx9 g9s "permission" false), count (req V10 ["other lack of livelihood"] g10s),
  count (req V11 fx11 g11s), count (req V5 fx5 g5), count (req V8 fx8 g8), count (req V12 [] g12s)] ==
  [2, 2, 2, 4, 4, 4]
#guard [req V9 fx9 g9s "permission" false, req V11 fx11 g11s, req V8 fx8 g8].all (verdict · == "LISTED")
-- the counts are `phraseReadings`' (one owner), and each paraphrase is the table's
#guard count (req V8 fx8 g8) == (match pr V8 .right fx8 g8 with | .ok Rs => Rs.length | .limit => 0)
#guard paraphraseAt (req V9 fx9 g9s "permission" false) 1 == some (.str (paraphrase fx9 .mustNot none (atoms (g9 true))))
-- P9m: *may* on G9 has no reading (D-22's table cell), refused with the mode's text
#guard verdict (req V9 fx9 g9s "permission") == "REFUSED" && diag (req V9 fx9 g9s "permission") ==
  "InvalidInput: this act phrase has no reading under the declared frames and its modal words"

/-! ### AR1: Lean's genuine `LISTED` answer for P11, pinned (the relay's fuzz mutates this row) -/

#guard (row (req V11 fx11 g11s)).compress == "{\"id\":\"c\",\"readings\":[{\"acts\":[{\"act\":\"{0} to directly take part in {1}\",\"from\":[0,1,6,2,3,4,5],\"text\":\"{0} has the right to directly take part in {1}\"},{\"act\":\"{0} to take part in {1} through freely chosen representatives\",\"from\":[0,1,2,3,4,5,8,9],\"text\":\"{0} has the right to take part in {1} through freely chosen representatives\"}],\"paraphrase\":\"{0} has the right to directly take part in {1}, and {0} has the right to take part in {1} through freely chosen representatives.\"},{\"acts\":[{\"act\":\"{0} to directly take part in {1} or to take part in {1} through freely chosen representatives\",\"from\":[0,6,7,1,2,3,4,5,8,9],\"text\":\"{0} has the right to directly take part in {1} or to take part in {1} through freely chosen representatives\"}],\"paraphrase\":\"{0} has the right to directly take part in {1} or to take part in {1} through freely chosen representatives, as one act done in any one of these ways (not each way on its own).\"}],\"status\":\"ok\",\"tokens\":[[0,3],[4,6],[7,11],[12,16],[17,19],[20,23],[24,32],[33,35],[36,43],[44,73]],\"verdict\":\"LISTED\"}"

/-! ### Token spans and indices -/

-- spans are UTF-8 bytes of the phrase as written: runs of whitespace skipped, U+2019 (3 bytes) read as `'`
#guard spans [] "{0}  to\tseek  asylum’s" [.slot 0, .word "to", .word "seek", .word "asylum's"] ==
  some [(0, 3), (5, 7), (8, 12), (14, 24)]
-- a fixed phrase is one token, its span the whole phrase; a comma its own byte
#guard spans fx5 "{0} to seek in other countries, asylum" [.slot 0, .word "to", .word "seek", .word "in", .fixed 0,
  .comma, .word "asylum"] == some [(0, 3), (4, 6), (7, 11), (12, 14), (15, 30), (30, 31), (32, 38)]
#guard verdict (req V5 [] "{00} to seek asylum") == "REFUSED"
-- `from`: G12's split *join* reads the second *to*, its whole join every token once; G5's *enjoy* reads the shared
-- object after its modifier, in the act's order
#guard (acts (req V12 [] g12s) 0).map (·.getObjValD "from") == [toJson [0, 1, 2, 6, 7], toJson [0, 4, 5, 6, 7, 8, 9, 10,
  11, 12, 13]]
#guard (acts (req V12 [] g12s) 1).map (·.getObjValD "from") == [toJson (List.range 14)]
#guard (acts (req V5 fx5 g5) 0).map (·.getObjValD "from") == [toJson [0, 1, 2, 8, 9, 10], toJson [0, 4, 5, 8, 9, 10, 6, 7]]
-- a token the rendering adds and the phrase lacks has no index: *to* after *has the right* on a phrase without it
#guard fromOf [.slot 0, .word "seek", .word "asylum"] [.slot 0, .word "to", .word "seek", .word "asylum"] == [0, 1, 2]
-- an equal word is matched case-insensitively, as the grammar reads it, and never twice in one act
#guard fromOf [.slot 0, .word "To", .word "a", .word "to"] [.slot 0, .word "to", .word "to"] == [0, 1, 3]

/-! ### An adverb inside the last joined item reads over that item only (D4; ap-7 FAIL ruling item 2) -/

def lastAdv := "{0} to participate in the cultural life of the community, to enjoy the arts and to freely share in " ++
  "scientific advancement and its benefits"
#guard pr V8 .right fx8 lastAdv == .ok (eachOrTogether (g8t [false, false, true]))
#guard count (req V8 fx8 lastAdv "obligation") == 1 && count (req V8 fx8 lastAdv) == 2

/-! ### The limits on both sides (DRI 2026-11-08 ap-4 item 1) -/

-- the act phrase: 400 bytes listed, 401 a limit
def p400 := "{0} to seek" ++ String.join (List.replicate 193 " a") ++ " ab"
#guard p400.utf8ByteSize == 400 && verdict (req V5 [] p400) == "LISTED"
#guard verdict (req V5 [] (p400 ++ "c")) == "LIMIT" && diag (req V5 [] (p400 ++ "c")) ==
  "ResourceLimit: this act phrase is over 400 bytes"
-- a fixed phrase: 300 bytes read as one token, 301 refused with `decodeFixed`'s limit
def f300 := "ab" ++ String.join (List.replicate 149 " a")
#guard f300.utf8ByteSize == 300 && verdict (req V5 [f300] ("{0} to seek " ++ f300)) == "LISTED"
#guard verdict (req V5 [f300 ++ "c"] ("{0} to seek " ++ f300 ++ "c")) == "LIMIT"
-- 64 readings listed (P64: L6 under *must*), 65 or more a limit (P65: L6 under *must not*, 128); a saturated raw cap
-- (L8, 256 raw derivations) a limit
#guard count (req V5 cities (ln 6) "obligation") == 64 && verdict (req V5 cities (ln 6) "obligation") == "LISTED"
#guard [req V5 cities (ln 6) "permission" false, req V5 cities (ln 8)].all fun j =>
  verdict j == "LIMIT" && diag j == "ResourceLimit: this act phrase has too many readings to list; split the sentence"

/-! ### Other refusals: no modal word, the frames' D-31, a lexing fault; a malformed request is the case's error -/

#guard diag (req V5 fx5 g5 "plain" false) ==
  "InvalidInput: this act phrase has no modal word: a plain act with sign false"
#guard verdict (req ⟨[fr "seek" [""] [] [], fr "seek" [""] [] []], []⟩ [] g5) == "REFUSED"
#guard diag (req V5 fx5 "{0} to seek asylum,") == "InvalidInput: this act phrase ends with a comma"
#guard (row ((req V5 fx5 g5).setObjVal! "extra" .null)).getObjValD "status" == "error"
#guard (row ((req V5 fx5 g5).setObjVal! "form" "may")).getObjValD "status" == "error"

end VE.Acts.RunExamples
