import VE.EnglishGrammar.Read
import VE.Grammar.Extension

/-! Extensions of an English environment and lexicon (docs/spec/english-lean-s2.md 2.13, 5.4 and 5.6;
docs/spec/english-lean-s3.md 2.13, 5.4 and 5.5).

`Extends E O L E2 O2 L2` holds when both environments have the same profile list and the same
`alternatives` block, every symbol of `E` is a symbol of `E2` with the same signature (and, for a
predicate, the same `functional` and `total` flags), every selection of `L` is a selection of `L2`, and both
lexicons are valid. Under it the grammar of `E` and `L` maps into the grammar of `E2` and `L2` rule for
rule (`grammar_extension`): the fixed rules are the same array with the same closed actions, because the
profile lists are equal, and every lexical row of `L` is a lexical row of `L2` after the property
nonterminal of each value sort of `E` is renamed to that sort's nonterminal in `E2` (`propRename`): each row
is built from one lexicon entry, the signature and flags of its symbol and, for the guard family, the block.
The map sends a fixed rule to itself and a lexical rule to the first rule of `L2` with the renamed row; it
is injective because repeated rows were dropped and the renaming is injective on the nonterminals that rows
of `E` name (`InDom`).
-/

namespace VE.EnglishGrammar
open VE.Grammar

def lexiconSub (L L2 : Lexicon) : Prop :=
  (∀ x ∈ L.nouns, x ∈ L2.nouns) ∧ (∀ x ∈ L.letters, x ∈ L2.letters) ∧
  (∀ x ∈ L.wordings, x ∈ L2.wordings) ∧ (∀ x ∈ L.negatives, x ∈ L2.negatives) ∧
  (∀ x ∈ L.aliases, x ∈ L2.aliases) ∧ (∀ x ∈ L.spellings, x ∈ L2.spellings)

def envSub (E E2 : Env) : Prop :=
  E2.profiles = E.profiles ∧ E2.alternatives = E.alternatives ∧
  (∀ s ∈ E.sorts, ∃ s2 ∈ E2.sorts, s2.name = s.name) ∧
  (∀ p ∈ E.predicates, ∃ q ∈ E2.predicates, q.name = p.name ∧ q.arity = p.arity ∧ q.args = p.args ∧
    q.functional = p.functional ∧ q.total = p.total) ∧
  (∀ c ∈ E.constants, ∃ c2 ∈ E2.constants, c2.name = c.name ∧ c2.sort = c.sort)

def Extends (E : Env) (O : Overlay) (L : Lexicon) (E2 : Env) (O2 : Overlay) (L2 : Lexicon) : Prop :=
  envSub E E2 ∧ lexiconSub L L2 ∧ L.valid E O = true ∧ L2.valid E2 O2 = true

/-! ## List facts -/

theorem flatMap_sub {α β γ : Type} {l1 : List α} {l2 : List β} {f : α → List γ} {g : β → List γ}
    (h : ∀ x ∈ l1, ∃ y ∈ l2, ∀ r ∈ f x, r ∈ g y) : ∀ r ∈ l1.flatMap f, r ∈ l2.flatMap g := by
  intro r hr
  obtain ⟨x, hx, hrx⟩ := List.mem_flatMap.mp hr
  obtain ⟨y, hy, hxy⟩ := h x hx
  exact List.mem_flatMap.mpr ⟨y, hy, hxy r hrx⟩

theorem flatMap_mono {α γ : Type} {l1 l2 : List α} {f : α → List γ} (h : ∀ x ∈ l1, x ∈ l2) :
    ∀ r ∈ l1.flatMap f, r ∈ l2.flatMap f :=
  flatMap_sub fun x hx => ⟨x, h x hx, fun _ hr => hr⟩

/-- Each part of a concatenation maps into the corresponding part. -/
theorem append_map {α : Type} {P : α → α} {a b a2 b2 : List α} (ha : ∀ r ∈ a, P r ∈ a2)
    (hb : ∀ r ∈ b, P r ∈ b2) : ∀ r ∈ a ++ b, P r ∈ a2 ++ b2 := by
  intro r hr
  rcases List.mem_append.mp hr with h | h
  · exact List.mem_append_left _ (ha r h)
  · exact List.mem_append_right _ (hb r h)

theorem append_all {α : Type} {Q : α → Prop} {a b : List α} (ha : ∀ r ∈ a, Q r) (hb : ∀ r ∈ b, Q r) :
    ∀ r ∈ a ++ b, Q r := by
  intro r hr
  rcases List.mem_append.mp hr with h | h
  · exact ha r h
  · exact hb r h

theorem flatMap_all {α β : Type} {Q : β → Prop} {l : List α} {f : α → List β} (h : ∀ x ∈ l, ∀ r ∈ f x, Q r) :
    ∀ r ∈ l.flatMap f, Q r := by
  intro r hr
  obtain ⟨x, hx, hrx⟩ := List.mem_flatMap.mp hr
  exact h x hx r hrx

/-! ## Positions in a list without repeats -/

theorem indexIn_get {α : Type} [DecidableEq α] {a : α} : ∀ {l : List α}, a ∈ l → l[indexIn a l]? = some a
  | [], h => absurd h List.not_mem_nil
  | x :: xs, h => by
    unfold indexIn
    by_cases hx : x = a
    · simp [hx]
    · simp only [hx, if_false, List.getElem?_cons_succ]
      exact indexIn_get ((List.mem_cons.mp h).resolve_left (Ne.symm hx))

theorem indexIn_lt {α : Type} [DecidableEq α] {a : α} {l : List α} (h : a ∈ l) : indexIn a l < l.length :=
  (List.getElem?_eq_some_iff.mp (indexIn_get h)).1

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

/-! ## The renaming of property nonterminals (S3 spec 2.13) -/

/-- The property nonterminal of the `i`-th value sort of `E` to that sort's nonterminal in `E2`; every other
number to itself. -/
def propRename (E E2 : Env) (A : Nat) : Nat :=
  if ntProperty ≤ A ∧ A < ntProperty + (valueSorts E).length then
    propertyNt E2 (((valueSorts E)[A - ntProperty]?).getD "")
  else A

/-- The nonterminals that rows of `E` name: the catalogue's, and the property nonterminal of a value sort. -/
def InDom (E : Env) (A : Nat) : Prop := A < ntProperty ∨ ∃ s ∈ valueSorts E, A = propertyNt E s

/-- The nonterminals of a row satisfy `P`. -/
def LexRow.NtsIn (P : Nat → Prop) (r : LexRow) : Prop := P r.lhs ∧ ∀ A, Sym.n A ∈ r.rhs → P A

/-- A row whose nonterminals are all in the catalogue. -/
def LexRow.Small (r : LexRow) : Prop := r.NtsIn (· < ntProperty)

/-- A row with its nonterminals renamed. -/
def LexRow.rename (ρ : Nat → Nat) (r : LexRow) : LexRow := { r with lhs := ρ r.lhs, rhs := r.rhs.map (Sym.rename ρ) }

section Renaming

variable {E E2 : Env}

theorem valueSorts_sub (hE : envSub E E2) : ∀ s ∈ valueSorts E, s ∈ valueSorts E2 := by
  obtain ⟨hprof, _, _, hp, _⟩ := hE
  intro s hs
  unfold valueSorts at hs ⊢
  rw [hprof]
  split at hs
  · rename_i hd
    rw [if_pos hd]
    rw [List.mem_reverse, mem_dedup, List.mem_reverse, List.mem_filterMap] at hs ⊢
    obtain ⟨d, hd, hv⟩ := hs
    obtain ⟨q, hq, _, _, hqa, hqf, hqt⟩ := hp d hd
    refine ⟨q, hq, ?_⟩
    unfold valueSortOf at hv ⊢
    rw [hqa, hqf, hqt]
    exact hv
  · exact absurd hs List.not_mem_nil

theorem rename_small {A : Nat} (h : A < ntProperty) : propRename E E2 A = A := by
  unfold propRename
  rw [if_neg (by omega)]

theorem rename_prop {s : String} (hs : s ∈ valueSorts E) : propRename E E2 (propertyNt E s) = propertyNt E2 s := by
  have hl := indexIn_lt hs
  have hg := indexIn_get hs
  unfold propRename propertyNt
  rw [if_pos (by omega), Nat.add_sub_cancel_left, hg]
  rfl

theorem propertyNt_ge (E : Env) (s : String) : ntProperty ≤ propertyNt E s := by
  unfold propertyNt; omega

theorem propRename_inj (hE : envSub E E2) {A B : Nat} (hA : InDom E A) (hB : InDom E B)
    (h : propRename E E2 A = propRename E E2 B) : A = B := by
  rcases hA with hA | ⟨s, hs, rfl⟩ <;> rcases hB with hB | ⟨t, ht, rfl⟩
  · rwa [rename_small hA, rename_small hB] at h
  · rw [rename_small hA, rename_prop ht] at h
    have := propertyNt_ge E2 t
    omega
  · rw [rename_prop hs, rename_small hB] at h
    have := propertyNt_ge E2 s
    omega
  · rw [rename_prop hs, rename_prop ht] at h
    unfold propertyNt at h
    have hi : indexIn s (valueSorts E2) = indexIn t (valueSorts E2) := by omega
    have g1 := indexIn_get (valueSorts_sub hE s hs)
    have g2 := indexIn_get (valueSorts_sub hE t ht)
    rw [hi, g2] at g1
    rw [Option.some.inj g1]

theorem ty_propertyNt {L : Lexicon} {s : String} (hs : s ∈ valueSorts E) : ty E L (propertyNt E s) = .adjective := by
  have hl := indexIn_lt hs
  unfold ty propertyNt
  rw [if_neg (by omega), if_pos (by omega)]

theorem ty_rename (hE : envSub E E2) {L L2 : Lexicon} {A : Nat} (hA : InDom E A) :
    ty E2 L2 (propRename E E2 A) = ty E L A := by
  rcases hA with hA | ⟨s, hs, rfl⟩
  · rw [rename_small hA]
    unfold ty
    rw [if_pos hA, if_pos hA]
  · rw [rename_prop hs, ty_propertyNt hs, ty_propertyNt (valueSorts_sub hE s hs)]

theorem map_rename_small : ∀ (xs : List (Sym Terminal)), (∀ A, Sym.n A ∈ xs → A < ntProperty) →
    xs.map (Sym.rename (propRename E E2)) = xs
  | [], _ => rfl
  | x :: xs, h => by
    rw [List.map_cons, map_rename_small xs (fun A hA => h A (List.mem_cons_of_mem _ hA))]
    cases x with
    | t a => rfl
    | n A => simp only [Sym.rename, rename_small (h A List.mem_cons_self)]

theorem LexRow.Small.rename_eq {r : LexRow} (h : r.Small) : r.rename (propRename E E2) = r := by
  obtain ⟨tag, lhs, rhs, act⟩ := r
  simp only [LexRow.rename, rename_small h.1, map_rename_small rhs h.2]

theorem LexRow.Small.dom {r : LexRow} (h : r.Small) : r.NtsIn (InDom E) :=
  ⟨Or.inl h.1, fun A hA => Or.inl (h.2 A hA)⟩

theorem map_rename_inj (hE : envSub E E2) : ∀ (xs ys : List (Sym Terminal)), (∀ A, Sym.n A ∈ xs → InDom E A) →
    (∀ A, Sym.n A ∈ ys → InDom E A) →
    xs.map (Sym.rename (propRename E E2)) = ys.map (Sym.rename (propRename E E2)) → xs = ys
  | [], [], _, _, _ => rfl
  | [], _ :: _, _, _, h => by simp at h
  | _ :: _, [], _, _, h => by simp at h
  | x :: xs, y :: ys, hx, hy, h => by
    simp only [List.map_cons, List.cons.injEq] at h
    rw [map_rename_inj hE xs ys (fun A hA => hx A (List.mem_cons_of_mem _ hA))
      (fun A hA => hy A (List.mem_cons_of_mem _ hA)) h.2]
    congr 1
    cases x with
    | t a => cases y with
      | t b => simp only [Sym.rename, Sym.t.injEq] at h; rw [h.1]
      | n B => simp [Sym.rename] at h
    | n A => cases y with
      | t b => simp [Sym.rename] at h
      | n B =>
        simp only [Sym.rename, Sym.n.injEq] at h
        rw [propRename_inj hE (hx A List.mem_cons_self) (hy B List.mem_cons_self) h.1]

theorem LexRow.rename_inj (hE : envSub E E2) {r1 r2 : LexRow} (h1 : r1.NtsIn (InDom E)) (h2 : r2.NtsIn (InDom E))
    (h : r1.rename (propRename E E2) = r2.rename (propRename E E2)) : r1 = r2 := by
  obtain ⟨tag1, lhs1, rhs1, act1⟩ := r1
  obtain ⟨tag2, lhs2, rhs2, act2⟩ := r2
  simp only [LexRow.rename, LexRow.mk.injEq] at h
  obtain ⟨ht, hl, hr, ha⟩ := h
  have e1 : lhs1 = lhs2 := propRename_inj hE h1.1 h2.1 hl
  have e2 : rhs1 = rhs2 := map_rename_inj hE rhs1 rhs2 h1.2 h2.2 hr
  rw [ht, ha, e1, e2]

end Renaming

/-! ## The nonterminals of the rows -/

theorem textSyms_noNt {t : String} {k : Tok → Terminal} {syms : List (Sym Terminal)} (h : textSyms t k = some syms) :
    ∀ A, Sym.n A ∉ syms := by
  intro A hA
  unfold textSyms at h
  cases ht : sentenceTokens t with
  | none => rw [ht] at h; cases h
  | some toks =>
    rw [ht] at h
    simp only [Option.map_some, Option.some.injEq] at h
    subst h
    simp at hA

theorem wordingSyms_nts {w : String} {o : List Nat} {syms : List (Sym Terminal)} (h : wordingSyms w = some (o, syms)) :
    ∀ A, Sym.n A ∈ syms → A = ntTerm := by
  intro A hA
  unfold wordingSyms at h
  cases ht : wordingTokens w with
  | none => rw [ht] at h; cases h
  | some x =>
    obtain ⟨order, toks⟩ := x
    rw [ht] at h
    simp only [Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
    obtain ⟨_, rfl⟩ := h
    obtain ⟨t, _, he⟩ := List.mem_map.mp hA
    split at he
    · cases he; rfl
    · split at he <;> cases he

theorem wordingSymsBy_nts {w : String} {slot : Nat → Nat} {o : List Nat} {syms : List (Sym Terminal)}
    (h : wordingSymsBy w slot = some (o, syms)) : ∀ A, Sym.n A ∈ syms → ∃ k, A = slot k := by
  intro A hA
  unfold wordingSymsBy at h
  cases ht : wordingTokens w with
  | none => rw [ht] at h; cases h
  | some x =>
    obtain ⟨order, toks⟩ := x
    rw [ht] at h
    simp only [Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
    obtain ⟨_, rfl⟩ := h
    obtain ⟨t, _, he⟩ := List.mem_map.mp hA
    split at he
    · split at he
      · rename_i k _
        cases he; exact ⟨k, rfl⟩
      · cases he
    · cases he

/-- A row whose nonterminals are below `ntProperty`. -/
theorem small_of {r : LexRow} (hl : r.lhs < ntProperty) (hr : ∀ A, Sym.n A ∈ r.rhs → A < ntProperty) : r.Small :=
  ⟨hl, hr⟩

/-- Terminals only. -/
theorem noNt_of {xs : List (Sym Terminal)} (h : ∀ A, Sym.n A ∉ xs) : ∀ A, Sym.n A ∈ xs → A < ntProperty :=
  fun A hA => absurd hA (h A)

theorem clauseRows_small {p w : String} {neg : Bool} {suf : String} : ∀ r ∈ clauseRows p w neg suf, r.Small := by
  intro r hr
  unfold clauseRows at hr
  split at hr
  · simp at hr
  · rename_i order syms hw
    have hs := wordingSyms_nts hw
    simp only [List.mem_append, List.mem_cons, List.mem_nil_iff, or_false] at hr
    rcases hr with (rfl | rfl) | h
    · exact small_of (by dsimp only; decide) fun A hA => by rw [hs A hA]; decide
    · refine small_of (by dsimp only; decide) fun A hA => ?_
      simp only at hA
      split at hA
      · rw [hs A (List.mem_of_mem_tail hA)]; decide
      · rw [hs A hA]; decide
    · split at h
      · rename_i o ho
        simp only [List.mem_cons, List.mem_nil_iff, or_false] at h
        subst h
        split at ho
        · obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.mp ho
          have := wordingSyms_nts hx
          exact small_of (by dsimp only; decide) fun A hA => by rw [this A hA]; decide
        · cases ho
      · simp at h

theorem slot_small (args : List String) (k : Nat) :
    (if (args.getD k "" == intSort) = true then ntIntTerm else ntTerm) < ntProperty := by
  split <;> decide

theorem clauseRowsOrder_small {p w : String} {neg : Bool} {suf : String} {args : List String} :
    ∀ r ∈ clauseRowsOrder p w neg suf args, r.Small := by
  intro r hr
  unfold clauseRowsOrder at hr
  dsimp only at hr
  split at hr
  · simp at hr
  · rename_i order syms hw
    have hs := wordingSymsBy_nts hw
    simp only [List.mem_append, List.mem_cons, List.mem_nil_iff, or_false] at hr
    rcases hr with (rfl | h) | h
    · exact small_of (by dsimp only; decide) fun A hA => by obtain ⟨k, rfl⟩ := hs A hA; exact slot_small args k
    · split at h
      · rename_i x hx
        simp only [List.mem_cons, List.mem_nil_iff, or_false] at h
        subst h
        split at hx
        · cases hx
          exact small_of (by dsimp only; decide) fun A hA => by
            obtain ⟨k, rfl⟩ := hs A (List.mem_of_mem_tail hA); exact slot_small args k
        · cases hx
      · simp at h
    · split at h
      · rename_i o ho
        simp only [List.mem_cons, List.mem_nil_iff, or_false] at h
        subst h
        split at ho
        · obtain ⟨x, hx, rfl⟩ := Option.map_eq_some_iff.mp ho
          have := wordingSymsBy_nts hx
          exact small_of (by dsimp only; decide) fun A hA => by obtain ⟨k, rfl⟩ := this A hA; exact slot_small args k
        · cases ho
      · simp at h

theorem wordingRows_small {E : Env} {p w : String} {neg : Bool} {suf : String} :
    ∀ r ∈ wordingRows E p w neg suf, r.Small := by
  unfold wordingRows
  split
  · exact flatMap_all fun _ _ => clauseRowsOrder_small
  · exact clauseRows_small

theorem spellingRows_small {c s sp : String} : ∀ r ∈ spellingRows c s sp, r.Small := by
  intro r hr
  unfold spellingRows at hr
  split at hr
  · simp at hr
  · simp only [List.mem_append, List.mem_cons, List.mem_nil_iff, or_false] at hr
    rcases hr with (rfl | h) | h
    · exact small_of (by dsimp only; decide) fun A hA => by simp at hA
    · split at h
      · simp only [List.mem_cons, List.mem_nil_iff, or_false] at h; subst h
        exact small_of (by dsimp only; decide) fun A hA => by simp at hA
      · simp at h
    · split at h
      · simp only [List.mem_cons, List.mem_nil_iff, or_false] at h; subst h
        exact small_of (by dsimp only; decide) fun A hA => by
          simp only [List.mem_cons] at hA
          rcases hA with hA | hA
          · cases hA
          · have := List.mem_of_mem_drop hA
            simp at this
      · simp at h

theorem intConstantRows_small {c sp : String} : ∀ r ∈ intConstantRows c sp, r.Small := by
  intro r hr
  unfold intConstantRows at hr
  split at hr
  · simp at hr
  · rename_i syms hs
    have := noNt_of (textSyms_noNt hs)
    simp only [List.mem_append, List.mem_cons, List.mem_nil_iff, or_false] at hr
    rcases hr with rfl | h
    · exact small_of (by dsimp only; decide) this
    · split at h
      · simp only [List.mem_cons, List.mem_nil_iff, or_false] at h; subst h
        exact small_of (by dsimp only; decide) this
      · simp at h

theorem constantRows_small {E : Env} {c s sp : String} : ∀ r ∈ constantRows E c s sp, r.Small := by
  unfold constantRows
  split
  · exact intConstantRows_small
  · exact spellingRows_small

theorem adjectiveRows_small {L : Lexicon} {p s a : String} : ∀ r ∈ adjectiveRows L p s a, r.Small := by
  intro r hr
  unfold adjectiveRows at hr
  rcases List.mem_append.mp hr with h | h
  · simp only [List.mem_cons, List.mem_nil_iff, or_false] at h; subst h
    exact small_of (by dsimp only; decide) fun A hA => by simp at hA
  · obtain ⟨⟨_, n⟩, _, hx⟩ := List.mem_flatMap.mp h
    cases hns : textSyms n contentTerminal with
    | none => simp [hns] at hx
    | some ns =>
      have := textSyms_noNt hns
      simp only [hns, List.mem_cons, List.mem_nil_iff, or_false] at hx
      rcases hx with rfl | rfl | rfl
      · refine small_of (by dsimp only; decide) fun A hA => ?_
        simp only [List.mem_cons] at hA
        rcases hA with hA | hA
        · cases hA
        · exact absurd hA (this A)
      · exact small_of (by dsimp only; decide) fun A hA => by simp at hA
      · exact small_of (by dsimp only; decide) fun A hA => by simp at hA

/-- Every nonterminal of the symbols is in the catalogue. -/
def symsSmall (xs : List (Sym Terminal)) : Bool :=
  xs.all fun
    | .n A => decide (A < ntProperty)
    | .t _ => true

theorem symsSmall_iff {xs : List (Sym Terminal)} : symsSmall xs = true ↔ ∀ A, Sym.n A ∈ xs → A < ntProperty := by
  unfold symsSmall
  rw [List.all_eq_true]
  constructor
  · intro h A hA
    simpa using h _ hA
  · intro h x hx
    cases x with
    | n A => simpa using h A hx
    | t _ => rfl

theorem symsSmall_append (xs ys : List (Sym Terminal)) : symsSmall (xs ++ ys) = (symsSmall xs && symsSmall ys) := by
  unfold symsSmall; rw [List.all_append]

theorem symsSmall_nil : symsSmall [] = true := rfl

theorem symsSmall_cons_t (a : Terminal) (xs : List (Sym Terminal)) : symsSmall (.t a :: xs) = symsSmall xs := rfl

theorem symsSmall_cons_n (A : Nat) (xs : List (Sym Terminal)) :
    symsSmall (.n A :: xs) = (decide (A < ntProperty) && symsSmall xs) := rfl

theorem symsSmall_textSyms {t : String} {k : Tok → Terminal} {syms : List (Sym Terminal)}
    (h : textSyms t k = some syms) : symsSmall syms = true :=
  symsSmall_iff.mpr (noNt_of (textSyms_noNt h))

theorem guardRows_small {E : Env} {B : AltBlock} {n : String} : ∀ r ∈ guardRows E B n, r.Small := by
  intro r hr
  unfold guardRows at hr
  split at hr
  · rename_i N Nc hN hNc
    have h1 := symsSmall_textSyms hN
    have h2 := symsSmall_textSyms hNc
    simp only [List.mem_cons, List.mem_nil_iff, or_false] at hr
    rcases hr with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl
    all_goals refine small_of (by dsimp only; decide) (symsSmall_iff.mp ?_)
    all_goals simp [symsSmall_append, symsSmall_nil, symsSmall_cons_t, symsSmall_cons_n, h1, h2, ntTerm,
      ntAltVerbPhrase, ntProperty]
  · simp at hr

theorem smallRow_of {r : LexRow} (hl : r.lhs < ntProperty) (h : symsSmall r.rhs = true) : r.Small :=
  small_of hl (symsSmall_iff.mp h)

/-- Every row of `E` names only the catalogue's nonterminals and the property nonterminals of its value
sorts. -/
theorem lexRowsAll_dom (E : Env) (L : Lexicon) : ∀ r ∈ lexRowsAll E L, r.NtsIn (InDom E) := by
  unfold lexRowsAll
  refine append_all (append_all (append_all (append_all (append_all (append_all (append_all (append_all
    (append_all (append_all (append_all ?_ ?_) ?_) ?_) ?_) ?_) ?_) ?_) ?_) ?_) ?_) ?_
  · exact flatMap_all fun _ _ r hr => (wordingRows_small r hr).dom
  · exact flatMap_all fun _ _ r hr => (wordingRows_small r hr).dom
  · exact flatMap_all fun _ _ r hr => (wordingRows_small r hr).dom
  · refine flatMap_all fun ⟨_, n⟩ _ r hr => ?_
    cases hns : textSyms n contentTerminal with
    | none => simp [hns] at hr
    | some ns =>
      simp only [hns, List.mem_cons, List.mem_nil_iff, or_false] at hr; subst hr
      exact (smallRow_of (by dsimp only; decide) (symsSmall_textSyms hns)).dom
  · intro r hr
    obtain ⟨x, _, rfl⟩ := List.mem_map.mp hr
    exact (small_of (by dsimp only; decide) fun A hA => by simp at hA).dom
  · exact flatMap_all fun _ _ => flatMap_all fun _ _ r hr => (constantRows_small r hr).dom
  · refine flatMap_all fun ⟨p, w⟩ _ r hr => ?_
    cases ha : adjectiveOf w with
    | none => simp only [ha] at hr; exact absurd hr List.not_mem_nil
    | some a =>
      simp only [ha] at hr
      obtain ⟨d, _, hd⟩ := List.mem_flatMap.mp hr
      cases hargs : d.args with
      | nil => simp only [hargs] at hd; exact absurd hd List.not_mem_nil
      | cons s rest =>
        cases rest with
        | nil => simp only [hargs] at hd; exact (adjectiveRows_small r hd).dom
        | cons _ _ => simp only [hargs] at hd; exact absurd hd List.not_mem_nil
  · refine flatMap_all fun ⟨p, w⟩ _ r hr => ?_
    by_cases hpw : (p == "owns" && w == "{0} owns {1}") = true
    · simp only [hpw, if_true] at hr
      obtain ⟨d, _, hd⟩ := List.mem_flatMap.mp hr
      cases hargs : d.args with
      | nil => simp only [hargs] at hd; exact absurd hd List.not_mem_nil
      | cons s1 rest =>
        cases rest with
        | nil => simp only [hargs] at hd; exact absurd hd List.not_mem_nil
        | cons s2 rest2 =>
          cases rest2 with
          | nil =>
            simp only [hargs, List.mem_cons, List.mem_nil_iff, or_false] at hd; subst hd
            exact (small_of (by dsimp only; decide) fun A hA => by simp at hA).dom
          | cons _ _ => simp only [hargs] at hd; exact absurd hd List.not_mem_nil
    · simp only [hpw] at hr; exact absurd hr List.not_mem_nil
  · refine flatMap_all fun d _ r hr => ?_
    split at hr
    · split at hr
      · rename_i hq
        cases hq' : textSyms (jsonQuote d.name) contentTerminal with
        | none => simp [hq'] at hr
        | some q =>
          simp only [hq', List.mem_cons, List.mem_nil_iff, or_false] at hr; subst hr
          exact (smallRow_of (by dsimp only; decide) (symsSmall_textSyms hq')).dom
      · simp at hr
    · simp at hr
  · split
    · refine flatMap_all fun d _ r hr => ?_
      unfold attributeRows at hr
      split at hr
      · rename_i _ b rs _ hrs
        have hn := symsSmall_textSyms hrs
        split at hr
        · simp only [List.mem_append, List.mem_cons, List.mem_nil_iff, or_false] at hr
          rcases hr with rfl | h
          · refine (smallRow_of (by dsimp only; decide) ?_).dom
            simp [symsSmall_append, symsSmall_nil, symsSmall_cons_t, symsSmall_cons_n, hn, ntTerm, ntProperty]
          · split at h
            · rename_i hb
              simp only [List.mem_cons, List.mem_nil_iff, or_false] at h; subst h
              refine ⟨Or.inl (by dsimp only; decide), fun A hA => ?_⟩
              simp only [List.mem_append, List.mem_cons, List.mem_nil_iff, or_false] at hA
              rcases hA with ((hA | hA) | hA | hA | hA) | hA
              · cases hA
              · exact absurd hA (textSyms_noNt hrs A)
              · cases hA
              · cases hA; exact Or.inl (by decide)
              · cases hA
              · cases hA; exact Or.inr ⟨b, List.contains_iff_mem.mp hb, rfl⟩
            · simp at h
        · simp at hr
      · simp at hr
    · simp
  · split
    · refine flatMap_all fun d _ r hr => ?_
      unfold propertyRows at hr
      split at hr
      · rename_i s ps _ hps
        split at hr
        · rename_i hs
          simp only [List.mem_cons, List.mem_nil_iff, or_false] at hr; subst hr
          exact ⟨Or.inr ⟨s, List.contains_iff_mem.mp hs, rfl⟩, fun A hA => absurd hA (textSyms_noNt hps A)⟩
        · simp at hr
      · simp at hr
    · simp
  · split
    · split
      · exact flatMap_all fun _ _ r hr => (guardRows_small r hr).dom
      · simp
    · simp

/-! ## Every lexical row of the smaller grammar is a row of the larger, renamed -/

section Sub

variable {E E2 : Env} {L L2 : Lexicon}

theorem adjectiveRows_sub (hn : ∀ x ∈ L.nouns, x ∈ L2.nouns) (p s a : String) :
    ∀ r ∈ adjectiveRows L p s a, r ∈ adjectiveRows L2 p s a := by
  intro r hr
  unfold adjectiveRows at hr ⊢
  rcases List.mem_append.mp hr with h | h
  · exact List.mem_append_left _ h
  · refine List.mem_append_right _ (flatMap_mono (fun x hx => ?_) r h)
    obtain ⟨hx1, hx2⟩ := List.mem_filter.mp hx
    exact List.mem_filter.mpr ⟨hn x hx1, hx2⟩

/-- A declaration of `E` named `p` has a declaration of `E2` named `p` with the same signature. -/
theorem decl_sub (hp : ∀ p ∈ E.predicates, ∃ q ∈ E2.predicates, q.name = p.name ∧
    q.arity = p.arity ∧ q.args = p.args ∧ q.functional = p.functional ∧ q.total = p.total) {p : String} {d : PredDecl}
    (hd : d ∈ declsOf E p) : ∃ q ∈ declsOf E2 p, q.args = d.args := by
  unfold declsOf at hd ⊢
  obtain ⟨hd1, hd2⟩ := List.mem_filter.mp hd
  obtain ⟨q, hq, hqn, _, hqa, _⟩ := hp d hd1
  exact ⟨q, List.mem_filter.mpr ⟨hq, by rw [hqn]; exact hd2⟩, hqa⟩

theorem wordingRows_sub (hE : envSub E E2) {p w : String} {neg : Bool} {suf : String} :
    ∀ r ∈ wordingRows E p w neg suf, r ∈ wordingRows E2 p w neg suf := by
  obtain ⟨hprof, _, _, hp, _⟩ := hE
  unfold wordingRows
  rw [hprof]
  split
  · refine flatMap_sub fun d hd => ?_
    obtain ⟨q, hq, hqa⟩ := decl_sub hp hd
    exact ⟨q, hq, fun r hr => by rw [hqa]; exact hr⟩
  · exact fun _ h => h

theorem constantRows_eq (hprof : E2.profiles = E.profiles) (c s sp : String) :
    constantRows E2 c s sp = constantRows E c s sp := by
  unfold constantRows; rw [hprof]

theorem guardRows_eq (hprof : E2.profiles = E.profiles) (B : AltBlock) (n : String) :
    guardRows E2 B n = guardRows E B n := by
  unfold guardRows Env.risk; rw [hprof]

/-- An attribute row of `E`, renamed, is an attribute row of `E2` for a declaration with the same name,
signature and flags. -/
theorem attributeRows_sub (hE : envSub E E2) {d q : PredDecl} (hn : q.name = d.name) (ha : q.args = d.args)
    (hf : q.functional = d.functional) (ht : q.total = d.total) :
    ∀ r ∈ attributeRows E d, r.rename (propRename E E2) ∈ attributeRows E2 q := by
  intro r hr
  unfold attributeRows at hr ⊢
  rw [hn, ha, hf, ht]
  split at hr
  · rename_i _ b rs _ hrs
    have hs := symsSmall_textSyms hrs
    split at hr
    · rename_i hft
      rw [if_pos hft]
      have hhead : symsSmall (Sym.t (.kw "the") :: rs ++ [.t (.kw "of"), .n ntTerm, .t (.kw "is")]) = true := by
        simp [symsSmall_append, symsSmall_nil, symsSmall_cons_t, symsSmall_cons_n, hs, ntTerm, ntProperty]
      have hmap := map_rename_small (E := E) (E2 := E2) _ (symsSmall_iff.mp hhead)
      simp only [List.mem_append, List.mem_cons, List.mem_nil_iff, or_false] at hr ⊢
      rcases hr with rfl | h
      · left
        simp only [LexRow.rename, List.map_append, rename_small (show ntAtom < ntProperty by decide), hmap,
          List.map_cons, List.map_nil, Sym.rename, rename_small (show ntTerm < ntProperty by decide)]
      · split at h
        · rename_i hb
          simp only [List.mem_cons, List.mem_nil_iff, or_false] at h; subst h
          right
          rw [if_pos (List.contains_iff_mem.mpr (valueSorts_sub hE b (List.contains_iff_mem.mp hb)))]
          simp only [List.mem_cons, List.mem_nil_iff, or_false]
          simp only [LexRow.rename, List.map_append, rename_small (show ntAtom < ntProperty by decide), hmap,
            List.map_cons, List.map_nil, Sym.rename, rename_prop (List.contains_iff_mem.mp hb)]
        · simp at h
    · simp at hr
  · simp at hr

theorem propertyRows_sub (hE : envSub E E2) {d q : PredDecl} (hn : q.name = d.name) (ha : q.args = d.args) :
    ∀ r ∈ propertyRows E d, r.rename (propRename E E2) ∈ propertyRows E2 q := by
  intro r hr
  unfold propertyRows at hr ⊢
  rw [hn, ha]
  split at hr
  · rename_i s ps _ hps
    split at hr
    · rename_i hs
      simp only [List.mem_cons, List.mem_nil_iff, or_false] at hr; subst hr
      rw [if_pos (List.contains_iff_mem.mpr (valueSorts_sub hE s (List.contains_iff_mem.mp hs)))]
      simp only [List.mem_cons, List.mem_nil_iff, or_false, LexRow.rename, rename_prop (List.contains_iff_mem.mp hs),
        map_rename_small ps (noNt_of (textSyms_noNt hps))]
    · simp at hr
  · simp at hr

theorem lexRowsAll_sub (hE : envSub E E2) (hL : lexiconSub L L2) :
    ∀ r ∈ lexRowsAll E L, r.rename (propRename E E2) ∈ lexRowsAll E2 L2 := by
  obtain ⟨hn, hl, hw, hneg, ha, hsp⟩ := hL
  have hE' := hE
  obtain ⟨hprof, halt, _, hp, hc⟩ := hE'
  -- a row of a family whose rows are small is itself, and the same family of `E2` holds it
  have keep : ∀ {a b : List LexRow}, (∀ r ∈ a, r.Small) → (∀ r ∈ a, r ∈ b) →
      ∀ r ∈ a, r.rename (propRename E E2) ∈ b := fun hs hab r hr => by
    rw [(hs r hr).rename_eq]; exact hab r hr
  unfold lexRowsAll
  refine append_map (append_map (append_map (append_map (append_map (append_map (append_map (append_map
    (append_map (append_map (append_map ?_ ?_) ?_) ?_) ?_) ?_) ?_) ?_) ?_) ?_) ?_) ?_
  · exact keep (flatMap_all fun _ _ => wordingRows_small)
      (flatMap_sub fun x hx => ⟨x, hw x hx, wordingRows_sub hE⟩)
  · exact keep (flatMap_all fun _ _ => wordingRows_small)
      (flatMap_sub fun x hx => ⟨x, hneg x hx, wordingRows_sub hE⟩)
  · exact keep (flatMap_all fun _ _ => wordingRows_small)
      (flatMap_sub fun x hx => ⟨x, ha x hx, wordingRows_sub hE⟩)
  · refine keep ?_ (flatMap_mono hn)
    refine flatMap_all fun ⟨_, n⟩ _ r hr => ?_
    cases hns : textSyms n contentTerminal with
    | none => simp [hns] at hr
    | some ns =>
      simp only [hns, List.mem_cons, List.mem_nil_iff, or_false] at hr; subst hr
      exact smallRow_of (by dsimp only; decide) (symsSmall_textSyms hns)
  · refine keep ?_ ?_
    · intro r hr
      obtain ⟨x, _, rfl⟩ := List.mem_map.mp hr
      exact small_of (by dsimp only; decide) fun A hA => by simp at hA
    · intro r hr
      obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hr
      exact List.mem_map.mpr ⟨x, hl x hx, rfl⟩
  · refine keep (flatMap_all fun _ _ => flatMap_all fun _ _ => constantRows_small) ?_
    refine flatMap_sub (fun x hx => ⟨x, hsp x hx, fun r hr => ?_⟩)
    obtain ⟨c, sp⟩ := x
    obtain ⟨d, hd, hrd⟩ := List.mem_flatMap.mp hr
    obtain ⟨hd1, hd2⟩ := List.mem_filter.mp hd
    obtain ⟨c2, hc2, hcn, hcs⟩ := hc d hd1
    refine List.mem_flatMap.mpr ⟨c2, List.mem_filter.mpr ⟨hc2, by rw [hcn]; exact hd2⟩, ?_⟩
    rw [hcs, constantRows_eq hprof]; exact hrd
  · refine keep ?_ ?_
    · refine flatMap_all fun ⟨p, w⟩ _ r hr => ?_
      cases hadj : adjectiveOf w with
      | none => simp only [hadj] at hr; exact absurd hr List.not_mem_nil
      | some a =>
        simp only [hadj] at hr
        obtain ⟨d, _, hd⟩ := List.mem_flatMap.mp hr
        cases hargs : d.args with
        | nil => simp only [hargs] at hd; exact absurd hd List.not_mem_nil
        | cons s rest =>
          cases rest with
          | nil => simp only [hargs] at hd; exact adjectiveRows_small r hd
          | cons _ _ => simp only [hargs] at hd; exact absurd hd List.not_mem_nil
    · refine flatMap_sub (fun x hx => ⟨x, hw x hx, fun r hr => ?_⟩)
      obtain ⟨p, w⟩ := x
      cases hadj : adjectiveOf w with
      | none => simp only [hadj] at hr; exact absurd hr List.not_mem_nil
      | some a =>
        simp only [hadj] at hr ⊢
        obtain ⟨d, hd, hrd⟩ := List.mem_flatMap.mp hr
        obtain ⟨q, hq, hqa⟩ := decl_sub hp hd
        refine List.mem_flatMap.mpr ⟨q, hq, ?_⟩
        rw [hqa]
        cases hargs : d.args with
        | nil => simp only [hargs] at hrd; exact absurd hrd List.not_mem_nil
        | cons s rest =>
          cases rest with
          | nil => simp only [hargs] at hrd ⊢; exact adjectiveRows_sub hn p s a r hrd
          | cons _ _ => simp only [hargs] at hrd; exact absurd hrd List.not_mem_nil
  · refine keep ?_ ?_
    · refine flatMap_all fun ⟨p, w⟩ _ r hr => ?_
      by_cases hpw : (p == "owns" && w == "{0} owns {1}") = true
      · simp only [hpw, if_true] at hr
        obtain ⟨d, _, hd⟩ := List.mem_flatMap.mp hr
        cases hargs : d.args with
        | nil => simp only [hargs] at hd; exact absurd hd List.not_mem_nil
        | cons s1 rest =>
          cases rest with
          | nil => simp only [hargs] at hd; exact absurd hd List.not_mem_nil
          | cons s2 rest2 =>
            cases rest2 with
            | nil =>
              simp only [hargs, List.mem_cons, List.mem_nil_iff, or_false] at hd; subst hd
              exact small_of (by dsimp only; decide) fun A hA => by simp at hA
            | cons _ _ => simp only [hargs] at hd; exact absurd hd List.not_mem_nil
      · simp only [hpw] at hr; exact absurd hr List.not_mem_nil
    · refine flatMap_sub (fun x hx => ⟨x, hw x hx, fun r hr => ?_⟩)
      obtain ⟨p, w⟩ := x
      by_cases hpw : (p == "owns" && w == "{0} owns {1}") = true
      · simp only [hpw, if_true] at hr ⊢
        obtain ⟨d, hd, hrd⟩ := List.mem_flatMap.mp hr
        obtain ⟨q, hq, hqa⟩ := decl_sub hp hd
        exact List.mem_flatMap.mpr ⟨q, hq, by rw [hqa]; exact hrd⟩
      · simp only [hpw] at hr; exact absurd hr List.not_mem_nil
  · refine keep ?_ ?_
    · refine flatMap_all fun d _ r hr => ?_
      split at hr
      · split at hr
        · cases hq' : textSyms (jsonQuote d.name) contentTerminal with
          | none => simp [hq'] at hr
          | some q =>
            simp only [hq', List.mem_cons, List.mem_nil_iff, or_false] at hr; subst hr
            exact smallRow_of (by dsimp only; decide) (symsSmall_textSyms hq')
        · simp at hr
      · simp at hr
    · refine flatMap_sub (fun d hd => ?_)
      obtain ⟨q, hq, hqn, _, hqa, _⟩ := hp d hd
      exact ⟨q, hq, fun r hr => by rw [hqn, hqa]; exact hr⟩
  · rw [hprof]
    split
    · intro r hr
      obtain ⟨d, hd, hrd⟩ := List.mem_flatMap.mp hr
      obtain ⟨q, hq, hqn, _, hqa, hqf, hqt⟩ := hp d hd
      exact List.mem_flatMap.mpr ⟨q, hq, attributeRows_sub hE hqn hqa hqf hqt r hrd⟩
    · simp
  · rw [hprof]
    split
    · intro r hr
      obtain ⟨d, hd, hrd⟩ := List.mem_flatMap.mp hr
      obtain ⟨q, hq, hqn, _, hqa, _⟩ := hp d hd
      exact List.mem_flatMap.mpr ⟨q, hq, propertyRows_sub hE hqn hqa r hrd⟩
    · simp
  · rw [halt, hprof]
    split
    · split
      · refine keep (flatMap_all fun _ _ => guardRows_small) ?_
        refine flatMap_sub fun x hx => ⟨x, ?_, fun r hr => by cases x; simp only at hr ⊢; rw [guardRows_eq hprof]; exact hr⟩
        obtain ⟨hx1, hx2⟩ := List.mem_filter.mp hx
        exact List.mem_filter.mpr ⟨hn x hx1, hx2⟩
      · simp
    · simp

theorem terminatorFree_rename (ρ : Nat → Nat) (r : LexRow) : (r.rename ρ).terminatorFree = r.terminatorFree := by
  obtain ⟨tag, lhs, rhs, act⟩ := r
  unfold LexRow.terminatorFree LexRow.rename
  simp only
  induction rhs with
  | nil => rfl
  | cons x xs ih =>
    simp only [List.map_cons, List.all_cons, ih]
    cases x <;> rfl

theorem lexRows_sub (hE : envSub E E2) (hL : lexiconSub L L2) :
    ∀ r ∈ lexRows E L, r.rename (propRename E E2) ∈ lexRows E2 L2 := by
  intro r hr
  unfold lexRows at hr ⊢
  obtain ⟨h1, h2⟩ := List.mem_filter.mp hr
  exact List.mem_filter.mpr ⟨mem_dedup.mpr (lexRowsAll_sub hE hL r (mem_dedup.mp h1)),
    by rw [terminatorFree_rename]; exact h2⟩

theorem lexRows_dom (E : Env) (L : Lexicon) : ∀ r ∈ lexRows E L, r.NtsIn (InDom E) := by
  intro r hr
  unfold lexRows at hr
  exact lexRowsAll_dom E L r (mem_dedup.mp (List.mem_filter.mp hr).1)

end Sub

/-! ## The rule map -/

/-- The rule of lexical row `i`. -/
theorem lexRules_get (E : Env) (L : Lexicon) (i : Nat) :
    (lexRules E L)[i]? = ((lexRows E L)[i]?).map fun r =>
      { lhs := r.lhs, rhs := r.rhs, act := (fixedTable E.profiles).size + i, tag := r.tag } := by
  unfold lexRules
  simp

theorem lexActs_get (E : Env) (L : Lexicon) (i : Nat) :
    (lexActs E L)[i]? = ((lexRows E L)[i]?).map fun r => r.act.action (rhsTys (ty E L) r.rhs) := by
  unfold lexActs
  simp

theorem fixedActs_size (profiles : List String) : (fixedActs profiles).size = (fixedTable profiles).size := by
  unfold fixedActs
  simp

theorem fixedRules_size (profiles : List String) : (fixedRules profiles).size = (fixedTable profiles).size := by
  unfold fixedRules
  simp

/-- A fixed row names only the catalogue's nonterminals. -/
def fixedSmall (r : FixedRow) : Bool := decide (r.lhs < ntProperty) && symsSmall r.rhs

set_option maxRecDepth 20000 in
theorem fixed_rows_small : (relationalFolRows ++ orderRows ++ alternativesRows).all fixedSmall = true := by
  decide

theorem fixedTable_small (profiles : List String) {r : FixedRow} (hr : r ∈ fixedTable profiles) :
    fixedSmall r = true := by
  have hall := Array.all_eq_true_iff_forall_mem.mp fixed_rows_small
  apply hall r
  unfold fixedTable at hr
  simp only [Array.mem_append] at hr ⊢
  rcases hr with (h | h) | h
  · split at h
    · exact Or.inl (Or.inl h)
    · simp at h
  · split at h
    · exact Or.inl (Or.inr h)
    · simp at h
  · split at h
    · exact Or.inr h
    · simp at h

/-- The map of `grammar_extension`: a fixed rule to itself, a lexical rule to the rule of its renamed row. -/
def extensionMap (E : Env) (L : Lexicon) (E2 : Env) (L2 : Lexicon) : RuleMap where
  rule r :=
    if r < (fixedTable E.profiles).size then r
    else
      match (lexRows E L)[r - (fixedTable E.profiles).size]? with
      | some row => (fixedTable E.profiles).size + indexIn (row.rename (propRename E E2)) (lexRows E2 L2)
      | none => r
  nt := propRename E E2

theorem rhsTys_rename {E E2 : Env} {L L2 : Lexicon} (hE : envSub E E2) :
    ∀ (xs : List (Sym Terminal)), (∀ A, Sym.n A ∈ xs → InDom E A) →
      rhsTys (ty E2 L2) (xs.map (Sym.rename (propRename E E2))) = rhsTys (ty E L) xs
  | [], _ => rfl
  | x :: xs, h => by
    have ih := rhsTys_rename (L := L) (L2 := L2) hE xs (fun A hA => h A (List.mem_cons_of_mem _ hA))
    unfold rhsTys at ih ⊢
    simp only [List.map_cons, List.cons.injEq]
    refine ⟨?_, ih⟩
    cases x with
    | t a => rfl
    | n A =>
      simp only [Sym.rename, symTy]
      exact ty_rename hE (h A List.mem_cons_self)

theorem grammar_extension : ∀ (E : Env) (O : Overlay) (L : Lexicon) (E2 : Env) (O2 : Overlay) (L2 : Lexicon),
    Extends E O L E2 O2 L2 →
    ∃ e : RuleMap, e.Ok (grammar E L) (grammar E2 L2) (acts E L) (acts E2 L2) := by
  intro E O L E2 O2 L2 ⟨hE, hL, _, _⟩
  have hprof : E2.profiles = E.profiles := hE.1
  have hsub := lexRows_sub hE hL
  have hF : (fixedRules E.profiles).size = (fixedTable E.profiles).size := fixedRules_size _
  have hF2 : (fixedRules E2.profiles).size = (fixedTable E.profiles).size := by rw [fixedRules_size, hprof]
  have hA : (fixedActs E.profiles).size = (fixedTable E.profiles).size := fixedActs_size _
  have hA2 : (fixedActs E2.profiles).size = (fixedTable E.profiles).size := by rw [fixedActs_size, hprof]
  refine ⟨extensionMap E L E2 L2, show propRename E E2 0 = 0 from rename_small (by decide), ?_, ?_⟩
  · -- injective
    intro r r2 hr hr2 h
    simp only [grammar, Array.size_append, hF] at hr hr2
    unfold extensionMap at h
    simp only at h
    by_cases h1 : r < (fixedTable E.profiles).size <;> by_cases h2 : r2 < (fixedTable E.profiles).size
    · simpa [h1, h2] using h
    · simp only [h1, h2, if_true, if_false] at h
      split at h <;> omega
    · simp only [h1, h2, if_true, if_false] at h
      split at h <;> omega
    · simp only [h1, h2, if_false] at h
      have hl1 : r - (fixedTable E.profiles).size < (lexRows E L).length := by
        simp [lexRules] at hr; omega
      have hl2 : r2 - (fixedTable E.profiles).size < (lexRows E L).length := by
        simp [lexRules] at hr2; omega
      have g1 := List.getElem?_eq_getElem hl1
      have g2 := List.getElem?_eq_getElem hl2
      rw [g1, g2] at h
      simp only [Nat.add_left_cancel_iff] at h
      have m1 := indexIn_get (hsub _ (List.getElem_mem hl1))
      have m2 := indexIn_get (hsub _ (List.getElem_mem hl2))
      rw [h, m2] at m1
      have heq := LexRow.rename_inj hE (lexRows_dom E L _ (List.getElem_mem hl2))
        (lexRows_dom E L _ (List.getElem_mem hl1)) (Option.some.inj m1)
      have := nodup_index_inj (lexRows_nodup E L) (i := r - (fixedTable E.profiles).size)
        (j := r2 - (fixedTable E.profiles).size) (by rw [g1, g2, heq]) hl1
      omega
  · -- rules
    intro r R hR
    unfold extensionMap
    by_cases h1 : r < (fixedTable E.profiles).size
    · simp only [h1, if_true]
      have hR' : (fixedRules E.profiles)[r]? = some R := by
        simp only [grammar] at hR
        rwa [Array.getElem?_append_left (by rw [hF]; exact h1)] at hR
      have hrow : (fixedTable E.profiles)[r]'h1 ∈ fixedTable E.profiles := Array.getElem_mem h1
      have hsmall := fixedTable_small E.profiles hrow
      have hRdef : R =
          { lhs := (fixedTable E.profiles)[r].lhs, rhs := (fixedTable E.profiles)[r].rhs, act := r,
            tag := (fixedTable E.profiles)[r].tag } := by
        unfold fixedRules at hR'
        rw [Array.getElem?_mapIdx, Array.getElem?_eq_getElem h1] at hR'
        simp only [Option.map_some, Option.some.injEq] at hR'
        exact hR'.symm
      unfold fixedSmall at hsmall
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hsmall
      refine ⟨R, ?_, ?_, ?_, ?_⟩
      · simp only [grammar]
        rw [Array.getElem?_append_left (by rw [hF2]; exact h1), hprof, hR']
      · rw [hRdef, rename_small hsmall.1]
      · rw [hRdef, map_rename_small _ (symsSmall_iff.mp hsmall.2)]
      · rw [hRdef]
        show (fixedActs E2.profiles ++ lexActs E2 L2)[r]? = (fixedActs E.profiles ++ lexActs E L)[r]?
        rw [Array.getElem?_append_left (by rw [hA2]; exact h1), Array.getElem?_append_left (by rw [hA]; exact h1),
          hprof]
    · simp only [h1, if_false]
      have hR' : (lexRules E L)[r - (fixedTable E.profiles).size]? = some R := by
        simp only [grammar] at hR
        rwa [Array.getElem?_append_right (by rw [hF]; omega), hF] at hR
      rw [lexRules_get] at hR'
      cases hrow : (lexRows E L)[r - (fixedTable E.profiles).size]? with
      | none => rw [hrow] at hR'; cases hR'
      | some row =>
        rw [hrow] at hR'
        simp only [Option.map_some, Option.some.injEq] at hR'
        subst hR'
        have hmem := List.mem_of_getElem? hrow
        have hm := indexIn_get (hsub row hmem)
        have hdom := lexRows_dom E L row hmem
        refine ⟨{ lhs := propRename E E2 row.lhs, rhs := row.rhs.map (Sym.rename (propRename E E2)),
                  act := (fixedTable E.profiles).size + indexIn (row.rename (propRename E E2)) (lexRows E2 L2),
                  tag := row.tag }, ?_, rfl, rfl, ?_⟩
        · simp only [grammar]
          rw [Array.getElem?_append_right (by rw [hF2]; omega), hF2, Nat.add_sub_cancel_left, lexRules_get, hm]
          simp only [Option.map_some, hprof, LexRow.rename]
        · simp only [acts]
          rw [Array.getElem?_append_right (by rw [hA2]; omega), hA2, Nat.add_sub_cancel_left,
            Array.getElem?_append_right (by rw [hA]; omega), hA, Nat.add_sub_cancel_left,
            lexActs_get, lexActs_get, hm, hrow]
          simp only [Option.map_some, LexRow.rename]
          rw [rhsTys_rename hE row.rhs hdom.2]

end VE.EnglishGrammar
