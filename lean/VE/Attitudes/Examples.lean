import VE.Attitudes.Syntax

/-! `#guard`s on the values sections 2.1 to 2.4 of docs/spec/attitudes.md compute, on the fixtures of
section 7.1 (F-AT0 to F-AT3, C-a's two conditions, C-e's reading-set part), and from at-1b on sections
2.5 and 2.6: elaboration, one guard per row of 5.2, what passes, 7.5's guard per theorem. The fixture
documents are the spec stub's (docs/spec/attitudes/SpecStubs_attitudes.lean, S5), copied as written;
the frame and the semantics are at-1's. -/

namespace VE.Attitudes.Examples
open VE.Attitudes
open VE.Reports (Act)

/-! ## The fixtures (spec 7.1; the stub's S5) -/

/-- A hypothetical table, kept only for the fixtures that need a table E1 and E2 did not give. -/
def fixtureTable : Table :=
  { candidates := e1Words,
    lowerBound := [("very likely", "E1.cert.very-likely"), ("quite likely", "E1.cert.quite-likely")],
    above := [("very likely", "quite likely", "E1.pair.very-likely.quite-likely")],
    factive := some "E2.factive",
    knowsBelieves := some "E2.knows-believes",
    knowsThinks := [("very likely", "E2.knows-thinks.very-likely"), ("quite likely", "E2.knows-thinks.quite-likely")] }

/-- As `fixtureTable` without the pair: the order of the two words then comes only from a document. -/
def fixtureTableNoPair : Table := { fixtureTable with above := [] }

/-- Closure-review failures: a derived premise-3 word without its own item; a derived pair without its own item. -/
def badTableKnows : Table := { fixtureTable with knowsThinks := [("very likely", "E2.knows-thinks.very-likely")] }
def badTablePair : Table :=
  { fixtureTable with
    lowerBound := fixtureTable.lowerBound ++ [("likely", "E1.cert.likely")],
    above := fixtureTable.above ++ [("quite likely", "likely", "E1.pair.quite-likely.likely")],
    knowsThinks := fixtureTable.knowsThinks ++ [("likely", "E2.knows-thinks.likely")] }

/-- The table before E1 and E2 reported (drafts 1 to 4): nothing admitted. -/
def preReportTable : Table :=
  { candidates := e1Words, lowerBound := [], above := [], factive := none, knowsBelieves := none, knowsThinks := [] }

def sortC : String := "claude_instance"
def sortS : String := "situation"

def preds (ns : List (String × List String)) : String → Option (List String) :=
  fun p => (ns.find? (·.1 == p)).map (·.2)

def categories : List String :=
  ["mass_casualty_weapon_uplift", "critical_infrastructure_attack_uplift", "damaging_cyberweapon",
    "undermining_ai_oversight", "disempowering_humanity", "illegitimate_power_seizure", "csam_generation"]

def predicateList : List (String × List String) :=
  categories.map (fun c => (c, [sortS])) ++
  (List.range 7).map (fun i => (s!"intentionally_does_restricted_action_{i + 1}", [sortC, sortS])) ++
  [("weapons_uplift_permitted", [sortC, sortS])]

def envP : VE.Environment := { sorts := [sortC, sortS], predicates := preds predicateList, constants := fun _ => none }

def regulatedP : VE.Norms.Regulated :=
  { name := "weapons_uplift_permitted", sorts := [sortC, sortS], allowByDefault := false, role := .permission,
    act := some "{0} do the weapons uplift in {1}", permission := none }

/-- The pilot's wording of each hand-named intention term and of the regulated act; every category atom takes the
    quoted fallback. -/
def actions : List String :=
  ["the weapons uplift", "the infrastructure attack uplift", "the cyberweapon work", "the oversight undermining",
    "the disempowering work", "the power seizure work", "the abuse material generation"]

def declaredWording (p : String) : Option String :=
  if p == "weapons_uplift_permitted" then some "{0} is permitted to do the weapons uplift in {1}" else
  ((List.range 7).find? (fun i => p == s!"intentionally_does_restricted_action_{i + 1}")).map
    (fun i => "{0} intentionally does " ++ actions[i]! ++ " in {1}")

def nounOf (s : String) : String := if s == "claude_instance" then "instance of Claude" else s

/-- The lexical view and the selected lexicon of a vocabulary (the fixture lexicon, SR-3). -/
def lexOf (ss : List String) (ps : List (String × List String × Option String)) (cs : List (String × String)) :
    Lex :=
  { env := { sorts := ss.map (fun s => { name := s, noun := some (nounOf s) }),
             predicates := ps.map (fun p => { name := p.1, arity := p.2.1.length, args := p.2.1, wording := p.2.2 }),
             constants := cs.map (fun c => { name := c.1, sort := c.2 }) },
    overlay := {},
    lexicon := { nouns := ss.map (fun s => (s, nounOf s)), letters := ss.map (fun s => (s, s.take 1)),
                 wordings := ps.map (fun p =>
                   (p.1, p.2.2.getD ((VE.EnglishGrammar.fallbackWording p.1 p.2.1.length).getD ""))),
                 negatives := [], aliases := [], spellings := cs.map (fun c => (c.1, c.1)) } }

def vocabP : List (String × List String × Option String) :=
  predicateList.map (fun p => (p.1, p.2, declaredWording p.1))

def lexP : Lex := lexOf [sortC, sortS] vocabP []

def contentOf (cat : String) : VE.Formula := .unary cat (.var 0)

def cond (m : Mode) (cat : String) : Cond :=
  { holder := .var 1, mode := m, slot := some (sortS, .var 0), content := contentOf cat }

def ql : Mode := .thinks "quite likely"

def docOf (T : Table) (declared : List (Word × Word)) (rules : List ARule) : AttDoc :=
  { E := envP, lits := [], authorPredicates := predicateList.map (·.1), regulated := [regulatedP],
    definitions := [], rules := rules, holders := [sortC], T := T, declared := declared,
    decidedBy := "unstated", lex := lexP }

def ruleOf (n : String) (g : AFormula) : ARule :=
  { name := n, pred := "weapons_uplift_permitted", sign := false, guard := g, carveOuts := [], over := [] }

/-- F-AT1: u0165.s01 with u0173.s01, `intends` kept as a fixture (debate F4). -/
def guard1 : AFormula :=
  .or (.and (.att (cond .knows categories[0]!)) (.att (cond (.act .intends) categories[0]!)))
    (.att (cond ql categories[0]!))
def fat1 : AttDoc := docOf table [] [ruleOf "u0165-s01" guard1]

/-- F-AT2: two categories, u0165.s01 and u0165.s07, `intends` as in F-AT1. -/
def guard2 (cat : String) : AFormula :=
  .or (.and (.att (cond .knows cat)) (.att (cond (.act .intends) cat))) (.att (cond ql cat))
def fat2 : AttDoc :=
  docOf table [] [ruleOf "u0165-s01" (guard2 categories[0]!), ruleOf "u0165-s07" (guard2 categories[6]!)]

/-- F-AT3: two degrees on one content, with and without the document's pair, on a table without the pair. -/
def guard3 : AFormula := .or (.att (cond (.thinks "very likely") categories[0]!)) (.att (cond ql categories[0]!))
def fat3 : AttDoc := docOf fixtureTableNoPair [("very likely", "quite likely")] [ruleOf "u0165-s01" guard3]
def fat3none : AttDoc := docOf fixtureTableNoPair [] [ruleOf "u0165-s01" guard3]

/-- F-AT0: F-AT1 with the attitude conditions removed. -/
def fat0 : AttDoc := docOf table [] [ruleOf "u0165-s01" (.base (contentOf categories[0]!))]

/-- C-a's two `knows` conditions (SR-2), both in one guard: the content `⊤` closed, and with the slot kept. Their
    keys differ only in `slotSort`, so their names differ only by their position. -/
def c_a_both : AttDoc :=
  docOf table [] [ruleOf "u0165-s01" (.and (.att { cond .knows categories[0]! with slot := none, content := .top })
    (.att { cond .knows categories[0]! with content := .top }))]

/-- C-e (at-rev, AT-R1; u0035.s12's shape): the closed `wants` node, holder `c0 : claude_instance`, content
    `C(s1)`; F-AT1 with it as a reading-set part, and with it as a disjunct of F-AT1's guard and no part. -/
def c_e_node : Cond :=
  { holder := .const "c0", mode := .act .wants, slot := none, content := .unary categories[0]! (.const "s1") }
def c_e_doc (ps : List Cond) (g : AFormula) : AttDoc :=
  { docOf table [] [ruleOf "u0165-s01" g] with
    E := { envP with constants := fun c => if c == "s1" then some sortS else if c == "c0" then some sortC else none },
    lex := lexOf [sortC, sortS] vocabP [("s1", sortS), ("c0", sortC)],
    parts := ps }
def c_e_part : AttDoc := c_e_doc [c_e_node] guard1
def c_e_guard : AttDoc := c_e_doc [] (.or guard1 (.att c_e_node))

def errOf : Except String Unit → String
  | .ok () => "ok"
  | .error e => e

def names (A : AttDoc) : List String := (keys A).map (name A)

/-! ## 2.1 The scale and the frozen table -/

-- `table_reviewed`'s guard (spec 7.5), and the review's two failures (spec 7.1, "Tables")
#guard table.reviewed && fixtureTable.reviewed && fixtureTableNoPair.reviewed && !badTableKnows.reviewed &&
  !badTablePair.reviewed
-- `badTablePair`'s closure derives ("very likely", "likely") without an item
#guard badTablePair.scale.atLeast "very likely" "likely" && !badTablePair.hasPair "very likely" "likely"
-- the frozen table: five words admitted, in E1's order; "as likely as not", "unlikely", "very unlikely" refused
#guard table.words == ["almost certain", "very likely", "quite likely", "likely", "more likely than not"] &&
  table.candidates == e1Words && e1Words.length == 8 &&
  ["as likely as not", "unlikely", "very unlikely"].all (fun w => e1Words.contains w && !table.words.contains w)
-- ten pairs, already closed: the closure adds no pair between two distinct words
#guard table.above.length == 10 && table.scale.above.length == 10 &&
  (table.words.flatMap (fun a => table.words.filter (fun b => a != b && table.scale.atLeast a b))).length == 10
#guard table.hasPair "almost certain" "more likely than not" && !table.hasPair "more likely than not" "almost certain"
-- `Scale.atLeast` is reflexive and directed on the frozen table; a refused word is related to no admitted one
#guard table.words.all (fun w => table.scale.atLeast w w)
#guard table.scale.atLeast "almost certain" "more likely than not" && table.scale.atLeast "very likely" "quite likely" &&
  !table.scale.atLeast "quite likely" "very likely" && !table.scale.atLeast "more likely than not" "likely"
#guard table.words.all (fun w => !table.scale.atLeast w "unlikely" && !table.scale.atLeast "unlikely" w)
-- before E1 and E2 reported nothing was admitted: no word, no pair, no premise, and no two words related
#guard preReportTable.reviewed && preReportTable.words == [] &&
  e1Words.all (fun a => e1Words.all (fun b => a == b || !preReportTable.scale.atLeast a b))
-- frame premises on the frozen table: 1 and 2 present, 3 for each of the five words
#guard table.factive == some "E2.factive" && table.knowsBelieves == some "E2.knows-believes" &&
  table.knowsThinks.map (·.1) == table.words
-- `Scale.toOrder` is QS-1's order; `scaleCaps` bounds it (8 words, 64 pairs) through `Order.admit`
#guard table.scale.toOrder.elems == table.words && table.scale.toOrder.edges == table.scale.above
#guard errOf (VE.Closure.Order.admit scaleCaps table.scale.toOrder) == "ok" &&
  errOf (VE.Closure.Order.admit scaleCaps ⟨e1Words ++ ["possible"], []⟩) == "ResourceLimit: At most 8 grades" &&
  errOf (VE.Closure.Order.admit scaleCaps ⟨e1Words.take 1, (List.range 65).map (fun _ => ("almost certain",
    "almost certain"))⟩) == "ResourceLimit: At most 64 order pairs" &&
  errOf (VE.Closure.Order.admit scaleCaps ⟨e1Words.take 8, (List.range 64).map (fun _ => ("almost certain",
    "almost certain"))⟩) == "ok"
-- F-AT3: a document's own pair orders two words the table leaves unordered (`AttDoc.scale`)
#guard fat3.scale.words == ["very likely", "quite likely"] && fat3.scale.above == [("very likely", "quite likely")] &&
  fat3.scale.atLeast "very likely" "quite likely" && !fat3.scale.atLeast "quite likely" "very likely" &&
  !fat3none.scale.atLeast "very likely" "quite likely"
#guard (docOf table [("likely", "almost certain")] []).scale.above.length == 11 &&
  (docOf table [("likely", "almost certain")] []).scale.atLeast "more likely than not" "almost certain" = false &&
  (docOf table [("likely", "almost certain")] []).scale.atLeast "likely" "very likely"

/-! ## 2.2 Modes, conditions, rules -/

#guard [Mode.act .says, .act .believes, .act .wants, .act .intends, .knows, .thinks "quite likely",
    .thinks "more likely than not"].map Mode.slug ==
  ["says", "believes", "wants", "intends", "knows", "thinks_quite_likely", "thinks_more_likely_than_not"]
#guard [Mode.act .wants, .knows, .thinks "quite likely"].map Mode.words == ["wants", "knows", "thinks it quite likely"]
-- a rule's guard context: its regulated predicate's sorts, last argument as variable 0; `[]` for any other
#guard ruleContext fat1 (ruleOf "r" guard1) == [sortS, sortC] &&
  ruleContext fat1 { ruleOf "r" guard1 with pred := "csam_generation" } == []
-- `AFormula.conds`: every condition with its context, in pre-order; a binder extends the context
#guard (condsOf fat1).map (·.2.mode) == [.knows, .act .intends, ql] &&
  (condsOf fat1).all (·.1 == [sortS, sortC])
#guard (AFormula.all "x" (.not (.implies (.base .top) (.ex "y" (.att (cond .knows "p")))))).conds ["a"] ==
  [(["y", "x", "a"], cond .knows "p")] &&
  (AFormula.and (.att (cond .knows "p")) (.or (.base .top) (.att (cond ql "q")))).conds [] ==
  [([], cond .knows "p"), ([], cond ql "q")]
-- carve-outs after the guard
#guard (condsOf (docOf table [] [{ ruleOf "r" (.att (cond .knows "p")) with carveOuts := [.att (cond ql "q")] }])).map
  (·.2.content) == [contentOf "p", contentOf "q"]
-- `Cond.key`: the holder's sort must be a holder sort; an unbound holder has none
#guard (cond .knows "p").key fat1 [sortS, sortC] == some ⟨.knows, sortC, some sortS, contentOf "p"⟩ &&
  { cond .knows "p" with holder := .var 0 }.key fat1 [sortS, sortC] == none &&
  { cond .knows "p" with holder := .var 2 }.key fat1 [sortS, sortC] == none &&
  { cond .knows "p" with holder := .const "c0" }.key fat1 [] == none

/-! ## 2.3 Keys and generated names -/

-- F-AT1: three keys, each on (claude_instance, situation), and their names
#guard keys fat1 == [⟨.knows, sortC, some sortS, contentOf categories[0]!⟩,
  ⟨.act .intends, sortC, some sortS, contentOf categories[0]!⟩, ⟨ql, sortC, some sortS, contentOf categories[0]!⟩]
#guard (keys fat1).all (·.sorts == [sortC, sortS]) &&
  ({ mode := .knows, holderSort := sortC, slotSort := none, content := .top } : Key).sorts == [sortC]
#guard names fat1 == ["attitudes__knows__1", "attitudes__intends__1", "attitudes__thinks_quite_likely__1"]
-- fresh, at most 64 bytes, distinct, and distinct from the regulated and defined names
#guard (names fat1).all (fun n => fat1.E.predicates n == none && n.utf8ByteSize ≤ 64 &&
  !(fat1.regulated.map (·.name) ++ fat1.definitions.map (·.name)).contains n) && (names fat1).Nodup
-- `keyOf` inverts `name` on the keys, and answers `none` elsewhere
#guard (keys fat1).all (fun k => keyOf fat1 (name fat1 k) == some k) && keyOf fat1 "attitudes__knows__2" == none &&
  keyOf fat1 "weapons_uplift_permitted" == none && keyOf fat1 "attitudes__thinks_very_likely__1" == none
-- F-AT2: six keys, numbered per mode in document order
#guard names fat2 == ["attitudes__knows__1", "attitudes__intends__1", "attitudes__thinks_quite_likely__1",
  "attitudes__knows__2", "attitudes__intends__2", "attitudes__thinks_quite_likely__2"] &&
  (keys fat2).all (fun k => keyOf fat2 (name fat2 k) == some k) && (names fat2).Nodup
-- one attitude per key: a repeated condition is one key (`VE.Reports.dedup`)
#guard keys (docOf table [] [ruleOf "a" guard1, ruleOf "b" guard1]) == keys fat1
-- C-a's two conditions differ only in `slotSort`: two keys, two names
#guard names c_a_both == ["attitudes__knows__1", "attitudes__knows__2"] && (names c_a_both).Nodup &&
  (keys c_a_both).map (·.slotSort) == [none, some sortS]
-- F-AT0: no key, no name
#guard keys fat0 == [] && keyOf fat0 "attitudes__knows__1" == none
-- C-e's part (spec 7.1, "c0 wants s1 to be classified as ..."): its key after the rules' keys, closed, on `c0`'s sort
#guard partsOf c_e_part == [([], c_e_node)] && partsOf fat1 == []
#guard names c_e_part == ["attitudes__knows__1", "attitudes__intends__1", "attitudes__thinks_quite_likely__1",
  "attitudes__wants__1"] &&
  keyOf c_e_part "attitudes__wants__1" == some ⟨.act .wants, sortC, none, .unary categories[0]! (.const "s1")⟩ &&
  (keys c_e_part).getLast?.map (·.sorts) == some [sortC]
-- the same node in a guard is the same attitude, with the same name
#guard keys c_e_guard == keys c_e_part

/-! ## 2.4 Environments -/

-- `envAtt` adds each key's name on its sorts, and agrees with `E` on every other name
#guard (names fat1).all (fun n => (envAtt fat1).predicates n == some [sortC, sortS])
#guard (predicateList.map (·.1) ++ ["attitudes__knows__2", "attitudes__wants__1", "x"]).all
  (fun p => (envAtt fat1).predicates p == fat1.E.predicates p) &&
  (envAtt fat1).sorts == fat1.E.sorts
#guard (envAtt c_e_part).predicates "attitudes__wants__1" == some [sortC] &&
  (envAtt c_e_part).constants "c0" == some sortC
-- F-AT0: `envAtt` agrees with `E` on every declared name and on three generated-looking names
#guard (predicateList.map (·.1) ++ ["attitudes__knows__1", "attitudes__intends__1",
  "attitudes__thinks_quite_likely__1"]).all (fun p => (envAtt fat0).predicates p == fat0.E.predicates p)
-- the base vocabulary hides the regulated (and defined) predicates; `baseEnvAtt` adds the names to it
#guard (baseEnv fat1).predicates "weapons_uplift_permitted" == none &&
  (baseEnv fat1).predicates categories[0]! == some [sortS] &&
  (baseEnv { fat1 with definitions := [{ name := categories[0]!, args := [sortS], body := .top }] }).predicates
    categories[0]! == none
#guard (names fat1).all (fun n => (baseEnvAtt fat1).predicates n == some [sortC, sortS]) &&
  (baseEnvAtt fat1).predicates "weapons_uplift_permitted" == none &&
  (baseEnvAtt fat1).predicates categories[6]! == some [sortS] &&
  (envAtt fat1).predicates "weapons_uplift_permitted" == some [sortC, sortS]

/-! ## Fixtures for the trust mutants (R16): each table fails one conjunct of `Table.reviewed`, with its offending
entry first or last; each document has three entries where F-AT1 has one. -/

def tab (cs ws : List Word) (ps : List (Word × Word)) (f kb : Bool) (kt : List Word) : Table :=
  { candidates := cs, lowerBound := ws.map (·, "i"), above := ps.map (fun p => (p.1, p.2, "i")),
    factive := if f then some "i" else none, knowsBelieves := if kb then some "i" else none,
    knowsThinks := kt.map (·, "i") }

def vql : List Word := ["very likely", "quite likely", "likely"]
def vqlPairs : List (Word × Word) :=
  [("very likely", "quite likely"), ("quite likely", "likely"), ("very likely", "likely")]

#guard [tab e1Words vql vqlPairs true true vql, tab e1Words vql.reverse vqlPairs true true vql,
    tab (e1Words.take 7) [] [] true true [],
    tab e1Words ["very unlikely", "almost certain"] [] true true [], tab e1Words vql vqlPairs true true ["likely"],
    tab e1Words vql vqlPairs false false []].all Table.reviewed
#guard [tab (e1Words ++ ["possible"]) [] [] true true [],
    tab e1Words ["possible", "very likely"] [] true true [], tab e1Words ["very likely", "possible"] [] true true [],
    tab e1Words vql (("unlikely", "very likely") :: vqlPairs) true true vql,
    tab e1Words vql (vqlPairs ++ [("very likely", "unlikely")]) true true vql,
    tab e1Words vql vqlPairs true true ("unlikely" :: vql), tab e1Words vql vqlPairs true true (vql ++ ["unlikely"]),
    tab e1Words vql vqlPairs.dropLast true true [], tab e1Words vql.reverse vqlPairs.dropLast true true [],
    tab e1Words vql vqlPairs true true ["likely", "very likely"], tab e1Words vql vqlPairs true true ["very likely", "likely"],
    tab e1Words ["quite likely", "very likely"] [("very likely", "quite likely")] true true ["very likely"],
    tab e1Words vql vqlPairs false true [], tab e1Words vql vqlPairs false false ["likely"]].all (!·.reviewed)
-- `AFormula.conds` keeps both operands' conditions, in order, in the whole context
#guard [AFormula.and, AFormula.or, AFormula.implies].all (fun f =>
  (f (.att (cond .knows "p")) (.and (.att (cond ql "q")) (.att (cond ql "r")))).conds ["a", "b"] ==
  [(["a", "b"], cond .knows "p"), (["a", "b"], cond ql "q"), (["a", "b"], cond ql "r")])
-- three holder sorts, regulated predicates, definitions, declared pairs and parts
def threeRegulated : List VE.Norms.Regulated :=
  [{ regulatedP with name := categories[1]!, sorts := [sortS] }, regulatedP,
    { regulatedP with name := categories[2]!, sorts := [sortS] }]
def threeDefinitions : List VE.Norms.Definition :=
  [3, 4, 5].map (fun i => { name := categories[i]!, args := [sortS], body := .top })
def threeDoc : AttDoc :=
  { fat1 with holders := ["x", sortC, "y"], regulated := threeRegulated, definitions := threeDefinitions }
#guard keys threeDoc == keys fat1 && ruleContext threeDoc (ruleOf "r" guard1) == [sortS, sortC]
#guard [1, 2, 3, 4, 5].all (fun i => (baseEnv threeDoc).predicates categories[i]! == none) &&
  (baseEnv threeDoc).predicates "weapons_uplift_permitted" == none &&
  [0, 6].all (fun i => (baseEnv threeDoc).predicates categories[i]! == some [sortS])
#guard (docOf table (vqlPairs.map (fun p => (p.2, p.1))) []).scale.above ==
  table.scale.above ++ vqlPairs.map (fun p => (p.2, p.1))
def c_e_three : AttDoc :=
  c_e_doc ([0, 1, 2].map (fun i => { c_e_node with content := .unary categories[i]! (.const "s1") })) guard1
#guard (partsOf c_e_three).length == 3 && (names c_e_three).drop 3 ==
  ["attitudes__wants__1", "attitudes__wants__2", "attitudes__wants__3"]

/-! ## 2.5 Elaboration (at-1b) -/

def Γ1 : List String := [sortS, sortC]
def cat0 : String := categories[0]!
def att2 (n : String) : VE.Formula := .binary n (.var 1) (.var 0)
def knows1 : VE.Formula := att2 "attitudes__knows__1"
def ql1 : VE.Formula := att2 "attitudes__thinks_quite_likely__1"
/-- F-AT1's elaborated guard (spec 7.1). -/
def guard1F : VE.Formula := .or (.and knows1 (att2 "attitudes__intends__1")) ql1

instance : Inhabited Key := ⟨⟨.knows, "", none, .top⟩⟩

def nodesOf (A : AttDoc) : Option (List VE.Norms.Node) := (toNorms A).map (·.T.nodes)

#guard guard1.toFormula fat1 Γ1 == some guard1F
#guard atom fat1 (keys fat1)[0]! (.var 1) (some (.var 0)) == knows1 &&
  atom fat1 (keys fat1)[0]! (.const "c0") none == .unary "attitudes__knows__1" (.const "c0")
-- every connective elaborates its operands in order, a binder extends the context, and a condition without a key
-- (holder out of scope) makes the whole formula none, on either side
def knowsA : AFormula := .att (cond .knows cat0)
def qlA : AFormula := .att (cond ql cat0)
def noKey : AFormula := .att { cond .knows cat0 with holder := .var 5 }
#guard (AFormula.base .top).toFormula fat1 [] == some .top && knowsA.toFormula fat1 Γ1 == some knows1 &&
  noKey.toFormula fat1 Γ1 == none && (AFormula.not knowsA).toFormula fat1 Γ1 == some (.not knows1) &&
  (AFormula.not noKey).toFormula fat1 Γ1 == none
#guard (AFormula.and knowsA qlA).toFormula fat1 Γ1 == some (.and knows1 ql1) &&
  (AFormula.or knowsA qlA).toFormula fat1 Γ1 == some (.or knows1 ql1) &&
  (AFormula.implies knowsA qlA).toFormula fat1 Γ1 == some (.implies knows1 ql1)
#guard [AFormula.and, AFormula.or, AFormula.implies].all (fun f =>
  (f noKey qlA).toFormula fat1 Γ1 == none && (f knowsA noKey).toFormula fat1 Γ1 == none)
-- under a binder the same holder index reaches the same sort only because the context grew
#guard (AFormula.all "z" (.att { cond .knows cat0 with holder := .var 2, slot := some (sortS, .var 1) })).toFormula
    fat1 Γ1 == some (.all "z" (.binary "attitudes__knows__1" (.var 2) (.var 1))) &&
  (AFormula.ex "z" (.att { cond .knows cat0 with holder := .var 2, slot := some (sortS, .var 1) })).toFormula
    fat1 Γ1 == some (.ex "z" (.binary "attitudes__knows__1" (.var 2) (.var 1))) &&
  (AFormula.all "z" noKey).toFormula fat1 Γ1 == none && (AFormula.ex "z" noKey).toFormula fat1 Γ1 == none
-- `toNode` and `toNorms`: the rule's fields, its carve-outs in order, in the rule's context; every rule; over `envAtt`
#guard nodesOf fat1 == some [⟨"u0165-s01", "weapons_uplift_permitted", false, guard1F, [], []⟩]
def fat1c : AttDoc :=
  docOf table [] [{ ruleOf "u0165-s01" guard1 with
    sign := true, over := ["other"], carveOuts := [qlA, .base .top, knowsA] }]
#guard nodesOf fat1c == some [⟨"u0165-s01", "weapons_uplift_permitted", true, guard1F, [ql1, .top, knows1], ["other"]⟩]
#guard (nodesOf fat2).map (·.map (·.name)) == some ["u0165-s01", "u0165-s07"]
#guard nodesOf (docOf table [] [ruleOf "a" guard1, ruleOf "b" noKey]) == none &&
  nodesOf (docOf table [] [ruleOf "a" noKey, ruleOf "b" guard1]) == none &&
  (ruleOf "a" noKey).toNode fat1 == none && ARule.toNode fat1 { ruleOf "a" guard1 with carveOuts := [qlA, noKey] } == none &&
  ARule.toNode fat1 { ruleOf "a" guard1 with carveOuts := [noKey, qlA] } == none
#guard match toNorms { threeDoc with lits := ["l1", "l2"] } with
  | some D => D.lits == ["l1", "l2"] && D.T.regulated == threeRegulated && D.T.definitions == threeDefinitions &&
      (names fat1).all (fun n => D.E.predicates n == some [sortC, sortS]) && D.E.sorts == envP.sorts
  | none => false
-- F-AT0 elaborates to its own guard, with nothing added
#guard nodesOf fat0 == some [⟨"u0165-s01", "weapons_uplift_permitted", false, contentOf cat0, [], []⟩]
-- C-e's part: no rule (`toNorms` elaborates the rules alone); its claim is its atom at its holder, closed
#guard nodesOf c_e_part == nodesOf (c_e_doc [] guard1) && partClaim c_e_part c_e_node ==
  some (.unary "attitudes__wants__1" (.const "c0"))
#guard partClaim c_e_part { c_e_node with holder := .var 0 } == none &&
  partClaim { c_e_part with holders := [sortC, sortS] } { c_e_node with holder := .var 0 } == none

/-! ## 2.6 The fixtures of 5.2 and 7.1 that 2.1 to 2.4 did not need (the stub's S5) -/

/-- A fixture document with more vocabulary: extra predicates `ps` in `E`; those of `authored` also in
    `authorPredicates`, and those of `worded` also in the lexical view and the lexicon; constants `cs` of sort
    `situation` in `E`, and those of `spelled` also in the view and the lexicon. -/
def docWith (rules : List ARule) (ps : List (String × List String)) (authored worded : List String)
    (cs spelled : List String) : AttDoc :=
  let d := docOf table [] rules
  { d with
    E := { envP with predicates := preds (predicateList ++ ps),
                     constants := fun c => if cs.contains c then some sortS else none },
    authorPredicates := d.authorPredicates ++ authored,
    lex := lexOf [sortC, sortS]
      (vocabP ++ (ps.filter (fun p => worded.contains p.1)).map (fun p => (p.1, p.2, none)))
      ((spelled.filter cs.contains).map (·, sortS)) }

/-- F-AT1 with its `knows` condition changed to `c`, and extra vocabulary as `docWith`. -/
def withKnows (c : Cond) (ps : List (String × List String)) (authored worded cs spelled : List String) : AttDoc :=
  docWith [ruleOf "u0165-s01" (.or (.and (.att c) (.att (cond (.act .intends) cat0))) qlA)] ps authored worded cs spelled

def withCond (c : Cond) : AttDoc := docOf table [] [ruleOf "u0165-s01" (.att c)]
def longWord : Word := "extraordinarily overwhelmingly and almost certainly likely"
def longTable : Table :=
  { fixtureTable with candidates := [longWord], lowerBound := [(longWord, "x")], above := [], knowsThinks := [] }
def lexNoWording : Lex :=
  { lexP with lexicon := { lexP.lexicon with wordings := lexP.lexicon.wordings.filter (·.1 != cat0) } }
def lexWrongArgs : Lex :=
  { lexP with env := { lexP.env with predicates := lexP.env.predicates.map (fun d =>
      if d.name == cat0 then { d with args := [sortC] } else d) } }
def morePreds (n : Nat) : List (String × List String) := (List.range n).map (fun i => (s!"p{i}", [sortS]))
def fatMore (n : Nat) : AttDoc :=
  docWith fat1.rules (morePreds n) ((morePreds n).map (·.1)) ((morePreds n).map (·.1)) [] []

def guardP (i : Nat) : AFormula :=
  .or (.and (.att (cond .knows categories[i]!))
      (.base (.binary s!"intentionally_does_restricted_action_{i + 1}" (.var 1) (.var 0))))
    (.att (cond ql categories[i]!))
def fat5 : AttDoc := docOf table [] ((List.range 7).map (fun i => ruleOf s!"u0165-s0{i + 1}" (guardP i)))
def guard6 : AFormula := .or (.or knowsA (.att (cond (.thinks "very likely") cat0))) qlA
def fat6 : AttDoc := docOf table [] [ruleOf "u0165-s01" guard6]
def guard7 : AFormula := .or knowsA (.att (cond (.thinks "very likely") cat0))
def table7 : Table := { fixtureTableNoPair with knowsThinks := [("quite likely", "E2.knows-thinks.quite-likely")] }
def fat7 : AttDoc := docOf table7 [] [ruleOf "u0165-s01" guard7]
def fat7item : AttDoc := docOf fixtureTableNoPair [] [ruleOf "u0165-s01" guard7]
def unsaidP : String := "unsaid__weapons_uplift_permitted"
def fat8 : AttDoc :=
  withKnows { cond .knows cat0 with content := .unary unsaidP (.var 0) } [(unsaidP, [sortS])] [unsaidP] [unsaidP] [] []
def guard9 : AFormula := .and (.base (contentOf cat0)) (.not knowsA)
def fat9 : AttDoc := docOf table [] [ruleOf "u0165-s01" guard9]
def closedC1 : Cond := { cond .knows cat0 with slot := none, content := .unary cat0 (.const "s1") }
def ca1 : AttDoc := withKnows { cond .knows cat0 with slot := none, content := .top } [] [] [] [] []
def ca2 : AttDoc := withKnows { cond .knows cat0 with content := .top } [] [] [] [] []
def cb1 : AttDoc := withKnows closedC1 [] [] [] ["s1"] ["s1"]
def cb2 : AttDoc := withKnows { cond .knows cat0 with slot := some (sortS, .const "s1") } [] [] [] ["s1"] ["s1"]
def wantsDoc (φ : VE.Formula) : AttDoc :=
  docWith [ruleOf "u0165-s01" (.or (.and knowsA (.att { cond (.act .wants) cat0 with content := φ })) qlA)] [] [] [] [] []
def cc1 : AttDoc := wantsDoc (contentOf cat0)
def cc2 : AttDoc := wantsDoc (.and (contentOf cat0) (contentOf categories[6]!))
def cd1 : AttDoc := withKnows closedC1 [] [] [] ["s1"] []
def cd2 : AttDoc :=
  withKnows { cond .knows cat0 with content := .unary "extra_case" (.var 0) } [("extra_case", [sortS])] [] [] [] []
/-- C-e's third document: the part with the compound content. -/
def c_e_compound : AttDoc :=
  c_e_doc [{ c_e_node with content := .and (.unary cat0 (.const "s1")) (.unary categories[6]! (.const "s1")) }] guard1

/-- D16: `E` declares a generated name. -/
def d16 : AttDoc :=
  { fat1 with E := { envP with predicates := fun p =>
      if p == "attitudes__knows__1" then some [sortS] else envP.predicates p } }

/-- `checkAtt`'s answer is exactly this text. -/
def fails (A : AttDoc) (text : String) : Bool := errOf (checkAtt A) == text && !WellFormedAtt A
def passes (A : AttDoc) : Bool := errOf (checkAtt A) == "ok" && WellFormedAtt A
def textD14c : String := "UnsupportedProfile: this 'wants' content has no reviewed wording in attitudes@0"
def textD14d : String := "InvalidInput: an attitude condition names a symbol with no entry in the English lexicon"

/-! ## 5.2 `checkAtt`, one guard per row, in the order of the table -/

#guard fails { fat1 with decidedBy := "" } "InvalidInput: attitudes decided_by is not a token"
#guard fails { fat1 with holders := ["robot"] } "UnknownSymbol: Unknown holder sort 'robot'"
#guard fails { fat1 with T := badTableKnows } "InvalidInput: the attitude table is not closure-reviewed"
#guard fails { fat1 with declared := [("as likely as not", "quite likely")] }
  "UnsupportedProfile: a declared scale pair names a word that attitudes@0 does not admit"
#guard fails { fat1 with declared := List.replicate 64 ("very likely", "quite likely") }
  "ResourceLimit: At most 64 order pairs"
#guard fails { fat1 with authorPredicates := fat1.authorPredicates ++ ["attitudes__x"] }
  "InvalidInput: predicate attitudes__x uses the reserved prefix attitudes__"
#guard fails { fat1 with lex := lexNoWording }
  "InvalidInput: the English lexicon fails V1 for predicate mass_casualty_weapon_uplift"
#guard fails { fat1 with lex := lexWrongArgs }
  "InvalidInput: the English lexicon does not describe the document's environment"
#guard fails (withCond { cond ql cat0 with holder := .var 5 }) "UnboundVariable: Variable index 5 is outside its scope"
#guard fails (withCond { cond ql cat0 with holder := .var 0 })
  "InvalidInput: attitude holder of sort situation is not of a holder sort"
#guard fails (withCond (cond (.thinks "unlikely") cat0))
  "UnsupportedProfile: 'thinks it unlikely' is not admitted by attitudes@0"
#guard fails (withCond (cond (.thinks "as likely as not") cat0))
  "UnsupportedProfile: 'thinks it as likely as not' is not admitted by attitudes@0"
#guard fails (withCond { cond ql cat0 with slot := some ("place", .var 0) }) "UnknownSymbol: Unknown slot sort 'place'"
#guard fails (withCond { cond ql cat0 with slot := some (sortS, .var 1) })
  "TypeMismatch: attitude slot term has sort 'claude_instance', not 'situation'"
#guard fails (withCond { cond ql cat0 with content := .ex sortS (.unary cat0 (.var 0)) })
  "InvalidInput: an attitude content has a quantifier"
#guard fails (withCond { cond ql cat0 with content := .binary "weapons_uplift_permitted" (.var 0) (.var 0) })
  "UnknownSymbol: Unknown predicate 'weapons_uplift_permitted'"
#guard fails (withCond { cond ql cat0 with slot := none }) "UnboundVariable: Variable index 0 is outside its scope"
#guard fails ca2 "InvalidInput: an attitude content does not mention its slot"
#guard fails cb2 "InvalidInput: an attitude slot term is not a variable of the guard"
#guard fails cc2 textD14c
#guard fails cd1 textD14d
#guard fails (fatMore 240) "ResourceLimit: MAX_PREDICATES"
#guard fails d16 "DuplicateDeclaration: generated predicate attitudes__knows__1"
#guard fails (docOf longTable [] [ruleOf "u0165-s01" (.att (cond (.thinks longWord) cat0))])
  "ResourceLimit: generated predicate attitudes__thinks_extraordinarily_overwhelmingly_and_almost_certainly_likely__1 exceeds 64 bytes"
#guard fails { fat1 with rules := [ruleOf "u0165-s01" (.and qlA (.base (.unary cat0 (.var 1))))] }
  "TypeMismatch: Predicate 'mass_casualty_weapon_uplift' expects ('situation',), received ('claude_instance',)"

/-! ## 7.4 `checkAtt`, the other side: what passes -/

#guard passes fat1 && passes fat0 && passes fat2 && passes fat3 && passes fat3none && passes fat5 && passes fat6
#guard passes fat7 && passes fat7item && passes fat8 && passes fat9 && passes ca1 && passes cb1 && passes cc1
-- spec 7.1's computed values: F-AT5's 14 generated keys; F-AT9's one key and elaborated guard
#guard (keys fat5).length == 14 && names fat9 == ["attitudes__knows__1"] &&
  guard9.toFormula fat9 Γ1 == some (.and (contentOf cat0) (.not knows1))
-- D14d: admitted exactly when every symbol has its entry (spec 7.4): C-b's first with `s1` in the lexicon, C-d's two
#guard passes cb1 && fails cd1 textD14d && fails cd2 textD14d
-- C-e: the part is admitted and named after the rules' keys; the same node in a guard, and the compound part, are not
#guard passes c_e_part && fails c_e_guard textD14c && fails c_e_compound textD14c
#guard errOf (checkParts c_e_part c_e_part.parts) == "ok" && errOf (checkCond c_e_part [] c_e_node) == textD14c &&
  errOf (checkCond c_e_part [] c_e_node (part := true)) == "ok"
-- D14c reads the wording without its subject (reviews/dri-decisions-20261105-at-1b.md item 1), and only the document's
-- own: a wording `wantsPhrase?` refuses is refused at D14c; one with no subject never gets there (D6a's V3)
def wordedDoc (w : String) : AttDoc :=
  { docWith [ruleOf "u0165-s01" (.att (cond (.act .wants) "safe_p"))] [("safe_p", [sortS])] ["safe_p"] [] [] [] with
    lex := lexOf [sortC, sortS] (vocabP ++ [("safe_p", [sortS], some w)]) [] }
#guard passes (wordedDoc "{0} is safe") && fails (wordedDoc "{0} is not safe") textD14c
#guard fails (wordedDoc "is safe") "InvalidInput: the English lexicon fails V3 for predicate safe_p" &&
  fails (wordedDoc "{0} is {0}") "InvalidInput: the English lexicon fails V3 for predicate safe_p"
-- `renderable` is `renderCheck` of a guard's condition (`part` false): a closed `wants` part is not `renderable`
#guard renderable fat1 (cond .knows cat0) && !renderable c_e_part c_e_node && !renderable fat1 (cond (.act .wants) "absent")
-- at the limit of MAX_PREDICATES, and one over: 15 author predicates and 3 keys, then 238 and 239 more
#guard (fatMore 238).authorPredicates.length + (keys (fatMore 238)).length == VE.Reports.maxPredicates &&
  passes (fatMore 238) && fails (fatMore 239) "ResourceLimit: MAX_PREDICATES"
-- at the bound of the order pairs: 54 declared and the table's 10, then 55
#guard passes { fat1 with declared := List.replicate 54 ("very likely", "quite likely") } &&
  fails { fat1 with declared := List.replicate 55 ("very likely", "quite likely") }
    "ResourceLimit: At most 64 order pairs"

/-! ## 7.5 One guard per theorem (spec 6.1's five) -/

#guard (keys fat1).all (fun k => (fat1.E.predicates (name fat1 k)).isNone && (name fat1 k).utf8ByteSize ≤ 64 &&
  !(fat1.regulated.map (·.name) ++ fat1.definitions.map (·.name)).contains (name fat1 k))
#guard decide ((keys fat2).map (name fat2)).Nodup
#guard (keys fat2).all (fun k => keyOf fat2 (name fat2 k) == some k)
#guard (contentOf cat0).check fat1.E [sortS] && (contentOf cat0).check (envAtt fat1) [sortS]
#guard match toNorms fat1 with
  | some D => VE.Norms.WellFormed D
  | none => false

/-! ## Each branch of 2.6, for the trust mutants (R16): every list's first and last entry, each side of each test -/

#guard [VE.Formula.unary "p" (.var 0), .binary "p" (.var 0) (.const "c"), .binary "p" (.const "c") (.var 0),
    .eq (.var 0) (.const "c"), .eq (.const "c") (.var 0), .not (contentOf "p"), .and (contentOf "p") .top,
    .and .top (contentOf "p"), .or (contentOf "p") .top, .or .top (contentOf "p"), .implies (contentOf "p") .top,
    .implies .top (contentOf "p")].all mentionsSlot
#guard [VE.Formula.top, .bottom, .unary "p" (.var 1), .unary "p" (.const "c"), .binary "p" (.var 1) (.const "c"),
    .eq (.var 1) (.const "c"), .not .top, .and .top .top, .or .top .top, .implies .top .top,
    .all "s" (contentOf "p"), .ex "s" (contentOf "p")].all (!mentionsSlot ·)

/-- F-AT1 with its lexical view changed. -/
def viewed (f : VE.EnglishGrammar.Env → VE.EnglishGrammar.Env) : AttDoc :=
  { fat1 with lex := { lexP with env := f lexP.env } }
def mapPreds (f : VE.EnglishGrammar.PredDecl → VE.EnglishGrammar.PredDecl) (e : VE.EnglishGrammar.Env) :
    VE.EnglishGrammar.Env := { e with predicates := e.predicates.map f }
-- `lexPred`: in the view with `E`'s sorts and matching arity, and with a wording
#guard lexPred fat1 cat0 && !lexPred fat1 "absent" && !lexPred { fat1 with lex := lexWrongArgs } cat0 &&
  !lexPred { fat1 with lex := lexNoWording } cat0 && !lexPred (viewed (mapPreds ({ · with arity := 2 }))) cat0 &&
  !lexPred { fat1 with E := { envP with predicates := fun _ => none } } cat0 &&
  !lexPred { fat1 with lex := { lexP with lexicon := { lexP.lexicon with wordings := [("absent", "{0} is absent")] } } } "absent"
-- `lexTerm`: a variable needs none; a constant in the view with its sort, and with a spelling
#guard lexTerm fat1 (.var 9) && lexTerm c_e_part (.const "s1") && !lexTerm c_e_part (.const "absent") &&
  !lexTerm { c_e_part with E := { c_e_part.E with constants := fun _ => none } } (.const "s1") &&
  !lexTerm { c_e_part with lex := { c_e_part.lex with lexicon := { c_e_part.lex.lexicon with spellings := [] } } }
    (.const "s1") &&
  !lexTerm { c_e_part with E := { c_e_part.E with constants := fun _ => some sortC } } (.const "s1") &&
  !lexTerm { fat1 with lex := { lexP with lexicon := { lexP.lexicon with spellings := [("absent", "absent")] } } }
    (.const "absent")
-- `lexCovers`: every connective reads both operands; both positions of a binary atom and of an equation
def lexA : VE.Formula := .unary cat0 (.const "s1")
def lexB : VE.Formula := .unary "absent" (.const "s1")
def lexC : VE.Formula := .unary cat0 (.const "absent")
#guard [VE.Formula.top, .bottom, lexA, .binary "weapons_uplift_permitted" (.var 0) (.const "s1"), .eq (.var 0) (.const "s1"),
    .not lexA, .all "x" lexA, .ex "x" lexA, .and lexA lexA, .or lexA lexA, .implies lexA lexA].all (lexCovers c_e_part)
#guard [lexB, lexC, .binary "absent" (.var 0) (.var 0), .binary "weapons_uplift_permitted" (.const "absent") (.var 0),
    .binary "weapons_uplift_permitted" (.var 0) (.const "absent"), .eq (.const "absent") (.var 0),
    .eq (.var 0) (.const "absent"), .not lexB, .all "x" lexB, .ex "x" lexB, .and lexB lexA, .and lexA lexB,
    .or lexB lexA, .or lexA lexB, .implies lexB lexA, .implies lexA lexB].all (!lexCovers c_e_part ·)
-- `renderCheck`: each failure with its text, one holder or slot symbol at a time; each mode's `wants` shape
def wc (slot : Option (String × VE.Term)) (φ : VE.Formula) : Cond :=
  { holder := .const "c0", mode := .act .wants, slot := slot, content := φ }
#guard errOf (renderCheck c_e_part (wc (some (sortS, .var 0)) (contentOf cat0))) == "ok" &&
  errOf (renderCheck c_e_part (wc none lexA) true) == "ok" && errOf (renderCheck c_e_part (wc none lexA)) == textD14c
-- a part's wording is found wherever it stands in the lexicon, as a slotted condition's is
#guard [categories[1]!, "weapons_uplift_permitted"].all (fun p =>
  errOf (renderCheck c_e_part (wc none (.unary p (.const "s1"))) true) == "ok" &&
  errOf (renderCheck c_e_part (wc (some (sortS, .var 0)) (.unary p (.var 0)))) == "ok")
#guard errOf (renderCheck c_e_part (wc (some (sortS, .var 0)) (contentOf "absent"))) == textD14c &&
  errOf (renderCheck c_e_part (wc none lexB) true) == textD14c &&
  errOf (renderCheck c_e_part (wc none (.binary cat0 (.const "s1") (.const "s1"))) true) == textD14c &&
  errOf (renderCheck c_e_part (wc none (contentOf cat0)) true) == textD14c
#guard errOf (renderCheck c_e_part { wc none lexB with mode := .knows }) == textD14d &&
  errOf (renderCheck c_e_part { wc none lexA with mode := .knows, holder := .const "absent" }) == textD14d &&
  errOf (renderCheck c_e_part { wc none lexA with mode := ql }) == "ok" &&
  errOf (renderCheck c_e_part { wc none lexA with mode := .act .says }) == "ok"
#guard errOf (renderCheck c_e_part { wc (some (sortS, .const "s1")) (contentOf cat0) with mode := .knows }) ==
  "InvalidInput: an attitude slot term is not a variable of the guard"
-- `lexAgrees`: generated symbols aside; each conjunct on its own, with the offending entry first and last
def gensort : VE.EnglishGrammar.SortDecl := { name := "gen", generated := true }
def robot : VE.EnglishGrammar.SortDecl := { name := "robot" }
def genpred : VE.EnglishGrammar.PredDecl := { name := "gen_p", arity := 1, args := [sortS], generated := true }
def extra : VE.EnglishGrammar.PredDecl := { name := "extra", arity := 1, args := [sortS] }
def genconst : VE.EnglishGrammar.ConstDecl := { name := "gc", sort := "gen", generated := true }
def undeclared : VE.EnglishGrammar.ConstDecl := { name := "gc", sort := sortS }
#guard lexAgrees fat1 && lexAgrees (viewed ({ · with sorts := gensort :: lexP.env.sorts ++ [gensort] })) &&
  lexAgrees (viewed ({ · with predicates := genpred :: lexP.env.predicates ++ [genpred] })) &&
  lexAgrees (viewed ({ · with constants := [genconst, genconst] })) && lexAgrees c_e_part
#guard [viewed ({ · with sorts := robot :: lexP.env.sorts }), viewed ({ · with sorts := lexP.env.sorts ++ [robot] }),
    viewed ({ · with sorts := lexP.env.sorts.drop 1 }), viewed ({ · with sorts := lexP.env.sorts.dropLast }),
    viewed ({ · with sorts := lexP.env.sorts.drop 1 ++ [gensort] }),
    viewed ({ · with predicates := extra :: lexP.env.predicates }),
    viewed ({ · with predicates := lexP.env.predicates ++ [extra] }),
    viewed ({ · with predicates := lexP.env.predicates.drop 1 }),
    viewed ({ · with predicates := lexP.env.predicates.dropLast }),
    { fat1 with authorPredicates := "extra" :: fat1.authorPredicates, lex := { lexP with env := { lexP.env with
        predicates := extra :: lexP.env.predicates } } },
    viewed (mapPreds ({ · with arity := 7 })), { fat1 with lex := lexWrongArgs },
    viewed ({ · with constants := [undeclared] }), viewed ({ · with constants := [genconst, undeclared] }),
    viewed ({ · with constants := [undeclared, genconst] })].all (!lexAgrees ·)
-- `checkCond`, `checkConds`, `checkParts`, `checkNames`: the first and the last entry both count
#guard errOf (checkConds fat1 []) == "ok" && errOf (checkParts fat1 []) == "ok" && errOf (checkNames fat1 []) == "ok" &&
  errOf (checkConds fat1 (condsOf fat1)) == "ok"
def badCond : List String × Cond := ([], cond .knows cat0)
#guard errOf (checkConds fat1 [badCond, (Γ1, cond .knows cat0)]) == "UnboundVariable: Variable index 1 is outside its scope" &&
  errOf (checkConds fat1 [(Γ1, cond .knows cat0), badCond]) == "UnboundVariable: Variable index 1 is outside its scope"
#guard errOf (checkParts c_e_part [c_e_node, cond .knows cat0]) == "UnboundVariable: Variable index 1 is outside its scope" &&
  errOf (checkParts c_e_part [cond .knows cat0, c_e_node]) == "UnboundVariable: Variable index 1 is outside its scope"
-- a part is closed: a holder or slot variable fails `termSort`, a slot at a constant D14b (spec 2.6)
#guard fails (c_e_doc [{ c_e_node with holder := .var 0 }] guard1) "UnboundVariable: Variable index 0 is outside its scope" &&
  fails (c_e_doc [{ c_e_node with slot := some (sortS, .var 0), content := contentOf cat0 }] guard1)
    "UnboundVariable: Variable index 0 is outside its scope" &&
  fails (c_e_doc [{ c_e_node with mode := .knows, slot := some (sortS, .const "s1"), content := contentOf cat0 }] guard1)
    "InvalidInput: an attitude slot term is not a variable of the guard"
#guard errOf (checkCond fat1 Γ1 (cond .knows cat0)) == "ok" && errOf (checkCond fat1 Γ1 (cond (.act .says) cat0)) == "ok" &&
  errOf (checkCond { fat1 with T := preReportTable } Γ1 (cond .knows cat0)) ==
    "UnsupportedProfile: 'knows' is not admitted by attitudes@0" &&
  errOf (checkCond fat1 Γ1 { cond ql cat0 with content := .binary cat0 (.var 0) (.var 0) }) ==
    "TypeMismatch: Predicate 'mass_casualty_weapon_uplift' has arity 1, not 2" &&
  errOf (checkCond fat1 Γ1 { cond ql cat0 with slot := some (sortC, .var 1) }) ==
    "TypeMismatch: Predicate 'mass_casualty_weapon_uplift' expects ('situation',), received ('claude_instance',)"
-- a closed content is typed in the empty context, a slotted one in the slot's alone
#guard errOf (checkCond fat1 Γ1 { cond ql cat0 with content := .unary cat0 (.var 1) }) ==
  "UnboundVariable: Variable index 1 is outside its scope"
-- `checkAtt`'s lists: the last entry of each counts
#guard fails { fat1 with holders := [sortC, "robot"] } "UnknownSymbol: Unknown holder sort 'robot'" &&
  fails { fat1 with holders := ["robot", sortC] } "UnknownSymbol: Unknown holder sort 'robot'"
#guard [[("very likely", "quite likely"), ("very likely", "as likely as not")],
    [("very likely", "as likely as not"), ("very likely", "quite likely")]].all (fun ps =>
  fails { fat1 with declared := ps } "UnsupportedProfile: a declared scale pair names a word that attitudes@0 does not admit")
-- the first and the last admitted word, on each side of a declared pair
#guard passes { fat1 with declared := [("almost certain", "more likely than not"), ("more likely than not", "almost certain")] }
-- several failures of the lexicon: the first is named
#guard fails { fat1 with lex := { lexP with lexicon := { lexP.lexicon with
    wordings := lexP.lexicon.wordings.filter (fun w => w.1 != cat0 && w.1 != categories[1]!) } } }
  "InvalidInput: the English lexicon fails V1 for predicate mass_casualty_weapon_uplift"
#guard passes { fat1 with holders := [sortS, sortC] } && passes { fat1 with holders := [sortC, sortS] } &&
  fails { fat1 with authorPredicates := "attitudes__x" :: fat1.authorPredicates }
    "InvalidInput: predicate attitudes__x uses the reserved prefix attitudes__"
-- `checkNames`: each check, on the first and the last key; a regulated name and a defined one
def wordsTable (ws : List Word) : Table :=
  { candidates := ws, lowerBound := ws.map (·, "x"), above := [], factive := some "x", knowsBelieves := none,
    knowsThinks := [] }
def thinksDoc (ws : List Word) : AttDoc :=
  docOf (wordsTable ws) [] [ruleOf "u0165-s01" (ws.foldr (fun w g => .or (.att (cond (.thinks w) cat0)) g) (.base .top))]
#guard fails (thinksDoc ["a:b"]) "InvalidInput: generated predicate attitudes__thinks_a:b__1 contains ':'" &&
  fails (thinksDoc ["a", "a:b"]) "InvalidInput: generated predicate attitudes__thinks_a:b__1 contains ':'"
#guard fails (thinksDoc ["a b", "a_b"]) "InvalidInput: generated predicate names collide" && passes (thinksDoc ["a", "b"])
#guard errOf (checkNames fat1 (keys fat1).reverse) == "ok"
def namedAs (rs ds : List String) : AttDoc :=
  { fat1 with regulated := rs.map (fun n => { regulatedP with name := n }),
              definitions := ds.map (fun n => { name := n, args := [], body := .top }) }
#guard [namedAs ["attitudes__knows__1", "x"] [], namedAs ["x", "attitudes__knows__1"] [],
    namedAs [] ["attitudes__knows__1", "x"], namedAs [] ["x", "attitudes__knows__1"],
    namedAs ["attitudes__knows__1"] ["x"], namedAs ["x"] ["attitudes__knows__1"]].all (fun A =>
  errOf (checkNames A (keys fat1)) == "DuplicateDeclaration: generated predicate attitudes__knows__1")
-- 64 bytes is the limit: a word whose name has exactly 64 passes, one byte more does not
def wordOf (n : Nat) : Word := String.mk (List.replicate n 'a')
#guard (name (thinksDoc [wordOf 43]) (keys (thinksDoc [wordOf 43]))[0]!).utf8ByteSize == 64 && passes (thinksDoc [wordOf 43]) &&
  (errOf (checkAtt (thinksDoc [wordOf 44]))).startsWith "ResourceLimit: generated predicate"

/-! ## `AWellFormed`: decided, with a proof that the decision is the predicate, so its guards can fail -/

def awf (A : AttDoc) : List String → AFormula → Bool
  | Γ, .base φ => φ.check A.E Γ
  | Γ, .att c => match c.key A Γ with
    | some k => (keys A).contains k && c.slot.all (fun p => p.2.sortOf A.E Γ == some p.1)
    | none => false
  | Γ, .not a => awf A Γ a
  | Γ, .and a b | Γ, .or a b | Γ, .implies a b => awf A Γ a && awf A Γ b
  | Γ, .all s a | Γ, .ex s a => A.E.sorts.contains s && awf A (s :: Γ) a

theorem awf_iff (A : AttDoc) (Γ : List String) (a : AFormula) : awf A Γ a = true ↔ AWellFormed A Γ a := by
  induction a generalizing Γ with
  | base φ => exact VE.check_iff_wellFormed A.E Γ φ
  | att c =>
    simp only [awf, AWellFormed]
    cases hk : c.key A Γ <;> cases c.slot <;> simp
  | not a ih => exact ih Γ
  | and a b iha ihb | or a b iha ihb | implies a b iha ihb =>
    simp only [awf, AWellFormed, Bool.and_eq_true, iha, ihb]
  | all s a ih | ex s a ih =>
    simp only [awf, AWellFormed, Bool.and_eq_true, ih, List.contains_iff_mem]

#guard awf fat1 Γ1 guard1 && awf fat1 Γ1 (.base (contentOf cat0)) && awf fat1 Γ1 (.not knowsA)
#guard !awf fat1 Γ1 (.base (contentOf "absent")) && !awf fat1 Γ1 noKey && !awf fat1 Γ1 (.not noKey)
-- a condition outside the document's keys (spec 11 item 6), and a slot term of another sort, are not well formed
#guard !awf fat1 Γ1 (.att (cond (.act .wants) cat0)) &&
  !awf fat1 Γ1 (.att { cond .knows cat0 with slot := some (sortC, .var 0) })
#guard [AFormula.and, AFormula.or, AFormula.implies].all (fun f => awf fat1 Γ1 (f knowsA qlA) &&
  !awf fat1 Γ1 (f noKey qlA) && !awf fat1 Γ1 (f knowsA noKey))
#guard [AFormula.all, AFormula.ex].all (fun f => awf fat1 Γ1 (f sortS (.base .top)) && !awf fat1 Γ1 (f "place" (.base .top)) &&
  !awf fat1 Γ1 (f sortS noKey))

end VE.Attitudes.Examples
