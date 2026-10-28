# gen-inv-design: report

**Summary.** The design is done: [DESIGN.md](DESIGN.md). It recommends (a), train-only writing, for the Lean
inventories, the audit manifests, the axiom record, the checker pins and the assurance doc. For the signed trust and
decoder ledgers it recommends per-item or per-directory files. The first implementation item is gi-1 (both audit
manifests out of every build, about 150 lines). No product or script changes, no DELTA rows, trust +0, no reserved
signature.

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
  readers (`lean_service`, `rust_jsonl`, `rust_build`, x86 essentials) one reader with a guard test. The Rust build's
  cost is measured: 76 of 81 regen-log writes under 1.2 s, 5 at 28-69 s.
- Regression tests: `tests/test_gen_inv_design.py` reads its expectations from the code, not from the review's
  examples. `test_gi1_names_every_default_build_route_of_every_manifest` takes the lakefile globs and the importers
  of each `audit.MANIFESTS` module. `test_the_candidate_prep_writes_every_pin_key` takes every key of
  `lean/checkers.lock`. Both failed on ccb29b9a's DESIGN.md (the glob route; `rust_jsonl`) and pass now. Both PROBE
  lines failed before (exit 1) and pass after.
- The C findings F3-F7 are left to the follow-up gen-inv-design-c.
- Backlog rows to update (the DRI signed before the review): **gi-1** scope "both manifests out of every build (DESIGN
  section 4 step 4: import, `ResponseShape.*` glob, dump build; `RUN_ONLY` from `audit.MANIFESTS`)", size ~150;
  **gi-2b** "one pin reader with local pins for `lean_service` and `rust_jsonl` plus a guard test; `checker-pins`
  split into `service-pins` and `rust-pins`; `rust-pins` checked after the Rust build", size ~450; **gi-3** "the prep
  builds both checkers on every candidate, with the train entries' `--check` as its condition; harness test: a
  Rust-only candidate (probe 0, `ve_service` pinned) gets its Rust pin", size ~270 plus ~170 harness.

## Not applicable (design only)

The statement gate, seeded bugs, the trust re-measure and mutants do not apply: no Lean, Python or Rust product
file is changed. The only code is the regression test above, and its seeded bug is the pre-fix DESIGN.md (both tests
fail on it). The overlap check was done: no branch in flight touches `docs/infra/gen-inv-design/`.

## Next item

gi-1: take `VE.Audit` out of the default Lean build, and measure `lake build` before and after. It is queued by the
DRI after reading the design.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay change)
2. Every required deliverable built, no rule broken: PASS (DESIGN.md has every section the task names; no script or product file changed)
3. Tests and gates can fail: PASS (both regression tests fail on the pre-fix DESIGN.md; no product code)
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
