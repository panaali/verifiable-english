import VE.SoftNorms.SelectedSound

/-! Prepared soft documents (kb-10e): the per-document work of the `soft-selected` kind, done once
per document.

A `soft-selected` case spent most of its time on its document, not on its model or queries: the
model vocabulary (`primeModelVocabulary`) recomputed the layer order of `soften D` (a topological
sort) once per predicate of the environment, and the expansion (`expanded`) once per layer symbol.
`prepare` decodes the source once and computes, from it alone, the softened document, its layer
symbols, the model vocabulary, the expansion of every rule's selection formula and every regulated
atom, and the background formulas; `runSelectedP` then reads only the case's `model` and `queries`.

* `prepare_ok`: every field of a prepared document is the existing definition applied to its source;
* `runSelected_eq_prepared`: the unprepared runner is `prepare` followed by `runSelectedP`, so a
  prepared document never changes an answer;
* `soft_wire_selected_prepared`: `soft_wire_selected`'s conclusion, for a case answered from a
  prepared document;
* `runCaseReportedP_eq`: the soft route's reported answer, from a prepared document, is
  `runCaseReported`'s for the case with that document's environment and norms.

The faster computations share `soften D` and its layer symbols, and each is proved equal to the
definition it stands for (`vocabularyIn`, `expandedIn_eq`, `backgroundIn_valid`), so `prepare_ok`
states every field as the existing definition. The unprepared runner `runSelected` is unchanged. -/
namespace VE.SoftNorms.Run
open Lean
open VE.Norms
open VE.SoftNorms.Wire

/-! ## Computations sharing `soften D` -/

/-- `primeModelVocabulary` with the layer names given (`layerNames (soften D).T` recomputed the layer
order once per predicate of the environment). -/
def vocabularyIn (se : SoftEnvironment) (D : SoftDoc) (names : List String) : VE.Bridge.Vocabulary :=
  { se.ne.rv.modelVocabulary with
    predicates := decisions D ++ se.ne.rv.vocabulary.predicates.filter (fun p => !names.contains p.1) }

theorem vocabularyIn_eq (se : SoftEnvironment) (D : SoftDoc) :
    vocabularyIn se D (layerNames (soften D).T) = primeModelVocabulary se D := rfl

/-- `expList` built from the layer symbols given, earliest first, onto `acc`. -/
def expListOf (T : Tree) : List Sym → List (String × VE.Formula) → List (String × VE.Formula)
  | [], acc => acc
  | q :: qs, acc => expListOf T qs ((q.name, substWith (listTable acc) (q.meaning T)) :: acc)

theorem expListOf_append (T : Tree) (q : Sym) :
    ∀ (l : List Sym) (acc : List (String × VE.Formula)),
      expListOf T (l ++ [q]) acc =
        (q.name, substWith (listTable (expListOf T l acc)) (q.meaning T)) :: expListOf T l acc
  | [], _ => rfl
  | _ :: l, _ => expListOf_append T q l _

/-- `expList T k` is `expListOf` over the first `k` layer symbols. -/
theorem expList_eq_of (T : Tree) : ∀ k, expList T k = expListOf T ((syms T).take k) []
  | 0 => rfl
  | k + 1 => by
    simp only [expList]
    cases hk : (syms T)[k]? with
    | none =>
      have hle : (syms T).length ≤ k := List.getElem?_eq_none_iff.mp hk
      rw [expList_eq_of T k, List.take_of_length_le hle, List.take_of_length_le (by omega)]
    | some q =>
      rw [List.take_succ, hk, Option.toList_some, expListOf_append, ← expList_eq_of T k]
      rfl

/-- `expanded` from the softened document `S` and its layer symbols `ls` (`expList` recomputed the
layer order once per layer symbol, `selects'` the softened document once per rule). -/
def expandedIn (D : SoftDoc) (S : Doc) (ls : List Sym) :
    List (SoftNode × VE.Formula) × List (String × VE.Formula) :=
  let tbl := listTable (expListOf S.T ls [])
  let f := VE.Norms.fuel S.T
  (D.T.nodes.map fun N => (N, substWith tbl (VE.Norms.selects S.T f (primeNode D N))),
    D.T.regulated.map fun r => (r.name, substWith tbl (atom r.name (sortsOf D r.name))))

theorem expandedIn_eq (D : SoftDoc) : expandedIn D (soften D) (syms (soften D).T) = expanded D := by
  simp only [expandedIn, expanded, expList_eq_of, size, List.take_length]
  rfl

/-- The formulas of the classification background: `Background_base` of `soften D`, then `Exc_T`. -/
def backgroundIn (D : SoftDoc) (S : Doc) : List VE.Formula := VE.Norms.backgroundBase S ++ excPremises D

theorem backgroundIn_valid (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) :
    (backgroundIn D (soften D)).all (fun a => a.eval M []) = classificationBackgroundValid D M := by
  simp only [backgroundIn, List.all_append, classificationBackgroundValid, VE.Norms.backgroundValid]

/-! ## The prepared document -/

/-- A decoded soft source and what `runSelected` computes from the source alone. -/
structure Prepared where
  src : SoftSource
  softened : Doc
  layers : List Sym
  vocabulary : VE.Bridge.Vocabulary
  expanded : List (SoftNode × VE.Formula) × List (String × VE.Formula)
  background : List VE.Formula

/-- The prepared document of a decoded source: `soften` once, its layer symbols once. -/
def prepareFrom (src : SoftSource) : Prepared :=
  let S := soften src.D
  let ls := syms S.T
  { src, softened := S, layers := ls, vocabulary := vocabularyIn src.se src.D (ls.map Sym.name),
    expanded := expandedIn src.D S ls, background := backgroundIn src.D S }

/-- Decode a soft document and prepare it. It fails exactly when `decodeSoftSource` fails, with
its message. -/
def prepare (environment norms : Json) : Except String Prepared := do
  let src ← decodeSoftSource environment norms
  pure (prepareFrom src)

/-- The model of a case, decoded over the vocabulary `v` (`decodeModel`'s body). -/
def decodeModelIn (v : VE.Bridge.Vocabulary) (j : Json) : Except String (VE.FiniteModel VE.Bridge.Entity) := do
  let data ← VE.Bridge.decodeModelData v (← j.getObjVal? "model")
  if data.valid v = true then pure data.toModel
  else throw "model is not semantically admissible"

/-- `runSelected` on a prepared document: it reads only `model` and `queries` from the case. -/
def runSelectedP (p : Prepared) (id : String) (j : Json) : Except String Json := do
  let M ← decodeModelIn p.vocabulary j
  let qs ← selectedQueries p.src.D M j
  pure (VE.Route.Wire.ok id [("background", .bool (p.background.all fun a => a.eval M [])),
    ("results", Json.arr (qs.map (selectedRow p.expanded M)).toArray)])

/-! ## Theorems -/

/-- A prepared document is `prepareFrom` of its source, the source `decodeSoftSource` decodes. -/
theorem prepare_eq {e n : Json} {p : Prepared} (h : prepare e n = .ok p) :
    decodeSoftSource e n = .ok p.src ∧ p = prepareFrom p.src := by
  unfold prepare at h
  cases hs : decodeSoftSource e n with
  | error m => rw [hs] at h; cases h
  | ok src =>
    rw [hs] at h
    simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
    subst h
    exact ⟨rfl, rfl⟩

/-- Every field of a prepared document is the existing definition applied to its source. -/
theorem prepare_ok {e n : Json} {p : Prepared} (h : prepare e n = .ok p) :
    decodeSoftSource e n = .ok p.src ∧ p.softened = soften p.src.D ∧ p.layers = syms (soften p.src.D).T ∧
      p.vocabulary = primeModelVocabulary p.src.se p.src.D ∧ p.expanded = expanded p.src.D ∧
      p.background = VE.Norms.backgroundBase (soften p.src.D) ++ excPremises p.src.D := by
  obtain ⟨hs, hp⟩ := prepare_eq h
  rw [hp]
  exact ⟨hs, rfl, rfl, rfl, expandedIn_eq p.src.D, rfl⟩

/-- Over the prime model vocabulary, `decodeModelIn` is `decodeModel` without its proof. -/
theorem decodeModelIn_prime (src : SoftSource) (j : Json) :
    decodeModelIn (primeModelVocabulary src.se src.D) j = Subtype.val <$> decodeModel src j := by
  simp only [decodeModelIn, decodeModel, bind, Except.bind, Functor.map, Except.map]
  cases j.getObjVal? "model" with
  | error m => rfl
  | ok mj =>
    simp only
    cases VE.Bridge.decodeModelData (primeModelVocabulary src.se src.D) mj with
    | error m => rfl
    | ok data =>
      simp only
      by_cases hv : data.valid (primeModelVocabulary src.se src.D) = true
      · simp [hv, pure, Except.pure]
      · simp [hv, throw, throwThe, MonadExceptOf.throw]

/-- `runSelectedP` on a decoded source's prepared document, written with `decodeModel`. -/
theorem runSelectedP_prepareFrom (src : SoftSource) (id : String) (j : Json) :
    runSelectedP (prepareFrom src) id j = (do
      let ⟨M, _⟩ ← decodeModel src j
      let qs ← selectedQueries src.D M j
      pure (VE.Route.Wire.ok id [("background", .bool (classificationBackgroundValid src.D M)),
        ("results", Json.arr (qs.map (selectedRow (expanded src.D) M)).toArray)])) := by
  have hv : (prepareFrom src).vocabulary = primeModelVocabulary src.se src.D := rfl
  have he : (prepareFrom src).expanded = expanded src.D := expandedIn_eq src.D
  unfold runSelectedP
  rw [hv, he, decodeModelIn_prime]
  cases decodeModel src j with
  | error m => rfl
  | ok x =>
    obtain ⟨M, hM⟩ := x
    show (do let qs ← selectedQueries (prepareFrom src).src.D M j; _) = _
    simp only [prepareFrom, backgroundIn_valid]
    rfl

/-- (a) The unprepared runner is `prepare` followed by `runSelectedP`. -/
theorem runSelected_eq_prepared (id : String) (j : Json) :
    runSelected id j = (do
      let e ← j.getObjVal? "environment"
      let p ← prepare e (j.getObjValD "norms")
      runSelectedP p id j) := by
  unfold runSelected prepare
  cases j.getObjVal? "environment" with
  | error m => rfl
  | ok e =>
    simp only [bind, Except.bind]
    cases decodeSoftSource e (j.getObjValD "norms") with
    | error m => rfl
    | ok src =>
      simp only [pure, Except.pure]
      exact (runSelectedP_prepareFrom src id j).symm

/-- (c) `soft_wire_selected`'s conclusion for a case answered from a prepared document: the
source is `decodeSoftSource e n`'s, the model and queries are the case's own decoders', and the
answer is exactly `SelectedAnswer`. -/
theorem soft_wire_selected_prepared (e n : Json) (p : Prepared) (id : String) (j answer : Json)
    (hp : prepare e n = .ok p) (h : runSelectedP p id j = .ok answer) :
    ∃ (src : SoftSource) (M : VE.FiniteModel VE.Bridge.Entity)
      (hM : M.Valid (envAt (soften src.D) 0)) (raws : Array Json) (qs : List SelectedQuery),
      decodeSoftSource e n = .ok src ∧
      decodeModel src j = .ok ⟨M, hM⟩ ∧
      j.getObjValD "queries" = Json.arr raws ∧ raws.toList ≠ [] ∧
      qs.length = raws.size ∧ (∀ x ∈ raws.toList.zip qs, QueryDecoded src.D M x.1 x.2) ∧
      SelectedAnswer id src.D M qs answer := by
  obtain ⟨hsrc, hpf⟩ := prepare_eq hp
  rw [hpf, runSelectedP_prepareFrom] at h
  obtain ⟨⟨M, hM⟩, hmod, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨qs, hqs, h⟩ := VE.Order.ProfileGate.bind_ok h
  simp only [pure, Except.pure, Except.ok.injEq] at h
  subst h
  obtain ⟨raws, hq, hne, hl, hall, hreg⟩ := selectedQueries_ok hqs
  refine ⟨p.src, M, hM, raws, qs, hsrc, hmod, hq, hne, hl, hall, ?_⟩
  unfold SelectedAnswer
  rw [List.map_congr_left (fun q hq => selectedRow_eq p.src.D M q (hreg q hq))]

/-! ## The reported answer -/

/-- `runCaseReported` for a case whose document is prepared as `pe`: a `soft-selected` case is
answered by `runSelectedP`; any other case, or a refusal, by `runCaseReported` itself, so the
reported answer is `runCaseReported`'s (`runCaseReportedP_eq`). -/
def runCaseReportedP (pe : Except String Prepared) (j : Json) : Json :=
  match pe, VE.Bridge.stringField j "id", VE.Route.Run.caseKind j, usesSoftPath j with
  | .ok p, .ok id, .ok "soft-selected", true =>
    match runSelectedP p id j with
    | .ok result => result
    | .error _ => runCaseReported j
  | _, _, _, _ => runCaseReported j

/-- A `soft-selected` case is answered by `runSelected`. -/
theorem runCase_selected (j : Json) (id : String) (hid : VE.Bridge.stringField j "id" = .ok id)
    (hk : VE.Route.Run.caseKind j = .ok "soft-selected") (hn : usesSoftPath j = true) :
    runCase j = runSelected id j := by
  unfold runCase
  simp only [hid, hk, bind, Except.bind, hn, show ("soft-selected" == "admission") = false from by decide,
    Bool.false_and, Bool.not_true, Bool.false_eq_true, ↓reduceIte]
  unfold runSoftKind
  simp only [show ("soft-selected" == "soft-selected") = true from by decide, ↓reduceIte]
  cases runSelected id j <;> rfl

/-- The reported answer from the prepared document of a case's own environment and norms is
`runCaseReported`'s. -/
theorem runCaseReportedP_eq (e n j : Json) (he : j.getObjVal? "environment" = .ok e)
    (hn : j.getObjValD "norms" = n) : runCaseReportedP (prepare e n) j = runCaseReported j := by
  unfold runCaseReportedP
  split
  · rename_i p id hp hid hk hu
    have hsel : runCase j = runSelectedP p id j := by
      rw [runCase_selected j id hid hk hu, runSelected_eq_prepared]
      simp only [he, hn, hp, bind, Except.bind]
    split
    · rename_i result hr
      unfold runCaseReported
      rw [hu, hsel, hr]
      rfl
    · rfl
  · rfl

end VE.SoftNorms.Run
