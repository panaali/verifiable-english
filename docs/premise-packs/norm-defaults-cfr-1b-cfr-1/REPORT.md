# norm-defaults-cfr-1b-cfr-1: readings-route binds its norm-defaults rows (ndc1b-F6)

No DRI signature is reserved; no DELTA row (step 1: no Python relay reaches the changed path).

Item: second row of reviews/dri-decisions-20261111-portfolio1500.md item 5 (regrade #10, ndc1b-F6, C->A, Astra
11-11). Ruling: ADD the binding (R8: a missing request binding is a B-class defect; the fix only refuses more).
Base: merge base 175814252 (main; `ve/backends/lean_service.py` and `ReadingsRoute.lean` are unchanged since
e78b6d949: `git diff e78b6d949 HEAD --stat -- <both>` printed nothing).

SIZE: 12 product, 125 tests, ~110 other hand-written lines (this REPORT); `git diff --numstat $(git merge-base HEAD
main)` before the REPORT: `125 0 tests/test_readings_route_norm_defaults_binding.py`, `12 2 ve/backends/lean_service.py`.

## Step 1: measure (before any edit)

### Astra's probe, reproduced on main (HEAD 175814252, no edit)

Script `/tmp/ndc1bcfr1_probe.py` (run as `uv run python -I /tmp/ndc1bcfr1_probe.py`):

```python
from ve.backends.lean_service import Invalid, bind_answers
from ve.backends.service_schema import check_row
case = {"id": "c", "kind": "norm-defaults-certificate", "environment": {"profiles": ["norm-defaults@0", "norms@0", "readings@1"]},
        "premises": [], "certificate": {"premise_meaning_ids": ["m1", "m2"]}}
row = {"id": "c", "status": "ok", "valid": True, "premises": 999}
for mode in ("readings-route", "norm-defaults"):
    try:
        check_row(mode, row, case, 0)
        bind_answers(mode, {"status": "ok", "results": [{"index": 0, "result": row}]}, {"cases": [case]})
        print(mode, "ACCEPTED premises=999")
    except Invalid as e:
        print(mode, "Invalid:", e)
```

Output on main:

```
readings-route ACCEPTED premises=999
norm-defaults Invalid: norm-defaults-certificate premises is not the count its certificate is bound to
```

On HEAD the same script prints `readings-route Invalid: ...` for both modes (the condition test asserts it).

### Which Python relays can send a norm-defaults case to `readings-route`

Found with `grep -rn '"readings-route"\|readings_route\b' ve --include=*.py`, then reading each caller of
`readings_route.run_lean` for the kind it sends:

- `ve/norms.py:336` (`plain_wordings`): sends `readings-route` for a `readings@1` environment, but only the kind
  `norm-defaults-elaborate` / `norms-elaborate` (`ve/norms.py:335`). That kind is not bound by `_bind_norm_defaults`.
- `ve/readings_route.py:454` (`run_lean`), whose callers send only readings kinds: `readings-elaborate`
  (`ve/readings_route.py:67`, `ve/readings_components.py:54`), `readings-validate` (`ve/readings_route.py:852`,
  `ve/readings_components.py:55`), `readings-verdicts` (`ve/readings_components.py:56`, `:281`,
  `ve/readings_verdicts/superposed.py:430`, `ve/readings_verdicts/enumerated.py:63`), `readings-conflict`,
  `readings-model`, `readings-certificate` (`ve/readings_verdicts/superposed.py:171`, `:204`, `:254`, `:350`, `:396`),
  and `readings-choice` (`ve/readings_verdicts/choice.py:269`, `ve/readings_components.py:321`), whose **inner** case
  may be `norm-defaults-certificate` or `norm-defaults-elaborate`. The outer kind is `readings-choice` and the row is
  `choice_answer`, not `norm-defaults.json#/row`, so that path is not the one this item binds.
- No CLI option names a service mode (`grep -rn '"--mode"' ve` finds only `grammar --mode full|syntax`,
  `ve/__main__.py:361`).

Result: **none** of the Python relays sends a top-level `norm-defaults-status` or `norm-defaults-certificate` case to
`readings-route`. This agrees with the cfr-1b reviewer, who found no relay sending status cases there. The defect is
reachable only by a direct client call (`LeanService.run("readings-route", ...)` or `check_row` + `bind_answers`, as
in Astra's probe), so **no DELTA row** is written: no reachable relay refuses an answer it used to accept.

### Why dispatching on the case's kind is sound (Lean read, not changed)

`Readings.Run.runLower` (`lean/VE/Readings/Run.lean:519-530`) runs a case of no readings kind on the runner that
`Compose.gateOf` names for the profiles without `readings@1`: rights, soft-norms, norm-defaults or norms.
Only `NormDefaults.Run` answers the kinds `norm-defaults-status` and `norm-defaults-certificate` with `ok`. The
other runners have no such kind (`grep -rn 'norm-defaults-' lean/VE/SoftNorms lean/VE/Rights lean/VE/Norms/Run.lean`
finds nothing). So an `ok` readings-route row for such a case is the norm-defaults runner's row for the same case JSON
(`ReadingsRoute.lean:896-900` admits `norm-defaults.json#/row`). The binding `_bind_norm_defaults` applies under
`norm-defaults` mode, and under `readings-route` it binds the same request fields. The `readings@1` profile does not
affect `_profiles`, `_rule_names` or `GENERATED_RULE_PROFILES` (`ve/backends/lean_service.py:368-398`).

## Deliverables

| Task row | Delivered by | Test |
|---|---|---|
| (1) readings-route rows of the norm-defaults row schema go through `_bind_norm_defaults` by a `MODE_BINDINGS` entry dispatching on the case kind, one owner | `_bind_readings_route` (`ve/backends/lean_service.py:441`) calls `_bind_norm_defaults`, which binds only `norm-defaults-status` and `norm-defaults-certificate`; `MODE_BINDINGS` at `:451`. The binding logic is not copied. | below |
| (2) `test_readings_route_binds_norm_defaults_certificate_count`: forged count via readings-route raises `Invalid` (fails on main), the genuine row passes, the status-rule binding applies under readings-route | `tests/test_readings_route_norm_defaults_binding.py:51`; also the scripted client path (`LeanService.run`: `CheckerUnavailable` for the forged row, the genuine row relayed) | fails on main's `lean_service.py` (4 failed, 5 passed with the main file copied in; then 9 passed on HEAD) |
| (3) every other readings-route row binds as before | `test_other_readings_route_rows_bind_as_before` (readings, norms, `norm-defaults-elaborate`, error rows); `tests/test_relay_binding_inventory.py` unchanged: `45 passed in 69.38s` | readings-route relay/fuzz tests: selected run below |

Further tests in the new file (BUILDER-CHECKLIST 1, 5, 14):
- `test_readings_route_norm_defaults_field_deleted_or_retyped`: `id`, `premises` and `valid` of the certificate row,
  and `id`, `rules`, `sources` and `tuple` of the status row, each deleted or set to `7`, `true`, `null`, `[]`, `{}`,
  `1.5`, `"\ud800"`, `""`, `"2"`, `[7]`, `[null]`, `-1` or a 10k-deep list, give `Invalid`.
- `test_readings_route_status_rows_extra_duplicated_or_empty`: a duplicated row, an extra row, an undeclared rule,
  an empty echo list or one echo too many each give `Invalid`.
- `test_readings_route_certificate_case_without_its_certificate_has_no_count`: no count binds without the request's
  certificate or premise list.

`uv run pytest -q tests/test_readings_route_norm_defaults_binding.py`: `16 passed in 0.49s`.

## Seeded bugs (Python; the only language changed)

Each was planted in `ve/backends/lean_service.py`, run with `uv run pytest -q
tests/test_readings_route_norm_defaults_binding.py`, then restored (`git diff --stat` afterwards: unchanged).

| # | Behaviour | Mutant | Failing test |
|---|---|---|---|
| S1 | readings-route has a binding | drop the entry: `MODE_BINDINGS = {"norm-defaults": _bind_norm_defaults}` | `test_readings_route_binds_norm_defaults_certificate_count` (+ `..._field_deleted_or_retyped[case0-row0-premises]`, `..._without_its_certificate_has_no_count[certificate]`, `[premises]`): 4 failed |
| S2 | the certificate count is bound under readings-route | bind only status rows: `_bind_readings_route` calls `_bind_status_rules` for `norm-defaults-status` only | the same 4 tests fail |
| S3 | the status-rule binding applies under readings-route | bind only certificate rows: `_bind_readings_route` calls `_bind_norm_defaults` for `norm-defaults-certificate` only | `test_readings_route_binds_norm_defaults_certificate_count` (its status part): 1 failed |

## Trust and gates

- Trust: `uv run python tools/trust_map.py --check`: `against 175814252daf: K +0, S +0, D +0, G +0, tied +0,
  unclassified +0, trusted +0` and `PASS`. No allow record is needed (Python only).
- Light lane: `python3 -I .../tools-local/light-lane.py check <worktree>`: `LIGHT 139 changed lines outside generated
  files <= 150 (2 files), no trusted-core file`. The task requires no trust_mutants record, so no sweep was run.
- Generated files: `uv run python tools/regen_generated.py --check`: rc=0, `checked 40 entries`, none stale.
- Test selection: `tools/select_tests.py --base $(git merge-base HEAD main)` selects
  `tests/test_readings_route_norm_defaults_binding.py`, `tests/test_norm_defaults_response_binding.py`,
  `tests/test_readings_route_relay.py`, `tests/test_readings_route_fuzz.py` and `tests/test_relay_binding_inventory.py`
  (429/610 units).
- Selected run: see "Selected tests" below.
- Pilot bytes expected to move: 0 (a refusal of forged answers only; Lean's genuine rows pass unchanged).

## Selected tests

PENDING (filled in after the final selected run on the committed tree).

## DELTA

None. Step 1 found no Python relay that sends a top-level `norm-defaults-status` or `norm-defaults-certificate`
case to `readings-route`, so no user-visible answer changes. A direct client of the mode now gets
`CheckerUnavailable` for a forged row, a refusal covered by R8 that only refuses more.

## Spec re-read

- R8 (`/home/seyran/code/manage-agents/DRI-RULINGS.md:32`): "binding to the request: every id, span, count ... exists
  in the request" and "A missing ... binding IS a B finding". The certificate `premises` count and the status
  rules' sources are both bound now under readings-route. Nothing semantic is rechecked in Python.
- `lean/ResponseShape/Schemas/ReadingsRoute.lean:896-900` and the file comment ("such a row is any of those four
  modes' rows for the case"): the new binding applies to the norm-defaults kinds only and leaves the other three
  modes' rows alone.
- `lean/VE/Readings/Run.lean:519-530` (`runLower`): the same case JSON goes to `NormDefaults.Run.runCaseReported`,
  with `readings@1` stripped from the environment's profiles only.
- `ve/backends/lean_service.py:424` (`_bind_norm_defaults` docstring) is the one owner; it is not edited.

## Notes for the DRI

- The relay mutation gate (`tests/data/relay-gate-cases.jsonl`) has no readings-route fixture with a top-level
  `norm-defaults-*` kind; its norm-defaults kinds under readings-route are only `readings-choice` inner cases
  (lines 345-346). So the gate neither exercises nor is changed by this binding, and no allow-list entry goes stale
  (the two readings-route `results/*/result/premises` entries, B0 duplicate/empty, are about a list-valued
  `premises`, not the certificate's integer). The new test file covers the path with rows built by hand to the
  schema.

## Self-review against BUILDER-CHECKLIST

1. Fully typed and contained: PASS. `test_readings_route_norm_defaults_field_deleted_or_retyped` covers the
   checklist values on every field of both rows; `test_readings_route_binds_norm_defaults_certificate_count` goes
   through the client and gives `CheckerUnavailable`.
2. Deliverables and rules: PASS. Deliverables table above; one owner (`_bind_readings_route` delegates to
   `_bind_norm_defaults`, nothing copied); no report test; no overlap with `tests/test_norm_defaults_response_binding.py`
   or the assurance manifest.
3. Tests can fail: PASS. Seeded bugs S1-S3, each with its failing test.
4. Valid inputs still pass: PASS. The genuine certificate and status rows pass
   (`test_readings_route_binds_norm_defaults_certificate_count`); other rows pass
   (`test_other_readings_route_rows_bind_as_before`); `tests/test_relay_binding_inventory.py` passes (45 passed).
5. R8 binding: PASS. `test_readings_route_status_rows_extra_duplicated_or_empty` (absent, duplicated, extra, empty);
   shifted counts 3, 1, 0 and 999 in the condition test.
6. Gate evidence on final HEAD: PASS. The selected run is on the committed final tree (see "Selected tests"); the
   chain runs the full gate.
7. No unsigned item: PASS. No DELTA row and no trust growth (`trust_map.py --check`: trusted +0).
8. Every user-visible change in DELTA: PASS. Step 1 relay search: no relay reaches the path; DELTA is "None" with
   the reason.
9. Test selection: PASS. `select_tests.py` selects the new file and the readings-route and inventory tests; seeded
   bug S1 fails `tests/test_readings_route_norm_defaults_binding.py`, which is selected.
10. Lean statements: N.A. (no Lean changed).
11. Budgets and deadlines: N.A. (no budget, limit or deadline touched; the tests use no sleep or timeout).
12. CPU/memory: N.A. (one dict lookup and one call per `ok` row, the same cost as under norm-defaults).
13. Test-removed trailers: N.A. (no test removed or renamed).
14. Both directions, cited evidence, spec re-read: PASS. Each refusal is tested with its genuine accept
    (`test_readings_route_binds_norm_defaults_certificate_count`); each claim cites its command above; "Spec re-read"
    section.
15. Overclaim, silent cut, checks can fail, limits: PASS. "none" in Step 1 and DELTA cites the grep and caller list;
    no deliverable was cut; S1-S3; no limits (N.A. part).

Next item: norm-defaults-cfr-1-cfr-1 (runs beside this one); nothing waits on this row.
