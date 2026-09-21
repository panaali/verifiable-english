BRANCH

`codex/fluent`; merged `codex/views` at `eea6b51` and `ve-integration` at `12538d8`
in that order (merge commits `a9d5759` and `d45f658`).

SUMMARY

- Fluent v2 uses the reviewed validator, shared limits/case/punctuation, identical legend, length helper, and CLI.
- Optional identity-bound negative templates must exactly negate an accepted positive; false negations produce stable lint codes and explicit fallback.
- Sort-letter sequences are disjoint across sorts and document statements, deterministic for shared initials, and mapped to sorts in every legend.
- Preserved search/non-vacuity/exit-code fixes; reconciled the grammar CLI test and Lean's display-metadata decoder.
- [Six examples in all five views plus the complete legend](fluent-examples.md) are committed with executable source fixtures.

VERIFY

Run from the `ve-codex-fluent` worktree:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent
uv run --frozen python -m pytest -q
uv build --out-dir /private/tmp/ve-fluent-dist
uv run --frozen python examples/fluent_views.py > /private/tmp/ve-fluent-examples.md
diff -u docs/fluent-examples.md /private/tmp/ve-fluent-examples.md
git merge-base --is-ancestor eea6b51 HEAD
git merge-base --is-ancestor 12538d8 HEAD
git diff --check
```

- Complete suite: **479 passed, 2 skipped in 70.28s**. It includes Lean build,
  differential conformance, and transitive axiom audit, argument/grammar/search
  regressions, 68,460 seeded all-view inverse checks, negative-template attacks,
  all 32 sorts sharing an initial, and multiple-statement name allocation.
- Source and wheel distributions built successfully. An isolated `python -I`
  import from the built wheel passed five-view rendering, exact negative
  templates, byte-identical legends, and length measurement on the six examples.
- The generated example report matches the committed file byte-for-byte;
  both merged tips are ancestors and the whitespace check is clean.
- The initial full run exposed a grammar test expecting resource exit 2; its
  expectation now correctly preserves the reviewed resource exit 4.

GAPS

The two optional backend tests skipped because `llguidance` and `xgrammar` are
not installed. Fluent injectivity is checked through independent structural
inverse tests; it is not a Lean theorem or human-readability result. Negative
template validation proves the prescribed lexical derivation, not that a
positive alias or description truthfully names a real-world relation. Rejected
templates remain quoted identity-bound metadata, never selected display text.

PLAN CHANGES

None.
