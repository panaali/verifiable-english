# W-13: the route check's Lean CPU, measured (OPEN-SC11-7)

Measured 2026-11-09 on the VM: AMD EPYC 7B12, 32 vCPU, 125 GB, Linux 7.0.0-1014-gcp, 5-minute load 78 to 108 (other
worktrees' builds). Compiled Lean: a throwaway Lake package requiring this
worktree's `lean/` by path, whose `main` decodes `SoftSupWireExamples.envWith 0`, builds `NSDbig n` (with `wide e` as
set 0's strict guard for the last three rows) and prints `routeSD re N` and `sdCheckWork N`; `/usr/bin/time` user CPU
of one run, with `maxSdCheckWork` = 4,194,304 (the spec's provisional value then), so no case below is cut by work.

| Document | Choices | `sdCheckWork` | Route | Lean CPU |
| --- | --- | --- | --- | --- |
| NSDbig 6 | 64 | 4,672 | superposed | 0.21 s |
| NSDbig 7 | 128 | 10,880 | superposed | 0.39 s |
| NSDbig 8 | 256 | 24,832 | superposed | 0.71 s |
| NSDbig 9 | 512 | 55,808 | superposed | 1.58 s |
| NSDbig 10 (W-13 row 1) | 1024 | 123,904 | superposed | 3.67 s |
| NSDbig 8, one guard of 191 nodes | 256 | 73,472 | superposed | 4.58 s |
| NSDbig 8, one guard of 767 nodes | 256 | 220,928 | enumerated | 10.98 s |
| NSDbig 6, one guard of 3,071 nodes | 64 | 201,152 | enumerated | 94.23 s |

On W-13's shape the check costs about 29 µs of Lean CPU per unit of `sdCheckWork` (3.67 s / 123,904); R4's bar is
1 s. A wide guard costs more per unit (62 µs at 191 nodes, 468 µs at 3,071 nodes). The last row has 64 choices, so
today's admission (`admitSDOf`, 3.3 step 5) already runs the same per-choice texts on it.
