import VE.Alternatives.Wire

/-! kb-4a: the alternatives route's other declarations read their norms environment through the acts hook
(`ActsHook.acts`), with its `data@0` flags admitted, as before the hook. -/

namespace VE.Alternatives.HookExamples
open Lean

def desc (d : String) : Json := Json.mkObj [("description", .str d)]
/-- A norms environment with a `data@0` flag (`dept`, functional) beside one permission. -/
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

-- the environment scope admits the flags; the document scope refuses them
#guard match VE.Norms.Wire.decodeNormsEnvironmentWith VE.Norms.Wire.ActsHook.plain flaggedEnv with
  | .ok ne => (VE.Alternatives.Wire.otherDeclarations .environment flaggedEnv ne).isOk &&
      !(VE.Alternatives.Wire.otherDeclarations .document flaggedEnv ne).isOk
  | .error _ => false

end VE.Alternatives.HookExamples
