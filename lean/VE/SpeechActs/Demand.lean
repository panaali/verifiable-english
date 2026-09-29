import VE.SpeechActs.Tree

/-! Commands (docs/spec/speech-acts.md 4.2, 4.3 and 8.2): the shape and polarity
of every elaborated command rule, faithfulness of its equality guard to the
direct reading "the rule applies exactly at the bound tuple when the guard
holds", its normative contribution through W1's elaboration, the opposite case
(the local elaboration incompatibility, and a W1 base conflict under W1's
`AgreesBelow`), and the one addressee of the scope. -/
namespace VE.SpeechActs
open VE.Norms (Regulated Role Node Tree Doc WellFormed Valid elaborate elabPremise AppliesD SelectsD DecidesD
  tupleVal Sat AgreesBelow before ConflictFree restrictAll envAt size preds syms layerNames rulesOn children
  valid_of_wellFormed Sym)
universe u

/-! ## Formula helpers -/

theorem conj_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    ∀ l : List VE.Formula, (conj l).denote S ρ ↔ ∀ a ∈ l, a.denote S ρ
  | [] => by simp [conj, VE.Formula.denote]
  | [a] => by simp [conj]
  | a :: b :: rest => by
    have ih := conj_denote S ρ (b :: rest)
    simp only [conj] at ih ⊢
    simp only [VE.Formula.denote, ih, List.mem_cons, forall_eq_or_imp]

theorem conj_wellFormed (E : VE.Environment) (Γ : List String) :
    ∀ l : List VE.Formula, (∀ a ∈ l, a.WellFormed E Γ) → (conj l).WellFormed E Γ
  | [], _ => trivial
  | [a], h => by simpa [conj] using h
  | a :: b :: rest, h => by
    have ih := conj_wellFormed E Γ (b :: rest) (fun x hx => h x (List.mem_cons_of_mem _ hx))
    simp only [conj] at ih ⊢
    exact ⟨h a List.mem_cons_self, ih⟩

theorem preds_conj : ∀ l : List VE.Formula, (∀ a ∈ l, preds a = []) → preds (conj l) = []
  | [], _ => rfl
  | [a], h => by simpa [conj] using h
  | a :: b :: rest, h => by
    have ih := preds_conj (b :: rest) (fun x hx => h x (List.mem_cons_of_mem _ hx))
    simp only [conj] at ih ⊢
    simp [preds, h a List.mem_cons_self, ih]

theorem preds_eqsFrom : ∀ (k : Nat) (names : List String), ∀ a ∈ eqsFrom k names, preds a = []
  | _, [] => by simp [eqsFrom]
  | k, n :: ns => by
    intro a ha
    simp only [eqsFrom, List.mem_cons] at ha
    rcases ha with rfl | ha
    · rfl
    · exact preds_eqsFrom (k - 1) ns a ha

theorem constsOf_cons (S : VE.Structure.{u}) (a : String) (as : List String) (v : S.Carrier)
    (vs : List S.Carrier) : constsOf S (a :: as) = some (v :: vs) ↔
      S.constant a = some v ∧ constsOf S as = some vs := by
  simp only [constsOf]
  cases S.constant a <;> cases constsOf S as <;> simp

theorem constsOf_length (S : VE.Structure.{u}) :
    ∀ (names : List String) (vs : List S.Carrier), constsOf S names = some vs → vs.length = names.length
  | [], vs, h => by simp [constsOf] at h; subst h; rfl
  | a :: as, vs, h => by
    simp only [constsOf] at h
    cases ha : S.constant a <;> cases hs : constsOf S as <;> simp [ha, hs] at h
    subst h
    simp [constsOf_length S as _ hs]

/-- The equalities of `eqsFrom k names` hold under `ρ` exactly when the names denote the tuple `vs`, when
`ρ[k - i]` is `vs[i]` for every slot. -/
theorem eqsFrom_denote (S : VE.Structure.{u}) :
    ∀ (names : List String) (vs : List S.Carrier) (k : Nat) (ρ : VE.Valuation S),
      names.length = vs.length → (∀ i, i < names.length → ρ[k - i]? = vs[i]?) →
      ((∀ a ∈ eqsFrom k names, a.denote S ρ) ↔ constsOf S names = some vs)
  | [], vs, _, _, hl, _ => by
    match vs, hl with
    | [], _ => simp [eqsFrom, constsOf]
  | n :: ns, vs, k, ρ, hl, hi => by
    match vs, hl with
    | v :: ws, hl =>
      have hl' : ns.length = ws.length := by simpa using hl
      have h0 : ρ[k]? = some v := by simpa using hi 0 (by simp)
      have hrest : ∀ i, i < ns.length → ρ[k - 1 - i]? = ws[i]? := by
        intro i hlt
        have := hi (i + 1) (by simp; omega)
        rw [show k - (i + 1) = k - 1 - i by omega] at this
        simpa using this
      rw [constsOf_cons, ← eqsFrom_denote S ns ws (k - 1) ρ hl' hrest]
      simp only [eqsFrom, List.mem_cons, forall_eq_or_imp, VE.Formula.denote, VE.Term.denote, h0]
      constructor
      · rintro ⟨⟨x, hx, hc⟩, hr⟩
        cases hx
        exact ⟨hc, hr⟩
      · rintro ⟨hc, hr⟩
        exact ⟨⟨v, rfl, hc⟩, hr⟩

/-- A closed typed formula has the same truth under every valuation. -/
theorem denote_agree (S : VE.Structure.{u}) (E : VE.Environment) (a : VE.Formula) :
    ∀ (Γ : List String) (ρ₁ ρ₂ : VE.Valuation S), a.WellFormed E Γ →
      (∀ i, i < Γ.length → ρ₁[i]? = ρ₂[i]?) → (a.denote S ρ₁ ↔ a.denote S ρ₂) := by
  have term : ∀ (Γ : List String) (ρ₁ ρ₂ : VE.Valuation S) (t : VE.Term) (s : String),
      t.sortOf E Γ = some s → (∀ i, i < Γ.length → ρ₁[i]? = ρ₂[i]?) → t.denote S ρ₁ = t.denote S ρ₂ := by
    intro Γ ρ₁ ρ₂ t s ht hag
    cases t with
    | const c => rfl
    | var i => exact hag i (List.getElem?_eq_some_iff.mp ht).1
  induction a with
  | top | bottom => intros; simp [VE.Formula.denote]
  | unary p t =>
    intro Γ ρ₁ ρ₂ ⟨s, _, ht⟩ hag
    simp only [VE.Formula.denote, term Γ ρ₁ ρ₂ t s ht hag]
  | binary p t w =>
    intro Γ ρ₁ ρ₂ ⟨s, s', _, ht, hw⟩ hag
    simp only [VE.Formula.denote, term Γ ρ₁ ρ₂ t s ht hag, term Γ ρ₁ ρ₂ w s' hw hag]
  | eq t w =>
    intro Γ ρ₁ ρ₂ ⟨s, ht, hw⟩ hag
    simp only [VE.Formula.denote, term Γ ρ₁ ρ₂ t s ht hag, term Γ ρ₁ ρ₂ w s hw hag]
  | not a ih =>
    intro Γ ρ₁ ρ₂ hw hag
    simp only [VE.Formula.denote]; rw [ih Γ ρ₁ ρ₂ hw hag]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    intro Γ ρ₁ ρ₂ hw hag
    simp only [VE.Formula.denote]; rw [ia Γ ρ₁ ρ₂ hw.1 hag, ib Γ ρ₁ ρ₂ hw.2 hag]
  | all s a ih | ex s a ih =>
    intro Γ ρ₁ ρ₂ hw hag
    have key : ∀ v, a.denote S (v :: ρ₁) ↔ a.denote S (v :: ρ₂) := fun v =>
      ih (s :: Γ) _ _ hw.2 (fun i hi => by
        cases i with
        | zero => rfl
        | succ i => simpa using hag i (by simpa using hi))
    simp only [VE.Formula.denote]
    first
    | exact forall_congr' fun v => imp_congr_right fun _ => key v
    | exact exists_congr fun v => and_congr_right fun _ => key v

theorem denote_closed (S : VE.Structure.{u}) (E : VE.Environment) (a : VE.Formula) (h : a.WellFormed E [])
    (ρ : VE.Valuation S) : a.denote S ρ ↔ a.denote S [] :=
  denote_agree S E a [] ρ [] h (fun _ hi => absurd hi (Nat.not_lt_zero _))

/-- Typing is stable under extending the context. -/
theorem wellFormed_append (E : VE.Environment) (a : VE.Formula) :
    ∀ (Γ Δ : List String), a.WellFormed E Γ → a.WellFormed E (Γ ++ Δ) := by
  have term : ∀ (Γ Δ : List String) (t : VE.Term) (s : String),
      t.sortOf E Γ = some s → t.sortOf E (Γ ++ Δ) = some s := by
    intro Γ Δ t s ht
    cases t with
    | const c => exact ht
    | var i =>
      simp only [VE.Term.sortOf] at ht ⊢
      rw [List.getElem?_append_left (List.getElem?_eq_some_iff.mp ht).1]
      exact ht
  induction a with
  | top | bottom => intros; trivial
  | unary p t => intro Γ Δ ⟨s, hp, ht⟩; exact ⟨s, hp, term Γ Δ t s ht⟩
  | binary p t w => intro Γ Δ ⟨s, s', hp, ht, hw⟩; exact ⟨s, s', hp, term Γ Δ t s ht, term Γ Δ w s' hw⟩
  | eq t w => intro Γ Δ ⟨s, ht, hw⟩; exact ⟨s, term Γ Δ t s ht, term Γ Δ w s hw⟩
  | not a ih => intro Γ Δ h; exact ih Γ Δ h
  | and a b ia ib | or a b ia ib | implies a b ia ib => intro Γ Δ h; exact ⟨ia Γ Δ h.1, ib Γ Δ h.2⟩
  | all s a ih | ex s a ih => intro Γ Δ h; exact ⟨h.1, ih (s :: Γ) Δ h.2⟩

/-- `eqsFrom k names` is typed in `Γ` when `Γ[k - i]` is the sort of the `i`-th name. -/
theorem eqsFrom_wellFormed (E : VE.Environment) :
    ∀ (names sorts : List String) (k : Nat) (Γ : List String), constsTyped E names sorts = true →
      (∀ i, i < names.length → Γ[k - i]? = sorts[i]?) → ∀ a ∈ eqsFrom k names, a.WellFormed E Γ
  | [], _, _, _, _, _ => by simp [eqsFrom]
  | n :: ns, [], _, _, h, _ => by simp [constsTyped] at h
  | n :: ns, s :: ss, k, Γ, h, hi => by
    simp only [constsTyped, Bool.and_eq_true, beq_iff_eq] at h
    intro a ha
    simp only [eqsFrom, List.mem_cons] at ha
    rcases ha with rfl | ha
    · exact ⟨s, by simpa using hi 0 (by simp), h.1⟩
    · refine eqsFrom_wellFormed E ns ss (k - 1) Γ h.2 (fun i hlt => ?_) a ha
      have := hi (i + 1) (by simp; omega)
      rw [show k - (i + 1) = k - 1 - i by omega] at this
      simpa using this

theorem constsTyped_length (E : VE.Environment) :
    ∀ (names sorts : List String), constsTyped E names sorts = true → names.length = sorts.length
  | [], [], _ => rfl
  | _ :: as, _ :: ss, h => by
    simp only [constsTyped, Bool.and_eq_true] at h
    simp [constsTyped_length E as ss h.2]
  | [], _ :: _, h | _ :: _, [], h => by simp [constsTyped] at h

/-! ## The facts a command of a well-formed document carries -/

theorem regOf_spec {D : SpeechDoc} {p : String} {r : Regulated} (h : regOf D p = some r) :
    r ∈ D.regulated ∧ r.name = p := by
  unfold regOf at h
  exact ⟨List.mem_of_find?_eq_some h, by simpa using List.find?_some h⟩

/-- What `commandOk` gives for a command of a well-formed document. -/
theorem command_facts {D : SpeechDoc} (h : WellFormedSpeech D = true) {c : Command} (hc : c ∈ D.commands) :
    ∃ r s you, regOf D c.act = some r ∧ D.scope.addressee = some (s, you) ∧
      r.role = (if c.force = .require then Role.obligation else Role.permission) ∧
      D.E.predicates c.act = some r.sorts ∧ r.sorts.head? = some s ∧
      constsTyped D.E (you :: c.args) r.sorts = true ∧ c.guard.WellFormed D.E [] := by
  have hv := validSpeech_of_wellFormed D h
  have hk := hv.commands c hc
  unfold commandOk at hk
  split at hk
  · rename_i r s you hr ha
    simp only [Bool.and_eq_true, beq_iff_eq] at hk
    obtain ⟨⟨⟨⟨hrole, hp⟩, hs⟩, ht⟩, hg⟩ := hk
    exact ⟨r, s, you, hr, ha, hrole, hp, hs, ht, (VE.check_iff_wellFormed _ _ _).mp hg⟩
  · cases hk

theorem addresseeConst_eq {D : SpeechDoc} {s you : String} (h : D.scope.addressee = some (s, you)) :
    addresseeConst D = some you := by
  simp [addresseeConst, h]

theorem actSorts_eq {D : SpeechDoc} {c : Command} {ss : List String} (h : D.E.predicates c.act = some ss) :
    actSorts D c = ss := by
  simp [actSorts, h]

theorem policy_nodes (D : SpeechDoc) : (policy D).T.nodes = D.norms ++ D.commands.map (demand D) := rfl
theorem policy_E (D : SpeechDoc) : (policy D).E = D.E := rfl
theorem policy_regulated (D : SpeechDoc) : (policy D).T.regulated = D.regulated := rfl

/-- The equality guard, read at the valuation of a tuple of the right length, says exactly that the tuple is
the bound one. -/
theorem eqGuard_denote {D : SpeechDoc} {c : Command} {you : String} (hy : addresseeConst D = some you)
    (S : VE.Structure.{u}) (vs : List S.Carrier) (hl : vs.length = c.args.length + 1) :
    (eqGuard D c).denote S (tupleVal vs) ↔ boundTuple D c S = some vs := by
  have hsc : slotConsts D c = you :: c.args := by simp [slotConsts, hy]
  rw [eqGuard, conj_denote, hsc, eqsFrom_denote S (you :: c.args) vs c.args.length (tupleVal vs)
    (by simp [hl]) ?_]
  · simp [boundTuple, hy]
  · intro i hi
    simp only [List.length_cons] at hi
    simp only [tupleVal]
    rw [List.getElem?_reverse (by omega)]
    congr 1
    omega

/-! ## 8.2 -/

/-- 4.1 ⇒ W1 well-formedness of the regenerated policy. -/
theorem policy_wellFormed (D : SpeechDoc) (h : WellFormedSpeech D = true) : WellFormed (policy D) = true :=
  (validSpeech_of_wellFormed D h).policy

/-- The shape of every command rule: consequence over the situation variables, equality guard, no carve-outs, no edges. -/
theorem demand_shape (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands) :
    (demand D c).carveOuts = [] ∧ (demand D c).over = [] ∧ (demand D c).pred = c.act ∧
    ((demand D c).guard.WellFormed D.E (actSorts D c).reverse) := by
  obtain ⟨r, s, you, _, ha, _, hp, _, ht, hg⟩ := command_facts h hc
  refine ⟨rfl, rfl, rfl, ?_, ?_⟩
  · apply conj_wellFormed
    have hsc : slotConsts D c = you :: c.args := by simp [slotConsts, addresseeConst_eq ha]
    rw [hsc]
    have hlen : c.args.length + 1 = r.sorts.length := by simpa using constsTyped_length D.E _ _ ht
    refine eqsFrom_wellFormed D.E (you :: c.args) r.sorts c.args.length _ ht ?_
    intro i hi
    simp only [List.length_cons] at hi
    rw [actSorts_eq hp, List.getElem?_reverse (by omega)]
    congr 1
    omega
  · simpa using wellFormed_append D.E c.guard [] (actSorts D c).reverse hg

/-- Polarity: require realises the obligation role with sign +, forbid the permission role with sign −. -/
theorem demand_polarity (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands) :
    (c.force = .require → (demand D c).sign = true  ∧ ∃ r, regOf D c.act = some r ∧ r.role = .obligation) ∧
    (c.force = .forbid  → (demand D c).sign = false ∧ ∃ r, regOf D c.act = some r ∧ r.role = .permission) := by
  obtain ⟨r, _, _, hr, _, hrole, _⟩ := command_facts h hc
  refine ⟨fun hf => ⟨by simp [demand, hf], r, hr, by simpa [hf] using hrole⟩,
    fun hf => ⟨by simp [demand, hf], r, hr, by simpa [hf] using hrole⟩⟩

theorem typed_length {D : SpeechDoc} (h : WellFormedSpeech D = true) {c : Command} (hc : c ∈ D.commands)
    {S : VE.Structure.{u}} {vs : List S.Carrier} (typed : VE.TupleTyped S (actSorts D c) vs) :
    vs.length = c.args.length + 1 := by
  obtain ⟨r, s, you, _, _, _, hp, _, ht, _⟩ := command_facts h hc
  rw [VE.Norms.tupleTyped_length typed, actSorts_eq hp, ← constsTyped_length D.E _ _ ht]
  rfl

/-- 4.3, faithfulness of the elaborated guard to the direct reading: the rule applies exactly at the bound tuple when
    the guard holds. -/
theorem demand_applies (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands)
    (S : VE.Structure) (hS : S.Admissible (En D)) (vs : List S.Carrier)
    (typed : VE.TupleTyped S (actSorts D c) vs) :
    AppliesD S (tupleVal vs) (demand D c) ↔ (boundTuple D c S = some vs ∧ c.guard.denote S []) := by
  obtain ⟨r, s, you, _, ha, _, _, _, _, hg⟩ := command_facts h hc
  simp only [AppliesD, demand, VE.Formula.denote, List.not_mem_nil, false_and, exists_false, not_false_eq_true,
    and_true]
  rw [eqGuard_denote (addresseeConst_eq ha) S vs (typed_length h hc typed), denote_closed S D.E c.guard hg]

theorem demand_mem (D : SpeechDoc) {c : Command} (hc : c ∈ D.commands) : demand D c ∈ (policy D).T.nodes := by
  rw [policy_nodes]
  exact List.mem_append_right _ (List.mem_map_of_mem hc)

/-- No rule takes precedence over a command rule. -/
theorem demand_children (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands) :
    children (policy D).T (demand D c) = [] := by
  have hv := validSpeech_of_wellFormed D h
  apply List.eq_nil_iff_forall_not_mem.mpr
  intro C hC
  obtain ⟨hC, _, hn⟩ := VE.Norms.mem_children_iff.mp hC
  rw [policy_nodes] at hC
  rcases List.mem_append.mp hC with hC | hC
  · exact hv.noOver C hC c hc hn
  · obtain ⟨c', _, rfl⟩ := List.mem_map.mp hC
    simp [demand] at hn

/-- At the bound tuple with the guard true, the command rule itself decides with its sign. -/
theorem demand_decides (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands)
    (S : VE.Structure.{u}) (hS : S.Admissible (En D)) (vs : List S.Carrier)
    (typed : VE.TupleTyped S (actSorts D c) vs) (hb : boundTuple D c S = some vs) (hg : c.guard.denote S []) :
    DecidesD (policy D).T S (tupleVal vs) c.act (decide (c.force = .require)) := by
  refine ⟨demand D c, ?_, rfl, (demand_applies D h c hc S hS vs typed).mpr ⟨hb, hg⟩, ?_⟩
  · simp only [rulesOn, List.mem_filter, beq_iff_eq]
    exact ⟨demand_mem D hc, rfl⟩
  · rw [demand_children D h c hc]
    simp

/-- The realising predicate of a command, as a layer symbol of the policy. -/
theorem command_symbol {D : SpeechDoc} (h : WellFormedSpeech D = true) {c : Command} (hc : c ∈ D.commands) :
    ∃ (r : Regulated) (k : Nat), regOf D c.act = some r ∧ r.name = c.act ∧ r ∈ (policy D).T.regulated ∧
      (syms (policy D).T)[k]? = some (.reg r) ∧ actSorts D c = r.sorts := by
  obtain ⟨r, _, _, hr, _, _, hp, _⟩ := command_facts h hc
  obtain ⟨hmem, hn⟩ := regOf_spec hr
  have hv := valid_of_wellFormed _ (policy_wellFormed D h)
  obtain ⟨k, hk⟩ := VE.Norms.mem_syms_index (hv.regulated r hmem)
  exact ⟨r, k, hr, hn, hmem, hk, actSorts_eq hp⟩

/-- The elaboration clauses of the realising predicate at a typed tuple. -/
theorem elab_at {D : SpeechDoc} (h : WellFormedSpeech D = true) {c : Command} (hc : c ∈ D.commands)
    (S : VE.Structure.{u}) (hel : Sat S (elaborate (policy D).T)) (vs : List S.Carrier)
    (typed : VE.TupleTyped S (actSorts D c) vs) :
    ((VE.Norms.pos (policy D).T c.act).denote S (tupleVal vs) → S.relation c.act vs) ∧
      ((VE.Norms.neg (policy D).T c.act).denote S (tupleVal vs) → ¬ S.relation c.act vs) := by
  obtain ⟨r, k, _, hn, _, hk, hsorts⟩ := command_symbol h hc
  have hv := valid_of_wellFormed _ (policy_wellFormed D h)
  have hs : Sym.reg r ∈ syms (policy D).T := List.mem_of_getElem? hk
  have he := hel _ (VE.Norms.mem_elaborate.mpr ⟨r, hs, rfl⟩)
  rw [elabPremise, VE.Norms.bindAll_denote_nil] at he
  rw [hsorts] at typed
  have hb := (VE.Norms.elabBody_denote _ r (VE.Norms.regulated_arity hv hs) S vs typed).mp (he vs typed)
  rw [hn] at hb
  exact ⟨hb.1, hb.2.1⟩

/-- The command's normative contribution: where the elaboration holds and no opposite rule decides at the bound tuple,
    the realising predicate holds there iff the force is require (required_act(ā), respectively ¬permitted_act(ā)). -/
theorem demand_consequence (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands)
    (S : VE.Structure) (hS : S.Admissible (En D)) (hel : Sat S (elaborate (policy D).T))
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSorts D c) vs)
    (hb : boundTuple D c S = some vs) (hg : c.guard.denote S [])
    (hno : ¬ DecidesD (policy D).T S (tupleVal vs) c.act (!decide (c.force = .require))) :
    S.relation c.act vs ↔ c.force = .require := by
  have hd := demand_decides D h c hc S hS vs typed hb hg
  have he := elab_at h hc S hel vs typed
  cases hf : c.force with
  | require =>
    simp only [hf, decide_true] at hd
    exact ⟨fun _ => rfl, fun _ => he.1 ((VE.Norms.decides_denote _ S _ _ _).mpr hd)⟩
  | forbid =>
    simp only [hf] at hd
    exact ⟨fun hr => absurd hr (he.2 ((VE.Norms.decides_denote _ S _ _ _).mpr hd)), fun e => by cases e⟩

/-- Where an opposite rule does decide there, the local elaboration of `c.act` cannot hold in `S` (via
    `decides_forget` and `elaborate_iff_at`). This is the whole of what follows from `hop` alone. -/
theorem demand_conflict_local (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands)
    (S : VE.Structure) (hS : S.Admissible (En D)) (vs : List S.Carrier) (typed : VE.TupleTyped S (actSorts D c) vs)
    (hb : boundTuple D c S = some vs) (hg : c.guard.denote S [])
    (hop : DecidesD (policy D).T S (tupleVal vs) c.act (!decide (c.force = .require))) :
    ¬ Sat S (elaborate (policy D).T) := by
  intro hel
  have hd := demand_decides D h c hc S hS vs typed hb hg
  have he := elab_at h hc S hel vs typed
  cases hf : c.force with
  | require =>
    simp only [hf, decide_true, Bool.not_true] at hd hop
    exact he.2 ((VE.Norms.decides_denote _ S _ _ _).mpr hop) (he.1 ((VE.Norms.decides_denote _ S _ _ _).mpr hd))
  | forbid =>
    simp only [hf] at hd hop
    exact he.2 ((VE.Norms.decides_denote _ S _ _ _).mpr hd) (he.1 ((VE.Norms.decides_denote _ S _ _ _).mpr hop))

/-- ... and, when `S` agrees with every layer below `c.act` (W1's `AgreesBelow`, the hypothesis of `conflict_denote`),
    the base policy is a W1 conflict at that tuple: never a silent override. Without `ha` the conclusion is false:
    with a guard over a lower regulated predicate (12.11), an `S` admissible over `En D` whose lower relations are
    arbitrary can satisfy `hop` while the regenerated `conflict_p°` is false at the base restriction. `ConstantsTyped`
    comes from `hS`; the `PrefixAdmissible` form is a corollary through `agreesBelow_of_meanings`. -/
theorem demand_conflict (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands)
    (S : VE.Structure) (hS : S.Admissible (En D)) (vs : List S.Carrier) (typed : VE.TupleTyped S (actSorts D c) vs)
    (ha : AgreesBelow (policy D) (before (policy D) c.act) S)
    (hb : boundTuple D c S = some vs) (hg : c.guard.denote S [])
    (hop : DecidesD (policy D).T S (tupleVal vs) c.act (!decide (c.force = .require))) :
    ¬ ConflictFree (policy D) (restrictAll (policy D).T S) := by
  intro hcf
  obtain ⟨r, k, _, hn, hmem, hk, hsorts⟩ := command_symbol h hc
  have hv := valid_of_wellFormed _ (policy_wellFormed D h)
  have hbk : before (policy D) c.act = k := by rw [← hn]; exact VE.Norms.before_eq hv hk
  rw [hbk] at ha
  have hct : VE.Norms.ConstantsTyped (policy D) S := fun x s hx => hS.1 x s hx
  have typed' : VE.TupleTyped S r.sorts vs := hsorts ▸ typed
  have hd := demand_decides D h c hc S hS vs typed hb hg
  have hclash : ((VE.Norms.Sym.reg r).clash (policy D).T).denote S (tupleVal vs) := by
    simp only [VE.Norms.Sym.clash, VE.Formula.denote, VE.Norms.pos, VE.Norms.neg, VE.Norms.decides_denote, hn]
    cases hf : c.force with
    | require =>
      simp only [hf, decide_true, Bool.not_true] at hd hop
      exact ⟨hd, hop⟩
    | forbid =>
      simp only [hf] at hd hop
      exact ⟨hop, hd⟩
  exact hcf.1 r hmem vs ((VE.Norms.tupleTyped_restrictAll _ S _ vs).mpr typed')
    ((VE.Norms.conflict_denote hv hk S hct ha vs typed').mpr hclash)

/-- Every command rule is guarded by the one addressee of the scope. -/
theorem scope_single (D : SpeechDoc) (h : WellFormedSpeech D = true) (c : Command) (hc : c ∈ D.commands) :
    ∃ you, addresseeConst D = some you ∧ VE.Norms.preds (eqGuard D c) = [] ∧
      (∀ S : VE.Structure, ∀ vs, boundTuple D c S = some vs → vs.head? = S.constant you) := by
  obtain ⟨_, s, you, _, ha, _⟩ := command_facts h hc
  have hy := addresseeConst_eq ha
  refine ⟨you, hy, preds_conj _ (preds_eqsFrom _ _), fun S vs hvs => ?_⟩
  simp only [boundTuple, hy, constsOf] at hvs
  cases h1 : S.constant you <;> cases h2 : constsOf S c.args <;> simp [h1, h2] at hvs
  subst hvs
  simp

end VE.SpeechActs
