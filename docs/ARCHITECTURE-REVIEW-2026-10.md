# Architecture and tech-debt review, October 2026: a ranked, buildable plan

**Status:** Draft 1, 2026-10-10, branch `design/arch-review` from `main` at `c24aeab2` (lean-first 16c merged).
Planning only: no code, proof or test changes. Lead request of 2026-10-09: look at VE the way a senior staff
engineer at a frontier lab would, and optimise the architecture before the project grows further.

**Method.** Every figure below comes from `git` history, line counts or text search on `c24aeab2`, or from a cited
report, review file or commit. The review environment did not allow running Python, Lean or the test suite, so no
timing, build or test result is new here; where a batch needs a number that only a run can give, the batch measures
it first. Estimates are marked *estimate*. Section 7 lists the commands, so every number can be re-taken.

**Inputs.** `docs/ARCHITECTURE-LAYERS.md`, `docs/ARCHITECTURE-LAYERS-PLAN2.md`, `docs/CONSOLIDATION-PLAN.md`,
`design/lean-first:docs/LEAN-FIRST-PLAN.md` (draft 3) with the DRI answers (`manage-agents/lean-first-dri.md`,
including the rule-3 decision A of 2026-10-08), `tools/layer_policy.py`, `tools/check_rust_deps.py`,
`docs/trust-baseline.json`, the earlier architecture reviews (`manage-agents/arch-review-astra.final.md`,
`manage-agents/reviews/arch-review-fable.md`), `manage-agents/FINDING-CLASSES.md`, `manage-agents/FOLLOW-UPS.md` and
the lean-first and readings-defaults review and recheck files (`manage-agents/{lf,rd,e2}-*{review,looprecheck}*.final.md`).

## 0. Summary

The direction is right and mostly executed. Lean decides meaning and acceptance, Python relays and displays, Rust
proposes search candidates that Lean checks. In the 14 days to 2026-10-09, 101 branches merged into `main`, among
them lean-first batches 0–13a, 15a, 15b, 16a–16c and 17. What follows is about the four things that now grow with
every feature, and about what to change so that they stop growing.

1. **The boundary between Python and Lean is rebuilt by hand for every route.** Lean answers are checked in six
   different ways (section 2.4), JSON null is handled four ways, Lean has 25 `runCaseReported` wrappers that each
   turn an error into a row, and a route's mode name appears in at least 12 files. The largest class of open review
   findings in the lean-first and readings batches is an unbound or untyped Lean answer: at least 23 B-level findings
   in 13 batches (section 2.10). The fixes often re-derive Lean's content in Python to "bind" it: the document
   coverage is recomputed in `ve/document.py:508-540`, and Python still builds identity hashes at 36 sites in 18
   modules. That recreates the duplication lean-first exists to remove.
2. **Hand-kept inventories tax every change.** Of 629 commits that changed Lean sources since 2026-09-26, 346 also
   edited the hash list `lean/VE/Route/frozen-sources.sha256`, which today lists every one of the 391 `VE` modules.
   In the same 14 days `lean/VE/Audit.lean` was edited by 202 commits, the 13,747-line test-ID list
   `tools/gate-collection.json` by 274 and `lean/checkers.lock` by 159. Merge syncs resolve their conflicts with a
   model worker under the rule "Lean audit manifest = union" (`manage-agents/merge-train.sh:50`).
3. **The trusted base doubled, and its budget is reset at merges.** The trust map's untied verdict-bearing Lean
   (`V`) went from 17,113 to 35,892 lines across the history of `docs/trust-baseline.json`; the signed allowances in
   that history add up to 1,515 `V` lines, and the rest arrived through re-baselining entries. Trusted Lean is now
   46,563 of 151,450 lines. The pinned decoder total, which the consolidation plan said "may shrink but not grow"
   (16,985), is 27,833 (`ve/assurance-manifest.json`). Consolidation steps 2b–10 have not started; the last
   consolidation merge was on 2026-10-05.
4. **Python is not shrinking.** Since the lean-first base (`f4142cb9`, 2026-10-04) the `ve/` Python files lost
   10,908 lines and gained 10,301: net −607 against the plan's expected ~14,000 by batch 18. The new lines are
   mostly the readings S2 work (`readings_verdicts.py` 1,637, `readings_sup.py` 611, `readings_s2_*` 1,055) and new
   transports. Batches 16g and 18 will delete more, but new features keep adding Python decision-adjacent code.

**Eight structural changes, ranked** (section 3): T1 one route contract (binding by construction, one route
registry, one Python relay pattern); T2 typed diagnostics in Lean; T3 generated, merge-safe inventories and a narrow
freeze; T4 a trust budget that only shrinks without a signature, and the consolidation steps resumed; T5 a Python
layer map that matches lean-first, checked by a real import tool; T6 one evidence toolkit, report tests out of the
suite, bulky evidence out of the checkout; T7 module splits after the deletions; T8 identities owned by Lean.

**Batch plan** (section 4): nine batches can start now, touch only tools, tests and docs, and collide with no
running batch (*estimate* 26–35 builder hours). Eighteen wait for lean-first batch 18 (and, for readings, for
RD-7) (*estimate* 61–91 h). The Lean consolidation batches wait for lf-14a–d and lf-18 and follow the converged
consolidation plan. Nothing here changes the VE language, the one-reading rule or any text people read or write;
user-facing diagnostics stay English sentences from Lean.

**Decisions for the DRI** (section 5): the binding contract (D1), what stays hash-frozen (D2), the trust ratchet
(D3), where report tests and bulky evidence live (D4), the Python layer map (D5), typed codes (D6), identity owners
(D7), and whether lf-18 absorbs AR-10's handshake half (D8).

## 1. Current architecture

### 1.1 Layers and sizes

```
 people, editors, web app, agents
          │  files, CLI, JSON
 ┌────────▼─────────────────────────────────────────────────────────┐
 │ Python ve/ (38,587 lines)                                        │
 │   CLI ve/__main__.py, documents ve/document.py, display and      │
 │   English rendering, assist, adapters                            │
 │   route modules (soft_route, rights_route, readings_route, ...)  │
 │   ve/backends (4,129): relay → lean_service pool → schemas ──────┼──► Rust `ve` JSON-lines pool
 └────────┬─────────────────────────────────────────────────────────┘     (search, untrusted, rule 3)
          │ JSON lines: {id, mode, cases, environments?} → bound rows
 ┌────────▼─────────────────────────────────────────────────────────┐
 │ Lean ve_service (Serve.lean → VE.Service.Protocol, 31 modes)     │
 │   runners per profile: VE.<Profile>.Run, Wire, Admission, ...    │
 │   kernel and logic: VE.Syntax/Semantics, Core, Closure, Order    │
 │   ResponseShape: schemas, encoders, fits proofs                  │
 └──────────────────────────────────────────────────────────────────┘
 one-shot Lean executables still called in production: ve_conformance, ve_metered,
 ve_senses_route, ve_speech_acts_route (section 2.4)
```

| Part | Where | Size | Notes |
|---|---|---:|---|
| Lean, all classified sources | `lean/**/*.lean` | 151,450 lines | trust map classes (1.5); 391 modules under `VE/` |
| Lean service | `lean/VE/Service/*`, `lean/Serve.lean` | Protocol 854, Standalone 1,293, Document 922, Family 812, … | 31 modes (`Protocol.lean:69-114`) |
| Response shapes | `lean/ResponseShape*`, `lean/ResponseDecode.lean` | about 60 files | schemas, encoder proofs (`runMode_fits`, `ResponseShape/Encoders.lean:37`) |
| Generated Lean inventories (committed) | `lean/statements.txt`, `declarations.txt`, `axioms.txt`, `predicates.txt` | 34,448 + 16,677 + 4,999 + 1,042 lines | written by `tools/lean_statements.py` and `lean/audit.py` |
| Python relay and transport | `ve/backends/` | 4,129 lines + 7,165 generated JSON schema lines | `relay.py` 167, `lean_service.py` 952, `service_schema.py` 590 |
| Python CLI, documents, display, English, assist | rest of `ve/` | about 34,500 lines | largest: `english.py` 2,147, `document.py` 1,719, `readings_verdicts.py` 1,637 |
| Rust | `rust/ve-kernel`, `ve-profile`, `ve-core` (facade), `ve` (binary) | 2,320 + 2,025 + 21 + 488 lines | down from 7,654 at the lean-first base |
| Tools | `tools/` | about 18,000 lines Python | gate, selection, A/B, fuzz, trust map, layer checkers |
| Tests | `tests/` | 98,896 lines: 337 test files, 19 helper modules; 13,745 collected test IDs | plus about 19,100 lines of Python in `conformance/` |
| Docs and evidence | `docs/` | 135 MB, of which `docs/lean-first/` 127 MB | a checkout is 375 MB without `.git` |

### 1.2 Module boundaries and the layer checkers

`tools/layer_policy.py` is the single table of five layers (kernel, profiles, surface, tools, apps) for Python and
Lean; `tools/check_python_layers.py`, `tools/check_lean_imports.py` and `tools/check_rust_deps.py` enforce
inward-only imports against exception ledgers. Today the ledgers hold 42 Python edges
(`tools/layer-exceptions.json`, 30 of them from kernel, profile or surface modules into `ve.backends`), about 22 Lean
edges (`tools/lean-layer-exceptions.json`, mostly the legacy `Core` and `TableauExtended*` proofs importing
`Closure` and `Route` machinery) and no Rust edge (`tools/rust-module-exceptions.json` is `{}`). Rust's crate
split is done: `ve-kernel` and `ve-profile` are separate crates, `ve-core` is a 21-line facade, so cargo enforces
the Rust boundary.

The Python layer table predates lean-first. It files `entailment`, `evaluate`, `norms`, `rights`, `softnorms` and
`units` as layer 2 "profiles" (`layer_policy.py:19-20`) although they are now relays and containers, and it files
the relay (`ve.backends`) as layer 4, so every module that relays Lean's answer is an exception. Under lean-first
rule 2 the transport is the innermost Python layer, not the outermost (T5).

### 1.3 The wire contract and the response shapes

- **Protocol.** One JSON line per request, `{"id", "mode", "cases", "budget"?, "environments"?}`; one line per
  response, with result `i` as `{"digest", "index", "result"}`, where `digest` is the SHA-256 of case `i`'s text as
  the client sent it (`docs/spec/lean-service.md:17-39`, `lean/VE/Service/Protocol.lean:30-60`). Environments can be
  registered once and named by handle (lean-first F2).
- **Modes.** 31 modes, each mapped to a runner `Json → Json` (`Protocol.lean:132-163`) and pinned by an `rfl`
  theorem (`Protocol.lean:671-721`). Statement-layer runners dispatch on a `kind` string and delegate cases they do
  not claim down a chain (rights → soft norms → norms → route, `Rights/Run.lean:403-407`,
  `SoftNorms/Run.lean:377-385`).
- **Diagnostics.** Runners return `Except String`. The service derives the public `code` from the message's text
  before the first colon (`rejectionCode`, `Protocol.lean:191-195`); the soft-norms route keeps its own table of
  25 message prefixes and three further text tests (`SoftNorms/Run.lean:411-447`). About 1,300 string literals in
  `.lean` files under `lean/VE` begin with one of the 12 public code names followed by `:` or `(`.
- **Response shapes.** Written once as Lean data (`lean/ResponseShape/Schemas/*.lean`, 31 files), rendered to the
  JSON files in `ve/backends/lean_service_schema/` by `tools/response_schemas.py`, and interpreted twice: by
  `ve/backends/service_schema.py` in the client and by `ResponseShape.check` in `ve_response_decode`, with a test
  that the two agree (`tests/test_lean_service_schema.py`). The dialect is JSON Schema plus 17 extension keywords
  (`lean_service_schema/README.md:83-104`). Every mode's encoder is proved to fit its shape (`runMode_fits`).
- **Binding.** Binding a field to the request is opt-in, keyword by keyword (`echo`, `equals`, `references`,
  `count`, `length`, `zip`, `index`, `digest`). A text search of the schema modules finds 307 bare `str` leaves
  against 120 binding keywords; AR-11 replaces this rough count with an exact census.
- **Threat model.** The client checks binding and well-formedness and "does **not** re-derive semantic content"
  (`docs/spec/lean-service.md:14-15, 41-60`). The build checklists and reviews of the lean-first batches ask for a
  binding of every named ID and count, and the fixes meet that by recomputation in Python (2.1, rows P2 and P3).
  The spec and the practice disagree; decision D1 settles it.
- **Rust.** A pool of JSON-lines `ve` processes (`ve/backends/rust_jsonl.py`, schema
  `ve/backends/rust_schema/jsonl.json`); Lean checks every witness Rust reports (rule 3, decision A).

### 1.4 Data flow per main operation

- **Formula operations** (`ve parse|check|evaluate|countermodel`): `ve/__main__.py` reads files and builds the
  `Environment` after Lean's `environment` mode accepts it (`ve/backends/validation.py`); parsing and typing go
  through `ve/backends/dispatch.py`, whose default authority is still `python` for operations that are not single
  owner yet (`dispatch.py:100`; lf-13b flips the covered ones, lf-18 removes the authority); evaluation and
  countermodel search use Rust's evaluator inside search (rule 3) and Lean's checks of every reported value and
  witness; metered evaluation runs as a one-shot `ve_metered` process per call (`ve/backends/lean_runner.py:78,84`).
- **Document check** (`ve document check FILE`): `ve/document.py:_load` sends a `ve-document@1` text to Lean's
  `document` mode (`document.py:387-402`); when the mode answers `CheckerUnavailable` or `ResourceLimit` (profiles it
  does not own yet, lf-16d–16f), Python's own path `_load_document` (`document.py:553-835`) calls each profile's
  route; `ve-document@2` goes through Lean's discourse admission first. `_report` (`document.py:1226-1443`) builds
  the coverage and the report for display. lf-16g deletes the Python path once the residue ledger is empty.
- **Statement-layer route** (for example rights): the route module builds a case from the environment and units,
  drops nulls in its own way (`ve/rights_route.py:6-12`), and calls `relay.decide_once("rights", case)`; the service
  runs `VE.Rights.Run.runCaseReported`; the client checks the envelope and the row against the generated schema;
  Python reads fields for display.
- **English admission** (`parse_english`): `ve/english.py` → `ve/backends/english_lean.py` → mode `english.read`;
  Lean's reader decides one reading or a rejection; Python's `EnglishParser` runs only as a shadow comparator
  (`english_lean.py:1-7`).
- **Readings** (`ve document readings`): S1 validation is Lean's, relayed; S2 elaboration takes Lean's answer and
  compares it with a Python regeneration of the route, choices, vocabulary, units, names and slot
  (`ve/readings_route.py:48-146`); verdicts across readings use Python's prover and model search as generators,
  each piece of evidence checked by a Lean readings kind (`ve/readings_verdicts.py:1-10`).
- **Assist** (`ve assist`): Python session, journal and recovery (editor help); proposals are untrusted and every
  "yes" is replayed through Lean (lf-17).

### 1.5 The trusted base

From `docs/trust-baseline.json` (written by `tools/trust_map.py --write`, last rebaselined at the 16c merge):

| Class | Meaning (consolidation plan 1.1) | Lines |
|---|---|---:|
| K | kernel definitions read once | 997 |
| S | reviewed statements and meaning predicates | 9,674 |
| D | decoders (D[V] verdict-bearing 12,214, D[R] reject-only 996, D[I] identity 527) | 13,737 |
| G | glue (G[V] 23,837, G[R] 1,406, G[I] 229) | 25,472 |
| C, P, T, o | checkers, proofs, tests, other: not trusted | 8,329 / 68,097 / 13,528 / 11,616 |
| **trusted** | K + S + untied [V] (budget 997 + 9,674 + 35,892) | **46,563 of 151,450** |

The rest of the trusted path: the Lean toolchain, compiler and runtime; the restricted JSON reader and the request
splitter (`Protocol.lean:59-60`); in Python, the envelope and binding checks and the wire primitives
(`ve/backends/`, `ve/wire.py`, `ve/environment_wire.py`). Rust is not trusted. `ve/assurance-manifest.json`
("trusted", lines 17-34) is the declared list; it still describes `python` authorities that lf-18 removes.

History of the budget (`trust-baseline.json:29-417`): the first recorded `V` is 17,431 (consolidate-b1, review B3),
then 17,113; one refresh entry moved it to 26,181 by reclassifying modules that had accumulated; later entries,
mostly merges, raised it to 35,892. Signed allowances: K 19, S 327 (one of the S entries is recorded twice), V 1,515
(164 + 952 + 399). `trust_map.py --check` fails on `main` (FOLLOW-UPS, rd-6a round 2).

### 1.6 Where the documents are stale

| Document | It says | Today |
|---|---|---|
| `docs/architecture-and-design.md:3` | "First draft. Implementation, proofs, and usability results are pending." | 151,450 Lean lines; `lean/audit.py` passed 4,327 theorems on 2026-10-06 (lf-7 recheck) |
| `docs/implementation.md:1-7` | "Experimental Python VE v0 core … supports exactly `ve.core@0`, `relational-fol@0` … no third-party runtime dependencies" | Python is the CLI and relay; `pyproject.toml:10-16` lists five runtime dependencies |
| `docs/ARCHITECTURE-LAYERS.md:12, 23-28` | Rust "one crate holds all three groups until the crate split" | `ve-kernel`, `ve-profile`, `ve-core` facade |
| `docs/ARCHITECTURE-LAYERS.md:15` | Lean entry points `NormsMain`, `SoftNormsMain`, `RightsMain`, … | deleted by lean-first batch 1; `lakefile.toml` has 9 executables |
| `docs/ARCHITECTURE-LAYERS.md:52-55` | the service is "still outside the `ve` command path" | `relay.py:22-24`: every statement-layer route is a service mode |
| `docs/ARCHITECTURE-LAYERS.md:77-79, 92-96` | "12 Python edges plus the assist CLI app edge" | 42 entries in `tools/layer-exceptions.json` |
| `docs/INTEGRATION-GAPS.md:31, 35, 39, 41` | the service "is not yet called by `ve`"; alternatives, reports, quantity are not service modes | all are modes (`Protocol.lean:69-108`) |
| `docs/spec/lean-service.md:7` | "Nothing in `ve` calls the service yet" | the relay is the main path |
| `docs/trust-baseline.json:418-3582` (`section11`) | per-file classes for 12 `*Main.lean` files | those files no longer exist |
| `docs/CONSOLIDATION-PLAN.md:80-81` | pinned decoder total 16,985, "may shrink but not grow" | 27,833 (`assurance-manifest.json` `lean_decoders.total_lines`) |
| lean-first plan, section 5 | expected ~14,000 Python lines deleted by batch 18; batch 16 as 16a/16b | net −607 so far; 16 split into 16a–16g by DRI ruling (2026-10-09) |

## 2. Debt and risk inventory

### 2.1 Duplicated logic remaining after lean-first

Python-side, with the batch that removes it today, if any:

| # | Logic | Where | Scheduled | Left after lf-18 |
|---|---|---|---|---|
| P1 | Document wrapper, unit statuses, coverage for documents Lean's mode refuses | `ve/document.py` 553–835, 1226–1443; Lean `VE/Service/Document.lean` | lf-16d–16g | none, if 16g's precondition holds |
| P2 | Coverage arithmetic recomputed to "bind" Lean's document answer | `document.py:508-540` (bytes by kind and status, residual counts, compared whole) | none | all → D1, AR-11 |
| P3 | Identity preimages built in Python (`digest("ve-<domain>…")`) | at least 36 sites in 18 modules (9 of them Python's own records in `argument.py`, `adapters/records.py`, `propose.py`), for example `document.py:181, 431`, `norm_defaults_route.py:58`, `readings_verdicts.py:1354-1357`, `backends/speech_source.py:296-301` | lean-first rows 12–13 ("small") | most → AR-6, AR-15 |
| P4 | Readings S2: route, choices, vocabulary, units, names, slot regenerated and compared with Lean | `readings_route.py:48-146`, `readings_sup.py` | RD-7 deletes the superposed fold and wording selection | the regeneration compare → AR-17 |
| P5 | Speech scope regenerated from authored units | `backends/speech_source.py:59` | none | → AR-12c |
| P6 | Python copies of Lean tables | modes `service_schema.py:22-26`, deadlines `lean_service.py:117-128`, code classes `relay.py:57-63`, senses statuses and budgets `senses.py:24-26` ("checked against compiled Lean in tests"), `MAX_CHOICES = 64` `readings_sup.py:17` | lf-18 (classes, I/O caps) | modes, deadlines, statuses → AR-10 |
| P7 | Limits | `ve/limits.py`; `10000`, `10_000`, `maxNodes` or `MAX_NODES` occur 114 times in 53 files under `lean/VE` (not all the node limit) | lf-18 (`VE/Limits.lean`) | — |
| P8 | English: Python comparator parser, Lark grammar, vocabulary lint, statement-layer English | `ve/english.py`, `ve/*_english.py`, `ve/surface/` | English track E3 | — |
| P9 | Test oracles that copy logic on purpose | `conformance/english_lean_{engine,lexer,lexicon}.py` (1,441 lines), frozen norm-defaults and soft oracles | deleted after lf-18 plus 14 clean days (lean-first 6.2–6.3) | — |
| — | Rule-3 accelerators: `eval.rs`, the order evaluator, the provers' Python replay | | kept by decision A (2026-10-08): untrusted, never reported, differential-tested | not debt |

Lean-internal (one owner applies inside Lean too):

| # | Logic | Where | Scheduled |
|---|---|---|---|
| L1 | Closure, Core and root `TableauExtended*` copies | 14 file pairs, about 2,050 lines in `VE/Core/`; the 12 pairs compared differ by 2 to 57 inserted lines; `Core/Paths.lean` differs from `Closure/Paths.lean` only in its namespace lines; `Core.Formula` adds the n-ary `atom` case (`Core/Substitution.lean:23`) | consolidation step 3, not scheduled → AR-20–23 |
| L2 | Admission skeleton restated per profile | `Route/Admission`, `Norms`, `NormDefaults`, `SoftNorms`, `Rights`, `Alternatives`, `Risk`, `Time/Document`, `Attribution` (consolidation plan step 4) | not scheduled |
| L3 | Per-route wrappers | 25 `runCaseReported` definitions; `norms_wire_acceptance` (`Norms/Run.lean:176`), `soft_wire_acceptance` (`SoftNorms/Run.lean:387-408`) and `rights_wire_acceptance` (`Rights/Run.lean:409-429`) repeat one proof script | consolidation step 7, not scheduled → AR-24 |
| L4 | Two owners of environment diagnostic texts | the document mode's walks and batch 12's located decoders (`docs/INTEGRATION-GAPS.md:45`) | "a follow-up" → AR-16c |
| L5 | Legacy profiles worked out a second time in the error path; `Legacy.family` repeats the checker's name | `Service/Standalone.lean:214, 239, 442` (FOLLOW-UPS lf-15a) | → AR-16c |
| L6 | Canonical array and object handling copied | `CertificateWire.lean:140` (FOLLOW-UPS lf-16c) | → AR-20 |
| L7 | `decodeSoftDoc`, `decodeFilledDoc`: copies of `Route.Admission.decodeDoc`; `bind_ok` (about 900 uses) lives in `Order/ProfileGate` | consolidation 4a | → AR-20 |

### 2.2 Large modules

Files over about 1,500 lines, and the next tier where it matters:

| File | Lines | Owner of the change |
|---|---:|---|
| `ve/english.py` | 2,147 | English track (E3) |
| `ve/document.py` | 1,719 | lf-16g deletes about 900; AR-16a splits the rest |
| `ve/readings_verdicts.py` | 1,637 (91 function-level imports) | RD-7; AR-16b after it |
| `ve/assist/recovery.py`, `ve/assist/session.py` | 1,359, 1,338 | AR-9 (no running batch touches them) |
| `lean/VE/Audit.lean` | 4,805, hand-appended | AR-1 generates it |
| `lean/VE/Readings/VerdictsWire.lean`, `Readings/Separate.lean` | 1,565, 1,499 | readings track |
| `lean/VE/Service/Standalone.lean` | 1,293: S 250, D 462, G 527 trusted-class lines in one file; 42 commits in 14 days | AR-16c after lf-18 |
| `lean/VE/EnglishGrammar/LexiconFixtures.lean`, `Grammar/TableInvariant.lean` | 1,714, 1,658 | fixtures and proof; leave |
| `tests/test_discourse_lean.py`, `test_speech_acts_conformance.py`, `test_assist.py`, `test_readings_s2_document.py` | 2,173, 2,096, 1,862, 1,647 | split with their modules |
| `tools/difffuzz.py` | 2,059 | leave |

Proof files are large without much harm; what matters is trusted glue in one file (`Standalone.lean`) and Python
modules that mix transport, binding, generation and display (`document.py`, `readings_verdicts.py`).

### 2.3 Cyclic and leaky dependencies

- **Python, inverted by lean-first.** 30 of the 42 layer exceptions are kernel, profile or surface modules calling
  `ve.backends` (`tools/layer-exceptions.json:2-42`); their reason text still says "place the dispatch and checker
  clients below the kernel when stage 5 deletes the Python bodies". 646 indented relative imports in 65 modules
  hide cycles at run time (`readings_verdicts.py` 91, `document.py` 69, `readings_route.py` 33, `norms.py` 33).
  `ve/__init__.py:31-34` imports the English parser and the argument checker for every `import ve`.
- **Lean.** About 22 exception edges, mostly legacy `Core` and `TableauExtended*` proofs (L1). `Service/Protocol.lean`
  imports 27 modules: every route links into one `ve_service` binary (170–180 MiB), so any Lean change relinks the
  service, re-locks `checkers.lock` and, through test selection's rule for executables (`docs/TESTING.md:17`),
  selects every test that starts the service.
- **Mirrored tables across languages** (P6, P7): a Lean change to a mode, a budget or a status word has a Python
  twin to edit, kept equal by tests.
- **Rust.** None at the crate boundary; `tools/check_rust_deps.py` (648 lines, a hand-written Rust tokenizer) still
  checks module groups inside crates that the split made single-group (AR-8).

### 2.4 Inconsistent patterns across routes

| Concern | Variants on `main` | Evidence |
|---|---|---|
| Transport | service pool through the relay; one-shot processes: `graph.compose` and `bundle.check` (`ve_conformance`), metered `evaluate` and `countermodel.search` (`ve_metered`), senses (`ve_senses_route`), speech source (`ve_speech_acts_route`); Rust JSON-lines pool | `argument.py:531`, `bundle.py:95`, `backends/lean_runner.py:78,84`, `backends/senses.py:328`, `backends/speech_source.py:271`; lean-first batch 1 had moved every route into the service, and later batches added one-shots again |
| Checking a Lean answer | (1) generated schema (`service_schema.py`); (2) type strings `"array<string>"` (`backends/lean.py:138-166`, `speech_source.py:23-30`); (3) predicate combinators `_obj`, `_arr`, `_either` (`readings_route.py:228-304`); (4) predicate functions (`senses.py:29-60`); (5) `_need` binders (`readings_verdicts.py`, 45 sites; `readings_route.py`, 38); (6) `require` with recomputation (`document.py:458-540`) | six styles, one rule |
| JSON null | omit (`rights_route.py:6-12`, `backends/soft_relay.py:27-33`, `readings_s1.py:33-36`); omit and send the null paths for Lean to restore (`reports_route.py:17-38`); Lean's front-matter rules (lf-16c review B2: 107 accepted-to-rejected flips) | four policies |
| Answer post-processing | `{k: v for k, v in row.items() if k not in ("id", "status")}` | 5 copies: `norm_defaults_route.py:112`, `readings_route.py:146,169`, `soft_route.py:65`, `rights_route.py:58` |
| Error code | parsed from the message prefix (`Protocol.lean:191`); the soft route's own prefix table (`SoftNorms/Run.lean:411-447`) | a reworded message can change its code |
| Lean runner | 25 `runCaseReported`; kind dispatch by string; delegation by `uses<X>Path`; copied acceptance proofs | L3 |
| Mode names | spelled in Lean and again in Python and tests | `"risk-eval"`: 18 occurrences in 12 files |
| Caches | `relay.decide_once` (`relay.py:150-167`), the soft rule cache (`soft_relay.py:18-20`) | each route chooses its own |

### 2.5 Hash-frozen and locked files

Commits since 2026-09-26 that edited each file (2,376 non-merge commits in that window; 629 touched Lean sources):

| File | What it pins | Commits | Problem |
|---|---|---:|---|
| `lean/VE/Route/frozen-sources.sha256` (391 lines) | SHA-256 of every `VE/*.lean` module (`frozen.py:20-33`) | 346 | every Lean edit is re-hashed by the same worker, so it records that a file changed, which `git` already does; the per-module hashes are also in `lean/declarations.txt` |
| `lean/VE/Audit.lean` (4,805) | one `#print axioms` line per theorem, by hand | 202 | the most edited Lean file; `lean/audit.py:80-112` finds theorems with a regex scanner |
| `ve/assurance-manifest.json` (3,963) | decoder files by SHA-256, line count and ranges; authorities | 176 | a third hash ledger over the same files |
| `lean/checkers.lock` (138) | built binary hashes | 159 | changes with every Lean change |
| `lean/axioms.txt` (4,999) | audit output | 84 | generated, committed |
| `lean/Main.lean` | `MAIN_BASE` hash (`frozen.py:15`) | — | intended and narrow; keep |
| `ve/wire_contract/contracts.lock`, `ve/english_grammar/LOCK.json` | generated tables | — | intended; keep |

### 2.6 Manifests and inventories kept or regenerated by hand

| Inventory | Lines | Commits | Generated by | Conflict on merge |
|---|---:|---:|---|---|
| `tools/gate-collection.json` (every test ID) | 13,747 | 274 | `tools/gate_collection.py --write` | every branch that adds a test |
| `lean/VE/Audit.lean`, `lean/ResponseShape/Audit.lean` | 4,805, 429 | 202 | by hand | "union" by a model worker |
| `lean/statements.txt`, `declarations.txt`, `predicates.txt` | 34,448, 16,677, 1,042 | 44, 112, — | `tools/lean_statements.py` | regenerate |
| `docs/trust-baseline.json` | 12,826 | 25 | `trust_map.py --write` plus hand-written history | duplicated history entries; stale `section11` |
| `conformance/difffuzz-baseline.json` | 50,925 | 24 | `--update-baseline` plus hand follow-up IDs | regenerate and re-triage |
| `tools/layer_policy.py`, `layer-exceptions.json`, `lean-layer-exceptions.json` | 188, 44, 24 | 40, —, — | by hand | small |
| `tools/relay_lint.py` `RELAYED` | — | — | by hand per batch | small |
| `tools/consolidation-ledger.json` | 85 | — | by hand | rare |
| Python mode and deadline tables, `tests/lean_routes.py` | — | — | by hand (P6) | small |

`manage-agents/FOLLOW-UPS.md` (rd-2a round 1) records one effect: "A trial merge conflicts in 7 generated or
inventory files; the merge train needs to regenerate them."

### 2.7 Test architecture

- **Size and cost.** 13,745 collected test IDs; about 20,000 CPU seconds for the suite (`docs/TESTING.md:47`); 25.3
  minutes at `-n 16` under load 88–105 (`docs/testing-profile.md:193`); longest test 271 s (`:137`). Tests are 2.6
  times the size of `ve/` in lines.
- **Report tests.** 27 test files (about 2,800 lines) check one batch's saved evidence, for example
  `test_b15b_evidence.py`, `test_lean_first_b12_report.py`, `test_readings_defaults_rd3_report.py`. They stay in the
  default suite for good. Two branches each failed a report test after syncing with `main`, from stale evidence
  or a live `git diff` (`manage-agents/CURRENT-STATE.md`, 2026-10-07 17:20Z: lf-6 and lf-10b).
- **Process-named tests.** 13 files are named after a review round or an amendment (`test_w6a_looprecheck1.py`,
  `test_p1_amendment7.py` to `test_p1_amendment15.py`, `test_soft_review_regressions.py`); their names say when a bug
  was found, not what behaviour they hold.
- **Per-batch evidence code.** 70 Python scripts under `docs/lean-first/b*/` and `docs/readings-defaults/` are
  copies of a few tools: `latency.py` 10 times, `report.py` 9, `difffuzz_ab.py` 5, mutant seeding 6. Three
  findings were false passes inside such copies: `docs/lean-first/b1/latency.py:57` (results keyed by file name),
  `docs/lean-first/b10a/trace_fuzzer.py` (stops hashing before the baseline replay) and
  `docs/lean-first/b10b/fuzzer_gate.py:85`; a fourth was in the shared A/B tool, which accepted empty evidence (lf-0).
- **Selection.** Lean changes select tests by executable; since `ve_service` contains every route, a one-line Lean
  change selects every test that starts the service. Product-module changes are coarse too (`TESTING.md:23`).

### 2.8 Build and tooling friction

- A Lean edit costs a rebuild (9 minutes from scratch on a quiet machine, more than an hour at the load of
  2026-10-04: lean-first 7.4), a re-hash, an audit line, `axioms.txt`, three statement dumps, a re-lock, perhaps
  regenerated schemas and a trust-baseline entry; then each sync of `main` into the branch is a model-worker merge.
- Hand-rolled scanners of real languages: the Rust tokenizer (`check_rust_deps.py`), the theorem regex
  (`audit.py:80-112`), the Python import resolver (`layer_policy.py:43-87`). `FINDING-CLASSES.md` class 7 (33
  findings, layers2-b1 took 5 rounds) recommends the real tool as oracle.
- No static type checker for Python. Lean rows are dicts; in lf-10b six B findings were English helpers reading
  attributes of legacy objects from Lean rows (`norm_defaults_english.py:155, 257, 278, 284, 359`).
- The core package pulls in model-API libraries at run time (`google-genai`, `httpx`, `tokenizers`:
  `pyproject.toml:10-16`) for the assist and experiment code.
- A checkout is 375 MB; `docs/lean-first/` is 127 MB of it (`b15b` 64 MB, `e2` 30 MB), copied into every worktree.

### 2.9 Naming and documentation drift

- Plan-stage names in code: `readings_s1.py`, `readings_s2_*.py`, `readings_sup.py`, `tools/stage2_parity.py`,
  `tools/b17_ab.py`, `tests/b15b_model_cases.py`.
- "Route" means a service mode, a statement-layer runner (`VE/<Profile>/Run.lean`) and the P0 admission runner
  (`VE/Route/*`) at once.
- Python inside the Lean tree: `lean/VE/Route/frozen.py`, `lean/VE/Service/english_copy.py`,
  `lean/VE/Route/examples/*.py`.
- 16 `PLAN*.md` files at the repository root; architecture is described in at least five documents, several stale
  (1.6).

### 2.10 Review-finding history

`FINDING-CLASSES.md` (about 800 findings to 2026-10-04) ranks Python/Lean/Rust disagreement first (124 findings),
vacuous tests or gates second (70), and names incomplete schemas for untrusted responses (21 findings, 5.5 rounds
open on average) and hand-rolled scanners (33). Features with duplicated implementations took 6.6 fix rounds against
3.4. For the lean-first and readings batches since then, the B-level items in their review and recheck files fall,
by a hand classification, into:

| Class | B findings (at least) | Batches | Examples |
|---|---:|---|---|
| Lean answer unbound, untyped or not contained | 23 | lf-0, 1, 2, 3, 4, 5, 8, 11b, 13b, 16b, 16c, rd-3, lf-9 | `lf-13b-review` (assumption names, certificate counts), `lf-16b-review` (spans and `accounted_bytes`), `rd-3-review` B1–B2 |
| Gate or evidence that passes when it should not | 14 | lf-0, 1, 7, 10b, 11b, 12c, 15b, 16a, 17, rd-6a | empty A/B evidence passes; latency keyed by name; final-HEAD gate not evidenced |
| Diagnostic texts changed without a signature | 9 | lf-7, 8, 11a, 11b, 12, 16b | 730 wording and 544 order records unsigned (lf-12) |
| Python display code broken by Lean rows | 6 | lf-10b | `AttributeError` on legacy objects |
| New duplicate logic inside Lean | 1, and 2 follow-ups | lf-15a, 16c | a fourth copy of the layer projection |

The method: every line starting with a B marker in `manage-agents/{lf,rd,e2}-*{review,looprecheck}*.final.md`,
read and classed by hand; confirmations of earlier fixes are not counted.

### 2.11 Risks that grow with size

1. **Trusted base.** 46,563 trusted lines and rising with each profile; the budget follows the code (1.5).
2. **Binding creep.** Each new route adds Python that re-derives some of Lean's answer to satisfy "bind every field"
   (P2, P3, P5): the duplication class returns through the relay.
3. **Inventory conflicts** grow with the number of branches in flight, not with the code: two branches that both
   add a theorem conflict in `Audit.lean`.
4. **Profile combinations.** 17 profiles in Python's registry; `docs/INTEGRATION-GAPS.md` lists the pairs that do
   not compose. Each profile adds a gate in Lean's dispatch, a schema, a relay module and tests.
5. **Messages as API.** Codes come from message prefixes, texts are compared byte for byte in tests and A/B, and
   every wording improvement is a signed `DELTA` (2.10).
6. **One service binary.** Build, link, lock and test selection scale with the whole Lean tree.
7. **Evidence in the tree.** 127 MB after 30 batches, in every worktree.
8. **Report tests.** Each batch adds permanent tests about its own evidence; they fail when a later merge moves the
   evidence.

## 3. Target architecture

Eight changes, ranked by risk removed and time saved per builder hour. Each is incremental: a first step that is
safe now, then batches that switch one route or one profile at a time and delete the old path in the same batch.

### T1. One route contract: binding by construction, one registry, one Python relay

**What.** (a) A short, closed definition of binding (D1): a response field is bound when it echoes, equals, counts,
measures, indexes or references something in the request, or is bounded by a request value; a derived value (a sum,
an identity hash, an unfolding) is Lean's and is covered by a Lean theorem or a `ResponseDecode` invariant, never
recomputed in Python. (b) Every string and integer leaf of every response shape is either bound, in a closed domain,
or explicitly marked as display text; a Lean `#guard` holds the census at zero (AR-11). (c) One Lean registry of
routes from which the mode names, deadlines and handshake come; Python reads them from the handshake (AR-10).
(d) One Python relay call per route, typed rows generated from the shapes, one null policy declared per mode, every
production Lean call through the service (AR-12).

**Benefit.** Turns the largest open finding class (23 B findings) into a build failure; removes the six checking
styles, four null policies and the Python mirrors; stops binding creep (P2, P3, P5). Adding a route touches the
runner, its shape and one registry line, instead of about 12 files.

**Cost.** *Estimate* 26–33 builder hours over six batches (AR-10 to AR-12c), including two dialect keywords
implemented in both interpreters.

**Risk.** Medium: a wrong shape rejects Lean's own answers (lf-16c review B1). Mitigation: every shape change runs
the genuine-answer corpus (`tests/data/route-cases.jsonl`) and the drop, empty and retype mutation suite before it
merges.

**When.** The binding ADR and the census tooling now (AR-7, AR-6); the Lean and relay batches after lf-18, because
lf-16d–16g and 18 edit `Service/Document.lean`, `Protocol.lean` and the relay.

### T2. Typed diagnostics in Lean

**What.** One `inductive Code` and a `Diag` structure (code, English text, optional path) in Lean; producers write
`fail .invalidInput "…"` instead of a string that begins with the code's name; the service's code list is
`Code.all.map Code.name`; route-specific code tables attach codes at the throw site.

**Benefit.** No code is parsed out of a message; a reworded message cannot change a code; tests and A/B can compare
code and path and treat wording as wording. Builds on lf-18's one Python class per code.

**Cost.** *Estimate* 4–6 h for the core, 2–4 h per profile. **Risk.** Low: wire texts stay byte-identical (the
format function reproduces today's text), and the A/B shows it. **When.** After lf-18.

### T3. Generated, merge-safe inventories and a narrow freeze

**What.** The audit manifests are generated from the compiled environment; the hash freeze covers only files whose
bytes are a frozen contract or hold kernel definitions; the expected test collection comes from the merge base at
gate time; the trust baseline keeps budgets and signed allowances only; generated dumps are regenerated, never
merged by hand.

**Benefit.** Removes the most frequent edits of the last two weeks (346, 274, 202 commits) and most merge-sync
conflicts. **Cost.** *Estimate* 12–16 h over four batches (AR-1 to AR-4). **Risk.** Low; each keeps a check at
least as strong as today's (2.5). **When.** Now.

### T4. A trust budget that only shrinks without a signature, and the consolidation resumed

**What.** The budget becomes a ratchet: a merge may lower it; raising it needs a signed allowance in the same merge.
The consolidation plan's remaining steps (2b, 3, 4, 7, 8a, 8b, 9) resume as 2–6 h batches after lf-14 and lf-18,
re-estimated with `trust_map.py --ledger` on the current tree.

**Benefit.** The trusted base is measured and held, as the project rule requires. Consolidation step 3 alone removes
about 1,550 untrusted and some trusted lines and one of four definitions of the logic (consolidation plan 3b–3c).
**Cost.** Policy 3–4 h now; Lean work as planned there. **Risk.** Low for the policy; medium for Lean refactors,
handled by "tie, then delete" and the statement dump. **When.** Policy now; Lean after lf-14a–d and lf-18.

### T5. A Python layer map that matches lean-first

**What.** Python layers become: 1 transport and wire (`errors`, `wire`, `environment_wire`, `limits`,
`backends.*`), 2 containers built from Lean's answers (`ast`, `environment`, `model`, profile containers),
3 display and English rendering, 4 CLI, documents, assist, adapters, route modules, 5 apps. Enforced with
`import-linter` (already a dev dependency) instead of the custom resolver.

**Benefit.** The 30 adapter exceptions disappear because they are no longer outward; the ledger shrinks to real
problems; function-level imports can move back to module level. **Cost.** 3–5 h. **Risk.** Low. **When.** After
lf-18, which deletes `backends/dispatch.py`'s authorities.

### T6. One evidence toolkit; report tests out of the suite; bulky evidence out of the checkout

**What.** `tools/evidence/` holds one implementation of each batch measurement (paired latency with the 20% rule,
corpus A/B, fuzz A/B, mutant seeding, report numbers from evidence); a batch writes an `evidence.toml`, not scripts.
`tools/batch_evidence.py --check <dir>` validates a batch's evidence at its gate and in the merge train, instead of
a permanent `tests/test_bNN_*.py`. Evidence files over 1 MB go to a separate evidence branch, with a manifest of
SHA-256 and size in the tree.

**Benefit.** Fewer false-pass gates (14 findings), no branch gate broken by another batch's report test, a smaller
suite and smaller checkouts.
**Cost.** 5–6 h toolkit, 3–4 h migration. **Risk.** Low; evidence stays in the repository. **When.** Toolkit now
for batches started after it; migration after lf-18.

### T7. Module splits after the deletions

`ve/document.py` after lf-16g; `ve/readings_verdicts.py` after RD-7; `lean/VE/Service/Standalone.lean` after lf-18;
`ve/assist/{recovery,session}.py` now. Splits move code without changing it; they follow deletions so that nothing
is moved twice.

### T8. Identities owned by Lean

**What.** One table of identity domains with an owner each. Python reads Lean-owned identities from Lean's answers
and compares stored identities with Lean's, never recomputing them; Python-only record identities (assist journal,
adapters, proposals) are declared as such.

**Benefit.** Closes P3 and lean-first rule 5 ("Python reads identities from Lean's answers"). **Cost.** 2–3 h
inventory and lint now, 4–6 h switch later. **When.** Inventory now; switch after lf-16g, lf-18 and RD-7.

### Not recommended

- **Splitting `ve_service` into several binaries.** One persistent service is what made calls cheap (lean-first F1).
  Selection precision is better fixed through the registry (AR-10) than by more executables.
- **Generating Python validators from a contract language** (the earlier reviews' proposal and wire-contract S10).
  Lean owns acceptance; Python checks binding only. The shapes are already generated from Lean.
- **New dialect keywords beyond `x-text` and `x-at-most`.** Each keyword is implemented twice (Python and Lean).
- **Rewriting Rust.** It is 4,854 lines, split into crates, and untrusted.

## 4. Batch plan

### 4.1 The gate for every architecture batch

1. **Suite.** The full suite at the batch head in chunks with `VE_NATIVE_PREBUILT=1`, and `tools/gate.py` in a clean
   worktree before the merge.
2. **No behaviour change unless signed.** A batch that touches `ve/` or `lean/` runs `tools/lean_first_diff.py` over
   the nine corpora of the current lean-first gate (the lf-16d task; `tools/batch_evidence.py:21` names seven of
   them) with 0 unlisted differences; any difference is listed in the batch's `DELTA.md` and signed by the DRI.
   The differential fuzzer's baseline must not grow.
3. **Lean.** `lake build`; `lean/audit.py`; `tools/lean_statements.py --check` shows every kept statement
   byte-identical and lists additions; `tools/trust_map.py --since <merge-base>` shows no growth of K, S or untied
   V unless signed; Phase C batches must show a reduction.
4. **Measured outcome.** The batch report states its outcome (lines, files, findings class, commits avoided) from
   numbers its tools generate, not from prose.
5. **English.** A batch that touches English modules (none in Phases A and B) runs the English corpus gate of
   lean-first E2 and keeps the readability evaluation's results.
6. **Lean source gotcha.** `lean/audit.py` forbids the words `sorry`, `axiom`, `unsafe`, `native_decide`,
   `implemented_by`, `partial`, `opaque` and `extern` anywhere in project Lean files, comments included; recursion
   over `Shape` must therefore be structural.

### 4.2 Coordination with running work

Running or queued on 2026-10-10 (`manage-agents/IN-FLIGHT.md`, prompts): lf-13b (fix loop), lf-14a–d, lf-16d–16g,
lf-18; readings-defaults RD-4b, RD-5, RD-6b, RD-7, RD-9; question answering; English E3. Their files:
`ve/admission.py`, `argument.py`, `entailment.py`, `definitions.py`, `bundle.py`, `background.py`, `norms.py`,
`readings*.py`, `document.py`, `backends/dispatch.py`, `relay.py`, `errors.py`, `limits.py`, the assurance manifest,
`lean/VE/{Definitions,Norms,Core,Closure,Order,Readings}/*`, `VE/Service/{Document,Protocol}.lean`,
`ResponseShape/Schemas/Document.lean`, `ve/english*.py`.

- **Phase A** batches touch none of these files except shared inventories (`Audit.lean`, the frozen list,
  `gate-collection.json`, `trust-baseline.json`, the `RELAYED` list of `tools/relay_lint.py`). For those, each batch ships a one-line resolution rule that the
  merge-train sync prompt adopts before the batch merges ("conflict in X: take `main`'s file and run Y").
- **Phase B** starts when lf-18 has merged; its readings parts start when RD-7 has merged; its English parts are
  offered to the English track's owner instead of built here.
- **Phase C** starts when lf-14a–d and lf-18 have merged.
- At its start, each batch lists the files it will touch and checks them against
  `git diff --name-only main...<branch>` for every branch in flight; an overlap moves it back in the queue
  (consolidation plan rule 1.4.5).
- The lead's "speed and efficiency" item covers the pipeline (watchdogs, pacing, fix-round rules). AR-3 and AR-5
  change gate inputs; the batch reports tell that item's owner.

### 4.3 Phase A: start now (tools, tests, docs; no running batch's files)

#### AR-1. Audit manifests generated from the compiled environment (3–4 h)

- **Why.** `lean/VE/Audit.lean` is hand-appended (4,805 lines, 202 commits in 14 days) and `lean/audit.py:80-112`
  finds theorems with a regular expression over source text.
- **Change.** `lean/audit.py --write` regenerates `VE/Audit.lean` and `ResponseShape/Audit.lean` from
  `lean/declarations.txt`: exactly the constants it records with kind `theorem` and a source range, split by module
  prefix (`VE.` against `ResponseShape.`), sorted by name, with the `import` lines for exactly the modules that
  declare them, each file headed "generated by `lean/audit.py --write`; do not edit". The order is unchanged:
  `declarations.txt` comes from the compiled environment, the manifests from it, `statements.txt` from the
  manifests. `--check` regenerates in memory and fails on any difference, then runs `lake env lean` on both as today
  and compares the output with `axioms.txt`. The regex scan of theorem names is deleted; the forbidden-word scan
  stays.
- **Lean.** No new declaration. The `#print axioms` command and the allowed set (`propext`, `Classical.choice`,
  `Quot.sound`) are unchanged.
- **Fixtures.** A scratch module with a new theorem and no manifest line: `--write` adds it, `--check` passes after
  the write and fails before it. A theorem whose proof uses `sorry`: the audit fails. The Prop-class instances Lean
  compiles as theorems (three today, consolidate-b1 fix 4) are listed and audited; the batch lists them.
- **Deleted.** Hand edits of both manifests; the theorem regex in `audit.py`.
- **Gate.** 4.1 items 1 and 3; `tests/test_lean_audit_record.py`; the precommit tests; the new manifests list a
  superset of today's names, with the additions listed.
- **Outcome.** No hand edit of an audit manifest per theorem (202 edits in 14 days before); a conflict in either
  manifest resolves by regeneration. **Collision rule:** "conflict in an `Audit.lean`: take either side, run
  `python3 lean/audit.py --write`".

#### AR-2. A narrow freeze (3–4 h; needs D2)

- **Why.** `frozen-sources.sha256` lists all 391 modules, and 346 of 629 Lean-source commits re-hashed it. The same
  per-module hashes are in `lean/declarations.txt`, and decoder hashes again in the assurance manifest.
- **Change.** The frozen list keeps only the files D2 names. The recommendation: files holding K declarations
  (kernel definitions, trust map class K; 25 files in the current trust inventory) and the frozen-contract
  decoders (`ve.core@0.1` identities). `frozen.py` gains `--write`. The precommit hook's frozen-file rule applies
  to the short list only. Statement changes everywhere stay visible through `statements.txt` and the trust report
  (4.1 item 3).
- **Lean.** None.
- **Fixtures.** An edit to a K file without a re-hash fails the hook and `frozen.py`; an edit to a non-frozen
  module passes both; a new module is not required in the list; `Main.lean`'s rule is unchanged.
- **Deleted.** About 370 of 391 lines; the per-module re-hash step in every Lean batch.
- **Gate.** 4.1 item 1; `tests/test_precommit_hook.py`, `test_wire_contract_lint.py`, `test_wire_contract_s4_lean.py`.
- **Outcome.** Share of Lean-source commits that edit the frozen list: 55% today; *estimate* under 10%, measured
  over the two weeks after the merge. **Collision rule:** "conflict in `frozen-sources.sha256`: take `main`'s file,
  run `python3 VE/Route/frozen.py --write`".

#### AR-3. Test collection checked against the merge base (3–4 h)

- **Why.** `tools/gate-collection.json` (13,747 lines) was regenerated by 274 commits in 14 days; it exists to catch
  tests that silently drop out of collection (`FINDING-CLASSES` class 2).
- **Change.** The gate record (the git note `tools/batch_evidence.py` reads) starts storing the collected IDs.
  `tools/gate.py` takes the expected collection from the merge base's record, or collects the merge base in a
  scratch worktree when there is none. A base ID may be missing at the head only if
  `git diff --no-renames base..head` deletes its file or its test function (read with `ast`), or changes that
  function's parametrisation. Collection errors still fail (`gate_collection.py:49-51`).
  `tools/gate-optional.json` stays.
- **Lean.** None.
- **Fixtures.** A module that fails to import; a conftest change that skips a module at collection; a parametrise
  list that shrinks in an unchanged function: each fails. A deleted test function and a deleted test file: pass.
- **Deleted.** `tools/gate-collection.json`, the `--write` path of `gate_collection.py`.
- **Gate.** `tests/test_gate_collection.py`, `test_gate.py`, `test_gate_integrity.py`; one full gate.
- **Outcome.** −13,747 committed lines and no regeneration commits; the extra cost is at most one collection of the
  base, which the batch measures. **Collision rule:** "modify/delete conflict on `gate-collection.json`: take the
  deletion".

#### AR-4. The trust budget as a ratchet (3–4 h; needs D3)

- **Why.** 1.5: the budget follows the code; `trust_map.py --check` fails on `main`; the per-file tables
  (12,826-line file) conflict and one is stale.
- **Change.** The committed file keeps `budget` and a list of `allowances` (class, lines, reason, signature, commit).
  `trust_map.py --check` measures the head, reads the merge base's budget, adds the allowances introduced in
  `base..head`, and fails on any excess; the merge train writes `budget := measured` when the measurement is lower.
  Per-file tables go into the gate record, not the tree. `section11` and the duplicated history entry are dropped;
  the history moves to the allowances list.
- **Lean.** None.
- **Fixtures.** Ten new untied V lines without an allowance: fail; with one: pass; deleting trusted lines lowers
  the budget at the merge; two branches that each add an allowance merge without a conflict on totals.
- **Deleted.** About 12,600 lines of committed per-file classification.
- **Gate.** `tests/test_consolidation_tools.py` (1,478 lines; the trust-map parts updated); the check passes on
  `main` after the DRI signs today's budget or a lower one.
- **Outcome.** A budget that cannot rise without a signature; file 12,826 → *estimate* under 300 lines.

#### AR-5a. The evidence toolkit (5–6 h; needs D4)

- **Why.** 2.7: 70 copied scripts, 14 false-pass findings on gates and evidence, 27 permanent report-test files,
  two branch gates broken by them after a sync.
- **Change.** `tools/evidence/`: `latency` (paired base and head CPU samples, the 20% rule, fails on empty, missing
  or duplicated keys), `ab` (calls `tools/lean_first_diff.py`, fails on empty or unavailable-on-both), `fuzz_ab`,
  `mutants` (apply, run the named test, restore, record), `report` (numbers rendered from the evidence JSON);
  `docs/<track>/<batch>/evidence.toml` names the corpora, workloads and claims. `tools/batch_evidence.py --check
  <dir>` reads the toml and the evidence. Batches started after this merge use it and add no `tests/test_bNN_*.py`;
  the merge train runs the check for the batch it merges.
- **Lean.** None.
- **Fixtures.** The four historical false passes as known-answer tests: two documents with the same file name in
  different directories (b1 latency), a replay verdict swapped after hashing stops (b10a trace fuzzer), empty A/B
  files (lf-0), an unexplained new Lean answer after a known rejection (b10b fuzzer gate). Each must fail.
- **Deleted.** Nothing yet (AR-5b migrates).
- **Gate.** The toolkit's own tests; one finished batch (b16c) re-checked with the toolkit gives the same verdict as
  its saved report.
- **Outcome.** New batches add 0 lines of evidence code and 0 report tests.

#### AR-6. Identity and binding inventories with a ratchet lint (2–3 h)

- **Why.** P2, P3, P5: re-derivation in the relay grows with each route.
- **Change.** `tools/relay_lint.py` rule 4: in a relayed module, no call that builds a Lean-owned identity preimage
  (`digest` or `sha256` over a string literal starting `ve-meaning-`, `ve-environment-`, `ve-source-`,
  `ve-report-`, `ve-document@`, `ve-rights-`, `ve-soft-norms-`, `ve-norms-`, `ve-situation-`, `ve-model-`), and no
  `ve-` domain literal in any `ve/` module outside an allowlist. Today's 36 sites go into the allowlist, each with the
  batch that removes it (AR-15, lf-16g, RD-7) or "Python-owned record" (assist, adapters, proposals, argument
  package, checker build). The lint reads Python with Python's `ast`, as the existing rules do.
- **Lean.** None.
- **Fixtures.** A new `digest("ve-meaning-…")` in a relayed module fails; an allowlisted site passes; an allowlist
  entry whose site is gone fails (stale entry).
- **Deleted.** Nothing; the allowlist can only shrink.
- **Gate.** `tests/test_relay_lint.py`.
- **Outcome.** A ratchet at 36 sites.

#### AR-7. One architecture map, a stale-document sweep, the binding ADR (2–3 h; docs only)

- **Change.** `docs/ARCHITECTURE.md`: section 1 of this review, kept current with the commands of section 7; the
  corrections of table 1.6 applied (each stale passage replaced or marked superseded with a link);
  `docs/adr/0001-response-binding.md` with the binding definition of T1(a) for the DRI to sign (D1);
  `docs/ARCHITECTURE-LAYERS.md` points to the new map for anything but the checker commands.
- **Lean.** None. **Fixtures.** `tests/test_testing_profile_doc.py` and the other doc tests pass.
- **Outcome.** One current map; 11 stale statements corrected (table 1.6).

#### AR-8. Rust boundary checked by cargo (2–3 h)

- **Why.** Since the crate split each crate holds one group; `tools/check_rust_deps.py` still tokenizes Rust to
  check module groups (`FINDING-CLASSES` class 7).
- **Change.** The checker reads `cargo metadata --format-version 1 --no-deps`: `ve-kernel` depends on no workspace
  crate, `ve-profile` only on `ve-kernel`, `ve-core` has no modules of its own beyond its re-exports, the `ve`
  binary may depend on all. The module-group tokenizer and the empty `tools/rust-module-exceptions.json` are
  deleted.
- **Lean.** None.
- **Fixtures.** `ve-kernel/Cargo.toml` gains a dependency on `ve-profile`: fail; a new module in `ve-core/src`:
  fail.
- **Deleted.** *Estimate* 500 of 648 lines.
- **Gate.** `cargo test --workspace --locked`; `tools/test_layer_policy.py`.

#### AR-9. Split the assist modules (3–4 h)

- **Change.** `ve/assist/recovery.py` (1,359) into journal, replay and commands modules; `ve/assist/session.py`
  (1,338) into session state, proposals and views. Code moves, nothing else; public names re-exported.
- **Lean.** None.
- **Fixtures.** `tests/test_assist*.py` (5 files) unchanged and passing.
- **Gate.** 4.1 item 1 (assist has no corpus in the A/B; its tests are the gate).
- **Outcome.** No assist file over 700 lines (*estimate*); function-level imports in `assist/` counted before and
  after.

### 4.4 Phase B: after lf-18 merges (readings parts after RD-7)

#### AR-10. Route registry in Lean; Python reads modes and deadlines from the handshake (4–6 h)

- **Lean.** New `lean/VE/Service/Registry.lean`:

```lean
namespace VE.Service

/-- One public mode of the service and its deadline: CPU milliseconds per case and per MiB of
cases. The values are today's `ve/backends/lean_service.py` `DEADLINES`. -/
structure RouteSpec where
  mode : Mode
  baseMs : Nat
  perMiBMs : Nat
  deriving Repr

def registry : List RouteSpec := [
  ⟨.evaluate, 5000, 30000⟩, ⟨.checkCertificate, 5000, 30000⟩, -- … one entry per `Mode`, in `modes` order
  ⟨.rights, 120000, 1000000⟩, ⟨.document, 120000, 120000⟩ ]

theorem modes_complete (m : Mode) : m ∈ modes := by cases m <;> decide
theorem registry_modes : registry.map (·.mode) = modes := by decide
theorem registry_names_nodup : (registry.map (·.mode.name)).Nodup := by decide
```

  The handshake gains `"deadlines": {mode: [baseMs, perMiBMs]}` from `registry`, with its shape in
  `ResponseShape/Schemas/Envelope.lean`. If `decide` is slow in the kernel, `#guard` on the Boolean forms is the
  fallback the project already uses.
- **Python.** `service_schema.MODES`, `lean_service.DEADLINES` and the mode lists in `tests/lean_routes.py` and
  `tests/test_lean_service.py` come from the handshake (lf-18 already moves the I/O caps there).
- **Fixtures.** A handshake golden; a new `Mode` constructor without a registry entry fails to compile.
- **Deleted.** P6's modes and deadlines; mode-name lists in tests.
- **Outcome.** Adding a mode edits Lean only (runner, shape, one registry line); the number of files spelling a mode
  name, measured with `"risk-eval"` (12 today).

#### AR-11a and AR-11b. Binding by construction in the response shapes (5–6 h each; needs D1)

- **Lean.** In `lean/ResponseShape.lean`, two new `Shape` constructors and a census:

```lean
  /-- Display text: the client never compares it with the request (rendered `x-text: why`). -/
  | text (why : String) (s : Shape)
  /-- An integer at most the request's integer at `pointer` (rendered `x-at-most`). -/
  | atMost (pointer : String)

/-- The paths, under `path`, of leaves typed only `string` or `integer` that no binding
keyword (`echo`, `equals`, `references`, `count`, `length`, `index`, `digest`, `atMost`),
closed domain (`const`, `enum`, `pattern`, `lean`, `tagged`) or mark (`text`, `copied`)
covers. A `node` is covered when any of its keywords is. Structural recursion over `Shape`. -/
def Shape.unbound (path : String) : Shape → List String

/-- Every schema of a file: its top-level schemas and its `$defs`, groups included. -/
def File.shapes (f : File) : List (String × Shape) :=
  f.top ++ f.defs.flatMap fun
    | (k, .schema s) => [(s!"$defs/{k}", s)]
    | (k, .group _ es) => es.map fun (e, s) => (s!"$defs/{k}/{e}", s)

def Schemas.unboundCensus : List String :=
  Schemas.files.flatMap fun f => f.shapes.flatMap fun (k, s) => s.unbound s!"{f.name}#/{k}"

/-- The ratchet: no unbound leaf beyond the list; AR-11b ends with the list empty. -/
#guard Schemas.unboundCensus.all (· ∈ Schemas.pendingUnbound)
```

  AR-11a: the constructors, both interpreters (`ResponseShape.check` and `ve/backends/service_schema.py`), the
  census with `pendingUnbound` set to today's list, and the core and envelope modes classified. AR-11b: the
  statement-layer modes and `document`; `pendingUnbound = []`. The skeleton of `text why s` is that of `s` and the
  skeleton of `atMost p` is an integer, so the encoder proofs (`runMode_fits`) need no new reasoning; the batch
  re-checks them.
- **Python.** `x-text` checks nothing; `x-at-most` compares integers (type-strict, so `true` is not 1).
  `tests/test_lean_service_schema.py` requires the two interpreters to agree on every mutation, as today.
- **Fixtures.** The genuine-answer corpus (`tests/data/route-cases.jsonl`) and the existing drop, empty and retype
  mutations, plus one new mutation: every string leaf replaced by a value absent from the request must fail unless
  the leaf is `text`. The open findings as regression cases: assumption names not in the graph (lf-13b B1),
  `steps` over `max_steps` (lf-13b B2), a changed span (lf-16b), an invented coverage unit (lf-5), a forged unit
  status (lf-11b).
- **Deleted.** Binding code the shapes now cover: the ID and span checks of `document.py:458-507`, the `_need` binders
  in `readings_route.py` that the shape covers, `speech_source.py`'s field table. `document.py:508-540` (coverage
  recomputation) moves to `ResponseDecode.invariants` (bytes by kind sum to the source bytes; the residual total
  is the sum of the residual lines), tested on the document corpus; the Python copy is deleted.
- **Outcome.** Unbound leaves: today's census → 0; class "Lean answer unbound" findings in later reviews, counted
  as in 2.10.

#### AR-12a. Typed rows and a type checker at the boundary (4–5 h)

- **Change.** `tools/response_schemas.py --write` also writes `ve/backends/rows.py`: one `TypedDict` per mode's row,
  from the shapes. `pyright` (or `mypy`) runs on `ve/backends/` and the route modules in the gate; display code
  reads typed rows.
- **Lean.** None.
- **Fixtures.** The lf-10b regressions: a helper reading `.witness` from a row dict fails the type check.
- **Outcome.** Type errors at the boundary: count before (the batch measures) and after (0 in checked modules).

#### AR-12b. One null policy and one admission call (3–4 h)

- **Lean.** `RouteSpec` gains `nulls : NullPolicy` with `inductive NullPolicy | omit | omitWithPaths`, set per mode
  to today's behaviour (`reports` is `omitWithPaths`); the handshake carries it.
- **Python.** The relay applies the declared policy. `rights_route._wire`, `reports_route._without_null` and
  `_split_nulls`, `soft_relay.wire` and `readings_s1.wire` are deleted; the five copies of the `id`/`status` strip
  become `relay.admission(mode, environment, document)`.
- **Fixtures.** Every corpus case with a null at every depth gives the same request bytes before and after.
- **Outcome.** Null policies 4 → 1 declared table; −5 copies.

#### AR-12c. Every production Lean call through the service (5–6 h)

- **Lean.** Modes for the speech-source runner, the senses reader, metered evaluation and search, `graph.compose`
  and `bundle.check`, each with its `runMode_<name> … := rfl` theorem and `runMode_fits` extended to the new cases;
  `ve_speech_acts_route` and `ve_senses_route` leave `defaultTargets`.
- **Python.** `backends/lean.py`'s one-shot runners (`run`, `run_route_cases`, `conforms`, `row_problem`) are
  deleted with their last callers; `speech_source.py` and `senses.py` keep only case building and display.
- **Fixtures.** Byte parity between the one-shot runner and the service mode on each route's corpus (as lean-first
  batch 1 did); the senses and speech corpora.
- **Outcome.** Transports 3 → 2 (service and Rust); one-shot executables in production 4 → 0; latency per call
  measured (lean-first 3.2: about 0.1 s CPU per one-shot process before any work).

#### AR-13a to AR-13e. Typed diagnostic codes (13a: 4–6 h; 13b–13e: 2–4 h each; needs D6)

- **Lean (13a).** New `lean/VE/Diag.lean`:

```lean
namespace VE.Diag

inductive Code where
  | invalidInput | syntaxError | unknownSymbol | duplicateDeclaration | unboundVariable
  | shadowedVariable | typeMismatch | invalidModel | unsupportedProfile | resourceLimit
  | admissionError | checkerUnavailable
  deriving DecidableEq, Repr, Inhabited

def Code.name : Code → String
  | .invalidInput => "InvalidInput" | .syntaxError => "SyntaxError"
  | .unknownSymbol => "UnknownSymbol" | .duplicateDeclaration => "DuplicateDeclaration"
  | .unboundVariable => "UnboundVariable" | .shadowedVariable => "ShadowedVariable"
  | .typeMismatch => "TypeMismatch" | .invalidModel => "InvalidModel"
  | .unsupportedProfile => "UnsupportedProfile" | .resourceLimit => "ResourceLimit"
  | .admissionError => "AdmissionError" | .checkerUnavailable => "CheckerUnavailable"

def Code.all : List Code := [.invalidInput, .syntaxError, .unknownSymbol, .duplicateDeclaration,
  .unboundVariable, .shadowedVariable, .typeMismatch, .invalidModel, .unsupportedProfile,
  .resourceLimit, .admissionError, .checkerUnavailable]

def Code.ofName? (s : String) : Option Code := Code.all.find? (·.name == s)

/-- A rejection: its public code, its English text, and the JSON path when Lean can name it. -/
structure Diag where
  code : Code
  text : String
  path : Option String := none

/-- The wire text of a rejection, byte-identical to today's `"<Code>: <text>"` messages. -/
def Diag.message (d : Diag) : String := d.code.name ++ ": " ++ d.text

def fail {α : Type} (c : Code) (text : String) : Except String α := .error (Diag.message ⟨c, text, none⟩)

theorem Code.ofName?_name (c : Code) : Code.ofName? c.name = some c := by cases c <;> decide
theorem Code.all_complete (c : Code) : c ∈ Code.all := by cases c <;> simp [Code.all]
theorem Code.names_nodup : (Code.all.map Code.name).Nodup := by decide
```

  `VE.Service.rejectionCodes` is redefined as `Code.all.map Code.name` (one owner; the handshake's list is
  unchanged, so `theorem rejectionCodes_eq : VE.Service.rejectionCodes = Code.all.map Code.name := rfl`).
- **Lean (13b–13e).** One profile group per batch (core routes; norms and norm defaults; soft norms and rights;
  the rest): each `throw s!"InvalidInput: …"` becomes `fail .invalidInput s!"…"`; the soft route's prefix table
  (`SoftNorms/Run.lean:411-447`) is replaced by codes attached where `Phases.fail` already names them.
- **Fixtures.** The A/B over all corpora: messages and codes byte-identical. A grep count of code-prefixed literals
  (about 1,300 today) is the progress metric, not a gate.
- **Deleted.** Prefix parsing for migrated producers; the soft prefix table; nothing user-visible changes.
- **Outcome.** Code-prefixed literals → 0 in migrated modules; codes no longer derived from texts.

#### AR-14. Python layer map after lean-first, checked by `import-linter` (3–5 h; needs D5)

- **Change.** `tools/layer_policy.py`'s Python table becomes T5's five layers; `import-linter` contracts replace
  `check_python_layers.py` and the custom resolver (`layer_policy.py:43-87`); the 30 adapter exceptions are
  deleted; indented imports that no longer hide a cycle move to module level; `ve/__init__.py` resolves names
  lazily (`__getattr__`), so `import ve` no longer loads the English parser.
- **Lean.** None.
- **Fixtures.** A seeded outward import fails; `tools/test_layer_policy.py` updated.
- **Outcome.** Python layer exceptions 42 → *estimate* at most 6; indented relative imports 646 → measured.

#### AR-15. Identities read from Lean (4–6 h; needs D7; after lf-16g, lf-18, RD-7)

- **Change.** Each allowlisted Lean-owned site of AR-6 is replaced: Python reads `environment_id`, `meaning_id`,
  `source_id`, `document_id`, `report_id` and the document hashes from Lean's answers, and binds a stored identity
  by equality with Lean's value. Where a route does not yet return an identity Python needs, the batch adds it to
  the row and its shape as a bound field (`echo` of the stored value, or a digest of request text).
- **Lean.** Only the added row fields and their shapes; `runMode_fits` re-proved for the touched modes.
- **Fixtures.** Corpus A/B identities identical; a forged identity in a row fails binding.
- **Outcome.** Python identity sites 36 → the Python-owned records only (9 today, unless D7 moves some).

#### AR-16a, AR-16b, AR-16c. Module splits (3–5 h each)

- **16a** (after lf-16g): `ve/document.py` → `ve/document/` with file reading and front matter, the Lean relay and
  binding, rendering and the report display.
- **16b** (after RD-7): `ve/readings_verdicts.py` along its classes (`Superposed`, `Enumerated`, the choice document)
  and the binding helpers that AR-11 has not removed.
- **16c** (after lf-18): `lean/VE/Service/Standalone.lean` into legacy envelopes, model and environment decoders and
  typing; one owner for environment diagnostic texts (L4); `Legacy.family` and the error-path recomputation removed
  (L5). Lean statements: every moved declaration keeps its name; `statements.txt` byte-identical for kept theorems.
- **Outcome.** No Python module over 1,000 lines in these areas (*estimate*); trusted lines unchanged or lower.

#### AR-17. Readings S2 regeneration removed (4–6 h; after RD-7 and lf-14d, if RD-7 has not done it)

- **Change.** `readings_route.elaborate` relays Lean's S2 row like S1; the comparisons at `readings_route.py:74-145`
  and the `readings_sup.py` functions used only by them are deleted; generators keep what they use.
- **Lean.** None; Lean already returns every compared field.
- **Fixtures.** The readings corpora, the UDHR and constitution pilots, the 1,000-document rights corpus; each
  disagreement that today yields `ReadingsConformance` is listed as an `availability` change for signature.
- **Outcome.** P4 closed; lines deleted measured.

#### AR-5b. Evidence migration (3–4 h; needs D4)

- **Change.** The 27 report-test files move to `docs/<track>/<batch>/evidence.toml` checks; evidence files over 1 MB
  move to the evidence branch with a manifest; the copied scripts are deleted where the toolkit reproduces their
  result.
- **Fixtures.** Each migrated batch's check gives the same verdict as its report test did.
- **Outcome.** −27 test files (about 2,800 lines); checkout −*estimate* 120 MB.

### 4.5 Phase C: Lean consolidation (after lf-14a–d and lf-18)

The converged consolidation plan (`docs/CONSOLIDATION-PLAN.md`, steps 2b–9) is the design; its Lean statements stand.
This phase cuts it into 2–6 h batches, re-estimated with `tools/trust_map.py --ledger` on the tree of that day. The
first six:

| Batch | Consolidation step | Change | Lean statements | Deleted |
|---|---|---|---|---|
| AR-20 (3–4 h) | 4a + L6 + Paths | `bind_ok` to `VE/Kit/Except.lean` with the old name as an alias; delete `SoftNorms.Admission.decodeSoftDoc` and `NormDefaults.Admission.decodeFilledDoc` (copies of `Route.Admission.decodeDoc`); `CertificateWire.lean:140` calls `canonical`; `Core/Paths.lean` and `Closure/Paths.lean` (today equal but for their namespace lines) re-export one `VE/Paths.lean` | every old name stays, as an abbreviation or a corollary with the identical statement (for example `VE.Core.reachEval_iff`); `statements.txt` byte-identical for kept names | about 67 D lines; one of the two 195-line Paths files |
| AR-21 (5–6 h) | 3a | theorem only: closure's `replay E a b` equals Core's on the embedding, both flags explicit | as in consolidation 3a | none |
| AR-22 (5–6 h) | 3b | closure runs through Core's `replay` behind an atom-free gate, keeping its `@0`/`@1` version gate | 3a's theorem | `VE/TableauExtended*` (6 files, 1,075 lines) and four closure files (473 lines) |
| AR-23 (5–6 h) | 3c | `Closure.Formula.denote` through Core; `Closure/{Paths,Finite}` aliases | `embedClosure_denote` by `rfl`; `conservativity` and `closure_route_acceptance` unchanged | about 50 K lines |
| AR-24 (5–6 h) | 7 | the statement-layer route skeleton below, with the registry of AR-10 | below | the statement-layer `runCase` and `runCaseReported` copies whose equality theorem holds; the copied acceptance proofs |
| AR-25 onward | 4b–4d, 8a, 8b, 9 | admission kit, conflict kit, choices, formula codec, decoder combinators, normative core | as in the consolidation plan | per its table |

AR-24's statements (draft for the batch's statement review):

```lean
namespace VE.Service

/-- A statement-layer route: which cases it answers, its case kinds, and the routes that
answer (and report) every case it does not. -/
structure KindRoute where
  name : String
  /-- Whether the route answers a case of this kind: today's `uses<X>Path` test, plus the
  kinds a route answers whatever the environment (as `Norms.Run.runCase:143-154` does). -/
  claims : String → Json → Bool
  kinds : List (String × (String → Json → Except String Json))
  delegate : Json → Except String Json
  /-- Whether the route reports a case's error itself (today's `runCaseReported` test). -/
  reports : Json → Bool
  delegateReported : Json → Json
  extra : Json → String → List (String × Json) := fun _ _ => []

def KindRoute.runCase (r : KindRoute) (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let kind ← VE.Route.Run.caseKind j
  if !r.claims kind j then return ← r.delegate j
  match List.lookup kind r.kinds with
  | some run => run id j
  | none => throw s!"UnsupportedProfile: case kind {kind} is not available on the {r.name} route"

def KindRoute.runCaseReported (r : KindRoute) (j : Json) : Json :=
  if r.reports j then
    match r.runCase j with
    | .ok result => result
    | .error m => Json.mkObj ([("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str m)] ++
        r.extra j m)
  else r.delegateReported j

theorem KindRoute.runCase_claimed (r : KindRoute) (j answer : Json) (id kind : String)
    (run : String → Json → Except String Json)
    (hid : VE.Bridge.stringField j "id" = .ok id) (hk : VE.Route.Run.caseKind j = .ok kind)
    (hc : r.claims kind j = true) (hl : List.lookup kind r.kinds = some run)
    (h : r.runCase j = .ok answer) : run id j = .ok answer
```

Per route, before its own definitions are deleted (tie, then delete): `theorem rights_runCase_eq (j : Json) :
VE.Rights.Run.runCase j = rightsRoute.runCase j` and the same for `runCaseReported`, then `rights_wire_acceptance`
restated from `runCase_claimed` and `runAdmission_sound` with an unchanged statement. The soft route's `extra` is
today's `code` and `dual_guard_cycle` members (`SoftNorms/Run.lean:476-483`). The equality theorem decides: a route
whose order of checks the table cannot reproduce (the norms route admits only on its own path but answers
`norms-elaborate` everywhere, `Norms/Run.lean:139-171`) keeps its own `runCase` until a signed change aligns it.

### 4.6 Order, totals and expected outcomes

```
now:            AR-7 first (the map and the binding ADR), then AR-1 to AR-6, AR-8, AR-9 in any order
after lf-18:    AR-10 ─ AR-11a ─ AR-11b ─ AR-12a ─ AR-12b ─ AR-12c       AR-13a ─ AR-13b..e
                AR-14   AR-16c   AR-5b
after lf-16g:   AR-16a          after RD-7: AR-15, AR-16b, AR-17
after lf-14:    AR-20 ─ AR-21 ─ AR-22 ─ AR-23    AR-24 (needs AR-10) ─ AR-25…
```

| Phase | Batches | Builder hours (*estimate*) | Measured outcome to report |
|---|---:|---:|---|
| A (now) | 9 | 26–35 | −13,747 (test IDs), −~12,600 (trust tables), −~370 (frozen list) committed inventory lines; edits per Lean commit of the frozen list and audit manifests; 0 new evidence scripts and report tests; −~500 lines of Rust tokenizer |
| B (after lf-18) | 18 | 61–91 | unbound leaves → 0; checking styles 6 → 1; one-shot executables in production 4 → 0; null policies 4 → 1; code-prefixed literals → 0 in migrated modules; Python identity sites 36 → 9; layer exceptions 42 → at most 6; −27 report-test files; −~120 MB per checkout |
| C (after lf-14, lf-18) | 6, then the consolidation plan | 28–34 for the first six | trusted lines (K, S, untied V) lower at every batch; −1,548 untrusted lines (3b); one definition of the logic fewer (3c) |

The expected fall in review findings is an estimate: classes "unbound answer" and "gate passes when it should not"
were at least 37 of the B findings in 2.10; after Phase B the same classification, run on the next 20 review files,
measures the effect.

## 5. Decisions for the DRI

1. **D1. Binding contract.** Adopt T1(a): binding is a closed list of relations to the request; derived values are
   Lean's, proved or checked by `ResponseDecode` invariants, never recomputed in Python. Recommended: yes. It
   settles the disagreement between `docs/spec/lean-service.md:41-60` and the build checklists, and review prompts
   can cite it.
2. **D2. What stays hash-frozen.** Recommended: files with K declarations and the frozen-contract decoders; statement
   changes guarded by `statements.txt` and the trust report.
3. **D3. Trust ratchet.** The budget falls automatically and rises only by a signed allowance in the same merge; the
   DRI signs today's 35,892 V (or a lower measured value) as the starting point.
4. **D4. Report tests and evidence.** Batch evidence is checked at the batch's gate and by the merge train, not by
   permanent tests; evidence files over 1 MB live on an evidence branch with an in-tree manifest.
5. **D5. Python layer map.** T5's five layers, with `import-linter` as the checker.
6. **D6. Typed codes.** The `Code` enumeration and `Diag` of AR-13, with wire texts unchanged.
7. **D7. Identity owners.** Lean owns the meaning, environment, source, document, report and document-hash domains;
   Python owns only its app records (assist, adapters, proposals, argument packages, checker build).
8. **D8. lf-18's scope.** lf-18 moves I/O caps into the handshake; AR-10 adds modes and deadlines. Either lf-18
   takes AR-10's Python half, or AR-10 follows it. Recommended: AR-10 follows, so lf-18 keeps its size.

## 6. What this plan does not change

- The VE language, the one-reading rule, the English grammar and every text people read or write. Diagnostics stay
  English sentences produced by Lean; codes are machine fields and are not shown by default.
- Lean-first's design, its gate and the rule-3 decision A.
- The running batches' scopes; this plan only orders new work around them.

## 7. Re-measuring

Every number above was taken with single commands on `c24aeab2`; re-run them before each batch:

| Number | Command |
|---|---|
| Lines per Python, Lean, Rust file | `wc -l ve/*.py ve/*/*.py`; `wc -l lean/VE/*.lean lean/VE/*/*.lean lean/VE/*/*/*.lean lean/*.lean lean/ResponseShape/*.lean lean/ResponseShape/*/*.lean`; `wc -l rust/ve-kernel/src/*.rs rust/ve-profile/src/*.rs` |
| Python change since the lean-first base | `git diff --shortstat f4142cb9 HEAD -- 've/*.py' 've/**/*.py'` |
| Commits editing an inventory | `git rev-list --count --no-merges --since=2026-09-26 HEAD -- <file>` |
| Merges into `main` | `git rev-list --count --merges --first-parent --since=2026-09-26 HEAD` |
| Near-copies in Lean | `git diff --no-index --shortstat lean/VE/Closure/<F>.lean lean/VE/Core/<F>.lean` |
| Trust classes and budget | `docs/trust-baseline.json` `totals`, `budget`, `history`; `python3 tools/trust_map.py --since <base>` |
| Identity sites, null helpers, mode spellings, code-prefixed literals | text search for `"ve-` domain strings passed to `digest`, `soft_digest` or `sha256`, for `if item is not None}`, for `"risk-eval"`, and for `"(InvalidInput\|SyntaxError\|…)[:(]` under `ve/` and `lean/VE` |
| Layer exceptions | `tools/layer-exceptions.json`, `tools/lean-layer-exceptions.json` |
| Review-finding classes | B-marked lines in `manage-agents/{lf,rd,e2}-*{review,looprecheck}*.final.md`, classed by hand |
