import VE.Rights.Examples
import VE.NormDefaults.Layered

/-! `legacy_labels_nodup` (docs/spec/premise-packs/SpecStubs_pk1.lean) is false as stated.

`WellFormedRights` checks neither limitation names nor predicate names for `:` (only the route's JSON
environment decoder applies `VE.Bridge.identifier` to predicate names, `Route/Wire.lean:98`). With limitations
`x` and `x:p`, both over all lines, and act keys `p:q` and `q`, the label
`rights:limitation:{L.name}:{act}:necessary:c` of (`x`, `p:q`) equals that of (`x:p`, `q`). `cxU` is the layered
document of the rights route, `(soften (correlate cx), [])`, and it is `WellFormedU`, so the hypotheses hold. -/
namespace VE.Rights.Examples
open VE.Norms.Checks (envOf perm oblig)
open VE.SoftNorms (SoftNode SoftDoc SoftEnv soften)

def cx : RightsDoc :=
  mkRights ["state", "person"] []
    [perm "p:q" ["state", "person"] true "{0} arrest {1}",
     perm "q" ["state", "person"] true "{0} detain {1}"]
    [] block
    [⟨"r9", "person", .top, [line .claim (strictNode "no-a" "p:q" false), line .claim (strictNode "no-b" "q" false)]⟩]
    [⟨"x", none, none, some "unstated", [⟨"c", true, "c holds", none⟩], []⟩,
     ⟨"x:p", none, none, some "unstated", [⟨"c", true, "c holds", none⟩], []⟩] []

def cxU : VE.NormDefaults.UDoc := ⟨soften (correlate cx), []⟩

-- the hypotheses of `legacy_labels_nodup`
#guard WellFormedRights cx = true
#guard VE.NormDefaults.WellFormedU cxU = true
-- its conclusion fails: the first and the last label are equal
#guard ((VE.NormDefaults.Wire.softLabelledU cxU (correlate cx) ++ limPremisesLabelled cx).map (·.1)) ==
  ["rights:limitation:x:p:q:necessary:c", "rights:limitation:x:q:necessary:c",
   "rights:limitation:x:p:p:q:necessary:c", "rights:limitation:x:p:q:necessary:c"]
#guard !decide ((VE.NormDefaults.Wire.softLabelledU cxU (correlate cx) ++ limPremisesLabelled cx).map (·.1)).Nodup
-- the extra hypothesis `hk` of the candidate `legacy_labels_nodup_of_actKeys` fails on `cx`: act key `p:q`
#guard !decide (∀ k ∈ condKeys cx, ':' ∉ k.2.1.toList)
#guard (condKeys cx).map (·.2.1) == ["p:q", "q", "p:q", "q"]

end VE.Rights.Examples
