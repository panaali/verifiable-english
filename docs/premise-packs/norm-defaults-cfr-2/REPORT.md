# norm-defaults-cfr-2: what the spec says is built with norm-defaults@0 (REPORT)

READY FOR REVIEW. Docs and test only; DRI 2026-11-10 lp0001 Q2 (regrade #4); base de7fb9469; no DELTA row; trust +0
(`uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0"); pilot
bytes 0; no lean/ or generated file touched; next item: none.

**Delivered** (6d8534eb3, 0241a7047, review fixes after). (1) docs/spec/norm-defaults.md 3.3 "Integration status":
alternatives@0 with norm-defaults@0 admitted (`todayGate`, Dispatch.lean:31-71; `runCaseU`, Alternatives/Run.lean:407,
chosen at :422; `admission` and the readers refusing it via `pendingWithDefaults` named); risk@0 refused (Dispatch.lean:39).
"Not built": `ResourceLimit: unsaid atoms` (`rg -F 'ResourceLimit: unsaid atoms' lean ve rust tools`: no
hit; over budget `enumerateSettledX`, Evidence.lean:1069, gives UNKNOWN) and the reader test (4.3, 8, Q6). (2) tests/
test_norm_defaults_documented_support.py reads `todayGate` and `pendingWithDefaults` from Dispatch.lean; `..._refuses`
is the opposite direction. `disagreements(<git show de7fb9469:docs/spec/norm-defaults.md>, Dispatch.lean)` on main's
spec: "names no composed block: Their combination with `norm-defaults@0` is rejected at profile validation ...", "spec:
[] for risk@0 ...; todayGate: refused", "spec: [] for alternatives@0 ...; todayGate: admitted". `select_tests.py --paths
<Dispatch.lean> <spec> --static --explain` selects it for both. Size: light-lane.py check "LIGHT 149 changed lines".

**Seeded bugs** (each planted, `uv run pytest -q tests/test_norm_defaults_documented_support.py` FAILED, restored):
S1 docs/spec/norm-defaults.md, old sentence restored: "names no composed block". S2 same file, risk row "admitted":
"spec: ['admitted'] for risk@0 ...; todayGate: refused". S3 same file, alternatives row "refused": "...todayGate:
admitted". S4 lean/VE/Compose/Dispatch.lean (source text only, test function called directly since conftest rebuilds
Lean): gate refuses alternatives with norm-defaults: "spec: ['admitted'] for alternatives@0 ...; todayGate: refused".
No product code changed in any language. **Spec re-read:** every line the spec cites, against its file.
**Test runs:** `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select` on 9371b1fc5: exit 0, 221 units passed; regen --check: rc 0.
**Self-review against BUILDER-CHECKLIST:** 1 N.A. no relayed answer; 2 PASS both deliverables (test above); 3 PASS
S1-S4; 4 N.A. no product code; 5 N.A. no binding; 6 PASS selected run above; 7 PASS no DRI row; 8 PASS DELTA.md
(no user-visible delta); 9 PASS select_tests line above; 10 N.A. no Lean; 11 N.A. no limit; 12 N.A. no runtime code;
13 N.A. no test removed; 14 PASS `..._refuses`, commands cited, spec re-read; 15 PASS no overclaim (spec "Not built"
list), nothing cut, S1-S4, no limit.
