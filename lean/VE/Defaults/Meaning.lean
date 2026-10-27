import VE.Defaults.Wire

/-! The meaning of a default answer (docs/spec/defeasible.md 3.7 and 7.3; plan DF-2): a default answer holds in every
default base, the bases whose open decisions are as few as the document and the facts allow, whatever the text leaves
unsaid.

`DefaultBase` is circumscription of the decision predicates (exceptions, switches, `outweighs`) with norm-defaults'
unsaid predicates varied (D15): a competitor `withOpen U D B δ F` keeps `B`'s facts, domain and constants, takes the
decision tables `δ` below `B`'s, and any unsaid tables `F`. `defaultBase_of_dflt` says that a base with the
no-exception premises `Dflt_T` is a default base. `replace_admissible` puts the least decisions `δ_B` (an exception
exactly where a stated sufficient condition holds) on a base admissible with `softX`, repairs the pair members' unsaid
tables by `fill_extends`, and gets a base admissible with `defaultX`; it needs the gate `hcoh` (for `Coh_T`) and the
computed check `replacementSafe` (the other packs and the base background read no table that changes). With both,
`default_entails_minimal` says that `defaultX`'s entailment is truth in every default base with an expansion.
`default_entails_minimal_of` is the plan's fallback, with `replace_admissible`'s conclusion as a hypothesis.

What the proofs read from a well-formed soft document: a default rule's exception conditions name only predicates
of the source environment, so neither a decision nor an unsaid predicate (`cond_free`); every decision predicate has
arity 1 or 2 (`decision_arity`), so its atom is its table on typed tuples; and decision names are distinct
(`decNodup`), so the least decisions hold on exception predicates only. -/
namespace VE.Defaults
open VE.Norms (bindAll atom anyF preds Sat DocumentExpansion restrictAll envAt size)
open VE.SoftNorms (SoftDoc SoftNode exceptedF exceptedName sortsOf decisionNames soften WellFormedSoft)
open VE.NormDefaults (UDoc fill fillPremises WellFormedU EntailsX)
open VE.NormDefaults.Wire (BaseAdmissibleX softLabelledU)
universe u

/-- `B` with the tables `δ` on the decision predicates of `D` and `F` on the unsaid predicates of `U`; the facts, the
    domain, the constants and every other symbol as in `B`. -/
def withOpen (U : UDoc) (D : SoftDoc) (B : VE.Structure.{u}) (δ F : String → List B.Carrier → Prop) :
    VE.Structure.{u} :=
  { B with relation := fun p vs =>
      if p ∈ decisionNames D then δ p vs
      else if p ∈ VE.NormDefaults.unsaidNames U then F p vs
      else B.relation p vs }

/-- No switch of `D` is on in `B`: the switch premises of `Dflt_T` hold (at typed tuples, as every premise reads). -/
def SwitchesOff (D : SoftDoc) (B : VE.Structure.{u}) : Prop :=
  Sat B (((dfltLabelled D).filter (fun a => a.1.startsWith "default:switch:")).map (·.2))

/-- A default base: admissible with the document's own `X`, no switch on, and no admissible base on the same facts
    with fewer decisions, where the competing base may also change the unsaid tables: circumscription of the decision
    predicates with norm-defaults' unsaid predicates varied (D15). The facts, the domain and the constants are fixed. -/
def DefaultBase (U : UDoc) (D : SoftDoc) (X : List VE.Formula) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissibleX U X B ∧ SwitchesOff D B ∧
  ∀ δ F : String → List B.Carrier → Prop,
    (∀ p ∈ decisionNames D, ∀ vs, δ p vs → B.relation p vs) →
    BaseAdmissibleX U X (withOpen U D B δ F) → SwitchesOff D (withOpen U D B δ F) →
    ∀ p ∈ decisionNames D, ∀ vs, B.relation p vs → δ p vs

/-- `X` as RD-9 and PK-1 assemble it: soft's pack (exception premises, then coherence premises on `fill U`), then
    the other packs `R`. -/
def softX (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : List VE.Formula :=
  (softLabelledU U D).map (·.2) ++ R

/-- `δ_B`: the least decision tables on `B`'s facts. A rule's exception holds exactly at the typed tuples where one of
    its stated sufficient conditions holds in `B`; no switch; no `outweighs`. -/
def leastDecisions (D : SoftDoc) (B : VE.Structure.{u}) : String → List B.Carrier → Prop := fun p vs =>
  ∃ N ∈ D.T.nodes, N.mode = .default ∧ p = exceptedName N ∧ VE.TupleTyped B (sortsOf D N.pred) vs ∧
    ∃ C ∈ ((N.exception.map (·.sufficient)).getD []), C.denote B (VE.Norms.tupleVal vs)

/-- The computed check that replaces draft 1's `hfill`: the other packs' premises `R` and the base background name no
    decision predicate of `D` and no unsaid predicate of a pair member (the tables `fill_extends` repairs). -/
def replacementSafe (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : Bool :=
  (R ++ VE.Norms.backgroundBase (fill U)).all (fun φ => (preds φ).all (fun p =>
    !(decisionNames D).contains p &&
    !((VE.NormDefaults.pairMembers U).map VE.NormDefaults.unsaidName).contains p))

/-- The fallback (plan 3.4): `replace_admissible`'s conclusion as an explicit hypothesis. -/
def ReplacementHolds (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U (softX U D R) B →
    ∃ F : String → List B.Carrier → Prop,
      BaseAdmissibleX U (defaultX D (softX U D R)) (withOpen U D B (leastDecisions D B) F)

/-! ## What a well-formed soft document guarantees -/

section Vocabulary
variable {D : SoftDoc} (hD : WellFormedSoft D = true)
include hD

/-- An exception condition names only predicates of the source environment (`checkSoftRule`'s typing check). -/
theorem cond_declared {N : SoftNode} (hN : N ∈ D.T.nodes) {e : VE.SoftNorms.Exception} (he : N.exception = some e)
    {C : VE.Formula} (hC : C ∈ e.sufficient ++ e.necessary) : ∀ p ∈ preds C, ∃ ss, D.E.predicates p = some ss := by
  have hr := (VE.Readings.checkSoft_parts D (VE.Readings.wellFormedSoft_check D hD)).2 N hN
  unfold VE.SoftNorms.checkSoftRule at hr
  simp only [he, bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw] at hr
  repeat' split at hr
  all_goals (try (simp at hr; done))
  all_goals
    have hfor := ‹forIn (e.sufficient ++ e.necessary) PUnit.unit _ = Except.ok _›
    obtain ⟨_, _, hc⟩ := VE.NormDefaults.forIn_each _ (fun x t r hr => by
      repeat' split at hr
      all_goals first | (cases hr; exact ⟨_, rfl⟩) | (simp at hr) | skip) _ _ _ hfor C hC
    repeat' split at hc
    all_goals (try (simp at hc; done))
    exact VE.NormDefaults.preds_declared C _ ((VE.check_iff_wellFormed _ _ _).mp ‹VE.Formula.check D.E _ C = true›)

omit hD in
/-- The decision names in their three groups. -/
theorem decisionNames_split : decisionNames D = (VE.SoftNorms.exceptedDecisions D).map (·.1) ++
    (VE.SoftNorms.offDecisions D).map (·.1) ++ (VE.SoftNorms.outweighsDecisions D).map (·.1) := by
  simp [decisionNames, VE.SoftNorms.decisions]

/-- Two default rules with the same exception predicate are the same rule. -/
theorem excepted_inj {N M : SoftNode} (hN : N ∈ D.T.nodes) (hn : N.mode = .default) (hM : M ∈ D.T.nodes)
    (hm : M.mode = .default) (h : exceptedName N = exceptedName M) : N = M := by
  have hnd := (VE.SoftNorms.softValid_of_wellFormed D hD).decNodup
  rw [decisionNames_split, List.nodup_append, List.nodup_append] at hnd
  have hk : ((D.T.nodes.filter (·.mode == .default)).map exceptedName).Nodup := by
    simpa [VE.SoftNorms.exceptedDecisions, Function.comp_def] using hnd.1.1
  have h1 := VE.SoftNorms.find_key exceptedName _ hk N (List.mem_filter.mpr ⟨hN, by simp [hn]⟩)
  have h2 := VE.SoftNorms.find_key exceptedName _ hk M (List.mem_filter.mpr ⟨hM, by simp [hm]⟩)
  rw [h] at h1
  exact Option.some.inj (h1.symm.trans h2)

/-- An exception predicate is neither a switch nor an `outweighs` predicate. -/
theorem excepted_only {N : SoftNode} (hN : N ∈ D.T.nodes) (hn : N.mode = .default) :
    exceptedName N ∉ (VE.SoftNorms.offDecisions D).map (·.1) ++ (VE.SoftNorms.outweighsDecisions D).map (·.1) := by
  have hnd := (VE.SoftNorms.softValid_of_wellFormed D hD).decNodup
  rw [decisionNames_split, List.append_assoc, List.nodup_append] at hnd
  exact fun hx => hnd.2.2 _ (List.mem_map.mpr ⟨_, List.mem_map.mpr ⟨N, List.mem_filter.mpr ⟨hN, by simp [hn]⟩, rfl⟩,
    rfl⟩) _ hx rfl

/-- A regulated predicate has arity 1 or 2. -/
theorem reg_arity {r : VE.Norms.Regulated} (hr : r ∈ D.T.regulated) : VE.Norms.Arity (sortsOf D r.name) := by
  have hv := VE.SoftNorms.softValid_of_wellFormed D hD
  have hvX := VE.Norms.valid_of_wellFormed _ hv.wf
  rw [VE.SoftNorms.sortsOf_reg hv hr]
  exact VE.Norms.regulated_arity hvX (hvX.regulated r hr)

theorem node_arity {N : SoftNode} (hN : N ∈ D.T.nodes) : VE.Norms.Arity (sortsOf D N.pred) := by
  obtain ⟨r, hr, hrn, _⟩ := VE.SoftNorms.reg_of_node (VE.SoftNorms.softValid_of_wellFormed D hD) hN
  exact hrn ▸ reg_arity hD hr

theorem act_arity {N : SoftNode} (hN : N ∈ D.T.nodes) :
    VE.Norms.Arity (VE.SoftNorms.actSortsOf D (VE.SoftNorms.act D N)) := by
  unfold VE.SoftNorms.actSortsOf VE.SoftNorms.act VE.SoftNorms.actKey
  cases hd : VE.SoftNorms.dualPerm D N.pred with
  | none => exact node_arity hD hN
  | some m =>
    simp only [VE.SoftNorms.dualPerm, Option.map_eq_some_iff] at hd
    obtain ⟨pr, hpr, rfl⟩ := hd
    obtain ⟨_, ⟨m', hm', hmn, _⟩⟩ := VE.SoftNorms.pair_regs (VE.SoftNorms.softValid_of_wellFormed D hD)
      (List.mem_of_find?_eq_some hpr)
    exact hmn ▸ reg_arity hD hm'

/-- Every decision predicate has arity 1 or 2. -/
theorem decision_arity {d : String × List String} (hd : d ∈ VE.SoftNorms.decisions D) : VE.Norms.Arity d.2 := by
  rcases VE.Readings.mem_decisions.mp hd with ⟨N, hN, _, rfl⟩ | ⟨N, hN, _, _, rfl⟩ | ⟨a, L, H, ht, rfl⟩
  · exact node_arity hD hN
  · exact node_arity hD hN
  · obtain ⟨_, M, N, hp, _, hx⟩ := VE.Readings.mem_outweighsTriples.mp ht
    obtain ⟨hM, hN, _⟩ := VE.SoftNorms.mem_collidingPairs.mp hp
    unfold VE.SoftNorms.pairTriple at hx
    split at hx <;> cases hx
    · exact act_arity hD hN
    · exact act_arity hD hM

end Vocabulary

section Facts
variable {U : UDoc} (h : WellFormedU U = true) {D : SoftDoc} (hU : U.D = soften D) (hD : WellFormedSoft D = true)
include h hU hD

/-- An exception condition names neither a decision predicate nor an unsaid predicate. -/
theorem cond_free {N : SoftNode} (hN : N ∈ D.T.nodes) {e : VE.SoftNorms.Exception} (he : N.exception = some e)
    {C : VE.Formula} (hC : C ∈ e.sufficient ++ e.necessary) :
    ∀ p ∈ preds C, p ∉ decisionNames D ∧ p ∉ VE.NormDefaults.unsaidNames U := by
  intro p hp
  obtain ⟨ss, hss⟩ := cond_declared hD hN he hC p hp
  have hd : p ∉ decisionNames D := fun hd => by
    rw [(VE.SoftNorms.softValid_of_wellFormed D hD).decFresh p hd] at hss
    cases hss
  refine ⟨hd, (VE.NormDefaults.uvalid h).not_unsaid (ss := ss) ?_⟩
  rw [hU]
  show (VE.SoftNorms.envPrime D).predicates p = some ss
  unfold VE.SoftNorms.envPrime
  simp only
  rw [List.find?_eq_none.mpr (fun x hx he => hd (List.mem_map.mpr ⟨x, hx, by simpa using he⟩))]
  exact hss

/-- A decision predicate is declared at level 0 of `fill U` with its sorts. -/
theorem decision_declared {d : String × List String} (hd : d ∈ VE.SoftNorms.decisions D) :
    (envAt (fill U) 0).predicates d.1 = some d.2 :=
  VE.NormDefaults.envAt_fill_mono (VE.NormDefaults.uvalid h) 0 _ _ (hU ▸ VE.Readings.envAt_decision hD 0 hd)

theorem decision_not_unsaid {p : String} (hp : p ∈ decisionNames D) : p ∉ VE.NormDefaults.unsaidNames U := by
  obtain ⟨d, hd, rfl⟩ := List.mem_map.mp hp
  refine (VE.NormDefaults.uvalid h).not_unsaid (ss := d.2) ?_
  rw [hU]
  exact VE.Readings.envPrime_decision hD hd

omit h hU hD in
/-- The rule's exception premise for one sufficient condition, and for one necessary condition. -/
theorem mem_exc {N : SoftNode} (hN : N ∈ D.T.nodes) (hn : N.mode = .default) {e : VE.SoftNorms.Exception}
    (he : N.exception = some e) :
    (∀ C ∈ e.sufficient, bindAll (sortsOf D N.pred) (.implies C (exceptedF D N)) ∈ VE.SoftNorms.excPremises D) ∧
    (∀ C ∈ e.necessary, bindAll (sortsOf D N.pred) (.implies (exceptedF D N) C) ∈ VE.SoftNorms.excPremises D) := by
  refine ⟨fun C hC => ?_, fun C hC => ?_⟩ <;> refine List.mem_flatMap.mpr ⟨N, hN, ?_⟩ <;>
    simp only [VE.SoftNorms.excPremisesOf, hn, he]
  · exact List.mem_append_left _ (List.mem_map.mpr ⟨C, hC, rfl⟩)
  · exact List.mem_append_right _ (List.mem_map.mpr ⟨C, hC, rfl⟩)

omit h hU hD in
theorem softX_eq (R : List VE.Formula) : softX U D R = VE.SoftNorms.excPremises D ++
    (VE.SoftNorms.collidingPairs D).map (fun x => VE.NormDefaults.Wire.cohPremiseU U D x.1 x.2) ++ R := by
  simp only [softX, softLabelledU, List.map_append, List.map_map]
  rw [List.map_snd_zip (Nat.le_of_eq ?_)]
  · rfl
  · simp only [VE.SoftNorms.Wire.excLabels, VE.SoftNorms.excPremises, List.length_flatMap]
    congr 1
    apply List.map_congr_left
    intro N _
    simp only [VE.SoftNorms.excPremisesOf]
    cases N.mode <;> cases N.exception <;> simp

end Facts

/-! ## Bases with the least decisions -/

section Least
variable {U : UDoc} {D : SoftDoc}

/-- A formula that names no decision and no unsaid predicate reads the same in every competitor. -/
theorem withOpen_denote (B : VE.Structure.{u}) (δ F : String → List B.Carrier → Prop) (φ : VE.Formula)
    (ρ : VE.Valuation B) (hφ : ∀ p ∈ preds φ, p ∉ decisionNames D ∧ p ∉ VE.NormDefaults.unsaidNames U) :
    φ.denote (withOpen U D B δ F) ρ ↔ φ.denote B ρ :=
  VE.NormDefaults.denote_congr_preds B _ φ ρ (fun p hp vs => by simp [(hφ p hp).1, (hφ p hp).2])

variable (hD : WellFormedSoft D = true)
include hD

/-- `Dflt_T` holds wherever every decision table lies below `δ_B` and the exception conditions read as in `B`. -/
theorem sat_dflt (B : VE.Structure.{u}) (Rel : String → List B.Carrier → Prop)
    (hfacts : ∀ N ∈ D.T.nodes, ∀ e, N.exception = some e → ∀ C ∈ e.sufficient, ∀ ρ,
      C.denote { B with relation := Rel } ρ ↔ C.denote B ρ)
    (hle : ∀ p ∈ decisionNames D, ∀ vs, Rel p vs → leastDecisions D B p vs) :
    Sat { B with relation := Rel } (dfltPremises D) := by
  intro a ha
  obtain ⟨⟨l, a⟩, hla, rfl⟩ := List.mem_map.mp ha
  rcases List.mem_append.mp hla with hn | hr
  · obtain ⟨N, hN, hx⟩ := List.mem_flatMap.mp hn
    unfold dfltOf at hx
    rcases List.mem_append.mp hx with he | hw
    · split at he
      · rename_i e hm hexc
        cases List.mem_singleton.mp he
        have hd : (exceptedName N, sortsOf D N.pred) ∈ VE.SoftNorms.decisions D :=
          VE.Readings.mem_decisions.mpr (Or.inl ⟨N, hN, hm, rfl⟩)
        show (bindAll _ _).denote _ []
        rw [VE.Norms.bindAll_denote_nil]
        intro vs hvs hx
        obtain ⟨N', hN', hm', hname, _, C, hC, hCd⟩ := hle _ (List.mem_map.mpr ⟨_, hd, rfl⟩) vs
          ((VE.Norms.atom_denote _ _ _ (decision_arity hD hd) vs hvs).mp hx)
        cases excepted_inj hD hN hm hN' hm' hname
        simp only [hexc, Option.map_some, Option.getD_some] at hC
        exact (VE.Norms.anyF_denote _ _ _).mpr ⟨C, hC, (hfacts N hN e hexc C hC _).mpr hCd⟩
      · cases he
    · obtain ⟨π, hπ, hx⟩ := List.mem_map.mp hw
      cases hx
      have hd : (VE.SoftNorms.offName N π, sortsOf D N.pred) ∈ VE.SoftNorms.decisions D :=
        VE.Readings.mem_decisions.mpr (Or.inr (Or.inl ⟨N, hN, π, hπ, rfl⟩))
      show (bindAll _ _).denote _ []
      rw [VE.Norms.bindAll_denote_nil]
      intro vs hvs hx
      obtain ⟨N', hN', hm', hname, _⟩ := hle _ (List.mem_map.mpr ⟨_, hd, rfl⟩) vs
        ((VE.Norms.atom_denote _ _ _ (decision_arity hD hd) vs hvs).mp hx)
      exact excepted_only hD hN' hm' (hname ▸ List.mem_append_left _
        (List.mem_map.mpr ⟨_, List.mem_flatMap.mpr ⟨N, hN, List.mem_map.mpr ⟨π, hπ, rfl⟩⟩, rfl⟩))
  · obtain ⟨⟨a', L, H⟩, ht, hx⟩ := List.mem_map.mp hr
    cases hx
    have hd : (VE.SoftNorms.outweighsName a' L H, VE.SoftNorms.actSortsOf D a') ∈ VE.SoftNorms.decisions D :=
      VE.Readings.mem_decisions.mpr (Or.inr (Or.inr ⟨a', L, H, ht, rfl⟩))
    show (bindAll _ _).denote _ []
    rw [VE.Norms.bindAll_denote_nil]
    intro vs hvs hx
    obtain ⟨N', hN', hm', hname, _⟩ := hle _ (List.mem_map.mpr ⟨_, hd, rfl⟩) vs
      ((VE.Norms.atom_denote _ _ _ (decision_arity hD hd) vs hvs).mp hx)
    exact excepted_only hD hN' hm' (hname ▸ List.mem_append_right _
      (List.mem_map.mpr ⟨_, List.mem_map.mpr ⟨_, ht, rfl⟩, rfl⟩))

/-- On a base with the exception premises, `δ_B` lies below the base's decisions. -/
theorem least_le (B : VE.Structure.{u}) (hB : Sat B (VE.SoftNorms.excPremises D)) :
    ∀ p vs, leastDecisions D B p vs → B.relation p vs := by
  rintro p vs ⟨N, hN, hm, rfl, hvs, C, hC, hCd⟩
  obtain ⟨e, he⟩ := Wire.default_exception hD hN hm
  simp only [he, Option.map_some, Option.getD_some] at hC
  have hd : (exceptedName N, sortsOf D N.pred) ∈ VE.SoftNorms.decisions D :=
    VE.Readings.mem_decisions.mpr (Or.inl ⟨N, hN, hm, rfl⟩)
  have hp := hB _ ((mem_exc hN hm he).1 C hC)
  rw [VE.Norms.bindAll_denote_nil] at hp
  exact (VE.Norms.atom_denote _ _ _ (decision_arity hD hd) vs hvs).mp (hp vs hvs hCd)

end Least

/-! ## The meaning theorem -/

/-- Replacement admissibility: on a base admissible with `softX`, the least decisions `δ_B`, with the pair members'
    unsaid tables repaired and every other unsaid table kept, give a base admissible with `defaultX`. -/
theorem replace_admissible (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (hsafe : replacementSafe U D R = true)
    (hcoh : DefaultCoherent.{u} U D R) (B : VE.Structure.{u}) (hB : BaseAdmissibleX U (softX U D R) B) :
    ∃ F : String → List B.Carrier → Prop,
      (∀ p, p ∉ (VE.NormDefaults.pairMembers U).map VE.NormDefaults.unsaidName →
        ∀ vs, (F p vs ↔ B.relation p vs)) ∧
      BaseAdmissibleX U (defaultX D (softX U D R)) (withOpen U D B (leastDecisions D B) F) := by
  classical
  have hu := VE.NormDefaults.uvalid h
  have hBs : Sat B (VE.SoftNorms.excPremises D) := fun a ha =>
    hB.2 a (by rw [softX_eq]; exact List.mem_append_left _ (List.mem_append_left _ ha))
  -- the least decisions, no unsaid table: a base structure of `U.D`
  let R₀ : String → List B.Carrier → Prop := fun n vs =>
    if n ∈ decisionNames D then leastDecisions D B n vs
    else if n ∈ VE.NormDefaults.unsaidNames U then False else B.relation n vs
  let B₀ : VE.Structure.{u} := { B with relation := R₀ }
  have hB₀ : VE.Norms.BaseAdmissible U.D B₀ := by
    refine ⟨⟨fun c s hc => hB.1.1.1.1 c s hc, fun n vs hn => ?_⟩,
      (VE.NormDefaults.sat_literals_relation _ B _).mpr hB.1.1.2⟩
    by_cases hd : n ∈ decisionNames D
    · simp only [B₀, R₀, hd, if_true] at hn
      obtain ⟨N, hN, hm, rfl, hvs, _⟩ := hn
      exact ⟨_, hU ▸ VE.Readings.envAt_decision hD 0 (VE.Readings.mem_decisions.mpr (Or.inl ⟨N, hN, hm, rfl⟩)),
        (VE.Norms.tupleTyped_relation B _ _ vs).mpr hvs⟩
    · by_cases hn' : n ∈ VE.NormDefaults.unsaidNames U
      · simp [B₀, R₀, hd, hn'] at hn
      · simp only [B₀, R₀, hd, hn', if_false] at hn
        obtain ⟨ss, hss, hvs⟩ := hB.1.1.1.2 n vs hn
        refine ⟨ss, ?_, (VE.Norms.tupleTyped_relation B _ _ vs).mpr hvs⟩
        simpa only [envAt, VE.Norms.hide, VE.NormDefaults.layerNames_fill hu, VE.NormDefaults.fill_E,
          VE.NormDefaults.fillEnv_off U hn'] using hss
  obtain ⟨F', hF'off, hF'⟩ := VE.NormDefaults.fill_extends U h B₀ hB₀ B.relation
  let F : String → List B.Carrier → Prop := fun n vs =>
    if n ∈ (VE.NormDefaults.pairMembers U).map VE.NormDefaults.unsaidName then
      (VE.NormDefaults.withFill U B₀ F').relation n vs else B.relation n vs
  have hrel : ∀ n vs, (withOpen U D B (leastDecisions D B) F).relation n vs ↔
      (VE.NormDefaults.withFill U B₀ F').relation n vs := by
    intro n vs
    by_cases hd : n ∈ decisionNames D
    · rw [VE.NormDefaults.withFill_off U B₀ F' (decision_not_unsaid h hU hD hd)]
      simp only [withOpen, B₀, R₀, hd, if_true]
    · by_cases hn : n ∈ VE.NormDefaults.unsaidNames U
      · obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hn
        simp only [withOpen, hd, hn, if_false, if_true, F]
        by_cases hp : VE.NormDefaults.unsaidName q ∈ (VE.NormDefaults.pairMembers U).map VE.NormDefaults.unsaidName
        · simp only [hp, if_true]
        · simp only [hp, if_false]
          rw [VE.NormDefaults.withFill_unsaid U B₀ F' hq, hF'off _ hp]
          refine ⟨fun hr => ⟨hr, ?_⟩, And.left⟩
          obtain ⟨ss, hss, ht⟩ := hB.1.1.1.2 _ vs hr
          rw [VE.NormDefaults.envAt_fill_unsaid hu 0 hq] at hss
          cases hss
          exact (VE.Norms.tupleTyped_relation B R₀ _ vs).mpr ht
      · rw [VE.NormDefaults.withFill_off U B₀ F' hn]
        simp only [withOpen, B₀, R₀, hd, hn, if_false]
  have heq : withOpen U D B (leastDecisions D B) F = VE.NormDefaults.withFill U B₀ F' := by
    unfold withOpen VE.NormDefaults.withFill
    congr 1
    funext n vs
    exact propext (hrel n vs)
  refine ⟨F, fun p hp vs => by simp only [F, if_neg hp], ?_⟩
  have hfacts : ∀ N ∈ D.T.nodes, ∀ e, N.exception = some e → ∀ C ∈ e.sufficient ++ e.necessary, ∀ ρ,
      C.denote (withOpen U D B (leastDecisions D B) F) ρ ↔ C.denote B ρ :=
    fun N hN e he C hC ρ => withOpen_denote B _ F C ρ (cond_free h hU hD hN he hC)
  have hexc : Sat (withOpen U D B (leastDecisions D B) F) (VE.SoftNorms.excPremises D) := by
    intro a ha
    obtain ⟨N, hN, ha⟩ := List.mem_flatMap.mp ha
    unfold VE.SoftNorms.excPremisesOf at ha
    split at ha
    · rename_i e hm he
      have hd : (exceptedName N, sortsOf D N.pred) ∈ VE.SoftNorms.decisions D :=
        VE.Readings.mem_decisions.mpr (Or.inl ⟨N, hN, hm, rfl⟩)
      have hdn : exceptedName N ∈ decisionNames D := List.mem_map.mpr ⟨_, hd, rfl⟩
      rcases List.mem_append.mp ha with ha | ha <;> obtain ⟨C, hC, rfl⟩ := List.mem_map.mp ha <;>
        rw [VE.Norms.bindAll_denote_nil] <;> intro vs hvs hx
      · refine (VE.Norms.atom_denote _ _ _ (decision_arity hD hd) vs hvs).mpr ?_
        simp only [withOpen, hdn, if_true]
        exact ⟨N, hN, hm, rfl, (VE.Norms.tupleTyped_relation B _ _ vs).mp hvs, C, by simp [he, hC],
          (hfacts N hN e he C (List.mem_append_left _ hC) _).mp hx⟩
      · have hr := (VE.Norms.atom_denote _ _ _ (decision_arity hD hd) vs hvs).mp hx
        simp only [withOpen, hdn, if_true] at hr
        obtain ⟨N', hN', hm', hname, hvB, C', hC', hC'd⟩ := hr
        cases excepted_inj hD hN hm hN' hm' hname
        simp only [he, Option.map_some, Option.getD_some] at hC'
        have h1 := hBs _ ((mem_exc hN hm he).1 C' hC')
        have h2 := hBs _ ((mem_exc hN hm he).2 C hC)
        rw [VE.Norms.bindAll_denote_nil] at h1 h2
        exact (hfacts N hN e he C (List.mem_append_right _ hC) _).mpr (h2 vs hvB (h1 vs hvB hC'd))
    · cases ha
  have hRs : Sat (withOpen U D B (leastDecisions D B) F) R := fun φ hφ =>
    (VE.NormDefaults.denote_congr_preds B _ φ [] (fun p hp vs => by
      have hs := List.all_eq_true.mp (List.all_eq_true.mp hsafe φ (List.mem_append_left _ hφ)) p hp
      rw [Bool.and_eq_true] at hs
      have h1 : p ∉ decisionNames D := fun hm => by rw [List.contains_iff_mem.mpr hm] at hs; simp at hs
      have h2 : p ∉ (VE.NormDefaults.pairMembers U).map VE.NormDefaults.unsaidName := fun hm => by
        rw [List.contains_iff_mem.mpr hm] at hs; simp at hs
      by_cases hn : p ∈ VE.NormDefaults.unsaidNames U <;> simp only [F, h1, h2, hn, if_false, if_true])).mpr
      (hB.2 φ (by rw [softX_eq]; exact List.mem_append_right _ hφ))
  have hdflt : Sat (withOpen U D B (leastDecisions D B) F) (dfltPremises D) :=
    sat_dflt hD B _ (fun N hN e he C hC ρ => hfacts N hN e he C (List.mem_append_left _ hC) ρ)
      (fun p hp vs hr => by simpa [hp] using hr)
  have hadm : VE.NormDefaults.BaseAdmissibleU U (withOpen U D B (leastDecisions D B) F) := heq ▸ hF'
  refine ⟨hadm, fun a ha => ?_⟩
  simp only [defaultX, softX_eq, List.mem_append] at ha
  rcases ha with ((ha | ha) | ha) | ha
  · exact hexc a ha
  · obtain ⟨⟨M, N⟩, hMN, rfl⟩ := List.mem_map.mp ha
    exact hcoh _ ⟨hadm, fun b hb => by
      simp only [List.mem_append] at hb
      rcases hb with (hb | hb) | hb
      · exact hexc b hb
      · exact hRs b hb
      · exact hdflt b hb⟩ M N hMN
  · exact hRs a ha
  · exact hdflt a ha

/-- A base with the no-exception premises is a default base. No gate needed. -/
theorem defaultBase_of_dflt (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (B : VE.Structure.{u})
    (hB : BaseAdmissibleX U (defaultX D (softX U D R)) B) :
    DefaultBase U D (softX U D R) B := by
  have hdf : Sat B (dfltPremises D) := fun a ha => hB.2 a (List.mem_append_right _ ha)
  refine ⟨⟨hB.1, fun a ha => hB.2 a (List.mem_append_left _ ha)⟩, fun a ha => hdf a (by
      obtain ⟨x, hx, rfl⟩ := List.mem_map.mp ha
      exact List.mem_map.mpr ⟨x, (List.mem_filter.mp hx).1, rfl⟩), fun δ F _ hC _ p hp vs hr => ?_⟩
  obtain ⟨d, hd, rfl⟩ := List.mem_map.mp hp
  obtain ⟨ss, hss, hvs⟩ := hB.1.1.1.2 _ vs hr
  rw [decision_declared h hU hD hd] at hss
  cases hss
  have hx := (VE.Norms.atom_denote B _ _ (decision_arity hD hd) vs hvs).mpr hr
  rcases VE.Readings.mem_decisions.mp hd with ⟨N, hN, hm, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, ht, rfl⟩
  · obtain ⟨e, he⟩ := Wire.default_exception hD hN hm
    have hp := hdf _ (List.mem_map.mpr ⟨_, List.mem_append_left _ (List.mem_flatMap.mpr ⟨N, hN, by
      simp only [dfltOf, hm, he]; exact List.mem_append_left _ List.mem_cons_self⟩), rfl⟩)
    rw [VE.Norms.bindAll_denote_nil] at hp
    obtain ⟨C, hCm, hCd⟩ := (VE.Norms.anyF_denote _ _ _).mp (hp vs hvs hx)
    have hc := hC.2 _ (by rw [softX_eq]; exact List.mem_append_left _ (List.mem_append_left _
      ((mem_exc hN hm he).1 C hCm)))
    rw [VE.Norms.bindAll_denote_nil] at hc
    have hvW : VE.TupleTyped (withOpen U D B δ F) _ vs := (VE.Norms.tupleTyped_relation B _ _ vs).mpr hvs
    have := (VE.Norms.atom_denote (withOpen U D B δ F) _ _ (decision_arity hD hd) vs hvW).mp (hc vs hvW
      ((withOpen_denote B δ F C _ (cond_free h hU hD hN he (List.mem_append_left _ hCm))).mpr hCd))
    have hdn : exceptedName N ∈ decisionNames D := List.mem_map.mpr ⟨_, hd, rfl⟩
    simp only [withOpen] at this
    rwa [if_pos hdn] at this
  · have hq := hdf _ (List.mem_map.mpr ⟨_, List.mem_append_left _ (List.mem_flatMap.mpr ⟨N, hN,
      List.mem_append_right _ (List.mem_map.mpr ⟨π, hπ, rfl⟩)⟩), rfl⟩)
    rw [VE.Norms.bindAll_denote_nil] at hq
    exact absurd hx (hq vs hvs)
  · have hq := hdf _ (List.mem_map.mpr ⟨_, List.mem_append_right _ (List.mem_map.mpr ⟨_, ht, rfl⟩), rfl⟩)
    rw [VE.Norms.bindAll_denote_nil] at hq
    exact absurd hx (hq vs hvs)

/-- The fallback (plan 3.4): with `replace_admissible`'s conclusion as a hypothesis, a default answer means truth in
    every default base. -/
theorem default_entails_minimal_of (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (hrep : ReplacementHolds.{u} U D R)
    (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsX.{u} U (defaultX D (softX U D R)) Γ φ ↔
      ∀ S : VE.Structure.{u}, DefaultBase U D (softX U D R) (restrictAll (fill U).T S) →
        DocumentExpansion (fill U) (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S [] := by
  refine ⟨fun he S hS hE hΓ => he S ?_ hE hΓ,
    fun hr S hS hE hΓ => hr S (defaultBase_of_dflt U h D hU hD R _ hS) hE hΓ⟩
  obtain ⟨hB, -, hmin⟩ := hS
  have hBs : Sat (restrictAll (fill U).T S) (VE.SoftNorms.excPremises D) := fun a ha =>
    hB.2 a (by rw [softX_eq]; exact List.mem_append_left _ (List.mem_append_left _ ha))
  obtain ⟨F, hF⟩ := hrep _ hB
  have hle := hmin _ F (fun p _ vs => least_le hD _ hBs p vs) ⟨hF.1, fun a ha => hF.2 a (List.mem_append_left _ ha)⟩
    (fun a ha => hF.2 a (List.mem_append_right _ (by
      obtain ⟨x, hx, rfl⟩ := List.mem_map.mp ha
      exact List.mem_map.mpr ⟨x, (List.mem_filter.mp hx).1, rfl⟩)))
  exact ⟨hB.1, fun a ha => (List.mem_append.mp ha).elim (hB.2 a)
    (sat_dflt hD (restrictAll (fill U).T S) (restrictAll (fill U).T S).relation
      (fun _ _ _ _ _ _ _ => Iff.rfl) hle a)⟩

/-- Under the gate and the computed check, a default answer means: the conclusion holds in every expansion of every
    default base where the question's facts hold. -/
theorem default_entails_minimal (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (hsafe : replacementSafe U D R = true)
    (hcoh : DefaultCoherent.{u} U D R) (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsX.{u} U (defaultX D (softX U D R)) Γ φ ↔
      ∀ S : VE.Structure.{u}, DefaultBase U D (softX U D R) (restrictAll (fill U).T S) →
        DocumentExpansion (fill U) (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S [] :=
  default_entails_minimal_of U h D hU hD R
    (fun B hB => (replace_admissible U h D hU hD R hsafe hcoh B hB).imp fun _ hF => hF.2) Γ φ

/-- `defaults_model_sound`'s situation is a default base. -/
theorem defaults_model_default_base (x : Wire.ModelReplay) (hv : x.ok = true) :
    ∃ S : VE.Structure.{0}, DefaultBase x.v.L.U x.v.L.D x.v.L.X (restrictAll (fill x.v.L.U).T S) ∧
      DocumentExpansion (fill x.v.L.U) (restrictAll (fill x.v.L.U).T S) S ∧ Sat S x.Γ ∧ ¬ x.φ.denote S [] := by
  obtain ⟨S, hB, hE, hΓ, hφ, -⟩ := Wire.defaults_model_sound x hv
  have hX : x.v.L.X = softX x.v.L.U x.v.L.D x.v.R := x.v.hX
  rw [hX] at hB ⊢
  exact ⟨S, defaultBase_of_dflt _ x.v.L.wfU _ x.v.hU x.v.hD _ _ hB, hE, hΓ, hφ⟩

end VE.Defaults
