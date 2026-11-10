import VE.Presupposition.Couple
import VE.Presupposition.Examples
import VE.Discourse.Admission
import VE.Scope.Readings

/-! PS-3's fixture data and the proofs about it (docs/spec/presupposition.md 7.2 and 4.8). The `#guard`s on
these fixtures are in VE/Presupposition/CoupleExamples.lean, which imports this module: a broken proof here is cut by
tools/trust_mutants.py (it never cuts a proof in its --test file) and the guards decide the mutant. -/
namespace VE.Presupposition.CoupleExamples
open VE.Presupposition VE.Presupposition.Examples

def emptyTree : VE.Norms.Tree := { regulated := [], definitions := [], nodes := [] }
def allPicks : List String → List Candidate → List Pick
  | [], _ => [[]]
  | o :: os, cs => cs.flatMap (fun k => (allPicks os cs).map (fun ch => (o, k) :: ch))

/-! ## S19: "the user" in 5 rules (spec 7.2, the `couplable` row) -/
def preUser : VE.Formula := .ex "entity" (.unary "user" (.var 0))
def E19 : VE.Environment :=
  { sorts := ["entity"], predicates := fun p => if p == "user" then some ["entity"] else none,
    constants := fun _ => none }
def chk (i : String) (g : VE.Formula) : Checked :=
  { ob := { id := i, unit := "u-" ++ i, span := (0, 0), row := "plural", position := .ruleAct ("r-" ++ i),
            args := {}, carrier := .unresolved },
    frame := .hole, pre := preUser, reading := none, goal := g, pos := .ruleAct }
def ids5 : List String := ["o1", "o2", "o3", "o4", "o5"]
def report19 (g : String → VE.Formula) : Report :=
  { checked := ids5.map (fun i => chk i (g i)), bases := [], baseTree := emptyTree }
def same19 : Report := report19 (fun _ => .unary "user_exists" (.const "c"))
def diff19 : Report := report19 (fun i => .unary ("guard_" ++ i) (.const "c"))
def J19 : List Pick := allPicks ids5 [.assumed, .conditioned]
-- `repCandidate`: assumed over asserted over conditioned
def g3 : Group := { members := ["o1", "o2"], goal := .top, cands := [.assumed, .conditioned] }
-- `couplings_spec` on S19: lf-14d's `satisfiesAll` with the generated constraints keeps exactly the coupled set.
def ver0 : String → Nat := fun _ => 0
def K19 (R : Report) : VE.Discourse.Manifest :=
  { VE.Discourse.emptyManifest with
    constraints := VE.Discourse.emptyManifest.constraints ++ couplingConstraints ver0 J19 (groups fixtureTable R) }
-- through lf-14d's enumeration: one reading set per obligation, named by it (PS-4 must name the sets so)
def sets5 : List VE.Route.Admission.ReadingSet := ids5.map (fun o => ⟨o, 0, [.top, .bottom]⟩)

/-! ## S18: an existing constraint excludes both uniform picks -/
def g18 : Group := { members := ["o1", "o2"], goal := .top, cands := [.assumed, .conditioned] }
def J18 : List Pick := [[("o1", .assumed), ("o2", .conditioned)], [("o1", .conditioned), ("o2", .assumed)]]
def neg2 (pc : PositionClass) : Report :=
  { checked := ["o1", "o2"].map (fun i => { chk i .top with pos := pc }), bases := [], baseTree := emptyTree }
-- positions inside lists (the trust-mutants survivors): the pick or candidate that decides is first, middle or last
def pAA : Pick := [("o1", .assumed), ("o2", .assumed)]
def pCC : Pick := [("o1", .conditioned), ("o2", .conditioned)]
def pAC : Pick := [("o1", .assumed), ("o2", .conditioned)]
def gA : VE.Formula := .unary "a_exists" (.const "c")
def gB : VE.Formula := .unary "b_exists" (.const "c")
def rep2 : Report :=
  { checked := [chk "o1" gA, chk "o3" gB, chk "o2" gA, chk "o4" gB, chk "o5" gA], bases := [], baseTree := emptyTree }
def gC : VE.Formula := .unary "c_exists" (.const "c")
def rep3 : Report := { rep2 with checked := rep2.checked ++ [chk "o6" gC, chk "o7" gC] }
def tIn : CandidateTable := fun _ pc => if pc == .negated then [.inPlace, .assumed] else [.assumed, .conditioned]

/-! ## R-3: a pick names emitted readings only -/
def chkNeg : Checked := { chk "o1" .top with pos := .negated }
def repNeg : Report := { checked := [chkNeg], bases := [], baseTree := emptyTree }

/-! ## lf-14d's budget: over 64 joint choices is `ResourceLimit: joint choices` (UNKNOWN), unchanged -/
def sets7 : List VE.Route.Admission.ReadingSet :=
  (List.range 7).map (fun i => ⟨"o" ++ toString i, 0, [.top, .bottom]⟩)

/-! ## S15: mixed carriers in two units, one goal `U` -/
def theOwnerBusy : VE.Formula := (definite 0 "entity" owner busy).strong
def chk15 (i : String) : Checked :=
  { ob := { id := i, unit := "u-" ++ i, span := (0, 0), row := "definite", position := .path [],
            args := {}, carrier := .unresolved },
    frame := .hole, pre := theOwnerU, reading := none, goal := theOwnerU, pos := .top }
def R15 : Report :=
  { checked := [chk15 "o1", chk15 "o2"], bases := [("u-o1", theOwner), ("u-o2", theOwnerBusy)],
    baseTree := emptyTree }
def unit15 (i : String) : DocUnit :=
  { id := "u-" ++ i, asserted := true,
    content := .readings (((R15.checked.find? (·.ob.id == i)).bind (expectedReadings fixtureTable R15)).getD []) }
def D15 : PDoc :=
  { E := E19, lits := [], norms := emptyTree, defaults := false, unspec := [], background := [],
    units := [unit15 "o1", unit15 "o2"], proofs := [], block := none }
def J15 : List Pick := allPicks ["o1", "o2"] [.assumed, .conditioned]
def mixed15 : Pick := [("o1", .assumed), ("o2", .conditioned)]
def mOneReadyBusy : VE.FiniteModel String :=
  model [("entity", ["a"])] [("owner", [["a"]]), ("ready", [["a"]]), ("busy", [["a"]])] []
def models15 : List (VE.FiniteModel String) := [mNone, mOne, mOneReadyBusy, mTwoReady]
def holds (M : VE.FiniteModel String) (as : List VE.Formula) : Bool := as.all (ev M)
-- the same units with a background formula, a literal, a fixed rule, an asserted and an unasserted claim unit, and a
-- resolved obligation listed first in the readings unit
def bgF : VE.Formula := .unary "bg" (.const "c")
def saidF : VE.Formula := .unary "said" (.const "c")
def fixedNode : VE.Norms.Node := { name := "r-fixed", pred := "x", sign := true, guard := .top, carveOuts := [], over := [] }
def c0 : Checked := { chk15 "o1" with ob := { (chk15 "o1").ob with id := "o0", carrier := .asserted } }
def R15x : Report := { R15 with checked := c0 :: R15.checked }
def unitsX : List DocUnit :=
  [{ id := "u-a", asserted := true, content := .claim saidF },
   { id := "u-n", asserted := false, content := .claim (.unary "unsaid" (.const "c")) }]
def D15x : PDoc :=
  { E := E19, lits := ["lit"], norms := { regulated := [], definitions := [], nodes := [fixedNode] },
    defaults := false, unspec := [], background := [bgF], units := unitsX ++ D15.units, proofs := [], block := none }
-- `SameModels` and `SameDecides` (spec 4.8): a pick has its own models; the all-conditioned pick does not have the
-- mixed pick's (no owner: mixed asserts `B1`, all-conditioned holds vacuously).
def cond15 : Pick := [("o1", .conditioned), ("o2", .conditioned)]
example : SameModels.{0} D15 R15 mixed15 mixed15 :=
  ⟨(fun h => by simp [D15] at h), (fun h => by simp [D15] at h), fun _ _ => Iff.rfl⟩
example : SameDecides.{0} D15 R15 mixed15 mixed15 := fun _ _ _ _ _ _ _ _ => Iff.rfl
example : ¬ SameModels.{0} D15 R15 mixed15 cond15 := by
  intro h
  have hadm : mNone.asStructure.Admissible D15.E :=
    ⟨(fun _ _ hc => nomatch hc), fun _ _ hr => by simp [VE.FiniteModel.asStructure, mNone, model] at hr⟩
  have hc : SatUnder D15 R15 cond15 mNone.asStructure := by
    unfold SatUnder; rw [if_neg (by decide)]
    exact fun a ha => (VE.eval_iff_denote _ _ _).mp (List.all_eq_true.mp
      (by decide : holds mNone (formulasUnder D15 R15 cond15 ++ VE.Norms.elaborate (treeUnder D15 R15 cond15))) a ha)
  have hm := (h.2.2 _ hadm).mpr hc
  unfold SatUnder at hm; rw [if_neg (by decide)] at hm
  have : holds mNone (formulasUnder D15 R15 mixed15 ++ VE.Norms.elaborate (treeUnder D15 R15 mixed15)) = true :=
    List.all_eq_true.mpr fun a ha => (VE.eval_iff_denote _ _ _).mpr (hm a ha)
  exact absurd this (by decide)
-- two background formulas, two fixed rules over two regulated predicates: each premise read, first and last
def regOf (p : String) : VE.Norms.Regulated :=
  { name := p, sorts := ["entity"], allowByDefault := false, role := .obligation, act := none, permission := none }
def nodeY : VE.Norms.Node := { fixedNode with name := "r-y", pred := "y" }
def D2n : PDoc :=
  { D15 with background := [bgF, saidF],
             norms := { regulated := [regOf "x", regOf "y"], definitions := [], nodes := [fixedNode, nodeY] } }
def mXo : VE.FiniteModel String := model [("entity", ["a"])] [("x", [["a"]])] []
def mYo : VE.FiniteModel String := model [("entity", ["a"])] [("y", [["a"]])] []
example : ¬ SatUnder.{0} D2n R15 cond15 mXo.asStructure := by
  unfold SatUnder; rw [if_neg (by decide)]; intro h
  have : holds mXo (VE.Norms.elaborate (treeUnder D2n R15 cond15)) = true :=
    List.all_eq_true.mpr fun a ha => (VE.eval_iff_denote _ _ _).mpr (h a (List.mem_append_right _ ha))
  exact absurd this (by decide)
example : ¬ SatUnder.{0} D2n R15 cond15 mYo.asStructure := by
  unfold SatUnder; rw [if_neg (by decide)]; intro h
  have : holds mYo (VE.Norms.elaborate (treeUnder D2n R15 cond15)) = true :=
    List.all_eq_true.mpr fun a ha => (VE.eval_iff_denote _ _ _).mpr (h a (List.mem_append_right _ ha))
  exact absurd this (by decide)

/-! ## S22 (R-9): two picks on an `unspecified` predicate, a gap where no rule decides and `p` is true -/
def g22 : VE.Formula := .unary "g" (.var 0)
def instr : VE.Formula := .ex "entity" (.unary "instruction" (.var 0))
def reg22 : VE.Norms.Regulated :=
  { name := "p", sorts := ["situation"], allowByDefault := false, role := .obligation, act := some "follow",
    permission := none }
def node22 (n : String) : VE.Norms.Node :=
  { name := n, pred := "p", sign := true, guard := g22, carveOuts := [], over := [] }
def E22 : VE.Environment :=
  { sorts := ["situation", "entity"],
    predicates := fun p => if p == "p" || p == "g" then some ["situation"]
      else if p == "instruction" then some ["entity"] else none,
    constants := fun _ => none }
def chk22 (i : String) : Checked :=
  { ob := { id := i, unit := "u-" ++ i, span := (0, 0), row := "definite", position := .ruleAct ("r-" ++ i),
            args := {}, carrier := .unresolved },
    frame := .hole, pre := instr, reading := none, goal := ruleGoal reg22 (node22 ("r-" ++ i)) instr,
    pos := .ruleAct }
def R22 : Report :=
  { checked := [chk22 "o1", chk22 "o2"], bases := [],
    baseTree := { regulated := [reg22], definitions := [], nodes := [node22 "r-o1", node22 "r-o2"] } }
def unit22 (i : String) : DocUnit :=
  { id := "u-" ++ i, asserted := true,
    content := .readings (((R22.checked.find? (·.ob.id == i)).bind (expectedReadings fixtureTable R22)).getD []) }
def D22 : PDoc :=
  { E := E22, lits := [], norms := { regulated := [reg22], definitions := [], nodes := [] }, defaults := true,
    unspec := ["p"], background := [], units := [unit22 "o1", unit22 "o2"], proofs := [], block := none }
def rep22 : Pick := [("o1", .assumed), ("o2", .assumed)]
def mixed22 : Pick := [("o1", .assumed), ("o2", .conditioned)]
/-- `p` holds at `s1` (decided) and at the gap `s2`; `unsaid__p` is norm-defaults' filling at the gap. -/
def m22 : VE.FiniteModel String :=
  model [("situation", ["s1", "s2"]), ("entity", ["i"])]
    [("g", [["s1"]]), ("instruction", [["i"]]), ("p", [["s1"], ["s2"]]), ("unsaid__p", [["s2"]])] []
/-- `forget [p]` of a finite model is the finite model without `p`. -/
def dropRel (M : VE.FiniteModel String) (p : String) : VE.FiniteModel String :=
  { M with relations := fun q => if q = p then [] else M.relations q }
theorem forget_asStructure (M : VE.FiniteModel String) (p : String) :
    VE.Norms.forget [p] M.asStructure = (dropRel M p).asStructure := by
  unfold VE.Norms.forget VE.FiniteModel.asStructure dropRel
  congr 1; funext q vs; by_cases h : q = p <;> simp [h]
theorem denote_of_eq {S T : VE.Structure.{0}} (h : S = T) (a : VE.Formula) (ρ : List S.Carrier)
    (ρ' : List T.Carrier) (hρ : HEq ρ ρ') : a.denote S ρ ↔ a.denote T ρ' := by
  subst h; cases hρ; exact Iff.rfl
/-- The completion at a unary unspecified predicate, read off `decides` on a finite model. -/
theorem intendedAt3_of_eval (U : VE.NormDefaults.UDoc) (r : VE.Norms.Regulated) (M : VE.FiniteModel String)
    (s : String) (hs : r.sorts = [s]) (hc : VE.NormDefaults.completionOf U r = .unspecified)
    (h : (M.domains s).all (fun v =>
      (!(VE.Norms.decides U.D.T r.name true).eval (dropRel M r.name) [v] || decide ([v] ∈ M.relations r.name)) &&
      (!(VE.Norms.decides U.D.T r.name false).eval (dropRel M r.name) [v] || !decide ([v] ∈ M.relations r.name)))
      = true) :
    VE.NormDefaults.IntendedAt3 U r M.asStructure := by
  intro vs hvs
  rw [hs] at hvs
  match vs, hvs with
  | [v], ⟨hv, _⟩ =>
    have hb := List.all_eq_true.mp h v hv
    simp only [Bool.and_eq_true, Bool.or_eq_true, Bool.not_eq_true', decide_eq_true_eq] at hb
    have key : ∀ b, VE.Norms.DecidesD U.D.T (VE.Norms.forget [r.name] M.asStructure) (VE.Norms.tupleVal [v])
        r.name b ↔ (VE.Norms.decides U.D.T r.name b).eval (dropRel M r.name) [v] = true := fun b => by
      rw [← VE.Norms.decides_denote, VE.eval_iff_denote]
      exact denote_of_eq (forget_asStructure M r.name) _ _ _ HEq.rfl
    unfold VE.NormDefaults.Value3
    rw [VE.NormDefaults.value3_holds, hc, key, key]
    refine ⟨fun hp => ?_, fun hn => ?_, fun _ => ⟨(fun h => nomatch h), (fun h => nomatch h)⟩⟩
    · rcases hb.1 with h1 | h1
      · simp [hp] at h1
      · simpa using h1
    · rcases hb.2 with h1 | h1
      · simp [hn] at h1
      · simpa using h1
/-- A computed model of a picked document under the completion. -/
theorem satUnder_of_eval (D : PDoc) (R : Report) (ch : Pick) (M : VE.FiniteModel String) (hd : D.defaults = true)
    (hf : holds M (formulasUnder D R ch) = true)
    (hi : ∀ r ∈ D.norms.regulated, VE.NormDefaults.IntendedAt3 (pickedU D R ch) r M.asStructure) :
    SatUnder D R ch M.asStructure := by
  unfold SatUnder; rw [if_pos hd]
  exact ⟨fun a ha => (VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp hf a ha), hi⟩
-- `SameDecides` both ways: without the block, all-conditioned and all-assumed decide `p` differently at `s1` (`g`
-- holds, no instruction); a pick decides as itself (above).
def D22n : PDoc := { D22 with defaults := false }
def cond22 : Pick := [("o1", .conditioned), ("o2", .conditioned)]
def mDec : VE.FiniteModel String := model [("situation", ["s1"]), ("entity", ["i"])] [("g", [["s1"]])] []
example : ¬ SameDecides.{0} D22n R22 cond22 rep22 := by
  intro h
  have hadm : mDec.asStructure.Admissible D22n.E := by
    refine ⟨(fun _ _ hc => nomatch hc), fun p vs hr => ?_⟩
    by_cases hp : p = "g"
    · subst hp
      have : vs = ["s1"] := by simpa [VE.FiniteModel.asStructure, mDec, model] using hr
      subst this
      exact ⟨["situation"], rfl, by simp [VE.TupleTyped, VE.FiniteModel.asStructure, mDec, model]⟩
    · simp [VE.FiniteModel.asStructure, mDec, model, Ne.symm hp] at hr
  have hs : SatUnder D22n R22 cond22 mDec.asStructure := by
    unfold SatUnder; rw [if_neg (by decide)]
    exact fun a ha => (VE.eval_iff_denote _ _ _).mp (List.all_eq_true.mp
      (by decide : holds mDec (formulasUnder D22n R22 cond22 ++ VE.Norms.elaborate (treeUnder D22n R22 cond22))) a ha)
  have hd := h _ hadm hs reg22 (by simp [D22n, D22]) ["s1"]
    (by simp [VE.TupleTyped, VE.FiniteModel.asStructure, mDec, model, reg22]) true
  rw [← VE.eval_iff_denote, ← VE.eval_iff_denote] at hd
  exact absurd (hd.mpr (by decide)) (by decide)
theorem s22_completion (ch : Pick) (hch : ch = rep22 ∨ ch = mixed22) : SatUnder D22 R22 ch m22.asStructure := by
  rcases hch with rfl | rfl <;>
  · refine satUnder_of_eval _ _ _ _ rfl (by decide) fun r hr => ?_
    obtain rfl : r = reg22 := by simpa [D22] using hr
    exact intendedAt3_of_eval _ _ _ "situation" rfl rfl (by decide)

end VE.Presupposition.CoupleExamples
