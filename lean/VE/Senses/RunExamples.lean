import VE.Senses.Run
import VE.Senses.Fixtures

/-! The runner's projection helpers (senses plan 2.6, 2.7, B6) as `#guard` checks: the projected lexicon is one
`english.read` reads back; preamble lines project as a document with those lines does; a candidate's identities
are its projection's; and a fault's status is `senses.read`'s. -/

namespace VE.Senses.RunExamples
open Lean VE.EnglishGrammar VE.Senses VE.Senses.Fixtures VE.Senses.Run

def caseJ : VE.EnglishGrammar.Run.Case := { E := EJ, O := {}, L := LJ, overlayFailure := none, identities := [] }

def lineFunny2 : String := "In this document, funny means strange."

/-- A lexicon with an entry in every list, a negated alias among them. -/
def LA : Lexicon :=
  { nouns := LJ.nouns, letters := LJ.letters, wordings := [("p", "{0} is p")],
    negatives := [("p", "{0} is not p")], aliases := [("p", "{0} is q", true), ("p", "{0} is r", false)],
    spellings := LJ.spellings }

#guard [LJ, LA].all fun L => match VE.EnglishGrammar.Run.decodeLexicon "e" (lexiconJson "e" L) with
  | .ok L' => reprStr L' == reprStr L
  | .error _ => false
#guard (VE.EnglishGrammar.Run.decodeLexicon "f" (lexiconJson "e" LJ)).toOption.isNone

/-- The projection of `lines` over `used`, against `project` under the assignment the lines give. -/
def sameAs (lines : String) (A : List (String × Nat)) (used : List String) : Bool :=
  match linesProjection F caseJ workBudget lines used, project F ⟨A⟩ EJ LJ used with
  | .ok (.ok P), .ok Q => P.envJson == Q.envJson && reprStr P.map == reprStr Q.map && reprStr P.lexicon == reprStr Q.lexicon
  | _, _ => false

#guard sameAs lineFunny2 [("funny", 2)] ["funny"]
#guard sameAs (lineFunny2 ++ "\nIn this document, tells means says aloud.") [("funny", 2), ("tells", 1)] ["funny", "tells"]
#guard sameAs "" [] ["funny", "tells"]
#guard !sameAs lineFunny2 [("funny", 1)] ["funny"]
#guard match linesProjection F caseJ workBudget (lineFunny2 ++ " The riddle is funny.") ["funny"] with
  | .error e => e == "InvalidInput: sentence 2 of the lines is not a preamble line"
  | .ok _ => false
#guard match linesProjection F caseJ workBudget "In this document, funny means purple." ["funny"] with
  | .ok (.error f) => f.code == "UnknownGloss"
  | _ => false

#guard match project F ⟨[]⟩ EJ LJ ["funny", "tells"], project F ⟨[]⟩ EJ LJ [] with
  | .ok P, .ok Q => usedOf P == ["funny", "tells"] && usedOf Q == []
  | _, _ => false

/-- The identities of the projection of `lines` over `funny`. -/
def idsOf (lines : String) : List (String × Json) :=
  match linesProjection F caseJ workBudget lines ["funny"] with
  | .ok (.ok P) => match projectionIds caseJ P with
    | .ok (lexicon, ids) => ids ++ [("lexicon", lexicon)]
    | .error _ => []
  | _ => []

#guard match idsOf lineFunny2, idsOf "In this document, funny means amusing.", project F ⟨[("funny", 2)]⟩ EJ LJ ["funny"] with
  | [("environment_id", .str e2), ("lexicon_id", .str l2), ("grammar_id", .str g2), ("lexicon", lex)],
    [("environment_id", .str e1), ("lexicon_id", .str l1), ("grammar_id", .str g1), _], .ok Q =>
    e2 != e1 && l2 != l1 && g2 == g1 &&
    (VE.EnglishGrammar.Run.environmentId Q.envJson).toOption == some e2 &&
    (VE.CertificateWire.digest "ve-english-lexicon-v1\n" lex).toOption == some l2 &&
    (VE.EnglishGrammar.Run.grammarId EJ.profiles).toOption == some g2 && lex.getObjValD "environment_id" == .str e2
  | _, _, _ => false

#guard (faultJson (.preambleBudget 0)).getObjValD "status" == .str "budget"
#guard (faultJson (.unknownWord 0 "x")).getObjValD "status" == .str "rejected"
#guard (faultJson (.unknownWord 0 "x")).getObjValD "code" == .str "UnknownWord"

/-! ## The runner's answers to whole requests

Requests over the joke's environment, overlay and lexicon (`EJ`, `LJ`) and the fixture pack, as the relay sends
them. Each answer is pinned by the SHA-256 of its compact JSON without its `actions_version` (`pin`), so a change to
any other member it writes is caught; the version is checked once per answer form against `Fixed.actionsVersion`
(below the pins), so raising it re-pins nothing. The members are checked by the relay's tests
(tests/test_senses_project.py, tests/test_senses_route.py). -/

def overlayJ : Json := Json.mkObj [("constants", Json.mkObj [("riddle", Json.mkObj [("verbalisation", .str "the riddle")])])]

def lexJ : Json :=
  lexiconJson ((VE.EnglishGrammar.Run.environmentId (displayJson EJ.source overlayJ)).toOption.getD "") LJ

def req (extra : List (String × Json)) (pack : String := packF.toJson.compress) : Json := Json.mkObj ([("id", .str "r"),
  ("environment", EJ.source), ("overlay", overlayJ), ("lexicon", lexJ), ("packs", Json.arr #[.str pack]),
  ("own", Json.arr #[]), ("budget", toJson workBudget)] ++ extra)

/-- An answer without the `actions_version` of its identities, the one place each answer form writes it
(`result.reading` of a run, `result.projection` of a projection); every other member is kept. -/
def withoutVersion (j : Json) : Json :=
  ["reading", "projection"].foldl (fun j form =>
    let result := j.getObjValD "result"
    match (result.getObjValD form).getObjValD "identities" with
    | .obj ids => j.setObjVal! "result" (result.setObjVal! form
        ((result.getObjValD form).setObjVal! "identities" (.obj (ids.erase "actions_version"))))
    | _ => j) j

/-- The `actions_version` an answer of `form` writes. -/
def versionOf (form : String) (j : Json) : Json :=
  (((j.getObjValD "result").getObjValD form).getObjValD "identities").getObjValD "actions_version"

/-- An answer of `form` with `v` as the `actions_version` of its identities. -/
def withVersion (form : String) (v : Json) (j : Json) : Json :=
  let result := j.getObjValD "result"
  j.setObjVal! "result" (result.setObjVal! form ((result.getObjValD form).setObjVal! "identities"
    (((result.getObjValD form).getObjValD "identities").setObjVal! "actions_version" v)))

def pin (j : Json) : String := VE.CertificateWire.sha256 (withoutVersion j).compress.toUTF8

def projectReq (lines : String) (used : List String) (pack : String := packF.toJson.compress) : Json :=
  req [("lines", .str lines), ("used", toJson used)] pack

def src (s : String) : Json := req [("source", .str s)]

def fenced (fs ids allowed : List String) (defaults : List (String × Nat) := []) : Json :=
  req ([("fences", toJson fs), ("fence_ids", toJson ids), ("reading_set_units", toJson allowed)] ++
    if defaults.isEmpty then [] else [("defaults", Json.mkObj (defaults.map fun (w, i) => (w, toJson i)))])




-- an open unit: two candidates with their identities
#guard pin (runCaseReported (src "The riddle is funny.")) == "6ee6e93e6d4c2543b1736bbe7da70ca049788800671676e213822e5fdfad6354"
-- resolved by its line
#guard pin (runCaseReported (src (lineFunny2 ++ " The riddle is funny."))) == "8c302fd926430f668bbdb2f6a7bb8a961647df85ca43901a0a9a6242ea31d483"
-- a sense fault
#guard pin (runCaseReported (src "In this document, funny means purple. The riddle is funny.")) == "8aa7234e6df92e54d69f44f1bba92872c35e84323286f05e888703a7b6a12076"
-- S2's outcome
#guard pin (runCaseReported (src "Every joke that is funny (meaning strange) is not funny.")) == "fb9e6abd68375e75c51b0e110d13523925c83a7a26f675d72e380e9e81219367"
-- an open unit beside a glossed one
#guard pin (runCaseReported (src "Both the riddle is odd and the riddle is funny (meaning strange).")) == "1fa2458b4dd847832d333f6566af2173e1ad8541bc815de939d5599933815a37"
-- an open fence without a reading set
#guard pin (runCaseReported (fenced ["The riddle is funny.\n"] ["u1"] [])) == "1b6b6d44dcc4b67a043c3acd17db11d58f3191b8dc529039fa04c3e54bd3a3bd"
-- an open fence with its reading set
#guard pin (runCaseReported (fenced ["The riddle is funny.\n"] ["u1"] ["u1"])) == "80ec199e72aa7c9fd075b2cc3fbe50ec7f6347459cd0f8039c7a2715dd4e5c53"
-- a fence that is a line
#guard pin (runCaseReported (fenced [lineFunny2 ++ "\n", "The riddle is funny.\n"] ["l", "u1"] [])) == "81a67f2d4300e05dbb5b54f6cc0250c56263203462b1900a175ab63b639fe167"
-- front-matter defaults
#guard pin (runCaseReported (fenced ["The riddle is funny.\n"] ["u1"] [] [("funny", 2)])) == "f73f2199749f63d665e84726d97815d159fc9310c59b498024810d6f2805cfb5"
-- fence identities refused
#guard pin (runCaseReported (fenced ["The riddle is funny.\n"] ["u1", "u2"] [])) == "2047a621e3c95f46bbf587bd22854141989afcd335200861aa63d0748985cb0b"
-- an unknown member refused
#guard pin (runCaseReported (req [("source", .str "The riddle is funny."), ("extra", .bool true)])) == "9d07b16a9d2073c32578e58dca75e99f1bb7df8bcc9d25b9444d70c2a3957bd9"
-- the document mode's call: no identities
#guard pin ((readCase (src "The riddle is funny.")).toOption.getD .null) == "3431251338e339e03cb19096277d4102b41476ffcf023d9e456f029268146ce4"
-- budget 0
#guard pin (runCaseReported ((src "The riddle is funny.").setObjVal! "budget" (toJson 0))) == "3b520a3ca8a86a3df1a98ab6df2acc3b8b5a509e4edb8fcfe9337b2a41330a39"
-- a projection
#guard pin (projectCaseReported (projectReq lineFunny2 ["funny"])) == "b52883a8b67fc1b86f3760ea569dbd661fe0d9d62f5bb6d25b385503e074da5b"
-- no lines
#guard pin (projectCaseReported (projectReq "" ["funny", "tells"])) == "b57e299dcbb7f22b3a60e759b23fd3264c0d4ff2da6e03e9be8c8ef66fa4d00e"
-- a fault of the lines
#guard pin (projectCaseReported (projectReq "In this document, funny means purple." ["funny"])) == "8f22518a9d293069fa4adb2a75cf1c72d0d6721a468e11037fda2f32aac69f18"
-- a repeated default
#guard pin (projectCaseReported (projectReq (lineFunny2 ++ " In this document, funny means amusing.") ["funny"])) == "78c1755c326978027727606441164e2074c5e75fe3b732e969e7e6c7dd151319"
-- a used word outside the dictionary
#guard pin (projectCaseReported (projectReq lineFunny2 ["giggle"])) == "19bdf30a4256160b6f1b8a478a4d3f4b0c6a15c1ff99c0ff226bf234ffbb19e5"
-- a used word twice
#guard pin (projectCaseReported (projectReq lineFunny2 ["funny", "funny"])) == "875f47624cc3d1af4b5b10e0702d29fb69c7eaa525a653a85d8659f91d98abe6"
-- a line that is not a preamble line
#guard pin (projectCaseReported (projectReq "The riddle is funny." ["funny"])) == "6ef218a1e4a131556f360ec8a9ee5ee5e8f7ff5011cf8c406d390dd9df4d58e1"
-- budget 0
#guard pin (projectCaseReported ((projectReq lineFunny2 ["funny"]).setObjVal! "budget" (toJson 0))) == "729f7a8122b924376131537da39db68935e5eb64f59467265da2eb7bc9d3d696"
-- an invalid dictionary
#guard pin (projectCaseReported (projectReq lineFunny2 ["funny"] (Pack.toJson ⟨"bad@1", sortsF, sensesF ++ [{ sFunny1 with word := "planetary", kinds := ["planet"] }]⟩).compress)) == "382e631e1b45c0a0dbceaa3b29650a95475f4bd166ca7997ee3b15145517200b"
-- two sorts with one letter
#guard pin (projectCaseReported ((projectReq lineFunny2 ["funny"]).setObjVal! "lexicon" (lexiconJson ((VE.EnglishGrammar.Run.environmentId (displayJson EJ.source overlayJ)).toOption.getD "") { LJ with letters := [("joke", "J"), ("person", "J")] }))) == "c1ed6b25af860fd3bb8359ed639b363b6a9c04784525a0f1c44a24b8f2ccae07"
-- an unknown member refused
#guard pin (projectCaseReported ((projectReq lineFunny2 ["funny"]).setObjVal! "extra" (.bool true))) == "ac20cd6890a736700e2d9d59c13e92fcf06f0447570c76bf7f4eb1a82f4770b8"



-- two unresolved words: choices of two senses
#guard pin (runCaseReported (src "Both the riddle is funny and the riddle is odd.")) == "f220964f1a6d2d5459ea9dfa43d730e535be2e98715895067f738c56049f23e2"
-- two units
#guard pin (runCaseReported (src "The riddle is funny. Alice tells the riddle.")) == "30a6a5ea3f23a80a75d61fc44c066b523a45262185cef8eda2e42ddf7af0caa8"
-- own senses whose kinds are the document's sorts
#guard pin (projectCaseReported ((projectReq "" ["funny", "tells"]).setObjVal! "packs" (Json.arr #[]) |>.setObjVal! "own" (Json.arr #[sFunny1.toJson, sTells1.toJson]))) == "08943366b5fe4a578e4b902d6f77ca06d5879cfffd0f3e9bec6a8553919da21c"
-- a second used word outside the dictionary
#guard pin (projectCaseReported (projectReq lineFunny2 ["funny", "giggle"])) == "19bdf30a4256160b6f1b8a478a4d3f4b0c6a15c1ff99c0ff226bf234ffbb19e5"
-- the used word outside the dictionary first
#guard pin (projectCaseReported (projectReq lineFunny2 ["giggle", "funny"])) == "19bdf30a4256160b6f1b8a478a4d3f4b0c6a15c1ff99c0ff226bf234ffbb19e5"
-- every word of the dictionary
#guard pin (projectCaseReported (projectReq "" ["funny", "odd", "tells", "deployed", "reviewed", "access"])) == "f705e96b12737c57ce9dca498666b29a834a4ebbe986557a06842b55c86fe7a4"
-- a one-character line
#guard pin (projectCaseReported (projectReq "x" ["funny"])) == "50c8b279ed22fc5d46e876ac027ba3d93f52cbdb0cfc8dbdc1fab42c05488de3"
-- a lexicon english.read refuses
#guard pin (projectCaseReported ((projectReq lineFunny2 ["funny"]).setObjVal! "lexicon" (lexiconJson ((VE.EnglishGrammar.Run.environmentId (displayJson EJ.source overlayJ)).toOption.getD "") { LJ with nouns := [("joke", "joke")] }))) == "97d9cdc7cda6f59b517a91ca091ccb4264362263ac3afec2b0efccc55a12015e"

-- The version the pins leave out, one guard per answer form: Lean's generated `Fixed.actionsVersion`, never a copy.
#guard versionOf "reading" (runCaseReported (src "The riddle is funny.")) == .str VE.EnglishGrammar.Fixed.actionsVersion
#guard versionOf "projection" (projectCaseReported (projectReq lineFunny2 ["funny"])) ==
  .str VE.EnglishGrammar.Fixed.actionsVersion
-- `withoutVersion` takes out that member and no other: put back, it is the answer again.
#guard let j := runCaseReported (src "The riddle is funny.")
  withoutVersion j != j && withVersion "reading" (versionOf "reading" j) (withoutVersion j) == j
#guard let j := projectCaseReported (projectReq lineFunny2 ["funny"])
  withoutVersion j != j && withVersion "projection" (versionOf "projection" j) (withoutVersion j) == j

/-! ## The profile list as written (`Projection.written`, `SensesOutcome.written`)

A request environment with a document layer (`judgments@0`): the reader decides without it
(`VE.Compose.decidingEnvironment`), and the environment each answer returns lists it as written. -/

def envL : Json := Json.mkObj [("language", .str "ve.core@0.2"), ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
  ("profiles", toJson ["documents@1", "judgments@0", "relational-fol@0"]), ("vocabulary", EJ.source.getObjValD "vocabulary")]

def layered (extra : List (String × Json)) : Json :=
  ((req extra).setObjVal! "environment" envL).setObjVal! "lexicon"
    (lexiconJson ((VE.EnglishGrammar.Run.environmentId (displayJson envL overlayJ)).toOption.getD "") LJ)

def profilesOf (form : String) (j : Json) : Json :=
  (((j.getObjValD "result").getObjValD form).getObjValD "environment").getObjValD "profiles"

-- the list the reader decides over differs from the request's
#guard ((VE.Compose.decidingEnvironment envL).toOption.map (·.getObjValD "profiles")) ==
  some (toJson ["documents@1", "relational-fol@0"])
-- `Projection.written`: `senses.project` returns the request's list
#guard profilesOf "projection" (projectCaseReported (layered [("lines", .str lineFunny2), ("used", toJson ["funny"])])) ==
  envL.getObjValD "profiles"
-- `SensesOutcome.written`: an identified `senses.read` answer returns the request's list
#guard profilesOf "reading" (runCaseReported (layered [("source", .str "The riddle is funny.")])) ==
  envL.getObjValD "profiles"

/-! ## The preamble lines of a source answer (plan B6): the source's sentences before the body, as written -/

def readingOf (j : Json) : Json := ((runCaseReported j).getObjValD "result").getObjValD "reading"

#guard writtenLines (lineFunny2 ++ "\n\nThe riddle is funny.") 1 == [lineFunny2]
#guard writtenLines (lineFunny2 ++ "  In this document, odd means strange.\nThe riddle is odd.") 2
  == [lineFunny2, "In this document, odd means strange."]
#guard writtenLines "The riddle is funny." 0 == []
#guard (readingOf (src (lineFunny2 ++ "\nThe riddle is funny."))).getObjValD "preamble" == toJson [lineFunny2]
#guard (readingOf (src "The riddle is funny.")).getObjValD "preamble" == toJson ([] : List String)
-- a fence request has no single source: its lines are mapped by `fences`, and there is no member
#guard ((readingOf (fenced [lineFunny2 ++ "\n", "The riddle is funny.\n"] ["l", "u1"] ["u1"])).getObjVal? "preamble").toOption.isNone

/-! ## Flip models (plan 2.6 step 7; spec 2.6 and 8.7's flip valuations of s2 and n7)

Each side of the rule: a pair the first valuation distinguishes, a pair only the exchanged one does (s2's unit 0),
a pair neither does, a form the evaluator has no case for, and an exhausted budget, which leaves the later pairs of
the answer unknown too. -/

def PJ : Projection := match project F ⟨[]⟩ EJ LJ ["funny"] with
  | .ok P => P
  | .error _ => { env := EJ, lexicon := LJ, envJson := .null, map := [] }

def cand (i : Nat) (f : EFormula) : Candidate := { choice := [("funny", i)], lines := "", formula := f, mark := true }
def funny (i : Nat) (t : ETerm) : EFormula := .pred s!"sense__funny_{i}" [t]
def riddle : ETerm := .const "riddle"
/-- s2's unit 0: `all joke (funny_2 → ¬funny_k)`. -/
def s2 (k : Nat) : EFormula := .all "joke" (.implies (funny 2 (.var 0)) (.not (funny k (.var 0))))
/-- An open unit over `funny` with candidates `cs`. -/
def openOf (cs : List Candidate) : SenseUnit :=
  { formula := none, candidates := cs, unresolved := ["funny"], after := DState.init }
/-- `n` universal quantifiers over a two-entity domain (the joke's own entity and the riddle) around `f`. -/
def deep : Nat → EFormula → EFormula
  | 0, f => f
  | n + 1, f => .all "joke" (deep n f)

/-- A flip with its model left out, for the guards on the valuation and the values; the model's own guards follow. -/
def _root_.VE.Senses.Flip.bare : Flip → Flip
  | .distinguished on a b _ => .distinguished on a b ⟨[], [], []⟩
  | f => f
def dist (on : List String) (a b : Bool) : Flip := .distinguished on a b ⟨[], [], []⟩
def bareRows (rows : List ((Nat × Nat × Nat) × Flip)) : List ((Nat × Nat × Nat) × Flip) :=
  rows.map fun (k, f) => (k, f.bare)

-- the first valuation distinguishes the pair (n7's form, negated)
#guard (flipPair PJ (cand 1 (.not (funny 1 riddle))) (cand 2 (.not (funny 2 riddle))) 0).1.bare
  == dist ["sense__funny_1"] false true
-- only the exchanged valuation distinguishes it: s2's unit 0, `sense__funny_2` true alone, first true, second false
#guard (flipPair PJ (cand 1 (s2 1)) (cand 2 (s2 2)) 0).1.bare == dist ["sense__funny_2"] true false
-- neither does: the two senses only under a conjunct both make false
#guard (flipPair PJ (cand 1 (.and (funny 1 riddle) .bottom)) (cand 2 (.and (funny 2 riddle) .bottom)) 0).1
  == .undistinguished
-- a comparison is outside the evaluator: unknown, no work spent
#guard flipPair PJ (cand 1 (.lt (.num 0) (.num 1))) (cand 2 (funny 2 riddle)) 7 == (.unknown, 7)
-- an exhausted budget is unknown, and leaves none for the next pair of the answer
#guard (flipPair PJ (cand 1 (.and (funny 1 riddle) (deep 21 (funny 1 (.var 0))))) (cand 2 (funny 2 riddle)) 0)
  == (.unknown, VE.Limits.maxEvaluations)
#guard (flipsOf PJ [openOf [cand 1 (.and (funny 1 riddle) (deep 21 (funny 1 (.var 0)))), cand 2 (funny 2 riddle)],
  openOf [cand 1 (funny 1 riddle), cand 2 (funny 2 riddle)]]).map (·.2) == [.unknown, .unknown]
-- the same two units within the budget: one row per pair, in order
#guard bareRows (flipsOf PJ [openOf [cand 1 (deep 3 (funny 1 (.var 0))), cand 2 (funny 2 riddle),
  cand 3 (funny 1 riddle)], openOf [cand 1 (funny 1 riddle), cand 2 (funny 2 riddle)]]) ==
  [((0, 0, 1), dist ["sense__funny_1"] true false), ((0, 0, 2), .undistinguished),
   ((0, 1, 2), dist ["sense__funny_2"] true false), ((1, 0, 1), dist ["sense__funny_1"] true false)]

-- the model in the model wire form's table: every sort with its own entity, every constant (one the formulas do not
-- name is its sort's entity), every predicate; the sense made true holds of every tuple of its sorts' entities
#guard (flipPair PJ (cand 1 (s2 1)) (cand 2 (s2 2)) 0).1 == .distinguished ["sense__funny_2"] true false
  { domains := [("joke", ["joke"]), ("person", ["person"]), ("service", ["service"]), ("number", ["number"]),
      ("principal", ["principal"]), ("resource", ["resource"])],
    constants := [("alice", "person"), ("riddle", "joke")],
    relations := [("sense__funny_1", []), ("sense__funny_2", [["joke"]])] }
-- the values are the formulas' truth in that model (`flipValues_sound`), here read back by `Formula.eval`
#guard match (flipPair PJ (cand 1 (s2 1)) (cand 2 (s2 2)) 0).1, formulaCore (s2 1), formulaCore (s2 2) with
  | .distinguished _ a b m, some fc, some fd => a == fc.eval m.finite [] && b == fd.eval m.finite []
  | _, _, _ => false
/-- The joke's projection with `sense__funny_1` over `n` jokes: `2 ^ n` tuples of the joke's entity and the riddle. -/
def wide (n : Nat) : Projection :=
  { PJ with env := { PJ.env with predicates := PJ.env.predicates.map fun p =>
      if p.name == "sense__funny_1" then { p with args := List.replicate n "joke" } else p } }
-- a model over `maxTuples` tuples is unknown, the work kept; one within it is written
#guard flipModelOf (wide 17) [funny 1 riddle] ["sense__funny_1"] == none && 2 ^ 17 > VE.Limits.maxTuples
#guard ((flipModelOf (wide 16) [funny 1 riddle] ["sense__funny_1"]).map fun m =>
  ((List.lookup "sense__funny_1" m.relations).getD []).length) == some (2 ^ 16)
#guard flipPair (wide 17) (cand 1 (funny 1 riddle)) (cand 2 (funny 2 riddle)) 5 == (.unknown, 5)
/-- The joke's projection with both senses of `funny` over `n` jokes. -/
def wideBoth (n : Nat) : Projection :=
  { PJ with env := { PJ.env with predicates := PJ.env.predicates.map fun p => { p with args := List.replicate n "joke" } } }
-- the limit counts every sense made true: two of `2 ^ 16` tuples each are over it, either alone within it
#guard flipModelOf (wideBoth 16) [funny 1 riddle] ["sense__funny_1", "sense__funny_2"] == none &&
  2 * 2 ^ 16 > VE.Limits.maxTuples && 2 ^ 16 ≤ VE.Limits.maxTuples
/-- The joke's projection with `sense__funny_1` over five jokes and five persons, and three more jokes. -/
def atTuples : Projection := { PJ with env := { PJ.env with
    constants := PJ.env.constants ++ ["j1", "j2", "j3"].map fun c => { name := c, sort := "joke" },
    predicates := PJ.env.predicates.map fun p => if p.name == "sense__funny_1" then
      { p with args := List.replicate 5 "joke" ++ List.replicate 5 "person" } else p } }
/-- A formula naming four jokes and alice: five entities of the joke, two of the person. -/
def namesFive : EFormula :=
  .and (.eq (.const "riddle") (.const "j1")) (.and (.eq (.const "j2") (.const "j3")) (.eq (.const "alice") (.const "alice")))
-- exactly `maxTuples` tuples, `5 ^ 5 * 2 ^ 5`, are within the limit
#guard 5 ^ 5 * 2 ^ 5 == VE.Limits.maxTuples && ((flipModelOf atTuples [namesFive] ["sense__funny_1"]).map fun m =>
  ((List.lookup "sense__funny_1" m.relations).getD []).length) == some VE.Limits.maxTuples
-- a constant of every sort of the projection, the last included, is in the table
#guard ((flipModelOf { PJ with env := { PJ.env with constants := PJ.env.constants ++ [{ name := "vault", sort := "resource" }] } }
  [funny 1 riddle] ["sense__funny_1"]).map (·.constants)) == some [("alice", "person"), ("riddle", "riddle"), ("vault", "resource")]
-- a distinguishing model on the wire carries its table in the model wire form
#guard flipJson 0 ((0, 0, 1), .distinguished ["p"] true false ⟨[("joke", ["joke"])], [], [("p", [["joke"]])]⟩) ==
  Json.mkObj [("sentence", toJson 0), ("first", toJson 0), ("second", toJson 1), ("status", .str "distinguished"),
    ("true", toJson ["p"]), ("values", Json.arr #[.bool true, .bool false]),
    ("model", Json.mkObj [("complete", .bool true), ("domains", Json.mkObj [("joke", toJson ["joke"])]),
      ("constants", Json.mkObj []), ("relations", Json.mkObj [("p", toJson [["joke"]])])])]

-- the pairs of `n` candidates, each once, in order
#guard candidatePairs 3 == [(0, 1), (0, 2), (1, 2)] && candidatePairs 1 == [] && candidatePairs 0 == []
-- the evaluator's forms, each arm; a number is outside it
#guard formulaCore (.and .top (.or (.ex "joke" (.eq (.var 0) riddle)) (.implies .bottom (.not
    (.all "joke" (.pred "p" [.var 0, riddle])))))) == some (.and .top (.or (.ex "joke" (.eq (.var 0) (.const "riddle")))
    (.implies .bottom (.not (.all "joke" (.binary "p" (.var 0) (.const "riddle"))))))) &&
  formulaCore (funny 1 (.num 0)) == none && formulaCore (.pred "p" [riddle, riddle, riddle]) == none
-- a pair no valuation separates, and one outside the evaluator, on the wire
#guard flipJson 2 ((1, 0, 1), .unknown) == Json.mkObj [("sentence", toJson 3), ("first", toJson 0),
    ("second", toJson 1), ("status", .str "unknown")]
#guard flipJson 0 ((0, 0, 1), .undistinguished) == Json.mkObj [("sentence", toJson 0), ("first", toJson 0),
    ("second", toJson 1), ("status", .str "undistinguished")]

/-- The joke's projection over two words, with a second joke constant `gag` declared first. -/
def PJ2 : Projection := match project F ⟨[]⟩ EJ LJ ["funny", "odd"] with
  | .ok P => { P with env := { P.env with constants := { name := "gag", sort := "joke" } :: P.env.constants } }
  | .error _ => PJ
def odd (i : Nat) (t : ETerm) : EFormula := .pred s!"sense__odd_{i}" [t]
def cand2 (f o : Nat) (φ : EFormula) : Candidate :=
  { choice := [("funny", f), ("odd", o)], lines := "", formula := φ, mark := true }

-- every sense the first chooses and the second does not is true, in the projection's order
#guard flipOn PJ2 (cand2 1 1 .top) (cand2 2 2 .top) == ["sense__funny_1", "sense__odd_1"]
#guard flipOn PJ2 (cand2 1 1 .top) (cand2 1 2 .top) == ["sense__odd_1"]
#guard (flipPair PJ2 (cand2 1 1 (.and (funny 1 riddle) (odd 1 riddle))) (cand2 2 2 (.and (funny 2 riddle) (odd 2 riddle)))
  0).1.bare == dist ["sense__funny_1", "sense__odd_1"] true false
-- only the exchanged valuation separates them, and the second candidate reads both of its senses
#guard (flipPair PJ2 (cand2 1 1 .bottom) (cand2 2 2 (.and (funny 2 riddle) (.ex "number" (odd 2 (.var 0))))) 0).1.bare
  == dist ["sense__funny_2", "sense__odd_2"] false true
-- every constant of both formulas is an entity of its sort's domain, each its own: alice is not the person's own
#guard (flipPair PJ2 (cand 1 (.and (funny 1 riddle) (.ex "person" (.not (.eq (.var 0) (.const "alice"))))))
  (cand 2 (funny 2 (.const "gag"))) 0).1.bare == dist ["sense__funny_1"] true false
#guard match (flipPair PJ2 (cand 1 (.and (funny 1 riddle) (.ex "person" (.not (.eq (.var 0) (.const "alice"))))))
    (cand 2 (funny 2 (.const "gag"))) 0).1 with
  | .distinguished _ _ _ m => m.domains.take 2 == [("joke", ["gag", "joke", "riddle"]), ("person", ["alice", "person"])] &&
      m.constants == [("gag", "gag"), ("alice", "alice"), ("riddle", "riddle")]
  | _ => false
#guard (flipPair PJ2 (cand 1 (.and (funny 1 riddle) (.and (.ex "joke" (.eq (.var 0) (.const "gag")))
    (.ex "joke" (.eq (.var 0) riddle))))) (cand 2 (funny 2 riddle)) 0).1.bare == dist ["sense__funny_1"] true false
#guard (flipPair PJ2 (cand 1 (.ex "joke" (.not (.eq (.var 0) riddle)))) (cand 2 (.all "joke" (.eq (.var 0) riddle))) 0).1.bare
  == dist ["sense__funny_1"] true false

/-- `deep i (funny_1 x)`, or `top` for `0`: true under `sense__funny_1`, with work `2 ^ (i + 1) - 1`. -/
def piece : Nat → EFormula
  | 0 => .top
  | i => deep i (funny 1 (.var 0))
/-- The pieces of `is`, conjoined: one more unit of work per conjunction. -/
def chain : List Nat → EFormula
  | [] => .top
  | [i] => piece i
  | i :: is => .and (piece i) (chain is)
/-- A pair whose flip model takes exactly `maxEvaluations` work: `2 + Σ 2 ^ (i + 1)` = 1,000,000. -/
def atLimit : Candidate × Candidate :=
  (cand 1 (.and (funny 1 riddle) (chain [0, 1, 2, 3, 4, 8, 13, 15, 16, 17, 18])), cand 2 (funny 2 riddle))
-- at the limit from no work: the model; one unit of work earlier spent: unknown
#guard bareRows (flipsOf PJ [openOf [atLimit.1, atLimit.2]]) == [((0, 0, 1), dist ["sense__funny_1"] true false)]
#guard (fun (f, w) => (Flip.bare f, w)) (flipPair PJ atLimit.1 atLimit.2 0) ==
  (dist ["sense__funny_1"] true false, VE.Limits.maxEvaluations)
#guard flipPair PJ atLimit.1 atLimit.2 1 == (.unknown, VE.Limits.maxEvaluations)

end VE.Senses.RunExamples
