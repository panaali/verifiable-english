# AR-20: deltas

None. AR-20 merges copies in Lean without changing what any public operation returns or raises: the two
document decoders call the one they copied (same checks, order, messages and limits), the two Paths modules
re-export one shared module under their old names, `bind_ok` has one owner with two aliases, and the two
canonical JSON encoders share their cases. Every kept Lean statement is byte-identical
(`evidence/statements.json`), and the corpus A/B over the nine corpora of the lean-first gate found 0
differences; the base and head recordings are byte-identical (`evidence/ab.json`). Python's product code and
Rust are unchanged.

The only rows the A/B lists are records unavailable on both sides with identical outputs. None is a delta. Each
is in `evidence/ab-delta.json` with its reason.

| # | Records | What both sides return | Ruling | Test |
|---|---|---|---|---|
| 1 | 14 `pilots/default` `document_check` records, one `translation-companions-with_source_word.ve.md` per constitution pilot run | The same pre-existing `CheckerUnavailable` (`ReadingsConstruction: ... KeyError`), byte for byte | R7 | `uv run python -m tools.evidence ab ... --delta docs/arch/AR-20/evidence/ab-delta.json` (PASS, 0 unlisted) |
| 2 | 8 `pilots/default` `document_check` records, the whole-UDHR pilot document of runs 20261012T0600Z, 20261012T1800Z, 20261014T1800Z, 20261017T1800Z, 20261018T1800Z, 20261021T0600Z, 20261021T1800Z and 20261026T1800Z (the last published during the A/B and recorded on both sides by `pilot_rerun.py`, `evidence/new-pilots.json`) | The recorder's 600 s time-out on both sides | R7 | the same comparison; `evidence/pilot-rerun.json` |
