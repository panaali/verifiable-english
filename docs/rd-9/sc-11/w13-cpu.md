# W-13: the route check's Lean CPU, measured (OPEN-SC11-7)

Measured 2026-11-09 on the VM: AMD EPYC 7B12, 32 vCPU, 125 GB, Linux 7.0.0-1014-gcp, 5-minute load 78 to 108 (other
worktrees' builds). Compiled Lean: `w13_bench.lean` as of commit 9a563edce (`git show 9a563edce:docs/rd-9/sc-11/w13_bench.lean`), the
`main` of a throwaway Lake package (`[[require]] path = "<worktree>/lean"`, `[[lean_exe]] root = "Bench"`, built by
`lake build bench`), run as `/usr/bin/time -f %U ./.lake/build/bin/bench <sets> [<e>]`: it decodes the soft-chain
environment of `SoftSupWireExamples.envWith 0`, builds `NSDbig <sets>` (with `wide <e>` as set 0's strict guard) and
prints `routeSD re N` and `sdCheckWork N`. User CPU of one run, with `maxSdCheckWork` = 4,194,304 (the spec's
provisional value then), so no case below is cut by work.

| Document | Choices | `sdCheckWork` | Route | Lean CPU |
| --- | --- | --- | --- | --- |
| NSDbig 6 | 64 | 4,672 | superposed | 0.21 s |
| NSDbig 7 | 128 | 10,880 | superposed | 0.39 s |
| NSDbig 8 | 256 | 24,832 | superposed | 0.71 s |
| NSDbig 9 | 512 | 55,808 | superposed | 1.58 s |
| NSDbig 10 (W-13 row 1) | 1024 | 123,904 | superposed | 3.67 s |
| NSDbig 8, one guard of 191 nodes | 256 | 73,472 | superposed | 4.58 s |
| NSDbig 8, one guard of 767 nodes | 256 | 220,928 | enumerated: `sdSuperposable` false | 10.98 s |
| NSDbig 6, one guard of 3,071 nodes | 64 | 201,152 | enumerated: `sdSuperposable` false | 94.23 s; again 100.11 s |

On W-13's shape the check costs about 29 µs of Lean CPU per unit of `sdCheckWork` (3.67 s / 123,904); R4's bar is
1 s. The NSDbig 8 row with a 191-node guard costs 62 µs per unit. The last two rows are enumerated because
`sdSuperposable` is false (a generated layer over `superposable`'s size limit; checked on `NSDbig 6 (wide 8)`, which
has row 7's guard), so `&&` reads no `sdChecked`: their CPU is `sdSuperposable`'s own, `superposable` and
`WellFormedU` of the superposed document, read before the work limit. Correction (2026-11-09 21:44): the builder's
message to the DRI read these two rows as per-choice text cost. Measured with a third argument that times only
`(checkedChoices N.D).all (sdChoiceText re N ·)`: 0.09 s on row 8's document (its first choice's text fails, so `all`
stops) and 0.63 s on row 7's (`main` of the same bench at 9a563edce plus that branch).
