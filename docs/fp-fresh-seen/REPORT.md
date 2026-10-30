# fp-fresh-seen (2026-10-30): the fresh draw rebuilds the saved pools

Status: built on base f58ef91bb, HEAD is the commit of this report; 13 new tests and the 9 fp-fulltext tests pass. Installed in manage-agents tools-local (not a git repository); this branch carries only this report.
What changed: `fidelity-pilot-units-fresh.py` now marks only the units drawn as seen, so `apol` rebuilds both saved pools (38 and 18 ids) and exits 0.
Open for fp-apol: the complement is 40 units (33 assent + 7 flow), not 10. The ruling's "5+5" and "flow 13 left" do not match what this script returns; see "Open item". No script change was made for it.
No signature is needed: no VE product code, no DELTA row, no Ruling cell.

Order: reviews/dri-decisions-20261030-fp-fulltext.md item 3; task prompts/task-fp-fresh-seen.txt; backlog fp-fresh-seen.

## Changes

- tools-local/fidelity-pilot-units-fresh.py (backup .bak-20261030-fpfresh; .new, `python3 -I -m py_compile`, mv). No pilot was running it: the `systemctl --user list-units --type=scope | grep fp-` scopes were this item and a fp-fulltext review, and `pgrep -af 'fidelity-pilot|pc-fid-rev'` printed nothing.
  - First pass: rebuilds each stratum's pool excluding only the keys of units drawn in earlier strata, the rule of `draw` in fidelity-pilot-units.py (`taken.update(p["key"] for p in got)`). The `ids != sv["pool_ids"]` check is unchanged, exit 3.
  - Second pass: the complement. A unit drawn in ANY stratum is out; a unit left in two complements stays in the first and is dropped from the later one, recorded in draw.json as the new per-stratum field `repeated`. The `len(set(ids))` assert stays.
- tools-local/test_fidelity_pilot_units_fresh.py (new, 13 tests, `python3 -I <file>`; temp roots only).

## Beyond the task's text

Three small additions; none changes a unit on any saved draw.

1. **The complement also drops units drawn in a LATER stratum.** The first pass cannot see those, so the complement runs after it. The task requires "no id from units.tsv", and a unit in pool 1 drawn from pool 2 would otherwise come back. It does not happen in the 5 saved draws (probe of draw.json: no later-drawn id is in an earlier pool), so it is covered by a fake (test_unit_drawn_in_a_later_stratum_stays_out_of_the_earlier_complement).
2. **A saved drawn id outside its pool exits 3.** Otherwise it would map to no key and silently stay unseen (test_drawn_id_outside_the_pool_exits_3).
3. **stdout gains `repeated N`** on each stratum line. Nothing parses that output: pc-fid-rev.sh only saves it to draw.out.

## Evidence

`python3 -I tools-local/test_fidelity_pilot_units_fresh.py`: `Ran 13 tests ... OK`. `python3 -I tools-local/test_fidelity_pilot_units.py`: `Ran 9 tests ... OK`.

| Claim | Test |
|---|---|
| apol rebuilds pool_ids of both strata, 38 and 18; 40 units, none repeated, none from the seen units.tsv; the seen directory's hashes unchanged | test_apol_rebuilds_both_saved_pools_and_returns_no_seen_unit |
| The 6 ids in both strata (u0049.s03, u0050.s04, u0052.s03, u0052.s04, u0124.s04, uap.speech_2) stay in assent and are recorded in flow's `repeated` | test_apol_overlap_stays_in_assent_and_is_recorded_on_flow |
| The whole-pool update, put back, exits 3 on apol-flow (a seed inside the suite; the test first asserts the line it replaces exists) | test_whole_pool_update_is_refused |
| A missing id, extra id, other order or other label in the saved pool exits 3 and writes nothing | test_saved_pool_with_any_difference_exits_3 |
| A units.tsv with other bytes: exit 4, bytes kept, no .new, no draw.json | test_never_overwrites_a_units_tsv |
| Opposite direction: a rerun with the same bytes exits 0 and changes nothing | test_rerun_with_the_same_bytes_passes_and_changes_nothing |
| Opposite direction: disjoint strata drop nothing | test_disjoint_strata_drop_nothing |
| Existing fresh draw: profile-composition units.tsv byte-identical; draw.json equal but for `repeated` | test_profile_composition_units_do_not_change |
| action-assurance (13), commands-imperatives (14), commitments (273) rebuild their saved pools | test_other_paths_rebuild_their_saved_pools |
| A count other than 40 exits 3 and writes nothing, 10 included | test_wrong_count_exits_3_and_writes_nothing |

## Seeded bugs

Each was planted in a temp copy and run with the one test below; each run failed. The live file was never seeded.

| # | file | seed | failing test |
|---|---|---|---|
| S1 | tools-local/fidelity-pilot-units-fresh.py | whole-pool `seen_keys.update` back | test_apol_rebuilds_both_saved_pools_and_returns_no_seen_unit |
| S2 | tools-local/fidelity-pilot-units-fresh.py | no drop from a later complement | test_unit_in_two_complements_stays_in_the_first |
| S3 | tools-local/fidelity-pilot-units-fresh.py | complement minus its own stratum's draw only | test_unit_drawn_in_a_later_stratum_stays_out_of_the_earlier_complement |
| S4 | tools-local/fidelity-pilot-units-fresh.py | pool check ignores order | test_saved_pool_with_any_difference_exits_3 |
| S5 | tools-local/fidelity-pilot-units-fresh.py | overwrite guard off | test_never_overwrites_a_units_tsv |
| S6 | tools-local/fidelity-pilot-units-fresh.py | `repeated` not recorded | test_apol_overlap_stays_in_assent_and_is_recorded_on_flow |
| S7 | tools-local/fidelity-pilot-units-fresh.py | drawn-in-pool check off | test_drawn_id_outside_the_pool_exits_3 |

## Open item

For fp-apol's preparer; the task did not ask to settle this, so nothing was decided here.

- reviews/dri-decisions-20261030-fp-apol.md item 4 says "assent 33 left, flow 13 left), 5+5". After this task's item 2 flow has 7, not 13: its other 6 are in assent's complement.
- The script returns the whole complement, no random draw, and exits 3 unless the count is exact. So `apol ... 10` exits 3, and `apol ... 40` writes 40 units. A 5+5 pilot needs a sampling rule (seed, order) this script does not have; profile-composition did not, because its complement was exactly 10.
- Same-sentence ledger rows in one stratum are outside the task's rule and stay: commitments' OpenAI stratum has upf.C.04/.08/.13 and upf.C.06/.14 on shared keys. No commitments fresh draw exists; the complement is 273.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed: N.A., no relayed answer.
2. Deliverables: PASS, task items 1-3 and the install rule, tests in the table above; no later-work item.
3. Tests can fail: PASS, S1-S7; test_whole_pool_update_is_refused.
4. Python/Lean/Rust agree: N.A., one Python tool; old and new output compared by test_profile_composition_units_do_not_change.
5. R8 binding: PASS for the tool's own input: test_drawn_id_outside_the_pool_exits_3, test_saved_pool_with_any_difference_exits_3.
6. Gate evidence: N.A. for the builder, the chain gates the final HEAD.
7. Nothing unsigned: PASS, no DELTA row; the branch diff is this report only (`git diff --stat main...HEAD`).
8. User-visible change: PASS, draw.json `repeated` and the stdout field, both listed here; test_profile_composition_units_do_not_change.
9. Test selection: PASS, `tools/select_tests.py --base $(git merge-base HEAD main)` printed `8/500 test units`, changed: docs/fp-fresh-seen/REPORT.md (not every unit; the fresh-draw tests live outside this repository, so the selection cannot reach them, and they are run directly as above). `mac-pytest.sh --select` on efa1ba611: `ran on ve-mac-1 ... 2006s; exit=0; failed/error ids=0`.
10. Lean statements: N.A., no Lean.
11. Budgets: N.A., no budget or deadline.
12. CPU: N.A., no VE path; the suite's 13 tests take about 7 s.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS, test_rerun_with_the_same_bytes_passes_and_changes_nothing, test_disjoint_strata_drop_nothing; task and decision re-read before finishing.
