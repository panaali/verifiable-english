import VE.EnglishGrammar.SourceWords

/-! Boundary fixtures for the Lean-owned source-word catalogue. No fixture row is exported. -/
namespace VE.EnglishGrammar.SourceWordsExamples

open VE.EnglishGrammar
open Lean

def reading (wording situation : String) : SourceWordReading := ⟨wording, situation⟩
def a : SourceWordReading := reading "before" "The first event ended before the second."
def b : SourceWordReading := reading "by" "The second event began by the deadline."
def base : SourceWordRow := ⟨"until", "", "", "ET-5", .readings [a, b]⟩

#guard sourceWordsValid []
#guard sourceWordsValid [base]
#guard !sourceWordsValid [base, base]
#guard sourceWordsValid [base, { base with frame := "time clause" }]
#guard sourceWordsValid [base, { base with profile := "events@0" }]
#guard sourceWordsValid [base, { base with word := "by" }]
#guard !sourceWordsValid [base, { base with word := "by", owner := "" }]
#guard !sourceWordsValid [{ base with word := "by", owner := "" }, base]

#guard !sourceWordsValid [{ base with kind := .readings [] }]
#guard !sourceWordsValid [{ base with kind := .readings [a] }]
#guard sourceWordsValid [{ base with kind := .readings [a, b] }]
#guard !sourceWordsValid [{ base with kind := .readings [a, a] }]
#guard !sourceWordsValid [{ base with kind := .readings [a, reading "before" "Another situation."] }]
#guard !sourceWordsValid [{ base with kind := .readings [a, reading "Before" "Another situation."] }]
#guard !sourceWordsValid [{ base with kind := .readings [a, reading "BEFORE" "Another situation."] }]
#guard !sourceWordsValid [{ base with kind := .readings [a, reading "before  " "Another situation."] }]
#guard !sourceWordsValid [{ base with kind := .readings [reading "  " "A situation.", b] }]
#guard sourceWordsValid [{ base with kind := .readings [a, b, reading "during" "One overlaps."] }]
#guard !sourceWordsValid [{ base with kind := .readings [reading "before" "", b] }]
#guard sourceWordsValid [{ base with kind := .readings [reading "before" "x", b] }]
#guard !sourceWordsValid [{ base with kind := .readings [a, reading "by" ""] }]

def refusal (code advice rewrite : String) : SourceWordRow :=
  { base with kind := .refuse code advice rewrite }
#guard sourceWordsValid [refusal "SW01" "Use a dated phrase." "before the deadline"]
#guard !sourceWordsValid [refusal "" "a" "b"]
#guard sourceWordsValid [refusal "x" "a" "b"]
#guard !sourceWordsValid [refusal "x" "" "b"]
#guard sourceWordsValid [refusal "x" "a" "b"]
#guard !sourceWordsValid [refusal "x" "a" ""]
#guard sourceWordsValid [refusal "x" "a" "b"]
#guard !sourceWordsValid [refusal "x" "a" "until"]
#guard !sourceWordsValid [refusal "x" "a" "before until later"]
#guard !sourceWordsValid [refusal "x" "a" "preuntilpost"]
#guard !sourceWordsValid [refusal "x" "a" "Until noon"]
#guard !sourceWordsValid [refusal "x" "a" "UNTIL noon"]
#guard !sourceWordsValid [{ base with word := "in most cases", kind := .refuse "x" "a" "in  most cases" }]
#guard !sourceWordsValid [{ base with word := "in most cases", kind := .refuse "x" "a" "in\tmost cases" }]
#guard !sourceWordsValid [{ base with word := "in most cases", kind := .refuse "x" "a" "in\u00A0most cases" }]
#guard !sourceWordsValid [{ base with word := "k", kind := .refuse "x" "a" "\u212A" }]
#guard !sourceWordsValid [{ base with word := "i", kind := .refuse "x" "a" "\u0130" }]
#guard !sourceWordsValid [{ base with word := "s", kind := .refuse "x" "a" "\u017F" }]
#guard sourceWordsValid [refusal "x" "a" "before later"]

#guard sourceWordsValid [{ base with kind := .fixed "before" }]
#guard !sourceWordsValid [{ base with kind := .fixed "  " }]
#guard !sourceWordsValid [{ base with word := "Until" }]
#guard !sourceWordsValid [{ base with word := "uNtil" }]
#guard !sourceWordsValid [{ base with word := "" }]
#guard !sourceWordsValid [{ base with word := " " }]
#guard !sourceWordsValid [{ base with word := "Ünder" }]
#guard !sourceWordsValid [{ base with word := "in\tmost cases" }]
#guard !sourceWordsValid [{ base with word := "in  most cases" }]
#guard !sourceWordsValid [{ base with owner := "" }]
#guard sourceWordsValid [{ base with word := "x", owner := "x" }]
#guard sourceWordsValid [{ base with word := "in most cases" }]

def kindReadingJson : Json := Json.mkObj [
  ("type", "readings"), ("candidates", Json.arr #[
    Json.mkObj [("wording", "before"), ("situation", a.situation)],
    Json.mkObj [("wording", "by"), ("situation", b.situation)]])]
def kindRefuseJson : Json := Json.mkObj [
  ("type", "refuse"), ("code", "SW01"), ("advice", "Use a dated phrase."),
  ("rewrite", "before the deadline")]
def kindFixedJson : Json := Json.mkObj [("type", "fixed"), ("wording", "before")]
def rowJson (word kind : Json) : Json := Json.mkObj [
  ("word", word), ("frame", ""), ("profile", ""), ("owner", "ET-5"), ("kind", kind)]

#guard SourceWordKind.toJson base.kind == kindReadingJson
#guard SourceWordKind.toJson (refusal "SW01" "Use a dated phrase." "before the deadline").kind == kindRefuseJson
#guard SourceWordKind.toJson (.fixed "before") == kindFixedJson
#guard SourceWordRow.toJson base == rowJson "until" kindReadingJson
#guard SourceWordRow.toJson { base with frame := "time", profile := "events@0", owner := "ET-6" } ==
  Json.mkObj [("word", "until"), ("frame", "time"), ("profile", "events@0"),
    ("owner", "ET-6"), ("kind", kindReadingJson)]
#guard sourceWordsJson [base, refusal "SW01" "Use a dated phrase." "before the deadline"] ==
  Json.mkObj [("format", "ve.source-words@1"),
    ("rows", Json.arr #[rowJson "until" kindReadingJson, rowJson "until" kindRefuseJson])]
#guard sourceWordsJson == sourceWordsJson sourceWords

end VE.EnglishGrammar.SourceWordsExamples
