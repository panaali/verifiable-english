# Evidence excerpts (srccov-openai-preparedness-1119): the lines each REPORT claim cites, copied from the /tmp logs

## condition test on main's PF files (/tmp/pf-cond-main.log)
196 failed, 1 passed in 3.27s

## condition test + the two reran selected failures at HEAD (/tmp/pf-rerun.log)
200 passed in 3.28s

## six PF tests of test_safetyfw_usecases.py (/tmp/pf-rerun2.log)
6 passed, 99 deselected in 31.11s

## seeded bug S1-legend (/tmp/seed-S1-legend.log)
1 failed, 196 passed in 1.60s
FAILED tests/test_srccov_openai_preparedness_1119.py::test_the_legend_quotes_the_source_passage_whole[S0145-reached-The determin]

## seeded bug S2-constants (/tmp/seed-S2-constants.log)
28 failed, 169 passed in 1.64s
FAILED tests/test_srccov_openai_preparedness_1119.py::test_the_legend_quotes_the_source_passage_whole[S0065-biological_and_chemical_high-The model ca]
FAILED tests/test_srccov_openai_preparedness_1119.py::test_the_legend_quotes_the_source_passage_whole[S0066-biological_and_chemical_high-Significantl]

## seeded bug S3-record (/tmp/seed-S3-record.log)
11 failed, 186 passed in 1.34s
FAILED tests/test_srccov_openai_preparedness_1119.py::test_the_unit_is_recorded_as_labelled_exposition[S0209]
FAILED tests/test_srccov_openai_preparedness_1119.py::test_the_unit_is_recorded_as_labelled_exposition[S0211]

## seeded bug S4-placement (/tmp/seed-S4-placement.log)
2 failed, 195 passed in 1.22s
FAILED tests/test_srccov_openai_preparedness_1119.py::test_the_unit_is_recorded_as_labelled_exposition[S0211]
FAILED tests/test_srccov_openai_preparedness_1119.py::test_the_records_are_the_label_placements_of_the_build

## run.py (/tmp/pf-run.log)
236 / 239 (1931.9 s)
results.json paths changed: /metrics/M3/bytes_by_kind/exposition, /metrics/M3/bytes_by_kind/unformalised, /metrics/M3/bytes_by_status/LABELLED, /metrics/M3/bytes_by_status/UNFORMALISED; comparison equal: True mutants equal: True

## trust mutants (/tmp/pf-tm.log)
trust_mutants: 0 definitions, 0 mutants (0 to run), 8 jobs, base 09bea0972dee
trust_mutants: 0 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 0 ALLOWED, 0 NOT RUN in 21 s

## trust mutants plan (/tmp/pf-tm-plan.log)
{"base": "09bea0972dee7c3738557d6799a754b43dd782b1", "definitions": 0, "mutants": 0, "to_run": 0, "not_run": 0}

## light lane
NOT 993 changed lines outside generated files > 150 (14 files) against 09bea097

## selected run (/tmp/pf-select.log)
[mac-pytest 10:22:06Z] CLOUD2_RUNNER: trying the remote hosts before the VM (REMOTE_FIRST: remote hosts before the test pools and the Mac)
FAILED tests/test_english_lean_lexicon.py (exit 1): tests/test_english_lean_lexicon.py::test_every_corpus_environment_has_a_valid_selected_lexicon; log /tmp/ve-select-run-pq1cimrb/tests__test_english_
FAILED tests/test_fidmech_records.py (exit 1): tests/test_fidmech_records.py::test_every_third_value_spelling_in_an_adapted_documents_sources_is_recognised_by_the_kill_rule; log /tmp/ve-select-run-pq1
recorded 378 units for tree b32d75be57; 288 others left to the static graph until they run; 2 failed
[mac-pytest 11:37:18Z] summary: ran on ve-cloud-2 (x86_64) instead of the VM because: REMOTE_FIRST: remote hosts before the test pools and the Mac; exit=1; 4512s

## accounting report (/tmp/pf-acc2.log; main's value from `git diff` of docs/usecases/safetyfw/openai-preparedness/accounting.json)
main: "unaccounted_words": 509, "blocks_with_unaccounted_words": 70
openai-preparedness: 101 blocks, 468 unaccounted words in 69 blocks, 15 blocks with a loss {'1': 17, '3': 1, 'limit 21': 1}, 0 of 118 quotes unanchored

## regen check (/tmp/pf-regen2.log)
regen_generated: checked 41 entries

## lexicon report (/tmp/pf-lex2.log)
{"valid": 43, "invalid": 0, "failures_by_condition": {}}
