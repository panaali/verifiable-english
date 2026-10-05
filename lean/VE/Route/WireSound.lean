import VE.Route.Wire

/-! One acceptance theorem for the `route` runners `Wire.runFol`,
`Wire.runClosure` and `Wire.runOrder` (docs/CONSOLIDATION-PLAN.md step 2a).

What a reviewer reads instead of the runners is a `Family` (a logic, a
vocabulary type, its typing environment, the reviewed meaning `Intended` of a
vocabulary, and the decoders of a case's premises, conclusion and document) and
three claims over it:

* `CertificateClaim`: the decoded conclusion holds in every intended structure
  satisfying the decoded premises;
* `CountermodelAnswer`: the decoded model is intended, and the answer's
  `refutes` is `true` exactly when it satisfies the decoded premises and
  falsifies the decoded conclusion (`CountermodelClaim` is the refuting case);
* `EvaluateClaim`: each answered value is the truth of the corresponding
  decoded formula in the decoded, intended model.

The checked side of a family is a `Runner`: the runner function, its checker
and the regenerated Background. `Runner.acceptance` is proved once, over any
family and any `Checker`, through `route_acceptance` on the identity layer of
the family's meaning. The three instances `folRunner`, `closureRunner` and
`orderRunner` have `runFol`, `runClosure` and `runOrder` as their `run`, by
`rfl`; each discharges `Runner.Sound` by inverting the runner's binds, so a
successful certificate case whose `"valid"` field is `true` yields the
source-decode, binding and checker conjuncts.

The meanings: the FOL and closure families read `Definitions.Intended` (string
admissible, every defined predicate agreeing with its body) and the flags'
`Data.Background.Intended` (functional and total tables), the meaning
`decodeDataModel_combined` states; this is the meaning of the whole regenerated
Background `fullBackground` (flags, definitions, literals). The order family
reads `OrderStringAdmissible` (admissible, declared literals distinct): a
`RouteOrderVocabulary` has no flags and no definitions (it has no such fields,
and `orderVocabulary_no_definitions` shows the decoder rejects a `defined`
predicate), so `Background.orderLiterals` is its whole Background.

The public entry `Route.Run.runCase` is reached in `VE.Route.RunSound`. -/
namespace VE.Route.WireSound
open Lean
open VE.Route.Wire
open VE.Order.ProfileGate (bind_ok)
universe u

/-! ## The family record and its claims -/

/-- A checker family as the reviewer reads it. -/
structure Family where
  L : Semantics.{u}
  Vocab : Type
  env : Vocab → L.Env
  /-- The reviewed meaning of a vocabulary: admissible, flags, definitions, literals. -/
  Intended : Vocab → L.Model → Prop
  decodePremises : Vocab → Json → Except String (List L.Formula)
  decodeConclusion : Vocab → Json → Except String L.Formula
  /-- The formulas of an `evaluate` case. -/
  decodeDocument : Vocab → Json → Except String (List L.Formula)

/-- An accepted certificate case: the decoded conclusion holds in every
intended structure that satisfies the decoded premises. -/
def CertificateClaim (F : Family.{u}) (rv : F.Vocab) (j : Json) : Prop :=
  ∃ ps c, F.decodePremises rv j = .ok ps ∧ F.decodeConclusion rv j = .ok c ∧
    ∀ S, F.Intended rv S → F.L.Sat S ps → F.L.Holds S c

/-- A refuting countermodel case: the case's model decodes to an intended
structure that satisfies the decoded premises and falsifies the decoded
conclusion. Finite models live in universe 0. -/
def CountermodelClaim (F : Family.{0}) (decodeModel : F.Vocab → Json → Except String F.L.Model)
    (rv : F.Vocab) (j : Json) : Prop :=
  ∃ ps c S, F.decodePremises rv j = .ok ps ∧ F.decodeConclusion rv j = .ok c ∧
    decodeModel rv j = .ok S ∧ F.Intended rv S ∧ F.L.Sat S ps ∧ ¬ F.L.Holds S c

/-- A countermodel answer: the case's model decodes to an intended structure,
and the answer's `refutes` field is `true` exactly when that structure satisfies
the decoded premises and falsifies the decoded conclusion. -/
def CountermodelAnswer (F : Family.{0}) (decodeModel : F.Vocab → Json → Except String F.L.Model)
    (rv : F.Vocab) (j answer : Json) : Prop :=
  ∃ ps c S b, F.decodePremises rv j = .ok ps ∧ F.decodeConclusion rv j = .ok c ∧
    decodeModel rv j = .ok S ∧ F.Intended rv S ∧ answer.getObjValD "refutes" = .bool b ∧
    (b = true ↔ F.L.Sat S ps ∧ ¬ F.L.Holds S c)

theorem countermodelAnswer_refutes (F : Family.{0})
    (decodeModel : F.Vocab → Json → Except String F.L.Model) (rv : F.Vocab) (j answer : Json)
    (h : CountermodelAnswer F decodeModel rv j answer) (hr : answer.getObjValD "refutes" = .bool true) :
    CountermodelClaim F decodeModel rv j := by
  obtain ⟨ps, c, S, b, hps, hc, hS, hi, hb, hiff⟩ := h
  rw [hr] at hb
  cases hb
  obtain ⟨hsat, hn⟩ := hiff.mp rfl
  exact ⟨ps, c, S, hps, hc, hS, hi, hsat, hn⟩

/-- An evaluate answer: the case's model decodes to an intended structure, and
the answer's `values` are, in order, the truth of each decoded formula in it. -/
def EvaluateClaim (F : Family.{0}) (decodeModel : F.Vocab → Json → Except String F.L.Model)
    (rv : F.Vocab) (j answer : Json) : Prop :=
  ∃ fs S vs, F.decodeDocument rv j = .ok fs ∧ decodeModel rv j = .ok S ∧ F.Intended rv S ∧
    answer.getObjValD "values" = toJson vs ∧ vs.length = fs.length ∧
    ∀ p ∈ fs.zip vs, (p.2 = true ↔ F.L.Holds S p.1)

/-- A certificate claim and a countermodel claim never hold of the same case:
the route cannot answer `valid: true` and `refutes: true` for one premise list
and conclusion against one vocabulary. -/
theorem certificate_countermodel_exclusive (F : Family.{0})
    (decodeModel : F.Vocab → Json → Except String F.L.Model) (rv : F.Vocab) (j₁ j₂ : Json)
    (hp : F.decodePremises rv j₁ = F.decodePremises rv j₂)
    (hc : F.decodeConclusion rv j₁ = F.decodeConclusion rv j₂)
    (h₁ : CertificateClaim F rv j₁) : ¬ CountermodelClaim F decodeModel rv j₂ := by
  rintro ⟨ps₂, c₂, S, hps₂, hc₂, _, hS, hsat, hn⟩
  obtain ⟨ps₁, c₁, hps₁, hc₁, hall⟩ := h₁
  rw [hp, hps₂] at hps₁
  rw [hc, hc₂] at hc₁
  cases hps₁
  cases hc₁
  exact hn (hall S hS hsat)

/-! ## The checked side: runners -/

/-- The checked side of a family: the runner, its checker, the regenerated
Background and its identity encoding, and the certificate decoder. -/
structure Runner (F : Family.{u}) where
  run : (profiles : List String) → (environment : Json) → F.Vocab → (id kind : String) → Json →
    Except String Json
  checker : (rv : F.Vocab) → Checker F.L (F.env rv)
  stmt : (rv : F.Vocab) → F.L.Formula → (checker rv).Stmt
  background : F.Vocab → List F.L.Formula
  backgroundJson : F.Vocab → List Json
  decodeCertificate : (rv : F.Vocab) → Json → Except String (checker rv).Cert
  certIds : (rv : F.Vocab) → (checker rv).Cert → String × List String × String

namespace Runner
variable {F : Family.{u}} (R : Runner F)

/-- The certificate's identity fields are bound (`Wire.bindingOk`) to the
environment, the regenerated Background followed by the case's premises, and
the case's conclusion. -/
def Bound (profiles : List String) (environment : Json) (rv : F.Vocab) (j : Json)
    (cert : (R.checker rv).Cert) : Prop :=
  ∃ premiseArray : Array Json, (j.getObjValD "premises").getArr? = .ok premiseArray ∧
    Wire.bindingOk profiles environment (R.backgroundJson rv ++ premiseArray.toList)
      (j.getObjValD "conclusion") (R.certIds rv cert).1 (R.certIds rv cert).2.1
      (R.certIds rv cert).2.2 = .ok ()

/-- What a successful, valid certificate run establishes: the premises,
conclusion and certificate decode, the certificate is bound, and the checker
accepts it for Background followed by the premises. -/
def Accepted (profiles : List String) (environment : Json) (rv : F.Vocab) (j : Json) : Prop :=
  ∃ ps c cert, F.decodePremises rv j = .ok ps ∧ F.decodeConclusion rv j = .ok c ∧
    R.decodeCertificate rv (j.getObjValD "certificate") = .ok cert ∧
    R.Bound profiles environment rv j cert ∧
    (R.checker rv).valid cert ((R.background rv ++ ps).map (R.stmt rv)) (R.stmt rv c)

/-- The obligations of a runner, proved per family. -/
structure Sound : Prop where
  stmt_formula : ∀ rv a, (R.checker rv).formula (R.stmt rv a) = a
  intended_admissible : ∀ rv S, F.Intended rv S → F.L.Admissible (F.env rv) S
  background_sound : ∀ rv S, F.Intended rv S → F.L.Sat S (R.background rv)
  run_accepted : ∀ profiles environment rv id j out,
    R.run profiles environment rv id "certificate" j = .ok out →
    out.getObjValD "valid" = .bool true → R.Accepted profiles environment rv j

/-- The family's meaning as a route layer: no new symbols, no premises,
admissibility `Intended`. -/
def layer (hR : R.Sound) (rv : F.Vocab) : Layer F.L Unit :=
  Layer.id (F.env rv) (F.Intended rv) (hR.intended_admissible rv)

theorem background_routeSound (hR : R.Sound) (rv : F.Vocab) :
    BackgroundSound (R.layer hR rv) (R.background rv) :=
  fun _ S hS _ => hR.background_sound rv S hS

/-- The one acceptance theorem of the certificate kind, proved once over any
family and any checker: a certificate case answered with `"valid": true`
decodes, its certificate is bound, and the decoded conclusion holds in every
intended structure satisfying the decoded premises. -/
theorem acceptance (hR : R.Sound) (profiles : List String) (environment : Json) (rv : F.Vocab)
    (id : String) (j out : Json) (h : R.run profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    (∃ cert, R.decodeCertificate rv (j.getObjValD "certificate") = .ok cert ∧
      R.Bound profiles environment rv j cert) ∧ CertificateClaim F rv j := by
  obtain ⟨ps, c, cert, hps, hc, hcert, hb, hvalid⟩ := hR.run_accepted profiles environment rv id j out h hv
  refine ⟨⟨cert, hcert, hb⟩, ps, c, hps, hc, fun S hS hsat => ?_⟩
  have hmap : ((R.background rv ++ ps).map (R.stmt rv)).map (R.checker rv).formula =
      checkedPremises (R.layer hR rv) (R.background rv) () ps := by
    simp only [List.map_map, Function.comp_def, hR.stmt_formula, List.map_id', checkedPremises,
      layer, Layer.id, List.append_nil]
  have := route_acceptance (R.layer hR rv) (R.background rv) (R.background_routeSound hR rv)
    (R.checker rv) () ps c cert _ _ hvalid hmap (hR.stmt_formula rv c)
  exact this.2.1 S hS trivial hsat

end Runner

/-! ## Shared lemmas -/

theorem getObjValD_of_ok {j v : Json} {k : String} (h : j.getObjVal? k = .ok v) :
    j.getObjValD k = v := by
  simp [Json.getObjValD, h, Except.toOption]

theorem valid_field (id : String) (b : Bool) (n : Json) :
    (Wire.ok id [("valid", .bool b), ("background", n)]).getObjValD "valid" = .bool b := rfl

theorem refutes_field (id : String) (b : Bool) :
    (Wire.ok id [("refutes", .bool b)]).getObjValD "refutes" = .bool b := rfl

theorem values_field (id : String) (v : Json) :
    (Wire.ok id [("values", v)]).getObjValD "values" = v := rfl

/-- Each pair of a list zipped with its image is related by the map. -/
theorem mem_zip_map {α β : Type} (f : α → β) :
    ∀ (l : List α) (p : α × β), p ∈ l.zip (l.map f) → p.2 = f p.1
  | [], _, h => nomatch h
  | a :: l, p, h => by
    rcases List.mem_cons.mp h with rfl | h
    · rfl
    · exact mem_zip_map f l p h

/-- The data flag only adds a rejection: what decodes with it decodes to the
same formulas without it. -/
theorem decodeFormulas_data (E : VE.Environment) (j : Json) (data : Bool) (fs : List VE.Formula)
    (h : decodeFormulas E j data = .ok fs) : decodeFormulas E j = .ok fs := by
  cases data
  · exact h
  unfold decodeFormulas at h ⊢
  obtain ⟨js, hjs, h⟩ := bind_ok h
  obtain ⟨fs', hfs, h⟩ := bind_ok h
  obtain ⟨_, hn, h⟩ := bind_ok h
  rw [hjs]; simp only [bind, Except.bind]; rw [hfs]; simp only; rw [hn]
  simp only [Bool.false_and, Bool.false_eq_true, ↓reduceIte, Bool.true_and, pure, Except.pure,
    bind, Except.bind] at h ⊢
  split at h
  · cases h
  · split at h
    · rename_i hc; simp only [hc, ↓reduceIte]; exact h
    · cases h

theorem decodeClosed_data (E : VE.Environment) (j : Json) (data : Bool) (a : VE.Formula)
    (h : decodeClosed E j data = .ok a) : decodeClosed E j = .ok a := by
  cases data
  · exact h
  unfold decodeClosed at h ⊢
  obtain ⟨_, hl, h⟩ := bind_ok h
  obtain ⟨a', ha, h⟩ := bind_ok h
  rw [hl]; simp only [bind, Except.bind]; rw [ha]
  simp only [Bool.false_and, Bool.false_eq_true, ↓reduceIte, Bool.true_and, pure, Except.pure,
    bind, Except.bind] at h ⊢
  split at h
  · cases h
  · split at h
    · rename_i hc; simp only [hc, ↓reduceIte]; exact h
    · cases h

/-- The regenerated Background without its generators: flags, definitions, literals. -/
theorem fullBackground_formulas (rv : RouteVocabulary) :
    (fullBackground rv).map Prod.fst = VE.Data.Background.generate rv.flags ++
      VE.Definitions.expand rv.definitions ++ Background.literals rv.literals := by
  simp [fullBackground, Background.background, List.map_map, Function.comp_def]

/-! ## The FOL and closure meaning -/

/-- The reviewed meaning of a FOL or closure vocabulary (`decodeDataModel_combined`):
string admissible, every defined predicate agreeing with its body, every flag's
functional and total meaning. -/
def RouteIntended (rv : RouteVocabulary) (S : VE.Structure.{u}) : Prop :=
  VE.Definitions.Intended rv.environment rv.definitions rv.literals S ∧
    ∀ f ∈ rv.flags, VE.Data.Background.Intended S f

theorem routeIntended_background (rv : RouteVocabulary) (S : VE.Structure.{u})
    (hS : RouteIntended rv S) : ∀ a ∈ (fullBackground rv).map Prod.fst, a.denote S [] := by
  rw [fullBackground_formulas]
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · rcases List.mem_append.mp ha with ha | ha
    · exact (VE.Data.Background.generate_sat_iff S rv.flags).mpr hS.2 a ha
    · exact (VE.Definitions.faithful rv.definitions
        (VE.Definitions.chain_arity _ _ rv.chain) S).mpr hS.1.2 a ha
  · exact (Background.literals_sat_iff S rv.literals rv.nodup).mpr hS.1.1.2 a ha

/-- The decoded model of a FOL or closure case. -/
def routeModel (rv : RouteVocabulary) (j : Json) : Except String VE.Structure.{0} :=
  match j.getObjVal? "model" with
  | .error e => .error e
  | .ok m => match decodeDataModel rv m with
    | .error e => .error e
    | .ok M => .ok M.asStructure

theorem routeModel_ok (rv : RouteVocabulary) (j m : Json) (M : VE.FiniteModel VE.Bridge.Entity)
    (hm : j.getObjVal? "model" = .ok m) (hM : decodeDataModel rv m = .ok M) :
    routeModel rv j = .ok M.asStructure := by
  simp [routeModel, hm, hM]

/-! ## FOL -/

/-- The FOL family: v0 formulas, the meaning of the whole regenerated Background. -/
def folFamily : Family.{u} where
  L := fol
  Vocab := RouteVocabulary
  env := RouteVocabulary.environment
  Intended := RouteIntended
  decodePremises rv j := do decodeFormulas rv.environment (← j.getObjVal? "premises")
  decodeConclusion rv j := do decodeClosed rv.environment (← j.getObjVal? "conclusion")
  decodeDocument rv j := do decodeFormulas rv.environment (← j.getObjVal? "ast")

/-- `runFol` with the v0 tableau checker and `fullBackground`. -/
def folRunner : Runner folFamily.{u} where
  run := runFol
  checker rv := Checker.tableau rv.environment
  stmt _ a := a
  background rv := (fullBackground rv).map Prod.fst
  backgroundJson rv := ((fullBackground rv).map Prod.fst).map encodeFormula
  decodeCertificate _ := VE.CertificateWire.decodeCertificate
  certIds _ c := (c.environment_id, c.premise_meaning_ids, c.conclusion_meaning_id)

theorem folRunner_run : folRunner.{u}.run = runFol := rfl

theorem runFol_accepted (profiles : List String) (environment : Json) (rv : RouteVocabulary)
    (id : String) (j out : Json) (h : runFol profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    folRunner.{u}.Accepted profiles environment rv j := by
  unfold runFol at h
  simp only [show ("certificate" == "background") = false from rfl,
    show ("certificate" == "evaluate") = false from rfl,
    show ("certificate" == "countermodel") = false from rfl,
    show ("certificate" == "certificate") = true from rfl, Bool.false_eq_true, ↓reduceIte,
    pure_bind] at h
  obtain ⟨pj, hpj, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  obtain ⟨cj, hcj, h⟩ := bind_ok h
  obtain ⟨c, hc, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨certj, hcertj, h⟩ := bind_ok h
  obtain ⟨cert, hcert, h⟩ := bind_ok h
  obtain ⟨arr, harr, h⟩ := bind_ok h
  obtain ⟨cj', hcj', h⟩ := bind_ok h
  obtain ⟨_, hb, h⟩ := bind_ok h
  split at h
  · obtain ⟨_, hx, _⟩ := bind_ok h; cases hx
  cases h
  rw [valid_field] at hv
  cases hvalid : VE.Tableau.checkCertificate rv.environment ((fullBackground rv).map Prod.fst ++ ps) c cert
  · rw [hvalid] at hv; cases hv
  refine ⟨ps, c, cert, ?_, ?_, ?_, ⟨arr, ?_, ?_⟩, ?_⟩
  · show (do decodeFormulas rv.environment (← j.getObjVal? "premises")) = _
    rw [hpj]; exact decodeFormulas_data _ _ _ _ hps
  · show (do decodeClosed rv.environment (← j.getObjVal? "conclusion")) = _
    rw [hcj]; exact decodeClosed_data _ _ _ _ hc
  · rw [getObjValD_of_ok hcertj]; exact hcert
  · rw [getObjValD_of_ok hpj]; exact harr
  · rw [getObjValD_of_ok hcj']; exact hb
  · show VE.Tableau.checkCertificate rv.environment _ c cert = true
    simpa [folRunner] using hvalid

theorem folRunner_sound : folRunner.{u}.Sound where
  stmt_formula _ _ := rfl
  intended_admissible _ _ hS := hS.1.1.1
  background_sound rv S hS := routeIntended_background rv S hS
  run_accepted := runFol_accepted

/-- `runFol`'s certificate kind: a `"valid": true` answer means the decoded
conclusion holds in every structure that is string admissible, agrees with
every definition and satisfies every flag, and satisfies the decoded premises;
the certificate is bound to the environment, Background, premises and
conclusion. -/
theorem runFol_certificate_acceptance (profiles : List String) (environment : Json)
    (rv : RouteVocabulary) (id : String) (j out : Json)
    (h : runFol profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    (∃ cert, VE.CertificateWire.decodeCertificate (j.getObjValD "certificate") = .ok cert ∧
      folRunner.{u}.Bound profiles environment rv j cert) ∧ CertificateClaim folFamily.{u} rv j :=
  folRunner.acceptance folRunner_sound profiles environment rv id j out h hv

/-- `runFol`'s countermodel kind: the decoded model is intended (string
admissible, definitions computed, flags hold), and `refutes` is `true` exactly
when it satisfies the decoded premises and falsifies the decoded conclusion. -/
theorem runFol_countermodel (profiles : List String) (environment : Json) (rv : RouteVocabulary)
    (id : String) (j out : Json) (h : runFol profiles environment rv id "countermodel" j = .ok out) :
    CountermodelAnswer folFamily routeModel rv j out := by
  unfold runFol at h
  simp only [show ("countermodel" == "background") = false from rfl,
    show ("countermodel" == "evaluate") = false from rfl,
    show ("countermodel" == "countermodel") = true from rfl, Bool.false_eq_true, ↓reduceIte,
    pure_bind] at h
  obtain ⟨pj, hpj, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  obtain ⟨cj, hcj, h⟩ := bind_ok h
  obtain ⟨c, hc, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨mj, hmj, h⟩ := bind_ok h
  obtain ⟨M, hM, h⟩ := bind_ok h
  split at h
  rotate_left
  · cases h
  rename_i b hb
  cases h
  have hcm := Budget.refutesF_sound _ M _ (Budget.tableMem_iff _ M) ps c 0 b hb
  refine ⟨ps, c, M.asStructure, b, ?_, ?_, routeModel_ok rv j mj M hmj hM,
    decodeDataModel_combined rv mj M hM, refutes_field _ _, ?_⟩
  rotate_left 2
  · rw [hcm]; exact VE.countermodelCheck_iff M ps c
  · show (do decodeFormulas rv.environment (← j.getObjVal? "premises")) = _
    rw [hpj]; exact decodeFormulas_data _ _ _ _ hps
  · show (do decodeClosed rv.environment (← j.getObjVal? "conclusion")) = _
    rw [hcj]; exact decodeClosed_data _ _ _ _ hc

/-- `runFol`'s evaluate kind: the answered values are the truth of the decoded
formulas in the decoded, intended model. -/
theorem runFol_evaluate (profiles : List String) (environment : Json) (rv : RouteVocabulary)
    (id : String) (j out : Json) (h : runFol profiles environment rv id "evaluate" j = .ok out) :
    EvaluateClaim folFamily routeModel rv j out := by
  unfold runFol at h
  simp only [show ("evaluate" == "background") = false from rfl,
    show ("evaluate" == "evaluate") = true from rfl, Bool.false_eq_true, ↓reduceIte,
    pure_bind] at h
  obtain ⟨aj, haj, h⟩ := bind_ok h
  obtain ⟨fs, hfs, h⟩ := bind_ok h
  split at h
  · obtain ⟨_, hx, _⟩ := bind_ok h; cases hx
  obtain ⟨mj, hmj, h⟩ := bind_ok h
  obtain ⟨M, hM, h⟩ := bind_ok h
  obtain ⟨vs, hvs, h⟩ := bind_ok h
  cases h
  have hv := Budget.valuesF_sound _ M (Budget.tableMem_iff _ M) fs vs hvs
  refine ⟨fs, M.asStructure, vs, ?_, routeModel_ok rv j mj M hmj hM,
    decodeDataModel_combined rv mj M hM, values_field _ _, by simp [hv], fun p hp => ?_⟩
  · show (do decodeFormulas rv.environment (← j.getObjVal? "ast")) = _
    rw [haj]; exact decodeFormulas_data _ _ _ _ hfs
  · rw [hv] at hp
    rw [mem_zip_map _ fs p hp]
    exact VE.eval_iff_denote M [] p.1

/-! ## Closure -/

/-- The closure family: closure formulas over v0 structures, the FOL family's meaning. -/
def closureFamily : Family.{u} where
  L := closure
  Vocab := RouteVocabulary
  env := RouteVocabulary.environment
  Intended := RouteIntended
  decodePremises rv j := do VE.Closure.Bridge.decodeFormulas rv.environment (← j.getObjVal? "premises")
  decodeConclusion _ j := do VE.Closure.Bridge.decodeFormula 64 (← j.getObjVal? "conclusion")
  decodeDocument rv j := do VE.Closure.Bridge.decodeFormulas rv.environment (← j.getObjVal? "ast")

/-- `runClosure` with the closure checker and the embedded `fullBackground`. -/
def closureRunner : Runner closureFamily.{u} where
  run := runClosure
  checker rv := Checker.closure rv.environment
  stmt _ a := a
  background rv := ((fullBackground rv).map Prod.fst).map VE.Closure.embed
  backgroundJson rv := ((fullBackground rv).map Prod.fst).map encodeFormula
  decodeCertificate _ := VE.CertificateWire.decodeClosureCertificate
  certIds _ c := (c.environment_id, c.premise_meaning_ids, c.conclusion_meaning_id)

theorem closureRunner_run : closureRunner.{u}.run = runClosure := rfl

theorem runClosure_accepted (profiles : List String) (environment : Json) (rv : RouteVocabulary)
    (id : String) (j out : Json) (h : runClosure profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    closureRunner.{u}.Accepted profiles environment rv j := by
  unfold runClosure at h
  simp only [show ("certificate" == "background") = false from rfl,
    show ("certificate" == "evaluate") = false from rfl,
    show ("certificate" == "countermodel") = false from rfl,
    show ("certificate" == "certificate") = true from rfl, Bool.false_eq_true, ↓reduceIte,
    pure_bind] at h
  obtain ⟨pj, hpj, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  obtain ⟨cj, hcj, h⟩ := bind_ok h
  obtain ⟨c, hc, h⟩ := bind_ok h
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨certj, hcertj, h⟩ := bind_ok h
  obtain ⟨cert, hcert, h⟩ := bind_ok h
  obtain ⟨arr, harr, h⟩ := bind_ok h
  obtain ⟨cj', hcj', h⟩ := bind_ok h
  obtain ⟨_, hb, h⟩ := bind_ok h
  split at h
  · obtain ⟨_, hx, _⟩ := bind_ok h; cases hx
  cases h
  rw [valid_field] at hv
  cases hvalid : VE.Closure.Tableau.checkCertificate rv.environment
      (((fullBackground rv).map Prod.fst).map VE.Closure.embed ++ ps) c cert
  · rw [hvalid] at hv; cases hv
  refine ⟨ps, c, cert, ?_, ?_, ?_, ⟨arr, ?_, ?_⟩, ?_⟩
  · show (do VE.Closure.Bridge.decodeFormulas rv.environment (← j.getObjVal? "premises")) = _
    rw [hpj]; exact hps
  · show (do VE.Closure.Bridge.decodeFormula 64 (← j.getObjVal? "conclusion")) = _
    rw [hcj]; exact hc
  · rw [getObjValD_of_ok hcertj]; exact hcert
  · rw [getObjValD_of_ok hpj]; exact harr
  · rw [getObjValD_of_ok hcj']; exact hb
  · show VE.Closure.Tableau.checkCertificate rv.environment _ c cert = true
    simpa [closureRunner] using hvalid

theorem closureRunner_sound : closureRunner.{u}.Sound where
  stmt_formula _ _ := rfl
  intended_admissible _ _ hS := hS.1.1.1
  background_sound rv S hS a ha := by
    obtain ⟨b, hb, rfl⟩ := List.mem_map.mp ha
    exact (VE.Closure.conservativity S [] b).mpr (routeIntended_background rv S hS b hb)
  run_accepted := runClosure_accepted

/-- `runClosure`'s certificate kind, with the same meaning as `runFol`'s;
Background is embedded unchanged (`Closure.conservativity`). -/
theorem runClosure_certificate_acceptance (profiles : List String) (environment : Json)
    (rv : RouteVocabulary) (id : String) (j out : Json)
    (h : runClosure profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    (∃ cert, VE.CertificateWire.decodeClosureCertificate (j.getObjValD "certificate") = .ok cert ∧
      closureRunner.{u}.Bound profiles environment rv j cert) ∧
      CertificateClaim closureFamily.{u} rv j :=
  closureRunner.acceptance closureRunner_sound profiles environment rv id j out h hv

/-- `runClosure`'s countermodel kind, with `runFol`'s meaning over closure formulas. -/
theorem runClosure_countermodel (profiles : List String) (environment : Json) (rv : RouteVocabulary)
    (id : String) (j out : Json) (h : runClosure profiles environment rv id "countermodel" j = .ok out) :
    CountermodelAnswer closureFamily routeModel rv j out := by
  unfold runClosure at h
  simp only [show ("countermodel" == "background") = false from rfl,
    show ("countermodel" == "evaluate") = false from rfl,
    show ("countermodel" == "countermodel") = true from rfl, Bool.false_eq_true, ↓reduceIte,
    pure_bind] at h
  obtain ⟨pj, hpj, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  obtain ⟨cj, hcj, h⟩ := bind_ok h
  obtain ⟨c, hc, h⟩ := bind_ok h
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨mj, hmj, h⟩ := bind_ok h
  obtain ⟨M, hM, h⟩ := bind_ok h
  split at h
  rotate_left
  · cases h
  rename_i b hb
  cases h
  have hcm := Budget.refutesC_sound _ M _ (Budget.tableMem_iff _ M) ps c 0 b hb
  refine ⟨ps, c, M.asStructure, b, ?_, ?_, routeModel_ok rv j mj M hmj hM,
    decodeDataModel_combined rv mj M hM, refutes_field _ _, ?_⟩
  rotate_left 2
  · rw [hcm]; exact VE.Closure.countermodelCheck_iff M ps c
  · show (do VE.Closure.Bridge.decodeFormulas rv.environment (← j.getObjVal? "premises")) = _
    rw [hpj]; exact hps
  · show (do VE.Closure.Bridge.decodeFormula 64 (← j.getObjVal? "conclusion")) = _
    rw [hcj]; exact hc

/-- `runClosure`'s evaluate kind, with `runFol`'s meaning over closure formulas. -/
theorem runClosure_evaluate (profiles : List String) (environment : Json) (rv : RouteVocabulary)
    (id : String) (j out : Json) (h : runClosure profiles environment rv id "evaluate" j = .ok out) :
    EvaluateClaim closureFamily routeModel rv j out := by
  unfold runClosure at h
  simp only [show ("evaluate" == "background") = false from rfl,
    show ("evaluate" == "evaluate") = true from rfl, Bool.false_eq_true, ↓reduceIte,
    pure_bind] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨aj, haj, h⟩ := bind_ok h
  obtain ⟨fs, hfs, h⟩ := bind_ok h
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  obtain ⟨mj, hmj, h⟩ := bind_ok h
  obtain ⟨M, hM, h⟩ := bind_ok h
  obtain ⟨vs, hvs, h⟩ := bind_ok h
  cases h
  have hv := Budget.valuesC_sound _ M (Budget.tableMem_iff _ M) fs vs hvs
  refine ⟨fs, M.asStructure, vs, ?_, routeModel_ok rv j mj M hmj hM,
    decodeDataModel_combined rv mj M hM, values_field _ _, by simp [hv], fun p hp => ?_⟩
  · show (do VE.Closure.Bridge.decodeFormulas rv.environment (← j.getObjVal? "ast")) = _
    rw [haj]; exact hfs
  · rw [hv] at hp
    rw [mem_zip_map _ fs p hp]
    exact VE.Closure.eval_iff_denote M [] p.1

/-! ## Order -/

/-- The order family: order formulas; admissible and declared literals distinct. -/
def orderFamily : Family.{u} where
  L := order
  Vocab := RouteOrderVocabulary
  env rv := rv.vocabulary.environment
  Intended rv S := Background.OrderStringAdmissible rv.vocabulary.environment rv.literals S
  decodePremises rv j := do
    VE.Order.Wire.decodeFormulas rv.vocabulary.environment (← j.getObjVal? "premises")
  decodeConclusion _ j := do VE.Order.Wire.decodeFormula 64 (← j.getObjVal? "conclusion")
  decodeDocument rv j := do VE.Order.Wire.decodeFormulas rv.vocabulary.environment (← j.getObjVal? "ast")

/-- `runOrder` with the order checker and the order form of `literals`. -/
def orderRunner : Runner orderFamily.{u} where
  run := runOrder
  checker rv := Checker.order rv.vocabulary.environment
  stmt _ a := a
  background rv := Background.orderLiterals rv.literals
  backgroundJson rv := (Background.literals rv.literals).map encodeFormula
  decodeCertificate _ := VE.Order.Wire.decodeCertificate
  certIds _ c := (c.environment_id, c.premise_meaning_ids, c.conclusion_meaning_id)

theorem orderRunner_run : orderRunner.{u}.run = runOrder := rfl

theorem runOrder_accepted (profiles : List String) (environment : Json) (rv : RouteOrderVocabulary)
    (id : String) (j out : Json) (h : runOrder profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    orderRunner.{u}.Accepted profiles environment rv j := by
  unfold runOrder at h
  simp only [show ("certificate" == "evaluate") = false from rfl,
    show ("certificate" == "countermodel") = false from rfl,
    show ("certificate" == "certificate") = true from rfl, Bool.false_eq_true, ↓reduceIte,
    pure_bind] at h
  obtain ⟨pj, hpj, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  obtain ⟨cj, hcj, h⟩ := bind_ok h
  obtain ⟨c, hc, h⟩ := bind_ok h
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨certj, hcertj, h⟩ := bind_ok h
  obtain ⟨cert, hcert, h⟩ := bind_ok h
  obtain ⟨arr, harr, h⟩ := bind_ok h
  obtain ⟨cj', hcj', h⟩ := bind_ok h
  obtain ⟨_, hb, h⟩ := bind_ok h
  split at h
  · obtain ⟨_, hx, _⟩ := bind_ok h; cases hx
  cases h
  rw [valid_field] at hv
  cases hvalid : VE.Order.Tableau.checkCertificate rv.vocabulary.environment
      (Background.orderLiterals rv.literals ++ ps) c cert
  · rw [hvalid] at hv; cases hv
  refine ⟨ps, c, cert, ?_, ?_, ?_, ⟨arr, ?_, ?_⟩, ?_⟩
  · show (do VE.Order.Wire.decodeFormulas rv.vocabulary.environment (← j.getObjVal? "premises")) = _
    rw [hpj]; exact hps
  · show (do VE.Order.Wire.decodeFormula 64 (← j.getObjVal? "conclusion")) = _
    rw [hcj]; exact hc
  · rw [getObjValD_of_ok hcertj]; exact hcert
  · rw [getObjValD_of_ok hpj]; exact harr
  · rw [getObjValD_of_ok hcj']; exact hb
  · show VE.Order.Tableau.checkCertificate rv.vocabulary.environment _ c cert = true
    simpa [orderRunner] using hvalid

theorem orderRunner_sound : orderRunner.{u}.Sound where
  stmt_formula _ _ := rfl
  intended_admissible _ _ hS := hS.1
  background_sound rv S hS := (Background.orderLiterals_sat_iff S rv.literals rv.nodup).mpr hS.2
  run_accepted := runOrder_accepted

/-- `runOrder`'s certificate kind: a `"valid": true` answer means the decoded
conclusion holds in every admissible order structure in which the declared
literals are distinct and the decoded premises hold. -/
theorem runOrder_certificate_acceptance (profiles : List String) (environment : Json)
    (rv : RouteOrderVocabulary) (id : String) (j out : Json)
    (h : runOrder profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    (∃ cert, VE.Order.Wire.decodeCertificate (j.getObjValD "certificate") = .ok cert ∧
      orderRunner.{u}.Bound profiles environment rv j cert) ∧ CertificateClaim orderFamily.{u} rv j :=
  orderRunner.acceptance orderRunner_sound profiles environment rv id j out h hv

/-- The order model decoder's last check: the tables are a valid presentation. -/
theorem decodeOrderModel_validFast (v : VE.Order.Vocabulary) (j : Json)
    (d : VE.Order.ModelData VE.Order.Wire.Entity) (h : Decode.decodeOrderModel v j = .ok d) :
    Decode.validOrderFast v d = true := by
  unfold Decode.decodeOrderModel at h
  repeat (first
    | (obtain ⟨_, _, h⟩ := bind_ok h)
    | ((try dsimp only at h); split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)))
  cases h
  assumption

/-- The decoded model of an order case. -/
def orderModel (rv : RouteOrderVocabulary) (j : Json) : Except String VE.Order.Structure.{0} :=
  match j.getObjVal? "model" with
  | .error e => .error e
  | .ok m => match decodeOrderModel rv m with
    | .error e => .error e
    | .ok d => .ok d.toModel.asStructure

/-- A decoded order model is admissible for the vocabulary and its declared
literals are distinct. -/
theorem decodeOrderModel_intended (rv : RouteOrderVocabulary) (j : Json)
    (d : VE.Order.ModelData VE.Order.Wire.Entity) (h : decodeOrderModel rv j = .ok d) :
    orderFamily.Intended rv d.toModel.asStructure := by
  have hl := decodeOrderModel_valid rv j d h
  unfold decodeOrderModel at h
  obtain ⟨d', hd, h⟩ := bind_ok h
  split at h
  · rename_i hlits
    have hdd : d' = d := by cases h; rfl
    subst hdd
    have hv := (VE.Order.validModel_iff _ d').mp
      ((Decode.validOrderFast_eq _ d').symm.trans (decodeOrderModel_validFast _ _ d' hd))
    exact ⟨hv, Background.orderLiteralsValid_sound _ rv.literals rv.nodup hl⟩
  · cases h

theorem orderModel_ok (rv : RouteOrderVocabulary) (j m : Json) (d : VE.Order.ModelData VE.Order.Wire.Entity)
    (hm : j.getObjVal? "model" = .ok m) (hd : decodeOrderModel rv m = .ok d) :
    orderModel rv j = .ok d.toModel.asStructure := by
  simp [orderModel, hm, hd]

/-- A `for` loop over a list in `Except` whose body only yields succeeds only if
the body succeeds on every element. -/
theorem forIn_yield_ok {α : Type} (f : α → PUnit.{1} → Except String (ForInStep PUnit.{1}))
    (hy : ∀ x r s, f x r = .ok s → s = .yield PUnit.unit) :
    ∀ (l : List α) (u : PUnit.{1}), forIn l PUnit.unit f = .ok u →
      ∀ x ∈ l, f x PUnit.unit = .ok (.yield PUnit.unit)
  | [], _, _, x, hx => nomatch hx
  | a :: l, u, h, x, hx => by
    rw [List.forIn_cons] at h
    obtain ⟨s, hs, h⟩ := bind_ok h
    have hsy := hy a _ s hs
    subst hsy
    rcases List.mem_cons.mp hx with rfl | hx
    · exact hs
    · exact forIn_yield_ok f hy l u h x hx

/-- The order family has no definitions: `decodeOrderVocabulary` rejects every
predicate declaration that carries a `defined` payload. -/
theorem orderVocabulary_no_definitions (v : Json) (rv : RouteOrderVocabulary)
    (h : decodeOrderVocabulary v = .ok rv) (ps : List (String × Json))
    (hps : VE.Bridge.fields (v.getObjValD "predicates") = .ok ps) :
    ∀ p ∈ ps, (p.2.getObjVal? "defined").isOk = false := by
  unfold decodeOrderVocabulary at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨pj, hpj, h⟩ := bind_ok h
  obtain ⟨ps', hps', h⟩ := bind_ok h
  obtain ⟨_, hfor, _⟩ := bind_ok h
  rw [getObjValD_of_ok hpj, hps'] at hps
  cases hps
  intro p hp
  have := forIn_yield_ok _ ?_ ps _ hfor p hp
  rotate_left
  · rintro ⟨_, entry⟩ r s hs
    dsimp only at hs
    split at hs
    · obtain ⟨_, hx, _⟩ := bind_ok hs; cases hx
    · cases hs; rfl
  obtain ⟨n, entry⟩ := p
  dsimp only at this ⊢
  cases hd : (entry.getObjVal? "defined").isOk
  · rfl
  · rw [hd] at this
    simp only [↓reduceIte] at this
    obtain ⟨_, hx, _⟩ := bind_ok this; cases hx

/-- `runOrder`'s countermodel kind: the decoded model is an admissible order
structure with distinct literals, and `refutes` is `true` exactly when it
satisfies the decoded premises and falsifies the decoded conclusion. -/
theorem runOrder_countermodel (profiles : List String) (environment : Json) (rv : RouteOrderVocabulary)
    (id : String) (j out : Json) (h : runOrder profiles environment rv id "countermodel" j = .ok out) :
    CountermodelAnswer orderFamily orderModel rv j out := by
  unfold runOrder at h
  simp only [show ("countermodel" == "evaluate") = false from rfl,
    show ("countermodel" == "countermodel") = true from rfl, Bool.false_eq_true, ↓reduceIte,
    pure_bind] at h
  obtain ⟨pj, hpj, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  obtain ⟨cj, hcj, h⟩ := bind_ok h
  obtain ⟨c, hc, h⟩ := bind_ok h
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨mj, hmj, h⟩ := bind_ok h
  obtain ⟨d, hd, h⟩ := bind_ok h
  split at h
  rotate_left
  · cases h
  rename_i b hb
  cases h
  have hcm := Budget.refutesB_sortOrderData_sound d _ _ ps c 0 b hb
  refine ⟨ps, c, d.toModel.asStructure, b, ?_, ?_, orderModel_ok rv j mj d hmj hd,
    decodeOrderModel_intended rv mj d hd, refutes_field _ _, ?_⟩
  rotate_left 2
  · rw [hcm]; exact VE.Order.countermodelCheck_iff d.toModel ps c
  · show (do VE.Order.Wire.decodeFormulas rv.vocabulary.environment (← j.getObjVal? "premises")) = _
    rw [hpj]; exact hps
  · show (do VE.Order.Wire.decodeFormula 64 (← j.getObjVal? "conclusion")) = _
    rw [hcj]; exact hc

/-- `runOrder`'s evaluate kind: the answered values are the truth of the decoded
formulas in the decoded model. -/
theorem runOrder_evaluate (profiles : List String) (environment : Json) (rv : RouteOrderVocabulary)
    (id : String) (j out : Json) (h : runOrder profiles environment rv id "evaluate" j = .ok out) :
    EvaluateClaim orderFamily orderModel rv j out := by
  unfold runOrder at h
  simp only [show ("evaluate" == "evaluate") = true from rfl, ↓reduceIte, pure_bind] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨aj, haj, h⟩ := bind_ok h
  obtain ⟨fs, hfs, h⟩ := bind_ok h
  split at h <;> try (obtain ⟨_, hx, _⟩ := bind_ok h; cases hx)
  obtain ⟨mj, hmj, h⟩ := bind_ok h
  obtain ⟨d, hd, h⟩ := bind_ok h
  obtain ⟨vs, hvs, h⟩ := bind_ok h
  cases h
  have hv := Budget.orderValues_sorted_sound d _ fs vs hvs
  refine ⟨fs, d.toModel.asStructure, vs, ?_, orderModel_ok rv j mj d hmj hd,
    decodeOrderModel_intended rv mj d hd, values_field _ _, by simp [hv], fun p hp => ?_⟩
  · show (do VE.Order.Wire.decodeFormulas rv.vocabulary.environment (← j.getObjVal? "ast")) = _
    rw [haj]; exact hfs
  · rw [hv] at hp
    rw [mem_zip_map _ fs p hp]
    exact VE.Order.eval_iff_denote d.toModel [] p.1

end VE.Route.WireSound
