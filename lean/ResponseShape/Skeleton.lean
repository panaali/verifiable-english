import ResponseShape
import Std.Data.TreeMap.Raw.Lemmas
import Std.Data.TreeMap.Raw.WF
import Lean.ToExpr

/-! # Skeletons: the fields of a shape, for the theorems that tie each encoder to its shape

A `Skel` is what a `Shape` says about the fields of the objects in a value: for each object
its allowed fields (each with the skeleton of its value), the fields it requires and the
fields it forbids, through arrays, alternatives and references; and, where a field's presence
depends on another field's string value (an `if`/`then`/`else`), that value. Everything else a
shape checks (patterns, numbers, echoes, counts, grammars without objects) is `any` here.

`skeleton files s` extracts the skeleton of a shape. It describes at least every value valid
under the shape (it may allow more: a condition it cannot express is dropped, never
strengthened), and it keeps every field list: an object closed by `additionalProperties:
false` is closed here with exactly its properties, and its `required` list is required.

`Fits Γ k v` says that the JSON value `v` has the fields `k` describes (`Γ` names the
skeletons of recursive references). The theorems of `ResponseShape.Encoders` prove, for every
service mode, that every row its runner returns fits the skeleton of the mode's row shape, so
a field an encoder adds or drops, or a shape that lists another field, fails the build. -/

namespace ResponseShape
open Lean

inductive Skel where
  /-- Any value. -/
  | any
  /-- No value (the value of a field a closed object does not allow). -/
  | nothing
  /-- A string among these. -/
  | strIn (vs : List String)
  /-- Any value but a string among these. -/
  | strNotIn (vs : List String)
  /-- An object: a field of `fields` has a value fitting its skeleton, any other field one
  fitting `extra` (none: no other field); `required` are present, `absent` are not. -/
  | obj (fields : List (String × Skel)) (extra : Option Skel) (required : List String) (absent : List String)
  /-- An array: element `i` fits `pre[i]`, and every element after `pre` fits `items`. -/
  | arr (pre : List Skel) (items : Skel)
  | all (ss : List Skel)
  | alt (ss : List Skel)
  /-- A recursive reference, named in `Γ`. -/
  | ref (target : String)
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

inductive Fits (Γ : String → Skel) : Skel → Json → Prop where
  | any (v : Json) : Fits Γ .any v
  | strIn {vs : List String} {s : String} : s ∈ vs → Fits Γ (.strIn vs) (.str s)
  | strNotIn {vs : List String} {v : Json} : (∀ s, v = .str s → s ∉ vs) → Fits Γ (.strNotIn vs) v
  | obj {fields : List (String × Skel)} {extra : Option Skel} {required absent : List String}
      {m : Std.TreeMap.Raw String Json} :
      (∀ k v, m[k]? = some v → Fits Γ (Skel.field fields extra k) v) →
      (∀ k ∈ required, k ∈ m) → (∀ k ∈ absent, k ∉ m) →
      Fits Γ (.obj fields extra required absent) (.obj m)
  | arr {pre : List Skel} {items : Skel} {xs : Array Json} :
      (∀ i (h : i < xs.size), Fits Γ (Skel.item pre items i) xs[i]) → Fits Γ (.arr pre items) (.arr xs)
  | all {ss : List Skel} {v : Json} : (∀ s ∈ ss, Fits Γ s v) → Fits Γ (.all ss) v
  | alt {ss : List Skel} {s : Skel} {v : Json} : s ∈ ss → Fits Γ s v → Fits Γ (.alt ss) v
  | ref {target : String} {v : Json} : Fits Γ (Γ target) v → Fits Γ (.ref target) v

namespace Fits

variable {Γ : String → Skel}

theorem nothing_not (v : Json) : ¬ Fits Γ .nothing v := by
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
theorem ofList_get' {l : List (String × Json)} {k : String} {v : Json}
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
theorem mkObjExtra {s : Skel} {l : List (String × Json)} (hv : ∀ p ∈ l, Fits Γ s p.2) :
    Fits Γ (.obj [] (some s) [] []) (Json.mkObj l) := by
  refine Fits.obj (fun k v h => ?_) (fun _ h => by cases h) (fun _ h => by cases h)
  obtain ⟨k', hm⟩ := ofList_get' h
  exact hv _ hm

/-- An object built from a list of fields (`Json.mkObj`): its field names pass `keysOk` and each
value fits the skeleton of its field. -/
theorem mkObj {fields : List (String × Skel)} {extra : Option Skel} {required absent : List String}
    {l : List (String × Json)} (hk : Skel.keysOk fields extra required absent (l.map Prod.fst) = true)
    (hv : ∀ p ∈ l, Fits Γ (Skel.field fields extra p.1) p.2) :
    Fits Γ (.obj fields extra required absent) (Json.mkObj l) := by
  simp only [Skel.keysOk, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hk
  obtain ⟨⟨⟨hd, _⟩, hreq⟩, hab⟩ := hk
  refine Fits.obj (fun k v h => hv (k, v) (ofList_get hd h)) (fun k hk => ?_) (fun k hk => ?_)
  · exact Std.TreeMap.Raw.mem_ofList.mpr (hreq k hk)
  · intro hm
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
    (hv : ∀ p ∈ l.filter (·.1 != k), Fits Γ (Skel.field fields extra p.1) p.2)
    (hkv : Fits Γ (Skel.field fields extra k) v) :
    Fits Γ (.obj fields extra required absent) ((Json.mkObj l).setObjVal! k v) := by
  simp only [Skel.distinct, Bool.and_eq_true, decide_eq_true_eq, Skel.keysOk, List.all_eq_true] at hk
  obtain ⟨hd, ⟨⟨_, _⟩, hreq⟩, hab⟩ := hk
  have wf : (Std.TreeMap.Raw.ofList l compare).WF := Std.TreeMap.Raw.WF.ofList
  refine Fits.obj (fun k' v' h => ?_) (fun k' hk' => ?_) (fun k' hk' => ?_)
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
theorem arrMap {α : Type} {items : Skel} {xs : List α} {f : α → Json} (h : ∀ x ∈ xs, Fits Γ items (f x)) :
    Fits Γ (.arr [] items) (Json.arr (xs.map f).toArray) := by
  refine Fits.arr fun i hi => ?_
  simp only [Skel.item, List.getD_nil, List.getElem_toArray, List.getElem_map]
  exact h _ (List.getElem_mem _)

theorem arrList {items : Skel} {xs : List Json} (h : ∀ x ∈ xs, Fits Γ items x) :
    Fits Γ (.arr [] items) (Json.arr xs.toArray) := by
  have := arrMap (Γ := Γ) (f := id) h
  simpa using this

theorem altHead {s : Skel} {ss : List Skel} {v : Json} (h : Fits Γ s v) : Fits Γ (.alt (s :: ss)) v :=
  Fits.alt List.mem_cons_self h

theorem altTail {s : Skel} {ss : List Skel} {v : Json} (h : Fits Γ (.alt ss) v) : Fits Γ (.alt (s :: ss)) v := by
  cases h with
  | alt hm h => exact Fits.alt (List.mem_cons_of_mem _ hm) h

theorem strIn_lit {vs : List String} {s : String} (h : vs.contains s = true) : Fits Γ (.strIn vs) (.str s) :=
  Fits.strIn (by simpa using h)

theorem strNotIn_lit {vs : List String} {s : String} (h : vs.contains s = false) :
    Fits Γ (.strNotIn vs) (.str s) :=
  Fits.strNotIn fun t ht => by
    cases ht
    simpa using h

/-- An array whose every element fits `items`. -/
theorem arrOf {items : Skel} {a : Array Json} (h : ∀ x ∈ a, Fits Γ items x) : Fits Γ (.arr [] items) (.arr a) :=
  Fits.arr fun i hi => by
    simp only [Skel.item, List.getD_nil]
    exact h _ (Array.getElem_mem hi)

/-- The alternative `n` of `ss` is an object skeleton the fields of `l` pass. -/
theorem mkObjAlt {ss : List Skel} (n : Nat) {fields : List (String × Skel)} {extra : Option Skel}
    {required absent : List String} {l : List (String × Json)}
    (hn : ss[n]? = some (.obj fields extra required absent))
    (hk : Skel.keysOk fields extra required absent (l.map Prod.fst) = true)
    (hv : ∀ p ∈ l, Fits Γ (Skel.field fields extra p.1) p.2) : Fits Γ (.alt ss) (Json.mkObj l) :=
  Fits.alt (List.mem_of_getElem? hn) (mkObj hk hv)

/-- The alternative `n` of `ss` is an object skeleton the fields of `(Json.mkObj l).setObjVal! k v` pass. -/
theorem setObjAlt {ss : List Skel} (n : Nat) {fields : List (String × Skel)} {extra : Option Skel}
    {required absent : List String} {l : List (String × Json)} {k : String} {v : Json}
    (hn : ss[n]? = some (.obj fields extra required absent))
    (hk : (Skel.distinct (l.map Prod.fst) && Skel.keysOk fields extra required absent
      (k :: (l.map Prod.fst).filter (· != k))) = true)
    (hv : ∀ p ∈ l.filter (·.1 != k), Fits Γ (Skel.field fields extra p.1) p.2)
    (hkv : Fits Γ (Skel.field fields extra k) v) : Fits Γ (.alt ss) ((Json.mkObj l).setObjVal! k v) :=
  Fits.alt (List.mem_of_getElem? hn) (setObj hk hv hkv)

/-- Every member of `ss` is one of `ts`: a value fitting `ss` fits `ts` (a runner delegating to
another mode's runner). -/
theorem altSub {ss ts : List Skel} {v : Json} (hs : ∀ s ∈ ss, s ∈ ts) (h : Fits Γ (.alt ss) v) :
    Fits Γ (.alt ts) v := by
  cases h with
  | alt hm h => exact Fits.alt (hs _ hm) h

theorem ofAlt {s : Skel} {ss : List Skel} {v : Json} (hs : s ∈ ss) (h : Fits Γ s v) : Fits Γ (.alt ss) v :=
  Fits.alt hs h

end Fits

/-- `∀ v, r = .ok v → P v`: every result a computation returns satisfies `P`. -/
def OkP {α : Type} (P : α → Prop) (r : Except String α) : Prop := ∀ v, r = .ok v → P v

/-- Every result a runner returns fits `k`. -/
abbrev OkFits (Γ : String → Skel) (k : Skel) (r : Except String Json) : Prop := OkP (Fits Γ k) r

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

theorem of {r : Except String α} {Q : α → Prop} (h : OkP Q r) (hq : ∀ v, Q v → P v) : OkP P r :=
  fun v hv => hq v (h v hv)

end OkP

theorem isEmpty_empty : ("" : String).isEmpty = true := rfl

theorem getArr?_arr (a : Array Json) : (Json.arr a).getArr? = .ok a := rfl

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
  | _, .strIn a, .strIn b => .strIn (a.filter b.contains)
  | _, .strIn a, .strNotIn b => .strIn (a.filter (!b.contains ·))
  | _, .strNotIn a, .strIn b => .strIn (b.filter (!a.contains ·))
  | _, .strNotIn a, .strNotIn b => .strNotIn (mergeStr a b)
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
  | _, .ref t, b => .all [.ref t, b]
  | _, a, .ref t => .all [a, .ref t]
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
    | k => k

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
recursive and stays a `ref`) and the recursive targets met so far. -/
structure Extract where
  stack : List String := []
  recursive : List String := []

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
      let fields ← ps.mapM fun (k, v) => do pure (k, ← go cond v)
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
        pure (.ref target)
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
    | .select cs => do pure (Skel.mkAlt (← cs.mapM fun (_, t) => go cond t))
    | .lean _ x _ => go cond x
    | .copied _ _ => pure .any
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
    | _ => pure .any

/-- The skeleton of the shape at `target`, and the recursive targets it names. -/
def skeleton (files : List File) (target : String) : Except String (Skel × List String) := do
  match lookup files target with
  | none => throw s!"unresolved $ref {target}"
  | some s =>
    let (k, st) ← (skeletonOf files depth false s).run { stack := [target] }
    pure (Skel.simp depth k, st.recursive)

end ResponseShape
