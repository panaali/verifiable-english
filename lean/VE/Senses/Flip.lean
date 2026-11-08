import VE.Senses.Read
import VE.Route.Budget

/-! Flip models (senses plan 2.6 step 7; spec 2.6, "Flip models"). For two candidates of one open unit: the
valuation that makes true exactly the senses the first chooses and the second does not, every other predicate
false for all arguments; if the two formulas differ in truth under it, it distinguishes the pair; else the same
with the two exchanged; else the pair is undistinguished. The model has one entity per sort and one per constant
the two formulas name; it is a table of the existing model wire form (`FlipModel`, `VE.Bridge.decodeModelData`;
`VE.Senses.Run.flipModelJson` writes it), and the budgeted evaluator (`VE.Route.Budget.evalF`) reads its
relations, so `evalF_sound`'s premise holds by construction, under one budget, `maxEvaluations`, charged across
the whole answer. A formula the evaluator has no case for, an exhausted budget or a model over `maxTuples` gives
`unknown`, never a distinction. -/

namespace VE.Senses
open VE.EnglishGrammar

/-- The core term the evaluator reads: a variable or a constant. -/
def termCore : ETerm → Option VE.Term
  | .var i => some (.var i)
  | .const c => some (.const c)
  | _ => none

/-- The core formula the evaluator reads, or none for a form it has no case for (numbers, comparisons, reach, an
atom of three or more arguments). -/
def formulaCore : EFormula → Option VE.Formula
  | .top => some .top
  | .bottom => some .bottom
  | .pred p [t] => return .unary p (← termCore t)
  | .pred p [t, u] => return .binary p (← termCore t) (← termCore u)
  | .eq t u => return .eq (← termCore t) (← termCore u)
  | .not a => return .not (← formulaCore a)
  | .and a b => return .and (← formulaCore a) (← formulaCore b)
  | .or a b => return .or (← formulaCore a) (← formulaCore b)
  | .implies a b => return .implies (← formulaCore a) (← formulaCore b)
  | .all s a => return .all s (← formulaCore a)
  | .ex s a => return .ex s (← formulaCore a)
  | _ => none

/-- The senses `c` chooses and `d` does not, as the projection's predicate ids, in the projection's order. -/
def flipOn (P : Projection) (c d : Candidate) : List String :=
  (P.map.filter fun (_, s, _) => c.choice.contains (s.word, s.index) && !d.choice.contains (s.word, s.index)).map (·.1)

/-- A flip model as a table, as the existing model wire form writes it (`VE.Bridge.decodeModelData`): each sort of
the projected environment with its entities, each constant of those sorts with its entity, each predicate with
its tuples. -/
structure FlipModel where
  domains : List (String × List String)
  constants : List (String × String)
  relations : List (String × List (List String))
  deriving DecidableEq, Repr

/-- The model the evaluator reads: the table's. -/
def FlipModel.finite (m : FlipModel) : VE.FiniteModel String :=
  { domains := fun s => (List.lookup s m.domains).getD []
    constants := fun c => List.lookup c m.constants
    relations := fun p => (List.lookup p m.relations).getD [] }

/-- Every choice of one entity from each list, in order. -/
def tuples : List (List String) → List (List String)
  | [] => [[]]
  | d :: ds => d.flatMap fun x => (tuples ds).map (x :: ·)

/-- The flip model making the senses `on` true, over the formulas `fs`: each sort of the projection has one entity
of its own (its name: no constant shares a sort's name) and the constants of that sort that `fs` name, each its
own entity, in order; another constant of the sort is the sort's entity; each predicate of `on` holds of every
tuple of its sorts' entities and every other of none. None when the senses would hold of more than `maxTuples`
tuples, the model wire form's limit. -/
def flipModelOf (P : Projection) (fs : List EFormula) (on : List String) : Option FlipModel :=
  let named := (fs.flatMap EFormula.consts).eraseDups
  let sorts := P.env.sorts.map (·.name)
  let domain (s : String) : List String :=
    (s :: (P.env.constants.filter fun k => k.sort == s && named.contains k.name).map (·.name)).mergeSort
      fun a b => decide (a ≤ b)
  let made := P.env.predicates.filter (on.contains ·.name)
  if (made.map fun p => (p.args.map fun s => (domain s).length).foldl (· * ·) 1).foldl (· + ·) 0 > VE.Limits.maxTuples
  then none
  else some { domains := sorts.map fun s => (s, domain s)
              constants := (P.env.constants.filter (sorts.contains ·.sort)).map fun k =>
                (k.name, if named.contains k.name then k.name else k.sort)
              relations := P.env.predicates.map fun p =>
                (p.name, if on.contains p.name then tuples (p.args.map domain) else []) }

/-- The flip model of a pair: the senses made true, the two formulas' values and the model, or no distinction,
or unknown. -/
inductive Flip where
  | distinguished (on : List String) (first second : Bool) (model : FlipModel)
  | undistinguished
  | unknown
  deriving DecidableEq, Repr

/-- The values of the two formulas under the model `m` from work `w`, read through its relations, and the work
after them; none when the budget runs out. -/
def flipValues (m : FlipModel) (fc fd : VE.Formula) (w : Nat) : Option ((Bool × Bool) × Nat) := do
  let M := m.finite
  let mem (p : String) (row : List String) : Bool := (M.relations p).contains row
  let (a, w) ← VE.Route.Budget.evalF mem M VE.Limits.maxEvaluations [] fc w
  let (b, w) ← VE.Route.Budget.evalF mem M VE.Limits.maxEvaluations [] fd w
  pure ((a, b), w)

/-- The values `flipValues` gives are the two formulas' truth in the model's finite view (`Formula.eval`), by
`evalF_sound`: the evaluator reads the table's relations, so its premise holds. -/
theorem flipValues_sound {m : FlipModel} {fc fd : VE.Formula} {w w' : Nat} {a b : Bool}
    (h : flipValues m fc fd w = some ((a, b), w')) : a = fc.eval m.finite [] ∧ b = fd.eval m.finite [] := by
  have hmem : ∀ p row, (m.finite.relations p).contains row = true ↔ row ∈ m.finite.relations p := by
    intro p row; simp
  unfold flipValues at h
  dsimp only at h
  cases h1 : VE.Route.Budget.evalF (fun p row => (m.finite.relations p).contains row) m.finite
      VE.Limits.maxEvaluations [] fc w with
  | none => rw [h1] at h; exact absurd h (by simp [bind, Option.bind])
  | some r1 =>
    rw [h1] at h
    cases h2 : VE.Route.Budget.evalF (fun p row => (m.finite.relations p).contains row) m.finite
        VE.Limits.maxEvaluations [] fd r1.2 with
    | none => simp only [bind, Option.bind, h2] at h; exact absurd h (by simp)
    | some r2 =>
      simp only [bind, Option.bind, h2, pure, Option.some.injEq, Prod.mk.injEq] at h
      obtain ⟨⟨rfl, rfl⟩, -⟩ := h
      exact ⟨VE.Route.Budget.evalF_sound _ _ _ hmem fc [] w r1 h1,
        VE.Route.Budget.evalF_sound _ _ _ hmem fd [] r1.2 r2 h2⟩

/-- The flip model of candidates `c` and `d` from work `w`, and the work after it; an exhausted budget leaves
none for the pairs after it. -/
def flipPair (P : Projection) (c d : Candidate) (w : Nat) : Flip × Nat :=
  match formulaCore c.formula, formulaCore d.formula with
  | some fc, some fd =>
    let fs := [c.formula, d.formula]
    match flipModelOf P fs (flipOn P c d) with
    | none => (.unknown, w)
    | some m => match flipValues m fc fd w with
      | none => (.unknown, VE.Limits.maxEvaluations)
      | some ((a, b), w) =>
        if a != b then (.distinguished (flipOn P c d) a b m, w) else
        match flipModelOf P fs (flipOn P d c) with
        | none => (.unknown, w)
        | some m => match flipValues m fc fd w with
          | none => (.unknown, VE.Limits.maxEvaluations)
          | some ((a, b), w) => if a != b then (.distinguished (flipOn P d c) a b m, w) else (.undistinguished, w)
  | _, _ => (.unknown, w)

/-- The pairs `(i, j)`, `i < j < n`, in order. -/
def candidatePairs (n : Nat) : List (Nat × Nat) :=
  (List.range n).flatMap fun i => (List.range (n - i - 1)).map fun k => (i, i + k + 1)

/-- Every unit's flip models (`flipModel`, plan 4.2): for unit `k` and its candidates `i < j`, `(k, i, j)` and the
pair's flip model, in unit order, then pair order, under one budget. -/
def flipsOf (P : Projection) (units : List SenseUnit) : List ((Nat × Nat × Nat) × Flip) :=
  let pairs := (units.mapIdx fun k u => (candidatePairs u.candidates.length).filterMap fun (i, j) => do
    pure ((k, i, j), ← u.candidates[i]?, ← u.candidates[j]?)).flatten
  (pairs.foldl (fun (acc, w) (key, c, d) => let (f, w) := flipPair P c d w; (acc ++ [(key, f)], w)) ([], 0)).1

end VE.Senses
