# E2/E4 Colab DEV bundles

Use the shared [export/scoring contract](../../E5/colab/README.md). E2/E4 retain
their native harness instructions and three named cells; they do not invent an
E5-style medium/neutral/audit factor. Keys end in `|harness`.

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
uv run python experiments/E2E4/colab/export_prompts.py --experiment E4 --split dev --out experiments/E2E4/colab/out/dev/E4
uv run python experiments/E2E4/colab/export_prompts.py --experiment E2 --split dev --out experiments/E2E4/colab/out/dev/E2
```

E4 exports **48 prompts / 16 items**, crossing `checked_countermodel`,
`prose_critique`, `dishonest_critic`. E2 exports **432 prompts / 144 items**,
crossing `direct`, `structured_fol`, `ve`, with all sizes 4/32/256 and both
fixed/growing evidence workloads. `--cells` optionally selects named cells;
the default is all three. No item is removed to meet context.

Only submit the bundle's **`gpu/` child directory**. `labels.jsonl` stays local
in its parent. The models, 400-token PREREG budget, mandatory 8k preflight, input
hashes, revision pinning and failure handling are shared with E5. Each experiment
requires its own PREREG first-line freeze and byte-identical HEAD check for
scored export. Both current drafts refuse scored export.

```sh
uv run python experiments/E2E4/colab/score.py --outputs PATH/TO/E4/out --labels experiments/E2E4/colab/out/dev/E4/labels.jsonl
uv run python experiments/E2E4/colab/score.py --outputs PATH/TO/E2/out --labels experiments/E2E4/colab/out/dev/E2/labels.jsonl
```

E4's primary is checked-countermodel minus prose-critique BAD approval; GOOD
acceptance and dishonest-critic outcomes accompany it. E2 reports each cell,
error family, size, workload and checker visibility, plus paired VE/direct and
VE/FOL size-256 minus size-4 interactions. Sizes are paired within
(template, vocabulary, workload, error visibility) before averaging within
templates. Good acceptance is also reported. No judge or workload pooling.
Native E2/E4 cells are used instead of meaningless a–e contrasts.

The full E2 assignment contains large prompts; the complete job may be refused
by preflight. Proxy counts and the exact-fit limitation are in
[the DEV report](../../E5/colab/dev-export-report.md). A larger context on suitable
hardware or an explicitly amended assignment is an orchestrator decision. The
exporter never silently truncates or drops the size-256 condition.
