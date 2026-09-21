# Experimental Python VE v0 core

The implementation supports exactly `ve.core@0`, `relational-fol@0`, and
`ve-v0-draft-2026-09-20`. It implements the draft semantics; it does not establish
the pending theorems in [the verification contract](spec/verification-contract.md).
`uv.lock` pins the test/build dependencies. There are no third-party runtime
dependencies. Use Python 3.14 and `uv sync`; run `uv run python -m pytest`.

## Python API

```python
from pathlib import Path
from ve import Environment, FiniteModel, parse, print_document, evaluate
from ve import check, find_countermodel, check_countermodel

env = Environment.from_json(Path("examples/environment.json").read_bytes())
source = Path("examples/requirements.ve").read_bytes()
document = parse(env, source)
model = FiniteModel.from_json(env, Path("examples/model.json").read_bytes())
assert evaluate(env, document, model).status == "Satisfied"
print(print_document(env, document))
record = check(env, source, model, candidate_ast=document)

premises = parse(env, Path("examples/premise.ve").read_bytes()).formulas
conclusion = parse(env, Path("examples/conclusion.ve").read_bytes()).formulas[0]
search = find_countermodel(env, premises, conclusion, max_domain_size=2)
if search.status == "Found":
    assert check_countermodel(env, premises, conclusion, search.model).valid
```

`ve.ast` exposes frozen raw constructors: `Var(index)`, `Const(name)`, `Top`,
`Bottom`, `Unary(predicate, term)`, `Binary(predicate, left, right)`, `Eq`, `Not`,
`And`, `Or`, `Implies`, `Forall(sort, body)`, and `Exists(sort, body)`.
`Document(formulas)` defensively copies its ordered, nonempty formula sequence
(nonemptiness is checked at validation). Variables use nearest-first de Bruijn
indices. The runtime uses **extrinsic typing**: constructors are convenient raw
syntax, and `check_formula`/`check_document` establish closure, scope, sort and
arity correctness under the supplied environment. Public semantic consumers
validate inputs themselves. Python annotations alone are not evidence of typing.
The Python interpreter and in-process code are trusted; arbitrary malicious
Python execution is outside this data-only interface's threat model.

Environment and model factories validate all required fields and make defensive,
immutable copies. Empty sorts are permitted unless a constant inhabits them.
Constants may alias. Equal local identifiers in different sorts are distinct
entities. Model membership is closed-world only inside the explicitly complete
supplied inventory; this makes no assertion about real-world completeness.

`parse_with_metadata` retains original source names and spans separately from
semantic nodes. Its metadata documents its ordering. `canonicalize` changes only
binder names and grammar serialization; `is_canonical` compares exact bytes.
There is no source normalization before checking: CRLF, tabs, comments, missing
final LF, implicit grouping and unsupported operators fail.

## Interchange and identity

Use the [specified wire shapes](spec/v0-language.md) for environments and models.
Use `ve.ast.document_from_data`, `document_to_data`, and `doc_from_json` for the
indexed AST. Documents are arrays of formula arrays; single formulas are tagged
arrays. Invalid tags, arities, Boolean/negative indices, free indices and sort
mismatches fail. Source remains separate from AST; `check(..., candidate_ast=...)`
rejects an individually valid AST that does not match the parsed source.

`ve.wire.loads_json` rejects duplicate object keys before overwrite, lone
surrogates, floats, null, excessive size/depth, and integers outside `[0, 2^53-1]`.
`canonical_json` implements the restricted RFC 8785 subset: UTF-16 key order,
minimal JSON string escaping, integer serialization, no insignificant whitespace.
Model domain and relation sets are sorted before identity; duplicates are errors.
Formula order, tuple argument order, and predicate signatures are never sorted.

`source_id` binds exact submitted bytes. `Environment.environment_id` binds the
complete vocabulary including descriptions. `meaning_id(env, document)` binds
the entire document array; `meaning_id(env, formula)` binds one formula array.
These are deliberately different preimages. The argument layer should use the
single-formula variant consistently for claims and must require one statement.
`FiniteModel.model_id` binds the normalized inventory and its environment.
All hashes use the specified domain-separated SHA-256 preimages. Hashes identify
artifacts; they do not certify semantic equivalence or truth.
Diagnostic result records use ordinary JSON, including `null` for an unavailable
Boolean or absent search witness. They are not semantic input packages or new
certificate encodings; the argument-layer wire contract remains a separate task.

## FOL rendering

`render_fol(env, value, view="canonical" | "natural")` accepts a `Document`, an
indexed document array, or the following explicit named-FOL object. This is an
AST API, not an arbitrary FOL string parser. Adapters must handle dataset syntax
and declare all sorts, constants, and predicates themselves; unsupported items
must remain visible in coverage accounting.

```python
from ve import render_fol

named = {"formulas": [{
    "op": "forall", "sort": "service", "variable": "s", "body": {
        "op": "exists", "sort": "person", "variable": "p", "body": {
            "op": "binary", "predicate": "owns",
            "left": {"var": "p"}, "right": {"var": "s"}
        }
    }
}]}
strict_text = render_fol(env, named)
natural_view = render_fol(env, named, view="natural")
print(natural_view.text)
```

Named formulas use the same tags as indexed formulas in an `op` field:
`top`/`bottom`; `unary` with `predicate, term`; `binary` with `predicate, left,
right`; `eq` with `left, right`; `not` with `body`; binary connectives with
`left, right`; quantifiers with `sort, variable, body`. Terms have exactly one
`var` or `const` field. Unknown fields and missing operands fail.

The natural view is a conservative ACE-style experimental display, **not an ACE
parser or an independently verified ACE translation**. It returns text, renderer
name/version, environment ID and meaning ID. Every constructor is rendered with
explicit scope; existential witnesses remain nested under their dependencies,
disjunction explicitly permits both, and no statement or antecedent is omitted.
No LLM paraphrasing, vocabulary definitions, inference, quantifier reordering,
or implicit existence assumptions occur. Read-only natural text is not accepted
as strict VE. Its readability and semantic fidelity still require review and
formal correspondence evidence before higher assurance is claimed.

## Evaluation, search, and the next argument layer

`evaluate` returns `Satisfied`, `Violated`, or `ResourceLimit`, a Boolean or no
result, work count, and explanatory bindings. Explanations explicitly distinguish
empty-domain universal satisfaction, lack of existential witnesses, and material
implication with a false antecedent. Binding records contain de Bruijn index,
sort, and local ID rather than ambiguous untyped names. Evaluation short-circuits;
an unvisited branch is not evidence about that branch. Work exhaustion is never
reported as a false claim. A separate `max_trace_nodes` budget defaults to 10,000;
exhausting it also returns `ResourceLimit`, even when formula-work budget remains.

`find_countermodel` enumerates finite domains, constant denotations (including
aliases), and relation subsets within explicit size/model/work bounds. It is a
small exponential search tool intended for mechanism examples, not a scalable
general-purpose solver. `Found` supplies a witness; `NotFound` means only that
the bounded enumeration finished; `ResourceLimit` means the search stopped
early. None supplies positive entailment evidence. The language has invalid
inferences with no finite countermodels at all.

`check_countermodel` is the independent trusted witness-checking entry point.
It checks every premise and the exact conclusion and binds the result to the
environment, model, ordered premise meaning IDs and conclusion meaning ID.
This can support a future `gap` finding; a gap does not make the conclusion
false in reality. No `follows`, proof-certificate checker, graph composition, or
leaf-assumption discharge is implemented in this task. These should consume the
same closed checked ASTs and artifact IDs, without promoting search exhaustion
or finite satisfaction into entailment.

## CLI and operational outcomes

`python -m ve --help` lists `parse`, `format`, `render`, `evaluate`, `check`,
`import-fol`, and `countermodel`. Every command takes `--env`; source `-` reads
stdin where applicable. Text inputs are read as bytes so newline conversion
cannot conceal malformed input. The examples in the README are executable.

`parse` emits an acceptance record; `format` emits canonical source. `check`
optionally takes `--model` and `--candidate-ast`; `evaluate` requires a model.
Records explicitly retain `assurance: experimental`, `intent: unconfirmed`, and
`proof: not_checked`. Exit 0 means successful output or a found countermodel;
exit 1 means finite violation or bounded countermodel absence; exit 2 means
invalid input or resource exhaustion. Read the distinct JSON status fields.

The v0 envelope bounds source bytes, JSON package size, AST depth/nodes,
vocabulary size, model entities/tuples, explanatory trace size, and formula-node evaluations. JSON
nesting additionally has a 256-level decoding guard. Search is separately
bounded; search also stops if a candidate domain vector requires more than
100,000 possible relation atoms. Host cancellation remains a process interruption,
not a logical finding.

## Trust and tests

Trusted for the experimental acceptance/evaluation path: Python and its standard
library/runtime; strict byte and JSON decoding; environment/model validators;
parser and name resolver; AST type/scope checker; finite evaluator; canonical
serializer, SHA-256 binding and acceptance-record code; printer and displayed
rendering fidelity. FOL adapters additionally belong to the trust boundary when
dataset claims are about their source syntax. The CLI/file-I/O boundary is
trusted to supply and display the checked objects.

Search has no authority to assert validity: found models are checked separately.
There are no external solver or model calls in the core, no proof replay, no
hidden domain nonemptiness or unique-name axioms, and no empirical evidence
verification. All metatheory obligations P1–P11 remain pending. Property tests
are empirical evidence, not proofs of grammar uniqueness or correspondence.

The tests include spec examples, malformed packages, scope/type errors, source
substitution and environment changes, all logical constructors, vacuity,
constant aliasing, countermodel subset enumeration, operational limits, and CLI
exit codes. Hypothesis tests compare parser/printer and wire round trips and a
separately written finite denotation for generated formulas. This is a development
suite, not the independently frozen 240-case corpus proposed in the roadmap,
and it is not evidence for any oversight or readability benefit.

Validation on September 21, 2026: `uv run --frozen python -m pytest -q` passed
90 tests; `uv build` produced both source and wheel distributions; importing the
built wheel in isolated Python and checking the worked inventory succeeded.
In the restricted worker environment these `uv` commands used
`UV_CACHE_DIR=/private/tmp/ve-uv-cache`. The ordinary `uv` cache is outside that
worker's writable paths; direct `.venv/bin/python -m pytest` also passed.
