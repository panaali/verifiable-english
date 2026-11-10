import VE.Service.DocumentView
import VE.Compose.ContractExamples

/-! sa-checked-view's build-time checks on `VE.Service.ScopeExamples`' documents (`full`: plain; `doc`: two items
under a `frame` governor; `governedSet`: a reading set governed per choice), for the trust-mutant sweep (`--test`)
and tests/test_sa_checked_view.py. -/

open Lean VE.Service.Document VE.Service.ScopeExamples VE.Compose.ContractExamples

def agrees (j : Json) : Bool := match checkDocSetsView j, checkDocSets j with
  | .ok (a, _), .ok b => a == b
  | .error e, .error f => e == f
  | _, _ => false

def renders (j : Json) : Bool := match checkDocSetsView j with
  | .ok (a, V) => a.getObjValD "units" == toJson (V.rows.map unitJson) && a.getObjValD "source" == .str V.source
  | .error _ => false

def view? (j : Json) : Option CheckedView := (checkDocSetsView j).toOption.map (·.2)

#guard [full, doc, governedSet, full.setObjVal! "admit" (.str "x"), full.setObjVal! "document" (.num 1)].all agrees
#guard [full, doc, governedSet].all renders
-- Scope's fold: each lead-in is LABELLED before it and takes its items' status after it.
#guard (view? doc).map (·.rows.map (·.status.name)) == some ["CHECKED", "CHECKED", "CHECKED", "UNFORMALISED"]
#guard (view? governedSet).map (·.rows.map (·.status.name)) == some ["OPEN", "OPEN", "CHECKED", "UNFORMALISED"]
#guard (view? governedSet).map (·.readings) == some [("i1", ["a"])]
#guard (view? governedSet).map (·.candidates) == some [("i1", [.norm])]
#guard (activeKinds governedSet).toOption == (view? governedSet).map (·.candidates)
#guard [full, doc].all fun j => (view? j).map (fun V => (V.candidates, V.readings)) == some ([], [])
#guard [full, doc, governedSet].all fun j => (view? j).map (·.packSources) == some []
