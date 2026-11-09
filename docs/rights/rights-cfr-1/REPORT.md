# rights-cfr-1 REPORT: a rights meaning id binds the normal form (rights.md 3.5)

Status: delivered, no signature reserved; HEAD is the branch tip (`git log -1`), base `6db6ee16d` (merge base with main).
Open: none in this item; FOLLOW-UPS row "## rights-cfr-1" asks for the R16 ties pass (and notes the Python table twin).
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
| (1) The id is computed over the normal form; Lean owns it, Python relays, both agree | Lean: `rightsNormalForm` (`lean/VE/Service/Document.lean`), applied where `rightsContentOf` binds a rights unit; its default table is soft-norms' own, factored out of `canonicalNorm` as `VE.SoftNorms.Wire.softDefault` (`canonicalNorm` unchanged in behaviour). Python: `rights_normal_form` in `ve/readings.py`, used by `rights_meaning_id`, the one rights id function, which the loader (`ve/document/load.py:112,139`), the reading-set check (`ve/readings.py:263`) and the binding of Lean's answer (`ve/document/lean.py:271`) call; no call site changed | `test_rights_meaning_id_omits_soft_defaults` (each case compares Lean's `document`-mode id with Python's); differential `test_lean_and_python_rights_meaning_ids_agree` (6 fixtures: omitted, defaults, nulls, `mode: default`, power line omitted and with defaults; Lean, Python's retained loader and `rights_meaning_id` give one id per unit); `#guard`s beside `rightsNormalForm` and `softDefault` |
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

Python twin: `ve/readings.py` `_SOFT_DEFAULTS` (five rows) mirrors `softDefault`, because `rights_meaning_id` also runs
on Python-only paths (the retained loader, the reading-set check) and binds Lean's answer; the task's deliverable (1)
asks for this pair held equal by a differential, which the condition test and `test_lean_and_python_rights_meaning_ids_agree`
are. Generating the table from Lean is noted in the FOLLOW-UPS row. A rights reading in a reading set gets its id
through the same `rights_meaning_id` (`ve/readings.py:263`); no fixture of this item writes a defaulted rights reading.

Spec re-read:
- `rightsNormalForm` and `rights_normal_form` against rights.md:441 ("every soft field at its default omitted as
  soft-norms 3.4 does"; lines included; `right_lines` likewise).
- The default table against soft-norms.md:331-332 (`mode: strict`, no `rank`, empty `alterable`, no `exception`,
  `hard: false`).
- The DELTA 1 row against reviews/dri-decisions-20261109-lp0801.md item 1 (as quoted in the task: the ids SIGNED when
  the condition test passes and every stored id is recomputed).

## Seeded bugs (each restored; outputs saved)

| # | Language | File | Bug | Fails (evidence) |
|---|---|---|---|---|
| 1 | Python | `ve/readings.py` | the normal form skipped (`rights_meaning_id` hashes `content`) | `test_rights_meaning_id_omits_soft_defaults` (15), the differential (3), the negative test `test_no_verdict_or_reason_changes` (the defaults fixtures become `CheckerUnavailable`), `test_a_stored_pre_change_id_is_not_its_new_id`: 20 failed (`evidence/seeded-1.txt`) |
| 2 | Python | `ve/readings.py` | a non-default value dropped (`_soft_default` true for every `mode`) | the different-id cases `test_rights_meaning_id_omits_soft_defaults[mode-*, exception-*]` (6), the differential `[default-mode]`, the negative test: 8 failed (`evidence/seeded-2.txt`) |
| 3 | Lean | `lean/VE/Service/Document.lean` | `rightsNormalForm` keeps `null` soft fields | `#guard` at `Document.lean:177` (`evidence/seeded-3.txt`) |
| 4 | Lean | `lean/VE/Service/Document.lean` | `rightsContentOf` binds the content as written | `test_rights_meaning_id_omits_soft_defaults` (15, Lean's id against Python's), the differential (3), the negative test, the stale-id test: 20 failed (`evidence/seeded-4.txt`; full build, the mutant `ve_service` pinned for that run only) |
| 5 | Lean | `lean/VE/SoftNorms/Wire.lean` | `softDefault` reads `hard: true` as the default in place of `hard: false` | `#guard` at `Document.lean:177` (`evidence/seeded-5.txt`; at this HEAD also the `#guard` beside `softDefault`) |

`mutants.json` lists them per definition. Trust mutants (`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/rights/rights-cfr-1/trust-mutants-allow.json
--json docs/rights/rights-cfr-1/trust-mutants.json`, ran on the VM, the Mac unreachable): 59 mutants of the 2 new trusted
definitions, 46 KILLED, 0 SURVIVOR, 0 UNKNOWN, 9 INVALID, 4 ALLOWED (the `list-empty` mutants of `rightsNormalForm`,
which do not typecheck; `trust-mutants-allow.json`), exit 0 (`trust-mutants.json`). A first sweep left 9 survivors
(`softDefault`'s rows, checked only by a `#guard` outside its directory; `take 1` / `reverse` / `dropLast` of the
body's members and of the lines, which the one-line fixtures did not move); the `#guard` beside `softDefault` and the
two-line, `holder`-before / `lines`-last `#guard`s beside `rightsNormalForm` kill them.

## Trust

`uv run python tools/trust_map.py --check` against `6db6ee16ddb1` on this HEAD: K +0, S +0, trusted +32 (V):
`lean/VE/Service/Document.lean` +26 (`rightsNormalForm`), `lean/VE/SoftNorms/Wire.lean` +6 (`softDefault`). Recorded
with `trust_map.py --allow` (docs/trust-baseline.json), "SIGNED by standing ruling R16 (DRI-RULINGS.md), rights-cfr-1,
2026-11-09"; within R16's 150 lines, no K growth; each new trusted definition is exercised by `#guard`s and tests that
fail on its mutants (above). FOLLOW-UPS.md "## rights-cfr-1" asks for the ties pass. No Python decision path is
deleted, so R6 covers nothing here.

## Size

SIZE-PLACEHOLDER

## Pilot bytes

None expected to move: no stored id changes and no verdict changes; a pilot document that writes a soft default in a
right line would change only that unit's meaning id (an estimate; nothing is claimed before a pilot audit).

## Next item

None.

## Self-review against BUILDER-CHECKLIST

SELFCHECK-PLACEHOLDER
