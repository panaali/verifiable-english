import VE.Closure.Surface

namespace VE.Closure.Surface
open VE.Surface

/-- Strict Named closure round trip for either kind, arbitrary typed endpoints,
canonical outer scopes, every parser fuel > 0, and every suffix. Body printing
and parsing are executable but their round-trip extension is not asserted here. -/
theorem parseRaw_print_named (E : Environment) (hv : NamesValid E)
    (Γ names : List String) (next : Nat) (hs : Scope names next)
    (hl : names.length = Γ.length) (k : Kind) (p : String) (t u : Term)
    (hw : (Formula.reachNamed k p t u).WellFormed E Γ)
    (fuel : Nat) (tail : List Char) :
    parseRaw E (fuel + 1) names ((printAux names next (.reachNamed k p t u)).1 ++ tail) =
      some (.reachNamed k p t u, tail) := by
  obtain ⟨s, hp, ht, hu⟩ := hw
  have hid := declaration_identifier p (hv.2.1 p [s, s] hp)
  have hi := readIdent_append p
    ("](".toList ++ printTerm names t ++ ", ".toList ++ printTerm names u ++ ')' :: tail)
    hid (by rfl)
  have hpt := parseTerm_print E hv Γ names next hs hl t s ht
    (", ".toList ++ printTerm names u ++ ')' :: tail) (by rfl)
  have hpu := parseTerm_print E hv Γ names next hs hl u s hu (')' :: tail) (by rfl)
  simp only [String.toList, List.append_assoc, List.cons_append, List.nil_append] at hi hpt hpu
  cases k <;>
    simp [printAux, kindText, List.append_assoc, parseRaw, parseReach, hi, hpt, hpu, consume]

end VE.Closure.Surface
