# Lean-first batch 9 (quantities): DELTA and gate record

Base `9aaf918d` (main after batch 2), head `lean-first/b9`. Row 9 of `docs/LEAN-FIRST-PLAN.md` 5.2:
`ve_quantity` decides by default and W6 typing goes to Lean's `check` mode; Python's W6 elaborator and
`quantity_admission.py` and Rust's `units.rs` are deleted ([`LEDGER.md`](LEDGER.md)).

## What changed

- **Lean (+22 lines).** The service's `check` mode takes a W6 case: when the environment carries
  `unit_schema` or `units`, it decodes the environment and the `ve-quantity@1` statement with
  `VE.Time.Wire.decodeEnvironment` and `decodeQuantity` (the decoders the `quantity` route already uses)
  and answers `Q`, the erased `core`, `meaning_id`, `environment_id` and `target_environment_id`
  (`VE/Service/Standalone.lean` `checkCase`; the row schema in `ResponseShape/Schemas/Check.lean`, generated
  into `ve/backends/lean_service_schema/check.json`). No theorem or approved statement changed
  (`tools/lean_statements.py --check`: 0 added, 0 removed, 0 changed); `VE/Time/Wire.lean` is the base file.
- **Python relays.** `elaborate_quantity`, `quantity_meaning_id` and `prove_quantity`'s problem read
  Lean's `check` row; `check_quantity_certificate` and `quantity_countermodel` return Lean's `quantity`
  rows (`certificate`, `countermodel`); `admit_document` sends every W6 document to Lean's `quantity`
  route under every authority. `Environment` of a W6 envelope (profiles with `time@0`, no `risk@0`) asks
  the `check` mode first, then constructs from the accepted input (a failure after acceptance, or an
  identity Lean did not answer, is `CheckerUnavailable`). Python keeps certificate search
  (`prove_quantity`, rule 3) and the English surface's numerals and dates.
- **Rust.** `ve conformance` refuses a `quantity` case with `UnsupportedProfile` (`rust/ve/src/main.rs`,
  test `quantity_tests::quantity_cases_are_the_lean_routes`). The fuzzer has no Rust engine on the
  quantity surface (`tools/difffuzz.py` `ROUTES["quantity"].no_rust`).
- **Limits stay Lean's.** The replay step limit is not sent by the client:
  `check_quantity_certificate` lost its `max_steps` argument (only one test passed it).
- **Transport check (review B).** The W6 relays sent the caller's data to Lean with no wire check: a lone
  surrogate escaped as `UnicodeEncodeError`, a set or bytes as `TypeError`, and `json` sent a tuple
  formula as a list, so it was admitted. Every checker transport now runs one check,
  `ve.environment_wire.wire_checked`, before encoding: `relay.decide`, `relay.rows` (every Lean service
  call, not only W6's) and `rust_jsonl.run`. The check rejects with `ve.wire`'s texts exactly the values
  `json` cannot send as themselves: a lone surrogate, a set, bytes, a tuple, another type, a non-string
  key, a non-finite float, a cycle, or nesting past 10,000 levels, where the encoder's C stack overflows.
  The walk is iterative. JSON values that are off the restricted subset (null, a float, a negative or
  over-range integer, depth past 256) are still sent. Lean decides them in its own words (R9). The
  review's suggested `canonical_json` would have pre-empted Lean on those, including signed row W9.3. No
  case of the quantity corpus (12,863) or the discourse corpus (3,175) is rejected by the check, and it
  returns its input unchanged, so the corpus A/B cannot change. One internal caller sent a tuple: the
  norm-defaults conformance harness's conflict witness filling, now `filling_json` (the same bytes).
  Tests: `tests/test_relay_wire_check.py` (every W6 entry point × unsendable and wrong-shaped values,
  every formula node replaced, the CLI's `check_document` reproduction, both transports, the 256 and
  10,000 depth boundaries); seeded bug M6.

## Gate 5.1

### 1. Suite

The full suite at the head, `VE_NATIVE_PREBUILT=1`, in five chunks plus the four known >10-minute tests
in their own call (`full-suite-in-chunks`; host load 35–90): 11,072 passed, 6 skipped (optional packages,
pinned tokenizer, P5 materials, admission outside Rust scope), 0 failed after two fixes found by the run
(`test_nested_pytest`: the mutant runner now builds its command with `tools/nested_pytest`;
`test_consolidation_tools`: `lean/declarations.txt` regenerated), whose files were re-run and pass. Cargo:
every crate's tests pass; `tools/rust_build.py --check` and the `ve_service` hash are pinned in
`lean/checkers.lock`. Lean: `lake build`, `lean/audit.py` (4,311 theorems, standard axioms only),
`VE/Route/frozen.py`, `tools/lean_statements.py --check` pass.

Test changes are limited to the batch's own: the Rust legs of the W6 tests are removed (Rust has no
quantity route), the W6 tests compare Lean with Python's relay, `test_units_rust_w6a.py` becomes
`test_units_relay_w6a.py`, and the asserted codes and texts follow the rows below. The gate collection
(`tools/gate-collection.json`) lists 81 removed and 78 added IDs: renames (`…three_ways` →
`…relay_and_lean`), the removed Rust-only tests, and the new relay tests.

After review B's fix: `lake build` and `lean/audit.py` pass. The full suite (5 chunks, `-n 16`,
`VE_LEAN_PREBUILT=1`, then the four slow tests alone) has 11,212 passed, 6 skipped and 0 failed. The
gate collection gains the 144 new test IDs and removes none.

Not run: the hermetic `tools/gate.py` in a fresh worktree (its Lean rebuild and suite exceed one
60-minute call); the suite above ran on the committed head in this worktree.

### 2. Corpus A/B

`tools/lean_first_diff.py`, base recorded from `/tmp/ve-b9-base` (`9aaf918d` with its own builds), head
from this checkout; `compare --delta docs/lean-first/b9/delta.json` exits 0 with `"unlisted": 0` on every
corpus (`evidence/*-compare.json`).

The batch's own corpus is new: no W6 corpus is stored, so the calls the W6 tests make to a W6 public
operation were captured at the base (`capture_quantity.py`, the method of batch 4) into
`docs/lean-first/quantity-corpus.json.gz`: 12,863 distinct calls (11,375 `elaborate_quantity`, 584 W6
`Environment`, 724 `prove_quantity`, 62 `quantity_meaning_id`, 42 `admit_document`, 41
`check_quantity_certificate`, 35 `quantity_countermodel`), each recorded under the `python` and `lean`
authorities (`--corpus quantity`).

The counts are in the generated block at the end of this file (`report.py`).

Every difference comes from one rule, **R9: a W6 answer is Lean's, relayed verbatim**. The differences
are the same under both authorities, except the four W9.4 admission records (69 `python`, 65 `lean`):
the base's `lean` authority already sent W6 admission to Lean's quantity route.

**Use-case harness (eligibility, W6).** `usecases/eligibility/run.py --no-write` at base and head prints
byte-identical results (80 profiles, 32/32 mutants killed; `evidence/eligibility.json`). No other harness
or pilot calls a W6 operation; the pilots corpus covers the use-case documents.

#### W9 wording (88 records, 10 pairs, signed as one block)

| Id | Base (Python) | Head (Lean) | Records |
|---|---|---|---:|
| W9.1 | `<text>` of a `ResourceLimit` (aggregate nodes, evaluation budget, node or depth limit, 40-digit decimals) | `ResourceLimit: <text>`, Lean's text under its class's `Code: ` form (batch 0's W1 rule) | 62 |
| W9.2 | `Integer literal exceeds 40 characters` | `ResourceLimit: numeral length` | 16 |
| W9.3 | `Quantity AST exceeds node or depth limit` (a statement nested past the wire reader) | `ResourceLimit: JSON depth exceeds 256` (the service's JSON reader stops first) | 2 |
| W9.4 | `Incorrect fields (missing=['certificate'], unknown=[])`, `Invalid quantity certificate` (documents, `python` authority only) | Lean's decoder texts: `fields do not match: expected [...], got [...]`, `Invalid quantity certificate: fields do not match: ...` | 4 |
| W9.5 | `Verbalisations must be nonempty strings` | `String expected` (not a string) or `Verbalisation must be nonempty` (empty) | 4 |

#### O9 order (40 records)

| Id | Base | Head | Records |
|---|---|---|---:|
| O9.1 | `SyntaxError: Non-canonical integer literal '١١…'` (Arabic-Indic digits in a W6 numeral) | `InvalidInput: invalid integer` | 40 |

Outside the corpus (no base test builds the input; pinned by
`test_units_relay_w6a.py::test_either_w6_field_takes_lean_s_decoder`): a `time@0` envelope with only one
of `unit_schema` and `units` was Python's `UnsupportedProfile: unit_schema and units require the
ve.core@0.2 quantity route together`; it is now Lean's `InvalidInput: fields do not match: expected
[language, profiles, spec_revision, vocabulary, unit_schema, units], got [...]` (O9.2).

#### V9 verdict (6 records, each needs a DRI signature)

| Id | Base | Head | Records | Why |
|---|---|---|---:|---|
| V9.1 | `check_quantity_certificate` returns `false` for a certificate whose replay exceeds 10,000 steps | raises `ResourceLimit: certificate replay exceeds 10,000 steps` | 4 (2 cases × 2 authorities) | An exhausted replay is UNKNOWN, never "not valid" (checklist item 6); Lean's route already answered `ResourceLimit` for the same case (`test_w6a_certificate_steps.py`) |
| V9.2 | `ResourceLimit` `domain exceeds entity limit` with `path: /domains/s` | `ResourceLimit` `ResourceLimit: domain size`, no `path` | 2 (1 case × 2 authorities) | Same code and outcome; the tool classes it `verdict` because the `path` member is gone (Lean's diagnostic names no path) |

### 3. Deletion ledger

[`LEDGER.md`](LEDGER.md): 599 Python lines deleted in `ve/` (87 added: the relay, net −512), 1,021 Rust
lines (`units.rs` 922, its 93-line test, the re-exports and dispatch; 19 added: the refusal and its test),
+22 Lean. Every deleted decision site maps to a
Lean check. `tools/relay_lint.py` passes; the stage-0 inventory and inventory lint show no consumer of a
deleted symbol; `tools/check_rust_deps.py` and the layer checks pass with two new reviewed relay edges
(`ve.environment -> ve.backends.relay`, `ve.units -> ve.backends.relay`).

### 4. Latency

Measured back to back on the same host (load 30–50, so CPU is the comparison).

Measured: the eligibility harness (budget ≤ 1.25× base wall, `evidence/eligibility.json`) and every W6
operation of the quantity corpus in one process (`timing.py`, `evidence/timing-*.json`); the numbers are
in the generated block at the end of this file.

Each corpus call constructs its `Environment` first, so a typing call here is two service calls (the
environment, then the statement); a caller that keeps its `Environment` pays one. The interactive row
(p50 ≤ 2 ms Lean CPU, p95 ≤ 10 ms wall per service call on a quiet host) could not be checked on a
quiet host: the host load never fell below 30 during the batch. 79.4 s of Lean CPU over about 25,000
service calls is about 3 ms per call at load 45.

### Differential fuzzer

`difffuzz_ab.py` ran `--ci` and the 14 date seeds 2026-09-23 to 2026-10-06 (`--deep 1`) in both
checkouts (`evidence/difffuzz-ab.json`; summary in the generated block): no head-only finding signature in
any run, no unreproduced or unreviewed baseline entry. The baseline loses 27 `environment`/`quantity`
disagreements, because Python's W6 environment is Lean's. One entry (`{"units": {}}`, DF-9, Python's
`UnsupportedProfile` against Lean's `InvalidInput`) is re-recorded with Rust `n/a` (signature `cc847b4f…`
→ `41c14060…`); the count does not grow.

## Seeded bugs

`mutants.py` plants each bug alone, runs its test, and restores the file; a Lean mutant's build is
allowed in the lock while its test runs, and the clean build is rebuilt and checked against the lock after
each (`evidence/mutants.txt`).

| Seed | Behaviour claimed | Planted bug | Failing test |
|---|---|---|---|
| M1 | Lean's `check` mode answers the erased core | `check` returns `Q` as `core` | `test_units_lean_w6a.py::test_news_admission_agrees_with_the_relay` |
| M2 | either W6 field selects Lean's decoder | the `units` condition dropped | `test_units_relay_w6a.py::test_either_w6_field_takes_lean_s_decoder` |
| M3 | a W6 environment is admitted by Lean before Python constructs it | the relay gate never fires | `test_units_relay_w6a.py::test_every_display_collision_class_rejects` |
| M4 | an exhausted certificate replay is `ResourceLimit`, never `false` | the relay maps `ResourceLimit` to `False` | `test_w6a_certificate_steps.py::test_quantity_certificates_share_the_step_budget[12-False]` |
| M5 | Rust refuses a quantity case | `ve conformance` answers `ok` | `quantity_tests::quantity_cases_are_the_lean_routes` (cargo) |
| M6 | every transport sends only values `json` writes as themselves | `wire_checked` returns its input unchecked | `test_relay_wire_check.py::test_document_check_of_a_file_with_a_lone_surrogate_is_the_wires_veerror`, `::test_a_tuple_formula_is_not_admitted_as_a_list` |

M6 was added for review B and run alone (`mutants.py M6`); its block is appended to `evidence/mutants.txt`.
`test_every_seeded_bug_was_caught` takes the seed list from `mutants.py`.

## Acceptance items

| Item | Owner | State |
|---|---|---|
| Lean `check` mode for W6, relays, deletions, tests, A/B, fuzzer, latency, seeded bugs | AGENT | done, evidence above |
| Wording block W9 and order rows O9.1–O9.2 | HUMAN (DRI) | signed 2026-10-06 (Lean texts and order canonical) |
| Verdict rows V9.1 and V9.2 | HUMAN (DRI) | signed 2026-10-06: V9.1 an exhausted replay is UNKNOWN (ResourceLimit), never "false"; V9.2 same code and outcome, Lean wording |
| Hermetic `tools/gate.py` in a fresh worktree | AGENT (reviewer's run) | not run here, see 5.1 item 1 |
| Quiet-host latency for the interactive row | AGENT | deferred: the host was never quiet |

## Generated numbers

<!-- BEGIN GENERATED: python docs/lean-first/b9/report.py --write -->
| Corpus | Records per side | Same | Wording | Order | Verdict | Availability |
|---|---:|---:|---:|---:|---:|---:|
| quantity (`lean`, `python`) | 25,726 | 25,592 | 88 | 40 | 6 | 0 |
| probe (`lean`, `python`) | 18,870 | 18,870 | 0 | 0 | 0 | 0 |
| conformance (`lean`, `python`) | 39,612 | 39,612 | 0 | 0 | 0 | 0 |
| pilots | 278 | 278 | 0 | 0 | 0 | 0 |
| readings | 1,137 | 1,137 | 0 | 0 | 0 | 0 |
| discourse | 6,350 | 6,350 | 0 | 0 | 0 | 0 |
| **All** | 91,973 | 91,839 | 88 | 40 | 6 | 0 |

Eligibility harness: base 424.9 s wall, 224.4 s user CPU; head 394.8 s wall, 181.6 s user CPU (0.93× wall); results byte-identical.

Quantity corpus in one process: CPU 211.8 s at the base (211.8 s Python, 0.0 s Lean) and 230.7 s at the head (151.4 s Python, 79.4 s Lean), +9%; wall 333.2 s → 296.1 s.

| Operation | Calls | p50 wall base → head (ms) | p95 wall base → head (ms) | Total base → head (s) |
|---|---:|---:|---:|---:|
| `elaborate_quantity` | 11,375 | 3.5 → 6.6 | 18.6 → 17.4 | 72.7 → 106.8 |
| W6 `Environment` | 584 | 1.5 → 3.3 | 6.9 → 7.3 | 1.4 → 2.1 |
| `quantity_meaning_id` | 62 | 7.8 → 12.5 | 19.0 → 25.0 | 0.5 → 1.6 |
| `quantity_countermodel` | 35 | 6.3 → 13.9 | 4,075.8 → 370.6 | 24.1 → 3.3 |
| `check_quantity_certificate` | 41 | 19.4 → 15.0 | 1,109.3 → 220.7 | 6.9 → 2.0 |
| `admit_document` | 42 | 15.7 → 8.8 | 53.8 → 19.1 | 1.2 → 0.5 |
| `prove_quantity` | 724 | 152.5 → 126.9 | 1,199.3 → 1,044.6 | 226.4 → 179.8 |

Differential fuzzer: 15 runs (`--ci` and 14 date seeds), 0 head-only signatures, 682 → 647 new findings, baseline 384 → 357 entries, 0 head entries not reproduced.
<!-- END GENERATED -->
