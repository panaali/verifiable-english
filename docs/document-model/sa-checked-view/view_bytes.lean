import VE.Service.DocumentView

/-! sa-checked-view's fixture run (tests/test_sa_checked_view.py): one JSON line per request in the file
`VE_VIEW_CASES` names: `checkDocSets`'s answer, the view's first component, and what the view says of the answer. -/

open Lean VE.Service.Document

def side (r : Except String Json) : Json := match r with
  | .ok a => Json.mkObj [("ok", .str a.compress)]
  | .error e => Json.mkObj [("error", .str e)]

def kindsJson (xs : List (String × List VE.Route.Admission.Kind)) : Json :=
  toJson (xs.map fun (u, ks) => (u, ks.map reprStr))

def caseLine (j : Json) : Json :=
  let view := checkDocSetsView j
  let said := match view, checkedRun j with
    | .ok (a, V), .ok (_, _, c) =>
      [("rows_render", toJson (a.getObjValD "units" == toJson (V.rows.map unitJson))),
       ("source_is", toJson (a.getObjValD "source" == .str V.source)),
       ("fold_changed", toJson (c.rows.map unitJson != V.rows.map unitJson)),
       ("candidates", kindsJson V.candidates), ("readings", toJson V.readings),
       ("pack_sources", toJson V.packSources),
       ("active_kinds", match activeKinds j with
         | .ok ks => kindsJson ks
         | .error e => .str e)]
    | _, _ => []
  Json.mkObj ([("answer", side (checkDocSets j)), ("view", side (view.map (·.1)))] ++ said)

#eval show IO Unit from do
  let some path ← IO.getEnv "VE_VIEW_CASES" | throw (IO.userError "VE_VIEW_CASES is not set")
  for line in (← IO.FS.readFile path).splitOn "\n" do
    unless line.isEmpty do
      match Json.parse line with
      | .ok j => IO.println (caseLine j).compress
      | .error e => throw (IO.userError e)
