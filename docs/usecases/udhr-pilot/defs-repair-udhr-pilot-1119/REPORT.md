# defs-repair-udhr-pilot-1119: REPORT

| row id | KEPT / DROPPED | reason |
|---|---|---|
| defs-udhr-pilot-1-1119 | KEPT | The source has the sentence at `usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md:86` (Article 14(1), unit u051). u052 at line 88 cites it as "This right". The legend `asylum_right_covers_case` (front matter, line 2) carries 7 of its 15 words and lacks "in other countries" and "from persecution": FRAGMENT. |
| defs-udhr-pilot-2-1119 | KEPT | The source has the sentence at `translation.ve.md:34` (Article 2, sentence 1). u033a at `translation.ve.md:54` says "any discrimination in violation of this Declaration". u032, u033a and u033b all have `open: ["discrimination", ...]`. The factors of `open_terms[discrimination]` carry 1 of 39 words: NOT CARRIED. |
| defs-udhr-pilot-3-1119 | KEPT | The source has the sentence at `translation.ve.md:102` (Article 16(3), units u060 and u061). u061 has `open: ["protection_of_the_family"]`. Its factors carry 2 of 21 words: NOT CARRIED. |

**Summary.**
- Status: all 3 P1 rows hold (KEPT). All 3 stay **NOT CARRIED**. The only carrier is the front matter of the sealed, measured run `run-20261010T1400Z`, and no live translation or legend of this document exists anywhere else. Under the task's rule I report them and do not force them in.
- HEAD: see the final commit on `feature/defs-repair-udhr-pilot-1119`. Base: VE main `f5553bc894`. answers_touched: `unknown` for every row (the document has no keyed answers).
- What changed: a saved record `rows.json` and its condition test `tests/test_defs_repair_udhr_pilot_1119.py`. No product code changed, no document text changed and no derived file changed.
- Open: the carry itself. It needs a new live UDHR run, which is a decision for the DRI (see Notes for the DRI). No signature is reserved, and there is no DELTA row.

## Deliverable 0: verification

I checked each row against the in-repo source at main: the body of `translation.ve.md`. METHOD amendment 8 applies: no hash-pinned source exists. I also checked each row against the text the reader is shown, which is the same file's front matter. `git diff --stat 3d6b459df4 main -- usecases/udhr-pilot` is empty, so the audit's pin and main agree. Commands and their output:
- `grep -n` for the three sentences gives lines 34, 86 and 102 (above). The unit spans were read from the front matter: u051 = Article 14(1), u052 = 14(2), u060 + u061 = 16(3), u033a = Article 7 sentence 2.
- `carried.py` was run on the carrier runs (the description with its citation stripped, and the factors) and gave `7/15`, `1/39` and `2/21` words. Run on the whole front matter it gave `13/15`, `8/39` and `3/21`. The 13/15 hit is the `why` text of a reading in rs_u051. A reading set is not a carrier (amendment 7), and rs_u051 belongs to a different unit.
- Row 1's audit quote reads `Article 14(1): "…"`. The prefix and the quotation marks are audit prose. The record holds only the source sentence, to the byte.
- Row 2: u032 (Article 7 sentence 1, "without any discrimination") is tied to Article 2 less directly than u033a and u033b ("in violation of this Declaration"). I kept the row because all three units share the one carrier.
- Row 3: the second half of the sentence is u061's own text. I kept the full sentence anyway, as amendment 3 requires (complete span, sentence boundary to sentence boundary).

## Deliverable 1: why NOT CARRIED (sealed run)

`translation.ve.md` is the recorded output of a run. It is not a live document:
- `migrate.py:50-51` reads its input from `frozen-run.json` and pins that input by SHA-256 (`fe165c3c…`). The test checks the pin: `test_a_row_left_not_carried_for_the_seal_names_a_sealed_measured_run`.
- `tests/test_readings_rd5_udhr.py:77-81` (`test_the_migration_reproduces_the_committed_document`) requires the committed file to equal the migration's output byte for byte. A legend appended in place breaks that test.
- `metrics.json` `after.document_bytes` = 374535 = `wc -c translation.ve.md`. The run's `reports/after.*`, `SUMMARY.md` ("migrated by `migrate.py` and measured by `measure.py` at commit `ae7fa229`") and `docs/premise-scale/evidence/ab-documents.json:121` (sha256 `5151b58b…`) all describe exactly these bytes.
- There is no other place to carry them. `usecases/udhr-pilot/` holds only this run (`ls`). The body is the source, and reading sets are not carriers (amendment 7). `udhr-part07.ve.md` belongs to question-answering, which is out of scope.
- What a carry would take: rewriting this run in place is ruled out (DRI decision 20261119: "a sealed run is never rewritten in place"). The other route is a new run, migrated and then re-measured, and re-measuring needs a whole-UDHR `ve document check`, which L70 forbids.

## Deliverables 2 and 3

- 2: I regenerated nothing, because no source of a derived file changed. `uv run python tools/regen_generated.py --check` returned 0 ("checked 41 entries").
- 3: `tests/test_defs_repair_udhr_pilot_1119.py`, 11 tests, reads only saved files. It checks five things:
  - the record holds exactly the audit's 3 P1 ids;
  - each quote occurs once in the source body, byte for byte, on its line, from one sentence boundary to the next;
  - each row's rules use its term;
  - a row recorded CARRIED has the whole normalised sentence in one legend run of its carrier, and a row recorded NOT CARRIED has it in none;
  - the seal the NOT CARRIED rows rely on still holds.
- Results: with `rows.json` removed (the tree as it is on main) the run gives `11 failed in 1.26s`. At HEAD it gives `11 passed in 2.10s`. The selected run was `mac-pytest.sh --select` at 0bc2f390: 29 units, 0 failed, exit 0, and this file ran in it (`exit 0 in 4.9 s`).

## Seeded bugs

Each bug was planted alone. I ran `uv run pytest -q tests/test_defs_repair_udhr_pilot_1119.py`, then restored the file with `git checkout`. `git status` was clean afterwards.

| # | planted in | bug | failing test |
|---|---|---|---|
| S1 | `usecases/udhr-pilot/run-20261010T1400Z/translation.ve.md` | Article 14(1) appended in place to the `asylum_right_covers_case` legend (a rewrite of the sealed run) | `test_a_rows_carry_verdict_matches_its_carrier[defs-udhr-pilot-1-1119]`, `test_a_row_left_not_carried_for_the_seal_names_a_sealed_measured_run` |
| S2 | `docs/usecases/udhr-pilot/defs-repair-udhr-pilot-1119/rows.json` | row 2's quote has "colour" changed to "color" | `test_a_kept_rows_definition_is_the_source_sentence_byte_for_byte[defs-udhr-pilot-2-1119]` |
| S3 | same | row 3 deleted | `test_the_record_holds_exactly_the_audits_p1_rows` (plus 3 more) |
| S4 | same | row 3's rule changed to u060 (a rule that does not use the term) | `test_a_rows_rules_use_its_term[defs-udhr-pilot-3-1119]` |
| S5 | same | row 3's quote cut down to one clause | `test_a_kept_rows_definition_is_the_source_sentence_byte_for_byte[defs-udhr-pilot-3-1119]` |

No product code changed in Lean, Python or Rust, so no seeded bug per product language applies.

## Trust, DELTA, size

- Trust: `uv run python tools/trust_map.py --check` gave "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0; PASS". No allowance is recorded and there is no FOLLOW-UPS row.
- DELTA: none. Nothing the reader is shown changed, so there is no DELTA.md.
- Light lane: `light-lane.py check` printed `NOT 166 changed lines outside generated files > 150`. I did not run a trust_mutants sweep. This item changes no trusted file and no product code (trust +0), and checklist 13a asks for a sweep only on trusted Lean growth.
- SIZE: 0 product, 120 tests, 46 + this report's lines other hand-written lines.
- Pilot bytes the item is expected to move: 0. No unit or legend changed.
- Not run: the full gate (the chain runs it on the final HEAD), a Lean build (no Lean changed) and a trust_mutants sweep (see above).

## Spec re-read

- Task deliverable 1 ("A carrier inside a frozen or sealed run directory … report the row as NOT CARRIED with the reason") against the task text and `reviews/dri-decisions-20261119-defs-repair.md` item 1.
- METHOD amendment 3 (complete span) against the record's quotes and the sentence-boundary assertion.
- Amendment 7 (reading sets are not carriers) against the 13/15 hit in rs_u051.
- Amendment 8 (in-repo source) against the use of the body of `translation.ve.md`.

## Notes for the DRI

- The three definitions can be carried only in a new live UDHR document: a new run directory, or a re-migration with the appends, together with a recorded re-measurement. Either way the run's `metrics.json`, `reports/` and SUMMARY stay true of the run they describe. Whole-UDHR checks are refused under L70, so the re-measurement needs part documents or a ruling on how to measure. The open terms have no `description` field, so a carry there means a new factor string or a schema field. A schema field is a decoder change and is out of scope for a LANGUAGE-only row.
- D5, D6 and D7 (udhr-pilot.md notes) stay with the audit. I added no candidates.

FOLLOW-UP: defs-repair-udhr-pilot-1119b carry the three UDHR P1 definitions in a new live UDHR run (the current run is sealed and measured)

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relay or Lean answer was added.
2. Deliverables built, no rule broken: PASS. Deliverable 0 is the table. Deliverable 1 is reported NOT CARRIED under the task's own rule. Deliverable 2: `regen_generated.py --check` rc 0. Deliverable 3: `tests/test_defs_repair_udhr_pilot_1119.py`.
3. Tests can fail: PASS. Seeded bugs S1-S5, and 11 failures with the record absent.
4. Python, Lean and Rust agree: N.A. No product code changed.
5. R8 binding: N.A. No relay. The record binds itself to the audit's ids (`test_the_record_holds_exactly_the_audits_p1_rows`).
6. Gate evidence matches the final HEAD: PASS for the selected run at 0bc2f390. Only this report was committed after it. The chain runs the full gate.
7. No unsigned item: PASS. No DELTA row and no reserved signature.
8. Every user-visible change is in DELTA: N.A. No user-visible change.
9. Test selection finds the tests: PASS. The selected run included `tests/test_defs_repair_udhr_pilot_1119.py`.
10. Lean statements and proofs: N.A. No Lean.
11. Budgets fail closed: N.A. No evaluator.
12. No CPU or memory regression: N.A. The tests read saved files in about 2 s.
13. Test-removed trailers: N.A. No test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. The carry check runs both ways (`test_a_rows_carry_verdict_matches_its_carrier`: S1 makes NOT CARRIED false). Each claim cites its command. The spec re-read is listed above.
15. No overclaim (each "no" or "none" here cites `trust_map --check`, `regen --check` or the numstat). No silent cut: the carry is reported per the task's rule and named as a FOLLOW-UP. Every new check can fail: S1-S5. Limits: N.A.
