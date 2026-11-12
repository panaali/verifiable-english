import VE.Events.Decl
import Lean

/-! The date of this document (docs/spec/events-time-causation.md 1.3, ET-R1; et-5b): the anchor's fixed wording, the
open anchor term `date_of_this_document`, its check on the document route (2.9 item 8, the first half; spec 4) and the
legend lines Lean owns (2.3). The second half of item 8, `AnchorOpen`, reads the source-word catalogue and is the
document route's (`Service.Document.eventsAnchorChecks`). -/

namespace VE.Events
open Lean

/-- The fixed verbalisation of the anchor's constant, ISO or open (1.3). -/
def anchorWording : String := "the date of this document"

/-- The open anchor term's constant (1.3): no named date, no `date__` name, not counted in `maxDates`. -/
def anchorConstant : String := "date_of_this_document"

/-- Item 8's first half: `none` when the vocabulary declares no `date_of_this_document`; `some ()` when it declares it
with the day sort and the fixed verbalisation and the block has no `anchor` (the term is open); otherwise
`AnchorNotOpen: date_of_this_document`. -/
def openAnchor (environment : Json) (V : Option EventsEnv) : Except String (Option Unit) :=
  match (((environment.getObjValD "vocabulary").getObjValD "constants").getObjVal? anchorConstant).toOption with
  | none => .ok none
  | some c =>
    if V.any fun V => c.getObjValD "sort" == .str V.day &&
        c.getObjValD "description" == .str anchorWording && V.anchor.isNone then .ok (some ())
    else .error s!"AnchorNotOpen: {anchorConstant}"

/-- The legend of 2.3 in its order, without the ISO anchor's line, whose long date form is the date-literal class's
(1.3: events adds no month table): the day line, the state line, the link line when links are declared, and the open
anchor's line when the term is open. -/
def legend (V : EventsEnv) (isOpen : Bool) : List String :=
  ["Times are counted in whole days: two things on the same day happen on the same day, and neither is before the " ++
     "other.",
   "A state is in progress from the day it begins through the day it ends."] ++
  (if V.links.isEmpty then [] else
    ["A cause does not start after the day of an event it contributed to, and does not start after the last day of " ++
       "a state it contributed to, when that state ends. Whatever was necessary for something contributed to it."]) ++
  (if isOpen then [s!"This document states no date of its own, so \"{anchorWording}\" is left open."] else [])

end VE.Events
