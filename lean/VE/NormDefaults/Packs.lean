import VE.NormDefaults.Explain
import VE.Rights.Wire

/-! Premise packs (docs/spec/premise-packs.md, PK-1). The layered norm-defaults route's extra base premises `X` are the
premises of a list of packs, one per provider, in one fixed order (`packOrder`). `assemble` checks a decoded pack list
(ids, labels, generated names, prefixes, the vocabulary limit, in that fault order) and returns it in that order;
`X`, `envX`, the `"soft"` and `"rights"` elaborate arrays and `filledX`'s text are functions of the ordered packs.

Today's routes give `[soft]` and `[soft, rights]` (`Layered.lean`'s `softPack`, `rightsPack`); a plain norm-defaults
document gives the empty list (JT-R2). On those lists every output is today's (`legacyIds`, `X_legacy`,
`elaborateArrays_legacy`; the legacy theorems over `Layered.lean` are in `PacksLegacy.lean`). -/
namespace VE.NormDefaults.Packs
open Lean
open VE.Norms (envAt size)

/-! ## 2.1 The data -/

/-- 2.1: a pack adds fresh generated names, or only constrains names that already exist. -/
inductive PackKind
  | vocabulary
  | constraint
  deriving DecidableEq, Repr

/-- 2.1: object keys and array indices from the request root, as strings. -/
abbrev RequestPath := List String

/-- 2.1: what one provider regenerates from the decoded request. -/
structure Pack where
  id : String
  kind : PackKind
  decls : List (String × List String)
  consts : List (String × String)
  labelled : List (String × VE.Formula)
  origins : List (String × RequestPath)

/-- 2.2: the one order of `X`. -/
def packOrder : List String := ["soft", "rights", "weighing", "attitudes", "scales", "events"]

/-- 2.3: each reserved prefix with its owner. -/
def reservedPrefixes : List (String × String) :=
  [("soft", "soft__"), ("rights", "rights__"), ("norm-defaults", "unsaid__")]

/-- 2.3: an author name that begins with a reserved prefix. -/
def reserved (n : String) : Bool := reservedPrefixes.any (fun (_, x) => n.startsWith x)

def Pack.names (p : Pack) : List String := p.decls.map (·.1) ++ p.consts.map (·.1)

/-- 2.3: `n` begins with a prefix that `p`'s provider owns. -/
def ownPrefixIn (pre : List (String × String)) (p : Pack) (n : String) : Bool :=
  pre.any (fun (o, x) => o == p.id && n.startsWith x)

def ownPrefix : Pack → String → Bool := ownPrefixIn reservedPrefixes

/-! ## 2.4 Assembly -/

/-- The packs in `packOrder`, the first of each id. -/
def ordered (ps : List Pack) : List Pack := packOrder.filterMap (fun i => ps.find? (·.id == i))

def labelledX (qs : List Pack) : List (String × VE.Formula) := qs.flatMap (·.labelled)
def X (qs : List Pack) : List VE.Formula := (labelledX qs).map (·.2)
def names (qs : List Pack) : List String := qs.flatMap Pack.names

/-- One pack's labelled premises; `[]` when the pack is absent. -/
def packPremises (qs : List Pack) (i : String) : List (String × VE.Formula) :=
  ((qs.find? (·.id == i)).map (·.labelled)).getD []

/-- `E` with the generated predicates and constants; sorts unchanged. -/
def extendEnv (E : VE.Environment) (ds : List (String × List String)) (cs : List (String × String)) :
    VE.Environment :=
  { E with
    predicates := fun n => match ds.lookup n with | some ss => some ss | none => E.predicates n
    constants := fun n => match cs.lookup n with | some s => some s | none => E.constants n }

/-- The complete environment of the filled tree, layer symbols and `unsaid__` names included. -/
def fullEnv (U : UDoc) : VE.Environment := envAt (fill U) (size (fill U))

/-- The base environment `X` is typed over: `envAt (fill U) 0` extended by every pack's names. -/
def envX (U : UDoc) (qs : List Pack) : VE.Environment :=
  extendEnv (envAt (fill U) 0) (qs.flatMap (·.decls)) (qs.flatMap (·.consts))

/-- The first `(pack, key)` whose key is already in `seen` or earlier in the list. -/
def firstRepeat (seen : List String) : List (String × String) → Option (String × String)
  | [] => none
  | (i, n) :: rest => if seen.contains n then some (i, n) else firstRepeat (n :: seen) rest

def declaredIn (E : VE.Environment) (n : String) : Bool := (E.predicates n).isSome || (E.constants n).isSome

/-- 2.4, over a prefix table and the environment the names must be fresh in; `used` counts the vocabulary
`checkAuthorN` charged. -/
def assembleIn (pre : List (String × String)) (E : VE.Environment) (used : Nat) (ps : List Pack) :
    Except String (List Pack) := do
  if let some p := ps.find? (fun p => !packOrder.contains p.id) then
    throw s!"InvalidInput: unknown premise pack {p.id}"
  if let some i := packOrder.find? (fun i => ps.countP (·.id == i) > 1) then
    throw s!"InvalidInput: premise pack {i} is given twice"
  let qs := ordered ps
  if let some (i, l) := firstRepeat [] (qs.flatMap (fun p => p.labelled.map (fun a => (p.id, a.1)))) then
    throw s!"InvalidInput: premise label {l} of pack {i} is used twice"
  let named := qs.flatMap (fun p => p.names.map (fun n => (p.id, n)))
  if let some (i, n) := named.find? (fun (_, n) => declaredIn E n) then
    throw s!"InvalidInput: generated name {n} of pack {i} is already declared"
  if let some (i, n) := firstRepeat [] named then
    throw s!"InvalidInput: generated name {n} of pack {i} is declared twice"
  if let some p := qs.find? (fun p => !p.names.all (ownPrefixIn pre p)) then
    throw s!"InvalidInput: a generated name of pack {p.id} lacks its reserved prefix"
  if used + (names qs).length > 256 then throw "ResourceLimit: vocabulary size"
  pure qs

/-- 2.4. -/
def assemble (U : UDoc) (used : Nat) (ps : List Pack) : Except String (List Pack) :=
  assembleIn reservedPrefixes (fullEnv U) used ps

/-! ## 2.5 Theorems -/

theorem extendEnv_nil (E : VE.Environment) : extendEnv E [] [] = E := rfl

theorem envX_nil (U : UDoc) : envX U [] = envAt (fill U) 0 := rfl

/-- What a successful `assembleIn` has checked. -/
theorem assembleIn_ok {pre : List (String × String)} {E : VE.Environment} {used : Nat} {ps qs : List Pack}
    (h : assembleIn pre E used ps = .ok qs) :
    (∀ p ∈ ps, p.id ∈ packOrder) ∧ (∀ i ∈ packOrder, ps.countP (·.id == i) ≤ 1) ∧ qs = ordered ps ∧
    firstRepeat [] (qs.flatMap (fun p => p.labelled.map (fun a => (p.id, a.1)))) = none ∧
    (∀ x ∈ qs.flatMap (fun p => p.names.map (fun n => (p.id, n))), declaredIn E x.2 = false) ∧
    firstRepeat [] (qs.flatMap (fun p => p.names.map (fun n => (p.id, n)))) = none ∧
    (∀ p ∈ qs, ∀ n ∈ p.names, ownPrefixIn pre p n = true) ∧ used + (names qs).length ≤ 256 := by
  simp only [assembleIn] at h
  split at h
  · cases h
  rename_i h1
  split at h
  · cases h
  rename_i h2
  split at h
  · cases h
  rename_i h3
  split at h
  · cases h
  rename_i h4
  split at h
  · cases h
  rename_i h5
  split at h
  · cases h
  rename_i h6
  split at h
  · cases h
  rename_i h7
  cases h
  refine ⟨fun p hp => ?_, fun i hi => ?_, rfl, ?_, fun x hx => ?_, ?_, fun p hp n hn => ?_, Nat.not_lt.mp h7⟩
  · cases hf : ps.find? (fun p => !packOrder.contains p.id) with
    | some p' => exact absurd hf (h1 p')
    | none => simpa using List.find?_eq_none.mp hf p hp
  · cases hf : packOrder.find? (fun i => decide (ps.countP (·.id == i) > 1)) with
    | some _ => exact absurd hf (h2 _)
    | none =>
      have := List.find?_eq_none.mp hf i hi
      simpa using this
  · cases hr : firstRepeat [] (List.flatMap (fun p => p.labelled.map (fun a => (p.id, a.1))) (ordered ps)) with
    | none => rfl
    | some x => exact absurd hr (h3 x.1 x.2)
  · cases hf : (List.flatMap (fun p => p.names.map (fun n => (p.id, n))) (ordered ps)).find?
        (fun x => declaredIn E x.2) with
    | some y => exact absurd hf (h4 y.1 y.2)
    | none => simpa using List.find?_eq_none.mp hf x hx
  · cases hr : firstRepeat [] (List.flatMap (fun p => p.names.map (fun n => (p.id, n))) (ordered ps)) with
    | none => rfl
    | some x => exact absurd hr (h5 x.1 x.2)
  · cases hf : (ordered ps).find? (fun p => !p.names.all (ownPrefixIn pre p)) with
    | some _ => exact absurd hf (h6 _)
    | none =>
      have h' : p.names.all (ownPrefixIn pre p) = true := by simpa using List.find?_eq_none.mp hf p hp
      exact List.all_eq_true.mp h' n hn

/-- The ids of `ordered`-style lists are a sublist of the order. -/
theorem filterMap_find_ids (O : List String) (l : List Pack) :
    ((O.filterMap (fun i => l.find? (·.id == i))).map (·.id)).Sublist O := by
  induction O with
  | nil => exact List.Sublist.slnil
  | cons i O ih =>
    rw [List.filterMap_cons]
    cases hf : l.find? (·.id == i) with
    | none => exact ih.cons _
    | some p =>
      have : p.id = i := by simpa using List.find?_some hf
      rw [List.map_cons, this]
      exact ih.cons₂ _

theorem mem_filterMap_find {O : List String} {l : List Pack} {q : Pack}
    (h : q ∈ O.filterMap (fun i => l.find? (·.id == i))) : q ∈ l ∧ q.id ∈ O := by
  obtain ⟨i, hi, hf⟩ := List.mem_filterMap.mp h
  have : q.id = i := by simpa using List.find?_some hf
  exact ⟨List.mem_of_find?_eq_some hf, this ▸ hi⟩

theorem filterMap_congr {α β : Type} {f g : α → Option β} : ∀ {l : List α}, (∀ x ∈ l, f x = g x) →
    l.filterMap f = l.filterMap g
  | [], _ => rfl
  | x :: l, h => by
    rw [List.filterMap_cons, List.filterMap_cons, h x List.mem_cons_self,
      filterMap_congr (fun y hy => h y (List.mem_cons_of_mem _ hy))]

/-- A list whose ids are in `O`, each at most once, is a permutation of its `ordered`-style list. -/
theorem filterMap_find_perm (O : List String) (hO : O.Nodup) :
    ∀ l : List Pack, (∀ p ∈ l, p.id ∈ O) → (∀ i ∈ O, l.countP (·.id == i) ≤ 1) →
      (O.filterMap (fun i => l.find? (·.id == i))).Perm l := by
  induction O with
  | nil =>
    intro l hm _
    cases l with
    | nil => exact List.Perm.refl _
    | cons p _ => exact absurd (hm p List.mem_cons_self) List.not_mem_nil
  | cons i O ih =>
    intro l hm hc
    obtain ⟨hiO, hO'⟩ := List.nodup_cons.mp hO
    let l' := l.filter (·.id != i)
    have hfind : ∀ j ∈ O, l.find? (·.id == j) = l'.find? (·.id == j) := by
      intro j hj
      rw [List.find?_filter]
      congr 1
      funext a
      by_cases ha : a.id = j
      · have : j ≠ i := fun h => hiO (h ▸ hj)
        simp [ha, this]
      · simp [ha]
    have hrest : (O.filterMap (fun j => l.find? (·.id == j))).Perm l' := by
      rw [filterMap_congr hfind]
      refine ih hO' l' (fun p hp => ?_) (fun j hj => ?_)
      · obtain ⟨hp, hne⟩ := List.mem_filter.mp hp
        rcases List.mem_cons.mp (hm p hp) with h | h
        · simp [h] at hne
        · exact h
      · exact Nat.le_trans (List.Sublist.countP_le (List.filter_sublist)) (hc j (List.mem_cons_of_mem _ hj))
    cases hf : l.find? (·.id == i) with
    | none =>
      rw [List.filterMap_cons, hf]
      have : l' = l := List.filter_eq_self.mpr (fun a ha => by
        have := List.find?_eq_none.mp hf a ha
        simpa using this)
      rw [this] at hrest
      exact hrest
    | some p =>
      obtain ⟨hpi, as, bs, rfl, has⟩ := List.find?_eq_some_iff_append.mp hf
      have hpi : p.id = i := by simpa using hpi
      have hcount := hc i List.mem_cons_self
      simp only [List.countP_append, List.countP_cons, hpi, beq_self_eq_true, if_true] at hcount
      have hbs : bs.countP (·.id == i) = 0 := by omega
      have hl' : l' = as ++ bs := by
        simp only [l', List.filter_append, List.filter_cons, hpi, bne_self_eq_false]
        rw [List.filter_eq_self.mpr (fun a ha => by simpa using has a ha),
          List.filter_eq_self.mpr (fun a ha => by
            have := List.countP_eq_zero.mp hbs a ha
            simpa using this)]
        rfl
      rw [hl'] at hrest
      rw [List.filterMap_cons, hf]
      exact (hrest.cons p).trans List.perm_middle.symm

/-- The keys of a list `firstRepeat` finds no repeat in are distinct, and none is in `seen`. -/
theorem firstRepeat_none : ∀ (seen : List String) (l : List (String × String)), firstRepeat seen l = none →
    (l.map (·.2)).Nodup ∧ ∀ x ∈ l, x.2 ∉ seen
  | _, [], _ => ⟨List.nodup_nil, fun _ h => absurd h List.not_mem_nil⟩
  | seen, (i, n) :: rest, h => by
    simp only [firstRepeat] at h
    split at h
    · cases h
    rename_i hn
    obtain ⟨ih1, ih2⟩ := firstRepeat_none (n :: seen) rest h
    refine ⟨List.nodup_cons.mpr ⟨fun hm => ?_, ih1⟩, fun x hx => ?_⟩
    · obtain ⟨y, hy, he⟩ := List.mem_map.mp hm
      exact ih2 y hy (he ▸ List.mem_cons_self)
    · rcases List.mem_cons.mp hx with rfl | hx
      · simpa using hn
      · exact fun hs => ih2 x hx (List.mem_cons_of_mem _ hs)

/-- 2.5 (1). -/
theorem assemble_order {U : UDoc} {used : Nat} {ps qs : List Pack} (h : assemble U used ps = .ok qs) :
    qs = ordered ps ∧ qs.Perm ps ∧ (qs.map (·.id)).Sublist packOrder := by
  obtain ⟨hm, hc, rfl, -⟩ := assembleIn_ok h
  exact ⟨rfl, filterMap_find_perm packOrder (by decide) ps hm hc, filterMap_find_ids packOrder ps⟩

/-- 2.5 (2). -/
theorem assemble_fresh {U : UDoc} {used : Nat} {ps qs : List Pack} (h : assemble U used ps = .ok qs) :
    ((labelledX qs).map (·.1)).Nodup ∧ (names qs).Nodup ∧
    (∀ p ∈ qs, ∀ n ∈ p.names, (fullEnv U).predicates n = none ∧ (fullEnv U).constants n = none ∧
      ownPrefix p n = true) ∧
    used + (names qs).length ≤ 256 := by
  obtain ⟨-, -, -, hl, hd, hn, hp, hu⟩ := assembleIn_ok h
  have e1 : (labelledX qs).map (·.1) = (qs.flatMap (fun p => p.labelled.map (fun a => (p.id, a.1)))).map (·.2) := by
    simp [labelledX, List.map_flatMap, Function.comp_def]
  have e2 : names qs = (qs.flatMap (fun p => p.names.map (fun n => (p.id, n)))).map (·.2) := by
    simp [names, List.map_flatMap, Function.comp_def]
  refine ⟨e1 ▸ (firstRepeat_none [] _ hl).1, e2 ▸ (firstRepeat_none [] _ hn).1, fun p hpq n hnp => ?_, hu⟩
  · have := hd (p.id, n) (List.mem_flatMap.mpr ⟨p, hpq, List.mem_map.mpr ⟨n, hnp, rfl⟩⟩)
    simp only [declaredIn, Bool.or_eq_false_iff, Option.isSome_eq_false_iff, Option.isNone_iff_eq_none] at this
    exact ⟨this.1, this.2, hp p hpq n hnp⟩

/-- 2.5 (4): the empty pack list (JT-R2). -/
theorem assemble_nil (U : UDoc) (used : Nat) (hu : used ≤ 256) : assemble U used [] = .ok [] := by
  simp [assemble, assembleIn, ordered, packOrder, firstRepeat, names, Nat.not_lt.mpr hu]
  rfl

/-! ## 2.6 The legacy lists -/

/-- The pack-id lists whose outputs and texts are today's. -/
def legacyIds : List (List String) := [[], ["soft"], ["soft", "rights"]]

/-- 2.6 (6): `X` is today's `L.labelled.map (·.2)`. -/
theorem X_legacy (s r : Pack) : X [s, r] = (s.labelled ++ r.labelled).map (·.2) := by
  simp [X, labelledX]

/-- A one-pack list's `X` is that pack's premises (today's soft route). -/
theorem X_single (p : Pack) : X [p] = p.labelled.map (·.2) := by
  simp [X, labelledX]

/-- 2.6 (7): today's `"soft"` array and `filledX`'s soft prefix are the soft pack's premises. -/
theorem legacy_take (s r : List (String × VE.Formula)) :
    (s ++ r).take ((s ++ r).length - r.length) = s := by
  simp

/-- 2.6 (7): today's `"rights"` array is the rights pack's premises. -/
theorem legacy_drop (s r : List (String × VE.Formula)) :
    (s ++ r).drop ((s ++ r).length - r.length) = r := by
  simp

theorem packPremises_absent (qs : List Pack) (i : String) (h : ∀ p ∈ qs, p.id ≠ i) : packPremises qs i = [] := by
  simp only [packPremises]
  rw [List.find?_eq_none.mpr (fun p hp => by simpa using h p hp)]
  rfl

/-- One pack's premises are premises of `X`. -/
theorem packPremises_sub (qs : List Pack) (i : String) : ∀ a ∈ packPremises qs i, a ∈ labelledX qs := by
  intro a ha
  simp only [packPremises] at ha
  cases hf : qs.find? (·.id == i) with
  | none => rw [hf] at ha; cases ha
  | some p =>
    rw [hf] at ha
    exact List.mem_flatMap.mpr ⟨p, List.mem_of_find?_eq_some hf, ha⟩

/-- 2.6 (DF5): soft is first in `X`, so `X` is soft's premises, then the other packs' (`R` in defeasible's
`DefaultsView`). -/
theorem X_soft_first {U : UDoc} {used : Nat} {ps qs : List Pack} (h : assemble U used ps = .ok qs) :
    X qs = (packPremises qs "soft").map (·.2) ++ X (qs.filter (·.id != "soft")) := by
  obtain ⟨-, -, rfl, -⟩ := assembleIn_ok h
  let rest := (packOrder.tail).filterMap (fun i => ps.find? (·.id == i))
  have hrest : ∀ q ∈ rest, q.id ≠ "soft" := by
    intro q hq hs
    have := (mem_filterMap_find hq).2
    rw [hs] at this
    exact absurd this (by decide)
  have hfilter : rest.filter (·.id != "soft") = rest :=
    List.filter_eq_self.mpr (fun q hq => by simpa using hrest q hq)
  have hord : ordered ps = ((ps.find? (·.id == "soft")).toList) ++ rest := by
    simp only [ordered, packOrder, List.filterMap_cons, rest, List.tail_cons]
    cases ps.find? (·.id == "soft") <;> rfl
  rw [hord]
  cases hf : ps.find? (·.id == "soft") with
  | none =>
    simp only [Option.toList, List.nil_append, hfilter, packPremises_absent rest "soft" hrest, List.map_nil]
  | some p =>
    have hp : p.id = "soft" := by simpa using List.find?_some hf
    simp only [Option.toList, List.singleton_append, List.filter_cons, hp, bne_self_eq_false, hfilter,
      packPremises, List.find?_cons, beq_self_eq_true, Option.map_some, Option.getD_some, X, labelledX,
      List.flatMap_cons, List.map_append]
    rfl

/-! ## 2.7 Elaborate entries -/

def labelledJson (l : String) (a : VE.Formula) (origin : Option RequestPath) : Json :=
  Json.mkObj ([("label", .str l), ("ast", VE.SoftNorms.Wire.enc a)] ++
    match origin with | some o => [("origin", toJson o)] | none => [])

/-- 2.7: the `"soft"` and `"rights"` arrays as today, and nothing else, whatever the pack list: `layered_elaborate`
is closed on these two keys, and `layeredCase_fits` quantifies over every `LayeredU`. -/
def elaborateArrays (qs : List Pack) : List (String × Json) :=
  [("soft", Json.arr ((packPremises qs "soft").map (fun (l, a) => labelledJson l a none)).toArray),
   ("rights", Json.arr ((packPremises qs "rights").map (fun (l, a) => labelledJson l a none)).toArray)]

/-- 2.7: the keys pk-1's elaborate writes do not depend on the packs (the fact the encoder theorem needs). -/
theorem elaborateArrays_keys (qs : List Pack) : (elaborateArrays qs).map (·.1) = ["soft", "rights"] := rfl

/-- 2.7 (7′): on a legacy list the arrays are today's expressions over `labelled` and `rightsCount`. -/
theorem elaborateArrays_legacy (s r : Pack) (hs : s.id = "soft") (hr : r.id = "rights") :
    elaborateArrays [s, r] =
      [("soft", Json.arr (((s.labelled ++ r.labelled).take ((s.labelled ++ r.labelled).length - r.labelled.length)).map
          (fun (l, a) => Json.mkObj [("label", .str l), ("ast", VE.SoftNorms.Wire.enc a)])).toArray),
       ("rights", Json.arr (((s.labelled ++ r.labelled).drop ((s.labelled ++ r.labelled).length - r.labelled.length)).map
          (fun (l, a) => Json.mkObj [("label", .str l), ("ast", VE.SoftNorms.Wire.enc a)])).toArray)] := by
  rw [legacy_take, legacy_drop]
  simp [elaborateArrays, packPremises, labelledJson, hs, hr]

/-! ## 2.8 Diagnostics -/

/-- The first premise of `X`, in `X` order, that `holds` rejects, with its pack id and label. -/
def firstFailing (qs : List Pack) (holds : VE.Formula → Bool) : Option (String × String) :=
  (qs.flatMap (fun p => p.labelled.map (fun a => (p.id, a)))).findSome? fun (i, l, a) =>
    if holds a then none else some (i, l)

/-- 2.8: `filledX`'s text when `X` fails: today's for a legacy list, pack and label otherwise. -/
def packFault (qs : List Pack) (holds : VE.Formula → Bool) : String :=
  match firstFailing qs holds with
  | some (i, l) =>
    if legacyIds.contains (qs.map (·.id)) then VE.Route.Wire.invalidModel i
    else VE.Route.Wire.invalidModel i ++ ": " ++ l
  | none => VE.Route.Wire.invalidModel "premises"

theorem firstFailing_some (qs : List Pack) (holds : VE.Formula → Bool) (h : (X qs).all holds = false) :
    (firstFailing qs holds).isSome := by
  obtain ⟨a, ha, hf⟩ := List.all_eq_false.mp h
  simp only [X, labelledX, List.mem_map, List.mem_flatMap] at ha
  obtain ⟨b, ⟨p, hp, hb⟩, rfl⟩ := ha
  refine List.findSome?_isSome_iff.mpr ⟨(p.id, b), List.mem_flatMap.mpr ⟨p, hp, List.mem_map.mpr ⟨b, hb, rfl⟩⟩, ?_⟩
  simp [hf]

/-! ## 2.9 What PK-1 guarantees about witnesses -/

/-- 2.9: `X` without the premises under the labels in `drop`. -/
def xWithout (qs : List Pack) (drop : List String) : List VE.Formula :=
  ((labelledX qs).filter (fun a => !drop.contains a.1)).map (·.2)

/-- 2.9: the soft pack's coherence labels, from the colliding pairs (DF7's collision witness drops these). -/
def coherenceLabels (D : VE.SoftNorms.SoftDoc) : List String :=
  (VE.SoftNorms.collidingPairs D).map (fun (M, N) => VE.SoftNorms.Wire.cohLabel M N)

theorem xWithout_nil (qs : List Pack) : xWithout qs [] = X qs := by
  simp only [xWithout, X, List.contains_nil, Bool.not_false]
  rw [List.filter_eq_self.mpr (fun _ _ => rfl)]

theorem xWithout_sub (qs : List Pack) (drop : List String) : ∀ a ∈ xWithout qs drop, a ∈ X qs := by
  intro a ha
  simp only [xWithout, List.mem_map, List.mem_filter] at ha
  obtain ⟨b, ⟨hb, _⟩, rfl⟩ := ha
  exact List.mem_map.mpr ⟨b, hb, rfl⟩

end VE.NormDefaults.Packs
