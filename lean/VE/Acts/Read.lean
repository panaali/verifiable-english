import VE.Acts.Syntax
import VE.Grammar.Reading

/-! Readings and reading of an act phrase, with the limits of D2 (docs/spec/act-phrases.md 1.6, 5.4, 5.6).

A listing is complete or it is the limit outcome: the step budget exhausted, a saturated parse (`N` raw derivations,
which may hide more), or more than `maxReadings` distinct meanings. The limit is a refusal, never a choice. These
definitions take the grammar and the meaning as arguments, and the meaning's value type: `VE.Acts.readings V` is
`readingsIn (grammar V) (meaning V)` once the rule table, the act trees and the meaning (1.5, 5.2, 5.3) are built.
-/

namespace VE.Acts
open Lexical (Tok)
open VE.Grammar (Grammar Tree Derives Meaning parse)

/-- The raw derivation budget N (D2): R = 2 measured on 38 rows after D9 (i) (docs/act-phrases/ap-2), so 256 stands. -/
def rawCap : Nat := 256
/-- The step budget (D2): S = 19,184 measured at cap 256 after D9 (i), and 10 S ≤ 2,100,000, so the budget stands. -/
def stepBudget : Nat := 2100000
/-- The public listing limit: `readings@1`'s `maxChoices`. -/
def maxReadings : Nat := 64

/-- Every reading, complete; or the limit outcome, a refusal. -/
inductive Listing (α : Type) | ok (xs : List α) | limit
  deriving DecidableEq, Repr

/-- First occurrences, in order. -/
def firsts {α : Type} [DecidableEq α] : List α → List α
  | [] => []
  | x :: xs => x :: (firsts xs).filter (· ≠ x)

/-- From a parse (`none`: step budget exhausted) and a meaning: the distinct meanings, or `limit`. -/
def listing {α : Type} [DecidableEq α] (N L : Nat) (parsed : Option (List (Tree Tok)))
    (μ : Tree Tok → Option α) : Listing α :=
  match parsed with
  | none => .limit
  | some ts => if N ≤ ts.length then .limit else
      let ms := firsts (ts.filterMap μ)
      if L < ms.length then .limit else .ok ms

/-- The outcome of reading a phrase that must have one meaning. -/
inductive ReadOutcome (α : Type) | ok (A : α) | none | many (A B : α) | limit
  deriving DecidableEq, Repr

/-- The value a derivation means, if it has a meaning. -/
def valueOf {α : Type} (μ : Meaning Tok Unit String α) (t : Tree Tok) : Option α :=
  match μ () t with
  | .ok (A, _, _) => some A
  | .error _ => none

section Read

variable {α : Type} [DecidableEq α]

/-- Every reading, equal meanings once, in derivation order (translation). -/
def readingsIn (G : Grammar Term) (μ : Meaning Tok Unit String α) (N b : Nat) (ts : Array Tok) : Listing α :=
  listing N maxReadings (parse G N b ts) (valueOf μ)

/-- One reading required (authoring, and every declared act): a listing with exactly one element. -/
def readIn (G : Grammar Term) (μ : Meaning Tok Unit String α) (N b : Nat) (ts : Array Tok) : ReadOutcome α :=
  match readingsIn G μ N b ts with
  | .limit => .limit
  | .ok [] => .none
  | .ok [A] => .ok A
  | .ok (A :: B :: _) => .many A B

end Read

/-- A meaning of the token list: some derivation means `A`. -/
def DerivedIn {α : Type} (G : Grammar Term) (μ : Meaning Tok Unit String α) (ts : List Tok) (A : α) : Prop :=
  ∃ d, Derives G (.n G.start) ts d ∧ ∃ c, μ () d = .ok (A, c, ())

section Proofs

variable {α : Type} [DecidableEq α]

theorem mem_firsts {x : α} : ∀ {l : List α}, x ∈ firsts l ↔ x ∈ l
  | [] => by simp [firsts]
  | y :: ys => by
    simp only [firsts, List.mem_cons, List.mem_filter, mem_firsts, decide_eq_true_eq]
    by_cases h : x = y <;> simp [h]

theorem nodup_firsts : ∀ (l : List α), (firsts l).Nodup
  | [] => by simp [firsts]
  | y :: ys => by
    simp only [firsts]
    refine List.nodup_cons.mpr ⟨?_, (nodup_firsts ys).filter _⟩
    simp

/-- The generic listing, for the boundary fixtures (N−1 and N raw trees; 63, 64 and 65 meanings). -/
theorem listing_ok (N L : Nat) (parsed : Option (List (Tree Tok))) (μ : Tree Tok → Option α) (xs : List α) :
    listing N L parsed μ = .ok xs ↔
      ∃ ts, parsed = some ts ∧ ts.length < N ∧ xs = firsts (ts.filterMap μ) ∧ xs.length ≤ L := by
  cases parsed with
  | none => simp [listing]
  | some ts =>
    simp only [listing, Option.some.injEq, exists_eq_left']
    by_cases hN : N ≤ ts.length
    · simp only [hN, if_true, reduceCtorEq, false_iff]
      rintro ⟨h, _⟩
      omega
    · by_cases hL : L < (firsts (ts.filterMap μ)).length
      · simp only [hN, hL, if_false, if_true, reduceCtorEq, false_iff]
        rintro ⟨_, rfl, h⟩
        omega
      · simp only [hN, hL, if_false, Listing.ok.injEq]
        constructor
        · rintro rfl; exact ⟨by omega, rfl, by omega⟩
        · rintro ⟨_, rfl, _⟩; rfl

/-- The limit outcome, exactly: an exhausted step budget, a saturated parse, or more than `L` meanings. -/
theorem listing_limit (N L : Nat) (parsed : Option (List (Tree Tok))) (μ : Tree Tok → Option α) :
    listing N L parsed μ = .limit ↔
      (parsed = none ∨ ∃ ts, parsed = some ts ∧ (N ≤ ts.length ∨ L < (firsts (ts.filterMap μ)).length)) := by
  cases parsed with
  | none => simp [listing]
  | some ts =>
    simp only [listing, reduceCtorEq, Option.some.injEq, exists_eq_left', false_or]
    by_cases hN : N ≤ ts.length
    · simp [hN]
    · by_cases hL : L < (firsts (ts.filterMap μ)).length <;> simp [hN, hL]

theorem listing_nodup {N L : Nat} {parsed : Option (List (Tree Tok))} {μ : Tree Tok → Option α} {xs : List α}
    (h : listing N L parsed μ = .ok xs) : xs.Nodup := by
  obtain ⟨_, _, _, rfl, _⟩ := (listing_ok N L parsed μ xs).mp h
  exact nodup_firsts _

variable {G : Grammar Term} {μ : Meaning Tok Unit String α} {N b : Nat} {ts : Array Tok}

omit [DecidableEq α] in
theorem valueOf_eq_some {t : Tree Tok} {A : α} : valueOf μ t = some A ↔ ∃ c, μ () t = .ok (A, c, ()) := by
  unfold valueOf
  split
  · rename_i A2 c2 s2 hm
    simp only [Option.some.injEq, hm]
    constructor
    · rintro rfl; exact ⟨c2, rfl⟩
    · rintro ⟨c, h⟩; cases h; rfl
  · rename_i e hm
    simp [hm]

theorem readingsIn_nodup {As : List α} (hp : readingsIn G μ N b ts = .ok As) : As.Nodup :=
  listing_nodup hp

/-- Complete enumeration: `.ok` already means fewer than `N` raw derivations, so no length hypothesis. -/
theorem readingsIn_exact (hG : G.wf = true) {As : List α} (hp : readingsIn G μ N b ts = .ok As) (A : α) :
    A ∈ As ↔ DerivedIn G μ ts.toList A := by
  obtain ⟨trees, hparse, hlen, rfl, _⟩ := (listing_ok _ _ _ _ _).mp hp
  rw [mem_firsts, List.mem_filterMap]
  constructor
  · rintro ⟨t, ht, hv⟩
    exact ⟨t, VE.Grammar.parse_sound hparse ht, valueOf_eq_some.mp hv⟩
  · rintro ⟨t, hd, hm⟩
    exact ⟨t, VE.Grammar.parse_complete hG hparse hlen hd, valueOf_eq_some.mpr hm⟩

/-- The limit outcome of `readingsIn`, exactly. -/
theorem readingsIn_limit : readingsIn G μ N b ts = .limit ↔
    (parse G N b ts = none ∨ ∃ trees, parse G N b ts = some trees ∧
      (N ≤ trees.length ∨ maxReadings < (firsts (trees.filterMap (valueOf μ))).length)) :=
  listing_limit _ _ _ _

theorem readIn_ok {A : α} : readIn G μ N b ts = .ok A ↔ readingsIn G μ N b ts = .ok [A] := by
  unfold readIn
  split <;> simp_all

/-- One meaning: some derivation means `A`, and every derivation that has a meaning means `A`. -/
theorem readIn_unique (hG : G.wf = true) {A : α} (hr : readIn G μ N b ts = .ok A) :
    DerivedIn G μ ts.toList A ∧ ∀ d B c, Derives G (.n G.start) ts.toList d → μ () d = .ok (B, c, ()) → B = A := by
  have hp := readIn_ok.mp hr
  refine ⟨(readingsIn_exact hG hp A).mp (by simp), fun d B c hd hm => ?_⟩
  simpa using (readingsIn_exact hG hp B).mpr ⟨d, hd, c, hm⟩

theorem readIn_none (hG : G.wf = true) (hr : readIn G μ N b ts = .none) : ∀ A, ¬ DerivedIn G μ ts.toList A := by
  intro A hA
  unfold readIn at hr
  split at hr <;> try simp at hr
  rename_i hp
  simpa using (readingsIn_exact hG hp A).mpr hA

theorem readIn_many (hG : G.wf = true) {A B : α} (hr : readIn G μ N b ts = .many A B) :
    A ≠ B ∧ DerivedIn G μ ts.toList A ∧ DerivedIn G μ ts.toList B := by
  unfold readIn at hr
  split at hr <;> try simp at hr
  rename_i A2 B2 rest hp
  obtain ⟨rfl, rfl⟩ := hr
  have hn := readingsIn_nodup hp
  refine ⟨fun h => ?_, (readingsIn_exact hG hp _).mp (by simp), (readingsIn_exact hG hp _).mp (by simp)⟩
  subst h
  simp at hn

end Proofs

end VE.Acts
