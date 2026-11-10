# norm-defaults-cfr-2: what the spec says is built with norm-defaults@0 (REPORT)

READY FOR REVIEW. Docs and test only; DRI 2026-11-10 lp0001 Q2 (regrade #4); base de7fb9469; no DELTA row; trust +0
(`uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0"); pilot
bytes 0; no lean/ or generated file touched; next item: none.

**Delivered.** (1) docs/spec/norm-defaults.md 3.3 "Integration status" replaces the 2026-10-01 gap note: alternatives@0
with norm-defaults@0 admitted (`todayGate`, Dispatch.lean:31-71; `runCaseU`, Alternatives/Run.lean:407, chosen at :421;
the readers refusing it via `pendingWithDefaults` named); risk@0 refused (Dispatch.lean:39, its text quoted). "Not
built": `ResourceLimit: unsaid atoms` (`rg -F 'ResourceLimit: unsaid atoms' lean/VE ve` hits only the spec; over
`MAX_UNSAID_ATOMS` the point stays UNKNOWN, Report.lean:178) and the reader test (marked at 4.3, 8 and Q6). (2)
tests/test_norm_defaults_documented_support.py: `test_norm_defaults_documented_support` reads `todayGate` and
`pendingWithDefaults` from Dispatch.lean; `..._refuses` is the opposite direction. On main's spec (commit 6d8534eb3^'s
text) it failed: "a profile-validation claim names no composed block: ['Their combination with `norm-defaults@0` is
rejected at profile validation ...']". `select_tests.py --paths lean/VE/Compose/Dispatch.lean docs/spec/norm-defaults.md
--static --explain` selects it for both files. Size: 120 changed lines + this report (light lane).

**Seeded bugs** (each planted, `uv run pytest -q tests/test_norm_defaults_documented_support.py` FAILED, restored):
S1 docs/spec/norm-defaults.md, old sentence restored: "names no composed block". S2 same file, risk row "admitted":
"spec: ['admitted'] for risk@0 ...; todayGate: refused". S3 same file, alternatives row "refused": "...todayGate:
admitted". S4 lean/VE/Compose/Dispatch.lean (source text only, test function called directly since conftest rebuilds
Lean): gate refuses alternatives with norm-defaults: "spec: ['admitted'] for alternatives@0 ...; todayGate: refused".
No product code changed in any language, so no per-language product seed applies.

**Spec re-read:** each cited line against the file (Dispatch.lean:39, :83; Run.lean:407, :421; Document.lean:1174;
NormDefaults/Run.lean:446; Alternatives/Wire.lean:233; Evidence.lean:786; Report.lean:178).

**Test runs:** PENDING.

**Self-review against BUILDER-CHECKLIST:** 1 N.A. no relayed answer; 2 PASS both deliverables (test above); 3 PASS
S1-S4; 4 N.A. no product code; 5 N.A. no binding; 6 PASS chain gate on final HEAD; 7 PASS no DRI row; 8 PASS DELTA.md
(no user-visible delta); 9 PASS select_tests line above; 10 N.A. no Lean; 11 N.A. no limit; 12 N.A. no runtime code;
13 N.A. no test removed; 14 PASS `..._refuses`, commands cited, spec re-read; 15 PASS no overclaim (spec "Not built"
list), nothing cut, S1-S4, no limit.
