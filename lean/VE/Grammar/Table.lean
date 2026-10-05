import VE.Grammar.Derives

/-! The parser and the verdict (docs/spec/english-lean.md 2.6 and 5.4).

`parse G cap budget w` fills a table from the last start position to the first. Within a row the
rules are applied in increasing rank of their left-hand side, so a rule whose right-hand side begins
with a nonterminal reads an entry of the same row that is already complete (W3). The rest of a rule is
read from a suffix entry of a later row (W2): for each start position, rule and position `d ≥ 1` of
its right-hand side, the lists of trees that derive the symbols from `d` on, by end position. Every
entry holds at most `cap` items per end position and is either complete or full (the cap
invariant). Stored trees refer to the stored trees of their parts; nothing is copied.

Indexing (`Grammar.prepare`, once per grammar). The distinct terminals of the grammar are listed, and
the positions `d ≥ 1` of all right-hand sides are grouped by their symbol: one group per distinct
terminal, one per nonterminal. Each row computes, once per distinct terminal, whether it accepts the
row's token, and fills only the suffix entries of the groups whose symbol has something at the row: a
terminal that accepts the token, a nonterminal whose entry is not empty. Every other suffix entry is
empty. A rule whose first symbol has nothing at the row is skipped in the same way.

The budget counts steps: one per rule attempt and per suffix attempt, failed or not, and one per
combination of a first symbol's tree with a suffix list. An attempt that indexing skips is an attempt
that fails at once, so every row costs at least the number of rules and rule positions; the count is
the same as without indexing. It is checked after each row, so the work done is at most the budget plus
one row; when it is exceeded the result is `none`, never a shorter list. The last pass re-checks each
returned tree against `Tree.derives` and the sentence, removes duplicates and keeps at most `cap` trees;
under well-formedness it changes nothing.
-/

namespace VE.Grammar

/-- A table entry: for each end position, up to `cap` items. -/
abbrev Bucket (X : Type) := List (Nat × List X)

variable {X : Type}

/-- The items of an entry that end at `j`. -/
def Bucket.get : Bucket X → Nat → List X
  | [], _ => []
  | (k, xs) :: e, j => if k = j then xs else Bucket.get e j

/-- Adds `x` when the list is shorter than `cap`. The items offered to one entry are distinct, so no
membership test is made here; the last pass removes duplicates in any case. -/
def insertCapped (cap : Nat) (xs : List X) (x : X) : List X :=
  if xs.length < cap then xs ++ [x] else xs

/-- Adds candidates sorted by end position to a bucket whose end positions increase. One pass over
both lists. -/
def Bucket.merge (cap : Nat) : Bucket X → List (Nat × X) → Bucket X
  | e, [] => e
  | [], (j, x) :: cs => Bucket.merge cap [(j, insertCapped cap [] x)] cs
  | (k, xs) :: e, (j, x) :: cs =>
    if k < j then (k, xs) :: Bucket.merge cap e ((j, x) :: cs)
    else if k = j then Bucket.merge cap ((k, insertCapped cap xs x) :: e) cs
    else Bucket.merge cap ((j, insertCapped cap [] x) :: (k, xs) :: e) cs
termination_by e cs => e.length + 2 * cs.length

/-- Adds candidates to a bucket: they are sorted by end position, then merged in. -/
def Bucket.addAll (cap : Nat) (e : Bucket X) (cands : List (Nat × X)) : Bucket X :=
  Bucket.merge cap e (cands.mergeSort fun a b => decide (a.1 ≤ b.1))

/-- Keeps the last occurrence of each item. -/
def dedup [DecidableEq X] : List X → List X
  | [] => []
  | x :: xs => if x ∈ xs then dedup xs else x :: dedup xs

variable {T K : Type} [DecidableEq T] [DecidableEq K] [Accepts K T]

/-- Adds the terminals of a right-hand side that are not listed yet. -/
def addTerms (acc : Array K) : List (Sym K) → Array K
  | [] => acc
  | .t a :: rest => addTerms (if acc.contains a then acc else acc.push a) rest
  | .n _ :: rest => addTerms acc rest

/-- The distinct terminals of the grammar, in order of first occurrence. -/
def termsOf (G : Grammar K) : Array K :=
  G.rules.foldl (fun acc R => addTerms acc R.rhs) #[]

/-- The index of a symbol's terminal in `terms`; `0` for a nonterminal. -/
def termIndex (terms : Array K) : Sym K → Nat
  | .t a => terms.idxOf a
  | .n _ => 0

/-- A rule as the parser reads it: its index, its left-hand side, its right-hand side, and the index
of its first symbol's terminal in the list of distinct terminals. -/
structure CRule (K : Type) where
  index : Nat
  lhs : Nat
  rhs : List (Sym K)
  first : Nat

/-- A position `d ≥ 1` of the right-hand side of a rule: the rule, `d`, the symbol there, and whether
it is the last symbol. -/
structure SufPos (K : Type) where
  rule : Nat
  pos : Nat
  sym : Sym K
  last : Bool

/-- The positions `d ≥ 1` of a right-hand side whose symbols from `d` on are given. -/
def sufPositions (r : Nat) : List (Sym K) → Nat → List (SufPos K)
  | [], _ => []
  | Y :: rest, d =>
    if d = 0 then sufPositions r rest 1 else ⟨r, d, Y, rest.isEmpty⟩ :: sufPositions r rest (d + 1)

/-- Each item in the group its key names, when the key is below `n`. -/
def groupBy {α : Type} (n : Nat) (key : α → Option Nat) (xs : List α) : Array (List α) :=
  xs.foldl (fun g x => match key x with
    | some k => g.modify k (x :: ·)
    | none => g) (Array.replicate n [])

/-- The nonempty groups with their keys. -/
def groupList {α : Type} (g : Array (List α)) : List (Nat × List α) :=
  g.toList.zipIdx.filterMap fun (xs, k) => if xs.isEmpty then none else some (k, xs)

/-- A grammar with what the parser computes once per grammar: its distinct terminals; its rules in
increasing rank of their left-hand side; the positions `d ≥ 1` of all right-hand sides grouped by
terminal and by nonterminal; the length of each right-hand side; and the number of those positions.
A reader of several sentences prepares the grammar once. -/
structure Prepared (K : Type) where
  grammar : Grammar K
  terms : Array K
  order : List (CRule K)
  byTerm : List (Nat × List (SufPos K))
  byNt : List (Nat × List (SufPos K))
  shape : Array Nat
  positions : Nat

def Grammar.prepare (G : Grammar K) : Prepared K :=
  let terms := termsOf G
  let rules := G.rules.toList.zipIdx.map fun (R, r) =>
    ({ index := r, lhs := R.lhs, rhs := R.rhs, first := (R.rhs.head?.map (termIndex terms)).getD 0 } : CRule K)
  let pos := G.rules.toList.zipIdx.flatMap fun (R, r) => sufPositions r R.rhs 0
  { grammar := G, terms,
    order := rules.mergeSort fun a b => decide (G.rank.getD a.lhs 0 ≤ G.rank.getD b.lhs 0),
    byTerm := groupList (groupBy terms.size (fun p => match p.sym with
      | .t a => some (terms.idxOf a)
      | .n _ => none) pos),
    byNt := groupList (groupBy G.rank.size (fun p => match p.sym with
      | .n B => some B
      | .t _ => none) pos),
    shape := G.rules.map (·.rhs.length),
    positions := pos.length }

/-- The entries of one start position for the nonterminals, indexed by nonterminal. -/
abbrev NtRow (T : Type) := Array (Bucket (Tree T))

/-- The suffix entries of one start position, indexed by rule and by position in its right-hand side;
position `0` is unused. -/
abbrev SufRow (T : Type) := Array (Array (Bucket (List (Tree T))))

/-- The suffix entry of the rule `r` from position `d` on, at the start position `p`. -/
def sufGet (suf : Array (SufRow T)) (p r d : Nat) : Bucket (List (Tree T)) :=
  ((suf.getD p #[]).getD r #[]).getD d []

/-- The trees of a symbol that start at `i`: one leaf for a terminal, the row's entry for a
nonterminal. -/
def firstAt (w : Array T) (i : Nat) (row : NtRow T) : Sym K → Bucket (Tree T)
  | .t a =>
      match w[i]? with
      | some x => if Accepts.accepts a x then [(i + 1, [.leaf x])] else []
      | none => []
  | .n B => row.getD B []

/-- Whether a rule's first symbol can start at the row: `acc` says which distinct terminals accept
the row's token. When it is false, `firstAt` is empty. -/
def avail (acc : Array Bool) (row : NtRow T) (R : CRule K) : Sym K → Bool
  | .t _ => acc.getD R.first false
  | .n B => !(row.getD B []).isEmpty

/-- A symbol's trees followed by a suffix's lists: each tree that ends at `j1` is put in front of
each list of the suffix entry at `j1`. With `last`, the symbol is the last one of the rule. -/
def combine (first : Bucket (Tree T)) (next : Nat → Bucket (List (Tree T))) (last : Bool) :
    List (Nat × List (Tree T)) :=
  first.flatMap fun p => p.2.flatMap fun t =>
    if last then [(p.1, [t])]
    else (next p.1).flatMap fun q => q.2.map fun us => (q.1, t :: us)

/-- The rules applied at the start position `i`, in the order given: the trees of each rule are
added to the entry of its left-hand side. Each rule attempt is a step, and so is each combination. -/
def ntRowGo (acc : Array Bool) (cap : Nat) (w : Array T) (i : Nat) (suf : Array (SufRow T)) :
    List (CRule K) → NtRow T → Nat → NtRow T × Nat
  | [], row, steps => (row, steps)
  | R :: Rs, row, steps =>
    match R.rhs with
    | [] => ntRowGo acc cap w i suf Rs row (steps + 1)
    | Y :: rest =>
      if avail acc row R Y then
        match combine (firstAt w i row Y) (fun j1 => sufGet suf j1 R.index 1) rest.isEmpty with
        | [] => ntRowGo acc cap w i suf Rs row (steps + 1)
        | cands =>
          ntRowGo acc cap w i suf Rs
            (row.modify R.lhs fun e => e.addAll cap (cands.map fun c => (c.1, Tree.node R.index c.2)))
            (steps + 1 + cands.length)
      else ntRowGo acc cap w i suf Rs row (steps + 1)

/-- The suffix entries of the positions given, at the start position `i`; `c` counts the
combinations. An entry with no member is left as it is in `out`, empty. -/
def sufPosGo (cap : Nat) (w : Array T) (i : Nat) (row : NtRow T) (suf : Array (SufRow T)) :
    List (SufPos K) → SufRow T → Nat → SufRow T × Nat
  | [], out, c => (out, c)
  | p :: ps, out, c =>
    match combine (firstAt w i row p.sym) (fun j1 => sufGet suf j1 p.rule (p.pos + 1)) p.last with
    | [] => sufPosGo cap w i row suf ps out c
    | cands =>
      sufPosGo cap w i row suf ps
        (out.modify p.rule fun e => e.setIfInBounds p.pos (Bucket.addAll cap [] cands))
        (c + cands.length)

/-- The groups whose key `on` selects, each filled by `sufPosGo`. -/
def sufGroups (cap : Nat) (w : Array T) (i : Nat) (row : NtRow T) (suf : Array (SufRow T))
    (on : Nat → Bool) : List (Nat × List (SufPos K)) → SufRow T → Nat → SufRow T × Nat
  | [], out, c => (out, c)
  | (k, g) :: gs, out, c =>
    if on k then
      match sufPosGo cap w i row suf g out c with
      | (out2, c2) => sufGroups cap w i row suf on gs out2 c2
    else sufGroups cap w i row suf on gs out c

/-- Which distinct terminals accept the token at `i`. -/
def accepted (terms : Array K) (w : Array T) (i : Nat) : Array Bool :=
  match w[i]? with
  | some x => terms.map fun a => Accepts.accepts a x
  | none => #[]

/-- One row: the nonterminal entries, the suffix entries and the steps of the row. `empty` is the
suffix row with every entry empty. -/
def rowAt (P : Prepared K) (cap : Nat) (w : Array T) (empty : SufRow T) (suf : Array (SufRow T))
    (i : Nat) : NtRow T × SufRow T × Nat :=
  let acc := accepted P.terms w i
  match ntRowGo acc cap w i suf P.order (Array.replicate P.grammar.rank.size []) 0 with
  | (nt, s1) =>
    match sufGroups cap w i nt suf (fun k => acc.getD k false) P.byTerm empty 0 with
    | (o1, c1) =>
      match sufGroups cap w i nt suf (fun B => !(nt.getD B []).isEmpty) P.byNt o1 c1 with
      | (o2, c2) => (nt, o2, s1 + P.positions + c2)

/-- The rows from the start position `k - 1` down to `0`, with the step budget checked after each
row. -/
def fill (P : Prepared K) (cap : Nat) (w : Array T) (empty : SufRow T) (budget : Nat) :
    Nat → Array (SufRow T) → Nat → NtRow T → Option (NtRow T × Nat)
  | 0, _, steps, last => some (last, steps)
  | k + 1, suf, steps, _ =>
    let row := rowAt P cap w empty suf k
    if budget < steps + row.2.2 then none
    else fill P cap w empty budget k (suf.setIfInBounds k row.2.1) (steps + row.2.2) row.1

/-- The last pass: the returned trees are derivations of the start symbol over the sentence, without
duplicates, at most `cap` of them. -/
def finalPass (G : Grammar K) (cap : Nat) (w : Array T) (ts : List (Tree T)) : List (Tree T) :=
  (dedup (ts.filter fun t => t.derives G (.n G.start) && t.yield == w.toList)).take cap

/-- The filled table of `w`, with its steps, when they are within the budget. -/
def Prepared.table (P : Prepared K) (cap budget : Nat) (w : Array T) : Option (NtRow T × Nat) :=
  fill P cap w (P.shape.map fun n => Array.replicate n []) budget w.size
    (Array.replicate (w.size + 1) #[]) 0 #[]

/-- `parse` on a prepared grammar. -/
def Prepared.parse (P : Prepared K) (cap budget : Nat) (w : Array T) : Option (List (Tree T)) :=
  match P.table cap budget w with
  | none => none
  | some (last, _) => some (finalPass P.grammar cap w ((last.getD P.grammar.start []).get w.size))

/-- Up to `cap` derivations of the start symbol over `w`; `none` when the step budget is exhausted. -/
def parse (G : Grammar K) (cap budget : Nat) (w : Array T) : Option (List (Tree T)) :=
  G.prepare.parse cap budget w

/-- The steps that `parse` takes on `w`, when they are within the budget. Measurement only. -/
def Prepared.steps (P : Prepared K) (cap budget : Nat) (w : Array T) : Option Nat :=
  (P.table cap budget w).map (·.2)

inductive Verdict (T : Type) where
  | zero
  | one (t : Tree T)
  | many (t u : Tree T)

/-- `verdict` on a prepared grammar. -/
def Prepared.verdict (P : Prepared K) (budget : Nat) (w : Array T) : Option (Verdict T) :=
  match P.parse 2 budget w with
  | none => none
  | some [] => some .zero
  | some [t] => some (.one t)
  | some (t :: u :: _) => some (.many t u)

def verdict (G : Grammar K) (budget : Nat) (w : Array T) : Option (Verdict T) :=
  match parse G 2 budget w with
  | none => none
  | some [] => some .zero
  | some [t] => some (.one t)
  | some (t :: u :: _) => some (.many t u)

end VE.Grammar
