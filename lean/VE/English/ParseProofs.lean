import VE.English.ClauseProofs

/-! # The parser finds every derivation and returns only derivations

`parseF_complete`: for a grammatical tree followed by a token that may follow a
formula, the parser returns that tree and leaves the continuation untouched.
Two trees with the same tokens are therefore equal. `parseF_sound`: whatever
the parser returns is a grammatical tree whose tokens are the consumed input.
Soundness needs no lexical condition. -/
namespace VE.English

@[simp] theorem kw_eq_kw {a b : String} : kw a = kw b ↔ a = b := by simp [kw]
@[simp] theorem kws_nil : kws [] = [] := rfl
@[simp] theorem kws_cons {x : String} {xs : List String} : kws (x :: xs) = kw x :: kws xs := rfl
@[simp] theorem kw_ne_label {a c : String} {k : Nat} : kw a ≠ Tok.label c k := by simp [kw]
@[simp] theorem length_kws {xs : List String} : (kws xs).length = xs.length := by simp [kws]

/-- The tokens that may follow a complete formula. -/
def Stop (rest : List Tok) : Prop := ∀ x rest', rest = x :: rest' → x ∈ formulaStops

theorem Stop.atom {rest : List Tok} (h : Stop rest) : AtomStop rest := by
  intro x rest' hr
  have := h x rest' hr
  simp only [formulaStops, atomStops, kws, List.map, List.mem_cons, List.not_mem_nil,
    or_false] at this ⊢
  rcases this with h | h | h <;> simp [h]

theorem stop_nil : Stop [] := by intro x rest h; cases h

theorem stop_cons {x : String} (hx : x = "," ∨ x = ";" ∨ x = ".") (rest : List Tok) :
    Stop (kw x :: rest) := by
  intro y rest' h
  cases h
  rcases hx with rfl | rfl | rfl <;> simp [formulaStops, kws, kw]

theorem atomStop_cons {x : String} (hx : x = "and" ∨ x = "or" ∨ x = ",") (rest : List Tok) :
    AtomStop (kw x :: rest) := by
  intro y rest' h
  cases h
  rcases hx with rfl | rfl | rfl <;> simp [atomStops, kws, kw]

/-! ## Declarations -/

theorem readNoun_yield {L : Lexicon} (hL : Admitted L) {s : String} (hs : s ∈ L.sorts)
    (rest : List Tok) : readNoun L (kws (L.noun s) ++ rest) = some (s, rest) := by
  unfold readNoun
  cases h : L.sorts.find? (fun s' => (kws (L.noun s')).isPrefixOf (kws (L.noun s) ++ rest)) with
  | none =>
    have := List.find?_eq_none.mp h s hs
    simp [List.isPrefixOf_iff_prefix, List.prefix_append] at this
  | some s' =>
    have hp := List.find?_some h
    have hs' := List.mem_of_find?_eq_some h
    rw [List.isPrefixOf_iff_prefix] at hp
    have hq : kws (L.noun s) <+: kws (L.noun s) ++ rest := List.prefix_append _ _
    have heq : s' = s := by
      rcases Nat.le_total (kws (L.noun s')).length (kws (L.noun s)).length with hle | hle
      · exact hL.noun_prefix_free s' hs' s hs (List.prefix_of_prefix_length_le hp hq hle)
      · exact (hL.noun_prefix_free s hs s' hs' (List.prefix_of_prefix_length_le hq hp hle)).symm
    subst heq
    simp [List.drop_left' (length_kws (xs := L.noun s'))]

theorem readNoun_sound {L : Lexicon} {input rest : List Tok} {s : String}
    (h : readNoun L input = some (s, rest)) : s ∈ L.sorts ∧ input = kws (L.noun s) ++ rest := by
  simp only [readNoun, Option.map_eq_some_iff, Prod.mk.injEq] at h
  obtain ⟨s', hf, rfl, rfl⟩ := h
  have hp := List.find?_some hf
  rw [List.isPrefixOf_iff_prefix, List.prefix_iff_eq_append] at hp
  refine ⟨List.mem_of_find?_eq_some hf, ?_⟩
  rw [length_kws] at hp
  exact hp.symm

theorem takeLabel_none {L : Lexicon} {s : String} {rest : List Tok}
    (h : rest.head? ≠ some (kw "named")) : takeLabel L s rest = none := by
  unfold takeLabel
  split
  · rename_i y c k rest'
    have : y ≠ kw "named" := by simpa using h
    simp [this]
  · rfl

theorem takeLabel_sound {L : Lexicon} {s : String} {input rest : List Tok} {k : Nat}
    (h : takeLabel L s input = some (k, rest)) : input = [kw "named", .label (L.letter s) k] ++ rest := by
  unfold takeLabel at h
  split at h
  · rename_i y c k' rest'
    split at h
    · rename_i hc
      obtain ⟨rfl, rfl⟩ := hc
      simp only [Option.some.injEq, Prod.mk.injEq] at h
      obtain ⟨rfl, rfl⟩ := h
      rfl
    · simp at h
  · simp at h

theorem parseDecl_yield {L : Lexicon} (hL : Admitted L) (r : Ref) (hr : r.sort ∈ L.sorts)
    (rest : List Tok) (hn : rest.head? ≠ some (kw "named")) :
    parseDecl L (r.declYield L ++ rest) = some (r, rest) := by
  obtain ⟨x, xs, hx, hf, hs⟩ := hL.noun_opens r.sort hr
  cases r with
  | plain s =>
    have h := readNoun_yield hL hr rest
    simp only [Ref.sort] at hx h
    simp only [Ref.declYield]
    rw [hx] at h ⊢
    simp only [kws_cons, List.cons_append] at h ⊢
    simp [parseDecl, hf, hs, h, takeLabel_none hn]
  | first s =>
    have h := readNoun_yield hL hr rest
    simp only [Ref.sort] at h
    simp [Ref.declYield, parseDecl, h]
  | second s =>
    have h := readNoun_yield hL hr rest
    simp only [Ref.sort] at h
    simp [Ref.declYield, parseDecl, h]
  | named s k =>
    have h := readNoun_yield hL hr (kw "named" :: .label (L.letter s) k :: rest)
    simp only [Ref.sort] at hx h
    simp only [Ref.declYield, List.append_assoc, List.cons_append, List.nil_append]
    rw [hx] at h ⊢
    simp only [kws_cons, List.cons_append] at h ⊢
    simp [parseDecl, hf, hs, h, takeLabel]

theorem parseDecl_sound {L : Lexicon} {input rest : List Tok} {r : Ref}
    (h : parseDecl L input = some (r, rest)) : r.sort ∈ L.sorts ∧ input = r.declYield L ++ rest := by
  match input, h with
  | x :: input, h =>
    simp only [parseDecl] at h
    split at h
    · subst x
      simp only [Option.map_eq_some_iff, Prod.mk.injEq] at h
      obtain ⟨⟨s, rest'⟩, hs, rfl, rfl⟩ := h
      obtain ⟨hm, rfl⟩ := readNoun_sound hs
      exact ⟨hm, rfl⟩
    · split at h
      · subst x
        simp only [Option.map_eq_some_iff, Prod.mk.injEq] at h
        obtain ⟨⟨s, rest'⟩, hs, rfl, rfl⟩ := h
        obtain ⟨hm, rfl⟩ := readNoun_sound hs
        exact ⟨hm, rfl⟩
      · split at h
        · simp at h
        · rename_i s rest' hs
          obtain ⟨hm, he⟩ := readNoun_sound hs
          split at h
          · rename_i k rest'' hk
            simp only [Option.some.injEq, Prod.mk.injEq] at h
            obtain ⟨rfl, rfl⟩ := h
            rw [takeLabel_sound hk] at he
            exact ⟨hm, by simp [he, Ref.declYield]⟩
          · simp only [Option.some.injEq, Prod.mk.injEq] at h
            obtain ⟨rfl, rfl⟩ := h
            exact ⟨hm, by simp [he, Ref.declYield]⟩

/-! ## Formulas -/

theorem not_opener {x : Tok} (h : x ∉ openers) :
    x ≠ kw "it" ∧ x ≠ kw "both" ∧ x ≠ kw "either" ∧ x ≠ kw "if" ∧ x ≠ kw "all" ∧
    x ≠ kw "at" ∧ x ≠ kw "for" ∧ x ≠ kw "there" ∧ x ≠ kw "of" := by
  simpa [openers, kws, kw] using h

theorem parseF_lit {L : Lexicon} {fuel d : Nat} {x : Tok} {rest : List Tok} (hx : x ∉ openers) :
    parseF L (fuel + 1) d (x :: rest) =
      (parseLitPrefix L (x :: rest)).bind fun p => some (.lit p.1, p.2) := by
  obtain ⟨h1, h2, h3, h4, h5, h6, h7, h8, -⟩ := not_opener hx
  simp only [parseF, h1, h2, h3, h4, h5, h6, h7, h8, if_false]
  rfl

theorem consume_header_none {L : Lexicon} (hL : Admitted L) {a : Lit} (hok : a.ok L = true)
    (rest : List Tok) : consume (kws ["of", "the", "following", "hold", ":"]) (a.yield L ++ rest) = none := by
  obtain ⟨x, ys, hy, hx⟩ := hL.atom_opens a hok
  have hof := (not_opener hx).2.2.2.2.2.2.2.2
  rw [hy]
  simp [consume, Ne.symm hof]

theorem size_pos (t : Tree) : 0 < t.size := by
  cases t <;> simp [Tree.size]

theorem parseF_complete {L : Lexicon} (hL : Admitted L) :
    ∀ (t : Tree) (d fuel : Nat) (rest : List Tok), t.Syntactic L → t.size < fuel → Stop rest →
      parseF L fuel d (t.yield L d ++ rest) = some (t, rest) := by
  intro t
  induction t with
  | lit a =>
    intro d fuel rest hs hf hr
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by simp [Tree.size] at hf; omega⟩
    obtain ⟨x, ys, hy, hx⟩ := hL.atom_opens a hs
    simp only [Tree.yield]
    rw [hy, List.cons_append, parseF_lit hx, ← List.cons_append, ← hy,
      parseLitPrefix_yield hL hs hr.atom]
    rfl
  | neg b ih =>
    intro d fuel rest hs hf hr
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by simp [Tree.size] at hf; omega⟩
    simp only [Tree.size] at hf
    simp only [Tree.yield, kws_cons, kws_nil, List.cons_append, List.nil_append]
    simp [parseF, consume, ih d f rest hs (by omega) hr]
  | both a b =>
    intro d fuel rest hs hf hr
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by simp [Tree.size] at hf; omega⟩
    obtain ⟨ha, hb⟩ := hs
    simp only [Tree.yield, List.cons_append, List.append_assoc]
    simp only [parseF, kw_eq_kw, if_true]
    simp (config := { decide := true }) only [if_false]
    rw [consume_header_none hL ha]
    simp only [parseLitPrefix_yield hL ha (atomStop_cons (Or.inl rfl) _), Option.bind_eq_bind,
      Option.bind_some, consume, if_true, parseLitPrefix_yield hL hb hr.atom]
  | either a b =>
    intro d fuel rest hs hf hr
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by simp [Tree.size] at hf; omega⟩
    obtain ⟨ha, hb⟩ := hs
    simp only [Tree.yield, List.cons_append, List.append_assoc, kws_cons, kws_nil]
    simp (config := { decide := true }) only [parseF, if_true, if_false]
    simp only [parseLitPrefix_yield hL ha (atomStop_cons (Or.inr (Or.inl rfl)) _), Option.bind_eq_bind,
      Option.bind_some, consume, if_true,
      parseLitPrefix_yield hL hb (atomStop_cons (Or.inr (Or.inr rfl)) _)]
    simp [consume]
  | cond a b iha ihb =>
    intro d fuel rest hs hf hr
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by simp [Tree.size] at hf; omega⟩
    obtain ⟨ha, hb⟩ := hs
    simp only [Tree.size] at hf
    simp only [Tree.yield, List.cons_append, List.append_assoc]
    simp (config := { decide := true }) only [parseF, if_true, if_false]
    rw [iha d f _ ha (by omega) (stop_cons (Or.inl rfl) _)]
    simp [consume, ihb d f rest hb (by omega) hr]
  | list h a b iha ihb =>
    intro d fuel rest hs hf hr
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by simp [Tree.size] at hf; omega⟩
    obtain ⟨ha, hb⟩ := hs
    simp only [Tree.size] at hf
    have tail : listTail (parseF L f) d h ((markers d).1 ::
        (a.yield L (d + 1) ++ kw ";" :: (markers d).2 :: b.yield L (d + 1)) ++ rest) =
        some (.list h a b, rest) := by
      simp only [listTail, List.cons_append, List.append_assoc, consume, if_true,
        Option.bind_eq_bind, Option.bind_some]
      rw [iha (d + 1) f _ ha (by omega) (stop_cons (Or.inr (Or.inl rfl)) _)]
      simp [consume, ihb (d + 1) f rest hb (by omega) hr]
    cases h with
    | both =>
      simp only [Tree.yield, Header.yield, kws_cons, kws_nil, List.cons_append, List.nil_append,
        List.append_assoc] at tail ⊢
      simp (config := { decide := true }) only [parseF, if_true, if_false, consume]
      exact tail
    | all =>
      simp only [Tree.yield, Header.yield, kws_cons, kws_nil, List.cons_append, List.nil_append,
        List.append_assoc] at tail ⊢
      simp (config := { decide := true }) only [parseF, if_true, if_false, consume,
        Option.bind_eq_bind]
      exact tail
    | atLeastOne =>
      simp only [Tree.yield, Header.yield, kws_cons, kws_nil, List.cons_append, List.nil_append,
        List.append_assoc] at tail ⊢
      simp (config := { decide := true }) only [parseF, if_true, if_false, consume,
        Option.bind_eq_bind]
      exact tail
  | all r b ih =>
    intro d fuel rest hs hf hr
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by simp [Tree.size] at hf; omega⟩
    obtain ⟨hsort, hb⟩ := hs
    simp only [Tree.size] at hf
    simp only [Tree.yield, List.cons_append, List.append_assoc]
    simp (config := { decide := true }) only [parseF, if_true, if_false, consume,
      Option.bind_eq_bind, Option.bind_some]
    rw [parseDecl_yield hL r hsort _ (by simp)]
    simp [consume, ih d f rest hb (by omega) hr]
  | ex an r b ih =>
    intro d fuel rest hs hf hr
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by simp [Tree.size] at hf; omega⟩
    obtain ⟨hsort, hb⟩ := hs
    simp only [Tree.size] at hf
    simp only [Tree.yield, List.cons_append, List.append_assoc]
    have hart : (kw (if an = true then "an" else "a") = kw "a" ∨
        kw (if an = true then "an" else "a") = kw "an") := by cases an <;> simp
    have han : (kw (if an = true then "an" else "a") == kw "an") = an := by cases an <;> decide
    simp (config := { decide := true }) only [parseF, kw_eq_kw, if_true, if_false, true_and]
    rw [parseDecl_yield hL r hsort _ (by simp)]
    simp [consume, ih d f rest hb (by omega) hr, han]

end VE.English

/-! ## Soundness: the parser returns only derivations of the consumed tokens -/

namespace VE.English

theorem listTail_sound {L : Lexicon} {p : Nat → List Tok → Option (Tree × List Tok)} {d : Nat}
    {h : Header} {input rest : List Tok} {t : Tree}
    (hp : ∀ d input t rest, p d input = some (t, rest) → t.Syntactic L ∧ input = t.yield L d ++ rest)
    (hl : listTail p d h input = some (t, rest)) :
    ∃ a b, t = .list h a b ∧ a.Syntactic L ∧ b.Syntactic L ∧
      input = (markers d).1 :: (a.yield L (d + 1) ++ kw ";" :: (markers d).2 :: b.yield L (d + 1)) ++ rest := by
  simp only [listTail, Option.bind_eq_bind, Option.bind_eq_some_iff] at hl
  obtain ⟨r1, h1, ⟨a, r2⟩, h2, r3, h3, ⟨b, r4⟩, h4, hl⟩ := hl
  simp only [Option.some.injEq, Prod.mk.injEq] at hl
  obtain ⟨rfl, rfl⟩ := hl
  dsimp only at h3
  obtain ⟨ha, rfl⟩ := hp _ _ _ _ h2
  obtain ⟨hb, rfl⟩ := hp _ _ _ _ h4
  obtain rfl := consume_sound h3
  obtain rfl := consume_sound h1
  exact ⟨a, b, rfl, ha, hb, by simp⟩

theorem parseF_sound {L : Lexicon} : ∀ (fuel d : Nat) (input rest : List Tok) (t : Tree),
    parseF L fuel d input = some (t, rest) → t.Syntactic L ∧ input = t.yield L d ++ rest := by
  intro fuel
  induction fuel with
  | zero => intro d input rest t h; simp [parseF] at h
  | succ f ih =>
    intro d input rest t h
    match input, h with
    | x :: input, h =>
      simp only [parseF] at h
      split at h
      · subst x
        simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
        obtain ⟨r1, h1, ⟨b, r2⟩, h2, h⟩ := h
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        try dsimp only at *
        obtain ⟨hb, rfl⟩ := ih _ _ _ _ h2
        obtain rfl := consume_sound h1
        exact ⟨hb, by simp [Tree.yield]⟩
      split at h
      · subst x
        split at h
        · rename_i r1 h1
          obtain ⟨a, b, rfl, ha, hb, rfl⟩ := listTail_sound (fun d i t r h => ih d i r t h) h
          obtain rfl := consume_sound h1
          exact ⟨⟨ha, hb⟩, by simp [Tree.yield, Header.yield]⟩
        · simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
          obtain ⟨⟨a, r1⟩, h1, r2, h2, ⟨b, r3⟩, h3, h⟩ := h
          simp only [Option.some.injEq, Prod.mk.injEq] at h
          obtain ⟨rfl, rfl⟩ := h
          try dsimp only at *
          obtain ⟨ha, rfl⟩ := parseLitPrefix_sound h1
          obtain rfl := consume_sound h2
          obtain ⟨hb, rfl⟩ := parseLitPrefix_sound h3
          exact ⟨⟨ha, hb⟩, by simp [Tree.yield]⟩
      split at h
      · subst x
        simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
        obtain ⟨⟨a, r1⟩, h1, r2, h2, ⟨b, r3⟩, h3, r4, h4, h⟩ := h
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        try dsimp only at *
        obtain ⟨ha, rfl⟩ := parseLitPrefix_sound h1
        obtain rfl := consume_sound h2
        obtain ⟨hb, rfl⟩ := parseLitPrefix_sound h3
        obtain rfl := consume_sound h4
        exact ⟨⟨ha, hb⟩, by simp [Tree.yield]⟩
      split at h
      · subst x
        simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
        obtain ⟨⟨a, r1⟩, h1, r2, h2, ⟨b, r3⟩, h3, h⟩ := h
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        try dsimp only at *
        obtain ⟨ha, rfl⟩ := ih _ _ _ _ h1
        obtain rfl := consume_sound h2
        obtain ⟨hb, rfl⟩ := ih _ _ _ _ h3
        exact ⟨⟨ha, hb⟩, by simp [Tree.yield]⟩
      split at h
      · subst x
        simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
        obtain ⟨r1, h1, h⟩ := h
        obtain ⟨a, b, rfl, ha, hb, rfl⟩ := listTail_sound (fun d i t r h => ih d i r t h) h
        obtain rfl := consume_sound h1
        exact ⟨⟨ha, hb⟩, by simp [Tree.yield, Header.yield]⟩
      split at h
      · subst x
        simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
        obtain ⟨r1, h1, h⟩ := h
        obtain ⟨a, b, rfl, ha, hb, rfl⟩ := listTail_sound (fun d i t r h => ih d i r t h) h
        obtain rfl := consume_sound h1
        exact ⟨⟨ha, hb⟩, by simp [Tree.yield, Header.yield]⟩
      split at h
      · subst x
        simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
        obtain ⟨r1, h1, ⟨r, r2⟩, h2, r3, h3, ⟨b, r4⟩, h4, h⟩ := h
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        try dsimp only at *
        obtain ⟨hr, rfl⟩ := parseDecl_sound h2
        obtain ⟨hb, rfl⟩ := ih _ _ _ _ h4
        obtain rfl := consume_sound h3
        obtain rfl := consume_sound h1
        exact ⟨⟨hr, hb⟩, by simp [Tree.yield]⟩
      split at h
      · subst x
        split at h
        · rename_i y z input
          split at h
          · rename_i hyz
            obtain ⟨rfl, hz⟩ := hyz
            simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
            obtain ⟨⟨r, r2⟩, h2, r3, h3, ⟨b, r4⟩, h4, h⟩ := h
            simp only [Option.some.injEq, Prod.mk.injEq] at h
            obtain ⟨rfl, rfl⟩ := h
            try dsimp only at *
            obtain ⟨hr, rfl⟩ := parseDecl_sound h2
            obtain ⟨hb, rfl⟩ := ih _ _ _ _ h4
            obtain rfl := consume_sound h3
            refine ⟨⟨hr, hb⟩, ?_⟩
            rcases hz with rfl | rfl <;> simp [Tree.yield]
          · simp at h
        · simp at h
      · simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
        obtain ⟨⟨a, r1⟩, h1, h⟩ := h
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        try dsimp only at *
        obtain ⟨ha, he⟩ := parseLitPrefix_sound h1
        exact ⟨ha, he⟩

end VE.English
