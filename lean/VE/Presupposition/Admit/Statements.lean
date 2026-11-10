import VE.Presupposition.Admit.Facts

/-! # Spec 4.7's statements on `admit` (docs/spec/presupposition.md 4.7, "**Statements.**")

Each statement is the spec's text; its proof reads the step it names back with `Facts.lean`. -/

namespace VE.Presupposition
universe u

/-- The checked obligation `c` of an admitted document: pass 1 regenerated it from one of the block's. -/
theorem admit_pass1 {t : CandidateTable} {fx : Fixed} {D : PDoc} {R : Report} (h : admitWith t fx D = .ok R)
    {c : Checked} (hc : c ∈ R.checked) :
    ∃ obs P o, D.block = some obs ∧ bases3 D obs = .ok P ∧ R.bases = basesOf P ∧ R.baseTree = baseTreeOf D P ∧
      regen D obs P (baseTreeOf D P) o = .ok c ∧ carrierOk t D (baseTreeOf D P) c = .ok () ∧
      c.ob = o := by
  obtain ⟨obs, P, hb, _, hP, hB, hT, hc', _, _⟩ := admitWith_ok h
  obtain ⟨o, _, hr, hk⟩ := pass1_mem hc' hc
  exact ⟨obs, P, o, hb, hP, hB, hT, hr, hk, (regen_ok hr).1⟩

theorem admitWith_regenerates {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) :
    D.block = some (R.checked.map (·.ob)) := by
  obtain ⟨obs, P, hb, _, _, _, _, hc, _, _⟩ := admitWith_ok h
  rw [hb, pass1_obs hc]

theorem admit_regenerates (D : PDoc) (R : Report) (h : admit D = .ok R) :
    D.block = some (R.checked.map (·.ob)) :=
  admitWith_regenerates (t := candidateTable) (fx := admitInputs) D R h

theorem admitWith_goals_from_base {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (p : List Nat) (hp : c.ob.position = .path p) :
    ∃ B r, (c.ob.unit, B) ∈ R.bases ∧ c.reading = some r ∧ Frame.locate B p = some (c.frame, r.strong) ∧
      buildReading c.ob.row c.frame.binders.length c.ob.args.tuple = .ok r ∧
      c.pre = r.pre ∧ c.goal = c.frame.goal r.pre ∧ c.pos = c.frame.cls := by
  obtain ⟨obs, P, o, _, _, hB, _, hr, _, ho⟩ := admit_pass1 h hc
  obtain ⟨B, f, s, r, hf, hl, _, hb, hs, he⟩ := (regen_ok hr).2.1 p (ho ▸ hp)
  subst hs he
  exact ⟨B, r, hB ▸ find_base hf, rfl, hl, hb, rfl, rfl, rfl⟩

theorem admit_goals_from_base (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (p : List Nat) (hp : c.ob.position = .path p) :
    ∃ B r, (c.ob.unit, B) ∈ R.bases ∧ c.reading = some r ∧ Frame.locate B p = some (c.frame, r.strong) ∧
      buildReading c.ob.row c.frame.binders.length c.ob.args.tuple = .ok r ∧
      c.pre = r.pre ∧ c.goal = c.frame.goal r.pre ∧ c.pos = c.frame.cls :=
  admitWith_goals_from_base (t := candidateTable) (fx := admitInputs) D R h c hc p hp

theorem buildPre_body {row : String} {n : Nat} {a : Option String × Option VE.Formula × Option VE.Formula ×
    Option VE.Formula} {p : VE.Formula} (h : buildPre row n a = .ok p) : a.2.2.1 = none := by
  unfold buildPre at h
  split at h <;> simp_all

theorem admitWith_rule_goal {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (n : String) (hp : c.ob.position = .ruleAct n) :
    ∃ N ∈ R.baseTree.nodes, N.name = n ∧ ∃ r ∈ D.norms.regulated, r.name = N.pred ∧
      buildPre c.ob.row r.sorts.length c.ob.args.tuple = .ok c.pre ∧ c.goal = ruleGoal r N c.pre ∧
      c.pos = .ruleAct ∧ c.ob.args.body = none := by
  obtain ⟨obs, P, o, _, _, _, hT, hr, _, ho⟩ := admit_pass1 h hc
  obtain ⟨N, r, pre, hN, hR, hpre, he⟩ := (regen_ok hr).2.2.1 n (ho ▸ hp)
  subst he
  refine ⟨N, hT ▸ List.mem_of_find?_eq_some hN, by simpa using List.find?_some hN, r,
    List.mem_of_find?_eq_some hR, by simpa using (List.find?_some hR).symm, hpre, rfl, rfl, ?_⟩
  exact buildPre_body hpre

theorem admit_rule_goal (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (n : String) (hp : c.ob.position = .ruleAct n) :
    ∃ N ∈ R.baseTree.nodes, N.name = n ∧ ∃ r ∈ D.norms.regulated, r.name = N.pred ∧
      buildPre c.ob.row r.sorts.length c.ob.args.tuple = .ok c.pre ∧ c.goal = ruleGoal r N c.pre ∧
      c.pos = .ruleAct ∧ c.ob.args.body = none :=
  admitWith_rule_goal (t := candidateTable) (fx := admitInputs) D R h c hc n hp

/-- R-10: a heading's goal is its `pre` over the empty context; no body; only proved or assumed. -/
theorem admitWith_heading_goal {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (hp : c.ob.position = .heading) :
    buildPre c.ob.row 0 c.ob.args.tuple = .ok c.pre ∧ c.goal = c.pre ∧ c.ob.args.body = none ∧
      ((∃ n, c.ob.carrier = .proved n) ∨ (∃ u, c.ob.carrier = .assumed u)) := by
  obtain ⟨obs, P, o, _, _, _, _, hr, hk, ho⟩ := admit_pass1 h hc
  have hcar := (carrierOk_ok hk).2.2.2.1 hp
  obtain ⟨_, pre, _, hpre, he⟩ := (regen_ok hr).2.2.2.1 (ho ▸ hp)
  subst he
  exact ⟨hpre, rfl, buildPre_body hpre, hcar⟩

theorem admit_heading_goal (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (hp : c.ob.position = .heading) :
    buildPre c.ob.row 0 c.ob.args.tuple = .ok c.pre ∧ c.goal = c.pre ∧ c.ob.args.body = none ∧
      ((∃ n, c.ob.carrier = .proved n) ∨ (∃ u, c.ob.carrier = .assumed u)) :=
  admitWith_heading_goal (t := candidateTable) (fx := admitInputs) D R h c hc hp

/-- R-D6: no admitted path enters the restriction of another obligation of its unit. -/
theorem admitWith_outside_restrictions {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c d : Checked)
    (hc : c ∈ R.checked) (hd : d ∈ R.checked) (hu : c.ob.unit = d.ob.unit) (p q : List Nat)
    (hp : c.ob.position = .path p) (hq : d.ob.position = .path q) :
    entersRestriction c.ob.row p q = false := by
  obtain ⟨obs, P, o, hb, _, _, _, hr, _, ho⟩ := admit_pass1 h hd
  obtain ⟨_, _, _, _, _, _, hall, _⟩ := (regen_ok hr).2.1 q (ho ▸ hq)
  rw [← ho] at hall
  have hmem : c.ob ∈ obs := by
    have := admitWith_regenerates D R h
    rw [hb] at this
    rw [Option.some.inj this]
    exact List.mem_map_of_mem hc
  have := List.all_eq_true.mp hall c.ob hmem
  simp only [hu, bne_self_eq_false, Bool.false_or, hp, Bool.not_eq_true'] at this
  exact this

theorem admit_outside_restrictions (D : PDoc) (R : Report) (h : admit D = .ok R) (c d : Checked)
    (hc : c ∈ R.checked) (hd : d ∈ R.checked) (hu : c.ob.unit = d.ob.unit) (p q : List Nat)
    (hp : c.ob.position = .path p) (hq : d.ob.position = .path q) :
    entersRestriction c.ob.row p q = false :=
  admitWith_outside_restrictions (t := candidateTable) (fx := admitInputs) D R h c d hc hd hu p q hp hq

theorem admitWith_claim_content {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (x : String × VE.Formula)
    (hx : x ∈ R.bases) (hres : ∀ c ∈ R.checked, c.ob.unit = x.1 → c.ob.carrier ≠ .unresolved) :
    unitContent D x.1 = some (carried (unitModes R x.1) x.2) := by
  obtain ⟨_, _, _, _, _, _, _, _, _, hu, _⟩ := admitWith_ok h
  refine ((unitsOk_ok hu).1 x hx).resolve_left fun ha => ?_
  obtain ⟨c, hc, he⟩ := List.any_eq_true.mp ha
  simp only [Bool.and_eq_true, beq_iff_eq] at he
  exact hres c hc he.1 he.2

theorem admit_claim_content (D : PDoc) (R : Report) (h : admit D = .ok R) (x : String × VE.Formula)
    (hx : x ∈ R.bases) (hres : ∀ c ∈ R.checked, c.ob.unit = x.1 → c.ob.carrier ≠ .unresolved) :
    unitContent D x.1 = some (carried (unitModes R x.1) x.2) :=
  admitWith_claim_content (t := candidateTable) (fx := admitInputs) D R h x hx hres

theorem admitWith_rule_content {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) :
    VE.Norms.WellFormed ⟨D.E, D.lits, D.norms⟩ = true ∧ VE.Norms.WellFormed ⟨D.E, D.lits, R.baseTree⟩ = true ∧
    ∀ N ∈ R.baseTree.nodes, ∀ M ∈ D.norms.nodes, M.name = N.name →
      M = (ruleConditions R N.name).foldl conditionNode N := by
  obtain ⟨_, _, _, _, _, _, _, _, _, hu, _⟩ := admitWith_ok h
  obtain ⟨_, hrules, hw₁, hw₂, _⟩ := unitsOk_ok hu
  exact ⟨hw₁, hw₂, hrules⟩

theorem admit_rule_content (D : PDoc) (R : Report) (h : admit D = .ok R) :
    VE.Norms.WellFormed ⟨D.E, D.lits, D.norms⟩ = true ∧ VE.Norms.WellFormed ⟨D.E, D.lits, R.baseTree⟩ = true ∧
    ∀ N ∈ R.baseTree.nodes, ∀ M ∈ D.norms.nodes, M.name = N.name →
      M = (ruleConditions R N.name).foldl conditionNode N :=
  admitWith_rule_content (t := candidateTable) (fx := admitInputs) D R h

theorem admitWith_proved_sound {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (n : String) (hp : c.ob.carrier = .proved n) :
    ∃ cert, nodeCertificate D n = some cert ∧
      VE.Tableau.checkCertificate (env D) (premisesBefore D c.ob.unit) c.goal cert = true := by
  obtain ⟨_, _, _, _, _, _, _, _, hk, _⟩ := admit_pass1 h hc
  have := (carrierOk_ok hk).1 n hp
  unfold provedOk at this
  split at this
  · rename_i cert hcert; exact ⟨cert, hcert, this⟩
  · cases this

theorem admit_proved_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (n : String) (hp : c.ob.carrier = .proved n) :
    ∃ cert, nodeCertificate D n = some cert ∧
      VE.Tableau.checkCertificate (env D) (premisesBefore D c.ob.unit) c.goal cert = true :=
  admitWith_proved_sound (t := candidateTable) (fx := admitInputs) D R h c hc n hp

/-- R-D5: the assumed unit is the obligation's own only at a heading. -/
theorem admitWith_assumed_sound {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (u : String) (hp : c.ob.carrier = .assumed u) :
    unitAsserted D u = true ∧ unitContent D u = some c.goal ∧ (c.ob.position ≠ .heading → u ≠ c.ob.unit) := by
  obtain ⟨_, _, _, _, _, _, _, _, hk, _⟩ := admit_pass1 h hc
  exact (carrierOk_ok hk).2.1 u hp

theorem admit_assumed_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (u : String) (hp : c.ob.carrier = .assumed u) :
    unitAsserted D u = true ∧ unitContent D u = some c.goal ∧ (c.ob.position ≠ .heading → u ≠ c.ob.unit) :=
  admitWith_assumed_sound (t := candidateTable) (fx := admitInputs) D R h c hc u hp

theorem admitWith_unconditional_sound {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (u : String) (hp : c.ob.carrier = .unconditional u) :
    unitAsserted D u = true ∧ unitContent D u = some (c.frame.close c.pre) := by
  obtain ⟨_, _, _, _, _, _, _, _, hk, _⟩ := admit_pass1 h hc
  exact (carrierOk_ok hk).2.2.1 u hp

theorem admit_unconditional_sound (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (u : String) (hp : c.ob.carrier = .unconditional u) :
    unitAsserted D u = true ∧ unitContent D u = some (c.frame.close c.pre) :=
  admitWith_unconditional_sound (t := candidateTable) (fx := admitInputs) D R h c hc u hp

/-- R-7: also an unresolved rule obligation whose cell lists conditioned. -/
theorem admitWith_conditioned_rule_unspecified {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (n : String) (hpos : c.ob.position = .ruleAct n)
    (hcar : c.ob.carrier = .conditioned ∨
      (c.ob.carrier = .unresolved ∧ Candidate.conditioned ∈ t c.ob.row .ruleAct)) :
    ∃ N ∈ R.baseTree.nodes, N.name = n ∧ N.pred ∈ D.unspec := by
  obtain ⟨_, _, _, _, _, _, hT, _, hk, _⟩ := admit_pass1 h hc
  rw [hT]
  refine (carrierOk_ok hk).2.2.2.2.1 n hpos ?_
  unfold needsUnspec
  rcases hcar with hcar | ⟨hcar, hm⟩
  · simp [hcar]
  · simp [hcar, hm]

theorem admit_conditioned_rule_unspecified (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (n : String) (hpos : c.ob.position = .ruleAct n)
    (hcar : c.ob.carrier = .conditioned ∨
      (c.ob.carrier = .unresolved ∧ Candidate.conditioned ∈ candidateTable c.ob.row .ruleAct)) :
    ∃ N ∈ R.baseTree.nodes, N.name = n ∧ N.pred ∈ D.unspec :=
  admitWith_conditioned_rule_unspecified (t := candidateTable) (fx := admitInputs) D R h c hc n hpos hcar

/-- R-D1, R-10: a recorded carrier is in the cell, and in place only at a shallow frame; headings excepted. -/
theorem admitWith_carrier_candidate {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hpos : c.ob.position ≠ .heading) (k : Candidate) (hk : c.ob.carrier.cand = some k) :
    k ∈ t c.ob.row c.pos ∧ (k = .inPlace → c.frame.shallow) := by
  obtain ⟨_, _, _, _, _, _, _, _, hok, _⟩ := admit_pass1 h hc
  have := (carrierOk_ok hok).2.2.2.2.2.1 k hk hpos
  simp only [carrierAllowed, Bool.and_eq_true, List.contains_iff_mem, Bool.or_eq_true, bne_iff_ne, ne_eq,
    decide_eq_true_eq] at this
  exact ⟨this.1, fun hi => this.2.resolve_left (not_not_intro hi)⟩

theorem admit_carrier_candidate (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hpos : c.ob.position ≠ .heading) (k : Candidate) (hk : c.ob.carrier.cand = some k) :
    k ∈ candidateTable c.ob.row c.pos ∧ (k = .inPlace → c.frame.shallow) :=
  admitWith_carrier_candidate (t := candidateTable) (fx := admitInputs) D R h c hc hpos k hk

/-- R-6, R-D3: exactly the expected readings, at least two of them; no UNFORMALISED escape. -/
theorem admitWith_unresolved_readings {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hu : c.ob.carrier = .unresolved) :
    unitReadings D c.ob.unit = expectedReadings t R c ∧
      ∃ rs, expectedReadings t R c = some rs ∧ 2 ≤ rs.length := by
  obtain ⟨_, _, _, _, _, _, _, _, ho, _⟩ := admitWith_ok h
  obtain ⟨⟨rs, he, hr, hl⟩, _⟩ := openOk_ok (allE_ok ho c hc) hu
  exact ⟨hr.trans he.symm, rs, he, hl⟩

theorem admit_unresolved_readings (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hu : c.ob.carrier = .unresolved) :
    unitReadings D c.ob.unit = expectedReadings candidateTable R c ∧
      ∃ rs, expectedReadings candidateTable R c = some rs ∧ 2 ≤ rs.length :=
  admitWith_unresolved_readings (t := candidateTable) (fx := admitInputs) D R h c hc hu

/-- R-6: under the empty table no checked obligation is unresolved. -/
theorem admitWith_empty_table {t : CandidateTable} {fx : Fixed}
    (hT : ∀ row pc, t row pc = []) (D : PDoc) (R : Report)
    (h : admitWith t fx D = .ok R) (c : Checked) (hc : c ∈ R.checked) : c.ob.carrier ≠ .unresolved := by
  intro hu
  obtain ⟨_, rs, he, hl⟩ := admitWith_unresolved_readings D R h c hc hu
  have hem : emitted t c = [] := by simp [emitted, hT]
  unfold expectedReadings at he
  rw [hem] at he
  split at he
  · obtain ⟨_, _, rfl⟩ := Option.map_eq_some_iff.mp he; simp at hl
  · obtain ⟨_, _, rfl⟩ := Option.map_eq_some_iff.mp he; simp at hl
  · cases he

theorem admit_empty_table (hT : ∀ row pc, candidateTable row pc = []) (D : PDoc) (R : Report)
    (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked) : c.ob.carrier ≠ .unresolved :=
  admitWith_empty_table (t := candidateTable) (fx := admitInputs) hT D R h c hc

/-- The id of `c` occurs once among the checked obligations. -/
theorem admit_ids_nodup {t : CandidateTable} {fx : Fixed} {D : PDoc} {R : Report} (h : admitWith t fx D = .ok R) : (R.checked.map (·.ob.id)).Nodup := by
  obtain ⟨obs, P, hb, hi, _, _, _, hc, _, _⟩ := admitWith_ok h
  have := (checkIds_nodup hi).1
  rw [← pass1_obs hc, List.map_map] at this
  exact this

/-- R-D2 over `claimReading`: at a shallow frame, in place and conditioned have the same content denotation for the
    whole unit, and neither has a premise. The alias of `aliasesOf` is attached exactly where this applies. -/
theorem admitWith_inPlace_alias {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (p : List Nat) (hp : c.ob.position = .path p) (hs : c.frame.shallow) (B : VE.Formula)
    (hB : (c.ob.unit, B) ∈ R.bases) (r : Reading) (hr : c.reading = some r)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hpre : ∀ τ, c.frame.Reach S ρ τ → r.strong.denote S τ → r.pre.denote S τ) :
    (∃ a a', (claimReading R c B .inPlace).content = .claim a ∧
      (claimReading R c B .conditioned).content = .claim a' ∧ (a.denote S ρ ↔ a'.denote S ρ)) ∧
    (claimReading R c B .inPlace).premise = none ∧ (claimReading R c B .conditioned).premise = none := by
  refine ⟨?_, rfl, rfl⟩
  obtain ⟨B', r', hB', hr', hl, _, _, hg, _⟩ := admitWith_goals_from_base D R h c hc p hp
  rw [hr] at hr'; cases hr'
  have hBB : B = c.frame.plug r.strong := by
    obtain ⟨_, P, _, _, hP, hbs, _, _, _, _⟩ := admit_pass1 h hc
    rw [hbs] at hB hB'
    rw [bases_unique hP hB hB', locate_plug _ _ _ _ hl]
  -- the unit's obligations around `c`: `c` occurs once (ids are distinct)
  have hmem : c ∈ R.checked.filter (fun d => d.ob.unit == c.ob.unit) := List.mem_filter.mpr ⟨hc, by simp⟩
  obtain ⟨l₁, l₂, hsplit⟩ := List.append_of_mem hmem
  have hnd : ((R.checked.filter (fun d => d.ob.unit == c.ob.unit)).map (·.ob.id)).Nodup :=
    (List.Nodup.sublist (List.Sublist.map _ List.filter_sublist) (admit_ids_nodup h))
  rw [hsplit, List.map_append, List.map_cons, List.nodup_append] at hnd
  have hn₁ : ∀ d ∈ l₁, d.ob.id ≠ c.ob.id := fun d hd he =>
    hnd.2.2 _ (List.mem_map_of_mem hd) _ (List.mem_cons_self ..) he
  have hn₂ : ∀ d ∈ l₂, d.ob.id ≠ c.ob.id := fun d hd he =>
    (List.nodup_cons.mp hnd.2.1).1 (he ▸ List.mem_map_of_mem hd)
  let M (l : List Checked) := l.map (fun d => (d.ob.carrier.root, d.goal))
  have hms : ∀ k : Candidate, (R.checked.filter (fun d => d.ob.unit == c.ob.unit)).map (fun d =>
      (if d.ob.id == c.ob.id then k.root else d.ob.carrier.root, d.goal)) = M l₁ ++ (k.root, c.goal) :: M l₂ := by
    intro k
    rw [hsplit, List.map_append, List.map_cons]
    simp only [beq_self_eq_true, if_true, M]
    congr 1
    · exact List.map_congr_left (fun d hd => by simp [hn₁ d hd])
    · exact congrArg _ (List.map_congr_left (fun d hd => by simp [hn₂ d hd]))
  refine ⟨carried (M l₁ ++ (.bare, c.goal) :: M l₂) B, carried (M l₁ ++ (.conditioned, c.goal) :: M l₂) B,
    by simp only [claimReading, hms]; rfl, by simp only [claimReading, hms]; rfl, ?_⟩
  rw [hBB, hg]
  exact inPlace_iff_conditioned_shallow c.frame hs r (M l₁) (M l₂) S ρ hpre

theorem admit_inPlace_alias (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked) (hc : c ∈ R.checked)
    (p : List Nat) (hp : c.ob.position = .path p) (hs : c.frame.shallow) (B : VE.Formula)
    (hB : (c.ob.unit, B) ∈ R.bases) (r : Reading) (hr : c.reading = some r)
    (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hpre : ∀ τ, c.frame.Reach S ρ τ → r.strong.denote S τ → r.pre.denote S τ) :
    (∃ a a', (claimReading R c B .inPlace).content = .claim a ∧
      (claimReading R c B .conditioned).content = .claim a' ∧ (a.denote S ρ ↔ a'.denote S ρ)) ∧
    (claimReading R c B .inPlace).premise = none ∧ (claimReading R c B .conditioned).premise = none :=
  admitWith_inPlace_alias (t := candidateTable) (fx := admitInputs) D R h c hc p hp hs B hB r hr S ρ hpre

theorem admitWith_no_silent_accommodation {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hu : c.ob.carrier = .unresolved) : unitContent D c.ob.unit = none := by
  obtain ⟨_, _, _, _, _, _, _, _, hk, _⟩ := admit_pass1 h hc
  have := (carrierOk_ok hk).2.2.2.2.2.2 hu
  unfold unitReadings at this
  unfold unitContent
  split at this <;> simp_all

theorem no_silent_accommodation (D : PDoc) (R : Report) (h : admit D = .ok R) (c : Checked)
    (hc : c ∈ R.checked) (hu : c.ob.carrier = .unresolved) : unitContent D c.ob.unit = none :=
  admitWith_no_silent_accommodation (t := candidateTable) (fx := admitInputs) D R h c hc hu

theorem admitWith_one_open_per_unit {t : CandidateTable} {fx : Fixed}
    (D : PDoc) (R : Report) (h : admitWith t fx D = .ok R) (c d : Checked)
    (hc : c ∈ R.checked) (hd : d ∈ R.checked) (hu : c.ob.unit = d.ob.unit)
    (hcu : c.ob.carrier = .unresolved) (hdu : d.ob.carrier = .unresolved) : c.ob.id = d.ob.id := by
  obtain ⟨_, _, _, _, _, _, _, _, ho, _⟩ := admitWith_ok h
  have h₁ := (openOk_ok (allE_ok ho c hc) hcu).2.1
  have h₂ := (openOk_ok (allE_ok ho d hd) hdu).2.1
  rw [hu] at h₁
  exact Option.some.inj (h₁.symm.trans h₂)

theorem one_open_per_unit (D : PDoc) (R : Report) (h : admit D = .ok R) (c d : Checked)
    (hc : c ∈ R.checked) (hd : d ∈ R.checked) (hu : c.ob.unit = d.ob.unit)
    (hcu : c.ob.carrier = .unresolved) (hdu : d.ob.carrier = .unresolved) : c.ob.id = d.ob.id :=
  admitWith_one_open_per_unit (t := candidateTable) (fx := admitInputs) D R h c d hc hd hu hcu hdu

theorem candidates_ruleAct (t : CandidateTable) (ht : tableOk rowNames t = true) (row : String)
    (hrow : row ∈ rowNames) (c : Candidate) (hc : c ∈ t row .ruleAct) : c = .assumed ∨ c = .conditioned := by
  have hcell := List.all_eq_true.mp (List.all_eq_true.mp ht row hrow) .ruleAct (by simp)
  simp only [cellOk, Bool.and_eq_true, List.all_eq_true] at hcell
  have := hcell.2 c hc
  cases c <;> simp_all

/-- PS-2a's wrapper (and PS-4's document mode) on a document without the block. -/
theorem no_block_unchanged (D : PDoc) (h : D.block = none) : admitWrapped D = admitBase D := by
  simp [admitWrapped, admitBase, h]

end VE.Presupposition
