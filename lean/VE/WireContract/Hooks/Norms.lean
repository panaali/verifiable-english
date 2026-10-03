import VE.Norms.Wire
import VE.NormDefaults.Wire
import VE.WireContract.Engine
import VE.WireContract.Tables.Norms

/-! The hand-written hooks, classifiers and adapter of the contract `norms@0`
(docs/spec/wire-contract-s5.md 2.3 and 2.5).

Each hook reads its two arguments only and calls the frozen norms code read-only:
`Norms.Wire.decodeNormsEnvironment` and the route's environment decoder for 1.1,
`Route.dependencyOrder` for 6.1 and 6.3, `Norms.height` for 6.2. A hook may assume
that every earlier instance of the table holds (base spec 2.5, rule 2); where it
then cannot read what it needs, it holds. None calls `Norms.Wire.decodeSource`.

Two walks have no frozen function with their order, and this module holds them,
diagnostic only and under no theorem (spec 5.2):

* the syntax walk of 3.8 and 3.9, `synFormula`: `Norms.Wire.budgetFormula` and
  `budgetTerm` line for line, except that a value that is not a string in a name
  position is read as `sentinel`, so that the name fails typing (4.7b) and not the
  walk. Where the names are strings it returns `budgetFormula`'s result (L8, the
  `#guard`s below);
* the typing walk of 4.7, `typeWalk`: the checks and texts of
  `Norms.typeDiagnostic` and `termSort` in their order, with one running node
  total that counts each formula and term node on entering it, before its own
  check, as Python's `_Checker` does.

No verdict depends on this module; the route's legacy validator alone accepts or
rejects. -/

namespace VE.WireContract.Hooks.Norms
open Lean
open VE.WireContract
open VE.Norms (pyRepr pyTuple termSort)

def environmentOf (root : Json) : Json := root.getObjValD "environment"
def normsOf (root : Json) : Json := root.getObjValD "norms"

/-- The value of the `n`-th enclosing item. -/
def itemValue (root : Json) (items : List Pointer) (n : Nat) : Option Json :=
  items[n]?.bind (resolvePointer root)

/-- The index of the `n`-th enclosing item in its array. -/
def itemIndex (items : List Pointer) (n : Nat) : Option Nat :=
  items[n]?.bind fun p => p.getLast?.bind indexToken?

/-- The text after a fixed leading text, or the whole text when it does not start with it. -/
def after (lead text : String) : String :=
  if text.startsWith lead then text.drop lead.length else text

def message (text : String) : List (String × Json) := [("message", .str text)]

def ruleField (rule : Json) (field : String) : Json := (rule.getObjValD "norm").getObjValD field

def rulesOf (root : Json) : List Json :=
  match normsOf root with
  | .arr xs => xs.toList
  | _ => []

/-- The profiles of the submitted environment (`[]` when they are not a string array). -/
def profiles (root : Json) : List String := VE.NormDefaults.Wire.profilesOf (environmentOf root)

def underDefaults (root : Json) : Bool := (profiles root).contains VE.NormDefaults.Wire.profile

/-! ## 1.1: the environment -/

/-- `w1_environment`: with `norms@0`, the norms route's decoder, on the placeholder environment under
    `norm-defaults@0` and then that profile's reserved `unsaid__` names (`checkAuthor`'s first loop); then the
    check `decodeSource` makes after its decoder, that a `defined` declaration has `definitions@0`. Without
    `norms@0`, the route's environment decoder (`Gate.decodeEnvelope` and `Route.Wire.decodeVocabulary`) with the
    same check, which refuses a `regulated` member as Python's `Environment` does without the profile. -/
def w1Environment (environment : Json) : Except String Unit := do
  let listed := VE.NormDefaults.Wire.profilesOf environment
  if listed.contains "norms@0" then
    let defaults := listed.contains VE.NormDefaults.Wire.profile
    let decoded ← if defaults then VE.NormDefaults.Wire.placeholderJson environment else pure environment
    let ne ← VE.Norms.Wire.decodeNormsEnvironment decoded
    if defaults then
      for n in VE.NormDefaults.Wire.declaredNames environment do
        if n.startsWith "unsaid__" then throw s!"InvalidInput: reserved name {n}"
    unless ne.rv.definitions.isEmpty || ne.profiles.contains "definitions@0" do
      throw "defined declarations require the definitions@0 profile"
  else
    let e ← VE.Route.Gate.decodeEnvelope environment
    let rv ← VE.Route.Wire.decodeVocabulary e.profiles e.vocabulary
    unless rv.definitions.isEmpty || e.profiles.contains "definitions@0" do
      throw "defined declarations require the definitions@0 profile"

/-- The environment the typing walk reads: the norms route's, as 1.1 decodes it; `none` before 1.1 holds. -/
def typingEnvironment (root : Json) : Option VE.Environment := do
  let environment := environmentOf root
  let decoded ← if underDefaults root then (VE.NormDefaults.Wire.placeholderJson environment).toOption
    else some environment
  let ne ← (VE.Norms.Wire.decodeNormsEnvironment decoded).toOption
  pure ne.rv.environment

/-! ## 3.8 and 3.9: the syntax walk -/

/-- The name read for a value in a name position that is not a string. It is outside `[a-z][a-z0-9_]*`
    (`ve/environment.py:29`) and is no built-in sort, so no vocabulary declares it and typing refuses it. -/
def sentinel : String := "<not a string>"

def nameOf : Json → String
  | .str s => s
  | _ => sentinel

/-- `Norms.Wire.budgetTerm`, with `sentinel` for a `const` name that is not a string. -/
def synTerm (count : Nat) (j : Json) : Except String (VE.Term × Nat) := do
  if count + 1 > VE.Norms.Wire.maxNodes then throw "ResourceLimit: AST exceeds depth or node budget"
  let t ← match (← j.getArr?).toList with
    | [.str "var", i] => pure (VE.Term.var (← i.getNat?))
    | [.str "const", c] => pure (VE.Term.const (nameOf c))
    | _ => throw "invalid indexed term"
  if let .var i := t then
    unless i ≤ VE.Norms.Wire.maxIndex do throw "UnboundVariable: Invalid variable index"
  pure (t, count + 1)

/-- `Norms.Wire.budgetFormula`, with `sentinel` for a predicate or binder sort that is not a string. -/
def synFormula : Nat → Nat → Json → Except String (VE.Formula × Nat)
  | 0, _, _ => throw "ResourceLimit: formula depth exceeds 64"
  | n + 1, count, j => do
    let count := count + 1
    if count > VE.Norms.Wire.maxNodes then throw "ResourceLimit: AST exceeds depth or node budget"
    match (← j.getArr?).toList with
    | [.str "top"] => return (.top, count)
    | [.str "bottom"] => return (.bottom, count)
    | [.str "unary", p, t] =>
      let (t, count) ← synTerm count t
      return (.unary (nameOf p) t, count)
    | [.str "binary", p, t, u] =>
      let (t, count) ← synTerm count t
      let (u, count) ← synTerm count u
      return (.binary (nameOf p) t u, count)
    | [.str "eq", t, u] =>
      let (t, count) ← synTerm count t
      let (u, count) ← synTerm count u
      return (.eq t u, count)
    | [.str "not", a] =>
      let (a, count) ← synFormula n count a
      return (.not a, count)
    | [.str "and", a, b] =>
      let (a, count) ← synFormula n count a
      let (b, count) ← synFormula n count b
      return (.and a b, count)
    | [.str "or", a, b] =>
      let (a, count) ← synFormula n count a
      let (b, count) ← synFormula n count b
      return (.or a b, count)
    | [.str "implies", a, b] =>
      let (a, count) ← synFormula n count a
      let (b, count) ← synFormula n count b
      return (.implies a b, count)
    | [.str "forall", s, a] =>
      let (a, count) ← synFormula n count a
      return (.all (nameOf s) a, count)
    | [.str "exists", s, a] =>
      let (a, count) ← synFormula n count a
      return (.ex (nameOf s) a, count)
    | _ => throw "invalid indexed formula"

/-- A rule's guard, then its carve-outs, under one count (as `decodeNorm`'s `shared := true`). -/
def synRule (rule : Json) : Except String (List VE.Formula) := do
  let (guard, count) ← synFormula 64 0 (ruleField rule "guard")
  let carveOuts ← match ruleField rule "unless" with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: unless and over must be arrays"
  let mut count := count
  let mut formulas := [guard]
  for x in carveOuts do
    let (φ, next) ← synFormula 64 count x
    count := next
    formulas := formulas ++ [φ]
  pure formulas

/-- 3.8a on a failure whose leading word is `ResourceLimit`, 3.8b (or 3.9b) on any other. -/
def syntaxMember (budget shape : String) (e : String) : ClassifierResult :=
  if e.startsWith "ResourceLimit:" then .fail budget (message e) else .fail shape (message e)

/-- 3.9 at the `k`-th carve-out: the guard and the carve-outs before it are read under one count (each holds,
    by rule 2), and the item's first refused node names the member. -/
def carveOutSyntax (rule : Json) (k : Nat) : ClassifierResult :=
  match synFormula 64 0 (ruleField rule "guard"), ruleField rule "unless" with
  | .ok (_, count), .arr xs =>
    let rec go : Nat → Nat → List Json → ClassifierResult
      | _, _, [] => .ok
      | 0, count, x :: _ => match synFormula 64 count x with
        | .ok _ => .ok
        | .error e => syntaxMember "3.9a" "3.9b" e
      | i + 1, count, x :: rest => match synFormula 64 count x with
        | .ok (_, next) => go i next rest
        | .error _ => .ok
    go k count xs.toList
  | _, _ => .ok

/-! ## 4.7: the typing walk -/

/-- Enter one node: the running total gains one; past 10,000 it is `_Checker`'s `ResourceLimit`. -/
def tick (n : Nat) : Except String Nat :=
  if n + 1 > 10000 then .error "ResourceLimit: AST exceeds 10,000 nodes" else .ok (n + 1)

def typeTerm (E : VE.Environment) (Γ : List String) (n : Nat) (t : VE.Term) : Except String (String × Nat) := do
  let n ← tick n
  let s ← termSort E Γ t
  pure (s, n)

/-- `Norms.typeDiagnostic` with its checks and texts in its order, each node counted on entering it. Before a
    binder's sort is looked up, `$string` under `data@0` is `_Checker`'s `UnsupportedProfile`. -/
def typeWalk (E : VE.Environment) (data : Bool) : List String → Nat → VE.Formula → Except String Nat
  | _, n, .top | _, n, .bottom => tick n
  | Γ, n, .unary p t => do
    let n ← tick n
    let some sig := E.predicates p | throw s!"UnknownSymbol: Unknown predicate {pyRepr p}"
    unless sig.length == 1 do throw s!"TypeMismatch: Predicate {pyRepr p} has arity {sig.length}, not 1"
    let (a, n) ← typeTerm E Γ n t
    unless [a] == sig do
      throw s!"TypeMismatch: Predicate {pyRepr p} expects {pyTuple sig}, received {pyTuple [a]}"
    pure n
  | Γ, n, .binary p t u => do
    let n ← tick n
    let some sig := E.predicates p | throw s!"UnknownSymbol: Unknown predicate {pyRepr p}"
    unless sig.length == 2 do throw s!"TypeMismatch: Predicate {pyRepr p} has arity {sig.length}, not 2"
    let (a, n) ← typeTerm E Γ n t
    let (b, n) ← typeTerm E Γ n u
    unless [a, b] == sig do
      throw s!"TypeMismatch: Predicate {pyRepr p} expects {pyTuple sig}, received {pyTuple [a, b]}"
    pure n
  | Γ, n, .eq t u => do
    let n ← tick n
    let (a, n) ← typeTerm E Γ n t
    let (b, n) ← typeTerm E Γ n u
    unless a == b do throw s!"TypeMismatch: Equality requires one sort, received {pyRepr a} and {pyRepr b}"
    pure n
  | Γ, n, .not a => do
    let n ← tick n
    typeWalk E data Γ n a
  | Γ, n, .and a b | Γ, n, .or a b | Γ, n, .implies a b => do
    let n ← tick n
    let n ← typeWalk E data Γ n a
    typeWalk E data Γ n b
  | Γ, n, .all s a | Γ, n, .ex s a => do
    let n ← tick n
    if data && s == "$string" then throw "UnsupportedProfile: $string quantification requires data stage 2"
    unless E.sorts.contains s do throw s!"UnknownSymbol: Unknown binder sort {pyRepr s}"
    typeWalk E data (s :: Γ) n a

/-- One rule's guard and carve-outs, in order, from the running total `n`. -/
def typeRule (E : VE.Environment) (data : Bool) (rule : Json) (n : Nat) : Option (Except String Nat) := do
  let .str p := ruleField rule "predicate" | none
  let sig ← E.predicates p
  let formulas ← (synRule rule).toOption
  pure (formulas.foldlM (typeWalk E data sig.reverse) n)

/-- The member of 4.7 named by the leading word of the text at the refused node; any other names none. -/
def typingMember (e : String) : ClassifierResult :=
  if e.startsWith "TypeMismatch:" then .fail "4.7a" (message e)
  else if e.startsWith "UnknownSymbol:" then .fail "4.7b" (message e)
  else if e.startsWith "UnboundVariable:" then .fail "4.7c" (message e)
  else if e.startsWith "ResourceLimit:" then .fail "4.7d" (message e)
  else if e.startsWith "UnsupportedProfile:" then .fail "4.7e" (message e)
  else .ok

/-- 4.7 at the `i`-th rule: one running total over the earlier rules (each well typed, by rule 2), then this one. -/
def ruleTyping (root : Json) (i : Nat) : ClassifierResult :=
  match typingEnvironment root with
  | none => .ok
  | some E =>
    let data := (profiles root).contains "data@0"
    let rec go : Nat → Nat → List Json → ClassifierResult
      | _, _, [] => .ok
      | 0, n, rule :: _ => match typeRule E data rule n with
        | some (.error e) => typingMember e
        | _ => .ok
      | j + 1, n, rule :: rest => match typeRule E data rule n with
        | some (.ok next) => go j next rest
        | _ => .ok
    go i 0 (rulesOf root)

/-! ## 6.1 to 6.3: the document graphs -/

/-- The rules as nodes with their names, predicates and `over`; the formulas are not read. `none` before the
    phases `rule-shape` and `rules` hold. -/
def skeleton (root : Json) : Option VE.Norms.Tree := do
  let nodes ← (rulesOf root).mapM fun rule => do
    let .str name := ruleField rule "name" | none
    let .str pred := ruleField rule "predicate" | none
    let over ← (VE.Bridge.strings (ruleField rule "over")).toOption
    pure ({ name, pred, sign := false, guard := .top, carveOuts := [], over } : VE.Norms.Node)
  pure ⟨[], [], nodes⟩

/-- The regulated predicates of the submitted vocabulary, in its order. -/
def regulatedNames (root : Json) : List String :=
  match (environmentOf root).getObjVal? "vocabulary" >>= (·.getObjVal? "predicates") >>= VE.Bridge.fields with
  | .ok preds => preds.filterMap fun (p, entry) => if (entry.getObjVal? "regulated").isOk then some p else none
  | .error _ => []

/-- 6.3's graph, as `NormDocument` builds it: one node per regulated predicate, and an edge from a rule's
    predicate to each predicate its guard or carve-outs mention (only regulated ones are nodes). -/
def layerGraph (root : Json) : Option (List VE.Route.DepNode) := do
  let mentioned ← (rulesOf root).mapM fun rule => do
    let .str p := ruleField rule "predicate" | none
    let formulas ← (synRule rule).toOption
    pure (p, formulas.flatMap VE.Norms.preds)
  pure ((regulatedNames root).map fun q =>
    ⟨q, mentioned.flatMap fun (p, ms) => if p == q then ms else []⟩)

def cycle (e : String) : HookResult :=
  if e.startsWith "DependencyCycle: " then .fail [("detail", .str (after "DependencyCycle: " e))] else .ok

def predicate : String → Json → List Pointer → HookResult
  -- 1.1
  | "w1_environment", root, _ => match w1Environment (environmentOf root) with
    | .ok () => .ok
    | .error e => .fail (message e)
  -- 4.3
  | "rule_name_not_reserved", root, items => match itemValue root items 0 with
    | some rule => match ruleField rule "name" with
      | .str n => if underDefaults root && n.startsWith "unsaid--" then .fail [] else .ok
      | _ => .ok
    | none => .ok
  -- 4.4
  | "regulated_predicate", root, items => match itemValue root items 0 with
    | some rule => match ruleField rule "predicate" with
      | .str p =>
        let entry := (((environmentOf root).getObjValD "vocabulary").getObjValD "predicates").getObjValD p
        match entry with
        | .obj _ => if (entry.getObjVal? "regulated").isOk then .ok else .fail []
        | _ => .fail []
      | _ => .ok
    | none => .ok
  -- 5.2: the item is a name in the rule's `over`, the enclosing item the rule
  | "over_same_predicate", root, items => match itemValue root items 0, itemValue root items 1 with
    | some (.str m), some rule =>
      match (rulesOf root).find? (fun r => same (ruleField r "name") (.str m)) with
      | some parent =>
        if same (ruleField parent "predicate") (ruleField rule "predicate") then .ok
        else .fail [("rule", ruleField rule "name"), ("predicate", ruleField rule "predicate"),
          ("parent_predicate", ruleField parent "predicate")]
      | none => .ok
    | _, _ => .ok
  -- 6.1
  | "precedence_acyclic", root, _ => match skeleton root with
    | some T => match VE.Route.dependencyOrder (VE.Norms.precedenceNodes T) with
      | .ok _ => .ok
      | .error e => cycle e
    | none => .ok
  -- 6.2: `Norms.check`'s height, with its fuel
  | "precedence_depth_fits", root, _ => match skeleton root with
    | some T => if T.nodes.any (fun N => VE.Norms.height T T.nodes.length N > 16) then .fail [] else .ok
    | none => .ok
  -- 6.3
  | "layers_acyclic", root, _ => match layerGraph root with
    | some ns => match VE.Route.dependencyOrder ns with
      | .ok _ => .ok
      | .error e => cycle e
    | none => .ok
  | _, _, _ => .ok

def classifier : String → Json → List Pointer → ClassifierResult
  -- 3.8: the guard with the rule's fresh count
  | "guard_syntax", root, items => match itemValue root items 0 with
    | some rule => match synFormula 64 0 (ruleField rule "guard") with
      | .ok _ => .ok
      | .error e => syntaxMember "3.8a" "3.8b" e
    | none => .ok
  -- 3.9: the item is a carve-out, the enclosing item the rule
  | "carve_out_syntax", root, items => match itemValue root items 1, itemIndex items 0 with
    | some rule, some k => carveOutSyntax rule k
    | _, _ => .ok
  -- 4.7
  | "rule_typing", root, items => match itemIndex items 0 with
    | some i => ruleTyping root i
    | none => .ok
  | _, _, _ => .ok

def view : String → Json → Json
  | _, v => v

def hooks : Hooks := ⟨predicate, classifier, view⟩

/-! ## The adapter -/

/-- The profiles a source of either unit may list (spec 2.2); any other is dispatched elsewhere or refused by
    the routes before their validator runs. -/
def domainProfiles : List String :=
  ["data@0", "definitions@0", "documents@1", "norm-defaults@0", "norms@0", "relational-fol@0", "time@0"]

/-- The norm objects of an `admission` case: the `content` of each unit whose `kind` is `norm` and whose
    `content` is an object with a member `norm`, in document order; `null`, outside the domain, when the
    document is not an object with a `units` array (Python's `active_norms` gives `None`). -/
def activeNorms (document : Json) : Json :=
  match document.getObjValD "units" with
  | .arr us => .arr (us.filterMap fun u =>
      match u.getObjValD "kind", u.getObjValD "content" with
      | .str "norm", c@(.obj _) => if (c.getObjVal? "norm").isOk then some c else none
      | _, _ => none)
  | _ => .null

def outsideDomain : String := "UnsupportedProfile: the case is outside the unit's domain"

/-- The domain conditions of 2.2 shared by both units: `norms` an array of objects, every member of an array
    `profiles` a string in `domainProfiles` (a member that is not a string is outside it, as in Python's
    `in_domain`), and no quantity schema. -/
def inSharedDomain (environment norms : Json) : Bool :=
  let objects := match norms with
    | .arr xs => xs.all fun x => match x with
      | .obj _ => true
      | _ => false
    | _ => false
  let listed := match environment.getObjValD "profiles" with
    | .arr ps => ps.all fun p => match p with
      | .str s => domainProfiles.contains s
      | _ => false
    | _ => true
  objects && listed && !(environment.getObjVal? "unit_schema").isOk &&
    !(environment.getObjVal? "units").isOk

/-- The root `{environment, norms}` of a case of one of `kinds` (or of an `admission` case), refused when the
    case kind has no input or the source is outside the domain. -/
def sourceAdapter (kinds : String → Bool) (inDomain : Json → Json → Bool) (case : Json) : Except String Json :=
  let build (norms : Json) : Except String Json :=
    let environment := case.getObjValD "environment"
    if inDomain environment norms then .ok (Json.mkObj [("environment", environment), ("norms", norms)])
    else .error outsideDomain
  match case.getObjValD "kind" with
  | .str "admission" => build (activeNorms (case.getObjValD "document"))
  | .str kind =>
    if kinds kind then build (case.getObjValD "norms")
    else .error s!"UnsupportedProfile: case kind {kind} has no wire contract input"
  | kind => .error s!"UnsupportedProfile: case kind {kind.compress} has no wire contract input"

/-- The adapter `norm_source` (spec 2.2): `norm-defaults@0` is not listed. -/
def adapter (case : Json) : Except String Json :=
  sourceAdapter (fun k => k == "norms-elaborate" || k == "norms-conflict" || k == "norms-certificate")
    (fun environment norms => inSharedDomain environment norms &&
      !(VE.NormDefaults.Wire.profilesOf environment).contains VE.NormDefaults.Wire.profile) case

/-- The names this module registers. -/
def registered : List String :=
  ["w1_environment", "rule_name_not_reserved", "regulated_predicate", "over_same_predicate", "precedence_acyclic",
   "precedence_depth_fits", "layers_acyclic", "guard_syntax", "carve_out_syntax", "rule_typing"]

#guard Tables.Norms.table.hookNames.all registered.contains

/-! L8: where the names are strings, the syntax walk is `budgetFormula`. -/

def sameAsBudget (count : Nat) (j : Json) : Bool :=
  match synFormula 64 count j, VE.Norms.Wire.budgetFormula 64 count j with
  | .ok a, .ok b => a == b
  | .error a, .error b => a == b
  | _, _ => false

def num (n : Int) : Json := toJson n

def l8Samples : List Json :=
  let atom := Json.arr #[.str "unary", .str "c", .arr #[.str "var", (num 0)]]
  let chain (k : Nat) (inner : Json) : Json := (List.range k).foldl (fun j _ => .arr #[.str "not", j]) inner
  let reach := Json.arr #[.str "reach", .str "plus", .arr #[.str "named", .str "c"],
    .arr #[.str "var", (num 0)], .arr #[.str "var", (num 0)]]
  [atom, .arr #[.str "top"], (num 5), .arr #[], .arr #[.str "binary", .str "c", .arr #[.str "var", (num 0)],
     .arr #[.str "const", .str "k"]],
   .arr #[.str "unary", .str "c", .arr #[.str "var", (num (-1))]],
   .arr #[.str "unary", .str "c", .arr #[.str "var", (num 9007199254740992)]],
   .arr #[.str "unary", .str "c", .arr #[.str "var", .bool true]],
   .arr #[.str "forall", .str "assistant", .arr #[.str "eq", .arr #[.str "var", (num 0)],
     .arr #[.str "var", (num 0)]]],
   .arr #[.str "exists", .str "s", .arr #[.str "implies", atom, .arr #[.str "or", atom, .arr #[.str "bottom"]]]],
   chain 63 (.arr #[.str "top"]), chain 64 (.arr #[.str "top"]), chain 65 (.arr #[.str "top"]),
   .arr #[.str "and", reach, chain 65 (.arr #[.str "top"])], .arr #[.str "and", chain 65 (.arr #[.str "top"]), reach],
   .arr #[.str "and", atom], .arr #[.str "lt", .arr #[.str "var", (num 0)], .arr #[.str "var", (num 0)]]]

#guard l8Samples.all (sameAsBudget 0)
#guard l8Samples.all (sameAsBudget 9990)
#guard l8Samples.all (sameAsBudget 10000)

/-! The walk reads a name that is not a string, where `budgetFormula` refuses the node (spec 2.5, N33 to N35). -/

#guard (synFormula 64 0 (.arr #[.str "unary", (num 7), .arr #[.str "var", (num 0)]])).toBool
#guard (synFormula 64 0 (.arr #[.str "eq", .arr #[.str "const", (num 5)], .arr #[.str "var", (num 0)]])).toBool
#guard (synFormula 64 0 (.arr #[.str "forall", (num 5), .arr #[.str "top"]])).toBool
#guard !(VE.Norms.Wire.budgetFormula 64 0 (.arr #[.str "forall", (num 5), .arr #[.str "top"]])).toBool

end VE.WireContract.Hooks.Norms
