import VE.Readings.Verdicts

/-! A document's components and the product fold (docs/spec/readings-defaults.md 1.9, 1.10, 4.5 and 6.6; plan
RD-4b).

A document whose sets carry their own vocabulary splits (`Wire.splitCase`, RD-4a) into the main document and one
document per companion set, each checked by itself (`Components`). Its meaning is the product of its components: a
reading of the document is one compatible choice per component (`CompatibleK`); it is CONFLICT-FREE when every
component's chosen document is (`ConflictFreeK`), and a situation of it is one situation per component (`ConsistentK`).

The product fold reads each component's rows (`ComponentRows`: its conflict rows and premise rows over every
compatible choice, `RowsSound`), and a query's rows in the one component its conclusion is typed in. Each verdict for
the document concludes `ConflictFreeK` of every compatible product choice (A2's gate on a reading of the whole
document, SR2): `foldK_conflict_free`, `foldK_conflict`, `foldK_consistent`, `foldK_all`, `foldK_none`, `foldK_some`.

`--under` on a component (the open gap the DRI note of 2026-10-07 gave RD-3 and its update of 2026-10-09 gave RD-4b):
the query's rows are then the compatible choices of component `k` taking `A`, so the approved statements, which take
`RowsHold N []`, say nothing of them. `foldK_all_under`, `foldK_none_under` and `foldK_some_under` take
`RowsHold N A` and conclude the same of every compatible product choice whose component `k` takes `A`
(`TakesAt`); the approved statements are their case `A = []`.

1.10's rule (`fixedDecided`, `setDecided`) is here too; the wire computes `decided_units` with it
(`ComponentsWire.lean`). -/
namespace VE.Readings
open VE.NormDefaults (EntailsU)
universe u

/-- A document's components: the main document and one document per companion set (1.9). -/
structure Components where
  main : NDoc
  parts : List (String × NDoc)
def Components.all (K : Components) : List NDoc := K.main :: K.parts.map (·.2)
def CompatibleK (K : Components) (cs : List Choice) : Prop :=
  cs.length = K.all.length ∧
    ∀ (k : Nat) (N : NDoc) (c : Choice), K.all[k]? = some N → cs[k]? = some c → Compatible N.D c
def ConflictFreeK (K : Components) (cs : List Choice) : Prop :=
  ∀ (k : Nat) (N : NDoc) (c : Choice), K.all[k]? = some N → cs[k]? = some c →
    VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
def ConsistentK (K : Components) (cs : List Choice) : Prop :=
  ∀ (k : Nat) (N : NDoc) (c : Choice), K.all[k]? = some N → cs[k]? = some c →
    ConsistentU (choiceU N c) (choiceDoc N.D c).2
/-- One component's checked rows: its conflict rows and its premise rows, over every compatible choice. -/
structure ComponentRows where
  conflicts : List (Choice × ChoiceResult)
  premises : List (Choice × ChoiceResult)
def RowsSound (K : Components) (rows : List ComponentRows) : Prop :=
  rows.length = K.all.length ∧ ∀ (k : Nat) (N : NDoc) (r : ComponentRows), K.all[k]? = some N → rows[k]? = some r →
    Covers N [] r.conflicts ∧ Covers N [] r.premises ∧ (∀ x ∈ r.conflicts, Holds.{u} N [] .bottom x.1 x.2) ∧
      ∀ x ∈ r.premises, Holds.{u} N [] .bottom x.1 x.2
/-- Every component other than `k` is CONFLICT-FREE under every reading and has a model under every compatible
    choice (`every = true`) or under some choice (`every = false`). -/
def OthersSettled (rows : List ComponentRows) (k : Nat) (every : Bool) : Prop :=
  ∀ (j : Nat) (r : ComponentRows), j ≠ k → rows[j]? = some r → foldConflict r.conflicts = .free ∧
    (if every then r.premises.all (·.2 == .model) = true else foldPremises r.premises = .model)

/-! ## `--under` on a component

The queried component's rows may be those of the compatible choices taking `A`; every other component's rows are
over all of its compatible choices (`--under` names sets of the queried component only, 4.5). -/

/-- `RowsSound` at every component but `k`, and one row list per component. -/
def RowsSoundBut (K : Components) (rows : List ComponentRows) (k : Nat) : Prop :=
  rows.length = K.all.length ∧ ∀ (j : Nat) (N : NDoc) (r : ComponentRows), j ≠ k → K.all[j]? = some N →
    rows[j]? = some r →
    Covers N [] r.conflicts ∧ Covers N [] r.premises ∧ (∀ x ∈ r.conflicts, Holds.{u} N [] .bottom x.1 x.2) ∧
      ∀ x ∈ r.premises, Holds.{u} N [] .bottom x.1 x.2
/-- A product choice whose component `k` takes every reading `A` names. -/
def TakesAt (cs : List Choice) (k : Nat) (A : Choice) : Prop := ∀ c, cs[k]? = some c → ∀ x ∈ A, x ∈ c

theorem rowsSoundBut_of (K : Components) (rows : List ComponentRows) (k : Nat) (h : RowsSound.{u} K rows) :
    RowsSoundBut.{u} K rows k :=
  ⟨h.1, fun j N r _ hN hr => h.2 j N r hN hr⟩

theorem takesAt_nil (cs : List Choice) (k : Nat) : TakesAt cs k [] := fun _ _ _ h => nomatch h

/-! ### Indices -/

theorem rows_at {K : Components} {rows : List ComponentRows} (hl : rows.length = K.all.length) {j : Nat}
    {N : NDoc} (h : K.all[j]? = some N) : ∃ r, rows[j]? = some r := by
  obtain ⟨hj, _⟩ := List.getElem?_eq_some_iff.mp h
  exact ⟨rows[j]'(hl ▸ hj), List.getElem?_eq_getElem _⟩

theorem all_at {K : Components} {rows : List ComponentRows} (hl : rows.length = K.all.length) {j : Nat}
    {r : ComponentRows} (h : rows[j]? = some r) : ∃ N, K.all[j]? = some N := by
  obtain ⟨hj, _⟩ := List.getElem?_eq_some_iff.mp h
  exact ⟨K.all[j]'(hl ▸ hj), List.getElem?_eq_getElem _⟩

/-- One element per position, each satisfying the position's property: the product choices are built so. -/
theorem exists_pointwise {α β : Type} (L : List α) (P : Nat → α → β → Prop)
    (h : ∀ (j : Nat) (a : α), L[j]? = some a → ∃ b, P j a b) :
    ∃ bs : List β, bs.length = L.length ∧ ∀ (j : Nat) (a : α) (b : β), L[j]? = some a → bs[j]? = some b → P j a b := by
  induction L generalizing P with
  | nil => exact ⟨[], rfl, fun j a b ha _ => by simp at ha⟩
  | cons a L ih =>
    obtain ⟨b0, hb0⟩ := h 0 a rfl
    obtain ⟨bs, hl, hbs⟩ := ih (fun j a b => P (j + 1) a b) (fun j a' ha => h (j + 1) a' (by simpa using ha))
    refine ⟨b0 :: bs, by simp [hl], fun j a' b ha hb => ?_⟩
    cases j with
    | zero =>
      simp only [List.getElem?_cons_zero, Option.some.injEq] at ha hb
      subst ha hb
      exact hb0
    | succ j =>
      simp only [List.getElem?_cons_succ] at ha hb
      exact hbs j a' b ha hb

/-- A product choice: at `k` the given choice `c`, elsewhere a choice with property `P`; it is compatible when each
    is. -/
theorem exists_product (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (c : Choice)
    (hc : Compatible N.D c) (P : Nat → NDoc → Choice → Prop)
    (hP : ∀ (j : Nat) (M : NDoc), j ≠ k → K.all[j]? = some M → ∃ c', Compatible M.D c' ∧ P j M c') :
    ∃ cs : List Choice, CompatibleK K cs ∧ cs[k]? = some c ∧
      ∀ (j : Nat) (M : NDoc) (c' : Choice), j ≠ k → K.all[j]? = some M → cs[j]? = some c' → P j M c' := by
  obtain ⟨cs, hl, hcs⟩ := exists_pointwise K.all
    (fun j M c' => Compatible M.D c' ∧ (j = k → c' = c) ∧ (j ≠ k → P j M c'))
    (fun j M hM => by
      by_cases hj : j = k
      · subst hj
        rw [hk] at hM
        cases hM
        exact ⟨c, hc, fun _ => rfl, fun h => absurd rfl h⟩
      · obtain ⟨c', h1, h2⟩ := hP j M hj hM
        exact ⟨c', h1, fun h => absurd h hj, fun _ => h2⟩)
  obtain ⟨hk', _⟩ := List.getElem?_eq_some_iff.mp hk
  have hck : cs[k]? = some (cs[k]'(hl ▸ hk')) := List.getElem?_eq_getElem _
  refine ⟨cs, ⟨hl, fun j M c' hM hc' => (hcs j M c' hM hc').1⟩, ?_, fun j M c' hj hM hc' => (hcs j M c' hM hc').2.2 hj⟩
  rw [hck, (hcs k N _ hk hck).2.1 rfl]

/-! ### What a component's settled rows give -/

theorem free_of_rows {N : NDoc} {r : ComponentRows} (hs : Covers N [] r.conflicts)
    (hh : ∀ x ∈ r.conflicts, Holds.{u} N [] .bottom x.1 x.2) (hf : foldConflict r.conflicts = .free) {c : Choice}
    (hc : Compatible N.D c) : VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) :=
  fold_conflict_free_sound N [] r.conflicts hs hh hf c hc (fun _ h => nomatch h)

theorem model_of_every {N : NDoc} {r : ComponentRows} (hs : Covers N [] r.premises)
    (hh : ∀ x ∈ r.premises, Holds.{u} N [] .bottom x.1 x.2) (hm : r.premises.all (·.2 == .model) = true)
    {c : Choice} (hc : Compatible N.D c) : ConsistentU (choiceU N c) (choiceDoc N.D c).2 := by
  obtain ⟨x, hx⟩ := covers_row hs hc (fun _ h => nomatch h)
  have hp := List.all_eq_true.mp hm _ hx
  simp only [beq_iff_eq] at hp
  have := hh _ hx
  simp only [hp] at this
  exact this

theorem model_of_some {N : NDoc} {r : ComponentRows} (hs : Covers N [] r.premises)
    (hh : ∀ x ∈ r.premises, Holds.{u} N [] .bottom x.1 x.2) (hm : foldPremises r.premises = .model) :
    ∃ c, Compatible N.D c ∧ ConsistentU (choiceU N c) (choiceDoc N.D c).2 := by
  obtain ⟨c, hc, _, h⟩ := fold_premises_model_sound N [] r.premises hs hh hm
  exact ⟨c, hc, h⟩

/-- `ConflictFreeK` of a compatible product choice whose component `k` takes `A`: at `k` by the gate of `k`'s own
    fold, elsewhere by the other components' CONFLICT-FREE folds. -/
theorem conflictFreeK_of (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (A : Choice)
    (rows : List ComponentRows) (hrs : RowsSoundBut.{u} K rows k) (cs : List (Choice × ChoiceResult))
    (hcc : Covers N A cs) (hrc : ∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) (hf : foldConflict cs = .free)
    (ho : ∀ (j : Nat) (r' : ComponentRows), j ≠ k → rows[j]? = some r' → foldConflict r'.conflicts = .free)
    (cs' : List Choice) (hK : CompatibleK K cs') (hA : TakesAt cs' k A) : ConflictFreeK.{u} K cs' := by
  intro j M c hM hc
  by_cases hj : j = k
  · subst hj
    rw [hk] at hM
    cases hM
    exact fold_conflict_free_sound N A cs hcc hrc hf c (hK.2 j N c hk hc) (hA c hc)
  · obtain ⟨r', hr'⟩ := rows_at hrs.1 hM
    obtain ⟨h1, _, h3, _⟩ := hrs.2 j M r' hj hM hr'
    exact free_of_rows h1 h3 (ho j r' hj hr') (hK.2 j M c hM hc)

/-! ## The product fold (6.6) -/

theorem foldK_conflict_free (K : Components) (rows : List ComponentRows) (hr : RowsSound.{u} K rows)
    (h : rows.all (fun r => foldConflict r.conflicts == .free) = true) :
  ∀ cs, CompatibleK K cs → ConflictFreeK.{u} K cs := by
  intro cs hK j N c hN hc
  obtain ⟨r, hr'⟩ := rows_at hr.1 hN
  obtain ⟨h1, _, h3, _⟩ := hr.2 j N r hN hr'
  have hf := List.all_eq_true.mp h r (List.mem_of_getElem? hr')
  simp only [beq_iff_eq] at hf
  exact free_of_rows h1 h3 hf (hK.2 j N c hN hc)

theorem foldK_conflict (K : Components) (rows : List ComponentRows) (hr : RowsSound.{u} K rows)
    (hne : ∀ (k : Nat) (N : NDoc), K.all[k]? = some N → ∃ c, Compatible N.D c)
    (h : rows.any (fun r => foldConflict r.conflicts == .conflict) = true) :
  ∃ cs, CompatibleK K cs ∧ ∃ (k : Nat) (N : NDoc) (c : Choice), K.all[k]? = some N ∧ cs[k]? = some c ∧
    ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c) := by
  obtain ⟨r, hm, hf⟩ := List.any_eq_true.mp h
  simp only [beq_iff_eq] at hf
  obtain ⟨k, hk⟩ := List.mem_iff_getElem?.mp hm
  obtain ⟨N, hN⟩ := all_at hr.1 hk
  obtain ⟨h1, _, h3, _⟩ := hr.2 k N r hN hk
  obtain ⟨c, hc, _, hw⟩ := fold_conflict_sound N [] r.conflicts h1 h3 hf
  obtain ⟨cs, hK, hck, _⟩ := exists_product K k N hN c hc (fun _ _ _ => True)
    (fun j M _ hM => by obtain ⟨c', hc'⟩ := hne j M hM; exact ⟨c', hc', trivial⟩)
  exact ⟨cs, hK, k, N, c, hN, hck, hw⟩

theorem foldK_consistent (K : Components) (rows : List ComponentRows) (hr : RowsSound.{u} K rows)
    (h : rows.all (fun r => foldPremises r.premises == .model) = true) :
  ∃ cs, CompatibleK K cs ∧ ConsistentK K cs := by
  have hm : ∀ (j : Nat) (N : NDoc), K.all[j]? = some N →
      ∃ c, Compatible N.D c ∧ ConsistentU (choiceU N c) (choiceDoc N.D c).2 := by
    intro j N hN
    obtain ⟨r, hr'⟩ := rows_at hr.1 hN
    obtain ⟨_, h2, _, h4⟩ := hr.2 j N r hN hr'
    have hf := List.all_eq_true.mp h r (List.mem_of_getElem? hr')
    simp only [beq_iff_eq] at hf
    exact model_of_some h2 h4 hf
  obtain ⟨cs, hl, hcs⟩ := exists_pointwise K.all
    (fun _ N c => Compatible N.D c ∧ ConsistentU (choiceU N c) (choiceDoc N.D c).2) hm
  exact ⟨cs, ⟨hl, fun j N c hN hc => (hcs j N c hN hc).1⟩, fun j N c hN hc => (hcs j N c hN hc).2⟩

/-- ALL for the document under `--under` on component `k`: ALL in component `k` over the compatible choices taking
    `A`, every other component CONFLICT-FREE under every compatible choice. -/
theorem foldK_all_under (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (rows : List ComponentRows) (hrs : RowsSoundBut.{u} K rows k)
    (cs r : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N A Γ φ cs r) (h : foldEntailment cs r = .all)
    (ho : ∀ (j : Nat) (r' : ComponentRows), j ≠ k → rows[j]? = some r' → foldConflict r'.conflicts = .free) :
  ∀ cs', CompatibleK K cs' → TakesAt cs' k A → ConflictFreeK.{u} K cs' ∧
    ∀ c, cs'[k]? = some c → EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ := by
  intro cs' hK hA
  obtain ⟨hf, _, _⟩ := foldEntailment_all h
  refine ⟨conflictFreeK_of K k N hk A rows hrs cs hr.1 hr.2.2.1 hf ho cs' hK hA, fun c hc => ?_⟩
  exact (fold_all_sound N A Γ φ cs r hr h c (hK.2 k N c hk hc) (hA c hc)).2

/-- NONE for the document under `--under` on component `k`: NONE in component `k`, every other component settled
    under every compatible choice. -/
theorem foldK_none_under (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (rows : List ComponentRows) (hrs : RowsSoundBut.{u} K rows k)
    (cs r : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N A Γ φ cs r) (h : foldEntailment cs r = .none)
    (ho : OthersSettled rows k true) :
  ∀ cs', CompatibleK K cs' → TakesAt cs' k A → ConflictFreeK.{u} K cs' ∧
    (∀ (j : Nat) (M : NDoc) (c : Choice), j ≠ k → K.all[j]? = some M → cs'[j]? = some c →
      ConsistentU (choiceU M c) (choiceDoc M.D c).2) ∧
    ∀ c, cs'[k]? = some c → CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ := by
  intro cs' hK hA
  obtain ⟨hf, _, _⟩ := foldEntailment_none h
  refine ⟨conflictFreeK_of K k N hk A rows hrs cs hr.1 hr.2.2.1 hf (fun j r' hj hr' => (ho j r' hj hr').1)
    cs' hK hA, fun j M c hj hM hc => ?_, fun c hc => ?_⟩
  · obtain ⟨r', hr'⟩ := rows_at hrs.1 hM
    obtain ⟨_, h2, _, h4⟩ := hrs.2 j M r' hj hM hr'
    have hm := (ho j r' hj hr').2
    simp only [if_true] at hm
    exact model_of_every h2 h4 hm (hK.2 j M c hM hc)
  · exact (fold_none_sound N A Γ φ cs r hr h c (hK.2 k N c hk hc) (hA c hc)).2

/-- SOME for the document under `--under` on component `k`: SOME in component `k`, every other component settled
    under some choice; every compatible product choice taking `A` at `k` is CONFLICT-FREE. -/
theorem foldK_some_under (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (rows : List ComponentRows) (hrs : RowsSoundBut.{u} K rows k)
    (cs r : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N A Γ φ cs r) (h : foldEntailment cs r = .some)
    (ho : OthersSettled rows k false) :
  (∀ cs', CompatibleK K cs' → TakesAt cs' k A → ConflictFreeK.{u} K cs') ∧
  (∃ cs', CompatibleK K cs' ∧ TakesAt cs' k A ∧ ∃ c, cs'[k]? = some c ∧
    EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ) ∧
  (∃ cs', CompatibleK K cs' ∧ TakesAt cs' k A ∧
    (∀ (j : Nat) (M : NDoc) (c : Choice), j ≠ k → K.all[j]? = some M → cs'[j]? = some c →
      ConsistentU (choiceU M c) (choiceDoc M.D c).2) ∧
    ∃ c, cs'[k]? = some c ∧ CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ) := by
  obtain ⟨hf, _, _⟩ := foldEntailment_some h
  obtain ⟨_, ⟨cp, hcp, hAp, hp⟩, ⟨cn, hcn, hAn, hn⟩⟩ := fold_some_sound N A Γ φ cs r hr h
  -- Every other component has a choice with a model.
  have hm : ∀ (j : Nat) (M : NDoc), j ≠ k → K.all[j]? = some M →
      ∃ c', Compatible M.D c' ∧ ConsistentU (choiceU M c') (choiceDoc M.D c').2 := by
    intro j M hj hM
    obtain ⟨r', hr'⟩ := rows_at hrs.1 hM
    obtain ⟨_, h2, _, h4⟩ := hrs.2 j M r' hj hM hr'
    have hs := (ho j r' hj hr').2
    simp only [Bool.false_eq_true, if_false] at hs
    exact model_of_some h2 h4 hs
  have htakes : ∀ (cs' : List Choice) (c : Choice), cs'[k]? = some c → (∀ x ∈ A, x ∈ c) → TakesAt cs' k A :=
    fun cs' c hc hAc c' hc' => by rw [hc] at hc'; cases hc'; exact hAc
  refine ⟨fun cs' hK hA => conflictFreeK_of K k N hk A rows hrs cs hr.1 hr.2.2.1 hf
    (fun j r' hj hr' => (ho j r' hj hr').1) cs' hK hA, ?_, ?_⟩
  · obtain ⟨cs', hK, hck, _⟩ := exists_product K k N hk cp hcp
      (fun _ M c' => ConsistentU (choiceU M c') (choiceDoc M.D c').2) hm
    exact ⟨cs', hK, htakes cs' cp hck hAp, cp, hck, hp⟩
  · obtain ⟨cs', hK, hck, hoth⟩ := exists_product K k N hk cn hcn
      (fun _ M c' => ConsistentU (choiceU M c') (choiceDoc M.D c').2) hm
    exact ⟨cs', hK, htakes cs' cn hck hAn, hoth, cn, hck, hn⟩

/-- ALL for the document: ALL in component `k`, every other component CONFLICT-FREE under every compatible choice
    (A2's gate on a reading of the whole document; SR2). -/
theorem foldK_all (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (Γ : List VE.Formula)
    (φ : VE.Formula) (rows : List ComponentRows) (hrs : RowsSound.{u} K rows)
    (cs r : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N [] Γ φ cs r) (h : foldEntailment cs r = .all)
    (ho : ∀ (j : Nat) (r' : ComponentRows), j ≠ k → rows[j]? = some r' → foldConflict r'.conflicts = .free) :
  ∀ cs', CompatibleK K cs' → ConflictFreeK.{u} K cs' ∧
    ∀ c, cs'[k]? = some c → EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ :=
  fun cs' hK => foldK_all_under K k N hk [] Γ φ rows (rowsSoundBut_of K rows k hrs) cs r hr h ho cs' hK
    (takesAt_nil cs' k)

/-- NONE for the document: NONE in component `k`, every other component settled under every compatible choice. -/
theorem foldK_none (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (Γ : List VE.Formula)
    (φ : VE.Formula) (rows : List ComponentRows) (hrs : RowsSound.{u} K rows)
    (cs r : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N [] Γ φ cs r) (h : foldEntailment cs r = .none)
    (ho : OthersSettled rows k true) :
  ∀ cs', CompatibleK K cs' → ConflictFreeK.{u} K cs' ∧
    (∀ (j : Nat) (M : NDoc) (c : Choice), j ≠ k → K.all[j]? = some M → cs'[j]? = some c →
      ConsistentU (choiceU M c) (choiceDoc M.D c).2) ∧
    ∀ c, cs'[k]? = some c → CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ :=
  fun cs' hK => foldK_none_under K k N hk [] Γ φ rows (rowsSoundBut_of K rows k hrs) cs r hr h ho cs' hK
    (takesAt_nil cs' k)

/-- SOME for the document: SOME in component `k`, every other component settled under some choice; every compatible
    product choice is CONFLICT-FREE (SR2). -/
theorem foldK_some (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (Γ : List VE.Formula)
    (φ : VE.Formula) (rows : List ComponentRows) (hrs : RowsSound.{u} K rows)
    (cs r : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N [] Γ φ cs r) (h : foldEntailment cs r = .some)
    (ho : OthersSettled rows k false) :
  (∀ cs', CompatibleK K cs' → ConflictFreeK.{u} K cs') ∧
  (∃ cs', CompatibleK K cs' ∧ ∃ c, cs'[k]? = some c ∧ EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ) ∧
  (∃ cs', CompatibleK K cs' ∧
    (∀ (j : Nat) (M : NDoc) (c : Choice), j ≠ k → K.all[j]? = some M → cs'[j]? = some c →
      ConsistentU (choiceU M c) (choiceDoc M.D c).2) ∧
    ∃ c, cs'[k]? = some c ∧ CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ) := by
  obtain ⟨h1, ⟨cs1, hK1, _, h1'⟩, ⟨cs2, hK2, _, h2'⟩⟩ :=
    foldK_some_under K k N hk [] Γ φ rows (rowsSoundBut_of K rows k hrs) cs r hr h ho
  exact ⟨fun cs' hK => h1 cs' hK (takesAt_nil cs' k), ⟨cs1, hK1, h1'⟩, ⟨cs2, hK2, h2'⟩⟩

/-! ## Lean-decided units (1.10) -/

/-- 1.10: the Lean-decided rule. -/
inductive Premise | model | inconsistent | dead | narrowed | unknown
  deriving DecidableEq, Repr
def fixedDecided (status premises : ChoiceResult) : Bool :=
  (status == .free || status == .conflict) && (premises == .model || premises == .inconsistent)
/-- The unit of an open set (SR4): `rows` are its component's conflict rows, one per compatible choice (`Covers N []`,
    a choice without checked evidence `unknown`); `readings` the premise status of each of the set's readings. A
    `dead` or `narrowed` reading is in no compatible choice, so its own status decides it. -/
def setDecided (rows : List (Choice × ChoiceResult)) (readings : List Premise) : Bool :=
  rows.all (fun x => x.2 == .free || x.2 == .conflict) && readings.all (· != .unknown)

/-- What `setDecided` says: every compatible choice's conflict result is checked, and no reading's premise status is
    UNKNOWN (1.10; the conflict results read per choice, SR4). -/
theorem setDecided_iff (rows : List (Choice × ChoiceResult)) (readings : List Premise) :
    setDecided rows readings = true ↔
      (∀ x ∈ rows, x.2 = .free ∨ x.2 = .conflict) ∧ ∀ p ∈ readings, p ≠ .unknown := by
  simp [setDecided, List.all_eq_true]

theorem fixedDecided_iff (status premises : ChoiceResult) :
    fixedDecided status premises = true ↔
      (status = .free ∨ status = .conflict) ∧ (premises = .model ∨ premises = .inconsistent) := by
  simp [fixedDecided]

end VE.Readings
