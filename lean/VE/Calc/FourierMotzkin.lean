import VE.Calc.Linear

/-! Fourier-Motzkin elimination with multiplier tracking (plan ME-5). Nothing here is trusted: a refutation is
replayed by `Farkas.check`, and a point is checked by evaluation (`Derive.lean`). -/

namespace VE.Calc.FM

def maxFacts : Nat := 64
def maxUnknowns : Nat := 16
def maxSteps : Nat := 10000

/-- The unknowns of a list of facts, in order of first appearance. -/
def unknowns (fs : List QFact) : List String :=
  (fs.flatMap fun f => f.form.coeffs.map (·.1)).foldl (fun acc n => if n ∈ acc then acc else acc ++ [n]) []

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

/-- Eliminates `x` with the number of combinations it takes, or none when they are more than `budget`; they are
counted before any is built. -/
def eliminate (x : String) (rows : List Row) (budget : Nat) : Option (List Row × Nat) :=
  let pos := rows.filter fun r => decide (0 < r.fact.form.coeffOf x)
  let neg := rows.filter fun r => decide (r.fact.form.coeffOf x < 0)
  let zero := rows.filter fun r => r.fact.form.coeffOf x == 0
  if pos.length * neg.length > budget then none else
  some ((zero ++ pos.flatMap fun p => neg.map (Row.combine x p)).filter (!·.trivial), pos.length * neg.length)

inductive Result where
  | refuted (weights : List Rat)
  | point (κ : List (String × Rat))
  | exhausted
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

/-- Eliminates `xs` in order within `budget` combinations; the stages are recorded, latest first. -/
def run : List String → List Row → List (String × List Row) → Nat → Option (List Row × List (String × List Row))
  | [], rows, stages, _ => some (rows, stages)
  | x :: xs, rows, stages, budget =>
      match eliminate x rows budget with
      | none => none
      | some (next, used) => run xs next ((x, rows) :: stages) (budget - used)

def inputRows (fs : List QFact) : List Row :=
  (List.range fs.length).zip fs |>.map fun (i, f) =>
    ⟨⟨f.form.norm, f.strict⟩, (List.range fs.length).map fun j => if i = j then 1 else 0⟩

/-- Searches a refutation of `fs`, or a point satisfying all of them. -/
def search (fs : List QFact) : Result :=
  let xs := unknowns fs
  if fs.length > maxFacts || xs.length > maxUnknowns then .exhausted else
  match run xs (inputRows fs) [] maxSteps with
  | none => .exhausted
  | some (rows, stages) =>
    match rows.find? Row.contradiction with
    | some r => .refuted r.weights
    | none => .point (backSubstitute stages [])

/-- The least upper bound on `x` that the facts imply, with its strictness: every other unknown eliminated. -/
def upperBound (fs : List QFact) (x : String) : Option (Rat × Bool) :=
  let xs := (unknowns fs).filter (· != x)
  match run xs (inputRows fs) [] maxSteps with
  | none => none
  | some (rows, _) =>
    let ups := rows.filterMap fun r =>
      let c := r.fact.form.coeffOf x
      if decide (c < 0) && r.fact.form.coeffs.all (·.1 == x) then some (r.fact.form.const / -c, r.fact.strict)
      else none
    ups.foldl (fun best u => match best with
      | none => some u
      | some b => if u.1 < b.1 || (u.1 == b.1 && u.2) then some u else some b) none

end VE.Calc.FM
