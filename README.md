# Verifiable English

**[Onboarding guide](https://claude.ai/artifact/3vLxUDY9QeL3xUTLHUBBjy)**

**Verifiable English (VE) is a controlled subset of English, built on the Lean proof assistant, for writing mechanically checkable claims and arguments.** You write readable English; VE checks whether conclusions follow from the stated assumptions.

VE is built for AI oversight: helping people understand and verify what an AI system claims, promises, or proposes to do. Today it is a research implementation with a command-line interface, Python APIs, a Lean checker, and worked applications—not a finished general-purpose document editor.

[Start with an example](#a-small-example) · [Try it locally](#try-it-locally) · [Documentation](#where-to-go-next) · [Vision](VISION.md)

## Why build this?

An AI can produce a persuasive explanation that contains an invalid step, quietly changes a definition, or proves a weaker claim than the one requested. Reviewing all of its reasoning can be harder than solving the original problem.

VE explores a different division of work: the author or AI supplies precise claims and supporting proofs; a mechanical checker checks the deductions; a person reviews the meanings, assumptions, and evidence that remain. The English presentation is intended to make that review accessible without requiring the reviewer to read symbolic logic.

The long-term vision is to apply this to policies, contracts, scientific arguments, and agent actions. An agent could submit a proposed action together with a checked proof that it meets an approved policy. This is a research goal, not a deployed enforcement system. See the [vision](VISION.md) and [oversight rationale](design/crypto-inspired-oversight.md).

## A small example

> Every reviewed service is safe. The API is reviewed. Therefore the API is safe.

**This is what a user or AI agent writes directly into VE, in natural English.** With the [declared vocabulary](examples/assist/environment.json) and [English names](examples/assist/environment.english.json), VE reads the sentences, identifies the first two as assumptions, and checks that the conclusion follows. The [executable example](tests/test_natural.py) checks both the English reading and the deduction.

Change “The API is reviewed” to “The API is deployed,” and the conclusion no longer follows: the rules say nothing about whether deployed services are safe. VE can expose that missing step instead of accepting a plausible-sounding explanation.

You can also write:

> Every deployed service has an owner.

This allows different owners for different services. It does not silently become the stronger claim that one person owns every service. VE keeps that distinction precise while letting you read ordinary sentences.

The guarantee is about the reasoning: **if the assumptions hold, the checked conclusion holds.** Someone still has to establish that the API really was reviewed and that review is sufficient for safety. VE makes those assumptions visible; it does not turn them into facts.

## What you can do now

The following capabilities are present in the October 20, 2026 code snapshot. Features have explicit scopes, and some combinations are rejected; they are not a promise that arbitrary prose can be formalised automatically.

| Task | What VE provides | Start here |
| --- | --- | --- |
| Write and inspect precise claims | Declared vocabulary, parsing and type checking, definitions, and several English/logical renderings | [Small examples](examples/), [rendering guide](docs/fluent-examples.md) |
| Check reasoning | Finite-model evaluation, checked proof certificates and argument graphs, and counterexamples to invalid inferences | [Python API](docs/implementation.md), [proof results](lean/METATHEORY.md) |
| Review a document | Source-span accounting, explicit assumptions and unsupported passages, and alternative readings rather than silently choosing an interpretation | [Document format](docs/spec/document.md), [safety-framework case](usecases/safety-framework/README.md) |
| Express policy rules | Obligations, permissions, prohibitions, exceptions and priorities; worked checks for conflicts and uncovered situations | [Agent-policy case](usecases/agent-policy/README.md), [norms specification](docs/spec/norms.md) |
| Work with exact quantities | Supported decimals, unit tags, dates, comparisons and bounded counting; staged reasoning in an eligibility example | [Quantity status](docs/W6A-STATUS.md), [eligibility case](usecases/eligibility/README.md) |
| Build a formalisation step by step | `ve assist` records source sentences, freezes target claims, checks proposed steps, and reports missing support | [Assisted-authoring guide](docs/assisted-formalisation.md) |

These examples demonstrate particular implemented routes. They do not establish general translation accuracy, legal correctness, or improved human oversight. The eligibility case, for example, records translation errors that its initial tests missed because the translation and answer key shared assumptions.

## Current status and limits

VE has grown beyond its original first-order-logic prototype. Lean owns the main checking operations; Python provides the CLI, file handling, request validation and display; Rust accelerates search, with proposed witnesses checked by Lean. The [Lean-first completion report](docs/lean-first/b18/REPORT.md) records the current dispatch changes and remaining exceptions. The [architecture map](docs/ARCHITECTURE.md) explains the system, with dated measurements and migration notes.

The checker has machine-checked soundness results for specific operations. That is not an end-to-end proof of the entire application: decoding, transport, display, the toolchain, and the connection between formal statements and the world still matter. See the [verification contract](docs/spec/verification-contract.md) and [assurance manifest](docs/spec/assurance-manifest.md).

Language expansion is ongoing, including work on events and time, quantities, scope, judgment terms, and defeasible reasoning. A design document or theorem alone does not mean a feature is available through every user-facing route. See the [plans](docs/plans/README.md), [specifications](docs/spec/), and [integration gaps](docs/INTEGRATION-GAPS.md).

The research case is still open. The project's [paper](paper/sections/00-abstract.md) reports no demonstrated benefit of strict controlled English over symbolic logic for its stronger model judge. Human sign-off and scalable oversight remain untested. VE can check the consequences of a specification; it cannot decide whether you chose the right specification, whether a premise is true, or what “reasonable” should mean. Exhausted search is unresolved, not a proof that a claim is false.

## Try it locally

You need Python 3.12+, `uv`, Lean via `elan`, and Rust via `rustup`, with `lake` and `cargo` on your `PATH`. The repository pins Lean in [`lean/lean-toolchain`](lean/lean-toolchain), Rust in [`rust-toolchain.toml`](rust-toolchain.toml), and Python dependencies in [`uv.lock`](uv.lock).

Clone the repository, then run these commands from its root:

```sh
git clone git@github.com:panaali/verifiable-english.git
cd verifiable-english
uv sync --locked --group dev
(cd lean && lake build)
uv run python tools/rust_build.py
```

The first native build can take a while. Once it finishes, try the committed inventory example:

```sh
uv run python -m ve render --env examples/environment.json --view ve_natural examples/requirements.ve
uv run python -m ve evaluate --env examples/environment.json --model examples/model.json examples/requirements.ve
```

The first command displays the requirements; the second should report `Satisfied` for the sample inventory. `environment.json` defines the vocabulary, `requirements.ve` states the rules, and `model.json` supplies the facts.

Now ask whether “every service is reviewed” implies “there exists a reviewed service”:

```sh
uv run python -m ve countermodel --env examples/environment.json --premises examples/premise.ve --conclusion examples/conclusion.ve
```

The search should find a counterexample with no services: the universal statement holds, but the existence claim does not. This is a concrete example of a missing assumption, not a model-generated critique.

These commands do not call an AI model. Model-backed suggestions in `ve assist` are optional and have separate setup. Explore other commands with `uv run python -m ve --help`.

## Where to go next

| You want to… | Read |
| --- | --- |
| Understand the ideas from first principles | [Illustrated tutorial](docs/onboarding/ve-tutorial.html) — download and open the HTML locally; its implementation snapshot is September 26, 2026 |
| See the long-term goal | [Vision](VISION.md) |
| Review applications and their limitations | [Agent policy](usecases/agent-policy/README.md), [eligibility](usecases/eligibility/README.md), [safety framework](usecases/safety-framework/README.md) |
| Write a formal argument interactively | [Assisted formalisation](docs/assisted-formalisation.md) |
| Integrate VE into a program | [Python API](docs/implementation.md), [architecture](docs/ARCHITECTURE.md) |
| Understand the evidence for the project | [Paper](paper/), [critical research review](docs/research-review.md), [experiments](experiments/) |
| Follow plans and historical results | [Roadmap](ROADMAP.md) — includes older dated snapshots; [plans index](docs/plans/README.md) |
| Find a specification or development guide | [Documentation index](docs/README.md), [specifications](docs/spec/) |
| Contribute | [Repository instructions](AGENTS.md), [testing guide](docs/TESTING.md) |

For complete verification, run `python3 tools/gate.py` on a clean, committed checkout. It builds the native backends, audits the Lean proofs, runs the test suite, and writes `gate-result.json`. See the [full gate guide](docs/verification-gate.md) for its environment, checks, and result format.
