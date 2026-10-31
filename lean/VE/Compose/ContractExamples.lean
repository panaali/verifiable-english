import VE.Compose.Contract
import VE.Service.ScopeExamples

/-! PC-3's fixtures (profile-composition 5.3: F3.1, F3.1b, F3.4 to F3.7) as build-time checks. The scope documents
are `VE.Service.ScopeExamples`': `doc` governs its two items `i1` and `i2` by one `frame` governor; `full` is the
same rules written out, without scope. -/

namespace VE.Compose.ContractExamples
open Lean VE.Compose VE.Compose.Contract VE.Service.Document VE.Service.ScopeExamples

/-! F3.1: `checkDocSets_pipeline` on the two-unit scope document. The answer is `pipeline [scopeRewriter]`, then
`checkCore`, then `foldGovernors`; the pipeline is GOVERN alone, and it rewrites the case. -/

#guard (pipelineOf profileTable (profilesOf doc) docRewriters).map (·.profile) == ["scope@0"]
#guard (checkDocSets doc).isOk
#guard (checkDocSets doc).toOption == (do
  let D ← VE.Scope.decodeScope doc
  let a ← checkCore (← pipeline [scopeRewriter] doc)
  pure (VE.Scope.foldGovernors D a)).toOption
-- Not the identity: the pipeline hands the chain the items' parts written out as norms under the lead's frame.
#guard (pipeline [scopeRewriter] doc).toOption.map (·.getObjValD "units") !=
  some (toJson (units (some (part "r1")) (some (part "r2"))))
#guard ((pipeline [scopeRewriter] doc).toOption.bind fun j => ((j.getObjValD "units").getArrVal? 1).toOption).map
  (fun u => ((u.getObjValD "content").getObjValD "norm").getObjValD "name") == some (.str "r1")
#guard (pipeline [scopeRewriter] doc).toOption != some doc

/-! `pipeline_off`'s example: on a case that does not list `scope@0` GOVERN is off and the pipeline is the
identity. -/

#guard scopeRewriter.on full == false
#guard (pipeline [scopeRewriter] full).toOption == some full

/-! F3.1b: a document with no governor and no part. GOVERN returns the block's document (`govern_identity`), so
`scopeRewriter.run` hands the chain the case's own units. -/

def ungoverned : Json := case (front (units none none) listed (some (block [])))

#guard (VE.Scope.decodeScope ungoverned).toOption.map (fun D =>
  (D.governors.isEmpty, (VE.Scope.partUnits D).isEmpty, (VE.Scope.govern D).toOption == some D.doc)) ==
  some (true, true, true)
#guard (scopeRewriter.run ungoverned).toOption.map (·.getObjValD "units") == some (toJson (units none none))
#guard (checkDocSets ungoverned).isOk

/-! F3.4: C1 to C3. -/

example : ∀ r ∈ profileTable, slotAgrees r.slot r.interface = true := interface_slot
example : ∀ r ∈ profileTable, ∀ s ∈ profileTable, r.profile = s.profile → r.interface = s.interface :=
  interface_functional
example : ((rewriters profileTable).map (·.1)).Nodup := rewriter_ranks_distinct

/-- F3.4b, F3.4c. The planned rows' slots and interface values (1.1's table, synthesis round 2 edit 6). Each owning
plan confirms its value in its row batch; until then the profile has no row, so the gate refuses it. -/
def plannedRows : List ProfileRow :=
  (["presupposition@0", "modality@0", "hedges@0", "purposes@0", "examples@0"].map fun p =>
    ⟨p, [], [], "layer", .layer⟩) ++
  [⟨"commitments@0", [], [], "commitments", .outside⟩] ++
  (["weighing", "attitudes", "scales", "events"].map fun k => ⟨s!"{k}@0", [], [], "pack", .pack k⟩)

-- F3.4b: C1 on the planned rows, and on qt-a3c's `cardinality@0` row, whose slot is "layer".
#guard plannedRows.all fun r => slotAgrees r.slot r.interface
#guard (profileTable.filter (·.profile == "cardinality@0")).map (fun r => (r.slot, r.interface)) == [("layer", .layer)]
-- `slotAgrees` names no `"cardinality"` slot, and each interface refuses another's slot.
#guard [slotAgrees "cardinality" .outside, slotAgrees "layer" (.pack "weighing"), slotAgrees "pack" .chain,
  slotAgrees "pack" .layer, slotAgrees "govern" .layer, slotAgrees "soft" .outside, slotAgrees "checker" .base,
  slotAgrees "risk" (.rewrite 12)] == List.replicate 8 false
-- F3.4c: the values.
#guard plannedRows.map (fun r => (r.profile, r.interface)) ==
  [("presupposition@0", .layer), ("modality@0", .layer), ("hedges@0", .layer), ("purposes@0", .layer),
   ("examples@0", .layer), ("commitments@0", .outside), ("weighing@0", .pack "weighing"),
   ("attitudes@0", .pack "attitudes"), ("scales@0", .pack "scales"), ("events@0", .pack "events")]
-- The values of main's rows (1.1's Interface column), one per profile in table order.
#guard (profileTable.map (fun r => (r.profile, r.interface))).eraseDups ==
  [("alternatives@0", .outside), ("risk@0", .outside), ("speech-acts@0", .outside), ("relational-fol@0", .checker),
   ("reports@0", .outside), ("order@0", .checker), ("nary@0", .checker), ("rights@0", .chain),
   ("soft-norms@0", .chain), ("norm-defaults@0", .chain), ("norms@0", .chain), ("acts@0", .rewrite 11),
   ("closure@0", .checker), ("data@0", .base), ("definitions@0", .base), ("documents@1", .layer), ("time@0", .base),
   ("judgments@0", .layer), ("cardinality@0", .layer), ("ve.discourse@1", .rewrite 10),
   ("right-clauses@0", .rewrite 20), ("readings@1", .rewrite 30), ("scope@0", .rewrite 12)]
-- A planned profile has no row: the gate refuses it, as today.
#guard plannedRows.all fun r => !profileTable.any (·.profile == r.profile)
#guard (match gateOf profileTable ["norms@0", "presupposition@0", "relational-fol@0"] with
  | .error e => e | .ok _ => "ok") == "UnsupportedProfile: Unsupported profile presupposition@0"

/-! F3.5, F3.6: the rewriters of main's table and the stack order. -/

#guard rewriters profileTable ==
  [(11, "acts@0"), (10, "ve.discourse@1"), (20, "right-clauses@0"), (30, "readings@1"), (12, "scope@0")]
#guard stackOf profileTable ["norms@0", "readings@1", "relational-fol@0", "scope@0"] == ["scope@0", "readings@1"]
#guard stackOf profileTable ["acts@0", "norms@0", "relational-fol@0", "scope@0"] == ["acts@0", "scope@0"]
#guard stackOf profileTable ["norms@0", "relational-fol@0", "scope@0"] == ["scope@0"]
#guard stackOf profileTable ["norms@0", "relational-fol@0"] == []
#guard stackOf profileTable ["readings@1", "right-clauses@0", "scope@0", "ve.discourse@1"] ==
  ["ve.discourse@1", "scope@0", "right-clauses@0", "readings@1"]

/-! F3.7: a run statement alone is not evidence. An entry that refuses every case satisfies `ScopeRunsOf`; the
route facts add GOVERN's own faithfulness and preservation, and a stack no batch has listed has none. -/

example : ScopeRunsOf (fun _ => .error "refused") := refuseAll_runs
example : RouteFacts ["scope@0"] ↔ ScopeRuns ∧ ScopeFaithful ∧ ScopePreserves := .rfl
example : ¬ RouteFacts ["acts@0", "scope@0"] := id
example : ∀ s ∈ listedStacks, RouteFacts s := listed_evidence
#guard listedStacks == [["scope@0"], ["scope@0", "readings@1"]]

end VE.Compose.ContractExamples
