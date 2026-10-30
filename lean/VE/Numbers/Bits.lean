/-! The size of a value (spec 12.2 and 3.2): one owner for `arith@0`'s budget and `calc@0`'s work. -/

namespace VE.Numbers

/-- The size of a value: the bit length of its magnitude, and 1 for 0. -/
def bits (x : Int) : Nat := x.natAbs.log2 + 1

end VE.Numbers
