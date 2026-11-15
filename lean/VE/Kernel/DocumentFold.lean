import VE.Kernel.Carry

/-! The document mode's fold (kb-2a-b; the architect seat's design for kb-2a, section 2.3): each unit's status from
the request's unit table and the kernel's rows, nothing else. A status is not a verdict: CHECKED says the unit's core
statements were admitted by the checker. -/
namespace VE.Kernel.DocumentFold
open Lean

/-- One core statement of a unit, in some choice: the judgment terms it reads (directly or through a definition). -/
structure Stmt where
  reads : List String

/-- A unit of the request's table: its meaning class (`specified`, `open`, `unformalised`, or none), its core
statements over every choice (the shell keeps a statement of a unit that does not assert its content only where it
reads a judgment term), whether its active reading set is authored with every reading asserted (none: no
active set), and whether the rights route reads it as open. -/
structure UnitRow where
  id : String
  meaning : String
  statements : List Stmt
  set : Option Bool
  rightsOpen : Bool

/-- A unit's status (`Service.Document.UnitStatus` renders it). It is not a verdict: CHECKED says the unit's core
statements were admitted by the checker. -/
inductive Status | checked | opened | labelled | unformalised
  deriving DecidableEq, Repr

def Row.ok (r : Row) : Bool := match r.result with
  | .ok _ => true
  | .error _ => false

/-- The three conditions of 2.3 that make a unit OPEN, read on its core statements. -/
def opens (u : UnitRow) : Bool := u.statements.any (!·.reads.isEmpty) || u.set == some false || u.rightsOpen

/-- A status that no core statement decides, as today (`Loader.w2Status` without content). -/
def baseless (meaning : String) : Status :=
  if meaning == "open" then .opened else if meaning == "unformalised" then .unformalised else .labelled

def status (u : UnitRow) (rows : List Row) : Status :=
  if opens u then .opened
  else if u.statements.isEmpty then baseless u.meaning
  else if rows.all Row.ok then .checked else .opened

def statuses (table : List UnitRow) (rows : List Row) : List (String × Status) :=
  table.map fun u => (u.id, status u rows)

/-- The answer: the shell's view over the statuses, and the kernel's rows verbatim (`carry`). -/
def fold (view : List (String × Status) → Json) (table : List UnitRow) (request : Json) (rows : List Row) : Json :=
  carry (fun _ => view (statuses table rows)) request rows

theorem fold_checked_iff (u : UnitRow) (rows : List Row) :
    status u rows = .checked ↔
      u.statements ≠ [] ∧ opens u = false ∧ ∀ r ∈ rows, r.result.isOk = true := by
  have hb : ∀ m, baseless m ≠ .checked := fun m => by
    unfold baseless; split
    · decide
    · split <;> decide
  have hok : ∀ r : Row, Row.ok r = r.result.isOk := fun r => by
    cases h : r.result <;> simp [Row.ok, h, Except.isOk, Except.toBool]
  unfold status
  by_cases ho : opens u <;> by_cases hs : u.statements = [] <;>
    by_cases hr : rows.all Row.ok <;> simp_all [List.all_eq_true]

/-- The answer reads the rows only: in the form `shell_provenance` gives it, a shell answer with this fold is the fold
of rows the kernel itself gave. -/
theorem fold_reads_rows_only (p : Path) (elaborate : Json → Except String (List Json))
    (view : List (String × Status) → Json) (table : List UnitRow) (request answer : Json)
    (h : shell p elaborate (fold view table) request = .ok answer) :
    ∃ rows : List Row, (∀ r ∈ rows, p.Ran r) ∧ answer = fold view table request rows :=
  shell_provenance p elaborate (fold view table) request answer h

end VE.Kernel.DocumentFold
