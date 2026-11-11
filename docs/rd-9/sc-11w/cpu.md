# sc-11w: `routeSD`'s reads before its work limit, measured

## Method

- Machine: the VM, AMD EPYC 7B12, 32 vCPU, 125 GB, Linux 7.0.0-1014-gcp. Compiled Lean, leanprover/lean4:v4.24.0.
- Code: commit 0f979e53d0. Its `lean/` is that of 4559df88d0, the last Lean change.
- Bench: `cpu_bench.lean` (this directory) is the `main` of a throwaway Lake package that requires this worktree's
  `lean/`. It is built by `lake build bench` and run as `/usr/bin/time -f %U ./.lake/build/bin/bench <case> <value>`,
  one value per process.
- Figures: user CPU of three runs each. A process that only decodes the environment and builds the document takes
  about 0.05-0.07 s, and every figure includes it.
- Load: the 5-minute load was 36 to 37 (other worktrees' builds; 15-minute load 44 to 45). The method follows docs/rd-9/sc-11/w13-cpu.md.
- Documents: the bench restates SoftSupWireExamples.lean's documents, so it builds without that module's `#guard`s.
  - `withRules n m g` is `NSDbig n` plus `m` fixed strict rules with guard `g i`. NSDheavy, atCharge and overCharge
    are this shape.
  - `withSets n k` is `NSDbig n` plus `k` sets of two assertions.
  - `withCandidates n k` is `NSDbig n` plus one set of `k` assertion candidates.

## `routeSD` on the committed code

Columns:
- `reads` evaluates `superposable N.D` and `WellFormedU (supU N)` without the charge. Where the charge refuses, this
  is the time it saves.
- `work` is `sdCheckWork N`, evaluated through `sdCheckWork_eq_fast`.

| Case | `sdSizeCharge` | `routeSD` | `routeSD` CPU | `reads` CPU | `work` CPU |
| --- | --- | --- | --- | --- | --- |
| `wideGuard191` (`NSDbig 8 (wide 6)`) | 5,975 | enumerated (work 73,472) | 0.21, 0.21, 0.21 s | 0.21, 0.22, 0.21 s | 0.06, 0.07, 0.07 s |
| `wideGuard767` (`NSDbig 8 (wide 8)`) | 20,375 | enumerated (over the charge) | 0.06, 0.06, 0.07 s | 0.31, 0.31, 0.30 s | 0.07, 0.07, 0.07 s |
| `wideGuard3071` (`NSDbig 6 (wide 10)`) | 59,033 | enumerated (over the charge) | 0.07, 0.06, 0.07 s | 0.27, 0.25, 0.27 s | 0.07, 0.07, 0.07 s |
| `NSDheavy` (sc-11-2 item 2) | 14,703 | enumerated (work 34,752) | 0.19, 0.20, 0.20 s | 0.18, 0.19, 0.17 s | 0.06, 0.06, 0.08 s |
| `NSDbig 8` (W-13 row 1) | 1,225 | superposed | 0.60, 0.53, 0.50 s | 0.08, 0.09, 0.09 s | 0.07, 0.06, 0.06 s |
| `atCharge` (16 units × 1,024 nodes) | 16,384 | superposed | 0.11, 0.11, 0.11 s | 0.09, 0.08, 0.08 s | 0.06, 0.06, 0.07 s |
| `overCharge` (29 × 565) | 16,385 | enumerated (over the charge) | 0.06, 0.06, 0.06 s | 0.10, 0.09, 0.10 s | 0.07, 0.07, 0.07 s |
| `withRules 2 25` (32 × 512) | 16,384 | superposed | 0.15, 0.15, 0.14 s | 0.09, 0.10, 0.10 s | 0.07, 0.07, 0.07 s |
| `withSets 1 40` (124 × 127) | 15,748 | enumerated (work) | 0.20, 0.18, 0.19 s | 0.08, 0.09, 0.09 s | 0.18, 0.16, 0.17 s |
| `withCandidates 1 121` (126 × 129) | 16,254 | superposed | 0.17, 0.19, 0.17 s | 0.07, 0.09, 0.08 s | 0.07, 0.07, 0.07 s |
| `NSDsets` (`withSets 1 300`) | 819,928 | enumerated (over the charge) | 0.06, 0.06, 0.07 s | 2.59, 2.72, 2.58 s | 4.25, 4.24, 3.59 s |
| `NSDcands` (`withCandidates 1 5000`) | 25,065,040 | enumerated (over the charge) | 0.04, 0.04, 0.06 s | 12.70, 9.37, 8.84 s | 0.67, 0.71, 0.72 s |
| `heavyIn` (`withRules 6 9`, 47-node guards; open, row sc-11wc) | 12,880 | superposed | 0.69, 0.67, 0.74 s | 0.12, 0.10, 0.10 s | 0.04, 0.04, 0.04 s |

Results:
- Every case here ends within R4's 1 s at this load, but the charge does not ensure that for every document within
  both limits. The slowest is `heavyIn` at 0.74 s, and it took up to 1.16 s at a higher load (below); that is the
  accepted gap of row sc-11wc. The slowest of the other cases is `NSDbig 8` at 0.60 s; its 256 per-choice texts are
  charged by the work limit.
- `withRules 2 25`, `withSets 1 40` and `withCandidates 1 121` are at or just under 16,384, with `superposable` and
  `WellFormedU (supU N)` both true. They are the largest admitted documents of their shapes. The reads take at most
  0.10 s on them, and at most 0.22 s on any case within the charge (`wideGuard191`). One more shape is at 16,384 but has `superposable` false: `withRules 2 57` (64 × 256).
- Without the charge, the many-sets and many-candidates documents found by the self-review would cost 2.6-12.7 s in
  `superposable` alone. With the charge they are refused in at most 0.07 s.
- `heavyIn` took 0.85-1.16 s at load 43-67 earlier in the day (reviews/dri-decisions-20261110-sc-11w-cpu.md) and
  0.67-0.74 s here. Its cost is the per-choice texts within `maxSdCheckWork`, which is row sc-11wc's to bound.

## `sdCheckWork` before and after the csimp

Before: `sdCheckWork`'s own body (`cpu_bench.lean`'s `slowWork`, the text 14.8 states) builds every premise of
`softXL N (sup N.D).1`, including each `cohPremiseU`'s `fill`, `selects` and `subst` of the guard, only to count them.
After: `sdCheckWorkFast` counts the exception labels and the colliding pairs and builds no coherence premise. It
still builds the exception premises (`excPremises`), one formula per exception condition, to read their count. The `@[csimp]`
theorem `sdCheckWork_eq_fast` proves the two equal, and both give the same values. The "before" column was measured
at 8b08388be5, load 44 to 76. `slowWork` does not read the size charge, so the later charge change leaves it as is.

| Case | `sdCheckWork` | before (main's body) | after (`work` above) |
| --- | --- | --- | --- |
| `wideGuard191` | 73,472 | 0.93, 0.93, 0.95 s | 0.06-0.07 s |
| `NSDheavy` | 34,752 | 0.65, 0.60, 0.64 s | 0.06-0.08 s |
| `wideGuard767` | 220,928 | 10.19, 10.27, 10.30 s | 0.07 s |
| `wideGuard3071` | 201,152 | 97.25, 92.02, 87.34 s | 0.07 s |

## Where w13-cpu.md's 10.98 s and 94-100 s went

w13-cpu.md's bench (`w13_bench.lean` at 9a563edce) prints `sdCheckWork N` in the same timed process as `routeSD re N`.
Its 10.98 s and 94-100 s are therefore `sdCheckWork`'s premise build (the "before" column above), not `sdSuperposable`'s.

Main's `routeSD` alone, timed in this session with `IO.monoNanosNow`:
- On the 767- and 3,071-node documents it never reads `sdCheckWork`, because `&&` stops at `sdSuperposable` false: it
  took 142 ms and 130 ms (load 25).
- On the 191-node document `sdSuperposable` is true, so it reads `sdCheckWork`: 952 ms, and 1,444 ms in a second run
  at load 70.
- On NSDheavy: 1,324 ms.

The DRI accepted this correction in reviews/dri-decisions-20261110-sc-11w.md.

## Per-choice texts (row sc-11wc)

Within the work limit, the per-choice texts cost about 31-54 µs per `sdCheckWork` unit across the shapes tried.
NSDheavy's 64 texts took 1.87 s, but its work (34,752) is over the limit, so they are never read. `heavyIn` is within
both limits and took up to 1.16 s. The DRI filed row sc-11wc to bound this before sc-11b
(reviews/dri-decisions-20261110-sc-11w-cpu.md).
