import VE.Calc.Wire

/-! Fixtures of the charged lowering (spec 3.2 (b), 13.3; me-2nc): units *by hand* in 13.3, computed here by product
code. The decoder's limit 10 at P-2 and N-1's premise counts is pinned on the service (`tests/test_calc_service.py`):
those cases run too long for `#guard`'s interpreter. -/

namespace VE.Calc.WorkExamples
open VE.Calc VE.Calc.Work VE.Numbers

def nines : Rat := 10 ^ 40 - 1
def powChain : Nat → Expr
  | 0 => .lit nines
  | k + 1 => .pow (powChain k) 64
def lowered (e : Expr) : Option (Option QLin × Nat) := (Expr.linearC maxWork e 0).map fun
  | (.form L, w) => (some L, w)
  | (_, w) => (none, w)
def isBeyond (e : Expr) : Bool := match Expr.linearC maxWork e 0 with
  | some (.tooLarge _, _) => true
  | _ => false

/-! L-1 to L-5: L-1 lowers (2,560 digits), L-2 to L-4 are ruled out from the base and never computed, and the charge
refuses at the limit, not past it. -/
#guard (lowered (powChain 1)).map (·.1) = some (powChain 1).linear
#guard [1, 2, 3, 4].map (fun k => (lowered (powChain k)).map (·.2)) = [some 8642, some 8643, some 8644, some 8645]
#guard !isBeyond (powChain 1) && [2, 3, 4].all fun k => isBeyond (powChain k)
#guard (Expr.linearC 8641 (powChain 1) 0).isNone && (Expr.linearC 8642 (powChain 1) 0).isSome
def big : Expr := .mul (.pow (.lit nines) 64) (.pow (.lit nines) 38)
#guard !isBeyond big && isBeyond (.mul big big)
#guard match Expr.linearC maxWork (.mul big big) 0 with | some (.tooLarge _, w) => w == 81879 | _ => false
-- The digit limit's boundary: 10^4,096 − 1 stays a form, 10^4,096 does not, as a constant or as a coefficient.
def limitValue : Rat := 10 ^ maxDigits
#guard !isBeyond (.lit (limitValue - 1)) && isBeyond (.lit limitValue)
#guard !isBeyond (.mul (.lit (limitValue - 1)) (.val "x")) && isBeyond (.mul (.lit limitValue) (.val "x"))
#guard !isBeyond (.div (.val "x") (.lit (limitValue - 1))) && isBeyond (.div (.val "x") (.lit limitValue))

/-! P-1 and P-2: one premise's units, in 13.3, and P-2's premise count at limit 10. -/
def keep : List String := (List.range 16).map (s!"u{·}")
def lowerName (ds : List Decl) (n : String) : Option (Option QLin × Nat) :=
  match Expr.inline ds keep (.val n) with
  | .ok e => lowered e
  | .error _ => none
def defd (n : String) (e : Expr) : Decl := ⟨n, .defined e⟩
def fan (k : Nat) : List Decl :=
  ⟨"u0", .free⟩ :: defd "a0" (.val "u0") ::
    (List.range k).map fun i => defd s!"a{i + 1}" (.add (.val s!"a{i}") (.val s!"a{i}"))
#guard (lowerName (fan 12) "a12").map (·.2) = some 16824301
#guard match Expr.inline (fan 12) keep (.val "a12") with
  | .ok e => (e.nodesWithin maxPolyTerms).isSome && (lowered e).map (·.1) == some e.linear
  | .error _ => false
def dense (k : Nat) : List Decl :=
  keep.map (fun n => (⟨n, .free⟩ : Decl)) ++
  [defd "big" (.pow (.lit nines) 20),
   defd "a0" (.mul (.val "big") ((List.range 15).foldl (fun e j => .add e (.val s!"u{j + 1}")) (.val "u0")))] ++
  (List.range k).map fun i => defd s!"a{i + 1}" (.add (.val s!"a{i}") (.val s!"a{i}"))
#guard (lowerName (dense 8) "a8").map (·.2) = some 118478125
#guard 72 * 118478125 < maxWork && maxWork < 73 * 118478125

/-! S-1 to S-10 (me-2n review F2): a side beyond the digit limit keeps 5's linearity. C is beyond the limit and never
computed; S-8 to S-10 add sides whose coefficients may cancel, decided exactly, charged before it is computed. -/
-- A power of a form that is not constant: the 0th builds a new form and pays for it, the 1st reuses the form.
#guard (lowered (.pow (.val "x") 1)).map (·.2) = some 2054 && (lowered (.pow (.val "x") 0)).map (·.2) = some 2056
def C : Expr := powChain 2
def xC : Expr := .add (.val "x") C
def shapes : List Expr :=
  [.pow xC 2, .mul xC (.val "x"), .div (.val "x") xC,                                  -- S-1 to S-3: not linear
   .mul xC C, .div xC C, .pow xC 1, .pow xC 0,                                         -- S-4 to S-7: linear
   .mul (.sub (.mul C (.val "x")) (.mul C (.val "x"))) (.val "x"),                      -- S-8: cancels, linear
   .mul (.sub (.mul C (.val "x")) (.mul C (.val "y"))) (.val "x"),                      -- S-9: not linear
   .div (.val "x") (.sub C C)]                                                          -- S-10: a zero divisor
def linearity (e : Expr) : Option Bool := (Expr.linearC maxWork e 0).map fun
  | (.nonlinear, _) => false
  | _ => true
#guard shapes.map linearity = [false, false, false, true, true, true, true, true, false, false].map some
#guard shapes.all fun e => linearity e == some e.linear.isSome
#guard [0, 7].map (fun i => (Expr.linearC maxWork (shapes.getD i (.lit 0)) 0).map (·.2)) = [some 10698, some 144138778]
#guard (Expr.linearC 144138777 (shapes.getD 7 (.lit 0)) 0).isNone && (Expr.linearC 144138778 (shapes.getD 7 (.lit 0)) 0).isSome
#guard match Expr.linearC maxWork (shapes.getD 7 (.lit 0)) 0 with
  | some (.tooLarge s, _) => s == .const (some false)
  | _ => false
-- The exact fallback refuses before it computes: a bound past limit 10, on a value of 64^4 powers.
def hugeC : Expr := powChain 4
def hugeCancel : Expr := .mul (.sub (.mul hugeC (.val "x")) (.mul hugeC (.val "x"))) (.val "x")
#guard maxWork < Expr.exactBound hugeCancel && (Expr.linearC maxWork hugeCancel 0).isNone

/-! The shape rules, each way (5's linearity): a constant zero factor, a nonzero one, and a sum that may cancel. -/
#guard [addS (.const (some false)) .nonconst, addS .nonconst (.const (some false))].all (· matches .linear .nonconst)
#guard addS (.const (some true)) (.const none) matches .linear (.const none)
#guard addS (.const none) .nonconst matches .linear .nonconst
#guard addS .nonconst .nonconst matches .linear .unknown
#guard mulS (.const (some false)) .nonconst matches .linear (.const (some false))
#guard mulS .nonconst (.const (some true)) matches .linear .nonconst
#guard mulS (.const none) .nonconst matches .linear .unknown
#guard mulS .nonconst .nonconst matches .nonlinear
#guard mulS .unknown .nonconst matches .unknown
#guard (divS .nonconst (.const (some true)) matches .linear .nonconst) && (divS .nonconst (.const (some false)) matches .nonlinear)
#guard (divS .nonconst .nonconst matches .nonlinear) && (divS .nonconst (.const none) matches .unknown) && (divS .nonconst .unknown matches .unknown)
#guard (powS .nonconst 0 matches .linear (.const (some true))) && (powS .nonconst 1 matches .linear .nonconst)
#guard (powS (.const none) 2 matches .linear (.const none)) && (powS .nonconst 2 matches .nonlinear) && (powS .unknown 2 matches .unknown)

/-! The one-pass steps equal 5's (me-2n review F1). N-1 is `QLin.norm`'s case: a side of 8 mentions of a sum of 400
free values. -/
def names (k : Nat) : List String := (List.range k).map (s!"v{·}")
def forms : List QLin :=
  [⟨1, [("a", 1), ("b", 2), ("a", -1), ("c", 0), ("b", 1/2)]⟩, ⟨0, [("a", 1), ("a", -1)]⟩, ⟨3, []⟩,
   ⟨0, (names 400).map (·, 1) ++ (names 400).reverse.map (·, 2)⟩]
#guard forms.all fun L => QLin.normOnce L == L.norm && L.isConstOnce == L.isConst
#guard forms.map QLin.isConstOnce = [false, true, true, false]
def pairUp : List Expr → List Expr
  | a :: b :: r => .add a b :: pairUp r
  | r => r
/-- The review probe's balanced sum: neighbours paired, round by round. -/
def balanced (es : List Expr) : Expr := ((List.range 12).foldl (fun acc _ => pairUp acc) es).headD (.lit 0)
def n1Side : Expr := balanced ((List.range 8).map fun _ => balanced ((names 400).map .val))
#guard (lowered n1Side).map (·.2) = some 70576397

/-! The pick probe's stages (me-2n review F1): 0 < x − k_i and 0 < s + b_j − x over s = y + z1 + ... + z14, for the
conclusion y < 0; bounds on y increasing (`inc`) or decreasing in row order. -/
def zs : List String := (List.range 14).map (s!"z{· + 1}")
def probeFacts (sign : Int) (np nn : Nat) : List QFact :=
  (List.range np).map (fun i => ⟨⟨-(sign * 1000 * i), [("x", 1)]⟩, true⟩) ++
  (List.range nn).map (fun j => ⟨⟨-(sign * j), ("y", 1) :: zs.map (·, 1) ++ [("x", -1)]⟩, true⟩) ++
  [⟨⟨0, [("y", 1)]⟩, false⟩]
def stageY (fs : List QFact) : List FM.Row :=
  match (FM.run (FM.unknowns fs) (FM.inputRows fs) []).run' FM.maxSteps with
  | .ok (_, stages) => ((stages.find? (·.1 == "y")).map (·.2)).getD []
  | .error _ => []
def κz : List (String × Rat) := zs.map (·, 0)
def mixed : List FM.Row := [⟨1, [("x", 2)]⟩, ⟨-3, [("x", 1), ("y", 1)]⟩, ⟨-4, [("x", 2)]⟩, ⟨5, [("x", -1)]⟩,
  ⟨5, [("x", -1)]⟩, ⟨2, [("y", 1)]⟩].zipIdx.map fun ((c, l), i) => ⟨⟨⟨c, l⟩, i % 2 == 0⟩, [1]⟩
#guard [1, -1].all fun sign => let r := stageY (probeFacts sign 8 7); r.length == 57 &&
  FM.pickOnce "y" r κz == FM.pick "y" r κz
#guard [mixed, mixed.reverse, mixed.take 3, mixed.drop 3, []].all fun r =>
  [[], [("y", 1)], [("y", -7)]].all fun κ => FM.pickOnce "x" r κ == FM.pick "x" r κ
#guard FM.pickOnce "x" [] [] = 0
-- Equal bounds, one strict: the strict one rules the candidate out, on either side and in either order.
def tied (c : Rat) (s t : Bool) : List FM.Row := [⟨⟨⟨-c, [("x", c)]⟩, s⟩, [1]⟩, ⟨⟨⟨-c, [("x", c)]⟩, t⟩, [1]⟩]
#guard [(1, false, false), (1, true, false), (1, false, true), (1, true, true), (-1, true, false), (-1, false, true)].all
  fun (c, s, t) => FM.pickOnce "x" (tied c s t) [] == FM.pick "x" (tied c s t) []
#guard FM.pickOnce "x" (tied 1 false false) [] = 1 && FM.pickOnce "x" (tied 1 true false) [] = 2
-- A row without `x` that fails: no candidate fits, the midpoint or a step is taken instead.
def failing : List FM.Row := ⟨⟨⟨-1, []⟩, false⟩, [1]⟩ :: tied 1 false false
#guard FM.pickOnce "x" failing [] = FM.pick "x" failing [] && FM.pickOnce "x" failing [] = 2
#guard let fs := probeFacts 1 3 2 ++ [⟨⟨-1, [("y", -1)]⟩, false⟩]
  match (FM.search fs).run' FM.maxSteps with
  | .ok (.refuted ws) => [ws, ws.map (· * 2), ws.map (· - 1), ws.drop 1].all fun ws =>
      Farkas.checkOnce fs ⟨ws⟩ == Farkas.check fs ⟨ws⟩
  | _ => false
#guard Farkas.checkOnce [⟨⟨-1, []⟩, false⟩] ⟨[1]⟩ && !Farkas.checkOnce [⟨⟨0, []⟩, false⟩] ⟨[1]⟩ &&
  Farkas.checkOnce [⟨⟨0, []⟩, true⟩] ⟨[1]⟩ && !Farkas.checkOnce [⟨⟨0, [("x", 1)]⟩, true⟩] ⟨[1]⟩

/-! The decoder's check, once per side, names the part 5 names: a product inside a definition (`sq`), an unknown
name, P-1, a side beyond `maxPolyTerms` nodes, and S-1, S-2 and S-8 as premises over the declared value `C`. -/
def decoderDecls : List Decl :=
  [⟨"x", .free⟩, ⟨"y", .free⟩, defd "C" C, defd "sq" (.mul (.val "x") (.val "x"))] ++ fan 14
def decoderSides : List Expr :=
  [.add (.val "sq") (.lit 1), .add (.val "x") (.val "nope"), .val "a12", .val "a14", .mul (.val "a14") (.val "x"),
   .pow (.add (.val "x") (.val "C")) 2, .mul (.add (.val "x") (.val "C")) (.val "x"),
   .mul (.sub (.mul (.val "C") (.val "x")) (.mul (.val "C") (.val "x"))) (.val "x")]
def decoderTable : Inlined := inlineTable decoderDecls (freeNames decoderDecls)
#guard decoderSides.zipIdx.all fun (e, i) =>
  ((nonlinearAtC maxWork decoderTable s!"p{i}" e 0).map (·.1.1)) == some (Wire.nonlinearAt decoderTable s!"p{i}" e)
#guard decoderSides.zipIdx.map (fun (e, i) => Wire.nonlinearAt decoderTable s!"p{i}" e) =
  [some "p0.1", none, none, none, none, some "p5", some "p6", none]
-- The right operand's path, and a part inside a part: the decoder names the same one, not the node above it.
def nestedSides : List Expr :=
  [.add (.lit 1) (.val "sq"), .sub (.lit 1) (.add (.val "x") (.val "sq")), .mul (.lit 2) (.pow (.add (.val "x") (.lit 1)) 2),
   .div (.val "x") (.add (.val "x") (.lit 1))]
#guard nestedSides.map (Wire.nonlinearAt decoderTable "p") = [some "p.2", some "p.2.2", some "p.2", some "p"]
#guard nestedSides.map (fun e => (nonlinearAtC maxWork decoderTable "p" e 0).map (·.1.1)) =
  [some (some "p.2"), some (some "p.2.2"), some (some "p.2"), some (some "p")]
-- A side costs its `linearC` and never more: the written sum of two mentions, and P-1's name.
#guard (nonlinearAtC maxWork (inlineTable (fan 12) keep) "p" (.val "a12") 0).map (·.2) = some 16824301
def twice : Expr := .add (.val "a11") (.val "a11")
#guard (nonlinearAtC maxWork (inlineTable (fan 12) keep) "p" twice 0).map (·.2) = some 16824301
-- A written side keeps its lowering, and a part not judged has none, the node above it neither.
#guard match nonlinearAtC maxWork (inlineTable (fan 12) keep) "p" (.val "a12") 0 with
  | some ((none, some (.form L)), _) => some L == (Expr.inline (fan 12) keep (.val "a12")).toOption.bind Expr.linear
  | _ => false
#guard (nonlinearAtC maxWork decoderTable "p" (.add (.val "a14") (.lit 1)) 0) matches some ((none, none), _)
#guard (nonlinearAtC maxWork decoderTable "p" (.pow (.val "a14") 2) 0) matches some ((none, none), _)
#guard (nonlinearAtC maxWork decoderTable "p" (.pow (.add (.val "x") (.val "y")) 2) 0) matches some ((some "p", _), _)
#guard (nonlinearAtC 0 decoderTable "p" (.pow (.add (.val "x") (.val "y")) 2) 0).isNone

/-! `Wire.derivations`, in 3.2's order: only `.nonlinear` is `NonlinearPremise`; the first limit met refuses. -/
def eqc : Comparison := ⟨.lt, false⟩
def over : Claim := .compare eqc hugeCancel (.lit 0)
def bad : Claim := .compare eqc (.mul (.val "x") (.val "x")) (.lit 0)
def beyond : Claim := .compare eqc (.val "C") (.lit 0)
def judge (ps : List Claim) (k : List Check := []) : String :=
  match Wire.derivations decoderDecls (ps.zipIdx.map fun (c, i) => (s!"p{i}", c))
      (k.zipIdx.map fun (c, i) => (s!"c{i}", c)) with
  | .ok _ => "ok"
  | .error e => e
#guard judge [beyond] = "ok" && judge [] = "ok"
#guard judge [bad, over] = "NonlinearPremise: premises.0.claim.1 (declare a square link or name the product)"
#guard judge [over, bad] = Wire.workLimit
#guard judge [] [.follows [] [] bad] = "NonlinearPremise: claims.0.claim.1.1 (declare a square link or name the product)"
#guard judge [] [.follows [] [("x", "nope")] bad] = "UnknownLink: nope"
#guard judge [] [.follows [] [] over] = Wire.workLimit
-- The value table comes first on the one count: its units and the side's, refused one unit short.
def tableUnits : Nat := ((valueTableC maxWork (fan 12) [] 0).map (·.2)).getD 0
def sideA12 : List (String × Expr) := [("p", .val "a12")]
#guard tableUnits != 0 &&
  (loweredC maxWork (fan 12) (inlineTable (fan 12) keep) sideA12).map (·.2) == some (tableUnits + 16824301)
#guard (loweredC (tableUnits + 16824301) (fan 12) (inlineTable (fan 12) keep) sideA12).isSome &&
  (loweredC (tableUnits + 16824300) (fan 12) (inlineTable (fan 12) keep) sideA12).isNone
#guard (loweredC (tableUnits - 1) (fan 12) (inlineTable (fan 12) keep) []).isNone
-- A nonlinear side ends the count there: the sides after it are not lowered.
#guard (firstNonlinearC maxWork decoderTable [("a", .mul (.val "x") (.val "x")), ("b", .val "a12")] 0).map (·.1) = some (some "a")
#guard (firstNonlinearC maxWork decoderTable [("a", .lit 1), ("b", .mul (.val "x") (.val "x"))] 0).map (·.1) = some (some "b")
#guard (firstNonlinearC maxWork decoderTable [("a", .lit 1), ("b", .val "a14")] 0).map (·.1) = some none

end VE.Calc.WorkExamples
