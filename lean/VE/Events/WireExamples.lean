import VE.Events.Wire

/-! ET-4's decoder fixtures (docs/spec/events-time-causation.md 4, items 2 to 7): each check refused at its boundary
and accepted just inside it, and the `events` pack placed last by PK-1's one assembler. -/
namespace VE.Events.WireExamples
open Lean
open VE.Events
open VE.Bridge (fields)
open VE.NormDefaults.Packs (assembleIn reservedPrefixes Pack X)

def parse (s : String) : Json := (Json.parse s).toOption.getD .null

def pred (args : String) (wording : String) : Json :=
  parse s!"\{\"arguments\": {args}, \"description\": \"d\", \"verbalisation\": \"{wording}\"}"

def vocab : Json := Json.mkObj [
  ("sorts", parse "{\"day\": {\"description\": \"d\"}, \"act\": {\"description\": \"d\"}, \"stay\": {\"description\": \"d\"}, \"lease\": {\"description\": \"d\"}}"),
  ("predicates", Json.mkObj [
    ("before", pred "[\"day\", \"day\"]" "{0} is before {1}"),
    ("committed_on", pred "[\"act\", \"day\"]" "{0} happens on {1}"),
    ("stay_begins", pred "[\"stay\", \"day\"]" "{0} begins on {1}"),
    ("stay_ends", pred "[\"stay\", \"day\"]" "{0} ends on {1}"),
    ("contributed_to", pred "[\"act\", \"stay\"]" "{0} contributed to {1}"),
    ("needed_for", pred "[\"act\", \"stay\"]" "{0} was necessary for {1}"),
    ("happens_at", pred "[\"act\", \"day\"]" "{0} happens at {1}"),
    ("lease_begins", pred "[\"lease\", \"day\"]" "{0} begins on {1}"),
    ("lease_ends", pred "[\"lease\", \"day\"]" "{0} ends on {1}"),
    ("led_to", pred "[\"stay\", \"act\"]" "{0} contributed to {1}")]),
  ("constants", parse "{\"today\": {\"sort\": \"day\", \"description\": \"d\"}}")]

def block : Json := parse ("{\"day\": \"day\", \"before\": \"before\", " ++
  "\"events\": [{\"sort\": \"act\", \"on\": \"committed_on\"}], " ++
  "\"states\": [{\"sort\": \"stay\", \"begins\": \"stay_begins\", \"ends\": \"stay_ends\"}], " ++
  "\"dates\": [\"2026-10-14\", \"2026-10-12\"], \"anchor\": \"2026-10-13\", " ++
  "\"links\": [{\"predicate\": \"contributed_to\", \"form\": \"contributed\", \"decided_by\": \"the drafters\"}]}")

/-- The object without one field. -/
def drop (k : String) (b : Json) : Json := Json.mkObj (((fields b).toOption.getD []).filter (·.1 != k))

def env (b : Json) (v : Json := vocab) : Json := Json.mkObj [("vocabulary", v), ("events", b)]

/-- The block with one field replaced. -/
def set (k : String) (v : Json) (b : Json := block) : Json := b.setObjVal! k v
/-- The vocabulary with one predicate replaced. -/
def setPred (p : String) (e : Json) : Json :=
  vocab.setObjVal! "predicates" ((vocab.getObjValD "predicates").setObjVal! p e)

def diag (j : Json) : String :=
  match decodeEvents j with
  | .ok none => "none"
  | .ok (some d) => s!"ok {d.V.dates.map (·.iso)} {(eventsLabelled d.V).length} {d.V.links.map (·.decidedBy.getD "unstated")}"
  | .error e => e

-- The base block: dates sorted with the anchor, 3 order + 2 date + 2 adjacent + 1 + 3 + 1 conventions.
#guard diag (env block) == "ok [2026-10-12, 2026-10-13, 2026-10-14] 12 [the drafters]"

-- eventsX_absent: no block, no pack; any other key is not the block.
#guard diag (Json.mkObj [("vocabulary", vocab)]) == "none"
#guard diag (Json.mkObj [("vocabulary", vocab), ("event", block)]) == "none"

-- Item 2: the block's shape.
#guard diag (env (.str "x")) == "InvalidInput: events"
#guard diag (env (set "extra" (.num 1))) == "InvalidInput: events.extra"
#guard diag (env (drop "links" block)) ==
  "InvalidInput: events.links"
#guard diag (env (drop "anchor" block)) ==
  "ok [2026-10-12, 2026-10-14] 9 [the drafters]"
#guard diag (env (set "day" (.num 3))) == "InvalidInput: events.day"
#guard diag (env (set "anchor" (.num 3))) == "InvalidInput: events.anchor"
#guard diag (env (set "dates" (parse "[\"2026-10-12\", 4]"))) == "InvalidInput: events.dates"
#guard diag (env (set "events" (parse "[{\"sort\": \"act\", \"on\": \"committed_on\", \"x\": 1}]"))) ==
  "InvalidInput: events.events.x"
#guard diag (env (set "states" (parse "[{\"sort\": \"stay\", \"begins\": \"stay_begins\"}]"))) ==
  "InvalidInput: events.states.ends"
def link (p form by_ : String) : Json :=
  parse s!"\{\"predicate\": \"{p}\", \"form\": \"{form}\", \"decided_by\": \"{by_}\"}"
#guard diag (env (set "links" (.arr #[link "contributed_to" "caused" "x"]))) == "InvalidInput: events.links.form"
def by64 : String := String.mk (List.replicate 64 'b')
#guard diag (env (set "links" (.arr #[link "contributed_to" "contributed" by64]))) ==
  s!"ok [2026-10-12, 2026-10-13, 2026-10-14] 12 [{by64}]"
#guard diag (env (set "links" (.arr #[link "contributed_to" "contributed" (by64 ++ "b")]))) ==
  "InvalidInput: events.links.decided_by"
#guard diag (env (set "links" (.arr #[link "contributed_to" "contributed" "unstated"]))) ==
  "ok [2026-10-12, 2026-10-13, 2026-10-14] 12 [unstated]"

-- Item 3: the day sort and `before`, then no regulated or defined `before`, role or link.
#guard diag (env (set "day" (.str "date"))) == "EventsSort: date"
#guard diag (env (set "before" (.str "stay_begins"))) == "EventsSort: stay_begins"
#guard diag (env block (setPred "before" (pred "[\"day\", \"day\"]" "{0} precedes {1}"))) ==
  "EventsVerbalisation: before"
def regulated (e : Json) : Json := e.setObjVal! "regulated" (parse "{\"default\": \"deny\"}")
#guard diag (env block (setPred "before" (regulated (pred "[\"day\", \"day\"]" "{0} is before {1}")))) ==
  "EventsRegulated: before"
#guard diag (env block (setPred "stay_ends" ((pred "[\"stay\", \"day\"]" "{0} ends on {1}").setObjVal! "defined"
  (.str "x")))) == "EventsRegulated: stay_ends"
#guard diag (env block (setPred "contributed_to" (regulated (pred "[\"act\", \"stay\"]" "{0} contributed to {1}")))) ==
  "EventsRegulated: contributed_to"

-- Item 4: event and state sorts, their roles' signatures and wordings, distinct roles.
#guard diag (env (set "events" (parse "[{\"sort\": \"deed\", \"on\": \"committed_on\"}]"))) == "EventsSort: deed"
#guard diag (env (set "events" (parse "[{\"sort\": \"day\", \"on\": \"before\"}]"))) == "EventsSort: day"
#guard diag (env (set "events" (parse "[{\"sort\": \"act\", \"on\": \"committed_on\"}, {\"sort\": \"act\", \"on\": \"happens_at\"}]"))) ==
  "DuplicateDeclaration: event sort act"
#guard diag (env (set "states" (parse "[{\"sort\": \"act\", \"begins\": \"stay_begins\", \"ends\": \"stay_ends\"}]"))) ==
  "DuplicateDeclaration: state sort act"
#guard diag (env (set "events" (parse "[{\"sort\": \"act\", \"on\": \"stay_begins\"}]"))) == "EventsSort: stay_begins"
#guard diag (env (set "events" (parse "[{\"sort\": \"act\", \"on\": \"happens_at\"}]"))) ==
  "EventsVerbalisation: happens_at"
#guard diag (env block (setPred "committed_on" (pred "[\"act\", \"day\"]" "{0} on {1}"))) ==
  "EventsVerbalisation: committed_on"
#guard diag (env block (setPred "committed_on" (pred "[\"act\", \"day\"]" "{0} x on {1}"))) ==
  "ok [2026-10-12, 2026-10-13, 2026-10-14] 12 [the drafters]"
#guard diag (env (set "states" (parse "[{\"sort\": \"stay\", \"begins\": \"stay_begins\", \"ends\": \"stay_begins\"}]"))) ==
  "DuplicateDeclaration: role stay_begins"

-- Item 5: each link's signature and its form's wording, then no predicate twice.
#guard diag (env (set "links" (.arr #[link "committed_on" "contributed" "x"]))) == "EventsSort: committed_on"
#guard diag (env (set "links" (.arr #[link "missing" "contributed" "x"]))) == "EventsSort: missing"
#guard diag (env (set "links" (.arr #[link "contributed_to" "necessary" "x"]))) ==
  "EventsVerbalisation: contributed_to"
#guard diag (env (set "links" (.arr #[link "needed_for" "necessary" "x"]))) ==
  "ok [2026-10-12, 2026-10-13, 2026-10-14] 12 [x]"
#guard diag (env (set "links" (.arr #[link "contributed_to" "contributed" "x", link "contributed_to" "contributed" "y"]))) ==
  "DuplicateDeclaration: link contributed_to"
-- A `necessary` and a `contributed` link on one sort pair add `link_weaker`.
#guard diag (env (set "links" (.arr #[link "contributed_to" "contributed" "x", link "needed_for" "necessary" "y"]))) ==
  "ok [2026-10-12, 2026-10-13, 2026-10-14] 14 [x, y]"

-- Item 6: dates through `parseIso` (its texts), unique, at most 64 with the anchor; no `date__` name declared.
def dates (ds : List String) (anchor : Option String := none) : Json :=
  let b := set "dates" (.arr (ds.map Json.str).toArray)
  match anchor with
  | some a => set "anchor" (.str a) b
  | none => drop "anchor" b
#guard diag (env (dates ["2026-02-30"])) == "InvalidDate(2026-02-30)"
#guard diag (env (dates ["1969-12-31"])) == "DateRange(1969-12-31)"
#guard diag (env (dates ["1970-01-01", "9999-12-31"])) == "ok [1970-01-01, 9999-12-31] 9 [the drafters]"
#guard diag (env (dates ["2026-10-12"] (some "2025-13-01"))) == "InvalidDate(2025-13-01)"
#guard diag (env (dates ["2026-10-12", "2026-10-12"])) == "DuplicateDeclaration: date 2026-10-12"
#guard diag (env (dates ["2026-10-12"] (some "2026-10-12"))) == "ok [2026-10-12] 8 [the drafters]"
def days (n : Nat) : List String := (List.range n).map fun k => (VE.Time.epoch.addDays (2 * k)).iso
#guard (diag (env (dates (days 64)))).startsWith "ok "
#guard diag (env (dates (days 65))) == "ResourceLimit: events dates"
#guard (diag (env (dates (days 63) (some "2026-10-12")))).startsWith "ok "
#guard diag (env (dates (days 64) (some "2026-10-12"))) == "ResourceLimit: events dates"
#guard (diag (env (dates (days 64) (some "1970-01-01")))).startsWith "ok "
def withConst (c : String) : Json :=
  vocab.setObjVal! "constants" ((vocab.getObjValD "constants").setObjVal! c (parse "{\"sort\": \"day\", \"description\": \"d\"}"))
#guard diag (env block (withConst "date__2026_10_12")) == "EventsReserved: date__2026_10_12"
#guard diag (env block (withConst "date__x")) == "EventsReserved: date__x"
#guard diag (env block (withConst "date_x")) == "ok [2026-10-12, 2026-10-13, 2026-10-14] 12 [the drafters]"
#guard ownedByEvents (dateName ⟨2026, 10, 12⟩) && !ownedByEvents "date_x" && !ownedByEvents "dates__x"

-- Item 7: each generated premise within the node limit, at the limit and one below it.
def oneDay : List (String × VE.Formula) := [("events:irreflexive", .all "day" (.not (.binary "before" (.var 0) (.var 0))))]
#guard (oneDay.map (VE.Bridge.formulaNodes ·.2)) == [5]
#guard (checkPremiseSize 5 oneDay).toOption.isSome
#guard (match checkPremiseSize 4 oneDay with | .error e => e | .ok _ => "ok") ==
  "ResourceLimit: events premise events:irreflexive"

-- Trust-mutant survivors (trust-mutants.json): each check over every element, not only the first or the last.
-- A link from the state sort to the event sort; two state sorts; the fault on the first link, then on the second.
#guard diag (env (set "links" (.arr #[link "led_to" "contributed" "x"]))) ==
  "ok [2026-10-12, 2026-10-13, 2026-10-14] 12 [x]"
#guard diag (env (set "states" (parse ("[{\"sort\": \"stay\", \"begins\": \"stay_begins\", \"ends\": \"stay_ends\"}, " ++
  "{\"sort\": \"lease\", \"begins\": \"lease_begins\", \"ends\": \"lease_ends\"}]")))) ==
  "ok [2026-10-12, 2026-10-13, 2026-10-14] 15 [the drafters]"
#guard diag (env (set "links" (.arr #[link "needed_for" "necessary" "x", link "contributed_to" "necessary" "y"]))) ==
  "EventsVerbalisation: contributed_to"
#guard diag (env (set "links" (.arr #[link "contributed_to" "necessary" "y", link "needed_for" "necessary" "x"]))) ==
  "EventsVerbalisation: contributed_to"
def vocabReg : Json := setPred "contributed_to" (regulated (pred "[\"act\", \"stay\"]" "{0} contributed to {1}"))
#guard diag (env (set "links" (.arr #[link "needed_for" "necessary" "x", link "contributed_to" "contributed" "y"])) vocabReg) ==
  "EventsRegulated: contributed_to"
#guard diag (env (set "links" (.arr #[link "contributed_to" "contributed" "y", link "needed_for" "necessary" "x"])) vocabReg) ==
  "EventsRegulated: contributed_to"
-- The anchor equal to a date listed after the first is the same date.
#guard diag (env (dates ["2026-10-14", "2026-10-12"] (some "2026-10-12"))) == "ok [2026-10-12, 2026-10-14] 9 [the drafters]"
-- The vocabulary view, its environment and the reserved names, first and last of each list.
def W2 : VocabView := ⟨["date__s", "day"], [("p", parse "{\"arguments\": [\"day\"]}"), ("q", .null)],
  [("c", parse "{\"sort\": \"day\"}"), ("date__c", parse "{\"sort\": \"s\"}")]⟩
#guard W2.names == ["date__s", "day", "p", "q", "c", "date__c"]
#guard W2.env.sorts == ["date__s", "day"] && W2.env.predicates "p" == some ["day"] && W2.env.predicates "q" == none &&
  W2.env.constants "c" == some "day" && W2.env.constants "date__c" == some "s"
#guard (match checkDates W2 [] none with | .error e => e | .ok _ => "ok") == "EventsReserved: date__s"
#guard (match checkDates { W2 with sorts := ["day"] } [] none with | .error e => e | .ok _ => "ok") ==
  "EventsReserved: date__c"
#guard reservedPrefixes.filter (·.1 == "events") == [("events", "date__")]

-- The regenerated environment declares each named date of the day sort, and nothing else.
def decoded : Option EventsDecoded := (decodeEvents (env block)).toOption.join
#guard decoded.any fun d => d.E.constants "date__2026_10_13" == some "day" && d.E.constants "today" == some "day" &&
  d.E.constants "date__2026_10_15" == none && d.V.anchor.map (·.iso) == some "2026-10-13"

-- The pack: PK-1's one assembler places it last, after soft, whatever the order it is given in (X1).
def softP : Pack := ⟨"soft", .constraint, [], [], [("soft:x", .top)], []⟩
#guard decoded.any fun d => (eventsPack d).id == "events" && (eventsPack d).labelled == eventsLabelled d.V
#guard decoded.any fun d => match assembleIn reservedPrefixes d.E 0 [eventsPack d, softP] with
  | .ok qs => X qs == .top :: eventsX d.V &&
      (qs.flatMap (·.labelled.map (·.1))).take 3 == ["soft:x", "events:irreflexive", "events:transitive"]
  | .error _ => false

end VE.Events.WireExamples
