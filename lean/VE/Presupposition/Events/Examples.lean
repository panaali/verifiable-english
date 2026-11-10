import VE.Presupposition.Events
import VE.Events.Examples

/-! # PS-7 fixtures (presupposition PLAN PS-7, P9, P10 and UDHR u055's and u067's "change")

`#guard` lines on finite events situations, both directions for each row: a state with no stated end
(persistence is never assumed: the same begin day with a stated end changes "is in progress on" and `strong`;
the `pre` "in progress before" cannot fail by an end, since a state is in progress on its own begin day), a state that
begins on the day itself, an earlier state or event of another sort, and days and instances bound by
an outer quantifier (the lifts). P9 and P10 are at formula level (ps-2ab's `admit` is not on main).
Days run a < b < c < d; the day term `t` is c. -/
namespace VE.Presupposition.Events.Examples
open VE.Presupposition VE.Presupposition.Events VE.Events
open VE.Events.Examples (chain)

def stay : StateSort := ⟨"stay", "begins", "ends"⟩
def job : StateSort := ⟨"job", "job_begins", "job_ends"⟩
def audit : EventSort := ⟨"audit", "audit_on"⟩
def visit : EventSort := ⟨"visit", "visit_on"⟩
def V : EventsEnv :=
  { day := "day", before := "before", events := [audit, visit], states := [stay, job], dates := [], anchor := none,
    links := [] }

/-- Days a, b, c, d; the constant `s` names the stay `s`, `t` the day c and `a` the day a. -/
def sit (doms : List (String × List String)) (rels : List (String × List (List String))) : VE.FiniteModel String :=
  chain ["a", "b", "c", "d"] [("s", "s"), ("t", "c"), ("a", "a"), ("b", "b")] doms rels
def stayS (rels : List (String × List (List String))) : VE.FiniteModel String := sit [("stay", ["s"])] rels

def x : VE.Term := .const "s"
def t : VE.Term := .const "t"
def ip : VE.Formula := inProgress V stay x t
def ipBefore : VE.Formula := inProgressBefore V stay x t

-- the situations of the state rows: no stated end, ended on a, ended on c, begins on t itself, never begins
def noEnd : VE.FiniteModel String := stayS [("begins", [["s", "a"]])]
def endA : VE.FiniteModel String := stayS [("begins", [["s", "a"]]), ("ends", [["s", "a"]])]
def endC : VE.FiniteModel String := stayS [("begins", [["s", "a"]]), ("ends", [["s", "c"]])]
def onT : VE.FiniteModel String := stayS [("begins", [["s", "c"]])]
def none0 : VE.FiniteModel String := stayS []
def states : List (VE.FiniteModel String) := [noEnd, endA, endC, onT, none0]

-- events' "is in progress on": persistence is never assumed (noEnd against endA), the last day counts (endC)
#guard states.map (ip.eval · []) == [true, false, true, true, false]
#guard (inProgress V stay x (.const "b")).eval endA [] == false && (inProgress V stay x (.const "a")).eval endA []
-- the `pre` reads only the begin day: a stated end before t leaves it true (endA as noEnd)
#guard ipBefore.eval noEnd [] == ipBefore.eval endA []

-- "stops" / "ceases": in progress before the day; a state beginning on t is not
#guard states.map ((stops V stay x t (.not ip)).pre.eval · []) == [true, true, true, false, false]
#guard states.map ((stops V stay x t (.not ip)).strong.eval · []) == [false, true, false, false, false]
#guard states.map ((stops V stay x t (.not ip)).weak.eval · []) == [false, true, false, true, true]

-- "continues" / "remains": `strong` is the plan's "before and on" exactly
#guard states.map ((continues V stay x t ip).strong.eval · []) == [true, false, true, false, false]
#guard states.all fun M => (continues V stay x t ip).strong.eval M [] == (ipBefore.eval M [] && ip.eval M [])

-- "no longer": in progress before, not on
#guard states.map ((noLonger V stay x t (.not ip)).strong.eval · []) == [false, true, false, false, false]
#guard states.all fun M => (noLonger V stay x t (.not ip)).pre.eval M [] == ipBefore.eval M []

-- "resumes": another stay ended before t; a stay ending on t or later, or a job, does not count
def other (rels : List (String × List (List String))) : VE.FiniteModel String :=
  sit [("stay", ["s", "y"]), ("job", ["j"])] rels
#guard (resumes V stay t ip).pre.eval (other [("ends", [["y", "a"]])]) []
#guard (resumes V stay t ip).pre.eval (other [("ends", [["y", "b"]])]) []
#guard !(resumes V stay t ip).pre.eval (other [("ends", [["y", "c"]])]) []
#guard !(resumes V stay t ip).pre.eval (other [("ends", [["y", "d"]])]) []
#guard !(resumes V stay t ip).pre.eval (other [("job_ends", [["j", "a"]])]) []
#guard !(resumes V stay t ip).pre.eval (other [("begins", [["y", "a"]])]) []

-- "again": an earlier visit; a visit on t or later, or an earlier audit, does not count
def evs (rels : List (String × List (List String))) : VE.FiniteModel String :=
  sit [("visit", ["v"]), ("audit", ["w"])] rels
def againPre : VE.Formula := (again V visit t .top).pre
#guard againPre.eval (evs [("visit_on", [["v", "a"]])]) []
#guard !againPre.eval (evs [("visit_on", [["v", "c"]])]) []
#guard !againPre.eval (evs [("visit_on", [["v", "d"]])]) []
#guard !againPre.eval (evs [("audit_on", [["w", "a"]])]) []

-- "returns to" p (reviews/dri-decisions-20261110-ps-7.md): (a) an earlier stay at p ended before t; (b) at q only;
-- (c) it ends on t or later; (d) no stated end (F: not assumed); (e) a variable place and day (the lifts)
def places (rels : List (String × List (List String))) : VE.FiniteModel String :=
  chain ["a", "b", "c", "d"] [("t", "c"), ("b", "b"), ("p", "p")] [("stay", ["s", "y"]), ("place", ["p", "q"])] rels
def retPre : VE.Formula := (returnsTo V stay "at" (.const "p") t .top).pre
#guard retPre.eval (places [("ends", [["y", "a"]]), ("at", [["y", "p"]])]) []
#guard !retPre.eval (places [("ends", [["y", "a"]]), ("at", [["y", "q"]])]) []
#guard !retPre.eval (places [("ends", [["y", "c"]]), ("at", [["y", "p"]])]) []
#guard !retPre.eval (places [("ends", [["y", "d"]]), ("at", [["y", "p"]])]) []
#guard !retPre.eval (places [("begins", [["y", "a"]]), ("at", [["y", "p"]])]) []
def somePlace (M : VE.FiniteModel String) : Bool :=
  (VE.Formula.ex "place" (.all "day" (.implies (.binary "before" (.const "b") (.var 0))
    (endedAtBefore V stay "at" (.var 1) (.var 0))))).eval M []
#guard somePlace (places [("ends", [["y", "a"]]), ("at", [["y", "p"]])])
#guard !somePlace (places [("ends", [["y", "c"]]), ("at", [["y", "p"]])])

-- "returns to" p, the amended ruling (reviews/dri-decisions-20261110-ps-7-returns.md, guards (f)-(l) of
-- reviews/ps-7-dri-note-20261110-next.md). The body is an arrival at p on t, `arrives(p, t)` (the subject's own
-- arrival, the subject left implicit: VE has no ternary atom); y and z are the subject's own stays. Each structure
-- is built without (F) and with (T) the arrival, and each guard that involves the body checks both values.
def ret (rels : List (String × List (List String))) (arrives : Bool) : VE.FiniteModel String :=
  chain ["a", "b", "c", "d"] [("t", "c"), ("p", "p")] [("stay", ["y", "z"]), ("place", ["p", "q"])]
    (rels ++ if arrives then [("arrives", [["p", "c"]])] else [])
def arrival : VE.Formula := .binary "arrives" (.const "p") t
def retR (body : VE.Formula) : Reading := returnsTo V stay "at" (.const "p") t body
/-- (pre, strong, weak) of "returns to p on t" with the arrival body. -/
def retV (M : VE.FiniteModel String) : Bool × Bool × Bool :=
  ((retR arrival).pre.eval M [], (retR arrival).strong.eval M [], (retR arrival).weak.eval M [])
def neverLeft : List (String × List (List String)) := [("begins", [["y", "a"]]), ("at", [["y", "p"]])]
def leftA : List (String × List (List String)) := [("begins", [["y", "a"]]), ("ends", [["y", "a"]]), ("at", [["y", "p"]])]
def leftOnT : List (String × List (List String)) := [("begins", [["y", "a"]]), ("ends", [["y", "c"]]), ("at", [["y", "p"]])]
def endOnly : List (String × List (List String)) := [("ends", [["y", "a"]]), ("at", [["y", "p"]])]
def leftAndStaying : List (String × List (List String)) :=
  [("begins", [["y", "a"], ["z", "b"]]), ("ends", [["y", "a"]]), ("at", [["y", "p"], ["z", "p"]])]
def retCases : List (List (String × List (List String))) := [neverLeft, leftA, leftOnT, endOnly, leftAndStaying]
-- (f) never left (an ongoing stay at p begun on a, no end day): pre F, strong F, weak T (silent: the intended weak
-- reading), with the arrival too
#guard retV (ret neverLeft false) == (false, false, true) && retV (ret neverLeft true) == (false, false, true)
-- (g) left: the stay at p ended on a, before t: pre T, strong and weak follow the arrival
#guard retV (ret leftA true) == (true, true, true) && retV (ret leftA false) == (true, false, false)
-- (h) the stay ends on t itself: pre F, strong F, weak T (the day-level limit)
#guard retV (ret leftOnT false) == (false, false, true) && retV (ret leftOnT true) == (false, false, true)
-- (i) an end on a with no begin day: pre T (ENDS reads the end only; ENDS and BEGINS are not ordered)
#guard retV (ret endOnly true) == (true, true, true) && retV (ret endOnly false) == (true, false, false)
-- (j) a conditioned carrier `G → (pre → body)` over the never-left structure, G "the subject is at p" (true there):
-- true for both arrival values (silent), as the reviewed conditioned carrier at `impR G hole`
def stayingAtP : VE.Formula := .ex "stay" (.binary "at" (.var 0) (.const "p"))
#guard [false, true].all fun b => stayingAtP.eval (ret neverLeft b) [] &&
  ((Frame.impR stayingAtP .hole).plug (retR arrival).weak).eval (ret neverLeft b) [] &&
  (conditionedAt (.impR stayingAtP .hole) (retR arrival)).eval (ret neverLeft b) []
-- (k) left on a, then a current stay z at p from b with no end, no arrival on t: pre T, the arrival body gives strong F
-- and weak F; an occupancy body ("at p on t", true here) would give strong T: the body must be an arrival
#guard retV (ret leftAndStaying false) == (true, false, false)
def occupancy : VE.Formula := .ex "stay" (.and (.binary "at" (.var 0) (.const "p")) (inProgress V stay (.var 0) t))
#guard occupancy.eval (ret leftAndStaying false) [] && (retR occupancy).strong.eval (ret leftAndStaying false) []
-- (l) "X did not return to p" of an X who never left: asserted `pre ∧ ¬body` F, conditioned `pre → ¬body` T
#guard [false, true].all fun b => !(assertedAt .hole (retR (.not arrival))).eval (ret neverLeft b) [] &&
  !(retR (.not arrival)).strong.eval (ret neverLeft b) [] && (retR (.not arrival)).weak.eval (ret neverLeft b) [] &&
  (conditionedAt .hole (retR (.not arrival))).eval (ret neverLeft b) []
-- latest-stay limit, row ps-7c: today pre is T in structure (k) (an earlier stay ended, though X is at p since b), so
-- weak follows the body; a "latest stay ended" pre flips this guard. "resumes" shares the limit (its pre is T there).
#guard [false, true].all fun b => retV (ret leftAndStaying b) == (true, b, b) &&
  (resumes V stay t ip).pre.eval (ret leftAndStaying b) []

-- a variable day under "on each day after a", and a variable stay under "some stay": the lifts
def eachDay (p : VE.Term → VE.Formula) : VE.Formula :=
  .all "day" (.implies (.binary "before" (.const "a") (.var 0)) (p (.var 0)))
#guard (eachDay (inProgressBefore V stay x)).eval noEnd []
#guard !(eachDay (inProgressBefore V stay x)).eval (stayS [("begins", [["s", "b"]])]) []
#guard (eachDay (inProgress V stay x)).eval noEnd [] && !(eachDay (inProgress V stay x)).eval endA []
#guard states.map ((VE.Formula.ex "stay" (inProgress V stay (.var 0) t)).eval · []) == [true, false, true, true, false]
def someStay (M : VE.FiniteModel String) : Bool :=
  (VE.Formula.ex "stay" (.all "day" (.implies (.binary "before" (.const "a") (.var 0))
    (inProgressBefore V stay (.var 1) (.var 0))))).eval M []
#guard someStay noEnd && !someStay (stayS [("begins", [["s", "b"]])])
#guard (eachDay (fun d => .implies (.binary "before" (.const "b") d) (endedBefore V stay d))).eval
  (other [("ends", [["y", "b"]])]) []
#guard !(eachDay (endedBefore V stay)).eval (other [("ends", [["y", "b"]])]) []
#guard (eachDay (fun d => .implies (.binary "before" (.const "b") d) (occurredBefore V visit d))).eval
  (evs [("visit_on", [["v", "b"]])]) []
#guard !(eachDay (occurredBefore V visit)).eval (evs [("visit_on", [["v", "b"]])]) []
-- the same `pre` at a valuation: the day as variable 0 of the hole's context
#guard states.all fun M => ipBefore.eval M [] == (inProgressBefore V stay x (.var 0)).eval M ["c"]

-- P9 (u0220.s06), "continuing with an ongoing action", the action as a state: "ongoing" (in progress before t)
-- is the phrase's left conjunct and "continuing" (in progress on t) the trigger in its right conjunct. The
-- projected goal `ongoing → pre` holds on every situation (proved within the phrase), so asserted, conditioned and
-- in place all equal the weak plug: one reading.
def p9 : Reading := continues V stay x t ip
def p9F : Frame := .andR ipBefore .hole
#guard states.all fun M => (p9F.goal p9.pre).eval M [] &&
  [assertedAt p9F p9, conditionedAt p9F p9, inPlaceAt p9F p9].all (·.eval M [] == (p9F.plug p9.weak).eval M [])
#guard states.map ((p9F.plug p9.strong).eval · []) == [true, false, true, false, false]
-- the phrase's content entails the pre on every situation; with "ongoing" read as in progress on t (`ip`) instead,
-- the goal fails on onT and asserted and conditioned differ there: one reading rests on "ongoing" = before t
#guard states.all fun M => !(VE.Formula.and ipBefore ip).eval M [] || p9.pre.eval M []
#guard !((Frame.andR ip .hole).goal p9.pre).eval onT [] &&
  (assertedAt (.andR ip .hole) p9).eval onT [] != (conditionedAt (.andR ip .hole) p9).eval onT []

-- P10 (u0168.s01), "remain firm", Claude's firmness as a state: {assumed: the before part as its own unit, then
-- the clause; conditioned: goal → clause}. They differ where the firmness begins on t (not in progress before).
def p10 : Reading := continues V stay x t ip
def p10Assumed : VE.Formula := .and (Frame.hole.close p10.pre) (Frame.hole.plug p10.strong)
#guard !p10Assumed.eval onT [] && (conditionedAt .hole p10).eval onT []
#guard p10Assumed.eval noEnd [] && (conditionedAt .hole p10).eval noEnd []

-- UDHR u055 ("change his nationality") and u067 ("change his religion or belief"): "stops" on the earlier state
-- (the nationality or religion `s` held before t is not in progress on t) and a new state `y` begins on t.
def change : VE.Formula :=
  .and (stops V stay x t (.not ip)).strong (.ex "stay" (.binary "begins" (.var 0) t))
def changed : VE.FiniteModel String := other [("begins", [["s", "a"], ["y", "c"]]), ("ends", [["s", "b"]])]
def stateless : VE.FiniteModel String := other [("begins", [["y", "c"]])]
#guard change.eval changed [] && !change.eval stateless []
#guard !(stops V stay x t (.not ip)).pre.eval stateless [] && (stops V stay x t (.not ip)).weak.eval stateless []

-- a situation of each family above satisfies events' premises (one begin, one end, no end before the begin,
-- the order), and an end before the begin is refused
#guard (states ++ [stayS [("begins", [["s", "b"]])], other [("ends", [["y", "a"]])], other [("job_ends", [["j", "a"]])],
  evs [("visit_on", [["v", "a"]])], evs [("audit_on", [["w", "a"]])], changed, stateless,
  places [("ends", [["y", "a"]]), ("at", [["y", "p"]])]] ++
  retCases.flatMap fun r => [ret r false, ret r true]).all (VE.Events.Examples.firstFailing V · == none)
#guard VE.Events.Examples.firstFailing V (stayS [("begins", [["s", "b"]]), ("ends", [["s", "a"]])]) != none

-- ps-1-locate-path: `locate` follows the path (a `locate` that ignores it gives one answer for both)
#guard Frame.locate (.or .top .bottom) [0] == some (.orL .hole .bottom, .top)
#guard (Frame.locate (.and .top .bottom) [0]).map (·.2) == some .top &&
  (Frame.locate (.and .top .bottom) [1]).map (·.2) == some .bottom

end VE.Presupposition.Events.Examples
