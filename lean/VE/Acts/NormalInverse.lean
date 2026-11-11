import VE.Acts.NormalProofs

/-! Reading a derivation of the act grammar backwards, for the uniqueness half of `read_normal`
(docs/spec/act-phrases.md 5.6; `VE.Acts.NormalUnique`).

Proofs only. Every derivation of `a.normal` from the start symbol has the pieces `[.act (.one a.canon)]`, for a
`normalOk` atom `a` under a `framesOk` vocabulary (`normal_pieces`); so every derivation that has a meaning means
`.one a.canon` (`normal_unique`). With `normal_derived` and `parse_bounds` (`VE.Acts.NormalProofs`) that is
`read_normal`. The argument reads the rule table backwards (`gen_inv`, `rules_of`): the head fixes the frame, a
marker's words fix the marker (no marker begins another), a filler run stops only where the next token is not a
filler word, and a join word or comma of a normal form is always followed by a part's first token, which no
coordination, split construct or joined modifier can start with.
-/

namespace VE.Acts.NormalProofs

set_option linter.unusedSimpArgs false
open VE.Acts
open VE.Grammar (Tree Sym derivesAll yieldAll)
open VE.Acts.Lexical (Tok)

/-! ### Reading a derivation backwards -/

variable {V : Vocab}

theorem getElem?_idxOf {α : Type} [DecidableEq α] : ∀ {l : List α} {x : α}, x ∈ l → l[l.idxOf x]? = some x
  | [], _, h => by cases h
  | y :: ys, x, h => by
    rw [List.idxOf_cons]
    by_cases hy : y = x
    · subst hy; simp
    · have hx : x ∈ ys := by rcases List.mem_cons.mp h with h | h; exact absurd h.symm hy; exact h
      have hb : (y == x) = false := by simpa using hy
      simp [hb, getElem?_idxOf hx]

theorem nm_inj {x y : NT} (hx : x ∈ (closed (schema V)).map (·.lhs)) (he : nm V x = nm V y) : x = y := by
  unfold nm at he
  have hx' := mem_firsts.mpr hx
  by_cases hy : y ∈ firsts ((closed (schema V)).map (·.lhs))
  · have h1 := getElem?_idxOf hx'
    have h2 := getElem?_idxOf hy
    rw [he] at h1; rw [h1] at h2; exact Option.some.inj h2
  · have := List.idxOf_lt_length_of_mem hx'
    rw [he, List.idxOf_eq_length hy] at this; omega

theorem genAll_inv_nil {w : List Tok} {ps : List Piece} (h : GenAll V [] w ps) : w = [] ∧ ps = [] := by
  obtain ⟨ts, hts, hy, hp⟩ := h
  cases ts with
  | nil => simp_all [VE.Grammar.yieldAll_nil]
  | cons t ts => simp [VE.Grammar.derivesAll_nil_cons] at hts

theorem genAll_inv_cons {Y : RSym} {Ys : List RSym} {w : List Tok} {ps : List Piece} (h : GenAll V (Y :: Ys) w ps) :
    ∃ w1 w2 p1 p2, w = w1 ++ w2 ∧ ps = p1 ++ p2 ∧ Gen V Y w1 p1 ∧ GenAll V Ys w2 p2 := by
  obtain ⟨ts, hts, hy, hp⟩ := h
  cases ts with
  | nil => simp [VE.Grammar.derivesAll_cons_nil] at hts
  | cons t ts =>
    simp only [List.map_cons, VE.Grammar.derivesAll_cons, Bool.and_eq_true] at hts
    simp only [List.mapM_cons] at hp
    cases h1 : piecesOf (closed (schema V)).toArray t with
    | none => simp [h1] at hp
    | some p1 =>
      cases h2 : ts.mapM (piecesOf (closed (schema V)).toArray) with
      | none => simp [h1, h2] at hp
      | some l =>
        simp [h1, h2] at hp
        refine ⟨t.yield, yieldAll ts, p1, l.flatten, ?_, hp.symm, ⟨t, hts.1, rfl, h1⟩, ⟨ts, hts.2, rfl, by simp [h2]⟩⟩
        rw [← hy, VE.Grammar.yieldAll_cons]

theorem gen_t_inv {a : Term} {w : List Tok} {ps : List Piece} (h : Gen V (.t a) w ps) :
    ∃ x, w = [x] ∧ a.accepts x = true ∧ piecesOf (closed (schema V)).toArray (.leaf x) = some ps := by
  obtain ⟨t, ht, hy, hp⟩ := h
  cases t with
  | leaf x => exact ⟨x, by rw [← hy, VE.Grammar.yield_leaf], by simpa [symB, VE.Grammar.derives_leaf] using ht, hp⟩
  | node i kids => simp [symB, VE.Grammar.derives_node_t] at ht

theorem genAll_never {w : List Tok} {ps : List Piece} : ¬ GenAll V [.t .never] w ps := by
  intro h
  obtain ⟨w1, w2, p1, p2, -, -, h1, -⟩ := genAll_inv_cons h
  obtain ⟨x, -, hx, -⟩ := gen_t_inv h1
  cases x <;> simp [Term.accepts] at hx

/-- A derivation of a nonterminal is a rule of the table with that left side over derivations of its right side. -/
theorem gen_inv {X : NT} {w : List Tok} {ps : List Piece} (hg : Gen V (.n X) w ps) :
    ∃ r ∈ schema V, r.lhs = X ∧ ∃ cs, GenAll V r.rhs w cs ∧ applyRule r cs = some ps := by
  obtain ⟨t, ht, hy, hp⟩ := hg
  cases t with
  | leaf x => simp [symB, VE.Grammar.derives_leaf_n] at ht
  | node i kids =>
    simp only [symB] at ht
    rw [VE.Grammar.derives_node] at ht
    cases hr : (closed (schema V))[i]? with
    | none =>
      have : (grammar V).rules[i]? = none := by simp [grammar, build, List.getElem?_toArray, hr]
      rw [this] at ht; simp at ht
    | some r =>
      rw [grammar_rule hr] at ht
      simp only [Bool.and_eq_true, beq_iff_eq] at ht
      have hmem := List.mem_of_getElem? hr
      have hl : r.lhs = X := nm_inj (List.mem_map_of_mem hmem) ht.1
      rw [piecesOf_node] at hp
      simp only [List.getElem?_toArray, hr, Option.bind_some] at hp
      cases hm : kids.mapM (piecesOf (closed (schema V)).toArray) with
      | none => simp [hm] at hp
      | some l =>
        simp only [hm, Option.bind_some] at hp
        have hg : GenAll V r.rhs w l.flatten := ⟨kids, ht.2, by rw [← hy, VE.Grammar.yield_node], by simp [hm]⟩
        refine ⟨r, ?_, hl, l.flatten, hg, hp⟩
        simp only [closed, List.mem_append, List.mem_map] at hmem
        rcases hmem with hmem | ⟨x, _, rfl⟩
        · exact hmem
        · exact (genAll_never hg).elim


theorem mem_ite_iff {α : Type} {a : α} {c : Prop} [Decidable c] {l1 l2 : List α} :
    (a ∈ if c then l1 else l2) ↔ (c ∧ a ∈ l1) ∨ (¬c ∧ a ∈ l2) := by
  by_cases hc : c <;> simp [hc]
theorem eq_ite_iff {α : Type} {a x y : α} {c : Prop} [Decidable c] :
    (a = if c then x else y) ↔ (c ∧ a = x) ∨ (¬c ∧ a = y) := by
  by_cases hc : c <;> simp [hc]

/-- A goal kept whole while `rules_of` splits a rule's cases. -/
def Box (p : Prop) : Prop := p
theorem box_intro {p : Prop} (h : Box p) : p := h

/-- The rules of the table whose left side is the one in `hr : ⟨X, rhs, k⟩ ∈ schema V`, one goal per rule, with
`rhs` and `k` substituted; a frame's rule names the frame `fr` and its number's membership `hfr`. -/
macro "rules_of" hr:ident fr:ident hfr:ident : tactic => `(tactic| (
  apply box_intro
  simp only [schema, List.mem_append, List.mem_flatMap] at $hr:ident
  rcases $hr:ident with $hr:ident | ⟨⟨$fr:ident, _⟩, $hfr:ident, $hr:ident⟩ <;>
  first
  | (have _ := $hfr:ident; simp [frameRules, many1, tail, mem_ite_iff, eq_ite_iff] at $hr:ident <;>
      revert $hr:ident <;> simp only [or_imp, and_imp, forall_and, imp_self, forall_exists_index] <;> and_intros <;>
      intros <;> subst_vars)
  | (simp [globalRules, items, many1, tail] at $hr:ident <;>
      revert $hr:ident <;> simp only [or_imp, and_imp, forall_and, imp_self, forall_exists_index] <;> and_intros <;>
      intros <;> subst_vars)) <;> simp only [Box])

/-- `gen_inv` with the rule written out. -/
theorem gen_rule {X : NT} {w : List Tok} {ps : List Piece} (hg : Gen V (.n X) w ps) :
    ∃ rhs k cs, (⟨X, rhs, k⟩ : RuleS) ∈ schema V ∧ GenAll V rhs w cs ∧ applyRule ⟨X, rhs, k⟩ cs = some ps := by
  obtain ⟨⟨X', rhs, k⟩, hr, rfl, cs, hg, ha⟩ := gen_inv hg
  exact ⟨rhs, k, cs, hr, hg, ha⟩

theorem genAll1 {Y : RSym} {w : List Tok} {cs : List Piece} (h : GenAll V [Y] w cs) : Gen V Y w cs := by
  obtain ⟨w1, w2, p1, p2, rfl, rfl, h1, h2⟩ := genAll_inv_cons h
  obtain ⟨rfl, rfl⟩ := genAll_inv_nil h2
  simpa using h1

theorem genAll2 {Y1 Y2 : RSym} {w : List Tok} {cs : List Piece} (h : GenAll V [Y1, Y2] w cs) :
    ∃ w1 w2 c1 c2, w = w1 ++ w2 ∧ cs = c1 ++ c2 ∧ Gen V Y1 w1 c1 ∧ Gen V Y2 w2 c2 := by
  obtain ⟨w1, w2, p1, p2, rfl, rfl, h1, h2⟩ := genAll_inv_cons h
  exact ⟨w1, w2, p1, p2, rfl, rfl, h1, genAll1 h2⟩

theorem genAll3 {Y1 Y2 Y3 : RSym} {w : List Tok} {cs : List Piece} (h : GenAll V [Y1, Y2, Y3] w cs) :
    ∃ w1 w2 w3 c1 c2 c3, w = w1 ++ w2 ++ w3 ∧ cs = c1 ++ c2 ++ c3 ∧ Gen V Y1 w1 c1 ∧ Gen V Y2 w2 c2 ∧
      Gen V Y3 w3 c3 := by
  obtain ⟨w1, w2, p1, p2, rfl, rfl, h1, h2⟩ := genAll_inv_cons h
  obtain ⟨w2, w3, p2, p3, rfl, rfl, h2, h3⟩ := genAll2 h2
  exact ⟨w1, w2, w3, p1, p2, p3, by simp, by simp, h1, h2, h3⟩

theorem genAll4 {Y1 Y2 Y3 Y4 : RSym} {w : List Tok} {cs : List Piece} (h : GenAll V [Y1, Y2, Y3, Y4] w cs) :
    ∃ w1 w2 w3 w4 c1 c2 c3 c4, w = w1 ++ w2 ++ w3 ++ w4 ∧ cs = c1 ++ c2 ++ c3 ++ c4 ∧ Gen V Y1 w1 c1 ∧
      Gen V Y2 w2 c2 ∧ Gen V Y3 w3 c3 ∧ Gen V Y4 w4 c4 := by
  obtain ⟨w1, w2, p1, p2, rfl, rfl, h1, h2⟩ := genAll_inv_cons h
  obtain ⟨w2, w3, w4, p2, p3, p4, rfl, rfl, h2, h3, h4⟩ := genAll3 h2
  exact ⟨w1, w2, w3, w4, p1, p2, p3, p4, by simp, by simp, h1, h2, h3, h4⟩

/-- A derivation yields at least one token (W2). -/
theorem gen_ne (hV : framesOk V = true) {Y : RSym} {w : List Tok} {ps : List Piece} (h : Gen V Y w ps) : w ≠ [] := by
  obtain ⟨t, ht, rfl, -⟩ := h
  exact VE.Grammar.yield_ne_nil_of (grammar_wf V hV) _ t ht

/-- The frame numbered `h` is one frame. -/
theorem zip_frame {f g : Frame} {h : Nat} (hf : (f, h) ∈ V.frames.zipIdx) (hg : (g, h) ∈ V.frames.zipIdx) : g = f := by
  rw [List.mem_zipIdx_iff_getElem?] at hf hg
  simp only at hf hg
  rw [hf] at hg; exact (Option.some.inj hg).symm

/-! ### What `framesOk` gives the uniqueness argument -/

theorem firstDup_none : ∀ {l : List String}, firstDup l = none → l.Nodup
  | [], _ => List.nodup_nil
  | x :: xs, h => by
    simp only [firstDup] at h
    split at h
    · cases h
    · next hx => exact List.nodup_cons.mpr ⟨by simpa using hx, firstDup_none h⟩

/-- What `framesOk` gives the uniqueness argument (1.4): reserved words, prefixes and overlaps. -/
structure VocabOk (V : Vocab) : Prop where
  headRes : ∀ g ∈ V.frames, ∀ w ∈ g.head, w ≠ "to" ∧ w ≠ "be" ∧ w ≠ "and" ∧ w ≠ "or" ∧ w ≠ "nor"
  headDup : (V.frames.map (fun g => " ".intercalate g.head)).Nodup
  headPre : ∀ g ∈ V.frames, ∀ g' ∈ V.frames, g.head.isPrefixOf g'.head = true → g'.head = g.head
  modsMk : ∀ g ∈ V.frames, ∀ m ∈ g.mods, m ∉ g.markers
  mkRes : ∀ g ∈ V.frames, ∀ m ∈ g.markers ++ g.mods, m ≠ "" → ∀ w ∈ wordsOf m, w ≠ "and" ∧ w ≠ "or" ∧ w ≠ "nor"
  mkPre : ∀ g ∈ V.frames, ∀ m ∈ g.markers ++ g.mods, m ≠ "" → ∀ n ∈ g.markers ++ g.mods, n ≠ "" →
    (wordsOf m).isPrefixOf (wordsOf n) = true → n = m
  advRes : ∀ w ∈ V.adverbs, w ≠ "and" ∧ w ≠ "or" ∧ w ≠ "nor" ∧ w ≠ "to" ∧ w ≠ "be"
  advMk : ∀ w ∈ V.adverbs, ∀ g ∈ V.frames, ∀ m ∈ g.markers ++ g.mods, m ≠ "" → w ∉ wordsOf m
  advHd : ∀ w ∈ V.adverbs, ∀ g ∈ V.frames, w ∉ g.head

theorem vocabOk {V : Vocab} (h : framesOk V = true) : VocabOk V := by
  have h' : checkVocab V = .ok () := by
    unfold framesOk at h; cases hc : checkVocab V <;> simp_all [Except.isOk, Except.toBool]
  unfold checkVocab at h'
  simp only [bind, Except.bind, pure, Except.pure] at h'
  split at h'; · cases h'
  split at h'; · cases h'
  split at h'; · cases h'
  split at h'; · cases h'
  next h4 =>
  split at h'; · cases h'
  next h5 =>
  split at h'; · cases h'
  next h6 =>
  iterate 4 (split at h'; · cases h')
  split at h'; · cases h'
  next h11 =>
  split at h'; · cases h'
  split at h'; · cases h'
  split at h'; · cases h'
  next h14 =>
  split at h'; · cases h'
  next h15 =>
  split at h'; · cases h'
  split at h'; · cases h'
  next h17 =>
  split at h'; · cases h'
  next h18 =>
  refine ⟨fun g hg w hw => ?_, ?_, fun g hg g' hg' hp => ?_, fun g hg m hm hmk => ?_, fun g hg m hm hne w hw => ?_,
    fun g hg m hm hne n hnm hne' hp => ?_, fun w hw => ?_, fun w hw g hg m hm hne hwm => ?_, fun w hw g hg hwg => ?_⟩
  · have := Lexical.forIn_ok h4 (by intro x; split <;> simp) g hg
    split at this
    · cases this
    next hn =>
    cases hx : g.head.find? (["and", "or", "nor", "to", "be"] ++ Lexical.clauseWords).contains with
    | some u => exact (hn u hx).elim
    | none =>
      have := List.find?_eq_none.mp hx w hw
      refine ⟨?_, ?_, ?_, ?_, ?_⟩ <;> (intro he; subst he; simp at this)
  · cases hx : firstDup (V.frames.map (fun g => " ".intercalate g.head)) with
    | some u => exact (h5 u hx).elim
    | none => exact firstDup_none hx
  · have := Lexical.forIn_ok h6 (by intro x; split <;> simp) g hg
    split at this
    · cases this
    next hn =>
    cases hx : V.frames.find? (fun g' => g'.head != g.head && g.head.isPrefixOf g'.head) with
    | some u => exact (hn u hx).elim
    | none =>
      have := List.find?_eq_none.mp hx g' hg'
      simpa [hp] using this
  · have := Lexical.forIn_ok h11 (by intro x; split <;> simp) g hg
    split at this
    · cases this
    next hn =>
    cases hx : g.mods.find? g.markers.contains with
    | some u => exact (hn u hx).elim
    | none =>
      have := List.find?_eq_none.mp hx m hm
      simp_all
  · have := Lexical.forIn_ok h14 (by intro x; split <;> simp) g hg
    split at this
    · cases this
    next hn =>
    cases hx : (((g.markers ++ g.mods).filter (fun x => decide (x ≠ ""))).flatMap wordsOf).find?
        (["and", "or", "nor", "be"] ++ Lexical.clauseWords).contains with
    | some u => exact (hn u hx).elim
    | none =>
      have := List.find?_eq_none.mp hx w (List.mem_flatMap.mpr ⟨m, List.mem_filter.mpr ⟨hm, by simpa using hne⟩, hw⟩)
      refine ⟨?_, ?_, ?_⟩ <;> (intro he; subst he; simp at this)
  · have := Lexical.forIn_ok h15 (by intro x; split <;> simp) g hg
    split at this
    · cases this
    next hn0 hfor =>
    have := Lexical.forIn_ok hfor (by intro x; split <;> simp) m (List.mem_filter.mpr ⟨hm, by simpa using hne⟩)
    split at this
    · cases this
    next hn2 =>
    cases hx : ((g.markers ++ g.mods).filter (fun x => decide (x ≠ ""))).find?
        (fun n => n != m && (wordsOf m).isPrefixOf (wordsOf n)) with
    | some u => exact (hn2 u hx).elim
    | none =>
      have := List.find?_eq_none.mp hx n (List.mem_filter.mpr ⟨hnm, by simpa using hne'⟩)
      simp only [hp, Bool.and_true, bne_iff_ne, ne_eq, Decidable.not_not] at this
      exact this
  · cases hx : V.adverbs.find? (fun a => !wordOk a || (["and", "or", "nor", "to", "be"] ++ Lexical.clauseWords).contains a) with
    | some u => exact (h17 u hx).elim
    | none =>
      have := List.find?_eq_none.mp hx w hw
      refine ⟨?_, ?_, ?_, ?_, ?_⟩ <;> (intro he; subst he; simp at this)
  · cases hx : V.adverbs.find? (fun a => (V.frames.flatMap (fun f => ((f.markers ++ f.mods).filter
        (fun x => decide (x ≠ ""))).flatMap wordsOf)).contains a || V.frames.any (fun x => x.head.contains a)) with
    | some u => exact (h18 u hx).elim
    | none =>
      have := List.find?_eq_none.mp hx w hw
      simp only [Bool.or_eq_true, not_or, List.contains_iff_mem, List.mem_flatMap, List.mem_filter] at this
      exact this.1 ⟨g, hg, m, ⟨hm, by simpa using hne⟩, hwm⟩
  · cases hx : V.adverbs.find? (fun a => (V.frames.flatMap (fun f => ((f.markers ++ f.mods).filter
        (fun x => decide (x ≠ ""))).flatMap wordsOf)).contains a || V.frames.any (fun x => x.head.contains a)) with
    | some u => exact (h18 u hx).elim
    | none =>
      have := List.find?_eq_none.mp hx w hw
      simp only [Bool.or_eq_true, not_or, List.any_eq_true, List.contains_iff_mem] at this
      exact this.2 ⟨g, hg, by simpa using hwg⟩

/-! ### Tokens: keyword runs, markers, join words, function words, heads, adverbs, filler words -/

theorem kwSyms_cons (w : String) (ws : List String) : kwSyms (w :: ws) = .t (.kw w) :: kwSyms ws := rfl

theorem kw_inv : ∀ {ws : List String} {u : List Tok} {cs : List Piece}, GenAll V (kwSyms ws) u cs →
    ∃ vs : List String, u = vs.map .word ∧ vs.map String.toLower = ws ∧ cs = vs.map .w
  | [], u, cs, h => by
    obtain ⟨rfl, rfl⟩ := genAll_inv_nil (by simpa [kwSyms] using h)
    exact ⟨[], rfl, rfl, rfl⟩
  | w :: ws, u, cs, h => by
    rw [kwSyms_cons] at h
    obtain ⟨w1, w2, p1, p2, rfl, rfl, h1, h2⟩ := genAll_inv_cons h
    obtain ⟨x, rfl, hx, hp⟩ := gen_t_inv h1
    obtain ⟨vs, rfl, hvs, rfl⟩ := kw_inv h2
    cases x with
    | word v =>
      simp only [Term.accepts, beq_iff_eq] at hx
      rw [pieces_word] at hp
      exact ⟨v :: vs, rfl, by simp [hx, hvs], by simp [← Option.some.inj hp]⟩
    | _ => simp [Term.accepts] at hx

theorem ap_FW_w (w : String) (ws : List String) (v : String) (vs : List String) :
    applyRule ⟨.FW, kwSyms (w :: ws), .shape⟩ ((v :: vs).map .w) =
      some [.fw (((v :: vs).map String.toLower).contains "to") (((v :: vs).map String.toLower).contains "be")] := by
  simp only [kwSyms, List.map_cons]; unfold applyRule; split <;> simp_all [filterMap_w]
theorem ap_HD_w (h : Nat) (w : String) (ws : List String) (v : String) (vs : List String) :
    applyRule ⟨.F h .HD, kwSyms (w :: ws), .shape⟩ ((v :: vs).map .w) = some [.head ((v :: vs).map String.toLower)] := by
  simp only [kwSyms, List.map_cons]; unfold applyRule; split <;> simp_all [filterMap_w, Function.comp_def]
theorem ap_J_w (w v : String) : applyRule ⟨.J, kwSyms [w], .shape⟩ [.w v] =
    ([("and", Join.and), ("or", .or), ("nor", .nor)].lookup v.toLower).map ([.j ·]) := by
  simp only [kwSyms, List.map_cons, List.map_nil]; unfold applyRule; split <;> simp_all

theorem mk_inv {m : String} (hw : wordsOf m ≠ []) {u : List Tok} {ps : List Piece} (hg : Gen V (.n (.MK m)) u ps) :
    ps = [] ∧ ∃ vs : List String, u = vs.map .word ∧ vs.map String.toLower = wordsOf m := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr
  obtain ⟨w, ws, hws⟩ := List.exists_cons_of_ne_nil hw
  refine ⟨by rw [hws, ap_MK] at ha; exact (Option.some.inj ha).symm, ?_⟩
  obtain ⟨vs, rfl, hvs, -⟩ := kw_inv hg; exact ⟨vs, rfl, hvs⟩

theorem one_lower {vs : List String} {w : String} (h : vs.map String.toLower = [w]) : ∃ v, vs = [v] ∧ v.toLower = w := by
  match vs, h with
  | [v], h => exact ⟨v, rfl, by simpa using h⟩

theorem j_inv {u : List Tok} {ps : List Piece} (hg : Gen V (.n .J) u ps) :
    ∃ v, u = [.word v] ∧ (v.toLower = "and" ∨ v.toLower = "or" ∨ v.toLower = "nor") := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr <;> obtain ⟨vs, rfl, hvs, -⟩ := kw_inv hg <;> obtain ⟨v, rfl, hv⟩ := one_lower hvs <;>
    exact ⟨v, rfl, by simp [hv]⟩

/-- The pieces of `J`: the join its word names. -/
theorem j_pieces {v : String} {ps : List Piece} (hg : Gen V (.n .J) [.word v] ps) (j : Join)
    (hv : v.toLower = joinWord j) : ps = [.j j] := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr <;> obtain ⟨vs, hu, hvs, rfl⟩ := kw_inv hg <;> obtain ⟨v', rfl, hv'⟩ := one_lower hvs <;>
    simp only [List.map_cons, List.map_nil, List.cons.injEq, Tok.word.injEq, and_true] at hu <;> subst hu <;>
    simp only [List.map_cons, List.map_nil, ap_J_w, hv] at ha <;>
    cases j <;> simp [joinWord, List.lookup] at ha hv' <;> simp_all

theorem fw_inv {u : List Tok} {ps : List Piece} (hg : Gen V (.n .FW) u ps) :
    ∃ vs : List String, u = vs.map .word ∧
      (vs.map String.toLower = ["to"] ∨ vs.map String.toLower = ["be"] ∨ vs.map String.toLower = ["to", "be"]) ∧
      ps = [.fw ((vs.map String.toLower).contains "to") ((vs.map String.toLower).contains "be")] := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr <;> obtain ⟨vs, rfl, hvs, rfl⟩ := kw_inv hg <;> refine ⟨vs, rfl, by simp [hvs], ?_⟩ <;>
    obtain ⟨v, vs', rfl⟩ := List.exists_cons_of_ne_nil (l := vs) (by rintro rfl; simp at hvs) <;>
    rw [ap_FW_w] at ha <;> exact (Option.some.inj ha).symm

theorem hd_inv {f : Frame} {h : Nat} (hf : (f, h) ∈ V.frames.zipIdx) (hne : f.head ≠ []) {u : List Tok}
    {ps : List Piece} (hg : Gen V (.n (.F h .HD)) u ps) :
    ∃ vs : List String, u = vs.map .word ∧ vs.map String.toLower = f.head ∧ ps = [.head f.head] := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr <;> (have e := zip_frame hf hfr; subst fr) <;> obtain ⟨vs, rfl, hvs, rfl⟩ := kw_inv hg <;>
    refine ⟨vs, rfl, hvs, ?_⟩ <;>
    obtain ⟨w, ws, hh⟩ := List.exists_cons_of_ne_nil hne <;>
    obtain ⟨v, vs', rfl⟩ := List.exists_cons_of_ne_nil (l := vs) (by rintro rfl; simp [hh] at hvs) <;>
    rw [hh, ap_HD_w] at ha <;> (rw [← hvs]; exact (Option.some.inj ha).symm)

theorem advo_inv {u : List Tok} {ps : List Piece} (hg : Gen V (.n .ADVO) u ps) :
    ∃ v, u = [.word v] ∧ V.adverbs.contains v.toLower = true ∧ ps = [.elt (.mod (.adv v.toLower)) .own] := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr
  have h1 := genAll1 hg
  obtain ⟨x, rfl, hx, hp⟩ := gen_t_inv h1
  cases x with
  | word v =>
    rw [pieces_word] at hp; cases hp
    rw [ap_ADVO] at ha
    exact ⟨v, rfl, by simpa [Term.accepts] using hx, (Option.some.inj ha).symm⟩
  | _ => simp [Term.accepts] at hx

theorem advso_inv : ∀ (n : Nat) {u : List Tok} {ps : List Piece}, u.length ≤ n → Gen V (.n .ADVSO) u ps →
    ∃ vs : List String, vs ≠ [] ∧ u = vs.map .word ∧ (∀ v ∈ vs, V.adverbs.contains v.toLower = true) ∧
      ps = vs.map (fun v => .elt (.mod (.adv v.toLower)) .own)
  | n, u, ps, hn, hg => by
    obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
    rules_of hr fr hfr
    · rw [ap_ADVSO1] at ha; cases ha
      obtain ⟨v, rfl, hv, rfl⟩ := advo_inv (genAll1 hg)
      exact ⟨[v], by simp, rfl, by simpa using hv, rfl⟩
    · rw [ap_ADVSO2] at ha; cases ha
      obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
      obtain ⟨v, rfl, hv, rfl⟩ := advo_inv h1
      match n with
      | 0 => simp at hn
      | n + 1 =>
        obtain ⟨vs, -, rfl, hvs, rfl⟩ := advso_inv n (by simpa using hn) h2
        exact ⟨v :: vs, by simp, rfl, fun x hx => (List.mem_cons.mp hx).elim (fun e => e ▸ hv) (hvs x), rfl⟩

theorem wr_inv {f : Frame} {h : Nat} (hf : (f, h) ∈ V.frames.zipIdx) : ∀ (n : Nat) {u : List Tok} {ps : List Piece},
    u.length ≤ n → Gen V (.n (.F h .WR)) u ps →
    ∃ vs : List String, vs ≠ [] ∧ u = vs.map .word ∧ (∀ v ∈ vs, (fillExcl V f).contains v.toLower = false) ∧
      ps = vs.map .w
  | n, u, ps, hn, hg => by
    obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
    rules_of hr fr hfr <;> (have e := zip_frame hf hfr; subst fr)
    · obtain ⟨x, rfl, hx, hp⟩ := gen_t_inv (genAll1 hg)
      cases x with
      | word v =>
        rw [pieces_word] at hp; cases hp
        rw [ap_WR1] at ha; cases ha
        exact ⟨[v], by simp, rfl, by simpa [Term.accepts] using hx, rfl⟩
      | _ => simp [Term.accepts] at hx
    · rw [ap_WR2] at ha; cases ha
      obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
      obtain ⟨x, rfl, hx, hp⟩ := gen_t_inv h1
      cases x with
      | word v =>
        rw [pieces_word] at hp; cases hp
        match n with
        | 0 => simp at hn
        | n + 1 =>
          obtain ⟨vs, -, rfl, hvs, rfl⟩ := wr_inv hf n (by simpa using hn) h2
          have hx' : (fillExcl V f).contains v.toLower = false := by simpa [Term.accepts] using hx
          exact ⟨v :: vs, by simp, rfl, fun x hx => (List.mem_cons.mp hx).elim (fun e => e ▸ hx') (hvs x), rfl⟩
      | _ => simp [Term.accepts] at hx

/-- A slot (not `{0}`) or a fixed phrase, as a part. -/
def IsTok (x : Tok) (p : Part) : Prop := (∃ i, x = .slot (i + 1) ∧ p = .slot (i + 1)) ∨ (∃ i, x = .fixed i ∧ p = .fixed i)

theorem tok_inv {u : List Tok} {ps : List Piece} (hg : Gen V (.n .TOK) u ps) :
    ∃ x p, u = [x] ∧ ps = [.part p] ∧ IsTok x p := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr <;> obtain ⟨x, rfl, hx, hp⟩ := gen_t_inv (genAll1 hg) <;>
    (cases x with
     | slot i =>
       cases i with
       | zero => simp [Term.accepts] at hx
       | succ i =>
         simp [piecesOf] at hp; subst hp
         rw [ap_TOK _ (by simp)] at ha; cases ha
         exact ⟨_, _, rfl, rfl, .inl ⟨i, rfl, rfl⟩⟩
     | fixed i =>
       simp [piecesOf] at hp; subst hp
       rw [ap_TOK _ (by simp)] at ha; cases ha
       exact ⟨_, _, rfl, rfl, .inr ⟨i, rfl, rfl⟩⟩
     | _ => simp [Term.accepts] at hx)

/-- A filler, as `FL`: a run of filler words, or one slot or fixed phrase. -/
theorem fl_inv {f : Frame} {h : Nat} (hf : (f, h) ∈ V.frames.zipIdx) {u : List Tok} {ps : List Piece}
    (hg : Gen V (.n (.F h .FL)) u ps) :
    (∃ vs : List String, vs ≠ [] ∧ u = vs.map .word ∧ (∀ v ∈ vs, (fillExcl V f).contains v.toLower = false) ∧
      ps = [.part (.words vs)]) ∨ ∃ x p, u = [x] ∧ ps = [.part p] ∧ IsTok x p := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr <;> (have e := zip_frame hf hfr; subst fr)
  · obtain ⟨vs, hne, rfl, hvs, rfl⟩ := wr_inv hf _ (Nat.le_refl _) (genAll1 hg)
    rw [ap_FL_words] at ha; cases ha
    exact .inl ⟨vs, hne, rfl, hvs, rfl⟩
  · obtain ⟨x, p, rfl, rfl, hx⟩ := tok_inv (genAll1 hg)
    rw [ap_FL_tok] at ha; cases ha
    exact .inr ⟨x, p, rfl, rfl, hx⟩

/-! ### Token classes of a frame, and where a run can stop -/

/-- A filler word of frame `f`: a word that is not one of `fillExcl V f`. -/
def FillW (V : Vocab) (f : Frame) (x : Tok) : Prop := ∃ w, x = .word w ∧ (fillExcl V f).contains w.toLower = false
/-- A word of `fillExcl V f`: a join or function word, an adverb, a first marker word of `f` or a first head word. -/
def ExclW (V : Vocab) (f : Frame) (x : Tok) : Prop := ∃ w, x = .word w ∧ (fillExcl V f).contains w.toLower = true
/-- A comma or a join word. -/
def JC (x : Tok) : Prop := x = .comma ∨ ∃ w, x = .word w ∧ (w.toLower = "and" ∨ w.toLower = "or" ∨ w.toLower = "nor")
/-- The first token of an element of frame `f` after its object: an adverb or the first word of one of its markers. -/
def EF (V : Vocab) (f : Frame) (x : Tok) : Prop :=
  ∃ w, x = .word w ∧ (V.adverbs.contains w.toLower = true ∨
    ∃ m ∈ f.markers ++ f.mods, m ≠ "" ∧ (wordsOf m).head? = some w.toLower)
/-- `v` does not begin with a filler word. -/
def Stop (V : Vocab) (f : Frame) (v : List Tok) : Prop := ∀ x ∈ v.head?, ¬ FillW V f x
/-- `v` is empty or begins an element (`EF`). -/
def Next (V : Vocab) (f : Frame) (v : List Tok) : Prop := ∀ x ∈ v.head?, EF V f x

variable {f : Frame}

theorem excl_not_fill {x : Tok} (h : ExclW V f x) : ¬ FillW V f x := by
  rintro ⟨w, rfl, hw⟩; obtain ⟨w', he, hw'⟩ := h; cases he; simp_all

theorem jw_excl {w : String} (h : w.toLower = "and" ∨ w.toLower = "or" ∨ w.toLower = "nor") :
    (fillExcl V f).contains w.toLower = true := by
  rcases h with h | h | h <;> simp [fillExcl, h]

theorem jc_not_fill {x : Tok} (h : JC x) : ¬ FillW V f x := by
  rcases h with rfl | ⟨w, rfl, hw⟩
  · rintro ⟨w, he, -⟩; cases he
  · exact excl_not_fill ⟨w, rfl, jw_excl hw⟩

theorem ef_excl {x : Tok} (h : EF V f x) : ExclW V f x := by
  obtain ⟨w, rfl, hw⟩ := h
  refine ⟨w, rfl, ?_⟩
  rcases hw with hw | ⟨m, hm, -, hh⟩
  · simp only [fillExcl, List.contains_iff_mem, List.mem_append] at hw ⊢; exact .inl (.inl (.inr hw))
  · simp only [fillExcl, List.contains_iff_mem, List.mem_append, List.mem_filterMap]
    exact .inl (.inr ⟨m, by simpa using hm, hh⟩)

theorem ef_not_jc (hW : VocabOk V) (hfr : f ∈ V.frames) {x : Tok} (h : EF V f x) : ¬ JC x := by
  obtain ⟨w, rfl, hw⟩ := h
  rintro (he | ⟨w', he, hj⟩)
  · cases he
  cases he
  rcases hw with hw | ⟨m, hm, hne, hh⟩
  · have := hW.advRes _ (by simpa using hw)
    rcases hj with hj | hj | hj <;> simp_all
  · have := hW.mkRes f hfr m hm hne w.toLower (List.mem_of_mem_head? hh)
    rcases hj with hj | hj | hj <;> simp_all

theorem next_stop {v : List Tok} (h : Next V f v) : Stop V f v :=
  fun x hx => excl_not_fill (ef_excl (h x hx))

/-- Two splittings of one list agree when the first parts are of one class and the second parts begin outside it. -/
theorem split_class {α : Type} (P : α → Prop) {a b c d : List α} (h : a ++ b = c ++ d) (ha : ∀ x ∈ a, P x)
    (hc : ∀ x ∈ c, P x) (hb : ∀ x ∈ b.head?, ¬ P x) (hd : ∀ x ∈ d.head?, ¬ P x) : a = c ∧ b = d := by
  rcases List.append_eq_append_iff.mp h with ⟨a', rfl, rfl⟩ | ⟨c', rfl, rfl⟩
  · cases a' with
    | nil => simp
    | cons x a' => exact (hb x (by simp) (hc x (by simp))).elim
  · cases c' with
    | nil => simp
    | cons x c' => exact (hd x (by simp) (ha x (by simp))).elim

theorem map_word_inj : ∀ {vs ws : List String}, vs.map Tok.word = ws.map Tok.word → vs = ws
  | [], [], _ => rfl
  | v :: vs, w :: ws, h => by
    simp only [List.map_cons, List.cons.injEq, Tok.word.injEq] at h
    rw [h.1, map_word_inj h.2]
  | [], _ :: _, h => by simp at h
  | _ :: _, [], h => by simp at h

/-- The first token of a part `normalOk` admits: a filler word, a slot other than `{0}`, or a fixed phrase. -/
theorem part_head {p : Part} (hp : PartOk V f p) : ∃ x rest, p.toks = x :: rest ∧ (FillW V f x ∨ ∃ q, IsTok x q) := by
  cases p with
  | words ws =>
    obtain ⟨hne, hw⟩ := hp
    obtain ⟨w, ws', rfl⟩ := List.exists_cons_of_ne_nil hne
    exact ⟨_, _, rfl, .inl ⟨w, rfl, hw w (by simp)⟩⟩
  | slot i =>
    cases i with
    | zero => exact absurd rfl hp
    | succ i => exact ⟨_, _, rfl, .inr ⟨_, .inl ⟨i, rfl, rfl⟩⟩⟩
  | fixed i => exact ⟨_, _, rfl, .inr ⟨_, .inr ⟨i, rfl, rfl⟩⟩⟩

/-- A part's first token is not a word of `fillExcl` (so not a join word, an adverb or a marker's first word). -/
theorem part_head_not_excl {p : Part} (hp : PartOk V f p) : ∃ x rest, p.toks = x :: rest ∧ ¬ ExclW V f x := by
  obtain ⟨x, rest, he, hx⟩ := part_head hp
  refine ⟨x, rest, he, ?_⟩
  rintro ⟨w, rfl, hw⟩
  rcases hx with ⟨w', he', hw'⟩ | ⟨q, ⟨i, he', -⟩ | ⟨i, he', -⟩⟩ <;> cases he'
  simp_all

theorem part_fill_or_tok {p : Part} (hp : PartOk V f p) : ∀ x ∈ p.toks, FillW V f x ∨ ∃ q, IsTok x q := by
  cases p with
  | words ws =>
    intro x hx
    obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hx
    exact .inl ⟨w, rfl, hp.2 w hw⟩
  | slot i =>
    cases i with
    | zero => exact absurd rfl hp
    | succ i => intro x hx; simp [Part.toks] at hx; subst hx; exact .inr ⟨_, .inl ⟨i, rfl, rfl⟩⟩
  | fixed i => intro x hx; simp [Part.toks] at hx; subst hx; exact .inr ⟨_, .inr ⟨i, rfl, rfl⟩⟩

theorem part_not_jc {p : Part} (hp : PartOk V f p) : ∀ x ∈ p.toks, ¬ JC x := by
  intro x hx hj
  rcases part_fill_or_tok hp x hx with hf | ⟨q, ⟨i, rfl, -⟩ | ⟨i, rfl, -⟩⟩
  · exact jc_not_fill hj hf
  all_goals (rcases hj with he | ⟨w, he, -⟩ <;> cases he)

/-! ### A filler and a list of parts -/

/-- A filler (`FL`) that starts where a part starts, and is followed by no filler word, is that part. -/
theorem fl_part {h : Nat} (hf : (f, h) ∈ V.frames.zipIdx) {u v r : List Tok} {ps : List Piece} {p : Part}
    (hg : Gen V (.n (.F h .FL)) u ps) (he : u ++ v = p.toks ++ r) (hp : PartOk V f p) (hv : Stop V f v)
    (hr : Stop V f r) : u = p.toks ∧ v = r ∧ ps = [.part p] := by
  rcases fl_inv hf hg with ⟨vs, hne, rfl, hvs, rfl⟩ | ⟨x, q, rfl, rfl, hx⟩
  · cases p with
    | words ws =>
      obtain ⟨e1, e2⟩ := split_class (FillW V f) he (fun x hx => by
          obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hx; exact ⟨w, rfl, hvs w hw⟩)
        (fun x hx => by obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hx; exact ⟨w, rfl, hp.2 w hw⟩) hv hr
      have := map_word_inj e1
      subst this; exact ⟨rfl, e2, rfl⟩
    | slot i =>
      obtain ⟨w, vs', rfl⟩ := List.exists_cons_of_ne_nil hne
      simp [Part.toks] at he
    | fixed i =>
      obtain ⟨w, vs', rfl⟩ := List.exists_cons_of_ne_nil hne
      simp [Part.toks] at he
  · cases p with
    | words ws =>
      obtain ⟨w, ws', rfl⟩ := List.exists_cons_of_ne_nil hp.1
      rcases hx with ⟨i, rfl, -⟩ | ⟨i, rfl, -⟩ <;> simp [Part.toks] at he
    | slot i =>
      simp only [Part.toks, List.singleton_append, List.cons.injEq] at he
      obtain ⟨rfl, rfl⟩ := he
      rcases hx with ⟨i, he, rfl⟩ | ⟨i, he, -⟩ <;> cases he
      exact ⟨rfl, rfl, rfl⟩
    | fixed i =>
      simp only [Part.toks, List.singleton_append, List.cons.injEq] at he
      obtain ⟨rfl, rfl⟩ := he
      rcases hx with ⟨i, he, -⟩ | ⟨i, he, rfl⟩ <;> cases he
      exact ⟨rfl, rfl, rfl⟩

/-- The tokens of a list after its first part: a comma before each middle part, the join word before the last. -/
def tailToks (j : Join) : List Part → List Tok
  | [] => []
  | [q] => .word (joinWord j) :: q.toks
  | q :: rest => .comma :: (q.toks ++ tailToks j rest)

theorem tailToks_cons2 (j : Join) (q q' : Part) (rest : List Part) :
    tailToks j (q :: q' :: rest) = .comma :: (q.toks ++ tailToks j (q' :: rest)) := rfl

theorem listToks_eq (j : Join) (p q : Part) : ∀ rest : List Part,
    listToks j (p :: q :: rest) = p.toks ++ tailToks j (q :: rest)
  | [] => by simp [listToks, tailToks]
  | q' :: rest => by
    rw [tailToks_cons2, ← listToks_eq j q q' rest]
    simp [listToks]

theorem jw_lower (j : Join) : (joinWord j).toLower = joinWord j := by
  cases j <;> simp [joinWord, lower_and, lower_or, lower_nor]

theorem tailToks_head (j : Join) (q : Part) (rest : List Part) : ∃ x u, tailToks j (q :: rest) = x :: u ∧ JC x := by
  cases rest with
  | nil => exact ⟨_, _, rfl, .inr ⟨_, rfl, by cases j <;> simp [joinWord, lower_and, lower_or, lower_nor]⟩⟩
  | cons q' rest => exact ⟨_, _, rfl, .inl rfl⟩

theorem stop_jc {x : Tok} {u : List Tok} (h : JC x) : Stop V f (x :: u) := by
  intro y hy; cases hy; exact jc_not_fill h

theorem pt_head {h : Nat} {u : List Tok} {cs : List Piece} (hg : Gen V (.n (.F h .PT)) u cs) :
    ∃ x u', u = x :: u' ∧ JC x := by
  obtain ⟨rhs, k, cs', hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr
  · obtain ⟨w1, w2, c1, c2, rfl, -, h1, -⟩ := genAll2 hg
    obtain ⟨v, rfl, hv⟩ := j_inv h1
    exact ⟨_, _, rfl, .inr ⟨v, rfl, hv⟩⟩
  all_goals
    obtain ⟨w1, w2, c1, c2, rfl, -, h1, -⟩ := genAll_inv_cons hg
    obtain ⟨x, rfl, hx, -⟩ := gen_t_inv h1
    cases x <;> simp [Term.accepts] at hx
    exact ⟨_, _, rfl, .inl rfl⟩

theorem jw_not_part {p : Part} (hp : PartOk V f p) {v : String} (hv : v.toLower = "and" ∨ v.toLower = "or" ∨ v.toLower = "nor")
    {rest : List Tok} : p.toks ≠ .word v :: rest := by
  obtain ⟨x, rest', he, hx⟩ := part_head_not_excl hp
  rw [he]; intro e; cases e
  exact hx ⟨v, rfl, jw_excl hv⟩

theorem pt_inv {h : Nat} (hf : (f, h) ∈ V.frames.zipIdx) (j : Join) : ∀ (rest : List Part) (q : Part)
    {u v r : List Tok} {cs : List Piece}, Gen V (.n (.F h .PT)) u cs → u ++ v = tailToks j (q :: rest) ++ r →
    (∀ x ∈ q :: rest, PartOk V f x) → Stop V f v → Stop V f r →
    u = tailToks j (q :: rest) ∧ v = r ∧ ∀ p, listOf (.part p :: cs) = some (j, (p :: q :: rest).map .part)
  | rest, q, u, v, r, cs, hg, he, hok, hv, hr => by
    obtain ⟨rhs, k, cs', hr', hg, ha⟩ := gen_rule hg
    rules_of hr' fr hfr <;> (have e := zip_frame hf hfr; subst fr)
    · rw [ap_PT1] at ha; cases ha
      obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
      obtain ⟨v0, rfl, hv0⟩ := j_inv h1
      cases rest with
      | nil =>
        simp only [tailToks, List.append_assoc, List.singleton_append, List.cons_append, List.cons.injEq,
          Tok.word.injEq] at he
        obtain ⟨rfl, he⟩ := he
        obtain ⟨rfl, rfl, rfl⟩ := fl_part hf h2 he (hok q (by simp)) hv hr
        refine ⟨by simp [tailToks], rfl, fun p => ?_⟩
        rw [j_pieces h1 j (jw_lower j)]
        simp [listOf]
      | cons q' rest => simp [tailToks] at he
    · obtain ⟨w1, w2, w3, c1, c2, c3, rfl, rfl, h1, h2, h3⟩ := genAll3 hg
      obtain ⟨x, rfl, hx, -⟩ := gen_t_inv h1
      cases x <;> simp [Term.accepts] at hx
      obtain ⟨v0, rfl, hv0⟩ := j_inv h2
      cases rest with
      | nil => simp [tailToks] at he
      | cons q' rest =>
        simp only [tailToks_cons2, List.append_assoc, List.singleton_append, List.cons_append, List.cons.injEq,
          true_and] at he
        obtain ⟨x, rest', hq, hx⟩ := part_head_not_excl (hok q (by simp))
        rw [hq] at he
        simp only [List.nil_append, List.cons_append, List.cons.injEq] at he
        exact (hx (he.1 ▸ ⟨v0, rfl, jw_excl hv0⟩)).elim
    · obtain ⟨w1, w2, w3, c1, c2, c3, rfl, rfl, h1, h2, h3⟩ := genAll3 hg
      obtain ⟨x, rfl, hx, hp1⟩ := gen_t_inv h1
      cases x <;> simp [Term.accepts] at hx
      simp [piecesOf] at hp1; subst hp1
      rw [ap_PT2] at ha; cases ha
      cases rest with
      | nil => simp [tailToks] at he
      | cons q' rest =>
        simp only [tailToks_cons2, List.append_assoc, List.singleton_append, List.cons_append, List.cons.injEq,
          true_and] at he
        obtain ⟨x3, w3', rfl, hx3⟩ := pt_head h3
        obtain ⟨xt, ut, htl, hxt⟩ := tailToks_head j q' rest
        obtain ⟨rfl, he2, rfl⟩ := fl_part hf h2 he (hok q (by simp)) (stop_jc hx3) (by rw [htl]; exact stop_jc hxt)
        obtain ⟨e3, rfl, hl⟩ := pt_inv hf j rest q' h3 he2 (fun x hx => hok x (List.mem_cons_of_mem _ hx)) hv hr
        refine ⟨by rw [tailToks_cons2, ← e3]; simp, rfl, fun p => ?_⟩
        simp only [List.nil_append, List.singleton_append, listOf_part, hl q, Option.map_some]
        rfl

theorem ap_PL_inv {h : Nat} {p : Part} {cs : List Piece} {j : Join} {ps : List Part} {X : List Piece}
    (hl : listOf (.part p :: cs) = some (j, ps.map .part))
    (ha : applyRule ⟨.F h .PL, [.n (.F h .FL), .n (.F h .PT)], .shape⟩ (.part p :: cs) = some X) : X = [.list j ps] := by
  unfold applyRule at ha
  split at ha <;> simp_all [Function.comp_def, mapM_some, mapM_part]

theorem pl_inv {h : Nat} (hf : (f, h) ∈ V.frames.zipIdx) {j : Join} {ps : List Part} {u v r : List Tok}
    {cs : List Piece} (hg : Gen V (.n (.F h .PL)) u cs) (he : u ++ v = listToks j ps ++ r) (hlen : 2 ≤ ps.length)
    (hok : ∀ x ∈ ps, PartOk V f x) (hv : Stop V f v) (hr : Stop V f r) :
    u = listToks j ps ∧ v = r ∧ cs = [.list j ps] := by
  obtain ⟨p, q, rest, rfl⟩ : ∃ p q rest, ps = p :: q :: rest := by
    match ps, hlen with
    | p :: q :: rest, _ => exact ⟨p, q, rest, rfl⟩
  obtain ⟨rhs, k, cs', hr', hg, ha⟩ := gen_rule hg
  rules_of hr' fr hfr
  have e := zip_frame hf hfr; subst fr
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
  rw [listToks_eq, List.append_assoc, List.append_assoc] at he
  obtain ⟨x2, w2', rfl, hx2⟩ := pt_head h2
  obtain ⟨xt, ut, htl, hxt⟩ := tailToks_head j q rest
  obtain ⟨rfl, he2, rfl⟩ := fl_part hf h1 he (hok p (by simp)) (stop_jc hx2) (by rw [htl]; exact stop_jc hxt)
  obtain ⟨e2, rfl, hl⟩ := pt_inv hf j rest q h2 he2 (fun x hx => hok x (List.mem_cons_of_mem _ hx)) hv hr
  refine ⟨by rw [listToks_eq, e2], rfl, ap_PL_inv (hl p) ha⟩

/-- A part followed by a comma or a join word, where the normal form has the part followed by an element (or the end):
impossible. -/
theorem jc_after_part (hW : VocabOk V) (hfr : f ∈ V.frames) {h : Nat} (hf : (f, h) ∈ V.frames.zipIdx) {p : Part}
    {u x w r : List Tok} {cs : List Piece} (hg : Gen V (.n (.F h .FL)) u cs) (he : u ++ x ++ w = p.toks ++ r)
    (hx : ∃ y x', x = y :: x' ∧ JC y) (hp : PartOk V f p) (hr : Next V f r) : False := by
  obtain ⟨y, x', rfl, hy⟩ := hx
  rw [List.append_assoc] at he
  obtain ⟨-, rfl, -⟩ := fl_part hf hg he hp (stop_jc hy) (next_stop hr)
  exact ef_not_jc hW hfr (hr y (by simp)) hy

theorem pl_one (hW : VocabOk V) (hfr : f ∈ V.frames) {h : Nat} (hf : (f, h) ∈ V.frames.zipIdx) {p : Part}
    {u v r : List Tok} {cs : List Piece} (hg : Gen V (.n (.F h .PL)) u cs) (he : u ++ v = p.toks ++ r)
    (hp : PartOk V f p) (hr : Next V f r) : False := by
  obtain ⟨rhs, k, cs', hr', hg, ha⟩ := gen_rule hg
  rules_of hr' fr hfr'
  have e := zip_frame hf hfr'; subst fr
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
  rw [List.append_assoc, ← List.append_assoc w1] at he
  exact jc_after_part hW hfr hf h1 he (pt_head h2) hp hr

/-! ### Markers: a marker's words fix the marker -/

theorem map_word_append : ∀ {vs ws : List String} {w r : List Tok}, vs.map Tok.word ++ w = ws.map Tok.word ++ r →
    (∃ t, ws = vs ++ t ∧ w = t.map Tok.word ++ r) ∨ (∃ t, vs = ws ++ t ∧ r = t.map Tok.word ++ w)
  | [], ws, w, r, h => .inl ⟨ws, rfl, by simpa using h⟩
  | v :: vs, [], w, r, h => .inr ⟨v :: vs, rfl, by simpa using h.symm⟩
  | v :: vs, x :: ws, w, r, h => by
    simp only [List.map_cons, List.cons_append, List.cons.injEq, Tok.word.injEq] at h
    obtain ⟨rfl, h⟩ := h
    rcases map_word_append h with ⟨t, rfl, rfl⟩ | ⟨t, rfl, rfl⟩
    · exact .inl ⟨t, rfl, rfl⟩
    · exact .inr ⟨t, rfl, rfl⟩

theorem lower_map {ws : List String} (h : ∀ w ∈ ws, w.toLower = w) : ws.map String.toLower = ws := by
  rw [List.map_congr_left h, List.map_id']

/-- `MK m` where the normal form has the words of marker `n` of the same frame: `m` is `n` (no marker of a frame
begins another), and `MK m` reads exactly those words. -/
theorem mk_block (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {m n : String} (hm : m ∈ f.markers ++ f.mods)
    (hmne : m ≠ "") (hn : n ∈ f.markers ++ f.mods) (hnne : n ≠ "") {u w r : List Tok} {ps : List Piece}
    (hg : Gen V (.n (.MK m)) u ps) (he : u ++ w = (wordsOf n).map .word ++ r) :
    m = n ∧ u = (wordsOf n).map .word ∧ w = r ∧ ps = [] := by
  obtain ⟨rfl, vs, rfl, hvs⟩ := mk_inv (hF.words m hm hmne) hg
  have ln := hF.lower n hn hnne
  rcases map_word_append he with ⟨t, ht, rfl⟩ | ⟨t, rfl, rfl⟩
  · have hl : vs.map String.toLower = vs := lower_map (fun x hx => ln x (by rw [ht]; exact List.mem_append_left _ hx))
    have hpre : (wordsOf m).isPrefixOf (wordsOf n) = true := by
      rw [List.isPrefixOf_iff_prefix, ← hvs, hl, ht]; exact List.prefix_append _ _
    have := hW.mkPre f hF.frame m hm hmne n hn hnne hpre
    subst this
    rw [← hvs, hl] at ht
    have : t = [] := by simpa using ht
    subst this
    rw [← hvs, hl]; simp
  · have hpre : (wordsOf n).isPrefixOf (wordsOf m) = true := by
      rw [List.isPrefixOf_iff_prefix, ← hvs, List.map_append, lower_map ln]; exact List.prefix_append _ _
    have := hW.mkPre f hF.frame n hn hnne m hm hmne hpre
    subst this
    rw [List.map_append, lower_map ln] at hvs
    have : t = [] := by simpa using hvs
    subst this
    simp

/-! ### The elements after the object -/

/-- An element of the normal form after the object: an argument (its marker is not `""`) or a prepositional
modifier. -/
inductive Blk | arg (m : String) (fl : Filler) | prep (m : String) (p : Part)

def Blk.marker : Blk → String
  | .arg m _ => m
  | .prep m _ => m
def Blk.rest : Blk → List Tok
  | .arg _ fl => fl.toks
  | .prep _ p => p.toks
def Blk.toks (b : Blk) : List Tok := (wordsOf b.marker).map .word ++ b.rest
def Blk.piece : Blk → Piece
  | .arg m fl => .elt (.arg m fl) .own
  | .prep m p => .elt (.mod (.prep m p)) .own
/-- An element `normalOk` admits under frame `f`. -/
def BlkOk (V : Vocab) (f : Frame) : Blk → Prop
  | .arg m fl => m ∈ f.markers ∧ m ≠ "" ∧ (∀ p ∈ fl.parts, PartOk V f p) ∧
      ∀ j ps, fl = .joined j ps → f.split.contains m = false ∧ 2 ≤ ps.length ∧ longEnd ps = false
  | .prep m p => m ∈ f.mods ∧ PartOk V f p
def blocks (bs : List Blk) : List Tok := bs.flatMap Blk.toks

theorem blkOk_marker {b : Blk} (hb : BlkOk V f b) (hF : FrameOk V f h) : b.marker ∈ f.markers ++ f.mods ∧ b.marker ≠ "" := by
  cases b with
  | arg m fl => exact ⟨List.mem_append_left _ hb.1, hb.2.1⟩
  | prep m p => exact ⟨List.mem_append_right _ hb.1, fun he => hF.mods (he ▸ hb.1)⟩

theorem blocks_next {h : Nat} (hF : FrameOk V f h) : ∀ {bs : List Blk}, (∀ b ∈ bs, BlkOk V f b) → Next V f (blocks bs)
  | [], _ => by intro x hx; simp [blocks] at hx
  | b :: bs, hbs => by
    intro x hx
    obtain ⟨hm, hne⟩ := blkOk_marker (hbs b (by simp)) hF
    obtain ⟨w, ws, hw⟩ := List.exists_cons_of_ne_nil (hF.words _ hm hne)
    simp [blocks, Blk.toks, hw] at hx
    subst hx
    refine ⟨w, rfl, .inr ⟨b.marker, hm, hne, ?_⟩⟩
    rw [hw, hF.lower _ hm hne w (by simp [hw])]; rfl

theorem blocks_cons (b : Blk) (bs : List Blk) : blocks (b :: bs) = (wordsOf b.marker).map .word ++ (b.rest ++ blocks bs) := by
  simp [blocks, Blk.toks]

/-- What starts an element: the first word of a marker of the frame. -/
theorem mk_head {h : Nat} (hF : FrameOk V f h) {m : String} (hm : m ∈ f.markers ++ f.mods) (hne : m ≠ "")
    {u : List Tok} {ps : List Piece} (hg : Gen V (.n (.MK m)) u ps) : Next V f u := by
  obtain ⟨-, vs, rfl, hvs⟩ := mk_inv (hF.words m hm hne) hg
  intro x hx
  cases vs with
  | nil => simp at hx
  | cons v vs =>
    simp at hx; subst hx
    refine ⟨v, rfl, .inr ⟨m, hm, hne, ?_⟩⟩
    rw [← hvs]; rfl

theorem gen_head2 (hV : framesOk V = true) {Y1 Y2 : RSym} {w : List Tok} {cs : List Piece} (h : GenAll V [Y1, Y2] w cs)
    {P : List Tok → Prop} (hP : ∀ u c, Gen V Y1 u c → ∀ x ∈ u.head?, P [x]) : ∀ x ∈ w.head?, P [x] := by
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, -⟩ := genAll2 h
  obtain ⟨x, w1', rfl⟩ := List.exists_cons_of_ne_nil (gen_ne hV h1)
  intro y hy; simp at hy; subst hy; exact hP _ _ h1 x (by simp)

/-- `MK m` then anything: it starts with `m`'s first word. -/
theorem mk_then_head (hV : framesOk V = true) {h : Nat} (hF : FrameOk V f h) {m : String} (hm : m ∈ f.markers ++ f.mods)
    (hne : m ≠ "") {Y : RSym} {w : List Tok} {cs : List Piece} (hg : GenAll V [.n (.MK m), Y] w cs) : Next V f w := by
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, -⟩ := genAll2 hg
  obtain ⟨x, w1', rfl⟩ := List.exists_cons_of_ne_nil (gen_ne hV h1)
  intro y hy; simp at hy; subst hy; exact mk_head hF hm hne h1 x (by simp)

theorem ar_head (hV : framesOk V = true) {h : Nat} (hF : FrameOk V f h) {m : String} (hm : m ∈ f.markers)
    (hne : m ≠ "") {u : List Tok} {ps : List Piece} (hg : Gen V (.n (.F h (.AR m))) u ps) : Next V f u := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr
  have e := zip_frame hF.mem hfr; subst fr
  exact mk_then_head hV hF (List.mem_append_left _ hm) hne hg

theorem rl_head (hV : framesOk V = true) {h : Nat} (hF : FrameOk V f h) {m : String}
    {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h (.RL m))) u ps) : Next V f u := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr
  have e := zip_frame hF.mem hfr; subst fr
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, -⟩ := genAll2 hg
  obtain ⟨x, w1', rfl⟩ := List.exists_cons_of_ne_nil (gen_ne hV h1)
  intro y hy; simp at hy; subst hy
  exact ar_head hV hF (by assumption) (by assumption) h1 x (by simp)

theorem ol_head (hV : framesOk V = true) {h : Nat} (hF : FrameOk V f h) {m : String}
    {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h (.OL m))) u ps) : Next V f u := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr
  have e := zip_frame hF.mem hfr; subst fr
  exact mk_then_head hV hF (List.mem_append_left _ (by assumption)) (by assumption) hg

theorem lst_head (hV : framesOk V = true) {h : Nat} (hF : FrameOk V f h) {m : String} {sp : Bool}
    {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h (.LST m sp))) u ps) : Next V f u := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr)
  · exact rl_head hV hF (genAll1 hg)
  · exact ol_head hV hF (genAll1 hg)

theorem adv_head {u : List Tok} {cs : List Piece} (hg : GenAll V [.t (.adv V.adverbs)] u cs) : Next V f u := by
  obtain ⟨x, rfl, hx, -⟩ := gen_t_inv (genAll1 hg)
  intro y hy; simp at hy; subst hy
  cases x <;> simp [Term.accepts] at hx
  exact ⟨_, rfl, .inl (by simpa using hx)⟩

theorem head_first (hV : framesOk V = true) {Y : RSym} {Ys : List RSym} {w : List Tok} {cs : List Piece}
    (hg : GenAll V (Y :: Ys) w cs) (hY : ∀ u c, Gen V Y u c → Next V f u) : Next V f w := by
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, -⟩ := genAll_inv_cons hg
  obtain ⟨x, w1', rfl⟩ := List.exists_cons_of_ne_nil (gen_ne hV h1)
  intro y hy; simp at hy; subst hy; exact hY _ _ h1 x (by simp)

theorem ee_head (hV : framesOk V = true) {h : Nat} (hF : FrameOk V f h)
    {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h .EE)) u ps) : Next V f u := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr)
  · exact ar_head hV hF (by assumption) (by assumption) (genAll1 hg)
  · exact lst_head hV hF (genAll1 hg)
  · exact adv_head hg
  · exact mk_then_head hV hF (List.mem_append_right _ (by assumption)) (fun he => hF.mods (he ▸ (by assumption))) hg

theorem er_head (hV : framesOk V = true) {h : Nat} (hF : FrameOk V f h)
    {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h .ER)) u ps) : Next V f u := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr) <;>
    exact head_first hV hg (fun _ _ h1 => ee_head hV hF h1)

theorem mel_head (hV : framesOk V = true) {h : Nat} (hF : FrameOk V f h)
    {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h .MEL)) u ps) : Next V f u := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr)
  · exact adv_head hg
  · exact mk_then_head hV hF (List.mem_append_right _ (by assumption)) (fun he => hF.mods (he ▸ (by assumption))) hg

theorem spl_head (hV : framesOk V = true) {h : Nat} (hF : FrameOk V f h)
    {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h .SPL)) u ps) : Next V f u := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr)
  · exact lst_head hV hF (genAll1 hg)
  · obtain ⟨rhs2, k2, cs2, hr2, hg2, ha2⟩ := gen_rule (genAll1 hg)
    rules_of hr2 fr2 hfr2
    have e := zip_frame hF.mem hfr2; subst fr2
    exact head_first hV hg2 (fun _ _ h1 => mel_head hV hF h1)

/-- A list tail (`RT`, `MGT`) starts with a comma or a join word. -/
theorem rt_head {h : Nat} {m : String} {u : List Tok} {cs : List Piece} (hg : Gen V (.n (.F h (.RT m))) u cs) :
    ∃ x u', u = x :: u' ∧ JC x := by
  obtain ⟨rhs, k, cs', hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr
  · obtain ⟨w1, w2, c1, c2, rfl, -, h1, -⟩ := genAll2 hg
    obtain ⟨v, rfl, hv⟩ := j_inv h1
    exact ⟨_, _, rfl, .inr ⟨v, rfl, hv⟩⟩
  all_goals
    obtain ⟨w1, w2, c1, c2, rfl, -, h1, -⟩ := genAll_inv_cons hg
    obtain ⟨x, rfl, hx, -⟩ := gen_t_inv h1
    cases x <;> simp [Term.accepts] at hx
    exact ⟨_, _, rfl, .inl rfl⟩

theorem mgt_head {h : Nat} {u : List Tok} {cs : List Piece} (hg : Gen V (.n (.F h .MGT)) u cs) :
    ∃ x u', u = x :: u' ∧ JC x := by
  obtain ⟨rhs, k, cs', hr, hg, ha⟩ := gen_rule hg
  rules_of hr fr hfr
  · obtain ⟨w1, w2, c1, c2, rfl, -, h1, -⟩ := genAll2 hg
    obtain ⟨v, rfl, hv⟩ := j_inv h1
    exact ⟨_, _, rfl, .inr ⟨v, rfl, hv⟩⟩
  all_goals
    obtain ⟨w1, w2, c1, c2, rfl, -, h1, -⟩ := genAll_inv_cons hg
    obtain ⟨x, rfl, hx, -⟩ := gen_t_inv h1
    cases x <;> simp [Term.accepts] at hx
    exact ⟨_, _, rfl, .inl rfl⟩

/-- `RT m`'s second token is a join word or `m`'s first word. -/
theorem rt_head2 (hV : framesOk V = true) {h : Nat} (hF : FrameOk V f h) {m : String} {u : List Tok}
    {cs : List Piece} (hg0 : Gen V (.n (.F h (.RT m))) u cs) : ∃ x y u', u = x :: y :: u' ∧ ExclW V f y := by
  obtain ⟨rhs, k, cs', hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr)
  · obtain ⟨w1, w2, c1, c2, rfl, -, h1, h2⟩ := genAll2 hg
    obtain ⟨v, rfl, hv⟩ := j_inv h1
    obtain ⟨y, w2', rfl⟩ := List.exists_cons_of_ne_nil (gen_ne hV h2)
    exact ⟨_, y, w2', rfl, ef_excl (ar_head hV hF (by assumption) (by assumption) h2 y (by simp))⟩
  · obtain ⟨w1, w2, w3, c1, c2, c3, rfl, -, h1, h2, -⟩ := genAll3 hg
    obtain ⟨x, rfl, -, -⟩ := gen_t_inv h1
    obtain ⟨v, rfl, hv⟩ := j_inv h2
    exact ⟨x, _, _, rfl, ⟨v, rfl, jw_excl hv⟩⟩
  · obtain ⟨w1, w2, w3, c1, c2, c3, rfl, -, h1, h2, -⟩ := genAll3 hg
    obtain ⟨x, rfl, -, -⟩ := gen_t_inv h1
    obtain ⟨y, w2', rfl⟩ := List.exists_cons_of_ne_nil (gen_ne hV h2)
    exact ⟨x, y, w2' ++ w3, by simp, ef_excl (ar_head hV hF (by assumption) (by assumption) h2 y (by simp))⟩

theorem tailToks_two (j : Join) (q : Part) (rest : List Part) : ∃ t more, tailToks j (q :: rest) = t :: (q.toks ++ more) := by
  cases rest with
  | nil => exact ⟨.word (joinWord j), [], by simp [tailToks]⟩
  | cons q' rest => exact ⟨_, _, tailToks_cons2 j q q' rest⟩

end VE.Acts.NormalProofs
