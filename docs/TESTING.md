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

The session hook in `tests/conftest.py` builds Lean and Rust once per pytest invocation under a checkout-wide file lock in `rust/target/`. Every pytest process holds a shared lock while tests read the prepared binaries and Lean object files, so another invocation waits before rebuilding them. Builders inherit the exclusive lock, and timed-out builds stop their whole process group before the lock is released. Rust's release and debug targets share this lock; individual tests do not start further builds. Each test's `tmp_path` is unique across workers, including the Rust fuzz test inputs and summaries. Tests that change environment variables or module globals use pytest's `monkeypatch`, which is local to their worker process and restored after the test.

After a successful explicit `lake build` and both Rust release and debug builds, set `VE_NATIVE_PREBUILT=1` to take the shared read lock and run pytest against those binaries without rebuilding. Set `VE_LEAN_PREBUILT=1` as well to skip the service tests' redundant target builds. The ordinary command above still performs the native builds itself.
