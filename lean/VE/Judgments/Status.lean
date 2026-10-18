import VE.Judgments.Decl
import VE.Judgments.Scan
import VE.Closure.Paths

/-! Judgment terms: dependence, status and the usage map (docs/spec/judgment-terms.md section 4). A unit's content
depends on a bound judgment when it uses it, directly or through W3 definitions; judgment dependence forces OPEN,
otherwise today's status applies. This file does not import `VE.Service.Document`: the document mode (JT-2) maps its
`UnitContent` onto `Content`. -/

namespace VE.Judgments

/-! ### Dependence (D4) -/

/-- What one content reads: a formula, or a rule (its guard and carve-outs, as rights' `nodeOpen` reads them). -/
inductive Content
  | formula (φ : VE.Formula)
  | rule (N : VE.Norms.Node)
  deriving DecidableEq, Repr

def Content.formulas : Content → List VE.Formula
  | .formula φ => [φ]
  | .rule N => N.guard :: N.carveOuts

/-- The definition graph: a defined name points at each predicate of its body. -/
def defEdges (defs : List VE.Definitions.Def) : List (String × String) :=
  defs.flatMap fun d => (VE.Norms.preds d.body).map (d.name, ·)

/-- The bodies of the definitions the formulas reach: each definition whose name a formula mentions, or reaches
    through other definitions. -/
def reachedBodies (defs : List VE.Definitions.Def) (fs : List VE.Formula) : List VE.Formula :=
  let ps := fs.flatMap VE.Norms.preds
  (defs.filter fun d => ps.any fun p => p == d.name || VE.Closure.reachEval .plus (defEdges defs) p d.name).map
    (·.body)

/-- The judgments the formulas depend on: used directly, or reached through W3 definitions. One scan, `opensIn`. -/
def dependsOn (defs : List VE.Definitions.Def) (J : List String) (fs : List VE.Formula) : List String :=
  opensIn J (fs ++ reachedBodies defs fs)

/-- A positive path ends with an edge. -/
theorem path_last {α : Type} {R : α → α → Prop} {a c : α} (h : VE.Closure.Path R a c) :
    R a c ∨ ∃ b, VE.Closure.Path R a b ∧ R b c := by
  induction h with
  | edge h => exact .inl h
  | @cons a b c h _ ih =>
    rcases ih with h' | ⟨b', p, r⟩
    · exact .inr ⟨b, .edge h, h'⟩
    · exact .inr ⟨b', .cons h p, r⟩

theorem mem_defEdges (defs : List VE.Definitions.Def) (a b : String) :
    (a, b) ∈ defEdges defs ↔ ∃ d ∈ defs, d.name = a ∧ b ∈ VE.Norms.preds d.body := by
  simp only [defEdges, List.mem_flatMap, List.mem_map, Prod.mk.injEq]
  constructor
  · rintro ⟨d, hd, x, hx, rfl, rfl⟩; exact ⟨d, hd, rfl, hx⟩
  · rintro ⟨d, hd, rfl, hb⟩; exact ⟨d, hd, b, hb, rfl, rfl⟩

theorem dependsOn_iff (defs J fs j) :
    j ∈ dependsOn defs J fs ↔
      j ∈ J ∧ ∃ φ ∈ fs, ∃ p ∈ VE.Norms.preds φ, p = j ∨
        VE.Closure.Reachable .plus (fun a b => (a, b) ∈ defEdges defs) p j := by
  simp only [dependsOn, opensIn_iff, List.mem_append, reachedBodies, List.mem_map, List.mem_filter,
    List.any_eq_true, List.mem_flatMap, Bool.or_eq_true, beq_iff_eq, VE.Closure.reachEval_iff]
  refine and_congr_right fun _ => ?_
  constructor
  · rintro ⟨φ, hφ | ⟨d, ⟨hd, p, ⟨ψ, hψ, hp⟩, hreach⟩, rfl⟩, hj⟩
    · exact ⟨φ, hφ, j, hj, .inl rfl⟩
    · have he : (d.name, j) ∈ defEdges defs := (mem_defEdges defs _ _).mpr ⟨d, hd, rfl, hj⟩
      refine ⟨ψ, hψ, p, hp, .inr ?_⟩
      rcases hreach with rfl | hr
      · exact .edge he
      · exact VE.Closure.Path.trans hr (.edge he)
  · rintro ⟨φ, hφ, p, hp, rfl | hr⟩
    · exact ⟨φ, .inl hφ, hp⟩
    · rcases path_last hr with he | ⟨b, hpb, he⟩
      · obtain ⟨d, hd, rfl, hj⟩ := (mem_defEdges defs _ _).mp he
        exact ⟨d.body, .inr ⟨d, ⟨hd, d.name, ⟨φ, hφ, hp⟩, .inl rfl⟩, rfl⟩, hj⟩
      · obtain ⟨d, hd, rfl, hj⟩ := (mem_defEdges defs _ _).mp he
        exact ⟨d.body, .inr ⟨d, ⟨hd, p, ⟨φ, hφ, hp⟩, .inr hpb⟩, rfl⟩, hj⟩

/-- Without definitions, dependence is the direct scan. -/
theorem dependsOn_no_defs (J fs) : dependsOn [] J fs = opensIn J fs := by
  simp [dependsOn, reachedBodies]

/-- The judgments a list of contents depends on. -/
def dependsOnC (defs : List VE.Definitions.Def) (J : List String) (cs : List Content) : List String :=
  dependsOn defs J (cs.flatMap Content.formulas)

theorem dependsOnC_sub (defs J cs j) (h : j ∈ dependsOnC defs J cs) : j ∈ J :=
  ((dependsOn_iff defs J _ j).mp h).1

/-! ### One traversal per unit (plan fix 2) -/

/-- The active reading set of a unit, as the loader folds it: its two flags and its candidates, in order; a pending
    reading (`content: null`) is `none`. -/
structure ActiveSet where
  authored    : Bool
  allAsserted : Bool
  candidates  : List (Option Content)
  deriving DecidableEq, Repr

/-- A unit as the status reads it. `meaning` is `Loader.meaningStatus`'s value; `listed` the names of an `open`
    meaning (empty otherwise); `asserted` whether the unit's kind is `asserted`. -/
structure UnitView where
  id       : String
  meaning  : String
  listed   : List String
  asserted : Bool
  own      : Option Content
  set      : Option ActiveSet
  deriving DecidableEq, Repr

/-- The one list a unit's status and usage read: the active set's elaborated candidates, or the unit's own content. -/
def UnitView.reads (u : UnitView) : List Content :=
  match u.set with
  | some s => s.candidates.filterMap fun c => c
  | none => u.own.toList

/-- Whether `reads` is all the unit's content, so that a listed judgment it does not use is really unused. With an
    active set (which takes precedence, as in `reads`): the set has a reading and none is pending, whatever the unit's
    own content. Without one: the unit has its own content. -/
def UnitView.complete (u : UnitView) : Bool :=
  match u.set with
  | some s => !s.candidates.isEmpty && s.candidates.all Option.isSome
  | none => u.own.isSome

/-- Today's status: `w2SetStatus` with an active set, `w2Status` without. -/
def UnitView.legacy (u : UnitView) : String :=
  match u.set with
  | some s => VE.Discourse.Loader.w2SetStatus s.authored s.allAsserted
  | none => VE.Discourse.Loader.w2Status u.own.isSome u.meaning

/-- A unit's view: the active set is the one `Loader.foldStatus` finds in `Loader.activeOf`'s list. -/
def viewOf (active : List (VE.Discourse.FrontSet × List Bool))
    (candidates : VE.Discourse.FrontSet → List (Option Content))
    (unit meaning : String) (listed : List String) (asserted : Bool) (own : Option Content) : UnitView :=
  { id := unit, meaning, listed, asserted, own,
    set := (active.find? (·.1.unit == unit)).map fun (rs, kinds) =>
      ⟨rs.status == "authored", kinds.all id, candidates rs⟩ }

theorem viewOf_legacy (active candidates unit meaning listed asserted own) :
    (viewOf active candidates unit meaning listed asserted own).legacy =
      VE.Discourse.Loader.foldStatus active unit (VE.Discourse.Loader.w2Status own.isSome meaning) := by
  simp only [viewOf, UnitView.legacy, VE.Discourse.Loader.foldStatus]
  cases active.find? (·.1.unit == unit) <;> rfl

/-! ### Status (D3) -/

/-- The status under `judgments@0`: the unit refusals of plan 2.1, item 6, in that order (the third only on a
    complete unit), then OPEN if the unit's list depends on a bound judgment, else today's status. -/
def status (defs : List VE.Definitions.Def) (J : List String) (u : UnitView) : Except String String := do
  let deps := dependsOnC defs J u.reads
  if u.meaning == "specified" then
    if let some j := deps.head? then throw s!"JudgmentNotChecked: {u.id} {j}"
  if u.meaning == "open" then
    if let some j := deps.find? (!u.listed.contains ·) then throw s!"JudgmentNotListed: {u.id} {j}"
    if u.complete then
      if let some j := u.listed.find? (fun j => J.contains j && !deps.contains j) then
        throw s!"JudgmentListedUnused: {u.id} {j}"
  pure (if deps.isEmpty then u.legacy else "OPEN")

/-- The value: judgment dependence forces OPEN; otherwise the legacy status applies. -/
theorem status_eq (defs J u s) (h : status defs J u = .ok s) :
    s = if dependsOnC defs J u.reads = [] then u.legacy else "OPEN" := by
  have hv : (if (dependsOnC defs J u.reads).isEmpty = true then u.legacy else "OPEN") =
      if dependsOnC defs J u.reads = [] then u.legacy else "OPEN" := by simp [List.isEmpty_iff]
  rw [← hv]
  revert h
  unfold status
  generalize dependsOnC defs J u.reads = deps
  simp only [bind, Except.bind, pure, Except.pure]
  generalize (if deps.isEmpty = true then u.legacy else "OPEN") = v
  have hok : (Except.ok v : Except String String) = .ok s → s = v := fun h => by cases h; rfl
  have herr : ∀ e, (Except.error e : Except String String) = .ok s → s = v := fun _ h => by cases h
  cases u.meaning == "specified" <;> cases deps.head? <;> cases u.meaning == "open" <;>
    cases deps.find? (!u.listed.contains ·) <;> cases u.complete <;>
    cases u.listed.find? (fun j => J.contains j && !deps.contains j) <;>
    simp only [Bool.false_eq_true, if_false, if_true] <;> first | exact hok | exact herr _

/-- "Never present a judgment as checked": a judgment used in the unit's own content or its definitions. -/
theorem status_never_checked (defs J u s) (h : status defs J u = .ok s) (hd : dependsOnC defs J u.reads ≠ []) :
    s = "OPEN" := by
  rw [status_eq defs J u s h, if_neg hd]

theorem status_checked (defs J u) (h : status defs J u = .ok "CHECKED") : dependsOnC defs J u.reads = [] := by
  have := status_eq defs J u _ h
  split at this
  · assumption
  · exact absurd this (by decide)

/-- The refusals, exactly: `specified` content uses no judgment, and an `open` list names every judgment the content
    depends on and, when the unit is complete, no bound judgment it does not. -/
theorem status_ok_iff (defs J u) :
    (∃ s, status defs J u = .ok s) ↔
      (u.meaning = "specified" → dependsOnC defs J u.reads = []) ∧
      (u.meaning = "open" → (∀ j ∈ dependsOnC defs J u.reads, j ∈ u.listed) ∧
        (u.complete = true → ∀ j ∈ u.listed, j ∈ J → j ∈ dependsOnC defs J u.reads)) := by
  unfold status
  generalize dependsOnC defs J u.reads = deps
  simp only [bind, Except.bind, pure, Except.pure]
  generalize (if deps.isEmpty = true then u.legacy else "OPEN") = v
  have hok : ∃ s, (Except.ok v : Except String String) = .ok s := ⟨v, rfl⟩
  have herr : ∀ e, ¬ ∃ s, (Except.error e : Except String String) = .ok s := by
    rintro e ⟨s, h⟩; cases h
  by_cases hs : u.meaning = "specified"
  · have ho : (u.meaning == "open") = false := by simp [hs]
    have hs' : (u.meaning == "specified") = true := by simp [hs]
    have hne : u.meaning ≠ "open" := by simp [hs]
    simp only [hs', ho, if_true, Bool.false_eq_true, if_false]
    cases hd : deps.head? with
    | none =>
      simp only [List.head?_eq_none_iff] at hd
      exact iff_of_true hok ⟨fun _ => hd, fun h => absurd h hne⟩
    | some j =>
      have hn : deps ≠ [] := by intro h; simp [h] at hd
      exact iff_of_false (herr _) fun h => hn (h.1 hs)
  · have hs' : (u.meaning == "specified") = false := by simp [hs]
    simp only [hs', Bool.false_eq_true, if_false]
    by_cases ho : u.meaning = "open"
    · have ho' : (u.meaning == "open") = true := by simp [ho]
      simp only [ho', if_true]
      cases hf : deps.find? (!u.listed.contains ·) with
      | some j =>
        have hj := List.find?_some hf
        have hm := List.mem_of_find?_eq_some hf
        refine iff_of_false (herr _) fun h => ?_
        have := (h.2 ho).1 j hm
        simp [this] at hj
      | none =>
        have hall := List.find?_eq_none.mp hf
        have hlist : ∀ j ∈ deps, j ∈ u.listed := fun j hj => by simpa using hall j hj
        cases hc : u.complete with
        | false =>
          exact iff_of_true hok ⟨fun h => absurd h hs, fun _ => ⟨hlist, fun h => absurd h (by simp)⟩⟩
        | true =>
          simp only [if_true]
          cases hg : u.listed.find? (fun j => J.contains j && !deps.contains j) with
          | some j =>
            have hj := List.find?_some hg
            have hm := List.mem_of_find?_eq_some hg
            refine iff_of_false (herr _) fun h => ?_
            simp only [Bool.and_eq_true, Bool.not_eq_true', List.contains_iff_mem] at hj
            have := (h.2 ho).2 trivial j hm (by simpa using hj.1)
            simp [this] at hj
          | none =>
            have hall' := List.find?_eq_none.mp hg
            refine iff_of_true hok ⟨fun h => absurd h hs, fun _ => ⟨hlist, fun _ j hj hJ => ?_⟩⟩
            have := hall' j hj
            simp only [Bool.and_eq_true, Bool.not_eq_true', List.contains_iff_mem, not_and,
              Bool.not_eq_false] at this
            simpa using this (by simpa using hJ)
    · have ho' : (u.meaning == "open") = false := by simp [ho]
      simp only [ho', Bool.false_eq_true, if_false]
      exact iff_of_true hok ⟨fun h => absurd h hs, fun h => absurd h ho⟩

/-- Without bound judgments, today's status. -/
theorem status_legacy (defs u) : status defs [] u = .ok u.legacy := by
  have hf : u.listed.find? (fun _ => false) = none := List.find?_eq_none.mpr (by simp)
  simp [status, dependsOnC, dependsOn, opensIn]
  split
  · split
    · rw [hf]; rfl
    · rfl
  · rfl

/-! ### The usage map (plan 2.2) -/

/-- For each bound judgment that some unit depends on, the ids of those units, in unit order; then the bound
    judgments no unit depends on. Both in declaration order. -/
def usageMap (defs : List VE.Definitions.Def) (J : List String) (units : List UnitView) :
    List (String × List String) × List String :=
  let rows := J.map fun j => (j, (units.filter fun u => (dependsOnC defs J u.reads).contains j).map (·.id))
  (rows.filter (!·.2.isEmpty), (rows.filter (·.2.isEmpty)).map (·.1))

theorem usageMap_sound (defs J units j ids) (h : (j, ids) ∈ (usageMap defs J units).1) (id) (hid : id ∈ ids) :
    ∃ u ∈ units, u.id = id ∧ j ∈ dependsOnC defs J u.reads := by
  simp only [usageMap, List.mem_filter, List.mem_map, Prod.mk.injEq] at h
  obtain ⟨⟨j', _, rfl, rfl⟩, _⟩ := h
  simp only [List.mem_map, List.mem_filter, List.contains_iff_mem] at hid
  obtain ⟨u, ⟨hu, hj⟩, rfl⟩ := hid
  exact ⟨u, hu, rfl, hj⟩

theorem usageMap_complete (defs J units u j) (hu : u ∈ units) (hj : j ∈ dependsOnC defs J u.reads) :
    ∃ ids, (j, ids) ∈ (usageMap defs J units).1 ∧ u.id ∈ ids := by
  have hm : u.id ∈ (units.filter fun v => (dependsOnC defs J v.reads).contains j).map (·.id) :=
    List.mem_map.mpr ⟨u, List.mem_filter.mpr ⟨hu, List.contains_iff_mem.mpr hj⟩, rfl⟩
  refine ⟨_, ?_, hm⟩
  simp only [usageMap, List.mem_filter, List.mem_map]
  refine ⟨⟨j, dependsOnC_sub defs J _ j hj, rfl⟩, ?_⟩
  simp only [Bool.not_eq_true', List.isEmpty_eq_false_iff_exists_mem]
  exact ⟨_, hm⟩

theorem usageMap_unused (defs J units j) :
    j ∈ (usageMap defs J units).2 ↔ j ∈ J ∧ ∀ u ∈ units, j ∉ dependsOnC defs J u.reads := by
  simp [usageMap, List.filter_eq_nil_iff]
  constructor
  · rintro ⟨a, ha, rfl, h⟩; exact ⟨ha, h⟩
  · rintro ⟨ha, h⟩; exact ⟨j, ha, rfl, h⟩

/-- No row is empty. -/
theorem usageMap_rows (defs J units j ids) (h : (j, ids) ∈ (usageMap defs J units).1) : ids ≠ [] := by
  simp only [usageMap, List.mem_filter] at h
  intro hn
  simp [hn] at h

/-! ### Removing a judgment no unit uses (plan JT-5) -/

/-- A list lemma for `dependsOnC_remove`: removing a name the filter does not keep changes nothing it keeps. -/
theorem filter_remove (J : List String) (P : String → Bool) (j : String) (h : j ∉ J.filter P) :
    (J.filter (· != j)).filter P = J.filter P := by
  rw [List.filter_filter]
  apply List.filter_congr
  intro a ha
  by_cases hj : a = j
  · subst hj
    have hp : P a = false := by
      cases hp : P a
      · rfl
      · exact absurd (List.mem_filter.mpr ⟨ha, hp⟩) h
    simp [hp]
  · simp [hj]

/-- Removing a bound judgment that the content does not depend on leaves the dependence unchanged. -/
theorem dependsOnC_remove (defs J cs j) (h : j ∉ dependsOnC defs J cs) :
    dependsOnC defs (J.filter (· != j)) cs = dependsOnC defs J cs := by
  unfold dependsOnC dependsOn opensIn at *
  exact filter_remove _ _ _ h

theorem find_congr_mem {l : List String} {p q : String → Bool} (h : ∀ x ∈ l, p x = q x) : l.find? p = l.find? q := by
  induction l with
  | nil => rfl
  | cons a l ih => simp only [List.find?_cons, h a (by simp), ih (fun x hx => h x (by simp [hx]))]

/-- Plan JT-5's removal: a judgment that the unit's content does not depend on (directly or through W3 definitions)
    and that its meaning does not list can be removed without changing the unit's status or refusal. -/
theorem status_remove_unused (defs J u j) (hd : j ∉ dependsOnC defs J u.reads) (hl : j ∉ u.listed) :
    status defs (J.filter (· != j)) u = status defs J u := by
  have hfind : u.listed.find? (fun x => (J.filter (· != j)).contains x && !(dependsOnC defs J u.reads).contains x) =
      u.listed.find? (fun x => J.contains x && !(dependsOnC defs J u.reads).contains x) := by
    apply find_congr_mem
    intro x hx
    have hxj : x ≠ j := fun e => hl (e ▸ hx)
    simp [List.mem_filter, hxj]
  simp only [status, dependsOnC_remove defs J u.reads j hd, hfind]

end VE.Judgments
