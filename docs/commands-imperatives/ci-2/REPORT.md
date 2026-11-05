# ci-2 REPORT: the `english.command` mode and `readInstruction` (CI-2, cut after deliverable (3))

**Status:** deliverables (1) to (3) built and committed on `feature/ci-2`; (4) to (6) are ci-2b (the size line). HEAD: the commit that adds this file.
**What changed:** `VE.Commands.Run` (the proof task with O2 and O10, `readInstruction`, the request and answer), the service mode `english.command` with its shape, encoder theorem and `runMode_fits` branch, 43 `#guard`s (42 in `RunExamples.lean`, 1 in `RunSplit.lean`); no Python caller yet.
**Open:** none blocking. The cut of (4) to (6) to ci-2b and the facts-based statements are SIGNED (reviews/dri-decisions-20261104-ci-2.md items 1 and 2); size is about 960 hand-written lines (the excess over about 600 is R16's mutant-killing guards, the route's fixtures, side tables and evidence).
**Signatures:** none reserved; the one DELTA row cites R16.

FOLLOW-UP: ci-2b the relay, the wrapper and the deletions of CI-2: read_command, speech_document's command fences through readInstruction (commandFence_needs_context), command.read, the inventory rows (D9), the deletion ledger and the A/B
FOLLOW-UP: ci-2-ties a ties pass for VE/Commands/Run.lean under R16 (FOLLOW-UPS.md "## ci-2")

Plan and spec: `docs/spec/commands-imperatives-PLAN.md` and `docs/spec/commands-imperatives.md`, copied verbatim from
9a12df17a (commit c1a17b46b); section 17 records the DRI's rulings of O1, O2, O7 and O10 (d2e265bf4, as
reviews/dri-decisions-20261102-ci-0.md asks). Statement gate: passed (reviews/dri-decisions-20261102-ci-0.md item 1).

## Deliverables

| Plan row | Delivered | Evidence |
|---|---|---|
| (1) `lean/VE/Commands/Run.lean`: `QueryRecord`, `Context`, `proofTask`, `proofMany` (O2), `readInstruction`, `Request`, `Run.decodeRequest`, `Run.encode`, `Run.caseReported` | yes (a46ff03de) | `cd lean && lake build`: 1279 jobs, success (final tree) |
| (1) statements `readInstruction_command`, `proofTask_bound`, `proofTask_addressed`, `caseReported_eq` | yes, as stated in spec section 6 | `python3 lean/audit.py`: PASS, 761 source files, 8399 theorems, the allowed axioms only; `lean/axioms.txt` lists each |
| (1) `readInstruction_refused_classed`, `readInstruction_typed` | as `_refused_classed_of` and `_typed_of_facts` (deviations 2 and 3; SIGNED, reviews/dri-decisions-20261104-ci-2.md item 1, its conditions in `lean/VE/Commands/RunSplit.lean`); the spec's statements are ci-2b's, after ci-1b | the same audit |
| (1) `Texts.lean`: the act wording `{0} submit a proof of {1}` (`proofAct`), no legend; `("QueryMismatch", "VEError")` in `codeClasses` | yes | `RunExamples.lean`: P4′ guard, the class guard |
| (2) `Protocol.lean` entry, `runMode_englishCommand ... := rfl`, `Schemas/Command.lean`, `Encoders/Command.lean` (`caseReported_fits`), the `runMode_fits` branch | yes (b13d280d0) | `lake build`; `uv run python tools/repo_map.py --check`: "PASS: 42 modes, each with its schema file" |
| (3) the plan's fixtures through the mode: P1′, P2, P3, P3′, P3″, P4, P4′, P5-like, P6, P7, P8, the two-request echo, O7, O10, the `jsonWF?` refusal, the `caseReported_eq` comparison | yes, as `#guard`s in `lean/VE/Commands/RunExamples.lean` | `lake build VE.Commands.RunExamples`: success |
| (4) `Source/Run.lean`: command fences read by `readInstruction`, `commandFence_needs_context` | no: ci-2b | the task's size clause ("the relay, the wrapper and the deletions must land together") |
| (5) Python `read_command`, `speech_document.py`, manifest `command.read`, `relay_lint.py`, the inventory rows | no: ci-2b | as above |
| (6) the deletions (`_command_candidates`, the command branch of `parse_speech`, `legend`'s scope sentences, `PROOF_TASK_ACT`) | no: ci-2b, in the same change as (5) | as above |

Route plumbing the mode needed: its CPU deadline (`ve/backends/lean_service.py`), layer (`tools/layer_policy.py`),
the manifest pin of `Run.lean` and the `other_json` reason of `RunExamples.lean`, the schema seed of
`tests/test_lean_service.py`, the corpus cases `command_cases()` (`tests/lean_service_corpus.py`) with the relay gate's
rows (`tests/data/relay-gate-cases.jsonl`, the rows `relay_mutation_gate.record` keeps for this route) and the census's
genuine answers (`tests/data/binding-answers.jsonl.gz`, the six `english.command` rows only).

## Deviations from the spec at 9a12df17a

1. **The request** is `{id, environment, lexicon, unit, wording, queries, overlay?, generated?}`: one environment,
   decoded by the speech decoder and by `english.read`'s `decodeCase`, so the lexicon names the same environment the
   reader reads. It has no `cap`, `source` or `mode`: the reader reads its condition at `maxCandidates` and
   `workBudget` (O7), so such a field would be unbound. `queries` are the document's query records, decoded by the
   pinned `Wire.decodeQuery`; a duplicate id is `InvalidInput: duplicate query`, and an id that is not a declared
   constant of sort `query` is `InvalidInput: query`, so every decoded request satisfies `readInstruction_typed`'s
   `hq` (by reading `decodeRequest`, not proved; spec section 6 asked CI-2 to check it). `Context.sc` is the environment's scope (`se.scope`); a document's
   bindings reach it through the source wrapper (ci-2b).
2. **`readInstruction_typed_of_facts`** replaces `hd` by ci-1's `declared` facts (`hf : declared ctx.se = true`), as
   the task says while ci-1b (`readCommand_typed`, the decoder half) is not on main; it keeps `hE`, `hS`, `hR`, `hk`
   and `hq`. The spec's statement, with `hd` and `hw`, closes through ci-1b's `readCommand_typed` in ci-2b.
3. **`readInstruction_refused_classed_of`** takes ci-1b's two statements as hypotheses: `hc` (the reader's
   refusals are classed, ci-1b's `refused_classed`) and `hg` (english-lean's refusal of a sentence is classed, ci-1b's
   `guardOf_classed`). Its proof covers every proof-task refusal. The spec's statement is not claimed. SIGNED as ci-1
   item 2's split (reviews/dri-decisions-20261104-ci-2.md item 1). Its conditions: (i)
   `VE.Commands.RunSplit.readInstruction_refused_classed_of_ci1b` takes ci-1b's two statements as written (spec
   section 3's `refused_classed`; `guardOf_classed` at df2dee88b, which the spec does not state) and concludes the
   spec's statement, and `typed_facts_are_ci1s` passes `hf` to ci-1's `readCommand_typed_of_facts` unchanged; (ii) a
   `#guard` in `RunSplit.lean` that ci-1's `declared` holds of `E_web`'s and this item's fixture environments (and
   ci-1's own at `Examples.lean:240`); (iii) the table above lists neither spec theorem as delivered.
4. **O1:** `proofTask` refuses with `Texts.queryMismatch` = `("QueryMismatch", "")`, and `Run.outcomeFields` writes
   `q.unit` as the text of every `QueryMismatch` (the only code no other path writes).
5. **The relay's `jsonWF?`** runs on the whole request, before any decoder: `InvalidInput: the request is not a
   well-formed JSON tree`.
6. **An overlay or lexicon `english.read` refuses** is the error row `InvalidOverlay: …` or `InvalidGrammar: …`
   (`english.read`'s code and text with the mode named `english.command`), from `c.overlayFailure` and
   `grammarFault c.E {} c.L`, before any wording is read.
7. **The answer** (`english.command.json`): `id`, `status`, and `result` with `unit`, `wording`, `legend` (at least
   one line) and `outcome`; `one` adds `reading`, `many` `readings`, `refused` `code`, `class` and `text`, `limit`
   `text`. A reading is `{command: {force, act, args, guard}, fills: [{constant, words, span}], query, paraphrase}`,
   at most one fill (a decoded environment's predicates have at most two argument sorts). The shape binds `id`,
   `unit` and `wording` to the request (`equals`). The relay gate's eight remaining accepted mutants (act, constants,
   words, span and query against the request, args and fills emptied, the legend repeated) are allow-listed as
   follow-ups F4 and F10 naming ci-2b's `read_command` (`tools/relay-gate-allow.json`).
8. **P4′** puts the second proof predicate on `service` (`submitx_required(service, query)`, as the spec's row
   says): the speech decoder refuses two obligations with one act on the same sorts (`DuplicateActRole`).

Spec re-read: `proofTask`'s order (byte bound, `guardOf` cases, record, predicate, `checkedAddressee`) against spec
section 6 (`docs/spec/commands-imperatives.md:610-632`) and the ruled O10; `proofMany` against O2's ruling (item 3); `QueryMismatch`'s text against
O1's (item 2); `Context.b` against O7's (item 4); `Request` and `encode` against section 6's `Request` and `Run.encode`
docstrings (`docs/spec/commands-imperatives.md:648-666`) and the plan's (`docs/spec/commands-imperatives-PLAN.md:518-536`); the relay's `jsonWF?` against reviews/dri-decisions-20261102-ci-1.md item 1;
the BOUND and LEAN classes against spec section 6 "Relay binding" (the shape's descriptions name them).

## Fixtures (`lean/VE/Commands/RunExamples.lean`, all through `Run.caseReported` unless noted)

P1′ `one` on `submit_required`, fill (`q1`, "q1"), span null, query `q1`, paraphrase "In this task, you are required
to submit a proof of q1." (:71); P2 no record and P3 a wrong target: `QueryMismatch` with the unit as text (:72, :73);
P3′ two matching records: `QueryMismatch` (:74); P3″ `one` on `q2` (:75); P4′ two proof predicates:
`MissingObligationRole: {0} submit a proof of {1}` (:76); an unread sentence to prove: `NoDerivation: The sentence to
prove has no reading …` (:80); P6 "Click Check." `one` with span [6, 11] (:82); P7 `UnboundSlot: you` (:87, and for a command :88);
"Submit a proof of q1." is a command, span [18, 20] (:89); P4 over `E_web` and P8 at budget 0 (`limit`), on contexts
(:100, :103). O7 `ctx.b = workBudget` (:107); O10 400 bytes `one`, 401 `limit` (:110, :111). O2 over `goProof` (ci-1's
`goCase` with a proof predicate): two matching readings `many` with two entries, one of two `QueryMismatch`, a reading
two records match dropped so `QueryMismatch` (:125, :127, :128); `proofMany` on 2, 64 and 65 targets: `many`, `many`,
`limit` (:134). The echo: ids `r1`/`r2`, units `u1`/`u2`, legends for `alice`/`bob` (:142 to :147); the prohibition's
span [15, 24] after leading spaces (:148); W10's `many` over `E_web` (:150); `jsonWF?`'s refusal of F-raw (:154);
another environment's lexicon refused (:156); a duplicate record and an undeclared query id (:157, :159). R16's
guards (:163 to :177). `caseReported_eq` as a guard over six requests (:181).

Limits (the common rule): `readInstruction` sends the wording to the proof task or to `readCommand`, never both
(`Option.getD` is `@[macro_inline]`, `Init/Prelude.lean:2868`, so `readCommand` runs only when `proofTask` is `none`).
`guardOf` now formats refusals from its existing `TranslateOutcome` through `translationOf`, so both paths translate
each sentence once. The proof wording's
400-byte bound comes before it is read (O10, both sides of the boundary); `many` is at most `readingsBound`
(`manyOf`, both sides); budget 0 is `limit`.

## Seeded bugs (`docs/commands-imperatives/ci-2/mutants.json`)

| Id | File | Bug | Fails |
|---|---|---|---|
| S1 | lean/VE/Commands/Run.lean | `encode` writes a fixed unit (the plan's cached answer) | RunExamples.lean:142 |
| S2 | lean/VE/Commands/Run.lean | `matchedRecord` ignores the records' targets | :73 (P3), :75, :125, :127; `proofTask_one` |
| S3 | lean/VE/Commands/Run.lean | `matchedRecord` takes the first matching record | :74 (P3′), :128; `proofTask_one` |
| S4 | lean/VE/Commands/Run.lean | `proofTask` skips `checkedAddressee` | :87 (P7); `proofTask_one`, `readInstruction_refused_classed_of` |
| S5 | lean/VE/Commands/Run.lean | `proofMany` lists a reading two records match (O2) | :128 |
| P1 | ve/backends/lean_service.py | no deadline for `english.command` | tests/test_lean_service.py::test_the_deadline_keys_are_the_handshakes_modes |

Each was planted, shown failing, and restored. The plan's fourth seed (Python `read_command` accepting a fill the
request does not hold) is ci-2b's: `read_command` does not exist yet. No Rust product code changed.

## Trust

`uv run python tools/trust_map.py --check`: "K +0, S +0, … trusted +141", PASS with the allowance (V +141, signed
R16) in `docs/trust-baseline.json`; per file in DELTA.md. R16's mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/Commands/RunExamples.lean --test
lean/VE/Service/RegistryExamples.lean --allow …/trust-mutants-allow.json`, then `--rescore` on each later Lean tree):
`docs/commands-imperatives/ci-2/trust-mutants.json` at ad415a76a, the final Lean tree: 14 definitions, KILLED 229,
SURVIVOR 0, UNKNOWN 0, INVALID 40, ALLOWED 37, NOT RUN 0. The first run (c3508e1e4) had 20 survivors and 29 unknown:
the survivors were killed by the guards of fd80f6039, and the 29 unknown (mutated text Lean refuses) and the
equivalent `take 1` mutants (at most one fill) are allowed with reasons in `trust-mutants-allow.json`. The six new or
changed trusted definitions with no operator site have hand mutants H1 to H6 in `mutants.json`, each killed.

## Tests

The selected tests (`mac-pytest.sh --select`, base 94580b39b, at c3508e1e4): the fast stage ran 412 of 538 units,
"1 failed, 11908 passed" (`test_every_json_handling_lean_file_is_classified`), and the six cloud shards ran the rest:
shards 2, 4, 5 and 6 passed, shards 1 and 3 failed `test_relay_mutation_gate.py::test_every_route_has_fixtures`,
`::test_the_gate_passes_on_every_route[service:english.command]` and
`test_shape_binding_mutants.py::…[english.command]` (results on `claude/cc-result-ci-2-c3508e1e-t765432-s*`). Fixed
in fd80f6039 and 54d980238; rerun of exactly those ids (`mac-pytest.sh -- <ids>`): 1 passed, then 3 passed. After the
fix, `tests/test_lean_service_schema.py` (every corpus case through the real service): 161 passed;
`tools/relay_mutation_gate.py --route service:english.command`: 1126 mutants, 1118 refused, 8 allowed, 0 failures.
`tools/gate_collection.py --check --prebuilt`: 3 added, 0 removed, 0 refused, 0 stale, 0 malformed.
`uv run python tools/regen_generated.py --check`: 35 entries checked.

Not run, per the task: the full gate (the chain runs it on the final HEAD), and no whole-UDHR or constitution run.
Pre-existing failures on main (main-known-red.txt) were not touched.

## Pilot bytes

Expected: 0 from this batch (no document path calls the mode). CI-1's +9 segments / +273 B reach a document only
through ci-2b's wrapper. Nothing is claimed before a pilot audit.

## ci-1's review items folded here

F2 (ci-1's DELTA.md said no `ve/` path changed): fixed. F6 (the spec was not in the tree): the plan and spec are
copied. ci-1's `goCase` is the base of O2's fixture. F3 (the A/B's two rows) is ci-2b's, with the A/B. F4's hand
mutants of `Read.lean` and F8 (`ofCondition` and "Sentence 2") were left to ci-1b. F5's second translation in
`unreadOf` is removed by the ci-2 review fix: the refusal formatter receives the original `TranslateOutcome`.

## ci-2b

Blocked by ci-2 and ci-1b (the DRI's backlog row). It carries (4) to (6) and the spec's two statements, exactly as
`docs/spec/commands-imperatives.md:679-689` states them:

```lean
theorem readInstruction_refused_classed (ctx : Context) (s code text : String)
    (h : readInstruction ctx s = .refused code text) : (Texts.classOf code).isSome = true

theorem readInstruction_typed (j : Lean.Json) (ctx : Context) (r : Reading) (D : VE.SpeechActs.SpeechDoc) (u : String)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok ctx.se)
    (h : readInstruction ctx s = .one r)
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true)
    (hq : ∀ q ∈ ctx.queries, (q.id, "query") ∈ ctx.se.ne.rv.vocabulary.constants) :
    VE.SpeechActs.commandOk D (r.command u) = true
```

with `hw : VE.Scope.JsonWF j` added beside `hd` (reviews/dri-decisions-20261102-ci-1.md item 1), through ci-1b's
`readCommand_typed`. Also ci-2b's: the plan's Python seed (`read_command` accepting a fill the request does not
hold), the A/B over the pinned command corpus with ci-1's review F3, and the relay gate's F4/F10 entries for this
route, which `read_command`'s binding retires.

## Next item

ci-2b, then ci-5.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: PASS. `uv run python tools/relay_mutation_gate.py --route service:english.command`: "1126 mutants, 1118 refused, 8 allowed", 0 failures (the 8 are ci-2b's request bindings, allow-listed F4/F10 with literal paths); `tests/test_lean_service_schema.py`: 161 passed (genuine answers of every corpus case, each field dropped, emptied, nulled and retyped against `ve_response_decode`); the corpus's adversarial requests (300-deep array, `{}`, no environment) and F-raw (`RunExamples.lean:154`) are error rows.
2. Deliverables built, no rule broken: PASS. The table above; (4) to (6) are ci-2b under the task's size clause. No Python decision code is added (the corpus builds requests only); no permanent report test; no authority switch; `ve/backends/english_lean.py` and `tests/test_relay_binding_inventory.py` (jt-3, pc-2a) are not touched; the other shared files are generated or union-merged (`lean/VE.lean`, `lean/VE/Audit.lean`).
3. Tests and gates can fail: PASS. `mutants.json` (S1 to S5, P1, each with its failing guard or test); `trust-mutants.json` (229 killed, 0 survivors, 0 unknown) and the hand mutants H1 to H6; the allow-list entries name literal paths.
4. Python, Lean and Rust agree: N.A.: no Python or Rust path reads command English in this item (no A/B base exists); the Python-built corpus cases read through Lean as the Lean guards do (P1′, P2, P6, P7 outcomes).
5. R8 binding: N.A.: no Python code reads the answer until ci-2b's `read_command`; the shape binds `id`, `unit` and `wording` (`equals`), and the relay gate's rebind mutants of them are refused.
6. Gate evidence on the final HEAD: PASS for what this item runs: main merged (ef6c43f75), `regen_generated.py --check` 35 entries; the full gate is the chain's, on the final HEAD.
7. No unsigned item: PASS. DELTA row 1 cites R16; `trust_map.py --check` PASS with the allowance; no row reserves the DRI.
8. Every user-visible change in DELTA: PASS. Public output none: no CLI, document or conformance path calls the mode (`git grep -n english.command -- 've/*.py' 've/**/*.py'`: only `ve/backends/lean_service.py:159-160`, the deadline).
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main) --explain`: 538/538 units, because every service test reads `envelope.json`, whose mode list gains the mode, and the service links `VE.Commands.Run`; the selection contains P1's failing test.
10. Statements say what is claimed: PASS. S2 to S4 break `proofTask_one` and `readInstruction_refused_classed_of`; renaming `wording` in `Run.encode` breaks `encode_fits` (`lake build ResponseShape.Encoders.Command`: "unsolved goals" at `Encoders/Command.lean:15`); `caseReported_eq` is about the value `caseReported` returns. The two facts-based statements are named as such and do not claim the spec's.
11. Budgets and limits fail closed: PASS. Budget 0 is `limit` (`RunExamples.lean:103`); 401 bytes `limit` (:111); 65 readings `limit` (:134).
12. No CPU regression: N.A.: no document or pilot path calls the mode; each proof sentence or matched command condition is translated once, inside `_CORE`'s deadline.
13. `Test-removed` trailers: PASS. `tools/gate_collection.py --check --prebuilt`: "3 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed".
14. Both directions, cited evidence, spec re-read: PASS. 400 bytes `one` and 401 `limit` (:110, :111); 64 `many` and 65 `limit` (:134); one matching record `one` (:71) and none, a wrong one or two `QueryMismatch` (:72 to :74); an addressee `one` and none `UnboundSlot` (:71, :87); two matching readings `many` and one `QueryMismatch` (:125, :127); a declared query id read (:174) and an undeclared one refused (:159); every fixture request accepted and F-raw refused (:181, :154). Spec re-read: listed under the deviations.
