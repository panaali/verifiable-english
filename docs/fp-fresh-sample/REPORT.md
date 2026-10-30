# fp-fresh-sample (2026-10-30): a seeded sample mode for the fresh draw

Status: built on base 70da2be4d. The 21 tests in the fresh test file (8 new) and the 9 fp-fulltext tests pass. The change is installed in manage-agents tools-local, which is not a git repository; this branch carries only this report and `mutants.json`.
What changed: `fidelity-pilot-units-fresh.py <path> <seen> <out> <count> --sample <k> --seed <n>` takes a seeded draw with the original draw's rule in place of the exhaustive complement. Without the two flags, every byte written and printed is the same as before.
Not done, by order: the fp-apol draw itself. It was not run into any pilot directory, and no test pins its ids, because that draw runs after both revised apol plans are frozen. The tests compute it only in temp roots, and its ids were not printed.
No signature is needed: no VE product code changed, and there is no DELTA row and no Ruling cell.
Bookkeeping (review F5 of fp-fresh-seen): the fp-fresh-seen backlog row reads `status: merged` (`status_by: seed`, updated 2026-10-30T09:54Z), not `done`. That is the state after done, so the review's F5 concern (it read `in-flight`) no longer applies. Reported as asked.

Order: reviews/dri-decisions-20261030-fp-apol-draw.md item 1; task prompts/task-fp-fresh-sample.txt; backlog fp-fresh-sample; folds in fp-fresh-seen-review-ov.final.md F1-F3.

## Changes

- tools-local/fidelity-pilot-units-fresh.py (backup `.bak-20261030-fpsample`, sha256 e039104ce3cff809…; written as `.new`, checked with `python3 -I -m py_compile`, then mv). No pilot was running it: `systemctl --user list-units --type=scope | grep fp-` showed only this item and `ve-rvab-fp-fulltext` (review-ab-shadow, a review), and `grep -c fidelity-pilot` on the scopes gave 0.
  - `--sample k --seed n`, only as the last four arguments in that order (anything else prints the usage and exits 1). It runs after the unchanged pool checks, which exit 3 on any difference. Strata go in saved order. Each stratum's candidates are its rebuilt pool minus the keys drawn in any stratum of the seen draw. That list goes to fidelity-pilot-units.py's own `draw(rng, cand, k, taken)`, which drops the keys taken earlier in this draw and calls `rng.sample`, with one `random.Random(seed)` and one `taken` for the whole draw.
  - draw.json in this mode: `rule`, `seed`, and per stratum `pool`, `pool_ids`, `excluded`, `candidates` (size), `candidate_ids`, `drawn`. There is no `repeated`. The same `<count>` check exits 3, with the message "sample has N units", and the same fixed-once-written rule exits 4.
  - Complement mode: the same code path and the same strings. The `excluded` expression was hoisted into a local variable shared by both modes.
  - F3: the docstring now says that `excluded` is every pool id whose key was drawn in any stratum of the seen draw, not only that stratum's drawn ids.
- tools-local/test_fidelity_pilot_units_fresh.py (backup `.bak-20261030-fpsample`; 13 → 21 tests, `python3 -I <file>`, temp roots only). `unit()` now gives every fake unit key `k:<id>`, so key ≠ id, and a pool entry `(id, key)` gives a second id the same key (F1). `fake()` computes the saved pool_ids by key, as `draw` does, and takes extra arguments and another script.

## Evidence

`python3 -I tools-local/test_fidelity_pilot_units_fresh.py`: `Ran 21 tests in 6.982s / OK`. `python3 -I tools-local/test_fidelity_pilot_units.py`: `Ran 9 tests in 0.739s / OK`. Both were run on the installed files after the mv. Before the mv, the same 21 passed on the `.new` copy with `FIDELITY_PILOT_UNITS_FRESH_PY`.

| Claim | Test |
|---|---|
| apol, seed 20261030, 5+5: two runs into two roots give byte-identical units.tsv and draw.json; a rerun into the same root exits 0; seed and rule recorded; no `repeated`; the pool_ids match the saved ones; assent has 33 candidates (pool minus excluded); flow has 8-13 candidates, exactly its pool minus excluded minus assent's drawn ids; each drawn id is among its candidates; 10 distinct ids, none from reviews/fidelity-pilot-20261029/apol/units.tsv; the seen directory's hashes are unchanged | test_apol_sample_is_deterministic |
| Fake strata share u2, u3, u4 and a key (u3b = u3 under another id). Over 30 seeds, b's candidates are its unseen units minus every key a took, and no key is drawn twice | test_sample_never_repeats_across_strata |
| Seeded bug kept in the suite: `taken` replaced by `set()`; b gets 7 candidates instead of 4-5 (the test first asserts the line it replaces exists) | test_dropping_taken_repeats_a_unit |
| Complement mode: profile-composition 10, apol 40 and apol 10 give the same return code, stdout, stderr, units.tsv and draw.json bytes as the pre-item backup | test_complement_mode_writes_the_same_bytes_as_before |
| Existing pc fresh units.tsv byte-identical to reviews/fidelity-pilot-20261030 (unchanged test) | test_profile_composition_units_do_not_change |
| Sample mode keeps the checks: an extra pool id exits 3; a count of 9 or 11 exits 3 and writes nothing; another seed into a written root exits 4 and keeps both files; opposite direction: count 10 exits 0 | test_sample_keeps_the_pool_count_and_overwrite_checks |
| Refuses `--sample` alone, the flags in the other order, k = 0 and a trailing argument (exit 1, usage, nothing written) | test_sample_needs_both_flags_in_order |
| F1: key ≠ id; a later-drawn key under another id (u3a) is excluded from the earlier stratum; an earlier-kept key under another id (u2b) is `repeated` in the later one | test_a_key_shared_by_two_ids_is_one_unit |
| F2: an earlier-drawn unit (u1, and u1b with u1's key) in a later raw pool is left out of the later pool_ids, in both modes | test_unit_drawn_earlier_is_left_out_of_a_later_raw_pool |

## Seeded bugs

All in Python, the only language changed. File: /home/seyran/code/manage-agents/tools-local/fidelity-pilot-units-fresh.py. Each mutant was written to a scratch copy under /tmp/fpsample-mut and run with `FIDELITY_PILOT_UNITS_FRESH_PY=<copy> python3 -I tools-local/test_fidelity_pilot_units_fresh.py Fresh.<test>`. The installed file was never edited; its sha256 is a5765b0a92952cc4… before and after. Details are in `docs/fp-fresh-sample/mutants.json`.

| Bug | Test that fails | Result |
|---|---|---|
| `draw(rng, got, sample, taken)` → `set()` (drops `taken`) | test_sample_never_repeats_across_strata | FAILED (failures=1) |
| `random.Random(seed)` → `random.Random()` | test_apol_sample_is_deterministic | FAILED (failures=1) |
| sample from `pool` instead of the unseen candidates | test_apol_sample_is_deterministic | FAILED (failures=1) |
| complement rule text `(no seed)` → `(no seed, complement)` | test_complement_mode_writes_the_same_bytes_as_before | FAILED (failures=1) |
| F1: complement filters `p["id"] not in seen_keys` | test_a_key_shared_by_two_ids_is_one_unit | FAILED (errors=1) |
| F1: repeated drop filters `p["id"] not in kept` | test_a_key_shared_by_two_ids_is_one_unit | FAILED (errors=1) |
| F1: `excluded` uses `p["id"] in seen_keys` | test_a_key_shared_by_two_ids_is_one_unit | FAILED (failures=1) |
| F2: line 45's seen-key filter removed | test_unit_drawn_earlier_is_left_out_of_a_later_raw_pool | FAILED (errors=1) |

"errors" means the mutant's main exited 3 (count or pool mismatch) inside the in-process fake.

## Spec re-read

- "after the existing checks that rebuild each stratum's saved pool_ids (exit 3 on any difference)": checked against prompts/task-fp-fresh-sample.txt item 1. The sample branch runs after the unchanged rebuild loop.
- "candidate pool = the rebuilt pool minus the keys drawn in ANY stratum of the seen draw, minus the keys taken earlier in this draw": checked against the same item. `seen_keys` is complete after the loop, and `taken` is filtered inside `draw`.
- "with fidelity-pilot-units.py's own `draw` and ONE random.Random(seed)": checked against the same item and against fidelity-pilot-units.py:83-87. `fp.draw` is called, and the rng is created once before the loop.
- "draw.json records rule, seed, and per stratum the candidates' size and ids; no `repeated` list": checked against the same item.
- "strata in their saved order … flow is sampled from 8 to 13 units": checked against reviews/dri-decisions-20261030-fp-apol-draw.md item 1. Asserted in test_apol_sample_is_deterministic.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no Lean and no relay.
2. Deliverables built, no rule broken: PASS. Task items 1-3 and F1-F3 are listed above. Item 4 holds: no pilot directory was written, and the F5 row check is reported. The .new / py_compile / .bak / mv rule was followed.
3. Tests can fail: PASS, 8 seeded bugs (table above, mutants.json).
4. Python, Lean and Rust agree: N.A., Python tooling only; the sample uses the original script's own `draw`.
5. R8 binding: N.A., no VE binding.
6. Gate evidence matches the final HEAD: PASS. The chain runs the gate on the final HEAD. Selected tests, run once on 11574c728: `mac-pytest.sh --select -- --base 70da2be4d --run` rc 0, "48 units, 48 passed" (GitHub Actions run fp-fresh-sample-11574c72-t362896, 2009 s).
7. No unsigned item: PASS. There is no DELTA row, and the DRI decision item 1 is SIGNED in its decision file.
8. User-visible change in DELTA: N.A., no VE user-visible change.
9. Test selection: N.A., no VE source changed. tools-local tests run by file.
10. Lean statements: N.A.
11. Budgets fail closed: N.A., no budget. Exit codes 3 and 4 are kept in sample mode (test_sample_keeps_the_pool_count_and_overwrite_checks).
12. CPU or memory regression: N.A. The whole file runs in about 7 s, and the sample is one pass over at most 38 units.
13. Removed or renamed tests: PASS. None was removed or renamed; all 13 old tests are kept.
14. Both directions, cited evidence, spec re-read: PASS. The accept and refuse pairs are in test_sample_keeps_the_pool_count_and_overwrite_checks, test_sample_needs_both_flags_in_order and test_rerun_with_the_same_bytes_passes_and_changes_nothing. Every claim cites a test or a command, and the spec re-read is above.

Sibling lessons (fp-fresh-seen review): F1 and F2 are closed by tests and F3 by the docstring. The new `candidates` and `candidate_ids` fields are documented in the docstring and here, so there is no undocumented field.
