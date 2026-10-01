import VE.Discourse.Fusion
import VE.Route.Readings

/-! # Correlated readings and the joint set (docs/spec/discourse.md 4.8, 9.4)

The active open reading sets `R₁ … Rₙ` give choice vectors `c` (one reading index per
set, positionally); `Compatible K sets c` holds when `c` satisfies every declared
`requires`/`excludes` constraint and nothing else. `compatibleChoices` enumerates the
product filtered by exactly these constraints, under a limit on the product size: beyond
it the result is `ResourceLimit: joint choices` (validation not completed, UNKNOWN),
and only a completed empty enumeration is `InvalidCompatibility`. The joint disjunction
`Joint(K)` is the disjunction of the conjunctions of the chosen readings; the empty
conjunction is `top`, so zero open sets give the one empty choice whose conjunction is
`top`. The composition gate (`ExtendsTo`) requires each W3 choice list to extend to a
validated compatible choice. -/
namespace VE.Discourse
open VE.Route.Admission (ReadingSet disjunction)
universe u

abbrev Choice := List (String × Nat × Nat)

def chosen (c : Choice) (x : String × Nat × Nat) : Prop := x ∈ c

def Satisfies (c : Choice) : Constraint → Prop
  | ⟨.requires, a, b⟩ => chosen c a → chosen c b
  | ⟨.excludes, a, b⟩ => ¬ (chosen c a ∧ chosen c b)

instance (c : Choice) (k : Constraint) : Decidable (Satisfies c k) := by
  rcases k with ⟨kind, a, b⟩
  cases kind <;> unfold Satisfies chosen <;> infer_instance

def Compatible (K : Manifest) (sets : List ReadingSet) (c : Choice) : Prop :=
  c.length = sets.length ∧
  (∀ i (h : i < sets.length), ∃ r, c[i]? = some (sets[i].id, sets[i].version, r) ∧
    r < sets[i].readings.length) ∧
  ∀ k ∈ K.constraints, Satisfies c k

def productSize (sets : List ReadingSet) : Nat := sets.foldl (fun n rs => n * rs.readings.length) 1

/-- Every choice vector of the product, in order. -/
def allChoices : List ReadingSet → List Choice
  | [] => [[]]
  | rs :: rest => (List.range rs.readings.length).flatMap fun r =>
      (allChoices rest).map ((rs.id, rs.version, r) :: ·)

def satisfiesAll (K : Manifest) (c : Choice) : Bool := K.constraints.all fun k => decide (Satisfies c k)

def setsText (sets : List ReadingSet) : String := ", ".intercalate (sets.map ReadingSet.id)

def compatibleChoices (K : Manifest) (sets : List ReadingSet) (limit : Nat) : Except String (List Choice) :=
  if productSize sets > limit then .error "ResourceLimit: joint choices"
  else
    let cs := (allChoices sets).filter (satisfiesAll K)
    if cs.isEmpty then .error ("InvalidCompatibility: " ++ setsText sets) else .ok cs

/-- The chosen readings of a choice vector. -/
def readingsOf (sets : List ReadingSet) (c : Choice) : List VE.Formula :=
  (sets.zip c).filterMap fun (rs, _, _, r) => rs.readings[r]?

def conj : List VE.Formula → VE.Formula
  | [] => .top
  | [a] => a
  | a :: as => .and a (conj as)

def disj : List VE.Formula → VE.Formula
  | [] => .bottom
  | [a] => a
  | a :: as => .or a (disj as)

def joint (sets : List ReadingSet) (cs : List Choice) : Option VE.Formula :=
  match cs with
  | [] => none
  | _ => some (disj (cs.map fun c => conj (readingsOf sets c)))

def occurring (sets : List ReadingSet) (cs : List Choice) : List VE.Formula := cs.flatMap (readingsOf sets)

/-- 4.8, the composition gate: a W3 choice list (set ↦ "v:i" | "v:all") extends to a
compatible choice. -/
def ExtendsTo (ch : List (String × String)) (c : Choice) : Prop :=
  ∀ e ∈ ch, ∃ v i, (e.1, v, i) ∈ c ∧ (e.2 = toString v ++ ":" ++ toString i ∨ e.2 = toString v ++ ":all")

def extendsTo (ch : List (String × String)) (c : Choice) : Bool :=
  ch.all fun e => c.any fun x => x.1 == e.1 &&
    (e.2 == toString x.2.1 ++ ":" ++ toString x.2.2 || e.2 == toString x.2.1 ++ ":all")

theorem extendsTo_iff (ch : List (String × String)) (c : Choice) : extendsTo ch c = true ↔ ExtendsTo ch c := by
  simp only [extendsTo, ExtendsTo, List.all_eq_true, List.any_eq_true, Bool.and_eq_true,
    Bool.or_eq_true, beq_iff_eq]
  constructor
  · intro h e he
    obtain ⟨x, hx, h1, h2⟩ := h e he
    exact ⟨x.2.1, x.2.2, by rw [← h1]; exact hx, h2⟩
  · intro h e he
    obtain ⟨v, i, hm, h2⟩ := h e he
    exact ⟨(e.1, v, i), hm, rfl, h2⟩

/-! ## The enumeration -/

theorem mem_allChoices : ∀ (sets : List ReadingSet) (c : Choice),
    c ∈ allChoices sets ↔ c.length = sets.length ∧
      ∀ i (h : i < sets.length), ∃ r, c[i]? = some (sets[i].id, sets[i].version, r) ∧
        r < sets[i].readings.length
  | [], c => by
    simp only [allChoices, List.mem_singleton, List.length_nil, List.length_eq_zero_iff]
    constructor
    · rintro rfl; exact ⟨rfl, fun i h => absurd h (Nat.not_lt_zero _)⟩
    · exact fun h => h.1
  | rs :: rest, c => by
    simp only [allChoices, List.mem_flatMap, List.mem_range, List.mem_map]
    constructor
    · rintro ⟨r, hr, c', hc', rfl⟩
      obtain ⟨hl, hi⟩ := (mem_allChoices rest c').mp hc'
      refine ⟨by simp [hl], fun i h => ?_⟩
      cases i with
      | zero => exact ⟨r, rfl, hr⟩
      | succ i =>
        obtain ⟨r', h1, h2⟩ := hi i (by simpa using h)
        exact ⟨r', by simpa using h1, by simpa using h2⟩
    · rintro ⟨hl, hi⟩
      cases c with
      | nil => simp at hl
      | cons x c' =>
        obtain ⟨r, h1, h2⟩ := hi 0 (by simp)
        simp only [List.getElem?_cons_zero, Option.some.injEq, List.getElem_cons_zero] at h1 h2
        subst h1
        refine ⟨r, h2, c', (mem_allChoices rest c').mpr ⟨by simpa using hl, fun i h => ?_⟩, rfl⟩
        obtain ⟨r', h1', h2'⟩ := hi (i + 1) (by simpa using h)
        exact ⟨r', by simpa using h1', by simpa using h2'⟩

theorem foldl_mul (f : ReadingSet → Nat) : ∀ (l : List ReadingSet) (a : Nat),
    l.foldl (fun n rs => n * f rs) a = a * l.foldl (fun n rs => n * f rs) 1
  | [], a => by simp
  | x :: xs, a => by
    simp only [List.foldl_cons]
    rw [foldl_mul f xs (a * f x), foldl_mul f xs (1 * f x)]
    simp [Nat.mul_assoc]

theorem length_flatMap_range {α : Type} (f : Nat → List α) (k : Nat) (hf : ∀ r, (f r).length = k) :
    ∀ n, ((List.range n).flatMap f).length = n * k
  | 0 => by simp
  | n + 1 => by
    rw [List.range_succ, List.flatMap_append, List.length_append, length_flatMap_range f k hf n]
    simp [hf, Nat.succ_mul]

theorem length_allChoices : ∀ sets : List ReadingSet, (allChoices sets).length = productSize sets
  | [] => rfl
  | rs :: rest => by
    have h1 : productSize (rs :: rest) = rs.readings.length * productSize rest := by
      simp only [productSize, List.foldl_cons]
      rw [foldl_mul (fun rs => rs.readings.length) rest (1 * rs.readings.length)]
      simp
    rw [h1, ← length_allChoices rest]
    exact length_flatMap_range _ _ (fun r => by simp) _

theorem satisfiesAll_iff (K : Manifest) (c : Choice) :
    satisfiesAll K c = true ↔ ∀ k ∈ K.constraints, Satisfies c k := by
  simp [satisfiesAll, List.all_eq_true]

/-- The enumeration is exactly the compatibility relation, and never empty on success. -/
theorem compatible_sound (K : Manifest) (sets : List ReadingSet) (n : Nat) (cs : List Choice)
    (h : compatibleChoices K sets n = .ok cs) : (∀ c, c ∈ cs ↔ Compatible K sets c) ∧ cs ≠ [] ∧ cs.length ≤ n := by
  unfold compatibleChoices at h
  split at h
  · cases h
  · rename_i hle
    dsimp only at h
    split at h
    · cases h
    · rename_i hne
      cases h
      refine ⟨fun c => ?_, fun he => hne (by simp [he]), ?_⟩
      · rw [List.mem_filter, mem_allChoices, satisfiesAll_iff]
        simp only [Compatible, and_assoc]
      · calc _ ≤ (allChoices sets).length := List.length_filter_le _ _
          _ = productSize sets := length_allChoices sets
          _ ≤ n := Nat.le_of_not_gt hle

/-- Emptiness is reported only by a completed enumeration (the product within the limit);
beyond it the result is the resource error, never InvalidCompatibility. -/
theorem compatible_empty_error (K : Manifest) (sets : List ReadingSet) (n : Nat) (hfin : productSize sets ≤ n)
    (hε : ∀ c, ¬ Compatible K sets c) :
    compatibleChoices K sets n = .error ("InvalidCompatibility: " ++ setsText sets) := by
  unfold compatibleChoices
  rw [if_neg (Nat.not_lt.mpr hfin)]
  have : (allChoices sets).filter (satisfiesAll K) = [] := by
    apply List.filter_eq_nil_iff.mpr
    intro c hc hs
    obtain ⟨hl, hi⟩ := (mem_allChoices sets c).mp hc
    exact hε c ⟨hl, hi, (satisfiesAll_iff K c).mp hs⟩
  simp [this]

theorem compatible_budget (K : Manifest) (sets : List ReadingSet) (n : Nat) (hover : productSize sets > n) :
    compatibleChoices K sets n = .error "ResourceLimit: joint choices" := by
  unfold compatibleChoices
  rw [if_pos hover]

/-- Zero open sets: the one empty choice, whose conjunction is top. `productSize [] = 1`, so
the limit must allow one choice; at `n = 0` `compatible_budget` applies instead. -/
theorem compatible_no_sets (K : Manifest) (n : Nat) (hn : 0 < n) :
    compatibleChoices K [] n = .ok [[]] ∧ Compatible K [] [] := by
  have hs : ∀ k ∈ K.constraints, Satisfies [] k := by
    intro k _
    rcases k with ⟨kind, a, b⟩
    cases kind <;> simp [Satisfies, chosen]
  have hsat : satisfiesAll K [] = true := (satisfiesAll_iff K []).mpr hs
  refine ⟨?_, ⟨rfl, fun i h => absurd h (Nat.not_lt_zero _), hs⟩⟩
  unfold compatibleChoices
  have : ¬ productSize [] > n := by simp [productSize]; omega
  rw [if_neg this]
  simp [allChoices, hsat]

theorem conj_nil : conj [] = .top := rfl

theorem joint_no_sets : joint [] [[]] = some .top := rfl

/-! ## Denotation of the joint disjunction -/

theorem conj_denote (S : VE.Structure.{u}) : ∀ l : List VE.Formula,
    (conj l).denote S [] ↔ ∀ r ∈ l, r.denote S []
  | [] => by simp [conj, VE.Formula.denote]
  | [a] => by simp [conj]
  | a :: b :: l => by
    simp only [conj, VE.Formula.denote]
    rw [conj_denote S (b :: l)]
    simp

theorem disj_denote (S : VE.Structure.{u}) : ∀ l : List VE.Formula,
    (disj l).denote S [] ↔ ∃ r ∈ l, r.denote S []
  | [] => by simp [disj, VE.Formula.denote]
  | [a] => by simp [disj]
  | a :: b :: l => by
    simp only [disj, VE.Formula.denote]
    rw [disj_denote S (b :: l)]
    simp

theorem disjunction_denote (S : VE.Structure.{u}) : ∀ (l : List VE.Formula) (φ : VE.Formula),
    disjunction l = some φ → (φ.denote S [] ↔ ∃ r ∈ l, r.denote S [])
  | [], φ, h => by simp [disjunction] at h
  | [a], φ, h => by simp [disjunction] at h; subst h; simp
  | a :: b :: l, φ, h => by
    simp only [disjunction, Option.map_eq_some_iff] at h
    obtain ⟨ψ, hψ, rfl⟩ := h
    simp only [VE.Formula.denote]
    rw [disjunction_denote S (b :: l) ψ hψ]
    simp

/-- 4.8: the joint disjunction holds iff some compatible choice holds. -/
theorem joint_denote (sets : List ReadingSet) (cs : List Choice) (J : VE.Formula) (hJ : joint sets cs = some J)
    (S : VE.Structure) : J.denote S [] ↔ ∃ c ∈ cs, ∀ r ∈ readingsOf sets c, r.denote S [] := by
  unfold joint at hJ
  split at hJ
  · cases hJ
  · cases hJ
    rw [disj_denote]
    simp only [List.mem_map]
    constructor
    · rintro ⟨_, ⟨c, hc, rfl⟩, h⟩; exact ⟨c, hc, (conj_denote S _).mp h⟩
    · rintro ⟨c, hc, h⟩; exact ⟨_, ⟨c, hc, rfl⟩, (conj_denote S _).mpr h⟩

/-- ALL over the joint set is one entailment from the disjunction. -/
theorem joint_all_iff (E : VE.Environment) (K : Manifest) (sets : List ReadingSet) (cs : List Choice)
    (Γ : List VE.Formula) (φ J : VE.Formula)
    (hcs : compatibleChoices K sets 64 = .ok cs) (hJ : joint sets cs = some J) :
    VE.Entails.{u} E (Γ ++ [J]) φ ↔ ∀ c ∈ cs, VE.Entails.{u} E (Γ ++ readingsOf sets c) φ := by
  constructor
  · intro h c hc S hS hp
    apply h S hS
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact hp a (List.mem_append_left _ ha)
    · rw [List.mem_singleton.mp ha, joint_denote sets cs J hJ S]
      exact ⟨c, hc, fun r hr => hp r (List.mem_append_right _ hr)⟩
  · intro h S hS hp
    obtain ⟨c, hc, hr⟩ := (joint_denote sets cs J hJ S).mp (hp J (List.mem_append_right _ (List.mem_singleton_self _)))
    apply h c hc S hS
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact hp a (List.mem_append_left _ ha)
    · exact hr a ha

theorem readingsOf_cons (rs : ReadingSet) (rest : List ReadingSet) (x : String × Nat × Nat) (c : Choice) :
    readingsOf (rs :: rest) (x :: c) = (rs.readings[x.2.2]?).toList ++ readingsOf rest c := by
  rcases x with ⟨s, v, r⟩
  simp only [readingsOf, List.zip_cons_cons, List.filterMap_cons]
  cases rs.readings[r]? <;> simp

theorem product_iff (S : VE.Structure.{u}) : ∀ sets : List ReadingSet,
    (∃ c ∈ allChoices sets, ∀ r ∈ readingsOf sets c, r.denote S []) ↔
      ∀ rs ∈ sets, ∃ r ∈ rs.readings, r.denote S []
  | [] => by simp [allChoices, readingsOf]
  | rs :: rest => by
    simp only [allChoices, List.mem_flatMap, List.mem_range, List.mem_map, List.forall_mem_cons]
    constructor
    · rintro ⟨_, ⟨r, hr, c, hc, rfl⟩, h⟩
      rw [readingsOf_cons] at h
      have hget : rs.readings[r]? = some rs.readings[r] := List.getElem?_eq_getElem hr
      refine ⟨⟨rs.readings[r], List.getElem_mem hr, h _ (by simp [hget])⟩, ?_⟩
      exact (product_iff S rest).mp ⟨c, hc, fun x hx => h x (List.mem_append_right _ hx)⟩
    · rintro ⟨⟨a, ha, hda⟩, hrest⟩
      obtain ⟨c, hc, hcr⟩ := (product_iff S rest).mpr hrest
      obtain ⟨r, hr, rfl⟩ := List.getElem_of_mem ha
      refine ⟨_, ⟨r, hr, c, hc, rfl⟩, ?_⟩
      rw [readingsOf_cons]
      intro x hx
      rcases List.mem_append.mp hx with hx | hx
      · simp only [List.getElem?_eq_getElem hr, Option.toList_some, List.mem_singleton] at hx
        subst hx; exact hda
      · exact hcr x hx

theorem compatibleChoices_unconstrained (K : Manifest) (hK : K.constraints = []) (sets : List ReadingSet)
    (n : Nat) (cs : List Choice) (hcs : compatibleChoices K sets n = .ok cs) : cs = allChoices sets := by
  unfold compatibleChoices at hcs
  split at hcs
  · cases hcs
  · dsimp only at hcs
    split at hcs
    · cases hcs
    · cases hcs
      apply List.filter_eq_self.mpr
      intro c _
      simp [satisfiesAll, hK]

/-- With no constraints the joint set is the product and W2's shortcut is regained
(`VE.Route.readings_all_iff`). -/
theorem unconstrained_product (K : Manifest) (hK : K.constraints = []) (sets : List ReadingSet) (cs : List Choice)
    (hcs : compatibleChoices K sets 64 = .ok cs) (S : VE.Structure) :
    (∃ c ∈ cs, ∀ r ∈ readingsOf sets c, r.denote S []) ↔ ∀ rs ∈ sets, ∃ r ∈ rs.readings, r.denote S [] := by
  rw [compatibleChoices_unconstrained K hK sets 64 cs hcs]
  exact product_iff S sets

/-- NONE: one shared model refutes every compatible choice. -/
theorem joint_none_sound {α : Type u} [DecidableEq α] (E : VE.Environment) (sets : List ReadingSet)
    (cs : List Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (M : VE.FiniteModel α) (valid : M.Valid E) (hΓ : ∀ g ∈ Γ, g.eval M [] = true)
    (hr : ∀ r ∈ occurring sets cs, r.eval M [] = true) (hφ : φ.eval M [] = false) :
    ∀ c ∈ cs, ¬ VE.Entails.{u} E (Γ ++ readingsOf sets c) φ := by
  intro c hc he
  have := he M.asStructure valid (fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact (VE.eval_iff_denote M [] a).mp (hΓ a ha)
    · exact (VE.eval_iff_denote M [] a).mp (hr a (List.mem_flatMap.mpr ⟨c, hc, ha⟩)))
  exact (VE.eval_false_iff_not_denote M [] φ).mp hφ this

/-- SOME: a certificate for one compatible choice and a countermodel for another. -/
theorem joint_some_sound {α : Type u} [DecidableEq α] (E : VE.Environment) (sets : List ReadingSet)
    (cs : List Choice) (Γ : List VE.Formula) (φ : VE.Formula) (c₁ c₂ : Choice) (h₁ : c₁ ∈ cs) (h₂ : c₂ ∈ cs)
    (cert : VE.Tableau.Certificate) (acc : VE.Tableau.checkCertificate E (Γ ++ readingsOf sets c₁) φ cert = true)
    (M : VE.FiniteModel α) (valid : M.Valid E) (hΓ : ∀ g ∈ Γ, g.eval M [] = true)
    (hr : ∀ r ∈ readingsOf sets c₂, r.eval M [] = true) (hφ : φ.eval M [] = false) :
    VE.Entails.{u} E (Γ ++ readingsOf sets c₁) φ ∧ ¬ VE.Entails.{u} E (Γ ++ readingsOf sets c₂) φ := by
  refine ⟨VE.Tableau.checkCertificate_sound.{u} E _ φ cert acc, fun he => ?_⟩
  have := he M.asStructure valid (fun a ha => by
    rcases List.mem_append.mp ha with ha | ha
    · exact (VE.eval_iff_denote M [] a).mp (hΓ a ha)
    · exact (VE.eval_iff_denote M [] a).mp (hr a ha))
  exact (VE.eval_false_iff_not_denote M [] φ).mp hφ this

/-- Independence: without constraints, on a completed enumeration of nonempty sets, the
per-unit shortcut and the joint enumeration give the same verdicts. -/
theorem independent_shortcut (E : VE.Environment) (K : Manifest) (hK : K.constraints = []) (sets : List ReadingSet)
    (hne : ∀ rs ∈ sets, rs.readings ≠ []) (cs : List Choice) (hcs : compatibleChoices K sets 64 = .ok cs)
    (Γ : List VE.Formula) (φ J : VE.Formula) (hJ : joint sets cs = some J) :
    VE.Entails.{u} E (Γ ++ [J]) φ ↔
      VE.Entails.{u} E (Γ ++ (sets.filterMap (fun rs => disjunction rs.readings))) φ := by
  have hdis : ∀ rs ∈ sets, ∃ ψ, disjunction rs.readings = some ψ := by
    intro rs hrs
    have := hne rs hrs
    match h : rs.readings with
    | [] => exact absurd h this
    | a :: l =>
      clear h this
      induction l generalizing a with
      | nil => exact ⟨a, rfl⟩
      | cons b l ih =>
        obtain ⟨ψ, hψ⟩ := ih b
        exact ⟨.or a ψ, by simp [disjunction, hψ]⟩
  have key : ∀ S : VE.Structure.{u}, J.denote S [] ↔
      ∀ a ∈ sets.filterMap (fun rs => disjunction rs.readings), a.denote S [] := by
    intro S
    rw [joint_denote sets cs J hJ S, unconstrained_product K hK sets cs hcs S]
    constructor
    · intro h a ha
      obtain ⟨rs, hrs, hd⟩ := List.mem_filterMap.mp ha
      exact (disjunction_denote S _ a hd).mpr (h rs hrs)
    · intro h rs hrs
      obtain ⟨ψ, hψ⟩ := hdis rs hrs
      exact (disjunction_denote S _ ψ hψ).mp (h ψ (List.mem_filterMap.mpr ⟨rs, hrs, hψ⟩))
  constructor
  · intro h S hS hp
    apply h S hS
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact hp a (List.mem_append_left _ ha)
    · rw [List.mem_singleton.mp ha, key S]
      exact fun b hb => hp b (List.mem_append_right _ hb)
  · intro h S hS hp
    apply h S hS
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact hp a (List.mem_append_left _ ha)
    · exact (key S).mp (hp J (List.mem_append_right _ (List.mem_singleton_self _))) a ha

/-- Citation composition is W3's, reused with its per-set meaning: a citing lemma's
transitive leaves include every cited leaf, its reading choices agree within each set,
and the recorded choices equal the choices derived from the leaves. -/
theorem citation_choices_retained (E : VE.Environment) (bg : List VE.Definitions.Bundle.Leaf) (sets : List ReadingSet)
    (bind : List VE.Formula → VE.Formula → VE.Tableau.Certificate → Except String Unit)
    (known : List VE.Definitions.Bundle.Known) (L : VE.Definitions.Bundle.Lemma) (k : VE.Definitions.Bundle.Known)
    (h : VE.Definitions.Bundle.checkLemma E bg sets bind known L = .ok k) :
    VE.Definitions.Bundle.ReadingCompatible k.leaves ∧
    (∀ m ∈ L.cites, ∀ k' ∈ known, k'.meaningId = m → ∀ l ∈ k'.leaves, l ∈ k.leaves) ∧
    VE.Definitions.Bundle.choicesEqual L.choices k.choices = true := by
  refine ⟨VE.Definitions.Bundle.checkLemma_reading E bg sets bind known L k h, ?_⟩
  unfold VE.Definitions.Bundle.checkLemma at h
  obtain ⟨⟨leaves, _, cited⟩, hc, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, hhyp, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨derived, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, hch, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  refine ⟨fun m hm k' hk' hid l hl => ?_, VE.Route.Gate.require_ok hch⟩
  have hall := List.all_eq_true.mp (VE.Route.Gate.require_ok hhyp) k' hk'
  rw [if_pos (by rw [hid]; exact List.contains_iff_mem.mpr hm)] at hall
  have hl' := List.all_eq_true.mp hall l hl
  have hsub := (VE.Definitions.Bundle.citeAll_sound known L.cites _ _ _ _ _ hc).1 l
  apply hsub
  simp only [Bool.or_eq_true, List.contains_iff_mem] at hl'
  rcases hl' with hl' | hl'
  · exact List.mem_append_left _ hl'
  · exact List.mem_append_right _ hl'

end VE.Discourse
