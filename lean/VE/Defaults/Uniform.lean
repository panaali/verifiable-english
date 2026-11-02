import VE.Defaults.Meaning

/-! One "no exception" (docs/spec/profile-composition.md 1.8 and 1.9; plan PC-9): defeasible's `Dflt_T` made
uniform. Every decision premise takes the form `Dflt_T` already gives exceptions: a decision is taken only where a
stated sufficient condition forces it. The conditions are soft's own exceptions and the provider-exported metadata
`Pack.conditions` (PK-1), looked up by the decision key of `decisionRule N` (PC-6a).

`dfltUniform_legacy`: on packs that state no condition, today's `[soft]` and `[soft, rights]`, the uniform premises
are today's, label for label. `dfltUniform_sound` is stated here (`DfltUniformSound`) and proved by defeasible's DF-U.
Until EXP-D3 settles, the defaults kinds refuse a document some of whose packs state a condition
(`providerConditions`, `providerRefusal` and its sentence E1d, read by `defaultsRows` in `Defaults/Route.lean`). -/
namespace VE.Defaults
open VE.Norms (bindAll atom anyF Sat)
open VE.SoftNorms (SoftDoc SoftNode DecisionKey decisionRule exceptedF exceptedName outweighsF outweighsName offName
  sortsOf actSortsOf outweighsTriples soften WellFormedSoft)
open VE.NormDefaults (UDoc WellFormedU)
open VE.NormDefaults.Packs (Pack)
open VE.NormDefaults.Wire (BaseAdmissibleX)
universe u

/-- W1's precedence check reads no rank pair. -/
theorem precedence_apart (D : VE.SoftNorms.SoftDoc) (o : List (String × String)) :
    VE.Norms.precedenceNodes ({ D with soft := { D.soft with outranks := o } } : VE.SoftNorms.SoftDoc).base.T =
      VE.Norms.precedenceNodes D.base.T := rfl

def packConditions (qs : List Pack) (k : DecisionKey) : List VE.Formula :=
  qs.flatMap fun p => (p.conditions.filter (·.1 == k)).map (·.2)

/-- A decision with no stated condition is never taken; otherwise it is taken only where one holds. -/
def noneOr (d : VE.Formula) : List VE.Formula → VE.Formula
  | [] => .not d
  | cs => .implies d (anyF cs)

/-- A rule's decisions are looked up by its decision key, `decisionRule N` (1.10, PC-6a), never by `N.name`:
provider metadata on a source rule reaches every part of it after a split (F6.7). -/
def dfltUniformOf (D : SoftDoc) (qs : List Pack) (N : SoftNode) : List (String × VE.Formula) :=
  (match N.mode, N.exception with
   | .default, some e =>
       [("default:exception:" ++ N.name, bindAll (sortsOf D N.pred)
         (.implies (exceptedF D N) (anyF (e.sufficient ++ packConditions qs (.excepted (decisionRule N))))))]
   | _, _ => []) ++
  N.alterable.map (fun π =>
    ("default:switch:" ++ N.name ++ ":" ++ π, bindAll (sortsOf D N.pred)
      (noneOr (atom (offName N π) (sortsOf D N.pred)) (packConditions qs (.off (decisionRule N) π)))))

def dfltUniformLabelled (D : SoftDoc) (qs : List Pack) : List (String × VE.Formula) :=
  D.T.nodes.flatMap (dfltUniformOf D qs) ++
  (outweighsTriples D).map (fun (a, L, H) =>
    ("default:ranking:" ++ L ++ ":" ++ H ++ ":" ++ a,
     bindAll (actSortsOf D a) (noneOr (outweighsF D a L H) (packConditions qs (.outweighs a L H)))))

def dfltUniform (D : SoftDoc) (qs : List Pack) : List VE.Formula := (dfltUniformLabelled D qs).map (·.2)

theorem packConditions_nil {qs : List Pack} (h : ∀ p ∈ qs, p.conditions = []) (k : DecisionKey) :
    packConditions qs k = [] := by
  simp only [packConditions, List.flatMap_eq_nil_iff]
  intro p hp
  simp [h p hp]

/-- On packs that state no condition (today's `[soft]`, `[soft, rights]`), the uniform premises are today's,
label for label. -/
theorem dfltUniform_legacy (D : SoftDoc) (qs : List Pack) (h : ∀ p ∈ qs, p.conditions = []) :
    dfltUniformLabelled D qs = dfltLabelled D := by
  have hN : dfltUniformOf D qs = dfltOf D := by
    funext N
    simp only [dfltUniformOf, dfltOf, packConditions_nil h, List.append_nil, noneOr]
    cases N.mode <;> cases N.exception <;> rfl
  simp only [dfltUniformLabelled, dfltLabelled, hN, packConditions_nil h, noneOr]

/-- The least decision tables of the stated conditions on `B`'s facts. -/
def leastUniform (D : SoftDoc) (qs : List Pack) (B : VE.Structure.{u}) : String → List B.Carrier → Prop :=
  fun p vs =>
    (∃ N ∈ D.T.nodes, N.mode = .default ∧ p = exceptedName N ∧ VE.TupleTyped B (sortsOf D N.pred) vs ∧
      ∃ C ∈ ((N.exception.map (·.sufficient)).getD []) ++ packConditions qs (.excepted (decisionRule N)),
        C.denote B (VE.Norms.tupleVal vs)) ∨
    (∃ N ∈ D.T.nodes, ∃ π ∈ N.alterable, p = offName N π ∧ VE.TupleTyped B (sortsOf D N.pred) vs ∧
      ∃ C ∈ packConditions qs (.off (decisionRule N) π), C.denote B (VE.Norms.tupleVal vs)) ∨
    (∃ t ∈ outweighsTriples D, p = outweighsName t.1 t.2.1 t.2.2 ∧ VE.TupleTyped B (actSortsOf D t.1) vs ∧
      ∃ C ∈ packConditions qs (.outweighs t.1 t.2.1 t.2.2), C.denote B (VE.Norms.tupleVal vs))

/-- With no stated provider condition, the least tables are today's (`leastDecisions`). -/
theorem leastUniform_legacy (D : SoftDoc) {qs : List Pack} (h : ∀ p ∈ qs, p.conditions = [])
    (B : VE.Structure.{u}) : leastUniform D qs B = leastDecisions D B := by
  funext p vs
  simp [leastUniform, leastDecisions, packConditions_nil h]

/-- The stated conditions are all that force a decision: the least tables keep the base admissible (the uniform
analogue of `ReplacementHolds`, Meaning.lean:70). -/
def ConditionsExact (U : UDoc) (D : SoftDoc) (qs : List Pack) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U (VE.NormDefaults.Packs.X qs) B →
    ∃ F : String → List B.Carrier → Prop,
      BaseAdmissibleX U (VE.NormDefaults.Packs.X qs) (withOpen U D B (leastUniform D qs B) F) ∧
      SwitchesOff D (withOpen U D B (leastUniform D qs B) F)

/-- With no stated provider condition, `ConditionsExact` reads today's least tables. -/
theorem conditionsExact_legacy (U : UDoc) (D : SoftDoc) {qs : List Pack} (h : ∀ p ∈ qs, p.conditions = []) :
    ConditionsExact.{u} U D qs ↔ ∀ B : VE.Structure.{u}, BaseAdmissibleX U (VE.NormDefaults.Packs.X qs) B →
      ∃ F : String → List B.Carrier → Prop,
        BaseAdmissibleX U (VE.NormDefaults.Packs.X qs) (withOpen U D B (leastDecisions D B) F) ∧
        SwitchesOff D (withOpen U D B (leastDecisions D B) F) := by
  simp only [ConditionsExact, leastUniform_legacy D h]

/-- The statement of `dfltUniform_sound` (1.9), binders and conclusion as the specification gives them. Proved by
defeasible's named batch DF-U (DRI ruling 2(b)), against `DefaultBase`, as `dfltUniform_sound : DfltUniformSound`. -/
def DfltUniformSound : Prop :=
  ∀ (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (qs : List Pack) (hex : ConditionsExact.{u} U D qs) (B : VE.Structure.{u})
    (hB : DefaultBase U D (VE.NormDefaults.Packs.X qs) B), Sat B (dfltUniform D qs)

/-- The guard the defaults kinds read until EXP-D3 settles (one line in `defaultsRows`, `Defaults/Route.lean:17`):
some provider states a decision condition. Every pack is read, not only `weighing`. -/
def providerConditions (qs : List Pack) : Bool := qs.any (!·.conditions.isEmpty)

def providerRefusal : String := "UnsupportedProfile: defaults with provider conditions is not implemented"

/-- E1d (2.1): `providerRefusal` in English. It names no provider. -/
def providerE1d : String :=
  "This question assumes no exception, and this document's providers state decision conditions. " ++
  "VE cannot check these two together yet. Nothing in this document was checked."

end VE.Defaults
