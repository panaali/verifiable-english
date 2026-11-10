# sa-wire-purposes0 build report: the `purposes@0` wire contract, in shadow

**Status: built; no DRI signature is reserved; nothing stops the item.** The `purposes@0` contract (revision 1,
`shadow`) names, for a block `VE.Purposes.Wire`'s decoder refuses, spec 7.1's row (1.1b-1.1i) with spec 7's text,
and 7.2's row 2 (2.1b, duplicate link ids). It decides nothing: the decoder still decides, `purposes@0` is not
admitted, and every document-mode answer equals main's. No DELTA row (no user-visible output changes). Trust: R16.

Scope: [purpose-explanation-PLAN.md](../../spec/purpose-explanation-PLAN.md) "The C6 wire-contract item";
[wire-contract-PLAN.md](../../spec/wire-contract-PLAN.md) S10 ("contract first"); spec
[purpose-explanation.md](../../spec/purpose-explanation.md) 1.2, 5.4 (last bullet) and 7.1-7.2. Precedent: ap-1bf.

## 1. Rows delivered

| Task part | Status | Where |
|---|---|---|
| (1) `purposes@0.json`, hook, `Diagnose.lean` row, `UNITS` row, lock | done: 9 members in fault order; texts registered verbatim (spec 7, rule 8); the limit is `VE.Purposes.maxLinks`, read | `ve/wire_contract/purposes@0.json`, `lean/VE/WireContract/Hooks/Purposes.lean`, `tools/wire_contract.py` |
| (1) 7.2 rows computed without the checked view | 2.1b only (see 2) | `Hooks/Purposes.lean` `classifier "purposes_ids"` |
| (2) examples: one accepted, one at the limit, one refused per 7.1 row class | done: `base.json`, `limit.json` (256 links, accepted: WC10 requires examples clean), 12 refused (`links-over` is 257 links) | `ve/wire_contract/examples/purposes@0/` |
| (3) fault catalogue, generated | done: regen entry `purposes-fault-catalogue` | `conformance/wire_contract_faults_purposes.py`, `conformance/wire-contract/purposes@0-catalogue.json` |
| (4) shadow test | done: every document answer (sha256 of its bytes, status, error, `document_id`, `source_id`) equals main's, recorded with the merge base's `ve_service`, on `causal.ve.md` as written, with `purposes@0` listed and each example's block, the block without the profile, and the profile without a block | `tests/test_purposes_contract.py::test_the_contract_is_off_the_verdict_and_identity_paths`, `shadow-main.json` |

The relay (`conformance/purposes_contract.py` `bound`) types and binds each `diagnose` row to the table (member of
the check's phase, path `/purposes`, exactly the template's arguments, each a string); the fuzz test retypes and
rebinds each field (`test_the_relay_refuses_a_retyped_or_rebound_record`).

## 2. Not delivered: rows that wait for PE-2

- 7.1 row 1 (`purposes@0` listed, no block): the document mode's, PE-2 (no block to diagnose here).
- 7.2 row 1 (more than 256 links): unreachable after decoding (7.1's 1.1c refuses first).
- 7.2 rows 3-10 (unknown unit, distinct parts, adjacency, marker kind, inertness, 6a, denied with a share, sole,
  unmarked unit, LABELLED coverage): `check` tests them per link after row 3, which reads the checked view, so the
  first of them to fire cannot be named without it (row 7 needs no view but follows rows 3-6 of its link). PE-2.

## 3. Deviations

1. The legacy call in `_check_unit` reads a contract's own `input` members (one line), so a unit whose input is not
   `environment, norms` can run its legacy validator; the existing units' inputs are unchanged.
2. Size: ~620 hand-written lines (548 before this report and mutants.json), over the ~600 line by the evidence;
   nothing was cut, since the remaining rows are PE-2's, not a next item of this one.

## 4. Seeded bugs

[mutants.json](mutants.json): **7, all killed** (Lean 3, Python 2, contract table 2). Planted, run, restored.

| Id | File (definition) | Bug | Killed by |
|---|---|---|---|
| `lean-limit-copied` | `Hooks/Purposes.lean` (`member`) | limit copied as 255 | `Hooks/Purposes.lean:119` `#guard` |
| `lean-ids-never` | `Hooks/Purposes.lean` (`classifier`) | 2.1b never named | `Hooks/Purposes.lean:109` `#guard` |
| `lean-order-polarity-first` | `Hooks/Purposes.lean` (`linkMember`) | 1.1g before 1.1f | `Hooks/Purposes.lean:119` `#guard` |
| `table-text-differs` | `purposes@0.json` (1.1g) | text differs from Lean's | `test_every_refused_example_round_trips_through_the_contract_in_both_engines` |
| `table-order` | `purposes@0.json` (1.1f/1.1g) | fault out of 7.1's order | `test_the_contract_registers_spec_7s_texts_verbatim_and_in_fault_order` |
| `py-verdict-path` | `ve/backends/relay.py` (`answer`) | contract on the verdict path | `test_the_contract_is_off_the_verdict_and_identity_paths` |
| `py-bound-path` | `conformance/purposes_contract.py` (`bound`) | path unbound | `test_the_relay_refuses_a_retyped_or_rebound_record` |

Rust: only the generated `rust/ve-kernel/src/contract_tables.rs` changed; no hand-written Rust.

## 5. Trust, evidence and tests

- Trust: new Lean-owned diagnostic behaviour, R16 (standing ruling): `Hooks/Purposes.lean` and `Tables/Purposes.lean`
  classed `G[V]` as `Hooks/Acts.lean`; numbers and allowance in section 6. FOLLOW-UPS.md row under
  "## sa-wire-purposes0" (the ties pass).
- Pilot bytes: 0 (shadow; no route reads the contract).
- Overlap: only generated inventories and shared side tables (`tools/trust-classes.json`,
  `ve/assurance-manifest.json`) with en-e3a, cmp-s3-cfr-1, ps-2ac, ps-3, sa-checked-view.

## 6. Final checks

(filled in after the heavy checks)

Next item: pe-2 (the purposes block in the document mode), after sa-checked-view.
