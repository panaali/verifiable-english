import VE.Calc.Linear

/-! Fourier-Motzkin elimination with multiplier tracking (plan ME-5). Nothing here is trusted: a refutation is
replayed by `Farkas.check`, and a point is checked by evaluation (`Derive.lean`). -/

namespace VE.Calc.FM

def maxFacts : Nat := 64
def maxUnknowns : Nat := 16
def maxSteps : Nat := 10000

/-- Names in order of first appearance, each once. -/
def firstAppearance (ns : List String) : List String :=
  ns.foldl (fun acc n => if n ∈ acc then acc else acc ++ [n]) []

/-- The unknowns of a list of facts, in order of first appearance. -/
def unknowns (fs : List QFact) : List String := firstAppearance (fs.flatMap fun f => f.form.coeffs.map (·.1))

/-- A derivation's input is within the limits of spec 5: at most `maxFacts` facts, and at most `maxUnknowns` unknowns
counting `names` (the square links') with the facts'. Checked once, on the derivation's input. -/
def admits (fs : List QFact) (names : List String) : Bool :=
  fs.length ≤ maxFacts && (firstAppearance (unknowns fs ++ names)).length ≤ maxUnknowns

/-- A search step within the combinations left for the whole derivation (the state). Running out throws, so it ends
the derivation as `limit .derivationSteps` and no search can turn it into "nothing found". -/
abbrev Search := StateT Nat (Except Unit)

/-- One coefficient per unknown, in order of first appearance, zeros dropped. -/
def _root_.VE.Calc.QLin.norm (L : QLin) : QLin :=
  ⟨L.const, ((unknowns [⟨L, false⟩]).map fun n => (n, L.coeffOf n)).filter (·.2 != 0)⟩

/-- A derived fact with its weights on the input facts. -/
structure Row where
  fact : QFact
  weights : List Rat

def Row.trivial (r : Row) : Bool :=
  r.fact.form.coeffs.isEmpty && (decide (0 < r.fact.form.const) || (r.fact.form.const == 0 && !r.fact.strict))

def Row.contradiction (r : Row) : Bool :=
  r.fact.form.coeffs.isEmpty && (decide (r.fact.form.const < 0) || (r.fact.form.const == 0 && r.fact.strict))

/-- `p` has a positive and `n` a negative coefficient on `x`; the positive combination cancels `x`. -/
def Row.combine (x : String) (p n : Row) : Row :=
  let cp := p.fact.form.coeffOf x
  let cn := n.fact.form.coeffOf x
  ⟨⟨(QLin.add (p.fact.form.scale (-cn)) (n.fact.form.scale cp)).norm, p.fact.strict || n.fact.strict⟩,
    List.zipWith (fun a b => -cn * a + cp * b) p.weights n.weights⟩

/-- Eliminates `x`, charging its combinations to the budget before any is built; throws when they are more than
the budget left. -/
def eliminate (x : String) (rows : List Row) : Search (List Row) := do
  let pos := rows.filter fun r => decide (0 < r.fact.form.coeffOf x)
  let neg := rows.filter fun r => decide (r.fact.form.coeffOf x < 0)
  let zero := rows.filter fun r => r.fact.form.coeffOf x == 0
  let left ← get
  if pos.length * neg.length > left then throw ()
  set (left - pos.length * neg.length)
  pure ((zero ++ pos.flatMap fun p => neg.map (Row.combine x p)).filter (!·.trivial))

inductive Result where
  | refuted (weights : List Rat)
  | point (κ : List (String × Rat))
  deriving Repr

/-- The value of `x` meeting every row, given the later unknowns' values in `κ`: a bound itself when it meets them
all, else between the tightest bounds. -/
def pick (x : String) (rows : List Row) (κ : List (String × Rat)) : Rat :=
  let val := fun v n => if n = x then v else (κ.lookup n).getD 0
  let bounds := rows.filterMap fun r =>
    let c := r.fact.form.coeffOf x
    if c == 0 then none else some (c, -(r.fact.form.eval (val 0)) / c)
  let fits := fun v => rows.all fun r => decide (r.fact.Holds (val v))
  match (bounds.map (·.2)).find? fits, ((bounds.filter (0 < ·.1)).map (·.2)).max?,
      ((bounds.filter (·.1 < 0)).map (·.2)).min? with
  | some v, _, _ => v
  | none, some l, some h => (l + h) / 2
  | none, some l, none => l + 1
  | none, none, some h => h - 1
  | none, none, none => 0

/-- Back-substitution through the stages, last eliminated unknown first. -/
def backSubstitute : List (String × List Row) → List (String × Rat) → List (String × Rat)
  | [], κ => κ
  | (x, rows) :: rest, κ => backSubstitute rest ((x, pick x rows κ) :: κ)

/-- Eliminates `xs` in order; the stages are recorded, latest first. -/
def run : List String → List Row → List (String × List Row) → Search (List Row × List (String × List Row))
  | [], rows, stages => pure (rows, stages)
  | x :: xs, rows, stages => do run xs (← eliminate x rows) ((x, rows) :: stages)

def inputRows (fs : List QFact) : List Row :=
  (List.range fs.length).zip fs |>.map fun (i, f) =>
    ⟨⟨f.form.norm, f.strict⟩, (List.range fs.length).map fun j => if i = j then 1 else 0⟩

/-- Searches a refutation of `fs`, or a point satisfying all of them. -/
def search (fs : List QFact) : Search Result := do
  let (rows, stages) ← run (unknowns fs) (inputRows fs) []
  match rows.find? Row.contradiction with
  | some r => pure (.refuted r.weights)
  | none => pure (.point (backSubstitute stages []))

/-- The least upper bound on `x` that the facts imply, with its strictness: every other unknown eliminated. -/
def upperBound (fs : List QFact) (x : String) : Search (Option (Rat × Bool)) := do
  let (rows, _) ← run ((unknowns fs).filter (· != x)) (inputRows fs) []
  let ups := rows.filterMap fun r =>
    let c := r.fact.form.coeffOf x
    if decide (c < 0) && r.fact.form.coeffs.all (·.1 == x) then some (r.fact.form.const / -c, r.fact.strict)
    else none
  pure <| ups.foldl (fun best u => match best with
    | none => some u
    | some b => if u.1 < b.1 || (u.1 == b.1 && u.2) then some u else some b) none

end VE.Calc.FM
