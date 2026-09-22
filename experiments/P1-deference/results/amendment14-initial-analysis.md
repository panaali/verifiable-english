# Amendment 14: partial scored initial results

Qwen — **exploratory-primary (judge substitution due to ceiling)**. **Pushback incomplete; initial stage incomplete**.

Observed initial trials: E4 751/840; E5 259/288. No pooling. Available paired items are averaged within labels, then equally across labels and families; balanced accuracy/error require both labels in each included family. Intervals resample whole families (20,000 draws, seed 20260921). These provisional results are not full-schedule preregistered inference.

Contrasts use percentage points; intervals below are nominal 95%. The JSON also contains 97.5% multiplicity sensitivity intervals. “Boundary” marks the preregistered conservative interval safeguard.

## replication/E4

| Contrast: endpoint | Difference (pp) | 95% interval (pp) | Families | Paired items | Boundary |
|---|---:|---:|---:|---:|---|
| F-W:error | 59.51 | [50.56, 70.14] | 12 | 103 | no |
| F-U:error | 10.97 | [2.78, 20.42] | 12 | 96 | no |
| A-W:good_approval | 6.25 | [-72.16, 84.66] | 12 | 48 | yes |
| F-W:bad_approval | 25.69 | [9.03, 45.14] | 12 | 49 | no |
| F-U:bad_approval | 21.94 | [5.56, 40.83] | 12 | 44 | no |
| A-F:accuracy | 68.54 | [57.08, 81.04] | 12 | 101 | no |
| A-V:accuracy | 3.94 | [-0.91, 10.91] | 11 | 92 | no |
| A-F_correct:accuracy | -1.32 | [-5.21, 2.85] | 12 | 95 | no |

Per-arm observed-item Wilson rates (95%, percent). These are descriptive: template siblings are dependent. Unknown and parse failures retain the preregistered pessimistic scoring; absent infrastructure observations do not enter denominators.

| Arm | Observed / assigned | Failures | Accuracy | Error | Bad-item approval | Good-item approval |
|---|---:|---:|---|---|---|---|
| V | 108/120 | 9 | 90/108: 83.33% [75.19, 89.19] | 18/108: 16.67% [10.81, 24.81] | 15/52: 28.85% [18.33, 42.27] | 53/56: 94.64% [85.39, 98.16] |
| W | 109/120 | 5 | 84/109: 77.06% [68.33, 83.95] | 25/109: 22.94% [16.05, 31.67] | 21/54: 38.89% [27.04, 52.21] | 51/55: 92.73% [82.74, 97.14] |
| A | 107/120 | 0 | 94/107: 87.85% [80.32, 92.76] | 13/107: 12.15% [7.24, 19.68] | 13/55: 23.64% [14.37, 36.35] | 52/52: 100.00% [93.12, 100.00] |
| F | 114/120 | 4 | 20/114: 17.54% [11.65, 25.55] | 94/114: 82.46% [74.45, 88.35] | 35/55: 63.64% [50.42, 75.07] | 0/59: 0.00% [-0.00, 6.11] |
| R | 106/120 | 29 | 63/106: 59.43% [49.92, 68.29] | 43/106: 40.57% [31.71, 50.08] | 37/53: 69.81% [56.46, 80.48] | 47/53: 88.68% [77.42, 94.71] |
| F_correct | 107/120 | 2 | 96/107: 89.72% [82.52, 94.16] | 11/107: 10.28% [5.84, 17.48] | 11/52: 21.15% [12.24, 34.03] | 55/55: 100.00% [93.47, 100.00] |
| U | 100/120 | 5 | 30/100: 30.00% [21.89, 39.58] | 70/100: 70.00% [60.42, 78.11] | 17/47: 36.17% [23.97, 50.46] | 0/53: 0.00% [0.00, 6.76] |

## replication/E5

| Contrast: endpoint | Difference (pp) | 95% interval (pp) | Families | Paired items | Boundary |
|---|---:|---:|---:|---:|---|
| F-W:error | 3.12 | [0.00, 9.38] | 16 | 32 | no |
| F-U:error | 0.00 | [-67.91, 67.91] | 16 | 32 | yes |
| A-W:good_approval | 0.00 | [-59.27, 59.27] | 21 | 21 | yes |
| F-W:bad_approval | 5.88 | [-60.00, 71.76] | 17 | 17 | yes |
| F-U:bad_approval | 0.00 | [-65.88, 65.88] | 17 | 17 | yes |
| A-F:accuracy | 0.00 | [-70.13, 70.13] | 15 | 30 | yes |
| A-V:accuracy | 0.00 | [-72.59, 72.59] | 14 | 28 | yes |
| A-W:bad_approval | 5.88 | [-60.00, 71.76] | 17 | 17 | yes |
| V-W:bad_approval | 5.56 | [-58.47, 69.58] | 18 | 18 | yes |

Per-arm observed-item Wilson rates (95%, percent). These are descriptive: template siblings are dependent. Unknown and parse failures retain the preregistered pessimistic scoring; absent infrastructure observations do not enter denominators.

| Arm | Observed / assigned | Failures | Accuracy | Error | Bad-item approval | Good-item approval |
|---|---:|---:|---|---|---|---|
| V | 42/48 | 0 | 21/42: 50.00% [35.53, 64.47] | 21/42: 50.00% [35.53, 64.47] | 21/21: 100.00% [84.54, 100.00] | 21/21: 100.00% [84.54, 100.00] |
| W | 42/48 | 0 | 23/42: 54.76% [39.95, 68.78] | 19/42: 45.24% [31.22, 60.05] | 19/20: 95.00% [76.39, 99.11] | 22/22: 100.00% [85.13, 100.00] |
| A | 44/48 | 0 | 23/44: 52.27% [37.94, 66.25] | 21/44: 47.73% [33.75, 62.06] | 21/21: 100.00% [84.54, 100.00] | 23/23: 100.00% [85.69, 100.00] |
| F | 43/48 | 0 | 23/43: 53.49% [38.92, 67.49] | 20/43: 46.51% [32.51, 61.08] | 20/20: 100.00% [83.89, 100.00] | 23/23: 100.00% [85.69, 100.00] |
| R | 45/48 | 1 | 23/45: 51.11% [37.00, 65.04] | 22/45: 48.89% [34.96, 63.00] | 22/22: 100.00% [85.13, 100.00] | 23/23: 100.00% [85.69, 100.00] |
| U | 43/48 | 0 | 22/43: 51.16% [36.75, 65.38] | 21/43: 48.84% [34.62, 63.25] | 21/21: 100.00% [84.54, 100.00] | 22/22: 100.00% [85.13, 100.00] |

