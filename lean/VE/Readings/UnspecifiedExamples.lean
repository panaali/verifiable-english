import VE.Readings.UnspecifiedWire
import VE.Readings.Examples

/-! The fixtures of RD-1 (docs/spec/readings-defaults.md 8.1) and RD-2a's admission limits (8.3: F-ND4, F-ND5,
F-ND10), each a `#guard` on `fillDoc` and on separation under
the completion; each iff claim has a fixture for each direction. F-ND11 is the counterexample that made
`attached_fillDoc` take `singlyAttached` (the approved statement had `fillNamesFree` only). -/
namespace VE.Readings.UnspecifiedExamples
open VE.Readings
open VE.Norms (Regulated)
open VE.Norms.Checks (envOf perm oblig)
open VE.Rights.Examples (noSoft strictNode)
open VE.Rights (RightsDoc correlate)
open VE.SoftNorms (SoftNode soften)

def regs1 : List Regulated :=
  [oblig "help_required" ["agent", "user"] false (some "help_permitted") "{0} help {1}",
   perm "help_permitted" ["agent", "user"] false "{0} help {1}"]
def frameOf (regs : List Regulated) (base : List (String × List String)) : RightsDoc where
  soft := ⟨envOf ["agent", "user"] (base ++ regs.map (fun r => (r.name, r.sorts))), [], noSoft, ⟨regs, [], []⟩⟩
  rights := ⟨[], [], [], []⟩
  rs := []
  limits := []
  bars := []
  outsideCites := []
  sourceOrder := some []
def frame1 : RightsDoc := frameOf regs1 [("asks", ["user", "agent"])]
def mustHelp : SoftNode := strictNode "must-help" "help_required" true
def mustHelpAsks : SoftNode := strictNode "must-help" "help_required" true (.binary "asks" (.var 0) (.var 1))
def cand (id : String) (M : SoftNode) : Candidate := ⟨id, some (.norm M), [], []⟩
def rs1 : ReadingSet := ⟨"rs_1", "u1", 1, [cand "every" mustHelp, cand "asks" mustHelpAsks]⟩
def unspec1 : List String := ["help_required", "help_permitted"]
/-- F-ND1: "every agent must help each user", against "… each user who asks". -/
def ND1 : NDoc := ⟨⟨.norms, frame1, [.set rs1], [], []⟩, unspec1⟩
/-- F-ND0: F-ND1 with no unspecified predicate. -/
def ND0 : NDoc := { ND1 with unspec := [] }
/-- Two W1 documents agree on the sorts, the literals, the regulated predicates, the rules and the predicates of
    every listed name (`VE.Environment` holds its predicates as a function). -/
def sameOn (names : List String) (A B : VE.Norms.Doc) : Bool :=
  A.E.sorts == B.E.sorts && names.all (fun n => A.E.predicates n == B.E.predicates n) && A.lits == B.lits &&
    A.T.regulated == B.T.regulated && A.T.nodes == B.T.nodes
def names1 : List String :=
  ["asks", "help_required", "help_permitted", "unsaid__help_required", "unsaid__help_permitted", "unsaid__asks"]

/-! ### F-ND1 -/

-- 1.1: the `F_p` units come last, named by their rules
#guard (fillDoc ND1).items.map itemUnit == ["u1", "unsaid--help-required", "unsaid--help-permitted"]
-- 1.2: both readings' root rules are placed under `F_p`
#guard ((fillDoc ND1).sets.flatMap (·.candidates)).map (fun a => a.content.map (fun
  | .norm M => M.over | _ => [])) == [some ["unsaid--help-required"], some ["unsaid--help-required"]]
-- 1.3: the facts admission needs
#guard (normsShaped ND1.D, fillNamesFree ND1, WellFormedDoc ND1.D, WellFormedDoc (fillDoc ND1), WellFormedND ND1) ==
  (true, true, true, true, true)
-- 1.4: the four equalities on the instance
#guard [0, 1].all (fun i => sameOn names1 (soften (correlate (one (fillDoc ND1) "rs_1" i).1))
  (VE.NormDefaults.fill (oneU ND1 "rs_1" i)))
#guard sameOn names1 (soften (correlate (free (fillDoc ND1)).1)) (VE.NormDefaults.fill (freeU ND1))
#guard [[("rs_1", 0)], [("rs_1", 1)]].all (fun c => sameOn names1 (soften (correlate (choiceDoc (fillDoc ND1) c).1))
  (VE.NormDefaults.fill (choiceU ND1 c)))
#guard sameOn (names1 ++ ["ve__bit__1__0"]) (soften (correlate (sup (fillDoc ND1)).1)) (VE.NormDefaults.fill (supU ND1))
-- the equalities compare whole rule lists: a wrong filling would fail them
#guard (soften (correlate (one (fillDoc ND1) "rs_1" 0).1)).T.nodes.map (·.name) ==
  ["must-help", "unsaid--help-required", "unsaid--help-permitted"]

/-- One agent `a`, one user `u`, nobody asks; the filling of `help_permitted` is `permitted`. -/
def base1 (permitted : List (List String)) : VE.FiniteModel String where
  domains s := match s with | "agent" => ["a"] | "user" => ["u"] | _ => []
  constants _ := none
  relations p := if p == "unsaid__help_permitted" then permitted else []
def probe1 : Probe String := .outcome "help_required" ["a", "u"]
def sit1 (permitted : List (List String)) (v : Bool) : Situation String := ⟨base1 permitted, [], [], probe1, v⟩

-- 1.5: separated with witness 0, whose `Fill_T` holds
#guard (separates (fillDoc ND1) "rs_1" 0 1 (sit1 [["a", "u"]] true), fillHolds ND1 "rs_1" 0 (base1 [["a", "u"]])) ==
  (true, true)
-- 1.6: the same base without the permission: the witness's filling breaks its `Fill_T`
#guard (separates (fillDoc ND1) "rs_1" 0 1 (sit1 [] true), fillHolds ND1 "rs_1" 0 (base1 [])) == (true, false)
-- 1.7: separated the other way: the shared filling answers reading 1's gap 'no'
#guard (separates (fillDoc ND1) "rs_1" 1 0 (sit1 [["a", "u"]] false), fillHolds ND1 "rs_1" 1 (base1 [["a", "u"]])) ==
  (true, true)
-- 1.8: not separated
#guard (separates (fillDoc ND1) "rs_1" 1 0 (sit1 [["a", "u"]] true),
  separates (fillDoc ND1) "rs_1" 0 1 (sit1 [["a", "u"]] false)) == (false, false)

/-- F-ND1 with a narrowing `n1` keeping reading `every`. -/
def ND1n : NDoc := { ND1 with D := { ND1.D with narrowings := [⟨"n1", "rs_1", 1, ["every"]⟩] } }
-- 1.9: `compatible_fillDoc`, both directions
#guard [[("rs_1", 0)], [("rs_1", 1)]].map (fun c => (compatible (fillDoc ND1n) c, compatible ND1n.D c)) ==
  [(true, true), (false, false)]
-- 1.10: the compatible choices
#guard (choices ND1.D, choices ND1n.D) == ([[("rs_1", 0)], [("rs_1", 1)]], [[("rs_1", 0)]])

/-! ### F-ND5: the collision `fillNamesFree` excludes (review A1) -/

def beHelpful : SoftNode := strictNode "be-helpful" "help_required" true
def rs5 : ReadingSet := ⟨"rs_1", "u1", 1, [cand "named" (strictNode "unsaid--help-required" "help_permitted" true)]⟩
def ND5 : NDoc := ⟨⟨.norms, frame1, [.fixed "u0" (.norm beHelpful) [], .set rs5], [], []⟩, unspec1⟩

-- 5.1: S1 alone admits it; `fillNamesFree` refuses it
#guard (fillNamesFree ND5, WellFormedDoc ND5.D, normsShaped ND5.D) == (false, true, true)
-- 5.2: `u0` becomes attached to `rs_1` after filling
#guard (attached ND5.D "u0", attached (fillDoc ND5) "u0") == ([], ["rs_1"])
-- 5.3: `free (fillDoc N)` drops `be-helpful` while `fill (freeU N)` keeps it
#guard ((soften (correlate (free (fillDoc ND5)).1)).T.nodes.map (·.name),
  (VE.NormDefaults.fill (freeU ND5)).T.nodes.map (·.name)) ==
  (["unsaid--help-required", "unsaid--help-permitted"],
   ["be-helpful", "unsaid--help-required", "unsaid--help-permitted"])
#guard !sameOn names1 (soften (correlate (free (fillDoc ND5)).1)) (VE.NormDefaults.fill (freeU ND5))

/-! ### F-ND0: no unspecified predicate, `fillDoc` adds nothing -/

#guard (fillDoc ND0).items.map itemUnit == ["u1"]
#guard (fillDoc ND0).items == ND0.D.items
#guard sameOn names1 (soften (correlate (free (fillDoc ND0)).1)) (soften (correlate (free ND0.D).1))

/-! ### F-ND11: `attached` as a list needs `singlyAttached`

Four fixed units over three sets, each unit's rule naming others in its `over`: unit `u0` uses the names of set
`s0`, of itself and of `u1`. Every name is free of `unsaid--` and the document is norms-shaped, yet `u0`'s
attached sets come out in another order after filling, because `attached` iterates once per item and the level
lists of a unit attached to several sets alternate. The members agree (`mem_attached_fillDoc`); the lists agree
when no unit is attached to two sets (`attached_fillDoc`). -/

def ruleOver (n : String) (over : List String) : SoftNode := { strictNode n "help_permitted" true with over := over }
def itemsK : List Item :=
  [.fixed "u0" (.norm (ruleOver "r-zero" ["c-zero", "r-zero", "r-one"])) [],
   .fixed "u1" (.norm (ruleOver "r-one" ["c-one", "r-three"])) [],
   .fixed "u2" (.norm (ruleOver "r-two" ["r-one"])) [],
   .fixed "u3" (.norm (ruleOver "r-three" ["c-two", "r-zero", "r-one"])) [],
   .set ⟨"s0", "v0", 1, [cand "a" (strictNode "c-zero" "help_permitted" true)]⟩,
   .set ⟨"s1", "v1", 1, [cand "a" (strictNode "c-one" "help_permitted" true)]⟩,
   .set ⟨"s2", "v2", 1, [cand "a" (strictNode "c-two" "help_permitted" true)]⟩]
def NK : NDoc := ⟨⟨.norms, frame1, itemsK, [], []⟩, ["help_required"]⟩

#guard (fillNamesFree NK, normsShaped NK.D, singlyAttached NK.D) == (true, true, false)
#guard (attached NK.D "u0", attached (fillDoc NK) "u0") == (["s2", "s0", "s1"], ["s0", "s1", "s2"])
#guard ["u0", "u1", "u2", "u3"].all (fun u =>
  (attached NK.D u).all ((attached (fillDoc NK) u).contains ·) &&
    (attached (fillDoc NK) u).all ((attached NK.D u).contains ·))
-- and with one set per unit the lists agree (F-ND1 has no fixed unit; F-ND5's `u0` is attached to none)
#guard (attached ND5.D "u0" == [], singlyAttached ND1.D) == (true, true)

/-! ### RD-2a (8.3): admission's limits under the completion

F-ND4 and F-ND10 are sized against `checkAuthorN`'s rule limit (rules plus unspecified predicates at most 256). The
counts are those below (F-ND4, and that the documents within the limit pass, are checked through the service in
`tests/test_readings_nd_lean.py`: `free` and `one` compute `attached` over 252 units, which the interpreter does
not finish in an hour): F-ND4's free document has 252 + 4 = 256, its reading's 253 + 4 = 257; F-ND10's free
document 251 + 4 = 255, each reading's 252 + 4 = 256, the one compatible choice's 253 + 4 = 257 (SR1). -/

def regs4 : List Regulated :=
  [oblig "p_required" ["agent", "user"] false (some "p_permitted") "{0} p {1}",
   perm "p_permitted" ["agent", "user"] false "{0} p {1}",
   oblig "q_required" ["agent", "user"] false (some "q_permitted") "{0} q {1}",
   perm "q_permitted" ["agent", "user"] false "{0} q {1}"]
def unspec4 : List String := ["p_required", "p_permitted", "q_required", "q_permitted"]
/-- `n` fixed strict rules on `p_required`, each its own unit. -/
def rulesOnP (n : Nat) : List Item :=
  (List.range n).map (fun k => .fixed s!"f{k}" (.norm (strictNode s!"rule-{k}" "p_required" true)) [])
def oneRuleSet (s u : String) : ReadingSet := ⟨s, u, 1, [cand "more" (strictNode s!"more-{s}" "p_required" true)]⟩
/-- F-ND4: 252 fixed rules and one set with one more rule. -/
def ND4 : NDoc := ⟨⟨.norms, frameOf regs4 [], rulesOnP 252 ++ [.set (oneRuleSet "rs_1" "u1")], [], []⟩, unspec4⟩
/-- F-ND10: 251 fixed rules and two sets of one reading each, each one more rule. -/
def ND10 : NDoc :=
  ⟨⟨.norms, frameOf regs4 [], rulesOnP 251 ++ [.set (oneRuleSet "rs_1" "u1"), .set (oneRuleSet "rs_2" "u2")], [], []⟩,
   unspec4⟩
/-- `checkAuthorN`'s text on a document (no declared `unsaid__` name, no generated predicate), or `none`. -/
def authorText (U : VE.NormDefaults.UDoc) : Option String :=
  match VE.NormDefaults.Wire.checkAuthorN (Lean.Json.mkObj []) 0 U with
  | .error e => some e
  | .ok () => none

-- F-ND10: the one compatible choice's document is beyond the limit (4.1 step 5), with 253 + 4 rules
#guard choices ND10.D == [[("rs_1", 0), ("rs_2", 0)]]
#guard (choiceU ND10 [("rs_1", 0), ("rs_2", 0)]).D.T.nodes.length == 253
#guard authorText (choiceU ND10 [("rs_1", 0), ("rs_2", 0)]) == some "ResourceLimit: rules"
-- the choice's text names it in `choiceText`'s form
#guard VE.Readings.choiceText ND10.D [("rs_1", 0), ("rs_2", 0)] == "rs_1@1:0, rs_2@1:0"
-- F-ND5: 4.1 step 2 names the reserved rule (no suffix); F-ND1 has none
#guard (Wire.reservedUnsaid ND5, Wire.reservedUnsaid ND1) == (some "unsaid--help-required", none)
-- F-ND1: admission's facts on the instance (`ndRest`, the part of `WellFormedND` after S1's)
#guard Wire.ndRest ND1 && !Wire.ndRest ND5

end VE.Readings.UnspecifiedExamples
