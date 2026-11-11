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

theorem ap_SINGLE' (cs : List Piece) (rhs : List RSym) (hr : rhs = [.n .SC] ∨ rhs = [.n .ADVSO, .n .SC] ∨
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
    rw [ap_SINGLE' cs _ (by simp)] at ha
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
    rw [ap_SINGLE' _ _ (by simp)] at ha
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
    rw [ap_SINGLE' _ _ (by simp)] at ha
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
    rw [ap_SINGLE' _ _ (by simp)] at ha
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

end VE.Acts.NormalProofs
