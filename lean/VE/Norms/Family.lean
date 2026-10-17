import VE.Norms.Tree
import VE.Core.Substitution
import VE.Core.Conservativity
import VE.Order.Syntax
import VE.Order.Wire
import VE.Closure.Bridge
import VE.Core.Bridge
import VE.Norms.Plain

/-! Norm documents whose guards leave the first-order fragment, on the closure,
core and order families (lean-first batch 14b, the stage-2c gap "non-first-order
norm guards"): reachability, n-ary atoms, integer comparisons and arithmetic.

The norms theory (`VE.Norms`) is first-order, and a first-order document on a
family is still regenerated over the family's FOL view
(`VE.Service.FamilyNorms`). The regeneration here is the same construction over
the family's own formulas, written once over a `Syntax` and used at
`VE.Core.Formula` (the closure family embeds by `VE.Core.embedClosure`) and at
`VE.Order.Formula`:

* `elaborate`: one layer premise per regulated predicate, in the dependency
  order of the regulated predicates, `∀x̄. (P → p) ∧ (N → ¬p) ∧ ((¬P ∧ ¬N) → d)`
  with the selections `P`/`N` of section 4 (as `VE.Norms.Elaborate` builds them);
* `targets`: the conflict targets, each regulated predicate's `P ∧ N` and each
  declared pair's `O_r ∧ ¬O_m`, with the earlier regulated atoms replaced by
  their completed outcomes at the atom's arguments (as `VE.Norms.Flagged.pyTargets`
  builds them).

Guards are kept as written: a reachability, n-ary or arithmetic subformula is copied,
and only the unary and binary atoms of regulated predicates are replaced. A
regulated predicate never occurs inside a closure edge (`regulatedEdge`
refuses it), and its arguments are entity-sorted, so its atoms are always
unary or binary. What an accepted certificate over these premises proves is
the family checker's soundness theorem (`VE.Service.FamilyNorms`); no theorem
here relates the premises to the Catala reading of section 4. -/
namespace VE.Norms.Family
open Lean

/-- The connectives, atoms and substitution of one family's formulas. -/
structure Syntax (F : Type) where
  top : F
  bottom : F
  not : F → F
  and : F → F → F
  or : F → F → F
  implies : F → F → F
  all : String → F → F
  /-- The atom of a unary or binary symbol applied to its situation variables. -/
  atom : String → List String → F
  /-- Replace every unary and binary atom of a tabled symbol by its formula at
  the atom's arguments; every other subformula is kept. -/
  substWith : (String → Option F) → F → F
  /-- The predicates a formula mentions. -/
  preds : F → List String
  /-- Variable `i` becomes the `i`-th named constant (de Bruijn order). -/
  instConsts : List String → F → F

/-- A rule over a family's formulas, typed in `(sorts pred).reverse`. -/
structure Rule (F : Type) where
  name : String
  pred : String
  sign : Bool
  guard : F
  carveOuts : List F
  over : List String

structure Doc (F : Type) where
  regulated : List Regulated
  rules : List (Rule F)

section
variable {F : Type} (S : Syntax F) (D : Doc F)

def anyF (l : List F) : F := l.foldl S.or S.bottom
def allF (l : List F) : F := l.foldl S.and S.top
def bindAll (sorts : List String) (body : F) : F := sorts.foldr S.all body

def rulesOn (p : String) : List (Rule F) := D.rules.filter (·.pred == p)

/-- The exceptions of `N`, sorted by name, one per occurrence in a rule's `over`
(`VE.Norms.children`). -/
def children (N : Rule F) : List (Rule F) :=
  sortBy (fun a b => decide (a.name < b.name))
    (D.rules.flatMap (fun C => if C.pred == N.pred then (C.over.filter (· == N.name)).map (fun _ => C) else []))

def applies (N : Rule F) : F := S.and N.guard (S.not (anyF S N.carveOuts))

def yields : Nat → Rule F → F
  | 0, N => S.or (applies S N) (anyF S [])
  | f + 1, N => S.or (applies S N) (anyF S ((children D N).map (yields f)))

def selects (N : Rule F) : F :=
  S.and (applies S N) (S.not (anyF S ((children D N).map (yields S D D.rules.length))))

def decides (p : String) (sign : Bool) : F :=
  anyF S (((rulesOn D p).filter (·.sign == sign)).map (selects S D))

def pos (p : String) : F := decides S D p true
def neg (p : String) : F := decides S D p false

/-- The completed outcome: `P_p` for deny, `¬N_p` for allow. -/
def outcome (r : Regulated) : F :=
  if r.allowByDefault then S.not (neg S D r.name) else pos S D r.name

def elabBody (r : Regulated) : F :=
  let P := pos S D r.name
  let N := neg S D r.name
  let A := S.atom r.name r.sorts
  allF S [S.implies P A, S.implies N (S.not A),
    S.implies (S.and (S.not P) (S.not N)) (if r.allowByDefault then A else S.not A)]

def elabPremise (r : Regulated) : F := bindAll S r.sorts (elabBody S D r)

/-- The regulated predicates a predicate's rules mention, as the dependency
nodes of the regulated layer order: sorted by name, mentions sorted and
distinct, as Python's `dependency_order` request lists them. -/
def depNodes : List VE.Route.DepNode :=
  let names := D.regulated.map (·.name)
  sortBy (fun a b => decide (a.name < b.name)) (D.regulated.map fun r =>
    ⟨r.name, sortBy (fun a b => decide (a < b))
      (((rulesOn D r.name).flatMap (fun N => (N.guard :: N.carveOuts).flatMap S.preds)).filter
        names.contains).eraseDups⟩)

/-- The regulated predicates in layer order (or the cycle diagnostic). -/
def layers : Except String (List Regulated) := do
  let order ← VE.Route.dependencyOrder (depNodes S D)
  pure (order.filterMap fun n => D.regulated.find? (·.name == n))

/-- Each earlier layer's completed outcome, its own earlier atoms replaced. -/
def regTable (ls : List Regulated) : Nat → String → Option F
  | 0 => fun _ => none
  | k + 1 => fun n => match ls[k]? with
    | some r => if n = r.name then some (S.substWith (regTable ls k) (outcome S D r)) else regTable ls k n
    | none => regTable ls k n

def regSubst (ls : List Regulated) (p : String) (φ : F) : F :=
  S.substWith (regTable S D ls ((ls.map (·.name)).idxOf p)) φ

def outcomeBase (ls : List Regulated) (n : String) : F :=
  match D.regulated.find? (·.name == n) with
  | some r => regSubst S D ls n (outcome S D r)
  | none => S.bottom

/-- The premises of `norms-elaborate`, labelled, in layer order. -/
def elaborate (ls : List Regulated) : List (String × F) :=
  ls.map fun r => ("layer:norms:" ++ r.name, elabPremise S D r)

/-- The conflict targets in Python `NormDocument.conflict_targets`' order. -/
def targets (ls : List Regulated) : List (String × List String × F) :=
  ls.map (fun r => (r.name, r.sorts,
      S.and (regSubst S D ls r.name (pos S D r.name)) (regSubst S D ls r.name (neg S D r.name)))) ++
    (pairs ⟨D.regulated, [], []⟩).map (fun pr => (pr.req ++ "->" ++ pr.perm, pr.sorts,
      S.and (outcomeBase S D ls pr.req) (S.not (outcomeBase S D ls pr.perm))))

/-- A target's certificate conclusion `∀x̄. ¬conflict`. -/
def targetConclusion (t : String × List String × F) : F := bindAll S t.2.1 (S.not t.2.2)

end

/-! ## The core family (closure formulas embed) -/

/-- `σ` of an argument list: variable `i` becomes the `i`-th argument
(de Bruijn order, the last argument first). -/
def argSub (args : List VE.Term) (i : Nat) : VE.Term := args[i]?.getD (.var i)

def coreSubstWith (tbl : String → Option VE.Core.Formula) : VE.Core.Formula → VE.Core.Formula
  | .unary q t => match tbl q with
    | some φ => φ.subst (argSub [t])
    | none => .unary q t
  | .binary q t u => match tbl q with
    | some φ => φ.subst (argSub [u, t])
    | none => .binary q t u
  | .not a => .not (coreSubstWith tbl a)
  | .and a b => .and (coreSubstWith tbl a) (coreSubstWith tbl b)
  | .or a b => .or (coreSubstWith tbl a) (coreSubstWith tbl b)
  | .implies a b => .implies (coreSubstWith tbl a) (coreSubstWith tbl b)
  | .all s a => .all s (coreSubstWith tbl a)
  | .ex s a => .ex s (coreSubstWith tbl a)
  | a => a

def corePreds : VE.Core.Formula → List String
  | .unary p _ | .binary p _ _ | .atom p _ | .reachNamed _ p _ _ => [p]
  | .reachBody _ _ a _ _ | .not a | .all _ a | .ex _ a => corePreds a
  | .and a b | .or a b | .implies a b => corePreds a ++ corePreds b
  | _ => []

def coreSyntax : Syntax VE.Core.Formula where
  top := .top
  bottom := .bottom
  not := .not
  and := .and
  or := .or
  implies := .implies
  all := .all
  atom p sorts := match sorts with
    | [_] => .unary p (.var 0)
    | [_, _] => .binary p (.var 1) (.var 0)
    | _ => .bottom
  substWith := coreSubstWith
  preds := corePreds
  instConsts cs φ := φ.subst (argSub (cs.map .const))

/-- A closure edge naming a regulated predicate, or a closure body mentioning
one (Python `_regulated_closure`). -/
def regulatedEdge (regulated : List String) : VE.Core.Formula → Bool
  | .reachNamed _ r _ _ => regulated.contains r
  | .reachBody _ _ a _ _ => (corePreds a).any regulated.contains
  | .not a | .all _ a | .ex _ a => regulatedEdge regulated a
  | .and a b | .or a b | .implies a b => regulatedEdge regulated a || regulatedEdge regulated b
  | _ => false

def encodeTerm : VE.Term → Json
  | .var i => Json.arr #[.str "var", toJson i]
  | .const c => Json.arr #[.str "const", .str c]

def encodeKind : VE.Core.Kind → Json
  | .plus => .str "plus"
  | .star => .str "star"

/-- The wire form of a core formula (Python `ve/ast.py` `_to_data`). -/
def encodeCore : VE.Core.Formula → Json
  | .top => Json.arr #[.str "top"]
  | .bottom => Json.arr #[.str "bottom"]
  | .unary p t => Json.arr #[.str "unary", .str p, encodeTerm t]
  | .binary p t u => Json.arr #[.str "binary", .str p, encodeTerm t, encodeTerm u]
  | .atom p ts => Json.arr #[.str "atom", .str p, Json.arr (ts.map encodeTerm).toArray]
  | .eq t u => Json.arr #[.str "eq", encodeTerm t, encodeTerm u]
  | .not a => Json.arr #[.str "not", encodeCore a]
  | .and a b => Json.arr #[.str "and", encodeCore a, encodeCore b]
  | .or a b => Json.arr #[.str "or", encodeCore a, encodeCore b]
  | .implies a b => Json.arr #[.str "implies", encodeCore a, encodeCore b]
  | .all s a => Json.arr #[.str "forall", .str s, encodeCore a]
  | .ex s a => Json.arr #[.str "exists", .str s, encodeCore a]
  | .reachNamed k r t u => Json.arr #[.str "reach", encodeKind k, Json.arr #[.str "named", .str r],
      encodeTerm t, encodeTerm u]
  | .reachBody k s a t u => Json.arr #[.str "reach", encodeKind k,
      Json.arr #[.str "body", .str s, encodeCore a], encodeTerm t, encodeTerm u]

/-! ## The order family -/

def orderLift : VE.Order.Term → VE.Order.Term
  | .var i => .var (i + 1)
  | .add t u => .add (orderLift t) (orderLift u)
  | .scale z t => .scale z (orderLift t)
  | t => t

def orderLiftSub (σ : Nat → VE.Order.Term) : Nat → VE.Order.Term
  | 0 => .var 0
  | i + 1 => orderLift (σ i)

def orderSubstTerm (σ : Nat → VE.Order.Term) : VE.Order.Term → VE.Order.Term
  | .var i => σ i
  | .add t u => .add (orderSubstTerm σ t) (orderSubstTerm σ u)
  | .scale z t => .scale z (orderSubstTerm σ t)
  | t => t

def orderSubst (σ : Nat → VE.Order.Term) : VE.Order.Formula → VE.Order.Formula
  | .unary p t => .unary p (orderSubstTerm σ t)
  | .binary p t u => .binary p (orderSubstTerm σ t) (orderSubstTerm σ u)
  | .eq t u => .eq (orderSubstTerm σ t) (orderSubstTerm σ u)
  | .lt t u => .lt (orderSubstTerm σ t) (orderSubstTerm σ u)
  | .le t u => .le (orderSubstTerm σ t) (orderSubstTerm σ u)
  | .not a => .not (orderSubst σ a)
  | .and a b => .and (orderSubst σ a) (orderSubst σ b)
  | .or a b => .or (orderSubst σ a) (orderSubst σ b)
  | .implies a b => .implies (orderSubst σ a) (orderSubst σ b)
  | .all s a => .all s (orderSubst (orderLiftSub σ) a)
  | .ex s a => .ex s (orderSubst (orderLiftSub σ) a)
  | a => a

def orderArgSub (args : List VE.Order.Term) (i : Nat) : VE.Order.Term := args[i]?.getD (.var i)

def orderSubstWith (tbl : String → Option VE.Order.Formula) : VE.Order.Formula → VE.Order.Formula
  | .unary q t => match tbl q with
    | some φ => orderSubst (orderArgSub [t]) φ
    | none => .unary q t
  | .binary q t u => match tbl q with
    | some φ => orderSubst (orderArgSub [u, t]) φ
    | none => .binary q t u
  | .not a => .not (orderSubstWith tbl a)
  | .and a b => .and (orderSubstWith tbl a) (orderSubstWith tbl b)
  | .or a b => .or (orderSubstWith tbl a) (orderSubstWith tbl b)
  | .implies a b => .implies (orderSubstWith tbl a) (orderSubstWith tbl b)
  | .all s a => .all s (orderSubstWith tbl a)
  | .ex s a => .ex s (orderSubstWith tbl a)
  | a => a

def orderPreds : VE.Order.Formula → List String
  | .unary p _ | .binary p _ _ => [p]
  | .not a | .all _ a | .ex _ a => orderPreds a
  | .and a b | .or a b | .implies a b => orderPreds a ++ orderPreds b
  | _ => []

def orderSyntax : Syntax VE.Order.Formula where
  top := .top
  bottom := .bottom
  not := .not
  and := .and
  or := .or
  implies := .implies
  all := .all
  atom p sorts := match sorts with
    | [_] => .unary p (.var 0)
    | [_, _] => .binary p (.var 1) (.var 0)
    | _ => .bottom
  substWith := orderSubstWith
  preds := orderPreds
  instConsts cs φ := orderSubst (orderArgSub (cs.map .const)) φ

def encodeOrderTerm : VE.Order.Term → Json
  | .var i => Json.arr #[.str "var", toJson i]
  | .const c => Json.arr #[.str "const", .str c]
  | .num z => Json.arr #[.str "num", .str (toString z)]
  | .add t u => Json.arr #[.str "add", encodeOrderTerm t, encodeOrderTerm u]
  | .scale z t => Json.arr #[.str "scale", .str (toString z), encodeOrderTerm t]

/-- The wire form of an order formula (Python `ve/ast.py` `_to_data`). -/
def encodeOrder : VE.Order.Formula → Json
  | .top => Json.arr #[.str "top"]
  | .bottom => Json.arr #[.str "bottom"]
  | .unary p t => Json.arr #[.str "unary", .str p, encodeOrderTerm t]
  | .binary p t u => Json.arr #[.str "binary", .str p, encodeOrderTerm t, encodeOrderTerm u]
  | .eq t u => Json.arr #[.str "eq", encodeOrderTerm t, encodeOrderTerm u]
  | .lt t u => Json.arr #[.str "lt", encodeOrderTerm t, encodeOrderTerm u]
  | .le t u => Json.arr #[.str "le", encodeOrderTerm t, encodeOrderTerm u]
  | .not a => Json.arr #[.str "not", encodeOrder a]
  | .and a b => Json.arr #[.str "and", encodeOrder a, encodeOrder b]
  | .or a b => Json.arr #[.str "or", encodeOrder a, encodeOrder b]
  | .implies a b => Json.arr #[.str "implies", encodeOrder a, encodeOrder b]
  | .all s a => Json.arr #[.str "forall", .str s, encodeOrder a]
  | .ex s a => Json.arr #[.str "exists", .str s, encodeOrder a]

/-- Whether an order formula is first-order (no comparison, no arithmetic term). -/
def orderTermFol : VE.Order.Term → Bool
  | .var _ | .const _ => true
  | _ => false

def orderFol : VE.Order.Formula → Bool
  | .top | .bottom => true
  | .unary _ t => orderTermFol t
  | .binary _ t u | .eq t u => orderTermFol t && orderTermFol u
  | .lt _ _ | .le _ _ => false
  | .not a | .all _ a | .ex _ a => orderFol a
  | .and a b | .or a b | .implies a b => orderFol a && orderFol b

end VE.Norms.Family

/-! ## Reading and checking a document -/

namespace VE.Norms.Family
open Lean

/-- A family's formulas as the regeneration reads them: the decoder of a guard
or carve-out, its typing in a rule's context, its node count, the closure-edge
test and the wire form. -/
structure Reader (F : Type) where
  ops : Syntax F
  decode : Json → Except String F
  check : List String → F → Bool
  nodes : F → Nat
  regulatedEdge : List String → F → Bool
  encode : F → Json

def height {F : Type} (D : Doc F) : Nat → Rule F → Nat
  | 0, _ => 1
  | f + 1, N => 1 + ((children D N).map (height D f)).foldl max 0

/-- The rules, checked in `Tree.check`'s order and with its diagnostics: names,
regulated predicates, carve-out counts, each formula's decoding, typing in the
rule's context and the shared node budget, closure edges, precedence edges, the
precedence DAG and its depth. -/
def decodeDoc {F : Type} (R : Reader F) (profiles : List String) (regulated : List Regulated)
    (norms : Json) : Except String (Doc F) := do
  let units ← match norms with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: norms must be an array"
  if units.length > 256 then throw "ResourceLimit: rules"
  let raws ← units.mapM VE.Norms.Wire.normFields
  let regNames := regulated.map (·.name)
  let mut names : List String := []
  let mut nodes := 0
  let mut rules : List (Rule F) := []
  for (name, pred, sign, guardJ, carveJ, over) in raws do
    unless ruleName name do throw s!"InvalidInput: invalid rule name {pyRepr name}"
    if names.contains name then throw s!"DuplicateDeclaration: rule {name}"
    if profiles.contains "norm-defaults@0" && name.startsWith "unsaid--" then
      throw s!"InvalidInput: reserved name {name}"
    names := names ++ [name]
    match regulated.find? (·.name == pred) with
    | none => throw s!"UnknownSymbol: regulated predicate {pred}"
    | some r =>
      if carveJ.length > 8 then throw "InvalidInput: invalid sign or too many carve-outs"
      let mut formulas : List F := []
      for x in guardJ :: carveJ do
        let φ ← R.decode x
        unless R.check r.sorts.reverse φ do throw s!"InvalidInput: ill-typed rule {name}"
        nodes := nodes + R.nodes φ
        if nodes > 10000 then throw "ResourceLimit: AST exceeds 10,000 nodes"
        if R.regulatedEdge regNames φ then throw "UnsupportedProfile: regulated closure edge in norm guard"
        formulas := formulas ++ [φ]
      match formulas with
      | guard :: carveOuts => rules := rules ++ [⟨name, pred, sign, guard, carveOuts, over⟩]
      | [] => throw "InvalidInput: invalid rule"
  for N in rules do
    for m in N.over do
      match rules.find? (·.name == m) with
      | none => throw s!"UnknownRule: rule {m}"
      | some M =>
        unless M.pred == N.pred do
          throw s!"PrecedenceAcrossPredicates: rule {N.name} on {N.pred}, rule {M.name} on {M.pred}"
  match VE.Route.dependencyOrder (rules.map fun N => ⟨N.name, N.over⟩) with
  | .error e => throw e
  | .ok _ => pure ()
  let D : Doc F := ⟨regulated, rules⟩
  if rules.any (fun N => height D rules.length N > 16) then throw "ResourceLimit: precedence depth"
  pure D

/-- The regulated declarations a family document's rules range over, with the
arity and sort checks of `Tree.check`. -/
def regulatedOf (environment : Json) : Except String (List Regulated) := do
  let vocabulary ← environment.getObjVal? "vocabulary"
  let regulated ← VE.Norms.Plain.decodeRegulatedAll (← VE.Bridge.fields (← vocabulary.getObjVal? "predicates"))
  let sorts := (← VE.Bridge.fields (← vocabulary.getObjVal? "sorts")).map Prod.fst
  for r in regulated do
    unless r.sorts.length == 1 || r.sorts.length == 2 do
      throw s!"UnsupportedArity: regulated predicate {r.name}"
    unless r.sorts.all sorts.contains do throw s!"UnknownSymbol: sort of {r.name}"
  pure regulated

def closureReader (E : VE.Environment) : Reader VE.Core.Formula where
  ops := coreSyntax
  decode j := VE.Core.embedClosure <$> VE.Closure.Bridge.decodeFormula 64 j
  check Γ a := a.check E Γ
  nodes := VE.Core.Bridge.formulaNodes
  regulatedEdge := regulatedEdge
  encode := encodeCore

def coreReader (E : VE.Environment) : Reader VE.Core.Formula where
  ops := coreSyntax
  decode := VE.Core.Bridge.decodeFormula 64
  check Γ a := a.check E Γ
  nodes := VE.Core.Bridge.formulaNodes
  regulatedEdge := regulatedEdge
  encode := encodeCore

def orderReader (E : VE.Order.Environment) : Reader VE.Order.Formula where
  ops := orderSyntax
  decode := VE.Order.Wire.decodeFormula 64
  check Γ a := a.check E (Γ.map .user)
  nodes := VE.Order.Wire.formulaNodes
  regulatedEdge _ _ := false
  encode := encodeOrder

/-! ## Which documents leave the first-order fragment -/

/-- Whether a declaration uses the integer sort. -/
def usesInt (environment : Json) : Bool :=
  let vocabulary := environment.getObjValD "vocabulary"
  let predicates := match VE.Bridge.fields (vocabulary.getObjValD "predicates") with
    | .ok ps => ps.any fun (_, e) => match e.getObjValD "arguments" with
      | .arr xs => xs.contains (.str "$int")
      | _ => false
    | .error _ => false
  let constants := match VE.Bridge.fields (vocabulary.getObjValD "constants") with
    | .ok cs => cs.any fun (_, e) => e.getObjValD "sort" == .str "$int"
    | .error _ => false
  predicates || constants

/-- Whether a guard or carve-out is first-order in its family. A formula the
family decoder refuses counts as first-order: the FOL view's decoder reports it. -/
def firstOrderFormula (order : Bool) (j : Json) : Bool :=
  if order then match VE.Order.Wire.decodeFormula 64 j with
    | .ok a => orderFol a
    | .error _ => true
  else match VE.Core.Bridge.decodeFormula 64 j with
    | .ok a => (VE.Core.erase a).isSome
    | .error _ => true

/-- Whether the FOL view carries a declaration's definition: a head of at most
two arguments and a first-order body. The view keeps only unary and binary
predicates, so an n-ary head is dropped and a body mentioning an n-ary atom
does not decode there; such a definition is elaborated by the family's reader. -/
def firstOrderDefinition (order : Bool) (entry : Json) : Bool :=
  match entry.getObjVal? "defined" with
  | .error _ => true
  | .ok payload => VE.Core.Layers.folEntry entry && firstOrderFormula order (payload.getObjValD "body")

/-- Whether the FOL view regenerates a family document: no declaration uses
`$int`, the view carries every definition and every guard and carve-out is
first-order. -/
def firstOrder (environment norms : Json) : Bool :=
  let order := match VE.Route.Gate.profilesOf environment with
    | .ok ps => ps.contains "order@0"
    | .error _ => false
  !usesInt environment &&
  (VE.Core.Layers.predicatesOf environment).all (fun (_, e) => firstOrderDefinition order e) &&
  match norms with
    | .arr xs => xs.all fun u =>
      let raw := u.getObjValD "norm"
      firstOrderFormula order (raw.getObjValD "guard") && match raw.getObjValD "unless" with
        | .arr ys => ys.all (firstOrderFormula order)
        | _ => true
    | _ => true

end VE.Norms.Family
