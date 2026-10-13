# Merge and review tooling (eff-merge)

Opportunities 1, 2 and 7 of the October efficiency baseline (`manage-agents/reviews/efficiency-baseline-2026-10.md`):
mechanical regeneration and merging of generated files, a mutation gate over every relayed Lean answer, and a
seeded-mutant harness. These are tools, not product logic: each runs the owner of the logic it touches (a
generated file's own generator, the service client's own reader, pytest through `tools/nested_pytest.py`).
Every number below is read by `tests/test_merge_tooling_evidence.py` from the saved evidence in
`docs/merge-tooling/`, never from a live run.

## 1. Generated files: `tools/regen_generated.py`

`GENERATED` in the script is the one list of generated inventories, manifests and locks. Each entry names its
files, the command that rewrites them and the one that checks them (both belong to the file's generator), and
its merge strategy:

| Entry | Files | Merge |
|---|---|---|
| gitattributes | `.gitattributes` (generated from this list) | regenerate |
| wire-contract | `lean/VE/WireContract/{Limits,Names}.lean`, `Tables/*.lean`, both `contracts.lock`, `docs/spec/*-wire-table.md` | regenerate |
| english-grammar | `lean/VE/EnglishGrammar/Fixed/*.lean`, `ve/english_grammar/LOCK.json` | regenerate |
| english-lexicon-fixtures | `lean/VE/EnglishGrammar/LexiconFixtures.lean` | regenerate |
| question-fixtures | `lean/VE/Question/Fixtures.lean` | regenerate |
| english-run-copy | `lean/VE/Service/EnglishRun.lean` | regenerate |
| route-cases | `lean/VE/Route/examples/route-cases.json` | regenerate |
| lean-roots | `lean/VE.lean`, `lean/ResponseShape.lean` | union |
| lake-build | (the build every later entry reads) | - |
| lean-statements | `lean/statements.txt`, `predicates.txt`, `declarations.txt` | regenerate |
| lean-audit-manifests | `lean/VE/Audit.lean`, `lean/ResponseShape/Audit.lean`, `lean/axioms.txt` (`audit.py --write`, from `declarations.txt`; AR-1) | regenerate |
| frozen-inventory | `lean/VE/Route/frozen-sources.sha256` (`frozen.py --write`, new) | regenerate |
| trust-tables | `tools/trust-classes.json`, `docs/trust-baseline.json` | json (check only) |
| checker-pins | `lean/checkers.lock` (pins the built `ve_service` and the Rust release binary) | json |
| response-schemas | `ve/backends/lean_service_schema/*.json` | regenerate |
| english-codes | `ve/english_grammar/codes.json` | regenerate |
| question-codes | `ve/question/codes.json` | regenerate |
| question-lock | `ve/question/LOCK.json` | regenerate |
| assurance-manifest | `ve/assurance-manifest.json` (decoder total recomputed) | json (check only) |
| assurance-doc | `docs/spec/assurance-manifest.md` (`assurance_manifest.py --check`, new) | regenerate |
| layer-ledgers | `tools/layer-exceptions.json`, `lean-layer-exceptions.json` | json (check only) |
| import-contract | `.importlinter` | regenerate |
| uv-lock | `uv.lock` | regenerate |
| gate-collection | `tools/gate-collection.json` (last) | regenerate |

`python tools/regen_generated.py --list` prints every command. `--write` runs the writers in that order,
`--check` runs the checks (a writer without a check is checked by rewriting and comparing, then restoring);
`--only`/`--skip NAME` select entries; `VE_REGEN_NO_RUST=1` leaves the Rust pin alone. On a clean tree
`--check` passes every entry (16 minutes on the VM, most of it `lean/audit.py` and the statement dump) and
`--write` changes nothing.

Strategies: *regenerate* takes either side and lets the writer rebuild the file; *union* takes the line union
of both sides (the build that follows, `lake build`, catches a wrong one); *json* is a
structural three-way merge (`merge_json`): objects per key, records per key field (`id`, `file`, `name`,
`path`), other lists keep both sides' additions and drop either side's removals, a value derived from the
rest (the decoder `total_lines`) is recomputed, and a value both sides changed differently is a conflict left
to a person or the sync agent. Ledgers are never rewritten: growth beyond the signed trust budget still needs
`trust_map.py --write --reason`, and decoder pins are still reviewed by hand.

Not regenerated (`NOT_REGENERATED`, each with its reason; `tests/test_regen_generated.py` fails on a script
with a writing mode that is in neither list): reviewed ledgers (`conformance/difffuzz-baseline.json`), batch
and conformance reports, recorded oracles and evidence pinned at a commit, use-case results, and
`docs/spec/semantics-inventory.md` (reads repositories outside this tree). `rust/Cargo.lock` and
`lean/lakefile.toml` are hand-written sources, not generated.

### Merge driver and the merge train

`.gitattributes` marks every generated pattern `merge=ve-generated`. Install the driver once per repository
(the config is shared by all worktrees; a branch without the script falls back to an ordinary conflict):

    python3 tools/regen_generated.py --install-driver

How merge-train uses it, in place of the agent sync when only generated files conflict (presync, outside the
lock; the same in the under-the-lock re-merge):

    git -C $wt merge -q --no-ff --no-commit $h > /dev/null 2>&1   # the driver merges generated files
    ( cd $wt && PATH=~/.elan/bin:$PATH uv run python tools/regen_generated.py --resolve ); rc=$?
    if [ $rc -eq 0 ]; then git -C $wt commit -q --no-edit            # mechanical: no agent
    else git -C $wt merge --abort                                     # rc 2: other conflicts; rc 1: a check
      <agent sync as today, with the --resolve output in the prompt>  #   failed (for example the trust budget)
    fi

`--resolve` needs a merge in progress. If a conflicted path is not a generated file, or a ledger value
conflicts, it writes nothing and exits 2. Otherwise it merges the conflicted generated files by their strategy
(also without the driver, from the index stages), runs every writer and every check, stages the generated files
and exits 0; a failed writer or check exits 1. Run it after a clean merge too: two sides can merge textually
and still leave a derived file stale. The verify that follows is unchanged.

Evidence (`docs/merge-tooling/sync-merge-survey.json`, `docs/merge-tooling/survey.py`): of the sync merges in
main's history, re-merged in memory with `git merge-tree`, the ones with conflicts only in generated files
would have needed no agent. The replay of one of them (`docs/merge-tooling/replay-dddeb893.json`: sync merge
`dddeb893` of readings-defaults/rd2b, both parents plus this batch's commits): with the driver `git merge` left
no conflict; the assurance manifest and trust classes came out with exactly the agent's content, the audit
manifests identical; `--resolve` ran every writer and every check passed except the trust budget (+21 trusted
lines over the signed allowance, which the agent had rebaselined with a reason): a decision for a person, as
designed. That tree predates `wire_contract.py --write --generated-only`, so the replay skipped that entry.

| Number | Value |
|---|---|
| sync merges surveyed | 97 |
| sync merges without conflicts | 28 |
| sync merges with conflicts only in generated files | 16 |
| sync merges with other conflicts | 53 |
| replay: files conflicted without the driver | 4 |
| replay: files conflicted with the driver | 0 |
| replay: failed checks | 1 |

## 2. Relay mutation gate: `tools/relay_mutation_gate.py`

A route is one way `ve` reads a Lean answer: each of the 31 service modes (read by `LeanService.exchange`,
the transport of `relay`) and each one-shot runner call site (the manifest bindings whose operations have call
sites, and every call of the one-shot route reader outside `ve/backends/lean.py`: 7 today). For every route the
gate takes genuine answers (the built executables' answers to the committed requests in
`tests/data/relay-gate-cases.jsonl`), mutates the answer itself (a one-shot answer's row array loses and gains
rows) and every field of it (drop, empty, duplicate an element or a key, retype
to each other JSON type and, near the top, to a 10,000-deep array; rebind a request name, position, digest, nonce or count to one the request does not
hold), and sends each mutant through the route's own reader with the line or runner output replaced. Each must
raise `CheckerUnavailable`. It fails on an accepted mutant, a crash, another `VEError` (a malformed answer read
as Lean's rejection), an untyped field (every retype accepted) or a manifest type `json`, unless
`tools/relay-gate-allow.json` lists it; on an allow-list path that matches nothing; on an allow-list entry that
names no single route or lists a path of wildcards only; and on a route without an `ok` fixture. The most
specific entry takes a finding (a literal path first), so a broad follow-up never takes a narrower entry's
count. Run it in about 8 minutes:

    uv run python tools/relay_mutation_gate.py [--json OUT] [--route NAME ...]
    uv run python tools/relay_mutation_gate.py --record    # re-record the fixtures from a test run

`--record` runs the tests in `RECORD_TESTS` with `tests/route_case_recorder.py` (`VE_RELAY_CASES`) and keeps the
smallest two requests of each answer shape of each route, plus the service corpus `tests/lean_service_corpus.py`.

Suggested wiring (not done here; manage-agents scripts are outside this repository): `infra-item.sh` runs it
before review and fixloop before recheck, on the routes of the diff (`--route`).

The allow-list has two kinds of entries. *By design* (B0 to B6): content Lean computes (an emptied or repeated
list or map the runners decide, which the threat model leaves to the service; listed path by path for each
route, never an id, digest, name or request-bound list), readings-route's opaque `inner`
row, echoed vocabulary content the caller compares with Python's regeneration, documented unions, rendered
text, optional diagnostic extras, and bundle lemma ids the caller compares. *Follow-ups* (F1 to F11) are open
relays, listed below. The one open relay fixed in this batch was small: the speech-source reader crashed with
`TypeError` on a unit whose `class` or `status` was a list or an object (a set membership test); it now
refuses it.

| Number | Value |
|---|---|
| routes | 38 |
| service modes | 31 |
| one-shot routes | 7 |
| fixtures | 465 |
| mutants | 106761 |
| refused | 98511 |
| accepted and listed | 8250 |
| accepted by design | 2949 |
| accepted follow-ups | 5301 |
| untyped fields | 250 |
| unlisted findings | 0 |

Follow-ups (accepted mutants per item in the saved report):

| Id | Accepted | Open relay |
|---|---|---|
| F1 | 1835 | English service modes (`english.read`, `english.grammar`, `english.check`): the schema types `id` and `result` as `true` |
| F2 | 815 | readings-route `filled`: `environment` untyped, `units` an array of anything |
| F3 | 660 | retype accepted (a union, no type, or untyped array items that take a 10,000-deep array) in check, english, parse, readings-route and reports fields |
| F4 | 1236 | request names (predicates, sorts, targets, units, sets, labels, choosers, profiles) not checked against the request |
| F5 | 139 | optional fields whose encoder condition the schema does not state |
| F6 | 35 | maps keyed by request names: a dropped entry is accepted |
| F8 | 62 | `ve_metered` `evaluation` typed `object` in the assurance manifest |
| F9 | 9 | senses.read: the projected environment's vocabulary is not bound to the request's |
| F10 | 264 | request-bound lists the schema does not bind (choices and readings per open set, tuples and argument and sort lists of a predicate's arity, echoed profiles and units): an emptied or repeated element is accepted |
| F11 | 246 | strings the schema lets be empty (ids, digests, names, labels, generators, rendered text) |

F7 (34 untyped fields in check, parse, readings-route and reports) overlaps F3. Each follow-up is a schema
change in `lean/ResponseShape/Schemas` (or the manifest's response types) plus `response_schemas.py --write`;
none is small.

Not yet covered: readings-defaults RD-4b's answer shapes (merged from ve-integration `cc534bfc`). The committed
fixtures predate them, so the gate passes without exercising them. Adding RD-4b's tests to `RECORD_TESTS`
(`test_readings_verdicts_lean.py` and `test_readings_components_{lean,load,document}.py`) and re-recording gave
131 accepted mutants: 126 under readings-route's `components` rows (`checked`, `document`, `answer/filled`,
`answer/fill_premises`, `answer/sets`, the `component` name) and 5 in `english/*/component`, `english/*/result`,
`per_choice/*/query` and `sentence`. It also left 27 allow-list paths matching nothing, because the
smallest-per-shape picks moved. `ve/readings_components.py` binds these rows to the request after the transport.
The gate reads only the transport, so each path still needs a B or F entry, and that classification goes to the
DRI. Until then the fixtures stay as they were reviewed.

## 3. Seeded mutants: `tools/mutants.py`

A builder commits `mutants.json` (`{"mutants": [{"id", "file", "find", "replace", "tests" | "command",
"claim"}]}`); the harness checks each `find` occurs once, runs the tests on the unmutated file (they must pass),
applies the mutant, requires a named test to FAIL (pytest exit 1 with the node in its summary: a collection
error is not a kill) or the command to exit non-zero, and restores the file's bytes and mtime. Exit 1 on any
survivor.

    uv run python tools/mutants.py MUTANTS.json [--id ID ...] [--evidence OUT.json]

`tools/mutation_check.py` applies its layer mutations through the same `applied()` helper. Building the harness
found two real problems: a same-length mutant written within the second of the baseline's import ran Python's
stale `.pyc` (the mutated file's mtime now moves), and one of this batch's tests wrote to a repository file and
left it changed under a mutant (it now works in `tmp_path`). One planted mutant was equivalent (pytest runs only
the named tests, so filtering failures to them cannot change the result) and was replaced.

This batch's mutants are `docs/merge-tooling/mutants.json`, one per claimed behaviour (and one on this document's
numbers), with the results in
`docs/merge-tooling/mutants-evidence.json`:

| Number | Value |
|---|---|
| seeded mutants | 21 |
| killed | 21 |

## Acceptance

| Item | Tag | State |
|---|---|---|
| `tools/regen_generated.py` with `--check`, every generated file and its generator | AGENT | done; clean-tree check and write pass |
| `.gitattributes` and the merge driver; `--resolve` for merge-train | AGENT | done; replay of `dddeb893` |
| Wiring `--resolve` into `merge-train.sh` | EXTERNAL (orchestrator, manage-agents) | deferred: the commands are above |
| Installing the driver in the shared repository config | HUMAN (orchestrator) | deferred: `--install-driver` |
| `tools/relay_mutation_gate.py` over every relayed route, failing on a route without fixtures | AGENT | done |
| Fixing the open relays found | AGENT (small) / follow-up | the speech-source crash fixed; F1 to F11 listed |
| Review of the allow-list's by-design entries | HUMAN (DRI) | deferred |
| Gate fixtures and allow entries for RD-4b's readings-route shapes (section 2) | AGENT after DRI | deferred: 131 accepted mutants to classify |
| Running the gate from `infra-item.sh` and fixloop | EXTERNAL (orchestrator, manage-agents) | deferred |
| `tools/mutants.py` and this batch's seeded mutants | AGENT | done: 21 of 21 killed |

## Not run, and outside this repository

- The full test suite and the release gate (the merge train runs them). The targeted runs are listed in the
  batch report.
- `merge-train.sh`, `infra-item.sh` and fixloop are not changed: the commands above are how they would call the
  tools. The garbled seeded-mutant sentence in `infra-item.sh` (baseline section 6) is still to fix there.
- The driver is not installed in the shared repository config; `--install-driver` does that.
