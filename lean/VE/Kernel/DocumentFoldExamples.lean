import VE.Kernel.DocumentFold

/-! Examples of the document mode's fold (`VE.Kernel.DocumentFold`, kb-2a-b): each branch of a unit's status, each of
the three OPEN conditions, the meaning classes without a core statement, and the answer's carried rows. -/
namespace VE.Kernel.DocumentFoldExamples
open Lean VE.Kernel VE.Kernel.DocumentFold

def ok : Row := ⟨.str "c0", .ok (.str "a0")⟩
def refused : Row := ⟨.str "c1", .error "e1"⟩

def unit (meaning : String) (reads : List (List String)) (set : Option Bool := none) (rightsOpen := false) : UnitRow :=
  ⟨"u", meaning, reads.map (⟨·⟩), set, rightsOpen⟩

-- A row is `ok` exactly when the kernel accepted its case.
#guard DocumentFold.Row.ok ok && !DocumentFold.Row.ok refused
-- CHECKED: a core statement, not open, every row ok (an empty row list included).
#guard status (unit "specified" [[]]) [ok, ok] == .checked
#guard status (unit "specified" [[], []]) [] == .checked
-- One refused row: no unit is CHECKED.
#guard status (unit "specified" [[]]) [ok, refused] == .opened
#guard status (unit "specified" [[]]) [refused] == .opened
-- The three OPEN conditions, each alone.
#guard status (unit "specified" [[], ["t"]]) [ok] == .opened
#guard status (unit "specified" [[]] (some false)) [ok] == .opened
#guard status (unit "specified" [[]] none true) [ok] == .opened
#guard opens (unit "specified" [["t"]]) && opens (unit "specified" [] (some false)) && opens (unit "specified" [] none true)
#guard !opens (unit "specified" [[], []]) && !opens (unit "specified" [[]] (some true))
-- An authored set with every reading asserted decides the unit, whatever its meaning class.
#guard status (unit "open" [[]] (some true)) [ok] == .checked
-- No core statement: the meaning class decides, as W2 does without content (the shell's table gives a unit that does
-- not assert its content no statement that reads no judgment term: `CoreCheck.tableOf`).
#guard status (unit "specified" []) [ok] == .labelled
#guard status (unit "specified" [] (some true)) [ok] == .labelled
#guard status (unit "open" []) [ok] == .opened
#guard status (unit "unformalised" []) [ok] == .unformalised
#guard status (unit "unformalised" [["t"]]) [ok] == .opened
#guard status (unit "none" []) [ok] == .labelled
#guard baseless "open" == .opened && baseless "unformalised" == .unformalised && baseless "specified" == .labelled
-- Each unit of the table, in order, with its own status.
#guard statuses [{ unit "specified" [[]] with id := "a" }, { unit "unformalised" [] with id := "b" },
    { unit "specified" [["t"]] with id := "c" }] [ok] == [("a", .checked), ("b", .unformalised), ("c", .opened)]
-- The answer: the view over the statuses, and every row verbatim, an answer or a refusal.
def view (st : List (String × Status)) : Json :=
  Json.arr (st.map fun (u, s) => Json.mkObj [("u", .str u), ("checked", .bool (s == .checked))]).toArray
#guard fold view [unit "specified" [[]]] .null [ok, refused] == Json.mkObj [
  ("view", Json.arr #[Json.mkObj [("u", .str "u"), ("checked", .bool false)]]),
  ("rows", Json.arr #[Json.mkObj [("case", .str "c0"), ("answer", .str "a0")],
    Json.mkObj [("case", .str "c1"), ("refused", .str "e1")]])]
#guard fold view [unit "specified" [[]]] .null [ok] == Json.mkObj [
  ("view", Json.arr #[Json.mkObj [("u", .str "u"), ("checked", .bool true)]]),
  ("rows", Json.arr #[Json.mkObj [("case", .str "c0"), ("answer", .str "a0")]])]

end VE.Kernel.DocumentFoldExamples
