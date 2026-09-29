import VE.Service.Standalone

/-! The readings checker (SEMANTICS-MIGRATION-PLAN.md section 1.2 row 2, stage 2d)
and the service `readings` mode, for assertion reading sets over a ve.core@0.2
FOL-family environment.

A *choice* picks one reading from each set, in set order (`Choice`). Python's
`check_readings` claims one of three verdicts, each with its evidence; Lean
rebuilds every premise list itself and checks the evidence:

* `ALL`: one certificate for `Background ++ fixed ++ [disjunction of each set]
  ⊢ conclusion`, bound to those formulas (`readings_all_sound`: every choice
  entails the conclusion);
* `NONE`: one admissible finite model satisfying Background, the fixed premises
  and every reading of every set, where the conclusion is false
  (`readings_none_sound`: no choice entails it);
* `SOME`: a certificate for one choice and a countermodel for another
  (`readings_some_sound`).

The disjunction of a set is Python's right-nested one, `r₀ ∨ (r₁ ∨ … r_{n-1})`.
Choices are submitted as reading indices. -/
namespace VE.Service.Readings
open Lean
universe u

/-- Python's per-set disjunction (`ve/readings.py`). -/
def disjunction : List VE.Formula → VE.Formula
  | [] => .bottom
  | [a] => a
  | a :: b :: rest => .or a (disjunction (b :: rest))

theorem disjunction_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    ∀ rs : List VE.Formula, (disjunction rs).denote S ρ ↔ ∃ r ∈ rs, r.denote S ρ
  | [] => by simp [disjunction, VE.Formula.denote]
  | [a] => by simp [disjunction]
  | a :: b :: rest => by
    have ih := disjunction_denote S ρ (b :: rest)
    simp only [disjunction, VE.Formula.denote, ih, List.mem_cons, exists_eq_or_imp]

/-- `choice` picks one reading of each set, in order. -/
inductive Choice : List (List VE.Formula) → List VE.Formula → Prop where
  | nil : Choice [] []
  | cons {r : VE.Formula} {rs : List VE.Formula} {sets : List (List VE.Formula)}
      {choice : List VE.Formula} (member : r ∈ rs) (tail : Choice sets choice) :
      Choice (rs :: sets) (r :: choice)

theorem choice_covers {sets : List (List VE.Formula)} {choice : List VE.Formula}
    (h : Choice sets choice) : ∀ rs ∈ sets, ∃ r ∈ choice, r ∈ rs := by
  induction h with
  | nil => intro _ hm; cases hm
  | cons hr _ ih =>
    intro rs hm
    rcases List.mem_cons.mp hm with rfl | hm
    · exact ⟨_, List.mem_cons_self .., hr⟩
    · obtain ⟨r', hr', hm'⟩ := ih rs hm
      exact ⟨r', List.mem_cons_of_mem _ hr', hm'⟩

theorem choice_within {sets : List (List VE.Formula)} {choice : List VE.Formula}
    (h : Choice sets choice) : ∀ r ∈ choice, ∃ rs ∈ sets, r ∈ rs := by
  induction h with
  | nil => intro _ hm; cases hm
  | cons hr _ ih =>
    intro r hm
    rcases List.mem_cons.mp hm with rfl | hm
    · exact ⟨_, List.mem_cons_self .., hr⟩
    · obtain ⟨rs, hrs, hm'⟩ := ih r hm
      exact ⟨rs, List.mem_cons_of_mem _ hrs, hm'⟩

/-- The `ALL` check: the certificate over `B ++ fixed ++ disjunctions`. -/
def allCheck (E : VE.Environment) (B fixed : List VE.Formula) (sets : List (List VE.Formula))
    (φ : VE.Formula) (c : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate E (B ++ fixed ++ sets.map disjunction) φ c

/-- `readings_all_sound`: an accepted `ALL` certificate makes every choice entail
the conclusion (with Background and the fixed premises). -/
theorem readings_all_sound (E : VE.Environment) (B fixed : List VE.Formula)
    (sets : List (List VE.Formula)) (φ : VE.Formula) (c : VE.Tableau.Certificate)
    (h : allCheck E B fixed sets φ c = true) :
    ∀ choice, Choice sets choice → VE.Entails.{u} E (B ++ fixed ++ choice) φ := by
  intro choice hc S hS hsat
  apply VE.Tableau.checkCertificate_sound.{u} E _ φ c h S hS
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact hsat a (List.mem_append_left _ ha)
  · obtain ⟨rs, hrs, rfl⟩ := List.mem_map.mp ha
    obtain ⟨r, hr, hm⟩ := choice_covers hc rs hrs
    exact (disjunction_denote S [] rs).mpr ⟨r, hm, hsat r (List.mem_append_right _ hr)⟩

/-- A finite model refuting `φ` while satisfying every formula of `Γ`. -/
def refutes {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (Γ : List VE.Formula)
    (φ : VE.Formula) : Bool :=
  Γ.all (fun a => a.eval M []) && !φ.eval M []

theorem refutes_not_entails {α : Type} [DecidableEq α] (E : VE.Environment) (M : VE.FiniteModel α)
    (hM : M.asStructure.Admissible E) (Γ Δ : List VE.Formula) (φ : VE.Formula)
    (h : refutes M Γ φ = true) (sub : ∀ a ∈ Δ, a ∈ Γ) : ¬ VE.Entails.{0} E Δ φ := by
  simp only [refutes, Bool.and_eq_true, List.all_eq_true, Bool.not_eq_true'] at h
  intro hent
  have hφ := hent M.asStructure hM (fun a ha => (VE.eval_iff_denote M [] a).mp (h.1 a (sub a ha)))
  have := (VE.eval_iff_denote M [] φ).mpr hφ
  rw [h.2] at this
  cases this

/-- `readings_none_sound`: an admissible model satisfying Background, the fixed
premises and every reading of every set, where the conclusion is false, is a
countermodel for every choice. -/
theorem readings_none_sound (E : VE.Environment) (M : VE.FiniteModel VE.Bridge.Entity)
    (hM : M.asStructure.Admissible E) (B fixed : List VE.Formula) (sets : List (List VE.Formula))
    (φ : VE.Formula) (h : refutes M (B ++ fixed ++ sets.flatten) φ = true) :
    ∀ choice, Choice sets choice → ¬ VE.Entails.{0} E (B ++ fixed ++ choice) φ := by
  intro choice hc
  apply refutes_not_entails E M hM _ _ φ h
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · exact List.mem_append_left _ ha
  · obtain ⟨rs, hrs, hm⟩ := choice_within hc a ha
    exact List.mem_append_right _ (List.mem_flatten.mpr ⟨rs, hrs, hm⟩)

/-- The readings a list of indices picks, one per set. -/
def resolve : List (List VE.Formula) → List Nat → Option (List VE.Formula)
  | [], [] => some []
  | rs :: sets, i :: is => do
    let r ← rs[i]?
    let rest ← resolve sets is
    pure (r :: rest)
  | _, _ => none

theorem resolve_choice : ∀ (sets : List (List VE.Formula)) (is : List Nat) (choice : List VE.Formula),
    resolve sets is = some choice → Choice sets choice
  | [], [], _, h => by cases h; exact .nil
  | rs :: sets, i :: is, choice, h => by
    simp only [resolve, Option.bind_eq_bind, Option.bind_eq_some_iff, Option.pure_def,
      Option.some.injEq] at h
    obtain ⟨r, hr, rest, hrest, rfl⟩ := h
    exact .cons (List.mem_of_getElem? hr) (resolve_choice sets is rest hrest)
  | [], _ :: _, _, h => by cases h
  | _ :: _, [], _, h => by cases h

/-- `readings_some_sound`: an accepted certificate for one choice and a refuting
admissible model for another: some choice entails the conclusion and some
choice does not. -/
theorem readings_some_sound (E : VE.Environment) (B fixed : List VE.Formula)
    (sets : List (List VE.Formula)) (φ : VE.Formula)
    (proved refuted : List VE.Formula) (hp : Choice sets proved) (hr : Choice sets refuted)
    (c : VE.Tableau.Certificate) (hc : VE.Tableau.checkCertificate E (B ++ fixed ++ proved) φ c = true)
    (M : VE.FiniteModel VE.Bridge.Entity) (hM : M.asStructure.Admissible E)
    (hm : refutes M (B ++ fixed ++ refuted) φ = true) :
    (∃ choice, Choice sets choice ∧ VE.Entails.{0} E (B ++ fixed ++ choice) φ) ∧
      (∃ choice, Choice sets choice ∧ ¬ VE.Entails.{0} E (B ++ fixed ++ choice) φ) :=
  ⟨⟨proved, hp, VE.Tableau.checkCertificate_sound.{0} E _ φ c hc⟩,
   ⟨refuted, hr, refutes_not_entails E M hM _ _ φ hm (fun _ ha => ha)⟩⟩

/-! ## The service case -/

/-- An admissible decoded model (the route's data-model decoder: tables, flags,
definitions and literals). -/
def decodeModel (rv : VE.Route.Wire.RouteVocabulary) (j : Json) :
    Except String { M : VE.FiniteModel VE.Bridge.Entity // M.asStructure.Admissible rv.environment } :=
  match h : VE.Route.Wire.decodeDataModel rv j with
  | .ok M => .ok ⟨M, (VE.Route.Wire.decodeDataModel_valid rv j M h).1.1⟩
  | .error e => .error e

def readingsCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  let checked ← VE.Service.Standalone.validated environment
  let e := checked.envelope
  unless e.family == .fol do
    throw (VE.Route.Gate.unsupported "reading checks on this family are not implemented")
  let rv ← VE.Route.Run.decodeRouteVocabulary e
  let E := rv.environment
  let data := e.profiles.contains "data@0"
  let B := (← VE.Service.Standalone.folBackground environment rv).map Prod.fst
  let fixedJson ← (← j.getObjVal? "fixed").getArr?
  let fixed ← fixedJson.toList.mapM (VE.Route.Wire.decodeClosed E · data)
  let setsJson ← (← (← j.getObjVal? "sets").getArr?).toList.mapM fun s => do pure (← s.getArr?).toList
  unless setsJson.all (!·.isEmpty) do throw "every reading set holds a reading"
  let sets ← setsJson.mapM (·.mapM (VE.Route.Wire.decodeClosed E · data))
  let conclusionJson ← j.getObjVal? "conclusion"
  let φ ← VE.Route.Wire.decodeClosed E conclusionJson data
  let evidence ← j.getObjVal? "evidence"
  let bound := fun (premises : List VE.Formula) (c : VE.Tableau.Certificate) =>
    VE.Route.Wire.bindingOk e.profiles environment ((B ++ fixed ++ premises).map VE.Route.Wire.encodeFormula)
      conclusionJson c.environment_id c.premise_meaning_ids c.conclusion_meaning_id
  let chosen := fun (field : String) (ev : Json) => do
    let is ← (← (← ev.getObjVal? field).getArr?).toList.mapM fun x => do
      match x.getNat? with
      | .ok n => pure n
      | .error _ => throw "a choice is a list of reading indices"
    match resolve sets is with
    | some choice => pure choice
    | none => throw "a choice must pick one reading of each set"
  let verdict ← VE.Bridge.stringField j "verdict"
  let accepted ← match verdict with
    | "ALL" => do
      let c ← VE.CertificateWire.decodeCertificate (← evidence.getObjVal? "certificate")
      bound (sets.map disjunction) c
      pure (allCheck E B fixed sets φ c)
    | "NONE" => do
      let ⟨M, _⟩ ← decodeModel rv (← evidence.getObjVal? "model")
      pure (refutes M (B ++ fixed ++ sets.flatten) φ)
    | "SOME" => do
      let proof ← evidence.getObjVal? "proof"
      let proved ← chosen "choice" proof
      let c ← VE.CertificateWire.decodeCertificate (← proof.getObjVal? "certificate")
      bound proved c
      let counter ← evidence.getObjVal? "countermodel"
      let refuted ← chosen "choice" counter
      let ⟨M, _⟩ ← decodeModel rv (← counter.getObjVal? "model")
      pure (VE.Tableau.checkCertificate E (B ++ fixed ++ proved) φ c && refutes M (B ++ fixed ++ refuted) φ)
    | _ => throw s!"unknown readings verdict {verdict}"
  unless accepted do throw s!"the {verdict} evidence does not check"
  pure (VE.Route.Wire.ok id [("verdict", .str verdict)])

end VE.Service.Readings
