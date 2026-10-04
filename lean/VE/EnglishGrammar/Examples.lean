import VE.EnglishGrammar.Lexer

/-! Fixtures of the English instance that need no lexicon: the lexer (docs/spec/english-lean.md 8.4,
`conformance/english-lean/lexer.json`), the `glued` flags of the DRI's ruling on O1, the matching of
2.3 and the terminator condition W4 (e27). -/

namespace VE.EnglishGrammar.Examples
open VE.Grammar VE.EnglishGrammar

def w (s : String) : Tok := .word s false
def wi (s : String) : Tok := .word s true

/-- The tokens of a source that lexes. -/
def toks (s : String) : Array (Array Tok) :=
  match lex s with
  | .ok ss => ss
  | .error _ => #[]

def rejects (s : String) (r : Reject) : Bool :=
  match lex s with
  | .error r2 => r2 == r
  | .ok _ => false

-- x1, x16
#guard toks "Every service is reviewed." == #[#[wi "Every", w "service", w "is", w "reviewed"]]
#guard toks "Every \t\n service\r\n\t is  \n\n reviewed." == #[#[wi "Every", w "service", w "is", w "reviewed"]]
-- x2 to x4
#guard toks "Legacy is deployed.  It is reviewed." ==
  #[#[wi "Legacy", w "is", w "deployed"], #[wi "It", w "is", w "reviewed"]]
#guard toks "Therefore legacy is deployed." == #[#[wi "Therefore", wi "legacy", w "is", w "deployed"]]
#guard toks "It follows that Legacy is deployed." ==
  #[#[wi "It", w "follows", w "that", wi "Legacy", w "is", w "deployed"]]
-- x5, x6
#guard toks "alice is classified as \"has_owner\"." ==
  #[#[wi "alice", w "is", w "classified", w "as", .quoted "has_owner"]]
#guard toks "\"a. b\" is deployed." == #[#[.quoted "a. b", w "is", w "deployed"]]
-- x7: a comma glued to the label before it, with a space after it
#guard toks "For every service named S1, S1 is reviewed." ==
  #[#[wi "For", w "every", w "service", w "named", .label "S" 1, .punct "," true false, .label "S" 1,
      w "is", w "reviewed"]]
-- x8
#guard toks "(a) x; (b) y." ==
  #[#[.punct "(a)" false false, w "x", .punct ";" true false, .punct "(b)" false false, w "y"]]
#guard toks "( a ) x." == #[#[.punct "(" false false, w "a", .punct ")" false false, w "x"]]
-- x9 to x15
#guard rejects "Every service is reviewed" .unterminated
#guard rejects "" .emptyDocument
#guard rejects "   \t \n " .emptyDocument
#guard rejects "Alice owns legacy.." (.emptySentence 1)
#guard rejects "alice is classified as \"has_owner." (.openQuote 23)
#guard rejects "alice owns 007." (.badNumeral 11)
#guard rejects "alice owns #legacy." (.badCharacter 11)
#guard rejects ("".pushn 'a' 65536 ++ ".") .sourceTooLong
#guard rejects (String.join (List.replicate 5000 "a ") ++ "a.") .textTooLong
-- x17
#guard toks "ſervice café." == #[#[wi "ſervice", w "café"]]
-- Labels and numerals: `S01` and `x1` are words; `0` is a numeral.
#guard toks "S01 x1 0 12." == #[#[wi "S01", w "x1", .numeral 0, .numeral 12]]
-- Python's whitespace: a no-break space separates words.
#guard toks "a b." == #[#[wi "a", w "b"]]

-- The `glued` flags (DRI ruling 1 on O1): spacing variants that Python rejects lex differently.
#guard toks "deployed, it." == #[#[wi "deployed", .punct "," true false, w "it"]]
#guard toks "deployed , it." == #[#[wi "deployed", .punct "," false false, w "it"]]
#guard toks "deployed,it." == #[#[wi "deployed", .punct "," true true, w "it"]]
#guard toks "non-compliant." == #[#[wi "non", .punct "-" true true, w "compliant"]]
#guard toks "non - compliant." == #[#[wi "non", .punct "-" false false, w "compliant"]]
#guard toks "non -compliant." == #[#[wi "non", .punct "-" false true, w "compliant"]]
#guard toks "[n + 1]." ==
  #[#[.punct "[" false true, w "n", .punct "+" false false, .numeral 1, .punct "]" true true]]

-- The matching of 2.3 (fixtures g11 to g14 through `Terminal.accepts`).
#guard (Terminal.content "service").accepts (w "SERVICE")
#guard (Terminal.content "service").accepts (w "ſervice")
#guard !(Terminal.content "service").accepts (w "services")
#guard (Terminal.kw "every").accepts (wi "Every")
#guard !(Terminal.kw "every").accepts (w "Every")
#guard !(Terminal.kw "every").accepts (wi "EVERY")
#guard (Terminal.exact (.quoted "svc")).accepts (.quoted "svc")
#guard !(Terminal.exact (.quoted "svc")).accepts (.quoted "SVC")
#guard (Terminal.cls (.label "S")).accepts (.label "S" 3)
#guard !(Terminal.cls (.label "S")).accepts (.label "T" 3)
#guard (Terminal.cls .numeral).accepts (.numeral 7)
#guard (Terminal.exact (.punct "," true false)).accepts (.punct "," true false)
#guard !(Terminal.exact (.punct "," true false)).accepts (.punct "," false false)

-- e27: W4. `S → x .` is well-formed, and its terminal accepts the terminator.
def e27 : Grammar Terminal :=
  { rules := #[{ lhs := 0, rhs := [.t (.kw "x"), .t (.exact (.punct "." true false))], act := 0, tag := "r0" }],
    start := 0, rank := #[0] }
#guard e27.wf
#guard !terminatorFree e27

end VE.EnglishGrammar.Examples
