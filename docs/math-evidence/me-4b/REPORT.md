# me-4b: stopped at the prerequisite (ap-4 not on main)

Status: **not built.** The task's prerequisite is unmet, and the task says: "Prerequisite: ap-4 must
have merged (protocol queue, SYNTHESIS 4.2) ... If ap-4 is not on main when you start, stop and
report." This report records the stop. No product code, test, fixture, generated file, plan or spec
copy is in this branch.

## Evidence (main at 5c6a54444, checked 2026-11-04)

- ap-4 (part 3 of the ap-4 split: the act-readings mode, its relay and the admission hook) has not
  merged. Its backlog row is `"status": "ready"`, state "path lean/VE/Service/Protocol.lean in
  flight on feature/ci-2". No `feature/ap-4` branch exists, and main's
  `lean/VE/Service/Protocol.lean` has no act-readings mode.
- Only ap-4a (`56cc350e5`) and ap-4b (`3e2f97e38`) are on main; the ap-4 row comes after them.
- SYNTHESIS 4.2's queue for `Protocol.lean` and `service_schema.py` puts ME-4's `Handles` kind last,
  after AP-4.
- `feature/ci-2` is in flight on `lean/VE/Service/Protocol.lean`, the file this item must edit.

## Plan rows

| Row | Delivered |
|---|---|
| (1) `Handles` data kind, `"source"` handle, digest recheck, plan 2.5 limits | no: blocked on ap-4 |
| (2) relay by SHA-256, relay lint, binding inventory, schema | no: blocked on ap-4 |
| (3) `tests/test_calc_tables.py`, `tests/data/calc/`, V-5 from the committed file | no: blocked on ap-4 |
| (4) spec 4.4 spans, `spanMatches_iff`, V-12 | no: blocked on ap-4 |

## Seeded bugs, trust, DELTA

None: there is no changed product code, so no seeded bugs, no trust growth and no user-visible
delta (no DELTA.md). Pilot bytes moved: 0.

## Next

Restart me-4b once ap-4 has merged to main (after ci-2's `Protocol.lean` edit). Rows r-10a and
r-10c (rights) stay blocked until then.
