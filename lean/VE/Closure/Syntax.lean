import VE.Closure.Paths
import VE.Core.Syntax

namespace VE.Closure
universe u

inductive Formula where
  | top
  | bottom
  | unary (predicate : String) (term : Term)
  | binary (predicate : String) (left right : Term)
  | eq (left right : Term)
  | not (body : Formula)
  | and (left right : Formula)
  | or (left right : Formula)
  | implies (left right : Formula)
  | all (sort : String) (body : Formula)
  | ex (sort : String) (body : Formula)
  | reachNamed (kind : Kind) (relation : String) (left right : Term)
  | reachBody (kind : Kind) (sort : String) (body : Formula) (left right : Term)
  deriving DecidableEq, Repr, BEq

/-- The closure language embeds constructor for constructor into Core's syntax; Core's
`Kind` and closure's are the same type (`VE.Paths.Kind`), so each kind is passed on unchanged.
Closure's typing, checker and meaning are Core's on this embedding (`VE.Core.embedClosure`). -/
def Formula.toCore : Formula → VE.Core.Formula
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p t
  | .binary p t r => .binary p t r
  | .eq t r => .eq t r
  | .not a => .not a.toCore
  | .and a b => .and a.toCore b.toCore
  | .or a b => .or a.toCore b.toCore
  | .implies a b => .implies a.toCore b.toCore
  | .all s a => .all s a.toCore
  | .ex s a => .ex s a.toCore
  | .reachNamed k p t r => .reachNamed k p t r
  | .reachBody k s a t r => .reachBody k s a.toCore t r

/-- Typing does not infer undeclared sorts or permit equality across sorts: Core's typing. -/
def Formula.WellFormed (E : Environment) (Γ : List String) (a : Formula) : Prop :=
  a.toCore.WellFormed E Γ

/-- A total executable scope, arity and sort checker: Core's checker. -/
def Formula.check (E : Environment) (Γ : List String) (a : Formula) : Bool :=
  a.toCore.check E Γ

/-- The two edge variants lower injectively to separate recursive constructors,
so Lean's ordinary structural recursor includes the Body induction hypothesis. -/
inductive Edge where
  | named (relation : String)
  | body (sort : String) (formula : Formula)
  deriving DecidableEq, Repr, BEq

def Formula.reach (k : Kind) (e : Edge) (t u : Term) : Formula :=
  match e with
  | .named r => .reachNamed k r t u
  | .body s a => .reachBody k s a t u

/-- One semantics, two syntaxes: a closure formula means what its Core embedding means. -/
def Formula.denote (S : Structure) (ρ : Valuation S) (a : Formula) : Prop :=
  a.toCore.denote S ρ

/-- The executable checker recognizes exactly the typing predicate (Core's theorem on the embedding). -/
theorem check_iff_wellFormed (E : Environment) (Γ : List String) (a : Formula) :
    a.check E Γ = true ↔ a.WellFormed E Γ :=
  VE.Core.check_iff_wellFormed E Γ a.toCore

/-- The v0 embedding changes no constructor, term, index, or sort. -/
def embed : VE.Formula → Formula
  | .top => .top
  | .bottom => .bottom
  | .unary p t => .unary p t
  | .binary p t u => .binary p t u
  | .eq t u => .eq t u
  | .not a => .not (embed a)
  | .and a b => .and (embed a) (embed b)
  | .or a b => .or (embed a) (embed b)
  | .implies a b => .implies (embed a) (embed b)
  | .all s a => .all s (embed a)
  | .ex s a => .ex s (embed a)

theorem conservativity (S : Structure) (ρ : Valuation S) (a : VE.Formula) :
    (embed a).denote S ρ ↔ a.denote S ρ := by
  induction a generalizing ρ <;>
    simp_all [embed, Formula.denote, Formula.toCore, VE.Core.Formula.denote, VE.Formula.denote]

def erase : Formula → Option VE.Formula
  | .top => some .top
  | .bottom => some .bottom
  | .unary p t => some (.unary p t)
  | .binary p t u => some (.binary p t u)
  | .eq t u => some (.eq t u)
  | .not a => return .not (← erase a)
  | .and a b => return .and (← erase a) (← erase b)
  | .or a b => return .or (← erase a) (← erase b)
  | .implies a b => return .implies (← erase a) (← erase b)
  | .all s a => return .all s (← erase a)
  | .ex s a => return .ex s (← erase a)
  | .reachNamed .. | .reachBody .. => none

theorem erase_embed (a : VE.Formula) : erase (embed a) = some a := by
  induction a <;> simp_all [erase, embed]

theorem embed_of_erase (a : Formula) (b : VE.Formula) (h : erase a = some b) :
    embed b = a := by
  induction a generalizing b <;> simp only [erase, bind, pure, Option.bind_eq_some_iff, Option.some.injEq, reduceCtorEq] at h <;>
    grind [embed]

/-- Every Reach-free new formula (recognized by erase) has exactly the old denotation. -/
theorem conservativity_without_reach (S : Structure) (ρ : Valuation S)
    (a : Formula) (b : VE.Formula) (h : erase a = some b) :
    a.denote S ρ ↔ b.denote S ρ := by
  rw [← embed_of_erase a b h]
  exact conservativity S ρ b

end VE.Closure
