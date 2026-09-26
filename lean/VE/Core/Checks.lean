import VE.Core.Bridge

namespace VE.Core.Checks

def env : Environment := ⟨["node"], fun p => if p = "edge" then some ["node", "node"] else none,
  fun c => if c = "start" then some "node" else none⟩

def model : FiniteModel Nat := ⟨fun _ => [0, 1, 2], fun _ => some 0,
  fun _ => [[0, 1], [1, 0], [1, 2]]⟩

#guard (Formula.reachNamed .plus "edge" (.const "start") (.const "start")).eval model []
#guard !(Formula.reachNamed .plus "edge" (.var 0) (.var 0)).eval model [2]
#guard (Formula.reachNamed .star "edge" (.var 0) (.var 0)).eval model [2]
#guard !(Formula.reachNamed .plus "edge" (.var 0) (.var 1)).eval model [2, 0]
#guard (Formula.reachBody .plus "node" (.binary "edge" (.var 1) (.var 0))
  (.var 0) (.var 1)).eval model [0, 2]
#guard !(Formula.reachBody .plus "node"
  (.and (.binary "edge" (.var 1) (.var 0)) (.not (.eq (.var 0) (.var 2))))
  (.var 1) (.var 2)).eval model [1, 0, 2]
#guard (Formula.reachBody .plus "node"
  (.and (.binary "edge" (.var 1) (.var 0)) (.not (.eq (.var 0) (.var 2))))
  (.var 1) (.var 2)).eval model [0, 0, 2]
#guard (Formula.all "empty" (.bottom)).eval ⟨fun _ => [], fun _ => none, fun _ => []⟩ ([] : List Nat)
#guard !(Formula.ex "empty" (.reachNamed .star "edge" (.var 0) (.var 0))).eval
  ⟨fun _ => [], fun _ => none, fun _ => []⟩ ([] : List Nat)
#guard (Formula.reachNamed .plus "edge" (.const "start") (.const "start")).check env []
#guard !(Formula.reachBody .star "node" .top (.var 0) (.var 1)).check env []
#guard Surface.parse env "tc[edge](@start, @start).\n" ==
  some [.reachNamed .plus "edge" (.const "start") (.const "start")]
#guard Surface.parse env "rtc[node a, b | (a edge b)](@start, @start).\n" ==
  some [.reachBody .star "node" (.binary "edge" (.var 1) (.var 0)) (.const "start") (.const "start")]

def naryEnv : Environment := ⟨["signal", "time", "reading"],
  fun p => if p = "value" then some ["signal", "time", "reading"] else none,
  fun c => if c = "speed" then some "signal"
    else if c = "instant" then some "time"
    else if c = "high" then some "reading" else none⟩

def naryModel : FiniteModel Nat := ⟨fun s =>
    if s = "signal" then [0] else if s = "time" then [1] else [2],
  fun c => if c = "speed" then some 0
    else if c = "instant" then some 1
    else if c = "high" then some 2 else none,
  fun p => if p = "value" then [[0, 1, 2]] else []⟩

def valueAtom : Formula := .atom "value" [.const "speed", .const "instant", .const "high"]

#guard valueAtom.check naryEnv []
#guard valueAtom.eval naryModel []
#guard !(Formula.atom "value" [.const "speed", .const "high", .const "instant"]).check naryEnv []
#guard Surface.parse naryEnv "value(@speed, @instant, @high).\n" == some [valueAtom]
#guard Surface.parse naryEnv (Surface.print [valueAtom]) == some [valueAtom]

end VE.Core.Checks
