# E1 difficulty tuning (dev only)

fol_symbols view, no explanation unless the cell says otherwise. Intervals: 95% bootstrap over the 16 dev base items.

| cell | model | accuracy | false approval | honest acceptance | failures |
|---|---|---|---|---|---|
| single/direct|fol_symbols|none | claude-haiku-4-5-20251001@thinking=0 | 0.97 | 0.02 [0.00, 0.05] (2/109) | 0.94 [0.85, 1.00] (45/48) | 0 |
| single/direct|fol_symbols|none | gpt-5.6-luna@effort=none | 0.89 | 0.16 [0.09, 0.24] (17/109) | 1.00 [1.00, 1.00] (48/48) | 0 |
| single/direct|fol_symbols|attacker | claude-haiku-4-5-20251001@thinking=0 | 0.91 | 0.13 [0.06, 0.20] (14/109) | 1.00 [1.00, 1.00] (48/48) | 0 |
| single/direct|fol_symbols|attacker | gpt-5.6-luna@effort=none | 0.96 | 0.06 [0.02, 0.13] (7/109) | 1.00 [1.00, 1.00] (48/48) | 0 |
| single/direct|fol_symbols|none | claude-haiku-4-5-20251001@thinking=0 | 0.97 | 0.02 [0.00, 0.05] (2/109) | 0.94 [0.85, 1.00] (45/48) | 0 |
| single/direct|fol_symbols|none | gpt-5.6-luna@effort=none | 0.89 | 0.16 [0.09, 0.24] (17/109) | 1.00 [1.00, 1.00] (48/48) | 0 |
| single/direct|ve_strict|attacker | claude-haiku-4-5-20251001@thinking=0 | 0.89 | 0.16 [0.09, 0.23] (17/109) | 1.00 [1.00, 1.00] (48/48) | 0 |
| single/direct|ve_strict|attacker | gpt-5.6-luna@effort=none | 0.85 | 0.21 [0.12, 0.32] (23/109) | 1.00 [1.00, 1.00] (48/48) | 0 |
| single/direct|ve_strict|none | claude-haiku-4-5-20251001@thinking=0 | 0.95 | 0.07 [0.03, 0.13] (8/109) | 1.00 [1.00, 1.00] (48/48) | 0 |
| single/direct|ve_strict|none | gpt-5.6-luna@effort=none | 0.82 | 0.27 [0.16, 0.38] (29/109) | 1.00 [1.00, 1.00] (48/48) | 0 |
| doc4/direct|fol_symbols|none | claude-haiku-4-5-20251001@thinking=0 | 0.70 | 0.00 [0.00, 0.00] (0/109) | 0.02 [0.00, 0.06] (1/48) | 0 |
| doc4/direct|fol_symbols|none | gpt-5.6-luna@effort=none | 0.86 | 0.11 [0.04, 0.18] (12/109) | 0.79 [0.69, 0.88] (38/48) | 0 |
