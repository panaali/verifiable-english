# sa-nd-atoms: user-visible deltas

None. Every legacy output is byte-identical: the 62 `norm-defaults` route cases of
`tests/data/route-cases.jsonl` answer the same on the merge base `09fca5013` and on this branch
(`byte-identity.json`, written by `byte_identity.py`: 62 of 62 identical). The new functions have no
route or relay yet; DF-5, JT-4, AA-1 and WG-6 adopt them in their own items. Trust growth is 0 lines
(`python3 tools/trust_map.py --check`: K +0, S +0, untied [V] +0), so no allowance row is needed: there
are no rows.
