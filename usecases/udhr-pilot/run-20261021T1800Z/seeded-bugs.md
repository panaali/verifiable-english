# Seeded bugs, 2026-10-21T0600Z

This run changed no file under `ve/`, `lean/` or `rust/`: it only changed and added files under `usecases/udhr-pilot/`. So there is no changed Lean, Python or Rust behaviour to plant a bug in.
What it changed is translation: the four units the 20261020T1800Z audit rejected (u042, u043 back to UNFORMALISED; u060 and u061 repaired). For the units that now carry content (u061, u060) and the carried JT-0p unit u010, a fault was planted in the translation, a check that should notice it was run, and the original was restored
(`seeded_bugs_translation.py`; the faulty copies live in a temp directory; results in `seeded-bugs-translation.json`). u042 and u043 are UNFORMALISED again, so their rows are gone.

| unit | planted fault | check | faulty copy | restored |
|---|---|---|---|---|
| u061 | the rule's guard is dropped (every thing, not only the family, would be entitled) | Lean norm-defaults-status witnesses (u061.entitlement) | FAILS: [(['c1'], 'SETTLED yes', ['UNDECIDED', None])] | all as expected |
| u061 | the rule's sign is flipped (the entitlement becomes its denial) | Lean norm-defaults-status witnesses (u061.entitlement) | FAILS: [(['c0'], 'SETTLED no', ['SETTLED', True])] | all as expected |
| u010 | the two constants of the binary predicate are swapped | the rendering must contain the expected sentence (or the loader must refuse) | FAILS: expected sentence absent | all as expected |
| u060 | the uniqueness conjunct is dropped (the unit says only that the family is a natural and fundamental group unit) | the rendering must contain the expected sentence (or the loader must refuse) | FAILS: expected sentence absent | all as expected |
| u060 | the uniqueness conjunct names another constant than the family | the rendering must contain the expected sentence (or the loader must refuse) | refused by the loader: UnknownSymbol: Unknown constant 'common_understanding_of_these_rights_and_freedoms' | all as expected |
| u061 | the entitlement is given to another thing than the family (the subject u060 names) | the rendering must contain the expected sentence (or the loader must refuse) | refused by the loader: UnknownSymbol: Unknown constant 'common_understanding_of_these_rights_and_freedoms' | all as expected |
| u010 | the unit's meaning names an open term the document does not declare | load_document | refused: invalid meaning status | loads (the part checks) |
| u060 | the unit's meaning names an open term the document does not declare | load_document | refused: invalid meaning status | loads (the part checks) |
