import VE.Tableau
import VE.TableauExtended
import VE.Core.TableauExtended
import VE.Order.Tableau
import VE.CertificateWire
import Lean.Data.Json

/-! Certificate replay steps.

Python replays a certificate under `max_steps = 10,000`, one step per trace
node, and reports `ResourceLimit` when a trace needs more; the frozen Lean
checkers bound only the trace's depth. Each runner counts a decoded trace's
nodes before replaying it: a route or quantity certificate case reports the
limit, and a certificate inside an admission graph, a lemma bundle or a
quantity document is not established, as in Python. -/
namespace VE.Route.Steps

abbrev maxSteps : Nat := VE.CertificateWire.maxSteps
abbrev stepLimit : String := VE.CertificateWire.stepLimit
abbrev caseCap : Nat := VE.CertificateWire.caseCap
abbrev limit (j : Lean.Json) : Except String Nat := VE.CertificateWire.limit j
abbrev fol (trace : VE.Tableau.Trace) : Nat := VE.CertificateWire.folSteps trace
abbrev closure (trace : VE.Closure.Tableau.Trace) : Nat := VE.CertificateWire.closureSteps trace

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
