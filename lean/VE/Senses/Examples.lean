import VE.Senses.Fixtures

/-! The acceptance fixtures of docs/spec/senses.md section 8, as `#guard` checks on the built definitions.

Every reading row is the *as merged* column of the specification: the reader uses S2's grammar as merged,
without request R3 (6.2). The rows that need R3 (the *with R3* column of 8.5, s1 and s2 with R3, s13, m1
and m2) wait for the DRI's decision; their merged values are checked here where the specification gives
them. A difference between this file and a computed row of section 8 is a finding against the
specification or the build, decided before the row is changed (spec 12).
-/

namespace VE.Senses.Examples
open Lean VE.Grammar VE.EnglishGrammar VE.Senses VE.Senses.Fixtures

/-! ## 8.1 Dictionary (d) -/

#guard F.failures [] == []                                                                       -- d1
#guard (Fwith (swap sFunny2 { sFunny2 with gloss := "amusing" })).failures [] ==                 -- d2
  [("W2", "funny", "the word funny has two senses with the gloss amusing"),
   ("W6", "funny", "the wording {0} is funny (meaning amusing) belongs to two senses of funny")]
#guard (Fwith (swap sOdd1 { sOdd1 with gloss := "odd" })).failures [] ==                         -- d3
  [("W2", "odd", "the gloss of odd is the word itself")]
#guard (Fwith (swap sFunny2 { sFunny2 with gloss := "deployed" })).failures [] ==                -- d4
  [("W2", "funny", "the gloss deployed of funny is itself a word of the vocabulary")]
#guard (Fwith (swap sFunny1 { sFunny1 with wording := "{0} is amusing" })).failures [] ==         -- d5
  [("W3", "funny", "the wording {0} is amusing of funny does not contain funny exactly once")]
#guard (Fwith (swap sTells1 { sTells1 with wording := "{1} tells {0}" })).failures [] ==          -- d6
  [("W3", "tells", "the wording {1} tells {0} of tells does not begin with its first place")]
#guard (Fwith (swap sFunny1 { sFunny1 with kinds := ["thing"] })).failures [] ==                  -- d7
  [("W4", "funny", "funny applies to thing, which is not a kind of the pack fixtures@1")]
#guard (Fwith (swap sFunny1 { sFunny1 with negative := some "{0} is not funny" })).failures [] == -- d8
  [("W5", "funny", "funny declares a negative wording although its negative is automatic")]
#guard (Fwith (swap sAccess1 { sAccess1 with negative := none })).failures [] == []               -- d9
#guard (Fwith (swap sAccess1 { sAccess1 with negative := some "{0} cannot access {1}" })).failures [] == []  -- d10
#guard (Fwith fun l => swap sFunny1 { sFunny1 with wording := "{0} is funny weird" } l ++ [sWeird]).failures [] ==
  [("W6", "funny", "the wording {0} is funny weird belongs to both funny and weird")]           -- d11
#guard (⟨[packF, ⟨"other@1", [srt "joke" "J"], [{ sFunny1 with gloss := "droll" }]⟩], []⟩ : Dictionary).failures [] ==
  [("W1", "funny", "the word funny is in two packs: fixtures@1 and other@1")]                   -- d12
#guard (⟨[packF], [{ sFunny1 with gloss := "droll" }]⟩ : Dictionary).failures ["joke"] ==
  [("W1", "funny", "the document gives its own sense to funny, a word of the pack fixtures@1")] -- d13
#guard (Fwith (swap sFunny1 { sFunny1 with wording := "{0} is funny (meaning amusing)" })).failures [] ==
  [("W3", "funny", "the wording {0} is funny (meaning amusing) of funny contains a bracket or a full stop")]  -- d14
#guard (Fwith fun l => l ++ [⟨"every", 1, "total", "each one", ["joke"], "{0} is every", none⟩]).failures [] ==
  [("W1", "every", "every is a reserved word")]                                                 -- d15
#guard (Fwith (swap sFunny2 { sFunny2 with index := 3 })).failures [] ==                          -- d16
  [("W1", "funny", "the senses of funny are not numbered from 1, each number once")]
#guard (Fwith fun l => swap sFunny2 { sFunny2 with wording := "{0} is funny weird" } l ++ [sWeird]).failures [] ==
  [("W6", "funny", "the wording {0} is funny weird belongs to both funny and weird")]           -- d17
#guard Fn.failures [] == []                                                                      -- d18
#guard (Fwith id (sortsF.map fun t => if t.name == "joke" then srt "joke" "P" else t)).failures [] ==
  [("W4", "joke", "the label letter P is given to two kinds: joke and person")]                 -- d19
#guard (Fwith id (sortsF.map fun t => if t.name == "joke" then srt "joke" "j" else t)).failures [] ==
  [("W4", "fixtures@1", "the label letter j of the kind joke is not one capital letter")]       -- d20
#guard (Fwith fun l => l ++ [⟨"gives", 1, "hands over", "hands the joke to someone", ["person", "joke", "person"],
    "{0} gives {1} to {2}", none⟩]).failures [] ==
  [("W4", "gives", "gives does not apply to one or two kinds")]                                 -- d21
#guard (Fwith id (sortsF ++ [⟨"gag", "joke", "jokes", "A gag.", "G"⟩])).failures [] ==
  [("W4", "gag", "the noun joke is given to two kinds: gag and joke")]                          -- d22
def sDry : Sense := ⟨"dry", 1, "deadpan", "told without expression", ["remark"], "{0} is dry", none⟩
#guard (⟨[packF], [sDry]⟩ : Dictionary).failures ["remark"] == []                                -- d23
#guard (⟨[packF], [sDry]⟩ : Dictionary).failures [] ==
  [("W4", "dry", "dry applies to remark, which is not a kind of the document or of its packs")]
#guard (Fwith (swap sFunny1 { sFunny1 with wording := "{0} is funny in this document" })).failures [] ==
  [("W7", "funny", "{0} is funny in this document contains in this document")]                  -- d24
-- d25: `glossed_negative`'s equation, on two fixture senses and five malformed ones
#guard [sFunny1, sFunny2, { sFunny1 with word := "is", wording := "{0} is is" },
    { sFunny1 with word := "not", wording := "{0} is not" }, { sFunny1 with word := "{0}", wording := "{0} is {0}" },
    { sFunny1 with word := "a b", wording := "{0} is a b" }, { sFunny1 with word := "", wording := "{0} is " }].all
  fun s => s.isSimpleAdjective && negativeTemplate (s.glossed s.wording) 1 == some (s.glossed ("{0} is not " ++ s.word))
#guard Fd.failures [] ==                                                                         -- d26
  [("W6", "near", "the wording {0} is near, in the sense of beside bob belongs to two senses of near")]
-- d27: each a separate change to `F`, each one failure
def long (n : Nat) : String := String.mk (List.replicate n 'a')
#guard ([srt "every" "G", srt "x1" "G", srt "sense__joke" "G", { srt "gag" "G" with name := "Joke" },
    ⟨"gag", "gag", "gags", "", "G"⟩].map fun t => ((Fwith id (sortsF ++ [t])).failures []).map (·.2.2)) ==
  [["the kind name every is reserved"], ["the kind name x1 is reserved"], ["the kind name sense__joke is reserved"],
   ["the kind name Joke is not lower-case letters, digits and underscores beginning with a letter, at most sixty-four in all"],
   ["the kind gag has no description"]]
#guard ((Fwith (swap sFunny1 { sFunny1 with description := "" })).failures []) ==
  [("W4", "funny", "a sense of funny has no description")]
#guard ((Fwith (swap sFunny2 { sFunny2 with gloss := long 51 })).failures []).map (·.1) == ["W2"]
#guard ((Fwith (swap sFunny2 { sFunny2 with gloss := long 50 })).failures []) == []
#guard ((Fwith (swap sFunny1 { sFunny1 with wording := "{0} is funny " ++ " ".intercalate (List.replicate 52 "abcd") })).failures []).map
  (·.2.2.takeRight 61) == ["gives a form longer than two hundred and fifty-six characters"]
#guard ((Fwith (swap sFunny1 { sFunny1 with wording := "{0} is funny " ++ " ".intercalate (List.replicate 40 "abcd") })).failures []) == []
-- a sort name at the identifier limit, and one past it
#guard ((Fwith id (sortsF ++ [srt (long 64) "G"])).failures []) == []
#guard ((Fwith id (sortsF ++ [srt (long 65) "G"])).failures []).map (·.1) == ["W4"]

-- the forms of 2.3
#guard sFunny2.decoratedForms ==
  ["{0} is funny (meaning strange)", "{0} is funny, in the sense of strange,", "{0} is funny, in the sense of strange",
   "{0} is not funny (meaning strange)", "{0} is not funny, in the sense of strange,",
   "{0} is not funny, in the sense of strange"]
#guard sTells1.selectedWording false == "{0} tells (meaning says aloud) {1}"
#guard sTells1.selectedNegative false == some "{0} does not tell (meaning says aloud) {1}"
#guard sAccess1.selectedNegative false == some "{0} may not access (meaning read) {1}"
#guard (sFunny1.aliases true).length == 6 && (sFunny1.aliases false).length == 4 && (sTells1.aliases true).length == 6
#guard sensesF.map (·.headwordTokens) ==
  [["funny"], ["funny"], ["odd"], ["odd"], ["tells", "tell"], ["deployed"], ["reviewed"], ["reviewed"], ["access"]]

/-! ## 8.3 Preamble (a) -/

#guard (preambleGrammar F).wf && terminatorFree (preambleGrammar F) && (preambleGrammar F).rules.size == 9
#guard preIs F "In this document, funny means amusing." workBudget (.ok (⟨[("funny", 1)]⟩, 1))         -- a1
#guard preIs F "In this document, funny means amusing. In this document, reviewed means rated." workBudget
  (.ok (⟨[("funny", 1), ("reviewed", 2)]⟩, 2))                                                      -- a2
#guard preIs F "In this document, funny means amusing. In this document, funny means strange." workBudget
  (.error (.repeatedDefault 1 "funny"))                                                             -- a3
#guard preIs F "In this document, purple means amusing." workBudget (.error (.unknownWord 0 "purple"))  -- a4
#guard preIs F "In this document, funny means purple." workBudget (.error (.unknownGloss 0 "funny" "purple"))  -- a5
#guard preIs F "In this document, tells means says aloud." workBudget (.ok (⟨[("tells", 1)]⟩, 1))   -- a6
#guard unneeded F ⟨[("tells", 1)]⟩ == ["tells"] && unneeded F ⟨[("funny", 1)]⟩ == []
#guard preIs F "in this document , funny means amusing." workBudget (.ok (⟨[]⟩, 0))                 -- a7
#guard rs F EJ LJ "in this document , funny means amusing." == .stopped 0 .none
#guard preIs F "The riddle is funny. In this document, funny means amusing." workBudget (.error (.preambleLate 1))  -- a8
#guard preIs F "In this document, Funny means Amusing." workBudget (.ok (⟨[("funny", 1)]⟩, 1))      -- a9
#guard Assignment.lines F ⟨[("funny", 1), ("reviewed", 2)]⟩ ==                                     -- a10
  "In this document, funny means amusing.\nIn this document, reviewed means rated."
#guard preIs F (Assignment.lines F ⟨[("funny", 1), ("reviewed", 2)]⟩) workBudget (.ok (⟨[("funny", 1), ("reviewed", 2)]⟩, 2))
#guard preIs F (Assignment.lines F ⟨[("funny", 1), ("reviewed", 2)]⟩) 0 (.error (.preambleBudget 0))  -- a11
#guard preIs F lineFunny 454 (.error (.preambleBudget 0)) && preIs F lineFunny 455 (.ok (⟨[("funny", 1)]⟩, 1))
#guard preIs F "In this document, funny is amusing." workBudget (.error (.malformedPreamble 0))     -- a12
#guard preIs F "In this document funny means amusing." workBudget (.ok (⟨[]⟩, 0))                  -- a13
#guard preIs F "In that document, funny means amusing." workBudget (.ok (⟨[]⟩, 0))                 -- a14
#guard ["IN THIS DOCUMENT, funny means amusing.", "In this document,funny means amusing.",          -- a15
    "In this document, funny Means amusing.", "In this document, funny means."].all fun s =>
  preIs F s workBudget (.error (.malformedPreamble 0))
#guard preIs F "In this document, funny means amusing strange." workBudget
  (.error (.unknownGloss 0 "funny" "amusing strange"))                                              -- a16
#guard rs F EJ LJ lineFunny == .lexical .emptyDocument                                             -- a17
-- the shape test, both directions
#guard preambleShaped (sentsOf "In this document, funny means amusing.").head!
#guard preambleShaped (sentsOf "IN THIS DOCUMENT, funny means amusing.").head!
#guard !preambleShaped (sentsOf "in this document , funny means amusing.").head!
#guard !preambleShaped (sentsOf "In this document funny means amusing.").head!
#guard !preambleShaped (sentsOf "In that document, funny means amusing.").head!

/-! ## 8.4 Projection (j) -/

#guard LJ.valid EJ {}
-- j1: the predicates, the aliases and the lexicon
#guard match project F A1 EJ LJ ["funny", "tells"] with
  | .ok P => P.lexicon.valid P.env {} &&
    (P.env.predicates.map fun p => (p.name, p.wording, p.negative)) ==
      [("sense__funny_1", some "{0} is funny", some "{0} is not funny"),
       ("sense__funny_2", some "{0} is funny (meaning strange)", some "{0} is not funny (meaning strange)"),
       ("sense__tells_1", some "{0} tells {1}", some "{0} does not tell {1}")] &&
    P.env.forms.aliases.length == 16 &&
    (P.env.forms.aliases.filter (·.1 == "sense__funny_1")).length == 6 &&
    (P.env.forms.aliases.filter (·.1 == "sense__funny_2")).length == 4 &&
    (P.env.forms.aliases.filter (·.1 == "sense__tells_1")).length == 6 &&
    (P.env.forms.aliases.filter (·.2.2)).length == 8 &&
    P.lexicon.letters == [("joke", "J"), ("number", "N"), ("person", "P"), ("principal", "R"), ("resource", "Q"),
      ("service", "S")] &&
    P.lexicon.spellings == LJ.spellings
  | .error _ => false
-- j2: no default, both `funny` senses glossed with four aliases each
#guard match project F ⟨[]⟩ EJ LJ ["funny", "tells"] with
  | .ok P => P.lexicon.valid P.env {} &&
    (P.lexicon.wordings.filter (·.1.startsWith "sense__funny")).map (·.2) ==
      ["{0} is funny (meaning amusing)", "{0} is funny (meaning strange)"] &&
    (P.env.forms.aliases.filter (·.1 == "sense__funny_1")).length == 4 &&
    (P.env.forms.aliases.filter (·.1 == "sense__funny_2")).length == 4
  | .error _ => false
-- j3: `tells` alone
#guard match project F A1 EJ LJ ["tells"] with
  | .ok P => P.lexicon.valid P.env {} && P.map.map (·.1) == ["sense__tells_1"]
  | .error _ => false
-- j4: `access` with its declared negative, fixed by the projection and absent from the environment JSON
#guard match project F A1 EJ LJ ["funny", "tells", "access"] with
  | .ok P => P.lexicon.valid P.env {} &&
    (P.env.predicates.find? (·.name == "sense__access_1")).map (·.negative) == some none &&
    P.env.forms.negatives == [("sense__access_1", "{0} may not access {1}")] &&
    P.lexicon.negatives.lookup "sense__access_1" == some "{0} may not access {1}" &&
    ((P.envJson.getObjValD "vocabulary").getObjValD "predicates").getObjValD "sense__access_1" ==
      Json.mkObj [("arguments", toJson ["principal", "resource"]), ("description", .str "may read the resource"),
        ("verbalisation", .str "{0} may access {1}")]
  | .error _ => false
/-- A projection's JSON, lexicon and aliases, compared as text. -/
def lexSummary (P : Except SenseFault Projection) : String :=
  match P with
  | .ok P => P.envJson.compress ++ toString (repr P.lexicon) ++ toString (repr P.env.forms.aliases)
  | .error f => toString (repr f)
-- j5: a line for a word with one sense changes nothing
#guard lexSummary (project F A1 EJ LJ ["funny", "tells", "access"]) ==
  lexSummary (project F ⟨[("funny", 1), ("access", 1)]⟩ EJ LJ ["funny", "tells", "access"])
-- j6, j6b
#guard LJ6.valid EJ6 {} && projFault (project F A1 EJ6 LJ6 ["funny", "tells"]) ==
  some (.collision "predicate" "funny" "sense__funny_1")
#guard projFault (project F ⟨[]⟩ EJ6 LJ6 ["funny", "tells"]) == none
-- j7
#guard LJ7.valid EJ7 {} && match project F A1 EJ7 LJ7 ["funny", "tells"] with
  | .ok P => P.lexicon.valid P.env {} &&
    ReadExamples.rd P.env P.lexicon "The riddle is funny (meaning strange)." == ReadExamples.ok1 (u "sense__funny_2" "riddle") &&
    ReadExamples.rd P.env P.lexicon "The riddle is strange." == ReadExamples.ok1 (u "peculiar" "riddle")
  | .error _ => false
-- j8 (the Lean half): the stored environment JSON, read by S2 alone with the declared wordings and no alias
#guard match project F A1 EJ LJ ["funny", "tells"] with
  | .ok P =>
    let E := ReadExamples.env P.envJson [("riddle", "the riddle")]
    let L : Lexicon := { P.lexicon with aliases := [] }
    L.valid E {} && ReadExamples.rd E L "The riddle is funny (meaning strange). Alice tells the riddle. The riddle is not funny." ==
      .ok [(u "sense__funny_2" "riddle", false), (bin "sense__tells_1" "alice" "riddle", false),
           (.not (u "sense__funny_1" "riddle"), false)]
  | .error _ => false
-- j9: the fresh sorts in the environment JSON
#guard match project F A1 EJ LJ ["funny", "tells"] with
  | .ok P =>
    let sorts := (P.envJson.getObjValD "vocabulary").getObjValD "sorts"
    ["number", "principal", "resource", "service"].all (fun n =>
      (sorts.getObjValD n).getObjValD "verbalisation" ==
        Json.mkObj [("singular", .str n), ("plural", .str (n ++ "s"))]) &&
    sorts.getObjValD "joke" == Json.mkObj [("description", .str "A sort.")]
  | .error _ => false
-- j10, j11
#guard lexSummary (project F A1 EJ LJ ["funny", "tells", "is"]) == lexSummary (project F A1 EJ LJ ["funny", "tells"])
#guard usedWords F (sentsOf "Alice does not tell the riddle.") == ["tells"] &&
  usedWords F (sentsOf "Alice is funny.") == ["funny"] && usedWords F (sentsOf "The riddle is strange.") == []
-- j12, j12b
def EJt : Env := mkEnv ["joke", "person", "story"] [("alice", "person"), ("riddle", "joke")] [("riddle", "the riddle")]
def LJt : Lexicon := { LJ with nouns := LJ.nouns ++ [("story", "story")], letters := LJ.letters ++ [("story", "S")] }
#guard LJt.valid EJt {} && projFault (project F A1 EJt LJt ["funny"]) == some (.collision "letter" "S" "service")
#guard projFault (project F A1 EJ { LJ with letters := [("joke", "K"), ("person", "P")] } ["funny"]) ==
  some (.collision "letter" "J" "joke")
#guard projFault (project F A1 EJ { LJ with letters := [("joke", "J"), ("person", "S")] } ["funny"]) ==
  some (.collision "letter" "P" "person")
-- j13: two kinds under one noun, a well-formed pack
def Dgag : Dictionary := ⟨[⟨"gags@1", [⟨"gag", "joke", "jokes", "A gag.", "G"⟩],
  [⟨"dry", 1, "deadpan", "told without expression", ["gag"], "{0} is dry", none⟩]⟩], []⟩
#guard Dgag.failures [] == [] && projFault (project Dgag ⟨[]⟩ EJ LJ ["dry"]) == some (.collision "sort" "joke" "gag")
-- j14
#guard projFault (project F A1 EJ { LJ with nouns := [("joke", "gag"), ("person", "person")] } ["funny"]) ==
  some (.collision "sort" "joke" "")
-- step 4: a fresh sort named as a constant of the document
def EJk : Env := mkEnv ["joke", "person"] [("alice", "person"), ("riddle", "joke"), ("number", "person")]
  [("riddle", "the riddle")]
def LJk : Lexicon := { LJ with spellings := LJ.spellings ++ [("number", "number")] }
#guard LJk.valid EJk {} && projFault (project F A1 EJk LJk ["funny"]) == some (.collision "name" "number" "")
-- j15: two senses of one word that share a comma form, projected without the dictionary check
#guard projFault (project Fd ⟨[]⟩ EJn LJn ["near"]) == some (.collision "predicate" "sense__near_1" "sense__near_2")
#guard (clashes (projectionOf Fd ⟨[]⟩ EJn LJn ["near"]).env (projectionOf Fd ⟨[]⟩ EJn LJn ["near"]).lexicon).head? ==
  some ("predicate", "sense__near_1", "predicate", "sense__near_2", "{0} is near, in the sense of beside bob")
-- j16: the cap of 32 sorts, at it and past it
def envN (n : Nat) : Env := mkEnv ((List.range n).map fun i => "k" ++ toString i) []
def lexN (n : Nat) : Lexicon := {
  nouns := (List.range n).map fun i => ("k" ++ toString i, "k" ++ toString i),
  letters := (List.range n).map fun i => ("k" ++ toString i, String.mk [Char.ofNat (65 + i / 26), Char.ofNat (65 + i % 26)]),
  wordings := [], negatives := [], aliases := [], spellings := [] }
#guard (lexN 32).valid (envN 32) {} && projFault (project Dgag ⟨[]⟩ (envN 32) (lexN 32) ["dry"]) == some (.limit "sorts")
#guard projFault (project Dgag ⟨[]⟩ (envN 31) (lexN 31) ["dry"]) == none
-- the cap of 256 predicates, at it and past it
def manyPreds (n : Nat) : List ReadExamples.PredSpec :=
  (List.range n).map fun i => ("p" ++ toString i, ["joke"], "{0} is p" ++ toString i, none)
def envP (n : Nat) : Env := mkEnv ["joke", "person"] [("alice", "person"), ("riddle", "joke")] [("riddle", "the riddle")]
  (manyPreds n)
#guard projFault (project F A1 (envP 254) LJ ["funny"]) != some (.limit "predicates")
#guard projFault (project F A1 (envP 255) LJ ["funny"]) == some (.limit "predicates")
-- j17: the colliding pair, with its shared wording
def EJ17 : Env := mkEnv ["joke", "person"] [("alice", "person"), ("riddle", "joke")] [("riddle", "the riddle")]
  [("a", ["joke"], "{0} is funny", none), ("b", ["joke"], "{0} is calm", none)]
def LJ17 : Lexicon := { LJ with wordings := [("a", "{0} is funny"), ("b", "{0} is calm")] }
def D17 : Dictionary := ⟨[⟨"calm@1", [srt "joke" "J"],
  [⟨"funny", 1, "amusing", "causes laughter", ["joke"], "{0} is funny", none⟩,
   ⟨"calm", 1, "quiet", "not agitated", ["joke"], "{0} is calm", none⟩]⟩], []⟩
#guard LJ17.valid EJ17 {} && D17.failures ["joke", "person"] == [] &&
  projFault (project D17 ⟨[]⟩ EJ17 LJ17 ["funny", "calm"]) == some (.collision "predicate" "a" "sense__funny_1")

/-! ## 8.5 The gloss forms (c), as merged -/

/-- The projection of j1 with `odd` also used. -/
def Pj1 : Projection := projectionOf F A1 EJ LJ ["funny", "tells", "odd"]
#guard projFault (project F A1 EJ LJ ["funny", "tells", "odd"]) == none && grammarFault Pj1 == none
#guard ([("The riddle is funny (meaning strange).", 1),                                                         -- c1
  ("The riddle is funny, in the sense of strange.", 1),                                                         -- c2
  ("Every joke that is funny, in the sense of strange, is not funny.", 0),                                      -- c3
  ("Every joke that is funny, in the sense of strange, and is odd (meaning strange) is not funny.", 0),         -- c4
  ("Every joke that is funny, in the sense of strange, and is odd (meaning strange) and is funny is not funny.", 0),  -- c5
  ("Every joke that is funny, in the sense of strange, and is odd (meaning strange), and is funny is not funny.", 0), -- c6
  ("The riddle is funny ( meaning strange ).", 0),                                                              -- c7
  ("The riddle is funny (meaning amusing).", 1),                                                                -- c8
  ("Every joke that is funny (meaning strange) is not funny.", 0),                                              -- c9
  ("Every joke that is funny, in the sense of strange is not funny.", 1),                                       -- c10
  ("The riddle is funny, in the sense of strange,.", 1),                                                        -- c11
  ("Alice tells (meaning says aloud) the riddle.", 1),                                                          -- c12
  ("Alice tells, in the sense of says aloud, the riddle.", 1),                                                  -- c13
  ("Alice tells, in the sense of says aloud the riddle.", 1),                                                   -- c14
  ("Alice does not tell (meaning says aloud) the riddle.", 1),                                                  -- c15
  ("Every joke that is funny, in the sense of strange, and is odd, in the sense of strange, and is funny is not funny.", 0),  -- c16
  ("Every joke that alice tells (meaning says aloud) is odd (meaning strange).", 0)]                            -- c17
  : List (String × Nat)).all fun (s, n) => countsIn (grammar Pj1.env Pj1.lexicon) s == [n]

/-! ## 8.6 Extension (q) -/

instance (E : Env) (L : Lexicon) (E2 : Env) (L2 : Lexicon) : Decidable (Extends E {} L E2 {} L2) := by
  unfold Extends envSub lexiconSub; infer_instance
def extendsB (P P2 : Except SenseFault Projection) : Option Bool :=
  match P, P2 with
  | .ok P, .ok P2 => some (decide (Extends P.env {} P.lexicon P2.env {} P2.lexicon))
  | _, _ => none
#guard extendsB (project F A1 EJ LJ ["tells"]) (project F A1 EJ LJ ["funny", "tells"]) == some true      -- q1
#guard extendsB (project F A1 EJ LJ ["funny", "tells"]) (project F A1 EJ LJ ["tells"]) == some false
#guard extendsB (project F A1 EJ LJ ["funny", "tells"]) (project F ⟨[("funny", 2)]⟩ EJ LJ ["funny", "tells"]) ==
  some false                                                                                                 -- q2

/-! ## 8.7 Reading (s, n, m), as merged -/

def rJ : DState := st ["alice", "riddle"]
def allJoke (A B : EFormula) : EFormula := .all "joke" (.implies A B)
#guard rs F EJ LJ J == .stopped 1 .none                                                         -- s1
#guard rs F EJ LJ (doc Jbody) == .stopped 0 .none                                               -- s2
#guard rs F EJs LJs (doc [lineFunny, "Legacy is funny."]) == .illTyped                          -- s3
#guard rs F EJs LJs "Legacy is funny." == .stopped 0 .none
#guard rs F EJ LJ (doc ("In this document, funny means purple." :: Jbody)) ==                   -- s4
  .fault (.unknownGloss 0 "funny" "purple")
#guard rs F EJ LJ (doc [Jbody[0]!, Jbody[1]!, lineFunny, Jbody[2]!, Jbody[3]!]) == .fault (.preambleLate 2)  -- s5
#guard rs F EJ6 LJ6 J == .fault (.collision "predicate" "funny" "sense__funny_1")              -- s6
#guard rs F EJ LJ "Alice tells the riddle." ==                                                 -- s7
  .ok [res (bin "sense__tells_1" "alice" "riddle") rJ] [occ 0 1 2 "sense__tells_1" true] [] []
#guard rs F EJ LJ (doc [lineFunny, "The riddle is funny (meaning amusing)."]) ==                -- s8
  .ok [res (u "sense__funny_1" "riddle") (st ["riddle"])] [occ 1 3 8 "sense__funny_1" true] [] []
-- s8: S2's `checkRendering` of the unit under the projection
#guard match readWithSenses F EJ LJ workBudget (doc [lineFunny, "The riddle is funny (meaning amusing)."]) with
  | .ok us _ _ _ P =>
    let rs := us.filterMap (·.formula)
    checkRendering P.env {} P.lexicon workBudget rs "The riddle is funny." &&
    checkRendering P.env {} P.lexicon workBudget rs "The riddle is funny (meaning amusing)." &&
    !checkRendering P.env {} P.lexicon workBudget rs "The riddle is funny (meaning strange)."
  | _ => false
#guard rs F EJ LJ (doc [lineFunny, "In this document, odd means strange.", "Every funny joke is odd."]) ==  -- s9
  .ok [res (allJoke (.pred "sense__funny_1" [v0]) (.pred "sense__odd_1" [v0])) (st [] true)]
    [occ 2 1 2 "sense__funny_1" true, occ 2 4 5 "sense__odd_1" true] [] []
#guard rs F EJ LJ (doc ["In this document, odd means strange.", "Every funny (meaning strange) joke is odd."]) ==
  .stopped 1 .none                                                                              -- s10
#guard rs F3 EJ LJ "The riddle is warm, cool and mild." ==                                     -- s11
  .fault (.tooManyCandidates 0 ["warm", "cool", "mild"])
#guard (choicesOf F3 ["warm", "cool", "mild"]).length == 27
#guard rs F2 EJ LJ "Both alice tells the riddle and the riddle is funny." ==                   -- s12
  .ok [⟨none, [(1, 1), (1, 2), (2, 1), (2, 2)].map (fun (f, t) =>
      ⟨[("funny", f), ("tells", t)],
       "In this document, funny means " ++ (if f == 1 then "amusing" else "strange") ++ ".\nIn this document, tells means " ++
         (if t == 1 then "says aloud" else "reveals") ++ ".",
       .and (bin ("sense__tells_" ++ toString t) "alice" "riddle") (u ("sense__funny_" ++ toString f) "riddle"), false⟩),
      ["funny", "tells"], rJ⟩]
    ([(1, 1), (1, 2), (2, 1), (2, 2)].zipIdx.flatMap fun ((f, t), j) =>
      [occ 0 2 3 ("sense__tells_" ++ toString t) true (some j), occ 0 9 10 ("sense__funny_" ++ toString f) true (some j)])
    [] []
#guard rs F EJ LJ ("﻿" ++ J) == .stopped 0 .none                                           -- s14
#guard rs F ES LS "Legacy, beta and gamma are deployed." ==                                     -- s15
  .ok [res (.and (u "sense__deployed_1" "legacy") (.and (u "sense__deployed_1" "beta") (u "sense__deployed_1" "gamma")))
      (st ["beta", "gamma", "legacy"])] [occ 0 6 7 "sense__deployed_1" true] [] []
#guard rs F EJ LJ "The riddle is odd." ==                                                       -- s16
  .ok [⟨none, [⟨[("odd", 1)], "In this document, odd means strange.", u "sense__odd_1" "riddle", false⟩], ["odd"],
      st ["riddle"]⟩] [occ 0 3 4 "sense__odd_1" true (some 0)] [] []
#guard rs Fn EJn LJn "Alice is near bob." == .fault (.candidatesDiverge 0 ["near"] (.referent "bob"))  -- s17
#guard rs F EJn LJn "Alice is near bob." == .stopped 0 .none
#guard rs Fn EJn LJn (doc ["In this document, near means beside.", "Alice is near bob."]) ==    -- s18
  .ok [res (bin "sense__near_2" "alice" "bob") (st ["alice", "bob"])] [occ 1 2 3 "sense__near_2" true] [] []
#guard rs Fn EJn LJn (doc ["In this document, near means beside bob.", "Alice is near bob.", "It is near bob."]) ==  -- s19
  .ok [res (u "sense__near_1" "alice") (st ["alice"]), res (u "sense__near_1" "alice") (st ["alice"])]
    [occ 1 2 3 "sense__near_1" true, occ 2 2 3 "sense__near_1" true] [] []
#guard rs Fn EJn LJn "Alice is near alice." ==                                                  -- s20
  .ok [⟨none, [⟨[("near", 2)], "In this document, near means beside.", bin "sense__near_2" "alice" "alice", false⟩],
      ["near"], st ["alice"]⟩] [occ 0 2 3 "sense__near_2" true (some 0)] [] []
#guard rs F EJ LJ "Alice tells the riddle." 1 == .stopped 0 .budget                             -- s21
#guard rs F EJ LJ (doc [lineFunny, "Alice tells the riddle."]) 1 == .fault (.preambleBudget 0)
#guard rs F EJ LJ "Both the riddle is odd and the riddle is funny (meaning strange)." ==       -- s22
  .ok [⟨none, [⟨[("odd", 1)], "In this document, odd means strange.",
      .and (u "sense__odd_1" "riddle") (u "sense__funny_2" "riddle"), false⟩], ["odd"], st ["riddle"]⟩]
    [occ 0 4 5 "sense__odd_1" true (some 0), occ 0 9 14 "sense__funny_2" false (some 0)] [] []
#guard rs Fn EJn LJn (doc ["In this document, near means beside.", "Alice is near bob.",        -- s23
    "Starting from alice, bob is reachable by one or more \"sense__near_2\" steps."]) == .fault (.quotedSense 2 "near")
#guard rs F EJ LJ (doc [lineFunny, "The riddle is not funny."]) ==                              -- n1
  .ok [res (.not (u "sense__funny_1" "riddle")) (st ["riddle"])] [occ 1 4 5 "sense__funny_1" true] [] []
#guard rs F EJ LJ "The riddle is not funny (meaning strange)." ==                               -- n2
  .ok [res (.not (u "sense__funny_2" "riddle")) (st ["riddle"])] [occ 0 4 9 "sense__funny_2" false] [] []
#guard rs F EJ LJ "Alice does not tell the riddle." ==                                          -- n3
  .ok [res (.not (bin "sense__tells_1" "alice" "riddle")) rJ] [occ 0 3 4 "sense__tells_1" true] [] []
#guard rs F EJ LJ (doc [lineFunny, "Every joke that is not funny is odd (meaning strange)."]) == -- n4
  .ok [res (allJoke (.not (.pred "sense__funny_1" [v0])) (.pred "sense__odd_1" [v0])) (st [] true)]
    [occ 1 5 6 "sense__funny_1" true, occ 1 7 12 "sense__odd_1" false] [] []
#guard rs F EP LP "Alice may not access the api." ==                                            -- n5
  .ok [res (.not (bin "sense__access_1" "alice" "api")) (st ["alice", "api"])] [occ 0 3 4 "sense__access_1" true] [] []
#guard rs (Fwith (swap sAccess1 { sAccess1 with negative := none })) EP LP "Alice may not access the api." ==
  .stopped 0 .none                                                                              -- n6
#guard rs F2 EJ LJ "Alice does not tell the riddle." ==                                         -- n7
  .ok [⟨none, [⟨[("tells", 1)], "In this document, tells means says aloud.", .not (bin "sense__tells_1" "alice" "riddle"), false⟩,
      ⟨[("tells", 2)], "In this document, tells means reveals.", .not (bin "sense__tells_2" "alice" "riddle"), false⟩],
      ["tells"], rJ⟩]
    [occ 0 3 4 "sense__tells_1" true (some 0), occ 0 3 4 "sense__tells_2" true (some 1)] [] []
-- m1 as merged: both senses of `funny` in the resolved formulas, in order of first occurrence
#guard rs F EJ LJ (doc [lineFunny, "The riddle is funny (meaning strange).", "The riddle is not funny."]) ==
  .ok [res (u "sense__funny_2" "riddle") (st ["riddle"]), res (.not (u "sense__funny_1" "riddle")) (st ["riddle"])]
    [occ 1 3 8 "sense__funny_2" false, occ 2 4 5 "sense__funny_1" true]
    [("funny", ["sense__funny_2", "sense__funny_1"])] []
#guard rs F EJ LJ (doc [lineFunny, "The riddle is funny."]) ==                                  -- m3
  .ok [res (u "sense__funny_1" "riddle") (st ["riddle"])] [occ 1 3 4 "sense__funny_1" true] [] []
#guard rs F EJ LJ "The riddle is funny (meaning strange). The riddle is not funny (meaning strange)." ==  -- m4
  .ok [res (u "sense__funny_2" "riddle") (st ["riddle"]), res (.not (u "sense__funny_2" "riddle")) (st ["riddle"])]
    [occ 0 3 8 "sense__funny_2" false, occ 1 4 9 "sense__funny_2" false] [] []
-- s13's unused default, as merged: the second line's word is not used by a body that reads
#guard rs F EJ LJ (doc [lineFunny, "In this document, odd means strange.", "Alice tells the riddle."]) ==
  .ok [res (bin "sense__tells_1" "alice" "riddle") rJ] [occ 2 1 2 "sense__tells_1" true] [] ["funny", "odd"]

/-! ## 8.8 The "No X that …" row (w), without the proposed row -/

#guard ["No joke that is funny (meaning strange) is funny.", "No joke that is funny (meaning strange) is not funny.",
  "No joke is funny."].map (countsIn (grammar Pj1.env Pj1.lexicon)) == [[0], [0], [1]]

/-! ## 8.10 The two-direction claims that need no reading -/

-- the divergence test, both components, and its fallback
#guard divergence (st ["alice"]) (st ["alice", "bob"]) == .referent "bob"
#guard divergence (st ["alice"]) (st ["alice"] true) == .binder
-- a used word with no default is unresolved exactly when it has an unswitched occurrence
#guard unresolvedIn F ⟨[]⟩ (sentsOf "Both the riddle is odd and the riddle is funny (meaning strange).").head! == ["odd"]
#guard unresolvedIn F ⟨[]⟩ (sentsOf "Every joke that is funny (meaning strange) is not funny.").head! == ["funny"]
#guard unresolvedIn F ⟨[]⟩ (sentsOf "The riddle is funny (meaning strange).").head! == []
#guard unresolvedIn F ⟨[]⟩ (sentsOf "The riddle is funny, in the sense of strange.").head! == []
#guard unresolvedIn F ⟨[]⟩ (sentsOf "The riddle is funny ( meaning strange ).").head! == []
#guard unresolvedIn F ⟨[]⟩ (sentsOf "The riddle is funny and odd.").head! == ["funny", "odd"]
#guard unresolvedIn F A1 (sentsOf "The riddle is funny and odd.").head! == ["odd"]
-- mixed_exact, both directions, on hand-built units
#guard mixedOf (projectionOf F A1 EJ LJ ["funny", "tells"])
    [res (u "sense__funny_2" "riddle") DState.init, res (.not (u "sense__funny_1" "riddle")) DState.init] ==
  [("funny", ["sense__funny_2", "sense__funny_1"])]
#guard mixedOf (projectionOf F A1 EJ LJ ["funny", "tells"])
    [res (u "sense__funny_1" "riddle") DState.init, res (.not (u "sense__funny_1" "riddle")) DState.init] == []

end VE.Senses.Examples
