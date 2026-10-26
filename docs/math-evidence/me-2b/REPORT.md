# me-2b report: the `calc` service mode (math-evidence ME-2, second part)

No DRI signature is reserved. DELTA row 1 (the mode answers) cites SYNTHESIS 2.2's table row that lists ME-2's mode,
as the task asks; row 2 (trust) cites R16. The item is cut by the size rule: the mode, its shape and encoder, its
schema, deadline, case decoder and service-level route cases are here; the row fields and the words checks are the
next item **me-2c** (below, "Not delivered").

## Statement gate

ME-S passed its bounded re-checks (manage-agents `math-evidence-p3ver1.final.md`, then `math-evidence-p3ver2.final.md`:
PASS); plan and spec are main's. The two statements this item proves equal the reviewed text of spec 3.4 and plan 3.2
after whitespace normalisation (checked by a script over both documents and the Lean files):

- `theorem runMode_calc (j : Lean.Json) : runMode .calc j = VE.Calc.Run.runCaseReported j` (`lean/VE/Service/Protocol.lean`, `rfl`; listed in `lean/VE/Audit.lean`);
- `theorem runCaseReported_fits (j : Lean.Json) : ResponseShape.Fits j ResponseShape.Skeletons.calc (VE.Calc.Run.runCaseReported j)` (`lean/ResponseShape/Encoders/Calc.lean`; listed in `lean/ResponseShape/Audit.lean`).

`calc` is a Lean keyword: the skeleton is declared `«calc»`, and the dotted name in the reviewed statement resolves to
it unchanged. No row-field statement is proved here (cut). No statement changed.

## Plan rows (ME-2's mode half; task order)

| Row | Delivered | Where, checked by |
|---|---|---|
| `Mode.calc` in AR-10's registry (constructor, name, `modes` entry) | yes | `lean/VE/Service/Registry.lean`; `modes_complete`, `registry_modes`, `registry_names_nodup`; the handshake (`envelope.json`, generated) |
| Dispatch line and `runMode_calc` | yes | `lean/VE/Service/Protocol.lean` |
| `MODES` in `ve/backends/service_schema.py` | yes, generated: `MODES` reads the handshake's list from `envelope.json` (ar-10b), so no hand line | `tests/test_lean_service.py::test_handshake` |
| `lean/ResponseShape/Schemas/Calc.lean`, `Encoders/Calc.lean` with `runCaseReported_fits` | yes; registered in `Schemas.lean`, `Skeletons.lean` and `Encoders.lean` (`runMode_fits`' case) | `lake build`; `tests/test_route_row_schemas.py` |
| `calc.json` | yes, generated (`tools/response_schemas.py` via `regen_generated.py --write`) | `regen_generated.py --check` |
| `DEADLINES` | yes: `"calc": (60.0, 60.0)` (at most 512 claims, each stopped at the 4,096-digit limit) | `test_the_deadline_keys_are_the_handshakes_modes` |
| Service-level route cases in `tests/data/route-cases.jsonl` | yes, 20 cases: R-1, R-2 (V-11), V-2, V-5 (20 claims), V-9, V-8 (rule per claim and per case), I-1 (`["sci", "5.89", -7]`) and its plain spelling, every claim form, `rounds-down`/`rounds-up`; the hostile set (a printed sign error, an unknown name, a name defined after its use, `pow` 65, a 41-digit literal, a forged `meaning_id`, a duplicate name, a duplicate claim id, no claims) | `tests/test_calc_service.py::test_route_cases_answer_their_rows` (every row's outcome, reason and reproduction, or the refusal); `tests/test_route_row_schemas.py` (shape, fuzz, Lean-side agreement) |
| Plan's seeded bug (claim i + 1's verdict for claim i) at the service level | yes | `mutants.json` `plan-seeded-bug` |
| Row fields `line`, `display`, `sides`, `tie`, `finding`, `rests_on`; words checks `VerbalisationCollision`, `ValueWordsForm`, `ReservedWord` | **me-2c** (size rule) | FOLLOW-UPS "## me-2b" |
| No hand-written `Dispatch.lean` rows, gate lemmas or `ve/profiles.py` rows | none written; the `calc@0` profile row stays with ME-10 (me-2's FOLLOW-UPS) | |
| `ve/assurance-manifest.json` decoder pins | no pin changes: the new decoder lines are in `lean/VE/Service/Protocol.lean`, which the manifest already classifies under `other_json` ("the service request decoder and dispatcher"); `lean/ResponseShape/Encoders/Calc.lean` gets its `other_json` reason (JSON access in proofs only), as the other encoders have | `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` |
| `ROADMAP.md` trust-cost line | yes | |

### The mode's case decoder (me-2's open B and its spelling question)

me-2 left two questions for this item (FOLLOW-UPS "## me-2"): duplicate JSON keys (`Lean.Json.parse` keeps the last of
two equal keys, so an earlier member over a limit was never seen), and exponent spellings (`65.0` refused, `6.4e1` read
as 64). The restricted decoder `VE.JsonInput.parse` refuses duplicate keys, fractions and exponents, but also negative
numbers, which `sci` needs, and it is a hash-frozen `ve.core@0.1` decoder. `VE.Service.calcCases` uses both, unchanged:
each case is first read by `restrictedCases` with every `-` outside strings read as a space (`unsigned`: one byte for
one, so the case cuts are the same), then, if admitted, read again with its signs by `Lean.Json.parse`. So a `calc`
request refuses, as every restricted mode does, duplicate keys (the PROBE's three forms), every fraction and exponent
spelling of an integer (`6.4e1`, `64.0`, `640e-1`: refused alike, which answers the spelling question), `null`, and
integers beyond 2^53; `-7` is read as −7, and a `-` inside a string or key is kept (`"a-b"` and `"a b"` stay two keys).
A refusal there is a request error, as in the other restricted modes. Guards: `lean/VE/Service/Protocol.lean` (signs,
refusals, escapes, routing); tests: `test_signs_are_read_and_strings_kept`, `test_duplicate_keys_are_refused`,
`test_an_exponent_is_an_integer_written_plainly`.

### Shape and binding

`calc.json#/row` is the case error, the runner's refusal `{"status": "error", "error"}`, or the answer
`{"status": "ok", "meaning_id", "rows"}`, whose rows are one per request claim, in order (`x-zip` over `/claims`),
each naming the request's claim id (`x-equals`). A row is decided (`holds`, `fails`, `undefined`, reason `null`) or
unknown (reason one of Lean's unknown texts, `Run.words` of `Run.outcomes`: the enum is computed from Lean, one owner);
`kind` is `"claim"` (the decoder admits no other kind yet). `reproduction` is bound to the request: the row shape
selects on the case (`x-select`), so a case without `software` has rows whose reproduction is `null` and a case with
it rows whose reproduction is `"unknown"`; the encoder theorem proves it through `decode_software` (a decoded case
names a software convention when its object has a `software` member).
`test_answers_are_bound_to_their_request` refuses a rebound or foreign claim id, a dropped, added or swapped row, no
rows, a reason on a decided row, an unknown row without a reason or with another text, a retyped reproduction or kind,
and a meaning id that is no digest; `test_a_reproduction_is_unknown_exactly_under_a_software_convention` refuses
`"unknown"` for R-1 and `null` for V-9; `tests/test_route_row_schemas.py` drops, retypes and empties every field and
mutates every node, with the Lean side (`ve_response_decode`) agreeing, and detects the weakenings `calc-rows-unbound`
and `calc-reason-free`.

The relay mutation gate (`tools/relay_mutation_gate.py --route service:calc`, 6 fixtures in
`tests/data/relay-gate-cases.jsonl` kept as `--record` keeps them, from the `calc` entry of
`tests/lean_service_corpus.py`): 953 mutants, 952 refused, 1 allowed, 0 failures. Its first run found the
reproduction binding above (a `"unknown"` retyped to `null` was accepted) and the allowed one: a batch decoder's case
error (a case nested beyond 255) without its `case_index` is the runner's refusal shape. `tools/relay-gate-allow.json`
`ME2B-1` (by design) gives the reason. `tests/data/binding-answers.jsonl.gz` was re-recorded
(`tools/binding_census.py --answers`, as after any Lean change): 6 `calc` answers are new, and the other modes'
recording catches up with main's relay-gate fixtures (alternatives, ask, the English modes, metered).

Deviations, each in FOLLOW-UPS "## me-2b": (a) spec 3.4 says a refused case answers the common case error with
`case_index`; the runner cannot see the index, so the refusal is `{"status", "error"}` and the service's binding
carries `index`, `digest` and `code` (spec wording, or the protocol adds it); (b) the reason enum is every unknown
text of 1.5, to be narrowed per kind when ME-5/8/9 add their kinds.

## Trust (R16)

`tools/trust_map.py --check` on the final HEAD: K +0, S +0, untied V +25, PASS with the allowance recorded:
`lean/VE/Service/Protocol.lean` +22 (`calcCases` 11, `unsigned` 6, the `decodeCases` and `runMode` lines),
`lean/VE/Service/Registry.lean` +2, `lean/ResponseShape/Schemas.lean` +1. The shape and the skeleton are G[R]
(`tools/trust-classes.json`). FOLLOW-UPS "## me-2b" asks for the ties pass (a refinement statement for `calcCases`).

## Seeded bugs and mutants

- [`mutants.json`](mutants.json): 13 seeded bugs, each applied alone and restored, all caught. Lean: the plan's bug in
  `lean/VE/Calc/Run.lean` (`Run.runCaseReported` gives row i claim i + 1's outcome; `Run.outcome_sound` stubbed so
  `ve_service` builds, the checker pin rewritten for the run) fails
  `tests/test_calc_service.py::test_route_cases_answer_their_rows`; `lean/VE/Service/Registry.lean` (`.calc` dropped:
  `modes_complete`); `lean/VE/Service/Protocol.lean` (dispatch: `runMode_calc`; `calcCases` twice, `decodeCases`,
  `unsigned` twice: their guards); `lean/ResponseShape/Schemas/Calc.lean` (`kind` "follows": `rowJson_fits`; a decided
  row's reason a string, which the skeleton does not read: six `tests/test_calc_service.py` tests refuse the genuine
  answers; the software select negated, and a software case given the plain answer: `runCaseReported_fits`, and
  `test_a_reproduction_is_unknown_exactly_under_a_software_convention`). Python: `ve/backends/lean_service.py` without the `calc` deadline fails
  `test_the_deadline_keys_are_the_handshakes_modes` and `test_handshake`. No Rust changed.
- [`trust-mutants.json`](trust-mutants.json) with [`trust-mutants-allow.json`](trust-mutants-allow.json):
  `tools/trust_mutants.py --max-mutants 1000` over the 5 trusted definitions the branch adds or changes. The first run
  had 9 survivors; the new guards (an empty string, an escaped quote and an escaped backslash before a sign; the
  routing of `decodeCases`) killed 3. The allowed: the initial `escaped` flag of `unsigned` (equivalent: read only
  inside a string, and the first character is read outside one), the five `modes` list mutants (killed by the proof
  `modes_complete`, which the tool does not count as a check; `registry-drop-calc` shows the build failure), and
  mutants that do not elaborate. Final numbers: "Final checks" below.

## Size

Hand-written lines over the merge base: Lean 184 (`Protocol.lean` 41, `Schemas/Calc.lean` 59, `Encoders/Calc.lean`
69, the registries 15), tests and fixtures 198 (`tests/test_calc_service.py` 155, `route-cases.jsonl` 20,
`relay-gate-cases.jsonl` 6, `lean_service_corpus.py` 9, `test_route_row_schemas.py` 8), side tables 33
(`tools/trust-classes.json` 16, the relay allow entry 10, the trust allowance 7), Python 2, and evidence and docs
about 230 (this report, DELTA, `mutants.json`, the allow file, ROADMAP): about 650, a little over the ~600 guide
because the relay mutation gate's finding (the reproduction binding) was fixed here rather than left to a later item. Generated:
`calc.json`, `envelope.json`, the inventories, `trust-mutants.json`, the binding census and the mode pins. The row
fields would add a shape change, Lean encoders for exact values, truncated displays and the line, `rests_on` (which
needs each value's support and span, not in spec 3.4's `Case`) and words checks that refuse words the me-2 fixtures
use: well over the rest of the budget, so they are me-2c.

## Pilot bytes and next item

0 expected (plan: "Bytes: 0"); nothing claimed. Next: **me-2c** (the row fields and words checks above), then qt-a3
(the protocol queue), me-4, me-6c and ME-P2. ME-3 (the Python relay) can start on the rows delivered here.

## Final checks

- Builds and static checks on the merged HEAD (main f1943fab6 merged; only the binding-answers recording conflicted,
  re-recorded): `lake build` (whole library), `python3 lean/audit.py` (PASS, 618 files), `regen_generated.py --write`
  then `--check` (33 entries), `trust_map.py --check` (K +0, S +0, V +25: PASS), `repo_map.py --check` (38 modes),
  `check_lean_imports.py`, `gate_collection.py --check --prebuilt` (20 added, 0 refused, 0 stale, 0 malformed).
- Selected tests (`mac-pytest.sh --select`, ve-mac-1): first on d4bee36e, 3 failures, all asking for `calc` in shared
  fixtures: `test_relay_mutation_gate.py` (no `service:calc` fixture) and `test_shape_binding_mutants.py[calc]` (no
  recorded answer); fixed by the corpus entry, the fixtures and the reproduction binding above. Then on 7a17bbe6: 2
  failures, `test_every_json_handling_lean_file_is_classified` (the encoder's `other_json` reason) and
  `test_random_malformed_responses_never_escape_schema[calc]` (no `calc` seed in `_SCHEMA_SEEDS`); both fixed, the two
  files and `tests/test_calc_service.py` rerun: 363 passed. After the merge of main, the affected files on ve-mac-1
  (`test_calc_service`, `test_route_row_schemas`, `test_relay_mutation_gate`, `test_shape_binding_mutants`,
  `test_lean_service`, `test_lean_service_schema`, `test_assurance_manifest`, `test_enum_domains`): 732 passed;
  `test_response_schemas.py`: 6 passed. No test in `main-known-red.txt` is touched.
- `tools/relay_mutation_gate.py --route service:calc`: 953 mutants, 0 failures (1 allowed, `ME2B-1`).
- `trust_mutants.py --max-mutants 1000 --allow ...` on the final Lean change (7a17bbe6; ran on the VM, no Mac slot):
  30 KILLED, 0 SURVIVOR, 0 UNKNOWN, 4 INVALID, 11 ALLOWED, 0 NOT RUN, exit 0.
- Not run: the full gate (the chain runs it on the final HEAD).

## Self-review against BUILDER-CHECKLIST

1. PASS: every field of a genuine `calc` answer dropped, retyped, emptied and mutated (`tests/test_route_row_schemas.py`,
   `tools/relay_mutation_gate.py --route service:calc`: 953 mutants, all refused but one allowed); the decoder side is
   me-2's guard 413 and `calcCases`' refusals (`test_duplicate_keys_are_refused`, the `calcCases` guards).
2. PASS: the plan-row table above; me-2c named for the row fields; no Python copy of a Lean decision (the reason enum is
   rendered from Lean); no permanent report test; overlap: no in-flight branch edits the hand-written files.
3. PASS: `mutants.json` 13 of 13 caught (Lean and Python, the plan's bug at the service level); `trust-mutants.json`
   exit 0; the two shape weakenings of `test_fuzz_detects_a_weakened_route_schema`.
4. PASS: `test_route_cases_answer_their_rows` checks the service's answers equal the runner's (the expected rows are
   RunExamples'); reordered keys and signs inside strings (`test_signs_are_read_and_strings_kept`, the key guard). No
   Rust change.
5. PASS: `test_answers_are_bound_to_their_request` (a foreign or rebound claim id, a dropped, added, duplicated or
   swapped row, no rows) and `test_a_reproduction_is_unknown_exactly_under_a_software_convention`; inputs: unknown
   names and a name defined after use are refused (route cases 13 and 14).
6. PASS: merged main f1943fab6 and regenerated; the selected and affected tests above; the gate is the chain's.
7. PASS: DELTA row 1 SIGNED by the DRI through SYNTHESIS 2.2's table row (the task's stated exception), row 2 R16 with
   per-file counts; FOLLOW-UPS "## me-2b" has the ties-pass row.
8. PASS: DELTA row 1 states the newly answered mode, the handshake's new mode and the decoder's refusals; nothing else
   moves (no other mode's answer changed: the relay gate and route schemas pass for every route).
9. PASS: the selected plan ran `test_relay_mutation_gate.py`, `test_shape_binding_mutants.py`,
   `test_assurance_manifest.py` and `test_lean_service.py`, and each caught a missing `calc` entry (above).
10. PASS: `runMode_calc` and `runCaseReported_fits` equal the reviewed text; the shape mutants `schema-kind`,
    `schema-select-negated` and `schema-software-unbound` break `runCaseReported_fits`.
11. PASS: limits are me-2's (each at and past its value); the mode's deadline is a `DEADLINES` row tested by
    `test_the_deadline_keys_are_the_handshakes_modes`; no timing in tests (`HANG_TIMEOUT` only).
12. N.A.: no runtime path of another mode changes; `calcCases` is one linear pass over the text plus the existing
    parsers.
13. PASS: no test removed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.

