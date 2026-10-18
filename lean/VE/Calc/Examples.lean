import VE.Calc.Render

/-! Fixtures for the Calc meaning and checker (me-1b): `VE.Calc.Syntax`, `VE.Calc.Eval` and
`VE.Calc.Decls`, and for its English lines (me-1c): `VE.Calc.Render`. Each `#guard` fails the build when
the definition it exercises changes its answer, and each `example` fails it when a meaning (`Denotes`,
`Claim.Holds`, `Claim.Defined`, `WellFormed`, the overflow and exhaustion causes) changes. The spec
fixtures are V-1, V-2, V-4, V-9, V-10, V-11, V-13, D-1, H-4, H-5, H-9, DL-1, DL-2 and DL-4. -/

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
#guard Small (-(10 : Rat) ^ 4095)
#guard ¬ Small (-(10 : Rat) ^ 4096)
-- A negative value is within the limit, so its claim is decided (me-1b review F1).
#guard decide ((eq (lit (-1)) (lit 0)).run [] = .decided .fails)
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
-- A counted value whose count finished is not exhausted (me-1b review F2).
example : ¬ (eq (.val "c") (.lit 0)).ReadsExhausted sources := by
  rintro ⟨e, he, m, hm, hx⟩
  simp only [eq, Claim.exprs, List.mem_cons, List.mem_nil_iff, or_false] at he
  rcases he with rfl | rfl
  · simp only [Expr.names, List.mem_singleton] at hm
    subst hm
    cases hx with
    | here hd => simp [sources] at hd
    | dep hd _ _ => simp [sources] at hd
  · simp [Expr.names] at hm

/-! The English lines (spec 9 and 11.2, `VE.Calc.English.renderClaim`): display only. -/

private def words (n : String) : Option String :=
  if n = "baseline" then some "the baseline" else none

#guard VE.Calc.English.renderClaim words (.rounds .tiesUp (.val "baseline") ⟨296, 3⟩) =
  some "The baseline is 0.296 when rounded to three decimal places, with exact ties going up."
#guard VE.Calc.English.renderClaim words (.rounds .halfEven (.val "baseline") ⟨296, 3⟩) =
  some "The baseline is 0.296 when rounded to three decimal places, with exact ties going to the even digit."

/-! Rendering follows 11.2 (ME-1 review F1): an infix phrase stands only at the top, with an atom on
its left; anything else is `none`. -/

private def letters (n : String) : Option String :=
  if n = "a" ∨ n = "b" ∨ n = "c" then some ("the " ++ n)
  else if n = "minus" then some "the a minus the b"
  else if n = "phrase" then some "the sum of the a and the b"
  else if n = "spaced" then some "the  a"
  else if n = "slot" then some "the {1} rate"
  else none

private def line (e : Expr) : Option String :=
  VE.Calc.English.renderClaim letters (eq e (lit 1))

#guard (line (.sub (.val "a") (.sub (.val "b") (.val "c")))).isNone
#guard (line (.div (.val "a") (.div (.val "b") (.val "c")))).isNone
#guard (line (.sub (.val "a") (.div (.val "b") (.val "c")))).isNone
#guard (line (.pow (.sub (.val "a") (.val "b")) 2)).isNone
#guard (line (.pow (.div (.val "a") (.val "b")) 3)).isNone
#guard (line (.pow (.add (.val "a") (.val "b")) 4)).isNone
#guard (line (.add (.sub (.val "a") (.val "b")) (.val "c"))).isNone
#guard (line (.add (.val "c") (.div (.val "a") (.val "b")))).isNone
#guard (line (.mul (.div (.val "a") (.val "b")) (.val "c"))).isNone
#guard (line (.mul (.val "c") (.pow (.val "a") 4))).isNone
#guard (line (.sub (.add (.val "a") (.val "b")) (.val "c"))).isNone
#guard (line (.div (.pow (.val "a") 2) (.val "c"))).isNone
#guard (line (.sub (.val "a") (.add (.val "b") (.mul (.val "c") (.val "a"))))).isNone
#guard line (.sub (.val "a") (.add (.val "b") (.val "c"))) =
  some "The a minus the sum of the b and the c equals 1."
#guard line (.div (lit 1) (lit 4)) = some "1 divided by 4 equals 1."
#guard line (.pow (.add (.val "a") (.val "b")) 2) = some "The square of the sum of the a and the b equals 1."
#guard line (.pow (.val "a") 4) = some "The a to the power 4 equals 1."
-- A negative number, value words that read as a phrase, and a template slot in value words.
#guard (line (lit (-1))).isNone
#guard (VE.Calc.English.renderClaim letters (.rounds .down (.val "a") ⟨-5, 1⟩)).isNone
#guard (line (.val "minus")).isNone
#guard (line (.val "phrase")).isNone
#guard (line (.val "spaced")).isNone
#guard VE.Calc.English.renderClaim letters (eq (.val "slot") (.val "a")) =
  some "The {1} rate equals the a."
#guard VE.Calc.English.renderClaim letters (.within (.val "a") (.val "slot") (.val "b")) =
  some "The a is from the {1} rate through the b."

/-! The same for every expression to depth 3 over a few atoms: a line is written exactly when 11.2
accepts the expression, and a reader of 11.2's grammar, which returns every parse, reads it back as
that expression and nothing else. -/

private def numerals : List (String × Rat) := [("1", 1), ("0.5", 1 / 2)]

private def readAtom : List String → List (Expr × List String)
  | "the" :: n :: rest => if n = "a" ∨ n = "b" then [(.val n, rest)] else []
  | t :: rest => (numerals.filter (·.1 = t)).map fun row => (lit row.2, rest)
  | [] => []

private def readTerm : Nat → List String → List (Expr × List String)
  | 0, _ => []
  | fuel + 1, ts =>
    let two (mk : Expr → Expr → Expr) (rest : List String) :=
      (readTerm fuel rest).flatMap fun (a, r) => match r with
        | "and" :: r' => (readTerm fuel r').map fun (b, r'') => (mk a b, r'')
        | _ => []
    let one (k : Nat) (rest : List String) :=
      (readTerm fuel rest).map fun (a, r) => (.pow a k, r)
    readAtom ts ++ match ts with
      | "the" :: "sum" :: "of" :: rest => two .add rest
      | "the" :: "product" :: "of" :: rest => two .mul rest
      | "the" :: "square" :: "of" :: rest => one 2 rest
      | "the" :: "cube" :: "of" :: rest => one 3 rest
      | _ => []

private def readExpr (ts : List String) : List Expr :=
  let whole (l : List (Expr × List String)) := l.filterMap fun (e, r) => if r.isEmpty then some e else none
  let atTop (mk : Expr → Expr → Expr) (a : Expr) (r : List String) :=
    whole ((readTerm (r.length + 1) r).map fun (b, r') => (mk a b, r'))
  whole (readTerm (ts.length + 1) ts) ++ (readAtom ts).flatMap fun (a, r) => match r with
    | "minus" :: r' => atTop .sub a r'
    | "divided" :: "by" :: r' => atTop .div a r'
    | ["to", "the", "power", k] => (k.toNat?.map fun k => Expr.pow a k).toList
    | _ => []

private def readLine (s : String) : List Expr :=
  match ((s.dropRight 1).decapitalize.splitOn " ").reverse with
  | "1" :: "equals" :: ts => readExpr ts.reverse
  | _ => []

private def okAtom : Expr → Bool
  | .lit q => 0 ≤ q
  | .val n => n = "a" ∨ n = "b"
  | _ => false

private def okTerm : Expr → Bool
  | .add a b | .mul a b => okTerm a && okTerm b
  | .pow a k => (k = 2 ∨ k = 3) && okTerm a
  | e => okAtom e

private def depth : Expr → Nat
  | .lit _ | .val _ => 0
  | .add a b | .sub a b | .mul a b | .div a b => 1 + max (depth a) (depth b)
  | .pow a _ => 1 + depth a

private def okExpr (e : Expr) : Bool :=
  depth e ≤ 2 && match e with
    | .sub a b | .div a b => okAtom a && okTerm b
    | .pow a k => if k = 2 ∨ k = 3 then okTerm a else okAtom a
    | _ => okTerm e

private def grow (es : List Expr) : List Expr :=
  es.flatMap fun a => [.pow a 2, .pow a 3, .pow a 4] ++
    es.flatMap fun b => [.add a b, .sub a b, .mul a b, .div a b]

private def atoms : List Expr := [.val "a", lit (1 / 2), lit (-1), .val "minus"]
private def upTo2 : List Expr := atoms ++ grow atoms ++ (grow (atoms ++ grow atoms)).filter (depth · = 2)
private def depth3 : List Expr :=
  upTo2.flatMap fun e => [.pow e 2, .sub (.val "a") e, .add e (lit 1)]

private def readsBack (e : Expr) : Bool :=
  match line e with
  | some s => okExpr e && readLine s == [e]
  | none => !okExpr e

#guard (upTo2 ++ depth3).all readsBack
#guard (upTo2.filter okExpr).length = 480

/-! Every other part of a line (me-1c): the comparison phrases, the four rounding rules, the places
wording, printed numbers and numerals, and 11.2's form of value words. -/

#guard VE.Calc.English.renderClaim letters (lt (.val "a") (.val "b")) = some "The a is less than the b."
#guard VE.Calc.English.renderClaim letters (.compare ⟨.le, false⟩ (.val "a") (.val "b")) =
  some "The a is at most the b."
#guard VE.Calc.English.renderClaim letters (.compare ⟨.lt, true⟩ (.val "a") (.val "b")) =
  some "The a is more than the b."
#guard VE.Calc.English.renderClaim letters (.compare ⟨.le, true⟩ (.val "a") (.val "b")) =
  some "The a is at least the b."
-- A comparison with no phrase has no line.
#guard (VE.Calc.English.renderClaim letters (.compare ⟨.eq, true⟩ (.val "a") (.val "b"))).isNone
#guard VE.Calc.English.renderClaim letters (.rounds .down (.val "a") ⟨29, 2⟩) =
  some "The a is 0.29 when rounded down to two decimal places."
#guard VE.Calc.English.renderClaim letters (.rounds .up (.val "a") ⟨3, 1⟩) =
  some "The a is 0.3 when rounded up to one decimal place."
#guard VE.Calc.English.renderClaim letters (.rounds .tiesUp (.val "a") ⟨12, 0⟩) =
  some "The a is 12 when rounded to a whole number, with exact ties going up."
#guard VE.Calc.English.renderClaim letters (.rounds .down (.val "a") ⟨3, -2⟩) =
  some "The a is 3 times ten to the power 2 when rounded down to a multiple of ten to the power 2."
-- The places in words: one through twenty, then numerals.
#guard ((List.range 21).map fun k =>
    VE.Calc.English.renderClaim letters (.rounds .down (.val "a") ⟨0, (k + 1 : Nat)⟩)) =
  ["one decimal place", "two decimal places", "three decimal places", "four decimal places",
   "five decimal places", "six decimal places", "seven decimal places", "eight decimal places",
   "nine decimal places", "ten decimal places", "eleven decimal places", "twelve decimal places",
   "thirteen decimal places", "fourteen decimal places", "fifteen decimal places",
   "sixteen decimal places", "seventeen decimal places", "eighteen decimal places",
   "nineteen decimal places", "twenty decimal places", "21 decimal places"].zipIdx.map fun (p, k) =>
    some ("The a is " ++ VE.Time.renderAmount (k + 1) 0 ++ " when rounded down to " ++ p ++ ".")
-- A numeral is exact decimal digits, at most 40 places; a value with no such numeral has no line.
#guard line (lit (3 / 2)) = some "1.5 equals 1."
#guard line (lit 0) = some "0 equals 1."
#guard (line (lit (1 / 3))).isNone
#guard (line (lit (1 / (10 : Rat) ^ 40))).isSome
#guard (line (lit (1 / (10 : Rat) ^ 41))).isNone
-- 11.2's form of value words: "the" first, single spaces, no phrase word first, no reserved word.
#guard VE.Calc.English.valueWordsOk "the baseline"
#guard VE.Calc.English.valueWordsOk "the summary"
#guard ["baseline", "the", "the a ", " the a", "the sum of the a", "the product of the a",
    "the square of the a", "the cube of the a", "the x and y", "the x minus y", "the x divided by y",
    "the x to the power y", "the x times ten to the power y", "the x is y", "the x be y",
    "the x equals y", "the x when rounded", "the x through y"].all
  (fun w => !VE.Calc.English.valueWordsOk w)
-- A reserved or phrase word inside another word is no reserved word.
#guard ["the island", "the minuses", "the bees", "the throughput", "the sumo of things"].all
  VE.Calc.English.valueWordsOk

end VE.Calc.Examples
