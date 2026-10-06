import VE.EnglishGrammar.Read
import VE.Grammar.Extension

/-! Extensions of an English environment and lexicon (docs/spec/english-lean-s2.md 2.13, 5.4 and 5.6).

`Extends E O L E2 O2 L2` holds when both environments have the base profile alone, every symbol of `E`
is a symbol of `E2` with the same signature, every selection of `L` is a selection of `L2`, and both
lexicons are valid. Under it the grammar of `E` and `L` maps into the grammar of `E2` and `L2` rule for
rule (`grammar_extension`): the fixed rules are the same array with the same closed actions, and every
lexical row of `L` is a lexical row of `L2`, because each row is built from one lexicon entry and the
signature of its symbol only. The map sends a fixed rule to itself and a lexical rule to the first rule
of `L2` with the same row; it is injective because repeated rows were dropped.
-/

namespace VE.EnglishGrammar
open VE.Grammar

def lexiconSub (L L2 : Lexicon) : Prop :=
  (∀ x ∈ L.nouns, x ∈ L2.nouns) ∧ (∀ x ∈ L.letters, x ∈ L2.letters) ∧
  (∀ x ∈ L.wordings, x ∈ L2.wordings) ∧ (∀ x ∈ L.negatives, x ∈ L2.negatives) ∧
  (∀ x ∈ L.aliases, x ∈ L2.aliases) ∧ (∀ x ∈ L.spellings, x ∈ L2.spellings)

def envSub (E E2 : Env) : Prop :=
  E.profiles = ["relational-fol@0"] ∧ E2.profiles = E.profiles ∧
  (∀ s ∈ E.sorts, ∃ s2 ∈ E2.sorts, s2.name = s.name) ∧
  (∀ p ∈ E.predicates, ∃ q ∈ E2.predicates, q.name = p.name ∧ q.arity = p.arity ∧ q.args = p.args) ∧
  (∀ c ∈ E.constants, ∃ c2 ∈ E2.constants, c2.name = c.name ∧ c2.sort = c.sort)

def Extends (E : Env) (O : Overlay) (L : Lexicon) (E2 : Env) (O2 : Overlay) (L2 : Lexicon) : Prop :=
  envSub E E2 ∧ lexiconSub L L2 ∧ L.valid E O = true ∧ L2.valid E2 O2 = true

/-! ## Every lexical row of the smaller grammar is a row of the larger -/

theorem flatMap_sub {α β γ : Type} {l1 : List α} {l2 : List β} {f : α → List γ} {g : β → List γ}
    (h : ∀ x ∈ l1, ∃ y ∈ l2, ∀ r ∈ f x, r ∈ g y) : ∀ r ∈ l1.flatMap f, r ∈ l2.flatMap g := by
  intro r hr
  obtain ⟨x, hx, hrx⟩ := List.mem_flatMap.mp hr
  obtain ⟨y, hy, hxy⟩ := h x hx
  exact List.mem_flatMap.mpr ⟨y, hy, hxy r hrx⟩

theorem flatMap_mono {α γ : Type} {l1 l2 : List α} {f : α → List γ} (h : ∀ x ∈ l1, x ∈ l2) :
    ∀ r ∈ l1.flatMap f, r ∈ l2.flatMap f :=
  flatMap_sub fun x hx => ⟨x, h x hx, fun _ hr => hr⟩

theorem adjectiveRows_sub {L L2 : Lexicon} (hn : ∀ x ∈ L.nouns, x ∈ L2.nouns) (p s a : String) :
    ∀ r ∈ adjectiveRows L p s a, r ∈ adjectiveRows L2 p s a := by
  intro r hr
  unfold adjectiveRows at hr ⊢
  rcases List.mem_append.mp hr with h | h
  · exact List.mem_append_left _ h
  · refine List.mem_append_right _ (flatMap_mono (fun x hx => ?_) r h)
    obtain ⟨hx1, hx2⟩ := List.mem_filter.mp hx
    exact List.mem_filter.mpr ⟨hn x hx1, hx2⟩

/-- A declaration of `E` named `p` has a declaration of `E2` named `p` with the same signature. -/
theorem decl_sub {E E2 : Env} (hp : ∀ p ∈ E.predicates, ∃ q ∈ E2.predicates, q.name = p.name ∧
    q.arity = p.arity ∧ q.args = p.args) {p : String} {d : PredDecl} (hd : d ∈ declsOf E p) :
    ∃ q ∈ declsOf E2 p, q.args = d.args := by
  unfold declsOf at hd ⊢
  obtain ⟨hd1, hd2⟩ := List.mem_filter.mp hd
  obtain ⟨q, hq, hqn, _, hqa⟩ := hp d hd1
  exact ⟨q, List.mem_filter.mpr ⟨hq, by rw [hqn]; exact hd2⟩, hqa⟩

theorem lexRowsAll_sub {E E2 : Env} {L L2 : Lexicon} (hE : envSub E E2) (hL : lexiconSub L L2) :
    ∀ r ∈ lexRowsAll E L, r ∈ lexRowsAll E2 L2 := by
  obtain ⟨hn, hl, hw, hneg, ha, hsp⟩ := hL
  obtain ⟨_, _, _, hp, hc⟩ := hE
  intro r hr
  unfold lexRowsAll at hr ⊢
  simp only [List.mem_append, or_assoc] at hr ⊢
  rcases hr with h | h | h | h | h | h | h | h | h
  · exact Or.inl (flatMap_mono hw r h)
  · exact Or.inr (Or.inl (flatMap_mono hneg r h))
  · exact Or.inr (Or.inr (Or.inl (flatMap_mono ha r h)))
  · exact Or.inr (Or.inr (Or.inr (Or.inl (flatMap_mono hn r h))))
  · refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ?_))))
    obtain ⟨x, hx, rfl⟩ := List.mem_map.mp h
    exact List.mem_map.mpr ⟨x, hl x hx, rfl⟩
  · refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ?_)))))
    refine flatMap_sub (fun x hx => ⟨x, hsp x hx, fun r hr => ?_⟩) r h
    obtain ⟨c, sp⟩ := x
    obtain ⟨d, hd, hrd⟩ := List.mem_flatMap.mp hr
    obtain ⟨hd1, hd2⟩ := List.mem_filter.mp hd
    obtain ⟨c2, hc2, hcn, hcs⟩ := hc d hd1
    exact List.mem_flatMap.mpr ⟨c2, List.mem_filter.mpr ⟨hc2, by rw [hcn]; exact hd2⟩, by rw [hcs]; exact hrd⟩
  · refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ?_))))))
    refine flatMap_sub (fun x hx => ⟨x, hw x hx, fun r hr => ?_⟩) r h
    obtain ⟨p, w⟩ := x
    simp only at hr ⊢
    split at hr
    · rename_i a ha
      obtain ⟨d, hd, hrd⟩ := List.mem_flatMap.mp hr
      obtain ⟨q, hq, hqa⟩ := decl_sub hp hd
      refine List.mem_flatMap.mpr ⟨q, hq, ?_⟩
      rw [hqa]
      split at hrd
      · rename_i s _
        exact adjectiveRows_sub hn p s a r hrd
      · simp at hrd
    · simp at hr
  · refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ?_)))))))
    refine flatMap_sub (fun x hx => ⟨x, hw x hx, fun r hr => ?_⟩) r h
    obtain ⟨p, w⟩ := x
    simp only at hr ⊢
    split at hr
    · rename_i hpw
      rw [if_pos hpw]
      obtain ⟨d, hd, hrd⟩ := List.mem_flatMap.mp hr
      obtain ⟨q, hq, hqa⟩ := decl_sub hp hd
      exact List.mem_flatMap.mpr ⟨q, hq, by rw [hqa]; exact hrd⟩
    · simp at hr
  · refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr ?_)))))))
    refine flatMap_sub (fun d hd => ?_) r h
    obtain ⟨q, hq, hqn, _, hqa⟩ := hp d hd
    exact ⟨q, hq, fun r hr => by rw [hqn, hqa]; exact hr⟩

theorem lexRows_sub {E E2 : Env} {L L2 : Lexicon} (hE : envSub E E2) (hL : lexiconSub L L2) :
    ∀ r ∈ lexRows E L, r ∈ lexRows E2 L2 := by
  intro r hr
  unfold lexRows at hr ⊢
  obtain ⟨h1, h2⟩ := List.mem_filter.mp hr
  exact List.mem_filter.mpr ⟨mem_dedup.mpr (lexRowsAll_sub hE hL r (mem_dedup.mp h1)), h2⟩

/-! ## Positions in a list without repeats -/

/-- The position of the first occurrence of `a`. -/
def indexIn {α : Type} [DecidableEq α] (a : α) : List α → Nat
  | [] => 0
  | x :: xs => if x = a then 0 else indexIn a xs + 1

theorem indexIn_get {α : Type} [DecidableEq α] {a : α} : ∀ {l : List α}, a ∈ l → l[indexIn a l]? = some a
  | [], h => absurd h List.not_mem_nil
  | x :: xs, h => by
    unfold indexIn
    by_cases hx : x = a
    · simp [hx]
    · simp only [hx, if_false, List.getElem?_cons_succ]
      exact indexIn_get ((List.mem_cons.mp h).resolve_left (Ne.symm hx))

theorem nodup_index_inj {α : Type} : ∀ {l : List α} {i j : Nat}, l.Nodup → l[i]? = l[j]? → i < l.length →
    i = j
  | [], _, _, _, _, hi => absurd hi (Nat.not_lt_zero _)
  | x :: xs, i, j, hn, h, hi => by
    obtain ⟨hx, hxs⟩ := List.nodup_cons.mp hn
    match i, j with
    | 0, 0 => rfl
    | 0, j + 1 =>
      simp only [List.getElem?_cons_zero, List.getElem?_cons_succ] at h
      exact absurd (List.mem_of_getElem? h.symm) hx
    | i + 1, 0 =>
      simp only [List.getElem?_cons_zero, List.getElem?_cons_succ] at h
      exact absurd (List.mem_of_getElem? h) hx
    | i + 1, j + 1 =>
      simp only [List.getElem?_cons_succ] at h
      simp only [List.length_cons] at hi
      rw [nodup_index_inj hxs h (by omega)]

theorem nodup_filter {α : Type} {p : α → Bool} : ∀ {l : List α}, l.Nodup → (l.filter p).Nodup
  | [], _ => List.nodup_nil
  | x :: xs, h => by
    obtain ⟨hx, hxs⟩ := List.nodup_cons.mp h
    unfold List.filter
    split
    · exact List.nodup_cons.mpr ⟨fun hm => hx (List.mem_filter.mp hm).1, nodup_filter hxs⟩
    · exact nodup_filter hxs

theorem lexRows_nodup (E : Env) (L : Lexicon) : (lexRows E L).Nodup :=
  nodup_filter (nodup_dedup _)

/-! ## The rule map -/

/-- The rule of lexical row `i`. -/
theorem lexRules_get (E : Env) (L : Lexicon) (i : Nat) :
    (lexRules E L)[i]? = ((lexRows E L)[i]?).map fun r =>
      { lhs := r.lhs, rhs := r.rhs, act := relationalFolRows.size + i, tag := r.tag } := by
  unfold lexRules
  simp

theorem lexActs_get (E : Env) (L : Lexicon) (i : Nat) :
    (lexActs E L)[i]? = ((lexRows E L)[i]?).map fun r => r.act.action (rhsTys r.rhs) := by
  unfold lexActs
  simp

theorem fixedActs_size : fixedActs.size = relationalFolRows.size := by
  unfold fixedActs
  simp

theorem fixedRules_base {profiles : List String} (h : profiles = ["relational-fol@0"]) :
    fixedRules profiles = relationalFolRows.mapIdx fun i r =>
      { lhs := r.lhs, rhs := r.rhs, act := i, tag := r.tag } := by
  subst h
  rfl

theorem rename_id : ∀ (X : Sym Terminal), Sym.rename (fun A => A) X = X
  | .t _ => rfl
  | .n _ => rfl

theorem map_rename_id : ∀ (xs : List (Sym Terminal)), xs.map (Sym.rename fun A => A) = xs
  | [] => rfl
  | x :: xs => by rw [List.map_cons, rename_id, map_rename_id xs]

/-- The map of `grammar_extension`: a fixed rule to itself, a lexical rule to the rule of the same row. -/
def extensionMap (E : Env) (L : Lexicon) (E2 : Env) (L2 : Lexicon) : RuleMap where
  rule r :=
    if r < relationalFolRows.size then r
    else
      match (lexRows E L)[r - relationalFolRows.size]? with
      | some row => relationalFolRows.size + indexIn row (lexRows E2 L2)
      | none => r
  nt A := A

theorem grammar_extension : ∀ (E : Env) (O : Overlay) (L : Lexicon) (E2 : Env) (O2 : Overlay) (L2 : Lexicon),
    Extends E O L E2 O2 L2 →
    ∃ e : RuleMap, e.Ok (grammar E L) (grammar E2 L2) (acts E L) (acts E2 L2) := by
  intro E O L E2 O2 L2 ⟨hE, hL, _, _⟩
  have hbase : E.profiles = ["relational-fol@0"] := hE.1
  have hbase2 : E2.profiles = ["relational-fol@0"] := hE.2.1.trans hbase
  have hsub := lexRows_sub hE hL
  have hF : (fixedRules E.profiles).size = relationalFolRows.size := by
    rw [fixedRules_base hbase]; simp
  have hF2 : (fixedRules E2.profiles).size = relationalFolRows.size := by
    rw [fixedRules_base hbase2]; simp
  refine ⟨extensionMap E L E2 L2, rfl, ?_, ?_⟩
  · -- injective
    intro r r2 hr hr2 h
    simp only [grammar, Array.size_append, hF] at hr hr2
    unfold extensionMap at h
    simp only at h
    by_cases h1 : r < relationalFolRows.size <;> by_cases h2 : r2 < relationalFolRows.size
    · simpa [h1, h2] using h
    · simp only [h1, h2, if_true, if_false] at h
      split at h <;> omega
    · simp only [h1, h2, if_true, if_false] at h
      split at h <;> omega
    · simp only [h1, h2, if_false] at h
      have hl1 : r - relationalFolRows.size < (lexRows E L).length := by
        simp [lexRules] at hr; omega
      have hl2 : r2 - relationalFolRows.size < (lexRows E L).length := by
        simp [lexRules] at hr2; omega
      have g1 := List.getElem?_eq_getElem hl1
      have g2 := List.getElem?_eq_getElem hl2
      rw [g1, g2] at h
      simp only [Nat.add_left_cancel_iff] at h
      have m1 := indexIn_get (hsub _ (List.getElem_mem hl1))
      have m2 := indexIn_get (hsub _ (List.getElem_mem hl2))
      rw [h, m2] at m1
      have heq := Option.some.inj m1
      have := nodup_index_inj (lexRows_nodup E L) (i := r - relationalFolRows.size)
        (j := r2 - relationalFolRows.size) (by rw [g1, g2, heq]) hl1
      omega
  · -- rules
    intro r R hR
    unfold extensionMap
    by_cases h1 : r < relationalFolRows.size
    · simp only [h1, if_true]
      have hR' : (fixedRules E.profiles)[r]? = some R := by
        simp only [grammar] at hR
        rwa [Array.getElem?_append_left (by rw [hF]; exact h1)] at hR
      refine ⟨R, ?_, rfl, (map_rename_id _).symm, ?_⟩
      · simp only [grammar]
        rw [Array.getElem?_append_left (by rw [hF2]; exact h1), hbase2, ← hbase, hR']
      · have hact : R.act = r := by
          rw [fixedRules_base hbase] at hR'
          simp [Array.getElem?_mapIdx] at hR'
          obtain ⟨_, _, rfl⟩ := hR'
          rfl
        simp only [acts]
        rw [hact, Array.getElem?_append_left (by rw [fixedActs_size]; exact h1),
          Array.getElem?_append_left (by rw [fixedActs_size]; exact h1)]
    · simp only [h1, if_false]
      have hR' : (lexRules E L)[r - relationalFolRows.size]? = some R := by
        simp only [grammar] at hR
        rwa [Array.getElem?_append_right (by rw [hF]; omega), hF] at hR
      rw [lexRules_get] at hR'
      cases hrow : (lexRows E L)[r - relationalFolRows.size]? with
      | none => rw [hrow] at hR'; cases hR'
      | some row =>
        rw [hrow] at hR'
        simp only [Option.map_some, Option.some.injEq] at hR'
        subst hR'
        have hm := indexIn_get (hsub row (List.mem_of_getElem? hrow))
        refine ⟨{ lhs := row.lhs, rhs := row.rhs,
                  act := relationalFolRows.size + indexIn row (lexRows E2 L2), tag := row.tag }, ?_, rfl, (map_rename_id _).symm, ?_⟩
        · simp only [grammar]
          rw [Array.getElem?_append_right (by rw [hF2]; omega), hF2, Nat.add_sub_cancel_left, lexRules_get, hm]
          rfl
        · simp only [acts]
          rw [Array.getElem?_append_right (by rw [fixedActs_size]; omega), fixedActs_size, Nat.add_sub_cancel_left,
            Array.getElem?_append_right (by rw [fixedActs_size]; omega), fixedActs_size, Nat.add_sub_cancel_left,
            lexActs_get, lexActs_get, hm, hrow]

end VE.EnglishGrammar
