import VE.Compose.Slot
import VE.SoftNorms.Wire
import VE.EvaluationCounts

/-! The premise slot of the soft route on the wire (kb-3; docs/spec/kernel-boundary.md 4.1, 4.2, 7).

A case may send `facts`: closed formulas over the soft route's base vocabulary `E′_base :=
envAt (soften D) 0` (`decodeFacts`). They are the slot `P` of `lean/VE/Compose/Slot.lean`, and the three
replays below are the soft replays of `lean/VE/SoftNorms/Wire.lean` relative to `P`:

* `replaySlotConflict`: the conflict packages are bound to `Background_base′ ++ P` and checked by
  `slotConflictFreeCheck` (`slot_wire_conflict_sound`, from `slot_conflict_free`);
* `replaySlotWitness`: the soft witness, whose model must also satisfy `P`
  (`slot_wire_conflict_witness_sound`, from `slot_conflict_witness_sound`);
* `replaySlotEntailment`: the certificate is bound to `background′ ++ P ++ layer premises ++ premises`
  (`slot_wire_acceptance`, from `slot_route_acceptance`).

A non-empty `P` must come with `facts_model`, a base model of `Background_base′ ++ P` (`factsModel`):
`ConflictFreeP` and an accepted certificate are vacuous when `P` cannot hold together with the base, so
an accepted answer shows that it can (`slot_wire_conflict_facts`, `slot_wire_entailment_facts`).
Every fact is read from the request's own `facts`, one formula per item (`decodeFacts_ok`). With no
facts each replay is its soft twin (`slot_wire_empty`): no existing answer can change. -/
namespace VE.Compose.SlotWire
open Lean
open VE.Norms
open VE.SoftNorms (SoftDoc soften WellFormedSoft background' backgroundBase' backgroundValid' softPremises holdsSoft
  SoftConflictFree softConflictFreeCheck NoStrictCollision NoHardPairConflict)
open VE.SoftNorms.Wire
open VE.Compose
open VE.Order.ProfileGate (bind_ok)

/-! ## The facts -/

/-- The request's `facts`: absent, no facts; else an array whose every item decodes, by the route's
formula decoder, to a closed formula over the base vocabulary (a rule's predicate or a layer symbol is not
in it, so the decoder refuses it), and names no soft decision predicate (an open term: its decider decides
it, docs/spec/kernel-boundary.md 4.1). The raw items are kept for the certificates' bindings. -/
def decodeFacts (src : SoftSource) (j : Json) : Except String (List VE.Formula × List Json) :=
  match j.getObjVal? "facts" with
  | .error _ => pure ([], [])
  | .ok v => match v.getArr? with
    | .error _ => throw "InvalidInput: facts must be an array"
    | .ok items =>
      if items.isEmpty then pure ([], []) else do
        let fs ← VE.Route.Wire.decodeFormulas (envAt (soften src.D) 0) v
        match (fs.flatMap VE.Norms.preds).find? (fun p => (VE.SoftNorms.decisionNames src.D).contains p) with
        | some p => throw s!"InvalidInput: facts: {p} is a soft decision predicate; its decider decides it, not a fact"
        | none => pure (fs, items.toList)

/-- The diagnostic of a base model that fails the soft background or a fact. -/
def slotModelFault (src : SoftSource) (M : VE.FiniteModel VE.Bridge.Entity) : String :=
  if backgroundValid' src.D M then "InvalidModel(facts): the model violates a fact"
  else VE.Route.Wire.invalidModel "soft background"

/-- Facts need a model: `facts_model`, a base model over `E′_base` in which `Background_base′` and every
fact hold. No facts, no model. -/
def factsModel (src : SoftSource) (P : List VE.Formula) (j : Json) : Except String Unit :=
  if P.isEmpty then pure () else
  match j.getObjVal? "facts_model" with
  | .error _ => throw "InvalidInput: facts need a facts_model: a base model of the background and the facts"
  | .ok m => do
    let ⟨M, _⟩ ← decodeModel src (Json.mkObj [("model", m)])
    unless backgroundValidP src.D P M do throw (slotModelFault src M)

theorem decodeFormulas_check (E : VE.Environment) (j : Json) (fs : List VE.Formula)
    (h : VE.Route.Wire.decodeFormulas E j = .ok fs) : ∀ a ∈ fs, a.check E [] = true := by
  unfold VE.Route.Wire.decodeFormulas at h
  obtain ⟨js, _, h⟩ := bind_ok h
  obtain ⟨fs', _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  simp only [Bool.false_and, Bool.false_eq_true, ↓reduceIte, pure, Except.pure, bind, Except.bind] at h
  split at h
  · rename_i hc
    simp only [Except.ok.injEq] at h
    subst h
    simpa [List.all_eq_true] using hc
  · cases h

/-- What a decoded slot is: the request's own items (none when `facts` is absent), one well-formed
base formula per item. -/
theorem decodeFacts_ok {src : SoftSource} {j : Json} {P : List VE.Formula} {items : List Json}
    (h : decodeFacts src j = .ok (P, items)) :
    SlotWellFormed src.D P ∧ P.length = items.length ∧
      (∀ a ∈ P, ∀ p ∈ VE.Norms.preds a, p ∉ VE.SoftNorms.decisionNames src.D) ∧
      ((∃ e, j.getObjVal? "facts" = .error e) ∧ items = [] ∨ j.getObjVal? "facts" = .ok (Json.arr items.toArray)) := by
  unfold decodeFacts at h
  split at h
  · rename_i e he
    simp only [pure, Except.pure, Except.ok.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    exact ⟨(fun a ha => nomatch ha), rfl, (fun a ha => nomatch ha), Or.inl ⟨⟨e, he⟩, rfl⟩⟩
  · rename_i v hv
    split at h
    · cases h
    · rename_i arr harr
      have hvarr : v = Json.arr arr := by
        cases v <;> simp only [Json.getArr?, pure, Except.pure] at harr <;> first | (cases harr; rfl) | cases harr
      split at h
      · rename_i he
        simp only [pure, Except.pure, Except.ok.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        have : arr = #[] := by simpa using he
        subst this
        exact ⟨(fun a ha => nomatch ha), rfl, (fun a ha => nomatch ha), Or.inr (by rw [hv, hvarr])⟩
      · obtain ⟨fs, hfs, h⟩ := bind_ok h
        split at h
        · cases h
        rename_i hnone
        simp only [pure, Except.pure, Except.ok.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        obtain ⟨arr', harr', hlen⟩ := VE.EvaluationCounts.route_decodeFormulas_length v false hfs
        rw [harr] at harr'
        cases harr'
        refine ⟨fun a ha => (VE.check_iff_wellFormed _ _ a).mp (decodeFormulas_check _ _ _ hfs a ha),
          by simpa using hlen, fun a ha p hp hd => ?_, .inr ?_⟩
        · have := List.find?_eq_none.mp hnone p (List.mem_flatMap.mpr ⟨a, ha, hp⟩)
          simp_all
        · rw [hv, hvarr, Array.toArray_toList]

/-- `facts` absent or empty. -/
def NoFacts (j : Json) : Prop := (∃ e, j.getObjVal? "facts" = .error e) ∨ j.getObjVal? "facts" = .ok (.arr #[])

theorem decodeFacts_empty (src : SoftSource) {j : Json} (h : NoFacts j) : decodeFacts src j = .ok ([], []) := by
  rcases h with ⟨e, he⟩ | he <;> simp [decodeFacts, he, Json.getArr?, pure, Except.pure]

theorem factsModel_nil (src : SoftSource) (j : Json) : factsModel src [] j = .ok () := rfl

/-- An accepted facts model is a base structure admissible for the slot. -/
theorem factsModel_sat {src : SoftSource} {P : List VE.Formula} {j : Json} (h : factsModel src P j = .ok ())
    (hne : P ≠ []) : ∃ B : VE.Structure.{0}, BaseAdmissibleP src.D P B := by
  unfold factsModel at h
  have hP : P.isEmpty = false := by cases P <;> simp_all
  simp only [hP, Bool.false_eq_true, ↓reduceIte] at h
  split at h
  · cases h
  · obtain ⟨⟨M, hM⟩, _, h⟩ := bind_ok h
    simp only at h
    split at h
    · rename_i hb
      exact ⟨_, baseAdmissibleP_of_valid src.D P M hM hb⟩
    · cases h

/-! ## Conflict packages relative to the slot -/

/-- `decodeSoftPackage` with the certificate's premise binding `Background_base′` followed by the facts'
wire items. -/
def decodeSlotPackage (src : SoftSource) (environment norms packages : Json) (items : List Json)
    (t : String × List String × VE.Formula) : Option VE.Tableau.Certificate := Id.run do
  let some baseEnv := (basePrimeJson src.D environment).toOption | none
  let some baseProfiles := (VE.Bridge.strings (baseEnv.getObjValD "profiles")).toOption | none
  let some canonical := (Norms.Wire.canonicalEnvironmentJson environment).toOption | none
  let some envId := (VE.Route.Wire.environmentId src.se.profiles canonical).toOption | none
  let some docHash := (softDocumentHash src.se.profiles environment norms).toOption | none
  let package := packages.getObjValD t.1
  unless package.getObjValD "environment_id" == .str envId &&
      package.getObjValD "document_hash" == .str docHash &&
      package.getObjValD "target" == .str t.1 do return none
  let some c := (VE.CertificateWire.decodeCertificate (package.getObjValD "certificate")).toOption | none
  match VE.Route.Wire.bindingOk baseProfiles baseEnv ((backgroundBase' src.D).map enc ++ items)
      (enc (targetConclusion t)) c.environment_id c.premise_meaning_ids c.conclusion_meaning_id with
  | .ok () => some c
  | .error _ => none

structure SlotConflictReplay where
  src : SoftSource
  facts : List VE.Formula
  items : List Json
  certs : List (Option VE.Tableau.Certificate)

def SlotConflictReplay.conflictFree (r : SlotConflictReplay) : Bool := slotConflictFreeCheck r.src.D r.facts r.certs

def replaySlotConflict (j : Json) : Except String SlotConflictReplay := do
  let environment ← j.getObjVal? "environment"
  let norms := j.getObjValD "norms"
  let src ← decodeSoftSource environment norms
  let (P, items) ← decodeFacts src j
  factsModel src P j
  let packages := j.getObjValD "packages"
  pure ⟨src, P, items, (targets (soften src.D)).map (decodeSlotPackage src environment norms packages items)⟩

theorem replaySlotConflict_parts (j : Json) (res : SlotConflictReplay) (h : replaySlotConflict j = .ok res) :
    decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok res.src ∧
      decodeFacts res.src j = .ok (res.facts, res.items) ∧ factsModel res.src res.facts j = .ok () := by
  unfold replaySlotConflict at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨src, hd, h⟩ := bind_ok h
  obtain ⟨⟨P, items⟩, hf, h⟩ := bind_ok h
  obtain ⟨_, hm, h⟩ := bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  exact ⟨by rw [he]; exact hd, hf, hm⟩

/-- A successful slot replay whose every target certificate is accepted: the input decodes to the
replayed well-formed soft document and well-formed facts, and the document is conflict-free over every
coherent base in which the facts hold. -/
theorem slot_wire_conflict_sound (j : Json) (res : SlotConflictReplay) (h : replaySlotConflict j = .ok res)
    (hv : res.conflictFree = true) :
    decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok res.src ∧
      WellFormedSoft res.src.D = true ∧ SlotWellFormed res.src.D res.facts ∧ ConflictFreeP.{0} res.src.D res.facts := by
  obtain ⟨hd, hf, _⟩ := replaySlotConflict_parts j res h
  exact ⟨hd, res.src.wf, (decodeFacts_ok hf).1, slot_conflict_free res.src.D res.src.wf res.facts res.certs hv⟩

/-- The facts of a slot conflict replay are the request's, and, when there are any, they hold together
with `Background_base′` in some base structure: `ConflictFreeP` is not vacuous. -/
theorem slot_wire_conflict_facts (j : Json) (res : SlotConflictReplay) (h : replaySlotConflict j = .ok res) :
    decodeFacts res.src j = .ok (res.facts, res.items) ∧
      (res.facts ≠ [] → ∃ B : VE.Structure.{0}, BaseAdmissibleP res.src.D res.facts B) := by
  obtain ⟨_, hf, hm⟩ := replaySlotConflict_parts j res h
  exact ⟨hf, factsModel_sat hm⟩

/-- `firstFailure` relative to the slot. -/
def slotFirstFailure (r : SlotConflictReplay) : Option String :=
  (((targets (soften r.src.D)).zip r.certs).find? (fun (t, c) => match c with
    | some c => !VE.Tableau.checkCertificate (envAt (soften r.src.D) 0) (backgroundBaseP r.src.D r.facts)
        (targetConclusion t) c
    | none => true)).map (fun (t, c) => match c with
      | some _ => s!"invalid certificate for {t.1}"
      | none => s!"missing certificate for {t.1}")

/-! ## Witnesses relative to the slot -/

/-- A soft witness whose model also satisfies every fact. -/
structure SlotWitnessData (src : SoftSource) (P : List VE.Formula) where
  sw : SoftWitnessData src
  facts : P.all (fun a => a.eval sw.M []) = true

def SlotWitnessData.M {src : SoftSource} {P : List VE.Formula} (w : SlotWitnessData src P) :
    VE.FiniteModel VE.Bridge.Entity := w.sw.M
def SlotWitnessData.target {src : SoftSource} {P : List VE.Formula} (w : SlotWitnessData src P) :
    String × List String × VE.Formula := w.sw.target
def SlotWitnessData.tuple {src : SoftSource} {P : List VE.Formula} (w : SlotWitnessData src P) :
    List VE.Bridge.Entity := w.sw.tuple
def SlotWitnessData.conflict {src : SoftSource} {P : List VE.Formula} (w : SlotWitnessData src P) : Bool :=
  w.sw.conflict

theorem SlotWitnessData.background {src : SoftSource} {P : List VE.Formula} (w : SlotWitnessData src P) :
    backgroundValidP src.D P w.M = true := by
  simp only [backgroundValidP, Bool.and_eq_true]
  exact ⟨w.sw.background, w.facts⟩

def slotWitnessFrom (src : SoftSource) (P : List VE.Formula) (w : Json) : Except String (SlotWitnessData src P) := do
  let sw ← softWitnessFrom src w
  if hf : P.all (fun a => a.eval sw.M []) = true then pure ⟨sw, hf⟩
  else throw (slotModelFault src sw.M)

structure SlotWitnessReplay where
  src : SoftSource
  facts : List VE.Formula
  items : List Json
  w : SlotWitnessData src facts

def replaySlotWitness (j : Json) : Except String SlotWitnessReplay := do
  let environment ← j.getObjVal? "environment"
  let src ← decodeSoftSource environment (j.getObjValD "norms")
  let (P, items) ← decodeFacts src j
  let wd ← slotWitnessFrom src P (← j.getObjVal? "witness")
  pure ⟨src, P, items, wd⟩

theorem replaySlotWitness_parts (j : Json) (r : SlotWitnessReplay) (h : replaySlotWitness j = .ok r) :
    decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.src ∧
      decodeFacts r.src j = .ok (r.facts, r.items) := by
  unfold replaySlotWitness at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨src, hd, h⟩ := bind_ok h
  obtain ⟨⟨P, items⟩, hf, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  exact ⟨by rw [he]; exact hd, hf⟩

/-- A successful slot witness replay whose regenerated target formula is true at the typed tuple: the
input decodes to that document; the model is a coherent base in which every fact holds, and it refutes
conflict-freedom relative to the facts; the witness is a strict collision or a pair conflict. -/
theorem slot_wire_conflict_witness_sound (j : Json) (r : SlotWitnessReplay) (h : replaySlotWitness j = .ok r)
    (hw : r.w.conflict = true) :
    decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.src ∧
    BaseAdmissibleP.{0} r.src.D r.facts r.w.M.asStructure ∧
    ¬ VE.Norms.ConflictFree (soften r.src.D) r.w.M.asStructure ∧ ¬ ConflictFreeP.{0} r.src.D r.facts ∧
    (¬ NoStrictCollision r.src.D r.w.M.asStructure ∨ ¬ NoHardPairConflict r.src.D r.w.M.asStructure) := by
  obtain ⟨hd, _⟩ := replaySlotWitness_parts j r h
  have hB := baseAdmissibleP_of_valid r.src.D r.facts r.w.M r.w.sw.valid r.w.background
  obtain ⟨hn, hc, hcl⟩ := slot_conflict_witness_sound r.src.D r.src.wf r.facts r.w.target r.w.sw.mem r.w.M
    r.w.sw.valid r.w.background r.w.tuple r.w.sw.typed hw
  exact ⟨hd, hB, hn, hc, hcl⟩

/-- The facts of a slot witness replay are the request's. -/
theorem slot_wire_witness_facts (j : Json) (r : SlotWitnessReplay) (h : replaySlotWitness j = .ok r) :
    decodeFacts r.src j = .ok (r.facts, r.items) :=
  (replaySlotWitness_parts j r h).2

/-! ## Entailment certificates relative to the slot -/

structure SlotEntailmentReplay where
  src : SoftSource
  facts : List VE.Formula
  items : List Json
  premises : List VE.Formula
  conclusion : VE.Formula
  cert : VE.Tableau.Certificate

def SlotEntailmentReplay.valid (r : SlotEntailmentReplay) : Bool :=
  VE.Tableau.checkCertificate (envAt (soften r.src.D) (size (soften r.src.D)))
    (backgroundP r.src.D r.facts ++ elaborate (soften r.src.D).T ++ r.premises) r.conclusion r.cert

/-- `replaySoftEntailment` with the facts after `background′`: the certificate is bound to the regenerated
`E′`, `background′`, the facts' wire items, the layer premises, the premises and the conclusion. -/
def replaySlotEntailment (j : Json) : Except String SlotEntailmentReplay := do
  let environment ← j.getObjVal? "environment"
  let src ← decodeSoftSource environment (j.getObjValD "norms")
  let (P, items) ← decodeFacts src j
  factsModel src P j
  let E := envAt (soften src.D) (size (soften src.D))
  let premisesJson ← j.getObjVal? "premises"
  let ps ← VE.Route.Wire.decodeFormulas E premisesJson
  let conclusionJson ← j.getObjVal? "conclusion"
  let c ← VE.Route.Wire.decodeClosed E conclusionJson
  let cert ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  VE.Route.Wire.bindingOk src.se.profiles (← primeJson src.D environment)
    ((background' src.D).map enc ++ items ++ (elaborate (soften src.D).T).map enc ++ (← premisesJson.getArr?).toList)
    conclusionJson cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  pure ⟨src, P, items, ps, c, cert⟩

theorem replaySlotEntailment_parts (j : Json) (r : SlotEntailmentReplay) (h : replaySlotEntailment j = .ok r) :
    decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.src ∧
      decodeFacts r.src j = .ok (r.facts, r.items) ∧ factsModel r.src r.facts j = .ok () := by
  unfold replaySlotEntailment at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨src, hd, h⟩ := bind_ok h
  obtain ⟨⟨P, items⟩, hf, h⟩ := bind_ok h
  obtain ⟨_, hm, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  have he : j.getObjValD "environment" = env := by
    simp only [Json.getObjValD, henv]
    rfl
  exact ⟨by rw [he]; exact hd, hf, hm⟩

/-- The certificate half of the slot wire: from a successful slot replay with an accepted certificate,
the conclusion holds under the direct soft semantics with the soft premises and the facts, and, given
conflict-freedom relative to the facts and base formulas, over every coherent base satisfying the facts. -/
theorem slot_wire_acceptance (j : Json) (r : SlotEntailmentReplay) (h : replaySlotEntailment j = .ok r)
    (hv : r.valid = true) :
    decodeSoftSource (j.getObjValD "environment") (j.getObjValD "norms") = .ok r.src ∧
    (∀ S : VE.Structure.{0}, S.Admissible (envAt (soften r.src.D) (size (soften r.src.D))) → holdsSoft r.src.D S →
      VE.Norms.definitionsHold (soften r.src.D) S → VE.Norms.profileHold (soften r.src.D) S →
      Sat S (VE.Norms.backgroundBase (soften r.src.D)) → Sat S (softPremises r.src.D) → Sat S r.facts →
      Sat S r.premises → r.conclusion.denote S []) ∧
    (ConflictFreeP.{0} r.src.D r.facts →
      (∀ a ∈ r.premises, a.WellFormed (envAt (soften r.src.D) 0) []) →
        r.conclusion.WellFormed (envAt (soften r.src.D) 0) [] →
      ∀ B : VE.Structure.{0}, BaseAdmissibleP r.src.D r.facts B → Sat B r.premises → r.conclusion.denote B []) := by
  obtain ⟨hd, hf, _⟩ := replaySlotEntailment_parts j r h
  have hP := (decodeFacts_ok hf).1
  refine ⟨hd, fun S hS hs hdf hp hb hsp hslot hΓ => ?_, fun hc hΓ hφ => ?_⟩
  · exact slot_route_intended r.src.D r.src.wf r.facts r.premises r.conclusion r.cert hv S hS hs hdf hp hb hsp hslot hΓ
  · exact (slot_route_acceptance r.src.D r.src.wf r.facts hP hc r.premises r.conclusion r.cert hv).2 hΓ hφ

/-- The facts of a slot certificate replay are the request's, and, when there are any, they hold together
with `Background_base′` in some base structure: an accepted certificate is not vacuous in them. -/
theorem slot_wire_entailment_facts (j : Json) (r : SlotEntailmentReplay) (h : replaySlotEntailment j = .ok r) :
    decodeFacts r.src j = .ok (r.facts, r.items) ∧
      (r.facts ≠ [] → ∃ B : VE.Structure.{0}, BaseAdmissibleP r.src.D r.facts B) := by
  obtain ⟨_, hf, hm⟩ := replaySlotEntailment_parts j r h
  exact ⟨hf, factsModel_sat hm⟩

/-! ## No facts: each slot replay is its soft twin -/

theorem map_bind_congr {ε α β γ δ : Type} (x : Except ε α) {f : α → Except ε β} {g : α → Except ε γ}
    {p : β → δ} {q : γ → δ} (h : ∀ a, (f a).map p = (g a).map q) : (x >>= f).map p = (x >>= g).map q := by
  cases x with
  | error e => rfl
  | ok a => exact h a

theorem ok_bind {ε α β : Type} (a : α) (f : α → Except ε β) : (Except.ok a >>= f) = f a := rfl

theorem decodeSlotPackage_nil (src : SoftSource) (environment norms packages : Json) :
    decodeSlotPackage src environment norms packages [] = decodeSoftPackage src environment norms packages := by
  funext t
  unfold decodeSlotPackage decodeSoftPackage
  rw [List.append_nil]
  rfl

theorem slotWitnessFrom_nil (src : SoftSource) (w : Json) :
    (slotWitnessFrom src [] w).map (fun d => (d.M, d.target, d.tuple, d.conflict)) =
      (softWitnessFrom src w).map (fun d => (d.M, d.target, d.tuple, d.conflict)) := by
  unfold slotWitnessFrom
  cases softWitnessFrom src w with
  | error e => rfl
  | ok sw => rfl

/-- With `facts` absent or empty, each slot replay succeeds exactly when its soft twin does, with the same
source, certificates (or witness) and validity, and no facts: no existing answer can change. -/
theorem slot_wire_empty (j : Json) (h : NoFacts j) :
    (replaySlotConflict j).map (fun r => (r.src, r.facts, r.certs, r.conflictFree)) =
      (replaySoftConflict j).map (fun r => (r.src, ([] : List VE.Formula), r.certs, r.conflictFree)) ∧
    (replaySlotWitness j).map (fun r => (r.src, r.facts, r.w.M, r.w.target, r.w.tuple, r.w.conflict)) =
      (replaySoftWitness j).map (fun r => (r.1, ([] : List VE.Formula), r.2.M, r.2.target, r.2.tuple, r.2.conflict)) ∧
    (replaySlotEntailment j).map (fun r => (r.src, r.facts, r.premises, r.conclusion, r.cert, r.valid)) =
      (replaySoftEntailment j).map (fun r => (r.src, ([] : List VE.Formula), r.premises, r.conclusion, r.cert, r.valid)) := by
  refine ⟨?_, ?_, ?_⟩
  · unfold replaySlotConflict replaySoftConflict
    refine map_bind_congr _ fun env => map_bind_congr _ fun src => ?_
    simp only [decodeFacts_empty src h, ok_bind, factsModel_nil]
    simp only [Except.map, pure, Except.pure, decodeSlotPackage_nil, SlotConflictReplay.conflictFree, slot_empty_check,
      VE.SoftNorms.Wire.SoftConflictReplay.conflictFree]
  · unfold replaySlotWitness replaySoftWitness
    refine map_bind_congr _ fun env => map_bind_congr _ fun src => ?_
    simp only [decodeFacts_empty src h, ok_bind]
    refine map_bind_congr _ fun w => ?_
    have := slotWitnessFrom_nil src w
    revert this
    cases slotWitnessFrom src [] w <;> cases softWitnessFrom src w <;>
      simp_all [Except.map, bind, Except.bind, pure, Except.pure]
  · unfold replaySlotEntailment replaySoftEntailment
    refine map_bind_congr _ fun env => map_bind_congr _ fun src => ?_
    simp only [decodeFacts_empty src h, ok_bind, factsModel_nil]
    refine map_bind_congr _ fun pj => map_bind_congr _ fun ps => map_bind_congr _ fun cj => map_bind_congr _ fun c => ?_
    refine map_bind_congr _ fun cj' => map_bind_congr _ fun cert => map_bind_congr _ fun pe => map_bind_congr _ fun arr => ?_
    simp only [List.append_nil, List.map_append]
    refine map_bind_congr _ fun _ => ?_
    simp only [Except.map, pure, Except.pure, SlotEntailmentReplay.valid, VE.SoftNorms.Wire.SoftEntailmentReplay.valid,
      (slot_empty_background src.D).1]

end VE.Compose.SlotWire
