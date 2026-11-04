import VE.Acts.Elaborate
import VE.Closure.Order
import VE.SoftNorms.Soften

/-!
# Weighing's block, strength and targets (docs/spec/weighing.md 1.1-1.3)

The decoded `weighing` block of a `weighing@0` document, the strength of a rank pair (plan D4), the chain the
paraphrase shows for a strict pair (2.3) and the open decision a condition targets. Reachability is QS-1's (`VE.Closure.Order.atLeast`); weighing has no rank closure of
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

def chainEdges : List String → List (String × String)
  | a :: b :: rest => (a, b) :: chainEdges (b :: rest)
  | _ => []

/-- A chain of declared edges from `H` down to `L`. -/
def RankChain (Wd : WeighDoc) (H L : String) (c : List String) : Prop :=
  c.head? = some H ∧ c.getLast? = some L ∧ 2 ≤ c.length ∧ ∀ e ∈ chainEdges c, e ∈ Wd.D.soft.outranks

/-- Every chain of declared edges from `a` down to `L`, with fuel (the rank graph is acyclic, soft 4.1). -/
def chainsFrom (E : List (String × String)) (L : String) : Nat → String → List (List String)
  | 0, _ => []
  | f + 1, a => (E.filter (·.1 == a)).flatMap (fun e =>
      if e.2 == L then [[a, L]] else (chainsFrom E L f e.2).map (a :: ·))

def chainLt (c d : List String) : Bool :=
  c.length < d.length || (c.length == d.length && decide (c < d))

/-- The chain the paraphrase shows (2.3): the shortest chain from `H` to `L` that contains an `always` edge, the
    least in `String` list order on ties; `none` exactly when the pair is not strict (`strictWitness_isSome`).
    Display only; at most 2^14 chains on 16 ranks. -/
def strictWitness (Wd : WeighDoc) (H L : String) : Option (List String) :=
  ((chainsFrom Wd.D.soft.outranks L Wd.D.soft.ranks.length H).filter
      (fun c => (chainEdges c).any (Wd.W.always.contains ·))).foldl
    (fun best c => match best with
      | none => some c
      | some b => if chainLt c b then some c else some b) none

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
