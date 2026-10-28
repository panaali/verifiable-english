# me-4: tables and pinned data, the Lean core (plan 3.3, ME-4)

- **Status:** done; no DRI signature needed (the one DELTA row is R16). Branch `feature/me-4`, synced with main at
  `d25bc343b`; the gate runs on the final HEAD.
- **What changed:** new `lean/VE/Calc/{Table,Csv,Jsonl,Data,TableExamples}.lean`: cells, tables, filters with typed
  negated atoms (J9), aggregates, CSV and JSON-lines decoders, and `runCounted` bound to SHA-256 under the budget (J2).
  Every theorem of plan 3.3 and spec 4.1 to 4.3 is proved (12, spec text); spec 4.4's `spanMatches_iff` is me-4b's.
- **Open:** me-4b (the `Handles` data kind, relay, committed files, spans). Size is ~760 hand-written lines, over the
  ~600 guide (see "Size").

## Plan rows

| Plan row (ME-4, 3.3) | Delivered | Where |
|---|---|---|
| `lean/VE/Calc/{Table,Csv,Jsonl,Data}.lean` | yes | commit `e7431b070` and later |
| Proves 3.3 | yes, except `spanMatches_iff` | `Table.select_iff`, `select_sublist`, `Filter.bool_atoms`, `negated_typed`, `Agg.run_count`, `_sum`, `_mean`, `_empty`, `_nonnumber`, `Agg.runB_sound`, `counted_bound`, `counted_exhausted`; statements equal spec 4.1 to 4.3 after whitespace normalisation (12 of 12) |
| Filters: typed negated atoms, no general negation (J9) | yes | `Filter`, `Filter.bool_atoms`, `Filter.negated_typed`; T-1 guards `TableExamples.lean:22-32` |
| `runCounted` under the case's budget; `Counted.exhausted` (J2) | yes | `Data.lean` `runCounted`; `Agg.runB` charges one unit per (row, filter node) visit |
| Lean recomputes the digest; a wrong digest refused | yes | `runCounted`; guards `:35-39` (DigestMismatch, UnknownHandle, UnknownColumn, TableFormat) |
| `Handles` data kind; relay registers bytes by SHA-256 | **no: me-4b** | the task's seam (protocol queue, SYNTHESIS 4.2); `Protocol.lean` and `service_schema.py` untouched |
| `tests/test_calc_tables.py`, `tests/data/calc/*.csv`, `*.jsonl` | **no: me-4b** | the committed files are read by me-4b's relay; here the tables are in-source bytes (size rule) |
| Fixture: 30-row synthetic trial, counts by filter | yes | `:96-106`, generated in Lean from a stated rule |
| Fixture: V-5 from the 20 rows' counts | yes (in-source table) | `:108-132`: all 20 hold; a changed printed value fails. The committed-file copy is me-4b |
| Fixtures: empty selections; an absent cell; T-1; T-3 | yes | `:22-32`, `:41-62`; T-3 at budget 6 and at the default, each boundary (12/11 and 5/4 visits) on both sides |
| R-10a, R-10c (spec 13.6) | **no: me-4b** | complete requests; they need the counted-value wire |
| V-12; a source finding beside "transcription unchecked" | **no: me-4b** | span checks need the source handle (task text) |
| Seeded bug, Lean: `isFalse` selects every non-true cell | yes | S1 below |
| Seeded bug, Python: the relay sends the wrong handle's bytes | **no: me-4b** | no Python product code here |

Choices where the spec is silent, all on the refusing side: a CSV header must name every declared column once and no
other; a JSON-lines line is a flat object of scalars with each key once (Lean's own parser keeps the last of two equal
keys, so a reader built from its `str` and `num` parsers refuses them); a JSON number or Boolean is that value in a
column of its type and text in any other; `null` is absent; budget 0 allows nothing, even over no rows (BUILDER-CHECKLIST
11). `DataDecl` follows spec 4.3 (plan 3.3's `formatOf d`/`columnsOf d` became its fields). `Agg.variance` and
`populationVariance` are ME-7's.

## Seeded bugs (Lean; no Python or Rust product code changed)

Each was planted, shown failing and restored (`mutants.json`):

| Bug | File | Fails |
|---|---|---|
| S1 `isFalse` selects every cell that is not the Boolean true (plan) | `Table.lean` | `Filter.sel_iff`, `Filter.bool_atoms`; its count is 3 against the guard's 1 (`:25`) |
| S2 `notEquals` selects a non-number cell | `Table.lean` | `Filter.sel_iff` |
| S3 an `and` node costs nothing | `Table.lean` | `Filter.selB_sound` |
| S4 the mean of an empty list is 0 | `Table.lean` | `Agg.run_mean`, `Agg.run_empty` |
| S5 the digest is not checked | `Data.lean` | `counted_bound` |
| S6 CRLF ends a record only after a quote | `Csv.lean` | guard `:68` |
| S7 a repeated JSON key accepted | `Jsonl.lean` | guard `:90` |
| S8 budget 0 allows a run | `Table.lean` | guard `:47` |
| S9, S10 end of file drops a last record without a line end | `Csv.lean` | guards `:68-75` |
| H1 to H4 `Table.cell`, `decodeTable`, `Filter.Selects`, `Agg.run` | `Table.lean`, `Data.lean` | guards `:32`, `:39`; `Filter.sel_iff`; guards `:23`, `:27` |

`tools/trust_mutants.py` (12 definitions, full run on the merged HEAD `0f35bb7c8` in the cloud): 253 KILLED,
0 SURVIVOR, 0 UNKNOWN, 24 INVALID, 68 ALLOWED (`trust-mutants.json`). The allowed ones (`trust-mutants-allow.json`)
are `Filter.Selects` (a proposition no evaluated check reads; every mutant falsifies `Filter.sel_iff`), equivalents
(`l ≤ []` is `l = []`; `(l.reverse.take 1).getLast?` is `l.getLast?`) and mutants Lean refuses to build. Its
survivors in earlier runs became fixtures: the CSV end-of-file cases, a key or column missing first, in the middle or
last, a JSON Boolean in other columns, and the decoded JSON-lines columns. The last commit after it reorders
`tools/trust-classes.json` to main's order, with no class changed.

## Trust, size, bytes

- `tools/trust_map.py --check` on the final HEAD: K +0, S +54, untied V +94, total +148; PASS with the R16 allowance
  (DELTA row 1). FOLLOW-UPS "## me-4" asks for the ties pass. `lean/audit.py`: PASS.
- Size (`git diff --numstat $(git merge-base HEAD main)`, hand-written): Lean 550 (product 414, fixtures 134,
  imports 2), `tools/trust-classes.json` 85, `ve/assurance-manifest.json` 19 (the JSON-lines decoder pinned), allow
  file 104, DELTA 10. With this report, about 760, over the ~600 guide. Moving more out would have split the
  decoders from `decodeTable` or the fixtures from what they check; the scope already cut is in the table above.
- Pilot bytes expected: 0 (plan "Bytes: 0"; ME-P2 lands them after me-4b). Nothing is claimed.

## Tests

- Selected tests (`mac-pytest.sh --select`, GitHub Actions, 4 shards, 90 units): 89 passed. One failure,
  `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`, was the new JSON-lines
  decoder not yet in the manifest. It is now pinned (`ve/assurance-manifest.json`, total 39046), and the file's
  137 tests pass locally.
- `gate_collection.py --check --prebuilt`: 0 added, 0 refused, 0 stale, 0 malformed. `regen_generated.py`: 33 entries
  written after the merge. The full gate is the chain's.

## Next item

**me-4b**: the `Handles` data kind (`Protocol.lean`, protocol queue), the relay registering file bytes by SHA-256 with
Python's seeded wrong-handle bug, `tests/test_calc_tables.py` with `tests/data/calc/*.csv`/`*.jsonl` (V-5 from the
committed file), span checks (`spanText`, `readSourceNumber`, `spanMatches_iff`), V-12, the source finding, R-10a
and R-10c. Then ME-P2.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer; the service mode is me-4b.
2. PASS: the plan rows above, each with its commit or test, or me-4b by the task's seam; a grep of the diff finds no
   Python copy of a Lean decision and no report test.
3. PASS: `mutants.json` (S1 to S10, H1 to H4) and `trust-mutants.json` (0 survivors); allow entries name exact
   definitions and operators.
4. N.A.: no Python or Rust path computes tables.
5. N.A.: no relay; undeclared columns and handles are refused in Lean (guards `:35-39`, `:70`, `:90`).
6. PASS: synced with main (`0f35bb7c8`); trust mutants were rerun on that merge; the gate runs on the final HEAD.
7. PASS: DELTA row 1 cites R16 with its evidence; FOLLOW-UPS row written.
8. PASS: no public output changes (DELTA preamble); nothing relays the new modules.
9. PASS: the selection picked `tests/test_assurance_manifest.py`, which caught the unpinned decoder.
10. PASS: 12 of 12 statements equal the spec text; S2 to S5 and H3 break proofs.
11. PASS: budget 0 is UNKNOWN even over no rows (guard `:47`); T-3's boundaries at 12/11 and 5/4 visits (`:44-46`).
12. PASS: `Agg.runB` is one pass over the rows; the visit counts in guards `:44-46` fail if the charge changes.
13. N.A.: no test removed or renamed (`gate_collection.py --check --prebuilt`: 0 refused, 0 stale).
