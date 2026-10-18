# speed-abcache: DELTA

No user-visible delta, so this file has no rows. The item changes evidence tooling only (`tools/lean_first_diff.py`,
the new `tools/lean_first_cache.py`). It changes no file under `ve/`, `lean/`, `rust/` or `conformance/`, so no VE
output, diagnostic, verdict, limit or fault order can change. Trust budget: +0 (no Lean change).

What the tooling does differently, none of it a VE output:

- `record` with no `--cache` and `VE_AB_CACHE` unset runs the recorder child exactly as before
  (`test_without_a_cache_record_runs_as_before`). The child's records are serialised by one function, `line`, the
  same canonical JSON as before. The discourse and quantity source digests come from `discourse_source` and
  `quantity_source`, with the same formulas.
- `record --cache` writes the same lines in the same order as a recording without a cache. A segment it takes from
  the cache is the one stored for the same key, and it passes the checks `compare` makes
  (`test_hit_returns_the_records_a_recording_writes`, `test_a_damaged_entry_is_a_miss_and_is_replaced`).
- `compare` is unchanged and never reads the cache. The merge train's full live gate and the nightlies (the plan's
  R2 and R3, not standing rulings) never call `record`.
