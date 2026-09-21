# View covariates on `dev` (158 candidates)

Tokens are `\w+|[^\w\s]` matches (words and single symbols), not model tokens.

| view | mean chars | median chars | mean tokens | median tokens |
|---|---|---|---|---|
| fol_symbols | 89.6 | 89 | 39.5 | 38 |
| fol_keywords | 108.1 | 107 | 39.5 | 38 |
| ve_strict | 120.6 | 119 | 37.4 | 35 |
| ve_natural | 136.6 | 130 | 41.7 | 38 |
| ve_fluent | 117.4 | 115 | 28.0 | 27 |

## ve_fluent contraction

- 74/158 (47%) use a relative-clause guard on a universal (`for every N V that ...` or `such that ...`).
- 61/158 (39%) contain an uncontracted `if (...)` or `such that (both ...)`.
- By label: good: guard 20/48; bad: guard 54/110
