import VE.English.Parse

/-! # Clause-level parser lemmas

Every lexically valid simple clause is among the parser's candidates for its
own tokens, so under `Admitted` the clause parser returns exactly that clause;
conversely whatever it returns is a lexically valid clause with those tokens. -/
namespace VE.English

theorem consume_append : ∀ (xs rest : List Tok), consume xs (xs ++ rest) = some rest
  | [], _ => rfl
  | x :: xs, rest => by simp [consume, consume_append xs rest]

theorem consume_sound : ∀ {xs input rest : List Tok}, consume xs input = some rest → input = xs ++ rest
  | [], _, _, h => by simp [consume] at h; simp [h]
  | _ :: _, [], _, h => by simp [consume] at h
  | x :: xs, y :: ys, rest, h => by
    simp only [consume] at h
    split at h
    · subst x; simp [consume_sound h]
    · simp at h

theorem infixB_of_infix {a b : List Tok} (h : a <:+: b) : infixB a b = true := by
  obtain ⟨s, t, rfl⟩ := h
  simp only [infixB, List.any_eq_true, List.mem_range]
  refine ⟨s.length, by simp; omega, ?_⟩
  rw [List.append_assoc, List.drop_left' rfl, List.isPrefixOf_iff_prefix]
  exact List.prefix_append _ _

theorem infix_flatMap {α β : Type} (f : α → List β) :
    ∀ {x : α} {T : List α}, x ∈ T → f x <:+: T.flatMap f
  | _, [], h => by simp at h
  | x, y :: T, h => by
    simp only [List.flatMap_cons]
    rcases List.mem_cons.mp h with rfl | h
    · exact (List.prefix_append _ _).isInfix
    · exact (infix_flatMap f h).trans (List.suffix_append _ _).isInfix

theorem mem_labelsIn : ∀ {run : List Tok} {c : String} {k : Nat}, Tok.label c k ∈ run → (c, k) ∈ labelsIn run
  | [], _, _, h => by simp at h
  | .label c' k' :: run, c, k, h => by
    rcases List.mem_cons.mp h with h | h
    · cases h; simp [labelsIn]
    · simp [labelsIn, mem_labelsIn h]
  | .word _ :: run, c, k, h => by
    rcases List.mem_cons.mp h with h | h
    · cases h
    · simp [labelsIn, mem_labelsIn h]

theorem mem_tuples {α : Type} {pool : List α} : ∀ {n : Nat} {xs : List α},
    xs.length = n → (∀ x ∈ xs, x ∈ pool) → xs ∈ tuples pool n
  | 0, [], _, _ => by simp [tuples]
  | n + 1, x :: xs, hn, hmem => by
    simp only [tuples, List.mem_flatMap, List.mem_map]
    exact ⟨x, hmem x (by simp), xs, mem_tuples (by simpa using hn) (fun y hy => hmem y (by simp [hy])), rfl⟩
  | 0, _ :: _, hn, _ => by simp at hn
  | _ + 1, [], hn, _ => by simp at hn

/-- A valid term whose tokens occur in `run` is in the pool for `run`. -/
theorem mem_termPool {L : Lexicon} {run : List Tok} {t : TermTree}
    (hok : t.ok L = true) (hin : t.yield L <:+: run) : t ∈ termPool L run := by
  simp only [termPool, List.mem_filter, infixB_of_infix hin, and_true]
  cases t with
  | const c =>
    simp only [TermTree.ok, List.contains_iff_mem] at hok
    simp [hok]
  | ref r =>
    simp only [TermTree.ok, List.contains_iff_mem] at hok
    refine List.mem_append_right _ (List.mem_flatMap.mpr ⟨r.sort, hok, ?_⟩)
    cases r with
    | plain s => simp [Ref.sort]
    | first s => simp [Ref.sort]
    | second s => simp [Ref.sort]
    | named s k =>
      have hl : Tok.label (L.letter s) k ∈ run :=
        hin.mem (by simp [TermTree.yield, Ref.refYield])
      simp only [Ref.sort, List.mem_append, List.mem_cons, List.not_mem_nil, or_false,
        namedRefs, List.mem_filterMap]
      exact Or.inr ⟨(L.letter s, k), mem_labelsIn hl, by simp⟩

theorem arg_infix {L : Lexicon} {T : Template} {args : List TermTree} {i : Nat}
    (hi : i < args.length) (hT : Slot.hole i ∈ T) :
    (args[i]).yield L <:+: fill T (args.map (TermTree.yield L)) := by
  have h := infix_flatMap (fun
    | Slot.word w => [Tok.word w]
    | Slot.hole i => (args.map (TermTree.yield L)).getD i []) hT
  simpa [fill, List.getD_eq_getElem?_getD, hi] using h

/-- Every valid clause is a candidate for its own tokens. -/
theorem mem_litCandidates {L : Lexicon} (a : Lit) (hok : a.ok L = true) :
    a ∈ litCandidates L (a.yield L) := by
  cases a with
  | truth => simp [litCandidates]
  | falsity => simp [litCandidates]
  | eq x y =>
    simp only [Lit.ok, Bool.and_eq_true] at hok
    have hx := mem_termPool (run := Lit.yield L (.eq x y)) hok.1
      (by simp only [Lit.yield, List.append_assoc]; exact (List.prefix_append _ _).isInfix)
    have hy := mem_termPool (run := Lit.yield L (.eq x y)) hok.2
      (by simp only [Lit.yield]; exact (List.suffix_append _ _).isInfix)
    simp only [litCandidates, List.mem_append, List.mem_flatMap, List.mem_map]
    exact Or.inl (Or.inr ⟨x, hx, y, hy, rfl⟩)
  | pred p args =>
    simp only [Lit.ok, Bool.and_eq_true, List.contains_iff_mem, List.all_eq_true] at hok
    obtain ⟨⟨hp, hargs⟩, hT⟩ := hok
    cases hTp : L.template p with
    | none => simp [hTp] at hT
    | some T =>
      simp only [hTp, Bool.and_eq_true, beq_iff_eq, List.all_eq_true, List.mem_range,
        List.contains_iff_mem] at hT
      obtain ⟨hlen, hholes⟩ := hT
      simp only [litCandidates, List.mem_append, List.mem_flatMap]
      refine Or.inr ⟨p, hp, ?_⟩
      simp only [hTp, List.mem_map]
      refine ⟨args, mem_tuples hlen ?_, rfl⟩
      intro t ht
      obtain ⟨i, hi, rfl⟩ := List.mem_iff_getElem.mp ht
      refine mem_termPool (hargs _ ht) ?_
      simpa [Lit.yield, hTp] using arg_infix (L := L) hi (hholes i hi)

theorem parseLit_yield {L : Lexicon} (hL : Admitted L) {a : Lit} (hok : a.ok L = true) :
    parseLit L (a.yield L) = some a := by
  unfold parseLit
  cases h : (litCandidates L (a.yield L)).find? (fun b => b.ok L && b.yield L == a.yield L) with
  | none =>
    have := List.find?_eq_none.mp h a (mem_litCandidates a hok)
    simp [hok] at this
  | some b =>
    have hb := List.find?_some h
    simp only [Bool.and_eq_true, beq_iff_eq] at hb
    rw [hL.atom_unique b a hb.1 hok hb.2]

theorem parseLit_sound {L : Lexicon} {run : List Tok} {a : Lit} (h : parseLit L run = some a) :
    a.ok L = true ∧ a.yield L = run := by
  have hb := List.find?_some h
  simpa only [Bool.and_eq_true, beq_iff_eq] using hb

/-- The tokens that may follow a simple clause. -/
def AtomStop (rest : List Tok) : Prop := ∀ x rest', rest = x :: rest' → x ∈ atomStops

theorem takeWhile_nonstop {a rest : List Tok} (ha : ∀ x ∈ a, x ∉ atomStops) (hr : AtomStop rest) :
    (a ++ rest).takeWhile (fun x => !isAtomStop x) = a ∧
    (a ++ rest).dropWhile (fun x => !isAtomStop x) = rest := by
  induction a with
  | nil =>
    cases rest with
    | nil => simp
    | cons x rest' =>
      have hx := hr x rest' rfl
      have : isAtomStop x = true := by simpa [isAtomStop] using hx
      simp [this]
  | cons x a ih =>
    have hx : isAtomStop x = false := by
      simpa [isAtomStop] using ha x (by simp)
    have ih := ih (fun y hy => ha y (by simp [hy]))
    simp [hx, ih.1, ih.2]

theorem parseLitPrefix_yield {L : Lexicon} (hL : Admitted L) {a : Lit} {rest : List Tok}
    (hok : a.ok L = true) (hr : AtomStop rest) :
    parseLitPrefix L (a.yield L ++ rest) = some (a, rest) := by
  have hs := takeWhile_nonstop (hL.atom_delimited a hok) hr
  simp [parseLitPrefix, hs.1, hs.2, parseLit_yield hL hok]

theorem parseLitPrefix_sound {L : Lexicon} {input rest : List Tok} {a : Lit}
    (h : parseLitPrefix L input = some (a, rest)) : a.ok L = true ∧ input = a.yield L ++ rest := by
  simp only [parseLitPrefix, Option.map_eq_some_iff, Prod.mk.injEq] at h
  obtain ⟨b, hb, rfl, rfl⟩ := h
  obtain ⟨hok, hy⟩ := parseLit_sound hb
  exact ⟨hok, by rw [hy, List.takeWhile_append_dropWhile]⟩

end VE.English
