# E2/E4 mechanism demonstrations

This directory contains deterministic, synthetic materials. It makes no model calls. Run
`python experiments/E2E4/generate.py` to recreate the committed JSONL files. Each row has the
harness shape `{id, label, payload, group, split}`. `materials.build_items(split, experiment)` and
`materials.render_cell(item, cell)` are the stable interfaces; the renderer accepts either a full
row or the visible payload passed by the harness.

E2 fixes one requirement and varies the review workload (4, 32, 256 local deductions). Each
family/size group has an honest control, a checker-visible invalid step, and a checker-invisible
grounding or specification error. The direct arm displays the complete linked sequence without
checker findings. Structured FOL and VE show the root and two remaining leaves, with byte-identical
checker output. Each step depends on the previous step; the size manipulation adds logical
equivalences without adding empirical assumptions. Local deductions replay through `check_argument`;
`validate_e2` audits exact links and correspondence with the displayed statements. The 256-step
condition makes no global core composition claim, avoiding the core's 256-claim limit.

E4 pairs invalid and valid inferences within vocabulary-family groups. The three displays provide
a checked countermodel/checker result, a prose objection, or a critic's unchecked countermodel
assertion. On valid items the last display is deliberately dishonest; the label remains `good`.

The labels are construction-derived: `good` means approve and `bad` means reject. Hidden
`_audit` metadata is stripped by the harness before a condition renderer is called. Splits
hold out entire vocabulary families and are fixed in `splits.json`.

Use harness Experiment IDs `E2E4/E2` and `E2E4/E4`, respectively, so the committed
preregistrations resolve at the correct paths. Pass `splits.json` as `split_file`;
`as_harness(split, experiment)` lazily supplies Item and Condition objects after integration.
E2 contains 36 items (12 honest, 12 invalid-step, 6 false-leaf, 6 wrong-specification),
12 at each size. E4 contains eight items (four valid and four invalid inferences).
Both split evenly into dev and scored, with E4 renaming one structural template.

Run the focused tests with:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run pytest experiments/E2E4/tests
```
