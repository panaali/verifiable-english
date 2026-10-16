# tarch-select delta

No VE document, checker, relay, diagnostic, limit, verdict or public output changes. The batch changes
developer tooling only: `tools/select_tests.py`, `tools/source_graph.py`, `tools/test_map.py` and
`tools/test_map_recorder.py`. The merge train's full live `tools/gate.py` (R2) and the nightly
`tools/gate.py --no-quarantine` (R3) select nothing and read no map, store or build record, so they
run exactly the checks they ran before.

Every row below is a change the batch directive asks for (draft 2 section 3.5 items 2-6 and Astra
re-check point 6, in the DRI's tarch-select prompt of 2026-10-16). None is a VE output, so no standing
ruling R1-R15 applies; the prompt is the item-specific DRI directive.

| # | What a developer sees | Directed by | Test |
|---|---|---|---|
| 1 | `find_map` leaves `tree-*` maps out before its 30-newest window | item 2 | `test_tree_maps_do_not_crowd_commit_maps_out_of_the_window` |
| 2 | `tools/test_map.py fresh --base REV` replaces `find -mmin` freshness checks | item 2 | `test_freshness_is_the_map_selection_would_use` |
| 3 | Version-6 maps load again, through a converter (no service modes: every service user stays selected); a new format version must name a converter or a recorded map | Astra 6 | `test_each_map_format_version_ships_with_a_converter_or_a_recorded_map`, `test_a_version_6_map_converts_and_keeps_every_service_user` |
| 4 | A recorded file may run 4 h (was 1 h); the longest start first. A killed child of a hooked process no longer makes its file opaque; a nested recording hands its records over | item 3 | `test_recording_starts_the_longest_units_first`, `test_a_child_that_records_here_and_left_no_file_ran_nothing`, `test_a_child_records_here_only_if_the_hook_started_this_process`, `test_a_recording_inside_a_recorded_test_hands_over_its_records` |
| 5 | In `ve/` and `ve_experiments/`, a bare directory-name literal names only product directories (an `evidence/` file no longer reaches every unmapped unit) | item 4 | `test_a_product_word_names_only_product_directories`, `test_an_evidence_file_selects_its_readers_not_every_unmapped_unit` |
| 6 | `.gitattributes` is data whose readers include the tests that run git, unless a checkout attribute line changes (then everything, as before) | item 5 | `test_a_merge_driver_edit_of_gitattributes_selects_its_readers_and_git_users`, `test_only_checkout_attribute_edits_of_gitattributes_change_everything` |
| 7 | A shared manifest field selects its whole-manifest readers (the `version` still selects everything); an `authority` edit also selects the registrations of its entries | item 5 | `test_a_shared_manifest_field_selects_its_whole_manifest_readers`, `test_an_authority_change_selects_the_registrations_of_its_entries` |
| 8 | Binary-level cutoff: a test is selected through a Lean executable only if its recorded digest changed between the base and head builds; `tools/test_map.py build-record`; `--run` builds the head first when only its record is missing | item 6 | `test_an_identical_rebuild_selects_no_runner`, `test_a_changed_binary_selects_all_its_runners`, `test_without_both_build_records_every_runner_is_selected`, `test_no_cutoff_when_the_trees_cannot_show_the_change`, `test_a_build_record_needs_a_current_build_of_one_tree`, `test_a_current_build_is_up_to_date_and_traced`, `test_a_run_builds_the_head_for_the_cutoff_when_the_base_build_is_recorded` |

Zero rows wait for a signature.
