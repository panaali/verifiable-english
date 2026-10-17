# Build report: infra/fu-rd9-checks

**No DRI signature is needed for a delta.** Every DELTA row cites a standing ruling: R8, R16 and R12
([DELTA.md](DELTA.md)). **One point for the DRI:** gap 2 (`report_id`) gets no relay check, because ADR 0001 (D1)
forbids one; see the second row of the table below and DELTA row 3.

## The task's first check: did rights-licence-relay close either gap?

No. On main 85b20fcba (the rights-licence-relay merge), the relay accepted all three forgeries: audit row 38, a
rights admission `report_id` of 64 zeros, and the same for soft admission
([evidence/forgery-replay.json](evidence/forgery-replay.json)).

## Delivery

| Task line | Delivery | Commit | Check |
| --- | --- | --- | --- |
| 1. The relay must refuse the row-38 "CONFLICT-FREE … 9 coherence premises" line on an UNKNOWN verdict, in Lean's schema where that is the right place | **Lean shape** `rights.json#/$defs/packages`, per verdict. UNKNOWN: `status_text` matches `UNKNOWN: .*`, `detail` matches `(missing\|invalid) certificate for .*`, and `conditional_on` is empty. CONFLICT-FREE: `status_text` matches `CONFLICT-FREE among rules on the same act, conditional on .*`. Row 38 now fails the Lean service client's schema check. **Relay** (`_bind_conflict`, R8 (b)): the target an UNKNOWN line's detail names must be one of the bound `targets`, and the line must be the UNKNOWN line of that detail. A forgery is refused with the neighbouring CONFLICT-FREE check's text: `CheckerUnavailable: Lean rights conflict is not bound to the request: unbound conflict status text`. The inventory now fuzzes `detail` and `status_text` | e9f2b755a | `tests/test_rd9_followup_bindings.py` (10 forgeries: 5 the shape refuses, 5 that fit the shape and the relay refuses); `tests/test_relay_binding_inventory.py::test_every_bound_field_mutant_is_unavailable[rights-conflict]` |
| 2. The `report_id` of soft-norms and rights admission is not checked against the request | **Left to Lean, with the missing regression tests.** `report_id` names no request item. It is an identity hash, a derived value. ADR 0001 D1 (signed): "Python never recomputes it to check it"; "new relaying code adds no Python recomputation of a derived value". `bound_admission`'s digest on the core route is debt that AR-15 owns, and `tools/identity_lint.py` ratchets it. Lean already proves the binding: `VE.SoftNorms.Run.runAdmission_sound` and `VE.Rights.Run.runAdmission_sound` show every admission answer's `report_id` is the digest of the canonical environment id, the document sent and the report. So under R8 the gap is closed by Lean. A Python check (e9f2b755a) was built and then removed (dc97aa4fd). It reused `bound_admission`'s preimage in two new relays, which D1 forbids and which `tests/test_identity_lint.py` failed. The regressions pin Lean's guarantee: both theorems stay stated and audited, and Lean's genuine answers for 3 soft and 3 rights sources carry exactly the stated identity (distinct per source). If the DRI wants the relay to refuse at run time, that is AR-15's Lean-side work | dc97aa4fd | `tests/test_rd9_followup_bindings.py::test_the_report_id_guarantee_is_a_stated_audited_theorem`, `::test_lean_admission_report_ids_are_the_identity_the_theorem_states[soft]`, `[rights]` |
| Keep both relays (Python and Rust) in step | Rust has no rights or soft-norms relay: `rust/` has no `rights-conflict`, `report_id` or `soft-elaborate`. Nothing to keep in step | — | `uv run python tools/repo_map.py route rights` lists only Python relays |
| Lean owns meaning; record trust growth under R6/R16 per file, re-measured on the final HEAD | V +6, all G[V] in `ResponseShape/Schemas/Rights.lean` (`packages`); K +0, S +0; measured against the merge base bc1936dd5. R16 allowance recorded with `tools/trust_map.py --allow`; the ties pass is a FOLLOW-UPS row | e9f2b755a | `python3 tools/trust_map.py --check` exit 0; DELTA row 4 |
| Coordinate: no edits to the `-- uses` lines of the ties-rights-licence-relay files, none to `lean/VE/Service/Document.lean`, generated files only through the regenerator | Edited only the `packages` definition of `lean/ResponseShape/Schemas/Rights.lean`, which has no `-- uses` lines. `VE/Rights/Run.lean`, `VE/Rights/Scope.lean` and `Service/Document.lean` are untouched (L3 was a seeded bug, reverted). Generated files came from `tools/regen_generated.py --write` | all | `git diff main...HEAD --stat` |

Other: the branch is synced with main at bc1936dd5 (merge c9452489f). `tools/relay_mutation_gate.py --route
service:rights` reports 6,549 mutants and 0 failures.

## Seeded bugs ([seeded-bugs.json](seeded-bugs.json))

Each was planted alone, shown to fail its test, then removed. The tree is clean after each run.

| Id | Language | File | Bug | Test that fails |
| --- | --- | --- | --- | --- |
| L1 | Lean | `lean/ResponseShape/Schemas/Rights.lean` | the UNKNOWN branch drops the `UNKNOWN: ` pattern (schema regenerated for the run) | `test_a_status_line_of_the_wrong_verdict_does_not_fit_the_lean_shape[row 38]`, `[UNKNOWN line renamed]` |
| L2 | Lean | `lean/ResponseShape/Schemas/Rights.lean` | the UNKNOWN branch drops `conditional_on` `maxItems 0` | `…does_not_fit_the_lean_shape[UNKNOWN conditional on a premise]` |
| L3 | Lean | `lean/VE/Norms/Run.lean` (not changed by the item) | `reportDomain` writes `ve-reportX-`; the build and `runAdmission_sound` pass; `ve_service` pinned for the run | `test_lean_admission_report_ids_are_the_identity_the_theorem_states[soft]`, `[rights]` |
| P1 | Python | `ve/rights_route.py` | `_bind_conflict`'s UNKNOWN check becomes `pass` | `test_an_unknown_line_naming_what_the_request_lacks_is_unavailable[*]` (5), `test_every_bound_field_mutant_is_unavailable[rights-conflict]` |
| P2 | Python | `ve/rights_route.py` | the UNKNOWN check drops its target binding | `…lacks_is_unavailable[detail names ghost]`, `[no target]` |

P1 and P2 were rerun on the final code (after dc97aa4fd). L1 and L2 ran at e9f2b755a, and the shape has not changed
since.

## Tests run

- Selected tests (`mac-pytest.sh --select`, base bc1936dd5) on HEAD 830a5c0b: 151 units, 0 failed, exit 0. The one
  later commit adds only this report.
- The tests I added and their neighbours, 689 passed: `test_rd9_followup_bindings.py`,
  `test_relay_binding_inventory.py`, `test_identity_lint.py`, `test_relay_lint.py`, `test_soft_decision_keys.py`,
  `test_rights_licence_relay.py`, `test_architecture_docs.py`, `test_binding_census.py`, `test_response_schemas.py`,
  `test_trust_ratchet.py`.
- `tools/regen_generated.py --check`, `tools/trust_map.py --check` and `tools/gate_collection.py --check --prebuilt`
  (14 added, 0 removed, 0 refused, stale or malformed) all pass.
- **Not run:** the full release gate (`tools/gate.py`). The chain runs it on the final HEAD.
- **Pre-existing failures:** none of `main-known-red.txt`'s three tests were selected or seen failing.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: PASS. `packages` is typed per verdict; the fuzz checks it
   (`test_relay_binding_inventory.py::test_every_bound_field_mutant_is_unavailable[rights-conflict]`), and
   `tools/relay_mutation_gate.py --route service:rights` reports 6,549 mutants and 0 failures.
2. Deliverables built, no rule broken: PASS. Delivery table above. The grep of the diff for a new Python copy of a
   Lean decision found the `report_id` digest, which was removed (D1, `test_identity_lint.py`). One Lean wording
   remains in the relay: the UNKNOWN line's `, budget 10000`. It sits beside the CONFLICT-FREE template that
   `_bind_conflict` already held before this item, and it compares Lean's text with Lean's own detail; it derives
   nothing.
3. Tests and gates can fail: PASS. Seeded bugs L1–L3 and P1–P2 (`seeded-bugs.json`).
4. Python, Lean and Rust agree; valid inputs pass: PASS. The genuine answers of 25 rights and 3 soft sources are
   accepted (`test_every_bound_field_mutant_is_unavailable[*]`), and recorded cases fit the schema
   (`tests/test_route_row_schemas.py`). Rust relays neither route.
5. R8 binding: PASS. An undeclared target in the line or the detail, a shifted value and an empty target are each
   refused (`test_an_unknown_line_naming_what_the_request_lacks_is_unavailable[*]`). Both fields are scalars: the
   inventory fuzz renames each one and swaps in every other genuine value
   (`test_every_bound_field_mutant_is_unavailable[rights-conflict]`).
6. Gate evidence matches the final HEAD: PASS. Synced with main bc1936dd5; the evidence lists commits from
   `main..HEAD --no-merges`. The chain runs the full gate on the committed final HEAD.
7. Nothing unsigned: PASS. DELTA rows 1–5 cite R8, R16 and R12 with their tests; the trust allowance is signed R16;
   `python3 tools/trust_map.py --check` passes.
8. Every user-visible change in DELTA: PASS. No genuine answer or relay output changes. Only refusals of non-Lean
   answers are new (DELTA rows 1–2); `evidence/forgery-replay.json` has the base and head replays.
9. Test selection finds the tests: PASS. `tools/select_tests.py --base bc1936dd5` selects 151 units, not the whole
   suite, including `tests/test_rd9_followup_bindings.py`, which fails under P1 and P2.
10. Lean statements: N.A. No theorem was added or changed. The shape edit leaves `runCaseReported_fits` valid
    because skeletons ignore patterns; the FOLLOW-UPS ties row asks for a theorem.
11. Budgets fail closed: N.A. No budget, limit or deadline code changed.
12. No CPU or memory regression: N.A. The Lean runner is unchanged. The relay adds one string comparison per
    rights-conflict answer.
13. Test-removed trailers: PASS. No test was removed or renamed; `uv run python tools/gate_collection.py --check
    --prebuilt` reports 0 removed, 0 refused, 0 stale and 0 malformed.
