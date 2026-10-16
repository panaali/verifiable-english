# tarch-cutoff delta

No VE document, checker, relay, diagnostic, limit, verdict or public output changes, and no Lean,
Rust or product Python file changes: `ve/` is untouched. No standing ruling is invoked and no DRI
signature is needed for a user-visible delta, because there is none.

Developer tooling only:

- `tools/test_map_recorder.py`: with `VE_TESTMAP_REQUESTS` set, each recorded process also writes the
  `ve_service` cases its unit sent, beside the map. Unset (every existing caller), the recorder and
  the map it feeds are as before (`tests/test_answer_cutoff.py::test_request_records_leave_the_map_as_it_was`).
- `tools/select_tests.py`: one opt-in flag, `--cutoff RULE`, off by default
  (`::test_the_hook_passes_its_rule_and_is_off_by_default`). <!-- r1 -->
- New: `tools/answer_cutoff.py`, `tools/answer_replay.py`, `tests/test_answer_cutoff.py`, and this
  batch's evidence and scripts under `docs/test-architecture/cutoff/`.
