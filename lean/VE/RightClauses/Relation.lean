import VE.RightClauses.Plain
import VE.RightClauses.PlainWellFormed.Hyp

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

/-! ## Labels -/

theorem relLabel_inj {a b : String} (h : "rights:relation:" ++ a ++ ":total" = "rights:relation:" ++ b ++ ":total") :
    a = b := by
  have := congrArg String.data h
  simp only [String.data_append, List.append_assoc] at this
  exact String.ext (List.append_cancel_right (List.append_cancel_left this))

theorem limLabel_at7 (X : RightsDoc) : ∀ x ∈ limPremisesLabelled X, (x.1.data.drop 7).head? = some 'l' := by
  intro x hx
  obtain ⟨k, -, hk⟩ := List.mem_filterMap.1 hx
  unfold VE.Rights.keyPremise at hk
  split at hk
  · cases hk
  · split at hk
    · cases hk
    · cases hk; simp only [String.data_append, toString]; rfl

theorem relLabel_at7 (D : ClauseDoc) : ∀ x ∈ relPremisesLabelled D, (x.1.data.drop 7).head? = some 'r' := by
  intro x hx
  obtain ⟨y, -, hy⟩ := List.mem_filterMap.1 hx
  simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff] at hy
  obtain ⟨_, -, _, -, rfl⟩ := hy
  simp only [String.data_append]; rfl

/-- Entries that are each the only one of their name have distinct names. -/
theorem map_nodup_of_filter {α : Type} (k : α → String) :
    ∀ l : List α, (∀ x ∈ l, l.filter (fun y => k y == k x) = [x]) → (l.map k).Nodup
  | [], _ => List.nodup_nil
  | y :: l, h => by
    have hy := h y List.mem_cons_self
    simp only [List.filter_cons, beq_self_eq_true, if_true, List.cons.injEq, true_and] at hy
    rw [List.map_cons, List.nodup_cons]
    refine ⟨fun hm => ?_, map_nodup_of_filter k l fun x hx => ?_⟩
    · obtain ⟨z, hz, hzk⟩ := List.mem_map.1 hm
      have : z ∈ l.filter (fun w => k w == k y) := List.mem_filter.2 ⟨hz, by simp [hzk]⟩
      rw [hy] at this; cases this
    · have hx' := h x (List.mem_cons_of_mem _ hx)
      by_cases he : k y = k x
      · have : x ∈ l.filter (fun w => k w == k y) := List.mem_filter.2 ⟨hx, by simp [he]⟩
        rw [hy] at this; cases this
      · simpa [List.filter_cons, he] using hx'

theorem filterMap_labels_nodup {α β : Type} (k : α → String) (f : α → Option (String × β)) (g : String → String)
    (hg : ∀ a b, g a = g b → a = b) (hf : ∀ a p, f a = some p → p.1 = g (k a)) :
    ∀ l : List α, (l.map k).Nodup → ((l.filterMap f).map (·.1)).Nodup
  | [], _ => List.nodup_nil
  | a :: l, h => by
    rw [List.map_cons, List.nodup_cons] at h
    rw [List.filterMap_cons]
    cases hfa : f a with
    | none => exact filterMap_labels_nodup k f g hg hf l h.2
    | some p =>
      rw [List.map_cons, List.nodup_cons]
      refine ⟨fun hm => h.1 ?_, filterMap_labels_nodup k f g hg hf l h.2⟩
      obtain ⟨q, hq, hqp⟩ := List.mem_map.1 hm
      obtain ⟨b, hb, hfb⟩ := List.mem_filterMap.1 hq
      rw [hf a p hfa, hf b q hfb] at hqp
      exact List.mem_map.2 ⟨b, hb, hg _ _ hqp⟩

/-- The slot's labels are distinct: `Rel_D`'s, one per rule, and none is a `Lim_D` label. `hl` (DRI question Q3:
    `Lim_D`'s own labels may repeat on a well-formed rights document) is that `Lim_D`'s are. -/
theorem clauseSlot_labelled (D : ClauseDoc) (h : WellFormedClauses D = true) (hw : WellFormedRights (plain D) = true)
    (hl : VE.Compose.Labelled.wellLabelled (limPremisesLabelled D.doc) = true) :
  VE.Compose.Labelled.wellLabelled (clauseSlotLabelled D) = true := by
  have hc : checkClauses D = .ok () := by unfold WellFormedClauses at h; split at h <;> simp_all
  have hnames : (D.lines.map (·.2.1)).Nodup := map_nodup_of_filter (·.2.1) D.lines fun x hx => by
    have := (checkEntry_ok (forM_ok _ _ hc _ hx)).1
    simp only [entryOk, Bool.and_eq_true, decide_eq_true_eq] at this
    exact this.1.2
  have hrel : ((relPremisesLabelled D).map (·.1)).Nodup := by
    unfold relPremisesLabelled
    refine filterMap_labels_nodup (·.2.1) _ (fun n => "rights:relation:" ++ n ++ ":total")
      (fun _ _ => relLabel_inj) (fun x p hp => ?_) D.lines hnames
    simp only [Option.bind_eq_some_iff, Option.map_eq_some_iff] at hp
    obtain ⟨_, -, _, -, rfl⟩ := hp; rfl
  simp only [VE.Compose.Labelled.wellLabelled, decide_eq_true_eq, clauseSlotLabelled, List.map_append,
    plain_limPremises] at hl ⊢
  refine List.nodup_append.2 ⟨hl, hrel, fun a ha b hb hab => ?_⟩
  obtain ⟨x, hx, rfl⟩ := List.mem_map.1 ha
  obtain ⟨y, hy, rfl⟩ := List.mem_map.1 hb
  have h1 := limLabel_at7 _ x hx
  rw [hab, relLabel_at7 D y hy] at h1
  cases h1

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
/-! ## The slot is well formed (4.2's `hP`)

`Lim_D`'s premises are typed at layer 0 by rights (`limTyped`). A totality premise is typed over the base vocabulary
in the line's context: `relationOk` types the relation and `H_R` there, and rights' `checkShape` puts the right's
holder sort on the holder slot (`SlotWF.holder_sort`). The base vocabulary is inside layer 0 of the correlated
tree (`SlotWF.baseEnv_layer0`): its regulated and defined names are the base tree's layer names, since the base
stratum graph is a subgraph of the correlated one (`PWF.layer_names`), and no generated name is an author's
(`PWF.genDecls_fresh`, the soft check's fresh decisions). -/

namespace SlotWF
open VE.RightClauses.PWF (bind_eq_ok)

theorem except_bind_ok_iff {α β : Type} {x : Except String α} {f : α → Except String β} {b : β} :
    (x >>= f) = .ok b ↔ ∃ a, x = .ok a ∧ f a = .ok b := by
  cases x <;> simp [bind, Except.bind]

theorem restRights_ok (X : RightsDoc) (h : VE.Rights.checkRights X = .ok ()) : PWF.restRights X = .ok () := by
  rw [PWF.checkRights_eq] at h
  generalize PWF.restRights X = k at h ⊢
  unfold PWF.checkRightsK at h
  simp only [] at h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  split at h
  · simp [bind, Except.bind] at h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  split at h
  · simp [bind, Except.bind] at h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  split at h
  · split at h
    · simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h
    · split at h
      · simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h
      · split at h <;> simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h
  · obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
    obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
    obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
    exact h

theorem shape_ok (X : RightsDoc) (h : VE.Rights.checkRights X = .ok ()) (RN : String × Line) (hRN : RN ∈ linesOf X)
    (Rt : VE.Rights.Right) (hR : VE.Rights.rightOf X RN.1 = some Rt) : VE.Rights.checkShape X Rt RN.2 = .ok () := by
  have hk := restRights_ok X h
  unfold PWF.restRights at hk
  obtain ⟨_, -, hk⟩ := bind_eq_ok.1 hk
  obtain ⟨_, -, hk⟩ := bind_eq_ok.1 hk
  obtain ⟨u, h3, -⟩ := bind_eq_ok.1 hk
  cases u
  have := (VE.NormDefaults.forIn_unit_ok _ (fun x r hx => by
    revert hx
    cases hx' : VE.Rights.rightOf X x.1 with
    | none => simp [throw, throwThe, MonadExceptOf.throw, Except.bind, bind]
    | some R =>
      simp only []
      intro hx
      obtain ⟨_, -, hx⟩ := except_bind_ok_iff.1 hx
      split at hx
      · simp [throw, throwThe, MonadExceptOf.throw, Except.bind, bind] at hx
      · simp [Except.bind, bind, pure, Except.pure] at hx; exact hx.symm) (linesOf X)).1 h3 RN hRN
  simp only [hR] at this
  obtain ⟨u, hs, -⟩ := except_bind_ok_iff.1 this
  cases u; exact hs

theorem getElem?_idxOf : ∀ (l : List String) (a : String), a ∈ l → l[l.idxOf a]? = some a
  | [], _, h => absurd h List.not_mem_nil
  | b :: t, a, h => by
    by_cases hb : b = a
    · subst hb; simp [List.idxOf_cons]
    · have ht : a ∈ t := by rcases List.mem_cons.1 h with h | h; exact absurd h.symm hb; exact h
      rw [List.idxOf_cons, show (b == a) = false from beq_false_of_ne hb, cond_false, List.getElem?_cons_succ]
      exact getElem?_idxOf t a ht

theorem idx_holder (ss : List String) (h : String) (x : Nat) (hx : x ∈ VE.Rights.holderObjectSlots ss h) :
    ss[(ss.drop 1).idxOf h + 1]? = some h := by
  simp only [VE.Rights.holderObjectSlots, List.mem_filter, beq_iff_eq] at hx
  obtain ⟨hr, hxs⟩ := hx
  rw [List.range_eq_range', List.drop_range'] at hr
  simp only [List.mem_range'_1] at hr
  have hmem : h ∈ ss.drop 1 := by
    have : (ss.drop 1)[x - 1]? = some h := by rw [List.getElem?_drop]; rw [show 1 + (x - 1) = x by omega]; exact hxs
    exact List.mem_of_getElem? this
  have := getElem?_idxOf _ _ hmem
  rw [List.getElem?_drop, Nat.add_comm] at this
  exact this

/-- A checked claim, liberty or immunity instance with a non-empty context: its holder slot holds its right's holder. -/
theorem holder_sort (X : RightsDoc) (Rt : VE.Rights.Right) (N : Line) (hs : VE.Rights.checkShape X Rt N = .ok ())
    (hk : N.ikind = .claim ∨ N.ikind = .liberty ∨ N.ikind = .immunity) (hR : VE.Rights.rightOf X N.right = some Rt)
    (hne : sortsOf X N ≠ []) :
    (sortsOf X N)[holderSlot X N]? = some Rt.holder := by
  unfold VE.Rights.checkShape at hs
  cases hr : VE.Rights.regOfName X N.node.pred with
  | none => simp [hr, throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at hs
  | some r =>
    have hso : sortsOf X N = r.sorts := by
      simp only [VE.Rights.regOfName] at hr
      simp [sortsOf, VE.SoftNorms.sortsOf, VE.SoftNorms.sortsIn, hr]
    rw [hso] at hne ⊢
    simp only [hr] at hs
    have os : ∀ e e' : String, (match N.source.holderSlot with
        | some k => if (decide (k ≥ 1) && r.sorts[k]? == some Rt.holder) = true then pure PUnit.unit else throw e
        | none => match VE.Rights.holderObjectSlots r.sorts Rt.holder with
          | [] => throw e
          | [_] => pure ()
          | _ => throw e' : Except String PUnit) = .ok () →
        r.sorts[(match N.source.holderSlot with
          | some k => k
          | none => (r.sorts.drop 1).idxOf Rt.holder + 1)]? = some Rt.holder := by
      intro e e' h
      cases hsl : N.source.holderSlot with
      | some k =>
        simp only [hsl] at h ⊢
        split at h
        · rename_i hc; simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hc; exact hc.2
        · cases h
      | none =>
        simp only [hsl] at h ⊢
        split at h
        · cases h
        · rename_i x hx; exact idx_holder _ _ x (by rw [hx]; exact List.mem_singleton_self x)
        · cases h
    rcases hk with hk | hk | hk
    · simp only [hk] at hs
      unfold holderSlot; simp only [hk, hR, hso]
      split at hs
      · simp only [pure, Except.pure, bind, Except.bind] at hs
        split at hs
        · exact os _ _ (by simpa [pure, Except.pure, bind, Except.bind] using hs)
        · revert hs; simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind]
      · revert hs; simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind]
    · simp only [hk] at hs
      unfold holderSlot; simp only [hk]
      split at hs
      · rename_i hc
        obtain ⟨a, t, he⟩ := List.exists_cons_of_ne_nil hne
        simp only [he, Bool.and_eq_true, beq_iff_eq, List.head?_cons, Option.getD_some] at hc ⊢
        simp [hc.1.1]
      · revert hs; simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind]
    · simp only [hk] at hs
      unfold holderSlot; simp only [hk, hR, hso]
      split at hs
      · simp only [pure, Except.pure, bind, Except.bind] at hs
        split at hs
        · obtain ⟨u, ho, -⟩ := except_bind_ok_iff.1 hs
          exact os _ _ ho
        · revert hs; simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind]
      · revert hs; simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind]

/-- A checked entry with a relation: its right, and the relation's check against it (4.1 step 3). -/
theorem entry_relation (D : ClauseDoc) (h : WellFormedClauses D = true) (x : String × String × CLine)
    (hx : x ∈ D.lines) (rel : Relation) (hrel : x.2.2.relation = some rel) :
    ∃ Rt, VE.Rights.rightOf D.doc x.1 = some Rt ∧ relationOk (baseEnv D) Rt
      ((VE.Rights.instancesOf x.1 x.2.2.line 0).head?.map (holderSlot D.doc)) (lineSorts D.doc.soft x.2.2.line) rel = true := by
  have hc : checkClauses D = .ok () := by unfold WellFormedClauses at h; split at h <;> simp_all
  have he := forM_ok _ _ hc x hx
  unfold checkEntry at he
  split at he
  · rename_i Rt hRt
    split at he
    · cases he
    split at he
    · cases he
    obtain ⟨R, n, L⟩ := x
    unfold checkBody at he
    obtain ⟨u1, -, he⟩ := bind_eq_ok.1 he
    obtain ⟨u2, -, he⟩ := bind_eq_ok.1 he
    obtain ⟨u3, h3, -⟩ := bind_eq_ok.1 he
    cases u3
    have hl2 := (VE.NormDefaults.forIn_unit_ok _ (fun x r hx => by
      simp only [bind, Except.bind, pure, Except.pure] at hx
      split at hx
      · split at hx <;> cases hx <;> rfl
      · cases hx) _).1 h3 rel (by simp only at hrel; simp [hrel])
    simp only [bind, Except.bind, pure, Except.pure] at hl2
    split at hl2
    · rename_i hro; exact ⟨Rt, hRt, hro⟩
    · cases hl2
  · cases he

/-- A layer symbol is a regulated or defined name. -/
theorem layer_keep {T : VE.Norms.Tree} {x : String} (h : x ∈ VE.Norms.layerNames T) :
    PWF.keepOf T.regulated T.definitions x = true := by
  obtain ⟨q, hq, rfl⟩ := List.mem_map.mp h
  obtain ⟨y, _, hl⟩ := List.mem_filterMap.mp hq
  simp only [PWF.keepOf, List.contains_iff_mem, List.mem_append, List.mem_map]
  cases q with
  | reg r => exact Or.inl ⟨r, VE.Norms.lookupSym_reg hl, rfl⟩
  | defn d => exact Or.inr ⟨d, VE.Norms.lookupSym_defn hl, rfl⟩

/-- The base vocabulary is inside layer 0 of the correlated plained document. -/
theorem baseEnv_layer0 (D : ClauseDoc) (hw : WellFormedRights (plain D) = true) :
    ∀ p s, (baseEnv D).predicates p = some s →
      (VE.Norms.envAt (soften (correlate (plain D))) 0).predicates p = some s := by
  have F := PWF.facts ⟨plain D, [], []⟩ hw
  intro p s hp
  obtain ⟨hk, -⟩ := PWF.baseEnv_keep F hp
  have hl : p ∉ VE.Norms.layerNames (soften (correlate (plain D))).T := fun hm => by
    have := layer_keep hm; simp only [soften] at this; rw [this] at hk; cases hk
  simp only [VE.Norms.envAt, VE.Norms.hide, List.drop_zero]
  split
  · rename_i hm; exact absurd hm hl
  · exact (PWF.envP F).2.2 p s hp hk

end SlotWF
open SlotWF in
/-- The hP of every slot theorem at this instance (4.2). -/
theorem clauseSlot_wellFormed (D : ClauseDoc) (h : WellFormedClauses D = true) (hw : WellFormedRights (plain D) = true) :
  VE.Compose.SlotWellFormed (correlate (plain D)) (clauseSlot D) := by
  intro φ hφ
  rw [clauseSlot_eq] at hφ
  rcases List.mem_append.1 hφ with hφ | hφ
  · exact (VE.Rights.rightsValid_of_wellFormed _ hw).limTyped φ hφ
  simp only [relPremises, VE.Compose.Labelled.formulas, relPremisesLabelled, List.mem_map, List.mem_filterMap,
    Option.bind_eq_some_iff, Option.map_eq_some_iff] at hφ
  obtain ⟨_, ⟨x, hx, rel, hrel, j, hj, rfl⟩, rfl⟩ := hφ
  obtain ⟨Rt, hRt, hro⟩ := entry_relation D h x hx rel hrel
  obtain ⟨R, n, L⟩ := x
  simp only at hrel hRt hro ⊢
  -- the line's own instance `N0`, and its holder slot's sort (rights' `checkShape`)
  obtain ⟨hsh, hmem, -, -, -⟩ := entry_facts D h R n L hx
  have hsh' : L.line.kind ≠ .power ∧ L.line.fanOut = [] ∧ L.line.norm.isSome := by
    simp only [shapeOk, hrel, Option.isNone_some, Bool.and_false, Bool.false_or, Bool.and_eq_true, bne_iff_ne,
      ne_eq, List.isEmpty_iff] at hsh
    exact ⟨hsh.1.1, hsh.1.2, hsh.2⟩
  obtain ⟨hk, hf, hnm⟩ := hsh'
  obtain ⟨nm, hnm⟩ := Option.isSome_iff_exists.1 hnm
  have hinst : VE.Rights.instancesOf R L.line 0 = [⟨R, L.line, L.line.kind, VE.Rights.ikindOf L.line.kind, nm, none⟩] := by
    unfold VE.Rights.instancesOf; cases hK : L.line.kind <;> simp_all
  have hN0 := own_instance_mem R L.line nm hk hf hnm _ 0 hmem
  rw [hinst] at hro
  simp only [relationOk, List.head?_cons, Option.map_some, Bool.and_eq_true, bne_iff_ne, ne_eq, decide_eq_true_eq,
    beq_iff_eq, hj, Option.all_some, Bool.or_eq_true, Option.some.injEq] at hro
  obtain ⟨⟨⟨⟨⟨hab, ha⟩, hb⟩, hp⟩, -⟩, ⟨hjab, hslot⟩, hH⟩ := hro
  have hcr : VE.Rights.checkRights D.doc = .ok () := by
    rw [← PWF.checkRights_plain]; exact (PWF.facts ⟨plain D, [], []⟩ hw).rights
  have hss : sortsOf D.doc ⟨R, L.line, L.line.kind, VE.Rights.ikindOf L.line.kind, nm, none⟩ =
      lineSorts D.doc.soft L.line := by simp [sortsOf, lineSorts, hnm]
  have hhold := holder_sort D.doc Rt _ (shape_ok D.doc hcr _ hN0 Rt hRt)
    (by cases hK : L.line.kind <;> simp_all [VE.Rights.ikindOf]) hRt
    (by rw [hss]; intro he; rw [he] at ha; cases ha)
  rw [hss, hslot] at hhold
  -- every sort of the line is declared (W1's `Valid` of the correlated tree: a regulated predicate's sorts)
  have hdecl : ∀ s ∈ lineSorts D.doc.soft L.line, s ∈ (baseEnv D).sorts := by
    intro s hs
    have hv := VE.Norms.valid_of_wellFormed _
      (VE.SoftNorms.softValid_of_wellFormed _ (VE.Rights.rightsValid_of_wellFormed _ hw).wfSoft).wf
    simp only [lineSorts, hnm, Option.map_some, Option.getD_some, VE.SoftNorms.sortsOf, VE.SoftNorms.sortsIn] at hs
    cases hr : D.doc.soft.T.regulated.find? (·.name == nm.pred) with
    | none => simp [hr] at hs
    | some r =>
      simp only [hr, Option.map_some, Option.getD_some] at hs
      exact (hv.decl _ (hv.regulated r (List.mem_of_find?_eq_some hr))).2.2 s hs
  have hget : ∀ k, k < (lineSorts D.doc.soft L.line).length →
      (lineSorts D.doc.soft L.line).getD k "" ∈ (baseEnv D).sorts := fun k hk =>
    hdecl _ (by rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hk, Option.getD_some]; exact List.getElem_mem hk)
  have hjl : j < (lineSorts D.doc.soft L.line).length := by rcases hjab with rfl | rfl <;> assumption
  have hsj : (lineSorts D.doc.soft L.line).getD j "" = Rt.holder := by
    simp [List.getD_eq_getElem?_getD, hhold]
  have hG : holderGuardOf D R = Rt.guard := by simp [holderGuardOf, hRt]
  refine VE.Norms.wf_mono (E := baseEnv D) (E' := VE.Norms.envAt (soften (correlate (plain D))) 0) rfl rfl
    (baseEnv_layer0 D hw) _ _ ?_
  simp only [totalF, VE.Formula.WellFormed, hG, hsj]
  refine ⟨hsj ▸ hget j hjl, (VE.check_iff_wellFormed _ _ _).mp hH, ?_⟩
  by_cases haj : rel.slots.1 = j
  · subst haj
    have hbj : ¬ rel.slots.2 = rel.slots.1 := fun e => hab e.symm
    refine ⟨by simpa using hget _ hb, _, _, hp, ?_, ?_⟩ <;> simp [VE.Term.sortOf, hbj, ← hsj]
  · have hbj : rel.slots.2 = j := by rcases hjab with e | e; exact absurd e.symm haj; exact e.symm
    subst hbj
    refine ⟨by simpa [haj] using hget _ ha, _, _, hp, ?_, ?_⟩ <;> simp [VE.Term.sortOf, haj, ← hsj]

end VE.RightClauses
