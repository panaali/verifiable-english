import VE.Calc.Identity

/-! `#guard`s for the trusted definitions of `Inline.lean` (R16, `tools/trust_mutants.py`). The runner's fixtures,
R-6 and H-4 among them, are `tests/test_calc_algebra.py`. -/

namespace VE.Calc.IdentityExamples
open VE.Calc

def ds : List Decl :=
  [⟨"a", .free⟩, ⟨"s", .stated 5⟩, ⟨"b", .free⟩, ⟨"d", .defined (.div (.val "a") (.val "b"))⟩,
   ⟨"c", .counted (Thunk.pure (some 7)) (.ok (some 7))⟩]
def κ (n : String) : Rat := if n = "a" then 3 else 2

#guard freeNames ds = ["a", "b"]
-- The assigned names take κ's value, a definition reads them, and every other declaration keeps its own.
#guard ["a", "s", "b", "d", "c", "z"].map (values (assign ds ["a", "b"] κ)) =
  [some 3, some 5, some 2, some (3 / 2), some 7, none]
#guard ["a", "b", "d"].map (values (assign ds ["a"] κ)) = [some 3, none, none]
#guard (assign ds ["a", "s"] κ).map Decl.name = ds.map Decl.name

end VE.Calc.IdentityExamples
