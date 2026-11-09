import VE.RightClauses.PlainWellFormed.Clauses

/-! `correlate (plain D)` is `mapG (γ D) (correlate D.doc)` (`correlate_plain_mapG`), and the new guards meet
`GHyp` (`ghyp`): each extends the old one by the line's clauses and relation atom, typed over the base vocabulary
in the line's context (8.3, `plain_wellFormed`). Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.Rights (RightsDoc SourceLine Line linesOf sourceLines)
open VE.SoftNorms (SoftNode SoftDoc)

/-- What an instance keeps of its source line. -/
def FromSource (N : Line) : Prop :=
  N.kind = N.source.kind ∧ (N.kind ≠ .power → ∃ n0, N.source.norm = some n0 ∧ N.node.guard = n0.guard ∧
    N.node.pred = (if N.source.fanOut = [] then n0.pred else N.node.pred) ∧ (N.source.fanOut = [] → N.node = n0))

theorem instancesOf_from (R : String) (S : SourceLine) (k : Nat) :
    ∀ N ∈ VE.Rights.instancesOf R S k, N.source = S ∧ FromSource N := by
  intro N hN
  obtain ⟨kd, n, l, r, f, hs, cs⟩ := S
  cases kd
  case power =>
    simp only [VE.Rights.instancesOf] at hN
    split at hN
    · simp only [List.mem_cons, List.not_mem_nil, or_false] at hN
      rcases hN with rfl | rfl <;> exact ⟨rfl, rfl, fun h => absurd rfl h⟩
    · simp at hN
  all_goals
    cases n with
    | none => simp [VE.Rights.instancesOf] at hN
    | some n0 =>
      simp only [VE.Rights.instancesOf] at hN
      by_cases hf : f = []
      · subst hf
        simp only [if_true, List.mem_singleton] at hN; subst hN
        exact ⟨rfl, rfl, fun _ => ⟨n0, rfl, rfl, by simp, fun _ => rfl⟩⟩
      · simp only [hf, if_false, List.mem_mapIdx] at hN
        obtain ⟨i, hi, rfl⟩ := hN
        exact ⟨rfl, rfl, fun _ => ⟨n0, rfl, rfl, by simp [hf], fun h => absurd h hf⟩⟩

theorem linesAux_from : ∀ (l : List (String × SourceLine)) (k : Nat) (RN : String × Line),
    RN ∈ VE.Rights.linesAux l k → (RN.1, RN.2.source) ∈ l ∧ FromSource RN.2
  | [], _, _, h => by cases h
  | (R, S) :: rest, k, RN, h => by
    simp only [VE.Rights.linesAux, List.mem_append, List.mem_map] at h
    rcases h with ⟨N, hN, rfl⟩ | h
    · obtain ⟨hs, hf⟩ := instancesOf_from R S k N hN
      exact ⟨by simp [hs], hf⟩
    · obtain ⟨h1, h2⟩ := linesAux_from rest _ RN h
      exact ⟨List.mem_cons_of_mem _ h1, h2⟩

theorem mem_linesOf {X : RightsDoc} {RN : String × Line} (h : RN ∈ linesOf X) :
    (RN.1, RN.2.source) ∈ sourceLines X ∧ FromSource RN.2 := linesAux_from _ 0 RN h

/-! ### `correlate (plain D)` as `mapG` -/

/-- The new guard of the node named `n` (its old guard `G` when no line instance has that name). -/
def γP (D : ClauseDoc) (n : String) (G : VE.Formula) : VE.Formula :=
  match (linesOf D.doc).find? (fun RN => RN.2.node.name == n) with
  | some RN => newGuard D RN
  | none => G

theorem find?_key {α : Type} (k : α → String) :
    ∀ {l : List α}, (l.map k).Nodup → ∀ {a : α}, a ∈ l → l.find? (fun b => k b == k a) = some a
  | [], _, _, ha => by cases ha
  | b :: l, hnd, a, ha => by
    simp only [List.map_cons, List.nodup_cons, List.mem_map] at hnd
    rcases List.mem_cons.1 ha with rfl | ha
    · simp
    · have hne : (k b == k a) = false := by
        simp only [beq_eq_false_iff_ne]; intro he; exact hnd.1 ⟨a, ha, he.symm⟩
      simp [List.find?_cons, hne, find?_key k hnd.2 ha]

theorem setG_self (γ : String → VE.Formula → VE.Formula) (N : SoftNode) (h : γ N.name N.guard = N.guard) :
    setG γ N = N := by
  obtain ⟨⟨⟩⟩ := N; simp only [setG] at h ⊢; rw [h]

theorem plainNodes_mapG (D : ClauseDoc) (hnd : ((VE.Rights.correlate D.doc).T.nodes.map (·.name)).Nodup) :
    plainNodes D = (VE.Rights.correlate D.doc).T.nodes.map (setG (γP D)) := by
  have hC : (VE.Rights.correlate D.doc).T.nodes =
      (linesOf D.doc).map (fun RN => VE.Rights.nodeOf D.doc RN.2) ++ D.doc.soft.T.nodes ++ VE.Rights.barNodes D.doc :=
    rfl
  rw [hC] at hnd ⊢
  simp only [List.map_append, List.nodup_append, List.map_map, Function.comp_def] at hnd
  have hlines : ((linesOf D.doc).map (fun RN => RN.2.node.name)).Nodup := by
    have := hnd.1.1; simpa [VE.Rights.nodeOf] using this
  have hout : ∀ N : SoftNode, (∀ RN ∈ linesOf D.doc, RN.2.node.name ≠ N.name) → setG (γP D) N = N := by
    intro N hN
    apply setG_self
    simp only [γP]
    rw [List.find?_eq_none.2 (fun RN hRN => by simpa using hN RN hRN)]
  have h1 : (linesOf D.doc).map (fun RN => { VE.Rights.nodeOf D.doc RN.2 with guard := newGuard D RN }) =
      (linesOf D.doc).map (fun RN => setG (γP D) (VE.Rights.nodeOf D.doc RN.2)) := by
    apply List.map_congr_left
    intro RN hRN
    simp only [setG, γP, VE.Rights.nodeOf]
    rw [find?_key (fun RN : String × Line => RN.2.node.name) hlines hRN]
  have h2 : D.doc.soft.T.nodes = D.doc.soft.T.nodes.map (setG (γP D)) := by
    have : D.doc.soft.T.nodes.map (setG (γP D)) = D.doc.soft.T.nodes.map id := by
      apply List.map_congr_left
      intro N hN
      refine hout N (fun RN hRN he => hnd.1.2.2 _ (List.mem_map_of_mem hRN) N.name (List.mem_map_of_mem hN) ?_)
      simpa [VE.Rights.nodeOf] using he
    rw [List.map_id] at this; exact this.symm
  have h3 : VE.Rights.barNodes D.doc = (VE.Rights.barNodes D.doc).map (setG (γP D)) := by
    have : (VE.Rights.barNodes D.doc).map (setG (γP D)) = (VE.Rights.barNodes D.doc).map id := by
      apply List.map_congr_left
      intro N hN
      refine hout N (fun RN hRN he => hnd.2.2 _ (List.mem_append_left _ (List.mem_map_of_mem hRN)) N.name
        (List.mem_map_of_mem hN) ?_)
      simpa [VE.Rights.nodeOf] using he
    rw [List.map_id] at this; exact this.symm
  unfold plainNodes
  rw [h1, List.map_append, List.map_append, List.map_map, ← h2, ← h3]
  rfl

end VE.RightClauses.PWF
