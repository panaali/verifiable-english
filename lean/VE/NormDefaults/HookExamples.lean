import VE.NormDefaults.Wire

/-! kb-4a: a norm-defaults document reads its source through the acts hook (`ActsHook.acts`), with its `data@0` flags
and its constants' display fields admitted, as before the hook. -/

namespace VE.NormDefaults.HookExamples
open Lean

def desc (d : String) : Json := Json.mkObj [("description", .str d)]
/-- A norm-defaults environment with a `data@0` flag (`dept`) and a constant shown by its verbalisation. -/
def ndEnv (profiles : List String := ["data@0", "norm-defaults@0", "norms@0", "relational-fol@0"]) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("person", desc "person")]),
      ("predicates", Json.mkObj [
        ("p", Json.mkObj [("arguments", toJson ["person"]), ("description", .str "d"),
          ("regulated", Json.mkObj [("role", .str "permission"), ("default", .str "allow"),
            ("act", .str "{0} seek asylum")])]),
        ("dept", Json.mkObj [("arguments", toJson ["person", "person"]), ("description", .str "d"),
          ("functional", .bool true)])]),
      ("constants", Json.mkObj [("ann", Json.mkObj [("sort", .str "person"), ("description", .str "Ann"),
        ("verbalisation", .str "Ann")])])])]
def err {α} (e : Except String α) : String := match e with | .error m => m | .ok _ => "ok"

-- the first branch (`norm-defaults@0`) admits the flag and the verbalisation; the second refuses the flag
#guard err (VE.NormDefaults.Wire.decodeSourceUWith false (ndEnv) (Json.arr #[])) == "ok"
#guard err (VE.NormDefaults.Wire.decodeSourceUWith false (ndEnv ["data@0", "norms@0", "relational-fol@0"])
  (Json.arr #[])) == "UnsupportedProfile: norms route with data flags is not implemented"

end VE.NormDefaults.HookExamples
