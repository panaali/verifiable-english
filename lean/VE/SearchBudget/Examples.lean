import VE.SearchBudget.Budget

/-! Fixtures of the demand count and the raised bounds (premise-scale): QT-0p's "exactly three principal
types" by constants and by an existential chain, the same facts under a disjunction (no fact), and a sort
past the cap. -/
namespace VE.SearchBudget.Examples
open VE VE.SearchBudget

def types : List (String × String) :=
  [("anthropic", "principal_type"), ("operators", "principal_type"), ("users", "principal_type"),
   ("alice", "person")]

def ne (t u : Term) : Formula := .not (.eq t u)

def threeConstants : Formula :=
  .and (ne (.const "anthropic") (.const "operators"))
    (.and (ne (.const "anthropic") (.const "users")) (ne (.const "operators") (.const "users")))

def threeChain : Formula :=
  .ex "principal_type" (.ex "principal_type" (.ex "principal_type"
    (.and (ne (.var 0) (.var 1)) (.and (ne (.var 0) (.var 2)) (ne (.var 1) (.var 2))))))

#guard demand types [threeConstants] "principal_type" == 3
#guard demand types [threeConstants] "person" == 1  -- one constant: one entity
#guard demand types [threeChain] "principal_type" == 3
#guard demand types [.or threeConstants .top] "principal_type" == 1  -- no fact: one constant
-- Two of the three pairs stated: the greedy choice keeps two.
#guard demand types [.and (ne (.const "anthropic") (.const "operators"))
  (ne (.const "anthropic") (.const "users"))] "principal_type" == 2
#guard sortBounds premiseBudget types [threeConstants] ["person", "principal_type"] ==
  [("principal_type", 3, 3)]

def nine : List (String × String) := (List.range 9).map fun i => (s!"t{i}", "principal_type")

def allDistinct (cs : List (String × String)) : List Formula :=
  cs.flatMap fun (a, _) => cs.filterMap fun (b, _) => if a < b then some (ne (.const a) (.const b)) else none

#guard demand nine (allDistinct nine) "principal_type" == 9
#guard sortBounds premiseBudget nine (allDistinct nine) ["principal_type"] == []
#guard sortBounds premiseBudget (nine.take 8) (allDistinct (nine.take 8)) ["principal_type"] ==
  [("principal_type", 8, 8)]

end VE.SearchBudget.Examples
