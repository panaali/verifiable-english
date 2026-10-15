import VE.EnglishGrammar.ProfileExamples
import VE.EnglishGrammar.PolicyReference

/-! The acceptance fixtures of docs/spec/english-lean-e2.md section 8 as `#guard` checks on the built port,
the overlay check, the request guards, the response texts and the advice table.

The environment `F` is `ReadExamples`'; `FA`, `FR` and `FM` are `ProfileExamples`', decoded after the boundary.
"F + p" is `F` with one more predicate (`fJson`), decoded by `Env.decode` as the service decodes it. For a
predicate fixture of 8.1 to 8.3 the lexicon is Python's choice as the port computes it (`portLex`), with the
selection the row names put in (`select`); each row checks Python's choice, the V1 to V5 failures
(`Lexicon.failures`) and the V6 failures (`Lexicon.policyFailures`) the section gives. Each block names the
fixture ids it checks.
-/

namespace VE.EnglishGrammar.E2Examples
open Lean VE.Grammar VE.EnglishGrammar

/-! ## The wire form of integers (`decode_encode`)

`intText` is the text `toString` writes, here on the compiled code, so `decode_encode`, proved of `intText`, is
a statement about the wire form the service sends. -/

#guard [0, 1, 9, 10, 99, 100, 12345678901234567890, -1, -9, -10, -100, -12345678901234567890].all
  fun (v : Int) => intText v == toString v
#guard ((List.range 2001).map fun (n : Nat) => (n : Int) - 1000).all fun v => intText v == toString v
#guard [EFormula.top, .pred "p" [], .pred "p" [.num (-3)], .pred "q" [.var 0, .scale (-2) (.const "c")],
  .pred "r" [.num 0, .num 1, .add (.num (-1)) (.var 2)], .not (.eq (.num 7) (.num (-7))),
  .reachBody true "s" (.lt (.var 0) (.num (-12))) (.const "a") (.const "b"),
  .reachNamed false "next" (.var 1) (.var 0)].all fun A => EFormula.decode A.encode == some A

/-! ## Environments and lexicons -/

/-- A declaration with its JSON fields. -/
abbrev Decl := String × List (String × Json)

def wording (w : String) : List (String × Json) := [("verbalisation", .str w)]
def described (d : String) : List (String × Json) := [("description", .str d)]
def nounOf (n : String) : List (String × Json) :=
  [("verbalisation", Json.mkObj [("singular", .str n), ("plural", .str (n ++ "s"))])]

/-- `F` as environment JSON (`ve.core@0`), without the predicates `drop`, with more predicates (name,
arguments, fields; the description `A predicate.` unless a field gives one), sorts and constants. -/
def fJson (preds : List (String × List String × List (String × Json)) := []) (sorts : List Decl := [])
    (consts : List (String × String × List (String × Json)) := []) (drop : List String := []) : Json :=
  let base : List (String × List String × List (String × Json)) :=
    [("deployed", ["service"], wording "{0} is deployed"),
     ("reviewed", ["service"], wording "{0} is reviewed" ++ [("negative_verbalisation", .str "{0} is not reviewed")]),
     ("owns", ["person", "service"], wording "{0} owns {1}" ++
       [("negative_verbalisation", .str "{0} does not own {1}")])]
  let predEntry := fun ((p, args, more) : String × List String × List (String × Json)) =>
    (p, Json.mkObj ([("arguments", toJson args)] ++
      (if more.any (·.1 == "description") then [] else described "A predicate.") ++ more))
  let sortEntry := fun ((s, more) : Decl) => (s, Json.mkObj (described "A sort." ++ more))
  let constEntry := fun ((c, s, more) : String × String × List (String × Json)) =>
    (c, Json.mkObj ([("sort", .str s)] ++ described "A constant." ++ more))
  Json.mkObj [("language", .str "ve.core@0"), ("profile", .str "relational-fol@0"),
    ("spec_revision", .str "ve-v0-draft-2026-09-20"),
    ("vocabulary", Json.mkObj [
      ("sorts", Json.mkObj ((([("person", []), ("service", [])] : List Decl) ++ sorts).map sortEntry)),
      ("predicates", Json.mkObj (((base.filter fun d => !drop.contains d.1) ++ preds).map predEntry)),
      ("constants", Json.mkObj ((([("alice", "person", []), ("legacy", "service", [])] :
        List (String × String × List (String × Json))) ++ consts).map constEntry))])]

/-- The decoded environment, with an overlay (`{}` for none), as `Env.decode` decodes a request. -/
def envOf (j : Json) (overlay : Json := Json.mkObj []) : Env :=
  match Env.decode j overlay with
  | .ok E => E
  | .error _ => ReadExamples.emptyEnv

/-- The decoded overlay. -/
def overlayOf (overlay : Json) : Overlay :=
  match Overlay.decode overlay with
  | .ok O => O
  | .error _ => {}

/-- `F` with more declarations. -/
def Fp (preds : List (String × List String × List (String × Json)) := []) (sorts : List Decl := [])
    (consts : List (String × String × List (String × Json)) := []) (drop : List String := []) : Env :=
  envOf (fJson preds sorts consts drop)

/-- A label letter for every sort: the fixture lexicons' where they have one. -/
def lettersFor (E : Env) : List (String × String) :=
  E.sorts.map fun s => (s.name, ((ReadExamples.LF.letters ++ ProfileExamples.LR.letters).lookup s.name).getD "I")

/-- Python's choice, as the port computes it: the wording and negative of every predicate, every noun and
spelling, the profile aliases, and a letter for every sort. -/
def portLex (E : Env) (O : Overlay := {}) : Lexicon :=
  { nouns := policyNouns E O, letters := lettersFor E,
    wordings := E.predicates.filterMap fun d => (policyPredicate E O d.name).map fun s => (d.name, s.1),
    negatives := E.predicates.filterMap fun d => ((policyPredicate E O d.name).bind (·.2)).map (d.name, ·),
    aliases := E.forms.aliases, spellings := policySpellings E O }

/-- `L` with `p` selecting `w` and, when given, the negative `n` (and no negative otherwise). -/
def select (L : Lexicon) (p w : String) (n : Option String := none) : Lexicon :=
  { L with wordings := L.wordings.map (fun e => if e.1 == p then (p, w) else e),
           negatives := (L.negatives.filter (·.1 != p)) ++ (n.toList.map (p, ·)) }

/-- `L` with the sort `s` selecting the noun `n`. -/
def selectNoun (L : Lexicon) (s n : String) : Lexicon :=
  { L with nouns := L.nouns.map fun e => if e.1 == s then (s, n) else e }

/-- `L` with the constant `c` spelled `sp`. -/
def spell (L : Lexicon) (c sp : String) : Lexicon :=
  { L with spellings := L.spellings.map fun e => if e.1 == c then (c, sp) else e }

/-- Python's choice of `p`'s wording. -/
def choice (E : Env) (p : String) : Option String := (policyPredicate E {} p).map (·.1)

def fallback (E : Env) (p : String) : Option String := fallbackWording p (E.arity p)

/-- A row of 8.1: Python's choice (`declared` or the fallback) and, for the lexicon that is Python's choice
with `p` selecting `w`, its V1 to V5 failures and its V6 failures. -/
def row (E : Env) (p w : String) (declared : Bool) (v15 v6 : List Failure) : Bool :=
  let L := select (portLex E) p w
  choice E p == (if declared then some w else fallback E p) &&
    L.failures E {} == v15 && L.policyFailures E {} == v6

def V6 (p : String) : List Failure := [("V6", "predicate", p)]

/-- F + a predicate of one argument (`service`) or two (`person`, `service`) with a wording. -/
def un (p w : String) (more : List (String × Json) := []) : String × List String × List (String × Json) :=
  (p, ["service"], wording w ++ more)
def bin (p w : String) (args : List String := ["person", "service"]) (more : List (String × Json) := []) :
    String × List String × List (String × Json) := (p, args, wording w ++ more)

/-! ## 8.1 V6: declared wordings (lx15 to lx22) -/

-- lx15a, lx15b
#guard row (Fp [un "stable" "{0} never fails"]) "stable" "{0} never fails" false [] (V6 "stable")
#guard row (Fp) "deployed" "{0} is deployed" true [] []
-- lx16a, lx16b
#guard row (Fp [un "archived" "{0} is legacy"]) "archived" "{0} is legacy" false [] (V6 "archived")
#guard row (Fp [un "archived" "{0} is archived"]) "archived" "{0} is archived" true [] []
-- lx17a, lx17b
#guard row (Fp [un "undeployed" "{0} is undeployed"]) "undeployed" "{0} is undeployed" false [] (V6 "undeployed")
#guard row (Fp [un "undeployed" "{0} is undeployed"] (drop := ["deployed"])) "undeployed" "{0} is undeployed" true
  [] []
-- lx18a, lx18b
#guard row (Fp [bin "managed_by" "{0} is managed by {1}" ["service", "person"]]) "managed_by"
  "{0} is managed by {1}" false [] (V6 "managed_by")
#guard row (Fp [bin "manages" "{0} manages {1}"]) "manages" "{0} manages {1}" true [] []
-- lx19a, lx19b
#guard row (Fp [bin "reports_to" "{0} reports to {1}"]) "reports_to" "{0} reports to {1}" true [] []
#guard row (Fp [bin "belongs_to" "{0} belongs to {1}"]) "belongs_to" "{0} belongs to {1}" false [] (V6 "belongs_to")
-- lx20a to lx20q
#guard row (Fp [bin "manage" "{0} manage {1}"]) "manage" "{0} manage {1}" false [] (V6 "manage")
def longWording : String :=
  "{0} supervises abcdefghij abcdefghij abcdefghij abcdefghij abcdefghij abcdefghij {1}"
#guard longWording.length == 84 && (longWording.splitOn " ").length == 9
#guard row (Fp [bin "supervises" longWording]) "supervises" longWording false [] (V6 "supervises")
#guard row (Fp [bin "denies_protection" "{0} denies the equal protection of the laws to {1}"]) "denies_protection"
  "{0} denies the equal protection of the laws to {1}" true [] []
#guard row (Fp [un "recorded" "{0} is recorded"]) "recorded" "{0} is recorded" false [] (V6 "recorded")
#guard row (Fp [un "logged" "{0} is logged"]) "logged" "{0} is logged" true [] []
def jFOsame : Json := ProfileExamples.routeEnv ["order@0", "relational-fol@0"] ["person", "service"]
  (ProfileExamples.basePreds ++ [("same", ["service"], ProfileExamples.worded "{0} is same")])
  [("alice", "person"), ("legacy", "service")]
#guard row (envOf jFOsame) "same" "{0} is same" false [] (V6 "same")
#guard row (Fp [un "same" "{0} is same"]) "same" "{0} is same" true [] []
#guard row (Fp [un "compliant" "{0} is v1.2 compliant"]) "compliant" "{0} is v1.2 compliant" false
  [("V3", "predicate", "compliant")] (V6 "compliant")
#guard row (Fp [un "compliant" "{0} is compliant"]) "compliant" "{0} is compliant" true [] []
#guard row (Fp [un "checked" "{0} is checked daily"]) "checked" "{0} is checked daily" false [] (V6 "checked")
#guard row (Fp [un "checked" "{0} is checked"]) "checked" "{0} is checked" true [] []
#guard row (Fp [un "running" "{0} runs"]) "running" "{0} runs" false [] (V6 "running")
#guard row (Fp [bin "relates" "{0} relates X1 {1}"]) "relates" "{0} relates X1 {1}" false [] (V6 "relates")
#guard row (Fp [bin "relates" "{0} relates {1}"]) "relates" "{0} relates {1}" true [] []
#guard row (Fp [un "ready" "{0} is service ready"]) "ready" "{0} is service ready" false [] (V6 "ready")
#guard row (Fp [un "checked" "{0} is checked", un "inspected" "{0} is checked"]) "checked" "{0} is checked" false
  [("V4", "predicate", "checked")] (V6 "checked")
#guard row (Fp [un "inspected" "{0} is inspected"]) "inspected" "{0} is inspected" true [] []
-- lx21a to lx21c
#guard row (Fp [bin "voted_for" "{0} voted for {1}" ["person", "person"]]) "voted_for" "{0} voted for {1}" true [] []
#guard row (Fp [bin "ballot" "{0} voted for {1}" ["person", "person"] (described "A member voted for a proposal.")])
  "ballot" "{0} voted for {1}" true [] []
#guard row (Fp [bin "ballot" "{0} voted for {1}" ["person", "person"] (described "A recorded choice.")])
  "ballot" "{0} voted for {1}" false [] (V6 "ballot")
-- lx22a to lx22f
#guard row (Fp [bin "appointed" "{0} was appointed by {1}" ["person", "person"]]) "appointed"
  "{0} was appointed by {1}" false [] (V6 "appointed")
#guard row (Fp [bin "appointed_by" "{0} was appointed by {1}" ["person", "person"]]) "appointed_by"
  "{0} was appointed by {1}" true [] []
#guard row (Fp [bin "undermines" "{0} undermines {1}", bin "erodes" "{0} undermines the oversight role of {1}"])
  "undermines" "{0} undermines {1}" true [] []
#guard row (Fp [bin "undermines" "{0} undermines {1}",
    bin "undermines_check" "{0} undermines the oversight role of {1}"]) "undermines" "{0} undermines {1}" true [] []
-- DRI X2: `allow` and `consent` reject each other through the head `permits`, so neither claims it for `open`
def Fpermits : Env :=
  Fp [bin "allow" "{0} permits {1}", bin "consent" "{0} permits visits {1}", un "open" "{0} is fully permits"]
#guard row Fpermits "open" "{0} is fully permits" true [] [] && row Fpermits "allow" "{0} permits {1}" false [] (V6 "allow")
#guard !(PolicyCtx.of Fpermits {}).lintHeads.any (·.1 == "permits") &&
  ["allow", "consent"].all ((PolicyCtx.of Fpermits {}).dropped.map (·.1)).contains
#guard row (Fp [(("undocumented_parent", ["person"], wording "{0} has an undocumented noncitizen parent")),
    (("documented", ["person"], wording "{0} is documented"))]) "undocumented_parent"
  "{0} has an undocumented noncitizen parent" false [] (V6 "undocumented_parent")
#guard row (Fp [(("undocumented_parent", ["person"], wording "{0} has an undocumented noncitizen parent"))])
  "undocumented_parent" "{0} has an undocumented noncitizen parent" true [] []

/-! ## 8.2 V6: risk, and the S3 fixture lexicons (lx23, lx24, lx29) -/

def FA := ProfileExamples.FA
def FR := ProfileExamples.FR
def LA := ProfileExamples.LA
def LR := ProfileExamples.LR
def safeFallback : String := "{0} is classified as \"safe\""
def laSafe : Lexicon := select LA "safe" safeFallback
def lrSafe : Lexicon := select LR "safe" safeFallback

/-- `FR` with `hazard` (action, harm) declared with the wording `w`. -/
def jFRh (w : String) : Json :=
  ProfileExamples.routeEnv ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"] ["action", "agent", "harm"]
    (ProfileExamples.altPreds ++ [("hazard", ["action", "harm"], ProfileExamples.worded w)])
    ProfileExamples.altConsts [("alternatives", ProfileExamples.altBlock), ("risk", ProfileExamples.riskBlock)]
def FRh (w : String) : Env := ProfileExamples.envOf (jFRh w)
def hazardFallback : String := "{0} has the recorded relation \"hazard\" to {1}"
def lrHazard (w : String) : Lexicon := { lrSafe with wordings := lrSafe.wordings ++ [("hazard", w)] }

-- lx23a to lx23e
#guard (lrHazard "{0} risks {1}").failures (FRh "{0} risks {1}") {} == [] &&
  (lrHazard "{0} risks {1}").policyFailures (FRh "{0} risks {1}") {} == V6 "hazard" &&
  choice (FRh "{0} risks {1}") "hazard" == some hazardFallback
#guard (lrHazard hazardFallback).failures (FRh "{0} risks {1}") {} == [] &&
  (lrHazard hazardFallback).policyFailures (FRh "{0} risks {1}") {} == []
#guard (lrHazard "{0} endangers {1}").failures (FRh "{0} endangers {1}") {} == [] &&
  (lrHazard "{0} endangers {1}").policyFailures (FRh "{0} endangers {1}") {} == []
#guard (select lrSafe "prevents" "{0} prevents {1}").failures FR {} == [] &&
  (select lrSafe "prevents" "{0} prevents {1}").policyFailures FR {} == V6 "prevents"
#guard laSafe.failures FA {} == [] && laSafe.policyFailures FA {} == []
-- lx24 and lx24′: V6 comes first in `lexiconFailure`
def lx24 : Lexicon := { lrHazard hazardFallback with
  negatives := (lrHazard hazardFallback).negatives ++ [("hazard", "{0} cannot lead to {1}")] }
#guard lx24.failures (FRh "{0} risks {1}") {} == [("V2", "negative", "hazard"), ("V5", "negative", "hazard")] &&
  lx24.policyFailures (FRh "{0} risks {1}") {} == [("V6", "negative", "hazard")] &&
  lexiconFailure (FRh "{0} risks {1}") {} lx24 == some ("V6", "negative", "hazard")
-- lx29
#guard [(ReadExamples.F, ReadExamples.LF), (ProfileExamples.FO, ProfileExamples.LO),
    (ProfileExamples.FD, ProfileExamples.LD), (ProfileExamples.FM, ProfileExamples.LM)].all fun (E, L) =>
  L.failures E {} == [] && L.policyFailures E {} == []
#guard LA.failures FA {} == [] && LA.policyFailures FA {} == [] &&
  LR.failures FR {} == [] && LR.policyFailures FR {} == []
#guard lrSafe.failures FR {} == [] && lrSafe.policyFailures FR {} == []

/-! ## 8.3 V6: the selections S3 did not name (lx25 to lx28) -/

def Fbare (p : String) (args : List String) (more : List (String × Json) := []) : Env := Fp [(p, args, more)]
-- lx25a to lx25e
#guard (select (portLex (Fbare "likes" ["person", "service"])) "likes" "{0} likes {1}").policyFailures
  (Fbare "likes" ["person", "service"]) {} == V6 "likes"
#guard (select (portLex (Fbare "likes" ["person", "service"])) "likes"
  "{0} has the recorded relation \"likes\" to {1}").policyFailures (Fbare "likes" ["person", "service"]) {} == []
#guard (select (portLex (Fbare "audits" ["person", "service"])) "audits" "{0} audits {1}").policyFailures
  (Fbare "audits" ["person", "service"]) {} == []
#guard (select (portLex (Fbare "archived" ["service"])) "archived" "{0} is archived").policyFailures
  (Fbare "archived" ["service"]) {} == []
#guard (select (portLex (Fbare "holds" ["service"])) "holds" "{0} is holds").policyFailures
  (Fbare "holds" ["service"]) {} == V6 "holds"
-- lx26a, lx26b
def assignsNeg : String :=
  "{0} does not have recorded relation assigns with argument two {1} and argument three {2}"
def Fassigns : Env := Fbare "assigns" ["person", "service", "person"] [("negative_verbalisation", .str assignsNeg)]
#guard (portLex Fassigns |>.failures Fassigns {}) == [] &&
  ({ portLex Fassigns with negatives := (portLex Fassigns).negatives ++ [("assigns", assignsNeg)] }).policyFailures
    Fassigns {} == [("V6", "negative", "assigns")]
#guard ReadExamples.LFv3.failures ReadExamples.F {} == [("V5", "negative", "owns")] &&
  ReadExamples.LFv3.policyFailures ReadExamples.F {} == [("V6", "negative", "owns")]
-- lx27a to lx27d
def Fitem (noun : String) : Env := Fp (sorts := [("item", nounOf noun)])
#guard (selectNoun (portLex (Fitem "every item")) "item" "every item").policyFailures (Fitem "every item") {} ==
  [("V6", "sort", "item")]
#guard (selectNoun (portLex (Fitem "every item")) "item" "entity of sort \"item\"").policyFailures
  (Fitem "every item") {} == []
#guard (selectNoun (portLex (Fitem "deployed service")) "item" "deployed service").policyFailures
  (Fitem "deployed service") {} == []
#guard (selectNoun (portLex (Fitem "deployed service")) "item" "item").policyFailures (Fitem "deployed service") {} ==
  [("V6", "sort", "item")]
-- lx28a to lx28d
def Fhence : Env := Fp (consts := [("hence", "service", [])])
#guard (spell (portLex Fhence) "hence" "hence").policyFailures Fhence {} == [("V6", "constant", "hence")]
#guard (spell (portLex Fhence) "hence" "\"hence\"").policyFailures Fhence {} == []
def constOverlay (displays : List (String × String)) : Json :=
  Json.mkObj [("constants", Json.mkObj (displays.map fun (c, d) => (c, Json.mkObj [("verbalisation", .str d)])))]
def Fapi : Env := envOf (fJson (consts := [("api", "service", [])])) (constOverlay [("api", "the api")])
def Fapi2 : Env := envOf (fJson (consts := [("api", "service", []), ("api2", "service", [])]))
  (constOverlay [("api", "the api"), ("api2", "api")])
#guard policySpellings Fapi {} == [("alice", "alice"), ("api", "the api"), ("legacy", "legacy")] &&
  (spell (portLex Fapi) "api" "the api").policyFailures Fapi {} == []
#guard policySpellings Fapi2 {} == [("alice", "alice"), ("api", "\"api\""), ("api2", "\"api2\""), ("legacy", "legacy")] &&
  (spell (portLex Fapi2) "api" "the api").policyFailures Fapi2 {} == [("V6", "constant", "api")]

/-! ## 8.3 (continued) and 8.11: overlay entries, suggested and not (lx31, lx32), and the overlay check -/

/-- A predicate overlay entry, suggested or not, with an optional negative. -/
def predOverlay (entries : List (String × String × Bool × Option String)) (sorts : List (String × String) := [])
    (consts : List (String × String) := []) : Json :=
  Json.mkObj [("sorts", Json.mkObj (sorts.map fun (s, n) => (s, Json.mkObj [("verbalisation",
      Json.mkObj [("singular", .str n), ("plural", .str (n ++ "s"))])]))),
    ("predicates", Json.mkObj (entries.map fun (p, w, sug, neg) => (p, Json.mkObj ([("verbalisation", .str w)] ++
      (if sug then [("suggested", .bool true)] else []) ++
      (neg.toList.map fun n => ("negative_verbalisation", .str n)))))),
    ("constants", Json.mkObj (consts.map fun (c, d) => (c, Json.mkObj [("verbalisation", .str d)])))]

/-- The environment with the overlay merged in, and the decoded overlay. -/
def withOverlay (j overlay : Json) : Env × Overlay := (envOf j overlay, overlayOf overlay)
def checkOf (j overlay : Json) : Option Failure := let (E, O) := withOverlay j overlay; overlayCheck E O

def jFast : Json := fJson [un "fast" "{0} is fast"]
-- lx31a, lx31b
#guard choice (withOverlay jFast (predOverlay [("fast", "{0} is a fast service", true, none)])).1 "fast" ==
  some "{0} is a fast service" && checkOf jFast (predOverlay [("fast", "{0} is a fast service", true, none)]) == none
#guard checkOf jFast (predOverlay [("fast", "{0} is a fast service", false, none)]) == some ("O3", "predicate", "fast")
-- lx31c to lx31f: the Kelvin sign K (U+212A) under `re.I`
def kelvin : String := String.singleton (Char.ofNat 0x212A)
def jKeen : Json := fJson [un "keen" "{0} is eager"]
#guard choice (withOverlay jKeen (predOverlay [("keen", "{0} is " ++ kelvin ++ "een", true, none)])).1 "keen" ==
  some ("{0} is " ++ kelvin ++ "een") &&
  checkOf jKeen (predOverlay [("keen", "{0} is " ++ kelvin ++ "een", true, none)]) == none
#guard checkOf jKeen (predOverlay [("keen", "{0} IS keen", true, none)]) == none
def jObscure : Json := fJson [un "known" "{0} is known", un "obscure" "{0} is obscure"]
#guard checkOf jObscure (predOverlay [("obscure", "{0} is un" ++ kelvin ++ "nown", true, none)]) ==
  some ("O3", "predicate", "obscure")
def jGreen : Json := fJson [un "green" "{0} is green"] (consts := [("kelp", "service", [])])
#guard checkOf jGreen (predOverlay [("green", "{0} is " ++ kelvin ++ "elp green", true, none)]) ==
  some ("O3", "predicate", "green")
-- lx32a, lx32b: generated names keep their declared wordings under Python's enumeration
def jFApre : Json := ProfileExamples.routeEnv ["alternatives@0", "norms@0", "relational-fol@0"]
  ["action", "agent", "harm"] (ProfileExamples.altPreds ++
    [("preventable", ["harm"], ProfileExamples.worded "{0} is fully avoidable")])
  ProfileExamples.altConsts [("alternatives", ProfileExamples.altBlock)]
#guard choice (ProfileExamples.envOf jFApre) "preventable" == some "{0} is fully avoidable"
def jFRslight : Json := ProfileExamples.routeEnv ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"]
  ["action", "agent", "harm"] (ProfileExamples.altPreds ++
    [("slight", ["harm"], ProfileExamples.worded "{0} is fully minor")])
  ProfileExamples.altConsts [("alternatives", ProfileExamples.altBlock), ("risk", ProfileExamples.riskBlock)]
#guard choice (ProfileExamples.envOf jFRslight) "slight" == some "{0} is fully minor"
-- lx32c: the severity sort named `level`, beside a sort `grade` whose noun is `level`
def riskBlockLevel : Json := Json.mkObj [
  ("severity", Json.mkObj [("sort", .str "level"), ("classes", toJson ["minor", "catastrophic"]),
    ("more_severe", toJson [["catastrophic", "minor"]]), ("unranked", Json.arr #[]),
    ("decided_by", .str "the fixture author")]),
  ("harm_classes", toJson [["injury", "catastrophic"]]), ("unexamined", .str "possible")]
def jFRlevel : Json := (ProfileExamples.routeEnv ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"]
  ["action", "agent", "harm", "grade"] ProfileExamples.altPreds ProfileExamples.altConsts
  [("alternatives", ProfileExamples.altBlock), ("risk", riskBlockLevel)])
def FRlevel : Env := envOf (jFRlevel.setObjVal! "vocabulary" ((jFRlevel.getObjValD "vocabulary").setObjVal! "sorts"
  (((jFRlevel.getObjValD "vocabulary").getObjValD "sorts").setObjVal! "grade"
    (Json.mkObj (described "A sort." ++ nounOf "level")))))
#guard (policyNouns FRlevel {}).lookup "grade" == some "level" &&
  (policyNouns FRlevel {}).lookup "level" == some "severity"

-- ov1a, ov1b: a duplicate wording as a declaration (the fallback) and as an overlay entry (O1)
def jInspected : Json := fJson [un "inspected" "{0} is inspected"]
#guard choice (Fp [un "inspected" "{0} is reviewed"]) "inspected" ==
  fallback (Fp [un "inspected" "{0} is reviewed"]) "inspected"
#guard checkOf jInspected (predOverlay [("inspected", "{0} is reviewed", false, none)]) ==
  some ("O1", "predicate", "inspected")
-- ov2a, ov2b: a reused risk wording (O2)
#guard choice (FRh "{0} risks {1}") "hazard" == some hazardFallback
#guard checkOf (jFRh "{0} endangers {1}") (predOverlay [("hazard", "{0} risks {1}", false, none)]) ==
  some ("O2", "predicate", "hazard")
-- ov3a, ov3b: an entry the producer would not select (O3)
#guard checkOf (fJson [un "stable" "{0} is stable"]) (predOverlay [("stable", "{0} never fails", false, none)]) ==
  some ("O3", "predicate", "stable")
-- ov4a to ov4c: a negative left with an issue
def jChecked : Json := fJson [un "checked" "{0} is checked"]
#guard (policyPredicate (Fp [un "checked" "{0} is checked" [("negative_verbalisation", .str "{0} is never checked")]])
  {} "checked") == some ("{0} is checked", none)
#guard checkOf jChecked (predOverlay [("checked", "{0} is checked", false, some "{0} is never checked")]) ==
  some ("O3", "predicate", "checked")
#guard checkOf jChecked (predOverlay [("checked", "{0} is checked", false, some "{0} is not checked")]) == none
-- ov5a, ov5b: a sort entry whose noun is not selected (O3, sort)
#guard (policyNouns (Fitem "every item") {}).lookup "item" == some "entity of sort \"item\""
#guard checkOf (fJson (sorts := [("item", [])])) (predOverlay [] [("item", "every item")]) == some ("O3", "sort", "item")
-- ov6: constant entries are never refused
#guard checkOf (fJson (consts := [("api", "service", []), ("api2", "service", [])]))
  (predOverlay [] [] [("api", "the api"), ("api2", "api")]) == none
-- ov7: O1 runs before O3
#guard checkOf (fJson [un "inspected" "{0} is inspected", un "stable" "{0} is stable"])
  (predOverlay [("stable", "{0} never fails", false, none), ("inspected", "{0} is reviewed", false, none)]) ==
  some ("O1", "predicate", "inspected")
-- ov8, ov9: a role keeps its fixed wording; with another symbol's negative it is O1
#guard checkOf ProfileExamples.jFA (predOverlay [("available", "{0} is available to {1}", false,
  some "{0} leads to {1}")]) == some ("O1", "predicate", "available")
#guard checkOf ProfileExamples.jFA (predOverlay [("available", "{0} is available to {1}", false, none)]) == none &&
  choice (envOf ProfileExamples.jFA (predOverlay [("available", "{0} is available to {1}", false, none)]))
    "available" == some "{0} is available to {1}"
-- ov10: O2 runs before O3
#guard checkOf (ProfileExamples.routeEnv ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"]
    ["action", "agent", "harm", "item"] (ProfileExamples.altPreds ++
      [("hazard", ["action", "harm"], ProfileExamples.worded "{0} endangers {1}")])
    ProfileExamples.altConsts [("alternatives", ProfileExamples.altBlock), ("risk", ProfileExamples.riskBlock)])
  (predOverlay [("hazard", "{0} risks {1}", false, none)] [("item", "every item")]) == some ("O2", "predicate", "hazard")
-- ov11a, ov11b: what the check gives on its own (display_environment refuses both first)
#guard checkOf ProfileExamples.jFA (predOverlay [("available", "{0} leads to {1}", false, none)]) ==
  some ("O1", "predicate", "available")
#guard checkOf ProfileExamples.jFA (predOverlay [("available", "{0} can use {1}", false, none)]) == none
-- overlayCheck_constants: constant entries change no refusal
#guard overlayCheck (envOf jInspected) { overlayOf (predOverlay [("inspected", "{0} is reviewed", false, none)]) with
  constants := [("legacy", "the legacy")] } == some ("O1", "predicate", "inspected")

/-! ## 8.6 Advice (ad1 to ad19), and the advice of a refused sentence -/

def adviceOf (profiles : List String) (s : String) : Option String :=
  match lex s with
  | .ok sents => ((sents[0]?).bind fun toks => advice profiles toks.toList).map (·.1)
  | .error _ => none
def risk : List String := ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"]
def alts : List String := ["alternatives@0", "norms@0", "relational-fol@0"]
def base : List String := ["relational-fol@0"]
#guard [("Wait may lead to injury.", "risk-may"), ("Wait does not lead to injury.", "risk-does-not"),
  ("Wait could lead to injury.", "risk-degree"), ("Wait certainly leads to injury.", "risk-certainly"),
  ("Wait prevents injury.", "risk-prevents"), ("Wait is safer than proceed.", "risk-safer"),
  ("Wait cannot lead to injury unless robot is safe.", "risk-condition"),
  ("Wait causes injury.", "alternatives-causes")].all fun (s, id) => adviceOf risk s == some id
#guard adviceOf alts "Wait could lead to injury." == some "alternatives-degree"
#guard adviceOf base "Wait may lead to injury." == none
#guard adviceOf base "No service that is deployed is not reviewed." == some "negated-existential"
#guard adviceOf base "No service is deployed." == none
#guard adviceOf base "They are deployed." == some "plural-pronoun"
#guard adviceOf base "Every sevice is reviewed." == none
#guard adviceOf alts "Wait allows a harm to a human being to happen." == some "alternatives-human-harm"
#guard adviceOf alts "Wait allows robot to leave." == some "alternatives-person"
#guard adviceOf alts "Wait allows injury to happen." == none
#guard adviceOf alts "Wait through inaction allows injury." == some "alternatives-inaction"
#guard adviceOf alts "They allows robot to leave." == some "plural-pronoun"
-- review B2 of E2: `another action` without an action in scope gets Python's hint as advice
#guard adviceOf alts "Another action available to robot prevents injury." == some "alternatives-another"

/-! ## 8.7 Admission and the check of candidates (cn10 to cn18) -/

def F := ReadExamples.F
def LF := ReadExamples.LF
def dl : EFormula := ReadExamples.u "deployed" (ReadExamples.c "legacy")
def adm (E : Env) (L : Lexicon) (s : String) : AdmitOutcome := admitRequest E {} L workBudget s
def admOk (o : AdmitOutcome) : Option (List (EFormula × Bool) × List (Nat × List Nat)) :=
  match o with
  | .ok rs obs => some (rs, obs)
  | _ => none
#guard admOk (adm F LF "Legacy is deployed. Therefore legacy is deployed.") ==
  some ([(dl, false), (dl, true)], [(1, [0])])
def avail : List (EFormula × Bool) :=
  [(ReadExamples.b "available" (ReadExamples.c "wait") (ReadExamples.c "robot"), false)]
#guard admOk (adm FA LA "Wait is available to robot.") == some (avail, [])
#guard admOk (adm FA laSafe "Wait is available to robot.") == some (avail, [])
#guard checkRequest FA {} LA workBudget avail ["Wait is available to robot."] == some 0
#guard checkRequest FA {} laSafe workBudget avail ["Wait is available to robot."] == some 0
#guard Run.noPremiseText 0 == "Sentence 1 is marked as a conclusion, and no earlier sentence is a premise." &&
  Run.unprovedText 1 == "Sentence 2 is marked as a conclusion, and no checked derivation from the earlier premises " ++
    "was found: {status}"
#guard (match adm F LF "Therefore legacy is deployed." with | .noPremise 0 => true | _ => false)
#guard (match adm F LF "Therefore legacy is deployed. So legacy is deployed." with | .noPremise 0 => true | _ => false)
#guard (match adm F LF "Every sevice is reviewed." with
  | .refused (.stopped 0 .noDerivation) => true
  | _ => false)

/-! ## 8.8 The service: the check of candidates (ev4a to ev4d) and the lexicon format (ev15d) -/

#guard checkRequest F {} LF workBudget [(dl, false)]
  ["Legacy is reviewed.", "Legacy is deployed", "Legacy is deployed.", "legacy is deployed."] == some 2
#guard checkRequest F {} LF workBudget [(dl, false)] ["Legacy is reviewed."] == none
#guard checkRequest F {} LF workBudget [(dl, false), (dl, true)]
  ["Legacy is deployed. Legacy is deployed.", "Legacy is deployed. Therefore legacy is deployed."] == some 1
#guard grammarFault FA {} LA == none && lexiconFailure FA {} LA == none
def lexJson (format envId : String) : Json :=
  Json.mkObj [("format", .str format), ("environment_id", .str envId), ("nouns", Json.arr #[]),
    ("letters", Json.arr #[]), ("wordings", Json.arr #[]), ("negatives", Json.arr #[]), ("aliases", Json.arr #[]),
    ("spellings", Json.arr #[])]
#guard (match Run.decodeLexicon "e" (lexJson "x" "e") with
  | .error m => m == "InvalidInput: the lexicon format is not ve.english-lexicon@1"
  | .ok _ => false)
#guard (match Run.decodeLexicon "e" (lexJson "ve.english-lexicon@1" "f") with
  | .error m => m == "InvalidInput: the lexicon names another environment"
  | .ok _ => false)

/-! ## 8.13 Guards, codes and texts (gg1, gg2, tg1, tg2, cn19, cl1, lx33a, lx33b) -/

#guard grammarFault FA {} LA == none && grammarFault FA {} laSafe == none
#guard (match translateRequest FA {} LA 2 workBudget "Wait is available to robot." with
  | .readings [_] true => true
  | _ => false)
#guard (match translateRequest FA {} laSafe 2 workBudget "Wait is available to robot." with
  | .readings [_] true => true
  | _ => false)
#guard (match translateRequest F {} LF 2 workBudget "Legacy is deployed. Legacy is reviewed." with
  | .notOneSentence => true
  | _ => false)
#guard Run.codeClasses.lookup "NotOneSentence" == some "SyntaxError" &&
  Run.codeClasses.lookup "InvalidOverlay" == some "VEError" &&
  Run.codeClasses.lookup "Internal" == some "CheckerUnavailable"
#guard !acceptsDeclared FA {} "available" && choice FA "available" == some "{0} is available to {1}"
def jFMa : Json := ProfileExamples.routeEnv ["norms@0", "relational-fol@0"] ["person", "service"]
  (ProfileExamples.basePreds ++ [("access", ["person", "service"], ProfileExamples.worded "{0} accesses {1}" ++
    ProfileExamples.regulated "permission" "{0} access {1}")])
  [("alice", "person"), ("legacy", "service")]
#guard acceptsDeclared (ProfileExamples.envOf jFMa) {} "access" &&
  choice (ProfileExamples.envOf jFMa) "access" == some "{0} may access {1}"
-- md4: a role predicate regulated as a permission gets its modal form under `Env.decode` (D18)
def jFAreg : Json := ProfileExamples.routeEnv ["alternatives@0", "norms@0", "relational-fol@0"]
  ["action", "agent", "harm"]
  ([("available", ["action", "agent"], ProfileExamples.worded "{0} is available to {1}" ++
      ProfileExamples.regulated "permission" "{0} choose {1}")] ++ ProfileExamples.altPreds.drop 1)
  ProfileExamples.altConsts [("alternatives", ProfileExamples.altBlock)]
#guard choice (envOf jFAreg) "available" == some "{0} may choose {1}"
#guard (Run.environmentId jFAreg).toOption.isNone

/-! ## The responses: spans, texts and classes (review B1, B3 of E2)

Every status other than `one` has its codes in `statusCodes`, and every code a class; a lexical rejection's span
is the offending character, in code points; `IllTyped` names the sentence whose formula fails the typed check;
`InvalidGrammar` and `InvalidOverlay` texts say what the mode did not do. -/

#guard Run.statusCodes.all fun (_, codes) => codes.all fun c => (Run.codeClasses.lookup c).isSome
-- the lexer's rejections are exactly the unsentenced codes of `rejected`
#guard (["", "x", "Legacy is deployed", "Legacy is deployed .", "Legacy is # deployed.", "Alice owns 007.",
    "Alice owns \"legacy.", "Legacy is deployed.."].filterMap fun s => match lex s with
      | .error r => some r.code
      | .ok _ => none).all Run.unsentencedCodes.contains
/-- The span of a lexical rejection of `s`, in code points: `é` is two bytes and one code point. -/
def lexSpanOf (s : String) : Option (String × Option (Nat × Nat)) :=
  match lexSpans s with
  | .error r => some (r.code, Run.lexicalSpan s r)
  | .ok _ => none
#guard lexSpanOf "Légacy is deployed. Alice owns legacy # x." == some ("BadCharacter", some (38, 39))
#guard lexSpanOf "Légacy is deployed. Alice owns 007." == some ("BadNumeral", some (31, 32))
#guard lexSpanOf "Légacy is deployed. Alice owns \"legacy." == some ("OpenQuote", some (31, 32))
#guard lexSpanOf "Légacy is deployed. Alice owns legacy ." == some ("BadSpacing", some (38, 39))
#guard Run.lexicalSpan "ab" .unterminated == none
#guard Run.invalidGrammarText "english.read" "lexicon" (some ("V6", "predicate", "safe")) ==
  "The vocabulary selection was not accepted (invalidGrammar lexicon: V6 predicate safe). No text was read."
#guard Run.invalidGrammarText "english.check" "notTyped" none ==
  "The vocabulary selection was not accepted (invalidGrammar notTyped). No candidate was checked."
#guard Run.invalidGrammarText "english.grammar" "lexicon" none ==
  "The vocabulary selection was not accepted (invalidGrammar lexicon). No grammar was exported."
#guard Run.rejectionText "Every action available to robot cannot lead to injury." 0
    (.blockedWording "risk-every-cannot") ==
  Run.riskEveryCannotText 0 "robot" "injury"

/-! ## The policy against spec 5.2's text (GE2 item 9)

`Policy.lean` computes the environment's tables once (`PolicyCtx`); `PolicyReference.lean` is spec 5.2's text. On
every environment of this file, with and without overlays, and on a crowded one whose wordings collide, every
selection, verdict, lint code, noun, spelling, V6 failure and overlay refusal is the same. -/

/-- Forty predicates whose wordings repeat, collide with heads and nouns, and include 8.1's refused shapes. -/
def crowded : Env := Fp (sorts := [("item", nounOf "every item"), ("box", nounOf "deployed service")])
  (consts := [("hence", "service", []), ("api", "service", [])])
  ((List.range 40).map fun k =>
    let words := ["{0} never fails", "{0} is reviewed", "{0} is archived", "{0} is checked daily",
      "{0} is v1.2 compliant", "{0} runs", "{0} is service ready", "{0} is deployed", "{0} is undeployed",
      "{0} is legacy"]
    let pairs := ["{0} manages {1}", "{0} reports to {1}", "{0} belongs to {1}", "{0} owns {1}",
      "{0} undermines {1}", "{0} voted for {1}", "{0} relates X1 {1}", "{0} was appointed by {1}"]
    if k % 2 == 0 then (s!"q{k}", ["service"], wording (words.getD (k % 10) "{0} is ok"))
    else (s!"r{k}", ["person", "service"], wording (pairs.getD (k % 8) "{0} sees {1}")))

def noOverlay : Overlay := {}

def policyEnvs : List (Env × Overlay) :=
  [(F, noOverlay), (FA, noOverlay), (FR, noOverlay), (ProfileExamples.FM, noOverlay), (ProfileExamples.FO, noOverlay), (ProfileExamples.FD, noOverlay),
   (FRh "{0} risks {1}", noOverlay), (FRh "{0} endangers {1}", noOverlay), (Fitem "every item", noOverlay), (Fitem "deployed service", noOverlay),
   (Fhence, noOverlay), (Fapi, noOverlay), (Fapi2, noOverlay), (envOf jFOsame, noOverlay), (Fassigns, noOverlay), (envOf jFApre, noOverlay),
   (envOf jFRslight, noOverlay), (envOf jFMa, noOverlay), (FRlevel, noOverlay), (crowded, noOverlay),
   (Fp [bin "undermines" "{0} undermines {1}", bin "erodes" "{0} undermines the oversight role of {1}"], noOverlay),
   (Fpermits, noOverlay),
   (Fp [(("undocumented_parent", ["person"], wording "{0} has an undocumented noncitizen parent")),
     (("documented", ["person"], wording "{0} is documented"))], noOverlay),
   (Fp [bin "ballot" "{0} voted for {1}" ["person", "person"] (described "A member voted for a proposal.")], noOverlay),
   (Fp [un "checked" "{0} is checked", un "inspected" "{0} is checked"], noOverlay)] ++
  [(jFast, predOverlay [("fast", "{0} is a fast service", true, none)]),
   (jFast, predOverlay [("fast", "{0} is a fast service", false, none)]),
   (jKeen, predOverlay [("keen", "{0} is " ++ kelvin ++ "een", true, none)]),
   (jObscure, predOverlay [("obscure", "{0} is un" ++ kelvin ++ "nown", true, none)]),
   (jGreen, predOverlay [("green", "{0} is " ++ kelvin ++ "elp green", true, none)]),
   (jInspected, predOverlay [("inspected", "{0} is reviewed", false, none)]),
   (jChecked, predOverlay [("checked", "{0} is checked", false, some "{0} is never checked")]),
   (fJson (sorts := [("item", [])]), predOverlay [] [("item", "every item")]),
   (ProfileExamples.jFA, predOverlay [("available", "{0} is available to {1}", false, some "{0} leads to {1}")]),
   (jFRh "{0} endangers {1}", predOverlay [("hazard", "{0} risks {1}", false, none)])].map
    fun (j, o) => withOverlay j o

/-- Every symbol-level result of the policy, on one environment and overlay, against the reference. -/
def agreesWithReference (E : Env) (O : Overlay) : Bool :=
  let L := portLex E O
  E.predicates.all (fun d => policyPredicate E O d.name == PolicyReference.policyPredicate E O d.name &&
    acceptsDeclared E O d.name == PolicyReference.acceptsDeclared E O d.name &&
    duplicateWording E O d.name == PolicyReference.duplicateWording E O d.name &&
    mainSelection E O d == PolicyReference.mainSelection E O d &&
    ((E.declaredWording O d.name).map fun w => lintCodes E O d.name w d.arity ==
      PolicyReference.lintCodes E O d.name w d.arity).getD true &&
    ((E.declaredWording O d.name).map fun w => templateCodes E O w == PolicyReference.templateCodes E O w).getD true) &&
  policyNouns E O == PolicyReference.policyNouns E O &&
  policySpellings E O == PolicyReference.policySpellings E O &&
  L.policyFailures E O == PolicyReference.policyFailures E O L &&
  E.predicates.all (fun d => (select L d.name ((fallbackWording d.name d.arity).getD "x")).policyFailures E O ==
    PolicyReference.policyFailures E O (select L d.name ((fallbackWording d.name d.arity).getD "x"))) &&
  E.predicates.all (fun d => ((E.declaredWording O d.name).map fun w =>
    (select L d.name w).policyFailures E O == PolicyReference.policyFailures E O (select L d.name w)).getD true) &&
  overlayCheck E O == PolicyReference.overlayCheck E O

-- `wordOccursIn` is `wordOccurs` on every token of word characters, and defers to it on any other
#guard (["owns", "own", "x1", "_a", "un-safe", "safe", "A", "café", "", "re view", "Kelvin"].all fun tok =>
  ["owns legacy", "x1 owns", "un-safe owns", "the_a b", "safe-ish", "unclear", "A b", "café au lait",
   "reviewed", "re view", "Kelvin", "own", ""].all fun phrase =>
    wordOccursIn (runs isW phrase) phrase tok == wordOccurs tok phrase)
#guard policyEnvs.length == 35
#guard policyEnvs.all fun (E, O) => agreesWithReference E O
#guard crowded.predicates.length == 43 &&
  (crowded.predicates.map fun d => (policyPredicate crowded {} d.name).isSome).all id

end VE.EnglishGrammar.E2Examples
