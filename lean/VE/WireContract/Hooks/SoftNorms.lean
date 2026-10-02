import VE.SoftNorms.Wire
import VE.Norms.Admission
import VE.WireContract.Engine
import VE.WireContract.Tables.SoftNorms

/-! The hand-written hooks, classifiers and adapter of the pilot contract `soft-norms@0`
(docs/spec/wire-contract.md section 6).

Each one calls the frozen soft-norms code read-only, as the route does, and only
reads the result: `Phases` for the table of soft-norms.md 8, `Wire.primeVocabulary`
for 6.4, `validateSoft` and `checkW1` for 6.5 to 6.15. A hook may assume that every
earlier instance of the table holds (spec 2.5, rule 2); where the frozen code then
fails, the hook reports that failure, and where it cannot be run, the hook holds.
The classifiers never read a name out of a message: they compare a message with a
fixed text or take what follows a fixed leading text. No verdict depends on this
module; the route's `Wire.decodeSoftSource` alone accepts or rejects.
-/

namespace VE.WireContract.Hooks.SoftNorms
open Lean
open VE.WireContract
open VE.SoftNorms
open VE.Norms (ruleName pyRepr precedenceNodes)

def environmentOf (root : Json) : Json := root.getObjValD "environment"
def normsOf (root : Json) : Json := root.getObjValD "norms"

/-- The value of the `n`-th enclosing item. -/
def itemValue (root : Json) (items : List Pointer) (n : Nat) : Option Json :=
  items[n]?.bind (resolvePointer root)

/-- The text after a fixed leading text, or the whole text when it does not start with it. -/
def after (lead text : String) : String :=
  if text.startsWith lead then text.drop lead.length else text

def message (text : String) : List (String × Json) := [("message", .str text)]

/-- Phase 2's declarations, as the legacy validator decodes them; `none` before phase 2 holds. -/
def declared (root : Json) : Option (Norms.Wire.NormsEnvironment × SoftEnv) :=
  match Phases.envelope (environmentOf root) (normsOf root) with
  | .ok (profiles, _) => (Phases.declarations (environmentOf root) profiles).toOption
  | .error _ => none

/-- The source of `Wire.decodeSoftSource` after the table of soft-norms.md 8 holds over it. -/
def checked (root : Json) : Option (Wire.SoftEnvironment × SoftDoc) :=
  match Phases.checkSource (environmentOf root) (normsOf root) with
  | .ok c =>
    let se : Wire.SoftEnvironment := ⟨c.ne, c.soft, c.profiles, environmentOf root⟩
    some (se, ⟨se.ne.rv.environment, se.ne.rv.literals, se.soft, ⟨se.ne.regulated, [], c.nodes⟩⟩)
  | .error _ => none

/-- 4.2a: W1's decoding of the rule's W1 fields, its rule name and its carve-out count, in
`Phases.ruleFields`' order and with its texts. -/
def w1RuleFields (raw : Json) : HookResult :=
  match VE.Bridge.fields raw with
  | .error e => .fail (message e)
  | .ok obj =>
    match Norms.Wire.decodeNorm
        (Json.mkObj [("norm", Json.mkObj (obj.filter fun kv => Phases.w1Keys.contains kv.1))]) (shared := false) with
    | .error e => .fail (message e)
    | .ok N =>
      if !ruleName N.name then .fail (message s!"InvalidInput: invalid rule name {pyRepr N.name}")
      else if N.carveOuts.length > 8 then .fail (message "InvalidInput: invalid sign or too many carve-outs")
      else .ok

def ruleField (rule : Json) (field : String) : Json := (rule.getObjValD "norm").getObjValD field

def predicate : String → Json → List Pointer → HookResult
  -- 2.3: the inherited part of `Phases.declarations`. 2.1 and 2.2 hold, and every later check of that
  -- function has a code other than SOFT_INVALID_INPUT, so a failure with that code is 2.3's.
  | "w1_declarations", root, _ =>
    match Phases.envelope (environmentOf root) (normsOf root) with
    | .ok (profiles, _) => match Phases.declarations (environmentOf root) profiles with
      | .error f => if f.code == "SOFT_INVALID_INPUT" then .fail (message f.message) else .ok
      | .ok _ => .ok
    | .error _ => .ok
  -- 3.2
  | "profile_registered", root, items => match itemValue root items 0 with
    | some (.str p) => if VE.Route.Gate.known p || p == Phases.softProfile then .ok else .fail []
    | _ => .ok
  -- 3.5a, 3.5b
  | "no_definitions", root, _ => match declared root with
    | some (ne, _) => if ne.rv.definitions.isEmpty then .ok else .fail []
    | none => .ok
  | "no_data_flags", root, _ => match declared root with
    | some (ne, _) => if ne.rv.flags.isEmpty then .ok else .fail []
    | none => .ok
  -- 4.2a
  | "w1_rule_fields", root, items => match itemValue root items 0 with
    | some rule => w1RuleFields (rule.getObjValD "norm")
    | none => .ok
  -- 4.13b, 4.13d: one exception condition, with its own budget
  | "fol_formula", root, items => match itemValue root items 0 with
    | some condition => match Norms.Wire.decodeBudgeted condition with
      | .ok _ => .ok
      | .error e => .fail (message e)
    | none => .ok
  -- 5.4
  | "regulated_predicate", root, items => match declared root, itemValue root items 0 with
    | some (ne, _), some rule => match ruleField rule "predicate" with
      | .str p => if ne.regulated.any (·.name == p) then .ok else .fail []
      | _ => .ok
    | _, _ => .ok
  -- 5.9b: the item is a name in the rule's `over`, the enclosing item the rule
  | "over_same_predicate", root, items => match itemValue root items 0, itemValue root items 1, normsOf root with
    | some (.str m), some rule, .arr rules =>
      match rules.toList.find? (fun r => same (ruleField r "name") (.str m)) with
      | some parent =>
        if same (ruleField parent "predicate") (ruleField rule "predicate") then .ok
        else .fail [("rule", ruleField rule "name"), ("predicate", ruleField rule "predicate"),
          ("parent_predicate", ruleField parent "predicate")]
      | none => .ok
    | _, _, _ => .ok
  -- 6.1 to 6.3: `Phases.rankSemantics`
  | "outranks_acyclic", root, _ => match declared root with
    | some (_, soft) => match VE.Route.dependencyOrder (rankNodes soft) with
      | .ok _ => .ok
      | .error e => .fail [("detail", .str (after "DependencyCycle: " e))]
    | none => .ok
  | "tie_not_comparable", root, items => match declared root, itemValue root items 0 with
    | some (_, soft), some (.arr #[.str a, .str b]) =>
      if outranksPlus soft a b || outranksPlus soft b a then .fail [] else .ok
    | _, _ => .ok
  | "ties_distinct_unordered", root, _ => match declared root with
    | some (_, soft) =>
      if (soft.ties.map (fun (a, b) => if a ≤ b then (a, b) else (b, a))).eraseDups.length != soft.ties.length
      then .fail [] else .ok
    | none => .ok
  -- 6.4a, 6.4b: `Wire.primeVocabulary`, whose two loops give the two texts
  | "decision_names_fit", root, _ => match checked root with
    | some (se, D) => match Wire.primeVocabulary se D with
      | .error e =>
        if e.startsWith "ResourceLimit: decision predicate " then
          .fail [("name", .str (after "ResourceLimit: decision predicate " e))]
        else .ok
      | .ok () => .ok
    | none => .ok
  | "extended_vocabulary_fits", root, _ => match checked root with
    | some (se, D) => match Wire.primeVocabulary se D with
      | .error e => if e == "ResourceLimit: extended vocabulary" then .fail [] else .ok
      | .ok () => .ok
    | none => .ok
  | _, _, _ => .ok

/-- `soft_semantic` (section 6): the member for the message `m` with which `validateSoft` rejects; the first
    rule that applies decides. -/
def semanticMember (D : SoftDoc) (m : String) : ClassifierResult :=
  let detail (lead : String) : List (String × Json) := [("detail", .str (after lead m))]
  let base := match checkW1 D.base with
    | .error e => e == m
    | .ok () => false
  if base && m == "ResourceLimit: AST exceeds 10,000 nodes" then .fail "6.5a" []
  else if base && m == "ResourceLimit: precedence depth" then .fail "6.6" []
  else if base && m.startsWith "DependencyCycle: " then
    if (VE.Route.dependencyOrder (precedenceNodes D.base.T)).toBool then .fail "6.7" (detail "DependencyCycle: ")
    else .fail "6.5b" (detail "DependencyCycle: ")
  else if base then .ok
  else if m.startsWith "SoftOverHard: " then .fail "6.8" (detail "SoftOverHard: ")
  else if m.startsWith "ResourceLimit: derived carve-out" then .fail "6.9" (detail "ResourceLimit: derived carve-out")
  else if m.startsWith "ResourceLimit: generated soft premise" then .fail "6.11" []
  else if m == "ResourceLimit: generated norm layers" then .fail "6.15" []
  else if m.startsWith "ResourceLimit: generated norm layer " then
    .fail "6.12" (detail "ResourceLimit: generated norm layer ")
  else if m.startsWith "ResourceLimit: generated conflict target " then
    .fail "6.13" (detail "ResourceLimit: generated conflict target ")
  else if m == "ResourceLimit: generated background" then .fail "6.14" []
  else if m.startsWith "DependencyCycle: " then .fail "6.10a" (detail "DependencyCycle: ")
  else if m.startsWith "ResourceLimit: " then .fail "6.10b" (message m)
  else .fail "6.10c" (message m)

def classifier : String → Json → List Pointer → ClassifierResult
  -- 5.7 and 5.8 for one rule: `Phases.ruleReferences` on the rule without its exception, then on the rule
  | "rule_typing", root, items =>
    match declared root, itemValue root items 0 with
    | some (ne, soft), some rule => match Phases.ruleFields soft.exceptionDecider rule with
      | .ok N => match Phases.ruleReferences ne soft { N with exception := none } with
        | .error f => .fail "5.7" (message f.message)
        | .ok () => match Phases.ruleReferences ne soft N with
          | .error f =>
            if f.code == "SOFT_INVALID_EXCEPTION_CONDITION" then
              .fail "5.8b" [("detail", .str (after "InvalidInput: exception condition of rule " f.message))]
            else .fail "5.8a" (message f.message)
          | .ok () => .ok
      | .error _ => .ok
    | _, _ => .ok
  -- 6.5 to 6.15: `validateSoft` on the document that `Wire.decodeSoftSource` builds
  | "soft_semantic", root, _ => match checked root with
    | some (_, D) => match validateSoft D with
      | .error m => semanticMember D m
      | .ok () => .ok
    | none => .ok
  | _, _, _ => .ok

def view : String → Json → Json
  | _, v => v

def hooks : Hooks := ⟨predicate, classifier, view⟩

/-- The adapter `soft_source` (section 6): the root `{environment, norms}` of a `soft-*` case, and for an
    `admission` case the active norm units that `VE.Norms.Admission.splitDocument` returns, as
    `SoftNorms.Run.reportedCode` reads them. -/
def adapter (case : Json) : Except String Json :=
  let root (norms : Json) : Json := Json.mkObj [("environment", case.getObjValD "environment"), ("norms", norms)]
  match case.getObjValD "kind" with
  | .str "admission" => match VE.Norms.Admission.splitDocument (case.getObjValD "document") with
    | .ok (_, active, _) => .ok (root active)
    | .error _ => .ok (root .null)
  | .str "soft-elaborate" => .ok (root (case.getObjValD "norms"))
  | .str kind => .error s!"UnsupportedProfile: case kind {kind} has no wire contract input"
  | kind => .error s!"UnsupportedProfile: case kind {kind.compress} has no wire contract input"

/-- The names this module registers. -/
def registered : List String :=
  ["w1_declarations", "profile_registered", "no_definitions", "no_data_flags", "w1_rule_fields", "fol_formula",
   "regulated_predicate", "over_same_predicate", "outranks_acyclic", "tie_not_comparable",
   "ties_distinct_unordered", "decision_names_fit", "extended_vocabulary_fits", "rule_typing", "soft_semantic"]

#guard Tables.SoftNorms.table.hookNames.all registered.contains

end VE.WireContract.Hooks.SoftNorms
