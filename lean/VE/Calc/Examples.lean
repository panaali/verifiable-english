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
#guard (Claim.rounds .tiesUp (lit (4 / 512)) ⟨7812, 6⟩).tieSensitive empty
#guard !(Claim.rounds .tiesUp (lit (669 / 250)) ⟨267, 2⟩).tieSensitive empty

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

end VE.Calc.Examples
