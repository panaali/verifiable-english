# Verifiable English

An English-like language for human-inspectable, machine-checkable claims in AI oversight.

**Stage:** first draft; implementation and proofs are pending.

VE aims to support AI alignment and scalable oversight, especially debate: people should be able to inspect what an agent claims, while a checker verifies that deductions use those exact meanings and explicit assumptions.

The first research target is **meaning changes during debate**: reinterpreting a requirement, changing quantifier scope, or using the same term differently in separate argument branches. The prototype combines a typed claim language, canonical English rendering, and checked argument composition. Finite examples and counterexamples help people inspect the claims.

The central question is whether VE reduces successful deception at a fixed review budget, beyond debate with cross-examination, shared definitions, and structured formal claims using the same checker. Formal verification establishes consequences of the stated assumptions; human intent, empirical evidence, and the usefulness of the oversight protocol still need evaluation.

The current recommendation is a small study of **human review of requirements and evidence**, before building the full verified implementation. Test formal commitments, readable presentation, and debate separately. A useful review interface may survive even if a new language or multi-round debate adds no benefit.

- [Critical review, source checks, and recommended first study](docs/research-review.md)
- [Architecture, rationale, and alternatives](docs/architecture-and-design.md)
- [v0 language specification](docs/spec/v0-language.md)
- [Debate claims and argument checking](docs/spec/debate-protocol.md)
- [Verification contracts and status labels](docs/spec/verification-contract.md)
- [Roadmap and acceptance criteria](docs/roadmap.md)
- [Work plan and remaining tasks](docs/plan.md)
