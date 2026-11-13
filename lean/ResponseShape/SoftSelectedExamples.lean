import ResponseShape.DefaultsExamples
import VE.SoftNorms.SelectedExamples

/-! The `soft-selected` rows of `soft-norms.json` (`Schemas.SoftNorms.selected`) on the mode's own answers to the
kind's fixtures (`VE/SoftNorms/SelectedExamples.lean`): every answer and refusal is accepted, and an answer with a
member added, dropped or retyped, a flag or outcome retyped, or a result not bound to its query is refused. -/
namespace ResponseShape.SoftSelectedExamples
open Lean VE.SoftNorms.SelectedExamples
open ResponseShape.DefaultsExamples (variants)

def accepts (j a : Json) : Bool :=
  (ResponseShape.decide Schemas.files (.ref "soft-norms.json#/row") { value := j } a).toOption.isSome
def run (j : Json) : Json := VE.SoftNorms.Run.runCaseReported j

/-- The answer `a` with field `k` of its `i`-th result set to `v`. -/
def setResult (a : Json) (i : Nat) (k : String) (v : Json) : Json :=
  match a.getObjValD "results" with
  | .arr rs => a.setObjVal! "results" (.arr (rs.modify i (·.setObjVal! k v)))
  | _ => a

def deny : Json := selectedCase "deny" r#"[["a"], ["e"]]"# queriesText
def allow : Json := selectedCase "allow" r#"[["a"], ["e"]]"# queriesText
def violating : Json := selectedCase "deny" r#"[["e"]]"# r#"[{"predicate": "x_required", "tuple": ["a"]}]"#
def refused : List Json := [selectedCase "deny" r#"[["a"]]"# r#"[{"predicate": "nope", "tuple": ["a"]}]"#,
  selectedCase "deny" r#"[["a"]]"# r#"[{"predicate": "x_required", "tuple": ["zz"]}]"#, selectedCase "deny" r#"[["a"]]"# "[]"]

-- accepted: both defaults, a model that fails the soft background, and each refusal (the mode's error row)
#guard [deny, allow, violating].all fun j => accepts j (run j)
#guard refused.all fun j => (run j).getObjValD "status" == .str "error" && accepts j (run j)
-- refused: every variant of each answer (a member added or dropped, an object, array or leaf retyped)
#guard [deny, violating].all fun j => (variants [] 6 (run j)).all (!accepts j ·)
-- refused: a flag or an outcome retyped, a result not its query's (predicate, tuple, order, count)
#guard let a := run deny; let rs := (a.getObjValD "results").getArr?.toOption.getD #[]
  [a.setObjVal! "background" (.str "true"), setResult a 0 "outcome" (.str "false"),
    setResult a 0 "tuple" (toJson ["b"]), setResult a 1 "tuple" (toJson ["b", "b"]),
    setResult a 0 "predicate" (.str "x_permitted"), setResult a 0 "selected" (.str "o"),
    a.setObjVal! "results" (.arr rs.reverse), a.setObjVal! "results" (.arr rs.pop),
    a.setObjVal! "results" (.arr (rs.push rs[0]!)), a.setObjVal! "results" (.arr #[])].all (!accepts deny ·)
-- refused: an `ok` row with no result, for a request whose `queries` is empty (Lean refuses that request)
#guard let j := selectedCase "deny" r#"[["a"]]"# "[]"
  !accepts j ((run deny).setObjVal! "id" (.str "s") |>.setObjVal! "results" (.arr #[]))
-- the mode's other rows on the same source: a soft-conflict over packages and with a witness, a case off the soft
-- path (the norms mode's row), and the service's own rejection of a case at its position
#guard let src := (selectedCase "deny" r#"[["a"], ["e"]]"# "[]").setObjVal! "kind" (.str "soft-conflict")
  let packages := src.setObjVal! "packages" (Json.mkObj [])
  let witness := src.setObjVal! "witness" (Json.mkObj [("target", .str "x_required->x_permitted"),
    ("model", parsed (modelText r#"[["a"], ["e"]]"#)), ("tuple", toJson ["a"])])
  let off := Json.mkObj [("id", .str "n"), ("kind", .str "norms-conflict")]
  [packages, witness, off].all (fun j => accepts j (run j)) &&
  (run packages).getObjValD "verdict" == .str "UNKNOWN" && (run witness).getObjValD "target" == .str "x_required->x_permitted"
#guard (ResponseShape.decide Schemas.files (.ref "soft-norms.json#/row") { value := deny, index := some 0 }
  (Json.mkObj [("status", .str "error"), ("case_index", toJson (0 : Nat)), ("error", .str "bad case")])).toOption.isSome
-- the genuine row with the other default's outcomes is still a well-typed, bound row (the shape does not decide
-- outcomes: `soft_wire_selected` does)
#guard accepts deny (run allow |>.setObjVal! "id" (.str "s"))

end ResponseShape.SoftSelectedExamples
