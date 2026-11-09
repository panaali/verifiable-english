# cmp-s3-cfr-1: user-visible deltas

With the profile off, nothing changes. The rights mode's answers to the 28 recorded rights route cases are
byte-identical to the base build's (saved digests, docs/composition/cmp-s3-cfr-1/profile-off.json, base 6db6ee16d).
K10's line is refused with today's `fields do not match` text. So no row below is a changed record of spec 9.3: the
row the DRI signed ahead for this item (reviews/dri-decisions-20261109-lp0801.md item 1) is not needed.

| Delta | Detail | Evidence (negative tests) | Ruling |
|---|---|---|---|
| Documents that enable `right-clauses@0` with `rights@0` are read by the new head | The `clauses-elaborate` mode reads them (spec 4.1, 7). `right-clauses@0` joins the profile table's environment list. Lean's environment mode gates a list with it by the whole table, as for `readings@1`, so such an environment is accepted, and one without `rights@0` gets the dispatcher's `UnsupportedProfile: right-clauses@0 requires rights@0` (D33, D41, D52) in place of `Unsupported profile right-clauses@0`. | `test_right_clauses_k10_profile_off`; `test_right_clauses_profile_off_regression` (profile off: every recorded rights answer byte-identical to the saved base digests; profile on with `elided: []`: each document elaborates to itself or is refused with the profile-off text). REPORT "Seeded bugs" shows the regression failing on a seeded break. | SIGNED by the DRI 2026-10-31 (reviews/dri-decisions-20261031-spec-right-clauses.md item 2) |
| Trust budget | K +0, S +16, untied [V] +118 (per file in REPORT "Trust") | `uv run python tools/trust_map.py --check`; trust mutants (REPORT) | SIGNED by standing ruling R16 (DRI-RULINGS.md), cmp-s3-cfr-1, 2026-10-18 |

## Statement change (not an answer delta)

`elaborate_plain` (spec 8.5) has the hypothesis `(hd : PlainOnWire D)` after `hp`: W1's budgeted decoder reads every
structured line's plain guard back within `VE.Limits.maxDepth` and `maxNodes`. SIGNED by the DRI 2026-11-04
(reviews/dri-decisions-20261104-cmp-s3.md Q1 A1). Its counterexample for the statement as written is `notChain` in
lean/VE/RightClauses/Examples.lean. `decode_unstructured` is word for word.
