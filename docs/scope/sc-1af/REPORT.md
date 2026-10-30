# sc-1af: the `JsonWF` guarantee on real input, as a proved check at the scope route's boundary. Build report

**Status: built, no DRI signature reserved.** HEAD: the commit that adds this report (code final at `226aa8dcb`).
Changed: a total `jsonWF? : Json → Bool` and `jsonWF?_sound` beside `JsonWF` (`lean/VE/Scope/Govern.lean`), and
`decodeBlock` refuses a front matter that fails it with `InvalidInput` naming the unit, before any `govern_*` path.
`decodeBlock_jsonWF` gives `JsonWF D.doc ∧ JsonWF D.block` from the check's success. Open: SC-1b's end-to-end
statement on the check (next item). Selected tests: 398 of 398 passed. The full gate is the chain's to run.

The DRI's decision implemented: `reviews/dri-decisions-20261028-sc-1af.md` item 1 (it amends the condition of
`reviews/dri-decisions-20261027-featureplan-gates.md` item 2). Synthesis round 2's edits to the scope plan
(`debates/plan-synthesis-2/edits-scope.md`, items 1-7 and DEC 10/16) are about SC-2, SC-3b, `foldGovernors`, names,
shared files, headings and layout readers. This item implements none of them and conflicts with none.

## Deliverables

| Task line | Delivered | Commit | Test |
|---|---|---|---|
| (1) a total `jsonWF? : Json → Bool` (structural recursion, no `partial`) and `jsonWF?_sound`, beside `JsonWF` | `jsonWF?`, `listWF?`, `implWF?` (one `mutual` block, each `termination_by structural`), `balanced?`, `ascending`; `jsonWF?_sound : jsonWF? j = true → JsonWF j` (dumped statement `lean/statements.txt`: `∀ {j : Lean.Json}, VE.Scope.jsonWF? j = Bool.true → VE.Scope.JsonWF j`), with `balanced?_sound` and `ascending_sound`. The objects' `kvs.WF` is decided through Std's `Impl.WF.wf` (balanced and ordered) | `a1c66e1ab` | `lean/VE/Scope/Examples.lean:760-794`; `example … := jsonWF?_sound (by decide)` at `:794` |
| (2) the scope route runs it on every parsed document and decoded rule before any `govern_*` path, refusing with `InvalidInput` naming the unit | `illFormed` and its call at the top of `decodeBlock` (`lean/VE/Scope/Wire.lean:103-118`). `decodeScope` (`VE/Service/Document.lean`) calls `decodeBlock` before `checkDoc` and `checkDocSets` call `governFast` or `governSetsWith`. Every rule the route decodes is read from the checked tree: units' parts and rules, the scope block's frame parts and conditions, and the environment. `decodeBlock_jsonWF` (`lean/VE/Service/ScopeAdmission.lean:111`) proves `JsonWF D.doc ∧ JsonWF D.block` from success, so the decoded block's payloads are covered (spec 11.3) | `a1c66e1ab`, `226aa8dcb` | `lean/VE/Scope/WireExamples.lean:165`, `:172` |
| (3)(i) each F-raw tree fails `jsonWF?` and is refused at the boundary with `InvalidInput` | `rawA`, `rawB` (F-raw item 1's two trees), `rawUnit`, `rawRule`, `rawUdhr` all fail. At the boundary each is refused naming its unit: `document`, `units.u0165.s01`, `units[2]` (id unreadable), `scope` | `a1c66e1ab` | `Examples.lean:760`, `:1058`; `WireExamples.lean:165` |
| (3)(ii) every scope route fixture passes `jsonWF?` (booleans and numbers included), so no answer on main changes | each scope document of `tests/test_scope_document.py` (F1, the F1 probe, and every chain × effect document, each with a boolean and a number) is answered and never refused there. The route's parsed `ScopeExamples` documents pass, as do the Lean fixtures (`hcDoc parts`, `udhrDoc`, `lDoc udhrPieces`, `softEnv`, `envJ`, `leadPart`, and a parsed document of booleans and numbers). The selected run (398 units) passed unchanged | `a1c66e1ab` | `tests/test_scope_document.py::test_sc1af_every_scope_route_fixture_passes_the_boundary_check`; `lean/VE/Service/ScopeExamples.lean:97`; `Examples.lean:761`, `:1058` |
| (3)(iii) a mutant dropping any constructor case from `jsonWF?` or `JsonWF` fails the build or a test | all 12 drops fail the build. Each wrong-constant case fails a `#guard` | `bcdd4d78d` | `docs/scope/sc-1af/mutants.json` |
| (3)(iv) F-raw's four `#guard`s stay in `Examples.lean` | unchanged at `:738`, `:743`, `:748` (and F-raw-title's at `:1027`) | none | `git diff main -- lean/VE/Scope/Examples.lean` adds lines only |
| (4) seeded bugs: boundary call removed; `jsonWF?` `true` on objects; one per new trusted definition | 41 seeded mutants, all killed (below) | `bcdd4d78d` | `docs/scope/sc-1af/mutants.json` |
| Python only relays (R8), no Python copy of the check | no Python product file changed (`git diff --stat main...HEAD -- ve/*.py` is empty). Only `ve/assurance-manifest.json` changed, a pin | none | none |
| Fixtures on both sides of every boundary of each check | balance: 1 against 0 passes, 2 against 0 fails; 3 against 1 passes, 4 against 1 fails (both sides of the tree); stored size right or off by one either way; keys ascending, swapped, repeated, a third out of order; a bad value at the root, left, right, first or second in an array, deeper; the boundary's unit naming on all three paths and the next check reached on a well-formed document | `a1c66e1ab` | `Examples.lean:768`, `:772`, `:780`, `:783`, `:787`; `WireExamples.lean:165`, `:172` |
| Evaluator rule (each value read once, size charged against a stated limit, a large well-formed fixture) | each node is read once by `jsonWF?`/`listWF?`/`implWF?` and once by `balanced?`. An object's keys are listed once, and only after its tree is balanced (`&&` stops first), so in `O(n log n)`. The limits are the route's own: `maxLineBytes` (16 MiB, `lean/VE/Limits.lean:42`) and depth 256 (`VE.Json.parse`). Fixture: an object of 20,000 keys and a 255-level nesting pass, and a malformed tree under 255 levels fails | `0eb06471b` | `Examples.lean:790`, `:792` |

**Spec re-read** (checklist 14):
- `jsonWF?_sound` against the decision's text (`reviews/dri-decisions-20261028-sc-1af.md` item 1): identical.
- `JsonWF` is unchanged, so it still matches spec 11.3's `Pinned.JsonWF` (`docs/spec/scope.md:2091-2099`) and sc-1ae's definition (`Govern.lean:283`).
- The boundary against spec 11.3's "Its parser lemma … discharges it for every decoded document … a decoded block's payloads are parsed, so the same lemma discharges it" (`docs/spec/scope.md:2093-2099`, as amended by the decision): `decodeBlock_jsonWF` gives the document and its block.
- The refusal text against the block's wire faults (`wireFault`, spec 3): same form, `InvalidInput: scope@0 <path> must be <form>`.

## Seeded bugs

Lean is the only language whose product code changed. 41 mutants, each applied alone to the committed source,
built, and restored (harness and rows in `docs/scope/sc-1af/mutants.json`). For mutants that also break
`jsonWF?_sound`, the proof block was stubbed so the `#guard`s run; each such mutant also fails the build as written.

| Definition | Mutants | Killed by |
|---|---|---|
| `decodeBlock` (Wire.lean) | the boundary call removed | `WireExamples.lean:165` |
| `illFormed` (Wire.lean) | the unit not named; no index fallback; the scope block not named | `WireExamples.lean:165` (each) |
| `jsonWF?` (Govern.lean) | `true` on objects; objects skip key order, balance, or values; `true` on arrays; `false` on null, bool, num, str; each of the 6 cases dropped | `Examples.lean:760`, `:780`, `:761`; drops: build (missing cases) |
| `listWF?` | `false` on `[]`; skips the rest; skips the head | `Examples.lean:761`, `:760`, `:760` |
| `implWF?` | `false` on leaf; skips left, root value, right | `Examples.lean:761`, `:783`, `:760`, `:783` |
| `ascending` | a repeated key passes; only the first pair checked; `false` on one key | `Examples.lean:780`, `:780`, `:761` |
| `balanced?` | skips left, right, the stored size, the left ratio, the right ratio; 2 against 0 passes | `Examples.lean:772` (each) |
| `JsonWF` (sc-1ae's, condition iii) | each of the 6 constructors dropped | build: `jsonWF?_sound` (`Govern.lean:349-357`, unknown constant) |

No mutant survived. The pytest of (ii) is a test, not product code. A seeded bug in `jsonWF?` would reach it only
through a rebuilt service binary, which `lean/checkers.lock` does not pin, so the bug was not seeded through it.
The same path is covered in Lean by `ScopeExamples.lean:97` (UNVERIFIED as a kill: not part of the mutant runs).

## Trust

`uv run python tools/trust_map.py --check` on the final code: "against 81b8371210db: K +0, S +0, D +10, G +31,
tied +0, unclassified +0, trusted +1". The +1 is `decodeBlock`'s boundary line, recorded with `--allow` under R16,
with a FOLLOW-UPS.md row "## sc-1af" for the ties pass. The check is reject-only: G[R] in `Govern.lean`, as
`admitBlock` and `orderCheck` are, and D[R] for `illFormed` in `Wire.lean`, as `membersIn` is. The fixture
definitions are T. trust_mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --json
docs/scope/sc-1af/trust-mutants.json`) exited 0 with "0 definitions, 0 mutants": nothing new is trusted, and the
seeded mutant above covers the one changed trusted line.

## Size and evidence

- Hand-written lines: 314 by `git diff --numstat $(git merge-base HEAD main)`. That counts the Lean sources, the
  test, the trust table, the manifest pin and the mutants evidence, but not this report, DELTA.md or generated files.
  With this report and DELTA.md it stays under 600.
- Commits (`git log --oneline main..HEAD --no-merges`): `a1c66e1ab`, `0eb06471b`, `bcdd4d78d`, `796aea2f1`,
  `226aa8dcb`, and the report commit.
- Runs on the final code:
  - `lake build`: rc 0, 1161 jobs.
  - `python3 lean/audit.py`: PASS (670 files, 7483 theorems).
  - `regen_generated.py --check`: rc 0, 33 entries.
  - `gate_collection.py --check --prebuilt`: 1 added, 0 removed, 0 refused, 0 stale, 0 malformed.
  - `tests/test_assurance_manifest.py`: 138 passed.
  - `tests/test_scope_lean.py`: 18 passed.
- Selected tests: `mac-pytest.sh --select -- --base 81b837121 --run` ran on GitHub Actions in 4 shards on tree
  `e202bc44eb` (HEAD `796aea2f1`), and 398 of 398 units passed. The later commit `226aa8dcb` changes one Lean
  lemma's statement (proof only), plus generated inventories and the mutants JSON's layout. No selected test was
  rerun after it.
- No test in `main-known-red.txt` was among the failures (there were none).
- Not run: the full gate (the chain runs it on the final HEAD).

Pilot bytes: 0 expected (the task: "Bytes 0"). The check refuses no tree a parser builds, so no unit's status moves.

## Next item

SC-1b's end-to-end statement, discharging `JsonWF` from `decodeBlock_jsonWF` (never as a bare hypothesis). Also
sc-5rc's (1), the four `Pinned.JsonWF` statements, if it was cut to sc-5rd.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A. No response field or schema changed. The new refusal is an
   `InvalidInput` string the document mode already relays. The route's answers are unchanged:
   `test_sc1af_every_scope_route_fixture_passes_the_boundary_check` and the selected run.
2. Every deliverable built, no rule broken: PASS (the Deliverables table). There is no Python copy of the check
   (`git diff main...HEAD -- 've/*.py'` is empty). No report test was added, and no in-flight branch touches these
   files (overlap check over `feature/*`, `lean-first/*`, `infra/*` and `foundation/*`: none).
3. Tests and gates can fail: PASS. 41 of 41 seeded mutants were killed (`docs/scope/sc-1af/mutants.json`), and
   trust_mutants exited 0 (`docs/scope/sc-1af/trust-mutants.json`).
4. Python, Lean and Rust agree, valid inputs still pass: PASS for valid inputs
   (`test_sc1af_every_scope_route_fixture_passes_the_boundary_check`, `ScopeExamples.lean:97`, `Examples.lean:761`).
   Rust is untouched.
5. R8 binding: N.A. No field Python reads changed, and Python is unchanged.
6. Gate evidence matches the final HEAD: PASS for the evidence here. The commit list comes from
   `main..HEAD --no-merges`, the base from `git merge-base`, and the full gate is the chain's.
7. No unsigned item: PASS. DELTA.md row 1 is SIGNED by the DRI's decision file, and row 2 cites R16 with
   `trust_map.py --check` and a FOLLOW-UPS row.
8. Every user-visible change in DELTA: PASS. One refusal, reachable only by trees no parser builds. No answer
   changed on any fixture (selected run, 398 passed).
9. Test selection finds the tests: PASS. The selected run listed `tests/test_scope_document.py` as changed and ran
   398 units, not every unit. The Lean guards run in `lake build`.
10. Lean statements say what is claimed: PASS. `jsonWF?_sound`'s dumped statement is the decision's. The output-wrong
    mutants (`jsonWF?` `true` on objects, and others) break `jsonWF?_sound` as written (mutants.json harness note).
11. Budgets, limits, deadlines fail closed: PASS for its scope. The check is total, with no budget of its own, and is
    charged against the route's `maxLineBytes` and depth 256, with the large fixtures at `Examples.lean:790`, `:792`.
12. No CPU or memory regression: PASS by construction, no timing claimed. The check is `O(n log n)` and lists keys
    only after balance (`Examples.lean:790` builds and checks 20,000 keys inside `lake build`).
13. `Test-removed` trailers: N.A. `gate_collection.py --check --prebuilt` reports 0 removed.
14. Both directions, cited evidence, spec re-read: PASS. Each check has an accepting and a refusing fixture
    (`Examples.lean:768`/`:772`, `:780`, `:783`; `WireExamples.lean:165`/`:172`). Claims cite commands above, and
    the spec re-read is listed under Deliverables.
