import VE.Readings.Verdicts

/-! The kind `readings-verdicts` on the enumerated route (docs/spec/readings-defaults.md 3, 4.4, 2.3 to 2.5, 6.4
and 6.5; plan RD-3).

The request carries the question (`conflict`, `premises` or `query`), the query's `premises`, `conclusion` and
optional `assumed`, and `evidence`: per compatible choice its conflict packages and witness, a certificate or a
countermodel of the query, a certificate of `⊥` or a model of the premises, and, once for the document, the dead
readings' certificates. Lean enumerates the compatible choices taking `assumed` (at most 64), checks every piece of
evidence on the choice's document it regenerates, folds the rows (`Verdicts.lean`), computes the conditions and the
English plan, and answers. Missing or refused evidence is a row `unknown`.

Under the unspecified completion each row is computed by Lean's own checkers on `choiceU N c`, and
`nd_rowsHold` proves that every row holds of its choice (`Holds`), so the fold theorems apply to the answer
(`readings_wire_verdicts_*`). Without the completion, each row is the lower route's own answer on the choice's
regenerated document, exactly as `readings-choice` answers it, and the wire theorems say what the fold reads of
those rows (`lower_verdicts_*`). -/
namespace VE.Readings.Wire
open Lean
open VE.Readings
open VE.Bridge (Entity stringField strings)
open VE.Norms (envAt size targets Sat restrictAll DocumentExpansion)
open VE.NormDefaults (UDoc fill EntailsU)
universe u

/-! ## A checked finite model under the completion is a situation of the filled document -/

/-- Every conflict target of `fill U` is false at every typed tuple of the filled finite model. -/
def localFree (U : UDoc) (M : VE.FiniteModel Entity) (F : VE.NormDefaults.FiniteFill U Entity) : Bool :=
  (targets (fill U)).all (fun t => (VE.NormDefaults.allTuples M t.2.1).all (fun vs =>
    !t.2.2.eval (M.withFill F) (VE.Norms.tupleVal vs)))

theorem conflictFree_of_localFree (U : UDoc) (h : VE.NormDefaults.WellFormedU U = true)
    (M : VE.FiniteModel Entity) (F : VE.NormDefaults.FiniteFill U Entity) (hl : localFree U M F = true) :
    VE.Norms.ConflictFree (fill U) (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F)) := by
  have hv := VE.Norms.valid_of_wellFormed _ (VE.NormDefaults.fill_wellFormed U h)
  simp only [localFree, List.all_eq_true, Bool.not_eq_true'] at hl
  have hno : ∀ t ∈ targets (fill U), ∀ vs : List Entity,
      VE.TupleTyped (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F)) t.2.1 vs →
      ¬ t.2.2.denote (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F))
        (VE.Norms.tupleVal vs) := by
    intro t ht vs hvs hd
    have hm : vs ∈ VE.NormDefaults.allTuples M t.2.1 :=
      (VE.NormDefaults.mem_allTuples M t.2.1 vs).mpr ((VE.Norms.tupleTyped_relation M.asStructure _ _ vs).mp hvs)
    have he := (VE.NormDefaults.eval_withFill U M F _ _).mpr hd
    rw [hl t ht vs hm] at he
    cases he
  refine ⟨fun r hr vs hvs => hno _ (List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩))
    vs hvs, fun pr hpr vs hvs => hno _ (List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs hvs⟩

/-- A checked finite model and filling, locally conflict-free, is the base of a filled expansion where the premises
    hold, the conclusion with the value the check reports. -/
theorem expansion_of_modelCheck (U : UDoc) (h : VE.NormDefaults.WellFormedU U = true) (M : VE.FiniteModel Entity)
    (valid : M.Valid (envAt U.D 0)) (F : VE.NormDefaults.FiniteFill U Entity) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAt (fill U) (size (fill U))) [])
    (hφ : φ.WellFormed (envAt (fill U) (size (fill U))) [])
    (hm : (VE.NormDefaults.modelCheckU U M F Γ φ).1 = true) (hl : localFree U M F = true) :
    ∃ S : VE.Structure.{0}, VE.NormDefaults.BaseAdmissibleU U (restrictAll (fill U).T S) ∧
      DocumentExpansion (fill U) (restrictAll (fill U).T S) S ∧ Sat S Γ ∧
      (φ.denote S [] ↔ (VE.NormDefaults.modelCheckU U M F Γ φ).2 = true) := by
  obtain ⟨hB, hΓs, hφs⟩ := VE.NormDefaults.modelCheckU_sound U h M valid F Γ φ hm
  have hcf := conflictFree_of_localFree U h M F hl
  have hE := VE.NormDefaults.canonTyped_expansion h hB hcf
  have hr := hE.1
  have hv := VE.Norms.valid_of_wellFormed _ (VE.NormDefaults.fill_wellFormed U h)
  obtain ⟨_, hpa⟩ := (VE.Norms.documentExpansion_iff hv _ _ hB.1).mp hE
  obtain ⟨hA, _, hM, _⟩ := (VE.Norms.prefix_char hv _ (Nat.le_refl _) _).mp hpa
  have hden : ∀ ψ : VE.Formula, ψ.denote (restrictAll (fill U).T (VE.NormDefaults.canonTyped (fill U)
      (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F)))) [] ↔
      ψ.denote (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F)) [] := fun ψ => by
    rw [hr]
  have key : ∀ a : VE.Formula, a.WellFormed (envAt (fill U) (size (fill U))) [] →
      ((VE.Norms.subst (fill U).T (size (fill U)) a).denote
        (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F)) [] ↔
        a.denote (VE.NormDefaults.canonTyped (fill U)
          (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F))) []) := fun a hw =>
    (hden _).symm.trans (VE.Norms.subst_restrict_denote hv _ _ hA.1 (VE.Norms.agreesBelow_of_meanings hM) a [] hw []
      (VE.typed_empty _))
  refine ⟨_, by rw [hr]; exact hB, by rw [hr]; exact hE, fun a ha => (key a (hΓ a ha)).mp (hΓs a ha),
    (key φ hφ).symm.trans hφs⟩

/-! ## A choice's evidence under the completion, and its rows -/

/-- A checked finite model with its filling (a countermodel of the query, or a model of the premises). -/
structure FilledModel (U : UDoc) where
  M : VE.FiniteModel Entity
  valid : M.Valid (envAt U.D 0)
  F : VE.NormDefaults.FiniteFill U Entity

/-- What Lean decoded of one compatible choice's evidence under the completion (4.3): its conflict packages
    (`certs`, bound to the choice's targets), a checked witness, and the query's and the premises' evidence. -/
structure NDEvidence (N : NDoc) (c : Choice) where
  wfc : VE.NormDefaults.WellFormedU (choiceU N c) = true
  certs : List (Option VE.Tableau.Certificate)
  witness : Option (PLift (¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c)))
  cert : Option VE.Tableau.Certificate
  counter : Option (FilledModel (choiceU N c))
  unsat : Option VE.Tableau.Certificate
  model : Option (FilledModel (choiceU N c))

/-- The complete environment of a choice's filled document. -/
def fullEnv (N : NDoc) (c : Choice) : VE.Environment :=
  envAt (fill (choiceU N c)) (size (fill (choiceU N c)))

def ndFree {N : NDoc} {c : Choice} (e : NDEvidence N c) : Bool :=
  VE.NormDefaults.Wire.conflictFreeCheckU (choiceU N c) e.certs

/-- A certificate of `Γ ⊢ φ` over the choice's filled premises (`premisesU`), its assertions first. -/
def ndCertOk (N : NDoc) (c : Choice) (Γ : List VE.Formula) (φ : VE.Formula) (k : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate (fullEnv N c) (VE.NormDefaults.Wire.premisesU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ))
    φ k

/-- A filled model where the premises (its assertions, then `Γ`) hold, locally conflict-free, typed, with the
    conclusion's value `v`. -/
def ndModelOk (N : NDoc) (c : Choice) (Γ : List VE.Formula) (φ : VE.Formula) (m : FilledModel (choiceU N c))
    (v : Bool) : Bool :=
  (((choiceDoc N.D c).2 ++ Γ) ++ [φ]).all (·.check (fullEnv N c) []) &&
    (VE.NormDefaults.modelCheckU (choiceU N c) m.M m.F ((choiceDoc N.D c).2 ++ Γ) φ).1 &&
    (VE.NormDefaults.modelCheckU (choiceU N c) m.M m.F ((choiceDoc N.D c).2 ++ Γ) φ).2 == v &&
    localFree (choiceU N c) m.M m.F

/-- The conflict row (4.3): CONFLICT-FREE with the packages accepted, CONFLICT with a checked witness. -/
def ndConflictRow {N : NDoc} {c : Choice} (e : NDEvidence N c) : ChoiceResult :=
  if ndFree e then .free else if e.witness.isSome then .conflict else .unknown

/-- The query row: `proved` with a certificate and the conflict packages (S2a 14.8), `refuted` with a checked
    countermodel. -/
def ndQueryRow {N : NDoc} {c : Choice} (e : NDEvidence N c) (Γ : List VE.Formula) (φ : VE.Formula) : ChoiceResult :=
  if (e.cert.map (ndCertOk N c Γ φ)).getD false && ndFree e then .proved
  else if (e.counter.map (ndModelOk N c Γ φ · false)).getD false then .refuted
  else .unknown

/-- The premise row: INCONSISTENT with a certificate of `⊥` and the conflict packages (4.5's table, A2), `model` with
    a checked model. -/
def ndPremiseRow {N : NDoc} {c : Choice} (e : NDEvidence N c) : ChoiceResult :=
  if (e.unsat.map (ndCertOk N c [] .bottom)).getD false && ndFree e then .inconsistent
  else if (e.model.map (ndModelOk N c [] .bottom · false)).getD false then .model
  else .unknown

theorem ndFree_sound {N : NDoc} {c : Choice} (e : NDEvidence N c) (h : ndFree e = true) :
    VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) :=
  VE.NormDefaults.Wire.conflictFreeCheckU_sound _ (VE.NormDefaults.fill_wellFormed _ e.wfc) _ h

theorem ndCertOk_sound {N : NDoc} {c : Choice} (e : NDEvidence N c) (Γ : List VE.Formula) (φ : VE.Formula)
    (k : VE.Tableau.Certificate) (h : ndCertOk N c Γ φ k = true) :
    EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ :=
  VE.NormDefaults.acceptanceU _ e.wfc _ φ k h

theorem ndModelOk_sound {N : NDoc} {c : Choice} (e : NDEvidence N c) (Γ : List VE.Formula) (φ : VE.Formula)
    (m : FilledModel (choiceU N c)) (v : Bool) (h : ndModelOk N c Γ φ m v = true) :
    ∃ S : VE.Structure.{0},
      VE.NormDefaults.BaseAdmissibleU (choiceU N c) (restrictAll (fill (choiceU N c)).T S) ∧
      DocumentExpansion (fill (choiceU N c)) (restrictAll (fill (choiceU N c)).T S) S ∧
      Sat S ((choiceDoc N.D c).2 ++ Γ) ∧ (φ.denote S [] ↔ v = true) := by
  simp only [ndModelOk, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at h
  obtain ⟨⟨⟨hw, hm⟩, hv⟩, hl⟩ := h
  have hw' : ∀ a ∈ ((choiceDoc N.D c).2 ++ Γ) ++ [φ], a.WellFormed (fullEnv N c) [] :=
    fun a ha => (VE.check_iff_wellFormed _ _ a).mp (hw a ha)
  obtain ⟨S, h1, h2, h3, h4⟩ := expansion_of_modelCheck _ e.wfc m.M m.valid m.F _ φ
    (fun a ha => hw' a (List.mem_append_left _ ha)) (hw' φ (List.mem_append_right _ List.mem_cons_self)) hm hl
  exact ⟨S, h1, h2, h3, by rw [h4, hv]⟩

/-- Every conflict row holds of its choice. -/
theorem ndConflictRow_holds {N : NDoc} {c : Choice} (e : NDEvidence N c) :
    Holds.{u} N [] .bottom c (ndConflictRow e) := by
  unfold ndConflictRow
  split
  · exact ndFree_sound e (by assumption)
  · split
    · rename_i hw
      obtain ⟨⟨p⟩, _⟩ := Option.isSome_iff_exists.mp hw
      exact p
    · trivial

theorem ndQueryRow_holds {N : NDoc} {c : Choice} (e : NDEvidence N c) (Γ : List VE.Formula) (φ : VE.Formula) :
    Holds.{u} N Γ φ c (ndQueryRow e Γ φ) := by
  unfold ndQueryRow
  split
  · rename_i hp
    simp only [Bool.and_eq_true] at hp
    obtain ⟨hk, hf⟩ := hp
    cases hc : e.cert with
    | none => rw [hc] at hk; cases hk
    | some k =>
      rw [hc] at hk
      exact ⟨ndFree_sound e hf, ndCertOk_sound e Γ φ k hk⟩
  · split
    · rename_i _ hr
      cases hc : e.counter with
      | none => rw [hc] at hr; cases hr
      | some m =>
        rw [hc] at hr
        obtain ⟨S, h1, h2, h3, h4⟩ := ndModelOk_sound e Γ φ m false hr
        exact ⟨S, h1, h2, h3, fun hd => by simpa using h4.mp hd⟩
    · trivial

theorem ndPremiseRow_holds {N : NDoc} {c : Choice} (e : NDEvidence N c) :
    Holds.{u} N [] .bottom c (ndPremiseRow e) := by
  unfold ndPremiseRow
  split
  · rename_i hp
    simp only [Bool.and_eq_true] at hp
    obtain ⟨hk, hf⟩ := hp
    cases hc : e.unsat with
    | none => rw [hc] at hk; cases hk
    | some k =>
      rw [hc] at hk
      have := ndCertOk_sound.{u} e [] .bottom k hk
      rw [List.append_nil] at this
      exact ⟨ndFree_sound e hf, this⟩
  · split
    · rename_i _ hr
      cases hc : e.model with
      | none => rw [hc] at hr; cases hr
      | some m =>
        rw [hc] at hr
        obtain ⟨S, h1, h2, h3, _⟩ := ndModelOk_sound e [] .bottom m false hr
        rw [List.append_nil] at h3
        exact ⟨S, h1, h2, h3⟩
    · trivial

/-- What the answer shows of one piece of evidence: whether Lean accepted it, its refusal, the shown model and the
    filled gaps of a shown result. -/
structure PieceNote where
  name : String
  accepted : Bool
  error : Option String := none
  shown : Option Json := none
  gaps : List (String × List String × Bool) := []
  conditionalOn : List String := []
  statusText : Option String := none

/-! ## The replay of a `readings-verdicts` case under the completion -/

/-- The compatible choices taking `A`, in canonical order. -/
def chosenOf (D : Doc) (A : Choice) : List Choice := (choices D).filter (fun c => A.all (c.contains ·))

theorem mem_chosenOf (D : Doc) (hr : supReady D = true) (hle : (choices D).length ≤ maxChoices) (A c : Choice) :
    c ∈ chosenOf D A ↔ Compatible D c ∧ ∀ x ∈ A, x ∈ c := by
  simp only [chosenOf, List.mem_filter, List.all_eq_true, List.contains_iff_mem, choices_spec D hr hle c]

/-- A replayed `readings-verdicts` case under the completion: the admitted document, `assumed`, the query's
    formulas, and the decoded evidence of exactly the compatible choices taking `A` (at most 64). -/
structure NDVerdicts where
  r : AdmittedND
  A : Choice
  Γ : List VE.Formula
  φ : VE.Formula
  ready : supReady r.N.D = true
  hle : (choices r.N.D).length ≤ maxChoices
  evs : List ((c : Choice) × NDEvidence r.N c)
  hevs : evs.map (·.1) = chosenOf r.N.D A
  /-- What the answer shows of each choice's evidence, in the order of `evs`. -/
  notes : List (List PieceNote)

def NDVerdicts.conflictRows (x : NDVerdicts) : List (Choice × ChoiceResult) :=
  x.evs.map (fun e => (e.1, ndConflictRow e.2))
def NDVerdicts.queryRows (x : NDVerdicts) : List (Choice × ChoiceResult) :=
  x.evs.map (fun e => (e.1, ndQueryRow e.2 x.Γ x.φ))
def NDVerdicts.premiseRows (x : NDVerdicts) : List (Choice × ChoiceResult) :=
  x.evs.map (fun e => (e.1, ndPremiseRow e.2))

theorem NDVerdicts.covers (x : NDVerdicts) {rs : List (Choice × ChoiceResult)} (h : rs.map (·.1) = x.evs.map (·.1)) :
    Covers x.r.N x.A rs := fun c => by
  rw [h, x.hevs, mem_chosenOf _ x.ready x.hle]

theorem mem_rows {N : NDoc} {evs : List ((c : Choice) × NDEvidence N c)} {f : (c : Choice) → NDEvidence N c → ChoiceResult}
    {y : Choice × ChoiceResult} (hy : y ∈ evs.map (fun e => (e.1, f e.1 e.2))) : ∃ e ∈ evs, y = (e.1, f e.1 e.2) := by
  obtain ⟨e, he, rfl⟩ := List.mem_map.mp hy
  exact ⟨e, he, rfl⟩

/-- Every row of a replayed case holds of its choice, and both row lists are exactly the compatible choices taking
    `A`: the hypotheses of every fold theorem (`fold_*_sound`). -/
theorem nd_rowsHold (x : NDVerdicts) : RowsHold.{u} x.r.N x.A x.Γ x.φ x.conflictRows x.queryRows := by
  refine ⟨x.covers (by simp [NDVerdicts.conflictRows]), x.covers (by simp [NDVerdicts.queryRows]), ?_, ?_⟩
  · intro y hy
    obtain ⟨e, _, rfl⟩ := mem_rows (f := fun _ e => ndConflictRow e) hy
    exact ndConflictRow_holds e.2
  · intro y hy
    obtain ⟨e, _, rfl⟩ := mem_rows (f := fun _ e => ndQueryRow e x.Γ x.φ) hy
    exact ndQueryRow_holds e.2 x.Γ x.φ

/-- The premise rows: exactly the compatible choices taking `A`, each holding. -/
theorem nd_premiseRowsHold (x : NDVerdicts) :
    Covers x.r.N x.A x.premiseRows ∧ ∀ y ∈ x.premiseRows, Holds.{u} x.r.N [] .bottom y.1 y.2 := by
  refine ⟨x.covers (by simp [NDVerdicts.premiseRows]), fun y hy => ?_⟩
  obtain ⟨e, _, rfl⟩ := mem_rows (f := fun _ e => ndPremiseRow e) hy
  exact ndPremiseRow_holds e.2

/-! ## Decoding a choice's evidence -/

theorem notFreeU_of_notFreeX {L : VE.NormDefaults.Wire.LayeredU} {U : UDoc} (hL : L.U = U)
    (h : ¬ VE.NormDefaults.Wire.ConflictFreeX.{0} L.U L.X) : ¬ VE.NormDefaults.ConflictFreeU.{0} U := by
  subst hL
  exact fun hc => h (fun B hB => hc B hB.1)

def castFM {U U' : UDoc} (h : U = U') (m : FilledModel U) : FilledModel U' := h ▸ m

/-- An object's members, `[]` for anything else. -/
def membersOf (j : Json) : List (String × Json) := (VE.Bridge.fields j).toOption.getD []

/-- `j` without the member `k`. -/
def without (j : Json) (k : String) : Json := Json.mkObj ((membersOf j).filter (·.1 != k))

/-- The model a line shows (`shown`, the generator's complete model) extends the checked one: the same domains and
    constants, every table of the checked model and of its `filling` as checked. Only tables the check does not
    read may be added (the outcome tables of the rules, which the situation's wording reads). -/
def shownOk (shown model filling : Json) : Bool :=
  let rel := shown.getObjValD "relations"
  shown.getObjValD "domains" == model.getObjValD "domains" &&
  shown.getObjValD "constants" == model.getObjValD "constants" &&
  (membersOf (model.getObjValD "relations")).all (fun (n, rows) => rel.getObjValD n == rows) &&
  (membersOf filling).all (fun (n, rows) => rel.getObjValD n == rows || (rows == Json.arr #[] && rel.getObjValD n == .null))

/-- The shown model of a piece: its `shown` member, else its checked model. -/
def shownText : String := "InvalidInput: the shown model differs from the checked model"

def shownOf (piece model : Json) : Json :=
  match piece.getObjVal? "shown" with
  | .ok s => s
  | .error _ => model

/-- The filled gaps a shown result depends on (2.2): the unsaid atoms the Kleene value of `ψ` reads at `ρ` with
    nothing filled, each with the regulated predicate, the tuple's ids and the filling's answer; none where the
    value is definite. -/
def gapsOf (U : UDoc) (Mf : VE.FiniteModel Entity) (ρ : List Entity) (ψ : VE.Formula) : List (String × List String × Bool) :=
  let x := VE.NormDefaults.coneEval U Mf ρ ψ
  if x.1.isSome then [] else
  x.2.eraseDups.filterMap (fun (n, vs) => (U.unspec.find? (fun p => VE.NormDefaults.unsaidName p == n)).map
    (fun p => (p, vs.map (·.2), decide (vs ∈ Mf.relations n))))

def gapsJson (gs : List (String × List String × Bool)) : Json :=
  Json.arr (gs.map (fun g => Json.arr #[.str g.1, toJson g.2.1, .bool g.2.2])).toArray

def acceptedNote (name : String) (accepted : Bool) (on : List String) (shown : Option Json)
    (gaps : List (String × List String × Bool)) : PieceNote :=
  { name := name, accepted := accepted, shown := shown, gaps := gaps, conditionalOn := on }

/-- A certificate bound as the norm-defaults route binds a choice's (`ndCertificate`): the regenerated premises of
    `fill U` and the choice's assertions, then `own` as written, and the conclusion `conclusion`. -/
def ndBoundCert (r : AdmittedND) (c : Choice) (own : List Json) (conclusion : Json) (j : Json) :
    Except String VE.Tableau.Certificate := do
  let re := r.b.a.re
  let cert ← VE.CertificateWire.decodeCertificate j
  VE.Route.Wire.bindingOk (VE.NormDefaults.Wire.profilesOf re.lowerJson)
    (← VE.NormDefaults.Wire.canonicalEnvironmentJsonU re.lowerJson)
    ((VE.NormDefaults.Wire.premisesU (choiceU r.N c) (choiceDoc r.N.D c).2).map encF ++ own)
    conclusion cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  pure cert

/-- A base model with a separate filling, on the choice's layered source (`choice-model` under the completion). -/
def ndFilled (r : AdmittedND) (c : Choice) (L : {L : VE.NormDefaults.Wire.LayeredU // L.U = choiceU r.N c})
    (piece : Json) : Except String (FilledModel (choiceU r.N c)) := do
  let S ← VE.NormDefaults.Wire.situationX L.1 (← piece.getObjVal? "model")
  let F ← VE.NormDefaults.Wire.decodeFilling L.1.U S.M (piece.getObjValD "filling")
  unless shownOk (shownOf piece (piece.getObjValD "model")) (piece.getObjValD "model") (piece.getObjValD "filling") do
    throw shownText
  pure (castFM L.2 ⟨S.M, S.valid, F⟩)

def pieceOf (e : Json) (k : String) : Option Json :=
  match e.getObjVal? k with
  | .ok j => if j == .null then none else some j
  | .error _ => none

/-- One choice's evidence under the completion, decoded on its layered source (4.3), and the notes the answer
    shows. A piece Lean refuses is absent from the evidence (its row is `unknown`) and noted with its refusal. -/
def ndEvidenceOf (r : AdmittedND) (c : Choice) (hw : VE.NormDefaults.WellFormedU (choiceU r.N c) = true)
    (e premisesJ conclusionJ : Json) (Γ : List VE.Formula) (φ : VE.Formula) : NDEvidence r.N c × List PieceNote :=
  let empty : NDEvidence r.N c := ⟨hw, [], none, none, none, none, none⟩
  match choiceLayered r c hw with
  | .error err => (empty, [{ name := "conflict", accepted := false, error := some err }])
  | .ok L =>
    let U := choiceU r.N c
    let packages := (e.getObjValD "conflict").getObjValD "packages"
    let certs := (targets (fill L.1.U)).map (VE.NormDefaults.Wire.decodePackageX L.1 packages)
    let free := VE.NormDefaults.Wire.conflictFreeCheckU U certs
    let fillL := VE.NormDefaults.Admission.fillLabelled U
    let pkOk : List VE.Formula → Bool := fun fs => (targets (fill U)).length == certs.length &&
      ((targets (fill U)).zip certs).all (fun (t, k) => match k with
        | some k => VE.Tableau.checkCertificate (envAt (fill U) 0) (VE.Norms.backgroundBase (fill U) ++ fs)
            (VE.Norms.targetConclusion t) k
        | none => false)
    let conflictOn := if free then usedLabels pkOk [] fillL [] else []
    let wit : Option (PLift (¬ VE.NormDefaults.ConflictFreeU.{0} U)) × List PieceNote :=
      match pieceOf e "witness" with
      | none => (none, [])
      | some w => match VE.NormDefaults.Wire.witnessConflictX L.1 (w.getObjValD "witness") with
        | .error err => (none, [{ name := "witness", accepted := false, error := some err }])
        | .ok (_, p, (Mf, ψ, vs)) =>
          let wj := w.getObjValD "witness"
          if shownOk (shownOf w (wj.getObjValD "model")) (wj.getObjValD "model") (wj.getObjValD "filling") then
            (p.map (fun q => ⟨notFreeU_of_notFreeX L.2 q.down⟩),
              [{ name := "witness", accepted := p.isSome, shown := some (shownOf w (wj.getObjValD "model")),
                 gaps := gapsOf U Mf (VE.Norms.tupleVal vs) ψ }])
          else (none, [{ name := "witness", accepted := false, error := some shownText }])
    let own := match premisesJ with | .arr xs => xs.toList | _ => []
    let certPiece (k : String) (own : List Json) (conclusion : Json) : Option VE.Tableau.Certificate × List PieceNote :=
      match pieceOf e k with
      | none => (none, [])
      | some j => match ndBoundCert r c own conclusion (j.getObjValD "certificate") with
        | .error err => (none, [{ name := k, accepted := false, error := some err }])
        | .ok cert => (some cert, [])
    let modelPiece (k : String) : Option (FilledModel U) × Option Json × List PieceNote :=
      match pieceOf e k with
      | none => (none, none, [])
      | some j => match ndFilled r c L j with
        | .error err => (none, none, [{ name := k, accepted := false, error := some err }])
        | .ok m => (some m, some (shownOf j (j.getObjValD "model")), [])
    let (cert, certNotes) := certPiece "certificate" own conclusionJ
    let (unsat, unsatNotes) := certPiece "unsat" [] (encF .bottom)
    let (counter, counterShown, counterNotes) := modelPiece "countermodel"
    let (model, modelShown, modelNotes) := modelPiece "model"
    let ev : NDEvidence r.N c := ⟨hw, certs, wit.1, cert, counter, unsat, model⟩
    let all := (choiceDoc r.N.D c).2 ++ Γ
    let sub := VE.Norms.subst (fill U).T (size (fill U))
    let certOn (Γ' : List VE.Formula) (φ' : VE.Formula) (k : VE.Tableau.Certificate) : List String :=
      usedLabels (fun fs => pkOk fs && VE.Tableau.checkCertificate (fullEnv r.N c)
        (VE.Norms.background (fill U) ++ fs ++ VE.Norms.elaborate (fill U).T ++ ((choiceDoc r.N.D c).2 ++ Γ')) φ' k)
        [] fillL []
    let notes :=
      (if (e.getObjValD "conflict") == .null then [] else [acceptedNote "conflict" free conflictOn none []]) ++
      wit.2 ++ certNotes ++
      (cert.map (fun k => [acceptedNote "certificate" (ndCertOk r.N c Γ φ k && free)
        (if ndCertOk r.N c Γ φ k && free then certOn Γ φ k else []) none []])).getD [] ++
      counterNotes ++
      (counter.map (fun m => [acceptedNote "countermodel" (ndModelOk r.N c Γ φ m false) [] counterShown
        (gapsOf U (m.M.withFill m.F) [] (sub φ))])).getD [] ++
      unsatNotes ++
      (unsat.map (fun k => [acceptedNote "unsat" (ndCertOk r.N c [] .bottom k && free) [] none []])).getD [] ++
      modelNotes ++
      (model.map (fun m => [acceptedNote "model" (ndModelOk r.N c [] .bottom m false) [] modelShown
        (gapsOf U (m.M.withFill m.F) [] (sub (conj (choiceDoc r.N.D c).2)))])).getD []
    let _ := all
    (ev, notes)

end VE.Readings.Wire

/-! ## The English plan (2.3, 2.4; 6.5) -/

namespace VE.Readings
open Lean

structure Line where
  frame : String                  -- E3, E5, E7, E10, E12, E13, E17, E26, E27, E28, E29, E30, E31, E32
  result : Option String          -- R1 to R7
  readings : List (String × Nat)  -- the candidates named, in source order (the `<reading>` slot, 2.3)
  model : Option String           -- the id of the checked model shown
  gaps : List (String × List String × Bool)  -- filled gaps the result depends on: predicate, tuple, value
  label : Option String           -- an E3, E5 or E7 line's premise label

/-- A line of the plan as it is chosen: a sentence that shows no model (its frame, result, the readings or sentences
    it names, its label), or a result that shows a checked model, which is always E12 and names the complete choice
    the model encodes (2.4's non-wordings hold by construction: `plan_no_every_for_models`,
    `plan_model_names_every_set`). A frame that names a sentence and no reading (E13, E29) lists that sentence's set
    with index 0. A `status` line relays the lower route's own status text of a witness, in `label`. -/
inductive PlanItem
  | text (frame : String) (result : Option String) (readings : List (String × Nat)) (label : Option String)
  | shown (result : String) (c : Choice) (model : String) (gaps : List (String × List String × Bool))

def PlanItem.line (D : Doc) : PlanItem → Line
  | .text f r rs l => ⟨f, r, rs, none, [], l⟩
  | .shown r c m g => ⟨"E12", some r, D.sets.map (fun R => (R.id, (c.index R.id).getD 0)), some m, g, none⟩

/-- A string member's text, the empty string for anything else: the plan compares texts, never `Json` values
    (`Json`'s `==` cannot be unfolded in a proof, so a plan that compared them could not be reasoned about). -/
def strOf (j : Json) : String := match j with | .str s => s | _ => ""
def isNull (j : Json) : Bool := match j with | .null => true | _ => false

def jstrings (j : Json) : List String := (VE.Bridge.strings j).toOption.getD []
def jchoice (j : Json) : Choice := (Wire.decodeChoice j).toOption.getD []
def jgaps (j : Json) : List (String × List String × Bool) :=
  match j with
  | .arr xs => xs.toList.filterMap (fun g => match g with
      | .arr #[.str p, ids, .bool v] => some (p, jstrings ids, v)
      | _ => none)
  | _ => []

/-- The sets the used labels restrict: a coupling's sets, the set a narrowing is in force on (a `Fill_T` label
    names no set). -/
def mentioned (D : Doc) (labels : List String) : List String :=
  labels.flatMap (fun l =>
    (D.couplings.filter (fun K => "coupling:" ++ K.id == l)).flatMap (fun K => K.sets.map (·.1)) ++
    (D.narrowings.filter (fun N => "narrowing:" ++ N.id == l)).filterMap (fun N => (inForce D N).map (·.id)))

/-- The label a line cites (E3's lines, and a `status` line's relayed text). -/
def PlanItem.label? : PlanItem → Option String
  | .text _ _ _ l => l
  | .shown .. => none

@[simp] theorem PlanItem.label_text (f : String) (r : Option String) (rs : List (String × Nat)) (l : Option String) :
    (PlanItem.text f r rs l).label? = l := rfl
@[simp] theorem PlanItem.label_shown (r : String) (c : Choice) (m : String) (g : List (String × List String × Bool)) :
    (PlanItem.shown r c m g).label? = none := rfl

/-- One condition's lines (2.3 item 1): a `Fill_T` label's pair sentence, a coupling's E5, one E7 per candidate a
    narrowing in force drops. A label with none of these is never left out of the plan: it gets an `unworded` line,
    which no renderer words, so the answer is unavailable rather than shown without its condition. -/
def conditionLines (D : Doc) (l : String) : List PlanItem :=
  if l.startsWith "unsaid:pair:" then [PlanItem.text "P1" none [] (some l)]
  else if D.couplings.any (fun K => "coupling:" ++ K.id == l) then [.text "E5" none [] (some l)]
  else match D.narrowings.find? (fun N => "narrowing:" ++ N.id == l) with
    | some N => match inForce D N with
      | some R => (List.range R.candidates.length).filterMap (fun i => R.candidates[i]?.bind (fun a =>
          if N.keeps.contains a.id then none else some (.text "E7" none [(R.id, i)] (some l))))
      | none => []
    | none => []

def conditionItems (D : Doc) (l : String) : List PlanItem :=
  if (conditionLines D l).isEmpty then [.text "unworded" none [] (some l)] else conditionLines D l

/-- E3 and its lines: every condition's lines, in the order of the labels; nothing when there is no condition. -/
def providedItems (D : Doc) (labels : List String) : List PlanItem :=
  if labels.isEmpty then [] else .text "E3" none [] none :: labels.flatMap (conditionItems D)

/-- E13 for every open sentence no used label mentions. -/
def independentItems (D : Doc) (labels : List String) : List PlanItem :=
  (D.sets.filter (fun R => !(mentioned D labels).contains R.id)).map (fun R => .text "E13" none [(R.id, 0)] none)

/-- The candidates `A` names, in source order, the last entry of a set winning. -/
def assumedReadings (D : Doc) (A : Choice) : List (String × Nat) :=
  D.sets.filterMap (fun R => (Choice.index A.reverse R.id).map (R.id, ·))

def fullReadings (D : Doc) (c : Choice) : List (String × Nat) := D.sets.map (fun R => (R.id, (c.index R.id).getD 0))

/-- The per-choice entries of an answer with their indices. -/
def perChoice (answer : Json) : List (Nat × Json) :=
  match answer.getObjValD "per_choice" with
  | .arr xs => (List.range xs.size).zip xs.toList
  | _ => []

/-- The first entry whose `key` is `value`, as a shown result of its `piece`. -/
def firstShown (answer : Json) (key value piece result : String) : List PlanItem :=
  match (perChoice answer).find? (fun (_, e) => strOf (e.getObjValD key) == value) with
  | some (k, e) => [.shown result (jchoice (e.getObjValD "choice")) s!"{piece}@{k}"
      (jgaps ((e.getObjValD "gaps").getObjValD piece))]
  | none => []

/-- The plan of `answer`. Its condition lines (E3 and the lines under it) are planned from `labels`, the very value
    the answer's `labels` and `conditional_on` encode (`Run.labelsOf`, `Run.conditionsOf`), never re-read from the
    JSON; `plan_cites_conditions` and `plan_conditions_only` say each label gets its lines and no line cites another. -/
def planItems (D : Doc) (route : Route) (question : String) (labels : List String) (answer : Json) : List PlanItem :=
  if route != .enumerated then [] else
  let res := answer.getObjValD "result"
  let every := if D.sets.length == 1 then "E26" else "E10"
  if question == "conflict" then
    let finding := jstrings (answer.getObjValD "finding_sets")
    let head := if finding.isEmpty then [] else [PlanItem.text "E29" none (finding.map (·, 0)) none]
    let status := strOf (res.getObjValD "status")
    if status == "CONFLICT-FREE" then
      head ++ [.text every (some "R1") [] none] ++ providedItems D labels ++ independentItems D labels
    else if status == "CONFLICT" then
      head ++ (perChoice answer).flatMap (fun (k, e) =>
        if strOf (e.getObjValD "conflict") == "CONFLICT" then
          [PlanItem.shown "R4" (jchoice (e.getObjValD "choice")) s!"witness@{k}"
            (jgaps ((e.getObjValD "gaps").getObjValD "witness"))] ++
          match e.getObjValD "status_text" with
          | .str t => if t.isEmpty then [] else [.text "status" none [] (some t)]
          | _ => []
        else [])
    else head
  else if question == "premises" then
    (if strOf (res.getObjValD "status") == "model" then firstShown answer "premises" "model" "model" "R5" else []) ++
    (match answer.getObjValD "dead_readings" with
     | .arr xs => xs.toList.filterMap (fun d => match d.getObjValD "set", (d.getObjValD "index").getNat? with
         | .str s, .ok i => some (PlanItem.text "E17" none [(s, i)] none)
         | _, _ => none)
     | _ => [])
  else
    let A := jchoice (res.getObjValD "assumed")
    let verdict := strOf (res.getObjValD "verdict")
    if verdict == "ALL" then
      (if A.isEmpty then [PlanItem.text every (some "R2") [] none]
       else [.text "E12" (some "R2") (assumedReadings D A) none]) ++ providedItems D labels
    else if verdict == "SOME" then
      [PlanItem.text "E12" (some "R2") (fullReadings D (jchoice ((res.getObjValD "proof").getObjValD "choice"))) none] ++
        providedItems D labels ++ firstShown answer "query" "refuted" "countermodel" "R3"
    else if verdict == "NONE" then
      (if D.sets.length ≥ 2 && A.isEmpty then [PlanItem.text "E27" none [] none] else []) ++
      (perChoice answer).flatMap (fun (k, e) =>
        if strOf (e.getObjValD "query") == "refuted" then
          [PlanItem.shown "R3" (jchoice (e.getObjValD "choice")) s!"countermodel@{k}"
            (jgaps ((e.getObjValD "gaps").getObjValD "countermodel"))]
        else []) ++
      providedItems D labels
    else if !isNull (res.getObjValD "countermodel") && A.isEmpty then
      PlanItem.text "E28" none [] none :: firstShown answer "query" "refuted" "countermodel" "R3"
    else []

/-- The plan of the case's decoded document `D` (2.4; review E5), its conditions planned from the answer's
    `labels` (`jstrings_toJson`: exactly the list the answer encodes there). -/
def englishPlan (D : Doc) (route : Route) (question : String) (answer : Lean.Json) : List Line :=
  (planItems D route question (jstrings (answer.getObjValD "labels")) answer).map (PlanItem.line D)

theorem jstrings_toJson (l : List String) : jstrings (toJson l) = l := by
  have h : ∀ l : List String, (l.map (fun x => (toJson x : Json))).mapM Json.getStr? = .ok l := by
    intro l
    induction l with
    | nil => rfl
    | cons x xs ih =>
      simp only [List.map_cons, List.mapM_cons, ih]
      rfl
  have e : (toJson l : Json) = Json.arr (l.map (fun x => (toJson x : Json))).toArray := by
    simp only [toJson, List.toJson, Array.toJson, List.map_toArray]
  have hs : VE.Bridge.strings (Json.arr (l.map (fun x => (toJson x : Json))).toArray) = .ok l := by
    have hd : VE.Bridge.strings (Json.arr (l.map (fun x => (toJson x : Json))).toArray) =
        (l.map (fun x => (toJson x : Json))).toArray.toList.mapM Json.getStr? := rfl
    rw [hd, List.toList_toArray, h]
  simp only [jstrings, e, hs]
  rfl

/-! ### The condition lines (2.3 item 1): every label gets its lines, and no line cites another label -/

theorem conditionLines_label (D : Doc) (l : String) : ∀ it ∈ conditionLines D l, it.label? = some l := by
  intro it hit
  unfold conditionLines at hit
  split at hit
  · simp only [List.mem_singleton] at hit; subst hit; rfl
  · split at hit
    · simp only [List.mem_singleton] at hit; subst hit; rfl
    · split at hit
      · split at hit
        · obtain ⟨i, _, hi⟩ := List.mem_filterMap.mp hit
          obtain ⟨a, _, ha⟩ := Option.bind_eq_some_iff.mp hi
          split at ha
          · cases ha
          · cases ha; rfl
        · cases hit
      · cases hit

theorem conditionItems_label (D : Doc) (l : String) : ∀ it ∈ conditionItems D l, it.label? = some l := by
  intro it hit
  unfold conditionItems at hit
  split at hit
  · simp only [List.mem_singleton] at hit; subst hit; rfl
  · exact conditionLines_label D l it hit

theorem conditionItems_ne_nil (D : Doc) (l : String) : conditionItems D l ≠ [] := by
  unfold conditionItems
  split
  · simp
  · rename_i h
    intro he
    rw [he] at h
    exact h rfl

theorem providedItems_label (D : Doc) (labels : List String) :
    ∀ it ∈ providedItems D labels, it.label? = none ∨ ∃ l ∈ labels, it.label? = some l := by
  intro it hit
  unfold providedItems at hit
  split at hit
  · cases hit
  · rcases List.mem_cons.mp hit with rfl | hit
    · exact Or.inl rfl
    · obtain ⟨l, hl, hit⟩ := List.mem_flatMap.mp hit
      exact Or.inr ⟨l, hl, conditionItems_label D l it hit⟩

theorem providedItems_cites (D : Doc) (labels : List String) :
    ∀ l ∈ labels, ∃ it ∈ providedItems D labels, it.label? = some l := by
  intro l hl
  obtain ⟨it, hit⟩ := List.exists_mem_of_ne_nil _ (conditionItems_ne_nil D l)
  refine ⟨it, ?_, conditionItems_label D l it hit⟩
  unfold providedItems
  split
  · rename_i h
    simp only [List.isEmpty_iff] at h
    subst h
    cases hl
  · exact List.mem_cons_of_mem _ (List.mem_flatMap.mpr ⟨l, hl, hit⟩)

/-- Where the plan states conditions (a CONFLICT-FREE conflict answer, an ALL, a SOME, a NONE), every label in `labels`
    is cited by a line of the plan. -/
theorem plan_cites_conditions (D : Doc) (q : String) (labels : List String) (answer : Lean.Json)
    (h : (q = "conflict" ∧ strOf ((answer.getObjValD "result").getObjValD "status") = "CONFLICT-FREE") ∨
      (q = "query" ∧ (strOf ((answer.getObjValD "result").getObjValD "verdict") = "ALL" ∨
        strOf ((answer.getObjValD "result").getObjValD "verdict") = "SOME" ∨
        strOf ((answer.getObjValD "result").getObjValD "verdict") = "NONE"))) :
    ∀ l ∈ labels, ∃ it ∈ planItems D .enumerated q labels answer, it.label? = some l := by
  intro l hl
  obtain ⟨it, hit, he⟩ := providedItems_cites D labels l hl
  refine ⟨it, ?_, he⟩
  rcases h with ⟨rfl, hs⟩ | ⟨rfl, hs | hs | hs⟩
  all_goals
    simp (config := {decide := true}) only [planItems, hs, Bool.false_eq_true, ↓reduceIte]
    first
      | simp (config := {decide := true}) [hit]
      | (split <;> simp (config := {decide := true}) [hit])

theorem firstShown_label (a : Lean.Json) (k v p r : String) : ∀ x ∈ firstShown a k v p r, x.label? = none := by
  intro x hx
  unfold firstShown at hx
  split at hx
  · simp only [List.mem_singleton] at hx; subst hx; rfl
  · cases hx

theorem independentItems_label (D : Doc) (ls : List String) : ∀ x ∈ independentItems D ls, x.label? = none := by
  intro x hx
  obtain ⟨R, _, rfl⟩ := List.mem_map.mp hx
  rfl

theorem providedItems_only (D : Doc) (ls : List String) : ∀ x ∈ providedItems D ls, ∀ l, x.label? = some l → l ∈ ls := by
  intro x hx l hl
  rcases providedItems_label D ls x hx with h | ⟨l', hl', h⟩
  · rw [h] at hl; cases hl
  · rw [h] at hl; cases hl; exact hl'

/-- No line of a plan cites a label outside `labels`, other than a `status` line relaying a witness's own text. -/
theorem plan_conditions_only (D : Doc) (q : String) (labels : List String) (answer : Lean.Json) :
    ∀ it ∈ planItems D .enumerated q labels answer, ∀ l, it.label? = some l →
      l ∈ labels ∨ it = .text "status" none [] (some l) := by
  have hf := firstShown_label
  have hi := independentItems_label D
  have hp := providedItems_only D
  intro it hit l hl
  unfold planItems at hit
  simp (config := {decide := true}) only [Bool.false_eq_true, ↓reduceIte] at hit
  repeat' split at hit
  all_goals (revert hl; revert hit; revert it)
  all_goals simp only [List.mem_append, List.mem_cons, List.mem_singleton, List.mem_flatMap, List.mem_filterMap,
    List.not_mem_nil, or_false, false_or, or_imp, forall_and, forall_exists_index, and_imp, forall_eq,
    PlanItem.label_text, PlanItem.label_shown, reduceCtorEq, false_implies, implies_true, and_true, true_and]
  all_goals (repeat' apply And.intro)
  all_goals first
    | (intro it h hl; exact Or.inl (hp _ _ h l hl))
    | (intro it h hl; rw [hi _ _ h] at hl; cases hl)
    | (intro it h hl; rw [hf _ _ _ _ _ _ h] at hl; cases hl)
    | (intro it x _ h hl
       repeat' split at h
       all_goals simp only [List.mem_append, List.mem_singleton, List.mem_cons, List.not_mem_nil, or_false,
         Option.some.injEq, reduceCtorEq] at h
       all_goals (try rcases h with h | h)
       all_goals (try subst h)
       all_goals (try simp only [PlanItem.label_text, PlanItem.label_shown, reduceCtorEq, Option.some.injEq] at hl)
       all_goals (try subst hl)
       all_goals first
         | exact Or.inr rfl
         | exact h.elim
         | done)

/-- composition-s2 2.4's non-wordings hold of every plan. -/
theorem plan_no_every_for_models (D : Doc) (route : Route) (q : String) (a : Lean.Json) :
  ∀ l ∈ englishPlan D route q a, l.model.isSome → l.frame ∉ ["E10", "E26", "E30"] := by
  intro l hl hm
  obtain ⟨x, _, rfl⟩ := List.mem_map.mp hl
  cases x with
  | text => simp [PlanItem.line] at hm
  | shown => simp [PlanItem.line]
theorem plan_model_names_every_set (D : Doc) (route : Route) (q : String) (a : Lean.Json) :
  ∀ l ∈ englishPlan D route q a, l.model.isSome → l.readings.map (·.1) = D.sets.map (·.id) := by
  intro l hl hm
  obtain ⟨x, _, rfl⟩ := List.mem_map.mp hl
  cases x with
  | text => simp [PlanItem.line] at hm
  | shown => simp [PlanItem.line, List.map_map, Function.comp_def]

def Line.json (l : Line) : Json :=
  Json.mkObj [("frame", .str l.frame), ("result", match l.result with | some r => .str r | none => .null),
    ("readings", Json.arr (l.readings.map (fun x => Json.arr #[.str x.1, toJson x.2])).toArray),
    ("model", match l.model with | some m => .str m | none => .null),
    ("gaps", Wire.gapsJson l.gaps), ("label", match l.label with | some t => .str t | none => .null)]

end VE.Readings

/-! ## The kind `readings-verdicts` -/

namespace VE.Readings.Run
open Lean
open VE.Readings
open VE.Readings.Wire
open VE.Bridge (stringField)
open VE.Norms (envAt size)
open VE.NormDefaults (fill)

/-- One compatible choice's rows and what the answer shows of its evidence. -/
structure RowInfo where
  choice : Choice
  conflict : ChoiceResult
  query : ChoiceResult
  premise : ChoiceResult
  notes : List PieceNote

def RowInfo.note (i : RowInfo) (k : String) : Option PieceNote := i.notes.find? (·.name == k)
def RowInfo.on (i : RowInfo) (k : String) : List String := ((i.note k).map (·.conditionalOn)).getD []
def RowInfo.shown (i : RowInfo) (k : String) : Json := (((i.note k).bind (·.shown))).getD .null

/-! ### Without the completion: the lower route's own answers (as `readings-choice` gives them) -/

/-- A piece of evidence run as `readings-choice` runs its inner case on the choice's regenerated document. -/
def lowerRun (lower : List String → Json → Json) (id : String) (b : Admitted2) (c : Choice) (inner : Json) : Json :=
  match runChoice lower id b (Json.mkObj [("choice", choiceJson c), ("inner", inner)]) with
  | .ok a => a
  | .error e => Json.mkObj [("status", .str "error"), ("error", .str e)]

def innerOf (a : Json) : Json := a.getObjValD "inner"
def lowerOk (a : Json) : Bool := a.getObjValD "status" == .str "ok" && (innerOf a).getObjValD "status" == .str "ok"
def lowerError (a : Json) : Option String :=
  if a.getObjValD "status" != .str "ok" then some ((a.getObjValD "error").getStr?.toOption.getD "error")
  else if (innerOf a).getObjValD "status" != .str "ok" then some (((innerOf a).getObjValD "error").getStr?.toOption.getD "error")
  else none
def optStr (j : Json) : Option String := match j with | .str t => some t | _ => none

/-- A lower piece's note: accepted, its refusal, its shown model and the labels its answer depends on. -/
def lowerNote (name : String) (a : Json) (accepted : Bool) (shown : Option Json) : PieceNote :=
  { name := name, accepted := accepted, error := lowerError a, shown := shown,
    conditionalOn := jstrings ((innerOf a).getObjValD "conditional_on"),
    statusText := optStr ((innerOf a).getObjValD "status_text") }

/-- One choice's rows on the lower route: the conflict packages, then a witness when they are not accepted; a
    certificate with the conflict packages (S2a 14.8) or a countermodel; a certificate of `⊥` or a model. Each is the
    lower route's answer on the choice's regenerated document. -/
def lowerInfo (lower : List String → Json → Json) (id : String) (b : Admitted2) (c : Choice)
    (e premisesJ conclusionJ : Json) : RowInfo :=
  let run := lowerRun lower id b c
  let conflictPiece := pieceOf e "conflict"
  let pk := conflictPiece.map run
  let free := pk.any (fun a => lowerOk a && (innerOf a).getObjValD "verdict" == .str "CONFLICT-FREE")
  let packs := (conflictPiece.map (without · "kind")).getD (Json.mkObj [])
  let wit := if free then none else (pieceOf e "witness").map (fun w =>
    let wj := w.getObjValD "witness"
    let ok := shownOk (shownOf w (wj.getObjValD "model")) (wj.getObjValD "model") .null
    (ok, shownOf w (wj.getObjValD "model"), run (without w "shown")))
  let conflictB := wit.any (fun (ok, _, a) => ok && lowerOk a && (innerOf a).getObjValD "verdict" == .str "CONFLICT")
  let withQ (p : Json) (ps conclusion : Json) : Json := ((without p "shown").setObjVal! "premises" ps).setObjVal! "conclusion" conclusion
  let cert := (pieceOf e "certificate").map (fun p => run ((withQ p premisesJ conclusionJ).setObjVal! "conflict" packs))
  let proved := cert.any (fun a => lowerOk a && a.getObjValD "accepted" == .bool true && (innerOf a).getObjValD "valid" == .bool true)
  let modelOk (p : Json) (a : Json) : Bool := shownOk (shownOf p (p.getObjValD "model")) (p.getObjValD "model") .null &&
    lowerOk a && (innerOf a).getObjValD "valid" == .bool true && (innerOf a).getObjValD "conclusion_value" == .bool false
  let counter := (pieceOf e "countermodel").map (fun p => (p, run (withQ p premisesJ conclusionJ)))
  let refuted := counter.any (fun (p, a) => modelOk p a)
  let unsat := (pieceOf e "unsat").map (fun p => run ((withQ p (.arr #[]) (encF .bottom)).setObjVal! "conflict" packs))
  let inconsistent := unsat.any (fun a => lowerOk a && a.getObjValD "accepted" == .bool true && (innerOf a).getObjValD "valid" == .bool true)
  let model := (pieceOf e "model").map (fun p => (p, run (withQ p (.arr #[]) .null)))
  let modelB := model.any (fun (p, a) => modelOk p a)
  { choice := c,
    conflict := if free then .free else if conflictB then .conflict else .unknown,
    query := if proved then .proved else if refuted then .refuted else .unknown,
    premise := if inconsistent then .inconsistent else if modelB then .model else .unknown,
    notes := (pk.map (fun a => [lowerNote "conflict" a free none])).getD [] ++
      (wit.map (fun (ok, sh, a) => [{ lowerNote "witness" a conflictB (some sh) with
        error := if ok then lowerError a else some shownText }])).getD [] ++
      (cert.map (fun a => [lowerNote "certificate" a proved none])).getD [] ++
      (counter.map (fun (p, a) => [{ lowerNote "countermodel" a refuted (some (shownOf p (p.getObjValD "model"))) with
        error := if shownOk (shownOf p (p.getObjValD "model")) (p.getObjValD "model") .null then lowerError a
          else some shownText }])).getD [] ++
      (unsat.map (fun a => [lowerNote "unsat" a inconsistent none])).getD [] ++
      (model.map (fun (p, a) => [{ lowerNote "model" a modelB (some (shownOf p (p.getObjValD "model"))) with
        error := if shownOk (shownOf p (p.getObjValD "model")) (p.getObjValD "model") .null then lowerError a
          else some shownText }])).getD [] }

/-- A replayed `readings-verdicts` case on the lower route: the document, `assumed`, and one row per compatible
    choice taking `A`, in canonical order. -/
structure LowerVerdicts where
  b : Admitted2
  A : Choice
  rows : List RowInfo
  hrows : rows.map (·.choice) = chosenOf b.D A

def LowerVerdicts.conflictRows (x : LowerVerdicts) : List (Choice × ChoiceResult) := x.rows.map (fun i => (i.choice, i.conflict))
def LowerVerdicts.queryRows (x : LowerVerdicts) : List (Choice × ChoiceResult) := x.rows.map (fun i => (i.choice, i.query))
def LowerVerdicts.premiseRows (x : LowerVerdicts) : List (Choice × ChoiceResult) := x.rows.map (fun i => (i.choice, i.premise))

/-! ### Under the completion: Lean's checkers on `choiceU N c` -/

def ndInfo (x : NDVerdicts) (e : (c : Choice) × NDEvidence x.r.N c) (notes : List PieceNote) : RowInfo :=
  { choice := e.1, conflict := ndConflictRow e.2, query := ndQueryRow e.2 x.Γ x.φ, premise := ndPremiseRow e.2,
    notes := notes }

def ndInfos (x : NDVerdicts) : List RowInfo :=
  (x.evs.zip (x.notes ++ List.replicate x.evs.length [])).map (fun (e, n) => ndInfo x e n)

theorem ndInfos_rows (x : NDVerdicts) :
    (ndInfos x).map (fun i => (i.choice, i.conflict)) = x.conflictRows ∧
    (ndInfos x).map (fun i => (i.choice, i.query)) = x.queryRows ∧
    (ndInfos x).map (fun i => (i.choice, i.premise)) = x.premiseRows := by
  have hl : (x.notes ++ List.replicate x.evs.length []).length ≥ x.evs.length := by simp
  refine ⟨?_, ?_, ?_⟩ <;>
  · simp only [ndInfos, NDVerdicts.conflictRows, NDVerdicts.queryRows, NDVerdicts.premiseRows,
      List.map_map]
    apply List.ext_getElem
    · simp only [List.length_map, List.length_zip]; omega
    · intro n h1 h2
      simp [ndInfo]

/-- The evidence entry of choice `c`: the first entry naming it, else none. -/
def entryFor (evidence : List Json) (c : Choice) : Json :=
  (evidence.find? (fun e => jchoice (e.getObjValD "choice") == c)).getD (Json.mkObj [])

def evidenceList (j : Json) : List Json := match j.getObjValD "evidence" with | .arr xs => xs.toList | _ => []

/-- The request's premises and conclusion over the complete environment of the first choice's filled document
    (`⊥` and none for the conflict and premises questions). -/
def queryFormulas (E : VE.Environment) (question : String) (j : Json) : Except String (List VE.Formula × VE.Formula) := do
  if question != "query" then return ([], .bottom)
  let Γ ← match j.getObjValD "premises" with
    | .null => pure []
    | p => VE.Route.Wire.decodeFormulas E p
  let φ ← VE.Route.Wire.decodeClosed E (← j.getObjVal? "conclusion")
  pure (Γ, φ)

/-- The replay under the completion: the document admitted (4.1), at most 64 compatible choices, the ones taking
    `A` (some, else `ReadingsUnsatisfiable`), each checked by `ndChoiceText`'s checks (its `WellFormedU`), and its
    evidence decoded on its own filled document. -/
def replayND (f : AdmittedNDFull) (question : String) (A : Choice) (j : Json) : Except String NDVerdicts := do
  let r := f.r
  if hr : supReady r.N.D = true then
    if hle : (choices r.N.D).length ≤ maxChoices then
      let chosen := chosenOf r.N.D A
      if chosen.isEmpty then throw (untakenText r.N.D A)
      if hw : chosen.all (fun c => ndDocText r.b.a.re (choiceU r.N c) == none) = true then
        let (Γ, φ) ← queryFormulas (fullEnv r.N (chosen.headD [])) question j
        let evidence := evidenceList j
        let premisesJ := match j.getObjValD "premises" with | .null => Json.arr #[] | p => p
        let pairs : List ((c : Choice) × (NDEvidence r.N c × List PieceNote)) := chosen.attach.map (fun x =>
          ⟨x.1, ndEvidenceOf r x.1 (wellFormedU_of_ndDocText (by
              have := List.all_eq_true.mp hw x.1 x.2
              simpa using this)) (entryFor evidence x.1) premisesJ (j.getObjValD "conclusion") Γ φ⟩)
        pure ⟨r, A, Γ, φ, hr, hle, pairs.map (fun p => ⟨p.1, p.2.1⟩), by
          simp only [pairs, List.map_map, Function.comp_def]
          exact List.attach_map_subtype_val _, pairs.map (·.2.2)⟩
      else
        let c := (chosen.find? (fun c => ndDocText r.b.a.re (choiceU r.N c) != none)).getD []
        throw ((ndChoiceText r.b.a.re r.N c).getD "InvalidInput: norm-defaults document is not well formed")
    else throw "readings-verdicts: more than 64 compatible readings"
  else throw "InvalidInput: readings document is not well-formed"

/-- The `readings-verdicts` input under the completion: environment, document, question, `assumed`, evidence. -/
def replayVerdictsND (j : Json) : Except String NDVerdicts := do
  let f ← admitNDFullJ (← j.getObjVal? "environment") (← j.getObjVal? "document")
  replayND f (← stringField j "question") (← decodeChoice (j.getObjValD "assumed")) j

/-! ### The wire theorems (6.4): every verdict a replayed case folds to is its fold theorem's conclusion -/

theorem readings_wire_verdicts_all (j : Json) (x : NDVerdicts) (h : replayVerdictsND j = .ok x)
    (hv : foldEntailment x.conflictRows x.queryRows = .all) :
    ∀ c, Compatible x.r.N.D c → (∀ y ∈ x.A, y ∈ c) →
      VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N c) ∧
      VE.NormDefaults.EntailsU.{u} (choiceU x.r.N c) ((choiceDoc x.r.N.D c).2 ++ x.Γ) x.φ := by
  have _ := h
  exact fold_all_sound _ _ _ _ _ _ (nd_rowsHold x) hv

theorem readings_wire_verdicts_none (j : Json) (x : NDVerdicts) (h : replayVerdictsND j = .ok x)
    (hv : foldEntailment x.conflictRows x.queryRows = .none) :
    ∀ c, Compatible x.r.N.D c → (∀ y ∈ x.A, y ∈ c) →
      VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N c) ∧
      CounterU (choiceU x.r.N c) ((choiceDoc x.r.N.D c).2 ++ x.Γ) x.φ := by
  have _ := h
  exact fold_none_sound _ _ _ _ _ _ (nd_rowsHold x) hv

theorem readings_wire_verdicts_some (j : Json) (x : NDVerdicts) (h : replayVerdictsND j = .ok x)
    (hv : foldEntailment x.conflictRows x.queryRows = .some) :
    (∀ c, Compatible x.r.N.D c → (∀ y ∈ x.A, y ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N c)) ∧
    (∃ c, Compatible x.r.N.D c ∧ (∀ y ∈ x.A, y ∈ c) ∧
      VE.NormDefaults.EntailsU.{u} (choiceU x.r.N c) ((choiceDoc x.r.N.D c).2 ++ x.Γ) x.φ) ∧
    (∃ c, Compatible x.r.N.D c ∧ (∀ y ∈ x.A, y ∈ c) ∧ CounterU (choiceU x.r.N c) ((choiceDoc x.r.N.D c).2 ++ x.Γ) x.φ) := by
  have _ := h
  exact fold_some_sound _ _ _ _ _ _ (nd_rowsHold x) hv

theorem readings_wire_verdicts_conflict_free (j : Json) (x : NDVerdicts) (h : replayVerdictsND j = .ok x)
    (hv : foldConflict x.conflictRows = .free) :
    ∀ c, Compatible x.r.N.D c → (∀ y ∈ x.A, y ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N c) := by
  have _ := h
  obtain ⟨hc, _, hr, _⟩ := nd_rowsHold.{u} x
  exact fold_conflict_free_sound _ _ _ hc hr hv

theorem readings_wire_verdicts_conflict (j : Json) (x : NDVerdicts) (h : replayVerdictsND j = .ok x)
    (hv : foldConflict x.conflictRows = .conflict) :
    ∃ c, Compatible x.r.N.D c ∧ (∀ y ∈ x.A, y ∈ c) ∧ ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU x.r.N c) := by
  have _ := h
  obtain ⟨hc, _, hr, _⟩ := nd_rowsHold.{0} x
  exact fold_conflict_sound _ _ _ hc hr hv

theorem readings_wire_verdicts_model (j : Json) (x : NDVerdicts) (h : replayVerdictsND j = .ok x)
    (hv : foldPremises x.premiseRows = .model) :
    ∃ c, Compatible x.r.N.D c ∧ (∀ y ∈ x.A, y ∈ c) ∧ ConsistentU (choiceU x.r.N c) (choiceDoc x.r.N.D c).2 := by
  have _ := h
  obtain ⟨hc, hr⟩ := nd_premiseRowsHold.{0} x
  exact fold_premises_model_sound _ _ _ hc hr hv

theorem readings_wire_verdicts_inconsistent (j : Json) (x : NDVerdicts) (h : replayVerdictsND j = .ok x)
    (hv : foldPremises x.premiseRows = .inconsistent) :
    ∀ c, Compatible x.r.N.D c → (∀ y ∈ x.A, y ∈ c) →
      VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N c) ∧
      VE.NormDefaults.EntailsU.{u} (choiceU x.r.N c) (choiceDoc x.r.N.D c).2 .bottom := by
  have _ := h
  obtain ⟨hc, hr⟩ := nd_premiseRowsHold.{u} x
  exact fold_premises_inconsistent_sound _ _ _ hc hr hv

/-- On the lower route the rows are exactly the compatible choices taking `A` that the search lists, and each
    verdict reads its rows as the fold says: the lower route's own answers on each choice's regenerated document
    (its theorems say what each answer means). -/
theorem lower_verdicts_rows (x : LowerVerdicts) :
    x.rows.map (·.choice) = chosenOf x.b.D x.A ∧ ∀ c ∈ chosenOf x.b.D x.A, Compatible x.b.D c ∧ ∀ y ∈ x.A, y ∈ c := by
  refine ⟨x.hrows, fun c hc => ?_⟩
  simp only [chosenOf, List.mem_filter, List.all_eq_true, List.contains_iff_mem] at hc
  exact ⟨compatible_of_mem_search _ _ _ hc.1, hc.2⟩

theorem lower_verdicts_all (x : LowerVerdicts) (hv : foldEntailment x.conflictRows x.queryRows = .all) :
    x.rows ≠ [] ∧ ∀ i ∈ x.rows, i.conflict = .free ∧ i.query = .proved := by
  obtain ⟨hf, hne, hall⟩ := foldEntailment_all hv
  obtain ⟨_, hfree⟩ := foldConflict_free hf
  refine ⟨fun h => hne (by simp [LowerVerdicts.queryRows, h]), fun i hi => ⟨?_, ?_⟩⟩
  · exact hfree (i.choice, i.conflict) (List.mem_map.mpr ⟨i, hi, rfl⟩)
  · exact hall (i.choice, i.query) (List.mem_map.mpr ⟨i, hi, rfl⟩)

theorem lower_verdicts_none (x : LowerVerdicts) (hv : foldEntailment x.conflictRows x.queryRows = .none) :
    x.rows ≠ [] ∧ ∀ i ∈ x.rows, i.conflict = .free ∧ i.query = .refuted := by
  obtain ⟨hf, hne, hall⟩ := foldEntailment_none hv
  obtain ⟨_, hfree⟩ := foldConflict_free hf
  refine ⟨fun h => hne (by simp [LowerVerdicts.queryRows, h]), fun i hi => ⟨?_, ?_⟩⟩
  · exact hfree (i.choice, i.conflict) (List.mem_map.mpr ⟨i, hi, rfl⟩)
  · exact hall (i.choice, i.query) (List.mem_map.mpr ⟨i, hi, rfl⟩)

theorem lower_verdicts_some (x : LowerVerdicts) (hv : foldEntailment x.conflictRows x.queryRows = .some) :
    (∀ i ∈ x.rows, i.conflict = .free) ∧ (∃ i ∈ x.rows, i.query = .proved) ∧ ∃ i ∈ x.rows, i.query = .refuted := by
  obtain ⟨hf, ⟨p, hp, hpp⟩, ⟨n, hn, hnn⟩⟩ := foldEntailment_some hv
  obtain ⟨_, hfree⟩ := foldConflict_free hf
  refine ⟨fun i hi => hfree (i.choice, i.conflict) (List.mem_map.mpr ⟨i, hi, rfl⟩), ?_, ?_⟩
  · obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hp
    exact ⟨i, hi, hpp⟩
  · obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hn
    exact ⟨i, hi, hnn⟩

/-! ### The answer -/

def word : ChoiceResult → String
  | .free => "CONFLICT-FREE"
  | .conflict => "CONFLICT"
  | .proved => "proved"
  | .refuted => "refuted"
  | .model => "model"
  | .inconsistent => "INCONSISTENT"
  | .unknown => "UNKNOWN"

/-- The first occurrence of each label, in order. -/
def dedupStrings (l : List String) : List String := l.foldl (fun acc x => if acc.contains x then acc else acc ++ [x]) []

/-- The conditions a verdict rests on (2.3 item 1): every label a row's accepted evidence uses (`on k`: the conflict
    packages' for a CONFLICT-FREE answer, the certificates' for an ALL, whose labels include their conflict
    packages'), then the restrictions, each once. One value: the result's `conditional_on`, the answer's `labels`
    under the completion and the plan's condition lines are all this list (`verdicts_conditions_*`). -/
def conditionsOf (k : String) (D : Doc) (A : Choice) (infos : List RowInfo) : List String :=
  dedupStrings (infos.flatMap (·.on k) ++ restrictionsFor D A)

/-- W2's budget shape past 64 compatible choices, after its status. -/
def overBudgetRest (D : Doc) : List (String × Json) :=
  [("route", .str "enumerated"), ("budget", Json.mkObj [("max_choices", toJson maxChoices)]),
   ("units", toJson (D.sets.map (·.unit)))]

def overBudgetFields (D : Doc) : List (String × Json) := ("status", .str "UNKNOWN") :: overBudgetRest D

def statusesJson (infos : List RowInfo) (f : RowInfo → ChoiceResult) : Json :=
  Json.arr (infos.map (fun i => Json.mkObj [("choice", choiceJson i.choice), ("status", .str (word (f i)))])).toArray

/-- The conflict answer over the compatible choices taking `A` (`foldConflict`), in the form composition-s2 4.6's
    report gives it. -/
def conflictResult (D : Doc) (A : Choice) (infos : List RowInfo) : Json :=
  let rest := restrictionsFor D A
  match foldConflict (infos.map (fun i => (i.choice, i.conflict))) with
  | .free => Json.mkObj [("status", .str "CONFLICT-FREE"), ("route", .str "enumerated"),
      ("conditional_on", toJson (conditionsOf "conflict" D A infos)),
      ("restrictions", toJson rest), ("reading_premises_used", toJson rest),
      ("status_text", .str s!"CONFLICT-FREE among rules on the same act under every reading ({infos.length} readings checked one at a time)"),
      ("choices", statusesJson infos (·.conflict))]
  | s =>
    let witnesses := infos.filter (·.conflict == .conflict)
    Json.mkObj [("status", .str (word s)), ("route", .str "enumerated"),
      ("status_text", .str (match witnesses.head? with
        | some i => s!"CONFLICT under {choiceText D i.choice}"
        | none => "UNKNOWN: a reading's conflict status is not certified")),
      ("choices", statusesJson infos (·.conflict)),
      ("witnesses", Json.arr (witnesses.map (fun i => Json.mkObj [("choice", choiceJson i.choice),
        ("model", i.shown "witness"),
        ("status_text", match (i.note "witness").bind (·.statusText) with | some t => .str t | none => .null)])).toArray)]

/-- The narrowing in force that drops candidate `i` of `R`, the first in document order. -/
def droppedBy (D : Doc) (R : ReadingSet) (i : Nat) : Option String :=
  (D.narrowings.find? (fun N => N.set == R.id && N.version == R.version &&
    (R.candidates[i]?.map (fun a => !N.keeps.contains a.id)).getD false)).map (·.id)

def candidatesOf (D : Doc) : List (ReadingSet × Nat) := D.sets.flatMap (fun R => (List.range R.candidates.length).map (R, ·))

/-- The candidates no compatible choice takes and no narrowing drops: each is dead only with its certificate. -/
def untakenOf (D : Doc) (infos : List RowInfo) : List (String × Nat) :=
  (candidatesOf D).filterMap (fun (R, i) =>
    if infos.any (·.choice.contains (R.id, i)) || (droppedBy D R i).isSome then none else some (R.id, i))

/-- S2a's dead readings (1.9): every untaken candidate with a certificate of `¬χ` from `choiceCore D` that Lean
    accepts (`deadCheck`), or none when one of them has none (an incomplete list is never reported). -/
def deadOf (D : Doc) (infos : List RowInfo) (dead : List Json) : Option (List (String × Nat)) × List Json :=
  let ok := fun (s : String) (i : Nat) => dead.any (fun d => d.getObjValD "set" == .str s &&
    (d.getObjValD "index").getNat?.toOption == some i &&
    match VE.CertificateWire.decodeCertificate (d.getObjValD "certificate") with
    | .ok cert => supReady D && deadCheck D s i cert
    | .error _ => false)
  let untaken := untakenOf D infos
  (if untaken.all (fun (s, i) => ok s i) then some untaken else none,
   dead.map (fun d => match d.getObjValD "set", (d.getObjValD "index").getNat? with
     | .str s, .ok i => Json.mkObj [("set", .str s), ("index", toJson i),
         ("accepted", .bool (ok s i && untaken.contains (s, i)))]
     | _, _ => Json.mkObj [("accepted", .bool false)]))

def premisesResult (D : Doc) (infos : List RowInfo) (dead : Option (List (String × Nat))) : Json :=
  let overall := foldPremises (infos.map (fun i => (i.choice, i.premise)))
  let deadL := dead.getD []
  Json.mkObj ([("status", .str (word overall)), ("route", .str "enumerated"), ("evidence", .str "per choice"),
      ("choices", statusesJson infos (·.premise))] ++
    (if overall == .model then match infos.find? (·.premise == .model) with
      | some i => [("choice", choiceJson i.choice), ("model", i.shown "model")]
      | none => []
     else []) ++
    [("candidates", Json.arr ((candidatesOf D).map (fun (R, i) =>
      let base : List (String × Json) := [("set", .str R.id), ("index", toJson i)]
      Json.mkObj (base ++ match droppedBy D R i with
        | some n => [("status", .str "narrowed"), ("narrowing", .str n)]
        | none =>
          if deadL.contains (R.id, i) then [("status", .str "dead")]
          else
            let taking := infos.filter (·.choice.contains (R.id, i))
            if taking.isEmpty then [("status", .str "UNKNOWN"), ("reason", .str (untakenText D [(R.id, i)]))]
            else [("status", .str (word (foldPremises (taking.map (fun t => (t.choice, t.premise))))))]))).toArray)])

/-- The `assumed` member a result keeps when the request named readings (composition-s2 review A of looprecheck1). -/
def assumedFields : Option Choice → List (String × Json)
  | some A => [("assumed", choiceJson A)]
  | none => []

def proofJson (i : RowInfo) : Json :=
  Json.mkObj [("choice", choiceJson i.choice), ("outcome", .str "proof"), ("conditional_on", toJson (i.on "certificate"))]
def counterJson (i : RowInfo) : Json :=
  Json.mkObj [("choice", choiceJson i.choice), ("outcome", .str "countermodel"), ("model", i.shown "countermodel")]

/-- The query's answer (4.4): the gate of 14.8, then `foldEntailment`, naming what an UNKNOWN rests on
    (`reasonOf`). -/
def entailmentResult (D : Doc) (A : Choice) (assumed : Option Choice) (infos : List RowInfo) : Json :=
  let cs := infos.map (fun i => (i.choice, i.conflict))
  let rs := infos.map (fun i => (i.choice, i.query))
  let rest := restrictionsFor D A
  let route : String × Json := ("route", .str "enumerated")
  let named := assumedFields assumed
  match reasonOf cs rs with
  | some (.conflictStatus s c) => Json.mkObj ([("verdict", .str "UNKNOWN"), route,
      ("status", .str s!"UNKNOWN (conflict status: {word s})"), ("conflict_status", .str (word s)),
      ("choice", choiceJson c)] ++ named)
  | some (.noResult c) => Json.mkObj ([("verdict", .str "UNKNOWN"), route, ("choice", choiceJson c)] ++ named)
  | none => match foldEntailment cs rs with
    | .all => Json.mkObj ([("verdict", .str "ALL"), route, ("evidence", .str "certificates"),
        ("proofs", Json.arr (infos.map proofJson).toArray),
        ("conditional_on", toJson (conditionsOf "certificate" D A infos)),
        ("restrictions", toJson rest), ("reading_premises_used", toJson rest)] ++ named)
    | .none => Json.mkObj ([("verdict", .str "NONE"), route, ("countermodels", Json.arr (infos.map counterJson).toArray),
        ("restrictions", toJson rest)] ++ named)
    | .some => Json.mkObj ([("verdict", .str "SOME"), route,
        ("proof", ((infos.find? (·.query == .proved)).map proofJson).getD .null),
        ("countermodel", ((infos.find? (·.query == .refuted)).map counterJson).getD .null)] ++ named)
    | .unknown => Json.mkObj ([("verdict", .str "UNKNOWN"), route] ++ named)

def notesJson (notes : List PieceNote) (f : PieceNote → Option Json) : Json :=
  Json.mkObj (notes.filterMap (fun n => (f n).map (n.name, ·)))

def perChoiceJson (question : String) (i : RowInfo) : Json :=
  Json.mkObj ([("choice", choiceJson i.choice), ("conflict", .str (word i.conflict))] ++
    (if question == "query" then [("query", .str (word i.query))] else []) ++
    (if question == "premises" then [("premises", .str (word i.premise))] else []) ++
    [("evidence", notesJson i.notes (fun n => some (.bool n.accepted))),
     ("errors", notesJson i.notes (fun n => n.error.map Json.str)),
     ("shown", notesJson i.notes (·.shown)),
     ("gaps", notesJson i.notes (fun n => if n.gaps.isEmpty then none else some (gapsJson n.gaps))),
     ("status_text", match (i.note "witness").bind (·.statusText) with | some t => .str t | none => .null)])

/-- The sets the route's finding names (1.8; under the completion every open set), for E29; none for a document
    without an open set (a component's checked fixed units, RD-4b). -/
def findingSets (nd : Bool) (D : Doc) : List String :=
  match (if nd then some (completionFinding D) else notSuperposable D) with
  | some (sets, _) => (sets.splitOn ", ").filter (· != "")
  | none => []

/-- The question's result (none beyond 64 choices: W2's budget shape, and for a query the first checked
    countermodel among the evidence, `UNKNOWN (not ALL: countermodel under <choice>)`). -/
def resultOf (question : String) (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) : Json :=
  let named := assumedFields assumed
  match infos with
  | none => match question with
    | "conflict" => Json.mkObj (overBudgetFields D ++ [("status_text", .str "UNKNOWN: more than 64 compatible readings")])
    | "premises" => Json.mkObj (overBudgetFields D)
    | _ => match over.find? (·.query == .refuted) with
      | some i => Json.mkObj ([("verdict", .str "UNKNOWN"),
          ("status", .str s!"UNKNOWN (not ALL: countermodel under {choiceText D i.choice})")] ++ overBudgetRest D ++
          [("countermodel", counterJson i)] ++ named)
      | none => Json.mkObj ([("verdict", .str "UNKNOWN")] ++ overBudgetFields D ++ named)
  | some infos => match question with
    | "conflict" => conflictResult D A infos
    | "premises" => premisesResult D infos (deadOf D infos dead).1
    | _ => entailmentResult D A assumed infos

/-- The labels E3 cites (2.3 item 1), the one value the plan's condition lines are planned from: for a
    CONFLICT-FREE conflict answer and an ALL, under the completion the answer's `conditional_on` itself
    (`conditionsOf`: the `Fill_T` labels its certificates use, then the restrictions), on the lower route the
    restrictions (a lower answer's own labels, its coherence premises, are not worded); for a SOME under the
    completion the labels its proof uses (the proved choice is named in full, so no restriction applies), on the
    lower route none; for a NONE the restrictions. -/
def labelsOf (question : String) (nd : Bool) (D : Doc) (A : Choice) (infos : Option (List RowInfo)) : List String :=
  match infos with
  | none => []
  | some infos =>
    let cs := infos.map (fun i => (i.choice, i.conflict))
    let rs := infos.map (fun i => (i.choice, i.query))
    let rest := restrictionsFor D A
    if question == "conflict" then
      if foldConflict cs == .free then (if nd then conditionsOf "conflict" D A infos else rest)
      else []
    else if question == "query" && reasonOf cs rs == none && foldEntailment cs rs == .all then
      (if nd then conditionsOf "certificate" D A infos else rest)
    else if question == "query" && reasonOf cs rs == none && foldEntailment cs rs == .some then
      (if nd then ((infos.find? (·.query == .proved)).map (·.on "certificate")).getD [] else [])
    else if question == "query" && reasonOf cs rs == none && foldEntailment cs rs == .none then rest
    else []

def deadReadingsJson (d : Option (List (String × Nat))) : Json :=
  match d with
  | some l => Json.arr (l.map (fun (s, i) => Json.mkObj [("set", .str s), ("index", toJson i),
      ("finding", .str s!"DeadReading: {s}:{i}")])).toArray
  | none => .null

def untakenJson (l : List (String × Nat)) : Json := Json.arr (l.map (fun (s, i) => Json.arr #[.str s, toJson i])).toArray

/-- The answer's members before its English plan. -/
def answerFields (question : String) (nd : Bool) (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) : List (String × Json) :=
  let premises := question == "premises" && infos.isSome
  let d := deadOf D (infos.getD []) dead
  [("route", .str "enumerated"), ("question", .str question),
    ("finding_sets", toJson (findingSets nd D)),
    ("restrictions", toJson (match infos with | some _ => restrictionsFor D A | none => [])),
    ("result", resultOf question D A assumed infos over dead),
    ("per_choice", Json.arr ((infos.getD over).map (perChoiceJson question)).toArray),
    ("labels", toJson (labelsOf question nd D A infos)),
    ("dead_readings", if premises then deadReadingsJson d.1 else .null),
    ("untaken", untakenJson (if premises then untakenOf D (infos.getD []) else [])),
    ("dead", Json.arr (if premises then d.2 else []).toArray)]

/-- The English plan of the answer (`englishPlan` of its members): its condition lines planned from `labelsOf`,
    the value the answer's `labels` encodes (`verdictsPlan_eq`). -/
def verdictsPlan (question : String) (nd : Bool) (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) : List Line :=
  englishPlan D .enumerated question (Json.mkObj (answerFields question nd D A assumed infos over dead))

theorem verdictsPlan_eq (question : String) (nd : Bool) (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) :
    verdictsPlan question nd D A assumed infos over dead =
      (planItems D .enumerated question (labelsOf question nd D A infos)
        (Json.mkObj (answerFields question nd D A assumed infos over dead))).map (PlanItem.line D) := by
  have h : (Json.mkObj (answerFields question nd D A assumed infos over dead)).getObjValD "labels" =
      toJson (labelsOf question nd D A infos) := rfl
  simp only [verdictsPlan, englishPlan, h, jstrings_toJson]

/-- The answer: the question's result, its rows, the labels E3 cites, the dead readings, the untaken candidates and
    the dead evidence (the premises question's), then the English plan Lean makes of them (`verdictsPlan`). -/
def verdictsAnswer (id question : String) (nd : Bool) (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) : Json :=
  okWith id (answerFields question nd D A assumed infos over dead ++
    [("english", Json.arr ((verdictsPlan question nd D A assumed infos over dead).map Line.json).toArray)])

theorem map_row_choice (l : List Choice) (row : Choice → RowInfo) (h : ∀ c, (row c).choice = c) :
    (l.map row).map (·.choice) = l := by
  simp [List.map_map, Function.comp_def, h]

def verdictsQuestions : List String := ["conflict", "premises", "query"]

/-- `readings-verdicts` (4.4): on the enumerated route, the question folded over the compatible choices taking
    `assumed`, each piece of evidence checked on the choice's regenerated document (under the completion by Lean's
    checkers, `replayND`; else by the lower route, `lowerInfo`). `b` is the case's one admission. -/
def runVerdicts (lower : List String → Json → Json) (id : String) (b : Admitted2) (j : Json) :
    Except String Json := do
  let question ← stringField j "question"
  unless verdictsQuestions.contains question do throw s!"InvalidInput: unknown readings-verdicts question {question}"
  let ndProfile := b.a.re.lower.contains "norm-defaults@0"
  unless routeOf ndProfile b.D == .enumerated do
    throw "UnsupportedProfile: readings-verdicts answers the enumerated route; use the superposed kinds"
  let A ← decodeChoice (j.getObjValD "assumed")
  let named : Option Choice := match j.getObjVal? "assumed" with
    | .ok v => if v == .null then none else some A
    | .error _ => none
  let evidence := evidenceList j
  let dead := match j.getObjValD "dead" with | .arr xs => xs.toList | _ => []
  let premisesJ := match j.getObjValD "premises" with | .null => Json.arr #[] | p => p
  let conclusionJ := if question == "query" then j.getObjValD "conclusion" else .null
  let takes := fun (c : Choice) => A.all (c.contains ·)
  if underCompletion b.a.re b.D then
    let f ← admitNDFull b
    let D := f.r.N.D
    if (choices D).isEmpty then throw (unsatText D)
    if (choices D).length ≤ maxChoices then
      let x ← replayND f question A j
      return verdictsAnswer id question true D A named (some (ndInfos x)) [] dead
    -- Beyond 64: only a checked countermodel says anything (not ALL).
    let over := evidence.filterMap (fun e =>
      let c := jchoice (e.getObjValD "choice")
      if compatible D c && takes c then
        match hn : ndDocText f.r.b.a.re (choiceU f.r.N c) with
        | none =>
          let E := fullEnv f.r.N c
          match queryFormulas E question j with
          | .ok (Γ, φ) =>
            let (ev, notes) := ndEvidenceOf f.r c (wellFormedU_of_ndDocText hn) e premisesJ conclusionJ Γ φ
            some { choice := c, conflict := ndConflictRow ev, query := ndQueryRow ev Γ φ, premise := ndPremiseRow ev,
                   notes := notes }
          | .error _ => none
        | some _ => none
      else none)
    return verdictsAnswer id question true D A named none over dead
  if let some e := routeRefusal ndProfile b.D then throw e
  let D := b.D
  let row := fun (c : Choice) => lowerInfo lower id b c (entryFor evidence c) premisesJ conclusionJ
  if (choices D).length ≤ maxChoices then
    let chosen := chosenOf D A
    if chosen.isEmpty then throw (untakenText D A)
    let x : LowerVerdicts := ⟨b, A, chosen.map row, map_row_choice chosen row (fun _ => rfl)⟩
    return verdictsAnswer id question false D A named (some x.rows) [] dead
  let over := evidence.filterMap (fun e =>
    let c := jchoice (e.getObjValD "choice")
    if compatible D c && takes c then some (lowerInfo lower id b c e premisesJ conclusionJ) else none)
  return verdictsAnswer id question false D A named none over dead

/-! ### The conditions of an answer (6.4; DRI ruling of rd-3 round 3)

An answer's `conditional_on` labels are exactly the conditions its verdict rests on: they are `conditionsOf`, computed
from the same rows the fold theorems read (`readings_wire_verdicts_*`, `lower_verdicts_*`), every label a row's
accepted evidence uses and every restriction, nothing dropped and nothing added (`mem_conditionsOf`). The answer's
`labels` are the same value under the completion (on the lower route the restrictions), and the English plan plans
its condition lines from that value, a line citing each label (`verdictsPlan_cites`) and no line citing another
(`plan_conditions_only`). So an answer whose `conditional_on`, `labels` or plan lacks a condition its rows use cannot
come from `runVerdicts`. -/

theorem mem_dedupStrings (l : List String) (x : String) : x ∈ dedupStrings l ↔ x ∈ l := by
  unfold dedupStrings
  suffices h : ∀ acc : List String,
      x ∈ l.foldl (fun acc x => if acc.contains x then acc else acc ++ [x]) acc ↔ x ∈ acc ∨ x ∈ l by
    simpa using h []
  induction l with
  | nil => intro acc; simp
  | cons y ys ih =>
    intro acc
    simp only [List.foldl_cons, List.mem_cons]
    rw [ih]
    split
    · rename_i hy
      have hy : y ∈ acc := by simpa using hy
      constructor
      · rintro (h | h)
        · exact Or.inl h
        · exact Or.inr (Or.inr h)
      · rintro (h | rfl | h)
        · exact Or.inl h
        · exact Or.inl hy
        · exact Or.inr h
    · simp only [List.mem_append, List.mem_singleton]
      constructor
      · rintro ((h | rfl) | h)
        · exact Or.inl h
        · exact Or.inr (Or.inl rfl)
        · exact Or.inr (Or.inr h)
      · rintro (h | rfl | h)
        · exact Or.inl (Or.inl h)
        · exact Or.inl (Or.inr rfl)
        · exact Or.inr h

/-- Nothing dropped, nothing added: a label is a condition exactly when a row's accepted evidence uses it or it is a
    restriction. -/
theorem mem_conditionsOf (k : String) (D : Doc) (A : Choice) (infos : List RowInfo) (l : String) :
    l ∈ conditionsOf k D A infos ↔ (∃ i ∈ infos, l ∈ i.on k) ∨ l ∈ restrictionsFor D A := by
  simp only [conditionsOf, mem_dedupStrings, List.mem_append, List.mem_flatMap]

theorem verdictsAnswer_result (id question : String) (nd : Bool) (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) :
    (verdictsAnswer id question nd D A assumed infos over dead).getObjValD "result" =
      resultOf question D A assumed infos over dead := rfl

theorem verdictsAnswer_labels (id question : String) (nd : Bool) (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) :
    (verdictsAnswer id question nd D A assumed infos over dead).getObjValD "labels" =
      toJson (labelsOf question nd D A infos) := rfl

theorem verdictsAnswer_english (id question : String) (nd : Bool) (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) :
    (verdictsAnswer id question nd D A assumed infos over dead).getObjValD "english" =
      Json.arr ((verdictsPlan question nd D A assumed infos over dead).map Line.json).toArray := rfl

theorem planItem_line_label (D : Doc) (it : PlanItem) : (it.line D).label = it.label? := by
  cases it <;> rfl

/-- The answer's plan cites every label of `labelsOf` where it states conditions. -/
theorem verdictsPlan_cites (question : String) (nd : Bool) (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json)
    (h : (question = "conflict" ∧ strOf ((resultOf question D A assumed infos over dead).getObjValD "status") =
        "CONFLICT-FREE") ∨
      (question = "query" ∧ (strOf ((resultOf question D A assumed infos over dead).getObjValD "verdict") = "ALL" ∨
        strOf ((resultOf question D A assumed infos over dead).getObjValD "verdict") = "SOME" ∨
        strOf ((resultOf question D A assumed infos over dead).getObjValD "verdict") = "NONE"))) :
    ∀ l ∈ labelsOf question nd D A infos,
      ∃ line ∈ verdictsPlan question nd D A assumed infos over dead, line.label = some l := by
  intro l hl
  obtain ⟨it, hit, he⟩ := plan_cites_conditions D question (labelsOf question nd D A infos)
    (Json.mkObj (answerFields question nd D A assumed infos over dead)) h l hl
  rw [verdictsPlan_eq]
  exact ⟨it.line D, List.mem_map_of_mem hit, by rw [planItem_line_label, he]⟩

theorem reasonOf_none_of_fold {cs rs : List (Choice × ChoiceResult)} (h : foldEntailment cs rs ≠ .unknown) :
    reasonOf cs rs = none := by
  have hf : foldConflict cs = .free := by
    by_cases hc : foldConflict cs = .free
    · exact hc
    · exfalso
      apply h
      unfold foldEntailment
      simp [hc]
  unfold reasonOf
  split
  · simp [h]
  · rename_i hs
    exact absurd hf hs

theorem proofJson_conditional_on (i : RowInfo) :
    (proofJson i).getObjValD "conditional_on" = toJson (i.on "certificate") := rfl

/-- A CONFLICT-FREE answer (its rows `infos` fold to CONFLICT-FREE): its `conditional_on` is `conditionsOf` of those
    rows, its `labels` are the same list under the completion (the restrictions on the lower route), and its plan
    cites each of them. -/
theorem verdicts_conditions_conflict_free (id : String) (nd : Bool) (D : Doc) (A : Choice)
    (assumed : Option Choice) (infos : List RowInfo) (dead : List Json)
    (hv : foldConflict (infos.map (fun i => (i.choice, i.conflict))) = .free) :
    ((verdictsAnswer id "conflict" nd D A assumed (some infos) [] dead).getObjValD "result").getObjValD
        "conditional_on" = toJson (conditionsOf "conflict" D A infos) ∧
    (verdictsAnswer id "conflict" nd D A assumed (some infos) [] dead).getObjValD "labels" =
        toJson (if nd then conditionsOf "conflict" D A infos else restrictionsFor D A) ∧
    (∀ l, l ∈ conditionsOf "conflict" D A infos ↔ (∃ i ∈ infos, l ∈ i.on "conflict") ∨ l ∈ restrictionsFor D A) ∧
    ∀ l ∈ (if nd then conditionsOf "conflict" D A infos else restrictionsFor D A),
      ∃ line ∈ verdictsPlan "conflict" nd D A assumed (some infos) [] dead, line.label = some l := by
  have hr : resultOf "conflict" D A assumed (some infos) [] dead = conflictResult D A infos := rfl
  have hl : labelsOf "conflict" nd D A (some infos) =
      (if nd then conditionsOf "conflict" D A infos else restrictionsFor D A) := by
    cases nd <;> simp (config := {decide := true}) [labelsOf, hv]
  refine ⟨?_, ?_, mem_conditionsOf "conflict" D A infos, ?_⟩
  · rw [verdictsAnswer_result, hr]
    unfold conflictResult
    simp only [hv]
    rfl
  · rw [verdictsAnswer_labels, hl]
  · rw [← hl]
    apply verdictsPlan_cites
    left
    refine ⟨rfl, ?_⟩
    rw [hr]
    unfold conflictResult
    simp only [hv]
    rfl

/-- An ALL: its `conditional_on` is `conditionsOf` of the rows, each proof's (per choice) is that row's own labels,
    each of them among the answer's; its `labels` are the same list under the completion (the restrictions on the
    lower route), and its plan cites each of them. -/
theorem verdicts_conditions_all (id : String) (nd : Bool) (D : Doc) (A : Choice)
    (assumed : Option Choice) (infos : List RowInfo) (dead : List Json)
    (hv : foldEntailment (infos.map (fun i => (i.choice, i.conflict))) (infos.map (fun i => (i.choice, i.query))) =
      .all) :
    ((verdictsAnswer id "query" nd D A assumed (some infos) [] dead).getObjValD "result").getObjValD
        "conditional_on" = toJson (conditionsOf "certificate" D A infos) ∧
    ((verdictsAnswer id "query" nd D A assumed (some infos) [] dead).getObjValD "result").getObjValD
        "proofs" = Json.arr (infos.map proofJson).toArray ∧
    (∀ i ∈ infos, ∀ l ∈ i.on "certificate", l ∈ conditionsOf "certificate" D A infos) ∧
    (verdictsAnswer id "query" nd D A assumed (some infos) [] dead).getObjValD "labels" =
        toJson (if nd then conditionsOf "certificate" D A infos else restrictionsFor D A) ∧
    (∀ l, l ∈ conditionsOf "certificate" D A infos ↔
      (∃ i ∈ infos, l ∈ i.on "certificate") ∨ l ∈ restrictionsFor D A) ∧
    ∀ l ∈ (if nd then conditionsOf "certificate" D A infos else restrictionsFor D A),
      ∃ line ∈ verdictsPlan "query" nd D A assumed (some infos) [] dead, line.label = some l := by
  have hn := reasonOf_none_of_fold (by rw [hv]; decide)
  have hr : resultOf "query" D A assumed (some infos) [] dead = entailmentResult D A assumed infos := rfl
  have he : entailmentResult D A assumed infos = Json.mkObj ([("verdict", .str "ALL"), ("route", .str "enumerated"),
      ("evidence", .str "certificates"), ("proofs", Json.arr (infos.map proofJson).toArray),
      ("conditional_on", toJson (conditionsOf "certificate" D A infos)),
      ("restrictions", toJson (restrictionsFor D A)), ("reading_premises_used", toJson (restrictionsFor D A))] ++
      assumedFields assumed) := by
    unfold entailmentResult
    simp only [hn, hv]
  have hl : labelsOf "query" nd D A (some infos) =
      (if nd then conditionsOf "certificate" D A infos else restrictionsFor D A) := by
    cases nd <;> simp (config := {decide := true}) [labelsOf, hv, hn]
  refine ⟨?_, ?_, fun i hi l hli => (mem_conditionsOf _ _ _ _ _).mpr (Or.inl ⟨i, hi, hli⟩), ?_,
    mem_conditionsOf "certificate" D A infos, ?_⟩
  · rw [verdictsAnswer_result, hr, he]
    cases assumed <;> rfl
  · rw [verdictsAnswer_result, hr, he]
    cases assumed <;> rfl
  · rw [verdictsAnswer_labels, hl]
  · rw [← hl]
    apply verdictsPlan_cites
    right
    refine ⟨rfl, Or.inl ?_⟩
    rw [hr, he]
    cases assumed <;> rfl

/-- A SOME: its proof is the first proved row's (per choice, `proofJson`: that row's own labels); its `labels` are
    those labels under the completion (none on the lower route), and its plan cites each of them. -/
theorem verdicts_conditions_some (id : String) (nd : Bool) (D : Doc) (A : Choice)
    (assumed : Option Choice) (infos : List RowInfo) (dead : List Json) (i : RowInfo)
    (hv : foldEntailment (infos.map (fun i => (i.choice, i.conflict))) (infos.map (fun i => (i.choice, i.query))) =
      .some)
    (hi : infos.find? (·.query == .proved) = some i) :
    ((verdictsAnswer id "query" nd D A assumed (some infos) [] dead).getObjValD "result").getObjValD "proof" =
        proofJson i ∧
    (verdictsAnswer id "query" nd D A assumed (some infos) [] dead).getObjValD "labels" =
        toJson (if nd then i.on "certificate" else []) ∧
    ∀ l ∈ (if nd then i.on "certificate" else []),
      ∃ line ∈ verdictsPlan "query" nd D A assumed (some infos) [] dead, line.label = some l := by
  have hn := reasonOf_none_of_fold (by rw [hv]; decide)
  have hr : resultOf "query" D A assumed (some infos) [] dead = entailmentResult D A assumed infos := rfl
  have he : entailmentResult D A assumed infos = Json.mkObj ([("verdict", .str "SOME"), ("route", .str "enumerated"),
      ("proof", proofJson i),
      ("countermodel", ((infos.find? (·.query == .refuted)).map counterJson).getD .null)] ++
      assumedFields assumed) := by
    unfold entailmentResult
    simp only [hn, hv, hi, Option.map_some, Option.getD_some]
  have hl : labelsOf "query" nd D A (some infos) = (if nd then i.on "certificate" else []) := by
    cases nd <;> simp (config := {decide := true}) [labelsOf, hv, hn, hi]
  refine ⟨?_, ?_, ?_⟩
  · rw [verdictsAnswer_result, hr, he]
    cases assumed <;> rfl
  · rw [verdictsAnswer_labels, hl]
  · rw [← hl]
    apply verdictsPlan_cites
    right
    refine ⟨rfl, Or.inr (Or.inl ?_)⟩
    rw [hr, he]
    cases assumed <;> rfl

/-- A NONE: its conditions are the restrictions, which its `labels` are and its plan cites. -/
theorem verdicts_conditions_none (id : String) (nd : Bool) (D : Doc) (A : Choice)
    (assumed : Option Choice) (infos : List RowInfo) (dead : List Json)
    (hv : foldEntailment (infos.map (fun i => (i.choice, i.conflict))) (infos.map (fun i => (i.choice, i.query))) =
      .none) :
    ((verdictsAnswer id "query" nd D A assumed (some infos) [] dead).getObjValD "result").getObjValD
        "restrictions" = toJson (restrictionsFor D A) ∧
    (verdictsAnswer id "query" nd D A assumed (some infos) [] dead).getObjValD "labels" =
        toJson (restrictionsFor D A) ∧
    ∀ l ∈ restrictionsFor D A,
      ∃ line ∈ verdictsPlan "query" nd D A assumed (some infos) [] dead, line.label = some l := by
  have hn := reasonOf_none_of_fold (by rw [hv]; decide)
  have hr : resultOf "query" D A assumed (some infos) [] dead = entailmentResult D A assumed infos := rfl
  have he : entailmentResult D A assumed infos = Json.mkObj ([("verdict", .str "NONE"), ("route", .str "enumerated"),
      ("countermodels", Json.arr (infos.map counterJson).toArray),
      ("restrictions", toJson (restrictionsFor D A))] ++ assumedFields assumed) := by
    unfold entailmentResult
    simp only [hn, hv]
  have hl : labelsOf "query" nd D A (some infos) = restrictionsFor D A := by
    cases nd <;> simp (config := {decide := true}) [labelsOf, hv, hn]
  refine ⟨?_, ?_, ?_⟩
  · rw [verdictsAnswer_result, hr, he]
    cases assumed <;> rfl
  · rw [verdictsAnswer_labels, hl]
  · rw [← hl]
    apply verdictsPlan_cites
    right
    refine ⟨rfl, Or.inr (Or.inr ?_)⟩
    rw [hr, he]
    cases assumed <;> rfl

end VE.Readings.Run
