# Semantics migration, stage 3: progress

Checkpoint of the build of [mig3.md](mig3.md) (the statement spec) per [mig3-PLAN.md](mig3-PLAN.md). The Gate 3
report goes at the end of this file (statement spec, section 9).

## Lean (B4, fixture T1)

Stage 3 edits no file under `lean/` and adds no Lean statement (statement spec D12 and section 5); the Lean part
of the build is B4, checked here on branch `mig3/lean` at `a6c6b78b` (merge base with `main`: `a093a14d`),
2026-10-04. `git diff --stat a093a14d..a6c6b78b -- lean rust` is empty.

| Check | Result: the counts T1 compares against after the build |
|---|---|
| `lake build` (in `lean/`) | completed, 560 jobs |
| `python3 lean/audit.py` | PASS: 286 source files; 2959 named theorem declarations audited; only the declared standard axiom allowlist |
| `python3 lean/VE/Route/frozen.py` | PASS: frozen Lean sources and `Main.lean` subcommands unchanged |
| `lean/checkers.lock` | `lean/.lake/build/bin/ve_service` is `52ec157c…` and `rust/target/release/ve` (built by `tools/rust_build.py --check`) is `c8b4c7ab…`; both pinned |

The statements of section 5 are the ones built: `lean/VE/Service/Protocol.lean:468–498` in the namespace
`VE.Service` (lines 39 and 535), the fifteen `runMode_*` pins and `caseResult_ok`, each `rfl`.

The full suite at the default authority passed at the same commit, with `VE_NATIVE_PREBUILT=1`, 16 file chunks
and the merge smoke run on its own: 5,964 passed, 6 skipped. One test,
`tests/test_precommit_hook.py::test_large_staged_change_stays_under_ten_seconds`, failed its 10-second wall-clock
bound at load average about 40 and passed when run alone at load average about 23.
