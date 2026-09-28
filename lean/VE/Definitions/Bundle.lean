import VE.Route.Admission
import VE.Definitions.Route

/-! Lemma bundles and citation (PLAN-EXPAND2 W3), checked by the Lean route in
one run and mirrored by Python `ve/bundle.py`. A lemma lists labelled
hypotheses, the meaning ids of earlier lemmas it cites, a conclusion, its
reading-choice map, its complete transitive labelled leaves and a certificate.

Citation is not a new proof rule. A lemma's certificate is replayed by the
unchanged checker on `Background ++ own hypotheses ++ cited conclusions`; the
cited lemmas were checked earlier in the same bundle. The citing lemma must
list exactly Background's labelled leaves, its own hypotheses and every
transitive leaf of the cited lemmas (in that order, without repeats), so
stripping or changing a label is rejected. Citations must be strictly earlier
(hence the bundle is acyclic), and reading choices along a citation must agree
on every shared unit. `bundle_sound` is citation soundness by the cut pattern
of `VE.entails_cut`: every checked conclusion holds in every intended structure
in which the lemma's non-background leaves hold. -/
namespace VE.Definitions.Bundle
universe u
open Lean VE.Route

abbrev Leaf := String × VE.Formula

structure Lemma where
  name : String
  premises : List Leaf
  cites : List String
  conclusion : VE.Formula
  meaningId : String
  choices : List (String × String)
  leaves : List Leaf
  certificate : VE.Tableau.Certificate

/-- A checked lemma, as later citations see it. -/
structure Known where
  meaningId : String
  conclusion : VE.Formula
  choices : List (String × String)
  leaves : List Leaf

def lookupKnown (known : List Known) (m : String) : Option Known := known.find? (·.meaningId == m)

/-- Append the leaves not already present, in order. -/
def appendNew (xs ys : List Leaf) : List Leaf :=
  ys.foldl (fun acc y => if acc.any (fun x => decide (x = y)) then acc else acc ++ [y]) xs

/-- Merge a cited lemma's reading choices; a unit with two readings is rejected. -/
def mergeChoices (acc : List (String × String)) : List (String × String) →
    Except String (List (String × String))
  | [] => .ok acc
  | (u, r) :: cs => match VE.Bridge.lookup acc u with
    | some r' =>
      let versionPrefix := (r.splitOn ":").head! ++ ":"
      if r'.startsWith versionPrefix &&
          (r' == r || r' == versionPrefix ++ "all" || r == versionPrefix ++ "all") then
        let chosen := if r == versionPrefix ++ "all" then r' else r
        mergeChoices (acc.map fun (s, value) => if s == u then (s, chosen) else (s, value)) cs
      else .error "Citation has incompatible reading choices"
    | none => mergeChoices (acc ++ [(u, r)]) cs

/-- Reading labels carry both a set version and a branch choice. `all` may
coexist with a concrete choice at the same version. -/
def addReading (acc : List (String × String)) (l : Leaf) :
    Except String (List (String × String)) := do
  match Admission.parseLabel l.1 with
  | some (.readings set version choice) =>
    let versionPrefix := toString version ++ ":"
    let value := versionPrefix ++ (choice.map toString).getD "all"
    match VE.Bridge.lookup acc set with
    | none => pure (acc ++ [(set, value)])
    | some old =>
      unless old.startsWith versionPrefix && (old == value || old == versionPrefix ++ "all" || value == versionPrefix ++ "all") do
        throw "Citation has incompatible reading choices"
      if value == versionPrefix ++ "all" then pure acc
      else pure (acc.map fun (s, r) => if s == set then (s, value) else (s, r))
  | _ => pure acc

def leafChoices (ls : List Leaf) : Except String (List (String × String)) :=
  ls.foldlM addReading []

def choicesEqual (a b : List (String × String)) : Bool :=
  a.length == b.length && a.all (fun (u, r) => VE.Bridge.lookup b u == some r)

/-- Every reading label in the transitive leaves is mutually compatible. -/
def ReadingCompatible (ls : List Leaf) : Prop := (leafChoices ls).isOk

/-- Every reading label names the latest registered version and its formula.
`all` names the right-nested disjunction. Citation labels cannot be independent
hypotheses. -/
def leafBoundCheck (sets : List Admission.ReadingSet) (l : Leaf) : Bool :=
  match Admission.parseLabel l.1 with
  | some (.readings s v c) =>
    match sets.filter (fun rs => rs.id == s && rs.version == v) with
    | [rs] =>
      if sets.any (fun other => other.id == s && other.version > v) then false
      else match c with
        | some i => decide (rs.readings[i]? = some l.2)
        | none => decide (Admission.disjunction rs.readings = some l.2)
    | _ => false
  | some (.cite _ _) => false
  | some _ => true
  | none => false

def LeafBound (sets : List Admission.ReadingSet) (l : Leaf) : Prop :=
  leafBoundCheck sets l = true

def readingBindingOk (sets : List Admission.ReadingSet) (ls : List Leaf) : Bool :=
  ls.all fun l => leafBoundCheck sets l

def ReadingBound (sets : List Admission.ReadingSet) (ls : List Leaf) : Prop :=
  ∀ l ∈ ls, LeafBound sets l

/-- Resolve the citations in order: inherited leaves, merged choices, cited conclusions. -/
def citeAll (known : List Known) :
    List Leaf → List (String × String) → List String →
      Except String (List Leaf × List (String × String) × List VE.Formula)
  | ls, ch, [] => .ok (ls, ch, [])
  | ls, ch, m :: ms => match lookupKnown known m with
    | none => .error "Citation is absent, cyclic, or not earlier in the bundle"
    | some k => do
      let ch' ← mergeChoices ch k.choices
      let (ls', ch'', cs) ← citeAll known (appendNew ls k.leaves) ch' ms
      pure (ls', ch'', k.conclusion :: cs)

/-- Check one lemma against the lemmas before it. `bind` checks the
certificate's identity binding of the full checked list and conclusion. -/
def checkLemma (E : VE.Environment) (bg : List Leaf) (sets : List Admission.ReadingSet)
    (bind : List VE.Formula → VE.Formula → VE.Tableau.Certificate → Except String Unit)
    (known : List Known) (L : Lemma) : Except String Known := do
  let (leaves, _, cited) ← citeAll known (bg ++ L.premises) L.choices L.cites
  Gate.require (decide (L.leaves = leaves)) "Citation transitive leaf labels were changed or stripped"
  Gate.require (known.all fun k =>
    if L.cites.contains k.meaningId then
      k.leaves.all fun l => (bg.contains l || L.premises.contains l)
    else true) "Citation hypothesis is absent from the citing branch"
  let derived ← leafChoices leaves
  Gate.require (readingBindingOk sets leaves) "Reading label is not bound to its registered reading formula or citation is unresolved"
  Gate.require (choicesEqual L.choices derived) "Citation reading choices do not match transitive leaves"
  Gate.require (!known.any (·.meaningId == L.meaningId)) "Lemma meaning ID is stale or duplicated"
  let checked := bg.map Prod.snd ++ (L.premises.map Prod.snd ++ cited)
  bind checked L.conclusion L.certificate
  Gate.require (decide (VE.Route.Steps.fol L.certificate.trace ≤ VE.Route.Steps.maxSteps))
    s!"Lemma {L.name} certificate failed"
  Gate.require (VE.Tableau.checkCertificate E checked L.conclusion L.certificate)
    s!"Lemma {L.name} certificate failed"
  pure ⟨L.meaningId, L.conclusion, derived, leaves⟩

def checkAll (E : VE.Environment) (bg : List Leaf) (sets : List Admission.ReadingSet)
    (bind : List VE.Formula → VE.Formula → VE.Tableau.Certificate → Except String Unit) :
    List Known → List Lemma → Except String (List Known)
  | known, [] => .ok known
  | known, L :: Ls => do
    let k ← checkLemma E bg sets bind known L
    checkAll E bg sets bind (known ++ [k]) Ls

/-! ## Citation soundness -/

theorem mem_appendNew_left (xs ys : List Leaf) : ∀ l ∈ xs, l ∈ appendNew xs ys := by
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

theorem mem_appendNew_right (xs ys : List Leaf) : ∀ l ∈ ys, l ∈ appendNew xs ys := by
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

theorem lookupKnown_mem {known : List Known} {m : String} {k : Known}
    (h : lookupKnown known m = some k) : k ∈ known :=
  List.mem_of_find?_eq_some h

open VE.Order.ProfileGate in
theorem citeAll_sound (known : List Known) : ∀ (ms : List String) (ls : List Leaf)
    (ch : List (String × String)) (ls' : List Leaf) (ch' : List (String × String)) (cs : List VE.Formula),
    citeAll known ls ch ms = .ok (ls', ch', cs) →
      (∀ l ∈ ls, l ∈ ls') ∧ ∀ c ∈ cs, ∃ k ∈ known, k.conclusion = c ∧ ∀ l ∈ k.leaves, l ∈ ls'
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
      · exact ⟨k, lookupKnown_mem hk, rfl, fun l hl => hsub l (mem_appendNew_right _ _ l hl)⟩
      · exact hcs c hc

section Soundness
variable (E : VE.Environment) (bg : List Leaf)
  (sets : List Admission.ReadingSet)
  (bind : List VE.Formula → VE.Formula → VE.Tableau.Certificate → Except String Unit)
  (Good : VE.Structure.{u} → Prop) (hadm : ∀ S, Good S → S.Admissible E)

/-- A checked lemma's meaning: in every good structure where its leaves hold,
its conclusion holds. -/
def Sound (k : Known) : Prop :=
  ∀ S : VE.Structure.{u}, Good S → (∀ l ∈ k.leaves, l.2.denote S []) → k.conclusion.denote S []

include hadm

open VE.Order.ProfileGate in
theorem checkLemma_sound (known : List Known) (hk : ∀ k ∈ known, Sound Good k) (L : Lemma) (k : Known)
    (h : checkLemma E bg sets bind known L = .ok k) : Sound Good k := by
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
  have he := VE.Tableau.checkCertificate_sound.{u} E _ L.conclusion L.certificate (Gate.require_ok hcert)
  intro S hS hl
  apply he S (hadm S hS)
  intro a ha
  rcases List.mem_append.mp ha with ha | ha
  · obtain ⟨l, hlm, rfl⟩ := List.mem_map.mp ha
    exact hl l (hsub l (List.mem_append_left _ hlm))
  rcases List.mem_append.mp ha with ha | ha
  · obtain ⟨l, hlm, rfl⟩ := List.mem_map.mp ha
    exact hl l (hsub l (List.mem_append_right _ hlm))
  · obtain ⟨k', hk', rfl, hleaves⟩ := hcited a ha
    exact hk k' hk' S hS (fun l hm => hl l (hleaves l hm))

open VE.Order.ProfileGate in
theorem checkAll_sound : ∀ (known : List Known) (Ls : List Lemma) (res : List Known),
    (∀ k ∈ known, Sound Good k) → checkAll E bg sets bind known Ls = .ok res → ∀ k ∈ res, Sound Good k
  | known, [], res, hk, h => by
    simp only [checkAll, Except.ok.injEq] at h
    subst h; exact hk
  | known, L :: Ls, res, hk, h => by
    unfold checkAll at h
    obtain ⟨k, hL, h⟩ := bind_ok h
    have hk' := checkLemma_sound E bg sets bind Good hadm known hk L k hL
    refine checkAll_sound (known ++ [k]) Ls res (fun k₁ hm => ?_) h
    rcases List.mem_append.mp hm with hm | hm
    · exact hk k₁ hm
    · rw [List.mem_singleton.mp hm]; exact hk'

end Soundness

open VE.Order.ProfileGate in
theorem checkLemma_reading (E : VE.Environment) (bg : List Leaf) (sets : List Admission.ReadingSet)
    (bind : List VE.Formula → VE.Formula → VE.Tableau.Certificate → Except String Unit)
    (known : List Known) (L : Lemma) (k : Known)
    (h : checkLemma E bg sets bind known L = .ok k) : ReadingCompatible k.leaves := by
  unfold checkLemma at h
  obtain ⟨⟨leaves, _, _⟩, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨derived, hd, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  simp only [ReadingCompatible, hd]
  rfl

open VE.Order.ProfileGate in
theorem checkLemma_binding (E : VE.Environment) (bg : List Leaf) (sets : List Admission.ReadingSet)
    (bind : List VE.Formula → VE.Formula → VE.Tableau.Certificate → Except String Unit)
    (known : List Known) (L : Lemma) (k : Known)
    (h : checkLemma E bg sets bind known L = .ok k) : ReadingBound sets k.leaves := by
  unfold checkLemma at h
  obtain ⟨⟨leaves, _, _⟩, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, hb, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  intro l hl
  exact (List.all_eq_true.mp (Gate.require_ok hb)) l hl

open VE.Order.ProfileGate in
theorem checkAll_binding (E : VE.Environment) (bg : List Leaf) (sets : List Admission.ReadingSet)
    (bind : List VE.Formula → VE.Formula → VE.Tableau.Certificate → Except String Unit) :
    ∀ (known : List Known) (Ls : List Lemma) (res : List Known),
    (∀ k ∈ known, ReadingBound sets k.leaves) →
    checkAll E bg sets bind known Ls = .ok res → ∀ k ∈ res, ReadingBound sets k.leaves
  | known, [], res, hk, h => by
    simp only [checkAll, Except.ok.injEq] at h
    subst h; exact hk
  | known, L :: Ls, res, hk, h => by
    unfold checkAll at h
    obtain ⟨k, hL, h⟩ := bind_ok h
    have hk' := checkLemma_binding E bg sets bind known L k hL
    refine checkAll_binding E bg sets bind (known ++ [k]) Ls res (fun k₁ hm => ?_) h
    rcases List.mem_append.mp hm with hm | hm
    · exact hk k₁ hm
    · rw [List.mem_singleton.mp hm]; exact hk'

open VE.Order.ProfileGate in
theorem checkAll_reading (E : VE.Environment) (bg : List Leaf) (sets : List Admission.ReadingSet)
    (bind : List VE.Formula → VE.Formula → VE.Tableau.Certificate → Except String Unit) :
    ∀ (known : List Known) (Ls : List Lemma) (res : List Known),
    (∀ k ∈ known, ReadingCompatible k.leaves) →
    checkAll E bg sets bind known Ls = .ok res → ∀ k ∈ res, ReadingCompatible k.leaves
  | known, [], res, hk, h => by
    simp only [checkAll, Except.ok.injEq] at h
    subst h; exact hk
  | known, L :: Ls, res, hk, h => by
    unfold checkAll at h
    obtain ⟨k, hL, h⟩ := bind_ok h
    have hk' := checkLemma_reading E bg sets bind known L k hL
    refine checkAll_reading E bg sets bind (known ++ [k]) Ls res (fun k₁ hm => ?_) h
    rcases List.mem_append.mp hm with hm | hm
    · exact hk k₁ hm
    · rw [List.mem_singleton.mp hm]; exact hk'

/-- Background's labelled leaves: definitions, then literals. -/
def backgroundLeaves (ds : List Def) (lits : List String) : List Leaf :=
  (expand ds).map (fun a => ("background:definitions", a)) ++
    (Background.literals lits).map (fun a => ("background:literals", a))

theorem backgroundLeaves_hold (E : VE.Environment) (ds : List Def) (h : Chain E ds)
    (lits : List String) (hn : lits.Nodup) (S : VE.Structure.{u}) (hS : Intended E ds lits S) :
    ∀ l ∈ backgroundLeaves ds lits, l.2.denote S [] := by
  intro l hl
  rcases List.mem_append.mp hl with hl | hl
  · obtain ⟨a, ha, rfl⟩ := List.mem_map.mp hl
    exact (faithful ds (chain_arity E ds h) S).mpr hS.2 a ha
  · obtain ⟨a, ha, rfl⟩ := List.mem_map.mp hl
    exact (Background.literals_sat_iff S lits hn).mpr hS.1.2 a ha

/-- `bundle_sound`, citation soundness: every accepted lemma has compatible
reading choices and reading leaves bound to the latest registry versions.
Its conclusion is true in every intended structure (string-admissible, every
defined predicate agreeing with its body) in which its non-background
transitive leaves hold, whatever lemmas it cites. -/
theorem bundle_sound (E : VE.Environment) (ds : List Def) (h : Chain E ds)
    (lits : List String) (hn : lits.Nodup)
    (sets : List Admission.ReadingSet)
    (bind : List VE.Formula → VE.Formula → VE.Tableau.Certificate → Except String Unit)
    (Ls : List Lemma) (res : List Known)
    (accepted : checkAll E (backgroundLeaves ds lits) sets bind [] Ls = .ok res) :
    (∀ k ∈ res, ReadingCompatible k.leaves ∧ ReadingBound sets k.leaves) ∧
    ∀ k ∈ res, ∀ S : VE.Structure.{u}, Intended E ds lits S →
      (∀ l ∈ k.leaves, l ∉ backgroundLeaves ds lits → l.2.denote S []) → k.conclusion.denote S [] := by
  constructor
  · intro k hk
    exact ⟨checkAll_reading E (backgroundLeaves ds lits) sets bind [] Ls res
      (fun _ h => nomatch h) accepted k hk,
      checkAll_binding E (backgroundLeaves ds lits) sets bind [] Ls res
      (fun _ h => nomatch h) accepted k hk⟩
  intro k hk S hS hl
  have := checkAll_sound.{u} E (backgroundLeaves ds lits) sets bind (Intended E ds lits)
    (fun S hS => hS.1.1) [] Ls res (fun _ h => nomatch h) accepted k hk S hS
  apply this
  intro l hm
  by_cases hb : l ∈ backgroundLeaves ds lits
  · exact backgroundLeaves_hold E ds h lits hn S hS l hb
  · exact hl l hm hb

/-! ## Wire -/

open VE.Bridge (exactFields stringField strings) in
def decodeLeaf (E : VE.Environment) (j : Json) : Except String Leaf := do
  exactFields j ["label", "ast"]
  let label ← stringField j "label"
  unless (Admission.parseLabel label).isSome do throw s!"AdmissionError: invalid label {label}"
  pure (label, ← Wire.decodeClosed E (← j.getObjVal? "ast"))

open VE.Bridge (exactFields stringField strings fields) in
def decodeLemma (profiles : List String) (envId : String) (E : VE.Environment) (j : Json) :
    Except String Lemma := do
  exactFields j ["name", "environment_id", "premises", "cites", "conclusion", "meaning_id",
    "reading_choices", "transitive_leaves", "certificate"]
  unless (← stringField j "environment_id") == envId do
    throw "Citation has another environment or definitions version"
  let name ← stringField j "name"
  if name.isEmpty then throw "Lemma name must be nonempty"
  let premises ← (← (← j.getObjVal? "premises").getArr?).toList.mapM (decodeLeaf E)
  let cites ← strings (← j.getObjVal? "cites")
  let conclusion ← Wire.decodeClosed E (← j.getObjVal? "conclusion")
  let meaningId ← stringField j "meaning_id"
  unless meaningId == (← Wire.meaningId profiles envId (Wire.encodeFormula conclusion)) do
    throw "Lemma meaning ID is stale or duplicated"
  let choices ← (← fields (← j.getObjVal? "reading_choices")).mapM fun (u, r) => do
    pure (u, ← r.getStr?)
  let leaves ← (← (← j.getObjVal? "transitive_leaves").getArr?).toList.mapM (decodeLeaf E)
  let certificate ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  pure ⟨name, premises, cites, conclusion, meaningId, choices, leaves, certificate⟩

/-- The `bundle` case of the FOL family: decode every lemma, then check the
whole bundle in order. -/
def runBundle (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (id : String)
    (j : Json) : Except String Json := do
  let items := (← (← j.getObjVal? "lemmas").getArr?).toList
  if items.length > 256 then throw "ResourceLimit: Lemma bundle exceeds 256 lemmas"
  let envId ← Wire.environmentId profiles environment
  let E := rv.environment
  let sets ← match j.getObjVal? "document" with
    | .error _ => pure ([] : List Admission.ReadingSet)
    | .ok doc => do
      VE.Bridge.exactFields doc ["reading_sets"]
      let sets ← (← (← doc.getObjVal? "reading_sets").getArr?).toList.mapM
        (Admission.decodeReadingSet E (profiles.contains "data@0"))
      Gate.require ((sets.map (fun rs => (rs.id, rs.version))).eraseDups.length == sets.length)
        "duplicate reading set version"
      pure sets
  let lemmas ← items.mapM (decodeLemma profiles envId E)
  let names := lemmas.map Lemma.name
  unless names.eraseDups.length == names.length do throw "Duplicate lemma name"
  let bind := fun (ps : List VE.Formula) (c : VE.Formula) (cert : VE.Tableau.Certificate) =>
    Wire.bindingOk profiles environment (ps.map Wire.encodeFormula) (Wire.encodeFormula c)
      cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  let background := (Wire.fullBackground rv).map fun (formula, generator) =>
    ("background:" ++ generator, formula)
  let known ← checkAll E background sets bind [] lemmas
  pure (Wire.ok id [("checked", toJson known.length),
    ("lemmas", Json.arr (known.map (fun k => Json.str k.meaningId)).toArray)])

end VE.Definitions.Bundle
