import VE.Kernel.Carry

/-! Checks of the carry rule's definitions (`VE.Kernel.Carry`, docs/spec/kernel-boundary.md section 3),
evaluated on a toy kernel path: its rows, a shell over it and the plain fold `carry`, each compared with
the exact answer it must give (the JSON text, keys in `Json.mkObj`'s order). -/
namespace VE.Kernel.CarryChecks
open Lean VE.Kernel

/-- A toy runner: a number is answered with its successor; anything else is refused. -/
def toyRun (case : Json) : Except String Json :=
  match case.getNat? with
  | .ok n => .ok (toJson (n + 1))
  | .error _ => .error "not a number"

/-- The toy kernel path: an answer means what the runner returned. -/
def toy : Path := ⟨toyRun, fun case answer => toyRun case = .ok answer, fun _ _ h => h⟩

/-- A toy elaboration: an array request is its cases; anything else is refused. -/
def cases (request : Json) : Except String (List Json) :=
  match request.getArr? with
  | .ok xs => .ok xs.toList
  | .error _ => .error "not a list"

/-- An answer's text, or the refusal's under `error:`. -/
def text : Except String Json → String
  | .ok a => a.compress
  | .error e => "error:" ++ e

-- `Path.row`: the case, and the path's own result for it.
#guard (toy.row (toJson 1)).case.compress == "1"
#guard text (toy.row (toJson 1)).result == "2"
#guard text (toy.row (Json.str "a")).result == "error:not a number"

-- `carry`: the view under `view`, the rows verbatim and in order under `rows`, an answer under `answer` and a
-- refusal under `refused`.
#guard (carry (fun _ => Json.str "v") Json.null []).compress == "{\"rows\":[],\"view\":\"v\"}"
#guard (carry (fun r => r) (toJson 7) [⟨toJson 1, .ok (toJson 2)⟩, ⟨Json.str "a", .error "no"⟩,
    ⟨toJson 3, .ok (toJson 4)⟩]).compress ==
  "{\"rows\":[{\"answer\":2,\"case\":1},{\"case\":\"a\",\"refused\":\"no\"},{\"answer\":4,\"case\":3}],\"view\":7}"

-- `shell`: the fold of the path's rows for every elaborated case, in order; a refused elaboration is refused.
#guard text (shell toy cases (carry fun _ => Json.null) (Json.arr #[toJson 1, Json.str "a", toJson 5])) ==
  "{\"rows\":[{\"answer\":2,\"case\":1},{\"case\":\"a\",\"refused\":\"not a number\"},{\"answer\":6,\"case\":5}]," ++
  "\"view\":null}"
#guard text (shell toy cases (carry fun r => r) (Json.arr #[])) == "{\"rows\":[],\"view\":[]}"
#guard text (shell toy cases (carry fun r => r) (Json.str "x")) == "error:not a list"
#guard text (shell toy cases (fun request rows => toJson [request, toJson rows.length]) (Json.arr #[toJson 0])) ==
  "[[0],1]"

end VE.Kernel.CarryChecks
