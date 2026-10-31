# AR-21: deltas

None. AR-21 adds one proof module (`lean/VE/Closure/CoreEquiv.lean`) and changes no definition, no existing
statement, no Python and no Rust. The checker binaries are unchanged (`lean/checkers.lock` is byte-identical to the
base's), every kept Lean statement is byte-identical (`evidence/statements.json`), and the corpus A/B over the nine
corpora of the lean-first gate found 0 differences: 100,507 records the same, and the base and head recordings are
byte-identical (`evidence/ab.json`).

The only rows the A/B lists are records unavailable on both sides with identical outputs. None is a delta. Each is in
`evidence/ab-delta.json` with its reason.

| # | Records | What both sides return | Ruling | Test |
|---|---|---|---|---|
| 1 | 15 `pilots/default` `document_check` records, one `translation-companions-with_source_word.ve.md` per constitution pilot run | The same pre-existing `CheckerUnavailable` (`ReadingsConstruction: ... KeyError`), byte for byte | R7 | `uv run python -m tools.evidence ab ... --delta docs/arch/AR-21/evidence/ab-delta.json` (PASS, 0 unlisted) |
