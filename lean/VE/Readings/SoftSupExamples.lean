import VE.Readings.SoftSup
import VE.Readings.SoftSeparateExamples

/-! SC-10's fixtures (docs/spec/rd-9-soft-chain.md 13.5), each value computed here by `#guard` against the value the
spec records: S-1..S-7 on the merged fixtures of `SoftSeparateExamples.lean`, the query vocabulary of OPEN-SC10-1
(DRI decision 2026-10-31 item 1), `NSD4a`'s and `NSD4c`'s facts, and both directions of the iff fixtures of
`supX_pull`, `fillPremisesSD_pull`, `fill_sim` and `fill_sim_author`. The iff fixtures read each side on a finite
model: the superposed side on the model, the choice's side on its filled pull (`pullFM`, `pullF` on a finite model),
decisions through the substituted `decides` formula, which is the decision on the canonical interpretation
(`canon_subst`). -/
namespace VE.Readings.SoftSupExamples
open VE.Readings
open VE.Readings.SoftSeparateExamples (predsOf NSD1 NSD2 NSD4 NSDq NC9 frame4 mustX needNotX)
open VE.Readings.Examples (docK cand)
open VE.Rights.Examples (strictNode)
open VE.Rights (correlate)
open VE.Norms (envAt size)
open VE.NormDefaults (fill fillPremises)

def facts (N : NDoc) : Bool × Bool × Bool × Nat × List Nat × List String :=
  (WellFormedSD N, superposable N.D, VE.NormDefaults.WellFormedU (supU N), (choices N.D).length,
   (choices N.D).map (fun c => (choiceX N c).length), (softXL N (sup N.D).1).map (·.1))

/-! ## S-1..S-7 -/

#guard facts NSD1 == (true, true, true, 2, [0, 0], [])
#guard facts NSD4 == (true, true, true, 2, [0, 2],
  ["soft:exception:rd-2-must-x:sufficient:0", "soft:coherence:need-not-x,rd-2-must-x"])
-- S-2′
#guard facts NC9 == (true, true, true, 2, [0, 3], ["soft:exception:rd-2-comply:sufficient:0",
  "soft:exception:rd-2-comply:sufficient:1", "soft:exception:rd-2-comply:sufficient:2"])
#guard facts NSD2 == (true, true, true, 2, [0, 1], ["soft:exception:rd-2-no-deception:necessary:0"])
#guard facts NSDq == (true, true, true, 2, [0, 0], [])
-- S-3 (D3): the superposed coherence premise on the filled tree reads the gap; S2a's does not
#guard (softXL NSD4 (sup NSD4.D).1).map (fun x => (predsOf x.2).contains "unsaid__y_permitted") == [false, true]
#guard (VE.SoftNorms.cohPremises (correlate (sup NSD4.D).1)).map
  (fun a => (predsOf a).contains "unsaid__y_permitted") == [false]
-- S-4 (gating): each premise of `supX NSD4` reads the candidate's bit
#guard (supX NSD4).map predsOf == [["c", "ve__bit__1__0", "soft__excepted__rd_2_must_x"],
  ["soft__excepted__need_not_x", "unsaid__y_permitted", "ve__bit__1__0", "unsaid__y_permitted", "ve__bit__1__0",
    "soft__excepted__rd_2_must_x", "unsaid__y_permitted", "ve__bit__1__0"]]
-- S-4′ (necessary): the necessary-condition premise reads no bit
#guard (supX NSD2).map predsOf == [["soft__excepted__rd_2_no_deception"]]
#guard (supX NSD2).map (fun a => (predsOf a).any (·.startsWith "ve__bit__")) == [false]
-- S-5 (`pullF`): only the filled choice vocabulary declares the gap, and `nameMap` keeps its name
#guard (choices NSD1.D).map (fun c => (((choiceEnvFull NSD1.D c).predicates "unsaid__avoid_required").isSome,
  ((envAt (fill (choiceU NSD1 c)) (size (fill (choiceU NSD1 c)))).predicates "unsaid__avoid_required").isSome,
  nameMap NSD1.D c "unsaid__avoid_required")) ==
  [(false, true, "unsaid__avoid_required"), (false, true, "unsaid__avoid_required")]
#guard ((envAt (fill (supU NSD1)) 0).predicates "unsaid__avoid_required").isSome
-- S-6 (`Fill_T`)
#guard ((fillPremises (supU NSDq)).length, (choices NSDq.D).map (fun c => (fillPremises (choiceU NSDq c)).length)) ==
  (1, [1, 1])
#guard ((fillPremises (supU NSD1)).length, (choices NSD1.D).map (fun c => (fillPremises (choiceU NSD1 c)).length)) ==
  (0, [0, 0])
-- S-7 (pairs)
#guard (VE.SoftNorms.collidingPairs (correlate (sup NSD4.D).1)).map (fun x => (x.1.name, x.2.name)) ==
  [("need-not-x", "rd-2-must-x")]
#guard (choices NSD4.D).map (fun c => (VE.SoftNorms.collidingPairs (correlate (choiceDoc NSD4.D c).1)).map
  (fun x => (x.1.name, x.2.name))) == [[], [("must-x", "need-not-x")]]
#guard (choices NSD4.D).map (fun c => (softXL NSD4 (choiceDoc NSD4.D c).1).map (·.1)) ==
  [[], ["soft:exception:must-x:sufficient:0", "soft:coherence:must-x,need-not-x"]]
#guard (choices NC9.D).map (fun c => (softXL NC9 (choiceDoc NC9.D c).1).map (·.1)) ==
  [[], ["soft:exception:comply:sufficient:0", "soft:exception:comply:sufficient:1", "soft:exception:comply:sufficient:2"]]

/-! ## OPEN-SC10-1: a query may name a filled gap (DRI decision 2026-10-31 item 1) -/

def q3 : VE.Formula := .all "agent" (.all "user"
  (.implies (.binary "unsaid__avoid_required" (.var 1) (.var 0)) (.binary "avoid_required" (.var 1) (.var 0))))
#guard q3.check (sharedEnvSD NSD1) [] && !q3.check (sharedEnv NSD1.D) []
-- the superposed certificate check reads the filled vocabulary: a query naming the gap closes from itself, and does
-- not close without it
def closeCert : VE.Tableau.Certificate := ⟨"ve-tableau-checker@2", "", [], "", .close⟩
#guard supCertificateCheckSD NSD1 [] [q3] q3 closeCert && !supCertificateCheckSD NSD1 [] [] q3 closeCert
-- each list of the premises is read whole: every atom of `A`, premise of `supX`, superposed assertion and member of `Γ`
-- closes a goal equal to it
def q4 : VE.Formula := .all "agent" (.all "user" (.not (.binary "avoid_required" (.var 1) (.var 0))))
def NSDa : NDoc := ⟨docK [.fixed "u0" (.assertion VE.Readings.Examples.asksAll) [], .fixed "u1" (.assertion q4) [],
  .set VE.Readings.Examples.rs1], ["avoid_required"]⟩
#guard [0, 1].all (fun i => supCertificateCheckSD NSD1 [("rs1", 0), ("rs1", 1)] [] (choiceAtom NSD1.D "rs1" i) closeCert)
#guard (supX NSD4).all (fun a => supCertificateCheckSD NSD4 [] [] a closeCert)
#guard (sup NSDa.D).2.length == 2 && (sup NSDa.D).2.all (fun a => supCertificateCheckSD NSDa [] [] a closeCert)
#guard [q3, q4].all (fun a => supCertificateCheckSD NSD1 [] [q3, q4] a closeCert)

/-! ## `NSD4a` (`x_permitted` allowed by default) and `NSD4c` (`need-not-x` strict): facts -/

open VE.Norms.Checks (envOf perm oblig) in
def frame4a : VE.Rights.RightsDoc :=
  let regs := [oblig "x_required" ["assistant"] false (some "x_permitted") "{0} do x",
    perm "x_permitted" ["assistant"] true "{0} do x", perm "y_permitted" ["assistant"] false "{0} do y"]
  { frame4 with soft := ⟨envOf ["assistant"] ([("c", ["assistant"])] ++ regs.map (fun r => (r.name, r.sorts))), [],
      VE.Rights.Examples.noSoft, ⟨regs, [], []⟩⟩ }
def rs4 : ReadingSet := ⟨"rs1", "u1", 1, [cand "strict" (strictNode "must-x" "x_required" true
  (.unary "y_permitted" (.var 0))), cand "default" mustX]⟩
def NSD4a : NDoc := ⟨docK [.fixed "u0" (.norm needNotX) [], .set rs4] .soft frame4a, ["y_permitted"]⟩
def NSD4c : NDoc := ⟨docK [.fixed "u0" (.norm (strictNode "need-not-x" "x_required" false)) [], .set rs4] .soft frame4a,
  ["y_permitted"]⟩

#guard facts NSD4a == (true, true, true, 2, [0, 2],
  ["soft:exception:rd-2-must-x:sufficient:0", "soft:coherence:need-not-x,rd-2-must-x"])
#guard facts NSD4c == (true, true, true, 2, [0, 1], ["soft:exception:rd-2-must-x:sufficient:0"])

/-! ## The iff fixtures, each direction -/

/-- `pullF` on a finite model. -/
def pullFM (N : NDoc) (c : Choice) (M : VE.FiniteModel String) : VE.FiniteModel String :=
  { M with relations := fun p => if ((envAt (fill (choiceU N c)) (size (fill (choiceU N c)))).predicates p).isSome
      then M.relations (nameMap N.D c p) else [] }
/-- S2a's `pull` on a finite model. -/
def pullM (N : NDoc) (c : Choice) (M : VE.FiniteModel String) : VE.FiniteModel String :=
  { M with relations := fun p => if ((choiceEnvFull N.D c).predicates p).isSome
      then M.relations (nameMap N.D c p) else [] }
def satAll (M : VE.FiniteModel String) (l : List VE.Formula) : Bool := l.all (·.eval M [])
/-- The decision of the rules of `T` on `q` at `ws`, read on the canonical interpretation of `fill U`. -/
def decF (U : VE.NormDefaults.UDoc) (T : VE.Norms.Tree) (M : VE.FiniteModel String) (q : String) (sign : Bool)
    (ws : List String) : Bool :=
  (VE.Norms.subst (fill U).T (size (fill U)) (VE.Norms.decides T q sign)).eval M ws.reverse

/-- One assistant `a`; the bit on names `(rs1,1)`. -/
def m4 (bit : Bool) (cs exc : List (List String)) : VE.FiniteModel String where
  domains s := match s with | "assistant" => ["a"] | "ve__reading" => ["e"] | _ => []
  constants x := if x == "ve__here" then some "e" else none
  relations p := if p == "ve__bit__1__0" then (if bit then [["e"]] else []) else if p == "c" then cs
    else if p == "soft__excepted__rd_2_must_x" then exc else []
/-- One agent `a`, one user `u`; the bit on names `(rs1,1)`. -/
def m1 (bit : Bool) (exc fillY : List (List String)) : VE.FiniteModel String where
  domains s := match s with | "agent" => ["a"] | "user" => ["u"] | "ve__reading" => ["e"] | _ => []
  constants x := if x == "ve__here" then some "e" else none
  relations p := if p == "ve__bit__1__0" then (if bit then [["e"]] else [])
    else if p == "soft__excepted__rd_2_no_deception" then exc else if p == "unsaid__avoid_required" then fillY else []
/-- `NSDq`'s base (`base1`) with the bit; on names `(rs_1,1)`. -/
def mq (bit : Bool) (permitted : List (List String)) : VE.FiniteModel String where
  domains s := match s with | "agent" => ["a"] | "user" => ["u"] | "ve__reading" => ["e"] | _ => []
  constants x := if x == "ve__here" then some "e" else none
  relations p := if p == "ve__bit__1__0" then (if bit then [["e"]] else [])
    else if p == "unsaid__help_permitted" then permitted else []

-- the bit names the choice (`Encodes`)
#guard (choices NSD4.D).map (fun c => (atoms NSD4.D c).map (·.eval (m4 true [] []) [])) == [[false], [true]]
#guard (choices NSD1.D).map (fun c => (atoms NSD1.D c).map (·.eval (m1 true [] []) [])) == [[false], [true]]
#guard (choices NSDq.D).map (fun c => (atoms NSDq.D c).map (·.eval (mq true []) [])) == [[false], [true]]

-- `supX_pull`, NSD4: at `(rs1,1)` two premises on each side, both false without the exception and both true with
-- it; at `(rs1,0)` two premises gated off by the bit against none
#guard (supX NSD4).length == 2 && (choiceX NSD4 [("rs1", 1)]).length == 2 && (choiceX NSD4 [("rs1", 0)]).length == 0
#guard !satAll (m4 true [["a"]] []) (supX NSD4) &&
  !satAll (pullFM NSD4 [("rs1", 1)] (m4 true [["a"]] [])) (choiceX NSD4 [("rs1", 1)])
#guard satAll (m4 true [["a"]] [["a"]]) (supX NSD4) &&
  satAll (pullFM NSD4 [("rs1", 1)] (m4 true [["a"]] [["a"]])) (choiceX NSD4 [("rs1", 1)])
#guard satAll (m4 false [["a"]] []) (supX NSD4) &&
  satAll (pullFM NSD4 [("rs1", 0)] (m4 false [["a"]] [])) (choiceX NSD4 [("rs1", 0)])
-- `supX_pull` needs `hsl`: on NSD2 at `(rs1,0)` with the necessary condition's table filled, the slot is broken and
-- `supX` is false while `choiceX = []` holds; with the table empty the slot holds and both sides are true
#guard !satAll (m1 false [["a", "u"]] []) (slotP NSD2.D) && !satAll (m1 false [["a", "u"]] []) (supX NSD2) &&
  satAll (pullFM NSD2 [("rs1", 0)] (m1 false [["a", "u"]] [])) (choiceX NSD2 [("rs1", 0)])
#guard satAll (m1 false [] []) (slotP NSD2.D) && satAll (m1 false [] []) (supX NSD2) &&
  satAll (pullFM NSD2 [("rs1", 0)] (m1 false [] [])) (choiceX NSD2 [("rs1", 0)])

-- `fillPremisesSD_pull`, NSDq at `(rs_1,0)`: one premise on each side, both false at `base1 []` and both true at
-- `base1 [(a,u)]`; NSD1 has none on either side (S-6)
#guard !satAll (mq false []) (fillPremises (supU NSDq)) &&
  !satAll (pullFM NSDq [("rs_1", 0)] (mq false [])) (fillPremises (choiceU NSDq [("rs_1", 0)]))
#guard satAll (mq false [["a", "u"]]) (fillPremises (supU NSDq)) &&
  satAll (pullFM NSDq [("rs_1", 0)] (mq false [["a", "u"]])) (fillPremises (choiceU NSDq [("rs_1", 0)]))
-- with S2a's `pull` in place of `pullF` the choice's `Fill_T` fails there: the gap's table is dropped (S-5)
#guard !satAll (pullM NSDq [("rs_1", 0)] (mq false [["a", "u"]])) (fillPremises (choiceU NSDq [("rs_1", 0)]))

/-- Both sides of `fill_sim` (`author = false`) or `fill_sim_author` (`true`) on NSD1 at `avoid_required (a,u)`; `pl`
    chooses `pullF` (true) or S2a's `pull`. -/
def sides (c : Choice) (M : VE.FiniteModel String) (author sign pl : Bool) : Bool × Bool :=
  let U := supU NSD1; let V := choiceU NSD1 c
  (decF U (if author then U.D.T else (fill U).T) M "avoid_required" sign ["a", "u"],
   decF V (if author then V.D.T else (fill V).T) ((if pl then pullFM else pullM) NSD1 c M) "avoid_required" sign
     ["a", "u"])

-- `fill_sim`, NSD1 at `(rs1,1)` with the default excepted: with the filling yes both filled trees decide
-- positively and the author rules neither way; with the filling empty neither filled tree decides
#guard [true, false].map (sides [("rs1", 1)] (m1 true [["a", "u"]] [["a", "u"]]) false · true) ==
  [(true, true), (false, false)]
#guard [true, false].map (sides [("rs1", 1)] (m1 true [["a", "u"]] [["a", "u"]]) true · true) ==
  [(false, false), (false, false)]
#guard [true, false].map (sides [("rs1", 1)] (m1 true [["a", "u"]] []) false · true) == [(false, false), (false, false)]
-- `fill_sim_author`, both sides true: NSD1 at `(rs1,0)`, empty tables, the strict `no-deception` decides
#guard [true, false].map (sides [("rs1", 0)] (m1 false [] []) true · true) == [(true, true), (false, false)]
-- with S2a's `pull` in place of `pullF` the gap's table is dropped and the choice's `F_p` never applies (S-5)
#guard sides [("rs1", 1)] (m1 true [["a", "u"]] [["a", "u"]]) false true false == (true, false)

/-! ## `sd_superpose_conflict_free`, each direction

A CONFLICT side is shown by a filled finite model that is a base of the side's premises (background, `Fill_T`, `X`)
where a conflict target of the filled tree holds; the choice's side reads the model's filled pull. The CONFLICT-FREE
direction on NSD4a and NSD4c under `A = [(rs1,1)]` is derived through the per-choice route
(`tests/test_readings_sd_lean.py::test_sd_superpose_conflict_free_derived_rows`). -/

/-- Whether `M` with the filling `F` is a base of `U` with `X`, and whether a conflict target of `fill U` holds on it. -/
def conflictAt (U : VE.NormDefaults.UDoc) (X : List VE.Formula) (M : VE.FiniteModel String)
    (F : VE.NormDefaults.FiniteFill U String) : Bool × Bool :=
  (VE.Norms.backgroundValid U.D M && VE.NormDefaults.fillValid U M F && X.all (·.eval (M.withFill F) []),
   (VE.Norms.targets (fill U)).any fun t => (VE.NormDefaults.allTuples M t.2.1).any fun vs =>
     t.2.2.eval (M.withFill F) (VE.Norms.tupleVal vs))
/-- The filling of `y_permitted`: yes for `a`, or empty. -/
def fY {U : VE.NormDefaults.UDoc} (y : Bool) : VE.NormDefaults.FiniteFill U String :=
  fun n => if y && n == "unsaid__y_permitted" then [["a"]] else []
/-- `conflictAt` on the superposed side under `A` and on choice `c`'s side. -/
def bothSides (N : NDoc) (A c : Choice) (M : VE.FiniteModel String) (y : Bool) : (Bool × Bool) × (Bool × Bool) :=
  (conflictAt (supU N) (slotUnder N.D A ++ supX N) M (fY y), conflictAt (choiceU N c) (choiceX N c) (pullFM N c M) (fY y))

-- CONFLICT on both sides: NSD4c and NSD4 under `A = []`, bits naming `(rs1,0)` (strict `must-x`, guard `y_permitted`),
-- wherever the filling says `y_permitted`; with the filling empty no target holds
#guard [NSD4c, NSD4].all fun N => bothSides N [] [("rs1", 0)] (m4 false [] []) true == ((true, true), (true, true))
#guard bothSides NSD4c [] [("rs1", 0)] (m4 false [] []) false == ((true, false), (true, false))
-- NSD4a under `A = [(rs1,1)]` rests on `supX`'s coherence premise: where both defaults select, the model is a base of
-- neither side, and with `[]` for `supX` it is a base where a target holds (CONFLICT)
#guard bothSides NSD4a [("rs1", 1)] [("rs1", 1)] (m4 true [] []) true == ((false, true), (false, true))
#guard conflictAt (supU NSD4a) (slotUnder NSD4a.D [("rs1", 1)] ++ []) (m4 true [] []) (fY true) == (true, true)
-- NSD4c under `A = [(rs1,1)]`: the strict `need-not-x` blocks the default `must-x`; the same model is a base of both
-- sides with no target
#guard bothSides NSD4c [("rs1", 1)] [("rs1", 1)] (m4 true [] []) true == ((true, false), (true, false))

/-! ## `sharedEnvSD` is the free document's vocabulary, not `supU`'s (sc-10a review F2)

`sd_superpose_all`'s queries are typed over `sharedEnvSD`. A query naming a superposed decision table or a bit is typed
over `fill (supU N)`'s vocabulary and not over `sharedEnvSD N`. -/

def q5 : VE.Formula := .all "agent" (.all "user" (.binary "soft__excepted__rd_2_no_deception" (.var 1) (.var 0)))
def q6 : VE.Formula := .unary "ve__bit__1__0" (.const "ve__here")
#guard [q5, q6].all fun q => !q.check (sharedEnvSD NSD1) [] &&
  q.check (envAt (fill (supU NSD1)) (size (fill (supU NSD1)))) []

/-! ## `sd_superpose_all` and `sd_superpose_countermodel` (13.5)

A filled finite model is checked as the per-choice route checks one: `modelCheckX` (a base where the premises hold, and
the query's value) and `localFree`; the choice's side reads the model's filled pull. The certificate rows are the
per-choice route's (`tests/test_readings_sd_lean.py::test_fsd1_verdicts_query_some_all_none`: `(rs1,0)` proved, ALL
under `rs1:0`, `(rs1,1)` refuted); no superposed certificate exists under `A = []`, since the countermodel below names
`(rs1,1)`. -/

/-- A finite model over `Entity`, each entity named by itself. -/
def toE (M : VE.FiniteModel String) : VE.FiniteModel VE.Bridge.Entity where
  domains s := (M.domains s).map (("", ·))
  constants x := (M.constants x).map (("", ·))
  relations p := (M.relations p).map (·.map (("", ·)))
def avoidAll : VE.Formula := .all "agent" (.all "user" (.binary "avoid_required" (.var 1) (.var 0)))
def fillOf {U : VE.NormDefaults.UDoc} (F : List (String × List (List String))) :
    VE.NormDefaults.FiniteFill U VE.Bridge.Entity :=
  fun n => (((F.find? (·.1 == n)).map (·.2)).getD []).map (·.map (("", ·)))
/-- `modelCheckX` and `localFree` on the superposed side under `A` and on choice `c`'s side. -/
def checkSides (N : NDoc) (A c : Choice) (M : VE.FiniteModel String) (F : List (String × List (List String)))
    (Γ : List VE.Formula) (φ : VE.Formula) : (Bool × Bool × Bool) × (Bool × Bool × Bool) :=
  let r1 := VE.NormDefaults.modelCheckX (supU N) (slotUnder N.D A ++ supX N) (toE M) (fillOf F) ((sup N.D).2 ++ Γ) φ
  let r2 := VE.NormDefaults.modelCheckX (choiceU N c) (choiceX N c) (toE (pullFM N c M)) (fillOf F)
    ((choiceDoc N.D c).2 ++ Γ) φ
  ((r1.1, r1.2, VE.Readings.Wire.localFree (supU N) (toE M) (fillOf F)),
   (r2.1, r2.2, VE.Readings.Wire.localFree (choiceU N c) (toE (pullFM N c M)) (fillOf F)))
/-- The choices a model's bits name. -/
def named (N : NDoc) (M : VE.FiniteModel String) : List Choice :=
  (choices N.D).filter fun c => (atoms N.D c).all (·.eval M [])

-- the countermodel: NSD1 under `A = []`, the bit on, `soft__excepted__rd_2_no_deception = {(a,u)}`, the filling no.
-- It passes with the query false and `localFree`; its bits name `(rs1,1)`, whose side it is a countermodel of. Read as
-- `(rs1,0)` (the other choice) it holds the query: that choice's strict rule decides it
#guard named NSD1 (m1 true [["a", "u"]] []) == [[("rs1", 1)]]
#guard checkSides NSD1 [] [("rs1", 1)] (m1 true [["a", "u"]] []) [] [] avoidAll ==
  ((true, false, true), (true, false, true))
#guard (checkSides NSD1 [] [("rs1", 0)] (m1 true [["a", "u"]] []) [] [] avoidAll).2 == (true, true, true)
-- under `A = [(rs1,0)]` a model naming `(rs1,0)` holds the query on both sides (ALL)
#guard checkSides NSD1 [("rs1", 0)] [("rs1", 0)] (m1 false [] []) [] [] avoidAll == ((true, true, true), (true, true, true))
-- without `hl`: NSD4 under `A = [(rs1,0)]`, `Γ = [∃a. y_permitted a]`, `φ = ⊥`, the bit naming `(rs1,0)`, the filling yes
-- for `y_permitted`, every excepted table empty. The model passes `modelCheckX` with `⊥` false, but it is not
-- `localFree` on either side, so it has no expansion and is no `CounterX`
#guard checkSides NSD4 [("rs1", 0)] [("rs1", 0)] (m4 false [] []) [("unsaid__y_permitted", [["a"]])]
  [.ex "assistant" (.unary "y_permitted" (.var 0))] .bottom == ((true, false, false), (true, false, false))

end VE.Readings.SoftSupExamples
