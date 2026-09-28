# Running the complete test suite

From the repository root, with Lean's `lake` and Rust's `cargo` available:

```sh
PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-xdist-uv-cache uv run --frozen python -m pytest -n auto
```

The default pytest options exclude tests marked `live`, so this command makes no model calls. For a serial comparison, run:

```sh
PATH="$HOME/.elan/bin:$PATH" UV_CACHE_DIR=/tmp/ve-xdist-uv-cache uv run --frozen python -m pytest
```

`-n auto` uses the available CPUs (16 on the current VM).

The session fixture in `tests/conftest.py` builds Lean and Rust once per pytest invocation under a file lock shared by all xdist workers. Tests only read the prepared binaries and Lean object files. Rust's release and debug targets share this lock; individual tests do not start further builds. Each test's `tmp_path` is unique across workers. Tests that change environment variables or module globals use pytest's `monkeypatch`, which is local to their worker process and restored after the test.
