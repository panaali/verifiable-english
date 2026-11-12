import VE.SoftNorms.Wire

/-! The soft route's `soft-selected` kind (kb-10a): which rules are selected at a typed tuple of a
decoded base model, and the completed outcome there, both read from the soft route's own
base-expanded formulas (`circ D (selects' D N)` and `circ D (atom p (sortsOf D p))`).

`selectedAt` and `outcomeAt` evaluate those formulas in the finite model; `selected_semantics`
says what they mean: the selection formula and the regulated atom in every full structure over
`E′` whose base restriction is the model and whose layer symbols mean what the layers say
(`AgreesBelow … (size (soften D))`). The case decoder (`decodeQueries`) and the answer row
(`selectedRow`) are the kind's executable part; `SelectedSound.lean` states the wire answer. -/
namespace VE.SoftNorms.Run
open Lean
open VE.Norms
open VE.SoftNorms.Wire

/-- The names of the rules on predicate `p` whose selection formula, expanded to the base
vocabulary (`circ`), is true at the tuple `vs` of the base model `M`, in the source's rule order. -/
def selectedAt (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) (p : String)
    (vs : List VE.Bridge.Entity) : List String :=
  (D.T.nodes.filter fun N => N.pred == p && (circ D (selects' D N)).eval M (tupleVal vs)).map (·.name)

/-- The completed outcome of `p` at the tuple `vs` of `M`: the regulated atom expanded to the base
vocabulary (its layer body with the default, `circ`). -/
def outcomeAt (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) (p : String)
    (vs : List VE.Bridge.Entity) : Bool :=
  (circ D (atom p (sortsOf D p))).eval M (tupleVal vs)

/-- A rule name is listed exactly when some rule of that name on `p` has its expanded selection
formula true in the model's structure at the tuple. -/
theorem mem_selectedAt (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) (p : String)
    (vs : List VE.Bridge.Entity) (name : String) :
    name ∈ selectedAt D M p vs ↔
      ∃ N ∈ D.T.nodes, N.name = name ∧ N.pred = p ∧
        (circ D (selects' D N)).denote M.asStructure (tupleVal vs) := by
  unfold selectedAt
  simp only [List.mem_map, List.mem_filter, Bool.and_eq_true, beq_iff_eq]
  constructor
  · rintro ⟨N, ⟨hN, hp, he⟩, rfl⟩
    exact ⟨N, hN, rfl, hp, (VE.eval_iff_denote M _ _).mp he⟩
  · rintro ⟨N, hN, rfl, hp, hd⟩
    exact ⟨N, ⟨hN, hp, (VE.eval_iff_denote M _ _).mpr hd⟩, rfl⟩

/-- The outcome is true exactly when the expanded atom holds in the model's structure. -/
theorem outcomeAt_iff (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) (p : String)
    (vs : List VE.Bridge.Entity) :
    outcomeAt D M p vs = true ↔ (circ D (atom p (sortsOf D p))).denote M.asStructure (tupleVal vs) :=
  VE.eval_iff_denote M _ _

/-- A full structure over `E′` built on the model `M`: `M`'s carrier, domains and constants, and
the relations `rel`. Every structure whose base restriction is `M.asStructure` is one of these
(its carrier, domains and constants are `M`'s), with `rel` agreeing with `M` off the layer symbols. -/
def fullOver (M : VE.FiniteModel VE.Bridge.Entity) (rel : String → List VE.Bridge.Entity → Prop) :
    VE.Structure.{0} :=
  { M.asStructure with relation := rel }

/-- The semantics of the kind. For a well-formed soft document, a model valid over the base
vocabulary, a regulated predicate `p` and a tuple typed for its sorts, and every full structure
`S = fullOver M rel` whose base restriction is `M` (`rel` agrees with `M` on every non-layer
symbol) and whose layer symbols agree with their meanings (`AgreesBelow` at the full prefix): a
name is selected exactly when a rule of that name on `p` selects in `S`, and the outcome is `p` in
`S`. `ConstantsTyped` follows from the model's validity; no background premise is assumed (the
kind answers models that fail it, SPEC 4.2). -/
theorem selected_semantics (D : SoftDoc) (h : WellFormedSoft D = true)
    (M : VE.FiniteModel VE.Bridge.Entity) (hM : M.Valid (envAt (soften D) 0))
    (p : String) (hp : p ∈ D.T.regulated.map (·.name))
    (vs : List VE.Bridge.Entity) (hvs : VE.TupleTyped M.asStructure (sortsOf D p) vs)
    (rel : String → List VE.Bridge.Entity → Prop)
    (hbase : ∀ r ws, r ∉ layerNames (soften D).T → (rel r ws ↔ M.asStructure.relation r ws))
    (ha : AgreesBelow (soften D) (size (soften D)) (fullOver M rel)) :
    (∀ name, name ∈ selectedAt D M p vs ↔
      ∃ N ∈ D.T.nodes, N.name = name ∧ N.pred = p ∧ (selects' D N).denote (fullOver M rel) (tupleVal vs)) ∧
    (outcomeAt D M p vs = true ↔ (atom p (sortsOf D p)).denote (fullOver M rel) (tupleVal vs)) := by
  have hsv := softValid_of_wellFormed D h
  have hv : Valid (soften D) := valid_of_wellFormed _ hsv.wf
  have hc : ConstantsTyped (soften D) (fullOver M rel) := fun c s hcs => hM.1 c s hcs
  have hρ : VE.Valuation.Typed (fullOver M rel) (sortsOf D p).reverse (tupleVal vs) :=
    tupleVal_typed (fullOver M rel) _ vs ((tupleTyped_relation M.asStructure rel _ vs).mpr hvs)
  -- A formula over the full prefix: its expansion in `M` is the formula in `S`.
  have key : ∀ φ : VE.Formula, φ.WellFormed (envAt (soften D) (size (soften D))) (sortsOf D p).reverse →
      ((circ D φ).denote M.asStructure (tupleVal vs) ↔ φ.denote (fullOver M rel) (tupleVal vs)) := by
    intro φ hφ
    have hb := denote_relation_congr (ns := layerNames (soften D).T) (fun _ hr => envAt_zero_later hr)
      M.asStructure rel hbase (circ D φ) _ (tupleVal vs) (subst_wellFormed hv _ φ _ hφ)
    exact hb.symm.trans (subst_denote hv _ (fullOver M rel) hc ha φ _ hφ (tupleVal vs) hρ)
  refine ⟨fun name => (mem_selectedAt D M p vs name).trans ?_, (outcomeAt_iff D M p vs).trans ?_⟩
  · constructor
    · rintro ⟨N, hN, hn, hpN, hs⟩
      refine ⟨N, hN, hn, hpN, (key _ ?_).mp hs⟩
      rw [← hpN]; exact hsv.selTyped N hN
    · rintro ⟨N, hN, hn, hpN, hs⟩
      refine ⟨N, hN, hn, hpN, (key _ ?_).mpr hs⟩
      rw [← hpN]; exact hsv.selTyped N hN
  · apply key
    obtain ⟨r, hr, rfl⟩ := List.mem_map.mp hp
    obtain ⟨r', hfind⟩ : ∃ r', D.T.regulated.find? (·.name == r.name) = some r' :=
      Option.isSome_iff_exists.mp (List.find?_isSome.mpr ⟨r, hr, by simp⟩)
    have hr' := List.mem_of_find?_eq_some hfind
    have hname : r'.name = r.name := by simpa using List.find?_some hfind
    have hsorts : sortsOf D r.name = r'.sorts := by simp [sortsOf, sortsIn, hfind]
    have hdecl := hv.decl _ (hv.regulated r' hr')
    rw [hsorts]
    refine atom_wellFormed hdecl.2.1 ?_
    rw [envAt_size_predicates, ← hname]
    exact hdecl.1

/-! ## The case decoder -/

/-- One decoded query: a regulated predicate, the tuple's ids as sent and the typed tuple. -/
structure SelectedQuery where
  pred : String
  ids : List String
  tuple : List VE.Bridge.Entity

/-- The `i`-th query `{"predicate": p, "tuple": [ids]}`: `p` a regulated predicate of the source,
the ids one entity of `M` per sort of `p`. Every refusal names the query's index. -/
def decodeSelectedQuery (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) (i : Nat) (q : Json) :
    Except String SelectedQuery :=
  match (q.getObjValD "predicate").getStr?, VE.Bridge.strings (q.getObjValD "tuple") with
  | .error _, _ => .error s!"InvalidInput: query {i}: predicate must be a string"
  | _, .error _ => .error s!"InvalidInput: query {i}: tuple must be an array of entity ids"
  | .ok p, .ok ids =>
    if !D.T.regulated.any (·.name == p) then
      .error s!"InvalidInput: query {i}: {p} is not a regulated predicate of the source"
    else if ids.length == (sortsOf D p).length && VE.Bridge.tupleCheck M (sortsOf D p) ((sortsOf D p).zip ids) then
      .ok ⟨p, ids, (sortsOf D p).zip ids⟩
    else .error s!"InvalidInput: query {i}: tuple has the wrong length or sort for {p}"

/-- The queries in order, the first numbered `i`. -/
def decodeQueries (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) :
    Nat → List Json → Except String (List SelectedQuery)
  | _, [] => pure []
  | i, q :: qs => do
    let x ← decodeSelectedQuery D M i q
    let xs ← decodeQueries D M (i + 1) qs
    pure (x :: xs)

/-! ## One expansion per document

`circ` builds its substitution table (`expTable`) as nested closures, which recompute a layer's
expansion at every use. The kind expands each rule's selection formula and each regulated atom once
per case, with the table built once as a list (`expList`); `expList_lookup` and `expanded_circ` say
these are `circ`'s formulas, so the answer is `selectedAt` and `outcomeAt` (`selectedRow_eq`). -/

/-- The table as a list: each layer symbol before `k` with its base expansion, latest first. -/
def expList (T : Tree) : Nat → List (String × VE.Formula)
  | 0 => []
  | k + 1 =>
    let rest := expList T k
    match (syms T)[k]? with
    | some q => (q.name, substWith (fun n => ((rest.find? (·.1 == n)).map (·.2))) (q.meaning T)) :: rest
    | none => rest

/-- A lookup in `expList`. -/
def listTable (l : List (String × VE.Formula)) : Table := fun n => (l.find? (·.1 == n)).map (·.2)

theorem expList_lookup (T : Tree) : ∀ k, listTable (expList T k) = expTable T k
  | 0 => rfl
  | k + 1 => by
    funext n
    have ih := expList_lookup T k
    simp only [expList, expTable]
    cases (syms T)[k]? with
    | none => exact congrFun ih n
    | some q =>
      simp only [listTable, List.find?_cons] at ih ⊢
      by_cases h : n = q.name
      · subst h
        simp only [beq_self_eq_true, ↓reduceIte, Option.map_some]
        exact congrArg (fun t => some (substWith t (q.meaning T))) ih
      · have : (q.name == n) = false := by simpa [beq_iff_eq] using Ne.symm h
        simp only [this, h, ↓reduceIte]
        exact congrFun ih n

/-- Every rule with its expanded selection formula, and every regulated predicate with its expanded
atom, for one document. -/
def expanded (D : SoftDoc) : List (SoftNode × VE.Formula) × List (String × VE.Formula) :=
  let tbl := listTable (expList (soften D).T (size (soften D)))
  (D.T.nodes.map fun N => (N, substWith tbl (selects' D N)),
    D.T.regulated.map fun r => (r.name, substWith tbl (atom r.name (sortsOf D r.name))))

theorem expanded_circ (D : SoftDoc) (φ : VE.Formula) :
    substWith (listTable (expList (soften D).T (size (soften D)))) φ = circ D φ := by
  rw [expList_lookup]; rfl

/-- One result row: the query as sent, the rules selected and the outcome, read from `expanded D`. -/
def selectedRow (E : List (SoftNode × VE.Formula) × List (String × VE.Formula))
    (M : VE.FiniteModel VE.Bridge.Entity) (q : SelectedQuery) : Json :=
  Json.mkObj [("predicate", .str q.pred), ("tuple", toJson q.ids),
    ("selected", toJson ((E.1.filter fun x => x.1.pred == q.pred && x.2.eval M (tupleVal q.tuple)).map (·.1.name))),
    ("outcome", .bool (match E.2.find? (·.1 == q.pred) with
      | some x => x.2.eval M (tupleVal q.tuple)
      | none => false))]

/-- For a regulated predicate, the row is `selectedAt` and `outcomeAt`. -/
theorem selectedRow_eq (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) (q : SelectedQuery)
    (hp : q.pred ∈ D.T.regulated.map (·.name)) :
    selectedRow (expanded D) M q = Json.mkObj [("predicate", .str q.pred), ("tuple", toJson q.ids),
      ("selected", toJson (selectedAt D M q.pred q.tuple)), ("outcome", .bool (outcomeAt D M q.pred q.tuple))] := by
  unfold selectedRow expanded selectedAt outcomeAt
  simp only [expanded_circ, List.filter_map, List.map_map, List.find?_map]
  obtain ⟨r, hr, hname⟩ := List.mem_map.mp hp
  obtain ⟨r', hfind⟩ : ∃ r', D.T.regulated.find? (fun x => x.name == q.pred) = some r' :=
    Option.isSome_iff_exists.mp (List.find?_isSome.mpr ⟨r, hr, by simp [hname]⟩)
  have hname' : r'.name = q.pred := by simpa using List.find?_some hfind
  have hf : ∀ g : Regulated → VE.Formula,
      D.T.regulated.find? ((fun x : String × VE.Formula => x.1 == q.pred) ∘ fun r => (r.name, g r)) = some r' :=
    fun g => by simpa [Function.comp_def] using hfind
  rw [hf]
  simp only [Option.map_some, hname']
  rfl

/-- The kind `soft-selected`: `environment`, `norms`, `model` and a non-empty `queries`. A model
that fails the soft background is answered with `background: false`, not refused. -/
def runSelected (id : String) (j : Json) : Except String Json := do
  let environment ← j.getObjVal? "environment"
  let src ← decodeSoftSource environment (j.getObjValD "norms")
  let ⟨M, _⟩ ← decodeModel src j
  let qs ← (match j.getObjValD "queries" with
    | .arr raw =>
      if raw.isEmpty then .error "InvalidInput: soft-selected needs at least one query"
      else decodeQueries src.D M 0 raw.toList
    | _ => .error "InvalidInput: soft-selected needs a queries array")
  let E := expanded src.D
  pure (VE.Route.Wire.ok id [("background", .bool (classificationBackgroundValid src.D M)),
    ("results", Json.arr (qs.map (selectedRow E M)).toArray)])

end VE.SoftNorms.Run
