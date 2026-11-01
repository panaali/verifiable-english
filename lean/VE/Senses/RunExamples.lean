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
them. Each answer is pinned by the SHA-256 of its compact JSON (`pin`), so a change to any member it writes is
caught; the members are checked by the relay's tests (tests/test_senses_project.py, tests/test_senses_route.py). -/

def overlayJ : Json := Json.mkObj [("constants", Json.mkObj [("riddle", Json.mkObj [("verbalisation", .str "the riddle")])])]

def lexJ : Json :=
  lexiconJson ((VE.EnglishGrammar.Run.environmentId (displayJson EJ.source overlayJ)).toOption.getD "") LJ

def req (extra : List (String × Json)) (pack : String := packF.toJson.compress) : Json := Json.mkObj ([("id", .str "r"),
  ("environment", EJ.source), ("overlay", overlayJ), ("lexicon", lexJ), ("packs", Json.arr #[.str pack]),
  ("own", Json.arr #[]), ("budget", toJson workBudget)] ++ extra)

def pin (j : Json) : String := VE.CertificateWire.sha256 j.compress.toUTF8

def projectReq (lines : String) (used : List String) (pack : String := packF.toJson.compress) : Json :=
  req [("lines", .str lines), ("used", toJson used)] pack

def src (s : String) : Json := req [("source", .str s)]

def fenced (fs ids allowed : List String) (defaults : List (String × Nat) := []) : Json :=
  req ([("fences", toJson fs), ("fence_ids", toJson ids), ("reading_set_units", toJson allowed)] ++
    if defaults.isEmpty then [] else [("defaults", Json.mkObj (defaults.map fun (w, i) => (w, toJson i)))])




-- an open unit: two candidates with their identities
#guard pin (runCaseReported (src "The riddle is funny.")) == "9f64a8a5899cd6a359a87085dc9b6069cb4ae88a0875fadf3d26c055fe91f46e"
-- resolved by its line
#guard pin (runCaseReported (src (lineFunny2 ++ " The riddle is funny."))) == "a0e3cd25e8184c6a03b328a7f3d7cd554261a9c73aa78a1125bdf68159623ef2"
-- a sense fault
#guard pin (runCaseReported (src "In this document, funny means purple. The riddle is funny.")) == "95f53c1f0395ccf75fc3c669473b6ef312fdad77607b8900c047a4a4ef4a85d2"
-- S2's outcome
#guard pin (runCaseReported (src "Every joke that is funny (meaning strange) is not funny.")) == "feec3bb464919db664bec1018709bb45b5722ab78ea43711ecc19c365abe3c66"
-- an open unit beside a glossed one
#guard pin (runCaseReported (src "Both the riddle is odd and the riddle is funny (meaning strange).")) == "3da13dfcdf8454b6b7fa702277876882a6ac8877b3d979d28f65bf9ff43c0ac9"
-- an open fence without a reading set
#guard pin (runCaseReported (fenced ["The riddle is funny.\n"] ["u1"] [])) == "1b6b6d44dcc4b67a043c3acd17db11d58f3191b8dc529039fa04c3e54bd3a3bd"
-- an open fence with its reading set
#guard pin (runCaseReported (fenced ["The riddle is funny.\n"] ["u1"] ["u1"])) == "cf08c4889d8edae40c0cd17c99f25d733ae3e29d81648aeb86d938ceb507e7e8"
-- a fence that is a line
#guard pin (runCaseReported (fenced [lineFunny2 ++ "\n", "The riddle is funny.\n"] ["l", "u1"] [])) == "b4b10de5f3e1300995997b9fd37bfb26a8243a5a207a2e760fb588d910fb525d"
-- front-matter defaults
#guard pin (runCaseReported (fenced ["The riddle is funny.\n"] ["u1"] [] [("funny", 2)])) == "9765f5d3e58ffb7632d0ad4651d47128a59b87ffc91685c23e3f10c09b212789"
-- fence identities refused
#guard pin (runCaseReported (fenced ["The riddle is funny.\n"] ["u1", "u2"] [])) == "2047a621e3c95f46bbf587bd22854141989afcd335200861aa63d0748985cb0b"
-- an unknown member refused
#guard pin (runCaseReported (req [("source", .str "The riddle is funny."), ("extra", .bool true)])) == "9d07b16a9d2073c32578e58dca75e99f1bb7df8bcc9d25b9444d70c2a3957bd9"
-- the document mode's call: no identities
#guard pin ((readCase (src "The riddle is funny.")).toOption.getD .null) == "3431251338e339e03cb19096277d4102b41476ffcf023d9e456f029268146ce4"
-- budget 0
#guard pin (runCaseReported ((src "The riddle is funny.").setObjVal! "budget" (toJson 0))) == "3b520a3ca8a86a3df1a98ab6df2acc3b8b5a509e4edb8fcfe9337b2a41330a39"
-- a projection
#guard pin (projectCaseReported (projectReq lineFunny2 ["funny"])) == "243b5780ef71c06c02a8b654600941833eea188edf5fe75aa0e9f1d23ed17a6b"
-- no lines
#guard pin (projectCaseReported (projectReq "" ["funny", "tells"])) == "3a4d8c1001f5909f7b29ed762aaa76f8cf771b462efc4f645070aabc7a36cd79"
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
#guard pin (runCaseReported (src "Both the riddle is funny and the riddle is odd.")) == "fca2245f33b708c9c19b6a5bb39e8c4c7bfe3b44429bb9c3732ca2bfe37e0e07"
-- two units
#guard pin (runCaseReported (src "The riddle is funny. Alice tells the riddle.")) == "b25cd62066f0e5abcc48fa1ef608009edc6466fe0a7e3d14294c89d950537ac3"
-- own senses whose kinds are the document's sorts
#guard pin (projectCaseReported ((projectReq "" ["funny", "tells"]).setObjVal! "packs" (Json.arr #[]) |>.setObjVal! "own" (Json.arr #[sFunny1.toJson, sTells1.toJson]))) == "1fbb715fbb7d2a66a47e7bbc369aa8c7379c3df24178307e23ac83e9cea3c9d0"
-- a second used word outside the dictionary
#guard pin (projectCaseReported (projectReq lineFunny2 ["funny", "giggle"])) == "19bdf30a4256160b6f1b8a478a4d3f4b0c6a15c1ff99c0ff226bf234ffbb19e5"
-- the used word outside the dictionary first
#guard pin (projectCaseReported (projectReq lineFunny2 ["giggle", "funny"])) == "19bdf30a4256160b6f1b8a478a4d3f4b0c6a15c1ff99c0ff226bf234ffbb19e5"
-- every word of the dictionary
#guard pin (projectCaseReported (projectReq "" ["funny", "odd", "tells", "deployed", "reviewed", "access"])) == "7021bfea7953f20fbab75ac58db3d3749209c3f6879da8c16dd1224ceabc264b"
-- a one-character line
#guard pin (projectCaseReported (projectReq "x" ["funny"])) == "50c8b279ed22fc5d46e876ac027ba3d93f52cbdb0cfc8dbdc1fab42c05488de3"
-- a lexicon english.read refuses
#guard pin (projectCaseReported ((projectReq lineFunny2 ["funny"]).setObjVal! "lexicon" (lexiconJson ((VE.EnglishGrammar.Run.environmentId (displayJson EJ.source overlayJ)).toOption.getD "") { LJ with nouns := [("joke", "joke")] }))) == "97d9cdc7cda6f59b517a91ca091ccb4264362263ac3afec2b0efccc55a12015e"

end VE.Senses.RunExamples
