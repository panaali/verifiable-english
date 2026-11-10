# pk-1-cfr-1: pk-1's route-case differential is INVALID, not "0 differences" (REPORT)

Summary: READY FOR REVIEW. pk-1's REPORT (section 2 and self-review item 4) and DELTA no longer cite the 33 route
cases as "0 differences": the run in `evidence/ab_route_cases.txt` is INVALID (exit 1). `evidence/ab_full.txt`
(exit 0) is cited only for what it covers. `tests/test_pk1_route_case_evidence_validity.py` fails on main and passes
here. Docs and test only; trust +0; pilot bytes 0. No DELTA row, no DRI signature reserved. Next item: none.

Source: DRI 2026-11-10, reviews/dri-decisions-20261110-lp0001.md Q2 (applying dri-decisions-20261109-lp1801.md item
1; regrade #6 in reviews/l1-c-regrade-norm-defaults-b-20261109.md). The plan is the code on main; base de7fb9469
(`git merge-base HEAD main`). No plan section or statement gate.

## Deliverables (all AGENT)

| # | Row (task) | Delivered by |
|---|---|---|
| 1 | REPORT and DELTA rows say the route-case differential is INVALID (exit 1); `evidence/ab_full.txt` (exit 0) is cited only for what it covers; the old evidence file stays unchanged; no re-run | `docs/premise-packs/pk-1/REPORT.md` :62-65 and :184-186, `docs/premise-packs/pk-1/DELTA.md` :17-19. `git diff main -- docs/premise-packs/pk-1/evidence` is empty |
| 2 | `test_pk1_route_case_evidence_validity`: each "0 differences" claim in a `docs/premise-packs/*/REPORT.md` or `DELTA.md` cites an evidence file whose last line is "exit 0" and whose first line has no "INVALID"; fails on main | `tests/test_pk1_route_case_evidence_validity.py` |
| 3 | List the other reports the scan flags | pk-1b only (below): FOLLOW-UP, not a wording fix |

**The scan.** A claim is the markdown list item, paragraph or table row holding "0 differences" (not "10
differences"). Every evidence file it cites must exist and have no "INVALID" on its first line. Every cited
differential record (a file that mentions "differences") must end "exit 0". The claim must cite at least one such
passing record. A cited file that is not a differential record (`ab_recorded_kinds.txt`) is allowed beside it.
`test_scan_refuses_and_accepts` checks both directions on files in `tmp_path`: accepted (a passing record, a
passing record plus a kinds file, "10 differences") and refused (an INVALID first line, "exit 1", only a kinds
file, a citation in the next list item, a missing file).

**Fails on main.** At 47b95cc86 (the test only, main's docs) `uv run pytest -q --noconftest
tests/test_pk1_route_case_evidence_validity.py` gave `1 failed, 2 passed`:
`assert ['pk-1/REPORT...says INVALID'] == []`, three faults, one for each of pk-1 REPORT.md :62 and :183 and
DELTA.md :17, each "cites evidence/ab_route_cases.txt, whose first line says INVALID". At HEAD: `3 passed`.

**Other reports the scan flags.** pk-1b's DELTA.md :14 and REPORT.md :156 cite `pk-1b/evidence/ab_full.txt`
(0 differences). That record has no exit line: it ends "445 invocations, … 0 differences, 0 timed out". Wording
cannot fix this: the record needs the run's exit status, and this item does not re-run anything. The test exempts
that one exact path (`FOLLOW_UPS`). `test_follow_up_exemptions_are_still_needed` fails once the record is fixed,
so the exemption then has to be removed.

FOLLOW-UP: pk-1b-cfr-1 record the exit status of pk-1b's `evidence/ab_full.txt` differential (re-run if needed) and remove its exemption from `tests/test_pk1_route_case_evidence_validity.py`.

A valid re-run of the 33 route cases (one that invokes the rebuilt `ve_speech_acts_route`) is out of scope.
The differential is not needed for pk-1's verdict, because `evidence/ab_full.txt` already ran
`ve_speech_acts_route` 17 times with 0 differences. I name no follow-up for it; the DRI may file one.

## Seeded bugs

The product files of this item are docs only. Each bug was planted, run with `uv run pytest -q --noconftest
tests/test_pk1_route_case_evidence_validity.py`, seen to fail and restored (`3 passed` afterwards). Abbreviations:
"main" = `test_pk1_route_case_evidence_validity`, "scan" = `test_scan_refuses_and_accepts`, "exempt" =
`test_follow_up_exemptions_are_still_needed`.

| # | File | Bug | Fails |
|---|---|---|---|
| S1 | docs/premise-packs/pk-1/REPORT.md | main's REPORT wording restored | main: `Left contains 2 more items … cites evidence/ab_route_cases.txt, whose first line says INVALID` |
| S2 | docs/premise-packs/pk-1/DELTA.md | main's DELTA wording restored | main: `Left contains one more item: "pk-1/DELTA.md: …"` |
| S3 | docs/premise-packs/pk-1/REPORT.md | item 4's claim points at `evidence/ab_route_cases.txt` again | main: `"pk-1/REPORT.md: '4. **Python, Lean and Rust agree …' cites evidence/ab_route_cases.txt, whose first line says INVALID"` |
| S4 | tests/test_pk1_route_case_evidence_validity.py | "exit 0" check replaced by `if False:` | scan (`assert (0 == 1)`) and exempt (`assert [] != []`) |
| S5 | tests/test_pk1_route_case_evidence_validity.py | INVALID first-line check replaced by `elif False:` | scan (`assert (1 == 1 and False)`) |
| S6 | tests/test_pk1_route_case_evidence_validity.py | the exemption widened with `pk-1/evidence/ab_full.txt` | exempt (`assert [] != []`) |

S1 and S3 are the two the task names. No Lean, Python product or Rust file changed.

## Checks

- Size: `python3 -I …/tools-local/light-lane.py check` printed `LIGHT 114 changed lines outside generated files <=
  150 (3 files), no trusted-core file, against de7fb946`, so no trust_mutants sweep (the task asks for no record).
- Trust: `uv run python tools/trust_map.py --check` printed `against de7fb9469064: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0` and `PASS`.
- Generated files: no input of a generated file changed (`git diff --name-only main`: the three files above plus this
  directory), so no regen. `uv run python tools/regen_generated.py --check` reported `failed: route-cases,
  checker-pins`. Both checks start the Lean service or read the built binaries. Neither reads a file this diff
  changes: they fail on this worktree's local build and are not caused by this item.
- Overlap: no in-flight `feature/*`, `lean-first/*`, `infra/*` or `foundation/*` branch touches these files.
