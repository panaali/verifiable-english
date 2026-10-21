# ap-1c DELTA

None. The item adds theorems and their lemmas only (`lean/VE/Acts/LexicalProofs.lean`, `check_extends` in
`lean/VE/Acts/Compat.lean`). No definition, diagnostic, limit, verdict, field or mode changes. The answers of
`check`, `canonicalAct` and every decoder are those of the merge base `c5197da78`.

Trust: `uv run python tools/trust_map.py --check` on the final HEAD gives K +0, S +0, D +0, G +0, trusted +0 against
`c5197da78`. The four new definitions (`splitL`, `out`, `wordsL`, `pieceTok`) are proof helpers, class `P` in
`tools/trust-classes.json`, so no R16 allowance is recorded and no ruling is needed.
