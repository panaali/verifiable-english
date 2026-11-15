import VE.Service.CoreCheck

/-! What the core path's shell definitions are for (kb-2a-b-cutback; the ties pass of kb-2a-b's FOLLOW-UPS.md): each
theorem below states the role of one or more definitions of `VE.Service.CoreCheck` (and `DocumentFold.statuses`), and
`tools/trust-classes.json` ties each definition to it. Nothing here is trusted (P lines). -/

namespace VE.Service.CoreCheck
open Lean
open VE.Service.Document
open VE.Service.CoreDocument
open VE.Kernel
open VE.Kernel.DocumentFold (UnitRow Stmt)
open VE.Kit.Except (bind_ok)

/-! ## The premises a case carries read back -/

/-- The facts the shell sends read back as themselves: when `roundTrips` holds of the premises `P` over the source the
kernel decodes, the kernel's facts decoder reads `factsJson P` as exactly `P` (and their encodings). `roundTrips` is the
round trip's hypotheses; `factsJson` is the encoding that reads back. -/
theorem facts_round_trip (src : VE.SoftNorms.Wire.SoftSource) (P : List VE.Formula) (h : roundTrips src P = true) :
    VE.Compose.SlotWire.decodeFacts src (Json.mkObj [("facts", factsJson P)]) =
      .ok (P, P.map VE.Route.Wire.encodeFormula) := by
  simp only [roundTrips, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨hC, hD⟩, hNo⟩, hDec⟩ := h
  have hF : (Json.mkObj [("facts", factsJson P)]).getObjVal? "facts" = .ok (factsJson P) :=
    VE.Calc.Run.mkObj_get _ "facts" _ (by simp) (by simp)
  unfold VE.Compose.SlotWire.decodeFacts
  rw [hF]
  simp only [factsJson, Json.getArr?, pure, Except.pure]
  split
  · rename_i he
    have : P = [] := by simpa using he
    subst this
    rfl
  · rw [VE.Route.Wire.decodeFormulas_encode _ P false hC hD hNo (fun h => absurd h (by decide))]
    have hnone : P.findSome? (fun x => (VE.Norms.preds x).find? fun p => decide (p ∈ VE.SoftNorms.decisionNames src.D)) =
        none := by
      rw [List.findSome?_eq_none_iff]
      intro x hx
      rw [List.find?_eq_none]
      intro p hp
      simpa using hDec p (List.mem_flatMap.mpr ⟨x, hx, hp⟩)
    simp [bind, Except.bind]
    rw [hnone]

/-! ## Each unit's rendered status is the fold's -/

/-- `statuses` gives each unit row of the table its fold status, keyed by its id: the status of a unit is the status of
the first row with its id. -/
theorem statuses_lookup (table : List UnitRow) (rows : List Row) (id : String) :
    (DocumentFold.statuses table rows).lookup id = (table.find? (·.id == id)).map (DocumentFold.status · rows) := by
  unfold DocumentFold.statuses
  induction table with
  | nil => rfl
  | cons u us ih =>
    simp only [List.map_cons, List.lookup, List.find?_cons]
    by_cases h : u.id = id
    · simp [h]
    · have h1 : (u.id == id) = false := by rw [beq_eq_false_iff_ne]; exact h
      have h2 : (id == u.id) = false := by rw [beq_eq_false_iff_ne]; exact fun e => h e.symm
      simp only [h1, h2, ih]

theorem getObjValD_mkObj (l : List (String × Json)) (k : String) (v : Json) (hn : (l.map (·.1)).Nodup)
    (hm : (k, v) ∈ l) : (Json.mkObj l).getObjValD k = v := by
  simp only [Json.getObjValD, VE.Calc.Run.mkObj_get l k v hn hm]
  rfl

theorem unitJson_status (r : RowUnit) : (unitJson r).getObjValD "status" = .str r.status.name := by
  unfold unitJson
  cases r.parent <;> cases r.content <;> cases r.meaningId <;>
    simp only [Option.toList, List.map_nil, List.map_cons, List.append_nil, List.cons_append, List.nil_append] <;>
    apply getObjValD_mkObj <;> simp

/-- The view renders each unit's status as the fold gave it: the `k`-th unit of the view's `units` shows the name of
`unitStatus` of `DocumentFold.status` of that unit's row of the table, and that name is CHECKED, OPEN, LABELLED or
UNFORMALISED exactly when the fold's status is `checked`, `opened`, `labelled` or `unformalised`. -/
theorem view_unit_status (I : Inputs) (docs : List (Choice × CoreDoc)) (table : List UnitRow) (rows : List Row)
    (k : Nat) (hk : k < I.rows.length) (u : UnitRow) (hu : table.find? (·.id == I.rows[k].id) = some u) :
    ∃ x, ((viewOf I docs (DocumentFold.statuses table rows)).getObjValD "units").getArrVal? k = .ok x ∧
      x.getObjValD "status" = .str (unitStatus (DocumentFold.status u rows)).name ∧
      (x.getObjValD "status" = .str "CHECKED" ↔ DocumentFold.status u rows = .checked) ∧
      (x.getObjValD "status" = .str "OPEN" ↔ DocumentFold.status u rows = .opened) ∧
      (x.getObjValD "status" = .str "LABELLED" ↔ DocumentFold.status u rows = .labelled) ∧
      (x.getObjValD "status" = .str "UNFORMALISED" ↔ DocumentFold.status u rows = .unformalised) := by
  let shown := I.rows.map fun r => { r with status := (((DocumentFold.statuses table rows).lookup r.id).map unitStatus).getD r.status }
  have hunits : (viewOf I docs (DocumentFold.statuses table rows)).getObjValD "units" = toJson (shown.map unitJson) := by
    unfold viewOf encodeFields
    by_cases hj : I.d.judged <;> simp only [hj, ↓reduceIte, List.cons_append, List.nil_append, List.append_nil] <;>
      apply getObjValD_mkObj <;> simp [shown]
  have hk' : k < shown.length := by simpa [shown] using hk
  refine ⟨unitJson shown[k], ?_, ?_⟩
  · rw [hunits]
    simp [toJson, List.toJson, Array.toJson, Json.getArrVal?, shown, hk, pure, Except.pure]
  · rw [unitJson_status]
    have hs : shown[k].status = unitStatus (DocumentFold.status u rows) := by
      simp [shown, statuses_lookup, hu]
    rw [hs]
    cases DocumentFold.status u rows <;> simp [unitStatus, UnitStatus.name]

/-! ## Which documents the core path reads -/

/-- The two refusals `routed` looks for are the ones `Document.environmentOf` gives at its two sites: the first is
`Compose.layersApart`'s refusal of `judgments@0` beside `soft-norms@0` (the site of a rule with an exception condition),
the second the refusal of `soft-norms@0` with `readings@1` (or alternatives or risk). -/
theorem routedRefusals_sites :
    VE.Compose.layersApart ["judgments@0", "soft-norms@0"] ["soft-norms@0"] = .error (routedRefusals[0]'(by decide)) ∧
      routedRefusals[1]'(by decide) = unavailable "soft-norms with readings, alternatives or risk needs its composed Lean route" ∧
      routedRefusals.length = 2 := by
  refine ⟨?_, rfl, rfl⟩
  simp [VE.Compose.layersApart, VE.Compose.documentLayers, routedRefusals, unavailable]
  rfl

/-- `routed j` holds exactly for the documents whose environment `Document.environmentOf` refuses (without the core
flag) with one of the two refusals the core path replaces, whose profiles all have a row of the lowering, that list
`judgments@0` and that have no senses; for no other document. -/
theorem routed_iff (j : Json) :
    routed j = true ↔ ∃ front body e, frontOf j = some (front, body) ∧
      (front.getObjVal? "senses").isOk = false ∧
      (∀ p ∈ listedProfiles (front.getObjValD "environment"), p ∈ rowProfiles) ∧
      "judgments@0" ∈ listedProfiles (front.getObjValD "environment") ∧
      environmentOf (front.getObjValD "environment") (front.getObjValD "units") false
        (some (VE.Discourse.Loader.optionalList front "open_terms")) = .error e ∧
      e ∈ routedRefusals := by
  unfold routed
  cases hf : frontOf j with
  | none => simp
  | some fb =>
    obtain ⟨front, body⟩ := fb
    simp only [Option.some.injEq, Prod.mk.injEq, exists_and_left]
    cases he : environmentOf (front.getObjValD "environment") (front.getObjValD "units") false
        (some (VE.Discourse.Loader.optionalList front "open_terms")) with
    | ok E => simp [he]
    | error e =>
      simp only [List.all_eq_true, Bool.and_eq_true, Bool.not_eq_true', List.contains_iff_mem]
      constructor
      · rintro ⟨⟨⟨hs, hp⟩, hj⟩, hr⟩
        exact ⟨front, body, ⟨rfl, rfl⟩, hs, hp, hj, e, he, hr⟩
      · rintro ⟨_, _, ⟨rfl, rfl⟩, hs, hp, hj, x, hx, hr⟩
        rw [he] at hx
        cases hx
        exact ⟨⟨⟨hs, hp⟩, hj⟩, hr⟩

/-! ## The mode's entry -/

theorem setObjVal_mkObj (l : List (String × Json)) (k : String) (v : Json) :
    (Json.mkObj l).setObjVal! k v = Json.mkObj (l ++ [(k, v)]) := by
  simp only [Json.mkObj, Json.setObjVal!]
  rw [Std.TreeMap.Raw.ofList_eq_insertMany_empty, Std.TreeMap.Raw.ofList_eq_insertMany_empty,
    Std.TreeMap.Raw.insertMany_append, Std.TreeMap.Raw.insertMany_list_singleton]

/-- A refusal row of the core path, marked `lowering`: an error row. -/
theorem marked_row (l : List (String × Json)) (id : Json) (m : String)
    (hl : l = [] ∨ (∃ v, l = [("path", v)]) ∨ ∃ v, l = [("span", v)]) :
    ((Json.mkObj ([("id", id), ("status", .str "error"), ("error", .str m)] ++ l)).setObjVal! "lowering"
      (.bool true)).getObjValD "status" = .str "error" ∧
    ((Json.mkObj ([("id", id), ("status", .str "error"), ("error", .str m)] ++ l)).setObjVal! "lowering"
      (.bool true)).getObjValD "lowering" = .bool true := by
  simp only [setObjVal_mkObj]
  rcases hl with rfl | ⟨v, rfl⟩ | ⟨v, rfl⟩ <;>
    exact ⟨getObjValD_mkObj _ _ _ (by simp) (by simp), getObjValD_mkObj _ _ _ (by simp) (by simp)⟩

theorem locatedRow_marked (j : Json) (m : String) (at_ : Located) :
    ((locatedRow j m at_).setObjVal! "lowering" (.bool true)).getObjValD "status" = .str "error" ∧
    ((locatedRow j m at_).setObjVal! "lowering" (.bool true)).getObjValD "lowering" = .bool true := by
  cases at_ with
  | path p =>
    exact marked_row [("path", .str p)] (j.getObjValD "id") m (.inr (.inl ⟨_, rfl⟩))
  | span source d =>
    exact marked_row [("span", VE.Service.ParseDiagnostic.span source d)] (j.getObjValD "id") m (.inr (.inr ⟨_, rfl⟩))
  | none =>
    exact marked_row [] (j.getObjValD "id") m (.inl rfl)

/-- The mode's entry decides every routed document on the core path: its answer is `answer`'s, or, when `answer`
refuses for any reason other than a feature without a lowering row (`noRow`), an error row with that diagnostic marked
`lowering`, so no other path decides it. Every other document gets `Document.runCaseReported`'s row, unchanged. -/
theorem runCaseReported_routes (j : Json) :
    (routed j = false → runCaseReported j = Document.runCaseReported j) ∧
    (∀ a, routed j = true → answer j = .ok a → runCaseReported j = a) ∧
    (∀ m, routed j = true → answer j = .error m → noRow m = true → runCaseReported j = Document.runCaseReported j) ∧
    (∀ m, routed j = true → answer j = .error m → noRow m = false →
      (runCaseReported j).getObjValD "status" = .str "error" ∧
        (runCaseReported j).getObjValD "lowering" = .bool true) := by
  refine ⟨fun h => ?_, fun a h ha => ?_, fun m h hm hr => ?_, fun m h hm hr => ?_⟩
  · unfold runCaseReported
    rw [if_neg (by simp [h])]
  · unfold runCaseReported
    rw [if_pos h, ha]
  · unfold runCaseReported
    rw [if_pos h, hm]
    exact if_pos hr
  · unfold runCaseReported
    rw [if_pos h, hm]
    simp only [hr, Bool.false_eq_true, ↓reduceIte]
    split
    · exact locatedRow_marked j _ _
    · exact marked_row [] (j.getObjValD "id") m (.inl rfl)

/-! ## What the unit table reads -/

theorem mapM_get {α β ε : Type} {f : α → Except ε β} :
    ∀ {xs : List α} {ys : List β}, xs.mapM f = .ok ys → ys.length = xs.length ∧
      ∀ k (hk : k < xs.length), ∃ y, ys[k]? = some y ∧ f xs[k] = .ok y
  | [], ys, h => by
    simp only [List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h
    subst h
    exact ⟨rfl, fun k hk => absurd hk (Nat.not_lt_zero k)⟩
  | x :: xs, ys, h => by
    rw [List.mapM_cons] at h
    obtain ⟨y, hy, h⟩ := bind_ok h
    obtain ⟨ys', hys, h⟩ := bind_ok h
    simp only [pure, Except.pure, Except.ok.injEq] at h
    subst h
    obtain ⟨hl, hk⟩ := mapM_get hys
    refine ⟨by simp [hl], fun k hk' => ?_⟩
    cases k with
    | zero => exact ⟨y, rfl, hy⟩
    | succ k => simpa using hk k (by simpa using hk')

/-- What `inputs` reads: `Document.decode`'s values with `core`, the active sets of its reading sets, under
`judgments@0` each unit's view as `Document.check` builds it for `Judgments.status` (`judgedViews`), and one meaning
per unit. -/
theorem inputs_reads {j : Json} {I : Inputs} (h : inputs j = .ok I) :
    I.active = VE.Discourse.Loader.activeOf I.d.all ∧
    (I.d.judged = true → judgedViews I.d.E I.d.front I.d.names I.active I.d.units
      ((I.d.S.bind (·.rules)) <|> (I.d.R.bind (·.rules))) I.d.R = .ok I.views) ∧
    I.meanings.length = I.d.units.length := by
  unfold inputs at h
  obtain ⟨id, -, h⟩ := bind_ok h
  obtain ⟨text, -, h⟩ := bind_ok h
  obtain ⟨d, -, h⟩ := bind_ok h
  dsimp only at h
  split at h
  · obtain ⟨_, h1, _⟩ := bind_ok h
    cases h1
  · obtain ⟨_, -, h⟩ := bind_ok h
    split at h <;> rename_i hJ
    all_goals
      obtain ⟨y, hy, h⟩ := bind_ok h
      obtain ⟨sets, -, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      obtain ⟨meanings, hm, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      cases h
      refine ⟨rfl, fun hj => ?_, (mapM_get hm).1⟩
      first | exact hy | exact absurd hj hJ
theorem judgedViews_get {E : Env} {front : Json} {names : List String} {active : List (VE.Discourse.FrontSet × List Bool)}
    {units : List SourceUnit} {S : Option VE.SoftNorms.Wire.SoftEnvironment} {R : Option RightsDoc}
    {vs : List VE.Judgments.UnitView} (h : judgedViews E front names active units S R = .ok vs) (k : Nat)
    (hk : k < units.length) :
    ∃ v, vs[k]? = some v ∧ v.id = units[k].id ∧ (units[k].content.bind fun c => (c.judgedIn S R).toOption).join = v.own := by
  unfold judgedViews at h
  obtain ⟨sets, -, h⟩ := bind_ok h
  obtain ⟨_, hg⟩ := mapM_get h
  obtain ⟨v, hv, hf⟩ := hg k hk
  refine ⟨v, hv, ?_⟩
  obtain ⟨m, -, hf⟩ := bind_ok hf
  dsimp only at hf
  cases hc : units[k].content with
  | none =>
    rw [hc] at hf
    simp only [pure, Except.pure, bind, Except.bind, Except.ok.injEq] at hf
    subst hf
    exact ⟨rfl, rfl⟩
  | some c =>
    rw [hc] at hf
    obtain ⟨own, ho, hf⟩ := bind_ok hf
    simp only [pure, Except.pure, Except.ok.injEq] at hf
    subst hf
    simp [VE.Judgments.viewOf, ho, Except.toOption]

/-- The fold reads what `Judgments.status` reads. Under `judgments@0`, a core statement of a unit's own content (no
reading, not a judgment declaration) reads exactly the judgment terms `Judgments.dependsOnC` finds in that unit's
view, the one `Document.check` gives `Judgments.status` (its own content; `UnitView.reads` when the unit has no
active set), with the exception conditions of a soft rule added (`exceptionFormulas`). -/
theorem reads_status {j : Json} {I : Inputs} (h : inputs j = .ok I) (hJ : I.d.judged = true) (k : Nat)
    (hk : k < I.d.units.length) (st : Statement) (hr : st.origin.reading = none) (hb : ∀ t, st.body ≠ .judgment t) :
    ∃ v, I.views[k]? = some v ∧ v.id = I.d.units[k].id ∧
      reads I I.d.units[k] st = VE.Judgments.dependsOnC I.d.E.rv.definitions I.d.J
        (v.own.toList ++ (exceptionFormulas ((I.d.S.bind (·.rules)) <|> (I.d.R.bind (·.rules)))
          I.d.units[k].content).map .formula) ∧
      (v.set = none → reads I I.d.units[k] st = VE.Judgments.dependsOnC I.d.E.rv.definitions I.d.J
        (v.reads ++ (exceptionFormulas ((I.d.S.bind (·.rules)) <|> (I.d.R.bind (·.rules)))
          I.d.units[k].content).map .formula)) := by
  obtain ⟨-, hv, -⟩ := inputs_reads h
  obtain ⟨v, hvk, hid, hown⟩ := judgedViews_get (hv hJ) k hk
  have heq : reads I I.d.units[k] st = VE.Judgments.dependsOnC I.d.E.rv.definitions I.d.J
      (v.own.toList ++ (exceptionFormulas ((I.d.S.bind (·.rules)) <|> (I.d.R.bind (·.rules)))
        I.d.units[k].content).map .formula) := by
    unfold reads VE.Judgments.dependsOnC
    have hf : ∀ fs : List VE.Formula, (fs.map VE.Judgments.Content.formula).flatMap VE.Judgments.Content.formulas = fs :=
      fun fs => by induction fs <;> simp_all [VE.Judgments.Content.formulas]
    cases hbody : st.body with
    | judgment t => exact absurd hbody (hb t)
    | soft r | premise φ =>
      simp only [hr, hown, List.flatMap_append, hf]
      cases v.own <;> simp [VE.Judgments.Content.formulas]
  refine ⟨v, hvk, hid, heq, fun hs => ?_⟩
  rw [heq, VE.Judgments.UnitView.reads, hs]

/-- The unit table carries each unit's core statements with what they read, so the fold's first OPEN rule (design
2.3: a statement of the unit reads a judgment term) is read on the core statements: the `k`-th row of `tableOf` is
unit `k`'s, with its meaning, and a unit one of whose core statements, in any choice, reads a judgment term
(`reads`) is OPEN whatever the kernel's rows. -/
theorem tableOf_opens (I : Inputs) (docs : List (Choice × CoreDoc)) (k : Nat) (hk : k < I.d.units.length)
    (hm : k < I.meanings.length) (c : Choice × CoreDoc) (hc : c ∈ docs) (st : Statement) (hst : st ∈ c.2.statements)
    (hu : st.origin.unit = I.d.units[k].id) (hr : reads I I.d.units[k] st ≠ []) :
    ∃ row, (tableOf I docs)[k]? = some row ∧ row.id = I.d.units[k].id ∧ row.meaning = I.meanings[k] ∧
      VE.Kernel.DocumentFold.opens row = true ∧
      ∀ rows, VE.Kernel.DocumentFold.status row rows = .opened := by
  have hlen : k < (tableOf I docs).length := by simpa [tableOf] using Nat.lt_min.mpr ⟨hk, hm⟩
  have hmem : (⟨reads I I.d.units[k] st⟩ : VE.Kernel.DocumentFold.Stmt) ∈ docs.flatMap fun (x : Choice × CoreDoc) =>
      (x.2.statements.filter (·.origin.unit == I.d.units[k].id)).map (⟨reads I I.d.units[k] ·⟩) :=
    List.mem_flatMap.mpr ⟨c, hc, List.mem_map.mpr ⟨st, List.mem_filter.mpr ⟨hst, by simp [hu]⟩, rfl⟩⟩
  have hne : (!(⟨reads I I.d.units[k] st⟩ : VE.Kernel.DocumentFold.Stmt).reads.isEmpty) = true := by
    simpa [List.isEmpty_iff] using hr
  have ho : VE.Kernel.DocumentFold.opens ((tableOf I docs)[k]'hlen) = true := by
    simp only [tableOf, List.getElem_map, List.getElem_zip, VE.Kernel.DocumentFold.opens, Bool.or_eq_true]
    refine .inl (.inl (List.any_eq_true.mpr ⟨_, ?_, hne⟩))
    split
    · exact hmem
    · exact List.mem_filter.mpr ⟨hmem, hne⟩
  refine ⟨(tableOf I docs)[k]'hlen, List.getElem?_eq_getElem hlen, by simp [tableOf], by simp [tableOf], ho,
    fun rows => ?_⟩
  unfold VE.Kernel.DocumentFold.status
  rw [if_pos ho]

/-! ## The statements a unit shows -/

/-- A core statement is shown as the case carries it: its premise in the route's formula encoding, the encoding
`factsJson` sends as the case's facts (so it reads back by `facts_round_trip`); its soft rule as the norm object the
case's `norms` carry; a judgment term by its name; with its feature and, for a reading, its set and index. -/
theorem statement_shown (st : Statement) :
    (statementJson st).getObjValD "feature" = .str st.origin.feature ∧
    (∀ φ, st.body = .premise φ → (statementJson st).getObjValD "premise" = VE.Route.Wire.encodeFormula φ ∧
      Json.arr #[(statementJson st).getObjValD "premise"] = factsJson [φ]) ∧
    (∀ r, st.body = .soft r → (statementJson st).getObjValD "rule" = r) ∧
    (∀ t, st.body = .judgment t → (statementJson st).getObjValD "judgment" = .str t.name) ∧
    (∀ s i, st.origin.reading = some (s, i) →
      (statementJson st).getObjValD "reading" = Json.mkObj [("set", .str s), ("index", toJson i)]) := by
  unfold statementJson
  obtain ⟨body, ⟨unit, feature, reading⟩⟩ := st
  cases reading with
  | none =>
    cases body <;>
      refine ⟨by apply getObjValD_mkObj <;> simp, fun φ hφ => ?_, fun r hr => ?_, fun t ht => ?_, fun s i hs => ?_⟩ <;>
      (try cases hφ) <;> (try cases hr) <;> (try cases ht) <;> (try cases hs) <;>
      first
        | (apply getObjValD_mkObj <;> simp; done)
        | (rw [getObjValD_mkObj _ "premise" (VE.Route.Wire.encodeFormula _)]
           · exact ⟨rfl, rfl⟩
           all_goals simp)
  | some si =>
    obtain ⟨s0, i0⟩ := si
    cases body <;>
      refine ⟨by apply getObjValD_mkObj <;> simp, fun φ hφ => ?_, fun r hr => ?_, fun t ht => ?_, fun s i hs => ?_⟩ <;>
      (try cases hφ) <;> (try cases hr) <;> (try cases ht) <;> (try cases hs) <;>
      first
        | (apply getObjValD_mkObj <;> simp; done)
        | (rw [getObjValD_mkObj _ "premise" (VE.Route.Wire.encodeFormula _)]
           · exact ⟨rfl, rfl⟩
           all_goals simp)

end VE.Service.CoreCheck
