# Offline validation and execution boundary

Before the preregistration commit and before gate calls, the explicit host test
command passed all 12 tests:

```text
T1_SANDBOX_TEST=1 UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run pytest -q tests/test_t1.py
12 passed in 2.29s
```

Coverage includes deterministic generation at both sizes; unique 6–10-hop
sabotage paths; disjoint gate/full/dev IDs and balanced assignments; positive
and negative VE claims; omitted/duplicated mappings; forged witnesses; an
endpoint-reversal attack that passes exact source coverage while changing
meaning; gate threshold and incomplete-run behavior; four-candidate code
selection with blinded Sonnet prompts; four-step adaptive VE feedback; and
OS confinement of untrusted Python.

The sandbox was tested on the host because macOS refuses initializing a new
Seatbelt sandbox inside the tool's existing sandbox. The final sandbox passes
normal execution and denies repository/credential reads, network connections
and arbitrary child processes. The system Python runtime needs both its launcher
and its internal Python.app executable on the executable allowlist. Initialization
errors fail closed; the gate uses no generated-code execution.

No live b-exec, b-prime, c or d calls were made for this task. Their mechanisms
were checked offline; this document does not claim empirical performance for
those arms. The gate evaluates only arm a with Opus. All timestamps, model IDs,
accounts, prompts and usage remain available in the retained ledgers.
