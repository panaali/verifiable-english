/-! The `wants` verb-phrase test of `reports@0` ("Y to VP", attribution.md 2.1), its one owner
(docs/spec/attitudes.md section 10 item 6, RC-4): `wantsPhrase?` gives a finite verb phrase's
infinitive, only where `finitePhrase` gives the phrase back. Moved here by AT-1w from
`ve/report_english.py`'s `_infinitive` and `_finite` (deleted there), with their behaviour on
every input; `reports@0`'s English reads both through the `reports-wants` kind
(`VE.Reports.Run.runWants`). AT-5 adds the verbs (F6). -/
namespace VE.Reports

/-- A phrase's head (up to its first space) and the rest after that space (Python's `partition`). -/
private def headRest (w : String) : String × String :=
  (String.mk (w.toList.takeWhile (· != ' ')), String.mk ((w.toList.dropWhile (· != ' ')).drop 1))

private def vowel (c : Char) : Bool := c ∈ ['a', 'e', 'i', 'o', 'u']

private def joined (head rest : String) : String := match rest with
  | "" => head
  | _ => head ++ " " ++ rest

/-- The finite form of an infinitival verb phrase: `be safe` is `is safe`, `try x` is `tries x`,
`fix x` is `fixes x`, `audit x` is `audits x` (the head's third person singular; the rest as it is). -/
def finitePhrase (w : String) : String :=
  let (head, rest) := headRest w
  let verb := match head with
    | "be" => "is" | "have" => "has" | "do" => "does"
    | _ => match head.toList.reverse with
      | 'y' :: c :: _ => if vowel c then head ++ "s" else head.dropRight 1 ++ "ies"
      | 's' :: _ | 'x' :: _ | 'z' :: _ | 'o' :: _ | 'h' :: 's' :: _ | 'h' :: 'c' :: _ => head ++ "es"
      | _ => head ++ "s"
  joined verb rest

/-- The infinitive of a finite head, before the round trip (none where no rule applies). -/
private def baseOf (head : String) : Option String :=
  match head with
  | "is" => some "be" | "has" => some "have" | "does" => some "do"
  | _ => match head.toList.reverse with
    | 's' :: 'e' :: 'i' :: c :: _ =>
      if vowel c then some (head.dropRight 1) else some (head.dropRight 3 ++ "y")
    | 's' :: 'e' :: 's' :: 's' :: _ | 's' :: 'e' :: 'h' :: 's' :: _ | 's' :: 'e' :: 'h' :: 'c' :: _
    | 's' :: 'e' :: 'x' :: _ | 's' :: 'e' :: 'z' :: _ | 's' :: 'e' :: 'o' :: _ => some (head.dropRight 2)
    | 's' :: 's' :: _ => none
    | 's' :: _ :: _ => some (head.dropRight 1)
    | _ => none

/-- The `wants` test: a declared template's finite verb phrase (`is safe`) as an infinitive
(`be safe`), only where `finitePhrase` gives the phrase back exactly. Refused: a rest starting
`not `, a head outside `[a-z]+` (the empty head has no base), and a head no rule turns into a base. -/
def wantsPhrase? (w : String) : Option String :=
  let (head, rest) := headRest w
  if rest.startsWith "not " || !head.all (fun c => 'a' ≤ c && c ≤ 'z') then none else
  match baseOf head with
  | none => none
  | some base =>
    let infinitive := joined base rest
    if finitePhrase infinitive == w then some infinitive else none

/-! The parity table (`tests/data/reports_wants_parity.json`, recorded from the deleted Python
functions on `94580b39b`): its reached rows, then its probes. Fixture C-e's phrase (spec 7.1) is
the probes' first row and has its own guard. -/

#guard wantsPhrase? "is classified as \"mass_casualty_weapon_uplift\"" ==
  some "be classified as \"mass_casualty_weapon_uplift\"" &&
  finitePhrase "be classified as \"mass_casualty_weapon_uplift\"" ==
  "is classified as \"mass_casualty_weapon_uplift\""

#guard [("audits service", some "audit service"), ("is safe", some "be safe"),
    ("publishes service", some "publish service")].all fun (p, i) => wantsPhrase? p == i

#guard [("audit service", "audits service"), ("be safe", "is safe"),
    ("publish service", "publishes service")].all fun (p, f) => finitePhrase p == f

#guard [("is", some "be"), ("has a key", some "have a key"), ("does work", some "do work"),
    ("is not safe", none), ("does not work", none), ("is not", some "be not"), ("is  safe", some "be  safe"),
    ("Is safe", none), (" is", none), ("is\tsafe", none), ("", none), ("s", none), ("be", none),
    ("isnt", none), ("carries x", some "carry x"), ("studies", some "study"), ("plays x", some "play x"),
    ("says x", some "say x"), ("passes x", some "pass x"), ("wishes", some "wish"), ("watches", some "watch"),
    ("fixes", some "fix"), ("fizzes", some "fizz"), ("goes", some "go"), ("toes", some "to"),
    ("buses", some "buse"), ("runs", some "run"), ("pass x", none), ("boxs", none), ("trys", none),
    ("gos", none), ("ies", some "ie"), ("oes", some "o"), ("es", some "e"), ("zes", some "z"),
    ("sses", some "ss"), ("yies", some "yy"), ("aies", some "aie"), ("eies", some "eie"), ("iies", some "iie"),
    ("oies", some "oie"), ("uies", some "uie"), ("bathes", some "bathe"), ("x1s", none), ("dоes", none),
    ("élèves", none), ("is\u00a0safe", none), ("is safe\r", some "be safe\r"),
    ("is \u201csafe\u201d", some "be \u201csafe\u201d"), ("\u212aeeps x", none), ("\u0130s safe", none),
    ("is\x00", none)].all fun (p, i) => wantsPhrase? p == i

#guard [("be safe", "is safe"), ("have a key", "has a key"), ("do work", "does work"),
    ("be not safe", "is not safe"), ("try x", "tries x"), ("play", "plays"), ("pass", "passes"),
    ("wish", "wishes"), ("watch", "watches"), ("fix", "fixes"), ("buzz", "buzzes"), ("go", "goes"),
    ("", "s"), (" x", "s x"), ("Be safe", "Bes safe"), ("y", "ys"), ("ay", "ays"), ("Ay", "Aies"),
    ("1y", "1ies"), ("é", "és"), ("run fast", "runs fast"), ("key", "keys"), ("skiy", "skiys"),
    ("toy", "toys"), ("buy", "buys"), ("bath", "baths"), ("be\u00a0safe", "be\u00a0safes"),
    ("be safe\r", "is safe\r"), ("\u212aeep", "\u212aeeps")].all fun (p, f) => finitePhrase p == f

end VE.Reports
