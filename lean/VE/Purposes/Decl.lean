import VE.Route.Admission

/-! The `purposes@0` link declarations (purpose-explanation plan 2.1, spec 1.1). A link joins the parts that
carry a reason or purpose, its target and its marker words; it has no formula and adds no premise. -/

namespace VE.Purposes

/-- The two W2 relations a link carries; `prevents` is events-time-causation's (plan D8). -/
inductive Relation where
  | because
  | inOrderTo
  deriving DecidableEq, Repr

def Relation.wire : Relation → String
  | .because => "because"
  | .inOrderTo => "in order to"

def Relation.ofWire? : String → Option Relation
  | "because" => some .because
  | "in order to" => some .inOrderTo
  | _ => none

theorem Relation.wire_mem (r : Relation) : r.wire ∈ VE.Route.Admission.relations := by
  cases r <;> decide

theorem Relation.ofWire_wire (r : Relation) : Relation.ofWire? r.wire = some r := by
  cases r <;> rfl

theorem Relation.wire_ne_prevents (r : Relation) : r.wire ≠ "prevents" := by
  cases r <;> decide

inductive Polarity where
  | affirmed      -- "because", "in order to", "this is why"
  | denied        -- "this isn't because", "not because"
  deriving DecidableEq, Repr

/-- What the text says about other reasons for the same target. The constructor is `partly` because draft 1's
    name is a Lean keyword (plan 2.1). -/
inductive Share where
  | plain         -- says nothing about other reasons
  | sole          -- "only because", "solely because", "simply because", "just because"
  | partly        -- "partly because", "in part because"
  | notSole       -- "not merely because", "not only because", "not just because"
  deriving DecidableEq, Repr

/-- What one side of a link names: a part of the checked document, or (PE-4) a discourse mention. -/
inductive Ref where
  | part (id : String)
  | mention (id : String)
  deriving DecidableEq, Repr

structure Link where
  id       : String
  relation : Relation
  polarity : Polarity
  share    : Share
  reason   : List Ref        -- for `inOrderTo`, the purpose; in source order
  target   : List Ref        -- the rule, claim, ranking or device the reason is given for
  marker   : String          -- the part whose bytes are the link words
  deriving DecidableEq, Repr

structure Block where
  links : List Link
  deriving DecidableEq, Repr

def maxLinks : Nat := 256

end VE.Purposes
