# Post hoc reanalysis (2026-09-21)

All new analyses here are **POST HOC**, not preregistered. No model calls,
network requests, or new experiments are made. Frozen decisions are retained.
Run from `paper/` with `make reanalysis`, or from the repository root:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache MPLCONFIGDIR="$PWD/paper/.cache/matplotlib" uv run --offline --frozen --with matplotlib==3.11.2 python paper/analysis/reanalyse_e1.py
python3 paper/analysis/reanalyse_e4_e0.py
```

E1 reads both `experiments/E1/runs/e1-scored-0921*/trials.jsonl` files and
`experiments/E1/items/scored.jsonl`. E4 reads the supplied archived outputs and
labels (absolute defaults in the script, overridable using `--outputs`,
`--labels`, `--prompts`); prompts come from the matching archived job. E0 reads
the frozen, provenance-checked `paper/sources/e0-second-rater.md`. Input hashes
are written to generated JSON files. Newly derived tables and the figure are
under `paper/generated/`; generated files are committed. NumPy 2.5.3, SciPy
1.18.1, Matplotlib 3.11.2 were available offline. Python scripts assert pairing,
unique assignments, trial counts, oracle label consistency, and successful fits.

## E1 endpoints and inference

FA = approve / bad; HA = approve / good; balanced accuracy = (HA + 1 - FA)/2.
Good is the signal and approval is the positive response. For d-prime and
criterion c, apply the standard log-linear correction to **both** rates in
every cell: H=(hits+0.5)/(n_good+1), F=(false alarms+0.5)/(n_bad+1).
Then d'=Phi^-1(H)-Phi^-1(F), c=-(Phi^-1(H)+Phi^-1(F))/2. Counts and balanced
accuracy are uncorrected, pooled across candidates. Larger c is more reluctant
approval. The frozen worst-case rule is retained; no E1 sign-off trial failed.

Every paired contrast is the unweighted mean of within-template rate
differences, with identical candidates on both sides. Enumerate all 2^12 sign
flips, including the observed configuration; the two-sided p value is the
fraction with absolute mean at least the observed absolute mean. No Monte Carlo
pseudocount is needed. P1/P2 nominal per-comparison alpha is .025; other
contrasts use .05 and are exploratory/unadjusted. The printed p values are raw;
Bonferroni-adjusted co-primary p values are min(1,2p).

Intervals invert these same tests for a **constant location shift**, using
sign flips of d_t - delta on a grid with spacing .0005; the reported hull of
accepted grid points is expanded one grid step outward and constrained to the
logical parameter range. These are model-based sign-randomisation intervals,
not design-based causal randomisation intervals: the fixed authored templates
were not sampled or treatment-randomised. Exact enumeration is exact only
conditional on independent, sign-exchangeable template residuals under the
null; it does not solve template dependence or asymmetric heterogeneous
effects. Interval inversion adds a common symmetric-location assumption.
The zero-null test is the primary post hoc sensitivity; absolute-rate intervals
are particularly fragile on bounded heterogeneous template rates. Do not treat
them as population coverage guarantees. Leave-one-template-out ranges omit each
of the 12 templates in turn and recompute the equal-weight mean (not a CI).

The smallest-useful-effect table changes only the .03/.05/.08 threshold, retaining
the frozen HA constraint and the original 97.5% t intervals; a separate row uses
post hoc 97.5% sign-flip intervals. No choice is retroactively preregistered.

Weakening means the materials' **oracle** `direction == "weaker"`, not an attack
name or a finite-search guess: `build.py` overwrites the preliminary direction
using `oracle_validate_attack` (faithful entails attacked; converse has a
countermodel). There are 243 candidates in **nine** templates, hence 512 flips.
Three templates have no such attacks and are absent, not imputed as zero. Each
cell shows pooled counts/rate and the equal-template rate with its 95% inverted
sign-flip interval. Difference intervals test the paired equal-template effect.

## Logistic alternative

`uv run --offline --frozen --with statsmodels ...` failed because statsmodels
was absent from the offline cache. We therefore fit an unpenalized binomial
logistic GLM with SciPy, separately on bad and good candidates. Response =
approval; fixed terms = intercept + view + explanation + judge + view:judge.
Reference levels are symbolic FOL, no explanation, 14B. All repeated trials
within a semantic template share a sandwich cluster; base items are nested in
those templates, so their repeated views/judges are contained in the cluster.
This estimates marginal working-model associations, **not random-intercept
variances**, and imposes an additive explanation effect on the logit scale.
The robust covariance is H^-1 (sum_g U_g U_g') H^-1 times
G/(G-1)*(N-1)/(N-p), with t(11) reference intervals. Twelve clusters make that
approximation fragile. Coefficients and view-by-judge interactions are exploratory,
unadjusted; the model uses candidate weights, unlike the template contrasts.
Optimizer score convergence is checked (<1e-4); no separation or ridge penalty.

## E4 and E0

Lenient parser = last parseable JSON object anywhere in the reply with a valid
approve/reject verdict. All assigned replies yield verdicts; strict protocol
failures remain a separate count. No failure denominator is discarded. E4
lenient contrasts retain the descriptive template-t intervals, not E1's sign
flips. Frozen strict decisions are recomputed separately. The 7B sample uses
`random.Random(20260921).sample` over sorted prose keys, without replacement;
JSON saves full prompts, exact final instruction, label, and raw reply. Ten
verdict-only replies cannot establish the judge's internal interpretation.

The E0 ledger reproduces all 77 frozen inter-rater disputes, by dataset, with
the proposed adjudicator's item-specific adapter assumption. It does not rerate
items, execute source engines, or turn parse checks into semantic validation.
