import VE.RightClauses.Wire
import VE.Compose.Dispatch
import VE.CertificateWire

/-! The `clauses-elaborate` mode (docs/spec/right-clauses.md 8.1): the head of `right-clauses@0` on one document, in the
order of 4.1, answering with the plained document's canonical bytes and `clauseSlotLabelled`. -/
namespace VE.RightClauses.Run
open Lean VE.RightClauses
open VE.SoftNorms.Wire (enc)

def labelledJson (L : VE.Compose.Labelled) : Json :=
  Json.arr (L.map (fun (l, a) => Json.mkObj [("label", .str l), ("ast", enc a)])).toArray

/-- 4.1 in order: `dispatch` (its refusals are final), decoding, the head's checks on fixed lines and candidates,
    then the rights decoder and its checks on the plained document (step 6), whose texts are the answer. Output: the
    plained document's canonical bytes and `clauseSlotLabelled`. `elided_bytes` is not computed here (cmp-s3a-cfr-3). -/
def elaborateCase (j : Json) : Except String Json := do
  VE.Bridge.exactFields j ["id", "environment", "document"]
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let document ← j.getObjVal? "document"
  let route ← VE.Compose.gateOf VE.Compose.profileTable (← VE.Route.Gate.profilesOf environment)
  unless route == .clauses do throw "UnsupportedProfile: clauses-elaborate requires right-clauses@0"
  let D ← decodeClauseDoc environment document
  checkClauses D
  checkCandidates D
  let plained := elaborateJson D document
  let _ ← VE.Rights.Wire.decodeRightsSource (stripProfile environment) plained
  pure (VE.Route.Wire.ok id [("result", Json.mkObj [("plained", .str (← VE.CertificateWire.canonical 257 plained)),
    ("clause_slot", labelledJson (clauseSlotLabelled D))])])

def runCaseReported (j : Json) : Json :=
  match elaborateCase j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end VE.RightClauses.Run
