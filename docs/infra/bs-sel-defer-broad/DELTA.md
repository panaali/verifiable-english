# bs-sel-defer-broad delta

User-visible output delta of VE: **none**. The change is to `tools/select_tests.py`, the test selector, and
only when the new opt-in option `--defer-broad` is passed. No VE command, verdict, diagnostic or response changes.
Without the option the selector's plan is the same as before, except that each `deferred` row of `--defer-heavy`
now also carries `"class": "weak"` (`tests/test_select_defer.py::test_a_heavy_file_selected_only_for_weak_reasons_is_deferred`).
No standing ruling or DRI signature is needed.
