import VE.Presupposition.Admit

/-! # What an admitted document satisfies, step by step (helpers for the `admit_*` statements)

Each lemma reads one step of `admitWith` back from `admitWith t fx D = .ok R`, for any table `t` and fixed inputs
`fx`; `Statements.lean` instantiates them at `admit`. -/

namespace VE.Presupposition

theorem bind_ok {ε α β : Type} {x : Except ε α} {f : α → Except ε β} {b : β} (h : (x >>= f) = .ok b) :
    ∃ a, x = .ok a ∧ f a = .ok b := by
  cases x with
  | error e => exact absurd h (by simp [bind, Except.bind])
  | ok a => exact ⟨a, rfl, h⟩

theorem ensure_ok {b : Bool} {e : String} {u : Unit} (h : ensure b e = .ok u) : b = true := by
  unfold ensure at h; split at h <;> simp_all

theorem mapError_ok {α : Type} {x : Except String α} {g : String → String} {a : α} (h : x.mapError g = .ok a) :
    x = .ok a := by
  cases x <;> simp_all [Except.mapError]

theorem mapE_mem {α β : Type} {f : α → Except String β} :
    ∀ {l : List α} {l' : List β}, mapE f l = .ok l' → ∀ b ∈ l', ∃ a ∈ l, f a = .ok b
  | [], l', h, b, hb => by simp [mapE] at h; subst h; simp at hb
  | a :: as, l', h, b, hb => by
    obtain ⟨b₀, h₀, h⟩ := bind_ok h
    obtain ⟨bs, h₁, h⟩ := bind_ok h
    cases h
    rcases List.mem_cons.mp hb with rfl | hb
    · exact ⟨a, List.mem_cons_self .., h₀⟩
    · obtain ⟨a', ha', h'⟩ := mapE_mem h₁ b hb
      exact ⟨a', List.mem_cons_of_mem _ ha', h'⟩

theorem mapE_map {α β γ : Type} {f : α → Except String β} {g : β → γ} {g' : α → γ}
    (hf : ∀ a b, f a = .ok b → g b = g' a) : ∀ {l : List α} {l' : List β}, mapE f l = .ok l' → l'.map g = l.map g'
  | [], l', h => by simp [mapE] at h; subst h; rfl
  | a :: as, l', h => by
    obtain ⟨b₀, h₀, h⟩ := bind_ok h
    obtain ⟨bs, h₁, h⟩ := bind_ok h
    cases h
    simp only [List.map_cons, hf a b₀ h₀, mapE_map hf h₁]

theorem allE_ok {α : Type} {f : α → Except String Unit} :
    ∀ {l : List α}, allE f l = .ok () → ∀ a ∈ l, f a = .ok ()
  | [], _, a, ha => by simp at ha
  | x :: xs, h, a, ha => by
    obtain ⟨u, h₀, h⟩ := bind_ok h
    rcases List.mem_cons.mp ha with rfl | ha
    · exact h₀
    · exact allE_ok h a ha

/-- `admitWith`'s steps, read back from an admitted document. -/
theorem admitWith_ok {t : CandidateTable} {fx : Fixed} {D : PDoc} {R : Report} (h : admitWith t fx D = .ok R) :
    ∃ obs P, D.block = some obs ∧ checkIds D [] obs = .ok () ∧ bases3 D obs = .ok P ∧
      R.bases = basesOf P ∧ R.baseTree = baseTreeOf D P ∧
      mapE (fun o => do let c ← regen D obs P (baseTreeOf D P) o; carrierOk t D (baseTreeOf D P) c; pure c) obs =
        .ok R.checked ∧
      allE (openOk t D R) R.checked = .ok () ∧ unitsOk fx D obs R = .ok () := by
  unfold admitWith at h
  split at h
  · cases h
  · rename_i obs hb
    obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨_, hi, h⟩ := bind_ok h
    obtain ⟨P, hP, h⟩ := bind_ok h
    obtain ⟨cs, hc, h⟩ := bind_ok h
    obtain ⟨_, ho, h⟩ := bind_ok h
    obtain ⟨_, hu, h⟩ := bind_ok h
    cases h
    exact ⟨obs, P, hb, hi, hP, rfl, rfl, hc, ho, hu⟩

/-- What pass 1's regeneration gives at each kind of position. -/
theorem regen_ok {D : PDoc} {obs : List Obligation} {P : List (DocUnit × Base)} {T : VE.Norms.Tree}
    {o : Obligation} {c : Checked} (h : regen D obs P T o = .ok c) :
    c.ob = o ∧
    (∀ p, o.position = .path p → ∃ B f s r, (P.find? (·.1.id == o.unit)).map (·.2) = some (.claim B) ∧
      Frame.locate B p = some (f, s) ∧
      obs.all (fun d => d.unit != o.unit || match d.position with
        | .path q => !entersRestriction d.row q p | _ => true) = true ∧
      buildReading o.row f.binders.length o.args.tuple = .ok r ∧ s = r.strong ∧
      c = ⟨o, f, r.pre, some r, f.goal r.pre, f.cls⟩) ∧
    (∀ n, o.position = .ruleAct n → ∃ N r pre, T.nodes.find? (·.name == n) = some N ∧
      D.norms.regulated.find? (·.name == N.pred) = some r ∧ buildPre o.row r.sorts.length o.args.tuple = .ok pre ∧
      c = ⟨o, .hole, pre, none, ruleGoal r N pre, .ruleAct⟩) ∧
    (o.position = .heading → ∃ B pre, (P.find? (·.1.id == o.unit)).map (·.2) = some (.claim B) ∧
      buildPre o.row 0 o.args.tuple = .ok pre ∧ c = ⟨o, .hole, pre, none, pre, .top⟩) := by
  unfold regen at h
  split at h
  · rename_i p B hpos hB
    split at h
    · rename_i f s hl
      obtain ⟨_, he, h⟩ := bind_ok h
      obtain ⟨r, hr, h⟩ := bind_ok h
      obtain ⟨_, hs, h⟩ := bind_ok h
      obtain ⟨_, _, h⟩ := bind_ok h
      cases h
      refine ⟨rfl, fun p' hp' => ?_, fun n hn => by simp_all, fun hn => by simp_all⟩
      rw [hpos] at hp'; cases hp'
      exact ⟨B, f, s, r, hB, hl, ensure_ok he, mapError_ok hr, by simpa using ensure_ok hs, rfl⟩
    · cases h
  · rename_i n N₀ hpos hN
    obtain ⟨_, _, h⟩ := bind_ok h
    split at h
    · cases h
    · rename_i N hN'
      split at h
      · cases h
      · rename_i r hr
        obtain ⟨pre, hp, h⟩ := bind_ok h
        obtain ⟨_, _, h⟩ := bind_ok h
        cases h
        refine ⟨rfl, fun p hp' => by simp_all, fun n' hn' => ?_, fun hn => by simp_all⟩
        rw [hpos] at hn'; cases hn'
        exact ⟨N, r, pre, hN', hr, mapError_ok hp, rfl⟩
  · rename_i B hpos hB
    obtain ⟨pre, hp, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    cases h
    exact ⟨rfl, fun p hp' => by simp_all, fun n hn => by simp_all, fun _ => ⟨B, pre, hB, mapError_ok hp, rfl⟩⟩
  · cases h

/-- What pass 1's carrier check gives. -/
theorem carrierOk_ok {t : CandidateTable} {D : PDoc} {T : VE.Norms.Tree} {c : Checked}
    (h : carrierOk t D T c = .ok ()) :
    (∀ n, c.ob.carrier = .proved n → provedOk D c n = true) ∧
    (∀ u, c.ob.carrier = .assumed u → unitAsserted D u = true ∧ unitContent D u = some c.goal ∧
      (c.ob.position ≠ .heading → u ≠ c.ob.unit)) ∧
    (∀ u, c.ob.carrier = .unconditional u → unitAsserted D u = true ∧
      unitContent D u = some (c.frame.close c.pre)) ∧
    (c.ob.position = .heading → (∃ n, c.ob.carrier = .proved n) ∨ (∃ u, c.ob.carrier = .assumed u)) ∧
    (∀ n, c.ob.position = .ruleAct n → needsUnspec t c.ob = true →
      ∃ N ∈ T.nodes, N.name = n ∧ N.pred ∈ D.unspec) ∧
    (∀ k, c.ob.carrier.cand = some k → c.ob.position ≠ .heading → carrierAllowed t c k = true) ∧
    (c.ob.carrier = .unresolved → (unitReadings D c.ob.unit).isSome = true) := by
  unfold carrierOk at h
  obtain ⟨_, h₁, h⟩ := bind_ok h
  obtain ⟨_, h₂, h⟩ := bind_ok h
  obtain ⟨_, h₃, h⟩ := bind_ok h
  obtain ⟨_, h₄, h⟩ := bind_ok h
  obtain ⟨_, h₅, h₆⟩ := bind_ok h
  have e₁ := ensure_ok h₁; have e₂ := ensure_ok h₂; have e₃ := ensure_ok h₃
  have e₄ := ensure_ok h₄; have e₅ := ensure_ok h₅; have e₆ := ensure_ok h₆
  refine ⟨fun n hn => ?_, fun u hu => ?_, fun u hu => ?_, fun hp => ?_, fun n hn hu => ?_, fun k hk hp => ?_,
    fun hu => ?_⟩
  · simpa [hn] using e₁
  · simp only [hu, Bool.and_eq_true, beq_iff_eq, Bool.or_eq_true, bne_iff_ne, ne_eq] at e₂
    exact ⟨e₂.1.1, e₂.1.2, fun hp => e₂.2.resolve_left hp⟩
  · simp only [hu, Bool.and_eq_true, beq_iff_eq, bne_iff_ne, ne_eq] at e₂
    exact ⟨e₂.1.1, e₂.1.2⟩
  · rw [hp] at e₃
    revert e₃; cases c.ob.carrier <;> simp
  · simp only [hn, hu, Bool.not_true, Bool.false_or, List.any_eq_true, Bool.and_eq_true, beq_iff_eq,
      List.contains_iff_mem] at e₄
    exact e₄
  · simpa [hk, hp] using e₅
  · simpa [hu] using e₆

/-- Pass 1: every checked obligation is regenerated from one of the block's and passed its carrier check. -/
theorem pass1_mem {t : CandidateTable} {D : PDoc} {obs : List Obligation} {P : List (DocUnit × Base)}
    {cs : List Checked}
    (h : mapE (fun o => do let c ← regen D obs P (baseTreeOf D P) o; carrierOk t D (baseTreeOf D P) c; pure c) obs =
      .ok cs) {c : Checked} (hc : c ∈ cs) :
    ∃ o ∈ obs, regen D obs P (baseTreeOf D P) o = .ok c ∧ carrierOk t D (baseTreeOf D P) c = .ok () := by
  obtain ⟨o, ho, h⟩ := mapE_mem h c hc
  obtain ⟨c', h₁, h⟩ := bind_ok h
  obtain ⟨_, h₂, h⟩ := bind_ok h
  cases h
  exact ⟨o, ho, h₁, h₂⟩

theorem pass1_obs {t : CandidateTable} {D : PDoc} {obs : List Obligation} {P : List (DocUnit × Base)}
    {cs : List Checked}
    (h : mapE (fun o => do let c ← regen D obs P (baseTreeOf D P) o; carrierOk t D (baseTreeOf D P) c; pure c) obs =
      .ok cs) : cs.map (·.ob) = obs := by
  have := mapE_map (g := (·.ob)) (g' := id) (fun o c h => by
    obtain ⟨c', h₁, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    cases h
    exact (regen_ok h₁).1) h
  simpa using this

/-- Step 2: the block's ids are distinct. -/
theorem checkIds_nodup {D : PDoc} : ∀ {seen : List String} {obs : List Obligation}, checkIds D seen obs = .ok () →
    (obs.map (·.id)).Nodup ∧ ∀ o ∈ obs, o.id ∉ seen
  | _, [], _ => by simp
  | seen, o :: os, h => by
    unfold checkIds at h
    obtain ⟨_, h₁, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    have e₁ := ensure_ok h₁
    obtain ⟨hn, hs⟩ := checkIds_nodup h
    replace e₁ : o.id ∉ seen := by simpa using e₁
    refine ⟨List.nodup_cons.mpr ⟨fun hm => ?_, hn⟩, fun o' ho' => ?_⟩
    · obtain ⟨o', ho', he⟩ := List.mem_map.mp hm
      exact hs o' ho' (List.mem_cons.mpr (.inl he))
    · rcases List.mem_cons.mp ho' with rfl | ho'
      · exact e₁
      · exact fun hm => hs o' ho' (List.mem_cons_of_mem _ hm)

/-- Step 3: each entry is the first unit of its id with its base. -/
theorem bases3_mem {D : PDoc} {obs : List Obligation} {P : List (DocUnit × Base)} (h : bases3 D obs = .ok P)
    {x : DocUnit × Base} (hx : x ∈ P) : unitOf D x.1.id = some x.1 ∧ baseOf D obs x.1 = some x.2 := by
  obtain ⟨a, ha, h⟩ := mapE_mem h x hx
  split at h
  · rename_i b hb
    cases h
    simp only [withObligations, List.mem_filter, Bool.and_eq_true, beq_iff_eq] at ha
    exact ⟨ha.2.2, hb⟩
  · cases h

theorem mem_basesOf {P : List (DocUnit × Base)} {u : String} {B : VE.Formula} :
    (u, B) ∈ basesOf P ↔ ∃ x ∈ P, x.1.id = u ∧ x.2 = .claim B := by
  simp only [basesOf, List.mem_filterMap]
  constructor
  · rintro ⟨x, hx, he⟩
    split at he
    · rename_i B' hB; cases he; exact ⟨x, hx, rfl, hB⟩
    · cases he
  · rintro ⟨x, hx, rfl, hB⟩
    exact ⟨x, hx, by simp [hB]⟩

/-- A unit has one base content. -/
theorem bases_unique {D : PDoc} {obs : List Obligation} {P : List (DocUnit × Base)} (h : bases3 D obs = .ok P)
    {u : String} {B₁ B₂ : VE.Formula} (h₁ : (u, B₁) ∈ basesOf P) (h₂ : (u, B₂) ∈ basesOf P) : B₁ = B₂ := by
  obtain ⟨x₁, hx₁, hu₁, hb₁⟩ := mem_basesOf.mp h₁
  obtain ⟨x₂, hx₂, hu₂, hb₂⟩ := mem_basesOf.mp h₂
  obtain ⟨hU₁, hB₁⟩ := bases3_mem h hx₁
  obtain ⟨hU₂, hB₂⟩ := bases3_mem h hx₂
  rw [hu₁] at hU₁; rw [hu₂] at hU₂
  have : x₁.1 = x₂.1 := Option.some.inj (hU₁.symm.trans hU₂)
  rw [this, hB₂, hb₁, hb₂] at hB₁
  exact (Base.claim.inj (Option.some.inj hB₁)).symm

theorem find_base {P : List (DocUnit × Base)} {u : String} {B : VE.Formula}
    (h : (P.find? (·.1.id == u)).map (·.2) = some (.claim B)) : (u, B) ∈ basesOf P := by
  obtain ⟨x, hx, he⟩ := Option.map_eq_some_iff.mp h
  exact mem_basesOf.mpr ⟨x, List.mem_of_find?_eq_some hx, by simpa using List.find?_some hx, he⟩

/-- Pass 2, for an unresolved obligation. -/
theorem openOk_ok {t : CandidateTable} {D : PDoc} {R : Report} {c : Checked} (h : openOk t D R c = .ok ())
    (hu : c.ob.carrier = .unresolved) :
    (∃ rs, expectedReadings t R c = some rs ∧ unitReadings D c.ob.unit = some rs ∧ 2 ≤ rs.length) ∧
    (R.checked.find? (fun d => d.ob.unit == c.ob.unit && d.ob.carrier == .unresolved)).map (·.ob.id) =
      some c.ob.id := by
  unfold openOk at h
  simp only [hu, beq_self_eq_true, if_true] at h
  have e := ensure_ok h
  simp only [Bool.and_eq_true, beq_iff_eq] at e
  refine ⟨?_, e.2⟩
  have e1 := e.1
  split at e1
  · rename_i rs hrs
    simp only [Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at e1
    exact ⟨rs, hrs, e1⟩
  · cases e1

/-- Step 5's contents and rules. -/
theorem unitsOk_ok {fx : Fixed} {D : PDoc} {obs : List Obligation} {R : Report} (h : unitsOk fx D obs R = .ok ()) :
    (∀ x ∈ R.bases, R.checked.any (fun c => c.ob.unit == x.1 && c.ob.carrier == .unresolved) = true ∨
      unitContent D x.1 = some (carried (unitModes R x.1) x.2)) ∧
    (∀ N ∈ R.baseTree.nodes, ∀ M ∈ D.norms.nodes, M.name = N.name →
      M = (ruleConditions R N.name).foldl conditionNode N) ∧
    VE.Norms.WellFormed ⟨D.E, D.lits, D.norms⟩ = true ∧ VE.Norms.WellFormed ⟨D.E, D.lits, R.baseTree⟩ = true := by
  unfold unitsOk at h
  obtain ⟨_, h₁, h⟩ := bind_ok h
  obtain ⟨_, h₂, h⟩ := bind_ok h
  obtain ⟨_, h₃, _⟩ := bind_ok h
  have e₃ := ensure_ok h₃
  simp only [Bool.and_eq_true] at e₃
  refine ⟨fun x hx => ?_, fun N hN M hM he => ?_, e₃⟩
  · obtain ⟨_, _, h⟩ := bind_ok (allE_ok h₁ x hx)
    simpa [Bool.or_eq_true] using ensure_ok h
  · have := ensure_ok (allE_ok h₂ N hN)
    simp only [List.all_eq_true, Bool.or_eq_true, bne_iff_ne, ne_eq, beq_iff_eq] at this
    exact (this M hM).resolve_left (fun hn => hn he)

end VE.Presupposition
