import VE.Alternatives.Inline

/-! The Background slot `alternatives`, `BaseAdmissibleAlt`, the regenerated
`table_complete` premise, ownership, monotonicity, conservativity and the W1
conflict check over the extended background (docs/spec/alternatives.md 4.2,
4.4, 4.5, 4.9 and 7.2). -/
namespace VE.Alternatives
open VE.Norms
universe u

/-! ## The slot premises (4.2) -/

/-- `own: ∀a r r'. available(a, r) ∧ available(a, r') → r = r'`. -/
def ownPremise (A : AltEnv) : VE.Formula :=
  .all A.action (.all A.chooser (.all A.chooser
    (.implies (.and (.binary A.available (.var 2) (.var 1)) (.binary A.available (.var 2) (.var 0)))
      (.eq (.var 1) (.var 0)))))

/-- `∀r a a'. available(a, r) ∧ available(a', r) ∧ p(a) ∧ p(a') → a = a'`, for `taken` and `inaction`. -/
def oneOf (A : AltEnv) (p : String) : VE.Formula :=
  .all A.chooser (.all A.action (.all A.action
    (.implies (.and (.binary A.available (.var 1) (.var 2)) (.and (.binary A.available (.var 0) (.var 2))
        (.and (.unary p (.var 1)) (.unary p (.var 0)))))
      (.eq (.var 1) (.var 0)))))

def oneTakenPremise (A : AltEnv) : Option VE.Formula := A.taken.map (oneOf A)
def oneInactionPremise (A : AltEnv) : Option VE.Formula := A.inaction.map (oneOf A)

/-- `proximate: ∀a h. causes(a, h) → leads_to(a, h)`. -/
def proximatePremise (A : AltEnv) : Option VE.Formula :=
  A.proximate.map (fun p => .all A.action (.all A.harm
    (.implies (.binary p (.var 1) (.var 0)) (.binary A.leadsTo (.var 1) (.var 0)))))

/-- `own` then the declared optional premises, in 4.2 order. -/
def altPremises (A : AltDoc) : List VE.Formula :=
  ownPremise A.alt :: ((oneTakenPremise A.alt).toList ++ (oneInactionPremise A.alt).toList ++
    (proximatePremise A.alt).toList)

/-- The premise labels of `altPremises`, in the same order. -/
def altPremiseLabels (A : AltDoc) : List String :=
  "alternatives:own" :: ((oneTakenPremise A.alt).toList.map (fun _ => "alternatives:one_taken") ++
    (oneInactionPremise A.alt).toList.map (fun _ => "alternatives:one_inaction") ++
    (proximatePremise A.alt).toList.map (fun _ => "alternatives:proximate"))

/-- 4.4: `∀a h. leads_to(a, h) → ⋁ (a = c_a ∧ h = c_h)` over the document's positive cells
(`⊥` when there are none). -/
def tableComplete (A : AltDoc) (cells : List (String × String)) : VE.Formula :=
  .all A.alt.action (.all A.alt.harm (.implies (.binary A.alt.leadsTo (.var 1) (.var 0))
    (anyF (cells.map (fun c => .and (.eq (.var 1) (.const c.1)) (.eq (.var 0) (.const c.2)))))))

def backgroundBaseAlt (A : AltDoc) : List VE.Formula := backgroundBase (inlineTree A) ++ altPremises A
def backgroundAlt (A : AltDoc) : List VE.Formula := background (inlineTree A) ++ altPremises A

def BaseAdmissibleAlt (A : AltDoc) (B : VE.Structure.{u}) : Prop :=
  BaseAdmissible (inlineTree A) B ∧ Sat B (altPremises A)

def PrefixAdmissibleAlt (A : AltDoc) (k : Nat) (S : VE.Structure.{u}) : Prop :=
  PrefixAdmissible (inlineTree A) k S ∧ Sat (restrictAll (inlineTree A).T S) (altPremises A)

def AltConflictFree (A : AltDoc) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleAlt A B → ConflictFree (inlineTree A) B

/-! ## Typing of the slot premises -/

theorem ownPremise_denote (A : AltEnv) (S : VE.Structure.{u}) :
    (ownPremise A).denote S [] ↔ ∀ a, S.domain A.action a → ∀ r, S.domain A.chooser r →
      ∀ r', S.domain A.chooser r' → S.relation A.available [a, r] → S.relation A.available [a, r'] → r = r' := by
  simp only [ownPremise, VE.Formula.denote, VE.Term.denote]
  simp
  constructor <;> intro h a ha r hr r' hr' h1 h2 <;> exact (h a ha r hr r' hr' h1 h2).symm

theorem oneOf_denote (A : AltEnv) (p : String) (S : VE.Structure.{u}) :
    (oneOf A p).denote S [] ↔ ∀ r, S.domain A.chooser r → ∀ a, S.domain A.action a →
      ∀ a', S.domain A.action a' → S.relation A.available [a, r] → S.relation A.available [a', r] →
        S.relation p [a] → S.relation p [a'] → a = a' := by
  simp only [oneOf, VE.Formula.denote, VE.Term.denote]
  simp
  constructor <;> intro h r hr a ha a' ha' h1 h2 h3 h4 <;> exact (h r hr a ha a' ha' h1 h2 h3 h4).symm

theorem inlineTree_E (A : AltDoc) : (inlineTree A).E = A.E := rfl

section Typing
variable {A : AltDoc} (hv : AltValid A)
include hv

theorem ownPremise_wellFormed : (ownPremise A.alt).WellFormed (envAt (inlineTree A) 0) [] := by
  simp [ownPremise, VE.Formula.WellFormed, VE.Term.sortOf, base_available hv, envAt_sorts, inlineTree_E,
    hv.actionSort, hv.chooserSort]

theorem oneOf_wellFormed {p : String} (hp : (envAt (inlineTree A) 0).predicates p = some [A.alt.action]) :
    (oneOf A.alt p).WellFormed (envAt (inlineTree A) 0) [] := by
  simp [oneOf, VE.Formula.WellFormed, VE.Term.sortOf, base_available hv, hp, envAt_sorts, inlineTree_E,
    hv.actionSort, hv.chooserSort]

theorem altPremises_wellFormed : ∀ a ∈ altPremises A, a.WellFormed (envAt (inlineTree A) 0) [] := by
  intro a ha
  simp only [altPremises, List.mem_cons, List.mem_append, oneTakenPremise, oneInactionPremise,
    proximatePremise, Option.mem_toList, Option.map_eq_some_iff] at ha
  rcases ha with rfl | ((⟨p, hp, rfl⟩ | ⟨p, hp, rfl⟩) | ⟨p, hp, rfl⟩)
  · exact ownPremise_wellFormed hv
  · exact oneOf_wellFormed hv (base_taken hv hp)
  · exact oneOf_wellFormed hv (base_inaction hv hp)
  · simp [VE.Formula.WellFormed, VE.Term.sortOf, base_leadsTo hv, base_proximate hv hp, envAt_sorts,
      inlineTree_E, hv.actionSort, hv.harmSort]

theorem sat_altPremises_restrict (S : VE.Structure.{u}) :
    Sat (restrictAll (inlineTree A).T S) (altPremises A) ↔ Sat S (altPremises A) := by
  constructor
  · intro hs a ha
    exact (restrictAll_denote a [] (altPremises_wellFormed hv a ha) S []).mp (hs a ha)
  · intro hs a ha
    exact (restrictAll_denote a [] (altPremises_wellFormed hv a ha) S []).mpr (hs a ha)

end Typing

theorem sat_backgroundBaseAlt {A : AltDoc} {B : VE.Structure.{u}} (hB : BaseAdmissibleAlt A B) :
    Sat B (backgroundBaseAlt A) := by
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact hB.1.2 a ha
  · exact hB.2 a ha

/-- A true tuple of a base structure has its declared sorts. -/
theorem relation_typed {A : AltDoc} {B : VE.Structure.{u}} (hB : B.Admissible (envAt (inlineTree A) 0))
    {p : String} {ss : List String} (hp : (envAt (inlineTree A) 0).predicates p = some ss)
    {vs : List B.Carrier} (h : B.relation p vs) : VE.TupleTyped B ss vs := by
  obtain ⟨ss', hss', ht⟩ := hB.2 p vs h
  rw [hp] at hss'
  cases hss'
  exact ht

/-! ## Ownership (1.2) -/

/-- Under the slot premises an action's chooser is unique (`WellFormedAlt` gives the sorts of
`available`). -/
theorem owner_unique (A : AltDoc) (h : WellFormedAlt A = true) (B : VE.Structure.{u})
    (hB : BaseAdmissibleAlt A B) (a r r' : B.Carrier) :
    B.relation A.alt.available [a, r] → B.relation A.alt.available [a, r'] → r = r' := by
  have hv := altValid_of_wellFormed A h
  intro h1 h2
  have t1 := relation_typed hB.1.1 (base_available hv) h1
  have t2 := relation_typed hB.1.1 (base_available hv) h2
  exact (ownPremise_denote A.alt B).mp (hB.2 _ (List.mem_cons_self ..)) a t1.1 r t1.2.1 r' t2.2.1 h1 h2

/-! ## The profile words over a structure (4.3) -/

theorem avoidableF_denote (A : AltEnv) (S : VE.Structure.{u}) (h r : S.Carrier) :
    (avoidableF A).denote S (tupleVal [h, r]) ↔
      ∃ a, S.domain A.action a ∧ S.relation A.available [a, r] ∧ ¬ S.relation A.leadsTo [a, h] := by
  simp [avoidableF, tupleVal, VE.Formula.denote, VE.Term.denote]

theorem allowsF_denote (A : AltEnv) (S : VE.Structure.{u}) (a h : S.Carrier) :
    (allowsF A).denote S (tupleVal [a, h]) ↔ S.relation A.leadsTo [a, h] ∧
      ∃ r, S.domain A.chooser r ∧ S.relation A.available [a, r] ∧
        ∃ a', S.domain A.action a' ∧ S.relation A.available [a', r] ∧ ¬ S.relation A.leadsTo [a', h] := by
  simp [allowsF, tupleVal, VE.Formula.denote, VE.Term.denote]

theorem preventsF_denote (A : AltEnv) (S : VE.Structure.{u}) (a h : S.Carrier) :
    (preventsF A).denote S (tupleVal [a, h]) ↔ ¬ S.relation A.leadsTo [a, h] ∧
      ∃ r, S.domain A.chooser r ∧ S.relation A.available [a, r] ∧
        ∃ a', S.domain A.action a' ∧ S.relation A.available [a', r] ∧ S.relation A.leadsTo [a', h] := by
  simp [preventsF, tupleVal, VE.Formula.denote, VE.Term.denote]

theorem unavoidableF_denote (A : AltEnv) (S : VE.Structure.{u}) (h r : S.Carrier) :
    (unavoidableF A).denote S (tupleVal [h, r]) ↔
      (∃ a, S.domain A.action a ∧ S.relation A.available [a, r]) ∧ ¬ (avoidableF A).denote S (tupleVal [h, r]) := by
  simp [unavoidableF, tupleVal, VE.Formula.denote, VE.Term.denote]

/-! ## Monotonicity in the alternatives (7.2) -/

/-- Same carrier, domains, constants and every other relation; `available` extended by `more`. -/
def extendAvailable (A : AltEnv) (S : VE.Structure.{u}) (more : S.Carrier → S.Carrier → Prop) :
    VE.Structure.{u} :=
  { S with relation := fun p vs =>
      if p = A.available then S.relation p vs ∨ (match vs with | [a, r] => more a r | _ => False)
      else S.relation p vs }

/-- Adding available alternatives to `S` on the same carrier never removes avoidability, an
`allows` or a `prevents`. `WellFormedAlt` makes `available ≠ leads_to` (4.1(2)), so
`extendAvailable` leaves `leads_to` unchanged. Nothing is claimed for `clear`. -/
theorem alternative_monotone (A : AltDoc) (hw : WellFormedAlt A = true) (S : VE.Structure.{u})
    (more : S.Carrier → S.Carrier → Prop)
    (hS' : Sat (extendAvailable A.alt S more) (altPremises A)) (r h a : S.Carrier) :
    ((avoidableF A.alt).denote S (tupleVal [h, r]) →
        (avoidableF A.alt).denote (extendAvailable A.alt S more) (tupleVal [h, r])) ∧
      ((allowsF A.alt).denote S (tupleVal [a, h]) →
        (allowsF A.alt).denote (extendAvailable A.alt S more) (tupleVal [a, h])) ∧
      ((preventsF A.alt).denote S (tupleVal [a, h]) →
        (preventsF A.alt).denote (extendAvailable A.alt S more) (tupleVal [a, h])) := by
  have _ := hS'
  have hne : A.alt.leadsTo ≠ A.alt.available := fun he => available_ne_leadsTo (altValid_of_wellFormed A hw) he.symm
  have hav : ∀ x y, S.relation A.alt.available [x, y] →
      (extendAvailable A.alt S more).relation A.alt.available [x, y] := by
    intro x y hxy
    simp only [extendAvailable, if_true]
    exact Or.inl hxy
  have hlt : ∀ vs, (extendAvailable A.alt S more).relation A.alt.leadsTo vs ↔ S.relation A.alt.leadsTo vs := by
    intro vs
    simp [extendAvailable, hne]
  refine ⟨fun h1 => ?_, fun h1 => ?_, fun h1 => ?_⟩
  · obtain ⟨a', ha', h2, h3⟩ := (avoidableF_denote A.alt S h r).mp h1
    exact (avoidableF_denote A.alt (extendAvailable A.alt S more) h r).mpr
      ⟨a', ha', hav _ _ h2, by rw [hlt]; exact h3⟩
  · obtain ⟨h2, r', hr', h3, a', ha', h4, h5⟩ := (allowsF_denote A.alt S a h).mp h1
    exact (allowsF_denote A.alt (extendAvailable A.alt S more) a h).mpr ⟨(hlt _).mpr h2, r', hr', hav _ _ h3, a', ha', hav _ _ h4,
      by rw [hlt]; exact h5⟩
  · obtain ⟨h2, r', hr', h3, a', ha', h4, h5⟩ := (preventsF_denote A.alt S a h).mp h1
    exact (preventsF_denote A.alt (extendAvailable A.alt S more) a h).mpr ⟨by rw [hlt]; exact h2, r', hr', hav _ _ h3, a', ha',
      hav _ _ h4, (hlt _).mpr h5⟩

/-! ## Conservativity (4.9) -/

/-- The block's role predicates. -/
def roleNames (A : AltEnv) : List String :=
  [A.available, A.leadsTo] ++ A.inaction.toList ++ A.taken.toList ++ A.proximate.toList

/-- `E_base` minus `available`, `leads_to`, `inaction`, `taken`, `causes`. -/
def oldEnv (A : AltDoc) : VE.Environment := hide (envAt (inlineTree A) 0) (roleNames A.alt)

/-- Truth ignores the relations of predicates a formula does not mention. -/
theorem denote_forget_preds {ns : List String} (S : VE.Structure.{u}) :
    ∀ (a : VE.Formula) (ρ : VE.Valuation S), (∀ p ∈ preds a, p ∉ ns) →
      (a.denote (forget ns S) ρ ↔ a.denote S ρ)
  | .top, _, _ | .bottom, _, _ => Iff.rfl
  | .eq _ _, _, _ => Iff.rfl
  | .unary p t, ρ, h => by
    have : p ∉ ns := h p (by simp [preds])
    simp [VE.Formula.denote, forget, this, VE.Term.denote]
  | .binary p t w, ρ, h => by
    have : p ∉ ns := h p (by simp [preds])
    simp [VE.Formula.denote, forget, this, VE.Term.denote]
  | .not a, ρ, h => not_congr (denote_forget_preds S a ρ h)
  | .and a b, ρ, h => and_congr (denote_forget_preds S a ρ fun p hp => h p (List.mem_append_left _ hp))
      (denote_forget_preds S b ρ fun p hp => h p (List.mem_append_right _ hp))
  | .or a b, ρ, h => or_congr (denote_forget_preds S a ρ fun p hp => h p (List.mem_append_left _ hp))
      (denote_forget_preds S b ρ fun p hp => h p (List.mem_append_right _ hp))
  | .implies a b, ρ, h => imp_congr (denote_forget_preds S a ρ fun p hp => h p (List.mem_append_left _ hp))
      (denote_forget_preds S b ρ fun p hp => h p (List.mem_append_right _ hp))
  | .all s a, ρ, h => forall_congr' fun v => imp_congr_right fun _ => denote_forget_preds S a (v :: ρ) h
  | .ex s a, ρ, h => exists_congr fun v => and_congr_right fun _ => denote_forget_preds S a (v :: ρ) h

/-- The emptied relations of the conservativity expansion. -/
def emptied (A : AltEnv) : List String :=
  [A.available] ++ A.inaction.toList ++ A.taken.toList ++ A.proximate.toList

theorem emptied_sub (A : AltEnv) : ∀ p ∈ emptied A, p ∈ roleNames A := by
  intro p hp
  simp only [emptied, roleNames, List.mem_append, List.mem_cons, List.not_mem_nil, or_false] at hp ⊢
  rcases hp with ((h | h) | h) | h
  · exact Or.inl (Or.inl (Or.inl (Or.inl h)))
  · exact Or.inl (Or.inl (Or.inr h))
  · exact Or.inl (Or.inr h)
  · exact Or.inr h

theorem oldEnv_preds {A : AltDoc} {a : VE.Formula} (ha : a.WellFormed (oldEnv A) []) :
    ∀ p ∈ preds a, p ∉ emptied A.alt := by
  intro p hp he
  have := wf_preds ha p hp
  simp [oldEnv, hide, emptied_sub A.alt p he] at this

theorem literals_preds (lits : List String) : ∀ a ∈ VE.Route.Background.literals lits, preds a = [] := by
  intro a ha
  simp only [VE.Route.Background.literals, List.mem_map] at ha
  obtain ⟨_, _, rfl⟩ := ha
  rfl

/-- For formulas that mention none of the block's role predicates, the slot premises add no
consequence (the empty-relation expansion). -/
theorem alternatives_conservative (A : AltDoc) (h : WellFormedAlt A = true) (Γ : List VE.Formula)
    (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (oldEnv A) []) (hφ : φ.WellFormed (oldEnv A) []) :
    (∀ B : VE.Structure.{u}, BaseAdmissibleAlt A B → Sat B Γ → φ.denote B []) ↔
      (∀ B : VE.Structure.{u}, BaseAdmissible (inlineTree A) B → Sat B Γ → φ.denote B []) := by
  have _ := h
  constructor
  · intro hall B hB hs
    let B' := forget (emptied A.alt) B
    have hadm : B'.Admissible (envAt (inlineTree A) 0) :=
      ⟨hB.1.1, fun p vs hp => by
        obtain ⟨ss, hss, ht⟩ := hB.1.2 p vs hp.2
        exact ⟨ss, hss, (tupleTyped_forget _ B ss vs).mpr ht⟩⟩
    have hlit : Sat B' (backgroundBase (inlineTree A)) := fun a ha =>
      (denote_forget_preds B a [] (by
        intro p hp; rw [literals_preds _ a ha] at hp; cases hp)).mpr (hB.2 a ha)
    have hav : ∀ vs, ¬ B'.relation A.alt.available vs := fun vs hr =>
      hr.1 (by simp [emptied])
    have hslot : Sat B' (altPremises A) := by
      intro a ha
      simp only [altPremises, List.mem_cons, List.mem_append, oneTakenPremise, oneInactionPremise,
        proximatePremise, Option.mem_toList, Option.map_eq_some_iff] at ha
      rcases ha with rfl | ((⟨p, _, rfl⟩ | ⟨p, _, rfl⟩) | ⟨p, hp, rfl⟩)
      · exact (ownPremise_denote A.alt B').mpr fun _ _ _ _ _ _ h1 => absurd h1 (hav _)
      · exact (oneOf_denote A.alt p B').mpr fun _ _ _ _ _ _ h1 => absurd h1 (hav _)
      · exact (oneOf_denote A.alt p B').mpr fun _ _ _ _ _ _ h1 => absurd h1 (hav _)
      · have hne : ∀ vs, ¬ B'.relation p vs := fun vs hr => hr.1 (by simp [emptied, hp])
        simp only [VE.Formula.denote]
        intro _ _ _ _ ⟨_, _, _, _, hr⟩
        exact absurd hr (hne _)
    have hs' : Sat B' Γ := fun a ha =>
      (denote_forget_preds B a [] (oldEnv_preds (hΓ a ha))).mpr (hs a ha)
    exact (denote_forget_preds B φ [] (oldEnv_preds hφ)).mp (hall B' ⟨⟨hadm, hlit⟩, hslot⟩ hs')
  · intro hall B hB hs
    exact hall B hB.1 hs

/-! ## The conflict check over the extended background (4.5) -/

/-- One target's certificate is accepted over `Background_baseAlt`, or over W1's `Background_base`
alone (fewer premises, 4.5). -/
def targetAccepted (A : AltDoc) (t : String × List String × VE.Formula) (c : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (envAt (inlineTree A) 0) (backgroundBaseAlt A) (targetConclusion t) c ||
    VE.Tableau.checkCertificate (envAt (inlineTree A) 0) (backgroundBase (inlineTree A)) (targetConclusion t) c

/-- W1's `conflictFreeCheck` on the inlined document with `Background_baseAlt`. -/
def altConflictFreeCheck (A : AltDoc) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (targets (inlineTree A)).length == certs.length &&
    ((targets (inlineTree A)).zip certs).all (fun (t, c) => match c with
      | some c => targetAccepted A t c
      | none => false)

theorem altConflictFreeCheck_target {A : AltDoc} {certs : List (Option VE.Tableau.Certificate)}
    (hc : altConflictFreeCheck A certs = true) {t : String × List String × VE.Formula}
    (ht : t ∈ targets (inlineTree A)) : ∃ c, targetAccepted A t c = true := by
  simp only [altConflictFreeCheck, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
  obtain ⟨hl, hall⟩ := hc
  obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp ht
  have hlt : i < (targets (inlineTree A)).length := (List.getElem?_eq_some_iff.mp hi).1
  have hlt' : i < certs.length := hl ▸ hlt
  have hmem : (t, certs[i]) ∈ (targets (inlineTree A)).zip certs := by
    apply List.mem_iff_getElem?.mpr
    refine ⟨i, ?_⟩
    rw [List.getElem?_zip_eq_some]
    exact ⟨hi, List.getElem?_eq_getElem hlt'⟩
  have := hall _ hmem
  cases hci : certs[i] with
  | none => rw [hci] at this; cases this
  | some c => rw [hci] at this; exact ⟨c, this⟩

/-- 4.5: W1's conflict machinery over the extended background. -/
theorem alt_conflict_free (A : AltDoc) (h : WellFormedAlt A = true)
    (certs : List (Option VE.Tableau.Certificate)) (hc : altConflictFreeCheck A certs = true) :
    AltConflictFree.{u} A := by
  have hv := valid_of_wellFormed _ (alternatives_wellFormed A h)
  intro B hB
  have cert : ∀ t ∈ targets (inlineTree A), ∀ vs, VE.TupleTyped B t.2.1 vs →
      ¬ t.2.2.denote B (tupleVal vs) := by
    intro t ht vs hvs
    obtain ⟨c, hcc⟩ := altConflictFreeCheck_target hc ht
    have he : (targetConclusion t).denote B [] := by
      rcases Bool.or_eq_true_iff.mp hcc with hcc | hcc
      · exact VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc B hB.1.1 (sat_backgroundBaseAlt hB)
      · exact VE.Tableau.checkCertificate_sound.{u} _ _ _ c hcc B hB.1.1 hB.1.2
    exact (bindAll_denote_nil B _ _).mp he vs hvs
  refine ⟨fun r hr vs hvs => ?_, fun pr hpr vs hvs => ?_⟩
  · exact cert (r.name, r.sorts, conflict (inlineTree A) r)
      (List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)) vs hvs
  · exact cert (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflict (inlineTree A) pr)
      (List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs hvs

/-- W1's `backgroundValid` on the inlined document and the finite evaluation of the slot premises. -/
def backgroundValidAlt {α : Type u} [DecidableEq α] (A : AltDoc) (M : VE.FiniteModel α) : Bool :=
  backgroundValid (inlineTree A) M && (altPremises A).all (fun p => p.eval M [])

theorem baseAdmissibleAlt_of_valid {α : Type u} [DecidableEq α] (A : AltDoc) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (inlineTree A) 0)) (hb : backgroundValidAlt A M = true) :
    BaseAdmissibleAlt A M.asStructure := by
  simp only [backgroundValidAlt, Bool.and_eq_true, List.all_eq_true] at hb
  exact ⟨baseAdmissible_of_valid _ M valid hb.1, fun a ha => (VE.eval_iff_denote M [] a).mp (hb.2 a ha)⟩

/-- A typed finite base witness passing the extended Background check refutes conflict-freedom
there, unique expansion there and `AltConflictFree`. -/
theorem alt_conflict_witness_sound {α : Type u} [DecidableEq α] (A : AltDoc) (h : WellFormedAlt A = true)
    (t : String × List String × VE.Formula) (ht : t ∈ VE.Norms.targets (inlineTree A))
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (inlineTree A) 0)) (hb : backgroundValidAlt A M = true)
    (vs : List α) (typed : VE.TupleTyped M.asStructure t.2.1 vs) (hw : t.2.2.eval M (tupleVal vs) = true) :
    ¬ ConflictFree (inlineTree A) M.asStructure ∧ ¬ VE.Route.Unique (DocumentExpansion (inlineTree A) M.asStructure) ∧
      ¬ AltConflictFree.{u} A := by
  have hB := baseAdmissibleAlt_of_valid A M valid hb
  obtain ⟨hn, hu, _⟩ := Replay.target_refutes (inlineTree A) (alternatives_wellFormed A h) t ht
    M.asStructure hB.1 vs typed ((VE.eval_iff_denote M _ _).mp hw)
  exact ⟨hn, hu, fun hc => hn (hc _ hB)⟩

end VE.Alternatives
