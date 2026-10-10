import VE.Ask.PlainWire
import VE.NormDefaults.Replay

/-! The zero-set adapter: a `norms@0` document under `norm-defaults@0` with no reading set (the agent-policy documents),
answered by the norm-defaults route's own checkers (docs/spec/question-answering-q2-progress.md, decision 1; plan
4.7's zero-set case, D18).

RD-3's admission needs `readings@1` and a content-bearing set; with `readings@1` inserted it admits the agent-policy
document but takes about 73 s of Lean per replay, while the norm-defaults route decodes the same policy in 0.2 s. So a
document with no reading set is one choice, `[]`, checked on its own `UDoc` by the route that owns it: the norm
units' contents decoded as the route decodes a norm document (`decodeSourceU`), the asserted units' formulas as `Γ`,
the conflict packages bound as the route binds them (`decodePackageU`) and checked by `conflictFreeCheckU`, a filled
conflict witness by `witnessFromU`, certificates bound to the source environment and `premisesU` as
`replayEntailmentU` binds them and accepted by `acceptanceU`, base models admitted as the route admits them
(`admitModel`) with fillings (`decodeFilling`) checked by `modelCheckU` and `localFree`, as RD-3's `ndModelOk`.

The claims are RD-3's per-choice claims on the document's `UDoc` (`HoldsU`, `LeadHoldsU`, `ReasonHoldsU`): for a
readings document's choice `c`, `LeadHolds N ψ r` is `LeadHoldsU (choiceU N c) (choiceDoc N.D c).2 ψ r` by
definition (`leadHolds_eq`). These statements are new; they are not in spec 5.2. -/

namespace VE.Ask
open Lean VE.Readings VE.NormDefaults VE.NormDefaults.Wire
open VE.Norms (Sat restrictAll DocumentExpansion envAt size targets)
universe u

/-! ## What a row claims of one document -/

def HoldsU (U : UDoc) (Γ : List VE.Formula) (φ : VE.Formula) : ChoiceResult → Prop
  | .proved => ConflictFreeU.{u} U ∧ EntailsU.{u} U Γ φ
  | .refuted => CounterU U Γ φ
  | .free => ConflictFreeU.{u} U
  | .conflict => ¬ ConflictFreeU.{0} U
  | .model => ConsistentU U Γ
  | .inconsistent => ConflictFreeU.{u} U ∧ EntailsU.{u} U Γ .bottom
  | .unknown => True

/-- RD-3's per-choice claims are these, on the choice's `UDoc` and assertions. -/
theorem holds_iff (N : NDoc) (φ : VE.Formula) (c : Choice) (x : ChoiceResult) :
    Holds.{u} N [] φ c x ↔ HoldsU.{u} (choiceU N c) (choiceDoc N.D c).2 φ x := by
  cases x <;> simp [Holds, HoldsU]

def LeadHoldsU (U : UDoc) (Γ : List VE.Formula) (ψ : VE.Formula) (r : Row) : Prop :=
  match r.lead with
  | .yes => ConflictFreeU.{u} U ∧ ConsistentU U Γ ∧ EntailsU.{u} U Γ ψ
  | .no => ConflictFreeU.{u} U ∧ ConsistentU U Γ ∧ EntailsU.{u} U Γ (.not ψ)
  | .notSettled => ConflictFreeU.{u} U ∧ SplitU U Γ ψ
  | .notNecessarily => ConflictFreeU.{u} U ∧ CounterU U Γ ψ
  | .unknown => True

/-- The zero-set claims are the readings route's, for every choice. -/
theorem leadHolds_eq (N : NDoc) (ψ : VE.Formula) (r : Row) :
    LeadHolds.{u} N ψ r = LeadHoldsU.{u} (choiceU N r.choice) (choiceDoc N.D r.choice).2 ψ r := rfl

def ReasonHoldsU (U : UDoc) (Γ : List VE.Formula) (ψ : VE.Formula) : Reason → Prop
  | .conflict => ¬ ConflictFreeU.{0} U
  | .inconsistent => ConflictFreeU.{u} U ∧ EntailsU.{u} U Γ .bottom
  | .unchecked => ConflictFreeU.{u} U ∧ (EntailsU.{u} U Γ ψ ∨ EntailsU.{u} U Γ (.not ψ))
  | _ => True

def RowOkU (U : UDoc) (Γ : List VE.Formula) (ψ : VE.Formula) (r : Row) : Prop :=
  HoldsU.{u} U Γ .bottom r.conflict ∧ HoldsU.{u} U Γ .bottom r.premise ∧
  HoldsU.{u} U Γ ψ r.query ∧ HoldsU.{u} U Γ (.not ψ) r.negation ∧
  (r.split = true → SplitU U Γ ψ)

theorem leadU_sound (U : UDoc) (Γ : List VE.Formula) (ψ : VE.Formula) (r : Row) (h : RowOkU.{u} U Γ ψ r) :
    LeadHoldsU.{u} U Γ ψ r := by
  obtain ⟨hc, hp, hq, hn, hs⟩ := h
  unfold LeadHoldsU
  cases hl : r.lead with
  | yes =>
    obtain ⟨h1, h2, h3⟩ := lead_yes hl
    rw [h1] at hc; rw [h2] at hq; rw [h3] at hp
    exact ⟨hc, hp, hq.2⟩
  | no =>
    obtain ⟨h1, _, h3, h4⟩ := lead_no hl
    rw [h1] at hc; rw [h3] at hn; rw [h4] at hp
    exact ⟨hc, hp, hn.2⟩
  | notSettled =>
    obtain ⟨h1, _, _, h4⟩ := lead_notSettled hl
    rw [h1] at hc
    exact ⟨hc, hs h4⟩
  | notNecessarily =>
    obtain ⟨h1, h2, _, _⟩ := lead_notNecessarily hl
    rw [h1] at hc; rw [h2] at hq
    exact ⟨hc, hq⟩
  | unknown => trivial

theorem reasonU_sound (U : UDoc) (Γ : List VE.Formula) (ψ : VE.Formula) (r : Row) (x : Reason)
    (h : RowOkU.{u} U Γ ψ r) (hx : r.reason = some x) : ReasonHoldsU.{u} U Γ ψ x := by
  obtain ⟨hc, hp, hq, hn, _⟩ := h
  obtain ⟨f1, f2, f3⟩ := reason_fields hx
  cases x with
  | conflict =>
    have h1 := f1 rfl
    rw [h1] at hc
    exact hc
  | inconsistent =>
    obtain ⟨_, h2⟩ := f2 rfl
    rw [h2] at hp
    exact hp
  | unchecked =>
    obtain ⟨h1, h2⟩ := f3 rfl
    rw [h1] at hc
    rcases h2 with h2 | h2
    · rw [h2] at hq
      exact ⟨hc, Or.inl hq.2⟩
    · rw [h2] at hn
      exact ⟨hc, Or.inr hn.2⟩
  | conflictUnchecked => trivial
  | noResult => trivial
  | tooMany => trivial

/-! ## The decoded case -/

/-- What Lean decodes of a zero-set case: the source environment, the norm units' contents as the route's norm
    document, the decoded source, the asserted units (id, content JSON, formula over `E‴`), the conclusion. -/
structure ZeroParts where
  environment : Json
  norms : Json
  s : SourceU
  profiled : s.profiled = true
  units : List (String × Json × VE.Formula)
  conclusion : Json
  ψ : VE.Formula

abbrev ZeroParts.U (p : ZeroParts) : UDoc := p.s.U
abbrev ZeroParts.E (p : ZeroParts) : VE.Environment := envAt (fill p.s.U) (size (fill p.s.U))
abbrev ZeroParts.Γ (p : ZeroParts) : List VE.Formula := p.units.map (·.2.2)
theorem ZeroParts.wfU (p : ZeroParts) : WellFormedU p.s.U = true := p.s.wfU p.profiled

/-- One unit of the case: a norm unit's content, or an asserted unit's formula over `E‴`; none without content. -/
def zeroUnit (E : VE.Environment) (data : Bool) (u : Json) :
    Except String (Option (Json ⊕ (String × Json × VE.Formula))) := do
  let id ← VE.Bridge.stringField u "id"
  match u.getObjValD "content" with
  | .null => pure none
  | c =>
    match strOf? (u.getObjValD "kind") with
    | some "norm" => pure (some (.inl c))
    | some "asserted" => pure (some (.inr (id, c, ← VE.Route.Wire.decodeClosed E c data)))
    | _ => throw "UnsupportedProfile: the norm-defaults route of ask answers norm and asserted units"

def zeroParts (case : Json) : Except String { p : ZeroParts // p.conclusion = case.getObjValD "conclusion" } := do
  VE.Bridge.exactFields case ["environment", "document", "conclusion", "evidence"]
  let environment ← case.getObjVal? "environment"
  let ps := profilesOf environment
  unless hasProfile environment && ps.contains "norms@0" && !ps.contains "readings@1" do
    throw "UnsupportedProfile: the zero-set route answers norms@0 documents under norm-defaults@0 without readings@1"
  let us ← match (case.getObjValD "document").getObjValD "units" with
    | .arr us => pure us.toList
    | _ => throw "InvalidInput: the case's units are a list"
  let norms := Json.arr (us.filterMap fun u =>
    if strOf? (u.getObjValD "kind") == some "norm" && !(u.getObjValD "content" == .null) then
      some (u.getObjValD "content") else none).toArray
  let s ← decodeSourceU environment norms
  if hp : s.profiled = true then
    let E := envAt (fill s.U) (size (fill s.U))
    let data := ps.contains "data@0"
    let parts ← us.filterMapM (zeroUnit E data)
    let units := parts.filterMap fun x => match x with | .inr u => some u | .inl _ => none
    let conclusion := case.getObjValD "conclusion"
    let ψ ← VE.Route.Wire.decodeClosed E conclusion data
    pure ⟨⟨environment, norms, s, hp, units, conclusion, ψ⟩, rfl⟩
  else throw "UnsupportedProfile: the zero-set route needs norm-defaults@0"

/-! ## The evidence -/

def ZeroParts.piece (_p : ZeroParts) (case : Json) (k : String) : Option Json :=
  VE.Readings.Wire.pieceOf (case.getObjValD "evidence") k

/-- A certificate bound as `replayEntailmentU` binds one: to the source environment, the regenerated premises of
    `fill U` and the asserted units, and `conclusion`. -/
def zeroCert (p : ZeroParts) (conclusion : Json) (piece : Option Json) : Option VE.Tableau.Certificate :=
  piece.bind fun j => match VE.CertificateWire.decodeCertificate (j.getObjValD "certificate") with
    | .ok k => match canonicalEnvironmentJsonU p.environment with
      | .ok canonical => match VE.Route.Wire.bindingOk (profilesOf p.environment) canonical
          ((VE.Norms.background (fill p.U) ++ fillPremises p.U ++ VE.Norms.elaborate (fill p.U).T).map VE.NormDefaults.Wire.enc ++
            p.units.map (·.2.1)) conclusion k.environment_id k.premise_meaning_ids k.conclusion_meaning_id with
        | .ok () => some k
        | .error _ => none
      | .error _ => none
    | .error _ => none

def zeroProved (p : ZeroParts) (φ : VE.Formula) (k : Option VE.Tableau.Certificate) : Bool :=
  (k.map (VE.Tableau.checkCertificate p.E (premisesU p.U p.Γ) φ)).getD false

theorem zeroProved_sound {p : ZeroParts} {φ : VE.Formula} {k : Option VE.Tableau.Certificate}
    (h : zeroProved p φ k = true) : EntailsU.{u} p.U p.Γ φ := by
  unfold zeroProved at h
  cases hk : k with
  | none => rw [hk] at h; cases h
  | some k => rw [hk] at h; exact acceptanceU p.U p.wfU p.Γ φ k h

/-- The conflict packages of the case (`conflict.packages`), one per target of `fill U`, bound as the route binds
    them. -/
def zeroCerts (p : ZeroParts) (case : Json) : List (Option VE.Tableau.Certificate) :=
  let packages := ((p.piece case "conflict").map (·.getObjValD "packages")).getD (Json.mkObj [])
  (targets (fill p.U)).map (decodePackageU p.U p.environment p.norms packages)

def zeroFree (p : ZeroParts) (case : Json) : Bool := conflictFreeCheckU p.U (zeroCerts p case)

theorem zeroFree_sound {p : ZeroParts} {case : Json} (h : zeroFree p case = true) : ConflictFreeU.{u} p.U :=
  conflictFreeCheckU_sound p.U p.s.wfFill _ h

/-- A filled conflict witness (`witness.witness`) whose target holds at its tuple. -/
def zeroWitness (p : ZeroParts) (case : Json) : Option (WitnessDataU p.s) :=
  (p.piece case "witness").bind fun w => (witnessFromU p.s (w.getObjValD "witness")).toOption

def zeroConflict (p : ZeroParts) (case : Json) : Bool := (zeroWitness p case).any (·.conflict)

theorem zeroConflict_sound {p : ZeroParts} {case : Json} (h : zeroConflict p case = true) :
    ¬ ConflictFreeU.{0} p.U := by
  unfold zeroConflict at h
  cases hw : zeroWitness p case with
  | none => rw [hw] at h; cases h
  | some w =>
    rw [hw] at h
    have hc : w.conflict = true := by simpa using h
    exact targetU_refutes p.s.U p.s.wfFill w.target w.mem w.M.asStructure
      ⟨VE.Norms.baseAdmissible_of_valid (fill p.s.U) w.M w.valid w.background, fun φ hφ =>
        (VE.eval_iff_denote w.M [] φ).mp (List.all_eq_true.mp w.filled φ hφ)⟩
      w.tuple w.typed ((VE.eval_iff_denote w.M _ _).mp hc)

/-- A base model of the source (`model`), admitted as the route admits one, with its validity. -/
def zeroBase (p : ZeroParts) (m : Json) : Option { M : VE.FiniteModel VE.Bridge.Entity // M.Valid (envAt p.U.D 0) } :=
  let v := VE.Norms.Replay.baseModelVocabulary p.s.src.ne p.s.src.D
  match VE.Bridge.decodeModelData v m with
  | .ok data => match admitModel p.s v data with
    | .ok a => some ⟨a.data.toModel, by
        have h := VE.Norms.Replay.baseModel_valid p.s.src.ne p.s.src.D p.s.src.env a.data.toModel
          (VE.Bridge.modelData_valid a.data v a.valid)
        rw [← p.s.doc] at h
        exact h⟩
    | .error _ => none
  | .error _ => none

/-- A filled model: a base model with a filling of the unsaid tables. -/
def zeroFilled (p : ZeroParts) (m filling : Json) : Option (VE.Readings.Wire.FilledModel p.U) := do
  let ⟨M, valid⟩ ← zeroBase p m
  let F ← (decodeFilling p.U M filling).toOption
  pure ⟨M, valid, F⟩

/-- `ndModelOk` on the document's own `UDoc`: the premises and the conclusion typed, the model check passing with
    the conclusion's value `v`, locally conflict-free. -/
def zeroModelOk (p : ZeroParts) (φ : VE.Formula) (m : VE.Readings.Wire.FilledModel p.U) (v : Bool) : Bool :=
  (p.Γ ++ [φ]).all (·.check p.E []) && (modelCheckU p.U m.M m.F p.Γ φ).1 &&
    (modelCheckU p.U m.M m.F p.Γ φ).2 == v && VE.Readings.Wire.localFree p.U m.M m.F

theorem zeroModelOk_base {p : ZeroParts} {φ : VE.Formula} {m : VE.Readings.Wire.FilledModel p.U} {v : Bool}
    (h : zeroModelOk p φ m v = true) :
    ∃ S : VE.Structure.{0}, restrictAll (fill p.U).T S = withFill p.U m.M.asStructure (finFill m.M m.F) ∧
      BaseAdmissibleU p.U (withFill p.U m.M.asStructure (finFill m.M m.F)) ∧
      DocumentExpansion (fill p.U) (withFill p.U m.M.asStructure (finFill m.M m.F)) S ∧
      Sat S p.Γ ∧ (φ.denote S [] ↔ v = true) := by
  simp only [zeroModelOk, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at h
  obtain ⟨⟨⟨hw, hm⟩, hv⟩, hl⟩ := h
  have hw' : ∀ a ∈ p.Γ ++ [φ], a.WellFormed p.E [] := fun a ha => (VE.check_iff_wellFormed _ _ a).mp (hw a ha)
  obtain ⟨S, h0, h1, h2, h3, h4⟩ := expansion_of_modelCheck_base _ p.wfU m.M m.valid m.F _ φ
    (fun a ha => hw' a (List.mem_append_left _ ha)) (hw' φ (List.mem_append_right _ List.mem_cons_self)) hm hl
  exact ⟨S, h0, h1, h2, h3, by rw [← hv]; exact h4⟩

theorem zeroModelOk_counter {p : ZeroParts} {φ : VE.Formula} {m : VE.Readings.Wire.FilledModel p.U}
    (h : zeroModelOk p φ m false = true) : CounterU p.U p.Γ φ := by
  obtain ⟨S, h0, h1, h2, h3, h4⟩ := zeroModelOk_base h
  exact ⟨S, by rw [h0]; exact h1, by rw [h0]; exact h2, h3, fun hd => by simpa using h4.mp hd⟩

theorem zeroModelOk_consistent {p : ZeroParts} {m : VE.Readings.Wire.FilledModel p.U} (h : zeroModelOk p .bottom m false = true) :
    ConsistentU p.U p.Γ := by
  obtain ⟨S, h0, h1, h2, h3, _⟩ := zeroModelOk_base h
  exact ⟨S, by rw [h0]; exact h1, by rw [h0]; exact h2, h3⟩

/-- A model piece's filled model. -/
def zeroModel (p : ZeroParts) (piece : Option Json) : Option (VE.Readings.Wire.FilledModel p.U) :=
  piece.bind fun j => zeroFilled p (j.getObjValD "model") (j.getObjValD "filling")

/-- The split: one base model (`model`) with two fillings, `true` (ψ holds) and `false` (ψ fails). -/
def zeroSplitModels (p : ZeroParts) (piece : Option Json) : Option (VE.Readings.Wire.FilledModel p.U × VE.Readings.Wire.FilledModel p.U) := do
  let j ← piece
  let ⟨M, valid⟩ ← zeroBase p (j.getObjValD "model")
  let F₁ ← (decodeFilling p.U M (j.getObjValD "true")).toOption
  let F₂ ← (decodeFilling p.U M (j.getObjValD "false")).toOption
  pure (⟨M, valid, F₁⟩, ⟨M, valid, F₂⟩)

theorem zeroSplitModels_base {p : ZeroParts} {piece : Option Json} {m₁ m₂ : VE.Readings.Wire.FilledModel p.U}
    (h : zeroSplitModels p piece = some (m₁, m₂)) : m₁.M = m₂.M := by
  unfold zeroSplitModels at h
  simp only [Option.bind_eq_bind, Option.bind_eq_some_iff] at h
  obtain ⟨j, _, ⟨M, valid⟩, _, F₁, _, F₂, _, h⟩ := h
  simp only [Option.pure_def, Option.some.injEq, Prod.mk.injEq] at h
  obtain ⟨rfl, rfl⟩ := h
  rfl

def zeroSplit (p : ZeroParts) (case : Json) : Bool :=
  match zeroSplitModels p (p.piece case "split") with
  | some (m₁, m₂) => zeroModelOk p p.ψ m₁ true && zeroModelOk p p.ψ m₂ false
  | none => false

theorem zeroSplit_sound {p : ZeroParts} {case : Json} (h : zeroSplit p case = true) : SplitU p.U p.Γ p.ψ := by
  unfold zeroSplit at h
  split at h
  · rename_i m₁ m₂ hs
    simp only [Bool.and_eq_true] at h
    obtain ⟨S₁, e₁, a₁, x₁, s₁, d₁⟩ := zeroModelOk_base h.1
    obtain ⟨S₂, e₂, a₂, x₂, s₂, d₂⟩ := zeroModelOk_base h.2
    have hM := zeroSplitModels_base hs
    obtain ⟨M₁, v₁, F₁⟩ := m₁
    obtain ⟨M₂, v₂, F₂⟩ := m₂
    simp only at hM e₁ a₁ x₁ d₁ e₂ a₂ x₂ d₂
    subst hM
    exact ⟨M₁.asStructure, finFill M₁ F₁, finFill M₁ F₂, S₁, S₂, e₁, e₂, a₁, a₂, x₁, x₂, s₁, s₂, by simpa using d₁,
      by simpa using d₂⟩
  · cases h

/-! ## The row -/

def zeroQueryProved (p : ZeroParts) (case : Json) : Bool :=
  zeroProved p p.ψ (zeroCert p p.conclusion (p.piece case "certificate")) && zeroFree p case
def zeroNegationProved (p : ZeroParts) (case : Json) : Bool :=
  zeroProved p (.not p.ψ) (zeroCert p (VE.NormDefaults.Wire.enc (.not p.ψ)) (p.piece case "negation")) && zeroFree p case
def zeroUnsat (p : ZeroParts) (case : Json) : Bool :=
  zeroProved p .bottom (zeroCert p (VE.NormDefaults.Wire.enc .bottom) (p.piece case "unsat")) && zeroFree p case
def zeroRefuted (p : ZeroParts) (case : Json) : Bool :=
  (zeroModel p (p.piece case "countermodel")).any (zeroModelOk p p.ψ · false)
def zeroConsistent (p : ZeroParts) (case : Json) : Bool :=
  (zeroModel p (p.piece case "model")).any (zeroModelOk p .bottom · false)

/-- The row of a zero-set case, as RD-3's rows are made: conflict-free with the packages accepted, CONFLICT with a
    checked witness; a certificate with the packages, else a countermodel; a certificate of `⊥` with the packages,
    else a premise model; the negation's certificate with the packages; the split. -/
def zeroRow (p : ZeroParts) (case : Json) : Row :=
  { choice := [],
    conflict := if zeroFree p case then .free else if zeroConflict p case then .conflict else .unknown,
    premise := if zeroUnsat p case then .inconsistent else if zeroConsistent p case then .model else .unknown,
    query := if zeroQueryProved p case then .proved else if zeroRefuted p case then .refuted else .unknown,
    negation := if zeroNegationProved p case then .proved else .unknown,
    split := zeroSplit p case }

theorem any_some {α : Type} {o : Option α} {f : α → Bool} (h : o.any f = true) : ∃ a, o = some a ∧ f a = true := by
  cases o with
  | none => cases h
  | some a => exact ⟨a, rfl, by simpa using h⟩

theorem zeroRow_ok (p : ZeroParts) (case : Json) : RowOkU.{0} p.U p.Γ p.ψ (zeroRow p case) := by
  refine ⟨?_, ?_, ?_, ?_, fun h => zeroSplit_sound h⟩
  · show HoldsU p.U p.Γ .bottom
      (if zeroFree p case then .free else if zeroConflict p case then .conflict else .unknown)
    split
    · exact zeroFree_sound ‹_›
    · split
      · exact zeroConflict_sound ‹_›
      · trivial
  · show HoldsU p.U p.Γ .bottom
      (if zeroUnsat p case then .inconsistent else if zeroConsistent p case then .model else .unknown)
    split
    · rename_i h1
      simp only [zeroUnsat, Bool.and_eq_true] at h1
      exact ⟨zeroFree_sound h1.2, zeroProved_sound h1.1⟩
    · split
      · rename_i h2
        obtain ⟨m, _, hm⟩ := any_some h2
        exact zeroModelOk_consistent hm
      · trivial
  · show HoldsU p.U p.Γ p.ψ
      (if zeroQueryProved p case then .proved else if zeroRefuted p case then .refuted else .unknown)
    split
    · rename_i h1
      simp only [zeroQueryProved, Bool.and_eq_true] at h1
      exact ⟨zeroFree_sound h1.2, zeroProved_sound h1.1⟩
    · split
      · rename_i h2
        obtain ⟨m, _, hm⟩ := any_some h2
        exact zeroModelOk_counter hm
      · trivial
  · show HoldsU p.U p.Γ (.not p.ψ) (if zeroNegationProved p case then .proved else .unknown)
    split
    · rename_i h1
      simp only [zeroNegationProved, Bool.and_eq_true] at h1
      exact ⟨zeroFree_sound h1.2, zeroProved_sound h1.1⟩
    · trivial

structure ZeroVerdict where
  U : UDoc
  E : VE.Environment
  Γ : List VE.Formula
  ψ : VE.Formula
  row : Row
  hok : RowOkU.{0} U Γ ψ row

def replayZeroParts (case : Json) : Except String { px : ZeroParts × ZeroVerdict //
    px.1.conclusion = case.getObjValD "conclusion" ∧ px.2.E = px.1.E ∧ px.2.U = px.1.U } :=
  match zeroParts case with
  | .error e => .error e
  | .ok ⟨p, hc⟩ => .ok ⟨(p, ⟨p.U, p.E, p.Γ, p.ψ, zeroRow p case, zeroRow_ok p case⟩), hc, rfl, rfl⟩

def replayZero (case : Json) : Except String ZeroVerdict := (replayZeroParts case).map (·.1.2)

/-! ## The replayed request -/

structure ZeroAsked where
  request : Json
  text : String
  q : String
  case : Json
  E : VE.EnglishGrammar.Env
  L : VE.EnglishGrammar.Lexicon
  c : VE.Question.Candidate
  φ : VE.EnglishGrammar.EFormula
  x : ZeroVerdict
  hrequest : request.getObjValD "document" = .str text ∧
    request.getObjValD "question" = .str q ∧ request.getObjValD "case" = case
  hbind : PlainCaseBinding text case E L x.E
  hreplay : replayZero case = .ok x
  hread : VE.Question.QuestionOneReading VE.Question.auxiliaries E {} L q c φ
  hψ : Same (case.getObjValD "conclusion") φ.encode

def replayZeroAskCore (j : Json) : Except String { a : ZeroAsked // a.request = j } := do
  let ⟨text, hd⟩ ← strField j "document"
  let ⟨q, hq⟩ ← strField j "question"
  let case := j.getObjValD "case"
  let (_, L) ← englishOf text (j.getObjValD "lexicon")
  sameEnvironment text case
  match hr : replayZeroParts case with
  | .error e => throw e
  | .ok ⟨(_, x), _, _, _⟩ =>
    have hx : replayZero case = .ok x := by rw [replayZero, hr]; rfl
    let ⟨E, hbind⟩ ← checkPlainCase text case L x.E
    let ⟨(c, φ), hread⟩ ← oneReading E L q
    if hsame : Same (case.getObjValD "conclusion") φ.encode then
      pure ⟨⟨j, text, q, case, E, L, c, φ, x, ⟨hd, hq, rfl⟩, hbind, hx, hread, hsame⟩, rfl⟩
    else throw "InvalidInput: the case does not ask this question"

def replayZeroAsk (j : Json) : Except String ZeroAsked := (replayZeroAskCore j).map Subtype.val

theorem replayZeroAsk_request {j : Json} {a : ZeroAsked} (h : replayZeroAsk j = .ok a) : a.request = j := by
  unfold replayZeroAsk at h
  cases hc : replayZeroAskCore j with
  | error e => rw [hc] at h; cases h
  | ok s =>
    rw [hc] at h
    cases h
    exact s.2

/-- What an accepted zero-set request establishes: it is the request's document, question and case; the case is
    the document's (`PlainCaseBinding`) and replays to the verdict; the question has one reading; the row's lead and
    reason hold of the document's `UDoc`, with RD-3's per-choice meaning. -/
theorem zero_ask_wire_sound (j : Json) (a : ZeroAsked) (h : replayZeroAsk j = .ok a) :
    a.request = j ∧ a.text = (j.getObjValD "document").getStr?.toOption.getD "" ∧
    a.q = (j.getObjValD "question").getStr?.toOption.getD "" ∧ a.case = j.getObjValD "case" ∧
    replayZero a.case = .ok a.x ∧ PlainCaseBinding a.text a.case a.E a.L a.x.E ∧
    VE.Question.QuestionOneReading VE.Question.auxiliaries a.E {} a.L a.q a.c a.φ ∧
    LeadHoldsU.{0} a.x.U a.x.Γ a.x.ψ a.x.row ∧
    (∀ x, a.x.row.reason = some x → ReasonHoldsU.{0} a.x.U a.x.Γ a.x.ψ x) := by
  have hj := replayZeroAsk_request h
  obtain ⟨hd, hq, hc⟩ := a.hrequest
  rw [hj] at hd hq hc
  exact ⟨hj, by rw [hd]; rfl, by rw [hq]; rfl, hc.symm, a.hreplay, a.hbind, a.hread,
    leadU_sound _ _ _ _ a.x.hok, fun x hx => reasonU_sound _ _ _ _ x a.x.hok hx⟩

end VE.Ask
