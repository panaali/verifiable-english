import VE.Json
import VE.WireContract.Engine
import VE.WireContract.Hooks.Corpus
import VE.WireContract.Hooks.SoftNorms
import VE.WireContract.Hooks.Norms
import VE.WireContract.Hooks.NormDefaults
import VE.WireContract.Hooks.Acts
import VE.WireContract.Hooks.Purposes
import VE.WireContract.Limits
import VE.WireContract.Names

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

/-- One registered contract: its table, the hooks of one run on an input, and its input adapter. A unit whose
    hooks read a value of the whole input per item (4.7's environment, at every rule) builds it once per run there
    (ap-1bfb review F2); they give what the unit's `hooks` give (the `#guard`s of `Hooks.Acts`). -/
structure Registered where
  table : Table
  hooks : Json → Hooks
  adapter : Json → Except String Json

/-- The root of 2.1 for a contract without a named adapter: the object with exactly the members `input`, each
    the case's member of that name, or `null` when the case lacks it. -/
def caseRoot (input : List String) (case : Json) : Except String Json :=
  .ok (Json.mkObj (input.map fun name => (name, case.getObjValD name)))

/-- A unit's hooks that read no value of the whole input per item: the same on every input. -/
local instance : Coe Hooks (Json → Hooks) := ⟨fun h _ => h⟩

def units : List (String × Registered) :=
  [("inner@0", ⟨Tables.Corpus.Inner.table, Hooks.Corpus.hooks, caseRoot ["x", "ys"]⟩),
   ("demo@0", ⟨Tables.Corpus.Demo.table, Hooks.Corpus.hooks, caseRoot ["doc"]⟩),
   ("defer@0", ⟨Tables.Corpus.Defer.table, Hooks.Corpus.hooks, caseRoot ["v", "w", "note"]⟩),
   ("mid@0", ⟨Tables.Corpus.Mid.table, Hooks.Corpus.hooks, caseRoot ["tag", "part"]⟩),
   ("forms@0", ⟨Tables.Corpus.Forms.table, Hooks.Corpus.hooks, caseRoot ["doc", "nothing"]⟩),
   ("soft-norms@0", ⟨Tables.SoftNorms.table, Hooks.SoftNorms.hooksFor, Hooks.SoftNorms.adapter⟩)]
  ++ [("norms@0", ⟨Tables.Norms.table, Hooks.Norms.hooksFor, Hooks.Norms.adapter⟩),
      ("norm-defaults@0", ⟨Tables.NormDefaults.table, Hooks.NormDefaults.hooksFor, Hooks.NormDefaults.adapter⟩),
      ("acts@0", ⟨Tables.Acts.table, Hooks.Acts.hooksFor, Hooks.Acts.adapter⟩),
      ("purposes@0", ⟨Tables.Purposes.table, Hooks.Purposes.hooks, Hooks.Purposes.adapter⟩)]

-- every unit once, in order; `acts@0`'s and `purposes@0`'s rows read their own table, hooks and adapter
#guard units.map (·.1) == ["inner@0", "demo@0", "defer@0", "mid@0", "forms@0", "soft-norms@0", "norms@0",
  "norm-defaults@0", "acts@0", "purposes@0"]
#guard match units.lookup "purposes@0" with
  | some r => r.table.contract == "purposes@0" &&
      let j := (r.adapter (Json.mkObj [("purposes", Json.null)])).toOption.getD .null
      (run r.table (r.hooks j) j).isSome
  | none => false
#guard match units.lookup "acts@0" with
  | some r => r.table.contract == "acts@0" && (r.adapter (Hooks.Acts.caseOf "norms-elaborate" ["acts@0", "norms@0"])).isOk &&
      let j := Json.mkObj [("environment", Hooks.Acts.envOf [] "{0} seek and enjoy asylum")]
      (run r.table (r.hooks j) j).isSome
  | none => false

/-- One row: `fault` with the record of the first instance that does not hold, or `clean`. -/
def diagnoseCase (u : Registered) (case : Json) : Json :=
  let id := case.getObjValD "id"
  match u.adapter case with
  | .error message => Json.mkObj [("id", id), ("status", .str "error"), ("error", .str message)]
  | .ok root => match run u.table (u.hooks root) root with
    | none => Json.mkObj [("id", id), ("status", .str "ok"), ("outcome", .str "clean")]
    | some f => Json.mkObj [("id", id), ("status", .str "ok"), ("outcome", .str "fault"),
        ("diagnostic", record u.table f)]

end VE.WireContract.Diagnose
