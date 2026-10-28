import VE.Acts.Readings
import VE.Acts.RuleExamples
import VE.Acts.TableExamples

/-! Fixtures of the meaning, `readings`, `read` and `analyse` (docs/spec/act-phrases.md 5.3, 5.4, 11.2, 11.2b).

The readings of G5 to L0 by value, each tree of ap-3's hand-written ones (`TableExamples`) now built by `meaning`; the
meaning counts of the 13 `ap0` rows under D9 (i); and each check of the meaning on both sides of its boundary: D9 (i)
at the first and the last part of a list whose marker is written once, and `atomOk`'s object, argument-marker and
modifier-marker conditions.
-/

namespace VE.Acts.MeaningExamples
open VE.Acts VE.Acts.Examples VE.Acts.RuleExamples VE.Acts.TableExamples
open VE.Acts.Lexical (Tok)

def toks (fx : List String) (s : String) : Array Tok := ((Lexical.lex fx s).toOption.getD []).toArray
def rd (V : Vocab) (fx : List String) (s : String) (b := stepBudget) : Listing Act := readings V rawCap b (toks fx s)
def rd1 (V : Vocab) (fx : List String) (s : String) : ReadOutcome Act := read V rawCap stepBudget (toks fx s)
/-- The number of readings; `none` is the limit outcome. -/
def n (V : Vocab) (fx : List String) (s : String) : Option Nat :=
  match rd V fx s with | .ok xs => some xs.length | .limit => none
/-- Every derivation's meaning, duplicates kept: the plan's seeded bug (a third premodifier rule) makes A8's 3. -/
def meanings (V : Vocab) (fx : List String) (s : String) : List Act :=
  ((parsed V fx s).getD []).filterMap (valueOf (meaning V))

/-! ### 11.2: G5 to L0 -/

def fx5 : List String := ["other countries"]
def obj5 (h : String) (inn : Bool) : Atom :=
  ⟨true, false, [h], [("", .one (w "asylum from persecution"))], if inn then [.prep "in" (.fixed 0)] else []⟩
-- G5 and G5d's order: `in [other countries]` on the last item, then on both
#guard rd V5 fx5 g5 == .ok [.all false false [obj5 "seek" false, obj5 "enjoy" true],
  .all false false [obj5 "seek" true, obj5 "enjoy" true]]
#guard rd1 V5 fx5 g5 matches .many _ _
#guard rd V5 [] g5 == .ok [] && rd1 V5 [] g5 == .none                                                      -- G5b
#guard rd1 V6 fx6 "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment" == .ok g6
#guard rd1 V7 fx7 "{0} be held by secret vote or by equivalent free voting procedures" == .ok g7          -- G7
def fx8 : List String := ["the cultural life of the community", "scientific advancement and its benefits"]
/-- G8's tree with *freely* on the atoms `fr` says. -/
def g8t (fr : List Bool) : Act := .all false false ((["participate", "enjoy", "share"].zip
  [("in", Part.fixed 0), ("", w "the arts"), ("in", .fixed 1)]).zipWith (fun (h, m, p) f =>
    ⟨true, false, [h], [(m, .one p)], if f then [.adv "freely"] else []⟩) fr)
#guard rd V8 fx8 g8 == .ok [g8t [true, false, false], g8t [true, true, true]]                             -- G8
#guard meanings V8 fx8 g8 == [g8t [true, false, false], g8t [true, true, true]]                           -- A8
-- `readings_exact` right to left: *freely* on a middle item alone, or on the outer two, is not derived
#guard [g8t [false, true, false], g8t [true, false, true]].all (fun A => !(meanings V8 fx8 g8).contains A)
#guard rd V9 ["the right to change their nationality"]
  "{0} be arbitrarily deprived of their nationality nor denied the right to change their nationality" ==
  .ok [g9 false, g9 true]                                                                                  -- G9
#guard rd V10 ["other lack of livelihood"] ("{0} to security in the event of unemployment, sickness, " ++
  "disability, widowhood, old age or other lack of livelihood in circumstances beyond their control") ==
  .ok [g10 false, g10 true]                                                                                -- G10
#guard rd1 V11 fx11 "{0} to take part in {1} directly or through freely chosen representatives" == .ok g11  -- G11
#guard rd V12 [] "{0} to form and to join trade unions for the protection of their interests" ==
  .ok [g12 false, g12 true]                                                                                -- G12
#guard rd1 V14 ["its core identity or principles", "to be human", "genuinely deceptive tactics that could harm users",
  "health or safety", "Anthropic’s guidelines"] ("{0} abandon its core identity or principles, claim to be human, " ++
  "use genuinely deceptive tactics that could harm users, endanger health or safety, or act against " ++
  "Anthropic’s guidelines") == .ok g14v                                                                    -- G14v
#guard rd1 V5k [] "{0} to seek asylum or to enjoy asylum and to keep asylum" == .none                     -- G38
#guard rd1 V5k [] "{0} to seek, enjoy and to keep asylum" == .none                                        -- G39
#guard [6, 7, 8].map (fun k => n V5 cities (ln k)) == [some 64, none, none]                               -- L6, L7, L8
#guard rd1 V5 cities (ln 7) == .limit && rd V5 fx5 g5 0 == .limit                                         -- L7, L0
-- `analyse`: a simple act only for one meaning that is `one`
#guard analyse V7 rawCap stepBudget (toks fx7 "{0} be held by secret vote or by equivalent free voting procedures") ==
  some held
#guard analyse V6 rawCap stepBudget
  (toks fx6 "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment") == none &&
  [toks fx5 g5, toks [] g5].all (analyse V5 rawCap stepBudget · == none)                                -- any; many, none

/-! ### Joins, function words and shared elements -/

def V6b : Vocab := frames [fr "subjected" ["to", "by"] ["to"] []]
def sub (to : Bool) (p : Part) (by_ : List (String × Filler)) : Atom := ⟨to, true, ["subjected"], ("to", .one p) :: by_, []⟩
-- a split marker's *and* is `all true true`; *nor* is `any true true`; *to be* is both function words; an argument
-- after the split construct goes to every part
#guard rd1 V6 [] "{0} be subjected to torture and to exile" == .ok (.all true true [sub false (w "torture") [],
  sub false (w "exile") []])
#guard rd1 V6 [] "{0} to be subjected to torture nor to exile" == .ok (.any true true [sub true (w "torture") [],
  sub true (w "exile") []])
#guard rd1 V6b [] "{0} be subjected to torture or to exile by the state" == .ok (.any false true
  [sub false (w "torture") [("by", .one (w "the state"))], sub false (w "exile") [("by", .one (w "the state"))]])
-- joined modifiers by *and*: `all true false`
#guard rd1 V11 fx11 "{0} to take part in {1} directly and through freely chosen representatives" ==
  .ok (.all true false [directly, through])

/-! ### 11.2b: the 13 `ap0` rows, meaning counts under D9 (i) -/

#guard [n (ap 0) [] "{0} be held in slavery or servitude",                                                -- X024
  n (ap 1) [] "{0} be subjected to arbitrary arrest, detention or exile",                                  -- X037
  n (ap 1) [] "{0} be subjected to arbitrary interference with their privacy, family, home or correspondence",
  n (ap 2) [] ("{0} be subjected to arbitrary interference with their privacy, family, home or correspondence, " ++
    "nor to attacks upon their honour and reputation"),                                                   -- X045ab
  n (ap 3) [] "{0} to marry and to found a family",                                                        -- X057
  n (ap 4) [] "{0} to change their religion or belief",                                                    -- X067
  n (ap 5) [] ("{0} either alone or in community with others and in public or private, to manifest their " ++
    "religion or belief in teaching, practice, worship and observance"),                                   -- X068
  n (ap 6) [] "{0} to seek, receive and impart information and ideas through any media and regardless of frontiers",
  n (ap 7) [] "{0} promote understanding, tolerance and friendship among all nations, racial or religious groups",
  n (ap 8) [] "{0} give Claude a specific set of instructions, a persona, or information",                 -- X0062
  n (ap 9) [] "{0} actively deceive {1} about the existence of a system prompt or its content",            -- X0156
  n (ap 10) [s05] ("{0} engage or assist in " ++ s05),                                                     -- X0165s05
  n (ap 11) [s06] ("{0} engage or assist any individual or group with " ++ s06)] ==                       -- X0165s06
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0].map some

/-! ### D9 (i) on both sides: a joined filler whose marker is written once -/

def Vs : Vocab := frames [fr "change" [""] [""] []]
-- an object list (`O`): one-word ends, a long middle part and a fixed phrase or slot at an end are read; a first or a
-- last part of two words is refused
#guard ["{0} to change religion or belief", "{0} to change belief, their old religion or faith",
  "{0} to change {1} or belief"].map (n (ap 4) []) == [some 1, some 1, some 1]
#guard n (ap 4) ["their religion"] "{0} to change their religion or belief" == some 1
#guard ["{0} to change their religion or belief", "{0} to change belief or their religion",
  "{0} to change {1} or their belief"].map (n (ap 4) []) == [some 0, some 0, some 0]
-- a split object (`OS`) and a split marker written once (`OL`), each side
#guard ["{0} to change religion or belief", "{0} to change their religion or belief",
  "{0} to change religion or their belief"].map (n Vs []) == [some 1, some 0, some 0]
#guard [n V10 [] "{0} to security in the event of unemployment or sickness",
  n V10 [] "{0} to security in the event of long unemployment or sickness",
  n (ap 0) [] "{0} be held in slavery or forced servitude"] == [some 1, some 0, some 0]
-- a repeated marker (`RL`) is not refused: two-word parts are read
#guard n V7 [] "{0} be held by secret vote or by open vote" == some 1

/-! ### `atomOk` on both sides -/

def Vm : Vocab := frames [fr "seek" [""] [] ["in"], fr "enjoy" [""] [] ["from"]]
def Va : Vocab := frames [fr "seek" ["", "from"] [] [], fr "enjoy" [""] [] []]
-- the object: required (all bare items have none) and forbidden (X057, above); a shared object fits
#guard [n V5 [] "{0} to seek or to enjoy", n V5 [] "{0} to seek or to enjoy asylum"] == [some 0, some 1]
-- a modifier marker: on both items when both frames list it, on the last only when the first's does not
#guard [n V5 fx5 "{0} to seek and to enjoy in other countries asylum",
  n Vm fx5 "{0} to seek and to enjoy from other countries asylum"] == [some 2, some 1]
-- an argument marker shared from the last item: refused when the first item's frame does not list it
#guard [n Va [] "{0} to enjoy and to seek asylum from persecution", n Va [] "{0} to seek and to enjoy asylum"] ==
  [some 0, some 1]
#guard atomOk V5 (obj5 "seek" true) && !atomOk V5 { obj5 "seek" true with head := ["keep"] } &&
  !atomOk V8 ⟨true, false, ["enjoy"], [("", .one (w "the arts"))], [.adv "slowly"]⟩ &&
  atomOk V8 ⟨true, false, ["enjoy"], [("", .one (w "the arts"))], [.adv "freely"]⟩

end VE.Acts.MeaningExamples
