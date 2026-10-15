# DELTA: map-version-notice

User-visible changes of this item (test-architecture re-check, Astra point 6; reviews/test-architecture-2026-10-14.md rank 4 "map freshness"). Standard output, exit codes, return values and what selection selects are unchanged.

| Change | Ruling | Test |
|---|---|---|
| `tools/test_map.py` `find_map` writes one line on stderr for each cached ancestor map nearer than the best so far that does not load: `test_map: skipped map <file> for <base[:10]>: recorded by map format version <N>, this checkout reads version <VERSION> (record a new map: tools/test_map.py record)` for another map format version, `test_map: skipped map <file>: unreadable (<reason>)` for any other load failure. Reaches `select_tests.py`, `repo_map.py` and `test_map.py record/update/show` through `find_map`. | R3 (added explanation, nothing removed or renamed; the text names the true file and both versions) | `tests/test_select_tests.py::test_find_map_names_each_nearer_map_it_skips` |
| `tools/select_tests.py` writes one summary line on stderr when no map was found but ancestor maps of other versions were skipped: `select_tests: no map of format version <VERSION> for <base[:10]>; skipped <n> ancestor map(s) of other versions, so selection has no map (record a new map: tools/test_map.py record)`. Its stdout is byte-identical. | R3 (added explanation only; stdout unchanged) | `tests/test_select_tests.py::test_select_tests_says_why_old_maps_left_it_without_one` |
