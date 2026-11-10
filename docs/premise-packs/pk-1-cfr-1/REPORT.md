# pk-1-cfr-1: pk-1's route-case differential is INVALID (REPORT)

Summary: READY FOR REVIEW. pk-1's REPORT (section 2, self-review item 4) and DELTA say the 33 route cases' differential
is INVALID (exit 1) and cite `evidence/ab_full.txt` (exit 0) only for what it covers; the evidence files are unchanged
and nothing was re-run. `tests/test_pk1_route_case_evidence_validity.py` fails on main, passes here. Docs and test only;
trust +0; pilot bytes 0; no DELTA row; no DRI signature reserved. Next item: none; two FOLLOW-UPs below. Source: DRI
2026-11-10 (dri-decisions-20261110-lp0001.md Q2; regrade #6). Plan: the code on main; base de7fb9469.

**Deliverables (AGENT).** (1) Wording: pk-1 REPORT.md :62-65 and :184-187, DELTA.md :17-19; `git diff de7fb9469 --
docs/premise-packs/pk-1/evidence` is empty. (2) `test_pk1_route_case_evidence_validity`. A claim is the list item,
paragraph or table row claiming zero differences, wrapped lines included. Each cited evidence file (`evidence/x` or
`docs/premise-packs/<p>/evidence/x`) must exist with no "INVALID" first line; each cited differential record must end
"exit 0"; one such passing record must be cited. `test_scan_refuses_and_accepts` covers both directions on `tmp_path`
files. (3) Other reports flagged: pk-1b's DELTA.md :14 and REPORT.md :37 and :156 cite `pk-1b/evidence/ab_full.txt`,
which has no exit line. Not a wording fix, so `FOLLOW_UPS` exempts that one path, and
`test_follow_up_exemptions_are_still_needed` fails once it is fixed.

**Fails on main.** pk-1's main docs with this test: `1 failed, 2 passed`, `Left contains 3 more items` (pk-1 REPORT.md
:62, :183 and DELTA.md :17, each "cites evidence/ab_route_cases.txt, whose first line says INVALID"). HEAD: `3 passed`.

**Seeded bugs** (each planted, run with `uv run pytest -q --noconftest tests/test_pk1_route_case_evidence_validity.py`,
seen to fail, restored). "main", "scan" and "exempt" are the three tests.
S1 pk-1/REPORT.md, main's wording restored: main fails (`Left contains 2 more items`).
S2 pk-1/DELTA.md, main's wording restored: main fails (`Left contains one more item`).
S3 pk-1/REPORT.md, item 4 points at `evidence/ab_route_cases.txt` again: main fails ("whose first line says INVALID").
S4 test file, "exit 0" check made `False`: scan fails (`assert (0 == 1)`) and exempt fails.
S5 test file, INVALID check made `False`: scan fails. S6 test file, `\s+` back to a space: scan fails (wrapped case).
S7 test file, pack-prefix citations dropped: scan fails. S8 test file, pk-1's `ab_full.txt` exempted: exempt fails.
S1 and S3 are the two the task names. No Lean, Python product or Rust file changed.

**Checks.** `trust_map.py --check`: `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`, PASS. The light lane
holds: no lean/ or generated file, at most 150 changed lines, so no trust_mutants sweep. No input of a generated file
changed, so no regen. `regen_generated.py --check` reported `failed: route-cases, checker-pins`; both start the Lean
service or read the built binaries, and neither reads a file this diff changes. No in-flight branch touches these files.

FOLLOW-UP: pk-1b-cfr-1 record the exit status of pk-1b's `evidence/ab_full.txt` differential and drop its exemption.
FOLLOW-UP: pk-1-cfr-1b a valid differential of the 33 norm-defaults route cases (one that runs the rebuilt executables).

**Self-review against BUILDER-CHECKLIST.** 1, 5, 10, 11, 12 N.A. (no relayed answer, Lean, budget or runtime code).
2 PASS: the deliverables above. 3 PASS: S1-S8. 4 N.A. (no product code). 6 PASS: the chain gates the final HEAD.
7 PASS: no DELTA row. 8 PASS: no user-visible change (DELTA.md). 9 PASS: select_tests picks the test for a pack REPORT
change. 13 N.A. (no test removed). 14 PASS: both directions in `test_scan_refuses_and_accepts`. 15 PASS.
SELF-REVIEW: 2 A, 4 B, 4 C; fixed 10.
Selected tests (committed 82a855b2e, `mac-pytest.sh --select`, cloud run pk-1-cfr-1-82a855b2-t277231): 4 shards, 185 units passed, exit=0.
