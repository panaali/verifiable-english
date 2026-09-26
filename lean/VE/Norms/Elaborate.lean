import VE.Norms.Valid

/-! Elaboration (docs/spec/norms.md 4.2-4.4 and 6.1) and its faithfulness to the
direct Catala-style semantics.

The generated formulas (`applies`, `yields`, `selects`, `pos`, `neg`,
`outcome`, `elabPremise`) have exactly the shapes Python `ve/norms.py` builds, so the
premise lists compare byte-for-byte. Recursion on the precedence DAG uses fuel
`T.nodes.length`, which exceeds every rule's height in an acyclic DAG.

The direct semantics (`AppliesD`, `YieldsD`, `SelectsD`, `DecidesD`, `Value`)
is a recursion on rules over propositions, defined independently of the
generated formulas; `elaborate_iff_at` is faithfulness to it. -/
namespace VE.Norms
universe u

def fuel (T : Tree) : Nat := T.nodes.length

/-- The rule applies: its guard holds and no carve-out holds. -/
def applies (N : Node) : VE.Formula := .and N.guard (.not (anyF N.carveOuts))

/-- `N`'s subtree decides (Catala: the subtree yields a value). -/
def yields (T : Tree) : Nat → Node → VE.Formula
  | 0, N => .or (applies N) (anyF [])
  | f + 1, N => .or (applies N) (anyF ((children T N).map (yields T f)))

/-- `N` itself decides: it applies and no exception subtree yields. -/
def selects (T : Tree) (f : Nat) (N : Node) : VE.Formula :=
  .and (applies N) (.not (anyF ((children T N).map (yields T f))))

/-- Some rule of the given sign on `p` decides. -/
def decides (T : Tree) (p : String) (sign : Bool) : VE.Formula :=
  anyF (((rulesOn T p).filter (·.sign == sign)).map (selects T (fuel T)))

def pos (T : Tree) (p : String) : VE.Formula := decides T p true
def neg (T : Tree) (p : String) : VE.Formula := decides T p false

/-- The completed outcome `O_p`: `P_p` for deny, `¬N_p` for allow (4.3). -/
def outcome (T : Tree) (r : Regulated) : VE.Formula :=
  if r.allowByDefault then .not (neg T r.name) else pos T r.name

/-- The three clauses of `elab_p`, over the situation variables. -/
def elabBody (T : Tree) (r : Regulated) : VE.Formula :=
  let P := pos T r.name
  let N := neg T r.name
  let A := atom r.name r.sorts
  allF [.implies P A, .implies N (.not A),
    .implies (.and (.not P) (.not N)) (if r.allowByDefault then A else .not A)]

/-- `elab_p := ∀x̄. (P → p) ∧ (N → ¬p) ∧ ((¬P ∧ ¬N) → (p ↔ d))` (4.4). -/
def elabPremise (T : Tree) (r : Regulated) : VE.Formula := bindAll r.sorts (elabBody T r)

/-- W3's biconditional `∀x̄. p(x̄) ↔ body` (the shape of `VE.Definitions.Def.premise`). -/
def Definition.premise (d : Definition) : VE.Formula :=
  bindAll d.args (iffF (atom d.name d.args) d.body)

/-- The premise generated for one layer symbol. -/
def Sym.premise (T : Tree) : Sym → VE.Formula
  | .reg r => elabPremise T r
  | .defn d => d.premise

/-- `Norms.elaborate`: the norm elaborations, in DAG order (the layer premises). -/
def elaborate (T : Tree) : List VE.Formula :=
  (syms T).filterMap (fun | .reg r => some (elabPremise T r) | .defn _ => none)

/-- W3 biconditionals in DAG order: the `definitions` slice of Background. -/
def definitionPremises (T : Tree) : List VE.Formula :=
  (syms T).filterMap (fun | .defn d => some d.premise | .reg _ => none)

/-! ## The direct semantics -/

section Direct
variable (T : Tree) (S : VE.Structure.{u}) (ρ : VE.Valuation S)

def AppliesD (N : Node) : Prop := N.guard.denote S ρ ∧ ¬ ∃ U ∈ N.carveOuts, U.denote S ρ

def YieldsD : Nat → Node → Prop
  | 0, N => AppliesD S ρ N
  | f + 1, N => AppliesD S ρ N ∨ ∃ C ∈ children T N, YieldsD f C

def SelectsD (f : Nat) (N : Node) : Prop :=
  AppliesD S ρ N ∧ ¬ ∃ C ∈ children T N, YieldsD T S ρ f C

def DecidesD (p : String) (sign : Bool) : Prop :=
  ∃ N ∈ rulesOn T p, N.sign = sign ∧ SelectsD T S ρ (fuel T) N

end Direct

/-- Catala's four cases: a value when exactly one side decides, the default when
neither does, no value (the conflict error) when both do. -/
noncomputable def catalaValue (P N : Prop) (d : Bool) : Option Bool := by
  classical
  exact if P ∧ N then none else if P then some true else if N then some false else some d

/-- `Value_p(S, v̄)`, by direct rule recursion under `tupleVal vs`. -/
noncomputable def Value (T : Tree) (r : Regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) :
    Option Bool :=
  catalaValue (DecidesD T S (tupleVal vs) r.name true) (DecidesD T S (tupleVal vs) r.name false)
    r.allowByDefault

/-- `Intended_p`: on every typed tuple the rules give a value and `p` holds
exactly when it is true. The rules are read below `p` (`forget [p]`). -/
def IntendedAt (T : Tree) (r : Regulated) (S : VE.Structure.{u}) : Prop :=
  ∀ vs, VE.TupleTyped S r.sorts vs →
    ∃ b, Value T r (forget [r.name] S) vs = some b ∧ (S.relation r.name vs ↔ b = true)

def holdsCatala (T : Tree) (S : VE.Structure.{u}) : Prop := ∀ r ∈ T.regulated, IntendedAt T r S

/-! ## Denotation of the generated formulas -/

section Denote
variable (T : Tree) (S : VE.Structure.{u}) (ρ : VE.Valuation S)

theorem applies_denote (N : Node) : (applies N).denote S ρ ↔ AppliesD S ρ N := by
  simp [applies, AppliesD, VE.Formula.denote, anyF_denote]

theorem yields_denote : ∀ (f : Nat) (N : Node), (yields T f N).denote S ρ ↔ YieldsD T S ρ f N
  | 0, N => by simp [yields, YieldsD, VE.Formula.denote, anyF_denote, applies_denote]
  | f + 1, N => by
    simp only [yields, YieldsD, VE.Formula.denote, anyF_denote, applies_denote, List.mem_map]
    constructor
    · rintro (h | ⟨_, ⟨C, hC, rfl⟩, hy⟩)
      · exact Or.inl h
      · exact Or.inr ⟨C, hC, (yields_denote f C).mp hy⟩
    · rintro (h | ⟨C, hC, hy⟩)
      · exact Or.inl h
      · exact Or.inr ⟨_, ⟨C, hC, rfl⟩, (yields_denote f C).mpr hy⟩

theorem selects_denote (f : Nat) (N : Node) : (selects T f N).denote S ρ ↔ SelectsD T S ρ f N := by
  simp only [selects, SelectsD, VE.Formula.denote, anyF_denote, applies_denote, List.mem_map]
  apply and_congr_right
  intro _
  apply not_congr
  constructor
  · rintro ⟨_, ⟨C, hC, rfl⟩, hy⟩
    exact ⟨C, hC, (yields_denote T S ρ f C).mp hy⟩
  · rintro ⟨C, hC, hy⟩
    exact ⟨_, ⟨C, hC, rfl⟩, (yields_denote T S ρ f C).mpr hy⟩

theorem decides_denote (p : String) (sign : Bool) :
    (decides T p sign).denote S ρ ↔ DecidesD T S ρ p sign := by
  simp only [decides, DecidesD, anyF_denote, List.mem_map, List.mem_filter, beq_iff_eq]
  constructor
  · rintro ⟨_, ⟨N, ⟨hN, hs⟩, rfl⟩, h⟩
    exact ⟨N, hN, hs, (selects_denote T S ρ _ N).mp h⟩
  · rintro ⟨N, hN, hs, h⟩
    exact ⟨_, ⟨N, ⟨hN, hs⟩, rfl⟩, (selects_denote T S ρ _ N).mpr h⟩

theorem outcome_denote (r : Regulated) :
    (outcome T r).denote S ρ ↔
      (if r.allowByDefault then ¬ (neg T r.name).denote S ρ else (pos T r.name).denote S ρ) := by
  unfold outcome
  cases r.allowByDefault <;> simp [VE.Formula.denote]

end Denote

/-! ## Typing of the generated formulas -/

section Typing
variable (T : Tree) (E : VE.Environment) (Γ : List String)

theorem anyF_wellFormed (l : List VE.Formula) (h : ∀ a ∈ l, a.WellFormed E Γ) :
    (anyF l).WellFormed E Γ := by
  suffices ∀ acc : VE.Formula, acc.WellFormed E Γ → (l.foldl .or acc).WellFormed E Γ from
    this _ trivial
  induction l with
  | nil => intro acc h; exact h
  | cons a l ih =>
    intro acc hacc
    exact ih (fun b hb => h b (List.mem_cons_of_mem _ hb)) _ ⟨hacc, h a List.mem_cons_self⟩

theorem allF_wellFormed (l : List VE.Formula) (h : ∀ a ∈ l, a.WellFormed E Γ) :
    (allF l).WellFormed E Γ := by
  suffices ∀ acc : VE.Formula, acc.WellFormed E Γ → (l.foldl .and acc).WellFormed E Γ from
    this _ trivial
  induction l with
  | nil => intro acc h; exact h
  | cons a l ih =>
    intro acc hacc
    exact ih (fun b hb => h b (List.mem_cons_of_mem _ hb)) _ ⟨hacc, h a List.mem_cons_self⟩

/-- Every rule on `p` has a guard and carve-outs typed over `E` in `Γ`. -/
def RulesTyped (p : String) : Prop :=
  ∀ N ∈ T.nodes, N.pred = p → N.guard.WellFormed E Γ ∧ ∀ U ∈ N.carveOuts, U.WellFormed E Γ

variable {T E Γ}

theorem mem_children {N C : Node} (h : C ∈ children T N) : C ∈ T.nodes ∧ C.pred = N.pred := by
  simp only [children, List.mem_mergeSort, List.mem_filter, Bool.and_eq_true, beq_iff_eq] at h
  exact ⟨h.1, h.2.1⟩

theorem applies_wellFormed {N : Node} (h : N.guard.WellFormed E Γ ∧ ∀ U ∈ N.carveOuts, U.WellFormed E Γ) :
    (applies N).WellFormed E Γ :=
  ⟨h.1, anyF_wellFormed E Γ _ h.2⟩

theorem yields_wellFormed {p : String} (hT : RulesTyped T E Γ p) :
    ∀ (f : Nat) (N : Node), N ∈ T.nodes → N.pred = p → (yields T f N).WellFormed E Γ
  | 0, N, hN, hp => ⟨applies_wellFormed (hT N hN hp), anyF_wellFormed E Γ _ (by simp)⟩
  | f + 1, N, hN, hp => by
    refine ⟨applies_wellFormed (hT N hN hp), anyF_wellFormed E Γ _ ?_⟩
    intro a ha
    obtain ⟨C, hC, rfl⟩ := List.mem_map.mp ha
    obtain ⟨hC, hCp⟩ := mem_children hC
    exact yields_wellFormed hT f C hC (hCp.trans hp)

theorem selects_wellFormed {p : String} (hT : RulesTyped T E Γ p) (f : Nat) (N : Node)
    (hN : N ∈ T.nodes) (hp : N.pred = p) : (selects T f N).WellFormed E Γ := by
  refine ⟨applies_wellFormed (hT N hN hp), anyF_wellFormed E Γ _ ?_⟩
  intro a ha
  obtain ⟨C, hC, rfl⟩ := List.mem_map.mp ha
  obtain ⟨hC, hCp⟩ := mem_children hC
  exact yields_wellFormed hT f C hC (hCp.trans hp)

theorem decides_wellFormed {p : String} (hT : RulesTyped T E Γ p) (sign : Bool) :
    (decides T p sign).WellFormed E Γ := by
  apply anyF_wellFormed
  intro a ha
  obtain ⟨N, hN, rfl⟩ := List.mem_map.mp ha
  simp only [List.mem_filter, rulesOn, beq_iff_eq] at hN
  exact selects_wellFormed hT _ N hN.1.1 hN.1.2

theorem outcome_wellFormed {r : Regulated} (hT : RulesTyped T E Γ r.name) :
    (outcome T r).WellFormed E Γ := by
  unfold outcome
  cases r.allowByDefault
  · exact decides_wellFormed hT true
  · exact decides_wellFormed hT false

theorem atom_wellFormed {p : String} {sorts : List String} (ha : Arity sorts)
    (hp : E.predicates p = some sorts) : (atom p sorts).WellFormed E sorts.reverse := by
  unfold Arity at ha
  match sorts, ha with
  | [s], _ => exact ⟨s, hp, rfl⟩
  | [s, t], _ => exact ⟨s, t, hp, rfl, rfl⟩

theorem bindAll_wellFormed {sorts : List String} (hs : ∀ s ∈ sorts, s ∈ E.sorts) :
    ∀ (Δ : List String) (body : VE.Formula), body.WellFormed E (sorts.reverse ++ Δ) →
      (bindAll sorts body).WellFormed E Δ := by
  induction sorts with
  | nil => intro Δ body h; simpa [bindAll] using h
  | cons s ss ih =>
    intro Δ body h
    refine ⟨hs s List.mem_cons_self, ?_⟩
    exact ih (fun t ht => hs t (List.mem_cons_of_mem _ ht)) (s :: Δ) body (by simpa using h)

theorem elab_wellFormed {r : Regulated} (hT : RulesTyped T E r.sorts.reverse r.name)
    (ha : Arity r.sorts) (hp : E.predicates r.name = some r.sorts) (hs : ∀ s ∈ r.sorts, s ∈ E.sorts) :
    (elabPremise T r).WellFormed E [] := by
  apply bindAll_wellFormed hs [] _
  simp only [List.append_nil]
  have hP := decides_wellFormed hT true
  have hN := decides_wellFormed hT false
  have hA := atom_wellFormed ha hp
  apply allF_wellFormed
  intro a ha'
  simp only [List.mem_cons, List.mem_nil_iff, or_false] at ha'
  rcases ha' with rfl | rfl | rfl
  · exact ⟨hP, hA⟩
  · exact ⟨hN, hA⟩
  · refine ⟨⟨hP, hN⟩, ?_⟩
    cases r.allowByDefault
    · exact hA
    · exact hA

theorem definition_premise_wellFormed {d : Definition} (hb : d.body.WellFormed E d.args.reverse)
    (ha : Arity d.args) (hp : E.predicates d.name = some d.args) (hs : ∀ s ∈ d.args, s ∈ E.sorts) :
    d.premise.WellFormed E [] := by
  apply bindAll_wellFormed hs [] _
  simp only [List.append_nil]
  have hA := atom_wellFormed ha hp
  exact ⟨⟨hA, hb⟩, ⟨hb, hA⟩⟩

end Typing

/-! ## Faithfulness -/

theorem catalaValue_spec (P N R : Prop) (d : Bool) :
    (∃ b, catalaValue P N d = some b ∧ (R ↔ b = true)) ↔
      ((P → R) ∧ (N → ¬ R) ∧ (¬ P ∧ ¬ N → (R ↔ d = true))) := by
  classical
  unfold catalaValue
  by_cases hP : P <;> by_cases hN : N
  · rw [if_pos ⟨hP, hN⟩]
    constructor
    · rintro ⟨_, h, _⟩; cases h
    · rintro ⟨h₁, h₂, _⟩; exact absurd (h₁ hP) (h₂ hN)
  · rw [if_neg (fun h => hN h.2), if_pos hP]
    constructor
    · rintro ⟨b, hb, hR⟩
      cases hb
      exact ⟨fun _ => hR.mpr rfl, fun h => absurd h hN, fun h => absurd hP h.1⟩
    · rintro ⟨h₁, _, _⟩
      exact ⟨true, rfl, ⟨fun _ => rfl, fun _ => h₁ hP⟩⟩
  · rw [if_neg (fun h => hP h.1), if_neg hP, if_pos hN]
    constructor
    · rintro ⟨b, hb, hR⟩
      cases hb
      exact ⟨fun h => absurd h hP, fun _ hr => Bool.false_ne_true (hR.mp hr),
        fun h => absurd hN h.2⟩
    · rintro ⟨_, h₂, _⟩
      exact ⟨false, rfl, ⟨fun hr => absurd hr (h₂ hN), fun h => Bool.noConfusion h⟩⟩
  · rw [if_neg (fun h => hP h.1), if_neg hP, if_neg hN]
    constructor
    · rintro ⟨b, hb, hR⟩
      cases hb
      exact ⟨fun h => absurd h hP, fun h => absurd h hN, fun _ => hR⟩
    · rintro ⟨_, _, h₃⟩
      exact ⟨d, rfl, h₃ ⟨hP, hN⟩⟩

theorem elabBody_denote (T : Tree) (r : Regulated) (ha : Arity r.sorts) (S : VE.Structure.{u})
    (vs : List S.Carrier) (hv : VE.TupleTyped S r.sorts vs) :
    (elabBody T r).denote S (tupleVal vs) ↔
      (((pos T r.name).denote S (tupleVal vs) → S.relation r.name vs) ∧
        ((neg T r.name).denote S (tupleVal vs) → ¬ S.relation r.name vs) ∧
        (¬ (pos T r.name).denote S (tupleVal vs) ∧ ¬ (neg T r.name).denote S (tupleVal vs) →
          (S.relation r.name vs ↔ r.allowByDefault = true))) := by
  have hA := atom_denote S r.name r.sorts ha vs hv
  simp only [elabBody, allF_denote, List.mem_cons, List.mem_nil_iff, or_false, forall_eq_or_imp,
    forall_eq, VE.Formula.denote, hA]
  cases r.allowByDefault <;> simp [VE.Formula.denote, hA]

/-- Faithfulness at one tuple, for any structure in which the rule formulas do
not see `p` (as typing below `p` guarantees). -/
theorem elab_iff_intended (T : Tree) (r : Regulated) (ha : Arity r.sorts) (S : VE.Structure.{u})
    (hforget : ∀ (ρ : VE.Valuation S) sign, (decides T r.name sign).denote (forget [r.name] S) ρ ↔
      (decides T r.name sign).denote S ρ) :
    (elabPremise T r).denote S [] ↔ IntendedAt T r S := by
  rw [elabPremise, bindAll_denote_nil]
  apply forall_congr'
  intro vs
  apply imp_congr_right
  intro hv
  rw [elabBody_denote T r ha S vs hv]
  simp only [Value]
  rw [catalaValue_spec, ← decides_denote, ← decides_denote, hforget, hforget]
  rfl

/-- The rules on a regulated symbol are typed below it. -/
theorem rulesTyped_of_valid {D : Doc} (hv : Valid D) {k : Nat} {r : Regulated}
    (hk : (syms D.T)[k]? = some (.reg r)) : RulesTyped D.T (envAt D k) r.sorts.reverse r.name := by
  intro N hN hp
  have ht := hv.typed k (.reg r) hk
  simp only [Sym.formulas, Sym.sorts, List.mem_flatMap, List.mem_cons, rulesOn, List.mem_filter,
    beq_iff_eq] at ht
  exact ⟨ht N.guard ⟨N, ⟨hN, hp⟩, Or.inl rfl⟩, fun U hU => ht U ⟨N, ⟨hN, hp⟩, Or.inr hU⟩⟩

theorem decides_forget {D : Doc} (hv : Valid D) {k : Nat} {r : Regulated}
    (hk : (syms D.T)[k]? = some (.reg r)) (ns : List String)
    (hns : ∀ n ∈ ns, (envAt D k).predicates n = none) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (sign : Bool) :
    (decides D.T r.name sign).denote (forget ns S) ρ ↔ (decides D.T r.name sign).denote S ρ :=
  denote_forget hns S _ r.sorts.reverse ρ (decides_wellFormed (rulesTyped_of_valid hv hk) sign)

theorem regulated_arity {D : Doc} (hv : Valid D) {r : Regulated} (hr : Sym.reg r ∈ syms D.T) :
    Arity r.sorts :=
  (hv.decl _ hr).2.1

/-- `elaborate_iff_at`: the elaboration of `p` holds exactly when the direct
semantics does, on every structure (admissibility is not needed). -/
theorem elaborate_iff_at (D : Doc) (h : WellFormed D = true) (r : Regulated)
    (hr : r ∈ D.T.regulated) (S : VE.Structure.{u}) :
    (elabPremise D.T r).denote S [] ↔ IntendedAt D.T r S := by
  have hv := valid_of_wellFormed D h
  have hs := hv.regulated r hr
  obtain ⟨k, hk⟩ := mem_syms_index hs
  exact elab_iff_intended D.T r (regulated_arity hv hs) S
    (decides_forget hv hk [r.name] (self_hidden hv hk) S)

/-- Catala's value exists and is `outcome` exactly where not both sides decide. -/
theorem body_iff_outcome (P N R : Prop) (d : Bool) (hc : ¬ (P ∧ N)) :
    ((P → R) ∧ (N → ¬ R) ∧ (¬ P ∧ ¬ N → (R ↔ d = true))) ↔ (R ↔ if d then ¬ N else P) := by
  classical
  by_cases hP : P <;> by_cases hN : N <;> cases d <;> simp_all

/-- `elab_completion`: without opposite selections the elaboration is the
completed-outcome biconditional `∀x̄. p(x̄) ↔ O_p(x̄)`. -/
theorem elab_completion (T : Tree) (r : Regulated) (ha : Arity r.sorts) (S : VE.Structure.{u})
    (hc : ∀ vs, VE.TupleTyped S r.sorts vs →
      ¬ ((pos T r.name).denote S (tupleVal vs) ∧ (neg T r.name).denote S (tupleVal vs))) :
    (elabPremise T r).denote S [] ↔
      (∀ vs, VE.TupleTyped S r.sorts vs →
        (S.relation r.name vs ↔ (outcome T r).denote S (tupleVal vs))) := by
  rw [elabPremise, bindAll_denote_nil]
  apply forall_congr'
  intro vs
  apply imp_congr_right
  intro hv
  rw [elabBody_denote T r ha S vs hv, body_iff_outcome _ _ _ _ (hc vs hv), outcome_denote]

theorem lookupSym_reg {T : Tree} {n : String} {r : Regulated} (h : lookupSym T n = some (.reg r)) :
    r ∈ T.regulated := by
  unfold lookupSym at h
  split at h
  · rename_i r' hf
    cases h
    exact List.mem_of_find?_eq_some hf
  · cases hd : T.definitions.find? (·.name == n) <;> simp [hd] at h

theorem lookupSym_defn {T : Tree} {n : String} {d : Definition} (h : lookupSym T n = some (.defn d)) :
    d ∈ T.definitions := by
  unfold lookupSym at h
  split at h
  · cases h
  · cases hd : T.definitions.find? (·.name == n) with
    | none => simp [hd] at h
    | some d' =>
      simp only [hd, Option.map_some, Option.some.injEq, Sym.defn.injEq] at h
      subst h
      exact List.mem_of_find?_eq_some hd

theorem mem_syms_reg {T : Tree} {r : Regulated} (h : Sym.reg r ∈ syms T) : r ∈ T.regulated := by
  obtain ⟨n, _, hn⟩ := List.mem_filterMap.mp h
  exact lookupSym_reg hn

theorem mem_syms_defn {T : Tree} {d : Definition} (h : Sym.defn d ∈ syms T) : d ∈ T.definitions := by
  obtain ⟨n, _, hn⟩ := List.mem_filterMap.mp h
  exact lookupSym_defn hn

theorem mem_elaborate {T : Tree} {a : VE.Formula} :
    a ∈ elaborate T ↔ ∃ r, Sym.reg r ∈ syms T ∧ a = elabPremise T r := by
  simp only [elaborate, List.mem_filterMap]
  constructor
  · rintro ⟨q, hq, h⟩
    cases q with
    | reg r => simp only [Option.some.injEq] at h; exact ⟨r, hq, h.symm⟩
    | defn _ => cases h
  · rintro ⟨r, hr, rfl⟩
    exact ⟨.reg r, hr, rfl⟩

/-- `elaborate_iff`: the document's norm elaborations hold exactly when the
direct semantics holds for every regulated predicate. -/
theorem elaborate_iff (D : Doc) (h : WellFormed D = true) (S : VE.Structure.{u}) :
    (∀ a ∈ elaborate D.T, a.denote S []) ↔ holdsCatala D.T S := by
  have hv := valid_of_wellFormed D h
  constructor
  · intro hs r hr
    exact (elaborate_iff_at D h r hr S).mp (hs _ (mem_elaborate.mpr ⟨r, hv.regulated r hr, rfl⟩))
  · intro hc a ha
    obtain ⟨r, hr, rfl⟩ := mem_elaborate.mp ha
    exact (elaborate_iff_at D h r (mem_syms_reg hr) S).mpr (hc r (mem_syms_reg hr))

end VE.Norms
