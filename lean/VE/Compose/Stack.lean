import VE.Compose.Dispatch

/-! The stack order (profile-composition 1.3, PC-3): the rewriting profiles of AR-10's rows with their ranks, the
order a list enables, and the stacks the document mode admits. This file imports only `Dispatch.lean`, so
`Compose/Matrix.lean` reads it without importing `Contract.lean`, which imports `Service/Document.lean`. -/

namespace VE.Compose

/-- The rewriting profiles of a table with their ranks, each profile once, in table order. -/
def rewriters (t : List ProfileRow) : List (Nat × String) :=
  (t.filterMap fun r => match r.interface with
    | .rewrite k => some (k, r.profile)
    | _ => none).eraseDups

/-- The rewriting profiles a list enables, in stack order. -/
def stackOf (t : List ProfileRow) (ps : List String) : List String :=
  (((rewriters t).filter fun x => ps.contains x.2).mergeSort fun a b => decide (a.1 ≤ b.1)).map (·.2)

/-- C3. Ranks are distinct, so the stack order is determined. -/
theorem rewriter_ranks_distinct : ((rewriters profileTable).map (·.1)).Nodup := by decide

namespace Contract

/-- The stacks the document mode admits. `["acts@0", "scope@0"]` joins only with PC-6b, which proves
`ActsScopeRuns` (3.6); `["ve.discourse@1", "scope@0"]` and `["ve.discourse@1", "acts@0"]` with PC-7b (3.7); the
entries of the listing rule with PC-4b, PC-6c and PC-7c (pc-fid-rev). -/
def listedStacks : List (List String) := [["scope@0"], ["scope@0", "readings@1"]]

end Contract

end VE.Compose
