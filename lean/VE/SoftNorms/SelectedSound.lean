import VE.SoftNorms.Run

/-! The wire theorem of the soft route's `soft-selected` kind (kb-10a, kernel boundary).

`soft_wire_selected` states the whole answer: it is exactly `Wire.ok id` with the two fields
`background` and `results`, no other field, and one result per query of the request, in order,
naming the request's predicate and tuple, with `selected = selectedAt` and `outcome = outcomeAt`
for the source and the model the case's own decoders read. `selected_semantics` (`Selected.lean`)
says what `selectedAt` and `outcomeAt` mean; each decoded query carries its hypotheses
(`QueryDecoded`: a regulated predicate, a tuple typed for its sorts).

kb-9: a case that sends `facts` gets two more fields (`factsFields`), read in the same model.
`soft_wire_selected_facts` states the whole answer with them: the facts are the slot kinds' decoded
`P`, `facts` is present exactly when the member was sent and is true exactly when every fact holds in
the model. `selected_model_admissible`: when `background`, `coherent` and `facts` are all true, the
case model is a base structure admissible for the slot `P` (`BaseAdmissibleP`), one of those
`VE.Compose.slot_route_acceptance` quantifies over. One case, one theorem: nothing is carried
between calls (docs/spec/kernel-boundary.md 8.1). -/
namespace VE.SoftNorms.Run
open Lean
open VE.Norms
open VE.SoftNorms.Wire
open VE.Order.ProfileGate (bind_ok)

/-- A query as decoded: the predicate and the ids exactly as the request sent them, a regulated
predicate of the document, and the tuple its sorts paired with the ids, typed in `M`. -/
def QueryDecoded (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) (raw : Json) (q : SelectedQuery) :
    Prop :=
  raw.getObjValD "predicate" = .str q.pred ∧ VE.Bridge.strings (raw.getObjValD "tuple") = .ok q.ids ∧
  q.pred ∈ D.T.regulated.map (·.name) ∧ q.tuple = (sortsOf D q.pred).zip q.ids ∧
  VE.TupleTyped M.asStructure (sortsOf D q.pred) q.tuple

/-- The `soft-selected` answer for `D`, `M`, the decoded queries and the fields `extra` after
`results`, written out field by field (a closed list). -/
def SelectedAnswerWith (id : String) (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (qs : List SelectedQuery) (extra : List (String × Json)) (answer : Json) : Prop :=
  answer = VE.Route.Wire.ok id ([("background", .bool (classificationBackgroundValid D M)),
    ("results", Json.arr (qs.map fun q => Json.mkObj [("predicate", .str q.pred), ("tuple", toJson q.ids),
      ("selected", toJson (selectedAt D M q.pred q.tuple)),
      ("outcome", .bool (outcomeAt D M q.pred q.tuple))]).toArray)] ++ extra)

/-- The `soft-selected` answer for `D`, `M` and the decoded queries: no field beyond `id`, `status`,
`background`, `results` and, for a case that sent `facts`, `facts` and `coherent` (`coherentAt`).
`soft_wire_selected_facts` states which and what `facts` is. -/
def SelectedAnswer (id : String) (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (qs : List SelectedQuery) (answer : Json) : Prop :=
  ∃ sent facts, SelectedAnswerWith id D M qs (factsFields sent facts (coherentAt D M)) answer

theorem getStr_ok {x : Json} {s : String} (h : x.getStr? = .ok s) : x = .str s := by
  cases x <;> simp [Json.getStr?] at h <;> first | (cases h; rfl) | (rename_i e; cases e)

theorem decodeSelectedQuery_ok {D : SoftDoc} {M : VE.FiniteModel VE.Bridge.Entity} {i : Nat} {raw : Json}
    {q : SelectedQuery} (h : decodeSelectedQuery D M i raw = .ok q) : QueryDecoded D M raw q := by
  unfold decodeSelectedQuery at h
  split at h
  · cases h
  · cases h
  · rename_i p ids hp hi
    split at h
    · cases h
    · split at h
      · rename_i hr ht
        cases h
        simp only [Bool.and_eq_true] at ht
        refine ⟨getStr_ok hp, hi, ?_, rfl, (VE.Bridge.tupleCheck_iff M _ _).mp ht.2⟩
        simpa using hr
      · cases h

/-- The decoded queries: one per request query, in order. -/
theorem decodeQueries_ok {D : SoftDoc} {M : VE.FiniteModel VE.Bridge.Entity} :
    ∀ {i : Nat} {raws : List Json} {qs : List SelectedQuery}, decodeQueries D M i raws = .ok qs →
      qs.length = raws.length ∧ (∀ x ∈ raws.zip qs, QueryDecoded D M x.1 x.2) ∧
        ∀ q ∈ qs, q.pred ∈ D.T.regulated.map (·.name)
  | _, [], qs, h => by
    simp only [decodeQueries, pure, Except.pure, Except.ok.injEq] at h
    subst h
    simp
  | i, r :: rs, qs, h => by
    unfold decodeQueries at h
    obtain ⟨x, hx, h⟩ := bind_ok h
    obtain ⟨xs, hxs, h⟩ := bind_ok h
    simp only [pure, Except.pure, Except.ok.injEq] at h
    subst h
    obtain ⟨hl, hall, hreg⟩ := decodeQueries_ok hxs
    refine ⟨by simp [hl], ?_, ?_⟩
    · intro y hy
      rcases List.mem_cons.mp hy with rfl | hy
      · exact decodeSelectedQuery_ok hx
      · exact hall y hy
    · intro y hy
      rcases List.mem_cons.mp hy with rfl | hy
      · exact (decodeSelectedQuery_ok hx).2.2.1
      · exact hreg y hy

/-- The case's queries: a non-empty array, one decoded query per request query, in order, each
bound to the request's query at its position and naming a regulated predicate. -/
theorem selectedQueries_ok {D : SoftDoc} {M : VE.FiniteModel VE.Bridge.Entity} {j : Json}
    {qs : List SelectedQuery} (h : selectedQueries D M j = .ok qs) :
    ∃ raws : Array Json, j.getObjValD "queries" = Json.arr raws ∧ raws.toList ≠ [] ∧
      qs.length = raws.size ∧ (∀ x ∈ raws.toList.zip qs, QueryDecoded D M x.1 x.2) ∧
      ∀ q ∈ qs, q.pred ∈ D.T.regulated.map (·.name) := by
  unfold selectedQueries at h
  split at h
  · rename_i raw hq
    split at h
    · cases h
    · rename_i hne
      split at h
      · cases h
      obtain ⟨hl, hall, hreg⟩ := decodeQueries_ok h
      exact ⟨raw, hq, by simpa [Array.isEmpty] using hne, by simpa using hl, hall, hreg⟩
  · cases h

/-- The kind's runner: the case's decoders read the source, the facts, the model and a non-empty list
of queries, each bound to the request's query at its position, and the answer is `SelectedAnswerWith`
the facts' fields (one expansion per case, read back as `selectedAt` and `outcomeAt` by
`selectedRow_eq`). -/
theorem runSelected_answer (id : String) (j answer : Json) (h : runSelected id j = .ok answer) :
    ∃ (environment : Json) (src : SoftSource) (P : List VE.Formula) (items : List Json)
      (M : VE.FiniteModel VE.Bridge.Entity)
      (hM : M.Valid (envAt (soften src.D) 0)) (raws : Array Json) (qs : List SelectedQuery),
      j.getObjVal? "environment" = .ok environment ∧
      decodeSoftSource environment (j.getObjValD "norms") = .ok src ∧
      VE.Compose.SlotWire.decodeFacts src j = .ok (P, items) ∧
      decodeModel src j = .ok ⟨M, hM⟩ ∧
      j.getObjValD "queries" = Json.arr raws ∧ raws.toList ≠ [] ∧
      qs.length = raws.size ∧ (∀ x ∈ raws.toList.zip qs, QueryDecoded src.D M x.1 x.2) ∧
      SelectedAnswerWith id src.D M qs (factsFields (factsSent j) (factsAt P M) (coherentAt src.D M)) answer := by
  unfold runSelected at h
  obtain ⟨environment, henv, h⟩ := bind_ok h
  obtain ⟨src, hsrc, h⟩ := bind_ok h
  obtain ⟨⟨P, items⟩, hf, h⟩ := bind_ok h
  obtain ⟨⟨M, hM⟩, hmod, h⟩ := bind_ok h
  obtain ⟨qs, hqs, h⟩ := bind_ok h
  simp only [pure, Except.pure, Except.ok.injEq] at h
  subst h
  obtain ⟨raw, hq, hne, hl, hall, hreg⟩ := selectedQueries_ok hqs
  refine ⟨environment, src, P, items, M, hM, raw, qs, henv, hsrc, hf, hmod, hq, hne, hl, hall, ?_⟩
  unfold SelectedAnswerWith
  rw [List.map_congr_left (fun q hq => selectedRow_eq src.D M q (hreg q hq))]

/-- A field of an object with distinct keys reads its value; a key it lacks reads no value. -/
theorem mkObj_getObjVal_mem {l : List (String × Json)} {k : String} {v : Json} (hn : (l.map (·.1)).Nodup)
    (hm : (k, v) ∈ l) : (Json.mkObj l).getObjVal? k = .ok v := by
  have hp : l.Pairwise (fun a b => ¬ compare a.1 b.1 = .eq) :=
    (List.pairwise_map.mp hn).imp (fun hne heq => hne (Std.LawfulEqOrd.eq_of_compare heq))
  simp only [Json.mkObj, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?,
    Std.TreeMap.Raw.getElem?_ofList_of_mem (cmp := compare) (k_eq := Std.ReflCmp.compare_self) hp hm]
  rfl

theorem mkObj_getObjVal_not_mem {l : List (String × Json)} {k : String} (hk : (l.map (·.1)).contains k = false) :
    (Json.mkObj l).getObjVal? k = .error s!"property not found: {k}" := by
  simp only [Json.mkObj, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?,
    Std.TreeMap.Raw.getElem?_ofList_of_contains_eq_false hk]
  rfl

/-- The `soft-selected` case's runner, with its id. -/
theorem runCase_selected_run (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "soft-selected") (hn : usesSoftPath j = true) :
    ∃ id, VE.Bridge.stringField j "id" = .ok id ∧ runSelected id j = .ok answer := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "soft-selected" := by rw [hkind] at hk; cases hk; rfl
  subst heq
  simp only [hn, show ("soft-selected" == "admission") = false from by decide, Bool.false_and,
    Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
  unfold runSoftKind at h
  simp only [show ("soft-selected" == "soft-selected") = true from by decide, ↓reduceIte] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨res, hres, h⟩ := bind_ok h
  simp only [pure, Except.pure, Except.ok.injEq] at h
  subst h
  exact ⟨id, hid, hres⟩

/-- The soft route's answer to a `soft-selected` case: the case's own decoders read the source,
the model and a non-empty list of queries, each decoded query is bound to the request's query at
its position and carries `selected_semantics`'s hypotheses, and the answer is exactly the
`SelectedAnswer` for them: `background` is `classificationBackgroundValid`, and each result has
`selected = selectedAt` and `outcome = outcomeAt`. -/
theorem soft_wire_selected (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "soft-selected") (hn : usesSoftPath j = true) :
    ∃ (id : String) (environment : Json) (src : SoftSource) (M : VE.FiniteModel VE.Bridge.Entity)
      (hM : M.Valid (envAt (soften src.D) 0)) (raws : Array Json) (qs : List SelectedQuery),
      VE.Bridge.stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok environment ∧
      decodeSoftSource environment (j.getObjValD "norms") = .ok src ∧
      decodeModel src j = .ok ⟨M, hM⟩ ∧
      j.getObjValD "queries" = Json.arr raws ∧ raws.toList ≠ [] ∧
      qs.length = raws.size ∧ (∀ x ∈ raws.toList.zip qs, QueryDecoded src.D M x.1 x.2) ∧
      SelectedAnswer id src.D M qs answer := by
  obtain ⟨id, hid, h⟩ := runCase_selected_run j answer h hk hn
  obtain ⟨environment, src, _, _, M, hM, raws, qs, h₁, h₂, _, h₃, h₄, h₅, h₆, h₇, h₈⟩ := runSelected_answer id j answer h
  exact ⟨id, environment, src, M, hM, raws, qs, hid, h₁, h₂, h₃, h₄, h₅, h₆, h₇, ⟨_, _, h₈⟩⟩

/-! ## Facts and coherence (kb-9) -/

/-- The `facts` and `coherent` fields of a `SelectedAnswerWith` the facts' fields: present exactly when
`facts` was sent, with the flags' values. -/
theorem selectedAnswer_flags {id : String} {D : SoftDoc} {M : VE.FiniteModel VE.Bridge.Entity}
    {qs : List SelectedQuery} {sent b c : Bool} {answer : Json}
    (h : SelectedAnswerWith id D M qs (factsFields sent b c) answer) :
    (sent = true → answer.getObjVal? "facts" = .ok (.bool b) ∧ answer.getObjVal? "coherent" = .ok (.bool c)) ∧
    (sent = false → (∃ e, answer.getObjVal? "facts" = .error e) ∧ ∃ e, answer.getObjVal? "coherent" = .error e) := by
  unfold SelectedAnswerWith VE.Route.Wire.ok at h
  subst h
  constructor
  · intro hs
    subst hs
    exact ⟨mkObj_getObjVal_mem (by simp [factsFields]) (by simp [factsFields]),
      mkObj_getObjVal_mem (by simp [factsFields]) (by simp [factsFields])⟩
  · intro hs
    subst hs
    exact ⟨⟨_, mkObj_getObjVal_not_mem (by simp [factsFields])⟩, ⟨_, mkObj_getObjVal_not_mem (by simp [factsFields])⟩⟩

/-- (kb-9, a) `soft_wire_selected`'s conclusion, the facts, and the whole answer with them: the facts
are the slot kinds' decoded `P` (`decodeFacts`, closed and well-formed over the base vocabulary), the
answer is `SelectedAnswerWith` the facts' fields, `facts` and `coherent` are present exactly when the
case sent `facts`, and `facts` is true exactly when every fact holds in the model's structure. -/
theorem soft_wire_selected_facts (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "soft-selected") (hn : usesSoftPath j = true) :
    ∃ (id : String) (environment : Json) (src : SoftSource) (M : VE.FiniteModel VE.Bridge.Entity)
      (hM : M.Valid (envAt (soften src.D) 0)) (raws : Array Json) (qs : List SelectedQuery)
      (P : List VE.Formula) (items : List Json),
      VE.Bridge.stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok environment ∧
      decodeSoftSource environment (j.getObjValD "norms") = .ok src ∧
      decodeModel src j = .ok ⟨M, hM⟩ ∧
      j.getObjValD "queries" = Json.arr raws ∧ raws.toList ≠ [] ∧
      qs.length = raws.size ∧ (∀ x ∈ raws.toList.zip qs, QueryDecoded src.D M x.1 x.2) ∧
      SelectedAnswer id src.D M qs answer ∧
      VE.Compose.SlotWire.decodeFacts src j = .ok (P, items) ∧
      (∀ φ ∈ P, φ.WellFormed (envAt (soften src.D) 0) []) ∧
      SelectedAnswerWith id src.D M qs (factsFields (factsSent j) (factsAt P M) (coherentAt src.D M)) answer ∧
      (factsSent j = true ↔ ∃ v, j.getObjVal? "facts" = .ok v) ∧
      (factsSent j = true → ∃ b, answer.getObjVal? "facts" = .ok (.bool b) ∧
        (b = true ↔ ∀ φ ∈ P, φ.denote M.asStructure [])) ∧
      (factsSent j = false → (∃ e, answer.getObjVal? "facts" = .error e) ∧
        ∃ e, answer.getObjVal? "coherent" = .error e) := by
  obtain ⟨id, hid, h⟩ := runCase_selected_run j answer h hk hn
  obtain ⟨environment, src, P, items, M, hM, raws, qs, h₁, h₂, hf, h₃, h₄, h₅, h₆, h₇, h₈⟩ :=
    runSelected_answer id j answer h
  have hfl := selectedAnswer_flags h₈
  refine ⟨id, environment, src, M, hM, raws, qs, P, items, hid, h₁, h₂, h₃, h₄, h₅, h₆, h₇, ⟨_, _, h₈⟩, hf,
    (VE.Compose.SlotWire.decodeFacts_ok hf).1, h₈, ?_, fun hs => ⟨_, (hfl.1 hs).1, ?_⟩, hfl.2⟩
  · unfold factsSent
    cases j.getObjVal? "facts" <;> simp
  · simp only [factsAt, List.all_eq_true]
    exact ⟨fun hb φ hφ => (VE.eval_iff_denote M [] φ).mp (hb φ hφ),
      fun hd φ hφ => (VE.eval_iff_denote M [] φ).mpr (hd φ hφ)⟩

/-- The `coherent` flag is true exactly when every coherence conjunct holds in the model's structure. -/
theorem coherentAt_iff (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity) :
    coherentAt D M = true ↔ ∀ a ∈ cohPremises D, a.denote M.asStructure [] := by
  simp only [coherentAt, List.all_eq_true]
  exact ⟨fun hb a ha => (VE.eval_iff_denote M [] a).mp (hb a ha),
    fun hd a ha => (VE.eval_iff_denote M [] a).mpr (hd a ha)⟩

/-- The step of `selected_model_admissible`: a model whose `background`, `coherent` and `facts` flags are all true
is a base structure admissible for the slot `P` (`backgroundValid'` is `background` and `coherent`, since
`softPremises = excPremises ++ cohPremises`; then `baseAdmissibleP_of_valid`, the check `factsModel` uses). -/
theorem model_admissible_of_flags (D : SoftDoc) (P : List VE.Formula) (M : VE.FiniteModel VE.Bridge.Entity)
    (hM : M.Valid (envAt (soften D) 0)) (hb : classificationBackgroundValid D M = true)
    (hc : coherentAt D M = true) (hf : factsAt P M = true) :
    VE.Compose.BaseAdmissibleP D P M.asStructure := by
  apply VE.Compose.baseAdmissibleP_of_valid D P M hM
  simp only [VE.Compose.backgroundValidP, backgroundValid', softPremises, List.all_append, Bool.and_eq_true]
  simp only [classificationBackgroundValid, Bool.and_eq_true] at hb
  exact ⟨⟨hb.1, hb.2, hc⟩, hf⟩

/-- (kb-9, b) A `soft-selected` answer whose `background`, `coherent` and `facts` are all `true`: the case model,
read by the case's own decoders, is a base structure admissible for the slot `P` of the case's own facts
(`BaseAdmissibleP`), one of the structures `VE.Compose.slot_route_acceptance` quantifies over. So what the slot
route proves from the document and these facts holds in the model the selected rules were read in. -/
theorem selected_model_admissible (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "soft-selected") (hn : usesSoftPath j = true)
    (hb : answer.getObjVal? "background" = .ok (.bool true))
    (hc : answer.getObjVal? "coherent" = .ok (.bool true))
    (hf : answer.getObjVal? "facts" = .ok (.bool true)) :
    ∃ (environment : Json) (src : SoftSource) (M : VE.FiniteModel VE.Bridge.Entity)
      (hM : M.Valid (envAt (soften src.D) 0)) (P : List VE.Formula) (items : List Json),
      j.getObjVal? "environment" = .ok environment ∧
      decodeSoftSource environment (j.getObjValD "norms") = .ok src ∧
      decodeModel src j = .ok ⟨M, hM⟩ ∧
      VE.Compose.SlotWire.decodeFacts src j = .ok (P, items) ∧
      VE.Compose.BaseAdmissibleP src.D P M.asStructure := by
  obtain ⟨id, _, hrun⟩ := runCase_selected_run j answer h hk hn
  obtain ⟨environment, src, P, items, M, hM, _, _, h₁, h₂, hfd, h₃, _, _, _, _, h₈⟩ :=
    runSelected_answer id j answer hrun
  have hs : factsSent j = true := by
    cases hsj : factsSent j
    · obtain ⟨⟨e, he⟩, _⟩ := (selectedAnswer_flags h₈).2 hsj
      rw [he] at hf
      cases hf
    · rfl
  rw [hs] at h₈
  obtain ⟨hfv, hcv⟩ := (selectedAnswer_flags h₈).1 rfl
  have hbv : answer.getObjVal? "background" = .ok (.bool (classificationBackgroundValid src.D M)) := by
    unfold SelectedAnswerWith VE.Route.Wire.ok at h₈
    subst h₈
    exact mkObj_getObjVal_mem (by simp [factsFields]) (by simp [factsFields])
  rw [hbv] at hb
  rw [hcv] at hc
  rw [hfv] at hf
  simp only [Except.ok.injEq, Json.bool.injEq] at hb hc hf
  exact ⟨environment, src, M, hM, P, items, h₁, h₂, h₃, hfd, model_admissible_of_flags src.D P M hM hb hc hf⟩

end VE.SoftNorms.Run
