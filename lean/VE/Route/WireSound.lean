import VE.Route.Wire

/-! One acceptance theorem for the `route` runners `Wire.runFol`,
`Wire.runClosure` and `Wire.runOrder` (docs/CONSOLIDATION-PLAN.md step 2a).

What a reviewer reads instead of the runners is a `Family` (a logic, a
vocabulary type, its typing environment, what the vocabulary decoder
establishes, the reviewed meaning `Intended` of a vocabulary and the same
meaning as a route `Layer`, and the decoders of a case's premises, conclusion
and document) and four claims over it:

* `CertificateClaim`: the decoded conclusion holds in every intended structure
  satisfying the decoded premises;
* `BaseClaim`: for premises and conclusion over the layer's input vocabulary,
  the conclusion holds in every structure admissible below the layer that
  satisfies the premises (unique expansion, `route_base`);
* `CountermodelAnswer`: the decoded model is intended, and the answer's
  `refutes` is `true` exactly when it satisfies the decoded premises and
  falsifies the decoded conclusion (`CountermodelClaim` is the refuting case);
* `EvaluateClaim`: each answered value is the truth of the corresponding
  decoded formula in the decoded, intended model.

The checked side of a family is a `Runner`: the runner function, its checker
and the regenerated Background. `Runner.acceptance` is proved once, over any
family and any `Checker`, through `route_intended` and `route_base` on the
family's layer, with `BackgroundSound` of that layer as an obligation. The three
instances `folRunner`, `closureRunner` and `orderRunner` have `runFol`,
`runClosure` and `runOrder` as their `run`, by `rfl`; each discharges
`Runner.Sound` by inverting the runner's binds, so a successful certificate
case whose `"valid"` field is `true` yields the source-decode, binding and
checker conjuncts.

The meanings: the FOL and closure families read `Definitions.Intended` (string
admissible, every defined predicate agreeing with its body) and the flags'
`Data.Background.Intended` (functional and total tables), the meaning
`decodeDataModel_combined` states; this is the meaning of the whole regenerated
Background `fullBackground` (flags, definitions, literals). Their layer is
`fullLayer` (plan step 2a, item 1): the definitions layer composed over the
identity layer of `BaseAdmissible` (structurally admissible without the
defined predicates, literals distinct, flags hold), with
`fullLayer_background_sound`. Composing needs one decoder fact, `FlagsBase`:
no flag names a defined predicate, so forgetting the defined tables keeps the
flags (`Norms.FlaggedSpec.decodeVocabulary_flag_not_defined`, discharged at
`Route.Run.runCase`). The closure family reads the same layer over closure
formulas (`Layer.toClosure`). The order family reads `OrderStringAdmissible`
(admissible, declared literals distinct) and its identity layer: a
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
  /-- What the vocabulary decoder establishes beyond the record's own fields. -/
  Decoded : Vocab → Prop
  /-- The reviewed meaning of a vocabulary: admissible, flags, definitions, literals. -/
  Intended : Vocab → L.Model → Prop
  /-- The same meaning as a route layer: the structures admissible below it, the
  layers' premises, restriction and unique expansion. -/
  layer : (rv : Vocab) → Decoded rv → Layer L Unit
  decodePremises : Vocab → Json → Except String (List L.Formula)
  decodeConclusion : Vocab → Json → Except String L.Formula
  /-- The formulas of an `evaluate` case. -/
  decodeDocument : Vocab → Json → Except String (List L.Formula)

/-- The family's layer is its meaning: it ends at the family's environment, and
its admissible output structures meeting its meaning are the intended ones. -/
structure Family.Sound (F : Family.{u}) : Prop where
  layer_env : ∀ rv hd, (F.layer rv hd).E_out = F.env rv
  layer_intended : ∀ rv hd S,
    F.Intended rv S ↔ (F.layer rv hd).Admissible_out S ∧ (F.layer rv hd).Intended () S

/-- An accepted certificate case: the decoded conclusion holds in every
intended structure that satisfies the decoded premises. -/
def CertificateClaim (F : Family.{u}) (rv : F.Vocab) (j : Json) : Prop :=
  ∃ ps c, F.decodePremises rv j = .ok ps ∧ F.decodeConclusion rv j = .ok c ∧
    ∀ S, F.Intended rv S → F.L.Sat S ps → F.L.Holds S c

/-- An accepted certificate case below the family's layer (unique expansion):
when the decoded premises and conclusion are over the layer's input vocabulary,
the conclusion holds in every structure admissible below the layer that
satisfies the premises. -/
def BaseClaim (F : Family.{u}) (rv : F.Vocab) (hd : F.Decoded rv) (j : Json) : Prop :=
  ∃ ps c, F.decodePremises rv j = .ok ps ∧ F.decodeConclusion rv j = .ok c ∧
    ((∀ a ∈ ps, F.L.WellFormed (F.layer rv hd).E_in a) → F.L.WellFormed (F.layer rv hd).E_in c →
      ∀ S₀, (F.layer rv hd).Admissible_in S₀ → F.L.Sat S₀ ps → F.L.Holds S₀ c)

/-- Every structure admissible below the family's layer has exactly one
intended expansion. -/
theorem Family.Sound.expands_intended {F : Family.{u}} (hF : F.Sound) (rv : F.Vocab)
    (hd : F.Decoded rv) (S₀ : F.L.Model) (h₀ : (F.layer rv hd).Admissible_in S₀) :
    Unique fun S => (F.layer rv hd).restrict S = S₀ ∧ F.Intended rv S := by
  obtain ⟨S, ⟨hr, ha, hp⟩, hu⟩ := (F.layer rv hd).expands () S₀ h₀
  refine ⟨S, ⟨hr, (hF.layer_intended rv hd S).mpr ⟨ha, ((F.layer rv hd).faithful () S ha).mp hp⟩⟩,
    fun S' ⟨hr', hi'⟩ => ?_⟩
  obtain ⟨ha', hi''⟩ := (hF.layer_intended rv hd S').mp hi'
  exact hu S' ⟨hr', ha', ((F.layer rv hd).faithful () S' ha').mpr hi''⟩

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
  family : F.Sound
  stmt_formula : ∀ rv a, (R.checker rv).formula (R.stmt rv a) = a
  background_sound : ∀ rv hd, BackgroundSound (F.layer rv hd) (R.background rv)
  run_accepted : ∀ profiles environment rv id j out,
    R.run profiles environment rv id "certificate" j = .ok out →
    out.getObjValD "valid" = .bool true → R.Accepted profiles environment rv j

/-- The one acceptance theorem of the certificate kind, proved once over any
family and any checker through `route_intended` and `route_base` on the
family's layer: a certificate case answered with `"valid": true` decodes, its
certificate is bound, the decoded conclusion holds in every intended structure
satisfying the decoded premises, and (unique expansion) in every structure
admissible below the layer that satisfies them. The checker's premise list
(Background, then the case's premises) is part of the route's (Background, the
layer's premises, the case's premises), so the checked entailment is the
route's. -/
theorem acceptance (hR : R.Sound) (profiles : List String) (environment : Json) (rv : F.Vocab)
    (hd : F.Decoded rv) (id : String) (j out : Json)
    (h : R.run profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    (∃ cert, R.decodeCertificate rv (j.getObjValD "certificate") = .ok cert ∧
      R.Bound profiles environment rv j cert) ∧ CertificateClaim F rv j ∧ BaseClaim F rv hd j := by
  obtain ⟨ps, c, cert, hps, hc, hcert, hb, hvalid⟩ := hR.run_accepted profiles environment rv id j out h hv
  have hsound := (R.checker rv).sound cert _ _ hvalid
  simp only [List.map_map, Function.comp_def, hR.stmt_formula, List.map_id'] at hsound
  let l := F.layer rv hd
  have hbg := hR.background_sound rv hd
  have he : F.L.Entails l.E_out (checkedPremises l (R.background rv) () ps) c := by
    rw [hR.family.layer_env rv hd]
    intro S hS hs
    refine hsound S hS fun a ha => hs a ?_
    rcases List.mem_append.mp ha with ha | ha
    · exact List.mem_append_left _ (List.mem_append_left _ ha)
    · exact List.mem_append_right _ ha
  refine ⟨⟨cert, hcert, hb⟩, ⟨ps, c, hps, hc, fun S hS hsat => ?_⟩, ps, c, hps, hc, ?_⟩
  · obtain ⟨ha, hi⟩ := (hR.family.layer_intended rv hd S).mp hS
    exact route_intended l (R.background rv) hbg () ps c he S ha hi hsat
  · exact fun hwp hwc => route_base l (R.background rv) hbg () ps c hwp hwc he

end Runner

/-! ## Shared lemmas -/

theorem getObjValD_of_ok {j v : Json} {k : String} (h : j.getObjVal? k = .ok v) :
    j.getObjValD k = v := by
  simp [Json.getObjValD, h, Except.toOption]

theorem valid_field (id : String) (b : Bool) (n : Json) :
    (Wire.ok id [("valid", .bool b), ("background", n)]).getObjValD "valid" = .bool b := rfl

theorem valid_field_steps (id : String) (b : Bool) (n s : Json) :
    (Wire.ok id [("valid", .bool b), ("background", n), ("steps", s)]).getObjValD "valid" = .bool b := rfl

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

/-! ## The composed layer -/

/-- A layer cut down to the structures satisfying `P` below and above it;
restriction must preserve `P` on admissible output structures. -/
def _root_.VE.Route.Layer.within {L : Semantics.{u}} {Doc : Type} (l : Layer L Doc)
    (P : L.Model → Prop) (hP : ∀ S, l.Admissible_out S → (P (l.restrict S) ↔ P S)) :
    Layer L Doc where
  E_in := l.E_in
  E_out := l.E_out
  extends_env := l.extends_env
  premises := l.premises
  premises_wellFormed := l.premises_wellFormed
  Admissible_in S := l.Admissible_in S ∧ P S
  Admissible_out S := l.Admissible_out S ∧ P S
  admissible_out S h := l.admissible_out S h.1
  restrict := l.restrict
  restrict_admissible S h := ⟨l.restrict_admissible S h.1, (hP S h.1).mpr h.2⟩
  restrict_holds S a h := l.restrict_holds S a h.1
  Intended := l.Intended
  faithful d S h := l.faithful d S h.1
  expands d S₀ h := by
    obtain ⟨S, ⟨hr, ha, hp⟩, hu⟩ := l.expands d S₀ h.1
    refine ⟨S, ⟨hr, ⟨ha, (hP S ha).mp (by rw [hr]; exact h.2)⟩, hp⟩, fun S' hS' => ?_⟩
    exact hu S' ⟨hS'.1, hS'.2.1.1, hS'.2.2⟩

/-- What `decodeVocabulary` establishes beyond the record: no functional or
total flag names a defined predicate (`Defined predicates cannot carry
functional or total flags`; `Norms.FlaggedSpec.decodeVocabulary_flag_not_defined`). -/
def FlagsBase (rv : RouteVocabulary) : Prop :=
  ∀ f ∈ rv.flags, ∀ d ∈ rv.definitions, f.name ≠ d.name

/-- Every flag's functional and total meaning. -/
def FlagsHold (rv : RouteVocabulary) (S : VE.Structure.{u}) : Prop :=
  ∀ f ∈ rv.flags, VE.Data.Background.Intended S f

/-- Admissibility below the definitions: structurally admissible over the
vocabulary without its defined predicates, literals distinct, flags hold. -/
def BaseAdmissible (rv : RouteVocabulary) (S : VE.Structure.{u}) : Prop :=
  S.Admissible (VE.Definitions.hide rv.environment (VE.Definitions.names rv.definitions)) ∧
    Background.LiteralsDistinct S rv.literals ∧ FlagsHold rv S

/-- Typing is monotone in the declared sorts. -/
theorem wellFormed_sorts {E E' : VE.Environment} (hs : ∀ s ∈ E.sorts, s ∈ E'.sorts)
    (hp : E'.predicates = E.predicates) (hc : E'.constants = E.constants) :
    ∀ (a : VE.Formula) (Γ : List String), a.WellFormed E Γ → a.WellFormed E' Γ
  | .top, _, h | .bottom, _, h => h
  | .unary _ t, Γ, h => by
    simpa [VE.Formula.WellFormed, hp, VE.Definitions.sortOf_congr hc] using h
  | .binary _ t u, Γ, h => by
    simpa [VE.Formula.WellFormed, hp, VE.Definitions.sortOf_congr hc] using h
  | .eq t u, Γ, h => by
    simpa [VE.Formula.WellFormed, VE.Definitions.sortOf_congr hc] using h
  | .not a, Γ, h => wellFormed_sorts hs hp hc a Γ h
  | .and a b, Γ, h | .or a b, Γ, h | .implies a b, Γ, h =>
    ⟨wellFormed_sorts hs hp hc a Γ h.1, wellFormed_sorts hs hp hc b Γ h.2⟩
  | .all s a, Γ, h | .ex s a, Γ, h => ⟨hs s h.1, wellFormed_sorts hs hp hc a (s :: Γ) h.2⟩

/-- The definitions stay a checked chain over `RouteVocabulary.environment`,
which only adds `$string` to the sorts when a flag mentions it. -/
theorem chain_sorts (E : VE.Environment) (xs : List String) :
    ∀ ds, VE.Definitions.Chain E ds → VE.Definitions.Chain { E with sorts := E.sorts ++ xs } ds
  | [], _ => trivial
  | d :: ds, h =>
    ⟨{ sorts := rfl
       constants := rfl
       fresh := h.1.fresh
       declared := h.1.declared
       others := h.1.others
       arity := h.1.arity
       args := fun s hs => by
         show s ∈ E.sorts ++ xs; exact List.mem_append_left _ (h.1.args s hs)
       body := wellFormed_sorts (E := VE.Definitions.hide E _)
         (E' := VE.Definitions.hide { E with sorts := E.sorts ++ xs } _)
         (fun s hs => by show s ∈ E.sorts ++ xs; exact List.mem_append_left _ hs) rfl rfl _ _ h.1.body },
      chain_sorts E xs ds h.2⟩

theorem chain_environment (rv : RouteVocabulary) :
    VE.Definitions.Chain rv.environment rv.definitions :=
  chain_sorts _ _ _ rv.chain

/-- The definitions layer of the route (`Definitions.routeLayer`) over
`RouteVocabulary.environment`. -/
def definitionsLayer (rv : RouteVocabulary) : Layer fol.{u} Unit :=
  VE.Definitions.routeLayer rv.environment rv.definitions (chain_environment rv) rv.literals

theorem flagsHold_forget (rv : RouteVocabulary) (hd : FlagsBase rv) (S : VE.Structure.{u}) :
    FlagsHold rv (VE.Definitions.forget (VE.Definitions.names rv.definitions) S) ↔ FlagsHold rv S := by
  have hn : ∀ f ∈ rv.flags, f.name ∉ VE.Definitions.names rv.definitions := by
    intro f hf hm
    obtain ⟨d, hdm, hdn⟩ := List.mem_map.mp hm
    exact hd f hf d hdm hdn.symm
  apply forall₂_congr
  intro f hf
  simp [VE.Data.Background.Intended, VE.Data.Background.Functional, VE.Data.Background.Total,
    VE.Definitions.forget, hn f hf]

theorem definitionsLayer_restrict (rv : RouteVocabulary) (S : VE.Structure.{u}) :
    (definitionsLayer rv).restrict S = VE.Definitions.forget (VE.Definitions.names rv.definitions) S :=
  (VE.Definitions.chainLayer (Doc := Unit) rv.environment _ (VE.Definitions.literalsFree rv.literals)
    rv.definitions (chain_environment rv)).restrict S

/-- The composed layer of the FOL route (docs/CONSOLIDATION-PLAN.md step 2a,
item 1): the definitions layer, cut down to the structures whose flags hold,
composed over the identity layer of `BaseAdmissible` on the vocabulary without
its defined predicates. -/
def fullLayer (rv : RouteVocabulary) (hd : FlagsBase rv) : Layer fol.{u} Unit :=
  let c := VE.Definitions.chainLayer (Doc := Unit) rv.environment _
    (VE.Definitions.literalsFree rv.literals) rv.definitions (chain_environment rv)
  Layer.comp
    (Layer.id (L := fol) (VE.Definitions.hide rv.environment (VE.Definitions.names rv.definitions))
      (BaseAdmissible rv) (fun _ h => h.1))
    ((definitionsLayer rv).within (FlagsHold rv) fun S _ => by
      rw [definitionsLayer_restrict]; exact flagsHold_forget rv hd S)
    c.E_in
    (fun S => by
      show (c.layer.Admissible_in S ∧ FlagsHold rv S) ↔ BaseAdmissible rv S
      rw [c.Admissible_in]; exact and_assoc)

theorem fullLayer_E_out (rv : RouteVocabulary) (hd : FlagsBase rv) :
    (fullLayer.{u} rv hd).E_out = rv.environment := by
  show (VE.Definitions.chainLayer (Doc := Unit) rv.environment _
    (VE.Definitions.literalsFree.{u} rv.literals) rv.definitions (chain_environment rv)).layer.E_out = _
  rw [VE.Definitions.ChainLayer.E_out, VE.Definitions.hide_nil]

theorem fullLayer_premises (rv : RouteVocabulary) (hd : FlagsBase rv) :
    (fullLayer.{u} rv hd).premises () = VE.Definitions.expand rv.definitions :=
  (VE.Definitions.chainLayer (Doc := Unit) rv.environment _
    (VE.Definitions.literalsFree.{u} rv.literals) rv.definitions (chain_environment rv)).premises ()

theorem fullLayer_admissible_in (rv : RouteVocabulary) (hd : FlagsBase rv) (S : VE.Structure.{u}) :
    (fullLayer rv hd).Admissible_in S ↔ BaseAdmissible rv S :=
  Iff.rfl

theorem fullLayer_admissible_out (rv : RouteVocabulary) (hd : FlagsBase rv) (S : VE.Structure.{u}) :
    (fullLayer rv hd).Admissible_out S ↔
      Background.StringAdmissible rv.environment rv.literals S ∧ FlagsHold rv S := by
  show (VE.Definitions.chainLayer (Doc := Unit) rv.environment _
    (VE.Definitions.literalsFree rv.literals) rv.definitions (chain_environment rv)).layer.Admissible_out S
      ∧ FlagsHold rv S ↔ _
  rw [VE.Definitions.ChainLayer.Admissible_out, VE.Definitions.hide_nil]; rfl

theorem fullLayer_restrict (rv : RouteVocabulary) (hd : FlagsBase rv) (S : VE.Structure.{u}) :
    (fullLayer rv hd).restrict S = VE.Definitions.forget (VE.Definitions.names rv.definitions) S :=
  definitionsLayer_restrict rv S

/-- The composed layer's meaning is `RouteIntended`. -/
theorem fullLayer_intended (rv : RouteVocabulary) (hd : FlagsBase rv) (S : VE.Structure.{u}) :
    RouteIntended rv S ↔ (fullLayer rv hd).Admissible_out S ∧ (fullLayer rv hd).Intended () S := by
  have hfa : ∀ ha : (fullLayer rv hd).Admissible_out S,
      (fullLayer rv hd).Intended () S ↔ ∀ d ∈ rv.definitions, VE.Definitions.Agrees S d := fun ha => by
    rw [← (fullLayer rv hd).faithful () S ha, fullLayer_premises]
    exact VE.Definitions.faithful _ (VE.Definitions.chain_arity _ _ rv.chain) S
  constructor
  · intro hS
    have ha := (fullLayer_admissible_out rv hd S).mpr ⟨hS.1.1, hS.2⟩
    exact ⟨ha, (hfa ha).mpr hS.1.2⟩
  · rintro ⟨ha, hi⟩
    obtain ⟨hs, hf⟩ := (fullLayer_admissible_out rv hd S).mp ha
    exact ⟨⟨hs, (hfa ha).mp hi⟩, hf⟩

/-- Background holds on the composed layer: flags and literals by its
admissibility, the definitions by its premises. -/
theorem fullLayer_background_sound (rv : RouteVocabulary) (hd : FlagsBase rv) :
    BackgroundSound (fullLayer.{u} rv hd) ((fullBackground rv).map Prod.fst) := by
  intro _ S hS hp
  exact routeIntended_background rv S ((fullLayer_intended rv hd S).mpr
    ⟨hS, ((fullLayer rv hd).faithful () S hS).mp hp⟩)

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
  Decoded := FlagsBase
  Intended := RouteIntended
  layer := fullLayer
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
  rw [valid_field_steps] at hv
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

theorem folFamily_sound : folFamily.{u}.Sound where
  layer_env := fullLayer_E_out
  layer_intended := fullLayer_intended

theorem folRunner_sound : folRunner.{u}.Sound where
  family := folFamily_sound
  stmt_formula _ _ := rfl
  background_sound := fullLayer_background_sound
  run_accepted := runFol_accepted

/-- `runFol`'s certificate kind: a `"valid": true` answer means the decoded
conclusion holds in every structure that is string admissible, agrees with
every definition and satisfies every flag, and satisfies the decoded premises;
for premises and conclusion without defined predicates, it holds in every
`BaseAdmissible` structure satisfying the premises (through its unique
expansion by the definitions); the certificate is bound to the environment,
Background, premises and conclusion. -/
theorem runFol_certificate_acceptance (profiles : List String) (environment : Json)
    (rv : RouteVocabulary) (hd : FlagsBase rv) (id : String) (j out : Json)
    (h : runFol profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    (∃ cert, VE.CertificateWire.decodeCertificate (j.getObjValD "certificate") = .ok cert ∧
      folRunner.{u}.Bound profiles environment rv j cert) ∧ CertificateClaim folFamily.{u} rv j ∧
      BaseClaim folFamily.{u} rv hd j :=
  folRunner.acceptance folRunner_sound profiles environment rv hd id j out h hv

/-- `runFol`'s countermodel kind: the decoded model is intended (string
admissible, definitions computed, flags hold), and `refutes` is `true` exactly
when it satisfies the decoded premises and falsifies the decoded conclusion. -/
theorem runFol_countermodel (profiles : List String) (environment : Json) (rv : RouteVocabulary)
    (id : String) (j out : Json) (h : runFol profiles environment rv id "countermodel" j = .ok out) :
    CountermodelAnswer folFamily routeModel rv j out := by
  unfold runFol at h
  simp only [show ("countermodel" == "background") = false from rfl,
    show ("countermodel" == "evaluate") = false from rfl,
    show ("countermodel" == "countermodel") = true from rfl,
    show ("countermodel" == "certificate") = false from rfl, Bool.false_eq_true, ↓reduceIte,
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

/-- A declared predicate of the vocabulary hiding `ns` is not in `ns`. -/
theorem hide_predicates_some {E : VE.Environment} {ns : List String} {p : String}
    {ss : List String} (h : (VE.Definitions.hide E ns).predicates p = some ss) :
    p ∉ ns ∧ E.predicates p = some ss := by
  unfold VE.Definitions.hide at h
  dsimp only at h
  split at h
  · cases h
  · exact ⟨by assumption, h⟩

/-- A closure formula over the vocabulary hiding `ns` is one over the whole vocabulary. -/
theorem closure_wellFormed_hide (E : VE.Environment) (ns : List String) :
    ∀ (a : VE.Closure.Formula) (Γ : List String),
      a.WellFormed (VE.Definitions.hide E ns) Γ → a.WellFormed E Γ
  | .top, _, h | .bottom, _, h => h
  | .unary _ _, _, ⟨s, hp, ht⟩ => ⟨s, (hide_predicates_some hp).2, ht⟩
  | .binary _ _ _, _, ⟨s, r, hp, ht, hu⟩ => ⟨s, r, (hide_predicates_some hp).2, ht, hu⟩
  | .eq _ _, _, h => h
  | .not a, Γ, h => closure_wellFormed_hide E ns a Γ h
  | .and a b, Γ, h | .or a b, Γ, h | .implies a b, Γ, h =>
    ⟨closure_wellFormed_hide E ns a Γ h.1, closure_wellFormed_hide E ns b Γ h.2⟩
  | .all s a, Γ, h | .ex s a, Γ, h => ⟨h.1, closure_wellFormed_hide E ns a (s :: Γ) h.2⟩
  | .reachNamed _ _ _ _, _, ⟨s, hp, ht, hu⟩ => ⟨s, (hide_predicates_some hp).2, ht, hu⟩
  | .reachBody _ s a _ _, Γ, ⟨hs, ha, ht, hu⟩ =>
    ⟨hs, closure_wellFormed_hide E ns a (s :: s :: Γ) ha, ht, hu⟩

theorem term_denote_forget (ns : List String) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (t : VE.Term) : t.denote (VE.Definitions.forget ns S) ρ = t.denote S ρ := by
  cases t <;> rfl

/-- Forgetting the relations `ns` does not change the truth of a closure
formula over the vocabulary hiding them. -/
theorem closure_denote_forget (E : VE.Environment) (ns : List String) (S : VE.Structure.{u}) :
    ∀ (a : VE.Closure.Formula) (Γ : List String) (ρ : VE.Valuation S),
      a.WellFormed (VE.Definitions.hide E ns) Γ →
        (a.denote (VE.Definitions.forget ns S) ρ ↔ a.denote S ρ)
  | .top, _, _, _ | .bottom, _, _, _ => Iff.rfl
  | .unary p t, _, ρ, ⟨_, hp, _⟩ => by
    simp only [VE.Closure.Formula.denote, term_denote_forget]
    simp [VE.Definitions.forget, (hide_predicates_some hp).1]
  | .binary p t u, _, ρ, ⟨_, _, hp, _⟩ => by
    simp only [VE.Closure.Formula.denote, term_denote_forget]
    simp [VE.Definitions.forget, (hide_predicates_some hp).1]
  | .eq t u, _, _, _ => Iff.rfl
  | .not a, Γ, ρ, h => not_congr (closure_denote_forget E ns S a Γ ρ h)
  | .and a b, Γ, ρ, h =>
    and_congr (closure_denote_forget E ns S a Γ ρ h.1) (closure_denote_forget E ns S b Γ ρ h.2)
  | .or a b, Γ, ρ, h =>
    or_congr (closure_denote_forget E ns S a Γ ρ h.1) (closure_denote_forget E ns S b Γ ρ h.2)
  | .implies a b, Γ, ρ, h =>
    imp_congr (closure_denote_forget E ns S a Γ ρ h.1) (closure_denote_forget E ns S b Γ ρ h.2)
  | .all s a, Γ, ρ, h =>
    forall_congr' fun v => imp_congr Iff.rfl (closure_denote_forget E ns S a (s :: Γ) (v :: ρ) h.2)
  | .ex s a, Γ, ρ, h =>
    exists_congr fun v => and_congr Iff.rfl (closure_denote_forget E ns S a (s :: Γ) (v :: ρ) h.2)
  | .reachNamed k p t u, _, ρ, ⟨_, hp, _⟩ => by
    have hn := (hide_predicates_some hp).1
    simp only [VE.Closure.Formula.denote]
    refine exists_congr fun v => exists_congr fun w => and_congr Iff.rfl (and_congr Iff.rfl ?_)
    exact VE.Closure.reachable_congr k _ _ (fun x y => by simp [VE.Definitions.forget, hn]) v w
  | .reachBody k s a t u, Γ, ρ, ⟨_, ha, _⟩ => by
    simp only [VE.Closure.Formula.denote]
    refine exists_congr fun v => exists_congr fun w => and_congr Iff.rfl (and_congr Iff.rfl ?_)
    exact VE.Closure.reachable_congr k _ _ (fun x y => and_congr Iff.rfl (and_congr Iff.rfl
      (closure_denote_forget E ns S a (s :: s :: Γ) (y :: x :: ρ) ha))) v w

/-- The closure embedding keeps typing. -/
theorem embed_wellFormed (E : VE.Environment) :
    ∀ (a : VE.Formula) (Γ : List String), a.WellFormed E Γ → (VE.Closure.embed a).WellFormed E Γ
  | .top, _, h | .bottom, _, h | .unary _ _, _, h | .binary _ _ _, _, h | .eq _ _, _, h => h
  | .not a, Γ, h => embed_wellFormed E a Γ h
  | .and a b, Γ, h | .or a b, Γ, h | .implies a b, Γ, h =>
    ⟨embed_wellFormed E a Γ h.1, embed_wellFormed E b Γ h.2⟩
  | .all s a, Γ, h | .ex s a, Γ, h => ⟨h.1, embed_wellFormed E a (s :: Γ) h.2⟩

theorem embed_sat (S : VE.Structure.{u}) (as : List VE.Formula) :
    closure.Sat S (as.map VE.Closure.embed) ↔ fol.Sat S as := by
  simp only [Semantics.Sat, List.mem_map, forall_exists_index, and_imp, forall_apply_eq_imp_iff₂]
  exact forall₂_congr fun a _ => VE.Closure.conservativity S [] a

/-- A FOL layer read over closure formulas: the same structures, restriction
and meaning, its premises embedded unchanged (`Closure.conservativity`). -/
def _root_.VE.Route.Layer.toClosure (l : Layer fol.{u} Unit)
    (hext : ∀ a, closure.WellFormed l.E_in a → closure.WellFormed l.E_out a)
    (hres : ∀ S a, l.Admissible_out S → closure.WellFormed l.E_in a →
      (closure.Holds (l.restrict S) a ↔ closure.Holds S a)) : Layer closure.{u} Unit where
  E_in := l.E_in
  E_out := l.E_out
  extends_env := hext
  premises d := (l.premises d).map VE.Closure.embed
  premises_wellFormed d a ha := by
    obtain ⟨b, hb, rfl⟩ := List.mem_map.mp ha
    exact embed_wellFormed _ b [] (l.premises_wellFormed d b hb)
  Admissible_in := l.Admissible_in
  Admissible_out := l.Admissible_out
  admissible_out := l.admissible_out
  restrict := l.restrict
  restrict_admissible := l.restrict_admissible
  restrict_holds := hres
  Intended := l.Intended
  faithful d S h := (embed_sat S _).trans (l.faithful d S h)
  expands d S₀ h := by
    obtain ⟨S, ⟨hr, ha, hp⟩, hu⟩ := l.expands d S₀ h
    exact ⟨S, ⟨hr, ha, (embed_sat S _).mpr hp⟩,
      fun S' hS' => hu S' ⟨hS'.1, hS'.2.1, (embed_sat S' _).mp hS'.2.2⟩⟩

/-- The composed layer over closure formulas. -/
def closureLayer (rv : RouteVocabulary) (hd : FlagsBase rv) : Layer closure.{u} Unit :=
  (fullLayer rv hd).toClosure
    (fun a h => by rw [fullLayer_E_out]; exact closure_wellFormed_hide _ _ a [] h)
    (fun S a _ h => by
      show a.denote ((fullLayer rv hd).restrict S) [] ↔ a.denote S []
      rw [fullLayer_restrict]; exact closure_denote_forget _ _ S a [] [] h)

/-- The closure family: closure formulas over v0 structures, the FOL family's meaning. -/
def closureFamily : Family.{u} where
  L := closure
  Vocab := RouteVocabulary
  env := RouteVocabulary.environment
  Decoded := FlagsBase
  Intended := RouteIntended
  layer := closureLayer
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
  rw [valid_field_steps] at hv
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

theorem closureFamily_sound : closureFamily.{u}.Sound where
  layer_env := fullLayer_E_out
  layer_intended := fullLayer_intended

theorem closureRunner_sound : closureRunner.{u}.Sound where
  family := closureFamily_sound
  stmt_formula _ _ := rfl
  background_sound rv hd _ S hS hp :=
    (embed_sat S _).mpr (fullLayer_background_sound rv hd () S hS ((embed_sat S _).mp hp))
  run_accepted := runClosure_accepted

/-- `runClosure`'s certificate kind, with the same meaning as `runFol`'s;
Background is embedded unchanged (`Closure.conservativity`). -/
theorem runClosure_certificate_acceptance (profiles : List String) (environment : Json)
    (rv : RouteVocabulary) (hd : FlagsBase rv) (id : String) (j out : Json)
    (h : runClosure profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    (∃ cert, VE.CertificateWire.decodeClosureCertificate (j.getObjValD "certificate") = .ok cert ∧
      closureRunner.{u}.Bound profiles environment rv j cert) ∧
      CertificateClaim closureFamily.{u} rv j ∧ BaseClaim closureFamily.{u} rv hd j :=
  closureRunner.acceptance closureRunner_sound profiles environment rv hd id j out h hv

/-- `runClosure`'s countermodel kind, with `runFol`'s meaning over closure formulas. -/
theorem runClosure_countermodel (profiles : List String) (environment : Json) (rv : RouteVocabulary)
    (id : String) (j out : Json) (h : runClosure profiles environment rv id "countermodel" j = .ok out) :
    CountermodelAnswer closureFamily routeModel rv j out := by
  unfold runClosure at h
  simp only [show ("countermodel" == "background") = false from rfl,
    show ("countermodel" == "evaluate") = false from rfl,
    show ("countermodel" == "countermodel") = true from rfl,
    show ("countermodel" == "certificate") = false from rfl, Bool.false_eq_true, ↓reduceIte,
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
  Decoded _ := True
  Intended rv S := Background.OrderStringAdmissible rv.vocabulary.environment rv.literals S
  layer rv _ := Layer.id rv.vocabulary.environment
    (Background.OrderStringAdmissible rv.vocabulary.environment rv.literals) (fun _ h => h.1)
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
  rw [valid_field_steps] at hv
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

theorem orderFamily_sound : orderFamily.{u}.Sound where
  layer_env _ _ := rfl
  layer_intended _ _ _ := ⟨fun h => ⟨h, trivial⟩, fun h => h.1⟩

theorem orderRunner_sound : orderRunner.{u}.Sound where
  family := orderFamily_sound
  stmt_formula _ _ := rfl
  background_sound rv _ _ S hS _ := (Background.orderLiterals_sat_iff S rv.literals rv.nodup).mpr hS.2
  run_accepted := runOrder_accepted

/-- `runOrder`'s certificate kind: a `"valid": true` answer means the decoded
conclusion holds in every admissible order structure in which the declared
literals are distinct and the decoded premises hold. -/
theorem runOrder_certificate_acceptance (profiles : List String) (environment : Json)
    (rv : RouteOrderVocabulary) (id : String) (j out : Json)
    (h : runOrder profiles environment rv id "certificate" j = .ok out)
    (hv : out.getObjValD "valid" = .bool true) :
    (∃ cert, VE.Order.Wire.decodeCertificate (j.getObjValD "certificate") = .ok cert ∧
      orderRunner.{u}.Bound profiles environment rv j cert) ∧ CertificateClaim orderFamily.{u} rv j ∧
      BaseClaim orderFamily.{u} rv trivial j :=
  orderRunner.acceptance orderRunner_sound profiles environment rv trivial id j out h hv

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
