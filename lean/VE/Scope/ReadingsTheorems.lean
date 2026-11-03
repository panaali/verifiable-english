import VE.Scope.ReadingsLemmas

/-! Scope spec 11.3's statements on `governSets` (sc-5rb), as sc-5r's statement stub writes them. Of the four that take
    `Pinned.JsonWF`, sc-5rd proves `governSets_preserves`, `governSets_strings` and `governSets_readings_refused`
    (lemmas in `ReadingsLemmas.lean`); the route discharges `JsonWF` from sc-1af's boundary check
    (`decodeBlock_sets`, `VE/Service/ScopeAdmission.lean`). `governSets_every_choice` holds for a document whose unit ids
    are distinct (sc-5rdb; without them it is false, docs/scope/sc-5rd/every-choice-counterexample.md), which the
    boundary checks (`decodeBlock_unitIds_nodup`). -/

namespace VE.Scope
open Lean

-- The stub's placeholders for sc-1ae's definitions (11.2) are scope's own.
namespace Pinned
export VE.Scope (JsonWF HasStr payload)
end Pinned

/-- `governAt_no_frontier`, restated: with no governed set, the answer is `govern`'s, byte for byte as a value. -/
theorem governSets_no_sets (D : SDoc) (h : governedSetUnits D = []) : governSets D = govern D := by
  simp only [governSets, governSetsWith, h, List.isEmpty_nil, if_true]

/-- The run path answers as the statement (`governFast_eq` per choice). -/
theorem governSetsFast_eq (D : SDoc) : governSetsWith governFast D = governSets D := by
  rw [show governFast = govern from funext governFast_eq]; rfl

/-- `scope_choices`, restated: the choices checked are lf-14d's joint choices over the governed sets. -/
theorem scope_set_choices (D : SDoc) (cs : List VE.Discourse.Choice) (hcs : setChoices D = .ok cs)
    (K : VE.Discourse.Manifest) (n : Nat) (cs' : List VE.Discourse.Choice)
    (hk : VE.Discourse.compatibleChoices K (setShapes D) n = .ok cs') :
    (∀ c ∈ cs', c ∈ cs) ∧ (K.constraints = [] → cs' = cs) := by
  have hcs' : cs = VE.Discourse.allChoices (setShapes D) := by
    unfold setChoices at hcs; split at hcs
    · cases hcs
    · cases hcs; rfl
  subst hcs'
  refine ⟨fun c hc => ?_, fun hK => VE.Discourse.compatibleChoices_unconstrained K hK _ n cs' hk⟩
  obtain ⟨hl, hi, _⟩ := ((VE.Discourse.compatible_sound K _ n cs' hk).1 c).mp hc
  exact (VE.Discourse.mem_allChoices _ c).mpr ⟨hl, hi⟩

theorem faultOf_some (D : SDoc) (rs : List (VE.Discourse.Choice × Except String Json)) (ch : VE.Discourse.Choice)
    (e : String) (hm : (ch, .error e) ∈ rs) : ∃ x, faultOf D rs = some x := by
  unfold faultOf
  split
  · rename_i hf
    have := List.findSome?_eq_none_iff.mp hf _ hm
    simp at this
  · exact ⟨_, rfl⟩

/-- A fault under one choice refuses the document: it is admitted only when every choice is. -/
theorem governSets_choice_refused (D : SDoc) (hs : governedSetUnits D ≠ []) (cs : List VE.Discourse.Choice)
    (hcs : setChoices D = .ok cs) (ch : VE.Discourse.Choice) (hc : ch ∈ cs) (e : String)
    (he : governChoice D ch = .error e) : (governSets D).isOk = false := by
  have hm : (ch, Except.error e) ∈ cs.map fun ch => (ch, govern (atChoice D ch)) :=
    List.mem_map.mpr ⟨ch, hc, by rw [← he]; rfl⟩
  obtain ⟨x, hx⟩ := faultOf_some D _ ch e hm
  have hne : (governedSetUnits D).isEmpty = false := by simpa using hs
  simp only [governSets, governSetsWith, hne, hcs, Bool.false_eq_true, if_false]
  simp only [bind, Except.bind, hx]
  rfl

/-- A fault every choice has is the document's own text, named with no choice (as `govern` would give it). -/
theorem faultOf_every (D : SDoc) (rs : List (VE.Discourse.Choice × Except String Json)) (hn : rs ≠ []) (e : String)
    (h : ∀ p ∈ rs, p.2 = .error e) : faultOf D rs = some e := by
  obtain ⟨⟨ch, r⟩, rest, rfl⟩ := List.exists_cons_of_ne_nil hn
  have hr : r = .error e := h _ (List.mem_cons_self ..)
  subst hr
  unfold faultOf
  simp only [List.findSome?_cons, Option.some.injEq]
  rw [if_pos]
  simp only [List.all_cons, beq_self_eq_true, Bool.true_and, List.all_eq_true]
  intro p hp
  rw [h p (List.mem_cons_of_mem _ hp)]
  simp

/-- A resource limit under a choice is passed on unchanged: UNKNOWN, never a refusal of that choice (9.4 item 4). -/
theorem choiceFault_limit (D : SDoc) (ch : VE.Discourse.Choice) (e : String) (h : e.startsWith "ResourceLimit" = true) :
    choiceFault D ch e = e := by
  simp [choiceFault, h]

/-- More joint choices than the limit: `ResourceLimit` (UNKNOWN), never a truncated product. -/
theorem governSets_limit (D : SDoc) (h : VE.Discourse.productSize (setShapes D) > choiceLimit) :
    governSets D = .error "ResourceLimit: scope choices" := by
  cases he : (governedSetUnits D).isEmpty
  · simp only [governSets, governSetsWith, he, Bool.false_eq_true, if_false, setChoices, h, if_true]
    rfl
  · have : governedSets D = [] := by
      simp [governedSets, List.isEmpty_iff.mp he]
    simp [setShapes, this, VE.Discourse.productSize, choiceLimit] at h

/-- `readings_refused`, restated for the document mode: a set this section does not govern is still refused. -/
theorem governSets_readings_refused (D : SDoc) (hw : Pinned.JsonWF D.doc) (g : Governor) (hg : g ∈ D.governors)
    (us : List String) (hc : covered D g.reach = .ok us) (u : String) (hu : u = g.unit ∨ u ∈ us)
    (hs : u ∈ setUnits D.doc) (hn : u ∉ governedSetUnits D) : (governSets D).isOk = false := by
  by_cases he : governedSetUnits D = []
  · rw [governSets_no_sets D he]; exact readings_refused D g hg us hc u hu hs
  have hne : (governedSetUnits D).isEmpty = false := by simpa using he
  have hch : ∀ ch, (governChoice D ch).isOk = false := fun ch => by
    obtain ⟨us', hc', hsub⟩ := covered_atChoice D ch hw g.reach us hc
    refine readings_refused (atChoice D ch) g hg us' hc' u (hu.imp id (hsub u)) ?_
    rw [setUnits_eq] at hs ⊢
    simp only [atChoice]; rw [atChoiceOn_sets _ _ _ hw]
    obtain ⟨s, hm, rfl⟩ := List.mem_map.mp hs
    exact List.mem_map.mpr ⟨s, List.mem_filter.mpr ⟨hm, by simpa [List.contains_iff_mem] using hn⟩, rfl⟩
  cases hcs : setChoices D with
  | error e => simp only [governSets, governSetsWith, hne, hcs, Bool.false_eq_true, if_false]; rfl
  | ok cs =>
    cases cs with
    | nil => simp only [governSets, governSetsWith, hne, hcs, Bool.false_eq_true, if_false]; rfl
    | cons ch rest =>
      cases hg' : governChoice D ch with
      | ok o => have := hch ch; rw [hg'] at this; cases this
      | error e => exact governSets_choice_refused D he _ hcs ch List.mem_cons_self e hg'

/-- `governAt_preserves`, restated: all but `units`, `reading_sets` and the governed readings' `content` is kept. -/
theorem governSets_preserves (D : SDoc) (hw : Pinned.JsonWF D.doc) (out : Json) (ho : governSets D = .ok out) :
    (∀ k, k ≠ "units" → k ≠ "reading_sets" → out.getObjVal? k = D.doc.getObjVal? k) ∧
    (unitsOf out).map idOf = (unitsOf D.doc).map idOf ∧
    (∀ (i : Nat) (x y : Json), (unitsOf out)[i]? = some x → (unitsOf D.doc)[i]? = some y →
      (∀ k, k ≠ "content" → x.getObjVal? k = y.getObjVal? k) ∧ (idOf y ∈ governedSetUnits D → x = y)) ∧
    (setsJson out).length = (setsJson D.doc).length ∧
    ∀ (i : Nat) (x y : Json), (setsJson out)[i]? = some x → (setsJson D.doc)[i]? = some y →
      (setUnit y ∉ governedSetUnits D → x = y) ∧ (∀ k, k ≠ "readings" → x.getObjVal? k = y.getObjVal? k) ∧
      (readingsJson x).length = (readingsJson y).length ∧
      ∀ (n : Nat) (r r' : Json), (readingsJson x)[n]? = some r → (readingsJson y)[n]? = some r' →
        ∀ k, k ≠ "content" → r.getObjVal? k = r'.getObjVal? k := by
  by_cases he : governedSetUnits D = []
  · rw [governSets_no_sets D he] at ho
    obtain ⟨h₁, h₂, h₃⟩ := govern_preserves D hw out ho
    have hs := setsJson_of_get _ _ (h₁ "reading_sets" (by decide))
    refine ⟨fun k hk _ => h₁ k hk, h₂, fun i x y hx hy => ⟨(h₃ i x y hx hy).1, by simp [he]⟩, by rw [hs],
      fun i x y hx hy => ?_⟩
    rw [hs, hy] at hx; cases hx
    exact ⟨fun _ => rfl, fun _ _ => rfl, rfl, fun n r r' hr hr' => by rw [hr] at hr'; cases hr'; exact fun _ _ => rfl⟩
  obtain ⟨t, hd⟩ := su_obj D he
  have ht := jsonWF_top _ hw t hd
  obtain ⟨ch₀, o₀, outs, hall, hm, ha, -⟩ := governSets_ok D he out ho
  obtain ⟨sets, hout, hl, hi⟩ := assemble_ok D ch₀ o₀ outs out ha
  have hK : ∀ k, k ≠ "units" → k ≠ "reading_sets" → out.getObjVal? k = D.doc.getObjVal? k := fun k h₁ h₂ => by
    rw [hout, setObjVal_ne _ (top_set _ (jsonWF_top _ hw) _ _) _ _ _ (Ne.symm h₂),
      setObjVal_ne _ (jsonWF_top _ hw) _ _ _ (Ne.symm h₁)]
  have hUo : unitsOf out = ((unitsOf o₀).zip (unitsOf D.doc)).map fun (x, y) =>
      if (governedSetUnits D).contains (idOf y) then y else x := by
    rw [hout, hd]; unfold unitsOf
    rw [(getD_set2 t ht "units" "reading_sets" (by decide) _ _).2]
  have hSo : setsJson out = sets := by
    rw [hout, hd]; unfold setsJson
    rw [(getD_set2 t ht "units" "reading_sets" (by decide) _ _).1]
  clear hout
  have hg₀ : governChoice D ch₀ = .ok o₀ := hall (ch₀, o₀) hm
  unfold governChoice at hg₀
  have hw₀ : JsonWF (atChoice D ch₀).doc := jsonWF_atChoiceOn _ _ _ hw
  obtain ⟨F, -, hF, hp⟩ := atChoiceOn_units (governedSetUnits D) D.doc ch₀ hw
  obtain ⟨-, g₂, g₃⟩ := govern_preserves (atChoice D ch₀) hw₀ o₀ hg₀
  change (unitsOf o₀).map idOf = (unitsOf (atChoiceOn (governedSetUnits D) D.doc ch₀)).map idOf at g₂
  rw [hF, List.map_map, List.map_congr_left (f := idOf ∘ F) (g := idOf) fun y hy => (hp y hy).1] at g₂
  have hlen : (unitsOf o₀).length = (unitsOf D.doc).length := by simpa using congrArg List.length g₂
  -- unit `i` of the answer: `y` itself, or `o₀`'s, which has `y`'s id and every member of `y` but `content`
  have hu : ∀ i y, (unitsOf D.doc)[i]? = some y → ∃ x₀, idOf x₀ = idOf y ∧
      (∀ k, k ≠ "content" → x₀.getObjVal? k = y.getObjVal? k) ∧
      (unitsOf out)[i]? = some (if (governedSetUnits D).contains (idOf y) then y else x₀) := fun i y hy => by
    have hi' : i < (unitsOf o₀).length := hlen ▸ (List.getElem?_eq_some_iff.mp hy).1
    have hx₀ := List.getElem?_eq_getElem hi'
    refine ⟨(unitsOf o₀)[i], ?_, fun k hk => ?_, ?_⟩
    · have := congrArg (·[i]?) g₂
      simpa only [List.getElem?_map, hx₀, hy, Option.map_some, Option.some.injEq] using this
    · have hFy : (unitsOf (atChoice D ch₀).doc)[i]? = some (F y) := by
        show (unitsOf (atChoiceOn _ D.doc ch₀))[i]? = _
        rw [hF, List.getElem?_map, hy]; rfl
      exact ((g₃ i _ _ hx₀ hFy).1 k hk).trans ((hp y (List.mem_of_getElem? hy)).2.1 k hk)
    · rw [hUo, List.getElem?_map, (List.getElem?_zip_eq_some (z := ((unitsOf o₀)[i], y))).mpr ⟨hx₀, hy⟩]; rfl
  have hnone : ∀ i, (unitsOf D.doc)[i]? = none → (unitsOf out)[i]? = none := fun i h => by
    rw [hUo, List.getElem?_eq_none_iff]; rw [List.getElem?_eq_none_iff] at h; simp [hlen, h]
  refine ⟨hK, List.ext_getElem? fun i => ?_, fun i x y hx hy => ?_, by rw [hSo, hl], fun i x y hx hy => ?_⟩
  · cases hy : (unitsOf D.doc)[i]? with
    | none => simp [List.getElem?_map, hy, hnone i hy]
    | some y =>
      obtain ⟨x₀, hid, -, hx⟩ := hu i y hy
      simp only [List.getElem?_map, hy, hx, Option.map_some, Option.some.injEq]
      split <;> simp [hid]
  · obtain ⟨x₀, -, hk, hx'⟩ := hu i y hy
    rw [hx'] at hx; cases hx
    split
    · exact ⟨fun _ _ => rfl, fun _ => rfl⟩
    · next hc => exact ⟨hk, fun hm => absurd (List.elem_iff.mpr hm) hc⟩
  · rw [hSo] at hx
    have hiy := hi i y x hy hx
    have hyW : JsonWF y := (arrAt_mem D.doc y "reading_sets" (List.mem_of_getElem? hy)).2 hw
    have hyt := jsonWF_top _ hyW
    cases hc : (governedSetUnits D).contains (setUnit y)
    · cases hiy.1 hc
      exact ⟨fun _ => rfl, fun _ _ => rfl, rfl, fun n r r' hr hr' => by rw [hr] at hr'; cases hr'; exact fun _ _ => rfl⟩
    · obtain ⟨rs, rfl, hrl, hri⟩ := hiy.2 hc
      have hR := readingsJson_set y hyt rs hrl
      refine ⟨fun hn => absurd (List.elem_iff.mp hc) hn, fun k hk => setObjVal_ne _ hyt _ _ _ (Ne.symm hk),
        by rw [hR, hrl], fun n r r' hr hr' k hk => ?_⟩
      rw [hR] at hr
      obtain ⟨c, rfl, -⟩ := hri n r' r hr' hr
      exact setObjVal_ne _ (jsonWF_top _ ((arrAt_mem y r' "readings" (List.mem_of_getElem? hr')).2 hyW)) _ _ _
        (Ne.symm hk)

/-- Per choice: every joint choice of the governed sets, read off the answer, is `govern` of that choice. -/
theorem governSets_every_choice (D : SDoc) (hw : Pinned.JsonWF D.doc) (hd : (unitIds D.doc).Nodup)
    (hs : governedSetUnits D ≠ []) (out : Json) (ho : governSets D = .ok out) (cs : List VE.Discourse.Choice)
    (hcs : setChoices D = .ok cs) (ch : VE.Discourse.Choice) (hc : ch ∈ cs) :
    ∃ o, governChoice D ch = .ok o ∧ atChoiceOn (governedSetUnits D) out ch = o := by
  obtain ⟨ch₀, o₀, outs, hall, -, ha, hcov⟩ := governSets_ok D hs out ho
  obtain ⟨sets, hout, hl, hi⟩ := assemble_ok D ch₀ o₀ outs out ha
  have hU := assemble_units D ch₀ o₀ outs out ha
  obtain ⟨o, hmo⟩ := hcov cs hcs ch hc
  have go : governChoice D ch = .ok o := hall (ch, o) hmo
  refine ⟨o, go, ?_⟩
  unfold governChoice at go
  have hP := governSets_preserves D hw out ho
  obtain ⟨t, hdt⟩ := su_obj D hs
  have ht := jsonWF_top _ hw
  have hwX : JsonWF (atChoice D ch).doc := jsonWF_atChoiceOn _ _ _ hw
  have hX := govern_preserves _ hwX o go
  have hg : D.governors ≠ [] := by
    obtain ⟨u, hu⟩ := List.exists_mem_of_ne_nil _ hs
    have := (List.mem_filter.mp hu).2
    simp only [Bool.and_eq_true] at this
    obtain ⟨g, hg, -⟩ := List.any_eq_true.mp this.1.2
    exact List.ne_nil_of_mem hg
  rcases govern_ok _ o go with ⟨h0, -, -⟩ | ⟨comp, tt, -, -, ho'⟩
  · exact absurd h0 hg
  -- what the answer and the document under the choice read back
  have hUo : unitsOf out = ((unitsOf o₀).zip (unitsOf D.doc)).map fun (x, y) =>
      if (governedSetUnits D).contains (idOf y) then y else x := by
    rw [hout, hdt]; unfold unitsOf
    rw [(getD_set2 t (ht t hdt) "units" "reading_sets" (by decide) _ _).2]
  have hSo : setsJson out = sets := by
    rw [hout, hdt]; unfold setsJson
    rw [(getD_set2 t (ht t hdt) "units" "reading_sets" (by decide) _ _).1]
  have hUX := unitsOf_atChoiceOn (governedSetUnits D) D.doc ch ht
  have hids : (unitsOf o).map idOf = unitIds D.doc := by
    rw [hX.2.1]; exact unitIds_atChoiceOn _ _ _ hw
  have hnX : ((unitsOf (atChoice D ch).doc).map idOf).Nodup := by
    show (unitIds (atChoiceOn _ D.doc ch)).Nodup
    rw [unitIds_atChoiceOn _ _ _ hw]; exact hd
  have hno : ((unitsOf o).map idOf).Nodup := hids ▸ hd
  have hlo : (unitsOf o).length = (unitsOf D.doc).length := by
    simpa [unitIds] using congrArg List.length hids
  have hlout : (unitsOf out).length = (unitsOf D.doc).length := by
    simpa using congrArg List.length hP.2.1
  -- a set of the answer keeps its unit, id and version
  have hsU : ∀ j s s', (setsJson D.doc)[j]? = some s → sets[j]? = some s' →
      setUnit s' = setUnit s ∧ idOf s' = idOf s ∧ setVersion s' = setVersion s := fun j s s' hs hs' => by
    have hst := jsonWF_top _ ((arrAt_mem D.doc s "reading_sets" (List.mem_of_getElem? hs)).2 hw)
    cases hc : (governedSetUnits D).contains (setUnit s)
    · rw [(hi j s s' hs hs').1 hc]; exact ⟨rfl, rfl, rfl⟩
    · obtain ⟨rs, rfl, -⟩ := (hi j s s' hs hs').2 hc
      refine ⟨?_, ?_, ?_⟩ <;> simp only [setUnit, idOf, setVersion, getD_setObjVal s hst "readings" "unit" (by decide),
        getD_setObjVal s hst "readings" "id" (by decide), getD_setObjVal s hst "readings" "version" (by decide)]
  have hwo : ∀ kvs, out = .obj kvs → kvs.WF := hout ▸ top_set _ (top_set _ ht _ _) _ _
  -- the units of the answer under the choice are `govern`'s under it
  have hUL : unitsOf (atChoiceOn (governedSetUnits D) out ch) = unitsOf o := by
    rw [unitsOf_atChoiceOn _ _ _ hwo, hSo]
    apply List.ext_getElem?
    intro i
    rw [List.getElem?_map]
    cases hy : (unitsOf D.doc)[i]? with
    | none =>
      have h1 : (unitsOf out)[i]? = none := by rw [List.getElem?_eq_none_iff] at hy ⊢; omega
      have h2 : (unitsOf o)[i]? = none := by rw [List.getElem?_eq_none_iff] at hy ⊢; omega
      rw [h1, h2]; rfl
    | some y =>
      have hyw := jsonWF_top _ ((unitsOf_mem _ y (List.mem_of_getElem? hy)).2 hw)
      obtain ⟨u, hu⟩ : ∃ u, (unitsOf out)[i]? = some u :=
        ⟨_, List.getElem?_eq_getElem (hlout ▸ (List.getElem?_eq_some_iff.mp hy).1)⟩
      obtain ⟨w, hw'⟩ : ∃ w, (unitsOf o)[i]? = some w :=
        ⟨_, List.getElem?_eq_getElem (hlo ▸ (List.getElem?_eq_some_iff.mp hy).1)⟩
      have hidu : idOf u = idOf y := by
        have := congrArg (·[i]?) hP.2.1
        simpa only [List.getElem?_map, hu, hy, Option.map_some, Option.some.injEq] using this
      have hidw : idOf w = idOf y := by
        have := congrArg (·[i]?) hids
        simpa only [unitIds, List.getElem?_map, hw', hy, Option.map_some, Option.some.injEq] using this
      obtain ⟨x₀, hx₀, hux⟩ : ∃ x₀, (unitsOf o₀)[i]? = some x₀ ∧
          u = if (governedSetUnits D).contains (idOf y) then y else x₀ := by
        rw [hUo, List.getElem?_map] at hu
        cases hz : ((unitsOf o₀).zip (unitsOf D.doc))[i]? with
        | none => rw [hz] at hu; cases hu
        | some z =>
          obtain ⟨x₀, y'⟩ := z
          obtain ⟨h1, h2⟩ := List.getElem?_zip_eq_some.mp hz
          rw [hy] at h2; cases h2
          rw [hz] at hu; cases hu
          exact ⟨x₀, h1, rfl⟩
      rw [hu, hw', Option.map_some, Option.some.injEq]
      cases hc : (governedSetUnits D).contains (idOf y)
      · -- outside the governed set units: `o₀`'s unit on both sides
        rw [hc] at hux; simp only [Bool.false_eq_true, if_false] at hux; subst hux
        have hf : sets.find? (fun s => (governedSetUnits D).contains (setUnit s) && setUnit s == idOf u) = none := by
          rw [List.find?_eq_none]; intro s _ h
          simp only [Bool.and_eq_true, beq_iff_eq] at h
          rw [h.2, hidu, hc] at h; exact absurd h.1 (by decide)
        rw [hf]
        rcases hU (ch, o) hmo i w u hw' hx₀ with h | h
        · rw [hidw, hc] at h; cases h
        · exact h.symm
      · rw [hc] at hux; simp only [if_true] at hux; subst hux
        rcases find?_pair (fun s => (governedSetUnits D).contains (setUnit s) && setUnit s == idOf u)
            (fun s => (governedSetUnits D).contains (setUnit s) && setUnit s == idOf u) (setsJson D.doc) sets hl
            (fun j s s' h1 h2 => by simp only [(hsU j s s' h1 h2).1]) with ⟨h1, -⟩ | ⟨j, s, s', hs, hs', h1, h2⟩
        · exfalso
          have hm := (List.mem_filter.mp (List.contains_iff_mem.mp hc)).2
          simp only [Bool.and_eq_true] at hm
          cases hf : (setsJson D.doc).find? (setUnit · == idOf u) with
          | none => rw [hf] at hm; cases hm.1.1.2
          | some s =>
            have := List.find?_eq_none.mp h1 s (List.mem_of_find?_eq_some hf)
            have he := List.find?_some hf
            simp only [beq_iff_eq] at he
            simp only [he, Bool.and_true, beq_self_eq_true, List.contains_iff_mem] at this
            exact this (List.contains_iff_mem.mp hc)
        · have hP1 := List.find?_some h1
          simp only [Bool.and_eq_true, beq_iff_eq] at hP1
          obtain ⟨rs, hs'e, hrl, hri⟩ := (hi j s s' hs hs').2 hP1.1
          have hst := jsonWF_top _ ((arrAt_mem D.doc s "reading_sets" (List.mem_of_getElem? hs)).2 hw)
          rw [h2]; dsimp only
          generalize ha : ((pickOf ch s).map (readingAt s)).getD .null = a
          have hXi : (unitsOf (atChoice D ch).doc)[i]? = some (u.setObjVal! "content" a) := by
            show (unitsOf (atChoiceOn _ D.doc ch))[i]? = _
            rw [hUX, List.getElem?_map, hy, Option.map_some, h1]; dsimp only; rw [ha]
          have hwF : w = u.setObjVal! "content" a ∨ ∃ c, w = (u.setObjVal! "content" a).setObjVal! "content" c := by
            rw [ho', unitsOf_patch _ hwX, List.getElem?_map, hXi, Option.map_some, Option.some.injEq] at hw'
            split at hw'
            · exact .inr ⟨_, hw'.symm⟩
            · exact .inl hw'.symm
          have hpk : pickOf ch s' = pickOf ch s := by
            simp only [pickOf, (hsU j s s' hs hs').2.1, (hsU j s s' hs hs').2.2]
          rw [hpk]
          cases u with
          | obj ty =>
            have hty := hyw ty rfl
            have hwb : w = (Json.obj ty).setObjVal! "content" (w.getObjValD "content") := by
              rcases hwF with rfl | ⟨c, rfl⟩
              · simp only [Json.getObjValD, setObjVal_self ty hty]; rfl
              · rw [setObjVal_twice _ hyw]; simp only [Json.getObjValD, setObjVal_self ty hty]; rfl
            rw [hwb]; congr 1
            have getC : ∀ (tr : Std.TreeMap.Raw String Json) (c : Json), tr.WF →
                ((Json.obj tr).setObjVal! "content" c).getObjValD "content" = c := fun tr c h => by
              simp only [Json.getObjValD, setObjVal_self tr h]; rfl
            have hcont : contentOf o (idOf (Json.obj ty)) = w.getObjValD "content" := by
              unfold contentOf; rw [← hidw, find?_idOf _ hno i w hw']; rfl
            -- a unit given no content under the choice is no rule, so `govern` leaves it
            have hnull : a = .null → w.getObjValD "content" = a := fun han => by
              have hcX : contentOf (atChoice D ch).doc (idOf (Json.obj ty)) = a := by
                unfold contentOf
                rw [← idOf_set _ hyw a, find?_idOf _ hnX i _ hXi, Option.map_some, Option.getD_some, getC ty a hty]
              have hna : idOf ((Json.obj ty).setObjVal! "content" a) ∉ affected (atChoice D ch) := fun hm => by
                have := (List.mem_filter.mp (List.mem_filter.mp hm).1).2
                rw [idOf_set _ hyw, hcX, han] at this
                exact absurd this (by decide)
              rw [(hX.2.2 i w _ hw' hXi).2 hna, getC ty a hty]
            cases hpc : pickOf ch s with
            | none =>
              rw [hpc] at ha
              simp only [Option.map_none, Option.getD_none] at ha ⊢
              exact ((hnull ha.symm).trans ha.symm).symm
            | some n =>
              rw [hpc] at ha
              simp only [Option.map_some, Option.getD_some] at ha ⊢
              have hR : readingsJson s' = rs := hs'e ▸ readingsJson_set s hst rs hrl
              cases hr : (readingsJson s)[n]? with
              | none =>
                have hr' : rs[n]? = none := by rw [List.getElem?_eq_none_iff] at hr ⊢; omega
                have ha0 : a = .null := ha.symm.trans (by simp only [readingAt, hr]; rfl)
                rw [show readingAt s' n = .null by simp only [readingAt, hR, hr']; rfl]
                exact ((hnull ha0).trans ha0).symm
              | some r =>
                obtain ⟨r', hr'⟩ : ∃ r', rs[n]? = some r' :=
                  ⟨_, List.getElem?_eq_getElem (hrl ▸ (List.getElem?_eq_some_iff.mp hr).1)⟩
                obtain ⟨c, hr'e, -, hallc⟩ := hri n r r' hr hr'
                have hrw := jsonWF_top _ ((arrAt_mem s r "readings" (List.mem_of_getElem? hr)).2
                  ((arrAt_mem D.doc s "reading_sets" (List.mem_of_getElem? hs)).2 hw))
                rw [show readingAt s' n = r'.getObjValD "content" by simp only [readingAt, hR, hr']; rfl, hr'e]
                cases r with
                | obj tr => rw [getC tr c (hrw tr rfl), hallc (ch, o) hmo hpc, hP1.2, hcont]
                | _ =>
                  have ha0 : a = .null := ha.symm.trans (by simp only [readingAt, hr]; rfl)
                  exact ((hnull ha0).trans ha0).symm
          | _ =>
            rcases hwF with rfl | ⟨c, rfl⟩ <;> rfl
  have hpo : o = (atChoice D ch).doc.setObjVal! "units" (.arr (unitsOf o).toArray) := by
    rw [ho', unitsOf_patch _ hwX]; rfl
  have hXd : (atChoice D ch).doc = (D.doc.setObjVal! "units" (.arr (unitsOf (atChoice D ch).doc).toArray)).setObjVal!
      "reading_sets" (.arr ((setsJson D.doc).filter fun s => !(governedSetUnits D).contains (setUnit s)).toArray) := by
    simp only [atChoice]
    rw [unitsOf_atChoiceOn _ _ _ ht]; rfl
  have hLd : atChoiceOn (governedSetUnits D) out ch = (out.setObjVal! "units"
      (.arr (unitsOf (atChoiceOn (governedSetUnits D) out ch)).toArray)).setObjVal!
      "reading_sets" (.arr ((setsJson out).filter fun s => !(governedSetUnits D).contains (setUnit s)).toArray) := by
    rw [unitsOf_atChoiceOn _ _ _ hwo]; rfl
  rw [hLd, hUL, hSo]
  generalize unitsOf o = W at hpo ⊢
  rw [hpo, hXd]
  generalize unitsOf (atChoice D ch).doc = V
  rw [hout, setObjVal_swap _ ht "units" "reading_sets" (by decide), setObjVal_twice _ (top_set _ ht _ _),
    setObjVal_swap _ ht "units" "reading_sets" (by decide)]
  rw [filter_pair _ (setsJson D.doc) sets hl fun j s s' h1 h2 =>
    ⟨by simp only [(hsU j s s' h1 h2).1], fun hq => (hi j s s' h1 h2).1 (by simpa using hq)⟩]

set_option linter.unusedVariables false in
/-- `govern_strings`, per choice: no reading brings in a new symbol. -/
theorem governSets_strings (D : SDoc) (hw : Pinned.JsonWF D.doc)
    (hp : ∀ g ∈ D.governors, Pinned.JsonWF (Pinned.payload g.effect)) (out : Json) (ho : governSets D = .ok out)
    (s : String) (hs : Pinned.HasStr s out) :
    Pinned.HasStr s D.doc ∨ ∃ g ∈ D.governors, Pinned.HasStr s (Pinned.payload g.effect) := by
  by_cases he : governedSetUnits D = []
  · rw [governSets_no_sets D he] at ho; exact govern_strings D hw out ho s hs
  obtain ⟨ch₀, o₀, outs, hall, hm, ha, -⟩ := governSets_ok D he out ho
  obtain ⟨sets, hout, hl, hi⟩ := assemble_ok D ch₀ o₀ outs out ha
  -- a string of a per-choice answer is the document's or a payload's
  have hper : ∀ p ∈ outs, HasStr s p.2 → HasStr s D.doc ∨ ∃ g ∈ D.governors, HasStr s (payload g.effect) :=
    fun p hp h => by
      have hg : governChoice D p.1 = .ok p.2 := hall p hp
      unfold governChoice at hg
      rcases govern_strings (atChoice D p.1) (jsonWF_atChoiceOn _ _ _ hw) p.2 hg s h with h | h
      · exact .inl (hasStr_atChoiceOn _ _ _ hw s h)
      · exact .inr h
  have ht := jsonWF_top _ hw
  rw [hout] at hs
  rcases hasStr_set s _ (top_set _ ht _ _) _ _ hs with hs | hs
  · rcases hasStr_set s _ ht _ _ hs with hs | hs
    · exact .inl hs
    · cases hs with
      | arr hm' h =>
        obtain ⟨⟨x₀, y⟩, hz, rfl⟩ := List.mem_map.mp (List.mem_toArray.mp hm')
        dsimp only at h
        split at h
        · exact .inl ((unitsOf_mem _ y (List.of_mem_zip hz).2).1 s h)
        · exact hper (ch₀, o₀) hm ((unitsOf_mem _ x₀ (List.of_mem_zip hz).1).1 s h)
      | obj hk _ => cases hk
  · cases hs with
    | arr hm' h =>
      obtain ⟨i, hi'⟩ := List.mem_iff_getElem?.mp (List.mem_toArray.mp hm')
      obtain ⟨y, hy⟩ : ∃ y, (setsJson D.doc)[i]? = some y :=
        ⟨_, List.getElem?_eq_getElem (hl ▸ (List.getElem?_eq_some_iff.mp hi').1)⟩
      have hyd := arrAt_mem D.doc y "reading_sets" (List.mem_of_getElem? hy)
      have hiy := hi i y _ hy hi'
      cases hc : (governedSetUnits D).contains (setUnit y)
      · rw [hiy.1 hc] at h; exact .inl (hyd.1 s h)
      · obtain ⟨rs, he', hrl, hri⟩ := hiy.2 hc
        rw [he'] at h
        rcases hasStr_set s _ (jsonWF_top _ (hyd.2 hw)) _ _ h with h | h
        · exact .inl (hyd.1 s h)
        · cases h with
          | arr hm'' h =>
            obtain ⟨n, hn⟩ := List.mem_iff_getElem?.mp (List.mem_toArray.mp hm'')
            obtain ⟨r, hr⟩ : ∃ r, (readingsJson y)[n]? = some r :=
              ⟨_, List.getElem?_eq_getElem (hrl ▸ (List.getElem?_eq_some_iff.mp hn).1)⟩
            have hrd := arrAt_mem y r "readings" (List.mem_of_getElem? hr)
            obtain ⟨c, rfl, hc', -⟩ := hri n r _ hr hn
            rcases hasStr_set s _ (jsonWF_top _ (hrd.2 (hyd.2 hw))) _ _ h with h | h
            · exact .inl (hyd.1 s (hrd.1 s h))
            · rcases hc' with rfl | ⟨p, hp, rfl⟩
              · exact .inl (hyd.1 s ((readingAt_src y n).1 s h))
              · exact hper p hp ((contentOf_src _ _).1 s h)
          | obj hk _ => cases hk
    | obj hk _ => cases hk

end VE.Scope
