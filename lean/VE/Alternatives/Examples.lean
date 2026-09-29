import VE.Alternatives.Validate
import VE.Norms.Checks

/-! Concrete alternatives documents in the shapes of the item-1 fixtures
(docs/spec/alternatives.md 8.1, expectations 8.2) and build-time regression
checks on them (`#guard`: the build fails if one is false).

* Well-formedness and the exact diagnostic texts (l6, n), as compiled evaluations of
  `validateAlt` (W1's validator inside it does not reduce in the kernel).
* Scenario evaluation on finite base models: `validateAlternatives` with the signed rows,
  `scenarioConflict` first (s2), then `clear°` and `followable°` by `Formula.eval` and the
  untrusted `diagnose` (a, b, c, d, e, j, o).
* The `InvalidModel` texts of 6 (l1–l4, m, p1, p6, h3).

Document-wide FOLLOWABLE (b′, f3) needs a tableau certificate from the Python proof search;
the certificate replay is the executable's `alt-followable` case, not a build-time check. -/
namespace VE.Alternatives.Examples
open VE.Norms (Regulated Node tupleVal)
open VE.Norms.Checks (envOf perm oblig rule)

/-! ## The `asimov-v2` environment and rule texts (2.6) -/

def basePreds : List (String × List String) :=
  [("available", ["action", "robot"]), ("leads_to", ["action", "harm"]), ("inaction", ["action"]),
   ("taken", ["action"]), ("harms_human", ["harm"]), ("harms_humanity", ["harm"]), ("harm_to", ["harm", "robot"]),
   ("ordered", ["action"]), ("protects_robot", ["action"]), ("injures_human", ["action"]),
   ("injures_humanity", ["action"]), ("causes", ["action", "harm"])]

def regs : List Regulated :=
  [perm "permitted" ["action"] true "{0} be performed",
   oblig "required" ["action"] false (some "permitted") "{0} be performed",
   oblig "prevent_required" ["robot", "harm"] false none "{0} prevent {1}"]

def env (consts : List (String × String) := []) : VE.Environment :=
  { envOf ["robot", "action", "harm"] (basePreds ++ regs.map (fun r => (r.name, r.sorts))) with
    constants := fun c => (consts.find? (·.1 == c)).map Prod.snd }

/-- `avoids(a, h) := ¬leads_to(a, h)`, context `[harm, action]`. -/
def avoids : VE.Formula := .not (.binary "leads_to" (.var 1) (.var 0))

def block (outcomes : Outcomes := .signed) : AltEnv :=
  { chooser := "robot", action := "action", harm := "harm", available := "available", leadsTo := "leads_to",
    outcomes := outcomes, decidedBy := some "Asimov case annotator", performed := some ("permitted", "required"),
    inaction := some "inaction", taken := some "taken", proximate := none,
    fulfilments := [⟨"prevent_required", avoids⟩] }

def doc (rules : List Node) (alt : AltEnv := block) (Γ : List VE.Formula := [])
    (consts : List (String × String) := []) : AltDoc :=
  ⟨env consts, [], alt, ⟨regs, [], rules⟩, Γ⟩

/-- `∃h. harms_human(h) ∧ allows(a, h)` in the context `[action]`. -/
def allowsHuman (p : String := "harms_human") : VE.Formula :=
  .ex "harm" (.and (.unary p (.var 0)) (.binary "allows" (.var 1) (.var 0)))

def r1 : Node := rule "law-3-permission" "permitted" true (.unary "protects_robot" (.var 0))
def r2 : Node := rule "law-2-permission" "permitted" true (.unary "ordered" (.var 0)) [] ["law-3-permission"]
/-- Rule 3 in a subset without rule 2 (its `over` entry dropped, 2.6). -/
def r3 : Node := rule "law-1-direct" "permitted" false (.unary "injures_human" (.var 0))
def r3full : Node := { r3 with over := ["law-2-permission"] }
def r4 : Node := rule "law-0-direct" "permitted" false (.unary "injures_humanity" (.var 0)) [] ["law-1-direct"]
def r5 : Node := rule "law-2-obey" "required" true (.and (.unary "ordered" (.var 0)) (.unary "permitted" (.var 0)))
def r6 : Node := rule "law-3-preserve" "required" true
  (.and (.unary "protects_robot" (.var 0)) (.unary "permitted" (.var 0)))
def asimov : List Node := [r1, r2, r3full, r4, r5, r6]

def r7 : Node := rule "inaction-allows" "permitted" false (.and (.unary "inaction" (.var 0)) (allowsHuman))
def r7p : Node := rule "allows-harm" "permitted" false (allowsHuman)
/-- Rule 8, context `[harm, robot]`. -/
def r8 : Node := rule "prevent-harm" "prevent_required" true
  (.and (.unary "harms_human" (.var 0)) (.binary "avoidable" (.var 0) (.var 1)))
def r8m : Node := rule "prevent-harm" "prevent_required" true (.unary "harms_human" (.var 0))
/-- Rule 6′: `Every robot must prevent each harm that is a harm to that robot, if that harm is avoidable by that robot.` -/
def r6p : Node := rule "prevent-self-harm" "prevent_required" true
  (.and (.binary "harm_to" (.var 0) (.var 1)) (.binary "avoidable" (.var 0) (.var 1)))
def r10 : Node := rule "inaction-allows-humanity" "permitted" false
  (.and (.unary "inaction" (.var 0)) (allowsHuman "harms_humanity"))
/-- Rule X of s2: `Every action may be performed, if that action is inaction.` -/
def rX : Node := rule "inaction-permitted" "permitted" true (.unary "inaction" (.var 0))
/-- Rule N of n: an exception to rule 7 guarded by `permitted` on another action. -/
def rN : Node := rule "no-other-permitted" "permitted" true
  (.ex "robot" (.and (.binary "available" (.var 1) (.var 0))
    (.not (.ex "action" (.and (.binary "available" (.var 0) (.var 1))
      (.and (.not (.eq (.var 0) (.var 2))) (.unary "permitted" (.var 0))))))))
  [] ["inaction-allows"]

def diag (A : AltDoc) : String :=
  match validateAlt A with
  | .ok () => "ok"
  | .error e => e

/-! ## Models -/

def model (robots actions harms : List String) (rels : List (String × List (List String)))
    (consts : List (String × String) := []) : VE.FiniteModel String where
  domains s := match s with
    | "robot" => robots
    | "action" => actions
    | "harm" => harms
    | _ => []
  constants c := (consts.find? (·.1 == c)).map Prod.snd
  relations p := ((rels.find? (·.1 == p)).map (·.2)).getD []

/-- One robot `R` with the listed alternatives, `nothing` its inaction when listed. -/
def oneRobot (actions harms : List String) (pos : List (String × String))
    (facts : List (String × List (List String)) := []) (inaction : List String := ["nothing"]) :
    VE.FiniteModel String :=
  model ["R"] actions harms
    ([("available", actions.map (fun a => [a, "R"])), ("inaction", (inaction.filter (· ∈ actions)).map ([·])),
      ("leads_to", pos.map (fun c => [c.1, c.2]))] ++ facts)
    (actions.map (fun a => (a, a)) ++ harms.map (fun h => (h, h)))

/-- Signed rows for every (alternative, harm) pair, positive exactly on `pos`. -/
def signedRows (actions harms : List String) (pos : List (String × String)) : List Row :=
  actions.flatMap fun a => harms.map fun h => ⟨a, h, pos.contains (a, h), "testimony"⟩

def validation (A : AltDoc) (M : VE.FiniteModel String) (rows : List Row) (labels : List String := []) : String :=
  match validateAlternativesWith labels A M rows with
  | .ok () => "ok"
  | .error e => e

def clearAt (A : AltDoc) (M : VE.FiniteModel String) (r : String) : List String :=
  (availOf M A.alt.available r).filter (fun a => (clearF A).eval M (tupleVal [r, a]))

def followableAt (A : AltDoc) (M : VE.FiniteModel String) (r : String) : Bool :=
  (followableF A).eval M (tupleVal [r])

def diagText (A : AltDoc) (M : VE.FiniteModel String) (r : String) : String :=
  match diagnose A M r with
  | .noAlternatives => "no alternatives"
  | .nonePermitted => "NONE-PERMITTED"
  | .overRequired req => s!"OVER-REQUIRED {req}"
  | .undischargeable d => s!"UNDISCHARGEABLE {d}"
  | .jointlyUndischargeable ds => s!"JOINTLY-UNDISCHARGEABLE {ds}"
  | .clear as => s!"clear {as}"

/-! ## Well-formedness -/

#guard diag (doc [r3, r7]) == "ok"
#guard diag (doc [r3, r8]) == "ok"
#guard diag (doc [r3, r7p]) == "ok"
#guard diag (doc [r3, r8m]) == "ok"
#guard diag (doc asimov) == "ok"
#guard diag (doc [r3, r7, r10]) == "ok"
#guard diag (doc [r3, r6p]) == "ok"
#guard diag (doc [r3, r7, rX]) == "ok"
-- l6: one predicate in two roles.
#guard diag (doc [r3, r7] { block with leadsTo := "available" }) == "AlternativesSort: leads_to expects (action, harm)"
-- n: a guard on `permitted` of another action is W1's `DependencyCycle`.
#guard (diag (doc [r3, r7, rN])).startsWith "DependencyCycle"
def reservedEnv : VE.Environment :=
  { env with predicates := fun p => if p = "allows" then some ["action", "harm"] else (env).predicates p }
#guard diag { doc [r3, r7] with E := reservedEnv } == "AlternativesReserved: allows"
#guard diag (doc [r3, r7] { block with fulfilments := [⟨"required", avoids⟩] }) == "FulfilmentOnPerformed: required"
#guard diag (doc [r3, r7] { block with performed := some ("required", "permitted") }) ==
  "AlternativesPerformed: required, permitted"
#guard diag (doc [r3, r7] { block with fulfilments := [⟨"prevent_required", .unary "permitted" (.var 1)⟩] }) ==
  "FulfilmentNotBase: prevent_required"

/-! ## Scenarios -/

/-- (a) -/
def ma : VE.FiniteModel String := oneRobot ["nothing", "pull"] ["h1"] [("nothing", "h1")] [("harms_human", [["h1"]])]
def rowsA : List Row := signedRows ["nothing", "pull"] ["h1"] [("nothing", "h1")]
#guard validation (doc [r3, r7]) ma rowsA == "ok"
-- An unrelated, undeclared relation entry is invisible to the Boolean gate.
-- This is why the generic soundness theorem needs structural validity, while
-- decoded scenarios obtain it from their decoder.
def invalidMa : VE.FiniteModel String :=
  { ma with relations := fun p => if p == "ghost" then [["R"]] else ma.relations p }
#guard validation (doc [r3, r7]) invalidMa rowsA == "ok"
theorem invalidMa_not_valid : ¬ invalidMa.Valid (VE.Norms.envAt (inlineTree (doc [r3, r7])) 0) := by
  intro h
  obtain ⟨_, hr⟩ := h
  obtain ⟨ss, hs, _⟩ := hr "ghost" ["R"] (by simp [VE.FiniteModel.asStructure, invalidMa])
  have hp : (VE.Norms.envAt (inlineTree (doc [r3, r7])) 0).predicates "ghost" = none := by decide
  rw [hp] at hs
  cases hs
#guard (scenarioConflict (doc [r3, r7]) ma).isNone
#guard (allowsF (block)).eval ma (tupleVal ["nothing", "h1"])
#guard (avoidableF (block)).eval ma (tupleVal ["h1", "R"])
#guard clearAt (doc [r3, r7]) ma "R" == ["pull"]
#guard followableAt (doc [r3, r7]) ma "R"
#guard diagText (doc [r3, r7]) ma "R" == "clear [pull]"

/-- (b): h1 under `nothing` only, h2 under `pull` only. -/
def mb (facts : List (String × List (List String)) := []) : VE.FiniteModel String :=
  oneRobot ["nothing", "pull"] ["h1", "h2"] [("nothing", "h1"), ("pull", "h2")]
    ([("harms_human", [["h1"], ["h2"]])] ++ facts)
def rowsB : List Row := signedRows ["nothing", "pull"] ["h1", "h2"] [("nothing", "h1"), ("pull", "h2")]
def pullInjures : List (String × List (List String)) := [("injures_human", [["pull"]])]
-- A₀
#guard validation (doc [r3, r7]) (mb) rowsB == "ok"
#guard clearAt (doc [r3, r7]) (mb) "R" == ["pull"]
-- A₁: a valid witness with ¬followable°: document DILEMMA for {3, 7}
#guard validation (doc [r3, r7]) (mb pullInjures) rowsB == "ok"
#guard (scenarioConflict (doc [r3, r7]) (mb pullInjures)).isNone
#guard (notFollowableF (doc [r3, r7])).eval (mb pullInjures) (tupleVal ["R"])
#guard diagText (doc [r3, r7]) (mb pullInjures) "R" == "NONE-PERMITTED"
-- A₂
#guard (notFollowableF (doc [r3, r7p])).eval (mb) (tupleVal ["R"])
#guard diagText (doc [r3, r7p]) (mb) "R" == "NONE-PERMITTED"
-- B
#guard validation (doc [r3, r8]) (mb) rowsB == "ok"
#guard (notFollowableF (doc [r3, r8])).eval (mb) (tupleVal ["R"])
#guard diagText (doc [r3, r8]) (mb) "R" ==
  "JOINTLY-UNDISCHARGEABLE [(prevent_required, [h1]), (prevent_required, [h2])]"

/-- (c): h under both alternatives. -/
def mc : VE.FiniteModel String :=
  oneRobot ["nothing", "pull"] ["h"] [("nothing", "h"), ("pull", "h")] [("harms_human", [["h"]])]
#guard (unavoidableF (block)).eval mc (tupleVal ["h", "R"])
#guard !(allowsF (block)).eval mc (tupleVal ["nothing", "h"])
#guard clearAt (doc [r3, r7]) mc "R" == ["nothing", "pull"]
#guard clearAt (doc [r3, r8]) mc "R" == ["nothing", "pull"]
#guard diagText (doc [r3, r8m]) mc "R" == "UNDISCHARGEABLE (prevent_required, [h])"

/-- (d): hs a harm to R under `nothing` only; `shield` and `retreat` protective. -/
def md : VE.FiniteModel String :=
  oneRobot ["shield", "retreat", "nothing"] ["hs"] [("nothing", "hs")]
    [("harm_to", [["hs", "R"]]), ("protects_robot", [["shield"], ["retreat"]])]
#guard diagText (doc asimov) md "R" == "OVER-REQUIRED [shield, retreat]"
#guard clearAt (doc [r3, r6p]) md "R" == ["shield", "retreat"]

/-- (e): `nothing` leads to a harm to humanity, `act` to a harm to a human and injures one. -/
def me : VE.FiniteModel String :=
  oneRobot ["nothing", "act"] ["hH", "hp"] [("nothing", "hH"), ("act", "hp")]
    [("harms_humanity", [["hH"]]), ("harms_human", [["hp"]]), ("injures_human", [["act"]])]
#guard diagText (doc [r3, r7, r10]) me "R" == "NONE-PERMITTED"

/-- (j): two ordered, non-injuring alternatives beside the inaction; no harms. -/
def mj : VE.FiniteModel String := oneRobot ["a1", "a2", "nothing"] [] [] [("ordered", [["a1"], ["a2"]])]
#guard validation (doc asimov) mj (signedRows ["a1", "a2", "nothing"] [] []) == "ok"
#guard (scenarioConflict (doc asimov) mj).isNone
#guard diagText (doc asimov) mj "R" == "OVER-REQUIRED [a1, a2]"

/-- (o): the A/B distinguishing model. -/
def mo : VE.FiniteModel String :=
  oneRobot ["nothing", "act", "rescue"] ["h"] [("nothing", "h"), ("act", "h")] [("harms_human", [["h"]])]
#guard clearAt (doc [r3, r7]) mo "R" == ["act", "rescue"]
#guard clearAt (doc [r3, r8]) mo "R" == ["rescue"]

-- (s2): rule X permits and rule 7 forbids `nothing`: CONFLICT at the scenario.
#guard ((scenarioConflict (doc [r3, r7, rX]) ma).map (fun (t, vs) => (t.1, vs))) == some ("permitted", ["nothing"])

/-! ## Model diagnostics (6) -/

-- l1: two inactions.
#guard validation (doc [r3, r7]) (oneRobot ["nothing", "wait"] ["h1"] [] [("harms_human", [["h1"]])] ["nothing", "wait"])
  (signedRows ["nothing", "wait"] ["h1"] []) == "InvalidModel(alternatives): R has two inactions: nothing, wait"
-- l2: two taken.
#guard validation (doc [r3, r7]) (oneRobot ["nothing", "pull"] ["h1"] [] [("taken", [["nothing"], ["pull"]])])
  (signedRows ["nothing", "pull"] ["h1"] []) == "InvalidModel(alternatives): R has two taken actions: nothing, pull"
-- l3: an inaction available to no chooser.
#guard validation (doc [r3, r7])
  (model ["R"] ["nothing", "pull", "idle"] [] [("available", [["nothing", "R"], ["pull", "R"]]),
    ("inaction", [["nothing"], ["idle"]])]) [] == "InvalidModel(alternatives): action idle belongs to no chooser"
-- l4: R with `pull` only and no inaction.
#guard validation (doc [r3, r7]) (oneRobot ["pull"] [] [] [] []) [] == "InvalidModel(alternatives): R has no inaction"
-- m: an action available to two choosers.
#guard validation (doc [r3, r7])
  (model ["R1", "R2"] ["a", "n1", "n2"] [] [("available", [["a", "R1"], ["a", "R2"], ["n1", "R1"], ["n2", "R2"]]),
    ("inaction", [["n1"], ["n2"]])]) [] == "InvalidModel(alternatives): action a is available to two choosers: R1, R2"
#guard validation (doc [r3, r7])
  (model ["R1", "R2"] ["a1", "a2", "n1", "n2"] [] [("available", [["a1", "R1"], ["a2", "R2"], ["n1", "R1"], ["n2", "R2"]]),
    ("inaction", [["n1"], ["n2"]])]) [] == "ok"
-- p1: the row (pull, h1) omitted under `signed`.
#guard validation (doc [r3, r7]) ma [⟨"nothing", "h1", true, "testimony"⟩] ==
  "InvalidModel(alternatives): outcome of pull for h1 unstated"
/-- p2 and p6: `complete_by` with the document's one positive cell `nothing leads to h1`. -/
def docP : AltDoc :=
  let A := doc [r3, r7] (block (.completeBy "Asimov case annotator")) [] [("nothing", "action"), ("h1", "harm")]
  { A with Γ := [.binary "leads_to" (.const "nothing") (.const "h1"), tableComplete A [("nothing", "h1")]] }
#guard diag docP == "ok"
#guard validation docP ma [⟨"nothing", "h1", true, "testimony"⟩] ["cell-1", "alternatives:table_complete"] == "ok"
#guard validation docP (oneRobot ["nothing", "pull"] ["h1"] [("nothing", "h1"), ("pull", "h1")] [("harms_human", [["h1"]])])
  [⟨"nothing", "h1", true, "testimony"⟩, ⟨"pull", "h1", true, "testimony"⟩] ["cell-1", "alternatives:table_complete"] ==
  "InvalidModel(alternatives): premise alternatives:table_complete fails"
-- h3: `causes` outside `leads_to`.
#guard validation (doc [r3, r7] { block with proximate := some "causes" })
  (oneRobot ["operate", "wait", "nothing"] ["hc", "hd"] [("operate", "hc"), ("wait", "hd"), ("nothing", "hd")]
    [("causes", [["operate", "hd"]])])
  (signedRows ["operate", "wait", "nothing"] ["hc", "hd"] [("operate", "hc"), ("wait", "hd"), ("nothing", "hd")]) ==
  "InvalidModel(alternatives): operate causes hd but does not lead to it"

end VE.Alternatives.Examples
