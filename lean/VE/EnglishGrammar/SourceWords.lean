import VE.EnglishGrammar.Lexer
import VE.Events.Decl
import Lean

/-! The one Lean-owned catalogue of source-word reading sets, refusals and profile-fixed wordings.
Rows are added by the owning English batches, rows only (X9); `events@0`'s are ET-5's. -/

namespace VE.EnglishGrammar
open Lean

/-- A candidate wording and a sentence describing a situation that distinguishes it. -/
structure SourceWordReading where
  wording : String
  situation : String
  deriving DecidableEq, Repr

inductive SourceWordKind where
  | readings (candidates : List SourceWordReading)
  | refuse (code advice rewrite : String)
  | fixed (wording : String)
  deriving DecidableEq, Repr

/-- The source phrase, context, profile and plan-item owner of one reading decision. -/
structure SourceWordRow where
  word : String
  frame : String
  profile : String
  owner : String
  kind : SourceWordKind
  deriving DecidableEq, Repr

/-- Compare catalogue phrases using the lexer's whitespace and the English terminal's case fold. -/
def sourceWordNormal (s : String) : String :=
  fold (" ".intercalate ((s.split isSpace).filter (· != "")))

/-- A refused word may not occur even as a substring of the suggested rewrite. -/
def SourceWordRow.validKind (row : SourceWordRow) : Bool :=
  match row.kind with
  | .readings candidates =>
      candidates.length ≥ 2 &&
      (candidates.map (sourceWordNormal ∘ SourceWordReading.wording)).Nodup &&
      candidates.all (fun c => !((sourceWordNormal c.wording).isEmpty) &&
        !((sourceWordNormal c.situation).isEmpty))
  | .refuse code advice rewrite =>
      !(sourceWordNormal code).isEmpty && !(sourceWordNormal advice).isEmpty &&
      !(sourceWordNormal rewrite).isEmpty &&
      ((sourceWordNormal rewrite).splitOn row.word).length == 1
  | .fixed wording => !(sourceWordNormal wording).isEmpty

/-- Every row has a canonical ASCII source phrase and a plan-item owner. -/
def SourceWordRow.validIdentity (row : SourceWordRow) : Bool :=
  !row.word.isEmpty && row.word.toList.all (fun c => c.toNat < 128) &&
  sourceWordNormal row.word == row.word && !(sourceWordNormal row.owner).isEmpty

def SourceWordRow.key (row : SourceWordRow) : String × String × String :=
  (row.word, row.frame, row.profile)

/-- All catalogue invariants are checked by Lean, including the contextual key. -/
def sourceWordsValid (rows : List SourceWordRow) : Bool :=
  (rows.map SourceWordRow.key).Nodup &&
  rows.all (fun row => row.validIdentity && row.validKind)

/-! ## The rows of `events@0` (events-time-causation plan 2.7, spec 2.4 and 2.5; owner ET-5)

Frames: `authored` is a sentence written under the profile, refused with its advice and a rewrite (spec 2.5);
`source`, `source event`, `source date` and `source outside a rule` are a source word met in translation, with its
reading set (spec 2.4); `before` and `link <form>` are the profile-fixed wordings, which Lean checks exactly (spec 4
items 3 and 5) and the author lint does not judge (2.7). "always" has no row in a rule: there it is soft norms' force
word (DRI 2026-11-03, item 3). "during" and "whenever" have one candidate, so no reading set. -/

def eventsUntilAdvice : String :=
  "Write the rule for each day with the guard 'if it is not the case that <event> happens no later than that " ++
  "day'; the text then says nothing about later days. If it means the rule stops, add a second rule with the " ++
  "opposite wording ('must not' for 'may', 'need not' for 'must', 'may' for 'must not') for the days on which " ++
  "<event> happens no later than that day. For a date, say whether the date itself is included: 'before <date>' " ++
  "or 'no later than <date>'."
def eventsStateAdvice : String :=
  "Write the rule for each day with the guard '<state> is in progress on that day'."
def eventsDaysAdvice : String :=
  "Write the days explicitly: 'on each day, if ...', 'there is a day such that ...'."
def eventsLinkAdvice : String :=
  "Write '<cause> contributed to <effect>' or '<cause> was necessary for <effect>'; in a decision model write " ++
  "'leads to'."

def eventsRow (word frame : String) (kind : SourceWordKind) : SourceWordRow :=
  ⟨word, frame, "events@0", "ET-5", kind⟩
def eventsRefusal (word advice rewrite : String) : SourceWordRow :=
  eventsRow word "authored" (.refuse ("events-" ++ word.replace " " "-") advice rewrite)
/-- A reading set whose candidates share one distinguishing situation. -/
def eventsReadings (word frame situation : String) (candidates : List String) : SourceWordRow :=
  eventsRow word frame (.readings (candidates.map (⟨·, situation⟩)))

/-- The twelve source words refused in authored text (spec 2.5, T9). -/
def eventsRefusals : List SourceWordRow := [
  eventsRefusal "until" eventsUntilAdvice "if it is not the case that that closure happens no later than that day",
  eventsRefusal "by" "Write 'before <day>' or 'no later than <day>'." "no later than 31 December 2026",
  eventsRefusal "within" ("Durations over events are not available here; name the dates, or use the quantity " ++
    "wordings in a quantity document.") "on or after 5 January 2027 and no later than 15 January 2027",
  eventsRefusal "during" eventsStateAdvice "on each day, if that stay is in progress on that day",
  eventsRefusal "while" eventsStateAdvice "on each day, if that stay is in progress on that day",
  eventsRefusal "since" eventsDaysAdvice "on each day, if that act happens before that day",
  eventsRefusal "always" eventsDaysAdvice "on each day",
  eventsRefusal "eventually" eventsDaysAdvice "there is a day such that that act happens on that day",
  eventsRefusal "whenever" eventsDaysAdvice "on each day, if that act happens on that day",
  eventsRefusal "resulted in" eventsLinkAdvice "that act contributed to that harm",
  eventsRefusal "led to" eventsLinkAdvice "that act contributed to that harm",
  eventsRefusal "caused" eventsLinkAdvice "that act was necessary for that harm"]

/-- "m X until E": U1 states its silence (ET-E1's rewording, docs/events-time-causation/et-e1/RESULTS.md), U2 adds
the opposite modality from E's day (R2). -/
def untilEventReadings : SourceWordRow := eventsReadings "until" "source event"
  ("E's day, the day before it and a later day: with the act unspecified, from E's day U1 does not say and U2 " ++
   "gives the opposite modality.")
  ["<agent> <m> <act> on each day, if it is not the case that <event> happens no later than that day. This " ++
     "document does not say whether <agent> <m> <act> on a day on which <event> happens no later than that day.",
   "<agent> <m> <act> on each day, if it is not the case that <event> happens no later than that day. <agent> " ++
     "<opposite of m> <act> on each day on which <event> happens no later than that day."]

/-- "within n days of D" (SR-B4): both end dates are named dates, <start> n days before D and <end> n days after. -/
def withinDateReadings : SourceWordRow := eventsReadings "within" "source date"
  ("An act on <end> (W1 and W3 against W2) and an act before <date> and on or after <start> (W3 against W1 and " ++
   "W2).")
  ["<event> happens on or after <date> and no later than <end>.",
   "<event> happens on or after <date> and before <end>.",
   "<event> happens on or after <start> and no later than <end>."]

def eventsReadingSets : List SourceWordRow := [
  untilEventReadings,
  eventsReadings "until" "source date"
    "<date> itself (exclusive against inclusive) and the day after <date> (silent against ending)."
    ["<agent> <m> <act> on each day before <date>. This document does not say whether <agent> <m> <act> on " ++
       "<date> or on a day after <date>.",
     "<agent> <m> <act> on each day before <date>. <agent> <opposite of m> <act> on <date> and on each day " ++
       "after <date>.",
     "<agent> <m> <act> on each day no later than <date>. This document does not say whether <agent> <m> <act> " ++
       "on a day after <date>.",
     "<agent> <m> <act> on each day no later than <date>. <agent> <opposite of m> <act> on each day after <date>."],
  eventsReadings "by" "source" "The act on <date> itself."
    ["<event> happens before <date>.", "<event> happens no later than <date>."],
  withinDateReadings,
  eventsRow "within" "source event" (.refuse "duration"
    "Within n days of an event has no candidate: the span stays UNFORMALISED with reason duration (ET-T1)."
    "on or after 5 January 2027 and no later than 15 January 2027"),
  eventsReadings "while" "source" "A day on which <state> is not in progress."
    ["On each day on which <state> is in progress, <clause>.", "<clause> and <clause>."],
  eventsReadings "since" "source event" "The day <event> happens."
    ["On each day after the day <event> happens, <clause>.",
     "On each day on or after the day <event> happens, <clause>."],
  eventsReadings "always" "source outside a rule"
    ("A day before the date of this document; while the date of this document is open (no ISO anchor), only " ++
     "the first.")
    ["On each day, <clause>.", "On each day on or after the date of this document, <clause>."],
  eventsReadings "eventually" "source"
    ("Only a day before the date of this document; while the date of this document is open (no ISO anchor), " ++
     "only the first.")
    ["There is a day such that <clause> on that day.",
     "There is a day such that that day is after the date of this document and <clause> on that day."]] ++
  -- "lead to" and "cause" are source forms only (etc-rev's C point); "causes" and "leads to" stay outside.
  (["resulted in", "led to", "caused", "lead to", "cause"].map fun word => eventsReadings word "source"
    "A situation in which the contributed link holds and the necessary link does not."
    [VE.Events.linkWording .contributed, VE.Events.linkWording .necessary])

/-- The profile-fixed wordings (2.7), Lean's own (`VE.Events.beforeWording`, `linkWording`). -/
def eventsFixed : List SourceWordRow := [
  eventsRow "before" "before" (.fixed VE.Events.beforeWording),
  eventsRow "contributed to" "link contributed" (.fixed (VE.Events.linkWording .contributed)),
  eventsRow "was necessary for" "link necessary" (.fixed (VE.Events.linkWording .necessary))]

/-- The catalogue's rows, in owner order. -/
def sourceWords : List SourceWordRow := eventsRefusals ++ eventsReadingSets ++ eventsFixed

#guard sourceWordsValid sourceWords

def SourceWordKind.toJson : SourceWordKind → Json
  | .readings candidates => Json.mkObj [
      ("type", "readings"),
      ("candidates", Json.arr ((candidates.map fun c =>
        Json.mkObj [("wording", .str c.wording), ("situation", .str c.situation)]).toArray))]
  | .refuse code advice rewrite => Json.mkObj [
      ("type", "refuse"), ("code", .str code), ("advice", .str advice),
      ("rewrite", .str rewrite)]
  | .fixed wording => Json.mkObj [("type", "fixed"), ("wording", .str wording)]

def SourceWordRow.toJson (row : SourceWordRow) : Json := Json.mkObj [
  ("word", .str row.word), ("frame", .str row.frame),
  ("profile", .str row.profile), ("owner", .str row.owner),
  ("kind", row.kind.toJson)]

/-- This is the sole source of the generated Python view. -/
def sourceWordsJson (rows : List SourceWordRow := sourceWords) : Json := Json.mkObj [
  ("format", "ve.source-words@1"),
  ("rows", Json.arr ((rows.map SourceWordRow.toJson).toArray))]

end VE.EnglishGrammar
