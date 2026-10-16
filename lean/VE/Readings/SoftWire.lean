import VE.Readings.UnspecifiedWire
import VE.Readings.SoftSeparate

/-! The wire under the soft completion (docs/spec/rd-9-soft-chain.md 1.1, 3, 4.1 to 4.3 and 6.8; plan SC-4).

A document is under the soft completion when its profiles hold `readings@1` and `norm-defaults@0` on the soft chain
and some set is content-bearing (`underSoftCompletion`). Its admission (`admitSD`, 4.1) is S1's and S2a's, then the
reserved names, norm-defaults' author checks (each document's decision predicates counted) and `WellFormedU` on the
free document and each reading's document, the soft shape, and each compatible choice, at most 64 (`sdChoiceText`).
No filled readings document is admitted: `fillDoc` is not well formed on the soft chain.

Separation (4.2, `replaySeparateS`) runs S1's pair check on filled sides (`separatesS`); the situation is decoded
over the filled frame's author vocabulary, `unsaid__p` included: the document's own items admitted once more over
`filledEnvironment` (`UnsaidAdmitted`), whose author vocabulary is `filledAuthorEnv N`. Each choice (4.3,
`replayChoiceS`) is checked on its layered source `choiceLayeredG`, which carries `X` and its well-formedness. -/
namespace VE.Readings.Wire
open Lean
open VE.Readings
open VE.Bridge (stringField)
open VE.Norms (envAt size)
open VE.Rights (RightsDoc correlate)
universe u

def underSoftCompletion (re : ReadingsEnvironment) (D : Doc) : Bool :=
  re.lower.contains normDefaultsProfile && re.chain == .soft && D.sets.any contentBearing

/-- The source choice is checked before its completion and generated decisions. -/
def sdChoiceText (re : ReadingsEnvironment) (N : NDoc) (c : Choice) : Option String :=
  (choiceChainText N.D c).or
    ((ndDocTextG re (decisionCount (choiceDoc N.D c).1) (choiceU N c)).map
      (· ++ " under " ++ choiceText N.D c))

structure AdmittedSD where
  b : Admitted2
  N : NDoc
  hN : N.D = b.D
  wf : WellFormedSD N = true
  side : ∀ s i, b.a.side s i = one N.D s i

/-- Continue S2 admission using the common fill checks and the soft shape. -/
def admitSDOf (b : Admitted2) : Except String AdmittedSD :=
  let re := b.a.re
  let N : NDoc := ⟨b.D, unspecOf re b.D⟩
  if hsd : b.D.chain = b.a.D.chain ∧ b.D.items = b.a.D.items then
    have hside : ∀ s i, b.a.side s i = one N.D s i := fun s i => by
      rw [b.a.side_eq]
      exact one_congr hsd.1.symm (by rw [b.frame]; rfl) hsd.2.symm s i
    match hT : ndTextWith re N b.a.side with
    | some e => .error e
    | none =>
      have hT' : ndText re N = none := (ndTextWith_eq hside) ▸ hT
      if hs : softShaped N.D = true then
        match hc : if (choices N.D).length ≤ maxChoices then
            (choices N.D).findSome? (sdChoiceText re N) else none with
        | some e => .error e
        | none =>
          .ok ⟨b, N, rfl, by
            simpa [wellFormedSD_eq, hs, fillRest_of_ndText hT'] using b.wf, hside⟩
      else .error "InvalidInput: norm-defaults document is not well formed"
  else .error "InvalidInput: readings document is not well-formed"

def admitSD (environment document : Json) : Except String AdmittedSD := do
  let b ← admitS2 environment document
  unless underSoftCompletion b.a.re b.D do
    throw "UnsupportedProfile: the document is not under the unspecified completion"
  admitSDOf b

/-! ## The document over the filled author vocabulary (4.2) -/

/-- The document's own items admitted by S1 over the filled frame's environment (`filledEnvironment`, every
    `unsaid__p` added): its situations are decoded over the filled author vocabulary. -/
structure UnsaidAdmitted (r : AdmittedSD) where
  a : Admitted
  frame : a.D.frame = (fillDoc r.N).frame
  items : a.D.items = r.N.D.items

def admitUnsaid (r : AdmittedSD) : Except String (UnsaidAdmitted r) :=
  let re := r.b.a.re
  if hfree : r.N.unspec.all (fun p => VE.Bridge.lookup re.se.ne.rv.vocabulary.predicates
      (VE.NormDefaults.unsaidName p) == none) = true then
    let doc' : Decoded2 := ⟨r.N.D.items, r.b.a.doc.itemsJ, r.b.a.doc.units⟩
    match ha : admitDecoded (filledEnvironment re r.N) doc' with
    | .error e => .error e
    | .ok a' =>
      have hd := admitDecoded_ok ha
      have hframe : r.N.D.frame = frameOf re r.b.a.doc.units := by rw [r.hN]; exact r.b.frame
      .ok ⟨a', by
          show (docOf a'.re a'.doc).frame = _
          rw [hd.1, hd.2]
          exact frameOf_filled re r.N _ hframe hfree,
        by
          show (docOf a'.re a'.doc).items = _
          rw [hd.1, hd.2]
          rfl⟩
  else .error "InvalidInput: norm-defaults document is not well formed"

theorem candidate_unsaid {r : AdmittedSD} (fa : UnsaidAdmitted r) (s : String) (i : Nat) :
    candidate fa.a.D s i = candidate r.N.D s i := by
  simp only [candidate, Doc.sets, fa.items]

theorem authorEnv_unsaid {r : AdmittedSD} (fa : UnsaidAdmitted r) : authorEnv fa.a.D = filledAuthorEnv r.N := by
  rw [filledAuthorEnv_eq]
  simp only [authorEnv, fa.frame]

/-! ## Separation (4.2) -/

structure SeparateReplayS where
  r : AdmittedSD
  set : String
  witness : Nat
  other : Nat
  hw : (candidate r.N.D set witness).bind (·.content) ≠ none
  ho : (candidate r.N.D set other).bind (·.content) ≠ none
  σ : Situation VE.Bridge.Entity
  valid : σ.base.Valid (filledAuthorEnv r.N)

/-- The pair `(witness, other)` of a set and the situation recorded for it, decoded over the filled author
    vocabulary. -/
def replayPairS (r : AdmittedSD) (fa : UnsaidAdmitted r) (s sid other : String) :
    Except String (SeparateReplayS × SeparateReplay × SituationJ) :=
  match h : replayPair fa.a s sid other with
  | .error e => .error e
  | .ok (x, sj) =>
    .ok (⟨r, x.set, x.witness, x.other,
      by rw [← candidate_unsaid fa, ← replayPair_D h]; exact x.hw,
      by rw [← candidate_unsaid fa, ← replayPair_D h]; exact x.ho,
      x.σ, by rw [← authorEnv_unsaid fa, ← replayPair_D h]; exact x.valid⟩, x, sj)

/-- 4.2. -/
def replaySeparateS (j : Json) : Except String SeparateReplayS := do
  let r ← admitSD (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let fa ← admitUnsaid r
  pure (← replayPairS r fa (← stringField j "set") (← stringField j "situation") (← stringField j "other")).1

theorem readings_wire_sd_separate_sound (j : Json) (x : SeparateReplayS) (h : replaySeparateS j = .ok x)
    (hs : separatesS x.r.N x.set x.witness x.other x.σ = true) :
    AchievesS x.r.N x.set x.witness x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value ∧
      ¬ AchievesS x.r.N x.set x.other x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value := by
  -- The replay carries the facts: the admitted document, the pair's contents, the base's validity.
  have _ := h
  exact separatesS_sound x.r.N x.r.wf x.set x.witness x.other x.hw x.ho x.σ x.valid hs

/-! ## Each choice (4.3) -/

structure ChoiceReplayS where
  r : AdmittedSD
  c : Choice
  hc : Compatible r.N.D c
  wfc : VE.NormDefaults.WellFormedU (choiceU r.N c) = true
  L : VE.NormDefaults.Wire.LayeredU
  hU : L.U = choiceU r.N c
  hX : L.X = choiceX r.N c
  hXw : ∀ a ∈ L.X, a.WellFormed (envAt (VE.NormDefaults.fill L.U) 0) []

/-- 4.3 on an admitted document: `sdChoiceText` on its own choice (any replayed choice, beyond 64 too), refusing
    with its text, then `choiceLayeredG`. -/
def replayChoiceAtS (r : AdmittedSD) (c : Choice) : Except String ChoiceReplayS :=
  if hc : compatible r.N.D c = true then
    match ht : sdChoiceText r.b.a.re r.N c with
    | some e => .error e
    | none =>
      have hw : VE.NormDefaults.WellFormedU (choiceU r.N c) = true := by
        have h2 := (option_or_none ht).2
        exact wellFormedU_of_ndDocTextG (Option.map_eq_none_iff.mp h2)
      match choiceLayeredG r.b r.N c hw r.hN with
      | .error e => .error e
      | .ok L => .ok ⟨r, c, hc, hw, L.1, L.2.1, L.2.2.1, L.2.2.2⟩
  else .error "InvalidInput: the choice is not a compatible complete choice"

/-- 4.3: `sdChoiceText` on its own choice, refusing with its text, then `choiceLayeredG`. -/
def replayChoiceS (j : Json) : Except String ChoiceReplayS := do
  let r ← admitSD (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let c ← decodeChoice (j.getObjValD "choice")
  replayChoiceAtS r c

theorem readings_wire_sd_choice_conflict (j : Json) (x : ChoiceReplayS) (h : replayChoiceS j = .ok x)
    (packages : Json) (hv : VE.NormDefaults.Wire.conflictFreeX x.L packages = true) :
    Compatible x.r.N.D x.c ∧ VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU x.r.N x.c) (choiceX x.r.N x.c) := by
  have _ := h
  have hcf := VE.NormDefaults.Wire.layered_conflict_sound.{u} x.L packages hv
  rw [x.hU, x.hX] at hcf
  exact ⟨x.hc, hcf⟩

theorem readings_wire_sd_choice_entails (j : Json) (x : ChoiceReplayS) (h : replayChoiceS j = .ok x)
    (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (VE.NormDefaults.fill (choiceU x.r.N x.c))
            (size (VE.NormDefaults.fill (choiceU x.r.N x.c))))
            (VE.NormDefaults.Wire.premisesX (choiceU x.r.N x.c) (choiceX x.r.N x.c)
              ((choiceDoc x.r.N.D x.c).2 ++ Γ)) φ cert = true)
    (packages : Json) (hcf : VE.NormDefaults.Wire.conflictFreeX x.L packages = true) :
    VE.NormDefaults.Wire.ConflictFreeX.{u} (choiceU x.r.N x.c) (choiceX x.r.N x.c) ∧
      VE.NormDefaults.EntailsX.{u} (choiceU x.r.N x.c) (choiceX x.r.N x.c) ((choiceDoc x.r.N.D x.c).2 ++ Γ) φ := by
  have hXw := x.hXw
  rw [x.hU, x.hX] at hXw
  exact ⟨(readings_wire_sd_choice_conflict j x h packages hcf).2,
    VE.NormDefaults.acceptanceX _ x.wfc _ hXw _ φ cert hv⟩

end VE.Readings.Wire
