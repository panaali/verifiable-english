import VE.Service.FamilyNorms

/-! kb-4a: the family norms route decodes its FOL view through the acts hook (`ActsHook.acts`), with its `data@0`
flags admitted, as before the hook. -/

namespace VE.Service.HookExamples
open Lean

def desc (d : String) : Json := Json.mkObj [("description", .str d)]
def flaggedEnv : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson ["data@0", "norms@0", "relational-fol@0"]),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("person", desc "person")]),
      ("predicates", Json.mkObj [
        ("p", Json.mkObj [("arguments", toJson ["person"]), ("description", .str "d"),
          ("regulated", Json.mkObj [("role", .str "permission"), ("default", .str "allow"),
            ("act", .str "{0} seek asylum")])]),
        ("dept", Json.mkObj [("arguments", toJson ["person", "person"]), ("description", .str "d"),
          ("functional", .bool true)])]),
      ("constants", Json.mkObj [])])]
def err {α} (e : Except String α) : String := match e with | .error m => m | .ok _ => "ok"
def caseOf (kind : String) : Json :=
  Json.mkObj [("id", .str "c"), ("kind", .str kind), ("environment", flaggedEnv), ("norms", Json.arr #[])]
def flagRefusal : String := "UnsupportedProfile: norms route with data flags is not implemented"

-- both decodes of `folCase` admit the flag: `norms-elaborate`, and a `norms-conflict` without a witness
#guard err (VE.Service.FamilyNorms.folCase (caseOf "norms-elaborate")) == "ok"
#guard err (VE.Service.FamilyNorms.folCase (caseOf "norms-conflict")) != flagRefusal
#guard err (VE.Service.FamilyNorms.folCase (caseOf "norms-conflict")) != "UnsupportedProfile: Unsupported profile data@0"

end VE.Service.HookExamples
