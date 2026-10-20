# AR-16a: deltas

None. AR-16a moves `ve/document.py` into the package `ve/document/` without changing what any public operation
returns or raises. Every definition moved verbatim (`evidence/verbatim.json`: 63 of 63, 0 errors), and the
corpus A/B over the nine corpora of the lean-first gate found 0 differences (`evidence/ab.json`). Lean and Rust
are unchanged.

The only rows the A/B lists are records unavailable on both sides with identical outputs. None is a delta.
lf-18 already listed the same pre-existing records (`docs/lean-first/b18/DELTA.json`); each is in
`evidence/ab-delta.json` with its reason.

| # | Records | What both sides return | Ruling | Test |
|---|---|---|---|---|
| 1 | 11 `pilots/default` `document_check` records, one `translation-companions-with_source_word.ve.md` per constitution pilot run | The same `CheckerUnavailable` (`ReadingsConstruction: ... KeyError`), byte for byte | R7 | `uv run python tools/lean_first_diff.py compare ... --delta docs/arch/AR-16a/evidence/ab-delta.json` (exit 0, 0 unlisted) |
| 2 | 3 `pilots/default` `document_check` records, the UDHR whole-document pilot of runs 20261014T1800Z, 20261017T1800Z and 20261018T1800Z | The recorder's 600 s time-out on both sides | R7 | the same comparison |
