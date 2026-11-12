import VE.SoftNorms.Run

/-! The wire theorem of the soft route's `soft-selected` kind (kb-10a, kernel boundary).

`soft_wire_selected` states the whole answer: it is exactly `Wire.ok id` with the two fields
`background` and `results`, no other field, and one result per query of the request, in order,
naming the request's predicate and tuple, with `selected = selectedAt` and `outcome = outcomeAt`
for the source and the model the case's own decoders read. `selected_semantics` (`Selected.lean`)
says what `selectedAt` and `outcomeAt` mean; each decoded query carries its hypotheses
(`QueryDecoded`: a regulated predicate, a tuple typed for its sorts). -/
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

/-- The `soft-selected` answer for `D`, `M` and the decoded queries, written out field by field
(a closed list: no field beyond `id`, `status`, `background` and `results`). -/
def SelectedAnswer (id : String) (D : SoftDoc) (M : VE.FiniteModel VE.Bridge.Entity)
    (qs : List SelectedQuery) (answer : Json) : Prop :=
  answer = VE.Route.Wire.ok id [("background", .bool (classificationBackgroundValid D M)),
    ("results", Json.arr (qs.map fun q => Json.mkObj [("predicate", .str q.pred), ("tuple", toJson q.ids),
      ("selected", toJson (selectedAt D M q.pred q.tuple)),
      ("outcome", .bool (outcomeAt D M q.pred q.tuple))]).toArray)]

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
      qs.length = raws.length ∧ ∀ x ∈ raws.zip qs, QueryDecoded D M x.1 x.2
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
    obtain ⟨hl, hall⟩ := decodeQueries_ok hxs
    refine ⟨by simp [hl], ?_⟩
    intro y hy
    rcases List.mem_cons.mp hy with rfl | hy
    · exact decodeSelectedQuery_ok hx
    · exact hall y hy

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
  unfold runSelected at hres
  obtain ⟨environment, henv, hres⟩ := bind_ok hres
  obtain ⟨src, hsrc, hres⟩ := bind_ok hres
  obtain ⟨⟨M, hM⟩, hmod, hres⟩ := bind_ok hres
  obtain ⟨qs, hqs, hres⟩ := bind_ok hres
  simp only [pure, Except.pure, Except.ok.injEq] at hres
  subst hres
  split at hqs
  · rename_i raw hq
    split at hqs
    · cases hqs
    · rename_i hne
      obtain ⟨hl, hall⟩ := decodeQueries_ok hqs
      refine ⟨id, environment, src, M, hM, raw, qs, hid, henv, hsrc, hmod, hq, ?_, by simpa using hl, hall, rfl⟩
      simpa [Array.isEmpty] using hne
  · cases hqs

end VE.SoftNorms.Run
