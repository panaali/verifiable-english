# Baseline replay evidence

## 2026-09-28: clean-room replay on the same host (deviation from the second-machine requirement)
- Method: `git bundle create` of branch mig/stage0 at a33b07d, fresh `git clone` into an empty scratch directory, fresh `UV_CACHE_DIR` (new virtualenv, locked dependencies), then the two replay commands from README.md.
- Host: multi-agent-lab (the same VM that produced the baseline); Python 3.14.7.
- Exit codes: probe_matrix.py 0, semantic_inventory.py 0.
- SHA-256 before and after (identical):
```
f9ab0e23957ab021cdeef820a60e1a38e03d30145a08a3f45011edf430350ae4  conformance/baseline-2026-09/python.json
3cdf033372d37bc7b2478da7e6be48b046274a954624c6ff7fc0118d8d6bf51c  conformance/baseline-2026-09/external-imports.json
823763e0df3ee5d9272689f574fd4f16bf24b1bb72d6a77fee483780b25776a0  docs/spec/semantics-inventory.md
d1be411f8a56c0bad9b4f11902913f3829ac2d27fe1175bae413430f2271f050  docs/spec/semantics-support-matrix.md
```
- Status: local determinism from a clean checkout and environment is established. This is NOT an independent-machine replay. Orchestrator decision (DRI): Gate 0 may proceed with this recorded deviation; an actual second-machine replay (after the VM resize or on the lead's laptop) is still owed and must be appended here before Gate 5 (deletion).
