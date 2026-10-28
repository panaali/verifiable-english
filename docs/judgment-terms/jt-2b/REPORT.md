# jt-2b report: the relay of `judgments` (JT-2, Python part)

No DRI signature is reserved. DELTA's two rows cite R8 (the relay) and R6 (`ve/openterms.py` off the Lean path).
The composing modes' identity design was asked of the DRI and decided as the separate item jt-2c
(reviews/dri-decisions-20261028-jt-2c.md, in /home/seyran/code/manage-agents; jt-2b unchanged by it).

Plan: docs/spec/judgment-terms-PLAN.md batch JT-2, its Python bullets and seeded bugs P1/P2; spec judgment-terms.md
8.1 to 8.3. Statement gate: jt-2's REPORT records the plan's statement review (FIX joint position, draft 3, then
ACCEPT, draft 4) for JT-2. This item changes no statement. Shared-file queue (SYNTHESIS 4.2): `ve/document/lean.py`
has no other in-flight editor. `tests/data/route-cases.jsonl` is in feature/qt-a3c, and this item does not touch it.

## Plan rows

| Plan row / directive | Delivered | Where | Checked by |
|---|---|---|---|
| (1) Relay checks the `judgments` schema and binding only (R8): every unit id a unit of the request, every name a declared open term, no empty or extra row, Lean's order (terms in declaration order, unit ids in the request's unit order) | yes | `ve/document/lean.py` `_bind_document_answer` (the key set has `judgments` exactly under the profile), `_judgments_bound` | `tests/test_judgments_answer.py` (below) |
| (2) Fuzz tests in `tests/test_judgments_answer.py`: each member dropped, emptied, retyped (null, true, 7, 7.5, "7", a lone surrogate, [], {}, a 10,000-deep list), duplicated, reordered or rotated; an id or a term pushed out of the request; a term both used and unused; an empty row; an extra member | yes, over 130 mutants for each multi-row genuine answer (four genuine answers) | `test_every_mutant_of_the_usage_map_is_refused` | every mutant is refused, except the one class R8 leaves to Lean (see the limit below) |
| Each new check is tested on both sides of every boundary | yes | `test_the_order_is_lean_s` (8 rows: in order and out of order, a unit skipped, a term missing), `test_the_field_is_there_exactly_under_the_profile` (missing under the profile, extra without it), `test_the_genuine_answer_is_relayed` | |
| (3) Route cases recorded by the recorder | **no: moved to jt-2c** | | The document mode has no rows in `route-cases.jsonl`: `tests/route_case_recorder.py` records only the old one-shot route modes there. Its recorded fixtures are the relay gate's (`tests/data/relay-gate-cases.jsonl`), and that gate fails on a genuine answer its reader (`_lean_document`) refuses. `_lean_document` must refuse a `judgments@0` answer until jt-2c builds its environment. The genuine answers are checked against the generated `document.json` here (`relayed`, through `check_row`). |
| (4) The live document path stops calling `ve/openterms.py`; Lean's diagnostic relayed; the layer-policy entry says the file stays only while the frozen speech imports it | yes on the Lean-answered path; **the file also stays for Python's own path** | `ve/document/lean.py` (`_lean_document`: open-term names from the front matter Lean's `Loader.openTermNames` accepted); `tools/layer_policy.py` `RETAINED` | `test_a_rights_document_reads_lean_s_open_terms` (6 rows: same outcomes as the retained path, Lean's diagnostic for every malformed record), `test_openterms_is_imported_only_where_the_layer_policy_retains_it` |
| (5) Plan seeded bugs P1, P2 | yes | `mutants.json` | below |
| Composing modes (Python `Environment`, model operations) under `judgments@0` | **jt-2c**, by DRI decision (reviews/dri-decisions-20261028-jt-2c.md items 1 to 3) | | |

Deviation in (4): `ve/document/load.py` (Python's own path) still calls `validate_open_terms`. That path runs for a
`ve-document@2` document and for a document Lean's `document` mode answers `CheckerUnavailable`. In both cases no
Lean check of the same strength has run: the discourse loader runs `openTermNames` without `python := true` or the
formula type check, and `environmentOf` may refuse before the open terms are read. Removing the call there would
delete a check, which DRI-RULINGS.md lists as never covered by a standing ruling. So `RETAINED` names both importers,
and a test pins them: the file goes when the retained path goes.

Limit (R8): a unit dropped from a `units` list of two or more leaves a map that is still well-formed and bound.
Which units use a term is Lean's decision, and the relay never recomputes it (R8: a tampered semantic field is not a
finding when the schema, the binding and Lean's encoder theorem hold; `usage_fits` is jt-2's). The fuzz test pins
that exact set (`lean_s`), so any other accepted mutant fails it. Nothing displays the map yet: `ve document` on such
a document stops before the binding (jt-2c). When jt-2c or JT-3 shows the map, this class changes what is shown.

## Seeded bugs

[`mutants.json`](mutants.json), all in `ve/document/lean.py` (Python, the only product language changed). Each was
applied by `sed` to the committed tree, its test run, and the file restored:

- **P1** (plan): `_judgments_bound` checks a `units` list only over its ids that are request units, so an id outside
  the request is accepted. Fails `test_every_mutant_of_the_usage_map_is_refused` (3 of 4 fixtures).
- **P2** (plan): `ordered` checks for repeats but skips the order check. Fails
  `test_the_order_is_lean_s[used terms reversed|units reversed|unused out of order]` and
  `test_every_mutant_of_the_usage_map_is_refused[two-rows|three]`.
- The key set admits `judgments` without the profile. Fails `test_the_field_is_there_exactly_under_the_profile`.
- The declared terms are compared as sets, so a term both used and unused is accepted. Fails
  `test_every_mutant_of_the_usage_map_is_refused[J-alpha|three]`.
- The Lean path imports `ve/openterms.py` again. Fails
  `test_openterms_is_imported_only_where_the_layer_policy_retains_it`.

A survivor, recorded: passing no open-term names to the rights containers on the Lean path (`open_predicates=set()`)
changes nothing shown. Their `unit_open` is read only on Python's own path (`load.py`), and Lean's statuses are the
answer's.

## Trust, size and evidence

- Trust: no Lean or Rust change. `tools/trust_map.py --check` reports PASS on this branch against `c86861a2a`:
  K +0, S +0, V +0. No R16 allowance, so no FOLLOW-UPS row is needed.
- Size: about 330 hand-written lines before this report: tests 250, `ve/document/lean.py` +33 −4, layer policy 4,
  DELTA 6, a jt-2 test docstring 3.
- Tests: the selected plan ran on the Mac runner on `fcb123e12`: exit 0, 0 failed, 420 units, 1633 s. After that I
  added only the two fuzz retypes, and ran `tests/test_judgments_answer.py -k "every_mutant or genuine"` (8
  passed). `regen_generated.py --check` reports 33 entries, all current. `gate_collection.py --check --prebuilt`
  reports 24 added, 0 removed, 0 refused, 0 stale, 0 malformed. The chain runs the full gate on the final HEAD.
- Not run: whole-document pilots (L70) and base/head timing. No pilot lists `judgments@0`, and documents without it
  take the same path, except for the key-set expression.
- Pilot bytes expected to move: none from this item. `ve document` answers a `judgments@0` document only after jt-2c.
  After JT-5r, JT-5a then expects Lean statuses on 13 constitution units and JT-5b on 18 UDHR units. Nothing is
  claimed before a pilot audit.

## Next item

**jt-2c** (queued by the feature planner, per the DRI's decision): the modes Python's `Environment` and model
operations call compose with `judgments@0` under item 1's identity rule, `ve document` answers such a document
(DELTA row signed by that decision, item 2), and the route cases are recorded in the relay gate's fixtures (this
item's row 3). Then JT-5r's audit and the JT-5a/5b pilot switch-ons.

## Self-review against BUILDER-CHECKLIST

1. PASS: every `judgments` member is retyped (including a lone surrogate and a 10,000-deep list), dropped, emptied, duplicated and reordered, and each mutant is refused (`test_every_mutant_of_the_usage_map_is_refused`). `_lean_document` turns any binding exception into `CheckerUnavailable`.
2. PASS: plan rows above. Row 3 and the composing modes moved to jt-2c by the DRI's decision of 2026-10-28. The (4) deviation is explained above. No Python copy of a Lean decision: usage is never recomputed.
3. PASS: five seeded bugs, each failing a named test (`mutants.json`). No R16 growth, so no trust mutants.
4. PASS: the Lean path and the retained path give the same outcomes for rights documents with open terms (`test_a_rights_document_reads_lean_s_open_terms`). A document without the profile is relayed as before (`test_the_field_is_there_exactly_under_the_profile`).
5. PASS: undeclared names (`undeclared`, `arrest`, ""), out-of-request ids (`u999`, `u0`, `U1`), duplicated rows, empty `units` and an extra member are refused (`test_every_mutant_of_the_usage_map_is_refused`).
6. PASS: no merge needed (main has not moved past `c86861a2a`). The chain runs the full gate on the final HEAD.
7. PASS: both DELTA rows cite R8 and R6 with their tests. No reserved signature.
8. PASS: DELTA lists the relay (no change in `ve document`'s answer) and the open-term names. The retained path is unchanged.
9. PASS: the selected plan contained `tests/test_judgments_answer.py`, `tests/test_judgments_document.py` and `tools/test_layer_policy.py`.
10. N.A.: no Lean statement or proof changed.
11. N.A.: no budget, limit or deadline code.
12. N.A.: one pass over a usage map per answer; no pilot lists the profile.
13. PASS: `gate_collection.py --check --prebuilt`: 0 removed, 0 refused, 0 stale, 0 malformed.

## FIXMAP
- `ve/document/lean.py`: the document mode's relay. `_bind_document_answer` (the key set has `judgments` exactly under
  `judgments@0`) and `_judgments_bound` (spec 8.3's binding and order, just above `_governed_units`). `_lean_document`
  builds rights containers with the open-term names Lean accepted (no `ve/openterms.py`).
- `tools/layer_policy.py`: `RETAINED` (the files that may still import `ve.openterms`).
- `tests/test_judgments_answer.py`: genuine answers (`GENUINE`, `THREE`), `relayed` (`check_row` then the binding),
  `mutants`/`rebinds` (the fuzz), `lean_s` (the one bound class), `ORDERS` (boundaries), the rights open-term rows
  (`RIGHTS_OPEN_TERMS`) and the importer guard.
- `tests/test_judgments_document.py`: jt-2's file; one docstring now names jt-2c.
- `docs/judgment-terms/jt-2b/{DELTA.md,mutants.json,REPORT.md}`.
- Spec 8.3 maps to `ve/document/lean.py` `_judgments_bound`. Plan JT-2 "openterms off the live path" maps to
  `_lean_document`'s rights branch and `tools/layer_policy.py` `RETAINED`.
- Regression tests: `uv run pytest -q tests/test_judgments_answer.py tests/test_judgments_document.py`.
- Generated files: none changed. If needed, run `uv run python tools/regen_generated.py --write`.
- Trust mutants: not used (no trusted Lean change).
## END FIXMAP
