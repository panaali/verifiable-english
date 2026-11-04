# df-5: the zone on the route (report)

**Status**: built; waiting for the chain's gate. HEAD: the last commit of feature/df-5. No DRI signature is reserved.
**What changed**: the kind `defaults-zone` (one row of PK-1's kind table) answers df-5a's zone with DE10's form,
`forcedAll` and the rows after DE10 (DE11, DE10f, DE13), chosen in Lean; `ve.defaults` relays and binds it and renders
the rows. `zoneMin` runs once per request (DRI 2026-11-04 item 2: `Zone.lean` refactored, statements unchanged).
**Open**: size (about 1,000 hand-written lines against 600; the DRI asked twice, no ruling yet: see "Size"); df-5b (the CLI path, W7's gate).
**DELTA**: D1 SIGNED by the DRI (reviews/dri-decisions-20261104-df-5.md item 1); T1 V +113 under R16. Bytes 0.

## Plan rows (batch DF-5 at 174fbb62a, plan 2.7 and 2.8, D7, D10, D11; spec 3.8, 4, 5, 8.6, 8.8; task (1) to (5))

| Row | Delivered | Where | Evidence |
| --- | --- | --- | --- |
| (1) the `defaults-zone` row of PK-1's kind table; no new profile, no existing route, answer, identity, certificate or theorem statement changed (D7) | yes | `lean/VE/Defaults/Route.lean` (`defaultsKinds` gains the kind; `defaultsRows` answers by `zoneCase`, then `defaultsCase`); `layeredKindCase_other` keeps its statement | `evidence/conservativity.json` (62/62 identical, main's `ve_service` at the merge base against this branch's); `lean/statements.txt`: 0 removed, 0 changed |
| (1) its encoder and response-shape row | yes | `ResponseShape/Schemas/NormDefaults.lean` (`defaults_zone`, `defaults_zone_line`, digest-pinned); `ResponseShape/Encoders/NormDefaults.lean` (`zoneLine_fits`, `zoneCase_fits`, used by `layeredKindCase_fits`) | `lake build`; `tests/test_route_row_schemas.py` over the corpus with the 12 new cases (32 passed) |
| (2) DE10 in three forms, chosen by `zoneForm` (`zoneFormOf`) | yes | Lean: `zoneFieldsOf` gives `form` (short/long) with `byDefault`/`leftTo`; Python: `defaults_english.zone` renders DE10, DE10′, DE10″ | DF-μ/ξ/π′ short, DF-δz long (`ZoneWireExamples.lean`; `test_each_zone_is_lean_s_and_reads_as_spec_4_says`) |
| (2) DE10f once per `forcedAll` entry no stated condition forces; never from `unknown` or no completion | yes | `zoneLines` (DE11 first, then DE10f from `forcedOfMin`'s list, else DE13); `zoneFieldsOf` reads `forcedAll` only for `byDefault`/`leftTo` | DF-μ (DE10f g1 at o1), DF-ξ′ (DE11, no DE10f), budget/no completion (no rows); `test_de10f_only_from_forced_all_and_never_from_unknown_or_no_completion` |
| (2) DE11, DE13 (exception, switch, ranking) | yes | `ZoneLine` rows; DE13 names the decision by its key (`decisionKeyJson`) | DF-ξ′, β2 (two DE11, conditions 1 and 0), DF-ε with the switch recorded, DF-δ with the ranking recorded |
| (3) `ve/defaults.py`: relay and bind only (typed schema; every id, tuple and label in the request; no Python copy of a Lean decision) | yes | `bind_zone`, `answer`, `soft_source` (adds each decision's sorts by key, from Lean's soft elaboration) | `test_mutants_never_pass_as_answers` (every one-fault mutant of 7 genuine rows), `test_each_binding_refuses_its_tampered_field_and_keeps_the_genuine_row` (12 refusals, each with the genuine row accepted) |
| (4) route cases: DF-μ, DF-μ′, DF-μ″, DF-δz, DF-ξ, DF-π′ end to end; DF-θ refused; conservativity (8.8) | yes | `tests/data/route-cases.jsonl` (+12, recorded by `tests.route_case_recorder`); `tests/test_defaults_zone.py`; `ZoneWireExamples.lean` | `evidence/delta.json`, `evidence/conservativity.json` (saved; no live git) |
| (5) seeded bugs: DE10f from an `unknown` zone; the "exceptions" form with a ranking open (DF-δ); Python accepting a tampered `forcedAll` entry; one mutant per new trusted definition | yes | `mutants.json` S1-S3; `trust-mutants.json` | "Seeded bugs" below |
| DRI 2026-11-04 item 2: `zoneMin` once; `zoneOfMin`, `forcedOfMin` with `defaultZoneOf_eq`, `forcedAllOf_eq` (rfl); a guard that the one-call answer equals `defaultZoneOf`/`forcedAllOf`; df-5a's Zone mutants rerun | yes | `Zone.lean`; `zoneFields` binds `x.min` once; `oneCall` guard on 8.6's fixtures | statements 0 removed / 0 changed; `evidence/df-5a-mutants-rerun.out` (25: all fail their guards), `evidence/df-5ab-mutants-rerun.out` (12, F4 re-targeted as F4′: all fail) |
| DRI 2026-11-04 item 1, conditions (i)-(iii) | yes | — | (i) `evidence/conservativity.json`; (ii) `ZoneWireExamples.lean`: `weighingText` is row 1's text and `viewRest` gives it on a `defaults-zone` request; (iii) the 8.6 guards through `runCaseReported` |
| Evaluator rule (each value once, size charged) | yes | `zoneMin` once; the record and the open atoms by df-5a's `zoneCharge`; observations against `maxZoneObservations` (1,024) before any is read | guards: 1,025 observations `unknown (observations size)`, 1,024 answered; DF-λ at 13 operators `budget: 26 open atoms, over 12` |
| Spec text (edit 6, the routes paragraph) | yes | `docs/spec/defeasible.md` (the two hunks, verbatim from 174fbb62a); `docs/spec/defeasible-PLAN.md` (verbatim from 174fbb62a) | `diff` against the pinned files: only df-5a's DRI-signed `valid` lines differ |
| `ve document readings --assume-no-exception` at a situation with observations | **no: df-5b** (not in the task's deliverables; size) | — | — |
| W7's all-derivations gate on the new rows | **no: df-5b** (deferred for every DE row to df-1bbc already) | — | — |

## Recorded choices (no statement changes)

1. **The request.** `model` is the situation (`situationX`), with every decision table empty: a fixed decision goes in
   `record`, named by its key (`{"excepted": r}`, `{"off": r, "party": π}`, `{"outweighs": a, "lower": L, "higher":
   H}`); `observations` and `query` name a regulated outcome and a tuple. A non-empty decision table is refused
   (`InvalidInput: the situation's decision tables are empty; a fixed decision goes in the record`): the zone leaves
   those atoms open, so a table there would be silently ignored.
2. **DE10″'s `<two completions>`.** Rendered as the two completions' rows in their own words without the sentence
   frame, joined by "and" within a completion and ", or" between them: "…, the answer depends on which rule gives way:
   the exception to rule r2 applies to a, or the exception to rule r1 applies to a." The row's fixed words are spec
   4's verbatim; only the slot's joining is this item's.
3. **`<tuple>`** is the entity ids, joined by ", ". **`<result>`** is Lean's `words` clause of the query's outcome
   with the zone's value. For DF-λ's plain `instructs` (no `act`) that clause is "o2 is instructs": the existing
   renderer's text, not this item's.
4. **DF-θ.** On main the layered decoder refuses `weighing@0` (`UnsupportedProfile: Unsupported profile weighing@0`)
   before diagnostic 1, for every `defaults-*` kind (DF-1a). Row 1's text is reached by `viewRest` on a decoded
   document; both are guarded.
5. **`noCompletion`'s labels** are bound to X's labels (the layered `norm-defaults-elaborate` row) or `ZONE_CHECKS`,
   the names of `zoneMin`'s and `zoneRow`'s own checks (record, background, fill, observed, typing).

## Seeded bugs (each planted alone, the named test fails, then restored)

| Id | Language, file | Bug | Fails |
| --- | --- | --- | --- |
| S1 | Lean, `lean/VE/Defaults/ZoneWire.lean` | DE10f from an `unknown` zone (forcedAll read as `[]` from an incomplete enumeration, the zone shown with rows) | `ZoneWireExamples.lean:110` (observations-size guard) |
| S2 | Lean, `lean/VE/Defaults/ZoneWire.lean` | the "exceptions" form with DF-δ's ranking open | `ZoneWireExamples.lean:66` (DF-δz guard) |
| S3 | Python, `ve/defaults.py` | a tampered `forced_all` entry accepted | `tests/test_defaults_zone.py::test_each_binding_refuses_its_tampered_field (its first tamper: an absent rule in forced_all)` |
| R16 | Lean, every new trusted definition | `tools/trust_mutants.py` | `trust-mutants-final.json`: 389 killed, 0 survivor, 0 unknown (see "Trust") |

## Trust

`uv run python tools/trust_map.py --check`: K +0, S +0, V +113 (`ZoneWire.lean` +75, the two shapes +36, `Route.lean`
+2); PASS with the R16 allowance. Classes in `tools/trust-classes.json`. FOLLOW-UPS.md "## df-5" asks for the ties pass.
`tools/trust_mutants.py` (`mac-pytest.sh --trustmut`, cloud pool, `--test lean/VE/Defaults/ZoneWireExamples.lean --test
lean/ResponseShape/DefaultsExamples.lean`), 14 new or changed trusted definitions, 426 mutants:

- First run, `trust-mutants.json` (head 54a4a2067): 389 killed, 8 invalid, 4 survivors, 25 unknown.
- With `trust-mutants-allow.json` (13 entries, each with its reason), `trust-mutants-final.json` (head 66190bd0c, Lean
  unchanged since 54a4a2067): **389 killed, 8 invalid, 29 allowed, 0 survivor, 0 unknown, 0 not run**.
- Every definition has killed mutants except the inductive `ZoneLine`. Its three `ctor-drop` mutants do not
  elaborate, because `zoneLines` and `ZoneLine.json` name the dropped constructor (as df-5a's T8 for `DefaultZone`).
  Each constructor is exercised by guards: `stated` by DF-ξ′ and β2, `forced` by DF-μ and two tuples, `assumed` by
  DF-μ′, DF-ε and DF-δ.
- The allowed mutants are type errors in the mutated text (24 unknown), two equivalent ones (`value` has at most one
  element), two drops of `row`'s alternatives that no zone answer reaches (checked in Python by
  `tests/test_route_row_schemas.py`), and `defaultsRows` emptied. That last one fails RouteExamples' guards, but they
  also reach the fits proof the mutant breaks.
- Earlier runs on the way, kept out of the evidence: a run with the encoder file as `--test` (its proofs then count,
  which makes every row-shape mutant UNKNOWN) and a run before the two-tuple, two-rule and record fixtures. That run's
  survivors led to those fixtures and to `zoneLines` reading the record only.

## Tests run

- `tests/test_defaults_zone.py` (45 tests), and `tests/test_defaults_checks.py`: passed locally and on the Mac (the
  seven `tests/test_defaults_*.py` files: 204 passed, mac-pytest 14:28Z, HEAD 44fc281f).
- The selected tests (`mac-pytest.sh --select`, HEAD ace4f960): 270 units recorded, 2 failed:
  `tests/test_defaults_answer.py::test_soft_source_is_the_exception_tables` (my `soft_source` gained a member; fixed
  by `zone_source`, `soft_source` unchanged) and `tests/test_defaults_checks.py::test_review_f1_every_check_is_needed_by_a_both_sides_test`
  (the new `bind_zone` checks had no both-sides test; fixed). Both reran passing (above). The first selected run
  stopped at `tools/check_lean_imports.py` (ZoneWireExamples' layer; fixed in `tools/layer_policy.py`).
- `tests/test_route_row_schemas.py`: 32 passed (with the 12 new route cases). `tests/test_assurance_manifest.py`: 139
  passed. `tools/relay_mutation_gate.py`: 46 routes, 148,161 mutants, 0 failures (17 min).
- `cd lean && lake build`: completed; `python3 lean/audit.py`: PASS; `tools/lean_statements.py`: 0 removed, 0 changed;
  `tools/regen_generated.py --check`: 35 entries up to date; `tools/gate_collection.py --check --prebuilt`: 45 added, 0
  removed, 0 refused, 0 stale, 0 malformed; `tools/check_lean_imports.py`, `tools/test_layer_policy.py`: OK.
- Not run here: the full gate (the chain runs it on the final HEAD).

## Overlap

Hand-written files against every in-flight branch (`git diff --name-only <merge-base> <branch>`): feature/et-4b and
feature/ap-3db also edit `lean/ResponseShape/Schemas/NormDefaults.lean` and `lean/ResponseShape/Encoders/NormDefaults.lean`
(other hunks: `base_environment`, `layered_elaborate`); et-4b also edits `lean/VE/Defaults/Wire.lean`, which this
item does not touch (the wire is a new file). Several branches add imports to `lean/VE.lean`.

## Size

About 1,000 hand-written lines (`git diff --numstat` against the merge base, without generated files, the verbatim
plan and spec, and the saved evidence outputs), plus this report: the wire 154 and its guards 149, `Zone.lean` +50/-18
(the DRI-signed refactor), shapes, encoder and schema checks 89, Python 126, tests 268, route cases 12, trust classes,
layer and assurance-manifest entries 96, the DELTA and the evidence script 46. Against the 600-line rule. The DRI was
asked twice (inbox 20261104T083239Z-df-5-2047189 with the proposed cut, 20261104T152148Z-df-5-838769 with these
numbers); **no ruling yet**. Nothing of the task's deliverables (1)-(5) is cut; the CLI path and W7's gate are df-5b.

## Pilot bytes

0 (plan: none in bytes). The kind is reachable through the service; no pilot document asks a zone question yet.

## Next items

- df-5b: `ve document readings --assume-no-exception` at a situation with observations and a record (the CLI path to
  `ve.defaults.answer`), and W7's all-derivations gate on DE10-DE13.
- df-6, DF-E4 (the plan's next).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: PASS. `defaults_zone` types every field (`lake build`: the digest pins and
   `zoneCase_fits`); `tests/test_defaults_zone.py::test_mutants_never_pass_as_answers` (drop, retype to 7, 1.5, true,
   null, [], {}, "\ud800", a 10,000-deep list, swaps, duplicates, on 7 genuine rows);
   `::test_each_request_member_retyped_or_dropped_is_refused_by_lean` (12 request paths × 7 values);
   `tools/relay_mutation_gate.py`: 46 routes, 148,161 mutants, 0 failures.
2. Every deliverable built: PASS (the plan rows table; CLI and W7 named as df-5b, not in the task's list). Grep of the
   diff: no Python copy of a Lean decision (`bind_zone` checks shape and binding only; `ZONE_CHECKS` names Lean's
   labels for binding), no permanent report test, no def of the six weighing names under `lean/VE/Defaults/`.
3. Tests can fail: PASS. S1-S3 (`mutants.json`), the R16 mutants (`trust-mutants.json`), df-5a's and df-5ab's Zone
   mutants rerun on the refactor (`evidence/*-mutants-rerun.out`: all fail their guards).
4. Python and Lean agree, valid inputs still pass: PASS. `evidence/conservativity.json` (62 of 62 identical);
   `tests/test_route_row_schemas.py` (32 passed: both decoders agree on every mutation of the 12 new cases).
5. R8 binding: PASS. `::test_each_binding_refuses_its_tampered_field` (23 tampers: an absent or strict rule, a
   tuple outside the situation, of the wrong length or type, a condition out of range, a party the rule lacks, a
   forced exception shown as an assumption, a duplicated or reordered row, an extra, repeated or emptied completion,
   an absent, repeated or empty label, an empty reason) and `::test_every_genuine_row_binds` (17 genuine rows);
   `tests/test_defaults_checks.py` reads them as both-sides tests, so each check of `bind_zone` weakened or deleted
   fails one of them (`test_review_f1_every_check_is_needed_by_a_both_sides_test`: passed); inputs:
   `ZoneWireExamples.lean` refusals (an absent decision, a malformed key, an outcome the document does not regulate,
   an entity outside the situation, a non-empty decision table).
6. Gate evidence: N.A. here (the chain runs the gate on the final HEAD); the saved evidence reads no live git.
7. No unsigned item: PASS. D1 SIGNED by the DRI (reviews/dri-decisions-20261104-df-5.md item 1), T1 R16.
8. Every user-visible change in DELTA: PASS. `evidence/delta.json` (the 12 cases, main against this branch),
   `evidence/conservativity.json`.
9. Test selection: PASS. `tools/select_tests.py --base <merge base>` selects `tests/test_defaults_zone.py` (441 test
   files, not every unit).
10. Lean statements: PASS. `lean/statements.txt` 0 removed, 0 changed; `defaultZoneOf_eq`, `forcedAllOf_eq` added;
    `python3 lean/audit.py`: PASS. A `BOGUS` row label in `ZoneLine.json` breaks `zoneLine_fits`
    (`Encoders/NormDefaults.lean:145`, restored).
11. Budgets and limits: PASS. `budget: 26 open atoms, over 12` (13 operators), observations 1,025 `unknown`, 1,024
    answered (`ZoneWireExamples.lean`); df-5a's record and typed-atom bounds unchanged.
12. CPU: PASS. `zoneMin` is evaluated once per request (`zoneFields`' one `let m := x.min`, DRI 2026-11-04 item 2;
    the `oneCall` guard: the answer equals `defaultZoneOf`/`forcedAllOf`'s). No step counter exists for this path.
13. Test-removed trailers: N.A. (no test removed). `tools/gate_collection.py --check --prebuilt`: 45 added, 0
    removed, 0 refused, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS. Each guard and binding test has its accepting side; each
    claim here names its command; spec 3.8, 4 (DE10-DE13 words verbatim), 5 row 1 and 8.6 re-read against the
    fixtures (every computed zone matches 8.6).
