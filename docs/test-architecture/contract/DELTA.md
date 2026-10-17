# tarch-contract delta

This batch changes no VE document, checker, relay, diagnostic, limit, verdict or public output. No Lean or Rust
file changes.

The developer tooling gains what the DRI's task for test-architecture plan rank 2 (section 3.3) asks for:

- `tools/gate.py --contract [LIST]`, a new mode. It runs only the tests of the contract list, with the gate's
  environment, toolchain checks, builds, pin check, native Rust tests, pytest options and quarantine. It leaves
  out the Lean audit and the collection check. Its record says `"mode": "contract"`, its status is
  `contract-passed` or `failed` (never `passed`), and its default record is `platform-contract-result.json`
  (ignored by git, like `gate-result.json`).
- A gate run without `--contract` behaves exactly as before: same stages, collection, record and statuses.
  The only change is in `--help`: `--output` now names its default in words, and the default is unchanged.
- `tools/platform_contract.py` (`contract`, `divergences`, `run`, `misses`, `estimate`) and the two
  generated lists `tests/platform-contract.json` and `tests/platform-divergences.json`, registered in
  `tools/regen_generated.py`.

Zero pending rows: the task file directs each item, and none changes a user-visible VE output.
