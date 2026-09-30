import VE.Discourse.Documents

/-! # Fixture models (docs/spec/discourse.md section 10), checked by `decide`

μ: on `twoServices` (`s1` deployed not reviewed, `s2` reviewed not deployed) the split
formula `∃x deployed(x) ∧ ∃x reviewed(x)` is true and the fused same-witness formula is
false. ξ: the description "the owner" over `person`, with `U(D)`, the assertive and the
presuppositional readings evaluated on the five models of the fixture. η: the same three
formulas for `manager_of(x, alice)`, with two managers both ready. -/
namespace VE.Discourse
namespace Examples

def twoServices : VE.FiniteModel String where
  domains s := if s = "service" then ["s1", "s2"] else []
  constants _ := none
  relations p := if p = "deployed" then [["s1"]] else if p = "reviewed" then [["s2"]] else []

def splitFormula : VE.Formula :=
  .and (.ex "service" (.unary "deployed" (.var 0))) (.ex "service" (.unary "reviewed" (.var 0)))

def fusedFormula : VE.Formula := fused "service" (.unary "deployed" (.var 0)) (.unary "reviewed" (.var 0))

/-- A `person` model with the listed owners and ready people among `p1`, `p2`. -/
def ownerModel (owners ready : List String) : VE.FiniteModel String where
  domains s := if s = "person" then ["p1", "p2"] else []
  constants _ := none
  relations p := if p = "owner" then owners.map (fun x => [x]) else if p = "ready" then ready.map (fun x => [x]) else []

def ownerR : VE.Formula := .unary "owner" (.var 0)
def readyP : VE.Formula := .unary "ready" (.var 0)

/-- The three ξ formulas on a model: (U(D), assertive, presuppositional). -/
def xi (M : VE.FiniteModel String) : Bool × Bool × Bool :=
  ((uniqueD "person" ownerR).eval M [], (assertive "person" ownerR readyP).eval M [],
    (presupposed "person" ownerR readyP).eval M [])

/-- η: Alice's managers `p1`, `p2` among `alice`, `p1`, `p2`. -/
def managerModel (managers ready : List String) : VE.FiniteModel String where
  domains s := if s = "person" then ["alice", "p1", "p2"] else []
  constants c := if c = "alice" then some "alice" else none
  relations p := if p = "manager_of" then managers.map (fun x => [x, "alice"])
    else if p = "ready" then ready.map (fun x => [x]) else []

def managerR : VE.Formula := .binary "manager_of" (.var 0) (.const "alice")

def eta (M : VE.FiniteModel String) : Bool × Bool × Bool :=
  ((uniqueD "person" managerR).eval M [], (assertive "person" managerR readyP).eval M [],
    (presupposed "person" managerR readyP).eval M [])

end Examples

open Examples in
/-- μ: the fused reading implies the split reading, and the converse fails here. -/
theorem split_not_fused_model :
    (Examples.splitFormula).eval Examples.twoServices [] = true ∧
    (Examples.fusedFormula).eval Examples.twoServices [] = false := by decide

open Examples in
/-- ξ: no owner (U false, assertive false, presuppositional vacuously true); two owners both
ready (presuppositional true); two owners one not ready (all false); one ready owner (all
true); one owner not ready (U true, the others false). -/
theorem xi_models :
    xi (ownerModel [] []) = (false, false, true) ∧
    xi (ownerModel ["p1", "p2"] ["p1", "p2"]) = (false, false, true) ∧
    xi (ownerModel ["p1", "p2"] ["p1"]) = (false, false, false) ∧
    xi (ownerModel ["p1"] ["p1"]) = (true, true, true) ∧
    xi (ownerModel ["p1"] []) = (true, false, false) := by decide

open Examples in
/-- η: two managers of Alice both ready (U false, assertive false, presuppositional true);
two managers one not ready (all false); no manager (presuppositional vacuously true). -/
theorem eta_models :
    eta (managerModel ["p1", "p2"] ["p1", "p2"]) = (false, false, true) ∧
    eta (managerModel ["p1", "p2"] ["p1"]) = (false, false, false) ∧
    eta (managerModel [] []) = (false, false, true) := by decide

end VE.Discourse
