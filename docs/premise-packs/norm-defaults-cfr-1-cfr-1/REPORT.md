# norm-defaults-cfr-1-cfr-1: the norm-defaults mode's manifest binds every kind it answers (REPORT)

Summary: READY FOR REVIEW. The `ve_service`/`norm-defaults` bindings of ve/assurance-manifest.json now cover the
10 kinds the mode answers only through its `norms.json#/row` fallback, each with the binding its answering path
already declares. The coverage test reads the full answered set from the rendered schemas. No Lean, Rust or `ve/*.py`
change; trust +0; no DELTA row; no DRI signature reserved.

Source: regrade #3 (ndc1-F4, C->A, cross-family Astra 11-11; reviews/l1-c-regrade-norm-defaults-c-20261111.md) and
the DRI ruling "BIND, not reword" (reviews/dri-decisions-20261111-portfolio1500.md item 5, third bullet). Base
175814252d (`git merge-base HEAD main`).

SIZE: 188 product (manifest binding values, copied by script from the bindings they mirror), 101 tests (86 in
tests/test_norm_defaults_response_binding.py, 15 probe lines in conformance/binding_probes.py), about 90 other
hand-written lines (this REPORT, mutants.json, 4 changed lines in the cfr-1 REPORT). Generated: docs/spec/assurance-manifest.md
and seven docs/codemap files (regen; the codemap was already stale on main).

## The answered set, read from the rendered schemas

`norm-defaults.json#/row` answers a case on the norm-defaults path by its own `kind` table (13 kinds) and hands every
other case to `norms.json#/row`. That row answers a case on the norms path by the norms `kind` table and route's
`evaluate`, `countermodel` and `certificate` (plus a kindless case, an evaluation), and hands every other case to
`route.json#/row` (route's `kind` table). The kinds the mode answers beyond its own table are therefore 10:

- from the norms table: `background`, `norms-certificate`, `norms-conflict`, `norms-elaborate` (Astra's four);
- from route's table: `evaluate`, `countermodel`, `certificate`, `dependency-order`, `bundle`, `label`.

(`admission` and `acts-elaborate` are in all relevant tables and were already bound.) Before any binding was
written, 8 of the 10 answered `ok` through the built `ve_service` in mode `norm-defaults`, with the same fields as on
their norms or route path (`relay.decide` probe). The 4 route rows among them also passed their route bindings'
`row_problem`. The `evaluate` and `countermodel` probes need the Rust release binary to build, and it is missing in
this worktree. The final selected run checks all 10 through `test_every_lean_binding_routes_its_operation` and
`test_every_real_answer_is_counted_and_indexed`.

The ruling names Astra's four. The six route kinds are the same defect one level down: binding only four would leave
`test_the_manifest_lists_every_kind_the_mode_answers` claiming more than it checks, which is the finding itself.
They are bound here too (the same rule, six more bindings and probes).

## Deliverables

| # | Task row | Delivered by |
|---|---|---|
| 1 | The manifest's `ve_service`/`norm-defaults` bindings cover the delegated kinds with the bindings the norms path already applies | ve/assurance-manifest.json: one new `ve_service`/`norm-defaults` binding per kind, in the operation that already binds that kind on its path: `norms.elaborate`, `norms.conflict`, `norms.certificate` (copied from the `ve_service`/`norms` binding), `definitions.elaborate` (`background`, `dependency-order`), `evaluate`, `countermodel.check`, `certificate.check`, `bundle.check`, `label` (copied from the `ve_conformance`/`route` binding). Copied: `response`, `counts`, `uncounted`. `dispatch` is `lean/VE/NormDefaults/Run.lean`, `lean/VE/Norms/Run.lean` and then the source binding's files. Layout and docs/spec/assurance-manifest.md by `tools/regen_generated.py --write`. The pin tests (`test_decoder_files_are_pinned_whole`, `test_trusted_decoder_line_ranges_are_pinned`) pass. One probe per binding: conformance/binding_probes.py (the norms or route probe, sent to mode `norm-defaults`) |
| 2 | The coverage test compares the full answered set (own table + what the `norms.json#/row` fallback answers), read from the rendered schemas; new test fails on main for the four kinds | tests/test_norm_defaults_response_binding.py: `_answered_kinds` walks the rendered row through every reference and collects each kind an `x-select` condition selects, by the schema whose `kind` table names it. `test_the_manifest_lists_every_kind_the_mode_answers` now asserts that the manifest's kinds equal this whole set, each bound once (it also checks that the walk finds the own table and both fallbacks). New `test_norm_defaults_manifest_includes_delegated_kinds`: each delegated kind (a superset of Astra's four) has exactly one `norm-defaults` binding, for that kind alone, with the `response`/`counts`/`uncounted` of the norms binding of the same operation (else its route binding) and the norm-defaults dispatch prefix. On main's manifest both fail (S2 below) |
| 3 | docs/premise-packs/norm-defaults-cfr-1/REPORT.md :5/:17 say exactly what is bound | :5 now says the 13 kinds of the own `kind` table were bound there and the 10 fallback kinds are bound by this item. Row 1 (:18 after the edit) names the 10 kinds and what the cfr-1 test compared then and compares now |
| 4 | A delegated kind with no request binding anywhere is an R8 gap | None. Each of the 10 is bound on the path that answers it: the norms kinds by `ve_service`/`norms`, the route kinds by `ve_conformance`/`route`. The new bindings carry those bindings' case counts (`evaluate` `values`=`case.ast`, `dependency-order` `order`=`case.nodes`, `bundle` `lemmas`/`checked`=`case.lemmas`) and their row-to-row counts (`background`). The norms mode's own rows have no `MODE_BINDINGS` entry, and none was added for them, so `_bind_norm_defaults` is unchanged |

## DELTA and trust

- No DELTA row. A manifest binding is read only by `ve/backends/lean.py` `run` (`require_lean_binding`); every
  `ve` call of `run` is a declared `lean_call_sites` entry, and none calls mode `norm-defaults`. The relays that send
  cases to that mode (`relay.decide`: ve/norm_defaults_route.py, ve/norms.py) do not read bindings. So no reachable
  answer changes. A tool or test that calls `run(<op>, mode="norm-defaults")` for one of the 10 kinds used to get a
  RuntimeError; it now gets rows checked against the binding.
- Trust: `uv run python tools/trust_map.py --check` on this branch: K +0, S +0, D +0, G +0, tied +0, trusted +0; PASS.
  No Lean changed, so no audit, no trust_mutants sweep and no R16 row.

## Seeded bugs (docs/premise-packs/norm-defaults-cfr-1-cfr-1/mutants.json)

Each was planted, shown failing and restored (`git checkout HEAD -- <file>`).

| # | File | Seeded bug | Failing test |
|---|---|---|---|
| S1 | ve/assurance-manifest.json | drop the `norms-conflict` binding of mode `norm-defaults` (one delegated kind) | `test_the_manifest_lists_every_kind_the_mode_answers` (`{'norms-conflict'}`) and `test_norm_defaults_manifest_includes_delegated_kinds` |
| S2 | tests/test_norm_defaults_response_binding.py | revert the coverage test to the own-table comparison: main's manifest passes it, though main binds none of the 10 kinds | `test_norm_defaults_manifest_includes_delegated_kinds` on main's manifest: `('background', 'is answered by the norm-defaults mode but not bound once for it')`; the full-set test lists the 10 kinds |
| S3 | ve/assurance-manifest.json | the norm-defaults `background` binding loses its `counts` (a binding weaker than the route binding it mirrors) | `test_norm_defaults_manifest_includes_delegated_kinds` (`AssertionError: background`) |
| S4 | conformance/binding_probes.py (Python) | the `norms-conflict` probe keyed to mode `diagnose` | tests/test_assurance_manifest.py `test_every_lean_binding_has_a_probe` |

Languages: no Lean or Rust product code changed. The Python changed is conformance/binding_probes.py (S4).
ve/assurance-manifest.json is JSON data (S1, S3).

## Tests run

- While iterating: the two manifest tests; tests/test_assurance_manifest.py without its two Lean-probe tests (165 passed after
  regen); the probe/pin/spec tests again after regen.
- The two Lean-probe tests (`test_every_lean_binding_routes_its_operation`, `test_every_real_answer_is_counted_and_indexed`)
  need the Rust release binary to build the `evaluate` and `countermodel` probes. That binary is missing in this
  worktree, so they run in the final selected run on the Mac runner (below).
- Final selected run: see "Final run" below.

## Pilot bytes

None expected: no answer, verdict or diagnostic changes (manifest record and tests only).

## Notes for the DRI

- Scope beyond the ruling's four: the six route kinds were bound by the same rule. The reason is above; dropping
  them would leave the coverage test overclaiming again.
- The norms mode's own `ve_service`/`norms` bindings omit the route kinds its `route.json#/row` fallback answers
  (`background`, `evaluate`, `countermodel`, `certificate`, `dependency-order`, `bundle`, `label`): the same record gap
  one mode over. It is out of this item's scope and does not change a verdict or binding at any call site (no `run`
  call uses mode `norms` for them), so it is a note, not a follow-up.
- Merge: ve/assurance-manifest.json is also changed by kb-1, kb-8 and others in flight. It merges per record
  (`merge=ve-generated`), and this item only appends bindings to existing operations' lists.

## Next item

pk-1-cfr-1b (beside this one). norm-defaults' L1 acceptance stops being PROVISIONAL when the four rows of item 5 merge.
