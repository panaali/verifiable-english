# T1 mixed-format RBAC demo

Protocol: [PREREG-T1.md](PREREG-T1.md). Implements the final revision of
[PLAN-V5-DEMO.md](../../PLAN-V5-DEMO.md). Serial, one account throughout.

From repository root:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python -m ve_experiments.t1.run prepare
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python -m ve_experiments.t1.run stamp
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python -m ve_experiments.t1.run gate
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python -m ve_experiments.t1.run report
# Only if the gate passes and the full study is separately requested:
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run python -m ve_experiments.t1.run full
```

The full command refuses a failed/incomplete gate. Run in a macOS host terminal:
nested sandbox policies may prevent `sandbox-exec` initialization. There is no
unsafe execution fallback. The runner pins account `danielsaeedi37` for authors,
monitors and both judges. Infrastructure errors persist in `STOP.json` and
cannot be silently retried. A run spanning UTC midnight stops on context drift.

Offline checks (last includes sandbox confinement, outside a nested sandbox):

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run pytest -q tests/test_t1.py
T1_SANDBOX_TEST=1 UV_CACHE_DIR=/private/tmp/ve-uv-cache-v4 uv run pytest -q tests/test_t1.py
```

`items-*.json` include private gold data for the experiment, never transmitted
to judges. `results-*/ledgers` retain all model requests and raw responses;
`costs` count physical successful calls once; `scores` hold final decisions.
The closure arm uses the existing Python VE finite-model evaluator and a checked
cut/path witness; no Lean verification claim. Semantic fidelity remains a model
audit. Pending OpenTimestamps calendar receipts are not Bitcoin confirmation.
