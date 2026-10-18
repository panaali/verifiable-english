import VE.Limits
import VE.Bridge
import VE.Order.Wire
import VE.CertificateWire
import VE.EnglishGrammar.Lexer
import VE.Route.AstLimit
import VE.Route.Budget
import VE.Time.Wire
import VE.WireContract.Names

/-! The limits that frozen, hashed or generated modules keep as literals are `VE.Limits`' values:
at the limit and one past it for the frozen decoders' inline literals, and by value for their named
copies and for the diagnostics that state a limit. The frozen decoders are hash-frozen by
architecture decision D2 (`VE/Route/frozen-sources.sha256`), the English lexer by the grammar lock
(`ve/english_grammar/LOCK.json`), the wire-contract name classes are generated
(`tools/wire_contract.py`); none may import `VE.Limits`. A changed limit fails one of these guards
(lf-18 review F2: the frozen decoders' node and depth literals were not tied). -/
namespace VE.LimitTies
open Lean VE.Limits

private def nested (depth : Nat) : String :=
  String.mk (List.replicate depth '[') ++ String.mk (List.replicate depth ']')

private def name (bytes : Nat) : String := String.mk (List.replicate bytes 'a')

private def top : Json := Json.arr #[.str "top"]

/-- `n` formulas of one node each. -/
private def tops (n : Nat) : Json := Json.arr (List.replicate n top).toArray

/-- A formula `n + 1` levels deep. -/
private def nots : Nat → Json
  | 0 => top
  | n + 1 => Json.arr #[.str "not", nots n]

/-- One formula of `n` nodes (for `n ≥ 1`), about log₂ n levels deep. -/
private def tree : Nat → Json
  | 0 => top
  | 1 => top
  | 2 => Json.arr #[.str "not", top]
  | n + 1 => Json.arr #[.str "and", tree (n / 2), tree (n - n / 2)]
decreasing_by all_goals omega

private def failure : Except String α → String
  | .error e => e
  | .ok _ => ""

private def vocabulary : Json :=
  Json.mkObj [("sorts", Json.mkObj []), ("predicates", Json.mkObj []), ("constants", Json.mkObj [])]

private def empty : VE.Environment := ⟨[], fun _ => none, fun _ => none⟩
private def emptyOrder : VE.Order.Environment := ⟨[], fun _ => none, fun _ => none⟩

private def orderEnvironment : Json := Json.mkObj [("language", .str VE.Order.Wire.orderLanguage),
  ("profiles", toJson VE.Order.Wire.orderProfiles), ("spec_revision", .str VE.Order.Wire.orderRevision),
  ("vocabulary", vocabulary)]

private def closureEnvironment : Json := Json.mkObj [("language", .str "ve.core@0.1"),
  ("profiles", toJson ["closure@0", "relational-fol@0"]),
  ("spec_revision", .str "ve-v0.1-closure-2026-09-21"), ("vocabulary", vocabulary)]

/-- A certificate case without its certificate: the node and depth limits are checked before the
certificate is read, so a case within them fails only for the missing certificate. -/
private def query (environment : Json) (premises : Nat) (conclusion : Json) : Json :=
  Json.mkObj [("id", .str "tie"), ("environment", environment), ("kind", .str "certificate"),
    ("premises", tops premises), ("conclusion", conclusion)]

private def countermodel (premises : Nat) (conclusion : Json) : Json :=
  Json.mkObj [("premises", tops premises), ("conclusion", conclusion)]

private def induct (invariant : Json) : Json :=
  Json.mkObj [("rule", .str "closure-induct@1"), ("at", toJson (0 : Nat)), ("sort", .str "s"),
    ("invariant", invariant), ("children", Json.arr #[])]

private def depthFault : String := s!"ResourceLimit: formula depth exceeds {maxDepth}"

/-- `n` declarations named `stem0`, `stem1`, … with one entry. -/
private def entries (stem : String) (n : Nat) (entry : Json) : Json :=
  Json.mkObj ((List.range n).map fun i => (stem ++ toString i, entry))

private def described : Json := Json.mkObj [("description", .str "d")]
private def unaryOnS0 : Json := Json.mkObj [("arguments", Json.arr #[.str "s0"]), ("description", .str "d")]

private def declarations (sorts predicates : Nat) : Json :=
  Json.mkObj [("sorts", entries "s" sorts described), ("predicates", entries "p" predicates unaryOnS0),
    ("constants", Json.mkObj [])]

private def folEnvironment (sorts predicates : Nat) : Json := Json.mkObj [("language", .str "ve.core@0"),
  ("profile", .str "relational-fol@0"), ("spec_revision", .str "ve-v0-draft-2026-09-20"),
  ("vocabulary", declarations sorts predicates)]

private def orderDeclarations (sorts predicates : Nat) : Json :=
  orderEnvironment.setObjVal! "vocabulary" (declarations sorts predicates)

/-- A model of `folEnvironment 1 1` whose one domain holds `n` entities. -/
private def domainOf (n : Nat) : Json := Json.mkObj [("complete", .bool true),
  ("domains", Json.mkObj [("s0", Json.arr ((List.range n).map fun i => Json.str ("e" ++ toString i)).toArray)]),
  ("constants", Json.mkObj []), ("relations", Json.mkObj [("p0", Json.arr #[])])]

private def folDomain (n : Nat) : Except String Unit := do
  let _ ← VE.Bridge.decodeModelData (← VE.Bridge.decodeEnvironment (folEnvironment 1 1)) (domainOf n)

private def orderDomain (n : Nat) : Except String Unit := do
  let _ ← VE.Order.Wire.decodeModel (← VE.Order.Wire.decodeEnvironment (orderDeclarations 1 1)) (domainOf n)

private def vocabularyFault : String := "ResourceLimit: vocabulary size"
private def domainFault : String := "ResourceLimit: domain size"

-- `VE.Json`: nesting, the largest integer and the package cap.
#guard (VE.JsonInput.parse (nested maxJsonDepth)).toBool
#guard !(VE.JsonInput.parse (nested (maxJsonDepth + 1))).toBool
#guard (VE.JsonInput.parse (toString maxIndex)).toBool
#guard !(VE.JsonInput.parse (toString (maxIndex + 1))).toBool
#guard (VE.JsonInput.parse ("0".pushn ' ' (maxPackageBytes - 1))).toBool
#guard !(VE.JsonInput.parse ("0".pushn ' ' maxPackageBytes)).toBool
#guard (VE.JsonInput.parseCases ("[0]".pushn ' ' (maxPackageBytes - 3))).toBool
#guard !(VE.JsonInput.parseCases ("[0]".pushn ' ' (maxPackageBytes - 2))).toBool

-- `VE.Bridge`: identifiers, and a document's and a countermodel query's node total and depth.
#guard VE.Bridge.identifier (name maxIdentifierBytes)
#guard !VE.Bridge.identifier (name (maxIdentifierBytes + 1))
#guard VE.Bridge.sourceIdentifierBudget (name maxIdentifierBytes)
#guard !VE.Bridge.sourceIdentifierBudget (name (maxIdentifierBytes + 1))
#guard (VE.Bridge.decodeDocument empty (tops maxNodes)).toBool
#guard failure (VE.Bridge.decodeDocument empty (tops (maxNodes + 1))) == "ResourceLimit: AST node count"
#guard (VE.Bridge.decodeDocument empty (Json.arr #[nots (maxDepth - 1)])).toBool
#guard failure (VE.Bridge.decodeDocument empty (Json.arr #[nots maxDepth])) == depthFault
#guard (VE.Bridge.decodeCountermodel empty (countermodel (maxNodes - 1) top)).toBool
#guard failure (VE.Bridge.decodeCountermodel empty (countermodel maxNodes top)) ==
  "ResourceLimit: countermodel AST node count"
#guard (VE.Bridge.decodeCountermodel empty (countermodel 0 (nots (maxDepth - 1)))).toBool
#guard failure (VE.Bridge.decodeCountermodel empty (countermodel 0 (nots maxDepth))) == depthFault

-- `VE.Bridge`: an environment's sorts and predicates, and a domain's entities.
#guard failure (VE.Bridge.decodeEnvironment (folEnvironment maxSorts 1)) != vocabularyFault
#guard failure (VE.Bridge.decodeEnvironment (folEnvironment (maxSorts + 1) 1)) == vocabularyFault
#guard failure (VE.Bridge.decodeEnvironment (folEnvironment 1 maxPredicates)) != vocabularyFault
#guard failure (VE.Bridge.decodeEnvironment (folEnvironment 1 (maxPredicates + 1))) == vocabularyFault
#guard (folDomain maxEntities).toBool
#guard failure (folDomain (maxEntities + 1)) == domainFault

-- `VE.Order.Wire`: an environment's sorts and predicates, and a domain's entities.
#guard failure (VE.Order.Wire.decodeEnvironment (orderDeclarations maxSorts 1)) != vocabularyFault
#guard failure (VE.Order.Wire.decodeEnvironment (orderDeclarations (maxSorts + 1) 1)) == vocabularyFault
#guard failure (VE.Order.Wire.decodeEnvironment (orderDeclarations 1 maxPredicates)) != vocabularyFault
#guard failure (VE.Order.Wire.decodeEnvironment (orderDeclarations 1 (maxPredicates + 1))) == vocabularyFault
#guard (orderDomain maxEntities).toBool
#guard failure (orderDomain (maxEntities + 1)) == domainFault

-- `VE.Order.Wire`: a document's node total and depth, a certificate query's, and the numeral cap.
#guard (VE.Order.Wire.decodeFormulas emptyOrder (tops maxNodes)).toBool
#guard failure (VE.Order.Wire.decodeFormulas emptyOrder (tops (maxNodes + 1))) == "ResourceLimit: AST node count"
#guard (VE.Order.Wire.decodeFormulas emptyOrder (Json.arr #[nots (maxDepth - 1)])).toBool
#guard failure (VE.Order.Wire.decodeFormulas emptyOrder (Json.arr #[nots maxDepth])) == depthFault
#guard failure (VE.Order.Wire.runCase (query orderEnvironment (maxNodes - 1) top)) == "property not found: certificate"
#guard failure (VE.Order.Wire.runCase (query orderEnvironment maxNodes top)) == "ResourceLimit: AST node count"
#guard failure (VE.Order.Wire.runCase (query orderEnvironment 0 (nots (maxDepth - 1)))) ==
  "property not found: certificate"
#guard failure (VE.Order.Wire.runCase (query orderEnvironment 0 (nots maxDepth))) == depthFault
#guard VE.Order.Wire.maxNumeralChars == maxNumeralChars

-- `VE.CertificateWire`: a closure query's node total and depth, and an induction invariant's.
#guard failure (VE.CertificateWire.runClosureCase (query closureEnvironment (maxNodes - 1) top)) ==
  "property not found: certificate"
#guard failure (VE.CertificateWire.runClosureCase (query closureEnvironment maxNodes top)) ==
  "ResourceLimit: AST node count"
#guard failure (VE.CertificateWire.runClosureCase (query closureEnvironment 0 (nots (maxDepth - 1)))) ==
  "property not found: certificate"
#guard failure (VE.CertificateWire.runClosureCase (query closureEnvironment 0 (nots maxDepth))) == depthFault
#guard (VE.CertificateWire.decodeClosureTrace 2 (induct (tree maxNodes))).toBool
#guard failure (VE.CertificateWire.decodeClosureTrace 2 (induct (tree (maxNodes + 1)))) ==
  "ResourceLimit: invariant AST node count"
#guard (VE.CertificateWire.decodeClosureTrace 2 (induct (nots (maxDepth - 1)))).toBool
#guard failure (VE.CertificateWire.decodeClosureTrace 2 (induct (nots maxDepth))) == depthFault

-- The English lexer's source cap.
#guard VE.EnglishGrammar.maxSourceBytes == maxSourceBytes

-- Diagnostics that state a limit.
#guard VE.Route.AstLimit.depthLimit == depthFault
#guard VE.Route.AstLimit.numeralLimit == s!"ResourceLimit: Integer literal exceeds {maxNumeralChars} characters"
#guard VE.Route.Budget.budgetExhausted ==
  s!"ResourceLimit: formula-node evaluation budget MAX_EVALUATIONS={maxEvaluations} exhausted"
#guard VE.Time.Wire.budgetExhausted == VE.Route.Budget.budgetExhausted
#guard VE.Time.Wire.aggregateLimit ==
  s!"ResourceLimit: premises and conclusion exceed aggregate {maxNodes}-node limit"

-- The generated wire-contract name classes bound an identifier.
#guard [VE.WireContract.Names.decider, VE.WireContract.Names.rule_name, VE.WireContract.Names.soft_name].all
  (·.maxBytes == some maxIdentifierBytes)

end VE.LimitTies
