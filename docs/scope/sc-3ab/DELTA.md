# User-visible deltas (sc-3ab)

No user-visible delta, so the table has no row:

- **Trust budget: +0.** `uv run python tools/trust_map.py --check` against the merge base `68f18dcdc` passes with
  K +0, S +0 and untied V +0 (G +11, all reject-only G[R]: `kindOf`, `defSpans` and `admitBlock`'s step 7 and step 8
  lines). `coveredLayout`'s two changed lines replace two refusals, so its line count is unchanged. No R16 allowance
  is recorded, so no ties-pass row is needed.
- **No caller.** No route, service mode or other Lean module calls `VE.Scope.govern` or `VE.Scope.governFast` until
  the document mode (SC-1b). They now admit an anchor or label reach and a block with anchors as spec 4.2 states,
  where sc-1ac refused them with `UnsupportedProfile: scope@0 anchor reach requires SC-3a`, `... label reach ...`
  and `... anchors require SC-3a`. Those texts appear in no answer.
- **No approved statement changes.** `anchor_reach_iff` and `label_reach_iff` equal spec 5.5; all 6,403 compiled
  statements at `68f18dcdc` are unchanged (`docs/scope/sc-3ab/statement-diff.txt`). `title_identity` is not built:
  it waits for the DRI (REPORT, statement gate).
- **No other file changes behaviour.** The other edits are the trust side table, docs and generated inventories.
