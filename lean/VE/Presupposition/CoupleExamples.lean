import VE.Presupposition.Couple.Fixtures

/-! PS-3's fixtures (docs/spec/presupposition.md 7.2 and 4.8): S15 (mixed carriers have the models of the uniform
pick), S18 (an external constraint leaves a group uncoupled), S19 (identical guards: one group, 2 picks not 2^5;
different guards: 5 goals uncoupled plus the source-identity choice), S22 (`SatUnder` under the completion, the raw
placeholder `deny` refuting both picks), R-3 (a pick never names in place), and lf-14d's budget over 64 joint
choices (`ResourceLimit: joint choices`, UNKNOWN). The `#guard`s only; the fixture data and the proofs about it
(S15's `SameModels`, S22's completion) are in VE/Presupposition/Couple/Fixtures.lean. -/
namespace VE.Presupposition.CoupleExamples
open VE.Presupposition VE.Presupposition.Examples

/-! ## S19: "the user" in 5 rules (spec 7.2, the `couplable` row) -/
#guard J19.length == 32
#guard (groups fixtureTable same19).length == 1
#guard (groups fixtureTable same19).all (fun g => couplable J19 g)
#guard (coupledSet J19 (groups fixtureTable same19)).length == 2
#guard (coupledSet J19 (groups fixtureTable same19)).all (fun ch => (groups fixtureTable same19).all (uniformB · ch))
#guard (groups fixtureTable diff19).length == 0
#guard (coupledSet J19 (groups fixtureTable diff19)).length == 32
-- `rep` changes only the group's members: a pick outside every group is its own representative
#guard (groups fixtureTable same19).all (fun g =>
  rep g [("o1", .conditioned), ("x", .assumed)] == [("o1", .conditioned), ("x", .assumed)])
#guard (groups fixtureTable same19).all (fun g =>
  rep g [("o1", .conditioned), ("o2", .assumed), ("x", .conditioned)] ==
    [("o1", .assumed), ("o2", .assumed), ("x", .conditioned)])
#guard [[("o1", .asserted), ("o2", .conditioned)], [("o1", .asserted), ("o2", .assumed)],
  [("o1", .conditioned), ("o2", .conditioned)]].map (repCandidate g3) == [.asserted, .assumed, .conditioned]
#guard J19.filter (fun ch => VE.Discourse.satisfiesAll (K19 same19) (choiceOf fixtureTable same19 ver0 ch)) ==
  coupledSet J19 ((groups fixtureTable same19).filter (couplable J19))
#guard (K19 diff19).constraints.isEmpty
#guard (K19 same19).constraints.length == 50
#guard choiceOf fixtureTable same19 ver0 [("o1", .conditioned), ("o2", .assumed)] == [("o1", 0, 1), ("o2", 0, 0)]
#guard (match VE.Discourse.compatibleChoices (K19 same19) sets5 VE.Scope.choiceLimit with
  | .ok cs => cs == (coupledSet J19 ((groups fixtureTable same19).filter (couplable J19))).map
      (choiceOf fixtureTable same19 ver0) && cs.length == 2
  | .error _ => false)
#guard (match VE.Discourse.compatibleChoices (K19 diff19) sets5 VE.Scope.choiceLimit with
  | .ok cs => cs == J19.map (choiceOf fixtureTable diff19 ver0) | .error _ => false)
-- The source-identity choice: offered once for the shared closed `pre`, with the different guards too; never imposed
-- (the joint set, the groups and the coupled set above are computed without it).
#guard sourceChoices E19 diff19 == [⟨sourceLabel, preUser, ids5⟩]
#guard sourceChoices E19 same19 == [⟨sourceLabel, preUser, ids5⟩]
-- a `pre` that is not closed, or one rule act alone, offers none
#guard sourceChoices E19 { diff19 with checked := diff19.checked.map (fun c => { c with pre := owner }) } == []
#guard sourceChoices E19 { diff19 with checked := diff19.checked.take 1 } == []
#guard sourceChoices E19 { diff19 with checked := diff19.checked.map (fun c => { c with pos := .top }) } == []

/-! ## S18: an existing constraint excludes both uniform picks -/
#guard !couplable J18 g18
#guard uniformB g18 (rep g18 (J18.headD []))
#guard rep g18 (J18.headD []) == [("o1", .assumed), ("o2", .assumed)]
#guard couplingConstraints ver0 J18 [g18] == []
#guard (coupledSet J18 ([g18].filter (couplable J18))).length == 2
-- with both uniform picks present it is couplable
#guard couplable (J18 ++ [[("o1", .assumed), ("o2", .assumed)], [("o1", .conditioned), ("o2", .conditioned)]]) g18
-- a cell that is not all root carriers is never couplable, and `groups` never forms a group on one: the negated
-- cell lists in place (R-3); the same two obligations at the top cell form one group
#guard !couplable J18 { g18 with cands := [.assumed, .unconditional] }
#guard groups fixtureTable (neg2 .negated) == [] && (groups fixtureTable (neg2 .top)).length == 1
#guard couplable [pAA, pAC, pCC] g18 && couplable [pAC, pCC, pAA] g18
#guard !couplable [pAC, pCC] g18 && !couplable [pCC, pAC] g18
#guard !couplable [pAA, pAC, pCC] { g18 with cands := [.assumed, .unconditional] }
#guard !couplable [pAA, pAC, pCC] { g18 with cands := [.unconditional, .assumed] }
#guard repCandidate g18 [("o1", .conditioned), ("o2", .asserted)] == .asserted
#guard repCandidate g18 [("o1", .conditioned), ("o2", .assumed)] == .assumed
#guard decide (Uniform g18 pAA) && !decide (Uniform g18 pAC) && decide (Uniform { g18 with members := [] } pAC)
#guard !uniformB g18 pAC && uniformB { g18 with members := [] } pAC
-- two groups, interleaved, the first with a third member last: every position of `groups`' lists, and `coupledSet`
-- over two groups (uniform on both: 2 × 2 of the 32 picks)
#guard groups fixtureTable rep2 ==
  [{ members := ["o1", "o2", "o5"], goal := gA, cands := [.assumed, .conditioned] },
   { members := ["o3", "o4"], goal := gB, cands := [.assumed, .conditioned] }]
#guard (coupledSet J19 (groups fixtureTable rep2)).length == 4
-- a cell with in place first or last: no group on it
#guard groups tIn (neg2 .negated) == [] && groups fixtureTable (neg2 .negated) == []

/-! ## R-3: a pick names emitted readings only -/
#guard decide (PickFits fixtureTable repNeg [("o1", .conditioned)])
#guard !decide (PickFits fixtureTable repNeg [("o1", .inPlace)])
#guard !decide (PickFits fixtureTable repNeg [])
#guard !decide (PickFits fixtureTable repNeg [("o1", .conditioned), ("o1", .assumed)])
#guard !decide (PickFits fixtureTable repNeg [("o9", .conditioned)])
#guard !decide (PickFits fixtureTable repNeg [("o1", .conditioned), ("o9", .conditioned)])

/-! ## lf-14d's budget: over 64 joint choices is `ResourceLimit: joint choices` (UNKNOWN), unchanged -/
#guard (match VE.Discourse.compatibleChoices VE.Discourse.emptyManifest sets7 VE.Scope.choiceLimit with
  | .error e => e == "ResourceLimit: joint choices" | .ok _ => false)
#guard (match VE.Discourse.compatibleChoices (K19 same19) sets7 VE.Scope.choiceLimit with
  | .error e => e == "ResourceLimit: joint choices" | .ok _ => false)
#guard (match VE.Discourse.compatibleChoices VE.Discourse.emptyManifest (sets7.take 6) VE.Scope.choiceLimit with
  | .ok cs => cs.length == 64 | .error _ => false)

/-! ## S15: mixed carriers in two units, one goal `U` -/
#guard (groups fixtureTable R15).length == 1
#guard (groups fixtureTable R15).all (couplable J15)
#guard (groups fixtureTable R15).all (fun g => rep g mixed15 == [("o1", .assumed), ("o2", .assumed)])
-- mixed [B1, U, U → B2] and uniform assumed [B1, U, B2, U]: the same models, the same assumptions
#guard formulasUnder D15 R15 mixed15 == [theOwner, theOwnerU, .implies theOwnerU theOwnerBusy]
#guard (groups fixtureTable R15).all (fun g =>
  formulasUnder D15 R15 (rep g mixed15) == [theOwner, theOwnerU, theOwnerBusy, theOwnerU])
#guard (groups fixtureTable R15).all (fun g =>
  models15.map (fun M => holds M (formulasUnder D15 R15 mixed15)) ==
    models15.map (fun M => holds M (formulasUnder D15 R15 (rep g mixed15))))
#guard models15.map (fun M => holds M (formulasUnder D15 R15 mixed15)) == [false, false, true, false]
#guard assumptionsUnder D15 R15 mixed15 == [theOwnerU]
#guard (groups fixtureTable R15).all (fun g => assumptionsUnder D15 R15 (rep g mixed15) == [theOwnerU, theOwnerU])
#guard J15.all (fun ch => decide (PickFits fixtureTable R15 ch))
#guard treeUnder D15 R15 mixed15 == emptyTree
#guard formulasUnder D15x R15x mixed15 == [bgF, saidF] ++ formulasUnder D15 R15 mixed15
#guard (treeUnder D15x R15x mixed15).nodes == D15x.norms.nodes && D15x.norms.nodes.length == 1
#guard assumptionsUnder D15x R15x mixed15 == [theOwnerU]
#guard (pickedU D15x R15x mixed15).D.lits == ["lit"] && (pickedU D15x R15x mixed15).unspec == []
#guard (groups fixtureTable R15x).length == 1 && decide (PickFits fixtureTable R15x mixed15)
#guard holds mNone (formulasUnder D15 R15 cond15) && !holds mNone (formulasUnder D15 R15 mixed15)
#guard formulasUnder D2n R15 cond15 == [bgF, saidF] ++ formulasUnder D15 R15 cond15
#guard (treeUnder D2n R15 cond15).nodes == [fixedNode, nodeY]
#guard (VE.Norms.elaborate (treeUnder D2n R15 cond15)).map (ev mXo) == [true, false]
#guard (VE.Norms.elaborate (treeUnder D2n R15 cond15)).map (ev mYo) == [false, true]

/-! ## S22 (R-9): two picks on an `unspecified` predicate, a gap where no rule decides and `p` is true -/
#guard (groups fixtureTable R22).length == 1
#guard (groups fixtureTable R22).all (fun g => rep g mixed22 == rep22)
#guard (treeUnder D22 R22 mixed22).nodes == [node22 "r-o1", conditionNode (node22 "r-o2") instr]
#guard formulasUnder D22 R22 mixed22 == [(chk22 "o1").goal]
-- the raw W1 form, which applies the placeholder `deny` at `s2`, refutes both picks
#guard [rep22, mixed22].all (fun ch => !holds m22 (VE.Norms.elaborate (treeUnder D22 R22 ch)))
#guard [rep22, mixed22].all (fun ch => holds m22 (formulasUnder D22 R22 ch))
-- `PickedWF`: both picks pass norm-defaults' check; an undeclared `unspecified` predicate fails it, only with the block
#guard [rep22, mixed22].all (fun ch => decide (PickedWF D22 R22 ch))
#guard !decide (PickedWF { D22 with unspec := ["q"] } R22 rep22)
#guard decide (PickedWF { D22 with unspec := ["q"], defaults := false } R22 rep22)
#guard holds mDec (formulasUnder D22n R22 cond22 ++ VE.Norms.elaborate (treeUnder D22n R22 cond22))
#guard (VE.Norms.decides (treeUnder D22n R22 rep22) "p" true).eval mDec ["s1"] &&
  !(VE.Norms.decides (treeUnder D22n R22 cond22) "p" true).eval mDec ["s1"]

end VE.Presupposition.CoupleExamples
