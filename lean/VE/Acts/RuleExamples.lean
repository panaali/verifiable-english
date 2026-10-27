import VE.Acts.Grammar
import VE.Acts.GrammarExamples

/-! Fixtures of the act grammar's rule table (docs/spec/act-phrases.md 5.2, 5.6, 11.2, 11.2a, 11.2b).

The raw derivation counts of 11.2 (G5 to L0) and of the 13 `ap0` rows of 11.2b, each the number the spec records;
`grammar_wf` on both sides of its hypothesis; and a corpus over one vocabulary with a frame of each shape the table
tells apart (an object, no object, a split object), whose derivations use every rule of the grammar except the six
that nothing reaches, with each phrase's count pinned: 2 to the number of its edge choices (5.2). The meanings, and so
the readings, are ap-2c's.
-/

namespace VE.Acts.RuleExamples
open VE.Acts VE.Acts.Examples
open VE.Acts.Lexical (Tok)
open VE.Grammar (Tree)

/-- The derivations of an act phrase, up to `rawCap`; `none` when the step budget is exhausted or the phrase does not
lex. -/
def parsed (V : Vocab) (fx : List String) (s : String) (b := stepBudget) : Option (List (Tree Tok)) :=
  match Lexical.lex fx s with
  | .ok ts => VE.Grammar.parse (grammar V) rawCap b ts.toArray
  | .error _ => none
def rawOf (V : Vocab) (fx : List String) (s : String) (b := stepBudget) : Option Nat := (parsed V fx s b).map (·.length)
/-- The derivations of each phrase of `ps`, with `V`'s grammar prepared once. -/
def treesOf (V : Vocab) (fx ps : List String) : List (Option (List (Tree Tok))) :=
  let P := (grammar V).prepare
  ps.map (fun s => match Lexical.lex fx s with
    | .ok ts => P.parse rawCap stepBudget ts.toArray
    | .error _ => none)
def rawsOf (V : Vocab) (fx ps : List String) : List (Option Nat) := (treesOf V fx ps).map (·.map (·.length))

/-! ### 11.2: G5 to L0 (raw derivations) -/

def g5 := "{0} to seek and to enjoy in other countries asylum from persecution"
#guard rawOf V5 ["other countries"] g5 == some 2                                                       -- G5
#guard rawOf V5 [] g5 == some 0                                                                        -- G5b
#guard rawOf V6 ["cruel, inhuman or degrading treatment or punishment"]
  "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment" == some 1    -- G6
#guard rawOf V7 ["equivalent free voting procedures"]
  "{0} be held by secret vote or by equivalent free voting procedures" == some 1                        -- G7
def g8 := "{0} freely to participate in the cultural life of the community, to enjoy the arts and to share in " ++
  "scientific advancement and its benefits"
#guard rawOf V8 ["the cultural life of the community", "scientific advancement and its benefits"] g8 == some 2  -- G8
#guard rawOf V9 ["the right to change their nationality"]
  "{0} be arbitrarily deprived of their nationality nor denied the right to change their nationality" == some 2  -- G9
#guard rawOf V10 ["other lack of livelihood"] ("{0} to security in the event of unemployment, sickness, " ++
  "disability, widowhood, old age or other lack of livelihood in circumstances beyond their control") == some 2  -- G10
#guard rawOf V11 ["freely chosen representatives"]
  "{0} to take part in {1} directly or through freely chosen representatives" == some 1                -- G11
#guard rawOf V12 [] "{0} to form and to join trade unions for the protection of their interests" == some 2  -- G12
#guard rawOf V14 ["its core identity or principles", "to be human", "genuinely deceptive tactics that could harm users",
  "health or safety", "Anthropic’s guidelines"] ("{0} abandon its core identity or principles, claim to be human, " ++
  "use genuinely deceptive tactics that could harm users, endanger health or safety, or act against " ++
  "Anthropic’s guidelines") == some 1                                                                 -- G14v
def V5k : Vocab := frames [fr "seek" [""] [] ["in"], fr "enjoy" [""] [] ["in"], fr "keep" [""] [] []]
#guard rawOf V5k [] "{0} to seek asylum or to enjoy asylum and to keep asylum" == some 0                -- G38
#guard rawOf V5k [] "{0} to seek, enjoy and to keep asylum" == some 0                                    -- G39
def cities : List String := ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"].map
  (s!"the {·} city")
def ln (n : Nat) : String := "{0} to seek and to enjoy asylum" ++ String.join ((cities.take n).map (" in " ++ ·))
#guard [6, 7, 8].map (fun n => rawOf V5 cities (ln n)) == [some 64, some 128, some 256]                -- L6, L7, L8
#guard rawOf V5 ["other countries"] g5 0 == none                                                       -- L0

/-- G5's two derivations take its two `REt` rules in order: `in [other countries]` on the last item, then on all
(G5d lists the readings in this order). -/
def rets : List Nat := ((closed (schema V5)).zipIdx.filter (·.1.lhs == .F 1 .REt)).map (·.2)
#guard ((parsed V5 ["other countries"] g5).getD []).map (fun t => (rulesOf t).filter rets.contains) ==
  [[rets.getD 2 0], [rets.getD 3 0]]

/-! ### 11.2b: the 13 `ap0` rows (raw derivations) -/

def ap (i : Nat) : Vocab := ap0.getD i ⟨[], []⟩
#guard [rawOf (ap 0) [] "{0} be held in slavery or servitude",                                          -- X024
  rawOf (ap 1) [] "{0} be subjected to arbitrary arrest, detention or exile",                           -- X037
  rawOf (ap 1) [] "{0} be subjected to arbitrary interference with their privacy, family, home or correspondence",
  rawOf (ap 2) [] ("{0} be subjected to arbitrary interference with their privacy, family, home or correspondence, " ++
    "nor to attacks upon their honour and reputation"),                                                 -- X045ab
  rawOf (ap 3) [] "{0} to marry and to found a family",                                                 -- X057
  rawOf (ap 4) [] "{0} to change their religion or belief",                                             -- X067
  rawOf (ap 5) [] ("{0} either alone or in community with others and in public or private, to manifest their " ++
    "religion or belief in teaching, practice, worship and observance"),                                -- X068
  rawOf (ap 6) [] "{0} to seek, receive and impart information and ideas through any media and regardless of frontiers",
  rawOf (ap 7) [] "{0} promote understanding, tolerance and friendship among all nations, racial or religious groups",
  rawOf (ap 8) [] "{0} give Claude a specific set of instructions, a persona, or information",          -- X0062
  rawOf (ap 9) [] "{0} actively deceive {1} about the existence of a system prompt or its content",     -- X0156
  rawOf (ap 10) ["an attempt to kill or disempower the vast majority of humanity or the human species as whole"]
    "{0} engage or assist in an attempt to kill or disempower the vast majority of humanity or the human species as whole",
  rawOf (ap 11) ["an attempt to seize unprecedented and illegitimate degrees of absolute societal, military, or economic control"]
    ("{0} engage or assist any individual or group with an attempt to seize unprecedented and illegitimate degrees " ++
    "of absolute societal, military, or economic control")] ==
  [1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1].map some    -- X024 X037 X045a X045ab X057 X067 X068 X071b X101 X0062 X0156 X0165s05/s06

/-! ### `grammar_wf` on both sides of its hypothesis -/

#guard [V5, V6, V7, V8, V9, V10, V11, V12, V14, V5k].all (fun V => framesOk V && (grammar V).wf) &&
  ap0.all (fun V => framesOk V && (grammar V).wf)
/-- FR1: a marker of a space. `framesOk` refuses it; its rule `MK " "` has no right side, so the grammar is not well
formed. An empty head is the same through `HD`'s rule. A marker or head of one word is the boundary. -/
def fr1 : Vocab := frames [fr "seek" ["", " "] [] []]
def noHead : Vocab := frames [⟨[], [""], [], []⟩]
def oneWord : Vocab := frames [fr "seek" ["", "in"] [] [], fr "go" [] [] ["by"]]
#guard !framesOk fr1 && !(grammar fr1).wf && !framesOk noHead && !(grammar noHead).wf
#guard framesOk oneWord && (grammar oneWord).wf
/-- FR2: two spellings of one marker. `framesOk` refuses them, because each phrase that uses the marker would read
twice, once per spelling. -/
def fr2 (ms : List String) : Vocab := frames [fr "stand" ms [] []]
#guard rawOf (fr2 ["in front", "in  front"]) [] "{0} stand in front {1}" == some 2 &&
  rawOf (fr2 ["in front"]) [] "{0} stand in front {1}" == some 1 && !framesOk (fr2 ["in front", "in  front"])

/-! ### Every rule of the table: a corpus over a frame of each shape -/

/-- *seek* has an object, a split marker (`in`), a marker that is not split (`from`) and a modifier marker; *go* has
no object; *share* has a split object. -/
def K : Vocab := ⟨[fr "seek" ["", "from", "in"] ["in"] ["for"], fr "go" ["into", "at"] ["at"] ["by"],
  fr "share" ["", "with"] [""] ["for"]], ["freely"]⟩
def corpus : List String := ([
  "freely seek asylum", "freely to be seek asylum", "to freely seek asylum", "freely freely to freely seek asylum",
  "seek asylum from war, from peace or from {1}", "seek asylum from war, or from {1}",
  "seek asylum from war freely for peace", "seek the city in Paris and in Rome from war for peace",
  "seek asylum in Paris, Rome or {1} freely", "seek asylum in Paris, in Rome, and in Rome",
  "seek asylum freely or for peace", "seek asylum for peace, freely, and for war", "be seek asylum", "seek",
  "seek political asylum, peace, and war", "seek asylum from war or peace", "seek asylum in Paris",
  "seek asylum in Paris or in Rome in London", "seek asylum in Paris or Rome from war or peace",
  "freely to seek, to seek, and to seek", "to freely seek or to seek", "freely to freely seek nor to seek",
  "to seek asylum, to seek asylum, freely to seek asylum, to freely seek asylum, freely to freely seek asylum and to seek asylum",
  "freely to seek asylum, to seek asylum and freely to seek asylum from war freely",
  "to freely seek asylum, to seek asylum, and to freely seek asylum for peace",
  "freely to freely seek asylum and freely to freely seek asylum from war",
  "to seek asylum, to seek asylum, and to seek", "to seek asylum and freely to seek",
  "to seek, freely to seek, to freely seek, freely to freely seek and to seek asylum",
  "to seek, to seek, and freely to seek asylum", "to seek and to freely seek asylum",
  "to seek and freely to freely seek asylum", "to seek asylum and to seek asylum from war or peace",
  "to seek asylum and to seek asylum freely in Paris", "to seek asylum and to seek asylum freely for peace",
  "freely seek, freely seek, and seek", "to seek and seek", "to freely seek nor seek",
  "freely to freely seek and seek", "seek asylum, seek asylum, freely seek asylum and seek asylum",
  "freely seek asylum, seek asylum, and seek", "to seek asylum and freely seek asylum",
  "freely to seek asylum or seek asylum", "to freely seek asylum and seek asylum",
  "freely to freely seek asylum and seek asylum", "seek, seek, and freely seek asylum",
  "seek and seek freely for {1} asylum from war in Rome", "seek and seek freely asylum for peace in Rome",
  "freely freely to seek and seek", "seek asylum, seek asylum, and freely seek asylum",
  "seek and seek asylum from war or peace", "seek and seek freely asylum", "go", "go into big town", "go into {1}",
  "go into town, city, or village", "go into town, into city, or into village", "go into town or into city",
  "go at noon", "go at noon or night by car", "go into town at noon or at night", "go at noon or at night at dawn",
  "go at noon or at night into town or city", "go at noon or at night into town freely",
  "go by car, by bus, or freely", "go into town and go", "go into town and go into town or city",
  "go into town and go at noon", "go into town and go freely into city", "go into town and go by car freely",
  "go into town and go into city by car", "go and go into town at noon", "go and go into town or city",
  "go and go by car", "go and go freely", "go at noon, at night, or at dawn", "go into town by car",
  "go into town at noon or at night by car", "go by car or by bus", "share", "share brown bread with {1}",
  "share bread and water", "share bread, water, or salt for peace", "share bread for peace",
  "share bread freely or for peace with friends", "share bread and water with friends or neighbours",
  "share bread and share bread", "share bread and share bread freely with friends",
  "share bread and share bread with friends for peace", "share bread and share bread for peace freely",
  "share and share bread", "share and share bread with friends or neighbours", "share and share freely bread",
  "share and share freely for {1} bread with friends", "share bread with friends, with neighbours, or with {1}",
  "share bread with friends or with neighbours", "share bread with friends freely",
  "share bread and share bread with friends or neighbours", "share and share bread with friends for peace",
  "share bread and water with friends freely", "share bread freely, for peace, or for war"] : List String).map ("{0} " ++ ·)
def trees : List (Option (List (Tree Tok))) := treesOf K ["the city"] corpus
#guard framesOk K && trees.map (·.map (·.length)) == ([1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 4, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 4, 2, 1, 2, 4, 1, 2, 1, 2, 2, 4, 1, 4, 4, 4, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 4, 2, 1, 1, 2, 2, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 4, 1, 1, 2, 4, 1, 1, 1, 1, 2, 2, 1]).map some
/-- The rules of `K`'s grammar that no derivation of the corpus uses, apart from the `never` rules. -/
def unused : List RuleS :=
  let used := trees.flatMap (fun ts => (ts.getD []).flatMap rulesOf)
  ((closed (schema K)).zipIdx.filter (fun (r, i) => !used.contains i && r.rhs != [.t .never])).map (·.1)
-- Only the shared-object edges of *go* are unused: 5.2 writes `REt` and `REP` for every frame, and only an object
-- frame's `RM` reads them.
#guard unused.map (·.lhs) == [.F 1 .REt, .F 1 .REt, .F 1 .REt, .F 1 .REt, .F 1 .REP, .F 1 .REP]

/-! ### Lists of two: each element at either end of its list, on both sides -/

/-- Two split markers, two not split, `""` last; two modifier markers, one of two words; split objects with `""` first
and last; a head of two words; two adverbs. -/
def K2 : Vocab := ⟨[fr "seek" ["from", "about", "in", "on", ""] ["in", "on"] ["for", "close by"],
  fr "share" ["with", ""] ["with", ""] [], fr "give back" ["", "via"] ["", "via"] []], ["freely", "gladly"]⟩
#guard framesOk K2 && (["seek asylum close by home", "seek asylum for peace", "seek asylum about war or peace",
  "seek asylum from war or peace", "seek asylum on Monday or on Tuesday", "seek asylum in Paris or in Rome",
  "seek asylum on Monday or Tuesday", "seek asylum in Paris or Rome",
  "seek asylum close by home or for peace", "seek asylum for peace or close by home", "seek by", "give back back",
  "seek asylum in Paris or in Rome close by home", "seek asylum in Paris or in Rome for peace",
  "share bread and water freely", "give back bread and water freely"].map ("{0} " ++ ·) |> rawsOf K2 []) ==
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2].map some
-- Refused: an adverb, *be*, a modifier marker's first word or a head's first word as a filler; a repeated marker's
-- list without its first member.
#guard (["seek gladly", "seek freely", "seek be", "seek close", "seek for", "give back give",
  "seek asylum or from war"].map ("{0} " ++ ·) |> rawsOf K2 []).all (· == some 0)
-- `X → never` for exactly the nonterminals that have no rule: none in `K` and `K2`, *NM* of each frame of V5.
def nevers (V : Vocab) : List NT := ((closed (schema V)).filter (·.rhs == [.t .never])).map (·.lhs)
#guard nevers K == [] && nevers K2 == [] && nevers V5 == [.F 0 .NM, .F 1 .NM]

end VE.Acts.RuleExamples
