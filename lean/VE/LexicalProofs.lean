import VE.SurfaceProofs

namespace VE.Surface

/-- Decimal decoding used only to prove generated-name freshness. -/
def decimalValue (cs : List Char) : Nat :=
  cs.foldl (fun n c => 10 * n + (c.toNat - 48)) 0

theorem decimal_digit (n : Nat) (h : n < 10) :
    (Nat.digitChar n ≥ '0' && Nat.digitChar n ≤ '9') = true ∧
    (Nat.digitChar n).toNat - 48 = n := by
  match n with
  | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 => decide
  | n + 10 => omega

theorem digitsCore_valid (fuel n : Nat) (ds : List Char)
    (h : ds.all (fun c => c ≥ '0' && c ≤ '9') = true) :
    (Nat.toDigitsCore 10 fuel n ds).all (fun c => c ≥ '0' && c ≤ '9') = true := by
  induction fuel generalizing n ds with
  | zero => exact h
  | succ fuel ih =>
    have hd := (decimal_digit (n % 10) (Nat.mod_lt _ (by decide))).1
    simp only [Nat.toDigitsCore]
    split
    · simp [hd, h]
    · exact ih _ _ (by simp [hd, h])

theorem digitsCore_value (fuel n : Nat) (ds : List Char) (h : n < fuel) :
    (Nat.toDigitsCore 10 fuel n ds).foldl (fun v c => 10 * v + (c.toNat - 48)) 0 =
      ds.foldl (fun v c => 10 * v + (c.toNat - 48)) n := by
  induction fuel generalizing n ds with
  | zero => omega
  | succ fuel ih =>
    have hd := (decimal_digit (n % 10) (Nat.mod_lt _ (by decide))).2
    simp only [Nat.toDigitsCore]
    split
    next hz =>
      simp only [List.foldl_cons, Nat.mul_zero, Nat.zero_add, hd]
      have : n % 10 = n := by omega
      rw [this]
    next hn =>
      rw [ih (n / 10) _ (by omega)]
      simp only [List.foldl_cons, hd]
      congr 1
      omega

theorem digitsCore_nonempty (fuel n : Nat) (ds : List Char) (h : 0 < fuel) :
    Nat.toDigitsCore 10 fuel n ds ≠ [] := by
  cases fuel with
  | zero => omega
  | succ fuel =>
    simp only [Nat.toDigitsCore]
    split
    · simp
    · clear h
      -- A nonempty accumulator remains nonempty, even on fuel exhaustion.
      have helper : ∀ k m xs, xs ≠ [] → Nat.toDigitsCore 10 k m xs ≠ [] := by
        intro k
        induction k with
        | zero => simp [Nat.toDigitsCore]
        | succ k ih =>
          intro m xs hx
          simp only [Nat.toDigitsCore]
          split
          · simp
          · exact ih _ _ (by simp)
      apply helper
      simp

abbrev canonicalName (n : Nat) : String := "x" ++ toString n

theorem canonicalName_generated (n : Nat) : generatedName (canonicalName n) = true := by
  change (!(Nat.toDigits 10 n).isEmpty &&
    (Nat.toDigits 10 n).all (fun c => c ≥ '0' && c ≤ '9')) = true
  have hn := digitsCore_nonempty (n + 1) n [] (by omega)
  have hv := digitsCore_valid (n + 1) n [] (by rfl)
  simp_all [Nat.toDigits]

theorem canonicalName_injective (n m : Nat) (h : canonicalName n = canonicalName m) : n = m := by
  have hs : Nat.toDigits 10 n = Nat.toDigits 10 m := by
    have := congrArg String.toList h
    simpa using this
  have hn := digitsCore_value (n+1) n [] (by omega)
  have hm := digitsCore_value (m+1) m [] (by omega)
  simp only [List.foldl_nil] at hn hm
  rw [← hn, ← hm]
  exact congrArg decimalValue hs

theorem generated_identifier (s : String) (h : generatedName s = true) :
    identifier s = true := by
  unfold generatedName at h
  split at h
  next cs he =>
    simp only [Bool.and_eq_true, Bool.not_eq_true', List.isEmpty_eq_false_iff] at h
    unfold identifier
    rw [he]
    apply List.all_eq_true.mpr
    intro c hc
    have hd := List.all_eq_true.mp h.2 c hc
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hd
    simp [identChar, hd.1, hd.2]
  next => contradiction

theorem canonicalName_identifier (n : Nat) : identifier (canonicalName n) = true :=
  generated_identifier _ (canonicalName_generated n)

theorem generated_not_reserved (s : String) (h : generatedName s = true) :
    reserved.contains s = false := by
  have hn : s ∉ reserved := by
    intro hm
    simp only [reserved, List.mem_cons, List.not_mem_nil, or_false] at hm
    rcases hm with h' | h' | h' | h' | h' | h' | h' | h' | h' | h' | h' | h' | h' | h' | h' | h' <;>
      subst s <;> simp [generatedName] at h
  simpa using hn

theorem span_ident_loop (cs tail acc : List Char) (hc : cs.all identChar = true)
    (ht : boundary tail = true) :
    List.span.loop identChar (cs ++ tail) acc = (acc.reverse ++ cs, tail) := by
  induction cs generalizing acc with
  | nil =>
    cases tail with
    | nil => simp [List.span.loop]
    | cons c cs =>
      simp only [boundary, Bool.not_eq_true'] at ht
      simp [List.span.loop, ht]
  | cons c cs ih =>
    simp only [List.all_cons, Bool.and_eq_true] at hc
    simp [List.span.loop, hc.1, ih _ hc.2, List.reverse_cons, List.append_assoc]

theorem span_ident_append (cs tail : List Char) (hc : cs.all identChar = true)
    (ht : boundary tail = true) : (cs ++ tail).span identChar = (cs, tail) := by
  exact span_ident_loop cs tail [] hc ht

theorem readIdent_append (s : String) (tail : List Char)
    (hs : identifier s = true) (ht : boundary tail = true) :
    readIdent (s.toList ++ tail) = some (s, tail) := by
  cases s with
  | mk cs =>
    cases cs with
    | nil => simp [identifier] at hs
    | cons c cs =>
      change ((c ≥ 'a' && c ≤ 'z') && cs.all identChar) = true at hs
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hs
      have hc : (c :: cs).all identChar = true := by
        simp only [List.all_cons, hs.2, Bool.and_true]
        simp [identChar, hs.1.1, hs.1.2]
      have hp := span_ident_append (c :: cs) tail hc ht
      simp only [List.cons_append] at hp
      simp [readIdent, hs.1.1, hs.1.2, hp]

end VE.Surface
