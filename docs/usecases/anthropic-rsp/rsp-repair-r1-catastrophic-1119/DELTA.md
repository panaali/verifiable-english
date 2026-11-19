# rsp-repair-r1-catastrophic-1119 delta

No rows: this item has no user-visible delta. Every keyed answer of the RSP case is unchanged:
`uv run python usecases/anthropic-rsp/run.py --check` exits 0 on the item's code ("110 / 126", /tmp/r1-run.log),
so `usecases/anthropic-rsp/results.json` is untouched. The change adds source text to one description (the legend of
D2's footnote-1 constant `existential_threats`) and removes one `loss` entry from the D2D3 accounting line. D2 is still
admitted with the same classes, 16 might cells and 0 leads cells. Only its `environment_id` in the saved
`docs/usecases/safetyfw/anthropic-rsp/stage0.json` moves, because the id hashes the description. This follows the
precedent of rsp-b-repair-1115's legend quotes, which add source text and change no answer.

| Change | Before | After | Evidence | Ruling |
|---|---|---|---|---|
