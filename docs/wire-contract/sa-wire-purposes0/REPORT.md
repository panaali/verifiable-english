# sa-wire-purposes0 build report: the `purposes@0` wire contract, in shadow

**Status: built; no DRI signature is reserved; nothing stops the item.** The `purposes@0` contract (revision 1,
`shadow`) names spec 7.1's row (1.1b-1.1i) and 7.2's row 2 (2.1b) of a block `VE.Purposes.Wire`'s decoder refuses, with
spec 7's text, in Lean and Python. It decides nothing: the decoder still decides, `purposes@0` is not admitted, and
the document answers on the fixtures equal main's. No DELTA row (no user-visible output changes). Trust: R16, V +64,
K +0, S +0. Open: 7.2's rows 3-10 wait for PE-2 (section 2). Size: about 790 hand-written lines before the fix round,
over the ~600 line (section 3). Fix round 1 (section 8): every record argument is now bound to the request block (F1),
the R16 ties-pass row is in FOLLOW-UPS.md (F2), and the generated Rust table has seeded bugs (F-ready1).

Scope: [purpose-explanation-PLAN.md](../../spec/purpose-explanation-PLAN.md):1058 ("The C6 wire-contract item");
[wire-contract-PLAN.md](../../spec/wire-contract-PLAN.md):471 (S10, "contract first"); spec
[purpose-explanation.md](../../spec/purpose-explanation.md) 1.2, 5.4 (last bullet), 7.1-7.2 (:1448, :1465) and rule 8
(:1887). Precedent: ap-1bf.

## 1. Rows delivered

| Task part | Status | Where (test) |
|---|---|---|
| (1) `purposes@0.json`, its Lean hook, the `Diagnose.lean` row, the `UNITS` row, the lock | done: 9 members in fault order, texts registered verbatim (rule 8); 1.1c's limit is `VE.Purposes.maxLinks`, read | `ve/wire_contract/purposes@0.json`, `lean/VE/WireContract/Hooks/Purposes.lean` (`test_the_contract_registers_spec_7s_texts_verbatim_and_in_fault_order`, `test_the_limit_is_leans_and_never_copied`, the `#guard`s at :109-143) |
| (1) 7.2 rows computed without the checked view | 2.1b only; the `idsAgree` guard checks it against `VE.Purposes.check` both ways (deviation 6) | `Hooks/Purposes.lean:135-141` |
| (2) examples: one accepted, one at the limit, one refused per 7.1 row class | done: `base.json`, `limit.json` (256 links, accepted: WC10 requires examples clean), 15 refused (`links-over` is 257 links; 1.1e and 1.1i each have a side case) | `ve/wire_contract/examples/purposes@0/` (`test_the_examples_are_accepted_and_clean_in_both_engines`, `test_every_refused_example_round_trips_through_the_contract_in_both_engines`) |
| (3) fault catalogue, generated | done: regen entry `purposes-fault-catalogue` | `conformance/wire-contract/purposes@0-catalogue.json` |
| (4) shadow test | done: each answer (sha256 of its bytes, status, error, `document_id`, `source_id`) equals main's for `causal.ve.md` as written, with `purposes@0` and each example's block, with the block and no profile, and with the profile and no block; and for `rd9-docroute`, `group` and `qt0p-companion` (the document-mode fixtures under 8 KB), each as written and with the base block | `test_the_contract_is_off_the_verdict_and_identity_paths`, [shadow-main.json](shadow-main.json) |

The relay (`conformance/purposes_contract.py` `bound`) binds every field of a `diagnose` row to the table: the
member's contract, revision, check, phase, code, class and path, exactly its template's arguments (each a string),
and the text they render. `test_the_relay_refuses_a_retyped_or_rebound_record` deletes or retypes each field and
argument (7, true, null, [], {}, 1.5, a lone surrogate, a 10,000-deep list) and rebinds them.

`shadow-main.json` was recorded with `record()` (tests/test_purposes_contract.py) from a `ve_service` built at the
merge base 1ee886ca0 (sha256 6eb0cab36db5e46b56f677f80073320f177c482f9a3de2064d8248152ef99af2). If main changes a
fixture's answer, re-record it the same way from the new merge base.

## 2. Not delivered: the rows that wait for PE-2

- 7.1 row 1 (`purposes@0` listed, no block) belongs to the document mode (PE-2). Until then, a case with no block
  reads as `null` here and is reported as 1.1b (`test_the_adapters_read_the_case_block`).
- 7.2 row 1 (more than 256 links) cannot be reached after decoding, because 7.1's 1.1c refuses first.
- 7.2 rows 3-10: `check` tests them per link, and the first test (row 3) reads the checked view, so the first of
  them to fire cannot be named without the view. Row 7 needs no view, but it follows rows 3-6 of its link.

## 3. Deviations

1. **Region.** `tools/wire_contract.py` `_check_unit` (outside `UNITS`, one line): the legacy call reads the
   contract's own `input` members. Every existing unit's input is `["environment", "norms"]` (probe: `load(u)["input"]`
   for each `UNITS` key), so their call is unchanged. Mutant `py-legacy-input`.
2. **names.json and limits.json are not changed.** The limit is `VE.Purposes.maxLinks`, quoted from the decoder's
   record. A `MAX_LINKS` in limits.json would be a second owner of 256, and no name class applies.
3. **`adapter` stays.** The contract names an adapter (`purposes_block`). `Diagnose.caseRoot` serves contracts
   without one.
4. **Size.** 788 hand-written lines against the ~600 line before this section's final edit (`git diff --numstat
   1ee886ca0`, without generated files, locks, inventories, the trust baseline and the trust-mutant JSON). By file:
   test 192, hook 146 (guards included), this report 131, relay 84, table 52, faults 41, shadow record 28, other
   evidence and registrations. Nothing was cut: the self-review's fixes, R16's mutant fixtures and the evidence
   account for the growth past 548, and the remaining rows belong to PE-2, not to a next item of this one.
5. **Every value read once.** The two classifiers each run `decodeBlock`, and `member` decodes again up to the
   refused link: at most 3 decodes per block. Each one counts the links against `maxLinks` before it walks them
   (`decodeBlock`, `member`). `links-over` (257 links) and `limit()`'s 4,096-link probe both end in 1.1c.
6. **No theorems in the hook.** `tools/check_lean_imports.py` (spec wire-contract.md 7.3) lets `VE.Audit` import
   only the engine among `VE.WireContract.*`, so a theorem there could not be audited. The self-review's B (2.1b
   should be tied to `check`) is met by fixtures: `idsAgree` (guard :141) requires `purposes_ids` to name 2.1b
   exactly where `check` refuses with the text it gives two links of one id, on accepted, duplicate and 256-link
   blocks. The earlier `classifier_ok_iff` was removed for the same reason; guards :109-110 check its claim on
   fixtures. A universal tie is the FOLLOW-UPS ties pass.

## 4. Seeded bugs

[mutants.json](mutants.json): **35, all killed** (Lean 15, Python 16, contract table 2, Rust 2), plus 2 equivalent ones
(`hooks`' predicate and view, which the table never calls; guard :84 pins this, and mutant `lean-table-hook-kind`
shows that guard failing). Each was planted, run and restored. The file records the test and the first failure.
These are the task's four:

| Task's seeded bug | Mutant | Killed by |
|---|---|---|
| a 7.1 text differing from Lean's | `table-text-differs` | `test_every_refused_example_round_trips_through_the_contract_in_both_engines` |
| the link limit copied as 255 | `lean-limit-copied` | `Hooks/Purposes.lean:110` `#guard` (the 257-link round trip) |
| the contract on the verdict path | `py-verdict-path` (`ve/backends/relay.py` `answer`) | `test_the_contract_is_off_the_verdict_and_identity_paths` |
| a fault out of 7.1's order | `table-order`, `lean-order-polarity-first` | `test_the_contract_registers_spec_7s_texts_verbatim_and_in_fault_order`, `Hooks/Purposes.lean:127` |

Rust: only the generated `rust/ve-kernel/src/contract_tables.rs` changed; no Rust was written by hand. Its two seeded
bugs (`rust-table-text`, 1.1g's text; `rust-table-class`, 1.1c's class) each fail
`tests/test_wire_contract_rust.py::test_rust_table_rows_equal_the_contract_rows` (fix round 1).

## 5. Trust and evidence

- Trust (`uv run python tools/trust_map.py --check`, against 1ee886ca05d2): K +0, S +0, G +64 (`Hooks/Purposes.lean`
  +61, `Tables/Purposes.lean` +2, `Diagnose.lean` +1). The allowance is recorded in `docs/trust-baseline.json` with
  "SIGNED by standing ruling R16 (DRI-RULINGS.md), sa-wire-purposes0, 2026-10-18". The FOLLOW-UPS.md row under
  "## sa-wire-purposes0" asks for the ties pass (added in fix round 1: the build round claimed it but had not written it).
- Trust mutants (13a, `--test` the hook and Diagnose modules, `--allow` [trust-allow.json](trust-allow.json)):
  [trust-mutants.json](trust-mutants.json): 173 KILLED, 0 SURVIVOR, 0 UNKNOWN, 25 ALLOWED, 2 INVALID, exit 0
  (rescored after an allow-only wording edit; the full run before it had the same counts). Of the 25 allowed, 11 are
  the table's unread `inherited` flags, 3 are an unreachable `getD` default, 2 are the link-number literal inside
  `find?`, and 9 do not elaborate. The first sweep
  had 2 real survivors: a 256-link block refused for a link, and a later bad ref in a side. Both now have guards.
- Lean: `lake build` (1363 jobs) and `python3 lean/audit.py` PASS (824 files, 9276 theorems, only the allowed
  axioms). `regen_generated.py --write` ran twice (39 entries): once on the code, and once after the theorems left
  the hook. `tools/check_lean_imports.py` passes.
- Pilot bytes: 0 (shadow: no route reads the contract; `grep -rn purposes_contract ve/` finds nothing).
- Overlap with in-flight branches: only generated inventories and shared side tables (`tools/trust-classes.json`,
  `ve/assurance-manifest.json`), shared with en-e3a, cmp-s3-cfr-1, ps-2ac, ps-3 and sa-checked-view.
- SELF-REVIEW: 1 A, 6 B, 8 C; fixed 13 (A: side rows follow `decodeSide`; B: per-definition mutants, 2.1b checked
  against `check` (deviation 6), every record field bound, more document fixtures, this section, deviation 2; C: deviation 1,
  shadow record provenance, mutant lines re-cited, the size measured, a missing block noted, the read-once bound).
  Not done: C `adapter` → `caseRoot` (deviation 3), and C unreachable fallback (it is now an allowed equivalent).

## 6. Tests

- Selected run on 3c5d947be (`mac-pytest.sh --select -- --base 1ee886ca0 --run`, MAC_PYTEST_NO_DEFER=1): 502 units in 6
  Actions shards. Shards 1-5: 434 units, 433 passed, 1 failed:
  `tests/test_regen_generated.py::test_every_entry_whose_commands_import_the_service_client_is_marked` (the new
  `purposes-fault-catalogue` entry lacked `service="write"`; fixed in b94f57564). Shard 6 (68 units) gave Actions no
  result by the deadline. The runner's VM fallback re-ran the whole selection at load 70-80 (36 units in 2 h, its
  3-hour cap would have stopped it), so I stopped it. **Shard 6's units were not run on this branch**; the chain's
  gate on the final HEAD runs them.
- The failed id, rerun after the fix with `tests/test_purposes_contract.py` (`mac-pytest.sh -- <ids>`, VM): 8 passed.
- Not run: the full gate (the chain runs it on the final HEAD).

## 7. Self-review against BUILDER-CHECKLIST

1. Typed and contained: PASS, `test_the_relay_refuses_a_retyped_or_rebound_record` (every field and argument
   deleted or retyped with each value class, including a 10,000-deep list; it found and fixed a `TypeError` on a list `check`).
2. Deliverables: PASS, section 1 (one row per task part, each with its test). Section 2 lists what waits for PE-2
   (the task names that cut). No Python copy of a decision (the relay reads Lean's record) and no report test.
3. Tests can fail: PASS, [mutants.json](mutants.json) (22 killed) and [trust-mutants.json](trust-mutants.json) (exit 0).
4. Engines agree: PASS, `test_every_refused_example_round_trips_through_the_contract_in_both_engines` (Lean, the
   Python engine and the legacy validator, record by record), and `test_the_examples_are_accepted_and_clean_in_both_engines`.
5. R8 binding: PASS since fix round 1 (the build round's PASS overstated it: no argument was bound to the request
   block, review F1). The record is bound to the table by `test_the_relay_refuses_a_retyped_or_rebound_record` (`absent`,
   a shifted check, another unit's check, extra and missing arguments, an extra field), and each argument to the request
   block by `BINDS` (`conformance/purposes_contract.py`): `test_a_record_naming_what_the_request_does_not_carry_is_refused`,
   `test_every_argument_rebound_away_from_the_request_is_refused`, `test_binds_ties_every_member_of_the_table_and_no_other`
   and `test_leans_genuine_records_on_any_json_value_bind`. Row count and ids are bound by `run_bound` in the relay.
6. Gate evidence: PASS. The chain runs the gate on the final HEAD; section 6 says what the selected run did not cover (shard 6).
7. No unsigned item: PASS. The only growth is R16, signed in `docs/trust-baseline.json`, and there is no DELTA row.
8. DELTA: N.A. No user-visible output changes: `test_the_contract_is_off_the_verdict_and_identity_paths`
   (the answers' bytes equal main's).
9. Selection: PASS. `tools/select_tests.py --base 1ee886ca0` selects 473 of 578 files (the Lean change reaches
   `ve_service`), including `tests/test_purposes_contract.py` and `tests/test_wire_contract_lint.py`.
10. Statements: N.A. No theorem added (deviation 6); `lean-ids-wrong-test` and `lean-ids-never` break guards :109-110 and :141.
11. Limits fail closed: PASS, `test_the_limit_is_leans_and_never_copied` (257 links → 1.1c `ResourceLimit`) and
    guard :110 (a 256-link block refused for a link stays 1.1g). No clocks or sleeps.
12. CPU: N.A. No route runs the contract; the diagnose unit is new and only diagnostics read it.
13. Test-removed: N.A. No test removed or renamed.
14. Both directions: PASS. Each check has accepted cases (guard :109, `base`, `limit`) and refused ones (:110); `idsAgree` both ways. Spec
    re-read: the 9 texts against purpose-explanation.md:1448-1480 (also read by the test above), and the fault order
    against `decodeLink` (Wire.lean:71-83) and `check` (WellFormed.lean:142-145).
15. Overclaim, silent cut, every check can fail, limits charged first: PASS. "Every" claims cite their tests above.
    The cut is the task's own (7.2 rows that need the view). Each new guard has a mutant (mutants.json). Limits are
    charged before walking (deviation 5).

Next item: pe-2 (the purposes block in the document mode), after sa-checked-view.

## 8. Fix round 1 (review sa-wire-purposes0-review.final.md)

- **F1 (B), R8 (b).** `bound(row, block)` now ties every argument to the request block through one table, `BINDS`,
  one relation per member, enumerated from the contract (a member without one is refused): 1.1c's `limit` is a count the
  block's links exceed; 1.1d's `link` is a position 1..n; 1.1e's `id` is a link id, marker or side ref id of the block;
  1.1f-1.1i's `link` is a link id of the block, and 1.1f/g/h's quoted value is that link's field. A string is compared as
  it is; any other value is compared, type for type, with the JSON value Lean's spelling parses to, so no Lean spelling
  is copied. PROBE F1 exits 0 (it printed `accepted` before the fix). Python only; Lean and Rust unchanged.
- **F2 (B), R16.** The `## sa-wire-purposes0` row is in `/home/seyran/code/manage-agents/FOLLOW-UPS.md`
  (`trust_map.py --check` re-run: K +0, S +0, G +64, trusted +64, PASS). PROBE F2 exits 0.
- **F-ready1 (B).** Seeded Rust bugs `rust-table-text` and `rust-table-class` (section 4).
- Seeded Python bugs for F1: 11 `py-binds-*` mutants in [mutants.json](mutants.json), each failing a named test.
- Not done (C): F3 (the 2.1b description), F4 (size; this round adds about 60 lines of code and 120 of tests), F5, F6.
