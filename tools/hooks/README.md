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
`tests/test_precommit_hook.py` holds the hook's own work on a 1,882-path, 21 MB
staged change to under 10 CPU seconds; `lean --deps` adds at most its budget
(below) and two 2 s toolchain probes. `VE_PRECOMMIT_TIMEOUT` replaces all of the hook's
wall-clock waits (the test suite sets it to its hang guard). Run
`tools/hooks/pre-commit --timings` to see per-check times.

| Check | What it rejects | Source of truth |
| --- | --- | --- |
| secrets | In every added or modified staged file, text or binary: a match for private key blocks, AWS, GitHub, Anthropic, OpenAI, Google, Slack, Hugging Face or Stripe live credentials, or a quoted high-entropy `api_key`/`secret_key`/`client_secret`/`access_token`/`auth_token`/`password` value, on a line that is not already a line of that path at `HEAD`; any staged path under `.webapp-private/`; `.env` files (not `.env.example`/`.sample`/`.template`), `id_rsa`-style keys, `.p12`/`.pfx` files | patterns in `precommit.py` |
| layer imports | New outward imports (a module importing a higher layer) that are not in the reviewed ledger, in staged `ve/**/*.py` and `lean/**/*.lean` (Python: the whole file; Lean: the header, which must be in the plain layout below); a staged `lean/**/*.lean` header outside the plain layout, or one the pinned toolchain's `lean --deps` reads differently; a newly added module the layer map does not cover; a missing local Lean import; outward crate dependencies when a `rust/**/Cargo.toml` is staged | the staged `tools/layer_policy.py`, `tools/check_lean_imports.py`, `tools/check_rust_deps.py` and ledgers `tools/layer-exceptions.json`, `tools/lean-layer-exceptions.json` |
| Lean forbidden tokens | In staged files under `lean/`: every whole word the staged `lean/audit.py` forbids (today `sorry`, `sorryAx`, `admit`, `axiom`, `unsafe`, `native_decide`, `implemented_by`, `partial`, `opaque`, `extern`), in comments and strings too, as the audit does. In other staged `.lean` files: `sorry`, `sorryAx`, `admit` or `axiom` in code | the staged `lean/audit.py` |
| frozen files | A staged change to a file listed in `lean/VE/Route/frozen-sources.sha256` unless the staged inventory records the staged file's SHA-256; a deleted file that is still listed; a new `lean/VE/**/*.lean` module that is not listed; a changed `lean/Main.lean` that no longer matches `MAIN_BASE` in `lean/VE/Route/frozen.py`. A staged inventory or `frozen.py` re-checks every entry | `lean/VE/Route/frozen.py` rules |
| wire contract | When wire contract sources or the generated English table change, `tools/wire_contract.py --check` must pass on a staged snapshot within 30 s (`VE_PRECOMMIT_TIMEOUT` replaces it; a value that is not a positive number of seconds blocks) | staged `ve/`, `tools/wire_contract.py`, `lean/audit.py`, and `docs/spec/soft-norms-wire-table.md` |

A Lean header is in the plain layout when it is one `import A.B.C` per line at
column 0 (ASCII name parts, nothing else on the line), with only blank lines,
full-line `--` comments and `/- ... -/` block comments between the imports; a
block comment may not contain `/-` and nothing may follow its closing `-/` on
that line. The header ends at the first other line (a declaration, a `/--` or
`/-!` doc comment, ...). Any other layout Lean might read differently, such as
`/-/-/import X`, `import A import B`, `import X -- c`, `prelude`, `module`,
`public import` or `«»` names, is rejected rather than interpreted. When the
toolchain pinned by the staged `lean/lean-toolchain` is installed (elan is
asked; nothing is ever downloaded), `lean --deps` must also read the same
imports; it gets 3 s in total, and headers it has not reached by then rely on
the grammar alone. `tools/check_lean_imports.py` applies the same rules to the
whole tree.

The hook checks only what a commit adds. Existing drift, such as stale ledger
entries, `.importlinter` sync or modules that were unmapped before this commit,
is left to the full checkers.

Known drift on `ve-integration` as of 390dabe5, left open here because each
module needs a layer decision: `tools/check_python_layers.py` reports 14
unmapped modules (`ve.alternatives`, `ve.assurance`, `ve.quantity_admission`,
`ve.report_english`, `ve.reports`, `ve.reports_route`, `ve.rights`,
`ve.rights_route`, `ve.soft_route`, `ve.softnorms`, `ve.speech_acts`,
`ve.speech_document`, `ve.speech_english`, `ve.units`). The hook skips layer
checks on them until they are mapped in `tools/layer_policy.py`, so outward
imports added to them go unnoticed.

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
(`tools/gate.py`) runs `lean/audit.py` and the wire contract check, which cover the Lean forbidden tokens and wire table respectively,
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

The hook needs `python3` (3.11 or later) and `git` on
`PATH`; `elan` (or the pinned `lean`) on `PATH` adds the `lean --deps` check.
