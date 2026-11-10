# arch-20261109-2: deltas

None user-visible. The batch changes tooling only: `tools/layer_policy.py` and the checks that read it
(`tools/check_lean_imports.py`, `tools/check_python_layers.py`, `tools/hooks/precommit.py`, `tools/select_tests.py`),
a new listing tool (`tools/layer_declarations.py`), their tests, one comment in `tools/trust_mutants.py`, the
docs and the generated code map. It changes no `ve/`, `lean/` or `rust/` file, no response schema, no verdict and
no product diagnostic. Every module's layer is unchanged (`layers-before.txt` and `layers-after.txt` are identical,
REPORT.md), `.importlinter` is byte-identical and both layer checks give the same output (`checks-before-after.txt`).
The developer-facing messages of the layer checks gained a pointer to the in-module declaration; that is no product
output.
