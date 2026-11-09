# sc-11 report: the superposed soft route's labels and route condition (rd-9 14.13, first part)

**Cut by the size rule; nothing reserved for the DRI.** This item delivers the label mapping and the route condition
of 14.8 with their fixtures, and moves the rest of 14.8 to **sc-11c** (below). The dispatch is unchanged: no answer
changes, no DELTA row. Spec section 14 came in by cherry-picking 33bc5f48f and ea5b0e420 (docs only).

## Delivered

| 14.8 / 14.9 / 14.11 | Where |
| --- | --- |
| `nodeExcLabels`, `labelImage`, `sdShown`; `labelImage_fst`, `labelImage_snd_mem`, `sdShown_mem`, `sdShown_image`, `fillLabels_choice`, proved | `lean/VE/Readings/SoftSupLabels.lean` |
| `sdSuperposable`, `maxSdCheckWork`, `sdCheckWork`, `sdChecked`, `routeSD`; `routeSD_superposed_iff`, `sdChecked_spec`, `sdCheck_of_admitted`, proved | `lean/VE/Readings/SoftSupWire.lean` |
| W-2, W-2′, W-3, W-4 (label values), W-6, W-6′ (one row per conjunct, `w2`, `pending`), W-13's route values | `lean/VE/Readings/SoftSupWireExamples.lean` |
| Statement compare of 14.8 (both blocks; 10 declarations marked not built) | `tools/check_rd9_sc1_statements.py` |

Each statement equals 14.8's text after whitespace normalisation; `maxSdCheckWork` equals the text as signed on
2026-11-09 (below). The proofs reuse `softLabelledU_labels_nodup`'s pieces (`PacksLabels.lean`), `fmap_*`,
`dualPerm_eq`, `search_spec` and `wellFormedU_of_ndDocTextG`; `SoftSup.lean` and `SoftSupExamples.lean` are unchanged.
W-6′'s per-choice row is a 128-choice document whose readings each fit the vocabulary limit (253 declared names) and
whose 32 choices taking both default readings do not, the first at position 97. W-3's last column ("holds at each
encoded base") and W-5, W-5′ read `supLabel_other`/`supLabel_pull` and move with them.

## OPEN-SC11-7: `maxSdCheckWork` measured and set (DRI decision 2026-11-09 item 1, SIGNED)

`docs/rd-9/sc-11/w13-cpu.md`: compiled Lean on the VM (AMD EPYC 7B12, 32 vCPU, 5-minute load 78 to 108), the route
check on W-13's shape costs about 29 µs of Lean CPU per `sdCheckWork` unit; NSDbig 10 (1024 choices) took 3.67 s,
over R4's 1 s. The figure is measured. As the decision signs, `maxSdCheckWork` = 32,768: past 64 choices a document is
decided in one proof when `sdCheckWork` is within 32,768 (measured: 256 W-13-shaped choices, NSDbig 8, 0.71 s);
`maxChoiceChecks` 1024 stays as a second bound. It can still bind first: a choice charges the superposed premises and
rule nodes, which can be few (`NSDcount`, 2048 choices at 9 units each, work 9,225, enumerated by the count). The
signed spec change (14.8, 14.9 W-13, 14.11, 14.15) is commit b1b2e801f. A wide guard costs more per unit (62 to
468 µs): row sc-11w makes the charge cost-proportional before sc-11b (item 2); admission's own exposure is row
sc-admit-cpu (item 3).

## Not delivered: sc-11c (the size rule)

At the cut the item measured 532 hand-written lines outside generated files and the verbatim spec copy, plus the
17-line signed spec edit. Moved to **sc-11c**, before sc-11b:

- `labelImage_functional` (proved at 8af79f69a), `supLabel_pull`, `supLabel_other`; W-3's base column, W-5, W-5′;
- `SupReplaySD`, `readings_wire_sd_choices` and the five `readings_wire_sd_*_sound` theorems (proved at a4a17192e
  from sc-10b's theorems, applied, not restated);
- the soft runners (`readings-conflict`, `-certificate`, `-model`, the soft row, the verdict scopes), each value read
  once and charged as 14.11 tables it, reached only from `SoftSupWireExamples.lean`; W-13's "a conflict answer in one
  proof".

## Seeded bugs

`docs/rd-9/sc-11/mutants.json`: M1 `labelImage` (W-2 fails), M2 `routeSD` without `sdChecked` (W-6′ fails), M3 a
no-image label shown as `""` (W-3 fails), M4 `sdCheckWork` not charged (W-13's work case fails), M5 `nodeExcLabels`
(R16, W-2′ fails), P1 in the statement checker. Not run: 14.9's W-7 and W-9 bugs (sc-11b's wire fixtures).

## Trust, DELTA, bytes

TRUST: pending the final trust map. DELTA: none (dispatch unchanged). Pilot bytes expected to move: 0 (14.13).

## Next

sc-11c (above), then sc-11w, then sc-11b (the switch).
