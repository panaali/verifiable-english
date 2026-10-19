import VE.Discourse.Loader
import VE.Definitions.Layer

/-! Judgment terms (`judgments@0`), W2 records and admission (docs/spec/judgment-terms.md sections 1 and 2). A
judgment term is a W2 open term whose name is a base predicate with the record's sorts. W2's validator
(`Loader.openTermNames`, with `sorts := true`) stays the one check of the record; `records` then reads the fields it
checked, and `admit` binds each record to the base vocabulary `hide E (names defs)`. -/

namespace VE.Judgments
open Lean

/-- A bound judgment: a W2 open term whose name is a base predicate (D1, D2). `factors` are shown, never premises. -/
structure Judgment where
  name      : String
  arguments : List String
  decidedBy : String
  factors   : List String
  deriving DecidableEq, Repr

/-- One record as written, after W2's check: the judgment and the lengths of `necessary` and `sufficient`. -/
abbrev Rec := Judgment × Nat × Nat

/-- The records of `open_terms` under the profile: W2's check first (with `python`, and repeated sorts allowed),
then the fields it checked. -/
def records (rv : VE.Route.Wire.RouteVocabulary) (j : Json) (data : Bool)
    (formula : Option (Json → Except String Unit)) : Except String (List Rec) := do
  let names ← VE.Discourse.Loader.openTermNames rv j (python := true) (data := data) (formula := formula)
    (sorts := true)
  let items := match j with
    | .arr xs => xs.toList
    | _ => []
  let str := fun (item : Json) (k : String) => (item.getObjValD k).getStr?.toOption.getD ""
  let strs := fun (item : Json) (k : String) => (VE.Bridge.strings (item.getObjValD k)).toOption.getD []
  let len := fun (item : Json) (k : String) => ((item.getObjValD k).getArr?.toOption.getD #[]).size
  pure ((items.zip names).map fun (item, name) =>
    (⟨name, strs item "arguments", str item "decided_by", strs item "factors"⟩,
      len item "necessary", len item "sufficient"))

/-! ### W2's fold, read through its steps -/

/-- A fold whose steps keep every answer of `F` keeps every answer of the fold. -/
theorem foldlM_ok_mono {ε α β : Type} {F G : β → α → Except ε β}
    (hFG : ∀ b a s, F b a = .ok s → G b a = .ok s) :
    ∀ (L : List α) (b s : β), L.foldlM F b = .ok s → L.foldlM G b = .ok s := by
  intro L
  induction L with
  | nil => intro b s h; exact h
  | cons a rest ih =>
    intro b s h
    simp only [List.foldlM_cons, bind, Except.bind] at h ⊢
    cases hF : F b a with
    | error e => rw [hF] at h; cases h
    | ok c => rw [hF] at h; rw [hFG b a c hF]; exact ih c s h

/-- A fold whose steps each add one name adds one name per item. -/
theorem foldlM_ok_length {ε α : Type} {F : List String → α → Except ε (List String)}
    (hF : ∀ b a s, F b a = .ok s → s.length = b.length + 1) :
    ∀ (L : List α) (b s : List String), L.foldlM F b = .ok s → s.length = b.length + L.length := by
  intro L
  induction L with
  | nil => intro b s h; cases h; rfl
  | cons a rest ih =>
    intro b s h
    simp only [List.foldlM_cons, bind, Except.bind] at h
    cases hc : F b a with
    | error e => rw [hc] at h; cases h
    | ok c => rw [hc] at h; rw [ih c s h, hF b a c hc, List.length_cons]; omega

/-- The flag only relaxes: what W2 admits without it, it admits with it, with the same names. -/
theorem openTermNames_sorts (rv j python data formula ns)
    (h : VE.Discourse.Loader.openTermNames rv j python data formula (sorts := false) = .ok ns) :
    VE.Discourse.Loader.openTermNames rv j python data formula (sorts := true) = .ok ns := by
  unfold VE.Discourse.Loader.openTermNames at *
  cases j <;> try (simp [bind, Except.bind] at h; done)
  simp only [bind, Except.bind, pure, Except.pure] at h ⊢
  refine foldlM_ok_mono ?_ _ _ _ h
  intro seen item s hs
  repeat (split at hs <;> try (cases hs; done))
  clear h
  simp only [Bool.false_or, Bool.and_eq_true] at *
  simp only [*, Bool.true_or, if_true, and_self]

/-- W2 gives one name per record. -/
theorem openTermNames_length (rv xs python data formula sorts ns)
    (h : VE.Discourse.Loader.openTermNames rv (.arr xs) python data formula sorts = .ok ns) :
    ns.length = xs.toList.length := by
  unfold VE.Discourse.Loader.openTermNames at h
  simp only [bind, Except.bind, pure, Except.pure] at h
  have := foldlM_ok_length ?_ _ _ _ h
  · simpa using this
  intro seen item s hs
  repeat (split at hs <;> try (cases hs; done))
  cases hs
  simp

theorem records_names (rv j data formula rs) (h : records rv j data formula = .ok rs) :
    VE.Discourse.Loader.openTermNames rv j (python := true) (data := data) (formula := formula) (sorts := true) =
      .ok (rs.map (·.1.name)) := by
  unfold records at h
  cases hn : VE.Discourse.Loader.openTermNames rv j (python := true) (data := data) (formula := formula)
    (sorts := true) with
  | error e => rw [hn] at h; cases h
  | ok names =>
    rw [hn] at h
    cases h
    have hlen : names.length ≤ (match j with | .arr xs => xs.toList | _ => []).length := by
      cases j <;> try (simp [VE.Discourse.Loader.openTermNames, bind, Except.bind] at hn; done)
      exact Nat.le_of_eq (openTermNames_length _ _ _ _ _ _ _ hn)
    congr 1
    rw [List.map_map]
    exact (List.map_snd_zip hlen).symm ▸ rfl

theorem records_refuse (rv j data formula e)
    (h : VE.Discourse.Loader.openTermNames rv j (python := true) (data := data) (formula := formula)
      (sorts := true) = .error e) :
    records rv j data formula = .error e := by
  simp [records, h, bind, Except.bind]

/-! ### Admission -/

/-- The base vocabulary: the environment below the document's W3 definitions. -/
def baseEnv (E : VE.Environment) (defs : List VE.Definitions.Def) : VE.Environment :=
  VE.Definitions.hide E (VE.Definitions.names defs)

/-- The checks of plan 2.1, items 1–5, in that order, for one record. -/
def faultOf (E : VE.Environment) (defs : List VE.Definitions.Def) (regulated : List String) (r : Rec) :
    Option String :=
  match (baseEnv E defs).predicates r.1.name with
  | none => some s!"JudgmentUnbound: {r.1.name}"
  | some ss =>
    if ss != r.1.arguments then some s!"JudgmentArguments: {r.1.name}"
    else if regulated.contains r.1.name then some s!"JudgmentRegulated: {r.1.name}"
    else if r.2.1 != 0 || r.2.2 != 0 then some s!"JudgmentCriterionAsUnit: {r.1.name}"
    else if r.1.decidedBy == "unstated" then some s!"JudgmentDecider: {r.1.name}"
    else none

/-- `judgments@0`'s admission: the first fault in record order. -/
def admit (E : VE.Environment) (defs : List VE.Definitions.Def) (regulated : List String) (rs : List Rec) :
    Except String (List Judgment) :=
  match rs.findSome? (faultOf E defs regulated) with
  | some e => .error e
  | none => .ok (rs.map (·.1))

def names (js : List Judgment) : List String := js.map (·.name)

/-- A record is admitted exactly when it is bound to a base predicate with its sorts, no rule regulates it, it
    carries no criterion lists, and its decider is not `unstated`. -/
theorem faultOf_none_iff (E defs regulated r) :
    faultOf E defs regulated r = none ↔
      (baseEnv E defs).predicates r.1.name = some r.1.arguments ∧ r.1.name ∉ regulated ∧
        r.2.1 = 0 ∧ r.2.2 = 0 ∧ r.1.decidedBy ≠ "unstated" := by
  unfold faultOf
  split
  · rename_i h; simp [h]
  · rename_i ss h
    by_cases h1 : ss = r.1.arguments
    · subst h1
      by_cases h2 : r.1.name ∈ regulated
      · simp [h, h2]
      · by_cases h3 : r.2.1 = 0
        · by_cases h4 : r.2.2 = 0
          · by_cases h5 : r.1.decidedBy = "unstated"
            · simp [h, h2, h3, h4, h5]
            · simp [h, h2, h3, h4, h5]
          · simp [h, h2, h3, h4]
        · simp [h, h2, h3]
    · simp [h, h1]

theorem admit_ok_iff (E defs regulated rs js) :
    admit E defs regulated rs = .ok js ↔ js = rs.map (·.1) ∧ ∀ r ∈ rs, faultOf E defs regulated r = none := by
  unfold admit
  cases hf : rs.findSome? (faultOf E defs regulated) with
  | some e =>
    obtain ⟨_, r, _, rfl, hr, _⟩ := List.findSome?_eq_some_iff.mp hf
    simp only [reduceCtorEq, false_iff, not_and]
    intro _ hall
    simp [hall r (by simp)] at hr
  | none =>
    have hall := List.findSome?_eq_none_iff.mp hf
    constructor
    · intro h; cases h; exact ⟨rfl, hall⟩
    · rintro ⟨rfl, _⟩; rfl

/-- The fault is the first faulty record's first failing check. -/
theorem admit_first_fault (E defs regulated rs e) (h : admit E defs regulated rs = .error e) :
    ∃ pre r post, rs = pre ++ r :: post ∧ (∀ q ∈ pre, faultOf E defs regulated q = none) ∧
      faultOf E defs regulated r = some e := by
  unfold admit at h
  cases hf : rs.findSome? (faultOf E defs regulated) with
  | none => rw [hf] at h; cases h
  | some e' =>
    rw [hf] at h
    cases h
    obtain ⟨pre, r, post, hrs, hr, hpre⟩ := List.findSome?_eq_some_iff.mp hf
    exact ⟨pre, r, post, hrs, hpre, hr⟩

end VE.Judgments
