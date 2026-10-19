import VE.Calc.FourierMotzkin

/-! Derivations over rational unknowns at the level of facts (spec 5): a derivation is a replayed list of Farkas
refutations and square-rule steps; a counterexample is checked by evaluation, square links included. -/

namespace VE.Calc

/-- A step derives `goal` by a Farkas refutation of the facts so far and `goal.negate`, or derives `0 < b − r` from an
established `0 < a − s`, a link `(s, r)`, `a ≤ b * b` and `0 < b`. -/
inductive Step where
  | farkas (goal : QFact) (cert : Farkas)
  | square (s r : String) (a b : Rat)
  deriving Repr, DecidableEq

structure Derivation where
  steps : List Step
  deriving Repr, DecidableEq

/-- The fact a step derives from the facts so far, if it is valid. -/
def Step.derive (links : List (String × String)) (known : List QFact) : Step → Option QFact
  | .farkas goal cert => if cert.check (known ++ [goal.negate]) then some goal else none
  | .square s r a b =>
      if (s, r) ∈ links ∧ 0 < b ∧ a ≤ b * b ∧ (⟨⟨a, [(s, -1)]⟩, true⟩ : QFact) ∈ known
      then some ⟨⟨b, [(r, -1)]⟩, true⟩ else none

/-- The facts the steps derive, in order. -/
def Derivation.replay (links : List (String × String)) : List QFact → List Step → Option (List QFact)
  | _, [] => some []
  | known, st :: rest => do
      let f ← st.derive links known
      let fs ← Derivation.replay links (known ++ [f]) rest
      pure (f :: fs)

/-- Replays the steps in order; the conclusion must be the last derived fact. -/
def Derivation.check (P : List QFact) (links : List (String × String)) (C : QFact) (d : Derivation) : Bool :=
  match Derivation.replay links P d.steps with
  | some fs => fs.getLast? == some C
  | none => false

theorem Step.derive_sound (links : List (String × String)) (known : List QFact) (st : Step) (f : QFact)
    (h : st.derive links known = some f) (κ : String → Rat) (hk : ∀ g ∈ known, g.Holds κ)
    (hl : ∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) : f.Holds κ := by
  cases st with
  | farkas goal cert =>
      simp only [Step.derive] at h
      split at h
      · rename_i hc
        cases h
        apply Classical.byContradiction
        intro hn
        exact Farkas.check_sound _ cert hc κ (by
          intro g hg
          rcases List.mem_append.mp hg with hg | hg
          · exact hk g hg
          · simp only [List.mem_singleton] at hg; subst hg; exact (QFact.negate_holds κ f).mpr hn)
      · cases h
  | square s r a b =>
      simp only [Step.derive] at h
      split at h
      · rename_i hc
        obtain ⟨hlink, hb, hab, hmem⟩ := hc
        cases h
        have hs := hk _ hmem
        obtain ⟨hsq, hr⟩ := hl _ hlink
        simp only [QFact.Holds, QLin.eval, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil] at hs hsq ⊢
        have := lt_of_sq_lt (κ r) a b hr hb (by grind) hab
        grind
      · cases h

theorem Derivation.replay_sound (links : List (String × String)) (steps : List Step) :
    ∀ (known fs : List QFact), Derivation.replay links known steps = some fs → ∀ κ : String → Rat,
      (∀ g ∈ known, g.Holds κ) → (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) → ∀ f ∈ fs, f.Holds κ := by
  induction steps with
  | nil => intro known fs h; simp [Derivation.replay] at h; subst h; simp
  | cons st rest ih =>
      intro known fs h κ hk hl
      simp only [Derivation.replay, Option.bind_eq_bind, Option.bind_eq_some_iff, Option.pure_def,
        Option.some.injEq] at h
      obtain ⟨f, hf, fs', hfs', rfl⟩ := h
      have hfh := Step.derive_sound links known st f hf κ hk hl
      intro g hg
      rcases List.mem_cons.mp hg with rfl | hg
      · exact hfh
      · exact ih _ fs' hfs' κ (by
          intro g' hg'
          rcases List.mem_append.mp hg' with hg' | hg'
          · exact hk g' hg'
          · simp only [List.mem_singleton] at hg'; subst hg'; exact hfh) hl g hg

/-- A derivation is accepted only if each step is a checked Farkas refutation of (premises and the negated step) or
one square-rule step; then the conclusion holds wherever the premises and square links hold. -/
theorem Derivation.check_sound (P : List QFact) (links : List (String × String)) (C : QFact) (d : Derivation)
    (h : d.check P links C = true) :
    ∀ κ : String → Rat, (∀ f ∈ P, f.Holds κ) →
      (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) → C.Holds κ := by
  intro κ hP hl
  unfold Derivation.check at h
  split at h
  · rename_i fs hfs
    have hlast : fs.getLast? = some C := by simpa using h
    exact Derivation.replay_sound links d.steps P fs hfs κ hP hl C (List.mem_of_getLast? hlast)
  · cases h

def counterexampleCheck (P : List QFact) (links : List (String × String)) (C : QFact)
    (κ : String → Rat) : Bool :=
  P.all (fun f => decide (f.Holds κ)) &&
    links.all (fun l => κ l.1 == κ l.2 * κ l.2 && decide (0 ≤ κ l.2)) && !decide (C.Holds κ)

/-- Debate A2: a counterexample satisfies every square link and its nonnegativity condition. -/
theorem Counterexample.check_sound (P : List QFact) (links : List (String × String)) (C : QFact)
    (κ : String → Rat) (h : counterexampleCheck P links C κ = true) :
    (∀ f ∈ P, f.Holds κ) ∧ (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) ∧ ¬ C.Holds κ := by
  simp only [counterexampleCheck, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq, beq_iff_eq,
    Bool.not_eq_true', decide_eq_false_iff_not] at h
  exact ⟨h.1.1, h.1.2, h.2⟩

/-- What the fact-level search answers; untrusted until replayed (`Derivation.check`) or checked by evaluation. -/
inductive Answer where
  | follows (d : Derivation)
  | counterexample (κ : List (String × Rat))
  | unknown (u : VE.Numbers.UnknownReason)
  deriving Repr, DecidableEq

def Answer.point (κ : List (String × Rat)) (n : String) : Rat := (κ.lookup n).getD 0

/-- A Farkas step for `goal` from `known`, found by the search. -/
def farkasStep (known : List QFact) (goal : QFact) : FM.Search (Option Step) := do
  match ← FM.search (known ++ [goal.negate]) with
  | .refuted ws => pure (some (.farkas goal ⟨ws⟩))
  | .point _ => pure none

/-- Across a square link `(s, r)` with the conclusion an upper bound `r < b` or `r ≤ b`: the least upper bound `a` on
`s`, one square step, and a last Farkas step when the conclusion is not literally `0 < b − r`. -/
def squareSteps (P : List QFact) (links : List (String × String)) (C : QFact) : FM.Search (Option (List Step)) := do
  let [(r, c)] := C.form.norm.coeffs | return none
  let b := C.form.const / -c
  let some (s, _) := links.find? (·.2 == r) | return none
  unless decide (c < 0) && decide (0 < b) do return none
  let some (a, strict) ← FM.upperBound P s | return none
  let some a := if strict && decide (a ≤ b * b) then some a else if decide (a < b * b) then some (b * b) else none
    | return none
  let g : QFact := ⟨⟨a, [(s, -1)]⟩, true⟩
  let some first ← farkasStep P g | return none
  let derived : QFact := ⟨⟨b, [(r, -1)]⟩, true⟩
  if derived = C then return some [first, .square s r a b]
  let some last ← farkasStep (P ++ [g, derived]) C | return none
  return some [first, .square s r a b, last]

/-- Across a square link: the claimed bound itself, `r = b` and `s = b²`, the other unknowns found by the search. -/
def boundCandidate (P : List QFact) (links : List (String × String)) (C : QFact) :
    FM.Search (Option (List (String × Rat))) := do
  let [(r, c)] := C.form.norm.coeffs | return none
  let b := C.form.const / -c
  let some (s, _) := links.find? (·.2 == r) | return none
  let fixed : List (String × Rat) := [(r, b), (s, b * b)]
  let subst := fun (f : QFact) => QFact.mk ⟨f.form.eval fun n => if n ∈ [r, s] then (fixed.lookup n).getD 0 else 0,
    f.form.coeffs.filter (·.1 ∉ [r, s])⟩ f.strict
  match ← FM.search (P.map subst) with
  | .point κ => return some (fixed ++ κ)
  | .refuted _ => return none

/-- The search, in the order of spec 5: a linear refutation; else a counterexample, the claimed bound across a square
link tried first, then the linear point; else the square rule. Every search it runs draws on one budget. -/
def Derive.answer (P : List QFact) (links : List (String × String)) (C : QFact) : FM.Search Answer := do
  match ← FM.search (P ++ [C.negate]) with
  | .refuted ws => return .follows ⟨[.farkas C ⟨ws⟩]⟩
  | .point κ =>
    match ((← boundCandidate P links C).toList ++ [κ]).find? (counterexampleCheck P links C ∘ Answer.point) with
    | some κ => return .counterexample κ
    | none => match ← squareSteps P links C with
      | some st => return .follows ⟨st⟩
      | none => return .unknown .derivationInconclusive

/-- `Derive.answer` within `budget` combinations for the whole derivation, on an input within 64 facts and 16
unknowns: past any of these limits, wherever the search stops, the answer is `limit .derivationSteps` (spec 5). -/
def Derive.searchWithin (budget : Nat) (P : List QFact) (links : List (String × String)) (C : QFact) : Answer :=
  if !FM.admits (P ++ [C.negate]) (links.flatMap fun l => [l.1, l.2]) then .unknown (.limit .derivationSteps) else
  match (Derive.answer P links C).run' budget with
  | .ok a => a
  | .error _ => .unknown (.limit .derivationSteps)

def Derive.search (P : List QFact) (links : List (String × String)) (C : QFact) : Answer :=
  Derive.searchWithin FM.maxSteps P links C

end VE.Calc
