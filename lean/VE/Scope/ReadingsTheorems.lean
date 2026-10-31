import VE.Scope.ReadingsLemmas

/-! Scope spec 11.3's statements on `governSets` (sc-5rb), as sc-5r's statement stub writes them. Of the four that take
    `Pinned.JsonWF`, sc-5rd proves `governSets_preserves`, `governSets_strings` and `governSets_readings_refused`
    (lemmas in `ReadingsLemmas.lean`); the route discharges `JsonWF` from sc-1af's boundary check
    (`decodeBlock_sets`, `VE/Service/ScopeAdmission.lean`). `governSets_every_choice` is false as written (two units
    with one id, docs/scope/sc-5rd/every-choice-counterexample.md); the DRI's fix adds distinct unit ids (sc-5rdb). -/

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
  obtain ⟨ch₀, o₀, outs, hall, hm, ha⟩ := governSets_ok D he out ho
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

set_option linter.unusedVariables false in
/-- `govern_strings`, per choice: no reading brings in a new symbol. -/
theorem governSets_strings (D : SDoc) (hw : Pinned.JsonWF D.doc)
    (hp : ∀ g ∈ D.governors, Pinned.JsonWF (Pinned.payload g.effect)) (out : Json) (ho : governSets D = .ok out)
    (s : String) (hs : Pinned.HasStr s out) :
    Pinned.HasStr s D.doc ∨ ∃ g ∈ D.governors, Pinned.HasStr s (Pinned.payload g.effect) := by
  by_cases he : governedSetUnits D = []
  · rw [governSets_no_sets D he] at ho; exact govern_strings D hw out ho s hs
  obtain ⟨ch₀, o₀, outs, hall, hm, ha⟩ := governSets_ok D he out ho
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
            obtain ⟨c, rfl, hc'⟩ := hri n r _ hr hn
            rcases hasStr_set s _ (jsonWF_top _ (hrd.2 (hyd.2 hw))) _ _ h with h | h
            · exact .inl (hyd.1 s (hrd.1 s h))
            · rcases hc' with rfl | ⟨p, hp, rfl⟩
              · exact .inl (hyd.1 s ((readingAt_src y n).1 s h))
              · exact hper p hp ((contentOf_src _ _).1 s h)
          | obj hk _ => cases hk
    | obj hk _ => cases hk

end VE.Scope
