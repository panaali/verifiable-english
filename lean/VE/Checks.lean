import VE.Surface
import VE.Finite

/-! Executable regressions. These commands are tests, not additional metatheory. -/
namespace VE.Checks

private def env : Environment where
  sorts := ["person", "service"]
  predicates := fun p =>
    if p == "deployed" then some ["service"]
    else if p == "owns" then some ["person", "service"] else none
  constants := fun _ => none

#guard Surface.parse env "for every service trueish, (there exists person falsehood, (falsehood owns trueish)).\n" ==
  some [.all "service" (.ex "person" (.binary "owns" (.var 0) (.var 1)))]
#guard Surface.parse env "(for every service s, (s is deployed)) and (for every service s, (true)).\n" ==
  some [.and (.all "service" (.unary "deployed" (.var 0))) (.all "service" .top)]
#guard Surface.print [.and (.all "service" .top) (.ex "person" .top)] ==
  "(for every service x0, (true)) and (there exists person x1, (true)).\n"

-- Rejection is checked directly, without a candidate-AST mismatch masking it.
#guard Surface.parse env "true." == none
#guard Surface.parse env "true.\r\n" == none
#guard Surface.parse env "true.\n\n" == none
#guard Surface.parse env "true .\n" == none
#guard Surface.parse env "(true).\n" == none
#guard Surface.parse env "true and false.\n" == none
#guard Surface.parse env "true.\t\n" == none
#guard Surface.parse env "for every service s, (for every service s, (true)).\n" == none
#guard Surface.parse env "for every service person, (true).\n" == none
#guard Surface.parse env "for every service not, (true).\n" == none
#guard Surface.parse env "for every service s, (true).\ns is deployed.\n" == none
#guard Surface.parse env "for every person p, (p is deployed).\n" == none
#guard Surface.parse env "for every service s, (there exists person p, (p equals s)).\n" == none

private def emptyModel : FiniteModel String where
  domains := fun _ => []
  constants := fun _ => none
  relations := fun _ => []

#guard Formula.eval emptyModel [] (.all "service" .bottom)
#guard !(Formula.eval emptyModel [] (.ex "service" .top))
#guard Formula.eval emptyModel [] (.implies (.ex "service" .top) .bottom)

end VE.Checks
