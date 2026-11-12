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

/-- One result row: the query as sent, the selected rules and the outcome. -/
def selectedRow (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) (q : SelectedQuery) : Json :=
  Json.mkObj [("predicate", .str q.pred), ("tuple", toJson q.ids),
    ("selected", toJson (selectedAt D M q.pred q.tuple)), ("outcome", .bool (outcomeAt D M q.pred q.tuple))]

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
  pure (VE.Route.Wire.ok id [("background", .bool (classificationBackgroundValid src.D M)),
    ("results", Json.arr (qs.map (selectedRow src.D M)).toArray)])

end VE.SoftNorms.Run
