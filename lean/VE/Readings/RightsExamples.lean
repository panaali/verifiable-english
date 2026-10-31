import VE.Readings.BarQuiet
import VE.Rights.Examples

/-! S2b's fixtures on rights documents (docs/spec/composition-PLAN.md section 5), as build-time checks. F21: set
`rs48` {0: claim `no-expel` on `expel_permitted`, 1: liberty `may-move` on `move_permitted`}, both declaring right
`r13`, beside a fixed bar (reading `rule`). `sup F21` keeps correlate's bar node on `move_permitted`, guarded by
`rights__bar__1` alone, and `Choice_D` holds `∀x:person. rights__bar__1(x) → χ_liberty` under the liberty's quiescence
label. `f21_bar_dead`: under the claim choice the bar node is dead at every well-sorted tuple. `f21_needs_typed`: at
the ill-sorted tuple `[e]` it is live, so without `TupleTyped S r.sorts vs` the rights case of `superpose_faithful`
is false (reviews/dri-decisions-20261031-cmp-s2b.md item 1 (a)). F7 and F10: a fixed limitation over candidate lines,
and limitation candidates; their `lim` and `cond` keys are owned and quiesced by candidate. -/
namespace VE.Readings.RightsExamples
open VE.Readings
open VE.Norms (Sat tupleVal)
open VE.Norms.Checks (perm)
open VE.Rights.Examples (strictNode line mkRights barRule l29)
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

theorem perm21 : VE.Rights.permPreds (sup F21).1 = ["move_permitted"] := by decide
theorem bar21 : VE.Rights.barPreds (sup F21).1 = ["move_permitted"] := by
  rw [VE.Rights.barPreds, perm21]; simp [VE.SoftNorms.dedup, VE.Route.sortStrings]
theorem barIndex21 : VE.Rights.barIndex (sup F21).1 "move_permitted" = 1 := by rw [VE.Rights.barIndex, bar21]; rfl
theorem bar21_c0 : VE.Rights.barPreds (choiceDoc F21 c0).1 = [] := by
  have : VE.Rights.permPreds (choiceDoc F21 c0).1 = [] := by decide
  rw [VE.Rights.barPreds, this]; simp [VE.SoftNorms.dedup, VE.Route.sortStrings]

def N2 : SoftNode := { strictNode "rd-2-may-move" "move_permitted" true with guard := .and .top chi1 }
def N3 : SoftNode :=
  { strictNode "rights-bar-1" "move_permitted" false (.unary "rights__bar__1" (.var 0)) [] ["rd-2-may-move"] with
    hard := true }

/-- The bar node is correlate's, guarded by aimed alone; the liberty's line is gated by its atom. -/
theorem rules21 : rulesOn (correlate (sup F21).1) "move_permitted" = [N2, N3] := by
  simp only [rulesOn, correlate, VE.Rights.barNodes, bar21, List.map_cons, List.map_nil, VE.Rights.barNode,
    VE.Rights.aimedF, barIndex21]
  decide
theorem children21 : VE.SoftNorms.children (correlate (sup F21).1) N3 = [] := by
  simp only [VE.SoftNorms.children, correlate, VE.Rights.barNodes, bar21]
  decide
theorem rules21_c0 : rulesOn (correlate (choiceDoc F21 c0).1) "move_permitted" = [] := by
  simp only [rulesOn, correlate, VE.Rights.barNodes, bar21_c0]
  decide
theorem genKeys21 : genKeys (sup F21).1 = [(.aimed "move_permitted", "rights__bar__1", ["person"])] := by
  simp only [genKeys, keyedNodes, VE.Rights.barNodes, bar21, List.map_cons, List.map_nil, VE.Rights.barNode,
    VE.Rights.aimedF, barIndex21]
  decide
theorem aimedOwners21 : aimedOwners F21 "move_permitted" = [[(0, 1)]] := by decide
theorem choicePremises21 : choicePremises F21 = [quiet21] := by
  simp only [choicePremises, choiceLabelled, quietOwn, quietShared, genKeys21]
  decide

/-! ## F21 at well-sorted tuples: the dead bar node (DRI condition (b)) -/

theorem f21_bar_dead {S : VE.Structure.{u}} (he : Encodes F21 c0 S) (hq : Sat S (choicePremises F21))
    {vs : List S.Carrier} (ht : VE.TupleTyped S ["person"] vs) :
    ¬ LiveD (correlate (sup F21).1) S (tupleVal vs) (VE.Rights.barNode (sup F21).1 "move_permitted") := by
  have hs : VE.SoftNorms.sortsOf (sup F21).1.soft "move_permitted" = ["person"] := by decide
  refine bar_dead hq (by decide) (by rw [bar21]; simp) (by simp [fixedGenerated, owners, aimedOwners21])
    (fun o ho hd => ?_) (hs ▸ ht)
  rw [aimedOwners21, List.mem_singleton] at ho
  subst ho
  have h1 := (he rs48 (by simp [F21, Doc.sets]) 1 (by simp [rs48])).mp
  exact absurd (h1 (by simpa [conj, atomAt] using hd)) (by decide)

/-! ## F21 at an ill-sorted tuple: the counterexample (DRI condition (a)) -/

def M21 : VE.FiniteModel String where
  domains s := if s == "ve__reading" then ["h"] else []
  constants x := if x == "ve__here" then some "h" else none
  relations p := if p == "rights__bar__1" then [["e"]] else []

theorem encodes21 : Encodes F21 c0 M21.asStructure := by
  intro R hR i hi
  have hR' : R = rs48 := by simpa [F21, Doc.sets] using hR
  subst hR'
  have hi' : i = 0 ∨ i = 1 := by simp [rs48] at hi; omega
  rcases hi' with rfl | rfl
  · rw [← VE.eval_iff_denote]; decide
  · rw [← VE.eval_iff_denote]; decide

theorem quiet21_sat : Sat M21.asStructure (choicePremises F21) := by
  rw [choicePremises21]
  intro φ hφ
  rw [List.mem_singleton] at hφ
  subst hφ
  rw [← VE.eval_iff_denote]; decide

theorem untyped21 : ¬ VE.TupleTyped M21.asStructure rM.sorts ["e"] := by
  simp [VE.TupleTyped, rM, perm, VE.FiniteModel.asStructure, M21]

theorem value21_sup : ValueSoft (correlate (sup F21).1) rM M21.asStructure ["e"] = some false := by
  have hF : DecidesSoftD (correlate (sup F21).1) M21.asStructure (tupleVal ["e"]) "move_permitted" false := by
    refine ⟨N3, by rw [rules21]; simp, rfl, ⟨?_, by rw [children21]; simp⟩⟩
    refine ⟨?_, by simp [N3, strictNode], ?_, by simp [N3, strictNode]⟩
    · show (VE.Formula.unary "rights__bar__1" (.var 0)).denote M21.asStructure ["e"]
      rw [← VE.eval_iff_denote]; decide
    · simp [VE.SoftNorms.switchF, VE.SoftNorms.switchIn, N3, strictNode, VE.Norms.anyF, VE.Formula.denote]
  have hT : ¬ DecidesSoftD (correlate (sup F21).1) M21.asStructure (tupleVal ["e"]) "move_permitted" true := by
    rintro ⟨N, hN, hsg, hsel⟩
    rw [rules21] at hN
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hN
    rcases hN with rfl | rfl
    · have hg : (VE.Formula.and .top chi1).denote M21.asStructure ["e"] := hsel.1.1
      rw [← VE.eval_iff_denote] at hg
      exact absurd hg (by decide)
    · cases hsg
  unfold ValueSoft VE.Norms.catalaValue
  simp [hF, hT, rM, perm]

theorem value21_choice : ValueSoft (correlate (choiceDoc F21 c0).1) rM (pull F21 c0 M21.asStructure) ["e"] =
    some true := by
  have h : ∀ b, ¬ DecidesSoftD (correlate (choiceDoc F21 c0).1) (pull F21 c0 M21.asStructure) (tupleVal ["e"])
      "move_permitted" b := by
    rintro b ⟨N, hN, _⟩
    rw [rules21_c0] at hN
    cases hN
  unfold ValueSoft VE.Norms.catalaValue
  simp [h, rM, perm]

/-- Without `ht` the rights case of `superpose_faithful` is false: every hypothesis of the approved statement holds
    for F21, the claim choice and M21, and the two values differ at the ill-sorted tuple `[e]`. -/
theorem f21_needs_typed (hw : WellFormedDoc F21 = true) (hs : superposable F21 = true) :
    ¬ ∀ (D : Doc), WellFormedDoc D = true → superposable D = true → ∀ c, Compatible D c →
      ∀ (S : VE.Structure.{0}), Encodes D c S → Sat S (choicePremises D) →
      ∀ r ∈ (correlate (choiceDoc D c).1).T.regulated, ∀ vs : List S.Carrier,
        ValueSoft (correlate (sup D).1) r S vs = ValueSoft (correlate (choiceDoc D c).1) r (pull D c S) vs := by
  intro H
  have hr : rM ∈ (correlate (choiceDoc F21 c0).1).T.regulated := by
    show rM ∈ (choiceDoc F21 c0).1.soft.T.regulated
    decide
  have := H F21 hw hs c0 (show compatible F21 c0 = true by decide) M21.asStructure encodes21 quiet21_sat rM hr ["e"]
  rw [value21_sup, value21_choice] at this
  cases this

/-! ## F7: a fixed limitation with scope all over candidate lines -/

def F7 : Doc := ⟨.rights, frame21, [.set rs48, .fixed "u111" (.limitation l29) []], [], []⟩
#guard WellFormedDoc F7 && superposable F7
-- one lim per act of a candidate line, owned by that candidate, with its cond keys
#guard ((genKeys (sup F7).1).filter (fun g => match g.1 with | .lim .. => true | _ => false)).map (fun g => owners F7 g.1)
  == [[[(0, 0)]], [[(0, 1)]]]
#guard (choiceLabelled F7).map (·.1) == ["readings:rs48@1:0:quiet", "readings:rs48@1:1:quiet"]
#guard nameMap F7 c1 "rights__lim__1" == "rights__lim__2"

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

end VE.Readings.RightsExamples
