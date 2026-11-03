import VE.Defaults.Meaning

/-! One "no exception" (docs/spec/profile-composition.md 1.8 and 1.9; plan PC-9): defeasible's `Dflt_T` made
uniform. Every decision premise takes the form `Dflt_T` already gives exceptions: a decision is taken only where a
stated sufficient condition forces it. The conditions are soft's own exceptions and the provider-exported metadata
`Pack.conditions` (PK-1), looked up by the decision key of `decisionRule N` (PC-6a).

`dfltUniform_legacy`: on packs that state no condition, today's `[soft]` and `[soft, rights]`, the uniform premises
are today's, label for label. `dfltUniform_sound`: a default base satisfies the uniform premises wherever the stated
conditions are exact (`ConditionsExact`: on every admissible base the least tables lie below the base's, the conjunct
of DRI decision 2026-11-02, pc9-decide-check, item 2, and keep it admissible). It says nothing on a switch condition
that ever holds, since `ConditionsExact` then fails through `SwitchesOff` (item 4). Until EXP-D3 settles, the defaults
kinds refuse a document some of whose packs state a condition (`providerConditions` and `providerRefusal`, read by
`defaultsRows` in `Defaults/Route.lean`; E1d's text is `providerE1d`, which no route produces yet). -/
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

/-- The stated conditions are all that force a decision: on every admissible base the least tables lie below the
base's (sa-no-exception, DRI decision 2026-11-02, pc9-decide-check, item 2) and keep it admissible (the uniform
analogue of `ReplacementHolds`, Meaning.lean:70). -/
def ConditionsExact (U : UDoc) (D : SoftDoc) (qs : List Pack) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U (VE.NormDefaults.Packs.X qs) B →
    (∃ F : String → List B.Carrier → Prop,
      BaseAdmissibleX U (VE.NormDefaults.Packs.X qs) (withOpen U D B (leastUniform D qs B) F) ∧
      SwitchesOff D (withOpen U D B (leastUniform D qs B) F)) ∧
    ∀ p vs, leastUniform D qs B p vs → B.relation p vs

/-- With no stated provider condition, `ConditionsExact` reads today's least tables. -/
theorem conditionsExact_legacy (U : UDoc) (D : SoftDoc) {qs : List Pack} (h : ∀ p ∈ qs, p.conditions = []) :
    ConditionsExact.{u} U D qs ↔ ∀ B : VE.Structure.{u}, BaseAdmissibleX U (VE.NormDefaults.Packs.X qs) B →
      (∃ F : String → List B.Carrier → Prop,
        BaseAdmissibleX U (VE.NormDefaults.Packs.X qs) (withOpen U D B (leastDecisions D B) F) ∧
        SwitchesOff D (withOpen U D B (leastDecisions D B) F)) ∧
      ∀ p vs, leastDecisions D B p vs → B.relation p vs := by
  simp only [ConditionsExact, leastUniform_legacy D h]

/-! ## `dfltUniform_sound` -/

theorem key_inj {α : Type} (key : α → String) {l : List α} (hk : (l.map key).Nodup) {x y : α} (hx : x ∈ l)
    (hy : y ∈ l) (h : key x = key y) : x = y := by
  have h1 := VE.SoftNorms.find_key key l hk x hx
  rw [h] at h1
  exact Option.some.inj (h1.symm.trans (VE.SoftNorms.find_key key l hk y hy))

theorem noneOr_denote {B : VE.Structure.{u}} {d : VE.Formula} {cs : List VE.Formula} {ρ : VE.Valuation B}
    (h : d.denote B ρ → ∃ C ∈ cs, C.denote B ρ) : (noneOr d cs).denote B ρ := by
  cases cs with
  | nil => exact fun hd => by obtain ⟨_, hC, _⟩ := h hd; cases hC
  | cons c cs => exact fun hd => (VE.Norms.anyF_denote _ _ _).mpr (h hd)

section Names
variable {D : SoftDoc} (hD : WellFormedSoft D = true)
include hD

/-- A switch name and an `outweighs` name each name one decision, and never the same one. -/
theorem off_names :
    ((D.T.nodes.flatMap fun N => N.alterable.map (N, ·)).map fun x => offName x.1 x.2).Nodup ∧
    ((outweighsTriples D).map fun t => outweighsName t.1 t.2.1 t.2.2).Nodup ∧
    ∀ N ∈ D.T.nodes, ∀ π ∈ N.alterable, ∀ t ∈ outweighsTriples D, offName N π ≠ outweighsName t.1 t.2.1 t.2.2 := by
  have hnd := (VE.SoftNorms.softValid_of_wellFormed D hD).decNodup
  rw [decisionNames_split, List.nodup_append, List.nodup_append] at hnd
  refine ⟨by simpa [VE.SoftNorms.offDecisions, List.map_flatMap, Function.comp_def] using hnd.1.2.1,
    by simpa [VE.SoftNorms.outweighsDecisions, Function.comp_def] using hnd.2.1, fun N hN π hπ t ht => ?_⟩
  exact hnd.2.2 _ (List.mem_append_right _ (List.mem_map.mpr ⟨_, List.mem_flatMap.mpr ⟨N, hN,
    List.mem_map.mpr ⟨π, hπ, rfl⟩⟩, rfl⟩)) _ (List.mem_map.mpr ⟨_, List.mem_map.mpr ⟨t, ht, rfl⟩, rfl⟩)

/-- `dfltUniform` holds wherever every decision table of `B` lies below the least tables. -/
theorem sat_dfltUniform (qs : List Pack) (B : VE.Structure.{u})
    (hle : ∀ p ∈ VE.SoftNorms.decisionNames D, ∀ vs, B.relation p vs → leastUniform D qs B p vs) :
    Sat B (dfltUniform D qs) := by
  have offMem : ∀ N ∈ D.T.nodes, ∀ π ∈ N.alterable, offName N π ∈ (VE.SoftNorms.offDecisions D).map (·.1) ++
      (VE.SoftNorms.outweighsDecisions D).map (·.1) := fun N hN π hπ =>
    List.mem_append_left _ (List.mem_map.mpr ⟨_, List.mem_flatMap.mpr ⟨N, hN, List.mem_map.mpr ⟨π, hπ, rfl⟩⟩, rfl⟩)
  have owMem : ∀ t ∈ outweighsTriples D, outweighsName t.1 t.2.1 t.2.2 ∈ (VE.SoftNorms.offDecisions D).map (·.1) ++
      (VE.SoftNorms.outweighsDecisions D).map (·.1) := fun t ht =>
    List.mem_append_right _ (List.mem_map.mpr ⟨_, List.mem_map.mpr ⟨t, ht, rfl⟩, rfl⟩)
  have pairMem : ∀ N ∈ D.T.nodes, ∀ π ∈ N.alterable, (N, π) ∈ D.T.nodes.flatMap fun N => N.alterable.map (N, ·) :=
    fun N hN π hπ => List.mem_flatMap.mpr ⟨N, hN, List.mem_map.mpr ⟨π, hπ, rfl⟩⟩
  obtain ⟨hoff, how, hapart⟩ := off_names hD
  intro a ha
  obtain ⟨⟨l, a⟩, hla, rfl⟩ := List.mem_map.mp ha
  rcases List.mem_append.mp hla with hn | hr
  · obtain ⟨N, hN, hx⟩ := List.mem_flatMap.mp hn
    unfold dfltUniformOf at hx
    rcases List.mem_append.mp hx with he | hw
    · split at he
      · rename_i e hm hexc
        cases List.mem_singleton.mp he
        have hd : (exceptedName N, sortsOf D N.pred) ∈ VE.SoftNorms.decisions D :=
          VE.Readings.mem_decisions.mpr (Or.inl ⟨N, hN, hm, rfl⟩)
        show (bindAll _ _).denote _ []
        rw [VE.Norms.bindAll_denote_nil]
        intro vs hvs hx
        rcases hle _ (List.mem_map.mpr ⟨_, hd, rfl⟩) vs
          ((VE.Norms.atom_denote _ _ _ (decision_arity hD hd) vs hvs).mp hx) with
          ⟨N', hN', hm', hname, -, C, hC, hCd⟩ | ⟨N', hN', π, hπ, hname, -⟩ | ⟨t, ht, hname, -⟩
        · cases excepted_inj hD hN hm hN' hm' hname
          simp only [hexc, Option.map_some, Option.getD_some] at hC
          exact (VE.Norms.anyF_denote _ _ _).mpr ⟨C, hC, hCd⟩
        · have hn : exceptedName N = offName N' π := hname
          exact absurd (hn ▸ offMem N' hN' π hπ) (excepted_only hD hN hm)
        · have hn : exceptedName N = outweighsName t.1 t.2.1 t.2.2 := hname
          exact absurd (hn ▸ owMem t ht) (excepted_only hD hN hm)
      · cases he
    · obtain ⟨π, hπ, hx⟩ := List.mem_map.mp hw
      cases hx
      have hd : (offName N π, sortsOf D N.pred) ∈ VE.SoftNorms.decisions D :=
        VE.Readings.mem_decisions.mpr (Or.inr (Or.inl ⟨N, hN, π, hπ, rfl⟩))
      show (bindAll _ _).denote _ []
      rw [VE.Norms.bindAll_denote_nil]
      intro vs hvs
      refine noneOr_denote fun hx => ?_
      rcases hle _ (List.mem_map.mpr ⟨_, hd, rfl⟩) vs
        ((VE.Norms.atom_denote _ _ _ (decision_arity hD hd) vs hvs).mp hx) with
        ⟨N', hN', hm', hname, -⟩ | ⟨N', hN', π', hπ', hname, -, C, hC, hCd⟩ | ⟨t, ht, hname, -⟩
      · exact absurd (hname ▸ offMem N hN π hπ) (excepted_only hD hN' hm')
      · cases key_inj (fun x => offName x.1 x.2) hoff (pairMem N hN π hπ) (pairMem N' hN' π' hπ') hname
        exact ⟨C, hC, hCd⟩
      · exact absurd hname (hapart N hN π hπ t ht)
  · obtain ⟨⟨a', L, H⟩, ht, hx⟩ := List.mem_map.mp hr
    cases hx
    have hd : (outweighsName a' L H, actSortsOf D a') ∈ VE.SoftNorms.decisions D :=
      VE.Readings.mem_decisions.mpr (Or.inr (Or.inr ⟨a', L, H, ht, rfl⟩))
    show (bindAll _ _).denote _ []
    rw [VE.Norms.bindAll_denote_nil]
    intro vs hvs
    refine noneOr_denote fun hx => ?_
    rcases hle _ (List.mem_map.mpr ⟨_, hd, rfl⟩) vs
      ((VE.Norms.atom_denote _ _ _ (decision_arity hD hd) vs hvs).mp hx) with
      ⟨N', hN', hm', hname, -⟩ | ⟨N', hN', π, hπ, hname, -⟩ | ⟨t, ht', hname, -, C, hC, hCd⟩
    · have hn : outweighsName a' L H = exceptedName N' := hname
      exact absurd (hn ▸ owMem (a', L, H) ht) (excepted_only hD hN' hm')
    · have hn : outweighsName a' L H = offName N' π := hname
      exact absurd hn.symm (hapart N' hN' π hπ (a', L, H) ht)
    · have hn : outweighsName a' L H = outweighsName t.1 t.2.1 t.2.2 := hname
      have he : (a', L, H) = t := key_inj (x := (a', L, H)) (y := t) _ how ht ht' hn
      subst he
      exact ⟨C, hC, hCd⟩

end Names

/-- Proved by defeasible's named batch DF-U (DRI ruling 2(b)), against `DefaultBase`. -/
theorem dfltUniform_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (qs : List Pack) (hex : ConditionsExact.{u} U D qs) (B : VE.Structure.{u})
    (hB : DefaultBase U D (VE.NormDefaults.Packs.X qs) B) : Sat B (dfltUniform D qs) := by
  obtain ⟨⟨F, hF, hsw⟩, hlu⟩ := hex B hB.1
  exact sat_dfltUniform hD qs B (hB.2.2 _ F (fun p _ vs => hlu p vs) hF hsw)

/-- The guard the defaults kinds read until EXP-D3 settles (one line in `defaultsRows`, `Defaults/Route.lean:17`):
some provider states a decision condition. Every pack is read, not only `weighing`. -/
def providerConditions (qs : List Pack) : Bool := qs.any (!·.conditions.isEmpty)

def providerRefusal : String := "UnsupportedProfile: defaults with provider conditions is not implemented"

/-- E1d (2.1): `providerRefusal` in English. It names no provider. No route produces it yet (its display is open with the DRI). -/
def providerE1d : String :=
  "This question assumes no exception, and this document's providers state decision conditions. " ++
  "VE cannot check these two together yet. Nothing in this document was checked."

end VE.Defaults
