# me-6cc DELTA: a unit factor's shape comes before its limits

Before is main f58ef91bb, with me-6c's `decodeFactor`; after is this branch. Both are the answers of
`VE.Calc.Units.decode`, the only decoder of a `ve-units@2` environment. No route reads it yet, so nothing a user runs
changes and bytes are 0; `ME-P2` with ME-4 will read it. No Python or Rust file changes.

Order rule (R2): a factor's shape is checked before its limits; limits apply only to literal factors.

The literal shapes are a string and a list that starts with `"sci"`; anything else is `must be a literal`, at every
depth. Inside a calc case nothing moves: the whole-case `Wire.limitFault` still reads `pow`, `lit`, `rounds*` and
`stated` first, and neither it nor its callers change. These rows are every changed answer: the seeded bug
`guard-dropped` in [`mutants.json`](mutants.json) restores main's code, and exactly these four fixtures then differ.

Test ids are `tests/test_calc_units.py::test_fixture[...]`, also checked by the `-- sci` `#guard` of
`lean/VE/Calc/UnitsExamples.lean`.

| # | Input (a unit's `factor`) | Before | After | Fixtures | Ruling |
|---|---|---|---|---|---|
| 1 | `["pow", x, k]` with an integer `k`, `\|k\| ≥ 65` | `ResourceLimit: an exponent exceeds 64` | `InvalidInput: units.<name>.factor must be a literal` | `[sci-shape-pow-65]`; beside it `[sci-shape-pow-64]` (same answer, before and after), `[sci-exponent-64]` read, `[sci-exponent-65]` `ResourceLimit` | R2: a factor's shape is checked before its limits; limits apply only to literal factors |
| 2 | `["lit", s]` with `s` over 40 digits | `ResourceLimit: Decimal literal exceeds 40 digits` | `InvalidInput: units.<name>.factor must be a literal` | `[sci-shape-lit-41]`; beside it `[sci-shape-lit-40]`, `[refuse-digits]` (a 41-digit string, `ResourceLimit`) | R2: a factor's shape is checked before its limits; limits apply only to literal factors |
| 3 | `["rounds…", x, s, …]` with `s` over 40 digits | `ResourceLimit: Decimal literal exceeds 40 digits` | `InvalidInput: units.<name>.factor must be a literal` | `[sci-shape-rounds-41]`; beside it `[sci-shape-rounds-40]`, `[sci-digits]` (`ResourceLimit`) | R2: a factor's shape is checked before its limits; limits apply only to literal factors |
| 4 | an object with `"stated": s`, `s` over 40 digits | `ResourceLimit: Decimal literal exceeds 40 digits` | `InvalidInput: units.<name>.factor must be a literal` | `[sci-shape-stated-41]`; beside it `[sci-shape-stated-40]`, `[refuse-digits]` | R2: a factor's shape is checked before its limits; limits apply only to literal factors |

Unchanged, and pinned: `[["sci", "1", 65]]` (`[sci-shape-nested]`), `["sci", "1", 65, 4]` (`[sci-shape-sci-long-65]`)
and every other non-literal stay `must be a literal`; a `sci` list keeps its limits, malformed ones included
(`[sci-shape-sci-short-41]`, `[sci-digits]`, `[sci-exponent-65]`, `[sci-exponent-first]`), as me-6c's DELTA row 4 says;
a decimal string answers as before (`[refuse-digits]`, `[refuse-digits-40]`).

Trust: K +0, S +0, V +2 in `decodeFactor`, recorded in `docs/trust-baseline.json` as SIGNED by standing ruling R16.
