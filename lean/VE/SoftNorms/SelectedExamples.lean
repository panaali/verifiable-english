import VE.SoftNorms.SelectedSound
import VE.SoftNorms.Prepared

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

/-! The spec functions themselves, on the decoded source and model (the runner reads one expansion
per case, `selectedRow_eq`; these read `circ` directly). -/

/-- `selectedAt` and `outcomeAt` of `p` at the one-entity tuple `t`, or `none` if a decoder refuses. -/
def specAt (default excepted p t : String) (norms : String := normsText) (model : String := modelText excepted) :
    Option (List String × Bool) :=
  match VE.SoftNorms.Wire.decodeSoftSource (parsed (environmentText default)) (parsed norms) with
  | .error _ => none
  | .ok src =>
    match VE.SoftNorms.Wire.decodeModel src (Json.mkObj [("model", parsed model)]) with
    | .error _ => none
    | .ok ⟨M, _⟩ => some (selectedAt src.D M p [("assistant", t)], outcomeAt src.D M p [("assistant", t)])

#guard specAt "deny" r#"[["a"], ["e"]]"# "x_required" "a" == some (["o"], false)
#guard specAt "deny" r#"[["a"], ["e"]]"# "x_required" "b" == some (["h"], true)
#guard specAt "deny" r#"[["a"], ["e"]]"# "x_required" "c" == some (["d"], true)
#guard specAt "deny" r#"[["a"], ["e"]]"# "x_required" "e" == some ([], false)
#guard specAt "allow" r#"[["a"], ["e"]]"# "x_required" "e" == some ([], true)
#guard specAt "deny" r#"[["e"]]"# "x_required" "a" == some (["d"], true)
/-- Two strict rules on `x_required` with the same guard `v`: both select at `b`, in rule order. -/
def twoStrictText : String :=
  r#"[{"norm": {"name": "h", "predicate": "x_required", "sign": true, "guard": ["unary", "v", ["var", 0]], "unless": [], "over": []}}, {"norm": {"name": "h2", "predicate": "x_required", "sign": true, "guard": ["unary", "v", ["var", 0]], "unless": [], "over": []}}]"#

def twoStrictModel : String :=
  r#"{"complete": true, "domains": {"assistant": ["a", "b"], "user": []}, "constants": {}, "relations": {"v": [["b"]], "w": [], "s": []}}"#

#guard specAt "deny" "" "x_required" "b" twoStrictText twoStrictModel == some (["h", "h2"], true)
#guard specAt "deny" "" "x_required" "a" twoStrictText twoStrictModel == some ([], false)
#guard answerOf (Json.mkObj [("id", .str "s"), ("kind", .str "soft-selected"),
    ("environment", parsed (environmentText "deny")), ("norms", parsed twoStrictText),
    ("model", parsed twoStrictModel),
    ("queries", parsed r#"[{"predicate": "x_required", "tuple": ["b"]}]"#)]) ==
  "{\"background\":true,\"id\":\"s\",\"results\":[{\"outcome\":true,\"predicate\":\"x_required\",\"selected\":[\"h\",\"h2\"],\"tuple\":[\"b\"]}],\"status\":\"ok\"}"
-- No rule on `x_permitted`: nothing selected, its default (allow) decides.
#guard specAt "deny" r#"[["a"], ["e"]]"# "x_permitted" "a" == some ([], true)

/-! ## Facts and coherence (kb-9)

The same document and model with a `facts` member: `v(b)` makes the first fact true, and `w` fails
at `b`, so the second is false. The answer reports `facts: false` and still reports every selected
rule; `coherent` is reported beside it. -/

def factTrue : String := r#"["exists", "assistant", ["unary", "v", ["var", 0]]]"#
def factFalse : String := r#"["forall", "assistant", ["unary", "w", ["var", 0]]]"#

def factsCase (facts : String) (norms : String := normsText) (model : String := modelText r#"[["a"], ["e"]]"#)
    (queries : String := queriesText) : Json :=
  Json.mkObj [("id", .str "s"), ("kind", .str "soft-selected"), ("environment", parsed (environmentText "deny")),
    ("norms", parsed norms), ("model", parsed model), ("queries", parsed queries), ("facts", parsed facts)]

-- One true and one false fact: `facts: false`, the selected rules unchanged.
#guard answerOf (factsCase ("[" ++ factTrue ++ ", " ++ factFalse ++ "]")) ==
  "{\"background\":true,\"coherent\":true,\"facts\":false,\"id\":\"s\",\"results\":" ++ resultsText "false" ++
    ",\"status\":\"ok\"}"
-- The true fact alone: `facts: true`; with `background` and `coherent` true, `selected_model_admissible` applies.
#guard answerOf (factsCase ("[" ++ factTrue ++ "]")) ==
  "{\"background\":true,\"coherent\":true,\"facts\":true,\"id\":\"s\",\"results\":" ++ resultsText "false" ++
    ",\"status\":\"ok\"}"
-- An empty `facts` was sent: both fields are reported.
#guard answerOf (factsCase "[]") ==
  "{\"background\":true,\"coherent\":true,\"facts\":true,\"id\":\"s\",\"results\":" ++ resultsText "false" ++
    ",\"status\":\"ok\"}"
-- The slot kinds' refusals: an open or ill-typed fact, a decision predicate, a non-array.
#guard answerOf (factsCase r#"[["unary", "v", ["var", 0]]]"#) == "error: ill-typed or unbound formula"
#guard answerOf (factsCase r#"[["exists", "assistant", ["unary", "x_required", ["var", 0]]]]"#) ==
  "error: ill-typed or unbound formula"
#guard answerOf (factsCase r#"[["exists", "assistant", ["unary", "soft__excepted__d", ["var", 0]]]]"#) ==
  "error: InvalidInput: facts: soft__excepted__d is a soft decision predicate; its decider decides it, not a fact"
#guard answerOf (factsCase r#"{"a": 1}"#) == "error: InvalidInput: facts must be an array"

/-- Two unranked default rules of opposite sign: a colliding pair, one coherence conjunct. -/
def collidingText : String :=
  r#"[{"norm": {"name": "p", "predicate": "x_required", "sign": true, "guard": ["unary", "v", ["var", 0]], "unless": [], "over": [], "mode": "default", "exception": {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}}}, {"norm": {"name": "q", "predicate": "x_required", "sign": false, "guard": ["unary", "w", ["var", 0]], "unless": [], "over": [], "mode": "default", "exception": {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}}}]"#

def collidingModel : String :=
  r#"{"complete": true, "domains": {"assistant": ["a", "b"], "user": []}, "constants": {}, "relations": {"v": [["a"], ["b"]], "w": [["a"]], "s": [], "soft__excepted__p": [], "soft__excepted__q": []}}"#

-- Both rules select at `a`: `coherent: false`, and both are still reported (kb-10/SPEC.md 4.1).
#guard answerOf (factsCase "[]" collidingText collidingModel
    r#"[{"predicate": "x_required", "tuple": ["a"]}, {"predicate": "x_required", "tuple": ["b"]}]"#) ==
  "{\"background\":true,\"coherent\":false,\"facts\":true,\"id\":\"s\",\"results\":[{\"outcome\":true,\"predicate\":\"x_required\",\"selected\":[\"p\",\"q\"],\"tuple\":[\"a\"]},{\"outcome\":true,\"predicate\":\"x_required\",\"selected\":[\"p\"],\"tuple\":[\"b\"]}],\"status\":\"ok\"}"

/-! Each flag reads every fact and every conjunct, in any position, and the prepared runner answers as the
runner does (the checks the trust mutants of `factsAt`, `coherentAt`, `cohPremisesIn` and `decodeFactsIn`
are refuted by). -/

/-- The prepared path's answer (`prepare` then `runSelectedP`), compressed, or the refusal. -/
def answerOfP (j : Json) : String :=
  match prepare (j.getObjValD "environment") (j.getObjValD "norms") with
  | .error e => "error: " ++ e
  | .ok p => match runSelectedP p "s" j with
    | .ok a => a.compress
    | .error e => "error: " ++ e

-- The false fact first: `facts: false` (and last, above).
#guard (answerOf (factsCase ("[" ++ factFalse ++ ", " ++ factTrue ++ "]"))).startsWith
  "{\"background\":true,\"coherent\":true,\"facts\":false,"

def exceptionText : String :=
  r#""mode": "default", "exception": {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}"#

/-- Three unranked default rules: `p` (guard `v`) collides with `q` (guard `w`) and with `r` (guard `s`): two
coherence conjuncts, for the pairs (p, q) and (p, r) in that order. -/
def threeText : String :=
  "[{\"norm\": {\"name\": \"p\", \"predicate\": \"x_required\", \"sign\": true, \"guard\": [\"unary\", \"v\", [\"var\", 0]], \"unless\": [], \"over\": [], " ++ exceptionText ++ "}}, " ++
  "{\"norm\": {\"name\": \"q\", \"predicate\": \"x_required\", \"sign\": false, \"guard\": [\"unary\", \"w\", [\"var\", 0]], \"unless\": [], \"over\": [], " ++ exceptionText ++ "}}, " ++
  "{\"norm\": {\"name\": \"r\", \"predicate\": \"x_required\", \"sign\": false, \"guard\": [\"unary\", \"s\", [\"var\", 0]], \"unless\": [], \"over\": [], " ++ exceptionText ++ "}}]"

def threeModel (v w s : String) : String :=
  "{\"complete\": true, \"domains\": {\"assistant\": [\"a\"], \"user\": []}, \"constants\": {}, \"relations\": {\"v\": " ++ v ++ ", \"w\": " ++ w ++ ", \"s\": " ++ s ++ ", \"soft__excepted__p\": [], \"soft__excepted__q\": [], \"soft__excepted__r\": []}}"

def atA : String := r#"[{"predicate": "x_required", "tuple": ["a"]}]"#

/-- The (p, q) conjunct alone fails, the (p, r) conjunct alone fails, or neither. -/
def firstFails : Json := factsCase "[]" threeText (threeModel r#"[["a"]]"# r#"[["a"]]"# "[]") atA
def lastFails : Json := factsCase "[]" threeText (threeModel r#"[["a"]]"# "[]" r#"[["a"]]"#) atA
def noneFails : Json := factsCase "[]" threeText (threeModel r#"[["a"]]"# "[]" "[]") atA

#guard (answerOf firstFails).startsWith "{\"background\":true,\"coherent\":false,"
#guard (answerOf lastFails).startsWith "{\"background\":true,\"coherent\":false,"
#guard (answerOf noneFails).startsWith "{\"background\":true,\"coherent\":true,"

-- The prepared runner: the same answers, refusals included.
#guard [firstFails, lastFails, noneFails, factsCase ("[" ++ factFalse ++ ", " ++ factTrue ++ "]"),
    factsCase ("[" ++ factTrue ++ ", " ++ factFalse ++ "]"), factsCase "[]", selectedCase "deny" r#"[["a"], ["e"]]"# queriesText,
    factsCase r#"[["exists", "assistant", ["unary", "soft__excepted__o", ["var", 0]]]]"#].all
  fun j => answerOfP j == answerOf j

-- A decision predicate is refused wherever it is: the last decision name, and either position in the list.
def decisionFact (name : String) : String := "[\"exists\", \"assistant\", [\"unary\", \"" ++ name ++ "\", [\"var\", 0]]]"
#guard answerOf (factsCase ("[" ++ decisionFact "soft__excepted__o" ++ "]")) ==
  "error: InvalidInput: facts: soft__excepted__o is a soft decision predicate; its decider decides it, not a fact"
#guard answerOf (factsCase ("[" ++ factTrue ++ ", " ++ decisionFact "soft__excepted__d" ++ "]")) ==
  "error: InvalidInput: facts: soft__excepted__d is a soft decision predicate; its decider decides it, not a fact"
#guard answerOf (factsCase ("[" ++ decisionFact "soft__excepted__d" ++ ", " ++ factTrue ++ "]")) ==
  "error: InvalidInput: facts: soft__excepted__d is a soft decision predicate; its decider decides it, not a fact"

/-- Review kb-9 F2: `SelectedAnswer` cannot see the case, so it admits no flag field and also both
flag fields with any `facts` value; only `soft_wire_selected_facts` ties them to the case's `facts`. -/
example (id : String) (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) (qs : List SelectedQuery)
    (b : Bool) (answer : Json) (h : SelectedAnswerWith id D M qs (factsFields true b (coherentAt D M)) answer) :
    SelectedAnswer id D M qs answer := ⟨true, b, h⟩

example (id : String) (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) (qs : List SelectedQuery)
    (answer : Json) (h : SelectedAnswerWith id D M qs [] answer) : SelectedAnswer id D M qs answer :=
  ⟨false, false, h⟩

end VE.SoftNorms.SelectedExamples
