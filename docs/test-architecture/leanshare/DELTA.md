# tarch-leanshare: user-visible deltas

None in VE's output: no verdict, diagnostic code or text, fault order, field, limit or CPU budget changes. No standing
ruling is claimed.

Tooling additions (developer-facing, not a VE output):

| Change | Where | Test |
|---|---|---|
| New tool: shared Lean builds (`key`, `restore`, `publish`, `verify`, `prune`) | `tools/lean_share.py` | `tests/test_lean_share.py` |
| New `--obsolete` and `--drop-obsolete` flags; `executables`, `obsolete` and `drop_obsolete` | `tools/lake_outputs.py` | `tests/test_lake_outputs.py` |
| `lean_executable(env, name)` also finds `lake` (its default is still `lean`, with the same message) | `tools/lake_outputs.py` | `test_lean_is_found_in_the_accounts_elan_when_home_is_replaced` (unchanged, passes) |
