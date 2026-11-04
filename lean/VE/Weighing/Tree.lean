import VE.Acts.Elaborate
import VE.Closure.Order
import VE.SoftNorms.Soften

/-!
# Weighing's block, strength and targets (docs/spec/weighing.md 1.1-1.3)

The decoded `weighing` block of a `weighing@0` document, the strength of a rank pair (plan D4) and the open
decision a condition targets. Reachability is QS-1's (`VE.Closure.Order.atLeast`); weighing has no rank closure of
its own. The premises and checks are `Conditions.lean`'s.
-/

namespace VE.Weighing
open VE.Norms VE.SoftNorms

inductive CondKind | necessary | sufficient
  deriving DecidableEq, Repr

def CondKind.label : CondKind → String
  | .necessary => "necessary"
  | .sufficient => "sufficient"

/-- The open decision a condition constrains (soft 1.3). -/
inductive Target
  | outweighs (act lower higher : String)
  | off (rule party : String)
  deriving DecidableEq, Repr

structure CondDecl where
  target : Target
  kind : CondKind
  condition : VE.Formula    -- context (targetSorts target).reverse; base predicates of E only; quantifier-free;
                            -- decoded through the chain's guard decoder (3.1)
  deriving DecidableEq, Repr

structure FactorDecl where
  target : Target
  factors : List String
  deriving DecidableEq, Repr

structure GrantDecl where
  rule : String
  party : String
  grantor : String
  predicate : String        -- a base predicate with instruction_of = grantor, over the rule's argument sorts
  deriving DecidableEq, Repr

/-- The decoded block. Only `always` edges are on the wire: "generally outranks" is an input synonym of a plain
    "outranks" (plan D5). -/
structure WeighEnv where
  always : List (String × String)
  conditions : List CondDecl
  factors : List FactorDecl
  grants : List GrantDecl
  deriving DecidableEq, Repr

def WeighEnv.empty : WeighEnv := ⟨[], [], [], []⟩

/-- A soft document with its block, and AP's split map (empty unless `acts@0` split a rule or an act). -/
structure WeighDoc where
  D : SoftDoc
  W : WeighEnv
  split : VE.Acts.SplitMap

/-- Soft's ranks and declared edges as QS-1's order (`atLeast := reachEval .star`). -/
def rankOrder (Wd : WeighDoc) : VE.Closure.Order String := ⟨Wd.D.soft.ranks, Wd.D.soft.outranks⟩

/-- `(H, L)` is strict: some `always` edge `(a, b)` has `H` at or above `a` and `b` at or above `L`. -/
def strictPair (Wd : WeighDoc) (H L : String) : Bool :=
  Wd.W.always.any (fun e => (rankOrder Wd).atLeast H e.1 && (rankOrder Wd).atLeast e.2 L)

def nodeNamed (D : SoftDoc) (n : String) : Option SoftNode := D.T.nodes.find? (·.name == n)

def ruleSorts (Wd : WeighDoc) (n : String) : List String :=
  match nodeNamed Wd.D n with
  | some N => sortsOf Wd.D N.pred
  | none => []

def targetSorts (Wd : WeighDoc) : Target → List String
  | .outweighs a _ _ => actSortsOf Wd.D a
  | .off n _ => ruleSorts Wd n

def targetF (Wd : WeighDoc) : Target → VE.Formula
  | .outweighs a L H => outweighsF Wd.D a L H
  | .off n π => match nodeNamed Wd.D n with
    | some N => atom (offName N π) (sortsOf Wd.D N.pred)
    | none => .bottom

/-- The decision exists in `E′` (soft 1.3): an `outweighs` triple of a comparable colliding pair under the holistic
    flag, or a switch the rule declares. -/
def targetExists (Wd : WeighDoc) : Target → Bool
  | .outweighs a L H => (outweighsTriples Wd.D).contains (a, L, H)
  | .off n π => match nodeNamed Wd.D n with
    | some N => N.alterable.contains π
    | none => false

def renderTarget : Target → String
  | .outweighs a L H => s!"outweighs {a}, {L}, {H}"
  | .off n π => s!"off rule {n}, {π}"

end VE.Weighing
