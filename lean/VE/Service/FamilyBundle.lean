import VE.Service.Family

/-! Lemma bundles (PLAN-EXPAND2 W3, `VE/Definitions/Bundle.lean`) over any
family context (SEMANTICS-MIGRATION-PLAN.md stage 2c: bundles on the closure,
core and order families and over norms environments): the service `bundle`
mode.

The rules are `VE.Definitions.Bundle`'s, over the family's formulas and
certificate predicate: a lemma's certificate is replayed on `Background ++ own
hypotheses ++ cited conclusions`; citations are strictly earlier; the lemma
lists exactly Background's labelled leaves, its own hypotheses and every
transitive leaf of the cited lemmas; reading choices along a citation agree;
reading leaves are bound to the latest registered reading set. Background is
the family route's (the context's), labelled `background:<generator>`.

`bundle_sound` states citation soundness at the family's semantics: every
accepted lemma's conclusion holds in every admissible model in which its
transitive leaves (Background's included) hold, and its reading labels are
compatible and bound. Unlike the FOL route's `Definitions.Bundle.bundle_sound`,
Background leaves stay hypotheses here: no theorem of the family routes says
which structures satisfy them. -/
namespace VE.Service.FamilyBundle
open Lean
open VE.Service.GenericGraph (Ent)
open VE.Definitions.Bundle (mergeChoices choicesEqual)
universe u v

section
variable {F C : Type} [DecidableEq F]

abbrev Leaf (F : Type) := String × F

structure ReadingSet (F : Type) where
  id : String
  version : Nat
  readings : List F

structure Lemma (F C : Type) where
  name : String
  premises : List (Leaf F)
  premiseAsts : List Json
  cites : List String
  conclusion : F
  conclusionAst : Json
  meaningId : String
  choices : List (String × String)
  leaves : List (Leaf F)
  certificate : C

structure Known (F : Type) where
  meaningId : String
  conclusion : F
  conclusionAst : Json
  choices : List (String × String)
  leaves : List (Leaf F)

def lookupKnown (known : List (Known F)) (m : String) : Option (Known F) := known.find? (·.meaningId == m)

def appendNew (xs ys : List (Leaf F)) : List (Leaf F) :=
  ys.foldl (fun acc y => if acc.any (fun x => decide (x = y)) then acc else acc ++ [y]) xs

/-- `Definitions.Bundle.addReading` on family leaves (labels only). -/
def addReading (acc : List (String × String)) (l : Leaf F) :
    Except String (List (String × String)) := do
  match VE.Route.Admission.parseLabel l.1 with
  | some (.readings set version choice) =>
    let versionPrefix := toString version ++ ":"
    let value := versionPrefix ++ (choice.map toString).getD "all"
    match VE.Bridge.lookup acc set with
    | none => pure (acc ++ [(set, value)])
    | some old =>
      unless old.startsWith versionPrefix &&
          (old == value || old == versionPrefix ++ "all" || value == versionPrefix ++ "all") do
        throw "Citation has incompatible reading choices"
      if value == versionPrefix ++ "all" then pure acc
      else pure (acc.map fun (s, r) => if s == set then (s, value) else (s, r))
  | _ => pure acc

def leafChoices (ls : List (Leaf F)) : Except String (List (String × String)) :=
  ls.foldlM addReading []

def ReadingCompatible (ls : List (Leaf F)) : Prop := (leafChoices ls).isOk

/-- `Admission.disjunction` over family formulas. -/
def disjunction (disj : F → F → F) : List F → Option F
  | [] => none
  | [a] => some a
  | a :: as => (disjunction disj as).map (disj a)

def leafBoundCheck (disj : F → F → F) (sets : List (ReadingSet F)) (l : Leaf F) : Bool :=
  match VE.Route.Admission.parseLabel l.1 with
  | some (.readings s v c) =>
    match sets.filter (fun rs => rs.id == s && rs.version == v) with
    | [rs] =>
      if sets.any (fun other => other.id == s && other.version > v) then false
      else match c with
        | some i => decide (rs.readings[i]? = some l.2)
        | none => decide (disjunction disj rs.readings = some l.2)
    | _ => false
  | some (.cite _ _) => false
  | some _ => true
  | none => false

def ReadingBound (disj : F → F → F) (sets : List (ReadingSet F)) (ls : List (Leaf F)) : Prop :=
  ∀ l ∈ ls, leafBoundCheck disj sets l = true

def citeAll (known : List (Known F)) :
    List (Leaf F) → List (String × String) → List String →
      Except String (List (Leaf F) × List (String × String) × List (Known F))
  | ls, ch, [] => .ok (ls, ch, [])
  | ls, ch, m :: ms => match lookupKnown known m with
    | none => .error "Citation is absent, cyclic, or not earlier in the bundle"
    | some k => do
      let ch' ← mergeChoices ch k.choices
      let (ls', ch'', cs) ← citeAll known (appendNew ls k.leaves) ch' ms
      pure (ls', ch'', k :: cs)

/-- One lemma against the lemmas before it (`Definitions.Bundle.checkLemma`).
`bind` checks the certificate's binding of the lemma's hypotheses and cited
conclusions (after Background) and its conclusion, all as ASTs; `steps` is the
certificate's replay size. -/
def checkLemma (valid : C → List F → F → Bool) (steps : C → Nat) (disj : F → F → F)
    (bg : List (Leaf F)) (sets : List (ReadingSet F))
    (bind : List Json → Json → C → Except String Unit)
    (known : List (Known F)) (L : Lemma F C) : Except String (Known F) := do
  let (leaves, _, cited) ← citeAll known (bg ++ L.premises) L.choices L.cites
  VE.Route.Gate.require (decide (L.leaves = leaves)) "Citation transitive leaf labels were changed or stripped"
  VE.Route.Gate.require (known.all fun k =>
    if L.cites.contains k.meaningId then
      k.leaves.all fun l => (bg.contains l || L.premises.contains l)
    else true) "Citation hypothesis is absent from the citing branch"
  let derived ← leafChoices leaves
  VE.Route.Gate.require (leaves.all (leafBoundCheck disj sets))
    "Reading label is not bound to its registered reading formula or citation is unresolved"
  VE.Route.Gate.require (choicesEqual L.choices derived) "Citation reading choices do not match transitive leaves"
  VE.Route.Gate.require (!known.any (·.meaningId == L.meaningId)) "Lemma meaning ID is stale or duplicated"
  let checked := bg.map Prod.snd ++ (L.premises.map Prod.snd ++ cited.map Known.conclusion)
  bind (L.premiseAsts ++ cited.map Known.conclusionAst) L.conclusionAst L.certificate
  VE.Route.Gate.require (decide (steps L.certificate ≤ VE.Route.Steps.maxSteps))
    s!"Lemma {L.name} certificate failed"
  VE.Route.Gate.require (valid L.certificate checked L.conclusion) s!"Lemma {L.name} certificate failed"
  pure ⟨L.meaningId, L.conclusion, L.conclusionAst, derived, leaves⟩

def checkAll (valid : C → List F → F → Bool) (steps : C → Nat) (disj : F → F → F)
    (bg : List (Leaf F)) (sets : List (ReadingSet F))
    (bind : List Json → Json → C → Except String Unit) :
    List (Known F) → List (Lemma F C) → Except String (List (Known F))
  | known, [] => .ok known
  | known, L :: Ls => do
    let k ← checkLemma valid steps disj bg sets bind known L
    checkAll valid steps disj bg sets bind (known ++ [k]) Ls

/-! ### Citation soundness -/

theorem mem_appendNew_left (xs ys : List (Leaf F)) : ∀ l ∈ xs, l ∈ appendNew xs ys := by
  induction ys generalizing xs with
  | nil => intro l hl; exact hl
  | cons y ys ih =>
    intro l hl
    unfold appendNew
    simp only [List.foldl_cons]
    apply ih
    split
    · exact hl
    · exact List.mem_append_left _ hl

theorem mem_appendNew_right (xs ys : List (Leaf F)) : ∀ l ∈ ys, l ∈ appendNew xs ys := by
  induction ys generalizing xs with
  | nil => intro l hl; cases hl
  | cons y ys ih =>
    intro l hl
    unfold appendNew
    simp only [List.foldl_cons]
    rcases List.mem_cons.mp hl with rfl | hl
    · apply mem_appendNew_left
      split
      · rename_i h
        obtain ⟨x, hx, he⟩ := List.any_eq_true.mp h
        rw [← of_decide_eq_true he]; exact hx
      · exact List.mem_append_right _ (List.mem_singleton_self _)
    · exact ih _ l hl

omit [DecidableEq F] in
theorem lookupKnown_mem {known : List (Known F)} {m : String} {k : Known F}
    (h : lookupKnown known m = some k) : k ∈ known :=
  List.mem_of_find?_eq_some h

open VE.Order.ProfileGate in
theorem citeAll_sound (known : List (Known F)) : ∀ (ms : List String) (ls : List (Leaf F))
    (ch : List (String × String)) (ls' : List (Leaf F)) (ch' : List (String × String))
    (cs : List (Known F)),
    citeAll known ls ch ms = .ok (ls', ch', cs) →
      (∀ l ∈ ls, l ∈ ls') ∧ ∀ c ∈ cs, c ∈ known ∧ ∀ l ∈ c.leaves, l ∈ ls'
  | [], ls, ch, ls', ch', cs, h => by
    simp only [citeAll, Except.ok.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, _, rfl⟩ := h
    exact ⟨fun _ h => h, fun _ h => nomatch h⟩
  | m :: ms, ls, ch, ls', ch', cs, h => by
    unfold citeAll at h
    split at h
    · cases h
    · rename_i k hk
      obtain ⟨chm, _, h⟩ := bind_ok h
      obtain ⟨⟨ls₁, ch₁, cs₁⟩, hr, h⟩ := bind_ok h
      simp only [pure, Except.pure, Except.ok.injEq, Prod.mk.injEq] at h
      obtain ⟨rfl, rfl, rfl⟩ := h
      obtain ⟨hsub, hcs⟩ := citeAll_sound known ms _ _ _ _ _ hr
      refine ⟨fun l hl => hsub l (mem_appendNew_left _ _ l hl), fun c hc => ?_⟩
      rcases List.mem_cons.mp hc with rfl | hc
      · exact ⟨lookupKnown_mem hk, fun l hl => hsub l (mem_appendNew_right _ _ l hl)⟩
      · exact hcs c hc

section Soundness
variable {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
  (valid : C → List F → F → Bool) (steps : C → Nat) (disj : F → F → F)
  (sound : ∀ c ps r, valid c ps r = true → Ent Adm Holds ps r)
  (bg : List (Leaf F)) (sets : List (ReadingSet F)) (bind : List Json → Json → C → Except String Unit)

/-- A checked lemma's meaning: in every admissible model where its leaves hold,
its conclusion holds. -/
def Sound (k : Known F) : Prop :=
  ∀ S, Adm S → (∀ l ∈ k.leaves, Holds S l.2) → Holds S k.conclusion

include sound

open VE.Order.ProfileGate in
theorem checkLemma_sound (known : List (Known F)) (hk : ∀ k ∈ known, Sound Adm Holds k)
    (L : Lemma F C) (k : Known F)
    (h : checkLemma valid steps disj bg sets bind known L = .ok k) : Sound Adm Holds k := by
  unfold checkLemma at h
  obtain ⟨⟨leaves, choices, cited⟩, hc, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, hcert, h⟩ := bind_ok h
  simp only [pure, Except.pure, Except.ok.injEq] at h
  subst h
  obtain ⟨hsub, hcited⟩ := citeAll_sound known L.cites _ _ _ _ _ hc
  have he := sound L.certificate _ L.conclusion (VE.Route.Gate.require_ok hcert)
  intro S hS hl
  apply he S hS
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · obtain ⟨l, hlm, rfl⟩ := List.mem_map.mp ha
    exact hl l (hsub l (List.mem_append_left _ hlm))
  rcases List.mem_append.mp ha with ha | ha
  · obtain ⟨l, hlm, rfl⟩ := List.mem_map.mp ha
    exact hl l (hsub l (List.mem_append_right _ hlm))
  · obtain ⟨k', hk', rfl⟩ := List.mem_map.mp ha
    obtain ⟨hmem, hleaves⟩ := hcited k' hk'
    exact hk k' hmem S hS (fun l hm => hl l (hleaves l hm))

open VE.Order.ProfileGate in
theorem checkAll_sound : ∀ (known : List (Known F)) (Ls : List (Lemma F C)) (res : List (Known F)),
    (∀ k ∈ known, Sound Adm Holds k) → checkAll valid steps disj bg sets bind known Ls = .ok res →
      ∀ k ∈ res, Sound Adm Holds k
  | known, [], res, hk, h => by
    simp only [checkAll, Except.ok.injEq] at h
    subst h; exact hk
  | known, L :: Ls, res, hk, h => by
    unfold checkAll at h
    obtain ⟨k, hL, h⟩ := bind_ok h
    have hk' := checkLemma_sound Adm Holds valid steps disj sound bg sets bind known hk L k hL
    refine checkAll_sound (known ++ [k]) Ls res (fun k₁ hm => ?_) h
    rcases List.mem_append.mp hm with hm | hm
    · exact hk k₁ hm
    · rw [List.mem_singleton.mp hm]; exact hk'

end Soundness

open VE.Order.ProfileGate in
theorem checkLemma_labels (valid : C → List F → F → Bool) (steps : C → Nat) (disj : F → F → F)
    (bg : List (Leaf F)) (sets : List (ReadingSet F)) (bind : List Json → Json → C → Except String Unit)
    (known : List (Known F)) (L : Lemma F C) (k : Known F)
    (h : checkLemma valid steps disj bg sets bind known L = .ok k) :
    ReadingCompatible k.leaves ∧ ReadingBound disj sets k.leaves := by
  unfold checkLemma at h
  obtain ⟨⟨leaves, _, _⟩, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨derived, hd, h⟩ := bind_ok h
  obtain ⟨_, hb, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  refine ⟨by simp only [ReadingCompatible, hd]; rfl, fun l hl => ?_⟩
  exact (List.all_eq_true.mp (VE.Route.Gate.require_ok hb)) l hl

open VE.Order.ProfileGate in
theorem checkAll_labels (valid : C → List F → F → Bool) (steps : C → Nat) (disj : F → F → F)
    (bg : List (Leaf F)) (sets : List (ReadingSet F)) (bind : List Json → Json → C → Except String Unit) :
    ∀ (known : List (Known F)) (Ls : List (Lemma F C)) (res : List (Known F)),
    (∀ k ∈ known, ReadingCompatible k.leaves ∧ ReadingBound disj sets k.leaves) →
    checkAll valid steps disj bg sets bind known Ls = .ok res →
      ∀ k ∈ res, ReadingCompatible k.leaves ∧ ReadingBound disj sets k.leaves
  | known, [], res, hk, h => by
    simp only [checkAll, Except.ok.injEq] at h
    subst h; exact hk
  | known, L :: Ls, res, hk, h => by
    unfold checkAll at h
    obtain ⟨k, hL, h⟩ := bind_ok h
    have hk' := checkLemma_labels valid steps disj bg sets bind known L k hL
    refine checkAll_labels valid steps disj bg sets bind (known ++ [k]) Ls res (fun k₁ hm => ?_) h
    rcases List.mem_append.mp hm with hm | hm
    · exact hk k₁ hm
    · rw [List.mem_singleton.mp hm]; exact hk'

/-- `bundle_sound` at a family's semantics: every accepted lemma has
compatible, bound reading labels, and its conclusion holds in every admissible
model in which its transitive leaves hold. -/
theorem bundle_sound {Model : Type v} (Adm : Model → Prop) (Holds : Model → F → Prop)
    (valid : C → List F → F → Bool) (steps : C → Nat) (disj : F → F → F)
    (sound : ∀ c ps r, valid c ps r = true → Ent Adm Holds ps r)
    (bg : List (Leaf F)) (sets : List (ReadingSet F)) (bind : List Json → Json → C → Except String Unit)
    (Ls : List (Lemma F C)) (res : List (Known F))
    (accepted : checkAll valid steps disj bg sets bind [] Ls = .ok res) :
    ∀ k ∈ res, (ReadingCompatible k.leaves ∧ ReadingBound disj sets k.leaves) ∧
      ∀ S, Adm S → (∀ l ∈ k.leaves, Holds S l.2) → Holds S k.conclusion :=
  fun k hk => ⟨checkAll_labels valid steps disj bg sets bind [] Ls res (fun _ h => nomatch h) accepted k hk,
    checkAll_sound Adm Holds valid steps disj sound bg sets bind [] Ls res (fun _ h => nomatch h)
      accepted k hk⟩

end

/-! ## Wire -/

section Wire
variable {F C M : Type} [DecidableEq F]
open VE.Bridge (exactFields stringField strings fields)

def decodeLeaf (ctx : Family.Ctx F C M) (j : Json) : Except String (Leaf F × Json) := do
  exactFields j ["label", "ast"]
  let label ← stringField j "label"
  unless (VE.Route.Admission.parseLabel label).isSome do throw s!"AdmissionError: invalid label {label}"
  let ast ← j.getObjVal? "ast"
  pure ((label, ← ctx.formula ast), ast)

def decodeLemma (ctx : Family.Ctx F C M) (j : Json) : Except String (Lemma F C) := do
  exactFields j ["name", "environment_id", "premises", "cites", "conclusion", "meaning_id",
    "reading_choices", "transitive_leaves", "certificate"]
  unless (← stringField j "environment_id") == ctx.envId do
    throw "Citation has another environment or definitions version"
  let name ← stringField j "name"
  if name.isEmpty then throw "Lemma name must be nonempty"
  let premises ← (← (← j.getObjVal? "premises").getArr?).toList.mapM (decodeLeaf ctx)
  let cites ← strings (← j.getObjVal? "cites")
  let conclusionAst ← j.getObjVal? "conclusion"
  let conclusion ← ctx.formula conclusionAst
  let meaningId ← stringField j "meaning_id"
  unless meaningId == (← ctx.meaningId conclusionAst) do
    throw "Lemma meaning ID is stale or duplicated"
  let choices ← (← fields (← j.getObjVal? "reading_choices")).mapM fun (u, r) => do
    pure (u, ← r.getStr?)
  let leaves ← (← (← j.getObjVal? "transitive_leaves").getArr?).toList.mapM (decodeLeaf ctx)
  let certificate ← ctx.certificate (← j.getObjVal? "certificate")
  pure ⟨name, premises.map Prod.fst, premises.map Prod.snd, cites, conclusion, conclusionAst,
    meaningId, choices, leaves.map Prod.fst, certificate⟩

def decodeReadingSet (ctx : Family.Ctx F C M) (j : Json) : Except String (ReadingSet F) := do
  exactFields j ["id", "version", "readings"]
  let id ← stringField j "id"
  VE.Route.Gate.require (VE.Route.Admission.token id) s!"invalid reading set id {id}"
  let version ← (← j.getObjVal? "version").getNat?
  let readings ← (← (← j.getObjVal? "readings").getArr?).toList.mapM ctx.formula
  VE.Route.Gate.require (!readings.isEmpty && readings.length ≤ 64) "reading sets hold 1 to 64 readings"
  pure ⟨id, version, readings⟩

/-- A bundle over a family context: decode every lemma, then check the whole
bundle in order (`Definitions.Bundle.runBundle`). -/
def run (ctx : Family.Ctx F C M) (valid : C → List F → F → Bool) (steps : C → Nat)
    (disj : F → F → F) (id : String) (j : Json) : Except String Json := do
  let items := (← (← j.getObjVal? "lemmas").getArr?).toList
  if items.length > 256 then throw "ResourceLimit: Lemma bundle exceeds 256 lemmas"
  let sets ← match j.getObjVal? "document" with
    | .error _ => pure ([] : List (ReadingSet F))
    | .ok doc => do
      exactFields doc ["reading_sets"]
      let sets ← (← (← doc.getObjVal? "reading_sets").getArr?).toList.mapM (decodeReadingSet ctx)
      VE.Route.Gate.require ((sets.map (fun rs => (rs.id, rs.version))).eraseDups.length == sets.length)
        "duplicate reading set version"
      pure sets
  let lemmas ← items.mapM (decodeLemma ctx)
  let names := lemmas.map Lemma.name
  unless names.eraseDups.length == names.length do throw "Duplicate lemma name"
  let background := ctx.background.map fun (formula, _, generator) => ("background:" ++ generator, formula)
  let known ← checkAll valid steps disj background sets ctx.bound [] lemmas
  pure (VE.Route.Wire.ok id [("checked", toJson known.length),
    ("lemmas", Json.arr (known.map (fun k => Json.str k.meaningId)).toArray)])

end Wire

/-- The FOL family context (the route vocabulary, its Background with the
norms profile premises, the FOL certificate): bundles over norms environments,
which the route's bundle case refuses. -/
def folCtx (environment : Json) (checked : Standalone.Validated) :
    Except String (VE.Route.Wire.RouteVocabulary ×
      Family.Ctx VE.Formula VE.Tableau.Certificate Unit) := do
  let e := checked.envelope
  let rv ← VE.Route.Run.decodeRouteVocabulary e
  let envId ← Standalone.environmentIdOf e.profiles environment
  let bg ← Standalone.folBackground environment rv
  pure (rv, {
    environment := environment
    envId := envId
    version := VE.Route.Wire.identityVersion e.profiles
    formula := fun a => VE.Route.Wire.decodeClosed rv.environment a (e.profiles.contains "data@0")
    meaningId := VE.Route.Wire.meaningId e.profiles envId
    certificate := VE.CertificateWire.decodeCertificate
    bound := fun premises conclusion c => VE.Route.Wire.bindingOk e.profiles environment
      (bg.map (VE.Route.Wire.encodeFormula ·.1) ++ premises) conclusion
      c.environment_id c.premise_meaning_ids c.conclusion_meaning_id
    background := Family.withAst bg id
    model := fun _ => throw "no models in a bundle" })

/-- The service `bundle` mode: a lemma bundle over a ve.core@0.2 environment of
any family, norms environments included, or over a frozen pre-route envelope. -/
def bundleCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let environment ← j.getObjVal? "environment"
  if Standalone.isLegacy environment then
    match ← Standalone.decodeLegacy environment with
    | .v0 v =>
      return ← run (← Family.legacyFolCtx environment v) (Family.folValid v.environment)
        (fun c => VE.Route.Steps.fol c.trace) .or id j
    | .closure v =>
      return ← run (← Family.legacyClosureCtx environment v) (Family.closureValid v.environment)
        (fun c => VE.Route.Steps.closure c.trace) .or id j
    | .order v =>
      return ← run (← Family.legacyOrderCtx environment v) (Family.orderValid v.environment)
        (fun c => VE.Route.Steps.order c.trace) .or id j
  let checked ← Standalone.validated environment
  match checked.envelope.family with
  | .fol =>
    let (rv, ctx) ← folCtx environment checked
    run ctx (Family.folValid rv.environment) (fun c => VE.Route.Steps.fol c.trace) .or id j
  | .closure =>
    let f ← Family.closureEnv environment checked
    run f.ctx (Family.closureValid f.rv.environment) (fun c => VE.Route.Steps.closure c.trace) .or id j
  | .closureNary =>
    let f ← Family.coreEnv environment checked
    run f.ctx (Family.coreValid f.v.environment) (fun c => VE.Route.Steps.core c.trace) .or id j
  | .order =>
    let f ← Family.orderEnv environment checked
    run f.ctx (Family.orderValid f.rv.vocabulary.environment) (fun c => VE.Route.Steps.order c.trace)
      .or id j

/-! ### What an accepted bundle means, per family -/

theorem fol_bundle_sound (E : VE.Environment) (bg : List (Leaf VE.Formula))
    (sets : List (ReadingSet VE.Formula)) (bind : List Json → Json → VE.Tableau.Certificate → Except String Unit)
    (Ls : List (Lemma VE.Formula VE.Tableau.Certificate)) (res : List (Known VE.Formula))
    (accepted : checkAll (Family.folValid E) (fun c => VE.Route.Steps.fol c.trace) .or bg sets bind [] Ls = .ok res) :
    ∀ k ∈ res, (ReadingCompatible k.leaves ∧ ReadingBound .or sets k.leaves) ∧
      ∀ S : VE.Structure.{u}, S.Admissible E → (∀ l ∈ k.leaves, l.2.denote S []) → k.conclusion.denote S [] :=
  bundle_sound (fun S : VE.Structure.{u} => S.Admissible E) (fun S (a : VE.Formula) => a.denote S [])
    _ _ _ (fun c ps r h => VE.Tableau.checkCertificate_sound E ps r c h) bg sets bind Ls res accepted

theorem closure_bundle_sound (E : VE.Environment) (bg : List (Leaf VE.Closure.Formula))
    (sets : List (ReadingSet VE.Closure.Formula))
    (bind : List Json → Json → VE.Closure.Tableau.Certificate → Except String Unit)
    (Ls : List (Lemma VE.Closure.Formula VE.Closure.Tableau.Certificate)) (res : List (Known VE.Closure.Formula))
    (accepted : checkAll (Family.closureValid E) (fun c => VE.Route.Steps.closure c.trace) .or bg sets bind [] Ls
      = .ok res) :
    ∀ k ∈ res, (ReadingCompatible k.leaves ∧ ReadingBound .or sets k.leaves) ∧
      ∀ S : VE.Structure.{u}, S.Admissible E → (∀ l ∈ k.leaves, l.2.denote S []) → k.conclusion.denote S [] :=
  bundle_sound (fun S : VE.Structure.{u} => S.Admissible E) (fun S (a : VE.Closure.Formula) => a.denote S [])
    _ _ _ (fun c ps r h => VE.Closure.Tableau.checkCertificate_sound E ps r c h) bg sets bind Ls res accepted

theorem core_bundle_sound (E : VE.Environment) (bg : List (Leaf VE.Core.Formula))
    (sets : List (ReadingSet VE.Core.Formula))
    (bind : List Json → Json → VE.Core.Tableau.Certificate → Except String Unit)
    (Ls : List (Lemma VE.Core.Formula VE.Core.Tableau.Certificate)) (res : List (Known VE.Core.Formula))
    (accepted : checkAll (Family.coreValid E) (fun c => VE.Route.Steps.core c.trace) .or bg sets bind [] Ls
      = .ok res) :
    ∀ k ∈ res, (ReadingCompatible k.leaves ∧ ReadingBound .or sets k.leaves) ∧
      ∀ S : VE.Structure.{u}, S.Admissible E → (∀ l ∈ k.leaves, l.2.denote S []) → k.conclusion.denote S [] :=
  bundle_sound (fun S : VE.Structure.{u} => S.Admissible E) (fun S (a : VE.Core.Formula) => a.denote S [])
    _ _ _ (fun c ps r h => VE.Core.Tableau.checkCertificate_sound E ps r c h) bg sets bind Ls res accepted

theorem order_bundle_sound (E : VE.Order.Environment) (bg : List (Leaf VE.Order.Formula))
    (sets : List (ReadingSet VE.Order.Formula))
    (bind : List Json → Json → VE.Order.Tableau.Certificate → Except String Unit)
    (Ls : List (Lemma VE.Order.Formula VE.Order.Tableau.Certificate)) (res : List (Known VE.Order.Formula))
    (accepted : checkAll (Family.orderValid E) (fun c => VE.Route.Steps.order c.trace) .or bg sets bind [] Ls
      = .ok res) :
    ∀ k ∈ res, (ReadingCompatible k.leaves ∧ ReadingBound .or sets k.leaves) ∧
      ∀ S : VE.Order.Structure.{u}, S.Admissible E → (∀ l ∈ k.leaves, l.2.denote S []) →
        k.conclusion.denote S [] :=
  bundle_sound (fun S : VE.Order.Structure.{u} => S.Admissible E) (fun S (a : VE.Order.Formula) => a.denote S [])
    _ _ _ (fun c ps r h => VE.Order.Tableau.checkCertificate_sound E ps r c h) bg sets bind Ls res accepted

end VE.Service.FamilyBundle
