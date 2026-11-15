import VE.WireContract.Hooks.Acts
import VE.Acts.DecodeExamples

/-! kb-4a: the wire contract's acts hook (1.1d) reads its environment through `ActsHook.acts`, with `acts@0` read and
a joined act admitted, as before the hook. -/

namespace VE.WireContract.Hooks.HookExamples
open Lean

def desc (d : String) : Json := Json.mkObj [("description", .str d)]
def actsEnv : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson ["acts@0", "norms@0", "relational-fol@0"]),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("person", desc "person")]),
      ("predicates", Json.mkObj [("p", Json.mkObj [("arguments", toJson ["person"]), ("description", .str "d"),
        ("regulated", Json.mkObj [("role", .str "permission"), ("default", .str "allow"),
          ("act", .str "{0} seek asylum")])])]),
      ("constants", Json.mkObj [])])]

-- `acts@0` is read, and a joined act under its frames is admitted (`joined := true`)
#guard (VE.WireContract.Hooks.Acts.decoded actsEnv).isOk
#guard (VE.WireContract.Hooks.Acts.decoded (VE.Acts.DecodeExamples.envOf VE.Acts.DecodeExamples.plain6
  VE.Acts.DecodeExamples.block6 (default := "deny"))).isOk

end VE.WireContract.Hooks.HookExamples
