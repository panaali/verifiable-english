import VE.Acts.NormalInverse

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

/-- `AR m` where the normal form has an element `b`: `b` is an argument with the marker `m`; `AR m` reads its marker
and first part, which is all of it when the filler is one part. -/
theorem ar_block (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {m : String} {b : Blk} {u v R : List Tok}
    {ps : List Piece} (hg0 : Gen V (.n (.F h (.AR m))) u ps) (he : u ++ v = b.toks ++ R) (hb : BlkOk V f b)
    (hv : Stop V f v) (hR : Next V f R) :
    ∃ p, ps = [.elt (.arg m (.one p)) .own] ∧ ((b = .arg m (.one p) ∧ u = b.toks ∧ v = R) ∨
      ∃ j q rest, b = .arg m (.joined j (p :: q :: rest)) ∧ v = tailToks j (q :: rest) ++ R) := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr
  have e := zip_frame hF.mem hfr; subst fr
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
  obtain ⟨hbm, hbne⟩ := blkOk_marker hb hF
  simp only [Blk.toks, List.append_assoc] at he
  obtain ⟨hmn, rfl, he2, rfl⟩ := mk_block hW hF (List.mem_append_left _ (by assumption)) (by assumption) hbm hbne h1 he
  cases b with
  | prep n p =>
    simp only [Blk.marker] at hmn; subst hmn
    exact (hW.modsMk f hF.frame _ hb.1 (by assumption)).elim
  | arg n fl =>
    simp only [Blk.marker] at hmn; subst hmn
    obtain ⟨-, -, hok, hj⟩ := hb
    cases fl with
    | one p =>
      obtain ⟨rfl, rfl, rfl⟩ := fl_part hF.mem h2 he2 (hok p (by simp [Filler.parts])) hv (next_stop hR)
      simp only [List.nil_append] at ha; rw [ap_AR] at ha
      exact ⟨p, (Option.some.inj ha).symm, .inl ⟨rfl, by simp [Blk.toks, Blk.rest, Filler.toks], rfl⟩⟩
    | joined j ps =>
      obtain ⟨-, hlen, -⟩ := hj j ps rfl
      obtain ⟨p, q, rest, rfl⟩ : ∃ p q rest, ps = p :: q :: rest := by
        match ps, hlen with
        | p :: q :: rest, _ => exact ⟨p, q, rest, rfl⟩
      simp only [Blk.rest, Filler.toks, listToks_eq, List.append_assoc] at he2
      obtain ⟨xt, ut, htl, hxt⟩ := tailToks_head j q rest
      obtain ⟨rfl, rfl, rfl⟩ := fl_part hF.mem h2 he2 (hok p (by simp [Filler.parts])) hv
        (by rw [htl]; exact stop_jc hxt)
      simp only [List.nil_append] at ha; rw [ap_AR] at ha
      exact ⟨p, (Option.some.inj ha).symm, .inr ⟨j, q, rest, rfl, rfl⟩⟩


/-- `RL m` (each part with its own marker) cannot read an element of a normal form: after the first part comes an
element, or a part of the same list, never the join word and marker `RT m` needs. -/
theorem rl_false (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {m : String} {b : Blk} {bs : List Blk}
    {u v : List Tok} {ps : List Piece} (hV : framesOk V = true) (hg0 : Gen V (.n (.F h (.RL m))) u ps)
    (he : u ++ v = b.toks ++ blocks bs) (hb : BlkOk V f b) (hbs : Next V f (blocks bs)) : False := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr
  have e := zip_frame hF.mem hfr; subst fr
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
  rw [List.append_assoc] at he
  obtain ⟨x, w2', rfl, hx⟩ := rt_head h2
  obtain ⟨p, -, hc⟩ := ar_block hW hF h1 he hb (stop_jc hx) hbs
  rcases hc with ⟨-, -, hv⟩ | ⟨j, q, rest, rfl, hv⟩
  · exact ef_not_jc hW hF.frame (hbs x (by rw [← hv]; simp)) hx
  · obtain ⟨x', y, w2'', he2, hy⟩ := rt_head2 hV hF h2
    obtain ⟨t, more, ht⟩ := tailToks_two j q rest
    obtain ⟨y', q', hq, hy'⟩ := part_head_not_excl (hb.2.2.1 q (by simp [Filler.parts]))
    rw [he2, ht, hq] at hv
    simp only [List.cons_append, List.cons.injEq] at hv
    exact hy' (hv.2.1 ▸ hy)

/-- `OL m` (the marker once, then a list) where the normal form has an element `b`: `b` is an argument with the
marker `m` and a joined filler, and `OL m` reads all of it. -/
theorem ol_block (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {m : String} {b : Blk} {bs : List Blk}
    {u v : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h (.OL m))) u ps)
    (he : u ++ v = b.toks ++ blocks bs) (hb : BlkOk V f b) (hbs : Next V f (blocks bs)) (hv : Stop V f v) :
    ∃ j qs, b = .arg m (.joined j qs) ∧ u = b.toks ∧ v = blocks bs ∧ ps = [.list j qs] := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr
  have e := zip_frame hF.mem hfr; subst fr
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
  obtain ⟨hbm, hbne⟩ := blkOk_marker hb hF
  simp only [Blk.toks, List.append_assoc] at he
  obtain ⟨hmn, rfl, he2, rfl⟩ := mk_block hW hF (List.mem_append_left _ (by assumption)) (by assumption) hbm hbne h1 he
  cases b with
  | prep n p =>
    simp only [Blk.marker] at hmn; subst hmn
    exact (hW.modsMk f hF.frame _ hb.1 (by assumption)).elim
  | arg n fl =>
    simp only [Blk.marker] at hmn; subst hmn
    obtain ⟨-, -, hok, hj⟩ := hb
    cases fl with
    | one p => exact (pl_one hW hF.frame hF.mem h2 he2 (hok p (by simp [Filler.parts])) hbs).elim
    | joined j qs =>
      obtain ⟨-, hlen, -⟩ := hj j qs rfl
      obtain ⟨rfl, rfl, rfl⟩ := pl_inv hF.mem h2 he2 hlen hok hv (next_stop hbs)
      simp only [List.nil_append] at ha; rw [ap_OL] at ha
      exact ⟨j, qs, rfl, by simp [Blk.toks, Blk.rest, Filler.toks], rfl, (Option.some.inj ha).symm⟩

/-- An adverb where the normal form has an element: impossible (no adverb is a marker word). -/
theorem adv_not_block (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {b : Blk} {R : List Tok} {w : String}
    {u : List Tok} (he : .word w :: u = b.toks ++ R) (hw : V.adverbs.contains w.toLower = true) (hb : BlkOk V f b) :
    False := by
  obtain ⟨hbm, hbne⟩ := blkOk_marker hb hF
  obtain ⟨w0, ws, hws⟩ := List.exists_cons_of_ne_nil (hF.words _ hbm hbne)
  simp only [Blk.toks, hws, List.map_cons, List.cons_append, List.cons.injEq, Tok.word.injEq] at he
  obtain ⟨rfl, -⟩ := he
  have hl := hF.lower _ hbm hbne w (by simp [hws])
  rw [hl] at hw
  exact hW.advMk w (by simpa using hw) f hF.frame _ hbm hbne (by simp [hws])

/-- A prepositional modifier (`EE → MK m FL`, `m` a modifier marker) where the normal form has the element `b`. -/
theorem ee_prep (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {m : String} (hmm : m ∈ f.mods) {b : Blk}
    {bs : List Blk} {u v : List Tok} {cs ps : List Piece} (hg : GenAll V [.n (.MK m), .n (.F h .FL)] u cs)
    (ha : applyRule ⟨.F h .EE, [.n (.MK m), .n (.F h .FL)], .shape⟩ cs = some ps)
    (he : u ++ v = b.toks ++ blocks bs) (hb : BlkOk V f b) (hbs : Next V f (blocks bs)) (hv : Next V f v) :
    u = b.toks ∧ v = blocks bs ∧ ps = [b.piece] := by
  obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
  obtain ⟨hbm, hbne⟩ := blkOk_marker hb hF
  simp only [Blk.toks, List.append_assoc] at he
  obtain ⟨hmn, rfl, he2, rfl⟩ := mk_block hW hF (List.mem_append_right _ hmm)
    (fun e => hF.mods (e ▸ hmm)) hbm hbne h1 he
  cases b with
  | arg n fl =>
    simp only [Blk.marker] at hmn; subst hmn
    exact (hW.modsMk f hF.frame _ hmm hb.1).elim
  | prep n p =>
    simp only [Blk.marker] at hmn; subst hmn
    obtain ⟨rfl, rfl, rfl⟩ := fl_part hF.mem h2 he2 hb.2 (next_stop hv) (next_stop hbs)
    simp only [List.nil_append] at ha; rw [ap_EEmod] at ha
    exact ⟨by simp [Blk.toks, Blk.rest], rfl, by rw [← Option.some.inj ha]; rfl⟩

/-- One element (`EE`) where the normal form has the element `b`: it reads `b`, with `b`'s piece. -/
theorem ee_block (hV : framesOk V = true) (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {b : Blk}
    {bs : List Blk} {u v : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h .EE)) u ps)
    (he : u ++ v = b.toks ++ blocks bs) (hb : BlkOk V f b) (hbs : Next V f (blocks bs)) (hv : Next V f v) :
    u = b.toks ∧ v = blocks bs ∧ ps = [b.piece] := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr)
  · rw [ap_EE1] at ha; cases ha
    obtain ⟨p, rfl, hc⟩ := ar_block hW hF (genAll1 hg) he hb (next_stop hv) hbs
    rcases hc with ⟨rfl, rfl, rfl⟩ | ⟨j, q, rest, rfl, rfl⟩
    · exact ⟨rfl, rfl, rfl⟩
    · obtain ⟨xt, ut, htl, hxt⟩ := tailToks_head j q rest
      exact (ef_not_jc hW hF.frame (hv xt (by rw [htl]; simp)) hxt).elim
  · rw [ap_EE1] at ha; cases ha
    obtain ⟨rhs2, k2, cs2, hr2, hg2, ha2⟩ := gen_rule (genAll1 hg)
    rules_of hr2 fr2 hfr2 <;> (have e := zip_frame hF.mem hfr2; subst fr2)
    · exact (rl_false hW hF hV (genAll1 hg2) he hb hbs).elim
    · obtain ⟨j, qs, rfl, rfl, rfl, rfl⟩ := ol_block hW hF (genAll1 hg2) he hb hbs (next_stop hv)
      rw [ap_LST] at ha2
      exact ⟨rfl, rfl, (Option.some.inj ha2).symm⟩
  · obtain ⟨x, rfl, hx, -⟩ := gen_t_inv (genAll1 hg)
    cases x <;> simp [Term.accepts] at hx
    exact (adv_not_block hW hF he (by simpa using hx) hb).elim
  · exact ee_prep hW hF (by assumption) hg ha he hb hbs hv

end VE.Acts.NormalProofs
