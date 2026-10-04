# Cross-language differential fuzzer

`tools/difffuzz.py` runs Python, the Lean routes and Rust on seeded mutants of every fixture of the
conformance corpus and the use cases. It compares their answers and fails on any disagreement that is not in the
reviewed baseline [`difffuzz-baseline.json`](difffuzz-baseline.json). It also fails on any baseline entry that no
longer reproduces, so a fix has to shrink the baseline. It addresses classes 1, 4, 8 and 15 of
`manage-agents/FINDING-CLASSES.md`: Python/Lean/Rust disagreement, Unicode and whitespace, untrusted shapes, and
malformed input.

```
python3 tools/difffuzz.py --ci                     # the suite's run (tests/test_difffuzz.py)
python3 tools/difffuzz.py --deep 20                # nightly: 20 times the CI sample, seeded by the date
python3 tools/difffuzz.py --ci --update-baseline   # drop fixed entries, add new ones as TODO, then review
python3 tools/difffuzz.py --ci --report out.json   # the full report: corpus, mutants, findings, CPU
```

The run needs the Lean executables (`lake build`) and the Rust release binary (`tools/rust_build.py`, or
`VE_RUST_PREBUILT=1` with `VE_RUST_BINARY`).

## Surfaces

Each seed belongs to a surface. The surface says which implementations take part and how their answers compare.

| Surface | Seeds | Python | Lean | Rust | Compared |
|---|---|---|---|---|---|
| `p0` | every active case of the P0 families except `vacuity`, whose Python adapter asserts its own witness | `conformance.three_way.python_verdict` | `ve_conformance route` (not `search`, which Lean checks only as a countermodel) | `ve conformance` where `rust_request` maps the case | outcome; code as the P0 contract reduces it (`three_way.KNOWN`, otherwise `rejected`); the text of a `KNOWN` code (an `InvalidModel`'s generator instead); the verdict values. Rust's `certificate` verdict is a bounded search, so its value is not compared |
| `environment` | every distinct environment of the P0 families, `usecases/**/environment*.json`, the soft-norms test inputs and `conformance.risk.agent_ops` that Python accepts | `Environment` | the route that decodes the envelope (`lean_route`): the service's `environment` mode, or the alternatives, risk, soft-norms, speech-acts, reports or quantity route with a case that only decodes it | a `label` case | outcome; code; the text when Python or Lean gives a decoder type diagnostic (`TYPE_DIAGNOSTICS`, the env-profiles directive, Python against Lean only); the environment identity |
| `wire` | the wire-contract corpora (`demo@0`, `defer@0`, `forms@0`) and the `soft-norms@0` fixtures and test inputs | the engine | `ve_diagnose` | none | the whole record, except the text and args of an `inherited` check |

An implementation takes part on a seed when it has a path for it. For `environment`, Lean and Rust take part when
they accept the unmutated seed; for example, the quantity route's case does not decode a W6 envelope on its own,
and Rust has no alternatives or risk block. For `p0`, an implementation takes part when the three-way test runs it.
The CI report lists the seeds of each profile, so a profile without a path stays visible.

## Mutants

`one_faults` lists every 1-fault mutation of a seed:

- every node replaced by `7`, `true`, `null`, `[]`, `{}` and `"x"`;
- an object member removed (null against absent);
- an object's keys and a list reversed;
- a list's first entry duplicated;
- every string value and object key with NBSP, a double space, a tab, a trailing `\r`, U+212A for k,
  U+0130 for i, upper case and Arabic-Indic digits;
- every array or string that a wire-contract table limits (`max_items` and `max_bytes` checks of
  `soft-norms@0`, with `ve/wire_contract/limits.json`, and of the corpus units) resized to limit − 1, limit and
  limit + 1.

A 2-fault mutant combines two of them at unrelated paths. The CI sample takes `CI_BUDGET` mutants per surface
(6,000 1-fault and 1,500 2-fault mutants), round-robin over the seeds, from a fixed seed. `--deep N` takes N times
as many from the date's seed.

Lean and Rust read packages of restricted JSON only, so an input with `null` (Python's `canonical_json` refuses
it) is shown to Python alone. A runner that refuses one restricted-JSON input as a package is giving an answer
(`framing`), and that answer is compared.

## Findings

- **`python-crash`**: Python raised something other than `VEError`. An exception raised by the fuzzer's own
  adapter, for a field the adapter reads, means the call cannot be made and is not counted.
- **`no-answer`**: a Lean or Rust process did not answer, by panic, signal, CPU limit or malformed output. The
  batch is split until the input is alone.
- **`outcome`**, **`code`**, **`diagnostic`** or **`value`**: two implementations that take part disagree.

A finding's signature is the surface, the profile (P0 family and kind, Lean route or wire unit), the classes, and
each answer's outcome, code and contract-fixed text. In the text, values repeated from the input become `<v>` and
digits become `#`. A finding whose signature is not in the baseline is new. It is minimised by greedy deletion,
biggest cut first, keeping the signature, before it is reported. A baseline entry gives its minimised input, the
seed and mutation it came from, the participating engines, the answers, the signature and a follow-up id from the
table below. The suite fails on a new signature, on an entry that no longer reproduces (`fixed` or `changed`), and
on an entry with no follow-up id. After a fix, run `--update-baseline`, which drops entries that no longer
reproduce, and review the diff.

## Follow-ups

Each baseline entry names one of these ids. `tests/test_difffuzz.py` checks that every id used is listed here and
every id listed is used.

| Id | Disagreement | Where it is fixed |
|---|---|---|
| DF-1 | Python's `Environment` raises `TypeError` when `profiles` is a number or a Boolean. Lean and Rust say `UnsupportedProfile: profiles must be a sorted unique array`. | `fix/env-field-types` (env-profiles directive), not yet on `main` |
| DF-2 | Python raises `TypeError` (unhashable list or dict) when a definition body or AST node has an array or object where a name or tag belongs. Lean and Rust reject it with a diagnostic. | new: the Python formula decoder |
| DF-3 | Nested vocabulary fields of the wrong JSON type: Python's text is not Lean's decoder type diagnostic (`String expected`, `array expected`, `object expected`). This covers descriptions, verbalisations, predicate arguments, the sorts, predicates and constants objects, regulated blocks, definitions, and misspelt keys. The env-profiles directive fixed top-level fields only. | `wire-contract-PLAN.md` 7, S4 base row (`vocabulary@0.2`); env-profiles3-looprecheck1 notes the nested combinations |
| DF-4 | A non-string profile: Rust's text is `expected a string`. The P0 contract fixes `profiles must be a sorted unique array`, which Python and Lean give. | `wire-contract-PLAN.md` 7, S4 base row (`envelope@0.2`, Rust engine) |
| DF-5 | A non-string `spec_revision`: Python and Rust say `UnsupportedProfile: Unsupported specification revision …`; Lean says `InvalidInput: String expected`. Through the certificate verdict, Lean's rejection shows as `valid: false`. | `fix/env-field-types` for Python against Lean; `wire-contract-PLAN.md` 7, S4 base row for Rust |
| DF-6 | Unknown language and envelope field order. For an unknown `language` string, Python and Rust read the frozen v0 envelope (`Incorrect fields (missing profile)`) and Lean says `Unsupported language`. When fields are missing, Python reports the field set where Lean reports the profiles or the language. | `wire-contract-PLAN.md` 7, S4 base row (`envelope@0.2`) |
| DF-7 | P0 models: Lean's route reports a model's shape errors as `InvalidInput` (`fields do not match`, `invalid integer`, `String expected`) and reads the formulas before the model. Python and Rust report `InvalidModel`. | `wire-contract-PLAN.md` 7, S4 base row (`model@0.2`) |
| DF-8 | `dependency-order`: Lean's route does not decode the vocabulary (it accepts `{}`) and reports `DependencyCycle` or `DuplicateDeclaration` before an environment error. Rust checks node shape before the graph-size limit. | new: the P0 dependency-order route (PLAN-EXPAND2 3.4) |
| DF-9 | Nested decoder codes and order. Python reports `UnknownSymbol`, `SyntaxError` or `UnboundVariable` where Lean's decoder reports `InvalidInput` (sort references, AST bodies, variable indices). Python also checks declaration fields before the profile gates (definitions, data flags) that Lean and Rust check first. | `wire-contract-PLAN.md` 7, S4 base row (`vocabulary@0.2`, `formula@0.2`) |
| DF-10 | A non-string label: Python says `AdmissionError: invalid label []`; Lean and Rust say `InvalidInput`. | new: the P0 label route |
| DF-11 | Admission of a document whose certificate trace is malformed: Python reports the admission label error first, Lean the certificate's field set. | `wire-contract-PLAN.md` 7, S9 row (`ve-document@1`) |
| DF-12 | Unicode in a regulated act phrase (NBSP): Python rejects the risk environment (`W6 environment does not round-trip`) and Lean's risk route accepts it. | `wire-contract-PLAN.md` 7, S7 row (`risk@0`); FINDING-CLASSES class 4 (one normaliser) |
| DF-13 | Block routes (alternatives, risk, soft norms): Lean reports a block-level diagnostic (`risk.block`, `alternatives.block`, `invalid vocabulary`) where Python reports the field or the missing profile. | `wire-contract-PLAN.md` 7, S7 row (`alternatives@0`, `risk@0`); S3 for `soft-norms@0`'s environment |

## Not covered

- Duplicate object keys. The Python entry points take parsed objects, so the in-process comparison cannot
  carry them.
- The `max_count` limit form, and the core limits of `ve/limits.py`, which are not in a wire-contract table.
- 10,000-deep nesting.
- The legacy soft-norms route (`load_soft_document` against `ve_soft_norms_route`), which `wire_contract_gate.py`
  compares.
- The speech-acts, reports, discourse, rights, norm-defaults and readings routes. No corpus environment takes
  them, except through the routes listed above.
- `evaluation.json` and `countermodels.json` (v0 cases), which `tests/test_rust_conformance.py` and the Lean
  conformance runner check.
