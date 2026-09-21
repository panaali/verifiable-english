# Views cross-review resolution

This records the reproductions in `manage-agents/review-views.md`, plus the
requested follow-up checks. This historical report covers `ve.ace-explicit` version 2;
strict canonical bytes and the AST/wire semantics are unchanged. See the
[version-3 polish report](views-polish-report.md) for the current rendering policy.

## Exact reproduction outcomes

| Review reproduction | Outcome after this change | Regression |
|---|---|---|
| `owns(person,service)` → `{0} is owned by {1}` | Rejected; strict `owns` atom, original argument order; `BINARY_AUXILIARY` and `BINARY_CONVERSE` | `test_review_template_reproductions_fall_back_and_lint` |
| `{0} belongs to {1}` | Rejected; `BINARY_CONVERSE` | Same |
| `{0} lacks {1}` | Rejected; `LOGICAL_WORD` | Same |
| `owns` → `{0} audits carefully {1}` with declared `audits` | Rejected; word-level `SYMBOL_COLLISION` | Same |
| `deployed` → `{0} is undeployed` | Rejected; `NEGATED_HEAD` | Same |
| `deployed` → `{0} is reviewed already` | Rejected; `SYMBOL_COLLISION` and `UNARY_MODIFIER` | Same |
| Sort nouns `x` and `service x` | Rejected; `VARIABLE_TOKEN`, strict sort identifier | `test_review_variable_sort_nouns_rejected` |
| Sort `service` → `owner`, `person` → `asset` | Rejected if the noun is another declared sort identifier/noun. Arbitrary noncolliding aliases still render, but raw mappings are now exposed identically to every cell in the required legend. This semantic alias attack is **not claimed to be eliminated by linting**. | `test_review_sort_aliases_remain_visible_and_declared_collisions_reject` |
| Reordered/missing/repeated placeholders; parentheses; newlines; capitals; double spaces; format specs; `{0.__class__}`; `and`; bare `is`; duplicate templates; another predicate's strict form | Still rejected with strict fallback, now with stable lint codes | `test_review_template_reproductions_fall_back_and_lint`, `test_template_head_and_identifier_collisions_across_all_categories` |
| Two sorts, four binary + three unary predicates, `forall service / exists person` versus `exists person / forall service` | `Found` within default 10,000-model / 1,000,000-evaluation budgets, using `nonvacuous_for=a` to exclude the trivial empty-domain witness. Five-predicate variant also `Found`. Both take 23 candidate models / 264 evaluations in the committed fixture; used `owns` has two diagonal pairs and every unused relation is empty. | `test_review_quantifier_swap_found_with_default_budgets` |
| `forall s (not dep(s) or rev(s))` accepts a model with no deployed service as non-vacuous | Fails to reproduce with `semantic_nonvacuity=True`: guard `dep(s)` must have a witness. With a premise forcing `dep` empty, both search APIs return filtered `NotFound`; legacy mode remains explicit and unchanged. | `test_review_clause_nonvacuity_excludes_empty_guard_relation` |
| CLI `InvalidInput` and `ResourceLimit` both exit 2 | Fixed: invalid 2, resource 4, violated 1, bounded not-found 3 | `test_invalid_input_and_both_resource_limit_paths_have_distinct_exit_codes` |
| Different view size limits; natural-only capitalization; natural formula-only final period | Fixed: all use 65,536 UTF-8 bytes, preserve lexical case, and omit formula punctuation / append document period + LF | `test_same_real_output_limit_in_all_views`, `test_four_views_exact_example_and_legacy_entry_points` |
| Length confounded with view | Added per-item/per-view character and token-ish measurement, with optional identical vocabulary legend. This measures the confound; it does not remove it. | `test_per_item_view_length_covariates_measure_actual_text_and_optional_legend` |

The quantifier-swap model is checked by the independent public evaluator in the
test. Exhaustiveness and sparse enumeration order are checked on tiny complete
interpretation sets. Clause-guard mode is compared with implication guards over
all small interpretations of `dep` and `rev`; tests also cover jointly impossible
guards, separate occurrences, hidden branches, existential-only exclusions,
shared budgets, and both search APIs. Existing random injectivity and parser/
printer properties remain part of the complete test suite.

## Reproduce

From the `codex/views` worktree:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-views uv run pytest -q
UV_CACHE_DIR=/private/tmp/ve-uv-cache-views uv run pytest -q tests/test_views.py tests/test_search_options.py tests/test_cli.py -k review
```

To reproduce the search work counts:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-views uv run python - <<'PY'
import runpy
from ve import Binary, Exists, Forall, Var, find_distinguishing_model
fixture = runpy.run_path('tests/test_search_options.py')['review_search_environment']
a = Forall('service', Exists('person', Binary('owns', Var(0), Var(1))))
b = Exists('person', Forall('service', Binary('owns', Var(1), Var(0))))
for count in (5, 7):
    result = find_distinguishing_model(fixture(count), a, b, nonvacuous_for=a)
    print(count, result.status, result.models_checked, result.evaluations)
PY
```

Expected lines: `5 Found 23 264` and `7 Found 23 264`.

## Scientific limits

Templates, sort nouns, and descriptions remain trusted vocabulary data. The
linter is a conservative heuristic, not a proof; it can reject truthful phrases
and cannot detect every semantic lie. When an attacker authors vocabulary, the
required **identical legend** is the defence against unequal raw identity and
argument-order information. Use `ve.printer.render_cell` to include it automatically; the low-level
`render` API still returns claim text alone. The legend does not prove
that judges will interpret or scrutinize it correctly.

Semantic non-vacuity checks the documented implication and clause guards; it is
not arbitrary equivalence-invariant non-vacuity analysis. In particular, the
current `ve/search.py` recognizes explicit implication antecedents and maximal
`Or` clauses under a universal, requiring the positive bodies of negated
disjuncts to hold jointly at one assignment. It visits hidden branches and keeps
guard occurrences separate, but does **not** normalize De Morgan forms such as
`forall s. not (dep(s) and not rev(s))`, double negation, or distributive Boolean
variants before collecting guards. Item 6 of the polish request requires a
`ve/search.py` scope exception; no such change is included in the rendering-only
patch. Do not describe current semantic mode as covering these equivalents. Bounded search remains
exponential in **used** relation atoms and may still return `ResourceLimit`.
Token-ish counts are not real tokenizer counts, and common explicit bracketing
does not establish transfer to fluent ACE-style prose.
