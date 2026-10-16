import VE.Semantics

/-! # The entities a premise set forces in one sort (premise-scale)

The premise-consistency check searches finite models up to a domain bound. A premise set can
force more entities of a sort than that bound: "exactly three principal types" is three
constants stated pairwise distinct, or `∃ x y z` with pairwise `x ≠ y`. `demand` counts such
entities from the stated facts alone, and `demand_sound` proves the count is a lower bound: every
structure that satisfies the premises has that many pairwise distinct elements of the sort.

The facts are the top-level conjuncts of the premises (`conjuncts`). Two terms are stated
distinct when `¬(t = u)` or `¬(u = t)` is a fact. `distinctTerms` keeps a term when the facts
state it distinct from every term kept before it (a greedy choice: a lower bound, not the
largest such set). The terms are the constants of the sort, or the variables of a chain
`∃ x₁ … xₖ : s` at the head of a fact, read in the facts of the chain's body.

The count steers an untrusted search only (`VE.SearchBudget.Run`): a model the search finds
is still checked by Lean, and no count makes a check pass. -/
namespace VE.SearchBudget
open VE

/-- The top-level conjuncts of a formula. -/
def conjuncts : Formula → List Formula
  | .and a b => conjuncts a ++ conjuncts b
  | a => [a]

theorem conjuncts_denote {S : Structure} {ρ : Valuation S} :
    ∀ {a : Formula}, a.denote S ρ → ∀ c ∈ conjuncts a, c.denote S ρ
  | .and a b, h, c, hc => by
    simp only [conjuncts, List.mem_append] at hc
    exact hc.elim (conjuncts_denote h.1 c) (conjuncts_denote h.2 c)
  | .top, h, c, hc | .bottom, h, c, hc | .unary _ _, h, c, hc | .binary _ _ _, h, c, hc
  | .eq _ _, h, c, hc | .not _, h, c, hc | .or _ _, h, c, hc | .implies _ _, h, c, hc
  | .all _ _, h, c, hc | .ex _ _, h, c, hc => by
    simp only [conjuncts, List.mem_singleton] at hc
    exact hc ▸ h

/-- The facts of a premise list: every top-level conjunct of every premise. -/
def facts (premises : List Formula) : List Formula := premises.flatMap conjuncts

theorem facts_denote {S : Structure} {ρ : Valuation S} {premises : List Formula}
    (h : ∀ a ∈ premises, a.denote S ρ) : ∀ c ∈ facts premises, c.denote S ρ := by
  intro c hc
  simp only [facts, List.mem_flatMap] at hc
  obtain ⟨a, ha, hc⟩ := hc
  exact conjuncts_denote (h a ha) c hc

/-- Whether the facts state that `t` and `u` differ. -/
def statesDistinct (fs : List Formula) (t u : Term) : Bool :=
  fs.any (fun f => decide (f = .not (.eq t u)) || decide (f = .not (.eq u t)))

theorem statesDistinct_comm (fs : List Formula) (t u : Term) :
    statesDistinct fs t u = statesDistinct fs u t := by
  unfold statesDistinct
  congr 1
  funext f
  exact Bool.or_comm _ _

/-- A term is kept when the facts state it distinct from every term kept before it. -/
def keep (fs : List Formula) (kept : List Term) (t : Term) : List Term :=
  if kept.all (statesDistinct fs t) then kept ++ [t] else kept

def distinctTerms (fs : List Formula) (ts : List Term) : List Term :=
  ts.foldl (keep fs) []

theorem keep_pairwise {fs : List Formula} {kept : List Term} (t : Term)
    (h : kept.Pairwise (fun a b => statesDistinct fs a b = true)) :
    (keep fs kept t).Pairwise (fun a b => statesDistinct fs a b = true) := by
  unfold keep
  split
  · rename_i hall
    rw [List.pairwise_append]
    refine ⟨h, List.pairwise_singleton _ _, ?_⟩
    intro a ha b hb
    simp only [List.mem_singleton] at hb
    subst hb
    rw [statesDistinct_comm]
    exact List.all_eq_true.mp hall a ha
  · exact h

theorem keep_subset {fs : List Formula} {kept : List Term} {t : Term} :
    ∀ x ∈ keep fs kept t, x ∈ kept ∨ x = t := by
  intro x hx
  unfold keep at hx
  split at hx
  · simp only [List.mem_append, List.mem_singleton] at hx
    exact hx
  · exact .inl hx

theorem foldl_keep {fs : List Formula} :
    ∀ (ts kept : List Term), kept.Pairwise (fun a b => statesDistinct fs a b = true) →
      (ts.foldl (keep fs) kept).Pairwise (fun a b => statesDistinct fs a b = true) ∧
      ∀ x ∈ ts.foldl (keep fs) kept, x ∈ kept ∨ x ∈ ts
  | [], kept, h => ⟨h, fun x hx => .inl hx⟩
  | t :: ts, kept, h => by
    obtain ⟨hp, hs⟩ := foldl_keep ts (keep fs kept t) (keep_pairwise t h)
    refine ⟨hp, fun x hx => ?_⟩
    rcases hs x hx with hx | hx
    · rcases keep_subset x hx with hx | hx
      · exact .inl hx
      · exact .inr (hx ▸ List.mem_cons_self ..)
    · exact .inr (List.mem_cons_of_mem _ hx)

/-- The kept terms are pairwise stated distinct, and each is one of `ts`. -/
theorem distinctTerms_spec (fs : List Formula) (ts : List Term) :
    (distinctTerms fs ts).Pairwise (fun a b => statesDistinct fs a b = true) ∧
    ∀ x ∈ distinctTerms fs ts, x ∈ ts := by
  obtain ⟨hp, hs⟩ := foldl_keep (fs := fs) ts [] List.Pairwise.nil
  exact ⟨hp, fun x hx => (hs x hx).elim (fun h => by simp at h) id⟩

/-- Terms stated pairwise distinct by true facts, each denoting an element of `s`, denote that
many pairwise distinct elements of `s`. -/
theorem distinct_values {S : Structure} {ρ : Valuation S} {fs : List Formula} {s : String}
    (hfs : ∀ c ∈ fs, c.denote S ρ) :
    ∀ (ts : List Term), ts.Pairwise (fun a b => statesDistinct fs a b = true) →
      (∀ t ∈ ts, ∃ v, t.denote S ρ = some v ∧ S.domain s v) →
      ∃ vs : List S.Carrier, vs.length = ts.length ∧ vs.Nodup ∧ (∀ v ∈ vs, S.domain s v) ∧
        ∀ v ∈ vs, ∃ t ∈ ts, t.denote S ρ = some v
  | [], _, _ => ⟨[], rfl, List.Pairwise.nil, fun _ h => by simp at h, fun _ h => by simp at h⟩
  | t :: ts, hp, hd => by
    rw [List.pairwise_cons] at hp
    obtain ⟨vs, hl, hn, hdom, hof⟩ :=
      distinct_values hfs ts hp.2 (fun u hu => hd u (List.mem_cons_of_mem _ hu))
    obtain ⟨v, hv, hvs⟩ := hd t (List.mem_cons_self ..)
    refine ⟨v :: vs, by simp [hl], ?_, ?_, ?_⟩
    · rw [List.nodup_cons]
      refine ⟨fun hmem => ?_, hn⟩
      obtain ⟨u, hu, huv⟩ := hof v hmem
      have hst := hp.1 u hu
      simp only [statesDistinct, List.any_eq_true, Bool.or_eq_true, decide_eq_true_eq] at hst
      obtain ⟨f, hf, hfe | hfe⟩ := hst
      · have hn := hfs f hf
        rw [hfe] at hn
        exact hn ⟨v, hv, huv⟩
      · have hn := hfs f hf
        rw [hfe] at hn
        exact hn ⟨v, huv, hv⟩
    · intro w hw
      rcases List.mem_cons.mp hw with hw | hw
      · exact hw ▸ hvs
      · exact hdom w hw
    · intro w hw
      rcases List.mem_cons.mp hw with hw | hw
      · exact ⟨t, List.mem_cons_self .., hw ▸ hv⟩
      · obtain ⟨u, hu, huw⟩ := hof w hw
        exact ⟨u, List.mem_cons_of_mem _ hu, huw⟩

/-- The constants of sort `s` among the declared `(name, sort)` pairs, as terms. -/
def constantTerms (cs : List (String × String)) (s : String) : List Term :=
  (cs.filter (fun c => c.2 == s)).map (fun c => .const c.1)

/-- The head chain `∃ x₁ … xₖ : s. body` of a formula: `k` and the body. -/
def chain (s : String) : Formula → Nat × Formula
  | .ex s' a => if s' = s then ((chain s a).1 + 1, (chain s a).2) else (0, .ex s' a)
  | a => (0, a)

theorem chain_denote {S : Structure} {s : String} :
    ∀ (a : Formula) (σ : Valuation S), a.denote S σ →
      ∃ ρ : List S.Carrier, ρ.length = (chain s a).1 ∧ (∀ v ∈ ρ, S.domain s v) ∧
        (chain s a).2.denote S (ρ ++ σ)
  | .ex s' a, σ, h => by
    unfold chain
    split
    · rename_i hs
      subst hs
      obtain ⟨v, hv, ha⟩ := h
      obtain ⟨ρ, hl, hd, hb⟩ := chain_denote (s := s') a (v :: σ) ha
      refine ⟨ρ ++ [v], by simp [hl], ?_, by simpa using hb⟩
      intro w hw
      rcases List.mem_append.mp hw with hw | hw
      · exact hd w hw
      · simp only [List.mem_singleton] at hw
        exact hw ▸ hv
    · exact ⟨[], rfl, fun _ h => by simp at h, h⟩
  | .top, σ, h | .bottom, σ, h | .unary _ _, σ, h | .binary _ _ _, σ, h | .eq _ _, σ, h
  | .not _, σ, h | .and _ _, σ, h | .or _ _, σ, h | .implies _ _, σ, h | .all _ _, σ, h => by
    exact ⟨[], rfl, fun _ h => by simp at h, h⟩

/-- The entities a fact's head chain over `s` forces. -/
def chainDemand (s : String) (a : Formula) : Nat :=
  (distinctTerms (conjuncts (chain s a).2) ((List.range (chain s a).1).map .var)).length

/-- The entities of sort `s` the premises force: the most of the constants stated pairwise
distinct and of each fact's head chain. -/
def demand (cs : List (String × String)) (premises : List Formula) (s : String) : Nat :=
  ((facts premises).map (chainDemand s)).foldl max
    (distinctTerms (facts premises) (constantTerms cs s)).length

theorem foldl_max_of {P : Nat → Prop} :
    ∀ (ns : List Nat) (n : Nat), P n → (∀ m ∈ ns, P m) → P (ns.foldl max n)
  | [], _, h, _ => h
  | m :: ns, n, h, hs => by
    apply foldl_max_of ns (max n m) _ (fun k hk => hs k (List.mem_cons_of_mem _ hk))
    rcases Nat.le_total n m with hnm | hmn
    · rw [Nat.max_eq_right hnm]
      exact hs m (List.mem_cons_self ..)
    · rw [Nat.max_eq_left hmn]
      exact h

/-- The forced entities exist: in every admissible structure where the premises hold, sort `s`
has `demand cs premises s` pairwise distinct elements. `cs` are declared constants. -/
theorem demand_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    {cs : List (String × String)} (hcs : ∀ c ∈ cs, E.constants c.1 = some c.2)
    {premises : List Formula} (hp : ∀ a ∈ premises, a.denote S []) (s : String) :
    ∃ vs : List S.Carrier, vs.length = demand cs premises s ∧ vs.Nodup ∧
      ∀ v ∈ vs, S.domain s v := by
  have hf := facts_denote hp
  unfold demand
  apply foldl_max_of (P := fun n => ∃ vs : List S.Carrier, vs.length = n ∧ vs.Nodup ∧
    ∀ v ∈ vs, S.domain s v)
  · obtain ⟨hpw, hsub⟩ := distinctTerms_spec (facts premises) (constantTerms cs s)
    obtain ⟨vs, hl, hn, hd, _⟩ := distinct_values (s := s) hf _ hpw (by
      intro t ht
      have := hsub t ht
      simp only [constantTerms, List.mem_map, List.mem_filter, beq_iff_eq] at this
      obtain ⟨c, ⟨hc, hcs'⟩, rfl⟩ := this
      obtain ⟨v, hv, hd⟩ := hS.1 c.1 c.2 (hcs c hc)
      exact ⟨v, hv, hcs' ▸ hd⟩)
    exact ⟨vs, hl, hn, hd⟩
  · intro m hm
    simp only [List.mem_map] at hm
    obtain ⟨a, ha, rfl⟩ := hm
    obtain ⟨ρ, hl, hd, hb⟩ := chain_denote (s := s) a [] (hf a ha)
    rw [List.append_nil] at hb
    obtain ⟨hpw, hsub⟩ := distinctTerms_spec (conjuncts (chain s a).2)
      ((List.range (chain s a).1).map .var)
    obtain ⟨vs, hl', hn, hd', _⟩ := distinct_values (s := s) (conjuncts_denote hb) _ hpw (by
      intro t ht
      have := hsub t ht
      simp only [List.mem_map, List.mem_range] at this
      obtain ⟨i, hi, rfl⟩ := this
      rw [← hl] at hi
      exact ⟨ρ[i], by simp [Term.denote, hi], hd _ (List.getElem_mem hi)⟩)
    exact ⟨vs, hl', hn, hd'⟩

end VE.SearchBudget
