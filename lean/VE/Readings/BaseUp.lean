import VE.Readings.SupWitness

/-! Bases correspond, upward (docs/spec/composition-s2.md 8.4 `base_up`).

From an admissible base `B₀` of a compatible choice's document and an element `e`, `upB` is the base of `sup D`
that spells `c` on the bits at `ve__here := e` (whose sort `ve__reading` holds every element), interprets every
decision predicate of `sup D` that the name map reaches as `B₀` interprets its preimage, leaves every other decision
predicate of `sup D` empty, and keeps `B₀` elsewhere. Pulled back it is `B₀` (`pull_upB`). It is admissible for
`sup D`'s base vocabulary, keeps the literals, satisfies the exception and coherence premises (the image rules'
premises are the choice's, an unchosen copy's premises hold vacuously: its sufficient conditions carry a false `χ`,
its decision predicates are empty and it never selects), and the slot: the one, coupling and narrowing premises
because `c` is compatible, and every quiet premise because a non-empty decision table belongs to a rule or a pair
of rules of `c`'s document, whose owners are chosen. -/
namespace VE.Readings
open VE.Norms (envAt size Regulated tupleVal Sat ConstantsTyped bindAll atom)
open VE.SoftNorms (SoftNode SoftDoc soften canon envPrime decisions decisionNames exceptedName offName outweighsName
  SelectsSoftD)
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP Labelled Content)
universe u

/-! ## Generic facts -/

/-- `choiceExt_denote` with the relation agreement asked only on the vocabulary's predicates. -/
theorem ext_denote {E : VE.Environment} (hs : "ve__reading" ∉ E.sorts) (hk : E.constants "ve__here" = none)
    {S : VE.Structure.{u}} (R : String → List S.Carrier → Prop) (dom : String → S.Carrier → Prop)
    (k : String → Option S.Carrier) (hrel : ∀ p ss, E.predicates p = some ss → ∀ vs, R p vs ↔ S.relation p vs)
    (hd : ∀ σ, σ ≠ "ve__reading" → dom σ = S.domain σ) (hc : ∀ x, x ≠ "ve__here" → k x = S.constant x) :
    ∀ (φ : VE.Formula) (Γ : List String) (ρ : VE.Valuation S), φ.WellFormed E Γ →
      (φ.denote { S with relation := R, domain := dom, constant := k } ρ ↔ φ.denote S ρ) := by
  have hterm : ∀ (t : VE.Term) (Γ : List String) (s : String) (ρ : VE.Valuation S), t.sortOf E Γ = some s →
      t.denote { S with relation := R, domain := dom, constant := k } ρ = t.denote S ρ := by
    intro t Γ s ρ ht
    cases t with
    | var i => rfl
    | const c =>
      show k c = S.constant c
      apply hc
      rintro rfl
      simp [VE.Term.sortOf, hk] at ht
  intro φ
  induction φ with
  | top | bottom => intros; exact Iff.rfl
  | unary p t =>
    intro Γ ρ ⟨s, hps, ht⟩
    simp only [VE.Formula.denote, hterm t Γ s ρ ht]
    exact exists_congr fun v => and_congr_right fun _ => hrel p _ hps [v]
  | binary p t w =>
    intro Γ ρ ⟨s, r, hps, ht, hw⟩
    simp only [VE.Formula.denote, hterm t Γ s ρ ht, hterm w Γ r ρ hw]
    exact exists_congr fun v => exists_congr fun v' => and_congr_right fun _ => and_congr_right fun _ =>
      hrel p _ hps [v, v']
  | eq t w =>
    intro Γ ρ ⟨s, ht, hw⟩
    simp only [VE.Formula.denote, hterm t Γ s ρ ht, hterm w Γ s ρ hw]
  | not a ih => intro Γ ρ hw; exact not_congr (ih Γ ρ hw)
  | and a b ia ib => intro Γ ρ hw; exact and_congr (ia Γ ρ hw.1) (ib Γ ρ hw.2)
  | or a b ia ib => intro Γ ρ hw; exact or_congr (ia Γ ρ hw.1) (ib Γ ρ hw.2)
  | implies a b ia ib => intro Γ ρ hw; exact imp_congr (ia Γ ρ hw.1) (ib Γ ρ hw.2)
  | all s a ih =>
    intro Γ ρ ⟨hsE, hw⟩
    have hds : dom s = S.domain s := hd s (fun e => hs (e ▸ hsE))
    show (∀ v, dom s v → _) ↔ (∀ v, S.domain s v → _)
    rw [hds]
    exact forall_congr' fun v => imp_congr_right fun _ => ih (s :: Γ) (v :: ρ) hw
  | ex s a ih =>
    intro Γ ρ ⟨hsE, hw⟩
    have hds : dom s = S.domain s := hd s (fun e => hs (e ▸ hsE))
    show (∃ v, dom s v ∧ _) ↔ (∃ v, S.domain s v ∧ _)
    rw [hds]
    exact exists_congr fun v => and_congr_right fun _ => ih (s :: Γ) (v :: ρ) hw

theorem findSome_unique {α β : Type} {f : α → Option β} {a : α} {b : β} :
    ∀ {l : List α}, a ∈ l → f a = some b → (∀ x ∈ l, ∀ y, f x = some y → x = a) → l.findSome? f = some b
  | [], ha, _, _ => absurd ha List.not_mem_nil
  | x :: l, ha, hfa, hu => by
    rw [List.findSome?_cons]
    cases hx : f x with
    | some y =>
      have := hu x List.mem_cons_self y hx
      subst this
      rw [hfa] at hx; cases hx; rfl
    | none =>
      rcases List.mem_cons.mp ha with rfl | ha
      · rw [hfa] at hx; cases hx
      · exact findSome_unique ha hfa (fun x' hx' y hy => hu x' (List.mem_cons_of_mem _ hx') y hy)

theorem find_unique {α : Type} {p : α → Bool} {a : α} :
    ∀ {l : List α}, a ∈ l → p a = true → (∀ x ∈ l, p x = true → x = a) → l.find? p = some a
  | [], ha, _, _ => absurd ha List.not_mem_nil
  | x :: l, ha, hpa, hu => by
    rw [List.find?_cons]
    cases hx : p x with
    | true => rw [hu x List.mem_cons_self hx]
    | false =>
      rcases List.mem_cons.mp ha with rfl | ha
      · rw [hpa] at hx; cases hx
      · exact find_unique ha hpa (fun x' hx' h => hu x' (List.mem_cons_of_mem _ hx') h)

theorem sum_take_succ : ∀ (l : List Nat) (m : Nat) (hm : m < l.length),
    (l.take (m + 1)).sum = (l.take m).sum + l[m]
  | [], _, hm => absurd hm (by simp)
  | x :: l, 0, _ => by simp
  | x :: l, m + 1, hm => by
    simp only [List.take_succ_cons, List.sum_cons, List.getElem_cons_succ]
    rw [sum_take_succ l m (by simp at hm; omega)]
    omega

theorem sum_take_mono (l : List Nat) : ∀ {m m' : Nat}, m ≤ m' → (l.take m).sum ≤ (l.take m').sum := by
  intro m m' h
  induction h with
  | refl => exact Nat.le_refl _
  | step _ ih =>
    rename_i k _
    by_cases hk : k < l.length
    · rw [sum_take_succ l k hk]; omega
    · rw [List.take_of_length_le (by omega : l.length ≤ k + 1)]
      rw [List.take_of_length_le (by omega : l.length ≤ k)] at ih; exact ih

/-- Candidates of the sets have distinct positions. -/
theorem position_inj {D : Doc} {m m' i i' : Nat} (hm : m < D.sets.length) (hm' : m' < D.sets.length)
    (hi : i < D.sets[m].candidates.length) (hi' : i' < D.sets[m'].candidates.length)
    (h : position D m i = position D m' i') : m = m' ∧ i = i' := by
  unfold position at h
  have key : ∀ {a b : Nat} (ha : a < D.sets.length) (hb : b < D.sets.length) {j j' : Nat},
      j < D.sets[a].candidates.length → a < b →
      ((D.sets.take a).map (·.candidates.length)).sum + j + 1 <
        ((D.sets.take b).map (·.candidates.length)).sum + j' + 1 := by
    intro a b ha hb j j' hj hab
    let L := D.sets.map (·.candidates.length)
    have e : ∀ n, (D.sets.take n).map (·.candidates.length) = L.take n := fun n => List.map_take
    have hLa : L[a]'(by simp [L]; exact ha) = D.sets[a].candidates.length := List.getElem_map ..
    have h1 := sum_take_succ L a (by simp [L]; exact ha)
    have h2 := sum_take_mono L (show a + 1 ≤ b by omega)
    rw [e, e]
    omega
  rcases Nat.lt_trichotomy m m' with hlt | rfl | hgt
  · exact absurd h (Nat.ne_of_lt (key hm hm' hi hlt))
  · exact ⟨rfl, by omega⟩
  · exact absurd h.symm (Nat.ne_of_lt (key hm' hm hi' hgt))

theorem choiceAtom_rho {D : Doc} (S : VE.Structure.{u}) (s : String) (i : Nat) (ρ : VE.Valuation S) :
    (choiceAtom D s i).denote S ρ ↔ (choiceAtom D s i).denote S [] := by
  unfold choiceAtom
  split
  · split
    · exact pattern_rho S _ _ _ ρ
    · exact Iff.rfl
  · exact Iff.rfl

/-! ## The origin of a name -/

theorem origin_qualify {D : Doc} {m i : Nat} (hm : m < D.sets.length) (hi : i < D.sets[m].candidates.length)
    {a : Candidate} (ha : D.sets[m].candidates[i]? = some a) {c : Content} (hac : a.content = some c)
    {d : String × String} (hd : d ∈ c.declared) :
    origin D (qualify (position D m i) d.2) = some (m, i) := by
  unfold origin
  have hsz : ∀ m' (hm' : m' < D.sets.length), setSize D m' = D.sets[m'].candidates.length := fun m' hm' =>
    setSize_eq hm'
  have hpred : ∀ m' (hm' : m' < D.sets.length) i', i' < D.sets[m'].candidates.length →
      ((((D.sets[m']?).bind (·.candidates[i']?)).bind (·.content)).any
        (fun c => c.declared.any (fun d' => qualify (position D m' i') d'.2 == qualify (position D m i) d.2))) = true →
      m' = m ∧ i' = i := by
    intro m' hm' i' hi' h
    simp only [Option.any_eq_true, List.any_eq_true, beq_iff_eq] at h
    obtain ⟨_, _, _, _, he⟩ := h
    exact position_inj hm' hm hi' hi (qualify_inj he).1
  apply findSome_unique (a := m) (List.mem_range.mpr hm)
  · have : (List.range (setSize D m)).find? (fun i' =>
        ((((D.sets[m]?).bind (·.candidates[i']?)).bind (·.content)).any
          (fun c => c.declared.any (fun d' => qualify (position D m i') d'.2 == qualify (position D m i) d.2))))
        = some i := by
      apply find_unique (List.mem_range.mpr (by rw [hsz m hm]; exact hi))
      · simp only [List.getElem?_eq_getElem hm, Option.bind_some, ha, hac, Option.any_some, List.any_eq_true,
          beq_iff_eq]
        exact ⟨d, hd, rfl⟩
      · intro x hx h
        exact (hpred m hm x (by rw [← hsz m hm]; exact List.mem_range.mp hx) h).2
    rw [this]; rfl
  · intro x hx y hy
    simp only [Option.map_eq_some_iff] at hy
    obtain ⟨i', hf, _⟩ := hy
    have hxl := List.mem_range.mp hx
    have hi' := List.mem_range.mp (List.mem_of_find?_eq_some hf)
    have h3 := List.find?_some hf
    exact (hpred x hxl i' (by rw [← hsz x hxl]; exact hi') h3).1

theorem origin_unreserved {D : Doc} {n : String} (hn : reservedName n = false) : origin D n = none := by
  unfold origin
  apply List.findSome?_eq_none_iff.mpr
  intro m _
  simp only [Option.map_eq_none_iff]
  apply List.find?_eq_none.mpr
  intro i _ h
  simp only [Option.any_eq_true, List.any_eq_true, beq_iff_eq] at h
  obtain ⟨_, _, _, _, he⟩ := h
  rw [← he, reservedName_qualify] at hn
  cases hn

/-! ## The lifted base -/

/-- The index `c` takes in the `m`-th set. -/
def chosenIdx (D : Doc) (c : Choice) (m : Nat) : Nat := (c.index ((D.sets[m]?.map (·.id)).getD "")).getD 0

def IsBit (D : Doc) (p : String) : Prop :=
  ∃ m j, m < D.sets.length ∧ j < bitsOf (setSize D m) ∧ p = bitName (m + 1) j

def OnBit (D : Doc) (c : Choice) (p : String) : Prop :=
  ∃ m j, m < D.sets.length ∧ j < bitsOf (setSize D m) ∧ p = bitName (m + 1) j ∧ (chosenIdx D c m).testBit j = true

theorem onBit_isBit {D : Doc} {c : Choice} {p : String} (h : OnBit D c p) : IsBit D p :=
  let ⟨m, j, hm, hj, he, _⟩ := h
  ⟨m, j, hm, hj, he⟩

def upRel (D : Doc) (c : Choice) (B₀ : VE.Structure.{u}) (e : B₀.Carrier) : String → List B₀.Carrier → Prop :=
  fun p vs => (OnBit D c p ∧ vs = [e]) ∨
    (¬ IsBit D p ∧ p ∈ decisionNames (sup D).1.soft ∧
      ∃ q ∈ decisionNames (choiceDoc D c).1.soft, nameMap D c q = p ∧ B₀.relation q vs) ∨
    (¬ IsBit D p ∧ p ∉ decisionNames (sup D).1.soft ∧ p ∉ decisionNames (choiceDoc D c).1.soft ∧ B₀.relation p vs)

def upDom (B₀ : VE.Structure.{u}) : String → B₀.Carrier → Prop :=
  fun σ => if σ = "ve__reading" then fun _ => True else B₀.domain σ

def upConst (B₀ : VE.Structure.{u}) (e : B₀.Carrier) : String → Option B₀.Carrier :=
  fun x => if x = "ve__here" then some e else B₀.constant x

def upB (D : Doc) (c : Choice) (B₀ : VE.Structure.{u}) (e : B₀.Carrier) : VE.Structure.{u} :=
  { B₀ with relation := upRel D c B₀ e, domain := upDom B₀, constant := upConst B₀ e }

theorem chosen_spec {D : Doc} (hr : supReady D = true) {c : Choice} (hc : Compatible D c) :
    ∀ m (hm : m < D.sets.length), c.index D.sets[m].id = some (chosenIdx D c m) ∧ chosenIdx D c m < setSize D m := by
  have hn := supReady_nodup hr
  have hcm : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hmap := complete_map hcm
  have hcn : (c.map (·.1)).Nodup := hmap ▸ hn
  have hlen : c.length = D.sets.length := by simpa using congrArg List.length hmap
  intro m hm
  have hcm' : m < c.length := hlen ▸ hm
  have hfst : c[m].1 = D.sets[m].id := by
    have := congrArg (·[m]?) hmap
    simpa [List.getElem?_eq_getElem hcm', List.getElem?_eq_getElem hm] using this
  have hidx := index_of_mem hcn (List.getElem_mem hcm')
  rw [hfst] at hidx
  have hch : chosenIdx D c m = c[m].2 := by simp [chosenIdx, List.getElem?_eq_getElem hm, hidx]
  refine ⟨by rw [hidx, hch], ?_⟩
  obtain ⟨m', hf, hi⟩ := candidate_isSome (complete_mem hcm (List.getElem_mem hcm'))
  rw [hfst, findIdx_of_nodup hn hm] at hf
  cases hf
  rw [hch]; exact hi

theorem bitOn_upB {D : Doc} {c : Choice} {B₀ : VE.Structure.{u}} {e : B₀.Carrier} {m j : Nat}
    (hm : m < D.sets.length) (hj : j < bitsOf (setSize D m)) :
    bitOn (upB D c B₀ e) (m + 1) j ↔ (chosenIdx D c m).testBit j = true := by
  have hbit : IsBit D (bitName (m + 1) j) := ⟨m, j, hm, hj, rfl⟩
  show (∃ v, upConst B₀ e "ve__here" = some v ∧ upRel D c B₀ e (bitName (m + 1) j) [v]) ↔ _
  simp only [upConst, if_true]
  constructor
  · rintro ⟨v, hv, h⟩
    cases hv
    rcases h with ⟨⟨m', j', _, _, he, hb⟩, _⟩ | ⟨hn, _⟩ | ⟨hn, _⟩
    · obtain ⟨h1, h2⟩ := bitName_inj he
      have : m = m' := by omega
      subst this; subst h2; exact hb
    · exact absurd hbit hn
    · exact absurd hbit hn
  · intro hb
    exact ⟨e, rfl, Or.inl ⟨⟨m, j, hm, hj, rfl, hb⟩, rfl⟩⟩

theorem upB_encodes {D : Doc} (hr : supReady D = true) {c : Choice} (hc : Compatible D c)
    (B₀ : VE.Structure.{u}) (e : B₀.Carrier) : Encodes D c (upB D c B₀ e) := by
  have hn := supReady_nodup hr
  have hcm : complete D c = true := by
    simp only [Compatible, compatible, Bool.and_eq_true] at hc; exact hc.1.1
  have hcn : (c.map (·.1)).Nodup := (complete_map hcm) ▸ hn
  have hchosen := chosen_spec hr hc
  have hpat : ∀ m (hm : m < D.sets.length) i, i < 2 ^ bitsOf (setSize D m) →
      ((pattern (m + 1) (setSize D m) i).denote (upB D c B₀ e) [] ↔ i = chosenIdx D c m) := by
    intro m hm i hi
    have hk := le_two_pow_bitsOf (setSize D m)
    have hcl := (hchosen m hm).2
    rw [pattern_denote]
    constructor
    · intro h
      apply eq_of_low_bits hi (by omega)
      intro j hj
      have := (bitOn_upB hm hj).symm.trans (h j hj)
      cases h1 : i.testBit j <;> cases h2 : (chosenIdx D c m).testBit j <;> simp_all
    · rintro rfl j hj
      exact bitOn_upB hm hj
  intro R hR i hi
  obtain ⟨m, hm, rfl⟩ := mem_sets_getElem hR
  have hilt : i < setSize D m := by rw [setSize_eq hm]; exact hi
  rw [choiceAtom_eq (findIdx_of_nodup hn hm) hilt,
    hpat m hm i (by have := le_two_pow_bitsOf (setSize D m); omega)]
  constructor
  · rintro rfl; exact mem_of_index (hchosen m hm).1
  · intro hx
    have := index_of_mem hcn hx
    simp only at this
    rw [(hchosen m hm).1] at this
    cases this; rfl

section Pull
variable {D : Doc} (hh : Hyps D)
include hh

theorem sup_ruleName {P : SoftNode} (hP : P ∈ (sup D).1.soft.T.nodes) : VE.Norms.ruleName P.name = true := by
  have hv := sup_softValid hh
  obtain ⟨hck, _⟩ := (VE.NormDefaults.wellFormed_iff _).mp hv.wf
  obtain ⟨_, _, _, _, _, _, ⟨hrules, _, _⟩, _, _⟩ := hck
  exact (hrules _ (List.mem_map.mpr ⟨P, hP, rfl⟩)).1

theorem nameMap_decision (c : Choice) {p : String} (hp : p ∈ decisionNames (choiceDoc D c).1.soft) :
    nameMap D c p ∈ decisionNames (sup D).1.soft := by
  obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hp
  rcases mem_decisions.mp hx with ⟨N, hN, hd, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, ht, rfl⟩
  · obtain ⟨_, _, hmode, _, _, _⟩ := fmap_fields hh c hN
    show nameMap D c (exceptedName N) ∈ _
    rw [nameMap_excepted hh c hN hd]
    exact List.mem_map.mpr ⟨_, mem_decisions.mpr (Or.inl ⟨_, fmap_mem hh c hN, by rw [hmode]; exact hd, rfl⟩), rfl⟩
  · obtain ⟨_, _, _, _, halt, _⟩ := fmap_fields hh c hN
    show nameMap D c (offName N π) ∈ _
    rw [nameMap_off hh c hN hπ]
    exact List.mem_map.mpr ⟨_, mem_decisions.mpr (Or.inr (Or.inl ⟨_, fmap_mem hh c hN, π, by rw [halt]; exact hπ,
      rfl⟩)), rfl⟩
  · show nameMap D c (outweighsName a L H) ∈ _
    rw [nameMap_outweighs hh c]
    exact List.mem_map.mpr ⟨_, mem_decisions.mpr (Or.inr (Or.inr ⟨a, L, H, triple_sup hh c ht, rfl⟩)), rfl⟩

theorem nameMap_nondecision (c : Choice) {p : String} (hp : p ∉ decisionNames (choiceDoc D c).1.soft) :
    nameMap D c p = p := by
  unfold nameMap
  cases hf : (genKeys (choiceDoc D c).1).find? (·.2.1 == p) with
  | none => rfl
  | some g =>
    exfalso
    have hg := genKeys_decision (choiceDoc_noRights D c hh.noRights) (List.mem_of_find?_eq_some hf)
    rw [choice_correlate hh c] at hg
    have hn : g.2.1 = p := by simpa using List.find?_some hf
    exact hp (List.mem_map.mpr ⟨_, hg, hn⟩)

theorem nameMap_inj (c : Choice) {p q : String} (hp : p ∈ decisionNames (choiceDoc D c).1.soft)
    (hq : q ∈ decisionNames (choiceDoc D c).1.soft) (he : nameMap D c p = nameMap D c q) : p = q := by
  obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hp
  obtain ⟨y, hy, rfl⟩ := List.mem_map.mp hq
  have img : ∀ {N N' : SoftNode}, N ∈ (choiceDoc D c).1.soft.T.nodes → N' ∈ (choiceDoc D c).1.soft.T.nodes →
      (fmap D c N).name = (fmap D c N').name → N = N' := fun hN hN' h =>
    fmap_inj hh c hN hN' (sup_name_inj hh (fmap_mem hh c hN) (fmap_mem hh c hN') h)
  have rn : ∀ {N : SoftNode}, N ∈ (choiceDoc D c).1.soft.T.nodes → VE.Norms.ruleName (fmap D c N).name = true :=
    fun hN => sup_ruleName hh (fmap_mem hh c hN)
  rcases mem_decisions.mp hx with ⟨N, hN, hd, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, _, rfl⟩ <;>
  rcases mem_decisions.mp hy with ⟨N', hN', hd', rfl⟩ | ⟨N', hN', π', hπ', rfl⟩ | ⟨a', L', H', _, rfl⟩ <;>
  simp only [] at he ⊢
  · rw [nameMap_excepted hh c hN hd, nameMap_excepted hh c hN' hd'] at he
    rw [img hN hN' (exceptedName_inj (rn hN) (rn hN') he)]
  · rw [nameMap_excepted hh c hN hd, nameMap_off hh c hN' hπ'] at he
    exact absurd he (exceptedName_ne_offName _ _ _)
  · rw [nameMap_excepted hh c hN hd, nameMap_outweighs hh c] at he
    exact absurd he (exceptedName_ne_outweighsName _ _ _ _)
  · rw [nameMap_off hh c hN hπ, nameMap_excepted hh c hN' hd'] at he
    exact absurd he.symm (exceptedName_ne_offName _ _ _)
  · rw [nameMap_off hh c hN hπ, nameMap_off hh c hN' hπ'] at he
    have v1 := (choice_nodeFacts hh c hN).2.2.2.2 π hπ
    have v2 := (choice_nodeFacts hh c hN').2.2.2.2 π' hπ'
    obtain ⟨h1, h2⟩ := offName_inj (rn hN) (rn hN') v1 v2 he
    rw [img hN hN' h1, h2]
  · rw [nameMap_off hh c hN hπ, nameMap_outweighs hh c] at he
    exact absurd he (offName_ne_outweighsName _ _ _ _ _)
  · rw [nameMap_outweighs hh c, nameMap_excepted hh c hN' hd'] at he
    exact absurd he.symm (exceptedName_ne_outweighsName _ _ _ _)
  · rw [nameMap_outweighs hh c, nameMap_off hh c hN' hπ'] at he
    exact absurd he.symm (offName_ne_outweighsName _ _ _ _ _)
  · rw [nameMap_outweighs hh c, nameMap_outweighs hh c] at he
    exact he

omit hh in
theorem decision_not_bit {X : SoftDoc} {p : String} (hp : p ∈ decisionNames X) : ¬ IsBit D p := by
  rintro ⟨m, j, _, _, rfl⟩
  exact bitName_not_decision _ _ hp

theorem frame_not_isBit {p : String} (hp : D.frame.soft.E.predicates p ≠ none) : ¬ IsBit D p := by
  rintro ⟨m, j, hm, hj, rfl⟩
  have hf := frame_not_bit hh hp
  have hmem : (bitName (m + 1) j, ["ve__reading"]) ∈ bitDecls D := by
    simp only [bitDecls, List.mem_flatMap, List.mem_range, List.mem_map]
    exact ⟨m, hm, j, hj, rfl⟩
  exact absurd (List.find?_eq_none.mp hf _ hmem) (by simp)

theorem frame_not_supDecision {p : String} (hp : D.frame.soft.E.predicates p ≠ none) :
    p ∉ decisionNames (sup D).1.soft := fun hd => by
  have := (sup_softValid hh).decFresh p hd
  rw [sup_E_frame hh hp] at this; exact hp this

/-- Pulled back, the lifted base is the base it was lifted from. -/
theorem pull_upB (c : Choice) (B₀ : VE.Structure.{u}) (e : B₀.Carrier)
    (hadm : B₀.Admissible (envAt (soften (choiceDoc D c).1.soft) 0)) (p : String) (vs : List B₀.Carrier) :
    (pull D c (upB D c B₀ e)).relation p vs ↔ B₀.relation p vs := by
  show ((choiceEnvFull D c).predicates p ≠ none ∧ upRel D c B₀ e (nameMap D c p) vs) ↔ _
  by_cases hpd : p ∈ decisionNames (choiceDoc D c).1.soft
  · have h1 := nameMap_decision hh c hpd
    have h2 : ¬ IsBit D (nameMap D c p) := decision_not_bit h1
    constructor
    · rintro ⟨_, h | h | h⟩
      · exact absurd (onBit_isBit h.1) h2
      · obtain ⟨_, _, q, hq, he, hb⟩ := h
        rw [nameMap_inj hh c hpd hq he.symm]; exact hb
      · exact absurd h1 h.2.1
    · intro hb
      exact ⟨choiceEnvFull_decision hh c hpd, Or.inr (Or.inl ⟨h2, h1, p, hpd, rfl, hb⟩)⟩
  · rw [nameMap_nondecision hh c hpd]
    by_cases hfull : (choiceEnvFull D c).predicates p = none
    · constructor
      · rintro ⟨h, _⟩; exact absurd hfull h
      · intro hb
        obtain ⟨ss, hss, _⟩ := hadm.2 p vs hb
        have : (envPrime (choiceDoc D c).1.soft).predicates p = some ss := envAt_sub hss
        rw [← choiceEnvFull_eq hh c, hfull] at this
        cases this
    · have hfr : D.frame.soft.E.predicates p ≠ none := by
        rw [choiceEnvFull_eq hh c, envPrime_not_decision hpd, choice_E c] at hfull; exact hfull
      have hnb := frame_not_isBit hh hfr
      have hnd := frame_not_supDecision hh hfr
      constructor
      · rintro ⟨_, h | h | h⟩
        · exact absurd (onBit_isBit h.1) hnb
        · exact absurd h.2.1 hnd
        · exact h.2.2.2
      · intro hb
        exact ⟨hfull, Or.inr (Or.inr ⟨hnb, hnd, hpd, hb⟩)⟩

end Pull

/-! ## The lifted base agrees with `B₀` off the choice vocabulary -/

theorem here_reserved : reservedSym "ve__here" = true := by
  have : ("ve__here" : String) = "ve__" ++ "here" := by decide
  unfold reservedSym; rw [this]; exact startsWith_append_ascii _ _ (by decide)

theorem tt_up {B₀ : VE.Structure.{u}} {D : Doc} {c : Choice} {e : B₀.Carrier} :
    ∀ {ss : List String} {vs : List B₀.Carrier}, VE.TupleTyped B₀ ss vs → VE.TupleTyped (upB D c B₀ e) ss vs
  | [], [], _ => trivial
  | s :: _, v :: _, h => ⟨by
      show upDom B₀ s v
      unfold upDom
      split
      · trivial
      · exact h.1, tt_up h.2⟩
  | [], _ :: _, h => h.elim
  | _ :: _, [], h => h.elim

theorem tt_down {B₀ : VE.Structure.{u}} {D : Doc} {c : Choice} {e : B₀.Carrier} :
    ∀ {ss : List String} {vs : List B₀.Carrier}, (∀ s ∈ ss, s ≠ "ve__reading") →
      VE.TupleTyped (upB D c B₀ e) ss vs → VE.TupleTyped B₀ ss vs
  | [], [], _, _ => trivial
  | s :: _, v :: _, hs, h => ⟨by
      have h1 : upDom B₀ s v := h.1
      unfold upDom at h1
      rw [if_neg (hs s List.mem_cons_self)] at h1
      exact h1, tt_down (fun s' hs' => hs s' (List.mem_cons_of_mem _ hs')) h.2⟩
  | [], _ :: _, _, h => h.elim
  | _ :: _, [], _, h => h.elim

section Up
variable {D : Doc} (hh : Hyps D) {c : Choice} (hc : Compatible D c) (B₀ : VE.Structure.{u}) (e : B₀.Carrier)
include hh

omit hc in
theorem frame_here : D.frame.soft.E.constants "ve__here" = none := by
  have := (sharedEnv_noChoice hh.wf hh.ready).2.1; rwa [sharedEnv_constants] at this

omit hc B₀ e in
theorem lit_not_here {a : String} (ha : a ∈ D.frame.soft.lits) : a ≠ "ve__here" := by
  rintro rfl
  have hr := (wellFormedDoc_parts hh.wf).1
  simp only [reservedFree, Bool.and_eq_true, Bool.not_eq_true', List.any_eq_false] at hr
  have := hr.1.1 "ve__here" (by simp [ha])
  rw [here_reserved] at this
  exact this rfl

omit hc in
theorem frame_rel {p : String} {ss : List String} (hp : D.frame.soft.E.predicates p = some ss)
    (vs : List B₀.Carrier) : upRel D c B₀ e p vs ↔ B₀.relation p vs := by
  have hfr : D.frame.soft.E.predicates p ≠ none := by rw [hp]; simp
  have hnb := frame_not_isBit hh hfr
  have hnd := frame_not_supDecision hh hfr
  have hny : p ∉ decisionNames (choiceDoc D c).1.soft := fun h => by
    obtain ⟨x, hx, rfl⟩ := List.mem_map.mp h
    rw [choice_decision_fresh hh c hx] at hp; cases hp
  constructor
  · rintro (h | h | h)
    · exact absurd (onBit_isBit h.1) hnb
    · exact absurd h.2.1 hnd
    · exact h.2.2.2
  · intro hb; exact Or.inr (Or.inr ⟨hnb, hnd, hny, hb⟩)

omit hc in
/-- A formula over the frame's vocabulary reads the lifted base as it reads `B₀`. -/
theorem up_frame (φ : VE.Formula) (Γ : List String) (hφ : φ.WellFormed D.frame.soft.E Γ) (ρ : VE.Valuation B₀) :
    φ.denote (upB D c B₀ e) ρ ↔ φ.denote B₀ ρ :=
  ext_denote (frame_sorts_free hh.wf) (frame_here hh) (upRel D c B₀ e) (upDom B₀) (upConst B₀ e)
    (fun _ _ hp vs => frame_rel hh B₀ e hp vs) (fun σ hσ => by show (if σ = "ve__reading" then _ else _) = _; exact if_neg hσ)
    (fun x hx => by show (if x = "ve__here" then _ else _) = _; exact if_neg hx) φ Γ ρ hφ

omit hc in
/-- A formula over the choice's complete vocabulary reads the pulled lifted base as it reads `B₀`. -/
theorem pull_up (hadm : B₀.Admissible (envAt (soften (choiceDoc D c).1.soft) 0)) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (envPrime (choiceDoc D c).1.soft) Γ) (ρ : VE.Valuation B₀) :
    φ.denote (pull D c (upB D c B₀ e)) ρ ↔ φ.denote B₀ ρ :=
  ext_denote (E := envPrime (choiceDoc D c).1.soft) (S := B₀)
    (by rw [envPrime_sorts, choice_E c]; exact frame_sorts_free hh.wf)
    (by rw [envPrime_constants, choice_E c]; exact frame_here hh)
    (pull D c (upB D c B₀ e)).relation (upDom B₀) (upConst B₀ e)
    (fun p _ _ vs => pull_upB hh c B₀ e hadm p vs)
    (fun σ hσ => by show (if σ = "ve__reading" then _ else _) = _; exact if_neg hσ)
    (fun x hx => by show (if x = "ve__here" then _ else _) = _; exact if_neg hx) φ Γ ρ hφ

include hc in
omit B₀ e in
theorem sortsY_free (p : String) : ∀ s ∈ VE.SoftNorms.sortsOf (choiceDoc D c).1.soft p, s ≠ "ve__reading" := by
  intro s hs
  unfold VE.SoftNorms.sortsOf VE.SoftNorms.sortsIn at hs
  cases hf : (choiceDoc D c).1.soft.T.regulated.find? (·.name == p) with
  | none => rw [hf] at hs; simp at hs
  | some r =>
    rw [hf] at hs
    simp only [Option.map_some, Option.getD_some] at hs
    have hr := List.mem_of_find?_eq_some hf
    have hsym := (choice_valid hh hc).regulated r hr
    have h1 := (choice_decl hh hsym).2.2 s hs
    rw [envPrime_sorts, choice_E c] at h1
    rintro rfl
    exact frame_sorts_free hh.wf h1

include hc in
theorem upB_admissible (hadm : B₀.Admissible (envAt (soften (choiceDoc D c).1.soft) 0)) :
    (upB D c B₀ e).Admissible (envAt (soften (sup D).1.soft) 0) := by
  refine ⟨fun x s hx => ?_, fun p vs hrel => ?_⟩
  · have frame_case : D.frame.soft.E.constants x = some s → ∃ v, upConst B₀ e x = some v ∧ upDom B₀ s v := by
      intro hfx
      have hx' : x ≠ "ve__here" := by rintro rfl; rw [frame_here hh] at hfx; cases hfx
      obtain ⟨v, hv, hd⟩ := hadm.1 x s (by
        show (choiceDoc D c).1.soft.E.constants x = some s
        rw [choice_E c]; exact hfx)
      refine ⟨v, by show (if x = "ve__here" then _ else _) = _; rw [if_neg hx']; exact hv, ?_⟩
      show (if s = "ve__reading" then fun _ => True else B₀.domain s) v
      split
      · trivial
      · exact hd
    have hx2 : (choiceEnv D D.frame.soft.E).constants x = some s := by
      have : (sup D).1.soft.E.constants x = some s := hx
      rwa [sup_E] at this
    unfold choiceEnv at hx2
    split at hx2
    · exact frame_case hx2
    · by_cases hxh : x = "ve__here"
      · subst hxh
        simp only [beq_self_eq_true, if_true] at hx2
        cases hx2
        refine ⟨e, ?_, ?_⟩
        · show (if ("ve__here" : String) = "ve__here" then some e else B₀.constant "ve__here") = some e
          simp
        · show (if ("ve__reading" : String) = "ve__reading" then (fun _ => True) else B₀.domain "ve__reading") e
          simp
      · have : (x == "ve__here") = false := by simpa using hxh
        simp only [this] at hx2
        exact frame_case hx2
  · rcases hrel with ⟨⟨m, j, hm, hj, rfl, _⟩, rfl⟩ | ⟨_, hpX, q, hq, rfl, hb⟩ | ⟨_, hnX, hnY, hb⟩
    · refine ⟨["ve__reading"], sup_bit hh hm hj 0, ?_, trivial⟩
      show (if "ve__reading" = "ve__reading" then fun _ => True else B₀.domain "ve__reading") e
      simp
    · obtain ⟨ss, hss, htt⟩ := hadm.2 q vs hb
      have h1 : (envPrime (choiceDoc D c).1.soft).predicates q = some ss := envAt_sub hss
      have h2 := envPrime_nameMap hh c h1
      refine ⟨ss, ?_, tt_up htt⟩
      rw [VE.Norms.envAt_base (fun hl => layer_not_decision (sup_wfSoft hh) hl hpX)]
      exact h2
    · obtain ⟨ss, hss, htt⟩ := hadm.2 p vs hb
      have hnl : p ∉ VE.Norms.layerNames (soften (choiceDoc D c).1.soft).T := by
        intro hl
        simp [envAt, VE.Norms.hide, hl] at hss
      rw [VE.Norms.envAt_base hnl, soften_E, envPrime_not_decision hnY, choice_E c] at hss
      refine ⟨ss, ?_, tt_up htt⟩
      rw [VE.Norms.envAt_base (fun hl => hnl ((layer_iff hh hc p).mpr hl)), soften_E,
        envPrime_sup_frame hh (by rw [hss]; simp)]
      exact hss

omit hc in
theorem upB_literals (hl : Sat B₀ (VE.Norms.backgroundBase (soften (choiceDoc D c).1.soft))) :
    Sat (upB D c B₀ e) (VE.Norms.backgroundBase (soften (sup D).1.soft)) := by
  have hY : (soften (choiceDoc D c).1.soft).lits = D.frame.soft.lits := by
    show (build D (fun _ => true) (pickC c)).1.soft.lits = _
    rw [(build_shape D (fun _ => true) (pickC c)).lits]
  have hX : (soften (sup D).1.soft).lits = D.frame.soft.lits := (sup_shape D).lits
  intro a ha
  unfold VE.Norms.backgroundBase VE.Route.Background.literals at ha
  rw [hX] at ha
  obtain ⟨⟨x, y⟩, hxy, rfl⟩ := List.mem_map.mp ha
  have hmem : VE.Route.Background.literalPremise (x, y) ∈ VE.Norms.backgroundBase (soften (choiceDoc D c).1.soft) := by
    unfold VE.Norms.backgroundBase VE.Route.Background.literals
    rw [hY]; exact List.mem_map_of_mem hxy
  have h0 := (VE.Route.Background.literalPremise_denote B₀ (x, y)).mp (hl _ hmem)
  obtain ⟨hx, hy, _⟩ := VE.Route.Background.mem_pairs hxy
  rw [VE.Route.Background.mem_sortStrings] at hx hy
  apply (VE.Route.Background.literalPremise_denote _ (x, y)).mpr
  intro v hv
  have hx' : upConst B₀ e x = B₀.constant x := if_neg (lit_not_here hh hx)
  have hy' : upConst B₀ e y = B₀.constant y := if_neg (lit_not_here hh hy)
  show upConst B₀ e y ≠ some v
  rw [hy']
  exact h0 v (by rw [← hx']; exact hv)

end Up

end VE.Readings
