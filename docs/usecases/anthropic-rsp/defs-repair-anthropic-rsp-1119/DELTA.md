# defs-repair-anthropic-rsp-1119 DELTA

No user-visible change of VE, so this file has no rows. The item changes no product code of VE: nothing under `ve/`,
`lean/`, `rust/` or `tools/` changes, so VE's diagnostics, fault order, fields, verdicts, availability and CPU stay
as they are on main at 12cb72fa55. The changes are to one use case's legend text (`usecases/anthropic-rsp/
rsp_vocabulary.py` predicate descriptions; `stage0.py` D2 harm-constant descriptions and D3's coverage-date
description) and its omission sidecar (`accounting.d1.txt`, two losses that the new legends now carry), plus the
files generated from them by their own tools (`environment.d1.json`, `docs/usecases/safetyfw/anthropic-rsp/
accounting.json` and `stage0.json`, `tests/data/route-cases.jsonl`, `conformance/english-lean/lexicon-report.json`,
`conformance/english-lean/corpus-seal.json`). The identity digests that the legends feed change (D2's
`environment_id` in stage0.json; the RSP `lexicon_id`; the seal); no verdict does. `tools/trust_map.py --check`
reports K +0, S +0, trusted +0. This follows the fsf-repair-f9-mcca-1119 and defs-repair-bluedot-grant-1119
precedent. No standing ruling is needed, and no row is reserved for the DRI.
