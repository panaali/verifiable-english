import VE.SoftNorms.SelectedSound

/-! Examples of the `soft-selected` kind (kb-10a) on the three-rule document of
tests/test_soft_selected.py: a strict rule `h` (guard `v`), a default rule `d` whose exception
(sufficient condition `s`) holds at `a` and `e`, and a default rule `o` of the other sign (guard `w`)
that `d` overrides. At `a` only `o` selects; at `b` the strict rule blocks both defaults; at `c` `d`
selects and overrides `o`; at `e` nothing selects and the predicate's default decides. -/
namespace VE.SoftNorms.SelectedExamples
open Lean VE.SoftNorms.Run

def environmentText (default : String) : String :=
  r#"{"language": "ve.core@0.2", "profiles": ["norms@0", "relational-fol@0", "soft-norms@0"], "spec_revision": "ve-v0.2-expand2-2026-09-25", "vocabulary": {"sorts": {"assistant": {"description": "assistant"}, "user": {"description": "user"}}, "predicates": {"x_required": {"arguments": ["assistant"], "description": "obligation", "regulated": {"role": "obligation", "default": ""# ++
  default ++
  r#"", "act": "{0} do x", "permission": "x_permitted"}}, "x_permitted": {"arguments": ["assistant"], "description": "permission", "regulated": {"role": "permission", "default": "allow", "act": "{0} do x"}}, "v": {"arguments": ["assistant"], "description": "v"}, "w": {"arguments": ["assistant"], "description": "w"}, "s": {"arguments": ["assistant"], "description": "s"}}, "constants": {}}}"#

def normsText : String :=
  r#"[{"norm": {"name": "h", "predicate": "x_required", "sign": true, "guard": ["unary", "v", ["var", 0]], "unless": [], "over": []}}, {"norm": {"name": "d", "predicate": "x_required", "sign": true, "guard": ["top"], "unless": [], "over": ["o"], "mode": "default", "exception": {"decided_by": "assistant", "sufficient": [["unary", "s", ["var", 0]]], "necessary": [], "factors": []}}}, {"norm": {"name": "o", "predicate": "x_required", "sign": false, "guard": ["unary", "w", ["var", 0]], "unless": [], "over": [], "mode": "default", "exception": {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}}}]"#

/-- The model; `excepted` lists the tuples where `d`'s decision predicate holds. -/
def modelText (excepted : String) : String :=
  r#"{"complete": true, "domains": {"assistant": ["a", "b", "c", "e"], "user": []}, "constants": {}, "relations": {"v": [["b"]], "w": [["a"], ["c"]], "s": [["a"], ["e"]], "soft__excepted__o": [], "soft__excepted__d": "# ++
  excepted ++ "}}"

def queriesText : String :=
  r#"[{"predicate": "x_required", "tuple": ["a"]}, {"predicate": "x_required", "tuple": ["b"]}, {"predicate": "x_required", "tuple": ["c"]}, {"predicate": "x_required", "tuple": ["e"]}]"#

def parsed (text : String) : Json := (Json.parse text).toOption.getD .null

def selectedCase (default excepted queries : String) : Json :=
  Json.mkObj [("id", .str "s"), ("kind", .str "soft-selected"), ("environment", parsed (environmentText default)),
    ("norms", parsed normsText), ("model", parsed (modelText excepted)), ("queries", parsed queries)]

/-- The answer, compressed, or the refusal. -/
def answerOf (j : Json) : String :=
  match runCase j with
  | .ok a => a.compress
  | .error e => "error: " ++ e

def resultsText (outcomeAtE : String) : String :=
  "[{\"outcome\":false,\"predicate\":\"x_required\",\"selected\":[\"o\"],\"tuple\":[\"a\"]}," ++
  "{\"outcome\":true,\"predicate\":\"x_required\",\"selected\":[\"h\"],\"tuple\":[\"b\"]}," ++
  "{\"outcome\":true,\"predicate\":\"x_required\",\"selected\":[\"d\"],\"tuple\":[\"c\"]}," ++
  "{\"outcome\":" ++ outcomeAtE ++ ",\"predicate\":\"x_required\",\"selected\":[],\"tuple\":[\"e\"]}]"

-- Default deny: at `e` nothing selects and the outcome is false.
#guard answerOf (selectedCase "deny" r#"[["a"], ["e"]]"# queriesText) ==
  "{\"background\":true,\"id\":\"s\",\"results\":" ++ resultsText "false" ++ ",\"status\":\"ok\"}"
-- Default allow: the same selections; at `e` the outcome is true.
#guard answerOf (selectedCase "allow" r#"[["a"], ["e"]]"# queriesText) ==
  "{\"background\":true,\"id\":\"s\",\"results\":" ++ resultsText "true" ++ ",\"status\":\"ok\"}"
-- `s(a)` without `d`'s decision at `a` violates the exception premise: answered, `background: false`.
#guard answerOf (selectedCase "deny" r#"[["e"]]"# r#"[{"predicate": "x_required", "tuple": ["a"]}]"#) ==
  "{\"background\":false,\"id\":\"s\",\"results\":[{\"outcome\":true,\"predicate\":\"x_required\",\"selected\":[\"d\"],\"tuple\":[\"a\"]}],\"status\":\"ok\"}"
-- Refusals, each naming the query.
#guard answerOf (selectedCase "deny" r#"[["a"]]"# r#"[{"predicate": "nope", "tuple": ["a"]}]"#) ==
  "error: InvalidInput: query 0: nope is not a regulated predicate of the source"
#guard answerOf (selectedCase "deny" r#"[["a"]]"# r#"[{"predicate": "x_required", "tuple": ["a"]}, {"predicate": "x_required", "tuple": ["zz"]}]"#) ==
  "error: InvalidInput: query 1: tuple has the wrong length or sort for x_required"
#guard answerOf (selectedCase "deny" r#"[["a"]]"# "[]") ==
  "error: InvalidInput: soft-selected needs at least one query"

end VE.SoftNorms.SelectedExamples
