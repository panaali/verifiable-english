# VE manuscript handoff

This is an incomplete research draft on `paper/draft`, based on implementation
commit `14311840057b38e6554f35e7f5ff95c8e3c16145`. The Claude-side author created
the scaffold. At the user's request, GPT-6 Astra continued the draft after that
author exhausted quota. The user requested a subsequent Claude-side claim audit;
that manuscript audit has not yet occurred. Work in this drafting pass was serial.
No model experiments, training, pushes, or integration merges were performed.

The draft contains the abstract, all requested numbered sections, references,
and conspicuous RESULT markers. It distinguishes existing development evidence
from planned analyses and missing scored outcomes. It does not infer experiment
status from a moving branch tip. External experiments may have progressed after
the snapshots pinned in `sources/manifest.json`.

## Build and inspect

From `paper/`:

```sh
make html
make pdf
make placeholders
```

`make` defaults to the verified standalone HTML target. Both HTML and PDF passed
in this checkout. The PDF build successfully downloaded Tectonic's bundle into
the workspace cache. If bundle access fails elsewhere, `make html` remains the
fallback; it does not require TeX. HTML embeds its SVG figures and CSS and uses
MathML. PDF uses the corresponding vector PDF figures.

The Makefile enforces serial targets and exports:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache
export XDG_CACHE_HOME="$PWD/.cache"
export TECTONIC_CACHE_DIR="$PWD/.cache/tectonic"
export MPLCONFIGDIR="$PWD/.cache/matplotlib"
```

`.cache/` is ignored. Builds require `uv`, Python compatible with the repository,
Pandoc, and Matplotlib (pinned to 3.11.2 in the Makefile). PDF additionally requires
Tectonic and `pdftotext` for verification. Page inspection uses Poppler's
`pdfinfo` and `pdftoppm`. No network is needed for source data; the initial tool
or TeX dependency fetch may need network access.

Outputs, intentionally ignored by Git:

- `build/paper.html`: standalone manuscript.
- `build/paper.pdf`: typeset manuscript.
- `build/paper.md`: assembled Markdown, including source comments.
- `build/draft-status.json`: word-count methods and complete RESULT inventory.

The verified draft has **21 PDF pages** and **8,735 rendered words**, including tables, captions and
references but excluding metadata. The counting command is Pandoc plain-text
output split on whitespace, implemented by `verify.py`; Markdown-token counts
are recorded separately. Use `pdfinfo build/paper.pdf` for the current page count.
The final PDF was rasterized and every page inspected; selected dense tables,
math, worked views, and figures were also inspected at higher resolution.
Tables are kept on one page by `keep-tables.lua`; reconsider that filter if later
results introduce a table taller than a page. Pandoc/Tectonic reports its
absolute temporary image paths as reproducibility warnings; the manuscript uses
relative paths and the generated figures regenerate deterministically. The final
PDF itself includes build-time metadata and is not asserted byte-reproducible.

Verification commands used:

```sh
make html pdf
python3 verify.py --html --pdf
pdfinfo build/paper.pdf
pdftoppm -scale-to 1500 -png build/paper.pdf build/final
```

`verify.py` checks snapshot hashes, exact repository URL provenance, ASCII body
text, section and placeholder inventories, embedded HTML assets, and PDF text
extraction. The generators check the recorded counts, recompute Wilson intervals
and benchmark medians, invoke the actual five renderers, and verify strict-view
round trip and identical legends. A final sequential regeneration reproduced all committed
generated tables, data files and figure assets byte-for-byte. These checks do not audit every scientific
claim. The full Lean, Rust, and Python implementation test suites were not rerun
for this manuscript-only change; conformance outcomes are reported from the
committed development records, not described as fresh runs.

## Files and numerical provenance

| Files | Purpose / regeneration |
|---|---|
| `sections/00-abstract.md` through `sections/12-references.md` | Abstract, numbered sections, and reference include. Every quantitative block names its source in an HTML comment. |
| `references.md`, `reference-audit.json` | Exact URLs from repository reviews or the supplied capability brief, with verification status. |
| `sources/manifest.json`, other `sources/` records | Pinned branch snapshots, hashes, supplied reviewer limits, calibration summaries, and selected production-log entries. |
| `figures/gen_e0_tables.py` | Rater counts, Wilson intervals, agreement, proposed corrections, missing constructs, profile projections, and closure witness table. |
| `figures/gen_implementation_tables.py` | Renderer-generated worked example and legend, conformance sizes, recorded certificate/fuzz outcomes, raw-sample Rust medians. |
| `figures/gen_judge_ladder.py` | Local, Colab, and hosted DEV-PILOT tables and plot. |
| `figures/gen_system.py`, `sources/system-diagram.json` | Interface schematic; boxes do not imply verified implementation. |
| `generated/`, `figures/*.{pdf,svg,png}` | Committed generated outputs. `make generate` reproduces them from committed inputs without model calls. |
| `Makefile`, `build.py`, `verify.py`, `*.lua`, `style.css`, `metadata.yaml` | Serial generation, assembly, rendering, layout, and verification. |

All numerical source comments survive in `build/paper.md`. E0 and ladder source
branches are unnecessary for subsequent builds because their exact records are
committed under `sources/`. `manifest.json` retains original revisions and paths.
For manual methods parameters and process counts, the source comment points to
the frozen record; inspect with `git show HEAD:paper/sources/NAME` or the named
repository file. `make generate` is the reproduction command for derived tables.
Implementation corpus and timing inputs are the committed `conformance/*.json`,
`rust/benchmark-results.json`, and `experiments/E0/closure_witnesses/report.json`.
Their original execution commands and limitations remain in the adjacent READMEs
and reports. Reproducing a table is distinct from rerunning an experiment.

The external Colab and orchestrator records were first committed with this paper.
They are attributed supplied observations, not independent replications. The
process-log extract contains the complete selected entries needed for the six
review examples; it does not copy unrelated access details from the full log.
Older reviewer notes are historical: later committed implementation documents
resolve some of their earlier restrictions. The draft uses the latest scope
supported at the pinned implementation base, and does not import later Lean or
experiment milestones from other worktrees.

## RESULT inventory

| Marker | Missing evidence |
|---|---|
| `RESULT-ABSTRACT` | Audited scored E1/E5 effects and uncertainty, including null or harmful effects. |
| `RESULT-CONTRIBUTIONS` | Any scored experimental contribution. |
| `RESULT-E1-FREEZE` | Final preregistration, judges, assignment, validation attrition, power and deviations. |
| `RESULT-E1` | Scored paired false approval, honest acceptance and intervals. |
| `RESULT-E1B` | Model-satisfaction study; not yet run in the frozen evidence. |
| `RESULT-E5-FREEZE` | Revised calibration, power, selection, leak audit and scoring amendment. |
| `RESULT-E5` | Scored badge/panel effects, failures, forged tags and stale-evidence breakdowns. |
| `RESULT-E2` | Final design and scored mechanism/cost study; not yet run in the frozen evidence. |
| `RESULT-E4` | Final design and scored critique study; not yet run in the frozen evidence. |
| `RESULT-T-GATE` | Training competence, selection probe, paired pilot and throughput; not yet run. |
| `RESULT-T-TRAINING` | Training, cross-scoring, transfer and rollout audits; not yet run. |

## Questions and claim boundaries for the editor

- **E1 rules are internally unresolved.** Its point-estimate-plus-significance
  benefit rule conflicts with PLAN's useful-effect interval rule. Its validation
  UNKNOWN exclusions need explicit full-denominator attrition and bounds. The
  manuscript records these conflicts; it does not silently amend a preregistration.
- **E5 revision 3 is not calibrated or powered in this evidence.** The useful-size
  target is provisional and the power artifact is a placeholder. An earlier
  pilot is not evidence that the revised structural-shortcut materials pass the
  gate. The 0.50 structural feature bound is only the finite audited feature class.
- **E0 adjudication remains proposed.** Keep frozen labels, corrected witnesses,
  and convention changes separate. Wilson intervals do not measure rater truth;
  profile-extension totals are projections, not measured coverage gains.
- **The Lean claims concern reference definitions.** Base printer/parser round
  trip is not independent grammar correctness. Graph soundness is not verified
  Python graph composition or a graph-wire decoder. Common-carrier/disjoint-sort
  correspondence remains an external interpretation assumption. The pinned
  closure milestone does not prove arbitrary extended surface round trips or
  closure certificate replay. Do not borrow later branch results without a new
  evidence freeze.
- **Rust timings and corpus counts are development evidence.** The approximate
  thirtyfold claim concerns the larger measured kernels; public API ratios are
  not kernel ratios. Corpora overlap, schema-generated proofs are correlated,
  and most forgeries mutate a simple base.
- **One reference was not freshly verifiable.** The ACE chapter DOI fetch failed.
  It is explicitly marked in the references. Other cited links were inspected
  during drafting, but the mathematics announcements were not audited through
  their proof repositories. They motivate statement review, not VE efficacy.
- **Model and process claims have narrow scope.** The primary-band open judges
  come from one family. Local and Colab settings differ. No human subjects were
  studied. Cross-family review caught the listed defects but supplies no estimate
  of remaining defects, independence, or human-review equivalence.

No changes to `PLAN.md` were made. Proposed plan action: resolve and freeze the
E1 rules and the revised E5 calibration/power decisions before interpreting any
scored contrast; keep Phase T marked planned until its gates are actually run.
