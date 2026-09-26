import VE.English.Render
import VE.Typing

/-! # The canonical renderer produces a derivation of the rendered formula

The binder names chosen by `bindRef` are pairwise distinct within every scope
(this is where the per-sort maximum `sdepth` matters: `that person` is used
only when at most one person is ever in scope, `first`/`second` only for two),
so every rendered reference resolves to its own binder. -/
namespace VE.English

/-- A scope built by `bindRef` under the per-sort bounds `M`. -/
def Built (M : String → Nat) : List Ref → Prop
  | [] => True
  | r :: Γ => r = bindRef M Γ r.sort ∧ scopeCount r.sort Γ < M r.sort ∧ Built M Γ

theorem bindRef_sort (M : String → Nat) (Γ : List Ref) (s : String) : (bindRef M Γ s).sort = s := by
  unfold bindRef
  split
  · rfl
  · split
    · split <;> rfl
    · rfl

theorem scopeCount_cons (s : String) (r : Ref) (Γ : List Ref) :
    scopeCount s (r :: Γ) = scopeCount s Γ + (if r.sort = s then 1 else 0) := by
  simp [scopeCount, List.countP_cons]

theorem built_mem {M : String → Nat} : ∀ {Γ : List Ref} {e : Ref}, Built M Γ → e ∈ Γ →
    ∃ Γ', e = bindRef M Γ' e.sort ∧ scopeCount e.sort Γ' < scopeCount e.sort Γ
  | [], _, _, h => by simp at h
  | r :: Γ, e, hb, h => by
    obtain ⟨hr, -, hΓ⟩ := hb
    rcases List.mem_cons.mp h with rfl | h
    · exact ⟨Γ, hr, by simp [scopeCount_cons]⟩
    · obtain ⟨Γ', he, hlt⟩ := built_mem hΓ h
      refine ⟨Γ', he, ?_⟩
      rw [scopeCount_cons]
      omega

theorem bindRef_fresh {M : String → Nat} {Γ : List Ref} {s : String} (hb : Built M Γ)
    (hlt : scopeCount s Γ < M s) : bindRef M Γ s ∉ Γ := by
  intro hmem
  obtain ⟨Γ', he, hlt'⟩ := built_mem hb hmem
  rw [bindRef_sort] at he hlt'
  unfold bindRef at he
  split at he
  · omega
  · split at he
    · split at he
      · omega
      · split at he
        · cases he
        · omega
    · simp only [Ref.named.injEq, true_and] at he
      omega

theorem built_nodup {M : String → Nat} : ∀ {Γ : List Ref}, Built M Γ → Γ.Nodup
  | [], _ => List.nodup_nil
  | r :: Γ, ⟨hr, hlt, hΓ⟩ => by
    refine List.nodup_cons.mpr ⟨?_, built_nodup hΓ⟩
    rw [hr]
    exact bindRef_fresh hΓ hlt

theorem idxOfOpt_getElem : ∀ {Γ : List Ref} {i : Nat} (h : i < Γ.length), Γ.Nodup → Γ.idxOf? Γ[i] = some i
  | [], _, h, _ => by simp at h
  | r :: Γ, 0, _, _ => by simp [List.idxOf?_cons]
  | r :: Γ, i + 1, h, hn => by
    obtain ⟨hr, hn⟩ := List.nodup_cons.mp hn
    have hi : i < Γ.length := by simpa using h
    have hne : r ≠ Γ[i] := fun e => hr (e ▸ List.getElem_mem hi)
    simp [List.idxOf?_cons, hne, idxOfOpt_getElem hi hn]

section
variable {E : Environment} {L : Lexicon}

theorem renderTerm_correct (hC : Covers L E) {Γ : List Ref} {t : Term} {s : String}
    (ht : t.sortOf E (Γ.map Ref.sort) = some s) (hn : Γ.Nodup) (hs : ∀ r ∈ Γ, r.sort ∈ L.sorts) :
    (renderTerm Γ t).denote Γ = some t ∧ (renderTerm Γ t).ok L = true := by
  cases t with
  | var i =>
    simp only [Term.sortOf, List.getElem?_map, Option.map_eq_some_iff] at ht
    obtain ⟨r, hr, -⟩ := ht
    have hi : i < Γ.length := (List.getElem?_eq_some_iff.mp hr).1
    have hget : Γ[i]? = some Γ[i] := List.getElem?_eq_getElem hi
    simp only [renderTerm, hget, Option.getD_some, TermTree.denote, idxOfOpt_getElem hi hn,
      Option.map_some, TermTree.ok, List.contains_iff_mem, true_and]
    exact hs _ (List.getElem_mem hi)
  | const c =>
    simp only [Term.sortOf] at ht
    simp [renderTerm, TermTree.denote, TermTree.ok, hC.constants c s ht]

theorem pred_ok (hC : Covers L E) {p : String} {ss : List String} (hp : E.predicates p = some ss)
    {args : List TermTree} (hlen : args.length = ss.length) (hargs : ∀ a ∈ args, a.ok L = true) :
    (Lit.pred p args).ok L = true := by
  obtain ⟨hmem, T, hT, har, hholes⟩ := hC.predicates p ss hp
  simp only [Lit.ok, hT, Bool.and_eq_true, List.contains_iff_mem, List.all_eq_true, beq_iff_eq,
    List.mem_range]
  exact ⟨⟨hmem, hargs⟩, by omega, fun i hi => by simpa using hholes i (by omega)⟩

theorem renderLit_correct (hC : Covers L E) {Γ : List Ref} {A : Formula} (hA : isSimple A = true)
    (hw : A.WellFormed E (Γ.map Ref.sort)) (hn : Γ.Nodup) (hs : ∀ r ∈ Γ, r.sort ∈ L.sorts) :
    (renderLit Γ A).denote Γ = some A ∧ (renderLit Γ A).ok L = true := by
  cases A with
  | top => simp [renderLit, Lit.denote, Lit.ok]
  | bottom => simp [renderLit, Lit.denote, Lit.ok]
  | unary p t =>
    obtain ⟨s, hp, ht⟩ := hw
    obtain ⟨h1, h2⟩ := renderTerm_correct hC ht hn hs
    refine ⟨by simp [renderLit, Lit.denote, h1], pred_ok hC hp (by simp) (by simp [h2])⟩
  | binary p t u =>
    obtain ⟨s, r, hp, ht, hu⟩ := hw
    obtain ⟨h1, h2⟩ := renderTerm_correct hC ht hn hs
    obtain ⟨h3, h4⟩ := renderTerm_correct hC hu hn hs
    refine ⟨by simp [renderLit, Lit.denote, h1, h3], pred_ok hC hp (by simp) (by simp [h2, h4])⟩
  | eq t u =>
    obtain ⟨s, ht, hu⟩ := hw
    obtain ⟨h1, h2⟩ := renderTerm_correct hC ht hn hs
    obtain ⟨h3, h4⟩ := renderTerm_correct hC hu hn hs
    simp [renderLit, Lit.denote, Lit.ok, h1, h2, h3, h4]
  | _ => simp [isSimple] at hA

theorem renderTree_correct (hC : Covers L E) (M : String → Nat) :
    ∀ (A : Formula) (Γ : List Ref), A.WellFormed E (Γ.map Ref.sort) → Built M Γ →
      (∀ r ∈ Γ, r.sort ∈ L.sorts) → (∀ s, scopeCount s Γ + sdepth s A ≤ M s) →
      (renderTree L M Γ A).denote Γ = some A ∧ (renderTree L M Γ A).Syntactic L := by
  intro A
  induction A with
  | top | bottom | unary | binary | eq =>
    intro Γ hw hb hs _
    exact renderLit_correct hC rfl hw (built_nodup hb) hs
  | not a ih =>
    intro Γ hw hb hs hm
    obtain ⟨h1, h2⟩ := ih Γ hw hb hs (fun s => by simpa [sdepth] using hm s)
    exact ⟨by simp [renderTree, Tree.denote, h1], h2⟩
  | and a b iha ihb =>
    intro Γ hw hb hs hm
    obtain ⟨hwa, hwb⟩ := hw
    have hma : ∀ s, scopeCount s Γ + sdepth s a ≤ M s := fun s => by
      have := hm s; have := Nat.le_max_left (sdepth s a) (sdepth s b); simp [sdepth] at *; omega
    have hmb : ∀ s, scopeCount s Γ + sdepth s b ≤ M s := fun s => by
      have := hm s; have := Nat.le_max_right (sdepth s a) (sdepth s b); simp [sdepth] at *; omega
    by_cases hsimp : isSimple a = true ∧ isSimple b = true
    · obtain ⟨h1, h2⟩ := renderLit_correct hC hsimp.1 hwa (built_nodup hb) hs
      obtain ⟨h3, h4⟩ := renderLit_correct hC hsimp.2 hwb (built_nodup hb) hs
      simp only [renderTree, hsimp.1, hsimp.2, Bool.and_self, if_true]
      exact ⟨by simp [Tree.denote, h1, h3], h2, h4⟩
    · obtain ⟨h1, h2⟩ := iha Γ hwa hb hs hma
      obtain ⟨h3, h4⟩ := ihb Γ hwb hb hs hmb
      have hs' : (isSimple a && isSimple b) = false := by
        cases ha : isSimple a <;> cases hb' : isSimple b <;> simp_all
      simp only [renderTree, hs', Bool.false_eq_true, if_false]
      refine ⟨?_, h2, h4⟩
      split <;> simp [Tree.denote, h1, h3]
  | or a b iha ihb =>
    intro Γ hw hb hs hm
    obtain ⟨hwa, hwb⟩ := hw
    have hma : ∀ s, scopeCount s Γ + sdepth s a ≤ M s := fun s => by
      have := hm s; have := Nat.le_max_left (sdepth s a) (sdepth s b); simp [sdepth] at *; omega
    have hmb : ∀ s, scopeCount s Γ + sdepth s b ≤ M s := fun s => by
      have := hm s; have := Nat.le_max_right (sdepth s a) (sdepth s b); simp [sdepth] at *; omega
    by_cases hsimp : isSimple a = true ∧ isSimple b = true
    · obtain ⟨h1, h2⟩ := renderLit_correct hC hsimp.1 hwa (built_nodup hb) hs
      obtain ⟨h3, h4⟩ := renderLit_correct hC hsimp.2 hwb (built_nodup hb) hs
      simp only [renderTree, hsimp.1, hsimp.2, Bool.and_self, if_true]
      exact ⟨by simp [Tree.denote, h1, h3], h2, h4⟩
    · obtain ⟨h1, h2⟩ := iha Γ hwa hb hs hma
      obtain ⟨h3, h4⟩ := ihb Γ hwb hb hs hmb
      have hs' : (isSimple a && isSimple b) = false := by
        cases ha : isSimple a <;> cases hb' : isSimple b <;> simp_all
      simp only [renderTree, hs', Bool.false_eq_true, if_false]
      exact ⟨by simp [Tree.denote, h1, h3], h2, h4⟩
  | implies a b iha ihb =>
    intro Γ hw hb hs hm
    obtain ⟨hwa, hwb⟩ := hw
    have hma : ∀ s, scopeCount s Γ + sdepth s a ≤ M s := fun s => by
      have := hm s; have := Nat.le_max_left (sdepth s a) (sdepth s b); simp [sdepth] at *; omega
    have hmb : ∀ s, scopeCount s Γ + sdepth s b ≤ M s := fun s => by
      have := hm s; have := Nat.le_max_right (sdepth s a) (sdepth s b); simp [sdepth] at *; omega
    obtain ⟨h1, h2⟩ := iha Γ hwa hb hs hma
    obtain ⟨h3, h4⟩ := ihb Γ hwb hb hs hmb
    exact ⟨by simp [renderTree, Tree.denote, h1, h3], h2, h4⟩
  | all s a ih | ex s a ih =>
    intro Γ hw hb hs hm
    obtain ⟨hsE, hwa⟩ := hw
    have hsort := bindRef_sort M Γ s
    have hlt : scopeCount s Γ < M s := by
      have := hm s; simp [sdepth] at this; omega
    have hb' : Built M (bindRef M Γ s :: Γ) := ⟨by rw [hsort], by rw [hsort]; exact hlt, hb⟩
    have hs' : ∀ r ∈ bindRef M Γ s :: Γ, r.sort ∈ L.sorts := by
      intro r hr
      rcases List.mem_cons.mp hr with rfl | hr
      · rw [hsort]; exact hC.sorts s hsE
      · exact hs r hr
    have hm' : ∀ t, scopeCount t (bindRef M Γ s :: Γ) + sdepth t a ≤ M t := by
      intro t
      have := hm t
      rw [scopeCount_cons, hsort]
      by_cases hst : s = t
      · subst hst; simp [sdepth] at this ⊢; omega
      · simp [sdepth, hst] at this ⊢; omega
    have hwa' : a.WellFormed E ((bindRef M Γ s :: Γ).map Ref.sort) := by simpa [hsort] using hwa
    obtain ⟨h1, h2⟩ := ih _ hwa' hb' hs' hm'
    refine ⟨by simp [renderTree, Tree.denote, h1, hsort], ?_, h2⟩
    rw [hsort]; exact hC.sorts s hsE

/-- The canonical rendering of a closed well-typed formula is a derivation of it. -/
theorem renderStatement_correct (hC : Covers L E) {A : Formula} (hA : A.check E [] = true) :
    (renderStatement L A).denote [] = some A ∧ (renderStatement L A).Syntactic L :=
  renderTree_correct hC _ A [] ((check_iff_wellFormed E [] A).mp hA) trivial (by simp)
    (fun s => by simp [scopeCount])

end

end VE.English
