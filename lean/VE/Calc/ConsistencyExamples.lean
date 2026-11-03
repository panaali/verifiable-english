import VE.Calc.Consistency

/-! ME-8's fixtures (spec 13.2, 13.3 and 13.6, plan ME-8): C-1 and R-5 (an output reading a stated value left out of
the inputs, a witness at an interval endpoint, a free value refused), V-6 witnessed by its printed values, R-10b's
unknown and undefined over counted values, the limits, V-7, V-7b and V-8 by granularity, and GRIM (S-3). -/

namespace VE.Calc.ConsistencyExamples
open VE.Calc VE.Numbers

def lt (a b : Expr) : Claim := .compare ⟨.lt, false⟩ a b
def ge (a b : Expr) : Claim := .compare ⟨.le, true⟩ a b
def a : Expr := .val "a"
def run (ds : List Decl) (ins : List (String × Printed)) (outs : List Claim) : Option ConsistencyAnswer :=
  consistencyRun Work.maxWork ds .tiesUp ins outs

/-! C-1 and R-5: a "0.4" the input, b "0.3" not one (it keeps its exact value), f free. -/
def C1 : List Decl := [⟨"a", .stated (2 / 5)⟩, ⟨"b", .stated (3 / 10)⟩, ⟨"f", .free⟩, ⟨"g", .defined (.add a (.val "f"))⟩,
  ⟨"n", .counted (Thunk.pure none) .exhausted⟩, ⟨"m", .counted (Thunk.pure none) (.ok none)⟩]
def k1 : Claim := .rounds .tiesUp (.add a (.val "b")) ⟨9, 1⟩
def k2 : Claim := lt (.add a (.val "b")) (.lit (66 / 100))
def inA : List (String × Printed) := [("a", ⟨4, 1⟩)]
-- a's box under ties up is 7/20 ≤ a < 9/20: in it at 7/20 and 2/5, not at 9/20 or 1/2.
#guard decide (InBox .tiesUp inA fun _ => 7 / 20) && decide (InBox .tiesUp inA fun _ => 2 / 5)
#guard !decide (InBox .tiesUp inA fun _ => 9 / 20) && !decide (InBox .tiesUp inA fun _ => 1 / 2)
-- The lowering keeps the input and inlines b's exact value; the printed point 2/5 is no witness of k2.
#guard (k2.inline C1 ["a"]).toOption == some (lt (.add a (.lit (3 / 10))) (.lit (66 / 100)))
#guard enclose .tiesUp inA (.add a (.lit (3 / 10))) = some (13 / 20, 3 / 4)
#guard witnessCheck .tiesUp inA [lt (.add a (.lit (3 / 10))) (.lit (66 / 100))] [("a", 2 / 5)] = false
#guard run C1 inA [k1] = some (.fails 0 [(13 / 20, 3 / 4)])
#guard run C1 inA [k2] = some (.holds [("a", 7 / 20)])
#guard run C1 inA [k2, k1] = some (.fails 1 [(13 / 20, 3 / 4)])
-- A share's complement: 1 − a lies in [11/20, 13/20], so 1 − a ≥ 0.56 is consistent, witnessed by the printed 2/5.
#guard enclose .tiesUp inA (.sub (.lit 1) a) = some (11 / 20, 13 / 20)
#guard run C1 inA [ge (.sub (.lit 1) a) (.lit (56 / 100))] = some (.holds [("a", 2 / 5)])
#guard run C1 inA [lt (.add a (.val "f")) (.lit 1)] = some (.refused (.name "f"))
#guard run C1 inA [lt (.val "g") (.lit 1)] = some (.refused (.name "f"))
#guard run C1 [("f", ⟨4, 1⟩)] [k2] = some (.refused (.input "f"))
#guard run C1 [("a", ⟨4, 1⟩), ("a", ⟨4, 1⟩)] [k2] = some (.refused (.input "a"))
-- R-10b over counted values: one whose budget ran out (unknown), one with no value (undefined).
#guard run C1 inA [lt a (.val "n")] = some (.unknown (.limit .evaluations))
#guard run C1 inA [lt a (.val "m")] = some .undefined
-- Neither refuted nor witnessed: inconclusive with one input, the point limit with twelve (2¹² + 1 > 4,096).
#guard run C1 inA [.compare ⟨.eq, false⟩ a (.lit (41 / 100))] = some (.unknown .consistencyInconclusive)
def twelve : List (String × Printed) := (List.range 12).map fun i => (s!"d{i}", ⟨4, 1⟩)
def D12 : List Decl := twelve.map fun i => ⟨i.1, .stated (2 / 5)⟩
#guard run D12 twelve [.compare ⟨.eq, false⟩ (.val "d0") (.lit (41 / 100))] = some (.unknown (.limit .witnessPoints))

/-! V-6: the twelve printed per-template differences as inputs (thousandths); the sample variance and the three
printed roots as outputs by squared bounds (spec 13.3: 1,525,425 ≤ 1,527,611 < 1,553,937 in units of 1/132,000,000).
The printed values themselves are the witness. -/
def v6 : List Int := [-100, -133, 94, -192, 21, 86, -57, 0, 61, -50, -246, -29]
def V6in : List (String × Printed) := v6.zipIdx.map fun (x, i) => (s!"d{i}", ⟨x, 3⟩)
def sumOf (f : Expr → Expr) : Expr := (List.range 12).foldl (fun e i => .add e (f (.val s!"d{i}"))) (.lit 0)
def V6 : List Decl := (V6in.map fun i => ⟨i.1, .stated i.2.value⟩) ++
  [⟨"S", .defined (sumOf id)⟩, ⟨"Q", .defined (sumOf fun x => .mul x x)⟩,
   ⟨"v", .defined (.div (.sub (.val "Q") (.div (.mul (.val "S") (.val "S")) (.lit 12))) (.lit 11))⟩]
def sq (k : Int) : Expr := .lit ((k : Rat) / 10000 * ((k : Rat) / 10000))
def se : Expr := .div (.val "v") (.lit 12)
def hw : Expr := .mul (.lit (2593 / 1000 * (2593 / 1000))) se
def V6outs : List Claim :=
  [ge (.val "v") (sq 1075), lt (.val "v") (sq 1085), ge se (sq 305), lt se (sq 315), ge hw (sq 805), lt hw (sq 815)]
#guard run V6 V6in V6outs = some (.holds (V6in.map fun i => (i.1, i.2.value)))
-- V-6r: the population reading's root, 0.1030, is no 0.108: refuted by its enclosure.
#guard (run V6 V6in [ge (.div (.mul (.val "v") (.lit 11)) (.lit 12)) (sq 1075)]).map (·matches .fails ..) = some true

/-! Limits (fail closed): no units; C-1's measured chain a(i+1) = a(i) + a(i) to a12 over the input (8,191 inlined nodes)
within the limit at `maxWork` and at its work (the enclosure, then the printed point, each charged its pass), refused
one unit short; a search over 100 inputs cut off at 1,000,000 units, each point charged its pass before it is built
further, and ended at `maxWork` by its points. -/
def chain (k : Nat) : List Decl := ⟨"a", .stated (2 / 5)⟩ :: ⟨"a0", .defined a⟩ ::
  (List.range k).map fun i => ⟨s!"a{i + 1}", .defined (.add (.val s!"a{i}") (.val s!"a{i}"))⟩
#guard consistencyRun 0 C1 .tiesUp inA [k2] = none
#guard run (chain 12) inA [lt (.val "a12") (.lit 2000)] = some (.holds [("a", 2 / 5)])
#guard consistencyRun 8716291 (chain 12) .tiesUp inA [lt (.val "a12") (.lit 2000)] = some (.holds [("a", 2 / 5)])
#guard consistencyRun 8716290 (chain 12) .tiesUp inA [lt (.val "a12") (.lit 2000)] = none
def hundred : List (String × Printed) := (List.range 100).map fun i => (s!"d{i}", ⟨4, 1⟩)
def Dhundred : List Decl := hundred.map fun i => ⟨i.1, .stated (2 / 5)⟩
def d0IsNot : Claim := .compare ⟨.eq, false⟩ (.val "d0") (.lit (41 / 100))
#guard consistencyRun 1000000 Dhundred .tiesUp hundred [d0IsNot] = none
#guard run Dhundred hundred [d0IsNot] = some (.unknown (.limit .witnessPoints))

/-! The outputs' trees hold `maxPolyTerms` nodes together, before either phase: 10,000 are searched, 10,001 are not; two
outputs that fit alone do not fit together; a fault or a refusal is found first. -/
def tree (n : Nat) : Expr :=
  if n ≤ 1 then a else if n % 2 = 0 then .pow (tree (n - 1)) 1 else .add (tree (n / 2)) (tree (n / 2))
def atCap : Claim := lt (tree 9999) (.lit 10000)
def pastCap : Claim := lt (tree 10000) (.lit 10000)
#guard outputNodes [atCap] = some 10000 && outputNodes [pastCap] = none && outputNodes [k2, k2] = some 8
#guard run C1 inA [atCap] = some (.holds [("a", 2 / 5)])
#guard run C1 inA [pastCap] = some (.unknown .consistencyInconclusive)
#guard run (chain 12) inA [lt (.val "a12") (.lit 2000), lt (.val "a12") (.lit 2000)] =
  some (.unknown .consistencyInconclusive)
#guard run C1 inA [k1, pastCap] = some (.unknown .consistencyInconclusive)
#guard run C1 inA [pastCap, lt a (.val "m")] = some .undefined
#guard run C1 inA [pastCap, lt a (.val "f")] = some (.refused (.name "f"))
-- The pass is charged by input and by node: a limit between the two passes' works tells them apart.
#guard passWork inA 8192 = 4259848 && passWork hundred 2 = 82624 && passWork [] 0 = 0
-- Both chains of the review at the runner's limit: 2⁴¹ and 2²⁴ nodes, answered without walking them.
def squares (k : Nat) : List Decl := ⟨"a", .stated (2 / 5)⟩ :: ⟨"a0", .defined a⟩ ::
  (List.range k).map fun i => ⟨s!"a{i + 1}", .defined (.mul (.val s!"a{i}") (.val s!"a{i}"))⟩
#guard run (chain 40) inA [lt (.val "a40") (.lit 1)] = some (.unknown .consistencyInconclusive)
#guard run (squares 23) inA [lt (.val "a23") (.lit 1)] = some (.unknown .consistencyInconclusive)

/-! The digit hold (`encloseC_small`): an endpoint at 4,096 digits is kept and one past them gives no enclosure, for each
operation, so nothing above a held node is computed. The squaring chain stops growing at a¹²: a¹¹'s enclosure refutes,
a¹²'s denominator 20⁴⁰⁹⁶ has 5,330 digits, so no enclosure refutes it and its points decide. -/
def big : Expr := .lit (10 ^ 4096 - 1)
def e2048 : Expr := .lit (10 ^ 2048)
def noEnclosure (e : Expr) : Bool := match encloseC Work.maxWork .tiesUp inA e 0 with
  | some (none, _) => true
  | _ => false
#guard !noEnclosure big && !noEnclosure (.mul e2048 (.lit (10 ^ 2047))) && !noEnclosure (.lit (1 / (10 ^ 4096 - 1)))
#guard [Expr.lit (10 ^ 4096), .lit (1 / 10 ^ 4096), .add big (.lit 1), .sub (.lit (-(10 ^ 4096 - 1))) (.lit 1),
  .mul e2048 e2048, .div e2048 (.lit (1 / 10 ^ 2048)), .pow e2048 2, .pow (.lit (1 / 10 ^ 2048)) 2].all noEnclosure
#guard [Expr.mul (.mul e2048 e2048) big, .add big (.mul e2048 e2048), .pow (.mul e2048 e2048) 1,
  .div (.lit 1) (.mul e2048 e2048)].all noEnclosure
-- Either endpoint past the limit is enough: x printed with no places has [x − 1/2, x + 1/2].
def edge (d : Int) : Bool := match encloseC Work.maxWork .tiesUp [("x", ⟨d, 0⟩)] (.val "x") 0 with
  | some (none, _) => true
  | _ => false
#guard edge (10 ^ 4096 / 2) && edge (-(10 ^ 4096 / 2)) && !edge (10 ^ 4096 / 2 - 1) && !edge (-(10 ^ 4096 / 2 - 1))
-- Past the hold an operation costs its visit alone: nothing above the held node is charged, so nothing is computed.
#guard (encloseC Work.maxWork .tiesUp inA (.pow (.mul e2048 e2048) 1) 0).map (·.2) =
  (encloseC Work.maxWork .tiesUp inA (.mul e2048 e2048) 0).map (·.2 + 1)
def power (k : Nat) : Expr := (List.range k).foldl (fun e _ => .mul e e) a
#guard !noEnclosure (power 11) && noEnclosure (power 12)
#guard (run (squares 11) inA [lt (.val "a11") (.lit 0)]).map (·matches .fails ..) = some true
#guard run (squares 12) inA [lt (.val "a12") (.lit 0)] = some (.unknown .consistencyInconclusive)
#guard run (squares 12) inA [lt (.val "a12") (.lit 1)] = some (.holds [("a", 2 / 5)])

/-! V-7, V-8 (granularity 1/512, nine templates) and V-7b (1/4,096, twelve), both rules: no printed p is refuted but
V-8's 0.007812 under ties up (4/512 = 0.0078125 is a tie: half to even prints 0.007812). -/
def p6 (ks : List Int) : List Printed := ks.map fun k => ⟨k, 6⟩
def V7 : List Printed := p6 [812500, 85938, 687500, 7812, 679688, 359375, 125000, 875000]
def V7b : List Printed := p6 [460938, 875488, 977, 1953, 218750, 993164]
#guard V7.map (grainRefutes 512 .tiesUp) = [false, false, false, true, false, false, false, false]
#guard V7.all fun p => !grainRefutes 512 .halfEven p
#guard (V7b.map fun p => (grainRefutes 4096 .tiesUp p, grainRefutes 4096 .halfEven p)).all (· == (false, false))
-- The multiples behind each "not refuted" (13.3), and V-8's tie.
#guard [416, 44, 352, 348, 184, 64, 448].zip (V7.eraseIdx 3) |>.all fun (k, p) => decide (RoundsTo .tiesUp p ((k : Rat) / 512))
#guard [1888, 3586, 4, 8, 896, 4068].zip V7b |>.all fun (k, p) => decide (RoundsTo .tiesUp p ((k : Rat) / 4096))
#guard decide (RoundsTo .halfEven ⟨7812, 6⟩ (4 / 512)) && !decide (RoundsTo .tiesUp ⟨7812, 6⟩ (4 / 512))

/-- V-8 as a theorem: no sign flip over nine values prints as 0.007812 under ties up. -/
theorem v8_tiesUp (d : List Rat) (h : d.length = 9) : ¬ RoundsTo .tiesUp ⟨7812, 6⟩ (signFlipP d) :=
  signFlip_grain_refutes d .tiesUp _ (by rw [h]; decide +kernel)

/-! GRIM (S-3): five integer scores cannot have the mean 3.47; 3.40 and 3.4 (17/5) are not refuted. -/
#guard grainRefutes 5 .tiesUp ⟨347, 2⟩ && !grainRefutes 5 .tiesUp ⟨340, 2⟩ && !grainRefutes 5 .tiesUp ⟨34, 1⟩

theorem grim_347 (xs : List Int) (h : xs.length = 5) :
    ¬ RoundsTo .tiesUp ⟨347, 2⟩ ((xs.map fun (x : Int) => (x : Rat)).sum / xs.length) :=
  mean_grain_refutes xs (by intro e; simp [e] at h) .tiesUp _ (by rw [h]; decide +kernel)

end VE.Calc.ConsistencyExamples
