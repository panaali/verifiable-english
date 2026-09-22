import VE.Order.Conservativity
import VE.Order.Gate

namespace VE.Order.Checks

def env : Environment where
  sorts := ["item", "empty"]
  constants c := if c == "object" then some (.user "item")
    else if ["n", "alias", "m"].contains c then some .int else none
  predicates p := if p == "value" then some [.user "item", .int]
    else if p == "marked" then some [.int] else none

def model : FiniteModel Nat where
  domains s := if s == "item" then [0, 1] else []
  constants c := if c == "n" || c == "alias" then some (.inr (-7))
    else if c == "m" then some (.inr 3)
    else if c == "object" then some (.inl 0) else none
  relations p := if p == "value" then [[.inl 0, .inr (-7)], [.inl 1, .inr 3]]
    else if p == "marked" then [[.inr 3]] else []

#guard (Formula.lt (.const "n") (.num 0)).check env []
#guard (Formula.binary "value" (.const "object") (.add (.num (-10)) (.num 3))).check env []
#guard !(Formula.lt (.const "object") (.num 0)).check env []
#guard !(Formula.eq (.const "object") (.num 0)).check env []
#guard !(Formula.le (.var 0) (.num 0)).check env []
#guard !(Formula.unary "marked" (.scale 0 (.const "object"))).check env []
#guard !(Formula.all "$int" .top).check env []
#guard !(Formula.all "$int" .top).check {env with sorts := ["$int"]} []
#guard !(Formula.ex "$int" .top).check {env with sorts := ["$int"]} []
#guard (Formula.all "item" (.binary "value" (.var 0) (.const "n"))).check env []

#guard (Formula.lt (.const "n") (.num 0)).eval model []
#guard !(Formula.lt (.const "m") (.num 3)).eval model []
#guard (Formula.le (.const "m") (.num 3)).eval model []
#guard (Formula.eq (.const "alias") (.const "n")).eval model []
#guard !(Formula.eq (.const "object") (.num 0)).eval model []
#guard !(Formula.eq (.const "missing") (.const "missing")).eval model []
#guard !(Formula.eq (.scale 0 (.const "object")) (.num 0)).eval model []
#guard (Formula.eq (.scale (-3) (.const "n")) (.num 21)).eval model []
#guard (Formula.eq ((.const "n" : Term).neg) (.num 7)).eval model []
#guard (Formula.eq ((.const "n" : Term).sub (.const "m")) (.num (-10))).eval model []
#guard (Formula.eq (.add (.num 10000000000000000000000000000000000000000) (.num 1))
    (.num 10000000000000000000000000000000000000001)).eval model []
#guard (Formula.unary "marked" (.add (.num 1) (.num 2))).eval model []
#guard !(Formula.unary "marked" (.num 1000000)).eval model []
#guard (Formula.ex "item" (.binary "value" (.var 0) (.num (-7)))).eval model []
#guard !(Formula.all "item" (.binary "value" (.var 0) (.num (-7)))).eval model []
#guard (Formula.all "empty" .bottom).eval model []
#guard !(Formula.ex "empty" .top).eval model []
#guard countermodelCheck model [.lt (.const "n") (.num 0)] (.le (.num 0) (.const "n"))
#guard !countermodelCheck model [.lt (.num 0) (.const "n")] .bottom

end VE.Order.Checks
