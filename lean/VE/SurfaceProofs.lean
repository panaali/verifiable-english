import VE.Surface

namespace VE.Surface

/-- Exact proved surface fragment: true, false, negation, conjunction,
disjunction and implication, with arbitrary nesting but no atomic terms,
predicates or quantifiers. These are syntax trees, not truth-table quotients. -/
inductive Propositional where
  | top | bottom
  | not (a : Propositional)
  | and (a b : Propositional)
  | or (a b : Propositional)
  | implies (a b : Propositional)
  deriving Repr

def Propositional.embed : Propositional → Formula
  | .top => .top
  | .bottom => .bottom
  | .not a => .not a.embed
  | .and a b => .and a.embed b.embed
  | .or a b => .or a.embed b.embed
  | .implies a b => .implies a.embed b.embed

def Propositional.code : Propositional → List Char
  | .top => "true".toList
  | .bottom => "false".toList
  | .not a => "not (".toList ++ a.code ++ [')']
  | .and a b => ['('] ++ a.code ++ ") and (".toList ++ b.code ++ [')']
  | .or a b => ['('] ++ a.code ++ ") or (".toList ++ b.code ++ [')']
  | .implies a b => "if (".toList ++ a.code ++ "), then (".toList ++ b.code ++ [')']

def Propositional.depth : Propositional → Nat
  | .top | .bottom => 0
  | .not a => a.depth + 1
  | .and a b | .or a b | .implies a b => max a.depth b.depth + 1

theorem propositional_printAux (p : Propositional) (names : List String) (next : Nat) :
    printAux names next p.embed = (p.code, next) := by
  induction p generalizing names next <;>
    simp_all [Propositional.embed, Propositional.code, printAux]

theorem propositional_check (E : Environment) (Γ : List String) (p : Propositional) :
    p.embed.check E Γ = true := by
  induction p <;> simp_all [Propositional.embed, Formula.check]

theorem consume_append (pref suffix : List Char) :
    consume pref (pref ++ suffix) = some suffix := by
  induction pref with
  | nil => rfl
  | cons c cs ih => simp [consume, ih]

theorem propositional_depth_le_length (p : Propositional) : p.depth ≤ p.code.length := by
  induction p <;> simp_all [Propositional.depth, Propositional.code, List.length_append,
    String.toList] <;> omega

/-- The actual full parser recovers the embedded fragment from printed bytes,
leaving any delimiter-starting suffix untouched, with sufficient depth fuel. -/
theorem parseRaw_propositional (E : Environment) (p : Propositional)
    (fuel : Nat) (names : List String) (tail : List Char)
    (hd : boundary tail = true) (hf : p.depth < fuel) :
    parseRaw E fuel names (p.code ++ tail) = some (p.embed, tail) := by
  induction p generalizing fuel names tail with
  | top =>
    cases fuel with
    | zero => simp [Propositional.depth] at hf
    | succ n => simp [Propositional.code, Propositional.embed, parseRaw, parseRawWith, hd]
  | bottom =>
    cases fuel with
    | zero => simp [Propositional.depth] at hf
    | succ n => simp [Propositional.code, Propositional.embed, parseRaw, parseRawWith, hd]
  | not a ih =>
    cases fuel with
    | zero => omega
    | succ n =>
      have ha : a.depth < n := by simp only [Propositional.depth] at hf; omega
      have h := ih n names (')' :: tail) (by rfl) ha
      simp [Propositional.code, Propositional.embed, List.append_assoc, parseRaw, parseRawWith,
        h, consume]
  | and a b ia ib =>
    cases fuel with
    | zero => omega
    | succ n =>
      have ha : a.depth < n := by simp only [Propositional.depth] at hf; omega
      have hb : b.depth < n := by simp only [Propositional.depth] at hf; omega
      have hia := ia n names (") and (".toList ++ b.code ++ ')' :: tail) (by rfl) ha
      have hib := ib n names (')' :: tail) (by rfl) hb
      simp only [String.toList, List.cons_append, List.nil_append] at hia
      simp [Propositional.code, Propositional.embed, List.append_assoc, parseRaw, parseRawWith,
        hia, hib, consume]
  | or a b ia ib =>
    cases fuel with
    | zero => omega
    | succ n =>
      have ha : a.depth < n := by simp only [Propositional.depth] at hf; omega
      have hb : b.depth < n := by simp only [Propositional.depth] at hf; omega
      have hia := ia n names (") or (".toList ++ b.code ++ ')' :: tail) (by rfl) ha
      have hib := ib n names (')' :: tail) (by rfl) hb
      simp only [String.toList, List.cons_append, List.nil_append] at hia
      simp [Propositional.code, Propositional.embed, List.append_assoc, parseRaw, parseRawWith,
        hia, hib, consume]
  | implies a b ia ib =>
    cases fuel with
    | zero => omega
    | succ n =>
      have ha : a.depth < n := by simp only [Propositional.depth] at hf; omega
      have hb : b.depth < n := by simp only [Propositional.depth] at hf; omega
      have hia := ia n names ("), then (".toList ++ b.code ++ ')' :: tail) (by rfl) ha
      have hib := ib n names (')' :: tail) (by rfl) hb
      simp only [String.toList, List.cons_append, List.nil_append] at hia
      simp [Propositional.code, Propositional.embed, List.append_assoc, parseRaw, parseRawWith,
        hia, hib, consume]

def propositionalDocumentChars (ps : List Propositional) : List Char :=
  ps.flatMap (fun p => p.code ++ ['.', '\n'])

theorem propositional_code_nonempty (p : Propositional) : p.code ≠ [] := by
  cases p <;> simp [Propositional.code]

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

/-- The prefix proof lifts to any finite list of propositional statements. -/
theorem parseStatements_propositional (E : Environment) (ps : List Propositional)
    (fuel : Nat) (hf : ps.length < fuel) :
    parseStatements E fuel (propositionalDocumentChars ps) = some (ps.map Propositional.embed) := by
  induction ps generalizing fuel with
  | nil =>
    cases fuel with
    | zero => simp at hf
    | succ n => rfl
  | cons p ps ih =>
    cases fuel with
    | zero => omega
    | succ n =>
      have ht : ps.length < n := by simp only [List.length_cons] at hf; omega
      have hne : p.code ++ ['.', '\n'] ++ propositionalDocumentChars ps ≠ [] := by
        simp
      have hdepth : p.depth < (p.code ++ ['.', '\n'] ++ propositionalDocumentChars ps).length + 1 := by
        have := propositional_depth_le_length p
        simp only [List.length_append, List.length_cons, List.length_nil]
        omega
      have hp := parseRaw_propositional E p
        ((p.code ++ ['.', '\n'] ++ propositionalDocumentChars ps).length + 1)
        [] (['.', '\n'] ++ propositionalDocumentChars ps) (by rfl) hdepth
      change parseStatements E (n + 1)
        (p.code ++ ['.', '\n'] ++ propositionalDocumentChars ps) = _
      rw [parseStatements_nonempty E n _ hne]
      simp only [List.append_assoc] at hp ⊢
      rw [hp]
      simp [consume, ih n ht]

theorem propositional_document_length (ps : List Propositional) :
    ps.length ≤ (propositionalDocumentChars ps).length := by
  induction ps with
  | nil => simp [propositionalDocumentChars]
  | cons p ps ih =>
    change ps.length + 1 ≤ (p.code ++ ['.', '\n'] ++ propositionalDocumentChars ps).length
    simp only [List.length_append, List.length_cons, List.length_nil]
    omega

/-- P4 for all nonempty atom-free propositional documents: the actual String
printer and full String parser recover exactly the original indexed AST list. -/
theorem parse_print_propositional (E : Environment) (ps : List Propositional)
    (hne : ps ≠ []) :
    parse E (print (ps.map Propositional.embed)) = some (ps.map Propositional.embed) := by
  have hp : print (ps.map Propositional.embed) = String.mk (propositionalDocumentChars ps) := by
    simp [print, statementChars, propositional_printAux, propositionalDocumentChars,
      List.flatMap_map]
  rw [hp]
  unfold parse parseWith
  change (do
    let fs ← parseStatements E ((propositionalDocumentChars ps).length + 1) (propositionalDocumentChars ps)
    if !fs.isEmpty && fs.all (fun a => a.check E []) then some fs else none) = _
  rw [parseStatements_propositional E ps _ (by have := propositional_document_length ps; omega)]
  cases ps with
  | nil => contradiction
  | cons p ps => simp [propositional_check]

/-- P5 for any accepted text whose recovered AST is a nonempty document in the
proved fragment; applying normalization to its normalized text changes nothing. -/
theorem normalize_idempotent_propositional (E : Environment) (text : String)
    (ps : List Propositional) (hne : ps ≠ [])
    (accepted : parse E text = some (ps.map Propositional.embed)) :
    (normalize E text).bind (normalize E) = normalize E text := by
  simp only [normalize, accepted, Option.map_some, Option.bind_some]
  rw [parse_print_propositional E ps hne]
  rfl

end VE.Surface
