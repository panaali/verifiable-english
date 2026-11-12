import VE.Acts.NormalInverse

/-! The elements, the object and the head of a normal form read back, for the uniqueness half of `read_normal`
(docs/spec/act-phrases.md 5.6; `VE.Acts.NormalUnique`).

Proofs only. Where a normal form has an element after the object (`Blk`: a marker's words, then its filler), every
derivation of `EE` reads exactly that element with its piece (`ee_block`); a run `ER` reads the next elements
(`er_blocks`); no split construct `SPL` can start there (`spl_false`); `SM` reads the object and all the elements, in
order (`sm_inv`); and `SC` reads the head of the atom's own frame, then those (`sc_inv`, `hd_same`).
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


theorem blocks_append_cons (b : Blk) (bs : List Blk) : blocks (b :: bs) = b.toks ++ blocks bs := by simp [blocks]

theorem next_append {u v : List Tok} (hu : Next V f u) (hne : u ≠ []) : Next V f (u ++ v) := by
  obtain ⟨x, u', rfl⟩ := List.exists_cons_of_ne_nil hne
  intro y hy; simp at hy; subst hy; exact hu x (by simp)

theorem next_nil : Next V f [] := by intro x hx; simp at hx

/-- A run of elements (`ER`) where the normal form has the elements `bs`: it reads the first `k` of them. -/
theorem er_blocks (hV : framesOk V = true) (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) :
    ∀ (bs : List Blk) {u v : List Tok} {ps : List Piece}, Gen V (.n (.F h .ER)) u ps → u ++ v = blocks bs →
    (∀ b ∈ bs, BlkOk V f b) → Next V f v →
    ∃ k, 0 < k ∧ u = blocks (bs.take k) ∧ v = blocks (bs.drop k) ∧ ps = (bs.take k).map Blk.piece
  | [], u, v, ps, hg0, he, _, _ => (gen_ne hV hg0 (by simp [blocks] at he; exact he.1)).elim
  | b :: bs, u, v, ps, hg0, he, hbs, hv => by
    have hbs' : ∀ x ∈ bs, BlkOk V f x := fun x hx => hbs x (by simp [hx])
    rw [blocks_append_cons] at he
    obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
    rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr)
    · rw [ap_ER1] at ha; cases ha
      obtain ⟨rfl, rfl, rfl⟩ := ee_block hV hW hF (genAll1 hg) he (hbs b (by simp)) (blocks_next hF hbs') hv
      exact ⟨1, by omega, by simp [blocks], by simp [blocks], rfl⟩
    · rw [ap_ER2] at ha; cases ha
      obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
      rw [List.append_assoc] at he
      obtain ⟨rfl, he2, rfl⟩ := ee_block hV hW hF h1 he (hbs b (by simp)) (blocks_next hF hbs')
        (next_append (er_head hV hF h2) (gen_ne hV h2))
      obtain ⟨k, hk, rfl, rfl, rfl⟩ := er_blocks hV hW hF bs h2 he2 hbs' hv
      exact ⟨k + 1, by omega, by simp [blocks], by simp [blocks], by simp⟩

/-- `OL m` with a split marker `m` where the normal form has an element: impossible. -/
theorem ol_split_false (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {m : String} (hs : m ∈ f.split) {b : Blk}
    {bs : List Blk} {u v : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h (.OL m))) u ps)
    (he : u ++ v = b.toks ++ blocks bs) (hb : BlkOk V f b) (hbs : Next V f (blocks bs)) : False := by
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
    | one p => exact pl_one hW hF.frame hF.mem h2 he2 (hok p (by simp [Filler.parts])) hbs
    | joined j qs =>
      have h1 := (hj j qs rfl).1
      exact absurd hs (by simpa using h1)

/-- A prepositional modifier followed by a comma or join word where the normal form has an element: impossible. -/
theorem mk_fl_then_jc (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {m : String} (hmm : m ∈ f.mods) {b : Blk}
    {bs : List Blk} {u w : List Tok} {x : Tok} {cs : List Piece} (hg : GenAll V [.n (.MK m), .n (.F h .FL)] u cs)
    (he : u ++ x :: w = b.toks ++ blocks bs) (hx : JC x) (hb : BlkOk V f b) (hbs : Next V f (blocks bs)) : False := by
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
    obtain ⟨-, hxw, -⟩ := fl_part hF.mem h2 he2 hb.2 (stop_jc hx) (next_stop hbs)
    exact ef_not_jc hW hF.frame (hbs x (by rw [← hxw]; simp)) hx

/-- A split construct (`SPL`) where the normal form has elements: impossible. A split marker's filler is one part
(`normalOk`), and a joined modifier needs a join word after a modifier, where the normal form has an element. -/
theorem spl_false (hV : framesOk V = true) (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {bs : List Blk}
    {u v : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h .SPL)) u ps) (he : u ++ v = blocks bs)
    (hbs : ∀ b ∈ bs, BlkOk V f b) : False := by
  cases bs with
  | nil => exact gen_ne hV hg0 (by simp [blocks] at he; exact he.1)
  | cons b bs =>
  have hbs' : ∀ x ∈ bs, BlkOk V f x := fun x hx => hbs x (by simp [hx])
  have hb := hbs b (by simp)
  rw [blocks_append_cons] at he
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr)
  · obtain ⟨rhs2, k2, cs2, hr2, hg2, ha2⟩ := gen_rule (genAll1 hg)
    rules_of hr2 fr2 hfr2 <;> (have e := zip_frame hF.mem hfr2; subst fr2)
    · exact rl_false hW hF hV (genAll1 hg2) he hb (blocks_next hF hbs')
    · exact ol_split_false hW hF (by assumption) (genAll1 hg2) he hb (blocks_next hF hbs')
  · obtain ⟨rhs2, k2, cs2, hr2, hg2, ha2⟩ := gen_rule (genAll1 hg)
    rules_of hr2 fr2 hfr2
    have e := zip_frame hF.mem hfr2; subst fr2
    obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg2
    rw [List.append_assoc] at he
    obtain ⟨x2, w2', rfl, hx2⟩ := mgt_head h2
    obtain ⟨rhs3, k3, cs3, hr3, hg3, ha3⟩ := gen_rule h1
    rules_of hr3 fr3 hfr3 <;> (have e := zip_frame hF.mem hfr3; subst fr3)
    · obtain ⟨x, rfl, hx, -⟩ := gen_t_inv (genAll1 hg3)
      cases x <;> simp [Term.accepts] at hx
      exact adv_not_block hW hF he (by simpa using hx) hb
    · exact mk_fl_then_jc hW hF (by assumption) hg3 he hx2 hb (blocks_next hF hbs')


/-! ### The object, and the head's material (`SM`) -/

/-- The object of the atom, under a frame with `""` among its markers: its parts and joined filler as `normalOk`
admits them. -/
def ObjOk (V : Vocab) (f : Frame) : Option Filler → Prop
  | some fl => "" ∈ f.markers ∧ (∀ p ∈ fl.parts, PartOk V f p) ∧
      ∀ j ps, fl = .joined j ps → f.split.contains "" = false ∧ 2 ≤ ps.length ∧ longEnd ps = false
  | none => "" ∉ f.markers
def objToks : Option Filler → List Tok
  | some fl => fl.toks
  | none => []
def objPieces : Option Filler → List Piece
  | some fl => [.elt (.arg "" fl) .own]
  | none => []

theorem two_parts {ps : List Part} (h : 2 ≤ ps.length) : ∃ p q rest, ps = p :: q :: rest := by
  match ps, h with
  | p :: q :: rest, _ => exact ⟨p, q, rest, rfl⟩

/-- The object (`O`) where the normal form has the object filler `fl`. -/
theorem o_block (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {fl : Filler} (hok : ∀ p ∈ fl.parts, PartOk V f p)
    (hj : ∀ j ps, fl = .joined j ps → f.split.contains "" = false ∧ 2 ≤ ps.length ∧ longEnd ps = false)
    {bs : List Blk} {u v : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h .O)) u ps)
    (he : u ++ v = fl.toks ++ blocks bs) (hbs : Next V f (blocks bs)) (hv : Next V f v) :
    u = fl.toks ∧ v = blocks bs ∧ ps = [.elt (.arg "" fl) .own] := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr)
  · cases fl with
    | one p =>
      obtain ⟨rfl, rfl, rfl⟩ := fl_part hF.mem (genAll1 hg) he (hok p (by simp [Filler.parts])) (next_stop hv)
        (next_stop hbs)
      rw [ap_O1] at ha
      exact ⟨rfl, rfl, (Option.some.inj ha).symm⟩
    | joined j qs =>
      obtain ⟨p, q, rest, rfl⟩ := two_parts (hj j qs rfl).2.1
      simp only [Filler.toks, listToks_eq, List.append_assoc] at he
      obtain ⟨xt, ut, htl, hxt⟩ := tailToks_head j q rest
      obtain ⟨-, rfl, -⟩ := fl_part hF.mem (genAll1 hg) he (hok p (by simp [Filler.parts])) (next_stop hv)
        (by rw [htl]; exact stop_jc hxt)
      exact (ef_not_jc hW hF.frame (hv xt (by rw [htl]; simp)) hxt).elim
  · cases fl with
    | one p => exact (pl_one hW hF.frame hF.mem (genAll1 hg) he (hok p (by simp [Filler.parts])) hbs).elim
    | joined j qs =>
      obtain ⟨-, hlen, -⟩ := hj j qs rfl
      obtain ⟨rfl, rfl, rfl⟩ := pl_inv hF.mem (genAll1 hg) he hlen hok (next_stop hv) (next_stop hbs)
      rw [ap_O2] at ha
      exact ⟨rfl, rfl, (Option.some.inj ha).symm⟩

/-- The object read as a split list (`OS`) where the normal form has the object: impossible (a split object is one
part). -/
theorem os_false (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {fl : Filler} (hok : ∀ p ∈ fl.parts, PartOk V f p)
    (hj : ∀ j ps, fl = .joined j ps → f.split.contains "" = false ∧ 2 ≤ ps.length ∧ longEnd ps = false)
    {bs : List Blk} {u v : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h .OS)) u ps)
    (he : u ++ v = fl.toks ++ blocks bs) (hbs : Next V f (blocks bs)) : False := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr
  have e := zip_frame hF.mem hfr; subst fr
  cases fl with
  | one p => exact pl_one hW hF.frame hF.mem (genAll1 hg) he (hok p (by simp [Filler.parts])) hbs
  | joined j qs =>
    have h1 := (hj j qs rfl).1
    exact absurd (by assumption : "" ∈ f.split) (by simpa using h1)

/-- The object and the elements after it (`OWNM`): the object, then the first `k` elements. -/
theorem ownm_block (hV : framesOk V = true) (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {fl : Filler}
    (hob : ObjOk V f (some fl)) {bs : List Blk} (hbs : ∀ b ∈ bs, BlkOk V f b) {u v : List Tok} {ps : List Piece}
    (hg0 : Gen V (.n (.F h .OWNM)) u ps) (he : u ++ v = fl.toks ++ blocks bs) (hv : Next V f v) :
    ∃ k, u = fl.toks ++ blocks (bs.take k) ∧ v = blocks (bs.drop k) ∧
      ps = .elt (.arg "" fl) .own :: (bs.take k).map Blk.piece := by
  obtain ⟨hobj, hok, hj⟩ := hob
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr)
  · rw [ap_OWNM1] at ha; cases ha
    obtain ⟨rfl, rfl, rfl⟩ := o_block hW hF hok hj (genAll1 hg) he (blocks_next hF hbs) hv
    exact ⟨0, by simp [blocks], by simp, by simp⟩
  · rw [ap_OWNM2] at ha; cases ha
    obtain ⟨w1, w2, c1, c2, rfl, rfl, h1, h2⟩ := genAll2 hg
    rw [List.append_assoc] at he
    obtain ⟨rfl, he2, rfl⟩ := o_block hW hF hok hj h1 he (blocks_next hF hbs)
      (next_append (er_head hV hF h2) (gen_ne hV h2))
    obtain ⟨k, -, rfl, rfl, rfl⟩ := er_blocks hV hW hF bs h2 he2 hbs hv
    exact ⟨k, rfl, rfl, rfl⟩
  · exact absurd hobj (by assumption)

theorem blk_ne {h : Nat} (hF : FrameOk V f h) {b : Blk} (hb : BlkOk V f b) : b.toks ≠ [] := by
  obtain ⟨hm, hne⟩ := blkOk_marker hb hF
  obtain ⟨w, ws, hw⟩ := List.exists_cons_of_ne_nil (hF.words _ hm hne)
  simp [Blk.toks, hw]

theorem blocks_drop {h : Nat} (hF : FrameOk V f h) {bs : List Blk} (hbs : ∀ b ∈ bs, BlkOk V f b) {k : Nat}
    (he : blocks (bs.drop k) = []) : bs.take k = bs := by
  apply List.take_of_length_le
  refine Nat.le_of_not_lt (fun hk => ?_)
  obtain ⟨b, rest, hd⟩ := List.exists_cons_of_ne_nil (l := bs.drop k) (by simp; omega)
  rw [hd, blocks_append_cons] at he
  exact blk_ne hF (hbs b (List.mem_of_mem_drop (hd ▸ List.mem_cons_self))) (List.append_eq_nil_iff.mp he).1

/-- The head's material (`SM`) where the normal form has the object (if any) and the elements `bs`: their pieces,
in order. -/
theorem sm_inv (hV : framesOk V = true) (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h) {ob : Option Filler}
    (hob : ObjOk V f ob) {bs : List Blk} (hbs : ∀ b ∈ bs, BlkOk V f b) {u : List Tok} {ps : List Piece}
    (hg0 : Gen V (.n (.F h .SM)) u ps) (he : u = objToks ob ++ blocks bs) : ps = objPieces ob ++ bs.map Blk.piece := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  have hdrop : ∀ k, ∀ b ∈ bs.drop k, BlkOk V f b := fun k b hb => hbs b (List.mem_of_mem_drop hb)
  subst he
  rules_of hr fr hfr <;> (have e := zip_frame hF.mem hfr; subst fr) <;>
    (cases ob <;> (try exact absurd (by assumption : "" ∈ f.markers) hob) <;>
      (try exact absurd hob.1 (by assumption)))
  · rw [ap_SM] at ha; cases ha
    obtain ⟨k, -, hv, rfl⟩ := ownm_block hV hW hF hob hbs (genAll1 hg) (by simp [objToks]) next_nil
    rw [blocks_drop hF hbs hv.symm]; rfl
  · obtain ⟨w1, w2, c1, c2, he, -, h1, h2⟩ := genAll2 hg
    obtain ⟨k, -, hv, -⟩ := ownm_block hV hW hF hob hbs h1 (by rw [← he]; rfl) (spl_head hV hF h2)
    exact (spl_false hV hW hF h2 (v := []) (by simpa using hv) (hdrop k)).elim
  · obtain ⟨w1, w2, w3, c1, c2, c3, he, -, h1, h2, h3⟩ := genAll3 hg
    obtain ⟨k, -, hv, -⟩ := ownm_block hV hW hF hob hbs h1 (v := w2 ++ w3) (by rw [← List.append_assoc, ← he]; rfl)
      (next_append (spl_head hV hF h2) (gen_ne hV h2))
    exact (spl_false hV hW hF h2 hv (hdrop k)).elim
  · exact (os_false hW hF hob.2.1 hob.2.2 (genAll1 hg) (v := []) (by simp [objToks])
      (blocks_next hF hbs)).elim
  · obtain ⟨w1, w2, c1, c2, he, -, h1, h2⟩ := genAll2 hg
    exact (os_false hW hF hob.2.1 hob.2.2 h1 (by rw [← he]; rfl) (blocks_next hF hbs)).elim
  · rw [ap_SM] at ha; cases ha
    obtain ⟨k, -, he2, hv, rfl⟩ := er_blocks hV hW hF bs (genAll1 hg) (v := []) (by simp [objToks])
      hbs next_nil
    rw [blocks_drop hF hbs hv.symm]; rfl
  · obtain ⟨w1, w2, c1, c2, he, -, h1, h2⟩ := genAll2 hg
    obtain ⟨k, -, -, hv, -⟩ := er_blocks hV hW hF bs h1 (by rw [← he]; rfl) hbs (spl_head hV hF h2)
    exact (spl_false hV hW hF h2 (v := []) (by simpa using hv) (hdrop k)).elim
  · obtain ⟨w1, w2, w3, c1, c2, c3, he, -, h1, h2, h3⟩ := genAll3 hg
    obtain ⟨k, -, -, hv, -⟩ := er_blocks hV hW hF bs h1 (v := w2 ++ w3) (by rw [← List.append_assoc, ← he]; rfl) hbs
      (next_append (spl_head hV hF h2) (gen_ne hV h2))
    exact (spl_false hV hW hF h2 hv (hdrop k)).elim
  · exact (spl_false hV hW hF (genAll1 hg) (v := []) (by simp [objToks]) hbs).elim
  · obtain ⟨w1, w2, c1, c2, he, -, h1, h2⟩ := genAll2 hg
    exact (spl_false hV hW hF h1 (by rw [← he]; rfl) hbs).elim


/-! ### The head fixes the frame (`SC`) -/

theorem nodup_map_idx {α β : Type} (g : α → β) : ∀ {l : List α} {i j : Nat} {a b : α}, (l.map g).Nodup →
    l[i]? = some a → l[j]? = some b → g a = g b → i = j
  | [], _, _, _, _, _, h, _, _ => by simp at h
  | x :: l, 0, 0, _, _, _, _, _, _ => rfl
  | x :: l, 0, j + 1, a, b, hn, ha, hb, he => by
    simp only [List.map_cons, List.nodup_cons] at hn
    simp at ha hb; subst ha
    exact (hn.1 (List.mem_map.mpr ⟨b, List.mem_of_getElem? hb, he.symm⟩)).elim
  | x :: l, i + 1, 0, a, b, hn, ha, hb, he => by
    simp only [List.map_cons, List.nodup_cons] at hn
    simp at ha hb; subst hb
    exact (hn.1 (List.mem_map.mpr ⟨a, List.mem_of_getElem? ha, he⟩)).elim
  | x :: l, i + 1, j + 1, a, b, hn, ha, hb, he => by
    simp only [List.map_cons, List.nodup_cons] at hn
    simp only [List.getElem?_cons_succ] at ha hb
    rw [nodup_map_idx g hn.2 ha hb he]

/-- `HD` of any frame where the normal form has frame `f`'s head: it is frame `f`'s, and reads its head. -/
theorem hd_same (hV : framesOk V = true) (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h)
    (hl : ∀ w ∈ f.head, w.toLower = w) {g : Frame} {h' : Nat} (hg' : (g, h') ∈ V.frames.zipIdx) {u w R : List Tok}
    {ps : List Piece} (hg0 : Gen V (.n (.F h' .HD)) u ps) (he : u ++ w = f.head.map .word ++ R) :
    h' = h ∧ g = f ∧ u = f.head.map .word ∧ w = R ∧ ps = [.head f.head] := by
  have hgf := List.fst_mem_of_mem_zipIdx hg'
  obtain ⟨vs, rfl, hvs, rfl⟩ := hd_inv hg' (framesOk_words hV g hgf).1 hg0
  have heq : g.head = f.head := by
    rcases map_word_append he with ⟨t, ht, -⟩ | ⟨t, rfl, -⟩
    · have hlv : vs.map String.toLower = vs := lower_map (fun x hx => hl x (by rw [ht]; exact List.mem_append_left _ hx))
      have := hW.headPre g hgf f hF.frame (by rw [List.isPrefixOf_iff_prefix, ← hvs, hlv, ht]; exact List.prefix_append _ _)
      exact this.symm
    · exact hW.headPre f hF.frame g hgf (by
        rw [List.isPrefixOf_iff_prefix, ← hvs, List.map_append, lower_map hl]; exact List.prefix_append _ _)
  have hh : h' = h := by
    have h1 := List.mem_zipIdx_iff_getElem?.mp hg'
    have h2 := List.mem_zipIdx_iff_getElem?.mp hF.mem
    exact nodup_map_idx _ hW.headDup h1 h2 (by simp only; rw [heq])
  subst hh
  have := zip_frame hF.mem hg'; subst this
  have hlv : vs.map String.toLower = vs := by
    rcases map_word_append he with ⟨t, ht, -⟩ | ⟨t, rfl, -⟩
    · exact lower_map (fun x hx => hl x (by rw [ht]; exact List.mem_append_left _ hx))
    · rw [List.map_append, lower_map hl] at hvs
      have ht : t = [] := by simpa using hvs
      subst ht; simp [lower_map hl]
  rw [hlv] at hvs; subst hvs
  have := List.append_cancel_left he
  exact ⟨rfl, rfl, rfl, this, rfl⟩

theorem part_ne {p : Part} (hp : PartOk V f p) : p.toks ≠ [] := by
  obtain ⟨x, rest, he, -⟩ := part_head hp; rw [he]; simp

theorem obj_ne {fl : Filler} (hob : ObjOk V f (some fl)) : fl.toks ≠ [] := by
  obtain ⟨-, hok, hj⟩ := hob
  cases fl with
  | one p => exact part_ne (hok p (by simp [Filler.parts]))
  | joined j qs =>
    obtain ⟨p, q, rest, rfl⟩ := two_parts (hj j qs rfl).2.1
    simp only [Filler.toks, listToks_eq]
    intro he; exact part_ne (hok p (by simp [Filler.parts])) (List.append_eq_nil_iff.mp he).1

/-- The item's core (`SC`) where the normal form has frame `f`'s head, then the object and elements: the head and
their pieces. -/
theorem sc_inv (hV : framesOk V = true) (hW : VocabOk V) {h : Nat} (hF : FrameOk V f h)
    (hl : ∀ w ∈ f.head, w.toLower = w) {ob : Option Filler} (hob : ObjOk V f ob) {bs : List Blk}
    (hbs : ∀ b ∈ bs, BlkOk V f b) {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n .SC) u ps)
    (he : u = f.head.map .word ++ (objToks ob ++ blocks bs)) :
    ps = .head f.head :: (objPieces ob ++ bs.map Blk.piece) := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  subst he
  rules_of hr fr hfr
  · rw [ap_SC1] at ha; cases ha
    obtain ⟨-, -, -, hw, rfl⟩ := hd_same hV hW hF hl hfr (genAll1 hg) (w := []) (R := objToks ob ++ blocks bs) (by simp)
    have hob' : objToks ob = [] ∧ blocks bs = [] := List.append_eq_nil_iff.mp hw.symm
    have hbs0 : bs = [] := by
      cases bs with
      | nil => rfl
      | cons b bs => exact (blk_ne hF (hbs b (by simp)) (List.append_eq_nil_iff.mp (by simpa [blocks_append_cons] using hob'.2)).1).elim
    subst hbs0
    cases ob with
    | none => rfl
    | some fl => exact (obj_ne hob hob'.1).elim
  · rw [ap_SC2] at ha; cases ha
    obtain ⟨w1, w2, c1, c2, he, rfl, h1, h2⟩ := genAll2 hg
    obtain ⟨rfl, rfl, rfl, rfl, rfl⟩ := hd_same hV hW hF hl hfr h1 he.symm
    rw [sm_inv hV hW hF hob hbs h2 rfl]; rfl


/-! ### Function words and adverbs (`SINGLE`) -/

/-- A function word: *to* or *be*. -/
def TB (x : Tok) : Prop := ∃ v, x = .word v ∧ (v.toLower = "to" ∨ v.toLower = "be")
/-- An adverb. -/
def ADV (V : Vocab) (x : Tok) : Prop := ∃ v, x = .word v ∧ V.adverbs.contains v.toLower = true

/-- Neither a function word nor an adverb: how an item's core begins. -/
def NTA (V : Vocab) (x : Tok) : Prop := ¬ TB x ∧ ¬ ADV V x

/-- The function words of the normal form. -/
def fwToks (t b : Bool) : List Tok := (if t then [Tok.word "to"] else []) ++ (if b then [Tok.word "be"] else [])

theorem tb_not_adv (hW : VocabOk V) {x : Tok} (h : TB x) : ¬ ADV V x := by
  obtain ⟨v, rfl, hv⟩ := h; rintro ⟨v', he, ha⟩; cases he
  have := hW.advRes _ (by simpa using ha); rcases hv with hv | hv <;> simp_all

theorem head_all {P : Tok → Prop} {u : List Tok} (hu : ∀ x ∈ u, P x) : ∀ x ∈ u.head?, P x :=
  fun x hx => hu x (List.mem_of_mem_head? hx)

theorem head_append {P : Tok → Prop} {u w : List Tok} (hu : ∀ x ∈ u.head?, P x) (hne : u ≠ []) :
    ∀ x ∈ (u ++ w).head?, P x := by
  cases u with
  | nil => exact absurd rfl hne
  | cons y u => simpa using hu

theorem fwToks_tb (t b : Bool) : ∀ x ∈ fwToks t b, TB x := by
  intro x hx
  cases t <;> cases b <;> simp [fwToks] at hx <;> rcases hx with rfl | rfl <;>
    first | exact ⟨"to", rfl, .inl lower_to⟩ | exact ⟨"be", rfl, .inr lower_be⟩

theorem fw_tb {u : List Tok} {ps : List Piece} (hg : Gen V (.n .FW) u ps) : ∀ x ∈ u, TB x := by
  obtain ⟨vs, rfl, hvs, -⟩ := fw_inv hg
  intro x hx
  obtain ⟨v, hv, rfl⟩ := List.mem_map.mp hx
  have : v.toLower ∈ vs.map String.toLower := List.mem_map_of_mem hv
  refine ⟨v, rfl, ?_⟩
  rcases hvs with h | h | h <;> rw [h] at this <;> simp_all

theorem advso_adv {u : List Tok} {ps : List Piece} (hg : Gen V (.n .ADVSO) u ps) : ∀ x ∈ u, ADV V x := by
  obtain ⟨vs, -, rfl, hvs, -⟩ := advso_inv _ (Nat.le_refl _) hg
  intro x hx
  obtain ⟨v, hv, rfl⟩ := List.mem_map.mp hx
  exact ⟨v, rfl, hvs v hv⟩

theorem ws_adv {ws : List String} (hws : ∀ w ∈ ws, w ∈ V.adverbs ∧ w.toLower = w) : ∀ x ∈ ws.map Tok.word, ADV V x := by
  intro x hx
  obtain ⟨w, hw, rfl⟩ := List.mem_map.mp hx
  exact ⟨w, rfl, by rw [(hws w hw).2]; simpa using (hws w hw).1⟩

/-- The first token of a head: neither a function word nor an adverb. -/
theorem head_word (hW : VocabOk V) {g : Frame} (hg : g ∈ V.frames) {v : String} (hv : g.head.head? = some v.toLower) :
    ¬ TB (.word v) ∧ ¬ ADV V (.word v) := by
  have hm : v.toLower ∈ g.head := List.mem_of_mem_head? hv
  refine ⟨?_, ?_⟩
  · rintro ⟨v', he, hv'⟩; cases he
    have := hW.headRes g hg _ hm; rcases hv' with h | h <;> simp_all
  · rintro ⟨v', he, ha⟩; cases he
    exact hW.advHd _ (by simpa using ha) g hg hm

theorem hd_head (hV : framesOk V = true) (hW : VocabOk V) {g : Frame} {h' : Nat} (hg' : (g, h') ∈ V.frames.zipIdx)
    {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n (.F h' .HD)) u ps) : ∀ x ∈ u.head?, NTA V x := by
  have hgf := List.fst_mem_of_mem_zipIdx hg'
  obtain ⟨vs, rfl, hvs, -⟩ := hd_inv hg' (framesOk_words hV g hgf).1 hg0
  intro x hx
  cases vs with
  | nil => simp at hx
  | cons v vs =>
    simp at hx; subst hx
    exact head_word hW hgf (by rw [← hvs]; rfl)

theorem sc_head (hV : framesOk V = true) (hW : VocabOk V) {u : List Tok} {ps : List Piece} (hg0 : Gen V (.n .SC) u ps) :
    ∀ x ∈ u.head?, NTA V x := by
  obtain ⟨rhs, k, cs, hr, hg, ha⟩ := gen_rule hg0
  rules_of hr fr hfr <;>
  · obtain ⟨w1, w2, c1, c2, rfl, -, h1, -⟩ := genAll_inv_cons hg
    exact head_append (hd_head hV hW hfr h1) (gen_ne hV h1)

end VE.Acts.NormalProofs
