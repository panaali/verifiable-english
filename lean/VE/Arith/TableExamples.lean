import VE.Arith.Bounded

namespace VE.Arith.TableExamples
open VE.Arith

def k (n : Int) : Term := .num n
def call0 (f : String) : Term := .call f []
def byList (D : Defs) (φ : Formula) : Option (Bool × Nat) := Formula.evalB (D.opEnvList maxSteps) maxSteps [] φ 0
def name64 (c : Char) : String := "".pushn 'a' 63 |>.push c

def twice : Defs := [.fn "f" 0 (k 1), .fn "f" 0 (k 2), .pred "p" 0 (.eq (k 0) (k 1)), .pred "p" 0 (.eq (k 0) (k 0))]
def twiceCases : List Formula := [.eq (call0 "f") (k 2), .eq (call0 "f") (k 1), .call "p" []]
#guard twiceCases.map (decideBounded twice maxSteps) = [some (true, 10), some (false, 9), some (true, 6)]
#guard twiceCases.all fun φ => decideBounded twice maxSteps φ == byList twice φ

def near : Defs := [.fn (name64 'x') 0 (k 1), .fn (name64 'y') 0 (k 2), .fn "f" 0 (k 3), .fn "ff" 0 (k 4),
  .pred "f" 1 (.eq (.var 0) (k 5))]
def nearCases : List Formula := [
  .eq (call0 (name64 'x')) (k 1), .eq (call0 (name64 'y')) (k 2),
  .eq (call0 (name64 'z')) (k 2), .eq (call0 ("".pushn 'a' 63)) (k 2),
  .eq (call0 "f") (k 3), .eq (call0 "ff") (k 4), .eq (call0 "fff") (k 4),
  .call "f" [k 5], .call "ff" [k 5]]
#guard nearCases.map (decideBounded near maxSteps) =
  [some (true, 7), some (true, 10), none, none, some (true, 10), some (true, 13), none,
   some (true, 14), none]
#guard nearCases.all fun φ => decideBounded near maxSteps φ == byList near φ

def order : Defs := [.fn "h" 0 (k 1), .fn "g" 0 (call0 "h"), .fn "h" 0 (k 2), .fn "e" 0 (call0 "later"), .fn "later" 0 (k 7)]
def orderCases : List Formula := [.eq (call0 "g") (k 1), .eq (call0 "h") (k 2),
  .eq (call0 "e") (k 7), .eq (call0 "later") (k 7)]
#guard orderCases.map (decideBounded order maxSteps) = [some (true, 9), some (true, 10), none, some (true, 13)]
#guard orderCases.all fun φ => decideBounded order maxSteps φ == byList order φ

-- The same definitions must preserve UNKNOWN and exact work at each budget boundary.
#guard [0, 8, 9, 10, maxSteps].all fun limit =>
  orderCases.all fun φ => decideBounded order limit φ == Formula.evalB (order.opEnvList limit) limit [] φ 0

end VE.Arith.TableExamples
