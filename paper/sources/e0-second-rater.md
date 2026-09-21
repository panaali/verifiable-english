# E0 independent second-rater coverage audit

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

## Frozen independent labels

| Dataset | DIRECT | REIFIED | OPAQUE | NO | Fit witnesses checked |
|---|---:|---:|---:|---:|---:|
| FOLIO | 22 | 3 | 4 | 1 | 25 |
| ProofWriter | 26 | 0 | 4 | 0 | 26 |
| Cedar | 0 | 13 | 17 | 0 | 13 |
| Gatekeeper | 1 | 5 | 24 | 0 | 6 |
| Alloy | 4 | 14 | 3 | 9 | 18 |
| FRET | 0 | 12 | 12 | 6 | 12 |
| Clover | 3 | 11 | 9 | 7 | 14 |

## Coverage estimates

Each cell is k/30, percentage, and nominal 95% Wilson interval. Opaque-dependent fit is OPAQUE alone, disjoint from lenient fit; it does not establish that v0 implements the hidden check.

| Dataset | Strict: DIRECT | Lenient: DIRECT + REIFIED | Opaque-dependent: OPAQUE only |
|---|---|---|---|
| FOLIO | 22/30 = 73.3% [55.6, 85.8] | 25/30 = 83.3% [66.4, 92.7] | 4/30 = 13.3% [5.3, 29.7] |
| ProofWriter | 26/30 = 86.7% [70.3, 94.7] | 26/30 = 86.7% [70.3, 94.7] | 4/30 = 13.3% [5.3, 29.7] |
| Cedar | 0/30 = 0.0% [0.0, 11.4] | 13/30 = 43.3% [27.4, 60.8] | 17/30 = 56.7% [39.2, 72.6] |
| Gatekeeper | 1/30 = 3.3% [0.6, 16.7] | 6/30 = 20.0% [9.5, 37.3] | 24/30 = 80.0% [62.7, 90.5] |
| Alloy | 4/30 = 13.3% [5.3, 29.7] | 18/30 = 60.0% [42.3, 75.4] | 3/30 = 10.0% [3.5, 25.6] |
| FRET | 0/30 = 0.0% [0.0, 11.4] | 12/30 = 40.0% [24.6, 57.7] | 12/30 = 40.0% [24.6, 57.7] |
| Clover | 3/30 = 10.0% [3.5, 25.6] | 14/30 = 46.7% [30.2, 63.9] | 9/30 = 30.0% [16.7, 47.9] |

## Agreement with the first rater

Original a/b/c/d map to DIRECT/REIFIED/OPAQUE/NO. Collapsed FIT = DIRECT or REIFIED; NO_FIT = OPAQUE or NO. Raw labels are compared without silently repairing first-rater scope exceptions. Confusion matrices (first rater rows, second rater columns) are in `second_rater_comparison.json`.

| Dataset | 4-way agreement | 4-way κ | Fit/no-fit agreement | Fit/no-fit κ |
|---|---:|---:|---:|---:|
| FOLIO | 24/30 (80.0%) | 0.4268 | 27/30 (90.0%) | 0.5263 |
| ProofWriter | 26/30 (86.7%) | 0.0000 | 26/30 (86.7%) | 0.0000 |
| Cedar | 4/30 (13.3%) | -0.1127 | 12/30 (40.0%) | -0.0672 |
| Gatekeeper | 18/30 (60.0%) | 0.2593 | 22/30 (73.3%) | 0.4444 |
| Alloy | 20/30 (66.7%) | 0.5320 | 29/30 (96.7%) | 0.9315 |
| FRET | 22/30 (73.3%) | 0.5745 | 26/30 (86.7%) | 0.7059 |
| Clover | 19/30 (63.3%) | 0.5045 | 20/30 (66.7%) | 0.2991 |

ProofWriter has κ = 0 because the first rater used DIRECT for every item, so empirical chance agreement equals observed agreement. Kappa is undefined when both marginal distributions put all items in the same category; perfect observed agreement would still be reported.

## Proposed adjudication

These are Worker X proposals after seeing both rationales, not an independent third rating or accepted consensus. Frozen second-rater labels are unchanged. All matching labels are retained; each disagreement is addressed below.

| Dataset | Strict: DIRECT | Lenient: DIRECT + REIFIED | Opaque-dependent: OPAQUE only |
|---|---|---|---|
| FOLIO | 22/30 = 73.3% [55.6, 85.8] | 25/30 = 83.3% [66.4, 92.7] | 4/30 = 13.3% [5.3, 29.7] |
| ProofWriter | 26/30 = 86.7% [70.3, 94.7] | 26/30 = 86.7% [70.3, 94.7] | 4/30 = 13.3% [5.3, 29.7] |
| Cedar | 5/30 = 16.7% [7.3, 33.6] | 10/30 = 33.3% [19.2, 51.2] | 20/30 = 66.7% [48.8, 80.8] |
| Gatekeeper | 2/30 = 6.7% [1.8, 21.3] | 6/30 = 20.0% [9.5, 37.3] | 24/30 = 80.0% [62.7, 90.5] |
| Alloy | 4/30 = 13.3% [5.3, 29.7] | 18/30 = 60.0% [42.3, 75.4] | 3/30 = 10.0% [3.5, 25.6] |
| FRET | 0/30 = 0.0% [0.0, 11.4] | 12/30 = 40.0% [24.6, 57.7] | 12/30 = 40.0% [24.6, 57.7] |
| Clover | 3/30 = 10.0% [3.5, 25.6] | 14/30 = 46.7% [30.2, 63.9] | 9/30 = 30.0% [16.7, 47.9] |

## What v0 would need next

Counts use frozen NO and OPAQUE items. An item counts once per construct family and can contribute to multiple families; column sums are not sample sizes. The tag-to-family mapping, explicit per-item exclusions of already-supported constructs, and item memberships are committed for inspection. Lexical disambiguation is an authoring/grounding need, not a new logical connective.

| Construct | FOLIO | ProofWriter | Cedar | Gatekeeper | Alloy | FRET | Clover | Total items |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Numeric arithmetic and value comparisons | 1 | 0 | 0 | 8 | 2 | 18 | 16 | 45 |
| Transitive closure and reachability | 1 | 0 | 17 | 0 | 9 | 0 | 0 | 27 |
| String operations, regex and parsing | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 20 |
| Frequency and defeasible/default quantification | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 5 |
| General counting and multiplicities | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 4 |
| Metric time and duration | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 |
| Modal and propositional-attitude semantics | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 3 |
| Lexical sense disambiguation | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| Transcendental numeric functions | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 |
| Higher-order quantification | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |

After proposed adjudication:

| Construct | FOLIO | ProofWriter | Cedar | Gatekeeper | Alloy | FRET | Clover | Total items |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Numeric arithmetic and value comparisons | 1 | 0 | 0 | 8 | 2 | 18 | 16 | 45 |
| Transitive closure and reachability | 1 | 0 | 20 | 0 | 9 | 0 | 0 | 30 |
| String operations, regex and parsing | 0 | 0 | 0 | 20 | 0 | 0 | 0 | 20 |
| Frequency and defeasible/default quantification | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 5 |
| General counting and multiplicities | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 4 |
| Metric time and duration | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 3 |
| Modal and propositional-attitude semantics | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 3 |
| Lexical sense disambiguation | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| Transcendental numeric functions | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 |
| Higher-order quantification | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |

## Every disagreement

### FOLIO (6)

**`e545:c`**

- First: **DIRECT** — negated unary atom
- Second: **REIFIED** — The future and remaining-game scope are exposed as relations on a possible ejection event. The claim denies any Henry-ejection event after now and during the remaining part of the game, rather than hiding futurity in a unary predicate.
- Proposed: **REIFIED** — Future ejection and the rest-of-game restriction need explicit event/time relations; the checked reification retains both.

**`s367:p0`**

- First: **REIFIED** — gold uses ternary MakeWith(x, tea, powder); needs reification; also drops 'every morning'
- Second: **OPAQUE** — The core negative consequence is relational, but 'every morning' and 'regularly' require temporal or frequency semantics unavailable in v0. Naming predicates for those checks would conceal essential interpretation.
- Proposed: **OPAQUE** — Event roles alone do not preserve every-morning and regular-frequency qualifications omitted by the gold formula.

**`e1126:c`**

- First: **DIRECT** — disjunction of negated binary atoms
- Second: **OPAQUE** — The outer disjunction is relationally simple, but both branches are propositional attitudes: wanting an addiction state and awareness of the proposition that caffeine is a drug. v0 has no proposition terms or attitude operators. Predicates such as wants_addiction_to and aware_is_drug would hide those essential embedded meanings.
- Proposed: **OPAQUE** — Negated desire and awareness contain embedded propositions whose interpretation remains hidden by atomic attitude names.

**`e573:c`**

- First: **OPAQUE** — NL is modal/temporal ('possible ... without ever'); gold hides it in an opaque RedToYellow predicate
- Second: **NO** — The essential claim quantifies over a possible course of play reaching yellow while never visiting green. v0 cannot quantify over paths or arbitrary sequences, express reachability, or state 'ever/never' along a path. The gold's RedToYellow predicate hides and also omits the avoidance condition.
- Proposed: **NO** — Path possibility with never-visiting-green is the substance of the claim, so no independent relational claim survives the missing reachability semantics.

**`s69:p1`**

- First: **DIRECT** — year as a plain constant, no comparison; gold drops 'after being injured'
- Second: **REIFIED** — The word 'after' requires relating an injury event to a retirement event; reifying both events preserves precedence and the retirement year. The gold omits the injury and ordering entirely.
- Proposed: **REIFIED** — Retirement-year equality is supported, but preserving the injury-before-retirement relation requires the supplied event reification.

**`s217:p2`**

- First: **DIRECT** — propositional over unary atoms; modality folded into predicate names
- Second: **OPAQUE** — The sentence connects ability, desire, and a future action. v0 has neither modal accessibility nor proposition/action objects sufficient to interpret can, wants to, and will. Unary predicates named can_compose, wants_to_compose, and will_compose would hide every essential modal component.
- Proposed: **OPAQUE** — Ability, desire and future action remain modal content even when their predicate names parse.

### ProofWriter (4)

**`AttNonegNatLang-OWA-60#row11574`**

- First: **DIRECT** — single sort; unary predicates, constants, universally quantified Horn-style rules; crowd-paraphrased prose with hedges (usually/often) that the underlying rule ignores; formula fits, but gold label comes from a forward-chaining rule engine, not classical entailment
- Second: **OPAQUE** — The raw theory uses 'usually' and 'often' as frequency/default qualifiers. v0 has neither generalized frequency quantifiers nor default logic, so replacing them with universal implications would strengthen and lose the stated meaning. The remaining named-individual facts and strictly worded rules provide a useful relational skeleton, but not a faithful formalization of the complete theory.
- Proposed: **OPAQUE** — The sampled NatLang text explicitly keeps usually/often/default qualifications; deleting them to recover hidden Horn templates changes the full item.

**`AttNonegNatLang-OWA-211#row10260`**

- First: **DIRECT** — single sort; unary predicates, constants, universally quantified Horn-style rules; crowd-paraphrased prose with hedges (usually/often) that the underlying rule ignores; formula fits, but gold label comes from a forward-chaining rule engine, not classical entailment
- Second: **OPAQUE** — The raw theory includes 'often assumed' (an epistemic/default qualification) and 'usually'. v0 cannot express those qualifications, and treating them as strict universal implications is not faithful. The remaining named-individual facts and strictly worded rules provide a useful relational skeleton, but not a faithful formalization of the complete theory.
- Proposed: **OPAQUE** — The sampled NatLang text explicitly keeps usually/often/default qualifications; deleting them to recover hidden Horn templates changes the full item.

**`AttNonegNatLang-OWA-2#row12794`**

- First: **DIRECT** — single sort; unary predicates, constants, universally quantified Horn-style rules; crowd-paraphrased prose with hedges (usually/often) that the underlying rule ignores; formula fits, but gold label comes from a forward-chaining rule engine, not classical entailment
- Second: **OPAQUE** — The raw theory uses 'tends to', 'usually', and figurative color language. v0 cannot preserve the default/frequency force; a strict Horn normalization would erase those qualifications. The remaining named-individual facts and strictly worded rules provide a useful relational skeleton, but not a faithful formalization of the complete theory.
- Proposed: **OPAQUE** — The sampled NatLang text explicitly keeps usually/often/default qualifications; deleting them to recover hidden Horn templates changes the full item.

**`AttNonegNatLang-OWA-92#row10996`**

- First: **DIRECT** — single sort; unary predicates, constants, universally quantified Horn-style rules; crowd-paraphrased prose with hedges (usually/often) that the underlying rule ignores; formula fits, but gold label comes from a forward-chaining rule engine, not classical entailment
- Second: **OPAQUE** — The raw theory uses 'often' and 'usually' frequency/default claims as essential premises. v0 cannot express their force, so universally quantifying them would be a non-faithful strengthening. The remaining named-individual facts and strictly worded rules provide a useful relational skeleton, but not a faithful formalization of the complete theory.
- Proposed: **OPAQUE** — The sampled NatLang text explicitly keeps usually/often/default qualifications; deleting them to recover hidden Horn templates changes the full item.

### Cedar (26)

**`cedar-examples/cedar-example-use-cases/document_cloud/policies.cedar#5`**

- First: **DIRECT** — per-action binary permit predicate; owner attribute as binary relation
- Second: **REIFIED** — Exact action equality and resource ownership are binary/equality constraints after reifying the request and policy effect.
- Proposed: **DIRECT** — Specializing the one fixed action yields a unary/binary contribution condition; the checked alternative needs no request tuple and preserves field presence.

**`cedar-examples/cedar-example-use-cases/sales_orgs/templated/policies.cedar#3`**

- First: **REIFIED** — action constrained by action-group membership, so action is quantified: permit(principal, action, resource) is ternary -> request reification
- Second: **OPAQUE** — The owner equality is relational, but `action in PrezEditActions` invokes Cedar entity-hierarchy reachability. A binary `in_group` predicate would hide that closure, so the useful skeleton still depends on an unavailable interpreted check.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/cedar-example-use-cases/github_example/policies.cedar#5`**

- First: **DIRECT** — `principal in resource.writers` as binary group-membership relation plus attribute relation
- Second: **REIFIED** — The writers attribute is a set-valued resource field, represented directly as a resource-to-principal relation.
- Proposed: **OPAQUE** — Both raters missed that the referenced writers/readers/triagers field is a UserGroup entity; the frozen membership witness hides Cedar hierarchy closure.

**`cedar-examples/cedar-example-use-cases/document_cloud/policies.cedar#7`**

- First: **DIRECT** — constants, equality on enum-like string attribute, boolean attribute as unary
- Second: **REIFIED** — The fixed public principal, exact action, string-valued access field, and unless guard are preserved. The explicit false Boolean value makes a missing isPrivate field fail rather than count as false.
- Proposed: **DIRECT** — Specializing the one fixed action yields a unary/binary contribution condition; the checked alternative needs no request tuple and preserves field presence.

**`cedar-examples/cedar-example-use-cases/sales_orgs/static/policies.cedar#5`**

- First: **REIFIED** — action-group membership -> ternary permit -> request reification
- Second: **OPAQUE** — The viewerMarkets collection is relational, but the action-group `in` guard requires Cedar hierarchy reachability, which v0 cannot define without hiding it in a predicate.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/oopsla2024-benchmarks/benches/github-templates/cedar/policies.cedar#0`**

- First: **REIFIED** — template with ?principal/?resource slots is an open formula; needs instantiation (constants) before it is a closed claim
- Second: **OPAQUE** — The resource template slot can be reified as a parameter, but `principal in ?principal` has Cedar hierarchy semantics over a runtime-bound entity. v0 has neither policy parameters nor transitive closure; an `in` predicate would conceal the essential check.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/cedar-policy-language-in-action/PhotoApp/photoapp.cedar#4`**

- First: **DIRECT** — group/album membership with constants, single action
- Second: **OPAQUE** — Both principal and resource scopes use Cedar `in`, whose membership includes transitive entity ancestry. General reachability is not function-free FOL definable by a finite witness.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/cedar-policy-language-in-action/GitApp/gitapp.cedar#4`**

- First: **DIRECT** — explicit action list expands to a conjunction; has+in as exists over a binary relation
- Second: **OPAQUE** — The action list, attribute-presence guard, and contributors collection are relational, but `resource in GitApp` requires entity-hierarchy closure. Treating that as an input predicate would hide a necessary Cedar computation.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/cedar-policy-language-in-action/GitApp/gitapp.cedar#3`**

- First: **DIRECT** — explicit action list; has+in
- Second: **OPAQUE** — The policy has a useful relational contributors skeleton, but its resource hierarchy scope is essential and cannot be implemented in v0.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/cedar-example-use-cases/github_example/policies.cedar#4`**

- First: **DIRECT** — attribute chain resource.repo.triagers as two binary relations
- Second: **REIFIED** — The nested resource.repo.triagers lookup is expanded into an existential repository join and set membership.
- Proposed: **OPAQUE** — Both raters missed that the referenced writers/readers/triagers field is a UserGroup entity; the frozen membership witness hides Cedar hierarchy closure.

**`cedar-examples/oopsla2024-benchmarks/benches/gdrive-templates/cedar/policies.cedar#0`**

- First: **REIFIED** — template slots; needs instantiation
- Second: **OPAQUE** — Both template slots are used as hierarchy ancestors. Their transitive `in` meaning cannot be represented faithfully as an unconstrained relation.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/cedar-java-partial-evaluation/app/src/main/resources/policies.cedar#3`**

- First: **DIRECT** — three constants, single action
- Second: **REIFIED** — All three scope components are exact entity equalities and become typed constants in the request match.
- Proposed: **DIRECT** — Specializing the one fixed action yields a unary/binary contribution condition; the checked alternative needs no request tuple and preserves field presence.

**`cedar-examples/cedar-example-use-cases/github_example/policies.cedar#3`**

- First: **DIRECT** — attribute chain, membership, equality
- Second: **REIFIED** — The repo readers membership and reporter equality are explicit joins over resource, repository, and principal.
- Proposed: **OPAQUE** — Both raters missed that the referenced writers/readers/triagers field is a UserGroup entity; the frozen membership witness hides Cedar hierarchy closure.

**`cedar-examples/oopsla2024-benchmarks/benches/github-templates/cedar/policies.cedar#6`**

- First: **REIFIED** — action-group hierarchy -> ternary permit -> request reification
- Second: **OPAQUE** — Owner-writers membership is relational, but the action hierarchy scope `action in write` is an essential transitive ancestry test unavailable in v0.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-integration-tests/tests/example_use_cases/policies_3c.cedar#0`**

- First: **REIFIED** — unconstrained action -> ternary permit -> request reification
- Second: **OPAQUE** — The principal equality is expressible, but resource membership below the album entity uses Cedar's transitive hierarchy closure.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/cedar-java-partial-evaluation/app/src/main/resources/policies.cedar#2`**

- First: **DIRECT** — forbid with three constants (forbid_read binary predicate)
- Second: **REIFIED** — The forbid rule is an exact typed tuple match; the witness records only this rule's forbid effect.
- Proposed: **DIRECT** — Specializing the one fixed action yields a unary/binary contribution condition; the checked alternative needs no request tuple and preserves field presence.

**`cedar-examples/cedar-example-use-cases/hotel_chains/static/policies.cedar#2`**

- First: **REIFIED** — `resource in principal.hotelAdminPermissions`: the set mixes Hotel and Property entities; without subtyping needs a union sort or per-type predicates (sort assignment)
- Second: **OPAQUE** — Cedar `in` is hierarchy-aware even when its right operand is a set. Thus the action can descend from a listed action and the resource can descend from an entity in either permission attribute. Replacing these with ordinary set membership would omit essential closure semantics.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-integration-tests/tests/example_use_cases/policies_2a.cedar#0`**

- First: **DIRECT** — group membership, constants
- Second: **OPAQUE** — Principal membership in jane_friends is a Cedar entity-ancestry query. The exact action and resource do not remove that essential unavailable check.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/cedar-example-use-cases/document_cloud/policies.cedar#11`**

- First: **DIRECT** — explicit action list; owner equality
- Second: **OPAQUE** — Although ownership is relational, Cedar `action in [ModifyGroup, DeleteGroup]` is hierarchy-aware: a descendant of either listed action also matches. A finite equality disjunction would be too narrow, while an ancestry predicate would hide transitive closure.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/oopsla2024-benchmarks/benches/github/cedar/policies.cedar#3`**

- First: **REIFIED** — action-group hierarchy -> request reification
- Second: **OPAQUE** — Maintainers membership is relational, but `action in maintain` uses the Cedar action hierarchy and cannot be replaced with plain equality or an opaque ancestry predicate.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-integration-tests/tests/ip/policies_1.cedar#0`**

- First: **OPAQUE** — ip("...") extension constructor: value equality depends on IP parsing/normalisation that a constant would hide
- Second: **REIFIED** — The IP constructor is applied once to a fixed source literal at translation time, yielding a typed IP constant; the runtime policy operation is then exact equality of two already-typed IP values. The witness exposes the context-to-IP relation and exact constructor spelling rather than hiding a `source_ip_matches` check.
- Proposed: **REIFIED** — The source constructs one fixed typed IP literal; after literal decoding the only runtime operation is exact value equality, which the checked reification exposes.

**`cedar-examples/cedar-java-partial-evaluation/app/src/main/resources/policies.cedar#0`**

- First: **REIFIED** — action-group hierarchy -> request reification
- Second: **OPAQUE** — All three scopes use Cedar hierarchy membership. General transitive ancestry cannot be expressed by this fragment without an unimplemented closure predicate.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-integration-tests/tests/example_use_cases/policies_3a.cedar#0`**

- First: **DIRECT** — single action, album membership constant
- Second: **OPAQUE** — The action equality is direct, but resource membership under the album depends on Cedar hierarchy closure.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/cedar-policy-language-in-action/GitApp/gitapp.cedar#2`**

- First: **DIRECT** — explicit action list; has+in
- Second: **OPAQUE** — The action enumeration and reporters collection are relational, but the resource scope requires hierarchy reachability and is essential to matching.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/oopsla2024-benchmarks/benches/gdrive/cedar/policies.cedar#0`**

- First: **REIFIED** — set mixes Document and Folder entities -> union sort (sort assignment)
- Second: **OPAQUE** — The schema makes documentsAndFoldersWithViewAccess an entity-valued View ancestor, and Cedar `resource in` tests whether the resource equals or descends from it. A principal-to-resource relation would hide the required closure.
- Proposed: **OPAQUE** — Cedar in includes transitive entity ancestry, so a supplied ancestor relation would hide the policy check rather than implement it in v0.

**`cedar-examples/cedar-example-use-cases/streaming_service/policies.cedar#1`**

- First: **DIRECT** — `is` entity-type tests map to sorts; boolean attribute as unary
- Second: **REIFIED** — Cedar type tests become unary predicates on typed request entities. The unless guard requires an explicitly present false Boolean field, so a missing field does not spuriously permit. This rule contributes permit only.
- Proposed: **DIRECT** — Specializing the one fixed action yields a unary/binary contribution condition; the checked alternative needs no request tuple and preserves field presence.

### Gatekeeper (12)

**`gatekeeper-library/src/general/automount-serviceaccount-token/src.rego`**

- First: **DIRECT** — JSON tree as entities + binary relations; equality with a constant path; is_update as unary
- Second: **REIFIED** — The complete violation condition reduces to first-order membership, equality, presence, and negation. Imported update/exemption behavior and missing/default branches are explicit in the witness where applicable.
- Proposed: **REIFIED** — The full checked rule preserves nested collections or old/new input records through the explicitly stated relational representation.

**`gatekeeper-library/src/general/containerresources/src.rego`**

- First: **DIRECT** — missing required resource = exists required type with no has_limit(container,type); NOTE exemption clause is_exempt does image-name glob matching, which would be an opaque unary predicate
- Second: **OPAQUE** — The missing required-resource test is relational, but imported exempt_container trims a wildcard suffix and performs prefix matching over arbitrary image strings.
- Proposed: **OPAQUE** — The complete violation includes the imported image exemption, whose wildcard suffix trimming and prefix matching are not implemented by v0.

**`gatekeeper-library/src/pod-security-policy/selinux/src.rego`**

- First: **REIFIED** — allowed SELinux option records must be reified as entities with four attribute relations; NOTE is_exempt opaque
- Second: **OPAQUE** — The four optional SELinux fields and common allowed record can be faithfully reified, but the complete container branch imports exempt_container, whose wildcard image exemptions require arbitrary suffix trimming and prefix matching.
- Proposed: **OPAQUE** — The complete violation includes the imported image exemption, whose wildcard suffix trimming and prefix matching are not implemented by v0.

**`gatekeeper-library/src/general/noupdateserviceaccount/src.rego`**

- First: **DIRECT** — old/new service account inequality, user/group membership (count of intersection > 0 is just exists)
- Second: **REIFIED** — The complete violation condition reduces to first-order membership, equality, presence, and negation. Imported update/exemption behavior and missing/default branches are explicit in the witness where applicable.
- Proposed: **REIFIED** — The full checked rule preserves nested collections or old/new input records through the explicitly stated relational representation.

**`gatekeeper-library/src/pod-security-policy/seccompv2/src.rego`**

- First: **REIFIED** — profile/file records reified; equality only; NOTE is_exempt opaque
- Second: **OPAQUE** — Profile selection and allowed-value equality can be reified, but the complete condition invokes exempt_container, whose wildcard image exemptions require arbitrary suffix and prefix operations.
- Proposed: **OPAQUE** — The complete violation includes the imported image exemption, whose wildcard suffix trimming and prefix matching are not implemented by v0.

**`gatekeeper-library/src/pod-security-policy/privileged-containers/src.rego`**

- First: **DIRECT** — container has privileged flag; NOTE is_exempt opaque
- Second: **OPAQUE** — The privileged-field branch is relational, but the imported container exemption performs wildcard suffix trimming and arbitrary image-prefix matching.
- Proposed: **OPAQUE** — The complete violation includes the imported image exemption, whose wildcard suffix trimming and prefix matching are not implemented by v0.

**`gatekeeper-library/src/pod-security-policy/host-namespaces/src.rego`**

- First: **DIRECT** — two boolean fields
- Second: **REIFIED** — The complete violation condition reduces to first-order membership, equality, presence, and negation. Imported update/exemption behavior and missing/default branches are explicit in the witness where applicable.
- Proposed: **DIRECT** — The existing witness already uses only one request constant and three primitive unary field tests, with no tuple or collection reification.

**`gatekeeper-library/src/pod-security-policy/host-process/src.rego`**

- First: **DIRECT** — boolean field on pod or container; NOTE is_exempt opaque
- Second: **OPAQUE** — The pod-level branch is relational, but the complete violation disjunction includes container exemptions implemented by wildcard suffix trimming and arbitrary image-prefix matching.
- Proposed: **OPAQUE** — The complete violation includes the imported image exemption, whose wildcard suffix trimming and prefix matching are not implemented by v0.

**`gatekeeper-library/src/general/externalip/src.rego`**

- First: **DIRECT** — exists external IP not in allowed set (set difference non-empty)
- Second: **REIFIED** — The complete violation condition reduces to first-order membership, equality, presence, and negation. Imported update/exemption behavior and missing/default branches are explicit in the witness where applicable.
- Proposed: **REIFIED** — The full checked rule preserves nested collections or old/new input records through the explicitly stated relational representation.

**`gatekeeper-library/src/general/uniqueserviceselector/src.rego`**

- First: **REIFIED** — selector map equality: key/value entries reified; source implements it with concat/sort string building
- Second: **OPAQUE** — The helper flattens each selector into a sorted delimiter-concatenated string and compares those strings. Set equality would silently remove the source helper's delimiter-collision behavior, while v0 cannot express the actual concatenation.
- Proposed: **OPAQUE** — Without an additional input restriction proving delimiter serialization injective, source string equality cannot be replaced by selector-map equality.

**`gatekeeper-library/src/general/disallowinteractive/src.rego`**

- First: **DIRECT** — field presence and boolean values; NOTE is_exempt opaque
- Second: **OPAQUE** — The stdin and tty tests are relational, but imported exempt_container adds wildcard suffix trimming and arbitrary image-prefix matching to the full condition.
- Proposed: **OPAQUE** — The complete violation includes the imported image exemption, whose wildcard suffix trimming and prefix matching are not implemented by v0.

**`gatekeeper-library/src/pod-security-policy/allow-privilege-escalation/src.rego`**

- First: **DIRECT** — field presence and boolean values; NOTE is_exempt opaque
- Second: **OPAQUE** — Missing securityContext and false-value semantics are relational, but imported exempt_container requires wildcard suffix trimming and arbitrary image-prefix matching.
- Proposed: **OPAQUE** — The complete violation includes the imported image exemption, whose wildcard suffix trimming and prefix matching are not implemented by v0.

### Alloy (10)

**`alloy-models/algorithms/ring-orientation/stable-orient-ring.als@1924`**

- First: **OPAQUE** — RingAtTick calls graph/ring, defined by transitive closure; also ord/next
- Second: **NO** — After expanding RingAtTick and graph/ring, the preservation assertion essentially tests reachability and ring structure using reflexive/transitive closure. v0 cannot define that closure, and treating ring_at_tick as atomic would hide the essential claim.
- Proposed: **NO** — Ring preservation depends essentially on graph/ring reachability; the whole ring condition would otherwise be hidden.

**`alloy-models/algorithms/distributed-hashtable/chord2.als@81`**

- First: **OPAQUE** — transitive closure ^next
- Second: **NO** — less_than is defined by membership in the transitive closure of a cyclic successor relation after deleting edges into from. Reachability is the entire predicate and v0 has no closure operator.
- Proposed: **NO** — The selected cyclic-order predicate is defined by transitive closure of a modified successor graph.

**`alloy-models/algorithms/distributed-hashtable/chord.als@80`**

- First: **OPAQUE** — transitive closure ^next (same text as chord2.als; population not deduplicated across files)
- Second: **NO** — The duplicate less_than definition likewise depends essentially on transitive closure after relation restriction/difference.
- Proposed: **NO** — The selected cyclic-order predicate is defined by transitive closure of a modified successor graph.

**`alloy-models/utilities/types/sequence.als@1510`**

- First: **OPAQUE** — sequence cardinality # and add[1] arithmetic
- Second: **NO** — add expands startsWith/afterLastIdx and requires cardinality equality with integer addition. Unbounded counting and arithmetic are unavailable in v0.
- Proposed: **NO** — The source sequence equation requires unrestricted cardinality and integer-addition semantics, rather than a mere relation-name change.

**`alloy-models/algorithms/multicasting/iolus.als@5190`**

- First: **OPAQUE** — reflexive-transitive closure *(parent + ~parent)
- Second: **NO** — Connected is precisely reachability in the undirected parent graph via reflexive transitive closure. No independent non-closure content remains.
- Proposed: **NO** — The entire connectedness assertion is reflexive-transitive graph reachability.

**`alloy-models/utilities/types/sequence.als@1980`**

- First: **OPAQUE** — cardinality equalities over ord/prevs
- Second: **NO** — copy equates cardinalities of predecessor sets and therefore compares arbitrary indices by counting. v0 lacks general counting and arithmetic.
- Proposed: **NO** — The copy alignment is defined by equality of unbounded predecessor-set cardinalities.

**`alloy-models/models/java/javatypes_soundness.als@282`**

- First: **OPAQUE** — graph/dag = acyclicity via closure
- Second: **NO** — graph/dag expands to acyclicity via transitive closure; that is the whole fact.
- Proposed: **NO** — The whole fact is graph acyclicity, implemented by an unavailable transitive-closure check.

**`alloy-models/models/typography/paragraph-numbering.als@1226`**

- First: **REIFIED** — sub-signature equality: signatures become unary predicates over a parent sort (no subtyping in v0)
- Second: **DIRECT** — Because NumberedState is a subsignature of State, State = NumberedState is exactly that every State atom is numbered.
- Proposed: **DIRECT** — A unary predicate over State expresses membership in NumberedState without adding tuple entities or a subtype mechanism.

**`alloy-models/utilities/types/relation.als@268`**

- First: **NO** — quantifies over an arbitrary relation parameter (r: univ->univ): second-order
- Second: **REIFIED** — For the fixed relation and set parameters, function[r,s] says each in_s element has exactly one in_r image. Existence plus equality of every other image expresses one without counting.
- Proposed: **REIFIED** — r and s are supplied predicate parameters, not explicitly universally quantified relation variables inside this body; fixed input extensions suffice.

**`alloy-models/algorithms/distributed-hashtable/chord.als@3722`**

- First: **OPAQUE** — inlined predicates depend on less_than (closure)
- Second: **NO** — SameCPF2 expands ordering reachability through less_than and also uses #active=1. Although the latter is expressible, the closest-preceding semantics essentially uses closure.
- Proposed: **NO** — Expanding the closest-preceding-finger predicates leaves closure as the essential condition.

### FRET (8)

**`LM_requirements.json:LM_requirements:EUL-006C:3b33fb60`**

- First: **OPAQUE** — equality of real-valued signals with numeric constants (results of matrix arithmetic)
- Second: **REIFIED** — The requirement is mechanically expressible using explicit snapshots and ordinary unary/binary relations; the adapter semantics are stated rather than hidden in an interpreted predicate.
- Proposed: **REIFIED** — The exported semantics compare declared signal variables to a fixed numeric literal; no matrix multiplication occurs in this requirement.

**`LM_requirements.json:LM_requirements:NN-003B:c829ea64`**

- First: **OPAQUE** — metric time plus numeric bounds
- Second: **NO** — The substantive requirement is a numeric interval maintained for 200 seconds. No qualitative relational claim remains after removing metric time and comparisons.
- Proposed: **NO** — Only numeric bounds over a metric duration remain; the substantive claim needs both unsupported interpretations.

**`LM_requirements.json:LM_requirements:REG-007:c829ea78`**

- First: **OPAQUE** — numeric comparison
- Second: **NO** — This is solely a real-valued upper-bound claim; an atomic predicate would merely conceal the comparison.
- Proposed: **NO** — The entire response is an interpreted real-number upper bound, so a named predicate would conceal the whole claim.

**`LM_requirements.json:LM_requirements:EUL-007:89d04ff0`**

- First: **OPAQUE** — equalities with real constants produced by matrix arithmetic
- Second: **REIFIED** — The requirement is mechanically expressible using explicit snapshots and ordinary unary/binary relations; the adapter semantics are stated rather than hidden in an interpreted predicate.
- Proposed: **REIFIED** — The nine named signals are compared only to fixed zero/one values; typed constants and exact equality preserve the requirement.

**`LPC_full_reqts_and_vars.json:LPC:LPC_REACH_HOVER_16:79ba0711`**

- First: **OPAQUE** — 'within 16 ticks': metric bound (would need unrolling or counting)
- Second: **REIFIED** — The requirement is mechanically expressible using explicit snapshots and ordinary unary/binary relations; the adapter semantics are stated rather than hidden in an interpreted predicate.
- Proposed: **REIFIED** — Sixteen ticks is a fixed bound that the checked witness unrolls, including the exported finite-trace early-end rule.

**`LPC_full_reqts_and_vars.json:LPC:LPC_KIAS_0:79ba7c42`**

- First: **OPAQUE** — kias >= 0.0 numeric comparison
- Second: **NO** — The whole claim is a real-valued nonnegativity constraint; there is no independent qualitative content.
- Proposed: **NO** — The response is solely an interpreted numeric nonnegativity check.

**`LM_requirements.json:LM_requirements:TUI-003v3:0b8c7620`**

- First: **NO** — arithmetic equation
- Second: **OPAQUE** — The normalv3 guard is relational, but the response is a computed integration equation using multiplication and addition unavailable in v0.
- Proposed: **OPAQUE** — The normalv3 guard is independent Boolean content, while the integration equation remains an opaque numeric check.

**`LPC_full_reqts_and_vars.json:LPC:LPC_REACH_HOVER_13:79b76f00`**

- First: **OPAQUE** — 'within 13 ticks' metric bound
- Second: **REIFIED** — The requirement is mechanically expressible using explicit snapshots and ordinary unary/binary relations; the adapter semantics are stated rather than hidden in an interpreted predicate.
- Proposed: **REIFIED** — Thirteen ticks is a fixed bound that the checked witness unrolls, including the exported finite-trace early-end rule.

### Clover (11)

**`CloverBench/textbook_algo/convert_map_key`**

- First: **NO** — higher-order function parameter f and finite maps
- Second: **REIFIED** — The injective function and both maps can be expanded as single-valued binary graphs; the requires clause implies the two postconditions rather than being asserted as an unconditional fact.
- Proposed: **REIFIED** — A supplied function is represented by a total single-valued graph, and the injectivity precondition implies explicit map-domain and value postconditions.

**`CloverBench/textbook_algo/array_append`**

- First: **NO** — sequence concatenation equation
- Second: **REIFIED** — The contract appends one distinguished value and the invariant copies an ordered prefix; neither performs arithmetic on element values, so both admit an explicit position/cell encoding.
- Proposed: **REIFIED** — Appending one value becomes an extra final position and copied prefix; the implementation-only length addition does not require a numeric extension.

**`CloverBench/textbook_algo/array_copy`**

- First: **OPAQUE** — array contents via reified index/value relation, but index bounds/Length are numeric comparisons
- Second: **REIFIED** — The equal-length copy contract and prefix invariant use only equality and ordered index domains, so positions, cells, and loop-head snapshots can be expanded mechanically.
- Proposed: **REIFIED** — Explicit ordered positions, functional cells and loop-head snapshots preserve equal-length copying and the prefix invariant.

**`CloverBench/textbook_algo/swap_in_array`**

- First: **OPAQUE** — index comparisons; old() needs pre/post state reification
- Second: **REIFIED** — Bounds are exactly membership in the pre-state array domain; with functional before/after graphs the swap, unchanged domain, and frame condition are first-order relational constraints.
- Proposed: **REIFIED** — The checked pre/post cell graphs express domain membership, the two changed cells and the complete frame condition.

**`CloverBench/textbook_algo/seq_to_array`**

- First: **OPAQUE** — index bounds, lengths; fresh(a) heap predicate
- Second: **REIFIED** — With no loop invariants, the contract can be expanded into equal position domains, equal values at each position, functional cell graphs, and freshness of the returned object.
- Proposed: **REIFIED** — Equal position domains and pointwise functional values express the copy, with allocation-before facts expressing freshness.

**`CloverBench/textbook_algo/find`**

- First: **OPAQUE** — index order and -1 sentinel comparisons
- Second: **REIFIED** — The search uses only value equality, a strict position order, and a distinguished -1 sentinel; these are expanded directly along with the prefix invariant.
- Proposed: **REIFIED** — A distinguished sentinel and structural position order suffice for the first-match contract and prefix invariant.

**`CloverBench/textbook_algo/modify_2d_array`**

- First: **OPAQUE** — nested array index bounds and frame conditions with numeric comparisons
- Second: **REIFIED** — Outer references, stable inner-cell locations, pre/post values, bounds, the non-aliasing precondition, update, and frame condition can all be represented explicitly as relations.
- Proposed: **REIFIED** — The witness exposes outer references, inner locations, aliasing preconditions, changed values and unchanged-cell frames.

**`CloverBench/textbook_algo/remove_front`**

- First: **OPAQUE** — slice equality a[1..] == c[..] needs index successor arithmetic
- Second: **REIFIED** — Deleting the first position and shifting the remaining positions is an explicit order-preserving bijection; the slice equality and prefix invariant require no element arithmetic.
- Proposed: **REIFIED** — An explicit order-preserving bijection after deleting the first position implements the slice and index-shift invariant.

**`CloverBench/textbook_algo/linear_search1`**

- First: **OPAQUE** — index order comparisons
- Second: **REIFIED** — The contract and invariant use only equality lookup, strict prefix order, and the end boundary as the no-match result.
- Proposed: **REIFIED** — The end boundary serves as the no-match sentinel and ordinary order/equality expresses the first-match condition.

**`CloverBench/textbook_algo/rotate`**

- First: **NO** — index arithmetic (i+offset) % Length
- Second: **OPAQUE** — The pointwise correspondence skeleton is useful, but the defining source index is (i+offset) mod length, so an unexplained rotation relation would hide the essential semantics.
- Proposed: **OPAQUE** — The copy skeleton remains useful, but computing the shifted modulo index still needs arithmetic.

**`CloverBench/textbook_algo/linear_search3`**

- First: **OPAQUE** — P can be a unary predicate, but index order/bounds are numeric comparisons
- Second: **REIFIED** — The supplied predicate is a unary relation on values, while first-match and the invariants are explicit constraints over the ordered position graph.
- Proposed: **REIFIED** — For one invocation P is an explicit unary input relation, while ordered cells express the first match and all invariants.
