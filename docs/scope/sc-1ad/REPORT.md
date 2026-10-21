# sc-1ad: the precedence graph step, the refusal theorems and the run path `governFast` (scope@0, Lean core). Build report

**Stopped at the statement gate for five theorems; DRI decision needed (no DELTA signature reserved):**
`govern_preserves`, `govern_provenance`, `govern_strings`, `govern_no_new_symbols` and `decodeNorm_name` are false
as spec 5.1 states them, on JSON objects no parser builds (F-raw, mechanised). They, with `HasStr`, `payload`,
`BlockBound` and F-sym, are **sc-1ae**, after the DRI chooses between the two fixes below. Everything else is
delivered: the graph step, `governFast` with `governFast_eq` (what SC-1b needs), and the three refusal theorems.

- Branch `feature/sc-1ad`, worktree `/home/seyran/code/ve-sc-1ad`, merge base `9b7e6e5c7` (main, after sc-1ac).
- Plan and spec on main (`docs/spec/scope-PLAN.md`, `docs/spec/scope.md`), unchanged: section "SC-1a", design
  1.2–1.4, spec 1.5.5, 1.5.8, 4.2, 5.1, 7.1 and 8.1. SYNTHESIS 4.1/4.2: SC-1a is a phase-4 Lean core and no shared-file
  queue names its files. DRI-DECISIONS-PHASE2 "Scope" SC1–SC3 do not touch this item (as sc-1ac recorded).
- sc-3a's files (`lean/VE/Layout/`, `lean/VE/Discourse/`) are not touched. sc-3ab follows on `Govern.lean`; this item
  appends after `govern` and does not touch `coveredLayout` or `admitBlock`.

## Statement gate

The scope statement review closed with PASS (`scope-p3ver1.final.md`, then `scope-p3ver2.final.md`; sc-1a's
STATEMENT-GATE.md). [statement-diff.txt](statement-diff.txt) is sc-1ac's `evidence/spec_diff.py` rerun on this HEAD:
- sc-1ac's five theorems keep their statements (exact), and so do `frontier_graph_refused`, `readings_refused` and
  `nonrule_refused`.
- `governFast_eq` is `governFast D = govern D`: spec 5.1 writes the placeholder `Pinned.governFast`, which spec 8.1
  pins to "SC-1a's own definition: the run path"; the plan's own statement is exactly this text.
- `govern`, `normOf`, `edgesOf`, `edgesInto`, `ruleTable`, `edgesFor` and `addOver` equal spec 4.2. sc-1ac's
  deviation 3 (the precedence refusal) is gone. Deviations 1 and 2 (`coveredLayout`, `admitBlock`) are sc-3ab's.

**The FOLLOW-UPS risk, checked against unordered and unbalanced trees: it is real, and wider than recorded.**
`Json.obj` holds any `Std.TreeMap.Raw`. `patch` writes through `setObjVal!`, which is `insert!`; `insert!` calls
`balanceL!`/`balanceR!` on the path even when it replaces an existing key, and on a tree that is not balanced these
rotate and can drop a grandchild's subtrees. F-raw (`lean/VE/Scope/Examples.lean`, `#guard`s, each `govern` call
succeeding):
1. an ordered but unbalanced top level `x(units(·, w(·, wa)))`: the document reads `wa`, the answer does not
   (`govern_preserves`' first conjunct);
2. an unordered top level `x(units(·, zzz))`: the document does not read `zzz`, the answer does, with the string
   `"Z"` that is in neither the document (by `HasStr`) nor `g1`'s payload, and `BlockBound` holds there
   (`govern_strings`, `govern_no_new_symbols`, `govern_preserves`);
3. a unit `kind(content(·, c2(·, id)))`: after the patch the unit has no `id` (`govern_preserves`' second conjunct;
   `govern_provenance`: `contentOf out "u0165.s01"` is `null`);
4. the soft chain's decoder (`Phases.ruleFields`) reads a rule's members by `toList` and rebuilds the object, so it
   decodes the name `hidden` from a rule where `getObjVal? "name"` finds nothing (`decodeNorm_name`; the norms chain
   reads through lookup and the lemma holds there).

Every object a JSON parser builds is well formed, so no real document is affected; the statements are false only as
stated. Two fixes, for the DRI (FOLLOW-UPS "## sc-1ad"):
- (a) add a hypothesis that every object of the document (and of the decoded rule) is well formed (`.WF`), with a
  lemma for SC-1b that `Json.parse` builds such objects (recommended: the definitions stay spec text);
- (b) change the definitions: patch through a structure-preserving update, refuse repeated unit ids, and define
  `HasStr` over members.

Either changes approved text, so this item builds neither and changes no statement (BUILDER-CHECKLIST 10: an added
hypothesis needs a DRI ruling and a mechanised counterexample; F-raw is that counterexample).

## Plan rows

| Row (task) | Status | Where |
|---|---|---|
| (1) The graph step `normOf`, `edgesOf`, `edgesInto`, `ruleTable`, `edgesFor`, `addOver`; `govern` takes spec 4.2's text | delivered | `Govern.lean`, spec text; `077c3efcb` |
| (2) `HasStr`, `payload`, `BlockBound` | **sc-1ae** (statement gate) | they define what the stopped theorems claim, and fix (b) changes `HasStr` |
| (3) `decodeNorm_name`, `govern_preserves`, `govern_provenance`, `govern_strings`, `govern_no_new_symbols`, F-sym | **sc-1ae** (statement gate) | F-raw above; F-sym's computed half stands since sc-1ac |
| (4) `governFast` with `governFast_eq` | delivered | `Govern.lean` (run path), `Theorems.lean`; `645a81f18` |
| (5) `frontier_graph_refused`, `readings_refused`, `nonrule_refused` | delivered | from `wip/sc-1ad-refusals` (`cd750a68a`), with `admit_governor`; `bd0c1ee93` |
| Fixtures for the survivors of sc-1ac's review (F1) | delivered, 16 of 17 | "Survivors of sc-1ac's review" |
| Seeded bugs, trust, DELTA, REPORT | delivered | below |

## What is built

- **The graph step (spec 1.5.5).** Fixtures: `precedes` adds hc-2…hc-6 (same predicate, other name) to u0165.s01's
  `over`; `yields` adds hc-2 to each of them; another predicate (hc-csam) adds nothing; both together are
  deduplicated; `ScopeNoEffect` for a governor that adds nothing and for one whose unit is no rule, in governor
  order, not list order; a rule the decoder refuses gives the decoder's text; `addOver` on new, present and missing
  `over`. Theorems: `ruleTable_decoder` (every rule read is the chain's decoding of the composed object),
  `edgesFor_ok`, `edgesOf_graph` (only a graph governor adds an edge), `edgesInto_mem`, `addOver_nil`.
- **The run path (spec 1.5.8).** `governFast D` admits the block, computes `fastReads D` (each governor's reach as
  `frameOn` reads it, then each rule unit's base name, then each reach through the base-name table), and runs
  `governBody` on `ordered D` computed once. `memo t f x` reads `t` and falls back to `f x`, so a table of `f`'s own
  values reads as `f` (`memo_map`). `governFast_eq` follows from `fastReads_eq` and `governBody_slow`, and each step
  has its `rfl` equation to `govern`'s step (`frameOnF_slow` … `edgesOfF_slow`). `#guard`s check `governFast`'s
  values on answers, refusals, graph governors and governors of different reaches (they read no `govern`, so a
  `govern` mutant cannot pass through them).
- **The refusal theorems.** Unchanged statements. `admit_governor`'s proof needed two changes: sc-1ac's anchors step
  (after the wip branch) adds one split, and it doubled the cost of each `split` over the unfolded `admitBlock` past
  the default heartbeat limit; the proof now sets the two governor loops aside (`generalize`) before splitting
  (about 15 s, no `maxHeartbeats` option).

## Deviations

1. **The run path's tables are keyed by reach, not by governor id** (spec 1.5.8). A reach's value depends on the
   reach alone, so the table is right without unique ids (which a table by id would take from admission), and two
   governors with one reach share an entry. `deriving instance DecidableEq for Reach` is a separate command, so
   `Reach` keeps spec 4.2's text. Recorded for the spec's next revision (FOLLOW-UPS).
2. **`governBody` inlines `affected`, `ruleTable` and `edgesInto`** (with `orderCheckF` kept as its own definition so
   the `do` blocks stay definitionally equal). Its equation to `govern` is `rfl` (`governBody_slow`).

## Survivors of sc-1ac's review (F1), each with its fixture

Delivered (the review's line numbers are sc-1ac's `Govern.lean`): :204 a carve-out over an assertion is refused;
:229 the `yields` governor (now the graph step's fixtures); :201 a recorded reach of the right length with a wrong
unit; :159 `own` as a predicate and as a constant; :140 a lone non-narrowing reguard (`g2`) composes, its guard
`substOwn`'s value; :169 256 governors pass step 1; :113 a two-name `rules` reach; :66 a carve-out on a rule with
`unless` but no guard; :119/:120 order across classes (list 2, rules 3, fixed 4, against units' positions and list
order); :198 `yields` over a frontier; :191 a frame over an unknown list name; :202 the governor's unit reported
before its reach; :185-186 a condition both too deep and unsafe reports the depth. Left: fuel 63 at :63 (it changes
the output only for `own` at depth 64; no fixture fits the size), and :122 (the review found it equivalent).

## Size

About 595 hand-written lines of code, fixtures, side tables and tests against the merge base, and about 950 with the
docs and evidence, over the feed's ~600 (`git diff --numstat 9b7e6e5c7`, generated files excluded): Lean 468
(`Govern.lean` +134/−6: the graph step's 33 lines of spec text, the run path about 90; `Theorems.lean` +201/−3, of
which 89 are the refusal theorems restored as they were; `Examples.lean` +114/−5), `tests/test_scope_lean.py`
+12/−5, `tools/trust-classes.json` +88 (the side table; each tie takes six lines), `docs/trust-baseline.json` +14
(the `--allow` ledger), `lean/SCOPE.md` +22/−5; docs and evidence: this report, DELTA 18, the allow file 69,
`mutants.json` 15, and the outputs `statement-diff.txt` 66 and `trust-mutants.json` 165. The cut is the statement gate's: (2) and (3) go to sc-1ae. I measured at 346 lines after the run path,
before the fixtures, ties and docs; cutting the run path would leave SC-1b without `governFast`, and the fixtures were
asked for.

## Overlap check

Hand-written files: `lean/VE/Scope/{Govern,Theorems,Examples}.lean`, `lean/SCOPE.md`, `tests/test_scope_lean.py`,
`tools/trust-classes.json`, `docs/trust-baseline.json`, `docs/scope/sc-1ad/*`. Against `git diff --name-only
main...<b>` for every `lean-first/*`, `feature/*`, `infra/*`, `foundation/*` branch (2026-10-20): no other branch
touches `lean/VE/Scope/`, `lean/SCOPE.md` or `tests/test_scope_lean.py`. The ledgers (`tools/trust-classes.json`,
`docs/trust-baseline.json`) are also edited by `feature/ap-1b`, `ap-1c`, `df-1ac`, `jt-2`, `me-6b` and `foundation/me-1`,
and merge through the `ve-generated` driver; the generated `lean/VE/Audit.lean` likewise.

## Seeded bugs (Lean; [mutants.json](mutants.json), [trust-mutants.json](trust-mutants.json))

All in Lean, the only language whose product code changed (the Python change is a test file; the JSON files are side
tables and ledgers).

**Mechanical, every new trusted definition (R16, checklist 13a).** `zsh mac-pytest.sh --trustmut -- --max-mutants 1000
--allow docs/scope/sc-1ad/trust-mutants-allow.json --json docs/scope/sc-1ad/trust-mutants.json` on `fc0c533ea`, the
final Lean change: 163 mutants of the 5 trusted definitions with changed lines (`edgesOf`, `edgesInto`, `addOver`,
`govern`, `memo`; `normOf` and the derived instance have no operator site): **124 KILLED, 0 SURVIVOR, 0 UNKNOWN, 21
INVALID, 18 ALLOWED, exit 0**. The allow file has one reason per (definition, operator): `memo`'s five list operators
(a shorter table only falls back to `f x`), `govern`'s and `addOver`'s `take 1` and `reverse.take 1` inside an
`isEmpty` test (empty exactly when the list is), and the list-empty texts Lean refuses as ill-typed ("Function
expected", "cannot synthesize"); every allowed row in the JSON is one of these (checked by line), and the well-typed
list-empty mutants of those definitions are KILLED (`govern`'s `comp -> []` among them). Earlier runs found 28
survivors and 13 unknowns; each got a fixture (both ends of a reach, one edge, the second graph governor, a graph
governor first in order, `addOver` over two written names) or a cleaner check (`governFast` compared with values, and
`normsDoc` built without `govern`, so no run-path fixture reads `govern`).

**By hand, one per claimed behaviour (13).** Each was applied to `lean/VE/Scope/Govern.lean`, built with `lake build
VE.Scope.Examples`, then built again as fixtures only (a scratch copy of `Examples.lean` importing `VE.Scope.Govern`,
less the unmutated control's one error, sc-1ab's `mergeParts_text` at :359), and restored. The tree was clean after.

| Mutant (definition) | Claimed behaviour | First failure | Fixtures that fail without the proofs |
|---|---|---|---|
| `edgesOf-precedes-direction` (`edgesOf`) | a precedes edge runs from the governor's rule (1.5.5) | `VE/Scope/Theorems.lean:530` | Examples.lean 594, 614, 621 |
| `edgesOf-any-predicate` (`edgesOf`) | only reached rules on the governor's predicate join `over` | `VE/Scope/Theorems.lean:530` | Examples.lean 594 |
| `edgesInto-every-unit` (`edgesInto`) | an edge goes into its own unit only | `VE/Scope/Theorems.lean:399` | Examples.lean 594, 621 |
| `addOver-repeats` (`addOver`) | addOver appends each new name once | `VE/Scope/Examples.lean:594` | Examples.lean 594, 607, 627 |
| `govern-no-ScopeNoEffect` (`govern`) | a graph governor that adds nothing is refused | `VE/Scope/Theorems.lean:532` | Examples.lean 601, 602, 619 |
| `govern-edges-dropped` (`govern`) | each composed rule gets the edges into it | `VE/Scope/Theorems.lean:532` | Examples.lean 594, 614, 621 |
| `ruleTable-unit-only` (`ruleTable`) | the graph step decodes the governor's rule and its reach | `VE/Scope/Theorems.lean:532` | Examples.lean 594, 604, 614, 619, 621 |
| `normOf-reads-part` (`normOf`) | normOf reads a content's norm | `VE/Scope/Examples.lean:565` | Examples.lean 565, 594, 614, 621, 627, 639, 718 |
| `memo-first-entry` (`memo`) | memo reads x's own entry | `VE/Scope/Theorems.lean:517` | Examples.lean 639 |
| `fastReads-empty-layout` (`fastReads`) | the run path reads each layout reach | `VE/Scope/Theorems.lean:536` | Examples.lean 627, 632, 639 |
| `coveredBy-no-unknown-rule` (`coveredBy`) | the run path refuses an unknown rule name | `VE/Scope/Theorems.lean:525` | Examples.lean none: behind admission: governFast runs admitBlock first, whose covered refuses an unknown rule name, so this check never fires; only coveredBy_slow (the tie) catches it |
| `governBody-no-ScopeNoEffect` (`governBody`) | the run path refuses a graph governor that adds nothing | `VE/Scope/Theorems.lean:532` | Examples.lean 632 |
| `admitBlock-no-readings` (`admitBlock`) | readings_refused: a reading set's unit is refused | `VE/Scope/Theorems.lean:452` | Examples.lean 521, 522, 583 |

## Trust

`uv run python tools/trust_map.py --check` against `9b7e6e5c7` on this HEAD: **PASS** after `--allow`.
- K +0, S +23 (`edgesOf`, `edgesInto`, `addOver`, `govern`'s graph lines), G[V] +8 untied (`normOf`, `memo`, the
  derived `DecidableEq Reach`): trusted **+31**, all in `lean/VE/Scope/Govern.lean`.
- Tied, not trusted: `ruleTable`, `edgesFor`, `governFast`, `fastReads`, `frameOnF`, `baseObjF`, `coveredBy`,
  `governorsOfF`, `composedF`, `edgesOfF`, `governBody`. G[R]: `orderCheckF`.
- Recorded with `--allow` as `SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-1ad, 2026-10-18`; FOLLOW-UPS row
  "## sc-1ad (2026-10-20)".
- Every trusted definition is named by a theorem (`tests/test_scope_lean.py::test_every_trusted_scope_definition_is_used_by_a_theorem`),
  which can fail (`::test_a_govern_definition_no_theorem_uses_is_reported[VE.Scope.addOver|edgesInto|memo]`); the
  ties name their theorems (`::test_each_tie_names_a_theorem_about_its_definition`).

## Tests

- **Lean**: `lake build VE.Scope.Examples` has no error; every `#guard` and kernel fixture holds. `python3
  lean/audit.py` (through `regen_generated --write --only lean-audit-manifests`): PASS, 598 files, 6,847 theorems,
  the standard axioms only. `admit_governor` takes about 15 s, within the default heartbeats.
- **Generated files**: `uv run python tools/regen_generated.py --check --skip route-cases`: 31 entries current
  (`route-cases` needs the Rust release binary, absent here; this item changes no route; the gate checks it).
- **Gate collection**: `tools/gate_collection.py --check --prebuilt`: 18,950 collected, 3 added, 0 removed, 0
  refused, 0 stale, 0 malformed. No test was removed.
- **Other checks**: `tools/repo_map.py --check` PASS (37 modes); `tools/check_lean_imports.py` kept (598 modules);
  `tools/trust_map.py --check` PASS; `tests/test_scope_lean.py` 14 passed.
- **Selected tests** (`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`), on ve-mac-1 at
  `aad13d41` (clean; only this report follows): 80 units, exit 0, 0 failed. No test of `main-known-red.txt` failed.
- **Full gate**: not run by me, as the task says; the chain runs it on the final HEAD.

## Pilot bytes (estimate)

0 B: no route calls `govern` or `governFast` yet. SC-1b moves the first scope number (estimated +22 B on the
constitution, u0164.s02's lead-in), now that ar-10a, lf-16g and this item's `governFast` are in. Nothing is claimed
before a pilot audit.

## Next items

- **sc-1ae** (after the DRI's decision on fix (a) or (b)): `HasStr`, `payload`, `BlockBound`, `decodeNorm_name`,
  `govern_preserves`, `govern_provenance`, `govern_strings`, `govern_no_new_symbols`, with F-sym; F-raw becomes the
  fixture of the chosen hypothesis or definitions. The two survivors left above.
- **sc-3ab**: the anchor and label reaches and `admitBlock` step 7, on the same file, as planned.
- **SC-1b**: the document mode calls `governFast`; `governFast_eq` carries every theorem about `govern` to it.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** N.A.: no relayed Lean answer, route or response field is added.
2. **Every required deliverable built.** PASS, except the statement gate's stop: Plan rows lists each task row with
   its commit; (2) and (3) are stopped for the DRI's decision (first line), named sc-1ae. No Python copy of a Lean
   decision, no new report test; shared files are the ledgers only (Overlap check). Probe: `git diff --name-only
   main...HEAD`.
3. **Tests and gates can fail.** PASS: `docs/scope/sc-1ad/trust-mutants.json` (exit 0, 124 killed) and 13 hand
   mutants (`mutants.json`), each failing a theorem and, but one equivalent, a fixture with the proofs bypassed; the
   R16 check's can-fail tests `tests/test_scope_lean.py::test_a_govern_definition_no_theorem_uses_is_reported[VE.Scope.addOver]`
   (and `[VE.Scope.edgesInto]`, `[VE.Scope.memo]`).
4. **Python, Lean and Rust agree; valid inputs pass.** N.A. for agreement (Lean only). Valid inputs: F1-g, the graph
   fixtures and the `governFast` fixtures answer (`#guard`s in `Examples.lean`).
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS as far as I take it: committed and clean; the evidence commit list
   below is `git log --no-merges main..HEAD`; the chain runs the gate on the final HEAD.
7. **No unsigned item.** PASS: the DELTA row cites R16 and meets it (31 <= 150, K +0, itemised, exercised,
   FOLLOW-UPS row). The statement gate's stop reserves no DELTA cell; it is in the first line as the DRI decision
   needed.
8. **Every user-visible change in DELTA.** PASS: no caller reaches `govern` or `governFast` (DELTA.md).
9. **Test selection finds the tests.** PASS: `select_tests.py --base $(git merge-base HEAD main)` selects 80 units,
   among them `lake build`, `tests/test_scope_lean.py` and `tests/test_trust_budget.py`; every hand mutant fails in
   `lake build VE.Scope.Examples`.
10. **Lean statements say what is claimed.** PASS: `statement-diff.txt` (sc-1ac's five and the three refusal
    theorems exact; `governFast_eq` the pinned placeholder). Five statements are false as written: F-raw is the
    mechanised counterexample, and no hypothesis is added without the DRI.
11. **Budgets fail closed.** PASS for what this item touches: the 256-governor boundary (`#guard` with 256 passing
    step 1, 257 refused) and the depth refusal before `own` (`#guard`, `nest 64`).
12. **No CPU or memory regression.** N.A. for the pilots: no route calls the new code. `governFast` exists for SC-1b's
    B1 benchmark; `admit_governor`'s build cost fell from over the heartbeat limit to about 15 s.
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale, 0
    malformed; no test was removed.

## Evidence commit list (`git log --no-merges main..HEAD`, before this report's commit)

```
aad13d415 sc-1ad: R16 trust allowance (S +23, V +8, K +0)
9f4e2be54 sc-1ad: trust_mutants evidence on the final Lean change (Mac runner; exit 0)
fc0c533ea sc-1ad: 13 hand-seeded Lean mutants, each with the theorem and the fixtures (proofs bypassed) it fails
0b54128ec sc-1ad: run-path fixture over governors of different reaches and a rules reach (kills a memo mutant the proofs alone caught); regenerate
2b0954c52 sc-1ad: trust_mutants evidence (124 killed, 0 survivors, 18 allowed; exit 0)
a22ec823c sc-1ad: allow the ill-typed list-empty mutants of govern and edgesInto
cc426e81a sc-1ad: normsDoc built by mergeParts, not govern, so the run path's fixture reads no govern
c1903fd95 sc-1ad: regenerate
50877a5f5 sc-1ad: fixture for the edges of a second graph governor (trust_mutants survivor); trust-mutants evidence and allow file
3eb6bb51a sc-1ad: fixtures for trust_mutants' survivors (both ends of a reach, one edge, the second graph governor, a graph governor first, addOver over two names, depth before own); governFast checked against values; SCOPE.md, DELTA; regenerate
86edb0dc3 sc-1ad: trust classes; the run path's steps tied to govern's (rfl equations), ruleTable_decoder, edgesFor_ok, edgesOf_graph, edgesInto_mem, addOver_nil, reach_beq; R16 checks name them; regenerate
645a81f18 sc-1ad: the run path governFast with governFast_eq; fixtures for sc-1ac's review survivors and the F-raw counterfixture (the statement gate's finding)
bd0c1ee93 sc-1ad: frontier_graph_refused, readings_refused and nonrule_refused from wip/sc-1ad-refusals (cd750a68a); admit_governor sets the two governor loops aside before splitting (sc-1ac's anchors step doubled its cost)
077c3efcb sc-1ad: the precedence graph step (normOf, edgesOf, edgesInto, ruleTable, edgesFor, addOver) replaces govern's precedence refusal, with its fixtures; regenerate
```
