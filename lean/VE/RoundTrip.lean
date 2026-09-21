import VE.LexicalProofs

namespace VE.Surface

/-- The active names are distinct earlier allocations; inactive sibling names
are accounted for by the counter, not left in the lexical scope. -/
def Scope (names : List String) (next : Nat) : Prop :=
  names.Nodup ∧ ∀ name ∈ names, ∃ i, i < next ∧ name = canonicalName i

theorem scope_mono {names : List String} {n m : Nat} (h : Scope names n) (hm : n ≤ m) :
    Scope names m := by
  refine ⟨h.1, ?_⟩
  intro name hn
  obtain ⟨i, hi, he⟩ := h.2 name hn
  exact ⟨i, by omega, he⟩

theorem scope_fresh {names : List String} {n : Nat} (h : Scope names n) :
    canonicalName n ∉ names := by
  intro hm
  obtain ⟨i, hi, he⟩ := h.2 _ hm
  have := canonicalName_injective _ _ he
  omega

theorem scope_cons {names : List String} {n : Nat} (h : Scope names n) :
    Scope (canonicalName n :: names) (n + 1) := by
  refine ⟨List.nodup_cons.mpr ⟨scope_fresh h, h.1⟩, ?_⟩
  intro name hm
  rcases List.mem_cons.mp hm with he | hm
  · exact ⟨n, by omega, he⟩
  · obtain ⟨i, hi, he⟩ := h.2 name hm
    exact ⟨i, by omega, he⟩

theorem canonical_binderAllowed (E : Environment) (hv : NamesValid E)
    (names : List String) (n : Nat) (hs : Scope names n) :
    binderAllowed E names (canonicalName n) = true := by
  have hg := canonicalName_generated n
  have hr := generated_not_reserved _ hg
  have hdecl : declarationName (canonicalName n) ≠ true := by
    simp [declarationName, hg]
  have hsort : canonicalName n ∉ E.sorts := fun h => hdecl (hv.1 _ h)
  have hp : E.predicates (canonicalName n) = none := by
    cases he : E.predicates (canonicalName n) with
    | none => rfl
    | some ss => exact False.elim (hdecl (hv.2.1 _ _ he))
  have hc : E.constants (canonicalName n) = none := by
    cases he : E.constants (canonicalName n) with
    | none => rfl
    | some s => exact False.elim (hdecl (hv.2.2 _ _ he))
  have hr' : canonicalName n ∉ reserved := by simpa using hr
  simp [binderAllowed, scope_fresh hs, hr', hsort, hp, hc]

theorem printAux_counter (a : Formula) (names : List String) (next : Nat) :
    next ≤ (printAux names next a).2 := by
  induction a generalizing names next <;> simp only [printAux]
  all_goals first | omega | skip
  case not a ih => exact ih _ _
  case and a b ia ib | or a b ia ib | implies a b ia ib =>
    exact Nat.le_trans (ia _ _) (ib _ _)
  case all s a ih | ex s a ih =>
    exact Nat.le_trans (by omega) (ih _ _)

theorem index_lookup (names : List String) (i : Nat) (name : String)
    (hn : names.Nodup) (hi : names[i]? = some name) :
    name ∈ names ∧ names.idxOf name = i := by
  induction names generalizing i with
  | nil => simp at hi
  | cons a names ih =>
    simp only [List.nodup_cons] at hn
    cases i with
    | zero =>
      simp only [List.getElem?_cons_zero, Option.some.injEq] at hi
      subst name
      simp
    | succ i =>
      simp only [List.getElem?_cons_succ] at hi
      obtain ⟨hm, he⟩ := ih i hn.2 hi
      have hne : a ≠ name := by intro h; subst name; exact hn.1 hm
      have hb : (a == name) = false := beq_eq_false_iff_ne.mpr hne
      simp [hm, List.idxOf_cons, hb, he]

theorem parseTerm_print (E : Environment) (hv : NamesValid E)
    (Γ names : List String) (next : Nat) (hs : Scope names next)
    (hl : names.length = Γ.length) (t : Term) (s : String)
    (ht : t.sortOf E Γ = some s) (tail : List Char) (hb : boundary tail = true) :
    parseTerm names (printTerm names t ++ tail) = some (t, tail) := by
  cases t with
  | const c =>
    have hc : identifier c = true := by
      have := hv.2.2 c s ht
      simp only [declarationName, Bool.and_eq_true] at this
      exact this.1.1
    simp only [printTerm, List.cons_append, parseTerm]
    rw [readIdent_append c tail hc hb]
    rfl
  | var i =>
    have hi : i < Γ.length := by
      apply List.getElem?_eq_some_iff.mp ht |>.1
    have hi' : i < names.length := by omega
    let name := names[i]
    have he : names[i]? = some name := List.getElem?_eq_getElem hi'
    obtain ⟨hm, hidx⟩ := index_lookup names i name hs.1 he
    obtain ⟨k, _, hk⟩ := hs.2 name hm
    have hc : identifier name = true := hk ▸ canonicalName_identifier k
    have hp := readIdent_append name tail hc hb
    have hfirst : ∃ rest, name.toList = 'x' :: rest := by
      rw [hk]
      exact ⟨_, rfl⟩
    obtain ⟨rest, hr⟩ := hfirst
    simp only [printTerm, he, Option.getD_some]
    rw [hr]
    simp only [List.cons_append, parseTerm]
    rw [hr] at hp
    simp only [List.cons_append] at hp
    rw [hp]
    simp [hm, hidx]

theorem printTerm_head (E : Environment) (Γ names : List String) (next : Nat)
    (hs : Scope names next) (hl : names.length = Γ.length) (t : Term) (s : String)
    (ht : t.sortOf E Γ = some s) :
    (∃ rest, printTerm names t = '@' :: rest) ∨
    (∃ rest, printTerm names t = 'x' :: rest) := by
  cases t with
  | const c => exact Or.inl ⟨_, rfl⟩
  | var i =>
    have hi : i < Γ.length := (List.getElem?_eq_some_iff.mp ht).1
    have hi' : i < names.length := by omega
    have he := List.getElem?_eq_getElem hi'
    obtain ⟨k, _, hk⟩ := hs.2 names[i] (List.getElem_mem hi')
    right
    simp only [printTerm, he, Option.getD_some, hk]
    exact ⟨_, rfl⟩

theorem parseRaw_term (E : Environment) (Γ names : List String) (next : Nat)
    (hs : Scope names next) (hl : names.length = Γ.length) (t : Term) (s : String)
    (ht : t.sortOf E Γ = some s) (fuel : Nat) (tail : List Char) :
    parseRaw E (fuel+1) names (printTerm names t ++ tail) =
      parseAtom names (printTerm names t ++ tail) := by
  rcases printTerm_head E Γ names next hs hl t s ht with ⟨rest, he⟩ | ⟨rest, he⟩ <;>
    rw [he] <;> rfl

theorem consume_sound (pref input rest : List Char) (h : consume pref input = some rest) :
    input = pref ++ rest := by
  induction pref generalizing input with
  | nil => simpa [consume] using h
  | cons c cs ih =>
    cases input with
    | nil => simp [consume] at h
    | cons d ds =>
      simp only [consume] at h
      split at h
      next he => subst d; simp [ih _ h]
      next => contradiction

theorem consume_keyword_ne (key p : String) (hk : identifier key = true)
    (hp : identifier p = true) (hne : p ≠ key) (tail : List Char) :
    consume ([' '] ++ key.toList ++ [' ']) ([' '] ++ p.toList ++ [' '] ++ tail) = none := by
  cases he : consume ([' '] ++ key.toList ++ [' '])
      ([' '] ++ p.toList ++ [' '] ++ tail) with
  | none => rfl
  | some rest =>
    have hi := consume_sound _ _ _ he
    simp only [List.cons_append, List.nil_append, List.append_assoc, List.cons.injEq] at hi
    have hpk := readIdent_append p (' ' :: tail) hp (by rfl)
    have hkk := readIdent_append key (' ' :: rest) hk (by rfl)
    have heq : p.toList ++ ' ' :: tail = key.toList ++ ' ' :: rest := hi.2
    rw [heq, hkk] at hpk
    have : p = key := (congrArg Prod.fst (Option.some.inj hpk)).symm
    exact False.elim (hne this)

theorem declaration_identifier (s : String) (h : declarationName s = true) : identifier s = true := by
  simp only [declarationName, Bool.and_eq_true] at h
  exact h.1.1

theorem declaration_not_reserved (s : String) (h : declarationName s = true) : s ∉ reserved := by
  simp only [declarationName, Bool.and_eq_true, Bool.not_eq_true'] at h
  simpa using h.1.2

def formulaDepth : Formula → Nat
  | .top | .bottom | .unary .. | .binary .. | .eq .. => 0
  | .not a | .all _ a | .ex _ a => formulaDepth a + 1
  | .and a b | .or a b | .implies a b => max (formulaDepth a) (formulaDepth b) + 1

theorem depth_le_print_length (a : Formula) (names : List String) (n : Nat) :
    formulaDepth a ≤ (printAux names n a).1.length := by
  induction a generalizing names n <;>
    simp only [formulaDepth, printAux, List.length_append, List.length_cons,
      List.length_nil, String.toList] at *
  all_goals first | omega | skip
  case not a ih => have := ih names n; omega
  case all s a ih | ex s a ih => have := ih (("x" ++ toString n) :: names) (n+1); omega
  case and a b ia ib | or a b ia ib | implies a b ia ib =>
    have := ia names n
    have := ib names (printAux names n a).2
    omega

/-- Full prefix round trip, including lexical boundaries, scope and sufficient
fuel. The counter is threaded by the actual canonical printer. -/
theorem parseRaw_print (E : Environment) (hv : NamesValid E) (a : Formula)
    (Γ names : List String) (n : Nat) (hs : Scope names n) (hl : names.length = Γ.length)
    (hw : a.WellFormed E Γ) (fuel : Nat) (tail : List Char)
    (hd : boundary tail = true) (hf : formulaDepth a < fuel) :
    parseRaw E fuel names ((printAux names n a).1 ++ tail) = some (a, tail) := by
  induction a generalizing Γ names n fuel tail with
  | top =>
    cases fuel with
    | zero => omega
    | succ fuel => simp [printAux, parseRaw, hd]
  | bottom =>
    cases fuel with
    | zero => omega
    | succ fuel => simp [printAux, parseRaw, hd]
  | unary p t =>
    obtain ⟨s, hp, ht⟩ := hw
    have hid := declaration_identifier p (hv.2.1 p [s] hp)
    cases fuel with
    | zero => omega
    | succ fuel =>
      simp only [printAux, List.append_assoc]
      rw [parseRaw_term E Γ names n hs hl t s ht]
      have hterm := parseTerm_print E hv Γ names n hs hl t s ht
        (" is ".toList ++ p.toList ++ tail) (by rfl)
      have hident := readIdent_append p tail hid hd
      simp only [String.toList, List.cons_append, List.nil_append] at hterm hident ⊢
      simp [parseAtom, hterm, consume, hident]
  | binary p t u =>
    obtain ⟨s, r, hp, ht, hu⟩ := hw
    have hid := declaration_identifier p (hv.2.1 p [s,r] hp)
    have hnr := declaration_not_reserved p (hv.2.1 p [s,r] hp)
    cases fuel with
    | zero => omega
    | succ fuel =>
      simp only [printAux, List.append_assoc]
      rw [parseRaw_term E Γ names n hs hl t s ht]
      have hterm := parseTerm_print E hv Γ names n hs hl t s ht
        ([' '] ++ p.toList ++ [' '] ++ printTerm names u ++ tail) (by rfl)
      have htermu := parseTerm_print E hv Γ names n hs hl u r hu tail hd
      have hident := readIdent_append p ([' '] ++ printTerm names u ++ tail) hid (by rfl)
      have heq := consume_keyword_ne "equals" p (by decide) hid
        (by intro he; subst p; exact hnr (by simp [reserved])) (printTerm names u ++ tail)
      have his := consume_keyword_ne "is" p (by decide) hid
        (by intro he; subst p; exact hnr (by simp [reserved])) (printTerm names u ++ tail)
      simp only [String.toList, List.append_assoc, List.cons_append, List.nil_append] at hterm hident heq his ⊢
      simp only [consume, ↓reduceIte] at heq his
      simp [parseAtom, hterm, consume, heq, his, hident, htermu]
  | eq t u =>
    obtain ⟨s, ht, hu⟩ := hw
    cases fuel with
    | zero => omega
    | succ fuel =>
      simp only [printAux, List.append_assoc]
      rw [parseRaw_term E Γ names n hs hl t s ht]
      have hterm := parseTerm_print E hv Γ names n hs hl t s ht
        (" equals ".toList ++ printTerm names u ++ tail) (by rfl)
      have htermu := parseTerm_print E hv Γ names n hs hl u s hu tail hd
      simp only [String.toList, List.cons_append, List.nil_append] at hterm ⊢
      simp [parseAtom, hterm, consume, htermu]
  | not a ih =>
    cases fuel with
    | zero => omega
    | succ fuel =>
      have ha : formulaDepth a < fuel := by simp only [formulaDepth] at hf; omega
      have h := ih Γ names n hs hl hw fuel (')' :: tail) (by rfl) ha
      simp [printAux, List.append_assoc, parseRaw, h, consume]
  | and a b ia ib =>
    cases fuel with
    | zero => omega
    | succ fuel =>
      have ha : formulaDepth a < fuel := by simp only [formulaDepth] at hf; omega
      have hb : formulaDepth b < fuel := by simp only [formulaDepth] at hf; omega
      have hia := ia Γ names n hs hl hw.1 fuel
        (") and (".toList ++ (printAux names (printAux names n a).2 b).1 ++ ')' :: tail) (by rfl) ha
      have hib := ib Γ names (printAux names n a).2 (scope_mono hs (printAux_counter a names n))
        hl hw.2 fuel (')' :: tail) (by rfl) hb
      simp only [String.toList, List.cons_append, List.nil_append] at hia
      simp [printAux, List.append_assoc, parseRaw, hia, hib, consume]
  | or a b ia ib =>
    cases fuel with
    | zero => omega
    | succ fuel =>
      have ha : formulaDepth a < fuel := by simp only [formulaDepth] at hf; omega
      have hb : formulaDepth b < fuel := by simp only [formulaDepth] at hf; omega
      have hia := ia Γ names n hs hl hw.1 fuel
        (") or (".toList ++ (printAux names (printAux names n a).2 b).1 ++ ')' :: tail) (by rfl) ha
      have hib := ib Γ names (printAux names n a).2 (scope_mono hs (printAux_counter a names n))
        hl hw.2 fuel (')' :: tail) (by rfl) hb
      simp only [String.toList, List.cons_append, List.nil_append] at hia
      simp [printAux, List.append_assoc, parseRaw, hia, hib, consume]
  | implies a b ia ib =>
    cases fuel with
    | zero => omega
    | succ fuel =>
      have ha : formulaDepth a < fuel := by simp only [formulaDepth] at hf; omega
      have hb : formulaDepth b < fuel := by simp only [formulaDepth] at hf; omega
      have hia := ia Γ names n hs hl hw.1 fuel
        ("), then (".toList ++ (printAux names (printAux names n a).2 b).1 ++ ')' :: tail) (by rfl) ha
      have hib := ib Γ names (printAux names n a).2 (scope_mono hs (printAux_counter a names n))
        hl hw.2 fuel (')' :: tail) (by rfl) hb
      simp only [String.toList, List.cons_append, List.nil_append] at hia
      simp [printAux, List.append_assoc, parseRaw, hia, hib, consume]
  | all s a ih =>
    cases fuel with
    | zero => omega
    | succ fuel =>
      have ha : formulaDepth a < fuel := by simp only [formulaDepth] at hf; omega
      have hia := ih (s :: Γ) (canonicalName n :: names) (n+1) (scope_cons hs)
        (by simpa using hl) hw.2 fuel (')' :: tail) (by rfl) ha
      have his := readIdent_append s
        ([' '] ++ (canonicalName n).toList ++ ", (".toList ++
          (printAux (canonicalName n :: names) (n+1) a).1 ++ ')' :: tail)
        (declaration_identifier s (hv.1 s hw.1)) (by rfl)
      have hin := readIdent_append (canonicalName n)
        (", (".toList ++ (printAux (canonicalName n :: names) (n+1) a).1 ++ ')' :: tail)
        (canonicalName_identifier n) (by rfl)
      have hb := canonical_binderAllowed E hv names n hs
      simp only [canonicalName, String.toList, String.data_append, List.append_assoc, List.cons_append, List.nil_append] at hia his hin hb
      simp [printAux, List.append_assoc, parseRaw, his, hin, hb, hia, consume]
  | ex s a ih =>
    cases fuel with
    | zero => omega
    | succ fuel =>
      have ha : formulaDepth a < fuel := by simp only [formulaDepth] at hf; omega
      have hia := ih (s :: Γ) (canonicalName n :: names) (n+1) (scope_cons hs)
        (by simpa using hl) hw.2 fuel (')' :: tail) (by rfl) ha
      have his := readIdent_append s
        ([' '] ++ (canonicalName n).toList ++ ", (".toList ++
          (printAux (canonicalName n :: names) (n+1) a).1 ++ ')' :: tail)
        (declaration_identifier s (hv.1 s hw.1)) (by rfl)
      have hin := readIdent_append (canonicalName n)
        (", (".toList ++ (printAux (canonicalName n :: names) (n+1) a).1 ++ ')' :: tail)
        (canonicalName_identifier n) (by rfl)
      have hb := canonical_binderAllowed E hv names n hs
      simp only [canonicalName, String.toList, String.data_append, List.append_assoc, List.cons_append, List.nil_append] at hia his hin hb
      simp [printAux, List.append_assoc, parseRaw, his, hin, hb, hia, consume]

theorem document_length (fs : List Formula) :
    fs.length ≤ (fs.flatMap statementChars).length := by
  induction fs with
  | nil => simp
  | cons a fs ih =>
    simp only [List.length_cons, List.flatMap_cons, List.length_append, statementChars,
      List.length_cons, List.length_nil]
    omega

theorem parseStatements_print (E : Environment) (hv : NamesValid E) (fs : List Formula)
    (hw : ∀ a ∈ fs, a.WellFormed E []) (fuel : Nat) (hf : fs.length < fuel) :
    parseStatements E fuel (fs.flatMap statementChars) = some fs := by
  induction fs generalizing fuel with
  | nil =>
    cases fuel with
    | zero => simp at hf
    | succ n => rfl
  | cons a fs ih =>
    cases fuel with
    | zero => omega
    | succ n =>
      have ht : fs.length < n := by simp only [List.length_cons] at hf; omega
      have hne : statementChars a ++ fs.flatMap statementChars ≠ [] := by
        simp [statementChars]
      have hdepth : formulaDepth a < (statementChars a ++ fs.flatMap statementChars).length + 1 := by
        have := depth_le_print_length a [] 0
        simp only [statementChars, List.length_append, List.length_cons, List.length_nil]
        omega
      have hp := parseRaw_print E hv a [] [] 0 ⟨by simp, by simp⟩ rfl
        (hw a (by simp)) ((statementChars a ++ fs.flatMap statementChars).length + 1)
        (['.', '\n'] ++ fs.flatMap statementChars) (by rfl) hdepth
      change parseStatements E (n + 1) (statementChars a ++ fs.flatMap statementChars) = _
      rw [parseStatements_nonempty E n _ hne]
      simp only [statementChars, List.append_assoc] at hp ⊢
      rw [hp]
      simp [consume, ih (fun b hb => hw b (by simp [hb])) n ht]

/-- P4 for every closed, typed, nonempty full-language document under precisely
stated declaration-name restrictions. No formula-size or binder-count cap. -/
theorem parse_print (E : Environment) (hv : NamesValid E) (d : Document E) :
    parse E (print d.formulas) = some d.formulas := by
  unfold parse print
  change (do
    let fs ← parseStatements E ((d.formulas.flatMap statementChars).length + 1)
      (d.formulas.flatMap statementChars)
    if !fs.isEmpty && fs.all (fun a => a.check E []) then some fs else none) = _
  rw [parseStatements_print E hv d.formulas d.wellFormed _
    (by have := document_length d.formulas; omega)]
  have hn : d.formulas.isEmpty = false := List.isEmpty_eq_false_iff.mpr d.nonempty
  have ht : d.formulas.all (fun a => a.check E []) = true := by
    apply List.all_eq_true.mpr
    intro a ha
    exact (check_iff_wellFormed E [] a).mpr (d.wellFormed a ha)
  change (if (!d.formulas.isEmpty && d.formulas.all (fun a => a.check E [])) = true
    then some d.formulas else none) = _
  rw [hn, ht]
  rfl

/-- Acceptance always produces a nonempty closed well-typed list, even before
assuming declaration-name validity. This is typing soundness, not ParseSpec. -/
theorem parse_wellFormed (E : Environment) (text : String) (fs : List Formula)
    (h : parse E text = some fs) : fs ≠ [] ∧ ∀ a ∈ fs, a.WellFormed E [] := by
  unfold parse at h
  cases hp : parseStatements E (text.toList.length + 1) text.toList with
  | none => simp only [hp, bind, Option.bind, reduceCtorEq] at h
  | some as =>
    simp only [hp, bind, Option.bind] at h
    split at h
    next ht =>
      have he : as = fs := Option.some.inj h
      subst as
      simp only [Bool.and_eq_true, Bool.not_eq_true', List.isEmpty_eq_false_iff,
        List.all_eq_true] at ht
      exact ⟨ht.1, fun a ha => (check_iff_wellFormed E [] a).mp (ht.2 a ha)⟩
    next => contradiction

/-- P5 on all text, using Option.bind to preserve rejection. -/
theorem normalize_idempotent (E : Environment) (hv : NamesValid E) (text : String) :
    (normalize E text).bind (normalize E) = normalize E text := by
  cases h : parse E text with
  | none => simp [normalize, h]
  | some fs =>
    obtain ⟨hne, hw⟩ := parse_wellFormed E text fs h
    have hp := parse_print E hv ⟨fs, hne, hw⟩
    simp only [normalize, h, Option.map_some, Option.bind_some]
    rw [hp]
    rfl

end VE.Surface
