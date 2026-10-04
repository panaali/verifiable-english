import VE.Json
import VE.WireContract.Engine
import VE.WireContract.Hooks.Corpus
import VE.WireContract.Hooks.SoftNorms

/-! The diagnose runner (docs/spec/wire-contract.md 4.2), the `ve_service` mode `diagnose`
(`VE.Service.Diagnose`; formerly the one-shot `ve_diagnose`): the registry of contracts and the
rows it gives.

For a case of the same JSON as the unit's route, `diagnoseCase` builds the case's root with the
unit's input adapter, runs the engine and gives one row: the outcome `fault` with its record, or
`clean`. Rows keep `status` within `ok` and `error`. It decides no verdict: a route's legacy
validator alone accepts or rejects, and this runner only names the first failing check of a
rejection.
-/

namespace VE.WireContract.Diagnose
open Lean
open VE.WireContract

/-- One registered contract: its table, its hooks and its input adapter. -/
structure Registered where
  table : Table
  hooks : Hooks
  adapter : Json → Except String Json

/-- The root of 2.1 for a contract without a named adapter: the object with exactly the members `input`, each
    the case's member of that name, or `null` when the case lacks it. -/
def caseRoot (input : List String) (case : Json) : Except String Json :=
  .ok (Json.mkObj (input.map fun name => (name, case.getObjValD name)))

def units : List (String × Registered) :=
  [("inner@0", ⟨Tables.Corpus.Inner.table, Hooks.Corpus.hooks, caseRoot ["x", "ys"]⟩),
   ("demo@0", ⟨Tables.Corpus.Demo.table, Hooks.Corpus.hooks, caseRoot ["doc"]⟩),
   ("defer@0", ⟨Tables.Corpus.Defer.table, Hooks.Corpus.hooks, caseRoot ["v", "w", "note"]⟩),
   ("mid@0", ⟨Tables.Corpus.Mid.table, Hooks.Corpus.hooks, caseRoot ["tag", "part"]⟩),
   ("forms@0", ⟨Tables.Corpus.Forms.table, Hooks.Corpus.hooks, caseRoot ["doc", "nothing"]⟩),
   ("soft-norms@0", ⟨Tables.SoftNorms.table, Hooks.SoftNorms.hooks, Hooks.SoftNorms.adapter⟩)]

/-- One row: `fault` with the record of the first instance that does not hold, or `clean`. -/
def diagnoseCase (u : Registered) (case : Json) : Json :=
  let id := case.getObjValD "id"
  match u.adapter case with
  | .error message => Json.mkObj [("id", id), ("status", .str "error"), ("error", .str message)]
  | .ok root => match run u.table u.hooks root with
    | none => Json.mkObj [("id", id), ("status", .str "ok"), ("outcome", .str "clean")]
    | some f => Json.mkObj [("id", id), ("status", .str "ok"), ("outcome", .str "fault"),
        ("diagnostic", record u.table f)]

end VE.WireContract.Diagnose
