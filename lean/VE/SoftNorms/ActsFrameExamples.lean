import VE.SoftNorms.Phases

/-! ap-1bg: the soft view of an `acts@0` norms frame (`Phases.actsFrame`: `acts@0` listed and exactly the empty strict
block), as Python's superposed readings route asks `soft-elaborate` for it, is read with its `acts` block and acts as
the norms decoder reads them; any other soft source is read as before. `VE.Readings.ActsExamples` and
`VE.Service.ActsExamples` hold the readings route's and the model mode's guards of the same view. -/

namespace VE.SoftNorms.ActsFrameExamples
open Lean

def parse (s : String) : Json := (Json.parse s).toOption.getD .null
/-- Python's empty strict block, in its key order (`readings_s1.soft_frame`). -/
def block : Json := parse "{\"parties\":[],\"ranks\":[],\"outranks\":[],\"ties\":[],\"outranking\":{\"mode\":\"strict\"}}"
def paid := "{0} to equal pay for equal work without any discrimination"
def heard := "{0} to a fair and public hearing in {1}"
def reg (role act : String) (form : Bool) : Json := Json.mkObj ([("role", .str role), ("default", .str "deny"),
  ("act", .str act)] ++ if form then [("form", .str "has the right")] else [])
def pred (args : List String) (r : Option Json) : Json :=
  Json.mkObj ([("arguments", toJson args), ("description", .str "d")] ++ r.toList.map (("regulated", ·)))
/-- A frame with `profiles` and the soft block `soft` (absent: none). With `acts`: the plain act `paid` and the
permission `heard`, each holding a fixed phrase, and the `acts` block; without: one permission with a plain act. -/
def env (profiles : List String) (soft : Option Json) (acts := true) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"), ("vocabulary", Json.mkObj ([
      ("sorts", Json.mkObj [("person", Json.mkObj [("description", .str "p")]),
        ("case", Json.mkObj [("description", .str "c")])]),
      ("constants", Json.mkObj []),
      ("predicates", Json.mkObj (if acts then [("base", pred ["person"] none),
        ("heard", pred ["person", "case"] (some (reg "permission" heard false))),
        ("paid", pred ["person"] (some (reg "plain" paid true)))] else
        [("heard", pred ["person", "case"] (some (reg "permission" "{0} be heard in {1}" false)))]))] ++
      (if acts then [("acts", Json.mkObj [("fixed", toJson ["equal pay for equal work", "a fair and public hearing"])])]
        else []) ++ soft.toList.map (("soft", ·))))]
def sfP : List String := ["acts@0", "norms@0", "relational-fol@0", "soft-norms@0"]
def err (j : Json) : String :=
  match VE.SoftNorms.Phases.checkSource j (.arr #[]) with | .ok _ => "ok" | .error f => f.message
def actsOf (j : Json) : Option (List (String × Option String)) :=
  (VE.SoftNorms.Phases.checkSource j (.arr #[])).toOption.map (·.ne.regulated.map fun r => (r.name, r.act))
def frame (j : Json) : Bool := VE.SoftNorms.Phases.actsFrame sfP (j.getObjValD "vocabulary")

-- the view is read with its acts, each as written, its profiles as listed
#guard actsOf (env sfP (some block)) == some [("heard", some heard), ("paid", some paid)]
#guard (VE.SoftNorms.Phases.checkSource (env sfP (some block)) (.arr #[])).toOption.map (·.profiles) == some sfP
-- the block is exactly the empty strict one, in any key order; any other block, or none, is not the view
#guard VE.SoftNorms.Phases.emptyBlock == block && frame (env sfP (some block))
#guard ![block.setObjVal! "parties" (toJson ["x"]), block.setObjVal! "ties" (toJson [["a", "b"]]),
  block.setObjVal! "outranking" (Json.mkObj [("mode", .str "holistic"), ("decided_by", .str "d")]),
  block.setObjVal! "exception_decider" (.str "d"), Json.mkObj []].any (frame <| env sfP <| some ·) &&
  !frame (env sfP none) && !VE.SoftNorms.Phases.actsFrame (sfP.erase "acts@0") (block.setObjVal! "x" .null)
-- outside the view the `acts` block is refused as before, and so is `acts@0` the decoder did not read
#guard [env (sfP.erase "acts@0") (some block), env sfP (some (block.setObjVal! "parties" (toJson ["x"]))),
  env sfP none].map err == List.replicate 3 "InvalidInput: invalid vocabulary"
#guard err (env sfP (some (block.setObjVal! "parties" (toJson ["x"]))) (acts := false)) ==
  "UnsupportedProfile: Unsupported profile acts@0"
#guard err (env (sfP.erase "acts@0") (some block) (acts := false)) == "ok"
-- the frame the view stands for: without `soft-norms@0` and its block; any other environment as it is
#guard VE.SoftNorms.Phases.frameView (env sfP (some block)) == env (sfP.erase "soft-norms@0") none &&
  VE.SoftNorms.Phases.frameView (env sfP none) == env sfP none

end VE.SoftNorms.ActsFrameExamples
