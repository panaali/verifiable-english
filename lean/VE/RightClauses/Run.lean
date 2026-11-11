import VE.RightClauses.ElidedBytes
import VE.Compose.Dispatch
import VE.CertificateWire

/-! The `clauses-elaborate` mode (docs/spec/right-clauses.md 8.1): the head of `right-clauses@0` on one document, in the
order of 4.1, answering with the plained document's canonical bytes, `clauseSlotLabelled` and `elided_bytes` (6: the
document total and, in `unit_elided_bytes`, one count per unit in document order; ElidedBytes.lean). -/
namespace VE.RightClauses.Run
open Lean VE.RightClauses
open VE.SoftNorms.Wire (enc)

def labelledJson (L : VE.Compose.Labelled) : Json :=
  Json.arr (L.map (fun (l, a) => Json.mkObj [("label", .str l), ("ast", enc a)])).toArray

/-- The line objects of the document's units, counted from the `lines` arrays alone, before anything is decoded. Each
    is at least one rule of `plain D`, and W1 admits 256 rules (`VE.Norms.check`, `ResourceLimit: rules`, step
    6), so a document with more is refused whatever else it holds. -/
def lineObjects (document : Json) : Nat :=
  (unitsOf document).foldl (fun k u => k + ((unitBody u).map (fun b => (bodyLines b.2).length)).getD 0) 0

/-- A line with `maxDepth` (64) or more conjuncts for `plain` to add (clauses and relation): its plain guard nests one
    `and` per conjunct, past W1's depth limit, which the rights decoder refuses in step 6 (`ResourceLimit: formula depth
    exceeds 64`). The head refuses it before it writes that guard, whose nesting grows with the request. -/
def deepLine (D : ClauseDoc) : Bool :=
  (D.lines ++ D.cands.flatMap (·.2.2.2)).any fun x =>
    x.2.2.clauses.length + x.2.2.relation.toList.length ≥ VE.Limits.maxDepth

/-- 4.1 in order: `dispatch` (its refusals are final), decoding, the head's checks on fixed lines and candidates,
    then the rights decoder and its checks on the plained document (step 6), whose texts are the answer. Output: the
    plained document's canonical bytes, `clauseSlotLabelled`, and the elided bytes of the decoded document (its total
    and each unit's), every span read once (`entryElided`). -/
def elaborateCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j ["id", "environment", "document"]
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let document ← j.getObjVal? "document"
  let route ← VE.Compose.gateOf VE.Compose.profileTable (← VE.Route.Gate.profilesOf environment)
  unless route == .clauses do throw "UnsupportedProfile: clauses-elaborate requires right-clauses@0"
  -- reading candidates under the profile (4.1 steps 2-4 for candidates, K12) are cmp-s3-cfr-1c's
  if (← VE.Route.Gate.profilesOf environment).contains "readings@1" then
    throw "UnsupportedProfile: right-clauses@0 with readings@1 is not implemented"
  -- W1's rule limit charged before the head decodes (the evaluator rule of 2026-10-27): a document of many small
  -- lines would otherwise run the head's per-line checks quadratically before step 6 refuses it
  if lineObjects document > 256 then throw "ResourceLimit: rules"
  let D ← decodeClauseDoc environment document
  checkClauses D
  checkCandidates D
  if deepLine D then throw "ResourceLimit: formula depth exceeds 64"
  let plained := elaborateJson D document
  let _ ← VE.Rights.Wire.decodeRightsSource (stripProfile environment) plained
  let es := entryElided D
  pure (VE.Route.Wire.ok id [("result", Json.mkObj [("plained", .str (← VE.CertificateWire.canonical 257 plained)),
    ("clause_slot", labelledJson (clauseSlotLabelled D)), ("elided_bytes", toJson (elidedTotal es)),
    ("unit_elided_bytes", toJson (unitElided es document))])])

def runCaseReported (j : Json) : Json :=
  match elaborateCase j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end VE.RightClauses.Run
