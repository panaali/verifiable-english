import VE.Arith.BoundedExamples

/-! me-12nb evidence, not product code (nothing imports it): the three costs spec 12.2 leaves uncharged, each at its
worst within 12.5's wire limits, and each unknown at `maxSteps`. Run from `lean/`:
`lake env lean ../docs/math-evidence/me-12nb/uncharged-costs.lean` (times in the REPORT). -/

namespace VE.Arith.Examples
open VE.Arith

/-! A parameter read walks ρ: a function of 4,000 parameters (about 8,000 JSON nodes) reads its last one twice per
step of a count. -/
def wide : Defs := [.fn "p" 4000 (.countFromTo (lit 1) (lit 1000000) (.eq (.var 4000) (.var 4000)))]
#guard decideBounded wide maxSteps (.le (lit 0) (.call "p" ((List.range 4000).map fun _ => lit 0))) = none

/-! A call looks its name up among the definitions, newest first: 511 definitions of 64-byte names that differ only
in their last bytes, and a 512th whose body is a product tree of 1,024 calls of the first one (about 6 units each). -/
def nm (i : Nat) : String := "".pushn 'a' (62 - (toString i).length) ++ "_" ++ toString i ++ "_"
def tree : Nat → Term
  | 0 => .call (nm 0) []
  | n + 1 => .mul (tree n) (tree n)
def dense : Defs := (List.range 511).map (fun i => .fn (nm i) 0 (lit 1)) ++ [.fn "s" 0 (tree 10)]
#guard (nm 0).length = 64 && dense.WellFormed && decideBounded dense maxSteps (.eq (.call "s" []) (lit 1)) = some (true, 6147)
#guard decideBounded dense maxSteps (.allFromTo (lit 1) (lit 1000) (.eq (.call "s" []) (lit 1))) = none

/-! A range up to a 65,537-bit bound: its remaining count is decremented at each step, uncharged. -/
#guard decideBounded (sqChain 16) maxSteps (.allFromTo (lit 1) (.call "g16" []) yes) = none

end VE.Arith.Examples
