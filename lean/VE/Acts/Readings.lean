import VE.Acts.Meaning
import VE.Acts.Table

/-! The readings of an act phrase, `read` and `analyse` (docs/spec/act-phrases.md 1.6, 5.4), and spec 5.6's
theorems about them.

`readings V` is ap-2's generic listing `readingsIn` at the act grammar and its meaning, which is spec 5.4's
`listing N maxReadings (parse (grammar V) N b ts) …` exactly; `read V` is `readIn`. Spec 5.6's statements are proved
from ap-2's generic theorems (`readingsIn_exact`, `readIn_unique`, ...) and ap-2b's `grammar_wf`.

`phraseReadings` (spec 7, AP-4) is a phrase's readings under a modal: each meaning through the table, equal lists once.
It parses once, through `readings`, so the raw cap `N`, the step budget `b` and the 64-reading limit bound it before
the table runs: at most 64 meanings, each giving at most two lists (`table_length`), and the result is charged
against the same limit (`phraseReadings_length`). No route reads it yet: AP-7 runs on it first (plan G17).
-/

namespace VE.Acts
open Lexical (Tok)

/-- Every reading of a phrase: its distinct meanings in derivation order, or the limit outcome (5.4). -/
def readings (V : Vocab) (N b : Nat) (ts : Array Tok) : Listing Act := readingsIn (grammar V) (meaning V) N b ts
/-- One reading required: `ok` of the one meaning, `none`, `many` with the first two, or `limit` (5.4). -/
def read (V : Vocab) (N b : Nat) (ts : Array Tok) : ReadOutcome Act := readIn (grammar V) (meaning V) N b ts
/-- For AP-5 only: a simple act exactly when the phrase has one meaning and it is `one`; it renames nothing. -/
def analyse (V : Vocab) (N b : Nat) (ts : Array Tok) : Option Atom :=
  match read V N b ts with | .ok (.one a) => some a | _ => none
/-- A meaning of the token list: some derivation means `A` (spec 5.6's `Derived`, which is `DerivedIn`'s text). -/
def Derived (V : Vocab) (ts : List Tok) (A : Act) : Prop := DerivedIn (grammar V) (meaning V) ts A

/-- `Derived` is spec 5.6's text. -/
theorem derived_iff (V : Vocab) (ts : List Tok) (A : Act) : Derived V ts A ↔
    ∃ d, VE.Grammar.Derives (grammar V) (.n (grammar V).start) ts d ∧ ∃ c, meaning V () d = .ok (A, c, ()) :=
  Iff.rfl

/-- One meaning (design debate): some derivation means `A`, and every derivation that has a meaning means `A`. -/
theorem read_unique (V : Vocab) (h : framesOk V = true) {N b : Nat} {ts : Array Tok} {A : Act}
    (hr : read V N b ts = .ok A) :
    Derived V ts.toList A ∧ ∀ d B c, VE.Grammar.Derives (grammar V) (.n (grammar V).start) ts.toList d →
      meaning V () d = .ok (B, c, ()) → B = A :=
  readIn_unique (grammar_wf V h) hr

theorem read_none (V : Vocab) (h : framesOk V = true) {N b ts} (hr : read V N b ts = .none) :
    ∀ A, ¬ Derived V ts.toList A :=
  readIn_none (grammar_wf V h) hr

theorem read_many (V : Vocab) (h : framesOk V = true) {N b ts A B} (hr : read V N b ts = .many A B) :
    A ≠ B ∧ Derived V ts.toList A ∧ Derived V ts.toList B :=
  readIn_many (grammar_wf V h) hr

/-- Complete enumeration: no length hypothesis, because `.ok` already means fewer than `N` raw derivations. -/
theorem readings_exact (V : Vocab) (h : framesOk V = true) {N b : Nat} {ts : Array Tok} {As : List Act}
    (hp : readings V N b ts = .ok As) (A : Act) : A ∈ As ↔ Derived V ts.toList A :=
  readingsIn_exact (grammar_wf V h) hp A

theorem readings_nodup (V : Vocab) {N b ts As} (hp : readings V N b ts = .ok As) : As.Nodup :=
  readingsIn_nodup hp

/-- The limit outcome, exactly: an exhausted step budget, a saturated parse, or more than 64 meanings. -/
theorem readings_limit (V : Vocab) (N b : Nat) (ts : Array Tok) :
    readings V N b ts = .limit ↔
      (VE.Grammar.parse (grammar V) N b ts = none ∨
       ∃ trees, VE.Grammar.parse (grammar V) N b ts = some trees ∧
         (N ≤ trees.length ∨ maxReadings < (firsts (trees.filterMap (fun t => match meaning V () t with
            | .ok (A, _, _) => some A | .error _ => none))).length)) := by
  have hv : valueOf (meaning V) = fun t => match meaning V () t with | .ok (A, _, _) => some A | .error _ => none := by
    funext t; unfold valueOf; cases meaning V () t <;> rfl
  rw [← hv]; exact readingsIn_limit

/-- Every reading of a phrase under a modal: each meaning through the table, equal lists once; `limit` when the
readings are, or when more than 64 lists result (spec 7). -/
def phraseReadings (V : Vocab) (op : Op) (N b : Nat) (ts : Array Tok) : Listing (List Simple) :=
  match readings V N b ts with
  | .limit => .limit
  | .ok As =>
    let Rs := firsts (As.flatMap (table op))
    if maxReadings < Rs.length then .limit else .ok Rs

/-- Characterised by the grammar's derivations, not by a possibly truncated list. -/
theorem phraseReadings_exact (V : Vocab) (h : framesOk V = true) {op : Op} {N b : Nat} {ts : Array Tok}
    {Rs : List (List Simple)} (hp : phraseReadings V op N b ts = .ok Rs) (R : List Simple) :
    R ∈ Rs ↔ ∃ A, Derived V ts.toList A ∧ R ∈ table op A := by
  unfold phraseReadings at hp
  split at hp
  · cases hp
  next As hr =>
    dsimp only at hp
    split at hp
    · cases hp
    · cases hp
      simp only [mem_firsts, List.mem_flatMap]
      exact ⟨fun ⟨A, hA, hR⟩ => ⟨A, (readings_exact V h hr A).mp hA, hR⟩,
        fun ⟨A, hA, hR⟩ => ⟨A, (readings_exact V h hr A).mpr hA, hR⟩⟩

/-- The table gives a meaning at most two readings, so the lists `phraseReadings` compares are at most 128. -/
theorem table_length (op : Op) (A : Act) : (table op A).length ≤ 2 := by
  cases op <;> cases A <;> simp only [table, freeTable] <;> (try split) <;> simp

/-- The listed readings are charged against the 64-reading limit. -/
theorem phraseReadings_length {V : Vocab} {op : Op} {N b : Nat} {ts : Array Tok} {Rs : List (List Simple)}
    (hp : phraseReadings V op N b ts = .ok Rs) : Rs.length ≤ maxReadings := by
  unfold phraseReadings at hp
  split at hp
  · cases hp
  · dsimp only at hp
    split at hp
    · cases hp
    · cases hp; omega

theorem analyse_one (V : Vocab) {N b ts a} (h : analyse V N b ts = some a) : read V N b ts = .ok (.one a) := by
  unfold analyse at h
  split at h <;> simp_all

end VE.Acts
