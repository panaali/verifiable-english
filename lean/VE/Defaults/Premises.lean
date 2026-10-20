import VE.Readings.VerdictsWire
import VE.Readings.SupEnv

/-! Answers that hold unless an exception applies (docs/spec/defeasible.md 3.1 to 3.5 and 7.1; plan DF-1a): the
no-exception premises `Dflt_T`, the gate, the basis and the form.

`Dflt_T` is regenerated from the decoded soft document: per default rule, "its exception holds only where one of its
stated sufficient conditions holds" (`∀x̄. excepted → ⊥ ∨ C₁ ∨ … ∨ C_k`); per switch, "no one has turned it off"; per
`outweighs` decision, "the lower-ranked consideration does not outweigh the higher one". A default answer is RD-9's
checked entailment with `defaultX D X = X ++ Dflt_T`, so RD-9's theorems apply unchanged (`acceptanceX`,
`modelCheckX_sound`).

The gate `DefaultCoherent` asks that no two colliding default rules both select on a base admissible with
`Exc_T ++ R ++ Dflt_T`. It has three outcomes: one checked certificate per pair (`defaultCoherenceCheck_sound`), a
checked finite collision (`collision_sound`), or neither.

The basis is three-valued: `strict` when the certificate keeps no `Dflt_T` label (`basis_strict_sound`), `needs` when
it keeps some and a strict countermodel checks with RD-9's `xModelOk` (`basis_needs_sound`), `unsettled` otherwise.
The kept labels are sufficient for the certificate checked; they are not claimed to be the fewest. `followsForm`
selects DE1's short form only when every kept label is a rule's exception with no stated condition
(`followsForm_short`). -/
namespace VE.Defaults
open VE.Norms (bindAll atom anyF preds Sat DocumentExpansion restrictAll envAt size)
open VE.SoftNorms (SoftDoc SoftNode exceptedF outweighsF offName sortsOf actSortsOf outweighsTriples
  decisionNames offDecisions collidingPairs excPremises soften WellFormedSoft)
open VE.NormDefaults (UDoc fill fillPremises WellFormedU EntailsX modelCheckX)
open VE.NormDefaults.Wire (BaseAdmissibleX cohPremiseU softLabelledU premisesX LayeredU)
universe u

/-! ## `Dflt_T` -/

/-- The no-exception premises of one rule: its exception holds only where one of its stated sufficient conditions
    holds, and none of its switches is on. -/
def dfltOf (D : SoftDoc) (N : SoftNode) : List (String × VE.Formula) :=
  (match N.mode, N.exception with
   | .default, some e =>
       [("default:exception:" ++ N.name,
         bindAll (sortsOf D N.pred) (.implies (exceptedF D N) (anyF e.sufficient)))]
   | _, _ => []) ++
  N.alterable.map (fun π =>
    ("default:switch:" ++ N.name ++ ":" ++ π,
     bindAll (sortsOf D N.pred) (.not (atom (offName N π) (sortsOf D N.pred)))))

/-- `Dflt_T`: the rules' premises in rule order, then one per `outweighs` decision, in soft's triple order. -/
def dfltLabelled (D : SoftDoc) : List (String × VE.Formula) :=
  D.T.nodes.flatMap (dfltOf D) ++
  (outweighsTriples D).map (fun (a, L, H) =>
    ("default:ranking:" ++ L ++ ":" ++ H ++ ":" ++ a, bindAll (actSortsOf D a) (.not (outweighsF D a L H))))

def dfltPremises (D : SoftDoc) : List VE.Formula := (dfltLabelled D).map (·.2)
def dfltLabels (D : SoftDoc) : List String := (dfltLabelled D).map (·.1)

/-- The premises of a default answer: the document's own `X` (PK-1's assembled X), then `Dflt_T`. -/
def defaultX (D : SoftDoc) (X : List VE.Formula) : List VE.Formula := X ++ dfltPremises D

/-- `Dflt_T` read as `⊤`. -/
def withoutDefaults (D : SoftDoc) (X : List VE.Formula) : List VE.Formula :=
  X ++ (dfltPremises D).map (fun _ => VE.Formula.top)

/-! ## What a default answer may be asked (diagnostics 2, 3 and 4) -/

/-- No decision predicate occurs: an exception, a switch or an `outweighs` decision. -/
def decisionFree (D : SoftDoc) (φ : VE.Formula) : Bool :=
  (preds φ).all (fun p => !(decisionNames D).contains p)

/-- What a question premise naming `p` states: a decision (found by its key) or a regulated outcome. -/
def whatOf (D : SoftDoc) (p : String) : Option String :=
  match (VE.SoftNorms.keyedDecisions D).find? (·.2.1 == p) with
  | some (.excepted r, _) => some s!"whether rule {r}'s exception applies"
  | some (.off r π, _) => some s!"whether {π} has turned rule {r} off"
  | some (.outweighs a L H, _) => some s!"whether the {L} consideration outweighs the {H} consideration on {a}"
  | none => if (D.T.regulated.map (·.name)).contains p then some s!"the outcome {p}" else none

/-- Diagnostic 3: the first premise predicate, in premise order, that is a decision or a regulated outcome. -/
def questionDiag (D : SoftDoc) (Γ : List VE.Formula) : Option String :=
  ((Γ.flatMap preds).findSome? (whatOf D)).map (fun w =>
    "InvalidInput: a question that assumes no exception may state facts only; it states " ++ w)

/-- Without diagnostic 3 the question states facts only: no premise names a decision or a regulated outcome. -/
theorem questionDiag_none (D : SoftDoc) (Γ : List VE.Formula) (h : questionDiag D Γ = none) :
    ∀ a ∈ Γ, ∀ p ∈ preds a, p ∉ decisionNames D ∧ p ∉ D.T.regulated.map (·.name) := by
  intro a ha p hp
  have hw : whatOf D p = none := by
    unfold questionDiag at h
    exact List.findSome?_eq_none_iff.mp (Option.map_eq_none_iff.mp h) p (List.mem_flatMap.mpr ⟨a, ha, hp⟩)
  unfold whatOf at hw
  split at hw
  · cases hw
  · cases hw
  · cases hw
  · rename_i hf
    refine ⟨fun hd => ?_, fun hr => ?_⟩
    · rw [decisionNames, ← VE.SoftNorms.keyedDecisions_names, List.map_map] at hd
      obtain ⟨k, hk, hkp⟩ := List.mem_map.mp hd
      have := List.find?_eq_none.mp hf k hk
      simp_all
    · rw [if_pos (List.contains_iff_mem.mpr hr)] at hw
      cases hw

/-- Diagnostic 4: the first `Dflt_T` premise outside soft's node and depth limits. -/
def limitDiag (D : SoftDoc) : Option String :=
  ((dfltLabelled D).find? (fun x => !VE.SoftNorms.withinLimits x.2)).map (fun x =>
    "ResourceLimit: generated default premise " ++ x.1)

/-- `atom p ss` is typed by `ss` wherever `p` is declared with `ss` (outside arities 1 and 2 it is `⊥`). -/
theorem atom_wf {E : VE.Environment} {p : String} {ss : List String} (hp : E.predicates p = some ss) :
    (atom p ss).WellFormed E ss.reverse := by
  match ss with
  | [s] => exact ⟨s, hp, rfl⟩
  | [s, t] => exact ⟨s, t, hp, rfl, rfl⟩
  | [] | [_, _, _] | _ :: _ :: _ :: _ :: _ => trivial

/-- Each premise of `Dflt_T` is closed and typed over the filled base vocabulary (PK-1's provider obligation 2). -/
theorem dflt_wellFormed (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) :
    ∀ a ∈ dfltPremises D, a.WellFormed (envAt (fill U) 0) [] := by
  obtain ⟨D₀, unspec⟩ := U
  simp only at hU
  subst hU
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ hD
  -- A decision atom under its own sorts, with the sorts declared.
  have hdec : ∀ d ∈ VE.SoftNorms.decisions D, ∀ body : VE.Formula,
      body.WellFormed (envAt (soften D) 0) d.2.reverse → (bindAll d.2 body).WellFormed (envAt (soften D) 0) [] :=
    fun d hd body hb => VE.Norms.bindAll_wellFormed (E := envAt (soften D) 0) (fun s hs => VE.Readings.decision_sorts hD hd s hs) [] body
      (by simpa using hb)
  have hatom : ∀ d ∈ VE.SoftNorms.decisions D, (atom d.1 d.2).WellFormed (envAt (soften D) 0) d.2.reverse :=
    fun d hd => atom_wf (VE.Readings.envAt_decision hD 0 hd)
  suffices hs : ∀ a ∈ dfltPremises D, a.WellFormed (envAt (soften D) 0) [] from fun a ha =>
    VE.Norms.wf_mono (E := envAt (soften D) 0) (E' := envAt (fill ⟨soften D, unspec⟩) 0) rfl rfl
      (VE.NormDefaults.envAt_fill_mono (VE.NormDefaults.uvalid h) 0) a [] (hs a ha)
  intro a ha
  obtain ⟨⟨l, a⟩, hla, rfl⟩ := List.mem_map.mp ha
  rcases List.mem_append.mp hla with hn | hr
  · obtain ⟨N, hN, hx⟩ := List.mem_flatMap.mp hn
    unfold dfltOf at hx
    rcases List.mem_append.mp hx with he | hw
    · split at he
      · rename_i e hm hexc
        cases List.mem_singleton.mp he
        have hd : (VE.SoftNorms.exceptedName N, sortsOf D N.pred) ∈ VE.SoftNorms.decisions D :=
          VE.Readings.mem_decisions.mpr (Or.inl ⟨N, hN, hm, rfl⟩)
        refine hdec _ hd _ ⟨hatom _ hd, VE.Norms.anyF_wellFormed _ _ _ (fun C hC => ?_)⟩
        have hp : bindAll (sortsOf D N.pred) (.implies C (exceptedF D N)) ∈ excPremises D :=
          List.mem_flatMap.mpr ⟨N, hN, by
            simp only [VE.SoftNorms.excPremisesOf, hm, hexc]
            exact List.mem_append_left _ (List.mem_map.mpr ⟨C, hC, rfl⟩)⟩
        have := VE.Norms.bindAll_wellFormed_inv _ _ [] (hsv.premTyped _ (List.mem_append_left _ hp))
        simpa using this.1
      · cases he
    · obtain ⟨π, hπ, hx⟩ := List.mem_map.mp hw
      cases hx
      have hd : (offName N π, sortsOf D N.pred) ∈ VE.SoftNorms.decisions D :=
        VE.Readings.mem_decisions.mpr (Or.inr (Or.inl ⟨N, hN, π, hπ, rfl⟩))
      exact hdec _ hd _ (hatom _ hd)
  · obtain ⟨⟨a', L, H⟩, ht, hx⟩ := List.mem_map.mp hr
    cases hx
    have hd : (VE.SoftNorms.outweighsName a' L H, actSortsOf D a') ∈ VE.SoftNorms.decisions D :=
      VE.Readings.mem_decisions.mpr (Or.inr (Or.inr ⟨a', L, H, ht, rfl⟩))
    exact hdec _ hd _ (hatom _ hd)

/-- More premises (or `⊤`) never lose an entailment. -/
theorem entailsX_mono (U : UDoc) (X₁ X₂ Γ : List VE.Formula) (φ : VE.Formula)
    (h : ∀ a ∈ X₁, a = .top ∨ a ∈ X₂) : EntailsX.{u} U X₁ Γ φ → EntailsX.{u} U X₂ Γ φ := by
  intro he S hB hE hΓ
  refine he S ⟨hB.1, fun a ha => ?_⟩ hE hΓ
  rcases h a ha with rfl | ha
  · simp [VE.Formula.denote]
  · exact hB.2 a ha

/-- A conclusion that follows with every `Dflt_T` premise read as `⊤` follows from the document's own premises. -/
theorem strict_of_withoutDefaults (U : UDoc) (D : SoftDoc) (X Γ : List VE.Formula) (φ : VE.Formula)
    (h : EntailsX.{u} U (withoutDefaults D X) Γ φ) : EntailsX.{u} U X Γ φ :=
  entailsX_mono U _ _ Γ φ (fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact Or.inr ha
    · obtain ⟨_, _, rfl⟩ := List.mem_map.mp ha
      exact Or.inl rfl) h

/-! ## The gate -/

/-- On every base admissible with the exception premises, the other packs' premises `R` and `Dflt_T`, no colliding
    pair of default rules both selects. -/
def DefaultCoherent (U : UDoc) (D : SoftDoc) (R : List VE.Formula) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U (excPremises D ++ R ++ dfltPremises D) B →
    ∀ M N, (M, N) ∈ collidingPairs D → (cohPremiseU U D M N).denote B []

/-- One pair's certificate checks: the pair's `cohPremiseU` from `Exc_T ++ R ++ Dflt_T` with the base background
    and `Fill_T`. -/
def pairChecks (U : UDoc) (D : SoftDoc) (R : List VE.Formula) (P Q : SoftNode)
    (c : Option VE.Tableau.Certificate) : Bool :=
  match c with
  | some c => VE.Tableau.checkCertificate (envAt (fill U) 0)
      (VE.Norms.backgroundBase (fill U) ++ (excPremises D ++ R ++ dfltPremises D) ++ fillPremises U)
      (cohPremiseU U D P Q) c
  | none => false

/-- One certificate per colliding pair, in `collidingPairs` order. -/
def defaultCoherenceCheck (U : UDoc) (D : SoftDoc) (R : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (collidingPairs D).length == certs.length &&
    ((collidingPairs D).zip certs).all (fun (p, c) => pairChecks U D R p.1 p.2 c)

/-- One pair resolved: its coherence premise holds on every base admissible with `Exc_T ++ R ++ Dflt_T`. -/
theorem pairChecks_sound (U : UDoc) (D : SoftDoc) (R : List VE.Formula) (P Q : SoftNode)
    (c : Option VE.Tableau.Certificate) (hc : pairChecks U D R P Q c = true) (B : VE.Structure.{u})
    (hB : BaseAdmissibleX U (excPremises D ++ R ++ dfltPremises D) B) : (cohPremiseU U D P Q).denote B [] := by
  cases c with
  | none => cases hc
  | some c =>
    exact VE.Tableau.checkCertificate_sound.{u} _ _ _ c hc B hB.1.1.1 (fun a ha => by
      rcases List.mem_append.mp ha with ha | ha
      · rcases List.mem_append.mp ha with ha | ha
        · exact hB.1.1.2 a ha
        · exact hB.2 a ha
      · exact hB.1.2 a ha)

theorem defaultCoherenceCheck_sound (U : UDoc) (D : SoftDoc) (R : List VE.Formula)
    (certs : List (Option VE.Tableau.Certificate)) (hc : defaultCoherenceCheck U D R certs = true) :
    DefaultCoherent.{u} U D R := by
  intro B hB M N hMN
  simp only [defaultCoherenceCheck, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
  obtain ⟨hl, hall⟩ := hc
  obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp hMN
  have hlt : i < (collidingPairs D).length := (List.getElem?_eq_some_iff.mp hi).1
  have hlt' : i < certs.length := hl ▸ hlt
  have hmem : ((M, N), certs[i]) ∈ (collidingPairs D).zip certs := by
    apply List.mem_iff_getElem?.mpr
    refine ⟨i, ?_⟩
    rw [List.getElem?_zip_eq_some]
    exact ⟨hi, List.getElem?_eq_getElem hlt'⟩
  exact pairChecks_sound U D R M N _ (hall _ hmem) B hB

/-- A checked collision: the finite base and filling satisfy the base background, `Fill_T` and
    `Exc_T ++ R ++ Dflt_T`, and the coherence premise of the named colliding pair is false there. -/
def collisionCheck (U : UDoc) (D : SoftDoc) (R : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (m n : String) : Bool :=
  match (collidingPairs D).find? (fun p => p.1.name == m && p.2.name == n) with
  | none => false
  | some (P, Q) =>
    VE.Norms.backgroundValid U.D M && VE.NormDefaults.fillValid U M F &&
      VE.NormDefaults.Wire.extraValid U (excPremises D ++ R ++ dfltPremises D) M F &&
      !(cohPremiseU U D P Q).eval (M.withFill F) []

theorem collision_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (R : List VE.Formula)
    (M : VE.FiniteModel VE.Bridge.Entity) (valid : M.Valid (envAt U.D 0))
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (m n : String)
    (hc : collisionCheck U D R M F m n = true) :
    ¬ DefaultCoherent.{0} U D R := by
  intro hcoh
  unfold collisionCheck at hc
  split at hc
  · cases hc
  · rename_i P Q hf
    simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
    obtain ⟨⟨⟨hb, hF⟩, hX⟩, hn⟩ := hc
    have hB := VE.NormDefaults.Wire.admissibleX_of_fill U h _ M valid hb F hF hX
    have hd := hcoh _ hB P Q (List.mem_of_find?_eq_some hf)
    rw [← VE.NormDefaults.eval_withFill] at hd
    rw [hd] at hn
    cases hn

/-! ## The collision DE7 shows -/

/-- A rule's selection on the filled tree, as `cohPremiseU` builds it. -/
def selU (U : UDoc) (D : SoftDoc) (K : SoftNode) : VE.Formula :=
  VE.Norms.subst (fill U).T (size (fill U)) (VE.Norms.selects (fill U).T (VE.Norms.fuel (fill U).T) (VE.SoftNorms.primeNode D K))

theorem cohPremiseU_selU (U : UDoc) (D : SoftDoc) (P Q : SoftNode) :
    cohPremiseU U D P Q = bindAll (VE.SoftNorms.actSorts D P) (.not (.and (selU U D P) (selU U D Q))) := rfl

/-- The first tuple, in `allTuples` order, where both rules of the pair select. -/
def collisionTuple (U : UDoc) (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (P Q : SoftNode) : Option (List VE.Bridge.Entity) :=
  (VE.NormDefaults.allTuples M (VE.SoftNorms.actSorts D P)).find? (fun vs =>
    (VE.Formula.and (selU U D P) (selU U D Q)).eval (M.withFill F) (VE.Norms.tupleVal vs))

/-- DE7 always has a tuple to show. -/
theorem collisionTuple_some (U : UDoc) (D : SoftDoc) (R : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (m n : String) (P Q : SoftNode)
    (hp : (collidingPairs D).find? (fun p => p.1.name == m && p.2.name == n) = some (P, Q))
    (hc : collisionCheck U D R M F m n = true) :
    ∃ vs, collisionTuple U D M F P Q = some vs := by
  unfold collisionCheck at hc
  rw [hp] at hc
  simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
  have hn : ¬ (cohPremiseU U D P Q).denote
      (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F)) [] := fun hd => by
    rw [← VE.NormDefaults.eval_withFill, hc.2] at hd
    cases hd
  cases hf : collisionTuple U D M F P Q with
  | some vs => exact ⟨vs, rfl⟩
  | none =>
    refine absurd ?_ hn
    rw [cohPremiseU_selU, VE.Norms.bindAll_denote_nil]
    intro vs hvs hs
    have hb := List.find?_eq_none.mp hf vs ((VE.NormDefaults.mem_allTuples M _ vs).mpr ((VE.Norms.tupleTyped_relation M.asStructure
      (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F)).relation _ vs).mp hvs))
    exact hb ((VE.NormDefaults.eval_withFill U M F _ _).mpr hs)

/-- Soft's `coh_rank_valid_unconditional` on the filled tree: a ranked pair's coherence premise is valid. -/
theorem cohU_rank_valid (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (M N : SoftNode) (hc : (M, N) ∈ collidingPairs D)
    (hcmp : VE.SoftNorms.Comparable D M N = true) (B : VE.Structure.{u}) : (cohPremiseU U D M N).denote B [] := by
  rw [cohPremiseU_selU, VE.Norms.bindAll_denote_nil]
  intro vs _
  exact VE.SoftNorms.coh_rank_valid_with D hD M N hc hcmp _ _ _ B (VE.Norms.tupleVal vs)

/-- DE7's "The text ranks neither above the other": a checked collision's pair is unranked. -/
theorem collision_unranked (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (R : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (valid : M.Valid (envAt U.D 0)) (F : VE.NormDefaults.FiniteFill U VE.Bridge.Entity) (m n : String)
    (P Q : SoftNode) (hp : (collidingPairs D).find? (fun p => p.1.name == m && p.2.name == n) = some (P, Q))
    (hc : collisionCheck U D R M F m n = true) :
    VE.SoftNorms.Comparable D P Q = false := by
  cases hcmp : VE.SoftNorms.Comparable D P Q with
  | false => rfl
  | true =>
    unfold collisionCheck at hc
    rw [hp] at hc
    simp only [Bool.and_eq_true, Bool.not_eq_true'] at hc
    have hv := cohU_rank_valid.{0} U h D hU hD P Q (List.mem_of_find?_eq_some hp) hcmp
      (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F))
    rw [← VE.NormDefaults.eval_withFill, hc.2] at hv
    cases hv

/-! ## The basis -/

/-- The certificate check the answer kinds use, at `acceptanceX`'s environment. -/
def certChecks (U : UDoc) (ps : List VE.Formula) (φ : VE.Formula) (c : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) ps φ c

/-- RD-9's premise list with `defaultX`, split around `Dflt_T`. -/
theorem premisesX_split (U : UDoc) (D : SoftDoc) (X Γ : List VE.Formula) :
    premisesX U (defaultX D X) Γ =
      (VE.Norms.background (fill U) ++ X) ++ (dfltLabelled D).map (·.2) ++
        (fillPremises U ++ VE.Norms.elaborate (fill U).T ++ Γ) := by
  simp [VE.NormDefaults.Wire.premisesX, defaultX, dfltPremises, List.append_assoc]

/-- The `Dflt_T` labels a certificate needs: readings' `usedLabels` over `Dflt_T` in `premisesX`'s split. The list is
    sufficient for this certificate; it is not claimed to be the fewest. -/
def assumptionsOf (U : UDoc) (D : SoftDoc) (X Γ : List VE.Formula) (φ : VE.Formula)
    (c : VE.Tableau.Certificate) : List String :=
  VE.Readings.usedLabels (fun ps => certChecks U ps φ c)
    (VE.Norms.background (fill U) ++ X) (dfltLabelled D)
    (fillPremises U ++ VE.Norms.elaborate (fill U).T ++ Γ)

theorem assumptions_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (hl : VE.Compose.Labelled.wellLabelled (dfltLabelled D) = true)
    (X Γ : List VE.Formula) (hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []) (φ : VE.Formula)
    (c : VE.Tableau.Certificate) (hc : certChecks U (premisesX U (defaultX D X) Γ) φ c = true) :
    EntailsX.{u} U (X ++ VE.Readings.blank (dfltLabelled D) (assumptionsOf U D X Γ φ c)) Γ φ := by
  have hs := VE.Readings.usedLabels_sound (fun ps => certChecks U ps φ c) (VE.Norms.background (fill U) ++ X)
    (dfltLabelled D) (fillPremises U ++ VE.Norms.elaborate (fill U).T ++ Γ) hl
    (by rw [premisesX_split] at hc; exact hc)
  have hw := dflt_wellFormed U h D hU hD
  apply VE.NormDefaults.acceptanceX U h _ ?_ Γ φ c
  · simpa [certChecks, VE.NormDefaults.Wire.premisesX, assumptionsOf, List.append_assoc] using hs
  · intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact hX a ha
    · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp ha
      split
      · exact hw x.2 (List.mem_map.mpr ⟨x, hx, rfl⟩)
      · exact trivial

/-- `strict`: no `Dflt_T` label kept. `needs`: labels kept, and a strict countermodel checked. `unsettled`: labels
    kept, and no strict countermodel checked. -/
inductive Basis | strict | needs | unsettled
  deriving DecidableEq, Repr

def basisOf (as : List String) (strictCounter : Bool) : Basis :=
  if as.isEmpty then .strict else if strictCounter then .needs else .unsettled

/-- `basis = strict` is sound: the conclusion follows from the document's own premises. -/
theorem basis_strict_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (hl : VE.Compose.Labelled.wellLabelled (dfltLabelled D) = true)
    (X Γ : List VE.Formula) (hX : ∀ a ∈ X, a.WellFormed (envAt (fill U) 0) []) (φ : VE.Formula)
    (c : VE.Tableau.Certificate) (hc : certChecks U (premisesX U (defaultX D X) Γ) φ c = true) (sc : Bool)
    (hb : basisOf (assumptionsOf U D X Γ φ c) sc = .strict) :
    EntailsX.{u} U X Γ φ := by
  have he := assumptions_sound.{u} U h D hU hD hl X Γ hX φ c hc
  have hn : assumptionsOf U D X Γ φ c = [] := by
    unfold basisOf at hb
    split at hb
    · exact List.isEmpty_iff.mp (by assumption)
    · split at hb <;> cases hb
  rw [hn] at he
  apply strict_of_withoutDefaults U D X Γ φ
  simpa [withoutDefaults, dfltPremises, VE.Readings.blank, Function.comp_def] using he

/-- `basis = needs` is sound: a strict countermodel checked by RD-9's `xModelOk` on the document's own `X` (with local
    conflict freedom, so the situation has an expansion) shows that the conclusion does not follow without the
    assumptions. -/
theorem basis_needs_sound (U : UDoc) (h : WellFormedU U = true) (X Γ : List VE.Formula) (φ : VE.Formula)
    (m : VE.Readings.Wire.FilledModel U) (hm : VE.Readings.Wire.xModelOk U X [] Γ φ m false = true) :
    VE.Readings.CounterX U X Γ φ ∧ ¬ EntailsX.{0} U X Γ φ := by
  simp only [VE.Readings.Wire.xModelOk, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hm
  obtain ⟨⟨⟨hw, hm⟩, hv⟩, hl⟩ := hm
  have hw' : ∀ a ∈ ([] ++ Γ) ++ [φ], a.WellFormed (envAt (fill U) (size (fill U))) [] :=
    fun a ha => (VE.check_iff_wellFormed _ _ a).mp (hw a ha)
  obtain ⟨S, h1, h2, h3, h4⟩ := VE.Readings.Wire.expansionX_of_modelCheck U h X m.M m.valid m.F ([] ++ Γ) φ
    (fun a ha => hw' a (List.mem_append_left _ ha)) (hw' φ (List.mem_append_right _ List.mem_cons_self)) hm hl
  have hc : VE.Readings.CounterX U X Γ φ :=
    ⟨S, h1, h2, by simpa using h3, fun hd => by
      have := h4.mp hd
      rw [hv] at this
      cases this⟩
  refine ⟨hc, fun he => ?_⟩
  obtain ⟨S, h1, h2, h3, h4⟩ := hc
  exact h4 (he S h1 h2 h3)

/-! ## The form -/

/-- Which form of DE1 Lean selects. -/
inductive Form | short | long
  deriving DecidableEq, Repr

/-- The labels whose premise says only "rule n's exception does not apply": a default rule's exception premise with
    no stated sufficient condition. -/
def bareExceptionLabels (D : SoftDoc) : List String :=
  D.T.nodes.filterMap (fun N => match N.mode, N.exception with
    | .default, some e => if e.sufficient.isEmpty then some ("default:exception:" ++ N.name) else none
    | _, _ => none)

/-- DE1's short form only when every kept assumption is a bare exception: no switch, no ranking, no stated
    condition. -/
def followsForm (D : SoftDoc) (as : List String) : Form :=
  if as.all (fun l => (bareExceptionLabels D).contains l) then .short else .long

/-- DE1's short form says no more than the kept premises: each is "rule n's exception holds nowhere". -/
theorem followsForm_short (D : SoftDoc) (as : List String) (h : followsForm D as = .short) :
    ∀ l ∈ as, ∃ N ∈ D.T.nodes, l = "default:exception:" ++ N.name ∧
      (l, bindAll (sortsOf D N.pred) (.implies (exceptedF D N) (anyF []))) ∈ dfltLabelled D := by
  intro l hl
  unfold followsForm at h
  split at h
  · rename_i hall
    have hb := List.contains_iff_mem.mp (List.all_eq_true.mp hall l hl)
    obtain ⟨N, hN, hx⟩ := List.mem_filterMap.mp hb
    split at hx
    · rename_i e hm hexc
      split at hx
      · rename_i hemp
        cases hx
        refine ⟨N, hN, rfl, List.mem_append_left _ (List.mem_flatMap.mpr ⟨N, hN, ?_⟩)⟩
        simp only [dfltOf, hm, hexc, List.isEmpty_iff.mp hemp]
        exact List.mem_append_left _ List.mem_cons_self
      · cases hx
    · cases hx
  · cases h


/-! ## The deciders DE5 and DE7 name -/

/-- DE5's deciders: each rule's exception decider and switch parties, then the outranking decider when a ranking
    decision exists, each once, in rule order. -/
def decidersOf (D : SoftDoc) : List String :=
  let raw := D.T.nodes.flatMap (fun N =>
      (match N.mode, N.exception with
       | .default, some _ => [VE.SoftNorms.Wire.exceptionDecider D N]
       | _, _ => []) ++ N.alterable) ++
    (if (outweighsTriples D).isEmpty then [] else [(D.soft.outrankingDecider).getD "unstated"])
  raw.foldl (fun acc d => if acc.contains d then acc else acc ++ [d]) []

/-- DE7's deciders: one when the two rules' exceptions have the same decider (soft's `exceptionDecider`), otherwise
    both, in pair order. `unstated` selects the `·u` rows. -/
def giveWayDeciders (D : SoftDoc) (P Q : SoftNode) : List String :=
  let dP := VE.SoftNorms.Wire.exceptionDecider D P
  let dQ := VE.SoftNorms.Wire.exceptionDecider D Q
  if dP == dQ then [dP] else [dP, dQ]

end VE.Defaults
