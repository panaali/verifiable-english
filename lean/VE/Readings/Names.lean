import Lean
import VE.Readings.Choice

/-! Facts about the names of the superposed document (docs/spec/composition-s2.md 1.4, 1.7).

A qualified name `rd-<k>-<n>` is reserved (`reservedName_qualify`), so it is never an author name; a rule name
of the chain has no `_`, so `ruleKey` and the decision predicate names built from it are injective
(`exceptedName_inj`, `offName_inj`), and the three families of decision predicate names, the bit predicates and
one another, are disjoint by their prefixes. `String.startsWith` compares through a loop private to
`Init.Data.String.Basic`; `unfold_substrEq_loop` rewrites with that loop's unfolding equation, which the kernel
checks like any other. -/
namespace VE.Readings
open Lean Meta Elab Tactic

/-- The private loop of `String.substrEq`. -/
def substrEqLoopName : Name :=
  .str (.str (.str (.num (.str (.str (.str (.str (.str .anonymous "_private") "Init") "Data") "String") "Basic") 0)
    "String") "substrEq") "loop"

/-- Rewrites the goal once with the unfolding equation of `String.substrEq`'s loop. -/
elab "unfold_substrEq_loop" : tactic => do
  let some eqn ← getUnfoldEqnFor? substrEqLoopName | throwError "no unfolding equation for substrEq's loop"
  liftMetaTactic fun g => do
    let e ← mkConstWithFreshMVarLevels eqn
    let r ← g.rewrite (← g.getType) e
    let g' ← g.replaceTargetEq r.eNew r.eqProof
    return g' :: r.mvarIds

theorem rd_startsWith (t : String) : ("rd-" ++ t).startsWith "rd-" = true := by
  let s : String := String.mk ('r' :: 'd' :: '-' :: t.data)
  have hd : ("rd-" ++ t) = s := by apply String.ext; simp [s, String.data_append]
  rw [hd]
  have hE : s.endPos = ⟨3 + String.utf8ByteSize.go t.data⟩ := by
    show (⟨String.utf8ByteSize.go ('r' :: 'd' :: '-' :: t.data)⟩ : String.Pos) = _
    have : 'r'.utf8Size = 1 := rfl
    have : 'd'.utf8Size = 1 := rfl
    have : '-'.utf8Size = 1 := rfl
    simp [String.utf8ByteSize.go]; omega
  have hn0 : s.next 0 = ⟨1⟩ := rfl
  have hn1 : s.next ⟨1⟩ = ⟨2⟩ := rfl
  have hn2 : s.next ⟨2⟩ = ⟨3⟩ := rfl
  have h0 : (0 : String.Pos) ≠ s.endPos := by rw [hE]; simp [String.Pos.ext_iff]; omega
  have h1 : (⟨1⟩ : String.Pos) ≠ s.endPos := by rw [hE]; simp [String.Pos.ext_iff]; omega
  have h2 : (⟨2⟩ : String.Pos) ≠ s.endPos := by rw [hE]; simp [String.Pos.ext_iff]; omega
  unfold String.startsWith
  have hl : "rd-".length = 3 := rfl
  have hz : ∀ p : String.Pos, ({ } : String.Pos) + p = p := fun p => by simp [String.Pos.ext_iff]
  simp only [String.toSubstring, Substring.take, hl, Substring.nextn, Substring.next, hz]
  simp only [h0, if_false, hn0, Nat.sub_zero, h1, hn1, h2, hn2]
  have hE3 : "rd-".endPos = ⟨3⟩ := rfl
  show Substring.beq _ _ = true
  simp only [Substring.beq, Substring.bsize, hE3, String.substrEq]
  have hle : 0 + 3 ≤ s.endPos.byteIdx := by rw [hE]; show 0 + 3 ≤ 3 + _; omega
  have h3 : Nat.sub 3 0 = 3 := rfl
  simp only [beq_self_eq_true, Bool.true_and, h3, decide_eq_true hle]
  have g0 : s.get { } = 'r' := rfl
  have g1 : s.get ⟨1⟩ = 'd' := rfl
  have g2 : s.get ⟨2⟩ = '-' := rfl
  have r0 : "rd-".get { } = 'r' := rfl
  have r1 : "rd-".get ⟨1⟩ = 'd' := rfl
  have r2 : "rd-".get ⟨2⟩ = '-' := rfl
  have p0 : ({ } : String.Pos) + 'r' = ⟨1⟩ := rfl
  have p1 : (⟨1⟩ : String.Pos) + 'd' = ⟨2⟩ := rfl
  have p2 : (⟨2⟩ : String.Pos) + '-' = ⟨3⟩ := rfl
  unfold_substrEq_loop
  simp only [show (0 : Nat) < 3 from by decide, dite_true, g0, r0, p0, beq_self_eq_true, Bool.true_and,
    show (3 : Nat) ≤ 3 from by decide, decide_true]
  unfold_substrEq_loop
  simp only [show (1 : Nat) < 3 from by decide, dite_true, g1, r1, p1, beq_self_eq_true, Bool.true_and]
  unfold_substrEq_loop
  simp only [show (2 : Nat) < 3 from by decide, dite_true, g2, r2, p2, beq_self_eq_true, Bool.true_and]
  unfold_substrEq_loop
  simp

/-- A qualified name is reserved: no author name is one. -/
theorem reservedName_qualify (k : Nat) (n : String) : reservedName (qualify k n) = true := by
  unfold reservedName qualify
  rw [String.append_assoc, String.append_assoc]
  exact rd_startsWith _

theorem qualify_ne {k : Nat} {n m : String} (h : reservedName m = false) : qualify k n ≠ m := by
  intro he
  have := reservedName_qualify k n
  rw [he, h] at this
  cases this

/-! ## `String.map` on characters -/

theorem pos_add_char (i : String.Pos) (c : Char) : (i + c).byteIdx = i.byteIdx + c.utf8Size := rfl

theorem utf8GetAux_append (A : List Char) (c : Char) (rest : List Char) :
    ∀ i : String.Pos, String.utf8GetAux (A ++ c :: rest) i ⟨i.byteIdx + String.utf8ByteSize.go A⟩ = c := by
  induction A with
  | nil => intro i; simp [String.utf8GetAux, String.utf8ByteSize.go]
  | cons a A ih =>
    intro i
    have ha := Char.utf8Size_pos a
    simp only [List.cons_append, String.utf8GetAux, String.utf8ByteSize.go]
    rw [if_neg (by simp [String.Pos.ext_iff]; omega)]
    have := ih (i + a)
    simp only [pos_add_char] at this
    rw [show i.byteIdx + (String.utf8ByteSize.go A + a.utf8Size) = i.byteIdx + a.utf8Size +
      String.utf8ByteSize.go A by omega]
    exact this

theorem utf8SetAux_append (c' : Char) (A : List Char) (c : Char) (rest : List Char) :
    ∀ i : String.Pos,
      String.utf8SetAux c' (A ++ c :: rest) i ⟨i.byteIdx + String.utf8ByteSize.go A⟩ = A ++ c' :: rest := by
  induction A with
  | nil => intro i; simp [String.utf8SetAux, String.utf8ByteSize.go]
  | cons a A ih =>
    intro i
    have ha := Char.utf8Size_pos a
    simp only [List.cons_append, String.utf8SetAux, String.utf8ByteSize.go]
    rw [if_neg (by simp [String.Pos.ext_iff]; omega)]
    have := ih (i + a)
    simp only [pos_add_char] at this
    rw [show i.byteIdx + (String.utf8ByteSize.go A + a.utf8Size) = i.byteIdx + a.utf8Size +
      String.utf8ByteSize.go A by omega]
    rw [this]

theorem utf8ByteSize_go_append (l l' : List Char) :
    String.utf8ByteSize.go (l ++ l') = String.utf8ByteSize.go l + String.utf8ByteSize.go l' := by
  induction l with
  | nil => simp [String.utf8ByteSize.go]
  | cons c l ih => simp [String.utf8ByteSize.go, ih]; omega

theorem mapAux_data (f : Char → Char) : ∀ (post A : List Char) (s : String),
    s.data = A ++ post → (String.mapAux f ⟨String.utf8ByteSize.go A⟩ s).data = A ++ post.map f
  | [], A, s, hs => by
    unfold String.mapAux
    rw [dif_pos]
    · simpa using hs
    · simp [String.atEnd, String.utf8ByteSize, hs]
  | c :: post, A, s, hs => by
    obtain ⟨l⟩ := s
    simp only at hs
    subst hs
    unfold String.mapAux
    have hc := Char.utf8Size_pos c
    rw [dif_neg]
    · have hg : String.get ⟨A ++ c :: post⟩ ⟨String.utf8ByteSize.go A⟩ = c := by
        have := utf8GetAux_append A c post 0
        simpa using this
      simp only [hg]
      have hset : String.set ⟨A ++ c :: post⟩ ⟨String.utf8ByteSize.go A⟩ (f c) = ⟨A ++ f c :: post⟩ := by
        have := utf8SetAux_append (f c) A c post 0
        simp only [String.set]
        simpa using this
      rw [hset]
      have hnext : String.next ⟨A ++ f c :: post⟩ ⟨String.utf8ByteSize.go A⟩ =
          ⟨String.utf8ByteSize.go (A ++ [f c])⟩ := by
        have := utf8GetAux_append A (f c) post 0
        simp only [String.next, String.get, String.Pos.ext_iff, pos_add_char]
        simp at this
        rw [this, utf8ByteSize_go_append]
        simp [String.utf8ByteSize.go]
      rw [hnext]
      have := mapAux_data f post (A ++ [f c]) ⟨A ++ f c :: post⟩ (by simp)
      rw [this]
      simp
    · simp only [String.atEnd, String.utf8ByteSize, utf8ByteSize_go_append, String.utf8ByteSize.go]
      simp; omega

theorem map_data (f : Char → Char) (s : String) : (s.map f).data = s.data.map f := by
  have := mapAux_data f s.data [] s (by simp)
  simpa [String.map, String.utf8ByteSize.go] using this

/-! ## A soft name has no `__` -/

theorem splitOnAux_length (s sep : String) :
    ∀ (b i j : String.Pos) (r : List String), r.length + 1 ≤ (s.splitOnAux sep b i j r).length := by
  intro b i j r
  induction b, i, j, r using String.splitOnAux.induct s sep with
  | case1 b i j r h => rw [String.splitOnAux.eq_1, if_pos h]; simp
  | case2 b i j r h hg i' j' hj ih =>
    rw [String.splitOnAux.eq_1, if_neg h, if_pos hg]
    have e1 : i' = s.next i := rfl
    have e2 : j' = sep.next j := rfl
    rw [e2] at hj
    rw [e1, e2] at ih
    dsimp only
    rw [if_pos hj]
    simp only [List.length_cons] at ih; omega
  | case3 b i j r h hg i' j' hj ih =>
    rw [String.splitOnAux.eq_1, if_neg h, if_pos hg]
    have e1 : i' = s.next i := rfl
    have e2 : j' = sep.next j := rfl
    rw [e2] at hj
    rw [e1, e2] at ih
    dsimp only
    rw [if_neg hj]
    exact ih
  | case4 b i j r h hg ih => rw [String.splitOnAux.eq_1, if_neg h, if_neg hg]; exact ih

/-- In a string of one-byte characters, the byte position `k` holds the `k`-th character. -/
theorem utf8GetAux_ascii : ∀ (l : List Char), (∀ c ∈ l, c.utf8Size = 1) → ∀ (a k : Nat) (hk : k < l.length),
    String.utf8GetAux l ⟨a⟩ ⟨a + k⟩ = l[k]
  | [], _, _, _, hk => by simp at hk
  | c :: l, hl, a, k, hk => by
    simp only [String.utf8GetAux]
    cases k with
    | zero => simp
    | succ k =>
      rw [if_neg (by simp [String.Pos.ext_iff])]
      have hc : c.utf8Size = 1 := hl c (by simp)
      have := utf8GetAux_ascii l (fun d hd => hl d (by simp [hd])) (a + 1) k (by simp at hk; omega)
      have hp : (⟨a⟩ : String.Pos) + c = ⟨a + 1⟩ := by simp [String.Pos.ext_iff, hc]
      rw [hp, show a + (k + 1) = a + 1 + k by omega, this]
      simp

theorem utf8ByteSize_go_ascii : ∀ (l : List Char), (∀ c ∈ l, c.utf8Size = 1) → String.utf8ByteSize.go l = l.length
  | [], _ => rfl
  | c :: l, hl => by
    simp only [String.utf8ByteSize.go, List.length_cons]
    rw [utf8ByteSize_go_ascii l (fun d hd => hl d (by simp [hd])), hl c (by simp)]

/-- A string of one-byte characters with `__` at index `p` splits on `__` into at least two pieces. -/
theorem splitOn_dunder (s : String) (hs : ∀ c ∈ s.data, c.utf8Size = 1) (p : Nat)
    (hp : p + 1 < s.data.length) (h0 : s.data[p] = '_') (h1 : s.data[p + 1] = '_') :
    2 ≤ (s.splitOn "__").length := by
  have hE : s.endPos.byteIdx = s.data.length := utf8ByteSize_go_ascii s.data hs
  have hget : ∀ k (hk : k < s.data.length), s.get ⟨k⟩ = s.data[k] := by
    intro k hk
    have := utf8GetAux_ascii s.data hs 0 k hk
    simp only [Nat.zero_add] at this
    exact this
  have hnext : ∀ k, k < s.data.length → s.next ⟨k⟩ = ⟨k + 1⟩ := by
    intro k hk
    simp only [String.next, String.Pos.ext_iff, pos_add_char, hget k hk, hs _ (List.getElem_mem hk)]
  have key : ∀ (b i j : String.Pos) (r : List String), j.byteIdx ≤ 1 → j.byteIdx ≤ i.byteIdx →
      i.byteIdx - j.byteIdx ≤ p → r.length + 2 ≤ (s.splitOnAux "__" b i j r).length := by
    intro b i j r
    induction b, i, j, r using String.splitOnAux.induct s "__" with
    | case1 b i j r h =>
      intro hj hji hip
      have h' : s.utf8ByteSize ≤ i.byteIdx := by simpa [String.atEnd] using h
      have : s.utf8ByteSize = s.data.length := hE
      rw [this] at h'
      omega
    | case2 b i j r h hg i' j' hj ih =>
      intro _ _ _
      rw [String.splitOnAux.eq_1, if_neg h, if_pos hg]
      have e2 : j' = "__".next j := rfl
      rw [e2] at hj
      dsimp only
      rw [if_pos hj]
      have := splitOnAux_length s "__" (s.next i) (s.next i) 0 (s.extract b (s.next i - "__".next j) :: r)
      simp only [List.length_cons] at this; omega
    | case3 b i j r h hg i' j' hj ih =>
      intro hj1 hji hip
      rw [String.splitOnAux.eq_1, if_neg h, if_pos hg]
      have e1 : i' = s.next i := rfl
      have e2 : j' = "__".next j := rfl
      rw [e2] at hj
      rw [e1, e2] at ih
      dsimp only
      rw [if_neg hj]
      have hi : i.byteIdx < s.data.length := by
        have h' : ¬ s.utf8ByteSize ≤ i.byteIdx := by simpa [String.atEnd] using h
        have : s.utf8ByteSize = s.data.length := hE
        rw [this] at h'; omega
      have hj0 : j.byteIdx = 0 := by
        rcases Nat.lt_or_ge j.byteIdx 1 with h' | h'
        · omega
        · exfalso; apply hj
          have : j = ⟨1⟩ := by simp [String.Pos.ext_iff]; omega
          subst this; rfl
      have hjn : "__".next j = ⟨1⟩ := by
        have : j = ⟨0⟩ := by simp [String.Pos.ext_iff]; omega
        subst this; rfl
      have hin : s.next i = ⟨i.byteIdx + 1⟩ := hnext i.byteIdx hi
      rw [hin, hjn] at ih ⊢
      exact ih (by simp) (by simp) (by simp; omega)
    | case4 b i j r h hg ih =>
      intro hj1 hji hip
      rw [String.splitOnAux.eq_1, if_neg h, if_neg hg]
      have hi : i.byteIdx < s.data.length := by
        have h' : ¬ s.utf8ByteSize ≤ i.byteIdx := by simpa [String.atEnd] using h
        have : s.utf8ByteSize = s.data.length := hE
        rw [this] at h'; omega
      have hsep : "__".get j = '_' := by
        rcases Nat.lt_or_ge j.byteIdx 1 with h' | h'
        · have : j = ⟨0⟩ := by simp [String.Pos.ext_iff]; omega
          subst this; rfl
        · have : j = ⟨1⟩ := by simp [String.Pos.ext_iff]; omega
          subst this; rfl
      have hne : s.data[i.byteIdx] ≠ '_' := by
        intro he; apply hg; rw [hget _ hi, he, hsep]; rfl
      have hlt : i.byteIdx - j.byteIdx < p := by
        rcases Nat.lt_or_ge (i.byteIdx - j.byteIdx) p with h' | h'
        · exact h'
        · exfalso
          rcases Nat.lt_or_ge j.byteIdx 1 with hj' | hj'
          · have : i.byteIdx = p := by omega
            exact hne (by simp only [this]; exact h0)
          · have : i.byteIdx = p + 1 := by omega
            exact hne (by simp only [this]; exact h1)
      have hn : s.next (i - j) = ⟨i.byteIdx - j.byteIdx + 1⟩ := hnext _ (by omega)
      rw [hn] at ih ⊢
      exact ih (by simp) (by simp) (by simp; omega)
  have := key 0 0 0 [] (by simp) (by simp) (by simp)
  simpa [String.splitOn] using this

theorem ascii_size {c : Char} (h : c ≤ 'z') : c.utf8Size = 1 := by
  unfold Char.utf8Size
  have h1 : c.val.toNat ≤ 122 := by
    have : c.val ≤ 122 := h
    exact UInt32.le_iff_toNat_le.mp this
  rw [if_pos]
  exact UInt32.le_iff_toNat_le.mpr (by simp; omega)

/-- A valid soft name starts with a letter and has no two consecutive `_`. -/
theorem validSoftName_data {π : String} (h : VE.SoftNorms.validSoftName π = true) :
    (∃ c l, π.data = c :: l ∧ 'a' ≤ c ∧ c ≤ 'z') ∧ ∀ (u v : List Char), π.data ≠ u ++ '_' :: '_' :: v := by
  unfold VE.SoftNorms.validSoftName at h
  split at h
  · cases h
  · rename_i first rest hl
    simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, Bool.or_eq_true, beq_iff_eq,
      Bool.not_eq_true'] at h
    obtain ⟨⟨⟨⟨hf1, hf2⟩, hr⟩, _⟩, hd⟩ := h
    have hdata : π.data = first :: rest := hl
    refine ⟨⟨first, rest, hdata, hf1, hf2⟩, fun u v he => ?_⟩
    have hascii : ∀ c ∈ π.data, c.utf8Size = 1 := by
      intro c hc
      rw [hdata] at hc
      rcases List.mem_cons.mp hc with rfl | hc
      · exact ascii_size hf2
      · rcases hr c hc with (⟨_, h2⟩ | ⟨_, h2⟩) | h2
        · exact ascii_size h2
        · exact ascii_size (Char.le_trans h2 (by decide))
        · subst h2; rfl
    have hlen : u.length + 1 < π.data.length := by rw [he]; simp
    have := splitOn_dunder π hascii u.length hlen (by simp [he]) (by simp [he])
    simp only [VE.SoftNorms.containsDunder, gt_iff_lt, decide_eq_false_iff_not, Nat.not_lt] at hd
    omega

/-! ## Decision predicate names -/

/-- A W1 rule name has no `_`. -/
theorem ruleName_no_underscore {n : String} (h : VE.Norms.ruleName n = true) : ∀ c ∈ n.data, c ≠ '_' := by
  unfold VE.Norms.ruleName at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨_, h⟩ := h
  have hd : n.toList = n.data := rfl
  rw [hd] at h
  intro c hc
  split at h
  · rename_i c0 cs he
    rw [he] at hc
    simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, Bool.or_eq_true, beq_iff_eq] at h
    rcases List.mem_cons.mp hc with rfl | hc
    · intro e; subst e; exact absurd h.1.1 (by decide)
    · rcases h.2 c hc with (⟨h1, _⟩ | h1) | h1
      · intro e; subst e; exact absurd h1 (by decide)
      · intro e; subst e; exact absurd h1 (by decide)
      · intro e; subst e; exact absurd h1 (by decide)
  · cases h

def keyChar (c : Char) : Char := if c == '-' then '_' else c

theorem ruleKey_data (n : String) : (VE.SoftNorms.ruleKey n).data = n.data.map keyChar := map_data _ n

theorem keyChar_inj {c d : Char} (hc : c ≠ '_') (hd : d ≠ '_') (h : keyChar c = keyChar d) : c = d := by
  unfold keyChar at h
  by_cases h1 : c = '-' <;> by_cases h2 : d = '-'
  · rw [h1, h2]
  · simp [h1, h2] at h; exact absurd h.symm hd
  · simp [h1, h2] at h; exact absurd h hc
  · simpa [h1, h2] using h

theorem map_keyChar_inj : ∀ {l l' : List Char}, (∀ c ∈ l, c ≠ '_') → (∀ c ∈ l', c ≠ '_') →
    l.map keyChar = l'.map keyChar → l = l'
  | [], [], _, _, _ => rfl
  | [], _ :: _, _, _, h => by simp at h
  | _ :: _, [], _, _, h => by simp at h
  | c :: l, d :: l', hl, hl', h => by
    simp only [List.map_cons, List.cons.injEq] at h
    rw [keyChar_inj (hl c (by simp)) (hl' d (by simp)) h.1,
      map_keyChar_inj (fun x hx => hl x (by simp [hx])) (fun x hx => hl' x (by simp [hx])) h.2]

theorem ruleKey_inj {a b : String} (ha : VE.Norms.ruleName a = true) (hb : VE.Norms.ruleName b = true)
    (h : VE.SoftNorms.ruleKey a = VE.SoftNorms.ruleKey b) : a = b := by
  apply String.ext
  apply map_keyChar_inj (ruleName_no_underscore ha) (ruleName_no_underscore hb)
  rw [← ruleKey_data, ← ruleKey_data, h]

theorem exceptedName_inj {M N : VE.SoftNorms.SoftNode} (hM : VE.Norms.ruleName M.name = true)
    (hN : VE.Norms.ruleName N.name = true) (h : VE.SoftNorms.exceptedName M = VE.SoftNorms.exceptedName N) :
    M.name = N.name := by
  apply ruleKey_inj hM hN
  have := congrArg String.data h
  simp only [VE.SoftNorms.exceptedName, String.data_append] at this
  exact String.ext (List.append_cancel_left this)

/-- Two lists that end `__` followed by a word that starts with no `_` and has no `__` split there alike. -/
theorem split_dunder : ∀ (k k' p p' : List Char),
    (∀ u v, p ≠ u ++ '_' :: '_' :: v) → (∀ u v, p' ≠ u ++ '_' :: '_' :: v) →
    p.head? ≠ some '_' → p'.head? ≠ some '_' →
    k ++ '_' :: '_' :: p = k' ++ '_' :: '_' :: p' → k = k' ∧ p = p'
  | [], [], p, p', _, _, _, _, h => by simpa using h
  | [], c :: k', p, p', hp, _, h0, _, h => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h
    obtain ⟨_, h⟩ := h
    cases k' with
    | nil => simp at h; obtain ⟨_, rfl⟩ := h; simp at h0
    | cons d k'' =>
      simp only [List.cons_append, List.cons.injEq] at h
      obtain ⟨_, rfl⟩ := h
      exact absurd rfl (hp k'' p')
  | c :: k, [], p, p', _, hp', _, h0', h => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h
    obtain ⟨_, h⟩ := h
    cases k with
    | nil => simp at h; obtain ⟨_, rfl⟩ := h; simp at h0'
    | cons d k'' =>
      simp only [List.cons_append, List.cons.injEq] at h
      obtain ⟨_, h⟩ := h
      exact absurd h.symm (hp' k'' p)
  | c :: k, c' :: k', p, p', hp, hp', h0, h0', h => by
    simp only [List.cons_append, List.cons.injEq] at h
    obtain ⟨rfl, h⟩ := h
    obtain ⟨h1, h2⟩ := split_dunder k k' p p' hp hp' h0 h0' h
    exact ⟨by rw [h1], h2⟩

theorem offName_inj {M N : VE.SoftNorms.SoftNode} {π π' : String} (hM : VE.Norms.ruleName M.name = true)
    (hN : VE.Norms.ruleName N.name = true) (hπ : VE.SoftNorms.validSoftName π = true)
    (hπ' : VE.SoftNorms.validSoftName π' = true) (h : VE.SoftNorms.offName M π = VE.SoftNorms.offName N π') :
    M.name = N.name ∧ π = π' := by
  have hd := congrArg String.data h
  simp only [VE.SoftNorms.offName, String.data_append, List.append_assoc] at hd
  have hd' := List.append_cancel_left hd
  obtain ⟨⟨c, l, hc, hc1, _⟩, hp⟩ := validSoftName_data hπ
  obtain ⟨⟨c', l', hc', hc1', _⟩, hp'⟩ := validSoftName_data hπ'
  have h0 : π.data.head? ≠ some '_' := by
    rw [hc]; simp only [List.head?_cons, ne_eq, Option.some.injEq]; intro e; subst e; exact absurd hc1 (by decide)
  have h0' : π'.data.head? ≠ some '_' := by
    rw [hc']; simp only [List.head?_cons, ne_eq, Option.some.injEq]; intro e; subst e; exact absurd hc1' (by decide)
  simp only [List.cons_append, List.nil_append] at hd'
  obtain ⟨h1, h2⟩ := split_dunder _ _ _ _ hp hp' h0 h0' hd'
  exact ⟨ruleKey_inj hM hN (String.ext h1), String.ext h2⟩

theorem exceptedName_ne_offName (M N : VE.SoftNorms.SoftNode) (π : String) :
    VE.SoftNorms.exceptedName M ≠ VE.SoftNorms.offName N π := by
  intro h
  have := congrArg (fun s => s.data[6]?) h
  simp [VE.SoftNorms.exceptedName, VE.SoftNorms.offName, String.data_append] at this

theorem exceptedName_ne_outweighsName (M : VE.SoftNorms.SoftNode) (a L H : String) :
    VE.SoftNorms.exceptedName M ≠ VE.SoftNorms.outweighsName a L H := by
  intro h
  have := congrArg (fun s => s.data[7]?) h
  simp [VE.SoftNorms.exceptedName, VE.SoftNorms.outweighsName, String.data_append] at this

theorem offName_ne_outweighsName (N : VE.SoftNorms.SoftNode) (π a L H : String) :
    VE.SoftNorms.offName N π ≠ VE.SoftNorms.outweighsName a L H := by
  intro h
  have := congrArg (fun s => s.data[7]?) h
  simp [VE.SoftNorms.offName, VE.SoftNorms.outweighsName, String.data_append] at this

end VE.Readings
