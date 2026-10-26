# sc-1b: the Lean document mode admits `scope@0` (SC-1b). Build report

**No DRI signature is reserved.** Left for after sc-1ae (the DRI's choice between sc-1ad's fixes (a) and (b)):
`decodeScope_bound` and `decoded_no_new_symbols`, which need `BlockBound` and `HasStr`; neither is defined or
restated here. Cut by size: the B1 benchmark row, named **sc-1bb**.

**Over the size rule: 1,267 hand-written lines before this report and DELTA (about 1,430 with them), against the
~600 the common rules allow.** The item was not measured at its midpoint and was not cut there. Where the lines
are (section "Size"): product code 282 (Lean 273, Python 9), the proofs and the encoder theorem 230, fixtures and
tests 460, ledgers and side tables 205, evidence 90. Most of the fixtures (WireExamples, the F1 fuzz test) were
added to kill `trust_mutants`' survivors, which R16 requires. The only part that separates cleanly is the Python
relay with its end-to-end and fuzz tests (about 145 lines). Removing it would still leave the item over twice the
limit, and it would change DELTA row 3(e), so I kept it. The reviewer or DRI should decide whether to take the item
at this size or split the relay out as sc-1bb.

- Branch `feature/sc-1b`, worktree `/home/seyran/code/ve-sc-1b`, merge base `e9e63dda7` (main, after ap-1e; ap-1b,
  sc-1ad and sc-3ab merged).
- Plan and spec on main, unchanged: scope-PLAN "SC-1b", design 1.2-1.6, the SC-1b rows of section 6; spec 1.1, 1.5.8,
  1.6, 3, 5.2, 6, 7.2 and 8.1. SYNTHESIS 2.2 (the profile-gate table and its row "Rows: AP-1, AT-3a, SC-1b, …"), 4.2
  (`Dispatch.lean` rows in landing order; the Lean `document` mode queue after lf-16g: AT-3b, SC-1b, …) and 4.4 (the
  hard-constraint queue AT-0p → SC-1b → SC-2 → …); DRI-DECISIONS-PHASE2 "Scope" SC1-SC3 and AT3.
- Read first: sc-1ad's REPORT (`governFast`, `governFast_eq`; the statement-gate stop), sc-3ab's, ar-10a's (how a row
  registers) and ap-1b's DELTA and REPORT (the latest row; its DELTA row 2 cites the decision that schedules it).

## Statement gate

The scope statement review closed with PASS (`scope-p3ver1.final.md`, then `scope-p3ver2.final.md`).
[statement-diff.txt](statement-diff.txt) is [evidence/spec_diff.py](evidence/spec_diff.py) on this tree: every theorem
built and `governorStatus` equal spec 5.2's text after whitespace normalisation, with spec 8.1's `Pinned.` placeholders
resolved to the names built (`checkDoc`, `checkCore`, `profilesOf`, `withUnits`: the document mode's; `decodeScope`,
`foldGovernors`: SC-1b's own). Against the plan's text: `governor_status_weakest`, `governor_status_none` and
`decodeScope_layout` are exact (`Lean.Json` read as `Json`); `scope_admission` and `scope_absent_unchanged` are the
spec's versions, which govern where the plan's schema differs (the plan's header), the plan's lf-16g names
(`admitDocument`, `DocumentAnswer`, `admitChain`, `withContents`) being the ones spec 8.1 replaced by the `Pinned.`
placeholders. No compiled statement changed (`lean/statements.txt`: additions only). Not built: `decodeScope_bound`,
`decoded_no_new_symbols` (sc-1ae). `ResponseShape.Encoders.Document.document_fits` now names `checkCore`, the entry it
always proved (renamed from `documentCase`); `runCaseReported_fits` is unchanged and now covers `checkDoc`.

## Plan rows

| Row (task) | Status | Where |
|---|---|---|
| (1) `governorStatus` (by `VE.Reports.Status` rank), `governor_status_weakest`, `governor_status_none` | delivered | `lean/VE/Scope/Wire.lean`, `lean/VE/Service/ScopeAdmission.lean`; `d0a921e76` |
| (2) the front-matter decoder `decodeScope` with `decodeScope_layout` | delivered | `decodeBlock` (Wire.lean: the block, the layout of exactly the document's units from its source bytes), `VE.Scope.decodeScope` (Document.lean: the document split, its environment without `scope@0` checked, the chain's `ReadingsEnvironment`, spec 8.1); `d0a921e76` |
| (3) the `scope@0` row of AR-10's table, with scope's composition proof | delivered | `wrapperRows` (one appended row; slot `govern`, no route), `gate_scope`; `scope_admission` is the row's composition theorem (spec 5.2). No edit to `wrapperProfiles`, `sitsOn`, `wrapperHead` or the route proofs; `gate_legacy` needed one fact (`scope@0` is no legacy profile), as ap-1b's row needed in `todayGate_base`. Python's profile data is generated (`ve/profile_table.json`); `ve/profiles.py` unchanged |
| (4) the two call sites in `lean/VE/Service/Document.lean`, `scope_admission`, `scope_absent_unchanged` | delivered | `checkDoc`: `governFast` before the chain, `foldGovernors` (`governorStatus`) after it; `runCaseReported` calls it. `scope_admission` rewrites the call with `governFast_eq` |
| (5) fixtures F1-doc, F1-off, F1-bad (small part documents), the plan's seeded bugs, one mutant per new trusted definition | delivered | below |
| (6) B1 in `tools/bench` | **sc-1bb** | size; it fits no benchmark harness change in this item |

What `checkDoc` does (spec 1.1, 1.6): a case whose document lists `scope@0` is gated by the whole profile table,
its block is decoded, `governFast` governs it, and `checkCore`, the entry as it was, answers the case with the governed
units (`withUnits`: a case member `check` reads only under `scope@0`) on the environment without `scope@0`
(`lowerScope`, a wrapper at step 1b). Each governor unit without content, meaning `specified`, hosting a frame, reguard
or carve-out then takes `governorStatus` over the statuses before the fold (none: UNFORMALISED), and the coverage's
bytes by status are counted again. The identities are the document's as written (block and parts included; spec 3);
source and meaning ids are those of the environment the chain reads. Python's relay reads the `scope` member under
`scope@0` and binds the answer on that environment (`ve/document/source.py`, `ve/document/lean.py`; R8: a governed
unit's content is bound by its presence, since its authored content is a part only Lean composes).

## Fixtures

- **F1-doc** (`tests/data/scope/hard-constraints.scope.md`, 14 lines): the pinned constitution's u0164.s01-u0166.s01
  (1,368 B, run-20261021T0600Z's translation, guards as AT-0p left them), the seven rules' shared members
  `{"sign": false, "unless": [], "over": []}` as the lead-in's part and `{name, predicate, guard}` as each item's,
  u0164.s02 `specified`, the environment cut to what the units name, `norm-defaults@0` as the pilot's. Lean's answer:
  u0164.s02 OPEN, the seven OPEN, each of their rows byte for byte the row of the block as translated today
  (`tests/test_scope_document.py::test_f1_doc_…`); `ve document check` end to end (`…::test_ve_document_check_…`).
  u0165.s03 has no content in the translation (a reading set) and stays OPEN, uncomposed (F-pend).
- **F1-bad**: u0165.s02 not admitted: u0164.s02 UNFORMALISED, its 22 B with it.
- **F1-off** (deviation from spec 7.2's expected value): without `scope@0` the document mode refuses the block
  (`unknown document metadata`) and, without it, a part content (`unit fence must match its id`), as before
  (`scope_absent_unchanged`). Spec 7.2 expected UNFORMALISED from `VE.Readings.Wire.decodeContent`, which is the
  readings route's decoder; the document mode on this environment does not read content through it. For scope.md's
  next revision.
- **F1-none** and the status table: `lean/VE/Scope/WireExamples.lean`.
- Lean `#guard`s on a small part document built as a request carries it (`lean/VE/Service/ScopeExamples.lean`): F1-doc,
  F1-bad, a lead-in not `specified`, the identities, F1-off, the row's refusals, the block's faults, `ScopeOrphanPart`,
  the layout; `lean/VE/Scope/WireExamples.lean`: every reach and effect of the wire, each wire fault, the layout's
  clamping, the fold on a hand-built answer (two unary governors on one unit in each order, a single frame, a unit
  with content, a graph governor; every status looked up by id in any order), `changers`, `byStatus` (three keys, a
  missing span, non-numeric span ends); `lean/VE/Compose/Examples.lean`: the row's routes and refusals, and the row as
  published (`ve/profile_table.json`).
- R8 fuzz (`tests/test_scope_document.py::test_every_structural_mutant_of_the_f1_answer_is_refused`): every one-fault
  structural mutant of the genuine F1 answer (each member dropped, a member added, each list element dropped or
  duplicated, each value retyped to `7`, `true`, `null`, `[]`, `{}`, `"x"`), plus four rebinding mutants (an
  undeclared unit id `absent`, a shifted span, an extra row, a forged `source_id`), is refused by the response schema
  or the binding.

## Seeded bugs

[mutants.json](mutants.json): 19 by hand, one per claimed behaviour, each killed and restored (Lean 16: Wire.lean 9,
Document.lean 5, Dispatch.lean 2; Python 3: `ve/document/source.py` and `ve/document/lean.py` (environment), each
failing `tests/test_scope_document.py::test_ve_document_check_builds_the_governed_document_from_the_bound_answer`;
`ve/document/lean.py` (the unit id dropped from the binding), failing
`tests/test_scope_document.py::test_every_structural_mutant_of_the_f1_answer_is_refused`). Each Lean
mutant fails a `#guard` with the proofs out of the build (`ScopeExamples.lean` imports the mode, not the proofs; the
row's mutants were built with `gate_scope`'s proof cut); the theorem each also breaks is listed. Mechanical:
`zsh mac-pytest.sh --trustmut -- --jobs 6 --max-mutants 1000 --allow docs/scope/sc-1b/trust-mutants-allow.json --json
docs/scope/sc-1b/trust-mutants.json` on `24504cdd5`, the final Lean change, run on the Mac:
**239 KILLED, 0 SURVIVOR, 0 UNKNOWN, 48 INVALID, 41 ALLOWED, 0 NOT RUN, exit 0**
([trust-mutants.json](trust-mutants.json)). It covers the 20 trusted definitions with changed lines; the tied
`governorStatus` and `checkDoc` are covered by the hand mutants above.

- Killed per definition: `byStatus` 38, `foldGovernors` 30, `scopeReadings` 28, `decodeParts` 23, `wrapperRows` 21,
  `decodeListName` 20, `changers` 13, `layoutOf` 10, `lowerScope` 10, `decodeGovernor` 8, `split` 8,
  `decodeEffect` 6, `decodeReach` 6, `check` 5, `spanIn` 4, `statusOf` 4, `listMember` 3, `decodeScope` 1,
  `profilesOf` 1.
- `decodeBlock`: all 10 mechanical mutants are ill-typed or invalid. Its hand mutant `decodeBlock-no-layout` is
  killed.
- Allowed, each with one reason per (definition, operator) in
  [trust-mutants-allow.json](trust-mutants-allow.json); I checked each allowed row by line.
  - 31 replacements Lean cannot elaborate.
  - 10 equivalent mutants:
    - `check`'s default `withGraph := true`: never read, since its one caller passes it.
    - `listMember`, `decodeParts` and `decodeGovernor` member-list cuts that keep the one member looked up. Lean's
      JSON objects are sorted by key, so `version` and `units` sort last.
    - `foldGovernors`' `take 1` and `reverse.take 1` inside `isEmpty`.
    - `scopeReadings`' `dropLast` before the lower filter and `drop 1` before the upper one. The gate admits
      scope@0 only with `norms@0` and `relational-fol@0`, and the environment is sorted.
- Earlier runs on this branch found 25, 34, 6 and 2 survivors. Each got a fixture: the fold over two unary
  governors in each order and one frame, statuses looked up by id in any answer order, `changers`, `byStatus` with
  three keys, two list names and two anchors, scope@0 anywhere in the list for `split` and `check`, `scopeReadings`
  with profiles on both sides, and the row as published with its `risk@0` refusal. The one exception is
  `scopeReadings`' old `contains` branch, which was equivalent, so I simplified the code instead.

## Trust

`uv run python tools/trust_map.py --check` on the final tree, exit 0, against `e9e63dda7`: K +0, S +0, D +122, G +59,
tied +14, unclassified +0, **trusted +147** (V; R16's limit is 150): `VE/Scope/Wire.lean` +112,
`VE/Service/Document.lean` +33, `VE/Compose/Dispatch.lean` +2. Recorded with `trust_map.py --allow` (reason with
these counts, "SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-1b, 2026-10-18") in `docs/trust-baseline.json`;
the fixture helpers are classified T in `tools/trust-classes.json`. FOLLOW-UPS row "## sc-1b" asks for the ties pass.

## Size

`git diff --numstat $(git merge-base HEAD main)`, added + deleted, generated files excluded (the Lean inventories,
`checkers.lock`, `docs/spec/assurance-manifest.md`, `ve/profile_table.json`, `statement-diff.txt`,
`trust-mutants.json`): **1,267** before this report and DELTA, over the ~600 rule (see the top of this report).

| Part | Lines | Files |
|---|---|---|
| Lean product code | 273 | `Scope/Wire.lean` 154, `Service/Document.lean` 68, `Compose/Dispatch.lean` 51 |
| Python product code | 9 | `ve/document/lean.py` 7, `ve/document/source.py` 2 |
| Proofs | 230 | `Service/ScopeAdmission.lean` 137, `ResponseShape/Encoders/Document.lean` 93 |
| Fixtures and tests | 460 | `Scope/WireExamples.lean` 155, `Service/ScopeExamples.lean` 129, `Compose/Examples.lean` 23, `tests/test_scope_document.py` 122, F1 14, `tests/test_scope_lean.py` 12, `tests/test_profile_table.py` 5 |
| Ledgers and side tables | 205 | `tools/trust-classes.json` 95, `ve/assurance-manifest.json` 57, `lean/SCOPE.md` 23, `lean/VE/Audit.lean` 12, `lean/ResponseShape/Audit.lean` 7, `docs/trust-baseline.json` 7, `lean/VE.lean` 4 |
| Evidence | 90 | `evidence/spec_diff.py` 39, `trust-mutants-allow.json` 30, `mutants.json` 21 |

## Tests

- Selected tests (`mac-pytest.sh --select -- --base e9e63dda7 --run`; ran on the VM because no Mac slot was free)
  on `34e1a60d1`'s tree: **462 units, 0 failed**, exit 0. The first selected run (on `b548c10d2`) failed four files
  this branch caused, none on main's known-red list: `test_scope_lean.py` (the wire's helpers have no theorem; now
  listed by name as `WIRE`, sc-1ae), `test_profile_table.py` (the scope@0 row is no environment profile),
  `test_lean_document_wrapper.py` and `test_difffuzz.py::test_ci_run` (F1 was named `*.ve.md` and so joined the seed
  corpus Python and Lean are compared on; it is a Lean-only document, renamed `hard-constraints.scope.md` as the
  senses fixtures are named `*.senses.md`).
- After `34e1a60d1` only Lean fixtures, the allow file and the inventories changed; their tests: `test_scope_lean.py`,
  `test_trust_budget.py`, `test_scope_document.py`, `test_assurance_manifest.py`, `test_profile_table.py`: 167 passed.
- `lake build`, `python3 lean/audit.py` (7,015 theorems), `regen_generated.py --check` (33 entries),
  `check_lean_imports.py`, `repo_map.py --check`, `trust_map.py --check`: all pass on the final Lean tree.
  `gate_collection.py --check --prebuilt`: 7 tests added, 0 removed, 0 refused, 0 stale, 0 malformed.
- The full gate is the chain's, on the committed final HEAD (not run here).

## Changes made while finishing the item

- `scope_admission`'s module moved from `VE/Scope/Admission.lean` to `VE/Service/ScopeAdmission.lean`. It states
  theorems on `Service.Document.checkDoc`, and in the profile layer it was a new outward import
  (`check_lean_imports.py`). The theorem names are unchanged.
- `ve/assurance-manifest.json`: `Document.lean` repinned (`documentCase` is now `checkCore`; the new decoders are
  listed), `Scope/Wire.lean` pinned as a Lean decoder, and the new JSON-handling files classified. The reasons for
  `Govern.lean` and `Effects.lean` no longer say "no service mode calls it yet".
- `scopeReadings` inserts `readings@1` in order without the old `contains` branch: same answers on every sorted,
  unique list, and no equivalent mutant left.

## Pilot bytes (estimate)

u0164.s02, 22 B, UNFORMALISED → OPEN on the constitution once the pilot rewrites u0164/u0165 (step 2 of queue 4.4,
pilot data, after DRI AT3's audit of u0165.s01-s07); an estimate: nothing is claimed before a pilot audit. This item
edits no translation. The F1 part document shows the mechanism on the pinned bytes.

## Overlap

Hand-written files: `lean/VE/Scope/{Wire,WireExamples}.lean`, `lean/VE/Service/{Document,ScopeAdmission,ScopeExamples}.lean`,
`lean/VE/Compose/{Dispatch,Examples}.lean`, `lean/ResponseShape/Encoders/Document.lean`, `lean/VE.lean`,
`lean/SCOPE.md`, `lean/VE/Audit.lean`, `lean/ResponseShape/Audit.lean`, `ve/document/{source,lean}.py`,
`ve/assurance-manifest.json`, `tests/test_scope_document.py`, `tests/test_scope_lean.py`, `tests/test_profile_table.py`,
`tests/data/scope/`, `tools/trust-classes.json`, `docs/trust-baseline.json`, `docs/scope/sc-1b/`. Of the in-flight branches only
`feature/jt-2` (stopped, waiting on a DRI signature) touches `Dispatch.lean`, `Compose/Examples.lean` and
`Service/Document.lean`; whichever lands second merges main. The ledgers merge through the `ve-generated` driver.

## Next items

- **sc-1bb**: B1, a `tools/bench` row running the layout and `governFast` on F1-doc's document over the full pinned
  constitution (184,893 B, 1,132 units), with its baseline; never a timing assertion.
- **sc-1ae** (after the DRI's decision): `BlockBound`, `HasStr`, `payload`, then `decodeScope_bound` and
  `decoded_no_new_symbols` with F1-dec, beside sc-1ad's five.
- **SC-1c** (explain route and relay) and **SC-2**; the pilot rewrite of u0164/u0165 (queue 4.4 step 2).

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: PASS. `tests/test_scope_document.py::test_every_structural_mutant_of_the_f1_answer_is_refused`
   (every one-fault mutant of the F1 answer, values retyped to `7`, `true`, `null`, `[]`, `{}`, `"x"`); the document
   schema did not change (`regen_generated.py --check`), and its transport cases (bad bytes, deep lists) are the
   relay's unchanged tests (`tests/test_document_lean_switch.py::test_every_structural_mutant_of_an_answer_is_refused`).
2. Every deliverable built, no rule broken: PASS. The plan-rows table; B1 is named sc-1bb under the common rules' size
   rule. One owner: Lean gates, governs and folds. Python only reads the `scope` member and binds on the lowered
   environment (`ve/document/lean.py`). That binding drops `scope@0` from the profile list, which is a filter for
   binding, not a Python copy of the decision. No report test was added. The size rule is broken (top of this report).
3. Tests and gates can fail: PASS. [mutants.json](mutants.json) has 19 by hand. [trust-mutants.json](trust-mutants.json)
   is the mechanical run on the final Lean (exit 0; every allowed row has its one-line reason in
   [trust-mutants-allow.json](trust-mutants-allow.json)).
4. Python, Lean and Rust agree, valid inputs pass: PASS. Documents without `scope@0` are answered as before
   (`scope_absent_unchanged`; the `#guard` `checkDoc full == checkCore full`; the selected
   `tests/test_lean_document_wrapper.py` and `tests/test_difffuzz.py` pass on the seed corpus). F1 is Lean-only:
   Python's own path refuses `scope@0` by design. Rust is unchanged.
5. R8 binding: PASS. The rebinding mutants in the same fuzz test (an undeclared id `absent`, a shifted span, an extra
   row, a forged `source_id`), and the seeded bug `py-bind-id-dropped`.
6. Gate evidence matches the final HEAD: PASS. The chain runs the gate on the committed final HEAD. The commit list
   below is `main..HEAD --no-merges`; the base is `git merge-base` (`e9e63dda7`).
7. No unsigned item: PASS. DELTA rows cite R16 (row 1, trust +147), R2 (row 3), and for row 2 the DRI decision files
   SYNTHESIS 2.2 and 4.2 and DRI-DECISIONS-PHASE2 "Scope" (the exception the task names). No row reserves a signature.
8. Every user-visible change in DELTA: PASS. Inputs without `scope@0` do not change (`scope_absent_unchanged`, F1-off).
   Rows 2 and 3 cover `scope@0` inputs, including Python's retained path (3e).
9. Test selection finds the tests: PASS. `select_tests` chose 462 units, not the whole suite (19,284 collected), and
   ran the changed `tests/test_scope_document.py` first. It also found the four failures above.
10. Lean statements say what is claimed: PASS. [statement-diff.txt](statement-diff.txt) matches spec 5.2 exactly. The
    seeded `checkDoc-no-govern` and `checkDoc-no-gate` also break `scope_admission` (`also_fails` in mutants.json).
11. Budgets, limits, deadlines: N.A. No new budget, limit or deadline; `governFast` and the fold are total functions
    inside the document mode's existing deadline.
12. No CPU or memory regression: N.A. The benchmark row is sc-1bb (cut by size). Whole-pilot runs are forbidden
    (L70). The fold is one pass over the units, and each unit's changers are filtered from the governor list.
13. `Test-removed` trailers: PASS. `tools/gate_collection.py --check --prebuilt`: 7 added, 0 removed, 0 refused,
    0 stale, 0 malformed.

## Evidence commit list (`git log --no-merges main..HEAD`, before this report's commit)

```
6ea6dc913 sc-1b: trust_mutants evidence on the final Lean change (239 killed, 0 survivors, 0 unknown, exit 0); hand mutant for decodeBlock
24504cdd5 sc-1b: byStatus fixture with three status keys (the append keeps every earlier key); the allow file's byStatus reasons name the line they cover; regenerate
5a0051f93 sc-1b: the fold fixture's governors each cover one item through anchors (two unary governors on u1 and on u3 in opposite orders, one frame on i2), so no cut of a unit's governors folds the same; allow scopeReadings' two cuts the gate makes equivalent; regenerate
34e1a60d1 sc-1b: fixtures for the list-cut survivors (three changers on one unit, the fold by id in any order, two list names and two anchors, scope@0 anywhere in the list for split and check, scopeReadings with profiles on both sides, the scope@0 row as published, its risk@0 refusal); allow file: sorted-member and isEmpty equivalents, ill-typed cuts; regenerate
19e1fcf03 sc-1b: F1 is a Lean-only fixture (hard-constraints.scope.md, as the senses fixtures, outside the *.ve.md seed corpus Python and Lean are compared on); the profile table's scope@0 row is no environment profile; test_scope_lean names the wire's helpers no theorem states yet (sc-1ae)
b548c10d2 sc-1b: scopeReadings lists readings@1 in order without an equivalent branch; byStatus fixture for non-numeric span ends; trust_mutants allow file (ill-typed and dead-default mutants); repin, regenerate
92f5ba9c6 sc-1b: every one-fault structural mutant of the F1 answer, and its rebinding mutants, is refused (R8)
201271d8e sc-1b: scope_admission's module moves to the service layer (VE/Service/ScopeAdmission.lean: it states theorems on Service.Document, no outward import); assurance manifest pins Document.lean and Wire.lean and classifies the new JSON files; regenerate
c56309426 sc-1b: trust classes for the new fixtures (T); R16 allowance V +147
af6444154 sc-1b: regenerate
2a2015619 sc-1b: fixtures for trust_mutants' survivors (the fold on an answer, changers, byStatus, spanIn's non-numeric ends, scopeReadings in order, decodeScope on a senses document)
e1579878a sc-1b: regenerate
cee3741cd sc-1b: SCOPE.md; the statement diff (spec 5.2 exact; two theorems left for sc-1ae); 17 hand-seeded mutants (Lean and Python), each killed; ScopeExamples imports the mode, not the proofs
206ead1b6 sc-1b: trust classes for the new declarations (governorStatus and checkDoc tied); tests/test_scope_document.py (F1-doc, F1-bad, F1-off, the row's refusals, ve document check end to end)
d0a921e76 sc-1b: scope@0 in the Lean document mode: governorStatus, decodeScope, the scope@0 row of AR-10's table with gate_scope, checkDoc (governFast before the chain, the governor fold), scope_admission and scope_absent_unchanged; the F1 part document; regenerate
```
