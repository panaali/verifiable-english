import VE.English.Grammar

/-! # Canonical renderer for the core fragment

Mirrors `EnglishTraversal` in `ve/english.py` without relative-clause
contractions and validated negatives (those forms are Lean coverage pending):

* binder naming (`binding`): for each sort, `maxScope` is the largest number of
  simultaneously bound entities of that sort in the statement (`_max_scope`);
  at most one gives `that person`, two give `first`/`second`, more give numbered
  labels `S1`, `S2`, … by scope position;
* two simple operands use compact `both … and …`/`either … or …, or both`;
  otherwise a two-item list, headed `both of the following hold` unless an
  operand is itself a connective (`all of the following hold`);
* implication is always `if …, then …`; negation is `it is not the case that`;
* `there is a`/`an` agrees with the first letter of the declaration. -/
namespace VE.English

/-- Nesting depth of binders of sort `s` (`_max_scope` per sort). -/
def sdepth (s : String) : Formula → Nat
  | .all t a | .ex t a => (if t = s then 1 else 0) + sdepth s a
  | .not a => sdepth s a
  | .and a b | .or a b | .implies a b => max (sdepth s a) (sdepth s b)
  | _ => 0

def scopeCount (s : String) (Γ : List Ref) : Nat := Γ.countP fun r => r.sort == s

/-- The naming form of a new binder of sort `s` under scope `Γ`. -/
def bindRef (M : String → Nat) (Γ : List Ref) (s : String) : Ref :=
  if M s ≤ 1 then .plain s
  else if M s = 2 then (if scopeCount s Γ = 0 then .first s else .second s)
  else .named s (scopeCount s Γ + 1)

def isSimple : Formula → Bool
  | .top | .bottom | .unary .. | .binary .. | .eq .. => true
  | _ => false

def isConnective : Formula → Bool
  | .and .. | .or .. | .implies .. => true
  | _ => false

def renderTerm (Γ : List Ref) : Term → TermTree
  | .var i => .ref (Γ[i]?.getD default)
  | .const c => .const c

def renderLit (Γ : List Ref) : Formula → Lit
  | .bottom => .falsity
  | .unary p t => .pred p [renderTerm Γ t]
  | .binary p t u => .pred p [renderTerm Γ t, renderTerm Γ u]
  | .eq t u => .eq (renderTerm Γ t) (renderTerm Γ u)
  | _ => .truth

def vowelStart (L : Lexicon) (r : Ref) : Bool :=
  match r.declYield L with
  | .word w :: _ => ['a', 'e', 'i', 'o', 'u'].contains (w.toList.headD ' ')
  | _ => false

def renderTree (L : Lexicon) (M : String → Nat) : List Ref → Formula → Tree
  | Γ, .not a => .neg (renderTree L M Γ a)
  | Γ, .and a b =>
      if isSimple a && isSimple b then .both (renderLit Γ a) (renderLit Γ b)
      else .list (if isConnective a || isConnective b then .all else .both)
        (renderTree L M Γ a) (renderTree L M Γ b)
  | Γ, .or a b =>
      if isSimple a && isSimple b then .either (renderLit Γ a) (renderLit Γ b)
      else .list .atLeastOne (renderTree L M Γ a) (renderTree L M Γ b)
  | Γ, .implies a b => .cond (renderTree L M Γ a) (renderTree L M Γ b)
  | Γ, .all s a =>
      let r := bindRef M Γ s
      .all r (renderTree L M (r :: Γ) a)
  | Γ, .ex s a =>
      let r := bindRef M Γ s
      .ex (vowelStart L r) r (renderTree L M (r :: Γ) a)
  | Γ, A => .lit (renderLit Γ A)

def renderStatement (L : Lexicon) (A : Formula) : Tree :=
  renderTree L (fun s => sdepth s A) [] A

def render (L : Lexicon) (As : List Formula) : List Tok :=
  docYield L (As.map (renderStatement L))

end VE.English
