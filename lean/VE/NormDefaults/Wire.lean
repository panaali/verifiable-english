import VE.NormDefaults.Routes
import VE.Norms.Replay

/-! The `norm-defaults@0` decoder and its replay (docs/spec/norm-defaults.md 2.1,
6 and 8).

Without the profile the decoder is the unchanged norms decoder
(`decode_conservative`); a `default` of `unspecified` is then
`UnsupportedProfile: unspecified completion requires norm-defaults@0`. With the
profile, each `unspecified` default is read as the placeholder `deny`, the profile
is set aside for the frozen envelope gate, the author document is decoded and
validated by the unchanged norms decoder, and then the reserved names and the
author-side limits of section 8 are checked, in the table's order, each under its
own diagnostic. Identity is computed on the original environment, profile and
`unspecified` values included, so opting in changes `environment_id` (6.2).

Replay regenerates everything from the decoded document: the targets of `fill U`,
`Background_base(E‴) ++ Fill_T` as the base background, and the entailment
premises. `normDefaults_wire_conflict_sound` and `normDefaults_wire_acceptance`
follow the norms route's chain on `fill U`. -/
namespace VE.NormDefaults.Wire
open Lean
open VE.Norms
open VE.Bridge (fields strings)
universe u

def profile : String := "norm-defaults@0"

/-- The original profile list of an environment. -/
def profilesOf (environment : Json) : List String :=
  ((environment.getObjVal? "profiles" >>= strings).toOption).getD []

def hasProfile (environment : Json) : Bool := (profilesOf environment).contains profile

/-- The predicates whose raw `default` is `unspecified`. -/
def unspecifiedNames (environment : Json) : List String :=
  match environment.getObjVal? "vocabulary" >>= (·.getObjVal? "predicates") >>= fields with
  | .ok preds => preds.filterMap fun (p, e) => match e.getObjVal? "regulated" with
    | .ok r => if r.getObjValD "default" == .str "unspecified" then some p else none
    | .error _ => none
  | .error _ => []

/-- The declared predicate names of an environment. -/
def declaredNames (environment : Json) : List String :=
  match environment.getObjVal? "vocabulary" >>= (·.getObjVal? "predicates") >>= fields with
  | .ok preds => preds.map (·.1)
  | .error _ => []

/-- `unspecified` read as the placeholder `deny`, and the profile set aside. -/
def placeholderJson (environment : Json) : Except String Json := do
  let vocab ← environment.getObjVal? "vocabulary"
  let preds ← fields (← vocab.getObjVal? "predicates")
  let preds' := preds.map fun (p, e) => match e.getObjVal? "regulated" with
    | .ok r => if r.getObjValD "default" == .str "unspecified" then
        (p, e.setObjVal! "regulated" (r.setObjVal! "default" (.str "deny"))) else (p, e)
    | .error _ => (p, e)
  let profiles ← strings (← environment.getObjVal? "profiles")
  pure ((environment.setObjVal! "vocabulary" (vocab.setObjVal! "predicates" (Json.mkObj preds'))).setObjVal!
    "profiles" (toJson (profiles.filter (· != profile))))

/-- A decoded source under the profile (or without it): the author document, its
unspecified predicates and the facts the replay uses. -/
structure SourceU where
  src : VE.Norms.Wire.Source
  U : UDoc
  doc : U.D = src.D
  wfFill : WellFormed (fill U) = true
  profiled : Bool
  wfU : profiled = true → WellFormedU U = true
  plain : profiled = false → U.unspec = []

/-- Reserved names and the author-side limits of section 8, in the table's order;
`generated` counts the predicates the route adds to the author vocabulary (soft's
decision predicates, rights' generated ones; none on the norms route). -/
def checkAuthorN (environment : Json) (generated : Nat) (U : UDoc) : Except String Unit := do
  for n in declaredNames environment do
    if n.startsWith "unsaid__" then throw s!"InvalidInput: reserved name {n}"
  for N in U.D.T.nodes do
    if N.name.startsWith "unsaid--" then throw s!"InvalidInput: reserved name {N.name}"
  if (declaredNames environment).length + generated + U.unspec.length > 256 then
    throw "ResourceLimit: vocabulary size"
  if U.D.T.nodes.length + U.unspec.length > 256 then throw "ResourceLimit: rules"
  if U.unspec.any (fun p => p.utf8ByteSize > 56) then throw "ResourceLimit: unspecified name length"
  if (U.D.T.nodes.map ruleNodes).sum + fillGuardNodes U > 10000 then
    throw "ResourceLimit: AST exceeds 10,000 nodes"
  if U.D.T.nodes.any (fun N => decide (N.pred ∈ U.unspec) && decide (height U.D.T (fuel U.D.T) N > 15)) then
    throw "ResourceLimit: precedence depth"

/-- The norms route's author check: no generated predicates. -/
def checkAuthor (environment : Json) (U : UDoc) : Except String Unit := checkAuthorN environment 0 U

def decodeSourceU (environment norms : Json) : Except String SourceU :=
  if hasProfile environment then do
    let env' ← placeholderJson environment
    let src ← VE.Norms.Wire.decodeSource env' norms
    let names := unspecifiedNames environment
    let U : UDoc := ⟨src.D, (src.D.T.regulated.map Regulated.name).filter (names.contains ·)⟩
    checkAuthor environment U
    if h : WellFormedU U = true then
      pure ⟨src, U, rfl, fill_wellFormed U h, true, fun _ => h, fun hc => by cases hc⟩
    else throw "InvalidInput: norm-defaults document is not well formed"
  else do
    unless (unspecifiedNames environment).isEmpty do
      throw "UnsupportedProfile: unspecified completion requires norm-defaults@0"
    let src ← VE.Norms.Wire.decodeSource environment norms
    pure ⟨src, ⟨src.D, []⟩, rfl, (by rw [fill_eq_self _ rfl]; exact src.wf), false, (fun h => by cases h),
      fun _ => rfl⟩

/-- The environment bytes identity is computed on: the original environment,
canonicalised as the norms route does. -/
def canonicalEnvironmentJsonU (environment : Json) : Except String Json :=
  VE.Norms.Wire.canonicalEnvironmentJson environment

/-- `decode_conservative`: without an `unspecified` value and without the profile,
the decoder returns exactly the norms route decoder's result with `unspec = []`,
and the canonical environment bytes are the same. -/
theorem decode_conservative (environment norms : Json) (hp : hasProfile environment = false)
    (hu : unspecifiedNames environment = []) :
    (decodeSourceU environment norms).map (fun s => (s.src, s.U)) =
      (VE.Norms.Wire.decodeSource environment norms).map (fun s => (s, (⟨s.D, []⟩ : UDoc))) ∧
    canonicalEnvironmentJsonU environment = VE.Norms.Wire.canonicalEnvironmentJson environment := by
  refine ⟨?_, rfl⟩
  unfold decodeSourceU
  simp only [hp, Bool.false_eq_true, if_false, hu, List.isEmpty_nil]
  cases VE.Norms.Wire.decodeSource environment norms <;> rfl

theorem decodeSourceU_plain {environment norms : Json} {s : SourceU}
    (h : decodeSourceU environment norms = .ok s) (hp : hasProfile environment = false) :
    VE.Norms.Wire.decodeSource environment norms = .ok s.src ∧ s.U = ⟨s.src.D, []⟩ := by
  unfold decodeSourceU at h
  simp only [hp, Bool.false_eq_true, if_false] at h
  split at h
  · obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨src, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
    cases h
    exact ⟨hd, rfl⟩
  · obtain ⟨_, he, _⟩ := VE.Order.ProfileGate.bind_ok h
    cases he

/-! ## Regenerated outputs -/

def enc (a : VE.Formula) : Json := VE.Route.Wire.encodeFormula a

/-- The regenerated elaboration of `fill U`: W1's outputs on `T‴`, with `Fill_T`
(generator `fill`) after the Background, the unsaid predicates, and the
`default reached` targets of every regulated predicate. -/
def regeneratedU (U : UDoc) : List (String × Json) :=
  VE.Norms.Wire.regenerated (fill U) ++
  [("fill", Json.arr ((fillPremises U).map (fun a =>
      Json.mkObj [("generator", .str "fill"), ("ast", enc a)])).toArray),
   ("unspecified", toJson U.unspec),
   ("unsaid", Json.arr (U.unspec.map (fun p =>
      Json.mkObj [("name", .str (unsaidName p)), ("sorts", toJson (sortsOf U.D p))])).toArray),
   ("reached", Json.arr (U.D.T.regulated.map (fun r =>
      Json.mkObj [("predicate", .str r.name), ("sorts", toJson r.sorts), ("ast", enc (reachedF U r.name))])).toArray),
   ("fragment_fill", .bool (InFragment (fill U)))]

/-! ## Conflict replay (CONFLICT-FREE) -/

/-- The base background of `fill U`: `Background_base(E‴) ++ Fill_T`. -/
def baseBackgroundU (U : UDoc) : List VE.Formula := backgroundBase (fill U) ++ fillPremises U

def conflictFreeCheckU (U : UDoc) (certs : List (Option VE.Tableau.Certificate)) : Bool :=
  (targets (fill U)).length == certs.length &&
    ((targets (fill U)).zip certs).all (fun (t, c) => match c with
      | some c => VE.Tableau.checkCertificate (envAt (fill U) 0) (baseBackgroundU U) (targetConclusion t) c
      | none => false)

theorem conflictFreeCheckU_sound (U : UDoc) (h : WellFormed (fill U) = true)
    (certs : List (Option VE.Tableau.Certificate)) (hc : conflictFreeCheckU U certs = true) :
    ConflictFreeU.{u} U := by
  have hv := valid_of_wellFormed _ h
  intro B hB
  have hcert : ∀ t ∈ targets (fill U), ∀ vs : List B.Carrier, VE.TupleTyped B t.2.1 vs → ¬ t.2.2.denote B (tupleVal vs) := by
    intro t ht vs hvs
    simp only [conflictFreeCheckU, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hc
    obtain ⟨hl, hall⟩ := hc
    obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp ht
    have hlt : i < (targets (fill U)).length := (List.getElem?_eq_some_iff.mp hi).1
    have hlt' : i < certs.length := hl ▸ hlt
    have hmem : (t, certs[i]) ∈ (targets (fill U)).zip certs := by
      apply List.mem_iff_getElem?.mpr
      refine ⟨i, ?_⟩
      rw [List.getElem?_zip_eq_some]
      exact ⟨hi, List.getElem?_eq_getElem hlt'⟩
    have := hall _ hmem
    cases hci : certs[i] with
    | none => rw [hci] at this; cases this
    | some c =>
      rw [hci] at this
      have he := VE.Tableau.checkCertificate_sound.{u} _ _ _ c this B hB.1.1 (fun a ha => by
        rcases List.mem_append.mp ha with ha | ha
        · exact hB.1.2 a ha
        · exact hB.2 a ha)
      exact (bindAll_denote_nil B _ _).mp he vs hvs
  refine ⟨fun r hr vs hvs => ?_, fun pr hpr vs hvs => ?_⟩
  · exact hcert _ (List.mem_append_left _ (List.mem_filterMap.mpr ⟨.reg r, hv.regulated r hr, rfl⟩)) vs hvs
  · exact hcert _ (List.mem_append_right _ (List.mem_map.mpr ⟨pr, hpr, rfl⟩)) vs hvs

/-- The regenerated base environment `E‴_base`: regulated predicates and the
`norms@0` and `norm-defaults@0` profiles removed, one base predicate `unsaid__p`
per unspecified `p` added. -/
def baseEnvironmentJsonU (environment : Json) (U : UDoc) : Except String Json := do
  let base ← VE.Norms.Replay.baseEnvironmentJson (← placeholderJson environment)
  let vocab ← base.getObjVal? "vocabulary"
  let preds ← fields (← vocab.getObjVal? "predicates")
  let extra := U.unspec.map fun p => (unsaidName p, Json.mkObj [("arguments", toJson (sortsOf U.D p)),
    ("description", .str s!"the text does not say whether {p}")])
  pure (base.setObjVal! "vocabulary" (vocab.setObjVal! "predicates" (Json.mkObj (preds ++ extra))))

/-- One target's package bound to `E‴_base`, `Background_base(E‴) ++ Fill_T` and the
target's conclusion; the outer binding names the source environment (profile
included) and the norm document. -/
def decodePackageU (U : UDoc) (environment norms packages : Json) (t : String × List String × VE.Formula) :
    Option VE.Tableau.Certificate := Id.run do
  let profiles := profilesOf environment
  let some baseEnv := (baseEnvironmentJsonU environment U).toOption | none
  let some baseProfiles := (strings (baseEnv.getObjValD "profiles")).toOption | none
  let some canonical := (canonicalEnvironmentJsonU environment).toOption | none
  let some envId := (VE.Route.Wire.environmentId profiles canonical).toOption | none
  let some docHash := (VE.Norms.Replay.documentHash profiles environment norms).toOption | none
  let package := packages.getObjValD t.1
  unless package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash &&
      package.getObjValD "target" == .str t.1 do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  match VE.Route.Wire.bindingOk baseProfiles baseEnv ((baseBackgroundU U).map enc) (enc (targetConclusion t))
      c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
  | .ok () => some c
  | .error _ => none

structure ConflictReplayU where
  s : SourceU
  certs : List (Option VE.Tableau.Certificate)

def ConflictReplayU.conflictFree (r : ConflictReplayU) : Bool := conflictFreeCheckU r.s.U r.certs

def replayConflictU (j : Json) : Except String ConflictReplayU := do
  let environment ← j.getObjVal? "environment"
  let norms := j.getObjValD "norms"
  let s ← decodeSourceU environment norms
  let packages := j.getObjValD "packages"
  pure ⟨s, (targets (fill s.U)).map (decodePackageU s.U environment norms packages)⟩

/-- `normDefaults_wire_conflict_sound` (CONFLICT-FREE half): a successful raw replay
whose every target of `fill U` has an accepted certificate over
`Background_base(E‴) ++ Fill_T` proves, for the document decoded from that very
input, that it is CONFLICT-FREE under every admissible filling. -/
theorem normDefaults_wire_conflict_sound (j : Json) (res : ConflictReplayU) (h : replayConflictU j = .ok res)
    (hv : res.conflictFree = true) :
    decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") = .ok res.s ∧ ConflictFreeU.{u} res.s.U := by
  unfold replayConflictU at h
  obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨s, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  exact ⟨by rw [he]; exact hd, conflictFreeCheckU_sound s.U s.wfFill _ hv⟩

/-- With W1's document iff on `fill U`: every admissible filling then has exactly
one filled expansion. -/
theorem normDefaults_wire_expands (j : Json) (res : ConflictReplayU) (h : replayConflictU j = .ok res)
    (hv : res.conflictFree = true) :
    ∀ B : VE.Structure.{u}, BaseAdmissibleU res.s.U B → VE.Route.Unique (DocumentExpansion (fill res.s.U) B) :=
  fun B hB => (conflictFree_expands_document (fill res.s.U) res.s.wfFill B hB.1).mpr
    ((normDefaults_wire_conflict_sound j res h hv).2 B hB)

/-! ## Entailment certificates -/

/-- Every `Fill_T` formula is a closed base formula of `E‴`. -/
theorem fillPremises_wellFormed {U : UDoc} (h : WellFormedU U = true) :
    ∀ a ∈ fillPremises U, a.WellFormed (envAt (fill U) 0) [] := by
  have hu := uvalid h
  have hv' := valid_of_wellFormed _ (fill_wellFormed U h)
  intro a ha
  obtain ⟨pr, hpr, rfl⟩ := List.mem_map.mp ha
  have hpr : pr ∈ pairs U.D.T := (List.mem_filter.mp hpr).1
  obtain ⟨r, hr, _, _, _, hrs⟩ := pair_req hpr
  have hgap : ∀ q ∈ [pr.req, pr.perm], (gapF U q).WellFormed (envAt (fill U) 0) pr.sorts.reverse := by
    intro q hq
    unfold gapF
    split
    · rename_i hqu
      obtain ⟨rq, hrq, hrqn, _⟩ := hu.declared q hqu
      have hsorts : rq.sorts = pr.sorts := by
        simp only [List.mem_cons, List.not_mem_nil, or_false] at hq
        rcases hq with rfl | rfl
        · obtain ⟨r', hr', hr'n, _, _, hr's⟩ := pair_req hpr
          rw [hu.regulated_eq hrq hr' (hrqn.trans hr'n.symm)]; exact hr's
        · obtain ⟨m', hm', hm'n, _, hm's⟩ := pair_perm hu hpr
          rw [hu.regulated_eq hrq hm' (hrqn.trans hm'n.symm)]; exact hm's
      have hk := index_before hu.valid hrq
      have hT := rulesTyped_of_valid hu.valid hk
      have hmono : ∀ sign, (decides U.D.T q sign).WellFormed (envAt (fill U) (before U.D q)) pr.sorts.reverse := by
        intro sign
        rw [← hrqn, ← hsorts, ← VE.check_iff_wellFormed]
        exact check_envAt_fill hu ((VE.check_iff_wellFormed _ _ _).mpr (decides_wellFormed hT sign))
      rw [before_fill hu]
      exact ⟨subst_wellFormed hv' _ _ _ (hmono true), subst_wellFormed hv' _ _ _ (hmono false)⟩
    · trivial
  apply bindAll_wellFormed (fun s hs => ?_) [] _
  · simp only [List.append_nil]
    exact ⟨pairConflict_wellFormed hv' (show pr ∈ pairs (fill U).T from hpr),
      hgap _ List.mem_cons_self, hgap _ (List.mem_cons_of_mem _ List.mem_cons_self)⟩
  · have := (hu.ok.2.2.1 r hr).2.2.1 s (by rw [hrs]; exact hs)
    exact this

structure EntailmentReplayU where
  s : SourceU
  premises : List VE.Formula
  conclusion : VE.Formula
  cert : VE.Tableau.Certificate

/-- The regenerated premises of `fill U`: Background, `Fill_T`, the layer premises of
`T‴`, then the case's premises. -/
def premisesU (U : UDoc) (Γ : List VE.Formula) : List VE.Formula :=
  background (fill U) ++ fillPremises U ++ elaborate (fill U).T ++ Γ

end VE.NormDefaults.Wire

namespace VE.NormDefaults
open VE.Norms
universe u

/-- Entailment on a filled document: the conclusion of `normDefaults_wire_acceptance`, named. -/
def EntailsU (U : VE.NormDefaults.UDoc) (Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∀ S : VE.Structure.{u}, VE.NormDefaults.BaseAdmissibleU U (restrictAll (VE.NormDefaults.fill U).T S) →
    DocumentExpansion (VE.NormDefaults.fill U) (restrictAll (VE.NormDefaults.fill U).T S) S → Sat S Γ → φ.denote S []

/-- The certificate half on `fill U`, given only that `Fill_T` is typed at the base: the one proof both
    `acceptanceU` and `normDefaults_wire_acceptance` (whose unprofiled source has no `Fill_T`) use. -/
theorem acceptance_of_fillTyped (U : UDoc) (hfill : ∀ a ∈ fillPremises U, a.WellFormed (envAt (fill U) 0) [])
    (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) (Wire.premisesU U Γ) φ cert = true) :
    EntailsU.{u} U Γ φ := by
  intro S hBU hE hΓ
  apply VE.Tableau.checkCertificate_sound.{u} _ _ _ cert hv S hE.2.1
  intro a ha
  simp only [Wire.premisesU, List.mem_append] at ha
  rcases ha with ((ha | ha) | ha) | ha
  · exact hE.2.2 a (List.mem_append_left _ ha)
  · -- `Fill_T` is a base background: true at the base, hence in the expansion
    exact (restrictAll_denote a [] (hfill a ha) S []).mp (hBU.2 a ha)
  · exact hE.2.2 a (List.mem_append_right _ ha)
  · exact hΓ a ha

/-- `normDefaults_wire_acceptance`'s core on any well-formed UDoc (its proof moves here; its statement is kept). -/
theorem acceptanceU (U : VE.NormDefaults.UDoc) (h : VE.NormDefaults.WellFormedU U = true) (Γ : List VE.Formula)
    (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (VE.NormDefaults.fill U) (size (VE.NormDefaults.fill U)))
      (VE.NormDefaults.Wire.premisesU U Γ) φ cert = true) :
  EntailsU.{u} U Γ φ :=
  acceptance_of_fillTyped U (Wire.fillPremises_wellFormed h) Γ φ cert hv

end VE.NormDefaults

namespace VE.NormDefaults.Wire
open Lean
open VE.Norms
universe u

def EntailmentReplayU.valid (r : EntailmentReplayU) : Bool :=
  VE.Tableau.checkCertificate (envAt (fill r.s.U) (size (fill r.s.U))) (premisesU r.s.U r.premises) r.conclusion r.cert

def replayEntailmentU (j : Json) : Except String EntailmentReplayU := do
  let environment ← j.getObjVal? "environment"
  let s ← decodeSourceU environment (j.getObjValD "norms")
  let E := envAt (fill s.U) (size (fill s.U))
  let premisesJson ← j.getObjVal? "premises"
  let ps ← VE.Route.Wire.decodeFormulas E premisesJson
  let conclusionJson ← j.getObjVal? "conclusion"
  let c ← VE.Route.Wire.decodeClosed E conclusionJson
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  VE.Route.Wire.bindingOk (profilesOf environment) (← canonicalEnvironmentJsonU environment)
    ((background (fill s.U) ++ fillPremises s.U ++ elaborate (fill s.U).T).map enc ++ (← premisesJson.getArr?).toList)
    conclusionJson cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  pure ⟨s, ps, c, cert⟩

/-- `normDefaults_wire_acceptance` (the certificate half of norms 11.4 on `fill U`):
from a successful raw replay with an accepted certificate, for the document
decoded from that very input, the conclusion holds in every filled expansion of
an admissible filling that satisfies the premises. -/
theorem normDefaults_wire_acceptance (j : Json) (r : EntailmentReplayU) (h : replayEntailmentU j = .ok r)
    (hv : r.valid = true) :
    decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.s ∧
    ∀ S : VE.Structure.{u}, BaseAdmissibleU r.s.U (restrictAll (fill r.s.U).T S) →
      DocumentExpansion (fill r.s.U) (restrictAll (fill r.s.U).T S) S → Sat S r.premises →
      r.conclusion.denote S [] := by
  have hdec : decodeSourceU (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.s := by
    unfold replayEntailmentU at h
    obtain ⟨env, henv, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨s, hd, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
    cases h
    have he : j.getObjValD "environment" = env := by
      simp only [Json.getObjValD, henv]
      rfl
    rw [he]; exact hd
  -- `Fill_T` is typed at the base: by `WellFormedU` under the profile, vacuously without it.
  have hfill : ∀ a ∈ fillPremises r.s.U, a.WellFormed (envAt (fill r.s.U) 0) [] := by
    cases hp : r.s.profiled with
    | true => exact fillPremises_wellFormed (r.s.wfU hp)
    | false =>
      rw [fillPremises_nil _ (r.s.plain hp)]
      intro a ha
      cases ha
  exact ⟨hdec, acceptance_of_fillTyped.{u} r.s.U hfill r.premises r.conclusion r.cert hv⟩

end VE.NormDefaults.Wire
