import VE.SoftNorms.Run

/-! rights-cfr-2-budget-1 (docs/rights/rights-cfr-2-budget-1/REPORT.md): WP(T) under pair evidence,
`SoftNorms.Run.openAfterClassification`, which is `Wire.openCoherence` (the one owner of the open weighing points)
less the pairs the evidence discharges as DISJOINT. The fixture is four default rules on `x_required` whose pairs (a,b)
and (c,d) have disjoint guards, with a DISJOINT certificate for each; (a,d) and (b,c) stay open. It was written by
docs/rights/rights-cfr-2-budget-1/evidence/soft_pairs_fixture.py. -/
namespace ResponseShape.SoftPairsChecks
open Lean VE.SoftNorms.Run

def parse (s : String) : Json := (Json.parse s).toOption.getD .null
def env : Json := parse "{\"language\":\"ve.core@0.2\",\"profiles\":[\"norms@0\",\"relational-fol@0\",\"soft-norms@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"constants\":{},\"predicates\":{\"q\":{\"arguments\":[\"assistant\"],\"description\":\"q\"},\"r\":{\"arguments\":[\"assistant\"],\"description\":\"r\"},\"x_permitted\":{\"arguments\":[\"assistant\"],\"description\":\"permission\",\"regulated\":{\"act\":\"{0} do x\",\"default\":\"allow\",\"role\":\"permission\"}},\"x_required\":{\"arguments\":[\"assistant\"],\"description\":\"obligation\",\"regulated\":{\"act\":\"{0} do x\",\"default\":\"deny\",\"permission\":\"x_permitted\",\"role\":\"obligation\"}}},\"sorts\":{\"assistant\":{\"description\":\"assistant\"},\"user\":{\"description\":\"user\"}}}}"
def norms : Json := parse "[{\"norm\":{\"exception\":{\"decided_by\":\"assistant\",\"factors\":[],\"necessary\":[],\"sufficient\":[]},\"guard\":[\"unary\",\"q\",[\"var\",0]],\"mode\":\"default\",\"name\":\"a\",\"over\":[],\"predicate\":\"x_required\",\"sign\":true,\"unless\":[]}},{\"norm\":{\"exception\":{\"decided_by\":\"assistant\",\"factors\":[],\"necessary\":[],\"sufficient\":[]},\"guard\":[\"not\",[\"unary\",\"q\",[\"var\",0]]],\"mode\":\"default\",\"name\":\"b\",\"over\":[],\"predicate\":\"x_required\",\"sign\":false,\"unless\":[]}},{\"norm\":{\"exception\":{\"decided_by\":\"assistant\",\"factors\":[],\"necessary\":[],\"sufficient\":[]},\"guard\":[\"unary\",\"r\",[\"var\",0]],\"mode\":\"default\",\"name\":\"c\",\"over\":[],\"predicate\":\"x_required\",\"sign\":true,\"unless\":[]}},{\"norm\":{\"exception\":{\"decided_by\":\"assistant\",\"factors\":[],\"necessary\":[],\"sufficient\":[]},\"guard\":[\"not\",[\"unary\",\"r\",[\"var\",0]]],\"mode\":\"default\",\"name\":\"d\",\"over\":[],\"predicate\":\"x_required\",\"sign\":false,\"unless\":[]}}]"
def pairs : Json := parse "{\"soft:coherence:a,b\":{\"certificate\":{\"checker_version\":\"ve-tableau-checker@2\",\"conclusion_meaning_id\":\"3bb33b9232d2e9e2349aa3838a7089557e3a0941fd81be6c43415dedfe63a2fe\",\"environment_id\":\"6769952ea4c7f941bf0dd2ba94201185c64781a85902cfa3715513a6ef29eb7a\",\"premise_meaning_ids\":[],\"trace\":{\"at\":0,\"children\":[{\"at\":1,\"children\":[{\"at\":2,\"children\":[{\"at\":3,\"children\":[{\"at\":4,\"children\":[{\"at\":5,\"children\":[{\"at\":7,\"children\":[{\"at\":11,\"children\":[{\"rule\":\"close\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}},\"document_hash\":\"638163a3afc981ebe641986a1e8e2d0d681ed92b391730d33d2973d7dd32b968\",\"environment_id\":\"6bf04d435a2813d2a0189cb5e14348758dd2fa41c284bc35fb43ebf637d5dfd5\",\"target\":\"soft:coherence:a,b\"},\"soft:coherence:c,d\":{\"certificate\":{\"checker_version\":\"ve-tableau-checker@2\",\"conclusion_meaning_id\":\"91ee5d4205b1995ec4790c269c6e2d7476a54cd3cdc20141983f4c61f0b74ed2\",\"environment_id\":\"6769952ea4c7f941bf0dd2ba94201185c64781a85902cfa3715513a6ef29eb7a\",\"premise_meaning_ids\":[],\"trace\":{\"at\":0,\"children\":[{\"at\":1,\"children\":[{\"at\":2,\"children\":[{\"at\":3,\"children\":[{\"at\":4,\"children\":[{\"at\":5,\"children\":[{\"at\":7,\"children\":[{\"at\":11,\"children\":[{\"rule\":\"close\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}],\"rule\":\"expand\"}},\"document_hash\":\"638163a3afc981ebe641986a1e8e2d0d681ed92b391730d33d2973d7dd32b968\",\"environment_id\":\"6bf04d435a2813d2a0189cb5e14348758dd2fa41c284bc35fb43ebf637d5dfd5\",\"target\":\"soft:coherence:c,d\"}}"
def openWith (evidence : Json) : Option (List String) := do
  let src ← (VE.SoftNorms.Wire.decodeSoftSource env norms).toOption
  (openAfterClassification src env norms evidence).toOption

def all : List String := ["soft:coherence:a,b", "soft:coherence:a,d", "soft:coherence:b,c", "soft:coherence:c,d"]
-- No evidence: every colliding pair no ranking resolves is open (`openCoherence`, the rights route's count).
#guard openWith .null == some all
#guard ((VE.SoftNorms.Wire.decodeSoftSource env norms).toOption.map (VE.SoftNorms.Wire.openCoherence ·.D)) == some all
-- Both DISJOINT certificates discharge their pairs; the two others stay open, in order.
#guard openWith pairs == some ["soft:coherence:a,d", "soft:coherence:b,c"]
-- One certificate alone discharges only its pair.
#guard openWith (pairs.setObjVal! "soft:coherence:c,d" .null) == some ["soft:coherence:a,d", "soft:coherence:b,c", "soft:coherence:c,d"]

end ResponseShape.SoftPairsChecks
