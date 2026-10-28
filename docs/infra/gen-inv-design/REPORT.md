# gen-inv-design: report

**Summary.** The design is done: [DESIGN.md](DESIGN.md). It recommends (a), train-only writing, for the Lean
inventories, the audit manifests, the axiom record, the checker pins and the assurance doc. For the signed trust and
decoder ledgers it recommends per-item or per-directory files. The first implementation item is gi-1 (`VE.Audit` out
of the default Lean build, about 100 lines). No product or script changes, no DELTA rows, trust +0, no reserved
signature.

## Delivered

- Section 1 sorts the files into derived (D1-D4) and signed ledgers (L1-L3).
- Section 2 has the measured costs: `merge-train.log` from line 20000 (Oct 20 to Oct 28), `.git/ve-regen-log.jsonl`
  (per-entry timings), and `git log --full-history` on `9f81d1c1..c8b1f4f3`.
- Sections 4 and 5 cover designs (a) and (b): what the builder, gate.py, review-ready.py, the merge train (branchregen,
  specregen, mkcand), x86 essentials and the Mac leg each do; how R16, trust_map and DELTA counts are produced; what
  L82 becomes; and the risks.
- Sections 6-9 give the comparison, the migration steps, the sized items gi-1 to gi-4, and why no check gets weaker.

## Not applicable (design only)

The statement gate, seeded bugs, the trust re-measure and mutants do not apply: no Lean, Python or Rust file is
changed. The overlap check was done: no branch in flight touches `docs/infra/gen-inv-design/`.

## Next item

gi-1: take `VE.Audit` out of the default Lean build, and measure `lake build` before and after. It is queued by the
DRI after reading the design.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay change)
2. Every required deliverable built, no rule broken: PASS (DESIGN.md has every section the task names; no script or product file changed)
3. Tests and gates can fail: N.A. (no code; seeded bugs not required for a docs-only item)
4. Python, Lean and Rust agree: N.A.
5. R8 binding: N.A.
6. Gate evidence matches the final HEAD: PASS (the chain gates the final HEAD)
7. No unsigned item left: PASS (no DELTA rows, no reserved signature)
8. Every user-visible change in DELTA: N.A. (no user-visible change)
9. Test selection still finds the tests: N.A. (docs only)
10. Lean statements and proofs: N.A.
11. Budgets, limits and deadlines fail closed: N.A.
12. No CPU or memory regression: N.A.
13. Test-removed trailers: N.A. (no test removed)
