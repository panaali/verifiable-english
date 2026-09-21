# Verifiable English

An English-like language for human-inspectable, machine-checkable claims in AI oversight.

**Stage:** experimental Python v0 core implemented and tested; formal proofs and oversight experiments are pending.

Run `uv sync`, then `uv run python -m pytest`. The package requires Python 3.14.
For a worked inventory, run:

```sh
uv run python -m ve evaluate --env examples/environment.json --model examples/model.json examples/requirements.ve
uv run python -m ve render --env examples/environment.json --view natural examples/requirements.ve
uv run python -m ve countermodel --env examples/environment.json --premises examples/premise.ve --conclusion examples/conclusion.ve
```

See [the implementation/API guide](docs/implementation.md) for encodings, FOL import,
resource outcomes, and the explicit trust boundary. A successful finite evaluation
does not certify entailment, intent, or empirical grounding.

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
