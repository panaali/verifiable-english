import VE.Cardinality.Render
import VE.Question.Strings

/-! What the paraphrase's renderer guarantees (`Render.lean`): the DRI's rule of 2026-10-27 as a theorem. Every
rendering action charges exactly the bytes it appends and never ends past `maxBytes` (`Charges`), so the reply's
text, the line and every assumption together, is at most `maxBytes` UTF-8 bytes (`paraphrase_within`); the plan's
words for the tie rules (`texts`) and the vocabulary's descriptions (`describe_of`). -/
namespace VE.Cardinality.Render
open Lean

/-- An action that charges what it appends: from a state within the limit it ends within it, and the bytes it
charged are the bytes it appended. -/
def Charges (m : M Unit) : Prop :=
  ∀ n out n' out', m (n, out) = .ok ((), n', out') → n ≤ maxBytes →
    n' ≤ maxBytes ∧ out'.utf8ByteSize + n = out.utf8ByteSize + n'

theorem emit_charges (s : String) : Charges (emit s) := by
  intro n out n' out' h _
  simp only [emit] at h
  split at h
  · cases h
  · cases h; rw [VE.Question.Str.utf8ByteSize_append]; omega

theorem emit_over {s : String} {n : Nat} (out : String) (h : maxBytes < n + s.utf8ByteSize) :
    emit s (n, out) = .error tooLong := by
  simp only [emit, h, ↓reduceIte]

theorem pure_charges : Charges (pure ()) := by
  intro n out n' out' h hn
  cases h; omega

theorem bind_charges {a b : M Unit} (ha : Charges a) (hb : Charges b) : Charges (a >>= fun _ => b) := by
  intro n out n' out' h hn
  simp only [bind, StateT.bind, Except.bind] at h
  split at h
  · cases h
  · rename_i x hx
    obtain ⟨⟨⟩, m, o⟩ := x
    have h1 := ha _ _ _ _ hx hn
    have h2 := hb _ _ _ _ h h1.1
    omega

theorem ite_charges {c : Prop} [Decidable c] {a b : M Unit} (ha : Charges a) (hb : Charges b) :
    Charges (if c then a else b) := by
  split <;> assumption

set_option hygiene false in
/-- Each step of a rendering action charges: its pieces' lemmas, then the binds and branches between them. -/
macro "charges" : tactic => `(tactic| repeat' with_reducible (first
  | apply bind_charges | apply ite_charges | assumption | exact emit_charges _ | exact pure_charges
  | exact inParens_charges ‹_› | exact body_charges w _ | exact members_charges w _ _
  | exact atLeastOne_charges w _ _ | exact term_charges w _ | exact operand_charges w _ | exact positive_charges w _
  | exact countTerm_charges w _ _))

theorem inParens_charges {m : M Unit} (h : Charges m) : Charges (inParens m) :=
  bind_charges (emit_charges _) (bind_charges h (emit_charges _))

theorem body_charges (w : CardEnv) (b : Body) : Charges (body w b) := by
  induction b <;> simp only [body] <;> charges

theorem members_charges (w : CardEnv) (s : String) (b : Body) : Charges (members w s b) := by
  unfold members; split <;> charges
theorem atLeastOne_charges (w : CardEnv) (s : String) (b : Body) : Charges (atLeastOne w s b) := by
  unfold atLeastOne; split <;> charges
theorem term_charges (w : CardEnv) (t : VE.Time.QTerm) : Charges (term w t) := by
  unfold term; split <;> exact emit_charges _
theorem operand_charges (w : CardEnv) (t : CTerm) : Charges (operand w t) := by unfold operand; split <;> charges
theorem positive_charges (w : CardEnv) (t : CTerm) : Charges (positive w t) := by unfold positive; split <;> charges
theorem countTerm_charges (w : CardEnv) (s : String) (kb : Int × Body) : Charges (countTerm w s kb) := by
  unfold countTerm; charges

theorem forM_charges {α : Type} (f : α → M Unit) (h : ∀ x, Charges (f x)) :
    ∀ xs : List α, Charges (xs.forM f)
  | [] => pure_charges
  | x :: xs => bind_charges (h x) (forM_charges f h xs)

theorem count_charges (w : CardEnv) (c : CountAtom) : Charges (count w c) := by
  unfold count; split <;> charges; exact forM_charges _ (fun x => by charges) _

theorem formula_charges (w : CardEnv) (f : CFormula) : Charges (formula w f) := by
  induction f with
  | count c => exact count_charges w c
  | _ => simp only [formula]; charges

/-- A piece of the reply is the bytes it charged. -/
theorem piece_charges {m : M Unit} (h : Charges m) {n n' : Nat} {out out' r : String}
    (hp : piece m (n, out) = .ok (r, n', out')) (hn : n ≤ maxBytes) :
    n' ≤ maxBytes ∧ r.utf8ByteSize + n = n' := by
  simp only [piece, bind, Except.bind] at hp
  split at hp
  · cases hp
  · rename_i x hx
    obtain ⟨⟨⟩, k, o⟩ := x
    cases hp
    have := h _ _ _ _ hx hn
    simp only [String.utf8ByteSize, String.utf8ByteSize.go] at this ⊢
    omega

theorem ascii_size {c : Char} (h : c.toNat ≤ 127) : c.utf8Size = 1 := by
  unfold Char.utf8Size
  rw [if_pos ((UInt32.le_iff_toNat_le).2 (by simpa only [UInt32.toNat_ofNatLT] using h))]

theorem toUpper_size (c : Char) : c.toUpper.utf8Size = c.utf8Size := by
  unfold Char.toUpper
  dsimp only
  split
  · rename_i h
    rw [ascii_size (c := c) (by omega), ascii_size (c := Char.ofNat _) ?_]
    unfold Char.ofNat
    split
    · simp only [Char.ofNatAux, Char.toNat, UInt32.toNat, BitVec.toNat_ofNatLT] at h ⊢; omega
    · decide
  · rfl

theorem go_size : ∀ l : List Char, String.utf8ByteSize.go (initial.go l) = String.utf8ByteSize.go l
  | [] => rfl
  | c :: cs => by
    by_cases hc : c = '('
    · subst hc; simp only [initial.go, String.utf8ByteSize.go, go_size cs]
    · simp only [initial.go, String.utf8ByteSize.go, toUpper_size]

/-- A line's capital changes no byte count. -/
theorem initial_size (s : String) : (initial s).utf8ByteSize = s.utf8ByteSize := go_size s.data

/-- Pieces in a row are the bytes they charged. -/
theorem pieces_charge {α : Type} {A : α → M Unit} (hA : ∀ a, Charges (A a)) : ∀ (as : List α) {n n' : Nat}
    {out out' : String} {rs : List String}, (as.mapM fun a => piece (A a)) (n, out) = .ok (rs, n', out') →
      n ≤ maxBytes → n' ≤ maxBytes ∧ (rs.map String.utf8ByteSize).sum + n = n'
  | [], _, _, _, _, _, h, hn => by cases h; exact ⟨hn, by simp⟩
  | a :: as, n, n', out, out', rs, h, hn => by
    simp only [List.mapM_cons, bind, StateT.bind, Except.bind, pure, StateT.pure, Except.pure] at h
    split at h
    · cases h
    · rename_i x hx
      obtain ⟨r, k, o⟩ := x
      split at h
      · cases h
      · rename_i y hy
        obtain ⟨rs', k', o'⟩ := y
        cases h
        have h1 := piece_charges (hA a) hx hn
        have h2 := pieces_charge hA as hy h1.1
        simp only [List.map_cons, List.sum_cons]
        omega

theorem bind_ok {α β : Type} {x : M α} {f : α → M β} {s : Nat × String} {r : β × Nat × String}
    (h : (x >>= f) s = .ok r) : ∃ a s', x s = .ok (a, s') ∧ f a s' = .ok r := by
  simp only [bind, StateT.bind, Except.bind] at h
  split at h
  · cases h
  · rename_i y hy; exact ⟨y.1, y.2, hy, h⟩

/-- The DRI's rule of 2026-10-27: the reply's text, the line and every assumption together, is at most `maxBytes`
UTF-8 bytes. -/
theorem paraphrase_within {w : CardEnv} {f : CFormula} {r : String × List String}
    (h : paraphrase w f = .ok r) : r.1.utf8ByteSize + (r.2.map String.utf8ByteSize).sum ≤ maxBytes := by
  simp only [paraphrase, Functor.map, Except.map] at h
  split at h
  · cases h
  · rename_i v hv
    cases h
    obtain ⟨as, ⟨n1, o1⟩, h1, h2⟩ := bind_ok hv
    obtain ⟨line, ⟨n2, o2⟩, h3, h4⟩ := bind_ok h2
    simp only [pure, StateT.pure, Except.pure, Except.ok.injEq] at h4
    subst h4
    have hs := pieces_charge (fun s => by charges) _ h1 (Nat.zero_le _)
    have hl := piece_charges (bind_charges (formula_charges w f) (emit_charges _)) h3 hs.1
    simp only [initial_size]
    omega

/-- The plan's words (quantities-PLAN.md 2.1): how a value exactly halfway rounds under each admitted rule; a place,
a count's relation and a proportion's comparison; the limit. -/
theorem texts : tie .tiesUp = "a value exactly halfway rounds up, to the larger number" ∧
    tie .halfEven = "a value exactly halfway rounds to the even digit" ∧ place 3 = "thousandth" ∧
    relText .le = "is at most" ∧ cmpText .gt = "more than" ∧ maxBytes = 65536 :=
  ⟨rfl, rfl, rfl, rfl, rfl, rfl⟩

/-- A name reads as its vocabulary description. -/
theorem describe_of {w : CardEnv} {g n d : String}
    (h : (((w.w6.target.getObjValD "vocabulary").getObjValD g).getObjValD n).getObjValD "description" = .str d) :
    describe w g n = d := by
  unfold describe; rw [h]; rfl

end VE.Cardinality.Render
