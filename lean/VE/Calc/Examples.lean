import VE.Calc.Render

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

-- V-4 and D-1.
#guard decide ((Claim.within (.div (lit 34) (lit 110)) (lit (3 / 10)) (lit (3 / 5))).decide empty = .holds)
#guard decide ((eq (.add (lit 15) (lit 2)) (lit 17)).decide empty = .holds)

-- V-9, V-10 and V-8: exact decimal arithmetic and two declared tie rules.
#guard decide ((round (lit (107 / 40)) 267 2).decide empty = .fails)
#guard decide ((Claim.rounds .halfEven (lit (107 / 40)) ⟨267, 2⟩).decide empty = .fails)
#guard decide ((round (.sub (.add (lit (1 / 10)) (lit (1 / 5))) (lit (3 / 10))) 1 16).decide empty = .fails)
#guard decide ((round (lit (4 / 512)) 7812 6).decide empty = .fails)
#guard decide ((Claim.rounds .halfEven (lit (4 / 512)) ⟨7812, 6⟩).decide empty = .holds)

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

private def words (n : String) : Option String :=
  if n = "baseline" then some "the baseline" else none

#guard VE.Calc.English.renderClaim words (.rounds .tiesUp (.val "baseline") ⟨296, 3⟩) =
  some "the baseline is 0.296 when rounded to three decimal places, with exact ties going up."
#guard VE.Calc.English.renderClaim words (.rounds .halfEven (.val "baseline") ⟨296, 3⟩) =
  some "the baseline is 0.296 when rounded to three decimal places, with exact ties going to the even digit."

end VE.Calc.Examples
