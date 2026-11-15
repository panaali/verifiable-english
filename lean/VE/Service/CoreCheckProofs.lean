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
    I.meanings.length = I.d.units.length ∧
    (I.sets.length = I.active.length ∧ ∀ k (hk : k < I.active.length), ∃ c,
      I.sets[k]? = some (I.active[k].1, c) ∧ setCandidates I.d.E I.d.front I.active[k].1 = .ok c) := by
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
      obtain ⟨sets, hs, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      obtain ⟨meanings, hm, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      obtain ⟨_, -, h⟩ := bind_ok h
      cases h
      obtain ⟨hsl, hsg⟩ := mapM_get hs
      refine ⟨rfl, fun hj => ?_, (mapM_get hm).1, hsl, fun k hk => ?_⟩
      · first | exact hy | exact absurd hj hJ
      · obtain ⟨x, hx, hf⟩ := hsg k hk
        obtain ⟨c, hc, hf⟩ := bind_ok hf
        simp only [pure, Except.pure, Except.ok.injEq] at hf
        subst hf
        refine ⟨c, hx, ?_⟩
        cases hsc : setCandidates d.E d.front (VE.Discourse.Loader.activeOf d.all)[k].1 with
        | error e => rw [hsc] at hc; cases hc
        | ok c' => rw [hsc] at hc; cases hc; rfl

theorem judgedViews_get {E : Env} {front : Json} {names : List String} {active : List (VE.Discourse.FrontSet × List Bool)}
    {units : List SourceUnit} {S : Option VE.SoftNorms.Wire.SoftEnvironment} {R : Option RightsDoc}
    {vs : List VE.Judgments.UnitView} (h : judgedViews E front names active units S R = .ok vs) :
    ∃ sets : List (VE.Discourse.FrontSet × List (Option VE.Judgments.Content)),
      (sets.length = active.length ∧ ∀ k (hk : k < active.length), ∃ c,
        sets[k]? = some (active[k].1, c) ∧ setCandidates E front active[k].1 = .ok c) ∧
      ∀ k (hk : k < units.length), ∃ v, vs[k]? = some v ∧ v.id = units[k].id ∧
        (units[k].content.bind fun c => (c.judgedIn S R).toOption).join = v.own ∧
        v.set = (active.find? (·.1.unit == units[k].id)).map fun x =>
          ⟨x.1.status == "authored", x.2.all id, ((sets.find? (·.1 == x.1)).map (·.2)).getD []⟩ := by
  unfold judgedViews at h
  obtain ⟨sets, hs, h⟩ := bind_ok h
  obtain ⟨hsl, hsg⟩ := mapM_get hs
  refine ⟨sets, ⟨hsl, fun k hk => ?_⟩, fun k hk => ?_⟩
  · obtain ⟨x, hx, hf⟩ := hsg k hk
    obtain ⟨c, hc, hf⟩ := bind_ok hf
    simp only [pure, Except.pure, Except.ok.injEq] at hf
    subst hf
    exact ⟨c, hx, hc⟩
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
    exact ⟨rfl, rfl, rfl⟩
  | some c =>
    rw [hc] at hf
    obtain ⟨own, ho, hf⟩ := bind_ok hf
    simp only [pure, Except.pure, Except.ok.injEq] at hf
    subst hf
    refine ⟨rfl, by simp [VE.Judgments.viewOf, ho, Except.toOption], rfl⟩

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
  obtain ⟨_, -, hg⟩ := judgedViews_get (hv hJ)
  obtain ⟨v, hvk, hid, hown, -⟩ := hg k hk
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

theorem sets_eq {active : List (VE.Discourse.FrontSet × List Bool)}
    {f : VE.Discourse.FrontSet → Except String (List (Option VE.Judgments.Content))}
    {A B : List (VE.Discourse.FrontSet × List (Option VE.Judgments.Content))}
    (hA : A.length = active.length ∧ ∀ k (hk : k < active.length), ∃ c, A[k]? = some (active[k].1, c) ∧ f active[k].1 = .ok c)
    (hB : B.length = active.length ∧ ∀ k (hk : k < active.length), ∃ c, B[k]? = some (active[k].1, c) ∧ f active[k].1 = .ok c) :
    A = B := by
  apply List.ext_getElem?
  intro k
  by_cases hk : k < active.length
  · obtain ⟨c, hc, hf⟩ := hA.2 k hk
    obtain ⟨c', hc', hf'⟩ := hB.2 k hk
    rw [hf] at hf'
    cases hf'
    rw [hc, hc']
  · rw [List.getElem?_eq_none (by omega), List.getElem?_eq_none (by omega)]

theorem find?_of_stronger {α : Type} {p q : α → Bool} {x : α} (hq : q x = true) (hqp : ∀ y, q y = true → p y = true) :
    ∀ {l : List α}, l.find? p = some x → l.find? q = some x
  | [], h => by simp at h
  | y :: l, h => by
    rw [List.find?_cons] at h ⊢
    by_cases hp : p y = true
    · rw [hp] at h
      cases h
      rw [hq]
    · have : q y = false := by
        cases hy : q y
        · rfl
        · exact absurd (hqp y hy) hp
      rw [this]
      rw [show p y = false by simpa using hp] at h
      exact find?_of_stronger hq hqp h

/-- The fold reads what `Judgments.status` reads, for a statement of a reading: under `judgments@0`, a core statement
that reading `i` of a unit's active set contributes reads only judgment terms that `Judgments.dependsOnC` finds in
that unit's view (`UnitView.reads`: its active set's candidates), when no earlier active set has the same id. -/
theorem reads_reading {j : Json} {I : Inputs} (h : inputs j = .ok I) (hJ : I.d.judged = true) (k : Nat)
    (hk : k < I.d.units.length) (st : Statement) (rs : VE.Discourse.FrontSet) (kinds : List Bool) (i : Nat)
    (hset : I.active.find? (·.1.unit == I.d.units[k].id) = some (rs, kinds))
    (hfirst : (I.sets.find? (·.1.id == rs.id)).map (·.1) = some rs)
    (hr : st.origin.reading = some (rs.id, i)) (hb : ∀ t, st.body ≠ .judgment t) :
    ∃ v, I.views[k]? = some v ∧ v.id = I.d.units[k].id ∧ v.set.isSome ∧
      ∀ x ∈ reads I I.d.units[k] st, x ∈ VE.Judgments.dependsOnC I.d.E.rv.definitions I.d.J v.reads := by
  obtain ⟨-, hv, -, hsets⟩ := inputs_reads h
  obtain ⟨sets, hsets', hg⟩ := judgedViews_get (hv hJ)
  have heq : I.sets = sets := sets_eq hsets hsets'
  obtain ⟨v, hvk, hid, -, hvset⟩ := hg k hk
  cases hfind : I.sets.find? (·.1.id == rs.id) with
  | none => rw [hfind] at hfirst; cases hfirst
  | some x =>
  obtain ⟨rs', c⟩ := x
  rw [hfind] at hfirst
  simp only [Option.map_some, Option.some.injEq] at hfirst
  subst hfirst
  have hfind' : sets.find? (·.1 == rs') = some (rs', c) := by
    rw [← heq]
    exact find?_of_stronger (p := (·.1.id == rs'.id)) (by simp) (fun y hy => by
      simp only [beq_iff_eq] at hy ⊢
      rw [hy]) hfind
  have hvs : v.set = some ⟨rs'.status == "authored", kinds.all id, c⟩ := by
    rw [hvset, hset]
    simp [hfind']
  refine ⟨v, hvk, hid, by simp [hvs], fun x hx => ?_⟩
  have hreads : reads I I.d.units[k] st = VE.Judgments.dependsOn I.d.E.rv.definitions I.d.J
      ((c[i]?.join.map (·.formulas)).getD []) := by
    unfold reads
    cases hbody : st.body with
    | judgment t => exact absurd hbody (hb t)
    | soft r | premise φ => simp [hr, hfind, Option.bind]
  rw [hreads] at hx
  rw [VE.Judgments.dependsOnC, VE.Judgments.UnitView.reads, hvs]
  obtain ⟨hxJ, φ, hφ, p, hp, hreach⟩ := (VE.Judgments.dependsOn_iff _ _ _ _).mp hx
  refine (VE.Judgments.dependsOn_iff _ _ _ _).mpr ⟨hxJ, φ, ?_, p, hp, hreach⟩
  cases hci : c[i]? with
  | none => simp [hci] at hφ
  | some oc =>
    cases oc with
    | none => simp [hci] at hφ
    | some cc =>
      simp only [hci, Option.join] at hφ
      exact List.mem_flatMap.mpr ⟨cc, List.mem_filterMap.mpr ⟨some cc, List.mem_of_getElem? hci, rfl⟩, hφ⟩

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

/-! ## What `Document.decode` reads -/

/-- `Document.decode`'s role: the values `check` (and the core path) read before the status folds. Its environment is
`environmentOf`'s answer on the front matter it read, with the `core` flag it was given (the flag reaches nothing
else); the document is judged exactly when that environment lists `judgments@0`, and then the environment carries the
admitted judgment names; the units are `unitsOf`'s over that environment. -/
theorem decode_reads (text : String) (lexicon packs governed governedSets parent : Option Json) (core : Bool)
    (d : Document.Decoded)
    (h : Document.decode text lexicon packs governed governedSets parent core = .ok d) :
    ∃ E, environmentOf (d.whole.getObjValD "environment") (d.whole.getObjValD "units") d.senses
        (if d.whole == d.doc.front then some (VE.Discourse.Loader.optionalList d.whole "open_terms") else none) core =
          .ok E ∧
      d.senses = (d.whole.getObjVal? "senses").isOk ∧
      d.judged = E.profiles.contains "judgments@0" ∧
      d.E = (if d.judged then { E with boundNames := some (toJson d.J) } else E) ∧
      ∃ raw, unitsOf d.E d.R d.S d.N d.doc.source d.doc.fences lexicon d.names raw = .ok d.units := by
  unfold decode at h
  extract_lets jp at h
  split at h <;> obtain ⟨_, -, h⟩ := bind_ok h
  all_goals
    simp (config := { zeta := false }) only [jp] at h
    obtain ⟨doc, -, h⟩ := bind_ok h
    -- scope with judgments
    extract_lets front env senses whole a5 a6 a7 at h
    split at h
    · obtain ⟨_, h1, _⟩ := bind_ok h; cases h1
    obtain ⟨_, -, h⟩ := bind_ok h
    simp (config := { zeta := false }) only [a7] at h
    split at h
    · obtain ⟨_, h1, _⟩ := bind_ok h; cases h1
    obtain ⟨_, -, h⟩ := bind_ok h
    simp (config := { zeta := false }) only [a6] at h
    have henv : env = front.getObjValD "environment" := rfl
    have hsenses : senses = (front.getObjVal? "senses").isOk := rfl
    have hwhole : whole = front := rfl
    clear_value env senses whole
    split at h
    rotate_left
    · obtain ⟨_, h1, _⟩ := bind_ok h; cases h1
    obtain ⟨_, -, h⟩ := bind_ok h
    simp (config := { zeta := false }) only [a5] at h
    obtain ⟨E, hE, h⟩ := bind_ok h
    extract_lets b1 b2 b3 at h
    have hjudged : b2 = E.profiles.contains "judgments@0" := rfl
    clear_value b1 b2
    split at h <;> obtain ⟨front', hfront', h⟩ := bind_ok h
    all_goals
      simp (config := { zeta := false }) only [b3] at h
      extract_lets c1 c2 c3 at h
      replace h : c3 PUnit.unit = .ok d := by
        repeat' split at h
        all_goals first | (obtain ⟨_, h1, _⟩ := bind_ok h; cases h1; done) | (obtain ⟨_, -, h⟩ := bind_ok h; exact h)
      simp (config := { zeta := false }) only [c3] at h
      replace h : c2 PUnit.unit = .ok d := by
        repeat' split at h
        all_goals first | (obtain ⟨_, h1, _⟩ := bind_ok h; cases h1; done) | (obtain ⟨_, -, h⟩ := bind_ok h; exact h)
      simp (config := { zeta := false }) only [c2] at h
      obtain ⟨records, h⟩ : ∃ x, c1 x = .ok d := by
        split at h <;> obtain ⟨x, -, h⟩ := bind_ok h <;> exact ⟨x, h⟩
      simp (config := { zeta := false }) only [c1] at h
      extract_lets e1 at h
      obtain ⟨openNames, h⟩ : ∃ x, e1 x = .ok d := by
        split at h <;> obtain ⟨x, -, h⟩ := bind_ok h <;> exact ⟨x, h⟩
      simp (config := { zeta := false }) only [e1] at h
      extract_lets f1 at h
      obtain ⟨J, h⟩ : ∃ x, f1 x = .ok d := by
        split at h <;> obtain ⟨x, -, h⟩ := bind_ok h <;> exact ⟨x, h⟩
      simp (config := { zeta := false }) only [f1] at h
      extract_lets E' g1 at h
      obtain ⟨raw, h⟩ : ∃ x, g1 x = .ok d := by
        repeat' split at h
        all_goals first | (obtain ⟨_, h1, _⟩ := bind_ok h; cases h1; done) | (obtain ⟨x, -, h⟩ := bind_ok h; exact ⟨x, h⟩)
      simp (config := { zeta := false }) only [g1] at h
      extract_lets authored used g4 at h
      obtain ⟨R, h⟩ : ∃ x, g4 x = .ok d := by
        repeat' split at h
        all_goals first | (obtain ⟨_, h1, _⟩ := bind_ok h; cases h1; done) | (obtain ⟨x, -, h⟩ := bind_ok h; exact ⟨x, h⟩)
      simp (config := { zeta := false }) only [g4] at h
      extract_lets g5 at h
      obtain ⟨S, h⟩ : ∃ x, g5 x = .ok d := by
        repeat' split at h
        all_goals first | (obtain ⟨_, h1, _⟩ := bind_ok h; cases h1; done) | (obtain ⟨x, -, h⟩ := bind_ok h; exact ⟨x, h⟩)
      simp (config := { zeta := false }) only [g5] at h
      extract_lets names g7 at h
      obtain ⟨N, h⟩ : ∃ x, g7 x = .ok d := by
        repeat' split at h
        all_goals first | (obtain ⟨_, h1, _⟩ := bind_ok h; cases h1; done) | (obtain ⟨x, -, h⟩ := bind_ok h; exact ⟨x, h⟩)
      simp (config := { zeta := false }) only [g7] at h
      obtain ⟨units, hunits, h⟩ := bind_ok h
      extract_lets unitIds k2 F k4 k5 at h
      replace h : k5 PUnit.unit = .ok d := by
        repeat' split at h
        all_goals first | (obtain ⟨_, h1, _⟩ := bind_ok h; cases h1; done) | (obtain ⟨_, -, h⟩ := bind_ok h; exact h)
      simp (config := { zeta := false }) only [k5] at h
      replace h : k4 PUnit.unit = .ok d := by
        repeat' split at h
        all_goals first | (obtain ⟨_, h1, _⟩ := bind_ok h; cases h1; done) | (obtain ⟨_, -, h⟩ := bind_ok h; exact h)
      simp (config := { zeta := false }) only [k4] at h
      obtain ⟨p, h⟩ : ∃ p, k2 p = .ok d := by
        split at h <;> obtain ⟨x, -, h⟩ := bind_ok h <;> first | exact ⟨x, h⟩ | exact ⟨_, h⟩
      simp (config := { zeta := false }) only [k2, pure, Except.pure, Except.ok.injEq] at h
      subst h
      refine ⟨E, ?_, hsenses ▸ hwhole ▸ rfl, hjudged, rfl, raw, hunits⟩
      dsimp only
      rw [hwhole, ← henv]
      exact hE
end VE.Service.CoreCheck
