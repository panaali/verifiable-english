import VE.RightClauses.Wire

/-! `elided_bytes` (docs/spec/right-clauses.md 4.1 step 5, 6, 8.1, 9.1 K4, 9.3): the bytes of a unit that the author
lists in its structured lines' `elided` spans, that is, the bytes nothing in the line formalises.

A line's count is the sum of `b - a` over its elided spans (6). The head's checks (`checkSpans`, 1.1) have already
refused a span that is empty, outside the unit, or overlapping another span of the same line, so no byte of a line is
counted twice. 1.1 does not constrain spans of different lines of one unit, and 6 sums over the unit's lines; so does
`unitElided`.

Cost (the evaluator rule, reviews/dri-decisions-20261027-me-12-n1.md): `entryElided` reads every decoded elided span
exactly once, and `elidedTotal` and `unitElided` read only its numbers. `unitElided` finds a line object's entry by the
key `plainLineJson` uses (right, rule name). Its work is (named line objects) × (entries), the bound the elaboration
already has. Both are bounded by the request: the service's request size, and `decodeClauseDoc`'s 1,024 units. There is
no new limit (10). Reading candidates are not counted: this route refuses `readings@1` (`VE.RightClauses.Run`). -/
namespace VE.RightClauses
open Lean

/-- One line's elided bytes: the sum of `b - a` over its elided spans (6). -/
def lineElided (L : CLine) : Nat := L.elided.foldl (fun n s => n + (s.2 - s.1)) 0

/-- Each structured line's key (right, rule name) and its elided bytes, in document order. Every span is read here,
    once. -/
def entryElided (D : ClauseDoc) : List ((String × String) × Nat) :=
  D.lines.map fun (R, n, L) => ((R, n), lineElided L)

/-- The document total (6): the sum over every structured line. -/
def elidedTotal (es : List ((String × String) × Nat)) : Nat := es.foldl (fun n e => n + e.2) 0

/-- Per unit of `document`, in document order (6, 9.3): the sum over the unit's line objects of their entries' bytes,
    each entry found by (right, rule name). A unit with no line-bearing body, or no named line, has 0. -/
def unitElided (es : List ((String × String) × Nat)) (document : Json) : List Nat :=
  (unitsOf document).map fun u =>
    match unitBody (dropKeys ["span"] u) with
    | some (k, b) =>
      let R := bodyRight k b
      (bodyLines b).foldl (fun n l =>
        n + (((jsonLineName l).bind fun r => (es.find? (·.1 == (R, r))).map (·.2)).getD 0)) 0
    | none => 0

end VE.RightClauses
