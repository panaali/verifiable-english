# Batch 12 integration merge

This records the `ve-integration` merge into `lean-first/b12`. The 23 textual
conflicts were resolved by semantic ownership, with the audit inventory taking
the union of both branches' Lean declarations.

| Conflict area | Resolution |
| --- | --- |
| Lean route, service, and standalone decoders | Kept batch 12's Lean environment and model verdicts, including constant verbalisation and model identity checks; composed them with the integration service's English and readings modes. The source vocabulary proof is over the decoded source, while generated readings names extend the projected vocabulary. |
| Python environment, profiles, search, and soft norms | Kept Lean admission for environment/model and integration's profile projection, Rust search relay, and Lean soft norm route. Each public operation has one decision owner. Python builds accepted containers and conformance oracles only. |
| Audit, frozen hashes, lock, statements, trust, and assurance manifest | Unioned audited declarations and operation bindings, regenerated derived files, and measured a new trust baseline for the merged tree. The approved batch 12 report remains pinned to its premerge commit. |
| Wire contract, hooks, tests, and collection | Kept optional legacy wire handling and the integration staged Lean check; updated tests for composed behavior and refreshed the collected test ID baseline. |
| Differential fuzz baseline and docs | Replayed all 408 merged baseline entries: 147 no longer disagreed, 26 changed signatures coincided with existing findings, and 7 changed findings retained their reviewed follow ups. The CI sample added 19 minimized findings under existing `DF-6` and `DF-9` follow ups, giving 254 reviewed entries. |

The existing `closure@0` with `nary@0` and an n-ary defined predicate remains
outside the Lean core-family glue. `ve/backends/validation.py` identifies that
scope, so `ve/background.py` and `ve/definitions.py` retain their original
Python validation path for it, with its existing inventory status. A shared
Lean model route for this combination remains a follow up in
`docs/INTEGRATION-GAPS.md`.

`tools/select_tests.py --impacted` selected all 330 test files because the
conflicts include shared service and route modules. The merge ran targeted
tests for the environment/model, search, profiles, soft norms, norm defaults,
readings, English relay, Rust conformance, wire contract, differential fuzz,
manifest, branch evidence, and collection areas. The merge train runs the full
suite and release gate separately.
