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


theorem parseStatements_nonempty (E : Environment) (fuel : Nat) (input : List Char)
    (h : input ≠ []) :
    parseStatements E (fuel + 1) input = (do
      let (a, rest) ← parseRaw E (input.length + 1) [] input
      let rest ← consume ['.', '\n'] rest
      let tail ← parseStatements E fuel rest
      some (a :: tail)) := by
  cases input with
  | nil => contradiction
  | cons c cs => rfl

/-- Public document P4 for one closed well-typed Named closure statement. -/
theorem parse_print_named (E : Environment) (hv : NamesValid E)
    (k : Kind) (p : String) (t u : Term)
    (hw : (Formula.reachNamed k p t u).WellFormed E []) :
    parse E (print [.reachNamed k p t u]) = some [.reachNamed k p t u] := by
  let a := Formula.reachNamed k p t u
  have hn : statementChars a ≠ [] := by simp [statementChars]
  have hp := parseRaw_print_named E hv [] [] 0 ⟨by simp, by simp⟩ rfl k p t u hw
    (statementChars a).length ['.', '\n']
  have hc : a.check E [] = true := (check_iff_wellFormed E [] a).mpr hw
  unfold parse print
  simp only [List.flatMap_cons, List.flatMap_nil, List.append_nil]
  change (do
    let fs ← parseStatements E ((statementChars a).length + 1) (statementChars a)
    if !fs.isEmpty && fs.all (fun f => f.check E []) then some fs else none) = some [a]
  rw [parseStatements_nonempty E _ _ hn]
  change parseRaw E ((statementChars a).length + 1) [] (statementChars a) = some (a, ['.', '\n']) at hp
  rw [hp]
  simp [consume, statementChars, List.length_append, parseStatements, hc]

/-- Two closed typed Named atoms with identical printed documents are identical. -/
theorem print_injective_named (E : Environment) (hv : NamesValid E)
    (k l : Kind) (p q : String) (t u v w : Term)
    (ha : (Formula.reachNamed k p t u).WellFormed E [])
    (hb : (Formula.reachNamed l q v w).WellFormed E [])
    (h : print [.reachNamed k p t u] = print [.reachNamed l q v w]) :
    Formula.reachNamed k p t u = Formula.reachNamed l q v w := by
  have hparse := congrArg (parse E) h
  rw [parse_print_named E hv k p t u ha, parse_print_named E hv l q v w hb] at hparse
  exact List.cons.inj (Option.some.inj hparse) |>.1

end VE.Closure.Surface
