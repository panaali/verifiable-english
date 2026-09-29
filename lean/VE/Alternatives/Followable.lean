import VE.Alternatives.Route

/-! The followability check (docs/spec/alternatives.md 4.6, 7.1, 7.2).

`clearF` and `followableF` are formulas over `E_base`: the regulated outcomes
`O_p°` are W1's base-substituted outcomes of the inlined document
(`outcomeBase`), instantiated at the action or chooser by `inst`. `ClearIn` and
`FollowableIn` are the same conditions over a document expansion `S`
(regulated predicates read from `S`'s actual relations). `clear_denote` and
`followable_denote` relate the two on `S` and its base restriction (same
carrier); `followable_sound` is the FOLLOWABLE claim over the broader class,
`dilemma_witness_sound` the DILEMMA claim and `dilemma_expansion` its
expansion-level corollary. -/
namespace VE.Alternatives
open VE.Norms
universe u

/-! ## The formulas (context `[chooser, action].reverse`, evaluated at `tupleVal [r, a]`) -/

/-- `O_p°` of the inlined document. -/
def oBase (A : AltDoc) (n : String) : VE.Formula := outcomeBase (inlineTree A) n

/-- `[m] O_m°(a) ∧ [q] ∀a'. (available(a', r) ∧ O_q°(a') → a' = a)`. -/
def performedF (A : AltDoc) : VE.Formula :=
  match A.alt.performed with
  | none => .top
  | some (m, q) => .and (inst [.var 0] (oBase A m))
      (.all A.alt.action (.implies (.and (.binary A.alt.available (.var 0) (.var 2)) (inst [.var 0] (oBase A q)))
        (.eq (.var 0) (.var 1))))

/-- `∀x̄. O_o°(r, x̄) → F_o(a, x̄)` for one mapped obligation (arity 1 or 2, chooser first). -/
def fulfilF (A : AltDoc) (f : Fulfilment) : VE.Formula :=
  match findReg A.T f.obligation with
  | some ro => match ro.sorts.tail with
    | [] => .implies (inst [.var 1] (oBase A f.obligation)) (inst [.var 0] f.body)
    | [s] => .all s (.implies (inst [.var 0, .var 2] (oBase A f.obligation)) (inst [.var 0, .var 1] f.body))
    | _ => .top
  | none => .top

/-- 4.6, `clear°(r, a)`. -/
def clearF (A : AltDoc) : VE.Formula :=
  .and (.binary A.alt.available (.var 0) (.var 1)) (.and (performedF A) (allF (A.alt.fulfilments.map (fulfilF A))))

/-- 4.6, `followable°(r) := (∃a. available(a, r)) → ∃a. clear°(r, a)`, context `[chooser]`. -/
def followableF (A : AltDoc) : VE.Formula :=
  .implies (.ex A.alt.action (.binary A.alt.available (.var 0) (.var 1))) (.ex A.alt.action (clearF A))

def notFollowableF (A : AltDoc) : VE.Formula := .not (followableF A)
def allFollowable (A : AltDoc) : VE.Formula := bindAll [A.alt.chooser] (followableF A)

/-! ## The propositions over a document expansion -/

def TypedChooser (A : AltDoc) (S : VE.Structure.{u}) (r : S.Carrier) : Prop := S.domain A.alt.chooser r
def Avail (A : AltDoc) (S : VE.Structure.{u}) (a r : S.Carrier) : Prop := S.relation A.alt.available [a, r]

def ClearIn (A : AltDoc) (S : VE.Structure.{u}) (r a : S.Carrier) : Prop :=
  Avail A S a r ∧
  (∀ m q, A.alt.performed = some (m, q) →
     S.relation m [a] ∧ ∀ a', Avail A S a' r → S.relation q [a'] → a' = a) ∧
  (∀ f ∈ A.alt.fulfilments, ∀ xs, VE.TupleTyped S (restSorts A f) xs →
     S.relation f.obligation (r :: xs) → f.body.denote S (tupleVal (a :: xs)))

def FollowableIn (A : AltDoc) (S : VE.Structure.{u}) : Prop :=
  ∀ r, TypedChooser A S r → (∃ a, Avail A S a r) → ∃ a, ClearIn A S r a

/-! ## Helpers -/

theorem findReg_some {T : Tree} {n : String} {r : Regulated} (h : findReg T n = some r) :
    r ∈ T.regulated ∧ r.name = n :=
  ⟨List.mem_of_find?_eq_some h, by simpa using List.find?_some h⟩

theorem inst_var0_denote {S : VE.Structure.{u}} {E : VE.Environment} {φ : VE.Formula} {s : String}
    (hφ : φ.WellFormed E [s]) (x : S.Carrier) (ρ : VE.Valuation S) :
    (inst [.var 0] φ).denote S (x :: ρ) ↔ φ.denote S [x] :=
  inst_denote S E φ [s] [.var 0] (x :: ρ) [x] hφ rfl
    ⟨rfl, fun i h₁ _ => match i, h₁ with | 0, _ => rfl⟩

section Expansion
variable {A : AltDoc} (hv : AltValid A) {S : VE.Structure.{u}}
  (hS : DocumentExpansion (inlineTree A) (restrictAll (inlineTree A).T S) S)
include hv hS

theorem expansion_meanings : MeaningsBelow (inlineTree A) (size (inlineTree A)) S :=
  ((sat_document (valid_of_wellFormed _ hv.wf) S).mp hS.2.2).2.1

/-- In a document expansion, `O_p°` in the base restriction is the relation of `p`. -/
theorem oBase_relation {ro : Regulated} (hro : ro ∈ A.T.regulated) (vs : List S.Carrier)
    (hvs : VE.TupleTyped S ro.sorts vs) :
    (oBase A ro.name).denote (restrictAll (inlineTree A).T S) (tupleVal vs) ↔ S.relation ro.name vs := by
  have hvD := valid_of_wellFormed _ hv.wf
  obtain ⟨j, hj⟩ := mem_syms_index (hvD.regulated ro hro)
  have hjl : j < size (inlineTree A) := (List.getElem?_eq_some_iff.mp hj).1
  exact outcomeBase_relation hvD hj hjl S hS.2.1.1 (expansion_meanings hv hS) vs hvs

omit hS in
theorem oBase_wellFormed {ro : Regulated} (hro : ro ∈ A.T.regulated) :
    (oBase A ro.name).WellFormed (envAt (inlineTree A) 0) ro.sorts.reverse := by
  have hvD := valid_of_wellFormed _ hv.wf
  obtain ⟨j, hj⟩ := mem_syms_index (hvD.regulated ro hro)
  exact outcomeBase_wellFormed hvD hj

omit hv in
theorem expansion_relation_typed {p : String} {ss : List String} (hp : A.E.predicates p = some ss)
    {vs : List S.Carrier} (h : S.relation p vs) : VE.TupleTyped S ss vs := by
  obtain ⟨ss', hss', ht⟩ := hS.2.1.2 p vs h
  rw [envAt_size_predicates] at hss'
  change A.E.predicates p = some ss' at hss'
  rw [hp] at hss'
  cases hss'
  exact ht

omit hS in
theorem restrict_available (a r : S.Carrier) :
    (restrictAll (inlineTree A).T S).relation A.alt.available [a, r] ↔ Avail A S a r :=
  forget_relation S (available_not_layer hv) _

theorem performedF_denote (r a : S.Carrier) (ha : S.domain A.alt.action a) :
    (performedF A).denote (restrictAll (inlineTree A).T S) (tupleVal [r, a]) ↔
      ∀ m q, A.alt.performed = some (m, q) →
        S.relation m [a] ∧ ∀ a', Avail A S a' r → S.relation q [a'] → a' = a := by
  have hp := hv.performed
  unfold performedOk at hp
  unfold performedF
  cases hpf : A.alt.performed with
  | none => simp [VE.Formula.denote]
  | some mq =>
    obtain ⟨m, q⟩ := mq
    simp only [hpf] at hp
    cases hm : findReg A.T m with
    | none => simp [hm] at hp
    | some rm =>
      cases hq : findReg A.T q with
      | none => simp [hm, hq] at hp
      | some rq =>
        simp only [hm, hq, Bool.and_eq_true, beq_iff_eq] at hp
        obtain ⟨⟨⟨⟨_, hms⟩, _⟩, hqs⟩, _⟩ := hp
        obtain ⟨hmm, hmn⟩ := findReg_some hm
        obtain ⟨hqm, hqn⟩ := findReg_some hq
        have wm := oBase_wellFormed hv hmm
        have wq := oBase_wellFormed hv hqm
        rw [hms, hmn] at wm
        rw [hqs, hqn] at wq
        have em : ∀ x, S.domain A.alt.action x →
            ((oBase A m).denote (restrictAll (inlineTree A).T S) [x] ↔ S.relation m [x]) := by
          intro x hx
          have := oBase_relation hv hS hmm [x] (by rw [hms]; exact ⟨hx, trivial⟩)
          rw [hmn] at this
          exact this
        have eq : ∀ x, S.domain A.alt.action x →
            ((oBase A q).denote (restrictAll (inlineTree A).T S) [x] ↔ S.relation q [x]) := by
          intro x hx
          have := oBase_relation hv hS hqm [x] (by rw [hqs]; exact ⟨hx, trivial⟩)
          rw [hqn] at this
          exact this
        have key : (VE.Formula.and (inst [.var 0] (oBase A m))
            (.all A.alt.action (.implies (.and (.binary A.alt.available (.var 0) (.var 2))
              (inst [.var 0] (oBase A q))) (.eq (.var 0) (.var 1))))).denote
              (restrictAll (inlineTree A).T S) [a, r] ↔
            ((oBase A m).denote (restrictAll (inlineTree A).T S) [a] ∧
              ∀ v, S.domain A.alt.action v → Avail A S v r →
                (oBase A q).denote (restrictAll (inlineTree A).T S) [v] → v = a) := by
          simp only [VE.Formula.denote, VE.Term.denote, inst_var0_denote wm, inst_var0_denote wq]
          simp only [List.getElem?_cons_zero, List.getElem?_cons_succ, Option.some.injEq,
            exists_eq_left', restrict_available hv]
          constructor
          · rintro ⟨h1, h2⟩
            refine ⟨h1, fun v hv' hav hq' => ?_⟩
            obtain ⟨x, rfl, rfl⟩ := h2 v hv' ⟨⟨v, r, rfl, rfl, hav⟩, hq'⟩
            rfl
          · rintro ⟨h1, h2⟩
            refine ⟨h1, fun v hv' ⟨⟨x, y, hx, hy, hav⟩, hq'⟩ => ?_⟩
            cases hx; cases hy
            first
            | exact h2 v hv' hav hq'
            | exact (h2 v hv' hav hq').symm
        simp only [tupleVal, List.reverse_cons, List.reverse_nil, List.nil_append, List.cons_append]
        rw [key]
        constructor
        · rintro ⟨h1, h2⟩ m' q' he
          simp only [Option.some.injEq, Prod.mk.injEq] at he
          obtain ⟨rfl, rfl⟩ := he
          refine ⟨(em a ha).mp h1, fun a' hav hq' => ?_⟩
          have ht := expansion_relation_typed hS (E_available hv) hav
          exact h2 a' ht.1 hav ((eq a' ht.1).mpr hq')
        · intro h
          obtain ⟨h1, h2⟩ := h m q rfl
          exact ⟨(em a ha).mpr h1, fun v hv' hav hq' => h2 v hav ((eq v hv').mp hq')⟩

theorem fulfilF_denote {f : Fulfilment} (hf : f ∈ A.alt.fulfilments) (r a : S.Carrier)
    (hr : S.domain A.alt.chooser r) :
    (fulfilF A f).denote (restrictAll (inlineTree A).T S) [a, r] ↔
      ∀ xs, VE.TupleTyped S (restSorts A f) xs → S.relation f.obligation (r :: xs) →
        f.body.denote S (tupleVal (a :: xs)) := by
  have hok := hv.fulfil f hf
  unfold fulfilmentOk at hok
  unfold fulfilF restSorts
  cases hro : findReg A.T f.obligation with
  | none => simp [hro] at hok
  | some ro =>
    dsimp only
    simp only [hro, Bool.and_eq_true, beq_iff_eq, Bool.or_eq_true] at hok
    obtain ⟨⟨⟨⟨_, hhead⟩, hlen⟩, _⟩, hbody⟩ := hok
    obtain ⟨hmem, hname⟩ := findReg_some hro
    have wo := oBase_wellFormed hv hmem
    rw [hname] at wo
    have wb := (VE.check_iff_wellFormed _ _ _).mp hbody
    have eo := oBase_relation hv hS hmem
    rw [hname] at eo
    match hs : ro.sorts, hhead, hlen with
    | [c], hhead, _ =>
      simp only [List.head?_cons, Option.some.injEq] at hhead
      subst hhead
      rw [hs] at wb wo eo
      simp only [List.tail_cons, List.reverse_cons, List.reverse_nil, List.nil_append] at wb wo ⊢
      have e1 : (inst [.var 1] (oBase A f.obligation)).denote (restrictAll (inlineTree A).T S) [a, r] ↔
          S.relation f.obligation [r] := by
        rw [inst_denote (restrictAll (inlineTree A).T S) _ _ [A.alt.chooser] [.var 1] [a, r] [r] wo rfl
          ⟨rfl, fun i h₁ _ => match i, h₁ with | 0, _ => rfl⟩]
        exact eo [r] ⟨hr, trivial⟩
      have e2 : (inst [.var 0] f.body).denote (restrictAll (inlineTree A).T S) [a, r] ↔ f.body.denote S [a] := by
        rw [inst_var0_denote (S := restrictAll (inlineTree A).T S) wb a [r]]
        exact restrictAll_denote _ _ wb S [a]
      show ((inst [.var 1] (oBase A f.obligation)).denote (restrictAll (inlineTree A).T S) [a, r] →
        (inst [.var 0] f.body).denote (restrictAll (inlineTree A).T S) [a, r]) ↔ _
      rw [e1, e2]
      constructor
      · intro h xs hxs hrel
        match xs, hxs with
        | [], _ => exact h hrel
      · intro h hrel
        exact h [] trivial hrel
    | [c, s'], hhead, _ =>
      simp only [List.head?_cons, Option.some.injEq] at hhead
      subst hhead
      rw [hs] at wb wo eo
      simp only [List.tail_cons, List.reverse_cons, List.reverse_nil, List.nil_append,
        List.cons_append] at wb wo ⊢
      have e1 : ∀ x, S.domain s' x →
          ((inst [.var 0, .var 2] (oBase A f.obligation)).denote (restrictAll (inlineTree A).T S) [x, a, r] ↔
            S.relation f.obligation [r, x]) := by
        intro x hx
        rw [inst_denote (restrictAll (inlineTree A).T S) _ _ [s', A.alt.chooser] [.var 0, .var 2] [x, a, r] [x, r] wo rfl
          ⟨rfl, fun i h₁ _ => match i, h₁ with | 0, _ => rfl | 1, _ => rfl⟩]
        exact eo [r, x] ⟨hr, hx, trivial⟩
      have e2 : ∀ x, (inst [.var 0, .var 1] f.body).denote (restrictAll (inlineTree A).T S) [x, a, r] ↔
          f.body.denote S [x, a] := by
        intro x
        rw [inst_denote (restrictAll (inlineTree A).T S) _ _ [s', A.alt.action] [.var 0, .var 1] [x, a, r] [x, a] wb rfl
          ⟨rfl, fun i h₁ _ => match i, h₁ with | 0, _ => rfl | 1, _ => rfl⟩]
        exact restrictAll_denote _ _ wb S [x, a]
      show (∀ x, S.domain s' x →
        ((inst [.var 0, .var 2] (oBase A f.obligation)).denote (restrictAll (inlineTree A).T S) [x, a, r] →
          (inst [.var 0, .var 1] f.body).denote (restrictAll (inlineTree A).T S) [x, a, r])) ↔ _
      constructor
      · intro h xs hxs hrel
        match xs, hxs with
        | [x], ⟨hx, _⟩ =>
          exact (e2 x).mp (h x hx ((e1 x hx).mpr hrel))
      · intro h x hx hO
        exact (e2 x).mpr (h [x] ⟨hx, trivial⟩ ((e1 x hx).mp hO))

omit hS in
theorem availF_denote (a r : S.Carrier) :
    (VE.Formula.binary A.alt.available (.var 0) (.var 1)).denote (restrictAll (inlineTree A).T S) [a, r] ↔
      Avail A S a r := by
  simp only [VE.Formula.denote, VE.Term.denote, List.getElem?_cons_zero, List.getElem?_cons_succ,
    Option.some.injEq]
  constructor
  · rintro ⟨v, w, rfl, rfl, h⟩
    exact (restrict_available hv a r).mp h
  · intro h
    exact ⟨a, r, rfl, rfl, (restrict_available hv a r).mpr h⟩

theorem avail_typed {a r : S.Carrier} (h : Avail A S a r) : S.domain A.alt.action a ∧ S.domain A.alt.chooser r :=
  let t := expansion_relation_typed hS (E_available hv) h
  ⟨t.1, t.2.1⟩

/-- 4.6: the base formula `clear°` denotes `ClearIn` (carrier transport: `S` and its base
restriction share their carrier). -/
theorem clear_denote_of (r a : S.Carrier) (typed : VE.TupleTyped S [A.alt.chooser, A.alt.action] [r, a]) :
    (clearF A).denote (restrictAll (inlineTree A).T S) (tupleVal [r, a]) ↔ ClearIn A S r a := by
  obtain ⟨hr, ha, _⟩ := typed
  have hp := performedF_denote hv hS r a ha
  simp only [tupleVal, List.reverse_cons, List.reverse_nil, List.nil_append, List.cons_append] at hp
  show (VE.Formula.binary A.alt.available (.var 0) (.var 1)).denote (restrictAll (inlineTree A).T S) [a, r] ∧
    ((performedF A).denote (restrictAll (inlineTree A).T S) [a, r] ∧
      (allF (A.alt.fulfilments.map (fulfilF A))).denote (restrictAll (inlineTree A).T S) [a, r]) ↔ _
  rw [allF_denote, hp, availF_denote (S := S) hv]
  simp only [ClearIn, List.mem_map, forall_exists_index, and_imp, forall_apply_eq_imp_iff₂]
  refine and_congr Iff.rfl (and_congr Iff.rfl (forall_congr' fun f => imp_congr_right fun hf => ?_))
  exact fulfilF_denote hv hS hf r a hr

theorem followable_denote_of :
    (allFollowable A).denote (restrictAll (inlineTree A).T S) [] ↔ FollowableIn A S := by
  unfold allFollowable
  rw [bindAll_denote_nil]
  constructor
  · intro hall r hr ⟨a, hav⟩
    have hF := hall [r] ⟨hr, trivial⟩
    simp only [tupleVal, List.reverse_cons, List.reverse_nil, List.nil_append] at hF
    obtain ⟨a', ha', hc⟩ := hF ⟨a, (avail_typed hv hS hav).1, (availF_denote (S := S) hv a r).mpr hav⟩
    exact ⟨a', (clear_denote_of hv hS r a' ⟨hr, ha', trivial⟩).mp hc⟩
  · intro hF vs hvs
    match vs, hvs with
    | [r], ⟨hr, _⟩ =>
      simp only [tupleVal, List.reverse_cons, List.reverse_nil, List.nil_append]
      rintro ⟨a, _, hav⟩
      obtain ⟨a', hc⟩ := hF r hr ⟨a, (availF_denote (S := S) hv a r).mp hav⟩
      exact ⟨a', (avail_typed hv hS hc.1).1, (clear_denote_of hv hS r a' ⟨hr, (avail_typed hv hS hc.1).1, trivial⟩).mpr hc⟩

end Expansion

/-! ## The theorems (7.2) -/

/-- Membership of a finite model's sort domain. -/
def _root_.VE.FiniteModel.inDomain {α : Type u} (M : VE.FiniteModel α) (s : String) (v : α) : Prop :=
  v ∈ M.domains s

/-- 4.6: the base formulas denote the expansion-level propositions (via `subst_sound` and the
inlining), over the expansion `S` and its base restriction on the same carrier. -/
theorem clear_denote (A : AltDoc) (h : WellFormedAlt A = true) (S : VE.Structure.{u})
    (hS : DocumentExpansion (inlineTree A) (restrictAll (inlineTree A).T S) S)
    (hB : BaseAdmissibleAlt A (restrictAll (inlineTree A).T S))
    (r a : S.Carrier) (typed : VE.TupleTyped S [A.alt.chooser, A.alt.action] [r, a]) :
    (clearF A).denote (restrictAll (inlineTree A).T S) (tupleVal [r, a]) ↔ ClearIn A S r a := by
  have _ := hB
  exact clear_denote_of (altValid_of_wellFormed A h) hS r a typed

theorem followable_denote (A : AltDoc) (h : WellFormedAlt A = true) (S : VE.Structure.{u})
    (hS : DocumentExpansion (inlineTree A) (restrictAll (inlineTree A).T S) S)
    (hB : BaseAdmissibleAlt A (restrictAll (inlineTree A).T S)) :
    (allFollowable A).denote (restrictAll (inlineTree A).T S) [] ↔ FollowableIn A S := by
  have _ := hB
  exact followable_denote_of (altValid_of_wellFormed A h) hS

/-- FOLLOWABLE: the certified claim, over the broader class (4.2). -/
theorem followable_sound (A : AltDoc) (h : WellFormedAlt A = true) (hc : AltConflictFree.{u} A)
    (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (inlineTree A) 0) (backgroundBaseAlt A ++ A.Γ) (allFollowable A) c = true) :
    ∀ B : VE.Structure.{u}, BaseAdmissibleAlt A B → Sat B A.Γ →
      ∀ S, DocumentExpansion (inlineTree A) B S → FollowableIn A S := by
  have _ := hc
  intro B hB hΓ S hS
  have hden := VE.Tableau.checkCertificate_sound.{u} _ _ _ c ok B hB.1.1 (fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact sat_backgroundBaseAlt hB a ha
    · exact hΓ a ha)
  have hr := hS.1
  subst hr
  exact (followable_denote_of (altValid_of_wellFormed A h) hS).mp hden

/-- DILEMMA: a typed chooser of a valid finite witness at which `¬followable°` evaluates true
refutes the document-wide claim. The witness appears only as `M.asStructure` instantiating `B`. -/
theorem dilemma_witness_sound {α : Type u} [DecidableEq α] (A : AltDoc) (h : WellFormedAlt A = true)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (inlineTree A) 0)) (hb : backgroundValidAlt A M = true)
    (hΓ : A.Γ.all (fun p => p.eval M []) = true) (r : α) (typed : M.inDomain A.alt.chooser r)
    (hd : (notFollowableF A).eval M (tupleVal [r]) = true) :
    ¬ (∀ B : VE.Structure.{u}, BaseAdmissibleAlt A B → Sat B A.Γ → (allFollowable A).denote B []) := by
  have _ := h
  intro hall
  have hF := hall M.asStructure (baseAdmissibleAlt_of_valid A M valid hb)
    (fun a ha => (VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp hΓ a ha))
  have hF' := (bindAll_denote_nil _ _ _).mp hF [r] ⟨typed, trivial⟩
  exact ((VE.eval_iff_denote M _ _).mp hd) hF'

/-- The expansion-level corollary (carrier transport): on a document expansion `S` whose base
restriction satisfies the slot premises, a typed chooser at which `¬followable°` denotes true in
the restriction has no clear alternative in `S`. -/
theorem dilemma_expansion (A : AltDoc) (h : WellFormedAlt A = true) (S : VE.Structure.{u})
    (hS : DocumentExpansion (inlineTree A) (restrictAll (inlineTree A).T S) S)
    (hB : BaseAdmissibleAlt A (restrictAll (inlineTree A).T S))
    (r : S.Carrier) (typed : TypedChooser A S r)
    (hd : (notFollowableF A).denote (restrictAll (inlineTree A).T S) (tupleVal [r])) :
    ¬ ∃ a, ClearIn A S r a := by
  have _ := hB
  have hv := altValid_of_wellFormed A h
  rintro ⟨a, hc⟩
  have ha := (avail_typed hv hS hc.1).1
  apply hd
  intro _
  exact ⟨a, ha, (clear_denote_of hv hS r a ⟨typed, ha, trivial⟩).mpr hc⟩

/-- The finite evaluation of the followability formulas agrees with their denotation. -/
theorem followable_eval_iff_denote {α : Type u} [DecidableEq α] (A : AltDoc) (M : VE.FiniteModel α) (r : α) :
    (notFollowableF A).eval M (tupleVal [r]) = true ↔ (notFollowableF A).denote M.asStructure (tupleVal [r]) :=
  VE.eval_iff_denote M _ _

end VE.Alternatives
