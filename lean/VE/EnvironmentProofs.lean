import VE.Bridge
import VE.RoundTrip

namespace VE.Bridge

theorem lookup_name (xs : List (String × α)) (key : String) (value : α)
    (h : lookup xs key = some value) : ∃ v, (key, v) ∈ xs := by
  induction xs with
  | nil => simp [lookup] at h
  | cons x xs ih =>
    by_cases he : x.1 = key
    · subst key
      exact ⟨x.2, by simp⟩
    · have hb : (x.1 == key) = false := beq_eq_false_iff_ne.mpr he
      have ht : lookup xs key = some value := by
        simpa [lookup, List.find?_cons, hb] using h
      obtain ⟨v, hv⟩ := ih ht
      exact ⟨v, by simp [hv]⟩

/-- Successful executable name validation supplies exactly the lexical premises
of P4, for every finite vocabulary, independently of JSON decoding. -/
theorem vocabulary_namesValid (v : Vocabulary) (h : v.namesValid = true) :
    Surface.NamesValid v.environment := by
  simp only [Vocabulary.namesValid, Bool.and_eq_true, List.all_eq_true] at h
  refine ⟨h.1.1, ?_, ?_⟩
  · intro p ss hp
    obtain ⟨value, hm⟩ := lookup_name v.predicates p ss hp
    exact h.1.2 (p, value) hm
  · intro c s hc
    obtain ⟨value, hm⟩ := lookup_name v.constants c s hc
    exact h.2 (c, value) hm

end VE.Bridge
