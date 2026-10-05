import VE.WireContract.Hooks.Norms

/-!
L8 of docs/spec/wire-contract-s5.md 8.6, over the corpus: the syntax walk of
`VE.WireContract.Hooks.Norms` (`synFormula`) and `Norms.Wire.budgetFormula`, on
every guard and carve-out whose name positions hold strings, each from the
running count at which the route's decoder reads it.

Test-only: `tests/test_wire_contract_s5_lean.py` runs it with
`lake env lean --run tests/wire_contract_l8.lean` from `lean/`. It is not a
module of the package, nothing imports it, and no verdict depends on it.

Each input line is one rule: the JSON array of its guard and then its
carve-outs, the prefix the Python side selected (every name a string). The
first formula is read from count 0 and each later one from the count
`budgetFormula` returned before it, as `decodeNorm` shares one count over a
rule; a failure ends the rule, as it ends the decoder. Each output line is
`{"compared": k, "failed": b, "differ": null | text}`: the number of formulas
compared, whether the last one failed in both, and the first difference.
-/

open Lean
open VE.WireContract.Hooks.Norms (synFormula)

def describe : Except String (VE.Formula × Nat) → String
  | .ok (_, count) => s!"ok at count {count}"
  | .error text => s!"error {text}"

/-- The formulas of one rule from `count`: `(compared, failed, first difference)`. -/
def compareRule : Nat → List Json → Nat × Bool × Option String
  | _, [] => (0, false, none)
  | count, formula :: rest =>
    let walk := synFormula 64 count formula
    let budget := VE.Norms.Wire.budgetFormula 64 count formula
    match walk, budget with
    | .ok (a, n), .ok (b, m) =>
      if a == b && n == m then
        let (k, failed, differ) := compareRule m rest
        (k + 1, failed, differ)
      else (1, false, some s!"from count {count}: walk {describe walk}, budgetFormula {describe budget}")
    | .error a, .error b =>
      if a == b then (1, true, none)
      else (1, true, some s!"from count {count}: walk error {a}, budgetFormula error {b}")
    | _, _ => (1, false, some s!"from count {count}: walk {describe walk}, budgetFormula {describe budget}")

def row : Except String Json → Json
  | .ok (.arr formulas) =>
    let (compared, failed, differ) := compareRule 0 formulas.toList
    Json.mkObj [("compared", toJson compared), ("failed", toJson failed),
      ("differ", match differ with | some text => .str text | none => .null)]
  | .ok _ => Json.mkObj [("differ", .str "the line is not an array")]
  | .error text => Json.mkObj [("differ", .str s!"unreadable line: {text}")]

def main : IO UInt32 := do
  let input ← (← IO.getStdin).readToEnd
  let stdout ← IO.getStdout
  for line in input.splitOn "\n" do
    unless line.isEmpty do
      stdout.putStrLn (row (Json.parse line)).compress
  return 0
