import VE.EnglishGrammar.SourceWords

/-! Boundary fixtures for the Lean-owned source-word catalogue. No fixture row is exported. -/
namespace VE.EnglishGrammar.SourceWordsExamples

open VE.EnglishGrammar

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

#guard !sourceWordsValid [{ base with kind := .readings [] }]
#guard !sourceWordsValid [{ base with kind := .readings [a] }]
#guard sourceWordsValid [{ base with kind := .readings [a, b] }]
#guard !sourceWordsValid [{ base with kind := .readings [a, a] }]
#guard !sourceWordsValid [{ base with kind := .readings [a, reading "before" "Another situation."] }]
#guard sourceWordsValid [{ base with kind := .readings [a, b, reading "during" "One overlaps."] }]
#guard !sourceWordsValid [{ base with kind := .readings [reading "before" "", b] }]
#guard sourceWordsValid [{ base with kind := .readings [reading "before" "x", b] }]

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
#guard sourceWordsValid [refusal "x" "a" "before later"]

#guard sourceWordsValid [{ base with kind := .fixed "before" }]
#guard !sourceWordsValid [{ base with word := "Until" }]
#guard !sourceWordsValid [{ base with word := "" }]
#guard !sourceWordsValid [{ base with owner := "" }]
#guard sourceWordsValid [{ base with word := "in most cases" }]

end VE.EnglishGrammar.SourceWordsExamples
