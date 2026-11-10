import VE.Service.Document

/-! # The checked view (docs/spec/purpose-explanation.md 5.1; sa-checked-view, DRI 2(d))

One run of the document mode, two outputs: `checkDocSets`'s answer (`checkDocSetsView_answer`) and its typed view.
The view's rows render to the answer's `units` (`checkDocSetsView_rows`): under `scope@0` each row's status is read
back from the unit `VE.Scope.foldGovernors` wrote (`foldedRows`), so the fold keeps one owner. Its candidates are the
kinds of the readings of the active sets the status fold read (`Checked.active`), as written in the front matter the
check read (`candidatesOf`), with their names in the same order (`readings`). `packSources` is empty: for a list with
a pack its content and `packSources_complete` are the pack owner's (5.1). PE-2's `eligible` reads this view. -/

namespace VE.Service.Document
open Lean
open VE.Discourse
open VE.Bridge (stringField)

/-- The typed checked document after the status fold (scope's governor fold included): the answer's rows, its source,
    and each unit under an active reading set with its candidates' kinds. NEW under W2. -/
structure CheckedView where
  source : String
  rows : List RowUnit
  candidates : List (String × List VE.Route.Admission.Kind)
  /-- † PE-R8: the same sets' candidate names, in the same order as `candidates`. -/
  readings : List (String × List String) := []
  /-- † PE-R11: the unit and part ids that the premises the list's packs put in `X` name as their source. -/
  packSources : List String := []

/-- `checkBody`'s run, typed: the case id and the checked document `encode` writes (`checkBodyChecked_encode`). -/
def checkBodyChecked (j : Json) : Except String (String × Checked) := do
  let id ← stringField j "id"
  let text ← stringField j "document"
  let withGraph ← match j.getObjVal? "admit" with
    | .ok (.bool b) => pure b
    | .ok _ => throw "InvalidInput: admit must be a boolean"
    | .error _ => pure true
  let lexicon := (j.getObjVal? "lexicon").toOption
  pure (id, ← check text withGraph lexicon (j.getObjVal? "packs").toOption (j.getObjVal? "units").toOption
    (j.getObjVal? "reading_sets").toOption)

/-- `checkCore`'s run, typed: the case id and the checked document (`checkCoreChecked_encode`). -/
def checkCoreChecked (j : Json) : Except String (String × Checked) :=
  if "scope@0" ∈ profilesOf j then checkBodyChecked j else
  match clashRefusal j with
  | some e => .error e
  | none => checkBodyChecked j

/-- `checkDocSets`'s run, typed: under `scope@0` the scope block it folds by, then the case id and the checked
    document of the case it hands `checkCore`. -/
def checkedRun (j : Json) : Except String (Option VE.Scope.SDoc × String × Checked) :=
  if "scope@0" ∈ profilesOf j then do
    if let some e := clashRefusal j then throw e
    let _ ← VE.Compose.gateOf VE.Compose.profileTable (profilesOf j)
    let D ← VE.Scope.decodeScope j
    let out ← VE.Scope.governSetsWith VE.Scope.governFast D
    let (id, c) ← checkCoreChecked
      (if (VE.Scope.governedSetUnits D).isEmpty then withUnits j out else withSets j out)
    pure (some D, id, c)
  else do
    let (id, c) ← checkCoreChecked j
    pure (none, id, c)

/-- A row with the status the answer's unit `x` carries, when it is one of the four. -/
def readStatus (u : RowUnit) (x : Json) : RowUnit :=
  match ((x.getObjValD "status").getStr?.toOption).bind UnitStatus.ofName? with
  | some s => { u with status := s }
  | none => u

/-- The rows after the governor fold: each with the status of its unit in the folded answer `a`. -/
def foldedRows (rows : List RowUnit) (a : Json) : List RowUnit :=
  match a.getObjValD "units" with
  | .arr xs => (rows.zip xs.toList).map fun (u, x) => readStatus u x
  | _ => rows

/-- The readings of an active set as written in the front matter `front` the check compiled: each reading of the
    set, in the set's order, whose kind W2's decoder reads (`Admission.decodeKind`, as `Loader.compileReading`
    checks it), with its name. -/
def candidatesOf (front : Json) (s : FrontSet) : List (String × VE.Route.Admission.Kind) :=
  let item := ((Loader.optionalList front "reading_sets").getArr?.toOption.getD #[]).toList.find? fun x =>
    x.getObjValD "id" == .str s.id && (x.getObjValD "version").getNat?.toOption == some s.version
  let written := ((item.map (·.getObjValD "readings")).bind (·.getArr?.toOption)).map (·.toList) |>.getD []
  s.readings.filterMap fun (rid, _) => do
    let r ← written.find? (·.getObjValD "id" == .str rid)
    let k ← (VE.Route.Admission.decodeKind 16 (r.getObjValD "kind")).toOption
    pure (rid, k)

/-- Each unit once, at its first entry. -/
def firstPerUnit {α : Type} (xs : List (String × α)) : List (String × α) :=
  xs.foldl (fun acc x => if acc.any (·.1 == x.1) then acc else acc ++ [x]) []

/-- Each unit under an active set the fold read, with its candidates' names and kinds. -/
def unitSets (c : Checked) : List (String × List (String × VE.Route.Admission.Kind)) :=
  firstPerUnit (c.active.map fun (s, _) => (s.unit, candidatesOf c.front s))

/-- The view of a checked document whose answer's rows are `rows`. -/
def viewOf (c : Checked) (rows : List RowUnit) : CheckedView :=
  let us := unitSets c
  { source := c.source, rows, candidates := us.map fun (u, cs) => (u, cs.map (·.2)),
    readings := us.map fun (u, cs) => (u, cs.map (·.1)) }

/-- One run of the document mode, two outputs: the answer and its view. -/
def checkDocSetsView (j : Json) : Except String (Json × CheckedView) := do
  let (D, id, c) ← checkedRun j
  match D with
  | some D =>
    let a := VE.Scope.foldGovernors D (encode id c)
    pure (a, viewOf c (foldedRows c.rows a))
  | none => pure (encode id c, viewOf c c.rows)

/-- The kinds of each active reading set's candidates, from the same `Loader.activeOf` the fold reads. -/
def activeKinds (j : Json) : Except String (List (String × List VE.Route.Admission.Kind)) := do
  let (_, _, c) ← checkedRun j
  pure (firstPerUnit (c.active.map fun (s, _) => (s.unit, (candidatesOf c.front s).map (·.2))))

/-! ## The run is `checkDocSets`'s -/

theorem checkBodyChecked_encode (j : Json) :
    (checkBodyChecked j).map (fun r => encode r.1 r.2) = checkBody j := by
  unfold checkBodyChecked checkBody
  cases stringField j "id" <;> cases stringField j "document" <;> try rfl
  all_goals (rcases j.getObjVal? "admit" with _ | (_ | _ | _ | _ | _ | _))
  all_goals (dsimp only [bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw])
  all_goals (try rfl)
  all_goals (split <;> simp_all [Except.map])

theorem checkCoreChecked_encode (j : Json) :
    (checkCoreChecked j).map (fun r => encode r.1 r.2) = checkCore j := by
  unfold checkCoreChecked checkCore
  split
  · exact checkBodyChecked_encode j
  · cases clashRefusal j
    · exact checkBodyChecked_encode j
    · rfl

/-- The refactor changes no answer. -/
theorem checkDocSetsView_answer (j : Json) : (checkDocSetsView j).map (·.1) = checkDocSets j := by
  unfold checkDocSetsView checkedRun checkDocSets
  by_cases hs : "scope@0" ∈ profilesOf j
  · simp only [hs, if_true, ← checkCoreChecked_encode]
    cases clashRefusal j with
    | some e => rfl
    | none =>
      simp only [bind, Except.bind, pure, Except.pure]
      cases VE.Compose.gateOf VE.Compose.profileTable (profilesOf j) with
      | error e => rfl
      | ok g =>
        simp only
        cases VE.Scope.decodeScope j with
        | error e => rfl
        | ok D =>
          simp only
          cases VE.Scope.governSetsWith VE.Scope.governFast D with
          | error e => rfl
          | ok out =>
            simp only
            cases checkCoreChecked
              (if (VE.Scope.governedSetUnits D).isEmpty then withUnits j out else withSets j out) <;> rfl
  · simp only [hs, if_false, ← checkCoreChecked_encode]
    cases checkCoreChecked j <;> rfl

/-! ## The view is the answer -/

theorem unitJson_status (u : RowUnit) (s : UnitStatus) :
    (unitJson u).setObjVal! "status" (.str s.name) = unitJson { u with status := s } ∧
      (unitJson u).getObjValD "status" = .str u.status.name := by
  obtain ⟨id, span, kind, meaning, support, status, parent, content, mid⟩ := u
  cases parent <;> cases content <;> cases mid <;> exact ⟨rfl, rfl⟩

theorem readStatus_unitJson (u : RowUnit) (s : UnitStatus) :
    readStatus u (unitJson { u with status := s }) = { u with status := s } := by
  unfold readStatus
  rw [(unitJson_status _ s).2]
  cases s <;> rfl

/-- The fold writes one of the four statuses or none: the meet of statuses it read as one of the four. -/
theorem foldStatus_known (xs : List VE.Reports.Status) (h : ∀ x ∈ xs, x ≠ .unknown) :
    VE.Reports.foldStatus xs ≠ .unknown := by
  unfold VE.Reports.foldStatus
  suffices ∀ a, a ≠ .unknown → xs.foldl VE.Reports.Status.meet a ≠ .unknown from this _ (by decide)
  induction xs with
  | nil => exact fun _ ha => ha
  | cons x xs ih =>
    intro a ha
    apply ih (fun y hy => h y (List.mem_cons_of_mem _ hy))
    unfold VE.Reports.Status.meet
    split <;> first | exact ha | exact h x (List.mem_cons_self ..)

theorem mapM_known (st : String → Option VE.Reports.Status) (hs : ∀ x s, st x = some s → s ≠ .unknown) :
    ∀ (us : List String) (xs : List VE.Reports.Status), us.mapM st = some xs → ∀ x ∈ xs, x ≠ .unknown := by
  intro us
  induction us with
  | nil => intro xs h; simp at h; subst h; simp
  | cons u us ih =>
    intro xs h
    simp only [List.mapM_cons, Option.bind_eq_bind] at h
    cases hu : st u <;> cases hm : us.mapM st <;> simp [hu, hm] at h
    subst h
    exact fun x hx => (List.mem_cons.mp hx).elim (· ▸ hs u _ hu) (ih _ hm x)

theorem statusOf_known (x : String) (s : VE.Reports.Status) (h : VE.Scope.statusOf x = some s) : s ≠ .unknown := by
  unfold VE.Scope.statusOf at h
  split at h <;> cases h <;> decide

theorem governorStatus_known (st : String → Option VE.Reports.Status) (hs : ∀ x s, st x = some s → s ≠ .unknown)
    (us : List String) : ((VE.Scope.governorStatus st us).getD .unformalised) ≠ .unknown := by
  unfold VE.Scope.governorStatus
  split
  · decide
  · cases h : us.mapM st with
    | none => decide
    | some xs => exact foldStatus_known xs (mapM_known st hs us xs h)

theorem render_name (S : VE.Reports.Status) (h : S ≠ .unknown) : ∃ s : UnitStatus, s.name = S.render := by
  cases S <;> first | exact absurd rfl h | exact ⟨.unformalised, rfl⟩ | exact ⟨.opened, rfl⟩ |
    exact ⟨.labelled, rfl⟩ | exact ⟨.checked, rfl⟩

/-- A unit the fold leaves or gives a known status is the rendering of its row read back. -/
theorem readStatus_fold (u : RowUnit) (y : Json)
    (h : y = unitJson u ∨ ∃ S : VE.Reports.Status, S ≠ .unknown ∧ y = (unitJson u).setObjVal! "status" (.str S.render)) :
    unitJson (readStatus u y) = y := by
  rcases h with h | ⟨S, hS, h⟩
  · subst h; exact congrArg unitJson (readStatus_unitJson u u.status)
  · obtain ⟨s, hs⟩ := render_name S hS
    rw [← hs, (unitJson_status u s).1] at h
    subst h
    exact congrArg unitJson (readStatus_unitJson u s)

theorem foldedRows_zip (f : Json → Json) (hf : ∀ u, unitJson (readStatus u (f (unitJson u))) = f (unitJson u)) :
    ∀ rows : List RowUnit, (rows.zip (rows.map (f ∘ unitJson))).map (fun p => unitJson (readStatus p.1 p.2)) =
      rows.map (f ∘ unitJson) := by
  intro rows
  induction rows with
  | nil => rfl
  | cons u us ih =>
    simp only [List.map_cons, List.zip_cons_cons, Function.comp_apply]
    congr 1
    · exact hf u

theorem encode_units (id : String) (c : Checked) :
    (encode id c).getObjValD "units" = toJson (c.rows.map unitJson) ∧
      (encode id c).getObjValD "source" = .str c.source := by
  unfold encode VE.Route.Wire.ok
  cases c.judgments <;> cases c.cardinality <;> exact ⟨rfl, rfl⟩

theorem toJson_jsons (l : List Json) : toJson l = Json.arr l.toArray := by
  show Json.arr (l.toArray.map toJson) = _
  congr 1
  exact Array.map_id'' (fun _ => rfl) _

theorem mkObj_answer (i st did sid src us cov : Json) :
    (Json.mkObj [("id", i), ("status", st), ("document_id", did), ("source_id", sid), ("source", src),
      ("units", us), ("coverage", cov)]).getObjValD "units" = us ∧
    (Json.mkObj [("id", i), ("status", st), ("document_id", did), ("source_id", sid), ("source", src),
      ("units", us), ("coverage", cov)]).getObjValD "source" = src := ⟨rfl, rfl⟩

theorem rows_of_fold (F : Json → Json) (hF : ∀ u, F (unitJson u) = unitJson u ∨
      ∃ S : VE.Reports.Status, S ≠ .unknown ∧ F (unitJson u) = (unitJson u).setObjVal! "status" (.str S.render))
    (rows : List RowUnit) :
    Json.arr ((rows.map unitJson).map F).toArray =
      Json.arr (((rows.zip ((rows.map unitJson).map F)).map fun p => readStatus p.1 p.2).map unitJson).toArray := by
  congr 1
  rw [List.map_map, List.map_map]
  exact congrArg List.toArray (foldedRows_zip F (fun u => readStatus_fold u _ (hF u)) rows).symm

/-- Scope's fold keeps the source, and each unit it writes is its row with the status read back. -/
theorem foldGovernors_rows (D : VE.Scope.SDoc) (a : Json) (rows : List RowUnit)
    (ha : a.getObjValD "units" = toJson (rows.map unitJson)) :
    (VE.Scope.foldGovernors D a).getObjValD "units" =
      toJson ((foldedRows rows (VE.Scope.foldGovernors D a)).map unitJson) ∧
    (VE.Scope.foldGovernors D a).getObjValD "source" = a.getObjValD "source" := by
  unfold VE.Scope.foldGovernors foldedRows
  simp only [ha, toJson_jsons, mkObj_answer]
  refine ⟨rows_of_fold _ ?_ rows, trivial⟩
  intro u
  split
  · exact .inl rfl
  · refine .inr ⟨_, governorStatus_known _ ?_ _, rfl⟩
    intro x s h
    obtain ⟨y, -, hy⟩ := Option.bind_eq_some_iff.mp h
    exact statusOf_known y s hy

/-- The view is the answer: its rows render to the answer's `units`, and its source is the answer's. -/
theorem checkDocSetsView_rows (j a : Json) (V : CheckedView) (h : checkDocSetsView j = .ok (a, V)) :
    a.getObjValD "units" = toJson (V.rows.map unitJson) ∧ a.getObjValD "source" = .str V.source := by
  unfold checkDocSetsView at h
  cases hr : checkedRun j with
  | error e => simp [hr, bind, Except.bind] at h
  | ok r =>
    obtain ⟨D, id, c⟩ := r
    simp only [hr, bind, Except.bind, pure, Except.pure] at h
    obtain ⟨he, hu⟩ := encode_units id c
    cases D <;> simp only [Except.ok.injEq, Prod.mk.injEq] at h <;> obtain ⟨rfl, rfl⟩ := h
    · exact ⟨he, hu⟩
    · obtain ⟨h1, h2⟩ := foldGovernors_rows _ (encode id c) c.rows he
      exact ⟨h1, h2.trans hu⟩

/-! ## Candidates, readings and pack sources -/

theorem firstPerUnit_foldl {α β : Type} (g : α → β) : ∀ (xs acc : List (String × α)),
    (xs.foldl (fun acc x => if acc.any (·.1 == x.1) then acc else acc ++ [x]) acc).map (fun p => (p.1, g p.2)) =
      (xs.map fun p => (p.1, g p.2)).foldl (fun acc x => if acc.any (·.1 == x.1) then acc else acc ++ [x])
        (acc.map fun p => (p.1, g p.2)) := by
  intro xs
  induction xs with
  | nil => intro acc; rfl
  | cons x xs ih =>
    intro acc
    simp only [List.foldl_cons, List.map_cons]
    rw [ih]
    congr 1
    simp only [List.any_map, Function.comp_def]
    split <;> simp_all

theorem firstPerUnit_map {α β : Type} (g : α → β) (xs : List (String × α)) :
    (firstPerUnit xs).map (fun p => (p.1, g p.2)) = firstPerUnit (xs.map fun p => (p.1, g p.2)) :=
  firstPerUnit_foldl g xs []

theorem firstPerUnit_nodup {α : Type} : ∀ (xs acc : List (String × α)), (acc.map (·.1)).Nodup →
    ((xs.foldl (fun acc x => if acc.any (·.1 == x.1) then acc else acc ++ [x]) acc).map (·.1)).Nodup := by
  intro xs
  induction xs with
  | nil => intro acc h; exact h
  | cons x xs ih =>
    intro acc h
    simp only [List.foldl_cons]
    apply ih
    split
    · exact h
    · rename_i hx
      rw [List.map_append, List.nodup_append]
      refine ⟨h, List.nodup_cons.mpr ⟨List.not_mem_nil, List.nodup_nil⟩, ?_⟩
      intro a ha b hb hab
      simp only [List.map_cons, List.map_nil, List.mem_singleton] at hb
      obtain ⟨y, hy, rfl⟩ := List.mem_map.mp ha
      exact hx (List.any_eq_true.mpr ⟨y, hy, by simp [hab, hb]⟩)

theorem unique_key {α : Type} : ∀ (l : List (String × α)), (l.map (·.1)).Nodup →
    ∀ p q, p ∈ l → q ∈ l → p.1 = q.1 → p = q := by
  intro l
  induction l with
  | nil => intro _ p q hp; cases hp
  | cons x l ih =>
    intro h p q hp hq he
    rw [List.map_cons, List.nodup_cons] at h
    rcases List.mem_cons.mp hp with rfl | hp' <;> rcases List.mem_cons.mp hq with rfl | hq'
    · rfl
    · exact absurd (he ▸ List.mem_map_of_mem hq') h.1
    · exact absurd (he.symm ▸ List.mem_map_of_mem hp') h.1
    · exact ih h.2 p q hp' hq' he

/-- A successful run's view is the view of its checked document. -/
theorem checkDocSetsView_ok (j a : Json) (V : CheckedView) (h : checkDocSetsView j = .ok (a, V)) :
    ∃ D id c, checkedRun j = .ok (D, id, c) ∧ ∃ rows, V = viewOf c rows := by
  unfold checkDocSetsView at h
  cases hr : checkedRun j with
  | error e => simp [hr, bind, Except.bind] at h
  | ok r =>
    obtain ⟨D, id, c⟩ := r
    simp only [hr, bind, Except.bind, pure, Except.pure] at h
    refine ⟨D, id, c, rfl, ?_⟩
    cases D <;> simp only [Except.ok.injEq, Prod.mk.injEq] at h <;> exact ⟨_, h.2.symm⟩

theorem checkDocSetsView_candidates (j a : Json) (V : CheckedView) (h : checkDocSetsView j = .ok (a, V)) :
    activeKinds j = .ok V.candidates := by
  obtain ⟨D, id, c, hr, rows, rfl⟩ := checkDocSetsView_ok j a V h
  unfold activeKinds viewOf unitSets
  simp only [hr, bind, Except.bind, pure, Except.pure]
  simp only [firstPerUnit_map, List.map_map, Function.comp_def]

/-- † PE-R8: one name per candidate kind, for the same units in the same order. -/
theorem checkDocSetsView_readings (j a : Json) (V : CheckedView) (h : checkDocSetsView j = .ok (a, V)) :
    V.readings.map (·.1) = V.candidates.map (·.1) ∧
      ∀ i ns ks, (i, ns) ∈ V.readings → (i, ks) ∈ V.candidates → ns.length = ks.length := by
  obtain ⟨D, id, c, -, rows, rfl⟩ := checkDocSetsView_ok j a V h
  unfold viewOf
  refine ⟨by simp only [List.map_map]; rfl, ?_⟩
  intro i ns ks hn hk
  obtain ⟨p, hp, hpe⟩ := List.mem_map.mp hn
  obtain ⟨q, hq, hqe⟩ := List.mem_map.mp hk
  have hpq : p = q := unique_key _ (firstPerUnit_nodup _ [] List.nodup_nil) p q hp hq
    ((congrArg Prod.fst hpe).trans (congrArg Prod.fst hqe).symm)
  subst hpq
  have h1 := congrArg Prod.snd hpe
  have h2 := congrArg Prod.snd hqe
  simp only at h1 h2
  rw [← h1, ← h2, List.length_map, List.length_map]

-- `hn` is the spec's hypothesis: this item fills no pack source, so the proof does not read it (5.1, pack sources).
set_option linter.unusedVariables false in
/-- † PE-R11: a list with no pack gives no pack source. -/
theorem checkDocSetsView_packs (j a : Json) (V : CheckedView) (h : checkDocSetsView j = .ok (a, V))
    (hn : ∀ p ∈ ["weighing@0", "attitudes@0", "scales@0", "events@0"], p ∉ profilesOf j) :
    V.packSources = [] := by
  obtain ⟨D, id, c, -, rows, rfl⟩ := checkDocSetsView_ok j a V h
  rfl

end VE.Service.Document
