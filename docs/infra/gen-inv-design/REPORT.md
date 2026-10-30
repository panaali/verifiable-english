# gen-inv-design: report

**Summary.** The design is done: [DESIGN.md](DESIGN.md), with review findings F1-F8 fixed (gen-inv-design-c: F3-F8).
It recommends (a), train-only writing, for the Lean inventories, the audit manifests, the axiom record, the checker
pins and the assurance doc, and per-item or per-directory files for the signed trust and decoder ledgers. gi-1 has
merged; gi-2a reads this design next. No product or script changes, no DELTA rows, trust +0, no reserved signature.
The corrected estimate saves about 8 h of VM time per 8 days, not about 17 h; the prep lock is a new limit (section 8).

## Delivered

- Section 1 sorts the files into derived (D1-D4) and signed ledgers (L1-L3).
- Section 2 has the measured costs: `merge-train.log` from line 20000 (Oct 20 to Oct 28), `.git/ve-regen-log.jsonl`
  (per-entry timings), and `git log --full-history` on `9f81d1c1..c8b1f4f3`.
- Sections 4 and 5 cover designs (a) and (b): what the builder, gate.py, review-ready.py, the merge train (branchregen,
  specregen, mkcand), x86 essentials and the Mac leg each do; how R16, trust_map and DELTA counts are produced; what
  L82 becomes; and the risks.
- Sections 6-9 give the comparison, the migration steps, the sized items gi-1 to gi-4, and why no check gets weaker.

## Review fixes (gen-inv-design-review.final.md)

- **F1 (B)**: gi-1 named the `VE.Audit` import only. The `ResponseShape.*` glob of `lean/lakefile.toml` still builds
  `ResponseShape.Audit`, and `lean_statements.dump_all` builds every tree module by name. DESIGN.md section 4, step 4
  now closes all four routes (import, glob, the dump's build, `trust_map.scan_tree`'s hash). `RUN_ONLY` entries are
  derived from `audit.MANIFESTS`, so a route that comes back fails an existing test. Sections 5-8 and the summary
  follow. gi-1 is now about 150 lines.
- **F2 (B)**: the prep ran only on the probe or an unpinned `ve_service`, so a Rust-only change was never pinned. The
  prep now builds both checkers on every candidate, and its condition is the train entries' own `--check`. gi-2b
  checks `rust-pins` after the Rust build, splits `checker-pins` (`VE_REGEN_NO_RUST` goes) and gives the four pin
  readers it named (`lean_service`, `rust_jsonl`, `rust_build`, x86 essentials) one reader with a guard test; there
  are eleven (F8 below). The Rust build's
  cost is measured: 76 of 81 regen-log writes under 1.2 s, 5 at 28-69 s.
- Regression tests: `tests/test_gen_inv_design.py` reads its expectations from the code, not from the review's
  examples. `test_gi1_names_every_default_build_route_of_every_manifest` takes the lakefile globs and the importers
  of each `audit.MANIFESTS` module. `test_the_candidate_prep_writes_every_pin_key` takes every key of
  `lean/checkers.lock`. Both failed on ccb29b9a's DESIGN.md (the glob route; `rust_jsonl`) and pass now. Both PROBE
  lines failed before (exit 1) and pass after.
- The C findings F3-F8 are fixed below (gen-inv-design-c).
- Backlog rows to update (the DRI signed before the review): **gi-1** scope "both manifests out of every build (DESIGN
  section 4 step 4: import, `ResponseShape.*` glob, dump build; `RUN_ONLY` from `audit.MANIFESTS`)", size ~150;
  **gi-2b** "one pin reader with local pins for every `lean/checkers.lock` reader in DESIGN section 8, plus a guard
  test; `checker-pins` split into `service-pins` and `rust-pins`; `rust-pins` checked after the Rust build", size ~550
  (F8); **gi-3** "the prep
  builds both checkers on every candidate, with the train entries' `--check` as its condition; harness test: a
  Rust-only candidate (probe 0, `ve_service` pinned) gets its Rust pin", size ~270 plus ~170 harness.

## C fixes (gen-inv-design-c)

Findings: `gen-inv-design-review.final.md` F3-F7, `gen-inv-design-loop.final.md` F8. Nothing the DRI signed changes.

- **F3** (section 8, with the risks in section 4 and the row in section 6): the estimate now counts the prep's
  `lake build` and its single locked `ve-cand-regen` worktree: about 13 min at the median, about 18 min at p90, about
  14 h per 8 days against today's 21.8 h, so about 8 h saved, not all of it, and a ceiling of about 3-4 Lean candidates
  per hour. **Estimated** until gi-3 measures it (DRI decision (b)). The prep must wait for the lock, because
  `candregen`'s `flock -w 600` skip is shorter than one prep. The FAIL and builder-commit savings are unchanged.
- **F4** (section 2): `lake-build` max 1,251 s (ve-qt-a3c, 08:04Z Oct 28). The old 1,013 s left out the `bootstrap`
  phase. The medians are split: train 573 s, builders 0.9 s, the rows and the join rule are in the table.
- **F5** (section 4, step 2): the accessor never falls back to the committed copy; a missing or stale overlay is an
  error (DRI condition 1(b)). Section 7, step 2 follows: until gi-2b's flip every run asks for the committed copy.
- **F6** (section 9, with a pointer in section 3): the x86 build-time check of `VE/Audit.lean` that gi-1 removes, and
  DRI decision (b) item 3, which covers it; gi-1 delivered the audit in that leg.
- **F7** (section 7): the migration steps of design (b), marked not adopted. The pilot-bytes row is below.
- **F8** (sections 4, 7 and 8): every `lean/checkers.lock` reader is in gi-2b's scope, F8's five
  (`regen_generated`, `lean_output_diff`, `lean_first_cache`, `gate_collection`, `lean_share`) plus two found while
  listing them (`answer_cutoff`, `research/defeasible/baseline.py`). gi-2b goes from ~450 to ~550, and design (a)'s total
  from about 1,320 to about 1,420 lines.
- Regression tests in `tests/test_gen_inv_design.py`: `test_gi2b_names_every_pin_reader` takes the readers from the
  code, `test_the_accessor_never_falls_back_to_the_committed_copy` and
  `test_the_cost_estimate_counts_the_prep_build_and_its_lock` hold F5 and F3.

Seeded bugs (each planted, shown failing, restored; design and test files only, no product code):

| Seeded bug | File | Test that fails |
|---|---|---|
| `lean_share` dropped from gi-2b's row | `docs/infra/gen-inv-design/DESIGN.md` | `test_gi2b_names_every_pin_reader` |
| a new file that names the lock, `tools/seeded_pin_reader.py` | `tools/seeded_pin_reader.py` (removed) | `test_gi2b_names_every_pin_reader` |
| the accessor's "and the committed copy otherwise" restored | `docs/infra/gen-inv-design/DESIGN.md` | `test_the_accessor_never_falls_back_to_the_committed_copy` |
| "about 4-6 min per Lean candidate" restored, the build and the lock dropped | `docs/infra/gen-inv-design/DESIGN.md` | `test_the_cost_estimate_counts_the_prep_build_and_its_lock` |

All three new tests also fail on the pre-fix DESIGN.md (main at this branch's base).

| Row | Value |
|---|---|
| Pilot bytes | N.A.: design only, no pilot output moves (0 bytes) |
| Trust | +0 |
| DELTA | none |

## Not applicable (design only)

The statement gate, the trust re-measure and mutants do not apply: no Lean, Python or Rust product file is changed.
The only code is the regression tests above. The overlap check was done: no branch in flight touches
`docs/infra/gen-inv-design/`.

## Next item

None from this item. gi-2a reads the fixed design.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay change)
2. Every required deliverable built, no rule broken: PASS (F3-F8 each cite their finding id in DESIGN.md and above; no script or product file changed)
3. Tests and gates can fail: PASS (`test_gi2b_names_every_pin_reader`, `test_the_accessor_never_falls_back_to_the_committed_copy` and `test_the_cost_estimate_counts_the_prep_build_and_its_lock` fail on the seeded bugs above; no product code)
4. Python, Lean and Rust agree: N.A.
5. R8 binding: N.A.
6. Gate evidence matches the final HEAD: PASS (the chain gates the final HEAD)
7. No unsigned item left: PASS (no DELTA rows, no reserved signature)
8. Every user-visible change in DELTA: N.A. (no user-visible change)
9. Test selection still finds the tests: PASS (checked with select_tests on the final HEAD)
10. Lean statements and proofs: N.A.
11. Budgets, limits and deadlines fail closed: N.A.
12. No CPU or memory regression: N.A.
13. Test-removed trailers: N.A. (no test removed)
