import VE.Ask.Basic
import VE.EnglishGrammar.Encode

/-! The reasons of an answer: exactly the premises the certificate needs (docs/spec/question-answering.md 5.2; plan
4.3, D7, D8, R10, Q2.1).

`sourcesU` names where each premise of RD-3's `premisesU U Γ` comes from, position by position. `sourced` builds the
premises and their sources together, segment by segment from the same lists `premisesU` reads, so
`sourcesU_zip_premisesU` pins every position's source to that position's premise, in `premisesU`'s order (Background:
definitions, `Background_base`, pair premises; then `Fill_T`; then the layer premises; then the assertions).
`sourcesU_length` alone would let the segments be shuffled. `usedPositions` is RD-3's `usedLabels` over the
certificate's replay, one label per position; the used premises alone entail the conclusion
(`usedPositions_sufficient`), and `cited` is exactly the sources of the used positions, once each, in order of first
use (`mem_cited`, `cited_nodup`). -/

namespace VE.Ask
open VE.Readings VE.NormDefaults
open VE.Norms (syms Sym backgroundBase pairs elabPremise)
universe u

inductive Source
  | unit (id : String)
  | rules (pred : String)          -- the layer premise of one regulated predicate; its units are named at render
  | definition (name : String)
  | background
  | pair (req perm : String)
  | fill (req perm : String)
  deriving DecidableEq, Repr

/-- Where each premise of `premisesU U Γ` comes from, in its order: `background (fill U)` (definitions, then
    `Background_base`, then the pair premises), then `fillPremises U`, then `elaborate (fill U).T`, then the
    assertions, whose sources are given. -/
def sourcesU (U : UDoc) (assertions : List Source) : List Source :=
  let T := (fill U).T
  (VE.Norms.syms T).filterMap (fun | .defn d => some (Source.definition d.name) | .reg _ => none) ++
  (VE.Norms.backgroundBase (fill U)).map (fun _ => Source.background) ++
  (VE.Norms.pairs T).map (fun pr => Source.pair pr.req pr.perm) ++
  ((VE.Norms.pairs U.D.T).filter (fun pr => pr.req ∈ U.unspec ∨ pr.perm ∈ U.unspec)).map
    (fun pr => Source.fill pr.req pr.perm) ++
  (VE.Norms.syms T).filterMap (fun | .reg r => some (Source.rules r.name) | .defn _ => none) ++
  assertions

/-- One open pair's `Fill_T` premise, as `fillPremises` writes it. -/
def fillPremise (U : UDoc) (pr : VE.Norms.Pair) : VE.Formula :=
  VE.Norms.bindAll pr.sorts (.not (.and (VE.Norms.pairConflict (fill U) pr)
    (.or (VE.NormDefaults.gapF U pr.req) (VE.NormDefaults.gapF U pr.perm))))

/-- Each premise of `premisesU U Γ` with its source, segment by segment from the very lists `premisesU` reads. -/
def sourced (U : UDoc) (as : List (Source × VE.Formula)) : List (Source × VE.Formula) :=
  let T := (fill U).T
  (syms T).filterMap (fun | .defn d => some (Source.definition d.name, d.premise) | .reg _ => none) ++
  (backgroundBase (fill U)).map (fun f => (Source.background, f)) ++
  (pairs T).map (fun pr => (Source.pair pr.req pr.perm, pr.premise)) ++
  ((pairs U.D.T).filter (fun pr => pr.req ∈ U.unspec ∨ pr.perm ∈ U.unspec)).map
    (fun pr => (Source.fill pr.req pr.perm, fillPremise U pr)) ++
  (syms T).filterMap (fun | .reg r => some (Source.rules r.name, elabPremise T r) | .defn _ => none) ++
  as

theorem append_eq {α : Type} {l₁ l₂ l₃ l₄ : List α} (h₁ : l₁ = l₃) (h₂ : l₂ = l₄) : l₁ ++ l₂ = l₃ ++ l₄ := by
  rw [h₁, h₂]

theorem filterMap_ext {α β : Type} (l : List α) {f g : α → Option β} (h : ∀ a, f a = g a) :
    l.filterMap f = l.filterMap g := by
  rw [funext h]

theorem sourced_sources (U : UDoc) (as : List (Source × VE.Formula)) :
    (sourced U as).map (·.1) = sourcesU U (as.map (·.1)) := by
  simp only [sourced, sourcesU, List.map_append, List.map_filterMap, List.map_map]
  refine append_eq (append_eq (append_eq (append_eq
    (append_eq ?_ rfl) rfl) rfl) ?_) rfl
  · exact filterMap_ext _ (fun s => by cases s <;> rfl)
  · exact filterMap_ext _ (fun s => by cases s <;> rfl)

theorem sourced_premises (U : UDoc) (as : List (Source × VE.Formula)) :
    (sourced U as).map (·.2) = VE.NormDefaults.Wire.premisesU U (as.map (·.2)) := by
  simp only [sourced, VE.NormDefaults.Wire.premisesU, VE.Norms.background, VE.Norms.definitionPremises,
    VE.Norms.pairPremises, VE.NormDefaults.fillPremises, VE.Norms.elaborate, List.map_append, List.map_filterMap,
    List.map_map]
  refine append_eq (append_eq (append_eq (append_eq
    (append_eq ?_ ?_) ?_) ?_) ?_) ?_
  · exact filterMap_ext _ (fun s => by cases s <;> rfl)
  · simp [Function.comp_def]
  · simp [Function.comp_def]
  · simp [Function.comp_def, fillPremise]
  · exact filterMap_ext _ (fun s => by cases s <;> rfl)
  · simp

/-- Segment order: the `i`-th source names the `i`-th premise's origin, for every `i`. Given the assertions with their
    sources, the sources of `premisesU` zip with its premises into `sourced`. -/
theorem sourcesU_zip_premisesU : ∀ (U : UDoc) (as : List (Source × VE.Formula)),
    (sourcesU U (as.map (·.1))).zip (VE.NormDefaults.Wire.premisesU U (as.map (·.2))) = sourced U as := by
  intro U as
  rw [← sourced_sources, ← sourced_premises]
  induction sourced U as with
  | nil => rfl
  | cons x xs ih => simp [ih]

theorem sourcesU_length : ∀ (U : UDoc) (as : List Source) (Γ : List VE.Formula), as.length = Γ.length →
    (sourcesU U as).length = (VE.NormDefaults.Wire.premisesU U Γ).length := by
  intro U as Γ h
  have h1 := congrArg List.length (sourced_sources U (as.zip Γ))
  have h2 := congrArg List.length (sourced_premises U (as.zip Γ))
  simp only [List.length_map] at h1 h2
  have ha : (as.zip Γ).map (·.1) = as := by
    simpa using List.map_fst_zip (l₁ := as) (l₂ := Γ) (by omega)
  have hg : (as.zip Γ).map (·.2) = Γ := by
    simpa using List.map_snd_zip (l₁ := as) (l₂ := Γ) (by omega)
  rw [ha] at h1
  rw [hg] at h2
  omega

/-- The positions of a premise list as labels, the numeral of each position. -/
def positions (P : List VE.Formula) : VE.Compose.Labelled :=
  ((List.range P.length).zip P).map fun (i, f) => (toString i, f)

/-- R10: the replay without the meaning-id binding, which `ndBoundCert` checks once when the certificate is decoded. -/
def replayOk (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula) (k : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate E P ψ k

def usedPositions (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula) (k : VE.Tableau.Certificate) :
    List Nat :=
  (usedLabels (fun Q => replayOk E Q ψ k) [] (positions P) []).filterMap String.toNat?

theorem positions_labels (P : List VE.Formula) : (positions P).map (·.1) = (List.range P.length).map toString := by
  simp only [positions, List.map_map, Function.comp_def]
  have : ∀ (l : List Nat) (P : List VE.Formula), l.length = P.length →
      (l.zip P).map (fun x => toString x.1) = l.map toString := by
    intro l
    induction l with
    | nil => intro P _; rfl
    | cons a l ih =>
      intro P h
      cases P with
      | nil => simp at h
      | cons f P =>
        simp only [List.zip_cons_cons, List.map_cons, List.cons.injEq, true_and]
        exact ih P (by simpa using h)
  exact this _ _ (by simp)

theorem positions_get (P : List VE.Formula) :
    ∀ x ∈ positions P, ∃ i : Nat, x.1 = toString i ∧ P[i]? = some x.2 := by
  intro x hx
  simp only [positions, List.mem_map] at hx
  obtain ⟨⟨i, f⟩, hm, rfl⟩ := hx
  refine ⟨i, rfl, ?_⟩
  have hl := List.mem_iff_getElem.mp hm
  obtain ⟨n, hn, he⟩ := hl
  simp only [List.getElem_zip, List.getElem_range, Prod.mk.injEq] at he
  obtain ⟨rfl, rfl⟩ := he
  simp only [List.length_zip, List.length_range, Nat.min_self] at hn
  simp [hn]

theorem toString_inj {i j : Nat} (h : toString i = toString j) : i = j := by
  have hi := VE.EnglishGrammar.DecodeEncode.toNatOpt_toString i
  have hj := VE.EnglishGrammar.DecodeEncode.toNatOpt_toString j
  rw [h, hj] at hi
  exact (Option.some.inj hi).symm

theorem positions_wellLabelled (P : List VE.Formula) : (positions P).wellLabelled = true := by
  simp only [VE.Compose.Labelled.wellLabelled, decide_eq_true_eq, positions_labels]
  exact List.Pairwise.map toString (fun _ _ h he => h (toString_inj he)) List.nodup_range

/-- `⊤` premises change no entailment: a structure satisfying the kept premises satisfies the blanked list. -/
theorem blank_entails (E : VE.Environment) (P : List VE.Formula) (keep : List String) (ψ : VE.Formula)
    (h : VE.Entails.{u} E (blank (positions P) keep) ψ) :
    VE.Entails.{u} E ((keep.filterMap String.toNat?).filterMap (P[·]?)) ψ := by
  intro S hS hp
  apply h S hS
  intro a ha
  simp only [blank, List.mem_map] at ha
  obtain ⟨x, hx, rfl⟩ := ha
  split
  · rename_i hk
    obtain ⟨i, hi, hget⟩ := positions_get P x hx
    apply hp
    refine List.mem_filterMap.mpr ⟨i, List.mem_filterMap.mpr ⟨x.1, List.contains_iff_mem.mp hk, ?_⟩, hget⟩
    rw [hi]
    exact VE.EnglishGrammar.DecodeEncode.toNatOpt_toString i
  · exact trivial

theorem usedPositions_sufficient : ∀ (E : VE.Environment) (P : List VE.Formula) (ψ : VE.Formula)
    (k : VE.Tableau.Certificate), replayOk E P ψ k = true →
    VE.Entails.{u} E ((usedPositions E P ψ k).filterMap (P[·]?)) ψ := by
  intro E P ψ k h
  have hf : (positions P).formulas = P := by
    simp only [VE.Compose.Labelled.formulas, positions, List.map_map, Function.comp_def]
    have : ∀ (l : List Nat) (P : List VE.Formula), l.length = P.length → (l.zip P).map (fun x => x.2) = P := by
      intro l
      induction l with
      | nil => intro P h; cases P <;> simp_all
      | cons a l ih =>
        intro P h
        cases P with
        | nil => simp at h
        | cons f P => simp only [List.zip_cons_cons, List.map_cons, ih P (by simpa using h)]
    exact this _ _ (by simp)
  have hs := usedLabels_sound (fun Q => replayOk E Q ψ k) [] (positions P) [] (positions_wellLabelled P)
    (by simpa [hf] using h)
  simp only [List.nil_append, List.append_nil] at hs
  exact blank_entails E P _ ψ (VE.Tableau.checkCertificate_sound E _ ψ k hs)

theorem eraseDups_spec {α : Type} [BEq α] [LawfulBEq α] : ∀ (n : Nat) (l : List α), l.length ≤ n →
    (∀ a, a ∈ l.eraseDups ↔ a ∈ l) ∧ l.eraseDups.Nodup
  | 0, l, h => by
    cases l with
    | nil => simp
    | cons _ _ => simp at h
  | n + 1, [], _ => by simp
  | n + 1, a :: as, h => by
    rw [List.eraseDups_cons]
    have ih := eraseDups_spec n (as.filter fun b => !b == a)
      (Nat.le_trans (List.length_filter_le _ _) (by simp at h; omega))
    refine ⟨fun x => ?_, ?_⟩
    · simp only [List.mem_cons, ih.1, List.mem_filter, Bool.not_eq_true', beq_eq_false_iff_ne, ne_eq]
      by_cases hx : x = a <;> simp [hx]
    · refine List.nodup_cons.mpr ⟨?_, ih.2⟩
      rw [ih.1]
      simp

def cited (srcs : List Source) (used : List Nat) : List Source := (used.filterMap (srcs[·]?)).eraseDups

/-- Exactly the sources of the used positions: a source is cited when, and only when, some used position has it. -/
theorem mem_cited : ∀ (srcs : List Source) (used : List Nat) (s : Source),
    s ∈ cited srcs used ↔ ∃ i ∈ used, srcs[i]? = some s := by
  intro srcs used s
  simp only [cited, (eraseDups_spec _ _ (Nat.le_refl _)).1, List.mem_filterMap]

/-- Each cited source once. -/
theorem cited_nodup : ∀ (srcs : List Source) (used : List Nat), (cited srcs used).Nodup := by
  intro srcs used
  exact (eraseDups_spec _ _ (Nat.le_refl _)).2

end VE.Ask
