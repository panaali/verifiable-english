# rights-cfr-1 REPORT: a rights meaning id binds the normal form (rights.md 3.5)

Item rights-cfr-1 (DRI 2026-11-09, reviews/dri-decisions-20261109-lp0801.md item 1; regrade #1 of
reviews/l1-c-regrade-rights-20261109.md). Branch `feature/rights-cfr-1`, base `6db6ee16d`. No signature is reserved.

## The defect and the plan row

rights.md 3.5 (:441): a right unit's `meaning_id` is W1's digest over `{"environment_id", "ast"}` with `ast` the
right object "every soft field at its default omitted as soft-norms 3.4 does". On main both owners of the id hashed the
content as supplied: Python's `ve/readings.py` `rights_meaning_id`, and Lean's `document` mode
(`VE.Service.Document.rightsContentOf`, `nullableMeaningId` over the content as written). Probe: an omitted `mode` and
an explicit `mode: strict` gave two ids.

## Delivered

| Plan row | Where | Test |
|---|---|---|
| The id is computed over the normal form, in one place per language; Lean owns it | Lean: `rightsNormalForm` (`lean/VE/Service/Document.lean`), applied where `rightsContentOf` binds a rights unit; its default table is soft-norms' own, factored out of `canonicalNorm` as `VE.SoftNorms.Wire.softDefault` (no behaviour change to `canonicalNorm`). Python: `rights_normal_form` in `ve/readings.py`, used by `rights_meaning_id`, the only rights id function (the loader `ve/document/load.py`, the reading-set check and the binding of Lean's answer, `ve/document/lean.py`, all call it; no call site changed) | `#guard`s beside `rightsNormalForm`; `test_rights_meaning_id_omits_soft_defaults` |
| Lean and Python agree (differential over the rights fixtures) | `tests/test_rights_meaning_id.py` | `test_lean_and_python_rights_meaning_ids_agree` (6 fixtures: omitted, defaults, nulls, `mode: default`, power line omitted and with defaults; Lean's `document` mode, Python's retained loader and `rights_meaning_id` give one id per unit) |
| Every stored rights id and fixture recomputed | No stored id changes: the 8 rights contents recorded in `tests/data/` (`relay-gate-cases.jsonl` 3, `route-cases.jsonl` 4, `scope/rights-reach-absent-main.json` 1) are already their normal form, and every other rights id in the suite is computed at test time through `rights_meaning_id`. Searched: every tracked `.json`, `.jsonl` and front-matter `.md` | `test_every_stored_rights_content_is_already_its_normal_form` |
| A stale (pre-change) id is not its new id | main's ids for the fixtures, recorded on main in `tests/data/rights-cfr-1-verdicts.json` | `test_a_stored_pre_change_id_is_not_its_new_id` |
| The condition test fails on main first | `evidence/condition-test-on-main.txt`: 15 failed of 15 at `6db6ee16d` (a git worktree of main with main's Lean build), each on the "explicit default gives the omitted id" assertion | `test_rights_meaning_id_omits_soft_defaults` |
| No verdict changes (DRI adv0838 item 3 (b) negative test) | `tests/data/rights-cfr-1-verdicts.json`, written on main before the change by `python -m tests.test_rights_meaning_id --write`: each fixture's `ve document check` answer, its loaded units without `meaning_id` (statuses, contents as written) and main's meaning ids. A full diff of the unstripped answers on main and on this branch showed no difference at all (the check answer prints no unit meaning id) | `test_no_verdict_or_reason_changes` |

`null` soft fields: the rights wire reads a `null` soft field as absent (`rightsWireJson`), and soft-norms' unit id
(`softCanonical`, Python's `SoftRule.to_dict`) omits it, so the normal form omits a `null` `mode`, `hard` or
`alterable` too, beyond `canonicalNorm`'s table (which already covers `rank: null` and `exception: null`). This is
the only point where the rights normal form is wider than `canonicalNorm`; `canonicalNorm` and the soft document hash
are unchanged. A value of another JSON type (`hard: 0`) is not a default, as Lean's `Json` reads it.

Not delivered: nothing of the item. Python keeps its own copy of the normal form (`_SOFT_DEFAULTS`, five rows) because
`rights_meaning_id` also runs on Python-only paths (the retained loader, the reading-set check); the differential
holds the two equal. Moving those paths to a Lean mode is a route of its own and is not needed by this item.

## Seeded bugs (each restored; the failing test named)

| # | Language | File | Bug | Fails |
|---|---|---|---|---|
| 1 | Python | `ve/readings.py` | the normal form skipped (`rights_meaning_id` hashes `content`) | `test_rights_meaning_id_omits_soft_defaults` (15 cases), `test_lean_and_python_rights_meaning_ids_agree[defaults, nulls, power-defaults]`, `test_a_stored_pre_change_id_is_not_its_new_id`, and the negative test `test_no_verdict_or_reason_changes` (the defaults fixtures become `CheckerUnavailable: the Lean document answer is not bound to the document sent`): 20 failed |
| 2 | Python | `ve/readings.py` | a non-default value dropped (`_soft_default` true for every `mode`) | `test_rights_meaning_id_omits_soft_defaults[mode-*]` (the different-id case, 3), `test_lean_and_python_rights_meaning_ids_agree[default-mode]`, `test_no_verdict_or_reason_changes`: 5 failed |
| 3 | Lean | `lean/VE/Service/Document.lean` | `rightsNormalForm` keeps `null` soft fields | `#guard` at `Document.lean:177` (build fails) |
| 4 | Lean | `lean/VE/Service/Document.lean` | `rightsContentOf` binds the content as written | `test_lean_and_python_rights_meaning_ids_agree[defaults, nulls, power-defaults]`, `test_no_verdict_or_reason_changes`: 4 failed |
| 5 | Lean | `lean/VE/SoftNorms/Wire.lean` | `softDefault` treats `hard: true` as the default in place of `hard: false` | `#guard` at `Document.lean:177` (build fails) |

## Trust

TRUST-PLACEHOLDER

## Size

Hand-written lines (`git diff --numstat 6db6ee16d`, generated files and the tool-written snapshot excluded):
SIZE-PLACEHOLDER.

## Pilot bytes

None expected to move: no stored id changes and no verdict changes; a pilot document that writes a soft default in a
right line would change only that unit's meaning id (an estimate; nothing is claimed before a pilot audit).

## Next item

None.
