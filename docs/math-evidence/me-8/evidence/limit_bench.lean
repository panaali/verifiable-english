import VE.Calc.ConsistencyExamples

/-! Native time of `consistencyRun` at `Work.maxWork` on the request shapes that stress each kind of work (F1 of the
me-8 review). Not a test: run by hand as a temporary `lean_exe`, its output saved in `limit-times.txt`. -/

open VE.Calc VE.Calc.ConsistencyExamples VE.Numbers

def tag : Option ConsistencyAnswer → String
  | none => "limit 10"
  | some (.refused _) => "refused"
  | some (.holds _) => "holds"
  | some (.fails ..) => "fails"
  | some .undefined => "undefined"
  | some (.unknown .consistencyInconclusive) => "unknown: inconclusive"
  | some (.unknown (.limit .witnessPoints)) => "unknown: witness points"
  | some (.unknown _) => "unknown: other"

def timed (name : String) (run : Unit → Option ConsistencyAnswer) : IO Unit := do
  let t0 ← IO.monoMsNow
  let text ← IO.lazyPure fun _ => tag (run ())
  let t1 ← IO.monoMsNow
  IO.println s!"{name}\t{text}\t{t1 - t0} ms"
  (← IO.getStdout).flush

/-- Half to even with an even digit: both endpoints round to the printed value, so every point passes the input check and
is evaluated (under ties up the upper endpoint is outside, and only two points would reach the outputs). -/
def inputsOf (n : Nat) : List (String × Printed) := (List.range n).map fun i => (s!"d{i}", ⟨4, 1⟩)
def declsOf (ins : List (String × Printed)) : List Decl := ins.map fun i => ⟨i.1, .stated i.2.value⟩
/-- `count` reads of the first-declared input, the deepest in a point's table: `2 * count` nodes. -/
def readsOf (count : Nat) : Expr := (List.range (count - 1)).foldl (fun e _ => .add e (.val "d0")) (.val "d0")
def never (e : Expr) (x : Rat) : Claim := .compare ⟨.eq, false⟩ e (.lit x)

/-- `n` inputs and `count` reads, no point holding and no enclosure missing: every point is tried, or the limit ends it. -/
def reads (L n count : Nat) : Option ConsistencyAnswer :=
  let ins := inputsOf n
  consistencyRun L (declsOf ins) .halfEven ins [never (readsOf count) ((count : Rat) * (41 / 100))]

/-- 63rd powers of a sum with a 61-digit denominator: values just within the digit limit, the largest a point computes
and pays for by size. Every output but the last holds, so each point computes them all. -/
def p32 : Rat := 1 / 10000000000000000000000000000057
def q32 : Rat := 1 / 10000000000000000000000000000099
def fits : Expr := .pow (.add (.val "d0") (.add (.lit p32) (.lit q32))) 63
def bigFits (L n count : Nat) : Option ConsistencyAnswer :=
  let ins := inputsOf n
  consistencyRun L (declsOf ins) .halfEven ins
    (List.replicate count (lt fits (.lit 1)) ++ [never (.val "d0") (41 / 100)])

/-- A tree as deep as the node limit lets it be: 9,999 powers over a read (one stack frame group a level). -/
def deep (L n : Nat) : Option ConsistencyAnswer :=
  let ins := inputsOf n
  let e := (List.range 9998).foldl (fun e _ => Expr.pow e 1) (.val "d0")
  consistencyRun L (declsOf ins) .halfEven ins [never e (41 / 100)]

/-- The limit is read at run time (no argument: `Work.maxWork`), so no run is a closed term computed at start-up. -/
def main (args : List String) : IO Unit := do
  let L := (args.head?.bind String.toNat?).getD Work.maxWork
  timed "add chain, 40 levels" fun _ => consistencyRun L (chain 40) .tiesUp inA [lt (.val "a40") (.lit 1)]
  timed "mul chain, 23 levels" fun _ => consistencyRun L (squares 23) .tiesUp inA [lt (.val "a23") (.lit 1)]
  timed "mul chain, 12 levels (8,191 nodes, held)" fun _ =>
    consistencyRun L (squares 12) .tiesUp inA [lt (.val "a12") (.lit 0)]
  timed "add chain, 12 levels (8,191 nodes)" fun _ =>
    consistencyRun L (chain 12) .tiesUp inA [lt (.val "a12") (.lit 0)]
  timed "512 inputs, no reads" fun _ => reads L 512 1
  timed "1,447 inputs, no reads (past the wire's 512)" fun _ => reads L 1447 1
  timed "200 inputs, 5,000 reads (every point, near the limit)" fun _ => reads L 200 4999
  timed "512 inputs, 5,000 reads (the limit ends it)" fun _ => reads L 512 4999
  timed "12 inputs, 5,000 reads" fun _ => reads L 12 4999
  timed "12 inputs, 1,428 outputs of near-limit powers" fun _ => bigFits L 12 1428
  timed "12 inputs, a tree 9,999 levels deep" fun _ => deep L 12
