# Verifiable English

**[Onboarding guide](https://claude.ai/artifact/3vLxUDY9QeL3xUTLHUBBjy)**

**Verifiable English (VE) is a controlled subset of English, built on the Lean proof assistant, for writing mechanically checkable claims and arguments.** You write readable English; VE checks whether conclusions follow from the stated assumptions.

VE is built for AI oversight: helping people understand and verify what an AI system claims, promises, or proposes to do. Today it is a research implementation with a command-line interface, Python APIs, a Lean checker, and worked applications—not a finished general-purpose document editor.

[Try the release: Winter Fuel Payment demo](#try-the-release-winter-fuel-payment-eligibility) · [Start with an example](#a-small-example) · [Try it locally](#try-it-locally) · [Documentation](#where-to-go-next) · [Vision](VISION.md)

## Try the release: Winter Fuel Payment eligibility

The current release, **ve-elig-b2** (release B), is a checker for one benefit. It answers four questions about one person and the Winter Fuel Payment for winter 2026 to 2027 in England and Wales: is the person entitled, how much is the payment, does HMRC take it back because income is over £35,000, and how much is kept. With each answer it quotes the clauses of the regulations it used, lists in plain English the assumptions it took as given, and reports that every proof step of the answer was checked by Lean.

On a fresh Ubuntu 24.04 machine with about 10 GB of free disk, git, and a user who can run `sudo` (no GitHub account or key needed; [DEMO.md](usecases/eligibility/DEMO.md) step 1 installs git if it is missing):

```sh
git clone --branch ve-elig-b2 https://github.com/panaali/verifiable-english.git ve && cd ve
sh usecases/eligibility/demo/install.sh
export PATH="$HOME/.local/bin:$PATH"
uv run python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json
```

The install script, [`usecases/eligibility/demo/install.sh`](usecases/eligibility/demo/install.sh), adds what is missing and builds the checker; its first Lean build takes 20 to 40 minutes and prints nothing while it runs. The step-by-step guide, with the exact expected output: [usecases/eligibility/DEMO.md](usecases/eligibility/DEMO.md). What the checker covers and its limits: [the eligibility case](usecases/eligibility/README.md).

## Why build this?

An AI can produce a persuasive explanation that contains an invalid step, quietly changes a definition, or proves a weaker claim than the one requested. Reviewing all of its reasoning can be harder than solving the original problem.

VE explores a different division of work: the author or AI supplies precise claims and supporting proofs; a mechanical checker checks the deductions; a person reviews the meanings, assumptions, and evidence that remain. The English presentation is intended to make that review accessible without requiring the reviewer to read symbolic logic.

The long-term vision is to apply this to policies, contracts, scientific arguments, and agent actions. An agent could submit a proposed action together with a checked proof that it meets an approved policy. This is a research goal, not a deployed enforcement system. See the [vision](VISION.md) and [oversight rationale](design/crypto-inspired-oversight.md).

## A small example

> Every reviewed service is safe. The API is reviewed. Therefore the API is safe.

**This is what a user or AI agent writes directly into VE, in natural English.** With the [declared vocabulary](examples/assist/environment.json) and [English names](examples/assist/environment.english.json), VE reads the sentences, identifies the first two as assumptions, and checks that the conclusion follows. The [executable example](tests/test_natural.py) checks both the English reading and the deduction. Running it (`uv run pytest tests/test_natural.py`) first builds the native Lean and Rust checkers, as every pytest run does; the first Lean build takes 20 to 40 minutes ([Try it locally](#try-it-locally)). Later runs reuse the build while `lean/` and `rust/` are unchanged, and `VE_NATIVE_PREBUILT=1 uv run pytest tests/test_natural.py` uses the built checkers as they are, with no build step ([testing guide](docs/TESTING.md)). The same argument, one command at a time: the [assisted-formalisation walkthrough](docs/assisted-formalisation.md#worked-example).

Change “The API is reviewed” to “The API is deployed,” and the conclusion no longer follows: the rules say nothing about whether deployed services are safe. VE can expose that missing step instead of accepting a plausible-sounding explanation.

You can also write:

> Every deployed service has an owner.

This allows different owners for different services. It does not silently become the stronger claim that one person owns every service. VE keeps that distinction precise while letting you read ordinary sentences.

The guarantee is about the reasoning: **if the assumptions hold, the checked conclusion holds.** Someone still has to establish that the API really was reviewed and that review is sufficient for safety. VE makes those assumptions visible; it does not turn them into facts.

A VE document (`.ve.md`) keeps the English source together with its checked statements. To check a small committed one, three sentences about a group's members, after the native build ([Try it locally](#try-it-locally)):

```sh
uv run python -m ve document check usecases/question-answering/group.ve.md
```

It prints a JSON report. Its `coverage` part says that all 89 bytes of the source are in units whose status is CHECKED:

```text
    "bytes_by_status": {
      "CHECKED": 89
    },
    "coverage_percent": 100,
```

What a unit's status in `ve document check` says: CHECKED: the core statements shown for this unit were admitted by the checker (one reading, well-formed over the document's vocabulary, lemmas and certificates replayed). How the unit's English was turned into those statements is shown with them; that translation is tested and audited, and proved only where the feature's page says so. CHECKED does not say the statements are true or that a conclusion follows: that is what certificate and conflict verdicts are for.

## What you can do now

The following capabilities are present in the code on this branch. Features have explicit scopes, and some combinations are rejected; they are not a promise that arbitrary prose can be formalised automatically.

| Task | What VE provides | Start here |
| --- | --- | --- |
| Write and inspect precise claims | Declared vocabulary, parsing and type checking, definitions, and several English/logical renderings | [Small examples](examples/), [rendering guide](docs/fluent-examples.md) |
| Check reasoning | Finite-model evaluation, checked proofs and argument graphs, and counterexamples to invalid inferences | [Python API](docs/implementation.md), [proof results](lean/METATHEORY.md) |
| Review a document | Source-span accounting, explicit assumptions and unsupported passages, and alternative readings rather than silently choosing an interpretation | [Document format](docs/spec/document.md), [safety-framework case](usecases/safety-framework/README.md) |
| Express policy rules | Obligations, permissions, prohibitions, exceptions and priorities; worked checks for conflicts and uncovered situations | [Agent-policy case](usecases/agent-policy/README.md), [norms specification](docs/spec/norms.md) |
| Work with exact quantities | Supported decimals, unit tags, dates, comparisons and bounded counting; staged reasoning in an eligibility example | [Quantity status](docs/W6A-STATUS.md), [eligibility case](usecases/eligibility/README.md) |
| Build a formalisation step by step | `ve assist` records source sentences, freezes target claims, checks proposed steps, and reports missing support | [Assisted-authoring guide](docs/assisted-formalisation.md) |

These examples demonstrate particular implemented routes. They do not establish general translation accuracy, legal correctness, or improved human oversight. The eligibility case, for example, records translation errors that its initial tests missed because the translation and answer key shared assumptions.

## Current status and limits

Lean decides most keyed answers of the published use cases: 100 of the RSP key's 126, 228 of Preparedness's 239, 244 of the safety framework's 262 and 287 of eligibility's 287 come from a Lean check backed by a kernel theorem, with no Python decision on their path. Python still decides all 42 agent-policy answers and the conflict answers of the RSP, Preparedness and safety-framework cases, and the other answers of those three cases that are not Lean's either do not come from a Lean check backed by a kernel theorem or differ from the key (Python also runs the command line, file handling and display; Rust speeds up search, and Lean checks what it proposes). The per-answer table, with the reason each answer is or is not Lean's, is [docs/kernel/ownership.md](docs/kernel/ownership.md); [who computes the keyed answers](docs/usecases/keyed-answers.md) and the [architecture map](docs/ARCHITECTURE.md) give the details.

The checker has machine-checked soundness results for specific operations. That is not an end-to-end proof of the entire application: decoding, transport, display, the toolchain, and the connection between formal statements and the world still matter. See the [verification contract](docs/spec/verification-contract.md) and [assurance manifest](docs/spec/assurance-manifest.md).

Language expansion is ongoing, including work on events and time, quantities, scope, judgment terms, and defeasible reasoning. A design document or theorem alone does not mean a feature is available through every user-facing route. See the [plans](docs/plans/README.md), [specifications](docs/spec/), and [integration gaps](docs/INTEGRATION-GAPS.md).

The research case is still open. The project's [paper](paper/sections/00-abstract.md) reports no demonstrated benefit of strict controlled English over symbolic logic for its stronger model judge. Human sign-off and scalable oversight remain untested. VE can check the consequences of a specification; it cannot decide whether you chose the right specification, whether a premise is true, or what “reasonable” should mean. Exhausted search is unresolved, not a proof that a claim is false.

## Try it locally

You need Python 3.12+, `uv`, Lean via `elan`, and Rust via `rustup`, with `lake` and `cargo` on your `PATH`. If you installed them with the release's `install.sh`, put their directories on your `PATH` first: `export PATH="$HOME/.local/bin:$HOME/.elan/bin:$HOME/.cargo/bin:$PATH"`. The repository pins Lean in [`lean/lean-toolchain`](lean/lean-toolchain), Rust in [`rust-toolchain.toml`](rust-toolchain.toml), and Python dependencies in [`uv.lock`](uv.lock).

Clone the repository over HTTPS (no key needed), then run these commands from its root:

```sh
git clone https://github.com/panaali/verifiable-english.git
cd verifiable-english
uv sync --locked --group dev
(cd lean && lake build)
uv run python tools/rust_build.py
```

The first Lean build takes 20 to 40 minutes and prints nothing until it ends; a later build of an unchanged tree takes seconds. Every `ve` command below needs it: until it has finished they stop with `CheckerUnavailable`. Once it finishes, try the committed inventory example:

```sh
uv run python -m ve render --env examples/environment.json --view ve_natural examples/requirements.ve
uv run python -m ve evaluate --env examples/environment.json --model examples/model.json examples/requirements.ve
```

The first command displays the requirements; the second prints a JSON report whose `"status"` field is `"Satisfied"` for the sample inventory. `environment.json` defines the vocabulary, `requirements.ve` states the rules, and `model.json` supplies the facts.

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

For complete verification, run `python3 tools/gate.py` on a clean, committed checkout. It builds the native backends, audits the Lean proofs, runs the test suite, and writes `gate-result.json`. See the [full gate guide](docs/verification-gate.md) for its environment, checks, and result format. It is a long job: the full gate of 25 November 2026 took 153 minutes and peaked at 20.5 GB of memory on a 32-CPU x86-64 Linux machine with 125 GB of memory, shared with other jobs, with the Lean build already done. For everyday checks, run only the tests your change can affect (`tools/select_tests.py`, see the [testing guide](docs/TESTING.md)).

Licensed under the Apache License 2.0; see [LICENSE](LICENSE).
