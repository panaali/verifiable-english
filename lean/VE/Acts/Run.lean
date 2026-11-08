import VE.Acts.Decode
import VE.Compose.Dispatch

/-! The `acts-elaborate` case kind of the `norms` and `norm-defaults` modes (act-phrases 6.7, C18): the elaborated
document of an `acts@0` case and the map from each generated part to its source, which Python binds to the request
and relays. One runner answers both modes; each passes the decoder its route reads before elaboration
(`Norms.Wire.decodeSource` with its flags, or `NormDefaults.Wire.decodeSourceU`).

The row is `ELABORATED` with the parts' declarations (`predicates`), the part rules (`rules`), the joined acts that
did not split (`kept`) and, per split source, its parts and D-28's text (`split`); or `REFUSED` with the
elaboration's diagnostic and every list empty. A refusal of the decoder itself (the act check's D-15 to D-18) is the
case's error, as on every other kind. Each list is read off `e.U'` and `e.M` once: the decoded document is bounded by
the decoder's limits (64 regulated predicates, 256 rules) and the elaboration by step 6's (6.3). -/

namespace VE.Acts.Run
open Lean VE.Acts VE.NormDefaults

def roleJson : VE.Norms.Role → Json
  | .permission => "permission"
  | .obligation => "obligation"
  | .plain => "plain"

def completionJson (U : UDoc) (r : VE.Norms.Regulated) : Json :=
  match completionOf U r with
  | .allow => "allow"
  | .deny => "deny"
  | .unspecified => "unspecified"

def optJson : Option String → Json
  | some s => .str s
  | none => .null

/-- One row per part declared in `U'`, with its source and index from `M.preds`. -/
def predicatesJson (U' : UDoc) (M : SplitMap) : Json :=
  Json.arr (U'.D.T.regulated.filterMap fun r => (M.preds.find? (·.1 == r.name)).map fun (_, p, i) =>
    Json.mkObj [("name", .str r.name), ("source", .str p), ("index", toJson i), ("sorts", toJson r.sorts),
      ("role", roleJson r.role), ("default", completionJson U' r), ("act", optJson r.act),
      ("permission", optJson r.permission)]).toArray

/-- One row per part rule in `U'`, with its source rule and index from `M.rules`. -/
def rulesJson (U' : UDoc) (M : SplitMap) : Json :=
  Json.arr (U'.D.T.nodes.filterMap fun N => (M.rules.find? (·.1 == N.name)).map fun (_, n, i) =>
    Json.mkObj [("name", .str N.name), ("source", .str n), ("index", toJson i), ("pred", .str N.pred),
      ("sign", .bool N.sign), ("guard", VE.Norms.Wire.enc N.guard),
      ("unless", Json.arr (N.carveOuts.map VE.Norms.Wire.enc).toArray), ("over", toJson N.over)]).toArray

/-- D-28: the refusal of a model, data or question that names the split source `p`. -/
def partsText (p : String) (parts : List String) : String :=
  s!"InvalidInput: name one of its parts: {p} is split into {", ".intercalate parts}"

/-- Per split source, in the map's order: its parts in index order and D-28's text. -/
def splitRows (M : SplitMap) : Json :=
  Json.arr ((M.preds.map (·.2.1)).eraseDups.map fun p =>
    let parts := (M.preds.filter (·.2.1 == p)).map (·.1)
    Json.mkObj [("source", .str p), ("parts", toJson parts), ("text", .str (partsText p parts))]).toArray

/-- The elaborated row's lists. -/
def elaboratedFields (e : VE.Acts.Decode.ElaboratedU) : List (String × Json) :=
  [("predicates", predicatesJson e.U' e.M), ("rules", rulesJson e.U' e.M),
   ("kept", toJson ((e.D.acts.map (·.1)).filter fun p => !e.M.preds.any (·.2.1 == p))),
   ("split", splitRows e.M)]

def emptyFields : List (String × Json) :=
  [("predicates", Json.arr #[]), ("rules", Json.arr #[]), ("kept", Json.arr #[]), ("split", Json.arr #[])]

/-- `acts-elaborate`: the case's source decoded by `decode`, then `elaborateSource` and `sourceOf`, as the route
that reads it runs them (6.4); the identity is the route's own (`Flagged.decodePackage`). -/
def runElaborate (decode : Json → Json → Except String VE.NormDefaults.Wire.SourceU) (j : Json) :
    Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let written ← j.getObjVal? "environment"
  let environment ← VE.Compose.decidingEnvironment written
  if (VE.Norms.Wire.actsProfiles true environment).isEmpty then
    throw "UnsupportedProfile: acts-elaborate requires acts@0"
  let s ← decode environment (j.getObjValD "norms")
  let envId ← VE.Route.Wire.environmentId s.src.ne.profiles (← VE.Norms.Wire.canonicalEnvironmentJson written)
  match VE.Acts.Decode.elaborateSource environment s >>= fun e => (VE.Acts.Decode.sourceOf e).map fun _ => e with
  | .ok e => pure (VE.Route.Wire.ok id
      ([("environment_id", .str envId), ("verdict", .str "ELABORATED")] ++ elaboratedFields e))
  | .error d => pure (VE.Route.Wire.ok id
      ([("environment_id", .str envId), ("verdict", .str "REFUSED"), ("diagnostic", .str d)] ++ emptyFields))

/-- The norms route's decoder before elaboration (`Acts.Decode.decodeElaboratedFlagged`'s first step). -/
def normsSource (environment norms : Json) : Except String VE.NormDefaults.Wire.SourceU :=
  VE.Acts.Decode.plainU <$> VE.Norms.Wire.decodeSource environment norms (flags := true)

def isElaborate (j : Json) : Bool :=
  match j.getObjValD "kind" with
  | .str k => k == "acts-elaborate"
  | _ => false

end VE.Acts.Run
