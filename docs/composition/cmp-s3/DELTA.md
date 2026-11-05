# cmp-s3: user-visible deltas

None. This item changes no answer. No executable, mode, relay or Python file reads the new definitions:
`grep -rn RightClauses lean/VE --include=*.lean` finds only `lean/VE/RightClauses/*`, `lean/VE.lean` and
`lean/VE/Audit.lean`. The profile table, `ve/profile_table.json` and every Python file are as on main, so a document
with or without `right-clauses@0` gets today's answer, byte for byte.

The widening S3 brings, "documents that enable `right-clauses@0` with `rights@0` are read by the new head", arrives
with the head's mode and the registration in cmp-s3b. The DRI signed that row in advance
(reviews/dri-decisions-20261031-spec-right-clauses.md item 2). cmp-s3b records it with K10 and the 9.3 profile-off
byte-identity test as its evidence. The registration waits for that item (docs/composition/cmp-s3/QUESTIONS.md Q2).
Registered alone, it would change a profile-on refusal text that the signed row does not cover.

| Delta | Detail | Evidence | Ruling |
|---|---|---|---|
| Trust budget | S +13: lean/VE/RightClauses/Relation.lean (`totalF`, `relPremisesLabelled`, `relPremises`, `clauseSlotLabelled`, `clauseSlot`); K +0 | `uv run python tools/trust_map.py --check`: PASS; mutants.json (9 killed), trust-mutants.json (32 killed, 0 survivors) | SIGNED by standing ruling R16 (DRI-RULINGS.md), cmp-s3, 2026-10-18 |

## Statement changes (not answer deltas)

Signed by the DRI 2026-11-04 (reviews/dri-decisions-20261104-cmp-s3.md). Each comes with a mechanised counterexample
for the statement as written, kept as a `#guard` in lean/VE/RightClauses/Examples.lean:

- `clauseSlot_labelled` (spec 8.4) gains `(hl : VE.Compose.Labelled.wellLabelled (limPremisesLabelled D.doc) = true)`
  (Q3, option B1). `cxDoc` satisfies both of the spec's hypotheses and repeats a `Lim_D` label.
- `elaborate_plain` (spec 8.5) gains `(hd : PlainOnWire D)`: every plain guard is within `VE.Limits.maxDepth` and
  `VE.Limits.maxNodes` as the wire counts them (Q1, option A1). The theorem is cmp-s3b's. `notChain` shows that the
  rights decoder reads a depth-64 clause but not that clause under `plain`'s `and`.
