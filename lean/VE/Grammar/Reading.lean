import VE.Grammar.TableProofs

/-! Readings and documents (docs/spec/english-lean.md 2.8 and 5.6).

The reader is stated for any meaning function: from the state before a sentence and a tree, the
sentence's value, its conclusion mark and the state after it, or a declared rejection. A sentence has
one reading when it has exactly one derivation and that derivation has a meaning. `readSentence`
computes the verdict first and the meaning second; `readDocument` reads the sentences in order and
stops at the first outcome that is not `ok`. No statement here has a typing hypothesis.
-/

namespace VE.Grammar

/-- From the state before a sentence and a tree: the sentence's value, its conclusion mark and the
state after it; or a declared rejection. -/
abbrev Meaning (T σ ρ α : Type) := σ → Tree T → Except ρ (α × Bool × σ)

section Defs

variable {T K σ ρ α : Type} [Accepts K T]

/-- One derivation, and its complete result. -/
def OneReading (G : Grammar K) (μ : Meaning T σ ρ α) (st : σ) (w : List T) (A : α) (c : Bool) (st2 : σ) : Prop :=
  ∃ t, Derives G (.n G.start) w t ∧ (∀ u, Derives G (.n G.start) w u → u = t) ∧ μ st t = .ok (A, c, st2)

/-- A document: its sentences read in order, the state threaded. Every value and mark is exposed. -/
def DocOneReading (G : Grammar K) (μ : Meaning T σ ρ α) : σ → List (List T) → List (α × Bool) → σ → Prop
  | st, [], [], st2 => st2 = st
  | st, w :: ws, (A, c) :: rs, st2 =>
      ∃ st1, OneReading G μ st w A c st1 ∧ DocOneReading G μ st1 ws rs st2
  | _, _, _, _ => False

end Defs

inductive Outcome (T ρ α : Type) where
  | ok (A : α) (conclusion : Bool)
  | noDerivation
  | ambiguous (t u : Tree T)
  | rejected (r : ρ)
  | budget

inductive DocOutcome (T ρ α : Type) where
  | ok (rs : List (α × Bool))
  | stopped (index : Nat) (o : Outcome T ρ α)

variable {T K σ ρ α : Type} [DecidableEq T] [DecidableEq K] [Accepts K T]

def readSentence (G : Grammar K) (μ : Meaning T σ ρ α) (st : σ) (b : Nat) (w : Array T) : Outcome T ρ α × σ :=
  match verdict G b w with
  | none => (.budget, st)
  | some .zero => (.noDerivation, st)
  | some (.many t u) => (.ambiguous t u, st)
  | some (.one t) =>
      match μ st t with
      | .ok (A, c, st2) => (.ok A c, st2)
      | .error r => (.rejected r, st)

/-- Translation mode: the results of the listed trees that have a meaning. -/
def readingSet (μ : Meaning T σ ρ α) (st : σ) (ts : List (Tree T)) : List (α × Bool × σ) :=
  ts.filterMap fun t => match μ st t with
    | .ok x => some x
    | .error _ => none

/-- Reads the sentences in order and stops at the first outcome that is not `ok`. The state returned
with `stopped` is the state before that sentence. -/
def readDocument (G : Grammar K) (μ : Meaning T σ ρ α) (st : σ) (b : Nat) : List (Array T) →
    DocOutcome T ρ α × σ
  | [] => (.ok [], st)
  | w :: ws =>
    match readSentence G μ st b w with
    | (.ok A c, st1) =>
      match readDocument G μ st1 b ws with
      | (.ok rs, st2) => (.ok ((A, c) :: rs), st2)
      | (.stopped i o, st2) => (.stopped (i + 1) o, st2)
    | (o, _) => (.stopped 0 o, st)

variable {G : Grammar K} {μ : Meaning T σ ρ α} {st st1 st2 st3 : σ} {b cap : Nat}
variable {w : Array T} {ws : List (Array T)} {A B : α} {c d : Bool} {t u : Tree T} {r : ρ}

theorem read_sound : G.wf = true → readSentence G μ st b w = (.ok A c, st2) →
    OneReading G μ st w.toList A c st2 := by
  intro hG h
  unfold readSentence at h
  split at h
  · simp at h
  · simp at h
  · simp at h
  · rename_i t ht
    split at h
    · rename_i A2 c2 s2 hm
      simp only [Prod.mk.injEq, Outcome.ok.injEq] at h
      obtain ⟨⟨rfl, rfl⟩, rfl⟩ := h
      obtain ⟨hd, hu⟩ := verdict_one hG ht
      exact ⟨t, hd, hu, hm⟩
    · simp at h

theorem read_complete : G.wf = true → OneReading G μ st w.toList A c st2 →
    readSentence G μ st b w = (.ok A c, st2) ∨ readSentence G μ st b w = (.budget, st) := by
  rintro hG ⟨t, hd, hu, hm⟩
  unfold readSentence
  split
  · right; rfl
  · rename_i hv
    exact absurd hd (verdict_zero hG hv t)
  · rename_i t1 u1 hv
    obtain ⟨h1, h2, hne⟩ := verdict_many hv
    exact absurd ((hu t1 h1).trans (hu u1 h2).symm) hne
  · rename_i t1 hv
    have := (verdict_one hG hv).2 t hd
    subst this
    rw [hm]
    left; rfl

theorem read_none : G.wf = true → readSentence G μ st b w = (.noDerivation, st2) →
    st2 = st ∧ ∀ u, ¬ Derives G (.n G.start) w.toList u := by
  intro hG h
  unfold readSentence at h
  split at h
  · simp at h
  · rename_i hv
    simp only [Prod.mk.injEq, true_and] at h
    exact ⟨h.symm, verdict_zero hG hv⟩
  · simp at h
  · split at h <;> simp at h

theorem read_ambiguous : readSentence G μ st b w = (.ambiguous t u, st2) →
    st2 = st ∧ Derives G (.n G.start) w.toList t ∧ Derives G (.n G.start) w.toList u ∧ t ≠ u := by
  intro h
  unfold readSentence at h
  split at h
  · simp at h
  · simp at h
  · rename_i t1 u1 hv
    simp only [Prod.mk.injEq, Outcome.ambiguous.injEq] at h
    obtain ⟨⟨rfl, rfl⟩, rfl⟩ := h
    exact ⟨rfl, verdict_many hv⟩
  · split at h <;> simp at h

theorem read_rejected : G.wf = true → readSentence G μ st b w = (.rejected r, st2) →
    st2 = st ∧ ∃ t, Derives G (.n G.start) w.toList t ∧
      (∀ u, Derives G (.n G.start) w.toList u → u = t) ∧ μ st t = .error r := by
  intro hG h
  unfold readSentence at h
  split at h
  · simp at h
  · simp at h
  · simp at h
  · rename_i t ht
    split at h
    · simp at h
    · rename_i r2 hm
      simp only [Prod.mk.injEq, Outcome.rejected.injEq] at h
      obtain ⟨rfl, rfl⟩ := h
      obtain ⟨hd, hu⟩ := verdict_one hG ht
      exact ⟨rfl, t, hd, hu, hm⟩

omit [DecidableEq T] [DecidableEq K] in
theorem one_reading_unique {w : List T} : OneReading G μ st w A c st2 → OneReading G μ st w B d st3 →
    B = A ∧ d = c ∧ st3 = st2 := by
  rintro ⟨t, hd, hu, hm⟩ ⟨t2, hd2, _, hm2⟩
  have := hu t2 hd2
  subst this
  rw [hm] at hm2
  simp only [Except.ok.injEq, Prod.mk.injEq] at hm2
  exact ⟨hm2.1.symm, hm2.2.1.symm, hm2.2.2.symm⟩

omit [DecidableEq T] [DecidableEq K] in
theorem one_reading_single {w : List T} : OneReading G μ st w A c st2 → Derives G (.n G.start) w t →
    μ st t = .ok (B, d, st3) → B = A ∧ d = c ∧ st3 = st2 := by
  rintro ⟨t2, _, hu, hm⟩ hd hmt
  have := hu t hd
  subst this
  rw [hm] at hmt
  simp only [Except.ok.injEq, Prod.mk.injEq] at hmt
  exact ⟨hmt.1.symm, hmt.2.1.symm, hmt.2.2.symm⟩

omit [DecidableEq K] [Accepts K T] in
theorem mem_readingSet {ts : List (Tree T)} {x : α × Bool × σ} :
    x ∈ readingSet μ st ts ↔ ∃ t ∈ ts, μ st t = .ok x := by
  unfold readingSet
  rw [List.mem_filterMap]
  constructor
  · rintro ⟨t, ht, hm⟩
    refine ⟨t, ht, ?_⟩
    split at hm
    · rename_i y hy; simp at hm; rw [hy, hm]
    · simp at hm
  · rintro ⟨t, ht, hm⟩
    exact ⟨t, ht, by rw [hm]⟩

theorem readings_exact {ts : List (Tree T)} {x : α × Bool × σ} :
    G.wf = true → parse G cap b w = some ts → ts.length < cap →
    (x ∈ readingSet μ st ts ↔ ∃ t, Derives G (.n G.start) w.toList t ∧ μ st t = .ok x) := by
  intro hG hp hl
  rw [mem_readingSet]
  constructor
  · rintro ⟨t, ht, hm⟩
    exact ⟨t, parse_sound hp ht, hm⟩
  · rintro ⟨t, hd, hm⟩
    exact ⟨t, parse_complete hG hp hl hd, hm⟩

variable {rs rs2 : List (α × Bool)} {i : Nat} {o : Outcome T ρ α}

theorem doc_sound : G.wf = true → readDocument G μ st b ws = (.ok rs, st2) →
    DocOneReading G μ st (ws.map (·.toList)) rs st2 := by
  intro hG
  induction ws generalizing st rs with
  | nil =>
    intro h
    simp only [readDocument, Prod.mk.injEq, DocOutcome.ok.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    simp [DocOneReading]
  | cons w ws ih =>
    intro h
    unfold readDocument at h
    split at h
    · rename_i A c st1 hs
      split at h
      · rename_i rs1 st4 hr
        simp only [Prod.mk.injEq, DocOutcome.ok.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨st1, read_sound hG hs, ih hr⟩
      · simp at h
    · simp at h

theorem doc_complete : G.wf = true → DocOneReading G μ st (ws.map (·.toList)) rs st2 →
    readDocument G μ st b ws = (.ok rs, st2) ∨
    ∃ i st1, readDocument G μ st b ws = (.stopped i .budget, st1) := by
  intro hG
  induction ws generalizing st rs with
  | nil =>
    intro h
    match rs, h with
    | [], h =>
      simp only [List.map_nil, DocOneReading] at h
      subst h
      left; rfl
  | cons w ws ih =>
    intro h
    match rs, h with
    | (A, c) :: rs1, ⟨st1, h1, h2⟩ =>
      unfold readDocument
      rcases read_complete (b := b) hG h1 with hs | hs
      · rw [hs]
        simp only
        rcases ih h2 with hr | ⟨i, st4, hr⟩
        · rw [hr]; left; rfl
        · rw [hr]; right; exact ⟨i + 1, st4, rfl⟩
      · rw [hs]
        right; exact ⟨0, st, rfl⟩

theorem doc_stopped : G.wf = true → readDocument G μ st b ws = (.stopped i o, st1) →
    ∃ rs w, DocOneReading G μ st ((ws.take i).map (·.toList)) rs st1 ∧ ws[i]? = some w ∧
      (readSentence G μ st1 b w).1 = o ∧ ∀ A c, o ≠ .ok A c := by
  intro hG
  induction ws generalizing st i with
  | nil => intro h; simp [readDocument] at h
  | cons w ws ih =>
    intro h
    unfold readDocument at h
    split at h
    · rename_i A c st4 hs
      split at h
      · simp at h
      · rename_i i2 o2 st5 hr
        simp only [Prod.mk.injEq, DocOutcome.stopped.injEq] at h
        obtain ⟨⟨rfl, rfl⟩, rfl⟩ := h
        obtain ⟨rs, w2, hd, hw, ho, hne⟩ := ih hr
        exact ⟨(A, c) :: rs, w2, ⟨st4, read_sound hG hs, hd⟩, by simpa using hw, ho, hne⟩
    · rename_i o2 st4 hnot hs
      simp only [Prod.mk.injEq, DocOutcome.stopped.injEq] at h
      obtain ⟨⟨rfl, rfl⟩, rfl⟩ := h
      refine ⟨[], w, by simp [DocOneReading], by simp, ?_, ?_⟩
      · rw [hs]
      · intro A c he
        subst he
        exact hnot A c rfl

omit [DecidableEq T] [DecidableEq K] in
theorem doc_unique {ws : List (List T)} : DocOneReading G μ st ws rs st2 → DocOneReading G μ st ws rs2 st3 →
    rs2 = rs ∧ st3 = st2 := by
  induction ws generalizing st rs rs2 with
  | nil =>
    intro h1 h2
    match rs, rs2, h1, h2 with
    | [], [], h1, h2 => simp only [DocOneReading] at h1 h2; exact ⟨rfl, h2.trans h1.symm⟩
  | cons w ws ih =>
    intro h1 h2
    match rs, rs2, h1, h2 with
    | (A, c) :: rs1, (B, d) :: rs3, ⟨s1, h1a, h1b⟩, ⟨s2, h2a, h2b⟩ =>
      obtain ⟨rfl, rfl, rfl⟩ := one_reading_unique h1a h2a
      obtain ⟨rfl, rfl⟩ := ih h1b h2b
      exact ⟨rfl, rfl⟩

end VE.Grammar
