import VE.Discourse.Resolve

/-! # Well-formedness `WellFormedDiscourse` (docs/spec/discourse.md 4.1) and the theorems
that rely on it (9.2, 9.3)

`wellFormed` runs the manifest-level checks of 4.1 in order, each returning the diagnostic
text of section 8: the anchor tree (2), names, content names and documents (3), mentions
(4, 5), the bound units (6: every unit with a formula-producing mention validates, which
includes accessibility, typing, uniqueness and slot correspondence), groups and
constraints (7), the joint set (8) and the limits (11). The envelope and profile checks
(1), and the decoding and identity of embedded and imported documents (10), run in the
wrapper (`Admission.lean`). Definition/proof dependencies (9) are W3's, unchanged. -/
namespace VE.Discourse
open VE.English (Tok)
open VE.Route.Admission (ReadingSet DocUnit)
universe u

def req (b : Bool) (e : String) : Except String Unit := if b then .ok () else .error e

/-- Run the stages in order; the first failure is the diagnostic. -/
def runAll : List (Unit → Except String Unit) → Except String Unit
  | [] => .ok ()
  | f :: fs => match f () with
    | .ok _ => runAll fs
    | .error e => .error e

theorem runAll_ok : ∀ (fs : List (Unit → Except String Unit)), runAll fs = .ok () → ∀ f ∈ fs, f () = .ok ()
  | [], _, _, hf => nomatch hf
  | g :: gs, h, f, hf => by
    unfold runAll at h
    split at h
    · rename_i hg
      rcases List.mem_cons.mp hf with rfl | hf
      · exact hg
      · exact runAll_ok gs h f hf
    · cases h

def allOk {α : Type} (xs : List α) (f : α → Except String Unit) : Except String Unit :=
  runAll (xs.map fun x _ => f x)

theorem allOk_ok {α : Type} (xs : List α) (f : α → Except String Unit) (h : allOk xs f = .ok ()) :
    ∀ x ∈ xs, f x = .ok () := by
  intro x hx
  exact runAll_ok _ h _ (List.mem_map.mpr ⟨x, hx, rfl⟩)

def spanIn (inner outer : Nat × Nat) : Bool := outer.1 ≤ inner.1 && inner.2 ≤ outer.2
def spansDisjoint (a b : Nat × Nat) : Bool := a.2 ≤ b.1 || b.2 ≤ a.1
def spansNested (a b : Nat × Nat) : Bool := a != b && (spanIn a b || spanIn b a)

def firstDup (xs : List String) : Option String :=
  (xs.zipIdx.find? fun (x, i) => (xs.take i).contains x).map Prod.fst

/-- The anchor reaches the root through parents within the fuel. -/
def reachesRoot (D : DDoc) : Nat → Anchor → Bool
  | 0, _ => false
  | n + 1, a => match a.parent with
    | none => true
    | some p => match anchorOf D p with
      | some b => spanIn a.span b.span && reachesRoot D n b
      | none => false

def definitionIn (D : DDoc) (a : Anchor) : Bool :=
  D.base.units.any fun x => decide (x.kind = .definition) && spanIn (x.start, x.stop) a.span

/-- 4.1(2): one tree, nested and non-overlapping spans, unique labels per parent, exports. -/
def anchorsOk (D : DDoc) : Except String Unit := runAll [
  fun _ => req (D.K.anchors.length ≤ 1024) "ResourceLimit: anchors",
  fun _ => match firstDup (D.K.anchors.map Anchor.id) with
    | some a => .error ("DuplicateDeclaration: anchor " ++ a)
    | none => .ok (),
  fun _ => req ((D.K.anchors.filter (·.parent.isNone)).length == 1 || D.K.anchors.isEmpty)
    "InvalidInput: anchors must form one tree",
  fun _ => allOk D.K.anchors fun a => req (reachesRoot D (D.K.anchors.length + 1) a)
    ("DanglingAnchor: " ++ ((a.parent).getD a.id)),
  fun _ => allOk D.K.anchors fun a => allOk D.K.anchors fun b =>
    if a.id != b.id && a.parent == b.parent && a.parent.isSome then
      if a.label.toLower == b.label.toLower then .error ("DuplicateAnchor: " ++ a.label)
      else req (spansDisjoint a.span b.span) ("InvalidInput: anchors " ++ a.id ++ ", " ++ b.id ++ " overlap")
    else .ok (),
  fun _ => allOk D.K.anchors fun a => req (a.exports.all fun p => unaryPred D.E p && definitionIn D a)
    ("ManifestMismatch: anchors." ++ a.id ++ ".exports")]

def scopesOverlap (D : DDoc) (a b : String) : Bool :=
  match anchorOf D a, anchorOf D b with
  | some x, some y => !spansDisjoint x.span y.span
  | _, _ => true

def unitIdsOf (D : DDoc) : List String := D.base.units.map DocUnit.id

/-- 4.1(3): names, content names, documents and imports. -/
def tablesOk (D : DDoc) : Except String Unit := runAll [
  fun _ => req (D.K.names.length ≤ 1024) "ResourceLimit: names",
  fun _ => allOk D.K.names fun n =>
    if !(notBinder n.constant && (D.E.constants n.constant).isSome) then
      .error ("InvalidInput: name " ++ n.constant ++ " is not a declared constant")
    else req (anchorOf D n.scope).isSome ("DanglingAnchor: " ++ n.scope),
  fun _ => match firstDup (D.K.names.map Name.constant) with
    | some c => .error ("DuplicateDeclaration: name " ++ c)
    | none => .ok (),
  fun _ => allOk D.K.names fun n => allOk D.K.names fun n' =>
    if n.constant != n'.constant && n.display.toLower == n'.display.toLower && scopesOverlap D n.scope n'.scope then
      .error ("DuplicateDeclaration: name " ++ n.display) else .ok (),
  fun _ => allOk D.K.contentNames fun c => req (c.units.all (unitIdsOf D).contains && (anchorOf D c.scope).isSome)
    ("InvalidInput: content name " ++ c.name),
  fun _ => allOk D.K.contentNames fun c => allOk D.K.contentNames fun c' =>
    if c.units != c'.units && c.name.toLower == c'.name.toLower && scopesOverlap D c.scope c'.scope then
      .error ("DuplicateDeclaration: content_name " ++ c.name) else .ok (),
  fun _ => req (D.K.documents.length ≤ 64 && D.K.imports.length ≤ 64) "ResourceLimit: documents",
  fun _ => req (D.K.documents.isEmpty || D.E.sorts.contains D.K.documentSort)
    ("InvalidInput: document sort " ++ D.K.documentSort ++ " is not declared"),
  fun _ => match firstDup (D.K.documents.map DocName.name) with
    | some d => .error ("DuplicateDeclaration: document " ++ d)
    | none => .ok (),
  fun _ => allOk D.K.documents fun d =>
    if D.E.constants d.name != some D.K.documentSort then
      .error ("InvalidInput: document " ++ d.name ++ " is not a constant of the document sort")
    else match d.refers with
      | .self => req (d.sourceId.isNone && d.documentId.isNone) ("InvalidInput: document " ++ d.name ++ " pins")
      | .part a => req ((anchorOf D a).isSome && d.sourceId.isNone && d.documentId.isNone) ("DanglingAnchor: " ++ a)
      | .embedded u => req (D.base.units.any fun x => x.id == u && decide (x.kind = .«meta»))
          ("UnknownDocument: " ++ d.name)
      | .imported k => req (D.K.imports.any (·.key == k) && d.sourceId.isSome && d.documentId.isSome)
          ("UnknownDocument: " ++ d.name)]

def mentionUnitLength (D : DDoc) (x : Mention) : Option Nat := (D.text x.unit).map List.length

/-- The sort the restriction's context `[σ]` names. -/
def restrictionSort (D : DDoc) (m : Mention) : Option String :=
  match m.restriction with
  | some (.unary q _) => match D.E.predicates q with
    | some [s] => some s
    | _ => none
  | some (.binary q _ _) => match D.E.predicates q with
    | some [s, _] => some s
    | _ => none
  | _ => none

def targetShapeOk (x : Mention) : Bool :=
  let t := x.target
  (x.form != .plural || (decide (2 ≤ t.members.length) && decide t.members.Nodup)) &&
  (x.form != .ordinalPair || match t.pair, t.name with
    | some p, some c => c == p.1 || c == p.2
    | _, _ => false)

/-- 4.1(4, 5): mentions, their spans, target shapes, kind fit, restrictions and carriers. -/
def mentionsOk (D : DDoc) : Except String Unit := runAll [
  fun _ => req (D.K.mentions.length ≤ mentionLimit) "ResourceLimit: mentions",
  fun _ => match firstDup (D.K.mentions.map Mention.id) with
    | some m => .error ("DuplicateDeclaration: mention " ++ m)
    | none => .ok (),
  fun _ => allOk D.K.mentions fun x =>
    req ((unitIdsOf D).contains x.unit && decide (x.span.1 < x.span.2) &&
      (match mentionUnitLength D x with
       | some n => decide (x.span.2 ≤ n)
       | none => !formulaForm x.form)) ("InvalidInput: mention " ++ x.id ++ " span"),
  fun _ => allOk D.K.mentions fun x => allOk D.K.mentions fun y =>
    if x.id != y.id && x.unit == y.unit && !spansDisjoint x.span y.span && !spansNested x.span y.span then
      .error ("InvalidInput: mentions " ++ x.id ++ ", " ++ y.id ++ " overlap") else .ok (),
  fun _ => allOk D.K.mentions fun x => req (targetShapeOk x) ("InvalidInput: mention " ++ x.id ++ " target"),
  fun _ => allOk D.K.mentions fun x => req (formFits x.form x.target.kind)
    ("TargetKindMismatch: " ++ x.id ++ ": " ++ reprStr x.form ++ ", " ++ reprStr x.target.kind),
  fun _ => allOk D.K.mentions fun x =>
    if x.form == .definite then
      match x.restriction, x.reading, restrictionSort D x with
      | some Dr, some .presuppositional, some σ => match x.presuppositionUnit with
        | some u => req (decide (VE.Route.Admission.AssertedUnit D.base u (uniqueD σ Dr)))
            ("ManifestMismatch: mentions." ++ x.id ++ ".presupposition_unit")
        | none => .ok ()
      | some _, some .assertive, some _ => .ok ()
      | _, _, _ => .error ("InvalidInput: restriction of " ++ x.id)
    else .ok ()]

/-- The units carrying a formula-producing mention: each is elaborated on its own. -/
def boundUnits (D : DDoc) : List String :=
  (D.K.mentions.filter fun x => formulaForm x.form).map Mention.unit

/-- 4.1(6): every bound unit validates. -/
def boundOk (D : DDoc) : Except String Unit :=
  allOk (boundUnits D) fun u => match validate D u with
    | .ok _ => .ok ()
    | .error e => .error e

def activeSets (D : DDoc) : List ReadingSet :=
  D.base.readingSets.filter fun rs => !D.base.readingSets.any fun o => o.id == rs.id && o.version > rs.version

/-- The owning set's reading, regenerated per group. -/
def groupFormula (D : DDoc) (g : Group) : Option VE.Formula :=
  (D.base.readingSets.find? fun rs => rs.id == g.set && rs.version == g.version).bind fun rs => rs.readings[g.reading]?

def owningUnit (_D : DDoc) (g : Group) : Option String := g.spans.head?

def groupedUnits (D : DDoc) : List String := D.K.groups.flatMap Group.spans

def contentOf (D : DDoc) (u : String) : Option VE.Formula := (unitOf D.base u).bind DocUnit.content

/-- 4.1(7): groups and constraints. -/
def groupsOk (D : DDoc) : Except String Unit := runAll [
  fun _ => req (D.K.groups.length ≤ 256 && D.K.groups.all (fun g => decide (g.spans.length ≤ 16)) &&
    D.K.constraints.length ≤ 1024) "ResourceLimit: groups",
  fun _ => allOk D.K.groups fun g =>
    match groupFormula D g with
    | none => .error ("InvalidInput: reading " ++ toString g.reading ++ " not in " ++ g.set ++ "@" ++ toString g.version)
    | some φ =>
      if g.spans.isEmpty then .error ("InvalidInput: group " ++ g.set ++ " has no spans") else
      match g.spans.find? (fun u => (contentOf D u).isSome || (boundUnits D).contains u || !(unitIdsOf D).contains u) with
      | some u => .error ("IndependentFragment: " ++ u)
      | none => req (sharedWitness φ)
          ("WitnessSplit: " ++ g.set ++ "@" ++ toString g.version ++ ":" ++ toString g.reading),
  fun _ => allOk D.K.constraints fun k => req ([k.a, k.b].all fun (s, v, i) =>
      (activeSets D).any fun rs => rs.id == s && rs.version == v && decide (i < rs.readings.length))
    ("InvalidInput: constraint names an inactive reading")]

/-- 4.1(8): the joint set, validated to completion and nonempty, or UNKNOWN (not a rejection). -/
def jointOk (D : DDoc) : Except String Unit :=
  match compatibleChoices D.K (activeSets D) 64 with
  | .ok _ => .ok ()
  | .error e => if e.startsWith "ResourceLimit" then .ok () else .error e

/-- Validity bindings and self-truth labels (4.7): `meta` units without content. -/
def labelsOk (D : DDoc) : Except String Unit := runAll [
  fun _ => allOk D.K.validity fun v =>
    if !(D.base.units.any fun x => x.id == v.unit && decide (x.kind = .«meta») && x.content.isNone) then
      .error ("InvalidInput: validity unit " ++ v.unit)
    else if D.K.selfTruth.contains v.unit then .error ("InvalidInput: " ++ v.unit ++ " is a self-truth sentence")
    else match D.K.documents.find? (·.name == v.document) with
      | none => .error ("UnknownDocument: " ++ v.document)
      | some d => match d.refers with
        | .part _ => .error ("UnsupportedTarget: " ++ v.unit ++ ": part")
        | _ => .ok (),
  fun _ => allOk D.K.selfTruth fun u =>
    req (D.base.units.any fun x => x.id == u && decide (x.kind = .«meta») && x.content.isNone)
      ("InvalidInput: self-truth unit " ++ u)]

/-- 4.1 in order; every check returns the diagnostic text of section 8. -/
def wellFormed (D : DDoc) : Except String Unit :=
  runAll [fun _ => anchorsOk D, fun _ => tablesOk D, fun _ => mentionsOk D, fun _ => boundOk D,
    fun _ => groupsOk D, fun _ => jointOk D, fun _ => labelsOk D]

def WellFormedDiscourse (D : DDoc) : Bool := (wellFormed D).toBool

theorem wellFormed_of (D : DDoc) (h : WellFormedDiscourse D = true) : wellFormed D = .ok () := by
  unfold WellFormedDiscourse at h
  cases hw : wellFormed D with
  | ok v => rfl
  | error e => rw [hw] at h; cases h

theorem wf_bound (D : DDoc) (h : WellFormedDiscourse D = true) (x : Mention) (hx : x ∈ D.K.mentions)
    (hf : formulaForm x.form = true) : ∃ A, validate D x.unit = .ok A := by
  have hb := runAll_ok _ (wellFormed_of D h) (fun _ => boundOk D) (by simp)
  have hu : x.unit ∈ boundUnits D := by
    unfold boundUnits
    exact List.mem_map.mpr ⟨x, List.mem_filter.mpr ⟨hx, hf⟩, rfl⟩
  have := allOk_ok _ _ hb x.unit hu
  split at this
  · rename_i A hA; exact ⟨A, hA⟩
  · cases this

/-! ## The theorems of 9.2 and 9.3 over well-formed documents -/

/-- The validator is sound: whatever it returns is the unique accepted resolution of that unit's text. -/
theorem validate_sound (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (A : VE.Formula)
    (s : List Tok) (hs : D.text u = some s) (hv : validate D u = .ok A) : Accepted D u s A :=
  validate_accepted D u A s hs hv

/-- Slot correspondence: the recorded formula-producing mentions of the unit are the accepted
derivation's slots. -/
theorem validate_slots_recorded (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (A : VE.Formula)
    (s : List Tok) (hs : D.text u = some s) (hv : validate D u = .ok A) :
    ∃ d σ, Derives D u s d ∧ (∀ m ∈ d.slots, recordedTarget D m = some (σ m)) ∧ elaborateD D d σ = some A ∧
      recordedSlots D u = d.slots :=
  validate_recorded D u A s hs hv

theorem derives_units {D : DDoc} {u : String} {s : List Tok} {d : DTree} (hd : Derives D u s d) :
    ∀ m ∈ d.slots, m.unit = u ∧ formulaForm m.form = true := by
  obtain ⟨hs, j, hj, _⟩ := hd
  rw [hs]
  intro m hm
  have hnp : ∀ (i e : Nat) (np : NP), npEnd D u s i np = some e → ∀ m ∈ npSlots np, m.unit = u ∧ formulaForm m.form = true := by
    intro i e np h m hm
    cases np with
    | name => simp [npSlots] at hm
    | slot x =>
      simp only [npSlots, List.mem_singleton] at hm
      subst hm
      simp only [npEnd] at h
      split at h
      · rename_i hc
        simp only [Bool.and_eq_true, beq_iff_eq] at hc
        refine ⟨hc.1.1.1, ?_⟩
        have hsf := hc.1.2
        revert hsf
        cases m.form <;> simp [simpleForm, formulaForm]
      · cases h
    | definite x r =>
      cases r with
      | noun p =>
        simp only [npSlots, List.mem_singleton] at hm
        subst hm
        simp only [npEnd] at h
        split at h
        · rename_i hc
          simp only [Bool.and_eq_true, beq_iff_eq] at hc
          rw [hc.1.1.1]; simp [formulaForm]
        · cases h
      | rel p q =>
        simp only [npSlots, List.mem_cons, List.not_mem_nil, or_false] at hm
        simp only [npEnd] at h
        split at h
        · rename_i hc
          simp only [Bool.and_eq_true, beq_iff_eq] at hc
          rcases hm with rfl | rfl
          · rw [hc.1.1.1]; simp [formulaForm]
          · rw [hc.1.1.2]; simp [formulaForm]
        · cases h
  have hmod : ∀ (i e : Nat) (md : Mod), modEnd D u s i md = some e → ∀ m ∈ modSlots md, m.unit = u ∧ formulaForm m.form = true := by
    intro i e md h m hm
    cases md with
    | slot x =>
      simp only [modSlots, List.mem_singleton] at hm
      subst hm
      simp only [modEnd] at h
      split at h
      · rename_i hc
        simp only [Bool.and_eq_true, beq_iff_eq] at hc
        rw [hc.1]; simp [formulaForm]
      · cases h
    | _ => simp [modSlots] at hm
  have hcore : ∀ (i e : Nat) (c : Core), coreEnd D u s i c = some e → ∀ m ∈ coreSlots c, m.unit = u ∧ formulaForm m.form = true := by
    intro i e c h m hm
    cases c with
    | pred subj are p =>
      simp only [coreEnd] at h
      split at h
      · rename_i j hj; exact hnp i j subj hj m hm
      · cases h
    | coord => simp [coreSlots] at hm
    | rel subj p obj =>
      simp only [coreEnd] at h
      split at h
      · rename_i j hj
        split at h
        · rcases List.mem_append.mp hm with hm | hm
          · exact hnp i j subj hj m hm
          · exact hnp (j + 1) e obj h m hm
        · cases h
      · cases h
    | every md srt p =>
      simp only [coreEnd] at h
      split at h
      · split at h
        · rename_i j hj; exact hmod (i + 1) j md hj m hm
        · cases h
      · cases h
    | some an md srt p =>
      simp only [coreEnd] at h
      split at h
      · split at h
        · rename_i j hj; exact hmod (i + 1) j md hj m hm
        · cases h
      · cases h
    | everyDef x srt p sec =>
      simp only [coreEnd] at h
      split at h
      · rename_i hc
        simp only [Bool.and_eq_true, beq_iff_eq] at hc
        simp only [coreSlots, List.mem_singleton] at hm
        subst hm
        rw [hc.2]; simp [formulaForm]
      · cases h
  cases ht : d.tree with
  | core c =>
    rw [ht] at hj hm
    exact hcore 0 j c hj m hm
  | cite x c =>
    rw [ht] at hj hm
    simp only [treeEnd] at hj
    split at hj
    · rename_i hc
      simp only [Bool.and_eq_true, beq_iff_eq] at hc
      rcases List.mem_cons.mp hm with rfl | hm
      · rw [hc.1.1.1.2]; simp [formulaForm]
      · exact hcore 4 j c hj m hm
    · cases hj

theorem recordedSlots_nil {D : DDoc} {u : String} (h : recordedSlots D u = []) :
    ∀ x ∈ D.K.mentions, x.unit = u → formulaForm x.form = false := by
  intro x hx hu
  have hl := List.length_mergeSort (le := slotBefore)
    ((D.K.mentions.filter fun x => x.unit == u && formulaForm x.form).map fun x => (⟨x.unit, x.span, x.form⟩ : Slot))
  unfold recordedSlots at h
  rw [h] at hl
  simp only [List.length_nil, List.length_map] at hl
  have hn := List.length_eq_zero_iff.mp hl.symm
  cases hf : formulaForm x.form
  · rfl
  · have hmem : x ∈ D.K.mentions.filter (fun x => x.unit == u && formulaForm x.form) :=
      List.mem_filter.mpr ⟨hx, by simp [hu, hf]⟩
    rw [hn] at hmem
    cases hmem

theorem recordedTarget_none {D : DDoc} {u : String} (h : recordedSlots D u = []) (m : Slot) (hu : m.unit = u)
    (hf : formulaForm m.form = true) : recordedTarget D m = none := by
  unfold recordedTarget mentionAt
  cases hx : D.K.mentions.find? (fun x => x.unit == m.unit && x.span == m.span && x.form == m.form) with
  | none => rfl
  | some x =>
    have hm := List.mem_of_find?_eq_some hx
    have hp := List.find?_some hx
    simp only [Bool.and_eq_true, beq_iff_eq] at hp
    have := recordedSlots_nil h x hm (by rw [hp.1.1, hu])
    rw [hp.2, hf] at this
    cases this

theorem vectors_acc (D : DDoc) : ∀ (slots : List Slot) (vec : List Target),
    vec ∈ vectors (slots.map (accCands D)) → ∀ m ∈ slots, Acc D m (assignOf slots vec m)
  | [], _, _, m, hm => nomatch hm
  | x :: xs, vec, hv, m, hm => by
    simp only [List.map_cons, vectors, List.mem_flatMap, List.mem_map] at hv
    obtain ⟨t, ht, vs, hvs, rfl⟩ := hv
    by_cases hxm : x = m
    · subst hxm
      rw [assignOf_cons_self]
      exact (List.mem_filter.mp ht).2
    · rw [assignOf_cons_ne x m t xs vs hxm]
      rcases List.mem_cons.mp hm with h | h
      · exact absurd h.symm hxm
      · exact vectors_acc D xs vs hvs m h

theorem slots_of_derivs (D : DDoc) (u : String) (s : List Tok) (d : DTree) (h : d ∈ derivs D u s) :
    d.slots = slotsOf d.tree := ((mem_derivs D u s d).mp h).1

theorem definiteRestrs_nil {t : STree} (h : slotsOf t = []) : definiteRestrs t = [] := by
  unfold definiteRestrs
  split
  · simp [slotsOf, coreSlots, npSlots] at h
    revert h; rename_i r _ _; cases r <;> simp [npSlots]
  · simp [slotsOf] at h
  · rfl

theorem elaborate_tree {D : DDoc} {d d' : DTree} (h : d'.tree = d.tree) (σ : Assignment) :
    elaborateD D d' σ = elaborateD D d σ := by
  unfold elaborateD; rw [h]

/-- Complete on the supported fragment within fuel. -/
theorem validate_complete (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (s : List Tok)
    (hs : D.text u = some s) (hsup : Supported D u s) (A : VE.Formula) (hA : Accepted D u s A) :
    validate D u = .ok A := by
  by_cases hb : recordedSlots D u = []
  · -- no recorded formula-producing mention at `u`: the validator's steps succeed on `hA`
    obtain ⟨d, σ, hd, hr, he, hck, hall⟩ := hA
    have hnil : d.slots = [] := by
      cases hsl : d.slots with
      | nil => rfl
      | cons m ms =>
        have hm : m ∈ d.slots := by rw [hsl]; exact List.mem_cons_self
        obtain ⟨hu, hf⟩ := derives_units hd m hm
        have := (hr m hm).2
        rw [recordedTarget_none hb m hu hf] at this
        cases this
    have hill : (derivs D u s).find? (illTypedOf D) = none := by
      apply List.find?_eq_none.mpr
      intro d' hd' hi
      simp only [illTypedOf, Bool.and_eq_true, Bool.not_eq_true'] at hi
      obtain ⟨hne, hi⟩ := hi
      cases hsl : d'.slots with
      | nil => rw [hsl] at hne; cases hne
      | cons m ms =>
        split at hi
        · rename_i vec hvec
          obtain ⟨_, hrec⟩ := mapM_recorded D d'.slots vec hvec
          have hm : m ∈ d'.slots := by rw [hsl]; exact List.mem_cons_self
          obtain ⟨hu, hf⟩ := derives_units ((mem_derivs D u s d').mp hd') m hm
          have := hrec m hm
          rw [recordedTarget_none hb m hu hf] at this
          cases this
        · cases hi
    have hd0 : d ∈ derivs D u s := (mem_derivs D u s d).mpr hd
    have hcomp : (d, ([] : List Target), A) ∈ typedComps D (derivs D u s) := by
      refine (mem_typedComps D _ _ _ _).mpr ⟨hd0, by simp [hnil, vectors], ?_, hck⟩
      rw [elaborate_congr D d _ σ (fun m hm => by rw [← hd.1, hnil] at hm; cases hm)]
      exact he
    have hcomps : ∀ x ∈ typedComps D (derivs D u s), x.1.tree = d.tree ∧ x.1.slots = [] ∧
        elaborateD D x.1 (assignOf x.1.slots x.2.1) = some A := by
      intro x hx
      obtain ⟨d', vec', A'⟩ := x
      obtain ⟨hd', hv', he', hc'⟩ := (mem_typedComps D _ d' vec' A').mp hx
      have hder := (mem_derivs D u s d').mp hd'
      have hacc : ∀ m ∈ d'.slots, Acc D m (assignOf d'.slots vec' m) := by
        intro m hm
        exact vectors_acc D d'.slots vec' hv' m hm
      obtain ⟨ht, hsl, _⟩ := hall d' (assignOf d'.slots vec') A' hder hacc he' hc'
      refine ⟨ht, by rw [hsl, hnil], ?_⟩
      simp only
      rw [elaborate_tree ht, elaborate_congr D d _ σ (fun m hm => by rw [← hd.1, hnil] at hm; cases hm)]
      exact he
    unfold validate
    rw [if_neg (Nat.not_lt.mpr hsup.1), hs]
    dsimp only
    rw [hill, if_neg (Nat.not_lt.mpr hsup.2)]
    cases hc : typedComps D (derivs D u s) with
    | nil => rw [hc] at hcomp; cases hcomp
    | cons x rest =>
      obtain ⟨d0, vec0, A0⟩ := x
      have h0 := hcomps (d0, vec0, A0) (by rw [hc]; exact List.mem_cons_self)
      simp only at h0
      obtain ⟨ht0, hs0, he0⟩ := h0
      have hrest : rest.find? (fun x => !aligned D d0 x.1 vec0 x.2.1) = none := by
        apply List.find?_eq_none.mpr
        intro x hx
        obtain ⟨htx, hsx, _⟩ := hcomps x (by rw [hc]; exact List.mem_cons_of_mem _ hx)
        simp [aligned, htx, hsx, ht0, hs0]
      simp only [hrest]
      unfold checkRecorded
      have hrv : recordedVec D d0 = some [] := by simp [recordedVec, hs0]
      have hres : restrictionMismatch D d0 (assignOf d0.slots []) = none := by
        unfold restrictionMismatch
        rw [definiteRestrs_nil (by rw [← hs0]; exact (slots_of_derivs D u s d0 (by
          have := (mem_typedComps D _ d0 vec0 A0).mp (by rw [hc]; exact List.mem_cons_self)
          exact this.1)).symm)]
        rfl
      rw [hs0] at hres he0
      have hassign : assignOf [] vec0 = assignOf [] [] := by funext m; simp [assignOf]
      rw [hassign] at he0
      simp only [hrv, hs0, List.zip_nil_left, List.all_nil, Bool.not_true, Bool.false_eq_true, if_false,
        aligned, beq_self_eq_true, Bool.and_self, hb, bne_self_eq_false, hres, he0, hck, if_true]
  · -- a recorded formula-producing mention at `u`: `u` is bound, so well-formedness validated it
    obtain ⟨x, hx, hxf⟩ : ∃ x ∈ D.K.mentions, x.unit = u ∧ formulaForm x.form = true := by
      unfold recordedSlots at hb
      cases hl : (D.K.mentions.filter fun x => x.unit == u && formulaForm x.form) with
      | nil => simp [hl] at hb
      | cons x xs =>
        have hm : x ∈ D.K.mentions.filter fun x => x.unit == u && formulaForm x.form := by rw [hl]; exact List.mem_cons_self
        obtain ⟨hmem, hp⟩ := List.mem_filter.mp hm
        simp only [Bool.and_eq_true, beq_iff_eq] at hp
        exact ⟨x, hmem, hp⟩
    obtain ⟨A', hA'⟩ := wf_bound D h x hx hxf.2
    rw [hxf.1] at hA'
    rw [hA', accepted_unique D u s A' A (validate_accepted D u A' s hs hA') hA]

/-! ## The intended meaning and faithfulness (9.3) -/

/-- 4.4: the intended meaning: some accepted-shape derivation and validated assignment (the
recorded, accessible, type-checking one) whose slot-by-slot meaning holds in `S`. -/
def Intended (D : DDoc) (u : String) (s : List Tok) (S : VE.Structure.{u}) : Prop :=
  ∃ d σ, Derives D u s d ∧ (∀ m ∈ d.slots, Acc D m (σ m) ∧ recordedTarget D m = some (σ m)) ∧
    (∃ A, elaborateD D d σ = some A ∧ A.check D.E [] = true) ∧ SlotMeaning D S [] d σ

/-- 4.4: the elaborated formula holds exactly when the intended meaning does, on every
admissible structure. -/
theorem elaborate_faithful (D : DDoc) (h : WellFormedDiscourse D = true) (u : String) (s : List Tok)
    (hs : D.text u = some s) (A : VE.Formula) (hv : validate D u = .ok A) (S : VE.Structure) (hS : S.Admissible D.E) :
    A.denote S [] ↔ Intended D u s S := by
  have hacc := validate_sound D h u A s hs hv
  constructor
  · intro hA
    obtain ⟨d, σ, hd, hr, he, hck, _⟩ := hacc
    exact ⟨d, σ, hd, hr, ⟨A, he, hck⟩,
      (elaborateD_capture D d σ A he S hS [] (VE.typed_empty S)).mp hA⟩
  · rintro ⟨d', σ', hd', hr', ⟨A', he', hc'⟩, hM⟩
    have hAA := accepted_no_pruning D u s A hacc d' σ' A' hd' (fun m hm => (hr' m hm).1) he' hc'
    rw [← hAA]
    exact (elaborateD_capture D d' σ' A' he' S hS [] (VE.typed_empty S)).mpr hM

/-- The symbols a formula uses: sorts of binders, predicates and constants. -/
def termSymbols : VE.Term → List String
  | .var _ => []
  | .const c => [c]

def symbolsOf : VE.Formula → List String
  | .top | .bottom => []
  | .unary p t => p :: termSymbols t
  | .binary p t w => p :: (termSymbols t ++ termSymbols w)
  | .eq t w => termSymbols t ++ termSymbols w
  | .not a => symbolsOf a
  | .and a b | .or a b | .implies a b => symbolsOf a ++ symbolsOf b
  | .all s a | .ex s a => s :: symbolsOf a

/-- A symbol declared in the environment. -/
def DeclaredSymbol (E : VE.Environment) (q : String) : Prop :=
  q ∈ E.sorts ∨ E.predicates q ≠ none ∨ E.constants q ≠ none

theorem termSymbols_declared {E : VE.Environment} {Γ : List String} {t : VE.Term} {s : String}
    (h : t.sortOf E Γ = some s) : ∀ q ∈ termSymbols t, DeclaredSymbol E q := by
  cases t with
  | var => simp [termSymbols]
  | const c =>
    simp only [termSymbols, List.mem_singleton]
    rintro q rfl
    simp only [VE.Term.sortOf] at h
    exact Or.inr (Or.inr (by rw [h]; simp))

theorem symbolsOf_declared {E : VE.Environment} : ∀ (a : VE.Formula) (Γ : List String), a.WellFormed E Γ →
    ∀ q ∈ symbolsOf a, DeclaredSymbol E q
  | .top, _, _, q, hq => nomatch hq
  | .bottom, _, _, q, hq => nomatch hq
  | .unary p t, Γ, ⟨s, hp, ht⟩, q, hq => by
    rcases List.mem_cons.mp hq with rfl | hq
    · exact Or.inr (Or.inl (by rw [hp]; simp))
    · exact termSymbols_declared ht q hq
  | .binary p t w, Γ, ⟨s, r, hp, ht, hw⟩, q, hq => by
    rcases List.mem_cons.mp hq with rfl | hq
    · exact Or.inr (Or.inl (by rw [hp]; simp))
    · rcases List.mem_append.mp hq with hq | hq
      · exact termSymbols_declared ht q hq
      · exact termSymbols_declared hw q hq
  | .eq t w, Γ, ⟨s, ht, hw⟩, q, hq => by
    rcases List.mem_append.mp hq with hq | hq
    · exact termSymbols_declared ht q hq
    · exact termSymbols_declared hw q hq
  | .not a, Γ, h, q, hq => symbolsOf_declared a Γ h q hq
  | .and a b, Γ, h, q, hq | .or a b, Γ, h, q, hq | .implies a b, Γ, h, q, hq => by
    rcases List.mem_append.mp hq with hq | hq
    · exact symbolsOf_declared a Γ h.1 q hq
    · exact symbolsOf_declared b Γ h.2 q hq
  | .all s a, Γ, h, q, hq | .ex s a, Γ, h, q, hq => by
    rcases List.mem_cons.mp hq with rfl | hq
    · exact Or.inl h.1
    · exact symbolsOf_declared a (s :: Γ) h.2 q hq

/-- No new symbols: the elaboration is well formed over `E` itself and every symbol it uses is
declared there (no witness constant, choice function or fresh predicate). -/
theorem elaborate_no_new_symbols (D : DDoc) (u : String) (A : VE.Formula) (hv : validate D u = .ok A) :
    A.WellFormed D.E [] ∧ ∀ q ∈ symbolsOf A, DeclaredSymbol D.E q := by
  have hw := (VE.check_iff_wellFormed D.E [] A).mp (validate_closed D u A hv)
  exact ⟨hw, symbolsOf_declared A [] hw⟩

end VE.Discourse
