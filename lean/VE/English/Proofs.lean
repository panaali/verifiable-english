import VE.English.Statements
import VE.English.ParseProofs
import VE.English.RenderProofs
import VE.English.Check

/-! # Core-fragment English theorems

For an admitted lexicon covering the environment, the core surface satisfies
all four statements of `Statements.lean`:

* `core_unique_derivation`: a token text has at most one derivation;
* `core_parse_sound`: the parser returns only the reading of a derivation of
  its input (no lexical hypothesis needed);
* `core_parse_render` and `core_render_injective`: the canonical rendering of a
  checked document parses back to that document, so distinct documents render
  differently.

Scope of these results: the core productions listed in `Grammar.lean`, token
level (lexing and presentation Lean coverage pending), and the `Admitted`
lexical hypotheses, which the finite check `admissible` decides soundly
(`admissible_sound`, `Check.lean`); the `checked_*` corollaries state the
results for every vocabulary that passes the check. -/
namespace VE.English

variable {E : Environment} {L : Lexicon}

theorem size_le_length (hL : Admitted L) :
    ∀ (t : Tree) (d : Nat), t.Syntactic L → t.size ≤ (t.yield L d).length := by
  intro t
  induction t with
  | lit a =>
    intro d hs
    obtain ⟨x, rest, hy, -⟩ := hL.atom_opens a hs
    simp [Tree.size, Tree.yield, hy]
  | neg b ih => intro d hs; have := ih d hs; simp [Tree.size, Tree.yield]; omega
  | both a b => intro d hs; simp [Tree.size, Tree.yield]
  | either a b => intro d hs; simp [Tree.size, Tree.yield]
  | cond a b iha ihb =>
    intro d hs; have := iha d hs.1; have := ihb d hs.2; simp [Tree.size, Tree.yield]; omega
  | list h a b iha ihb =>
    intro d hs; have := iha (d + 1) hs.1; have := ihb (d + 1) hs.2
    simp [Tree.size, Tree.yield]; omega
  | all r b ih => intro d hs; have := ih d hs.2; simp [Tree.size, Tree.yield]; omega
  | ex an r b ih => intro d hs; have := ih d hs.2; simp [Tree.size, Tree.yield]; omega

/-- One sentence has at most one derivation at each list depth. -/
theorem tree_unique (hL : Admitted L) {d : Nat} {t₁ t₂ : Tree} (h₁ : t₁.Syntactic L)
    (h₂ : t₂.Syntactic L) (h : t₁.yield L d = t₂.yield L d) : t₁ = t₂ := by
  have e₁ := parseF_complete hL t₁ d (t₁.size + t₂.size + 1) [] h₁ (by omega) stop_nil
  have e₂ := parseF_complete hL t₂ d (t₁.size + t₂.size + 1) [] h₂ (by omega) stop_nil
  rw [h, e₂] at e₁
  exact (Prod.mk.inj (Option.some.inj e₁)).1.symm

theorem length_le_docYield (ts : List Tree) : ts.length ≤ (docYield L ts).length := by
  induction ts with
  | nil => simp [docYield]
  | cons t ts ih =>
    simp only [docYield, List.flatMap_cons, List.length_append, List.length_cons,
      List.length_nil] at ih ⊢
    omega

theorem parseTrees_complete (hL : Admitted L) :
    ∀ (ts : List Tree) (fuel : Nat), (∀ t ∈ ts, t.Syntactic L) → ts.length < fuel →
      parseTrees L fuel (docYield L ts) = some ts := by
  intro ts
  induction ts with
  | nil =>
    intro fuel _ hf
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by omega⟩
    rfl
  | cons t ts ih =>
    intro fuel hs hf
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by simp at hf; omega⟩
    have ht := hs t (by simp)
    have hsize := size_le_length hL t 0 ht
    have hdoc : docYield L (t :: ts) = t.yield L 0 ++ kw "." :: docYield L ts := by
      simp [docYield]
    obtain ⟨x, xs, hx⟩ : ∃ x xs, t.yield L 0 ++ kw "." :: docYield L ts = x :: xs := by
      cases h : t.yield L 0 ++ kw "." :: docYield L ts with
      | nil => simp at h
      | cons x xs => exact ⟨x, xs, rfl⟩
    have hlen : t.size < xs.length + 2 := by
      have := congrArg List.length hx
      simp at this; omega
    rw [hdoc, hx]
    simp only [parseTrees]
    rw [← hx, parseF_complete hL t 0 _ _ ht hlen (stop_cons (Or.inr (Or.inr rfl)) _)]
    simp [consume, ih f (fun t' h' => hs t' (by simp [h'])) (by simp at hf; omega)]

theorem parseTrees_sound : ∀ (fuel : Nat) (input : List Tok) (ts : List Tree),
    parseTrees L fuel input = some ts → (∀ t ∈ ts, t.Syntactic L) ∧ docYield L ts = input := by
  intro fuel
  induction fuel with
  | zero => intro input ts h; simp [parseTrees] at h
  | succ f ih =>
    intro input ts h
    match input, h with
    | [], h =>
      simp only [parseTrees, Option.some.injEq] at h
      subst h
      simp [docYield]
    | x :: xs, h =>
      simp only [parseTrees, Option.bind_eq_bind, Option.bind_eq_some_iff] at h
      obtain ⟨⟨t, r1⟩, h1, r2, h2, ts', h3, h⟩ := h
      simp only [Option.some.injEq] at h
      subst h
      try dsimp only at *
      obtain ⟨ht, he⟩ := parseF_sound _ _ _ _ _ h1
      obtain rfl := consume_sound h2
      obtain ⟨hs, rfl⟩ := ih _ _ h3
      refine ⟨fun t' h' => ?_, ?_⟩
      · rcases List.mem_cons.mp h' with rfl | h'
        · exact ht
        · exact hs t' h'
      · rw [he]; simp [docYield]

/-! ## The four statements for the core surface -/

theorem core_unique_derivation (hL : Admitted L) : UniqueDerivation (coreSurface E L) := by
  intro ts₁ ts₂ h₁ h₂ h
  have e₁ := parseTrees_complete hL ts₁ (ts₁.length + ts₂.length + 1) h₁ (by omega)
  have e₂ := parseTrees_complete hL ts₂ (ts₁.length + ts₂.length + 1) h₂ (by omega)
  change docYield L ts₁ = docYield L ts₂ at h
  rw [h, e₂] at e₁
  exact (Option.some.inj e₁).symm

theorem core_parse_sound : ParseSound (coreSurface E L) := by
  intro text As h
  change (do readTrees E (← parseTrees L (text.length + 1) text)) = some As at h
  simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
  obtain ⟨ts, h1, h2⟩ := h
  obtain ⟨hs, he⟩ := parseTrees_sound _ _ _ h1
  exact ⟨ts, hs, he, h2⟩

theorem mapM_denote_render (hC : Covers L E) :
    ∀ As : List Formula, (∀ A ∈ As, A.check E [] = true) →
      (As.map (renderStatement L)).mapM (Tree.denote []) = some As
  | [], _ => rfl
  | A :: As, h => by
    have hA := (renderStatement_correct hC (h A (by simp))).1
    simp [List.mapM_cons, hA, mapM_denote_render hC As (fun B hB => h B (by simp [hB]))]

theorem core_parse_render (hL : Admitted L) (hC : Covers L E) : ParseRender (coreSurface E L) := by
  intro As ⟨hne, hchk⟩
  change parse E L (render L As) = some As
  have hsyn : ∀ t ∈ As.map (renderStatement L), t.Syntactic L := by
    intro t ht
    obtain ⟨A, hA, rfl⟩ := List.mem_map.mp ht
    exact (renderStatement_correct hC (hchk A hA)).2
  have hfuel : (As.map (renderStatement L)).length < (render L As).length + 1 := by
    have := length_le_docYield (L := L) (As.map (renderStatement L))
    simp only [render]; omega
  simp only [parse, Option.bind_eq_bind]
  rw [show parseTrees L ((render L As).length + 1) (render L As) = some (As.map (renderStatement L))
    from parseTrees_complete hL _ _ hsyn hfuel]
  have hempty : (As.map (renderStatement L)).isEmpty = false := by
    cases As with
    | nil => exact absurd rfl hne
    | cons => rfl
  unfold readTrees
  rw [Option.bind_some, hempty, mapM_denote_render hC As hchk]
  simpa using hchk

theorem core_render_injective (hL : Admitted L) (hC : Covers L E) :
    RenderInjective (coreSurface E L) :=
  renderInjective_of_parseRender (core_parse_render hL hC)

theorem core_one_reading (hL : Admitted L) : OneReading (coreSurface E L) :=
  oneReading_of core_parse_sound (core_unique_derivation hL)

/-! ## For every vocabulary that passes the finite check -/

theorem checked_unique_derivation (h : admissible L = true) : UniqueDerivation (coreSurface E L) :=
  core_unique_derivation (admissible_sound h)

theorem checked_one_reading (h : admissible L = true) : OneReading (coreSurface E L) :=
  core_one_reading (admissible_sound h)

theorem checked_parse_render (h : admissible L = true) (hC : Covers L E) :
    ParseRender (coreSurface E L) :=
  core_parse_render (admissible_sound h) hC

theorem checked_render_injective (h : admissible L = true) (hC : Covers L E) :
    RenderInjective (coreSurface E L) :=
  core_render_injective (admissible_sound h) hC

end VE.English
