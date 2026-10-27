# sc-1bb delta: B1, the scope benchmark row

Base: `git merge-base HEAD main` (`ab010c3f0`). sc-1bb is the B1 row of [scope-PLAN.md](../../spec/scope-PLAN.md)
(benchmark table, with C11); [REPORT.md](REPORT.md) has the rest.

**No user-visible delta.** The item adds a benchmark row (`tools/bench/test_perf.py::test_scope_b1`), its input
builder (`tools/bench/scope_b1.py`), a Lean measurement executable outside the default build (`ve_scope_bench`,
`lean/ScopeBenchMain.lean`) and a suite test of the input. No route, service mode, response schema, diagnostic,
verdict, CLI output or document answer changes: `lean/VE/` and `ve/` are unchanged apart from one `other_json` line
in `ve/assurance-manifest.json` that records the new file's JSON use. The trust budget does not grow: the
executable's four declarations are class `T` (tests and checks), measured with `tools/trust_map.py --check`
(trusted +0 for this item). So this file has no table.
