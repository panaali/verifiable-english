import VE.Arith.Syntax

/-! Boundedness (spec 12.2) and the admission checks of 12.1: `Formula.Bounded`, `Defs.WellFormed` and
`Formula.Scoped`, and the refusals the core decides over de Bruijn terms, in the decoder's order of spec 12.5. The
named refusals (`ShadowedVariable`, and the names in each text) are the wire's, which reads the request's names. -/

namespace VE.Arith

mutual
def Term.bnd (B : String → Bool) : Term → Bool
  | .var _ => true
  | .num _ => true
  | .add a b => Term.bnd B a && Term.bnd B b
  | .sub a b => Term.bnd B a && Term.bnd B b
  | .mul a b => Term.bnd B a && Term.bnd B b
  | .call f args => B f && Term.bndList B args
  | .countFromTo lo hi φ => Term.bnd B lo && Term.bnd B hi && Formula.bnd B φ
def Term.bndList (B : String → Bool) : List Term → Bool
  | [] => true
  | t :: ts => Term.bnd B t && Term.bndList B ts
def Formula.bnd (B : String → Bool) : Formula → Bool
  | .eq a b => Term.bnd B a && Term.bnd B b
  | .lt a b => Term.bnd B a && Term.bnd B b
  | .le a b => Term.bnd B a && Term.bnd B b
  | .dvd a b => Term.bnd B a && Term.bnd B b
  | .call p args => B p && Term.bndList B args
  | .not φ => Formula.bnd B φ
  | .and φ ψ => Formula.bnd B φ && Formula.bnd B ψ
  | .or φ ψ => Formula.bnd B φ && Formula.bnd B ψ
  | .imp φ ψ => Formula.bnd B φ && Formula.bnd B ψ
  | .allNat _ => false
  | .exNat _ => false
  | .allInt _ => false
  | .exInt _ => false
  | .allFromTo lo hi φ => Term.bnd B lo && Term.bnd B hi && Formula.bnd B φ
  | .exFromTo lo hi φ => Term.bnd B lo && Term.bnd B hi && Formula.bnd B φ
end

def Defs.boundedNames (D : Defs) : String → Bool :=
  D.foldl (fun B d => match d with
    | .fn f _ body => fun g => if g = f then Term.bnd B body else B g
    | .pred p _ body => fun q => if q = p then Formula.bnd B body else B q) (fun _ => false)

def Formula.Bounded (D : Defs) (φ : Formula) : Bool := Formula.bnd D.boundedNames φ

def Def.name : Def → String
  | .fn f _ _ | .pred f _ _ => f

def Def.arity : Def → Nat
  | .fn _ n _ | .pred _ n _ => n

def Def.isPred : Def → Bool
  | .fn .. => false
  | .pred .. => true

/-- What admission reads in a body: a variable bound outside it (its index above the body's own binders), a call
(predicate or function, name, number of arguments) and a count's condition. -/
inductive Site where
  | free (j : Nat)
  | call (pred : Bool) (name : String) (argc : Nat)
  | count (φ : Formula)

mutual
def Term.sites (k : Nat) : Term → List Site
  | .var i => if k ≤ i then [.free (i - k)] else []
  | .num _ => []
  | .add a b | .sub a b | .mul a b => Term.sites k a ++ Term.sites k b
  | .call f args => .call false f args.length :: Term.sitesList k args
  | .countFromTo lo hi φ => Term.sites k lo ++ Term.sites k hi ++ .count φ :: Formula.sites (k + 1) φ
def Term.sitesList (k : Nat) : List Term → List Site
  | [] => []
  | t :: ts => Term.sites k t ++ Term.sitesList k ts
def Formula.sites (k : Nat) : Formula → List Site
  | .eq a b | .lt a b | .le a b | .dvd a b => Term.sites k a ++ Term.sites k b
  | .call p args => .call true p args.length :: Term.sitesList k args
  | .not φ => Formula.sites k φ
  | .and φ ψ | .or φ ψ | .imp φ ψ => Formula.sites k φ ++ Formula.sites k ψ
  | .allNat φ | .exNat φ | .allInt φ | .exInt φ => Formula.sites (k + 1) φ
  | .allFromTo lo hi φ | .exFromTo lo hi φ => Term.sites k lo ++ Term.sites k hi ++ Formula.sites (k + 1) φ
end

/-- A refusal the core decides (spec 12.5), in the decoder's order. -/
inductive Refusal where
  | duplicateName (name : String)
  | unscopedVariable (j : Nat)
  | unknownDefinition (name : String)
  | recursiveDefinition (name : String)
  | arityMismatch (name : String) (arity : Nat)
  | unboundedCount
  deriving Repr, DecidableEq

def Refusal.code : Refusal → String
  | .duplicateName _ => "DuplicateName"
  | .unscopedVariable _ => "UnscopedVariable"
  | .unknownDefinition _ => "UnknownDefinition"
  | .recursiveDefinition _ => "RecursiveDefinition"
  | .arityMismatch .. => "ArityMismatch"
  | .unboundedCount => "UnboundedCount"

def Refusal.rank : Refusal → Nat
  | .duplicateName _ => 0
  | .unscopedVariable _ => 1
  | .unknownDefinition _ => 2
  | .recursiveDefinition _ => 3
  | .arityMismatch .. => 4
  | .unboundedCount => 5

/-- A site's refusal in a body with `depth` outer values, over all definitions `D`, the definitions `earlier` it may
call, and `B` for its counts' conditions (`none`: counts are not checked). -/
def Site.refusal (D earlier : Defs) (depth : Nat) (B : Option (String → Bool)) : Site → Option Refusal
  | .free j => if j < depth then none else some (.unscopedVariable j)
  | .call pred f argc =>
    if D.any (fun d => d.name == f && d.isPred == pred) then
      match earlier.find? (fun d => d.name == f && d.isPred == pred) with
      | none => some (.recursiveDefinition f)
      | some d => if d.arity = argc then none else some (.arityMismatch f d.arity)
    else some (.unknownDefinition f)
  | .count φ => match B with
    | some B => if Formula.bnd B φ then none else some .unboundedCount
    | none => none

/-- Every refusal of the definitions: a name used twice, then each body's sites. -/
def Defs.refusals (D : Defs) : List Refusal :=
  ((List.range D.length).filterMap fun k =>
      D[k]?.bind fun d => if (D.take k).any (·.name == d.name) then some (.duplicateName d.name) else none) ++
    (List.range D.length).flatMap fun k => match D[k]? with
      | some d =>
        let sites := match d with
          | .fn _ n body => Term.sites 0 body |>.map (n, ·)
          | .pred _ n body => Formula.sites 0 body |>.map (n, ·)
        sites.filterMap fun (n, s) => s.refusal D (D.take k) n (some (Defs.boundedNames (D.take k)))
      | none => []

/-- The first refusal of the lowest rank, in order: one pass, kept until a lower rank follows. -/
def firstRefusal (rs : List Refusal) : Option Refusal :=
  rs.foldl (fun best r => if best.all (r.rank < ·.rank) then some r else best) none

def Defs.WellFormed (D : Defs) : Bool := D.refusals.isEmpty

def Formula.Scoped (D : Defs) (depth : Nat) (φ : Formula) : Bool :=
  ((Formula.sites 0 φ).filterMap (Site.refusal D D depth none)).isEmpty

/-- The core's admission of definitions and statements: the first refusal in the decoder's order, or none. -/
def caseRefusal (D : Defs) (φs : List Formula) : Option Refusal :=
  firstRefusal (D.refusals ++ φs.flatMap fun φ =>
    (Formula.sites 0 φ).filterMap (Site.refusal D D 0 (some D.boundedNames)))

end VE.Arith
