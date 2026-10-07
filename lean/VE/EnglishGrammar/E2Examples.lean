import VE.EnglishGrammar.ProfileExamples

/-! The acceptance fixtures of docs/spec/english-lean-e2.md section 8 as `#guard` checks on the built port,
the overlay check, the request guards and the service modes.

The environments are those of `ReadExamples` (`F`) and `ProfileExamples` (`FA`, `FR`, `FM`, decoded at the
boundary). Each block names the fixture ids of section 8 it checks.
-/

namespace VE.EnglishGrammar.E2Examples
open Lean VE.Grammar VE.EnglishGrammar

/-! ## The wire form of integers (`decode_encode`)

`intText` is the text `toString` writes, here on the compiled code, so `decode_encode`, proved of `intText`, is
a statement about the wire form the service sends. -/

#guard [0, 1, 9, 10, 99, 100, 12345678901234567890, -1, -9, -10, -100, -12345678901234567890].all
  fun (v : Int) => intText v == toString v
#guard ((List.range 2001).map fun (n : Nat) => (n : Int) - 1000).all fun v => intText v == toString v
#guard [EFormula.top, .pred "p" [], .pred "p" [.num (-3)], .pred "q" [.var 0, .scale (-2) (.const "c")],
  .pred "r" [.num 0, .num 1, .add (.num (-1)) (.var 2)], .not (.eq (.num 7) (.num (-7))),
  .reachBody true "s" (.lt (.var 0) (.num (-12))) (.const "a") (.const "b"),
  .reachNamed false "next" (.var 1) (.var 0)].all fun A => EFormula.decode A.encode == some A

end VE.EnglishGrammar.E2Examples
