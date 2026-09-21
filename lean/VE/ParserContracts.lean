import VE.RoundTrip

namespace VE.Surface

/-- Successful parsing determines the exact normalization result. This follows
from normalization's definition; it is not independent grammar soundness. -/
theorem accepted_normalize (E : Environment) (text : String) (fs : List Formula)
    (accepted : parse E text = some fs) : normalize E text = some (print fs) := by
  simp [normalize, accepted]

/-- Accepted text can be canonically printed and reparsed without changing any
constructor, term index, symbol, or statement order. -/
theorem accepted_reparse (E : Environment) (hv : NamesValid E) (text : String)
    (fs : List Formula) (accepted : parse E text = some fs) :
    parse E (print fs) = some fs := by
  obtain ⟨hne, hw⟩ := parse_wellFormed E text fs accepted
  exact parse_print E hv ⟨fs, hne, hw⟩

/-- Injectivity of canonical printing on closed typed nonempty documents.
This establishes uniqueness of canonical representations, not arbitrary EBNF
parse derivations; the latter requires an independent grammar relation. -/
theorem print_injective (E : Environment) (hv : NamesValid E) (a b : Document E)
    (same : print a.formulas = print b.formulas) : a = b := by
  have ha := parse_print E hv a
  have hb := parse_print E hv b
  rw [same, hb] at ha
  have he : b.formulas = a.formulas := Option.some.inj ha
  cases a
  cases b
  cases he
  rfl

/-- The canonical rendering relation has one document for each String. -/
theorem canonical_unique (E : Environment) (hv : NamesValid E) (text : String)
    (a b : Document E) (ha : print a.formulas = text) (hb : print b.formulas = text) :
    a = b :=
  print_injective E hv a b (ha.trans hb.symm)

/-- On accepted inputs, equal normal forms hold exactly when indexed AST lists
are equal. This excludes semantic simplification or loss of statement ordering. -/
theorem accepted_normalize_eq_iff (E : Environment) (hv : NamesValid E)
    (s t : String) (a b : List Formula)
    (hs : parse E s = some a) (ht : parse E t = some b) :
    normalize E s = normalize E t ↔ a = b := by
  rw [accepted_normalize E s a hs, accepted_normalize E t b ht]
  constructor
  · intro he
    obtain ⟨hna, hwa⟩ := parse_wellFormed E s a hs
    obtain ⟨hnb, hwb⟩ := parse_wellFormed E t b ht
    have hd := print_injective E hv ⟨a, hna, hwa⟩ ⟨b, hnb, hwb⟩ (Option.some.inj he)
    exact congrArg Document.formulas hd
  · intro he
    rw [he]

/-- Every well-formed document has exactly its own fixed canonical normal form. -/
theorem normalize_print (E : Environment) (hv : NamesValid E) (d : Document E) :
    normalize E (print d.formulas) = some (print d.formulas) :=
  accepted_normalize E _ _ (parse_print E hv d)

end VE.Surface
