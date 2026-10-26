# AR-16b: deltas

None. AR-16b moves `ve/readings_verdicts.py` into the package `ve/readings_verdicts/` without changing what any
public operation returns or raises. Every definition moved verbatim (`evidence/verbatim.json`: 38 of 38, 0 errors),
and the corpus A/B over the nine corpora of the lean-first gate found 0 differences (`evidence/ab.json`). Lean and
Rust are unchanged.

The only rows the A/B lists are records unavailable on both sides with identical outputs. None is a delta.
lf-18 and AR-16a already listed records of the same two kinds (`docs/lean-first/b18/DELTA.json`,
`docs/arch/AR-16a/evidence/ab-delta.json`); each is in `evidence/ab-delta.json` with its reason.

| # | Records | What both sides return | Ruling | Test |
|---|---|---|---|---|
| 1 | 14 `pilots/default` `document_check` records, one `translation-companions-with_source_word.ve.md` per constitution pilot run | The same `CheckerUnavailable` (`ReadingsConstruction: ... KeyError`), byte for byte | R7 | `uv run python tools/lean_first_diff.py compare ~/.cache/ve-ar16b-ab/base.jsonl ~/.cache/ve-ar16b-ab/head.jsonl --delta docs/arch/AR-16b/evidence/ab-delta.json` (exit 0, 0 unlisted) |
| 2 | 5 `pilots/default` `document_check` records, the UDHR whole-document pilot of runs 20261014T1800Z, 20261017T1800Z, 20261018T1800Z, 20261021T0600Z and 20261021T1800Z | The recorder's 600 s time-out on both sides | R7 | the same comparison |
