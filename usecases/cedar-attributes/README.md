# Cedar attribute fragment

The checked relation says that Alice's department is finance. The declaration
requires each person to have exactly one department. Replacing the model row
with two different department values, or removing Alice's row, makes the
model invalid with generator `flags`. The distinct declared string literals
cannot alias.

Run from the repository root:

```sh
uv run python -m ve evaluate --env usecases/cedar-attributes/environment.json \
  --model usecases/cedar-attributes/model.json usecases/cedar-attributes/claim.ve
```

The full Cedar permit and forbid decisions require the W1 norm adapter.
