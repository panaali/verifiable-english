import VE.Rights.Semantics

/-! Who owes what to whom (docs/spec/rights.md 4.4, 9.2): projections of which line
instances select on `T″`, attributed to their right and line.

`owes` and `free` say that a duty or liberty instance selects at a tuple; `rightsOf`
and `dutiesOf` collect `(right, line, tuple)` from the holder's and the bearer's end.
`projections_agree` is definitional, and that is its content: a claim and the bearer's
duty are one rule read from two ends. `owes_outcome` makes the completed outcome a
corollary of a selecting line of the document; `same_effect_delivered` is the fact
behind the report line "effect delivered by strict rule M" (4.5). This project has no
`Set`: a tuple set is a predicate with the membership instance below, so `t ∈ rightsOf …`
reads as in the spec. -/
namespace VE.Rights
open VE.Norms (Regulated tupleVal catalaValue)
open VE.SoftNorms (SoftNode SelectsSoftD DecidesSoftD StrictDecidesD ValueSoft)
universe u

/-- A set of tuples, as a predicate. -/
def TupleSet (α : Type u) : Type u := α → Prop

instance {α : Type u} : Membership α (TupleSet α) := ⟨fun s a => s a⟩

theorem mem_tupleSet {α : Type u} (s : TupleSet α) (a : α) : a ∈ s ↔ s a := Iff.rfl

/-- The regulated declaration named `p` (a plain placeholder named `p` when undeclared). -/
def regOf (D : RightsDoc) (p : String) : Regulated :=
  ((correlate D).T.regulated.find? (·.name == p)).getD ⟨p, [], true, .plain, none, none⟩

theorem regOf_name (D : RightsDoc) (p : String) : (regOf D p).name = p := by
  unfold regOf
  cases h : (correlate D).T.regulated.find? (·.name == p) with
  | none => rfl
  | some r => simpa using List.find?_some h

/-- Line `N`'s node selects on `T″` at `ρ`. -/
def SelectsRN (D : RightsDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (N : Line) : Prop :=
  SelectsSoftD (correlate D) S ρ (VE.SoftNorms.fuel (correlate D)) (nodeOf D N)

/-- Bearer `vs₀` owes the act of `N` to holder `vs_slot` here. -/
def owes (D : RightsDoc) (S : VE.Structure.{u}) (N : Line) (vs : List S.Carrier) : Prop :=
  dutyKind N = true ∧ SelectsRN D S (tupleVal vs) N

/-- Holder `vs₀` is at liberty here. -/
def free (D : RightsDoc) (S : VE.Structure.{u}) (N : Line) (vs : List S.Carrier) : Prop :=
  libertyKind N = true ∧ SelectsRN D S (tupleVal vs) N

def rightsOf (D : RightsDoc) (S : VE.Structure.{u}) (h : S.Carrier) : TupleSet (String × Line × List S.Carrier) :=
  fun t => ∃ R N vs, t = (R, N, vs) ∧ (R, N) ∈ linesOf D ∧ VE.TupleTyped S (sortsOf D N) vs ∧
    vs[holderSlot D N]? = some h ∧ SelectsRN D S (tupleVal vs) N

def dutiesOf (D : RightsDoc) (S : VE.Structure.{u}) (b : S.Carrier) : TupleSet (String × Line × List S.Carrier) :=
  fun t => ∃ R N vs, t = (R, N, vs) ∧ (R, N) ∈ linesOf D ∧ dutyKind N = true ∧ VE.TupleTyped S (sortsOf D N) vs ∧
    vs.head? = some b ∧ SelectsRN D S (tupleVal vs) N

/-- 4.4: correlativity by construction, the same `R`, `N` and tuple on both sides. -/
theorem projections_agree (D : RightsDoc) (_h : WellFormedRights D = true) (S : VE.Structure.{u})
    (R : String) (N : Line) (vs : List S.Carrier) {hv bv : S.Carrier} (hN : (R, N) ∈ linesOf D)
    (hk : dutyKind N = true) (typed : VE.TupleTyped S (sortsOf D N) vs)
    (hh : vs[holderSlot D N]? = some hv) (hb : vs.head? = some bv) :
    (R, N, vs) ∈ rightsOf D S hv ↔ (R, N, vs) ∈ dutiesOf D S bv := by
  simp only [mem_tupleSet, rightsOf, dutiesOf]
  constructor
  · rintro ⟨R', N', vs', he, _, _, _, hs⟩
    simp only [Prod.mk.injEq] at he
    obtain ⟨rfl, rfl, rfl⟩ := he
    exact ⟨R, N, vs, rfl, hN, hk, typed, hb, hs⟩
  · rintro ⟨R', N', vs', he, _, _, _, _, hs⟩
    simp only [Prod.mk.injEq] at he
    obtain ⟨rfl, rfl, rfl⟩ := he
    exact ⟨R, N, vs, rfl, hN, typed, hh, hs⟩

theorem catalaValue_true {P N : Prop} {d : Bool} (hP : P) (hN : ¬ N) : catalaValue P N d = some true := by
  classical
  unfold catalaValue
  rw [if_neg (fun h => hN h.2), if_pos hP]

theorem catalaValue_false {P N : Prop} {d : Bool} (hP : ¬ P) (hN : N) : catalaValue P N d = some false := by
  classical
  unfold catalaValue
  rw [if_neg (fun h => hP h.1), if_neg hP, if_pos hN]

/-- The value is the sign that is decided, when the opposite sign is not. -/
theorem valueSoft_of_decides (D : RightsDoc) (p : String) (S : VE.Structure.{u}) (vs : List S.Carrier) (sign : Bool)
    (hd : DecidesSoftD (correlate D) S (tupleVal vs) p sign)
    (hno : ¬ DecidesSoftD (correlate D) S (tupleVal vs) p (!sign)) :
    ValueSoft (correlate D) (regOf D p) S vs = some sign := by
  unfold ValueSoft
  rw [regOf_name]
  cases sign
  · exact catalaValue_false hno hd
  · exact catalaValue_true hd hno

/-- The completed outcome is a corollary of a selecting duty or liberty line of the document. -/
theorem owes_outcome (D : RightsDoc) (_h : WellFormedRights D = true) (S : VE.Structure.{u}) (R : String) (N : Line)
    (hN : (R, N) ∈ linesOf D) (vs : List S.Carrier) (_typed : VE.TupleTyped S (sortsOf D N) vs)
    (hs : SelectsRN D S (tupleVal vs) N)
    (hno : ¬ DecidesSoftD (correlate D) S (tupleVal vs) N.node.pred (!N.node.sign)) :
    ValueSoft (correlate D) (regOf D N.node.pred) S vs = some N.node.sign :=
  valueSoft_of_decides D _ S vs _
    ⟨nodeOf D N, VE.SoftNorms.mem_rulesOn.mpr ⟨lineNode_correlate D hN, rfl⟩, rfl, hs⟩ hno

/-- "Effect delivered" (4.5): a strict decision of `N`'s sign fixes the outcome to `N`'s sign
unless a strict decision of the opposite sign is also present. -/
theorem same_effect_delivered (D : RightsDoc) (h : WellFormedRights D = true) (S : VE.Structure.{u}) (R : String)
    (N : Line) (_hN : (R, N) ∈ linesOf D) (vs : List S.Carrier) (_typed : VE.TupleTyped S (sortsOf D N) vs)
    (hsd : StrictDecidesD (correlate D) S (tupleVal vs) N.node.pred N.node.sign)
    (hno : ¬ StrictDecidesD (correlate D) S (tupleVal vs) N.node.pred (!N.node.sign)) :
    ValueSoft (correlate D) (regOf D N.node.pred) S vs = some N.node.sign := by
  have hw := correlate_wellFormed D h
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ hw
  apply valueSoft_of_decides D _ S vs _
  · obtain ⟨M, hM, hs, hsel⟩ := hsd
    exact ⟨M, hM, hs, (VE.SoftNorms.selects_strict hsv _ M (VE.SoftNorms.mem_rulesOn.mp hM).1 hsel.1).mpr hsel⟩
  · intro hd
    rcases (VE.SoftNorms.decides_split hsv _ _).mp hd with hs | hd
    · exact hno hs
    · have hoh := (VE.SoftNorms.hard_over_soft _ hw S (tupleVal vs)).1 _ _ hsd
      cases hsg : N.node.sign
      · rw [hsg] at hd; exact hoh.1 hd
      · rw [hsg] at hd; exact hoh.2 hd

end VE.Rights
