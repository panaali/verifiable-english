import VE.Grammar.Basic
import Std.Data.HashSet
import Std.Data.HashMap

/-! Where a sentence without a derivation stops (docs/spec/english-lean-e2.md 4.5).

`viable G budget w` runs a recogniser of `G` over `w` from the left (Earley's: predict, scan, complete) and
returns the farthest position `k` such that the tokens before `k` begin some sentence of `G`, with the items of
that position: each a rule, how much of its right-hand side is read, and where that rule started. The reader
calls it only after `verdict` found no derivation, to say what the sentence needs at `k`; it decides nothing,
and no verdict reads it. A rule's right-hand side is never empty (W2), so an item that is complete at `k` began
before `k`, and its parents' column is already complete when it is read.

The budget counts the items processed; when it is exceeded the result is `none`, never a nearer position.
-/

namespace VE.Grammar

/-- A rule `rule` of the grammar with its first `dot` symbols read, started at position `origin`. -/
structure EarleyItem where
  rule : Nat
  dot : Nat
  origin : Nat
  deriving BEq, Hashable, Repr, Inhabited, DecidableEq

/-- One position of the recogniser: its items in the order found, and for each nonterminal the items that
wait for it there. -/
structure Column where
  items : Array EarleyItem := #[]
  seen : Std.HashSet EarleyItem := {}
  waiting : Std.HashMap Nat (Array EarleyItem) := {}

def Column.add (c : Column) (i : EarleyItem) : Column :=
  if c.seen.contains i then c else { c with items := c.items.push i, seen := c.seen.insert i }

variable {K T : Type} [Accepts K T]

/-- The symbol after the dot of an item, if any. -/
def EarleyItem.next (G : Grammar K) (i : EarleyItem) : Option (Sym K) :=
  (G.rules[i.rule]?).bind fun R => R.rhs[i.dot]?

/-- The rules of each nonterminal, by left-hand side. -/
def byLhs (G : Grammar K) : Array (Array Nat) := Id.run do
  let mut out : Array (Array Nat) := Array.replicate G.rank.size #[]
  for r in [0:G.rules.size] do
    let lhs := (G.rules[r]?.map (·.lhs)).getD 0
    if lhs < out.size then out := out.modify lhs (·.push r)
  return out

/-- The farthest position whose prefix begins a sentence, and that position's items; `none` when the budget
of processed items is exceeded. -/
def viable (G : Grammar K) (budget : Nat) (w : Array T) : Option (Nat × Array EarleyItem) := Id.run do
  let rulesOf := byLhs G
  let start : Column := ((rulesOf[G.start]?).getD #[]).foldl (fun c r => c.add ⟨r, 0, 0⟩) {}
  let mut cols : Array Column := #[start]
  let mut work := 0
  for k in [0:w.size + 1] do
    let mut col := (cols[k]?).getD {}
    let mut nextCol : Column := {}
    let mut idx := 0
    -- Every pass processes one item; a column holds at most rules × (positions + 1) × (k + 1) items.
    for _ in [0:budget + 1] do
      if idx ≥ col.items.size then break
      work := work + 1
      if work > budget then return none
      let it := col.items[idx]!
      idx := idx + 1
      match it.next G with
      | some (.n A) =>
        col := { col with waiting := col.waiting.insert A (((col.waiting.get? A).getD #[]).push it) }
        for r in (rulesOf[A]?).getD #[] do
          col := col.add ⟨r, 0, k⟩
      | some (.t a) =>
        if h : k < w.size then
          if Accepts.accepts a w[k] then nextCol := nextCol.add { it with dot := it.dot + 1 }
      | none =>
        let lhs := ((G.rules[it.rule]?).map (·.lhs)).getD 0
        let parents := ((cols[it.origin]?).bind fun c => c.waiting.get? lhs).getD #[]
        for p in parents do
          col := col.add { p with dot := p.dot + 1 }
    if idx < col.items.size then return none
    cols := cols.set! k col
    if nextCol.items.isEmpty then return some (k, col.items)
    cols := cols.push nextCol
  return some (w.size, ((cols[w.size]?).map (·.items)).getD #[])

end VE.Grammar
