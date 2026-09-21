# Verifiable English

An English-like language for human-inspectable, machine-checkable claims in AI oversight.

**Stage:** experimental Python v0 core, argument layer, constrained grammars, and Lean reference proofs implemented; full verification and oversight experiments are pending.

Run `uv sync`, then `uv run python -m pytest`. The package requires Python 3.12 or later.
For a worked inventory, run:

```sh
uv run python -m ve evaluate --env examples/environment.json --model examples/model.json examples/requirements.ve
uv run python -m ve render --env examples/environment.json --view ve_natural examples/requirements.ve
uv run python -m ve render --env examples/environment.json --view ve_fluent examples/requirements.ve
uv run python -m ve countermodel --env examples/environment.json --premises examples/premise.ve --conclusion examples/conclusion.ve
```

See [six examples across all five views with the shared legend](docs/fluent-examples.md)
and [the implementation/API guide](docs/implementation.md) for encodings, FOL import,
resource outcomes, and the explicit trust boundary. A successful finite evaluation
does not certify entailment, intent, or empirical grounding.

The [Lean reference](lean/README.md) now proves soundness of the full data-only
tableau certificate checker, including quantifiers over possibly empty sorts and
equality. Accepted certificates entail their exact supplied conclusions; the
named graph theorem composes accepted edges without an abstract certificate
soundness assumption. The conformance run accepts **732/732** Python-produced
certificates and rejects **150/150** forgeries; see the
[reproducible report](conformance/certificates-report.json).

Use `lean/.lake/build/bin/ve_conformance check-certificate query.json` after
`(cd lean && lake build)`. A query contains `id`, `environment`, ordered AST
`premises`, one AST `conclusion`, and the Python-produced `certificate`.
Acceptance is the response's `valid: true`. On this path Python is untrusted
search; the remaining trust base includes Lean's kernel/compiler/runtime,
JSON/AST/certificate decoding, serialization/hash binding, IO and faithful
display. The default Python argument API still uses Python replay. No theorem
verifies empirical premises, the JSON boundary or Python-to-Lean refinement;
the overall assurance level remains experimental.

VE aims to support AI alignment and scalable oversight. Its core is **human sign-off on precise claims, plus checked composition of those claims**: people inspect what an agent claims, and a checker verifies that deductions use those exact meanings and explicit assumptions. If an agent must prove that its work meets a specification, the supervisor reviews the specification and the remaining premises, not the work, so review cost need not grow with the agent's capability. This is a design argument, not a result.

Debate is the first protocol intended to use this core. Sign-off fixes the question, checked deductions confine the debate to the remaining premises, and finite countermodels give a critic objections the judge can verify. VE does not check premise evidence or vocabulary descriptions, where the hard part of debate remains. The prototype combines a typed claim language, canonical English rendering, and checked argument composition.

The central question is whether people can reliably detect incorrect specifications and mismatched evidence in a VE presentation, beyond a structured formal interface using the same checker. Formal verification establishes consequences of the stated assumptions; human intent, empirical evidence, and the usefulness of the oversight protocol still need evaluation.

The current recommendation is a small study of **human review of requirements and evidence**, before building the full verified implementation. Test formal commitments, readable presentation, and debate separately. A useful review interface may survive even if a new language or multi-round debate adds no benefit.

- [Critical review, source checks, and recommended first study](docs/research-review.md)
- [Architecture, rationale, and alternatives](docs/architecture-and-design.md)
- [v0 language specification](docs/spec/v0-language.md)
- [Debate claims and argument checking](docs/spec/debate-protocol.md)
- [Verification contracts and status labels](docs/spec/verification-contract.md)
- [Roadmap and acceptance criteria](docs/roadmap.md)
- [Work plan and remaining tasks](docs/plan.md)

The [semantic oracle and attack validator](docs/oracle.md) return checked proofs,
distinguishing models, or explicit uncertainty, with a JSONL validation CLI and
a reproducible FO2 template audit.
