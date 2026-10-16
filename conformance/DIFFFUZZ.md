# Cross-language differential fuzzer

`tools/difffuzz.py` runs Python, the Lean routes and Rust on every fixture of the conformance corpus and the use
cases, and on seeded mutants of them. It compares their answers and fails on any disagreement that is not in the
reviewed baseline [`difffuzz-baseline.json`](difffuzz-baseline.json). It also fails on any baseline entry that no
longer reproduces, so a fix has to shrink the baseline. It addresses classes 1, 2, 4, 8 and 15 of
`manage-agents/FINDING-CLASSES.md`: Python/Lean/Rust disagreement, vacuous comparison, Unicode and whitespace,
untrusted responses, and malformed input.

```
python3 tools/difffuzz.py --ci                     # the suite's run (tests/test_difffuzz.py)
python3 tools/difffuzz.py --deep 20                # nightly: 20 times the CI sample, seeded by the date
python3 tools/difffuzz.py --ci --update-baseline   # drop fixed entries, add new ones as TODO, then review
python3 tools/difffuzz.py --ci --report out.json   # the full report: corpus, mutants, findings, CPU
```

The run needs the Lean executables (`lake build`) and the Rust release binary (`tools/rust_build.py`, or
`VE_RUST_PREBUILT=1` with `VE_RUST_BINARY`). `--minimise-limit N` minimises up to N new signatures (default 40).

The batch 12 integration merge replayed both parents' baselines and the CI sample.
The merged baseline has 254 reproducing entries: 147 old entries were fixed,
26 changed entries collapsed onto an existing signature, 7 changed entries
retained their reviewed follow ups, and 19 minimized sample findings were
reviewed under `DF-6` (7 language/envelope version cases) or `DF-9` (12 nested
decoder code cases). The remaining findings are tracked below.

## Corpus

`tools/difffuzz_corpus.py` reads every JSON file under `conformance/` and `usecases/`. Each file is read by a
surface or listed in `EXCLUDED` with its reason: `artifact` files are outputs (reports, baselines, recorded
results), `no-input` files hold no environment and no request. `test_every_fixture_is_read_or_excluded_with_a_reason`
checks that every file is one or the other, that no `no-input` file holds an environment or a request, and that
every exclusion pattern still matches a file.

- **Environments**: every environment, wherever it sits: an environment file, the `environment` of a case or a
  use-case request, a bundle's environment. The generated corpora (`conformance/risk.py`,
  `conformance/alternatives.py`) and the speech-acts and reports route tests' environments are added
  (`GENERATED`), so that every Lean route has seeds.
- **Requests**: every route request of every fixture, found by its fields (`REQUEST_FIELDS`): the P0 families,
  the v0 families (`evaluation`, `identity`, `parser`, `validation`, `closure`, `countermodels`, `search`) and the
  use cases' requests (`closure-induction/*/query.json`). Each model of a use case is also run against each
  environment of its directory that decodes it, with the formulas of the directory's `.ve` documents that parse
  there (`usecase_requests`).
- **Wire-contract units**: the contracts and test inputs under `conformance/wire-contract/`, through the
  wire-contract tests' corpora, and the recorded test inputs of each production unit `ve_diagnose` serves
  (`WIRE_UNITS`: `soft-norms@0`, `norms@0`, `norm-defaults@0`).

## Surfaces

Each seed belongs to a surface. The surface says which implementations take part and how their answers compare.
Every seed is run as it is, besides its mutants: an implementation with a path for a seed takes part on it whether
or not it accepts it, so a rejection of a seed is compared like any other answer.

| Surface | Python | Lean | Rust | Compared |
|---|---|---|---|---|
| `requests` | `conformance.three_way.python_verdict` | by the environment's language (`LEAN_REQUESTS`): `ve_conformance route` for ve.core@0.2; `ve_conformance` and its `check-certificate` mode for ve.core@0 and ve.core@0.1; no `search` (`NO_LEAN` gives each reason) | `ve conformance` where `rust_request` maps the case | outcome; each implementation's own diagnostic code (`diagnostic_code`: Python's `VEError.code`, Rust's code, Lean's text as `checker_error` classifies it); the text of a P0 `KNOWN` code on the P0 route (an `InvalidModel`'s generator instead); the verdict values. Rust's `certificate` verdict is a bounded search, so its value is not compared and a certificate the Lean route rejects does not contradict it. Rust's `evaluate` verdict is the document's value (its `evaluate-budgeted` kind), compared with the conjunction of the others' statement values. Since lean-first batch 15b Rust has no label or dependency-order route and reads no source text: those requests are Python and Lean only |
| `environment` | `Environment` | the route that decodes the envelope (`lean_route`, `ROUTES`): the service's `environment` mode, or the alternatives, risk, soft-norms, speech-acts, reports, norm-defaults or quantity route with a case that only decodes it | a `check` case (`true` typed over the environment) for the core envelope and soft norms; none for W6 and the other blocks (`ROUTES` gives each reason) | outcome; code; the text when Python or Lean gives a decoder type diagnostic (`TYPE_DIAGNOSTICS`, the env-profiles directive, Python against Lean only); the environment identity on the envelope and quantity routes. A route that names its own code (`OwnCodes`: the soft-norms route's `code`, a code of `soft-norms@0`) keeps it: it is compared with the code of the route's Python counterpart (`load_soft_document` with no norms), and its class in the contract's `codes` table is the code compared with `Environment` and Rust |
| `wire` | the engine, on the root the unit's adapter builds (a case outside the unit's domain is the adapter's refusal, as in `ve_diagnose`) | `ve_diagnose` | none | the whole record, except the text and args of an `inherited` check (an included contract's by its include path, `w1-environment/1.1`) |
| `document` | `load_document`, then `check_document`'s wrapper (`_report` when the document has a claim graph, `coverage` otherwise), on the document text (`conformance/document_wrapper.py`) | the service's `document` mode on the same text | none | outcome, code and text; the value (identities, every unit's span, status and parent, the coverage owned by the wrapper). Python's added norm-defaults and content-bearing readings residuals are removed from the comparison. Lean's or Python's `CheckerUnavailable` or `ResourceLimit` agrees with any answer (the mode fails closed where it cannot decide yet), and so does a rejection whose Python text is another decoder's (`owner_of`: the environment, formula, admission, or readings decoder, DF-3 and DF-9). The readings exception applies when both sides reject and Python's rejection comes from `validate_reading_sets` on the original document path. The seeds are every `ve-document@1` text of the repository and generated documents; `tests/test_lean_document_wrapper.py` requires the seeds the mode owns to agree, so a mode that always refuses fails there |

An input off the restricted wire (`null`, a float) is never sent: every Lean and Rust package reader refuses it as
a whole (`test_every_runner_refuses_an_off_wire_package` checks each runner), and so does every Lean and Rust
backend's client before sending. Their answer is that refusal (`framing`), which agrees with any rejection and
disagrees with an acceptance. A runner that refuses one restricted-JSON input as a package gives the same answer.

## Runner rows

Every row a Lean or Rust runner prints is checked before it is read, against the schema its producer declares
(the `*_row_problem` checks of `tools/difffuzz.py`). A row that fails is a runner that did not answer
(`no-answer`), never an answer.

| Runner | Check |
|---|---|
| `ve_conformance route` | the service's `route` schema (`ve.backends.service_schema.check_row`), which `tests/test_lean_service_schema.py` checks against Lean's own decoders (`ve_response_decode`) |
| `ve_conformance` (v0) and `check-certificate` | the assurance manifest's runner bindings (`ve/assurance-manifest.json`), read by `ve.backends.lean.row_problem`: response types and counted fields; an error row carries nothing but the error (and `valid: false` in the certificate mode) |
| the service's `environment` mode | the service client's schema check, and the identity field |
| block routes and `ve_quantity` | the one-shot runner contract (`row_problem`), each route encoder's ok fields (`LEAN_ROUTE_FIELDS`) and no other field; on an error row of a route with its own code, that code, one of its contract's codes (`route_row_check`); `test_route_tables_are_the_genuine_rows_fields` checks the fields against genuine rows, field for field |
| `ve_diagnose` | `clean`, or `fault` with one record of the wire contract's record fields (`RECORD_FIELDS`, the Python engine's `Fault` record) |
| `ve conformance` (Rust) | the statuses and fields of the operation Rust reads the case as (`RUST_ROWS`, `rust_operation`); an error row's `{code, message}` and no other field |

Each batch must also print one row per case, bound to its case by id (or, for a case the runner could not read,
by position) with JSON types kept apart, and exit 1 exactly when some row is an error. The row of a case the
runner could not read is `POSITION_ROW` (`status`, `case_index`, `error`, and `valid: false` in the v0 runner's
certificate and order modes, as the service schemas' `case_error`) and nothing else: the runner never ran the
case's route, so a route's own code, an answer field or an `id` on it is a malformed row. Runner output is read by
the runners' one reader (`ve.backends.lean_service._decode_json`, which the production readers share), which
rejects duplicate fields, non-finite constants and strings that are not Unicode text (a `\ud800` escape). A
batch that does not answer (a crash or signal, no answer within `HANG_TIMEOUT`, a runner that cannot start,
output that is not UTF-8 or Unicode text, or nests too deep to decode) is split until the case is alone, and that
case did not answer. Every answer of every engine enters the comparison through one gate (`held`): one that cannot
be signed and stored as JSON text is Python's crash, or a Lean or Rust runner that did not answer. That, and a
runner's refusal of a case's package, are values of their own types (`NoAnswer`, `Refused`), never rows: a
printed `{"id": "0", "framing": "oops"}` is a malformed row, not a refusal, and a runner's own error code
`framing` is a code (`refusal` alone makes a refusal).
`test_genuine_rows_pass_their_checks_and_mutated_rows_are_not_answers` checks that every genuine row passes, that
a row reduced to its id (alone, or with a `framing` or `panic` member) is no answer on every runner, that each
field a check reads, dropped or retyped, is no answer, and that a field the producer does not print is no answer
where the producer's schema is closed.

## Mutants

`one_faults` lists every 1-fault mutation of a seed:

- every node replaced by `7`, `true`, `null`, `[]`, `{}` and `"x"`;
- an object member removed (null against absent);
- an object's keys and a list reversed;
- a list's first entry duplicated;
- every string value and object key with NBSP, a double space, a tab, a trailing `\r`, U+212A for k,
  U+0130 for i, upper case, Arabic-Indic digits, a curly quote and a control character (U+001C);
- every array or string that a wire-contract table limits (`max_items` and `max_bytes` checks of
  `soft-norms@0`, with `ve/wire_contract/limits.json`, and of the corpus units) resized to limit − 1, limit and
  limit + 1.

The sample draws them without listing them all (`Faults`: a node at random, then one of its mutations). A 2-fault
mutant combines two of them at unrelated paths. The CI sample takes `CI_BUDGET` mutants per surface (6,000
1-fault and 1,500 2-fault mutants), round-robin over the profiles and, within each, over its seeds, from a fixed
seed; `--deep N` takes N times as many from the date's seed.

## Findings

- **`python-crash`**: Python raised something other than `VEError`. An exception raised by the fuzzer's own
  adapter, for a field the adapter reads, means the call cannot be made and is not counted.
- **`timeout`**: a Python call spent its CPU budget (`PYTHON_CPU`).
- **`no-answer`**: a Lean or Rust process did not answer, by panic, signal, CPU limit, hang, failure to start,
  malformed output or a row that fails its check. The batch is split until the input is alone.
- **`outcome`**, **`code`**, **`diagnostic`** or **`value`**: two implementations that take part disagree.

A finding's signature is the surface, the profile (request family and kind, Lean route or wire unit), the classes,
and each answer's outcome, code and contract-fixed text. In the text, values repeated from the input become `<v>`
and digits become `#`. A finding whose signature is not in the baseline is new. It is minimised by greedy deletion,
biggest cut first, keeping the signature, before it is reported. A baseline entry gives its minimised input, the
seed and mutation it came from, the participating engines, the seed's runners (`meta`), the answers, the signature
and a follow-up id from the table below. The suite fails on a new signature, on an entry that no longer reproduces
(`fixed` or `changed`), and on an entry with no follow-up id. After a fix, run `--update-baseline`, which drops
entries that no longer reproduce, and review the diff.

## Follow-ups

Each baseline entry names one of these ids. `tests/test_difffuzz.py` checks that every id used is listed here and
every id listed is used. The grouping was made by rules over the answers (code, text and the mutated field); an
entry may sit under a neighbouring id.

| Id | Disagreement | Where it is fixed |
|---|---|---|
| DF-3 | Nested vocabulary fields of the wrong JSON type: Python's text is not Lean's decoder type diagnostic (`String expected`, `array expected`, `object expected`), on the envelope and on every route that decodes an environment. The env-profiles directive fixed top-level fields only. | `wire-contract-PLAN.md` 7, S4 base row (`vocabulary@0.2`); env-profiles3-looprecheck1 notes the nested combinations |
| DF-4 | A non-string profile: Rust's text is `expected a string`. The P0 contract fixes `profiles must be a sorted unique array`, which Python and Lean give. A `profile` or `profiles` of the wrong JSON type (or a non-string member): Python and Lean say `InvalidInput: String expected` or `array expected`, Rust says `UnsupportedProfile` (on the quantity route, `quantity route requires ve-units@1`). | `wire-contract-PLAN.md` 7, S4 base row (`envelope@0.2`, Rust engine) |
| DF-5 | A non-string or unknown `spec_revision`: Python and Lean say `InvalidInput: String expected` (since `fix/env-field-types`), Rust says `UnsupportedProfile: Unsupported specification revision …`. | `wire-contract-PLAN.md` 7, S4 base row for Rust |
| DF-6 | Language and envelope versions. For an unknown `language` string, Python and Rust read the frozen v0 envelope (`Incorrect fields (missing profile)`) and Lean says `Unsupported language`; Lean's direct v0 and closure runners say `InvalidInput: unsupported environment version` or `unsupported closure environment version/profiles` where Python and Rust say `UnsupportedProfile`. The shared Lean service decoder classifies these as `UnsupportedProfile`; the direct runner keeps its frozen error text. When fields are missing, Python reports the field set where Lean reports the profiles or the language. | `wire-contract-PLAN.md` 7, S4 base row (`envelope@0.2`) |
| DF-7 | Models: Lean's route and v0 runner report a model's shape errors as `InvalidInput` (`fields do not match`, `invalid integer`, `String expected`) and read the formulas before the model, as Rust does; Python reports `InvalidModel` first. | `wire-contract-PLAN.md` 7, S4 base row (`model@0.2`) |
| DF-8 | Dependency orders and cycles: Rust's code is `DependencyCycle` where Python and Lean's text classify as `InvalidInput`; Lean's dependency-order route does not decode the vocabulary (it accepts a misspelt field). | new: the P0 dependency-order route (PLAN-EXPAND2 3.4) |
| DF-9 | Nested decoder codes and order. Python and Rust report `UnknownSymbol`, `SyntaxError`, `UnboundVariable`, `TypeMismatch`, `DuplicateDeclaration` or `ResourceLimit` where Lean's route and v0 runner report `InvalidInput` (sort references, AST bodies, variable indices, reserved names, identifier lengths); some checks run in another order. | `wire-contract-PLAN.md` 7, S4 base row (`vocabulary@0.2`, `formula@0.2`) |
| DF-10 | A non-string label: Python says `AdmissionError: invalid label []`; Lean says `InvalidInput` (Rust has no label route since lean-first batch 15b). | new: the P0 label route |
| DF-11 | Admission of a document whose certificate trace is malformed: Python reports the admission label error first, Lean the certificate's field set. | `wire-contract-PLAN.md` 7, S9 row (`ve-document@1`) |
| DF-13 | Block routes (alternatives, risk, soft norms, speech acts, reports, norm defaults): Lean reports a block-level diagnostic (`risk.block`, `alternatives.block`, `invalid vocabulary`, a block's field set) where Python reports the field or the missing profile, or accepts. | `wire-contract-PLAN.md` 7, S7 row (`alternatives@0`, `risk@0`); S3 for `soft-norms@0`'s environment; S6 and S8 for speech acts and reports |
| DF-14 | The Python wire-contract engine accepts a JSON `null` (a contract field or the soft-norms decider) that every Lean and Rust package reader refuses. | `wire-contract-PLAN.md` 7 (restricted JSON at the contract boundary); spec 2.8 for the soft-norms decider |
| DF-15 | A request without its `model` (or with a misspelt key): Lean's route says `property not found`; Rust reads a countermodel check as a search and accepts, or rejects an evaluation for its document before it misses the model (since lean-first batch 15b no case shape is read as a parse). Python's adapter cannot make the call. | new: the Rust conformance dispatch (one case shape per kind) |
| DF-16 | Python's search and countermodel check accept an object where `premises` must be an array; Lean says `array expected` and Rust `premises must be an array`. | new: the Python premises decoder |

DF-12 closed in lean-first batch 5: the risk route now rejects the NBSP act phrase with the W6 canonical-round-trip diagnostic. Its baseline signature no longer reproduces.
| DF-18 | Python's `Environment` rejects the `soft` vocabulary block of the soft-norms sources of `conformance/soft_norms_rust.json` (`unknown=['soft']`), which Rust accepts and Lean's soft-norms route accepts or rejects by a soft check of its own (Python's soft counterpart gives the same code). | `wire-contract-PLAN.md` 7, S3 row (`soft-norms@0` environment) |
| DF-19 | A constant with a `verbalisation` member is accepted by Python and the merged Lean environment and norms decoders. Rust's older envelope decoder requires exactly `sort` and `description`; the norm-defaults wire route can report a different first fault. | Rust's constant declaration decoder and the norm-defaults wire phase order |
| DF-20 | Malformed nested vocabulary fields, norm blocks, and oversized norm lists can produce different rejection codes or diagnostic order across Python, Lean, and Rust. Without `norm-defaults@0`, Python and Lean report the missing profile for an `unspecified` regulated default before an unrelated malformed predicate argument sort; Rust reports the sort first. Without `definitions@0`, Python and Lean decode a `defined` body (its `SyntaxError`) before the missing profile; Rust's envelope decoder rejects the `defined` field by its field set first (exposed in lf-14c, when Lean's definition bodies took Python's decoder texts). Each baseline entry pins its exact input and answers. | Align nested validation, resource-limit diagnostics, and Rust's norm-defaults profile-gate order |

Fixed and retired (no entry reproduces since the merge of `ve-integration` with `fix/env-field-types`): DF-1, Python's
`TypeError` for a numeric or Boolean `profiles`; DF-2, Python's `TypeError` for an array or object where a
definition body or AST node has a name or tag. DF-17, the norm-defaults route's refusal of `data@0` flags (`norms route with data
flags is not implemented`) on an environment Python's `Environment` accepts: since English E2.6 Lean admits the flags
and refuses a supplied model that violates one (`InvalidModel(flags)`); its one `environment` entry is retired.

## Acceptance items

| Item | Tag | State |
|---|---|---|
| `--ci` is in the suite, at most 5 minutes of CPU (`test_ci_run`) | AGENT | done |
| Weakened comparisons and a changed Python diagnostic make the run fail (`test_a_weakened_comparison_fails_the_ci_verdict`, `test_a_changed_python_diagnostic_is_caught`, `test_a_python_code_outside_the_p0_contract_is_compared`) | AGENT | done |
| Off-wire inputs and Python timeouts are compared, not dropped (`test_python_accepting_an_off_wire_input_is_a_finding`, `test_a_python_timeout_is_a_finding`) | AGENT | done |
| Every fixture is read or excluded with a reason; every engine with a path answers every seed (`test_every_fixture_is_read_or_excluded_with_a_reason`, `test_every_engine_with_a_path_answers_every_environment_seed`) | AGENT | done |
| Every runner row is checked against its producer's schema; dropped and retyped fields are no answer (`test_genuine_rows_pass_their_checks_and_mutated_rows_are_not_answers`) | AGENT | done |
| A route's own code is kept, compared with its Python counterpart and checked against its contract's codes (`test_a_routes_own_code_is_kept_compared_and_checked`, `test_the_compared_code_of_an_own_code_is_its_contract_class`, `test_every_own_code_route_has_a_python_counterpart_that_agrees_on_its_seeds`; the production reader `run_soft_case` refuses a code or message that is not text: `test_the_soft_route_reader_checks_the_code_it_keeps`) | AGENT | done |
| Runner transport is not a row: printed `framing`/`panic` members and every transport failure are no answer, isolated by bisection (`test_a_printed_framing_member_is_a_malformed_row_not_a_refusal`, `test_a_runner_that_fails_in_transport_is_isolated_and_does_not_answer`, `test_a_runner_whose_output_is_not_utf8_does_not_answer`, `test_a_runner_code_named_framing_is_a_code_not_a_refusal`) | AGENT | done |
| Rows of unread cases carry the position row alone, on every Lean runner; no route code is taken from one, in the fuzzer or in production (`test_a_row_for_a_case_the_route_could_not_read_names_no_route_code`, `test_every_runner_rows_for_unread_cases_carry_the_position_row_alone`, `test_the_position_row_is_the_service_schemas_case_error`, `test_the_production_soft_reader_takes_no_code_from_an_unread_case`) | AGENT | done |
| Runner output that is not Unicode text is no answer, and no answer the fuzzer keeps can crash it (`test_runner_output_that_is_not_unicode_text_does_not_answer`, `test_every_answer_the_fuzzer_keeps_is_json_text`, `test_the_runner_reader_rejects_text_that_is_not_unicode`) | AGENT | done |
| Baseline seeded with today's disagreements, each with a follow-up id | AGENT | done |
| Review of the baseline's grouping into DF-3 to DF-19 | HUMAN | deferred to the branch review (owner: reviewer) |
| The nightly script calls `--deep 20` | EXTERNAL | deferred: the nightly script is outside the repository (owner: orchestrator); the instruction is in `docs/ARCHITECTURE-LAYERS.md` |
| Merge `fix/env-field-types`, then run `--update-baseline` to drop DF-1 and the Python-against-Lean part of DF-5 | AGENT | done: merged with `ve-integration`; DF-1 and DF-2 retired, the new signatures filed under DF-3 to DF-6, DF-9, DF-13 and DF-19 (two `--update-baseline` passes: a changed entry is dropped on the first and found again on the second) |
| Refresh after batch 12 decoder location repairs | AGENT | done: removed repaired signatures in two `--update-baseline` passes; retained four sampled constant-sort discrepancies under DF-9 (requests), DF-6 (core envelope), and DF-13 (soft-norms route). These are Rust/Python or v0 route code differences; the reviewed environment Python/Lean diagnostics agree. |
| Refresh after lf-14c's definition-body diagnostics (review F2) | AGENT | done: two `--update-baseline` passes dropped the 11 signatures where Lean's decoder texts for a definition body (`invalid indexed formula`, `array expected`, `Natural number expected`) differed from Python's `_Decoder` (DF-9, DF-15); the two new signatures, Rust's `defined` field-set rejection before the body's `SyntaxError` without `definitions@0`, are filed under DF-20. |

## Not covered

- Duplicate object keys. The Python entry points take parsed objects, so the in-process comparison cannot
  carry them.
- The `max_count` limit form, and the core limits of `ve/limits.py`, which are not in a wire-contract table.
- 10,000-deep nesting.
- The legacy soft-norms route's norms (`load_soft_document` against `ve_soft_norms_route`), which
  `wire_contract_gate.py` compares; the environment surface compares its environment decode, with no norms.
- The discourse, rights and readings routes: no fixture environment takes them, and the route table has no entry
  for them.
- Requests that a use case's own script builds (its `.ve` documents as admission graphs, certificates whose
  premises the script derives, the eligibility and safety-framework cases): the excluded files above name each.
- English in Lean (`conformance/english-lean/`): its engine, lexer and lexicon vectors are excluded. No route reads
  English through Lean yet (`english.admission` is Python's; `docs/spec/english-lean-integration.md`), so there is
  no surface to compare them on. The English-in-Lean tests check them Python against Lean. A surface belongs here
  once its Lean service route exists (English-in-Lean S2).
