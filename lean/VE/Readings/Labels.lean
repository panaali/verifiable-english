import VE.Readings.SupSlot

/-! The labels of `Choice_D` are distinct (docs/spec/composition-s2.md 1.6, 8.4 `slot_wellLabelled`).

A label is read from its end: `readings:<set>@<v>:one`, `readings:<set>@<v>:<i>:quiet` and
`readings:quiet:outweighs:<a>:<L>:<H>` end in runs of characters that contain neither `:` nor `@` (a numeral, a
rank, `one`, `quiet`), separated by `:` and `@`. Reversed, two labels agree run by run until they differ in a
separator, a run, or the rest; the version and the index are numerals, the ranks are soft names (a letter first),
and the set ids are distinct. The coupling and narrowing labels differ from the others in their first character. -/
namespace VE.Readings
open VE.Norms (Sat envAt size)
open VE.SoftNorms (SoftNode SoftDoc soften validSoftName)
open VE.Rights (RightsDoc correlate limPremises limPremisesLabelled)
open VE.Compose (Content Labelled)

/-- A run: neither separator. -/
def NoSep (l : List Char) : Prop := ∀ c ∈ l, c ≠ ':' ∧ c ≠ '@'

instance (l : List Char) : Decidable (NoSep l) := by unfold NoSep; infer_instance

theorem noSep_reverse {l : List Char} (h : NoSep l) : NoSep l.reverse := fun c hc => h c (List.mem_reverse.mp hc)

/-- Two strings that start with a run followed by a separator agree on the run and the separator. -/
theorem split_runs {x y : Char} (hx : x = ':' ∨ x = '@') (hy : y = ':' ∨ y = '@') :
    ∀ (a a' b b' : List Char), NoSep a → NoSep a' → a ++ x :: b = a' ++ y :: b' → a = a' ∧ x = y ∧ b = b'
  | [], [], b, b', _, _, h => by simp only [List.nil_append, List.cons.injEq] at h; exact ⟨rfl, h.1, h.2⟩
  | [], c :: a', b, b', _, h', h => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h
    have hc := h' c List.mem_cons_self
    rw [← h.1] at hc
    rcases hx with rfl | rfl
    · exact absurd rfl hc.1
    · exact absurd rfl hc.2
  | c :: a, [], b, b', h, _, h' => by
    simp only [List.nil_append, List.cons_append, List.cons.injEq] at h'
    have hc := h c List.mem_cons_self
    rw [h'.1] at hc
    rcases hy with rfl | rfl
    · exact absurd rfl hc.1
    · exact absurd rfl hc.2
  | c :: a, c' :: a', b, b', h, h', he => by
    simp only [List.cons_append, List.cons.injEq] at he
    obtain ⟨rfl, he⟩ := he
    obtain ⟨h1, h2, h3⟩ := split_runs hx hy a a' b b' (fun d hd => h d (by simp [hd]))
      (fun d hd => h' d (by simp [hd])) he
    exact ⟨by rw [h1], h2, h3⟩

theorem digits_digit (n : Nat) : ∀ c ∈ Nat.toDigits 10 n, '0' ≤ c ∧ c ≤ '9' := by
  have hv := toDigitsCore_valid (n + 1) n [] (by rfl)
  intro c hc
  have := List.all_eq_true.mp hv c hc
  simpa using this

theorem digits_noSep (n : Nat) : NoSep (Nat.toDigits 10 n) := by
  intro c hc
  obtain ⟨h1, h2⟩ := digits_digit n c hc
  constructor <;> intro he <;> subst he <;> exact absurd h2 (by decide)

theorem toDigitsCore_ne_nil : ∀ (f n : Nat) (ds : List Char), ds ≠ [] → Nat.toDigitsCore 10 f n ds ≠ []
  | 0, _, _, h => h
  | f + 1, n, ds, _ => by
    simp only [Nat.toDigitsCore]
    split
    · simp
    · exact toDigitsCore_ne_nil f _ _ (by simp)

theorem toDigits_ne_nil (n : Nat) : Nat.toDigits 10 n ≠ [] := by
  show Nat.toDigitsCore 10 (n + 1) n [] ≠ []
  simp only [Nat.toDigitsCore]
  split
  · simp
  · exact toDigitsCore_ne_nil _ _ _ (by simp)

theorem validSoftName_noSep {s : String} (h : validSoftName s = true) : NoSep s.data := by
  unfold validSoftName at h
  split at h
  · cases h
  · rename_i first rest hl
    simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, Bool.or_eq_true, beq_iff_eq] at h
    obtain ⟨⟨⟨⟨hf1, hf2⟩, hr⟩, _⟩, _⟩ := h
    have hdata : s.data = first :: rest := hl
    rw [hdata]
    intro c hc
    rcases List.mem_cons.mp hc with rfl | hc
    · constructor <;> intro he <;> subst he <;> exact absurd hf1 (by decide)
    · rcases hr c hc with (⟨h1, h2⟩ | ⟨h1, h2⟩) | h1
      · constructor <;> intro he <;> subst he <;> exact absurd h1 (by decide)
      · constructor <;> intro he <;> subst he <;> exact absurd h2 (by decide)
      · constructor <;> intro he <;> subst he <;> exact absurd h1 (by decide)

/-! ## The labels, reversed -/

theorem rv_one (R : ReadingSet) : ("readings:" ++ label R ++ ":one").data.reverse =
    ['e', 'n', 'o'] ++ ':' :: ((Nat.toDigits 10 R.version).reverse ++ '@' ::
      (R.id.data.reverse ++ "readings:".data.reverse)) := by
  have h1 : ":one".data = [':', 'o', 'n', 'e'] := rfl
  have h2 : "@".data = ['@'] := rfl
  simp [label, String.data_append, List.reverse_append, h1, h2, toString_data]

theorem rv_own (R : ReadingSet) (i : Nat) : ("readings:" ++ label R ++ ":" ++ toString i ++ ":quiet").data.reverse =
    ['t', 'e', 'i', 'u', 'q'] ++ ':' :: ((Nat.toDigits 10 i).reverse ++ ':' :: ((Nat.toDigits 10 R.version).reverse ++
      '@' :: (R.id.data.reverse ++ "readings:".data.reverse))) := by
  have h1 : ":quiet".data = [':', 'q', 'u', 'i', 'e', 't'] := rfl
  have h2 : "@".data = ['@'] := rfl
  have h3 : ":".data = [':'] := rfl
  simp [label, String.data_append, List.reverse_append, h1, h2, h3, toString_data]

theorem rv_shared (a L H : String) : ("readings:quiet:" ++ keyLabel (.outweighs a L H)).data.reverse =
    H.data.reverse ++ ':' :: (L.data.reverse ++ ':' :: (a.data.reverse ++ "outweighs:".data.reverse ++
      "readings:quiet:".data.reverse)) := by
  have h3 : ":".data = [':'] := rfl
  simp [keyLabel, String.data_append, List.reverse_append, h3]

theorem rev_inj {l l' : List Char} (h : l.reverse = l'.reverse) : l = l' := by
  simpa using congrArg List.reverse h

theorem string_rv {s t : String} (h : s = t) : s.data.reverse = t.data.reverse := by rw [h]

theorem one_inj {R R' : ReadingSet} (h : "readings:" ++ label R ++ ":one" = "readings:" ++ label R' ++ ":one") :
    R.id = R'.id ∧ R.version = R'.version := by
  have := string_rv h
  rw [rv_one, rv_one] at this
  simp only [List.append_assoc, List.cons_append, List.nil_append, List.cons.injEq, true_and] at this
  obtain ⟨hd, _, hr⟩ := split_runs (Or.inr rfl) (Or.inr rfl) _ _ _ _ (noSep_reverse (digits_noSep _))
    (noSep_reverse (digits_noSep _)) this
  exact ⟨String.ext (rev_inj (List.append_cancel_right hr)), toDigits_inj (rev_inj hd)⟩

theorem own_inj {R R' : ReadingSet} {i i' : Nat}
    (h : "readings:" ++ label R ++ ":" ++ toString i ++ ":quiet" = "readings:" ++ label R' ++ ":" ++ toString i' ++ ":quiet") :
    R.id = R'.id ∧ R.version = R'.version ∧ i = i' := by
  have := string_rv h
  rw [rv_own, rv_own] at this
  simp only [List.append_assoc, List.cons_append, List.nil_append, List.cons.injEq, true_and] at this
  obtain ⟨hi, _, hr⟩ := split_runs (Or.inl rfl) (Or.inl rfl) _ _ _ _ (noSep_reverse (digits_noSep _))
    (noSep_reverse (digits_noSep _)) this
  obtain ⟨hv, _, hr⟩ := split_runs (Or.inr rfl) (Or.inr rfl) _ _ _ _ (noSep_reverse (digits_noSep _))
    (noSep_reverse (digits_noSep _)) hr
  exact ⟨String.ext (rev_inj (List.append_cancel_right hr)), toDigits_inj (rev_inj hv), toDigits_inj (rev_inj hi)⟩

theorem one_ne_own (R R' : ReadingSet) (i : Nat) :
    "readings:" ++ label R ++ ":one" ≠ "readings:" ++ label R' ++ ":" ++ toString i ++ ":quiet" := by
  intro h
  have := string_rv h
  rw [rv_one, rv_own] at this
  simp at this

theorem one_ne_shared (R : ReadingSet) {a L H : String} (hL : NoSep L.data) (hH : NoSep H.data) :
    "readings:" ++ label R ++ ":one" ≠ "readings:quiet:" ++ keyLabel (.outweighs a L H) := by
  intro h
  have := string_rv h
  rw [rv_one, rv_shared] at this
  have hrun : NoSep ['e', 'n', 'o'] := by decide
  obtain ⟨_, _, hr⟩ := split_runs (Or.inl rfl) (Or.inl rfl) _ _ _ _ hrun (noSep_reverse hH) this
  obtain ⟨_, hx, _⟩ := split_runs (Or.inr rfl) (Or.inl rfl) _ _ _ _ (noSep_reverse (digits_noSep _))
    (noSep_reverse hL) hr
  cases hx

theorem own_ne_shared (R : ReadingSet) (i : Nat) {a L H : String} (hL : validSoftName L = true)
    (hH : NoSep H.data) :
    "readings:" ++ label R ++ ":" ++ toString i ++ ":quiet" ≠ "readings:quiet:" ++ keyLabel (.outweighs a L H) := by
  intro h
  have := string_rv h
  rw [rv_own, rv_shared] at this
  have hrun : NoSep ['t', 'e', 'i', 'u', 'q'] := by decide
  obtain ⟨_, _, hr⟩ := split_runs (Or.inl rfl) (Or.inl rfl) _ _ _ _ hrun (noSep_reverse hH) this
  obtain ⟨hd, _, _⟩ := split_runs (Or.inl rfl) (Or.inl rfl) _ _ _ _ (noSep_reverse (digits_noSep _))
    (noSep_reverse (validSoftName_noSep hL)) hr
  have hd' := rev_inj hd
  obtain ⟨⟨c, l, hcl, hc1, hc2⟩, _⟩ := validSoftName_data hL
  rw [hcl] at hd'
  have := digits_digit i c (by rw [hd']; simp)
  exact absurd (Char.le_trans hc1 this.2) (by decide)

theorem shared_inj {a L H a' L' H' : String} (hL : NoSep L.data) (hH : NoSep H.data) (hL' : NoSep L'.data)
    (hH' : NoSep H'.data)
    (h : "readings:quiet:" ++ keyLabel (.outweighs a L H) = "readings:quiet:" ++ keyLabel (.outweighs a' L' H')) :
    a = a' ∧ L = L' ∧ H = H' := by
  have := string_rv h
  rw [rv_shared, rv_shared] at this
  obtain ⟨hH0, _, hr⟩ := split_runs (Or.inl rfl) (Or.inl rfl) _ _ _ _ (noSep_reverse hH) (noSep_reverse hH') this
  obtain ⟨hL0, _, hr⟩ := split_runs (Or.inl rfl) (Or.inl rfl) _ _ _ _ (noSep_reverse hL) (noSep_reverse hL') hr
  simp only [List.append_assoc] at hr
  have ha := List.append_cancel_right hr
  exact ⟨String.ext (rev_inj ha), String.ext (rev_inj hL0), String.ext (rev_inj hH0)⟩

theorem head_ne {s t : String} {u v : String} (h : s.data.head? ≠ t.data.head?) (hs : s.data ≠ [])
    (ht : t.data ≠ []) : s ++ u ≠ t ++ v := by
  intro he
  have := congrArg (fun x : String => x.data.head?) he
  simp only [String.data_append] at this
  cases hsd : s.data with
  | nil => exact hs hsd
  | cons c l =>
    cases htd : t.data with
    | nil => exact ht htd
    | cons d l' =>
      rw [hsd, htd] at h this
      simp only [List.cons_append, List.head?_cons] at h this
      exact h this

end VE.Readings

namespace VE.Readings
open VE.SoftNorms (SoftNode SoftDoc soften validSoftName)
open VE.Rights (RightsDoc correlate limPremisesLabelled)
open VE.Compose (Labelled)

/-! ## `slot_wellLabelled` -/

theorem nodup_filterMap {α β : Type} {f : α → Option β} : ∀ {l : List α}, l.Nodup →
    (∀ a ∈ l, ∀ a' ∈ l, ∀ b, f a = some b → f a' = some b → a = a') → (l.filterMap f).Nodup
  | [], _, _ => List.nodup_nil
  | a :: l, hl, hf => by
    rw [List.nodup_cons] at hl
    have ih := nodup_filterMap hl.2 (fun x hx y hy b h1 h2 => hf x (List.mem_cons_of_mem _ hx) y
      (List.mem_cons_of_mem _ hy) b h1 h2)
    rw [List.filterMap_cons]
    cases ha : f a with
    | none => exact ih
    | some b =>
      refine List.nodup_cons.mpr ⟨fun hb => ?_, ih⟩
      obtain ⟨a', ha', hb'⟩ := List.mem_filterMap.mp hb
      have := hf a List.mem_cons_self a' (List.mem_cons_of_mem _ ha') b ha hb'
      subst this
      exact hl.1 ha'

theorem nodup_flatMap {α β : Type} {f : α → List β} : ∀ {l : List α}, l.Nodup → (∀ a ∈ l, (f a).Nodup) →
    (∀ a ∈ l, ∀ a' ∈ l, ∀ b ∈ f a, b ∈ f a' → a = a') → (l.flatMap f).Nodup
  | [], _, _, _ => List.nodup_nil
  | a :: l, hl, hn, hd => by
    rw [List.nodup_cons] at hl
    rw [List.flatMap_cons, List.nodup_append]
    refine ⟨hn a List.mem_cons_self, nodup_flatMap hl.2 (fun x hx => hn x (List.mem_cons_of_mem _ hx))
      (fun x hx y hy b h1 h2 => hd x (List.mem_cons_of_mem _ hx) y (List.mem_cons_of_mem _ hy) b h1 h2), ?_⟩
    intro b hb b' hb' he
    subst he
    obtain ⟨a', ha', hb''⟩ := List.mem_flatMap.mp hb'
    have := hd a List.mem_cons_self a' (List.mem_cons_of_mem _ ha') b hb hb''
    subst this
    exact hl.1 ha'

theorem depPath_mem {ns : List VE.Route.DepNode} {a b : String} (h : VE.Route.DepPath ns a b) :
    a ∈ VE.Route.nodeNames ns ∧ b ∈ VE.Route.nodeNames ns := by
  induction h with
  | edge he =>
    obtain ⟨n, hn, rfl, hb⟩ := he
    refine ⟨List.mem_map.mpr ⟨n, hn, rfl⟩, ?_⟩
    simp only [VE.Route.deps, List.mem_filter, List.contains_iff_mem] at hb
    exact hb.2
  | trans _ _ ih₁ ih₂ => exact ⟨ih₁.1, ih₂.2⟩

theorem higher_ranks {X : SoftDoc} (hv : VE.SoftNorms.RanksValid X.soft) {M N : SoftNode}
    (h : VE.SoftNorms.higher X M N = true) :
    ∃ a b, M.rank = some a ∧ N.rank = some b ∧ a ∈ X.soft.ranks ∧ b ∈ X.soft.ranks := by
  unfold VE.SoftNorms.higher at h
  split at h
  · rename_i a b ha hb
    have hp := depPath_mem ((VE.SoftNorms.outranksPlus_iff_path hv a b).mp h)
    simp only [VE.Route.nodeNames, VE.SoftNorms.rankNodes, List.map_map, List.mem_map] at hp
    obtain ⟨⟨x, hx, rfl⟩, ⟨y, hy, rfl⟩⟩ := hp
    exact ⟨x, y, ha, hb, hx, hy⟩
  · cases h

/-- The ranks of an outweighs key of a well-formed soft document are soft names. -/
theorem outweighs_ranks {X : RightsDoc} (hw : VE.SoftNorms.WellFormedSoft (correlate X) = true) {a L H : String}
    (ht : (a, L, H) ∈ VE.SoftNorms.outweighsTriples (correlate X)) : validSoftName L = true ∧ validSoftName H = true := by
  have hv := VE.SoftNorms.softValid_of_wellFormed _ hw
  have hn := checkSoftEnv_names _ (checkSoft_parts _ (wellFormedSoft_check _ hw)).1
  obtain ⟨_, M, N, _, hcmp, hpt⟩ := mem_outweighsTriples.mp ht
  have hr : ∀ {P Q : SoftNode}, VE.SoftNorms.higher (correlate X) P Q = true →
      validSoftName (VE.SoftNorms.rk P) = true ∧ validSoftName (VE.SoftNorms.rk Q) = true := by
    intro P Q hpq
    obtain ⟨x, y, hx, hy, hxr, hyr⟩ := higher_ranks hv.ranks hpq
    simp only [VE.SoftNorms.rk, hx, hy, Option.getD_some]
    exact ⟨hn x (List.mem_append_left _ hxr), hn y (List.mem_append_left _ hyr)⟩
  unfold VE.SoftNorms.pairTriple at hpt
  split at hpt
  · rename_i hh
    simp only [Prod.mk.injEq] at hpt
    obtain ⟨_, rfl, rfl⟩ := hpt
    exact ⟨(hr hh).2, (hr hh).1⟩
  · rename_i hh
    simp only [VE.SoftNorms.Comparable, Bool.or_eq_true, hh, false_or, Bool.false_eq_true] at hcmp
    simp only [Prod.mk.injEq] at hpt
    obtain ⟨_, rfl, rfl⟩ := hpt
    exact ⟨(hr hcmp).2, (hr hcmp).1⟩

/-- A key of `quietShared D` is an outweighs key: an exception or switch key has one owner, a single candidate or
    none, and a key of a fixed limitation or bar is fixed-generated. -/
theorem shared_outweighs {D : Doc} {k : GenKey}
    (hf : (!fixedGenerated D k && ((owners D k).length != 1 || (owners D k).any (·.length != 1))) = true) :
    ∃ a L H, k = .outweighs a L H := by
  cases k with
  | outweighs a L H => exact ⟨a, L, H, rfl⟩
  | excepted r b =>
    exfalso
    cases ho : origin D r <;> simp [owners, fixedGenerated, ho] at hf
  | off r b π =>
    exfalso
    cases ho : origin D r <;> simp [owners, fixedGenerated, ho] at hf
  | lim L a => simp [owners, fixedGenerated] at hf
  | cond L a c => simp [owners, fixedGenerated] at hf
  | aimed m => simp [owners, fixedGenerated] at hf

theorem readings_head (A B : String) : (("readings:" ++ A) ++ B).data.head? = some 'r' := by
  simp [String.data_append]

theorem readings_quiet_head (A : String) : ("readings:quiet:" ++ A).data.head? = some 'r' := by
  simp [String.data_append]

theorem readings_head₂ (A B C D : String) : (((("readings:" ++ A) ++ B) ++ C) ++ D).data.head? = some 'r' := by
  simp [String.data_append]

theorem coupling_head (A : String) : ("coupling:" ++ A).data.head? = some 'c' := by
  simp [String.data_append]

theorem narrowing_head (A : String) : ("narrowing:" ++ A).data.head? = some 'n' := by
  simp [String.data_append]

theorem ne_of_head {s t : String} {x y : Char} (hs : s.data.head? = some x) (ht : t.data.head? = some y)
    (hxy : x ≠ y) : s ≠ t := by
  intro h; rw [h, ht] at hs; cases hs; exact hxy rfl

theorem append_left_inj {p a b : String} (h : p ++ a = p ++ b) : a = b := by
  have := congrArg String.data h
  simp only [String.data_append] at this
  exact String.ext (List.append_cancel_left this)

theorem slot_wellLabelled (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) : (slotLabelled D).wellLabelled = true := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  have hr := hh.ready
  have hn := hh.nodup
  have hlim : limPremisesLabelled (sup D).1 = [] := by
    simp [limPremisesLabelled, VE.Rights.condKeys_nil _ (noRights_parts hh.noRights).2.1]
  have hwX : VE.SoftNorms.WellFormedSoft (correlate (sup D).1) = true := (sup_wellFormed D hs).2
  simp only [Labelled.wellLabelled, decide_eq_true_eq, slotLabelled, hlim, gatedRel, List.nil_append,
    List.append_nil, choiceLabelled, List.map_append]
  -- the five families
  have hone : ∀ x ∈ (onePremises D).map (·.1), ∃ m, ∃ hm : m < D.sets.length,
      x = "readings:" ++ label D.sets[m] ++ ":one" := by
    intro x hx
    simp only [onePremises, List.mem_map, List.mem_filterMap, List.mem_range] at hx
    obtain ⟨⟨l, f⟩, ⟨m, hm, hb⟩, rfl⟩ := hx
    rw [List.getElem?_eq_getElem hm] at hb
    simp only [Option.bind_some] at hb
    split at hb
    · cases hb
    · cases hb; exact ⟨m, hm, rfl⟩
  have hown : ∀ x ∈ (quietOwn D).map (·.1), ∃ m, ∃ hm : m < D.sets.length, ∃ i : Nat,
      x = "readings:" ++ label D.sets[m] ++ ":" ++ toString i ++ ":quiet" := by
    intro x hx
    simp only [quietOwn, List.mem_map, List.mem_flatMap, List.mem_filterMap, List.mem_range] at hx
    obtain ⟨⟨l, f⟩, ⟨m, hm, R, hR, i, _, hb⟩, rfl⟩ := hx
    rw [List.getElem?_eq_getElem hm] at hR
    simp only [Option.toList_some, List.mem_singleton] at hR
    subst hR
    split at hb
    · cases hb
    · cases hb; exact ⟨m, hm, i, rfl⟩
  have hsh : ∀ x ∈ (quietShared D).map (·.1), ∃ g ∈ genKeys (sup D).1, ∃ a L H, g.1 = .outweighs a L H ∧
      validSoftName L = true ∧ validSoftName H = true ∧ x = "readings:quiet:" ++ keyLabel (.outweighs a L H) := by
    intro x hx
    simp only [quietShared, List.map_map, List.mem_map, List.mem_filter, Function.comp] at hx
    obtain ⟨g, ⟨hg, hf⟩, rfl⟩ := hx
    obtain ⟨a, L, H, hk⟩ := shared_outweighs hf
    have hv := outweighs_ranks hwX (mem_genKeys_outweighs hg hk)
    exact ⟨g, hg, a, L, H, hk, hv.1, hv.2, by rw [hk]⟩
  have hcp : ∀ x ∈ (couplingPremises D).map (·.1), ∃ K ∈ D.couplings, x = "coupling:" ++ K.id := by
    intro x hx
    simp only [couplingPremises, List.mem_map, List.mem_filterMap] at hx
    obtain ⟨⟨l, f⟩, ⟨K, hK, hb⟩, rfl⟩ := hx
    split at hb
    · cases hb
    · cases hb; exact ⟨K, hK, rfl⟩
  have hnw : ∀ x ∈ (narrowingPremises D).map (·.1), ∃ N ∈ D.narrowings, x = "narrowing:" ++ N.id := by
    intro x hx
    simp only [narrowingPremises, List.mem_map, List.mem_filterMap] at hx
    obtain ⟨⟨l, f⟩, ⟨N, hN, hb⟩, rfl⟩ := hx
    cases hf : inForce D N with
    | none => rw [hf] at hb; cases hb
    | some R =>
      rw [hf] at hb
      simp only [Option.bind_some] at hb
      split at hb
      · cases hb
      · cases hb; exact ⟨N, hN, rfl⟩
  -- heads
  have hdr1 : ∀ x ∈ (onePremises D).map (·.1), x.data.head? = some 'r' := by
    intro x hx; obtain ⟨m, hm, rfl⟩ := hone x hx; exact readings_head _ _
  have hdr2 : ∀ x ∈ (quietOwn D).map (·.1), x.data.head? = some 'r' := by
    intro x hx; obtain ⟨m, hm, i, rfl⟩ := hown x hx; exact readings_head₂ _ _ _ _
  have hdr3 : ∀ x ∈ (quietShared D).map (·.1), x.data.head? = some 'r' := by
    intro x hx; obtain ⟨_, _, _, _, _, _, _, _, rfl⟩ := hsh x hx; exact readings_quiet_head _
  have hdc : ∀ x ∈ (couplingPremises D).map (·.1), x.data.head? = some 'c' := by
    intro x hx; obtain ⟨K, _, rfl⟩ := hcp x hx; exact coupling_head _
  have hdn : ∀ x ∈ (narrowingPremises D).map (·.1), x.data.head? = some 'n' := by
    intro x hx; obtain ⟨N, _, rfl⟩ := hnw x hx; exact narrowing_head _
  -- each family has distinct labels
  have n1 : ((onePremises D).map (·.1)).Nodup := by
    simp only [onePremises, List.map_filterMap]
    apply nodup_filterMap List.nodup_range
    intro m hm m' hm' b h1 h2
    rw [List.mem_range] at hm hm'
    rw [List.getElem?_eq_getElem hm] at h1
    rw [List.getElem?_eq_getElem hm'] at h2
    simp only [Option.bind_some] at h1 h2
    split at h1 <;> split at h2 <;> simp only [Option.map_none, Option.map_some, reduceCtorEq,
      Option.some.injEq] at h1 h2
    exact ids_inj hn hm hm' (one_inj (h1.trans h2.symm)).1
  have n2 : ((quietOwn D).map (·.1)).Nodup := by
    simp only [quietOwn, List.map_flatMap]
    apply nodup_flatMap List.nodup_range
    · intro m hm
      rw [List.mem_range] at hm
      rw [List.getElem?_eq_getElem hm]
      simp only [Option.toList_some, List.flatMap_cons, List.flatMap_nil, List.append_nil, List.map_filterMap]
      apply nodup_filterMap List.nodup_range
      intro i _ i' _ b h1 h2
      split at h1 <;> split at h2 <;> simp only [Option.map_none, Option.map_some, reduceCtorEq,
        Option.some.injEq] at h1 h2
      exact (own_inj (h1.trans h2.symm)).2.2
    · intro m hm m' hm' b h1 h2
      rw [List.mem_range] at hm hm'
      rw [List.getElem?_eq_getElem hm] at h1
      rw [List.getElem?_eq_getElem hm'] at h2
      simp only [Option.toList_some, List.flatMap_cons, List.flatMap_nil, List.append_nil, List.map_filterMap,
        List.mem_filterMap] at h1 h2
      obtain ⟨i, _, h1⟩ := h1
      obtain ⟨i', _, h2⟩ := h2
      split at h1 <;> split at h2 <;> simp only [Option.map_none, Option.map_some, reduceCtorEq,
        Option.some.injEq] at h1 h2
      exact ids_inj hn hm hm' (own_inj (h1.trans h2.symm)).1
  have n3 : ((quietShared D).map (·.1)).Nodup := by
    have hk := genKeys_nodup D.chain (sup D).1 (sup_wellFormed D hs).1 (by
      simp [linesOnce, (noRights_parts hh.noRights).2.2.2])
    have hgn : (genKeys (sup D).1).Nodup := nodup_of_map hk
    simp only [quietShared, List.map_map]
    apply nodup_map_on _ (hgn.sublist List.filter_sublist)
    intro g hg g' hg' he
    obtain ⟨hgm, hf⟩ := List.mem_filter.mp hg
    obtain ⟨hgm', hf'⟩ := List.mem_filter.mp hg'
    obtain ⟨a, L, H, hk1⟩ := shared_outweighs hf
    obtain ⟨a', L', H', hk1'⟩ := shared_outweighs hf'
    have hv := outweighs_ranks hwX (mem_genKeys_outweighs hgm hk1)
    have hv' := outweighs_ranks hwX (mem_genKeys_outweighs hgm' hk1')
    simp only [Function.comp] at he
    rw [hk1, hk1'] at he
    obtain ⟨rfl, rfl, rfl⟩ := shared_inj (validSoftName_noSep hv.1) (validSoftName_noSep hv.2)
      (validSoftName_noSep hv'.1) (validSoftName_noSep hv'.2) he
    exact inj_of_nodup_map hk hgm hgm' (hk1.trans hk1'.symm)
  have n4 : ((couplingPremises D).map (·.1)).Nodup := by
    have hci : (D.couplings.map (·.id)).Nodup := by
      simp only [supReady, Bool.and_eq_true, decide_eq_true_eq] at hr; exact hr.1.1.1.1.1.2
    simp only [couplingPremises, List.map_filterMap]
    apply nodup_filterMap (nodup_of_map hci)
    intro K hK K' hK' b h1 h2
    split at h1 <;> split at h2 <;> simp only [Option.map_none, Option.map_some, reduceCtorEq,
      Option.some.injEq] at h1 h2
    exact inj_of_nodup_map hci hK hK' (append_left_inj (h1.trans h2.symm))
  have n5 : ((narrowingPremises D).map (·.1)).Nodup := by
    have hni : (D.narrowings.map (·.id)).Nodup := by
      simp only [supReady, Bool.and_eq_true, decide_eq_true_eq] at hr; exact hr.1.1.1.2
    simp only [narrowingPremises, List.map_filterMap]
    apply nodup_filterMap (nodup_of_map hni)
    intro N hN N' hN' b h1 h2
    cases hf : inForce D N <;> cases hf' : inForce D N' <;> simp only [hf, hf', Option.bind_none,
      Option.bind_some, Option.map_none, reduceCtorEq] at h1 h2
    split at h1 <;> split at h2 <;> simp only [Option.map_none, Option.map_some, reduceCtorEq,
      Option.some.injEq] at h1 h2
    exact inj_of_nodup_map hni hN hN' (append_left_inj (h1.trans h2.symm))
  -- across families
  refine List.nodup_append.mpr ⟨List.nodup_append.mpr ⟨List.nodup_append.mpr ⟨List.nodup_append.mpr
    ⟨n1, n2, ?_⟩, n3, ?_⟩, n4, ?_⟩, n5, ?_⟩
  · intro x hx y hy he
    obtain ⟨m, hm, rfl⟩ := hone x hx
    obtain ⟨m', hm', i, rfl⟩ := hown y hy
    exact one_ne_own _ _ _ he
  · intro x hx y hy he
    obtain ⟨_, _, a, L, H, _, hL, hH, rfl⟩ := hsh y hy
    rcases List.mem_append.mp hx with hx | hx
    · obtain ⟨m, hm, rfl⟩ := hone x hx
      exact one_ne_shared _ (validSoftName_noSep hL) (validSoftName_noSep hH) he
    · obtain ⟨m, hm, i, rfl⟩ := hown x hx
      exact own_ne_shared _ _ hL (validSoftName_noSep hH) he
  · intro x hx y hy
    have hy' := hdc y hy
    have hx' : x.data.head? = some 'r' := by
      rcases List.mem_append.mp hx with hx | hx
      · rcases List.mem_append.mp hx with hx | hx
        · exact hdr1 x hx
        · exact hdr2 x hx
      · exact hdr3 x hx
    exact ne_of_head hx' hy' (by decide)
  · intro x hx y hy
    have hy' := hdn y hy
    rcases List.mem_append.mp hx with hx | hx
    · have hx' : x.data.head? = some 'r' := by
        rcases List.mem_append.mp hx with hx | hx
        · rcases List.mem_append.mp hx with hx | hx
          · exact hdr1 x hx
          · exact hdr2 x hx
        · exact hdr3 x hx
      exact ne_of_head hx' hy' (by decide)
    · exact ne_of_head (hdc x hx) hy' (by decide)

end VE.Readings
