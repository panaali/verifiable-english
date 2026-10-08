import VE.EnglishGrammar.Lexicon

/-! Fixtures of the English instance: the lexer (docs/spec/english-lean.md 8.4,
`conformance/english-lean/lexer.json`), the `glued` flags of the DRI's ruling on O1, the matching of
2.3, the terminator condition W4 (e27), and lexicon validity (8.5, `conformance/english-lean/lexicon.json`). -/

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
-- x18 to x22: the spacing table (DRI ruling 1, finding F1). Offsets are UTF-8 bytes (x18b: a no-break
-- space is two). A spacing breach is found where its item starts, so `..` stays `emptySentence` (x11).
#guard rejects " Legacy is deployed." (.badSpacing 1)
#guard rejects "\u00a0Legacy is deployed." (.badSpacing 2)
#guard rejects "Legacy is deployed ." (.badSpacing 19)
#guard rejects "Legacy is deployed\t." (.badSpacing 19)
#guard rejects "Legacy is deployed.It is reviewed." (.badSpacing 19)
#guard rejects "Legacy is deployed.(a) x." (.badSpacing 19)
#guard rejects "Legacy has the recorded relation\"owner_of\" to alice." (.badSpacing 32)
#guard rejects "Legacy has the recorded relation \"owner_of\"to alice." (.badSpacing 43)
#guard rejects "\"a\"\"b\" is deployed." (.badSpacing 3)
#guard rejects "Legacy is deployed. ." (.emptySentence 1)
#guard toks "Legacy is deployed. \n" == #[#[wi "Legacy", w "is", w "deployed"]]
#guard toks "x ,y." == #[#[wi "x", .punct "," false true, w "y"]]
-- V3 reads a wording through the substitution of the lexical rules (`wordingTokens`, review C2): a hole
-- glued to a word is no hole of its own, so `{0}s are {1}` fails V3 instead of passing and giving no rule.
#guard shapeOk "{0} owns {1}" 2 && shapeOk "{0}, then {1}" 2
#guard !shapeOk "{0}s are {1}" 2 && (wordingTokens "{0}s are {1}").isNone
#guard !shapeOk "{0}\"x\" {1}" 2 && !shapeOk " {0} is deployed" 1 && !shapeOk "{0} is deployed ." 1
-- Labels and numerals: `S01` and `x1` are words; `0` is a numeral.
#guard toks "S01 x1 0 12." == #[#[wi "S01", w "x1", .numeral 0, .numeral 12]]
-- A numeral or a label index has no bound but the text limit, beyond the 4,300 digits of Python's `int`
-- (review regression; `tests/test_english_lean_lexer.py` checks the same sources in Python).
#guard toks ("".pushn '9' 4301 ++ ".") == #[#[.numeral ((10 : Int) ^ 4301 - 1)]]
#guard toks ("S".pushn '9' 4301 ++ ".") == #[#[.label "S" (10 ^ 4301 - 1)]]
#guard toks ("".pushn '9' 9999 ++ ".") == #[#[.numeral ((10 : Int) ^ 9999 - 1)]]
#guard rejects ("".pushn '9' 10000 ++ ".") .textTooLong
#guard toks ("S".pushn '9' 9998 ++ ".") == #[#[.label "S" (10 ^ 9998 - 1)]]
#guard rejects ("S".pushn '9' 9999 ++ ".") .textTooLong
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
  #[#[.punct "[" false true, w "n", .punct "+" false false, .numeral 1, .punct "]" true false]]
-- The integer marks are read as the hand parser reads them (`gluedFlags`).
#guard toks "least [-[n + 1] - --2]]." ==
  #[#[wi "least", .punct "[" false true, .punct "-" false true, .punct "[" false true, w "n",
      .punct "+" false false, .numeral 1, .punct "]" true false, .punct "-" false false, .punct "-" false true,
      .punct "-" false true, .numeral 2, .punct "]" true false, .punct "]" true false]]
#guard toks "least-3 least[n]and." ==
  #[#[wi "least", .punct "-" true true, .numeral 3, w "least", .punct "[" true true, w "n",
      .punct "]" true true, w "and"]]
#guard toks "non-\"x\"-y." == #[#[wi "non", .punct "-" true true, .quoted "x", .punct "-" true true, w "y"]]
#guard toks "[n]- 1, [n]." ==
  #[#[.punct "[" false true, w "n", .punct "]" true false, .punct "-" true false, .numeral 1, .punct "," true false,
      .punct "[" false true, w "n", .punct "]" true false]]

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

-- 8.5: lexicon validity. `F` is examples/fluent/environment.json; `F2` adds `audited`.
def F : Env :=
  { sorts := [{ name := "person" }, { name := "service" }],
    predicates := [{ name := "deployed", arity := 1, wording := some "{0} is deployed" },
                   { name := "reviewed", arity := 1, wording := some "{0} is reviewed",
                     negative := some "{0} is not reviewed" },
                   { name := "owns", arity := 2, wording := some "{0} owns {1}",
                     negative := some "{0} does not own {1}" }],
    constants := [{ name := "alice" }, { name := "legacy" }] }
def F2 : Env := { F with predicates := F.predicates ++ [{ name := "audited", arity := 1, wording := some "{0} is reviewed" }] }
def LF : Lexicon :=
  { nouns := [("person", "person"), ("service", "service")], letters := [("person", "P"), ("service", "S")],
    wordings := [("deployed", "{0} is deployed"), ("owns", "{0} owns {1}"), ("reviewed", "{0} is reviewed")],
    negatives := [("owns", "{0} does not own {1}"), ("reviewed", "{0} is not reviewed")], aliases := [],
    spellings := [("alice", "alice"), ("legacy", "legacy")] }

def setW (L : Lexicon) (p w : String) : Lexicon :=
  { L with wordings := (L.wordings.filter (·.1 != p)) ++ [(p, w)] }
def dropN (L : Lexicon) (p : String) : Lexicon := { L with negatives := L.negatives.filter (·.1 != p) }
def setN (L : Lexicon) (p w : String) : Lexicon :=
  { L with negatives := (L.negatives.filter (·.1 != p)) ++ [(p, w)] }

/-- The failing conditions, without repetition, in order. -/
def conds (E : Env) (L : Lexicon) : List String :=
  ((L.failures E {}).map (·.1)).eraseDups.mergeSort (· ≤ ·)

def recorded : String := "{0} has the recorded relation \"owns\" to {1}"
def clsR : String := "{0} is classified as \"reviewed\""
def clsA : String := "{0} is classified as \"audited\""

#guard conds F LF == []                                                     -- v1
#guard conds F (dropN (setW LF "owns" recorded) "owns") == []              -- v2
#guard conds F (setW LF "owns" recorded) == ["V5"]                          -- v3
#guard conds F (setW LF "reviewed" "{0} is checked") == ["V2", "V5"]        -- v4
#guard conds F (setW LF "owns" "{0} owns") == ["V2", "V3", "V5"]            -- v5
#guard conds F (setN LF "reviewed" "{0} is reviewed") == ["V2", "V5"]       -- v6
#guard conds F { LF with spellings := [("alice", "alice")] } == ["V1"]      -- v7
#guard conds F { LF with spellings := LF.spellings ++ [("bob", "bob")] } == ["V1"]
#guard conds F2 (setW LF "audited" clsA) == ["V4"]                          -- v8
#guard conds F2 (setW (dropN (setW LF "reviewed" clsR) "reviewed") "audited" "{0} is reviewed") == ["V4"]  -- v9
#guard conds F2 (setW (dropN (setW LF "reviewed" clsR) "reviewed") "audited" clsA) == []  -- v10
#guard conds F2 (setW (dropN (setW LF "reviewed" "{0} is  Reviewed") "reviewed") "audited" clsA) ==
  ["V2", "V4"]                                                              -- v11
#guard (LF.valid F {}) && !((setW LF "owns" recorded).valid F {})
-- V1 exempts no symbol (DRI ruling 2): a generated predicate without a wording is a failure.
#guard conds { F with predicates := F.predicates ++ [{ name := "risk__more_severe", arity := 2 }] } LF == ["V1"]
-- v12
#guard negativeTemplate "{0} is deployed" 1 == some "{0} is not deployed"
#guard negativeTemplate "{0} owns {1}" 2 == some "{0} does not own {1}"
#guard negativeTemplate "{0} has a parent {1}" 2 == some "{0} does not have a parent {1}"
#guard negativeTemplate "{0} carries {1}" 2 == some "{0} does not carry {1}"
#guard negativeTemplate "{0} glass {1}" 2 == none
#guard negativeTemplate "{0} voted for {1}" 2 == some "{0} did not vote for {1}"
#guard negativeTemplate "{0} involves a hard constraint violation" 1 ==
  some "{0} does not involve a hard constraint violation"
-- wordingKey: case and runs of whitespace and hyphens outside quotes; quoted parts exact
#guard wordingKey "{0} is  Reviewed" == wordingKey "{0} is reviewed"
#guard wordingKey "{0} is non-Compliant" == "{0} is non compliant"
#guard wordingKey "{0} is classified as \"A  b\"" == "{0} is classified as \"A  b\""
#guard wordingKey "  a \"b" == "a \"b"
#guard jsonQuote "has_owner" == "\"has_owner\""
#guard jsonQuote "café\"" == "\"caf\\u00e9\\\"\""

end VE.EnglishGrammar.Examples
