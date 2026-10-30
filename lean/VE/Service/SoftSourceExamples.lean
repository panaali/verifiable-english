import VE.Service.Document

/-! The soft source of the document mode (`softSourceNorms`, Python's `_soft_contents`) reads a `MIXED` unit's parts
(rd9-docroute F7): wrapping a document's units in one `MIXED` parent leaves its norm objects, and so its decision
predicates, unchanged; a structural fault keeps the units `_parts` yields before it (`partsPrefix`), since the unit
loop reports that fault in source order. `tests/test_rd9_docroute.py::test_soft_source_reads_mixed_parts` checks
Python's side on the same units. -/

namespace VE.Service.SoftSourceExamples
open Lean VE.Service.Document

def rule : Json := Json.mkObj [("norm", Json.mkObj [("name", .str "s")])]
def unit (id : String) (s e : Nat) (kind : String) (content : Json) (status : Option String := none) : Json :=
  Json.mkObj ([("id", .str id), ("span", toJson [s, e]), ("kind", .str kind), ("meaning", .str "specified"),
    ("support", .str "none"), ("content", content)] ++ status.toList.map (("status", .str ·)))
def flat : List Json := [unit "u1" 0 24 "norm" rule, unit "u2" 24 38 "asserted" (toJson ["top"])]
def mixed (parts : List Json) (e : Nat := 38) : Json :=
  Json.mkObj [("id", .str "p"), ("span", toJson [0, e]), ("status", .str "MIXED"), ("parts", toJson parts)]
def checked : List Json :=
  [unit "u1" 0 24 "norm" rule (some "CHECKED"), unit "u2" 24 38 "asserted" (toJson ["top"]) (some "CHECKED")]

#guard softSourceNorms (toJson flat) == [rule]
-- The finding: a MIXED parent's norm part is in the soft source.
#guard softSourceNorms (toJson [mixed checked]) == [rule]
-- A parent whose parts end short of its span still yields them; the unit loop reports the partition fault.
#guard softSourceNorms (toJson [mixed checked 40]) == [rule]
-- A part that does not start at the cursor stops the source before it, and before every later unit.
#guard softSourceNorms (toJson [mixed checked.reverse, unit "u3" 38 40 "norm" rule]) == []
-- A non-object unit stops the source there, as `_parts` raises on it.
#guard softSourceNorms (toJson [unit "u1" 0 24 "norm" rule, .num 1, unit "u3" 24 38 "norm" rule]) == [rule]

end VE.Service.SoftSourceExamples
