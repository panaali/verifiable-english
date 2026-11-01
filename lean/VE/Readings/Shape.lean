import VE.Readings.Choice

/-! The shape of the documents S1's `build` and S2's `sup` assemble (docs/spec/composition-s2.md 1.4, 8.3): every
field of the soft document but the rule list is the frame's (`sup` extends only the environment, by the choice
vocabulary); the rule list is the frame's followed by the norm contents placed, in item order; and the rights
fields grow by the rights contents placed, measured by `junk`. -/
namespace VE.Readings
open VE.SoftNorms (SoftNode SoftDoc)
open VE.Rights (RightsDoc)
open VE.Compose (Content)

/-- The rule a content contributes. -/
def normsOf : Content → List SoftNode
  | .norm N => [N]
  | _ => []

/-- How much rights material a document holds: rights, limitations, bars and source lines. -/
def junk (X : RightsDoc) : Nat := X.rs.length + X.limits.length + X.bars.length + (X.sourceOrder.getD []).length

/-- How much rights material a content adds. -/
def contrib : Content → Nat
  | .right R => 1 + R.lines.length
  | .rightLines _ ls => ls.length
  | .limitation _ => 1
  | _ => 0

theorem place_soft_E (X : RightsDoc) (c : Content) (cs : List (String × List String)) :
    (place X c cs).soft.E = X.soft.E := by cases c <;> rfl
theorem place_soft_lits (X : RightsDoc) (c : Content) (cs : List (String × List String)) :
    (place X c cs).soft.lits = X.soft.lits := by cases c <;> rfl
theorem place_soft_soft (X : RightsDoc) (c : Content) (cs : List (String × List String)) :
    (place X c cs).soft.soft = X.soft.soft := by cases c <;> rfl
theorem place_regulated (X : RightsDoc) (c : Content) (cs : List (String × List String)) :
    (place X c cs).soft.T.regulated = X.soft.T.regulated := by cases c <;> rfl
theorem place_definitions (X : RightsDoc) (c : Content) (cs : List (String × List String)) :
    (place X c cs).soft.T.definitions = X.soft.T.definitions := by cases c <;> rfl
theorem place_nodes (X : RightsDoc) (c : Content) (cs : List (String × List String)) :
    (place X c cs).soft.T.nodes = X.soft.T.nodes ++ normsOf c := by
  cases c <;> simp [place, normsOf]
theorem place_junk (X : RightsDoc) (c : Content) (cs : List (String × List String)) :
    junk (place X c cs) = junk X + contrib c := by
  cases c <;> simp [place, junk, contrib] <;> omega

theorem copyContent_norms (D : Doc) (c : Content) : normsOf (copyContent D c) = (normsOf c).map (copyOver D) := by
  cases c <;> rfl
theorem copyContent_contrib (D : Doc) (c : Content) : contrib (copyContent D c) = contrib c := by
  cases c <;> rfl
theorem gateContent_contrib (D : Doc) (m i : Nat) (c : Content) : contrib (gateContent D m i c) = contrib c := by
  cases c <;> rfl

/-! ## `build` -/

def buildNodes (keep : String → Bool) (pick : ReadingSet → Option Candidate) : Item → List SoftNode
  | .fixed u c _ => if keep u then normsOf c else []
  | .bar _ _ => []
  | .set R => match (pick R).bind (fun a => a.content.map (fun c => (c, a.cites))) with
    | some (c, _) => normsOf c
    | none => []

def buildJunk (keep : String → Bool) (pick : ReadingSet → Option Candidate) : Item → Nat
  | .fixed u c _ => if keep u then contrib c else 0
  | .bar u _ => if keep u then 1 else 0
  | .set R => match (pick R).bind (fun a => a.content.map (fun c => (c, a.cites))) with
    | some (c, _) => contrib c
    | none => 0

/-- What a fold step leaves of the soft document, and how it grows the rules and the rights material. -/
structure Grows (X X' : RightsDoc) (ns : List SoftNode) (j : Nat) : Prop where
  E : X'.soft.E = X.soft.E
  lits : X'.soft.lits = X.soft.lits
  soft : X'.soft.soft = X.soft.soft
  regulated : X'.soft.T.regulated = X.soft.T.regulated
  definitions : X'.soft.T.definitions = X.soft.T.definitions
  nodes : X'.soft.T.nodes = X.soft.T.nodes ++ ns
  junk : junk X' = junk X + j

theorem Grows.refl (X : RightsDoc) : Grows X X [] 0 := ⟨rfl, rfl, rfl, rfl, rfl, by simp, by simp⟩

theorem Grows.trans {X Y Z : RightsDoc} {ns ns' : List SoftNode} {j j' : Nat} (h : Grows X Y ns j)
    (h' : Grows Y Z ns' j') : Grows X Z (ns ++ ns') (j + j') :=
  ⟨h'.E.trans h.E, h'.lits.trans h.lits, h'.soft.trans h.soft, h'.regulated.trans h.regulated,
    h'.definitions.trans h.definitions, by rw [h'.nodes, h.nodes, List.append_assoc], by rw [h'.junk, h.junk]; omega⟩

theorem grows_place (X : RightsDoc) (c : Content) (cs : List (String × List String)) :
    Grows X (place X c cs) (normsOf c) (contrib c) :=
  ⟨place_soft_E X c cs, place_soft_lits X c cs, place_soft_soft X c cs, place_regulated X c cs,
    place_definitions X c cs, place_nodes X c cs, place_junk X c cs⟩

theorem grows_bar (X : RightsDoc) (b : VE.Rights.Bar) : Grows X { X with bars := X.bars ++ [b] } [] 1 :=
  ⟨rfl, rfl, rfl, rfl, rfl, by simp, by simp [junk]; omega⟩

theorem build_grows (D : Doc) (keep : String → Bool) (pick : ReadingSet → Option Candidate) :
    ∀ (l : List Item) (acc : RightsDoc × List VE.Formula),
      Grows acc.1 (l.foldl (buildStep keep pick) acc).1 (l.flatMap (buildNodes keep pick))
        (l.map (buildJunk keep pick)).sum
  | [], acc => by simpa using Grows.refl acc.1
  | it :: l, acc => by
    simp only [List.foldl_cons, List.flatMap_cons, List.map_cons, List.sum_cons]
    refine Grows.trans ?_ (build_grows D keep pick l _)
    cases it with
    | fixed u c cs =>
      simp only [buildStep, buildNodes, buildJunk]
      split
      · exact grows_place _ c cs
      · exact Grows.refl _
    | bar u b =>
      simp only [buildStep, buildNodes, buildJunk]
      split
      · exact grows_bar _ b
      · exact Grows.refl _
    | set R =>
      simp only [buildStep, buildNodes, buildJunk]
      rcases hp : (pick R).bind (fun a => a.content.map (fun c => (c, a.cites))) with _ | ⟨c, cs⟩
      · exact Grows.refl _
      · exact grows_place _ c cs

theorem build_shape (D : Doc) (keep : String → Bool) (pick : ReadingSet → Option Candidate) :
    Grows D.frame (build D keep pick).1 (D.items.flatMap (buildNodes keep pick)) (D.items.map (buildJunk keep pick)).sum :=
  build_grows D keep pick D.items (D.frame, [])

/-! ## `sup` -/

/-- The fold step of `sup`, as written there. -/
def supStep (D : Doc) (acc : (RightsDoc × List VE.Formula) × Nat) (it : Item) : (RightsDoc × List VE.Formula) × Nat :=
  match it with
    | .fixed _ c cs => ((place acc.1.1 (copyContent D c) (copyCites D cs), acc.1.2 ++ asserted c), acc.2)
    | .bar _ b => (({ acc.1.1 with bars := acc.1.1.bars ++ [b] }, acc.1.2), acc.2)
    | .set R =>
      ((List.range R.candidates.length).foldl (fun acc' i =>
        match R.candidates[i]?.bind (fun a => a.content.map (fun c => (c, a.cites))) with
        | some (c, cs) => let g := gateContent D acc.2 i c
                          (place acc'.1 g cs, acc'.2 ++ asserted g)
        | none => acc') acc.1, acc.2 + 1)

theorem sup_eq (D : Doc) : sup D = (D.items.foldl (supStep D) ((supFrame D, []), 0)).1 := rfl

def candNodes (D : Doc) (m : Nat) (R : ReadingSet) (i : Nat) : List SoftNode :=
  match R.candidates[i]?.bind (fun a => a.content.map (fun c => (c, a.cites))) with
  | some (c, _) => normsOf (gateContent D m i c)
  | none => []

def candJunk (R : ReadingSet) (i : Nat) : Nat :=
  match R.candidates[i]?.bind (fun a => a.content.map (fun c => (c, a.cites))) with
  | some (c, _) => contrib c
  | none => 0

def isSet : Item → Bool
  | .set _ => true
  | _ => false

def supItemNodes (D : Doc) (m : Nat) : Item → List SoftNode
  | .fixed _ c _ => normsOf (copyContent D c)
  | .bar _ _ => []
  | .set R => (List.range R.candidates.length).flatMap (candNodes D m R)

def supItemJunk : Item → Nat
  | .fixed _ c _ => contrib c
  | .bar _ _ => 1
  | .set R => ((List.range R.candidates.length).map (candJunk R)).sum

def supNodesAux (D : Doc) : List Item → Nat → List SoftNode
  | [], _ => []
  | it :: l, m => supItemNodes D m it ++ supNodesAux D l (if isSet it then m + 1 else m)

theorem sup_inner_grows (D : Doc) (m : Nat) (R : ReadingSet) :
    ∀ (is : List Nat) (acc : RightsDoc × List VE.Formula),
      Grows acc.1 (is.foldl (fun acc' i =>
        match R.candidates[i]?.bind (fun a => a.content.map (fun c => (c, a.cites))) with
        | some (c, cs) => let g := gateContent D m i c
                          (place acc'.1 g cs, acc'.2 ++ asserted g)
        | none => acc') acc).1 (is.flatMap (candNodes D m R)) (is.map (candJunk R)).sum
  | [], acc => by simpa using Grows.refl acc.1
  | i :: is, acc => by
    simp only [List.foldl_cons, List.flatMap_cons, List.map_cons, List.sum_cons]
    refine Grows.trans ?_ (sup_inner_grows D m R is _)
    simp only [candNodes, candJunk]
    split
    · rename_i c cs _
      have := grows_place acc.1 (gateContent D m i c) cs
      rw [gateContent_contrib] at this
      exact this
    · exact Grows.refl _

theorem sup_grows (D : Doc) :
    ∀ (l : List Item) (acc : (RightsDoc × List VE.Formula) × Nat),
      Grows acc.1.1 (l.foldl (supStep D) acc).1.1 (supNodesAux D l acc.2) (l.map supItemJunk).sum
  | [], acc => by simpa [supNodesAux] using Grows.refl acc.1.1
  | it :: l, acc => by
    simp only [List.foldl_cons, supNodesAux, List.map_cons, List.sum_cons]
    cases it with
    | fixed u c cs =>
      refine Grows.trans ?_ (sup_grows D l (supStep D acc (.fixed u c cs)))
      have := grows_place acc.1.1 (copyContent D c) (copyCites D cs)
      rw [copyContent_contrib] at this
      exact this
    | bar u b => exact Grows.trans (grows_bar _ b) (sup_grows D l (supStep D acc (.bar u b)))
    | set R => exact Grows.trans (sup_inner_grows D acc.2 R _ acc.1) (sup_grows D l (supStep D acc (.set R)))

theorem sup_shape (D : Doc) :
    Grows (supFrame D) (sup D).1 (supNodesAux D D.items 0) (D.items.map supItemJunk).sum := by
  rw [sup_eq]
  exact sup_grows D D.items ((supFrame D, []), 0)

/-! ## No rights material -/

theorem noRights_junk (X : RightsDoc) : noRights X = true ↔ junk X = 0 := by
  simp only [noRights, Bool.and_eq_true, List.isEmpty_iff, junk, VE.Rights.sourceLines]
  constructor
  · rintro ⟨⟨⟨hr, hl⟩, hb⟩, hs⟩
    rw [hr] at hs
    simp only [List.flatMap_nil] at hs
    rw [hr, hl, hb]
    cases ho : X.sourceOrder <;> simp_all
  · intro h
    have hr : X.rs = [] := List.eq_nil_of_length_eq_zero (by omega)
    have hl : X.limits = [] := List.eq_nil_of_length_eq_zero (by omega)
    have hb : X.bars = [] := List.eq_nil_of_length_eq_zero (by omega)
    have hs : (X.sourceOrder.getD []).length = 0 := by omega
    refine ⟨⟨⟨hr, hl⟩, hb⟩, ?_⟩
    rw [hr]
    cases ho : X.sourceOrder <;> simp_all

theorem supFrame_junk (D : Doc) : junk (supFrame D) = junk D.frame := rfl

theorem le_sum_of_mem_nat : ∀ {l : List Nat} {a : Nat}, a ∈ l → a ≤ l.sum
  | x :: l, a, h => by
    rcases List.mem_cons.mp h with rfl | h
    · simp
    · have := le_sum_of_mem_nat h; simp; omega

theorem candJunk_le (R : ReadingSet) (i : Nat) (hi : i < R.candidates.length) :
    candJunk R i ≤ ((List.range R.candidates.length).map (candJunk R)).sum :=
  le_sum_of_mem_nat (List.mem_map.mpr ⟨i, List.mem_range.mpr hi, rfl⟩)

theorem choiceJunk_le (D : Doc) (c : Choice) :
    ∀ l : List Item, (l.map (buildJunk (fun _ => true) (fun R => (c.index R.id).bind (R.candidates[·]?)))).sum ≤
      (l.map supItemJunk).sum
  | [] => by simp
  | it :: l => by
    simp only [List.map_cons, List.sum_cons]
    have := choiceJunk_le D c l
    suffices buildJunk (fun _ => true) (fun R => (c.index R.id).bind (R.candidates[·]?)) it ≤ supItemJunk it by omega
    cases it with
    | fixed u c' cs => simp [buildJunk, supItemJunk]
    | bar u b => simp [buildJunk, supItemJunk]
    | set R =>
      simp only [buildJunk, supItemJunk]
      cases hi : c.index R.id with
      | none => simp
      | some i =>
        simp only [Option.bind_some]
        cases ha : R.candidates[i]? with
        | none => simp
        | some a =>
          have hlt : i < R.candidates.length := (List.getElem?_eq_some_iff.mp ha).1
          have := candJunk_le R i hlt
          simp only [candJunk, ha] at this
          simpa using this

theorem choiceDoc_noRights (D : Doc) (c : Choice) (h : noRights (sup D).1 = true) :
    noRights (choiceDoc D c).1 = true := by
  rw [noRights_junk] at h ⊢
  have hx := (sup_shape D).junk
  have hy := (build_shape D (fun _ => true) (fun R => (c.index R.id).bind (R.candidates[·]?))).junk
  have := choiceJunk_le D c D.items
  rw [supFrame_junk] at hx
  unfold choiceDoc
  omega

end VE.Readings
