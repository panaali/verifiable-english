# fp-onedoc-per-source: one document per source in the fidelity pilot runner

DRI decision `reviews/dri-decisions-20261030-fp-commitments.md` item 2 (DRI answer LP-20261030T1037-2/5).
Infra item for manage-agents tooling. No VE product code changed and there is no DELTA row, as the task requires.

## Defect

`tools-local/fidelity-pilot.sh` (writer rule 4) wrote every unit of a draw as one document with one header.
When a draw spanned two source documents (commitments: Anthropic RSP 3.4 and OpenAI Preparedness v2),
every row from the second source was refused with BearerNotOrgan, and narrowings cited units outside the draw.

## Change (installed in manage-agents, 2026-10-30 21:07Z)

The installed files are `/home/seyran/code/manage-agents/tools-local/fidelity-pilot.sh` and
`/home/seyran/code/manage-agents/tools-local/const-paper-pilot.py`. Backups are `*.bak-20261030-onedoc`.
Each file was replaced with `.new` + `zsh -n` + backup + `mv`, at a time when no process was running either file.

1. **Source of a unit:** taken from the `primary` column of `units.tsv`. Every draw tool writes it:
   `fidelity-pilot-units.py`, `fidelity-pilot-units-fresh.py`, `-1030c` and `pc-fid-rev2-units.py`.
   The grouping is written once to `<pilot>/DOCS` and checked against the units on every run, so a resumed
   run keeps the same grouping. A `DOCS` file that misses a unit stops the run.
2. **More than one source:** the writer composes one document per source, each with its own header,
   author and organs. Both auditors judge DOC per document (D1, D2, ...) in every round, including the
   round-2 relay. `diff` and `score` work per document. `RESULT.md` gives the number of documents
   composed and one DOC row per document.
3. **Resume safety:** a pilot dir whose `WRITTEN.md` already exists keeps one document (the same way
   `MODE` keeps family or whole).
4. **Single-source draw unchanged:** the writer input, audit topic, round-1 auditor prompts and `RESULT.md`
   are byte-identical to the old runner's (the `.bak` copy).

## Tests

`python3 -I /home/seyran/code/manage-agents/tools-local/test_fidelity_pilot_onedoc.py`: 8 tests, all
using scratch dirs, with no model calls. They passed on 2026-10-30 (`Ran 8 tests ... OK`). They cover:

- A 2-source fake draw gives 2 documents, each with its own header (family and whole modes).
- A 1-source draw is byte-identical to the old runner.
- The seeded bug "one header for all" fails a test (`test_seeded_one_header_for_all_fails`).
- `diff` requires every document from both seats.
- A `WRITTEN.md` written before the change keeps one document.
- A `DOCS` file that misses a unit stops the run.

The VE gate at `432763b0` (the merge base, with no product change) passed. This commit adds only these docs.

## Seeded bugs

Only Python and zsh changed (no Lean or Rust). Each bug was planted in a scratch copy and caught by the
named test. They are recorded in `mutants.json`.

| # | File | Bug | Failing test |
|---|---|---|---|
| S1 | `const-paper-pilot.py` | `docs()` puts every unit in one document (one header for all) | `test_two_sources_give_two_documents_family`, `test_seeded_one_header_for_all_fails` |
| S2 | `fidelity-pilot.sh` | audit topic not made per-document | `test_two_sources_give_two_documents_whole` |
| S3 | `const-paper-pilot.py` | `diff()` ignores the per-document DOC lines | `test_diff_needs_every_document_from_both_seats` |
| S4 | `const-paper-pilot.py` | `docs()` ignores an existing `WRITTEN.md` | `test_written_before_the_change_keeps_one_document` |
| S5 | `fidelity-pilot.sh` | prompts rewritten for a single-source draw too | `test_one_source_is_byte_identical_to_the_old_runner` |
| S6 | `const-paper-pilot.py` | `RESULT.md` without the document count | `test_two_sources_give_two_documents_family` |
| S7 | `fidelity-pilot.sh` | round-2 relay still asks for one DOC line | `test_two_sources_give_two_documents_family` |

## Open follow-ups from review (all class C, none blocking)

- **F1:** two stop paths have no test: the refusal of an empty `DOCS` document, and the stop in `lit`
  when a prompt edit finds no text.
- **F2:** the example header `"## Document D1 header"` leaves out the `(<source>)` part of the
  required format.
- **F3:** in multi-document runs, `score.json` `doc` changes from a string to a dict. Nothing reads it.
- **F4 (for the DRI):** the live action-assurance pilot `reviews/fidelity-pilot-20261030c` was composed
  as 2 documents, with D2 holding `uap.scope_1` from the agent-policy register.

These were not fixed here because the installed runner is in use by a live pilot.
