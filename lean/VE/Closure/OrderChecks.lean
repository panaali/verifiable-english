import VE.Closure.Order

namespace VE.Closure.OrderChecks

private def names : List String := ["a", "b", "c", "d"]
private def links : List (String × String) := [("a", "b"), ("b", "c")]
private def order : Order String := ⟨names, links⟩
private def standardCaps : Caps := ⟨16, 64⟩
private def edgeCap : Caps := ⟨16, 1⟩
private def emptyCaps : Caps := ⟨0, 0⟩
private def tooMany : Order String := ⟨List.range 17 |>.map toString, []⟩
private def undeclared : Order String := ⟨names, [("a", "absent")]⟩
private def result : Except String Unit → String
  | .ok _ => "ok"
  | .error s => s

#guard order.above "a" "c"
#guard !order.above "c" "a"
#guard !order.above "a" "a"
#guard order.atLeast "a" "a"
#guard !order.atLeast "d" "a"
#guard order.atLeast "a" "c"
#guard result (order.admit standardCaps) == "ok"
#guard result (tooMany.admit standardCaps) ==
  "ResourceLimit: At most 16 grades"
#guard result (undeclared.admit standardCaps) ==
  "UnknownSymbol: an order pair names an undeclared element"
#guard result (order.admit edgeCap) == "ResourceLimit: At most 1 order pairs"
#guard result (order.admit emptyCaps) == "ResourceLimit: At most 0 grades"

private def pairs : List (String × String) := names.flatMap (fun a => names.map (a, ·))
private def softAgrees : Bool := pairs.all fun p =>
  (VE.SoftNorms.belowAt (VE.SoftNorms.closureOf names links) p.1).contains p.2 == order.above p.1 p.2
private def softTrue : Nat := (pairs.filter fun p => order.above p.1 p.2).length
#guard pairs.length == 16
#guard softAgrees
#guard softTrue == 3

private def riskLinks : List (String × String) := links ++ [("c", "d")]
private def riskOrder : Order String := ⟨names, riskLinks⟩
private def riskAgrees : Bool := pairs.all fun p =>
  (VE.Risk.closeIter names (names.length + 1) riskLinks).contains p == riskOrder.above p.1 p.2
private def riskTrue : Nat := (pairs.filter fun p => riskOrder.above p.1 p.2).length
#guard riskAgrees
#guard riskTrue == 6

end VE.Closure.OrderChecks
