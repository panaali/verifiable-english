import VE.EnglishGrammar.SourceWords
import VE.EnglishGrammar.SourceReader
import VE.EnglishGrammar.Advice
import VE.EnglishGrammar.Policy
import VE.Alternatives.Wire
import VE.EnglishGrammar.JudgmentRunExamples

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

/-! ## `events@0`'s rows (ET-5; plan 2.7, spec 2.4 and 2.5, T9) -/

def eventsOf (word frame : String) : Option SourceWordKind :=
  (sourceWords.find? fun r => r.word == word && r.frame == frame && r.profile == "events@0").map (·.kind)

/-- T9: the twelve source words of 2.7, each refused in authored text with its advice and a rewrite. -/
def twelve : List String := ["until", "by", "within", "during", "while", "since", "always", "eventually",
  "whenever", "resulted in", "led to", "caused"]
#guard (sourceWords.filter (·.frame == "authored")).map (·.word) == twelve
#guard eventsOf "until" "authored" ==
  some (.refuse "events-until" eventsUntilAdvice "if it is not the case that that closure happens no later than that day")
#guard eventsOf "caused" "authored" == some (.refuse "events-caused" eventsLinkAdvice "that act was necessary for that harm")

/-- T9 through Lean's advice: a refused authored sentence under the profile gets its row's advice, and none without. -/
def adviceOf (profiles : List String) (s : String) : Option (String × String) :=
  match lex s with
  | .ok sents => (sents[0]?).bind fun toks => advice profiles toks.toList
  | .error _ => none
def ev : List String := ["events@0"]
#guard adviceOf ev "Every person may be presumed innocent until a conviction." == some ("events-until", eventsUntilAdvice)
#guard adviceOf ["norms@0", "relational-fol@0"] "Every person may be presumed innocent until a conviction." == none
#guard [("Every report must be filed by the deadline.", "events-by"), ("Every act happens within ten days.", "events-within"),
  ("Every person is protected during a stay.", "events-during"), ("Every person is protected while a stay lasts.", "events-while"),
  ("Every person has been protected since the conviction.", "events-since"), ("Every person is always protected.", "events-always"),
  ("Every person is eventually protected.", "events-eventually"), ("Every person is protected whenever a stay begins.", "events-whenever"),
  ("The act resulted in a harm.", "events-resulted-in"), ("The act led to a harm.", "events-led-to"),
  ("The act caused a harm.", "events-caused")].all fun (s, id) => (adviceOf ev s).map (·.1) == some id
#guard (adviceOf ev "The act caused a harm.").map (·.2) == some eventsLinkAdvice
-- A row matches through any of its patterns, not only its first ("brings about" is `alternatives-results`' second).
#guard (adviceOf ["alternatives@0"] "The act brings about a harm.").map (·.1) == some "alternatives-results"
-- DRI 2026-11-09 (reviews/dri-decisions-20261109-et-5.md item 2): an authored "always" gets its refusal and advice
-- (above), never a reading: its reading rows (et-5b) are the source frames, which `advice` does not read.
#guard (sourceWords.filter fun r => r.word == "always" && r.profile == "events@0").map (·.frame) ==
  ["authored", "source", "source no anchor"]
#guard (adviceOf ev "Every person is always protected.") == some ("events-always", eventsDaysAdvice)

/-! ## "always" and "eventually" (et-5b; spec 1.3, 2.4; DRI 2026-11-03 item 3, 2026-11-09 item 2) -/

/-- The reader on a source sentence: its words, the translator's lead-in, the document's anchor. -/
def readOf (word sentence : String) (leadIn : Option Bool) (a : AnchorState) : String × List String :=
  match sourceReadings word (ruleContext ((sentence.splitOn " ").filter (· != "")) leadIn) a with
  | .ok xs => ("ok", xs)
  | .error e => (e, [])
def a1 : String := "<clause> on each day."
def a2 : String := "<clause> on each day, if that day is on or after the date of this document."
def strictDefault : List String := ["<agent> must <act>.", "<agent> should <act>."]
-- The first 11-03 condition: "Claude should always <act>" gives soft-norms' {strict, default} READINGS and no events
-- A-candidate, whatever the anchor; so does a rule lead-in.
#guard [AnchorState.iso, .openTerm, .none].all fun a =>
  readOf "always" "Claude should always help" (some false) a == ("ok", strictDefault) &&
  readOf "always" "Claude always helps" (some true) a == ("ok", strictDefault)
#guard [AnchorState.iso, .openTerm, .none].all fun a =>
  !((readOf "always" "Claude should always help" none a).2.any fun w => w == a1 || w == a2)
-- The second: a descriptive "<x> always <verb>" with no ISO anchor gives A1 only; with one, A1 and A2.
#guard readOf "always" "The river always floods" (some false) .none == ("ok", [a1])
#guard readOf "always" "The river always floods" (some false) .openTerm == ("ok", [a1])
#guard readOf "always" "The river always floods" (some false) .iso == ("ok", [a1, a2])
-- Where it cannot be told which, the span stays UNFORMALISED `always-owner`, never both.
#guard readOf "always" "The river always floods" none .iso == ("always-owner", [])
-- "eventually" is no force word: E1 with no ISO anchor, E1 and E2 with one, inside a rule too.
#guard readOf "eventually" "Claude should eventually help" none .openTerm == ("ok", ["There is a day such that <clause> on that day."])
#guard (readOf "eventually" "The river eventually floods" (some false) .iso).2.length == 2
-- A deontic verb in any case is a rule; no deontic verb and no lead-in is not known.
#guard ruleContext ["Claude", "MUST", "always", "help"] none == .rule && ruleContext ["Claude", "always", "helps"] none == .unknown
-- The candidates a document with the open anchor term may not hold are the no-anchor rows' refused ones.
#guard anchorCandidates == ["A2", "E2"]
/-- The `english.grammar` export's advice ids, through `grammarCase` on JudgmentRunExamples' request (DELTA row 2). -/
def exportedAdvice : List String :=
  match (VE.EnglishGrammar.JudgmentRunExamples.shared []).head? with
  | some (.ok j) => (((j.getObjValD "result").getObjValD "advice").getArr?.toOption.getD #[]).toList.filterMap
      fun r => (r.getObjValD "id").getStr?.toOption
  | _ => []
#guard exportedAdvice == adviceTable.map (·.id)
#guard exportedAdvice.drop (exportedAdvice.length - 12) == twelve.map fun w => "events-" ++ w.replace " " "-"

-- U1 states its silence (ET-E1's rewording); U2 is ET-E1's measured sentence; T11d's W1-W3 (SR-B4), spec 8.1's
-- sentences with their dates and verb phrase as placeholders. The literals pin the rows' text.
#guard eventsOf "until" "source event" == some (.readings ([
  "<agent> <m> <act> on each day, if it is not the case that <event> <vp> no later than that day. This document does not say whether <agent> <m> <act> on a day on which <event> <vp> no later than that day.",
  "<agent> <m> <act> on each day, if it is not the case that <event> <vp> no later than that day. <agent> <opposite of m> <act> on each day, if <event> <vp> no later than that day."].map
  (⟨·, "E's day, the day before it and a later day: with the act unspecified, from E's day U1 does not say and U2 gives the opposite modality."⟩)))
#guard eventsOf "within" "source date" == some (.readings ([
  "<event> <vp> on or after <date>, and <event> <vp> no later than <end>.",
  "<event> <vp> on or after <date>, and <event> <vp> before <end>.",
  "<event> <vp> on or after <start>, and <event> <vp> no later than <end>."].map
  (⟨·, "An act on <end> (W1 and W3 against W2) and an act before <date> and on or after <start> (W3 against W1 and W2)."⟩)))
-- The profile-fixed wordings are Lean's checker's, in the frames `ve/english.py` reads.
#guard [("before", "before"), ("contributed to", "link contributed"), ("was necessary for", "link necessary")].map
    (fun (w, f) => eventsOf w f) ==
  [some (.fixed VE.Events.beforeWording), some (.fixed (VE.Events.linkWording .contributed)),
   some (.fixed (VE.Events.linkWording .necessary))]
/-- D11: the profile wordings (fixed and as candidates) are disjoint from `alternatives@0`'s and `risk@0`'s fixed wordings. -/
def eventsWordings : List String := sourceWords.flatMap fun r => match r.kind with
  | .fixed w => if r.profile == "events@0" then [w] else []
  | .readings cs => if r.profile == "events@0" then cs.map (·.wording) else []
  | .refuse .. => []
def otherProfileWordings : List String := VE.Alternatives.Wire.canonicalWording.map (·.2) ++ riskTemplates ++
  ["{0} is avoidable by {1}", "{0} is unavoidable by {1}", "{0} allows {1} to happen"]
#guard eventsWordings.length == 12
#guard eventsWordings.all fun w => !otherProfileWordings.contains w
#guard ["{0} leads to {1}", "{0} causes {1}", "{0} might lead to {1}", "{0} allows {1} to happen"].all
  otherProfileWordings.contains

end VE.EnglishGrammar.SourceWordsExamples
