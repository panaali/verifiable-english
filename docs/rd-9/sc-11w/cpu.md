# sc-11w: `routeSD`'s reads before its work limit, measured

Measured 2026-11-10 on the VM: AMD EPYC 7B12, 32 vCPU, 125 GB, Linux 7.0.0-1014-gcp; 5-minute load 67 to 80 for the
first table and 44 to 76 for the second (other worktrees' builds). Compiled Lean (leanprover/lean4:v4.24.0) at commit
8b08388be5: `cpu_bench.lean` (this directory) is the `main` of a throwaway Lake package requiring this worktree's
`lean/`, built by `lake build bench` and run as `/usr/bin/time -f %U ./.lake/build/bin/bench <case> <value>`, with one
value per process. The figure is user CPU, three runs each. A process that only decodes the environment and builds the
document takes about 0.07 s, and every figure includes it. The method follows docs/rd-9/sc-11/w13-cpu.md.

## `routeSD`, and the reads the charge guards, on the committed code

`reads` evaluates `superposable N.D` and `WellFormedU (supU N)` without the charge: it is what the charge saves where it
refuses. `work` is `sdCheckWork N`, evaluated through `sdCheckWork_eq_fast`.

| Case | `sdSizeCharge` | `routeSD` | `routeSD` CPU | `reads` CPU | `work` CPU |
| --- | --- | --- | --- | --- | --- |
| `wideGuard191` (`NSDbig 8 (wide 6)`) | 3,927 | enumerated (work 73,472) | 0.29, 0.25, 0.27 s | 0.27, 0.27, 0.28 s | 0.08, 0.08, 0.07 s |
| `wideGuard767` (`NSDbig 8 (wide 8)`) | 13,719 | enumerated (`superposable` false) | 0.24, 0.25, 0.25 s | 0.39, 0.40, 0.42 s | 0.08, 0.07, 0.07 s |
| `wideGuard3071` (`NSDbig 6 (wide 10)`) | 40,313 | enumerated (over the charge) | 0.08, 0.07, 0.07 s | 0.35, 0.34, 0.33 s | 0.09, 0.09, 0.09 s |
| `NSDheavy` (sc-11-2 item 2) | 11,523 | enumerated (work 34,752) | 0.23, 0.21, 0.22 s | 0.22, 0.23, 0.23 s | 0.07, 0.08, 0.08 s |
| `NSDbig 8` (W-13 row 1) | 697 | superposed | 0.66, 0.67, 0.69 s | 0.11, 0.12, 0.10 s | 0.07, 0.08, 0.08 s |
| `atCharge` (16 rules × 1,024 nodes) | 16,384 | superposed | 0.23, 0.22, 0.21 s | 0.14, 0.14, 0.14 s | 0.08, 0.07, 0.08 s |
| `overCharge` (29 × 565) | 16,385 | enumerated (over the charge) | 0.07, 0.08, 0.08 s | 0.12, 0.14, 0.14 s | 0.09, 0.08, 0.08 s |
| `NSDsized 3 679 0` (8 × 2,048) | 16,384 | superposed | 0.26, 0.27, 0.25 s | 0.16, 0.15, 0.16 s | 0.07, 0.07, 0.07 s |
| `NSDsized 27 18 15` (32 × 512) | 16,384 | superposed | 0.16, 0.17, 0.17 s | 0.12, 0.12, 0.12 s | 0.08, 0.08, 0.08 s |
| `NSDbig 6` and 3 rules of 331 nodes (16 × 1,024) | 16,384 | enumerated (work) | 0.22, 0.24, 0.24 s | 0.24, 0.25, 0.24 s | 0.07, 0.08, 0.08 s |

Every case ends within R4's 1 s, at most 0.69 s (`NSDbig 8`, whose 256 per-choice texts the work limit charges). The
at-limit documents have `superposable` and `WellFormedU (supU N)` both true. They are the worst admitted cases for the
reads before the work limit, and the slowest of those reads takes 0.25 s. `NSDsized 59 4 9` (64 × 256) is also at
16,384, but its `superposable` is false.

## `sdCheckWork` before and after the csimp

Before: `sdCheckWork`'s own body (`cpu_bench.lean`'s `slowWork`, the text 14.8 states) builds every premise of
`softXL N (sup N.D).1`, including each `cohPremiseU`'s `fill`, `selects` and `subst` of the guard, only to count them.
After: `sdCheckWorkFast` counts the exception labels and the colliding pairs and builds no premise. The `@[csimp]`
theorem `sdCheckWork_eq_fast` proves the two equal, and both give the same values below.

| Case | `sdCheckWork` | before (main) | after (`work` above) |
| --- | --- | --- | --- |
| `wideGuard191` | 73,472 | 0.93, 0.93, 0.95 s | 0.07-0.08 s |
| `NSDheavy` | 34,752 | 0.65, 0.60, 0.64 s | 0.07-0.08 s |
| `wideGuard767` | 220,928 | 10.19, 10.27, 10.30 s | 0.07-0.08 s |
| `wideGuard3071` | 201,152 | 97.25, 92.02, 87.34 s | 0.09 s |

## Where w13-cpu.md's 10.98 s and 94-100 s went

w13-cpu.md's bench (`w13_bench.lean` at 9a563edce) prints `sdCheckWork N` in the same timed process as `routeSD re N`.
Its 10.98 s and 94-100 s are therefore `sdCheckWork`'s premise build (the "before" column above), not `sdSuperposable`'s.
On main, `routeSD` alone never reads `sdCheckWork` on those two documents, because `&&` stops at `sdSuperposable` false.
Timed on main's code in this session (load 25, `IO.monoNanosNow`), it took 142 ms on the 767-node document and 130 ms on
the 3,071-node one. On the 191-node document `sdSuperposable` is true, so `routeSD` reads `sdCheckWork`, and it took
952 ms (1,444 ms in a second run at load 70). NSDheavy took 1,324 ms. The DRI accepted this correction in
reviews/dri-decisions-20261110-sc-11w.md.

## Per-choice texts (not changed here)

Within the work limit, the per-choice texts cost about 31-54 µs per `sdCheckWork` unit across the shapes tried. W-13's
shape costs about 31-36 µs per unit. Ten fixed rules of 47-node guards (NSDheavy's shape) cost about 54 µs per unit:
1.87 s for NSDheavy's 64 texts, which its work (34,752 units, over the limit) refuses. So a document just within
32,768 units on a heavy shape could take up to about 1.8 s. That bound is `maxSdCheckWork`'s (sc-11 item 1), not this
item's, and is filed as a follow-up in REPORT.md.
