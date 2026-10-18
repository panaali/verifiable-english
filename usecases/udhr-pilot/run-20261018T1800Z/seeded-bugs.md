# Seeded bugs, 2026-10-18T1800Z

This run changed no file under `ve/`, `lean/` or `rust/`: it only changed and added files under `usecases/udhr-pilot/`. So there is no changed Lean, Python or Rust behaviour to plant a bug in.
What it changed is translation: the four units u010, u060 (JT-0p) and u042, u043 (ET-0). For each, a fault was planted in the translation, a check that should notice it was run, and the original was restored
(`seeded_bugs_translation.py`; the faulty copies live in a temp directory; results in `seeded-bugs-translation.json`).

| unit | planted fault | check | faulty copy | original |
|---|---|---|---|---|
| u042 | the `not` before constitutes_penal_offence_on is removed | Lean norm-defaults-status witnesses (u042.prohibited) | FAILS: [(['f1'], 'UNDECIDED', ['SETTLED', False]), (['f1'], 'SETTLED no', ['UNDECIDED', None])] | all as expected |
| u042 | the rule's sign is flipped (a finding on account of a non-offence would be REQUIRED, not forbidden) | Lean norm-defaults-status witnesses (u042.prohibited) | FAILS: [(['f1'], 'SETTLED yes', ['SETTLED', False])] | all as expected |
| u043 | the existential reading is given the universal reading's guard | Lean norm-defaults-status witnesses (u043.existential) | FAILS: [(['i1'], 'UNDECIDED', ['SETTLED', False])] | all as expected |
| u043 | heavier_than's arguments are swapped in the universal reading (lighter-than) | Lean norm-defaults-status witnesses (u043.universal) | FAILS: [(['i1'], 'UNDECIDED', ['SETTLED', False]), (['i1'], 'UNDECIDED', ['SETTLED', False])] | all as expected |
| u010 | the two constants of the binary predicate are swapped | the rendering must contain the expected sentence | FAILS: expected sentence absent | all as expected |
| u010 | the unit's meaning names an open term the document does not declare | load_document | refused: invalid meaning status | loads (the part checks) |
| u060 | the unit's meaning names an open term the document does not declare | load_document | refused: invalid meaning status | loads (the part checks) |
| u043 | the recorded separating situation's value flipped, or the two readings made equal | load_document (Lean admits every separation) | a_flipped_value: refused: distinguishing model does not separate readings; b_readings_equal: refused: distinguishing model does not separate readings | loads (part01 checks) |

The committed `--rebuild-reading-ids` tool was also tried on the unchanged parts (`rebuild_command_check.py`, `evidence/rebuild-command.json`): it is not a no-op there and its output does not load. That is a finding about the tool, not a planted bug.
Earlier planted bugs for the pilot are in the 2026-10-14 run's `previous-20261014T1800Z/seeded-bugs.md`; the code they concern is unchanged.
