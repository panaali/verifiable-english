Worker X / GPT-6 Astra independently rated the seven fixed 30-item samples. This
is a cross-model-family audit against the earlier Claude survey, not a human
annotation study or a population-wide coverage estimate. The sample, item IDs,
and inclusion frame were inherited unchanged from `survey_sample.py` (seed
20260921). No failed or difficult item was removed from a denominator.

### Blinding and provenance

First-rater labels are in `survey_samples/<dataset>.jsonl`; raw sampled items are
in `survey_samples/_drawn/<dataset>.json`. The parent inspected the first files
programmatically for keys and row counts, without displaying label or reason
values. A location search also printed aggregate counts and dataset commentary
from `SURVEY.md` before independent rating. That exposure is a limitation: the
parent was not blind to all aggregate results. No item-specific first-rater label
or rationale was displayed before the freeze. Each of seven dataset agents began
with a fresh context containing none of those aggregates, read only the raw
sample/specification and necessary source context, and reported no blinding
breach. The parent reviewed witnesses and requested semantic corrections while
still blind to first-rater item labels. Independent labels and accepted witnesses
were then frozen in `second_rater.jsonl`, with hashes/timestamp in
`second_rater_freeze.json`, before opening first-rater values for comparison.

The language specification is `docs/spec/v0-language.md`. The actual checker is
the `ve` package exported from integration commit
`12538d8d418b3eeec59e58d74c3886786e5139da`, rather than the older package on this
branch. Its source hashes are recorded in the freeze. Every claimed fit has a
full authored witness, vocabulary, rationale, and actual `ve.check` result. Parser
acceptance proves syntax, binding and types only; it neither proves the semantic
translation faithful nor certifies the originating claim. No solver validity,
source-engine differential test, or human intent confirmation is claimed.
Nine targeted finite-model spot checks additionally exercise missing-versus-false
Cedar context values and distinct Gatekeeper probe bindings/update guards. These
check the authored witnesses on selected models, not their full source engines.

### Item units and decision rules

- FOLIO: the sampled natural-language sentence, consulting its supplied FOL but
  preserving qualifications even when the gold formula drops them.
- ProofWriter: the full sampled theory plus question. `statement_roles` separates
  the question from premises: a checked multi-statement document is a syntax
  witness, not an assertion that the question follows. Raw NatLang paraphrase
  qualifications are part of the item; benchmark templates do not justify
  silently deleting them. The supported rules use classical implication and
  explicit negation; benchmark operational entailment labels were not recomputed
  or claimed to agree with every consequence of classical FOL.
- Cedar: one policy's matching condition and permit/forbid contribution, including
  scopes, conditions, missing-field behavior, and exceptions. A policy effect is
  not the final decision of a multi-policy authorization engine. Interpretation
  of hierarchy membership, missing fields, and typed literals was checked against
  the official [operator](https://docs.cedarpolicy.com/policies/syntax-operators.html)
  and [datatype](https://docs.cedarpolicy.com/policies/syntax-datatypes.html) references.
- Gatekeeper: the entire violation condition, including imported helpers,
  exemptions, defaults and update guards. Formatting of diagnostic messages is
  excluded. This consistent rule differs from the original survey's occasional
  core-rule classification and is reflected in the disagreements.
- Alloy: the selected paragraph, expanding referenced definitions needed to
  interpret it. A scope used by a nearby example command is not a universal bound
  on the selected claim.
- FRET: the requirement's declared signal/trace semantics, consulting original
  exported semantic descriptions when needed. A signal name that resembles a
  computation is not itself a computation in the sampled formula.
- Clover: functional contracts, loop invariants and supporting specification
  definitions; algorithm statements are excluded. Per-invocation relational
  encodings keep preconditions distinguishable from postconditions.

DIRECT uses only v0's unary/binary function-free first-order formulas with
equality. REIFIED supplies a stated mechanical relational representation of
events, records, function graphs, collection cells or trace points. Fixed
cardinalities may expand to finitely many quantifiers and inequalities; equality
to fixed literals needs no arithmetic. Reification may require a faithful input
adapter, and does not establish that an arbitrary submitted relation is such an
adapter's output. These adapter assumptions are recorded with the witnesses.

OPAQUE retains a useful relational skeleton but names the interpreted content
that would remain unchecked. NO is used when unsupported interpretation is the
substance of the claim and no useful independent relational skeleton remains.
That OPAQUE/NO boundary is judgment-dependent; the four-way kappa should be read
alongside fit/no-fit kappa. Neither OPAQUE nor NO counts as verified v0 coverage.
Predicate names cannot turn regex, arbitrary arithmetic, closure or modality into
implemented v0 features.

The original survey sometimes counted the policy's core rule while separately
noting an opaque exemption, and sometimes followed a simplified benchmark logical
form. Thus agreement includes differences in application of the stated item unit,
not only random disagreement under an identical operational rubric. The original
labels are preserved so this limitation stays visible rather than being repaired
before calculating agreement.

### Findings during adjudication

The blind freeze is commit `266401b`. Agreement is calculated from that frozen
record, before any proposed corrections. Reviewing the two rationales exposed
three semantic errors in the second rater's Cedar witnesses: `github_example`
policies `#3`, `#4`, and `#5` use `principal in` a `UserGroup` entity referenced by
`readers`, `triagers`, or `writers`. The source schema confirms those fields are
group entities. The frozen witnesses incorrectly treated them as ordinary
user-set membership. All three parse, but are not faithful; their proposed labels
are OPAQUE and their actual missing construct is hierarchy closure. The schema
path, hash and finding are saved with those adjudication records.

Thus **114 frozen claimed-fit witnesses pass syntax/type checking, but three
were found semantically defective after unblinding; proposed adjudicated fit is
111/210 across this deliberately heterogeneous sample**. That count is an
inventory, not a pooled coverage estimate. The dataset-specific results below
remain the relevant measurements.

Six proposed DIRECT labels also use simpler encodings than the frozen ones:
five fixed-action Cedar policies can be specialized to binary contribution
relations, and Gatekeeper host-namespaces already uses only primitive unary
tests. Their six accepted alternatives are recorded separately in
`second_rater_adjudication_witnesses.jsonl`. Fixed-action specialization makes
the effect false for all other actions and retains field-presence checks. If an
audit requires one uniform ternary/request representation even for a fixed
action, keep these five Cedar labels REIFIED; their fit/no-fit outcome does not
change. This strict-label convention is distinct from the three actual semantic
corrections above.

### Statistical limits and reproduction

Wilson intervals use z = 1.959963984540054 and n = 30 for each dataset, without
pooling heterogeneous datasets or applying a finite-population correction. They
are nominal item-sampling intervals, not uncertainty intervals for model-rater
validity; shared source files, templates and subject matter can make the effective
sample size smaller. Cohen's kappa uses each rater's empirical marginal
distribution, with undefined values explicitly retained when expected agreement
is one. The code includes hand-checkable statistical self-tests.

From this worktree, reproduce verification and all tables with:

```sh
mkdir -p /private/tmp/ve-e0-integration
git archive 12538d8d418b3eeec59e58d74c3886786e5139da ve pyproject.toml | tar -x -C /private/tmp/ve-e0-integration
UV_CACHE_DIR=/private/tmp/ve-uv-cache-grammar python3 experiments/E0/second_rater_audit.py selftest
UV_CACHE_DIR=/private/tmp/ve-uv-cache-grammar python3 experiments/E0/second_rater_audit.py verify
UV_CACHE_DIR=/private/tmp/ve-uv-cache-grammar python3 experiments/E0/second_rater_spotchecks.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache-grammar python3 experiments/E0/second_rater_work/adjudication_witnesses.py
UV_CACHE_DIR=/private/tmp/ve-uv-cache-grammar python3 experiments/E0/second_rater_audit.py report
```

Dataset generators under `second_rater_work/` reproduce authored ratings and
witnesses from the fixed raw samples. They do not provide an automatic semantic
labeling algorithm. `freeze` is a one-time operation and intentionally refuses to
overwrite the saved independent ratings. Proposed adjudications remain separate
in `second_rater_adjudications.jsonl`; the first-rater files are unchanged.
