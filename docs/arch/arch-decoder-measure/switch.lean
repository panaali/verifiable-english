import VE.Closure.CoreEquiv
import VE.CertificateWire

/-! arch-decoder-measure, deliverable 2 (a): what a switch of closure's trace decoder to Core's would
have to state. Written out and elaborated against the tree; NOT part of the tree (no lakefile root
reaches it, nothing imports it). Run from `lean/`: `lake env lean ../docs/arch/arch-decoder-measure/switch.lean`.

Part A shows that the switch as first described (Core's decoder unchanged, then an atom-free check
of what it returns) cannot equal closure's decoder on every input: two inputs on which Core's decoder
answers the same, and closure's differently. Part B is the smallest switch that can: Core's decoders
gain an atom-free mode (`atoms := false`), and closure's decoder becomes that mode read back into
closure's syntax. Its definitions are copies of Core's with the flag added, under new names, so this
file changes nothing in the tree. Part C holds the statements, each with `sorry` unless proved here. -/

namespace ArchDecoderMeasure
open Lean
open VE.Closure.CoreEquiv (embedTrace embedTraces)
open VE.Core (embedClosure)

/-! ## Part A: Core's decoder unchanged, then a check of its answer: impossible -/

/-- A `closure-induct@1` node whose invariant is a ternary `atom` (AR-21's witness). -/
def atomNode : Json :=
  let c : Json := .arr #[.str "const", .str "a"]
  Json.mkObj [("rule", .str "closure-induct@1"), ("at", (0 : Nat)), ("sort", .str "s"),
    ("invariant", .arr #[.str "atom", .str "p", .arr #[c, c, c]]), ("children", .arr #[])]

def badNode : Json := Json.mkObj [("rule", .str "bogus")]

/-- The atom node first, a bad node after it: closure stops at the atom, Core at the bad node. -/
def atomThenBad : Json :=
  Json.mkObj [("rule", .str "expand"), ("at", (0 : Nat)), ("children", .arr #[atomNode, badNode])]

def message {α : Type} : Except String α → Option String
  | .error e => some e
  | .ok _ => none

/-- The fault order: no check that reads only Core's answer can give closure's answer on every input. -/
theorem no_check_after_core :
    ¬ ∃ check : Except String VE.Core.Tableau.Trace → Except String VE.Closure.Tableau.Trace,
      ∀ fuel j, check (VE.Core.Wire.decodeTrace fuel j) = VE.CertificateWire.decodeClosureTrace fuel j := by
  intro ⟨check, h⟩
  have core : VE.Core.Wire.decodeTrace 125 atomThenBad = VE.Core.Wire.decodeTrace 125 badNode := by
    have e1 : message (VE.Core.Wire.decodeTrace 125 atomThenBad) = some "unknown tableau rule" := by decide
    have e2 : message (VE.Core.Wire.decodeTrace 125 badNode) = some "unknown tableau rule" := by decide
    revert e1 e2
    cases VE.Core.Wire.decodeTrace 125 atomThenBad <;> cases VE.Core.Wire.decodeTrace 125 badNode <;>
      simp [message] <;> intro h1 h2 <;> simp [h1, h2]
  have closure := (h 125 atomThenBad).symm.trans ((congrArg check core).trans (h 125 badNode))
  have := congrArg message closure
  revert this
  decide

/-- Even on one node the text differs: a binary `atom` is Core's own fault, closure's generic one. -/
def binaryAtom : Json :=
  let c : Json := .arr #[.str "const", .str "a"]
  Json.mkObj [("rule", .str "closure-induct@1"), ("at", (0 : Nat)), ("sort", .str "s"),
    ("invariant", .arr #[.str "atom", .str "p", .arr #[c, c]]), ("children", .arr #[])]

theorem binaryAtom_texts :
    message (VE.Core.Wire.decodeTrace 125 binaryAtom) = some "Atom terms must be an array of three to six terms" ∧
    message (VE.CertificateWire.decodeClosureTrace 125 binaryAtom) = some "invalid indexed formula" := by
  decide

/-! ## Part B: the smallest switch that can hold: an atom-free mode in Core's decoders -/

section B
open VE.Bridge
open VE.Core.Bridge (decodeKind formulaNodes)

/-! `decodeFormulaWith` is Core's formula decoder (`VE.Core.Bridge.decodeFormula`, which has no
docstring) with one flag: with `atoms := false` an `atom` falls to the generic refusal, as in
closure's decoder. Changed lines: the header, the guard (the one new line) and the seven recursive
calls that pass the flag. `decodeTraceWith` is Core's trace decoder (`VE.Core.Wire.decodeTrace`, no
docstring either) passing the flag on: changed lines are the header, the invariant line and the two
recursive calls; no new line. Neither copy carries a docstring, so their line counts compare with
the originals'. -/

def decodeFormulaWith (atoms : Bool) : Nat → Json → Except String VE.Core.Formula
  | 0, _ => throw "ResourceLimit: formula depth exceeds 64"
  | n + 1, j => do
    match (← j.getArr?).toList with
    | [.str "top"] => return .top
    | [.str "bottom"] => return .bottom
    | [.str "unary", .str p, t] => return .unary p (← decodeTerm t)
    | [.str "binary", .str p, t, u] => return .binary p (← decodeTerm t) (← decodeTerm u)
    | [.str "atom", .str p, ts] =>
      unless atoms do throw "invalid indexed formula"
      let termArray ← match ts.getArr? with
        | .ok array => pure array
        | .error _ => throw "Atom terms must be an array of three to six terms"
      let terms ← termArray.toList.mapM decodeTerm
      unless decide (3 ≤ terms.length) && decide (terms.length ≤ 6) do
        throw "Atom terms must be an array of three to six terms"
      return .atom p terms
    | [.str "eq", t, u] => return .eq (← decodeTerm t) (← decodeTerm u)
    | [.str "not", a] => return .not (← decodeFormulaWith atoms n a)
    | [.str "and", a, b] => return .and (← decodeFormulaWith atoms n a) (← decodeFormulaWith atoms n b)
    | [.str "or", a, b] => return .or (← decodeFormulaWith atoms n a) (← decodeFormulaWith atoms n b)
    | [.str "implies", a, b] => return .implies (← decodeFormulaWith atoms n a) (← decodeFormulaWith atoms n b)
    | [.str "forall", .str s, a] => return .all s (← decodeFormulaWith atoms n a)
    | [.str "exists", .str s, a] => return .ex s (← decodeFormulaWith atoms n a)
    | [.str "reach", k, e, t, u] =>
      let k ← decodeKind k
      let t ← decodeTerm t
      let u ← decodeTerm u
      match (← e.getArr?).toList with
      | [.str "named", .str r] => pure (.reachNamed k r t u)
      | [.str "body", .str s, a] => return .reachBody k s (← decodeFormulaWith atoms n a) t u
      | _ => throw "invalid reach edge"
    | _ => throw "invalid indexed formula"

def decodeTraceWith (atoms : Bool) : Nat → Json → Except String VE.Core.Tableau.Trace
  | 0, _ => throw "ResourceLimit: certificate expansion depth exceeds 124"
  | fuel + 1, j => do
    let rule ← VE.Bridge.stringField j "rule"
    if rule == "close" then
      VE.Bridge.exactFields j ["rule"]
      pure .close
    else if rule == "closure-induct@1" then
      VE.Bridge.exactFields j ["rule", "at", "sort", "invariant", "children"]
      let index ← (← j.getObjVal? "at").getNat?
      let sort ← VE.Bridge.stringField j "sort"
      let invariant ← decodeFormulaWith atoms VE.Limits.maxDepth (← j.getObjVal? "invariant")
      if formulaNodes invariant > VE.Limits.maxNodes then throw "ResourceLimit: invariant AST node count"
      let children ← (← (← j.getObjVal? "children").getArr?).toList.mapM (decodeTraceWith atoms fuel)
      pure (.induct index sort invariant children)
    else if rule == "expand" || rule == "closure-plus@0" || rule == "closure-star@0" ||
        VE.Core.Tableau.extraRule rule then
      let names := (← VE.Bridge.fields j).map Prod.fst
      let optional := names.contains "parameter"
      VE.Bridge.exactFields j (["rule", "at", "children"] ++ if optional then ["parameter"] else [])
      let index ← (← j.getObjVal? "at").getNat?
      let parameter ← if optional then do pure (some (← VE.Bridge.stringField j "parameter")) else pure none
      let children ← (← (← j.getObjVal? "children").getArr?).toList.mapM (decodeTraceWith atoms fuel)
      pure (.expand rule index parameter children)
    else throw "unknown tableau rule"

/-- Read a Core formula back into closure's syntax; an `atom` has no closure form. New lines. -/
def unembedFormula : VE.Core.Formula → Except String VE.Closure.Formula
  | .top => pure .top
  | .bottom => pure .bottom
  | .unary p t => pure (.unary p t)
  | .binary p t u => pure (.binary p t u)
  | .atom _ _ => throw "invalid indexed formula"
  | .eq t u => pure (.eq t u)
  | .not a => return .not (← unembedFormula a)
  | .and a b => return .and (← unembedFormula a) (← unembedFormula b)
  | .or a b => return .or (← unembedFormula a) (← unembedFormula b)
  | .implies a b => return .implies (← unembedFormula a) (← unembedFormula b)
  | .all s a => return .all s (← unembedFormula a)
  | .ex s a => return .ex s (← unembedFormula a)
  | .reachNamed k r t u => pure (.reachNamed k r t u)
  | .reachBody k s a t u => return .reachBody k s (← unembedFormula a) t u

mutual
/-- Read a Core trace back into closure's. New lines. -/
def unembedTrace : VE.Core.Tableau.Trace → Except String VE.Closure.Tableau.Trace
  | .close => pure .close
  | .expand rule index parameter children => return .expand rule index parameter (← unembedTraces children)
  | .induct index sort P children => return .induct index sort (← unembedFormula P) (← unembedTraces children)
def unembedTraces : List VE.Core.Tableau.Trace → Except String (List VE.Closure.Tableau.Trace)
  | [] => pure []
  | t :: ts => return (← unembedTrace t) :: (← unembedTraces ts)
end

/-- What `VE.CertificateWire.decodeClosureTrace` would become: Core's decoder in its atom-free
mode, read back into closure's syntax (its 26 lines replaced by these 3). -/
def decodeClosureTraceViaCore (fuel : Nat) (j : Json) : Except String VE.Closure.Tableau.Trace := do
  unembedTrace (← decodeTraceWith false fuel j)

end B

/-! Spot checks of `switch_eq` (below) on the inputs that separate the decoders, and on accepted
traces: the replacement and closure's decoder print the same answer. Evidence, not a proof. -/

def unaryNode : Json :=
  Json.mkObj [("rule", .str "closure-induct@1"), ("at", (0 : Nat)), ("sort", .str "s"),
    ("invariant", .arr #[.str "unary", .str "p", .arr #[.str "var", (0 : Nat)]]),
    ("children", .arr #[Json.mkObj [("rule", .str "close")]])]

def badAtThenAtom : Json :=
  let c : Json := .arr #[.str "const", .str "a"]
  Json.mkObj [("rule", .str "closure-induct@1"), ("at", .str "x"), ("sort", .str "s"),
    ("invariant", .arr #[.str "atom", .str "p", .arr #[c, c, c]]), ("children", .arr #[])]

def nested (inner : Json) : Json :=
  Json.mkObj [("rule", .str "expand"), ("at", (1 : Nat)), ("parameter", .str "a"),
    ("children", .arr #[unaryNode, inner])]

def agree (j : Json) : Bool :=
  reprStr (decodeClosureTraceViaCore 125 j) == reprStr (VE.CertificateWire.decodeClosureTrace 125 j)

#guard [atomNode, badNode, atomThenBad, binaryAtom, unaryNode, badAtThenAtom, nested atomNode,
  nested binaryAtom, nested unaryNode, nested badNode].all agree
#guard (VE.CertificateWire.decodeClosureTrace 125 (nested unaryNode)).toBool
#guard !(VE.CertificateWire.decodeClosureTrace 125 atomThenBad).toBool

/-! ## Part C: the statements a switch needs

Trusted statements (what a reviewer must read to accept the switch): `switch_eq` (the decision's
condition: the replacement equals closure's decoder on every input, value and refusal text, so the
fault order too) and `core_unchanged_formula`, `core_unchanged_trace` (Core's own path is the same
decoder with the flag on; in the tree these would hold by definition if Core's `decodeFormula` and
`decodeTrace` were redefined as the `true` instances). The rest are proof obligations (audited, class P). -/

/-- TRUSTED STATEMENT 1: the switch changes nothing closure answers, refusal texts included. -/
theorem switch_eq (fuel : Nat) (j : Json) :
    decodeClosureTraceViaCore fuel j = VE.CertificateWire.decodeClosureTrace fuel j := by
  sorry

/-- TRUSTED STATEMENT 2: Core's formula decoder is the flag's `true` instance. -/
theorem core_unchanged_formula (n : Nat) (j : Json) :
    decodeFormulaWith true n j = VE.Core.Bridge.decodeFormula n j := by
  sorry

/-- TRUSTED STATEMENT 3: Core's trace decoder is the flag's `true` instance. -/
theorem core_unchanged_trace (fuel : Nat) (j : Json) :
    decodeTraceWith true fuel j = VE.Core.Wire.decodeTrace fuel j := by
  sorry

/-- Obligation O1: the atom-free formula decoder is closure's, embedded. -/
theorem decodeFormulaWith_false (n : Nat) (j : Json) :
    decodeFormulaWith false n j = (VE.Closure.Bridge.decodeFormula n j).map embedClosure := by
  sorry

/-- Obligation O2: the node count is the same on the embedding. -/
theorem formulaNodes_embed (a : VE.Closure.Formula) :
    VE.Core.Bridge.formulaNodes (embedClosure a) = VE.Closure.Bridge.formulaNodes a := by
  induction a <;> simp_all [embedClosure, VE.Closure.Formula.toCore, VE.Core.Bridge.formulaNodes,
    VE.Closure.Bridge.formulaNodes]

/-- Obligation O3: the atom-free trace decoder is closure's, embedded (AR-21's false equation,
true in the atom-free mode). -/
theorem decodeTraceWith_false (fuel : Nat) (j : Json) :
    decodeTraceWith false fuel j = (VE.CertificateWire.decodeClosureTrace fuel j).map embedTrace := by
  sorry

/-- Obligation O4: reading back an embedded formula gives it back. -/
theorem unembedFormula_embed (a : VE.Closure.Formula) : unembedFormula (embedClosure a) = .ok a := by
  induction a <;> simp_all [embedClosure, VE.Closure.Formula.toCore, unembedFormula] <;> rfl

mutual
/-- Obligation O5: reading back an embedded trace gives it back. -/
theorem unembedTrace_embed : (t : VE.Closure.Tableau.Trace) → unembedTrace (embedTrace t) = .ok t
  | .close => rfl
  | .expand r i p cs => by simp [embedTrace, unembedTrace, unembedTraces_embed cs]; rfl
  | .induct i s P cs => by
    simp [embedTrace, unembedTrace, unembedFormula_embed P, unembedTraces_embed cs]; rfl
theorem unembedTraces_embed : (ts : List VE.Closure.Tableau.Trace) → unembedTraces (embedTraces ts) = .ok ts
  | [] => rfl
  | t :: ts => by simp [embedTraces, unembedTraces, unembedTrace_embed t, unembedTraces_embed ts]; rfl
end

end ArchDecoderMeasure
