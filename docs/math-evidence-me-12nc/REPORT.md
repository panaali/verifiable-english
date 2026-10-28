No DRI signature is reserved. F2 is fixed; the trust probe passes with zero trusted growth.
HEAD: see `git log --oneline main..HEAD` (local commits only).
The table lookup and its equivalence proof remain as built; this round classifies their helpers and restores the report.
Open: none in this item. The merge train owns final candidate verification.

# me-12nc report

The DRI's 2026-10-27 decision on me-12nb authorized a name-to-definition table before the arithmetic evaluator is exposed by me-12b. `Defs.opEnv` now builds two hash tables once per case. `opEnv_eq_list` proves the table environment equals the reference list lookup for every definition list and name, so `decideBounded` keeps its answer and exact units. `TableExamples.lean` checks duplicate names, near-equal and prefix names, forward references, both function and predicate namespaces, and budget boundaries. The saved arity mutant in [`mutants.json`](mutants.json) made seven guards fail before restoration.

The recheck's F2 probe (`UV_CACHE_DIR=/tmp/ve-uv-cache uv run python tools/trust_map.py --check`) failed before this round: 39 unclassified trusted lines, comprising 22 in `Bounded.lean` and 17 in `TableExamples.lean`. After classification it passes: K +0, S +0, D +0, G +0, unclassified +0, trusted +0 against merge base `d25bc343be0f`. The new table and reference lookup helpers are C, like the existing evaluator; every fixture helper is T. No R16 allowance or ties follow-up is needed. `test_arith_lookup_and_fixture_helpers_are_classified` is the regression test: it checks every declaration in the fixture module and the table helpers through the live trust map.

| Finding | Fix | Regression | Commit |
|---|---|---|---|
| F-ready1 | Saved the arity mutant that breaks seven Lean guards | `VE.Arith.TableExamples`'s `twiceCases` guard | `8da777fc6` |
| F2 | Classified every new lookup and fixture helper; the live trust check now passes | `tests/test_trust_budget.py::test_arith_lookup_and_fixture_helpers_are_classified` | `38609871d` |

The recheck recorded three compiled dense-name runs returning UNKNOWN in 0.77 to 1.48 seconds, under the DRI's two-second condition. Guard 3 in `docs/math-evidence/me-12nb/uncharged-costs.lean` keeps the exact 6,147-unit count and UNKNOWN at one million; its selected test also keeps the parameter-read and large-countdown UNKNOWN guards. No approved statement, public verdict, diagnostic, or unit count changes in this item. There is no user-visible DELTA row; the item-specific DRI decision requires none.

Tests and checks for this round: the before/after F2 probe, the regression test, selected tests, `lake build`, and `lean/audit.py` are recorded in the final response after completion. The three tests listed in `main-known-red.txt` are pre-existing and belong to separate items; this branch does not change them. No Python or Rust product code changed, so the Lean fixture and proof are the relevant cross-language checks. Pilot bytes: zero expected until the later arithmetic wire and pilot audit.
