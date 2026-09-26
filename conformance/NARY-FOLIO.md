# FOLIO v2 n-ary witness audit

`UV_CACHE_DIR=/tmp/ve-uv-cache uv run python -m conformance.nary_folio` reads the
ignored, pinned `tasksource/folio` v2 train and validation files described in
`data/README.md`. Each pair's symbolic gold is parsed, translated to the
single-user-sort `nary@0` fragment, printed in strict VE, and parsed back.
The translation treats numeric-looking names as opaque entity constants; it
does not claim arithmetic or integer time.

- 216 unique sentence pairs contain an atom of arity greater than two.
- 189 gold formulas translate and strict-parse without semantic repair.
- 27 do not: 10 malformed gold expressions, 11 free variables, 5 overloaded
  predicate arities within one formula, and 1 shadowed variable. The script
  reports each ID and reason. Counting repaired expressions as direct parses
  would misstate what the source says.
- On the frozen 30-item sample, direct fit rises from 26 to 28. The new items
  are `e532:c` and `s367:p0`; the latter's gold still omits “every morning,”
  so this is a language-fit count, not an endorsement of the gold's fidelity.

The binding 216/216 acceptance target is open pending reviewed corrections to
the 27 source formulas or a clarified target that permits gold repairs.
