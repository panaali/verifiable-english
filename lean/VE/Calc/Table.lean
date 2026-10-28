import VE.Calc.Decls
import VE.Numbers.Decimal

/-! Tables, filters and aggregates (spec 4.1 and 4.2, plan 3.3, ME-4). A filter has negated atoms, each selecting only a
cell of its type, and no general negation (statement review J9). -/

namespace VE.Calc
open VE.Numbers

inductive Cell where
  | num (q : Rat) | text (s : String) | bool (b : Bool) | absent
  deriving Repr, DecidableEq

structure Table where
  columns : List String
  rows : List (List Cell)

def Table.cell (T : Table) (row : List Cell) (col : String) : Cell :=
  match T.columns.idxOf? col with
  | some i => row.getD i .absent
  | none => .absent

inductive Filter where
  | all
  | isText (col v : String)
  | isNotText (col v : String)
  | equals (col : String) (q : Rat)
  | notEquals (col : String) (q : Rat)
  | isTrue (col : String)
  | isFalse (col : String)
  | and (f g : Filter)
  | or (f g : Filter)

/-- The meaning of a filter. -/
def Filter.Selects (T : Table) : Filter → List Cell → Prop
  | .all, _ => True
  | .isText c v, r => T.cell r c = .text v
  | .isNotText c v, r => ∃ s, T.cell r c = .text s ∧ s ≠ v
  | .equals c q, r => T.cell r c = .num q
  | .notEquals c q, r => ∃ x, T.cell r c = .num x ∧ x ≠ q
  | .isTrue c, r => T.cell r c = .bool true
  | .isFalse c, r => T.cell r c = .bool false
  | .and f g, r => f.Selects T r ∧ g.Selects T r
  | .or f g, r => f.Selects T r ∨ g.Selects T r

/-- The executable filter. -/
def Filter.sel (T : Table) : Filter → List Cell → Bool
  | .all, _ => true
  | .isText c v, r => T.cell r c == .text v
  | .isNotText c v, r => match T.cell r c with
    | .text s => s != v
    | _ => false
  | .equals c q, r => T.cell r c == .num q
  | .notEquals c q, r => match T.cell r c with
    | .num x => x != q
    | _ => false
  | .isTrue c, r => T.cell r c == .bool true
  | .isFalse c, r => T.cell r c == .bool false
  | .and f g, r => f.sel T r && g.sel T r
  | .or f g, r => f.sel T r || g.sel T r

def Table.select (T : Table) (f : Filter) : List (List Cell) := T.rows.filter (f.sel T)

theorem Filter.sel_iff (T : Table) (f : Filter) (row : List Cell) : f.sel T row = true ↔ f.Selects T row := by
  induction f with
  | and f g ihf ihg => simp [Filter.sel, Filter.Selects, ihf, ihg]
  | or f g ihf ihg => simp [Filter.sel, Filter.Selects, ihf, ihg]
  | isNotText c v => cases h : T.cell row c <;> simp [Filter.sel, Filter.Selects, h]
  | notEquals c q => cases h : T.cell row c <;> simp [Filter.sel, Filter.Selects, h]
  | _ => simp [Filter.sel, Filter.Selects]

theorem Table.select_iff (T : Table) (f : Filter) (row : List Cell) :
    row ∈ T.select f ↔ row ∈ T.rows ∧ f.Selects T row := by
  simp [Table.select, List.mem_filter, Filter.sel_iff]

theorem Table.select_sublist (T : Table) (f : Filter) : (T.select f).Sublist T.rows :=
  List.filter_sublist

/-- A Boolean atom and its negation never select one row, and neither selects a row whose cell is not a Boolean. -/
theorem Filter.bool_atoms (T : Table) (c : String) (row : List Cell) :
    ¬ ((Filter.isTrue c).Selects T row ∧ (Filter.isFalse c).Selects T row) ∧
      ((∀ b, T.cell row c ≠ .bool b) →
        ¬ (Filter.isTrue c).Selects T row ∧ ¬ (Filter.isFalse c).Selects T row) := by
  simp only [Filter.Selects]
  refine ⟨fun ⟨h1, h2⟩ => by simp [h1] at h2, fun h => ⟨h true, h false⟩⟩

/-- A negated text or number atom selects only a cell of its type. -/
theorem Filter.negated_typed (T : Table) (c v : String) (q : Rat) (row : List Cell) :
    ((Filter.isNotText c v).Selects T row → ∃ s, T.cell row c = .text s) ∧
      ((Filter.notEquals c q).Selects T row → ∃ x, T.cell row c = .num x) := by
  simp only [Filter.Selects]
  exact ⟨fun ⟨s, h, _⟩ => ⟨s, h⟩, fun ⟨x, h, _⟩ => ⟨x, h⟩⟩

/-- The numbers of a column over the selected rows, in table order; none if a selected cell there is not a number. -/
def Table.numbers (T : Table) (f : Filter) (col : String) : Option (List Rat) :=
  (T.select f).mapM fun r => match T.cell r col with
    | .num q => some q
    | _ => none

def mean? (xs : List Rat) : Option Rat := if xs = [] then none else some (xs.sum / xs.length)

inductive Agg where
  | count | sum (col : String) | mean (col : String) | min (col : String) | max (col : String)

def Agg.run (T : Table) (f : Filter) : Agg → Option Rat
  | .count => some ((T.select f).length : Rat)
  | .sum c => (T.numbers f c).map List.sum
  | .mean c => (T.numbers f c).bind mean?
  | .min c => (T.numbers f c).bind List.min?
  | .max c => (T.numbers f c).bind List.max?

theorem Agg.run_count (T : Table) (f : Filter) : Agg.run T f .count = some ((T.select f).length : Rat) := rfl

theorem Agg.run_sum (T : Table) (f : Filter) (col : String) :
    Agg.run T f (.sum col) = (T.numbers f col).map List.sum := rfl

theorem Agg.run_mean (T : Table) (f : Filter) (col : String) (q : Rat) :
    Agg.run T f (.mean col) = some q ↔ ∃ xs, T.numbers f col = some xs ∧ xs ≠ [] ∧ q = xs.sum / xs.length := by
  simp only [Agg.run, Option.bind_eq_some_iff, mean?]
  constructor
  · rintro ⟨xs, hx, h⟩
    by_cases he : xs = [] <;> simp [he] at h
    exact ⟨xs, hx, he, h.symm⟩
  · rintro ⟨xs, hx, he, hq⟩
    exact ⟨xs, hx, by simp [he, hq]⟩

/-- Over an empty selection, count and sum are 0; mean, minimum and maximum are undefined. -/
theorem Agg.run_empty (T : Table) (f : Filter) (h : T.select f = []) (col : String) :
    Agg.run T f .count = some 0 ∧ Agg.run T f (.sum col) = some 0 ∧ Agg.run T f (.mean col) = none ∧
      Agg.run T f (.min col) = none ∧ Agg.run T f (.max col) = none := by
  simp [Agg.run, Table.numbers, h, mean?]

/-- A selected cell that is not a number makes sum, mean, minimum and maximum undefined. -/
theorem Agg.run_nonnumber (T : Table) (f : Filter) (col : String) (row : List Cell) (hr : row ∈ T.select f)
    (hc : ∀ q, T.cell row col ≠ .num q) :
    Agg.run T f (.sum col) = none ∧ Agg.run T f (.mean col) = none ∧ Agg.run T f (.min col) = none ∧
      Agg.run T f (.max col) = none := by
  have hn : T.numbers f col = none := by
    unfold Table.numbers
    generalize T.select f = rows at hr
    induction rows with
    | nil => simp at hr
    | cons y rows ih =>
        rw [List.mapM_cons]
        rcases List.mem_cons.mp hr with rfl | hr
        · cases h : T.cell row col <;> simp_all
        · cases (match T.cell y col with | .num q => some q | _ => none) <;> simp [ih hr]
  simp [Agg.run, hn]

/-- One filter over one row under a budget of one unit per node visit (`and` and `or` stop at a decisive left side):
the selection and the units left, or none when the budget runs out. -/
def Filter.selB (T : Table) (r : List Cell) : Filter → Nat → Option (Bool × Nat)
  | _, 0 => none
  | .and f g, n + 1 => (f.selB T r n).bind fun (b, m) => if b then g.selB T r m else some (false, m)
  | .or f g, n + 1 => (f.selB T r n).bind fun (b, m) => if b then some (true, m) else g.selB T r m
  | f, n + 1 => some (f.sel T r, n)

def Table.selectB (T : Table) (f : Filter) : List (List Cell) → Nat → Option (List (List Cell))
  | [], _ => some []
  | r :: rs, n => (f.selB T r n).bind fun (b, m) =>
      (T.selectB f rs m).map fun rest => if b then r :: rest else rest

/-- Aggregation under a budget of one unit per (row, filter node) visit; `none` is UNKNOWN, and a budget of 0 allows
nothing. -/
def Agg.runB (limit : Nat) (T : Table) (f : Filter) (a : Agg) : Option (Option Rat) :=
  if limit = 0 then none
  else (T.selectB f T.rows limit).map fun rows => Agg.run ⟨T.columns, rows⟩ .all a

theorem Filter.selB_sound (T : Table) (r : List Cell) (f : Filter) (n : Nat) (b : Bool) (m : Nat)
    (h : f.selB T r n = some (b, m)) : b = f.sel T r := by
  induction f generalizing n b m with
  | and f g ihf ihg =>
      cases n with
      | zero => simp [Filter.selB] at h
      | succ n =>
          simp only [Filter.selB, Option.bind_eq_some_iff] at h
          obtain ⟨⟨b1, m1⟩, h1, h2⟩ := h
          have := ihf n b1 m1 h1
          cases b1 <;> simp at h2
          · simp [Filter.sel, ← this, h2.1]
          · simp [Filter.sel, ← this, ihg _ _ _ h2]
  | or f g ihf ihg =>
      cases n with
      | zero => simp [Filter.selB] at h
      | succ n =>
          simp only [Filter.selB, Option.bind_eq_some_iff] at h
          obtain ⟨⟨b1, m1⟩, h1, h2⟩ := h
          have := ihf n b1 m1 h1
          cases b1 <;> simp at h2
          · simp [Filter.sel, ← this, ihg _ _ _ h2]
          · simp [Filter.sel, ← this, h2.1]
  | _ => cases n <;> simp_all [Filter.selB]

theorem Table.selectB_sound (T : Table) (f : Filter) (rs : List (List Cell)) (n : Nat) (out : List (List Cell))
    (h : T.selectB f rs n = some out) : out = rs.filter (f.sel T) := by
  induction rs generalizing n out with
  | nil => simp_all [Table.selectB]
  | cons r rs ih =>
      simp only [Table.selectB, Option.bind_eq_some_iff, Option.map_eq_some_iff] at h
      obtain ⟨⟨b, m⟩, h1, rest, h2, rfl⟩ := h
      rw [List.filter_cons, ← Filter.selB_sound T r f n b m h1, ih m rest h2]

theorem Agg.runB_sound (limit : Nat) (T : Table) (f : Filter) (a : Agg) (v : Option Rat)
    (h : Agg.runB limit T f a = some v) : v = Agg.run T f a := by
  unfold Agg.runB at h
  split at h
  · cases h
  · simp only [Option.map_eq_some_iff] at h
    obtain ⟨rows, hr, rfl⟩ := h
    have hs : rows = T.select f := Table.selectB_sound T f T.rows limit rows hr
    have hc : Table.cell ⟨T.columns, rows⟩ = T.cell := rfl
    have hall : Table.select ⟨T.columns, rows⟩ .all = T.select f := by simp [Table.select, Filter.sel, hs]
    cases a <;> simp [Agg.run, Table.numbers, hall, hc]

/-! Declared column types, shared by the CSV and JSON-lines decoders (spec 4.1). `readCell` reads a field as written:
empty is absent; a number column reads an exact decimal, a `bool` column `true` or `false`; any other text is kept as
text. -/

inductive ColType where
  | text | number | bool
  deriving Repr, DecidableEq

def readCell : ColType → String → Cell
  | _, "" => .absent
  | .number, s => match VE.Time.parseDecimal s with
    | .ok d => .num (decValue d)
    | .error _ => .text s
  | .bool, "true" => .bool true
  | .bool, "false" => .bool false
  | _, s => .text s

end VE.Calc
