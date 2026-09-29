# Verifiable English

An English-like language for human-inspectable, machine-checkable claims in AI oversight.

**Stage:** experimental Python v0 core, argument layer, constrained grammars, and Lean reference proofs implemented; full verification and oversight experiments are pending.

Run the complete offline verification gate with `python3 tools/gate.py`.
Every stage runs in an environment built from scratch, not inherited: `PATH` holds
only the pinned Lean and Rust toolchain `bin` directories (under the account's
`~/.elan/toolchains` and `~/.rustup/toolchains`), `uv` and `/usr/bin:/bin`; home,
caches and temporary files are fresh directories owned by that run. The allowed
variables are listed in `ALLOWED_ENVIRONMENT` in `tools/gate.py`, and the exact
environment of each stage is recorded in the result.
It checks the pinned Lean and Rust versions, syncs the locked Python environment
(refusing any ancestor `pyproject.toml` that declares a uv workspace, which would
substitute its own lock and `.venv`, and checking that Python runs from the
checkout's `.venv`), builds both native backends once, runs the Lean source audit, `cargo test`, and
the full non-live pytest suite, then writes `gate-result.json` with the commit SHA, tool versions, counts,
every skip and every failure. It exits nonzero for missing backends, unlisted skips,
missing test IDs, a dirty or changing worktree, or failed stages. Expected test
IDs are pinned in `tools/gate-collection.json`; regenerate that file after
intentional test changes by collecting with `tools.gate_pytest`. Optional backend
and fixture skips are listed in `tools/gate-optional.json`. The JSON result is local and ignored by Git;
use `--output PATH` to retain a particular gate record. The package requires
Python 3.12 or later.
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

## Assisted formalisation: `ve assist`

`ve assist` is an interactive tool for formalising prose **one sentence at a
time** ([plan](PLAN-ASSIST.md)). Humans use it through a small CLI; agents use
the same session through a JSON tool-calling API. The author owns fidelity to
the prose. The tool only reports: nothing enters the graph unless the author
adds it, and only the certificate checker and `check_countermodel` decide
"follows" or "countermodel".

Concepts:

- **Sentences.** Each source sentence has an id and a role. A `given` sentence
  states a premise. A `claimed` sentence asserts a conclusion, which must be
  derived. A `context` sentence needs no coverage. Every target sentence must
  be `claimed`. In plain-text sources, untagged paragraphs are `claimed`, not
  `given`, so intermediate conclusions never anchor assumptions by default; tag
  premise paragraphs `[given]`.
- **Frozen targets.** Each target sentence gets a formal statement through
  `freeze_target` before any node is added or any vocabulary is declared. It
  can never change afterwards. A target the prover derives from no premises
  (such as `true.`, or a conjunction of tautologies, checked conjunct by
  conjunct) is rejected as vacuous. If that check runs out of budget, the
  target's vacuity is `unknown` and the item can never succeed (fail closed);
  a target entailed by tautological assumptions alone also fails.
- **Nodes.** A node is one VE statement, anchored to the sentence(s) it
  formalises. A node with no parents is an assumption. A node with parents is
  a step, and `check_step` must certify it.
- **Unanchored assumptions.** An assumption is anchored only if it has a
  `given` anchor and no `claimed` anchor. Unanchored assumptions are
  *load-bearing* when a certified step no longer follows from its anchored
  parents alone (all unanchored parents removed at once), and the item then
  fails. Any assumption that alone entails a target also fails the item.
- **Declarations.** `declare` requires a gloss. It blocks near-duplicates of
  existing vocabulary (the `ve propose` gate) and names or glosses that restate
  a target sentence until the author acknowledges each flag. `status` also flags
  new vocabulary that carries a target: the assumptions using declared symbols
  (predicates, constants or sorts), together with the unanchored assumptions,
  entail it without the anchored premises.
- **Ledger.** The session file is an append-only ledger of every action,
  including rejected ones. For each action it records the result, the node
  provenance (`hand-written`, `proposer-verbatim`/`-edited`,
  `suggestion-verbatim`/`-edited`; a node typed by hand whose formula equals a
  shown candidate or suggestion is still marked as proposer/suggestion
  derived), the proposer's tokens, and author tokens
  (via `record_usage`). Every CLI command replays the ledger and fails if any
  recorded result does not reproduce, if the configuration does not match its
  `config_digest`, or if recorded token totals differ from the recorded calls.
  Failed proposer calls are logged with the tokens they spent and can be
  retried. An evaluator should also run `ve.assist.verify_session(ledger,
  item=DOSSIER, calls=CALLS_LEDGER)`, which rebuilds the configuration from
  the dossier and matches every recorded model call, failed ones included,
  against the claude CLI calls ledger (tokens, models, account, and the event
  that made the call), and reports calls-ledger rows the session never
  recorded. Every backend attempt is accounted for: earlier failed attempts
  under the same call key (infrastructure retries) are carried in the
  recorded call and counted in the session's token totals, which must equal
  the calls ledger's totals; a `started` row with no outcome fails
  verification. Earlier attempts are read from the calls ledger itself, so
  resuming a paused key reports every attempt, and a call rejected before it
  starts (e.g. by `max_calls`) after a failed attempt still reports that
  attempt's tokens and key; so does a retry whose preflight fails (no `claude`
  binary, a failing `claude --version`): every exit path keeps the prior
  attempt's key (found from the request itself when it cannot be recomputed)
  and its tokens. Counted usage is the field-wise maximum over EVERY
  usage-bearing record of the stream (each result record and each assistant
  message), for malformed streams too, so no later record erases reported
  tokens; `verify_session` recomputes it from each row's stored stream
  records with the same rule (`ve.stream_audit.stream_usage`). The raw stream
  is never persisted: rows keep its SHA-256 and its decoded JSON records. The
  access token is only in the child's environment, never in a prompt; as
  defence in depth ONE canonical sanitizer (`ve.stream_audit.sanitize`) is
  applied to every string of every calls-ledger row, returned row, error,
  session result and session-ledger event, and to parsed candidate JSON after
  parsing: it redacts the token, its prefix and known credential prefixes,
  sanitizes embedded JSON structurally, then decodes to a fixpoint (escapes
  at any JSON depth, percent-encoding, HTML entities, NFKC, base64/base64url,
  hex) and redacts any string that still exposes one. The default
  assumes a dedicated calls ledger held by the evaluator (every row counts).
  A shared calls ledger is attributable only through an independently trusted
  session id, so `verify_session(..., dedicated_calls=False)` is refused
  unless `trusted_session_id=` is supplied (the ledger's own `session_id` can
  be forged). Errors and
  backend-reported fields are redacted of anything that looks like a
  credential before they are logged or returned.

`status` reports `success` only when all of the following hold: every target
has a step whose certified support graph replays through `check_argument`;
every step is certified; every asserting `claimed` sentence is *derived* (a
certified step anchored to it, with a fully certified support in which no
single assumption already states it); every *witness* -- each certified step
that states a target or is anchored to a claimed sentence -- is evaluated,
not only the first found, and each must be entailed by the anchored
assumptions of its support alone (a witness that needs an unanchored
assumption blocks success whatever other witnesses exist); every asserting `given` sentence is
covered by a node; no asserting sentence is waived at all -- waiving ANY
asserting sentence blocks success, even one that is already covered or
derived (waivers of non-asserting sentences are recorded and harmless); no
unanchored assumption is load-bearing; no declared vocabulary carries a
target; no target is vacuous or of unknown vacuity; and the assumptions of
every target and every witness are consistent.

Every fidelity check fails closed. Each entailment, consistency, vacuity,
derivation, load-bearing and carrier question is decided as `yes`, `no`
(which needs a saturated proof search or a checked countermodel) or
`unknown`; an exhausted proof budget or countermodel search is `unknown`,
and `unknown` never counts as passing: `status` lists it as a failure marked
"undecided within budget (fail closed)". Raising or lowering
`max_proof_steps` can therefore turn an undecided item into a decided one,
but never a failing item into a success, and success at one budget implies
success at every larger budget. The outcome is a function of the graph:
premises are passed to every search -- including `check_step`'s own proof,
whose certificate is replayed with the deduction's premises in the same
canonical order -- and witnesses are evaluated in name order, so neither node
insertion order nor a step's parent order changes it.

The proposer and premise suggestions are separate ablations:

- **`propose SENTENCE`** asks a Claude model (`--proposer-model haiku|sonnet|opus`,
  Haiku 4.5 by default; claude CLI backend, no model fallback; account from
  `--account LABEL` or `$VE_ASSIST_CLAUDE_ACCOUNT`) for 1–3 candidates. The
  requested and served model ids are recorded with each call. Each
  candidate is parsed, type-checked and paraphrased, and each differing pair
  gets a checked distinguishing model. Accepting a candidate is a separate,
  explicit step.
- **Premise suggestions** are off unless the session is created with
  `--premise-suggestions`. A `bridge` suggestion assumes the step itself and is
  labelled as such.

### Worked example

Files: `examples/assist/environment.json` and `examples/assist/argument.txt`.
Run `uv run python -m ve assist ...`:

```text
$ python -m ve assist new demo.json --env examples/assist/environment.json --text examples/assist/argument.txt --target p2.1
created demo.json: 5 sentences, targets t_p2_1 -> p2.1
$ python -m ve assist sentences demo.json
    p1.1 [given] Every reviewed service is safe.
    p1.2 [given] The API is reviewed.
    p1.3 [given] The web front end is deployed.
    p2.1 [claimed] So the API is safe.
    p3.1 [context, non-asserting] The inventory was exported on Monday.
$ python -m ve assist freeze demo.json t_p2_1 '@api is safe.'
$ python -m ve assist add demo.json fact '@api is reviewed.' --anchor p1.2
$ python -m ve assist add demo.json goal '@api is safe.' --anchor p2.1 --parent fact
$ python -m ve assist check demo.json goal
goal: COUNTERMODEL  (fact => @api is safe.)
  countermodel (all parents true, conclusion false):
    entities: service: api, web
    true:  api is reviewed
    false: api is safe
$ python -m ve assist add demo.json rule 'Every service that is reviewed is safe.' --anchor p1.1
[rule] assumption, hand-written
  VE:   for every service x0, (if (x0 is reviewed), then (x0 is safe)).
  says: Every service that is reviewed is safe.
$ python -m ve assist rewrite demo.json goal --parent rule --parent fact
$ python -m ve assist check demo.json goal
goal: FOLLOWS  (rule, fact => @api is safe.)
$ python -m ve assist status demo.json
NOT YET: 1 given sentence(s) not covered by any node: p1.3
$ python -m ve assist add demo.json background '@web is deployed.' --anchor p1.3
$ python -m ve assist status demo.json
SUCCESS
target t_p2_1: certified (graph replays)
coverage: 1 claimed derived, 3 given covered, 0 waived, 0 uncovered, 0 claimed underived
$ python -m ve assist replay demo.json
ledger replays: 11 events reproduce
```

Nodes can be written in strict VE or in the controlled English surface; the
parser tries strict first. Other commands: `show`, `paraphrase`, `compare A B`
(prints distinguishing models), `declare NAME --gloss ... --arg SORT`,
`propose SENTENCE`, `export` (argument graphs), and `ledger` (usage).

For a P5 dossier, run `new s.json --p5 PATH/dev.jsonl.gz --item 0`. It loads
the premises and records as `given`, the paragraphs as `claimed`, and the root
paragraph's conclusion as the target. It builds a public vocabulary with one
predicate per glossary sense, such as `ready_packing_completed` and
`ready_staffing_arranged`.

### Agent API

`ve.assist.tool_schemas(proposer=..., premise_suggestions=...)` returns the
Anthropic-style tool definitions for one evaluation arm. The tools are
`sentences`, `freeze_target`, `add_node`, `rewrite`, `remove_node`, `declare`,
`check_step`, `status`, `waive`, `show`, `paraphrase` and `compare`, plus
`propose` and `accept` when a proposer is configured.
`ve.assist.call_tool(session, name, arguments)` executes and logs a call and
never raises on bad input. `AssistSession.to_ledger()` and
`AssistSession.from_ledger()` persist and replay a session. From a shell, run
`python -m ve assist call SESSION TOOL '{json}'`.
