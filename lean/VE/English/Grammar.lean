import VE.English.Lexicon

/-! # Grammar of the core English fragment

Derivations are parse trees (`Tree`), so "exactly one derivation" means equality
of trees, not merely of the ASTs they denote. A tree's `yield` is the token
sequence it derives; list markers depend on the nesting depth `d` exactly as in
`EnglishTraversal.formula` (`(a)`/`(b)` at even depth, `(i)`/`(ii)` at odd depth).

Core productions (a subset of the EBNF in `docs/english-surface.md`):

```
formula  = clause | "it is not the case that" formula
         | "both" clause "and" clause | "either" clause "or" clause ", or both"
         | "if" formula ", then" formula
         | header ":" marker formula ";" marker formula
         | "for every" declaration "," formula
         | "there is" ("a" | "an") declaration "such that" formula
clause   = "this holds in all cases" | "this is impossible"
         | term "is the same as" term | instantiated template
```

Not yet in the core (Lean coverage pending): relative-clause contractions and
guards, validated negative templates, legacy split-`if` lists, closure (`reach`),
order comparisons, and every later profile's wording. -/
namespace VE.English

inductive Header where
  | all
  | both
  | atLeastOne
  deriving DecidableEq, Repr

def Header.yield : Header → List Tok
  | .all => kws ["all", "of", "the", "following", "hold", ":"]
  | .both => kws ["both", "of", "the", "following", "hold", ":"]
  | .atLeastOne => kws ["at", "least", "one", "of", "the", "following", "holds", ":"]

def markers (d : Nat) : Tok × Tok :=
  if d % 2 = 0 then (kw "(a)", kw "(b)") else (kw "(i)", kw "(ii)")

inductive Tree where
  | lit (a : Lit)
  | neg (body : Tree)
  | both (a b : Lit)
  | either (a b : Lit)
  | cond (a b : Tree)
  | list (h : Header) (a b : Tree)
  | all (decl : Ref) (body : Tree)
  | ex (an : Bool) (decl : Ref) (body : Tree)
  deriving DecidableEq, Repr, Inhabited

def Tree.yield (L : Lexicon) : Nat → Tree → List Tok
  | _, .lit a => a.yield L
  | d, .neg b => kws ["it", "is", "not", "the", "case", "that"] ++ b.yield L d
  | _, .both a b => kw "both" :: (a.yield L ++ kw "and" :: b.yield L)
  | _, .either a b => kw "either" :: (a.yield L ++ kw "or" :: (b.yield L ++ kws [",", "or", "both"]))
  | d, .cond a b => kw "if" :: (a.yield L d ++ kw "," :: kw "then" :: b.yield L d)
  | d, .list h a b => h.yield ++ (markers d).1 ::
      (a.yield L (d + 1) ++ kw ";" :: (markers d).2 :: b.yield L (d + 1))
  | d, .all r b => kw "for" :: kw "every" :: (r.declYield L ++ kw "," :: b.yield L d)
  | d, .ex an r b => kw "there" :: kw "is" :: kw (if an then "an" else "a") ::
      (r.declYield L ++ kw "such" :: kw "that" :: b.yield L d)

/-- Grammatical trees: every symbol is in the lexicon. Scope and typing are
not part of the grammar, so uniqueness over these trees is the stronger claim. -/
def Tree.Syntactic (L : Lexicon) : Tree → Prop
  | .lit a => a.ok L = true
  | .neg b => b.Syntactic L
  | .both a b | .either a b => a.ok L = true ∧ b.ok L = true
  | .cond a b | .list _ a b => a.Syntactic L ∧ b.Syntactic L
  | .all r b | .ex _ r b => r.sort ∈ L.sorts ∧ b.Syntactic L

def Tree.size : Tree → Nat
  | .lit _ | .both .. | .either .. => 1
  | .neg b | .all _ b | .ex _ _ b => b.size + 1
  | .cond a b | .list _ a b => a.size + b.size + 1

/-! ## Readings: scoped declaration forms must be distinct, as in the Python parser. -/

def TermTree.denote (Γ : List Ref) : TermTree → Option Term
  | .const c => some (.const c)
  | .ref r => (Γ.idxOf? r).map Term.var

def Lit.denote (Γ : List Ref) : Lit → Option Formula
  | .truth => some .top
  | .falsity => some .bottom
  | .eq a b => do some (.eq (← a.denote Γ) (← b.denote Γ))
  | .pred p [a] => do some (.unary p (← a.denote Γ))
  | .pred p [a, b] => do some (.binary p (← a.denote Γ) (← b.denote Γ))
  | .pred _ _ => none

def Tree.denote : List Ref → Tree → Option Formula
  | Γ, .lit a => a.denote Γ
  | Γ, .neg b => (b.denote Γ).map .not
  | Γ, .both a b => do some (.and (← a.denote Γ) (← b.denote Γ))
  | Γ, .either a b => do some (.or (← a.denote Γ) (← b.denote Γ))
  | Γ, .cond a b => do some (.implies (← a.denote Γ) (← b.denote Γ))
  | Γ, .list h a b => do
      let x ← a.denote Γ
      let y ← b.denote Γ
      some (if h = .atLeastOne then .or x y else .and x y)
  | Γ, .all r b => if r ∈ Γ then none else (b.denote (r :: Γ)).map (.all r.sort)
  | Γ, .ex _ r b => if r ∈ Γ then none else (b.denote (r :: Γ)).map (.ex r.sort)

/-! ## Documents: sentences end with a period. -/

def docYield (L : Lexicon) (ts : List Tree) : List Tok :=
  ts.flatMap fun t => t.yield L 0 ++ [kw "."]

/-- The checked reading of a document derivation: nonempty, every sentence
resolves, and every formula is closed and well typed. -/
def readTrees (E : Environment) (ts : List Tree) : Option (List Formula) := do
  if ts.isEmpty then none else
  let As ← ts.mapM (Tree.denote [])
  if As.all (fun A => A.check E []) then some As else none

end VE.English
