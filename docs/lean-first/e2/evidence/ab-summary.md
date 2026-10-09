# E2.5 corpus A/B

Base: `9aaf918d538a35e63d64a7c5abc86bbcfbb87472`, the parent of the first E2 implementation commit. Head: the Python-authoritative shadow implementation committed at `5221c1c0`, prepared from reviewed merge `9cc8418d`; the later test-only fix commit `2aad9b8f` changes no public corpus outcome. Both sides ran `tools/lean_first_diff.py record` over the same frozen inputs, followed by `compare`. The recorder checks corpus digests and complete case sets. The two raw JSONL recordings for each run are saved here as deterministic gzip files; decompress them before invoking `compare` again.

| Corpus and authority | Records per side | Same | Wording | Order | Verdict | Availability |
|---|---:|---:|---:|---:|---:|---:|
| Conformance, Python and Lean | 39,612 | 39,564 | 48 | 0 | 0 | 0 |
| Probe, Python and Lean | 18,870 | 18,869 | 1 | 0 | 0 | 0 |
| Pilots | 303 | 302 | 0 | 0 | 0 | 1 |
| Readings | 1,137 | 1,137 | 0 | 0 | 0 | 0 |
| Discourse | 6,350 | 6,350 | 0 | 0 | 0 | 0 |
| Rights | 2,500 | 1,938 | 224 | 148 | 190 | 0 |
| Quantity, Python and Lean | 25,726 | 25,582 | 94 | 44 | 6 | 0 |
| **Total** | **94,498** | **93,742** | **367** | **192** | **196** | **1** |

The conformance comparison is [ab-conformance-compare.json](ab-conformance-compare.json); its 48 wording records map to 15 exact text pairs in [ab-conformance-delta.json](ab-conformance-delta.json). [ab-other-compare.json](ab-other-compare.json) holds **every one of the 708** other changes with both complete outcomes, source case, operation and class. Those 708 rows are unlisted by a signed delta: they are evidence of failure, not accepted changes.

The single availability row is a pilot `readings/s1.ve.md` check: the base reached the recorder's 600 second timeout, while the head returned a report. All 190 rights verdict rows change from `UnsupportedProfile` on the base's `readings@1` headed document to a returned report on the head. The six quantity verdict rows are four certificate calls changing from `false` to `ResourceLimit`, on both authorities, and two countermodel outputs with changed error structure. The 192 order rows comprise 148 rights `InvalidInput` to `UnknownSymbol` outcomes and 44 quantity error class changes. Wording rows include added error class prefixes. These are grouped in [DELTA.md](../DELTA.md); exact outcomes remain in the comparison JSON.

The result fails GE2 preservation. The verdict and availability changes have no DRI signature. The readability replay separately fails section 2.10, so Python remains English authority and Lean runs in shadow.
