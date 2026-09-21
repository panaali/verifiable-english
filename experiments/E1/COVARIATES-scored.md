# View covariates on `scored` (874 candidates)

Tokens are `\w+|[^\w\s]` matches (words and single symbols), not model tokens.

| view | mean chars | median chars | mean tokens | median tokens |
|---|---|---|---|---|
| fol_symbols | 92.1 | 91 | 39.6 | 38 |
| fol_keywords | 111.4 | 110 | 39.6 | 38 |
| ve_strict | 123.4 | 122 | 37.2 | 37 |
| ve_natural | 142.7 | 139 | 42.3 | 40 |
| ve_fluent | 120.4 | 116 | 27.8 | 26 |

## ve_fluent contraction

- 467/874 (53%) use a relative-clause guard on a universal (`for every N V that ...` or `such that ...`).
- 236/874 (27%) contain an uncontracted `if (...)` or `such that (both ...)`.
- By label: good: guard 148/280; bad: guard 319/594
