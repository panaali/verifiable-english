import VE.Compose.Stack
import VE.Service.Document
import VE.Service.ScopeAdmission

/-! The composition contract (profile-composition 1.4 and 1.5, PC-3): rewriters and their structural laws (G2), the
document mode's pipeline in the stack order of AR-10's rows, and the typed route evidence of the listed stacks. -/

namespace VE.Compose.Contract
open Lean

/-! ## Structural laws: well-formedness and name freshness (G2, 1.4)

G2 is not a soundness theorem. A rewriter that replaces every claim with its negation can satisfy all three laws, so
nothing is admitted on G2 alone (1.5). -/

structure Rewriter (σ : Type) where
  profile : String
  run     : σ → Except String σ
  on      : σ → Bool
  writes  : List String          -- the prefixes of the names it may introduce

structure Rewriter.Laws {σ : Type} (WF : σ → Prop) (names : σ → List String) (r : Rewriter σ) : Prop where
  preserves : ∀ D D', WF D → r.run D = .ok D' → WF D'
  off       : ∀ D, r.on D = false → r.run D = .ok D
  fresh     : ∀ D D', r.run D = .ok D' → ∀ n ∈ names D', n ∈ names D ∨ ∃ p ∈ r.writes, n.startsWith p = true

def pipeline {σ : Type} : List (Rewriter σ) → σ → Except String σ
  | [], D => .ok D
  | r :: rs, D => r.run D >>= pipeline rs

/-- The pipeline of a list in the stack order AR-10's rows give; a profile with no rewriter of this document type
is skipped. -/
def pipelineOf {σ : Type} (t : List ProfileRow) (ps : List String) (rw : String → Option (Rewriter σ)) :
    List (Rewriter σ) :=
  (stackOf t ps).filterMap rw

theorem pipeline_preserves {σ : Type} (WF : σ → Prop) (names : σ → List String) (rs : List (Rewriter σ))
    (hl : ∀ r ∈ rs, r.Laws WF names) (D D' : σ) (hD : WF D) (h : pipeline rs D = .ok D') : WF D' := by
  induction rs generalizing D with
  | nil => cases h; exact hD
  | cons r rs ih =>
    simp only [pipeline, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i D₁ h₁
      exact ih (fun r' hr => hl r' (.tail _ hr)) D₁ ((hl r (.head _)).preserves D D₁ hD h₁) h

theorem pipeline_off {σ : Type} (WF : σ → Prop) (names : σ → List String) (rs : List (Rewriter σ))
    (hl : ∀ r ∈ rs, r.Laws WF names) (D : σ) (hoff : ∀ r ∈ rs, r.on D = false) : pipeline rs D = .ok D := by
  induction rs with
  | nil => rfl
  | cons r rs ih =>
    simp only [pipeline, (hl r (.head _)).off D (hoff r (.head _)), bind, Except.bind]
    exact ih (fun r' hr => hl r' (.tail _ hr)) (fun r' hr => hoff r' (.tail _ hr))

theorem pipeline_names {σ : Type} (WF : σ → Prop) (names : σ → List String) (rs : List (Rewriter σ))
    (hl : ∀ r ∈ rs, r.Laws WF names) (D D' : σ) (h : pipeline rs D = .ok D') :
    ∀ n ∈ names D', n ∈ names D ∨ ∃ r ∈ rs, ∃ p ∈ r.writes, n.startsWith p = true := by
  induction rs generalizing D with
  | nil => cases h; exact fun n hn => .inl hn
  | cons r rs ih =>
    simp only [pipeline, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i D₁ h₁
      intro n hn
      rcases ih (fun r' hr => hl r' (.tail _ hr)) D₁ h n hn with h₂ | ⟨r', hr', p, hp, hs⟩
      · rcases (hl r (.head _)).fresh D D₁ h₁ n h₂ with h₃ | ⟨p, hp, hs⟩
        · exact .inl h₃
        · exact .inr ⟨r, .head _, p, hp, hs⟩
      · exact .inr ⟨r', .tail _ hr', p, hp, hs⟩

/-! ## Typed route evidence (1.5)

The document mode works on cases (`Lean.Json`), and GOVERN rewrites a case before the chain reads it
(`checkDocSets`), so the document mode's rewriters have one type, `Rewriter Json`. -/

/-- GOVERN as a rewriter of document-mode cases: `checkDocSets`' scope branch before the chain. -/
def scopeRewriter : Rewriter Json where
  profile := "scope@0"
  run := fun j =>
    if "scope@0" ∈ VE.Service.Document.profilesOf j then do
      let D ← VE.Scope.decodeScope j
      let out ← VE.Scope.governSetsWith VE.Scope.governFast D
      pure (if (VE.Scope.governedSetUnits D).isEmpty then VE.Service.Document.withUnits j out
        else VE.Service.Document.withSets j out)
    else .ok j
  on := fun j => decide ("scope@0" ∈ VE.Service.Document.profilesOf j)
  writes := []

/-- The document mode's case rewriters, by profile. -/
def docRewriters (p : String) : Option (Rewriter Json) :=
  if p == "scope@0" then some scopeRewriter else none

/-- A document-mode entry `run` runs its list's pipeline, then the chain, then scope's fold, whenever it answers. -/
def ScopeRunsOf (run : Json → Except String Json) : Prop :=
  ∀ j ans, run j = .ok ans → "scope@0" ∈ VE.Service.Document.profilesOf j →
    ∃ D j' a, VE.Scope.decodeScope j = .ok D ∧
      pipeline (pipelineOf profileTable (VE.Service.Document.profilesOf j) docRewriters) j = .ok j' ∧
      VE.Service.Document.checkCore j' = .ok a ∧ ans = VE.Scope.foldGovernors D a

/-- The document mode's run statement (scope's instance). -/
def ScopeRuns : Prop := ScopeRunsOf VE.Service.Document.checkDocSets

/-- The document rewriters of a list: one copy of GOVERN's for each time the list names it. -/
theorem filterMap_docRewriters (l : List String) :
    l.filterMap docRewriters = List.replicate (l.count "scope@0") scopeRewriter := by
  induction l with
  | nil => rfl
  | cons p l ih =>
    by_cases hp : p = "scope@0"
    · subst hp; simp [docRewriters, ih, List.replicate_succ]
    · simp [docRewriters, hp, ih]

/-- A list that lists `scope@0` has GOVERN as its one document rewriter. -/
theorem pipelineOf_scope (ps : List String) (hs : "scope@0" ∈ ps) :
    pipelineOf profileTable ps docRewriters = [scopeRewriter] := by
  have hr : rewriters profileTable =
      [(11, "acts@0"), (10, "ve.discourse@1"), (20, "right-clauses@0"), (30, "readings@1"), (12, "scope@0")] := by
    decide
  have hc : ps.contains "scope@0" = true := List.elem_iff.mpr hs
  unfold pipelineOf stackOf
  rw [filterMap_docRewriters, ((List.mergeSort_perm _ _).map Prod.snd).count_eq, hr]
  simp only [List.filter, hc]
  split <;> split <;> split <;> split <;> rfl

/-- The theorem tying the document mode's run to the pipeline (scope's instance); from `scope_admission_sets`
(ScopeAdmission.lean:158) and `governSetsFast_eq`. -/
theorem checkDocSets_pipeline : ScopeRuns := by
  intro j ans h hs
  obtain ⟨D, out, a, hD, ho, ha, rfl⟩ := VE.Scope.scope_admission_sets j ans h hs
  refine ⟨D, VE.Scope.Pinned.withGoverned j out, a, hD, ?_, ha, rfl⟩
  rw [pipelineOf_scope _ hs]
  simp only [pipeline, scopeRewriter, if_pos hs, hD, VE.Scope.governSetsFast_eq, ho, bind, Except.bind, pure,
    Except.pure, VE.Scope.Pinned.withGoverned]

/-- A run statement alone says nothing about meaning: an entry that refuses every case satisfies it (F3.7). -/
theorem refuseAll_runs : ScopeRunsOf (fun _ => .error "refused") := by
  intro j ans h
  cases h

/-- GOVERN's own faithfulness (scope 1.4, SC-1, SC-5): the run path is the statement, per choice included
(`governFast_eq`, Scope/Theorems.lean:545; `governSetsFast_eq`, ReadingsTheorems.lean:16), and a unit is governed
by exactly the governors whose reach covers it (`governorsOf_iff`, Theorems.lean:328). -/
def ScopeFaithful : Prop :=
  (∀ D, VE.Scope.governFast D = VE.Scope.govern D) ∧
  (∀ D, VE.Scope.governSetsWith VE.Scope.governFast D = VE.Scope.governSets D) ∧
  ∀ D u g, g ∈ VE.Scope.governorsOf D u ↔
    g ∈ D.governors ∧ VE.Scope.unary g.effect = true ∧ ∃ us, VE.Scope.covered D g.reach = .ok us ∧ u ∈ us

/-- GOVERN's semantic preservation: an admitted block with no governor and no part hands the chain the document
unchanged (`govern_identity`, Theorems.lean:308). -/
def ScopePreserves : Prop :=
  ∀ D, VE.Scope.admitBlock D = .ok () → D.governors = [] → VE.Scope.partUnits D = [] →
    VE.Scope.govern D = .ok D.doc

/-- Per choice (`readings@1` beside scope, SC-5rc): the choices governed are the joint choices over the governed
sets, and a fault under one choice refuses the document (`scope_set_choices`, `governSets_choice_refused`,
ReadingsTheorems.lean:20, :43). -/
def ScopeSetsFaithful : Prop :=
  (∀ D cs, VE.Scope.setChoices D = .ok cs → ∀ K n cs',
    VE.Discourse.compatibleChoices K (VE.Scope.setShapes D) n = .ok cs' →
      (∀ c ∈ cs', c ∈ cs) ∧ (K.constraints = [] → cs' = cs)) ∧
  ∀ D, VE.Scope.governedSetUnits D ≠ [] → ∀ cs, VE.Scope.setChoices D = .ok cs → ∀ ch ∈ cs, ∀ e,
    VE.Scope.governChoice D ch = .error e → (VE.Scope.governSets D).isOk = false

theorem scopeFaithful : ScopeFaithful :=
  ⟨VE.Scope.governFast_eq, VE.Scope.governSetsFast_eq, VE.Scope.governorsOf_iff⟩

theorem scopePreserves : ScopePreserves := VE.Scope.govern_identity

theorem scopeSetsFaithful : ScopeSetsFaithful :=
  ⟨VE.Scope.scope_set_choices, VE.Scope.governSets_choice_refused⟩

/-- What a listed stack's admission rests on: its run statement, and each rewriter's faithfulness and preservation.
`readings@1` has no case rewriter in the document mode (7, choice 2); its stack adds GOVERN's per-choice facts.
The acts, discourse and generic entries are PC-6b's, PC-7b's and PC-4b's; until they land, no other stack has
route facts. -/
def RouteFacts : List String → Prop
  | ["scope@0"] => ScopeRuns ∧ ScopeFaithful ∧ ScopePreserves
  | ["scope@0", "readings@1"] => ScopeRuns ∧ ScopeFaithful ∧ ScopePreserves ∧ ScopeSetsFaithful
  | _ => False

/-- M1 (evidence). Every listed stack has its route facts. -/
theorem listed_evidence : ∀ s ∈ listedStacks, RouteFacts s := by
  intro s hs
  simp only [listedStacks, List.mem_cons, List.not_mem_nil, or_false] at hs
  rcases hs with rfl | rfl
  · exact ⟨checkDocSets_pipeline, scopeFaithful, scopePreserves⟩
  · exact ⟨checkDocSets_pipeline, scopeFaithful, scopePreserves, scopeSetsFaithful⟩

end VE.Compose.Contract
