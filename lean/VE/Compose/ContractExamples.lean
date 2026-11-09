import VE.Compose.Contract
import VE.Readings.SupExtraExamples
import VE.Service.ScopeExamples

/-! PC-3's fixtures (profile-composition 5.3: F3.1, F3.1b, F3.4 to F3.7) as build-time checks, and one instance of
`composed_superpose_all` (1.6). The scope documents are `VE.Service.ScopeExamples`': `doc` governs its two items `i1`
and `i2` by one `frame` governor; `full` is the same rules written out, without scope. -/

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

/-- F3.1 per choice (`readings@1` beside scope): GOVERN governs one reading set, on `i1`. -/
def governedSet : Json :=
  let reading := Json.mkObj [("id", .str "a"), ("kind", .str "norm"), ("meaning_id", .str "m"),
    ("content", part "r1"), ("admission", Json.mkObj [("who", .str "translator"), ("why", .str "open")])]
  let set := Json.mkObj [("id", .str "s"), ("unit", .str "i1"), ("version", toJson (1 : Nat)),
    ("status", .str "open"), ("readings", toJson [reading])]
  case ((front (units none (some (part "r2"))) ["norms@0", "readings@1", "relational-fol@0", "scope@0"]).setObjVal!
    "reading_sets" (toJson [set]))

#guard (VE.Scope.decodeScope governedSet).toOption.map VE.Scope.governedSetUnits == some ["i1"]
#guard (checkDocSets governedSet).isOk
#guard (checkDocSets governedSet).toOption == (do
  let D ← VE.Scope.decodeScope governedSet
  let a ← checkCore (← pipeline [scopeRewriter] governedSet)
  pure (VE.Scope.foldGovernors D a)).toOption
-- The pipeline hands the chain the governed sets (`withSets`), not the units alone.
#guard (pipeline [scopeRewriter] governedSet).toOption.map (·.getObjValD "reading_sets") != some .null

/-- A rewriter for every profile that records its run, to read the order `pipelineOf` and `pipeline` give. -/
def tagRewriter (p : String) : Option (Rewriter (List String)) := some ⟨p, fun l => .ok (l ++ [p]), fun _ => true, []⟩

#guard (pipelineOf profileTable ["acts@0", "norms@0", "readings@1", "scope@0", "ve.discourse@1"] tagRewriter).map
  (·.profile) == ["ve.discourse@1", "acts@0", "scope@0", "readings@1"]
#guard (pipeline (pipelineOf profileTable ["acts@0", "norms@0", "readings@1", "scope@0", "ve.discourse@1"]
  tagRewriter) ["source"]).toOption == some ["source", "ve.discourse@1", "acts@0", "scope@0", "readings@1"]

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
  [("events@0", .pack "events"), ("alternatives@0", .outside), ("risk@0", .outside), ("speech-acts@0", .outside),
   ("relational-fol@0", .checker),
   ("reports@0", .outside), ("order@0", .checker), ("nary@0", .checker), ("rights@0", .chain),
   ("soft-norms@0", .chain), ("norm-defaults@0", .chain), ("norms@0", .chain), ("acts@0", .rewrite 11),
   ("closure@0", .checker), ("data@0", .base), ("definitions@0", .base), ("documents@1", .layer), ("time@0", .base),
   ("judgments@0", .layer), ("cardinality@0", .layer), ("ve.discourse@1", .rewrite 10),
   ("right-clauses@0", .rewrite 20), ("readings@1", .rewrite 30), ("scope@0", .rewrite 12)]
-- A planned profile has no row: the gate refuses it, as today. `events@0` has its row (et-4b), with the planned value.
#guard (plannedRows.filter fun r => profileTable.any (·.profile == r.profile)).map (·.profile) == ["events@0"]
#guard (profileTable.filter (·.profile == "events@0")).map (fun r => (r.slot, r.interface)) ==
  [("pack", .pack "events")]
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
-- The sort is stable: on a table where two ranks tie (C3 excludes it on `profileTable`) table order decides.
#guard stackOf [⟨"a@0", [], [], "layer", .rewrite 1⟩, ⟨"b@0", [], [], "layer", .rewrite 1⟩] ["a@0", "b@0"] ==
  ["a@0", "b@0"]

/-! F3.7: a run statement alone is not evidence. An entry that refuses every case satisfies `ScopeRunsOf`; the
route facts add GOVERN's own faithfulness and preservation, and a stack no batch has listed has none. -/

example : ScopeRunsOf (fun _ => .error "refused") := refuseAll_runs
example : RouteFacts ["scope@0"] ↔ ScopeRuns ∧ ScopeFaithful ∧ ScopePreserves := .rfl
example : ¬ RouteFacts ["acts@0", "scope@0"] := id
example : ∀ s ∈ listedStacks, RouteFacts s := listed_evidence
#guard listedStacks == [["scope@0"], ["scope@0", "readings@1"]]

/-! G1 with G4 (1.6): `composed_superpose_all` on S2a's M1 document `K1`, under the strict reading `A`, with one
constraint pack whose one premise `noAsks` is over the frame's base vocabulary. Every hypothesis is discharged at
`bare`, as X3 (`SupExtraExamples`) discharges `superpose_all_extra`'s without `hQw`; the closed checker runs the kernel
cannot reduce are the premise `G1Checks`, which Lean's evaluator runs. -/

namespace G1
open VE.Readings VE.Readings.SupExtraExamples
open VE.Readings.Examples (K1 modelK)
open VE.NormDefaults.Packs (Pack X)
open VE.Rights (correlate)
open VE.Norms (Sat envAt size)
open VE.SoftNorms (soften circ)
open VE.Compose (backgroundP backgroundValidP slotCheck slotConflictFreeCheck)
universe u

def noAsks : VE.Formula := .all "agent" (.all "user" (.not (.binary "asks" (.var 1) (.var 0))))
/-- `noAsks` with its quantifiers swapped, so the certificate instantiates the premise, not only matches it. -/
def noAsksUser : VE.Formula := .all "user" (.all "agent" (.not (.binary "asks" (.var 0) (.var 1))))
def askPack : Pack := ⟨"attitudes", .constraint, [], [], [("no-asks", noAsks)], [], []⟩
def qs : List Pack := [askPack]
def Qc : Pack → Choice → List VE.Formula := fun _ _ => [noAsks]
def A : Choice := [("rs1", 0)]
/-- The branch is `slotUnder K1 A ++ X qs`, the two elaborated premises and the negated goal; 2 names `noAsks`. -/
def cert : VE.Tableau.Certificate := ⟨"ve-tableau-checker@2", "", [], "",
  .expand 5 none [.expand 6 none [.expand 7 none [.expand 2 (some "w:1") [.expand 9 (some "w:0")
    [.expand 10 none [.close]]]]]]⟩
/-- `conflictCert`, one premise on: the atom of `A` comes after the slot. -/
def conflictCertA : VE.Tableau.Certificate :=
  ⟨"ve-tableau-checker@2", "", [], "", .expand 2 none [.expand 3 none [.expand 4 none [.expand 5 none [.close]]]]⟩

/-- `accepted` at a premise list in place of `slotUnder K1 A ++ X qs`. -/
def acceptedOn (P : List VE.Formula) : Bool :=
  let Y := correlate (sup K1).1
  VE.Tableau.checkCertificate (envAt (soften Y) (size (soften Y)))
    (backgroundP Y P ++ VE.Norms.elaborate (soften Y).T ++ (sup K1).2) noAsksUser cert

-- `accepted` is the one premise list, the slot and then the packs; with no pack, or the packs first, it is refused
#guard X qs == [noAsks]
#guard supCertificateCheckExtra K1 A (X qs) [] noAsksUser cert
#guard acceptedOn (slotUnder K1 A ++ X qs)
#guard !acceptedOn (X qs ++ slotUnder K1 A)
#guard !supCertificateCheckExtra K1 A [] [] noAsksUser cert
-- `hQw`: `noAsks` is over `sup K1`'s base vocabulary; X1's `noAvoid` is not, though it is accepted the same way
#guard slotCheck (correlate (sup K1).1) (X qs)
#guard !slotCheck (correlate (sup K1).1) (X [{ askPack with labelled := [("no-avoid", noAvoid)] }])
-- `hA`: a candidate no set has is refused
#guard !(candidate K1 "rs1" 2).isSome
-- `hB`: `bare` satisfies the pack; a base where one agent asks one user does not, and the conclusion fails there
#guard backgroundValidP (correlate (choiceDoc K1 A).1) (VE.Rights.limPremises (choiceDoc K1 A).1 ++ qs.flatMap (Qc · A)) bare
#guard (circ (correlate (choiceDoc K1 A).1) noAsksUser).eval bare []
#guard !backgroundValidP (correlate (choiceDoc K1 A).1) (VE.Rights.limPremises (choiceDoc K1 A).1 ++ qs.flatMap (Qc · A))
  (modelK ["u"] [["a", "u"]])
#guard !(circ (correlate (choiceDoc K1 A).1) noAsksUser).eval (modelK ["u"] [["a", "u"]]) []

/-- The closed checker runs of the instance: `X1Checks`, `accepted`, and the conflict certificates of `hcf`. -/
def G1Checks : Prop :=
  X1Checks ∧ supCertificateCheckExtra K1 A (X qs) [] noAsksUser cert = true ∧
    slotConflictFreeCheck (correlate (sup K1).1) (slotUnder K1 A) [some conflictCertA, some conflictCertA] = true

instance : Decidable G1Checks := inferInstanceAs (Decidable (_ ∧ _ ∧ _))

#guard G1Checks

/-- `hq` at the one pack: `noAsks` is over each choice's complete vocabulary, and over the frame's, which `pull` fixes. -/
theorem transfers_ask (hx : X1Checks) : Transfers.{u} K1 [noAsks] (fun _ => [noAsks]) := by
  refine ⟨fun c hc a ha => ?_, fun c _ B _ _ => ?_⟩
  · simp only [List.mem_singleton] at ha; subst ha
    rcases k1_compatible hc with rfl | rfl
    · exact (VE.check_iff_wellFormed _ _ _).mp (by decide)
    · exact (VE.check_iff_wellFormed _ _ _).mp (by decide)
  · have hd := pull_denote_frame (k1_hyps hx) c B noAsks [] ((VE.check_iff_wellFormed _ _ _).mp (by decide)) []
    constructor
    · intro h a ha; simp only [List.mem_singleton] at ha; subst ha
      exact hd.mp (h _ (.head _))
    · intro h a ha; simp only [List.mem_singleton] at ha; subst ha
      exact hd.mpr (h _ (.head _))

/-- The hypothesis `hB`: `bare` is an admissible base of the strict reading's document with the pack. -/
theorem bare_admissible_ask (hx : X1Checks) :
    VE.Compose.BaseAdmissibleP (correlate (choiceDoc K1 A).1)
      (VE.Rights.limPremises (choiceDoc K1 A).1 ++ qs.flatMap (fun p => Qc p A)) bare.asStructure := by
  refine VE.Compose.baseAdmissibleP_of_valid _ _ bare ⟨fun x s hx' => ?_, fun _ _ hr => nomatch hr⟩
    (by simp (config := { ground := true, decide := true }))
  rw [VE.Norms.envAt_constants, soften_E, envPrime_constants, choice_correlate (k1_hyps hx), choice_E] at hx'
  cases hx'

/-- The hypothesis `hcf`: the one premise list, the slot under `A` and then the pack, is conflict-free. -/
theorem conflict_free_ask (hx : G1Checks) :
    VE.Compose.ConflictFreeP.{u} (correlate (sup K1).1) (slotUnder K1 A ++ X qs) :=
  VE.Compose.conflictFreeP_append _ _ _ (VE.Compose.slot_conflict_free _
    (by rw [sup_correlate (k1_hyps hx.1)]; exact sup_wfSoft (k1_hyps hx.1)) _ _ hx.2.2)

/-- The instance: under the strict reading, on `bare`, the pack's premise gives the goal on the expansion. -/
theorem composed_instance (hx : G1Checks) :
    noAsksUser.denote (expand (choiceDoc K1 A).1 bare.asStructure) [] := by
  refine VE.Readings.composed_superpose_all K1 hx.1.1 (by decide) hx.1.2.1 A (by decide) qs Qc ?_ ?_
    (conflict_free_ask hx) [] noAsksUser
    (fun _ h => nomatch h) ((VE.check_iff_wellFormed _ _ _).mp (by decide)) cert hx.2.1 A
    (by decide : compatible K1 A = true)
    (fun _ h => h) bare.asStructure (bare_admissible_ask hx.1) ?_
  · intro p hp
    simp only [qs, List.mem_singleton] at hp
    subst hp
    exact transfers_ask hx.1
  · exact VE.Compose.slotCheck_sound _ _ (by decide)
  · rw [show (choiceDoc K1 A).2 = [] by decide]
    exact VE.Compose.sat_nil _

end G1

end VE.Compose.ContractExamples
