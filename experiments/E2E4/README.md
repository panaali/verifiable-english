# Revised E2 and E4 materials

No live model calls. Both preregistrations are draft amendments requiring a new
dev-only judge pilot and a frozen run manifest before scoring.

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
uv run python -m experiments.E2E4.generate
uv run python -m experiments.validate_materials
uv run pytest experiments/E2E4/tests -q
```

E2: 432 items, 144 dev / 288 scored; four dev and eight scored shape templates,
fresh vocabularies, sizes 4/32/256, fixed and growing remaining-premise workloads.
Exactly half the error-bearing items concern a false leaf or wrong specification
that the logic checker cannot see. Growing work has 5/33/257 cited leaves. Every
local inference and link is replayed; no monolithic 256-step core proof is claimed.

E4: 136 items, 16 dev / 120 scored. The scored split has 12 quantified/relational
templates × five vocabularies × valid/invalid: 60 of each label. The equivalence
oracle certifies the implication direction or supplies a checked countermodel.
All items cross checked-countermodel, prose-critique and unchecked dishonest-critic
arms. Critique word counts match exactly within items; this is a whitespace-token
proxy, not an exact match for each judge tokenizer.

The `.jsonl.gz` archives are complete frozen materials. E2's large repeated
proof objects are deduplicated under `certificates/<template>.jsonl.gz` (each less
than 1 MB). `materials.load_frozen(split, "E2"|"E4")` hydrates them into the same
harness-ready rows that `build_items` generates. Prompts use no hidden proof/label
fields. The expanded `.jsonl` files are local generated outputs and are ignored.
`generate --pack-existing` only repacks those local files; normal regeneration
and `validate_materials` are the checks to use for a changed generator.

`materials.render_cell` and `materials.as_harness` preserve the shared runner
contract. Structured-FOL renders every formula field, including records and
checker obligations, as FOL keywords. `counts.json`, `splits.json`, and
`../material-validation.json` report inventory and validation details.

Use template-cluster t intervals from `experiments.cluster_stats`, averaging
renamings within templates. Eight/twelve scored templates still limit population
precision. Neither E2 nor E4 freezes a useful-size effect without a dev-based power
amendment. An unrun revised pilot must not be described as meeting its rate gate.
