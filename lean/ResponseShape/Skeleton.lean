import ResponseShape.CaseDeciders
import Std.Data.TreeMap.Raw.Lemmas
import Std.Data.TreeMap.Raw.WF
import Lean.ToExpr

/-! # Skeletons: the fields of a shape, for the theorems that tie each encoder to its shape

A `Skel` is what a `Shape` says about the fields of the objects in a value: for each object
its allowed fields (each with the skeleton of its value), the fields it requires and the
fields it forbids, through arrays, alternatives and references; where a field's presence
depends on another field's string value (an `if`/`then`/`else`), that value; and where it
depends on the request case (an `if` over `x-case`), that condition (`CaseCond`). Everything
else a shape checks (patterns, numbers, echoes, counts, grammars without objects) is `any`
here, and a value the runner copies from the request (`Shape.copied`) is `any`.
An encoded environment instead retains an encoder obligation: its value is the prime
environment of its source, and every generated predicate entry fits the entry shape
extracted from the environment schema. The decoded source fields remain the request decoder's.

`skeleton files s` extracts the skeleton of a shape. It describes at least every value valid
under the shape (it may allow more: a condition on a field's value it cannot express is
dropped, never strengthened; a condition on the request it cannot express, or a recursive
reference, is an error), and it keeps every field list: an object closed by
`additionalProperties: false` is closed here with exactly its properties, and its `required`
list is required.

`Fits c k v` says that the JSON value `v`, answering the request case `c`, has the fields `k`
describes. The theorems of `ResponseShape.Encoders` prove, for every service mode, that every
row its runner returns for a case fits the skeleton of the mode's row shape, so a field an
encoder adds or drops, or a shape that lists another field, fails the build. -/

namespace ResponseShape
open Lean

/-- A condition on the request case, as the shapes write it (the condition of an `x-case` or of an
`x-select` entry). -/
inductive CaseCond where
  /-- The case's `kind` is this string: `{"type": "object", "required": ["kind"], "properties":
  {"kind": {"const": k}}}` (read as the runners read it, with `getStr?`: proofs cannot see into `Json`'s `==`). -/
  | kind (k : String)
  /-- The case has the field `ks[0]`, whose value is an object with the field `ks[1]`, and so
  on: `{"required": [k0], "properties": {k0: {"type": "object", "required": [k1], ...}}}`
  (true of a case that is not an object, as JSON Schema has it). -/
  | path (ks : List String)
  /-- The same with the case itself an object: `{"type": "object", "required": [k0], ...}`. -/
  | has (ks : List String)
  /-- The case is an object without the field `k`: `{"type": "object", "not": {"required": [k]}}`. -/
  | lacks (k : String)
  /-- Every condition holds (`allOf`; `true` is the empty conjunction). -/
  | all (cs : List CaseCond)
  /-- The runner's own test of the case (`decidedCase`) says yes. -/
  | decided (d : CaseDecider)
  deriving Inhabited, Repr, BEq, Lean.ToExpr

namespace CaseCond

/-- An object holding the nested fields `ks` (no condition on the value when `ks` is empty). -/
def objectHas : Json → List String → Bool
  | _, [] => true
  | j@(.obj _), k :: ks => match j.getObjVal? k with
    | .ok v => objectHas v ks
    | .error _ => false
  | _, _ :: _ => false

def holds : CaseCond → Json → Bool
  | .kind k, j => (j.getObjValD "kind").getStr?.toOption == some k
  | .path [], _ => true
  | .path (k :: ks), j => match j with
    | .obj _ => match j.getObjVal? k with
      | .ok v => objectHas v ks
      | .error _ => false
    | _ => true
  | .has ks, j => match j with
    | .obj _ => objectHas j ks
    | _ => false
  | .lacks k, j => match j with
    | .obj _ => !(j.getObjVal? k).toBool
    | _ => false
  | .all cs, j => allHold cs j
  | .decided d, j => d.fn j
where
  allHold : List CaseCond → Json → Bool
    | [], _ => true
    | c :: cs, j => holds c j && allHold cs j

@[simp] theorem holds_all_nil (j : Json) : (CaseCond.all []).holds j = true := rfl

@[simp] theorem holds_all_cons (c : CaseCond) (cs : List CaseCond) (j : Json) :
    (CaseCond.all (c :: cs)).holds j = (c.holds j && (CaseCond.all cs).holds j) := rfl

@[simp] theorem holds_decided (d : CaseDecider) (j : Json) : (CaseCond.decided d).holds j = d.fn j := rfl

/-- The case's `kind` is known: each condition on it reads off the string. -/
theorem holds_kind_of {j : Json} {s : String} (h : j.getObjValD "kind" = .str s) (k : String) :
    (CaseCond.kind k).holds j = (s == k) := by
  simp only [holds, h]
  show (some s == some k) = (s == k)
  by_cases e : s = k
  · subst e; simp
  · simp [e]

theorem getObjValD_eq (j : Json) (k : String) : j.getObjValD k = (j.getObjVal? k).toOption.getD .null := rfl

/-- A case with a `kind` string has the field. -/
theorem lacks_of_kind {j : Json} {s : String} (h : j.getObjValD "kind" = .str s) :
    (CaseCond.lacks "kind").holds j = false := by
  rw [getObjValD_eq] at h
  cases hv : j.getObjVal? "kind" with
  | error e => rw [hv] at h; cases h
  | ok v => cases j <;> simp_all [holds, Except.toBool]

/-- A case without `kind` has no kind. -/
theorem kind_of_lacks {j : Json} (h : (CaseCond.lacks "kind").holds j = true) (k : String) :
    (CaseCond.kind k).holds j = false := by
  have hd : j.getObjValD "kind" = .null := by
    rw [getObjValD_eq]
    cases hv : j.getObjVal? "kind" with
    | error e => rfl
    | ok v => cases j <;> simp_all [holds, Except.toBool]
  simp only [holds, hd]
  rfl

theorem path_ok {j v : Json} {k : String} (h : j.getObjVal? k = .ok v) : (CaseCond.path [k]).holds j = true := by
  cases j <;> simp_all [holds, objectHas, Json.getObjVal?]

/-- A case that is an object (it has the field `k'`) and lacks the field `k`. -/
theorem path_error {j w : Json} {k k' e : String} (hobj : j.getObjVal? k' = .ok w) (h : j.getObjVal? k = .error e) :
    (CaseCond.path [k]).holds j = false := by
  cases j <;> simp_all [holds, Json.getObjVal?]

theorem objectHas_cons {j v : Json} {k : String} {ks : List String} (h : j.getObjVal? k = .ok v) :
    objectHas j (k :: ks) = objectHas v ks := by
  cases j <;> simp_all [objectHas, Json.getObjVal?]

theorem holds_path_cons {j v : Json} {k : String} {ks : List String} (h : j.getObjVal? k = .ok v) :
    (CaseCond.path (k :: ks)).holds j = objectHas v ks := by
  cases j <;> simp_all [holds, Json.getObjVal?]

/-- One field of an object: present or not. -/
theorem objectHas_one {raw : Json} {m : Std.TreeMap.Raw String Json compare} (hobj : raw = .obj m) (k : String) :
    objectHas raw [k] = (raw.getObjVal? k).toBool := by
  subst hobj
  simp only [objectHas]
  split <;> simp_all [objectHas, Except.toBool]

/-- A case that is an object without the field `k`. -/
theorem lacks_of_error {j w : Json} {k k' e : String} (hobj : j.getObjVal? k' = .ok w) (h : j.getObjVal? k = .error e) :
    (CaseCond.lacks k).holds j = true := by
  cases j <;> simp_all [holds, Json.getObjVal?, Except.toBool]

/-- In an object case, `path [k]` is whether the field is there. -/
theorem path_toBool {j w : Json} {k' : String} (hobj : j.getObjVal? k' = .ok w) (k : String) :
    (CaseCond.path [k]).holds j = (j.getObjVal? k).toBool := by
  cases j <;> simp_all [holds, objectHas, Json.getObjVal?]
  split <;> simp_all [Except.toBool, objectHas]

/-- A case with the field `k` does not lack it. -/
theorem lacks_of_val {j v : Json} {k : String} (h : j.getObjVal? k = .ok v) : (CaseCond.lacks k).holds j = false := by
  cases j <;> simp_all [holds, Json.getObjVal?, Except.toBool]

/-- A field read as a string is the case's `getObjValD` of it. -/
theorem getObjValD_of_str {j v : Json} {k s : String} (h : j.getObjVal? k = .ok v) (hs : v.getStr? = .ok s) :
    j.getObjValD k = .str s := by
  rw [getObjValD_eq, h]
  cases v <;> simp_all [Json.getStr?] <;> cases hs <;> rfl

end CaseCond

/-- The runner read the case's kind as `k`: the case's `kind` string, or `d` (the runner's default)
for a case that is an object without one. The conditions of a mode's selection on the kind are
decided from it (`case_cond`). -/
def KindRead (d : String) (c : Json) (k : String) : Prop :=
  c.getObjValD "kind" = .str k ∨ ((CaseCond.lacks "kind").holds c = true ∧ k = d)

theorem KindRead.of_str {d k : String} {c : Json} (h : c.getObjValD "kind" = .str k) : KindRead d c k := Or.inl h

namespace CaseCond

def isKind : CaseCond → Bool
  | .kind _ => true
  | _ => false

end CaseCond

/-- A case whose object map, and its environment's, are well formed, as every case the service
decodes is (its maps are built by insertion). -/
def CaseWF (j : Json) : Prop := (∀ m, j = .obj m → m.WF) ∧ (∀ m, j.getObjValD "environment" = .obj m → m.WF)

/-- Setting a field other than `kind` keeps the case's kind. -/
theorem kind_setObjVal {j : Json} (hj : CaseWF j) {k : String} (hk : k ≠ "kind") (v : Json) :
    (j.setObjVal! k v).getObjValD "kind" = j.getObjValD "kind" := by
  cases j with
  | obj m =>
    have wf := hj.1 m rfl
    simp only [Json.setObjVal!, Json.getObjValD, Json.getObjVal?]
    have : (m.insert k v).get? "kind" = m.get? "kind" := by
      have h := Std.TreeMap.Raw.getElem?_insert (k := k) (v := v) (a := "kind") wf
      have hne : ¬ compare k "kind" = .eq := fun h => hk ((Std.LawfulEqCmp.compare_eq_iff_eq (cmp := compare)).mp h)
      simpa [hne] using h
    rw [this]
  | _ => rfl

/-- Setting another field keeps a field of the case. -/
theorem getObjVal_setObjVal {j : Json} (hj : ∀ m, j = .obj m → m.WF) {m : Std.TreeMap.Raw String Json compare}
    (hm : j = .obj m) {k k' : String} (hk : k ≠ k') (v : Json) : (j.setObjVal! k v).getObjVal? k' = j.getObjVal? k' := by
  subst hm
  have wf := hj _ rfl
  simp only [Json.setObjVal!, Json.getObjVal?]
  have : (m.insert k v).get? k' = m.get? k' := by
    have h := Std.TreeMap.Raw.getElem?_insert (k := k) (v := v) (a := k') wf
    have hne : ¬ compare k k' = .eq := fun h => hk ((Std.LawfulEqCmp.compare_eq_iff_eq (cmp := compare)).mp h)
    simpa [hne] using h
  rw [this]

inductive Skel where
  /-- Any value. -/
  | any
  /-- No value (the value of a field a closed object does not allow). -/
  | nothing
  /-- A string among these. -/
  | strIn (vs : List String)
  /-- Any value but a string among these. -/
  | strNotIn (vs : List String)
  /-- A value whose JSON type (`ResponseShape.kind`) is not this one. -/
  | kindNot (k : String)
  /-- An object: a field of `fields` has a value fitting its skeleton, any other field one
  fitting `extra` (none: no other field); `required` are present, `absent` are not. -/
  | obj (fields : List (String × Skel)) (extra : Option Skel) (required : List String) (absent : List String)
  /-- An array: element `i` fits `pre[i]`, and every element after `pre` fits `items`. -/
  | arr (pre : List Skel) (items : Skel)
  | all (ss : List Skel)
  | alt (ss : List Skel)
  /-- `t` when the request case meets `c`, else `e`. -/
  | onCase (c : CaseCond) (t e : Skel)
  /-- A prime environment produced by the soft-norms or rights encoder. Its generated
  predicate entries must fit the schema-derived `entry` skeleton. -/
  | encodedEnvironment (entry : Skel)
  deriving Inhabited, Repr, BEq, Lean.ToExpr

namespace Skel

/-- The skeleton of the value of field `k`. -/
def field (fields : List (String × Skel)) (extra : Option Skel) (k : String) : Skel :=
  match fields.lookup k with
  | some s => s
  | none => extra.getD .nothing

def item (pre : List Skel) (items : Skel) (i : Nat) : Skel := pre.getD i items

/-- Whether `keys` has no duplicate. -/
def distinct (keys : List String) : Bool := keys.Nodup

/-- Whether `keys` (an object's field names, in order) has no duplicate, only allowed fields,
every required field and no forbidden one. -/
def keysOk (fields : List (String × Skel)) (extra : Option Skel) (required absent : List String)
    (keys : List String) : Bool :=
  keys.Nodup && keys.all (fun k => (fields.lookup k).isSome || extra.isSome) &&
    required.all keys.contains && absent.all (fun k => !keys.contains k)

end Skel

/-! ## Fitting -/

inductive Fits (c : Json) : Skel → Json → Prop where
  | any (v : Json) : Fits c .any v
  | strIn {vs : List String} {s : String} : s ∈ vs → Fits c (.strIn vs) (.str s)
  | strNotIn {vs : List String} {v : Json} : (∀ s, v = .str s → s ∉ vs) → Fits c (.strNotIn vs) v
  | kindNot {k : String} {v : Json} : kind v ≠ k → Fits c (.kindNot k) v
  | obj {fields : List (String × Skel)} {extra : Option Skel} {required absent : List String}
      {m : Std.TreeMap.Raw String Json} :
      (∀ k v, m[k]? = some v → Fits c (Skel.field fields extra k) v) →
      (∀ k ∈ required, (m[k]?).isSome) → (∀ k ∈ absent, m[k]? = none) →
      Fits c (.obj fields extra required absent) (.obj m)
  | arr {pre : List Skel} {items : Skel} {xs : Array Json} :
      (∀ i (h : i < xs.size), Fits c (Skel.item pre items i) xs[i]) → Fits c (.arr pre items) (.arr xs)
  | all {ss : List Skel} {v : Json} : (∀ s ∈ ss, Fits c s v) → Fits c (.all ss) v
  | alt {ss : List Skel} {s : Skel} {v : Json} : s ∈ ss → Fits c s v → Fits c (.alt ss) v
  | onCaseT {cond : CaseCond} {t e : Skel} {v : Json} : cond.holds c = true → Fits c t v → Fits c (.onCase cond t e) v
  | onCaseE {cond : CaseCond} {t e : Skel} {v : Json} : cond.holds c = false → Fits c e v → Fits c (.onCase cond t e) v
  | softEnvironment {entry : Skel} (D : VE.SoftNorms.SoftDoc) (env : Json) :
      (∀ p ∈ VE.SoftNorms.decisions D,
        Fits c entry (VE.SoftNorms.Wire.decisionEntry p.2)) →
      VE.SoftNorms.Wire.primeJson D env = (do
        let canonical ← VE.Norms.Wire.canonicalEnvironmentJson env
        VE.Norms.Wire.appendPredicates canonical
          ((VE.SoftNorms.decisions D).map fun (n, ss) => (n, VE.SoftNorms.Wire.decisionEntry ss))) →
      Fits c (.encodedEnvironment entry) ((VE.SoftNorms.Wire.primeJson D env).toOption.getD .null)
  | rightsEnvironment {entry : Skel} (D : VE.Rights.RightsDoc) (env : Json) :
      (∀ p ∈ VE.Rights.Wire.genEntries D, Fits c entry p.2) →
      (∀ p ∈ VE.SoftNorms.decisions (VE.Rights.correlate D),
        Fits c entry (VE.SoftNorms.Wire.decisionEntry p.2)) →
      VE.Rights.Wire.primeJsonR D env = (do
        let canonical ← VE.Norms.Wire.canonicalEnvironmentJson env
        let rights ← VE.Norms.Wire.appendPredicates canonical (VE.Rights.Wire.genEntries D)
        VE.Norms.Wire.appendPredicates rights
          ((VE.SoftNorms.decisions (VE.Rights.correlate D)).map fun (n, ss) =>
            (n, VE.SoftNorms.Wire.decisionEntry ss))) →
      Fits c (.encodedEnvironment entry) ((VE.Rights.Wire.primeJsonR D env).toOption.getD .null)

namespace Fits

variable {c : Json}

theorem nothing_not (v : Json) : ¬ Fits c .nothing v := by
  intro h
  cases h

theorem ofList_get {l : List (String × Json)} (hd : (l.map Prod.fst).Nodup) {k : String} {v : Json}
    (h : (Std.TreeMap.Raw.ofList l compare)[k]? = some v) : (k, v) ∈ l := by
  have hpw : l.Pairwise (fun a b => ¬ compare a.1 b.1 = .eq) := by
    have := List.pairwise_map.mp hd
    exact this.imp fun hne heq => hne ((Std.LawfulEqCmp.compare_eq_iff_eq (cmp := compare)).mp heq)
  cases hc : (l.map Prod.fst).contains k with
  | false =>
    rw [Std.TreeMap.Raw.getElem?_ofList_of_contains_eq_false hc] at h
    cases h
  | true =>
    obtain ⟨⟨k', v'⟩, hm, hk⟩ : ∃ p ∈ l, p.1 = k := by
      simpa [List.contains_iff_mem] using hc
    simp only at hk
    subst hk
    rw [Std.TreeMap.Raw.getElem?_ofList_of_mem ((Std.LawfulEqCmp.compare_eq_iff_eq (cmp := compare)).mpr rfl) hpw hm] at h
    cases h
    exact hm

/-- A field of an object built from a list holds the value of some element of the list. -/
theorem ofList_value {l : List (String × Json)} {k : String} {v : Json}
    (h : (Std.TreeMap.Raw.ofList l compare)[k]? = some v) : ∃ k', (k', v) ∈ l := by
  rw [Std.TreeMap.Raw.ofList_eq_insertMany_empty,
    Std.TreeMap.Raw.getElem?_insertMany_list Std.TreeMap.Raw.WF.emptyc] at h
  simp only [Std.TreeMap.Raw.getElem?_emptyc, Option.or_none] at h
  rw [List.findSomeRev?_eq_findSome?_reverse] at h
  obtain ⟨⟨a, b⟩, hm, hb⟩ := List.exists_of_findSome?_eq_some h
  split at hb
  · cases hb
    exact ⟨a, List.mem_reverse.mp hm⟩
  · cases hb

/-- An object whose field names are data (a map): every value fits `s`. -/
theorem mkObjExtra {s : Skel} {l : List (String × Json)} (hv : ∀ p ∈ l, Fits c s p.2) :
    Fits c (.obj [] (some s) [] []) (Json.mkObj l) := by
  refine Fits.obj (fun k v h => ?_) (fun _ h => by cases h) (fun _ h => by cases h)
  obtain ⟨k', hm⟩ := ofList_value h
  exact hv _ hm

theorem isSome_of_mem {m : Std.TreeMap.Raw String Json} (wf : m.WF) {k : String} (h : k ∈ m) :
    (m[k]?).isSome = true :=
  (Std.TreeMap.Raw.mem_iff_isSome_getElem? wf).mp h

theorem none_of_not_mem {m : Std.TreeMap.Raw String Json} (wf : m.WF) {k : String} (h : k ∉ m) :
    m[k]? = none :=
  Option.not_isSome_iff_eq_none.mp fun hs => h ((Std.TreeMap.Raw.mem_iff_isSome_getElem? wf).mpr hs)

/-- An object built from a list of fields (`Json.mkObj`): its field names pass `keysOk` and each
value fits the skeleton of its field. -/
theorem mkObj {fields : List (String × Skel)} {extra : Option Skel} {required absent : List String}
    {l : List (String × Json)} (hk : Skel.keysOk fields extra required absent (l.map Prod.fst) = true)
    (hv : ∀ p ∈ l, Fits c (Skel.field fields extra p.1) p.2) :
    Fits c (.obj fields extra required absent) (Json.mkObj l) := by
  simp only [Skel.keysOk, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hk
  obtain ⟨⟨⟨hd, _⟩, hreq⟩, hab⟩ := hk
  have wf : (Std.TreeMap.Raw.ofList l compare).WF := Std.TreeMap.Raw.WF.ofList
  refine Fits.obj (fun k v h => hv (k, v) (ofList_get hd h)) (fun k hk => ?_) (fun k hk => ?_)
  · exact isSome_of_mem wf (Std.TreeMap.Raw.mem_ofList.mpr (hreq k hk))
  · refine none_of_not_mem wf fun hm => ?_
    have := hab k hk
    simp only [Bool.not_eq_true'] at this
    rw [Std.TreeMap.Raw.mem_ofList.mp hm] at this
    cases this

/-- An object built from a list of fields, then given the field `k` (`Json.setObjVal!`): the names
of `l` have no duplicate and, with `k` in place of any field of that name, pass `keysOk`. -/
theorem setObj {fields : List (String × Skel)} {extra : Option Skel} {required absent : List String}
    {l : List (String × Json)} {k : String} {v : Json}
    (hk : (Skel.distinct (l.map Prod.fst) && Skel.keysOk fields extra required absent
      (k :: (l.map Prod.fst).filter (· != k))) = true)
    (hv : ∀ p ∈ l.filter (·.1 != k), Fits c (Skel.field fields extra p.1) p.2)
    (hkv : Fits c (Skel.field fields extra k) v) :
    Fits c (.obj fields extra required absent) ((Json.mkObj l).setObjVal! k v) := by
  simp only [Skel.distinct, Bool.and_eq_true, decide_eq_true_eq, Skel.keysOk, List.all_eq_true] at hk
  obtain ⟨hd, ⟨⟨_, _⟩, hreq⟩, hab⟩ := hk
  have wf : (Std.TreeMap.Raw.ofList l compare).WF := Std.TreeMap.Raw.WF.ofList
  have wf' := Std.TreeMap.Raw.WF.insert (a := k) (b := v) wf
  refine Fits.obj (fun k' v' h => ?_) (fun k' hk' => isSome_of_mem wf' ?_) (fun k' hk' => none_of_not_mem wf' ?_)
  · rw [Std.TreeMap.Raw.getElem?_insert wf] at h
    split at h
    · rename_i he
      cases h
      rw [← (Std.LawfulEqCmp.compare_eq_iff_eq (cmp := compare)).mp he]
      exact hkv
    · rename_i he
      have hm := ofList_get hd h
      refine hv (k', v') (List.mem_filter.mpr ⟨hm, ?_⟩)
      simp only [bne_iff_ne, ne_eq]
      intro hh
      exact he ((Std.LawfulEqCmp.compare_eq_iff_eq (cmp := compare)).mpr hh.symm)
  · rw [Std.TreeMap.Raw.mem_insert wf]
    have := hreq k' hk'
    simp only [List.contains_cons, Bool.or_eq_true, beq_iff_eq, List.contains_iff_mem, List.mem_filter] at this
    rcases this with rfl | ⟨hm, _⟩
    · exact Or.inl ((Std.LawfulEqCmp.compare_eq_iff_eq (cmp := compare)).mpr rfl)
    · exact Or.inr (Std.TreeMap.Raw.mem_ofList.mpr (List.contains_iff_mem.mpr hm))
  · rw [Std.TreeMap.Raw.mem_insert wf, Std.TreeMap.Raw.mem_ofList]
    have := hab k' hk'
    simp only [List.contains_cons, Bool.or_eq_true, beq_iff_eq, List.contains_iff_mem, List.mem_filter,
      Bool.not_eq_true', Bool.or_eq_false_iff, beq_eq_false_iff_ne, ne_eq] at this
    intro hh
    rcases hh with hh | hh
    · exact this.1 ((Std.LawfulEqCmp.compare_eq_iff_eq (cmp := compare)).mp hh).symm
    · have hm := List.contains_iff_mem.mp hh
      simp_all

/-- An array of the images of a list's elements. -/
theorem arrMap {α : Type} {items : Skel} {xs : List α} {f : α → Json} (h : ∀ x ∈ xs, Fits c items (f x)) :
    Fits c (.arr [] items) (Json.arr (xs.map f).toArray) := by
  refine Fits.arr fun i hi => ?_
  simp only [Skel.item, List.getD_nil, List.getElem_toArray, List.getElem_map]
  exact h _ (List.getElem_mem _)

theorem arrList {items : Skel} {xs : List Json} (h : ∀ x ∈ xs, Fits c items x) :
    Fits c (.arr [] items) (Json.arr xs.toArray) := by
  have := arrMap (c := c) (f := id) h
  simpa using this

theorem altHead {s : Skel} {ss : List Skel} {v : Json} (h : Fits c s v) : Fits c (.alt (s :: ss)) v :=
  Fits.alt List.mem_cons_self h

theorem altTail {s : Skel} {ss : List Skel} {v : Json} (h : Fits c (.alt ss) v) : Fits c (.alt (s :: ss)) v := by
  cases h with
  | alt hm h => exact Fits.alt (List.mem_cons_of_mem _ hm) h

theorem strIn_lit {vs : List String} {s : String} (h : vs.contains s = true) : Fits c (.strIn vs) (.str s) :=
  Fits.strIn (by simpa using h)

theorem strNotIn_lit {vs : List String} {s : String} (h : vs.contains s = false) :
    Fits c (.strNotIn vs) (.str s) :=
  Fits.strNotIn fun t ht => by
    cases ht
    simpa using h

/-- An array whose every element fits `items`. -/
theorem arrOf {items : Skel} {a : Array Json} (h : ∀ x ∈ a, Fits c items x) : Fits c (.arr [] items) (.arr a) :=
  Fits.arr fun i hi => by
    simp only [Skel.item, List.getD_nil]
    exact h _ (Array.getElem_mem hi)

/-- The alternative `n` of `ss` is an object skeleton the fields of `l` pass. -/
theorem mkObjAlt {ss : List Skel} (n : Nat) {fields : List (String × Skel)} {extra : Option Skel}
    {required absent : List String} {l : List (String × Json)}
    (hn : ss[n]? = some (.obj fields extra required absent))
    (hk : Skel.keysOk fields extra required absent (l.map Prod.fst) = true)
    (hv : ∀ p ∈ l, Fits c (Skel.field fields extra p.1) p.2) : Fits c (.alt ss) (Json.mkObj l) :=
  Fits.alt (List.mem_of_getElem? hn) (mkObj hk hv)

/-- The alternative `n` of `ss` is an object skeleton the fields of `(Json.mkObj l).setObjVal! k v` pass. -/
theorem setObjAlt {ss : List Skel} (n : Nat) {fields : List (String × Skel)} {extra : Option Skel}
    {required absent : List String} {l : List (String × Json)} {k : String} {v : Json}
    (hn : ss[n]? = some (.obj fields extra required absent))
    (hk : (Skel.distinct (l.map Prod.fst) && Skel.keysOk fields extra required absent
      (k :: (l.map Prod.fst).filter (· != k))) = true)
    (hv : ∀ p ∈ l.filter (·.1 != k), Fits c (Skel.field fields extra p.1) p.2)
    (hkv : Fits c (Skel.field fields extra k) v) : Fits c (.alt ss) ((Json.mkObj l).setObjVal! k v) :=
  Fits.alt (List.mem_of_getElem? hn) (setObj hk hv hkv)

/-- Every member of `ss` is one of `ts`: a value fitting `ss` fits `ts` (a runner delegating to
another mode's runner). -/
theorem altSub {ss ts : List Skel} {v : Json} (hs : ∀ s ∈ ss, s ∈ ts) (h : Fits c (.alt ss) v) :
    Fits c (.alt ts) v := by
  cases h with
  | alt hm h => exact Fits.alt (hs _ hm) h

theorem ofAlt {s : Skel} {ss : List Skel} {v : Json} (hs : s ∈ ss) (h : Fits c s v) : Fits c (.alt ss) v :=
  Fits.alt hs h

theorem alt_inv {ss : List Skel} {v : Json} (h : Fits c (.alt ss) v) : ∃ s ∈ ss, Fits c s v := by
  cases h with
  | alt hm h => exact ⟨_, hm, h⟩

theorem onCase_inv {cond : CaseCond} {t e : Skel} {v : Json} (h : Fits c (.onCase cond t e) v) :
    (cond.holds c = true ∧ Fits c t v) ∨ (cond.holds c = false ∧ Fits c e v) := by
  cases h with
  | onCaseT hc h => exact .inl ⟨hc, h⟩
  | onCaseE hc h => exact .inr ⟨hc, h⟩

end Fits

/-- `∀ v, r = .ok v → P v`: every result a computation returns satisfies `P`. -/
def OkP {α : Type} (P : α → Prop) (r : Except String α) : Prop := ∀ v, r = .ok v → P v

/-- Every result a runner returns fits `k`. -/
abbrev OkFits (c : Json) (k : Skel) (r : Except String Json) : Prop := OkP (Fits c k) r

namespace OkP

variable {α : Type} {P : α → Prop}

theorem pure {v : α} (h : P v) : OkP P (Pure.pure v) := by
  intro w hw
  cases hw
  exact h

theorem ok {v : α} (h : P v) : OkP P (.ok v) := pure h

theorem throw {e : String} : OkP P (MonadExcept.throw e) := by
  intro w hw
  cases hw

theorem error {e : String} : OkP P (.error e) := throw

theorem bind {β : Type} {x : Except String β} {f : β → Except String α} (h : ∀ a, x = .ok a → OkP P (f a)) :
    OkP P (x >>= f) := by
  intro w hw
  cases x with
  | error e => cases hw
  | ok a => exact h a rfl w hw

theorem pure_ok {β : Type} {v a : β} : (Pure.pure v : Except String β) = .ok a ↔ v = a :=
  ⟨fun h => by cases h; rfl, fun h => by subst h; rfl⟩

theorem throw_bind {β : Type} {e : String} {f : β → Except String α} : OkP P (MonadExcept.throw e >>= f) := by
  intro w hw
  cases hw

theorem ite {c : Prop} [Decidable c] {a b : Except String α} (ha : c → OkP P a) (hb : ¬ c → OkP P b) :
    OkP P (if c then a else b) := by
  split
  · exact ha ‹_›
  · exact hb ‹_›

/-- A `mapM` returns the images of the elements, each satisfying what the function guarantees. -/
theorem mapM {β : Type} {Q : α → Prop} {f : β → Except String α} {xs : List β} (h : ∀ x ∈ xs, OkP Q (f x)) :
    OkP (fun ys => ∀ y ∈ ys, Q y) (xs.mapM f) := by
  induction xs with
  | nil =>
    intro ys hys
    cases hys
    simp
  | cons x xs ih =>
    intro ys hys
    cases hfx : f x with
    | error e => simp only [List.mapM_cons, hfx] at hys; cases hys
    | ok y =>
      cases hrest : List.mapM f xs with
      | error e => simp only [List.mapM_cons, hfx, hrest] at hys; cases hys
      | ok zs =>
        simp only [List.mapM_cons, hfx, hrest] at hys
        have hys : (Except.ok (y :: zs) : Except String (List α)) = .ok ys := hys
        cases hys
        intro w hw
        rcases List.mem_cons.mp hw with rfl | hw
        · exact h x List.mem_cons_self w hfx
        · exact ih (fun z hz => h z (List.mem_cons_of_mem _ hz)) zs hrest w hw

theorem map {β : Type} {x : Except String β} {f : β → α} (h : ∀ a, P (f a)) : OkP P (x.map f) := by
  intro w hw
  cases x with
  | error e => cases hw
  | ok a => cases hw; exact h a

theorem filterMapM_loop {β : Type} {Q : α → Prop} {f : β → Except String (Option α)}
    (h : ∀ x, OkP (fun o => ∀ b, o = some b → Q b) (f x)) :
    ∀ (xs : List β) (bs : List α), (∀ b ∈ bs, Q b) → OkP (fun ys => ∀ y ∈ ys, Q y) (List.filterMapM.loop f xs bs)
  | [], bs, hb => by
    intro ys hys
    simp only [List.filterMapM.loop] at hys
    have hys : (Except.ok bs.reverse : Except String (List α)) = .ok ys := hys
    cases hys
    intro y hy
    exact hb y (List.mem_reverse.mp hy)
  | x :: xs, bs, hb => by
    intro ys hys
    simp only [List.filterMapM.loop] at hys
    cases hfx : f x with
    | error e => rw [hfx] at hys; cases hys
    | ok o =>
      rw [hfx] at hys
      cases o with
      | none => exact filterMapM_loop h xs bs hb ys hys
      | some b =>
        exact filterMapM_loop h xs (b :: bs) (fun y hy => by
          rcases List.mem_cons.mp hy with rfl | hy
          · exact h x _ hfx y rfl
          · exact hb y hy) ys hys

/-- A `filterMapM` returns elements each satisfying what the function guarantees of its `some`. -/
theorem filterMapM {β : Type} {Q : α → Prop} {f : β → Except String (Option α)} {xs : List β}
    (h : ∀ x, OkP (fun o => ∀ b, o = some b → Q b) (f x)) : OkP (fun ys => ∀ y ∈ ys, Q y) (xs.filterMapM f) :=
  filterMapM_loop h xs [] (fun _ h => by cases h)

/-- An array `mapM` returns the images of the elements, each satisfying what the function guarantees. -/
theorem arrayMapM {β : Type} {Q : α → Prop} {f : β → Except String α} {xs : Array β}
    (h : ∀ x ∈ xs, OkP Q (f x)) : OkP (fun ys => ∀ y ∈ ys, Q y) (xs.mapM f) := by
  intro ys hys
  rw [Array.mapM_eq_mapM_toList] at hys
  cases hl : xs.toList.mapM f with
  | error e => rw [hl] at hys; cases hys
  | ok l =>
    rw [hl] at hys
    have hys : (Except.ok l.toArray : Except String (Array α)) = .ok ys := hys
    cases hys
    intro y hy
    exact OkP.mapM (fun x hx => h x (by simpa using hx)) l hl y (by simpa using hy)

/-- A `for` loop over a list keeps an invariant of its state. -/
theorem forIn {β : Type} {xs : List β} {init : α} {f : β → α → Except String (ForInStep α)}
    (h0 : P init) (hf : ∀ x ∈ xs, ∀ s, P s → OkP (fun r : ForInStep α => P r.value) (f x s)) :
    OkP P (ForIn.forIn xs init f) := by
  induction xs generalizing init with
  | nil => intro v hv; cases hv; exact h0
  | cons x xs ih =>
    intro v hv
    simp only [List.forIn_cons] at hv
    cases hfx : f x init with
    | error e => rw [hfx] at hv; cases hv
    | ok r =>
      rw [hfx] at hv
      have hr := hf x List.mem_cons_self init h0 r hfx
      cases r with
      | done s => exact (by cases hv; exact hr)
      | yield s => exact ih hr (fun y hy => hf y (List.mem_cons_of_mem _ hy)) v hv

theorem of {r : Except String α} {Q : α → Prop} (h : OkP Q r) (hq : ∀ v, Q v → P v) : OkP P r :=
  fun v hv => hq v (h v hv)

end OkP

theorem isEmpty_empty : ("" : String).isEmpty = true := rfl

/-- Setting a field of an object built from a list is building it from the list with that field
appended (a later field of the same name replaces an earlier one). -/
theorem setObjVal_mkObj (l : List (String × Json)) (k : String) (v : Json) :
    (Json.mkObj l).setObjVal! k v = Json.mkObj (l ++ [(k, v)]) := by
  simp only [Json.mkObj, Json.setObjVal!]
  rw [Std.TreeMap.Raw.ofList_eq_insertMany_empty, Std.TreeMap.Raw.ofList_eq_insertMany_empty,
    Std.TreeMap.Raw.insertMany_append, Std.TreeMap.Raw.insertMany_list_singleton]

theorem getArr_arr (a : Array Json) : (Json.arr a).getArr? = .ok a := rfl

theorem toOption_ok {α : Type} (a : α) : (Except.ok a : Except String α).toOption = some a := rfl

theorem isEmpty_iff_data (s : String) : s.isEmpty = true ↔ s.data = [] := by
  rcases s with ⟨cs⟩
  cases cs with
  | nil => decide
  | cons c cs =>
    simp only [String.isEmpty, beq_iff_eq, reduceCtorEq, iff_false]
    intro h
    have := congrArg String.Pos.byteIdx h
    simp [String.endPos, String.utf8ByteSize, String.utf8ByteSize.go] at this
    exact absurd this.2 (Nat.pos_iff_ne_zero.mp c.utf8Size_pos)

/-- A string built by appending (an interpolation) is empty exactly when every piece is: with
`simp +decide [isEmpty_append, toString]` a label with a literal prefix is never empty. -/
@[simp] theorem isEmpty_append (a b : String) : (a ++ b).isEmpty = (a.isEmpty && b.isEmpty) := by
  apply Bool.eq_iff_iff.mpr
  simp only [isEmpty_iff_data, String.data_append, List.append_eq_nil_iff, Bool.and_eq_true]

/-! ## Changing the case

A runner that answers a case through another runner on a rewritten case (`Readings.Run.runLower`
drops `readings@1` from the environment) gives rows that fit for the rewritten case; they fit for
the original one when every condition on the case in the skeleton reads the same of both. -/

namespace Skel

/-- Whether every condition on the case in `k` satisfies `p` (`fuel` bounds the nesting). -/
def condsOk (p : CaseCond → Bool) : Nat → Skel → Bool
  | 0, _ => false
  | n + 1, k => match k with
    | .obj fs ex _ _ => fs.all (fun f => condsOk p n f.2) && ex.all (condsOk p n)
    | .arr pre it => pre.all (condsOk p n) && condsOk p n it
    | .all ss | .alt ss => ss.all (condsOk p n)
    | .onCase c t e => p c && condsOk p n t && condsOk p n e
    | .encodedEnvironment entry => condsOk p n entry
    | _ => true

theorem lookup_mem {fs : List (String × Skel)} {k : String} {s : Skel} (h : fs.lookup k = some s) :
    ∃ k', (k', s) ∈ fs := by
  induction fs with
  | nil => cases h
  | cons f fs ih =>
    simp only [List.lookup] at h
    split at h
    · cases h; exact ⟨f.1, List.mem_cons_self⟩
    · obtain ⟨k', hm⟩ := ih h
      exact ⟨k', List.mem_cons_of_mem _ hm⟩

theorem condsOk_field {p : CaseCond → Bool} {n : Nat} {fs : List (String × Skel)} {ex : Option Skel} {k : String}
    (hf : fs.all (fun f => condsOk p n f.2) = true) (he : ex.all (condsOk p n) = true) :
    condsOk p n (field fs ex k) = true ∨ field fs ex k = .nothing := by
  unfold field
  split
  · rename_i s hs
    left
    obtain ⟨k', hm⟩ := lookup_mem hs
    exact (List.all_eq_true.mp hf) _ hm
  · cases ex with
    | none => right; rfl
    | some e => left; simpa using he

end Skel

namespace Fits

/-- Rows that fit for the case `c` fit for `c'` when every condition of the skeleton that `p`
admits reads the same of both, and `p` admits all of them. -/
theorem congr {p : CaseCond → Bool} {c c' : Json} (hp : ∀ cond, p cond = true → cond.holds c = cond.holds c')
    {k : Skel} {v : Json} (h : Fits c k v) : ∀ n, Skel.condsOk p n k = true → Fits c' k v := by
  induction h with
  | any v => intro _ _; exact Fits.any v
  | strIn hs => intro _ _; exact Fits.strIn hs
  | strNotIn hs => intro _ _; exact Fits.strNotIn hs
  | kindNot hk => intro _ _; exact Fits.kindNot hk
  | obj hv hreq hab ih =>
    intro n hn
    cases n with
    | zero => cases hn
    | succ n =>
      simp only [Skel.condsOk, Bool.and_eq_true] at hn
      refine Fits.obj (fun k v hk => ?_) hreq hab
      rcases Skel.condsOk_field (k := k) hn.1 hn.2 with hc | hc
      · exact ih k v hk n hc
      · have := hv k v hk
        rw [hc] at this
        exact absurd this (nothing_not v)
  | @arr pre items xs hv ih =>
    intro n hn
    cases n with
    | zero => cases hn
    | succ n =>
      simp only [Skel.condsOk, Bool.and_eq_true, List.all_eq_true] at hn
      refine Fits.arr fun i hi => ih i hi n ?_
      unfold Skel.item
      rw [List.getD_eq_getElem?_getD]
      cases h : pre[i]? with
      | none => simpa [h] using hn.2
      | some s => simpa [h] using hn.1 s (List.mem_of_getElem? h)
  | all hs ih =>
    intro n hn
    cases n with
    | zero => cases hn
    | succ n =>
      simp only [Skel.condsOk, List.all_eq_true] at hn
      exact Fits.all fun s hm => ih s hm n (hn s hm)
  | alt hm _ ih =>
    intro n hn
    cases n with
    | zero => cases hn
    | succ n =>
      simp only [Skel.condsOk, List.all_eq_true] at hn
      exact Fits.alt hm (ih n (hn _ hm))
  | onCaseT hc _ ih =>
    intro n hn
    cases n with
    | zero => cases hn
    | succ n =>
      simp only [Skel.condsOk, Bool.and_eq_true] at hn
      exact Fits.onCaseT ((hp _ hn.1.1).symm.trans hc) (ih n hn.1.2)
  | onCaseE hc _ ih =>
    intro n hn
    cases n with
    | zero => cases hn
    | succ n =>
      simp only [Skel.condsOk, Bool.and_eq_true] at hn
      exact Fits.onCaseE ((hp _ hn.1.1).symm.trans hc) (ih n hn.2)
  | softEnvironment D env he hassembly ih =>
    intro n hn
    cases n with
    | zero => cases hn
    | succ n =>
      exact Fits.softEnvironment D env (fun p hm => ih p hm n hn) hassembly
  | rightsEnvironment D env he hd hassembly ih ie =>
    intro n hn
    cases n with
    | zero => cases hn
    | succ n =>
      exact Fits.rightsEnvironment D env (fun p hm => ih p hm n hn)
        (fun p hm => ie p hm n hn) hassembly

end Fits

/-! ## Extraction -/

namespace Skel

def isAny : Skel → Bool
  | .any => true
  | _ => false

def mergeStr (a b : List String) : List String := a ++ b.filter (!a.contains ·)

/-- The conjunction of two skeletons, merged where both are of one kind. `fuel` bounds the
recursion through nested fields. -/
def conj : Nat → Skel → Skel → Skel
  | 0, a, b => .all [a, b]
  | _, .any, b => b
  | _, a, .any => a
  | _, .nothing, _ => .nothing
  | _, _, .nothing => .nothing
  | fuel + 1, .alt as, b => .alt (as.map (conj fuel · b))
  | fuel + 1, a, .alt bs => .alt (bs.map (conj fuel a ·))
  | fuel + 1, .onCase c t e, b => .onCase c (conj fuel t b) (conj fuel e b)
  | fuel + 1, a, .onCase c t e => .onCase c (conj fuel a t) (conj fuel a e)
  | _, .strIn a, .strIn b => .strIn (a.filter b.contains)
  | _, .strIn a, .strNotIn b => .strIn (a.filter (!b.contains ·))
  | _, .strNotIn a, .strIn b => .strIn (b.filter (!a.contains ·))
  | _, .strNotIn a, .strNotIn b => .strNotIn (mergeStr a b)
  | _, .kindNot a, .kindNot b => if a == b then .kindNot a else .all [.kindNot a, .kindNot b]
  | _, .kindNot k, .strIn vs | _, .strIn vs, .kindNot k => if k == "string" then .nothing else .strIn vs
  | _, .kindNot k, .strNotIn vs | _, .strNotIn vs, .kindNot k => .all [.kindNot k, .strNotIn vs]
  | _, .kindNot k, .obj fs ex req ab | _, .obj fs ex req ab, .kindNot k =>
    if k == "object" then .nothing else .obj fs ex req ab
  | _, .kindNot k, .arr pre it | _, .arr pre it, .kindNot k => if k == "array" then .nothing else .arr pre it
  | fuel + 1, .obj fa ea ra aa, .obj fb eb rb ab =>
    let keys := mergeStr (fa.map (·.1)) (fb.map (·.1))
    let side (fs : List (String × Skel)) (e : Option Skel) (k : String) : Option Skel :=
      match fs.lookup k with
      | some s => some s
      | none => e
    let both := keys.filterMap fun k => match side fa ea k, side fb eb k with
      | some x, some y => some (k, conj fuel x y)
      | _, _ => none
    let dropped := keys.filter fun k => (side fa ea k).isNone || (side fb eb k).isNone
    let extra := match ea, eb with
      | some x, some y => some (conj fuel x y)
      | _, _ => none
    .obj both extra (mergeStr ra rb) (mergeStr (mergeStr aa ab) dropped)
  | fuel + 1, .arr pa ia, .arr pb ib =>
    let n := max pa.length pb.length
    .arr ((List.range n).map fun i => conj fuel (pa.getD i ia) (pb.getD i ib)) (conj fuel ia ib)
  | _, .all as, .all bs => .all (as ++ bs)
  | _, .all as, b => .all (as ++ [b])
  | _, a, .all bs => .all (a :: bs)
  | _, _, _ => .nothing

def conjAll (fuel : Nat) (ss : List Skel) : Skel := ss.foldl (conj fuel) .any

/-- The members of an alternative, nested alternatives flattened. -/
def members : Skel → List Skel
  | .alt ss => ss
  | s => [s]

/-- An alternative of which one member is `any` is `any`; one of one member is that member;
nested alternatives are flattened and repeated members dropped. -/
def mkAlt (ss : List Skel) : Skel :=
  let flat := (ss.flatMap members).foldl (fun acc s => if acc.contains s then acc else acc ++ [s]) []
  if flat.any isAny then .any else
    match flat with
    | [s] => s
    | _ => .alt flat

def anyObject : Skel := .obj [] (some .any) [] []

/-- `any` for an array or object of which the skeleton says nothing more (its elements or fields
`any`, no field required or forbidden): the fields are what skeletons describe. -/
def simp : Nat → Skel → Skel
  | 0, k => k
  | fuel + 1, k =>
    match k with
    | .obj fs ex req ab =>
      let fs := fs.map fun (f, v) => (f, simp fuel v)
      let ex := ex.map (simp fuel)
      if fs.all (·.2.isAny) && ex == some .any && req.isEmpty && ab.isEmpty then .any else .obj fs ex req ab
    | .arr pre it =>
      let pre := pre.map (simp fuel)
      let it := simp fuel it
      if pre.all isAny && it.isAny then .any else .arr pre it
    | .all ss => match (ss.map (simp fuel)).filter (!·.isAny) with
      | [] => .any
      | [s] => s
      | ss => .all ss
    | .alt ss => mkAlt (ss.map (simp fuel))
    | .onCase c t e =>
      let t := simp fuel t
      let e := simp fuel e
      if t == e then t else .onCase c t e
    | .encodedEnvironment entry => .encodedEnvironment (simp fuel entry)
    | k => k

/-- The same generated-predicate entry skeleton in every request-selected vocabulary branch.
Extraction fails if the environment shape stops describing these entries or its branches disagree. -/
def environmentEntry : Nat → Skel → Option Skel
  | 0, _ => none
  | fuel + 1, .obj fields _ _ _ =>
    match fields.lookup "predicates" with
    | some (.obj [] (some entry) [] []) => some entry
    | _ => (fields.lookup "vocabulary").bind (environmentEntry fuel)
  | fuel + 1, .onCase _ t e => do
    let a ← environmentEntry fuel t
    let b ← environmentEntry fuel e
    if a == b then some a else none
  | _, _ => none

end Skel

/-- Whether no value valid under `s` needs an object check: no `object`, `required` or object type
is reachable from `s` (through references; `seen` are the references being followed). -/
def objectFree (files : List File) : Nat → List String → Shape → Bool
  | 0, _, _ => false
  | fuel + 1, seen, s =>
    let go := objectFree files fuel seen
    match s with
    | .type ts => !ts.contains "object"
    | .required _ | .object _ _ => false
    | .prefixItems ss | .anyOf ss | .allOf ss => ss.all go
    | .items x | .contains x | .not x | .zip _ x | .rows x | .lean _ x _ | .copied _ x => go x
    | .encodedEnvironment x => go x
    | .ite _ t e => go t && go e
    | .tagged table => table.all fun (_, slots) => slots.all go
    | .select cs => cs.all fun (_, t) => go t
    | .node _ keywords => keywords.all go
    | .ref target =>
      seen.contains target || match lookup files target with
        | some x => objectFree files fuel (target :: seen) x
        | none => false
    | _ => true

/-- The state of an extraction: the references being expanded (a reference to one of them is
recursive, which skeletons do not describe) and the recursive targets met so far. -/
structure Extract where
  stack : List String := []
  recursive : List String := []

/-- A condition on the request case (`x-case`, or an `x-select` entry's `when`) as a `CaseCond`, or
none if the shape is not one of the forms skeletons describe: a kind, a nested field, the absence
of a field, a conjunction, or a runner's test of the case (`decidedCase`). -/
def caseCondOf (files : List File) : Nat → Shape → Option CaseCond
  | 0, _ => none
  | fuel + 1, s =>
    match s with
    | .ref target => (lookup files target).bind (caseCondOf files fuel)
    | .lean name x _ => match CaseDecider.ofName? name with
      | some d => some (.decided d)
      | none => caseCondOf files fuel x
    | .bool true => some (.all [])
    | .allOf ss => (ss.mapM (caseCondOf files fuel)).map .all
    | .node _ [.type ["object"], .required ["kind"], .object [("kind", .const (.str k))] none] => some (.kind k)
    | .node _ [.type ["object"], .not (.required [k])] => some (.lacks k)
    | .required [k] => some (.path [k])
    | .node _ [.required [k]] => some (.path [k])
    | .node _ [.required [k], .object [(k', inner)] none] =>
      if k == k' then (innerPath fuel inner).map fun ks => .path (k :: ks) else none
    | .node _ [.type ["object"], .required [k], .object [(k', inner)] none] =>
      if k == k' then (innerPath fuel inner).map fun ks => .has (k :: ks) else none
    | _ => none
where
  /-- The nested fields an inner object requires: `{"type": "object", "required": [k], ...}`. -/
  innerPath : Nat → Shape → Option (List String)
    | 0, _ => none
    | fuel + 1, s => match s with
      | .node _ [.type ["object"], .required [k]] => some [k]
      | .node _ [.type ["object"], .required [k], .object [(k', inner)] none] =>
        if k == k' then (innerPath fuel inner).map (k :: ·) else none
      | _ => none

/-- The skeleton of a shape in `files`. `cond` marks a condition of an `if`, whose string
values are kept (a field present exactly when another field has one of some values). -/
def skeletonOf (files : List File) : Nat → Bool → Shape → StateT Extract (Except String) Skel
  | 0, _, _ => throw "shape nesting exceeds the skeleton's bound"
  | fuel + 1, cond, s => do
    let go := skeletonOf files fuel
    let conj := Skel.conj fuel
    match s with
    | .bool true => pure .any
    | .bool false => pure .nothing
    | .type ["object"] => pure Skel.anyObject
    | .type ["array"] => pure (.arr [] .any)
    | .type _ => pure .any
    | .const (.str v) => pure (if cond then .strIn [v] else .any)
    | .enum vs => pure (match cond, vs.mapM (fun | .str v => some v | _ => none) with
      | true, some ss => .strIn ss
      | _, _ => .any)
    | .const _ => pure .any
    | .required ks => pure (.obj [] (some .any) ks [])
    | .object ps extra => do
      let fields ← ps.mapM fun (k, v) => do
        -- Keep the branch discriminator even outside an if/then/else. Other constants
        -- are outside the field skeleton's scope; dynamic status enums remain data.
        let statusConst := k == "status" && match v with
          | .const (.str _) => true
          | _ => false
        pure (k, ← go (cond || statusConst) v)
      let extra ← match extra with
        | none => pure (some .any)
        | some (.bool false) => pure none
        | some e => pure (some (← go cond e))
      pure (.obj fields extra [] [])
    | .prefixItems ss => do pure (.arr (← ss.mapM (go cond)) .any)
    | .items x => do pure (.arr [] (← go cond x))
    | .anyOf ss => do pure (Skel.mkAlt (← ss.mapM (go cond)))
    | .allOf ss => do pure (Skel.conjAll fuel (← ss.mapM (go cond)))
    | .not (.required [k]) => pure (.obj [] (some .any) [] [k])
    | .not (.anyOf ss) =>
      match ss.mapM (fun | .required [k] => some k | _ => none) with
      | some ks => pure (.obj [] (some .any) [] ks)
      | none => pure .any
    | .not _ => pure .any
    | .ite (.onCase x) t e => do
      let some c := caseCondOf files depth x
        | throw "a condition on the request case that skeletons do not describe"
      pure (.onCase c (← go cond t) (← go cond e))
    | .ite c t e => do
      let yes ← go true c
      let no ← negation c
      let t ← go cond t
      let e ← go cond e
      if t.isAny && e.isAny then pure .any else pure (Skel.mkAlt [conj yes t, conj no e])
    | .ref target => do
      let st ← get
      if st.stack.contains target then
        unless st.recursive.contains target do set { st with recursive := st.recursive ++ [target] }
        throw s!"a recursive reference {target}; skeletons do not describe it"
      else
        match lookup files target with
        | none => throw s!"unresolved $ref {target}"
        | some x => do
          modify fun st => { st with stack := target :: st.stack }
          let r ← go cond x
          modify fun st => { st with stack := st.stack.drop 1 }
          pure r
    | .tagged table => do
      for (tag, slots) in table do
        unless slots.all (objectFree files depth []) do
          throw s!"a tagged slot of {tag} holds an object; skeletons do not describe it"
      pure .any
    | .fuel _ _ | .echo _ | .equals _ | .length _ | .count _ | .index | .digest | .pattern _
    | .minLength _ | .maxLength _ | .minimum _ | .minItems _ | .maxItems _ | .contains _ | .countWhere _ _ _
    | .onCase _ | .row => pure .any
    | .zip _ x => do pure (.arr [] (← go cond x))
    | .rows x => do pure (.arr [] (← go cond x))
    | .select cs => do
      -- The first entry whose condition the case meets gives the shape; no entry, no value.
      let mut out := Skel.nothing
      for (w, t) in cs.reverse do
        let some c := caseCondOf files depth w
          | throw "a selector on the request case that skeletons do not describe"
        -- An entry every case meets (`true`) ends the selection.
        let k ← go cond t
        out := if c == .all [] then k else .onCase c k out
      pure out
    | .lean _ x _ => go cond x
    | .copied _ _ => pure .any
    | .encodedEnvironment raw => do
      let k ← go cond raw
      let some entry := Skel.environmentEntry depth k
        | throw "the encoded environment has no common generated-predicate entry shape"
      pure (.encodedEnvironment entry)
    | .node _ keywords => do
      let skip := keywords.any fun | .prefixItems _ => true | _ => false
      let parts ← keywords.mapM fun k => match k, skip with
        | .items x, true => do pure (.arr [] (← go cond x))  -- beside prefixItems: the elements after them
        | k, _ => go cond k
      let pre := keywords.findSome? fun | .prefixItems ss => some ss | _ => none
      match pre with
      | some ss =>
        let items := (parts.zip keywords).findSome? fun
          | (.arr [] it, .items _) => some it
          | _ => none
        let rest := (parts.zip keywords).filterMap fun
          | (_, .items _) | (_, .prefixItems _) => none
          | (p, _) => some p
        pure (conj (.arr (← ss.mapM (go cond)) (items.getD .any)) (Skel.conjAll fuel rest))
      | none => pure (Skel.conjAll fuel parts)
where
  /-- A skeleton of every value failing the condition `c`, or `any` where none is expressible. -/
  negation : Shape → StateT Extract (Except String) Skel
    | .object [(k, .const (.str v))] none => pure (.obj [(k, .strNotIn [v])] (some .any) [k] [])
    | .object [(k, .enum vs)] none =>
      match vs.mapM (fun | .str v => some v | _ => none) with
      | some ss => pure (.obj [(k, .strNotIn ss)] (some .any) [k] [])
      | none => pure .any
    | .required [k] => pure (.obj [] (some .any) [] [k])
    -- `{"properties": {k: {"type": "object", "required": rs, "properties": {f: const or string}}}}`
    -- fails exactly when `k` is present and is not an object, lacks one of `rs`, or has one `f`
    -- of another value or type.
    | .object [(k, .node _ [.type ["object"], .required rs, .object ps none])] none =>
      let within (inner : Skel) : Skel := .obj [(k, inner)] (some .any) [k] []
      let fieldNot : String × Shape → Option Skel
        | (f, .const (.str v)) => some (within (.obj [(f, .strNotIn [v])] (some .any) [f] []))
        | (f, .type ["string"]) => some (within (.obj [(f, .kindNot "string")] (some .any) [f] []))
        | _ => none
      match ps.mapM fieldNot with
      | some fs => pure (Skel.mkAlt ([within (.kindNot "object")] ++
          rs.map (fun r => within (.obj [] (some .any) [] [r])) ++ fs))
      | none => pure .any
    | _ => pure .any

/-- The skeleton of the shape at `target`, and the recursive targets it names. -/
def skeleton (files : List File) (target : String) : Except String (Skel × List String) := do
  match lookup files target with
  | none => throw s!"unresolved $ref {target}"
  | some s =>
    let (k, st) ← (skeletonOf files depth false s).run { stack := [target] }
    pure (Skel.simp depth k, st.recursive)

end ResponseShape
