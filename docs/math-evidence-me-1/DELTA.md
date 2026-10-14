# ME-1 delta

- Existing English comparison phrases: **none**. The four generated rows are byte-for-byte the same phrase, relation, and operand order as `main:ve/english.py`; `tests/test_numbers_phrases.py::test_comparison_rows_match_generated_table` pins them. ME-1 registers no `calc` service mode or public command, so its new calculations have no existing public output to compare.
- Trust budget: **DRI signature needed** for S +183 and V +106 (`tools/trust_map.py --check` on the classified ME-1 tree; K +0). Standing ruling R6 does not apply because this is a new Lean core, not replacement of a deleted Python or Rust decision. The classified declarations are in `tools/trust-classes.json`.
