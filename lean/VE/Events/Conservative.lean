import VE.Events.Calendar
import VE.Readings.Names
import VE.Readings.Superpose

/-! Conservativity (docs/spec/events-time-causation.md 6.1, 6.2): the block changes no consequence
written in the vocabulary it does not touch (`oldEnv`: no day sort, nothing with the day sort in its
signature, no link). One way restricts a structure of the block to that vocabulary; the other expands
a structure of the old vocabulary with the named dates' days in date order (`expansion`). The proof
needs the date names to be one-to-one (`dateName_inj`). Its finite form with nothing to expand
(`datesSituation`) shows that the generated premises alone have a finite calendar situation. -/
namespace VE.Events
open VE.Norms (Sat)
open VE.Time (Civil pad dateMax)
universe u

/-- The vocabulary the block does not touch: no day sort, nothing with the day sort in its signature, no link. -/
def oldEnv (E : VE.Environment) (V : EventsEnv) : VE.Environment :=
  { sorts := E.sorts.filter (· != V.day)
    predicates := fun p => match E.predicates p with
      | some ss => if ss.contains V.day || V.links.any (·.predicate == p) then none else some ss
      | none => none
    constants := fun c => match E.constants c with
      | some s => if s == V.day then none else some s
      | none => none }

/-! ## Date names are one-to-one -/

theorem pad_value (w n : Nat) : (pad w n).data.foldl (fun v c => 10 * v + (c.toNat - 48)) 0 = n := by
  have hz : ∀ k, (List.replicate k '0').foldl (fun v c => 10 * v + (c.toNat - 48)) 0 = 0 := by
    intro k; induction k with
    | zero => rfl
    | succ k ih => rw [List.replicate_succ, List.foldl_cons]; exact ih
  have := VE.Readings.toDigitsCore_value (n + 1) n [] (by omega)
  simp only [List.foldl_nil] at this
  simp only [pad, String.data_append, List.foldl_append, hz, VE.Readings.toString_data]
  exact this

theorem pad_chars (w n : Nat) : ∀ c ∈ (pad w n).data, c ≠ '_' ∧ c ≠ '-' := by
  intro c hc
  simp only [pad, String.data_append, List.mem_append, VE.Readings.toString_data] at hc
  rcases hc with hc | hc
  · rw [List.eq_of_mem_replicate hc]; decide
  · have := List.all_eq_true.1 (VE.Readings.toDigitsCore_valid (n + 1) n [] rfl) c hc
    simp only [Bool.and_eq_true, decide_eq_true_eq] at this
    exact ⟨fun h => by subst h; exact absurd this.2 (by decide), fun h => by subst h; exact absurd this.1 (by decide)⟩

theorem dateName_data (D : Civil) : (dateName D).data = "date__".data ++
    ((pad 4 D.year).data ++ '_' :: ((pad 2 D.month).data ++ '_' :: (pad 2 D.day).data)) := by
  have keep : ∀ w n, (pad w n).data.map (fun c => if c = '-' then '_' else c) = (pad w n).data := fun w n => by
    conv => rhs; rw [← List.map_id (pad w n).data]
    exact List.map_congr_left (fun c hc => if_neg (pad_chars w n c hc).2)
  have ts : ∀ s : String, toString s = s := fun _ => rfl
  simp [dateName, Civil.iso, String.data_append, VE.Readings.map_data, ts, keep]

theorem dateName_inj {D D' : Civil} (h : dateName D = dateName D') : D = D' := by
  have := congrArg String.data h
  rw [dateName_data, dateName_data] at this
  have h2 := List.append_cancel_left this
  obtain ⟨hy, h3⟩ := VE.Readings.split_underscore _ _ _ _ (fun c hc => (pad_chars _ _ c hc).1)
    (fun c hc => (pad_chars _ _ c hc).1) h2
  obtain ⟨hm, hd⟩ := VE.Readings.split_underscore _ _ _ _ (fun c hc => (pad_chars _ _ c hc).1)
    (fun c hc => (pad_chars _ _ c hc).1) h3
  have vy := congrArg (List.foldl (fun v c => 10 * v + (c.toNat - 48)) 0) hy
  have vm := congrArg (List.foldl (fun v c => 10 * v + (c.toNat - 48)) 0) hm
  have vd := congrArg (List.foldl (fun v c => 10 * v + (c.toNat - 48)) 0) hd
  rw [pad_value, pad_value] at vy vm vd
  cases D; cases D'; simp_all

/-! ## Transfer along an embedding that is exact on a vocabulary -/

/-- A typed formula of `E'` has the same value in `S` and in `T` when `ι` embeds `S` in `T` exactly on
    `E'`'s sorts, constants and predicates. -/
theorem wf_transfer (E' : VE.Environment) (S T : VE.Structure.{u}) (ι : S.Carrier → T.Carrier)
    (inj : ∀ x y, ι x = ι y → x = y)
    (dom : ∀ s ∈ E'.sorts, ∀ y, T.domain s y ↔ ∃ x, ι x = y ∧ S.domain s x)
    (con : ∀ c s, E'.constants c = some s → T.constant c = (S.constant c).map ι)
    (rel : ∀ p ss, E'.predicates p = some ss → ∀ xs, T.relation p (xs.map ι) ↔ S.relation p xs) :
    ∀ (a : VE.Formula) (Γ : List String) (ρ : List S.Carrier), a.WellFormed E' Γ →
      (a.denote T (ρ.map ι) ↔ a.denote S ρ) := by
  have tm : ∀ (t : VE.Term) Γ s (ρ : List S.Carrier), t.sortOf E' Γ = some s →
      t.denote T (ρ.map ι) = (t.denote S ρ).map ι := by
    intro t Γ s ρ ht
    cases t with
    | var i => simp [VE.Term.denote]
    | const c => exact con c s ht
  intro a
  induction a with
  | top | bottom => intros; exact Iff.rfl
  | unary p t =>
    rintro Γ ρ ⟨s, hp, ht⟩
    simp only [VE.Formula.denote, tm t Γ s ρ ht]
    constructor
    · rintro ⟨_, hv, hr⟩
      obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.1 hv
      exact ⟨x, hx, (rel p _ hp [x]).1 hr⟩
    · rintro ⟨x, hx, hr⟩
      exact ⟨ι x, by simp [hx], (rel p _ hp [x]).2 hr⟩
  | binary p t w =>
    rintro Γ ρ ⟨s, r, hp, ht, hw⟩
    simp only [VE.Formula.denote, tm t Γ s ρ ht, tm w Γ r ρ hw]
    constructor
    · rintro ⟨_, _, hv, hv', hr⟩
      obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.1 hv
      obtain ⟨x', hx', rfl⟩ := Option.map_eq_some_iff.1 hv'
      exact ⟨x, x', hx, hx', (rel p _ hp [x, x']).1 hr⟩
    · rintro ⟨x, x', hx, hx', hr⟩
      exact ⟨ι x, ι x', by simp [hx], by simp [hx'], (rel p _ hp [x, x']).2 hr⟩
  | eq t w =>
    rintro Γ ρ ⟨s, ht, hw⟩
    simp only [VE.Formula.denote, tm t Γ s ρ ht, tm w Γ s ρ hw]
    constructor
    · rintro ⟨v, hv, hv'⟩
      obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.1 hv
      obtain ⟨x', hx', he⟩ := Option.map_eq_some_iff.1 hv'
      exact ⟨x, hx, by rw [hx', inj _ _ he]⟩
    · rintro ⟨x, hx, hx'⟩
      exact ⟨ι x, by simp [hx], by simp [hx']⟩
  | not a ih => intro Γ ρ h; exact not_congr (ih Γ ρ h)
  | and a b ia ib => intro Γ ρ h; exact and_congr (ia Γ ρ h.1) (ib Γ ρ h.2)
  | or a b ia ib => intro Γ ρ h; exact or_congr (ia Γ ρ h.1) (ib Γ ρ h.2)
  | implies a b ia ib => intro Γ ρ h; exact imp_congr (ia Γ ρ h.1) (ib Γ ρ h.2)
  | all s a ih =>
    rintro Γ ρ ⟨hs, ha⟩
    simp only [VE.Formula.denote]
    constructor
    · intro h x hx
      exact (ih (s :: Γ) (x :: ρ) ha).1 (h (ι x) ((dom s hs _).2 ⟨x, rfl, hx⟩))
    · intro h y hy
      obtain ⟨x, rfl, hx⟩ := (dom s hs y).1 hy
      exact (ih (s :: Γ) (x :: ρ) ha).2 (h x hx)
  | ex s a ih =>
    rintro Γ ρ ⟨hs, ha⟩
    simp only [VE.Formula.denote]
    constructor
    · rintro ⟨y, hy, h⟩
      obtain ⟨x, rfl, hx⟩ := (dom s hs y).1 hy
      exact ⟨x, hx, (ih (s :: Γ) (x :: ρ) ha).1 h⟩
    · rintro ⟨x, hx, h⟩
      exact ⟨ι x, (dom s hs _).2 ⟨x, rfl, hx⟩, (ih (s :: Γ) (x :: ρ) ha).2 h⟩


/-! ## The expansion and the theorem -/

/-- Guarded by an empty relation: `∀x. ∀y. p(x, y) → …` holds. -/
theorem guarded_empty {S : VE.Structure.{u}} {p : String} (h : ∀ v w, ¬ S.relation p [v, w])
    (s s' : String) (body : VE.Formula) (ρ : List S.Carrier) :
    (VE.Formula.all s (.all s' (.implies (bin p 1 0) body))).denote S ρ :=
  fun _ _ _ _ ⟨_, _, _, _, hr⟩ => absurd hr (h _ _)

/-- With every role and link relation empty, the conventions hold: each is guarded by one of them. -/
theorem conventions_empty (V : EventsEnv) (S : VE.Structure.{u})
    (h : ∀ p ∈ rolePreds V ++ V.links.map (·.predicate), ∀ v w, ¬ S.relation p [v, w]) :
    Sat S (conventionPremises V) := by
  have role : ∀ p ∈ rolePreds V, ∀ v w, ¬ S.relation p [v, w] := fun p hp => h p (List.mem_append_left _ hp)
  have link : ∀ l ∈ V.links, ∀ v w, ¬ S.relation l.predicate [v, w] := fun l hl =>
    h _ (List.mem_append_right _ (List.mem_map_of_mem hl))
  intro a ha
  simp only [conventionPremises, conventionLabelled, List.map_append, List.map_map, List.mem_append,
    List.mem_map, Function.comp, List.map_flatMap, List.mem_flatMap, List.map_cons, List.map_nil,
    List.mem_cons, List.not_mem_nil, or_false] at ha
  rcases ha with ((⟨e, hm, rfl⟩ | ⟨x, hm, hx⟩) | ⟨l, hm, rfl⟩) | ⟨⟨n, c⟩, hm, rfl⟩
  · unfold oneRoleF
    exact guarded_empty (role _ (by simp only [rolePreds, List.mem_append, List.mem_map]; exact .inl ⟨e, hm, rfl⟩)) _ _ _ _
  · have hb := role x.begins (by simp only [rolePreds, List.mem_append, List.mem_flatMap]; exact .inr ⟨x, hm, by simp⟩)
    have he := role x.ends (by simp only [rolePreds, List.mem_append, List.mem_flatMap]; exact .inr ⟨x, hm, by simp⟩)
    rcases hx with rfl | rfl | rfl
    · unfold oneRoleF; exact guarded_empty hb _ _ _ _
    · unfold oneRoleF; exact guarded_empty he _ _ _ _
    · unfold notBeforeBeginF; exact guarded_empty hb _ _ _ _
  · unfold linkForwardF
    split
    · exact guarded_empty (link l hm) _ _ _ _
    · trivial
  · simp only [weakerPairs, List.mem_flatMap, List.mem_filter, List.mem_map] at hm
    obtain ⟨n', ⟨hn, -⟩, c', -, he'⟩ := hm
    simp only [Prod.mk.injEq] at he'; obtain ⟨rfl, rfl⟩ := he'
    unfold linkWeakerF; exact guarded_empty (link n' hn) _ _ _ _

/-- The expansion's days: the named dates' numbers, or day 0 when there is none. -/
def expDays (V : EventsEnv) : List Nat := if V.dates = [] then [0] else V.dates.map (·.num)
def firstDay (V : EventsEnv) : Nat := (V.dates.head?.map (·.num)).getD 0

/-- `S` with the named dates' days in date order; author day constants denote the first day; role, link
    and day-indexed relations are empty. -/
def expansion (E : VE.Environment) (V : EventsEnv) (S : VE.Structure.{u}) : VE.Structure.{u} where
  Carrier := S.Carrier ⊕ ULift.{u} Nat
  domain := fun s z => match z with
    | .inl x => S.domain s x ∧ s ≠ V.day
    | .inr n => s = V.day ∧ n.down ∈ expDays V
  constant := fun c => match V.dates.find? (fun D => dateName D == c) with
    | some D => some (.inr ⟨D.num⟩)
    | none => if E.constants c = some V.day then some (.inr ⟨firstDay V⟩) else (S.constant c).map .inl
  relation := fun p zs =>
    (∃ xs, zs = xs.map .inl ∧ S.relation p xs ∧ (oldEnv E V).predicates p ≠ none) ∨
    (p = V.before ∧ ∃ m n : ULift.{u} Nat, zs = [.inr m, .inr n] ∧ m.down ∈ expDays V ∧ n.down ∈ expDays V ∧
      m.down < n.down)

theorem expansion_typed {E : VE.Environment} {V : EventsEnv} {S : VE.Structure.{u}} :
    ∀ (ss : List String) (xs : List S.Carrier), V.day ∉ ss → VE.TupleTyped S ss xs →
      VE.TupleTyped (expansion E V S) ss (xs.map .inl)
  | [], [], _, _ => trivial
  | _ :: ss, _ :: xs, hd, ⟨h, ht⟩ =>
    ⟨⟨h, fun he => hd (he ▸ List.mem_cons_self ..)⟩, expansion_typed ss xs (fun h => hd (List.mem_cons_of_mem _ h)) ht⟩
  | [], _ :: _, _, h => h.elim
  | _ :: _, [], _, h => h.elim

theorem tupleTyped_relation (S : VE.Structure.{u}) (r : String → List S.Carrier → Prop) :
    ∀ ss xs, VE.TupleTyped S ss xs → VE.TupleTyped { S with relation := r } ss xs
  | [], [], _ => trivial
  | _ :: ss, _ :: xs, ⟨h, ht⟩ => ⟨h, tupleTyped_relation S r ss xs ht⟩
  | [], _ :: _, h => h.elim
  | _ :: _, [], h => h.elim

/-- Conservativity over the untouched vocabulary. Proof by restriction one way and, the other way, by an expansion
    on `S.Carrier ⊕ ULift Nat` whose days are the named dates' days in date order (author day constants sent to the
    first named day, or to a single day 0 when there is none; role, link and day-indexed relations empty). -/
theorem events_conservative (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true)
    (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (oldEnv E V) []) (hφ : φ.WellFormed (oldEnv E V) []) :
    (∀ S : VE.Structure.{u}, S.Admissible (regenEnv E V) → Sat S (eventsX V) → Sat S Γ → φ.denote S []) ↔
    (∀ S : VE.Structure.{u}, S.Admissible (oldEnv E V) → Sat S Γ → φ.denote S []) := by
  have hT := regen_typed E V h
  simp only [WellFormedEvents, Bool.and_eq_true, List.all_eq_true, sig2, beq_iff_eq, decide_eq_true_eq,
    List.contains_iff_mem, Bool.not_eq_true', bne_iff_ne, ne_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨-, hb⟩, he⟩, hs⟩, -⟩, -⟩, hbr⟩, hl⟩, -⟩, hd⟩, -⟩, -⟩, -⟩ := h
  have hbr : V.before ∉ rolePreds V := by simpa using hbr
  have oldPred : ∀ p ss, (oldEnv E V).predicates p = some ss → E.predicates p = some ss ∧ V.day ∉ ss := by
    intro p ss hp
    simp only [oldEnv] at hp
    split at hp
    · next ss' hs' =>
      split at hp
      · cases hp
      · next hc => cases hp; simp only [Bool.or_eq_true, not_or, List.contains_iff_mem] at hc; exact ⟨hs', hc.1⟩
    · cases hp
  have dayNone : ∀ p ss, E.predicates p = some ss → V.day ∈ ss → (oldEnv E V).predicates p = none := by
    intro p ss hp hm
    cases h' : (oldEnv E V).predicates p with
    | none => rfl
    | some ss' => obtain ⟨h1, h2⟩ := oldPred p ss' h'; rw [hp] at h1; cases h1; exact absurd hm h2
  have linkNone : ∀ l ∈ V.links, (oldEnv E V).predicates l.predicate = none := by
    intro l hm
    simp only [oldEnv]
    split
    · rw [if_pos (by simp only [Bool.or_eq_true, List.any_eq_true, beq_iff_eq]; exact .inr ⟨l, hm, rfl⟩)]
    · rfl
  have roleNone : ∀ p ∈ rolePreds V, (oldEnv E V).predicates p = none := by
    intro p hp
    simp only [rolePreds, List.mem_append, List.mem_map, List.mem_flatMap, List.mem_cons,
      List.not_mem_nil, or_false] at hp
    rcases hp with ⟨e, hm, rfl⟩ | ⟨x, hm, rfl | rfl⟩
    · exact dayNone _ _ (he e hm).2 (by simp)
    · exact dayNone _ _ (hs x hm).1.2 (by simp)
    · exact dayNone _ _ (hs x hm).2 (by simp)
  have beforeNone : (oldEnv E V).predicates V.before = none := dayNone _ _ hb (by simp)
  have oldConst : ∀ c s, (oldEnv E V).constants c = some s → E.constants c = some s ∧ s ≠ V.day := by
    intro c s hc
    simp only [oldEnv] at hc
    split at hc
    · next s' hs' =>
      split at hc
      · cases hc
      · next hne => cases hc; exact ⟨hs', by simpa using hne⟩
    · cases hc
  have notDate : ∀ c s, E.constants c = some s → V.dates.any (fun D => dateName D == c) = false := by
    intro c s hc
    simp only [List.any_eq_false, beq_iff_eq]
    rintro D hD rfl
    rw [(hd D hD).2] at hc; cases hc
  constructor
  · -- expansion: a structure of the old vocabulary gains the named dates' days
    intro H S hS hΓS
    have dom : ∀ s ∈ (oldEnv E V).sorts, ∀ y, (expansion E V S).domain s y ↔ ∃ x, Sum.inl x = y ∧ S.domain s x := by
      intro s hm y
      have hne : s ≠ V.day := by simp only [oldEnv, List.mem_filter, bne_iff_ne] at hm; exact hm.2
      cases y with
      | inl x => exact ⟨fun h => ⟨x, rfl, h.1⟩, fun ⟨x', he, h⟩ => by cases he; exact ⟨h, hne⟩⟩
      | inr n => exact ⟨fun h => absurd h.1 hne, fun ⟨_, he, _⟩ => by cases he⟩
    have findNone : ∀ c s, E.constants c = some s → V.dates.find? (fun D => dateName D == c) = none := by
      intro c s hc
      rw [List.find?_eq_none]
      intro D hD he
      have := notDate c s hc
      simp only [List.any_eq_false] at this
      exact this D hD he
    have con : ∀ c s, (oldEnv E V).constants c = some s →
        (expansion E V S).constant c = (S.constant c).map Sum.inl := by
      intro c s hc
      obtain ⟨h1, h2⟩ := oldConst c s hc
      simp only [expansion, findNone c s h1, h1, Option.some.injEq]
      rw [if_neg (fun h => h2 h)]
    have rel : ∀ p ss, (oldEnv E V).predicates p = some ss →
        ∀ xs, (expansion E V S).relation p (xs.map Sum.inl) ↔ S.relation p xs := by
      intro p ss hp xs
      simp only [expansion]
      constructor
      · rintro (⟨xs', he, hr, -⟩ | ⟨rfl, -⟩)
        · rw [List.map_inj_right (fun _ _ h => Sum.inl.inj h) |>.1 he]; exact hr
        · rw [beforeNone] at hp; cases hp
      · exact fun hr => .inl ⟨xs, rfl, hr, by rw [hp]; simp⟩
    have tr := wf_transfer (oldEnv E V) S (expansion E V S) Sum.inl (fun _ _ h => Sum.inl.inj h) dom con rel
    have firstIn : firstDay V ∈ expDays V := by
      unfold firstDay expDays
      cases V.dates <;> simp
    have dateIn : ∀ D ∈ V.dates, D.num ∈ expDays V := by
      intro D hD
      unfold expDays
      rw [if_neg (List.ne_nil_of_mem hD)]
      exact List.mem_map_of_mem hD
    have dateConst : ∀ D ∈ V.dates, (expansion E V S).constant (dateName D) = some (.inr ⟨D.num⟩) := by
      intro D hD
      simp only [expansion]
      cases hf : V.dates.find? (fun D' => dateName D' == dateName D) with
      | some D' =>
        have := List.find?_some hf
        simp only [beq_iff_eq] at this
        rw [dateName_inj this]
      | none =>
        rw [List.find?_eq_none] at hf
        exact absurd (by simp) (hf D hD)
    have adm : (expansion E V S).Admissible (regenEnv E V) := by
      refine ⟨fun c s hc => ?_, fun p zs hr => ?_⟩
      · simp only [regenEnv] at hc
        split at hc
        · next hany =>
          cases hc
          obtain ⟨D, hD, he⟩ := List.any_eq_true.1 hany
          simp only [beq_iff_eq] at he; subst he
          exact ⟨_, dateConst D hD, rfl, dateIn D hD⟩
        · by_cases hday : s = V.day
          · subst hday
            refine ⟨.inr ⟨firstDay V⟩, ?_, rfl, firstIn⟩
            simp only [expansion, findNone c _ hc, hc, if_true]
          · obtain ⟨v, hv, dv⟩ := hS.1 c s (by simp only [oldEnv, hc, beq_iff_eq, if_neg hday])
            refine ⟨.inl v, ?_, dv, hday⟩
            simp only [expansion, findNone c _ hc, hc, Option.some.injEq]
            rw [if_neg hday, hv]; rfl
      · rcases hr with ⟨xs, rfl, hr, -⟩ | ⟨rfl, m, n, rfl, hm, hn, -⟩
        · obtain ⟨ss, hp, ht⟩ := hS.2 p xs hr
          obtain ⟨h1, h2⟩ := oldPred p ss hp
          exact ⟨ss, h1, expansion_typed ss xs h2 ht⟩
        · exact ⟨[V.day, V.day], hb, ⟨rfl, hm⟩, ⟨⟨rfl, hn⟩, trivial⟩⟩
    let num : (expansion E V S).Carrier → Nat := fun z => match z with
      | .inl _ => 0
      | .inr n => n.down
    have emb : Embeds V (expansion E V S) num := by
      have day : ∀ z, (expansion E V S).domain V.day z → ∃ n : ULift.{u} Nat, z = .inr n ∧ n.down ∈ expDays V := by
        intro z hz
        cases z with
        | inl x => exact absurd rfl hz.2
        | inr n => exact ⟨n, rfl, hz.2⟩
      refine ⟨fun z w hz hw he => ?_, fun z hz => ?_, fun z w hz hw => ?_, fun D hD => ⟨_, dateConst D hD, ⟨rfl, dateIn D hD⟩, rfl⟩⟩
      · obtain ⟨m, rfl, -⟩ := day z hz
        obtain ⟨n, rfl, -⟩ := day w hw
        exact congrArg Sum.inr (congrArg ULift.up.{u} he)
      · obtain ⟨n, rfl, hn⟩ := day z hz
        show n.down ≤ dateMax
        unfold expDays at hn
        split at hn
        · simp at hn; omega
        · obtain ⟨D, hD, he⟩ := List.mem_map.1 hn
          rw [← he]
          have hp := (VE.Time.Civil.properB_iff D).1 (hd D hD).1.1
          exact (VE.Time.valid_iff hp).1 ⟨hp, (hd D hD).1.2⟩
      · obtain ⟨m, rfl, hm⟩ := day z hz
        obtain ⟨n, rfl, hn⟩ := day w hw
        simp only [expansion]
        constructor
        · rintro (⟨xs, he, -, hne⟩ | ⟨-, m', n', he, -, -, hl⟩)
          · rw [beforeNone] at hne; exact absurd rfl hne
          · simp only [List.cons.injEq, Sum.inr.injEq, and_true] at he
            obtain ⟨rfl, rfl⟩ := he; exact hl
        · exact fun hl => .inr ⟨trivial, m, n, rfl, hm, hn, hl⟩
    have hX : Sat (expansion E V S) (eventsX V) := by
      have hc := calendar_sat (regenEnv E V) V hT _ adm num emb
      have hv := conventions_empty V (expansion E V S) (by
        intro p hp v w hr
        rcases hr with ⟨-, -, -, hne⟩ | ⟨rfl, -⟩
        · rcases List.mem_append.1 hp with hp | hp
          · exact hne (roleNone p hp)
          · obtain ⟨l, hm, rfl⟩ := List.mem_map.1 hp; exact hne (linkNone l hm)
        · rcases List.mem_append.1 hp with hp | hp
          · exact hbr hp
          · obtain ⟨l, hm, he⟩ := List.mem_map.1 hp; exact (hl l hm).2 he)
      intro a ha
      simp only [eventsX, eventsLabelled, List.map_append, List.mem_append] at ha
      exact ha.elim (hc a) (hv a)
    exact (tr φ [] [] hφ).1 (H _ adm hX (fun a ha => (tr a [] [] (hΓ a ha)).2 (hΓS a ha)))
  · -- restriction: a structure of the block forgets the touched vocabulary
    intro H S hS hX hΓS
    let R : VE.Structure.{u} :=
      { S with relation := fun p vs => S.relation p vs ∧ (oldEnv E V).predicates p ≠ none }
    have tr := wf_transfer (oldEnv E V) R S id (fun _ _ h => h)
      (fun s _ y => ⟨fun h => ⟨y, rfl, h⟩, fun ⟨_, he, hx⟩ => he ▸ hx⟩) (fun c s _ => by simp [R])
      (fun p ss hp xs => by simp [R, hp])
    have adm : R.Admissible (oldEnv E V) := by
      refine ⟨fun c s hc => ?_, fun p vs ⟨hr, hne⟩ => ?_⟩
      · obtain ⟨h1, -⟩ := oldConst c s hc
        exact hS.1 c s (by simp only [regenEnv, notDate c s h1, Bool.false_eq_true, if_false]; exact h1)
      · obtain ⟨ss, hp, ht⟩ := hS.2 p vs hr
        cases ho : (oldEnv E V).predicates p with
        | none => exact absurd ho hne
        | some ss' =>
          obtain ⟨h1, -⟩ := oldPred p ss' ho
          have : ss = ss' := by have h2 : E.predicates p = some ss := hp; rw [h1] at h2; cases h2; rfl
          subst this
          exact ⟨ss, rfl, tupleTyped_relation S _ ss vs ht⟩
    exact (tr φ [] [] hφ).2 (H R adm (fun a ha => (tr a [] [] (hΓ a ha)).1 (hΓS a ha)))

/-! ## The pack alone is satisfiable -/

/-- The days of `datesSituation`, by name: the named dates' constants, or one day `""` when there is none. -/
def dayNames (V : EventsEnv) : List String := if V.dates = [] then [""] else V.dates.map dateName
def firstName (V : EventsEnv) : String := (V.dates.head?.map dateName).getD ""

/-- The finite form of `expansion` with nothing to expand: the named dates' days `(day, name)` in date order, one
    element `(s, "")` of every other sort, author day constants on the first day, and no fact but the days' order. -/
def datesSituation (E : VE.Environment) (V : EventsEnv) : VE.FiniteModel VE.Bridge.Entity where
  domains := fun s => if s = V.day then (dayNames V).map (V.day, ·) else [(s, "")]
  constants := fun c => if V.dates.any (fun D => dateName D == c) then some (V.day, c)
    else (E.constants c).map fun s => if s = V.day then (V.day, firstName V) else (s, "")
  relations := fun p => if p = V.before then
      V.dates.flatMap fun D => (V.dates.filter (fun D' => decide (D.num < D'.num))).map
        fun D' => [(V.day, dateName D), (V.day, dateName D')]
    else []

theorem chain_pairwise {β : Type} (R : β → β → Prop) (trans : ∀ a b c, R a b → R b c → R a c) :
    ∀ (l : List β), (∀ p ∈ l.zip l.tail, R p.1 p.2) → l.Pairwise R
  | [], _ => .nil
  | a :: rest, h => .cons (chain_head R trans rest a h) (chain_pairwise R trans rest (fun p hp => h p (by
      cases rest with
      | nil => simp at hp
      | cons c rest => exact List.mem_cons_of_mem _ hp)))

/-- The pack alone is satisfiable by a finite calendar situation. -/
theorem eventsPremises_satisfiable (E : VE.Environment) (V : EventsEnv) (h : WellFormedEvents E V = true) :
    ∃ M : VE.FiniteModel VE.Bridge.Entity, M.Valid (regenEnv E V) ∧ Sat M.asStructure (eventsX V) ∧
      embeddable V M = true := by
  have hT := regen_typed E V h
  simp only [WellFormedEvents, Bool.and_eq_true, List.all_eq_true, sig2, beq_iff_eq, decide_eq_true_eq,
    List.contains_iff_mem, Bool.not_eq_true', bne_iff_ne, ne_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨-, hb⟩, -⟩, -⟩, -⟩, -⟩, hbr⟩, hl⟩, -⟩, hd⟩, hlt⟩, -⟩, -⟩ := h
  have hbr : V.before ∉ rolePreds V := by simpa using hbr
  let M := datesSituation E V
  have hlt : ∀ p ∈ V.dates.zip V.dates.tail, p.1.num < p.2.num := fun p hp => by
    simpa using hlt p hp
  have pos := chain_positions (fun D D' : Civil => D.num < D'.num) (fun _ _ _ => Nat.lt_trans) V.dates hlt
  have pw := chain_pairwise (fun D D' : Civil => D.num < D'.num) (fun _ _ _ => Nat.lt_trans) V.dates hlt
  have numInj : ∀ D ∈ V.dates, ∀ D' ∈ V.dates, D.num = D'.num → D = D' := fun D hD D' hD' he => by
    rcases pos D hD D' hD' with h | h | h
    · exact h
    · omega
    · omega
  let num : VE.Bridge.Entity → Nat := fun z => ((V.dates.find? (fun D => dateName D == z.2)).map (·.num)).getD 0
  have numD : ∀ D ∈ V.dates, num (V.day, dateName D) = D.num := fun D hD => by
    cases hf : V.dates.find? (fun D' => dateName D' == dateName D) with
    | some D' =>
      have := List.find?_some hf
      simp only [beq_iff_eq] at this
      simp [num, hf, dateName_inj this]
    | none => exact absurd (by simp) (List.find?_eq_none.1 hf D hD)
  have days : ∀ z, z ∈ M.domains V.day ↔ ∃ n ∈ dayNames V, z = (V.day, n) := fun z => by
    simp only [M, datesSituation, if_true, List.mem_map]
    exact ⟨fun ⟨n, hn, he⟩ => ⟨n, hn, he.symm⟩, fun ⟨n, hn, he⟩ => ⟨n, hn, he.symm⟩⟩
  -- a day is a named date's day, or the one day `""` when there is none
  have dayCases : ∀ z ∈ M.domains V.day, (∃ D ∈ V.dates, z = (V.day, dateName D)) ∨ (V.dates = [] ∧ z = (V.day, "")) :=
    fun z hz => by
      obtain ⟨n, hn, rfl⟩ := (days z).1 hz
      unfold dayNames at hn
      split at hn
      · next he => simp at hn; exact .inr ⟨he, by rw [hn]⟩
      · obtain ⟨D, hD, rfl⟩ := List.mem_map.1 hn; exact .inl ⟨D, hD, rfl⟩
  have dayOf : ∀ D ∈ V.dates, (V.day, dateName D) ∈ M.domains V.day := fun D hD =>
    (days _).2 ⟨_, by unfold dayNames; rw [if_neg (List.ne_nil_of_mem hD)]; exact List.mem_map_of_mem hD, rfl⟩
  have firstIn : (V.day, firstName V) ∈ M.domains V.day := (days _).2 ⟨_, by
    unfold dayNames firstName; cases V.dates <;> simp, rfl⟩
  have before : ∀ D ∈ V.dates, ∀ D' ∈ V.dates,
      [(V.day, dateName D), (V.day, dateName D')] ∈ M.relations V.before ↔ D.num < D'.num := by
    intro D hD D' hD'
    simp only [M, datesSituation, if_true, List.mem_flatMap, List.mem_map, List.mem_filter, decide_eq_true_eq,
      List.cons.injEq, Prod.mk.injEq, true_and, and_true]
    constructor
    · rintro ⟨A, -, B, ⟨-, hab⟩, ha, hb⟩
      rw [← dateName_inj ha, ← dateName_inj hb]; exact hab
    · exact fun hl => ⟨D, hD, D', ⟨hD', hl⟩, rfl, rfl⟩
  have relBefore : ∀ p zs, zs ∈ M.relations p → p = V.before ∧ ∃ D ∈ V.dates, ∃ D' ∈ V.dates,
      zs = [(V.day, dateName D), (V.day, dateName D')] := by
    intro p zs hz
    simp only [M, datesSituation] at hz
    split at hz
    · next hp =>
      obtain ⟨D, hD, hz⟩ := List.mem_flatMap.1 hz
      obtain ⟨D', hD', rfl⟩ := List.mem_map.1 hz
      exact ⟨hp, D, hD, D', (List.mem_filter.1 hD').1, rfl⟩
    · cases hz
  have emb : Embeds V M.asStructure num := by
    refine ⟨fun z w hz hw he => ?_, fun z hz => ?_, fun z w hz hw => ?_, fun D hD => ?_⟩
    · rcases dayCases z hz with ⟨D, hD, rfl⟩ | ⟨h0, rfl⟩ <;> rcases dayCases w hw with ⟨D', hD', rfl⟩ | ⟨h0', rfl⟩
      · rw [numD D hD, numD D' hD'] at he; rw [numInj D hD D' hD' he]
      · rw [h0'] at hD; cases hD
      · rw [h0] at hD'; cases hD'
      · rfl
    · rcases dayCases z hz with ⟨D, hD, rfl⟩ | ⟨h0, rfl⟩
      · rw [numD D hD]
        have hp := (VE.Time.Civil.properB_iff D).1 (hd D hD).1.1
        exact (VE.Time.valid_iff hp).1 ⟨hp, (hd D hD).1.2⟩
      · simp [num, h0]
    · show [z, w] ∈ M.relations V.before ↔ num z < num w
      rcases dayCases z hz with ⟨D, hD, rfl⟩ | ⟨h0, rfl⟩
      · rcases dayCases w hw with ⟨D', hD', rfl⟩ | ⟨h0', rfl⟩
        · rw [before D hD D' hD', numD D hD, numD D' hD']
        · rw [h0'] at hD; cases hD
      · refine ⟨fun hr => ?_, fun hl => by simp [num, h0] at hl⟩
        obtain ⟨-, D, hD, -⟩ := relBefore _ _ hr
        rw [h0] at hD; cases hD
    · refine ⟨_, ?_, dayOf D hD, numD D hD⟩
      show M.constants (dateName D) = _
      simp only [M, datesSituation]; rw [if_pos (List.any_eq_true.2 ⟨D, hD, by simp⟩)]
  have adm : M.Valid (regenEnv E V) := by
    refine ⟨fun c s hc => ?_, fun p zs hr => ?_⟩
    · simp only [regenEnv] at hc
      split at hc
      · next hany =>
        cases hc
        obtain ⟨D, hD, he⟩ := List.any_eq_true.1 hany
        simp only [beq_iff_eq] at he; subst he
        exact ⟨_, by simp [M, datesSituation, VE.FiniteModel.asStructure, hany], dayOf D hD⟩
      · next hany =>
        by_cases hday : s = V.day
        · subst hday
          exact ⟨_, by simp [M, datesSituation, VE.FiniteModel.asStructure, hany, hc], firstIn⟩
        · exact ⟨(s, ""), by simp [M, datesSituation, VE.FiniteModel.asStructure, hany, hc, hday],
            by simp [M, datesSituation, VE.FiniteModel.asStructure, hday]⟩
    · obtain ⟨rfl, D, hD, D', hD', rfl⟩ := relBefore p zs hr
      exact ⟨[V.day, V.day], hb, dayOf D hD, dayOf D' hD', trivial⟩
  have hn : (M.domains V.day).Nodup := by
    simp only [M, datesSituation, if_true]
    refine List.Pairwise.map (R := fun a b : String => a ≠ b) _ (fun a b hne he => hne (Prod.mk.inj he).2) ?_
    unfold dayNames
    split
    · simp
    · exact List.Pairwise.map (R := fun D D' : Civil => D.num < D'.num) _ (fun a b hlt he => Nat.ne_of_lt hlt (by rw [dateName_inj he])) pw
  refine ⟨M, adm, ?_, embeddable_complete (regenEnv E V) V hT M adm hn num emb⟩
  have hc := calendar_sat (regenEnv E V) V hT _ adm num emb
  have hv := conventions_empty V M.asStructure (by
    intro p hp v w hr
    obtain ⟨rfl, -⟩ := relBefore p _ hr
    rcases List.mem_append.1 hp with hp | hp
    · exact hbr hp
    · obtain ⟨l, hm, he⟩ := List.mem_map.1 hp; exact (hl l hm).2 he)
  intro a ha
  simp only [eventsX, eventsLabelled, List.map_append, List.mem_append] at ha
  exact ha.elim (hc a) (hv a)

end VE.Events
