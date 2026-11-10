# norm-defaults-cfr-1: the norm-defaults mode's answers bound to their request (REPORT)

Summary: READY FOR REVIEW. The client refuses (`CheckerUnavailable`) a norm-defaults status row whose tuple or rules
are not the request's and a certificate row whose premise count is not its certificate's (`bind_answers`,
ve/backends/lean_service.py); the assurance manifest binds all 13 kinds the mode answers (new operation
`norm-defaults.route`, one probe per kind). Python only; Lean +0, trust +0. One DELTA row (R16, conservative). No DRI
signature reserved. Next item: none. Base de7fb9469 (`git merge-base HEAD main`).

Source: regrade #3 (ND-FC2, grade A) in reviews/l1-c-regrade-norm-defaults-b-20261109.md; DRI 2026-11-10
reviews/dri-decisions-20261110-lp0001.md Q2. The plan is the code on main; no plan section or statement gate.

## Deliverables (all AGENT)

| # | Task row | Delivered by |
|---|---|---|
| 1 | The manifest lists every kind the norm-defaults mode answers | ve/assurance-manifest.json: new lean-only operation `norm-defaults.route` with one `ve_service`/`norm-defaults` binding per kind (`norm-defaults-elaborate`, `-conflict`, `-status`, `-gaps`, `-report`, `-certificate`, `defaults-elaborate`, `-coherence`, `-certificate`, `-model`, `-zone`, `acts-elaborate`), each with its declared response and counts; `admission` stays the `admission` operation's binding. One accepted probe per binding: conformance/binding_probes.py `_norm_defaults_cases`. Test: `test_the_manifest_lists_every_kind_the_mode_answers` (manifest kinds == the `kind` table of ve/backends/lean_service_schema/norm-defaults.json, which Lean's ResponseShape renders) and tests/test_assurance_manifest.py `test_every_lean_binding_has_a_probe`, `test_every_lean_binding_routes_its_operation`, `test_every_real_answer_is_counted_and_indexed` |
| 2 | A status row naming a rule or entity absent from the request, or a certificate whose premise count differs from the premises it carries, is refused (CheckerUnavailable), by binding in the relay | ve/backends/lean_service.py `bind_answers` / `MODE_BINDINGS` / `_bind_norm_defaults`, called in `LeanService._roundtrip` after `check_response`, so a refusal is a `_Failure`: one retry, then `CheckerUnavailable`. No Lean change was needed: Lean already echoes the tuple and the certificate's `premise_meaning_ids` are in the request |
| 3 | `test_norm_defaults_response_binding`: forged rule, entity and premise count refused; genuine passes; manifest kinds | tests/test_norm_defaults_response_binding.py (below) |

### What is bound, and why it is a binding and not a decision (R8)

- **Tuple.** `norm-defaults-status` `tuple` equals the case's `tuple` (`Wire.replayStatusIn` zips the request ids
  with the predicate's sorts after checking their number, and `statusFields` returns them).
- **Rules.** Each name in `rules` is the `name` of a `norm` object of the case's rule source: `norms` (author and soft
  norms) or `document` (a rights document's `right.lines[*].norm`). Under `acts@0` only, Lean answers with the part
  name `<rule>-a<k>` of a rule whose joined act it split (`VE.Acts.Elaborate.partRule`, lean/VE/Acts/Elaborate.lean:35;
  a genuine acts status answers `["r027-a1"]`), and the binding accepts that form for a request rule. The binding reads
  that one naming form; `test_genuine_answers_pass` asks Lean for a split act, so a renamed part fails there (closed:
  the answer would be refused, never shown). A name may appear once (Lean's rule names are unique, `selectedRules` is
  per predicate and `pairPartners` never repeats; 0 of 21,289 genuine rows repeat one).
- **Premise count.** `norm-defaults-certificate` `premises` is `len(certificate.premise_meaning_ids) -
  len(premises)`: Lean's `Wire.bindingOk` refuses a certificate unless its ids are those of `background ++ fill ++
  elaborate ++ premises`, and the row counts `premisesU U []` (Run.lean:281); the soft and layered branches count
  `premisesX` the same way (Run.lean:130).
- **Not bound** (Lean's to choose, stated so no reader takes them as bound): which request rules decide (an empty
  `rules` is a genuine answer: UNKNOWN, or a point settled by its default), and `differs`.

## Fails on main, passes on HEAD

`git show main:ve/backends/lean_service.py > ve/backends/lean_service.py` (main's client, the rest of HEAD), then
`uv run pytest -q -p no:cacheprovider tests/test_norm_defaults_response_binding.py`: `17 failed, 1 passed`
(evidence/on-main.txt: every forged row and the manifest test fail; the one pass is the genuine-answer test). The
manifest test fails on main's manifest by itself (its kinds are `["admission"]`). On HEAD: see "Test runs".

## Genuine answers

`PYTHONPATH=docs/premise-packs/norm-defaults-cfr-1/evidence NDLOG=<file> uv run pytest -q -p genuine_pairs -n 4`
over tests/test_defaults_answer.py, test_document_chain.py, test_events_route.py, test_norm_defaults_layered.py,
test_norm_defaults_relay_english.py, test_norm_defaults_soft_kinds.py, test_norm_defaults_switch.py,
test_norm_defaults_three_way.py, test_alternatives_fill.py and test_norm_defaults.py (`282 passed`), then
`uv run python docs/premise-packs/norm-defaults-cfr-1/evidence/genuine_pairs.py <file>`: 21,344 genuine ok rows
(21,282 status on norms, 7 status on a rights document, 55 certificates on plain, soft, events and layered sources),
**0 refused** (evidence/genuine-pairs.json).

## Seeded bugs

(below)

## Test runs

(below)

## Size, trust, pilot bytes

- Hand-written lines: 418 outside generated files (`light-lane.py check`: NOT, 418 > 150). Over the task's estimate of
  200 because the manifest change needs a probe per binding (45 lines) and the test fuzzes each bound field
  (BUILDER-CHECKLIST 1 and 5); evidence is 70 lines. ve/assurance-manifest.json (+280) is a generated-class file whose
  values are hand-reviewed pins.
- Trust: `uv run python tools/trust_map.py --check` on HEAD: `K +0, S +0, D +0, G +0, tied +0, unclassified +0,
  trusted +0`, PASS. No Lean change, so no trust-mutant sweep (build checklist 13a is for trusted Lean growth) and no
  FOLLOW-UPS row.
- Pilot bytes: 0 expected (a binding of relayed rows; no verdict, wording or coverage changes).

## Spec re-read

- "status rule or tuple names a rule or entity absent from the request" against the task file and
  reviews/l1-c-regrade-norm-defaults-b-20261109.md:115: tuple, rules and premises bound as above.
- "certificate premise count differs from the premises it carries" against lean/VE/NormDefaults/Run.lean:281 and
  lean/VE/Route/Wire.lean:553 (`bindingOk`).
- "the manifest lists every kind the norm-defaults mode answers" against the mode's schema `kind` table and
  lean/VE/NormDefaults/Run.lean:219-283 (`runOtherCaseIn`), lean/VE/Defaults/Route.lean:15 (`defaultsKinds`).
