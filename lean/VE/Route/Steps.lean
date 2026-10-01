import VE.Tableau
import VE.TableauExtended
import VE.Core.TableauExtended
import VE.Order.Tableau
import Lean.Data.Json

/-! Certificate replay steps.

Python replays a certificate under `max_steps = 10,000`, one step per trace
node, and reports `ResourceLimit` when a trace needs more; the frozen Lean
checkers bound only the trace's depth. Each runner counts a decoded trace's
nodes before replaying it: a route or quantity certificate case reports the
limit, and a certificate inside an admission graph, a lemma bundle or a
quantity document is not established, as in Python. -/
namespace VE.Route.Steps

def maxSteps : Nat := 10000

def stepLimit : String := "ResourceLimit: certificate replay exceeds 10,000 steps"

/-- The largest `max_steps` a route certificate case may request. -/
def caseCap : Nat := 1000000

/-- A route certificate case's step cap: its `max_steps` field (at most
`caseCap`; the adapter sets it to learn validity past the default budget, and
applies the caller's public budget itself), else `maxSteps`. -/
def limit (j : Lean.Json) : Nat :=
  match j.getObjVal? "max_steps" >>= (·.getNat?) with
  | .ok n => min n caseCap
  | .error _ => maxSteps

mutual
def fol : VE.Tableau.Trace → Nat
  | .close => 1
  | .expand _ _ cs => 1 + folList cs
def folList : List VE.Tableau.Trace → Nat
  | [] => 0
  | c :: cs => fol c + folList cs
end

mutual
def closure : VE.Closure.Tableau.Trace → Nat
  | .close => 1
  | .expand _ _ _ cs => 1 + closureList cs
  | .induct _ _ _ cs => 1 + closureList cs
def closureList : List VE.Closure.Tableau.Trace → Nat
  | [] => 0
  | c :: cs => closure c + closureList cs
end

mutual
def core : VE.Core.Tableau.Trace → Nat
  | .close => 1
  | .expand _ _ _ cs => 1 + coreList cs
  | .induct _ _ _ cs => 1 + coreList cs
def coreList : List VE.Core.Tableau.Trace → Nat
  | [] => 0
  | c :: cs => core c + coreList cs
end

mutual
def order : VE.Order.Tableau.Trace → Nat
  | .close => 1
  | .expand _ _ cs => 1 + orderList cs
  | .split _ cs => 1 + orderList cs
  | .neq _ cs => 1 + orderList cs
  | .farkas _ _ => 1
def orderList : List VE.Order.Tableau.Trace → Nat
  | [] => 0
  | c :: cs => order c + orderList cs
end

end VE.Route.Steps
