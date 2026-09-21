# VE manuscript handoff: v1

This manuscript is on `paper/v1`, revised by GPT-6 Astra after merging the
current integration work. `sources/manifest.json` pins the implementation base
and every imported source. The original Claude scaffold and GPT draft history
remain in Git. A subsequent Claude-side manuscript claim audit is still pending.
This revision was serial: no experiment calls, training, test suites, pushes,
or integration merges were performed by the drafting author.

E1 v5 and E4 revision 2 are frozen before scored judging. The supplied run log
ends with E1 scoring started and E4 queued; no scored outcomes are imported here.
E5 provides materials and pilots only, with scoring explicitly not executed.
E2 was not run after context preflight failed. The abstract and contributions
retain outcome placeholders rather than infer efficacy from development data.

## Build and inspect

From `paper/`:

```sh
XDG_CACHE_HOME="$PWD/.cache" TECTONIC_CACHE_DIR="$PWD/.cache/tectonic" make html pdf
make placeholders
pdfinfo build/paper.pdf
```

The Makefile enforces serial targets and sets workspace-local XDG, Tectonic,
and Matplotlib caches, plus `/private/tmp/ve-uv-cache`. It uses Pandoc, Tectonic,
Poppler, and Matplotlib 3.11.2 through `uv`. It regenerates tables from committed
records, not live model calls. First-time dependency downloads may need network.
The PDF has **25 pages**; the current rendered word count and marker inventory
are in `build/draft-status.json`. HTML and PDF verification checks source hashes,
citation provenance, section/marker inventories, embedded assets, and PDF text.
The final PDF pages were rasterized for layout review, including dense tables.
No implementation test suite was run. Generated tables report recorded outcomes,
not fresh conformance or benchmark runs.

Ignored build outputs are `build/paper.html`, `build/paper.pdf`, `build/paper.md`,
and `build/draft-status.json`. Tables use `keep-tables.lua` to stay on one page;
recheck layout when replacing RESULT cells with longer values. Tectonic may warn
about Pandoc's absolute temporary image paths; the manuscript uses relative paths.
The PDF includes build-time metadata and is not claimed byte-reproducible.

## Changed content and numerical provenance

- `sections/00`, `01`, `03`, `04`, `05`, `07`, `09`, `10`, `11`: abstract,
  contributions, compact legend, closure replay and Rust boundaries, experiments,
  limitations, process/cost disclosure, and future work.
- `sources/`: frozen E1 preregistration and judges, both Qwen DEV reports, frozen
  E4 preregistration and selected dev metrics, deferred E5 materials/pilots,
  fourth Lean review, post-v0 run log, operational outage entry, and approximate
  compute accounting supplied in the user handoff. Historical draft snapshots
  remain for provenance but no longer control the manuscript's current claims.
- `figures/gen_implementation_tables.py`, `generated/conformance-table.md`:
  include Rust closure comparison and distinguish base search counts from
  combined base/closure certificate totals.
- `verify.py`: explicit eight-marker inventory; `sources/manifest.json`:
  pinned revisions and hashes; source/handoff READMEs: current status.

All quantitative blocks name committed sources in HTML comments, preserved in
`build/paper.md`. External pilot and orchestration records are supplied
observations, not independent replications. Access-configuration details are
omitted from the new log excerpt. Builds never read moving branches.

## Remaining placeholders and result handoff

| Marker | Missing evidence |
|---|---|
| `RESULT-ABSTRACT` | Audited scored E1/E4 outcomes and uncertainty. |
| `RESULT-CONTRIBUTIONS` | Scored findings within the per-judge and mechanism limits. |
| `RESULT-E1` | Cell counts, failures, truncations, two co-primary decisions, HA constraints, bootstrap sensitivities, exploratory contrasts and descriptive covariates. |
| `RESULT-E1B` | Correct counts, template accuracy, 95% intervals and failures by judge/view. |
| `RESULT-E4` | Cell counts, paired 95% intervals, HA constraint, dishonest-critic acceptance and descriptive interpretation. |
| `RESULT-COST` | Completed scored wall time, units, actual tokens and any metered hosted cost. |
| `RESULT-T-GATE` | Training competence, selection probe, pilot and throughput; not run. |
| `RESULT-T-TRAINING` | Main training, cross-scoring, transfer and rollout audits; not run. |

Bare RESULT cells in Section 7 belong to the surrounding named marker. Fixed
assignment denominators are design counts, not completed calls. Populate E1 and
E1b from `experiments/E1/RESULTS.md` after complete import; populate E4 from its
scored `score-summary.json` and paired template analysis. Preserve 97.5% intervals
for 32B co-primary effects/constraints, 95% exploratory intervals, and the exact
condition-specific decision rule. Never promote 14B or optional hosted rows to
primary after observing scored results. Add actual backend revisions, deviations,
attack-family/direction breakdowns, and the empty-sort sensitivity from the
completed record. Update source snapshots/hashes, rebuild, and inspect layout.

E1 freeze, E5 freeze/results, and E2 result placeholders were retired because
their status is now known. E5 and E2 require new work before they can have scored
results; they are not outstanding outputs of the current run.

## Claim boundaries

Lean now has 200 audited named theorems, including helpers. Extended certificate
acceptance implies entailment over all admissible structures; the v0 theorem
is unchanged and the new v0 corollary uses conservativity. No completeness,
general induction, verified Python/JSON, extended graph theorem, or general
extended surface round trip is claimed. Rust includes closure with 3,000/3,000
recorded fuzz agreement, but has no refinement proof or certificate replay.
E1 has one primary judge from one family, with prompt-sensitive gate placement;
its final explanation helped on dev. E4 failed its original gate and is only a
mechanism demonstration. E0 rater disagreements and proposed corrections remain
separate from ground truth. There are no human-participant results. Cross-family
review caught concrete defects but does not quantify remaining errors.
