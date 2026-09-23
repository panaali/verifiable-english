# T1c: separating certificates for "cannot access" claims

Preregistration: [PREREG-T1c.md](PREREG-T1c.md). Design notes: `design/crypto-inspired-oversight.md`
(section 1 and Assessment) and `design/frontier-failure-modes-and-ve.md` (section 3, item 2).
Code: `ve_experiments/t1c/`. Tests: `tests/test_t1c.py`. This pilot replaces the PLAN-T4
policy-invariant pilot as the next use of the closure-induction rule.

Offline (no model calls), from the repository root, serially:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-t4
uv run python -m ve_experiments.t1c.run prepare   # items, certificates, Python+Lean replay, HASHES
uv run pytest -q tests/test_t1c.py
uv run python -m ve_experiments.t1c.run gate --backend oracle   # also random / approve / reject
uv run python -m ve_experiments.t1c.run stamp     # OpenTimestamps receipts, then commit
```

Offline results: all 44 true claims certify (Python and Lean); VE and the plain closure script agree on
every item; leak certificates are rejected; wrong-binding certificates are valid for another statement.
Synthetic-monitor results are in [known-answer.json](known-answer.json).

Gate (model calls; host, not a sandbox; account danielsaeedi37; not before 2026-09-23T06:00Z):

```sh
cd /Users/seyran/code/ve-opus-t4 && UV_CACHE_DIR=/private/tmp/ve-uv-cache-t4 \
  uv run python -u -m ve_experiments.t1c.run gate --account danielsaeedi37
```

Exit 75 means a resumable pause (transport failure or session limit): rerun the same command later.
After CONTINUE, `full` runs the four arms; `report --split gate|full` summarises without calls.
