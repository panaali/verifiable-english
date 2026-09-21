# E5 materials

No model calls. From the repository root:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
uv run python -m experiments.E5.materials --write
uv run python -m experiments.E5.leak_audit
uv run pytest experiments/E5/tests -q
```

`materials.build_items("dev" | "scored")` returns dictionaries accepted by
`ve_experiments.runner.Item(**row)`. `render_cell(item, "a" | "b" | "c" | "d" | "e")`
accepts a full row, a harness Item, or the visible payload passed to a Condition.
`harness_items` and `harness_conditions` lazily import the other worker's harness;
this directory does not include or modify it. Set Experiment id `E5`, crossed
assignment, and split_file to `experiments/E5/split.json`. A judge must return
`{"verdict":"approve"}` or `{"verdict":"reject"}`. Labels/IDs/audit metadata are
not rendered. The renderer explicitly selects fields rather than serializing payloads.

`dev.jsonl` / `scored.jsonl` are the frozen, harness-ready files. `split.json`
records groups, templates and vocabulary families. Generation uses this assignment
without rewriting it. `certificates.jsonl` stores each logical graph's replayable
tableau certificates or countermodels once; `graph_for_payload` attaches the
item's records as Evidence metadata and runs against the same logical structure.
`check_argument(..., search=False)` certifies all positive edges and checks every
gap witness. `_audit` stores exact checker/graph identities, family and strata.
The E5 tags deliberately do not alter `ve/` vocabulary identity.

Grounding truth is defined by the records' structured fields and the documented
closed support rule, not by a model. The independent checker certifies conditional
logic only. Every leaf remains an unassessed assumption. The evidence record
validity interval is substantive synthetic data, not the host machine's date.

The 192 primary items are balanced 96/96 for approval. The 192 invalid-edge
controls balance grounding GOOD/BAD, but all have approval label `bad` because
an invalid argument cannot be approved. Select `_audit.stratum == "primary"`
for the preregistered contrast; never mistake grounding GOOD for overall approval.
For analysis, join `template` from `_audit` into the harness's trial rows and use
`cluster="template"`, rather than the finer vocabulary group. Both grouping
keys are frozen within one split. No data record supplies its audit fields to a judge.

Every matched GOOD/BAD pair has identical character count and exact unigram
multiset in cell a. The leak audit fits a dev unigram logistic classifier and
checks held-out accuracy plus an upper bound for any classifier using unigram
counts or lengths/keyword counts. These tests cannot exclude semantic relational
heuristics, which should solve these transparent synthetic cases. Eight scored
templates are insufficient to promise narrow intervals; this is material and
preregistration preparation, not an experiment result.
