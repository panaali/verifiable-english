import VE.Readings.Verdicts
import VE.Readings.UnspecifiedExamples

/-! The fixtures of RD-3 (docs/spec/readings-defaults.md 8.2), each a `#guard`: the gate of the entailment fold
(3.1 to 3.3), each direction of ALL and NONE (3.4 to 3.6), `foldConflict` and `foldPremises` (3.7, 3.8),
`restrictionsFor` against the existential side computed by brute force over the complete choices (3.9, 3.11, 3.12;
the oracle is this file's, not the spec's), `usedLabels` (3.10), and thirty narrowed sets whose thirty labels are
computed without the 2^30 complete choices (3.13). -/
namespace VE.Readings.VerdictsExamples
open VE.Readings
open VE.Readings.UnspecifiedExamples (ND1 ND1n rs1 frame1 cand mustHelp mustHelpAsks)

def c0 : Choice := [("rs_1", 0)]
def c1 : Choice := [("rs_1", 1)]
def c2 : Choice := [("rs_1", 2)]
def rows (rs : List ChoiceResult) : List (Choice × ChoiceResult) := [c0, c1, c2].zip rs

/-- F-ND1's set with a third reading, so that `rs_1@1:2` is a choice of the document. -/
def D3 : Doc := ⟨.norms, frame1, [.set ⟨"rs_1", "u1", 1, [cand "every" mustHelp, cand "asks" mustHelpAsks,
  cand "third" mustHelp]⟩], [], []⟩

/-! ### The gate (review A2) and ALL, NONE, SOME -/

-- 3.1: the gate passed; SOME tolerates a row without a result
#guard (foldEntailment (rows [.free, .free, .free]) (rows [.proved, .refuted, .unknown]),
  reasonOf (rows [.free, .free, .free]) (rows [.proved, .refuted, .unknown])) == (.some, none)
-- 3.2: one conflict row unknown: UNKNOWN naming it
#guard (foldEntailment (rows [.free, .free, .unknown]) (rows [.proved, .proved, .proved]),
  reasonOf (rows [.free, .free, .unknown]) (rows [.proved, .proved, .proved])) ==
  (.unknown, some (.conflictStatus .unknown c2))
#guard choiceText D3 c2 == "rs_1@1:2"
-- 3.3: one conflict row CONFLICT: never ALL
#guard (foldEntailment (rows [.free, .conflict]) (rows [.proved, .proved]),
  reasonOf (rows [.free, .conflict]) (rows [.proved, .proved])) == (.unknown, some (.conflictStatus .conflict c1))
#guard choiceText D3 c1 == "rs_1@1:1"
-- 3.4, 3.5: ALL and NONE past the gate
#guard foldEntailment (rows [.free, .free]) (rows [.proved, .proved]) == .all
#guard foldEntailment (rows [.free, .free]) (rows [.refuted, .refuted]) == .none
-- 3.6: one row short of ALL
#guard (foldEntailment (rows [.free, .free, .free]) (rows [.proved, .proved, .unknown]),
  reasonOf (rows [.free, .free, .free]) (rows [.proved, .proved, .unknown])) == (.unknown, some (.noResult c2))
-- no rows: no verdict
#guard foldEntailment [] [] == .unknown

/-! ### `foldConflict` and `foldPremises`, each direction -/

-- 3.7
#guard [rows [.free, .free], rows [.free, .unknown, .conflict], rows [.free, .unknown], []].map foldConflict ==
  [.free, .conflict, .unknown, .unknown]
-- 3.8
#guard [rows [.inconsistent, .model], rows [.inconsistent, .inconsistent], rows [.inconsistent, .unknown], []].map
  foldPremises == [.model, .inconsistent, .unknown, .unknown]

/-! ### `restrictionsFor` against the existential side -/

/-- Every complete choice of `D`, by brute force (the oracle of 3.9, 3.11 and 3.12 only). -/
def completeChoices (D : Doc) : List Choice :=
  D.sets.foldr (fun R acc => (List.range R.candidates.length).flatMap (fun i => acc.map ((R.id, i) :: ·))) [[]]
/-- The existential side of `restrictionsFor_spec`, in `restrictionsFor`'s label order. -/
def existential (D : Doc) (A : Choice) : List String :=
  ((D.couplings.map ("coupling:" ++ ·.id)) ++ (D.narrowings.map ("narrowing:" ++ ·.id))).filter (fun l =>
    (completeChoices D).any (fun c => complete D c && A.all (c.contains ·) && excludedBy D l c))
def takes (D : Doc) (A : Choice) : Bool := (choices D).any (fun c => A.all (c.contains ·))

-- 3.9: `n1` excludes the choice of reading 1 when `A` does not fix the set, nothing when `A` fixes it
#guard (restrictionsFor ND1n.D [], existential ND1n.D [], takes ND1n.D []) == (["narrowing:n1"], ["narrowing:n1"], true)
#guard (restrictionsFor ND1n.D c0, existential ND1n.D c0, takes ND1n.D c0) == ([], [], true)
#guard (restrictionsFor ND1.D [], existential ND1.D []) == ([], [])
-- 3.11: without a compatible choice taking `A` the two sides differ (`hA` is needed)
#guard (restrictionsFor ND1n.D c1, existential ND1n.D c1, takes ND1n.D c1) == ([], ["narrowing:n1"], false)
#guard untakenText ND1n.D c1 == "ReadingsUnsatisfiable: no compatible reading takes rs_1@1:1"

/-- 3.12: two sets of F-ND1's readings, labelled `all` and `some` on the axis `who`, coupled by `k1`. -/
def labelled (id : String) : ReadingSet :=
  ⟨id, id ++ "-unit", 1, [{ cand "every" mustHelp with labels := [("who", "all")] },
    { cand "asks" mustHelpAsks with labels := [("who", "some")] }]⟩
def Dk : Doc := ⟨.norms, frame1, [.set (labelled "rs_1"), .set (labelled "rs_2")],
  [⟨"k1", "who", [("rs_1", 1), ("rs_2", 1)]⟩], []⟩

#guard Dk.couplings.all (couplingShape Dk)
#guard choices Dk == [[("rs_1", 0), ("rs_2", 0)], [("rs_1", 1), ("rs_2", 1)]]
#guard [[], [("rs_1", 0)], [("rs_1", 0), ("rs_2", 0)]].map (fun A => (restrictionsFor Dk A, existential Dk A)) ==
  [(["coupling:k1"], ["coupling:k1"]), (["coupling:k1"], ["coupling:k1"]), ([], [])]

/-! ### 3.13: thirty narrowed sets, no product -/

def setK (k : Nat) : ReadingSet := ⟨s!"rs_{k}", s!"u{k}", 1, [cand "every" mustHelp, cand "asks" mustHelpAsks]⟩
def D30 : Doc := ⟨.norms, frame1, (List.range 30).map (fun k => .set (setK (k + 1))), [],
  (List.range 30).map (fun k => ⟨s!"n{k + 1}", s!"rs_{k + 1}", 1, ["every"]⟩)⟩

#guard (choices D30).length == 1
#guard restrictionsFor D30 [] == (List.range 30).map (fun k => s!"narrowing:n{k + 1}")
#guard 2 ^ 30 = 1073741824

/-! ### 3.10: `usedLabels` -/

def P : VE.Formula := .unary "help_permitted" (.const "a")
def L2 : VE.Compose.Labelled := [("unsaid:pair:help_required,help_permitted", P), ("other", .bottom)]
/-- A check that passes exactly when every formula of `need` is among the checked formulas. -/
def needs (need : List VE.Formula) (fs : List VE.Formula) : Bool := need.all (fs.contains ·)

#guard usedLabels (needs [P]) [] L2 [] == ["unsaid:pair:help_required,help_permitted"]
#guard usedLabels (needs []) [] L2 [] == []
#guard usedLabels (needs [P, .bottom]) [] L2 [] == ["unsaid:pair:help_required,help_permitted", "other"]
#guard L2.wellLabelled

end VE.Readings.VerdictsExamples
