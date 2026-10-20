import VE.Cardinality.Erase
import VE.Time.Count
import VE.Readings.Names

/-! Theorems of `cardinality@0` (docs/spec/quantities.md 3.6, 3.7): counts over a declared finite sort exist and are
unique; the regions of a counted sort partition it, so a region sum denotes its body's count where region constants
are region sizes (`withRegions`); erasure is faithful (`erase_iff`), so W6a entailment of the erased problem is
counting entailment (`cardinality_elab_sound`), and the erased problem is W6a-admitted (`erasedProblem_admitted`).
`CEnv.WellFormed` keeps declared constants apart from region constants: every region name begins with the region
prefix (`regionConst_startsWith`) and names one (sort, region) pair (`regionConst_inj`). The count atoms for W6a's
four counting forms are defined here; their agreement theorems and `refutesC_sound` are qt-a1c's. -/
namespace VE.Cardinality
open VE.Time (QTerm QFormula TStructure TEntails)
universe u v

/-- Some duplicate-free list holds exactly the members of `xs` with `P`. -/
theorem exists_nodup_filter {α : Type u} (P : α → Prop) :
    ∀ xs : List α, ∃ ys : List α, ys.Nodup ∧ ∀ x, x ∈ ys ↔ x ∈ xs ∧ P x
  | [] => ⟨[], List.nodup_nil, by simp⟩
  | a :: xs => by
    classical
    obtain ⟨ys, hnd, hys⟩ := exists_nodup_filter P xs
    by_cases h : P a ∧ a ∉ ys
    · refine ⟨a :: ys, List.nodup_cons.mpr ⟨h.2, hnd⟩, fun x => ?_⟩
      simp only [List.mem_cons, hys]
      constructor
      · rintro (rfl | ⟨hx, hp⟩)
        · exact ⟨Or.inl rfl, h.1⟩
        · exact ⟨Or.inr hx, hp⟩
      · rintro ⟨rfl | hx, hp⟩
        · exact Or.inl rfl
        · exact Or.inr ⟨hx, hp⟩
    · refine ⟨ys, hnd, fun x => ?_⟩
      rw [hys]
      constructor
      · rintro ⟨hx, hp⟩; exact ⟨List.mem_cons_of_mem a hx, hp⟩
      · rintro ⟨hx, hp⟩
        rcases List.mem_cons.mp hx with rfl | hx
        · exact (hys x).mp (Classical.not_not.mp fun hn => h ⟨hp, hn⟩)
        · exact ⟨hx, hp⟩

/-- Two duplicate-free lists with the same members have the same length. -/
theorem nodup_length_eq {α : Type u} :
    ∀ {xs ys : List α}, xs.Nodup → ys.Nodup → (∀ x, x ∈ xs ↔ x ∈ ys) → xs.length = ys.length
  | [], ys, _, _, h => by
    cases ys with
    | nil => rfl
    | cons y _ => exact absurd ((h y).mpr (List.mem_cons_self ..)) (List.not_mem_nil)
  | a :: xs, ys, hx, hy, h => by
    classical
    have ha : a ∈ ys := (h a).mp (List.mem_cons_self ..)
    obtain ⟨hna, hxs⟩ := List.nodup_cons.mp hx
    have hlen := nodup_length_eq hxs (hy.erase a) fun x => by
      rw [List.Nodup.mem_erase_iff hy, ← h x, List.mem_cons]
      constructor
      · intro hm; exact ⟨fun he => hna (he ▸ hm), Or.inr hm⟩
      · rintro ⟨hne, rfl | hm⟩
        · exact absurd rfl hne
        · exact hm
    rw [List.length_cons, hlen, List.length_erase_of_mem ha]
    have : 0 < ys.length := List.length_pos_of_mem ha
    omega

/-- On an admissible structure every count over a declared finite sort exists and is unique, so a count atom and its
negation mean what they say. -/
theorem hasCount_exists_unique {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) :
    ∃ n, HasCount T s b n ∧ ∀ m, HasCount T s b m → m = n := by
  obtain ⟨xs, hxs⟩ := hT.2 s hs
  obtain ⟨ys, hnd, hys⟩ := exists_nodup_filter (fun x => b.holds T x) xs
  have hc : ∀ x, x ∈ ys ↔ T.objects s x ∧ b.holds T x := fun x => by rw [hys, hxs]
  refine ⟨ys.length, ⟨ys, hnd, rfl, hc⟩, ?_⟩
  rintro m ⟨zs, hz, rfl, hzs⟩
  exact nodup_length_eq hz hnd fun x => by rw [hzs, hc]

/-- A count is unique. -/
theorem hasCount_unique {α : Type u} {T : TStructure α} {s : String} {b : Body} {n m : Nat}
    (hn : HasCount T s b n) (hm : HasCount T s b m) : n = m := by
  obtain ⟨xs, hx, rfl, hxs⟩ := hn
  obtain ⟨ys, hy, rfl, hys⟩ := hm
  exact nodup_length_eq hx hy fun x => by rw [hxs, hys]

/-- Each region premise `0 ≤ n` holds where region constants are region sizes. -/
theorem nonneg_hold {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) :
    ∀ a ∈ nonnegPremises E fs, a.tdenote (withRegions E fs T) [] := by
  intro a ha
  obtain ⟨e, he, rfl⟩ := List.mem_map.mp ha
  have hs : ((regionTable E fs).find? (·.1 == e.1)).isSome := List.find?_isSome.mpr ⟨e, he, by simp⟩
  obtain ⟨⟨c, s, r⟩, hf⟩ := Option.isSome_iff_exists.mp hs
  refine ⟨dl, 0, regionSize T s (regionBody (predsOn E fs s) r), rfl, ?_, by omega⟩
  simp [VE.Time.QTerm.tdenote, withRegions, hf]

set_option linter.unusedVariables false in
/-- A proportion holds exactly when the population is nonempty and the share compares as written. -/
theorem proportion_holds_iff {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T) (p : Proportion)
    (hp : Admitted E (.proportion p)) :
    (CFormula.proportion p).holds T ↔
      ∃ n m : Nat, HasCount T p.sort p.whole n ∧ HasCount T p.sort (.and p.whole p.part) m ∧ 0 < n ∧
        p.cmp.holds ((m : Int) * p.den) ((n : Int) * p.num) := by
  simp only [CFormula.holds, Proportion.holds, Int.mul_comm (p.den : Int), Int.mul_comm (p.num : Int)]

/-! ## W6a's four counting forms as count atoms -/

/-- "At least n": `-1 · #b ≤ -n`; "at most n": `#b ≤ n`; "exactly n": `#b = n`. -/
def atLeastAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(-1, b)], .le, -(n : Int)⟩
def atMostAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(1, b)], .le, n⟩
def exactlyAtom (s : String) (b : Body) (n : Nat) : CountAtom := ⟨s, [(1, b)], .eq, n⟩
/-- "Exactly n of the m": exactly m selected and exactly n of them with the property (W6a's `nOfM`). -/
def nOfMFormula (s : String) (n m : Nat) (sel prop : Body) : CFormula :=
  .and (.count (exactlyAtom s sel m)) (.count (exactlyAtom s (.and sel prop) n))

/-- The body as an order@0 formula on the counted variable (de Bruijn index 0). -/
def Body.toFormula : Body → VE.Order.Formula
  | .atom p => .unary p (.var 0)
  | .any => .top
  | .not b => .not b.toFormula
  | .and a b => .and a.toFormula b.toFormula
  | .or a b => .or a.toFormula b.toFormula

/-! ## Region names (spec 3.5): they begin with the region prefix and name one (sort, region) pair -/

open VE.Readings (utf8GetAux_append utf8ByteSize_go_append pos_add_char)
local notation "go" => String.utf8ByteSize.go

theorem get_of_data {s : String} {A rest : List Char} {c : Char} (h : s.data = A ++ c :: rest) :
    s.get ⟨go A⟩ = c := by
  have := utf8GetAux_append A c rest 0
  show String.utf8GetAux s.data 0 _ = c
  rw [h]; simpa using this

/-- `substrEq`'s loop compares the rest `B` of `p` with `s` at the same positions. -/
theorem substrEq_prefix (s p : String) (r : List Char) (hs : s.data = p.data ++ r) :
    ∀ (B A : List Char), p.data = A ++ B → s.substrEq ⟨go A⟩ p ⟨go A⟩ (go B) = true := by
  intro B
  induction B with
  | nil =>
    intro A hp
    have h1 : go A + go [] ≤ s.endPos.byteIdx := by
      show _ ≤ go s.data; rw [hs, hp, utf8ByteSize_go_append, utf8ByteSize_go_append]; simp [String.utf8ByteSize.go]
    have h2 : go A + go [] ≤ p.endPos.byteIdx := by
      show _ ≤ go p.data; rw [hp, utf8ByteSize_go_append]; simp [String.utf8ByteSize.go]
    simp only [String.substrEq, decide_eq_true h1, decide_eq_true h2, Bool.true_and]
    unfold_substrEq_loop
    simp [String.utf8ByteSize.go]
  | cons c B ih =>
    intro A hp
    have hc := Char.utf8Size_pos c
    have hA : go (A ++ [c]) = go A + c.utf8Size := by rw [utf8ByteSize_go_append]; simp [String.utf8ByteSize.go]
    have hB : go (c :: B) = go B + c.utf8Size := rfl
    have h1 : go A + go (c :: B) ≤ s.endPos.byteIdx := by
      show _ ≤ go s.data; rw [hs, hp, utf8ByteSize_go_append, utf8ByteSize_go_append]; omega
    have h2 : go A + go (c :: B) ≤ p.endPos.byteIdx := by
      show _ ≤ go p.data; rw [hp, utf8ByteSize_go_append]; omega
    have ih' := ih (A ++ [c]) (by simp [hp])
    simp only [String.substrEq, decide_eq_true h1, decide_eq_true h2, Bool.true_and] at ih' ⊢
    unfold_substrEq_loop
    have hpos : (⟨go A⟩ : String.Pos) + c = ⟨go (A ++ [c])⟩ := by simp [String.Pos.ext_iff, hA]
    rw [show go (A ++ [c]) + go B = go A + go (c :: B) by omega, decide_eq_true h1, decide_eq_true h2] at ih'
    rw [dif_pos (by simp; omega)]
    simpa only [get_of_data (s := s) (A := A) (c := c) (rest := B ++ r) (by rw [hs, hp]; simp), get_of_data hp, hpos, beq_self_eq_true,
      Bool.true_and] using ih'

theorem nextn_prefix (s p : String) (r : List Char) (hs : s.data = p.data ++ r) :
    ∀ (B A : List Char), p.data = A ++ B → s.toSubstring.nextn B.length ⟨go A⟩ = ⟨go A + go B⟩ := by
  intro B
  induction B with
  | nil => intro A _; rfl
  | cons c B ih =>
    intro A hp
    have hA : go (A ++ [c]) = go A + c.utf8Size := by rw [utf8ByteSize_go_append]; simp [String.utf8ByteSize.go]
    have hne : ¬ ((⟨go A⟩ : String.Pos) = s.endPos) := by
      have := Char.utf8Size_pos c
      simp only [String.Pos.ext_iff]; show ¬ _ = go s.data
      rw [hs, hp, utf8ByteSize_go_append, utf8ByteSize_go_append]; simp [String.utf8ByteSize.go]; omega
    have hnext : s.toSubstring.next ⟨go A⟩ = ⟨go (A ++ [c])⟩ := by
      simp only [String.toSubstring, Substring.next, show ∀ q : String.Pos, ({ } : String.Pos) + q = q from
        fun q => by simp [String.Pos.ext_iff]]
      rw [if_neg hne]
      simp [String.next, get_of_data (s := s) (A := A) (c := c) (rest := B ++ r) (by rw [hs, hp]; simp), hA]
    show s.toSubstring.nextn B.length (s.toSubstring.next _) = _
    rw [hnext, ih (A ++ [c]) (by simp [hp]), hA]
    simp [String.utf8ByteSize.go]; omega

/-- A string whose characters begin with those of `p` starts with `p`. -/
theorem startsWith_of_data (s p : String) (r : List Char) (hs : s.data = p.data ++ r) : s.startsWith p = true := by
  have hn := nextn_prefix s p r hs p.data [] (by simp)
  have hq := substrEq_prefix s p r hs p.data [] (by simp)
  simp only [String.utf8ByteSize.go, Nat.zero_add] at hn hq
  unfold String.startsWith
  show Substring.beq _ _ = true
  simp only [Substring.take, String.toSubstring, show p.length = p.data.length from rfl] at hn ⊢
  rw [show (0 : String.Pos) = { } from rfl, hn]
  simp only [Substring.beq, Substring.bsize]
  simpa [show ∀ t : String, t.endPos.byteIdx = go t.data from fun _ => rfl] using hq

theorem regionConst_startsWith (s : String) (r : Region) : (regionConst s r).startsWith regionPrefix = true :=
  startsWith_of_data _ _ (s.data ++ "__".data ++ (bitString r).data)
    (by simp [regionConst, String.data_append, List.append_assoc])

theorem split_underscore : ∀ (u v x y : List Char), '_' ∉ u → '_' ∉ v → u ++ '_' :: x = v ++ '_' :: y →
    u = v ∧ x = y
  | [], [], _, _, _, _, h => by simpa using h
  | [], _ :: _, _, _, _, hv, h | _ :: _, [], _, _, hv, _, h => by
    simp at h; exact absurd (h.1 ▸ List.mem_cons_self ..) hv
  | a :: u, b :: v, x, y, hu, hv, h => by
    simp only [List.cons_append, List.cons.injEq] at h
    have := split_underscore u v x y (fun h' => hu (List.mem_cons_of_mem a h'))
      (fun h' => hv (List.mem_cons_of_mem b h')) h.2
    exact ⟨by rw [h.1, this.1], this.2⟩

/-- Two (sort, region) pairs never share a region constant. -/
theorem regionConst_inj {s s' : String} {r r' : Region} (h : regionConst s r = regionConst s' r') :
    s = s' ∧ r = r' := by
  have hd := congrArg (fun t => t.data.reverse) h
  simp only [regionConst, bitString, String.data_append, List.reverse_append] at hd
  have hb : ∀ q : Region, '_' ∉ (q.map fun b => if b then '1' else '0').reverse := by intro q hq; simp at hq
  have hs := split_underscore _ _ _ _ (hb r) (hb r') hd
  simp only [List.reverse_inj] at hs
  have h2 : s.data.reverse ++ regionPrefix.data.reverse = s'.data.reverse ++ regionPrefix.data.reverse := by
    simpa using hs.2
  refine ⟨String.ext (by simpa using h2), (List.map_inj_right fun a b h => ?_).mp hs.1⟩
  cases a <;> cases b <;> simp_all

/-! ## Regions partition a counted sort -/

theorem mem_regions : ∀ (n : Nat) (r : Region), r ∈ regions n ↔ r.length = n
  | 0, r => by cases r <;> simp [regions]
  | n + 1, [] => by simp [regions]
  | n + 1, v :: r => by cases v <;> simp [regions, mem_regions n r]

theorem regions_nodup : ∀ n : Nat, (regions n).Nodup
  | 0 => by simp [regions]
  | n + 1 => List.nodup_append.mpr ⟨List.pairwise_map.mpr ((regions_nodup n).imp fun hne he =>
      hne (List.cons.inj he).2), List.pairwise_map.mpr ((regions_nodup n).imp fun hne he =>
      hne (List.cons.inj he).2), by simp⟩

/-- An atom is read at its first index in the region. -/
theorem atom_inRegion (g : String → Bool) (p : String) :
    ∀ ps : List String, p ∈ ps → (Body.atom p).inRegion ps (ps.map g) = g p
  | [], h => absurd h List.not_mem_nil
  | q :: qs, h => by
    have ih := fun h' => atom_inRegion g p qs h'
    simp only [Body.inRegion, List.findIdx?_cons] at ih ⊢
    by_cases hq : q = p
    · subst hq; simp
    · have := ih (by simpa [Ne.symm hq] using h)
      simp only [beq_iff_eq, hq, if_false]
      cases hf : qs.findIdx? (· == p) <;> simp_all

open Classical in
/-- An object lies in the region of its own truth values, and a body holds of it as the region says. -/
theorem inRegion_iff {α : Type u} (T : TStructure α) (x : α) (ps : List String) :
    ∀ b : Body, (∀ p ∈ b.atoms, p ∈ ps) →
      (b.inRegion ps (ps.map fun p => decide (T.relation p [.obj x])) = true ↔ b.holds T x)
  | .atom p, h => by rw [atom_inRegion _ p ps (h p (by simp [Body.atoms]))]; simp [Body.holds]
  | .any, _ => by simp [Body.inRegion, Body.holds]
  | .not b, h => by simp [Body.inRegion, Body.holds, ← inRegion_iff T x ps b (by simpa [Body.atoms] using h)]
  | .and a b, h | .or a b, h => by
    simp only [Body.atoms, List.mem_append] at h
    simp [Body.inRegion, Body.holds, inRegion_iff T x ps a (fun p hp => h p (.inl hp)),
      inRegion_iff T x ps b (fun p hp => h p (.inr hp))]

open Classical in
theorem regionBody_holds {α : Type u} (T : TStructure α) (x : α) :
    ∀ (ps : List String) (r : Region), r.length = ps.length →
      ((regionBody ps r).holds T x ↔ ps.map (fun p => decide (T.relation p [.obj x])) = r)
  | [], [], _ => by simp [regionBody, Body.holds]
  | p :: ps, v :: r, h => by
    have ih := regionBody_holds T x ps r (by simpa using h)
    show (Body.and (if v then .atom p else .not (.atom p)) (regionBody ps r)).holds T x ↔ _
    cases v <;> simp [Body.holds, ih]
  | [], _ :: _, h | _ :: _, [], h => by simp at h

theorem regionSize_eq {α : Type u} {T : TStructure α} {s : String} {b : Body} {n : Nat}
    (h : HasCount T s b n) : regionSize T s b = n := by
  simp only [regionSize, dif_pos (⟨n, h⟩ : ∃ n, HasCount T s b n)]
  exact hasCount_unique (Classical.choose_spec _) h

theorem hasCount_regionSize {α : Type u} {E : CEnv} {T : TStructure α} (hT : Admissible E T) {s : String}
    (hs : s ∈ E.finite) (b : Body) : HasCount T s b (regionSize T s b) := by
  obtain ⟨n, hn, _⟩ := hasCount_exists_unique E T hT s hs b
  rwa [regionSize_eq hn]

/-- On a duplicate-free list of the objects of `s`, a count is the length of a filter. -/
theorem regionSize_filter {α : Type u} {T : TStructure α} {s : String} {ys : List α} (hnd : ys.Nodup)
    (hys : ∀ x, x ∈ ys ↔ T.objects s x) (b : Body) (P : α → Bool)
    (hP : ∀ x, T.objects s x → (P x = true ↔ b.holds T x)) : regionSize T s b = (ys.filter P).length :=
  regionSize_eq ⟨_, hnd.sublist List.filter_sublist, rfl, fun x => by
    rw [List.mem_filter, hys]
    exact ⟨fun h => ⟨h.1, (hP x h.1).mp h.2⟩, fun h => ⟨h.1, (hP x h.1).mpr h.2⟩⟩⟩

theorem length_filter_or {β : Type u} (p q : β → Bool) (h : ∀ x, ¬ (p x = true ∧ q x = true)) :
    ∀ xs : List β, (xs.filter (fun x => p x || q x)).length = (xs.filter p).length + (xs.filter q).length
  | [] => rfl
  | x :: xs => by
    have := length_filter_or p q h xs
    have := h x
    cases hp : p x <;> cases hq : q x <;> simp_all <;> omega

/-- Over distinct keys, the sizes of the classes sum to the size of their union. -/
theorem sum_classes {β : Type u} {γ : Type} [DecidableEq γ] (f : β → γ) (xs : List β) :
    ∀ R : List γ, R.Nodup → (R.map fun r => ((xs.filter fun x => decide (f x = r)).length : Int)).sum =
      (xs.filter fun x => decide (f x ∈ R)).length
  | [], _ => by simp; induction xs <;> simp_all
  | r :: R, h => by
    obtain ⟨hr, hR⟩ := List.nodup_cons.mp h
    have := length_filter_or (fun x => decide (f x = r)) (fun x => decide (f x ∈ R))
      (fun x hx => hr (by simp at hx; exact hx.1 ▸ hx.2)) xs
    simp only [List.map_cons, List.sum_cons, sum_classes f xs R hR, List.mem_cons, Bool.decide_or, this]
    omega

open Classical in
/-- **Regions partition a sort**: a body's count is the sum of the sizes of the regions inside it. -/
theorem regionSize_sum {α : Type u} {E : CEnv} {T : TStructure α} (hT : Admissible E T) {s : String}
    (hs : s ∈ E.finite) (ps : List String) (b : Body) (hb : ∀ p ∈ b.atoms, p ∈ ps) :
    (((regions ps.length).filter fun r => b.inRegion ps r).map
      fun r => (regionSize T s (regionBody ps r) : Int)).sum = regionSize T s b := by
  obtain ⟨xs, hxs⟩ := hT.2 s hs
  obtain ⟨ys, hnd, hys⟩ := exists_nodup_filter (fun _ => True) xs
  have hys' : ∀ x, x ∈ ys ↔ T.objects s x := fun x => by simp [hys, hxs]
  let sig := fun x => ps.map fun p => decide (T.relation p [.obj x])
  have hlen : ∀ x, (sig x).length = ps.length := by simp [sig]
  have hregion : ∀ r ∈ (regions ps.length).filter (fun r => b.inRegion ps r),
      (regionSize T s (regionBody ps r) : Int) = ((ys.filter fun x => decide (sig x = r)).length : Int) := by
    intro r hr
    rw [regionSize_filter hnd hys' _ (fun x => decide (sig x = r)) (fun x _ => by
      rw [regionBody_holds T x ps r ((mem_regions _ r).mp (List.mem_filter.mp hr).1)]; simp [sig])]
  have hbody : regionSize T s b = (ys.filter fun x => decide (sig x ∈ (regions ps.length).filter
      (fun r => b.inRegion ps r))).length :=
    regionSize_filter hnd hys' b _ (fun x _ => by
      rw [← inRegion_iff T x ps b hb]; simp [List.mem_filter, mem_regions, hlen, sig])
  rw [List.map_congr_left hregion, sum_classes sig ys _ ((regions_nodup _).sublist List.filter_sublist), hbody]
  congr; funext x; congr

/-! ## Region sums denote counts where region constants are region sizes -/

theorem sumTerms_denote {α : Type u} {β : Type} (W : TStructure α) (ρ : List α) (f : β → QTerm) (g : β → Int) :
    ∀ l : List β, (∀ x ∈ l, (f x).tdenote W ρ = some (.qty dl (g x))) →
      (sumTerms (l.map f)).tdenote W ρ = some (.qty dl (l.map g).sum)
  | [], _ => rfl
  | [x], h => by simpa [sumTerms] using h x (by simp)
  | x :: y :: l, h => by
    have ih := sumTerms_denote W ρ f g (y :: l) (fun z hz => h z (List.mem_cons_of_mem x hz))
    simp only [List.map_cons, sumTerms] at ih ⊢
    simp [QTerm.tdenote, h x (by simp), ih, List.sum_cons]

theorem mem_regionTable {E : CEnv} {fs : List CFormula} {s : String} {r : Region} (hs : s ∈ countedSorts fs)
    (hr : r ∈ regions (predsOn E fs s).length) : (regionConst s r, s, r) ∈ regionTable E fs :=
  List.mem_flatMap.mpr ⟨s, hs, List.mem_map.mpr ⟨r, hr, rfl⟩⟩

/-- `withRegions` reads a region constant as its own region's size. -/
theorem withRegions_const {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) {s : String}
    {r : Region} (hs : s ∈ countedSorts fs) (hr : r ∈ regions (predsOn E fs s).length) :
    (withRegions E fs T).constant (regionConst s r) =
      some (.qty dl (regionSize T s (regionBody (predsOn E fs s) r))) := by
  obtain ⟨e, he⟩ := Option.isSome_iff_exists.mp ((List.find?_isSome
    (p := fun e : String × String × Region => e.1 == regionConst s r)).mpr ⟨_, mem_regionTable hs hr, by simp⟩)
  obtain ⟨s', _, he'⟩ := List.mem_flatMap.mp (List.mem_of_find?_eq_some he)
  obtain ⟨r', _, rfl⟩ := List.mem_map.mp he'
  obtain ⟨rfl, rfl⟩ := regionConst_inj (by simpa using List.find?_some he)
  simp [withRegions, he]

theorem regionSum_denote {α : Type u} {E : CEnv} {T : TStructure α} (hT : Admissible E T) (fs : List CFormula)
    {s : String} (hs : s ∈ E.finite) (hc : s ∈ countedSorts fs) (b : Body)
    (hb : ∀ p ∈ b.atoms, p ∈ predsOn E fs s) (ρ : List α) :
    (regionSum E fs s b).tdenote (withRegions E fs T) ρ = some (.qty dl (regionSize T s b)) := by
  rw [regionSum, sumTerms_denote _ ρ _ (fun r => (regionSize T s (regionBody (predsOn E fs s) r) : Int)),
    regionSize_sum hT hs _ b hb]
  intro r hr
  simp [QTerm.tdenote, withRegions_const E fs T hc (List.mem_filter.mp hr).1]

theorem mem_firstUse_foldl {β : Type} [BEq β] [LawfulBEq β] (x : β) : ∀ (xs acc : List β),
    x ∈ xs.foldl (fun acc y => if acc.contains y then acc else acc ++ [y]) acc ↔ x ∈ acc ∨ x ∈ xs
  | [], acc => by simp
  | y :: ys, acc => by
    rw [List.foldl_cons, mem_firstUse_foldl x ys]
    by_cases hy : acc.contains y
    · have := List.contains_iff_mem.mp hy
      simp only [hy, if_true, List.mem_cons]
      constructor
      · rintro (h | h) <;> simp [h]
      · rintro (h | rfl | h) <;> simp [*]
    · simp only [hy, List.mem_cons]; simp [or_assoc]

theorem mem_firstUse {β : Type} [BEq β] [LawfulBEq β] {x : β} {xs : List β} : x ∈ firstUse xs ↔ x ∈ xs := by
  unfold firstUse; rw [mem_firstUse_foldl]; simp

/-- A counted body names a counted sort, and its predicates are among that sort's. -/
theorem counted_of_mem {E : CEnv} {fs : List CFormula} {s : String} {b : Body}
    (h : (s, b) ∈ fs.flatMap (·.countBodies)) : s ∈ countedSorts fs ∧ ∀ p ∈ b.atoms, p ∈ predsOn E fs s :=
  ⟨mem_firstUse.mpr (List.mem_map.mpr ⟨_, h, rfl⟩), fun p hp => mem_firstUse.mpr (List.mem_append_left _
    (List.mem_flatMap.mpr ⟨(s, b), List.mem_filter.mpr ⟨h, by simp⟩, hp⟩))⟩

/-! ## Declared symbols keep their meaning (`CEnv.WellFormed`) -/

theorem not_regionName {E : CEnv} (hE : E.WellFormed) (fs : List CFormula) {c : String} {τ : VE.Time.QType}
    (hc : E.q.constants c = some τ) : ∀ e ∈ regionTable E fs, (e.1 == c) = false := by
  intro e he
  obtain ⟨s, _, he'⟩ := List.mem_flatMap.mp he
  obtain ⟨r, _, rfl⟩ := List.mem_map.mp he'
  have := hE.fresh c τ hc
  cases h : (regionConst s r == c)
  · rfl
  · rw [← beq_iff_eq.mp h, regionConst_startsWith] at this; cases this

theorem withRegions_declared {α : Type u} {E : CEnv} (hE : E.WellFormed) (fs : List CFormula) (T : TStructure α)
    {c : String} {τ : VE.Time.QType} (hc : E.q.constants c = some τ) :
    (withRegions E fs T).constant c = T.constant c := by
  have : (regionTable E fs).find? (·.1 == c) = none :=
    List.find?_eq_none.mpr fun e he => by simp [not_regionName hE fs hc e he]
  simp [withRegions, this]

theorem elab_declared {E : CEnv} (hE : E.WellFormed) (fs : List CFormula) {c : String} {τ : VE.Time.QType}
    (hc : E.q.constants c = some τ) : (E.elab fs).constants c = some τ := by
  have : (regionTable E fs).any (·.1 == c) = false :=
    List.any_eq_false.mpr fun e he => by simp [not_regionName hE fs hc e he]
  simp [CEnv.elab, this, hc]

theorem hasType_elab {E : CEnv} (hE : E.WellFormed) (fs : List CFormula) {Γ : List String} {t : QTerm}
    {τ : VE.Time.QType} (h : VE.Time.HasType E.q Γ t τ) : VE.Time.HasType (E.elab fs) Γ t τ := by
  induction h with
  | obj hc => exact .obj (elab_declared hE fs hc)
  | const hv hc => exact .const hv (elab_declared hE fs hc)
  | _ => constructor <;> assumption

/-- Admission in `E.q` is admission in the elaborated environment. -/
theorem admitted_elab {E : CEnv} (hE : E.WellFormed) (fs : List CFormula) {Γ : List String} {a : QFormula}
    (h : VE.Time.Admitted E.q Γ a) : VE.Time.Admitted (E.elab fs) Γ a := by
  induction h <;> constructor <;> first | assumption | exact hasType_elab hE fs ‹_›

/-- A typed term reads only declared constants, which `withRegions` keeps. -/
theorem tdenote_withRegions {α : Type u} {E : CEnv} (hE : E.WellFormed) (fs : List CFormula) (T : TStructure α)
    {Γ : List String} {ρ : List α} {t : QTerm} {τ : VE.Time.QType} (h : VE.Time.HasType E.q Γ t τ) :
    t.tdenote (withRegions E fs T) ρ = t.tdenote T ρ := by
  induction h with
  | obj hc | const _ hc => simp [QTerm.tdenote, withRegions_declared hE fs T hc]
  | add _ _ _ _ il ir => simp [QTerm.tdenote, il, ir]
  | scale _ _ _ iu => simp [QTerm.tdenote, iu]
  | _ => rfl

/-- A well-formed core formula reads only declared constants. -/
theorem denote_congr {E : VE.Order.Environment} (S : VE.Order.Structure.{u})
    (k : String → Option (VE.Order.Value S.Carrier)) (hk : ∀ c σ, E.constants c = some σ → k c = S.constant c)
    (rel : String → List (VE.Order.Value S.Carrier) → Prop) (hr : ∀ p ws, rel p ws ↔ S.relation p ws) :
    ∀ (a : VE.Order.Formula) (Γ : List VE.Order.SortName) (ρ : VE.Order.Valuation S), a.WellFormed E Γ →
      (a.denote { S with constant := k, relation := rel } ρ ↔ a.denote S ρ) := by
  have ht : ∀ (t : VE.Order.Term) Γ ρ σ, t.sortOf E Γ = some σ →
      t.denote { S with constant := k, relation := rel } ρ = t.denote S ρ := by
    intro t Γ ρ
    induction t with
    | var | num => intro _ _; rfl
    | const c => exact hk c
    | add t u it iu =>
      intro σ h
      simp only [VE.Order.Term.sortOf] at h
      split at h
      · rename_i hs; simp only [VE.Order.Term.denote, it _ hs.1, iu _ hs.2]
        rcases VE.Order.Term.denote S ρ t with _ | _ | _ <;> rcases VE.Order.Term.denote S ρ u with _ | _ | _ <;> rfl
      · cases h
    | scale z t it =>
      intro σ h
      simp only [VE.Order.Term.sortOf] at h
      split at h
      · rename_i hs; simp only [VE.Order.Term.denote, it _ hs]; rcases VE.Order.Term.denote S ρ t with _ | _ | _ <;> rfl
      · cases h
  intro a
  induction a with
  | top | bottom => intro _ _ _; exact Iff.rfl
  | unary p t => rintro Γ ρ ⟨s, _, h⟩; simp only [VE.Order.Formula.denote, ht t Γ ρ s h, hr]
  | binary p t u =>
    rintro Γ ρ ⟨s, s', _, h, h'⟩; simp only [VE.Order.Formula.denote, ht t Γ ρ s h, ht u Γ ρ s' h', hr]
  | eq t u => rintro Γ ρ ⟨s, h, h'⟩; simp only [VE.Order.Formula.denote, ht t Γ ρ s h, ht u Γ ρ s h']
  | lt t u | le t u => rintro Γ ρ ⟨h, h'⟩; simp only [VE.Order.Formula.denote, ht t Γ ρ _ h, ht u Γ ρ _ h']
  | not a ih => intro Γ ρ h; simp only [VE.Order.Formula.denote, ih Γ ρ h]
  | and a b ia ib | or a b ia ib | implies a b ia ib =>
    rintro Γ ρ ⟨h, h'⟩; simp only [VE.Order.Formula.denote, ia Γ ρ h, ib Γ ρ h']
  | all s a ih | ex s a ih => rintro Γ ρ ⟨_, _, h⟩; simp only [VE.Order.Formula.denote, ih _ _ h]

/-! ## Recognised universal statements (`bodyOfQ?`) -/

/-- A recognised body means its body and reads only its own bound variable. -/
theorem bodyOfQ_spec {E : VE.Time.QEnv} {s : String} :
    ∀ (a : QFormula) (b : Body), bodyOfQ? a = some b →
      (∀ {α : Type u} (T : TStructure α) x ρ, a.tdenote T (x :: ρ) ↔ b.holds T x) ∧
      ∀ Γ, VE.Time.Admitted E (s :: Γ) a → VE.Time.Admitted E [s] a
  | .unary p (.var 0), b, h => by
    cases h
    refine ⟨fun T x ρ => by simp [QFormula.tdenote, QTerm.tdenote, Body.holds], fun Γ ha => ?_⟩
    cases ha with | unary hp ht => cases ht with | var hs => exact .unary hp (.var (by simpa using hs))
  | .top, b, h | .bottom, b, h => by cases h <;> exact ⟨fun T x ρ => by simp [QFormula.tdenote, Body.holds],
      fun _ _ => by first | exact .top | exact .bottom⟩
  | .not a, b, h => by
    simp only [bodyOfQ?, Option.map_eq_some_iff] at h
    obtain ⟨b', h', rfl⟩ := h
    have ih := bodyOfQ_spec (E := E) (s := s) a b' h'
    exact ⟨fun T x ρ => by simp [QFormula.tdenote, Body.holds, ih.1 T x ρ],
      fun Γ ha => by cases ha with | not ha => exact .not (ih.2 Γ ha)⟩
  | .and a a', b, h | .or a a', b, h | .implies a a', b, h => by
    simp only [bodyOfQ?] at h
    split at h
    · rename_i x y hx hy
      cases h
      have ia := bodyOfQ_spec (E := E) (s := s) a x hx
      have ib := bodyOfQ_spec (E := E) (s := s) a' y hy
      refine ⟨fun T z ρ => ?_, fun Γ ha => ?_⟩
      · simp only [QFormula.tdenote, Body.holds, ia.1 T z ρ, ib.1 T z ρ]
        try (by_cases hb : x.holds T z <;> simp [hb])
      · cases ha <;> constructor <;> first | exact ia.2 Γ ‹_› | exact ib.2 Γ ‹_›
    · cases h
  | .unary _ (.var (_ + 1)), _, h | .unary _ (.obj _), _, h | .unary _ (.num _ _), _, h
  | .unary _ (.const _ _), _, h | .unary _ (.add _ _ _), _, h | .unary _ (.scale _ _ _), _, h
  | .binary .., _, h | .eq .., _, h | .lt .., _, h | .le .., _, h | .all .., _, h | .ex .., _, h
  | .dateOn .., _, h | .dateBefore .., _, h | .dateAfter .., _, h | .dateNoLater .., _, h | .within .., _, h
  | .shift .., _, h | .elapsed .., _, h => by simp [bodyOfQ?] at h

theorem universalsOf_admitted {E : VE.Time.QEnv} {Γ : List String} {a : QFormula} (h : VE.Time.Admitted E Γ a) :
    ∀ x ∈ universalsOf a, VE.Time.Admitted E [] x.2.2 ∧ ∃ a', x.2.2 = .all x.1 a' ∧ bodyOfQ? a' = some x.2.1 := by
  induction h with
  | @all Γ s a' hs hm ha ih =>
    intro x hx
    simp only [universalsOf, List.mem_append] at hx
    rcases hx with hx | hx
    · cases hb : bodyOfQ? a' with
      | none => simp [hb] at hx
      | some b =>
        simp only [hb, List.mem_singleton] at hx; subst hx
        exact ⟨.all hs hm ((bodyOfQ_spec.{0} (E := E) a' b hb).2 Γ ha), a', rfl, hb⟩
    · exact ih x hx
  | ex _ _ _ ih | not _ ih => intro x hx; exact ih x (by simpa [universalsOf] using hx)
  | and _ _ ia ib | or _ _ ia ib | implies _ _ ia ib =>
    intro x hx; simp only [universalsOf, List.mem_append] at hx
    exact hx.elim (ia x) (ib x)
  | _ => intro x hx; simp [universalsOf] at hx

theorem universalsC_admitted {E : CEnv} {f : CFormula} (h : Admitted E f) :
    ∀ x ∈ f.universalsC E, x.1 ∈ E.finite ∧ VE.Time.Admitted E.q [] x.2.2 ∧
      ∃ a', x.2.2 = .all x.1 a' ∧ bodyOfQ? a' = some x.2.1 := by
  induction h with
  | quantity ha =>
    intro x hx
    simp only [CFormula.universalsC, List.mem_filter, List.contains_iff_mem] at hx
    exact ⟨hx.2, universalsOf_admitted ha x hx.1⟩
  | not _ ih => exact ih
  | and _ _ ia ib | or _ _ ia ib | implies _ _ ia ib =>
    intro x hx; simp only [CFormula.universalsC, List.mem_append] at hx
    exact hx.elim (ia x) (ib x)
  | _ => intro x hx; simp [CFormula.universalsC] at hx

theorem countedUniversals_spec {E : CEnv} {fs : List CFormula} (hfs : ∀ a ∈ fs, Admitted E a)
    {x : String × Body × QFormula} (hx : x ∈ countedUniversals E fs) :
    x.1 ∈ countedSorts fs ∧ (∀ p ∈ x.2.1.atoms, p ∈ predsOn E fs x.1) ∧ x.1 ∈ E.finite ∧
      VE.Time.Admitted E.q [] x.2.2 ∧ ∃ a', x.2.2 = .all x.1 a' ∧ bodyOfQ? a' = some x.2.1 := by
  have hx' := List.mem_filter.mp (mem_firstUse.mp hx)
  obtain ⟨f, hf, hxf⟩ := List.mem_flatMap.mp hx'.1
  exact ⟨List.contains_iff_mem.mp hx'.2, fun p hp => mem_firstUse.mpr (List.mem_append_right _
    (List.mem_flatMap.mpr ⟨x, List.mem_filter.mpr ⟨hx, by simp⟩, hp⟩)), universalsC_admitted (hfs f hf) x hxf⟩

theorem holds_withRegions {α : Type u} (E : CEnv) (fs : List CFormula) (T : TStructure α) (x : α) :
    ∀ b : Body, b.holds (withRegions E fs T) x ↔ b.holds T x
  | .atom _ | .any => Iff.rfl
  | .not b => by simp [Body.holds, holds_withRegions E fs T x b]
  | .and a b | .or a b => by simp [Body.holds, holds_withRegions E fs T x a, holds_withRegions E fs T x b]

theorem hasCount_zero {α : Type u} {T : TStructure α} {s : String} {b : Body} {n : Nat} (h : HasCount T s b n) :
    n = 0 ↔ ∀ x, T.objects s x → ¬ b.holds T x := by
  obtain ⟨xs, _, rfl, hxs⟩ := h
  rw [List.length_eq_zero_iff]
  constructor
  · rintro rfl x hx hb; exact List.not_mem_nil ((hxs x).mpr ⟨hx, hb⟩)
  · intro h; exact List.eq_nil_iff_forall_not_mem.mpr fun x hx => h x ((hxs x).mp hx).1 ((hxs x).mp hx).2

/-! ## The soundness theorems (spec 3.6) -/

set_option linter.unusedVariables false in
theorem withRegions_admissible {α : Type u} (E : CEnv) (hE : E.WellFormed) (fs : List CFormula)
    (T : TStructure α) (hT : Admissible E T) : (withRegions E fs T).Admissible (E.elab fs) := by
  refine ⟨fun c τ hc => ?_, hT.1.2⟩
  simp only [CEnv.elab] at hc
  split at hc
  · rename_i hany
    cases hc
    obtain ⟨e, he, hec⟩ := List.any_eq_true.mp hany
    obtain ⟨⟨c', s, r⟩, hf⟩ := Option.isSome_iff_exists.mp
      ((List.find?_isSome (p := fun e : String × String × Region => e.1 == c)).mpr ⟨e, he, hec⟩)
    exact ⟨.qty dl (regionSize T s (regionBody (predsOn E fs s) r)), by simp [withRegions, hf], rfl⟩
  · rename_i hany
    have hn : (regionTable E fs).find? (·.1 == c) = none :=
      List.find?_eq_none.mpr fun e he h => hany (List.any_eq_true.mpr ⟨e, he, h⟩)
    obtain ⟨v, hv, ht⟩ := hT.1.1 c τ hc
    exact ⟨v, by simp [withRegions, hn, hv], ht⟩

set_option linter.unusedVariables false in
theorem bridge_hold {α : Type u} (E : CEnv) (hE : E.WellFormed) (fs : List CFormula) (T : TStructure α)
    (hT : Admissible E T) (hfs : ∀ a ∈ fs, Admitted E a) :
    ∀ a ∈ bridgePremises E fs, a.tdenote (withRegions E fs T) [] := by
  intro a ha
  obtain ⟨⟨s, b, U⟩, hx, rfl⟩ := List.mem_map.mp ha
  obtain ⟨hc, hb, hs, _, a', hU, ha'⟩ := countedUniversals_spec hfs hx
  simp only at hc hb hs hU ha'
  subst hU
  have key : (QFormula.all s a').tdenote (withRegions E fs T) [] ↔
      (QFormula.eq (regionSum E fs s (.not b)) (.num dl 0)).tdenote (withRegions E fs T) [] := by
    simp only [QFormula.tdenote, regionSum_denote hT fs hs hc (.not b) (by simpa [Body.atoms] using hb),
      QTerm.tdenote, Option.some.injEq, exists_eq_left', (bodyOfQ_spec (E := E.q) (s := s) a' b ha').1,
      holds_withRegions, VE.Time.TValue.qty.injEq, true_and]
    rw [eq_comm, Int.natCast_eq_zero, hasCount_zero (hasCount_regionSize hT hs (.not b))]
    simp [Body.holds, withRegions]
  exact ⟨key.mp, key.mpr⟩

theorem counts_iff {α : Type u} {E : CEnv} {T : TStructure α} (hT : Admissible E T) {s : String}
    (hs : s ∈ E.finite) : ∀ (terms : List (Int × Body)) (ns : List Nat),
      Counts T s terms ns ↔ ns = terms.map fun kb => regionSize T s kb.2
  | [], [] | [], _ :: _ | _ :: _, [] => by simp [Counts]
  | kb :: rest, n :: ns => by
    simp only [Counts, counts_iff hT hs rest ns, List.map_cons, List.cons.injEq]
    exact and_congr_left fun _ => ⟨fun h => (regionSize_eq h).symm, fun h => h ▸ hasCount_regionSize hT hs _⟩

/-- A count atom holds exactly when its weighted sum of counts stands in its relation to its bound. -/
theorem countAtom_holds_iff {α : Type u} {E : CEnv} {T : TStructure α} (hT : Admissible E T) (c : CountAtom)
    (hs : c.sort ∈ E.finite) :
    c.holds T ↔ c.rel.holds (c.terms.map fun kb => kb.1 * (regionSize T c.sort kb.2 : Int)).sum c.bound := by
  have hz : ∀ terms : List (Int × Body), ((terms.zip (terms.map fun kb => regionSize T c.sort kb.2)).map
      fun p => p.1.1 * (p.2 : Int)) = terms.map fun kb => kb.1 * (regionSize T c.sort kb.2 : Int) := by
    intro terms; induction terms <;> simp_all
  simp only [CountAtom.holds, counts_iff hT hs, exists_eq_left, hz]

/-! ## Ratio statements, given the integers their operands denote -/

section
variable {α : Type u} {T : TStructure α} {n d : CTerm} {zn zd : Int}
  (hn : ∀ z, n.Denotes T z ↔ z = zn) (hd : ∀ z, d.Denotes T z ↔ z = zd)
include hn hd

theorem roundsTo_holds_iff (r : VE.Numbers.Rounding) (D : Int) (k : Nat) :
    (CFormula.roundsTo r n d D k).holds T ↔ 0 < zd ∧ erasedRounding r zn zd D k := by
  simp only [CFormula.holds, hn, hd, exists_and_left, exists_eq_left]
  exact and_congr_right fun h => (roundsTo_ratio_agree r zn zd D k h).symm

theorem percentOf_holds_iff (D : Int) (k : Nat) :
    (CFormula.percentOf n d D k).holds T ↔ 0 < zd ∧ 100 * 10 ^ k * zn = D * zd := by
  simp only [CFormula.holds, hn, hd, exists_and_left, exists_eq_left]

theorem percentRoundsTo_holds_iff (r : VE.Numbers.Rounding) (D : Int) (k : Nat) :
    (CFormula.percentRoundsTo r n d D k).holds T ↔ 0 < zd ∧ erasedRounding r (100 * zn) zd D k := by
  simp only [CFormula.holds, hn, hd, exists_and_left, exists_eq_left]
  refine and_congr_right fun h => ?_
  rw [roundsTo_ratio_agree r _ zd D k h]
  push_cast; exact Iff.rfl
end

/-- A typed ratio operand denotes one integer, and its erasure denotes it in its tag where region constants are
region sizes; erasure reads the operand's tag from `tagOf`. -/
theorem cterm_erase {α : Type u} {E : CEnv} (hE : E.WellFormed) (fs : List CFormula) {T : TStructure α}
    (hT : Admissible E T) {x : CTerm} {g : String} (hx : CTermTyped E x g)
    (hsub : ∀ sb ∈ x.countBodies, sb ∈ fs.flatMap (·.countBodies)) :
    ∃ z, (∀ z', x.Denotes T z' ↔ z' = z) ∧
      (x.erase E fs).tdenote (withRegions E fs T) [] = some (.qty g z) ∧ (x.tagOf E).getD dl = g := by
  cases hx with
  | @quantity t g h =>
    obtain ⟨v, hv, hty, -⟩ := VE.Time.term_faithful hT.1 (VE.Time.typed_nil T) h
    obtain ⟨z, rfl⟩ := VE.Time.typed_qty hty
    refine ⟨z, fun z' => ⟨fun ⟨g', h'⟩ => ?_, fun e => ⟨g, e ▸ hv⟩⟩, ?_, ?_⟩
    · rw [hv] at h'; cases h'; rfl
    · simp [CTerm.erase, tdenote_withRegions hE fs T h, hv]
    · simp [(tagOf_iff E _ g).mpr (.quantity h)]
  | @count s b hs hb =>
    have ⟨hc, hbs⟩ := counted_of_mem (E := E) (hsub (s, b) (by simp [CTerm.countBodies]))
    refine ⟨regionSize T s b, fun z' => ⟨fun ⟨n, hn, e⟩ => by rw [e, regionSize_eq hn],
      fun e => ⟨_, hasCount_regionSize hT hs b, e⟩⟩, regionSum_denote hT fs hs hc b hbs [], ?_⟩
    simp [(tagOf_iff E _ _).mpr (.count hs hb)]

theorem erase_iff_of {α : Type u} (E : CEnv) (hE : E.WellFormed) (fs : List CFormula) (T : TStructure α)
    (hT : Admissible E T) {a : CFormula} (ha : Admitted E a)
    (hsub : ∀ sb ∈ a.countBodies, sb ∈ fs.flatMap (·.countBodies)) :
    a.holds T ↔ (a.erase E fs).tdenote (withRegions E fs T) [] := by
  have hR : ∀ {s b}, s ∈ E.finite → (s, b) ∈ fs.flatMap (·.countBodies) → ∀ k : Int,
      (QTerm.scale dl k (regionSum E fs s b)).tdenote (withRegions E fs T) [] =
        some (.qty dl (k * regionSize T s b)) := fun hs h k => by
    simp [QTerm.tdenote, regionSum_denote hT fs hs (counted_of_mem (E := E) h).1 _ (counted_of_mem h).2]
  induction ha with
  | @quantity a ha =>
    simp only [CFormula.holds, CFormula.erase]
    rw [VE.Time.units_faithful hT.1 ha (VE.Time.typed_nil T),
      VE.Time.units_faithful (withRegions_admissible E hE fs T hT) (admitted_elab hE fs ha) (VE.Time.typed_nil _)]
    refine (denote_congr T.lower _ (fun c σ hc => ?_) _ (fun _ _ => Iff.rfl) a.erase [] _
      (VE.Time.erase_wellTyped ha)).symm
    obtain ⟨τ, hτ, _⟩ := Option.map_eq_some_iff.mp hc
    simp [VE.Time.TStructure.lower, withRegions_declared hE fs T hτ]
  | @count c hs _ =>
    have hL := sumTerms_denote (withRegions E fs T) [] _ (fun kb => kb.1 * (regionSize T c.sort kb.2 : Int))
      c.terms (fun kb hkb => hR hs (hsub _ (List.mem_map.mpr ⟨kb, hkb, rfl⟩)) kb.1)
    simp only [CFormula.holds, CFormula.erase, CountAtom.erase, countAtom_holds_iff hT c hs]
    (cases c.rel <;> simp [Rel.holds, QFormula.tdenote, tcompare_qty, QTerm.tdenote, hL]) <;> exact eq_comm
  | @proportion p hs _ _ _ _ =>
    have hw := hsub (p.sort, p.whole) (by simp [CFormula.countBodies])
    have hbp := (counted_of_mem (E := E) (hsub (p.sort, p.part) (by simp [CFormula.countBodies]))).2
    have ⟨hc, hbw⟩ := counted_of_mem (E := E) hw
    have hN := regionSum_denote hT fs hs hc p.whole hbw []
    have hM := regionSum_denote hT fs hs hc (.and p.whole p.part)
      (fun q hq => (List.mem_append.mp hq).elim (hbw q) (hbp q)) []
    have hex : ∀ P : Nat → Nat → Prop, (∃ n m, HasCount T p.sort p.whole n ∧
        HasCount T p.sort (.and p.whole p.part) m ∧ P n m) ↔
        P (regionSize T p.sort p.whole) (regionSize T p.sort (.and p.whole p.part)) :=
      fun P => ⟨fun ⟨n, m, h1, h2, h⟩ => regionSize_eq h1 ▸ regionSize_eq h2 ▸ h,
        fun h => ⟨_, _, hasCount_regionSize hT hs _, hasCount_regionSize hT hs _, h⟩⟩
    simp only [CFormula.holds, Proportion.holds, CFormula.erase, Proportion.erase]
    rw [hex fun n m => 0 < n ∧ p.cmp.holds (p.den * (m : Int)) (p.num * (n : Int))]
    (cases p.cmp <;> simp [Cmp.holds, Cmp.erase, QFormula.tdenote, tcompare_qty, QTerm.tdenote, hN, hM]) <;>
      exact fun _ => eq_comm
  | @roundsTo r n d D k g _ _ hn hd =>
    simp only [CFormula.countBodies, List.mem_append] at hsub
    obtain ⟨zn, hn', en, gn⟩ := cterm_erase hE fs hT hn fun sb h => hsub sb (.inl h)
    obtain ⟨zd, hd', ed, -⟩ := cterm_erase hE fs hT hd fun sb h => hsub sb (.inr h)
    simp only [roundsTo_holds_iff hn' hd', CFormula.erase, gn, QFormula.tdenote, ed, QTerm.tdenote, tcompare_qty,
      roundingQ_iff _ _ _ _ _ en ed]
  | @percentOf p w D k g _ hp hw =>
    simp only [CFormula.countBodies, List.mem_append] at hsub
    obtain ⟨zp, hp', ep, gp⟩ := cterm_erase hE fs hT hp fun sb h => hsub sb (.inl h)
    obtain ⟨zw, hw', ew, -⟩ := cterm_erase hE fs hT hw fun sb h => hsub sb (.inr h)
    simp [percentOf_holds_iff hp' hw', CFormula.erase, gp, QFormula.tdenote, ew, ep, QTerm.tdenote, tcompare_qty]
    exact fun _ => eq_comm
  | @percentRoundsTo r p w D k g _ _ hp hw =>
    simp only [CFormula.countBodies, List.mem_append] at hsub
    obtain ⟨zp, hp', ep, gp⟩ := cterm_erase hE fs hT hp fun sb h => hsub sb (.inl h)
    obtain ⟨zw, hw', ew, -⟩ := cterm_erase hE fs hT hw fun sb h => hsub sb (.inr h)
    have es : (QTerm.scale g 100 (p.erase E fs)).tdenote (withRegions E fs T) [] = some (.qty g (100 * zp)) := by
      simp [QTerm.tdenote, ep]
    simp only [percentRoundsTo_holds_iff hp' hw', CFormula.erase, gp, QFormula.tdenote, ew, QTerm.tdenote, tcompare_qty,
      roundingQ_iff _ _ _ _ _ es ew]
  | not _ ih => simp only [CFormula.holds, CFormula.erase, QFormula.tdenote, ih hsub]
  | and _ _ ia ib | or _ _ ia ib | implies _ _ ia ib =>
    simp only [CFormula.countBodies, List.mem_append] at hsub
    simp only [CFormula.holds, CFormula.erase, QFormula.tdenote, ia (fun sb h => hsub sb (.inl h)),
      ib (fun sb h => hsub sb (.inr h))]

/-- **Erasure is faithful**: on an admissible structure, a formula of the problem holds exactly when its erasure holds
where region constants are region sizes. -/
theorem erase_iff {α : Type u} (E : CEnv) (hE : E.WellFormed) (fs : List CFormula) (T : TStructure α)
    (hT : Admissible E T) (a : CFormula) (ha : Admitted E a) (hin : a ∈ fs) :
    a.holds T ↔ (a.erase E fs).tdenote (withRegions E fs T) [] :=
  erase_iff_of E hE fs T hT ha fun _ h => List.mem_flatMap.mpr ⟨a, hin, h⟩

/-- **Soundness**: W6a entailment of the erased problem gives counting entailment. -/
theorem cardinality_elab_sound (E : CEnv) (hE : E.WellFormed) (ps : List CFormula) (c : CFormula)
    (hps : ∀ a ∈ ps, Admitted E a) (hc : Admitted E c)
    (h : TEntails.{v} (E.elab (c :: ps)) (erasedProblem E ps c).1 (erasedProblem E ps c).2) :
    CEntails.{v} E ps c := by
  intro α T hT hp
  have hfs : ∀ a ∈ c :: ps, Admitted E a := fun a ha => (List.mem_cons.mp ha).elim (· ▸ hc) (hps a)
  refine (erase_iff E hE _ T hT c hc List.mem_cons_self).mpr
    (h α _ (withRegions_admissible E hE _ T hT) fun a ha => ?_)
  simp only [erasedProblem, List.mem_append, List.mem_map] at ha
  rcases ha with (ha | ha) | ⟨b, hb, rfl⟩
  · exact nonneg_hold E _ T a ha
  · exact bridge_hold E hE _ T hT hfs a ha
  · exact (erase_iff E hE _ T hT b (hps b hb) (List.mem_cons_of_mem c hb)).mp (hp b hb)

theorem sumTerms_typed {E : VE.Time.QEnv} {Γ : List String} :
    ∀ ts : List QTerm, (∀ t ∈ ts, VE.Time.HasType E Γ t (.qty dl)) → VE.Time.HasType E Γ (sumTerms ts) (.qty dl)
  | [], _ => .num (Or.inl rfl)
  | [t], h => h t (by simp)
  | t :: t' :: ts, h => .add (by decide) (Or.inl rfl) (h t (by simp))
      (sumTerms_typed (t' :: ts) fun u hu => h u (List.mem_cons_of_mem t hu))

theorem regionSum_typed {E : CEnv} {fs : List CFormula} {Γ : List String} {s : String} (hs : s ∈ countedSorts fs)
    (b : Body) : VE.Time.HasType (E.elab fs) Γ (regionSum E fs s b) (.qty dl) :=
  sumTerms_typed _ fun t ht => by
    obtain ⟨r, hr, rfl⟩ := List.mem_map.mp ht
    have : (regionTable E fs).any (·.1 == regionConst s r) = true :=
      List.any_eq_true.mpr ⟨_, mem_regionTable hs (List.mem_filter.mp hr).1, by simp⟩
    exact .const (Or.inl rfl) (by simp [CEnv.elab, this])

theorem hasType_validTag {E : VE.Time.QEnv} {Γ : List String} {t : QTerm} {g : String}
    (h : VE.Time.HasType E Γ t (.qty g)) : E.ValidTag g := by
  cases h <;> assumption

/-- A typed ratio operand erases to a term of its tag in the elaborated environment. -/
theorem cterm_typed {E : CEnv} (hE : E.WellFormed) (fs : List CFormula) {x : CTerm} {g : String}
    (hx : CTermTyped E x g) (hsub : ∀ sb ∈ x.countBodies, sb ∈ fs.flatMap (·.countBodies)) :
    VE.Time.HasType (E.elab fs) [] (x.erase E fs) (.qty g) ∧ (x.tagOf E).getD dl = g := by
  cases hx with
  | quantity h => exact ⟨hasType_elab hE fs h, by simp [(tagOf_iff E _ _).mpr (.quantity h)]⟩
  | @count s b hs hb =>
    exact ⟨regionSum_typed (counted_of_mem (E := E) (hsub (s, b) (by simp [CTerm.countBodies]))).1 b,
      by simp [(tagOf_iff E _ _).mpr (.count hs hb)]⟩

theorem erase_admitted {E : CEnv} (hE : E.WellFormed) (fs : List CFormula) {a : CFormula} (ha : Admitted E a)
    (hsub : ∀ sb ∈ a.countBodies, sb ∈ fs.flatMap (·.countBodies)) :
    VE.Time.Admitted (E.elab fs) [] (a.erase E fs) := by
  have hR : ∀ {s} (b : Body), s ∈ countedSorts fs → ∀ k : Int,
      VE.Time.HasType (E.elab fs) [] (.scale dl k (regionSum E fs s b)) (.qty dl) :=
    fun b h k => .scale (by decide) (Or.inl rfl) (regionSum_typed h b)
  induction ha with
  | quantity ha => exact admitted_elab hE fs ha
  | @count c _ _ =>
    have hl := sumTerms_typed (c.terms.map fun kb => QTerm.scale dl kb.1 (regionSum E fs c.sort kb.2)) fun t ht => by
      obtain ⟨kb, hkb, rfl⟩ := List.mem_map.mp ht
      exact hR _ (counted_of_mem (E := E) (hsub _ (List.mem_map.mpr ⟨kb, hkb, rfl⟩))).1 kb.1
    simp only [CFormula.erase, CountAtom.erase]
    cases c.rel <;> constructor <;> first | exact hl | exact .num (Or.inl rfl)
  | @proportion p _ _ _ _ _ =>
    have hc := (counted_of_mem (E := E) (hsub (p.sort, p.whole) (by simp [CFormula.countBodies]))).1
    have hM := hR (.and p.whole p.part) hc p.den
    have hN := hR p.whole hc p.num
    simp only [CFormula.erase, Proportion.erase]
    refine .and (.lt (.num (Or.inl rfl)) (regionSum_typed hc _)) ?_
    cases p.cmp <;> constructor <;> first | exact hM | exact hN
  | @roundsTo r n d D k g _ hg hn hd | @percentRoundsTo r n d D k g _ hg hn hd | @percentOf n d D k g hg hn hd =>
    simp only [CFormula.countBodies, List.mem_append] at hsub
    obtain ⟨hn', gn⟩ := cterm_typed hE fs hn fun sb h => hsub sb (.inl h)
    have hd' := (cterm_typed hE fs hd fun sb h => hsub sb (.inr h)).1
    have hv := hasType_validTag hn'
    simp only [CFormula.erase, gn]
    first
    | exact .and (.lt (.num hv) hd') (roundingQ_admitted r D k hg hv hn' hd')
    | exact .and (.lt (.num hv) hd') (roundingQ_admitted r D k hg hv (.scale hg hv hn') hd')
    | exact .and (.lt (.num hv) hd') (.eq (.scale hg hv hn') (.scale hg hv hd'))
  | not _ ih => exact .not (ih hsub)
  | and _ _ ia ib | or _ _ ia ib | implies _ _ ia ib =>
    simp only [CFormula.countBodies, List.mem_append] at hsub
    constructor
    · exact ia fun sb h => hsub sb (.inl h)
    · exact ib fun sb h => hsub sb (.inr h)

/-- **Admission is preserved**: every formula of the erased problem is W6a-admitted in the elaborated environment. -/
theorem erasedProblem_admitted (E : CEnv) (hE : E.WellFormed) (ps : List CFormula) (c : CFormula)
    (hps : ∀ a ∈ ps, Admitted E a) (hc : Admitted E c) :
    ∀ a ∈ (erasedProblem E ps c).1 ++ [(erasedProblem E ps c).2], VE.Time.Admitted (E.elab (c :: ps)) [] a := by
  have hfs : ∀ a ∈ c :: ps, Admitted E a := fun a ha => (List.mem_cons.mp ha).elim (· ▸ hc) (hps a)
  have herase : ∀ a ∈ c :: ps, VE.Time.Admitted (E.elab (c :: ps)) [] (a.erase E (c :: ps)) :=
    fun a ha => erase_admitted hE _ (hfs a ha) fun _ h => List.mem_flatMap.mpr ⟨a, ha, h⟩
  intro a ha
  simp only [erasedProblem, List.mem_append, List.mem_map, List.mem_singleton] at ha
  rcases ha with ((ha | ha) | ⟨b, hb, rfl⟩) | rfl
  · obtain ⟨e, he, rfl⟩ := List.mem_map.mp ha
    have : (regionTable E (c :: ps)).any (·.1 == e.1) = true := List.any_eq_true.mpr ⟨e, he, by simp⟩
    exact .le (.num (Or.inl rfl)) (.const (Or.inl rfl) (by simp [CEnv.elab, this]))
  · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp ha
    obtain ⟨hcs, -, -, hU, -⟩ := countedUniversals_spec hfs hx
    have hU := admitted_elab hE (c :: ps) hU
    have hz := VE.Time.Admitted.eq (regionSum_typed (E := E) (Γ := []) hcs (.not x.2.1)) (.num (z := 0) (Or.inl rfl))
    exact .and (.implies hU hz) (.implies hz hU)
  · exact herase b (List.mem_cons_of_mem c hb)
  · exact herase c List.mem_cons_self

/-! ## Agreement with W6a's four counting forms (spec 3.7) -/

/-- The units-only restriction relates `p` to an object exactly when the tagged structure does. -/
theorem lower_unary {α : Type u} (T : TStructure α) (p : String) (x : α) :
    T.lower.relation p [.inl x] ↔ T.relation p [.obj x] := by
  refine ⟨fun ⟨vs, hr, hm⟩ => ?_, fun h => ⟨[.obj x], h, rfl⟩⟩
  match vs, hm with
  | [.obj y], hm => cases hm; exact hr
  | [.qty _ _], hm | [], hm | _ :: _ :: _, hm => simp [VE.Time.TValue.forget] at hm

theorem toFormula_denote {α : Type u} (T : TStructure α) (x : α) (ρ : VE.Order.Valuation T.lower) :
    ∀ b : Body, b.toFormula.denote T.lower (.inl x :: ρ) ↔ b.holds T x
  | .atom p => by simp [Body.toFormula, VE.Order.Formula.denote, VE.Order.Term.denote, Body.holds, lower_unary]
  | .any => by simp [Body.toFormula, VE.Order.Formula.denote, Body.holds]
  | .not b => by simp [Body.toFormula, VE.Order.Formula.denote, Body.holds, toFormula_denote T x ρ b]
  | .and a b | .or a b => by
    simp [Body.toFormula, VE.Order.Formula.denote, Body.holds, toFormula_denote T x ρ a, toFormula_denote T x ρ b]

/-- W6a's "at least `n`" holds exactly when the count is at least `n`. -/
theorem atLeast_iff_le {α : Type u} {E : CEnv} {T : TStructure α} (hT : Admissible E T) {s : String}
    (hs : s ∈ E.finite) (b : Body) (n : Nat) :
    (VE.Time.atLeast s n b.toFormula).denote T.lower [] ↔ n ≤ regionSize T s b := by
  classical
  obtain ⟨ys, hnd, hlen, hys⟩ := hasCount_regionSize hT hs b
  simp only [VE.Time.expand_atLeast_iff, toFormula_denote]
  constructor
  · rintro ⟨xs, rfl, hx, hxs⟩
    rw [← hlen, nodup_length_eq hx (hnd.sublist List.filter_sublist) (ys := ys.filter (· ∈ xs)) fun x => by
      simpa using fun h => (hys x).mpr (hxs x h)]
    exact List.length_filter_le _ _
  · intro h
    exact ⟨ys.take n, by simp; omega, hnd.sublist (List.take_sublist _ _),
      fun x hx => (hys x).mp (List.mem_of_mem_take hx)⟩

set_option linter.unusedVariables false in
theorem count_atLeast_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) (hb : BodyTyped E s b) (n : Nat) :
    (CFormula.count (atLeastAtom s b n)).holds T ↔ (VE.Time.atLeast s n b.toFormula).denote T.lower [] := by
  rw [CFormula.holds, countAtom_holds_iff hT _ hs, atLeast_iff_le hT hs]
  simp [atLeastAtom, Rel.holds] <;> omega

set_option linter.unusedVariables false in
theorem count_atMost_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) (hb : BodyTyped E s b) (n : Nat) :
    (CFormula.count (atMostAtom s b n)).holds T ↔ (VE.Time.atMost s n b.toFormula).denote T.lower [] := by
  rw [CFormula.holds, countAtom_holds_iff hT _ hs, VE.Time.atMost, VE.Order.Formula.denote, atLeast_iff_le hT hs]
  simp [atMostAtom, Rel.holds] <;> omega

set_option linter.unusedVariables false in
theorem count_exactly_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (b : Body) (hb : BodyTyped E s b) (n : Nat) :
    (CFormula.count (exactlyAtom s b n)).holds T ↔ (VE.Time.exactly s n b.toFormula).denote T.lower [] := by
  rw [CFormula.holds, countAtom_holds_iff hT _ hs, VE.Time.exactly, VE.Order.Formula.denote,
    VE.Order.Formula.denote, atLeast_iff_le hT hs, atLeast_iff_le hT hs]
  simp [exactlyAtom, Rel.holds] <;> omega

/-- Follows from `count_exactly_agree`; on the wire W6a's `n_of_m` means "exactly". -/
theorem count_nOfM_agree {α : Type u} (E : CEnv) (T : TStructure α) (hT : Admissible E T)
    (s : String) (hs : s ∈ E.finite) (sel prop : Body) (h₁ : BodyTyped E s sel) (h₂ : BodyTyped E s prop)
    (n m : Nat) :
    (nOfMFormula s n m sel prop).holds T ↔
      (VE.Time.nOfM s n m sel.toFormula prop.toFormula).denote T.lower [] := by
  simp only [nOfMFormula, VE.Time.nOfM, CFormula.holds, VE.Order.Formula.denote]
  exact and_congr (count_exactly_agree E T hT s hs sel h₁ m)
    (count_exactly_agree E T hT s hs (.and sel prop) ⟨h₁, h₂⟩ n)

/-! ## Finite countermodels (spec 3.9) -/

theorem firstUse_nodup {β : Type} [BEq β] [LawfulBEq β] (xs : List β) : (firstUse xs).Nodup := by
  suffices ∀ (xs acc : List β), acc.Nodup →
      (xs.foldl (fun acc x => if acc.contains x then acc else acc ++ [x]) acc).Nodup from this xs [] List.nodup_nil
  intro xs
  induction xs with
  | nil => exact fun _ h => h
  | cons y ys ih =>
    intro acc h
    rw [List.foldl_cons]
    split
    · exact ih acc h
    · rename_i hy
      exact ih _ (List.nodup_append.mpr ⟨h, by simp, fun a ha b hb => by
        simp only [List.mem_singleton] at hb; subst hb; exact fun e => hy (List.contains_iff_mem.mpr (e ▸ ha))⟩)

/-- On a valid finite model, a body evaluates to true exactly when it holds in the model's tagged lift. -/
theorem evalFin_iff {α : Type} [DecidableEq α] {E : VE.Time.QEnv} {M : VE.Order.FiniteModel α}
    (hM : M.Valid E.erase) (x : α) :
    ∀ b : Body, b.evalFin M x = true ↔ b.holds (VE.Time.lift E M.asStructure) x
  | .atom p => by
    rw [Body.holds, ← lower_unary, (VE.Time.lower_lift hM).2]
    simp [Body.evalFin]
  | .any => by simp [Body.evalFin, Body.holds]
  | .not b => by simp [Body.evalFin, Body.holds, ← evalFin_iff hM x b]
  | .and a b | .or a b => by simp [Body.evalFin, Body.holds, ← evalFin_iff hM x a, ← evalFin_iff hM x b]

/-- `countFin` is the count in the lift of a valid finite model. -/
theorem countFin_eq {α : Type} [DecidableEq α] {E : VE.Time.QEnv} {M : VE.Order.FiniteModel α}
    (hM : M.Valid E.erase) (s : String) (b : Body) :
    countFin M s b = regionSize (VE.Time.lift E M.asStructure) s b :=
  (regionSize_filter (firstUse_nodup _) (fun _ => mem_firstUse) b _ fun x _ => evalFin_iff hM x b).symm

/-- Where region constants are region sizes, the lift of a valid finite model lowers to `withRegionsFinite` on every
formula well formed in the elaborated environment. -/
theorem withRegionsFinite_denote {α : Type} [DecidableEq α] {E : CEnv} (fs : List CFormula)
    {M : VE.Order.FiniteModel α} (hM : M.Valid E.q.erase) (a : VE.Order.Formula)
    (ha : a.WellFormed (E.elab fs).erase []) :
    a.denote (withRegions E fs (VE.Time.lift E.q M.asStructure)).lower [] ↔
      a.denote (withRegionsFinite E fs M).asStructure [] := by
  refine denote_congr (withRegionsFinite E fs M).asStructure _ (fun c σ hc => ?_) _
    (fun p ws => (VE.Time.lower_lift hM).2 p ws) a [] [] ha
  simp only [withRegions, withRegionsFinite]
  cases hf : (regionTable E fs).find? (·.1 == c) with
  | some e => obtain ⟨_, s, r⟩ := e; simp [VE.Time.TValue.forget, countFin_eq hM]
  | none =>
    have hany : (regionTable E fs).any (·.1 == c) = false :=
      List.any_eq_false.mpr fun e he h => by simp [List.find?_eq_none.mp hf e he] at h
    obtain ⟨τ, hτ, -⟩ := Option.map_eq_some_iff.mp hc
    simp only [CEnv.elab, hany] at hτ
    simpa [VE.Time.TStructure.lower] using (VE.Time.lower_lift hM).1 c τ hτ

/-- **A refuted counting claim is not entailed**: a valid finite model of the original vocabulary on which W6a's
countermodel check refutes the erased problem, with each region constant read as its region's size, is a structure
where the premises hold and the conclusion does not. -/
theorem refutesC_sound {α : Type} [DecidableEq α] (E : CEnv) (hE : E.WellFormed) (ps : List CFormula)
    (c : CFormula) (M : VE.Order.FiniteModel α) (hM : M.Valid E.q.erase) (hps : ∀ a ∈ ps, Admitted E a)
    (hc : Admitted E c) (h : refutesC E ps c M = true) : ¬ CEntails.{0} E ps c := by
  intro hent
  let T := VE.Time.lift E.q M.asStructure
  have hT : Admissible E T := ⟨VE.Time.lift_admissible hM, fun s _ => ⟨M.domains s, fun _ => Iff.rfl⟩⟩
  have hfs : ∀ a ∈ c :: ps, Admitted E a := fun a ha => (List.mem_cons.mp ha).elim (· ▸ hc) (hps a)
  have key : ∀ a ∈ c :: ps,
      a.holds T ↔ (a.erase E (c :: ps)).erase.denote (withRegionsFinite E (c :: ps) M).asStructure [] := by
    intro a ha
    have hq := erase_admitted hE (c :: ps) (hfs a ha) fun _ h => List.mem_flatMap.mpr ⟨a, ha, h⟩
    rw [erase_iff E hE _ T hT a (hfs a ha) ha,
      VE.Time.units_faithful (withRegions_admissible E hE _ T hT) hq (VE.Time.typed_nil _)]
    exact withRegionsFinite_denote _ hM _ (VE.Time.erase_wellTyped hq)
  obtain ⟨hp, hn⟩ := (VE.Order.countermodelCheck_iff _ _ _).mp h
  exact hn ((key c List.mem_cons_self).mp (hent α T hT fun a ha => (key a (List.mem_cons_of_mem c ha)).mpr
    (hp _ (List.mem_map.mpr ⟨_, List.mem_append_right _ (List.mem_map.mpr ⟨a, ha, rfl⟩), rfl⟩))))

end VE.Cardinality
