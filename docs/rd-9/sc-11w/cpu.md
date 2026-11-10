# sc-11w: `routeSD`'s reads before its work limit, measured

DRAFT (2026-11-10, builder): the measurements behind the DRI question of this item; the final table (committed code,
three runs each) replaces this section before review.

Machine: the VM, AMD EPYC 7B12, 32 vCPU, Linux 7.0.0-1014-gcp; compiled Lean, a throwaway Lake package requiring this
worktree's `lean/` (`bench` exe, timing with `IO.monoNanosNow` around each value, forced by printing it); 5-minute load
25 to 70 (other worktrees' builds).

## Where the wide-guard documents' CPU goes (main's code, 153d3a4be's `SoftSupWire.lean`)

Each value timed on its own (`NSDbig n (wide e)` as in w13-cpu.md):

| Document | `superposable`'s `sideWF` | `WellFormedU (supU N)` | `sdCheckWork N` | `routeSD re N` alone |
| --- | --- | --- | --- | --- |
| NSDbig 8, guard of 191 nodes | 154 ms | 52 ms | 868 ms | 952 ms (enumerated by work) |
| NSDbig 8, guard of 767 nodes | 124 ms (false) | 112 ms | 8,149 ms | 142 ms (enumerated: `sdSuperposable` false) |
| NSDbig 6, guard of 3,071 nodes | 78 ms (false) | 63 ms (false) | 89,722 ms | 130 ms (enumerated: `sdSuperposable` false) |

w13-cpu.md's bench (`w13_bench.lean` at 9a563edce) prints `sdCheckWork N` in the same timed run as `routeSD re N`, and
`/usr/bin/time` times the whole run, so its 10.98 s and 94-100 s are `sdCheckWork`'s own evaluation, not
`sdSuperposable`'s: `routeSD` never reads `sdCheckWork` on those two documents (`&&` stops at `sdSuperposable` false).
`sdCheckWork` reads `(softXL N (sup N.D).1).length`, which builds every coherence premise (`cohPremiseU`: `fill`,
`selects`, `subst` of the wide guard) only to count them.
