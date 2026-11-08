import VE.Acts.Elaborate
import VE.Acts.Wire

/-! The decoder after AP-3 (docs/spec/act-phrases.md 6.4): the decoded source, unchanged, and beside it the elaborated
document and its map.

Elaboration runs after `decodeSourceU` has decoded the document and recovered its `unspecified` completions (SR6),
so the source and its binding proofs are untouched. Each act of the decoded document was read once by `checkAct`,
in the decoder (`Norms.Wire.actsOf`): a lexical act gives no tree, a joined act its one meaning.

The norms hook admits a joined act, so every entry point an `acts@0` norms document reaches runs on `e.U'`: `sourceOf`
gives it as the `Source` the routes read, the parts declared in place of their sources, so a route's theorem over any
`Source` holds of it. A document whose acts are all lexical is its source (`sourceOf_lexical`).
-/

namespace VE.Acts.Decode
open Lean VE.Acts VE.NormDefaults

/-- The decoded source, unchanged, and beside it the elaborated document and its map. -/
structure ElaboratedU where
  s : VE.NormDefaults.Wire.SourceU
  D : ActsDoc
  hU : D.U = s.U
  U' : VE.NormDefaults.UDoc
  M : SplitMap
  hE : elaborateMap D = .ok (U', M)

/-- The decoded source `s`, elaborated: `V` and `fixed` from the `acts` block, each joined act's tree as the decoder
    read it (`Norms.Wire.actsOf`), `declared := (declaredNames environment).length`; then `elaborateMap D`. Without
    `acts@0` the decoder reads no act. -/
def elaborateSource (environment : Json) (s : VE.NormDefaults.Wire.SourceU) : Except String ElaboratedU := do
  let fx ← VE.Norms.Wire.actsFixed (VE.Norms.Wire.actsProfiles true environment) environment
  let V ← VE.Norms.Wire.actsVocab (VE.Norms.Wire.actsProfiles true environment) environment
  let D : ActsDoc := ⟨s.U, V, fx, s.src.ne.joined, (VE.NormDefaults.Wire.declaredNames environment).length⟩
  match h : elaborateMap D with
  | .ok (U', M) => pure ⟨s, D, rfl, U', M, h⟩
  | .error e => throw e

/-- `decodeSourceU`; then `D`: `V` and `fixed` from the `acts` block, each joined act's tree from `checkAct` (which is
    deterministic, so it is the decoder's answer), `declared := (declaredNames environment).length`; then
    `elaborateMap D`. -/
def decodeElaboratedU (environment norms : Json) : Except String ElaboratedU :=
  VE.NormDefaults.Wire.decodeSourceU environment norms >>= elaborateSource environment

/-- The norms route's source as `decodeSourceU`'s second branch gives it, for a source decoded with its flags. -/
def plainU (src : VE.Norms.Wire.Source) : VE.NormDefaults.Wire.SourceU :=
  ⟨src, ⟨src.D, []⟩, rfl, (by rw [fill_eq_self _ rfl]; exact src.wf), false, (fun h => by cases h), fun _ => rfl⟩

/-- `decodeElaboratedU` on the norms route, which admits `data@0` flags; `decodeSourceU`'s second branch does not
    and takes no parameter (6.4). -/
def decodeElaboratedFlagged (environment norms : Json) : Except String ElaboratedU :=
  VE.Norms.Wire.decodeSource environment norms (flags := true) >>= (elaborateSource environment <| plainU ·)

/-- A vocabulary's predicates with each part declared, and no split source. -/
def splitPredicates (P : List (String × List String)) (M : SplitMap) : List (String × List String) :=
  M.preds.map (fun x => (x.1, (VE.Bridge.lookup P x.2.1).getD [])) ++
    P.filter fun x => !M.preds.any (·.2.1 == x.1) && !M.preds.any (·.1 == x.1)

/-- The environment JSON with each part's declaration its source's, which `plainWordings` reads. -/
def splitJson (json : Json) (M : SplitMap) : Json :=
  let predicates := (json.getObjValD "vocabulary").getObjValD "predicates"
  json.setObjVal! "vocabulary" ((json.getObjValD "vocabulary").setObjVal! "predicates"
    (M.preds.foldl (fun acc x => acc.setObjVal! x.1 (predicates.getObjValD x.2.1)) predicates))

theorem lookup_cons (x : String × List String) (P : List (String × List String)) (q : String) :
    VE.Bridge.lookup (x :: P) q = if x.1 = q then some x.2 else VE.Bridge.lookup P q := by
  by_cases h : x.1 = q <;> simp [VE.Bridge.lookup, List.find?_cons, h]

theorem lookup_append (P Q : List (String × List String)) (q : String) :
    VE.Bridge.lookup (P ++ Q) q = (VE.Bridge.lookup P q).or (VE.Bridge.lookup Q q) := by
  induction P with
  | nil => rfl
  | cons x P ih =>
    rw [List.cons_append, lookup_cons, lookup_cons, ih]
    split <;> rfl

theorem lookup_map (f : String × String × Nat → List String) (q : String) (ps : List (String × String × Nat)) :
    VE.Bridge.lookup (ps.map fun x => (x.1, f x)) q = (ps.find? (·.1 == q)).map f := by
  induction ps with
  | nil => rfl
  | cons x ps ih =>
    rw [List.map_cons, lookup_cons, ih]
    by_cases h : x.1 = q <;> simp [List.find?_cons, h]

theorem lookup_filter_keep (P : List (String × List String)) (q : String) (f : String × List String → Bool)
    (hf : ∀ x ∈ P, x.1 = q → f x = true) : VE.Bridge.lookup (P.filter f) q = VE.Bridge.lookup P q := by
  induction P with
  | nil => rfl
  | cons x P ih =>
    have ih' := ih fun y hy => hf y (List.mem_cons_of_mem _ hy)
    by_cases h : x.1 = q
    · simp [List.filter_cons, hf x List.mem_cons_self h, lookup_cons, h]
    · by_cases hx : f x = true <;> simp [List.filter_cons, hx, lookup_cons, h, ih']

theorem lookup_filter_drop (P : List (String × List String)) (q : String) (f : String × List String → Bool)
    (hf : ∀ x ∈ P, x.1 = q → f x = false) : VE.Bridge.lookup (P.filter f) q = none := by
  induction P with
  | nil => rfl
  | cons x P ih =>
    have ih' := ih fun y hy => hf y (List.mem_cons_of_mem _ hy)
    by_cases h : x.1 = q
    · simp [List.filter_cons, hf x List.mem_cons_self h, ih']
    · by_cases hx : f x = true <;> simp [List.filter_cons, hx, lookup_cons, h, ih']

/-- `splitPredicates` declares what `splitEnv` does, when every split source is declared. -/
theorem lookup_split (P : List (String × List String)) (M : SplitMap) (q : String)
    (hall : (M.preds.all fun x => (VE.Bridge.lookup P x.2.1).isSome) = true) :
    VE.Bridge.lookup (splitPredicates P M) q = (M.preds.find? (·.1 == q)).elim
      (if M.preds.any (·.2.1 == q) then none else VE.Bridge.lookup P q) (VE.Bridge.lookup P ·.2.1) := by
  unfold splitPredicates
  rw [lookup_append, lookup_map]
  cases hx : M.preds.find? (·.1 == q) with
  | some x =>
    have hs := List.all_eq_true.mp hall x (List.mem_of_find?_eq_some hx)
    cases hl : VE.Bridge.lookup P x.2.1 with
    | none => rw [hl] at hs; cases hs
    | some a => simp [hl]
  | none =>
    have hno : ∀ y ∈ M.preds, y.1 ≠ q := fun y hy h => by
      simpa [h] using List.find?_eq_none.mp hx y hy
    have hany : M.preds.any (·.1 == q) = false := by
      simpa using hno
    simp only [Option.map_none, Option.none_or, Option.elim_none]
    by_cases hs : M.preds.any (·.2.1 == q) = true
    · rw [if_pos hs, lookup_filter_drop]
      intro y _ hy; subst hy; simp [hs]
    · rw [if_neg hs, lookup_filter_keep]
      intro y _ hy; subst hy
      simp only [Bool.not_eq_true] at hs
      simp [hs, hany]

/-! ### Theorems (6.4) -/

/-- A document whose acts are all lexical elaborates to itself. -/
theorem elaborated_lexical (e : ElaboratedU) (hl : e.D.acts = []) : e.U' = e.s.U ∧ e.M = ⟨[], []⟩ := by
  have hs : splitAtoms e.D = fun _ => none := funext fun p => by simp [splitAtoms, hl]
  obtain ⟨_, _, hU, hM, _⟩ := elaborateMap_ok e.hE
  rw [hs, splitDoc_none] at hU
  rw [hs] at hM
  exact ⟨hU.trans e.hU, hM.trans (by simp [splitMap, partsOf])⟩

theorem elaborateSource_s {environment : Json} {s : VE.NormDefaults.Wire.SourceU} {e : ElaboratedU}
    (h : elaborateSource environment s = .ok e) : e.s = s := by
  unfold elaborateSource at h
  simp only [bind, Except.bind] at h
  repeat' split at h
  all_goals first | (cases h; done) | (simp only [pure, Except.pure, Except.ok.injEq] at h; subst h; rfl)

theorem wellFormedU_D {U : UDoc} (h : WellFormedU U = true) : VE.Norms.WellFormed U.D = true := by
  simp only [WellFormedU, Bool.and_eq_true] at h
  exact h.1.1.1

/-- The elaborated document's environment is `splitEnv`, over the declarations of the source's vocabulary. -/
theorem splitEnv_route (e : ElaboratedU) (rv' : VE.Route.Wire.RouteVocabulary)
    (hs : (e.M.preds.all fun x => (VE.Bridge.lookup e.s.src.ne.rv.vocabulary.predicates x.2.1).isSome) = true)
    (hv : rv'.vocabulary = { e.s.src.ne.rv.vocabulary with
      predicates := splitPredicates e.s.src.ne.rv.vocabulary.predicates e.M })
    (hf : rv'.flags = e.s.src.ne.rv.flags) : e.U'.D.E = rv'.environment := by
  obtain ⟨_, _, hU, hM, _⟩ := elaborateMap_ok e.hE
  have hE : e.D.U.D.E = e.s.src.ne.rv.environment := by rw [e.hU, e.s.doc, e.s.src.env]
  have hsplit : e.U'.D.E = splitEnv e.D e.M := by rw [hU, hM]; rfl
  rw [hsplit]
  unfold splitEnv VE.Route.Wire.RouteVocabulary.environment
  rw [hE, hv, hf]
  unfold VE.Route.Wire.RouteVocabulary.environment
  simp only [VE.Bridge.Vocabulary.environment]
  congr
  funext q
  rw [lookup_split _ _ _ hs]
  cases M_find : e.M.preds.find? (·.1 == q) <;> rfl

/-- The elaborated document as the `SourceU` the routes read: the source's own value when its acts are all lexical;
    else the parts declared in place of their sources, the names and the definitions chain checked over them. -/
def sourceOf (e : ElaboratedU) : Except String VE.NormDefaults.Wire.SourceU :=
  let src := e.s.src
  let rv := src.ne.rv
  let v : VE.Bridge.Vocabulary := { rv.vocabulary with predicates := splitPredicates rv.vocabulary.predicates e.M }
  let sv : VE.Bridge.Vocabulary :=
    { rv.sourceVocabulary with predicates := splitPredicates rv.sourceVocabulary.predicates e.M }
  have hu := (elaborateMap_ok e.hE).2.2.2.2.1
  if e.D.acts.isEmpty then pure e.s else
  if hs : (e.M.preds.all fun x => (VE.Bridge.lookup rv.vocabulary.predicates x.2.1).isSome) = true then
    if hn : sv.namesValid = true then
      if hc : VE.Definitions.chainOk v.environment rv.definitions = true then
        let rv' : VE.Route.Wire.RouteVocabulary :=
          { rv with vocabulary := v, sourceVocabulary := sv, validNames := hn,
                    chain := VE.Definitions.chainOk_sound _ _ hc }
        let ne' : VE.Norms.Wire.NormsEnvironment :=
          { src.ne with rv := rv', regulated := e.U'.D.T.regulated, json := splitJson src.ne.json e.M }
        have hlits : e.U'.D.lits = src.ne.rv.literals := by
          rw [(elaborateMap_ok e.hE).2.2.1, ← src.lits, ← e.s.doc, ← e.hU]; rfl
        pure ⟨⟨ne', e.U'.D, wellFormedU_D hu, splitEnv_route e rv' hs rfl rfl, hlits⟩, e.U', rfl,
          VE.NormDefaults.fill_wellFormed _ hu, e.s.profiled, fun _ => hu, fun hp => by
            rw [(elaborateMap_ok e.hE).2.2.1]
            simp [splitDoc, e.hU, e.s.plain hp]⟩
      else throw "InvalidInput: the elaborated document is not well formed"
    else throw "InvalidInput: the elaborated document is not well formed"
  else throw "InvalidInput: the elaborated document is not well formed"

/-- A document whose acts are all lexical is its source. -/
theorem sourceOf_lexical (e : ElaboratedU) (hl : e.D.acts = []) : sourceOf e = .ok e.s := by
  simp [sourceOf, hl, pure, Except.pure]

/-- What the routes read of `sourceOf e`: `e.U'`, with the source's flags and profiled flag. -/
theorem sourceOf_U {e : ElaboratedU} {s : VE.NormDefaults.Wire.SourceU} (h : sourceOf e = .ok s) :
    s.U = e.U' ∧ s.src.D = e.U'.D ∧ s.src.ne.rv.flags = e.s.src.ne.rv.flags ∧ s.profiled = e.s.profiled := by
  unfold sourceOf at h
  simp only [pure, Except.pure] at h
  split at h
  next hl =>
    simp only [Except.ok.injEq] at h
    subst h
    have hU := (elaborated_lexical e (List.isEmpty_iff.mp hl)).1
    exact ⟨hU.symm, by rw [← e.s.doc, hU], rfl, rfl⟩
  · repeat' split at h
    all_goals first | (cases h; done) | skip
    simp only [Except.ok.injEq] at h
    subst h
    exact ⟨rfl, rfl, rfl, rfl⟩

/-- `decodeElaboratedU` as the `SourceU` every norm-defaults check reads. -/
def elaboratedU (environment norms : Json) : Except String VE.NormDefaults.Wire.SourceU :=
  decodeElaboratedU environment norms >>= sourceOf

/-- `decodeElaboratedFlagged` as the `Source` every norms check reads. -/
def flaggedSource (environment norms : Json) : Except String VE.Norms.Wire.Source :=
  (decodeElaboratedFlagged environment norms >>= sourceOf).map (·.src)

/-- `src` reads the elaborated document of `environment` and `norms` on the norms route. -/
def Elaborated (environment norms : Json) (src : VE.Norms.Wire.Source) : Prop :=
  ∃ e, decodeElaboratedFlagged environment norms = .ok e ∧ src.D = e.U'.D ∧
    src.ne.rv.flags = e.s.src.ne.rv.flags

theorem flaggedSource_elaborated {environment norms : Json} {src : VE.Norms.Wire.Source}
    (h : flaggedSource environment norms = .ok src) : Elaborated environment norms src := by
  unfold flaggedSource at h
  cases hd : decodeElaboratedFlagged environment norms with
  | error err => simp [hd, bind, Except.bind, Except.map] at h
  | ok e =>
    cases hs : sourceOf e with
    | error err => simp [hd, hs, bind, Except.bind, Except.map] at h
    | ok s =>
      simp only [hd, hs, bind, Except.bind, Except.map, Except.ok.injEq] at h
      subst h
      obtain ⟨_, h2, h3, _⟩ := sourceOf_U hs
      exact ⟨e, hd, h2, h3⟩

theorem decodeElaboratedU_source {environment norms : Lean.Json} {e : ElaboratedU}
    (h : decodeElaboratedU environment norms = .ok e) :
    VE.NormDefaults.Wire.decodeSourceU environment norms = .ok e.s := by
  unfold decodeElaboratedU at h
  cases hs : VE.NormDefaults.Wire.decodeSourceU environment norms with
  | error err => rw [hs] at h; cases h
  | ok s => rw [hs] at h; exact congrArg _ (elaborateSource_s h).symm

theorem decodeElaboratedU_wellFormed {environment norms : Lean.Json} {e : ElaboratedU}
    (h : decodeElaboratedU environment norms = .ok e) : VE.NormDefaults.WellFormedU e.U' = true :=
  (elaborateMap_ok e.hE).2.2.2.2.1

/-- A document whose acts are all lexical elaborates to itself (AP-3's "byte-identical to AP-1" test). -/
theorem decodeElaboratedU_lexical {environment norms : Lean.Json} {e : ElaboratedU}
    (h : decodeElaboratedU environment norms = .ok e) (hl : e.D.acts = []) : e.U' = e.s.U ∧ e.M = ⟨[], []⟩ :=
  elaborated_lexical e hl

end VE.Acts.Decode
