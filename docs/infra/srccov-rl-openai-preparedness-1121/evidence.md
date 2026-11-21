# Evidence: lines copied from the /tmp logs the REPORT cites

Each block is the tail or a grep of the named log, copied verbatim.

## /tmp/pfwork/cond-main.log
```
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_rule_line_is_in_the_carrier_the_reader_is_shown
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_line_parses_to_the_act_with_no_condition
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_unit_routes_to_the_line[S0171]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_unit_routes_to_the_line[S0172]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_unit_routes_to_the_line[S0173]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_unit_routes_to_the_line[S0186]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_only_these_units_route_to_the_line
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_and_header_quote_the_sentence_whole[S0171]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_and_header_quote_the_sentence_whole[S0172]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_and_header_quote_the_sentence_whole[S0173]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_and_header_quote_the_sentence_whole[S0186]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_quotes_exactly_the_four_sentences
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_text_is_the_source_text_of_the_unit[S0171]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_text_is_the_source_text_of_the_unit[S0172]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_text_is_the_source_text_of_the_unit[S0173]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_text_is_the_source_text_of_the_unit[S0186]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_build_places_exactly_these_units_on_the_block
17 failed in 0.39s
```
## /tmp/pfwork/cond.log
```
17 passed in 1.26s
```
## /tmp/pfwork/seed-S1.log
```
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_rule_line_is_in_the_carrier_the_reader_is_shown
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_line_parses_to_the_act_with_no_condition
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_and_header_quote_the_sentence_whole[S0171]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_and_header_quote_the_sentence_whole[S0172]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_and_header_quote_the_sentence_whole[S0173]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_and_header_quote_the_sentence_whole[S0186]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_quotes_exactly_the_four_sentences
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_build_places_exactly_these_units_on_the_block
8 failed, 9 passed in 0.35s
```
## /tmp/pfwork/seed-S2.log
```
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_unit_routes_to_the_line[S0173]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_only_these_units_route_to_the_line
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_build_places_exactly_these_units_on_the_block
3 failed, 14 passed in 0.81s
```
## /tmp/pfwork/seed-S3.log
```
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_and_header_quote_the_sentence_whole[S0173]
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_quotes_exactly_the_four_sentences
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_legend_text_is_the_source_text_of_the_unit[S0173]
3 failed, 14 passed in 0.82s
```
## /tmp/pfwork/seed-S4.log
```
FAILED tests/test_srccov_rl_openai_preparedness_1121.py::test_the_rule_line_is_in_the_carrier_the_reader_is_shown
1 failed, 16 passed in 0.70s
```
## /tmp/pfwork/rerun.log
```
18 passed in 4.60s
```
## /tmp/pfwork/select.log
```
105:order: failed last time []; changed []; then the rest; --maxfail 5
108:FAILED tests/test_pf_fidelity_fix.py (exit 1): tests/test_pf_fidelity_fix.py::test_regulated_predicates_stay_within_64; log /tmp/ve-select-run-wwtwyxjr/tests__test_pf_fidelity_fix.py.log
124:=========================== short test summary info ============================
125:FAILED tests/test_pf_fidelity_fix.py::test_regulated_predicates_stay_within_64 - assert 63 == 62
128:SHARD 1/3: exit 1 in 675.1 s; 105 units, 104 passed
221:order: failed last time []; changed ['tests/test_srccov_rl_openai_preparedness_1121.py']; then the rest; --maxfail 5
224:SHARD 2/3: exit 0 in 753.6 s; 101 units, 101 passed
317:order: failed last time []; changed []; then the rest; --maxfail 5
320:SHARD 3/3: exit 0 in 1401.5 s; 92 units, 92 passed
321:[gha-select 03:14:11Z] summary: selected tests ran on GitHub Actions (3 shards, run srccov-rl-openai-preparedness-1121-0a84e905-t229278); exit=1; 1573s
```
## /tmp/pfwork/tm.log
```
trust_mutants: 0 definitions, 0 mutants (0 to run), 8 jobs, base cebf4fd24f37
trust_mutants: 0 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 0 ALLOWED, 0 NOT RUN in 13 s
```
## /tmp/pfwork/gc.log
```
37008 collected, 36991 at cebf4fd24f37df2628e43f6fb5e9f352621c36b3; 17 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers
```
## /tmp/pfwork/acct.log (accounting --check)
```
openai-preparedness: 102 blocks, 451 unaccounted words in 68 blocks, 15 blocks with a loss {'1': 17, '3': 1, 'limit 21': 1}, 0 of 122 quotes unanchored
```
## results.json before/after (comparison, items, mutants equal; changed paths)
```
True True True
VAL /metrics/M5/regulated_predicates 62 -> 63
VAL /metrics/M10/rules 91 -> 92
```
## run.py with all 16 drafted blocks (first attempt, before the budget cut)
```
  File ".../usecases/openai-preparedness/run.py", line 737, in persuasion_probe
ve.errors.ResourceLimit: ResourceLimit: regulated predicates
```
## light-lane.py check
```
NOT 331 changed lines outside generated files > 150 (17 files) against cebf4fd2
```
