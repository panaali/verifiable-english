# Git hooks

`pre-commit` runs fast checks on the **staged** content of a commit (the index,
never the working tree). It runs no tests and no builds: the gate, fix loops and
merge train still run the full checkers. A typical commit takes well under a
second; `tests/test_precommit_hook.py` holds a 1,765-path, 18 MB staged change
to under 10 s. Run `tools/hooks/pre-commit --timings` to see per-check times.

| Check | What it rejects | Source of truth |
| --- | --- | --- |
| secrets | Added lines that look like private key blocks, AWS, GitHub, Anthropic, OpenAI, Google, Slack, Hugging Face or Stripe live credentials, or a quoted high-entropy `api_key`/`secret_key`/`client_secret`/`access_token`/`auth_token`/`password` value; any staged path under `.webapp-private/`; `.env` files (not `.env.example`/`.sample`/`.template`), `id_rsa`-style keys, `.p12`/`.pfx` files | patterns in `precommit.py` |
| layer imports | New outward imports (a module importing a higher layer) that are not in the reviewed ledger, in staged `ve/**/*.py` and `lean/**/*.lean`; a newly added module the layer map does not cover; a missing local Lean import; outward crate dependencies when a `rust/**/Cargo.toml` is staged | `tools/layer_policy.py`, `tools/check_lean_imports.py`, `tools/check_rust_deps.py`, the staged ledgers `tools/layer-exceptions.json` and `tools/lean-layer-exceptions.json` |
| Lean forbidden tokens | In staged files under `lean/`: every whole word `lean/audit.py` forbids (`sorry`, `sorryAx`, `admit`, `axiom`, `unsafe`, `native_decide`, `implemented_by`, `partial`, `opaque`, `extern`), in comments and strings too, as the audit does. In other staged `.lean` files: `sorry`, `sorryAx`, `admit` or `axiom` in code | `lean/audit.py` |
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

Either way, the gate still runs the full checks before a merge.

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
