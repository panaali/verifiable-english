# Working in this repository

Read this first. It changes only when a rule changes; the facts that change when a route is added
come from `tools/repo_map.py`, which reads them from the repository each time.

## What VE is

Verifiable English (VE) is a controlled English for claims that people can read and machines can
check, built for AI oversight. A document has exactly one reading: an ambiguous sentence is refused
or rephrased, never guessed. A checker written and proved in Lean 4 decides what the document means
and whether it holds; Python and Rust carry the files, the display and a fast path around it.

## Who owns what

- **Lean owns meaning.** Every verdict, diagnostic (code and text), limit, fault order and derived
  value is computed in Lean. A Lean answer is the answer; Python never recomputes it.
- **Python** does the command line, files, display, the response schema and request binding only.
  A relayed answer is checked for (a) its schema, fully typed, and (b) its binding to the request:
  every id, span, count and choice it names exists in the request, and no row is empty or extra.
  Anything else is `CheckerUnavailable`, never a Python verdict.
- **Rust** is an untrusted accelerator. Its answers are compared with Lean's, never trusted alone.
- **One owner per piece of logic.** A table, rule or wording lives in one place, in one language;
  the others read it from there or from a file generated from it. Never copy it.
- Layers (kernel, profiles, surface, tools, apps) are assigned in `tools/layer_policy.py`.

## Where things are

- `ve/` the Python package: the CLI (`ve/__main__.py`), document loading, display and relays.
- `ve/backends/` the Lean service client (`ve/backends/lean_service.py`), the one relay entry
  (`ve/backends/relay.py`), the response schemas and their checker (`ve/backends/service_schema.py`).
- `lean/VE/` Lean semantics, checkers and proofs, one directory per profile.
- `lean/VE/Service/` the persistent `ve_service`; `lean/VE/Service/Protocol.lean` dispatches every mode.
- `lean/ResponseShape/` response shapes (`lean/ResponseShape/Schemas/`) and encoder theorems
  (`lean/ResponseShape/Encoders/`).
- `rust/` the Rust accelerator crates.
- `tests/` the pytest suite; `tests/data/` recorded fixtures.
- `tools/` the gate, test selection, generators and lints.
- `conformance/` cross-implementation corpora and harnesses.
- `docs/` documentation; `docs/spec/` specifications; batch reports and evidence in `docs/<batch>/`.
- `usecases/` worked use cases with their harnesses; `experiments/` and `ve_experiments/` research.

## How to find a route

- `uv run python tools/repo_map.py routes` one row per service mode: Lean module, schema, relays, tests.
- `uv run python tools/repo_map.py route discourse` one mode in full, one file per line.
- `uv run python tools/repo_map.py file ve/discourse.py` the modes, layer, tests and generator of a file.
- `uv run python tools/repo_map.py --check` fails when a mode has no schema file or a schema file no mode.

A cell the repository's data cannot fill says "unknown"; then read the code, and do not guess.

## Recipe: a relayed Lean route

Worked example: the `discourse` mode.

1. **Lean runner.** `lean/VE/Discourse/Run.lean` defines `VE.Discourse.Run.runCaseReported`.
   `VE.Service.runMode` in `lean/VE/Service/Protocol.lean` dispatches the mode to it, and the equation
   `VE.Service.runMode_discourse` is listed in `lean/VE/Audit.lean`.
2. **Shape.** `lean/ResponseShape/Schemas/Discourse.lean` writes the row's shape, typed to the leaves.
3. **Encoder theorem.** `lean/ResponseShape/Encoders/Discourse.lean` proves
   `ResponseShape.Encoders.Discourse.runCaseReported_fits`: every row the runner writes fits the shape.
   It is listed in `lean/ResponseShape/Audit.lean`.
4. **Generated schema.** `ve/backends/lean_service_schema/discourse.json`, rendered from the shape by
   `uv run python tools/response_schemas.py --write`. The mode is in `MODES` of `ve/backends/service_schema.py`.
5. **Python relay.** `ve/discourse.py` sends the case with `rows` from `ve/backends/relay.py` and binds
   the answer to the document it asked about; it checks schema and binding only (R8 in the DRI rulings).
6. **Fixtures.** Genuine cases recorded from the suite in `tests/data/route-cases.jsonl`
   (`tests/route_case_recorder.py`), checked against the schemas by `tests/test_route_row_schemas.py`;
   the route's own documents in `tests/test_discourse_lean.py`.
7. **Fuzz tests.** `tests/test_discourse_answer.py` mutates genuine answers one and two faults at a time
   (each member dropped, emptied, retyped, duplicated or reordered, an index pushed out of range):
   every mutant is `CheckerUnavailable` or changes nothing the relay shows.

## Generated files

Never edit a generated file by hand, and never hand-merge one: regenerate it with its own tool.
`tools/regen_generated.py` is the one inventory of generated files and their generators:

- `uv run python tools/regen_generated.py --list` every generated file, its generator and its check.
- `uv run python tools/regen_generated.py --owner <path>` the entry that owns one file;
  `uv run python tools/repo_map.py file <path>` prints the same entry as its `generator` line.
- `uv run python tools/regen_generated.py --check` fails when a generated file is stale;
  `--write` regenerates them all, in dependency order; `--resolve` finishes a `git merge --no-commit`
  whose only conflicts are generated files.
- The gate records collected test IDs with the commit it checked. `tools/gate_collection.py --check`
  compares the current collection with its merge base; there is no committed collection file.
- `lean/checkers.lock` pins the built checkers; `python3 tools/rust_build.py --check` fails when the
  Rust binary is not pinned.

## Standard commands

- `cd lean && PATH=~/.elan/bin:$PATH lake build` builds the Lean library and the default executables.
- `python3 lean/audit.py` audits every Lean source and theorem against the allowed axioms.
- `uv run python tools/select_tests.py --base $(git merge-base HEAD main) --run` runs the tests a branch
  can affect. Use it while iterating.
- `python3 tools/gate.py` is the full release gate. It writes its result to gate-result.json in the checkout.
- `python3 tools/rust_build.py` builds the reproducible Rust release binary.

## Testing rules that recur in reviews

- **Run the full gate once,** on the committed final HEAD, as the last step. While iterating, run the
  selected tests and the tests you add. Never rerun the full gate on an unchanged commit.
- **Report and evidence tests read saved evidence**: numbers and commit lists saved with the batch,
  never a live `git diff` against a moving HEAD, so they still pass after a sync with main and after
  the merge.
- **No literal sleeps, no short timeouts, no elapsed-time asserts.** Waits use `HANG_TIMEOUT` from
  `tests/subprocesses.py`; deadlines are tested by injecting an expired clock; `tests/test_hang_guards.py`
  enforces this. Speed is measured in `tools/bench/test_perf.py`, never in the suite.
- **Seeded bugs in each changed language.** Before review, plant a bug in each behaviour you claim, in
  every language whose product code you changed (Lean, Python, Rust); show that a test fails; restore it.
  Record each with its file and the failing test.
- **Every relayed answer is typed and bound**, with fuzz tests that retype and rebind each field.
- **Verdicts are three-valued.** Exhaustion, a timeout or an empty budget is UNKNOWN, never false or none.
- **Hermetic tests.** Write only under `tmp_path`; do not rely on caches, the network or model calls.
- `docs/TESTING.md` has the full testing guide: selection, the coverage map, workers and benchmarks.
