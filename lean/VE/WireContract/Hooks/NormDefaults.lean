import VE.NormDefaults.Admission
import VE.WireContract.Hooks.Norms
import VE.WireContract.Tables.NormDefaults

/-! The hand-written hooks and adapter of the contract `norm-defaults@0`
(docs/spec/wire-contract-s5.md 2.4 and 2.5).

The included checks of `norms@0` run with `Hooks.Norms`' `predicate` and
`classifier`, by name. The six own hooks are the author-side limits of
norm-defaults.md 8 as `NormDefaults.Wire.checkAuthor` computes them, and the
budget of the fill premises: each reads the author document as the route's
decoder builds it (`Norms.Wire.decodeNormsEnvironment` on the placeholder
environment, `Norms.Wire.decodeNorm` on each unit), never `decodeSource`, and
holds when it cannot be built, which by base spec 2.5 rule 2 happens only before
the included checks hold. Diagnostic only: no verdict depends on this module. -/

namespace VE.WireContract.Hooks.NormDefaults
open Lean
open VE.WireContract
open VE.NormDefaults (UDoc ruleNodes fillGuardNodes)
open VE.WireContract.Hooks.Norms (environmentOf rulesOf)

/-- `U = (D, unspec)` as `NormDefaults.Wire.decodeSourceU` builds it, without its validation. -/
def author (root : Json) : Option UDoc := do
  let environment := environmentOf root
  let ne ← (VE.Norms.Wire.decodeNormsEnvironment (← (VE.NormDefaults.Wire.placeholderJson environment).toOption)).toOption
  let nodes ← ((rulesOf root).mapM fun u => VE.Norms.Wire.decodeNorm u).toOption
  let defs := ne.rv.definitions.map fun d =>
    ({ name := d.name, args := d.args, body := d.body } : VE.Norms.Definition)
  let D : VE.Norms.Doc := ⟨ne.rv.environment, ne.rv.literals, ⟨ne.regulated, defs, nodes⟩⟩
  let names := VE.NormDefaults.Wire.unspecifiedNames environment
  pure ⟨D, (D.T.regulated.map VE.Norms.Regulated.name).filter (names.contains ·)⟩

/-- The nesting depth of a formula's formula nodes, the outermost at depth 1 (`_Checker.formula`'s `depth`;
    a term under an atom is at depth 1 of its own). -/
def formulaDepth : VE.Formula → Nat
  | .top | .bottom | .unary _ _ | .binary _ _ _ | .eq _ _ => 1
  | .not a | .all _ a | .ex _ a => formulaDepth a + 1
  | .and a b | .or a b | .implies a b => max (formulaDepth a) (formulaDepth b) + 1

/-- 6.3: the label of the first pair premise of `Fill_T`, in `fillPremises` order, at which the running node
    total passes 10,000 or that is more than 64 levels deep. -/
def firstOverBudget (premises : List (String × VE.Formula)) : Option String :=
  let rec go : Nat → List (String × VE.Formula) → Option String
    | _, [] => none
    | n, (label, φ) :: rest =>
      let total := n + VE.Bridge.formulaNodes φ
      if total > 10000 || formulaDepth φ > 64 then some label else go total rest
  go 0 premises

def holdsUnless (b : Bool) : HookResult := if b then .fail [] else .ok

def own : String → Json → List Pointer → HookResult
  -- 5.1 to 5.3: `checkAuthor`'s three counts
  | "filled_vocabulary_fits", root, _ => match author root with
    | some U => holdsUnless
        ((VE.NormDefaults.Wire.declaredNames (environmentOf root)).length + U.unspec.length > 256)
    | none => .ok
  | "filled_rules_fit", root, _ => match author root with
    | some U => holdsUnless (U.D.T.nodes.length + U.unspec.length > 256)
    | none => .ok
  | "unspecified_names_fit", root, _ => match author root with
    | some U => holdsUnless (U.unspec.any (fun p => p.utf8ByteSize > 56))
    | none => .ok
  -- 6.1, 6.2: `checkAuthor`'s node budget with the fill guards, and the height on unspecified predicates
  | "filled_ast_fits", root, _ => match author root with
    | some U => holdsUnless ((U.D.T.nodes.map ruleNodes).sum + fillGuardNodes U > 10000)
    | none => .ok
  | "filled_precedence_depth_fits", root, _ => match author root with
    | some U => holdsUnless (U.D.T.nodes.any fun N =>
        decide (N.pred ∈ U.unspec) && decide (VE.Norms.height U.D.T (VE.Norms.fuel U.D.T) N > 15))
    | none => .ok
  -- 6.3: the pair premises as `Wire.regeneratedU` builds them, with their labels
  | "fill_premises_fit", root, _ => match author root with
    | some U => match firstOverBudget (VE.NormDefaults.Admission.fillLabelled U) with
      | some label => .fail [("label", .str label)]
      | none => .ok
    | none => .ok
  | _, _, _ => .ok

/-- The own hooks, then `norms@0`'s for the included names. -/
def ownNames : List String :=
  ["filled_vocabulary_fits", "filled_rules_fit", "unspecified_names_fit", "filled_ast_fits",
   "filled_precedence_depth_fits", "fill_premises_fit"]

def predicate (name : String) (root : Json) (items : List Pointer) : HookResult :=
  if ownNames.contains name then own name root items else Hooks.Norms.predicate name root items

def hooks : Hooks := ⟨predicate, Hooks.Norms.classifier, Hooks.Norms.view⟩

/-- The adapter `norm_defaults_source` (spec 2.2): the kinds beginning `norm-defaults-` and `admission`, with
    manifest bindings "norm-defaults-elaborate", "norm-defaults-conflict" and "norm-defaults-certificate".
    `norm-defaults@0` listed. -/
def adapter (case : Json) : Except String Json :=
  Hooks.Norms.sourceAdapter (fun k => k.startsWith "norm-defaults-")
    (fun environment norms => Hooks.Norms.inSharedDomain environment norms &&
      (VE.NormDefaults.Wire.profilesOf environment).contains VE.NormDefaults.Wire.profile) case

/-- The names this module registers. -/
def registered : List String := ownNames ++ Hooks.Norms.registered

#guard Tables.NormDefaults.table.hookNames.all registered.contains

end VE.WireContract.Hooks.NormDefaults
