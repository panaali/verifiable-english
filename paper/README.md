# VE manuscript handoff: scored results

This manuscript is on `paper/v1`, drafted by GPT-6 Astra. Scored E1/E1b and E4
results now replace the abstract, contribution, experiment, and cost placeholders.
The headline is a negative E1 primary conclusion and limited E4 checking benefits,
with exploratory renderer contrasts kept separate. A qualitative policy use case
and prospective replication/external-baseline comparisons are included.
A subsequent Claude-side manuscript claim audit is pending.

## Build and inspect

From `paper/`:

```sh
XDG_CACHE_HOME="$PWD/.cache" TECTONIC_CACHE_DIR="$PWD/.cache/tectonic" make html pdf
make placeholders
pdfinfo build/paper.pdf
```

The build succeeds for HTML and PDF, with **27 pages** and 13,284 rendered words.
Only the existing offline artifact generation and build verification were run;
no test suites, model calls, training, experiment reruns, or pushes were performed.
The Makefile uses workspace-local XDG, Tectonic, and Matplotlib caches and
`/private/tmp/ve-uv-cache`. Ignored outputs are `build/paper.html`,
`build/paper.pdf`, `build/paper.md`, and `build/draft-status.json`. Tectonic may
warn about temporary absolute image paths; the PDF includes build metadata and
is not claimed byte-reproducible. Rendered pages were inspected for layout.

## Frozen evidence

`sources/manifest.json` pins every copied source and its SHA-256. E1 results
come from `cb2b7ff`, its preregistration from `555b3ae`, and E4's preregistration
from `cbc6a80`. The supplied external E4 score JSON/table and selected runner
log entries were first committed as snapshots before manuscript authoring.
Use-case snapshots pin `usecases/main`; one Sonnet agent produced that pair,
without cross-review. Source comments locate each quantitative block.
The build never reads moving branches or makes model calls.

E1's 32B P1 is inconclusive; P2 refutes a 0.05 reduction without establishing
harm; the combined claim is inconclusive and not supported. E4's 14B result
satisfies its negative-upper-bound and HA-noninferiority rule; -0.22 is only
a planning reference. The 7B prose floor does not establish protection, while
its secondary HA contrast shows acceptance recovery. The snapshots preserve
historical interpretations even when the manuscript qualifies them, including
the use-case report's overstatement of bounded NotFound as entailment proof.

## Remaining placeholders and evidence gaps

Only `RESULT-T-GATE` and `RESULT-T-TRAINING` remain; training was not run.
E5 has materials and pilots only. E2 was not run after context preflight failed.
Humans, other families in scored comparisons, external baselines, long-context
and compaction settings, and training remain untested.

The supplied records do not give E1b raw correct counts or per-view failures,
E1 actual model-token usage, or absolute dishonest-arm E4 HA intervals. The
paper reports available template means, total failures, token proxies, and
paired contrasts without inventing missing values. Exact E1 runtime revisions
are not supplied by RESULTS.md. E4's generic manifest says a 300-token cap,
while its frozen design says 800; per-prompt overrides cannot be established
from the summary. This discrepancy is disclosed.

The runner's about-12 L4 estimate is in the earlier committed handoff, not the
new result log. E1's about-7.1 units is traceable. The supplied under-2 E4 units
is absent from the cited log; recorded load/generation times instead imply
about 2.44 units at the stated rate, excluding overhead. The paper flags this
unresolved estimate and gives no combined bill or dollar conversion.
