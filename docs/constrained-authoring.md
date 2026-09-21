# Constrained VE authoring

`ve.grammar` exports an environment-specific CFG without runtime dependencies.
`ve.authoring` checks and repairs injected proposals for SFT warm-up and coverage
audits. Neither component checks that a claim faithfully represents a requirement.
The gatekeeper is not part of RL rollouts: retrying until valid would change the
sampling distribution and hide invalid-output rates.

## Export and use

```python
from pathlib import Path
from ve.environment import Environment
from ve.grammar import export_grammar, structured_output_spec

env = Environment.from_json(Path("examples/environment.json").read_bytes())
grammar = export_grammar(env, dialect="lark", max_binder_depth=3)
spec = structured_output_spec(env, dialect="ebnf", max_binder_depth=3)
```

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-grammar
uv run python -m ve grammar --env examples/environment.json --dialect gbnf > /private/tmp/ve.gbnf
uv run python -m ve grammar --env examples/environment.json --dialect lark --wrapper
uv run python -m ve grammar --env examples/environment.json --dialect ebnf --spec
```

| Export | Entry rule | Consumer |
|---|---|---|
| `gbnf` | `root ::= ...` | llama.cpp grammar file / grammar request |
| `ebnf` | `root ::= ...` | XGrammar `Grammar.from_ebnf` / compiler; vLLM XGrammar backend |
| `lark` | `start: ...` | Lark; llguidance Lark compiler |

The GBNF and EBNF exports deliberately use the same common subset. Rule names
are generated identifiers; environment names occur only inside exact literals.
There is no ignored whitespace. Use the final period **and LF**, including on
the last statement. [llama.cpp GBNF](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md),
[XGrammar EBNF](https://xgrammar.mlc.ai/docs/latest/defining_structures/ebnf_grammar.html),
and [llguidance's Lark dialect](https://github.com/guidance-ai/llguidance/blob/main/docs/syntax.md)
are different input formats; a Lark grammar is not interchangeable with EBNF.

For current vLLM, pass an EBNF export as
`extra_body={"structured_outputs": {"grammar": grammar}}` to the client, or use
`StructuredOutputsParams(grammar=grammar)` in offline sampling. Select the
XGrammar backend in the server configuration. The old `guided_grammar` request
field was removed in vLLM 0.12.0. These are documented integration points, not a
claim that a vLLM server or GPU generation was tested here.
[vLLM structured outputs](https://docs.vllm.ai/en/latest/features/structured_outputs/)

## Bounds and guarantees

Both modes close the vocabulary over declared sorts, predicates, and constants;
enforce unary/binary predicate arity; restrict each constant to the appropriate
argument sort (and same-sort equality); preserve strict punctuation; and number
binders in preorder, resetting at each statement. In `mode="full"`, each term
also uses only an active variable of the required sort. A variable cannot escape
into a sibling scope, and previously consumed names cannot be reused.

`mode="syntax"` drops variable scope and variable-sort checks. All
`x0..x(max_binders-1)` are available as terms, even before binding or after leaving
scope. Constants remain sorted. This cheaper grammar intentionally accepts some
texts that `ve.parse` rejects. Always run the checker after generation.

There are two different bounds:

* `max_binder_depth` (default 3) bounds simultaneously nested binders.
* `max_binders` bounds the total binders in **one statement**, defaulting to
  `max_binder_depth`. Its finite variable alphabet is `x0..x(max_binders-1)`.

This distinction is required by the existing canonical printer, which uses
globally fresh preorder names within a statement. For example,
`(for every service x0, (true)) and (for every service x1, (true)).\n` has
depth 1 but two binders. Export with `max_binder_depth=1, max_binders=2` to admit
it. Depth alone cannot bound the number of canonical names: arbitrarily many
sibling scopes have depth 1. Thus completeness with the finite alphabet is
conditional on **both** bounds. We do not change canonicalization to recycle names.

Formula connectives and statement count remain recursive/unbounded. The ordinary
VE limits (64 KiB, 64 formula levels, 10,000 AST nodes) and Phase T's separate
six-statement limit are checked downstream. A completed CFG derivation can exceed
those resource budgets; full-mode well-typedness does not promise runtime
acceptance beyond them. Token truncation can also leave an unfinished derivation.
The grammar enforces form, scope, and sorts, not satisfaction or entailment.

## Construction cost

Full-mode formula states carry `(active name/sort context, next name, end name)`.
A binary connective splits the interval of consumed binder names between its
children; a quantifier consumes its first name and extends only its body's
context. Terms are shared per context and sort. Thus numbering across siblings
is enforced without leaking their bindings.

With `S` sorts and total bound `B`, each already-consumed name is either inactive
or active at one of `S` sorts. Without a tighter depth bound there are up to
`(S+1)^i` contexts at position `i`. A conservative formula-state bound is
`sum((B-i+1) * (S+1)^i for i in range(B+1))`; each state has up to `B+1` binary
splits plus vocabulary-dependent alternatives. This is exponential in `B`.
Syntax mode tracks only depth and the name interval: `O(D * B^2)` states and
`O(D * B^3)` connective alternatives, where `D=max_binder_depth+1`.

`max_rules=20000` caps generated VE production alternatives and raises
`ResourceLimit` before excessive expansion; wrapper overhead is constant. Lower
the binder bounds or choose syntax mode when the cap is reached. No partial or
silently weakened grammar is returned. Declaration insertion order does not
affect the export.

For `examples/environment.json` (two sorts), equal depth/total bounds produced:

| Bound | Full rule lines / bytes | Syntax rule lines / bytes |
|---|---:|---:|
| 0 | 4 / 201 | 4 / 201 |
| 1 | 10 / 1,001 | 9 / 1,087 |
| 2 | 31 / 4,123 | 15 / 2,826 |
| 3 | 99 / 14,748 | 25 / 6,159 |
| 4 | 312 / 49,616 | 40 / 11,620 |

These are Lark export sizes, not backend compilation timings. Reproduce by
calling `export_grammar` for each bound/mode and taking `len(g.splitlines())`
and `len(g.encode("utf-8"))`.

## VE plus explanation

`export_grammar(..., wrapper=True)` constrains a complete serialized JSON object:

```json
{"ve": "true.\n", "explanation": "Free text, including Unicode and JSON escapes."}
```

The key order and spaces shown above are fixed. The VE field uses canonical
JSON escaping (LF becomes a backslash followed by `n`) and the selected VE grammar; the explanation
is any JSON string, including empty text. The wrapper imposes no explanation
token limit; Phase T's 60-token limit must be enforced by its caller. Decode with
`json.loads`, then call `ve.parse(env, obj["ve"])`. Preserve the explanation
separately from the checked semantic artifact.

`structured_output_spec` returns `json_schema`, `grammar`, `dialect`, the
environment ID, and the bounds/mode. The `ve` schema property has an
`x-ve-grammar` annotation containing the **raw VE** grammar. This annotation is
informative, not a standard JSON Schema constraint or a provider request shape.
Passing only that schema does not constrain the VE field. The sibling `grammar`
constrains the whole JSON object and is what a CFG-capable backend should receive.
This avoids requiring backend-specific nested-grammar schema extensions.

When the serving path cannot combine the two fields, use two calls: generate
raw VE with the CFG and validate it; then request only an explanation conditional
on that fixed VE, and assemble the JSON in application code. If a serving path
offers only JSON Schema and no CFG support, its first call cannot guarantee VE
validity: use the gatekeeper during warm-up/audit or choose a CFG-capable decoder.
Do not replace recursive VE with a purported equivalent flat regular expression.

## Gatekeeper API

```python
from ve.authoring import gatekeep

proposals = iter(["true.", "true.\n"])
result = gatekeep(env, lambda request: next(proposals), max_rounds=3)
assert [r.accepted for r in result.rounds] == [False, True]
assert result.canonical_text == "true.\n"
```

The injected `propose(AuthoringRequest) -> str` receives a one-based round number,
previous raw text, and the previous diagnostic. Diagnostics expose the existing
stable `VEError.code`, message, span, optional path, and a short `repair_hint`.
Syntax/name-resolution locations come from the parser. The existing checker may
locate a type error to the whole document; errors before a cursor exists use
`Span(0, 0, 1, 1)`. No precise offending-token location is invented.

Acceptance requires both parsing/checking and a canonical rendering within the
runtime limits. A canonical-render resource error is returned as repair feedback.
The loop stops on acceptance or after `max_rounds`. Its result preserves every
raw proposal and decision, checked AST, canonical text, and the final status.
Valid noncanonical binder names are accepted; `canonical_text` exposes their
canonical spelling without changing the logged proposal. Provider exceptions and
non-string returns and invalid environments fail as caller errors, not VE rejections. The callable
owns model invocation; tests inject deterministic functions and make no model calls.

For an audit, aggregate `rounds[n].accepted` with the count of runs that reached
round `n` as the conditional denominator, and separately report cumulative
acceptance over **all** starting runs. `result.acceptance_rate` is just accepted
attempts / attempted rounds within that one run, not a model success-rate estimate.

## Verification

The default dev dependencies include Lark but no decoding backend. Tests sample
actual compiled Lark productions in both directions against the VE implementation.
The test-only syntax parser reuses `_Parser` with term name resolution disabled:
the production parser has no separate public syntax-only stage. Full-mode tests
use the public parser/checker and compare the canonical printer's bytes.

The acceptance audit uses two fixed-seed batches of 200 derivations, limited to
derivation height 18, plus deterministic Hypothesis runs. No failing generated
source was removed from a denominator:

| Direction / obligation | Accepted / tested | Rate |
|---|---:|---:|
| Full CFG derivation → parser/checker and canonical reprint | 200 / 200 | 100% |
| Syntax CFG derivation → syntax stage | 200 / 200 | 100% |
| Existing well-typed AST strategy → Lark full grammar | 100 / 100 | 100% |
| Recursive two-sort AST strategy → Lark full grammar | 100 / 100 | 100% |

The existing strategy filters out formulas exceeding the declared total binder
bound before testing. Hypothesis generation-invalid cases (including strategy
overruns) are reported separately by `--hypothesis-show-statistics`; they are not
grammar rejections. These rates measure this bounded software audit, not model
generation validity, performance, or a proof of correctness.

Backend smoke tests optionally compile Lark/GBNF with llguidance 1.8.0 and EBNF
with XGrammar 0.2.7, including the wrapper. The XGrammar matcher checks scope/type
rejections and Unicode/escaped explanations using a byte vocabulary without a
model. Native llama.cpp and an actual vLLM generation run have not been tested.

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-grammar
UV_PROJECT_ENVIRONMENT=/private/tmp/ve-grammar-py312 uv run --python 3.12 pytest
uv run --python 3.14 pytest
UV_PROJECT_ENVIRONMENT=/private/tmp/ve-grammar-py312 uv run --python 3.12 \
  --with xgrammar==0.2.7 --with llguidance==1.8.0 pytest -q tests/test_grammar_backends.py
uv run --python 3.14 pytest tests/test_grammar.py --hypothesis-show-statistics
uv build
```

Python 3.12.13 runs the package and tests without language-code changes. The
package requirement is now `>=3.12`. The wheel is
`dist/verifiable_english-0.1.0-py3-none-any.whl`; Lark and the decoding backends
are not runtime dependencies.

Final local verification on 2026-09-21: the complete suite with the optional
backend packages passed **144 tests on CPython 3.12.13**. The default dev suite
passed **142 tests on CPython 3.14.6**, with the two optional-backend tests skipped.
Both Hypothesis grammar properties had 100 passing and zero failing cases;
generation-invalid counts were 2 (existing strategy) and 13 (mixed strategy).
`uv build` produced the wheel and source distribution. An isolated Python 3.12
installation of that wheel imported both new modules, exported a grammar and
wrapper spec, and accepted an injected gatekeeper proposal; wheel metadata has
`Requires-Python: >=3.12` and no runtime dependencies.
