import VE.Norms.Elaborate

/-! The `unspecified` completion (docs/spec/norm-defaults.md sections 2.1, 2.3 and 7):
documents with unspecified predicates, the elaboration `fill` and the author-side
limits `WellFormedU`.

A `UDoc` is a W1 document plus the names of its `unspecified` predicates; each is
declared in `D.T.regulated` with the placeholder `allowByDefault = false`. `fill U`
is an ordinary W1 document: for every unspecified `p` it declares one fresh base
predicate `unsaid__p` (the filling of the gap) and adds one synthetic rule `F_p`
named `unsaid--p'`, sign `+`, guard `unsaid__p(x̄)`, which becomes the parent of
every root rule on `p`. Nothing else changes, so W1's definitions, checker and
theorems are reused on `fill U` unchanged.

`WellFormedU U` is `WellFormed U.D` plus the conditions that make `fill U` well
formed (`fill_wellFormed`): the unspecified names are regulated, distinct and
carry the placeholder; the names `fill` introduces are unused; and the author-side
limits (i)-(v) of section 7. -/
namespace VE.NormDefaults
open VE.Norms VE.Route

inductive Completion | deny | allow | unspecified
  deriving DecidableEq, Repr

/-- A W1 document plus its `unspecified` predicates; each is declared in
`D.T.regulated` with the placeholder `allowByDefault = false`. Soft, rights and
alternatives instantiate `D` with `soften`, `soften ∘ correlate`, `inlineTree`. -/
structure UDoc where
  D : Doc
  unspec : List String

def completionOf (U : UDoc) (r : Regulated) : Completion :=
  if r.name ∈ U.unspec then .unspecified else if r.allowByDefault then .allow else .deny

/-- The fresh base predicate filling the gap of `p`. -/
def unsaidName (p : String) : String := "unsaid__" ++ p

/-- The name of the synthetic rule on `p` (`_` becomes `-`, as rule names require). -/
def fillName (p : String) : String := "unsaid--" ++ p.map (fun c => if c = '_' then '-' else c)

/-- `F_p`: sign `+`, guard `unsaid__p(x̄)`, no carve-outs, no `over`. -/
def fillNode (r : Regulated) : Node :=
  { name := fillName r.name, pred := r.name, sign := true, guard := atom (unsaidName r.name) r.sorts,
    carveOuts := [], over := [] }

/-- `U.switch p`: `p`'s completion becomes `unspecified` (placeholder `false`, `p`
appended to `unspec`). -/
def UDoc.switch (U : UDoc) (p : String) : UDoc :=
  { D := { U.D with T := { U.D.T with regulated := U.D.T.regulated.map fun r =>
             if r.name = p then { r with allowByDefault := false } else r } },
    unspec := U.unspec ++ [p] }

/-- `p`'s declared argument sorts (`[]` if `p` is not regulated). -/
def sortsOf (D : Doc) (p : String) : List String :=
  ((D.T.regulated.find? (·.name == p)).map (·.sorts)).getD []

def unsaidNames (U : UDoc) : List String := U.unspec.map unsaidName

/-- The declared pairs with an unspecified member. -/
def openPairs (U : UDoc) : List Pair :=
  (pairs U.D.T).filter (fun pr => pr.req ∈ U.unspec ∨ pr.perm ∈ U.unspec)

/-- The members of declared pairs with an unspecified member. -/
def pairMembers (U : UDoc) : List String := (openPairs U).flatMap (fun pr => [pr.req, pr.perm])

/-! ## The elaboration -/

/-- `E‴`: every unsaid predicate is declared with its predicate's sorts. -/
def fillEnv (U : UDoc) : VE.Environment :=
  { U.D.E with predicates := fun n => match U.unspec.find? (fun p => unsaidName p == n) with
      | some p => some (sortsOf U.D p)
      | none => U.D.E.predicates n }

/-- A root rule (empty `over`) on an unspecified predicate gains `over := [F_p]`. -/
def fillRoot (U : UDoc) (N : Node) : Node :=
  if N.pred ∈ U.unspec ∧ N.over = [] then { N with over := [fillName N.pred] } else N

/-- The synthetic rules, in declaration order of their predicates. -/
def fillNodes (U : UDoc) : List Node :=
  (U.D.T.regulated.filter (fun r => r.name ∈ U.unspec)).map fillNode

def fillTree (U : UDoc) : Tree :=
  { U.D.T with nodes := U.D.T.nodes.map (fillRoot U) ++ fillNodes U }

/-- `fill U = (E‴, T‴)`: an ordinary W1 document. -/
def fill (U : UDoc) : Doc := { E := fillEnv U, lits := U.D.lits, T := fillTree U }

/-! ## The author-side conditions -/

/-- The AST nodes of a rule's guard and carve-outs. -/
def ruleNodes (N : Node) : Nat := ((N.guard :: N.carveOuts).map VE.Bridge.formulaNodes).sum

/-- The AST nodes of the synthetic guards. -/
def fillGuardNodes (U : UDoc) : Nat :=
  (U.unspec.map fun p => VE.Bridge.formulaNodes (atom (unsaidName p) (sortsOf U.D p))).sum

/-- Each unspecified name is regulated, once, with the placeholder `false`. -/
def unspecDeclared (U : UDoc) : Bool :=
  decide U.unspec.Nodup &&
  U.unspec.all (fun p => U.D.T.regulated.any (fun r => r.name == p && !r.allowByDefault))

/-- The reserved prefixes are unused by declared layer symbols and rules, and the
names `fill` introduces are free: no declared predicate is `unsaid__p`, no author
rule is `unsaid--p'`. -/
def reservedFree (U : UDoc) : Bool :=
  U.D.T.regulated.all (fun r => !r.name.startsWith "unsaid__") &&
  U.D.T.definitions.all (fun d => !d.name.startsWith "unsaid__") &&
  U.D.T.nodes.all (fun N => !N.name.startsWith "unsaid--") &&
  U.unspec.all (fun p => U.D.E.predicates (unsaidName p) == none) &&
  U.D.T.nodes.all (fun N => !(U.unspec.map fillName).contains N.name)

/-- The author-side limits of section 8:
(i) `ruleName (fillName p)`; (ii) the fill names are distinct; (iii) rules plus
unspecified predicates at most 256; (iv) precedence height at most 15 for every
author rule on an unspecified predicate; (v) the AST budget with the `F_p` guards. -/
def limitsU (U : UDoc) : Bool :=
  U.unspec.all (fun p => ruleName (fillName p)) &&
  decide (U.unspec.map fillName).Nodup &&
  decide (U.D.T.nodes.length + U.unspec.length ≤ 256) &&
  U.D.T.nodes.all (fun N => !(N.pred ∈ U.unspec) || decide (height U.D.T (fuel U.D.T) N ≤ 15)) &&
  decide ((U.D.T.nodes.map ruleNodes).sum + fillGuardNodes U ≤ 10000)

/-- `WellFormed U.D`; `unspec` duplicate-free, regulated, placeholder `false`; the
names `fill` introduces unused; and the author-side limits (i)-(v), which
`fill_wellFormed` proves sufficient for `WellFormed (fill U)`. -/
def WellFormedU (U : UDoc) : Bool :=
  WellFormed U.D && unspecDeclared U && reservedFree U && limitsU U

end VE.NormDefaults
