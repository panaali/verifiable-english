# rights-cfr-1 REPORT: a rights meaning id binds the normal form (rights.md 3.5)

Status: F2 ownership fix implemented and focused tests passed; F1 remains blocked by the read-only central FOLLOW-UPS.md mount.
Open: the R16 row must be copied from `FOLLOW-UPS.pending.md` into `/home/seyran/code/manage-agents/FOLLOW-UPS.md`.
No verdict changes (negative test below); the only user-visible deltas are the ids (DELTA 1, SIGNED by the DRI
2026-11-09, reviews/dri-decisions-20261109-lp0801.md item 1) and the trust growth (DELTA 2, R16).

Item rights-cfr-1 (DRI 2026-11-09, reviews/dri-decisions-20261109-lp0801.md item 1; regrade #1 of
reviews/l1-c-regrade-rights-20261109.md).

## The defect and the plan row

rights.md 3.5 (:441): a right unit's `meaning_id` is W1's digest over `{"environment_id", "ast"}` with `ast` the
right object "every soft field at its default omitted as soft-norms 3.4 does". On main both owners of the id hashed the
content as supplied: Python's `ve/readings.py` `rights_meaning_id`, and Lean's `document` mode
(`VE.Service.Document.rightsContentOf`, `nullableMeaningId` over the content as written). Probe: an omitted `mode` and
an explicit `mode: strict` gave two ids (`evidence/condition-test-on-main.txt`).

## Delivered (task deliverables)

| Deliverable | Where | Test / evidence |
|---|---|---|
| (1) The id is computed over the normal form; Lean owns it, Python relays, both agree | Lean: `VE.Rights.Wire.rightsNormalForm` and `rightsMeaningId` are shared by the document and identity routes. Python's `rights_meaning_id` calls the typed `identity` route with `kind=rights-meaning`; the retained loader, reading-set check and document-answer binder call it. The Python default table, normalizer and digest path are deleted. | `test_rights_meaning_id_omits_soft_defaults`; `test_lean_and_python_rights_meaning_ids_agree`; `test_rights_identity_is_relayed_from_lean`; `test_rights_identity_row_is_typed_and_bound`; Lean guards beside both definitions. |
| (2) Every stored rights id and fixture recomputed; a stale id is not its new id | No stored id changes: every rights content under `tests/data/` (`.json`, `.jsonl`, searched recursively) is already its normal form. Main's ids for this item's fixtures are recorded in `tests/data/rights-cfr-1-verdicts.jsonl` (written on main by the item's recorder before the change, one line per fixture; nothing in the suite rewrites it) | `test_every_stored_rights_content_is_already_its_normal_form`; `test_a_stored_pre_change_id_is_not_its_new_id` (main's id differs from the new one exactly where a default is written, and a document stating main's id is refused with `unit meaning id does not match content` by Lean and by Python's retained loader, while the new id is accepted) |
| (3) `test_rights_meaning_id_omits_soft_defaults`, failing on main first | 15 cases (5 soft fields x `right/norm`, `right_lines/liberty`, `right_lines/recognition`): omitted, default and `null` give one id, an admissible non-default another | `evidence/condition-test-on-main.txt`: this branch's test file run in a worktree of main `6db6ee16d`: 15 of 15 cases fail, each on `assert python[1] == python[0] and ...` (22 of 26 of the file fail there) |
| No verdict changes (DRI adv0838 item 3 (b), the negative test) | `test_no_verdict_or_reason_changes`: every fixture's verdicts and reasons (unit statuses, coverage by status, residual and its reasons, premises status, the rights report with each conflict's verdict and status text) equal main's recorded ones; each fixture's meaning ids are its normal form's main id; a defaults fixture's whole check answer equals its normal form's but for `document_id` | `evidence/answers-head-vs-main.txt` (the full answers at this tree against main's: no check-answer key differs, units identical, ids changed only in `defaults`, `nulls`, `power-defaults`); fails on seeded bugs 1, 2 and 4 (`evidence/seeded-1.txt`, `seeded-2.txt`, `seeded-4.txt`) |
| R8 rebind of the changed field | Lean's answer naming main's stale id, or another unit's id, for a rights unit | `test_a_lean_rights_id_away_from_the_normal_form_is_refused` (`CheckerUnavailable: ... is not bound to the document sent`) |

`null` soft fields (a stated reading of 3.5, not a widening): the rights wire reads a `null` soft field as absent
(`rightsWireJson`), and soft-norms 3.4 names the defaults "no `rank`" and "no `exception`", so a `null` `mode`, `hard` or
`alterable` is at its default too and the normal form omits it, beyond `canonicalNorm`'s table (which already covers
`rank: null` and `exception: null`). Only the rights normal form does this; `canonicalNorm` and the soft document hash
are unchanged (`#guard` beside `softDefault`; the soft-norms tests in the selected run). A value of another JSON type
(`hard: 0`) is not a default (`test_the_normal_form_leaves_other_content_and_shapes_unchanged`). `limitation` and `bar`
objects (rights.md 3.2, :369, :379) have no soft field, so the normal form leaves them as written (`#guard` on a `bar`).

Review F2 is closed structurally: the Python table, normalizer and rights digest were deleted. The existing
`identity` service route now asks Lean for the rights meaning id. Its schema binds `id` and `kind` to the request and
types the digest; the encoder theorem compiled for the extended kind. The `content_json` transport member preserves
nullable soft fields without widening the restricted parser for the other identity kinds. Rust has no rights meaning-id
path to migrate. A rights reading in a reading set uses this same relay.

Spec re-read:
- `rightsNormalForm` against rights.md:441 ("every soft field at its default omitted as
  soft-norms 3.4 does"; lines included; `right_lines` likewise).
- The default table against soft-norms.md:331-332 (`mode: strict`, no `rank`, empty `alterable`, no `exception`,
  `hard: false`).
- The DELTA 1 row against reviews/dri-decisions-20261109-lp0801.md item 1 (as quoted in the task: the ids SIGNED when
  the condition test passes and every stored id is recomputed).

## Review fixes

F1: the exact probe failed before the fix and still fails because the central file is mounted read-only.
`FOLLOW-UPS.pending.md` contains the required `## rights-cfr-1` row covering both trusted definitions. This is a
handoff, not an assertion that R16 is signed. The probe cannot be a hermetic repository test: it reads a file outside
this checkout, and the test suite writes only under `tmp_path`. The post-fix output is
`evidence/review-f1-post-probe.txt`.

F2: `VE.Rights.Wire.rightsNormalForm` is the single normalizer. The same module's `rightsMeaningId` is used by
`VE.Service.Document.rightsContentOf` and `VE.Service.Standalone.identityCase` (`rights-meaning`). Python's
`rights_meaning_id` now relays the latter. `ve/document/load.py`, `validate_reading_sets`, and the document-answer
binder use it. The Python `_SOFT_DEFAULTS`, `_soft_default`, `rights_normal_form` and local rights digest were deleted.
The existing response shape has a typed, request-bound `rights-meaning` kind; its encoder theorem compiled.
The identity route reads the profile list and recomputes Lean's canonical environment ID. Admission remains with the
document route: rights content also appears under `readings@1`, and a norm with citations can use a generated soft
frame without `rights@0`. The selected wire corpus exposed the former and the 16e rights corpus the latter.
`test_rights_meaning_id_accepts_readings_rights_environment` and
`test_rights_identity_does_not_admit_generated_soft_frame` cover both; the full 16e rights file passed (67 tests).

Regression IDs: `tests/test_rights_meaning_id.py::test_rights_meaning_id_omits_soft_defaults` (15 right/slot/field
cases); `test_lean_and_python_rights_meaning_ids_agree` (six document fixtures);
`test_reading_set_binds_defaulted_right_through_the_lean_identity` (reading-set caller);
`test_rights_identity_is_relayed_from_lean` (architectural delegation);
`test_rights_identity_row_is_typed_and_bound` (dropped, retyped and unbound result fields);
`test_rights_meaning_id_accepts_readings_rights_environment` (combined profile caller);
`test_rights_identity_keeps_nonrights_content_in_soft_environment` (non-rights content);
`test_rights_identity_does_not_admit_generated_soft_frame` (generated frame);
`test_a_lean_rights_id_away_from_the_normal_form_is_refused` (document answer binding). Lean `#guard`s beside
`rightsNormalForm`, `rightsMeaningId` and `softDefault` exercise the respective definitions.

The prior branch's seeded-bug outputs remain in `evidence/seeded-1.txt` through `seeded-5.txt`; they describe the
pre-review twin implementation. For this fix, changing Python's relay to return the request `id` in place of
`identity_id` made `test_rights_identity_is_relayed_from_lean` fail (`evidence/review-seeded-python.txt`); the source
was restored and all 52 focused rights and soft candidate tests passed. The Lean trust mutant sweep plants changes in scratch trees;
the first sweep found digest environment-binding and identity-schema survivors. A guard for each class was added;
the final wrapper sweep killed both classes (`mutants.json` entries 7 and 8).

## Trust and verification

The final-source `lake build` completed (1320 jobs), and `tools/trust_map.py --check` passed (K +0, S +0, V +35).
The 52 focused rights and soft candidate tests and all 67 tests in `test_b16e_rights_document.py` passed.
The +35 itemises as `Rights/Wire` +27, `SoftNorms/Wire` +6, `Service/Document` +1 and
`ResponseShape/Schemas/Identity` +1. The +3 R6 allowance covers the Lean relay and its typed schema replacing
the deleted Python decision path. The final trust mutant sweep, through `mac-pytest.sh --trustmut`, classified all
94 planned mutants on the prior source: 81 KILLED, 9 INVALID, 4 ALLOWED with documented reasons, 0 SURVIVOR,
0 UNKNOWN and 0 NOT RUN. The final-source audit, mutant sweep and selected run are pending.

## Pilot bytes and next item

No stored rights id changed, so no pilot byte change is expected. A pilot source that writes an explicit soft default
would get a new meaning id; this has not been measured. No new product item is deferred. F1 awaits the central row
copy in the writable management workspace.
