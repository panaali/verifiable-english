import VE.RightClauses.Plain

/-! Totality premises and the slot of the head (docs/spec/right-clauses.md 1.3, 4.2-4.4, 8.4).

A total relation adds one closed premise `ρ_n` (`totalF`) to the base-premise slot, labelled
`rights:relation:<n>:total`; the slot is `Lim_{plain D} ++ Rel_D` (`clauseSlot`). Where a clause or the relation
fails at a tuple the line does not select there (`clause_fails_not_selected`); under `ρ_n` every holder satisfying
the holder guard has a related bearer that owes the act wherever nothing narrows the line (`relation_some_bearer`). -/
namespace VE.RightClauses
open VE.Norms (Sat tupleVal)
open VE.Rights (RightsDoc Line linesOf holderSlot sortsOf dutyKind ownGuard narrowings NarrowsAt owes SelectsRN
  WellFormedRights correlate limPremises limPremisesLabelled)
open VE.SoftNorms (soften)
universe u

/-- ρ_n (1.3), for total slot `j`; `o` is the other slot. Inside: variable 0 is y (slot o), variable 1 is x (slot j). -/
def totalF (D : ClauseDoc) (R : String) (L : CLine) (rel : Relation) (j : Nat) : VE.Formula :=
  let ss := lineSorts D.doc.soft L.line
  let o := if rel.slots.1 = j then rel.slots.2 else rel.slots.1
  let t := fun k => if k = j then VE.Term.var 1 else VE.Term.var 0
  .all (ss.getD j "") (.implies (holderGuardOf D R) (.ex (ss.getD o "") (.binary rel.pred (t rel.slots.1) (t rel.slots.2))))
def relPremisesLabelled (D : ClauseDoc) : VE.Compose.Labelled :=
  D.lines.filterMap (fun x => x.2.2.relation.bind (fun rel => rel.total.map (fun j =>
    ("rights:relation:" ++ x.2.1 ++ ":total", totalF D x.1 x.2.2 rel j))))
def relPremises (D : ClauseDoc) : List VE.Formula := VE.Compose.Labelled.formulas (relPremisesLabelled D)
def clauseSlotLabelled (D : ClauseDoc) : VE.Compose.Labelled := limPremisesLabelled (plain D) ++ relPremisesLabelled D
def clauseSlot (D : ClauseDoc) : List VE.Formula := VE.Compose.Labelled.formulas (clauseSlotLabelled D)

theorem clauseSlot_eq (D : ClauseDoc) : clauseSlot D = limPremises (plain D) ++ relPremises D := by
  simp [clauseSlot, clauseSlotLabelled, relPremises, VE.Compose.Labelled.formulas, limPremises]

/-- No total relation: the slot is Lim_D and the route is the rights route on plain D (rights_is_slot). -/
theorem clauseSlot_no_total (D : ClauseDoc) (h : ∀ x ∈ D.lines, ∀ rel, x.2.2.relation = some rel → rel.total = none) :
  clauseSlot D = limPremises (plain D) := by
  have : relPremisesLabelled D = [] := by
    refine List.filterMap_eq_nil_iff.2 fun x hx => ?_
    cases hr : x.2.2.relation with
    | none => rfl
    | some rel => simp [h x hx rel hr]
  simp [clauseSlot_eq, relPremises, this, VE.Compose.Labelled.formulas]

/-! ## The line's own instance -/

theorem eq_of_nodup_map {α β : Type} (f : α → β) :
    ∀ {l : List α}, (l.map f).Nodup → ∀ {a b}, a ∈ l → b ∈ l → f a = f b → a = b
  | [], _, _, _, ha, _, _ => absurd ha List.not_mem_nil
  | x :: l, hn, a, b, ha, hb, he => by
    rw [List.map_cons, List.nodup_cons] at hn
    rcases List.mem_cons.1 ha with ha | ha <;> rcases List.mem_cons.1 hb with hb | hb
    · exact ha.trans hb.symm
    · exact absurd (show f x ∈ l.map f by rw [← ha, he]; exact List.mem_map_of_mem hb) hn.1
    · exact absurd (show f x ∈ l.map f by rw [← hb, ← he]; exact List.mem_map_of_mem ha) hn.1
    · exact eq_of_nodup_map f hn.2 ha hb he

/-- A source line with a norm, no fan-out and not a power has the one instance on its norm. -/
theorem own_instance_mem (R : String) (S : VE.Rights.SourceLine) (nm : VE.SoftNorms.SoftNode) (hk : S.kind ≠ .power)
    (hf : S.fanOut = []) (hn : S.norm = some nm) :
    ∀ (l : List (String × VE.Rights.SourceLine)) (k : Nat), (R, S) ∈ l →
      (R, (⟨R, S, S.kind, VE.Rights.ikindOf S.kind, nm, none⟩ : Line)) ∈ VE.Rights.linesAux l k
  | [], _, h => absurd h List.not_mem_nil
  | (R', S') :: l, k, h => by
    simp only [VE.Rights.linesAux, List.mem_append, List.mem_map]
    rcases List.mem_cons.1 h with he | h
    · obtain ⟨rfl, rfl⟩ := Prod.mk.inj he
      refine Or.inl ⟨_, ?_, rfl⟩
      unfold VE.Rights.instancesOf
      cases hS : S.kind <;> simp_all
    · exact Or.inr (own_instance_mem R S nm hk hf hn l _ h)

/-- The instance of `linesOf (plain D)` named by a structured entry is the entry's line, plained. -/
theorem entry_instance (D : ClauseDoc) (h : WellFormedClauses D = true) (hw : WellFormedRights (plain D) = true)
    (R n : String) (L : CLine) (hL : (R, n, L) ∈ D.lines) (hs : L.clauses ≠ [] ∨ L.relation.isSome)
    (N : Line) (hN : (R, N) ∈ linesOf (plain D)) (hn : N.node.name = n) :
    ∃ G, N.node.guard = plainGuard (lineSorts D.doc.soft L.line).length G L ∧
      sortsOf (plain D) N = lineSorts D.doc.soft L.line := by
  obtain ⟨hsh, hmem, hname, -, hplain⟩ := entry_facts D h R n L hL
  have hsh' : L.line.kind ≠ .power ∧ L.line.fanOut = [] ∧ L.line.norm.isSome := by
    simp [shapeOk, List.isEmpty_iff] at hsh
    rcases hsh with ⟨hc, hr⟩ | ⟨⟨hk, hf⟩, hn⟩
    · rcases hs with hs | hs
      · exact absurd hc hs
      · simp [hr] at hs
    · exact ⟨hk, hf, hn⟩
  obtain ⟨hk, hf, hnm⟩ := hsh'
  obtain ⟨nm, hnm⟩ := Option.isSome_iff_exists.1 hnm
  have hmem' : (R, plainSource D.doc.soft D.lines R L.line) ∈ VE.Rights.sourceLines (plain D) := by
    rw [sourceLines_plain]; exact List.mem_map.2 ⟨_, hmem, rfl⟩
  have h0 := own_instance_mem R _ { nm with guard := plainGuard (lineSorts D.doc.soft L.line).length nm.guard L }
    (by simpa [hplain] using hk) (by simp [hplain, hf]) (by simp [hplain, hnm]) _ 0 hmem'
  have hnd := VE.Rights.direct_names_nodup (VE.Rights.rightsValid_of_wellFormed _ hw)
  simp only [VE.Rights.directNodes, VE.Rights.lineNodes, List.map_append, List.map_map] at hnd
  have hname0 : nm.name = n := by simpa [lineName, hnm] using hname
  obtain ⟨-, rfl⟩ := Prod.mk.inj (eq_of_nodup_map _ (List.nodup_append.1 hnd).1 hN h0
    (by simp [VE.Rights.nodeOf, hn, hname0]))
  exact ⟨nm.guard, rfl, by simp [sortsOf, lineSorts, hnm, plain]⟩

/-- A line that selects has its own guard. -/
theorem selects_own (X : RightsDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (N : Line) (h : SelectsRN X S ρ N) :
    (ownGuard X N).denote S ρ := by
  obtain ⟨ha, -⟩ := h
  have hl : VE.SoftNorms.LiveD (correlate X) S ρ (VE.Rights.nodeOf X N) := by
    unfold VE.SoftNorms.AppliesSoftD at ha
    split at ha
    · exact ha
    · cases hf : VE.SoftNorms.rankFuel (correlate X) <;> rw [hf] at ha
      · exact ha.2.1
      · exact ha.1.2.1
  exact hl.1

theorem holderConj_left (X : RightsDoc) (N : Line) (G : VE.Formula) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (h : (VE.Rights.holderConj X N G).denote S ρ) : G.denote S ρ := by
  unfold VE.Rights.holderConj at h
  split at h
  · split at h
    · exact h
    · exact h.1
  · exact h

/-- 4.3: where a clause or the relation fails at a tuple, the line does not select there. -/
theorem clause_fails_not_selected (D : ClauseDoc) (h : WellFormedClauses D = true) (hw : WellFormedRights (plain D) = true)
    (R n : String) (L : CLine) (hL : (R, n, L) ∈ D.lines) (N : Line) (hN : (R, N) ∈ linesOf (plain D))
    (hn : N.node.name = n) (S : VE.Structure.{u}) (vs : List S.Carrier) (typed : VE.TupleTyped S (sortsOf (plain D) N) vs)
    (hf : (∃ c ∈ L.clauses, ¬ c.formula.denote S (tupleVal vs)) ∨
          (∃ rel, L.relation = some rel ∧ ¬ (relAtom (sortsOf (plain D) N).length rel).denote S (tupleVal vs))) :
  ¬ SelectsRN (plain D) S (tupleVal vs) N := by
  intro hsel
  have hs : L.clauses ≠ [] ∨ L.relation.isSome := by
    rcases hf with ⟨c, hc, -⟩ | ⟨rel, hr, -⟩
    · exact Or.inl (List.ne_nil_of_mem hc)
    · exact Or.inr (by simp [hr])
  obtain ⟨G, hG, hss⟩ := entry_instance D h hw R n L hL hs N hN hn
  have hg := holderConj_left _ _ _ S _ (selects_own _ S _ N hsel)
  rw [hG, plainGuard, foldl_and_denote] at hg
  rcases hf with ⟨c, hc, hnc⟩ | ⟨rel, hr, hnr⟩
  · exact hnc (hg.2 _ (List.mem_append_left _ (List.mem_map_of_mem hc)))
  · exact hnr (by rw [hss]; exact hg.2 _ (List.mem_append_right _ (by simp [hr])))

/-- 4.4: "some bearer owes it". Under ρ_n every holder satisfying the holder guard has a related bearer, and that
    bearer owes the act wherever the line's own guard holds and no narrowing mechanism is active. -/
theorem relation_some_bearer (D : ClauseDoc) (h : WellFormedClauses D = true) (hw : WellFormedRights (plain D) = true)
    (R n : String) (L : CLine) (hL : (R, n, L) ∈ D.lines) (N : Line) (hN : (R, N) ∈ linesOf (plain D))
    (hn : N.node.name = n) (hk : dutyKind N = true) (rel : Relation) (hr : L.relation = some rel)
    (ht : rel.total = some (holderSlot (plain D) N)) (hs : rel.slots = (0, holderSlot (plain D) N))
    (S : VE.Structure.{u}) (hS : Sat S (relPremises D))
    (sh : String) (hsh : (sortsOf (plain D) N)[holderSlot (plain D) N]? = some sh)
    (hv : S.Carrier) (hd : S.domain sh hv) (hH : (holderGuardOf D R).denote S [hv]) :
  ∃ bv, (∃ sb, (sortsOf (plain D) N).head? = some sb ∧ S.domain sb bv) ∧ S.relation rel.pred [bv, hv] ∧
    ∀ vs, VE.TupleTyped S (sortsOf (plain D) N) vs → vs.head? = some bv →
      vs[holderSlot (plain D) N]? = some hv →
      (ownGuard (plain D) N).denote S (tupleVal vs) →
      (¬ ∃ m ∈ narrowings (plain D) N, NarrowsAt (plain D) S (tupleVal vs) N m) →
      owes (plain D) S N vs := by
  obtain ⟨-, -, hss⟩ := entry_instance D h hw R n L hL (Or.inr (by simp [hr])) N hN hn
  have hmem : totalF D R L rel (holderSlot (plain D) N) ∈ relPremises D := by
    simp only [relPremises, VE.Compose.Labelled.formulas, relPremisesLabelled, List.mem_map, List.mem_filterMap]
    exact ⟨("rights:relation:" ++ n ++ ":total", totalF D R L rel _), ⟨(R, n, L), hL, by simp [hr, ht]⟩, rfl⟩
  have hρ := hS _ hmem
  rw [hss] at hsh
  have hj : (lineSorts D.doc.soft L.line).getD (holderSlot (plain D) N) "" = sh := by simp [List.getD, hsh]
  obtain ⟨s0, ss', hcons⟩ : ∃ s0 ss', lineSorts D.doc.soft L.line = s0 :: ss' := by
    cases hl : lineSorts D.doc.soft L.line with
    | nil => simp [hl] at hsh
    | cons a l => exact ⟨a, l, rfl⟩
  have hbear : ∃ bv, S.domain s0 bv ∧ S.relation rel.pred [bv, hv] := by
    simp only [totalF, hs, VE.Formula.denote, hj] at hρ
    obtain ⟨w, hwd, v1, v2, h1, h2, hrel⟩ := hρ hv hd hH
    by_cases h0 : (0 : Nat) = holderSlot (plain D) N
    · simp only [h0, if_true, VE.Term.denote] at h1 h2 hwd
      simp at h1 h2; subst h1; subst h2
      refine ⟨hv, ?_, hrel⟩
      rw [← h0] at hsh; rw [hcons] at hsh; simp at hsh; exact hsh ▸ hd
    · simp only [h0, if_false, if_true, VE.Term.denote] at h1 h2 hwd
      simp at h1 h2; subst h1; subst h2
      exact ⟨w, by simpa [List.getD, hcons] using hwd, hrel⟩
  obtain ⟨bv, hbd, hbr⟩ := hbear
  refine ⟨bv, ⟨s0, by rw [hss, hcons]; rfl, hbd⟩, hbr, fun vs _ _ _ hown hnn => ⟨hk, ?_⟩⟩
  exact Classical.byContradiction fun hns =>
    hnn (VE.Rights.narrowings_complete (plain D) hw N (List.mem_map.2 ⟨_, hN, rfl⟩) S _ hown hns)
end VE.RightClauses
