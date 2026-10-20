# jt-2 report: `judgments@0` in Lean's document mode (JT-2, Lean part)

**DRI signature needed: DELTA row "New profile `judgments@0`"** (an environment listing the profile is accepted where
main refuses it; DRI-RULINGS.md lists widening as never covered by a standing ruling). It is the reason this item
stops at review-ready; everything else is built and checked. Precedent: et-7b row 1 (dri-decisions-20261019.md #1).

Plan: judgment-terms-PLAN.md at 64339b6ce, batch JT-2 (copied on main, identical); spec judgment-terms.md 4.2, 8 and
11. Statement gate: the plan's change log records the statement review's FIX joint position (draft 3, A5 for JT-2)
and its ACCEPT (draft 4). Shared-file queue: SYNTHESIS 4.2 (document mode) and 4.3 (AR-10's table first; ar-10a
merged). DRI-DECISIONS-PHASE2 JT-R1..R5, X2, X3: none applies to this part (R4's grade check is JT-4's; X2/X3 are
jt-crossplan-fixes').

## Plan rows

| Plan row | Delivered | Where | Checked by |
|---|---|---|---|
| `Judgments.records` in place of `Loader.openTermNames`, then `Judgments.admit` over `E.rv.environment`, `E.rv.definitions` | yes; `regulated` is `Env.regulated` | `lean/VE/Service/Document.lean` `check` | 11.2 rows, `test_admission_of_each_record_in_record_order` (13) |
| Each unit's view (`viewOf`) from its own content or its active set's raw candidates, never `readingsSets`' `top`; a pending reading `none`; status in unit order; W2 and `readings@1` sets alike | yes (`UnitContent.judged`, `setCandidates`, `judgedViews`) | same | 11.3 and 11.9 rows (`test_status_and_usage_of_each_unit`, 24), `test_readings_sets_are_read_from_their_raw_candidates`, the pilots' profile list (4) |
| The report gains `judgments` (usage map, spec 8.3) | yes, only under the profile | `usageJson`, `encode` | J-λ: no field without the profile |
| The profile's row in AR-10's table: requires `documents@1`, refuses nothing; composition statement for each newly admitted combination | yes; `gate_judgments`: every sorted list with `documents@1` gets the answer of the same list without `judgments@0` | `lean/VE/Compose/Dispatch.lean` | theorem, `Compose/Examples.lean` `#guard`s |
| Response shape and encoder theorem | yes (`judgments`, `usage_fits`, `document_fits`) | `lean/ResponseShape/{Schemas,Encoders}/Document.lean` | `test_the_answer_fits_its_schema_and_models_refuse_the_profile` |
| Generated schema and inventories | yes, `regen_generated.py --write` | `ve/backends/lean_service_schema/document.json` | `regen_generated.py --check` |
| Python relay (schema and binding, order check), `tests/test_judgments_answer.py` fuzz tests, route-cases fixtures, `ve/openterms.py` off the live path, layer-policy entry | **not here: jt-2b** (size rule; see Size) | | |
| Plan seeded bugs | Lean 1 and 2 here; Python 1 and 2 (relay) in jt-2b | `mutants.json` | |

Needed by the plan and not in its text (Lean-owned, small):

- **Composition with the decoders.** Every frozen decoder refuses a profile it does not know, and
  `Route.Gate.decodeEnvelope`'s refusal theorems must stay true. `Compose.documentLayers` / `withoutDocumentLayers`:
  the environment mode, the document mode and the readings frame decode the environment without `judgments@0`; the
  table gate and every identity read the list as written. Without the profile nothing of this runs.
- **Compositions refused by name** in the document mode: `alternatives@0`, `rights@0`, `risk@0`, `soft-norms@0` and
  senses documents (`CheckerUnavailable: judgments@0 with <p> needs its composed Lean route`): their contents are no
  `Judgments.Content`.
- **Other Lean modes** (check, model, the definitions route Python's `Environment` calls) still refuse the profile.
  Their identities come from the envelope whose `AllowedFamily` theorem forbids an unknown profile, so composing them
  is a design step of its own (jt-2b). Until then `Compose.environmentProfiles` (Python's `BY_NAME`) leaves the
  document layer out, Python's model projection refuses it, and Python's own loader refuses a `judgments@0`
  document, so `ve document` is `CheckerUnavailable` on it: never a Python status.

Sibling lessons (jt-1b-review F1, F2): which judgment each refusal names and both lists' order are pinned through
the service with two candidates each (`two-specified`, `two-unlisted`, `two-unused`, `two-rows`), and by mutants
that reverse the unit list and the unused list.

## Seeded bugs and mutants

[`mutants.json`](mutants.json): 31 of 31 killed, one or more per new trusted definition and per claimed behaviour.
Lean (30): applied to the committed tree, `lake build VE.Service.Document`, then `tests/test_judgments_document.py`
over a probe that answers the `document` and `environment` modes from the freshly compiled modules (no relink of
`ve_service`), the tree restored. The plan's two Lean bugs: the status hook skipped
(`pure u`) fails 15 tests (J-β first); a norm candidate read as `top` fails
`test_readings_sets_are_read_from_their_raw_candidates`. The shape mutant (`term` typed as a nat) is caught by the
regenerated schema's check of a genuine answer, not by `usage_fits` (the skeleton reads a `common.json` reference as
any). `environmentProfiles` kept unfiltered fails `Compose/Examples.lean:240`. Python (1):
`ve/document/load.py` without the guard fails `test_python_never_decides_a_judgments_document`. One equivalent
mutant is not listed: `judgedViews`' `asserted` argument, which nothing in this item reads (JT-4's criteria do).

## Trust, size and evidence

- Trust (`tools/trust_map.py --check`, PASS on the final HEAD against `75a9bcef9`): K +0, S +0, untied V +113:
  `VE/Service/Document.lean` +79, `ResponseShape/Schemas/Document.lean` +12, `VE/Service/Standalone.lean` +11,
  `VE/Compose/Dispatch.lean` +11. Allowance signed by R16; FOLLOW-UPS "## jt-2 (2026-10-20)" asks for the ties pass.
- Size: about 640 hand-written lines before this report (Lean 210, the fixture file 393, Python 3, DELTA 12, side
  tables and pins about 25), plus `mutants.json` (written by the harness). Over the ~600 guideline mostly by the
  spec's fixture rows, which the Lean part needs for its seeded bugs; the Python relay was cut to jt-2b as the task
  directs.
- Tests: the selected plan on the Mac runner passed on `fae90056d` (exit 0, 0 failures), after fixing what its first
  runs found (the model oracle's profile coverage, the conformance owned-profile check, the assurance-manifest pins,
  b16b's seeded-fault text). After the two syncs with main: the touched files' tests (719 passed), `lean/audit.py`
  PASS, `regen_generated.py --check`, `gate_collection.py --check --prebuilt` (56 added, 0 removed). The full gate is
  the chain's, on this HEAD.
- Not run: whole-document pilots (L70); base/head timing (no pilot lists the profile; without it the path is
  unchanged).
- Pilot bytes expected to move: none from this item (no pilot lists `judgments@0`; `ve document` answers it only after
  jt-2b). JT-5a then expects Lean statuses on 13 constitution units (2,150 B), JT-5b on 18 UDHR units (1,945 B) after
  JT-5r; nothing is claimed before a pilot audit.
- Overlaps: `ve/document.py` was split by AR-16a (merged); the loader guard follows `_load_document` to
  `ve/document/load.py`. `tools/layer_policy.py` (ap-1a) was not touched. `lean/VE/Readings/Wire.lean` and
  `Service/Standalone.lean` had no in-flight editor.

## Next item

**jt-2b**: the relay of `judgments` (R8 binding and order, fuzz tests, recorded route cases, plan seeded bugs P1 and
P2), `ve/openterms.py` off the live path with its layer-policy entry, and the Lean modes Python's `Environment` and
model operations call composing with `judgments@0` (an identity design for document layers), after which
`environmentProfiles` lists it and `ve document` answers such a document.

## Self-review against BUILDER-CHECKLIST

1. PASS: the new field is typed in `document.json` (`test_the_answer_fits_its_schema_and_models_refuse_the_profile`); until jt-2b Python relays no `judgments` row (`_bind_document_answer`'s exact key set), so every mutant of it is `CheckerUnavailable` (`test_python_never_decides_a_judgments_document`).
2. PASS: plan rows table above; the relay rows moved to jt-2b by the task's size rule, named here and in FOLLOW-UPS.
3. PASS: `mutants.json`, 31 killed, each by a named test or `#guard`; the build-step catches are not counted.
4. PASS: J-λ's eight documents without the profile answer as on main (`test_without_the_profile_every_answer_is_todays`); Rust unchanged and never sees the profile.
5. N.A.: no relayed field is bound in this item (jt-2b); the request-side records are W2's (`test_the_profile_requires_documents_and_its_records_are_w2s`).
6. PASS: synced with main `75a9bcef9`; the chain runs the full gate on the final HEAD.
7. PASS: DELTA's trust row cites R16; the widening row reserves the DRI's signature and is this report's first line.
8. PASS: DELTA lists the profile's acceptance and refusals per mode; lists without the profile are unchanged (J-λ).
9. PASS: the selected plan contained `tests/test_judgments_document.py` and the inventory tests its first run caught.
10. PASS: `gate_judgments`, `usage_fits` and `document_fits` build on the final HEAD; the shape mutant's limit is reported above.
11. N.A.: no budget, limit or deadline code.
12. N.A.: no pilot lists the profile; without it the document path is unchanged; the new work is one pass per unit.
13. PASS: `gate_collection.py --check --prebuilt`: 0 removed, 0 refused, 0 stale, 0 malformed.
