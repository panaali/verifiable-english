import VE.SpeechActs.Demand

/-! Questions and answers (docs/spec/speech-acts.md 1.3, 4.4, 4.5 and 8.3): the
presupposition `H(q)`, the response tokens, the correctness formula `F(q, a)`,
`AnswersAt` (the spec's `Answers(q, S)` as a predicate on tokens), the finite
evaluator's answer test, and the proof-path and model-path theorems.

`P(a)` is W1's capture-avoiding `inst [.const a] q.body` (`instAt`). A
complete-list token is a sublist of the domain in domain order; the token list
of a complete-list question is every such sublist (`sublistsOf`), while
`correct` tests membership with `List.isSublist` and never enumerates. Follows
and reading questions have no answer tokens: their outcomes are the judgments
of `Consequence.lean` and the nomination records of the wire. -/
namespace VE.SpeechActs
open VE.Norms (anyF allF anyF_denote allF_denote inst Sat)
universe u

/-- `P(a)`: the body instantiated at the alternative. -/
def instAt (q : Question) (a : String) : VE.Formula := inst [.const a] q.body

/-- Every sublist of a list, in list order. -/
def sublistsOf : List String → List (List String)
  | [] => [[]]
  | x :: xs => (sublistsOf xs).map (x :: ·) ++ sublistsOf xs

/-- `F(S) = ⋀_{a∈S} P(a) ∧ ⋀_{a∈dom∖S} ¬P(a)`. -/
def allAnswer (q : Question) (S : List String) : VE.Formula :=
  .and (allF (S.map (instAt q))) (allF ((q.domain.filter (fun a => !S.contains a)).map (fun a => .not (instAt q a))))

/-- 1.3: presupposition, tokens and correctness. -/
def presupposition (_D : SpeechDoc) (q : Question) : VE.Formula :=
  match q.mode with
  | .whichOne => .and (anyF (q.domain.map (instAt q)))
      (allF ((pairsOf q.domain).map (fun (a, b) => .not (.and (instAt q a) (instAt q b)))))
  | _ => .top

def tokens (_D : SpeechDoc) (q : Question) : List Answer :=
  match q.mode with
  | .polar => [.yes, .no]
  | .whichOne => q.domain.map .one
  | .whichAll => (sublistsOf q.domain).map .all
  | .follows | .reading => []

def correct (_D : SpeechDoc) (q : Question) : Answer → Option VE.Formula := fun a =>
  match q.mode, a with
  | .polar, .yes => some q.body
  | .polar, .no => some (.not q.body)
  | .whichOne, .one x => if q.domain.contains x then some (instAt q x) else none
  | .whichAll, .all S => if S.isSublist q.domain then some (allAnswer q S) else none
  | _, _ => none

def AnswersAt (D : SpeechDoc) (q : Question) (S : VE.Structure) (a : Answer) : Prop :=
  a ∈ tokens D q ∧ (presupposition D q).denote S [] ∧ ∃ φ, correct D q a = some φ ∧ φ.denote S []

/-- The finite evaluator's answer test (model path). -/
def answerEval {α} [DecidableEq α] (D : SpeechDoc) (q : Question) (M : VE.FiniteModel α) (a : Answer) : Bool :=
  match correct D q a with
  | some φ => (presupposition D q).eval M [] && φ.eval M []
  | none => false

/-! ## Lemmas -/

theorem mem_sublistsOf : ∀ (L T : List String), T ∈ sublistsOf L ↔ T.Sublist L
  | [], T => by simp [sublistsOf]
  | x :: xs, T => by
    simp only [sublistsOf, List.mem_append, List.mem_map, mem_sublistsOf xs, List.sublist_cons_iff]
    constructor
    · rintro (⟨r, hr, rfl⟩ | h)
      · exact Or.inr ⟨r, rfl, hr⟩
      · exact Or.inl h
    · rintro (h | ⟨r, rfl, hr⟩)
      · exact Or.inr h
      · exact Or.inl ⟨r, hr, rfl⟩

/-- Two sublists of a duplicate-free list with the same members are equal. -/
theorem sublist_ext : ∀ {L l₁ l₂ : List String}, L.Nodup → l₁.Sublist L → l₂.Sublist L →
    (∀ x ∈ L, x ∈ l₁ ↔ x ∈ l₂) → l₁ = l₂
  | [], l₁, l₂, _, h₁, h₂, _ => by rw [List.sublist_nil.mp h₁, List.sublist_nil.mp h₂]
  | x :: xs, l₁, l₂, hL, h₁, h₂, hm => by
    obtain ⟨hx, hxs⟩ := List.nodup_cons.mp hL
    have hm' : ∀ y ∈ xs, y ∈ l₁ ↔ y ∈ l₂ := fun y hy => hm y (List.mem_cons_of_mem _ hy)
    rcases List.sublist_cons_iff.mp h₁ with h₁' | ⟨r₁, rfl, h₁'⟩
    · rcases List.sublist_cons_iff.mp h₂ with h₂' | ⟨r₂, rfl, h₂'⟩
      · exact sublist_ext hxs h₁' h₂' hm'
      · exact absurd (h₁'.subset ((hm x List.mem_cons_self).mpr List.mem_cons_self)) hx
    · rcases List.sublist_cons_iff.mp h₂ with h₂' | ⟨r₂, rfl, h₂'⟩
      · exact absurd (h₂'.subset ((hm x List.mem_cons_self).mp List.mem_cons_self)) hx
      · congr 1
        refine sublist_ext hxs h₁' h₂' (fun y hy => ?_)
        have hne : y ≠ x := fun e => hx (e ▸ hy)
        have := hm' y hy
        simp only [List.mem_cons, hne, false_or] at this
        exact this

theorem mem_pairsOf {α : Type} {a b : α} : ∀ {L : List α}, a ∈ L → b ∈ L → a ≠ b →
    (a, b) ∈ pairsOf L ∨ (b, a) ∈ pairsOf L
  | x :: xs, ha, hb, hab => by
    simp only [pairsOf, List.mem_append, List.mem_map, Prod.mk.injEq]
    rcases List.mem_cons.mp ha with rfl | ha' <;> rcases List.mem_cons.mp hb with rfl | hb'
    · exact absurd rfl hab
    · exact Or.inl (Or.inl ⟨b, hb', rfl, rfl⟩)
    · exact Or.inr (Or.inl ⟨a, ha', rfl, rfl⟩)
    · rcases mem_pairsOf ha' hb' hab with h | h
      · exact Or.inl (Or.inr h)
      · exact Or.inr (Or.inr h)

theorem correct_mem_tokens {D : SpeechDoc} {q : Question} {a : Answer} {φ : VE.Formula}
    (h : correct D q a = some φ) : a ∈ tokens D q := by
  unfold correct at h
  unfold tokens
  split at h
  · rename_i hm; simp [hm]
  · rename_i hm; simp [hm]
  · rename_i x hm
    rw [hm]
    split at h
    · rename_i hx; exact List.mem_map_of_mem (List.contains_iff_mem.mp hx)
    · cases h
  · rename_i S hm
    rw [hm]
    split at h
    · rename_i hs
      exact List.mem_map_of_mem ((mem_sublistsOf _ _).mpr (List.isSublist_iff_sublist.mp hs))
    · cases h
  · cases h

theorem tokens_correct {D : SpeechDoc} {q : Question} {a : Answer} (h : a ∈ tokens D q) :
    ∃ φ, correct D q a = some φ := by
  unfold tokens at h
  unfold correct
  cases hm : q.mode <;> rw [hm] at h <;> simp only [List.mem_cons, List.mem_nil_iff, or_false,
    List.mem_map] at h
  · rcases h with rfl | rfl <;> simp
  · obtain ⟨S, hS, rfl⟩ := h
    have : S.isSublist q.domain = true := List.isSublist_iff_sublist.mpr ((mem_sublistsOf _ _).mp hS)
    simp [this]
  · obtain ⟨x, hx, rfl⟩ := h
    simp [hx]

theorem correct_polar {D : SpeechDoc} {q : Question} (hm : q.mode = .polar) :
    correct D q .yes = some q.body ∧ correct D q .no = some (.not q.body) := by
  simp [correct, hm]

theorem correct_one {D : SpeechDoc} {q : Question} (hm : q.mode = .whichOne) {a : String} {φ : VE.Formula}
    (h : correct D q (.one a) = some φ) : a ∈ q.domain ∧ φ = instAt q a := by
  simp only [correct, hm] at h
  split at h
  · rename_i hx; cases h; exact ⟨List.contains_iff_mem.mp hx, rfl⟩
  · cases h

theorem presupposition_one {D : SpeechDoc} {q : Question} (hm : q.mode = .whichOne) (S : VE.Structure.{u})
    (hH : (presupposition D q).denote S []) {a b : String} (ha : a ∈ q.domain) (hb : b ∈ q.domain)
    (hab : a ≠ b) : ¬ ((instAt q a).denote S [] ∧ (instAt q b).denote S []) := by
  simp only [presupposition, hm, VE.Formula.denote, allF_denote, List.mem_map] at hH
  rcases mem_pairsOf ha hb hab with hp | hp
  · exact hH.2 _ ⟨_, hp, rfl⟩
  · intro ⟨h₁, h₂⟩; exact hH.2 _ ⟨_, hp, rfl⟩ ⟨h₂, h₁⟩

theorem not_contains_iff (S : List String) (a : String) : (!S.contains a) = true ↔ a ∉ S := by
  cases h : S.contains a
  · simp only [Bool.not_false, true_iff]
    exact fun hm => by rw [List.contains_iff_mem.mpr hm] at h; cases h
  · simp only [Bool.not_true, Bool.false_eq_true, false_iff]
    exact fun hn => hn (List.contains_iff_mem.mp h)

theorem allAnswer_denote (q : Question) (S : VE.Structure.{u}) (T : List String) :
    (allAnswer q T).denote S [] ↔
      (∀ a ∈ T, (instAt q a).denote S []) ∧ (∀ a ∈ q.domain, a ∉ T → ¬ (instAt q a).denote S []) := by
  simp only [allAnswer, VE.Formula.denote, allF_denote, List.mem_map, List.mem_filter, not_contains_iff]
  constructor
  · rintro ⟨h₁, h₂⟩
    exact ⟨fun a ha => h₁ _ ⟨a, ha, rfl⟩, fun a ha hn => h₂ _ ⟨a, ⟨ha, hn⟩, rfl⟩⟩
  · rintro ⟨h₁, h₂⟩
    exact ⟨fun _ ⟨a, ha, e⟩ => e ▸ h₁ a ha, fun _ ⟨a, ⟨ha, hn⟩, e⟩ => e ▸ h₂ a ha hn⟩

theorem which_nodup {D : SpeechDoc} (h : WellFormedSpeech D = true) {q : Question} (hq : q ∈ D.questions)
    (hm : q.mode = .whichAll ∨ q.mode = .whichOne) : q.domain.Nodup := by
  have hk := (validSpeech_of_wellFormed D h).questions q hq
  unfold questionOk at hk
  rcases hm with hm | hm <;> rw [hm] at hk <;> simp only at hk <;>
  · split at hk
    · simp only [Bool.and_eq_true, decide_eq_true_eq] at hk
      exact hk.1.1.2
    · cases hk

/-! ## 8.3 -/

/-- 4.4: at most one polar answer; at most one single-choice answer; exactly one complete-list answer; none when H fails. -/
theorem answers_polar (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .polar) (S : VE.Structure) : ¬ (AnswersAt D q S .yes ∧ AnswersAt D q S .no) := by
  rintro ⟨⟨_, _, φ, hφ, hy⟩, ⟨_, _, ψ, hψ, hn⟩⟩
  rw [(correct_polar hm).1] at hφ
  rw [(correct_polar hm).2] at hψ
  cases hφ; cases hψ
  exact hn hy

theorem answers_one (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .whichOne) (S : VE.Structure) (a b : String) :
    AnswersAt D q S (.one a) → AnswersAt D q S (.one b) → a = b := by
  rintro ⟨_, hH, φ, hφ, ha⟩ ⟨_, _, ψ, hψ, hb⟩
  obtain ⟨hma, rfl⟩ := correct_one hm hφ
  obtain ⟨hmb, rfl⟩ := correct_one hm hψ
  by_cases hab : a = b
  · exact hab
  · exact absurd ⟨ha, hb⟩ (presupposition_one hm S hH hma hmb hab)

theorem answersAt_all_iff {D : SpeechDoc} {q : Question} (hm : q.mode = .whichAll) (S : VE.Structure)
    (T : List String) : AnswersAt D q S (.all T) ↔ T.Sublist q.domain ∧
      (∀ a ∈ T, (instAt q a).denote S []) ∧ (∀ a ∈ q.domain, a ∉ T → ¬ (instAt q a).denote S []) := by
  simp only [AnswersAt, tokens, presupposition, correct, hm, List.mem_map, mem_sublistsOf, Answer.all.injEq,
    exists_eq_right, VE.Formula.denote, true_and]
  constructor
  · rintro ⟨hs, φ, hφ, hd⟩
    have hb : T.isSublist q.domain = true := List.isSublist_iff_sublist.mpr hs
    rw [if_pos hb] at hφ
    cases hφ
    exact ⟨hs, (allAnswer_denote q S T).mp hd⟩
  · rintro ⟨hs, hd⟩
    have hb : T.isSublist q.domain = true := List.isSublist_iff_sublist.mpr hs
    exact ⟨hs, _, by rw [if_pos hb], (allAnswer_denote q S T).mpr hd⟩

theorem answers_all (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .whichAll) (S : VE.Structure) (hS : S.Admissible (En D)) :
    ∃ T : List String, AnswersAt D q S (.all T) ∧ ∀ T₂ : List String, AnswersAt D q S (.all T₂) → T₂ = T := by
  classical
  have hnd := which_nodup h hq (Or.inl hm)
  have hT := answersAt_all_iff (D := D) hm S
  let T := q.domain.filter (fun a => decide ((instAt q a).denote S []))
  have hsub : T.Sublist q.domain := List.filter_sublist
  have hmemT : ∀ a ∈ q.domain, a ∈ T ↔ (instAt q a).denote S [] := fun a ha => by
    simp [T, List.mem_filter, ha]
  refine ⟨T, (hT T).mpr ⟨hsub, fun a ha => (hmemT a (hsub.subset ha)).mp ha,
    fun a ha hn => fun hp => hn ((hmemT a ha).mpr hp)⟩, fun T₂ h₂ => ?_⟩
  obtain ⟨hs₂, hp₂, hn₂⟩ := (hT T₂).mp h₂
  refine sublist_ext hnd hs₂ hsub (fun a ha => ?_)
  rw [hmemT a ha]
  exact ⟨fun hm₂ => hp₂ a hm₂, fun hp => Classical.byContradiction fun hn => hn₂ a ha hn hp⟩
theorem answers_all_empty (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .whichAll) (S : VE.Structure) (hS : S.Admissible (En D))
    (hnone : ∀ a ∈ q.domain, ¬ (inst [.const a] q.body).denote S []) : AnswersAt D q S (.all []) :=
  (answersAt_all_iff hm S []).mpr ⟨List.nil_sublist _, by simp, fun a ha _ => hnone a ha⟩

theorem answers_presupposition (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (S : VE.Structure) (hH : ¬ (presupposition D q).denote S []) : ∀ a : Answer, ¬ AnswersAt D q S a :=
  fun _ ha => hH ha.2.1

/-- 4.5, proof path. -/
theorem support_sound (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (a : Answer) (φ : VE.Formula) (hφ : correct D q a = some φ) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) φ) c = true) :
    ∀ S : VE.Structure, S.Admissible (En D) → Sat S (premises D) → AnswersAt D q S a := by
  intro S hS hp
  have hd := VE.Tableau.checkCertificate_sound _ _ _ c acc S hS hp
  exact ⟨correct_mem_tokens hφ, hd.1, φ, hφ, hd.2⟩

theorem support_conditional_sound (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question)
    (hq : q ∈ D.questions) (a : Answer) (φ : VE.Formula) (hφ : correct D q a = some φ) (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (En D) (premises D ++ [presupposition D q]) φ c = true) :
    ∀ S : VE.Structure, S.Admissible (En D) → Sat S (premises D) → (presupposition D q).denote S [] →
      AnswersAt D q S a := by
  intro S hS hp hH
  have hd := VE.Tableau.checkCertificate_sound _ _ _ c acc S hS (fun b hb => by
    rcases List.mem_append.mp hb with hb | hb
    · exact hp b hb
    · rw [List.mem_singleton.mp hb]; exact hH)
  exact ⟨correct_mem_tokens hφ, hH, φ, hφ, hd⟩

/-- Opposite polar answers are both supported only over unsatisfiable premises. -/
theorem support_exclusive (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .polar) (cy cn : VE.Tableau.Certificate)
    (hy : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) q.body) cy = true)
    (hn : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) (.not q.body)) cn = true) :
    ¬ ∃ S : VE.Structure, S.Admissible (En D) ∧ Sat S (premises D) := by
  rintro ⟨S, hS, hp⟩
  exact (VE.Tableau.checkCertificate_sound _ _ _ cn hn S hS hp).2
    (VE.Tableau.checkCertificate_sound _ _ _ cy hy S hS hp).2

/-- Two distinct single-choice answers are both supported only over unsatisfiable premises (4.5's second clause). -/
theorem support_exclusive_one (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question) (hq : q ∈ D.questions)
    (hm : q.mode = .whichOne) (a b : String) (hab : a ≠ b) (φa φb : VE.Formula)
    (hφa : correct D q (.one a) = some φa) (hφb : correct D q (.one b) = some φb) (ca cb : VE.Tableau.Certificate)
    (ha : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) φa) ca = true)
    (hb : VE.Tableau.checkCertificate (En D) (premises D) (.and (presupposition D q) φb) cb = true) :
    ¬ ∃ S : VE.Structure, S.Admissible (En D) ∧ Sat S (premises D) := by
  rintro ⟨S, hS, hp⟩
  obtain ⟨hma, rfl⟩ := correct_one hm hφa
  obtain ⟨hmb, rfl⟩ := correct_one hm hφb
  have da := VE.Tableau.checkCertificate_sound _ _ _ ca ha S hS hp
  have db := VE.Tableau.checkCertificate_sound _ _ _ cb hb S hS hp
  exact presupposition_one hm S da.1 hma hmb hab ⟨da.2, db.2⟩

/-- 4.5, model path: the evaluator's answers are exactly AnswersAt in that model; a failed presupposition yields none. -/
theorem model_answers {α : Type} [DecidableEq α] (D : SpeechDoc) (h : WellFormedSpeech D = true) (q : Question)
    (hq : q ∈ D.questions) (M : VE.FiniteModel α) (valid : M.Valid (En D))
    (hb : VE.Norms.backgroundValid (policy D) M = true) (hp : (premises D).all (fun φ => φ.eval M []) = true)
    (a : Answer) : answerEval D q M a = true ↔ AnswersAt D q M.asStructure a := by
  unfold answerEval
  constructor
  · intro he
    split at he
    · rename_i φ hφ
      simp only [Bool.and_eq_true, VE.eval_iff_denote] at he
      exact ⟨correct_mem_tokens hφ, he.1, φ, hφ, he.2⟩
    · cases he
  · rintro ⟨_, hH, φ, hφ, hd⟩
    rw [hφ]
    simp only [Bool.and_eq_true, VE.eval_iff_denote]
    exact ⟨hH, hd⟩

theorem model_presupposition_failed {α : Type} [DecidableEq α] (D : SpeechDoc) (h : WellFormedSpeech D = true)
    (q : Question) (hq : q ∈ D.questions) (M : VE.FiniteModel α)
    (hH : (presupposition D q).eval M [] = false) : ∀ a : Answer, answerEval D q M a = false := by
  intro a
  unfold answerEval
  split
  · simp [hH]
  · rfl

/-- A countermodel to P is evidence about that model only: it does not give ¬P over the premises. The second conjunct
    needs the hypothesis that some admissible model of the premises satisfies `q.body`: over the premises `[¬P]` a
    countermodel to `P` exists and every premise model satisfies `¬P`, so without `S'` the conjunct is false
    (fixture η's regression). `S'` and the quantified `S` range over one universe. -/
theorem countermodel_not_negative {α : Type} [DecidableEq α] (D : SpeechDoc) (h : WellFormedSpeech D = true)
    (q : Question) (hq : q ∈ D.questions) (hm : q.mode = .polar) (M : VE.FiniteModel α)
    (valid : M.Valid (En D)) (hp : (premises D).all (fun φ => φ.eval M []) = true) (hn : q.body.eval M [] = false)
    (S' : VE.Structure.{u}) (hS' : S'.Admissible (En D)) (hp' : Sat S' (premises D)) (hb' : q.body.denote S' []) :
    AnswersAt D q M.asStructure .no ∧
      ¬ (∀ S : VE.Structure.{u}, S.Admissible (En D) → Sat S (premises D) → AnswersAt D q S .no) := by
  refine ⟨⟨by simp [tokens, hm], by simp [presupposition, hm, VE.Formula.denote], _, (correct_polar hm).2,
    (VE.eval_false_iff_not_denote M [] _).mp hn⟩, fun hall => ?_⟩
  obtain ⟨_, _, φ, hφ, hd⟩ := hall S' hS' hp'
  rw [(correct_polar hm).2] at hφ
  cases hφ
  exact hd hb'

end VE.SpeechActs
