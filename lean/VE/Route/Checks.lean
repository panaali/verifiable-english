import VE.Route.Run
import VE.Route.Examples

/-! Executable checks for the route: the profile gate, the dependency DAG,
labels, nested kinds and the literal generator. -/
namespace VE.Route.Checks
open Lean
open Gate Admission

private instance {ε α : Type} [BEq ε] [BEq α] : BEq (Except ε α) where
  beq
    | .ok a, .ok b => a == b
    | .error a, .error b => a == b
    | _, _ => false

-- Profile families (mirrors ve/profiles.py).
#guard classify ["relational-fol@0"] == .ok .fol
#guard classify ["definitions@0", "documents@1", "norms@0", "relational-fol@0"] == .ok .fol
#guard classify ["closure@0", "relational-fol@0"] == .ok .closure
#guard classify ["closure@0", "nary@0", "relational-fol@0"] == .ok .closureNary
#guard classify ["order@0", "relational-fol@0", "time@0"] == .ok .order
#guard classify ["closure@0", "order@0", "relational-fol@0"] ==
  .error "UnsupportedProfile: Unsupported profile combination closure@0 x order@0"
#guard classify ["nary@0", "order@0", "relational-fol@0"] ==
  .error "UnsupportedProfile: Unsupported profile combination nary@0 x order@0"
#guard classify ["nary@0", "relational-fol@0"] ==
  .error "UnsupportedProfile: Unsupported profile nary@0 without closure@0"
#guard classify ["relational-fol@0", "zzz@0"] == .error "UnsupportedProfile: Unsupported profile zzz@0"
#guard classify ["definitions@0"] == .error "UnsupportedProfile: Missing profile relational-fol@0"
#guard classify ["relational-fol@0", "closure@0"] ==
  .error "UnsupportedProfile: profiles must be sorted and unique"
#guard classify ["relational-fol@0", "relational-fol@0"] ==
  .error "UnsupportedProfile: profiles must be sorted and unique"

private def definedVocabulary : Json := Json.mkObj [
  ("sorts", Json.mkObj [("point", Json.mkObj [("description", .str "point")])]),
  ("predicates", Json.mkObj [("alias", Json.mkObj [
    ("arguments", toJson (["point"] : List String)), ("description", .str "alias"),
    ("defined", Json.mkObj [("arguments", toJson (["point"] : List String)),
      ("body", toJson (["top"] : List String))])])]),
  ("constants", Json.mkObj [])]
#guard (match VE.Route.Wire.decodeVocabulary ["definitions@0", "relational-fol@0"] definedVocabulary with
  | .ok rv => VE.Definitions.names rv.definitions == ["alias"]
  | .error _ => false)

/-- Two definitions `a` and `b` over a base predicate, with the given bodies. -/
private def twoDefinitions (a b : Json) : Json := Json.mkObj [
  ("sorts", Json.mkObj [("point", Json.mkObj [("description", .str "point")])]),
  ("predicates", Json.mkObj [
    ("base", Json.mkObj [("arguments", toJson (["point"] : List String)), ("description", .str "base")]),
    ("a", Json.mkObj [("arguments", toJson (["point"] : List String)), ("description", .str "a"),
      ("defined", Json.mkObj [("arguments", toJson (["point"] : List String)), ("body", a)])]),
    ("b", Json.mkObj [("arguments", toJson (["point"] : List String)), ("description", .str "b"),
      ("defined", Json.mkObj [("arguments", toJson (["point"] : List String)), ("body", b)])])]),
  ("constants", Json.mkObj [])]

private def atom (p : String) (i : Nat) : Json :=
  Json.arr #[.str "unary", .str p, Json.arr #[.str "var", toJson i]]

private def decodeError (v : Json) : String :=
  match VE.Route.Wire.decodeVocabulary ["definitions@0", "relational-fol@0"] v with
  | .ok _ => "ok"
  | .error e => e

-- Definitions are ordered below their dependents (`b` mentions `a`)...
#guard (match VE.Route.Wire.decodeVocabulary ["definitions@0", "relational-fol@0"] (twoDefinitions (atom "base" 0) (atom "a" 0)) with
  | .ok rv => VE.Definitions.names rv.definitions == ["a", "b"]
  | .error _ => false)
-- ...whatever the declaration order.
#guard (match VE.Route.Wire.decodeVocabulary ["definitions@0", "relational-fol@0"] (twoDefinitions (atom "b" 0) (atom "base" 0)) with
  | .ok rv => VE.Definitions.names rv.definitions == ["b", "a"]
  | .error _ => false)
-- Recursion, a mutual cycle and a free variable are rejected with the Python diagnostics' shape.
#guard decodeError (twoDefinitions (atom "a" 0) (atom "base" 0)) == "DependencyCycle: a"
#guard decodeError (twoDefinitions (atom "b" 0) (atom "a" 0)) == "DependencyCycle: a, b"
#guard decodeError (twoDefinitions (atom "base" 1) (atom "base" 0)) ==
  "Definition a: the body is not a typed formula over the symbols below it"

-- One dependency DAG: definitions above and below norms; cycles rejected.
#guard dependencyOrder [⟨"violation", ["required", "done"]⟩, ⟨"required", ["safe"]⟩,
  ⟨"safe", ["base"]⟩] == .ok ["safe", "required", "violation"]
#guard dependencyOrder [⟨"b", []⟩, ⟨"a", []⟩, ⟨"c", ["a", "b"]⟩] == .ok ["a", "b", "c"]
#guard dependencyOrder [⟨"a", ["b"]⟩, ⟨"b", ["a"]⟩, ⟨"c", ["a"]⟩, ⟨"d", []⟩] ==
  .error "DependencyCycle: a, b, c"
#guard dependencyOrder [⟨"p", ["p"]⟩] == .error "DependencyCycle: p"
#guard dependencyOrder [⟨"p", []⟩, ⟨"p", []⟩] == .error "DuplicateDeclaration: dependency node p"
#guard dependencyOrder [] == .ok []

-- Labels: only canonical strings parse.
#guard parseLabel "asserted" == some .asserted
#guard parseLabel "bridge:accepts(bob,u2)" == some (.bridge "bob" "u2")
#guard parseLabel "background:literals" == some (.background "literals")
#guard parseLabel "background:other" == none
#guard parseLabel "cite:b1/t7mono" == some (.cite "b1" "t7mono")
#guard parseLabel "open:reasonable_precautions" == some (.openTerm "reasonable_precautions")
#guard parseLabel "readings:s1@2:all" == some (.readings "s1" 2 none)
#guard parseLabel "readings:s1@2:1" == some (.readings "s1" 2 (some 1))
#guard parseLabel "readings:s1@02:1" == none
#guard parseLabel "narrowing:n1" == some (.narrowing "n1")
#guard parseLabel "bridge:accepts(bob,u2,u3)" == none
#guard parseLabel "cite:a/b/c" == none
#guard compatible "readings:s1@1:0" "readings:s1@1:1" == false
#guard compatible "readings:s1@1:0" "readings:s1@1:all" == true
#guard compatible "readings:s1@1:0" "readings:s1@2:0" == false
#guard compatible "readings:s1@1:0" "readings:s2@1:1" == true

-- Nested kinds decode and render back exactly (depth 3).
private def nested : Json := Json.arr #[.str "attributed", .str "alice", .str "believes",
  Json.arr #[.str "hedged", .str "likely",
    Json.arr #[.str "causal", .str "because", .str "asserted", .str "asserted"]]]
#guard (decodeKind 16 nested).map renderKind == .ok nested
#guard (decodeKind 16 nested).map Kind.depth == .ok 4
#guard ((decodeKind 16 (Json.arr #[.str "attributed", .str "alice", .str "shouts", .str "asserted"])) matches .error _)
#guard ((decodeKind 2 nested) matches .error _)

-- The literal generator: sorted pairs.
#guard Background.literals ["legal", "finance", "hr"] ==
  [.not (.eq (.const "finance") (.const "hr")), .not (.eq (.const "finance") (.const "legal")),
   .not (.eq (.const "hr") (.const "legal"))]
#guard Background.literals ["only"] == []

end VE.Route.Checks
