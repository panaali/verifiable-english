import VE.English.Grammar

/-! # Executable parser for the core fragment

A deterministic prefix parser: the first token selects the production, a simple
clause extends to the next clause-ending token, and the clause itself is
recognised by searching the finite candidate set built from the lexicon and the
labels occurring in it. `Proofs.lean` shows the parser finds the derivation of
every grammatical text (so derivations are unique) and returns only
derivations. Recursive calls decrease explicit fuel; public entry points use
input length plus one. -/
namespace VE.English

/-- Literal consumption of a token prefix. -/
def consume : List Tok → List Tok → Option (List Tok)
  | [], input => some input
  | x :: xs, y :: ys => if x = y then consume xs ys else none
  | _ :: _, [] => none

def isAtomStop (x : Tok) : Bool := atomStops.contains x

/-- `a` occurs contiguously in `b`. -/
def infixB (a b : List Tok) : Bool :=
  (List.range (b.length + 1)).any fun i => a.isPrefixOf (b.drop i)

def labelsIn : List Tok → List (String × Nat)
  | [] => []
  | .label c k :: rest => (c, k) :: labelsIn rest
  | .word _ :: rest => labelsIn rest

def namedRefs (L : Lexicon) (run : List Tok) (s : String) : List TermTree :=
  (labelsIn run).filterMap fun (c, k) => if c = L.letter s then some (.ref (.named s k)) else none

/-- Every term that could occur in `run`. -/
def termPool (L : Lexicon) (run : List Tok) : List TermTree :=
  (L.constants.map TermTree.const ++
    L.sorts.flatMap (fun s => ([.ref (.plain s), .ref (.first s), .ref (.second s)] : List TermTree) ++
      namedRefs L run s))
  |>.filter fun t => infixB (t.yield L) run

def tuples {α : Type} (pool : List α) : Nat → List (List α)
  | 0 => [[]]
  | n + 1 => pool.flatMap fun x => (tuples pool n).map (x :: ·)

def litCandidates (L : Lexicon) (run : List Tok) : List Lit :=
  let pool := termPool L run
  [.truth, .falsity] ++ pool.flatMap (fun a => pool.map (Lit.eq a)) ++
    L.predicates.flatMap fun p => match L.template p with
      | some T => (tuples pool T.arity).map (Lit.pred p)
      | none => []

def parseLit (L : Lexicon) (run : List Tok) : Option Lit :=
  (litCandidates L run).find? fun a => a.ok L && a.yield L == run

def parseLitPrefix (L : Lexicon) (input : List Tok) : Option (Lit × List Tok) :=
  (parseLit L (input.takeWhile fun x => !isAtomStop x)).map
    fun a => (a, input.dropWhile fun x => !isAtomStop x)

def readNoun (L : Lexicon) (input : List Tok) : Option (String × List Tok) :=
  (L.sorts.find? fun s => (kws (L.noun s)).isPrefixOf input).map
    fun s => (s, input.drop (L.noun s).length)

def takeLabel (L : Lexicon) (s : String) : List Tok → Option (Nat × List Tok)
  | y :: .label c k :: rest => if y = kw "named" ∧ c = L.letter s then some (k, rest) else none
  | _ => none

def parseDecl (L : Lexicon) : List Tok → Option (Ref × List Tok)
  | [] => none
  | x :: rest =>
    if x = kw "first" then (readNoun L rest).map fun (s, rest) => (.first s, rest)
    else if x = kw "second" then (readNoun L rest).map fun (s, rest) => (.second s, rest)
    else match readNoun L (x :: rest) with
      | none => none
      | some (s, rest) => match takeLabel L s rest with
        | some (k, rest') => some (.named s k, rest')
        | none => some (.plain s, rest)

def listTail (p : Nat → List Tok → Option (Tree × List Tok)) (d : Nat) (h : Header)
    (rest : List Tok) : Option (Tree × List Tok) := do
  let rest ← consume [(markers d).1] rest
  let (a, rest) ← p (d + 1) rest
  let rest ← consume [kw ";", (markers d).2] rest
  let (b, rest) ← p (d + 1) rest
  some (.list h a b, rest)

def parseF (L : Lexicon) : Nat → Nat → List Tok → Option (Tree × List Tok)
  | 0, _, _ => none
  | _ + 1, _, [] => none
  | fuel + 1, d, x :: rest =>
    if x = kw "it" then do
      let rest ← consume (kws ["is", "not", "the", "case", "that"]) rest
      let (b, rest) ← parseF L fuel d rest
      some (.neg b, rest)
    else if x = kw "both" then
      match consume (kws ["of", "the", "following", "hold", ":"]) rest with
      | some rest => listTail (parseF L fuel) d .both rest
      | none => do
        let (a, rest) ← parseLitPrefix L rest
        let rest ← consume [kw "and"] rest
        let (b, rest) ← parseLitPrefix L rest
        some (.both a b, rest)
    else if x = kw "either" then do
      let (a, rest) ← parseLitPrefix L rest
      let rest ← consume [kw "or"] rest
      let (b, rest) ← parseLitPrefix L rest
      let rest ← consume (kws [",", "or", "both"]) rest
      some (.either a b, rest)
    else if x = kw "if" then do
      let (a, rest) ← parseF L fuel d rest
      let rest ← consume (kws [",", "then"]) rest
      let (b, rest) ← parseF L fuel d rest
      some (.cond a b, rest)
    else if x = kw "all" then do
      let rest ← consume (kws ["of", "the", "following", "hold", ":"]) rest
      listTail (parseF L fuel) d .all rest
    else if x = kw "at" then do
      let rest ← consume (kws ["least", "one", "of", "the", "following", "holds", ":"]) rest
      listTail (parseF L fuel) d .atLeastOne rest
    else if x = kw "for" then do
      let rest ← consume [kw "every"] rest
      let (r, rest) ← parseDecl L rest
      let rest ← consume [kw ","] rest
      let (b, rest) ← parseF L fuel d rest
      some (.all r b, rest)
    else if x = kw "there" then
      match rest with
      | y :: z :: rest =>
        if y = kw "is" ∧ (z = kw "a" ∨ z = kw "an") then do
          let (r, rest) ← parseDecl L rest
          let rest ← consume (kws ["such", "that"]) rest
          let (b, rest) ← parseF L fuel d rest
          some (.ex (z == kw "an") r b, rest)
        else none
      | _ => none
    else do
      let (a, rest) ← parseLitPrefix L (x :: rest)
      some (.lit a, rest)

def parseTrees (L : Lexicon) : Nat → List Tok → Option (List Tree)
  | 0, _ => none
  | _ + 1, [] => some []
  | fuel + 1, x :: xs => do
    let (t, rest) ← parseF L (xs.length + 2) 0 (x :: xs)
    let rest ← consume [kw "."] rest
    let ts ← parseTrees L fuel rest
    some (t :: ts)

/-- Parse a token sequence into checked closed formulas. -/
def parse (E : Environment) (L : Lexicon) (input : List Tok) : Option (List Formula) := do
  readTrees E (← parseTrees L (input.length + 1) input)

end VE.English
