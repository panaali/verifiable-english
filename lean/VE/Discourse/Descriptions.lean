import VE.Discourse.Manifest
import VE.Norms.Prefix

/-! # Definite descriptions (docs/spec/discourse.md 4.5, 9.3)

For an explicit restriction `Dr` over the sort `σ` (a formula over the context `[σ]`,
index 0 the described entity), `uniqueD σ Dr` is `U(D) := ∃x:σ (Dr x ∧ ∀y:σ (Dr y → y = x))`,
the assertive reading is `∃x:σ (Dr x ∧ ∀y:σ (Dr y → y = x) ∧ P x)` and the presuppositional
claim is `∀x:σ (Dr x → P x)`, checked only under `U(D)`. Every binder carries `σ`. No
choice function or witness constant is introduced. -/
namespace VE.Discourse
universe u

/-! ## The builders (presupposition 4.1): the restriction is written at each binder -/

def uniqueAt (σ : String) (Dr Dr' : VE.Formula) : VE.Formula :=
  .ex σ (.and Dr (.all σ (.implies Dr' (.eq (.var 0) (.var 1)))))
def assertiveAt (σ : String) (Dr Dr' P : VE.Formula) : VE.Formula :=
  .ex σ (.and Dr (.and (.all σ (.implies Dr' (.eq (.var 0) (.var 1)))) P))

/-- A restriction over `σ :: Δ` (`n = Δ.length`) weakened past one new binder at index 1, by W1's `inst`. -/
def raise1 (n : Nat) (Dr : VE.Formula) : VE.Formula :=
  VE.Norms.inst (.var 0 :: (List.range n).map (fun i => .var (i + 2))) Dr
def uniqueOpen (n : Nat) (σ : String) (Dr : VE.Formula) : VE.Formula := uniqueAt σ Dr (raise1 n Dr)
def assertiveOpen (n : Nat) (σ : String) (Dr P : VE.Formula) : VE.Formula := assertiveAt σ Dr (raise1 n Dr) P

-- today's definitions become wrappers; each is `rfl`-equal to its current body (S11)
def uniqueD (σ : String) (Dr : VE.Formula) : VE.Formula := uniqueAt σ Dr Dr
def assertive (σ : String) (Dr P : VE.Formula) : VE.Formula := assertiveAt σ Dr Dr P

example (σ : String) (Dr : VE.Formula) :
    uniqueD σ Dr = .ex σ (.and Dr (.all σ (.implies Dr (.eq (.var 0) (.var 1))))) := rfl
example (σ : String) (Dr P : VE.Formula) :
    assertive σ Dr P = .ex σ (.and Dr (.and (.all σ (.implies Dr (.eq (.var 0) (.var 1)))) P)) := rfl

theorem term_inst_range_id (k : Nat) (t : VE.Term) :
    VE.Norms.Term.inst ((List.range k).map (fun i => .var i)) t = t := by
  cases t with
  | var i =>
    simp only [VE.Norms.Term.inst, List.getElem?_map]
    by_cases h : i < k <;> simp [h]
  | const c => rfl

/-- `inst` by the identity prefix `[var 0, …, var (k-1)]` changes nothing. -/
theorem inst_range_id : ∀ (a : VE.Formula) (k : Nat),
    VE.Norms.inst ((List.range k).map (fun i => .var i)) a = a
  | .top, _ | .bottom, _ => rfl
  | .unary p t, k => by simp only [VE.Norms.inst, term_inst_range_id]
  | .binary p t w, k | .eq t w, k => by simp only [VE.Norms.inst, term_inst_range_id]
  | .not a, k => by simp only [VE.Norms.inst, inst_range_id a k]
  | .and a b, k | .or a b, k | .implies a b, k => by
    simp only [VE.Norms.inst, inst_range_id a k, inst_range_id b k]
  | .all s a, k | .ex s a, k => by
    have h : (.var 0 :: ((List.range k).map (fun i => VE.Term.var i)).map VE.Norms.Term.shift) =
        (List.range (k + 1)).map (fun i => VE.Term.var i) := by
      simp [List.range_succ_eq_map, VE.Norms.Term.shift, Function.comp_def]
    simp only [VE.Norms.inst, h, inst_range_id a (k + 1)]

theorem raise1_zero (Dr : VE.Formula) : raise1 0 Dr = Dr := inst_range_id Dr 1
theorem uniqueOpen_zero (σ : String) (Dr : VE.Formula) : uniqueOpen 0 σ Dr = uniqueD σ Dr := by
  simp only [uniqueOpen, uniqueD, raise1_zero]
theorem assertiveOpen_zero (σ : String) (Dr P : VE.Formula) : assertiveOpen 0 σ Dr P = assertive σ Dr P := by
  simp only [assertiveOpen, assertive, raise1_zero]

def presupposed (σ : String) (Dr P : VE.Formula) : VE.Formula := .all σ (.implies Dr P)

/-- The two frozen carriers of `U(D)`: no `discourse:*` label reaches W2. -/
inductive PresuppositionCarrier
  | proved (node : String)
  | assumed (unit : String)
  deriving DecidableEq, Repr

/-- 7.1: the report line naming the carrier. -/
def presuppositionLine (m : Mention) (c : Option PresuppositionCarrier) : String :=
  "discourse:presupposition:" ++ m.id ++ ": " ++ match c with
    | some (.proved n) => "proved (" ++ n ++ ")"
    | some (.assumed u) => "assumed (" ++ u ++ ")"
    | none => "unresolved"

/-! ## Denotation depends only on the typed prefix of the valuation -/

theorem term_denote_prefix {E : VE.Environment} {Γ : List String} {S : VE.Structure.{u}}
    {ρ ρ' : VE.Valuation S} (hρ : ∀ i < Γ.length, ρ[i]? = ρ'[i]?) {t : VE.Term} {s : String}
    (ht : t.sortOf E Γ = some s) : t.denote S ρ = t.denote S ρ' := by
  cases t with
  | var i =>
    simp only [VE.Term.sortOf] at ht
    have : i < Γ.length := (List.getElem?_eq_some_iff.mp ht).1
    exact hρ i this
  | const c => rfl

theorem denote_prefix {E : VE.Environment} {S : VE.Structure.{u}} :
    ∀ (a : VE.Formula) (Γ : List String) (ρ ρ' : VE.Valuation S), a.WellFormed E Γ →
      (∀ i < Γ.length, ρ[i]? = ρ'[i]?) → (a.denote S ρ ↔ a.denote S ρ')
  | .top, _, _, _, _, _ => Iff.rfl
  | .bottom, _, _, _, _, _ => Iff.rfl
  | .unary p t, Γ, ρ, ρ', h, hρ => by
    obtain ⟨s, _, ht⟩ := h
    simp only [VE.Formula.denote, term_denote_prefix hρ ht]
  | .binary p t w, Γ, ρ, ρ', h, hρ => by
    obtain ⟨s, r, _, ht, hw⟩ := h
    simp only [VE.Formula.denote, term_denote_prefix hρ ht, term_denote_prefix hρ hw]
  | .eq t w, Γ, ρ, ρ', h, hρ => by
    obtain ⟨s, ht, hw⟩ := h
    simp only [VE.Formula.denote, term_denote_prefix hρ ht, term_denote_prefix hρ hw]
  | .not a, Γ, ρ, ρ', h, hρ => by
    simp only [VE.Formula.denote, denote_prefix a Γ ρ ρ' h hρ]
  | .and a b, Γ, ρ, ρ', h, hρ => by
    simp only [VE.Formula.denote, denote_prefix a Γ ρ ρ' h.1 hρ, denote_prefix b Γ ρ ρ' h.2 hρ]
  | .or a b, Γ, ρ, ρ', h, hρ => by
    simp only [VE.Formula.denote, denote_prefix a Γ ρ ρ' h.1 hρ, denote_prefix b Γ ρ ρ' h.2 hρ]
  | .implies a b, Γ, ρ, ρ', h, hρ => by
    simp only [VE.Formula.denote, denote_prefix a Γ ρ ρ' h.1 hρ, denote_prefix b Γ ρ ρ' h.2 hρ]
  | .all s a, Γ, ρ, ρ', h, hρ => by
    have hc : ∀ v : S.Carrier, ∀ i < (s :: Γ).length, (v :: ρ)[i]? = (v :: ρ')[i]? := by
      intro v i hi
      cases i with
      | zero => rfl
      | succ i => exact hρ i (by simp at hi; omega)
    simp only [VE.Formula.denote]
    exact forall_congr' fun v => imp_congr_right fun _ => denote_prefix a (s :: Γ) _ _ h.2 (hc v)
  | .ex s a, Γ, ρ, ρ', h, hρ => by
    have hc : ∀ v : S.Carrier, ∀ i < (s :: Γ).length, (v :: ρ)[i]? = (v :: ρ')[i]? := by
      intro v i hi
      cases i with
      | zero => rfl
      | succ i => exact hρ i (by simp at hi; omega)
    simp only [VE.Formula.denote]
    exact exists_congr fun v => and_congr_right fun _ => denote_prefix a (s :: Γ) _ _ h.2 (hc v)

/-- A formula over `[σ]` evaluated at `b :: rest` is evaluated at `[b]`. -/
theorem denote_head {E : VE.Environment} {S : VE.Structure.{u}} {σ : String} {a : VE.Formula}
    (h : a.WellFormed E [σ]) (b : S.Carrier) (rest : List S.Carrier) :
    a.denote S (b :: rest) ↔ a.denote S [b] :=
  denote_prefix a [σ] _ _ h (fun i hi => by
    cases i with
    | zero => rfl
    | succ i => simp at hi)

/-! ## The readings, element-wise -/

theorem uniqueD_denote (E : VE.Environment) (σ : String) (Dr : VE.Formula)
    (hD : Dr.WellFormed E [σ]) (S : VE.Structure.{u}) :
    (uniqueD σ Dr).denote S [] ↔
      ∃ a, S.domain σ a ∧ Dr.denote S [a] ∧ ∀ b, S.domain σ b → Dr.denote S [b] → b = a := by
  simp only [uniqueD, uniqueAt, VE.Formula.denote, VE.Term.denote, List.getElem?_cons_zero,
    List.getElem?_cons_succ, Option.some.injEq]
  constructor
  · rintro ⟨a, ha, hDa, hu⟩
    refine ⟨a, ha, hDa, fun b hb hDb => ?_⟩
    obtain ⟨v, rfl, rfl⟩ := hu b hb ((denote_head hD b [a]).mpr hDb)
    rfl
  · rintro ⟨a, ha, hDa, hu⟩
    exact ⟨a, ha, hDa, fun b hb hDb => ⟨b, rfl, (hu b hb ((denote_head hD b [a]).mp hDb)).symm⟩⟩

theorem presupposed_denote (E : VE.Environment) (σ : String) (Dr P : VE.Formula)
    (S : VE.Structure.{u}) :
    (presupposed σ Dr P).denote S [] ↔ ∀ a, S.domain σ a → Dr.denote S [a] → P.denote S [a] := by
  simp only [presupposed, VE.Formula.denote]

/-- The assertive reading is the unique-element statement, element-wise, over the sort's domain. -/
theorem assertive_denote (E : VE.Environment) (σ : String) (hσ : σ ∈ E.sorts) (Dr P : VE.Formula)
    (hD : Dr.WellFormed E [σ]) (hP : P.WellFormed E [σ]) (S : VE.Structure) (hS : S.Admissible E) :
    (assertive σ Dr P).denote S [] ↔
      ∃ a, S.domain σ a ∧ Dr.denote S [a] ∧ (∀ b, S.domain σ b → Dr.denote S [b] → b = a) ∧
        P.denote S [a] := by
  simp only [assertive, assertiveAt, VE.Formula.denote, VE.Term.denote, List.getElem?_cons_zero,
    List.getElem?_cons_succ, Option.some.injEq]
  constructor
  · rintro ⟨a, ha, hDa, hu, hPa⟩
    refine ⟨a, ha, hDa, fun b hb hDb => ?_, hPa⟩
    obtain ⟨v, rfl, rfl⟩ := hu b hb ((denote_head hD b [a]).mpr hDb)
    rfl
  · rintro ⟨a, ha, hDa, hu, hPa⟩
    exact ⟨a, ha, hDa, fun b hb hDb => ⟨b, rfl, (hu b hb ((denote_head hD b [a]).mp hDb)).symm⟩, hPa⟩

/-- 4.5: definedness of the assertive reading, at the binder sort σ. -/
theorem description_definedness (E : VE.Environment) (σ : String) (hσ : σ ∈ E.sorts) (Dr P : VE.Formula)
    (hD : Dr.WellFormed E [σ]) (hP : P.WellFormed E [σ]) (S : VE.Structure) (hS : S.Admissible E) :
    (assertive σ Dr P).denote S [] ↔ (uniqueD σ Dr).denote S [] ∧ (presupposed σ Dr P).denote S [] := by
  rw [assertive_denote E σ hσ Dr P hD hP S hS, uniqueD_denote E σ Dr hD S, presupposed_denote E σ Dr P S]
  constructor
  · rintro ⟨a, ha, hDa, hu, hPa⟩
    exact ⟨⟨a, ha, hDa, hu⟩, fun b hb hDb => (hu b hb hDb) ▸ hPa⟩
  · rintro ⟨⟨a, ha, hDa, hu⟩, hp⟩
    exact ⟨a, ha, hDa, hu, hp a ha hDa⟩

/-- The presuppositional claim is proved only where U(D) holds: a checked certificate for
the claim over premises that include U(D) (the P0 acceptance theorem, instantiated). -/
theorem presupposition_retained (E : VE.Environment) (Γ : List VE.Formula) (σ : String) (Dr P : VE.Formula)
    (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate E (Γ ++ [uniqueD σ Dr]) (presupposed σ Dr P) c = true)
    (S : VE.Structure) (hS : S.Admissible E) (hΓ : VE.Norms.Sat S Γ) (hU : (uniqueD σ Dr).denote S []) :
    (presupposed σ Dr P).denote S [] := by
  apply VE.Tableau.checkCertificate_sound E _ _ c acc S hS
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact hΓ a ha
  · rw [List.mem_singleton.mp ha]; exact hU

end VE.Discourse
