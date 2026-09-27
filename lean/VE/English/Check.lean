import VE.English.ParseProofs

/-! # A decision procedure for the lexical conditions

`admissible L` is a finite Boolean check over the sorts, predicates and
constants of a lexicon; `admissible_sound` shows it implies `Admitted L`, so the
core theorems apply to every vocabulary that passes it. The check is
conservative: templates are compared slot by slot, and a literal word that
could begin a term is treated as a possible collision with a placeholder. -/
namespace VE.English

def atomStopWords : List String := [",", ";", ".", "and", "or"]

def openerWords : List String := ["it", "both", "either", "if", "all", "at", "for", "there", "of"]

/-- Words that can begin a term: reference keywords and first constant words. -/
def startsTerm (L : Lexicon) (w : String) : Bool :=
  w == "that" || w == "the" || L.constants.any fun c => (L.spelling c).head? == some w

/-- Instances of the two templates can never have the same tokens. -/
def disj (L : Lexicon) : Template → Template → Bool
  | [], [] => false
  | [], _ :: _ => true
  | _ :: _, [] => true
  | .word a :: r, .word b :: s => a != b || disj L r s
  | .hole _ :: r, .hole _ :: s => disj L r s
  | .word a :: _, .hole _ :: _ => !startsTerm L a
  | .hole _ :: _, .word b :: _ => !startsTerm L b

inductive AtomKey where
  | truth
  | falsity
  | eq
  | pred (p : String)
  deriving DecidableEq

def truthT : Template := [.word "this", .word "holds", .word "in", .word "all", .word "cases"]
def falsityT : Template := [.word "this", .word "is", .word "impossible"]
def eqT : Template := [.hole 0, .word "is", .word "the", .word "same", .word "as", .hole 1]

def keyTemplates (L : Lexicon) : List (AtomKey × Template) :=
  [(.truth, truthT), (.falsity, falsityT), (.eq, eqT)] ++
    L.predicates.filterMap fun p => (L.template p).map fun T => (.pred p, T)

def templateWords (T : Template) : List String :=
  T.filterMap fun | .word w => some w | .hole _ => none

def templateHoles (T : Template) : List Nat :=
  T.filterMap fun | .hole i => some i | .word _ => none

def templateOk (T : Template) : Bool :=
  (templateWords T).all (fun w => !atomStopWords.contains w) &&
  (templateHoles T).all (· < T.arity) &&
  match T with
  | .word w :: _ => !openerWords.contains w
  | .hole _ :: _ => true
  | [] => false

def admissible (L : Lexicon) : Bool :=
  L.sorts.all (fun s => match L.noun s with
    | x :: _ => x != "first" && x != "second"
    | [] => false) &&
  L.sorts.all (fun s => (L.noun s).all fun w => !atomStopWords.contains w) &&
  L.sorts.all (fun s => L.sorts.all fun s' =>
    !(kws (L.noun s)).isPrefixOf (kws (L.noun s')) || s == s') &&
  L.sorts.all (fun s => L.sorts.all fun s' => L.letter s != L.letter s' || s == s') &&
  L.constants.all (fun c => match L.spelling c with
    | x :: _ => !openerWords.contains x && x != "that" && x != "the"
    | [] => false) &&
  L.constants.all (fun c => (L.spelling c).all fun w => !atomStopWords.contains w) &&
  L.constants.all (fun c => L.constants.all fun c' =>
    !(kws (L.spelling c)).isPrefixOf (kws (L.spelling c')) || c == c') &&
  L.predicates.all (fun p => match L.template p with
    | some T => templateOk T
    | none => false) &&
  (keyTemplates L).all fun kT => (keyTemplates L).all fun kT' => kT.1 == kT'.1 || disj L kT.2 kT'.2

/-! ## Unpacking the check -/

structure Facts (L : Lexicon) : Prop where
  noun_opens : ∀ s ∈ L.sorts, ∃ x rest, L.noun s = x :: rest ∧ x ≠ "first" ∧ x ≠ "second"
  noun_words : ∀ s ∈ L.sorts, ∀ w ∈ L.noun s, w ∉ atomStopWords
  noun_prefix_free : ∀ s ∈ L.sorts, ∀ s' ∈ L.sorts, kws (L.noun s) <+: kws (L.noun s') → s = s'
  letter_inj : ∀ s ∈ L.sorts, ∀ s' ∈ L.sorts, L.letter s = L.letter s' → s = s'
  const_opens : ∀ c ∈ L.constants, ∃ x rest, L.spelling c = x :: rest ∧ x ∉ openerWords ∧
    x ≠ "that" ∧ x ≠ "the"
  const_words : ∀ c ∈ L.constants, ∀ w ∈ L.spelling c, w ∉ atomStopWords
  const_prefix_free : ∀ c ∈ L.constants, ∀ c' ∈ L.constants,
    kws (L.spelling c) <+: kws (L.spelling c') → c = c'
  templates : ∀ p ∈ L.predicates, ∃ T, L.template p = some T ∧ templateOk T = true
  disjoint : ∀ kT ∈ keyTemplates L, ∀ kT' ∈ keyTemplates L, kT.1 ≠ kT'.1 → disj L kT.2 kT'.2 = true

theorem facts_of_admissible {L : Lexicon} (h : admissible L = true) : Facts L := by
  simp only [admissible, Bool.and_eq_true, List.all_eq_true, Bool.or_eq_true, Bool.not_eq_true',
    beq_iff_eq, bne_iff_ne, ne_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩, h8⟩, h9⟩ := h
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro s hs
    have := h1 s hs
    split at this
    · rename_i x rest hx
      simp only [Bool.and_eq_true, bne_iff_ne, ne_eq] at this
      exact ⟨x, rest, hx, this.1, this.2⟩
    · simp at this
  · intro s hs w hw
    have := h2 s hs w hw
    simpa using this
  · intro s hs s' hs' hp
    rcases h3 s hs s' hs' with h | h
    · rw [List.isPrefixOf_iff_prefix.mpr hp] at h; simp at h
    · exact h
  · intro s hs s' hs' hl
    rcases h4 s hs s' hs' with h | h
    · exact absurd hl h
    · exact h
  · intro c hc
    have := h5 c hc
    split at this
    · rename_i x rest hx
      simp only [Bool.and_eq_true, Bool.not_eq_true', bne_iff_ne, ne_eq] at this
      refine ⟨x, rest, hx, ?_, this.1.2, this.2⟩
      intro hm
      have h := this.1.1
      rw [List.contains_iff_mem.mpr hm] at h
      simp at h
    · simp at this
  · intro c hc w hw
    have := h6 c hc w hw
    simpa using this
  · intro c hc c' hc' hp
    rcases h7 c hc c' hc' with h | h
    · rw [List.isPrefixOf_iff_prefix.mpr hp] at h; simp at h
    · exact h
  · intro p hp
    have := h8 p hp
    split at this
    · rename_i T hT
      exact ⟨T, hT, this⟩
    · simp at this
  · intro kT hkT kT' hkT' hne
    rcases h9 kT hkT kT' hkT' with h | h
    · exact absurd h hne
    · exact h

/-! ## Terms -/

theorem kw_mem_kws {w : String} {ws : List String} : kw w ∈ kws ws ↔ w ∈ ws := by
  simp [kws, kw]

theorem label_not_mem_kws {c : String} {k : Nat} {ws : List String} : Tok.label c k ∉ kws ws := by
  simp [kws]

theorem mem_kws {x : Tok} {ws : List String} (h : x ∈ kws ws) : ∃ w ∈ ws, x = kw w := by
  simp only [kws, List.mem_map] at h
  obtain ⟨w, hw, rfl⟩ := h
  exact ⟨w, hw, rfl⟩

section
variable {L : Lexicon} (F : Facts L)
include F

theorem term_tokens {t : TermTree} (hok : t.ok L = true) : ∀ x ∈ t.yield L, x ∉ atomStops := by
  intro x hx hs
  obtain ⟨w, hw, rfl⟩ := mem_kws hs
  cases t with
  | const c =>
    simp only [TermTree.ok, List.contains_iff_mem] at hok
    exact F.const_words c hok w (kw_mem_kws.mp hx) hw
  | ref r =>
    simp only [TermTree.ok, List.contains_iff_mem] at hok
    cases r with
    | plain s =>
      simp only [TermTree.yield, Ref.refYield, List.mem_cons] at hx
      rcases hx with h | h
      · simp [kw] at h; subst h; simp at hw
      · exact F.noun_words s hok w (kw_mem_kws.mp h) hw
    | first s =>
      simp only [TermTree.yield, Ref.refYield, List.mem_cons] at hx
      rcases hx with h | h | h
      · simp [kw] at h; subst h; simp at hw
      · simp [kw] at h; subst h; simp at hw
      · exact F.noun_words s hok w (kw_mem_kws.mp h) hw
    | second s =>
      simp only [TermTree.yield, Ref.refYield, List.mem_cons] at hx
      rcases hx with h | h | h
      · simp [kw] at h; subst h; simp at hw
      · simp [kw] at h; subst h; simp at hw
      · exact F.noun_words s hok w (kw_mem_kws.mp h) hw
    | named s k => simp [TermTree.yield, Ref.refYield, kw] at hx

theorem term_opens {t : TermTree} (hok : t.ok L = true) :
    ∃ x rest, t.yield L = x :: rest ∧ x ∉ openers ∧ ∀ w, x = kw w → startsTerm L w = true := by
  cases t with
  | const c =>
    simp only [TermTree.ok, List.contains_iff_mem] at hok
    obtain ⟨x, rest, hx, ho, -, -⟩ := F.const_opens c hok
    refine ⟨kw x, kws rest, by simp [TermTree.yield, hx], ?_, ?_⟩
    · intro hm
      apply ho
      simp only [openers, openerWords, kws, kw, List.map, List.mem_cons, Tok.word.injEq,
        List.not_mem_nil, or_false] at hm ⊢
      exact hm
    · intro w hw
      simp only [kw, Tok.word.injEq] at hw
      subst hw
      simp only [startsTerm, Bool.or_eq_true, beq_iff_eq, List.any_eq_true]
      exact Or.inr ⟨c, hok, by simp [hx]⟩
  | ref r =>
    cases r with
    | plain s =>
      exact ⟨kw "that", _, rfl, by simp [openers, kws, kw],
        fun w hw => by simp [kw] at hw; subst hw; simp [startsTerm]⟩
    | first s =>
      exact ⟨kw "the", _, rfl, by simp [openers, kws, kw],
        fun w hw => by simp [kw] at hw; subst hw; simp [startsTerm]⟩
    | second s =>
      exact ⟨kw "the", _, rfl, by simp [openers, kws, kw],
        fun w hw => by simp [kw] at hw; subst hw; simp [startsTerm]⟩
    | named s k =>
      exact ⟨.label (L.letter s) k, [], rfl, by simp [openers, kws],
        fun w hw => by simp [kw] at hw⟩

theorem term_prefix_free {t t' : TermTree} (h : t.ok L = true) (h' : t'.ok L = true)
    (hp : t.yield L <+: t'.yield L) : t = t' := by
  cases t with
  | const c =>
    simp only [TermTree.ok, List.contains_iff_mem] at h
    obtain ⟨x, rest, hx, -, hthat, hthe⟩ := F.const_opens c h
    cases t' with
    | const c' =>
      simp only [TermTree.ok, List.contains_iff_mem] at h'
      rw [F.const_prefix_free c h c' h' hp]
    | ref r =>
      simp only [TermTree.yield, hx, kws_cons] at hp
      cases r <;> simp [Ref.refYield, List.cons_prefix_cons, kw, hthat, hthe] at hp
  | ref r =>
    simp only [TermTree.ok, List.contains_iff_mem] at h
    cases t' with
    | const c' =>
      simp only [TermTree.ok, List.contains_iff_mem] at h'
      obtain ⟨x, rest, hx, -, hthat, hthe⟩ := F.const_opens c' h'
      simp only [TermTree.yield, hx, kws_cons] at hp
      cases r <;> simp [Ref.refYield, List.cons_prefix_cons, kw, Ne.symm hthat, Ne.symm hthe] at hp
    | ref r' =>
      simp only [TermTree.ok, List.contains_iff_mem] at h'
      cases r <;> cases r' <;>
        simp only [TermTree.yield, Ref.refYield, List.cons_prefix_cons, kw_eq_kw, Ref.sort,
          true_and, List.nil_prefix, and_true, TermTree.ref.injEq, Ref.plain.injEq,
          Ref.first.injEq, Ref.second.injEq, Ref.named.injEq, Tok.label.injEq] at hp h h' ⊢
      all_goals first
        | exact F.noun_prefix_free _ h _ h' hp
        | exact ⟨F.letter_inj _ h _ h' hp.1, hp.2⟩
        | (simp [kw] at hp)

end

/-! ## Templates -/

theorem mem_templateWords {w : String} {T : Template} : w ∈ templateWords T ↔ Slot.word w ∈ T := by
  simp only [templateWords, List.mem_filterMap]
  constructor
  · rintro ⟨s, hs, he⟩
    cases s with
    | word w' => simp at he; subst he; exact hs
    | hole _ => simp at he
  · intro h; exact ⟨_, h, rfl⟩

theorem mem_templateHoles {i : Nat} {T : Template} : i ∈ templateHoles T ↔ Slot.hole i ∈ T := by
  simp only [templateHoles, List.mem_filterMap]
  constructor
  · rintro ⟨s, hs, he⟩
    cases s with
    | hole i' => simp at he; subst he; exact hs
    | word _ => simp at he
  · intro h; exact ⟨_, h, rfl⟩

theorem fill_word (w : String) (T : Template) (ys : List (List Tok)) :
    fill (Slot.word w :: T) ys = kw w :: fill T ys := by simp [fill, kw]

theorem fill_hole {L : Lexicon} {xs : List TermTree} {i : Nat} (hi : i < xs.length) (T : Template) :
    fill (Slot.hole i :: T) (xs.map (TermTree.yield L)) = xs[i].yield L ++ fill T (xs.map (TermTree.yield L)) := by
  simp [fill, List.getD_eq_getElem?_getD, hi]

theorem mem_fill {L : Lexicon} {T : Template} {args : List TermTree} {x : Tok}
    (h : x ∈ fill T (args.map (TermTree.yield L))) :
    (∃ w ∈ templateWords T, x = kw w) ∨ ∃ t ∈ args, x ∈ t.yield L := by
  simp only [fill, List.mem_flatMap] at h
  obtain ⟨s, hs, hx⟩ := h
  cases s with
  | word w =>
    simp only [List.mem_singleton] at hx
    exact Or.inl ⟨w, mem_templateWords.mpr hs, hx⟩
  | hole i =>
    dsimp only at hx
    rw [List.getD_eq_getElem?_getD, List.getElem?_map] at hx
    cases hi : args[i]? with
    | none => simp [hi] at hx
    | some t =>
      simp only [hi, Option.map_some, Option.getD_some] at hx
      exact Or.inr ⟨t, List.mem_of_getElem? hi, hx⟩

section
variable {L : Lexicon} (F : Facts L)
include F

theorem disj_sound {xs ys : List TermTree} (hx : ∀ t ∈ xs, t.ok L = true)
    (hy : ∀ t ∈ ys, t.ok L = true) : ∀ (T1 T2 : Template),
    (∀ i, Slot.hole i ∈ T1 → i < xs.length) → (∀ i, Slot.hole i ∈ T2 → i < ys.length) →
    disj L T1 T2 = true → fill T1 (xs.map (TermTree.yield L)) ≠ fill T2 (ys.map (TermTree.yield L)) := by
  intro T1
  induction T1 with
  | nil =>
    intro T2 _ h2 hd he
    cases T2 with
    | nil => simp [disj] at hd
    | cons s T2 =>
      cases s with
      | word w => simp [fill] at he
      | hole j =>
        have hj := h2 j (by simp)
        obtain ⟨x, r, hr, -⟩ := term_opens F (hy _ (List.getElem_mem hj))
        rw [fill_hole hj, hr] at he
        simp [fill] at he
  | cons s T1 ih =>
    intro T2 h1 h2 hd he
    have h1' : ∀ i, Slot.hole i ∈ T1 → i < xs.length := fun i hi => h1 i (by simp [hi])
    cases T2 with
    | nil =>
      cases s with
      | word w => simp [fill] at he
      | hole i =>
        have hi := h1 i (by simp)
        obtain ⟨x, r, hr, -⟩ := term_opens F (hx _ (List.getElem_mem hi))
        rw [fill_hole hi, hr] at he
        simp [fill] at he
    | cons s' T2 =>
      have h2'' : ∀ i, Slot.hole i ∈ T2 → i < ys.length := fun i hi => h2 i (by simp [hi])
      cases s with
      | word a =>
        cases s' with
        | word b =>
          rw [fill_word, fill_word] at he
          simp only [List.cons.injEq, kw_eq_kw] at he
          obtain ⟨rfl, he⟩ := he
          simp only [disj, bne_self_eq_false, Bool.false_or] at hd
          exact ih T2 h1' h2'' hd he
        | hole j =>
          have hj := h2 j (by simp)
          obtain ⟨x, r, hr, -, hstart⟩ := term_opens F (hy _ (List.getElem_mem hj))
          rw [fill_word, fill_hole hj, hr] at he
          simp only [List.cons_append, List.cons.injEq] at he
          have := hstart a he.1.symm
          simp [disj, this] at hd
      | hole i =>
        have hi := h1 i (by simp)
        cases s' with
        | word b =>
          obtain ⟨x, r, hr, -, hstart⟩ := term_opens F (hx _ (List.getElem_mem hi))
          rw [fill_hole hi, fill_word, hr] at he
          simp only [List.cons_append, List.cons.injEq] at he
          have := hstart b he.1
          simp [disj, this] at hd
        | hole j =>
          have hj := h2 j (by simp)
          rw [fill_hole hi, fill_hole hj] at he
          have ht : xs[i] = ys[j] := by
            rcases List.prefix_or_prefix_of_prefix (List.prefix_append _ _) (he ▸ List.prefix_append _ _) with hp | hp
            · exact (term_prefix_free F (hy _ (List.getElem_mem hj)) (hx _ (List.getElem_mem hi)) hp).symm
            · exact term_prefix_free F (hx _ (List.getElem_mem hi)) (hy _ (List.getElem_mem hj)) hp
          rw [ht] at he
          simp only [disj] at hd
          exact ih T2 h1' h2'' hd (List.append_cancel_left he)

theorem fill_inj {xs ys : List TermTree} (hx : ∀ t ∈ xs, t.ok L = true)
    (hy : ∀ t ∈ ys, t.ok L = true) : ∀ (T : Template),
    (∀ i, Slot.hole i ∈ T → i < xs.length ∧ i < ys.length) →
    fill T (xs.map (TermTree.yield L)) = fill T (ys.map (TermTree.yield L)) →
    ∀ i (hi : i < xs.length) (hj : i < ys.length), Slot.hole i ∈ T → xs[i] = ys[i] := by
  intro T
  induction T with
  | nil => intro _ _ i _ _ h; simp at h
  | cons s T ih =>
    intro hb he i hi hj hm
    have hb' : ∀ i, Slot.hole i ∈ T → i < xs.length ∧ i < ys.length := fun i h => hb i (by simp [h])
    cases s with
    | word w =>
      rw [fill_word, fill_word] at he
      have he := (List.cons.inj he).2
      rcases List.mem_cons.mp hm with h | h
      · cases h
      · exact ih hb' he i hi hj h
    | hole k =>
      obtain ⟨hk1, hk2⟩ := hb k (by simp)
      rw [fill_hole hk1, fill_hole hk2] at he
      have ht : xs[k] = ys[k] := by
        rcases List.prefix_or_prefix_of_prefix (List.prefix_append _ _) (he ▸ List.prefix_append _ _) with hp | hp
        · exact (term_prefix_free F (hy _ (List.getElem_mem hk2)) (hx _ (List.getElem_mem hk1)) hp).symm
        · exact term_prefix_free F (hx _ (List.getElem_mem hk1)) (hy _ (List.getElem_mem hk2)) hp
      rw [ht] at he
      rcases List.mem_cons.mp hm with h | h
      · cases h; exact ht
      · exact ih hb' (List.append_cancel_left he) i hi hj h

end

/-! ## Clauses -/

def Lit.key : Lit → AtomKey
  | .truth => .truth
  | .falsity => .falsity
  | .eq _ _ => .eq
  | .pred p _ => .pred p

def Lit.args : Lit → List TermTree
  | .truth | .falsity => []
  | .eq a b => [a, b]
  | .pred _ args => args

theorem Lit.ext_key {a b : Lit} (hk : a.key = b.key) (ha : a.args = b.args) : a = b := by
  cases a <;> cases b <;> simp_all [Lit.key, Lit.args]

theorem keyTemplates_unique {L : Lexicon} {k : AtomKey} {T T' : Template}
    (h : (k, T) ∈ keyTemplates L) (h' : (k, T') ∈ keyTemplates L) : T = T' := by
  simp only [keyTemplates, List.mem_append, List.mem_cons, Prod.mk.injEq, List.not_mem_nil,
    or_false, List.mem_filterMap, Option.map_eq_some_iff] at h h'
  rcases h with (⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩) | ⟨p, -, U, hU, rfl, rfl⟩ <;>
  rcases h' with (⟨h1, rfl⟩ | ⟨h1, rfl⟩ | ⟨h1, rfl⟩) | ⟨q, -, U', hU', h1, rfl⟩ <;>
  first
    | rfl
    | (simp only [AtomKey.pred.injEq] at h1; subst h1; rw [hU] at hU'; cases hU'; rfl)
    | (cases h1)

theorem keyTemplate_shape {L : Lexicon} (F : Facts L) {k : AtomKey} {T : Template}
    (h : (k, T) ∈ keyTemplates L) :
    (∀ w ∈ templateWords T, w ∉ atomStopWords) ∧ (∀ i ∈ templateHoles T, i < T.arity) ∧
    ∃ s T', T = s :: T' ∧ ∀ w, s = .word w → w ∉ openerWords := by
  simp only [keyTemplates, List.mem_append, List.mem_cons, Prod.mk.injEq, List.not_mem_nil,
    or_false, List.mem_filterMap, Option.map_eq_some_iff] at h
  rcases h with (⟨-, rfl⟩ | ⟨-, rfl⟩ | ⟨-, rfl⟩) | ⟨p, hp, U, hU, -, rfl⟩
  · exact ⟨by decide, by decide, _, _, rfl, fun w h => by cases h; decide⟩
  · exact ⟨by decide, by decide, _, _, rfl, fun w h => by cases h; decide⟩
  · exact ⟨by decide, by decide, _, _, rfl, fun w h => by cases h⟩
  · obtain ⟨T, hT, hok⟩ := F.templates p hp
    rw [hT] at hU; cases hU
    simp only [templateOk, Bool.and_eq_true, List.all_eq_true, Bool.not_eq_true',
      decide_eq_true_eq] at hok
    obtain ⟨⟨hw, hh⟩, hs⟩ := hok
    refine ⟨fun w hm => by simpa using hw w hm, hh, ?_⟩
    cases U with
    | nil => simp at hs
    | cons s T' =>
      refine ⟨s, T', rfl, fun w hsw => ?_⟩
      subst hsw
      simpa using hs

theorem lit_template {L : Lexicon} (F : Facts L) (a : Lit) (hok : a.ok L = true) :
    ∃ T, (a.key, T) ∈ keyTemplates L ∧ a.yield L = fill T (a.args.map (TermTree.yield L)) ∧
      a.args.length = T.arity ∧ (∀ i, Slot.hole i ∈ T → i < a.args.length) ∧
      (∀ i < a.args.length, Slot.hole i ∈ T) ∧ ∀ t ∈ a.args, t.ok L = true := by
  cases a with
  | truth =>
    refine ⟨truthT, by simp [keyTemplates, Lit.key], by simp [Lit.yield, fill, truthT, kws, Lit.args],
      by decide, ?_, by simp [Lit.args], by simp [Lit.args]⟩
    intro i h; simp [truthT] at h
  | falsity =>
    refine ⟨falsityT, by simp [keyTemplates, Lit.key], by simp [Lit.yield, fill, falsityT, kws, Lit.args],
      by decide, ?_, by simp [Lit.args], by simp [Lit.args]⟩
    intro i h; simp [falsityT] at h
  | eq x y =>
    simp only [Lit.ok, Bool.and_eq_true] at hok
    refine ⟨eqT, by simp [keyTemplates, Lit.key], ?_, rfl, ?_, ?_, ?_⟩
    · simp [Lit.yield, fill, eqT, kws, Lit.args]
    · intro i h; simp [eqT] at h; simp [Lit.args]; omega
    · intro i h; simp [Lit.args] at h
      have : i = 0 ∨ i = 1 := by omega
      rcases this with rfl | rfl <;> simp [eqT]
    · intro t ht; simp [Lit.args] at ht; rcases ht with rfl | rfl
      · exact hok.1
      · exact hok.2
  | pred p args =>
    simp only [Lit.ok, Bool.and_eq_true, List.contains_iff_mem, List.all_eq_true] at hok
    obtain ⟨⟨hp, hargs⟩, hT⟩ := hok
    cases hTp : L.template p with
    | none => simp [hTp] at hT
    | some T =>
      simp only [hTp, Bool.and_eq_true, beq_iff_eq, List.all_eq_true, List.mem_range,
        List.contains_iff_mem] at hT
      obtain ⟨hlen, hholes⟩ := hT
      have hmem : (AtomKey.pred p, T) ∈ keyTemplates L := by
        simp only [keyTemplates, List.mem_append, List.mem_filterMap, Option.map_eq_some_iff]
        exact Or.inr ⟨p, hp, T, hTp, rfl⟩
      obtain ⟨-, hlt, -⟩ := keyTemplate_shape F hmem
      refine ⟨T, hmem, by simp [Lit.yield, hTp, Lit.args], hlen, ?_, hholes, hargs⟩
      intro i hi
      simp only [Lit.args]
      rw [hlen]
      exact hlt i (mem_templateHoles.mpr hi)

/-! ## Soundness of the check -/

theorem admitted_of_facts {L : Lexicon} (F : Facts L) : Admitted L where
  atom_unique := by
    intro a b ha hb hy
    obtain ⟨T1, hk1, hy1, hl1, hb1, hc1, ht1⟩ := lit_template F a ha
    obtain ⟨T2, hk2, hy2, hl2, hb2, hc2, ht2⟩ := lit_template F b hb
    by_cases hk : a.key = b.key
    · rw [hk] at hk1
      obtain rfl := keyTemplates_unique hk1 hk2
      have hlen : a.args.length = b.args.length := by omega
      have hargs : a.args = b.args := by
        refine List.ext_getElem hlen fun i hi hj => ?_
        refine fill_inj F ht1 ht2 T1 (fun i h => ⟨hb1 i h, hb2 i h⟩) (hy1 ▸ hy2 ▸ hy) i hi hj (hc1 i hi)
      exact Lit.ext_key hk hargs
    · exact absurd (hy1 ▸ hy2 ▸ hy) (disj_sound F ht1 ht2 T1 T2 hb1 hb2 (F.disjoint _ hk1 _ hk2 hk))
  atom_delimited := by
    intro a ha x hx hs
    obtain ⟨T, hk, hy, -, -, -, ht⟩ := lit_template F a ha
    rw [hy] at hx
    rcases mem_fill hx with ⟨w, hw, rfl⟩ | ⟨t, htm, hxt⟩
    · exact (keyTemplate_shape F hk).1 w hw (kw_mem_kws.mp hs)
    · exact term_tokens F (ht t htm) x hxt hs
  atom_opens := by
    intro a ha
    obtain ⟨T, hk, hy, hl, hb, -, ht⟩ := lit_template F a ha
    obtain ⟨-, -, s, T', rfl, hs⟩ := keyTemplate_shape F hk
    rw [hy]
    cases s with
    | word w =>
      refine ⟨kw w, _, fill_word w T' _, fun hm => hs w rfl ?_⟩
      exact kw_mem_kws.mp hm
    | hole i =>
      have hi := hb i (by simp)
      obtain ⟨x, r, hr, ho, -⟩ := term_opens F (ht _ (List.getElem_mem hi))
      exact ⟨x, r ++ fill T' (a.args.map (TermTree.yield L)), by rw [fill_hole hi, hr]; rfl, ho⟩
  noun_prefix_free := F.noun_prefix_free
  noun_opens := F.noun_opens

/-- A vocabulary passing the finite check satisfies the lexical conditions of
the core theorems. -/
theorem admissible_sound {L : Lexicon} (h : admissible L = true) : Admitted L :=
  admitted_of_facts (facts_of_admissible h)

end VE.English
