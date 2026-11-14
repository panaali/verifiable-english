-- ve-layer: 4 (examples of the metered wire theorems, which they import)
import VE.Route.MeteredWire

/-! Examples of the norms profile check on the `metered` path (kb-validators, decision D13), on the
environment of tests/test_metered_profile.py: one obligation `required` whose permission dual is
`permitted`, over the sort `point` (`a`, `b`). A model whose `required` holds a tuple `permitted`
does not is refused by `metered` on every family and both case kinds, with the `model` mode's own
diagnostic; a model within its permission, or one without a declared pair, is answered. -/
namespace VE.Route.MeteredProfileExamples
open Lean

def diagnostic : String :=
  "InvalidModel(profile): required relation required exceeds permission permitted"

def environmentText (profiles : String) (regulated : Bool) : String :=
  let permitted := if regulated then
    r#", "regulated": {"role": "permission", "default": "deny", "act": "{0} be done"}"# else ""
  let required := if regulated then
    r#", "regulated": {"role": "obligation", "default": "deny", "act": "{0} be done", "permission": "permitted"}"#
    else ""
  r#"{"language": "ve.core@0.2", "profiles": "# ++ profiles ++
  r#", "spec_revision": "ve-v0.2-expand2-2026-09-25", "vocabulary": {"sorts": {"point": {"description": "point"}}, "constants": {}, "predicates": {"upper": {"arguments": ["point"], "description": "upper"}, "permitted": {"arguments": ["point"], "description": "permission""# ++
  permitted ++ r#"}, "required": {"arguments": ["point"], "description": "obligation""# ++ required ++ "}}}}"

def modelText (required permitted : String) : String :=
  r#"{"complete": true, "domains": {"point": ["a", "b"]}, "constants": {}, "relations": {"upper": [["a"]], "required": "# ++
  required ++ r#", "permitted": "# ++ permitted ++ "}}"

def parsed (text : String) : Json := (Json.parse text).toOption.getD .null

def fol : String := r#"["norms@0", "relational-fol@0"]"#
def closure : String := r#"["closure@0", "norms@0", "relational-fol@0"]"#
def nary : String := r#"["closure@0", "nary@0", "norms@0", "relational-fol@0"]"#
def order : String := r#"["norms@0", "order@0", "relational-fol@0"]"#

def formula : Json := parsed r#"["forall", "point", ["unary", "upper", ["var", 0]]]"#

def meteredCase (profiles : String) (regulated : Bool) (required permitted kind : String) : Json :=
  Json.mkObj [("id", .str "e"), ("kind", .str kind), ("environment", parsed (environmentText profiles regulated)),
    ("model", parsed (modelText required permitted)), ("ast", .arr #[formula]), ("formula", formula),
    ("max_evaluations", toJson (1000 : Nat))]

/-- The refusal of a case, or none when it is answered. -/
def refusal (j : Json) : Option String :=
  match VE.Route.MeteredRun.runCase j with
  | .ok _ => none
  | .error e => some e

/-- An answered `evaluate-budgeted` case's value. -/
def value (j : Json) : Option Json :=
  match VE.Route.MeteredRun.runCase j with
  | .ok a => some ((a.getObjValD "evaluation").getObjValD "value")
  | .error _ => none

def families : List String := [fol, closure, nary, order]
def kinds : List String := ["evaluate-budgeted", "non-vacuity"]
/-- Required beyond permission: the only tuple, one of two, a different tuple. -/
def beyond : List (String × String) :=
  [("[[\"a\"]]", "[]"), ("[[\"a\"], [\"b\"]]", "[[\"a\"]]"), ("[[\"b\"]]", "[[\"a\"]]")]
/-- Within: a proper part, equal in another order, both empty, required empty. -/
def within : List (String × String) :=
  [("[[\"a\"]]", "[[\"a\"], [\"b\"]]"), ("[[\"a\"], [\"b\"]]", "[[\"b\"], [\"a\"]]"), ("[]", "[]"), ("[]", "[[\"b\"]]")]

-- Every family and kind refuses a model beyond its permission with the model mode's diagnostic.
#guard families.all fun f => kinds.all fun k => beyond.all fun (r, p) =>
  refusal (meteredCase f true r p k) == some diagnostic
-- and answers a model within it.
#guard families.all fun f => kinds.all fun k => within.all fun (r, p) =>
  refusal (meteredCase f true r p k) == none
#guard families.all fun f => within.all fun (r, p) =>
  value (meteredCase f true r p "evaluate-budgeted") == some (.bool false)
-- Without a declared pair the same tables are answered.
#guard families.all fun f => beyond.all fun (r, p) =>
  value (meteredCase f false r p "evaluate-budgeted") == some (.bool false)

-- The `model` mode refuses and accepts the same models (one check, two callers).
def modelRefusal (profiles : String) (required permitted : String) : Option String :=
  match VE.Service.Standalone.modelCase (Json.mkObj [("id", .str "model"),
      ("environment", parsed (environmentText profiles true)), ("model", parsed (modelText required permitted))]) with
  | .ok _ => none
  | .error e => some e

#guard families.all fun f => beyond.all fun (r, p) => modelRefusal f r p == some diagnostic
#guard families.all fun f => within.all fun (r, p) => modelRefusal f r p == none

-- The tree both modes read: the declared pair, and none without a `regulated` declaration.
def pairsOf (regulated : Bool) : Option (List VE.Norms.Pair) :=
  match VE.Service.Standalone.profileTree (parsed (environmentText fol regulated)) with
  | .ok (some T) => some (VE.Norms.pairs T)
  | _ => none

#guard pairsOf true == some [⟨"required", "permitted", ["point"]⟩]
#guard (VE.Service.Standalone.profileTree (parsed (environmentText fol false))).toOption == some none

-- The shared check on decoded relations: each required tuple must be a permitted one.
def tree : VE.Norms.Tree :=
  ⟨[⟨"r", ["s"], false, .obligation, some "{0} x", some "p"⟩, ⟨"p", ["s"], false, .permission, some "{0} x", none⟩],
   [], []⟩

def onRelations (r p : List (List String)) : Option String :=
  match VE.Norms.Plain.profileOkOn tree (fun name =>
      pure (if name == "r" then r else if name == "p" then p else [])) with
  | .ok () => none
  | .error e => some e

#guard onRelations [["a"]] [] == some "InvalidModel(profile): required relation r exceeds permission p"
#guard onRelations [["a"], ["b"]] [["a"]] == some "InvalidModel(profile): required relation r exceeds permission p"
#guard onRelations [["a"], ["b"]] [["b"], ["a"]] == none
#guard onRelations [] [] == none

#guard onRelations [["b"], ["a"]] [["a"]] == some "InvalidModel(profile): required relation r exceeds permission p"

-- Two pairs: a tuple beyond its permission in either pair is refused.
def tree2 : VE.Norms.Tree :=
  ⟨[⟨"r1", ["s"], false, .obligation, some "{0} x", some "p1"⟩, ⟨"p1", ["s"], false, .permission, some "{0} x", none⟩,
    ⟨"r2", ["s"], false, .obligation, some "{0} y", some "p2"⟩, ⟨"p2", ["s"], false, .permission, some "{0} y", none⟩],
   [], []⟩

def onTwo (r1 p1 r2 p2 : List (List String)) : Option String :=
  match VE.Norms.Plain.profileOkOn tree2 (fun name =>
      pure (match name with | "r1" => r1 | "p1" => p1 | "r2" => r2 | "p2" => p2 | _ => [])) with
  | .ok () => none
  | .error e => some e

#guard onTwo [["a"]] [] [] [] == some "InvalidModel(profile): required relation r1 exceeds permission p1"
#guard onTwo [] [] [["a"]] [] == some "InvalidModel(profile): required relation r2 exceeds permission p2"
#guard onTwo [["a"]] [["a"]] [["b"]] [["b"]] == none

-- The tree is read from every predicate, wherever the regulated ones sort.
def treeOf (predicates : String) : Option (List VE.Norms.Pair) :=
  match VE.Service.Standalone.profileTree (parsed (r#"{"vocabulary": {"predicates": "# ++ predicates ++ "}}")) with
  | .ok (some T) => some (VE.Norms.pairs T)
  | _ => none

def entry (role extra : String) : String :=
  r#"{"arguments": ["point"], "description": "d", "regulated": {"role": ""# ++ role ++
    r#"", "default": "deny""# ++ extra ++ "}}"

def plainEntry : String := r#"{"arguments": ["point"], "description": "d"}"#

-- An unregulated predicate first, the pair after it.
#guard treeOf ("{\"a_upper\": " ++ plainEntry ++ ", \"permitted\": " ++ entry "permission" r#", "act": "{0} be done""# ++
  ", \"required\": " ++ entry "obligation" r#", "act": "{0} be done", "permission": "permitted""# ++ "}") ==
  some [⟨"required", "permitted", ["point"]⟩]
-- One regulated predicate, sorted first or last: a tree with no pair.
#guard treeOf ("{\"a_lone\": " ++ entry "plain" "" ++ ", \"z_upper\": " ++ plainEntry ++ "}") == some []
#guard treeOf ("{\"a_upper\": " ++ plainEntry ++ ", \"z_lone\": " ++ entry "plain" "" ++ "}") == some []

-- `ProfileHolds` on finite relations, and `ProfileAdmits` of a prepared environment with a profile.
instance (T : VE.Norms.Tree) (relations : String → List (List String)) :
    Decidable (VE.Norms.Plain.ProfileHolds T relations) := by
  unfold VE.Norms.Plain.ProfileHolds; infer_instance

def good : String → List (List String) := fun name => if name == "r" then [["a"]] else [["a"], ["b"]]
def bad : String → List (List String) := fun name => if name == "r" then [["a"], ["b"]] else [["a"]]

#guard decide (VE.Norms.Plain.ProfileHolds tree good)
#guard !decide (VE.Norms.Plain.ProfileHolds tree bad)

def prep (T? : Option VE.Norms.Tree) : VE.Route.MeteredRun.Prepared :=
  { checked := .error "", layered := Thunk.pure (.error ""), route := Thunk.pure (.error ""),
    order := Thunk.pure (.error ""), core := Thunk.pure (.error ""), profile := Thunk.pure (.ok T?) }

example : VE.Route.MeteredRun.ProfileAdmits (prep (some tree)) good :=
  ⟨some tree, rfl, fun T h => by cases h; decide⟩
example : ¬ VE.Route.MeteredRun.ProfileAdmits (prep (some tree)) bad := fun ⟨T?, h, hall⟩ => by
  cases h; exact absurd (hall _ rfl) (by decide)
example : VE.Route.MeteredRun.ProfileAdmits (prep none) bad := ⟨none, rfl, fun T h => by cases h⟩

-- A frozen envelope has no profile, as its `model` mode has no profile check.
#guard match (VE.Route.MeteredRun.prepare (parsed r#"{"language": "ve.core@0"}"#)).profile.get with
  | .ok none => true
  | _ => false

end VE.Route.MeteredProfileExamples
