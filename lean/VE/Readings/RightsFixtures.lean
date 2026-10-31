import VE.Readings.Choice
import VE.Rights.Examples

/-! S2b's rights fixtures (docs/spec/composition-PLAN.md section 5) as build-time `#guard`s on `sup D`, `Choice_D`,
the owners and the name map. This module imports only `Choice.lean`, so a fault in a definition there fails a check
here whatever proof it also breaks; the theorems on the same documents are `RightsExamples.lean`. F21: set `rs48`
{0: claim `no-expel` on `expel_permitted`, 1: liberty `may-move` on `move_permitted`}, both declaring right `r13`,
beside a fixed bar (reading `rule`). F7: a fixed limitation over candidate lines. F10: limitation candidates. -/
namespace VE.Readings.RightsExamples
open VE.Readings
open VE.Norms (Sat tupleVal)
open VE.Norms.Checks (perm)
open VE.Rights.Examples (strictNode defaultNode line mkRights barRule l29)
open VE.SoftNorms (SoftNode LiveD DecidesSoftD ValueSoft rulesOn)
open VE.Rights (correlate)

def frame21 : VE.Rights.RightsDoc :=
  { mkRights ["person"] [] [perm "move_permitted" ["person"] true "{0} move",
      perm "expel_permitted" ["person", "person"] true "{0} expel {1}"] [] ⟨["person"], ["person"], [], []⟩ [] [] []
    with sourceOrder := some [] }
def claim21 : VE.Rights.SourceLine := line .claim (strictNode "no-expel" "expel_permitted" false)
def liberty21 : VE.Rights.SourceLine := line .liberty (strictNode "may-move" "move_permitted" true)
def rs48 : ReadingSet := ⟨"rs48", "u048", 1, [⟨"claim", some (.right ⟨"r13", "person", .top, [claim21]⟩), [], []⟩,
  ⟨"liberty", some (.right ⟨"r13", "person", .top, [liberty21]⟩), [], []⟩]⟩
def F21 : Doc := ⟨.rights, frame21, [.set rs48, .bar "u114" barRule], [], []⟩
def c0 : Choice := [("rs48", 0)]
def c1 : Choice := [("rs48", 1)]
def rM : VE.Norms.Regulated := perm "move_permitted" ["person"] true "{0} move"
def chi1 : VE.Formula := .unary "ve__bit__1__0" (.const "ve__here")
def quiet21 : VE.Formula := .all "person" (.implies (.unary "rights__bar__1" (.var 0)) chi1)

#guard WellFormedDoc F21 && superposable F21
#guard (choiceLabelled F21).map (·.1) == ["readings:rs48@1:1:quiet"]
-- the liberty choice's document has the bar node and aimed under the same name; the claim choice's has neither
#guard nameMap F21 c1 "rights__bar__1" == "rights__bar__1" && (genKeys (choiceDoc F21 c0).1).isEmpty

-- a claim on m is no liberty: only the liberty candidate owns aimed_m
def rs48m : ReadingSet := ⟨"rs48", "u048", 1, [⟨"claim", some (.right ⟨"r13", "person", .top,
  [line .claim (strictNode "no-move" "move_permitted" false)]⟩), [], []⟩,
  ⟨"liberty", some (.right ⟨"r13", "person", .top, [liberty21]⟩), [], []⟩]⟩
#guard aimedOwners ⟨.rights, frame21, [.set rs48m, .bar "u114" barRule], [], []⟩ "move_permitted" == [[(0, 1)]]

/-! ## F7: a fixed limitation with scope all over candidate lines -/

def F7 : Doc := ⟨.rights, frame21, [.set rs48, .fixed "u111" (.limitation l29) []], [], []⟩
#guard WellFormedDoc F7 && superposable F7
-- one lim per act of a candidate line, owned by that candidate, with its cond keys
#guard ((genKeys (sup F7).1).filter (fun g => match g.1 with | .lim .. => true | _ => false)).map (fun g => owners F7 g.1)
  == [[[(0, 0)]], [[(0, 1)]]]
#guard (choiceLabelled F7).map (·.1) == ["readings:rs48@1:0:quiet", "readings:rs48@1:1:quiet"]
#guard nameMap F7 c1 "rights__lim__1" == "rights__lim__2"
-- a fixed limitation's scope naming the set-declared right r13 names both copies
def F7r : Doc := ⟨.rights, frame21, [.set rs48, .fixed "u111" (.limitation { l29 with scope := some ["r13"] }) []], [], []⟩
#guard (sup F7r).1.limits.map (·.scope) == [some ["rd-1-r13", "rd-2-r13"]]
-- a fixed right's line rule over an interface rule is over every copy of it
def rsNorm : ReadingSet := ⟨"rsn", "u2", 1, [⟨"a", some (.norm (strictNode "base" "expel_permitted" true)), [], []⟩,
  ⟨"b", some (.norm (strictNode "base" "expel_permitted" false)), [], []⟩]⟩
def F7o : Doc := ⟨.rights, frame21, [.set rsNorm, .fixed "u3" (.right ⟨"r3", "person", .top,
  [line .claim (strictNode "over-base" "expel_permitted" false .top [] ["base"])]⟩) []], [], []⟩
#guard ((sup F7o).1.rs.flatMap (·.lines)).filterMap (·.norm.map (·.over)) == [["rd-1-base", "rd-2-base"]]

/-! ## F10: limitation candidates {on the liberties, on every line} over fixed lines -/

def onLiberties : VE.Rights.Limitation := { l29 with name := "l29c", kinds := some [.liberty] }
def onEvery : VE.Rights.Limitation := { l29 with name := "l29c" }
def rs112 : ReadingSet := ⟨"rs112", "u112", 1, [⟨"liberties", some (.limitation onLiberties), [], []⟩,
  ⟨"every", some (.limitation onEvery), [], []⟩]⟩
def F10 : Doc := ⟨.rights, frame21, [.fixed "u048" (.right ⟨"r13", "person", .top, [claim21, liberty21]⟩) [],
  .set rs112], [], []⟩
#guard WellFormedDoc F10 && superposable F10
#guard (sup F10).1.limits.map (·.name) == ["rd-1-l29c", "rd-2-l29c"]
-- the liberties candidate owns its one lim key, the every-line candidate its two; each choice maps to its copy
#guard ((genKeys (sup F10).1).filterMap (fun g => match g.1 with | .lim L a => some (L, a, owners F10 g.1) | _ => none))
  == [("rd-1-l29c", "move_permitted", [[(0, 0)]]), ("rd-2-l29c", "expel_permitted", [[(0, 1)]]),
      ("rd-2-l29c", "move_permitted", [[(0, 1)]])]
#guard qualifyKey F10 [("rs112", 1)] (.lim "l29c" "move_permitted") == .lim "rd-2-l29c" "move_permitted"
#guard nameMap F10 [("rs112", 0)] "rights__lim__1" == "rights__lim__1" &&
  nameMap F10 [("rs112", 1)] "rights__lim__2" == "rights__lim__3"

/-! ## The rules a candidate's contents bring, gated (plan 2.3), and the copies of fixed ones -/

def excNode : SoftNode := { defaultNode "exc" "move_permitted" true with exception := some ⟨some "unstated", [.top], [], []⟩ }
-- every sufficient exception condition of a candidate rule is conjoined with its atom
#guard (gateNorm F21 0 1 excNode).exception.map (·.sufficient) == some [.and .top chi1]
#guard gateContent F21 0 1 (.rightLines "r13" [liberty21]) ==
  .rightLines "r13" [{ liberty21 with norm := some { strictNode "rd-2-may-move" "move_permitted" true with
    guard := .and .top chi1 } }]
#guard copyContent F7o (.rightLines "r3" [line .claim (strictNode "x" "expel_permitted" false .top [] ["base"])]) ==
  .rightLines "r3" [line .claim (strictNode "x" "expel_permitted" false .top [] ["rd-1-base", "rd-2-base"])]
-- a fixed right's name is its one copy
#guard rightCopies F7o "r3" == ["r3"] && rightCopies F7r "r13" == ["rd-1-r13", "rd-2-r13"]
-- a choice of a candidate without content keeps the limitation name
def rs112n : ReadingSet := { rs112 with candidates := rs112.candidates ++ [⟨"none", none, [], []⟩] }
def F10n : Doc := ⟨.rights, frame21, [.fixed "u048" (.right ⟨"r13", "person", .top, [claim21, liberty21]⟩) [],
  .set rs112n], [], []⟩
#guard qualifyKey F10n [("rs112", 2)] (.lim "l29c" "move_permitted") == .lim "l29c" "move_permitted" &&
  qualifyKey F10n [("rs112", 0)] (.lim "l29c" "move_permitted") == .lim "rd-1-l29c" "move_permitted"

end VE.Readings.RightsExamples
