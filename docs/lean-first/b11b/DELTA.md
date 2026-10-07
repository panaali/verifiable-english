# Lean-first batch 11b: speech caller switch

Base `7345e3ed`; branch `lean-first/b11b`. `ve speech-acts` and `ve.speech_document` now call the Lean W2 `speech-source` route. The previous Python speech decision code is isolated in `tests/frozen_speech/` for differential tests. [LEDGER.md](LEDGER.md) maps every removed decision and successful-output site to its Lean owner.

## Measured result

The numbers in this block are generated and checked by `report.py` from the committed evidence files and the base-to-head source diff.

<!-- BEGIN GENERATED B11B METRICS -->

- Listed production files: **1,368 Python lines deleted**, 176 added; **59 Lean lines added**, 13 deleted.
- Corpus A/B: **94,489 identical records**, including 294 historical pilot checks; zero unlisted differences.
- Differential fuzzer: **15 runs** (CI plus 14 date seeds), 647 base and 647 head new-signature appearances; the signature sets and baseline replays match on every run.
- Speech-only availability: **3** listed changes requiring a DRI signature.
- W2 caller timing: **14** same-host rows (20 calls per side and template); maximum head p95 791.435 ms wall and 246.115 ms child CPU.

<!-- END GENERATED B11B METRICS -->

Evidence: [pre-fix full automated gate](evidence/full-gate.json), [typed corpus comparison](evidence/ab-compare.json), [15-run differential fuzzer](evidence/difffuzz-ab.json), [speech availability pairs](evidence/speech-availability.json), [latency samples](evidence/latency.json), and [seeded failures](evidence/mutants.txt). The final-HEAD gate result is attached to that commit as `refs/notes/ve-gate` (`git notes --ref=refs/notes/ve-gate show HEAD`); a Git note keeps the checked HEAD unchanged after the gate. The corpus recorder ran both commits' own rebuilt Lean route on the same probe, conformance, pilots, readings, discourse, rights, and quantity corpora. The speech switch tests also compare seven accepted W2 templates to the frozen Python caller; the new record kinds are listed separately because the general recorder has no speech corpus.

## Ownership and acceptance

| Item | Tag | Evidence or remaining gate |
|---|---|---|
| W2 decoding, identity, coverage, speech decisions, answer and compliance replay | AGENT | `VE.SpeechActs.Source`, `test_public_speech_projection_matches_frozen`, `test_every_record_kind_is_replayed`, `test_inconsistent_premises_keep_the_checked_certificate` |
| Bound caller and response checks | AGENT | `ve/backends/speech_source.py` uses the shared one-shot launcher and checks request-derived identities, record variants and references, byte totals and classes; `test_every_producer_field_is_required_and_typed` and `test_report_records_are_typed_and_bound_to_the_request` |
| Fenced English text-to-structure | EXTERNAL (English E3) | Python's existing `speech_english` parser supplies a structured fence; Lean checks it and preserves the authored W2 identity. Lean does not yet prove the English derivation. `test_fenced_english_is_checked_after_resolution`. |
| Gap, external compliance and nomination availability | HUMAN (speech-acts DRI) | Three exact base/head rows in `evidence/speech-availability.json`; **signed by the DRI 2026-10-07** (Lean is the one owner of these answers). |
| New Lean CPU on the one-shot W2 caller | HUMAN (speech-acts DRI) | `evidence/latency.json`; **signed by the DRI 2026-10-07**: exception to the 20% rule because the base made no Lean call at all; p95 stays under the 2 s document-check budget. |
| Lean statement review | HUMAN (speech-acts DRI/reviewers) | Deferred as in 11a. `tools/lean_statements.py --check` reports no new or changed statement; the existing W2 theorems remain inventoried. |

The W2 route is one-shot because `speech-source` is not yet a persistent `ve_service` mode. The Python premise search is an untrusted generator. It proposes a model or inconsistency certificate for the already expanded Lean premise list; Lean checks the exact witness before returning a status. If the search has no witness, the report stays `UNKNOWN`. Python's display adds only the generator's search budget or the same certificate Lean accepted.

## Gate 5.1

1. **Suite.** The full gate passed on clean commit `7ea56df0`: 11,465 Python passed, 7 allowed skips, 48 Rust passed, zero failures; Lean build and audit passed. The result is in `evidence/full-gate.json`. The focused speech suite and all 347 relay tests also passed. Earlier assurance, collection and inventory findings were fixed: the generated table and source pins, three new trust classes, the test collection, shared process launcher, stale inventory exception, and transport inventory test. The gate result for the final fix HEAD supersedes this record.
2. **Corpus A/B.** The general recorder's every typed result is identical, including all historical pilots; see generated block. The seven accepted W2 templates match the frozen caller in IDs, rules, legends, warnings, answers, compliance and coverage. The three new availability rows were signed by the DRI in `50b5a23b`.
3. **Deletion ledger.** See `LEDGER.md`; `tools/relay_lint.py` finds no content diagnostic authored by the relayed W2 adapter, and `tools/inventory_lint.py` finds no retained cross-owner body import.
4. **Latency.** The measured W2 p95 is below the 2 s document-check wall budget. The new Lean CPU exceeds the 20% baseline threshold because the frozen caller used no Lean process; the DRI signed the explicit exception in `50b5a23b`.

The fuzzer's baseline does not grow: every sampled signature, answer, and baseline replay matches the base run. The first full gate at `515f86dd` was superseded by the pin and regression fixes; it reported a resource-sensitive Lean service timeout under simultaneous corpus/fuzzer load. The next full gate at `586650ad` found one stale test inventory assertion after the shared transport refactor. The assertion was updated in `72479f0e`; the complete gate passed at `7ea56df0`.

## Integration with reports batch 8

The merge with `ve-integration` keeps both independent Lean routes: reports preflight and response-shape checks, and the speech-source caller. The decoder assurance table and frozen Lean inventory contain both sets of pins. The relay lint covers both reports modules and both speech-source modules. Its import-closure rule excludes `ve.speech_english` explicitly: that experimental English E3 parser still owns text-to-structure, and the speech-source route checks the structured fence it supplies. This is the existing E3 proof gap, not a second speech verdict owner. Mixed `reports@0` and `speech-acts@0` route composition remains outside the current composition profile as specified in `docs/spec/composition.md` (sections 2.9 and 8); neither batch adds such a dispatch.

## Seeded failures

Three temporary faults were applied one at a time in a detached checkout at `515f86dd`, with the unchanged route build, then removed. The raw failing test IDs and exit codes are in `evidence/mutants.txt`.

| Fault | Behavior | Test that failed |
|---|---|---|
| M1 | Substituted `source_id` for the W2 `document_id` | `test_public_speech_projection_matches_frozen[polar]` |
| M2 | Dropped the checked answer rows from the public display | `test_public_speech_projection_matches_frozen[certified]` |
| M3 | Suppressed the current English fence resolution | `test_fenced_english_is_checked_after_resolution` |

All three faults were restored; the detached checkout had no tracked change after the mutations. The final branch contains none of them.
