import VE.Calc.Decls

/-! Fixtures for the Calc meaning and checker (me-1b): `VE.Calc.Syntax`, `VE.Calc.Eval` and
`VE.Calc.Decls`. Each `#guard` fails the build when the definition it exercises changes its answer, and
each `example` fails it when a meaning (`Denotes`, `Claim.Holds`, `Claim.Defined`, `WellFormed`, the
overflow and exhaustion causes) changes. The spec fixtures are V-1, V-2, V-4, V-9, V-10, V-11, V-13,
D-1, H-4, H-5, H-9, DL-1, DL-2 and DL-4; the English lines come with `VE.Calc.Render` (me-1c). -/

namespace VE.Calc.Examples
open VE.Calc VE.Numbers

private def empty : Values := fun _ => none
private def lit (q : Rat) : Expr := .lit q
private def eq (a b : Expr) : Claim := .compare ⟨.eq, false⟩ a b
private def lt (a b : Expr) : Claim := .compare ⟨.lt, false⟩ a b
private def round (e : Expr) (d : Int) (k : Int) : Claim :=
  .rounds .tiesUp e ⟨d, k⟩

-- V-1 and V-1n: the written places distinguish 0.296 from 0.297.
private def baseline : Expr := .div (lit 176) (lit 594)
private def baselineDecls : List Decl :=
  [{name := "approved", source := .stated 176},
   {name := "total", source := .stated 594},
   {name := "baseline", source := .defined (.div (.val "approved") (.val "total"))}]
#guard decide ((round baseline 296 3).decide empty = .holds)
#guard decide ((lt baseline (lit (3 / 10))).decide empty = .holds)
#guard decide ((round baseline 297 3).decide empty = .fails)
#guard decide ((round (.val "baseline") 296 3).run baselineDecls = .decided .holds)
#guard decide ((round (.val "baseline") 297 3).run baselineDecls = .decided .fails)

-- V-2: strict and symbol rates and the pooled percentage-point increase.
private def strictRate : Expr := .div (lit 52) (lit 243)
private def symbolsRate : Expr := .div (lit 31) (lit 243)
private def increase : Expr := .mul (lit 100) (.sub strictRate symbolsRate)
#guard decide ((round strictRate 214 3).decide empty = .holds)
#guard decide ((round symbolsRate 128 3).decide empty = .holds)
#guard decide ((round increase 86 1).decide empty = .holds)
#guard decide ((round strictRate 213 3).decide empty = .fails)
-- Subtraction keeps its operand order: the reversed difference is not the increase.
#guard decide ((round (.mul (lit 100) (.sub symbolsRate strictRate)) 86 1).decide empty = .fails)

-- V-4 and D-1.
#guard decide ((Claim.within (.div (lit 34) (lit 110)) (lit (3 / 10)) (lit (3 / 5))).decide empty = .holds)
#guard decide ((eq (.add (lit 15) (lit 2)) (lit 17)).decide empty = .holds)

-- V-9, V-10 and V-8: exact decimal arithmetic and two declared tie rules.
#guard decide ((round (lit (107 / 40)) 267 2).decide empty = .fails)
#guard decide ((Claim.rounds .halfEven (lit (107 / 40)) ⟨267, 2⟩).decide empty = .fails)
#guard decide ((round (.sub (.add (lit (1 / 10)) (lit (1 / 5))) (lit (3 / 10))) 1 16).decide empty = .fails)
#guard decide ((round (lit (4 / 512)) 7812 6).decide empty = .fails)
#guard decide ((Claim.rounds .halfEven (lit (4 / 512)) ⟨7812, 6⟩).decide empty = .holds)
#guard (Claim.rounds .tiesUp (lit (4 / 512)) ⟨7812, 6⟩).tieSensitive empty
#guard !(Claim.rounds .tiesUp (lit (669 / 250)) ⟨267, 2⟩).tieSensitive empty
-- 27/200 at two places is a tie whose upper neighbour 14 is even, so both rules give 0.14.
#guard decide ((round (lit (27 / 200)) 14 2).decide empty = .holds)
#guard decide ((Claim.rounds .halfEven (lit (27 / 200)) ⟨14, 2⟩).decide empty = .holds)
#guard (Claim.rounds .halfEven (lit (27 / 200)) ⟨14, 2⟩).tieSensitive empty
-- Only the two tie rules are tie sensitive, and only when the value is defined.
#guard !(Claim.rounds .down (lit (27 / 200)) ⟨13, 2⟩).tieSensitive empty
#guard !(Claim.rounds .tiesUp (.val "absent") ⟨14, 2⟩).tieSensitive empty
#guard !(eq (lit (27 / 200)) (lit (27 / 200))).tieSensitive empty

-- H-4, H-5 and H-5b use the source's stated squared speed ratio 10^-8.
private def sq : Expr := lit (1 / 100000000)
private def physicsDecls (path : Rat) : List Decl :=
  [{name := "path", source := .stated path},
   {name := "sq", source := .stated (1 / 100000000)}]
private def physicsDisplacement : Expr :=
  .mul (.mul (lit 2) (.val "path")) (.val "sq")
#guard decide ((eq (.mul (.mul (lit 2) (lit 20000000)) sq) (lit (2 / 5))).decide empty = .holds)
#guard decide ((eq (.mul (.mul (lit 2) (lit 2000000)) sq) (lit (1 / 25))).decide empty = .holds)
#guard decide ((eq physicsDisplacement (lit (2 / 5))).run (physicsDecls 20000000) = .decided .holds)
#guard decide ((eq physicsDisplacement (lit (1 / 25))).run (physicsDecls 2000000) = .decided .holds)

-- H-9, noon mark 16 at the start of a turn: Mean, Mean in w. l., Final mean.
private def noonMean : Expr := .div (.add (.add (lit (447 / 10)) (lit (574 / 10)))
  (lit (273 / 10))) (lit 3)
#guard decide ((round noonMean 431 1).decide empty = .holds)
#guard decide ((eq (.mul (lit (1 / 50)) (lit (431 / 10))) (lit (431 / 500))).decide empty = .holds)
#guard decide ((eq (.div (.add (lit (431 / 500)) (lit (353 / 500))) (lit 2))
  (lit (98 / 125))).decide empty = .holds)
#guard decide ((round (.div (.add (.add (lit 44) (lit (573 / 10)))
  (lit (235 / 10))) (lit 3)) 419 1).decide empty = .fails)

-- DL-1, DL-2 and DL-4: bounds, rounded speed ratios and ablation comparison.
#guard decide ((Claim.within (lit (24 / 25)) (lit (17 / 20)) (lit (29 / 25))).decide empty = .holds)
#guard decide ((lt (lit (24 / 25)) (lit (14 / 5))).decide empty = .holds)
#guard decide ((Claim.within (lit (14 / 5)) (lit (27 / 10)) (lit 4)).decide empty = .holds)
#guard decide ((Claim.within (lit (3 / 2)) (lit (6 / 5)) (lit (8 / 5))).decide empty = .holds)
#guard decide ((Claim.within (lit (7 / 2)) (lit (31 / 10)) (lit (21 / 5))).decide empty = .holds)
#guard decide ((lt (lit (3 / 2)) (lit (7 / 2))).decide empty = .holds)
#guard decide ((round (.div (lit (48 / 10)) (lit (6 / 10))) 8 0).decide empty = .holds)
#guard decide ((round (.div (lit (92 / 10)) (lit (11 / 10))) 8 0).decide empty = .holds)
#guard decide ((round (.div (lit 18) (lit (21 / 10))) 8 0).decide empty = .fails)
#guard decide ((lt (.add (lit (2 / 5)) (lit (7 / 10))) (lit (61 / 10))).decide empty = .holds)
-- `within` is inclusive at both ends and fails just outside them.
#guard decide ((Claim.within (lit (17 / 20)) (lit (17 / 20)) (lit (29 / 25))).decide empty = .holds)
#guard decide ((Claim.within (lit (29 / 25)) (lit (17 / 20)) (lit (29 / 25))).decide empty = .holds)
#guard decide ((Claim.within (lit (21 / 25)) (lit (17 / 20)) (lit (29 / 25))).decide empty = .fails)
#guard decide ((Claim.within (lit (117 / 100)) (lit (17 / 20)) (lit (29 / 25))).decide empty = .fails)

-- An undefined operand (an unknown name, a zero divisor) makes every claim form undefined.
#guard decide ((eq (.val "absent") (lit 1)).decide empty = .undefined)
#guard decide ((eq (lit 1) (.div (lit 1) (lit 0))).decide empty = .undefined)
#guard decide ((Claim.within (lit 1) (lit 0) (.val "absent")).decide empty = .undefined)
#guard decide ((round (.pow (.div (lit 2) (.sub (lit 1) (lit 1))) 2) 0 0).decide empty = .undefined)
#guard Expr.eval empty (.pow (lit (1 / 2)) 3) = some (1 / 8)
#guard Expr.eval empty (.div (lit 0) (lit 5)) = some 0

-- V-11: intermediate digit exhaustion precedes the final mathematical verdict.
private def largeDecls : List Decl :=
  [{name := "x", source := .stated ((10 : Rat) ^ 39)},
   {name := "y", source := .defined (.pow (.val "x") 64)},
   {name := "z", source := .defined (.mul (.val "y") (.val "y"))}]
#guard decide ((Claim.compare ⟨.lt, false⟩ (.val "z") (lit 1)).run largeDecls =
  .unknown (.limit .digits))
#guard decide ((eq (.div (lit 1) (.sub (.val "x") (.val "x"))) (lit 1)).run largeDecls =
  .decided .undefined)
#guard decide ((lt (.val "y") (lit 1)).run largeDecls = .decided .fails)
-- The first faulty expression, in the claim's order, names the outcome.
#guard decide ((eq (.div (lit 1) (lit 0)) (.val "z")).run largeDecls = .decided .undefined)
#guard decide ((eq (.val "z") (.div (lit 1) (lit 0))).run largeDecls = .unknown (.limit .digits))

/-! The digit limit: `maxDigits` digits in numerator and denominator are allowed, one more is not
(limit − 1, limit and limit + 1). -/

#guard maxDigits = 4096
-- The unknown's text (`VE.Numbers.UnknownReason.text`, spec 1.5) names this limit.
#guard let s := toString maxDigits
  UnknownReason.text 0 (.limit .digits) =
    s!"unknown: an exact value would have more than {s.take (s.length - 3)},{s.drop (s.length - 3)} digits"
#guard digitCount (10 ^ 4095) = 4096
#guard Small ((10 : Rat) ^ 4095)
#guard Small ((10 : Rat) ^ 4095 * 9)
#guard ¬ Small ((10 : Rat) ^ 4096)
#guard Small (1 / (10 : Rat) ^ 4095)
#guard ¬ Small (1 / (10 : Rat) ^ 4096)
#guard ¬ Small (-(10 : Rat) ^ 4096)
#guard Val.guard ((10 : Rat) ^ 4095) = .ok ((10 : Rat) ^ 4095)
#guard Val.guard ((10 : Rat) ^ 4096) = .tooLarge
#guard decide ((eq (lit ((10 : Rat) ^ 4095)) (lit 1)).run [] = .decided .fails)
#guard decide ((eq (lit ((10 : Rat) ^ 4096)) (lit 1)).run [] = .unknown (.limit .digits))
#guard decide ((eq (.mul (lit ((10 : Rat) ^ 4000)) (lit ((10 : Rat) ^ 96))) (lit 1)).run [] =
  .unknown (.limit .digits))
#guard decide ((eq (.mul (lit ((10 : Rat) ^ 4000)) (lit ((10 : Rat) ^ 95))) (lit 1)).run [] =
  .decided .fails)

/-! Each source of a declared value, on both paths: `values` (the meaning) and `Claim.run` (the checker). -/

private def seven : Thunk (Option Rat) := Thunk.pure (some 7)
private def none' : Thunk (Option Rat) := Thunk.pure none
private def sources : List Decl :=
  [{name := "s", source := .stated 3},
   {name := "f", source := .free},
   {name := "c", source := .counted seven (.ok (some 7))},
   {name := "u", source := .counted none' (.ok none)},
   {name := "e", source := .counted none' .exhausted},
   {name := "d", source := .defined (.add (.val "s") (.val "c"))},
   {name := "g", source := .defined (.mul (.val "e") (lit 2))}]
#guard values sources "s" = some 3
#guard values sources "f" = none
#guard values sources "c" = some 7
#guard values sources "u" = none
#guard values sources "d" = some 10
#guard values sources "absent" = none
#guard Decl.valueUnder {name := "c", source := .counted seven .exhausted} empty = some 7
#guard Decl.valueUnder {name := "d", source := .defined (.val "s")} (values sources) = some 3
-- A later declaration of a name is the one `values` reads.
#guard values [{name := "s", source := .stated 3}, {name := "s", source := .stated 4}] "s" = some 4
#guard decide ((eq (.val "d") (lit 10)).run sources = .decided .holds)
#guard decide ((eq (.val "c") (lit 7)).run sources = .decided .holds)
#guard decide ((eq (.val "f") (lit 0)).run sources = .decided .undefined)
#guard decide ((eq (.val "u") (lit 0)).run sources = .decided .undefined)
#guard decide ((eq (.val "absent") (lit 0)).run sources = .decided .undefined)
#guard decide ((eq (.val "e") (lit 0)).run sources = .unknown (.limit .evaluations))
#guard decide ((eq (.val "g") (lit 0)).run sources = .unknown (.limit .evaluations))
#guard decide ((eq (.val "f") (.val "e")).run sources = .decided .undefined)
#guard decide ((eq (.val "e") (.val "f")).run sources = .unknown (.limit .evaluations))

-- V-13: finding kinds.
#guard findingKind none [true, true] = .source
#guard findingKind none [true, false] = .transcriptionUnchecked
#guard findingKind none [] = .transcriptionUnchecked
#guard findingKind (some "R 4.3") [true] = .softwareUnreproduced

/-! The meanings, stated directly from their constructors (not through the evaluator). -/

example : Denotes empty (.sub (.lit 5) (.lit 3)) (5 - 3) := .sub .lit .lit
example : Denotes empty (.div (.lit 3) (.lit 4)) (3 / 4) := .div .lit .lit (by decide +kernel)
example : Denotes empty (.pow (.lit 2) 3) (2 ^ 3) := .pow .lit
example (q : Rat) : ¬ Denotes empty (.div (.lit 1) (.lit 0)) q := by
  intro h
  cases h with
  | div _ hb hne => cases hb; exact hne rfl
example (q : Rat) : ¬ Denotes empty (.val "absent") q := by
  intro h
  cases h with
  | val hv => cases hv

example : (eq (.add (.lit 15) (.lit 2)) (.lit 17)).Holds empty :=
  ⟨15 + 2, 17, .add .lit .lit, .lit, by decide +kernel⟩
example : (Claim.within (.lit 1) (.lit 1) (.lit 1)).Holds empty :=
  ⟨1, 1, 1, .lit, .lit, .lit, by decide +kernel, by decide +kernel⟩
example : ¬ (Claim.within (.lit 2) (.lit 0) (.lit 1)).Holds empty := by
  rintro ⟨x, l, h, hx, hl, hh, _, hle⟩
  cases hx; cases hh
  revert hle; decide +kernel
example : (round (.lit (27 / 200)) 14 2).Holds empty :=
  ⟨27 / 200, .lit, by decide +kernel⟩
example : ¬ (lt (.lit 2) (.lit 1)).Holds empty := by
  rintro ⟨x, y, hx, hy, h⟩
  cases hx; cases hy
  revert h; decide +kernel
example : (eq (.lit 1) (.lit 2)).Defined empty := by
  intro e he
  simp only [eq, Claim.exprs, List.mem_cons, List.mem_nil_iff, or_false] at he
  rcases he with rfl | rfl
  · exact ⟨1, .lit⟩
  · exact ⟨2, .lit⟩
example : ¬ (eq (.div (.lit 1) (.lit 0)) (.lit 1)).Defined empty := by
  intro h
  obtain ⟨q, hq⟩ := h (.div (.lit 1) (.lit 0)) (by simp [eq, Claim.exprs])
  cases hq with
  | div _ hb hne => cases hb; exact hne rfl

/-! `WellFormed`: distinct names, a defined value reads only earlier names, and a counted value's
thunk is its recorded value. -/

example : WellFormed baselineDecls := by
  refine ⟨by decide, ?_, ?_⟩
  · intro i hi e he n hn
    match i, hi with
    | 0, _ => simp [baselineDecls] at he
    | 1, _ => simp [baselineDecls] at he
    | 2, _ =>
      simp only [baselineDecls, List.getElem_cons_succ, List.getElem_cons_zero, Source.defined.injEq]
        at he
      subst he
      simp only [Expr.names, List.mem_append, List.mem_singleton] at hn
      rcases hn with rfl | rfl <;> decide
  · intro d hd q v hs
    simp only [baselineDecls, List.mem_cons, List.mem_nil_iff, or_false] at hd
    rcases hd with rfl | rfl | rfl <;> cases hs
example : ¬ WellFormed [{name := "a", source := .stated 1}, {name := "a", source := .stated 2}] :=
  fun h => absurd h.1 (by decide)
example : ¬ WellFormed
    [{name := "a", source := .defined (.val "b")}, {name := "b", source := .stated 1}] := by
  intro h
  have := h.2.1 0 (by decide) (.val "b") rfl "b" (by simp [Expr.names])
  simp at this
example : ¬ WellFormed [{name := "c", source := .counted seven (.ok (some 8))}] := by
  intro h
  have := h.2.2 {name := "c", source := .counted seven (.ok (some 8))} (by simp) seven (some 8) rfl
  revert this; decide +kernel

/-! The causes of an unknown: a value over the digit limit (`Overflows`, `NameOverflows`) and a
counted value whose evaluation budget ran out (`ReadsExhausted`, `NameExhausted`). -/

private def bigDecl : Decl := {name := "b", source := .defined (.pow (.lit 10) 4096)}
private def readsBig : Decl := {name := "r", source := .defined (.add (.val "b") (.lit 1))}
private def big : List Decl := [bigDecl, readsBig]
example : (eq (.val "b") (.lit 1)).Overflows big :=
  ⟨.val "b", by simp [eq, Claim.exprs], Or.inr ⟨"b", by simp [Expr.names],
    .here ⟨bigDecl, by simp [big], rfl, rfl⟩
      ⟨.pow (.lit 10) 4096, by simp [Expr.subexprs], (10 : Rat) ^ 4096, .pow .lit,
        by decide +kernel⟩⟩⟩
example : (eq (.val "r") (.lit 1)).Overflows big :=
  ⟨.val "r", by simp [eq, Claim.exprs], Or.inr ⟨"r", by simp [Expr.names],
    .dep (m := "b") ⟨readsBig, by simp [big], rfl, rfl⟩ (by simp [Expr.names])
      (.here ⟨bigDecl, by simp [big], rfl, rfl⟩
        ⟨.pow (.lit 10) 4096, by simp [Expr.subexprs], (10 : Rat) ^ 4096, .pow .lit,
        by decide +kernel⟩)⟩⟩
example : (eq (.lit ((10 : Rat) ^ 4096)) (.lit 1)).Overflows [] :=
  ⟨.lit ((10 : Rat) ^ 4096), by simp [eq, Claim.exprs],
    Or.inl ⟨.lit ((10 : Rat) ^ 4096), by simp [Expr.subexprs], (10 : Rat) ^ 4096, .lit,
      by decide +kernel⟩⟩
example : ¬ (eq (.lit 1) (.lit 2)).Overflows [] := by
  rintro ⟨e, he, hsub | ⟨m, hm, _⟩⟩
  · simp only [eq, Claim.exprs, List.mem_cons, List.mem_nil_iff, or_false] at he
    obtain ⟨e', he', q, hq, hs⟩ := hsub
    rcases he with rfl | rfl <;>
      simp only [Expr.subexprs, List.mem_singleton] at he' <;> subst he' <;> cases hq <;>
      exact hs (by decide +kernel)
  · simp only [eq, Claim.exprs, List.mem_cons, List.mem_nil_iff, or_false] at he
    rcases he with rfl | rfl <;> simp [Expr.names] at hm
example : (eq (.val "g") (.lit 1)).ReadsExhausted sources :=
  ⟨.val "g", by simp [eq, Claim.exprs], "g", by simp [Expr.names],
    .dep ⟨{name := "g", source := .defined (.mul (.val "e") (lit 2))}, by simp [sources], rfl, rfl⟩
      (by simp [Expr.names])
      (.here ⟨{name := "e", source := .counted none' .exhausted}, by simp [sources], rfl, rfl⟩)⟩
example : ¬ (eq (.lit 1) (.val "s")).ReadsExhausted sources := by
  rintro ⟨e, he, m, hm, hx⟩
  simp only [eq, Claim.exprs, List.mem_cons, List.mem_nil_iff, or_false] at he
  rcases he with rfl | rfl
  · simp [Expr.names] at hm
  · simp only [Expr.names, List.mem_singleton] at hm
    subst hm
    cases hx with
    | here hd => simp [sources] at hd
    | dep hd _ _ => simp [sources] at hd

end VE.Calc.Examples
