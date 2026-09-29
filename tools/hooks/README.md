# Git hooks

`pre-commit` runs fast checks on the **staged** content of a commit. Everything
comes from the index: file contents are read raw with `git cat-file` (no
`.gitattributes`, diff drivers, filters or binary detection), and the policy
code the checks reuse (`tools/layer_policy.py`, `tools/check_lean_imports.py`,
`tools/check_rust_deps.py`, `lean/audit.py`) is the staged version, loaded from
a temporary snapshot of the index together with the staged directory and `.py`
layout that Python import resolution consults. The working tree is never read,
so a verdict depends only on what the commit would record. It runs no tests and
no builds. A typical commit takes well under a second;
`tests/test_precommit_hook.py` holds a 1,765-path, 18 MB staged change to under
10 s. Run `tools/hooks/pre-commit --timings` to see per-check times.

| Check | What it rejects | Source of truth |
| --- | --- | --- |
| secrets | In every added or modified staged file, text or binary: a match for private key blocks, AWS, GitHub, Anthropic, OpenAI, Google, Slack, Hugging Face or Stripe live credentials, or a quoted high-entropy `api_key`/`secret_key`/`client_secret`/`access_token`/`auth_token`/`password` value, on a line that is not already a line of that path at `HEAD`; any staged path under `.webapp-private/`; `.env` files (not `.env.example`/`.sample`/`.template`), `id_rsa`-style keys, `.p12`/`.pfx` files | patterns in `precommit.py` |
| layer imports | New outward imports (a module importing a higher layer) that are not in the reviewed ledger, in staged `ve/**/*.py` and `lean/**/*.lean` (Python: the whole file; Lean: the header exactly as the pinned toolchain's header parser reads it, however many lines or commands per line it spans, and nothing after it); a newly added module the layer map does not cover; a missing local Lean import; outward crate dependencies when a `rust/**/Cargo.toml` is staged | the staged `tools/layer_policy.py`, `tools/check_lean_imports.py`, `tools/check_rust_deps.py` and ledgers `tools/layer-exceptions.json`, `tools/lean-layer-exceptions.json` |
| Lean forbidden tokens | In staged files under `lean/`: every whole word the staged `lean/audit.py` forbids (today `sorry`, `sorryAx`, `admit`, `axiom`, `unsafe`, `native_decide`, `implemented_by`, `partial`, `opaque`, `extern`), in comments and strings too, as the audit does. In other staged `.lean` files: `sorry`, `sorryAx`, `admit` or `axiom` in code | the staged `lean/audit.py` |
| frozen files | A staged change to a file listed in `lean/VE/Route/frozen-sources.sha256` unless the staged inventory records the staged file's SHA-256; a deleted file that is still listed; a new `lean/VE/**/*.lean` module that is not listed; a changed `lean/Main.lean` that no longer matches `MAIN_BASE` in `lean/VE/Route/frozen.py`. A staged inventory or `frozen.py` re-checks every entry | `lean/VE/Route/frozen.py` rules |

The hook checks only what a commit adds. Existing drift, such as stale ledger
entries, `.importlinter` sync or modules that were unmapped before this commit,
is left to the full checkers.

To update the frozen inventory after an intended edit, rehash the file from
`lean/` (`sha256sum VE/Path/File.lean`), replace its line in
`VE/Route/frozen-sources.sha256`, stage both, and run `python3 VE/Route/frozen.py`.

A deliberate example of a credential in a test or document can carry the marker
`pragma: allowlist secret` on the same line. Build test credentials at run time
instead where possible, as `tests/test_precommit_hook.py` does.

## Emergency bypass

- `git commit --no-verify` skips every hook silently.
- `VE_SKIP_HOOKS=1 git commit ...` skips this hook and prints a warning.

Only part of what a bypass skips is checked again before a merge. The gate
(`tools/gate.py`) runs `lean/audit.py`, which covers the Lean forbidden tokens,
and the test suite, which runs `lean/VE/Route/frozen.py`. **Nothing downstream
scans for secrets**, and the layer checkers (`tools/check_python_layers.py`,
`tools/check_lean_imports.py`, `tools/check_rust_deps.py`) run only from
`tools/select_tests.py`, not in the gate. After a bypass, run
`tools/hooks/pre-commit` by hand once the commit's content is staged again (for
example after `git reset --soft HEAD~1`), or run those checkers directly.

## Install

Git runs the hook from the root of the worktree that commits, so a relative
`core.hooksPath` makes each worktree run its own branch's `tools/hooks/pre-commit`.
A worktree whose branch has no `tools/hooks/pre-commit` yet runs no hook.

Trial on one worktree only:

```sh
git config extensions.worktreeConfig true
git config --worktree core.hooksPath tools/hooks
```

Every worktree (the setting is in the shared `.git/config`, so it affects all
running workers at once; install only after review):

```sh
git config core.hooksPath tools/hooks
```

Uninstall with `git config --unset core.hooksPath` (add `--worktree` for the
trial install). Setting `core.hooksPath` hides hooks in `.git/hooks/`; there are
none apart from Git's samples today.

The hook needs `python3` (3.11 or later, standard library only) and `git` on `PATH`.
