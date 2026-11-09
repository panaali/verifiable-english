import VE.Commands.Steps
import VE.Commands.SplitOnLemmas
import VE.Question.Strings
import VE.Commands.StepsExamples

/-! Section 7's `preposed_eq` and `readStep_conservative` (docs/spec/commands-imperatives.md; item ci-3b), proved over
the `String.splitOn` lemmas of `VE.Commands.SplitOnLemmas`. `If <c>, <x>.` takes `<x>` from a split at `, `, so `<x>`
holds no `, then ` and the condition-scope refusal never fires. A merged wording keeps its reading: `hs` leaves no
sequence (`readStep_core`), and the act linter leaves no `If ` or `Then ` shape (`one_begins`): a read command's act
begins `{0} <verb>`, its verb is no clause word, and `checkTemplates` keeps a slot from joining it. -/

namespace VE.Commands

open VE.SpeechActs (Scope)
open VE.SpeechActs.Wire (SpeechEnvironment asciiSpace)
open VE.EnglishGrammar (Env Lexicon)
open VE.Readings (eq_append_of_startsWith)
open VE.Commands.SplitOn (splitOn_two splitOn_free)

/-! ### Strings -/

/-- The trimmed wording is a run of the wording's characters. -/
theorem trimmed_infix (y : String) : (trimmed y).data <:+: y.data := by
  have h1 : (y.data.dropWhile asciiSpace).reverse.dropWhile asciiSpace <:+ (y.data.dropWhile asciiSpace).reverse :=
    List.dropWhile_suffix _
  have h2 : ((y.data.dropWhile asciiSpace).reverse.dropWhile asciiSpace).reverse <+: y.data.dropWhile asciiSpace := by
    simpa using List.reverse_prefix.2 h1
  exact h2.isInfix.trans (List.dropWhile_suffix _).isInfix

/-- An occurrence of `l ++ u` with `u` non-empty in `x ++ [d]` puts `l` inside `x`. -/
theorem infix_of_cut {l u x : List Char} {d : Char} (hu : u ≠ []) (h : l ++ u <:+: x ++ [d]) : l <:+: x := by
  obtain ⟨p, q, he⟩ := h
  have hne : u ++ q ≠ [] := by simp [hu]
  refine ⟨p, (u ++ q).dropLast, ?_⟩
  have := congrArg List.dropLast he
  rw [List.dropLast_concat, show p ++ (l ++ u) ++ q = p ++ l ++ (u ++ q) by simp,
    List.dropLast_append_of_ne_nil hne] at this
  exact this

theorem not_if_then {body : String} (h1 : body.startsWith "If " = true) : body.startsWith "Then " = false := by
  obtain ⟨u, rfl⟩ := eq_append_of_startsWith (by decide) h1
  cases h2 : ("If " ++ u).startsWith "Then " with
  | false => rfl
  | true =>
    obtain ⟨v, hv⟩ := eq_append_of_startsWith (by decide) h2
    have := congrArg (fun z : String => z.data.head?) hv
    simp [String.data_append] at this

/-- `If <c>, <x>.` takes `<x>` from the split of the body after `If ` at `, `. -/
theorem shapes_preposed {s c x : String} (h : shapes s = [.preposed c x]) :
    x ∈ (((trimmed s).dropRight 1).drop 3).splitOn ", " := by
  unfold shapes at h
  dsimp only at h
  split at h
  · simp at h
  generalize (trimmed s).dropRight 1 = body at h ⊢
  split at h
  · simp at h
  by_cases hi : body.startsWith "If " = true
  · rw [if_pos hi, if_neg (by simp [not_if_then hi]), if_neg (by simp [hi])] at h
    simp only [List.append_nil] at h
    generalize (body.drop 3).splitOn ", " = ws at h ⊢
    have hl := congrArg List.length h
    simp only [List.length_map, List.length_range, List.length_singleton] at hl
    rw [show ws.length - 1 = 1 by omega, show List.range 1 = [0] from rfl] at h
    simp only [List.map_cons, List.map_nil, List.cons.injEq, Shape.preposed.injEq, and_true] at h
    match ws, hl with
    | [_, _], _ => rw [← h.2]; exact .tail _ (.head _)
  · rw [if_neg hi] at h
    split at h <;> split at h <;> simp at h

/-- `<x>` of `If <c>, <x>.` holds no `, then `, so its step never has the condition-scope refusal. -/
theorem hasThen_preposed {s c x : String} (h : shapes s = [.preposed c x]) : hasThen (x ++ ".") = false := by
  have hx := splitOn_free _ ", " (by decide) x (shapes_preposed h)
  unfold hasThen
  apply decide_eq_false
  intro hlen
  have hi := (splitOn_two _ ", then " (by decide)).1 hlen
  have hi' : ", ".data ++ "then ".data <:+: x.data ++ ['.'] := by
    simpa [String.data_append] using hi.trans (trimmed_infix (x ++ "."))
  exact hx (infix_of_cut (by decide) hi')

/-! ## The act linter's half of `readStep_conservative` -/

open VE.SpeechActs.Wire (attached slotsApart wordBreak)
open VE.EnglishGrammar (fillHoles)
open VE.Norms.Wire (pyWhitespace)

/-! ### Characters -/

theorem toNat_ofNat {n : Nat} (h : n < 55296) : (Char.ofNat n).toNat = n := by
  unfold Char.ofNat; rw [dif_pos (Or.inl h)]; simp [Char.ofNatAux, Char.toNat, UInt32.toNat_ofNatLT]

theorem toLower_eq {c x : Char} (h : c.toLower = x) :
    c = x ∨ (65 ≤ c.toNat ∧ c.toNat ≤ 90 ∧ c.toNat + 32 = x.toNat) := by
  unfold Char.toLower at h
  dsimp only at h
  split at h
  · rename_i hu; exact .inr ⟨hu.1, hu.2, by rw [← h, toNat_ofNat (by omega)]⟩
  · exact .inl h

/-- Lower case moves only `A`-`Z`: a character that lowers to ` ` or `{` is that character. -/
theorem toLower_fixed {c x : Char} (h : c.toLower = x) (hx : x = ' ' ∨ x = '{') : c = x := by
  rcases toLower_eq h with h | ⟨h1, h2, h3⟩
  · exact h
  · rcases hx with rfl | rfl <;> simp at h3 <;> omega

/-- A character that lowers to a letter of `if` or `then` joins a slot written next to it. -/
theorem toLower_attached {c x : Char} (h : c.toLower = x) (hx : x ∈ ['i', 'f', 't', 'h', 'e', 'n']) :
    attached c = true := by
  have hc : c ∈ ['i', 'f', 't', 'h', 'e', 'n', 'I', 'F', 'T', 'H', 'E', 'N'] := by
    rcases toLower_eq h with rfl | ⟨_, _, h3⟩
    · simp at hx ⊢; rcases hx with h | h | h | h | h | h <;> simp [h]
    · have hc : c = Char.ofNat (x.toNat - 32) := by rw [← Char.ofNat_toNat c]; congr 1; omega
      subst hc
      simp at hx; rcases hx with rfl | rfl | rfl | rfl | rfl | rfl <;> decide
  have hw : wordBreak c = false := by
    cases h : wordBreak c with
    | false => rfl
    | true =>
      have := VE.Acts.Lexical.contains_mem (by simp at hc; rcases hc with h|h|h|h|h|h|h|h|h|h|h|h <;> subst h <;> decide) h
      simp at hc; rcases hc with h|h|h|h|h|h|h|h|h|h|h|h <;> subst h <;> revert this <;> decide
  simp at hc
  unfold attached
  rw [hw]
  rcases hc with h|h|h|h|h|h|h|h|h|h|h|h <;> subst h <;> decide

/-! ### `fillHoles` and `slotsApart` before a `{` -/

theorem fill_copy (f : Nat → String) : ∀ (u l : List Char) (n : Nat) (hs : List Nat) (out : List Char),
    '{' ∉ u → u.length ≤ n → fillHoles.go f n (u ++ l) hs out = fillHoles.go f (n - u.length) l hs (u.reverse ++ out)
  | [], _, _, _, _, _, _ => by simp
  | c :: u, l, n + 1, hs, out, hu, hn => by
    simp only [List.mem_cons, not_or] at hu
    rw [List.cons_append, fillHoles.go, if_neg (by simpa using Ne.symm hu.1),
      fill_copy f u l n hs (c :: out) hu.2 (by simp at hn; omega)]
    simp

theorem fill_prefix (f : Nat → String) : ∀ (n : Nat) (l : List Char) (hs : List Nat) (out : List Char),
    ∃ z, (fillHoles.go f n l hs out).2 = out.reverse ++ z
  | 0, _, _, _ => ⟨[], by simp [fillHoles.go]⟩
  | _ + 1, [], _, _ => ⟨[], by simp [fillHoles.go]⟩
  | n + 1, c :: cs, hs, out => by
    rw [fillHoles.go]
    dsimp only
    split
    · split
      · split
        · obtain ⟨z, hz⟩ := fill_prefix f n cs hs (c :: out); exact ⟨c :: z, by rw [hz]; simp⟩
        · obtain ⟨z, hz⟩ := fill_prefix f n _ (_ :: hs) ((f _).toList.reverse ++ out)
          exact ⟨_, by rw [hz, List.reverse_append, List.reverse_reverse, List.append_assoc]⟩
      · obtain ⟨z, hz⟩ := fill_prefix f n cs hs (c :: out); exact ⟨c :: z, by rw [hz]; simp⟩
    · obtain ⟨z, hz⟩ := fill_prefix f n cs hs (c :: out); exact ⟨c :: z, by rw [hz]; simp⟩

theorem fill_step (f : Nat → String) {n : Nat} {c : Char} {l : List Char} {hs : List Nat} {out : List Char}
    (hc : c ≠ '{') : fillHoles.go f (n + 1) (c :: l) hs out = fillHoles.go f n l hs (c :: out) := by
  rw [fillHoles.go, if_neg (by simpa using hc)]

theorem fill_nil (f : Nat → String) (n : Nat) (hs : List Nat) (out : List Char) :
    (fillHoles.go f n [] hs out).2 = out.reverse := by
  cases n <;> simp [fillHoles.go]

theorem slots_step {n : Nat} {prev c : Char} {l : List Char} (hc : c ≠ '{') :
    slotsApart (n + 1) prev (c :: l) = slotsApart n c l := by
  conv => lhs; unfold slotsApart
  split <;> simp_all

theorem slots_copy : ∀ (u l : List Char) (n : Nat) (prev : Char), '{' ∉ u → u.length ≤ n →
    slotsApart n prev (u ++ l) = slotsApart (n - u.length) (u.getLast?.getD prev) l
  | [], _, _, _, _, _ => by simp
  | c :: u, l, n + 1, prev, hu, hn => by
    simp only [List.mem_cons, not_or] at hu
    rw [List.cons_append, slots_step (Ne.symm hu.1), slots_copy u l n c hu.2 (by simp at hn; omega)]
    cases u with
    | nil => simp
    | cons d u => simp only [List.getLast?_cons_cons, List.length_cons]; cases h : (d :: u).getLast? <;> simp_all

/-- The act's verb `w` (no whitespace, not a slot), then `R` (nothing, or a space and more): when the filled text
read in lower case begins with `T ++ " "`, `T` a word of the letters of `if` and `then`, the verb is `T` in some
case. A slot inside the verb would need an attached letter before it, which `slotsApart` refuses. -/
theorem filled_word (f : Nat → String) {T w R z : List Char} {N n : Nat}
    (hT : ∀ x ∈ T, x ∈ ['i', 'f', 't', 'h', 'e', 'n']) (hw : ∀ c ∈ w, pyWhitespace c = false)
    (hw0 : w.head? ≠ some '{') (hR : R = [] ∨ R.head? = some ' ') (hN : (w ++ R).length < N)
    (hn : (w ++ R).length < n) (hsl : slotsApart n ' ' (w ++ R) = true)
    (ht : ((fillHoles.go f N (w ++ R) [] []).2).map Char.toLower = T ++ ' ' :: z) :
    w.map Char.toLower = T := by
  have hsp : ∀ c ∈ w, c ≠ ' ' := fun c hc he => by have := hw c hc; subst he; simp [pyWhitespace] at this
  generalize hP : w.takeWhile (· != '{') = P
  generalize hQ : w.dropWhile (· != '{') = Q
  have hwPQ : w = P ++ Q := by rw [← hP, ← hQ, List.takeWhile_append_dropWhile]
  have hPb : '{' ∉ P := fun hm => by
    have := List.all_eq_true.1 (hP ▸ List.all_takeWhile (p := (· != '{')) (l := w)) _ hm; simp at this
  have hPw : P.length ≤ w.length := by rw [hwPQ]; simp
  rw [hwPQ, List.append_assoc, fill_copy f P _ N [] [] hPb (by simp at hN; omega)] at ht
  rw [hwPQ, List.append_assoc, slots_copy P _ n ' ' hPb (by simp at hn; omega)] at hsl
  obtain ⟨z1, hz1⟩ := fill_prefix f (N - P.length) (Q ++ R) [] P.reverse
  rw [List.append_nil, hz1, List.reverse_reverse, List.map_append] at ht
  -- the lowered `P` is a prefix of `T`: a longer one would hold a space
  obtain ⟨a', hTa, hza⟩ : ∃ a', T = P.map Char.toLower ++ a' ∧ z1.map Char.toLower = a' ++ ' ' :: z := by
    rcases List.append_eq_append_iff.1 ht with ⟨a', h1, h2⟩ | ⟨c', h1, h2⟩
    · exact ⟨a', h1, h2⟩
    · cases c' with
      | nil => exact ⟨[], by simpa using h1.symm, by simpa using h2.symm⟩
      | cons c0 c' =>
        simp only [List.cons_append, List.cons.injEq] at h2
        have hm : c0 ∈ P.map Char.toLower := by rw [h1]; simp
        obtain ⟨c, hc, hcl⟩ := List.mem_map.1 hm
        have h0 : c0 = ' ' := h2.1.symm
        exact absurd ((toLower_fixed hcl (.inl h0)).trans h0) (hsp c (hwPQ ▸ List.mem_append_left _ hc))
  -- the first lowered character after `P`: a letter of `T` or the space
  have hy : ∀ y, z1.head? = some y → y.toLower ∈ ['i', 'f', 't', 'h', 'e', 'n'] ∨ y.toLower = ' ' := by
    intro y hy
    cases z1 with
    | nil => cases hy
    | cons y' _ =>
      simp only [List.head?_cons, Option.some.injEq] at hy; subst hy
      simp only [List.map_cons] at hza
      cases a' with
      | nil => exact .inr (List.cons.inj hza).1
      | cons x _ => exact .inl ((List.cons.inj hza).1 ▸ hT x (by rw [hTa]; simp))
  cases Q with
  | nil =>
    rw [List.append_nil] at hwPQ
    subst hwPQ
    rcases hR with rfl | hR
    · rw [List.nil_append, fill_nil] at hz1; simp at hz1; subst hz1; simp at hza
    · obtain ⟨R', rfl⟩ : ∃ R', R = ' ' :: R' := by cases R <;> simp_all
      obtain ⟨m, hm⟩ : ∃ m, N - w.length = m + 1 := ⟨N - w.length - 1, by simp at hN; omega⟩
      rw [List.nil_append, hm, fill_step f (by decide)] at hz1
      obtain ⟨z2, hz2⟩ := fill_prefix f m R' [] (' ' :: w.reverse)
      rw [hz2] at hz1
      simp only [List.reverse_cons, List.reverse_reverse, List.append_assoc, List.singleton_append,
        List.append_cancel_left_eq] at hz1
      cases a' with
      | nil => simpa using hTa.symm
      | cons x _ =>
        subst hz1
        simp only [List.map_cons, List.cons_append, List.cons.injEq] at hza
        have := hT x (by rw [hTa]; simp)
        rw [← hza.1] at this; exact absurd this (by decide)
  | cons q Q' =>
    have hq : q = '{' := by
      have := List.head?_dropWhile_not (· != '{') w
      rw [hQ] at this; simpa using this
    subst hq
    have hP0 : P ≠ [] := by rintro rfl; simp [hwPQ] at hw0
    obtain ⟨m, hm⟩ : ∃ m, N - P.length = m + 1 := ⟨N - P.length - 1, by simp [hwPQ] at hN; omega⟩
    obtain ⟨k, hk⟩ : ∃ k, n - P.length = k + 1 := ⟨n - P.length - 1, by simp [hwPQ] at hn; omega⟩
    rw [List.cons_append, hm] at hz1
    rw [List.cons_append, hk] at hsl
    by_cases hslot : (Q' ++ R).takeWhile Char.isDigit ≠ [] ∧
        ∃ rest, (Q' ++ R).drop ((Q' ++ R).takeWhile Char.isDigit).length = '}' :: rest
    · obtain ⟨hds, rest, hrest⟩ := hslot
      unfold slotsApart at hsl
      simp only [hrest, List.isEmpty_iff, hds, if_false, Bool.and_eq_true, Bool.not_eq_true'] at hsl
      obtain ⟨x, hx⟩ : ∃ x, P.getLast? = some x := by cases h : P.getLast? <;> simp_all
      have hxm : x.toLower ∈ T := by
        rw [hTa]; exact List.mem_append_left _ (List.mem_map_of_mem (List.mem_of_getLast? hx))
      have := toLower_attached rfl (hT _ hxm)
      rw [hx] at hsl; simp_all
    · have hgo : fillHoles.go f (m + 1) ('{' :: (Q' ++ R)) [] P.reverse =
          fillHoles.go f m (Q' ++ R) [] ('{' :: P.reverse) := by
        rw [fillHoles.go]; dsimp only; rw [if_pos (by decide)]
        split
        · split
          · rfl
          · rename_i h; exact absurd ⟨by simpa using h, _, ‹_›⟩ hslot
        · rfl
      rw [hgo] at hz1
      obtain ⟨z2, hz2⟩ := fill_prefix f m (Q' ++ R) [] ('{' :: P.reverse)
      rw [hz2] at hz1
      simp only [List.reverse_cons, List.reverse_reverse, List.append_assoc, List.singleton_append,
        List.append_cancel_left_eq] at hz1
      exact absurd (hy '{' (by rw [← hz1]; rfl)) (by decide)

/-! ### The act's words -/

open VE.Norms.Wire (words)
open VE.SpeechActs.Wire (actVerb surfaceWords asciiSpace)

theorem words_facts {z w : String} (h : w ∈ words z) : w ≠ "" ∧ ∀ c ∈ w.data, pyWhitespace c = false := by
  unfold words at h
  rw [List.mem_filter, VE.Acts.Lexical.split_data] at h
  obtain ⟨hm, hne⟩ := h
  obtain ⟨v, hv, rfl⟩ := List.mem_map.1 hm
  exact ⟨by simpa using hne, fun c hc => (VE.Acts.Lexical.mem_splitL hv c hc).2⟩

theorem space_inj : ∀ {u u' X Y : List Char}, ' ' ∉ u → ' ' ∉ u' → u ++ ' ' :: X = u' ++ ' ' :: Y →
    u = u' ∧ X = Y
  | [], [], _, _, _, _, h => by simpa using h
  | [], _ :: _, _, _, _, h', h => by simp at h h'; exact absurd h.1 h'.1
  | _ :: _, [], _, _, h, _, h' => by simp at h h'; exact absurd h'.1.symm h.1
  | _ :: _, _ :: _, _, _, h, h', he => by
    simp only [List.cons_append, List.cons.injEq, List.mem_cons, not_or] at he h h'
    obtain ⟨rfl, he⟩ := he
    obtain ⟨h1, h2⟩ := space_inj h.2 h'.2 he
    exact ⟨by rw [h1], h2⟩

/-- A normal act that begins `{0} `: its first word is `{0}`, then a space and its second word. -/
theorem act_rest {W : List String} (hW : ∀ w ∈ W, w ≠ "" ∧ ∀ c ∈ w.data, pyWhitespace c = false)
    (hs : (" ".intercalate W).startsWith "{0} " = true) :
    ∃ w1 Ws, W = "{0}" :: w1 :: Ws ∧
      (" ".intercalate W).data = "{0} ".data ++ w1.data ++ Ws.flatMap (' ' :: ·.data) := by
  have hsp : ∀ w ∈ W, ' ' ∉ w.data := fun w hw hm => by have := (hW w hw).2 _ hm; simp [pyWhitespace] at this
  obtain ⟨v, hv⟩ := VE.Readings.eq_append_of_startsWith (by decide) hs
  have hd := congrArg String.data hv
  rw [String.data_append] at hd
  match W, hW, hsp with
  | [], _, _ => simp [String.intercalate] at hd
  | [w0], _, hsp =>
    have : ' ' ∈ w0.data := by
      rw [show " ".intercalate [w0] = w0 from rfl] at hd; simp [hd]
    exact absurd this (hsp w0 (by simp))
  | w0 :: w1 :: Ws, _, hsp =>
    rw [VE.Acts.Lexical.intercalate_data, List.flatMap_cons] at hd ⊢
    have := space_inj (u' := ['{', '0', '}']) (hsp w0 (by simp)) (by decide)
      (by rw [List.cons_append] at hd; simpa using hd)
    refine ⟨w1, Ws, by rw [show w0 = "{0}" from String.ext this.1], ?_⟩
    rw [this.1]; simp

theorem asciiSpace_py {c : Char} (h : asciiSpace c = true) : pyWhitespace c = true := by
  simp [asciiSpace] at h; rcases h with ((((rfl | rfl) | rfl) | rfl) | rfl) | rfl <;> decide

/-- A command's act has a verb after `{0}`, so its second word does not open a slot. -/
theorem verb_head {w1 : String} {Ws : List String}
    (hW : ∀ w ∈ "{0}" :: w1 :: Ws, w ≠ "" ∧ ∀ c ∈ w.data, pyWhitespace c = false)
    (hv : (actVerb (" ".intercalate ("{0}" :: w1 :: Ws))).isSome = true) : w1.data.head? ≠ some '{' := by
  generalize ha : " ".intercalate ("{0}" :: w1 :: Ws) = a at hv
  have hdata : a.data = "{0} ".data ++ w1.data ++ Ws.flatMap (' ' :: ·.data) := by
    rw [← ha, VE.Acts.Lexical.intercalate_data, List.flatMap_cons]; simp
  have hsurf : surfaceWords a = a.map Char.toLower := by
    unfold surfaceWords
    congr 1
    rw [VE.Acts.Lexical.split_data, VE.Acts.Lexical.splitL_congr (q := pyWhitespace) (fun c hc => by
      rcases VE.Acts.Lexical.mem_intercalate (ha ▸ hc) with rfl | ⟨w, hw, hc⟩
      · decide
      · have := (hW w hw).2 c hc
        cases h : asciiSpace c
        · exact this.symm
        · exact absurd (asciiSpace_py h) (by simp [this]))]
    rw [← VE.Acts.Lexical.split_data]
    show " ".intercalate (words a) = a
    rw [← ha, VE.Acts.Lexical.words_intercalate hW]
  have hlow : ∀ c, c.toLower = ' ' → c = ' ' := fun c h => toLower_fixed h (.inl rfl)
  obtain ⟨tl, htl⟩ : ∃ tl, VE.Acts.Lexical.splitL (· == ' ')
      ((w1.data ++ Ws.flatMap (' ' :: ·.data)).map Char.toLower) = w1.data.map Char.toLower :: tl := by
    have hw1 : ∀ c ∈ w1.data.map Char.toLower, (c == ' ') = false := fun c hc => by
      obtain ⟨d, hd, rfl⟩ := List.mem_map.1 hc
      have := (hW w1 (by simp)).2 d hd
      cases h : (d.toLower == ' ')
      · rfl
      · rw [hlow d (by simpa using h)] at this; simp [pyWhitespace] at this
    cases Ws with
    | nil => exact ⟨[], by simpa using VE.Acts.Lexical.splitL_word hw1⟩
    | cons w2 Ws => exact ⟨_, by simpa using VE.Acts.Lexical.splitL_append (by decide) _ hw1⟩
  have hsplit : (surfaceWords a).splitOn " " = "{0}" :: String.mk (w1.data.map Char.toLower) :: tl.map String.mk := by
    rw [hsurf, VE.Acts.Lexical.splitOn_space, VE.Readings.map_data, hdata, List.append_assoc, List.map_append,
      show "{0} ".data.map Char.toLower = ['{', '0', '}'] ++ [' '] by decide, List.append_assoc,
      List.singleton_append, VE.Acts.Lexical.splitL_append (by decide) _ (by decide), htl]
    rfl
  unfold actVerb at hv
  rw [hsplit] at hv
  intro h1
  obtain ⟨rest, hrest⟩ : ∃ rest, w1.data = '{' :: rest := by
    cases h : w1.data with
    | nil => rw [h] at h1; cases h1
    | cons d rest => rw [h] at h1; cases h1; exact ⟨rest, rfl⟩
  have hst : (String.mk (w1.data.map Char.toLower)).startsWith "{" = true := by
    rw [hrest, List.map_cons, show '{'.toLower = '{' by decide,
      show String.mk ('{' :: rest.map Char.toLower) = "{" ++ String.mk (rest.map Char.toLower) by
        apply String.ext; simp [String.data_append]]
    exact VE.Readings.startsWith_append_ascii _ _ (by decide)
  simp [hst] at hv

/-! ### What the decoder checked of every act -/

open VE.SpeechActs.Wire (decodeSpeechEnvironmentFull checkTemplates SpeechEnvironment)

theorem decode_templates {j : Lean.Json} {se : SpeechEnvironment} (h : decodeSpeechEnvironmentFull j = .ok se) :
    ∃ preds, checkTemplates preds se.ne.regulated = .ok () := by
  unfold decodeSpeechEnvironmentFull VE.SpeechActs.Wire.decodeEnvironmentWith at h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨preds, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  iterate 9 obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨u, ht, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h; cases u
  exact ⟨preds, ht⟩

theorem templates_act {preds : List (String × Lean.Json)} {regs : List VE.Norms.Regulated}
    (h : checkTemplates preds regs = .ok ()) {g : VE.Norms.Regulated} {a : String}
    (hg : g ∈ regs) (ha : g.act = some a) : slotsApart (a.length + 1) ' ' a.toList = true := by
  unfold checkTemplates at h
  simp only at h
  generalize hL : _ ++ regs.filterMap (·.act) = L at h
  have hm : a ∈ L := by rw [← hL]; exact List.mem_append_right _ (List.mem_filterMap.2 ⟨g, hg, ha⟩)
  clear hL
  induction L with
  | nil => cases hm
  | cons x L ih =>
    simp only [List.forIn_cons] at h
    by_cases hx : slotsApart (x.length + 1) ' ' x.toList = true
    · rw [if_pos hx] at h
      rcases List.mem_cons.1 hm with rfl | hm
      · exact hx
      · exact ih (by simpa using h) hm
    · rw [if_neg hx] at h; cases h

theorem decoded_actIn {j : Lean.Json} {se : SpeechEnvironment} (hd : decodeSpeechEnvironmentFull j = .ok se)
    {g : VE.Norms.Regulated} {a : String} (hg : g ∈ se.ne.regulated) (ha : g.act = some a) :
    ∃ ps fx k raw, VE.Norms.Wire.canonicalActIn ps fx g.name k raw = .ok a := by
  obtain ⟨s, -, -, -, -, hne, -⟩ := VE.SpeechActs.Wire.decode_steps hd
  generalize se.ne = ne at hne hg
  unfold VE.Norms.Wire.decodeNormsEnvironment at hne
  repeat' (first
    | (cases hne; done)
    | (have h' := VE.Order.ProfileGate.bind_ok hne; clear hne; obtain ⟨_, _, hne⟩ := h')
    | (have h' := VE.Norms.Wire.ite_ok_cases hne; clear hne
       rcases h' with ⟨hc', hne⟩ | ⟨hc', hne⟩ <;> try (simp at hc'; done))
    | split at hne)
  all_goals
    cases hne
    obtain ⟨⟨p, entry⟩, _, hf⟩ := VE.SpeechActs.Wire.filterMapM_mem (by assumption) g hg
    simp only [if_neg Bool.false_ne_true] at hf
    repeat' (first
      | (cases hf; done)
      | (have h' := VE.Order.ProfileGate.bind_ok hf; clear hf; obtain ⟨_, _, hf⟩ := h')
      | (have h' := VE.Norms.Wire.ite_ok_cases hf; clear hf
         rcases h' with ⟨hc', hf⟩ | ⟨hc', hf⟩ <;> try (simp at hc'; done))
      | split at hf)
    cases hf
    obtain ⟨hn, k, r, hk⟩ := VE.SpeechActs.Wire.decodeRegulatedWith_act (by assumption) ha
    exact ⟨_, _, k, r, hn ▸ hk⟩

theorem if_then_lower {w : String} (h : w.toLower = "if" ∨ w.toLower = "then") :
    VE.Norms.Wire.actReserved.contains w.toLower = true := by
  rcases h with h | h <;> rw [h] <;> decide

/-- Either act check gives a normal act `" ".intercalate W` that begins `{0} `, none of whose words without a
brace is `if` or `then` in any case. -/
theorem actIn_shape {ps fx : List String} {name : String} {k : Nat} {raw : Lean.Json} {a : String}
    (h : VE.Norms.Wire.canonicalActIn ps fx name k raw = .ok a) :
    ∃ W : List String, a = " ".intercalate W ∧ (∀ w ∈ W, w ≠ "" ∧ ∀ c ∈ w.data, pyWhitespace c = false) ∧
      a.startsWith "{0} " = true ∧ ∀ w ∈ W, '{' ∉ w.data → ¬ (w.toLower = "if" ∨ w.toLower = "then") := by
  unfold VE.Norms.Wire.canonicalActIn at h
  split at h
  · obtain ⟨hn, h1, -⟩ := (VE.Acts.Lexical.check_iff _ _ _ _ _).1 h
    have hcl := VE.Acts.Lexical.check_no_clause h
    unfold VE.Acts.Lexical.normal at hn
    have hW : ∀ w ∈ words (VE.Acts.Lexical.fold ((raw.getStr?).toOption.getD "")),
        w ≠ "" ∧ ∀ c ∈ w.data, pyWhitespace c = false := fun w hw => words_facts hw
    refine ⟨_, hn, hW, h1, fun w hw _ hif => ?_⟩
    have := hcl w (by rw [hn, VE.Acts.Lexical.words_intercalate hW]; exact hw)
    rcases hif with he | he <;> rw [he] at this <;> revert this <;> decide
  · unfold VE.Norms.Wire.canonicalAct at h
    simp only [bind, Except.bind, pure, Except.pure] at h
    split at h
    · rename_i hc
      cases h
      simp only [Bool.and_eq_true, Bool.not_eq_true', List.any_eq_false] at hc
      have hW : ∀ w ∈ words ((raw.getStr?).toOption.getD ""), w ≠ "" ∧ ∀ c ∈ w.data, pyWhitespace c = false :=
        fun w hw => words_facts hw
      refine ⟨_, rfl, hW, hc.1.1.1.1.2, fun w hw hb hif => ?_⟩
      have hw' : w ∈ words ⟨(VE.Norms.Wire.scanSlots (" ".intercalate (words ((raw.getStr?).toOption.getD ""))).toList).2⟩ := by
        have := VE.Acts.Lexical.word_out (a := " ".intercalate (words ((raw.getStr?).toOption.getD "")))
          (by rw [VE.Acts.Lexical.words_intercalate hW]; exact hw)
        rwa [VE.Acts.Lexical.out_eq_self _ hb] at this
      have := hc.2 w hw'
      by_cases hs : w = "slot"
      · subst hs
        rw [show "slot".toLower = "slot" from String.ext (by rw [String.toLower, VE.Readings.map_data]; decide)] at hif
        rcases hif with h | h <;> revert h <;> decide
      · exact this ⟨by simpa using hs, if_then_lower hif⟩
    · cases h

/-! ### The wording side -/

theorem intercalate_head (t a : String) (ys : List String) : a.data <+: (t.intercalate (a :: ys)).data := by
  have e : a :: ys = (a.data :: ys.map String.data).map String.mk := by
    simp only [List.map_cons, List.map_map, show (String.mk ∘ String.data) = id from funext fun _ => rfl,
      List.map_id]
  rw [e, SplitOn.intercalate_data, SplitOn.intercalate_cons]
  exact List.prefix_append _ _

/-- The plain part of a wording keeps a prefix that has no comma. -/
theorem splitLast_prefix {u : String} {P : List Char} (hP : ',' ∉ P) (h : P <+: u.data) :
    P <+: (splitLastIf u).1.data := by
  obtain ⟨x0, xs, hx⟩ : ∃ x0 xs, SplitOn.splitOnL ", if ".data u.data = x0 :: xs := by
    cases h' : SplitOn.splitOnL ", if ".data u.data with
    | nil => exact absurd h' (SplitOn.splitOnL_ne_nil _)
    | cons x0 xs => exact ⟨x0, xs, rfl⟩
  have hx0 : P <+: x0 := SplitOn.prefix_first (ds := " if ".data) hP h hx
  unfold splitLastIf
  rw [SplitOn.splitOn_data u ", if " (by decide), hx, List.map_cons]
  split
  · rename_i x hx'
    rw [List.cons.injEq] at hx'
    rw [← hx'.1]; exact hx0
  · rename_i ys hne
    cases xs with
    | nil => exact absurd rfl (hne (String.mk x0))
    | cons y xs =>
      rw [List.map_cons, List.dropLast_cons₂]
      exact hx0.trans (intercalate_head _ _ _)

/-- A wording whose body begins with `W` (no comma, not `D`) is read with a body that begins with `W`. -/
theorem body_prefix {s : String} {p : Parts} {W : String} (hc : ',' ∉ W.data) (hD : W.data.head? ≠ some 'D')
    (hp : parts s = some p) (hb : W.data <+: ((trimmed s).dropRight 1).data) : W.data <+: p.body.data := by
  unfold parts at hp
  dsimp only at hp
  split at hp
  · cases hp
  have hpl := splitLast_prefix hc hb
  generalize splitLastIf ((trimmed s).dropRight 1) = sl at hp hpl
  obtain ⟨plain, cond⟩ := sl
  dsimp only at hp hpl
  split at hp
  · rename_i hdn
    obtain ⟨v, rfl⟩ := VE.Readings.eq_append_of_startsWith (by decide) hdn
    obtain ⟨t, ht⟩ := hpl
    rw [String.data_append] at ht
    cases hw : W.data with
    | nil => exact List.nil_prefix
    | cons w0 _ =>
      have := congrArg List.head? ht
      rw [hw] at this hD
      simp at this
      exact absurd (by rw [this]; rfl) hD
  · cases hp; exact hpl

/-! ### Assembly -/

theorem slots_open {n : Nat} {l : List Char} (h : slotsApart (n + 4) ' ' ('{' :: '0' :: '}' :: ' ' :: l) = true) :
    slotsApart (n + 2) ' ' l = true := by
  have hd : List.takeWhile Char.isDigit ('0' :: '}' :: ' ' :: l) = ['0'] := by
    simp [show Char.isDigit '0' = true by decide, show Char.isDigit '}' = false by decide]
  unfold slotsApart at h
  simp only [hd, List.length_singleton, List.drop_succ_cons, List.drop_zero, List.isEmpty_cons,
    Bool.false_eq_true, if_false, Bool.and_eq_true] at h
  rw [slots_step (by decide)] at h
  exact h.2

/-! ### The statements -/

variable (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)

/-- Section 7's statement with the hypothesis `hb` (SIGNED by the DRI 2026-11-09,
reviews/dri-decisions-20261109-ci-3a-wording.md item 1): `readStep` charges `maxWordingBytes` first. -/
theorem preposed_eq (c x : String) (r : Reading) (h : shapes s = [.preposed c x])
    (hb : (trimmed s).utf8ByteSize ≤ maxWordingBytes) :
    readStep se sc E L b s = .one r false ↔
      readCommand se sc E L b (capitalise x ++ ", if " ++ c ++ ".") = .one r := by
  rw [readStep_one se sc E L b s hb h]
  simp only [shapeOutcome, hasThen_preposed h, Bool.false_eq_true, if_false, lift_one, and_true]

/-- `readStep_conservative` for a wording whose body begins with neither `If ` nor `Then `: the only shape is the
merged wording, since `hs` leaves no sequence; `one_begins` discharges the other two hypotheses. -/
theorem readStep_core (r : Reading) (h : readCommand se sc E L b s = .one r) (hs : hasThen s = false)
    (hi : ((trimmed s).dropRight 1).startsWith "If " = false)
    (ht : ((trimmed s).dropRight 1).startsWith "Then " = false) :
    readStep se sc E L b s = .one r false := by
  have hw := ((readCommand_one_iff se sc E L b s r).1 h).1
  simp only [withinLimits, Bool.and_eq_true, decide_eq_true_eq] at hw
  have hsq : ¬ 2 ≤ (((trimmed s).dropRight 1).splitOn ", then ").length := by
    rw [splitOn_two _ _ (by decide), VE.Question.Str.dropRight_one]
    intro hi'
    have := (splitOn_two (trimmed s) ", then " (by decide)).2 (hi'.trans (List.dropLast_prefix _).isInfix)
    unfold hasThen at hs
    simp at hs; omega
  have hsh : shapes s = [.core s] := by
    unfold shapes
    dsimp only
    split
    · rfl
    rw [if_neg (by simp [hi]), if_neg (by simp [ht]), if_neg (by simp [hsq])]
    rfl
  rw [readStep_one se sc E L b s hw.1 hsh]
  simp [shapeOutcome, lift, h]

/-- A wording `readCommand` reads as `one`, over a decoded environment, has a body that begins with neither `If `
nor `Then `: the act's verb follows `{0} ` and is no clause word, and a slot cannot join it. -/
theorem one_begins (j : Lean.Json) (hd : decodeSpeechEnvironmentFull j = .ok se) (r : Reading)
    (h : readCommand se sc E L b s = .one r) {W : String} (hW : W = "If " ∨ W = "Then ") :
    ((trimmed s).dropRight 1).startsWith W = false := by
  cases hst : ((trimmed s).dropRight 1).startsWith W with
  | false => rfl
  | true =>
  exfalso
  obtain ⟨v, hv⟩ := VE.Readings.eq_append_of_startsWith (by rcases hW with rfl | rfl <;> decide) hst
  have hb : W.data <+: ((trimmed s).dropRight 1).data := ⟨v.data, by rw [hv, String.data_append]⟩
  obtain ⟨_, hc, _⟩ := (readCommand_one_iff se sc E L b s r).1 h
  have hm : r ∈ candidates se sc E L b s := (mem_dedup _ _ (Nat.le_refl _) r).mp (by simp [hc])
  obtain ⟨p, g, a, t, hp, -, hg, -, -, ha, hv', hfill, hfold⟩ := candidate_reads_back se sc E L b s r hm
  have hbody := body_prefix (by rcases hW with rfl | rfl <;> decide) (by rcases hW with rfl | rfl <;> decide) hp hb
  obtain ⟨T, hT, hWT, hTl⟩ : ∃ T : List Char, (∀ x ∈ T, x ∈ ['i', 'f', 't', 'h', 'e', 'n']) ∧
      W.data.map Char.toLower = T ++ [' '] ∧
      ∀ w : String, w.data.map Char.toLower = T → w.toLower = "if" ∨ w.toLower = "then" := by
    rcases hW with rfl | rfl
    · exact ⟨['i', 'f'], by decide, by decide,
        fun w hw => .inl (String.ext (by rw [String.toLower, VE.Readings.map_data, hw]))⟩
    · exact ⟨['t', 'h', 'e', 'n'], by decide, by decide,
        fun w hw => .inr (String.ext (by rw [String.toLower, VE.Readings.map_data, hw]))⟩
  obtain ⟨rest, hrest⟩ := hbody
  have ht : t.data.map Char.toLower = T ++ ' ' :: rest.map Char.toLower := by
    have := congrArg String.data hfold
    simp only [fold, VE.Readings.map_data] at this
    rw [this, ← hrest, List.map_append, hWT]; simp
  obtain ⟨ps, fx, k, raw, hk⟩ := decoded_actIn hd hg ha
  obtain ⟨Wa, rfl, hWa, hst0, hres⟩ := actIn_shape hk
  obtain ⟨w1, Ws, rfl, hdata⟩ := act_rest hWa hst0
  have h0 := verb_head hWa hv'
  obtain ⟨preds, htp⟩ := decode_templates hd
  have hsl := templates_act htp hg ha
  unfold filled VE.EnglishGrammar.fillHoles at hfill
  generalize hgo : fillHoles.go _ _ _ _ _ = res at hfill
  obtain ⟨hs, out⟩ := res
  dsimp only at hfill
  obtain rfl : t = ⟨out⟩ := by
    split at hfill
    · exact (Option.some.inj hfill).symm
    · cases hfill
  generalize hR : Ws.flatMap (fun x => ' ' :: x.data) = R at hdata
  have hRs : R = [] ∨ R.head? = some ' ' := by subst hR; cases Ws <;> simp
  have hA : (" ".intercalate ("{0}" :: w1 :: Ws)).data = '{' :: '0' :: '}' :: ' ' :: (w1.data ++ R) := by
    rw [hdata]; rfl
  have hdrop : ((" ".intercalate ("{0}" :: w1 :: Ws)).drop 4).toList = w1.data ++ R := by
    rw [VE.Question.Str.drop_data]; show List.drop 4 _ = _; rw [hA]; rfl
  have hlen : ((" ".intercalate ("{0}" :: w1 :: Ws)).drop 4).length = (w1.data ++ R).length := by
    rw [← hdrop]; rfl
  rw [hlen, hdrop] at hgo
  have hsl' : slotsApart ((w1.data ++ R).length + 3) ' ' (w1.data ++ R) = true := by
    apply slots_open
    have hl : (" ".intercalate ("{0}" :: w1 :: Ws)).length + 1 = (w1.data ++ R).length + 1 + 4 := by
      show (" ".intercalate ("{0}" :: w1 :: Ws)).data.length + 1 = _; rw [hA]; simp
    rw [hl] at hsl
    exact (show (" ".intercalate ("{0}" :: w1 :: Ws)).toList = _ from hA) ▸ hsl
  have hw := filled_word _ hT (hWa w1 (by simp)).2 h0 hRs (Nat.lt_succ_self _) (by omega) hsl' (by rw [hgo]; exact ht)
  have hb1 : '{' ∉ w1.data := fun hm => by
    have := List.mem_map_of_mem (f := Char.toLower) hm
    rw [hw] at this
    exact absurd (hT _ this) (by decide)
  exact hres w1 (by simp) hb1 (hTl w1 hw)

/-- Conservative: a merged wording keeps its reading. -/
theorem readStep_conservative (j : Lean.Json) (r : Reading)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se)
    (h : readCommand se sc E L b s = .one r) (hs : hasThen s = false) :
    readStep se sc E L b s = .one r false :=
  readStep_core se sc E L b s r h hs (one_begins se sc E L b s j hd r h (.inl rfl))
    (one_begins se sc E L b s j hd r h (.inr rfl))

/-! ### Fixtures -/

-- `preposed_eq`'s rewritten wording: the S1 seed (a `capitalise` that lower-cases) fails here.
#guard capitalise "click Ask" ++ ", if " ++ "draft is approved" ++ "." == "Click Ask, if draft is approved."
#guard hasThen ("click Ask" ++ ".") == false
#guard shapes "Click Check rule conflict." == [.core "Click Check rule conflict."]
-- `readStep_conservative` on `E_web`: the merged wording keeps `readCommand`'s reading.
#guard match Examples.web "Click Check rule conflict." with
  | .one r => StepsExamples.step "Click Check rule conflict." == .one r false
  | _ => false

/-- `hb` is needed (the DRI's added hypothesis): `<x>` keeps the spaces after the comma, which `readCommand` trims
away, so the rewritten wording reads `one` within `maxWordingBytes` while the wording itself is over it and `limit`. -/
def padded : String := "If draft is approved," ++ String.mk (List.replicate 390 ' ') ++ "click Ask."
#guard shapes padded == [.preposed "draft is approved" (String.mk (List.replicate 389 ' ') ++ "click Ask")]
#guard maxWordingBytes < (trimmed padded).utf8ByteSize
#guard StepsExamples.step padded == .limit
#guard Examples.web (capitalise (String.mk (List.replicate 389 ' ') ++ "click Ask") ++ ", if draft is approved.") ==
  .one ⟨.require, "click_ask_required", [], Examples.approvedDraft⟩

end VE.Commands
