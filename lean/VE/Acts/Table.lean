import VE.Acts.Syntax
import VE.Norms.Tree

/-! The modal × connective table (docs/spec/act-phrases.md 1.7, 6.1, 6.2; plan 2.3).

A rule's op is fixed by its predicate's role and its sign. For an op and an act tree the table gives the readings, each
the list of simple acts the rule stands for: `[]` is no reading (refused), two or more make the English ambiguous.
The table holds the distribution equations of the five deontic modals only; it is never used for `intends` or
`believes`. Its equations stay provisional until the experiment AP-7 passes (decision D3).
-/

namespace VE.Acts

/-- A simple act of a reading: an atom, or a whole join read as one act. -/
inductive Simple | atom (a : Atom) | whole (A : Act)
  deriving DecidableEq, Repr

inductive Op | must | needNot | may | mustNot | right
  deriving DecidableEq, Repr

/-- The op of a rule with `sign` on `r`; a plain predicate with sign false has none (1.7). -/
def opOf (r : VE.Norms.Regulated) (sign : Bool) : Option Op :=
  match r.role, sign with
  | .obligation, true => some .must
  | .obligation, false => some .needNot
  | .permission, true => some .may
  | .permission, false => some .mustNot
  | .plain, true => some .right
  | .plain, false => none

/-- *may* and *has the right to*. -/
def freeTable : Act → List (List Simple)
  | .one a => [[.atom a]]
  | .all false _ ps => [ps.map Simple.atom]
  | .all true true ps => [ps.map Simple.atom]
  | .all true false ps => [ps.map Simple.atom, [.whole (.all true false ps)]]
  | .any true _ _ => []
  | .any false true ps => [ps.map Simple.atom]
  | .any false false ps => [ps.map Simple.atom, [.whole (.any false false ps)]]

/-- The plan's 2.3, for the five deontic modals only. -/
def table : Op → Act → List (List Simple)
  | _, .one a => [[.atom a]]
  | .needNot, _ => []
  | .must, .all _ _ ps => [ps.map Simple.atom]
  | .must, .any nor sp ps => if nor || sp then [] else [[.whole (.any nor sp ps)]]
  | .mustNot, .any _ _ ps => [ps.map Simple.atom]
  | .mustNot, .all s sp ps => if sp then [ps.map Simple.atom] else [ps.map Simple.atom, [.whole (.all s sp ps)]]
  | .may, A => freeTable A
  | .right, A => freeTable A

/-! ### The table's equations (6.2) -/

theorem table_one (op : Op) (a : Atom) : table op (.one a) = [[.atom a]] := by
  cases op <;> rfl
theorem table_must_all (s sp : Bool) (ps : List Atom) : table .must (.all s sp ps) = [ps.map Simple.atom] := rfl
theorem table_must_any (ps : List Atom) : table .must (.any false false ps) = [[.whole (.any false false ps)]] := rfl
theorem table_must_any_refused (n sp : Bool) (ps : List Atom) (h : n = true ∨ sp = true) :
    table .must (.any n sp ps) = [] := by
  rcases h with h | h <;> subst h <;> simp [table]
theorem table_mustNot_any (n sp : Bool) (ps : List Atom) : table .mustNot (.any n sp ps) = [ps.map Simple.atom] := rfl
theorem table_mustNot_all (s : Bool) (ps : List Atom) :
    table .mustNot (.all s false ps) = [ps.map Simple.atom, [.whole (.all s false ps)]] := rfl
theorem table_mustNot_all_split (s : Bool) (ps : List Atom) :
    table .mustNot (.all s true ps) = [ps.map Simple.atom] := rfl
theorem table_free_all_own (op : Op) (hop : op = .may ∨ op = .right) (sp : Bool) (ps : List Atom) :
    table op (.all false sp ps) = [ps.map Simple.atom] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_free_all_shared (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.all true false ps) = [ps.map Simple.atom, [.whole (.all true false ps)]] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_free_all_split (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.all true true ps) = [ps.map Simple.atom] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_free_any (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.any false false ps) = [ps.map Simple.atom, [.whole (.any false false ps)]] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_free_any_split (op : Op) (hop : op = .may ∨ op = .right) (ps : List Atom) :
    table op (.any false true ps) = [ps.map Simple.atom] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_free_nor (op : Op) (hop : op = .may ∨ op = .right) (sp : Bool) (ps : List Atom) :
    table op (.any true sp ps) = [] := by
  rcases hop with h | h <;> subst h <;> rfl
theorem table_needNot (A : Act) (h : ∀ a, A ≠ .one a) : table .needNot A = [] := by
  cases A with
  | one a => exact absurd rfl (h a)
  | all => rfl
  | any => rfl

end VE.Acts
