# sa-nd-atomsb: user-visible deltas

None. Every legacy output is byte-identical: the 62 `norm-defaults` route cases of
`tests/data/route-cases.jsonl` answer the same on the merge base `e63bae651` and on this branch
(`byte-identity.json`, written by `byte_identity.py`: 62 of 62 identical). The legacy definitions are
also proved equal to sa-nd-atoms' bodies by `rfl` (`coneValuesAtO_eq_legacy`,
`enumerateSettledO_eq_legacy`). The new functions have no route or relay yet; WG-6 adopts them in its
own item. Trust growth is 0 lines (`uv run python tools/trust_map.py --check`: K +0, S +0, D +0, G +0,
trusted +0), so no allowance row is needed: there are no rows.
