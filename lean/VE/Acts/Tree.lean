/-! The act trees: the meaning of a derivation of an act phrase (docs/spec/act-phrases.md 1.5, 5.4).

A `Filler` joined by a word that is not a split marker's stays one filler of one atom; `Act.all` and `Act.any` are
joins of whole atoms, with one join level. AP-2's meaning builds these trees; AP-3's table reads them.
-/

namespace VE.Acts

inductive Join | and | or | nor
  deriving DecidableEq, Repr
inductive Part | slot (i : Nat) | fixed (i : Nat) | words (ws : List String)
  deriving DecidableEq, Repr
inductive Filler | one (p : Part) | joined (j : Join) (ps : List Part)
  deriving DecidableEq, Repr
inductive Modifier | adv (w : String) | prep (m : String) (p : Part)
  deriving DecidableEq, Repr

/-- A simple act: *to* and *be* as read, the head, its arguments (marker, filler) and its modifiers. -/
structure Atom where
  toWord : Bool
  beWord : Bool
  head : List String
  args : List (String × Filler)
  mods : List Modifier
  deriving DecidableEq, Repr

/-- `all shared split`: joined by *and*, `shared` when the items share one *to*; `any nor split`: joined by *or*, or
by *nor* when `nor`; `split` when the join is a split marker's (1.5). -/
inductive Act
  | one (a : Atom)
  | all (shared split : Bool) (parts : List Atom)
  | any (nor split : Bool) (parts : List Atom)
  deriving DecidableEq, Repr

end VE.Acts
