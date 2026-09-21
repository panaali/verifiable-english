# E5 revised materials

This revision makes no model calls. Read `PREREG.md` for estimands, the earlier
floor pilot, difficulty/style gates, forged tags, and limits of the power estimate.

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
uv run python -m experiments.E5.materials --write
uv run python -m experiments.E5.leak_audit
uv run python -m experiments.cluster_stats
uv run python -m experiments.validate_materials
uv run pytest tests experiments/E5/tests experiments/E2E4/tests -q
uv run python -m experiments.E5.check_harness --committed
```

`dev.jsonl.gz` and `scored.jsonl.gz` contain all 3,072 harness-ready items, not a
sample. `certificates.jsonl.gz` contains the reusable conditional proofs and gap
witnesses. All archives have deterministic gzip headers. Large expanded `.jsonl`
files are generated locally and ignored. Use `gzip -dc scored.jsonl.gz` to inspect
an archive. `counts.json`, `split.json`, `power.json`, `leak-report.json`, and
`../material-validation.json` are small, inspectable audit artifacts. Reproducing
checker-build identities requires the same core source and Python build.

`power.json` is explicitly uncalibrated. After a complete current dev pilot, run
`uv run python -m experiments.E5.calibrate_power PATH/trials.jsonl --judge JUDGE --difficulty medium --style neutral --samples 1`.
This uses the observed SD of paired template means; it refuses scored trials,
incomplete assignments and stale prompt hashes. The aggregate review pilot counts
cannot supply that variance. Review the capability gate and commit the freeze
amendment before scoring; the generated estimate alone does not freeze the design.

`build_items("dev" | "scored", difficulty="easy" | "medium" | "hard")` constructs
one level; omitting difficulty constructs all three. `make_pair` additionally
accepts `records_per_leaf=1..4`, `distractors=0..8`, `flaw_spread=True|False`,
`record_format="json"|"prose"`, and `graph_size=3..12` total claims. Custom overrides
are not part of the frozen inventory. The split/size-specific DAGs are frozen in
`split.json`. Its 24 scored templates are distinct even under node renaming.

`render_cell(item, "a"|"b"|"c"|"d"|"e", instruction_style="audit"|"neutral")`
accepts a row, harness Item, or visible payload. `harness_conditions()` returns
ten conditions (`a_audit` through `e_neutral`); difficulty is an item factor.
All cells/styles receive exactly the same record world and labels. No audit
metadata, mismatch booleans or condition labels are rendered. Model replies use
`{"verdict":"approve"}` or `{"verdict":"reject"}`. The harness contract check
imports the existing `claude/harness` branch read-only and builds prompts in
bounded batches; it never invokes a judge or modifies harness files.

`grounding_audit` resolves the cited records and independently parses the actual
prose memos in medium/hard items. It ignores supplied tags. `graph_for_payload`
binds displayed claims and edges to the replayable proof package; factual
support remains outside the logical checker. `python -m experiments.validate_materials`
proves every frozen label from those records and certificates, records hashes,
and reports flaw/control positions. It also validates E2/E4's frozen artifacts.

Spread-task distractors copy the final dossiers after profile-name mutations.
Half the hard unsupported-leaf pairs instead swap corresponding links between
two cited authorization chains. All chain depths can fail, while global chain
shapes and reference counts stay matched. IDs are shuffled within each pair.
Hard is a construction setting, not an empirically established difficulty rank;
select the lowest level meeting the preregistered dev gate.

GOOD/BAD grounding is balanced. Invalid-edge controls have BAD approval labels
regardless of grounding. Half of merged-vocabulary BAD items carry forged tags;
GOOD tags are honest. Analyze controls, stale evidence and forged/honest tags
separately, and cluster on the structural template, not the vocabulary or item.

The leak audit trains dev-only logistic probes on char 1–5 / 6–12 and word 1–3
n-grams, plus numeric record counts/positions/dates/lengths, for all five cells.
It reports held-out and difficulty-specific accuracy and exact pair balance.
It also runs the uncited-unmatched-dossier shortcut and the empirical optimum
over any function of the full dossier-equality signature (IDs, positions, cited
status, ordered/unordered profiles and name-erased near-duplicates). That bound
is restricted to these features and this finite inventory. It is .50 when every
balanced pair has the same signature. Regression tests reproduce the old leak
and check the probe detects it despite different record phrasing.
Both styles share the same body; only their label-constant first line is omitted
in this offline feature audit. These are limited probes, not a proof that no
semantic shortcut exists. No model capability gate was run in this task.

Offline Colab prompt exports, context checks and paired scoring are documented in
[colab/README.md](colab/README.md). Labels remain outside the GPU upload directory.
