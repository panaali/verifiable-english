# Verifiable English: the architecture map

**Status:** the current map of the system. It replaces the architecture sections of older documents (section 6
lists them). The layer checkers and their commands stay in [ARCHITECTURE-LAYERS.md](ARCHITECTURE-LAYERS.md); the
binding contract is [ADR 0001](adr/0001-response-binding.md). Written from section 1 of the October 2026
architecture review (`docs/ARCHITECTURE-REVIEW-2026-10.md` on branch `design/arch-review`), batch AR-7.

<!-- numbers:measured -->
Measured on commit `8482c8c4f7e8ef1be9447423a08443634f465631` by `tools/architecture_numbers.py`; saved in `docs/architecture/numbers.json`.
<!-- /numbers:measured -->
Every table between `numbers` markers is rendered from that file; to bring them up to date, run
`python3 tools/architecture_numbers.py --write` on a committed head and commit the result (section 7).

## 1. Layers and sizes

```
 people, editors, web app, agents
          │  files, CLI, JSON
 ┌────────▼─────────────────────────────────────────────────────────┐
 │ Python ve/                                                       │
 │   CLI ve/__main__.py, documents ve/document.py, display and      │
 │   English rendering, assist, adapters                            │
 │   route modules (soft_route, rights_route, readings_route, ...)  │
 │   ve/backends: relay → lean_service pool → schemas ──────────────┼──► Rust `ve` JSON-lines pool
 └────────┬─────────────────────────────────────────────────────────┘     (search, untrusted, rule 3)
          │ JSON lines: {id, mode, cases, environments?} → bound rows
 ┌────────▼─────────────────────────────────────────────────────────┐
 │ Lean ve_service (Serve.lean → VE.Service.Protocol)               │
 │   runners per profile: VE.<Profile>.Run, Wire, Admission, ...    │
 │   kernel and logic: VE.Syntax/Semantics, Core, Closure, Order    │
 │   ResponseShape: schemas, encoders, fits proofs                  │
 └──────────────────────────────────────────────────────────────────┘
 one-shot Lean executables still called in production: ve_conformance, ve_metered,
 ve_senses_route, ve_speech_acts_route (section 3)
```

Lean decides meaning and acceptance; Python reads files, relays requests to Lean and displays Lean's answers; Rust
proposes search candidates (models, proofs) that Lean checks before anything is reported (lean-first rule 3,
decision A of 2026-10-08).

<!-- numbers:sizes -->
| Part | Where | Size | Notes |
|---|---|---:|---|
| Python `ve/` | `ve/**/*.py` | 39,866 lines | largest: `english.py` 2,147, `document.py` 1,758, `readings_verdicts.py` 1,722 |
| Python relay and transport | `ve/backends/` | 4,276 lines | plus 8,068 lines of generated JSON schemas; `relay.py` 167, `lean_service.py` 952, `service_schema.py` 590 |
| Lean | `lean/**/*.lean` | 158,021 lines | 408 modules under `lean/VE/`; service modules: Protocol 859, Standalone 1,293, Document 922, Family 812 |
| Response shapes | `lean/ResponseShape*`, `lean/ResponseDecode.lean` | 64 files | schemas, encoders and their fit proofs |
| Generated Lean inventories (committed) | `lean/{statements,declarations,axioms,predicates}.txt` | 36,431 + 17,296 + 5,276 + 1,076 lines | written by `tools/lean_statements.py` and `lean/audit.py` |
| Rust | `rust/*/src/**/*.rs` | 4,854 lines | 488 (`ve`) + 21 (`ve-core`) + 2,320 (`ve-kernel`) + 2,025 (`ve-profile`) |
| Tools | `tools/**/*.py` | 20,301 lines | gate, selection, A/B, fuzz, trust map, layer checkers |
| Tests | `tests/**/*.py` | 106,500 lines | 359 test modules, 25 other modules; 14,437 collected test IDs (`tools/gate-collection.json`); 19,170 lines of Python in `conformance/` |
| Committed files | the whole tree | 374 MiB | `docs/` 143 MiB, of which `docs/lean-first/` 125 MiB |
<!-- /numbers:sizes -->

<!-- numbers:counts -->
| Count | Source | Value |
|---|---|---:|
| Lean service modes | `MODES` in `ve/backends/service_schema.py` | 32 |
| Lean executables | `[[lean_exe]]` in `lean/lakefile.toml` | 9 |
| Python runtime dependencies | `[project] dependencies` in `pyproject.toml` | 5 |
| Python layer exceptions | `tools/layer-exceptions.json` | 42 |
| Lean layer exceptions | `tools/lean-layer-exceptions.json` | 22 |
| Pinned Lean decoder lines | `lean_decoders.total_lines` in `ve/assurance-manifest.json` | 29,166 |
<!-- /numbers:counts -->

## 2. Module boundaries and the layer checkers

`tools/layer_policy.py` is the single table of five layers (kernel, profiles, surface, tools, apps) for Python and
Lean; `tools/check_python_layers.py`, `tools/check_lean_imports.py` and `tools/check_rust_deps.py` enforce
inward-only imports against the exception ledgers counted above. Most Python exceptions are kernel, profile or
surface modules importing `ve.backends`; most Lean exceptions are the legacy `Core` and `TableauExtended*` proofs
importing `Closure` and `Route` machinery. Rust's crate split is done: `ve-kernel` and `ve-profile` are separate
crates and `ve-core` is a re-export facade, so cargo enforces the Rust boundary. How to run the checkers and the
test-selection policy: [ARCHITECTURE-LAYERS.md](ARCHITECTURE-LAYERS.md).

The Python layer table predates lean-first. It files `entailment`, `evaluate`, `norms`, `rights`, `softnorms` and
`units` as layer 2 "profiles" although they now relay and hold data, and it files the relay (`ve.backends`) as
layer 4, so every module that relays Lean's answer is an exception. Under lean-first rule 2 the transport is the
innermost Python layer; the DRI adopted the five-layer map of review T5, checked by `import-linter` (D5).

## 3. The wire contract and the response shapes

- **Protocol.** One JSON line per request, `{"id", "mode", "cases", "budget"?, "environments"?}`; one line per
  response, with result `i` as `{"digest", "index", "result"}`, where `digest` is the SHA-256 of case `i`'s text as
  the client sent it ([lean-service.md](spec/lean-service.md), `lean/VE/Service/Protocol.lean`). Environments can
  be registered once and named by handle (lean-first F2).
- **Modes.** One runner `Json → Json` per mode (counted above), each pinned by an `rfl` theorem in `Protocol.lean`.
  The client's list of modes is `MODES` in `ve/backends/service_schema.py`. Statement-layer runners dispatch on a
  `kind` string and pass the cases they do not claim down a chain (rights → soft norms → norms → route). Every
  statement-layer route is a service mode; `ve/backends/relay.py` and the manifest-bound calls of `lean.run` are the
  only ways `ve` reaches Lean.
- **One-shot executables.** `ve_conformance` and `ve_metered` (metered evaluation, one process per call), and the
  `ve_senses_route` and `ve_speech_acts_route` routes are still separate processes; the other `[[lean_exe]]`
  entries of `lean/lakefile.toml` are the service, the response decoder and English tools.
- **Diagnostics.** Runners return `Except String`. The service derives the public `code` from the message's text
  before the first colon (`rejectionCode` in `Protocol.lean`); the soft-norms route keeps its own table of message
  prefixes (`SoftNorms.Run.reportedCode`). Typed codes in Lean (D6, review T2) replace both.
- **Response shapes.** Written once as Lean data (`lean/ResponseShape/Schemas/*.lean`), rendered to the JSON files
  in `ve/backends/lean_service_schema/` by `tools/response_schemas.py`, and interpreted twice: by
  `ve/backends/service_schema.py` in the client and by `ResponseShape.check` in `ve_response_decode`, with a test
  that the two agree (`tests/test_lean_service_schema.py`). The dialect is JSON Schema plus extension keywords
  ([README](../ve/backends/lean_service_schema/README.md)). Every mode's encoder is proved to fit its shape
  (`runMode_fits`, `lean/ResponseShape/Encoders.lean`).
- **Binding.** [ADR 0001](adr/0001-response-binding.md) (DRI decision D1): binding is a closed list of relations to
  the request, and a field that names a request item is bound only by `references` or `equals` (a format check
  is not a binding); derived values are Lean's, covered by a Lean theorem or a `ResponseDecode` invariant, and
  never recomputed in Python. Binding a field is still opt-in, keyword by keyword; the review counted about 307 bare
  `str` leaves against 120 binding keywords by text search, and AR-11 replaces that count with an exact census
  in Lean.
- **Rust.** A pool of JSON-lines `ve` processes (`ve/backends/rust_jsonl.py`, schema
  `ve/backends/rust_schema/jsonl.json`); Lean checks every witness Rust reports.

## 4. Data flow per main operation

- **Formula operations** (`ve parse|check|evaluate|countermodel`): `ve/__main__.py` reads files and builds the
  `Environment` after Lean's `environment` mode accepts it (`ve/backends/validation.py`); parsing and typing go
  through `ve/backends/dispatch.py`, whose default authority is still `python` for operations without a single
  owner yet (lf-13b flips the covered ones, lf-18 removes the authority); evaluation and countermodel search use
  Rust's evaluator inside search and Lean's checks of every reported value and witness; metered evaluation runs
  as a one-shot `ve_metered` process per call (`ve/backends/lean_runner.py`).
- **Document check** (`ve document check FILE`): `ve/document.py` sends a `ve-document@1` text to Lean's `document`
  mode; when the mode answers `CheckerUnavailable` or `ResourceLimit` (profiles it does not own yet, lf-16d–16g),
  Python's own path `_load_document` calls each profile's route; `ve-document@2` goes through Lean's discourse
  admission first. `_report` builds the coverage and the report for display. lf-16g deletes the Python path once
  the residue ledger is empty.
- **Statement-layer route** (for example rights): the route module builds a case from the environment and units
  and calls `relay.decide_once("rights", case)`; the service runs `VE.Rights.Run.runCaseReported`; the client
  checks the envelope and the row against the generated schema; Python reads fields for display.
- **English admission** (`parse_english`): `ve/english.py` → `ve/backends/english_lean.py` → mode `english.read`;
  Lean's reader decides one reading or a rejection; Python's `EnglishParser` runs only as a shadow comparator.
- **Readings** (`ve document readings`): S1 validation is Lean's, relayed; S2 elaboration takes Lean's answer and
  compares it with a Python regeneration of the route, choices, vocabulary, units, names and slot
  (`ve/readings_route.py`); verdicts across readings use Python's prover and model search as generators, each piece
  of evidence checked by a Lean readings kind (`ve/readings_verdicts.py`).
- **Assist** (`ve assist`): Python session, journal and recovery (editor help); proposals are untrusted and every
  "yes" is replayed through Lean (lf-17).

## 5. The trusted base

From `docs/trust-baseline.json` (written by `tools/trust_map.py --write`):

<!-- numbers:trust -->
| Class | Meaning (consolidation plan 1.1) | Lines |
|---|---|---:|
| K | kernel definitions read once | 997 |
| S | reviewed statements and meaning predicates | 9,791 |
| D | decoders (D[V] verdict-bearing 12,256, D[R] reject-only 1,002, D[I] identity 527) | 13,785 |
| G | glue (G[V] 24,805, G[R] 1,751, G[I] 241) | 26,797 |
| C, P, T, o | checkers, proofs, tests, other: not trusted | 8,486 / 71,772 / 14,245 / 12,148 |
| **trusted** | K + S + untied [V] (budget 997 + 9,791 + 36,902) | **47,690 of 158,021** |
<!-- /numbers:trust -->

The rest of the trusted path: the Lean toolchain, compiler and runtime; the restricted JSON reader and the request
splitter of `Protocol.lean`; in Python, the envelope and binding checks and the wire primitives (`ve/backends/`,
`ve/wire.py`, `ve/environment_wire.py`). Rust is not trusted. `ve/assurance-manifest.json` ("trusted") is the
declared list; it still describes `python` authorities that lf-18 removes. The pinned decoder total is in the
counts table of section 1; the consolidation plan's earlier "may shrink but not grow" figure (16,985) no longer
holds.

The budget's history is in `trust-baseline.json` (`history`): the review found the untied verdict-bearing budget
`V` raised from 17,113 to its current value mostly by re-baselining entries at merges, with 1,515 lines of signed
`V` allowances. The DRI adopted a ratchet (D3): the budget falls automatically and rises only by a signed allowance
in the same merge (batch AR-4).

## 6. Stale documents

The statements below were current when written and are not any more. Each is either corrected in its file (marked
superseded, with a link here) or waits for the named reason; `tests/test_architecture_docs.py` checks both.

| # | Document | It says | Today | Status |
|---|---|---|---|---|
| 1 | [architecture-and-design.md](architecture-and-design.md) | "First draft. Implementation, proofs, and usability results are pending." | implemented and proved in Lean (sections 1 and 5); `lean/audit.py` checks every theorem of the audit manifests | corrected |
| 2 | [implementation.md](implementation.md) | "Experimental Python VE v0 core … supports exactly `ve.core@0`, `relational-fol@0` … no third-party runtime dependencies" | Python is the CLI and relay over Lean's checker; runtime dependencies are counted in section 1 | corrected |
| 3 | [ARCHITECTURE-LAYERS.md](ARCHITECTURE-LAYERS.md) table | Rust: "one crate holds all three groups until the crate split" | `ve-kernel`, `ve-profile`, `ve-core` facade (section 2); batch AR-8 deleted the module check and `tools/rust-module-exceptions.json` that its Rust paragraph describes: `tools/check_rust_deps.py` reads cargo's crate graph from `cargo metadata` | waits: branches `infra/ts-B1` and `lean-first/b16d` edit this file |
| 4 | [ARCHITECTURE-LAYERS.md](ARCHITECTURE-LAYERS.md) table | Lean entry points "`NormsMain`, `SoftNormsMain`, `RightsMain`", … | deleted by lean-first batch 1; the `[[lean_exe]]` count is in section 1 | waits: `ts-B1` and `b16d` edit this file |
| 5 | [ARCHITECTURE-LAYERS.md](ARCHITECTURE-LAYERS.md) | the service is "still outside the `ve` command path" | every statement-layer route is a service mode (section 3) | waits: `ts-B1` and `b16d` edit this file |
| 6 | [ARCHITECTURE-LAYERS.md](ARCHITECTURE-LAYERS.md), "Current exceptions" | "12 Python edges plus the assist CLI app edge" | the Python layer exception count is in section 1 | waits: `ts-B1` and `b16d` edit this file |
| 7 | [INTEGRATION-GAPS.md](INTEGRATION-GAPS.md) | the service "is not yet called by `ve`"; alternatives, reports and quantity are not service modes: "`alternatives@0` continues through the dedicated `ve_alternatives_route`", "The stage-1 service also has no reports mode", "The stage-1 `ve_service` has no quantity mode" | all three are modes and `ve` calls the service (section 3) | corrected |
| 8 | [spec/lean-service.md](spec/lean-service.md) | "Nothing in `ve` calls the service yet" | the relay is the main path (section 3) | corrected |
| 9 | `docs/trust-baseline.json`, `section11` | per-file classes for 12 `*Main.lean` files ("NormsMain.lean", "RightsMain.lean", "RiskMain.lean", …) | those files no longer exist | waits: batch AR-4 drops `section11`; `lean-first/b13b`, `lean-first/b16d`, `question-answering/q2` and `readings-defaults/rd6b` edit this file |
| 10 | [CONSOLIDATION-PLAN.md](CONSOLIDATION-PLAN.md) | pinned decoder total 16,985, "may shrink but not grow" | the total is in section 1's counts table | corrected |
| 11 | lean-first plan (`docs/LEAN-FIRST-PLAN.md` on branch `design/lean-first`), section 5 | about 14,000 Python lines deleted by batch 18; batch 16 as 16a/16b | the review measured net −607 `ve/` lines from the lean-first base to `c24aeab2`; 16 is split into 16a–16g (DRI ruling, 2026-10-09) | recorded here: the plan is not on `main` |

When a waiting row's reason clears, the next batch that may edit that file applies the correction and changes the
row to "corrected"; the test then requires the stale text to be gone from the file or marked superseded.

## 7. Re-measuring

`python3 tools/architecture_numbers.py --write [--rev REV]` measures the committed tree of `REV` (default `HEAD`),
saves `docs/architecture/numbers.json` and re-renders every table between `numbers` markers;
`--check` only compares the map with the saved file. The figures the tool does not take come from these commands
(review section 7):

| Number | Command |
|---|---|
| Python change since the lean-first base | `git diff --shortstat f4142cb9 HEAD -- 've/*.py' 've/**/*.py'` |
| Commits editing an inventory | `git rev-list --count --no-merges --since=2026-09-26 HEAD -- <file>` |
| Merges into `main` | `git rev-list --count --merges --first-parent --since=2026-09-26 HEAD` |
| Near-copies in Lean | `git diff --no-index --shortstat lean/VE/Closure/<F>.lean lean/VE/Core/<F>.lean` |
| Trust budget against a base | `python3 tools/trust_map.py --since <base>` |
| Identity sites, null helpers, mode spellings, code-prefixed literals | text search for `"ve-` domain strings passed to `digest`, `soft_digest` or `sha256`, for `if item is not None}`, for `"risk-eval"`, and for `"(InvalidInput\|SyntaxError\|…)[:(]` under `ve/` and `lean/VE` |
| Review-finding classes | B-marked lines in `manage-agents/{lf,rd,e2}-*{review,looprecheck}*.final.md`, classed by hand |
