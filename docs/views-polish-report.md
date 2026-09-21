BRANCH

`codex/views-polish`, based on `ve-integration` at `541e744`.

SUMMARY

- Tightened template vocabulary, length, and sort-noun checks; documented lexical limits and mandatory legends.
- All five views default to `per_statement` and support `per_document`; fluent letters are distinct and avoid A/I/O and identifiers.
- Replaced eight-verb negative validation with regular inflection rules plus explicit spelling exceptions; preserved explicit fallback.
- Added `ve.printer.render_cell`, CLI legend/naming options, `ve.fluent.contraction_stats`, and JSONL length measurement.
- Updated inverse tests, six-example documentation, and a committed six-item JSONL fixture; item 6 awaits a file-scope exception.

VERIFY

From this worktree, with `UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent`:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent
uv run pytest -q
uv run pytest -q -s tests/test_views_polish.py -k seeded_random
uv run python -m ve view-lengths --env examples/fluent/environment.json \
  --field claim --source-format ve tests/data/fluent-items.jsonl
uv run python -m ve render --env examples/fluent/environment.json \
  --view ve_fluent --with-legend --naming per_statement examples/fluent/examples.ve
git diff --check
```

Complete suite: **565 passed, 2 skipped in 88.36s**. The skips are the optional
`llguidance` and `xgrammar` backends. All five-view inverse checks, new lexical
and naming regressions, CLI checks, JSONL measurements, and existing semantic/
Lean checks pass. The complete-cell CLI invocation and whitespace check pass.

The seeded sample is 2,000 draws without deduplication, depth uniformly selected
from 1 through 6, using `tests.test_views._random_formula` and the declared
negative vocabulary from `tests.test_fluent.negative_vocabulary`. Exact results
are committed in [views-polish-sample.json](views-polish-sample.json).

| Negation form | Count | Share of all 478 negations |
|---|---:|---:|
| Validated declared predicate negative ("whitelisted") | 48 | 10.04% |
| Explicit `it is false that` fallback | 359 | 75.10% |
| Typed inequality | 71 | 14.85% |

Of 113 predicate-atom negations, 48 (42.48%) use validated negatives and 65
(57.52%) use fallback. The other 294 fallback occurrences negate non-atomic
formulas or truth constants. These are occurrence counts, including nested
negations; none are dropped. The generator has 408 universal groups and only
5 eligible guards, all relative; zero structural guards. This sparse guard
coverage is supplemented by a deterministic test with 2 relative and 3
structural guards (2 of those spell `such that (both ...)`). These figures
describe this generator and fixed vocabulary, not English verb coverage or
human readability. Expanded regular/irregular morphology is checked separately
in atomic and relative-clause inverse tests.

The committed JSONL fixture is the six existing `examples/fluent/examples.ve`
statements serialized as individual real input records, with IDs and environment
identity. Measurements below include the full shared legend once per item:

| View | Items | Total characters | Total token-ish units |
|---|---:|---:|---:|
| `fol_symbols` | 6 | 14,537 | 3,608 |
| `fol_keywords` | 6 | 14,631 | 3,608 |
| `ve_strict` | 6 | 14,689 | 3,596 |
| `ve_natural` | 6 | 14,800 | 3,626 |
| `ve_fluent` | 6 | 14,662 | 3,545 |

GAPS

**Item 6 remains unimplemented because `ve/search.py` is outside the explicitly
allowed files.** A scope exception was requested; none had arrived when this
report was prepared. Current coverage is documented in the
[review resolution](views-review-resolution.md). The unfixed reproduction is:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python - <<'PY'
import sys
sys.path.insert(0, 'tests')
from test_search_options import review_search_environment
from ve import Forall, Unary, Var, Not, And, Bottom, find_countermodel
p, q = Unary('dep', Var(0)), Unary('rev', Var(0))
guard = Forall('service', Not(And(p, Not(q))))
empty_dep = Forall('service', Not(p))
result = find_countermodel(review_search_environment(), (empty_dep,), Bottom(),
                          nonvacuous_for=guard, semantic_nonvacuity=True)
print(result.status, result.model.relations['dep'])
PY
```

Observed: `Found frozenset()`; the requested normalized guard check should
instead filter that empty guard and return `NotFound`. Both public search APIs
share `_nonvacuous` in `ve/search.py`; changing only the CLI would leave library
callers inconsistent. No runtime patching or renderer-side search interception
is introduced.

New helpers are public in `ve.printer` and `ve.fluent`; adding package-root
re-exports would require editing the excluded `ve/__init__.py`. The legacy
example generator's introductory sentence still states the old naming policy;
the documentation gives a corrected regeneration command and verifies it.
Optional `llguidance` and `xgrammar` backend checks are unavailable locally.
No external experiment dataset was present; file measurement is verified on
the committed six-item fixture and temporary AST/VE JSONL files.

PLAN CHANGES

None. Complete item 6 in `ve/search.py` once its scope exception is authorized.
