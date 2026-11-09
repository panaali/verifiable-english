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
#guard diag (env (set "states" (.num 1))) == "InvalidInput: events.states"
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
-- Each entry's field check refuses an unknown field (review F1).
#guard diag (env (set "states" (parse ("[{\"sort\": \"stay\", \"begins\": \"stay_begins\", \"ends\": \"stay_ends\", " ++
  "\"x\": 1}]")))) == "InvalidInput: events.states.x"
#guard diag (env (set "links" (parse ("[{\"predicate\": \"contributed_to\", \"form\": \"contributed\", " ++
  "\"decided_by\": \"x\", \"x\": 1}]")))) == "InvalidInput: events.links.x"
-- Two faults, the first one named: an unknown field, then a missing one, then each field in the block's order.
#guard diag (env (set "extra" (.num 1) (drop "links" block))) == "InvalidInput: events.extra"
#guard diag (env (set "day" (.num 3) (drop "links" block))) == "InvalidInput: events.links"
-- Every key and every required field is looked at (D[R] run): an unknown key read first or last, two fields missing.
#guard diag (env (set "a_extra" (.num 1))) == "InvalidInput: events.a_extra"
#guard diag (env (set "zz" (.num 1))) == "InvalidInput: events.zz"
#guard diag (env (drop "day" (drop "links" block))) == "InvalidInput: events.day"
#guard [("day", "before"), ("before", "events"), ("events", "states"), ("states", "dates"), ("dates", "anchor"),
  ("anchor", "links")].all fun (a, b) => diag (env (set a (.num 3) (set b (.num 3)))) == s!"InvalidInput: events.{a}"
#guard diag (env (set "links" (parse "[{\"predicate\": 3, \"form\": \"contributed\", \"decided_by\": \"x\", \"x\": 1}]"))) ==
  "InvalidInput: events.links.x"
#guard diag (env (set "links" (parse "[{\"predicate\": 3, \"form\": \"caused\", \"decided_by\": \"x\"}]"))) ==
  "InvalidInput: events.links.predicate"
#guard diag (env (set "links" (parse "[{\"predicate\": \"contributed_to\", \"form\": \"caused\", \"decided_by\": 3}]"))) ==
  "InvalidInput: events.links.form"

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
#guard diag (env block (setPred "committed_on" (regulated (pred "[\"act\", \"day\"]" "{0} happens on {1}")))) ==
  "EventsRegulated: committed_on"

-- The day sort is found wherever it is declared, first or last (D[R] run): the fault is then item 4's.
#guard diag (env block (vocab.setObjVal! "sorts"
  (parse "{\"day\": {\"description\": \"d\"}, \"lease\": {\"description\": \"d\"}, \"stay\": {\"description\": \"d\"}}"))) == "EventsSort: act"
#guard diag (env block (vocab.setObjVal! "sorts" (parse "{\"act\": {\"description\": \"d\"}, \"day\": {\"description\": \"d\"}}"))) == "EventsSort: stay"

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
-- A role with no wording, or a wording that is not a text, has no right wording (trust mutant any-all, D[R] run).
#guard diag (env block (setPred "committed_on" (parse "{\"arguments\": [\"act\", \"day\"], \"verbalisation\": 3}"))) ==
  "EventsVerbalisation: committed_on"
#guard diag (env block (setPred "committed_on" (parse "{\"arguments\": [\"act\", \"day\"]}"))) ==
  "EventsVerbalisation: committed_on"
#guard diag (env (set "states" (parse "[{\"sort\": \"stay\", \"begins\": \"stay_begins\", \"ends\": \"stay_begins\"}]"))) ==
  "DuplicateDeclaration: role stay_begins"
-- The state sorts and roles as the event ones (review F1): declared and not the day, each role's signature and wording.
def state (sort begins ends : String) : String :=
  s!"\{\"sort\": \"{sort}\", \"begins\": \"{begins}\", \"ends\": \"{ends}\"}"
def states (ss : List String) (b : Json := block) : Json := set "states" (parse ("[" ++ ", ".intercalate ss ++ "]")) b
#guard diag (env (states [state "tenancy" "stay_begins" "stay_ends"])) == "EventsSort: tenancy"
#guard diag (env (states [state "day" "stay_begins" "stay_ends"])) == "EventsSort: day"
#guard diag (env (states [state "stay" "stay_begins" "stay_ends", state "stay" "lease_begins" "lease_ends"])) ==
  "DuplicateDeclaration: state sort stay"
#guard diag (env block (setPred "stay_begins" (pred "[\"act\", \"day\"]" "{0} begins on {1}"))) == "EventsSort: stay_begins"
#guard diag (env block (setPred "stay_ends" (pred "[\"stay\", \"act\"]" "{0} ends on {1}"))) == "EventsSort: stay_ends"
#guard diag (env block (setPred "stay_ends" (pred "[\"stay\", \"day\"]" "{0} ends at {1}"))) ==
  "EventsVerbalisation: stay_ends"
-- Every event and every state is checked, the fault first or last (D[R] run); a state sort an earlier event sort repeats.
#guard diag (env (set "events" (parse "[{\"sort\": \"act\", \"on\": \"committed_on\"}, {\"sort\": \"lease\", \"on\": \"happens_at\"}]"))) ==
  "EventsSort: happens_at"
#guard diag (env (set "events" (parse "[{\"sort\": \"lease\", \"on\": \"happens_at\"}, {\"sort\": \"act\", \"on\": \"committed_on\"}]"))) ==
  "EventsSort: happens_at"
#guard diag (env (states [state "stay" "stay_begins" "stay_ends", state "lease" "lease_begins" "happens_at"])) ==
  "EventsSort: happens_at"
#guard diag (env (states [state "lease" "lease_begins" "happens_at", state "stay" "stay_begins" "stay_ends"])) ==
  "EventsSort: happens_at"
#guard diag (env (states [state "lease" "lease_begins" "lease_ends"] (set "events"
  (parse "[{\"sort\": \"act\", \"on\": \"committed_on\"}, {\"sort\": \"lease\", \"on\": \"lease_begins\"}]")))) ==
  "DuplicateDeclaration: state sort lease"
-- Two faults, in item 4's order: sorts, distinct event sorts, distinct state sorts, signatures, wordings, distinct roles.
def setPreds (ps : List (String × Json)) : Json :=
  vocab.setObjVal! "predicates" (ps.foldl (fun j (p, e) => j.setObjVal! p e) (vocab.getObjValD "predicates"))
def badWording : Json := setPred "committed_on" (pred "[\"act\", \"day\"]" "{0} on {1}")
#guard diag (env (set "events" (parse "[{\"sort\": \"deed\", \"on\": \"committed_on\"}, {\"sort\": \"deed\", \"on\": \"committed_on\"}]"))) ==
  "EventsSort: deed"
#guard diag (env (states [state "act" "stay_begins" "stay_ends"] (set "events"
  (parse "[{\"sort\": \"act\", \"on\": \"committed_on\"}, {\"sort\": \"act\", \"on\": \"happens_at\"}]")))) ==
  "DuplicateDeclaration: event sort act"
#guard diag (env block (setPreds [("committed_on", pred "[\"act\", \"day\"]" "{0} on {1}"),
  ("stay_ends", pred "[\"stay\", \"act\"]" "{0} ends on {1}")])) == "EventsSort: stay_ends"
#guard diag (env (states [state "stay" "stay_begins" "stay_begins"]) badWording) == "EventsVerbalisation: committed_on"

-- Item 5: each link's signature and its form's wording, then no predicate twice.
#guard diag (env (set "links" (.arr #[link "committed_on" "contributed" "x"]))) == "EventsSort: committed_on"
#guard diag (env (set "links" (.arr #[link "missing" "contributed" "x"]))) == "EventsSort: missing"
#guard diag (env (set "links" (.arr #[link "contributed_to" "necessary" "x"]))) ==
  "EventsVerbalisation: contributed_to"
#guard diag (env (set "links" (.arr #[link "needed_for" "necessary" "x"]))) ==
  "ok [2026-10-12, 2026-10-13, 2026-10-14] 12 [x]"
#guard diag (env (set "links" (.arr #[link "contributed_to" "contributed" "x", link "contributed_to" "contributed" "y"]))) ==
  "DuplicateDeclaration: link contributed_to"
-- The cause sort is a role sort too (review F1); a wrong wording comes before a repeated predicate.
#guard diag (env (set "links" (.arr #[link "lease_led" "contributed" "x"]))
  (setPred "lease_led" (pred "[\"lease\", \"stay\"]" "{0} contributed to {1}"))) == "EventsSort: lease_led"
#guard diag (env (set "links" (.arr #[link "contributed_to" "necessary" "x", link "contributed_to" "necessary" "y"]))) ==
  "EventsVerbalisation: contributed_to"
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
#guard diag (env (dates ["2026-10-12", "2026-10-14", "2026-10-12"])) == "DuplicateDeclaration: date 2026-10-12"
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
-- Two faults, in item 6's order (review F1): the dates, then the anchor, parse; then unique; the limit, then the names.
#guard diag (env (dates ["2026-02-30"] (some "2025-13-01"))) == "InvalidDate(2026-02-30)"
#guard diag (env (dates ["2026-10-12", "2026-10-12"] (some "2025-13-01"))) == "InvalidDate(2025-13-01)"
#guard diag (env (dates (days 65)) (withConst "date__x")) == "ResourceLimit: events dates"
-- Item 5 before item 6.
#guard diag (env (set "links" (.arr #[link "missing" "contributed" "x"]) (dates ["2026-02-30"]))) == "EventsSort: missing"
#guard ownedByEvents (dateName ⟨2026, 10, 12⟩) && !ownedByEvents "date_x" && !ownedByEvents "dates__x"

-- Item 7: each generated premise within the node limit, at the limit and one below it.
def oneDay : List (String × VE.Formula) := [("events:irreflexive", .all "day" (.not (.binary "before" (.var 0) (.var 0))))]
#guard (oneDay.map (VE.Bridge.formulaNodes ·.2)) == [5]
#guard (checkPremiseSize 5 oneDay).toOption.isSome
#guard (match checkPremiseSize 4 oneDay with | .error e => e | .ok _ => "ok") ==
  "ResourceLimit: events premise events:irreflexive"
-- Every premise is checked, not only the first (review F1).
#guard (match checkPremiseSize 4 (("events:top", .top) :: oneDay) with | .error e => e | .ok _ => "ok") ==
  "ResourceLimit: events premise events:irreflexive"
#guard (match checkPremiseSize 4 (oneDay ++ [("events:top", .top)]) with | .error e => e | .ok _ => "ok") ==
  "ResourceLimit: events premise events:irreflexive"
-- No block reaches the limit through `decodeEvents`: a premise of every kind (here) has a fixed shape of at most 20 nodes.
#guard ((decodeEvents (env (set "links" (.arr #[link "contributed_to" "contributed" "x", link "needed_for" "necessary" "y"]))))
  |>.toOption.join).any fun d => (eventsLabelled d.V).all (VE.Bridge.formulaNodes ·.2 ≤ 20)

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
def softP : Pack := ⟨"soft", .constraint, [], [], [("soft:x", .top)], [], []⟩
#guard decoded.any fun d => (eventsPack d).id == "events" && (eventsPack d).labelled == eventsLabelled d.V
#guard decoded.any fun d => match assembleIn reservedPrefixes d.E 0 [eventsPack d, softP] with
  | .ok qs => X qs == .top :: eventsX d.V &&
      (qs.flatMap (·.labelled.map (·.1))).take 3 == ["soft:x", "events:irreflexive", "events:transitive"]
  | .error _ => false

/-! ## et-4b: the route's hook, the row (item 1), `LinkNotOpen` and the charged limits -/

def listed : List String := ["events@0", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]
def profiled (b : Json) (ps : List String := listed) (v : Json := vocab) : Json :=
  (env b v).setObjVal! "profiles" (toJson ps)
def sortedWith (p : String) : List String := (listed ++ [p]).toArray.qsort (· < ·) |>.toList
def terms : Json := parse "[{\"name\":\"contributed_to\",\"decided_by\":\"the drafters\"}]"
def fault (e : Json) (t : Json := terms) : String := match eventsHook e t with
  | .ok _ => "ok"
  | .error m => m
def badDate : Json := block.setObjVal! "dates" (toJson ["nonsense"])
def linkJ (p : String) (form : String := "contributed") (by_ : String := "the drafters") : Json :=
  Json.mkObj [("predicate", .str p), ("form", .str form), ("decided_by", .str by_)]
def linked (ls : List Json) : Json := block.setObjVal! "links" (toJson ls)

-- The accepting side, and the row's requirements in order, each before the block's own fault.
#guard fault (profiled block) == "ok"
#guard fault (profiled badDate ["events@0", "norm-defaults@0", "norms@0"]) == "UnsupportedProfile: events@0 requires relational-fol@0"
#guard fault (profiled badDate ["events@0", "norm-defaults@0", "relational-fol@0"]) == "UnsupportedProfile: events@0 requires norms@0"
#guard fault (profiled badDate ["events@0", "norms@0", "relational-fol@0"]) == "UnsupportedProfile: events@0 requires norm-defaults@0"
#guard fault (profiled badDate) == "InvalidDate(nonsense)"
-- Every refused profile by name, the first of a sorted list ahead of any other row's text; beside the row, the block's.
#guard ["alternatives@0", "closure@0", "data@0", "nary@0", "order@0", "reports@0", "risk@0", "speech-acts@0", "time@0"].all
  fun p => fault (profiled badDate (sortedWith p)) == s!"UnsupportedProfile: events@0 with {p}"
#guard fault (profiled badDate ["alternatives@0", "events@0", "norm-defaults@0", "norms@0", "relational-fol@0", "risk@0"]) ==
  "UnsupportedProfile: events@0 with alternatives@0"
#guard ["documents@1", "rights@0", "readings@1", "definitions@0"].all fun p =>
  VE.Compose.eventsFault (sortedWith p) == none && fault (profiled badDate (sortedWith p)) == "InvalidDate(nonsense)"
#guard VE.Compose.eventsFault listed == none
-- A list without the profile has no hook, whatever its block: its decoders are today's.
#guard (match eventsHook (profiled badDate (listed.filter (· != "events@0"))) terms with
  | .ok none => true | _ => false)
#guard (match eventsHook (profiled badDate []) terms with | .ok none => true | _ => false)
-- `baseRows`' modes hook no pack: the profile stays unknown to them.
#guard (match VE.Compose.gateOf VE.Compose.baseRows listed with
  | .error e => e | .ok _ => "ok") == "UnsupportedProfile: Unsupported profile events@0"

-- `LinkNotOpen`: no term, another decider, another name, a malformed row or list; every link is read.
#guard fault (profiled block) (parse "[]") == "LinkNotOpen: contributed_to"
#guard fault (profiled block) (parse "[{\"name\":\"contributed_to\",\"decided_by\":\"the court\"}]") == "LinkNotOpen: contributed_to"
#guard fault (profiled block) (parse "[{\"name\":\"needed_for\",\"decided_by\":\"the drafters\"}]") == "LinkNotOpen: contributed_to"
#guard fault (profiled block) (parse "[{\"name\":\"contributed_to\"}]") == "LinkNotOpen: contributed_to"
#guard fault (profiled block) (parse "[{\"decided_by\":\"the drafters\"}]") == "LinkNotOpen: contributed_to"
#guard fault (profiled block) (.num 7) == "LinkNotOpen: contributed_to"
def twoLinks : Json := linked [linkJ "contributed_to", linkJ "needed_for" "necessary"]
def bothTerms : Json :=
  parse "[{\"name\":\"contributed_to\",\"decided_by\":\"the drafters\"},{\"name\":\"needed_for\",\"decided_by\":\"the drafters\"}]"
#guard fault (profiled twoLinks) == "LinkNotOpen: needed_for"
#guard fault (profiled twoLinks) bothTerms == "ok"
#guard fault (profiled (linked [linkJ "needed_for" "necessary", linkJ "contributed_to"])) == "LinkNotOpen: needed_for"
-- After the link's own faults, and before the dates; `unstated` is the decider as written.
#guard fault (profiled (linked [linkJ "needed_for", linkJ "contributed_to"])) (parse "[]") == "EventsVerbalisation: needed_for"
#guard fault (profiled (linked [linkJ "contributed_to", linkJ "contributed_to"])) (parse "[]") ==
  "DuplicateDeclaration: link contributed_to"
#guard fault (profiled badDate) (parse "[]") == "LinkNotOpen: contributed_to"
#guard fault (profiled (linked [linkJ "contributed_to" "contributed" "unstated"])) == "LinkNotOpen: contributed_to"
#guard fault (profiled (linked [linkJ "contributed_to" "contributed" "unstated"]))
  (parse "[{\"name\":\"contributed_to\",\"decided_by\":\"unstated\"}]") == "ok"
-- `decodeEvents` reads no open term; a route's check only refuses (`decodeEventsWith_ok`).
#guard (decodeEvents (profiled block)).toOption.isSome && (decodeEventsWith (checkOpen []) (profiled block)).toOption.isNone

-- A growing chain of days: the premises grow by two a day; past 64 dates the fault is one, at any size.
def isos (n : Nat) : List String := (List.range n).filterMap fun i => (VE.Time.civilOf (20000 + i)).map (·.iso)
def chain (n : Nat) : Json := profiled (block.setObjVal! "dates" (toJson (isos n)))
def labels (e : Json) : List String := match eventsHook e terms with
  | .ok (some ⟨_, some d⟩) => d.labelled.map (·.1)
  | _ => []
#guard [1, 10, 62].all fun n => (labels (chain n)).length == 2 * n + 7
#guard fault (chain 63) == "ok"
#guard fault (chain 64) == "ResourceLimit: events dates"
#guard fault (chain 2000) == "ResourceLimit: events dates"
-- The largest list still names its repeat (spec 4's order), and ends: the check is one pass.
#guard fault (profiled (block.setObjVal! "dates" (toJson (isos 20000 ++ ["2024-10-05"])))) == "DuplicateDeclaration: date 2024-10-05"
#guard repeatOf [] ["a", "b", "a", "b"] == some "a" && repeatOf ["b"] ["a", "b"] == some "b" &&
  repeatOf ["c"] ["a", "b"] == none && repeatOf [] [] == none
-- Roles and links are charged before they are read against each other; just inside, the next fault is theirs.
def manyLinks (n : Nat) : List Json := (List.range n).map fun i => linkJ s!"l{i}"
#guard fault (profiled (linked (manyLinks 254))) == "ResourceLimit: events premises"
#guard fault (profiled (linked (manyLinks 253))) == "EventsSort: l0"
#guard fault (profiled (linked (manyLinks 20000))) == "ResourceLimit: events premises"
-- The whole pack against `maxNodes`: 60 necessary and 60 contributed links on one pair.
def linkPred (p w : String) : String × Json := (p, pred "[\"act\", \"stay\"]" w)
def weaker (n : Nat) : Json :=
  let cs := (List.range n).map fun i => s!"c{i}"
  let ns := (List.range n).map fun i => s!"n{i}"
  let preds := (fields (vocab.getObjValD "predicates")).toOption.getD []
  let v := vocab.setObjVal! "predicates" (Json.mkObj (preds ++ cs.map (linkPred · "{0} contributed to {1}") ++
    ns.map (linkPred · "{0} was necessary for {1}")))
  profiled (linked (cs.map linkJ ++ ns.map (linkJ · "necessary"))) listed v
def weakerTerms (n : Nat) : Json := toJson ((List.range n).flatMap fun i =>
  [s!"c{i}", s!"n{i}"].map fun p => Json.mkObj [("name", .str p), ("decided_by", .str "the drafters")])
#guard fault (weaker 60) (weakerTerms 60) == "ResourceLimit: events premises"
#guard fault (weaker 30) (weakerTerms 30) == "ok"
-- Each premise at its limit and one over, then the whole list; the last premise is read too.
def pack : List (String × VE.Formula) := match eventsHook (profiled block) terms with
  | .ok (some ⟨_, some d⟩) => d.labelled
  | _ => []
def sized (limit : Nat) (ls : List (String × VE.Formula)) : String := match checkPremiseSize limit ls with
  | .ok _ => "ok"
  | .error e => e
def nodes (i : Nat) : Nat := VE.Bridge.formulaNodes (pack.getD i ("", .top)).2
#guard nodes 0 < nodes 1
#guard sized (nodes 1) (pack.take 2 |>.drop 1) == "ok"
#guard sized (nodes 1 - 1) (pack.take 2) == "ResourceLimit: events premise events:transitive"
#guard sized (nodes 0 + nodes 1) (pack.take 2) == "ok"
#guard sized (nodes 0 + nodes 1 - 1) (pack.take 2) == "ResourceLimit: events premises"

-- The view: no block, no profile, one constant per named date in the day sort, the anchor's with its fixed wording.
def view (e : Json) : Json := match eventsHook e terms with
  | .ok (some h) => h.view
  | _ => .null
def viewConstants : Json := ((view (profiled block)).getObjValD "vocabulary").getObjValD "constants"
#guard !((view (profiled block)).getObjVal? "events").toBool
#guard VE.Compose.listedProfiles (view (profiled block)) == listed.filter (· != "events@0")
#guard viewConstants.getObjValD "date__2026_10_12" == parse "{\"sort\":\"day\",\"description\":\"2026-10-12\"}"
#guard viewConstants.getObjValD "date__2026_10_13" == parse "{\"sort\":\"day\",\"description\":\"the date of this document\"}"
#guard viewConstants.getObjValD "date__2026_10_14" == parse "{\"sort\":\"day\",\"description\":\"2026-10-14\"}"
#guard viewConstants.getObjValD "today" != .null && (fields viewConstants).toOption.map (·.length) == some 4
-- The profile with no block: the view only drops the profile.
#guard view (drop "events" (profiled block)) ==
  (drop "events" (profiled block)).setObjVal! "profiles" (toJson (listed.filter (· != "events@0")))

end VE.Events.WireExamples
