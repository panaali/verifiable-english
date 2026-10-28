import VE.Arith.Bounded

namespace VE.Arith.TableExamples
open VE.Arith

def k (n : Int) : Term := .num n
def call0 (f : String) : Term := .call f []
def byList (D : Defs) (φ : Formula) : Option (Bool × Nat) := Formula.evalB (D.opEnvList maxSteps) maxSteps [] φ 0
def name64 (c : Char) : String := "".pushn 'a' 63 |>.push c

def twice : Defs := [.fn "f" 0 (k 1), .fn "f" 0 (k 2), .pred "p" 0 (.eq (k 0) (k 1)), .pred "p" 0 (.eq (k 0) (k 0))]
#eval [decideBounded twice maxSteps (.eq (call0 "f") (k 2)), decideBounded twice maxSteps (.eq (call0 "f") (k 1)),
  decideBounded twice maxSteps (.call "p" [])]

def near : Defs := [.fn (name64 'x') 0 (k 1), .fn (name64 'y') 0 (k 2), .fn "f" 0 (k 3), .fn "ff" 0 (k 4),
  .pred "f" 1 (.eq (.var 0) (k 5))]
#eval [decideBounded near maxSteps (.eq (call0 (name64 'x')) (k 1)), decideBounded near maxSteps (.eq (call0 (name64 'y')) (k 2)),
  decideBounded near maxSteps (.eq (call0 (name64 'z')) (k 2)), decideBounded near maxSteps (.eq (call0 ("".pushn 'a' 63)) (k 2)),
  decideBounded near maxSteps (.eq (call0 "f") (k 3)), decideBounded near maxSteps (.eq (call0 "ff") (k 4)),
  decideBounded near maxSteps (.eq (call0 "fff") (k 4)), decideBounded near maxSteps (.call "f" [k 5]),
  decideBounded near maxSteps (.call "ff" [k 5])]

def order : Defs := [.fn "h" 0 (k 1), .fn "g" 0 (call0 "h"), .fn "h" 0 (k 2), .fn "e" 0 (call0 "later"), .fn "later" 0 (k 7)]
#eval [decideBounded order maxSteps (.eq (call0 "g") (k 1)), decideBounded order maxSteps (.eq (call0 "h") (k 2)),
  decideBounded order maxSteps (.eq (call0 "e") (k 7)), decideBounded order maxSteps (.eq (call0 "later") (k 7))]

end VE.Arith.TableExamples
