import VE.Acts.NormalBlocks

/-! The uniqueness half of `read_normal` (docs/spec/act-phrases.md 5.6), and `read_normal` itself.

Proofs only. Every derivation of `a.normal` from the start symbol has the pieces `[.act (.one a.canon)]`, for a
`normalOk` atom `a` under a `framesOk` vocabulary (`normal_pieces`); so every derivation that has a meaning means
`.one a.canon` (`normal_unique`). With `normal_derived` and `parse_bounds` (`VE.Acts.NormalProofs`) that is
`read_normal`.
-/

namespace VE.Acts.NormalProofs

set_option linter.unusedSimpArgs false
open VE.Acts
open VE.Grammar (Tree Sym derivesAll yieldAll)
open VE.Acts.Lexical (Tok)

variable {V : Vocab} {f : Frame}


theorem fw_pieces {t b : Bool} {u : List Tok} {ps : List Piece} (hg : Gen V (.n .FW) u ps) (he : u = fwToks t b) :
    ps = [.fw t b] ∧ (t || b) = true := by
  obtain ⟨vs, rfl, hvs, rfl⟩ := fw_inv hg
  have h1 : ∀ ws : List String, vs.map Tok.word = ws.map Tok.word → vs = ws := fun ws h => map_word_inj h
  cases t <;> cases b <;> simp only [fwToks, if_true, if_false, Bool.false_eq_true, List.nil_append, List.append_nil,
    List.singleton_append] at he
  · rcases hvs with h | h | h <;> (have := congrArg List.length h; simp_all)
  · obtain rfl := h1 ["be"] he; simp [lower_be]
  · obtain rfl := h1 ["to"] he; simp [lower_to]
  · obtain rfl := h1 ["to", "be"] he; simp [lower_to, lower_be]

theorem adv_head_fw {t b : Bool} {X : List Tok} (hW : VocabOk V) (h : ∀ x ∈ (fwToks t b ++ X).head?, ADV V x) :
    t = false ∧ b = false := by
  cases t <;> cases b
  · exact ⟨rfl, rfl⟩
  · exact (tb_not_adv hW ⟨"be", rfl, .inr lower_be⟩ (h (.word "be") (by simp [fwToks]))).elim
  · exact (tb_not_adv hW ⟨"to", rfl, .inl lower_to⟩ (h (.word "to") (by simp [fwToks]))).elim
  · exact (tb_not_adv hW ⟨"to", rfl, .inl lower_to⟩ (h (.word "to") (by simp [fwToks]))).elim

theorem nta_head_fw {t b : Bool} {ws : List String} (hws : ∀ w ∈ ws, w ∈ V.adverbs ∧ w.toLower = w) {X : List Tok}
    (h : ∀ x ∈ (fwToks t b ++ ws.map Tok.word ++ X).head?, NTA V x) : t = false ∧ b = false ∧ ws = [] := by
  cases t <;> cases b
  · cases ws with
    | nil => exact ⟨rfl, rfl, rfl⟩
    | cons w ws => exact ((h (.word w) (by simp [fwToks])).2 (ws_adv hws _ (by simp))).elim
  · exact ((h (.word "be") (by simp [fwToks])).1 ⟨"be", rfl, .inr lower_be⟩).elim
  · exact ((h (.word "to") (by simp [fwToks])).1 ⟨"to", rfl, .inl lower_to⟩).elim
  · exact ((h (.word "to") (by simp [fwToks])).1 ⟨"to", rfl, .inl lower_to⟩).elim

/-- The normal form after the adverbs: the head, the object, the elements. -/
def coreToks (f : Frame) (ob : Option Filler) (bs : List Blk) : List Tok := f.head.map .word ++ (objToks ob ++ blocks bs)

theorem coreToks_head (hW : VocabOk V) (hfr : f ∈ V.frames) (hl : ∀ w ∈ f.head, w.toLower = w) (hne : f.head ≠ [])
    (ob : Option Filler) (bs : List Blk) : ∀ x ∈ (coreToks f ob bs).head?, NTA V x := by
  obtain ⟨w0, ws0, hw0⟩ := List.exists_cons_of_ne_nil hne
  intro x hx; simp [coreToks, hw0] at hx; subst hx
  exact head_word hW hfr (by rw [hw0, hl w0 (by simp [hw0])]; rfl)

theorem ap_SINGLE_rhs (cs : List Piece) (rhs : List RSym) (hr : rhs = [.n .SC] ∨ rhs = [.n .ADVSO, .n .SC] ∨
    rhs = [.n .FW, .n .SC] ∨ rhs = [.n .FW, .n .ADVSO, .n .SC]) :
    applyRule ⟨.SINGLE, rhs, .shape⟩ cs = (itemOf cs).map (fun (fw, h, es) => [.act (singleAct fw h es)]) := by
  rcases hr with rfl | rfl | rfl | rfl
  · exact ap_SINGLE cs [.SC] (by simp)
  · exact ap_SINGLE cs [.ADVSO, .SC] (by simp)
  · exact ap_SINGLE cs [.FW, .SC] (by simp)
  · exact ap_SINGLE cs [.FW, .ADVSO, .SC] (by simp)

theorem hrest (hW : VocabOk V) {ws : List String} {R : List Tok} (hadv : ∀ x ∈ ws.map Tok.word, ADV V x)
    (hR : ∀ x ∈ R.head?, NTA V x) : ∀ x ∈ (ws.map Tok.word ++ R).head?, ¬ TB x := by
  cases ws with
  | nil => simpa using (fun x hx => (hR x hx).1)
  | cons w ws => intro x hx; simp at hx; subst hx; exact fun ht => tb_not_adv hW ht (hadv _ (by simp))

theorem core_not_tb {R u : List Tok} (hR : ∀ x ∈ R.head?, NTA V x) (he : u = R) (hu : ∀ x ∈ u.head?, TB x)
    (hne : u ≠ []) : False := by
  subst he
  obtain ⟨x, u', rfl⟩ := List.exists_cons_of_ne_nil hne
  exact (hR x (by simp)).1 (hu x (by simp))

/-- The item (`SINGLE`) where the normal form has function words, adverbs, frame `f`'s head, the object and the
elements: the function-word piece, the adverbs and `SC`'s pieces, in order. -/
theorem single_inv (hV : framesOk V = true) (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h)
    (hl : ∀ w ∈ f.head, w.toLower = w) (hne : f.head ≠ []) {ob : Option Filler} (hob : ObjOk V f ob) {bs : List Blk}
    (hbs : ∀ b ∈ bs, BlkOk V f b) (t b : Bool) (ws : List String) (hws : ∀ w ∈ ws, w ∈ V.adverbs ∧ w.toLower = w)
    {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n .SINGLE) u ps)
    (he : u = fwToks t b ++ ws.map .word ++ coreToks f ob bs) :
    (itemOf ((if t || b then [Piece.fw t b] else []) ++ ws.map (fun w => .elt (.mod (.adv w)) .own) ++
      (Piece.head f.head :: (objPieces ob ++ bs.map Blk.piece)))).map
        (fun (fw, h, es) => [Piece.act (singleAct fw h es)]) = some ps := by
  have hRh := coreToks_head hW hF.frame hl hne ob bs
  have hadv : ∀ x ∈ ws.map Tok.word, ADV V x := ws_adv hws
  have hwsp : ws.map (fun w => Piece.elt (.mod (.adv w)) .own) = ws.map (fun v => .elt (.mod (.adv v.toLower)) .own) :=
    List.map_congr_left (fun w hw => by rw [(hws w hw).2])
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  subst he
  rules_of hr fr hfr
  · -- SC
    have h1 := genAll1 hg
    obtain ⟨rfl, rfl, rfl⟩ := nta_head_fw hws (sc_head hV hW h1)
    rw [ap_SINGLE_rhs cs _ (by simp)] at ha
    rw [← ha, sc_inv hV hW hF hl hob hbs h1 (by simp [fwToks, coreToks])]
    rfl
  · -- ADVSO SC
    obtain ⟨w1, w2, c1, c2, he, rfl, h1, h2⟩ := genAll2 hg
    obtain ⟨vs, hvne, rfl, hvs, rfl⟩ := advso_inv _ (Nat.le_refl _) h1
    obtain ⟨rfl, rfl⟩ := adv_head_fw (X := ws.map Tok.word ++ coreToks f ob bs) hW (by
      rw [List.append_assoc] at he; rw [he]
      exact head_append (head_all (advso_adv h1)) (by simpa using hvne))
    simp only [fwToks, if_false, Bool.false_eq_true, List.nil_append] at he
    obtain ⟨e1, rfl⟩ := split_class (ADV V) he.symm (advso_adv h1) hadv
      (fun x hx => (sc_head hV hW h2 x hx).2) (fun x hx => (hRh x hx).2)
    obtain rfl := map_word_inj e1
    rw [ap_SINGLE_rhs _ _ (by simp)] at ha
    rw [← ha, sc_inv hV hW hF hl hob hbs h2 rfl, hwsp]
    rfl
  · -- FW SC
    obtain ⟨w1, w2, c1, c2, he, rfl, h1, h2⟩ := genAll2 hg
    rw [List.append_assoc] at he
    obtain ⟨rfl, rfl⟩ := split_class TB he.symm (fw_tb h1) (fwToks_tb t b)
      (fun x hx => (sc_head hV hW h2 x hx).1) (hrest hW hadv hRh)
    obtain ⟨-, -, rfl⟩ := nta_head_fw (t := false) (b := false) hws (X := coreToks f ob bs)
      (by simpa [fwToks] using sc_head hV hW h2)
    obtain ⟨rfl, htb⟩ := fw_pieces h1 rfl
    rw [ap_SINGLE_rhs _ _ (by simp)] at ha
    rw [← ha, sc_inv hV hW hF hl hob hbs h2 (by simp [coreToks]), htb]
    rfl
  · -- ADVSO FW SC
    obtain ⟨w1, w2, w3, c1, c2, c3, he, -, h1, h2, h3⟩ := genAll3 hg
    have hw1 := gen_ne hV h1
    obtain ⟨rfl, rfl⟩ := adv_head_fw (X := ws.map Tok.word ++ coreToks f ob bs) hW (by
      rw [← List.append_assoc, he, List.append_assoc]
      exact head_append (head_all (advso_adv h1)) hw1)
    simp only [fwToks, if_false, Bool.false_eq_true, List.nil_append, List.append_assoc] at he
    obtain ⟨-, e2⟩ := split_class (ADV V) he.symm (advso_adv h1) hadv
      (head_append (fun x hx => tb_not_adv hW (head_all (fw_tb h2) x hx)) (gen_ne hV h2)) (fun x hx => (hRh x hx).2)
    exact (core_not_tb hRh e2 (head_append (head_all (fw_tb h2)) (gen_ne hV h2)) (by simp [gen_ne hV h2])).elim
  · -- FW ADVSO SC
    obtain ⟨w1, w2, w3, c1, c2, c3, he, rfl, h1, h2, h3⟩ := genAll3 hg
    rw [List.append_assoc, List.append_assoc] at he
    obtain ⟨rfl, e2⟩ := split_class TB he.symm (fw_tb h1) (fwToks_tb t b)
      (head_append (fun x hx ht => tb_not_adv hW ht (head_all (advso_adv h2) x hx)) (gen_ne hV h2))
      (hrest hW hadv hRh)
    obtain ⟨vs, hvne, rfl, hvs, rfl⟩ := advso_inv _ (Nat.le_refl _) h2
    obtain ⟨e3, rfl⟩ := split_class (ADV V) e2 (advso_adv h2) hadv
      (fun x hx => (sc_head hV hW h3 x hx).2) (fun x hx => (hRh x hx).2)
    obtain rfl := map_word_inj e3
    obtain ⟨rfl, htb⟩ := fw_pieces h1 rfl
    rw [ap_SINGLE_rhs _ _ (by simp)] at ha
    rw [← ha, sc_inv hV hW hF hl hob hbs h3 rfl, htb, hwsp]
    rfl
  · -- ADVSO FW ADVSO SC
    obtain ⟨w1, w2, w3, w4, c1, c2, c3, c4, he, -, h1, h2, h3, h4⟩ := genAll4 hg
    have hw1 := gen_ne hV h1
    obtain ⟨rfl, rfl⟩ := adv_head_fw (X := ws.map Tok.word ++ coreToks f ob bs) hW (by
      rw [← List.append_assoc, he, List.append_assoc, List.append_assoc]
      exact head_append (head_all (advso_adv h1)) hw1)
    simp only [fwToks, if_false, Bool.false_eq_true, List.nil_append, List.append_assoc] at he
    obtain ⟨-, e2⟩ := split_class (ADV V) he.symm (advso_adv h1) hadv
      (head_append (fun x hx => tb_not_adv hW (head_all (fw_tb h2) x hx)) (gen_ne hV h2)) (fun x hx => (hRh x hx).2)
    exact (core_not_tb hRh e2 (head_append (head_all (fw_tb h2)) (gen_ne hV h2)) (by simp [gen_ne hV h2])).elim


/-! ### No coordination: in a normal form, a comma or join word is followed by a part -/

/-- Every comma or join word of the list is followed by a token outside `fillExcl V f` (a part's first token). -/
def Adj (V : Vocab) (f : Frame) : List Tok → Prop
  | x :: y :: rest => (JC x → ¬ ExclW V f y) ∧ Adj V f (y :: rest)
  | _ => True

/-- The list does not end with a comma or join word. -/
def EndOk (l : List Tok) : Prop := ∀ x ∈ l.getLast?, ¬ JC x

theorem adj_cons {x : Tok} {l : List Tok} (h1 : ∀ y ∈ l.head?, JC x → ¬ ExclW V f y) (h2 : Adj V f l) :
    Adj V f (x :: l) := by
  cases l with
  | nil => trivial
  | cons y l => exact ⟨h1 y (by simp), h2⟩

theorem adj_drop {x : Tok} {l : List Tok} (h : Adj V f (x :: l)) : Adj V f l := by
  cases l with
  | nil => trivial
  | cons y l => exact h.2

theorem adj_append : ∀ {A B : List Tok}, Adj V f A → Adj V f B → EndOk A → Adj V f (A ++ B)
  | [], _, _, hB, _ => hB
  | [x], _, _, hB, hl => adj_cons (fun _ _ hx => (hl x (by simp) hx).elim) hB
  | x :: y :: A, B, hA, hB, hl => ⟨hA.1, adj_append (A := y :: A) hA.2 hB (by
      intro z hz; exact hl z (by simpa [List.getLast?_cons_cons] using hz))⟩

theorem adj_suffix : ∀ {A B : List Tok}, Adj V f (A ++ B) → Adj V f B
  | [], _, h => h
  | _ :: A, _, h => adj_suffix (A := A) (adj_drop h)

theorem adj_nojc : ∀ {l : List Tok}, (∀ x ∈ l, ¬ JC x) → Adj V f l
  | [], _ => trivial
  | [_], _ => trivial
  | x :: y :: l, h => ⟨fun hx => (h x (by simp) hx).elim, adj_nojc (fun z hz => h z (List.mem_cons_of_mem _ hz))⟩

theorem endOk_nojc {l : List Tok} (h : ∀ x ∈ l, ¬ JC x) : EndOk l := fun x hx => h x (List.mem_of_getLast? hx)

theorem endOk_append {A B : List Tok} (hB : EndOk B) (hne : B ≠ []) : EndOk (A ++ B) := by
  intro x hx
  rw [List.getLast?_append] at hx
  cases hb : B.getLast? with
  | none => exact absurd (List.getLast?_eq_none_iff.mp hb) hne
  | some y => rw [hb] at hx; simp at hx; subst hx; exact hB y hb

theorem adj_tailToks (j : Join) : ∀ rest : List Part, (∀ q ∈ rest, PartOk V f q) →
    Adj V f (tailToks j rest) ∧ EndOk (tailToks j rest)
  | [], _ => ⟨trivial, fun x hx => by simp [tailToks] at hx⟩
  | [q], hok => by
    have hq := hok q (by simp)
    obtain ⟨y, r, hy, hny⟩ := part_head_not_excl hq
    refine ⟨adj_cons (fun z hz _ => by rw [hy] at hz; simp at hz; subst hz; exact hny) (adj_nojc (part_not_jc hq)), ?_⟩
    simp only [tailToks]
    exact endOk_append (A := [_]) (endOk_nojc (part_not_jc hq)) (part_ne hq)
  | q :: q' :: rest, hok => by
    have hq := hok q (by simp)
    obtain ⟨ih1, ih2⟩ := adj_tailToks j (q' :: rest) (fun x hx => hok x (List.mem_cons_of_mem _ hx))
    obtain ⟨y, r, hy, hny⟩ := part_head_not_excl hq
    rw [tailToks_cons2]
    refine ⟨adj_cons (fun z hz _ => by rw [hy] at hz; simp at hz; subst hz; exact hny)
      (adj_append (adj_nojc (part_not_jc hq)) ih1 (endOk_nojc (part_not_jc hq))), ?_⟩
    obtain ⟨t, u, ht, -⟩ := tailToks_head j q' rest
    exact endOk_append (A := [Tok.comma] ++ q.toks) ih2 (by rw [ht]; simp)

theorem adj_filler {fl : Filler} (hok : ∀ p ∈ fl.parts, PartOk V f p)
    (hj : ∀ j ps, fl = .joined j ps → 2 ≤ ps.length) : Adj V f fl.toks ∧ EndOk fl.toks ∧ fl.toks ≠ [] := by
  cases fl with
  | one p =>
    have hp := hok p (by simp [Filler.parts])
    exact ⟨adj_nojc (part_not_jc hp), endOk_nojc (part_not_jc hp), part_ne hp⟩
  | joined j qs =>
    obtain ⟨p, q, rest, rfl⟩ := two_parts (hj j qs rfl)
    have hp := hok p (by simp [Filler.parts])
    obtain ⟨a1, a2⟩ := adj_tailToks j (q :: rest) (fun x hx => hok x (List.mem_cons_of_mem _ hx))
    obtain ⟨t, u, ht, -⟩ := tailToks_head j q rest
    simp only [Filler.toks, listToks_eq]
    exact ⟨adj_append (adj_nojc (part_not_jc hp)) a1 (endOk_nojc (part_not_jc hp)),
      endOk_append a2 (by rw [ht]; simp), by simp [part_ne hp]⟩

theorem mk_nojc (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {m : String} (hm : m ∈ f.markers ++ f.mods) :
    ∀ x ∈ (wordsOf m).map Tok.word, ¬ JC x := by
  intro x hx hj
  obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hx
  have hne : m ≠ "" := by rintro rfl; simp [wordsOf_empty] at hw
  have := hW.mkRes f hF.frame m hm hne w hw
  rcases hj with he | ⟨v, he, hv⟩
  · cases he
  · cases he; rw [hF.lower m hm hne _ hw] at hv; rcases hv with hv | hv | hv <;> simp_all

theorem adj_blocks (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) : ∀ {bs : List Blk}, (∀ b ∈ bs, BlkOk V f b) →
    Adj V f (blocks bs) ∧ EndOk (blocks bs)
  | [], _ => ⟨trivial, fun x hx => by simp [blocks] at hx⟩
  | b :: bs, hbs => by
    obtain ⟨i1, i2⟩ := adj_blocks hW hF (fun x hx => hbs x (List.mem_cons_of_mem _ hx))
    have hb := hbs b (by simp)
    obtain ⟨hm, -⟩ := blkOk_marker hb hF
    have hr : Adj V f b.rest ∧ EndOk b.rest ∧ b.rest ≠ [] := by
      cases b with
      | arg m fl => exact adj_filler hb.2.2.1 (fun j ps he => (hb.2.2.2 j ps he).2.1)
      | prep m p => exact ⟨adj_nojc (part_not_jc hb.2), endOk_nojc (part_not_jc hb.2), part_ne hb.2⟩
    obtain ⟨r1, r2, r3⟩ := hr
    have hbt : Adj V f b.toks ∧ EndOk b.toks := ⟨adj_append (adj_nojc (mk_nojc hW hF hm)) r1
      (endOk_nojc (mk_nojc hW hF hm)), endOk_append r2 r3⟩
    rw [blocks_append_cons]
    refine ⟨adj_append hbt.1 i1 hbt.2, ?_⟩
    cases bs with
    | nil => simpa [blocks] using hbt.2
    | cons b' bs' => exact endOk_append i2 (by rw [blocks_append_cons]; simp [blk_ne hF (hbs b' (by simp))])


theorem head_firstP (hV : framesOk V = true) {P : Tok → Prop} {Y : RSym} {Ys : List RSym} {w : List Tok}
    {cs : List Piece} (hg : GenAll V (Y :: Ys) w cs) (hY : ∀ u c, Gen V Y u c → ∀ x ∈ u.head?, P x) :
    ∀ x ∈ w.head?, P x := by
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, -⟩ := genAll_inv_cons hg
  exact head_append (hY _ _ h1) (gen_ne hV h1)

theorem tb_excl {x : Tok} (h : TB x) : ExclW V f x := by
  obtain ⟨v, rfl, hv⟩ := h
  exact ⟨v, rfl, by rcases hv with hv | hv <;> simp [fillExcl, hv]⟩

theorem adv_excl {x : Tok} (h : ADV V x) : ExclW V f x := by
  obtain ⟨v, rfl, hv⟩ := h
  have : v.toLower ∈ V.adverbs := by simpa using hv
  exact ⟨v, rfl, by simp [fillExcl, this]⟩

theorem hd_excl (hV : framesOk V = true) {g : Frame} {h' : Nat} (hg' : (g, h') ∈ V.frames.zipIdx) {u : List Tok}
    {ps : List Piece} (hg0 : Gen V (.n (.F h' .HD)) u ps) : ∀ x ∈ u.head?, ExclW V f x := by
  have hgf := List.fst_mem_of_mem_zipIdx hg'
  obtain ⟨vs, rfl, hvs, -⟩ := hd_inv hg' (framesOk_words hV g hgf).1 hg0
  intro x hx
  cases vs with
  | nil => simp at hx
  | cons v vs =>
    simp at hx; subst hx
    refine ⟨v, rfl, ?_⟩
    simp only [fillExcl, List.contains_iff_mem, List.mem_append, List.mem_filterMap]
    exact .inr ⟨g, hgf, by rw [← hvs]; rfl⟩

theorem c_head (hV : framesOk V = true) {c : Core} {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.C c)) u ps) :
    ∀ x ∈ u.head?, ExclW V f x := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> exact head_firstP hV hg (fun _ _ h1 => hd_excl hV hfr h1)

theorem l_rules {own : Bool} {c : Core} {rhs : List RSym} {k : Kind} (hr : ⟨.L own c, rhs, k⟩ ∈ schema V) :
    ∃ Y rest, rhs = .n Y :: rest ∧ (Y = .FW ∨ Y = .ADVSO ∨ ∃ c', Y = .C c') := by
  rules_of hr fr hfr <;> exact ⟨_, _, rfl, by simp⟩

/-- The first token of a later item of a coordination (`L`): a function word, an adverb or a head's first word. -/
theorem l_head (hV : framesOk V = true) {own : Bool} {c : Core} {u : List Tok} {ps : List Piece}
    (hg0 : Gen V (.n (.L own c)) u ps) : ∀ x ∈ u.head?, ExclW V f x := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  obtain ⟨Y, rest, rfl, hY⟩ := l_rules hr
  rcases hY with rfl | rfl | ⟨c', rfl⟩
  · exact head_firstP hV hg (fun _ _ h1 => head_all (fun x hx => tb_excl (fw_tb h1 x hx)))
  · exact head_firstP hV hg (fun _ _ h1 => head_all (fun x hx => adv_excl (advso_adv h1 x hx)))
  · exact head_firstP hV hg (fun _ _ h1 => c_head hV h1)

theorem t_rules {own : Bool} {c : Core} {rhs : List RSym} {k : Kind} (hr : ⟨.T own c, rhs, k⟩ ∈ schema V) :
    (∃ o c', rhs = [.n .J, .n (.L o c')]) ∨ (∃ o c', rhs = [.t .comma, .n .J, .n (.L o c')]) ∨
      (∃ o c' c'', rhs = [.t .comma, .n (.L o c'), .n (.T o c'')]) := by
  rules_of hr fr hfr <;>
    first | exact .inl ⟨_, _, rfl⟩ | exact .inr (.inl ⟨_, _, rfl⟩) | exact .inr (.inr ⟨_, _, _, rfl⟩)

/-- A coordination's tail (`T`) begins with a comma or join word, then a token of `fillExcl V f`. -/
theorem t_head2 (hV : framesOk V = true) {own : Bool} {c : Core} {u : List Tok} {ps : List Piece}
    (hg0 : Gen V (.n (.T own c)) u ps) : ∃ x y u', u = x :: y :: u' ∧ JC x ∧ ExclW V f y := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rcases t_rules hr with ⟨o, c', rfl⟩ | ⟨o, c', rfl⟩ | ⟨o, c', c'', rfl⟩
  · obtain ⟨w1, w2, c1, c2, rfl, -, h1, h2⟩ := genAll2 hg
    obtain ⟨v, rfl, hv⟩ := j_inv h1
    obtain ⟨y, w2', rfl⟩ := List.exists_cons_of_ne_nil (gen_ne hV h2)
    exact ⟨_, y, w2', rfl, .inr ⟨v, rfl, hv⟩, l_head hV h2 y (by simp)⟩
  · obtain ⟨w1, w2, w3, c1, c2, c3, rfl, -, h1, h2, -⟩ := genAll3 hg
    obtain ⟨x, rfl, hx, -⟩ := gen_t_inv h1
    cases x <;> simp [Term.accepts] at hx
    obtain ⟨v, rfl, hv⟩ := j_inv h2
    exact ⟨_, _, w3, by simp, .inl rfl, ⟨v, rfl, jw_excl hv⟩⟩
  · obtain ⟨w1, w2, w3, c1, c2, c3, rfl, -, h1, h2, -⟩ := genAll3 hg
    obtain ⟨x, rfl, hx, -⟩ := gen_t_inv h1
    cases x <;> simp [Term.accepts] at hx
    obtain ⟨y, w2', rfl⟩ := List.exists_cons_of_ne_nil (gen_ne hV h2)
    exact ⟨_, y, w2' ++ w3, by simp, .inl rfl, l_head hV h2 y (by simp)⟩

theorem coord_rules {rhs : List RSym} {k : Kind} (hr : ⟨.COORD, rhs, k⟩ ∈ schema V) :
    ∃ o c c', rhs = [.n (.F1 o c), .n (.T o c')] := by
  rules_of hr fr hfr <;> exact ⟨_, _, _, rfl⟩

/-- No coordination (`COORD`) reads a list in which every comma or join word is followed by a part's first token. -/
theorem coord_false (hV : framesOk V = true) {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n .COORD) u ps)
    (hadj : Adj V f u) : False := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  obtain ⟨o, c, c', rfl⟩ := coord_rules hr
  obtain ⟨w1, w2, c1, c2, rfl, -, -, h2⟩ := genAll2 hg
  obtain ⟨x, y, u', rfl, hx, hy⟩ := t_head2 (f := f) hV h2
  exact (adj_suffix hadj).1 hx hy


/-! ### The start, and the theorems -/

theorem head_nojc (hW : VocabOk V) (hfr : f ∈ V.frames) (hl : ∀ w ∈ f.head, w.toLower = w) :
    ∀ x ∈ f.head.map Tok.word, ¬ JC x := by
  intro x hx hj
  obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hx
  have := hW.headRes f hfr w hw
  rcases hj with he | ⟨v, he, hv⟩
  · cases he
  · cases he; rw [hl _ hw] at hv; rcases hv with hv | hv | hv <;> simp_all

theorem adj_normal (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) (hl : ∀ w ∈ f.head, w.toLower = w)
    {ob : Option Filler} (hob : ObjOk V f ob) {bs : List Blk} (hbs : ∀ b ∈ bs, BlkOk V f b) (t b : Bool)
    (ws : List String) (hws : ∀ w ∈ ws, w ∈ V.adverbs ∧ w.toLower = w) :
    Adj V f (fwToks t b ++ ws.map .word ++ coreToks f ob bs) := by
  have hfw : ∀ x ∈ fwToks t b, ¬ JC x := by
    intro x hx hj
    obtain ⟨v, rfl, hv⟩ := fwToks_tb t b x hx
    rcases hj with he | ⟨v', he, hv'⟩
    · cases he
    · cases he; rcases hv with hv | hv <;> rcases hv' with hv' | hv' | hv' <;> simp_all
  have hwj : ∀ x ∈ ws.map Tok.word, ¬ JC x := by
    intro x hx hj
    obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hx
    have := hW.advRes w (hws w hw).1
    rcases hj with he | ⟨v', he, hv'⟩
    · cases he
    · cases he; rw [(hws _ hw).2] at hv'; rcases hv' with hv | hv | hv <;> simp_all
  have hpre : ∀ x ∈ fwToks t b ++ ws.map Tok.word ++ f.head.map Tok.word, ¬ JC x := by
    intro x hx
    simp only [List.mem_append] at hx
    rcases hx with (hx | hx) | hx
    · exact hfw x hx
    · exact hwj x hx
    · exact head_nojc hW hF.frame hl x hx
  have hob' : Adj V f (objToks ob) ∧ EndOk (objToks ob) := by
    cases ob with
    | none => exact ⟨trivial, fun x hx => by simp [objToks] at hx⟩
    | some fl =>
      obtain ⟨a1, a2, -⟩ := adj_filler hob.2.1 (fun j ps he => (hob.2.2 j ps he).2.1)
      exact ⟨a1, a2⟩
  obtain ⟨b1, -⟩ := adj_blocks hW hF hbs
  have := adj_append (adj_nojc hpre) (adj_append hob'.1 b1 hob'.2) (endOk_nojc hpre)
  simpa [coreToks, List.append_assoc] using this

/-- The start (`S`) where the normal form is `{0}`, function words, adverbs, the head, the object and the elements:
the item's pieces (no coordination can read it). -/
theorem s_inv (hV : framesOk V = true) (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h)
    (hl : ∀ w ∈ f.head, w.toLower = w) (hne : f.head ≠ []) {ob : Option Filler} (hob : ObjOk V f ob) {bs : List Blk}
    (hbs : ∀ b ∈ bs, BlkOk V f b) (t b : Bool) (ws : List String) (hws : ∀ w ∈ ws, w ∈ V.adverbs ∧ w.toLower = w)
    {ps : List Piece} (hg0 : Gen V (.n .S) (.slot 0 :: (fwToks t b ++ ws.map .word ++ coreToks f ob bs)) ps) :
    (itemOf ((if t || b then [Piece.fw t b] else []) ++ ws.map (fun w => .elt (.mod (.adv w)) .own) ++
      (Piece.head f.head :: (objPieces ob ++ bs.map Blk.piece)))).map
        (fun (fw, h, es) => [Piece.act (singleAct fw h es)]) = some ps := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr
  · obtain ⟨w1, w2, c1, c2, he, rfl, h1, h2⟩ := genAll2 hg
    obtain ⟨x, rfl, hx, hp⟩ := gen_t_inv h1
    simp only [List.singleton_append, List.cons.injEq] at he
    obtain ⟨rfl, rfl⟩ := he
    simp [piecesOf] at hp; subst hp
    rw [ap_S] at ha; cases ha
    exact single_inv hV hW hF hl hne hob hbs t b ws hws h2 rfl
  · obtain ⟨w1, w2, c1, c2, he, -, h1, h2⟩ := genAll2 hg
    obtain ⟨x, rfl, hx, hp⟩ := gen_t_inv h1
    simp only [List.singleton_append, List.cons.injEq] at he
    obtain ⟨rfl, rfl⟩ := he
    exact (coord_false hV h2 (adj_normal hW hF hl hob hbs t b ws hws)).elim

/-- (3) Every derivation of `a.normal` has the pieces of `.one a.canon`. -/
theorem normal_pieces (V : Vocab) (hV : framesOk V = true) (a : Atom) (ha : normalOk V a = true) {ps : List Piece}
    (hg : Gen V (.n .S) a.normal ps) : ps = [.act (.one a.canon)] := by
  have hW := vocabOk hV
  have hwds := framesOk_words hV
  obtain ⟨lh, lm, la, lmods⟩ := framesOk_lower hV
  unfold normalOk at ha
  split at ha
  · cases ha
  rename_i f hfind
  have hfr : f ∈ V.frames := List.mem_of_find?_eq_some hfind
  have hfh : f.head = a.head := by simpa using List.find?_some hfind
  obtain ⟨h, hh⟩ : ∃ h, (f, h) ∈ V.frames.zipIdx := by
    obtain ⟨i, hi, he⟩ := List.getElem_of_mem hfr
    exact ⟨i, List.mem_zipIdx_iff_getElem?.mpr (by rw [List.getElem?_eq_getElem hi, he])⟩
  have hF : FrameOk V f h := ⟨hh, hfr, lm f hfr, (hwds f hfr).2, lmods f hfr⟩
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at ha
  obtain ⟨⟨⟨hatom, hparts⟩, _⟩, hjoin⟩ := ha
  unfold atomOk at hatom
  rw [hfind] at hatom
  simp only [Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hatom
  obtain ⟨⟨hcount, hmk⟩, hmods⟩ := hatom
  have hpa : ∀ x ∈ a.args, ∀ p ∈ x.2.parts, PartOk V f p := by
    intro x hx p hp
    have := hparts p (List.mem_append_left _ (List.mem_flatMap.mpr ⟨x, hx, hp⟩))
    cases p <;> simp_all [PartOk]
  have hpm : ∀ q ∈ preps a.mods, PartOk V f q.2 := by
    intro q hq
    have := hparts q.2 (List.mem_append_right _ (List.mem_filterMap.mpr ⟨.prep q.1 q.2, mem_preps hq, rfl⟩))
    cases hq2 : q.2 <;> simp_all [PartOk]
  have hja : ∀ x ∈ a.args, ∀ j ps, x.2 = .joined j ps →
      f.split.contains x.1 = false ∧ 2 ≤ ps.length ∧ longEnd ps = false := by
    intro x hx j ps he
    have := hjoin x hx
    obtain ⟨m, fl⟩ := x
    simp only at he; subst he
    simp_all
  -- the object, and the elements after it
  let objs := a.args.filter (·.1 == "")
  let rest := a.args.filter (·.1 != "")
  let bs : List Blk := rest.map (fun x => .arg x.1 x.2) ++ (preps a.mods).map (fun q => .prep q.1 q.2)
  have hbs : ∀ b ∈ bs, BlkOk V f b := by
    intro b hb
    rcases List.mem_append.mp hb with hb | hb
    · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hb
      obtain ⟨hxa, hxe⟩ := List.mem_filter.mp hx
      exact ⟨by simpa using hmk x hxa, by simpa using hxe, hpa x hxa, hja x hxa⟩
    · obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hb
      exact ⟨by simpa using hmods (.prep q.1 q.2) (mem_preps hq), hpm q hq⟩
  obtain ⟨ob, hob, hobj⟩ : ∃ ob, ObjOk V f ob ∧ objs = (ob.map (fun fl => ("", fl))).toList := by
    by_cases ho : "" ∈ f.markers
    · have h1 : objs.length = 1 := by simpa [ho] using hcount
      obtain ⟨x, hx⟩ := List.length_eq_one_iff.mp h1
      have hxm : x ∈ objs := by rw [hx]; simp
      obtain ⟨hxa, hxe⟩ := List.mem_filter.mp hxm
      obtain ⟨m, fl⟩ := x
      simp only [beq_iff_eq] at hxe
      subst hxe
      exact ⟨some fl, ⟨ho, hpa _ hxa, fun j ps he => hja _ hxa j ps he⟩, by rw [hx]; rfl⟩
    · have h0 : objs = [] := by
        have hc := hcount
        simp only [ho, List.elem_eq_mem, decide_false, Bool.false_eq_true, if_false] at hc
        exact List.length_eq_zero_iff.mp hc
      exact ⟨none, ho, by rw [h0]; rfl⟩
  have hws : ∀ w ∈ advWords a.mods, w ∈ V.adverbs ∧ w.toLower = w := by
    intro w hw
    have := hmods (.adv w) (mem_advWords hw)
    exact ⟨by simpa using this, la w (by simpa using this)⟩
  -- the normal form, as `s_inv` reads it
  have htoks : a.normal = .slot 0 :: (fwToks a.toWord a.beWord ++ (advWords a.mods).map .word ++
      coreToks f ob bs) := by
    rw [normal_toks, ← hfh]
    have hc : a.canon.args = objs ++ rest := rfl
    simp only [coreToks, fwToks, hc, List.flatMap_append, hobj, List.append_assoc]
    congr 4
    cases ob <;> simp [objToks, blocks, bs, Blk.toks, Blk.marker, Blk.rest, List.flatMap_map, wordsOf_empty,
      Filler.toks]
  rw [htoks] at hg
  have hs := s_inv hV hW hF (lh f hfr) (hwds f hfr).1 hob hbs a.toWord a.beWord (advWords a.mods) hws hg
  -- the item's meaning
  let es : List Elt := a.canon.args.map (fun q => Elt.arg q.1 q.2) ++ (preps a.mods).map (fun q => Elt.mod (.prep q.1 q.2))
  have hes : objPieces ob ++ bs.map Blk.piece = es.map (fun e => Piece.elt e .own) := by
    have hc : a.canon.args = objs ++ rest := rfl
    simp only [es, hc, hobj, bs, List.map_append, List.map_map, List.append_assoc]
    cases ob <;> simp [objPieces, Blk.piece, Function.comp_def]
  rw [hes, single_meaning] at hs
  have hcanon : (List.foldl Atom.add ⟨a.toWord, a.beWord, f.head, [], []⟩
      (List.map (fun w => Elt.mod (Modifier.adv w)) (advWords a.mods) ++ es)) = a.canon := by
    rw [canon_eq a, hfh]
  rw [hcanon] at hs
  exact (Option.some.inj hs).symm


/-- (3) Every derivation of `a.normal` that has a meaning means `.one a.canon`. -/
theorem normal_unique (V : Vocab) (hV : framesOk V = true) (a : Atom) (ha : normalOk V a = true) :
    ∀ d B c, VE.Grammar.Derives (grammar V) (.n (grammar V).start) a.normal d →
      meaning V () d = .ok (B, c, ()) → B = .one a.canon := by
  intro d B c hd hm
  have hp : piecesOf (closed (schema V)).toArray d = some [.act B] := by
    unfold meaning meaningWith at hm
    split at hm
    · split at hm
      · cases hm; assumption
      · cases hm
    · cases hm
  have hg : Gen V (.n .S) a.normal [.act B] := ⟨d, hd.1, hd.2, hp⟩
  have := normal_pieces V hV a ha hg
  simp only [List.cons.injEq, Piece.act.injEq, and_true] at this
  exact this

end VE.Acts.NormalProofs

namespace VE.Acts

/-- Render round trip (docs/spec/act-phrases.md 5.6): the normal form reads back with one meaning, the atom in
canonical order. (1) `normal_derived`, (2) `parse_bounds` and (3) `normal_unique`, through
`read_normal_of_unique`. -/
theorem read_normal (V : Vocab) (h : framesOk V = true) (a : Atom) (ha : normalOk V a = true) :
    ∃ N0 b0, ∀ N b, N0 ≤ N → b0 ≤ b → read V N b a.normal.toArray = .ok (.one a.canon) :=
  NormalProofs.read_normal_of_unique V h a ha (NormalProofs.normal_unique V h a ha)

end VE.Acts
