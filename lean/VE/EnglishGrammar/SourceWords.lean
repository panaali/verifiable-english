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
`source event` and `source date` are a source word met in translation, with its reading set (spec 2.4); `before`
and `link <form>` are the profile-fixed wordings, which Lean checks exactly (spec 4 items 3 and 5) and the author
lint does not judge (2.7). -/

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

/-- "m X until E" (spec 2.4), each candidate with the role's verb phrase `<vp>` (spec 2.1): U1 states its silence
(ET-E1's rewording, docs/events-time-causation/et-e1/RESULTS.md), U2 adds the opposite modality from E's day as
ET-E1 measured it (`until-U2`, 20/20). -/
def untilEventReadings : SourceWordRow := eventsReadings "until" "source event"
  ("E's day, the day before it and a later day: with the act unspecified, from E's day U1 does not say and U2 " ++
   "gives the opposite modality.")
  ["<agent> <m> <act> on each day, if it is not the case that <event> <vp> no later than that day. This " ++
     "document does not say whether <agent> <m> <act> on a day on which <event> <vp> no later than that day.",
   "<agent> <m> <act> on each day, if it is not the case that <event> <vp> no later than that day. <agent> " ++
     "<opposite of m> <act> on each day, if <event> <vp> no later than that day."]

/-- "within n days of D" (SR-B4; spec 8.1 T11d): two derived wordings joined by ", and", both end dates named, <start>
n days before D and <end> n days after it. -/
def withinDateReadings : SourceWordRow := eventsReadings "within" "source date"
  ("An act on <end> (W1 and W3 against W2) and an act before <date> and on or after <start> (W3 against W1 and " ++
   "W2).")
  ["<event> <vp> on or after <date>, and <event> <vp> no later than <end>.",
   "<event> <vp> on or after <date>, and <event> <vp> before <end>.",
   "<event> <vp> on or after <start>, and <event> <vp> no later than <end>."]

/-- "always" outside a rule (spec 2.4; DRI 2026-11-03 item 3), with an ISO anchor: A1 and A2, `<clause>` the source's
clause without the word. -/
def alwaysReadings : SourceWordRow := eventsReadings "always" "source"
  "A day before the date of this document: A1 covers it and A2 does not."
  ["<clause> on each day.", "<clause> on each day, if that day is on or after the date of this document."]

/-- "eventually" (spec 2.4), with an ISO anchor: E1 and E2. -/
def eventuallyReadings : SourceWordRow := eventsReadings "eventually" "source"
  "Only a day before the date of this document: E1 holds there and E2 does not."
  ["There is a day such that <clause> on that day.",
   "There is a day such that that day is after the date of this document and <clause> on that day."]

/-- The no-anchor row (spec 1.3 and 2.4): with no ISO anchor "always" has A1 only, the rewrite; A2, the refused
candidate, turns on where the undated document falls (`AnchorOpen: A2` while the term is open). -/
def alwaysNoAnchorReadings : SourceWordRow := eventsRow "always" "source no anchor" (.refuse "A2"
  "This document states no date of its own, so a day on or after its date is not known: the reading is A1."
  "<clause> on each day.")

/-- The no-anchor row of "eventually": E1 only; E2 refused (`AnchorOpen: E2` while the term is open). -/
def eventuallyNoAnchorReadings : SourceWordRow := eventsRow "eventually" "source no anchor" (.refuse "E2"
  "This document states no date of its own, so a day after its date is not known: the reading is E1."
  "There is a day such that <clause> on that day.")

/-- The reading sets ET-5 writes, and et-5b's "always" and "eventually" with their no-anchor rows; the rest of spec 2.4
is et-5c's. -/
def eventsReadingSets : List SourceWordRow := [untilEventReadings, withinDateReadings, alwaysReadings,
  eventuallyReadings, alwaysNoAnchorReadings, eventuallyNoAnchorReadings]

/-- "always" inside a rule (DRI 2026-11-03 item 3): soft-norms' force word only, the READINGS unit {strict, default}
(docs/spec/soft-norms.md 2.2, "any force word ... is a READINGS unit"). Events adds no candidate there. -/
def softAlwaysReadings : SourceWordRow := ⟨"always", "rule", "soft-norms@0", "soft-norms 2.2", .readings ([
  "<agent> must <act>.", "<agent> should <act>."].map (⟨·,
  "A situation in which an exception to the rule applies: the default rule gives way there and the strict one does not."⟩))⟩

/-- The profile-fixed wordings (2.7), Lean's own (`VE.Events.beforeWording`, `linkWording`). -/
def eventsFixed : List SourceWordRow := [
  eventsRow "before" "before" (.fixed VE.Events.beforeWording),
  eventsRow "contributed to" "link contributed" (.fixed (VE.Events.linkWording .contributed)),
  eventsRow "was necessary for" "link necessary" (.fixed (VE.Events.linkWording .necessary))]

/-- The catalogue's rows, in owner order. -/
def sourceWords : List SourceWordRow := eventsRefusals ++ eventsReadingSets ++ eventsFixed ++ [softAlwaysReadings]

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
