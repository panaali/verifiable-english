# Negative-result and methods note

Drafted by GPT-6 Astra on `paper/v1`, after merging `ve-integration`.
This revision implements sections B (existing-data reanalysis, first) and A
(rewriting) of the two-review synthesis. No model calls, new experiments, or
network access were used. The main conclusion is no demonstrated strict-VE
benefit for 32B on short authored translations; 14B fluent effects remain
exploratory and confounded with requirement wording. E4 is uptake of explicit
checker findings, with post hoc lenient parsing presented and protocol failures
reported separately. Frozen decisions are preserved in one compact table.

## Rebuild offline

From `paper/`:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache XDG_CACHE_HOME="$PWD/.cache" TECTONIC_CACHE_DIR="$PWD/.cache/tectonic" make html pdf
python3 analysis/check_numbers.py
pdfinfo build/paper.pdf
```

The Makefile uses `uv --offline` and Tectonic `--only-cached`; dependencies and
TeX resources must already be cached. Outputs are `build/paper.html` and
`build/paper.pdf`. Analysis scripts and results are committed under `analysis/`
and `generated/`. `analysis/README.md` specifies endpoints, corrections, exact
sign-flip enumeration, interval assumptions, the cluster-robust logistic
alternative, inputs, and reproduction commands. The E4 script's three external
archive paths can be overridden with flags. Raw E1 trials are in the repository.

The post hoc weakening subset uses oracle relation labels (243 candidates,
nine templates), not attack names. For 32B/e3, strict VE approves 52 versus
31 under symbols; the paired template increase is .088, 95% sign-flip interval
[-.009, .214], p=.125. This is observed harm with uncertainty spanning zero.

`statsmodels` could not be installed from the offline cache. An unpenalized
binomial logistic model with template-clustered sandwich covariance was fitted
using cached SciPy; base items are nested within those clusters. It is not a
random-intercept model. Twelve fixed authored templates limit both this model
and sign-randomisation inference. All new analyses are POST HOC.

## Provenance and remaining boundaries

`sources/manifest.json` verifies frozen historical snapshots. New input hashes
are in `generated/posthoc-e1.json` and `posthoc-e4-e0-provenance.json`. The two
critical reviews and synthesis were read from the supplied local reviews
archive; this revision has not received another independent review.

No human has read the Lean theorem statements, templates, or preregistrations;
there is no external preregistration timestamp. E4 replay is Python, not Lean.
No local documentation citation for verified FOL provers was available, so the
requested explicit citation-needed marker remains. E2/E5, training, human
sign-off, source-engine translation tests, larger/more varied judges, and
frontier-scale settings remain unrun. Planned round 2 lists synthesis 11--16.

The PDF has **10 pages of main text, 1 reference page, and 24 appendix pages** (35 total). The main text ends at Planned round 2. References and labeled appendices follow;
appendices retain the full exploratory tables, 10 sampled 7B replies with task
opening/final instruction, all 77 E0 disputes, training plans, non-runs, Rust
benchmarks, compute accounting, and process history. Page inventory and build
verification are recorded in `build/draft-status.json` and the revision audit.
