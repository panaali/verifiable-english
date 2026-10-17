# RD-7 user-visible delta ledger

The comparison base is f98183bf5ff518c14e0cbdcf2950cdaf7736deeb (the merge base with main). The corpus A/B
recorded the base and the code head 074f96d3fca99843b6c0208bcb9c0aedb8410b25; the later commits on the branch change
only `docs/readings-defaults/rd7/`. Saved evidence: [ab-compare.json](evidence/ab-compare.json) (the comparison,
with both recordings' digests), [ab-delta.json](evidence/ab-delta.json) (the listed rows below) and
[udhr-serial.json](evidence/udhr-serial.json) (serial reruns of the whole-UDHR documents).

## Corpus A/B

100,401 records over the seven required corpora and the document and norm-defaults corpora: 100,383 identical,
7 wording rows listed, 11 unavailable on both sides listed, 0 unlisted. No verdict, order or availability difference.

| Corpus | Records | Outcome |
|---|---:|---|
| Probe matrix (Lean, Python) | 18,870 | identical |
| Conformance (Lean, Python) | 39,612 | identical |
| Quantity (Lean, Python) | 25,726 | identical |
| Readings | 1,137 | identical |
| Discourse | 6,350 | identical |
| Rights | 2,500 | identical |
| Document | 3,632 | identical |
| Norm defaults | 2,020 | identical |
| Pilots (every `.ve.md` on every `pilot/*` branch) | 554 | 536 identical; 7 wording (W1); 11 unavailable on both sides (U1, U2) |

## Rows

| Row | Class | Difference | Disposition |
|---|---|---|---|
| W1 | wording | Seven constitution senses probes fail on both sides with the same `Cannot read sense pack` error; the texts differ only in the recorder's scratch directory (`/tmp/rd7-ab/base.pilots/pack.json` against `/tmp/rd7-ab/head.pilots/pack.json`) | Not a product difference: a recorder path. Listed as one wording pair in ab-delta.json; RD-3 and RD-6b list the same pair. |
| U1 | unavailable on both | Seven `probes/companion/translation-companions-with_source_word.ve.md` documents (constitution runs 2026-10-10 to 2026-10-17): `CheckerUnavailable: ReadingsConstruction ... KeyError` on both sides, byte-identical | SIGNED by standing ruling R7 (identical outputs on both sides). Pre-existing on the base; RD-7 neither causes nor fixes it. |
| U2 | unavailable on both | Four whole-UDHR `experiment-whole/translation-whole.ve.md` documents (runs 2026-10-12 0600Z and 1800Z, 2026-10-14 1800Z, 2026-10-17 1800Z). In the parallel recording each side was a Rust timeout or the recorder's 600 s limit; the 2026-10-17 document gave `{"timeout": 600}` on both sides. The first three were rerun one at a time with `VE_RUST_TIMEOUT=60`: each side is `CheckerUnavailable: Rust checker failed ... timed out after 60 s`, identical once the checkout path and the elapsed seconds are normalised (udhr-serial.json: 11–18 min and 18–30 GB per run on either side) | SIGNED by standing ruling R7 (unavailable on both sides; the outputs are identical up to the checkout path and the timer reading). |
| T1 | trust budget | K +0, S +0, V +603: from 37,154 to 37,757 V lines across five recorded allowances in docs/trust-baseline.json | SIGNED by standing ruling R6 (DRI-RULINGS.md): the Lean superposed fold, conditions, diagnostics, English plan, scoped model proposals, checked dead readings and shared conflict and model replay replace the Python decisions listed in evidence/deletion-ledger.json. Checked by `tools/trust_map.py --check`, the Lean build, the audit and the seeded proof and limit mutants. |
| E1 | wording (retained) | "reading N" is the reading's own sentence, as RD-1 made it; RD-7 does not change it | DRI item-specific ruling in readings-defaults-dri-note.md; checked by `tests/test_readings_defaults_english.py` and the identical readings and pilot corpora. |

M1 to M20 of S2a keep their verdicts and English (`tests/test_readings_s2_document.py`); they are `none` in this
ledger. No row needs a new DRI signature: there is no availability, verdict or order change.

`python -m tools.evidence ab` reports the 11 U rows as "an unlisted or unavailable result", because it refuses any
record unavailable on both sides as evidence of preservation. Those records are therefore not counted as
preserved here. They are listed with their reasons and signed under R7 only as non-regressions.
